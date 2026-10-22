"""Read-only x64 PE signature matching against a pinned external data file."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

import pefile


EXECUTABLE_SECTION = 0x20000000
AMD64 = 0x8664
BYTE_TOKEN = re.compile(r"[0-9A-Fa-f]{2}\Z")


def parse_signature(value: str) -> tuple[bytes, tuple[bool, ...]]:
    tokens = value.split()
    if not tokens:
        raise ValueError("empty signature")
    values: list[int] = []
    fixed: list[bool] = []
    for token in tokens:
        if token in {"?", "??"}:
            values.append(0)
            fixed.append(False)
        elif BYTE_TOKEN.fullmatch(token):
            values.append(int(token, 16))
            fixed.append(True)
        else:
            raise ValueError(f"invalid signature token: {token!r}")
    if not any(fixed):
        raise ValueError("signature has no fixed bytes")
    return bytes(values), tuple(fixed)


def longest_fixed_run(values: bytes, fixed: tuple[bool, ...]) -> tuple[int, bytes]:
    runs: list[tuple[int, bytes]] = []
    index = 0
    while index < len(fixed):
        if not fixed[index]:
            index += 1
            continue
        end = index + 1
        while end < len(fixed) and fixed[end]:
            end += 1
        runs.append((index, values[index:end]))
        index = end
    return max(runs, key=lambda run: len(run[1]))


def containing_range(ranges: list[tuple[int, int]], rva: int) -> tuple[int, int] | None:
    return next(((start, end) for start, end in ranges if start <= rva < end), None)


def scan_signature(
    sections: list[pefile.SectionStructure],
    ranges: list[tuple[int, int]],
    signature: str,
) -> list[tuple[int, str, tuple[int, int] | None]]:
    values, fixed = parse_signature(signature)
    anchor_offset, anchor = longest_fixed_run(values, fixed)
    results: dict[int, tuple[str, tuple[int, int] | None]] = {}
    for section in sections:
        raw = section.get_data()
        offset = raw.find(anchor)
        while offset >= 0:
            start = offset - anchor_offset
            end = start + len(values)
            if start >= 0 and end <= len(raw):
                if all(not is_fixed or raw[start + index] == values[index]
                       for index, is_fixed in enumerate(fixed)):
                    rva = section.VirtualAddress + start
                    results[rva] = (
                        section.Name.rstrip(b"\0").decode("ascii", errors="replace"),
                        containing_range(ranges, rva),
                    )
            offset = raw.find(anchor, offset + 1)
    return [(rva, *results[rva]) for rva in sorted(results)]


def load_records(path: Path) -> list[dict[str, object]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("signature data must be a JSON list")
    records = [item for item in value if isinstance(item, dict)]
    if any(not isinstance(item.get("name"), str)
           or not isinstance(item.get("signature"), str) for item in records):
        raise ValueError("each signature record needs string name and signature fields")
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path, help="exact NMS executable to inspect")
    parser.add_argument("--data-json", required=True, type=Path, help="external signature JSON; not copied into this repository")
    parser.add_argument("--name", action="append", required=True, help="exact record name; repeat for additional records")
    args = parser.parse_args()

    records = load_records(args.data_json)
    available = {str(item["name"]): item for item in records}
    missing = sorted(set(args.name) - set(available))
    if missing:
        parser.error("signature name(s) not found: " + ", ".join(missing))

    pe = pefile.PE(str(args.exe))
    if pe.FILE_HEADER.Machine != AMD64:
        parser.error("executable is not AMD64")
    if not hasattr(pe, "DIRECTORY_ENTRY_EXCEPTION"):
        parser.error("AMD64 exception-function table is missing")

    sections = [section for section in pe.sections
                if section.Characteristics & EXECUTABLE_SECTION]
    ranges = [(entry.struct.BeginAddress, entry.struct.EndAddress)
              for entry in pe.DIRECTORY_ENTRY_EXCEPTION]
    for name in args.name:
        matches = scan_signature(sections, ranges, str(available[name]["signature"]))
        print(f"{name}: count={len(matches)}")
        for rva, section_name, function in matches:
            if function is None:
                print(f"  RVA=0x{rva:X} section={section_name} no .pdata range")
            else:
                start, end = function
                print(f"  RVA=0x{rva:X} section={section_name} "
                      f"range=0x{start:X}-0x{end:X} entry={rva == start}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
