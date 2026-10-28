"""Selected static PE/unwind/PDB checks for the exact owned Microsoft candidate."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import struct
import pefile

FROZEN_ARTIFACTS = {
    "0.10.5-native-test": {
        "module_sha256": "8e6dd664c1fc0982a435b5932d0c9f006f1522926aa28b9556b7f2ce7dcb4695",
        "module_bytes": 747520,
        "pdb_sha256": "568376af58a3d4475cb6ceaea02b495e602a001bc8875d09734dc84abb183b6d",
        "pdb_bytes": 11210752,
    },
    "0.10.6-native-test": {
        "module_sha256": "30cc9542a2af3529fd4f3a2299d6331bddf51b61f8213a0a1a779b472789de3d",
        "module_bytes": 749568,
        "pdb_sha256": "5f32c8d508d3e8e4d03dcfdee7e2fdf533abd6ce600d85530d0cfd7aae47b8d1",
        "pdb_bytes": 11210752,
    },
}


def audit(module,pdb,artifact_version="0.10.5-native-test"):
    expected=FROZEN_ARTIFACTS[artifact_version]
    if module.stat().st_size!=expected["module_bytes"] or pdb.stat().st_size!=expected["pdb_bytes"]:
        raise ValueError("Exact artifact extents differ; refuse reads and image decoding")
    data=module.read_bytes(); symbols=pdb.read_bytes()
    if (hashlib.sha256(data).hexdigest()!=expected["module_sha256"] or
            hashlib.sha256(symbols).hexdigest()!=expected["pdb_sha256"]):
        raise ValueError("Not the exact candidate/symbol pair; refuse image decoding")
    if len(symbols)>32*1024*1024 or not symbols.startswith(b'Microsoft C/C++ MSF 7.00'):
        raise ValueError("Unsupported symbol input")
    pe=pefile.PE(data=data,fast_load=True)
    if pe.FILE_HEADER.Machine!=0x8664: raise ValueError("Expected x64 PE")
    text=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.text')
    low=text.VirtualAddress; high=low+text.Misc_VirtualSize
    directory=pe.OPTIONAL_HEADER.DATA_DIRECTORY[3]
    if directory.Size%12: raise ValueError("Incomplete runtime function table")
    entries=[struct.unpack('<III',pe.get_data(directory.VirtualAddress+i,12))
             for i in range(0,directory.Size,12)]
    if entries!=sorted(entries): raise ValueError("Unsorted runtime function table")
    seen=set(); chains=0; maximum=0; versions=collections.Counter()
    for entry in entries:
        versions[pe.get_data(entry[2],1)[0]&7]+=1
        path=set(); depth=0
        while True:
            begin,end,unwind=entry
            if not low<=begin<end<=high or entry in path or depth>=64:
                raise ValueError("Runtime range, cycle or depth control failed")
            path.add(entry); seen.add(entry); depth+=1
            raw=pe.get_data(unwind,4)
            # V1/V2 share these header/chain fields. V2 epilog opcodes are
            # outside these selected structural checks, as are all opcodes.
            if len(raw)!=4 or raw[0]&7 not in (1,2): raise ValueError("Unsupported unwind header")
            flags=raw[0]>>3
            if flags&~7: raise ValueError("Unknown unwind flags")
            code_end=(4+2*raw[2]+3)&~3
            if not flags&4: break
            if flags&3: raise ValueError("Incompatible chained/handler flags")
            chain=pe.get_data(unwind+code_end,12)
            if len(chain)!=12: raise ValueError("Incomplete chained runtime function")
            entry=struct.unpack('<III',chain); chains+=1
        maximum=max(maximum,depth)
    pe.parse_data_directories(directories=[3,6,0,1])
    debug=next(x for x in pe.DIRECTORY_ENTRY_DEBUG if x.struct.Type==2)
    cv=data[debug.struct.PointerToRawData:debug.struct.PointerToRawData+debug.struct.SizeOfData]
    if cv[:4]!=b'RSDS': raise ValueError("Expected CodeView RSDS record")
    guid=cv[4:20]; age=struct.unpack_from('<I',cv,20)[0]
    block,free,total,size,reserved,map_block=struct.unpack_from('<6I',symbols,32)
    if block not in (512,1024,2048,4096) or len(symbols)!=block*total:
        raise ValueError("Unsupported MSF extent")
    count=(size+block-1)//block
    blocks=struct.unpack_from('<'+'I'*count,symbols,map_block*block)
    directory=b''.join(symbols[x*block:(x+1)*block] for x in blocks)[:size]
    streams=struct.unpack_from('<I',directory)[0]
    sizes=struct.unpack_from('<'+'I'*streams,directory,4)
    offset=4+4*streams; info=None
    for index,size in enumerate(sizes):
        count=0 if size==0xffffffff else (size+block-1)//block
        indices=struct.unpack_from('<'+'I'*count,directory,offset) if count else ()
        offset+=4*count
        if index==1:
            info=b''.join(symbols[x*block:(x+1)*block] for x in indices)[:size]
            break
    if info is None or info[12:28]!=guid or struct.unpack_from('<I',info,8)[0]!=age:
        raise ValueError("PDB identity is not the selected module's CodeView identity")
    return {"status":"SELECTED_STATIC_CHECKS_COMPLETED","artifact_version":artifact_version,
            "module_sha256":expected["module_sha256"],"bytes":len(data),
            "pdb_sha256":hashlib.sha256(symbols).hexdigest(),"pdb_guid_and_age_match":True,
            "sections":[s.Name.rstrip(b'\0').decode() for s in pe.sections],
            "imports":[x.dll.decode() for x in pe.DIRECTORY_ENTRY_IMPORT],
            "exports":[x.name.decode() for x in pe.DIRECTORY_ENTRY_EXPORT.symbols if x.name],
            "overlay_present":pe.get_overlay_data_start_offset() is not None,
            "unwind":{"runtime_function_entries":len(entries),"unique_chained_entries":len(seen),
                      "chain_steps":chains,"max_depth":maximum,"bounds_sorted_and_no_cycles":True,
                      "table_header_versions":dict(versions)},
            "pefile_version":pefile.__version__,"pefile_warnings":pe.get_warnings(),
            "limits":["Unwind opcode/prologue semantics and all handler data are not validated.",
                      "Parser warnings are retained, not converted to a zero-warning claim.",
                      "PDB identity matching is not complete symbol-content validation.",
                      "These structural checks are not an antivirus or gameplay verdict."]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('module','pdb','output'): p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--artifact-version',choices=sorted(FROZEN_ARTIFACTS),default="0.10.5-native-test")
    args=p.parse_args(); report={"status":"TOOL_ERROR"}
    try: report=audit(args.module,args.pdb,args.artifact_version)
    finally: args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({"status":report['status'],"unwind":report['unwind'],
                      "pdb_guid_and_age_match":report['pdb_guid_and_age_match'],
                      "parser_warnings":len(report['pefile_warnings'])}))


if __name__=='__main__': main()
