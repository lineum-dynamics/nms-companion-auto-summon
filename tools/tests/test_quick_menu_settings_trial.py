"""Full settings-page integration using owned menu buffers and temporary data."""

import ctypes
import sys
import unittest
from unittest.mock import Mock, patch

from test_quick_menu_item import ITEM
from test_quick_menu_order_trial import load_trial
from test_quick_menu_toggle_trial import ToggleFixture


class SettingsFixture(ToggleFixture):
    extended_settings = True

    def prepare_parent(self):
        self.assertIsNone(self.begin())
        self.pet = self.incoming()
        self.pet_before = bytes(self.regions[self.pet])
        self.assertEqual(self.native_pet_append(self.pet), 0x7770000)
        self.assertIsNone(self.finish())
        self.assertFalse(self.trial._stopped)
        self.assertEqual(self.native_errors, [])
        self.assertEqual(self.vector(1)[1], 2)
        self.assertEqual(self.vector(2)[1], 7)
        self.parent = self.vector(1)[0]
        return self.parent

    def select_role(self, role):
        self.set_integer(ITEM.SELECTIONS_OFFSET + 8, role)
        self.child = self.vector(2)[0] + role * ITEM.ITEM_SIZE
        return self.child

    def expected_label(self, value):
        self.trial._writer.reset_mock()
        self.assertIsNone(self.label())
        self.trial._writer.assert_called_once_with(self.output, value)
        self.assertFalse(self.trial._stopped)


class FullPageTests(SettingsFixture):
    def test_all_seven_unique_roles_are_created_before_preserved_native_pet(self):
        self.prepare_child()
        pointer, count = self.vector(2)
        self.assertEqual(count, 7)
        for role in range(7):
            data = self.reader(pointer + role * ITEM.ITEM_SIZE, ITEM.ITEM_SIZE)
            self.assertEqual(data[ITEM.MARKER_OFFSET:ITEM.MARKER_OFFSET + 16], ITEM.CUSTOM_ACTION_MARKER)
            self.assertEqual(int.from_bytes(data[ITEM.SLOT_OFFSET:ITEM.SLOT_OFFSET + 4], "little", signed=True), role)
            self.assertEqual(int.from_bytes(data[ITEM.ACTION_OFFSET:ITEM.ACTION_OFFSET + 4], "little"), 0)
        self.assertEqual(self.reader(self.parent + ITEM.ITEM_SIZE, ITEM.ITEM_SIZE), self.pet_before)
        self.assertEqual(bytes(self.regions[self.pet]), self.pet_before)
        self.assertEqual(len(self.native_calls), 9)  # Parent, original pet, seven children.
        self.assert_no_request()

    def test_rebuild_reuses_complete_page_without_duplicate_children(self):
        self.prepare_child()
        before = self.memory_snapshot()
        count = len(self.native_calls)
        self.assertIsNone(self.builder())
        self.assertFalse(self.trial._stopped)
        self.assertEqual(len(self.native_calls), count)
        self.assertEqual(self.memory_snapshot(), before)

    def test_each_role_reports_applied_then_pending_then_applied_state(self):
        cases = (
            (0, "enabled", False, b"Automatic summoning: ON", b"Automatic summoning: OFF"),
            (1, "selection_mode", "last_manual", b"Selection: By habitat", b"Selection: Last selected"),
            (2, "prefer_same_biome", False, b"Random: prefer matching biome: ON", b"Random: prefer matching biome: OFF"),
            (3, "planets", False, b"Planets: ON", b"Planets: OFF"),
            (4, "space_stations", False, b"Space stations: ON", b"Space stations: OFF"),
            (5, "nexus", False, b"Space Anomaly: ON", b"Space Anomaly: OFF"),
            (6, "rotate_companions", False, b"Shuffle companions: ON", b"Shuffle companions: OFF"),
        )
        for role, key, desired, applied_label, desired_label in cases:
            with self.subTest(role=role):
                self.setUp()
                self.prepare_child()
                self.select_role(role)
                self.expected_label(applied_label)
                before = self.memory_snapshot()
                self.fresh_press()
                self.trigger_child()
                self.assertEqual(self.production_mod.requested_preferences, {key: desired})
                self.assertEqual(self.memory_snapshot(), before)
                self.assert_no_transition()
                self.assertFalse(list(self.data_path.rglob("*.json")))
                self.expected_label(desired_label + b" (pending)")
                self.production_mod._apply_control()
                self.assertEqual(self.production_mod.requested_preferences, {})
                self.expected_label(desired_label)
                self.assertTrue(list(self.data_path.rglob("*.json")))

    def test_changed_selection_between_confirmation_and_trigger_cannot_toggle_other_setting(self):
        self.prepare_child()
        self.select_role(1)
        self.fresh_press()
        self.select_role(2)
        self.trigger_child()
        self.assert_no_request()
        self.assertFalse(self.trial._stopped)

    def test_changed_selection_during_native_action_refuses_commit_and_preserves_result(self):
        self.prepare_child()
        action = self.select_role(4)
        self.fresh_press()
        self.assertIsNone(self.before(action))
        self.select_role(5)
        self.assertIsNone(self.after(False, action=action))
        self.assert_no_request()
        self.assertTrue(self.trial._stopped)
        self.assert_guard_retained()

    def test_selection_mode_requires_new_release_and_confirmation_for_each_change(self):
        self.prepare_child()
        self.select_role(1)
        self.observe(True)
        self.trigger_child()
        self.assert_no_request()
        self.expected_label(b"Selection: By habitat")
        for mode, caption in (("last_manual", b"Last selected"), ("random", b"Random"),
                              ("by_habitat", b"By habitat")):
            self.fresh_press()
            self.trigger_child()
            self.assertEqual(self.production_mod.requested_preferences, {"selection_mode": mode})
            self.expected_label(b"Selection: " + caption + b" (pending)")
            for _ in range(3):
                self.observe(True)
                self.trigger_child()
            self.assertEqual(self.production_mod.requested_preferences, {"selection_mode": mode})
        self.production_mod._apply_control()
        self.expected_label(b"Selection: By habitat")
        self.assert_no_transition()

    def test_parent_held_confirmation_does_not_change_first_setting(self):
        self.prepare_parent()
        self.fresh_press()
        self.assertIsNone(self.before())
        self.assertIsNone(self.after(False))
        self.select_role(0)
        self.trial._write_field.reset_mock()
        self.trial._select_first.reset_mock()
        self.observe(True)
        self.trigger_child()
        self.assert_no_request()

    def test_off_and_on_apply_without_touching_other_preferences_or_menu_bytes(self):
        self.prepare_child()
        before = self.memory_snapshot()
        original = self.production_mod._current_preferences()
        for enabled in (False, True):
            self.fresh_press()
            self.trigger_child()
            self.assertEqual(self.production_mod.requested_preferences, {"enabled": enabled})
            self.production_mod._apply_control()
            self.assertEqual(self.production_mod._current_preferences(), {**original, "enabled": enabled})
            self.assertEqual(self.memory_snapshot(), before)
            self.assert_no_transition()

    def test_each_role_stays_inert_for_navigation_and_preserves_native_true(self):
        self.prepare_child()
        before = self.memory_snapshot()
        for role in range(7):
            self.select_role(role)
            self.trigger_child(False)
            self.trigger_child(True)
            self.assertEqual(self.production_mod.requested_preferences, {})
            self.assertFalse(self.trial._stopped)
        self.select_role(0)
        self.assertEqual(self.memory_snapshot(), before)
        self.assert_no_transition()

    def test_authenticated_native_true_is_not_replaced_and_does_not_commit(self):
        self.prepare_child()
        self.select_role(5)
        self.fresh_press()
        self.trigger_child(True)
        self.assert_no_request()
        self.assertTrue(self.trial._stopped)
        self.assert_guard_retained()

    def test_unrelated_queued_preferences_survive_a_role_change(self):
        self.prepare_child()
        self.production_mod.requested_preferences = {"planets": False}
        self.select_role(1)
        self.fresh_press()
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences,
                         {"planets": False, "selection_mode": "last_manual"})

    def test_all_roles_report_session_only_stopped_and_unavailable_truthfully(self):
        self.prepare_child()
        for role, prefix in enumerate(self.module.toggle.SETTING_LABELS):
            self.select_role(role)
            self.production_mod.settings_ok = False
            self.assertIsNone(self.label())
            self.assertTrue(self.trial._writer.call_args.args[1].endswith(b" (session only)"))
            self.production_mod.enabled = False
            self.expected_label((prefix + ": stopped").encode())
            self.production_mod.enabled = True
        self.registry.clear()
        for role, prefix in enumerate(self.module.toggle.SETTING_LABELS):
            self.select_role(role)
            self.expected_label((prefix + ": unavailable").encode())


class IconFixture(SettingsFixture):
    custom_icon = True

    def setUp(self):
        super().setUp()
        self.icons = Mock(status="registered")
        self.icons.icon_handle.return_value = 0
        self.trial._icons = self.icons
        self.trial._load_texture = Mock()
        self.trial._retain_icon = Mock()

    def use_role_icons(self, handles):
        self.icons.icon_handle.side_effect = lambda reader, manager, role=-1: handles.get(role, 0)
        def construct(owned, icon, action, disabled, background):
            self.construct(owned, 0x12345678, action, disabled, background)
            owned[:4] = icon.to_bytes(4, "little")
        self.constructor.side_effect = construct

    def copied_role_icons(self):
        parent = int.from_bytes(self.reader(self.parent, 4), "little")
        pointer, count = self.vector(2)
        self.assertEqual(count, 7)
        return {-1: parent, **{
            role: int.from_bytes(self.reader(pointer + role * ITEM.ITEM_SIZE, 4), "little")
            for role in range(7)
        }}


class OptionalIconTests(IconFixture):
    def test_distinct_role_icons_reach_matching_items_and_hud_keeps_parent(self):
        handles = {role: 0x4455 + role + 1 for role in range(-1, 7)}
        self.use_role_icons(handles)
        self.assertIsNone(self.trial.after_resources(self.menu))
        self.prepare_child()
        self.assertEqual(self.copied_role_icons(), handles)
        self.assertEqual(self.reader(self.parent + ITEM.ITEM_SIZE, ITEM.ITEM_SIZE), self.pet_before)
        self.assertEqual(bytes(self.regions[self.pet]), self.pet_before)
        self.assertEqual(self.production_mod._notice_icon_handle(), handles[-1])
        options = self.trial._menu_options()
        self.assertEqual(set(options), {"child_roles", "permitted_icons"})
        self.assertEqual(set(options["permitted_icons"]), set(handles.values()))
        self.assert_no_request()

    def test_one_unavailable_role_uses_native_paw_without_changing_other_icons(self):
        handles = {role: 0x4455 + role + 1 for role in range(-1, 7)}
        expected = {**handles, 2: 0x12345678}
        handles[2] = 0
        self.use_role_icons(handles)
        self.prepare_child()
        self.assertEqual(self.copied_role_icons(), expected)
        self.select_role(2)
        self.expected_label(b"Random: prefer matching biome: ON")
        self.fresh_press()
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences, {"prefer_same_biome": False})
        self.assertEqual(self.reader(self.parent + ITEM.ITEM_SIZE, ITEM.ITEM_SIZE), self.pet_before)
        self.assert_no_transition()

    def test_nine_known_handles_keep_existing_page_usable_when_provider_is_unavailable(self):
        custom = {role: 0x4455 + role + 1 for role in range(-1, 7)}
        handles = {**custom, 6: 0x12345678}  # A retained native paw during the last asset's load.
        self.use_role_icons(handles)
        self.prepare_child()
        self.assertEqual(self.copied_role_icons(), handles)
        handles[6] = custom[6]
        fresh = self.trial._menu_options(construction=True)
        self.assertEqual(fresh["role_icons"], custom)
        self.assertEqual(set(fresh["permitted_icons"]), set(custom.values()) | {0x12345678})
        handles.clear()
        options = self.trial._menu_options()
        self.assertEqual(set(options), {"child_roles", "permitted_icons"})
        self.assertEqual(len(options["permitted_icons"]), 9)
        before = self.memory_snapshot()
        native_count = len(self.native_calls)
        for role, caption in enumerate((
                b"Automatic summoning: ON", b"Selection: By habitat",
                b"Random: prefer matching biome: ON", b"Planets: ON",
                b"Space stations: ON", b"Space Anomaly: ON", b"Shuffle companions: ON")):
            self.select_role(role)
            self.expected_label(caption)
        self.select_role(6)
        self.fresh_press()
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences, {"rotate_companions": False})
        self.select_role(0)
        self.assertIsNone(self.builder())
        self.assertFalse(self.trial._stopped)
        self.assertEqual(len(self.native_calls), native_count)
        self.assertEqual(self.memory_snapshot(), before)
        self.assert_no_transition()

    def test_resource_phase_has_independent_thread_and_binds_one_provider_without_native_calls(self):
        self.assertIsNone(self.trial._thread)
        self.module.get_native_id.return_value = 987654
        self.assertIsNone(self.trial.after_resources(self.menu))
        self.assertIsNone(self.trial._thread)
        self.module.get_native_id.assert_not_called()
        self.icons.register_once.assert_called_once_with(
            self.trial._reader, self.menu,
            self.module._internal.BASE_ADDRESS + self.module.icons.MANAGER_PTR_RVA,
            load_texture=self.trial._load_texture, retain_handle=self.trial._retain_icon,
            pin_owner=self.module.pin_icon_owner)
        self.assertIs(self.production_mod._notice_icon_provider, self.trial._icon_provider)
        self.trial._load_texture.assert_not_called()
        self.trial._retain_icon.assert_not_called()
        self.module.get_native_id.return_value = 271828
        self.prepare_child()
        self.assertEqual(self.trial._thread, 271828)
        self.assertIsNone(self.trial.after_resources(self.menu))
        self.icons.register_once.assert_called_once()
        self.assert_no_request()

    def test_tenth_handle_cannot_expand_recognition_or_construct_new_items(self):
        custom = {role: 0x4455 + role + 1 for role in range(-1, 7)}
        handles = {**custom, 6: 0x12345678}
        self.use_role_icons(handles)
        self.prepare_child()
        handles[6] = custom[6]
        self.trial._menu_options(construction=True)
        expected = set(custom.values()) | {0x12345678}
        self.assertEqual(self.trial._known_icon_handles, expected)
        handles[6] = 0x9988
        options = self.trial._menu_options(construction=True)
        self.assertNotIn(6, options["role_icons"])
        self.assertEqual(set(options["permitted_icons"]), expected)
        self.assertEqual(self.trial._known_icon_handles, expected)
        self.select_role(6)
        self.expected_label(b"Shuffle companions: ON")
        self.assert_no_request()

    def test_preparation_exception_does_not_disable_settings_or_retry(self):
        self.icons.register_once.side_effect = RuntimeError("synthetic loader refusal")
        self.assertIsNone(self.trial.after_resources(self.menu))
        self.assertIsNone(self.trial.after_resources(self.menu))
        self.icons.register_once.assert_called_once()
        self.assertFalse(self.trial._stopped)
        self.prepare_child()
        self.fresh_press()
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences, {"enabled": False})

    def test_logging_failure_cannot_escape_resource_after_callback(self):
        self.icons.register_once.side_effect = RuntimeError("synthetic loader refusal")
        self.module.LOGGER.warning.side_effect = RuntimeError("synthetic logging failure")
        self.assertIsNone(self.trial.after_resources(self.menu))
        self.assertFalse(self.trial._stopped)
        self.assertFalse(self.trial._icon_phase_lock.locked())

    def test_contended_initialization_skips_without_poisoning_menu_baseline(self):
        self.trial._icon_phase_lock.acquire()
        try:
            self.assertIsNone(self.trial.after_resources(self.menu))
        finally:
            self.trial._icon_phase_lock.release()
        self.assertFalse(self.trial._icon_phase_seen)
        self.assertIsNone(self.trial._thread)
        self.icons.register_once.assert_not_called()
        self.assertIsNone(self.trial.after_resources(self.menu))
        self.icons.register_once.assert_called_once()

    def test_provider_passes_ready_handle_and_failure_keeps_production_working(self):
        self.assertIsNone(self.trial.after_resources(self.menu))
        for handle in (11, 22, 0):
            self.icons.icon_handle.return_value = handle
            self.assertEqual(self.production_mod._notice_icon_handle(), handle)
        self.icons.icon_handle.side_effect = RuntimeError("synthetic unavailable resource")
        self.assertEqual(self.production_mod._notice_icon_handle(), 0)
        self.assertTrue(self.production_mod.enabled)
        self.assertTrue(self.production_mod.auto_enabled)
        self.assertEqual(self.production_mod.requested_preferences, {})

    def test_original_icon_fallback_keeps_all_seven_settings_usable(self):
        self.prepare_child()
        for _, _, data in self.native_calls:
            if data[ITEM.MARKER_OFFSET:ITEM.MARKER_OFFSET + 16] == ITEM.CUSTOM_ACTION_MARKER:
                self.assertEqual(int.from_bytes(data[:4], "little"), 0x12345678)
        self.select_role(6)
        self.fresh_press()
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences, {"rotate_companions": False})

    def test_ready_icon_is_used_only_by_tagged_parent_and_children(self):
        handle = 0x4455
        self.icons.icon_handle.return_value = handle
        def construct(owned, icon, action, disabled, background):
            self.assertEqual(icon, handle)
            self.construct(owned, 0x12345678, action, disabled, background)
            owned[:4] = icon.to_bytes(4, "little")
        self.constructor.side_effect = construct
        self.prepare_child()
        for _, _, data in self.native_calls:
            if data[ITEM.MARKER_OFFSET:ITEM.MARKER_OFFSET + 16] == ITEM.CUSTOM_ACTION_MARKER:
                self.assertEqual(int.from_bytes(data[:4], "little"), handle)
            else:
                self.assertEqual(data, self.pet_before)
        self.select_role(5)
        self.expected_label(b"Space Anomaly: ON")
        self.fresh_press()
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences, {"nexus": False})

    def test_temporary_provider_unavailable_does_not_reject_existing_custom_items(self):
        handle = 0x4455
        self.icons.icon_handle.return_value = handle
        def construct(owned, icon, action, disabled, background):
            self.assertEqual(icon, handle)
            self.construct(owned, 0x12345678, action, disabled, background)
            owned[:4] = icon.to_bytes(4, "little")
        self.constructor.side_effect = construct
        self.prepare_child()
        self.icons.icon_handle.return_value = 0  # Includes temporary owner-lock contention.
        before = self.memory_snapshot()
        self.select_role(3)
        self.expected_label(b"Planets: ON")
        self.fresh_press()
        self.trigger_child()
        self.assertEqual(self.production_mod.requested_preferences, {"planets": False})
        self.select_role(0)
        self.assertEqual(self.memory_snapshot(), before)
        self.assert_no_transition()

    def test_retained_recognition_does_not_construct_new_items_with_unavailable_icon(self):
        handle = 0x4455
        self.icons.icon_handle.return_value = handle
        def custom_construct(owned, icon, action, disabled, background):
            self.assertEqual(icon, handle)
            self.construct(owned, 0x12345678, action, disabled, background)
            owned[:4] = icon.to_bytes(4, "little")
        self.constructor.side_effect = custom_construct
        self.prepare_child()
        self.icons.icon_handle.return_value = 0
        self.set_integer(ITEM.DEPTH_OFFSET, 1)
        self.set_vector(2, 0x5550000, [], selected=-1)
        self.constructor.reset_mock()
        self.constructor.side_effect = self.construct  # Accept only the ordinary native paw.
        self.assertIsNone(self.builder())
        self.assertFalse(self.trial._stopped)
        self.assertEqual(self.constructor.call_count, 7)
        pointer, count = self.vector(2)
        self.assertEqual(count, 7)
        for role in range(7):
            self.assertEqual(int.from_bytes(self.reader(pointer + role * ITEM.ITEM_SIZE, 4), "little"),
                             0x12345678)

    def test_provider_binding_can_wait_until_production_is_registered(self):
        self.registry.clear()
        self.assertIsNone(self.trial.after_resources(self.menu))
        self.assertIsNone(self.production_mod._notice_icon_provider)
        self.registry["CompanionAutoSummon"] = self.production_mod
        self.prepare_child()
        self.assertIs(self.production_mod._notice_icon_provider, self.trial._icon_provider)
        self.icons.register_once.assert_called_once()


class FullSettingsMetadataTests(unittest.TestCase):
    def test_disabled_extended_icon_import_initializes_no_native_interfaces(self):
        module = load_trial(settings_enabled=True, extended_settings=True, custom_icon=True)
        self.assertEqual(module.test_events, [("class", True)])
        with patch.object(module, "current_process_io") as io, \
                patch.object(module, "native_adapters") as native, \
                patch.object(module, "icon_adapters") as icon, \
                patch.object(module.icons, "IconOwner") as owner:
            trial = module.CompanionMenuOrderTrial()
        self.assertTrue(trial._stopped)
        self.assertEqual(len(trial.hooks), 9)
        self.assertEqual(trial._gui_widgets, [])
        self.assertEqual(trial._hotkey_funcs, [])
        for call in (io, native, icon, owner, module.ensure_guard):
            call.assert_not_called()
        resource = next(value for value in module.test_declarations if value.offset == 0x151AD80)
        self.assertEqual(list(resource.function.__annotations__.values()), [ctypes.c_void_p, None])
        self.assertEqual(module.CompanionMenuOrderTrial.after_resources._test_hook_time, "after")
        self.assertEqual(module.CompanionMenuOrderTrial._version, "0.8.3-settings-trial")

    def test_process_owner_pin_refuses_replacement_without_native_activity(self):
        module = load_trial(settings_enabled=True, extended_settings=True, custom_icon=True)
        first, second = object(), object()
        with patch.dict(sys.modules):
            sys.modules.pop(module.ICON_REGISTRY_NAME, None)
            self.assertIs(module.pin_icon_owner(first), True)
            self.assertIs(module.pin_icon_owner(first), True)
            self.assertIs(module.pin_icon_owner(second), False)
            self.assertIs(sys.modules[module.ICON_REGISTRY_NAME].owner, first)

    def test_optional_icon_binding_failure_leaves_menu_and_preference_bridge_active(self):
        module = load_trial(enabled=True, settings_enabled=True,
                            extended_settings=True, custom_icon=True)
        bridge, guard = Mock(), Mock()
        module.LOGGER.warning.side_effect = RuntimeError("synthetic logger failure")
        with patch.object(module, "current_process_io", return_value=(Mock(), Mock(), Mock())), \
                patch.object(module, "native_adapters", return_value=(Mock(), Mock(), Mock())), \
                patch.object(module, "ensure_guard", return_value=guard), \
                patch.object(module, "PreferenceBridge", return_value=bridge), \
                patch.object(module, "icon_adapters", side_effect=RuntimeError("synthetic bind refusal")):
            trial = module.CompanionMenuOrderTrial()
        self.assertFalse(trial._stopped)
        self.assertIsNone(trial._icons)
        self.assertIs(trial._guard, guard)
        self.assertIs(trial._preferences, bridge)
        self.assertIsNone(trial.after_resources(0x1110000))
        self.assertEqual(trial._notification_icon(), 0)


if __name__ == "__main__":
    unittest.main()
