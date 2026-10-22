"""Find atomic memory operations at selected displacements in exact-build .pdata ranges."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, Cs


EXECUTABLE = 0x20000000
MEMORY_OPERAND = re.compile(r"\[([^\]]+)\]")
LAST_DISPLACEMENT = re.compile(
    r"(?:(?P<sign>[+-])\s*)?(?P<value>0x[0-9a-f]+|[0-9]+)\s*$",
    re.IGNORECASE,
)
def is_atomic_memory_mnemonic(mnemonic: str) -> bool:
    lowered = mnemonic.casefold()
    # XCHG with a memory operand is implicitly locked; the other operations
    # count here only when Capstone reports the explicit LOCK prefix.
    return lowered.startswith("lock ") or lowered == "xchg"


def last_displacement(operand: str) -> int | None:
    match = LAST_DISPLACEMENT.search(operand)
    if match is None:
        return None
    value = int(match.group("value"), 0)
    return -value if match.group("sign") == "-" else value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument(
        "--offset",
        required=True,
        action="append",
        type=lambda value: int(value, 0),
        help="memory displacement; repeat for multiple offsets",
    )
    parser.add_argument("--limit-per-offset", type=int, default=100)
    args = parser.parse_args()
    if not 1 <= args.limit_per_offset <= 1000:
        parser.error("--limit-per-offset must be between 1 and 1000")
    offsets = sorted(set(args.offset))
    if len(offsets) > 64:
        parser.error("at most 64 displacements can be scanned in one pass")

    try:
        data = args.exe.read_bytes()
        pe = pefile.PE(data=data, fast_load=False)
    except (OSError, pefile.PEFormatError) as error:
        parser.error(f"could not read a valid PE executable: {error}")
    if pe.FILE_HEADER.Machine != pefile.MACHINE_TYPE["IMAGE_FILE_MACHINE_AMD64"]:
        parser.error("the selected executable is not AMD64")
    if not hasattr(pe, "DIRECTORY_ENTRY_EXCEPTION"):
        parser.error("the executable has no parsed AMD64 runtime-function directory")

    image_base = pe.OPTIONAL_HEADER.ImageBase
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    counts = {offset: 0 for offset in offsets}
    matches = {offset: [] for offset in offsets}
    scanned_bytes = 0
    skipped_ranges = 0

    for entry in pe.DIRECTORY_ENTRY_EXCEPTION:
        runtime = entry.struct
        start_rva = runtime.BeginAddress
        end_rva = runtime.EndAddress
        section = next(
            (
                candidate
                for candidate in pe.sections
                if candidate.Characteristics & EXECUTABLE
                and candidate.VirtualAddress <= start_rva
                < candidate.VirtualAddress + max(
                    candidate.Misc_VirtualSize, candidate.SizeOfRawData
                )
            ),
            None,
        )
        if section is None or end_rva <= start_rva:
            skipped_ranges += 1
            continue
        file_offset = section.PointerToRawData + start_rva - section.VirtualAddress
        code = data[file_offset : file_offset + end_rva - start_rva]
        if len(code) != end_rva - start_rva:
            skipped_ranges += 1
            continue
        scanned_bytes += len(code)

        for address, _, mnemonic, operands in decoder.disasm_lite(
            code, image_base + start_rva
        ):
            if not is_atomic_memory_mnemonic(mnemonic):
                continue
            for memory_operand in MEMORY_OPERAND.finditer(operands):
                displacement = last_displacement(memory_operand.group(1))
                if displacement not in counts:
                    continue
                counts[displacement] += 1
                if len(matches[displacement]) < args.limit_per_offset:
                    matches[displacement].append(
                        (address - image_base, start_rva, end_rva, mnemonic, operands)
                    )

    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"IMAGE_BASE: 0x{image_base:X}")
    print(f"SCANNED_RUNTIME_FUNCTION_BYTES: {scanned_bytes}")
    print(f"SKIPPED_RANGES: {skipped_ranges}")
    print("REFERENCE_KIND: lock-prefixed and x86 atomic memory operations only")
    for displacement in offsets:
        sites = matches[displacement]
        print(f"\nDISPLACEMENT: 0x{displacement:X}")
        print(f"ATOMIC_OPERANDS: {counts[displacement]}")
        print(f"PRINTED: {len(sites)}")
        for rva, start, end, mnemonic, operands in sites:
            print(
                f"  0x{rva:X} {mnemonic} {operands} "
                f"[FUNCTION 0x{start:X}-0x{end:X}]"
            )
        if counts[displacement] > len(sites):
            print("TRUNCATED: yes")
    print(
        "\nLIMIT: memory displacements are candidate filters only; follow each "
        "base object and caller before naming the field or function role."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
