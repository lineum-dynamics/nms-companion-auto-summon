"""Compare only DLL /analyze against an independently reproduced, image-specific baseline."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
FROZEN_SHA256 = "30cc9542a2af3529fd4f3a2299d6331bddf51b61f8213a0a1a779b472789de3d"
BASELINES = {
    "20261022.344.1": {
        "sha256": FROZEN_SHA256, "validation_ci": 40653804116,
        "validation_receipt_sha256": "35e23e7b119b7fe3cd89132a24a6e14c9711fea894d55c3595707107dc4efd27"},
    "20261026.347.1": {
        "sha256": "a41fc094e98332682200d6c70857cc21be327843734127c092fc7484e1b583f7",
        "validation_ci": 40714275407,
        "validation_receipt_sha256": "ed0fd1b0700340e44f39dd5d5c2363f247294c097ccdec6faae7dda461bb8fb5"},
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    if (os.name != "nt" or os.environ.get("GITHUB_ACTIONS") != "true"
            or os.environ.get("GITHUB_REPOSITORY") != "lineum-dynamics/nms-companion-auto-summon"):
        raise ValueError("Only an isolated owned GitHub Actions Windows runner may execute this comparison")
    if ROOT != Path("C:/Projects/nms-companion-auto-summon-compat-cosmos-706"):
        raise ValueError("Use the exact original source mirror for the frozen-byte gate")
    report_path = ROOT / "build/msvc-analysis-comparison.json"
    image_version = os.environ.get("ImageVersion")
    baseline = BASELINES.get(image_version)
    report = {"schema": 1, "source_revision": os.environ["SUBJECT_REVISION"],
              "version": "0.10.6-native-test", "frozen_sha256": FROZEN_SHA256,
              "image_version": image_version, "registered_image_baseline": baseline,
              "game_access": False, "local_native_execution": False,
              "packaging_approved": False, "av_clearance": False,
              "completed": False, "commands": []}
    report_path.parent.mkdir(parents=True, exist_ok=True)

    def run(*arguments):
        command = [sys.executable, "-B", *(str(x) for x in arguments)]
        child_environment = {key: value for key, value in os.environ.items()
                             if not any(word in key.upper() for word in
                                        ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL"))}
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=1200,
                                env=child_environment)
        report["commands"].append({"arguments": command, "exit_code": result.returncode,
                                   "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            raise RuntimeError("Comparison command failed: " + result.stdout + result.stderr)

    def build(label, omit=False, failure=False):
        output = ROOT / ("build/msvc-0106-" + label)
        arguments = [ROOT / "tools/build_native_msvc_audit.py", "--release-candidate",
                     "--output", output]
        if omit:
            arguments.append("--omit-analysis-for-comparison")
        if failure:
            arguments.append("--startup-failure-fixture")
        run(*arguments)
        return output

    def record(label, directory):
        receipt = read(directory / "build-receipt.json")
        result = {"sha256": digest(directory / "CompanionAutoSummon.asi"),
                  "bytes": (directory / "CompanionAutoSummon.asi").stat().st_size,
                  "pdb_sha256": digest(directory / "CompanionAutoSummon.pdb"),
                  "receipt_sha256": digest(directory / "build-receipt.json"),
                  "dll_static_analysis_included": receipt["dll_static_analysis_included"]}
        report[label] = result
        return receipt

    def dll_command(directory):
        commands = read(directory / "compiler-audit.json")["commands"]
        matches = [item["arguments"] for item in commands
                   if any(arg.endswith("CompanionAutoSummon.asi") and arg.startswith("/Fe")
                          for arg in item["arguments"])]
        if len(matches) != 1:
            raise ValueError("The exact DLL compiler command is ambiguous")
        return [arg.replace(str(directory), "<OUTPUT>") for arg in matches[0]]

    def record_toolchain_inputs():
        roots = []
        for variable in ("INCLUDE", "LIB"):
            roots += [(variable, Path(value)) for value in os.environ[variable].split(";") if value]
        roots.append(("COMPILER", Path(os.environ["VCToolsInstallDir"]) / "bin/Hostx64/x64"))
        inventory, seen = [], set()
        for kind, root in roots:
            if not root.is_dir():
                raise ValueError("Configured compiler input directory is unavailable: " + str(root))
            files = []
            for path in sorted(root.rglob("*")):
                if not path.is_file() or str(path).lower() in seen:
                    continue
                seen.add(str(path).lower())
                with path.open("rb") as stream:
                    checksum = hashlib.file_digest(stream, "sha256").hexdigest()
                files.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size,
                              "sha256": checksum})
            inventory.append({"kind": kind, "root": str(root), "files": files})
        path = ROOT / "build/msvc-analysis-input-inventory.json"
        path.write_text(json.dumps({"schema": 1, "image_version": report["image_version"],
                                    "roots": inventory, "file_count": len(seen),
                                    "scope": "Configured include/library trees and native x64 compiler directory; not proof every file was consumed"},
                                   indent=2) + "\n", encoding="utf-8", newline="\n")
        report["toolchain_input_inventory_sha256"] = digest(path)
        report["toolchain_inventory_file_count"] = len(seen)

    try:
        if baseline is None:
            raise ValueError("No registered independently reproduced baseline covers this runner image")
        record_toolchain_inputs()
        a = build("a")
        receipt_a = record("analysis_enabled", a)
        report["original_frozen_reproduced"] = report["analysis_enabled"]["sha256"] == FROZEN_SHA256
        report["baseline_reproduced"] = report["analysis_enabled"]["sha256"] == baseline["sha256"]
        if not report["baseline_reproduced"]:
            raise RuntimeError("Registered image-specific baseline did not reproduce; do not interpret the flag comparison")
        b = build("b", omit=True, failure=True)
        receipt_b = record("analysis_omitted", b)
        for field in ("sources", "generated", "compatibility", "native_mapping", "version"):
            if receipt_a[field] != receipt_b[field]:
                raise ValueError("Uncontrolled build input difference: " + field)
        report["resource_source_identical"] = digest(a / "version.rc") == digest(b / "version.rc")
        command_a, command_b = dll_command(a), dll_command(b)
        report["only_dll_compiler_argument_difference_is_analyze"] = (
            command_a.count("/analyze") == 1 and "/analyze" not in command_b
            and [arg for arg in command_a if arg != "/analyze"] == command_b)
        if not (report["resource_source_identical"]
                and report["only_dll_compiler_argument_difference_is_analyze"]):
            raise ValueError("The single-flag comparison is not controlled")
        report["dll_byte_identical"] = report["analysis_omitted"]["sha256"] == baseline["sha256"]
        if report["dll_byte_identical"]:
            report["interpretation"] = "No /analyze output-byte difference on registered image " + image_version
            report["functional_retest"] = ("NOT REPEATED: identical baseline passed owned full bundle in CI "
                                           + str(baseline["validation_ci"]) + "; factory-failure control ran during build B")
            report["third_build"] = "NOT REPEATED: A and B are byte-identical"
        else:
            run(ROOT / "tools/validate_native_bundle.py", "--build", b)
            report["functional_retest"] = "PASSED: owned full bundle and factory-failure control"
            report["validation_receipt_sha256"] = digest(b / "validation-receipt.json")
            c = build("c", omit=True)
            record("analysis_omitted_repeat", c)
            report["comparison_reproduced"] = (
                report["analysis_omitted"]["sha256"] == report["analysis_omitted_repeat"]["sha256"])
            if not report["comparison_reproduced"]:
                raise RuntimeError("Flag-off DLL did not reproduce; no artifact may be selected")
            report["interpretation"] = "Controlled reproducible byte difference; PE and antivirus consequences NOT CHECKED"
        report["completed"] = True
    finally:
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: report[key] for key in
                     ("completed", "baseline_reproduced", "dll_byte_identical", "interpretation")}))


if __name__ == "__main__":
    main()
