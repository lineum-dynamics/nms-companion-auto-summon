"""Cross-compiler source audit on an isolated Windows CI runner, not a release build.

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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("GITHUB_ACTIONS") != "true":
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
    callers = re.findall(r"__builtin_return_address\s*\(\s*(\d+)\s*\)",bootstrap)
    if callers != ["0","0"] or bootstrap.count("__builtin_return_address") != 2:
        raise ValueError("Review the diagnostic return-address adapter before use")
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
    adapter = generated/"msvc_audit_compat.hpp"
    adapter.write_text("#pragma once\n#include <intrin.h>\n#pragma intrinsic(_ReturnAddress)\n"
                       "#define __builtin_return_address(level) _ReturnAddress()\n",encoding="utf-8")
    version = BASE_VERSION.split("-")[0]+"-msvc-audit"
    numeric_version = ",".join(BASE_VERSION.split("-")[0].split(".")+["0"])
    resource = output/"version.rc"
    resource.write_text('#include <windows.h>\n1 VERSIONINFO\nFILEVERSION NUMERIC_VERSION_VALUE\nPRODUCTVERSION NUMERIC_VERSION_VALUE\nFILEFLAGSMASK 0x3fL\nFILEFLAGS VS_FF_PRERELEASE\nFILEOS VOS_NT_WINDOWS32\nFILETYPE VFT_DLL\nBEGIN\n BLOCK "StringFileInfo"\n BEGIN\n  BLOCK "040904b0"\n  BEGIN\n   VALUE "CompanyName", "Lineum Dynamics\\0"\n   VALUE "FileDescription", "Companion Auto Summon - isolated compiler audit\\0"\n   VALUE "FileVersion", "VERSION_VALUE\\0"\n   VALUE "ProductName", "Companion Auto Summon compiler audit\\0"\n   VALUE "ProductVersion", "VERSION_VALUE\\0"\n   VALUE "OriginalFilename", "CompanionAutoSummon.asi\\0"\n  END\n END\n BLOCK "VarFileInfo"\n BEGIN\n  VALUE "Translation", 0x0409, 1200\n END\nEND\n'.replace("NUMERIC_VERSION_VALUE",numeric_version).replace("VERSION_VALUE",version),encoding="utf-8")
    commands = []

    def run(command, timeout=300):
        args = [str(x) for x in command]
        result = subprocess.run(args,cwd=output,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout)
        commands.append({"arguments":args,"exit_code":result.returncode,"stdout":result.stdout,"stderr":result.stderr})
        if result.returncode:
            raise RuntimeError("Compiler audit command failed: "+result.stdout+result.stderr)
        return result.stdout

    log = {"kind":"cross-compiler-audit","version":version,"base_player_version":BASE_VERSION,
           "game_access":False,"deployed":False,"binary_uploaded":False,"sources":before,"commands":commands,
           "compatibility":profile,"native_mapping":mapping,"completed":False,
           "adapter":{"call_sites":2,"level":0,"intrinsic":"_ReturnAddress","diagnostic_only":True}}
    try:
        includes = ["/I"+str(p) for p in (native/"include",native/"third_party",native/"third_party/minhook/include",generated)]
        cpp = [tools["cl.exe"],"/nologo","/std:c++17","/permissive-","/Zc:__cplusplus","/O2","/W4","/EHsc","/MT","/utf-8",
               "/DUNICODE","/D_UNICODE","/D_WIN32_WINNT=0x0A00","/D_CRT_SECURE_NO_WARNINGS",*includes,"/FI"+str(adapter)]
        objects = []
        for name in ("buffer.c","hook.c","trampoline.c","hde/hde64.c"):
            obj = output/(Path(name).stem+".obj")
            run([tools["cl.exe"],"/nologo","/TC","/std:c11","/O2","/W4","/MT","/c",native/"third_party/minhook/src"/name,"/Fo"+str(obj)])
            objects.append(obj)
        res = output/"version.res"
        run([tools["rc.exe"],"/nologo","/fo",res,resource])
        runtime = [native/"src"/(n+".cpp") for n in
                   ("bootstrap","probe","policy","selection","storage","runtime","backup","menu","binding_guard")]
        link = ["/link","/DYNAMICBASE","/NXCOMPAT","/INCREMENTAL:NO","/Brepro"]
        binary = output/"CompanionAutoSummon.asi"
        run([*cpp,"/analyze","/LD","/DCAS_NATIVE_RUNTIME","/DCAS_PROBE_BUILD","/DCAS_RESPAWN_OBSERVER",
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
        pe = run([tools["dumpbin.exe"],"/headers","/imports","/exports",binary])
        (output/"native-pe.txt").write_text(pe,encoding="utf-8")
        imports = sorted(set(re.findall(r"^\s+([A-Za-z0-9_.-]+\.dll)\s*$",pe,re.M)))
        if before != {p.relative_to(ROOT).as_posix():digest(p) for p in sources}:
            raise RuntimeError("Source changed during the compiler audit")
        tool_identity = {name:{"sha256":digest(path),"path":str(path)} for name,path in tools.items()}
        receipt = {"version":version,"kind":"cross-compiler-audit","gameplay_implemented":True,
                   "live_verified":False,"deployed":False,"compiler":"Microsoft MSVC - isolated source audit",
                   "compiler_sha256":digest(tools["cl.exe"]),"tool_identities":tool_identity,"sources":before,
                   "imports":imports,"compatibility":profile,"native_mapping":mapping,
                   "profile_validation":legacy,"locale_validation":locale,"dependency_validation":dependency,
                   "teleport_candidate_trial":True,"products":{p.name:{"sha256":digest(p),"bytes":p.stat().st_size} for p in products},
                   "generated":{p.name:digest(p) for p in generated.glob("*.hpp")}}
        (output/"build-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
        log.update(completed=True,products=receipt["products"],tool_identities=tool_identity,
                   build_receipt_sha256=digest(output/"build-receipt.json"),imports=imports)
    finally:
        (output/"compiler-audit.json").write_text(json.dumps(log,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"completed":log["completed"],"version":version,"products":log.get("products"),"imports":log.get("imports")}))


if __name__ == "__main__":
    main()
