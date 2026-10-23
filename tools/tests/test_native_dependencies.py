from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tools.validate_native_dependencies import ROOT, PATCH_PATH, GUARDED_QUERY, validate


class NativeDependencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.lock_path = self.root / "native/dependencies-lock.json"
        self.lock = json.loads((ROOT / "native/dependencies-lock.json").read_bytes())
        entries = [e for c in self.lock["components"] for e in c.get("retained_files", [])]
        entries += self.lock["notice_files"]
        for entry in entries:
            target = self.root / entry["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / entry["path"], target)
        self.component = next(c for c in self.lock["components"] if c["name"] == "MinHook")
        self.entry = next(e for e in self.component["retained_files"] if e["path"] == PATCH_PATH)
        self.save_lock()

    def save_lock(self):
        self.lock_path.write_text(json.dumps(self.lock), encoding="utf-8")

    def authorize_changed_file(self, data):
        (self.root / PATCH_PATH).write_bytes(data)
        self.entry.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        self.save_lock()

    def test_current_repository_dependencies_pass(self):
        report = validate()
        self.assertTrue(report["passed"])
        self.assertEqual(report["local_patches"], [PATCH_PATH])
        self.assertFalse(report["network_access"])

    def test_exact_copy_passes(self):
        self.assertTrue(validate(source_root=self.root)["passed"])

    def test_changed_source_is_rejected(self):
        (self.root / PATCH_PATH).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "identity differs"):
            validate(source_root=self.root)

    def test_changed_notice_is_rejected(self):
        (self.root / "native/licenses/README.md").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "identity differs"):
            validate(source_root=self.root)

    def test_wrong_original_identity_is_rejected(self):
        self.entry["upstream_sha256"] = "0"*64
        self.save_lock()
        with self.assertRaisesRegex(ValueError, "Original MinHook"):
            validate(source_root=self.root)

    def test_undeclared_local_patch_is_rejected(self):
        self.component["local_modifications"] = []
        self.save_lock()
        with self.assertRaisesRegex(ValueError, "local provenance"):
            validate(source_root=self.root)

    def test_claim_of_unmodified_upstream_is_rejected(self):
        self.component["retained_files_match_exact_upstream_bytes"] = True
        self.save_lock()
        with self.assertRaisesRegex(ValueError, "local provenance"):
            validate(source_root=self.root)

    def test_other_changes_cannot_be_hidden_in_updated_hash(self):
        self.authorize_changed_file((self.root / PATCH_PATH).read_bytes()+b"/* extra */\n")
        with self.assertRaisesRegex(ValueError, "delta exceeds"):
            validate(source_root=self.root)

    def test_missing_guard_is_rejected_even_with_updated_hash(self):
        self.authorize_changed_file((self.root / PATCH_PATH).read_bytes().replace(GUARDED_QUERY, b"    return FALSE;"))
        with self.assertRaisesRegex(ValueError, "exactly one"):
            validate(source_root=self.root)

    def test_duplicate_file_identity_is_rejected(self):
        self.component["retained_files"].append(dict(self.entry))
        self.save_lock()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate(source_root=self.root)

    def test_escape_path_is_rejected_before_read(self):
        self.component["retained_files"][0]["path"] = "native/../../outside"
        self.save_lock()
        with self.assertRaisesRegex(ValueError, "Invalid dependency path"):
            validate(source_root=self.root)

    def test_unexpected_patch_is_rejected(self):
        self.component["local_modifications"][0]["id"] = "other-patch"
        self.save_lock()
        with self.assertRaisesRegex(ValueError, "Unexpected local"):
            validate(source_root=self.root)


if __name__ == "__main__":
    unittest.main()
