"""Differential test of native storage in new repository-owned fixture folders.

The executable path must be explicit. Only fresh paths below repository build/
are supplied to the native driver or maintained Python storage references. This
tool never resolves LOCALAPPDATA, discovers saves, launches or attaches to NMS,
or reads/writes an installed mod. No third-party Python packages are required.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "native/include/cas/storage.hpp", "native/src/storage.cpp", "native/tests/storage_driver.cpp",
    "native/third_party/json.hpp", "src/settings.py", "src/persistence.py",
)


def reference(filename: str, name: str):
    path = ROOT / "src" / filename
    namespace = {"__name__": "cas_offline_storage_reference", "__file__": str(path)}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), namespace)
    return namespace[name], namespace


Settings, SETTINGS_NAMESPACE = reference("settings.py", "CompanionAutoSummonSettingsStore")
Selections, SELECTION_NAMESPACE = reference("persistence.py", "PetSelectionStore")
STORE_ERRORS = (SETTINGS_NAMESPACE["SettingsStoreError"], SELECTION_NAMESPACE["SelectionStoreError"])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invoke_python(path: Path, command: dict):
    op = command["op"]
    if op == "settings_load":
        return Settings(path).load_preferences()
    if op == "settings_enabled":
        return Settings(path).load()
    if op == "settings_save":
        return Settings(path).save_preferences(command["value"])
    if op == "settings_set_enabled":
        return Settings(path).save(command["value"])
    if op == "selection_load":
        return Selections(path).load(command["key"])
    if op == "selection_remember":
        return Selections(path).remember(command["key"], bytes.fromhex(command["seed"]), command["slot"])
    if op == "selection_forget":
        return Selections(path).forget(command["key"])
    raise AssertionError(op)


def response_python(path: Path, command: dict) -> dict:
    try:
        return {"ok": True, "result": invoke_python(path, command)}
    except STORE_ERRORS:
        return {"ok": False, "error": "storage"}
    except (ValueError, TypeError):
        return {"ok": False, "error": "argument"}


class Harness:
    def __init__(self, driver: Path, fixtures: Path):
        self.fixtures = fixtures
        self.process = subprocess.Popen(
            [str(driver)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", cwd=fixtures,
        )
        self.operations = 0
        self.cases = 0
        self.counts: dict[str, int] = {}
        self.names: list[str] = []

    def native(self, path: Path, command: dict) -> dict:
        assert path.resolve().is_relative_to(self.fixtures.resolve())
        self.process.stdin.write(json.dumps({**command, "path": str(path)}, ensure_ascii=True) + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            raise AssertionError("Native storage driver terminated unexpectedly: " + self.process.stderr.read())
        response = json.loads(line)
        response.pop("message", None)
        return response

    def case(self, name: str, raw: bytes | None, commands: list[dict], group="differential"):
        self.cases += 1
        self.names.append(name)
        directory = self.fixtures / f"{self.cases:04d}-{name}" / "Káťa 猫 🚀"
        paths = [directory / side / "data.json" for side in ("python", "native")]
        for path in paths:
            if raw is not None:
                path.parent.mkdir(parents=True)
                path.write_bytes(raw)
        for index, command in enumerate(commands):
            expected = response_python(paths[0], command)
            observed = self.native(paths[1], command)
            self.operations += 1
            self.counts[group] = self.counts.get(group, 0) + 1
            if observed != expected:
                raise AssertionError(f"{name}[{index}]: {command!r}: expected {expected!r}, observed {observed!r}")
            # Exact serialized bytes establish schema migration, canonical order,
            # ASCII escapes, other-save retention and invalid-file preservation.
            native_bytes = paths[1].read_bytes() if paths[1].is_file() else None
            python_bytes = paths[0].read_bytes() if paths[0].is_file() else None
            if native_bytes != python_bytes:
                raise AssertionError(f"{name}[{index}]: resulting document bytes differ")
            if paths[1].parent.exists() != paths[0].parent.exists():
                raise AssertionError(f"{name}[{index}]: unexpected directory creation")
            if paths[1].parent.exists() and list(paths[1].parent.glob("*.tmp")):
                raise AssertionError(f"{name}[{index}]: orphaned native temporary file")
        return paths

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            self.process.wait(timeout=10)
        stderr = self.process.stderr.read()
        if self.process.returncode != 0 or stderr:
            raise AssertionError(f"Native driver exit {self.process.returncode}: {stderr}")


def encoded(value) -> bytes:
    return json.dumps(value, ensure_ascii=True).encode("utf-8")


def exercise(h: Harness):
    defaults = Settings.defaults()
    load = {"op": "settings_load"}
    save = {"op": "settings_save", "value": defaults}
    h.case("fresh-defaults", None, [load, {"op": "settings_enabled"}])
    h.case("fresh-write", None, [save, load, {"op": "settings_set_enabled", "value": False}, load])
    for schema in (1, 2, 3, 4):
        for enabled in (False, True):
            document = {"schema": schema, "enabled": enabled}
            if schema >= 2:
                document.update(locations=[14, 2], selection_mode="random")
            if schema >= 3:
                document["prefer_same_biome"] = False
            if schema >= 4:
                document["rotate_companions"] = True
            h.case(f"schema-{schema}-{enabled}", encoded(document), [
                load, {"op": "settings_set_enabled", "value": not enabled}, load,
            ], "legacy_and_current_migration")
    for index, (enabled, prefer, rotate, mode, mask) in enumerate(itertools.product(
        (False, True), (False, True), (False, True), ("last_manual", "random", "by_habitat"), range(8),
    )):
        preferences = {
            "enabled": enabled, "prefer_same_biome": prefer, "rotate_companions": rotate,
            "selection_mode": mode, "locations": [x for i, x in enumerate((14, 3, 2)) if mask & (1 << i)],
        }
        h.case(f"settings-matrix-{index:03d}", None, [
            {"op": "settings_save", "value": preferences}, load,
        ], "settings_matrix")
    valid = {"schema": 4, **defaults}
    invalid_documents = [[], None, 1, True, {}, {"schema": True}, {"schema": 4.0, **defaults},
                         {"schema": 5, **defaults}, {**valid, "unexpected": 1},
                         {"schema": 1, "enabled": True, "locations": []},
                         {"schema": 2, "enabled": True, "locations": [], "selection_mode": "by_habitat"},
                         {"schema": 3, "enabled": True, "locations": [], "selection_mode": "by_habitat", "prefer_same_biome": True}]
    for key in defaults:
        for wrong in (None, {}, [], "yes", 1, 1.0, True):
            if type(wrong) is type(defaults[key]):
                continue
            invalid_documents.append({**valid, key: wrong})
        missing = dict(valid)
        del missing[key]
        invalid_documents.append(missing)
    for locations in ([2, 2], [1], [2.0], [True], [2, 3, 14, 0], [2**65]):
        invalid_documents.append({**valid, "locations": locations})
    invalid_documents.extend([{**valid, "selection_mode": "shuffle"}, {**valid, "schema": 2**65}])
    for index, document in enumerate(invalid_documents):
        h.case(f"invalid-settings-{index:03d}", encoded(document), [load, save], "invalid_existing_retained")
    for index, raw in enumerate([
        b"", b"{", b"\xff", b"\xef\xbb\xbf" + encoded(valid),
        b'{"schema":1,"enabled":true,"enabled":false}',
        b'{"schema":1,"schema":1,"enabled":true}',
        b'{"schema":1,"enabled":true,"\\u0065nabled":false}',
        b'{"schema":1,"enabled":NaN}',
        encoded(valid) + b" trailing", b"[" * 2000 + b"]" * 2000,
    ]):
        h.case(f"malformed-settings-{index:02d}", raw, [load, save], "invalid_existing_retained")
    for limit_delta in (-1, 0, 1):
        raw = encoded(valid)
        raw += b" " * (4096 + limit_delta - len(raw))
        h.case(f"settings-byte-limit-{limit_delta}", raw, [load, save], "byte_limits")
    for index, preferences in enumerate([
        {}, {**defaults, "enabled": 1}, {**defaults, "rotate_companions": 0},
        {**defaults, "locations": [2, 2]}, {**defaults, "locations": [2.0]},
        {**defaults, "locations": [True]}, {**defaults, "selection_mode": "unknown"},
    ]):
        h.case(f"invalid-preferences-{index:02d}", None, [{"op": "settings_save", "value": preferences}], "invalid_arguments")

    key = "nms:0123456789abcdef"
    seed = bytes(range(16)).hex()
    remember = {"op": "selection_remember", "key": key, "seed": seed, "slot": 29}
    selection_load = {"op": "selection_load", "key": key}
    forget = {"op": "selection_forget", "key": key}
    h.case("missing-favorite", None, [selection_load, forget, selection_load])
    h.case("favorite-lifecycle", None, [
        remember, selection_load,
        {**remember, "key": "second", "slot": 0, "seed": "ff" * 16},
        {**remember, "slot": 8}, selection_load, forget, selection_load,
        {**selection_load, "key": "second"}, {**forget, "key": "second"},
    ], "favorite_lifecycle")
    for index, unicode_key in enumerate(["猫", "Káťa", "🚀", "a\0b", "\r\n\t", "猫" * 256, "🚀" * 256]):
        h.case(f"unicode-save-key-{index}", None, [
            {**remember, "key": unicode_key}, {**selection_load, "key": unicode_key}, {**forget, "key": unicode_key},
        ], "unicode_paths_and_keys")
    for index, invalid_key in enumerate(["", "a" * 257, "猫" * 257, "🚀" * 257]):
        h.case(f"invalid-save-key-{index}", None, [
            {**remember, "key": invalid_key}, {**selection_load, "key": invalid_key}, {**forget, "key": invalid_key},
        ], "invalid_arguments")
    for slot in (-1, 30, True, 1.0):
        h.case(f"invalid-slot-{slot}", None, [{**remember, "slot": slot}], "invalid_arguments")
    favorite = {"seed": seed, "slot": 2}
    state = {"schema": 1, "selections": {key: favorite}}
    invalid_states = [None, [], {}, {"schema": 1}, {"schema": True, "selections": {}},
                      {"schema": 1.0, "selections": {}}, {**state, "extra": True},
                      {"schema": 2, "selections": {}}, {"schema": 1, "selections": []}]
    for invalid_favorite in (None, [], {}, {**favorite, "slot": True}, {**favorite, "slot": 2.0},
                             {**favorite, "slot": -1}, {**favorite, "slot": 30}, {**favorite, "slot": 2**65},
                             {**favorite, "seed": seed.upper()}, {**favorite, "seed": "aa" * 15},
                             {**favorite, "seed": "zz" * 16}, {**favorite, "seed": 1}, {**favorite, "extra": 1}):
        invalid_states.append({"schema": 1, "selections": {key: invalid_favorite}})
    for invalid_key in ("", "猫" * 257, "🚀" * 257):
        invalid_states.append({"schema": 1, "selections": {invalid_key: favorite}})
    invalid_states.append({"schema": 1, "selections": {str(i): favorite for i in range(257)}})
    for index, document in enumerate(invalid_states):
        h.case(f"invalid-favorite-state-{index:02d}", encoded(document), [selection_load, remember, forget], "invalid_existing_retained")
    for index, raw in enumerate([
        b"", b"{", b"\xff", b"\xef\xbb\xbf" + encoded(state),
        b'{"schema":1,"selections":{},"selections":{}}',
        b'{"schema":1,"selections":{"a":{"seed":"' + seed.encode() + b'","slot":1,"slot":2}}}',
        b'{"schema":1,"selections":{"a":{},"\\u0061":{}}}',
    ]):
        h.case(f"malformed-favorite-{index:02d}", raw, [selection_load, remember, forget], "invalid_existing_retained")
    full = {"schema": 1, "selections": {str(i): favorite for i in range(256)}}
    h.case("favorite-entry-limit", encoded(full), [
        {**selection_load, "key": "0"}, remember, {**remember, "key": "0"},
        {**forget, "key": "1"}, remember, selection_load,
    ], "entry_limit_and_preservation")
    for limit_delta in (-1, 0, 1):
        raw = encoded(state)
        raw += b" " * (1024 * 1024 + limit_delta - len(raw))
        h.case(f"favorite-byte-limit-{limit_delta}", raw, [selection_load, remember], "byte_limits")
    # Existing files are reread per operation, not retained in an object cache.
    paths = h.case("reread-before-write", None, [save])
    for path in paths:
        path.write_bytes(b'{"schema":1,"enabled":false}')
    command = {"op": "settings_set_enabled", "value": True}
    expected = response_python(paths[0], command)
    observed = h.native(paths[1], command)
    assert expected == observed and paths[0].read_bytes() == paths[1].read_bytes()
    h.operations += 1
    h.counts["reread_before_write"] = 1

    # Windows denies replacement of a destination held without FILE_SHARE_DELETE.
    # Both implementations must report failure, retain it and remove their temp.
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                                      wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        paths = h.case("locked-existing-destination", encoded(valid), [load])
        handles = [kernel.CreateFileW(str(path), 0x80000000, 1, None, 3, 0x80, None) for path in paths]
        assert all(handle != ctypes.c_void_p(-1).value for handle in handles)
        try:
            command = {"op": "settings_set_enabled", "value": False}
            expected = response_python(paths[0], command)
            observed = h.native(paths[1], command)
            assert expected == observed == {"ok": False, "error": "storage"}
            assert all(path.read_bytes() == encoded(valid) for path in paths)
            assert not list(paths[1].parent.glob("*.tmp"))
            h.operations += 1
            h.counts["locked_file_retained"] = 1
        finally:
            for handle in handles:
                kernel.CloseHandle(handle)

    # Intentional safe boundary: Python accepts escaped lone surrogate keys in
    # JSON; native storage requires Unicode scalar values and rejects them. Real
    # runtime identities are ASCII nms:<16 hex>. No such file is overwritten.
    lone_surrogate = b'{"schema":1,"selections":{"\\ud800":{"seed":"' + seed.encode() + b'","slot":0}}}'
    path = h.fixtures / "strict-unicode" / "native.json"
    path.parent.mkdir()
    path.write_bytes(lone_surrogate)
    assert h.native(path, remember) == {"ok": False, "error": "storage"}
    assert path.read_bytes() == lone_surrogate
    h.counts["intentional_lone_surrogate_rejection"] = 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    driver = args.driver.resolve(strict=True)
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    fixtures = Path(tempfile.mkdtemp(prefix="native-storage-", dir=build))
    assert fixtures.resolve().is_relative_to(build.resolve())
    harness = Harness(driver, fixtures)
    try:
        exercise(harness)
    finally:
        harness.close()
    report = {
        "status": "passed", "checked_utc": datetime.now(timezone.utc).isoformat(),
        "differential_cases": harness.cases, "differential_operations": harness.operations,
        "checks_by_group": harness.counts, "fixture_directory": str(fixtures),
        "driver": {"path": str(driver), "sha256": sha256(driver)},
        "source_sha256": {name: sha256(ROOT / name) for name in (*SOURCES, "tools/validate_native_storage.py")},
        "scope": "Fresh build-directory fixtures only; no game process, save or installed mod access",
        "strict_boundary": "Escaped lone-surrogate JSON keys are rejected without writes; valid Unicode scalar keys up to 256 characters match Python",
        "write_contract": "Single writer; flushed temporary, destination reread, atomic Windows replacement; no multi-process transaction guarantee",
        "cases": harness.names,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "differential_cases", "differential_operations", "checks_by_group")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
