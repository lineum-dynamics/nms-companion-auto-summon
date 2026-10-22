"""Search RTTI-anchored vtable method groups for exact member displacements.

The supplied vtable RVA and slot count must come from an exact-build RTTI
probe. This bounded scan does not discover RTTI, infer dynamic offsets, or
prove that a virtual call dispatches to a particular object at runtime.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import struct

import pefile
from capstone import CS_AC_READ, CS_AC_WRITE, CS_ARCH_X86, CS_MODE_64, Cs
from capstone.x86_const import X86_OP_MEM

from native_pdata_function_group import entry_key, read_chain_parent


AMD64 = 0x8664
IMAGE_SCN_MEM_EXECUTE = 0x20000000


def effective_memory_access(instruction: object, operand_index: int, operand: object) -> int:
    """Correct Capstone's READ-only report for explicit MOV-family stores."""
    mnemonic = instruction.mnemonic.lower()
    if operand_index == 0 and mnemonic.startswith(("mov", "vmov")):
        # Capstone 5.0.7 can mark vector MOV memory destinations as READ.
        # In x86 MOV-family instructions, an explicit memory operand in slot 0
        # is the destination; it writes memory and does not read it.
        return CS_AC_WRITE
    return operand.access


def parse_int(value: str) -> int:
    return int(value, 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--vtable-rva", required=True, type=parse_int)
    parser.add_argument("--slot-count", required=True, type=int)
    parser.add_argument("--offset", action="append", required=True, type=parse_int)
    parser.add_argument("--access", choices=("any", "read", "write"), default="any")
    args = parser.parse_args()

    try:
        data = args.exe.read_bytes()
        pe = pefile.PE(data=data, fast_load=False)
    except (OSError, pefile.PEFormatError) as error:
        parser.error(f"could not read a valid PE executable: {error}")
    if pe.FILE_HEADER.Machine != AMD64:
        parser.error("the selected executable is not AMD64")
    if not hasattr(pe, "DIRECTORY_ENTRY_EXCEPTION"):
        parser.error("the executable has no parsed AMD64 exception-function directory")
    if not 1 <= args.slot_count <= 512:
        parser.error("--slot-count must be between 1 and 512")
    if any(offset < 0 or offset > 0x7FFFFFFF for offset in args.offset):
        parser.error("member offsets must be nonnegative signed 32-bit values")

    image_base = pe.OPTIONAL_HEADER.ImageBase
    table_size = args.slot_count * 8
    table = pe.get_data(args.vtable_rva, table_size)
    if len(table) != table_size:
        parser.error("the requested vtable window is truncated")

    entries = [item.struct for item in pe.DIRECTORY_ENTRY_EXCEPTION]
    by_key = {entry_key(entry): entry for entry in entries}
    parents: dict[tuple[int, int, int], tuple[int, int, int] | None] = {}
    try:
        for entry in entries:
            key = entry_key(entry)
            parent = read_chain_parent(pe, entry)
            if parent is not None and parent not in by_key:
                raise ValueError(
                    f"chained parent 0x{parent[0]:X}-0x{parent[1]:X} "
                    "is absent from the exception directory"
                )
            parents[key] = parent
    except ValueError as error:
        parser.error(str(error))

    roots: dict[tuple[int, int, int], tuple[int, int, int]] = {}

    def resolve_root(start: tuple[int, int, int]) -> tuple[int, int, int]:
        if start in roots:
            return roots[start]
        chain: list[tuple[int, int, int]] = []
        seen: set[tuple[int, int, int]] = set()
        current = start
        while current not in roots:
            if current in seen:
                raise ValueError("cycle found in UNW_FLAG_CHAININFO parents")
            if current not in by_key:
                raise ValueError("chained parent is absent from the exception directory")
            seen.add(current)
            chain.append(current)
            parent = parents[current]
            if parent is None:
                root = current
                break
            current = parent
        else:
            root = roots[current]
        for key in chain:
            roots[key] = root
        return root

    group_ranges: dict[tuple[int, int, int], list[object]] = {}
    try:
        for entry in entries:
            root = resolve_root(entry_key(entry))
            group_ranges.setdefault(root, []).append(entry)
    except ValueError as error:
        parser.error(str(error))
    for ranges in group_ranges.values():
        ranges.sort(key=lambda entry: entry.BeginAddress)

    executable_ranges = [
        (section.VirtualAddress, section.VirtualAddress + max(
            section.Misc_VirtualSize, section.SizeOfRawData
        ))
        for section in pe.sections
        if section.Characteristics & IMAGE_SCN_MEM_EXECUTE
    ]
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True

    method_slots: dict[tuple[int, int, int], list[tuple[int, int]]] = {}
    no_pdata_slots = 0
    for slot in range(args.slot_count):
        va = struct.unpack_from("<Q", table, slot * 8)[0]
        if va < image_base:
            continue
        target = va - image_base
        if not any(start <= target < end for start, end in executable_ranges):
            continue
        containing = [
            entry for entry in entries
            if entry.BeginAddress <= target < entry.EndAddress
        ]
        if not containing:
            no_pdata_slots += 1
            continue
        for entry in containing:
            root = resolve_root(entry_key(entry))
            method_slots.setdefault(root, []).append((slot, target))

    matches: list[tuple[tuple[int, int, int], tuple[int, int], int, str, str, str]] = []
    wanted_access = {
        "any": 0,
        "read": CS_AC_READ,
        "write": CS_AC_WRITE,
    }[args.access]
    for root, ranges in sorted(group_ranges.items(), key=lambda item: item[0][0]):
        if root not in method_slots:
            continue
        for entry in ranges:
            code = pe.get_data(entry.BeginAddress, entry.EndAddress - entry.BeginAddress)
            for instruction in md.disasm(code, image_base + entry.BeginAddress):
                for operand_index, operand in enumerate(instruction.operands):
                    if operand.type != X86_OP_MEM or operand.mem.disp not in args.offset:
                        continue
                    address_only = instruction.mnemonic == "lea"
                    access_bits = effective_memory_access(
                        instruction, operand_index, operand
                    )
                    if wanted_access and address_only:
                        continue
                    if wanted_access and not access_bits & wanted_access:
                        continue
                    access = "ADDRESS_ONLY" if address_only else ""
                    if not address_only:
                        if access_bits & CS_AC_READ:
                            access += "R"
                        if access_bits & CS_AC_WRITE:
                            access += "W"
                    matches.append((
                        root,
                        (entry.BeginAddress, entry.EndAddress),
                        instruction.address - image_base,
                        access or "ADDRESS_ONLY",
                        instruction.mnemonic,
                        instruction.op_str,
                    ))

    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"PEFILE: {pefile.__version__}")
    import capstone
    print(f"CAPSTONE: {capstone.__version__}")
    print(f"VFTABLE_RVA: 0x{args.vtable_rva:X}")
    print(f"SLOT_COUNT: {args.slot_count}")
    print("MEMBER_OFFSETS: " + ", ".join(f"0x{offset:X}" for offset in args.offset))
    print(f"ACCESS_FILTER: {args.access}")
    print(f"RTTI_METHOD_ROOTS: {len(method_slots)}")
    print(f"METHOD_SLOTS_WITHOUT_PDATA: {no_pdata_slots}")
    print(f"MEMBER_OPERAND_MATCHES: {len(matches)}")
    for root, span, rva, access, mnemonic, operands in matches:
        slots = ",".join(str(slot) for slot, _target in method_slots[root])
        print(
            f"ROOT: 0x{root[0]:X}-0x{root[1]:X}; SLOTS: {slots}; "
            f"RANGE: 0x{span[0]:X}-0x{span[1]:X}; "
            f"RVA: 0x{rva:X}; ACCESS: {access}; {mnemonic} {operands}"
        )
    print(
        "LIMIT: bounded to the supplied vtable methods and their chained "
        "unwind ranges; validate the vtable separately with exact RTTI. "
        "No match does not prove the member is never accessed through aliases, "
        "dynamic offsets, or other classes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
