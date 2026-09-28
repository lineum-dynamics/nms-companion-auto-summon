"""Combined play-trial host checks; no framework execution or process access."""

import builtins
from contextlib import contextmanager
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "Launch-CompanionAutoSummon-PlayTrial.py"
SPEC = importlib.util.spec_from_file_location("play_trial_launcher_under_test", SOURCE)
LAUNCHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAUNCHER)
CONFIG = b'''[pymhf]
exe = "NMS.exe"
steam_gameid = 275850
start_paused = false
interactive_console = false
[pymhf.logging]
shown = false
log_dir = "{CURR_DIR}"
log_level = "info"
[pymhf.gui]
shown = true
always_on_top = false
'''


class PlayTrialFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cas-play-host-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.bundle = self.root / "bundle"
        self.bundle.mkdir()
        for name in LAUNCHER.PAYLOAD_FILES:
            data = b"# Owned fixture; not a loaded mod.\n"
            if name == LAUNCHER.HOST_NAME:
                data = SOURCE.read_bytes()
            elif name == LAUNCHER.BOOTSTRAP_NAME:
                data = (ROOT / name).read_bytes()
            elif name == "pymhf.toml":
                data = CONFIG
            elif name in {"cas_compatibility.py", "compatibility.json"} or name.startswith("locales/"):
                data = (ROOT / name).read_bytes()
            destination = self.bundle / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        self.manifest = {
            "version": "0.8.7-play-trial", "framework": "pymhf[gui]==0.2.4",
            "steam_build": LAUNCHER.compatibility.STEAM_BUILD,
            "supported_nms_exe_sha256": LAUNCHER.compatibility.SUPPORTED_GAME_SHA256,
            "auto_summon": True, "preference_actions": True,
            "preference_keys": ["enabled", "selection_mode", "prefer_same_biome", "locations"],
            "mods": [
                {"name": "CompanionAutoSummon", "version": "0.4.9-experimental",
                 "path": "CompanionAutoSummon.py"},
                {"name": "CompanionMenuOrderTrial", "version": "0.8.5-branding",
                 "path": "CompanionMenuOrderTrial.py"},
            ],
            "files": [{"path": name, "sha256": hashlib.sha256((self.bundle / name).read_bytes()).hexdigest()}
                      for name in sorted(LAUNCHER.PAYLOAD_FILES)],
        }
        self.save_manifest()
        self.host_patch = patch.object(LAUNCHER, "__file__", str(self.bundle / LAUNCHER.HOST_NAME))
        self.host_patch.start()
        self.addCleanup(self.host_patch.stop)
        self.events = []
        self.asset_setup = Mock(side_effect=lambda *args: self.events.append("asset"))
        self.verified_executable = self.root / "game" / "Binaries" / "NMS.exe"
        self.verify_game = Mock(return_value=self.verified_executable)
        self.failure = Mock()
        self.closed = Mock(return_value=True)
        self.bootstrap = types.SimpleNamespace(
            install_injection_guard=Mock(side_effect=lambda **kwargs: self.events.append("guard")),
            launcher_session=Mock(side_effect=self.host_lease))
        self.runtime = types.ModuleType("pymhf.main")
        self.runtime.run_module = Mock(side_effect=self.run_module)
        self.package = types.ModuleType("pymhf")
        self.package.__path__ = []
        self.entrypoints = Mock()
        self.entrypoints.select.return_value = ()

    def save_manifest(self):
        (self.bundle / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def rehash(self, name):
        for entry in self.manifest["files"]:
            if entry["path"] == name:
                entry["sha256"] = hashlib.sha256((self.bundle / name).read_bytes()).hexdigest()
        self.save_manifest()

    def run_module(self, folder, config):
        self.events.append("run")
        self.assertEqual(folder, str(self.bundle.resolve()))
        self.assertEqual(config, LAUNCHER.EXPECTED_CONFIG)
        return 42

    @contextmanager
    def host_lease(self):
        self.events.append("lease")
        try:
            yield
        finally:
            self.events.append("release")

    def main(self, argv=None, *, runtime_version="0.2.4"):
        with patch.object(LAUNCHER, "_load_bootstrap", return_value=self.bootstrap) as loader, patch.object(
            LAUNCHER.metadata, "version", return_value=runtime_version
        ), patch.object(LAUNCHER.metadata, "entry_points", return_value=self.entrypoints), patch.dict(
            sys.modules, {"pymhf": self.package, "pymhf.main": self.runtime}
        ), patch.object(LAUNCHER, "_prepare_icon_asset", self.asset_setup), \
                patch.object(LAUNCHER, "_game_closed", self.closed), \
                patch.object(LAUNCHER.compatibility, "verify_game_directory", self.verify_game), \
                patch.object(LAUNCHER.compatibility, "show_failure", self.failure):
            arguments = [str(self.bundle)] if argv is None else list(argv)
            arguments += ["--game-directory", str(self.root / "game"), "--no-dialog"]
            if "--language" not in arguments:
                arguments += ["--language", "en"]
            self.loader = loader
            result = LAUNCHER.main(arguments)
            return result

    def assert_bundle_refused(self, path=None):
        path = str(self.bundle) if path is None else path
        with self.assertRaises((LAUNCHER.BundleError, OSError, ValueError, KeyError)):
            LAUNCHER.validate_bundle(path)
        self.assertEqual(self.main([path]), 1)
        self.loader.assert_not_called()
        self.assertEqual(self.failure.call_args.args[0].key, "launcher.invalid_package")
        self.assertIs(self.failure.call_args.kwargs["show_dialog"], False)


class BundleValidationTests(PlayTrialFixture):
    def test_valid_bundle_preserves_two_mod_identities_and_global_settings_routes(self):
        bundle, config = LAUNCHER.validate_bundle(str(self.bundle))
        self.assertEqual(bundle, self.bundle.resolve())
        self.assertTrue(config["gui"]["shown"])
        self.assertEqual(len(self.manifest["files"]), 40)
        self.assertEqual({entry["name"] for entry in self.manifest["mods"]},
                         {"CompanionAutoSummon", "CompanionMenuOrderTrial"})
        self.assertFalse((self.bundle / "settings.json").exists())
        self.assertFalse((self.bundle / "state.json").exists())

    def test_relative_foreign_missing_or_file_argument_is_rejected_before_guard(self):
        other = self.root / "other"
        other.mkdir()
        for value in ("bundle", str(other), str(self.root / "absent"),
                      str(self.bundle / "CompanionAutoSummon.py")):
            with self.subTest(value=value):
                self.assert_bundle_refused(value)
        self.bootstrap.install_injection_guard.assert_not_called()
        self.runtime.run_module.assert_not_called()

    def test_path_alias_to_own_folder_is_resolved_before_framework_call(self):
        self.assertEqual(self.main([str(self.bundle / ".." / "bundle")]), 42)
        self.runtime.run_module.assert_called_once_with(str(self.bundle.resolve()), LAUNCHER.EXPECTED_CONFIG)

    def test_argument_count_errors_never_install_guard(self):
        for arguments in ([], [str(self.bundle), "unexpected"]):
            with self.subTest(arguments=arguments), patch("sys.stderr"), self.assertRaises(SystemExit):
                self.main(arguments)
        self.bootstrap.install_injection_guard.assert_not_called()

    def test_tampered_or_missing_payload_is_refused_before_bootstrap(self):
        for name in ("CompanionAutoSummon.py", "CompanionMenuOrderTrial.py", "quick_menu_order.py",
                     LAUNCHER.BOOTSTRAP_NAME, LAUNCHER.HOST_NAME, "pymhf.toml"):
            with self.subTest(name=name):
                path = self.bundle / name
                old = path.read_bytes()
                path.write_bytes(old + b"# changed\n")
                self.assert_bundle_refused()
                path.write_bytes(old)
        (self.bundle / "quick_menu_item.py").unlink()
        self.assert_bundle_refused()
        self.bootstrap.install_injection_guard.assert_not_called()
        self.runtime.run_module.assert_not_called()

    def test_wrong_manifest_semantics_are_not_accepted_as_another_trial(self):
        pristine = copy.deepcopy(self.manifest)
        for key, value in (("version", "0.8.5-branding"), ("framework", "pymhf==0.2.4"),
                           ("auto_summon", False), ("auto_summon", 1),
                           ("preference_actions", False), ("preference_keys", []),
                           ("preference_keys", ["enabled", "locations"]), ("mods", pristine["mods"][:1]),
                           ("mods", pristine["mods"] * 2)):
            with self.subTest(key=key, value=value):
                self.manifest = {**copy.deepcopy(pristine), key: value}
                self.save_manifest()
                self.assert_bundle_refused()
        self.bootstrap.install_injection_guard.assert_not_called()

    def test_missing_duplicate_traversal_and_bad_checksum_entries_are_rejected(self):
        original = copy.deepcopy(self.manifest["files"])
        for mutation in ("missing", "duplicate", "traversal", "uppercase", "not_entry"):
            with self.subTest(mutation=mutation):
                entries = copy.deepcopy(original)
                if mutation == "missing":
                    entries.pop()
                elif mutation == "duplicate":
                    entries[-1] = entries[0]
                elif mutation == "traversal":
                    entries[0]["path"] = "../CompanionAutoSummon.py"
                elif mutation == "uppercase":
                    entries[0]["sha256"] = entries[0]["sha256"].upper()
                else:
                    entries[0] = "invalid"
                self.manifest["files"] = entries
                self.save_manifest()
                self.assert_bundle_refused()
        self.bootstrap.install_injection_guard.assert_not_called()

    def test_extra_root_or_child_python_and_competing_project_are_rejected(self):
        for name in ("Other.py", "nested/Other.py", "pyproject.toml"):
            with self.subTest(name=name):
                path = self.bundle / name
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(b"# An unlisted discovery input")
                self.assert_bundle_refused()
                path.unlink()
        self.bootstrap.install_injection_guard.assert_not_called()

    def test_duplicate_python_alias_does_not_evade_exact_discovery(self):
        alias = self.bundle / "Extra.py"
        alias.write_bytes(b"# Simulated filesystem alias")
        actual_resolve = Path.resolve
        def resolve(path, *args, **kwargs):
            if path == alias:
                return actual_resolve(self.bundle / "CompanionAutoSummon.py", *args, **kwargs)
            return actual_resolve(path, *args, **kwargs)
        with patch.object(Path, "resolve", resolve):
            self.assert_bundle_refused()
        self.bootstrap.install_injection_guard.assert_not_called()

    def test_config_changes_are_rejected_even_with_matching_checksum(self):
        for content in (CONFIG.replace(b'shown = true', b'shown = false'),
                        CONFIG.replace(b'interactive_console = false', b'interactive_console = true'),
                        CONFIG + b'\n[extra]\nvalue = "unexpected"\n'):
            with self.subTest(content=content):
                (self.bundle / "pymhf.toml").write_bytes(content)
                self.rehash("pymhf.toml")
                self.assert_bundle_refused()
        self.bootstrap.install_injection_guard.assert_not_called()

    def test_profile_disagreement_is_rejected_even_with_updated_checksum(self):
        profile = dict(LAUNCHER.compatibility.PROFILE, exe_sha256="0" * 64)
        (self.bundle / "compatibility.json").write_text(json.dumps(profile), encoding="utf-8")
        self.rehash("compatibility.json")
        self.assert_bundle_refused()
        self.verify_game.assert_not_called()
        self.asset_setup.assert_not_called()


class HostRoutingTests(PlayTrialFixture):
    def test_asset_setup_failure_prevents_framework_start(self):
        self.asset_setup.side_effect = RuntimeError("owned asset setup failure")
        with self.assertRaisesRegex(RuntimeError, "owned asset setup failure"):
            self.main()
        self.bootstrap.install_injection_guard.assert_called_once()
        self.runtime.run_module.assert_not_called()
        self.assertEqual(self.events, ["lease", "guard", "release"])

    def test_existing_host_lease_stops_before_guard_assets_or_game(self):
        self.bootstrap.launcher_session.side_effect = RuntimeError("owned duplicate host")
        with self.assertRaisesRegex(RuntimeError, "owned duplicate host"):
            self.main()
        self.bootstrap.install_injection_guard.assert_not_called()
        self.asset_setup.assert_not_called()
        self.runtime.run_module.assert_not_called()
        self.assertEqual(self.events, [])

    def test_framework_failure_releases_host_lease(self):
        self.runtime.run_module.side_effect = RuntimeError("owned framework failure")
        with self.assertRaisesRegex(RuntimeError, "owned framework failure"):
            self.main()
        self.assertEqual(self.events, ["lease", "guard", "asset", "release"])

    def test_closed_probe_refuses_unknown_names_or_enumeration_failure(self):
        with patch.object(LAUNCHER, "_windows_process_names") as names:
            for name, expected in (("NMS.exe", False), (None, False), ("", False), ("other.exe", True)):
                with self.subTest(name=name):
                    names.return_value = [name]
                    self.assertIs(LAUNCHER._game_closed(), expected)
            names.return_value = ["Secure System", "python.exe"]
            self.assertTrue(LAUNCHER._game_closed())
            names.return_value = []
            self.assertFalse(LAUNCHER._game_closed())
            names.side_effect = RuntimeError("enumeration unavailable")
            self.assertFalse(LAUNCHER._game_closed())

    def test_native_snapshot_copies_protected_names_and_closes_handle(self):
        values = iter(["Secure System", "NMS.exe"])
        def advance(handle, pointer):
            name = next(values, None)
            if name is None:
                return False
            pointer._obj.name = name
            return True
        api = types.SimpleNamespace(CreateToolhelp32Snapshot=Mock(return_value=123),
                                    Process32FirstW=Mock(side_effect=advance),
                                    Process32NextW=Mock(side_effect=advance),
                                    CloseHandle=Mock(return_value=True), get_last_error=Mock(return_value=18))
        self.assertEqual(LAUNCHER._windows_process_names(api), ["Secure System", "NMS.exe"])
        api.CloseHandle.assert_called_once_with(123)
        api.CreateToolhelp32Snapshot.assert_called_once_with(2, 0)

    def test_incomplete_native_snapshot_refuses_and_releases_handle(self):
        def first(handle, pointer):
            pointer._obj.name = "python.exe"
            return True
        api = types.SimpleNamespace(CreateToolhelp32Snapshot=Mock(return_value=123),
                                    Process32FirstW=first, Process32NextW=Mock(return_value=False),
                                    CloseHandle=Mock(return_value=True), get_last_error=Mock(return_value=5))
        with self.assertRaisesRegex(LAUNCHER.BundleError, "incomplete"):
            LAUNCHER._windows_process_names(api)
        api.CloseHandle.assert_called_once_with(123)

    def test_icon_setup_requires_matching_explicit_game_and_preserves_other_files(self):
        game = self.root / "game"
        (game / "Binaries").mkdir(parents=True)
        executable = b"Owned fake executable; never run"
        (game / "Binaries/NMS.exe").write_bytes(executable)
        self.manifest["supported_nms_exe_sha256"] = hashlib.sha256(executable).hexdigest()
        self.save_manifest()
        (self.bundle / "quick_menu_assets.py").write_bytes((ROOT / "tools/quick_menu_assets.py").read_bytes())
        for name in ("SETTINGS.DDS", "AUTOMATION.DDS", "SELECTION.DDS", "BIOME.DDS", "PLANET.DDS", "STATION.DDS", "ANOMALY.DDS"):
            (self.bundle / name).write_bytes((ROOT / "assets/ui" / name).read_bytes())
        sentinel = game / "keep.txt"
        sentinel.write_bytes(b"preserved")
        with patch.object(LAUNCHER, "_game_closed", return_value=False), \
                self.assertRaisesRegex(LAUNCHER.compatibility.CompatibilityError, "launcher.game_running"):
            LAUNCHER._prepare_icon_asset(self.bundle, str(game))
        self.assertFalse((game / "GAMEDATA").exists())
        with patch.object(LAUNCHER, "_game_closed", return_value=True):
            result = LAUNCHER._prepare_icon_asset(self.bundle, str(game))
            self.assertTrue(result["installed"])
            self.assertTrue(LAUNCHER._prepare_icon_asset(self.bundle, str(game))["reused"])
            (game / "Binaries/NMS.exe").write_bytes(b"unsupported")
            with self.assertRaises(LAUNCHER.compatibility.CompatibilityError):
                LAUNCHER._prepare_icon_asset(self.bundle, str(game))
        self.assertEqual(sentinel.read_bytes(), b"preserved")

    def test_import_does_not_import_framework_or_access_processes(self):
        original_import = builtins.__import__
        def checked_import(name, *args, **kwargs):
            if name.startswith(("pymem", "pymhf", "pyrun_injected")):
                self.fail("Unexpected process/framework import: " + name)
            return original_import(name, *args, **kwargs)
        source = SOURCE.read_text(encoding="utf-8")
        with patch.object(builtins, "__import__", side_effect=checked_import), patch.object(
            Path, "open", side_effect=AssertionError("Import must not read bundle files")
        ):
            exec(compile(source, str(SOURCE), "exec"), {"__name__": "offline_import", "__file__": str(SOURCE)})

    def test_guard_precedes_mod_folder_entry_and_argv_is_unchanged(self):
        previous = sys.argv
        original = list(previous)
        self.assertEqual(self.main(), 42)
        self.assertEqual(self.events, ["lease", "guard", "asset", "run", "release"])
        self.runtime.run_module.assert_called_once_with(str(self.bundle.resolve()), LAUNCHER.EXPECTED_CONFIG)
        self.assertIs(sys.argv, previous)
        self.assertEqual(sys.argv, original)
        self.assertTrue(self.entrypoints.select.called)
        self.assertTrue(all(call.kwargs == {"group": "pymhflib"}
                            for call in self.entrypoints.select.call_args_list))
        self.verify_game.assert_called_once_with(str(self.root / "game"))
        self.bootstrap.install_injection_guard.assert_called_once_with(expected_executable=self.verified_executable)

    def test_framework_error_propagates_without_argv_changes_or_retry(self):
        previous = sys.argv
        original = list(previous)
        self.runtime.run_module.side_effect = RuntimeError("owned test framework error")
        with self.assertRaisesRegex(RuntimeError, "owned test framework error"):
            self.main()
        self.bootstrap.install_injection_guard.assert_called_once()
        self.runtime.run_module.assert_called_once()
        self.assertIs(sys.argv, previous)
        self.assertEqual(sys.argv, original)

    def test_wrong_framework_or_additional_library_stops_before_guard(self):
        self.assertEqual(self.main(runtime_version="0.2.3"), 1)
        self.assertEqual(self.failure.call_args.args[0].key, "launcher.wrong_framework")
        self.entrypoints.select.return_value = (object(),)
        self.assertEqual(self.main(), 1)
        self.assertEqual(self.failure.call_args.args[0].key, "launcher.invalid_package")
        self.bootstrap.install_injection_guard.assert_not_called()
        self.runtime.run_module.assert_not_called()

    def test_injection_guard_error_prevents_framework_call(self):
        self.bootstrap.install_injection_guard.side_effect = RuntimeError("owned guard failure")
        with self.assertRaisesRegex(RuntimeError, "owned guard failure"):
            self.main()
        self.runtime.run_module.assert_not_called()
        self.assertEqual(self.events, ["lease", "release"])

    def test_sibling_bootstrap_retains_verified_remote_dll_guard(self):
        bootstrap = LAUNCHER._load_bootstrap(self.bundle)
        self.assertIs(bootstrap.compatibility, LAUNCHER.compatibility)
        dll = self.root / "owned-placeholder.pyd"
        dll.write_bytes(b"Never loaded; only filename validation is exercised")
        canonical = os.path.normcase(os.path.realpath(str(dll)))
        remote_base, local_base = 0x7FFDA1200000, 0x7FFC55000000
        calls = []
        api = types.SimpleNamespace(
            inject_dll_from_path=Mock(side_effect=lambda *args: calls.append("inject") or local_base),
            enum_process_module=Mock(return_value=[types.SimpleNamespace(
                filename=str(dll), lpBaseOfDll=remote_base)]))
        original = api.inject_dll_from_path
        validator = Mock(side_effect=lambda handle: calls.append(("validate", handle)))
        guarded = bootstrap.install_injection_guard(api, target_validator=validator)
        self.assertEqual(guarded(123, str(dll)), remote_base)
        self.assertEqual(calls, [("validate", 123), "inject"])
        original.assert_called_once_with(123, canonical)
        api.enum_process_module.return_value = []
        with self.assertRaises(bootstrap.InjectionGuardError):
            guarded(123, str(dll))
        self.assertEqual(calls, [("validate", 123), "inject", ("validate", 123), "inject"])

    def test_actual_target_refusal_precedes_injection_and_remote_dll_enumeration(self):
        bootstrap = LAUNCHER._load_bootstrap(self.bundle)
        dll = self.root / "never-loaded.pyd"
        dll.write_bytes(b"Owned path fixture")
        api = types.SimpleNamespace(inject_dll_from_path=Mock(), enum_process_module=Mock())
        original = api.inject_dll_from_path
        rejection = LAUNCHER.compatibility.CompatibilityError("launcher.unsupported_game")
        validator = Mock(side_effect=rejection)
        guarded = bootstrap.install_injection_guard(api, target_validator=validator)
        with self.assertRaises(LAUNCHER.compatibility.CompatibilityError) as result:
            guarded(123, str(dll))
        self.assertIs(result.exception, rejection)
        validator.assert_called_once_with(123)
        original.assert_not_called()
        api.enum_process_module.assert_not_called()

    def test_game_mismatch_and_read_failure_report_without_lease_assets_or_framework(self):
        for key in ("launcher.unsupported_game", "launcher.unreadable_game"):
            with self.subTest(key=key):
                rejection = LAUNCHER.compatibility.CompatibilityError(key)
                self.verify_game.side_effect = rejection
                self.assertEqual(self.main([str(self.bundle), "--language", "fr"]), 1)
                self.failure.assert_called_with(rejection, language="fr", show_dialog=False)
                self.loader.assert_not_called()
        self.bootstrap.launcher_session.assert_not_called()
        self.bootstrap.install_injection_guard.assert_not_called()
        self.asset_setup.assert_not_called()
        self.runtime.run_module.assert_not_called()

    def test_check_only_does_not_probe_closed_state_take_lease_stage_or_launch(self):
        self.closed.side_effect = AssertionError("Check-only must permit a running game")
        before = {path.relative_to(self.root): path.read_bytes()
                  for path in self.root.rglob("*") if path.is_file()}
        with patch("sys.stdout"):
            self.assertEqual(self.main([str(self.bundle), "--check-only"]), 0)
        after = {path.relative_to(self.root): path.read_bytes()
                 for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(after, before)
        self.verify_game.assert_called_once()
        self.loader.assert_not_called()
        self.bootstrap.launcher_session.assert_not_called()
        self.bootstrap.install_injection_guard.assert_not_called()
        self.asset_setup.assert_not_called()
        self.runtime.run_module.assert_not_called()
        self.failure.assert_not_called()

    def test_running_game_refuses_before_guard_and_asset_staging(self):
        self.closed.return_value = False
        self.assertEqual(self.main(), 1)
        self.assertEqual(self.failure.call_args.args[0].key, "launcher.game_running")
        self.assertEqual(self.events, ["lease", "release"])
        self.bootstrap.install_injection_guard.assert_not_called()
        self.asset_setup.assert_not_called()
        self.runtime.run_module.assert_not_called()

    def test_target_rejection_during_framework_entry_releases_lease_without_retry(self):
        previous = sys.argv
        self.runtime.run_module.side_effect = LAUNCHER.compatibility.CompatibilityError("launcher.game_changed")
        self.assertEqual(self.main(), 1)
        self.assertEqual(self.events, ["lease", "guard", "asset", "release"])
        self.runtime.run_module.assert_called_once()
        self.assertIs(sys.argv, previous)
        self.assertEqual(self.failure.call_args.args[0].key, "launcher.game_changed")

    def test_bootstrap_without_guard_function_is_rejected(self):
        (self.bundle / LAUNCHER.BOOTSTRAP_NAME).write_bytes(b"# Owned empty module\n")
        with self.assertRaises(LAUNCHER.BundleError):
            LAUNCHER._load_bootstrap(self.bundle)


if __name__ == "__main__":
    unittest.main()
