"""Offline selection persistence tests using isolated temporary folders."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


_spec = importlib.util.spec_from_file_location(
    "companion_auto_summon_persistence_under_test",
    Path(__file__).resolve().parents[1] / "src" / "persistence.py",
)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
PetSelectionStore = _module.PetSelectionStore
SelectionStoreError = _module.SelectionStoreError


class PetSelectionStoreTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "mod-owned" / "selections.json"
        self.store = PetSelectionStore(self.path)
        self.seed_a = bytes.fromhex("abcdef0123456789abcdef0123456789")
        self.seed_b = bytes.fromhex("00112233445566778899aabbccddeeff")

    def write_bytes(self, content):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(content)

    def write_json(self, document):
        self.write_bytes(json.dumps(document).encode("utf-8"))

    def valid_document(self):
        return {"schema": 1, "selections": {"save-a": {"seed": self.seed_a.hex(), "slot": 7}}}

    def test_missing_read_and_forget_do_not_create_parent(self):
        self.assertIsNone(self.store.load("save-a"))
        self.store.forget("save-a")
        self.assertFalse(self.path.parent.exists())

    def test_restart_reads_same_pet_and_isolates_other_saves(self):
        self.store.remember("save-a", self.seed_a, 7)
        self.store.remember("save-b", self.seed_b, 29)
        restarted = PetSelectionStore(self.path)
        self.assertEqual(restarted.load("save-a"), {"seed": self.seed_a.hex(), "slot": 7})
        self.assertEqual(restarted.load("save-b"), {"seed": self.seed_b.hex(), "slot": 29})
        self.assertIsNone(restarted.load("save-c"))

    def test_updated_choice_is_visible_to_existing_instance(self):
        self.store.remember("save-a", self.seed_a, 7)
        second_instance = PetSelectionStore(self.path)
        second_instance.remember("save-a", self.seed_b, 0)
        self.assertEqual(self.store.load("save-a"), {"seed": self.seed_b.hex(), "slot": 0})

    def test_forget_preserves_other_saves(self):
        self.store.remember("save-a", self.seed_a, 7)
        self.store.remember("save-b", self.seed_b, 9)
        self.store.forget("save-a")
        self.assertIsNone(self.store.load("save-a"))
        self.assertEqual(self.store.load("save-b"), {"seed": self.seed_b.hex(), "slot": 9})

    def test_unicode_and_json_sensitive_identity_roundtrip(self):
        identity = 'Story \u00e9 / "\u4e16\u754c"\n\u0000'
        self.store.remember(identity, self.seed_a, 0)
        self.assertEqual(PetSelectionStore(self.path).load(identity)["seed"], self.seed_a.hex())

    def test_atomic_replace_failure_preserves_original_and_cleans_temporary_file(self):
        self.store.remember("save-a", self.seed_a, 7)
        original = self.path.read_bytes()
        with patch.object(_module.os, "replace", side_effect=PermissionError("locked")):
            with self.assertRaises(SelectionStoreError):
                self.store.remember("save-a", self.seed_b, 8)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_flush_failure_preserves_original_and_cleans_temporary_file(self):
        self.store.remember("save-a", self.seed_a, 7)
        original = self.path.read_bytes()
        with patch.object(_module.os, "fsync", side_effect=OSError("disk error")):
            with self.assertRaises(SelectionStoreError):
                self.store.forget("save-a")
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_corrupt_or_unknown_document_cannot_be_overwritten(self):
        examples = [
            b"{truncated", b"\xff", b"", b"[]",
            b'{"schema": 2, "selections": {}}',
            b'{"schema": true, "selections": {}}',
            b'{"schema": 1.0, "selections": {}}',
            b'{"schema": 1, "selections": {}, "future": 5}',
            b'{"schema": 1, "selections": null}',
            b'{"schema": 1, "schema": 2, "selections": {}}',
            b'{"schema": 1, "selections": {"a": {}, "a": {}}}',
        ]
        for content in examples:
            with self.subTest(content=content):
                self.write_bytes(content)
                for action in (
                    lambda: self.store.load("save-a"),
                    lambda: self.store.remember("save-a", self.seed_a, 7),
                    lambda: self.store.forget("save-a"),
                ):
                    with self.assertRaises(SelectionStoreError):
                        action()
                    self.assertEqual(self.path.read_bytes(), content)

    def test_malformed_unrelated_selection_blocks_write_without_dropping_it(self):
        bad_selections = [
            None, [], {"seed": self.seed_a.hex()},
            {"seed": self.seed_a.hex(), "slot": True},
            {"seed": self.seed_a.hex(), "slot": 1.0},
            {"seed": self.seed_a.hex(), "slot": -1},
            {"seed": self.seed_a.hex(), "slot": 30},
            {"seed": self.seed_a.hex().upper(), "slot": 1},
            {"seed": "f" * 31, "slot": 1},
            {"seed": "g" * 32, "slot": 1},
            {"seed": self.seed_a.hex(), "slot": 1, "unknown": 2},
        ]
        for selection in bad_selections:
            with self.subTest(selection=selection):
                document = self.valid_document()
                document["selections"]["unrelated"] = selection
                self.write_json(document)
                original = self.path.read_bytes()
                with self.assertRaises(SelectionStoreError):
                    self.store.remember("save-a", self.seed_b, 8)
                self.assertEqual(self.path.read_bytes(), original)

    def test_oversized_file_is_rejected_and_preserved(self):
        content = b" " * (PetSelectionStore.MAX_BYTES + 1)
        self.write_bytes(content)
        with self.assertRaises(SelectionStoreError):
            self.store.remember("save-a", self.seed_a, 7)
        self.assertEqual(self.path.read_bytes(), content)

    def test_entry_cap_allows_update_but_rejects_new_identity(self):
        document = {"schema": 1, "selections": {
            f"save-{index}": {"seed": self.seed_a.hex(), "slot": 1}
            for index in range(PetSelectionStore.MAX_ENTRIES)
        }}
        self.write_json(document)
        self.store.remember("save-0", self.seed_b, 2)
        original = self.path.read_bytes()
        with self.assertRaises(SelectionStoreError):
            self.store.remember("extra-save", self.seed_a, 7)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(self.store.load("save-0")["seed"], self.seed_b.hex())

    def test_invalid_caller_arguments_do_not_create_files(self):
        for key in ("", "k" * 257, None, 3, True):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    self.store.load(key)
                with self.assertRaises(ValueError):
                    self.store.remember(key, self.seed_a, 1)
                with self.assertRaises(ValueError):
                    self.store.forget(key)
        for seed in (b"", b"x" * 15, b"x" * 17, self.seed_a.hex(), bytearray(self.seed_a), None):
            with self.subTest(seed=seed):
                with self.assertRaises(ValueError):
                    self.store.remember("save-a", seed, 1)
        for slot in (-1, 30, True, False, 1.0, "1", None):
            with self.subTest(slot=slot):
                with self.assertRaises(ValueError):
                    self.store.remember("save-a", self.seed_a, slot)
        self.assertFalse(self.path.parent.exists())

    def test_invalid_stored_identity_is_not_silently_discarded(self):
        for key in ("", "k" * 257):
            with self.subTest(key=key):
                document = self.valid_document()
                document["selections"][key] = {"seed": self.seed_b.hex(), "slot": 8}
                self.write_json(document)
                original = self.path.read_bytes()
                with self.assertRaises(SelectionStoreError):
                    self.store.forget("save-a")
                self.assertEqual(self.path.read_bytes(), original)

    def test_directory_instead_of_file_reports_storage_error(self):
        self.path.mkdir(parents=True)
        with self.assertRaises(SelectionStoreError):
            self.store.load("save-a")


if __name__ == "__main__":
    unittest.main()
