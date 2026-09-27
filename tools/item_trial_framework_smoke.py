"""Inspect disabled inert-item trial metadata with real pyMHF, no game hooks."""

import ctypes as C
import hashlib
from importlib.metadata import version
import importlib.util
import inspect
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch


def check():
    root = Path(__file__).resolve().parents[1]
    paths = [root / "tools" / name for name in (
        "quick_menu_item_trial.py", "quick_menu_item.py", "quick_menu_native_guard.py",
        "quick_menu_guard_runtime.py",
    )]
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    if version("pymhf") != "0.2.4":
        raise RuntimeError("Use the supported pyMHF environment")
    # pyMHF's own test-mode marker suppresses its interactive launch prompt.
    # Importing the framework for metadata must never start a game session.
    with tempfile.TemporaryDirectory(prefix="cas-item-metadata-") as temporary:
        with patch.dict(os.environ, {"PYTEST_VERSION": "cas-item-metadata", "LOCALAPPDATA": temporary}):
            from pymhf.core import _internal
    import quick_menu_guard_runtime
    if _internal.IS_INJECTED:
        raise RuntimeError("Run this metadata check outside the game")
    with patch.object(quick_menu_guard_runtime, "ensure_guard", side_effect=AssertionError("No hook installation")):
        spec = importlib.util.spec_from_file_location("cas_item_trial_framework_check", paths[0])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        classes = [value for _, value in inspect.getmembers(module, inspect.isclass)
                   if value is not module.Mod and issubclass(value, module.Mod)]
        if len(classes) != 1 or classes[0].__name__ != "CompanionMenuItemTrial":
            raise RuntimeError("Unexpected trial Mod class discovery")
        cls = classes[0]
        if module.TRIAL_ENABLED or not cls._disabled:
            raise RuntimeError("Trial source must remain disabled")
        with patch.object(module, "current_process_io", side_effect=AssertionError("No game I/O")), \
                patch.object(module, "native_adapters", side_effect=AssertionError("No native game calls")):
            instance = cls()
        if not instance._abc_initialised or not instance._stopped or instance._guard is not None:
            raise RuntimeError("Disabled trial initialization is not inert or omitted Mod initialization")
        hooks = instance.hooks
        expected = {(0x151ED00, "AFTER"), (0x1523220, "AFTER")}
        if len(hooks) != 2 or {(h._hook_offset, h._hook_time.name) for h in hooks} != expected:
            raise RuntimeError("Unexpected item-trial hook metadata")
        for hook in hooks:
            if hook._noop or hook._hook_func_def.restype is not None:
                raise RuntimeError("Trial must preserve native execution")
            if hook._hook_func_def.argtypes != [C.c_void_p, C.c_void_p]:
                raise RuntimeError("Trial ABI differs from exact-build audit")
        if instance._gui_widgets or instance._hotkey_funcs:
            raise RuntimeError("Inert trial must have no GUI or physical hotkeys")
    if any(hashlib.sha256(path.read_bytes()).hexdigest() != hashes[path.name] for path in paths):
        raise RuntimeError("Trial sources changed during metadata check")
    result = {"source_sha256": hashes, "framework": "0.2.4", "disabled": True,
              "mod_initialized": True, "callbacks_discovered_not_registered": 2,
              "guard_installed": False, "game_accessed": False, "live_verified": False}
    report = root / "build/validation/menu-inert-item-framework.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(check()))
