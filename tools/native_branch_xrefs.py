"""Report direct x64 jump sites to one or more RVAs in AMD64 PE ranges."""

from __future__ import annotations

import argparse
import hashlib
from collections import deque
from pathlib import Path

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, Cs


EXECUTABLE = 0x20000000


def executable_section_for_rva(pe: pefile.PE, rva: int):
    for section in pe.sections:
        end = section.VirtualAddress + max(
            section.Misc_VirtualSize, section.SizeOfRawData
        )
        if (
            section.Characteristics & EXECUTABLE
            and section.VirtualAddress <= rva < end
        ):
            return section
    return None


def scan_jumps(
    data: bytes,
    pe: pefile.PE,
    target_vas: set[int],
    context: int,
    limit_per_target: int,
):
    base = pe.OPTIONAL_HEADER.ImageBase
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    decoder.detail = False
    sites = {target_va: [] for target_va in target_vas}
    counts = {target_va: 0 for target_va in target_vas}
    scanned_bytes = 0
    skipped_ranges = 0
    progress_interval = 5 * 1024 * 1024
    last_progress = 0

    for entry in getattr(pe, "DIRECTORY_ENTRY_EXCEPTION", ()):
        runtime = entry.struct
        start_rva = runtime.BeginAddress
        end_rva = runtime.EndAddress
        section = executable_section_for_rva(pe, start_rva)
        if section is None or end_rva <= start_rva:
            skipped_ranges += 1
            continue

        offset = section.PointerToRawData + start_rva - section.VirtualAddress
        code = data[offset : offset + end_rva - start_rva]
        if len(code) != end_rva - start_rva:
            skipped_ranges += 1
            continue
        scanned_bytes += len(code)

        previous = deque(maxlen=context)
        pending: list[dict] = []
        for address, size, mnemonic, op_str in decoder.disasm_lite(
            code, base + start_rva
        ):
            current = (address, size, mnemonic, op_str)
            remaining = []
            for site in pending:
                site["instructions"].append(current)
                site["after_remaining"] -= 1
                if site["after_remaining"] == 0:
                    sites[site["target_va"]].append(site["record"])
                else:
                    remaining.append(site)
            pending = remaining

            target_va = None
            if mnemonic == "jmp":
                try:
                    direct_target = int(op_str, 0)
                except ValueError:
                    direct_target = None
                if direct_target in target_vas:
                    target_va = direct_target

            if target_va is not None:
                counts[target_va] += 1
                if len(sites[target_va]) + sum(
                    site["target_va"] == target_va for site in pending
                ) < limit_per_target:
                    record = {
                        "start_rva": start_rva,
                        "end_rva": end_rva,
                        "jump_rva": address - base,
                        "next_rva": address + size - base,
                        "instructions": [*previous, current],
                    }
                    if context == 0:
                        sites[target_va].append(record)
                    else:
                        pending.append(
                            {
                                "target_va": target_va,
                                "record": record,
                                "instructions": record["instructions"],
                                "after_remaining": context,
                            }
                        )
            if context:
                previous.append(current)

        for site in pending:
            sites[site["target_va"]].append(site["record"])

        if scanned_bytes - last_progress >= progress_interval:
            print(
                f"PROGRESS: decoded 0x{scanned_bytes:X} runtime-function bytes",
                flush=True,
            )
            last_progress = scanned_bytes

    return sites, counts, scanned_bytes, skipped_ranges


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument(
        "--target-rva",
        required=True,
        action="append",
        type=lambda value: int(value, 0),
        help="target RVA; repeat to query multiple targets in one image scan",
    )
    parser.add_argument("--context", type=int, default=5)
    parser.add_argument("--limit-per-target", type=int, default=50)
    args = parser.parse_args()
    if not 0 <= args.context <= 12:
        parser.error("--context must be between 0 and 12")
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
    if not hasattr(pe, "DIRECTORY_ENTRY_EXCEPTION"):
        parser.error("the executable has no parsed AMD64 runtime-function directory")

    base = pe.OPTIONAL_HEADER.ImageBase
    for target_rva in target_rvas:
        if executable_section_for_rva(pe, target_rva) is None:
            parser.error(f"target RVA 0x{target_rva:X} is not in an executable section")

    target_vas = {base + target_rva for target_rva in target_rvas}
    sites, counts, scanned_bytes, skipped_ranges = scan_jumps(
        data, pe, target_vas, args.context, args.limit_per_target
    )
    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"IMAGE_BASE: 0x{base:X}")
    print(f"SCANNED_RUNTIME_FUNCTION_BYTES: {scanned_bytes}")
    print(f"SKIPPED_RUNTIME_RANGES: {skipped_ranges}")
    print("REFERENCE_KIND: direct immediate `jmp` instructions only")

    for target_rva in target_rvas:
        target_va = base + target_rva
        print(f"\nTARGET_RVA: 0x{target_rva:X}")
        print(f"DIRECT_JUMPS: {counts[target_va]}")
        print(f"PRINTED: {len(sites[target_va])}")
        for site in sites[target_va]:
            print(
                f"\nJUMP_RVA: 0x{site['jump_rva']:X}; "
                f"NEXT_RVA: 0x{site['next_rva']:X}; "
                f"FUNCTION_RVA: 0x{site['start_rva']:X}-0x{site['end_rva']:X}"
            )
            for address, _, mnemonic, op_str in site["instructions"]:
                print(f"  0x{address-base:X}: {mnemonic} {op_str}")
        if counts[target_va] > len(sites[target_va]):
            print("TRUNCATED: yes")

    print(
        "\nLIMIT: direct decoded immediate jumps only; this does not find calls, "
        "indirect branches or establish runtime semantics."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
