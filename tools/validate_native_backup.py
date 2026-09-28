"""Verify before-native-hooks backup against isolated repository-owned fixtures.

No game launch, installed mod paths, save discovery or real user data is used.
The native driver accesses only explicit freshly created build/ fixture paths.
"""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("native/include/cas/backup.hpp", "native/src/backup.cpp", "native/tests/backup_driver.cpp",
           "native/third_party/json.hpp", "tools/validate_native_backup.py")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invoke(driver, saves, preferences, destination, **options):
    request = {"saves": str(saves), "preferences": str(preferences), "destination": str(destination), **options}
    result = subprocess.run([str(driver)], input=json.dumps(request) + "\n", text=True,
                            capture_output=True, encoding="utf-8", timeout=60, check=True)
    return json.loads(result.stdout)


def snapshot(root):
    return {path.relative_to(root).as_posix(): (path.stat().st_size, digest(path))
            for path in root.rglob("*") if path.is_file() and not path.is_symlink()}


def dacl_sddl(path):
    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    get_security = advapi.GetFileSecurityW
    get_security.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
                             ctypes.POINTER(wintypes.DWORD)]
    get_security.restype = wintypes.BOOL
    convert = advapi.ConvertSecurityDescriptorToStringSecurityDescriptorW
    convert.argtypes = [ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                        ctypes.POINTER(wintypes.LPWSTR), ctypes.POINTER(wintypes.DWORD)]
    convert.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    size = wintypes.DWORD()
    get_security(str(path), 4, None, 0, ctypes.byref(size))
    assert size.value, ctypes.get_last_error()
    buffer = ctypes.create_string_buffer(size.value)
    assert get_security(str(path), 4, buffer, size, ctypes.byref(size)), ctypes.get_last_error()
    text = wintypes.LPWSTR()
    assert convert(buffer, 1, 4, ctypes.byref(text), None), ctypes.get_last_error()
    try:
        return text.value
    finally:
        kernel.LocalFree(ctypes.cast(text, ctypes.c_void_p))


def validate(driver):
    root = Path(tempfile.mkdtemp(prefix="native-backup-", dir=ROOT / "build"))
    report = {"schema": 1, "scope": "isolated before-native-hooks snapshot fixtures",
              "game_access": False, "live_user_data_access": False, "native_hooks": False,
              "fixture_root": str(root), "started_utc": datetime.now(timezone.utc).isoformat(),
              "driver": {"path": str(driver), "sha256": digest(driver)},
              "source_sha256": {name: digest(ROOT / name) for name in SOURCES},
              "passed": False, "checks": []}
    checks = report["checks"]
    try:
        saves = root / "Saves Káťa 猫"
        prefs = root / "Preferences Káťa 猫"
        targets = root / "Snapshots"
        saves.mkdir(); prefs.mkdir(); targets.mkdir()
        (saves / "nested" / "empty").mkdir(parents=True)
        contents = {"save.hg": os.urandom(132017), "mf_save.hg": b"metadata\x00\xff", "empty.bin": b"",
                    "nested/accountdata.hg": os.urandom(1048577), "nested/猫.hg": bytes(range(256))}
        for name, content in contents.items():
            (saves / name).write_bytes(content)
        (prefs / "settings.json").write_text('{"enabled":true}', encoding="utf-8")
        (prefs / "state.json").write_text('{"selections":{}}', encoding="utf-8")
        (prefs / "do-not-copy.log").write_text("unrelated content", encoding="utf-8")
        before_saves, before_prefs = snapshot(saves), snapshot(prefs)
        target = targets / "valid"
        result = invoke(driver, saves, prefs, target)
        assert result["ok"], result
        assert result["files"] == 7
        assert snapshot(target / "saves") == before_saves
        assert (target / "saves" / "nested" / "empty").is_dir()
        assert set(snapshot(target / "preferences")) == {"settings.json", "state.json"}
        assert not (target / "INCOMPLETE").exists()
        receipt = json.loads((target / "receipt.json").read_text(encoding="utf-8"))
        assert receipt["phase"] == "before_native_hooks" and receipt["game_closed_before_and_after"] is False
        assert receipt["sources_write_locked_during_verification"] is True
        assert receipt["snapshot_permissions"] == "protected_current_user_and_system"
        assert receipt["file_count"] == 7 and sum(item["bytes"] for item in receipt["files"]) == result["bytes"]
        for item in receipt["files"]:
            path = target / item["path"]
            assert path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]
        assert snapshot(saves) == before_saves and snapshot(prefs) == before_prefs
        checks.append("recursive_unicode_byte_hash_receipt_and_source_immutability")
        acl = dacl_sddl(target)
        assert acl.startswith("D:P") and acl.count("(") == 2 and ";;;SY)" in acl and ";;;S-1-5-21-" in acl, acl
        child_acl = dacl_sddl(target / "saves" / "save.hg")
        assert child_acl.count("(") == 2 and ";;;SY)" in child_acl and ";;;S-1-5-21-" in child_acl, child_acl
        checks.append("protected_current_user_system_acl_and_child_inheritance")

        # Existing snapshots are never replaced, even if apparently incomplete.
        before_target = snapshot(target)
        result = invoke(driver, saves, prefs, target)
        assert not result["ok"] and snapshot(target) == before_target
        checks.append("existing_destination_preserved")

        # A writer already holding the save prevents obtaining the necessary
        # lock; a retained INCOMPLETE marker makes this visibly non-restorable.
        blocked = targets / "locked"
        result = invoke(driver, saves, prefs, blocked, hold_writer=str(saves / "save.hg"))
        assert not result["ok"] and result["error"] == "backup", result
        assert (blocked / "INCOMPLETE").is_file() and not (blocked / "receipt.json").exists()
        assert snapshot(saves) == before_saves
        checks.append("existing_writer_refused_incomplete_snapshot_retained")

        # Empty/missing new-player roots are accurately distinguished.
        result = invoke(driver, root / "missing-saves", root / "missing-prefs", targets / "absent")
        assert result == {"ok": True, "files": 0, "bytes": 0, "saves_present": False, "preferences_present": False}
        checks.append("absent_new_player_roots_are_explicit")
        empty = root / "empty-saves"; empty.mkdir()
        result = invoke(driver, empty, root / "missing-prefs", targets / "empty")
        assert result["ok"] and result["saves_present"] and result["files"] == 0
        checks.append("empty_existing_saves_preserved")
        own_prefs = root / "prefs-with-backups"; own_prefs.mkdir()
        (own_prefs / "settings.json").write_bytes(b"original preference content")
        (own_prefs / "backups").mkdir()
        result = invoke(driver, empty, own_prefs, own_prefs / "backups" / "new")
        assert result["ok"] and result["files"] == 1
        assert (own_prefs / "settings.json").read_bytes() == b"original preference content"
        checks.append("private_snapshot_inside_preference_backup_directory")

        # Only the two named preference files enter the backup. A misleading
        # directory with one of these names must not be followed recursively.
        invalid_prefs = root / "invalid-prefs"; invalid_prefs.mkdir()
        (invalid_prefs / "settings.json").mkdir()
        result = invoke(driver, empty, invalid_prefs, targets / "invalid-prefs")
        assert not result["ok"] and (targets / "invalid-prefs" / "INCOMPLETE").exists()
        checks.append("preference_directory_refused")

        for name, s, p, d in (
            ("save_destination_overlap", saves, prefs, saves / "backup"),
            ("missing_destination_parent", saves, prefs, targets / "missing" / "nested"),
            ("relative_source", Path("relative-saves"), prefs, targets / "relative"),
            ("source_file_instead_of_root", saves / "save.hg", prefs, targets / "root-file"),
        ):
            result = invoke(driver, s, p, d)
            assert not result["ok"], (name, result)
            checks.append(name)

        # Reparse points require developer mode for symlinks, but a directory
        # junction is supported for a standard Windows user. It targets only
        # another owned fixture and is never removed by this validator.
        junction = root / "junction-saves"
        created = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(saves)],
                                 capture_output=True, text=True, check=False)
        assert created.returncode == 0, created.stderr
        result = invoke(driver, junction, prefs, targets / "junction")
        assert not result["ok"] and not (targets / "junction").exists()
        checks.append("source_reparse_root_refused_without_following")
        result = invoke(driver, saves, prefs, junction / "destination")
        assert not result["ok"] and not (saves / "destination").exists()
        checks.append("destination_reparse_ancestor_refused")

        # Size checking occurs from metadata before copying a sparse oversized
        # fixture, avoiding hundreds of megabytes of test I/O.
        oversized = root / "oversized"; oversized.mkdir()
        with (oversized / "large.hg").open("wb") as stream:
            stream.truncate(256 * 1024 * 1024 + 1)
        result = invoke(driver, oversized, root / "missing-prefs", targets / "oversized")
        assert not result["ok"] and (targets / "oversized" / "INCOMPLETE").exists()
        assert not (targets / "oversized" / "saves" / "large.hg").exists()
        checks.append("oversized_source_refused_before_copy")
        deep = root / "deep"; deep.mkdir(); node = deep
        for _ in range(33):
            node /= "d"; node.mkdir()
        result = invoke(driver, deep, root / "missing-prefs", targets / "deep")
        assert not result["ok"] and (targets / "deep" / "INCOMPLETE").exists()
        checks.append("excessive_directory_depth_refused")

        assert snapshot(saves) == before_saves and snapshot(prefs) == before_prefs
        assert digest(driver) == report["driver"]["sha256"]
        assert all(digest(ROOT / name) == value for name, value in report["source_sha256"].items())
        report["passed"] = True
    except (AssertionError, OSError, ValueError, subprocess.SubprocessError) as error:
        report["failure"] = str(error)
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    driver, destination = args.driver.resolve(strict=True), args.report.resolve()
    if destination == driver or destination in {ROOT / name for name in SOURCES}:
        parser.error("Report must not overwrite a validation input")
    report = validate(driver)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "checks": len(report["checks"]), "report": str(destination)}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
