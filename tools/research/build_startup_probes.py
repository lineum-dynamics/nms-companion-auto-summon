"""Build one fixed six-case startup/link comparison; every host is refused."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import build_component_probes as common
from build_inspection_probes import export_names

ROOT=common.ROOT
digest=common.digest
CASES={
    'cold': ('cold',False,False),
    'worker': ('worker',False,False),
    'full-stub': ('full',False,False),
    'full-real': ('full',True,False),
    'full-stub-ref': ('full',False,True),
    'full-real-ref': ('full',True,True),
}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True); args=p.parse_args()
    if (os.name!='nt' or os.environ.get('GITHUB_ACTIONS')!='true' or
            os.environ.get('GITHUB_REPOSITORY')!='lineum-dynamics/nms-companion-auto-summon'):
        raise ValueError('Owned Windows CI only')
    output=args.output.resolve()
    if not output.is_relative_to(ROOT/'build') or output.exists(): raise ValueError('Use a new owned output directory')
    compiler=Path(shutil.which('cl.exe') or ''); rc=Path(shutil.which('rc.exe') or ''); inspect=Path(shutil.which('dumpbin.exe') or '')
    if any(not x.is_file() for x in (compiler,rc,inspect)): raise ValueError('Use the verified installed tools')
    common.dependencies(source_root=ROOT); common.locales(locales_dir=ROOT/'locales',source_root=ROOT)
    native=ROOT/'native'; profile=common.load_native_profile(ROOT/'native_compatibility.json')
    mapping=common.load_native_mapping(profile)
    sources=sorted(x for x in native.rglob('*') if x.is_file())+sorted((ROOT/'locales').glob('*.json'))
    sources += [ROOT/x for x in ('native_compatibility.json','native_mappings.json',
        '.github/workflows/native-startup-probes.yml','tools/research/build_startup_probes.py',
        'tools/research/build_inspection_probes.py','tools/research/build_component_probes.py',
        'tools/research/startup_probe_entry.cpp','tools/research/startup_inspection_refusal.cpp',
        'tools/research/startup_refusal_driver.cpp','tools/research/inspection_probe_stub.cpp',
        'tools/generate_native_catalog.py','tools/native_compatibility.py','tools/native_mapping.py')]
    before={x.relative_to(ROOT).as_posix():digest(x) for x in sources}
    output.mkdir(); generated=output/'generated'; generated.mkdir()
    common.generate(generated/'catalog.hpp'); common.write_mapping_header(mapping,generated/'native_mapping_profile.hpp')
    (generated/'compatibility_profile.hpp').write_text('#pragma once\nnamespace cas::profile {\n'+
        'inline constexpr char exe_sha256[] = '+json.dumps(profile['exe_sha256'])+';\n'+
        'inline constexpr char steam_build[] = '+json.dumps(profile['steam_build'])+';\n}\n',encoding='utf-8',newline='\n')
    source=(native/'src/bootstrap.cpp').read_text(encoding='utf-8')
    marker='extern "C" __declspec(dllexport) std::uint32_t CasRuntimeStatus() {'
    if source.count(marker)!=1: raise ValueError('Review the actual production export tail')
    tail=source[source.index(marker):]
    if len(tail)>4096 or not tail.rstrip().endswith('BOOL WINAPI DllMain(HINSTANCE,DWORD,LPVOID) { return TRUE; }'):
        raise ValueError('Unexpected production export tail')
    (generated/'startup_exports.inc').write_text(tail,encoding='utf-8',newline='\n')
    report={'schema':1,'kind':'fixed-inactive-startup-link-probes','controller_revision':os.environ.get('GITHUB_SHA'),
            'compiler_sha256':digest(compiler),'sources':before,
            'generated':{x.name:digest(x) for x in generated.iterdir()},'cases':[],
            'game_access':False,'player_artifact_modified':False,'antivirus_upload_performed':False,'completed':False,
            'design':'Cold ABI, exact exported startup tail with minimal worker, full bootstrap; forced host refusal; two explicit link policies',
            'limits':['All diagnostic host inspectors refuse support, including a real-inspection adapter that converts supported to unsupported.',
                      'A source-inclusion boundary is not a private matching rule or an engineering defect.',
                      'Normal owned-process exit only. No player binary, game activation or automatic AV submission.']}
    def run(command,cwd,timeout=300,env=None):
        r=subprocess.run([str(x) for x in command],cwd=cwd,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
        if r.returncode: raise RuntimeError('Owned startup command failed: '+r.stdout+r.stderr)
        return r.stdout
    try:
        includes=['/I'+str(x) for x in (native/'include',native/'third_party',native/'third_party/minhook/include',generated)]
        cpp=[compiler,'/nologo','/std:c++17','/permissive-','/Zc:__cplusplus','/O2','/W4','/EHsc','/MT','/utf-8',
             '/DUNICODE','/D_UNICODE','/D_WIN32_WINNT=0x0A00','/D_CRT_SECURE_NO_WARNINGS',*includes]
        link=['/link','/DYNAMICBASE','/NXCOMPAT','/INCREMENTAL:NO','/Brepro']
        env={k:v for k,v in os.environ.items() if k.upper() in
             {'SYSTEMROOT','WINDIR','SYSTEMDRIVE','PATH','TEMP','TMP','GITHUB_ACTIONS','GITHUB_REPOSITORY'}}
        host=output/'native_host.exe'
        run([*cpp,native/'tests/native_host.cpp','/Fe'+str(host),*link],output)
        report['owned_host_sha256']=digest(host)
        driver=output/'cas-startup-refusal-check.exe'
        run([*cpp,ROOT/'tools/research/startup_refusal_driver.cpp',ROOT/'tools/research/startup_inspection_refusal.cpp',
             '/Fe'+str(driver),*link],output)
        refusal=json.loads(run([driver],output,30,env))
        if not refusal.get('passed') or not refusal.get('synthetic_supported_result_refused'):
            raise ValueError('Forced-refusal adapter control failed')
        report['supported_refusal_control']=refusal
        for label,(mode,real,optimized) in CASES.items():
            directory=output/label; directory.mkdir(); objects=[]
            symbols=['/Z7','/pathmap:'+str(directory)+'=C:\\cas-startup,'+str(output)+'=C:\\cas-generated,'+str(ROOT)+'=C:\\cas-source']
            for name in ('buffer.c','hook.c','trampoline.c','hde/hde64.c'):
                obj=directory/(Path(name).stem+'.obj')
                run([compiler,'/nologo','/TC','/std:c11','/O2','/W4','/MT',*symbols,'/c',native/'third_party/minhook/src'/name,'/Fo'+str(obj)],directory)
                objects.append(obj)
            defines=['/DCAS_NATIVE_RUNTIME','/DCAS_RESPAWN_OBSERVER','/DCAS_TELEPORT_CANDIDATE_TRIAL']
            inspection=ROOT/'tools/research/inspection_probe_stub.cpp'
            if real:
                production=directory/'production-inspection.obj'
                # The original C function is internal, not an extra exported API.
                run([*cpp,*symbols,*defines,'/DCasInspectHost=CasInspectHostProduction','/c',native/'src/probe.cpp','/Fo'+str(production)],directory)
                objects.append(production)
                inspection=ROOT/'tools/research/startup_inspection_refusal.cpp'
            startup=native/'src/bootstrap.cpp' if mode=='full' else ROOT/'tools/research/startup_probe_entry.cpp'
            if mode=='worker': defines.append('/DCAS_STARTUP_WORKER')
            resource=directory/'version.rc'
            resource.write_text('#include <windows.h>\n1 VERSIONINFO\nFILEVERSION 0,0,0,3\nPRODUCTVERSION 0,0,0,3\nFILEFLAGSMASK 0x3fL\nFILEFLAGS VS_FF_PRERELEASE\nFILEOS VOS_NT_WINDOWS32\nFILETYPE VFT_DLL\nBEGIN\n BLOCK "StringFileInfo"\n BEGIN\n  BLOCK "040904b0"\n  BEGIN\n   VALUE "CompanyName", "Lineum Dynamics\\0"\n   VALUE "FileDescription", "Inactive startup diagnostic - not a player mod\\0"\n   VALUE "ProductName", "Companion Auto Summon startup diagnostic\\0"\n   VALUE "OriginalFilename", "CASStartupProbe.asi\\0"\n  END\n END\n BLOCK "VarFileInfo"\n BEGIN\n  VALUE "Translation", 0x0409, 1200\n END\nEND\n',encoding='utf-8',newline='\n')
            res=directory/'version.res'; run([rc,'/nologo','/fo',res,resource],directory)
            binary=directory/'CASStartupProbe.asi'
            optimization=['/OPT:REF','/OPT:ICF'] if optimized else ['/OPT:NOREF','/OPT:NOICF']
            run([*cpp,*symbols,*defines,'/DCAS_PROBE_BUILD','/LD',startup,inspection,
                 *(native/'src'/(name+'.cpp') for name in common.CASES['core']),*objects,res,
                 'bcrypt.lib','advapi32.lib','shell32.lib','ole32.lib','uuid.lib','user32.lib','/Fe'+str(binary),
                 *link,'/DEBUG:FULL','/PDBALTPATH:%_PDB%',*optimization],directory,900)
            identity=digest(binary); runs=[]
            for _ in range(3):
                observed=json.loads(run([host,binary],directory,30,env))
                if (observed.get('native_status')!=2 or observed.get('hooks_active') is not False or
                    observed.get('concurrent_calls')!=8 or observed.get('host_sha256')!=(digest(host) if real else '')):
                    raise ValueError('Owned initializer/refusal/hash control failed')
                runs.append(observed)
            if digest(binary)!=identity: raise ValueError('Input changed during owned runs')
            pe=run([inspect,'/headers','/imports','/exports',binary],directory)
            exports=export_names(pe)
            if exports!=['CasInspectHost','CasRuntimeStatus','InitializeASI']:
                raise ValueError('Matched production export control differs: '+repr(exports)+'; '+pe[-6000:])
            report['cases'].append({'label':label,'startup':mode,'real_inspection_with_forced_refusal':real,
                'core_and_minhook_linked':True,'link_optimization':optimization,
                'unused_core_retention_requested':not optimized,'sha256':identity,'bytes':binary.stat().st_size,
                'resource_sha256':digest(resource),'exports':exports,'owned_initializer_runs':runs,
                'imports':sorted(set(re.findall(r'^\s+([A-Za-z0-9_.-]+\.dll)\s*$',pe,re.M)))})
        if before!={x.relative_to(ROOT).as_posix():digest(x) for x in sources}: raise ValueError('Source changed during startup build')
        if len(report['cases'])!=6 or len({x['resource_sha256'] for x in report['cases']})!=1:
            raise ValueError('Fixed case/resource controls differ')
        report['completed']=True
    finally:
        (output/'startup-probes.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'completed':True,'cases':report['cases']}))


if __name__=='__main__': main()
