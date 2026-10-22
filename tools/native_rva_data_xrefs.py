"""Find exact 32-bit RVA constants in non-executable PE data sections."""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

import pefile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument(
        "--target-rva",
        required=True,
        action="append",
        type=lambda value: int(value, 0),
        help="target RVA; repeat to query multiple targets in one file scan",
    )
    parser.add_argument("--limit-per-target", type=int, default=50)
    args = parser.parse_args()
    if not 1 <= args.limit_per_target <= 1000:
        parser.error("--limit-per-target must be between 1 and 1000")

    target_rvas = sorted(set(args.target_rva))
    if len(target_rvas) > 64:
        parser.error("at most 64 target RVAs can be scanned in one pass")
    if any(not 0 <= rva <= 0xFFFFFFFF for rva in target_rvas):
        parser.error("target RVAs must fit in an unsigned 32-bit value")

    try:
        data = args.exe.read_bytes()
        pe = pefile.PE(data=data, fast_load=False)
    except (OSError, pefile.PEFormatError) as error:
        parser.error(f"could not read a valid PE executable: {error}")
    if pe.FILE_HEADER.Machine != pefile.MACHINE_TYPE["IMAGE_FILE_MACHINE_AMD64"]:
        parser.error("the selected executable is not AMD64")

    exception_directory = pe.OPTIONAL_HEADER.DATA_DIRECTORY[
        pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]
    ]
    exception_data = pe.get_data(
        exception_directory.VirtualAddress, exception_directory.Size
    )
    pdata_records = {
        struct.unpack_from("<III", exception_data, offset)
        for offset in range(0, len(exception_data) - 11, 12)
    }

    results: dict[int, list[tuple[str, int, int, tuple[int, tuple[int, int, int], str] | None]]] = {
        rva: [] for rva in target_rvas
    }
    counts = {rva: 0 for rva in target_rvas}
    scanned_bytes = 0
    scanned_sections = 0
    for section in pe.sections:
        name = section.Name.rstrip(bytes([0])).decode(errors="replace")
        if (
            name in {".reloc", ".pdata"}
            or section.SizeOfRawData == 0
            or section.Characteristics & pefile.SECTION_CHARACTERISTICS["IMAGE_SCN_MEM_EXECUTE"]
        ):
            continue
        start = section.PointerToRawData
        end = min(start + section.SizeOfRawData, len(data))
        if start < 0 or end <= start:
            continue
        scanned_bytes += end - start
        scanned_sections += 1
        for target_rva in target_rvas:
            pointer = struct.pack("<I", target_rva)
            cursor = start
            while True:
                found = data.find(pointer, cursor, end)
                if found < 0:
                    break
                counts[target_rva] += 1
                if len(results[target_rva]) < args.limit_per_target:
                    hit_rva = section.VirtualAddress + found - start
                    pdata_match = None
                    for record_offset in (found - 8, found - 4, found):
                        if record_offset < 0 or record_offset + 12 > len(data):
                            continue
                        record = struct.unpack_from("<III", data, record_offset)
                        if record in pdata_records:
                            field = ("BEGIN", "END", "UNWIND")[(found - record_offset) // 4]
                            pdata_match = (record_offset, record, field)
                            break
                    results[target_rva].append((name, found, hit_rva, pdata_match))
                cursor = found + 1

    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"IMAGE_BASE: 0x{pe.OPTIONAL_HEADER.ImageBase:X}")
    print(f"SCANNED_NON_EXECUTABLE_DATA_BYTES: {scanned_bytes}")
    print(f"SCANNED_SECTIONS: {scanned_sections}")
    print("REFERENCE_KIND: exact unaligned 32-bit RVA constant")
    for target_rva in target_rvas:
        print(f"\nTARGET_RVA: 0x{target_rva:X}")
        print(f"RVA_CONSTANT_MATCHES: {counts[target_rva]}")
        print(f"PRINTED: {len(results[target_rva])}")
        for name, file_offset, hit_rva, pdata_match in results[target_rva]:
            print(
                f"  SECTION: {name}; FILE_OFFSET: 0x{file_offset:X}; "
                f"RVA: 0x{hit_rva:X}"
            )
            if pdata_match:
                record_offset, record, field = pdata_match
                print(
                    f"    PDATA_RECORD_MATCH: field={field}; "
                    f"FILE_OFFSET=0x{record_offset:X}; "
                    f"BEGIN=0x{record[0]:X}; END=0x{record[1]:X}; "
                    f"UNWIND=0x{record[2]:X}"
                )
            else:
                print("    PDATA_RECORD_MATCH: none")
        if counts[target_rva] > len(results[target_rva]):
            print("TRUNCATED: yes")
    print(
        "\nLIMIT: searches exact 32-bit RVA values in file-backed non-executable "
        "sections, excluding .pdata and .reloc. PDATA_RECORD_MATCH only labels "
        "an adjacent exact Begin/End/Unwind triple; other relative offsets, "
        "code immediates and dynamically constructed pointers are not found."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
