"""Validate exact native build outputs in owned hosts, never in No Man's Sky."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from build_native_probe import ROOT, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", required=True, type=Path)
    args = parser.parse_args()
    directory = args.build.resolve(strict=True)
    receipt = json.loads((directory / "build-receipt.json").read_text(encoding="utf-8"))
    for name, expected in receipt["products"].items():
        if digest(directory/name) != expected["sha256"]:
            raise ValueError("Built product changed: " + name)
    for name, expected in receipt["sources"].items():
        if digest(ROOT/name) != expected:
            raise ValueError("Source changed since build: " + name)
    validators = [
        ("policy", "validate_native_policy.py", "--driver", "policy_reference_driver.exe"),
        ("selection", "validate_native_selection.py", "--driver", "selection_reference_driver.exe"),
        ("storage", "validate_native_storage.py", "--driver", "storage_driver.exe"),
        ("runtime", "validate_native_runtime.py", "--fixture", "runtime_fixture.exe"),
        ("backup", "validate_native_backup.py", "--driver", "backup_driver.exe"),
    ]
    summaries = {}
    for name, script, option, executable in validators:
        report_path = directory / (name+"-validation.json")
        result = subprocess.run([sys.executable,"-X","utf8","-B",str(ROOT/"tools"/script),option,
                                 str(directory/executable),"--report",str(report_path)],
                                cwd=ROOT,capture_output=True,text=True,encoding="utf-8",timeout=120)
        if result.returncode:
            raise RuntimeError(f"{name} validation failed: {result.stdout}\n{result.stderr}")
        summaries[name] = {"report_sha256":digest(report_path),"summary":json.loads(result.stdout)}
        print(json.dumps({"validation":name,"result":summaries[name]["summary"]}),flush=True)
    host_results = []
    abi = subprocess.run([str(directory/"hook_host.exe")],cwd=directory,capture_output=True,
                         text=True,encoding="utf-8",timeout=30)
    if abi.returncode or abi.stderr:
        raise RuntimeError(f"Owned hook ABI smoke failed: {abi.stdout} {abi.stderr}")
    summaries["hook_abi"] = json.loads(abi.stdout)
    stage = Path(tempfile.mkdtemp(prefix="native-host-",dir=ROOT/"build")) / "Káťa 猫"
    stage.mkdir()
    for name in ("native_host.exe","CompanionAutoSummon.asi"):
        shutil.copyfile(directory/name,stage/name)
    for index, cwd in enumerate((directory,stage)):
        for repetition in range(3):
            env = os.environ.copy()
            env["PATH"] = str(Path(os.environ["SystemRoot"])/"System32")
            user = stage / (f"unused-user-{index}-{repetition}")
            env["LOCALAPPDATA"] = env["APPDATA"] = str(user)
            result = subprocess.run([str(cwd/"native_host.exe"),str(cwd/"CompanionAutoSummon.asi")],
                                    cwd=cwd,env=env,capture_output=True,text=True,encoding="utf-8",timeout=25)
            if result.returncode or result.stderr:
                raise RuntimeError(f"Owned native DLL host failed: {result.returncode} {result.stdout} {result.stderr}")
            report = json.loads(result.stdout)
            if report["host_sha256"] != digest(cwd/"native_host.exe") or report["native_status"] != 2 or user.exists():
                raise RuntimeError("Unsupported-host refusal/hash/no-side-effect check failed")
            host_results.append(report)
    for name, expected in receipt["products"].items():
        if digest(directory/name) != expected["sha256"]:
            raise ValueError("Product changed during validation: " + name)
    output = {"version":receipt["version"],"passed":True,"native_host_runs":host_results,
              "validators":summaries,"build_receipt_sha256":digest(directory/"build-receipt.json"),
              "game_started_or_attached":False,"gameplay_verified":False,"deployed":False}
    (directory/"validation-receipt.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"passed":True,"native_host_runs":len(host_results),"gameplay_verified":False}))


if __name__ == "__main__":
    main()
