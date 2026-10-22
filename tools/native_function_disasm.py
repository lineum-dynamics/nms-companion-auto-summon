"""Disassemble a bounded RVA window from an exact-build x64 PE executable."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, Cs


AMD64 = 0x8664
EXECUTABLE = 0x20000000


def parse_int(value: str) -> int:
    return int(value, 0)


def section_for_rva(pe: pefile.PE, rva: int):
    for section in pe.sections:
        section_end = section.VirtualAddress + max(
            section.Misc_VirtualSize, section.SizeOfRawData
        )
        if section.VirtualAddress <= rva < section_end:
            return section, section_end
    return None, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--rva", required=True, type=parse_int)
    parser.add_argument("--size", required=True, type=parse_int)
    args = parser.parse_args()

    if args.size <= 0 or args.size > 0x10000:
        parser.error("--size must be between 1 and 0x10000 bytes")

    pe = pefile.PE(str(args.exe), fast_load=False)
    if pe.FILE_HEADER.Machine != AMD64:
        parser.error("the input is not an AMD64 PE executable")

    section, section_end = section_for_rva(pe, args.rva)
    if not section or not section.Characteristics & EXECUTABLE:
        parser.error("--rva is not inside an executable section")
    if args.rva + args.size > section_end:
        parser.error("the requested window crosses the executable section boundary")

    code = pe.get_data(args.rva, args.size)
    if len(code) != args.size:
        parser.error("the requested RVA window is not fully backed by file data")

    sha256 = hashlib.sha256(args.exe.read_bytes()).hexdigest()
    base = pe.OPTIONAL_HEADER.ImageBase
    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {args.exe.stat().st_size}")
    print(f"SHA256: {sha256}")
    print(f"IMAGE_BASE: {base:#x}")
    print(f"RVA_WINDOW: {args.rva:#x}-{args.rva + args.size:#x}")
    print(f"SECTION: {section.Name.rstrip(bytes([0])).decode(errors='replace')}")

    entries = [
        entry.struct
        for entry in getattr(pe, "DIRECTORY_ENTRY_EXCEPTION", [])
        if entry.struct.BeginAddress <= args.rva < entry.struct.EndAddress
    ]
    for entry in entries:
        print(
            f"PDATA_ENTRY: {entry.BeginAddress:#x}-{entry.EndAddress:#x}; "
            f"UNWIND_RVA: {entry.UnwindData:#x}"
        )
    if not entries:
        print("PDATA_ENTRY: none contains the requested start RVA")

    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    for instruction in decoder.disasm(code, base + args.rva):
        print(
            f"{instruction.address - base:#x}: "
            f"{instruction.mnemonic} {instruction.op_str}".rstrip()
        )
    print(
        "LIMIT: bounded static disassembly only; chained unwind parents and "
        "instruction semantics require separate review."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
