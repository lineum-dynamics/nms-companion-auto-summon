"""Confirmation-gated menu tests using owned memory and fake framework hooks."""

import ctypes
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from test_quick_menu_item import ITEM
from test_quick_menu_order_trial import OrderFixture, load_trial
from test_quick_menu_preferences import HARNESS


class ToggleMetadataTests(unittest.TestCase):
    def test_disabled_trial_with_toggle_metadata_has_no_io_or_native_initialization(self):
        module = load_trial(settings_enabled=True)
        self.assertEqual(module.test_events, [("class", True)])
        with patch.object(module, "current_process_io") as io_factory, patch.object(
                module, "native_adapters") as native_factory, patch.object(
                module, "PreferenceBridge") as bridge_factory:
            trial = module.CompanionMenuOrderTrial()
        self.assertTrue(trial._abc_initialised)
        self.assertTrue(trial._stopped)
        self.assertEqual(len(trial.hooks), 8)
        self.assertEqual(trial._gui_widgets, [])
        self.assertEqual(trial._hotkey_funcs, [])
        io_factory.assert_not_called()
        native_factory.assert_not_called()
        bridge_factory.assert_not_called()
        module.ensure_guard.assert_not_called()

    def test_confirmation_adds_one_bool_target_and_two_observer_callbacks(self):
        module = load_trial(settings_enabled=True)
        actual = {entry.offset: list(entry.function.__annotations__.values())
                  for entry in module.test_declarations}
        self.assertEqual(actual, {
            0x151ED00: [ctypes.c_void_p, ctypes.c_void_p, None],
            0x1523220: [ctypes.c_void_p, ctypes.c_void_p, None],
            0x1526940: [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool, ctypes.c_bool],
            0x1533980: [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p],
            0x15311C0: [ctypes.c_void_p, ctypes.c_bool],
        })
        for name, phase in (("before_confirmation", "before"), ("after_confirmation", "after")):
            callback = getattr(module.CompanionMenuOrderTrial, name)
            self.assertEqual(callback._test_hook_time, phase)
            self.assertEqual(callback._test_hook_offset, 0x15311C0)
        self.assertEqual(module.CompanionMenuOrderTrial._version, "0.7.0-toggle-trial")

    def test_enabled_initialization_uses_registered_production_lookup_without_instantiation(self):
        module = load_trial(enabled=True, settings_enabled=True)
        bridge = Mock()
        with patch.object(module, "current_process_io", return_value=(Mock(), Mock(), Mock())), \
                patch.object(module, "native_adapters", return_value=(Mock(), Mock(), Mock())), \
                patch.object(module, "ensure_guard", return_value=Mock()), \
                patch.object(module, "PreferenceBridge", return_value=bridge) as factory:
            trial = module.CompanionMenuOrderTrial()
        self.assertFalse(trial._stopped)
        self.assertIs(trial._preferences, bridge)
        args, kwargs = factory.call_args
        self.assertEqual(args, (str(Path(module.__file__).absolute().with_name("CompanionAutoSummon.py")),))
        self.assertIsNone(kwargs["get_registered"]())
        sentinel = object()
        module.mod_manager.mods["CompanionAutoSummon"] = sentinel
        self.assertIs(kwargs["get_registered"](), sentinel)
        bridge.assert_not_called()


class ToggleFixture(OrderFixture):
    settings_enabled = True

    def setUp(self):
        super().setUp()
        temporary = tempfile.TemporaryDirectory(prefix="cas-toggle-adapter-")
        self.addCleanup(temporary.cleanup)
        self.data_path = Path(temporary.name)
        self.production = HARNESS.load_runtime()
        self.production.__name__ = "CompanionAutoSummon"
        self.production.__file__ = str(Path(self.module.__file__).with_name("CompanionAutoSummon.py"))
        self.production.CompanionAutoSummon.__module__ = "CompanionAutoSummon"
        self.production.CompanionAutoSummon._disabled = False
        self.production.LOGGER = Mock()
        with patch.dict(os.environ, {"LOCALAPPDATA": temporary.name}):
            self.production_mod = self.production.CompanionAutoSummon()
        self.production_mod._abc_initialised = True
        self.registry = {"CompanionAutoSummon": self.production_mod}
        self.trial._preferences = self.module.PreferenceBridge(
            self.production.__file__,
            get_registered=lambda: self.registry.get("CompanionAutoSummon"),
            get_module=lambda: self.production,
        )

    def prepare_child(self):
        self.prepare_parent()
        self.assertIsNone(self.before())
        self.assertIsNone(self.after(False))
        self.assertFalse(self.trial._stopped)
        self.child = self.vector(2)[0]
        self.trial._write_field.reset_mock()
        self.trial._select_first.reset_mock()
        self.trial._writer.reset_mock()
        return self.child

    def observe(self, result, *, menu=None):
        menu = self.menu if menu is None else menu
        self.assertIsNone(self.trial.before_confirmation(menu))
        self.assertIsNone(self.trial.after_confirmation(menu, result))

    def fresh_press(self):
        self.observe(False)
        self.observe(True)

    def trigger_child(self, result=False):
        self.assertIsNone(self.before(self.child))
        self.assertIsNone(self.after(result, action=self.child))

    def memory_snapshot(self):
        return {address: bytes(data) for address, data in self.regions.items()}

    def assert_no_request(self):
        self.assertEqual(self.production_mod.requested_preferences, {})
        self.assertTrue(self.production_mod.auto_enabled)
        self.assert_no_transition()
        self.assertFalse(list(self.data_path.rglob("*.json")))


class ConfirmationTests(ToggleFixture):
    def test_initial_true_without_observed_release_never_queues(self):
        self.prepare_child()
        self.observe(True)
        self.trigger_child()
        self.assert_no_request()
        self.assertFalse(self.trial._stopped)

    def test_one_fresh_press_queues_once_only_after_native_false_without_native_writes(self):
        self.prepare_child()
        before = self.memory_snapshot()
        self.fresh_press()
        self.assertEqual(self.production_mod.requested_preferences, {})
        self.assertIsNone(self.before(self.child))
        self.assertEqual(self.production_mod.requested_preferences, {})
        self.assertIsNone(self.after(False, action=self.child))
        self.assertEqual(self.production_mod.requested_preferences, {"enabled": False})
        self.assertTrue(self.production_mod.auto_enabled)
        self.assertEqual(self.memory_snapshot(), before)
        self.assert_no_transition()
        self.trial._writer.assert_not_called()
        self.assertFalse(list(self.data_path.rglob("*.json")))
        # A tail/selection dispatch carries no new confirmation capability.
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences, {"enabled": False})
        self.assertFalse(self.trial._stopped)

    def test_parent_confirmation_held_across_open_does_not_toggle_child(self):
        self.prepare_parent()
        self.fresh_press()
        self.assertIsNone(self.before())
        self.assertIsNone(self.after(False))
        self.child = self.vector(2)[0]
        self.trial._write_field.reset_mock()
        self.trial._select_first.reset_mock()
        self.observe(True)
        self.trigger_child()
        self.assert_no_request()
        self.fresh_press()
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences, {"enabled": False})

    def test_held_true_and_repeated_native_dispatch_do_not_reverse_pending_choice(self):
        self.prepare_child()
        self.fresh_press()
        self.trigger_child()
        for _ in range(3):
            self.observe(True)
            self.trigger_child()
            self.assertEqual(self.production_mod.requested_preferences, {"enabled": False})
        self.assertFalse(self.trial._stopped)
        self.fresh_press()
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences, {"enabled": True})

    def test_tail_or_navigation_dispatch_with_no_confirmation_stays_inert(self):
        self.prepare_child()
        before = self.memory_snapshot()
        for native_result in (False, True):
            self.trigger_child(native_result)
        self.assert_no_request()
        self.assertEqual(self.memory_snapshot(), before)
        self.assertFalse(self.trial._stopped)

    def test_repeated_after_consumes_no_second_preference_request(self):
        self.prepare_child()
        self.fresh_press()
        self.trigger_child()
        self.assertIsNone(self.after(False, action=self.child))
        self.assertEqual(self.production_mod.requested_preferences, {"enabled": False})
        self.assertTrue(self.trial._stopped)
        self.assert_guard_retained()

    def test_native_true_on_authenticated_child_is_preserved_and_refuses_toggle(self):
        self.prepare_child()
        self.fresh_press()
        self.trigger_child(True)
        self.assert_no_request()
        self.assertTrue(self.trial._stopped)
        self.assert_guard_retained()

    def test_intervening_label_builder_or_false_predicate_consumes_intent(self):
        for intervening in ("label", "builder", "false"):
            with self.subTest(intervening=intervening):
                self.setUp()
                self.prepare_child()
                self.fresh_press()
                if intervening == "label":
                    self.assertIsNone(self.label())
                elif intervening == "builder":
                    self.assertIsNone(self.builder())
                else:
                    self.observe(False)
                self.trigger_child()
                self.assert_no_request()

    def test_changed_selected_index_or_marker_refuses_captured_confirmation(self):
        for change in ("selection", "marker"):
            with self.subTest(change=change):
                self.setUp()
                self.prepare_child()
                self.fresh_press()
                if change == "selection":
                    self.set_integer(ITEM.SELECTIONS_OFFSET + 8, -1, signed=True)
                else:
                    self.regions[self.child][ITEM.MARKER_OFFSET] ^= 1
                self.trigger_child()
                self.assert_no_request()

    def test_other_menu_trigger_consumes_intent_without_reusing_it_on_original_menu(self):
        self.prepare_child()
        self.fresh_press()
        other = self.menu + 0x200000
        self.regions[other] = bytearray(self.regions[self.menu])
        self.assertIsNone(self.trial.before_trigger(other, self.child, True))
        self.assertIsNone(self.trial.after_trigger(other, self.child, True, False))
        self.trigger_child()
        self.assert_no_request()
        self.assertFalse(self.trial._stopped)

    def test_release_seen_only_on_another_menu_does_not_authorize_child(self):
        self.prepare_child()
        self.observe(False, menu=self.menu + 0x200000)
        self.observe(True)
        self.trigger_child()
        self.assert_no_request()
        self.assertFalse(self.trial._stopped)
        self.fresh_press()
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences, {"enabled": False})

    def test_thread_change_refuses_intent_and_keeps_native_guard(self):
        self.prepare_child()
        self.fresh_press()
        self.module.get_native_id.return_value += 1
        self.trigger_child()
        self.assert_no_request()
        self.assertTrue(self.trial._stopped)
        self.assert_guard_retained()

    def test_missing_mismatched_or_non_boolean_predicate_completion_stops(self):
        for mismatch in ("missing", "menu", "type"):
            with self.subTest(mismatch=mismatch):
                self.setUp()
                self.prepare_child()
                if mismatch != "missing":
                    self.assertIsNone(self.trial.before_confirmation(self.menu))
                menu = self.menu + 16 if mismatch == "menu" else self.menu
                result = 1 if mismatch == "type" else True
                self.assertIsNone(self.trial.after_confirmation(menu, result))
                self.trigger_child()
                self.assert_no_request()
                self.assertTrue(self.trial._stopped)
                self.assert_guard_retained()

    def test_nested_callback_between_predicate_pair_stops_without_latched_intent(self):
        self.prepare_child()
        self.assertIsNone(self.trial.before_confirmation(self.menu))
        self.assertIsNone(self.label())
        self.assertIsNone(self.trial.after_confirmation(self.menu, True))
        self.trigger_child()
        self.assert_no_request()
        self.assertTrue(self.trial._stopped)
        self.assert_guard_retained()

    def test_change_during_native_trigger_revalidates_without_reading_old_action(self):
        self.prepare_child()
        self.fresh_press()
        self.assertIsNone(self.before(self.child))
        replacement = self.child + 0x500000
        self.regions[replacement] = self.regions.pop(self.child)
        pointer_offset = ITEM.VECTORS_OFFSET + 2 * ITEM.VECTOR_SIZE + 8
        self.regions[self.menu][pointer_offset:pointer_offset + 8] = replacement.to_bytes(8, "little")
        self.set_integer(ITEM.SELECTIONS_OFFSET + 8, -1, signed=True)
        self.reads.clear()
        self.assertIsNone(self.after(False, action=self.child))
        self.assert_no_request()
        self.assertTrue(self.trial._stopped)
        self.assertFalse(any(self.child <= address < self.child + ITEM.ITEM_SIZE
                             for address, size in self.reads))
        self.assert_guard_retained()

    def test_identical_relocated_child_uses_fresh_storage_after_native_return(self):
        self.prepare_child()
        self.fresh_press()
        self.assertIsNone(self.before(self.child))
        replacement = self.child + 0x500000
        self.regions[replacement] = self.regions.pop(self.child)
        pointer_offset = ITEM.VECTORS_OFFSET + 2 * ITEM.VECTOR_SIZE + 8
        self.regions[self.menu][pointer_offset:pointer_offset + 8] = replacement.to_bytes(8, "little")
        self.reads.clear()
        self.assertIsNone(self.after(False, action=self.child))
        self.assertEqual(self.production_mod.requested_preferences, {"enabled": False})
        self.assertFalse(self.trial._stopped)
        self.assertFalse(any(self.child <= address < self.child + ITEM.ITEM_SIZE
                             for address, size in self.reads))
        self.assert_no_transition()

    def test_stopping_during_final_deferred_selection_read_prevents_commit(self):
        self.prepare_child()
        self.fresh_press()
        self.assertIsNone(self.before(self.child))
        original_reader = self.trial._reader

        def stop_during_read(address, size):
            result = original_reader(address, size)
            if (address, size) == (self.menu + self.module.PENDING_SELECTION_OFFSET, 1):
                self.trial._stop("synthetic_final_read_stop")
            return result

        self.trial._reader = stop_during_read
        self.assertIsNone(self.after(False, action=self.child))
        self.assert_no_request()
        self.assertTrue(self.trial._stopped)
        self.assert_guard_retained()

    def test_stop_at_bridge_commit_boundary_refuses_real_preference_queue_write(self):
        self.prepare_child()
        self.fresh_press()
        commit = self.trial._preferences.commit_toggle

        def stop_then_commit(token, *, authorize):
            self.trial._stop("synthetic_commit_boundary_stop")
            self.assertIs(authorize(), False)
            return commit(token, authorize=authorize)

        self.trial._preferences.commit_toggle = Mock(side_effect=stop_then_commit)
        self.trigger_child()
        self.trial._preferences.commit_toggle.assert_called_once()
        self.assert_no_request()
        self.assertTrue(self.trial._stopped)
        self.assert_guard_retained()

    def test_newer_gui_request_between_confirmation_and_completion_is_preserved(self):
        self.prepare_child()
        self.fresh_press()
        self.production_mod.automatic_summoning = False
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences, {"enabled": False})
        self.assertTrue(self.production_mod.auto_enabled)
        self.assertFalse(self.trial._stopped)
        self.assert_no_transition()


class LabelAndAvailabilityTests(ToggleFixture):
    def test_dynamic_labels_report_desired_pending_session_only_stopped_and_unavailable(self):
        self.prepare_child()
        states = (
            (True, {}, True, True, b"Automatic summoning: ON"),
            (False, {}, True, True, b"Automatic summoning: OFF"),
            (True, {"enabled": False}, True, True, b"Automatic summoning: OFF (pending)"),
            (False, {}, False, True, b"Automatic summoning: OFF (session only)"),
            (True, {}, True, False, b"Automatic summoning: stopped"),
        )
        for enabled, queue, saved, running, label in states:
            with self.subTest(label=label):
                self.production_mod.auto_enabled = enabled
                self.production_mod.requested_preferences = queue
                self.production_mod.settings_ok = saved
                self.production_mod.enabled = running
                self.trial._writer.reset_mock()
                self.assertIsNone(self.label())
                self.trial._writer.assert_called_once_with(self.output, label)
        self.registry.clear()
        self.trial._writer.reset_mock()
        self.assertIsNone(self.label())
        self.trial._writer.assert_called_once_with(self.output, b"Automatic summoning: unavailable")
        self.assert_no_transition()

    def test_parent_retains_title_and_vanilla_pet_caption_is_untouched(self):
        self.prepare_parent()
        self.assertIsNone(self.label())
        self.trial._writer.assert_called_once_with(self.output, b"Companion Auto Summon")
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 1)
        self.trial._writer.reset_mock()
        self.assertIsNone(self.label())
        self.trial._writer.assert_not_called()
        self.assert_no_request()

    def test_unavailable_or_stopped_production_never_yields_toggle_capability(self):
        for reason in ("unavailable", "stopped"):
            with self.subTest(reason=reason):
                self.setUp()
                self.prepare_child()
                if reason == "unavailable":
                    self.registry.clear()
                else:
                    self.production_mod.enabled = False
                self.fresh_press()
                self.trigger_child()
                self.assert_no_request()
                self.assertFalse(self.trial._stopped)

    def test_native_deferred_selection_or_revoked_guard_blocks_authenticated_toggle(self):
        for reason in ("pending", "guard"):
            with self.subTest(reason=reason):
                self.setUp()
                self.prepare_child()
                self.fresh_press()
                self.assertIsNone(self.before(self.child))
                if reason == "pending":
                    self.regions[self.menu][self.module.PENDING_SELECTION_OFFSET] = 1
                else:
                    self.guard.authorize_append.side_effect = None
                    self.guard.authorize_append.return_value = False
                self.assertIsNone(self.after(False, action=self.child))
                self.assert_no_request()
                self.assertTrue(self.trial._stopped)
                self.assert_guard_retained()


if __name__ == "__main__":
    unittest.main()
