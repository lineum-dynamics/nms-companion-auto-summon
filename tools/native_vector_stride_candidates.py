"""Find exact-build functions combining an element stride and vector-count writes.

This is a read-only candidate search. A matching stride and count field do not
identify the object, establish an append contract, or authorize a hook.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, CS_AC_WRITE, Cs, x86_const


AMD64 = 0x8664
EXECUTABLE = 0x20000000


def parse_int(value: str) -> int:
    return int(value, 0)


def is_memory_write(instruction, operand) -> bool:
    if operand.type != x86_const.X86_OP_MEM:
        return False
    access = operand.access
    if access & CS_AC_WRITE:
        return True
    return instruction.mnemonic in {"inc", "dec", "xadd", "cmpxchg"}


def count_field_writes(instruction, count_offset: int, image_base: int) -> list[str]:
    matches = []
    for operand in instruction.operands:
        if not is_memory_write(instruction, operand):
            continue
        if operand.mem.disp == count_offset:
            matches.append(
                f"{instruction.address - image_base:#x}: {instruction.mnemonic} "
                f"{instruction.op_str}"
            )
            break
    return matches


def stride_uses(instruction, stride: int, image_base: int) -> list[str]:
    if instruction.mnemonic != "imul":
        return []
    if any(
        operand.type == x86_const.X86_OP_IMM and operand.imm == stride
        for operand in instruction.operands[1:]
    ):
        return [
            f"{instruction.address - image_base:#x}: {instruction.mnemonic} "
            f"{instruction.op_str}"
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--stride", type=parse_int, default=0xE0)
    parser.add_argument("--count-offset", type=parse_int, default=4)
    parser.add_argument("--max-results", type=int, default=200)
    args = parser.parse_args()
    if args.stride <= 0:
        parser.error("--stride must be positive")
    if args.max_results <= 0:
        parser.error("--max-results must be positive")

    data = args.exe.read_bytes()
    pe = pefile.PE(data=data, fast_load=False)
    if pe.FILE_HEADER.Machine != AMD64:
        parser.error("the input is not an AMD64 PE executable")

    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    decoder.detail = True
    decoder.skipdata = True
    image_base = pe.OPTIONAL_HEADER.ImageBase
    scanned_bytes = 0
    skipped_ranges = 0
    candidates = []

    for entry in getattr(pe, "DIRECTORY_ENTRY_EXCEPTION", []):
        runtime = entry.struct
        start = runtime.BeginAddress
        end = runtime.EndAddress
        section = next(
            (
                item
                for item in pe.sections
                if item.Characteristics & EXECUTABLE
                and item.VirtualAddress <= start
                and end
                <= item.VirtualAddress
                + max(item.Misc_VirtualSize, item.SizeOfRawData)
            ),
            None,
        )
        if section is None:
            skipped_ranges += 1
            continue

        code = pe.get_data(start, end - start)
        if len(code) != end - start:
            skipped_ranges += 1
            continue
        scanned_bytes += len(code)

        count_hits = []
        stride_hits = []
        for instruction in decoder.disasm(code, image_base + start):
            if instruction.id == 0:
                continue
            count_hits.extend(
                count_field_writes(instruction, args.count_offset, image_base)
            )
            stride_hits.extend(stride_uses(instruction, args.stride, image_base))

        if count_hits and stride_hits:
            candidates.append(
                (start, end, tuple(sorted(set(stride_hits))), tuple(sorted(set(count_hits))))
            )

    digest = hashlib.sha256(data).hexdigest()
    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {digest}")
    print(f"STRIDE: {args.stride:#x}")
    print(f"COUNT_OFFSET: {args.count_offset:#x}")
    print(f"SCANNED_RUNTIME_FUNCTION_BYTES: {scanned_bytes}")
    print(f"SKIPPED_RUNTIME_RANGES: {skipped_ranges}")
    print(f"CANDIDATES: {len(candidates)}")
    for start, end, stride_hits, count_hits in candidates[: args.max_results]:
        print(f"\nFUNCTION_RANGE: {start:#x}-{end:#x}")
        for hit in stride_hits:
            print(f"  STRIDE: {hit}")
        for hit in count_hits:
            print(f"  COUNT_WRITE: {hit}")
    if len(candidates) > args.max_results:
        print(f"TRUNCATED: {len(candidates) - args.max_results} candidates omitted")
    print(
        "LIMIT: same-function stride/count co-occurrence only; verify the base "
        "object, caller, item initialization, and actual count growth."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
