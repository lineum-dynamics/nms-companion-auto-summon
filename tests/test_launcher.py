"""Offline host-launch tests: fake DLL loader, module list and pyMHF entrypoint."""

import builtins
import ctypes
import importlib.util
import hashlib
import json
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


class FakeMutexAPI:
    """A kernel-object lifetime model; no mutex or process is actually opened."""

    def __init__(self):
        self.error = 0
        self.next_handle = 100
        self.handles = {}
        self.events = []

    def set_last_error(self, value):
        self.error = value

    def get_last_error(self):
        return self.error

    def CreateMutexW(self, attributes, owner, name):
        self.events.append(("create", attributes, owner, name))
        self.error = 183 if name in self.handles.values() else 0
        self.next_handle += 1
        self.handles[self.next_handle] = name
        return self.next_handle

    def CloseHandle(self, handle):
        self.events.append(("close", handle))
        return self.handles.pop(handle, None) is not None


class LauncherSessionTests(unittest.TestCase):
    def test_single_session_uses_nonowning_stable_name_and_closes_handle(self):
        api = FakeMutexAPI()
        with launcher.launcher_session(api):
            self.assertEqual(api.events, [("create", None, False, launcher.LAUNCHER_MUTEX_NAME)])
            self.assertEqual(len(api.handles), 1)
        self.assertEqual(api.handles, {})
        self.assertEqual(api.events[-1], ("close", 101))
        self.assertEqual(launcher.LAUNCHER_MUTEX_NAME, r"Local\CompanionAutoSummon.Host.v1")

    def test_concurrent_package_refused_without_releasing_original_lease(self):
        api = FakeMutexAPI()
        # Independently imported copies still refer to one fixed kernel name.
        duplicate = {"__name__": "another_package_launcher", "__file__": str(SOURCE_PATH)}
        exec(compile(SOURCE_PATH.read_bytes(), str(SOURCE_PATH), "exec"), duplicate)
        with launcher.launcher_session(api):
            with self.assertRaisesRegex(launcher.LauncherSessionError, "already starting"):
                with launcher.launcher_session(api):
                    self.fail("A second host must not enter")
            self.assertEqual(len(api.handles), 1)
            with self.assertRaisesRegex(duplicate["LauncherSessionError"], "already starting"):
                with duplicate["launcher_session"](api):
                    self.fail("Another package must not enter")
            self.assertEqual(len(api.handles), 1)
        self.assertEqual(api.handles, {})

    def test_completed_or_crashed_host_does_not_leave_a_persistent_lock(self):
        api = FakeMutexAPI()
        with launcher.launcher_session(api):
            pass
        with launcher.launcher_session(api):
            self.assertEqual(len(api.handles), 1)
        # Model OS cleanup after an unowned process handle is closed on death.
        orphan = api.CreateMutexW(None, False, launcher.LAUNCHER_MUTEX_NAME)
        self.assertTrue(api.CloseHandle(orphan))
        with launcher.launcher_session(api):
            self.assertEqual(len(api.handles), 1)

    def test_body_exception_releases_lease(self):
        api = FakeMutexAPI()
        with self.assertRaisesRegex(RuntimeError, "body failed"):
            with launcher.launcher_session(api):
                raise RuntimeError("body failed")
        self.assertEqual(api.handles, {})

    def test_null_or_invalid_handle_refuses_without_yielding_or_closing_junk(self):
        for handle in (None, 0, False, True, -1, 1 << 64, "handle"):
            api = SimpleNamespace(set_last_error=Mock(), CreateMutexW=Mock(return_value=handle),
                                  get_last_error=Mock(return_value=0), CloseHandle=Mock())
            with self.subTest(handle=handle), self.assertRaises(launcher.LauncherSessionError):
                with launcher.launcher_session(api):
                    self.fail("An invalid handle must not enter")
            api.CloseHandle.assert_not_called()

    def test_creation_or_error_query_failure_refuses_and_closes_any_open_handle(self):
        for phase in ("set_last_error", "CreateMutexW", "get_last_error"):
            api = FakeMutexAPI()
            with patch.object(api, phase, side_effect=OSError("private OS detail")), \
                    self.assertRaises(launcher.LauncherSessionError) as caught:
                with launcher.launcher_session(api):
                    self.fail("API failure must not enter")
            self.assertNotIn("private", str(caught.exception))
            self.assertEqual(api.handles, {})

    def test_unexpected_error_code_refuses_and_cleans_valid_handle(self):
        api = FakeMutexAPI()
        with patch.object(api, "get_last_error", return_value=5), \
                self.assertRaises(launcher.LauncherSessionError):
            with launcher.launcher_session(api):
                self.fail("Unexpected error must not enter")
        self.assertEqual(api.handles, {})

    def test_cleanup_failure_is_reported(self):
        for error in (False, OSError("private close error")):
            api = FakeMutexAPI()
            replacement = (Mock(side_effect=error) if isinstance(error, Exception)
                           else Mock(return_value=error))
            with patch.object(api, "CloseHandle", replacement), \
                    self.assertRaises(launcher.LauncherSessionError) as caught:
                with launcher.launcher_session(api):
                    pass
            self.assertNotIn("private", str(caught.exception))
            replacement.assert_called_once_with(101)

    def test_kernel_binding_failure_is_lazy_and_refuses_session(self):
        with patch.object(launcher, "_launcher_mutex_api", side_effect=OSError("private binding")), \
                self.assertRaises(launcher.LauncherSessionError):
            with launcher.launcher_session():
                self.fail("Unavailable Windows API must not enter")

    def test_windows_bindings_preserve_pointer_width_without_calling_api(self):
        kernel = SimpleNamespace(CreateMutexW=Mock(), CloseHandle=Mock())
        with patch.object(launcher.os, "name", "nt"), \
                patch.object(ctypes, "WinDLL", return_value=kernel, create=True) as loader, \
                patch.object(ctypes, "set_last_error", Mock(), create=True), \
                patch.object(ctypes, "get_last_error", Mock(), create=True):
            api = launcher._launcher_mutex_api()
        loader.assert_called_once_with("kernel32", use_last_error=True)
        self.assertIs(api.CreateMutexW.restype, ctypes.c_void_p)
        self.assertEqual(api.CreateMutexW.argtypes, [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p])
        self.assertEqual(api.CloseHandle.argtypes, [ctypes.c_void_p])
        self.assertIs(api.CloseHandle.restype, ctypes.c_int)
        kernel.CreateMutexW.assert_not_called()
        kernel.CloseHandle.assert_not_called()


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
        self.mutex = FakeMutexAPI()
        mutex_patch = patch.object(launcher, "_launcher_mutex_api", return_value=self.mutex)
        mutex_patch.start()
        self.addCleanup(mutex_patch.stop)
        self.verified_executable = self.root / "game/Binaries/NMS.exe"
        self.compatibility_mocks = {}
        for name, returned in (("verify_target", self.verified_executable), ("verify_game_directory", self.verified_executable),
                               ("verify_framework", True), ("game_closed", True), ("show_failure", None)):
            item = patch.object(launcher.compatibility, name, return_value=returned)
            self.compatibility_mocks[name] = item.start()
            self.addCleanup(item.stop)
        package_patch = patch.object(launcher, "validate_standalone_package", return_value=True)
        self.package_check = package_patch.start()
        self.addCleanup(package_patch.stop)

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
                 {"__name__": "offline_import", "__file__": str(SOURCE_PATH)})

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
            self.assertEqual(len(self.mutex.handles), 1)
            return 42
        fake_pymhf = SimpleNamespace(run=fake_run)
        with patch.object(launcher, "install_injection_guard", side_effect=lambda **kwargs: events.append("guard")), \
             patch.dict(sys.modules, {"pymhf": fake_pymhf}):
            self.assertEqual(launcher.main([str(mod)]), 42)
        self.assertEqual(events, ["guard", "run"])
        self.assertIs(sys.argv, previous)
        self.assertEqual(self.mutex.handles, {})

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
        self.assertEqual(self.mutex.handles, {})

    def test_duplicate_main_refuses_before_guard_framework_import_or_run(self):
        mod = self.root / "CompanionAutoSummon.py"
        mod.write_bytes(b"# Test fixture")
        real_import = builtins.__import__
        def no_framework(name, *args, **kwargs):
            if name.startswith(("pymhf", "pymem")):
                self.fail("Duplicate host must not import a framework")
            return real_import(name, *args, **kwargs)
        with launcher.launcher_session(self.mutex), \
                patch.object(launcher, "install_injection_guard") as guard, \
                patch.object(builtins, "__import__", side_effect=no_framework), \
                self.assertRaisesRegex(launcher.LauncherSessionError, "already starting"):
            launcher.main([str(mod)])
        guard.assert_not_called()
        self.assertEqual(self.mutex.handles, {})

    def test_guard_failure_releases_session_without_framework_run(self):
        mod = self.root / "CompanionAutoSummon.py"
        mod.write_bytes(b"# Test fixture")
        fake_pymhf = SimpleNamespace(run=Mock())
        with patch.object(launcher, "install_injection_guard", side_effect=launcher.InjectionGuardError("test")), \
                patch.dict(sys.modules, {"pymhf": fake_pymhf}), \
                self.assertRaises(launcher.InjectionGuardError):
            launcher.main([str(mod)])
        fake_pymhf.run.assert_not_called()
        self.assertEqual(self.mutex.handles, {})

    def test_main_rejects_relative_or_other_file_before_guard(self):
        other = self.root / "Other.py"
        other.write_bytes(b"# Test fixture")
        with patch.object(launcher, "install_injection_guard") as guard, \
             patch("sys.stderr"):
            for path in ("CompanionAutoSummon.py", str(other), str(self.root)):
                with self.subTest(path=path), self.assertRaises(SystemExit):
                    launcher.main([path])
        guard.assert_not_called()

    def test_actual_target_is_verified_before_every_dll_load(self):
        events = []
        self.compatibility_mocks["verify_target"].side_effect = lambda *a, **kw: events.append("verify")
        self.api.inject_dll_from_path.side_effect = lambda *a: events.append("inject")
        _, guarded = self.install()
        guarded(123, str(self.dll))
        guarded(123, str(self.dll))
        self.assertEqual(events, ["verify", "inject", "verify", "inject"])

    def test_target_refusal_prevents_first_and_second_injection(self):
        original, guarded = self.install()
        checker = self.compatibility_mocks["verify_target"]
        checker.side_effect = launcher.compatibility.CompatibilityError("launcher.unsupported_game")
        with self.assertRaises(launcher.compatibility.CompatibilityError):
            guarded(123, str(self.dll))
        original.assert_not_called()
        self.api.enum_process_module.assert_not_called()
        checker.side_effect = [self.verified_executable,
                               launcher.compatibility.CompatibilityError("launcher.game_changed")]
        guarded(123, str(self.dll))
        with self.assertRaises(launcher.compatibility.CompatibilityError):
            guarded(123, str(self.dll))
        self.assertEqual(original.call_count, 1)

    def test_wrapper_cannot_silently_reuse_a_different_selected_game(self):
        launcher.install_injection_guard(self.api, expected_executable=self.verified_executable)
        with self.assertRaises(launcher.compatibility.CompatibilityError):
            launcher.install_injection_guard(self.api, expected_executable=self.root / "other.exe")

    def test_preflight_failure_reports_without_lease_framework_or_injection(self):
        mod = self.root / "CompanionAutoSummon.py"
        mod.write_bytes(b"# owned fixture")
        for method, key in (("verify_game_directory", "launcher.unsupported_game"),
                            ("verify_framework", "launcher.wrong_framework")):
            mock = self.compatibility_mocks[method]
            failure = launcher.compatibility.CompatibilityError(key)
            mock.side_effect = failure
            with patch.object(launcher, "install_injection_guard") as guard:
                self.assertEqual(launcher.main([str(mod), "--language", "fr", "--no-dialog"]), 1)
                guard.assert_not_called()
            self.compatibility_mocks["show_failure"].assert_called_with(failure, language="fr", show_dialog=False)
            self.assertEqual(self.mutex.events, [])
            mock.side_effect = None

    def test_missing_mod_path_reports_without_reading_game_or_starting_host(self):
        with patch.object(launcher, "install_injection_guard") as guard:
            self.assertEqual(launcher.main([str(self.root / "missing/CompanionAutoSummon.py"), "--no-dialog"]), 1)
            guard.assert_not_called()
        self.compatibility_mocks["verify_game_directory"].assert_not_called()
        failure = self.compatibility_mocks["show_failure"].call_args.args[0]
        self.assertEqual(failure.key, "launcher.invalid_package")
        self.assertEqual(self.mutex.events, [])

    def test_check_only_skips_lease_process_probe_and_framework_entry(self):
        mod = self.root / "CompanionAutoSummon.py"
        mod.write_bytes(b"# owned fixture")
        with patch.object(launcher, "install_injection_guard") as guard, patch("sys.stdout"):
            self.assertEqual(launcher.main([str(mod), "--check-only"]), 0)
            guard.assert_not_called()
        self.compatibility_mocks["game_closed"].assert_not_called()
        self.assertEqual(self.mutex.events, [])

    def test_final_gate_refusal_returns_failure_and_releases_host(self):
        mod = self.root / "CompanionAutoSummon.py"
        mod.write_bytes(b"# owned fixture")
        failure = launcher.compatibility.CompatibilityError("launcher.game_changed")
        fake = SimpleNamespace(run=Mock(side_effect=failure))
        previous = sys.argv
        with patch.object(launcher, "install_injection_guard") as guard, patch.dict(sys.modules, {"pymhf": fake}):
            self.assertEqual(launcher.main([str(mod), "--no-dialog"]), 1)
            guard.assert_called_once_with(expected_executable=self.verified_executable)
        self.assertIs(sys.argv, previous)
        self.assertEqual(self.mutex.handles, {})
        self.compatibility_mocks["show_failure"].assert_called_once_with(failure, language=None, show_dialog=False)


class StandalonePackageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.mod = self.root / "CompanionAutoSummon.py"
        self.mod.write_bytes((SOURCE_PATH.parent / "CompanionAutoSummon.py").read_bytes())
        for name in (SOURCE_PATH.name, "cas_compatibility.py"):
            (self.root / name).write_bytes(b"# owned inert fixture")
        (self.root / "compatibility.json").write_text(json.dumps(launcher.compatibility.PROFILE), encoding="utf-8")
        host_patch = patch.object(launcher, "__file__", str(self.root / SOURCE_PATH.name))
        host_patch.start()
        self.addCleanup(host_patch.stop)
        self.rehash()

    def rehash(self):
        self.manifest = {"steam_build": launcher.compatibility.STEAM_BUILD,
                         "supported_nms_exe_sha256": launcher.compatibility.SUPPORTED_GAME_SHA256,
                         "framework": "pymhf[gui]==0.2.4",
                         "files": [{"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                                   for p in self.root.iterdir() if p.name != "manifest.json"]}
        self.save_manifest()

    def save_manifest(self):
        (self.root / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def test_owned_complete_package_validates_without_executing_it(self):
        self.assertEqual(launcher.validate_standalone_package(self.mod), self.mod.resolve())

    def test_bad_sibling_and_duplicate_records_refused(self):
        for name in ("cas_compatibility.py", SOURCE_PATH.name, "CompanionAutoSummon.py"):
            target = self.root / name
            saved = target.read_bytes()
            target.write_bytes(saved + b"# changed")
            with self.subTest(name=name), self.assertRaises(launcher.compatibility.CompatibilityError):
                launcher.validate_standalone_package(self.mod)
            target.write_bytes(saved)
        self.manifest["files"].append(self.manifest["files"][0])
        self.save_manifest()
        with self.assertRaises(launcher.compatibility.CompatibilityError):
            launcher.validate_standalone_package(self.mod)

    def test_matching_hash_does_not_allow_paused_or_foreign_game_configuration(self):
        original = self.mod.read_bytes()
        for old, replacement in ((b"start_paused = false", b"start_paused = true"),
                                  (b"steam_gameid = 275850", b"steam_gameid = 42"),
                                  (b'exe = "NMS.exe"', b'exe = "Other.exe"'),
                                  (b"interactive_console = false", b'interactive_console = false\n# required_assemblies = ["foreign.dll"]')):
            self.mod.write_bytes(original.replace(old, replacement, 1))
            self.rehash()
            with self.subTest(old=old), self.assertRaises(launcher.compatibility.CompatibilityError):
                launcher.validate_standalone_package(self.mod)

    def test_inconsistent_profile_refused_even_with_updated_file_checksum(self):
        profile = dict(launcher.compatibility.PROFILE, exe_sha256="0" * 64)
        (self.root / "compatibility.json").write_text(json.dumps(profile), encoding="utf-8")
        self.rehash()
        with self.assertRaises(launcher.compatibility.CompatibilityError):
            launcher.validate_standalone_package(self.mod)


if __name__ == "__main__":
    unittest.main()
