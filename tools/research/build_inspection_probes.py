"""Build a fixed inspection/core 2x2 diagnostic comparison, never player bytes."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import build_component_probes as common

ROOT=common.ROOT
digest=common.digest
CASES={
    "baseline": (False,False),
    "inspection": (True,False),
    "core": (False,True),
    "inspection-core": (True,True),
}


def export_names(text):
    # Debug-enabled MSVC dumpbin appends "= implementation" to named rows.
    return sorted(re.findall(r'^\s+\d+\s+[0-9A-Fa-f]+\s+[0-9A-Fa-f]+\s+(\w+)(?:\s+=\s+\S+)?\s*$',text,re.M))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True); args=p.parse_args()
    if (os.name!='nt' or os.environ.get('GITHUB_ACTIONS')!='true' or
            os.environ.get('GITHUB_REPOSITORY')!='lineum-dynamics/nms-companion-auto-summon'):
        raise ValueError('Owned Windows CI only')
    output=args.output.resolve()
    if not output.is_relative_to(ROOT/'build') or output.exists(): raise ValueError('Use a new owned build directory')
    compiler=Path(shutil.which('cl.exe') or ''); rc=Path(shutil.which('rc.exe') or ''); inspect=Path(shutil.which('dumpbin.exe') or '')
    if any(not x.is_file() for x in (compiler,rc,inspect)): raise ValueError('Use the verified installed tools')
    common.dependencies(source_root=ROOT); common.locales(locales_dir=ROOT/'locales',source_root=ROOT)
    native=ROOT/'native'; profile=common.load_native_profile(ROOT/'native_compatibility.json')
    mapping=common.load_native_mapping(profile)
    sources=sorted(x for x in native.rglob('*') if x.is_file())+sorted((ROOT/'locales').glob('*.json'))
    sources += [ROOT/x for x in ('native_compatibility.json','native_mappings.json',
        'tools/research/build_inspection_probes.py','tools/research/build_component_probes.py',
        'tools/research/component_probe.cpp','tools/research/inspection_probe_stub.cpp',
        'tools/research/inspection_probe_host.cpp','tools/generate_native_catalog.py',
        'tools/native_compatibility.py','tools/native_mapping.py')]
    before={x.relative_to(ROOT).as_posix():digest(x) for x in sources}
    output.mkdir(); generated=output/'generated'; generated.mkdir()
    common.generate(generated/'catalog.hpp'); common.write_mapping_header(mapping,generated/'native_mapping_profile.hpp')
    (generated/'compatibility_profile.hpp').write_text('#pragma once\nnamespace cas::profile {\n'+
        'inline constexpr char exe_sha256[] = '+json.dumps(profile['exe_sha256'])+';\n'+
        'inline constexpr char steam_build[] = '+json.dumps(profile['steam_build'])+';\n}\n',encoding='utf-8',newline='\n')
    report={'schema':1,'kind':'fixed-inspection-core-factorial-probes','controller_revision':os.environ.get('GITHUB_SHA'),
            'compiler_sha256':digest(compiler),'sources':before,
            'generated':{x.name:digest(x) for x in generated.glob('*.hpp')},'cases':[],
            'game_access':False,'player_artifact_modified':False,'antivirus_upload_performed':False,'completed':False,
            'design':'2x2 host inspection versus inert ABI stub, crossed with core absent/present; identical exports/resource/link policy',
            'limits':['No bootstrap or gameplay activation is linked. A fixture negative does not exclude interactions or reachability.',
                      'Only status and current-owned-EXE inspection/stub are called; core methods are retained but never called.',
                      'No probe is a player replacement. No automatic multivendor upload.']}
    def run(command,cwd,timeout=300,env=None):
        r=subprocess.run([str(x) for x in command],cwd=cwd,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
        if r.returncode: raise RuntimeError('Owned inspection command failed: '+r.stdout+r.stderr)
        return r.stdout
    try:
        host=output/'cas-inspection-host.exe'
        run([compiler,'/nologo','/std:c++17','/EHsc','/O2','/W4','/WX','/MT','/I'+str(native/'include'),
             ROOT/'tools/research/inspection_probe_host.cpp','/Fe'+str(host),'/link','/INCREMENTAL:NO','/DYNAMICBASE','/NXCOMPAT','/Brepro'],output)
        env={k:v for k,v in os.environ.items() if k.upper() in
             {'SYSTEMROOT','WINDIR','SYSTEMDRIVE','PATH','TEMP','TMP','GITHUB_ACTIONS','GITHUB_REPOSITORY'}}
        includes=['/I'+str(x) for x in (native/'include',native/'third_party',native/'third_party/minhook/include',generated)]
        for label,(production,core) in CASES.items():
            directory=output/label; directory.mkdir(); objects=[]
            symbols=['/Z7','/pathmap:'+str(directory)+'=C:\\cas-inspection,'+str(output)+'=C:\\cas-generated,'+str(ROOT)+'=C:\\cas-source']
            if core:
                for name in ('buffer.c','hook.c','trampoline.c','hde/hde64.c'):
                    obj=directory/(Path(name).stem+'.obj')
                    run([compiler,'/nologo','/TC','/std:c11','/O2','/W4','/MT',*symbols,'/c',native/'third_party/minhook/src'/name,'/Fo'+str(obj)],directory)
                    objects.append(obj)
            resource=directory/'version.rc'
            resource.write_text('#include <windows.h>\n1 VERSIONINFO\nFILEVERSION 0,0,0,2\nPRODUCTVERSION 0,0,0,2\nFILEFLAGSMASK 0x3fL\nFILEFLAGS VS_FF_PRERELEASE\nFILEOS VOS_NT_WINDOWS32\nFILETYPE VFT_DLL\nBEGIN\n BLOCK "StringFileInfo"\n BEGIN\n  BLOCK "040904b0"\n  BEGIN\n   VALUE "CompanyName", "Lineum Dynamics\\0"\n   VALUE "FileDescription", "Owned inspection diagnostic - not a player mod\\0"\n   VALUE "ProductName", "Companion Auto Summon inspection diagnostic\\0"\n   VALUE "OriginalFilename", "CASInspectionProbe.dll\\0"\n  END\n END\n BLOCK "VarFileInfo"\n BEGIN\n  VALUE "Translation", 0x0409, 1200\n END\nEND\n',encoding='utf-8',newline='\n')
            res=directory/'version.res'; run([rc,'/nologo','/fo',res,resource],directory)
            binary=directory/'CASInspectionProbe.dll'
            inspection=native/'src/probe.cpp' if production else ROOT/'tools/research/inspection_probe_stub.cpp'
            components=common.CASES['core'] if core else []
            run([compiler,'/nologo','/std:c++17','/permissive-','/Zc:__cplusplus','/O2','/W4','/EHsc','/MT','/utf-8',
                 '/DUNICODE','/D_UNICODE','/D_WIN32_WINNT=0x0A00','/D_CRT_SECURE_NO_WARNINGS',
                 '/DCAS_NATIVE_RUNTIME','/DCAS_PROBE_BUILD','/DCAS_RESPAWN_OBSERVER','/DCAS_TELEPORT_CANDIDATE_TRIAL',
                 *includes,*symbols,'/LD',ROOT/'tools/research/component_probe.cpp',inspection,
                 *(native/'src'/(name+'.cpp') for name in components),*objects,res,
                 'bcrypt.lib','advapi32.lib','shell32.lib','ole32.lib','uuid.lib','user32.lib','/Fe'+str(binary),
                 '/link','/DYNAMICBASE','/NXCOMPAT','/INCREMENTAL:NO','/Brepro','/DEBUG:FULL','/PDBALTPATH:%_PDB%','/OPT:NOREF','/OPT:NOICF'],directory)
            identity=digest(binary)
            smoke=json.loads(run([host,binary,'inspection' if production else 'stub'],output,30,env))
            if not smoke.get('passed') or digest(binary)!=identity: raise ValueError('Inspection smoke/input check failed')
            if smoke['host_sha256']!=(digest(host) if production else ''): raise ValueError('Owned EXE hash/stub control failed')
            pe=run([inspect,'/headers','/imports','/exports',binary],directory)
            exports=export_names(pe)
            report['cases'].append({'label':label,'production_inspection':production,'core_included':core,
                'production_cpp_sources':(['probe'] if production else [])+components,
                'minhook_included':core,'sha256':identity,'bytes':binary.stat().st_size,
                'resource_sha256':digest(resource),'exports':exports,'smoke':smoke,
                'imports':sorted(set(re.findall(r'^\s+([A-Za-z0-9_.-]+\.dll)\s*$',pe,re.M)))})
            if exports!=['CasComponentProbeStatus','CasInspectHost']:
                raise ValueError('Matched export control differs: '+repr(exports)+'; inspect owned dumpbin output: '+pe[-6000:])
        if before!={x.relative_to(ROOT).as_posix():digest(x) for x in sources}: raise ValueError('Source changed during fixed probe build')
        if len(report['cases'])!=4 or len({x['resource_sha256'] for x in report['cases']})!=1: raise ValueError('Fixed resource/count controls differ')
        report['completed']=True
    finally:
        (output/'inspection-probes.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'completed':True,'cases':report['cases']}))


if __name__=='__main__': main()
