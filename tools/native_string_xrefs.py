"""Report direct RIP-relative references to selected PE strings in x64 functions.

This read-only research helper uses PE exception-directory ranges as function
bounds. It is a discovery aid only: indirect references, hashes, dynamically
constructed strings, and semantic behavior require separate analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, CS_OP_MEM, Cs
from capstone.x86_const import X86_REG_RIP


PRINTABLE_STRING = re.compile(rb"[ -~]{5,}\x00")
EXECUTABLE = 0x20000000


def safe_label(value: str) -> str:
    """Avoid emitting embedded source paths as if they were useful symbols."""
    if "/" in value or "\\" in value:
        return "<embedded path string>"
    return value


def matching_strings(data: bytes, pe: pefile.PE, terms: tuple[str, ...]):
    wanted = tuple(term.casefold() for term in terms)
    matches: dict[int, str] = {}
    base = pe.OPTIONAL_HEADER.ImageBase
    for section in pe.sections:
        if section.Characteristics & EXECUTABLE:
            continue
        raw = data[
            section.PointerToRawData : section.PointerToRawData + section.SizeOfRawData
        ]
        for match in PRINTABLE_STRING.finditer(raw):
            value = match.group()[:-1].decode("ascii", errors="replace")
            if any(term in value.casefold() for term in wanted):
                address = base + section.VirtualAddress + match.start()
                matches[address] = safe_label(value)
    return matches


def executable_section_for_rva(pe: pefile.PE, rva: int):
    for section in pe.sections:
        end = section.VirtualAddress + max(
            section.Misc_VirtualSize, section.SizeOfRawData
        )
        if section.Characteristics & EXECUTABLE and section.VirtualAddress <= rva < end:
            return section
    return None


def scan_xrefs(data: bytes, pe: pefile.PE, targets: dict[int, str]):
    base = pe.OPTIONAL_HEADER.ImageBase
    references: dict[int, list[tuple[int, int, int]]] = {
        address: [] for address in targets
    }
    scanned_bytes = 0
    skipped_ranges = 0
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    decoder.detail = True

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

        for instruction in decoder.disasm(code, start):
            for operand in instruction.operands:
                if operand.type != CS_OP_MEM or operand.mem.base != X86_REG_RIP:
                    continue
                destination = instruction.address + instruction.size + operand.mem.disp
                if destination in references:
                    references[destination].append(
                        (start_rva, end_rva, instruction.address - base)
                    )

    return references, scanned_bytes, skipped_ranges


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Find direct RIP-relative code references to selected PE strings, "
            "using x64 runtime-function boundaries."
        )
    )
    parser.add_argument("--exe", required=True, type=Path, help="Exact executable to inspect")
    parser.add_argument(
        "--contains",
        action="append",
        required=True,
        metavar="TEXT",
        help="Case-insensitive substring to select; may be repeated",
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

    targets = matching_strings(data, pe, tuple(args.contains))
    if not targets:
        parser.error("no printable non-executable-section strings matched the requested terms")

    references, scanned_bytes, skipped_ranges = scan_xrefs(data, pe, targets)
    image_base = pe.OPTIONAL_HEADER.ImageBase
    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"IMAGE_BASE: 0x{image_base:X}")
    print(f"MATCHED_STRINGS: {len(targets)}")
    print(f"SCANNED_RUNTIME_FUNCTION_BYTES: {scanned_bytes}")
    print(f"SKIPPED_RUNTIME_RANGES: {skipped_ranges}")
    print("REFERENCE_KIND: direct RIP-relative references only")

    for address, label in sorted(targets.items()):
        found = references[address]
        print(f"\nSTRING RVA 0x{address - image_base:X}: {label}")
        if not found:
            print("  no direct RIP-relative code reference found by this pass")
            continue
        for start_rva, end_rva, instruction_rva in found:
            print(
                f"  instruction RVA 0x{instruction_rva:X}; "
                f"function RVA 0x{start_rva:X}-0x{end_rva:X}; "
                f"offset +0x{instruction_rva - start_rva:X}"
            )

    print(
        "\nLIMIT: This report does not establish function semantics or find "
        "indirect, hashed, dynamically built, or non-RIP-relative references."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
