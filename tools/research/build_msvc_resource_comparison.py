"""Build one fixed VERSIONINFO ablation; all native code, guards and analysis remain enabled."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from compare_msvc_analysis_flag import BASELINES, ROOT, digest, read


def main():
    if (os.name != "nt" or os.environ.get("GITHUB_ACTIONS") != "true"
            or os.environ.get("GITHUB_REPOSITORY") != "lineum-dynamics/nms-companion-auto-summon"
            or ROOT != Path("C:/Projects/nms-companion-auto-summon-compat-cosmos-706")):
        raise ValueError("Only the isolated owned Windows runner and original mirror are supported")
    image = os.environ.get("ImageVersion")
    baseline = BASELINES.get(image)
    report_path = ROOT / "build/msvc-resource-comparison.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {"schema": 1, "source_revision": os.environ["SUBJECT_REVISION"],
              "controller_sha256": digest(Path(__file__)), "image_version": image,
              "registered_image_baseline": baseline, "version": "0.10.6-native-test",
              "factor": "Optional StringFileInfo/VarFileInfo blocks; fixed VERSIONINFO fields unchanged",
              "inactive_probe": False, "game_access": False, "local_native_execution": False,
              "av_clearance": False, "packaging_approved": False, "completed": False, "commands": []}

    def run(*arguments):
        command = [sys.executable, "-B", *(str(x) for x in arguments)]
        environment = {key: value for key, value in os.environ.items()
                       if not any(word in key.upper() for word in ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL"))}
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=1200, env=environment)
        report["commands"].append({"arguments": command, "exit_code": result.returncode,
                                   "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            raise RuntimeError("Resource comparison command failed: " + result.stdout + result.stderr)

    def build(label, fixed=False, failure=False):
        directory = ROOT / ("build/msvc-0106-" + label)
        command = [ROOT / "tools/build_native_msvc_audit.py", "--release-candidate", "--output", directory]
        if fixed:
            command.append("--fixed-version-resource-comparison")
        if failure:
            command.append("--startup-failure-fixture")
        run(*command)
        return directory

    def record(label, directory):
        receipt = read(directory / "build-receipt.json")
        report[label] = {"sha256": digest(directory / "CompanionAutoSummon.asi"),
                         "bytes": (directory / "CompanionAutoSummon.asi").stat().st_size,
                         "receipt_sha256": digest(directory / "build-receipt.json"),
                         "pdb_sha256": digest(directory / "CompanionAutoSummon.pdb"),
                         "resource_source_sha256": receipt["resource_source_sha256"]}
        if receipt["dll_static_analysis_included"] is not True:
            raise ValueError("Resource comparison must retain /analyze")
        return receipt

    def dll_command(directory):
        matches = [x["arguments"] for x in read(directory / "compiler-audit.json")["commands"]
                   if any(a.startswith("/Fe") and a.endswith("CompanionAutoSummon.asi") for a in x["arguments"])]
        if len(matches) != 1:
            raise ValueError("Ambiguous DLL compiler command")
        return [x.replace(str(directory), "<OUTPUT>") for x in matches[0]]

    try:
        if baseline is None:
            raise ValueError("No independently reproduced baseline covers this runner image")
        inventory, seen = [], set()
        roots = [(key, Path(value)) for key in ("INCLUDE", "LIB")
                 for value in os.environ[key].split(";") if value]
        roots.append(("COMPILER", Path(os.environ["VCToolsInstallDir"]) / "bin/Hostx64/x64"))
        for kind, root in roots:
            if not root.is_dir():
                raise ValueError("Unavailable compiler input root: " + str(root))
            files = []
            for path in sorted(root.rglob("*")):
                if not path.is_file() or str(path).lower() in seen:
                    continue
                seen.add(str(path).lower())
                with path.open("rb") as stream:
                    checksum = hashlib.file_digest(stream, "sha256").hexdigest()
                files.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": checksum})
            inventory.append({"kind": kind, "root": str(root), "files": files})
        inventory_path = ROOT / "build/msvc-resource-input-inventory.json"
        inventory_path.write_text(json.dumps({"schema": 1, "image_version": image, "roots": inventory,
                                               "file_count": len(seen)}, indent=2) + "\n", encoding="utf-8", newline="\n")
        report["toolchain_input_inventory_sha256"] = digest(inventory_path)
        a = build("a")
        receipt_a = record("baseline", a)
        report["baseline_reproduced"] = report["baseline"]["sha256"] == baseline["sha256"]
        if not report["baseline_reproduced"]:
            raise ValueError("Registered baseline bytes did not reproduce; stop interpretation")
        b = build("b", fixed=True, failure=True)
        receipt_b = record("fixed_resource", b)
        for key in ("sources", "generated", "compatibility", "native_mapping", "version"):
            if receipt_a[key] != receipt_b[key]:
                raise ValueError("Uncontrolled input difference: " + key)
        report["normalized_dll_commands_identical"] = dll_command(a) == dll_command(b)
        report["resource_source_differs"] = report["baseline"]["resource_source_sha256"] != report["fixed_resource"]["resource_source_sha256"]
        report["dll_byte_identical"] = report["baseline"]["sha256"] == report["fixed_resource"]["sha256"]
        if not report["normalized_dll_commands_identical"] or not report["resource_source_differs"] or report["dll_byte_identical"]:
            raise ValueError("The fixed resource ablation was not isolated")
        run(ROOT / "tools/validate_native_bundle.py", "--build", b)
        report["validation_receipt_sha256"] = digest(b / "validation-receipt.json")
        c = build("c", fixed=True)
        record("fixed_resource_repeat", c)
        report["comparison_reproduced"] = report["fixed_resource"]["sha256"] == report["fixed_resource_repeat"]["sha256"]
        if not report["comparison_reproduced"]:
            raise ValueError("Fixed-resource DLL did not reproduce")
        report["completed"] = True
        report["interpretation"] = "Owned validation/reproduction passed; independent program-section comparison and multivendor consequences NOT CHECKED"
    finally:
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ("completed", "baseline_reproduced", "comparison_reproduced")}))


if __name__ == "__main__":
    main()
