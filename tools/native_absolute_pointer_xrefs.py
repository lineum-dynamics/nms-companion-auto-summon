"""Find raw 64-bit preferred-image-base pointers to RVAs in PE sections."""

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

    try:
        data = args.exe.read_bytes()
        pe = pefile.PE(data=data, fast_load=False)
    except (OSError, pefile.PEFormatError) as error:
        parser.error(f"could not read a valid PE executable: {error}")
    if pe.FILE_HEADER.Machine != pefile.MACHINE_TYPE["IMAGE_FILE_MACHINE_AMD64"]:
        parser.error("the selected executable is not AMD64")

    image_base = pe.OPTIONAL_HEADER.ImageBase
    results: dict[int, list[tuple[str, int, int]]] = {
        rva: [] for rva in target_rvas
    }
    counts = {rva: 0 for rva in target_rvas}
    scanned_bytes = 0
    scanned_sections = 0
    for section in pe.sections:
        name = section.Name.rstrip(bytes([0])).decode(errors="replace")
        if name == ".reloc" or section.SizeOfRawData == 0:
            continue
        start = section.PointerToRawData
        end = min(start + section.SizeOfRawData, len(data))
        if start < 0 or end <= start:
            continue
        scanned_bytes += end - start
        scanned_sections += 1
        for target_rva in target_rvas:
            pointer = struct.pack("<Q", image_base + target_rva)
            cursor = start
            while True:
                found = data.find(pointer, cursor, end)
                if found < 0:
                    break
                counts[target_rva] += 1
                if len(results[target_rva]) < args.limit_per_target:
                    hit_rva = section.VirtualAddress + found - start
                    results[target_rva].append((name, found, hit_rva))
                cursor = found + 1

    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"IMAGE_BASE: 0x{image_base:X}")
    print(f"SCANNED_NON_RELOC_SECTION_BYTES: {scanned_bytes}")
    print(f"SCANNED_SECTIONS: {scanned_sections}")
    print("REFERENCE_KIND: literal 64-bit preferred-base VA only")
    for target_rva in target_rvas:
        print(
            f"\nTARGET_RVA: 0x{target_rva:X}; "
            f"TARGET_VA: 0x{image_base+target_rva:X}"
        )
        print(f"RAW_POINTER_MATCHES: {counts[target_rva]}")
        print(f"PRINTED: {len(results[target_rva])}")
        for name, file_offset, hit_rva in results[target_rva]:
            print(
                f"  SECTION: {name}; FILE_OFFSET: 0x{file_offset:X}; "
                f"RVA: 0x{hit_rva:X}"
            )
        if counts[target_rva] > len(results[target_rva]):
            print("TRUNCATED: yes")
    print(
        "\nLIMIT: excludes .reloc and searches literal preferred-base VAs only; "
        "does not find RVAs, relative tables or dynamically constructed pointers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
