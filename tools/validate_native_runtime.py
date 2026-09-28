"""Execute owned-memory integration tests of the native Runtime class.

Only the explicitly supplied fixture executable is executed. Its synthetic
addresses are keys in an owned byte map, never dereferenced pointers. All files
are test settings/favorites under a new repository build/ directory. No game,
installed runtime, real save or user-directory discovery is involved.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import uuid


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "native/include/cas/runtime.hpp", "native/src/runtime.cpp",
    "native/include/cas/policy.hpp", "native/src/policy.cpp",
    "native/include/cas/selection.hpp", "native/src/selection.cpp",
    "native/include/cas/storage.hpp", "native/src/storage.cpp",
    "native/tests/runtime_fixture.cpp", "tools/validate_native_runtime.py",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    fixture = args.fixture.resolve(strict=True)
    directory = ROOT / "build" / ("native-runtime-fixtures-" + uuid.uuid4().hex)
    assert directory.resolve().is_relative_to((ROOT / "build").resolve())
    assert not directory.exists()
    result = subprocess.run([str(fixture), str(directory)], cwd=ROOT, capture_output=True,
                            text=True, encoding="utf-8", timeout=90)
    report = json.loads(result.stdout)
    report.update({
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "fixture_directory": str(directory),
        "fixture_executable": {"path": str(fixture), "sha256": digest(fixture)},
        "source_sha256": {name: digest(ROOT / name) for name in SOURCES},
        "boundary": "Real Runtime, policy, selection and storage; synthetic address map/native service doubles only; no NMS validation",
        "stderr": result.stderr, "exit_code": result.returncode,
    })
    if result.stderr or result.returncode != 0:
        report["status"] = "failed"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "cases": report["cases"],
                      "failures": [item for item in report["results"] if item["status"] != "passed"]}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
