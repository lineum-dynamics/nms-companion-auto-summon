"""Probe MSVC x64 RTTI and vtable candidates in an exact-build PE image.

This is a read-only research helper. A validated CompleteObjectLocator and
contiguous executable pointer run are structural evidence, not proof of method
semantics or live behavior.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

import pefile


EXECUTABLE = 0x20000000
READABLE = 0x40000000
COL_SIZE = 24
TYPE_DESCRIPTOR_HEADER_SIZE = 16
BASE_CLASS_DESCRIPTOR_SIZE = 28


def section_for_rva(pe: pefile.PE, rva: int):
    for section in pe.sections:
        end = section.VirtualAddress + max(
            section.Misc_VirtualSize, section.SizeOfRawData
        )
        if section.VirtualAddress <= rva < end:
            return section
    return None


def valid_data_rva(pe: pefile.PE, rva: int, size: int = 1) -> bool:
    section = section_for_rva(pe, rva)
    return bool(
        section
        and section.Characteristics & READABLE
        and not section.Characteristics & EXECUTABLE
        and rva + size <= section.VirtualAddress
        + max(section.Misc_VirtualSize, section.SizeOfRawData)
    )


def executable_for_va(pe: pefile.PE, address: int) -> bool:
    base = pe.OPTIONAL_HEADER.ImageBase
    if address < base:
        return False
    section = section_for_rva(pe, address - base)
    return bool(section and section.Characteristics & EXECUTABLE)


def all_offsets(data: bytes, needle: bytes):
    offset = 0
    while True:
        offset = data.find(needle, offset)
        if offset < 0:
            return
        yield offset
        offset += 1


def type_name_at(pe: pefile.PE, data: bytes, type_descriptor_rva: int) -> str:
    name_rva = type_descriptor_rva + TYPE_DESCRIPTOR_HEADER_SIZE
    if not valid_data_rva(pe, name_rva):
        return ""
    section = section_for_rva(pe, name_rva)
    assert section is not None
    file_offset = section.PointerToRawData + name_rva - section.VirtualAddress
    end = data.find(b"\x00", file_offset, file_offset + 512)
    if end < 0:
        return ""
    return data[file_offset:end].decode("ascii", errors="replace")


def parse_hierarchy(
    pe: pefile.PE, data: bytes, hierarchy_rva: int, expected_type_rva: int
):
    if not valid_data_rva(pe, hierarchy_rva, 16):
        return None
    signature, attributes, count, base_array_rva = struct.unpack(
        "<4I", pe.get_data(hierarchy_rva, 16)
    )
    if signature not in (0, 1) or not 1 <= count <= 256:
        return None
    if not valid_data_rva(pe, base_array_rva, count * 4):
        return None
    descriptor_rvas = struct.unpack(
        "<" + "I" * count, pe.get_data(base_array_rva, count * 4)
    )
    names = []
    for descriptor_rva in descriptor_rvas:
        if not valid_data_rva(pe, descriptor_rva, BASE_CLASS_DESCRIPTOR_SIZE):
            return None
        values = struct.unpack(
            "<7I", pe.get_data(descriptor_rva, BASE_CLASS_DESCRIPTOR_SIZE)
        )
        names.append(type_name_at(pe, data, values[0]))
    if not descriptor_rvas or struct.unpack(
        "<I", pe.get_data(descriptor_rvas[0], 4)
    )[0] != expected_type_rva:
        return None
    return {
        "signature": signature,
        "attributes": attributes,
        "count": count,
        "base_names": names,
    }


def find_vftables(pe: pefile.PE, data: bytes, locator_rva: int, max_slots: int):
    base = pe.OPTIONAL_HEADER.ImageBase
    locator_va = base + locator_rva
    pointer = struct.pack("<Q", locator_va)
    candidates = []
    for file_offset in all_offsets(data, pointer):
        try:
            locator_pointer_rva = pe.get_rva_from_offset(file_offset)
        except pefile.PEFormatError:
            continue
        vftable_rva = locator_pointer_rva + 8
        if not valid_data_rva(pe, vftable_rva, 8):
            continue
        slots = []
        for index in range(max_slots):
            slot_rva = vftable_rva + index * 8
            if not valid_data_rva(pe, slot_rva, 8):
                break
            target_va = struct.unpack("<Q", pe.get_data(slot_rva, 8))[0]
            if not executable_for_va(pe, target_va):
                break
            slots.append(target_va - base)
        if slots:
            candidates.append((locator_pointer_rva, vftable_rva, slots))
    return candidates


def function_range(pe: pefile.PE, target_rva: int):
    for entry in getattr(pe, "DIRECTORY_ENTRY_EXCEPTION", ()):
        runtime = entry.struct
        if runtime.BeginAddress == target_rva:
            return (runtime.BeginAddress, runtime.EndAddress, True)
    for entry in getattr(pe, "DIRECTORY_ENTRY_EXCEPTION", ()):
        runtime = entry.struct
        if runtime.BeginAddress <= target_rva < runtime.EndAddress:
            return (runtime.BeginAddress, runtime.EndAddress, False)
    return None


def find_target_vftables(pe: pefile.PE, data: bytes, target_rva: int, max_slots: int):
    """Reverse-map an executable RVA to validated RTTI-backed vftable slots."""
    image_base = pe.OPTIONAL_HEADER.ImageBase
    needle = struct.pack("<Q", image_base + target_rva)
    candidates = {}

    for section in pe.sections:
        if not section.Characteristics & READABLE:
            continue
        if section.Characteristics & EXECUTABLE:
            continue

        raw_start = section.PointerToRawData
        raw_end = raw_start + section.SizeOfRawData
        offset = raw_start
        while True:
            offset = data.find(needle, offset, raw_end)
            if offset < 0:
                break
            try:
                slot_rva = pe.get_rva_from_offset(offset)
            except pefile.PEFormatError:
                offset += 1
                continue

            for slot_index in range(max_slots):
                table_offset = offset - slot_index * 8
                col_offset = table_offset - 8
                if col_offset < raw_start:
                    break
                col_va = struct.unpack_from("<Q", data, col_offset)[0]
                if col_va < image_base:
                    continue
                locator_rva = col_va - image_base
                if not valid_data_rva(pe, locator_rva, COL_SIZE):
                    continue

                values = struct.unpack("<6I", pe.get_data(locator_rva, COL_SIZE))
                signature, _, _, type_rva, hierarchy_rva, self_rva = values
                if signature != 1 or self_rva != locator_rva:
                    continue
                hierarchy = parse_hierarchy(pe, data, hierarchy_rva, type_rva)
                if hierarchy is None:
                    continue

                table_rva = slot_rva - slot_index * 8
                for col_pointer_rva, found_table_rva, slots in find_vftables(
                    pe, data, locator_rva, max_slots
                ):
                    if found_table_rva != table_rva:
                        continue
                    if slot_index >= len(slots) or slots[slot_index] != target_rva:
                        continue
                    type_name = type_name_at(pe, data, type_rva)
                    key = (type_name, found_table_rva, slot_index, locator_rva)
                    candidates[key] = hierarchy
            offset += 1

    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--type-name")
    selector.add_argument("--target-rva", type=lambda value: int(value, 0))
    parser.add_argument("--max-slots", type=int, default=64)
    args = parser.parse_args()
    if not 1 <= args.max_slots <= 256:
        parser.error("--max-slots must be between 1 and 256")

    try:
        data = args.exe.read_bytes()
        pe = pefile.PE(data=data, fast_load=False)
    except (OSError, pefile.PEFormatError) as error:
        parser.error(f"could not read a valid PE executable: {error}")
    if pe.FILE_HEADER.Machine != pefile.MACHINE_TYPE["IMAGE_FILE_MACHINE_AMD64"]:
        parser.error("the selected executable is not AMD64")

    if args.target_rva is not None:
        target_section = section_for_rva(pe, args.target_rva)
        if not target_section or not target_section.Characteristics & EXECUTABLE:
            parser.error("--target-rva is not inside an executable section")
        candidates = find_target_vftables(pe, data, args.target_rva, args.max_slots)
        print(f"FILE: {args.exe.name}")
        print(f"SIZE: {len(data)}")
        print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
        print(f"IMAGE_BASE: 0x{pe.OPTIONAL_HEADER.ImageBase:X}")
        print(f"TARGET_RVA: 0x{args.target_rva:X}")
        print(f"VALID_VFTABLE_HITS: {len(candidates)}")
        for (name, table_rva, slot_index, locator_rva), hierarchy in sorted(
            candidates.items()
        ):
            bounds = function_range(pe, args.target_rva)
            if bounds is None:
                function_detail = "no .pdata range"
            else:
                start, end, entry = bounds
                function_detail = (
                    f".pdata {'entry' if entry else 'interior'} "
                    f"0x{start:X}-0x{end:X}"
                )
            print(
                f"TYPE: {name}; VFTABLE_RVA: 0x{table_rva:X}; "
                f"SLOT: {slot_index}; COL_RVA: 0x{locator_rva:X}; "
                f"BASES: {', '.join(hierarchy['base_names'])}; "
                f"TARGET: {function_detail}"
            )
        if not candidates:
            print("No validated RTTI-backed vftable slot points to this RVA.")
            return 1
        return 0

    encoded_name = args.type_name.encode("ascii") + b"\x00"
    image_base = pe.OPTIONAL_HEADER.ImageBase
    matches = []
    for name_offset in all_offsets(data, encoded_name):
        try:
            name_rva = pe.get_rva_from_offset(name_offset)
        except pefile.PEFormatError:
            continue
        type_descriptor_rva = name_rva - TYPE_DESCRIPTOR_HEADER_SIZE
        if not valid_data_rva(pe, type_descriptor_rva, TYPE_DESCRIPTOR_HEADER_SIZE):
            continue
        for ref_offset in all_offsets(data, struct.pack("<I", type_descriptor_rva)):
            try:
                ref_rva = pe.get_rva_from_offset(ref_offset)
            except pefile.PEFormatError:
                continue
            locator_rva = ref_rva - 12
            if not valid_data_rva(pe, locator_rva, COL_SIZE):
                continue
            values = struct.unpack("<6I", pe.get_data(locator_rva, COL_SIZE))
            signature, object_offset, cd_offset, type_rva, hierarchy_rva, self_rva = values
            if (
                signature != 1
                or type_rva != type_descriptor_rva
                or self_rva != locator_rva
            ):
                continue
            hierarchy = parse_hierarchy(
                pe, data, hierarchy_rva, type_descriptor_rva
            )
            if hierarchy is None:
                continue
            vftables = find_vftables(pe, data, locator_rva, args.max_slots)
            matches.append(
                {
                    "name_rva": name_rva,
                    "type_descriptor_rva": type_descriptor_rva,
                    "locator_rva": locator_rva,
                    "object_offset": object_offset,
                    "cd_offset": cd_offset,
                    "hierarchy": hierarchy,
                    "vftables": vftables,
                }
            )

    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"IMAGE_BASE: 0x{image_base:X}")
    print(f"TYPE_NAME: {args.type_name}")
    print(f"VALID_LOCATORS: {len(matches)}")
    for match in matches:
        hierarchy = match["hierarchy"]
        print(
            f"\nTYPE_DESCRIPTOR_RVA: 0x{match['type_descriptor_rva']:X}; "
            f"NAME_RVA: 0x{match['name_rva']:X}"
        )
        print(
            f"COL_RVA: 0x{match['locator_rva']:X}; "
            f"OBJECT_OFFSET: 0x{match['object_offset']:X}; "
            f"CD_OFFSET: 0x{match['cd_offset']:X}; "
            f"CHD_SIGNATURE: {hierarchy['signature']}; "
            f"BASES: {', '.join(hierarchy['base_names'])}"
        )
        if not match["vftables"]:
            print("  no vftable pointer candidate found")
        for locator_pointer_rva, vftable_rva, slots in match["vftables"]:
            print(
                f"VFTABLE_RVA: 0x{vftable_rva:X}; "
                f"COL_POINTER_RVA: 0x{locator_pointer_rva:X}; "
                f"EXECUTABLE_SLOTS: {len(slots)}"
            )
            for index, target_rva in enumerate(slots):
                bounds = function_range(pe, target_rva)
                if bounds is None:
                    detail = "no .pdata range"
                else:
                    start, end, entry = bounds
                    detail = (
                        f".pdata {'entry' if entry else 'interior'} "
                        f"0x{start:X}-0x{end:X}"
                    )
                print(f"  SLOT {index}: 0x{target_rva:X} ({detail})")

    if not matches:
        print("No validated x64 CompleteObjectLocator/vftable candidate found.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
