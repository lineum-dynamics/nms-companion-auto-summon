"""Collect clean-runner build evidence; never deploy, access NMS or upload binaries."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import shutil
import tempfile
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

    def run(arguments, *, cwd=root, check=True):
        command = [str(value) for value in arguments]
        result = subprocess.run(command, cwd=cwd, capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=900)
        report["commands"].append({"arguments": command, "exit_code": result.returncode,
                                    "stdout": result.stdout, "stderr": result.stderr})
        print(result.stdout, end="", flush=True)
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="", flush=True)
        if result.returncode and check:
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
        report["owned_hook_abi"] = json.loads(run([output / "hook_host.exe"]))
        if (output / "minhook_query_host.exe").exists():
            report["owned_query_cases"] = json.loads(run([output / "minhook_query_host.exe"]))
        report["owned_load_context"] = json.loads(run([output / "load_context_host.exe"]))
        run([sys.executable, "-B", "tools/validate_native_menu.py", "--toolchain", toolchain,
             "--output", root / "build/native-clean-menu"])
        run([sys.executable, "-B", "tools/validate_native_bundle.py", "--build", output], check=False)
        if report["commands"][-1]["exit_code"]:
            # Frozen source has a known text-only SID assertion. Validate the
            # actual binary identity before classifying this specific failure.
            backup = json.loads((output / "backup-validation.json").read_bytes())
            controller = Path(__file__).resolve().parents[1]
            spec = importlib.util.spec_from_file_location("controller_backup", controller / "tools/validate_native_backup.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            expected_legacy_failure = (
                report["label"] == "frozen-0103"
                and backup.get("checks") == ["recursive_unicode_byte_hash_receipt_and_source_immutability"]
                and isinstance(backup.get("failure"), str)
                and module.private_dacl_matches_current_user(backup["failure"], require_protected=True))
            if not expected_legacy_failure:
                raise RuntimeError("Native bundle failed beyond the known frozen SID-format assertion")
            for name in module.SOURCES:
                if name != "tools/validate_native_backup.py" and digest(root/name) != digest(controller/name):
                    raise ValueError("Backup code differs from the controller-validated implementation")
            fixed_report = output / "backup-controller-validation.json"
            run([sys.executable, "-B", controller / "tools/validate_native_backup.py", "--driver", output / "backup_driver.exe",
                 "--fixture-parent", root / "build", "--report", fixed_report])
            report["legacy_bundle_passed"] = False
            report["known_legacy_validator_failure"] = "Text-only SID assertion rejects a binary-equivalent account alias; controller validator passed on byte-identical backup implementation."
            report["controller_backup_validation"] = json.loads(fixed_report.read_bytes())
            stage = Path(tempfile.mkdtemp(prefix="owned-host-", dir=root/"build")) / "Káťa 猫"
            stage.mkdir()
            for name in ("native_host.exe", "CompanionAutoSummon.asi"):
                shutil.copyfile(output/name, stage/name)
            host_runs = []
            for index, location in enumerate((output, stage)):
                for repetition in range(3):
                    env = os.environ.copy()
                    env["PATH"] = str(Path(os.environ["SystemRoot"])/"System32")
                    unused_user = stage / f"unused-user-{index}-{repetition}"
                    env["LOCALAPPDATA"] = env["APPDATA"] = str(unused_user)
                    result = subprocess.run([str(location/"native_host.exe"), str(location/"CompanionAutoSummon.asi")],
                                            cwd=location, env=env, capture_output=True, text=True, encoding="utf-8", timeout=30)
                    if result.returncode or result.stderr:
                        raise RuntimeError("Frozen unsupported-host run failed")
                    host = json.loads(result.stdout)
                    if host["native_status"] != 2 or host["host_sha256"] != digest(location/"native_host.exe") or unused_user.exists():
                        raise RuntimeError("Frozen unsupported-host refusal/hash/no-side-effect check failed")
                    host_runs.append(host)
            report["native_host_runs"] = host_runs
            for name, identity in receipt["products"].items():
                if digest(output/name) != identity["sha256"]:
                    raise ValueError("Frozen product changed during validation")
        else:
            report["validation"] = json.loads((output / "validation-receipt.json").read_bytes())
            report["validation_receipt_sha256"] = digest(output / "validation-receipt.json")
        if run(["git", "status", "--porcelain"]).strip():
            raise ValueError("Tracked source changed during reproduction")
        report["passed"] = True
    except Exception as exc:
        report["error"] = type(exc).__name__ + ": " + str(exc)
        print(report["error"], file=sys.stderr)
    finally:
        output = root / "build/native-clean-reproduction"
        partial = {}
        for path in sorted(output.glob("*-validation.json")):
            value = json.loads(path.read_bytes())
            if "failure" in value:
                # ACL diagnostics can contain the ephemeral runner's account SID.
                value["failure"] = re.sub(r"S-1-\d+(?:-\d+)+", "<SID>", value["failure"])
            partial[path.name] = value
        report["component_reports"] = partial
        # Distinguish source-path effects without changing submitted/local bytes.
        # This second build is confined to an ephemeral GitHub runner.
        if os.environ.get("GITHUB_ACTIONS") == "true" and report.get("build"):
            try:
                mirror = Path("C:/Projects/nms-companion-auto-summon-compat-cosmos-706")
                if mirror.exists():
                    raise ValueError("Refuse an existing mirror directory")
                mirror.parent.mkdir(parents=True, exist_ok=True)
                run(["git", "worktree", "add", "--detach", mirror, expected_revision])
                mirror_output = mirror / "build/native-prefix-reproduction"
                run([sys.executable, "-B", mirror / "tools/build_native_runtime.py", "--toolchain", toolchain,
                     "--output", mirror_output, "--teleport-candidate-trial"], cwd=mirror)
                mirror_receipt = json.loads((mirror_output / "build-receipt.json").read_bytes())
                report["source_prefix_control"] = {"products": mirror_receipt["products"],
                    "sources": mirror_receipt["sources"],
                    "matches_frozen_module": mirror_receipt["products"]["CompanionAutoSummon.asi"]["sha256"] == expected_module if expected_module else None}
                if expected_module and not report["source_prefix_control"]["matches_frozen_module"]:
                    report["passed"] = False
                    report["error"] = "Expected module bytes did not reproduce at the original source prefix"
            except Exception as exc:
                report["source_prefix_control_error"] = type(exc).__name__ + ": " + str(exc)
                report["passed"] = False
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        args.report.write_bytes((json.dumps(report, indent=2)+"\n").encode())
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
