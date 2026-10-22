"""Print a capped inventory of MSVC class-name strings from an exact PE image.

This is a bounded byte-string search, not a structural RTTI parser. A name
match is only a lead and a missing name does not show that a function or
behavior is absent.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument(
        "--contains",
        action="append",
        required=True,
        help="case-insensitive byte substring; provide more than once for OR filtering",
    )
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--max-name-bytes", type=int, default=128)
    parser.add_argument(
        "--include-structs",
        action="store_true",
        help="include MSVC struct TypeDescriptor names (.?AU) as well as classes (.?AV)",
    )
    args = parser.parse_args()

    if not 1 <= args.limit <= 500:
        parser.error("--limit must be between 1 and 500")
    if not 1 <= args.max_name_bytes <= 512:
        parser.error("--max-name-bytes must be between 1 and 512")

    data = args.exe.read_bytes()
    prefix = rb"\.\?A[UV]" if args.include_structs else rb"\.\?AV"
    pattern = re.compile(prefix + rb"[^\x00]{1," + str(args.max_name_bytes).encode() + rb"}\x00")
    selectors = tuple(value.encode("ascii", errors="ignore").lower() for value in args.contains)
    candidates = {
        match[:-1].decode("ascii", errors="replace")
        for match in pattern.findall(data)
        if any(selector in match.lower() for selector in selectors)
    }
    names = sorted(candidates)

    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"PATTERN: {'.?A[UV]' if args.include_structs else '.?AV'} + 1..{args.max_name_bytes} non-NUL bytes + NUL")
    print(f"SELECTORS: {', '.join(args.contains)} (OR)")
    print(f"UNIQUE_MATCHES: {len(names)}")
    print(f"PRINTED: {min(len(names), args.limit)}")
    for name in names[: args.limit]:
        print(f"  {name}")
    if len(names) > args.limit:
        print("TRUNCATED: yes")
    print(
        "LIMIT: bounded decorated-name byte search only; it does not validate "
        "TypeDescriptors, COLs, hierarchies, vftables or function semantics."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
