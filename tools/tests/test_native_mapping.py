from __future__ import annotations

import ast
import json
from pathlib import Path
import tempfile
import unittest

from tools.native_mapping import ROOT, load_native_mapping, read_native_mappings, write_mapping_header


class NativeMappingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "mappings.json"
        self.registry = json.loads((ROOT / "native_mappings.json").read_text(encoding="utf-8"))

    def write(self):
        self.path.write_text(json.dumps(self.registry), encoding="utf-8")
        return self.path

    def test_retained_and_candidate_identities_are_separate(self):
        records = read_native_mappings()
        self.assertTrue(records["25624745"]["activation_approved"])
        self.assertTrue(records["25732212"]["activation_approved"])
        self.assertNotEqual(records["25624745"]["exe_sha256"], records["25732212"]["exe_sha256"])

    def test_candidate_contains_exact_recorded_relocations(self):
        candidate = read_native_mappings()["25732212"]
        self.assertEqual(candidate["functions"]["position_observer"], 0x14F9E20)
        self.assertEqual(candidate["globals"]["application"], 0x6E8D708)
        self.assertEqual(candidate["position_returns"], [0x330314, 0x3306BF, 0x330996])
        self.assertEqual(candidate["local_load"]["state"], 0x6E8EA40)

    def test_rejects_mismatched_release_label(self):
        record = read_native_mappings()["25624745"]
        with self.assertRaisesRegex(ValueError, "no exact"):
            load_native_mapping(dict(record, game_release="Cosmos 7.06"))

    def test_rejects_unapproved_mapping_on_normal_path(self):
        self.registry["builds"]["25732212"]["activation_approved"] = False
        candidate = read_native_mappings(self.write())["25732212"]
        with self.assertRaisesRegex(ValueError, "not approved"):
            load_native_mapping(candidate, path=self.path)

    def test_inspection_keeps_unapproved_flag(self):
        self.registry["builds"]["25732212"]["activation_approved"] = False
        candidate = read_native_mappings(self.write())["25732212"]
        self.assertFalse(load_native_mapping(candidate, path=self.path, require_approved=False)["activation_approved"])

    def test_generated_header_uses_named_selected_values(self):
        approved = read_native_mappings()["25624745"]
        output = Path(self.temp.name) / "selected.hpp"
        write_mapping_header(approved, output)
        generated = output.read_text(encoding="utf-8")
        self.assertIn("build.functions.position_observer=0x14F7F60;", generated)
        self.assertIn("build.globals.application=0x6E89688;", generated)
        self.assertIn("build.activation_approved=true;", generated)
        self.assertNotIn("25732212", generated)

    def test_generated_candidate_cannot_lose_activation_refusal(self):
        output = Path(self.temp.name) / "candidate.hpp"
        self.registry["builds"]["25732212"]["activation_approved"] = False
        write_mapping_header(read_native_mappings(self.write())["25732212"], output)
        generated = output.read_text(encoding="utf-8")
        self.assertIn("build.activation_approved=false;", generated)
        self.assertIn("build.functions.position_observer=0x14F9E20;", generated)

    def test_rejects_duplicate_mapping_keys(self):
        self.path.write_text('{"schema_version":1,"schema_version":1,"builds":{}}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            read_native_mappings(self.path)

    def test_rejects_missing_function(self):
        del self.registry["builds"]["25732212"]["functions"]["label_menu"]
        with self.assertRaisesRegex(ValueError, "unexpected fields"):
            read_native_mappings(self.write())

    def test_rejects_partial_state_policy(self):
        self.registry["builds"]["25732212"]["local_load"]["vtable"] = "0x0"
        with self.assertRaisesRegex(ValueError, "complete or all zero"):
            read_native_mappings(self.write())

    def test_rejects_non_boolean_approval(self):
        self.registry["builds"]["25732212"]["activation_approved"] = 1
        with self.assertRaisesRegex(ValueError, "approval fields"):
            read_native_mappings(self.write())

    def test_rejects_duplicate_return_sites(self):
        values = self.registry["builds"]["25732212"]["position_returns"]
        values[1] = values[0]
        with self.assertRaisesRegex(ValueError, "distinct"):
            read_native_mappings(self.write())

    def test_rejects_private_or_parent_evidence_paths(self):
        for value in ("../private.md", "C:/private.md", "docs\\private.md"):
            with self.subTest(value=value):
                self.registry["builds"]["25732212"]["evidence"] = value
                with self.assertRaisesRegex(ValueError, "repository-relative"):
                    read_native_mappings(self.write())

    def test_package_label_and_windows_resource_revision_agree(self):
        versions = []
        for name in ("build_native_runtime.py", "package_native_runtime.py"):
            source = (ROOT / "tools" / name).read_text(encoding="utf-8")
            tree = ast.parse(source)
            values = [ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == "VERSION" for target in node.targets)]
            self.assertEqual(len(values), 1)
            versions.extend(values)
        self.assertEqual(versions[0], versions[1])
        self.assertRegex(versions[0], r"^\d+\.\d+\.\d+-native-test$")
        revision = ",".join(versions[0].split("-")[0].split(".") + ["0"])
        builder = (ROOT / "tools/build_native_runtime.py").read_text(encoding="utf-8")
        self.assertIn("FILEVERSION " + revision, builder)
        self.assertIn("PRODUCTVERSION " + revision, builder)


if __name__ == "__main__":
    unittest.main()
