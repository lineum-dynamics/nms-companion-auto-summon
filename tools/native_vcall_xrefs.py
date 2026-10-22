"""Find indirect virtual-call sites by vtable-slot byte offset in AMD64 PE ranges."""

from __future__ import annotations

import argparse
import hashlib
from collections import defaultdict, deque
from pathlib import Path
import re

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, Cs


EXECUTABLE = 0x20000000
MEMORY_OPERAND = re.compile(r"\[([^\]]+)\]")
REGISTER = re.compile(r"(?:r(?:ax|bx|cx|dx|si|di|bp|sp|[0-9]+[dwb]?)|e(?:ax|bx|cx|dx|si|di|bp|sp)|[abcd][lh])\Z")
TERM = re.compile(r"[+-]?[^+-]+")


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


def parse_memory(expression: str) -> tuple[str | None, str | None, int, int]:
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
        elif REGISTER.fullmatch(term):
            if base is None:
                base = term
        else:
            try:
                displacement += sign * int(term, 0)
            except ValueError:
                pass
    return base, index, scale, displacement


def scan_calls(
    data: bytes,
    pe: pefile.PE,
    slot_offset: int,
    required_fields: set[int],
    context: int,
    limit: int,
):
    base = pe.OPTIONAL_HEADER.ImageBase
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    calls: dict[str, int] = defaultdict(int)
    examples: dict[str, list[dict]] = defaultdict(list)
    scanned_bytes = 0
    skipped_ranges = 0
    progress_interval = 5 * 1024 * 1024
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

        instructions = list(decoder.disasm_lite(code, base + start_rva))
        scanned_bytes += len(code)
        fields = set()
        call_indices = []
        for index, (address, size, mnemonic, op_str) in enumerate(instructions):
            for operand in MEMORY_OPERAND.findall(op_str):
                fields.add(parse_memory(operand)[3])
            if mnemonic != "call":
                continue
            target = MEMORY_OPERAND.search(op_str)
            if not target:
                continue
            _, index_register, scale, displacement = parse_memory(target.group(1))
            if index_register is None and scale == 1 and displacement == slot_offset:
                call_indices.append(index)

        if required_fields and not required_fields.issubset(fields):
            continue
        label = (
            f"0x{start_rva:X}-0x{end_rva:X}"
            f" [REQUIRES {','.join(f'0x{x:X}' for x in sorted(required_fields))}]"
            if required_fields
            else f"0x{start_rva:X}-0x{end_rva:X}"
        )
        previous = deque(maxlen=context)
        call_set = set(call_indices)
        for index, instruction in enumerate(instructions):
            address, size, mnemonic, op_str = instruction
            if index in call_set:
                calls[label] += 1
                if len(examples[label]) < limit:
                    before = instructions[max(0, index - context) : index]
                    after = instructions[index + 1 : index + 1 + context]
                    examples[label].append(
                        {
                            "call_rva": address - base,
                            "start_rva": start_rva,
                            "end_rva": end_rva,
                            "instructions": [*before, instruction, *after],
                        }
                    )
            if context:
                previous.append(instruction)
        if scanned_bytes - last_progress >= progress_interval:
            print(f"PROGRESS: decoded 0x{scanned_bytes:X} runtime-function bytes", flush=True)
            last_progress = scanned_bytes

    return calls, examples, scanned_bytes, skipped_ranges


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--slot-offset", required=True, type=lambda value: int(value, 0))
    parser.add_argument(
        "--require-field",
        action="append",
        type=lambda value: int(value, 0),
        help="only print call sites in ranges that also reference this displacement; repeatable",
    )
    parser.add_argument("--context", type=int, default=4)
    parser.add_argument("--limit-per-range", type=int, default=40)
    args = parser.parse_args()
    if args.slot_offset < 0:
        parser.error("--slot-offset must be nonnegative")
    if not 0 <= args.context <= 12:
        parser.error("--context must be between 0 and 12")
    if not 1 <= args.limit_per_range <= 1000:
        parser.error("--limit-per-range must be between 1 and 1000")

    try:
        data = args.exe.read_bytes()
        pe = pefile.PE(data=data, fast_load=False)
    except (OSError, pefile.PEFormatError) as error:
        parser.error(f"could not read a valid PE executable: {error}")
    if pe.FILE_HEADER.Machine != pefile.MACHINE_TYPE["IMAGE_FILE_MACHINE_AMD64"]:
        parser.error("the selected executable is not AMD64")
    if not hasattr(pe, "DIRECTORY_ENTRY_EXCEPTION"):
        parser.error("the executable has no parsed AMD64 runtime-function directory")

    calls, examples, scanned_bytes, skipped_ranges = scan_calls(
        data,
        pe,
        args.slot_offset,
        set(args.require_field or []),
        args.context,
        args.limit_per_range,
    )
    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"SCANNED_RUNTIME_FUNCTION_BYTES: {scanned_bytes}")
    print(f"SKIPPED_RUNTIME_RANGES: {skipped_ranges}")
    print(f"SLOT_OFFSET: 0x{args.slot_offset:X}")
    print(f"REQUIRED_FIELDS: {', '.join(f'0x{x:X}' for x in (args.require_field or [])) or 'none'}")
    total = sum(calls.values())
    print(f"MATCHING_FUNCTION_RANGES: {len(calls)}")
    print(f"INDIRECT_CALLS: {total}")
    for label in sorted(calls):
        print(f"\nFUNCTION_RANGE: {label}; CALLS: {calls[label]}; PRINTED: {len(examples[label])}")
        for example in examples[label]:
            print(f"  CALL_RVA: 0x{example['call_rva']:X}")
            for address, _, mnemonic, op_str in example["instructions"]:
                print(f"    0x{address - pe.OPTIONAL_HEADER.ImageBase:X}: {mnemonic} {op_str}")
            if calls[label] > len(examples[label]):
                print("  TRUNCATED: yes")
    print(
        "LIMIT: indirect call slot-offset plus optional same-range displacement "
        "filter only; this does not identify the object's runtime type or prove dispatch."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
