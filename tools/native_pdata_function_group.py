"""Report the .pdata/UNW_FLAG_CHAININFO group containing an exact PE RVA."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import struct

import pefile


AMD64 = 0x8664
UNW_FLAG_CHAININFO = 0x4


def entry_key(entry) -> tuple[int, int, int]:
    return entry.BeginAddress, entry.EndAddress, entry.UnwindData


def read_chain_parent(pe: pefile.PE, entry) -> tuple[int, int, int] | None:
    """Return and validate the chained RUNTIME_FUNCTION, when present."""
    header = pe.get_data(entry.UnwindData, 4)
    if len(header) != 4:
        raise ValueError(f"truncated UNWIND_INFO at RVA 0x{entry.UnwindData:X}")

    flags = header[0] >> 3
    if not flags & UNW_FLAG_CHAININFO:
        return None

    code_count = header[2]
    aligned_count = (code_count + 1) & ~1
    parent_rva = entry.UnwindData + 4 + 2 * aligned_count
    raw_parent = pe.get_data(parent_rva, 12)
    if len(raw_parent) != 12:
        raise ValueError(f"truncated chained RUNTIME_FUNCTION at RVA 0x{parent_rva:X}")
    return struct.unpack("<3I", raw_parent)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--rva", required=True, type=lambda value: int(value, 0))
    args = parser.parse_args()

    try:
        data = args.exe.read_bytes()
        pe = pefile.PE(data=data, fast_load=False)
    except (OSError, pefile.PEFormatError) as error:
        parser.error(f"could not read a valid PE executable: {error}")
    if pe.FILE_HEADER.Machine != AMD64:
        parser.error("the selected executable is not AMD64")
    if not hasattr(pe, "DIRECTORY_ENTRY_EXCEPTION"):
        parser.error("the executable has no parsed AMD64 exception-function directory")

    entries = [item.struct for item in pe.DIRECTORY_ENTRY_EXCEPTION]
    by_key = {entry_key(entry): entry for entry in entries}
    containing = [
        entry for entry in entries
        if entry.BeginAddress <= args.rva < entry.EndAddress
    ]
    if not containing:
        parser.error(f"RVA 0x{args.rva:X} is not in a .pdata runtime-function range")

    parents: dict[tuple[int, int, int], tuple[int, int, int] | None] = {}
    try:
        for entry in entries:
            key = entry_key(entry)
            parent = read_chain_parent(pe, entry)
            if parent is not None and parent not in by_key:
                raise ValueError(
                    f"chained parent 0x{parent[0]:X}-0x{parent[1]:X} "
                    "is not present in the exception directory"
                )
            parents[key] = parent
    except ValueError as error:
        parser.error(str(error))

    roots: dict[tuple[int, int, int], tuple[int, int, int]] = {}

    def resolve_root(start: tuple[int, int, int]) -> tuple[int, int, int]:
        if start in roots:
            return roots[start]
        chain: list[tuple[int, int, int]] = []
        seen: set[tuple[int, int, int]] = set()
        current = start
        while current not in roots:
            if current in seen:
                raise ValueError("cycle found in UNW_FLAG_CHAININFO parents")
            if current not in by_key:
                raise ValueError("chained parent is not present in the exception directory")
            seen.add(current)
            chain.append(current)
            parent = parents[current]
            if parent is None:
                root = current
                break
            current = parent
        else:
            root = roots[current]
        for key in chain:
            roots[key] = root
        return root

    try:
        target_roots = {resolve_root(entry_key(entry)) for entry in containing}
        groups = {
            root: sorted(
                (entry for entry in entries if resolve_root(entry_key(entry)) == root),
                key=lambda entry: entry.BeginAddress,
            )
            for root in target_roots
        }
    except ValueError as error:
        parser.error(str(error))

    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"TARGET_RVA: 0x{args.rva:X}")
    print(f"CONTAINING_ENTRIES: {len(containing)}")
    for entry in containing:
        print(
            f"  0x{entry.BeginAddress:X}-0x{entry.EndAddress:X}; "
            f"UNWIND_RVA=0x{entry.UnwindData:X}; "
            f"ROOT=0x{resolve_root(entry_key(entry))[0]:X}"
        )
    for root, members in sorted(groups.items(), key=lambda item: item[0][0]):
        print(f"GROUP_ROOT: 0x{root[0]:X}-0x{root[1]:X}")
        print(f"GROUP_RANGES: {len(members)}")
        for entry in members:
            key = entry_key(entry)
            parent = parents[key]
            kind = "ROOT" if parent is None else f"CHAINED_TO=0x{parent[0]:X}"
            print(f"  0x{entry.BeginAddress:X}-0x{entry.EndAddress:X} {kind}")
    print(
        "LIMIT: unwind grouping only; it does not decode instructions or "
        "establish function semantics."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
