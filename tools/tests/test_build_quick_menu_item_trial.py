"""Packaging isolation checks for the explicitly mutating developer trial."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


TOOLS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("item_trial_builder", TOOLS / "build_quick_menu_item_trial.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class ItemTrialBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "tools").mkdir()
        (self.root / "tools/quick_menu_item_trial.py").write_text(
            'TRIAL_ENABLED = False\nraise AssertionError("must not execute")\n', encoding="utf-8")
        for name in builder.HELPERS:
            (self.root / "tools" / name).write_text('raise AssertionError("must not execute")\n', encoding="utf-8")
        (self.root / "Launch-CompanionAutoSummon.py").write_text('raise AssertionError("must not execute")\n')
        (self.root / "Start-CompanionAutoSummon.ps1").write_text(
            "foreach ($scriptName in @('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py')) {}\n"
            'throw "must not execute"\n')
        (self.root / "manifest.json").write_text(json.dumps({
            "framework": "pymhf 0.2.4", "steam_build": "fixture",
            "supported_nms_exe_sha256": "f" * 64,
        }))
        self.addCleanup(patch.stopall)
        patch.object(builder, "ROOT", self.root).start()

    def test_no_output_without_explicit_opt_in(self):
        for value in (False, None, 1, "yes"):
            with self.assertRaises(ValueError):
                builder.build(enable_inert_item=value)
        self.assertFalse((self.root / "build").exists())

    def test_isolated_enabled_copy_hashes_and_truthful_trial_scope(self):
        result = builder.build(enable_inert_item=True)
        output = Path(result["output"])
        self.assertFalse(result["launched"])
        self.assertFalse(result["deployed"])
        self.assertFalse(result["observation_only"])
        self.assertIn("TRIAL_ENABLED = True", (output / "CompanionAutoSummon.py").read_text())
        self.assertIn("TRIAL_ENABLED = False", (self.root / "tools/quick_menu_item_trial.py").read_text())
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertFalse(manifest["live_verified"])
        self.assertFalse(manifest["auto_summon"])
        self.assertFalse(manifest["preference_actions"])
        for entry in manifest["files"]:
            self.assertEqual(hashlib.sha256((output / entry["path"]).read_bytes()).hexdigest(), entry["sha256"])
        self.assertEqual(set(builder.HELPERS).difference(p.name for p in output.iterdir()), set())
        launcher = (output / "Start-CompanionAutoSummon.ps1").read_text()
        for name in builder.HELPERS:
            self.assertIn("'" + name + "'", launcher)

    def test_running_or_retained_output_is_never_overwritten(self):
        output = self.root / "build/quick-menu-inert-item"
        output.mkdir(parents=True)
        sentinel = output / "do-not-change"
        sentinel.write_bytes(b"running trial")
        with self.assertRaises(FileExistsError):
            builder.build(enable_inert_item=True)
        self.assertEqual(list(output.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(), b"running trial")

    def test_new_safe_output_name_retains_an_earlier_trial(self):
        first = builder.build(enable_inert_item=True)
        second = builder.build(enable_inert_item=True, output_name="quick-menu-inert-item-next")
        self.assertNotEqual(first["output"], second["output"])
        self.assertTrue(Path(first["output"]).is_dir())

    def test_path_escape_and_absolute_targets_rejected(self):
        for name in ("../elsewhere", "quick-menu-../../other", "C:\\tmp", "other", "quick-menu-x/y"):
            with self.assertRaises(ValueError):
                builder.build(enable_inert_item=True, output_name=name)
        self.assertFalse((self.root / "build").exists())

    def test_missing_or_ambiguous_opt_in_marker_produces_no_artifact(self):
        source = self.root / "tools/quick_menu_item_trial.py"
        for data in ("TRIAL_ENABLED = True\n", "TRIAL_ENABLED = False\nTRIAL_ENABLED = False\n"):
            source.write_text(data)
            with self.assertRaises(ValueError):
                builder.build(enable_inert_item=True)
        self.assertFalse((self.root / "build").exists())

    def test_missing_helper_or_invalid_source_fails_before_output_creation(self):
        helper = self.root / "tools" / builder.HELPERS[0]
        helper.unlink()
        with self.assertRaises(FileNotFoundError):
            builder.build(enable_inert_item=True)
        helper.write_text("def invalid syntax:")
        with self.assertRaises(SyntaxError):
            builder.build(enable_inert_item=True)
        self.assertFalse((self.root / "build").exists())


if __name__ == "__main__":
    unittest.main()
