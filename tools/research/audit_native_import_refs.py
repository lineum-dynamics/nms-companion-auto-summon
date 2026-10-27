"""Read-only IAT-reference audit of a hash-identified owned native module.

Decode physical Win64 exception ranges; do not infer a complete call graph,
runtime execution, argument provenance, or antivirus matching rules.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import struct
import sys

import capstone
from capstone import x86_const as x86
import pefile


def symbols(data, pe):
    base = pe.FILE_HEADER.PointerToSymbolTable
    count = pe.FILE_HEADER.NumberOfSymbols
    string_base = base + count * 18
    string_size = struct.unpack_from('<I', data, string_base)[0]
    assert 4 <= string_size <= len(data) - string_base
    result = collections.defaultdict(list)
    index = 0
    while index < count:
        offset = base + index * 18
        raw_name, value, section, kind, storage, aux = struct.unpack_from('<8sIhHBB', data, offset)
        if raw_name[:4] == b'\0' * 4:
            name_offset = string_base + struct.unpack_from('<I', raw_name, 4)[0]
            assert string_base <= name_offset < string_base + string_size
            name = data[name_offset:data.index(b'\0', name_offset, string_base + string_size)].decode('utf-8', 'replace')
        else:
            name = raw_name.rstrip(b'\0').decode('utf-8', 'replace')
        if 0 < section <= len(pe.sections) and kind & 0x20 and name:
            rva = pe.sections[section - 1].VirtualAddress + value
            result[rva].append(name)
        index += 1 + aux
    assert index == count
    return result


def root_begin(pe, begin, unwind, depth=0):
    assert depth < 16
    header = pe.get_data(unwind, 4)
    assert len(header) == 4
    flags = header[0] >> 3
    if flags & 4:
        chain = unwind + ((4 + header[2] * 2 + 3) & ~3)
        parent_begin, parent_end, parent_unwind = struct.unpack('<III', pe.get_data(chain, 12))
        return root_begin(pe, parent_begin, parent_unwind, depth + 1)
    return begin


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = args.image.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != args.expected_sha256:
        raise ValueError('Input hash mismatch; no decoding performed')
    pe = pefile.PE(data=data)
    assert pe.FILE_HEADER.Machine == 0x8664
    image_base = pe.OPTIONAL_HEADER.ImageBase
    names = symbols(data, pe)
    imports = {}
    for dll in pe.DIRECTORY_ENTRY_IMPORT:
        for entry in dll.imports:
            name = entry.name.decode('ascii') if entry.name else f'ordinal:{entry.ordinal}'
            imports[entry.address - image_base] = {'dll': dll.dll.decode('ascii'), 'name': name}
    selected = {'Sleep', 'SleepConditionVariableSRW', 'SuspendThread', 'ResumeThread',
                'GetThreadContext', 'SetThreadContext', 'WriteProcessMemory',
                'ReadProcessMemory', 'GetProcAddress', 'CreateThread', '_beginthreadex'}
    audit = {value['name']: {'iat_rva': hex(rva), 'references': []}
             for rva, value in imports.items() if value['name'] in selected}
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    decoder.detail = True
    coverage = {'exception_ranges': 0, 'bytes_in_exception_ranges': 0,
                'decoded_bytes': 0, 'instructions': 0, 'incomplete_ranges': []}
    for entry in pe.DIRECTORY_ENTRY_EXCEPTION:
        begin, end = entry.struct.BeginAddress, entry.struct.EndAddress
        assert begin < end
        section = pe.get_section_by_rva(begin)
        assert section and section.Characteristics & 0x20000000
        assert end <= section.VirtualAddress + section.Misc_VirtualSize
        root = root_begin(pe, begin, entry.struct.UnwindData)
        block = pe.get_data(begin, end - begin)
        coverage['exception_ranges'] += 1
        coverage['bytes_in_exception_ranges'] += len(block)
        decoded = 0
        for instruction in decoder.disasm(block, image_base + begin):
            decoded += instruction.size
            coverage['instructions'] += 1
            for operand in instruction.operands:
                if operand.type != x86.X86_OP_MEM or operand.mem.base != x86.X86_REG_RIP:
                    continue
                target = instruction.address + instruction.size + operand.mem.disp - image_base
                if target not in imports or imports[target]['name'] not in selected:
                    continue
                audit[imports[target]['name']]['references'].append({
                    'instruction_rva': hex(instruction.address - image_base),
                    'instruction': instruction.mnemonic + ' ' + instruction.op_str,
                    'physical_range': [hex(begin), hex(end)], 'root_begin': hex(root),
                    'exact_root_symbols': names.get(root, []),
                    'exact_range_symbols': names.get(begin, []),
                    'reference_kind': 'rip_relative_memory_operand',
                })
        coverage['decoded_bytes'] += decoded
        if decoded != len(block):
            coverage['incomplete_ranges'].append({'begin': hex(begin), 'end': hex(end), 'decoded_bytes': decoded})
    # A known production source call is a positive control for IAT resolution.
    assert any('InitializeASI' in r['exact_root_symbols'] for r in audit['CreateThread']['references'])
    assert audit['Sleep']['references'] and audit['WriteProcessMemory']['references']
    result = {
        'schema': 1, 'kind': 'bounded-owned-module-iat-reference-audit',
        'image_sha256': actual, 'image_bytes': len(data), 'image_base': hex(image_base),
        'tools': {'python': sys.version.split()[0], 'pefile': pefile.__version__, 'capstone': capstone.__version__},
        'coverage': coverage, 'imports': sorted(imports.values(), key=lambda x: (x['dll'], x['name'])),
        'selected_iat_references': audit,
        'limits': ['Physical exception ranges only; standalone import stubs and code outside them are not coverage.',
                   'Records IAT memory references including register loads; does not establish a complete call graph.',
                   'No propagation of API arguments, arbitrary dynamic lookup targets or runtime execution.',
                   'No matching antivirus rule or false-positive classification is inferred.'],
    }
    args.output.write_bytes((json.dumps(result, indent=2, ensure_ascii=True) + '\n').encode())
    print(json.dumps({'image_sha256': actual, 'coverage': coverage,
                      'selected': {k: {'references': len(v['references']),
                                       'root_symbols': sorted({n for r in v['references'] for n in r['exact_root_symbols']})}
                                   for k, v in audit.items()}}, indent=2))


if __name__ == '__main__':
    main()
