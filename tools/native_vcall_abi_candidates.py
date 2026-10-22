"""Shortlist indirect virtual calls with pointer setup for RDX and R8."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re

import pefile

from native_vcall_xrefs import scan_calls


AMD64 = 0x8664
REGISTER = re.compile(
    r"(?:r(?:ax|bx|cx|dx|si|di|bp|sp|[0-9]+)|e(?:ax|bx|cx|dx|si|di|bp|sp)|[abcd][lh])\Z",
    re.IGNORECASE,
)


def parse_int(value: str) -> int:
    return int(value, 0)


def pointer_assignment(instruction: tuple[int, int, str, str], register: str) -> bool:
    _, _, mnemonic, operand_text = instruction
    parts = [part.strip().lower() for part in operand_text.split(",", 1)]
    if mnemonic not in {"lea", "mov"} or len(parts) != 2 or parts[0] != register:
        return False
    source = parts[1]
    return "[" in source or REGISTER.fullmatch(source) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--slot-offset", required=True, type=parse_int)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()
    if args.slot_offset < 0:
        parser.error("--slot-offset must be nonnegative")
    if not 1 <= args.limit <= 1000:
        parser.error("--limit must be between 1 and 1000")

    pe = pefile.PE(str(args.exe), fast_load=False)
    if pe.FILE_HEADER.Machine != AMD64:
        parser.error("the input is not an AMD64 PE executable")

    data = args.exe.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {sha256}")
    print(f"SLOT_OFFSET: {args.slot_offset:#x}")

    calls, examples, scanned_bytes, skipped_ranges = scan_calls(
        data,
        pe,
        args.slot_offset,
        set(),
        context=12,
        limit=1000,
    )
    image_base = pe.OPTIONAL_HEADER.ImageBase
    candidates = []
    for function_range, rows in examples.items():
        for row in rows:
            instructions = row["instructions"]
            call_index = next(
                index
                for index, instruction in enumerate(instructions)
                if instruction[0] == image_base + row["call_rva"]
            )
            preceding = instructions[:call_index]
            last_call = max(
                (
                    index
                    for index, instruction in enumerate(preceding)
                    if instruction[2] == "call"
                ),
                default=-1,
            )
            setup = preceding[last_call + 1 :]
            rdx_set = [item for item in setup if pointer_assignment(item, "rdx")]
            r8_set = [item for item in setup if pointer_assignment(item, "r8")]
            if rdx_set and r8_set:
                candidates.append(
                    (
                        function_range,
                        row["call_rva"],
                        instructions[call_index],
                        rdx_set[-1],
                        r8_set[-1],
                    )
                )

    total_calls = sum(calls.values())
    print(
        f"SCAN: decoded={scanned_bytes} skipped={skipped_ranges} "
        f"ranges={len(calls)} calls={total_calls}"
    )
    print(f"ABI_SHAPE_CANDIDATES: {len(candidates)}")
    for function_range, call_rva, call, rdx_set, r8_set in candidates[: args.limit]:
        print(
            f"CANDIDATE: range={function_range} call={call_rva:#x} "
            f"target={call[3]} "
            f"rdx={rdx_set[0] - image_base:#x}:{rdx_set[2]} {rdx_set[3]} "
            f"r8={r8_set[0] - image_base:#x}:{r8_set[2]} {r8_set[3]}"
        )
    if len(candidates) > args.limit:
        print(f"TRUNCATED: printed {args.limit} of {len(candidates)} candidates")
    print(
        "LIMIT: candidates only; this does not prove receiver type, call target, "
        "output ownership, capacity, or semantic compatibility."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
