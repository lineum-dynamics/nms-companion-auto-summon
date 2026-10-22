"""Find decoded x64 memory operands using selected displacements in PE ranges."""

from __future__ import annotations

import argparse
import hashlib
import re
from collections import defaultdict
from pathlib import Path

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, CS_AC_READ, CS_AC_WRITE, CS_OP_MEM, Cs


EXECUTABLE = 0x20000000
AMD64 = 0x8664
MEMORY_OPERAND = re.compile(r"\[([^\]]+)\]")
DISPLACEMENT_TOKEN = re.compile(r"(^|[+\-]\s*)(0x[0-9a-f]+|\d+)", re.IGNORECASE)
READ_ONLY_MNEMONICS = {"bt", "cmp", "idiv", "div", "mul", "test", "push", "call", "jmp"}
READ_WRITE_MNEMONICS = {"add", "and", "dec", "inc", "or", "shl", "shr", "sub", "xadd", "xor"}
STORE_MNEMONICS = {"mov", "movaps", "movdqa", "movdqu", "movss", "movups", "pop", "xchg"}


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


def access_name(access: int) -> str:
    names = []
    if access & CS_AC_READ:
        names.append("READ")
    if access & CS_AC_WRITE:
        names.append("WRITE")
    return "+".join(names) if names else "UNKNOWN"


def effective_memory_access(instruction: object, operand_index: int, operand: object) -> int:
    """Correct Capstone's READ-only report for explicit MOV-family stores."""
    mnemonic = instruction.mnemonic.lower()
    if operand_index == 0 and mnemonic.startswith(("mov", "vmov")):
        # Capstone 5.0.7 can mark vector MOV memory destinations as READ.
        # In x86 MOV-family instructions, an explicit memory operand in slot 0
        # is the destination; it writes memory and does not read it.
        return CS_AC_WRITE
    return operand.access


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument(
        "--offset",
        required=True,
        action="append",
        type=lambda value: int(value, 0),
        help="memory displacement; repeat to scan multiple offsets in one pass",
    )
    parser.add_argument(
        "--access",
        choices=("read", "write"),
        action="append",
        help="optional access filter; repeat for both reads and writes",
    )
    parser.add_argument("--limit-per-offset", type=int, default=80)
    parser.add_argument("--rva-min", type=lambda value: int(value, 0), default=0)
    parser.add_argument("--rva-max", type=lambda value: int(value, 0))
    parser.add_argument(
        "--fast-candidates",
        action="store_true",
        help="use disasm_lite to shortlist displacement operands; access is not verified",
    )
    args = parser.parse_args()
    if not 1 <= args.limit_per_offset <= 1000:
        parser.error("--limit-per-offset must be between 1 and 1000")
    if args.rva_min < 0 or (args.rva_max is not None and args.rva_max <= args.rva_min):
        parser.error("RVA bounds must be nonnegative and --rva-max greater than --rva-min")
    offsets = sorted(set(args.offset))
    if len(offsets) > 64:
        parser.error("at most 64 displacements can be scanned in one pass")
    if args.fast_candidates and args.access:
        parser.error("--fast-candidates cannot apply the exact --access filter")

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
    decoder.detail = not args.fast_candidates
    matches = defaultdict(list)
    counts = {offset: 0 for offset in offsets}
    scanned_bytes = 0
    skipped_ranges = 0
    excluded_ranges = 0
    progress_interval = 5 * 1024 * 1024
    last_progress = 0

    for entry in pe.DIRECTORY_ENTRY_EXCEPTION:
        runtime = entry.struct
        start_rva = runtime.BeginAddress
        end_rva = runtime.EndAddress
        if start_rva < args.rva_min or (args.rva_max is not None and end_rva > args.rva_max):
            excluded_ranges += 1
            continue
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
        if args.fast_candidates:
            instructions = (
                (address, mnemonic, op_str)
                for address, _, mnemonic, op_str in decoder.disasm_lite(
                    code, base + start_rva
                )
            )
            for address, mnemonic, op_str in instructions:
                instruction_rva = address - base
                for operand in MEMORY_OPERAND.finditer(op_str):
                    tokens = DISPLACEMENT_TOKEN.findall(operand.group(1))
                    if not tokens:
                        continue
                    sign, numeric = tokens[-1]
                    displacement = int(numeric, 0) * (-1 if sign.strip() == "-" else 1)
                    if displacement not in counts:
                        continue
                    counts[displacement] += 1
                    before_operand = op_str[: operand.start()]
                    if "," in before_operand:
                        access = "READ_HINT"
                    elif mnemonic == "lea":
                        access = "ADDRESS_HINT"
                    elif mnemonic in READ_ONLY_MNEMONICS:
                        access = "READ_HINT"
                    elif mnemonic in READ_WRITE_MNEMONICS:
                        access = "READ_WRITE_HINT"
                    elif mnemonic in STORE_MNEMONICS or mnemonic.startswith("vmov"):
                        access = "WRITE_HINT"
                    else:
                        access = "UNKNOWN_HINT"
                    if len(matches[displacement]) < args.limit_per_offset:
                        matches[displacement].append(
                            (
                                instruction_rva,
                                start_rva,
                                end_rva,
                                access,
                                mnemonic,
                                op_str,
                            )
                        )
        else:
            for instruction in decoder.disasm(code, base + start_rva):
                instruction_rva = instruction.address - base
                for operand_index, operand in enumerate(instruction.operands):
                    if operand.type != CS_OP_MEM:
                        continue
                    displacement = int(operand.mem.disp)
                    if displacement not in counts:
                        continue
                    access = access_name(
                        effective_memory_access(instruction, operand_index, operand)
                    )
                    if args.access and not any(
                        selected.upper() in access for selected in args.access
                    ):
                        continue
                    counts[displacement] += 1
                    if len(matches[displacement]) < args.limit_per_offset:
                        matches[displacement].append(
                            (
                                instruction_rva,
                                start_rva,
                                end_rva,
                                access,
                                instruction.mnemonic,
                                instruction.op_str,
                            )
                        )

        if scanned_bytes - last_progress >= progress_interval:
            print(f"PROGRESS: decoded 0x{scanned_bytes:X} runtime-function bytes", flush=True)
            last_progress = scanned_bytes

    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"IMAGE_BASE: 0x{base:X}")
    print(f"SCANNED_RUNTIME_FUNCTION_BYTES: {scanned_bytes}")
    print(f"SKIPPED_RUNTIME_RANGES: {skipped_ranges}")
    if args.rva_min or args.rva_max is not None:
        print(f"RVA_MIN: 0x{args.rva_min:X}")
        print(f"RVA_MAX: {hex(args.rva_max) if args.rva_max is not None else 'unbounded'}")
        print(f"EXCLUDED_BY_RVA_BOUNDS: {excluded_ranges}")
        print("RANGE_LIMIT: only complete .pdata ranges inside the selected bounds; chained ranges outside are excluded")
    print(
        "ANALYSIS_MODE: FAST CANDIDATE; heuristic access hints only"
        if args.fast_candidates
        else "ANALYSIS_MODE: DETAILED CAPSTONE OPERAND ACCESS"
    )
    for displacement in offsets:
        sites = sorted(matches[displacement])
        formatted_displacement = f"-0x{-displacement:X}" if displacement < 0 else f"0x{displacement:X}"
        print(f"\nDISPLACEMENT: {formatted_displacement}")
        print(f"OPERAND_MATCHES: {counts[displacement]}")
        print(f"PRINTED: {len(sites)}")
        for rva, start, end, access, mnemonic, op_str in sites[
            : args.limit_per_offset
        ]:
            print(
                f"  0x{rva:X} {access} {mnemonic} {op_str} "
                f"[FUNCTION 0x{start:X}-0x{end:X}]"
            )
        if counts[displacement] > args.limit_per_offset:
            print("TRUNCATED: yes")
    if args.fast_candidates:
        print(
            "\nLIMIT: fast candidates are decoded on .pdata boundaries, but the "
            "operand access hint is heuristic; verify with a detailed disassembly."
        )
    else:
        print(
            "\nLIMIT: displacement matches in decoded .pdata ranges only; "
            "operands can be reads or writes, and this does not prove object identity."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
