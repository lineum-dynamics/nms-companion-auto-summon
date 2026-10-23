"""Collect clean-runner build evidence; never deploy, access NMS or upload binaries."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--toolchain", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    root = args.source.resolve(strict=True)
    toolchain = args.toolchain.resolve(strict=True)
    expected_revision = os.environ["SOURCE_REVISION"]
    expected_module = os.environ["EXPECTED_MODULE"]
    if not re.fullmatch(r"[0-9a-f]{40}", expected_revision):
        raise ValueError("Expected a full source commit")
    if expected_module and not re.fullmatch(r"[0-9a-f]{64}", expected_module):
        raise ValueError("Invalid expected module digest")
    report = {"schema": 1, "label": os.environ["REPRODUCTION_LABEL"],
              "expected_source_revision": expected_revision,
              "expected_module_sha256": expected_module or None,
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "python_executable_sha256": digest(Path(sys.executable)),
              "platform": platform.platform(), "commands": [], "passed": False,
              "game_access": False, "deployed": False, "binary_upload": False}

    def run(arguments):
        command = [str(value) for value in arguments]
        result = subprocess.run(command, cwd=root, capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=900)
        report["commands"].append({"arguments": command, "exit_code": result.returncode,
                                    "stdout": result.stdout, "stderr": result.stderr})
        print(result.stdout, end="", flush=True)
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="", flush=True)
        if result.returncode:
            raise RuntimeError("Build/validation command failed; preserve evidence without bypass")
        return result.stdout

    try:
        revision = run(["git", "rev-parse", "HEAD"]).strip()
        report["source_revision"] = revision
        if revision != expected_revision:
            raise ValueError("Checked-out source differs from requested commit")
        if run(["git", "status", "--porcelain"]).strip():
            raise ValueError("Source checkout is dirty before the build")
        compiler = toolchain / "bin/x86_64-w64-mingw32-clang++.exe"
        report["compiler_sha256"] = digest(compiler)
        if report["compiler_sha256"] != "20ba1856942744291a6aaaf9f2c94f6d0cd7cac5aa9557fce96471dc7ef25d6f":
            raise ValueError("Compiler differs from the reviewed wrapper")
        run([sys.executable, "-B", "tools/validate_locales.py"])
        run([sys.executable, "-B", "tools/validate_compatibility.py", "--developer", "--generated"])
        if (root / "tools/validate_native_dependencies.py").exists():
            run([sys.executable, "-B", "tools/validate_native_dependencies.py"])
        output = root / "build/native-clean-reproduction"
        run([sys.executable, "-B", "tools/build_native_runtime.py", "--toolchain", toolchain,
             "--output", output, "--teleport-candidate-trial"])
        receipt = json.loads((output / "build-receipt.json").read_bytes())
        report["build"] = {key: receipt[key] for key in
                            ("version", "sources", "products", "imports", "compiler_sha256", "compatibility", "native_mapping")}
        report["build_receipt_sha256"] = digest(output / "build-receipt.json")
        report["generated_headers"] = {p.name: digest(p) for p in sorted((output / "generated").glob("*.hpp"))}
        module = receipt["products"]["CompanionAutoSummon.asi"]["sha256"]
        report["module_matches_expected"] = module == expected_module if expected_module else None
        run([sys.executable, "-B", "tools/validate_native_bundle.py", "--build", output])
        report["validation"] = json.loads((output / "validation-receipt.json").read_bytes())
        report["validation_receipt_sha256"] = digest(output / "validation-receipt.json")
        run([sys.executable, "-B", "tools/validate_native_menu.py", "--toolchain", toolchain,
             "--output", root / "build/native-clean-menu"])
        if run(["git", "status", "--porcelain"]).strip():
            raise ValueError("Tracked source changed during reproduction")
        report["passed"] = True
    except Exception as exc:
        report["error"] = type(exc).__name__ + ": " + str(exc)
        print(report["error"], file=sys.stderr)
    finally:
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        args.report.write_bytes((json.dumps(report, indent=2)+"\n").encode())
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
