"""Inspect the disabled submenu trial with real pyMHF; never register hooks."""

import ctypes as C
import hashlib
from importlib.metadata import version
import importlib.util
import inspect
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock, patch


def check():
    root = Path(__file__).resolve().parents[1]
    paths = [root / "tools" / name for name in (
        "quick_menu_submenu_trial.py", "quick_menu_submenu.py", "quick_menu_item.py",
        "quick_menu_native_guard.py", "quick_menu_guard_runtime.py",
    )]
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    if version("pymhf") != "0.2.4":
        raise RuntimeError("Use the supported pyMHF environment")
    with tempfile.TemporaryDirectory(prefix="cas-submenu-metadata-") as temporary:
        with patch.dict(os.environ, {"PYTEST_VERSION": "cas-submenu-metadata", "LOCALAPPDATA": temporary}):
            from pymhf.core import _internal
    import quick_menu_guard_runtime
    if _internal.IS_INJECTED:
        raise RuntimeError("Run this metadata check outside the game")
    with patch.object(quick_menu_guard_runtime, "ensure_guard", side_effect=AssertionError("No hook installation")):
        spec = importlib.util.spec_from_file_location("cas_submenu_framework_check", paths[0])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        classes = [value for _, value in inspect.getmembers(module, inspect.isclass)
                   if value is not module.Mod and issubclass(value, module.Mod)]
        if len(classes) != 1 or classes[0].__name__ != "CompanionMenuSubmenuTrial":
            raise RuntimeError("Unexpected submenu Mod class discovery")
        cls = classes[0]
        if module.TRIAL_ENABLED or not cls._disabled:
            raise RuntimeError("Submenu source must remain disabled")
        with patch.object(module, "current_process_io", side_effect=AssertionError("No game I/O")), \
                patch.object(module, "native_adapters", side_effect=AssertionError("No native game calls")):
            instance = cls()
        if not instance._abc_initialised or not instance._stopped or instance._guard is not None:
            raise RuntimeError("Disabled submenu initialization is not inert")
        expected = {(0x151ED00, "AFTER"), (0x1523220, "AFTER"),
                    (0x1526940, "BEFORE"), (0x1526940, "AFTER")}
        hooks = instance.hooks
        if len(hooks) != 4 or {(h._hook_offset, h._hook_time.name) for h in hooks} != expected:
            raise RuntimeError("Unexpected submenu callback metadata")
        for hook in hooks:
            trigger = hook._hook_offset == 0x1526940
            result_type = C.c_bool if trigger else None
            arg_types = [C.c_void_p, C.c_void_p] + ([C.c_bool] if trigger else [])
            if hook._noop or hook._hook_func_def.restype is not result_type:
                raise RuntimeError("Native execution/return contract differs")
            if hook._hook_func_def.argtypes != arg_types:
                raise RuntimeError("Submenu ABI differs from exact-build audit")
            wants_result = trigger and hook._hook_time.name == "AFTER"
            if bool(hook._has__result_) != wants_result:
                raise RuntimeError("Trigger result must be supplied only to its AFTER callback")
        if instance._gui_widgets or instance._hotkey_funcs:
            raise RuntimeError("Submenu trial must not register a GUI or physical hotkey")
        # Exercise pyMHF's Python dispatcher body with our real callbacks and
        # mock originals. No FuncHook object or native trampoline is created.
        from pymhf.core.hooking import FuncHook
        arguments = (0x123000, 0x456000, True)
        for original_result, candidate in ((False, False), (True, False), (False, True)):
            instance._stopped = False
            instance._thread = None
            instance._pending = None
            instance._reader = Mock(return_value=b"\0")
            instance._write_checked = Mock()
            instance._select_checked = Mock()
            original = Mock(return_value=original_result)
            dispatch = SimpleNamespace(
                _before_detours=[instance.before_trigger], _has_noop=False,
                _after_detours=[], _after_detours_with_results=[instance.after_trigger],
                _disabled_detours=set(), original=original,
            )
            with patch.object(module.submenu, "capture_activation", return_value=object() if candidate else None), \
                    patch.object(module.submenu, "validate_activation", return_value=True):
                returned = FuncHook._compound_detour(dispatch, *arguments)
            original.assert_called_once_with(*arguments)
            if returned is not original_result or dispatch._disabled_detours or instance._stopped:
                raise RuntimeError("Paired callbacks changed native execution or Boolean result")
            if instance._pending is not None:
                raise RuntimeError("Completed callback retained an activation record")
            if candidate:
                instance._write_checked.assert_called_once_with(arguments[0], module.item.DEPTH_OFFSET, 2)
                instance._select_checked.assert_called_once_with(arguments[0])
            else:
                instance._reader.assert_not_called()
                instance._write_checked.assert_not_called()
                instance._select_checked.assert_not_called()
    if any(hashlib.sha256(path.read_bytes()).hexdigest() != hashes[path.name] for path in paths):
        raise RuntimeError("Submenu sources changed during metadata check")
    result = {"source_sha256": hashes, "framework": "0.2.4", "disabled": True,
              "mod_initialized": True, "callbacks_discovered_not_registered": 4,
              "native_function_targets": 3, "guard_installed": False,
              "mock_original_dispatch_cases": 3, "game_accessed": False, "live_verified": False}
    report = root / "build/validation/menu-submenu-framework.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(check()))
