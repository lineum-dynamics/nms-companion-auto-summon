"""Exercise only our inert native DLL inside our owned offline host.

No loader installation, game discovery/start/attach, settings, saves or runtime
editing. Product hashes must match the explicit build receipt before execution.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def tree(path):
    return {p.relative_to(path).as_posix(): digest(p) for p in path.rglob("*") if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    if not bundle.is_relative_to((ROOT / "build").resolve()):
        raise ValueError("Use the owned probe build under the repository build directory")
    receipt = json.loads((bundle / "build-receipt.json").read_text(encoding="utf-8"))
    dll_name = "CompanionAutoSummon.NativeProbe.asi"
    host_name = "native_probe_host.exe"
    for name in (dll_name, host_name):
        if digest(bundle / name) != receipt["products"][name]["sha256"]:
            raise ValueError(f"Probe product changed: {name}")
    environment = os.environ.copy()
    environment["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
    relocated = bundle / "Offline host Káťa 猫"
    relocated.mkdir()
    shutil.copy2(bundle / dll_name, relocated / dll_name)
    shutil.copy2(bundle / host_name, relocated / host_name)
    before = tree(bundle)
    results = []
    for directory in (bundle, relocated):
        for attempt in range(3):
            process = subprocess.run([str(directory / host_name), str(directory / dll_name)],
                                     cwd=directory, env=environment, capture_output=True,
                                     text=True, encoding="utf-8", errors="strict",
                                     timeout=30, check=True)
            observed = json.loads(process.stdout)
            expected_hash = digest(directory / host_name)
            if (observed != {"status": 4, "hooks_active": 0, "abi_version": 1,
                            "image_sha256": expected_hash, "initialization_status": 4}):
                raise AssertionError(f"Unexpected inert probe result: {observed}")
            results.append({"relocated": directory == relocated, "attempt": attempt + 1,
                            "observed": observed})
    if before != tree(bundle):
        raise AssertionError("The native probe or its owned host changed the bundle")
    report = {"passed": True, "owned_host_runs": len(results),
              "concurrent_initializers_per_run": 8, "results": results,
              "bundle_unchanged_during_host_runs": True, "native_game_host_tested": False,
              "game_started_or_attached": False, "loader_installed": False,
              "profile_match_activation": "Unimplemented; even a match remains inert",
              "build_receipt_sha256": digest(bundle / "build-receipt.json"),
              "validator_sha256": digest(Path(__file__))}
    (bundle / "probe-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
