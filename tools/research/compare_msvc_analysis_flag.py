"""Compare only DLL /analyze after reproducing the frozen 0.10.6 bytes in owned CI."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
FROZEN_SHA256 = "30cc9542a2af3529fd4f3a2299d6331bddf51b61f8213a0a1a779b472789de3d"


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
    report = {"schema": 1, "source_revision": os.environ["SUBJECT_REVISION"],
              "version": "0.10.6-native-test", "frozen_sha256": FROZEN_SHA256,
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

    try:
        a = build("a")
        receipt_a = record("analysis_enabled", a)
        report["baseline_reproduced"] = report["analysis_enabled"]["sha256"] == FROZEN_SHA256
        if not report["baseline_reproduced"]:
            raise RuntimeError("Frozen baseline did not reproduce; do not interpret the flag comparison")
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
        report["dll_byte_identical"] = report["analysis_omitted"]["sha256"] == FROZEN_SHA256
        if report["dll_byte_identical"]:
            report["interpretation"] = "No output-byte difference; /analyze cannot explain the frozen-file detection difference"
            report["functional_retest"] = "NOT REPEATED: same frozen DLL already validated; factory-failure control ran during build B"
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
