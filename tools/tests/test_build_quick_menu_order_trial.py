"""Offline packaging checks using synthetic source and isolated temporary paths."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


TOOLS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "order_trial_builder", TOOLS / "build_quick_menu_order_trial.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class OrderTrialBuildTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "tools").mkdir()
        self.source = self.root / "tools/quick_menu_order_trial.py"
        self.source.write_text(
            'TRIAL_ENABLED = False\nraise AssertionError("source must not execute")\n', encoding="utf-8")
        for name in builder.HELPERS:
            (self.root / "tools" / name).write_text(
                'raise AssertionError("helper must not execute")\n', encoding="utf-8")
        (self.root / "Launch-CompanionAutoSummon.py").write_text(
            'raise AssertionError("bootstrap must not execute")\n', encoding="utf-8")
        self.launcher = self.root / "Start-CompanionAutoSummon.ps1"
        self.launcher.write_text(
            "foreach ($scriptName in @('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py')) {}\n"
            'Write-Output "Companion Auto Summon"\nthrow "launcher must not execute"\n', encoding="utf-8")
        (self.root / "manifest.json").write_text(json.dumps({
            "framework": "pymhf[gui]==0.2.4", "steam_build": "synthetic-build",
            "supported_nms_exe_sha256": "f" * 64,
        }), encoding="utf-8")
        self.root_patch = patch.object(builder, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def test_no_output_without_literal_true_opt_in(self):
        for value in (False, None, 1, "yes"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                builder.build(enable_order=value)
        self.assertFalse((self.root / "build").exists())

    def test_ten_file_copy_enables_only_generated_source_and_hashes_every_payload(self):
        originals = {str(path.relative_to(self.root)): path.read_bytes()
                     for path in self.root.rglob("*") if path.is_file()}
        result = builder.build(enable_order=True)
        output = Path(result["output"])
        self.assertEqual(output, self.root / "build/quick-menu-order-trial")
        self.assertEqual(result["files"], 10)
        self.assertFalse(result["launched"])
        self.assertFalse(result["deployed"])
        self.assertFalse(result["observation_only"])
        expected_main = self.source.read_text().replace("TRIAL_ENABLED = False", "TRIAL_ENABLED = True", 1)
        self.assertEqual((output / "CompanionAutoSummon.py").read_bytes(), expected_main.encode())
        self.assertEqual(result["trial_sha256"], hashlib.sha256(expected_main.encode()).hexdigest())
        for name, data in originals.items():
            self.assertEqual((self.root / name).read_bytes(), data)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["version"], "0.6.0-order-trial")
        self.assertEqual(manifest["steam_build"], "synthetic-build")
        self.assertEqual(manifest["supported_nms_exe_sha256"], "f" * 64)
        for key in ("live_verified", "auto_summon", "preference_actions", "observation_only"):
            self.assertFalse(manifest[key])
        self.assertEqual({entry["path"] for entry in manifest["files"]},
                         {path.name for path in output.iterdir()} - {"manifest.json"})
        self.assertEqual(len(manifest["files"]), 9)
        for entry in manifest["files"]:
            self.assertEqual(hashlib.sha256((output / entry["path"]).read_bytes()).hexdigest(), entry["sha256"])
        for name in builder.HELPERS:
            self.assertEqual((output / name).read_bytes(), (self.root / "tools" / name).read_bytes())

    def test_launcher_requires_all_five_helpers_and_preserves_other_content(self):
        original = self.launcher.read_text()
        output = Path(builder.build(enable_order=True)["output"])
        required = ("CompanionAutoSummon.py", "Launch-CompanionAutoSummon.py", *builder.HELPERS)
        expected = original.replace(
            "@('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py')",
            "@(" + ", ".join("'" + name + "'" for name in required) + ")"
        ).replace("Companion Auto Summon", "Companion Auto Summon ordered submenu trial")
        self.assertEqual((output / "Start-CompanionAutoSummon.ps1").read_text(), expected)
        self.assertEqual(set(builder.HELPERS), {"quick_menu_item.py", "quick_menu_submenu.py", "quick_menu_order.py",
                                             "quick_menu_native_guard.py", "quick_menu_guard_runtime.py"})

    def test_instructions_describe_inert_child_native_icon_and_lifecycle(self):
        output = Path(builder.build(enable_order=True)["output"])
        readme = (output / "README.md").read_text()
        for required in ("Settings preview", "fresh backup", "Close NMS normally",
                         "Never hot-reload", "native back control", "close and reopen",
                         "ordinary manual pet actions", "No settings are applied",
                         "icon is still borrowed", "no custom texture", "before the", "first individual pet or pet page"):
            self.assertIn(required, readme)

    def test_existing_output_directory_or_file_is_never_overwritten(self):
        output = self.root / "build/quick-menu-order-trial"
        output.mkdir(parents=True)
        sentinel = output / "do-not-change"
        sentinel.write_bytes(b"retained artifact")
        with self.assertRaises(FileExistsError):
            builder.build(enable_order=True)
        self.assertEqual(list(output.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(), b"retained artifact")
        other = output.parent / "quick-menu-file"
        other.write_bytes(b"retained file")
        with self.assertRaises(FileExistsError):
            builder.build(enable_order=True, output_name=other.name)
        self.assertEqual(other.read_bytes(), b"retained file")

    def test_new_output_name_preserves_previous_trial(self):
        first = Path(builder.build(enable_order=True)["output"])
        before = {path.name: path.read_bytes() for path in first.iterdir()}
        second = Path(builder.build(enable_order=True, output_name="quick-menu-order-next")["output"])
        self.assertNotEqual(first, second)
        self.assertEqual(before, {path.name: path.read_bytes() for path in first.iterdir()})

    def test_path_escape_absolute_and_invalid_targets_fail_before_creation(self):
        for name in ("../elsewhere", "quick-menu-../../other", "C:\\tmp", "other",
                     "quick-menu-x/y", "quick-menu-x\\y", "quick-menu-", None, "quick-menu-x\n"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                builder.build(enable_order=True, output_name=name)
        self.assertFalse((self.root / "build").exists())

    def test_missing_or_ambiguous_opt_in_marker_creates_nothing(self):
        for data in ("TRIAL_ENABLED = True\n", "TRIAL_ENABLED = False\nTRIAL_ENABLED = False\n"):
            self.source.write_text(data)
            with self.assertRaises(ValueError):
                builder.build(enable_order=True)
        self.assertFalse((self.root / "build").exists())

    def test_missing_helper_or_invalid_code_fails_before_output_creation(self):
        helper = self.root / "tools/quick_menu_submenu.py"
        helper.unlink()
        with self.assertRaises(FileNotFoundError):
            builder.build(enable_order=True)
        helper.write_text("def invalid syntax:")
        with self.assertRaises(SyntaxError):
            builder.build(enable_order=True)
        self.assertFalse((self.root / "build").exists())

    def test_unrecognized_launcher_checksum_list_creates_nothing(self):
        original = self.launcher.read_text()
        for text in ("# no checksum list\n", original + original):
            self.launcher.write_text(text)
            with self.assertRaises(ValueError):
                builder.build(enable_order=True)
        self.assertFalse((self.root / "build").exists())

    def test_failed_write_leaves_output_reserved_and_cannot_be_retried_over_it(self):
        real_write = Path.write_bytes
        def failing_write(path, data):
            if path.name == "quick_menu_submenu.py":
                raise OSError("synthetic write failure")
            return real_write(path, data)
        with patch.object(Path, "write_bytes", failing_write), self.assertRaises(OSError):
            builder.build(enable_order=True)
        output = self.root / "build/quick-menu-order-trial"
        before = {path.name: path.read_bytes() for path in output.iterdir()}
        self.assertTrue(before)
        with self.assertRaises(FileExistsError):
            builder.build(enable_order=True)
        self.assertEqual(before, {path.name: path.read_bytes() for path in output.iterdir()})


if __name__ == "__main__":
    unittest.main()
