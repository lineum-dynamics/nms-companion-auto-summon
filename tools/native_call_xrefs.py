"""Report direct x64 call sites for one RVA inside AMD64 PE function ranges."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, CS_OP_IMM, Cs


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


def scan_calls(data: bytes, pe: pefile.PE, target_va: int, context: int):
    base = pe.OPTIONAL_HEADER.ImageBase
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    decoder.detail = True
    sites = []
    scanned_bytes = 0
    skipped_ranges = 0

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
        scanned_bytes += len(code)
        instructions = list(decoder.disasm(code, base + start_rva))
        for index, instruction in enumerate(instructions):
            if instruction.mnemonic != "call":
                continue
            if not any(
                operand.type == CS_OP_IMM and operand.imm == target_va
                for operand in instruction.operands
            ):
                continue
            sites.append(
                {
                    "start_rva": start_rva,
                    "end_rva": end_rva,
                    "call_rva": instruction.address - base,
                    "return_rva": instruction.address + instruction.size - base,
                    "instructions": instructions[
                        max(0, index - context) : index + context + 1
                    ],
                }
            )

    return sites, scanned_bytes, skipped_ranges


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--target-rva", required=True, type=lambda value: int(value, 0))
    parser.add_argument("--context", type=int, default=5)
    args = parser.parse_args()
    if not 0 <= args.context <= 12:
        parser.error("--context must be between 0 and 12")

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
    target_va = base + args.target_rva
    if executable_section_for_rva(pe, args.target_rva) is None:
        parser.error("the requested target RVA is not in an executable section")

    sites, scanned_bytes, skipped_ranges = scan_calls(
        data, pe, target_va, args.context
    )
    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"IMAGE_BASE: 0x{base:X}")
    print(f"TARGET_RVA: 0x{args.target_rva:X}")
    print(f"SCANNED_RUNTIME_FUNCTION_BYTES: {scanned_bytes}")
    print(f"SKIPPED_RUNTIME_RANGES: {skipped_ranges}")
    print(f"DIRECT_CALLS: {len(sites)}")

    for site in sites:
        print(
            f"\nCALL_RVA: 0x{site['call_rva']:X}; "
            f"RETURN_RVA: 0x{site['return_rva']:X}; "
            f"FUNCTION_RVA: 0x{site['start_rva']:X}-0x{site['end_rva']:X}"
        )
        for instruction in site["instructions"]:
            rva = instruction.address - base
            print(f"  0x{rva:X}: {instruction.mnemonic} {instruction.op_str}")

    print(
        "\nLIMIT: Direct decoded E8-style call references only; this does not "
        "find indirect calls or establish runtime semantics."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
