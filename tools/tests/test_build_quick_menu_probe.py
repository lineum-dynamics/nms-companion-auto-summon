"""Build diagnostics in temporary directories, never in a game installation."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "build_quick_menu_probe.py"
SPEC = importlib.util.spec_from_file_location("probe_builder_under_test", SOURCE)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class ObserverBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.patch = patch.object(BUILDER, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        (self.root / "tools").mkdir()
        for profile in BUILDER.STAGES.values():
            (self.root / "tools" / profile["source"]).write_text(
                "PROBE_ENABLED = False\nraise RuntimeError('Build must never execute source')\n",
                encoding="utf-8")
        (self.root / "manifest.json").write_text(json.dumps({
            "framework": "pymhf[gui]==0.2.4", "steam_build": "25442159",
            "supported_nms_exe_sha256": "a" * 64,
        }), encoding="utf-8")
        (self.root / "Launch-CompanionAutoSummon.py").write_bytes(b"# Offline fixture\n")
        (self.root / "Start-CompanionAutoSummon.ps1").write_text(
            "# Companion Auto Summon\nthrow 'Build must never launch'\n", encoding="utf-8")

    def test_explicit_opt_in_is_required_before_writing(self):
        with self.assertRaises(ValueError):
            BUILDER.build()
        self.assertFalse((self.root / "build").exists())

    def test_structure_output_is_separate_and_hashes_match(self):
        action = BUILDER.build(enable_observer=True)
        action_path = Path(action["output"])
        retained = {p.name: p.read_bytes() for p in action_path.iterdir()}
        result = BUILDER.build(enable_observer=True, stage="structure")
        output = Path(result["output"])
        self.assertNotEqual(output, action_path)
        self.assertFalse(result["deployed"])
        self.assertFalse(result["launched"])
        self.assertEqual(result["files"], 5)
        self.assertEqual({p.name: p.read_bytes() for p in action_path.iterdir()}, retained)
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.2.0-observer")
        self.assertFalse(manifest["live_verified"])
        for entry in manifest["files"]:
            self.assertEqual(hashlib.sha256((output / entry["path"]).read_bytes()).hexdigest(),
                             entry["sha256"])
        self.assertIn(b"PROBE_ENABLED = True", (output / "CompanionAutoSummon.py").read_bytes())
        self.assertIn("PROBE_ENABLED = False",
                      (self.root / "tools" / "quick_menu_structure_probe.py").read_text())

    def test_existing_artifact_and_logs_are_never_overwritten(self):
        result = BUILDER.build(enable_observer=True)
        output = Path(result["output"])
        (output / "active.log").write_bytes(b"existing runtime evidence")
        snapshot = {p.name: p.read_bytes() for p in output.iterdir()}
        with self.assertRaises(FileExistsError):
            BUILDER.build(enable_observer=True)
        self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, snapshot)
        alternate = BUILDER.build(enable_observer=True, output_name="quick-menu-fresh-trial")
        self.assertNotEqual(alternate["output"], str(output))

    def test_phase_stage_preserves_both_previous_observers(self):
        retained = {}
        for stage in ("actions", "structure"):
            output = Path(BUILDER.build(enable_observer=True, stage=stage)["output"])
            retained[output] = {path.name: path.read_bytes() for path in output.iterdir()}
        result = BUILDER.build(enable_observer=True, stage="phases")
        output = Path(result["output"])
        self.assertNotIn(output, retained)
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.3.0-observer")
        self.assertFalse(manifest["live_verified"])
        for previous, contents in retained.items():
            self.assertEqual({path.name: path.read_bytes() for path in previous.iterdir()}, contents)

    def test_output_name_cannot_escape_build_directory(self):
        for name in ("../outside", "quick-menu-../escape", "C:\\outside", "", "quick-menu-"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                BUILDER.build(enable_observer=True, output_name=name)
        self.assertFalse((self.root / "build").exists())

    def test_invalid_stage_or_source_is_rejected_before_output_creation(self):
        with self.assertRaises(ValueError):
            BUILDER.build(enable_observer=True, stage="unknown")
        source = self.root / "tools" / "quick_menu_structure_probe.py"
        source.write_text("PROBE_ENABLED = True\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            BUILDER.build(enable_observer=True, stage="structure")
        source.write_text("PROBE_ENABLED = False\ninvalid syntax here\n", encoding="utf-8")
        with self.assertRaises(SyntaxError):
            BUILDER.build(enable_observer=True, stage="structure")
        self.assertFalse((self.root / "build").exists())


if __name__ == "__main__":
    unittest.main()
