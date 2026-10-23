"""Verify retained native dependency bytes and the single documented local patch."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PATCH_PATH = "native/third_party/minhook/src/buffer.c"
ORIGINAL_SHA256 = "0ab484d7870c3a8e7a3a1ee61e2070072cf445ed85b619d4c4207fed34356d99"
ORIGINAL_BYTES = 9814
ORIGINAL_QUERY = b"    VirtualQuery(pAddress, &mi, sizeof(mi));"
GUARDED_QUERY = (b"    if (VirtualQuery(pAddress, &mi, sizeof(mi)) != sizeof(mi))\n"
                 b"        return FALSE;")


def validate(*, source_root: Path = ROOT) -> dict:
    root = source_root.resolve(strict=True)
    lock = json.loads((root / "native/dependencies-lock.json").read_bytes())
    seen = set()
    patched = []
    for component in lock["components"]:
        local = component.get("local_modifications", [])
        if local and (component["name"] != "MinHook" or len(local) != 1
                      or local[0].get("id") != "cas-minhook-virtualquery-result-guard"
                      or local[0].get("path") != PATCH_PATH):
            raise ValueError("Unexpected local dependency modification")
        for entry in component.get("retained_files", []):
            _check_file(root, entry, seen)
            if entry["path"] == PATCH_PATH:
                if component.get("retained_files_match_exact_upstream_bytes") is not False or not local:
                    raise ValueError("Patched MinHook must declare its local provenance")
                if (entry.get("upstream_sha256") != ORIGINAL_SHA256
                        or entry.get("upstream_bytes") != ORIGINAL_BYTES):
                    raise ValueError("Original MinHook identity differs")
                data = (root / PATCH_PATH).read_bytes()
                if data.count(GUARDED_QUERY) != 1:
                    raise ValueError("Expected exactly one MinHook query guard")
                original = data.replace(GUARDED_QUERY, ORIGINAL_QUERY)
                if (len(original) != ORIGINAL_BYTES
                        or hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256):
                    raise ValueError("MinHook delta exceeds the documented query guard")
                patched.append(PATCH_PATH)
    if patched != [PATCH_PATH]:
        raise ValueError("Missing patched MinHook identity")
    for entry in lock["notice_files"]:
        _check_file(root, entry, seen)
    return {"passed": True, "retained_and_notice_files": len(seen),
            "local_patches": patched, "network_access": False}


def _check_file(root: Path, entry: dict, seen: set) -> None:
    name = entry["path"]
    path = PurePosixPath(name)
    if (not name.startswith("native/") or "\\" in name or ":" in name
            or path.is_absolute() or any(p in ("", ".", "..") for p in name.split("/"))):
        raise ValueError("Invalid dependency path")
    if name in seen:
        raise ValueError("Duplicate dependency path")
    seen.add(name)
    resolved = (root / name).resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError("Dependency path escapes source root")
    data = resolved.read_bytes()
    if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise ValueError("Dependency identity differs: " + name)


if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))
