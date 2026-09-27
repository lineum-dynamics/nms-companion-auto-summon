"""Bridge checks against real production Python code and temporary preferences."""

import builtins
from dataclasses import FrozenInstanceError
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


def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BRIDGE = load_file("cas_preference_bridge_tests", ROOT / "tools/quick_menu_preferences.py")
HARNESS = load_file("cas_preference_runtime_harness", ROOT / "tests/test_runtime.py")


class BridgeFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cas-preference-bridge-")
        self.addCleanup(temporary.cleanup)
        self.data_path = Path(temporary.name)
        # The existing harness compiles production sources with fake framework
        # decorators. No native declaration can execute. These metadata fields
        # model the real loader's module registration without invoking it.
        self.module = HARNESS.load_runtime()
        self.production_path = str(ROOT / "CompanionAutoSummon.py")
        self.module.__name__ = "CompanionAutoSummon"
        self.module.__file__ = self.production_path
        self.module.CompanionAutoSummon.__module__ = "CompanionAutoSummon"
        self.module.CompanionAutoSummon._disabled = False
        self.module.LOGGER = Mock()
        with patch.dict(os.environ, {"LOCALAPPDATA": temporary.name}):
            self.mod = self.module.CompanionAutoSummon()
        self.mod._abc_initialised = True
        self.registry = {"CompanionAutoSummon": self.mod}
        self.modules = {"CompanionAutoSummon": self.module}
        self.bridge = self.make_bridge()

    def make_bridge(self):
        return BRIDGE.PreferenceBridge(
            self.production_path,
            get_registered=lambda: self.registry.get("CompanionAutoSummon"),
            get_module=lambda: self.modules.get("CompanionAutoSummon"),
        )


class IdentityAndSnapshotTests(BridgeFixture):
    def test_snapshot_is_owned_immutable_and_preserves_actual_runtime(self):
        snapshot = self.bridge.snapshot()
        self.assertEqual(snapshot, BRIDGE.PreferenceState(True, True, False, True, False))
        self.assertFalse(hasattr(snapshot, "__dict__") and "instance" in snapshot.__dict__)
        with self.assertRaises(FrozenInstanceError):
            snapshot.applied = False
        self.assertIs(self.registry["CompanionAutoSummon"], self.mod)
        self.assertEqual(self.mod.requested_preferences, {})

    def test_snapshot_distinguishes_applied_desired_pending_and_session_only(self):
        self.mod.automatic_summoning = False
        self.mod.settings_ok = False
        self.assertEqual(self.bridge.snapshot(), BRIDGE.PreferenceState(True, False, True, False, False))
        self.assertTrue(self.mod.auto_enabled)

    def test_stopped_runtime_remains_readable_but_cannot_capture_or_commit(self):
        token = self.bridge.capture_toggle()
        self.mod.enabled = False
        self.assertTrue(self.bridge.snapshot().stopped)
        self.assertIsNone(self.bridge.capture_toggle())
        self.assertFalse(self.bridge.commit_toggle(token))
        self.assertEqual(self.mod.requested_preferences, {})

    def test_absent_initial_registry_can_become_ready_without_instantiation(self):
        self.registry.clear()
        self.assertIsNone(self.bridge.snapshot())
        self.assertIsNone(self.bridge.capture_toggle())
        self.registry["CompanionAutoSummon"] = self.mod
        self.assertIsNotNone(self.bridge.snapshot())

    def test_replaced_or_removed_bound_runtime_permanently_refuses(self):
        for replacement in (None, object.__new__(type(self.mod))):
            with self.subTest(replacement=replacement is None):
                bridge = self.make_bridge()
                token = bridge.capture_toggle()
                if replacement is None:
                    self.registry.clear()
                else:
                    replacement.__dict__.update(self.mod.__dict__)
                    self.registry["CompanionAutoSummon"] = replacement
                self.assertFalse(bridge.commit_toggle(token))
                self.registry["CompanionAutoSummon"] = self.mod
                self.assertIsNone(bridge.snapshot())
                self.assertEqual(self.mod.requested_preferences, {})

    def test_wrong_module_class_path_version_or_disabled_contract_is_unavailable(self):
        cases = (
            (self.module, "__name__", "Other"),
            (self.module, "__file__", str(ROOT / "Elsewhere.py")),
            (self.module, "EXPECTED_PYMHF", "0.2.3"),
            (self.module, "EXPECTED_EXE_SHA256", "another-build"),
            (self.module, "CompanionAutoSummon", object),
            (type(self.mod), "_disabled", True),
            (self.mod, "_abc_initialised", False),
            (type(self.mod), "__init__", lambda self: None),
        )
        for owner, name, value in cases:
            with self.subTest(field=name), patch.object(owner, name, value):
                self.assertIsNone(self.make_bridge().snapshot())

    def test_no_lookups_or_io_during_bridge_construction(self):
        registered, module = Mock(), Mock()
        with patch.object(builtins, "open", side_effect=AssertionError("No file I/O")), \
                patch.object(Path, "open", side_effect=AssertionError("No file I/O")):
            BRIDGE.PreferenceBridge(self.production_path, get_registered=registered, get_module=module)
        registered.assert_not_called()
        module.assert_not_called()
        with self.assertRaises(ValueError):
            BRIDGE.PreferenceBridge("relative.py", get_registered=registered, get_module=module)


class ToggleTests(BridgeFixture):
    def test_capture_does_not_queue_and_commit_queues_once_without_apply(self):
        queue = self.mod.requested_preferences
        token = self.bridge.capture_toggle()
        self.assertEqual(queue, {})
        self.assertTrue(self.bridge.commit_toggle(token))
        self.assertIs(self.mod.requested_preferences, queue)
        self.assertEqual(queue, {"enabled": False})
        self.assertTrue(self.mod.auto_enabled)
        self.assertFalse(self.bridge.commit_toggle(token))
        self.assertIsNone(token._instance)
        self.assertIsNone(token._queue)
        self.assertFalse(list(self.data_path.rglob("*.json")))

    def test_toggle_inverts_current_visible_pending_value_not_applied_value(self):
        self.mod.automatic_summoning = False
        token = self.bridge.capture_toggle()
        self.assertTrue(self.bridge.commit_toggle(token))
        self.assertEqual(self.mod.requested_preferences, {"enabled": True})
        self.assertTrue(self.mod.auto_enabled)

    def test_newer_gui_enabled_request_refuses_old_capture(self):
        token = self.bridge.capture_toggle()
        self.mod.automatic_summoning = False
        self.assertFalse(self.bridge.commit_toggle(token))
        self.assertEqual(self.mod.requested_preferences, {"enabled": False})
        self.assertFalse(self.bridge.commit_toggle(token))

    def test_new_identical_enabled_request_is_still_detected_by_key_presence(self):
        token = self.bridge.capture_toggle()
        self.mod.automatic_summoning = True
        self.assertFalse(self.bridge.commit_toggle(token))
        self.assertEqual(self.mod.requested_preferences, {"enabled": True})

    def test_unrelated_gui_requests_survive_and_do_not_prevent_toggle(self):
        token = self.bridge.capture_toggle()
        self.mod.planets = False
        self.mod.companion_selection = self.module.SelectionMode("random")
        self.assertTrue(self.bridge.commit_toggle(token))
        self.assertEqual(self.mod.requested_preferences,
                         {"planets": False, "selection_mode": "random", "enabled": False})

    def test_applied_or_replaced_queue_invalidates_capture_even_when_values_match(self):
        token = self.bridge.capture_toggle()
        self.mod.automatic_summoning = True
        self.mod._apply_control()  # A real no-op apply still replaces the queue.
        self.assertFalse(self.bridge.commit_toggle(token))
        self.assertTrue(self.mod.auto_enabled)
        self.assertEqual(self.mod.requested_preferences, {})

    def test_foreign_or_non_token_cannot_commit(self):
        token = self.bridge.capture_toggle()
        self.assertFalse(self.make_bridge().commit_toggle(token))
        self.assertFalse(self.bridge.commit_toggle(token))
        for invalid in (None, True, object()):
            self.assertFalse(self.bridge.commit_toggle(invalid))
        self.assertEqual(self.mod.requested_preferences, {})

    def test_busy_control_lock_never_blocks_or_unlocks_another_owner(self):
        token = self.bridge.capture_toggle()
        self.mod.control_lock.acquire()
        try:
            self.assertIsNone(self.bridge.snapshot())
            self.assertIsNone(self.bridge.capture_toggle())
            self.assertFalse(self.bridge.commit_toggle(token))
            self.assertTrue(self.mod.control_lock.locked())
        finally:
            self.mod.control_lock.release()
        self.assertFalse(self.bridge.commit_toggle(token))
        self.assertEqual(self.mod.requested_preferences, {})

    def test_bridge_contention_and_lookup_exception_do_not_mutate_preferences(self):
        token = self.bridge.capture_toggle()
        self.bridge._lock.acquire()
        try:
            self.assertIsNone(self.bridge.snapshot())
            self.assertFalse(self.bridge.commit_toggle(token))
        finally:
            self.bridge._lock.release()
        with patch.object(self.bridge, "_get_module", side_effect=RuntimeError("Unavailable")):
            self.assertIsNone(self.bridge.snapshot())
        self.assertEqual(self.mod.requested_preferences, {})
        self.assertFalse(self.mod.control_lock.locked())

    def test_registry_change_during_final_check_refuses_without_queue_write(self):
        token = self.bridge.capture_toggle()
        calls = 0

        def changing_lookup():
            nonlocal calls
            calls += 1
            return self.mod if calls == 1 else None

        with patch.object(self.bridge, "_get_registered", side_effect=changing_lookup):
            self.assertFalse(self.bridge.commit_toggle(token))
        self.assertEqual(self.mod.requested_preferences, {})

    def test_revocation_during_final_lookup_refuses_and_consumes_token(self):
        token = self.bridge.capture_toggle()
        authorized = True
        calls = 0

        def revoking_lookup():
            nonlocal authorized, calls
            calls += 1
            if calls == 2:
                authorized = False
            return self.mod

        with patch.object(self.bridge, "_get_registered", side_effect=revoking_lookup):
            self.assertFalse(self.bridge.commit_toggle(token, authorize=lambda: authorized))
        self.assertEqual(calls, 2)
        self.assertEqual(self.mod.requested_preferences, {})
        self.assertFalse(self.bridge.commit_toggle(token))
        self.assertIsNone(token._instance)

    def test_final_authorization_runs_under_both_locks_and_requires_literal_true(self):
        for decision in (False, None, 1, True):
            with self.subTest(decision=repr(decision)):
                token = self.bridge.capture_toggle()
                observed = []

                def authorize():
                    observed.append((self.bridge._lock.locked(), self.mod.control_lock.locked(),
                                     dict(self.mod.requested_preferences)))
                    return decision

                self.assertIs(self.bridge.commit_toggle(token, authorize=authorize), decision is True)
                self.assertEqual(observed, [(True, True, {})])
                self.assertEqual(self.mod.requested_preferences,
                                 {"enabled": False} if decision is True else {})

    def test_authorization_exception_refuses_consumes_and_releases_locks(self):
        token = self.bridge.capture_toggle()
        predicate = Mock(side_effect=RuntimeError("Authorization unavailable"))
        self.assertFalse(self.bridge.commit_toggle(token, authorize=predicate))
        predicate.assert_called_once_with()
        self.assertFalse(self.bridge.commit_toggle(token))
        self.assertEqual(self.mod.requested_preferences, {})
        self.assertFalse(self.bridge._lock.locked())
        self.assertFalse(self.mod.control_lock.locked())
        self.assertIsNone(token._instance)

    def test_snapshot_and_commit_do_not_open_files_apply_or_call_setter(self):
        with patch.object(builtins, "open", side_effect=AssertionError("No file I/O")), \
                patch.object(Path, "open", side_effect=AssertionError("No file I/O")), \
                patch.object(self.mod, "_apply_control", side_effect=AssertionError("No apply")), \
                patch.object(self.mod, "_queue_preference", side_effect=AssertionError("No nested setter lock")):
            self.assertIsNotNone(self.bridge.snapshot())
            self.assertTrue(self.bridge.commit_toggle(self.bridge.capture_toggle()))

    def test_production_apply_persists_one_queue_and_cancels_existing_intent(self):
        self.mod.policy.remember(5)
        self.mod.policy.eject(0.0)
        self.mod._load_summon_pending = True
        self.mod.planets = False
        original_store = self.mod.settings_store
        self.assertTrue(self.bridge.commit_toggle(self.bridge.capture_toggle()))
        self.assertTrue(self.mod.policy.pending)
        self.assertTrue(self.mod._load_summon_pending)
        self.assertFalse(list(self.data_path.rglob("*.json")))
        self.mod._apply_control()  # Same production method called by local Player.Update.
        self.assertIs(self.mod.settings_store, original_store)
        self.assertFalse(self.mod.auto_enabled)
        self.assertFalse(self.mod.policy.pending)
        self.assertFalse(self.mod._load_summon_pending)
        self.assertEqual(self.mod.policy.last_slot, 5)
        stored = json.loads((self.data_path / "NMS-AutoPet/settings.json").read_text())
        self.assertFalse(stored["enabled"])
        self.assertEqual(stored["locations"], [2, 14])
        self.assertEqual(self.mod.pending_notice, "Companion Auto Summon: OFF")

    def test_session_only_runtime_accepts_toggle_without_repairing_or_replacing_store(self):
        self.mod.settings_ok = False
        store = self.mod.settings_store
        self.assertTrue(self.bridge.commit_toggle(self.bridge.capture_toggle()))
        self.mod._apply_control()
        self.assertFalse(self.mod.auto_enabled)
        self.assertIs(self.mod.settings_store, store)
        self.assertEqual(self.mod.pending_notice, "Companion Auto Summon: OFF (session only)")
        self.assertFalse(list(self.data_path.rglob("*.json")))


if __name__ == "__main__":
    unittest.main()
