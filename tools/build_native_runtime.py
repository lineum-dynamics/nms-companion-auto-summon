"""Build the next native player test and owned hosts. Never deploy or run NMS."""
import argparse
import json
import re
from pathlib import Path
from build_native_probe import ROOT, digest, run
from generate_native_catalog import generate
from native_compatibility import load_native_profile
from validate_compatibility import validate

VERSION = "0.10.2-native-test"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toolchain", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--respawn-observer", action="store_true",
                        help="Build a test-only passive observer for three exact-build respawn-path candidate returns")
    parser.add_argument("--teleport-candidate-trial", action="store_true",
                        help="Include the experimental teleport trigger in the next player test build")
    args = parser.parse_args()
    if args.respawn_observer and args.teleport_candidate_trial:
        parser.error("--respawn-observer and --teleport-candidate-trial are separate build modes")
    version = VERSION + ("-respawn-observer" if args.respawn_observer else "")
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "build") or output.exists():
        raise ValueError("Use a new directory beneath build")
    profile_report = validate(source_root=ROOT, developer=True, generated=True)
    profile = load_native_profile(ROOT / "native_compatibility.json")
    native = ROOT / "native"
    sources = sorted(p for p in native.rglob("*") if p.is_file())
    sources += sorted((ROOT / "locales").glob("*.json"))
    sources += [ROOT / "compatibility.json", ROOT / "native_compatibility.json",
                ROOT / "tools/native_compatibility.py", Path(__file__), ROOT / "tools/generate_native_catalog.py"]
    before = {p.relative_to(ROOT).as_posix(): digest(p) for p in sources}
    output.mkdir(parents=True)
    generated = output / "generated"
    generated.mkdir()
    generate(generated / "catalog.hpp")
    (generated / "compatibility_profile.hpp").write_text(
        "#pragma once\nnamespace cas::profile {\n"
        f"inline constexpr char exe_sha256[] = {json.dumps(profile['exe_sha256'])};\n"
        f"inline constexpr char steam_build[] = {json.dumps(profile['steam_build'])};\n"
        "}\n", encoding="utf-8")
    compiler = args.toolchain.resolve() / "bin/x86_64-w64-mingw32-clang++.exe"
    c_compiler = args.toolchain.resolve() / "bin/x86_64-w64-mingw32-clang.exe"
    inspect = args.toolchain.resolve() / "bin/llvm-readobj.exe"
    windres = args.toolchain.resolve() / "bin/x86_64-w64-mingw32-windres.exe"
    common = [compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror", "-DUNICODE", "-D_UNICODE",
              "-D_WIN32_WINNT=0x0A00", "-static", "-Wl,--no-insert-timestamp,--dynamicbase,--nxcompat",
              "-I", native / "include", "-I", native / "third_party", "-I", native / "third_party/minhook/include",
              "-I", generated]
    commands, objects = [], []
    for source in ("buffer.c", "hook.c", "trampoline.c", "hde/hde64.c"):
        obj = output / (Path(source).stem + ".o")
        command = [c_compiler,"-O2","-Wall","-Wextra","-c",native / "third_party/minhook/src" / source,"-o",obj]
        commands.append(command)
        run(command,output)
        objects.append(obj)
    resource = output / "version.rc"
    resource.write_text('''#include <windows.h>
1 VERSIONINFO
FILEVERSION 0,10,2,0
PRODUCTVERSION 0,10,2,0
FILEFLAGSMASK 0x3fL
FILEFLAGS VS_FF_PRERELEASE
FILEOS VOS_NT_WINDOWS32
FILETYPE VFT_DLL
BEGIN
 BLOCK "StringFileInfo"
 BEGIN
  BLOCK "040904b0"
  BEGIN
   VALUE "CompanyName", "Lineum Dynamics\\0"
   VALUE "FileDescription", "Companion Auto Summon for No Man's Sky - native test\\0"
   VALUE "FileVersion", "{version}\\0"
   VALUE "ProductName", "Companion Auto Summon for No Man's Sky - by Lineum Dynamics\\0"
   VALUE "ProductVersion", "{version}\\0"
   VALUE "OriginalFilename", "CompanionAutoSummon.asi\\0"
  END
 END
 BLOCK "VarFileInfo"
 BEGIN
  VALUE "Translation", 0x0409, 1200
 END
END
'''.format(version=version),encoding="utf-8")
    command = [windres,resource,"-O","coff","-o",output / "version.o"]
    commands.append(command)
    run(command,output)
    objects.append(output / "version.o")
    runtime_sources = [native / "src" / (name + ".cpp") for name in
                       ("bootstrap","probe","policy","selection","storage","runtime","backup","menu","binding_guard")]
    observer_define = (["-DCAS_RESPAWN_OBSERVER", "-DCAS_TELEPORT_CANDIDATE_TRIAL"]
                       if args.teleport_candidate_trial else
                       ["-DCAS_RESPAWN_OBSERVER"] if args.respawn_observer else [])
    command = [*common,"-shared","-DCAS_NATIVE_RUNTIME","-DCAS_PROBE_BUILD",*observer_define,*runtime_sources,*objects,
               "-lbcrypt","-ladvapi32","-lshell32","-lole32","-luuid","-luser32","-o",output / "CompanionAutoSummon.asi"]
    commands.append(command)
    run(command,output)
    hosts = {
        "native_host": ("native/tests/native_host.cpp",),
        "runtime_fixture": ("native/src/runtime.cpp","native/src/policy.cpp","native/src/selection.cpp","native/src/storage.cpp","native/tests/runtime_fixture.cpp"),
        "selection_reference_driver": ("native/src/selection.cpp","native/tests/selection_reference_driver.cpp"),
        "storage_driver": ("native/src/storage.cpp","native/tests/storage_driver.cpp"),
        "policy_reference_driver": ("native/src/policy.cpp","native/tests/policy_reference_driver.cpp"),
        "backup_driver": ("native/src/backup.cpp","native/tests/backup_driver.cpp"),
    }
    for name, paths in hosts.items():
        unicode = ["-municode"] if name == "native_host" else []
        trial_define = ["-DCAS_TELEPORT_CANDIDATE_TRIAL"] if name == "runtime_fixture" and args.teleport_candidate_trial else []
        command = [*common,*unicode,*trial_define,*(ROOT / p for p in paths),"-lbcrypt","-ladvapi32","-o",output / (name+".exe")]
        commands.append(command)
        run(command,output)
    hook_host = output / "hook_host.exe"
    command = [*common,native/"tests/hook_host.cpp",*objects[:-1],"-o",hook_host]
    commands.append(command)
    run(command,output)
    binary = output / "CompanionAutoSummon.asi"
    pe = run([inspect,"--file-header","--coff-imports","--coff-exports",binary],output)
    (output / "native-pe.txt").write_text(pe,encoding="utf-8")
    for export in ("InitializeASI","CasInspectHost","CasRuntimeStatus"):
        if f"Name: {export}\n" not in pe:
            raise RuntimeError("Missing native export: " + export)
    imports = re.findall(r"Import \{\s+Name: ([^\r\n]+)",pe)
    if any(name.lower().startswith(("python","libc++","libunwind","libgcc","mscoree")) for name in imports):
        raise RuntimeError("Unexpected external language runtime")
    if before != {p.relative_to(ROOT).as_posix(): digest(p) for p in sources}:
        raise RuntimeError("Source changed while compiling; build retained but invalid")
    products = [binary,hook_host,*(output / (name+".exe") for name in hosts)]
    receipt = {"version":version,"gameplay_implemented":True,"diagnostic_observer":args.respawn_observer or args.teleport_candidate_trial,
               "diagnostic_candidate_rva":0x14F7F60 if args.respawn_observer or args.teleport_candidate_trial else None,
               "diagnostic_return_site_rvas":[0x3302C4,0x33066F,0x330946] if args.respawn_observer or args.teleport_candidate_trial else [],
               "teleport_candidate_trial":args.teleport_candidate_trial,
               "teleport_candidate_filter":{"return_rva":0x3302C4,"reason":11,"flag":1} if args.teleport_candidate_trial else None,
               "live_verified":False,"deployed":False,
               "compiler":run([compiler,"--version"],output).strip(),"compiler_sha256":digest(compiler),
               "sources":before,"imports":imports,"compatibility":profile,"profile_validation":profile_report,
               "products":{p.name:{"sha256":digest(p),"bytes":p.stat().st_size} for p in products},
               "commands":[[str(x) for x in command] for command in commands]}
    (output / "build-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("version","products","imports","live_verified","deployed")}))


if __name__ == "__main__":
    main()
