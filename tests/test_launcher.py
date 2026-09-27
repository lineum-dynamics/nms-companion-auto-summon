"""Offline host-launch tests: fake DLL loader, module list and pyMHF entrypoint."""

import builtins
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


SOURCE_PATH = Path(__file__).resolve().parents[1] / "Launch-CompanionAutoSummon.py"
spec = importlib.util.spec_from_file_location("companion_auto_summon_launcher_under_test", SOURCE_PATH)
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="companion_auto_summon-launcher-test-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.dll = self.root / "runtime" / "injector.pyd"
        self.dll.parent.mkdir()
        self.dll.write_bytes(b"test-owned placeholder, never loaded")
        self.expected = os.path.normcase(os.path.realpath(str(self.dll)))
        self.remote_base = 0x7FFDA1200000
        self.module = SimpleNamespace(filename=str(self.dll), lpBaseOfDll=self.remote_base)
        self.api = SimpleNamespace(
            inject_dll_from_path=Mock(return_value=0x7FFC55000000),
            enum_process_module=Mock(return_value=[self.module]),
        )

    def install(self):
        original = self.api.inject_dll_from_path
        guarded = launcher.install_injection_guard(self.api)
        return original, guarded

    def test_module_import_has_no_framework_or_process_import(self):
        real_import = builtins.__import__
        def checked_import(name, *args, **kwargs):
            if name.startswith(("pymem", "pymhf", "pyrun_injected")):
                self.fail(f"Unexpected runtime import: {name}")
            return real_import(name, *args, **kwargs)
        with patch.object(builtins, "__import__", side_effect=checked_import):
            exec(compile(SOURCE_PATH.read_text(encoding="utf-8"), str(SOURCE_PATH), "exec"),
                 {"__name__": "offline_import"})

    def test_returns_actual_remote_base_instead_of_local_base(self):
        original, guarded = self.install()
        self.assertEqual(guarded(123, str(self.dll)), self.remote_base)
        original.assert_called_once_with(123, self.expected)
        self.api.enum_process_module.assert_called_once_with(123)

    def test_canonical_path_is_passed_to_loader(self):
        original, guarded = self.install()
        alias = str(self.dll.parent / ".." / "runtime" / self.dll.name)
        self.assertEqual(guarded(123, alias), self.remote_base)
        original.assert_called_once_with(123, self.expected)

    def test_virtual_alias_resolves_before_injecting_and_matching(self):
        original, guarded = self.install()
        alias = str(self.root / "virtual-runtime" / self.dll.name)
        realpath = launcher.os.path.realpath
        def resolve(path, **kwargs):
            return str(self.dll) if path == alias else realpath(path, **kwargs)
        with patch.object(launcher.os.path, "realpath", side_effect=resolve):
            self.assertEqual(guarded(123, alias), self.remote_base)
        original.assert_called_once_with(123, self.expected)

    def test_missing_target_module_rejects_even_if_original_reports_success(self):
        self.api.enum_process_module.return_value = []
        _, guarded = self.install()
        with self.assertRaises(launcher.InjectionGuardError):
            guarded(123, str(self.dll))

    def test_same_basename_in_different_directory_is_rejected(self):
        other = self.root / "other" / self.dll.name
        other.parent.mkdir()
        other.write_bytes(b"different test-owned file")
        self.module.filename = str(other)
        _, guarded = self.install()
        with self.assertRaises(launcher.InjectionGuardError):
            guarded(123, str(self.dll))

    def test_ambiguous_full_path_matches_rejected(self):
        self.api.enum_process_module.return_value = [self.module, self.module]
        _, guarded = self.install()
        with self.assertRaises(launcher.InjectionGuardError):
            guarded(123, str(self.dll))

    def test_invalid_remote_bases_rejected(self):
        _, guarded = self.install()
        for base in (None, False, True, 0, -1, 0x1170, 0x10001, 1 << 47, "0x10000"):
            with self.subTest(base=base):
                self.module.lpBaseOfDll = base
                with self.assertRaises(launcher.InjectionGuardError):
                    guarded(123, str(self.dll))

    def test_null_original_return_does_not_replace_verified_remote_base(self):
        self.api.inject_dll_from_path.return_value = None
        _, guarded = self.install()
        self.assertEqual(guarded(123, str(self.dll)), self.remote_base)

    def test_enumeration_exception_fails_closed(self):
        self.api.enum_process_module.side_effect = OSError("test enumeration failure")
        _, guarded = self.install()
        with self.assertRaises(launcher.InjectionGuardError):
            guarded(123, str(self.dll))

    def test_lazy_enumeration_failure_after_match_is_not_ignored(self):
        def modules():
            yield self.module
            raise OSError("test truncated module list")
        self.api.enum_process_module.return_value = modules()
        _, guarded = self.install()
        with self.assertRaises(launcher.InjectionGuardError):
            guarded(123, str(self.dll))

    def test_unreadable_module_filename_fails_closed(self):
        self.module.filename = ""
        _, guarded = self.install()
        with self.assertRaises(launcher.InjectionGuardError):
            guarded(123, str(self.dll))

    def test_bad_source_path_rejected_before_original_loader(self):
        original, guarded = self.install()
        for path in ("", "relative.pyd", str(self.root / "missing.pyd"), None):
            with self.subTest(path=path):
                with self.assertRaises(launcher.InjectionGuardError):
                    guarded(123, path)
        original.assert_not_called()
        self.api.enum_process_module.assert_not_called()

    def test_original_loader_failure_is_propagated_without_enumeration(self):
        self.api.inject_dll_from_path.side_effect = OSError("test injection failure")
        _, guarded = self.install()
        with self.assertRaises(OSError):
            guarded(123, str(self.dll))
        self.api.enum_process_module.assert_not_called()

    def test_installing_twice_does_not_nest_wrappers(self):
        original, guarded = self.install()
        self.assertIs(launcher.install_injection_guard(self.api), guarded)
        guarded(123, str(self.dll))
        original.assert_called_once()

    def test_main_installs_guard_before_public_entrypoint_and_restores_argv(self):
        mod = self.root / "CompanionAutoSummon.py"
        mod.write_text("# Test fixture; never executed.\n", encoding="utf-8")
        events = []
        previous = sys.argv
        def fake_run():
            events.append("run")
            self.assertEqual(sys.argv, ["pymhf", "run", os.path.realpath(str(mod))])
            return 42
        fake_pymhf = SimpleNamespace(run=fake_run)
        with patch.object(launcher, "install_injection_guard", side_effect=lambda: events.append("guard")), \
             patch.dict(sys.modules, {"pymhf": fake_pymhf}):
            self.assertEqual(launcher.main([str(mod)]), 42)
        self.assertEqual(events, ["guard", "run"])
        self.assertIs(sys.argv, previous)

    def test_main_restores_argv_when_public_entrypoint_raises(self):
        mod = self.root / "CompanionAutoSummon.py"
        mod.write_bytes(b"# Test fixture")
        previous = sys.argv
        fake_pymhf = SimpleNamespace(run=Mock(side_effect=RuntimeError("test")))
        with patch.object(launcher, "install_injection_guard"), \
             patch.dict(sys.modules, {"pymhf": fake_pymhf}):
            with self.assertRaises(RuntimeError):
                launcher.main([str(mod)])
        self.assertIs(sys.argv, previous)

    def test_main_rejects_relative_or_other_file_before_guard(self):
        other = self.root / "Other.py"
        other.write_bytes(b"# Test fixture")
        with patch.object(launcher, "install_injection_guard") as guard, \
             patch("sys.stderr"):
            for path in ("CompanionAutoSummon.py", str(other), str(self.root)):
                with self.subTest(path=path), self.assertRaises(SystemExit):
                    launcher.main([path])
        guard.assert_not_called()


if __name__ == "__main__":
    unittest.main()
