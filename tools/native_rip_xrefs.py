"""Find direct RIP-relative code references to selected PE RVAs.

This read-only research helper decodes AMD64 runtime-function ranges and
reports RIP-relative memory operands whose resolved address equals a target
RVA. It is a discovery aid only; absolute, indirect, hashed, and dynamically
constructed references require separate analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, CS_AC_READ, CS_AC_WRITE, Cs
from capstone.x86 import X86_OP_MEM, X86_REG_RIP


EXECUTABLE = 0x20000000
RIP_OPERAND = re.compile(r"\[\s*rip(?:\s*([+-])\s*(0x[0-9a-f]+))?\s*\]", re.IGNORECASE)


def executable_section_for_rva(pe: pefile.PE, rva: int):
    for section in pe.sections:
        end = section.VirtualAddress + max(
            section.Misc_VirtualSize, section.SizeOfRawData
        )
        if section.Characteristics & EXECUTABLE and section.VirtualAddress <= rva < end:
            return section
    return None


def scan_xrefs(
    data: bytes,
    pe: pefile.PE,
    targets: set[int],
    limit_per_target: int,
    access: str,
):
    base = pe.OPTIONAL_HEADER.ImageBase
    references: dict[int, dict[str, object]] = {
        target: {"count": 0, "sites": []} for target in targets
    }
    scanned_bytes = 0
    skipped_ranges = 0
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    decoder.detail = False
    detailed_decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    detailed_decoder.detail = True
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

        start = base + start_rva
        length = end_rva - start_rva
        offset = section.PointerToRawData + start_rva - section.VirtualAddress
        code = data[offset : offset + length]
        scanned_bytes += len(code)

        for address, size, mnemonic, op_str in decoder.disasm_lite(code, start):
            text = f"{mnemonic} {op_str}"
            for match in RIP_OPERAND.finditer(op_str):
                sign = -1 if match.group(1) == "-" else 1
                displacement = int(match.group(2), 16) if match.group(2) else 0
                destination_rva = address + size + sign * displacement - base
                if destination_rva not in references:
                    continue

                if access != "any":
                    instruction_offset = address - start
                    raw_instruction = code[instruction_offset : instruction_offset + size]
                    instruction = next(
                        detailed_decoder.disasm(raw_instruction, address), None
                    )
                    if instruction is None:
                        continue
                    memory_operand = next(
                        (
                            operand
                            for operand in instruction.operands
                            if operand.type == X86_OP_MEM
                            and operand.mem.base == X86_REG_RIP
                        ),
                        None,
                    )
                    if memory_operand is None:
                        continue
                    flags = memory_operand.access
                    if access == "read" and not flags & CS_AC_READ:
                        continue
                    if access == "write" and not flags & CS_AC_WRITE:
                        continue

                entry = references[destination_rva]
                entry["count"] = int(entry["count"]) + 1
                sites = entry["sites"]
                assert isinstance(sites, list)
                if len(sites) < limit_per_target:
                    sites.append((start_rva, address - base, text))

        if scanned_bytes - last_progress >= progress_interval:
            print(f"PROGRESS: decoded 0x{scanned_bytes:X} runtime-function bytes", flush=True)
            last_progress = scanned_bytes

    return references, scanned_bytes, skipped_ranges


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Find direct RIP-relative references to selected RVAs using "
            "AMD64 runtime-function boundaries."
        )
    )
    parser.add_argument("--exe", required=True, type=Path, help="Exact executable to inspect")
    parser.add_argument(
        "--target-rva",
        action="append",
        required=True,
        type=lambda value: int(value, 0),
        help="Target RVA; may be repeated",
    )
    parser.add_argument(
        "--limit-per-target",
        type=int,
        default=50,
        help="maximum references printed per target (default: 50)",
    )
    parser.add_argument(
        "--access",
        choices=("any", "read", "write"),
        default="any",
        help="filter by the memory operand access type (default: any)",
    )
    args = parser.parse_args()

    try:
        data = args.exe.read_bytes()
        pe = pefile.PE(data=data, fast_load=False)
    except (OSError, pefile.PEFormatError) as error:
        parser.error(f"could not read a valid PE executable: {error}")

    if pe.FILE_HEADER.Machine != pefile.MACHINE_TYPE["IMAGE_FILE_MACHINE_AMD64"]:
        parser.error("the selected executable is not AMD64")
    if not hasattr(pe, "DIRECTORY_ENTRY_EXCEPTION"):
        parser.error("the executable has no parsed AMD64 runtime-function directory")
    if args.limit_per_target < 0:
        parser.error("--limit-per-target must be non-negative")

    targets = set(args.target_rva)
    for target in targets:
        if not any(
            section.VirtualAddress <= target < section.VirtualAddress + max(
                section.Misc_VirtualSize, section.SizeOfRawData
            )
            for section in pe.sections
        ):
            parser.error(f"target RVA 0x{target:X} is outside PE sections")

    references, scanned_bytes, skipped_ranges = scan_xrefs(
        data, pe, targets, args.limit_per_target, args.access
    )
    image_base = pe.OPTIONAL_HEADER.ImageBase
    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"IMAGE_BASE: 0x{image_base:X}")
    print(f"SCANNED_RUNTIME_FUNCTION_BYTES: {scanned_bytes}")
    print(f"SKIPPED_RUNTIME_RANGES: {skipped_ranges}")
    print(
        "REFERENCE_KIND: direct RIP-relative memory operands only; "
        f"access={args.access}"
    )

    for target in sorted(targets):
        print(f"\nTARGET RVA 0x{target:X}")
        entry = references[target]
        count = int(entry["count"])
        found = entry["sites"]
        assert isinstance(found, list)
        print(f"DIRECT_RIP_REFERENCES: {count}")
        if not count:
            print("  no direct RIP-relative reference found by this pass")
            continue
        for function_rva, instruction_rva, text in found[: args.limit_per_target]:
            print(
                f"  instruction RVA 0x{instruction_rva:X}; "
                f"runtime range begins 0x{function_rva:X}; {text}"
            )
        omitted = max(0, count - args.limit_per_target)
        if omitted:
            print(f"  OMITTED_REFERENCES: {omitted}")

    print(
        "\nLIMIT: This report does not establish constructor identity or find "
        "absolute, indirect, hashed, or dynamically built references."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
