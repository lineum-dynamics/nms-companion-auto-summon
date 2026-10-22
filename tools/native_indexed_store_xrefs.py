"""Find exact indexed memory stores in AMD64 PE runtime-function ranges."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, Cs


EXECUTABLE = 0x20000000
AMD64 = 0x8664
MEMORY_OPERAND = re.compile(r"\[([^\]]+)\]")
READ_ONLY = {"bt", "call", "cmp", "div", "idiv", "jmp", "mul", "test"}
REGISTER = re.compile(r"(?:r(?:ax|bx|cx|dx|si|di|bp|sp|[0-9]+[dwb]?)|e(?:ax|bx|cx|dx|si|di|bp|sp)|[abcd][lh])\Z")
TERM = re.compile(r"[+-]?[^+-]+")


def parse_memory(expression: str) -> tuple[str | None, str | None, int, int]:
    """Return base, index, scale and displacement from Capstone's memory text."""
    base: str | None = None
    index: str | None = None
    scale = 1
    displacement = 0
    for raw_term in TERM.findall(expression.replace(" ", "").lower()):
        sign = -1 if raw_term.startswith("-") else 1
        term = raw_term[1:] if raw_term[:1] in "+-" else raw_term
        if "*" in term:
            register, raw_scale = term.split("*", 1)
            if REGISTER.fullmatch(register):
                index = register
                scale = int(raw_scale, 0)
            continue
        if REGISTER.fullmatch(term):
            if base is None:
                base = term
            continue
        try:
            displacement += sign * int(term, 0)
        except ValueError:
            pass
    return base, index, scale, displacement


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--displacement", required=True, type=lambda value: int(value, 0))
    parser.add_argument("--scale", required=True, type=int, choices=(1, 2, 4, 8))
    parser.add_argument("--base-register", help="optional exact memory base register")
    parser.add_argument("--index-register", help="optional exact memory index register")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    if not 1 <= args.limit <= 5000:
        parser.error("--limit must be between 1 and 5000")

    try:
        data = args.exe.read_bytes()
        pe = pefile.PE(data=data, fast_load=False)
    except (OSError, pefile.PEFormatError) as error:
        parser.error(f"could not read a valid PE executable: {error}")
    if pe.FILE_HEADER.Machine != AMD64:
        parser.error("the selected executable is not AMD64")
    if not hasattr(pe, "DIRECTORY_ENTRY_EXCEPTION"):
        parser.error("the executable has no parsed AMD64 runtime-function directory")

    base = pe.OPTIONAL_HEADER.ImageBase
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    count = 0
    matches: list[tuple[int, int, int, str, str]] = []
    scanned_bytes = 0
    skipped_ranges = 0
    last_progress = 0

    for entry in pe.DIRECTORY_ENTRY_EXCEPTION:
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
        instructions = decoder.disasm_lite(code, base + start_rva)
        for address, _, mnemonic, op_str in instructions:
            operands = op_str.split(",")
            if mnemonic in READ_ONLY or not operands:
                continue
            destination = operands[0]
            match = MEMORY_OPERAND.search(destination)
            if not match:
                continue
            base_name, index_name, scale, displacement = parse_memory(match.group(1))
            base_match = args.base_register is None or base_name == args.base_register.lower()
            index_match = (
                index_name is not None
                and scale == args.scale
                and (args.index_register is None or index_name == args.index_register.lower())
            )
            matched = (
                base_match
                and index_match
                and displacement == args.displacement
            )
            if matched:
                count += 1
                if len(matches) < args.limit:
                    matches.append(
                        (
                            address - base,
                            start_rva,
                            end_rva,
                            mnemonic,
                            op_str,
                        )
                    )
        if scanned_bytes - last_progress >= 5 * 1024 * 1024:
            print(f"PROGRESS: decoded 0x{scanned_bytes:X} runtime-function bytes", flush=True)
            last_progress = scanned_bytes

    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"IMAGE_BASE: 0x{base:X}")
    print(f"SCANNED_RUNTIME_FUNCTION_BYTES: {scanned_bytes}")
    print(f"SKIPPED_RUNTIME_RANGES: {skipped_ranges}")
    print(f"WRITE_MATCHES: {count}")
    print(f"PRINTED: {len(matches)}")
    for rva, start, end, mnemonic, op_str in matches:
        print(f"  0x{rva:X} {mnemonic} {op_str} [FUNCTION 0x{start:X}-0x{end:X}]")
    if count > args.limit:
        print("TRUNCATED: yes")
    print(
        "LIMIT: fast destination-operand heuristic within .pdata ranges; confirm "
        "each candidate with detailed decoding. A match does not prove object identity or role."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
