"""Inspect a disabled diagnostic with real pyMHF, without registering hooks.

The optional Windows reader check copies only buffers allocated by this script.
It never finds, opens, launches or attaches to a game process.
"""

import argparse
import ctypes
import hashlib
import importlib.util
from importlib.metadata import version
import inspect
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

from build_quick_menu_probe import ROOT, STAGES


def check(stage):
    profile = STAGES[stage]
    source = ROOT / "tools" / profile["source"]
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if version("pymhf") != "0.2.4":
        raise RuntimeError("Use the exact supported pyMHF 0.2.4 environment")
    with tempfile.TemporaryDirectory(prefix="cas-observer-smoke-") as temporary:
        with patch.dict(os.environ, {"PYTEST_VERSION": "cas-observer-smoke", "LOCALAPPDATA": temporary}):
            from pymhf.core import _internal

            if _internal.IS_INJECTED:
                raise RuntimeError("Run this check outside the game")
            spec = importlib.util.spec_from_file_location("cas_observer_smoke", source)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            mods = [value for _, value in inspect.getmembers(module, inspect.isclass)
                    if value is not module.Mod and issubclass(value, module.Mod)]
            if len(mods) != 1 or mods[0].__name__ != profile["class"]:
                raise RuntimeError("Expected exactly one diagnostic Mod class")
            if module.PROBE_ENABLED or not mods[0]._disabled:
                raise RuntimeError("Source observer must be disabled outside the game")
            instance = mods[0]()
            expected = ({0x1526940} if stage == "actions" else {0x151ED00, 0x1523220})
            hooks = instance.hooks
            if len(hooks) != len(expected) or {hook._hook_offset for hook in hooks} != expected:
                raise RuntimeError("Unexpected diagnostic hook metadata")
            expected_time = "BEFORE" if stage == "actions" else "AFTER"
            if any(hook._hook_time.name != expected_time or hook._noop for hook in hooks):
                raise RuntimeError("Diagnostic must preserve the natural original call")
            expected_result = ctypes.c_bool if stage == "actions" else None
            expected_arguments = [ctypes.c_void_p, ctypes.c_void_p]
            if stage == "actions":
                expected_arguments.append(ctypes.c_bool)
            if any(hook._hook_func_def.restype is not expected_result
                   or hook._hook_func_def.argtypes != expected_arguments for hook in hooks):
                raise RuntimeError("Actual framework ABI metadata differs from the audited contract")
            if instance._gui_widgets or instance._hotkey_funcs:
                raise RuntimeError("Diagnostic must not expose GUI or hotkeys")
            reader = module.create_current_process_reader()
            sizes = (4,) if stage == "actions" else (4, 16, 128)
            for size in sizes:
                fixture = bytes(index % 251 for index in range(size))
                owned = ctypes.create_string_buffer(fixture, size)
                if reader(ctypes.addressof(owned), size) != fixture:
                    raise RuntimeError("Reader did not copy the test host's owned bytes")
            if list(Path(temporary).rglob("*.json")):
                raise RuntimeError("Diagnostic unexpectedly wrote preference data")
    if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
        raise RuntimeError("Observer source changed during the smoke check")
    record = {
        "stage": stage, "source_sha256": source_hash, "framework": "0.2.4",
        "disabled_outside_game": True, "hooks_discovered_not_registered": len(hooks),
        "hook_abi_metadata_verified": True,
        "hook_time": expected_time.lower(), "gui_widgets": 0, "hotkeys": 0,
        "owned_test_host_buffers_copied": list(sizes), "game_accessed": False,
        "live_verified": False,
    }
    report = ROOT / "build" / "validation" / f"menu-probe-{stage}-framework.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=STAGES, required=True)
    print(json.dumps(check(parser.parse_args().stage)))
