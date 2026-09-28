"""Build/run owned menu fixtures and compare the exact native leaf filter bytes.

Never start/attach NMS, install hooks, alter saves or stage player assets. The
CAS_MENU_FIXTURE build excludes the hook installation code and production API
has no fixture initializer. Passing these checks is not game ABI validation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from quick_menu_native_guard import build_filter

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, cwd):
    result = subprocess.run([str(value) for value in args], cwd=cwd, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=180)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toolchain", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / "build").resolve()) or output.exists():
        raise ValueError("Use a new output directory beneath repository build")
    compiler = args.toolchain.resolve() / "bin/x86_64-w64-mingw32-clang++.exe"
    sources = [ROOT / name for name in (
        "native/src/menu.cpp", "native/src/binding_guard.cpp", "native/tests/menu_host.cpp",
        "native/include/cas/menu.hpp", "native/include/cas/binding_guard.hpp",
        "tools/quick_menu_native_guard.py", "tools/validate_native_menu.py")]
    before = {path.relative_to(ROOT).as_posix(): digest(path) for path in sources}
    output.mkdir(parents=True)
    executable = output / "native_menu_fixture.exe"
    command = [compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror", "-static",
               "-DCAS_MENU_FIXTURE", "-DUNICODE", "-D_UNICODE", "-D_WIN32_WINNT=0x0A00",
               "-Wl,--no-insert-timestamp,--dynamicbase,--nxcompat", "-I", ROOT / "native/include",
               *sources[:3], "-o", executable]
    run(command, output)
    report = json.loads(run([executable], output))
    actual = bytes.fromhex(run([executable, "--filter"], output).strip())
    expected = build_filter(0x100151DDEB, 0x10002C1DDE0)
    if actual != expected:
        raise ValueError("C++ native leaf filter differs from audited Python emitter")
    after = {path.relative_to(ROOT).as_posix(): digest(path) for path in sources}
    if before != after:
        raise ValueError("Menu sources changed during validation")
    report.update({"binding_filter_exact_parity": True, "binding_filter_bytes": len(actual),
                   "binding_filter_sha256": hashlib.sha256(actual).hexdigest(),
                   "sources": before, "compiler_sha256": digest(compiler),
                   "fixture_sha256": digest(executable), "deployed": False,
                   "game_abi_validated": False, "command": [str(value) for value in command]})
    (output / "menu-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
