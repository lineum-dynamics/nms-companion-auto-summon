"""Build one preregistered four-library static component comparison in CI."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from generate_native_catalog import generate
from native_compatibility import load_native_profile
from native_mapping import load_native_mapping,write_mapping_header
from validate_native_dependencies import validate as dependencies
from validate_locales import validate as locales

CASES={
    'crt':[],
    'minhook':[],
    'binding':['binding_guard'],
    'core':['binding_guard','policy','selection','storage','runtime','backup','menu'],
}


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if (os.name!='nt' or os.environ.get('GITHUB_ACTIONS')!='true' or
            os.environ.get('GITHUB_REPOSITORY')!='lineum-dynamics/nms-companion-auto-summon'):
        raise ValueError('Owned Windows CI only')
    output=args.output.resolve()
    if not output.is_relative_to(ROOT/'build') or output.exists(): raise ValueError('Use a new owned build directory')
    compiler=Path(shutil.which('cl.exe') or ''); rc=Path(shutil.which('rc.exe') or ''); inspect=Path(shutil.which('dumpbin.exe') or '')
    if any(not x.is_file() for x in (compiler,rc,inspect)): raise ValueError('Use the signed installed Microsoft toolchain')
    dependencies(source_root=ROOT); locales(locales_dir=ROOT/'locales',source_root=ROOT)
    native=ROOT/'native'; profile=load_native_profile(ROOT/'native_compatibility.json'); mapping=load_native_mapping(profile)
    sources=sorted(x for x in native.rglob('*') if x.is_file())+sorted((ROOT/'locales').glob('*.json'))
    sources += [ROOT/x for x in ('native_compatibility.json','native_mappings.json',
        'tools/research/build_component_probes.py','tools/research/component_probe.cpp','tools/research/component_probe_host.cpp')]
    before={x.relative_to(ROOT).as_posix():digest(x) for x in sources}
    output.mkdir(); generated=output/'generated'; generated.mkdir()
    generate(generated/'catalog.hpp'); write_mapping_header(mapping,generated/'native_mapping_profile.hpp')
    (generated/'compatibility_profile.hpp').write_text('#pragma once\nnamespace cas::profile {\n'+
        'inline constexpr char exe_sha256[] = '+json.dumps(profile['exe_sha256'])+';\n'+
        'inline constexpr char steam_build[] = '+json.dumps(profile['steam_build'])+';\n}\n',encoding='utf-8',newline='\n')
    report={'schema':1,'kind':'fixed-inert-static-component-probes','controller_revision':os.environ.get('GITHUB_SHA'),
            'compiler_sha256':digest(compiler),'sources':before,'cases':[],
            'game_access':False,'player_artifact_modified':False,'antivirus_upload_performed':False,'completed':False,
            'design':'Four progressive component libraries; identical filename/entrypoints/resource; unused code deliberately retained',
            'limits':['Static component inclusion is not observed runtime behavior or a confirmed private-rule match.',
                      'Only the smoke entry point runs; retained production methods do not run.',
                      'No fixture is a player replacement. No automatic multivendor upload.']}
    def run(command,cwd,timeout=300):
        r=subprocess.run([str(x) for x in command],cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
        if r.returncode: raise RuntimeError('Owned component command failed: '+r.stdout+r.stderr)
        return r.stdout
    try:
        host=output/'cas-component-host.exe'
        run([compiler,'/nologo','/std:c++17','/EHsc','/O2','/W4','/WX','/MT',ROOT/'tools/research/component_probe_host.cpp','/Fe'+str(host),'/link','/INCREMENTAL:NO','/DYNAMICBASE','/NXCOMPAT','/Brepro'],output)
        includes=['/I'+str(x) for x in (native/'include',native/'third_party',native/'third_party/minhook/include',generated)]
        for label,components in CASES.items():
            directory=output/label; directory.mkdir(); objects=[]
            symbols=['/Z7','/pathmap:'+str(directory)+'=C:\\cas-component,'+str(output)+'=C:\\cas-generated,'+str(ROOT)+'=C:\\cas-source']
            if label!='crt':
                for name in ('buffer.c','hook.c','trampoline.c','hde/hde64.c'):
                    obj=directory/(Path(name).stem+'.obj')
                    run([compiler,'/nologo','/TC','/std:c11','/O2','/W4','/MT',*symbols,'/c',native/'third_party/minhook/src'/name,'/Fo'+str(obj)],directory)
                    objects.append(obj)
            resource=directory/'version.rc'
            resource.write_text('#include <windows.h>\n1 VERSIONINFO\nFILEVERSION 0,0,0,1\nPRODUCTVERSION 0,0,0,1\nFILEFLAGSMASK 0x3fL\nFILEFLAGS VS_FF_PRERELEASE\nFILEOS VOS_NT_WINDOWS32\nFILETYPE VFT_DLL\nBEGIN\n BLOCK "StringFileInfo"\n BEGIN\n  BLOCK "040904b0"\n  BEGIN\n   VALUE "CompanyName", "Lineum Dynamics\\0"\n   VALUE "FileDescription", "Owned component diagnostic - not a player mod\\0"\n   VALUE "ProductName", "Companion Auto Summon component diagnostic\\0"\n   VALUE "OriginalFilename", "CASComponentProbe.dll\\0"\n  END\n END\n BLOCK "VarFileInfo"\n BEGIN\n  VALUE "Translation", 0x0409, 1200\n END\nEND\n',encoding='utf-8',newline='\n')
            res=directory/'version.res'; run([rc,'/nologo','/fo',res,resource],directory)
            binary=directory/'CASComponentProbe.dll'
            run([compiler,'/nologo','/std:c++17','/permissive-','/Zc:__cplusplus','/O2','/W4','/EHsc','/MT','/utf-8',
                 '/DUNICODE','/D_UNICODE','/D_WIN32_WINNT=0x0A00','/D_CRT_SECURE_NO_WARNINGS',
                 '/DCAS_NATIVE_RUNTIME','/DCAS_PROBE_BUILD','/DCAS_RESPAWN_OBSERVER','/DCAS_TELEPORT_CANDIDATE_TRIAL',
                 *includes,*symbols,'/LD',ROOT/'tools/research/component_probe.cpp',
                 *(native/'src'/(name+'.cpp') for name in components),*objects,res,
                 'bcrypt.lib','advapi32.lib','shell32.lib','ole32.lib','uuid.lib','user32.lib','/Fe'+str(binary),
                 '/link','/DYNAMICBASE','/NXCOMPAT','/INCREMENTAL:NO','/Brepro','/DEBUG:FULL','/PDBALTPATH:%_PDB%','/OPT:NOREF','/OPT:NOICF'],directory)
            identity=digest(binary); smoke=json.loads(run([host,binary],output,30))
            if not smoke.get('passed') or digest(binary)!=identity: raise ValueError('Component smoke/input check failed')
            pe=run([inspect,'/headers','/imports','/exports',binary],directory)
            report['cases'].append({'label':label,'production_cpp_sources':components,
                'minhook_included':label!='crt','sha256':identity,'bytes':binary.stat().st_size,
                'resource_sha256':digest(resource),'probe_entry_source_sha256':digest(ROOT/'tools/research/component_probe.cpp'),
                'smoke':smoke,'imports':sorted(set(re.findall(r'^\s+([A-Za-z0-9_.-]+\.dll)\s*$',pe,re.M)))})
        if before!={x.relative_to(ROOT).as_posix():digest(x) for x in sources}: raise ValueError('Source changed during probe build')
        if len(report['cases'])!=4 or len({x['resource_sha256'] for x in report['cases']})!=1: raise ValueError('Fixed probe controls differ')
        report['completed']=True
    finally:
        (output/'component-probes.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'completed':True,'cases':report['cases']}))


if __name__=='__main__': main()
