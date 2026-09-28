"""Build an inert native DLL and owned offline hosts. Never deploy or start NMS.

The explicit compiler input is a developer toolchain; this tool does not fetch
dependencies, execute the built code, scan uploads, or modify installed mods.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_locales import validate as validate_locales
from validate_compatibility import validate as validate_compatibility


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(command, output):
    result = subprocess.run([str(arg) for arg in command], cwd=output,
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=180, check=False)
    if result.returncode:
        raise RuntimeError(f"Compiler/tool failed ({result.returncode}):\n{result.stderr}")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toolchain", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / "build").resolve()) or output.exists():
        raise ValueError("Use a new output directory beneath the repository build directory")
    compiler = args.toolchain.resolve() / "bin/x86_64-w64-mingw32-clang++.exe"
    inspect = args.toolchain.resolve() / "bin/llvm-readobj.exe"
    if not compiler.is_file() or not inspect.is_file():
        raise ValueError("Expected a Windows x64 LLVM-MinGW compiler and llvm-readobj")
    locale_report = validate_locales(locales_dir=ROOT / "locales", source_root=ROOT)
    compatibility_report = validate_compatibility(source_root=ROOT, developer=True, generated=True)
    profile = json.loads((ROOT / "compatibility.json").read_text(encoding="utf-8"))
    if (not re.fullmatch(r"[a-f0-9]{64}", profile["exe_sha256"]) or
            not re.fullmatch(r"\d+", profile["steam_build"])):
        raise ValueError("Invalid compatibility identity")
    sources = sorted((ROOT / "native").rglob("*.cpp"))
    sources += sorted((ROOT / "native").rglob("*.hpp"))
    sources += sorted((ROOT / "native").rglob("*.h"))
    sources += [ROOT / "compatibility.json", ROOT / "native/toolchain-lock.json", Path(__file__)]
    before = {p.relative_to(ROOT).as_posix(): digest(p) for p in sources}
    output.mkdir(parents=True)
    generated = output / "generated"
    generated.mkdir()
    (generated / "compatibility_profile.hpp").write_text(
        "#pragma once\nnamespace cas::profile {\n"
        f"inline constexpr char exe_sha256[] = {json.dumps(profile['exe_sha256'])};\n"
        f"inline constexpr char steam_build[] = {json.dumps(profile['steam_build'])};\n"
        "}\n", encoding="utf-8")
    version = run([compiler, "--version"], output)
    version_note = "Compiler version recorded; archive provenance is a separate verification"
    common = [compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
              "-DUNICODE", "-D_UNICODE", "-D_WIN32_WINNT=0x0A00", "-static",
              "-Wl,--no-insert-timestamp,--dynamicbase,--nxcompat",
              "-I", ROOT / "native/include", "-I", generated]
    commands = [
        [*common, "-shared", "-DCAS_PROBE_BUILD", ROOT / "native/src/probe.cpp",
         "-lbcrypt", "-o", output / "CompanionAutoSummon.NativeProbe.asi"],
        [*common, "-municode", ROOT / "native/tests/probe_host.cpp",
         "-o", output / "native_probe_host.exe"],
        [*common, ROOT / "native/src/policy.cpp", ROOT / "native/tests/policy_reference_driver.cpp",
         "-o", output / "policy_reference_driver.exe"],
    ]
    for command in commands:
        run(command, output)
    binary = output / "CompanionAutoSummon.NativeProbe.asi"
    pe = run([inspect, "--file-header", "--coff-imports", "--coff-exports", binary], output)
    (output / "probe-pe.txt").write_text(pe, encoding="utf-8")
    for export in ("CasInspectHost", "CasInitializationStatus", "InitializeASI"):
        if f"Name: {export}\n" not in pe:
            raise RuntimeError(f"Missing required export: {export}")
    imports = re.findall(r"Import \{\s+Name: ([^\r\n]+)", pe)
    if not imports or any(name.lower().startswith(("libc++", "libunwind", "libgcc", "python"))
                          for name in imports):
        raise RuntimeError("Missing import evidence or unexpected external language runtime")
    after = {p.relative_to(ROOT).as_posix(): digest(p) for p in sources}
    if before != after:
        raise RuntimeError("Native source changed during build")
    products = [binary, output / "native_probe_host.exe", output / "policy_reference_driver.exe"]
    receipt = {
        "milestone": "inert-native-probe-1", "gameplay_enabled": False,
        "deployed": False, "game_started_or_attached": False, "test_execution": False,
        "compiler_version": version.strip(), "compiler_sha256": digest(compiler),
        "compiler_provenance_note": version_note, "compatibility": profile,
        "sources": before, "locales": locale_report, "profile_validation": compatibility_report,
        "imports": imports,
        "products": {p.name: {"sha256": digest(p), "bytes": p.stat().st_size} for p in products},
        "commands": [[str(a) for a in command] for command in commands],
    }
    (output / "build-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"milestone": receipt["milestone"], "products": receipt["products"],
                      "gameplay_enabled": False, "deployed": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
