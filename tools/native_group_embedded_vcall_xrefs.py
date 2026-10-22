"""Find embedded-object virtual calls with control-flow across chained .pdata ranges."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import hashlib
from pathlib import Path
import re

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, Cs

from native_pdata_function_group import entry_key, read_chain_parent


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
READ_ONLY = {
    "cmp", "test", "call", "jmp", "ret", "push", "nop", "ud2", "int3",
    "je", "jne", "jz", "jnz", "ja", "jae", "jb", "jbe", "jg",
    "jge", "jl", "jle", "js", "jns", "jo", "jno", "jp", "jnp",
    "jecxz", "jrcxz", "loop", "loope", "loopne",
}


def canonical(register: str) -> str:
    if register in ALIASES:
        return ALIASES[register]
    if register.startswith("r") and register[1:-1].isdigit() and register[-1:] in {"d", "w", "b"}:
        return register[:-1]
    return register


def parse_memory(expression: str):
    base = index = None
    index_scale = 1
    displacement = 0
    for raw_term in TERM.findall(expression.replace(" ", "").lower()):
        sign = -1 if raw_term.startswith("-") else 1
        term = raw_term[1:] if raw_term[:1] in "+-" else raw_term
        if "*" in term:
            register, raw_scale = term.split("*", 1)
            if REGISTER.fullmatch(register):
                if sign < 0:
                    return None, None, 1, 0
                index = register
                try:
                    index_scale = int(raw_scale, 0)
                except ValueError:
                    return None, None, 1, 0
                if index_scale not in {1, 2, 4, 8}:
                    return None, None, 1, 0
            continue
        if REGISTER.fullmatch(term):
            if sign < 0:
                return None, None, 1, 0
            if base is None:
                base = term
            elif index is None:
                index = term
                index_scale = 1
        else:
            try:
                displacement += sign * int(term, 0)
            except ValueError:
                pass
    return base, index, index_scale, displacement


def split_operands(op_str: str) -> list[str]:
    return [part.strip().lower() for part in op_str.split(",")]


def executable_section_for_rva(pe: pefile.PE, rva: int):
    for section in pe.sections:
        end = section.VirtualAddress + max(section.Misc_VirtualSize, section.SizeOfRawData)
        if section.Characteristics & EXECUTABLE and section.VirtualAddress <= rva < end:
            return section
    return None


def object_expr(state, base_register: str, displacement: int, offsets: set[int]):
    base_register = canonical(base_register)
    if displacement == 0 and base_register in state["objects"]:
        return set(state["objects"][base_register])
    if displacement not in offsets:
        return set()
    owners = state["objects"].get(base_register) or {("arg", base_register)}
    return {("object", owner, displacement) for owner in owners}


def offset_objects(objects, displacement: int, offsets: set[int]):
    if displacement == 0:
        return set(objects)
    if displacement not in offsets:
        return set()
    return {("object", owner, displacement) for owner in objects}


def state_signature(state):
    return tuple(
        (kind, register, tuple(sorted(values, key=repr)))
        for kind in ("objects", "vtables", "methods", "scalars", "scaled", "constants")
        for register, values in sorted(state[kind].items())
        if values
    )


def copy_state(state):
    return {kind: {reg: set(values) for reg, values in state[kind].items()}
            for kind in ("objects", "vtables", "methods", "scalars", "scaled", "constants")}


def clear_register(state, register: str):
    for kind in ("objects", "vtables", "methods", "scalars", "scaled", "constants"):
        state[kind].pop(register, None)


def next_address(instruction, ranges, by_address, image_base):
    address, size, _, _ = instruction
    current_rva = address - image_base
    next_rva = current_rva + size
    if next_rva in by_address:
        current_range = ranges[current_rva]
        next_range = ranges[next_rva]
        if current_range == next_range or current_range[1] == next_rva:
            return next_rva
    return None


def branch_target(op_str: str, image_base: int):
    first = op_str.split(",", 1)[0].strip()
    try:
        value = int(first, 0)
    except ValueError:
        return None
    return value - image_base


def successors(instruction, ranges, by_address, image_base):
    address, _, mnemonic, op_str = instruction
    following = next_address(instruction, ranges, by_address, image_base)
    if mnemonic in {"ret", "retf", "iret", "ud2", "int3"}:
        return []
    if mnemonic == "jmp":
        target = branch_target(op_str, image_base)
        return [target] if target in by_address else []
    if mnemonic.startswith("j") or mnemonic.startswith("loop"):
        target = branch_target(op_str, image_base)
        result = [target] if target in by_address else []
        if following is not None:
            result.append(following)
        return list(dict.fromkeys(result))
    return [following] if following is not None else []


def transfer(instruction, incoming, offsets, index_field_offsets, index_strides, image_base):
    state = copy_state(incoming)
    address, _, mnemonic, op_str = instruction
    operands = split_operands(op_str)
    destination = canonical(operands[0]) if operands and REGISTER.fullmatch(operands[0]) else None
    source_objects = set()
    source_vtables = set()
    source_methods = set()
    source_scalars = set()
    source_scaled = set()
    source_constants = set()

    if mnemonic in {"lea", "mov", "movsxd"} and destination and len(operands) >= 2:
        source = operands[1]
        if REGISTER.fullmatch(source):
            source_register = canonical(source)
            source_objects = set(state["objects"].get(source_register, set()))
            source_vtables = set(state["vtables"].get(source_register, set()))
            source_methods = set(state["methods"].get(source_register, set()))
            source_scalars = set(state["scalars"].get(source_register, set()))
            source_scaled = set(state["scaled"].get(source_register, set()))
            source_constants = set(state["constants"].get(source_register, set()))
        elif "[" in source and "]" in source:
            base_register, index_register, index_scale, displacement = parse_memory(
                source[source.index("[") + 1:source.index("]")]
            )
            base_register = canonical(base_register) if base_register else None
            index_register = canonical(index_register) if index_register else None
            if mnemonic == "lea" and base_register:
                if index_register is None:
                    source_objects = object_expr(state, base_register, displacement, offsets)
                else:
                    base_objects = state["objects"].get(base_register, set())
                    base_scaled = state["scaled"].get(base_register, set())
                    index_objects = state["objects"].get(index_register, set())
                    index_scaled = state["scaled"].get(index_register, set())
                    index_constants = state["constants"].get(index_register, set())
                    if base_objects and index_constants:
                        for owner in base_objects:
                            for value in index_constants:
                                source_objects.update(
                                    offset_objects(base_objects & {owner}, displacement + value * index_scale, offsets)
                                )
                    indexed_objects = set()
                    if base_objects and index_scaled:
                        for term in index_scaled:
                            if index_scale != 1:
                                term = ("scaled-index", term, index_scale)
                            indexed_objects.update(
                                ("indexed-object", owner, term) for owner in base_objects
                            )
                    if base_scaled and index_objects and index_scale == 1:
                        for term in base_scaled:
                            indexed_objects.update(
                                ("indexed-object", owner, term) for owner in index_objects
                            )
                    source_objects.update(offset_objects(indexed_objects, displacement, offsets))
            elif base_register and index_register is None:
                if displacement in index_field_offsets:
                    owners = state["objects"].get(base_register) or {("arg", base_register)}
                    source_scalars = {
                        ("index-field", owner, displacement)
                        for owner in owners
                    }
                if displacement == 0:
                    source_vtables = {
                        ("vtable", obj, address - image_base)
                        for obj in state["objects"].get(base_register, set())
                    }
                elif displacement in offsets:
                    source_vtables = {
                        ("vtable", obj, address - image_base)
                        for obj in object_expr(state, base_register, displacement, offsets)
                    }
                if base_register in state["vtables"]:
                    source_methods = {
                        ("method", item[1], displacement, item[2])
                        for item in state["vtables"][base_register]
                    }
        else:
            try:
                source_constants = {int(source, 0)}
            except ValueError:
                pass

    if mnemonic == "imul" and destination and len(operands) >= 3:
        source_register = canonical(operands[1]) if REGISTER.fullmatch(operands[1]) else None
        try:
            stride = int(operands[2], 0)
        except ValueError:
            stride = None
        if source_register and stride in index_strides:
            source_scaled = {
                ("scaled-index", scalar, stride)
                for scalar in state["scalars"].get(source_register, set())
            }
            source_constants = {
                value * stride
                for value in state["constants"].get(source_register, set())
            }

    if mnemonic == "add" and destination and len(operands) >= 2:
        source = operands[1]
        if REGISTER.fullmatch(source):
            source_register = canonical(source)
            destination_objects = state["objects"].get(destination, set())
            destination_scaled = state["scaled"].get(destination, set())
            other_objects = state["objects"].get(source_register, set())
            other_scaled = state["scaled"].get(source_register, set())
            destination_constants = state["constants"].get(destination, set())
            other_constants = state["constants"].get(source_register, set())
            if destination_scaled and other_objects:
                source_objects = {
                    ("indexed-object", owner, term)
                    for owner in other_objects
                    for term in destination_scaled
                }
            elif destination_objects and other_scaled:
                source_objects = {
                    ("indexed-object", owner, term)
                    for owner in destination_objects
                    for term in other_scaled
                }
            elif destination_objects and other_constants:
                source_objects = {
                    obj
                    for owner in destination_objects
                    for value in other_constants
                    for obj in offset_objects({owner}, value, offsets)
                }
            elif destination_constants and other_objects:
                source_objects = {
                    obj
                    for owner in other_objects
                    for value in destination_constants
                    for obj in offset_objects({owner}, value, offsets)
                }
            if destination_constants and other_constants:
                source_constants = {
                    left + right
                    for left in destination_constants
                    for right in other_constants
                }
        else:
            try:
                displacement = int(source, 0)
            except ValueError:
                displacement = None
            if displacement in offsets:
                source_objects = {
                    ("object", owner, displacement)
                    for owner in state["objects"].get(destination, set())
                }
            if displacement is not None and state["constants"].get(destination):
                source_constants = {
                    value + displacement
                    for value in state["constants"][destination]
                }

    matches = []
    if mnemonic == "call" and operands:
        operand = operands[0]
        targets = set()
        if "[" in operand and "]" in operand:
            base_register, index_register, _, displacement = parse_memory(
                operand[operand.index("[") + 1:operand.index("]")]
            )
            base_register = canonical(base_register) if base_register else None
            if base_register and index_register is None:
                targets = {
                    (item[1], displacement, item[2])
                    for item in state["vtables"].get(base_register, set())
                }
        elif REGISTER.fullmatch(operand):
            base_register = canonical(operand)
            targets = {
                (item[1], item[2], item[3])
                for item in state["methods"].get(base_register, set())
            }
        receiver_objects = state["objects"].get("rcx", set())
        for obj, slot, vptr_rva in targets:
            if obj in receiver_objects:
                matches.append((address - image_base, slot, obj, vptr_rva))

    if mnemonic == "xchg":
        # Both operands are outputs; a memory-first form still overwrites its register.
        for operand in operands[:2]:
            if REGISTER.fullmatch(operand):
                clear_register(state, canonical(operand))
        return state, matches

    if destination and mnemonic not in READ_ONLY:
        clear_register(state, destination)
        if source_objects:
            state["objects"][destination] = source_objects
        if source_vtables:
            state["vtables"][destination] = source_vtables
        if source_methods:
            state["methods"][destination] = source_methods
        if source_scalars:
            state["scalars"][destination] = source_scalars
        if source_scaled:
            state["scaled"][destination] = source_scaled
        if source_constants:
            state["constants"][destination] = source_constants

    if mnemonic == "call":
        for register in VOLATILE:
            clear_register(state, register)
    return state, matches


def analyze_group(data, pe, members, offsets, index_field_offsets, index_strides,
                  slot_filter, seed_registers, required_immediates, context, max_states):
    base = pe.OPTIONAL_HEADER.ImageBase
    instructions = {}
    instruction_ranges = {}
    ranges = {}
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    skipped = []
    scanned = 0

    for entry in members:
        start, end = entry.BeginAddress, entry.EndAddress
        section = executable_section_for_rva(pe, start)
        if section is None or end <= start:
            skipped.append((start, end, "non-executable or invalid range"))
            continue
        offset = section.PointerToRawData + start - section.VirtualAddress
        code = data[offset:offset + end - start]
        if len(code) != end - start:
            skipped.append((start, end, "truncated raw bytes"))
            continue
        decoded = list(decoder.disasm_lite(code, base + start))
        if not decoded:
            skipped.append((start, end, "Capstone decoded no instructions; data-like/unclassified"))
            continue
        scanned += end - start
        rva_range = (start, end)
        for instruction in decoded:
            address, _, _, _ = instruction
            rva = address - base
            instructions[rva] = instruction
            instruction_ranges[rva] = rva_range
            ranges[rva] = rva_range

    if not instructions:
        return [], scanned, skipped, False, False, False

    has_required_immediate = not required_immediates
    if required_immediates:
        immediate_pattern = re.compile(r"(?<![\w])(?:0x[0-9a-f]+|[0-9]+)(?![\w])", re.IGNORECASE)
        for _, _, _, op_str in instructions.values():
            outside_memory = re.sub(r"\[[^\]]*\]", "", op_str)
            for token in immediate_pattern.findall(outside_memory):
                try:
                    if int(token, 0) in required_immediates:
                        has_required_immediate = True
                        break
                except ValueError:
                    continue
            if has_required_immediate:
                break
    if not has_required_immediate:
        return [], scanned, skipped, False, False, False

    # Limit expensive dataflow to groups containing a requested embedded offset.
    has_offset_seed = False
    for _, _, mnemonic, op_str in instructions.values():
        operands = split_operands(op_str)
        if mnemonic not in {"lea", "mov"} or len(operands) < 2 or "[" not in operands[1]:
            continue
        _, index_register, _, displacement = parse_memory(
            operands[1][operands[1].index("[") + 1:operands[1].index("]")]
        )
        if index_register is None and displacement in offsets:
            has_offset_seed = True
            break
    has_call_shape = False
    if seed_registers:
        for _, _, mnemonic, op_str in instructions.values():
            if mnemonic != "call":
                continue
            operands = split_operands(op_str)
            if not operands:
                continue
            operand = operands[0]
            if "[" in operand and "]" in operand:
                _, index_register, _, displacement = parse_memory(
                    operand[operand.index("[") + 1:operand.index("]")]
                )
                if index_register is None and (slot_filter is None or displacement in slot_filter):
                    has_call_shape = True
                    break
            elif REGISTER.fullmatch(operand):
                has_call_shape = True
                break
    if not has_offset_seed and not has_call_shape:
        return [], scanned, skipped, False, False, True

    root = min(entry.BeginAddress for entry in members)
    starts = sorted({entry.BeginAddress for entry in members if entry.BeginAddress in instructions})
    empty_state = {"objects": {}, "vtables": {}, "methods": {}, "scalars": {}, "scaled": {}, "constants": {}}
    work = deque((start, empty_state) for start in starts) if has_offset_seed else deque()
    if seed_registers and root in instructions:
        seeded = copy_state(empty_state)
        for register in seed_registers:
            seeded["objects"][register] = {("arg", register)}
        work.append((root, seeded))
    seen = defaultdict(set)
    matches = {}
    truncated = False

    while work:
        address, state = work.popleft()
        signature = state_signature(state)
        if signature in seen[address]:
            continue
        if len(seen[address]) >= max_states:
            truncated = True
            continue
        seen[address].add(signature)
        instruction = instructions.get(address)
        if instruction is None:
            continue
        output_state, call_matches = transfer(
            instruction, state, offsets, index_field_offsets, index_strides, base
        )
        for call_rva, slot, obj, vptr_rva in call_matches:
            if slot_filter is None or slot in slot_filter:
                matches[(call_rva, slot, obj)] = (call_rva, slot, obj, vptr_rva)
        for target in successors(instruction, ranges, instructions, base):
            work.append((target, output_state))

    result = []
    for call_rva, slot, obj, vptr_rva in sorted(matches.values(), key=lambda item: (item[0], item[1], repr(item[2]))):
        call_instruction = instructions.get(call_rva)
        call_range = instruction_ranges.get(call_rva)
        history = []
        if call_range:
            prior = [rva for rva in sorted(instructions) if call_range[0] <= rva < call_rva]
            for rva in prior[-context:]:
                history.append(instructions[rva])
        result.append({
            "call_rva": call_rva,
            "slot_offset": slot,
            "object": obj,
            "vptr_load_rva": vptr_rva,
            "root_rva": root,
            "range": call_range,
            "before": history,
            "instruction": call_instruction,
        })
    return result, scanned, skipped, truncated, True, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--object-offset", action="append", default=[], type=lambda value: int(value, 0))
    parser.add_argument("--index-field-offset", action="append", default=[], type=lambda value: int(value, 0),
                        help="track a scalar field as a possible signed vector index; repeatable")
    parser.add_argument("--index-stride", action="append", default=[], type=lambda value: int(value, 0),
                        help="track only this scaled-index multiplier; repeatable")
    parser.add_argument("--root-rva", action="append", default=[], type=lambda value: int(value, 0),
                        help="analyze only this resolved UNW_FLAG_CHAININFO root; repeatable")
    parser.add_argument("--seed-object-register", action="append", choices=("rcx", "rdx", "r8", "r9"))
    parser.add_argument("--slot-offset", action="append", type=lambda value: int(value, 0))
    parser.add_argument("--require-immediate", action="append", default=[], type=lambda value: int(value, 0),
                        help="analyze only function groups containing this instruction immediate; repeatable")
    parser.add_argument("--context", type=int, default=8)
    parser.add_argument("--max-states-per-instruction", type=int, default=32)
    parser.add_argument("--max-results", type=int, default=100)
    args = parser.parse_args()
    if not 0 <= args.context <= 20:
        parser.error("--context must be between 0 and 20")
    if not 1 <= args.max_states_per_instruction <= 512:
        parser.error("--max-states-per-instruction must be between 1 and 512")
    if not 1 <= args.max_results <= 1000:
        parser.error("--max-results must be between 1 and 1000")
    if not args.object_offset and not args.seed_object_register:
        parser.error("provide --object-offset or --seed-object-register")

    try:
        data = args.exe.read_bytes()
        pe = pefile.PE(data=data, fast_load=False)
    except (OSError, pefile.PEFormatError) as error:
        parser.error(f"could not read a valid PE executable: {error}")
    if pe.FILE_HEADER.Machine != pefile.MACHINE_TYPE["IMAGE_FILE_MACHINE_AMD64"]:
        parser.error("the selected executable is not AMD64")
    if not hasattr(pe, "DIRECTORY_ENTRY_EXCEPTION"):
        parser.error("the executable has no parsed AMD64 runtime-function directory")

    entries = [item.struct for item in pe.DIRECTORY_ENTRY_EXCEPTION]
    by_key = {entry_key(entry): entry for entry in entries}
    parent_map = {}
    try:
        for entry in entries:
            key = entry_key(entry)
            parent = read_chain_parent(pe, entry)
            if parent is not None and parent not in by_key:
                raise ValueError(f"chained parent 0x{parent[0]:X}-0x{parent[1]:X} is missing")
            parent_map[key] = parent
    except ValueError as error:
        parser.error(str(error))

    roots = {}

    def resolve_root(start):
        if start in roots:
            return roots[start]
        path = []
        seen = set()
        current = start
        while current not in roots:
            if current in seen or current not in by_key:
                raise ValueError("invalid cycle or missing parent in UNW_FLAG_CHAININFO")
            seen.add(current)
            path.append(current)
            parent = parent_map[current]
            if parent is None:
                root = current
                break
            current = parent
        else:
            root = roots[current]
        for key in path:
            roots[key] = root
        return root

    try:
        groups = defaultdict(list)
        for entry in entries:
            groups[resolve_root(entry_key(entry))].append(entry)
    except ValueError as error:
        parser.error(str(error))

    offsets = set(args.object_offset)
    index_field_offsets = set(args.index_field_offset)
    index_strides = set(args.index_stride)
    seed_registers = {canonical(register) for register in (args.seed_object_register or [])}
    slot_filter = set(args.slot_offset) if args.slot_offset else None
    selected_roots = set(args.root_rva)
    available_roots = {root[0] for root in groups}
    missing_roots = selected_roots - available_roots
    if missing_roots:
        parser.error("no resolved .pdata group root for: " + ", ".join(f"0x{value:X}" for value in sorted(missing_roots)))
    total_bytes = analyzed_groups = truncated_groups = groups_with_offset_or_seed = 0
    groups_with_required_immediate = 0
    skipped_ranges = []
    matches = []
    truncated_roots = []
    progress = 0
    for root, members in sorted(groups.items(), key=lambda item: item[0][0]):
        if selected_roots and root[0] not in selected_roots:
            continue
        found, scanned, skipped_details, truncated, has_seed, has_required_immediate = analyze_group(
            data, pe, members, offsets, index_field_offsets, index_strides,
            slot_filter, seed_registers,
            set(args.require_immediate), args.context,
            args.max_states_per_instruction,
        )
        total_bytes += scanned
        skipped_ranges.extend(skipped_details)
        groups_with_offset_or_seed += int(has_seed)
        groups_with_required_immediate += int(has_required_immediate)
        if found or truncated:
            analyzed_groups += 1
            matches.extend(found)
        truncated_groups += int(truncated)
        if truncated:
            truncated_roots.append(root[0])
        if total_bytes - progress >= 5 * 1024 * 1024:
            print(f"PROGRESS: group-aware scanned 0x{total_bytes:X} runtime-function bytes", flush=True)
            progress = total_bytes

    base = pe.OPTIONAL_HEADER.ImageBase
    print(f"FILE: {args.exe.name}")
    print(f"SIZE: {len(data)}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    print(f"IMAGE_BASE: 0x{base:X}")
    print(f"SCANNED_RUNTIME_FUNCTION_BYTES: {total_bytes}")
    if selected_roots:
        print("FILTER_ROOT_RVAS: " + ", ".join(f"0x{value:X}" for value in sorted(selected_roots)))
    if args.require_immediate:
        print(f"GROUPS_WITH_REQUIRED_IMMEDIATE: {groups_with_required_immediate}")
    skipped_bytes = sum(end - start for start, end, _ in skipped_ranges)
    print(f"UNDECODED_RUNTIME_RANGES: {len(skipped_ranges)}")
    print(f"UNDECODED_RUNTIME_BYTES: {skipped_bytes}")
    for start, end, reason in skipped_ranges:
        print(f"UNDECODED_RANGE: 0x{start:X}-0x{end:X}; {reason}")
    print(f"GROUPS_WITH_MATCHES_OR_TRUNCATION: {analyzed_groups}")
    print(f"GROUPS_WITH_OFFSET_OR_ARGUMENT_SEED: {groups_with_offset_or_seed}")
    print(f"TRUNCATED_GROUPS: {truncated_groups}")
    if index_field_offsets:
        print("FILTER_INDEX_FIELD_OFFSETS: " + ", ".join(f"0x{value:X}" for value in sorted(index_field_offsets)))
    if index_strides:
        print("FILTER_INDEX_STRIDES: " + ", ".join(f"0x{value:X}" for value in sorted(index_strides)))
    for root_rva in truncated_roots:
        print(f"TRUNCATED_ROOT_RVA: 0x{root_rva:X}")
    print(f"CANDIDATE_DISPATCHES: {len(matches)}")
    if slot_filter is not None:
        print("FILTER_SLOT_OFFSETS: " + ", ".join(f"0x{value:X}" for value in sorted(slot_filter)))
    for match in matches[:args.max_results]:
        start, end = match["range"]
        print(
            f"\nCALL_RVA: 0x{match['call_rva']:X}; SLOT_OFFSET: 0x{match['slot_offset']:X}; "
            f"OBJECT_EXPR: {match['object']!r}; ROOT: 0x{match['root_rva']:X}; "
            f"RANGE: 0x{start:X}-0x{end:X}; VPTR_LOAD_RVA: 0x{match['vptr_load_rva']:X}"
        )
        for instruction in match["before"]:
            address, _, mnemonic, op_str = instruction
            print(f"  0x{address - base:X}: {mnemonic} {op_str}".rstrip())
    if len(matches) > args.max_results:
        print(f"OMITTED_CANDIDATE_DISPATCHES: {len(matches) - args.max_results}")
        instruction = match["instruction"]
        if instruction:
            address, _, mnemonic, op_str = instruction
            print(f"  0x{address - base:X}: {mnemonic} {op_str}".rstrip())
    print(
        "LIMIT: register facts are propagated only along decoded direct control-flow edges "
        "inside each UNW_FLAG_CHAININFO group. Selected signed index fields and scale immediates are tracked "
        "only when explicitly requested. No pointer provenance is propagated across a call into its callee; "
        "object offsets remain candidates until RTTI/constructor proof."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
