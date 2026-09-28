"""Read every bundled PE import table without loading its native files.

Use the isolated runtime's Python so pefile comes from its pinned wheel. This
inventory includes unused optional modules; it is not a clean-Windows test.
"""

import argparse
import hashlib
import json
from pathlib import Path

import pefile


def audit(runtime):
    root = Path(runtime).resolve(strict=True)
    records = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in {".exe", ".pyd", ".dll"}:
            continue
        data = path.read_bytes()
        binary = pefile.PE(data=data, fast_load=True)
        try:
            binary.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT"],
            ])
            imports = sorted({entry.dll.decode("ascii").lower()
                              for key in ("DIRECTORY_ENTRY_IMPORT", "DIRECTORY_ENTRY_DELAY_IMPORT")
                              for entry in getattr(binary, key, [])})
            records.append({"path": path.relative_to(root).as_posix(),
                            "sha256": hashlib.sha256(data).hexdigest(), "imports": imports})
        finally:
            binary.close()
    return {"native_files": len(records), "records": records, "binaries_loaded": False,
            "game_accessed": False, "scope": "PE imports, including unused optional modules"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.runtime)
    with args.report.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({key: value for key, value in result.items() if key != "records"}))
