"""Run offline tests and record the exact source bytes tested.

From the repository root: python -B tools/validate_offline.py
No framework import, game discovery, installation, or deployment is performed.
"""

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIRECTORY = ROOT / "build" / "validation"


def source_hashes():
    files = sorted([
        ROOT / "AutoPet.py", ROOT / "Launch-AutoPet.py", ROOT / "build.py",
        ROOT / "Start-AutoPet.ps1", *ROOT.glob("src/*.py"),
        *ROOT.glob("tests/test_*.py"),
    ])
    return {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files}


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def main():
    sys.dont_write_bytecode = True
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    package_version = manifest["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+-experimental", package_version):
        raise ValueError("Expected an explicit experimental version in manifest.json")
    version = package_version.removesuffix("-experimental")
    before = source_hashes()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    counts = Counter(case.id().split(".")[0] for case in cases(suite))
    REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    transcript = REPORT_DIRECTORY / f"offline-{version}.txt"
    with transcript.open("w", encoding="utf-8") as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    after = source_hashes()
    record = {
        "version": version,
        "package_version": package_version,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "passed": (result.wasSuccessful() and before == after
                   and result.testsRun > 0 and not result.skipped
                   and sum(counts.values()) == result.testsRun),
        "tests_run": result.testsRun,
        "counts": dict(sorted(counts.items())),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "source_unchanged_during_test": before == after,
        "source_sha256": before,
    }
    (REPORT_DIRECTORY / f"offline-{version}.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in record.items() if key != "source_sha256"}))
    print(f"Test transcript: {transcript}")
    return 0 if record["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
