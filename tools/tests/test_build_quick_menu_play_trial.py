"""Offline combined-bundle packaging tests; every output is temporary."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch


TOOLS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "play_trial_builder", TOOLS / "build_quick_menu_play_trial.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class PlayTrialBuildTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "tools").mkdir()
        self.menu = self.root / "tools/quick_menu_order_trial.py"
        self.menu.write_bytes(
            b'TRIAL_ENABLED = False\r\nSETTINGS_TOGGLE_ENABLED = False\r\nraise AssertionError("menu must not execute")\r\n')
        self.production = self.root / builder.PRODUCTION_FILE
        self.production.write_bytes(
            b'# preserved production\r\nraise AssertionError("production must not execute")\r\n')
        self.guard_host = self.root / builder.GUARD_HOST_FILE
        self.guard_host.write_bytes(b'raise AssertionError("guard must not execute")\r\n')
        self.play_host = self.root / "tools" / builder.PLAY_HOST_FILE
        self.play_host.write_bytes(b'raise AssertionError("play host must not execute")\r\n')
        for name in builder.HELPERS:
            (self.root / "tools" / name).write_bytes(
                b'raise AssertionError("helper must not execute")\r\n')
        self.launcher = self.root / builder.LAUNCHER_FILE
        self.launcher.write_bytes(b"\r\n".join((
            b"# retained setup and game guards",
            b"Assert-GameClosed",
            b"$modPath = Join-Path $PSScriptRoot 'CompanionAutoSummon.py'",
            b"$bootstrapPath = Join-Path $PSScriptRoot 'Launch-CompanionAutoSummon.py'",
            b"if (-not (Test-Path -LiteralPath $modPath -PathType Leaf)) { throw 'missing' }",
            b"foreach ($scriptName in @('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py')) {}",
            b"& $runtimePython $bootstrapPath $modPath",
            b'throw "launcher must not execute"', b"",
        )))
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text(json.dumps({
            "version": "0.4.5-experimental", "framework": "pymhf[gui]==0.2.4",
            "steam_build": "synthetic-build", "supported_nms_exe_sha256": "f" * 64,
        }), encoding="utf-8")
        self.root_patch = patch.object(builder, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def build(self, **kwargs):
        return builder.build(enable_menu=True, **kwargs)

    def test_requires_literal_opt_in_before_reading_sources_or_creating_output(self):
        for enabled in (False, None, 1, "true"):
            with self.subTest(enabled=enabled), self.assertRaises(ValueError):
                builder.build(enable_menu=enabled)
        self.assertFalse((self.root / "build").exists())

    def test_exact_two_mod_bundle_preserves_sources_and_hashes_all_payloads(self):
        originals = {str(path.relative_to(self.root)): path.read_bytes()
                     for path in self.root.rglob("*") if path.is_file()}
        result = self.build()
        output = Path(result["output"])
        self.assertEqual(output, self.root / "build/quick-menu-play-trial-072")
        self.assertEqual(result["files"], 15)
        self.assertFalse(result["launched"])
        self.assertFalse(result["deployed"])
        self.assertTrue(result["auto_summon"])
        self.assertFalse(result["observation_only"])
        self.assertEqual((output / builder.PRODUCTION_FILE).read_bytes(), self.production.read_bytes())
        self.assertEqual((output / builder.GUARD_HOST_FILE).read_bytes(), self.guard_host.read_bytes())
        self.assertEqual((output / builder.PLAY_HOST_FILE).read_bytes(), self.play_host.read_bytes())
        expected_menu = self.menu.read_bytes().replace(b"TRIAL_ENABLED = False", b"TRIAL_ENABLED = True", 1)
        expected_menu = expected_menu.replace(b"SETTINGS_TOGGLE_ENABLED = False", b"SETTINGS_TOGGLE_ENABLED = True", 1)
        self.assertEqual((output / builder.MENU_FILE).read_bytes(), expected_menu)
        self.assertEqual(result["trial_sha256"], hashlib.sha256(expected_menu).hexdigest())
        self.assertEqual(result["production_sha256"], hashlib.sha256(self.production.read_bytes()).hexdigest())
        for name, data in originals.items():
            self.assertEqual((self.root / name).read_bytes(), data)
        for name in builder.HELPERS:
            self.assertEqual((output / name).read_bytes(), (self.root / "tools" / name).read_bytes())
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["version"], "0.7.2-play-trial")
        self.assertEqual(manifest["mods"], [
            {"name": "CompanionAutoSummon", "version": "0.4.5-experimental", "path": builder.PRODUCTION_FILE},
            {"name": "CompanionMenuOrderTrial", "version": "0.7.0-toggle-trial", "path": builder.MENU_FILE},
        ])
        self.assertTrue(manifest["auto_summon"])
        self.assertTrue(manifest["preference_actions"])
        self.assertEqual(manifest["preference_keys"], ["enabled"])
        for key in ("live_verified", "observation_only", "preferences_included"):
            self.assertFalse(manifest[key])
        self.assertEqual(manifest["steam_build"], "synthetic-build")
        self.assertEqual(manifest["supported_nms_exe_sha256"], "f" * 64)
        entries = manifest["files"]
        self.assertEqual(len(entries), 14)
        self.assertEqual({entry["path"] for entry in entries},
                         {path.name for path in output.iterdir()} - {"manifest.json"})
        for entry in entries:
            self.assertEqual(entry["sha256"], hashlib.sha256((output / entry["path"]).read_bytes()).hexdigest())

    def test_folder_configuration_matches_reviewed_framework_route(self):
        output = Path(self.build()["output"])
        config = tomllib.loads((output / builder.CONFIG_FILE).read_text())
        self.assertEqual(config, {"pymhf": {
            "exe": "NMS.exe", "steam_gameid": 275850, "start_paused": False,
            "interactive_console": False,
            "logging": {"shown": False, "log_dir": "{CURR_DIR}", "log_level": "info"},
            "gui": {"shown": True, "always_on_top": False},
        }})
        self.assertFalse((output / "pyproject.toml").exists())

    def test_launcher_only_changes_known_folder_markers_and_checks_every_executable(self):
        original = self.launcher.read_bytes()
        output = Path(self.build()["output"])
        generated = (output / builder.LAUNCHER_FILE).read_bytes()
        expected = original.replace(
            b"$modPath = Join-Path $PSScriptRoot 'CompanionAutoSummon.py'", b"$modPath = $PSScriptRoot"
        ).replace(
            b"$bootstrapPath = Join-Path $PSScriptRoot 'Launch-CompanionAutoSummon.py'",
            b"$bootstrapPath = Join-Path $PSScriptRoot 'Launch-CompanionAutoSummon-PlayTrial.py'"
        ).replace(
            b"@('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py')",
            ("@(" + ", ".join("'" + name + "'" for name in builder.CHECKED_FILES) + ")").encode()
        ).replace(
            b"(Test-Path -LiteralPath $modPath -PathType Leaf)",
            b"(Test-Path -LiteralPath $modPath -PathType Container)"
        )
        self.assertEqual(generated, expected)
        self.assertEqual(set(builder.CHECKED_FILES), {path.name for path in output.iterdir()}
                         - {"README.md", "manifest.json"})
        self.assertIn(b"& $runtimePython $bootstrapPath $modPath\r\n", generated)

    def test_missing_or_duplicate_launcher_marker_fails_before_creation(self):
        original = self.launcher.read_bytes()
        for marker in (
            b"$modPath = Join-Path $PSScriptRoot 'CompanionAutoSummon.py'",
            b"$bootstrapPath = Join-Path $PSScriptRoot 'Launch-CompanionAutoSummon.py'",
            b"@('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py')",
            b"(Test-Path -LiteralPath $modPath -PathType Leaf)",
        ):
            for changed in (original.replace(marker, b"# changed marker"), original + marker):
                with self.subTest(marker=marker, changed=changed):
                    self.launcher.write_bytes(changed)
                    with self.assertRaises(ValueError):
                        self.build()
                    self.assertFalse((self.root / "build").exists())

    def test_readme_explains_native_toggle_and_preserves_other_preferences(self):
        output = Path(self.build()["output"])
        readme = (output / "README.md").read_text()
        for phrase in ("two mods", "0.4.5-experimental", "0.7.0-toggle-trial", "Automatic summoning: ON/OFF",
                       "This revision is not yet live-verified", "not reset or forced",
                       "temporary CompanionAutoSummon development panel", "no personal data", "absolute LOCALAPPDATA",
                       "neither mod writes the game's save files", "Never hot-reload",
                       "Exit NMS normally", "fresh backup", "no custom texture",
                       "first eligible local-player update", "current selection mode",
                       "change is needed", "Deserialization makes no native"):
            self.assertIn(phrase, readme)

    def test_personal_data_and_unlisted_source_files_are_not_packaged(self):
        personal = self.root / "NMS-AutoPet"
        personal.mkdir()
        settings = personal / "settings.json"
        settings.write_bytes(b'{"enabled":false}')
        state = personal / "state.json"
        state.write_bytes(b'{"manual":"private"}')
        (self.root / "tools/unrelated.py").write_bytes(b"not valid Python and must not be read")
        with patch.dict("os.environ", {"LOCALAPPDATA": str(self.root)}):
            output = Path(self.build()["output"])
        self.assertEqual(settings.read_bytes(), b'{"enabled":false}')
        self.assertEqual(state.read_bytes(), b'{"manual":"private"}')
        self.assertFalse((output / "settings.json").exists())
        self.assertFalse((output / "state.json").exists())
        self.assertFalse((output / "unrelated.py").exists())

    def test_existing_file_or_directory_is_not_reused(self):
        output = self.root / "build/quick-menu-play-trial-072"
        output.mkdir(parents=True)
        sentinel = output / "keep"
        sentinel.write_bytes(b"prior trial")
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(list(output.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(), b"prior trial")
        file = output.parent / "quick-menu-file"
        file.write_bytes(b"prior file")
        with self.assertRaises(FileExistsError):
            self.build(output_name=file.name)
        self.assertEqual(file.read_bytes(), b"prior file")

    def test_new_output_name_keeps_earlier_output_immutable(self):
        first = Path(self.build()["output"])
        before = {path.name: path.read_bytes() for path in first.iterdir()}
        second = Path(self.build(output_name="quick-menu-play-next")["output"])
        self.assertNotEqual(first, second)
        self.assertEqual(before, {path.name: path.read_bytes() for path in first.iterdir()})

    def test_invalid_or_escaping_output_name_fails_before_creation(self):
        for name in (None, "../escape", "C:\\escape", "quick-menu-x/y", "quick-menu-x\\y",
                     "quick-menu-", "quick-menu-x\n", "other", "quick-menu-" + "x" * 65):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.build(output_name=name)
        self.assertFalse((self.root / "build").exists())

    def test_missing_or_duplicate_menu_opt_in_marker_is_rejected(self):
        for content in (b"TRIAL_ENABLED = True\n", b"TRIAL_ENABLED = False\n" * 2):
            self.menu.write_bytes(content)
            with self.assertRaises(ValueError):
                self.build()
        self.assertFalse((self.root / "build").exists())

    def test_missing_payload_or_invalid_python_creates_no_output(self):
        self.play_host.unlink()
        with self.assertRaises(FileNotFoundError):
            self.build()
        self.play_host.write_bytes(b"def bad syntax:")
        with self.assertRaises(SyntaxError):
            self.build()
        self.assertFalse((self.root / "build").exists())

    def test_production_or_framework_version_drift_is_rejected(self):
        original = json.loads(self.manifest.read_text())
        for key, value in (("version", "0.4.2-experimental"), ("version", "0.5.0"),
                           ("framework", "pymhf[gui]==0.3.0")):
            self.manifest.write_text(json.dumps({**original, key: value}))
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.build()
        self.assertFalse((self.root / "build").exists())

    def test_write_failure_retains_partial_output_and_refuses_retry(self):
        original_write = Path.write_bytes
        def failing_write(path, data):
            if path.name == builder.PLAY_HOST_FILE:
                raise OSError("synthetic write failure")
            return original_write(path, data)
        with patch.object(Path, "write_bytes", failing_write), self.assertRaises(OSError):
            self.build()
        output = self.root / "build/quick-menu-play-trial-072"
        before = {path.name: path.read_bytes() for path in output.iterdir()}
        self.assertTrue(before)
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(before, {path.name: path.read_bytes() for path in output.iterdir()})

    def test_readback_corruption_is_reported_without_overwriting_failed_output(self):
        original_write = Path.write_bytes
        def corrupting_write(path, data):
            if path.name == builder.MENU_FILE:
                data += b"# synthetic corruption\n"
            return original_write(path, data)
        with patch.object(Path, "write_bytes", corrupting_write), self.assertRaises(RuntimeError):
            self.build()
        with self.assertRaises(FileExistsError):
            self.build()


if __name__ == "__main__":
    unittest.main()
