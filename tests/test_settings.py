"""Offline settings-store tests using only temporary, test-owned files."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


_SOURCE_PATH = Path(__file__).resolve().parents[1] / "src" / "settings.py"
_spec = importlib.util.spec_from_file_location("companion_auto_summon_settings_under_test", _SOURCE_PATH)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
CompanionAutoSummonSettingsStore = _module.CompanionAutoSummonSettingsStore
SettingsStoreError = _module.SettingsStoreError


class CompanionAutoSummonSettingsStoreTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="companion-auto-summon-settings-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.path = self.root / "nested" / "settings.json"
        self.store = CompanionAutoSummonSettingsStore(self.path)

    def write_raw(self, raw):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(raw)

    def assert_invalid_preserved(self, raw):
        self.write_raw(raw)
        with self.assertRaises(SettingsStoreError):
            self.store.load_preferences()
        with self.assertRaises(SettingsStoreError):
            self.store.save(False)
        with self.assertRaises(SettingsStoreError):
            self.store.save_preferences(CompanionAutoSummonSettingsStore.defaults())
        self.assertEqual(self.path.read_bytes(), raw)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_import_and_constructor_have_no_filesystem_operations(self):
        source = _SOURCE_PATH.read_text(encoding="utf-8")
        with patch.object(Path, "open", side_effect=AssertionError("unexpected open")), patch.object(
            Path, "mkdir", side_effect=AssertionError("unexpected mkdir")
        ), patch.object(_module.os, "replace", side_effect=AssertionError("unexpected replace")):
            namespace = {"__name__": "offline_settings_import"}
            exec(compile(source, "<offline-settings.py>", "exec"), namespace)
            fresh = namespace["CompanionAutoSummonSettingsStore"](self.path)
        self.assertEqual(fresh.path, self.path)
        self.assertFalse(self.path.parent.exists())

    def test_missing_defaults_to_enabled_without_creating_file_or_directory(self):
        self.assertIs(self.store.load(), True)
        self.assertEqual(self.store.load_preferences(), {
            "enabled": True, "locations": [2, 3, 14], "selection_mode": "by_habitat", "prefer_same_biome": True, "rotate_companions": True
        })
        self.assertFalse(self.path.exists())
        self.assertFalse(self.path.parent.exists())

    def test_defaults_and_load_results_do_not_share_mutable_locations(self):
        defaults = CompanionAutoSummonSettingsStore.defaults()
        defaults["locations"].clear()
        defaults["enabled"] = False
        loaded = self.store.load_preferences()
        self.assertEqual(loaded, {
            "enabled": True, "locations": [2, 3, 14], "selection_mode": "by_habitat", "prefer_same_biome": True, "rotate_companions": True
        })
        loaded["locations"].append(99)
        self.assertEqual(self.store.load_preferences(), CompanionAutoSummonSettingsStore.defaults())
        self.assertFalse(self.path.parent.exists())

    def test_disabled_choice_survives_restart_and_can_be_enabled_again(self):
        self.store.save(False)
        self.assertIs(CompanionAutoSummonSettingsStore(self.path).load(), False)
        self.assertEqual(json.loads(self.path.read_text()), {
            "schema": 4, "enabled": False, "locations": [2, 3, 14],
            "selection_mode": "by_habitat", "prefer_same_biome": True, "rotate_companions": True
        })
        CompanionAutoSummonSettingsStore(self.path).save(True)
        self.assertIs(self.store.load(), True)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_legacy_off_migrates_in_memory_only_until_explicit_save(self):
        original = b'{"schema":1,"enabled":false}\n'
        self.write_raw(original)
        expected = {"enabled": False, "locations": [2, 3, 14], "selection_mode": "last_manual", "prefer_same_biome": True, "rotate_companions": False}
        self.assertEqual(self.store.load_preferences(), expected)
        self.assertIs(self.store.load(), False)
        self.assertEqual(self.path.read_bytes(), original)
        self.store.save_preferences(expected)
        self.assertEqual(json.loads(self.path.read_bytes()), {"schema": 4, **expected})
        self.assertEqual(CompanionAutoSummonSettingsStore(self.path).load_preferences(), expected)

    def test_all_preferences_round_trip_in_canonical_order_without_mutating_input(self):
        preferences = {"enabled": False, "locations": [14, 2, 3], "selection_mode": "random", "prefer_same_biome": False, "rotate_companions": False}
        self.store.save_preferences(preferences)
        expected = {"enabled": False, "locations": [2, 3, 14], "selection_mode": "random", "prefer_same_biome": False, "rotate_companions": False}
        self.assertEqual(CompanionAutoSummonSettingsStore(self.path).load_preferences(), expected)
        self.assertEqual(json.loads(self.path.read_bytes()), {"schema": 4, **expected})
        self.assertEqual(preferences["locations"], [14, 2, 3])
        preferences["locations"].clear()
        self.assertEqual(self.store.load_preferences(), expected)

    def test_schema_two_migration_preserves_choices_and_only_writes_schema_four_on_save(self):
        for locations, mode in (([], "last_manual"), ([14, 2], "random")):
            with self.subTest(locations=locations, mode=mode):
                legacy = {"schema": 2, "enabled": False, "locations": locations, "selection_mode": mode}
                original = json.dumps(legacy).encode("utf-8")
                self.write_raw(original)
                expected = {"enabled": False, "locations": sorted(locations),
                            "selection_mode": mode, "prefer_same_biome": True, "rotate_companions": False}
                self.assertEqual(self.store.load_preferences(), expected)
                self.assertEqual(self.path.read_bytes(), original)
                self.store.save(False)
                self.assertEqual(json.loads(self.path.read_bytes()), {"schema": 4, **expected})
                self.assertEqual(CompanionAutoSummonSettingsStore(self.path).load_preferences(), expected)

    def test_invalid_schema_two_preferences_are_not_repaired_during_migration(self):
        legacy = {"schema": 2, "enabled": False, "locations": [2, 3], "selection_mode": "random"}
        for updates in ({"enabled": 0}, {"locations": [2, 2]}, {"locations": [99]},
                        {"selection_mode": "future"}, {"extra": False}):
            with self.subTest(updates=updates):
                self.assert_invalid_preserved(json.dumps({**legacy, **updates}).encode("utf-8"))

    def test_schema_three_preserves_all_existing_choices_and_disables_new_rotation(self):
        for mode in ("last_manual", "random"):
            for biome in (False, True):
                with self.subTest(mode=mode, biome=biome):
                    legacy = {"schema": 3, "enabled": False, "locations": [14, 2],
                              "selection_mode": mode, "prefer_same_biome": biome}
                    original = json.dumps(legacy).encode("utf-8")
                    self.write_raw(original)
                    expected = {"enabled": False, "locations": [2, 14], "selection_mode": mode,
                                "prefer_same_biome": biome, "rotate_companions": False}
                    self.assertEqual(self.store.load_preferences(), expected)
                    self.assertEqual(self.path.read_bytes(), original)
                    self.store.save(False)
                    self.assertEqual(json.loads(self.path.read_bytes()), {"schema": 4, **expected})

    def test_legacy_documents_cannot_claim_new_mode_or_rotation(self):
        for schema in (2, 3):
            legacy = {"schema": schema, "enabled": True, "locations": [3], "selection_mode": "random"}
            if schema == 3:
                legacy["prefer_same_biome"] = False
            for change in ({"selection_mode": "by_habitat"}, {"rotate_companions": False},
                           {"selection_mode": []}):
                with self.subTest(schema=schema, change=change):
                    self.assert_invalid_preserved(json.dumps({**legacy, **change}).encode("utf-8"))

    def test_schema_four_round_trips_each_mode_and_rotation_without_changing_biome(self):
        for mode in ("last_manual", "random", "by_habitat"):
            for rotation in (False, True):
                with self.subTest(mode=mode, rotation=rotation):
                    preferences = {**self.store.defaults(), "selection_mode": mode,
                                   "rotate_companions": rotation, "prefer_same_biome": False}
                    self.store.save_preferences(preferences)
                    self.assertEqual(CompanionAutoSummonSettingsStore(self.path).load_preferences(), preferences)
                    self.assertEqual(json.loads(self.path.read_bytes()), {"schema": 4, **preferences})

    def test_empty_location_selection_is_valid_and_survives_restart(self):
        preferences = {"enabled": True, "locations": [], "selection_mode": "random", "prefer_same_biome": True, "rotate_companions": False}
        self.store.save_preferences(preferences)
        self.assertEqual(CompanionAutoSummonSettingsStore(self.path).load_preferences(), preferences)

    def test_boolean_compatibility_save_preserves_custom_preferences(self):
        original = {"enabled": True, "locations": [14, 3], "selection_mode": "random", "prefer_same_biome": False, "rotate_companions": False}
        self.store.save_preferences(original)
        self.store.save(False)
        self.assertIs(self.store.load(), False)
        self.assertEqual(self.store.load_preferences(), {
            "enabled": False, "locations": [3, 14], "selection_mode": "random", "prefer_same_biome": False, "rotate_companions": False
        })
        CompanionAutoSummonSettingsStore(self.path).save(True)
        self.assertEqual(self.store.load_preferences(), {
            "enabled": True, "locations": [3, 14], "selection_mode": "random", "prefer_same_biome": False, "rotate_companions": False
        })

    def test_each_load_observes_external_valid_update(self):
        self.store.save(False)
        self.assertIs(self.store.load(), False)
        self.write_raw(b'{"schema":1,"enabled":true}')
        self.assertIs(self.store.load(), True)

    def test_save_revalidates_file_changed_since_load(self):
        self.store.save(True)
        self.assertIs(self.store.load(), True)
        unsupported = b'{"schema":2,"enabled":true}'
        self.write_raw(unsupported)
        with self.assertRaises(SettingsStoreError):
            self.store.save(False)
        self.assertEqual(self.path.read_bytes(), unsupported)

    def test_corrupt_and_invalid_utf8_are_preserved(self):
        for raw in (b"", b"{unfinished", b"\xff\xfe", b'{"schema":1,"enabled":tru}'):
            with self.subTest(raw=raw):
                self.assert_invalid_preserved(raw)

    def test_unknown_schemas_fields_and_wrong_types_are_preserved(self):
        valid = {"schema": 4, **CompanionAutoSummonSettingsStore.defaults()}
        documents = [
            None, [], True, 1,
            {}, {"schema": 1}, {"enabled": True},
            {"schema": 2, "enabled": True},
            {**valid, "schema": 5},
            {**valid, "schema": 2},  # New field cannot silently appear in legacy schema.
            {"schema": True, "enabled": True},
            {"schema": 1.0, "enabled": True},
            {"schema": "1", "enabled": True},
            {"schema": 1, "enabled": 1},
            {"schema": 1, "enabled": 0},
            {"schema": 1, "enabled": "false"},
            {"schema": 1, "enabled": None},
            {"schema": 1, "enabled": True, "future": "preserve"},
            {**valid, "schema": True},
            {**valid, "schema": 2.0},
            {**valid, "future": "preserve"},
            {**valid, "enabled": 1},
        ]
        for locations in (None, True, 2, "2", {}, [True], [False], [2.0], ["2"], [99], [2, 2], [[]]):
            documents.append({**valid, "locations": locations})
        for mode in (None, True, 1, [], {}, "LAST_MANUAL", "", "first"):
            documents.append({**valid, "selection_mode": mode})
        for preference in (None, 1, 0, "true", [], {}):
            documents.append({**valid, "prefer_same_biome": preference})
            documents.append({**valid, "rotate_companions": preference})
        documents.append({key: value for key, value in valid.items() if key != "prefer_same_biome"})
        documents.append({key: value for key, value in valid.items() if key != "rotate_companions"})
        for document in documents:
            with self.subTest(document=document):
                self.assert_invalid_preserved(json.dumps(document).encode("utf-8"))

    def test_duplicate_json_keys_are_rejected_even_when_values_match(self):
        for raw in (
            b'{"schema":1,"schema":1,"enabled":true}',
            b'{"schema":1,"enabled":false,"enabled":true}',
            b'{"schema":2,"enabled":true,"locations":[],"locations":[],"selection_mode":"random"}',
            b'{"schema":2,"enabled":true,"locations":[],"selection_mode":"random","selection_mode":"random"}',
            b'{"schema":3,"enabled":true,"locations":[],"selection_mode":"random","prefer_same_biome":true,"prefer_same_biome":true}',
        ):
            with self.subTest(raw=raw):
                self.assert_invalid_preserved(raw)

    def test_oversized_file_is_preserved(self):
        prefix = b'{"schema":1,"enabled":true}'
        self.assert_invalid_preserved(prefix + b" " * (CompanionAutoSummonSettingsStore.MAX_BYTES + 1))

    def test_exact_size_limit_accepts_valid_document(self):
        prefix = b'{"schema":1,"enabled":false}'
        self.write_raw(prefix + b" " * (CompanionAutoSummonSettingsStore.MAX_BYTES - len(prefix)))
        self.assertIs(self.store.load(), False)
        self.store.save(True)
        self.assertIs(self.store.load(), True)

    def test_invalid_save_argument_is_rejected_before_any_io(self):
        with patch.object(Path, "open", side_effect=AssertionError("unexpected open")):
            for value in (1, 0, "true", "false", None, [], {}):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    self.store.save(value)
        self.assertFalse(self.path.parent.exists())

    def test_invalid_preferences_are_rejected_before_any_io(self):
        valid = CompanionAutoSummonSettingsStore.defaults()
        invalid = [
            None, [], True, 1, {}, {"enabled": True},
            {"schema": 2, **valid}, {**valid, "extra": 0},
            {**valid, "enabled": 1}, {**valid, "enabled": None},
        ]
        for locations in (None, True, 2, "2", {}, (2,), {2}, [True], [False], [2.0], ["2"], [99], [2, 2], [[]]):
            invalid.append({**valid, "locations": locations})
        for mode in (None, True, 1, [], {}, "LAST_MANUAL", "", "first"):
            invalid.append({**valid, "selection_mode": mode})
        for preference in (None, 1, 0, "true", [], {}):
            invalid.append({**valid, "prefer_same_biome": preference})
            invalid.append({**valid, "rotate_companions": preference})
        invalid.append({key: value for key, value in valid.items() if key != "prefer_same_biome"})
        invalid.append({key: value for key, value in valid.items() if key != "rotate_companions"})
        with patch.object(Path, "open", side_effect=AssertionError("unexpected open")), patch.object(
            Path, "mkdir", side_effect=AssertionError("unexpected mkdir")
        ), patch.object(_module.os, "replace", side_effect=AssertionError("unexpected replace")):
            for preferences in invalid:
                with self.subTest(preferences=preferences), self.assertRaises(ValueError):
                    self.store.save_preferences(preferences)
        self.assertFalse(self.path.parent.exists())

    def test_unreadable_existing_file_cannot_be_overwritten(self):
        original = b'{"schema":1,"enabled":false}'
        self.write_raw(original)
        with patch.object(Path, "open", side_effect=PermissionError("test unreadable")):
            with self.assertRaises(SettingsStoreError):
                self.store.load()
            with self.assertRaises(SettingsStoreError):
                self.store.save(True)
        self.assertEqual(self.path.read_bytes(), original)

    def test_atomic_replace_failure_preserves_original_and_removes_temporary(self):
        preferences = {"enabled": False, "locations": [14], "selection_mode": "random", "prefer_same_biome": False, "rotate_companions": False}
        self.store.save_preferences(preferences)
        original = self.path.read_bytes()
        with patch.object(_module.os, "replace", side_effect=OSError("test replace failure")):
            with self.assertRaises(SettingsStoreError):
                self.store.save_preferences(CompanionAutoSummonSettingsStore.defaults())
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])
        self.assertEqual(self.store.load_preferences(), preferences)

    def test_flush_failure_preserves_original_and_removes_temporary(self):
        self.store.save(False)
        original = self.path.read_bytes()
        with patch.object(_module.os, "fsync", side_effect=OSError("test flush failure")):
            with self.assertRaises(SettingsStoreError):
                self.store.save(True)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_first_write_failure_does_not_leave_partial_settings(self):
        with patch.object(_module.os, "replace", side_effect=OSError("test first write failure")):
            with self.assertRaises(SettingsStoreError):
                self.store.save(False)
        self.assertFalse(self.path.exists())
        self.assertEqual(list(self.path.parent.iterdir()), [])
        self.assertIs(self.store.load(), True)

    def test_directory_creation_failure_is_a_store_error(self):
        with patch.object(Path, "mkdir", side_effect=OSError("test mkdir failure")):
            with self.assertRaises(SettingsStoreError):
                self.store.save(False)
        self.assertFalse(self.path.exists())


if __name__ == "__main__":
    unittest.main()
