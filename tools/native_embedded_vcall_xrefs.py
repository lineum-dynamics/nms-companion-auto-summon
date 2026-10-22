"""Find virtual calls made through an embedded object tracked within .pdata ranges."""

from __future__ import annotations

import argparse
import hashlib
from collections import deque
from pathlib import Path
import re

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, Cs


EXECUTABLE = 0x20000000
VOLATILE = {"rax", "rcx", "rdx", "r8", "r9", "r10", "r11"}
ALIASES = {
    "eax": "rax", "ax": "rax", "al": "rax", "ah": "rax",
    "ebx": "rbx", "bx": "rbx", "bl": "rbx", "bh": "rbx",
    "ecx": "rcx", "cx": "rcx", "cl": "rcx", "ch": "rcx",
    "edx": "rdx", "dx": "rdx", "dl": "rdx", "dh": "rdx",
    "esi": "rsi", "si": "rsi", "sil": "rsi",
    "edi": "rdi", "di": "rdi", "dil": "rdi",
    "ebp": "rbp", "bp": "rbp", "bpl": "rbp",
    "esp": "rsp", "sp": "rsp", "spl": "rsp",
}
REGISTER = re.compile(r"(?:r(?:ax|bx|cx|dx|si|di|bp|sp|[0-9]+[dwb]?)|e(?:ax|bx|cx|dx|si|di|bp|sp)|[abcd][lh])\Z")
TERM = re.compile(r"[+-]?[^+-]+")


def canonical(register: str) -> str:
    if register in ALIASES:
        return ALIASES[register]
    if register.startswith("r") and register[1:-1].isdigit() and register[-1:] in {"d", "w", "b"}:
        return register[:-1]
    return register


def executable_section_for_rva(pe: pefile.PE, rva: int):
    for section in pe.sections:
        end = section.VirtualAddress + max(
            section.Misc_VirtualSize, section.SizeOfRawData
        )
        if section.Characteristics & EXECUTABLE and section.VirtualAddress <= rva < end:
            return section
    return None


def format_instruction(instruction, base: int) -> str:
    address, _, mnemonic, op_str = instruction
    return f"0x{address - base:X}: {mnemonic} {op_str}".rstrip()


def parse_memory(expression: str):
    base = index = None
    scale = 1
    displacement = 0
    for raw_term in TERM.findall(expression.replace(" ", "").lower()):
        sign = -1 if raw_term.startswith("-") else 1
        term = raw_term[1:] if raw_term[:1] in "+-" else raw_term
        if "*" in term:
            register, raw_scale = term.split("*", 1)
            if REGISTER.fullmatch(register):
                index, scale = register, int(raw_scale, 0)
        elif REGISTER.fullmatch(term):
            if base is None:
                base = term
        else:
            try:
                displacement += sign * int(term, 0)
            except ValueError:
                pass
    return base, index, scale, displacement


def split_operands(op_str: str) -> list[str]:
    return [part.strip().lower() for part in op_str.split(",")]


def scan_range(data, pe, entry, object_offsets, context):
    base = pe.OPTIONAL_HEADER.ImageBase
    runtime = entry.struct
    start_rva, end_rva = runtime.BeginAddress, runtime.EndAddress
    section = executable_section_for_rva(pe, start_rva)
    if section is None or end_rva <= start_rva:
        return None, 1
    offset = section.PointerToRawData + start_rva - section.VirtualAddress
    code = data[offset : offset + end_rva - start_rva]
    if len(code) != end_rva - start_rva:
        return None, 1

    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    instructions = list(decoder.disasm_lite(code, base + start_rva))
    objects = {}
    vtables = {}
    function_slots = {}
    previous = deque(maxlen=context)
    matches = []

    read_only = {
        "cmp", "test", "call", "jmp", "ret", "push", "nop", "ud2",
        "je", "jne", "jz", "jnz", "ja", "jae", "jb", "jbe", "jg",
        "jge", "jl", "jle", "js", "jns", "jo", "jno", "jp", "jnp",
        "jecxz", "jrcxz",
    }

    for instruction in instructions:
        address, _, mnemonic, op_str = instruction
        operands = split_operands(op_str)
        destination = canonical(operands[0]) if operands and REGISTER.fullmatch(operands[0]) else None
        source_object = source_vtable = source_slot = None

        if mnemonic in {"lea", "mov"} and destination and len(operands) >= 2:
            source = operands[1]
            if REGISTER.fullmatch(source):
                source_register = canonical(source)
                source_object = objects.get(source_register)
                source_vtable = vtables.get(source_register)
                source_slot = function_slots.get(source_register)
            elif "[" in source and "]" in source:
                base_register, index_register, _, displacement = parse_memory(source[source.index("[") + 1 : source.index("]")])
                base_register = canonical(base_register) if base_register else None
                if index_register is None and mnemonic == "lea" and displacement in object_offsets:
                    source_object = (base_register, displacement, address - base)
                elif index_register is None and mnemonic == "lea" and displacement == 0 and base_register in objects:
                    source_object = objects[base_register]
                elif index_register is None and mnemonic == "mov" and displacement == 0 and base_register in objects:
                    source_vtable = (objects[base_register], address - base)
                elif index_register is None and mnemonic == "mov" and displacement in object_offsets:
                    source_vtable = ((base_register, displacement, address - base), address - base)
                elif index_register is None and mnemonic == "mov" and base_register in vtables:
                    source_slot = (vtables[base_register][0], displacement, vtables[base_register][1])

        if mnemonic == "call" and operands:
            operand = operands[0]
            target = None
            if "[" in operand and "]" in operand:
                base_register, index_register, _, displacement = parse_memory(operand[operand.index("[") + 1 : operand.index("]")])
                base_register = canonical(base_register) if base_register else None
                if index_register is None and base_register in vtables:
                    target = (vtables[base_register][0], displacement, vtables[base_register][1])
            elif REGISTER.fullmatch(operand):
                target = function_slots.get(canonical(operand))
            if target is not None:
                matches.append({
                    "call_rva": address - base,
                    "slot_offset": target[1],
                    "object": target[0],
                    "vptr_load_rva": target[2],
                    "start_rva": start_rva,
                    "end_rva": end_rva,
                    "before": [*previous, instruction],
                })

        if destination and mnemonic not in read_only:
            objects.pop(destination, None)
            vtables.pop(destination, None)
            function_slots.pop(destination, None)
        if destination:
            if source_object is not None:
                objects[destination] = source_object
            if source_vtable is not None:
                vtables[destination] = source_vtable
            if source_slot is not None:
                function_slots[destination] = source_slot

        if mnemonic == "call":
            for register in VOLATILE:
                objects.pop(register, None)
                vtables.pop(register, None)
                function_slots.pop(register, None)
        previous.append(instruction)

    return matches, 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument(
        "--object-offset", required=True, action="append",
        type=lambda value: int(value, 0),
        help="embedded-object offset relative to a candidate owner; repeatable",
    )
    parser.add_argument("--context", type=int, default=8)
    parser.add_argument(
        "--slot-offset",
        action="append",
        type=lambda value: int(value, 0),
        help="only print these vtable byte offsets; repeatable",
    )
    args = parser.parse_args()
    if not 0 <= args.context <= 20:
        parser.error("--context must be between 0 and 20")

    try:
        data = args.exe.read_bytes()
        pe = pefile.PE(data=data, fast_load=False)
    except (OSError, pefile.PEFormatError) as error:
        parser.error(f"could not read a valid PE executable: {error}")
    if pe.FILE_HEADER.Machine != pefile.MACHINE_TYPE["IMAGE_FILE_MACHINE_AMD64"]:
        parser.error("the selected executable is not AMD64")
    if not hasattr(pe, "DIRECTORY_ENTRY_EXCEPTION"):
        parser.error("the executable has no parsed AMD64 runtime-function directory")

    scanned_bytes = skipped_ranges = 0
    matches = []
    offsets = set(args.object_offset)
    last_progress = 0
    for entry in pe.DIRECTORY_ENTRY_EXCEPTION:
        runtime = entry.struct
        section = executable_section_for_rva(pe, runtime.BeginAddress)
        if section is not None and runtime.EndAddress > runtime.BeginAddress:
            scanned_bytes += runtime.EndAddress - runtime.BeginAddress
        found, skipped = scan_range(data, pe, entry, offsets, args.context)
        skipped_ranges += skipped
        if found:
            matches.extend(found)
        if scanned_bytes - last_progress >= 5 * 1024 * 1024:
            print(f"PROGRESS: scanned 0x{scanned_bytes:X} runtime-function bytes", flush=True)
            last_progress = scanned_bytes

    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"SCANNED_RUNTIME_FUNCTION_BYTES: {scanned_bytes}")
    print(f"SKIPPED_RUNTIME_RANGES: {skipped_ranges}")
    print(f"QAM_CANDIDATE_DISPATCHES: {len(matches)}")
    selected = matches
    if args.slot_offset is not None:
        allowed_slots = set(args.slot_offset)
        selected = [match for match in matches if match["slot_offset"] in allowed_slots]
        print(
            "FILTER_SLOT_OFFSETS: "
            + ", ".join(f"0x{offset:X}" for offset in sorted(allowed_slots))
        )
        print(f"FILTERED_DISPATCHES: {len(selected)}")
    for match in selected:
        owner_register, object_offset, object_origin = match["object"]
        print(
            f"\nCALL_RVA: 0x{match['call_rva']:X}; SLOT_OFFSET: 0x{match['slot_offset']:X}; "
            f"OBJECT_DERIVATION_RVA: 0x{object_origin:X}; OWNER_REGISTER: {owner_register}; OFFSET: 0x{object_offset:X}; "
            f"RANGE: 0x{match['start_rva']:X}-0x{match['end_rva']:X}; "
            f"VPTR_LOAD_RVA: 0x{match['vptr_load_rva']:X}"
        )
        for instruction in match["before"]:
            print(f"  {format_instruction(instruction, pe.OPTIONAL_HEADER.ImageBase)}")
    print(
        "\nLIMIT: Register tracking is intentionally local to one .pdata range; "
        "the object offset is a candidate identity until corroborated by RTTI or a constructor."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
