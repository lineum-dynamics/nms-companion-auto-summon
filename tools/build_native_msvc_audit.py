"""Microsoft compiler audit or explicitly selected pre-release build in Windows CI.

No installer, game process, save discovery, deployment or binary upload is used.
The player packager rejects this distinct audit version. Frozen release bytes
are not rewritten or stripped to alter antivirus results.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from build_native_probe import ROOT, digest
from build_native_runtime import VERSION as BASE_VERSION
from generate_native_catalog import generate
from native_compatibility import load_native_profile
from native_mapping import load_native_mapping, write_mapping_header
from validate_compatibility import validate
from validate_native_dependencies import validate as validate_dependencies
from validate_locales import validate as validate_locales

CANDIDATE_VERSION = "0.10.6-native-test"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--release-candidate", action="store_true",
                        help="Build the distinct CRT-thread candidate with separate PDB symbols; packaging stays blocked")
    parser.add_argument("--startup-failure-fixture", action="store_true",
                        help="Also build an owned factory-failure DLL and check single-owner refusal")
    parser.add_argument("--omit-analysis-for-comparison", action="store_true",
                        help="Diagnostic compiler-flag comparison only; preserve source/version, omit DLL /analyze")
    parser.add_argument("--fixed-version-resource-comparison", action="store_true",
                        help="Diagnostic only: keep fixed VERSIONINFO fields and omit optional text resource blocks")
    args = parser.parse_args()
    if args.startup_failure_fixture and not args.release_candidate:
        parser.error("The startup failure fixture requires the explicit candidate mode")
    if args.omit_analysis_for_comparison and not args.release_candidate:
        parser.error("The compiler comparison requires explicit candidate mode; the default source audit stays enabled")
    if args.fixed_version_resource_comparison and not args.release_candidate:
        parser.error("The resource comparison requires explicit candidate mode")
    if args.fixed_version_resource_comparison and args.omit_analysis_for_comparison:
        parser.error("Compare one factor at a time; resource comparison retains /analyze")
    if (os.name != "nt" or os.environ.get("GITHUB_ACTIONS") != "true"
            or os.environ.get("GITHUB_REPOSITORY") != "lineum-dynamics/nms-companion-auto-summon"):
        raise ValueError("This audit runs only on an isolated GitHub Actions runner")
    output = args.output.resolve()
    if not output.is_relative_to(ROOT/"build") or output.exists():
        raise ValueError("Use a new repository build directory")
    tools = {name: Path(shutil.which(name) or "") for name in ("cl.exe", "rc.exe", "dumpbin.exe")}
    if any(not path.is_file() for path in tools.values()):
        raise ValueError("Use the existing official x64 Visual Studio developer environment")
    locale = validate_locales(locales_dir=ROOT/"locales",source_root=ROOT)
    legacy = validate(source_root=ROOT,developer=True,generated=True)
    dependency = validate_dependencies(source_root=ROOT)
    profile = load_native_profile(ROOT/"native_compatibility.json")
    mapping = load_native_mapping(profile)
    native = ROOT/"native"
    bootstrap = (native/"src/bootstrap.cpp").read_text(encoding="utf-8")
    if bootstrap.count("CAS_CALLER_ADDRESS()") != 2 or "__builtin_return_address" in bootstrap:
        raise ValueError("Review native caller attribution at both callback sites")
    sources = sorted(p for p in native.rglob("*") if p.is_file())
    sources += sorted((ROOT/"locales").glob("*.json"))
    sources += [ROOT/p for p in ("compatibility.json","native_compatibility.json","native_mappings.json",
                "tools/native_compatibility.py","tools/native_mapping.py","tools/generate_native_catalog.py",
                "tools/validate_native_dependencies.py","tools/build_native_msvc_audit.py")]
    before = {p.relative_to(ROOT).as_posix():digest(p) for p in sources}
    output.mkdir(parents=True)
    generated = output/"generated"; generated.mkdir()
    generate(generated/"catalog.hpp")
    (generated/"compatibility_profile.hpp").write_text(
        "#pragma once\nnamespace cas::profile {\n"
        f"inline constexpr char exe_sha256[] = {json.dumps(profile['exe_sha256'])};\n"
        f"inline constexpr char steam_build[] = {json.dumps(profile['steam_build'])};\n}}\n",encoding="utf-8")
    write_mapping_header(mapping,generated/"native_mapping_profile.hpp")
    version = CANDIDATE_VERSION if args.release_candidate else BASE_VERSION.split("-")[0]+"-msvc-audit"
    numeric_version = ",".join(version.split("-")[0].split(".")+["0"])
    resource = output/"version.rc"
    resource.write_text('#include <windows.h>\n1 VERSIONINFO\nFILEVERSION NUMERIC_VERSION_VALUE\nPRODUCTVERSION NUMERIC_VERSION_VALUE\nFILEFLAGSMASK 0x3fL\nFILEFLAGS VS_FF_PRERELEASE\nFILEOS VOS_NT_WINDOWS32\nFILETYPE VFT_DLL\nBEGIN\n BLOCK "StringFileInfo"\n BEGIN\n  BLOCK "040904b0"\n  BEGIN\n   VALUE "CompanyName", "Lineum Dynamics\\0"\n   VALUE "FileDescription", "Companion Auto Summon - isolated compiler audit\\0"\n   VALUE "FileVersion", "VERSION_VALUE\\0"\n   VALUE "ProductName", "Companion Auto Summon compiler audit\\0"\n   VALUE "ProductVersion", "VERSION_VALUE\\0"\n   VALUE "OriginalFilename", "CompanionAutoSummon.asi\\0"\n  END\n END\n BLOCK "VarFileInfo"\n BEGIN\n  VALUE "Translation", 0x0409, 1200\n END\nEND\n'.replace("NUMERIC_VERSION_VALUE",numeric_version).replace("VERSION_VALUE",version),encoding="utf-8")
    if args.release_candidate:
        resource.write_text(resource.read_text(encoding="utf-8").replace(
            "Companion Auto Summon - isolated compiler audit", "Companion Auto Summon for No Man's Sky - native test").replace(
            "Companion Auto Summon compiler audit", "Companion Auto Summon for No Man's Sky - by Lineum Dynamics"),encoding="utf-8")
    if args.fixed_version_resource_comparison:
        resource.write_text(
            '#include <windows.h>\n1 VERSIONINFO\n'
            f'FILEVERSION {numeric_version}\nPRODUCTVERSION {numeric_version}\n'
            'FILEFLAGSMASK 0x3fL\nFILEFLAGS VS_FF_PRERELEASE\n'
            'FILEOS VOS_NT_WINDOWS32\nFILETYPE VFT_DLL\nBEGIN\nEND\n',encoding="utf-8")
    commands = []

    def run(command, timeout=300):
        args = [str(x) for x in command]
        result = subprocess.run(args,cwd=output,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout)
        commands.append({"arguments":args,"exit_code":result.returncode,"stdout":result.stdout,"stderr":result.stderr})
        if result.returncode:
            raise RuntimeError("Compiler audit command failed: "+result.stdout+result.stderr)
        return result.stdout

    kind = "msvc-release-candidate" if args.release_candidate else "cross-compiler-audit"
    if args.omit_analysis_for_comparison:
        kind = "msvc-compiler-flag-comparison"
    if args.fixed_version_resource_comparison:
        kind = "msvc-fixed-resource-comparison"
    log = {"kind":kind,"version":version,"base_player_version":BASE_VERSION,
           "game_access":False,"deployed":False,"binary_uploaded":False,"sources":before,"commands":commands,
           "compatibility":profile,"native_mapping":mapping,"completed":False,
           "caller_attribution":{"call_sites":2,"level":0,"intrinsic":"_ReturnAddress","call_site_macro":True},
           "packaging_approved":False,"av_clearance":False,
           "dll_static_analysis_included":not args.omit_analysis_for_comparison,
           "fixed_version_resource_comparison":args.fixed_version_resource_comparison,
           "resource_source_sha256":digest(resource)}
    try:
        includes = ["/I"+str(p) for p in (native/"include",native/"third_party",native/"third_party/minhook/include",generated)]
        cpp = [tools["cl.exe"],"/nologo","/std:c++17","/permissive-","/Zc:__cplusplus","/O2","/W4","/EHsc","/MT","/utf-8",
               "/DUNICODE","/D_UNICODE","/D_WIN32_WINNT=0x0A00","/D_CRT_SECURE_NO_WARNINGS",*includes]
        symbol_options = (["/Z7", "/pathmap:"+str(output)+"=C:\\cas-build,"+str(ROOT)+"=C:\\cas-source"]
                          if args.release_candidate else [])
        cpp += symbol_options
        objects = []
        for name in ("buffer.c","hook.c","trampoline.c","hde/hde64.c"):
            obj = output/(Path(name).stem+".obj")
            run([tools["cl.exe"],"/nologo","/TC","/std:c11","/O2","/W4","/MT",*symbol_options,"/c",native/"third_party/minhook/src"/name,"/Fo"+str(obj)])
            objects.append(obj)
        res = output/"version.res"
        run([tools["rc.exe"],"/nologo","/fo",res,resource])
        runtime = [native/"src"/(n+".cpp") for n in
                   ("bootstrap","probe","policy","selection","storage","runtime","backup","menu","binding_guard")]
        link = ["/link","/DYNAMICBASE","/NXCOMPAT","/INCREMENTAL:NO","/Brepro"]
        if args.release_candidate:
            link += ["/DEBUG:FULL", "/PDBALTPATH:%_PDB%", "/OPT:REF", "/OPT:ICF"]
        binary = output/"CompanionAutoSummon.asi"
        analysis_options = [] if args.omit_analysis_for_comparison else ["/analyze"]
        run([*cpp,*analysis_options,"/LD","/DCAS_NATIVE_RUNTIME","/DCAS_PROBE_BUILD","/DCAS_RESPAWN_OBSERVER",
             "/DCAS_TELEPORT_CANDIDATE_TRIAL",*runtime,*objects,res,"bcrypt.lib","advapi32.lib","shell32.lib",
             "ole32.lib","uuid.lib","user32.lib","/Fe"+str(binary),*link],timeout=900)
        hosts = {
            "native_host":("native/tests/native_host.cpp",),
            "runtime_fixture":("native/src/runtime.cpp","native/src/policy.cpp","native/src/selection.cpp","native/src/storage.cpp","native/tests/runtime_fixture.cpp"),
            "selection_reference_driver":("native/src/selection.cpp","native/tests/selection_reference_driver.cpp"),
            "storage_driver":("native/src/storage.cpp","native/tests/storage_driver.cpp"),
            "policy_reference_driver":("native/src/policy.cpp","native/tests/policy_reference_driver.cpp"),
            "backup_driver":("native/src/backup.cpp","native/tests/backup_driver.cpp"),
            "load_context_host":("native/tests/load_context_host.cpp",),
        }
        products = [binary]
        for name, paths in hosts.items():
            executable = output/(name+".exe")
            defines = ["/DCAS_TELEPORT_CANDIDATE_TRIAL"] if name == "runtime_fixture" else []
            run([*cpp,*defines,*(ROOT/p for p in paths),"bcrypt.lib","advapi32.lib","/Fe"+str(executable),*link])
            products.append(executable)
        hook_host = output/"hook_host.exe"
        run([*cpp,native/"tests/hook_host.cpp",*objects,"/Fe"+str(hook_host),*link])
        products.append(hook_host)
        query_host = output/"minhook_query_host.exe"
        run([tools["cl.exe"],"/nologo","/TC","/std:c11","/O2","/W4","/MT",native/"tests/minhook_query_host.c",
             "/Fe"+str(query_host),*link])
        products.append(query_host)
        startup_failure = None
        if args.startup_failure_fixture:
            failure = output/"ThreadFactoryFailure.dll"
            shim = native/"tests/thread_factory_failure.hpp"
            run([*cpp,"/FI"+str(shim),"/LD","/DCAS_NATIVE_RUNTIME","/DCAS_PROBE_BUILD","/DCAS_RESPAWN_OBSERVER",
                 "/DCAS_TELEPORT_CANDIDATE_TRIAL",*runtime,native/"tests/thread_factory_failure.cpp",*objects,res,
                 "bcrypt.lib","advapi32.lib","shell32.lib","ole32.lib","uuid.lib","user32.lib",
                 "/Fe"+str(failure),*link],timeout=900)
            startup_failure = json.loads(run([output/"native_host.exe",failure,"--expect-thread-failure"],timeout=30))
            if (startup_failure.get("native_status") != 3 or startup_failure.get("hooks_active") is not False
                    or startup_failure.get("thread_factory_calls") != 1):
                raise RuntimeError("Thread factory failure did not remain stopped/inert")
            products.append(failure)
        pe = run([tools["dumpbin.exe"],"/headers","/imports","/exports",binary])
        (output/"native-pe.txt").write_text(pe,encoding="utf-8")
        imports = sorted(set(re.findall(r"^\s+([A-Za-z0-9_.-]+\.dll)\s*$",pe,re.M)))
        if before != {p.relative_to(ROOT).as_posix():digest(p) for p in sources}:
            raise RuntimeError("Source changed during the compiler audit")
        tool_identity = {name:{"sha256":digest(path),"path":str(path)} for name,path in tools.items()}
        receipt = {"version":version,"kind":kind,"gameplay_implemented":True,
                   "live_verified":False,"deployed":False,"compiler":"Microsoft MSVC - isolated source audit",
                   "compiler_sha256":digest(tools["cl.exe"]),"tool_identities":tool_identity,"sources":before,
                   "imports":imports,"compatibility":profile,"native_mapping":mapping,
                   "profile_validation":legacy,"locale_validation":locale,"dependency_validation":dependency,
                   "teleport_candidate_trial":True,"products":{p.name:{"sha256":digest(p),"bytes":p.stat().st_size} for p in products},
                   "generated":{p.name:digest(p) for p in generated.glob("*.hpp")}}
        receipt.update(packaging_approved=False,av_clearance=False,
                       caller_attribution=log["caller_attribution"],
                       debug_symbols_separate=args.release_candidate,
                       startup_thread_factory="_beginthreadex",startup_thread_failure_control=startup_failure,
                       dll_static_analysis_included=not args.omit_analysis_for_comparison,
                       fixed_version_resource_comparison=args.fixed_version_resource_comparison,
                       resource_source_sha256=digest(resource))
        if args.release_candidate:
            pdb = output/"CompanionAutoSummon.pdb"
            if not pdb.is_file():
                raise RuntimeError("Separate candidate PDB is missing")
            receipt["symbols"] = {pdb.name:{"sha256":digest(pdb),"bytes":pdb.stat().st_size}}
        (output/"build-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
        log.update(completed=True,products=receipt["products"],tool_identities=tool_identity,
                   build_receipt_sha256=digest(output/"build-receipt.json"),imports=imports)
    finally:
        (output/"compiler-audit.json").write_text(json.dumps(log,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"completed":log["completed"],"version":version,"products":log.get("products"),"imports":log.get("imports")}))


if __name__ == "__main__":
    main()
