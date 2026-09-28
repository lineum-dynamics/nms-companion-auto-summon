"""Settings-child policy checks using owned synthetic menu buffers only."""

from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from test_quick_menu_submenu import SubmenuFixture, SUB


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import quick_menu_toggle as TOGGLE
finally:
    sys.path.pop(0)
ITEM = TOGGLE.item


class ToggleFixture(SubmenuFixture):
    def setUp(self):
        super().setUp()
        self.select_parent_and_prepare()
        self.set_integer(ITEM.DEPTH_OFFSET, 2)
        self.set_integer(ITEM.SELECTIONS_OFFSET + 8, 0)
        self.child = self.vector_pointer(2)
        self.expected = TOGGLE.selected_child_state(self.reader, self.menu)
        self.reads.clear()
        self.events.clear()
        self.constructor.reset_mock()
        self.append_callback.reset_mock()

    def capture_child(self, *, reader=None, action=None, expected=None):
        return TOGGLE.capture_activation(
            reader or self.reader, self.menu, self.child if action is None else action,
            True, self.expected if expected is None else expected)

    def validate_child(self, token, **overrides):
        return TOGGLE.validate_activation(
            overrides.get("reader", self.reader), self.menu, token,
            guard_capability=overrides.get("guard", self.guard))


class FullSettingsRecognitionTests(SubmenuFixture):
    def setUp(self):
        super().setUp()
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2)
        self.request(child_roles=TOGGLE.CHILD_ROLES)
        self.set_integer(ITEM.DEPTH_OFFSET, 2)
        self.options = {"child_roles": TOGGLE.CHILD_ROLES}

    def capture_role(self, role, **options):
        self.set_integer(ITEM.SELECTIONS_OFFSET + 8, role)
        arguments = dict(self.options, **options)
        state = TOGGLE.selected_child_state(self.reader, self.menu, **arguments)
        address = self.vector_pointer(2) + role * ITEM.ITEM_SIZE
        token = TOGGLE.capture_activation(self.reader, self.menu, address, True, state, **arguments)
        return state, token

    def test_all_seven_selected_roles_capture_the_exact_item_and_setting(self):
        original = {key: bytes(data) for key, data in self.regions.items()}
        for role, key in enumerate(("enabled", "selection_mode", "prefer_same_biome", "planets",
                                    "space_stations", "nexus", "rotate_companions")):
            with self.subTest(role=role):
                state, token = self.capture_role(role)
                self.assertEqual(TOGGLE.setting_key(token.state.child_selected), key)
                self.assertTrue(TOGGLE.validate_activation(self.reader, self.menu, token,
                                                         guard_capability=self.guard, **self.options))
                foreign = self.vector_pointer(2) + ((role + 1) % 7) * ITEM.ITEM_SIZE
                self.assertIsNone(TOGGLE.capture_activation(self.reader, self.menu, foreign, True,
                                                           state, **self.options))
        for pointer in (self.vector_pointer(1), self.vector_pointer(2)):
            self.assertEqual(bytes(self.regions[pointer]), original[pointer])

    def test_navigation_after_capture_and_default_mode_refuse_full_page_token(self):
        state, token = self.capture_role(4)
        self.assertFalse(TOGGLE.validate_activation(self.reader, self.menu, token, guard_capability=self.guard))
        self.set_integer(ITEM.SELECTIONS_OFFSET + 8, 5)
        self.assertFalse(TOGGLE.validate_activation(self.reader, self.menu, token,
                                                  guard_capability=self.guard, **self.options))
        self.assertEqual(state.child_selected, 4)

    def test_custom_icon_must_be_permitted_for_capture_and_validation(self):
        custom = 0x23456789
        self.mutate_entry(2, 2, 0, custom.to_bytes(4, "little"))
        with self.assertRaises(TOGGLE.MenuItemError):
            self.capture_role(2)
        _, token = self.capture_role(2, permitted_icons=(custom,))
        self.assertTrue(TOGGLE.validate_activation(self.reader, self.menu, token,
                                                  guard_capability=self.guard, permitted_icons=(custom,),
                                                  **self.options))
        with self.assertRaises(TOGGLE.MenuItemError):
            TOGGLE.validate_activation(self.reader, self.menu, token, guard_capability=self.guard, **self.options)

    def test_labels_cover_existing_options_and_honest_pending_session_states(self):
        state = SimpleNamespace(desired=True, pending=False, settings_ok=True, stopped=False)
        expected = (b"Automatic summoning: ON", b"Selection: Random", b"Random: prefer matching biome: ON",
                    b"Planets: ON", b"Space stations: ON", b"Space Anomaly: ON", b"Rotate companions: ON")
        for role, label in enumerate(expected):
            state.desired = "random" if role == 1 else True
            self.assertEqual(TOGGLE.preference_label(role, state), label)
            _, token = self.capture_role(role)
            self.assertEqual(TOGGLE.selected_label(self.reader, self.menu, label, **self.options), label)
        state.desired = "last_manual"
        self.assertEqual(TOGGLE.preference_label(1, state), b"Selection: Last selected")
        state.pending = True
        self.assertEqual(TOGGLE.preference_label(1, state), b"Selection: Last selected (pending)")
        state.pending = False
        state.settings_ok = False
        self.assertEqual(TOGGLE.preference_label(1, state), b"Selection: Last selected (session only)")
        state.stopped = True
        self.assertEqual(TOGGLE.preference_label(1, state), b"Selection: stopped")
        self.assertEqual(TOGGLE.preference_label(1, None), b"Selection: unavailable")

    def test_each_role_with_distinct_allowlisted_icons_preserves_recognition(self):
        permitted = tuple(range(101, 110))
        self.mutate_entry(1, 2, 0, (101).to_bytes(4, "little"))
        for role in range(7):
            self.mutate_entry(2, role, 0, (102 + role).to_bytes(4, "little"))
        for role in range(7):
            _, token = self.capture_role(role, permitted_icons=permitted)
            self.assertTrue(TOGGLE.validate_activation(self.reader, self.menu, token,
                                                      guard_capability=self.guard,
                                                      permitted_icons=permitted, **self.options))
        self.mutate_entry(2, 5, 0, (110).to_bytes(4, "little"))
        with self.assertRaises(TOGGLE.MenuItemError):
            self.capture_role(5, permitted_icons=permitted)

    def test_biome_caption_keeps_random_scope_in_all_states(self):
        state = SimpleNamespace(desired=False, pending=True, settings_ok=True, stopped=False)
        self.assertEqual(TOGGLE.preference_label(2, state), b"Random: prefer matching biome: OFF (pending)")
        state.pending = False
        state.settings_ok = False
        self.assertEqual(TOGGLE.preference_label(2, state), b"Random: prefer matching biome: OFF (session only)")
        state.stopped = True
        self.assertEqual(TOGGLE.preference_label(2, state), b"Random: prefer matching biome: stopped")
        self.assertEqual(TOGGLE.preference_label(2, None), b"Random: prefer matching biome: unavailable")

    def test_habitat_and_rotation_captions_preserve_pending_and_session_only_state(self):
        state = SimpleNamespace(desired="by_habitat", pending=True, settings_ok=False, stopped=False)
        self.assertEqual(TOGGLE.preference_label(1, state), b"Selection: By habitat (pending)")
        state.pending = False
        self.assertEqual(TOGGLE.preference_label(1, state), b"Selection: By habitat (session only)")
        state.desired = False
        self.assertEqual(TOGGLE.preference_label(6, state), b"Rotate companions: OFF (session only)")
        self.assertEqual(TOGGLE.preference_label(6, None), b"Rotate companions: unavailable")
        self.assertEqual(TOGGLE.SETTING_KEYS[:6], ("enabled", "selection_mode", "prefer_same_biome",
                                                "planets", "space_stations", "nexus"))

    def test_invalid_roles_and_preference_values_cannot_create_a_caption(self):
        for role in (-1, 7, True, "1"):
            with self.subTest(role=role), self.assertRaises(TOGGLE.MenuItemError):
                TOGGLE.preference_label(role, None)
        for role, value in ((0, 1), (1, "unknown"), (2, "true")):
            state = SimpleNamespace(desired=value, stopped=False, pending=False, settings_ok=True)
            with self.assertRaises(TOGGLE.MenuItemError):
                TOGGLE.preference_label(role, state)


class ToggleRecognitionTests(ToggleFixture):
    def test_selected_child_token_is_immutable_owned_topology(self):
        token = self.capture_child()
        self.assertIs(type(token), TOGGLE.ChildActivationToken)
        self.assertEqual(token.state, self.expected)
        self.assertEqual([field.name for field in fields(token)], ["state"])
        self.assertFalse(any("pointer" in field.name for field in fields(token.state)))
        with self.assertRaises(FrozenInstanceError):
            token.state = None
        self.assertTrue(self.validate_child(token))

    def test_recognition_and_label_paths_do_not_modify_any_buffer_or_call_native_helpers(self):
        original = {key: bytes(data) for key, data in self.regions.items()}
        token = self.capture_child()
        self.assertTrue(self.validate_child(token))
        self.assertEqual(TOGGLE.selected_label(self.reader, self.menu, b"Automatic summoning: ON"),
                         b"Automatic summoning: ON")
        self.assertEqual(original, {key: bytes(data) for key, data in self.regions.items()})
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()
        self.assertEqual(set(self.events), {"guard"})

    def test_nonmenu_call_or_missing_intent_state_refuses_without_reads(self):
        self.assertIsNone(TOGGLE.capture_activation(self.reader, self.menu, 1, False, self.expected))
        for state in (None, True, object(), SUB.ActivationToken(self.expected),
                      replace(self.expected, depth=1), replace(self.expected, child_selected=-1)):
            with self.subTest(state_type=type(state).__name__):
                self.assertIsNone(TOGGLE.capture_activation(self.reader, self.menu, 1, True, state))
        self.assertEqual(self.reads, [])

    def test_invalid_menu_flag_refuses_without_reads(self):
        for value in (1, 0, None, "yes"):
            with self.subTest(value=value), self.assertRaises(TOGGLE.MenuItemError):
                TOGGLE.capture_activation(self.reader, self.menu, self.child, value, self.expected)
        self.assertEqual(self.reads, [])

    def test_parent_and_nonmatching_native_item_cannot_be_child_activation(self):
        self.assertIsNone(self.capture_child(action=self.parent))
        self.assertIsNone(self.capture_child(action=self.vector_pointer(1)))
        for offset, value in ((ITEM.ACTION_OFFSET, (46).to_bytes(4, "little")),
                              (ITEM.MARKER_OFFSET, b"X"),
                              (ITEM.SLOT_OFFSET, (1).to_bytes(4, "little"))):
            original = bytes(self.regions[self.child])
            with self.subTest(offset=offset):
                self.mutate_entry(2, 0, offset, value)
                self.assertIsNone(self.capture_child())
            self.regions[self.child][:] = original

    def test_matching_copied_item_is_rejected_before_native_call(self):
        copied = 0x7700000
        self.regions[copied] = bytearray(self.regions[self.child])
        self.assertIsNone(self.capture_child(action=copied))

    def test_changed_topology_since_predicate_refuses_capture(self):
        self.set_integer(ITEM.VECTORS_OFFSET + 16, self.expected.companion_capacity + 1)
        self.assertIsNone(self.capture_child())

    def test_changed_root_or_selection_excludes_current_child(self):
        for offset, value in ((ITEM.DEPTH_OFFSET, 0), (ITEM.DEPTH_OFFSET, 1),
                              (ITEM.SELECTIONS_OFFSET, 1),
                              (ITEM.SELECTIONS_OFFSET + 4, 0),
                              (ITEM.SELECTIONS_OFFSET + 8, 1),
                              (ITEM.SELECTIONS_OFFSET + 8, -1)):
            original = bytes(self.regions[self.menu])
            with self.subTest(offset=offset, value=value):
                self.set_integer(offset, value, signed=True)
                self.assertIsNone(TOGGLE.selected_child_state(self.reader, self.menu))
                self.assertIsNone(self.capture_child())
            self.regions[self.menu][:] = original

    def test_unknown_child_page_duplicate_parent_or_malformed_tag_fails_closed(self):
        saved = {key: bytes(data) for key, data in self.regions.items()}
        mutations = [
            lambda: self.mutate_entry(2, 0, 0x4C, b"\1"),
            lambda: self.mutate_entry(2, 0, 0x98, b"x"),
            lambda: self.mutate_entry(2, 0, 0xD8, bytes(4)),
            lambda: self.mutate_entry(2, 0, 0, bytes(4)),
            lambda: self.mutate_entry(1, 2, ITEM.SLOT_OFFSET, bytes(4)),
            lambda: self.regions[self.vector_pointer(1)].__setitem__(slice(0, 224), self.regions[self.vector_pointer(1)][448:672]),
            lambda: self.set_vector(2, self.child, [46], selected=0),
            lambda: self.set_vector(2, self.child, [0, 0], selected=0),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                mutate()
                with self.assertRaises(TOGGLE.MenuItemError):
                    TOGGLE.selected_child_state(self.reader, self.menu)
            self.regions = {key: bytearray(data) for key, data in saved.items()}

    def test_malformed_header_or_unreadable_data_fails_closed(self):
        for depth in (0, 1, 2):
            offset = ITEM.VECTORS_OFFSET + depth * ITEM.VECTOR_SIZE
            original = bytes(self.regions[self.menu][offset:offset + 4])
            with self.subTest(depth=depth):
                self.set_integer(offset, 0)
                with self.assertRaises(TOGGLE.MenuItemError):
                    TOGGLE.selected_child_state(self.reader, self.menu)
            self.regions[self.menu][offset:offset + 4] = original
        with self.assertRaises(TOGGLE.MenuItemError):
            TOGGLE.selected_child_state(Mock(side_effect=OSError("unreadable")), self.menu)

    def test_capture_rechecks_snapshot_before_returning_token(self):
        calls = 0
        def changing_reader(address, size):
            nonlocal calls
            if address == self.menu + ITEM.DEPTH_OFFSET:
                calls += 1
                if calls == 2:
                    self.set_integer(ITEM.SELECTIONS_OFFSET + 8, -1, signed=True)
            return self.reader(address, size)
        with self.assertRaises(TOGGLE.MenuItemError):
            self.capture_child(reader=changing_reader)

    def test_validation_uses_new_storage_without_reading_old_action_pointer(self):
        token = self.capture_child()
        relocated = 0x7800000
        self.regions[relocated] = self.regions.pop(self.child)
        offset = ITEM.VECTORS_OFFSET + 2 * ITEM.VECTOR_SIZE + 8
        self.regions[self.menu][offset:offset + 8] = relocated.to_bytes(8, "little")
        self.reads.clear()
        self.assertTrue(self.validate_child(token))
        self.assertFalse(any(self.child <= address < self.child + ITEM.ITEM_SIZE for address, _ in self.reads))

    def test_validation_rejects_wrong_token_before_reading_or_authorizing(self):
        for token in (None, True, self.expected, SUB.ActivationToken(self.expected),
                      TOGGLE.ChildActivationToken(replace(self.expected, depth=1))):
            with self.subTest(token_type=type(token).__name__):
                self.assertFalse(self.validate_child(token))
        self.assertEqual(self.reads, [])
        self.assertEqual(self.events, [])

    def test_validation_requires_guard_twice_and_refuses_changed_topology(self):
        token = self.capture_child()
        self.reads.clear()
        with self.assertRaises(TOGGLE.MenuItemError):
            self.validate_child(token, guard=None)
        self.assertEqual(self.reads, [])
        self.guard.authorize_append.side_effect = [True, False]
        with self.assertRaises(TOGGLE.MenuItemError):
            self.validate_child(token)
        self.guard.authorize_append.side_effect = self.authorize
        self.set_integer(ITEM.SELECTIONS_OFFSET + 8, -1, signed=True)
        self.assertFalse(self.validate_child(token))

    def test_validation_detects_mutation_at_final_authorization(self):
        token = self.capture_child()
        count = 0
        def changing_guard(menu):
            nonlocal count
            count += 1
            if count == 2:
                self.set_integer(ITEM.SELECTIONS_OFFSET + 8, -1, signed=True)
            return True
        self.guard.authorize_append.side_effect = changing_guard
        self.assertFalse(self.validate_child(token))


class ToggleLabelTests(ToggleFixture):
    def test_child_dynamic_label_does_not_change_identity_or_topology(self):
        before = self.expected
        for label in (b"Automatic summoning: ON", b"Automatic summoning: OFF",
                      b"Automatic summoning: OFF (pending)"):
            self.assertEqual(TOGGLE.selected_label(self.reader, self.menu, label), label)
            self.assertEqual(TOGGLE.selected_child_state(self.reader, self.menu), before)

    def test_parent_caption_is_retained_and_other_context_has_no_overlay(self):
        self.set_integer(ITEM.DEPTH_OFFSET, 1)
        self.assertEqual(TOGGLE.selected_label(self.reader, self.menu, b"OFF"),
                         b"Companion Auto Summon")
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 0)
        self.assertIsNone(TOGGLE.selected_label(self.reader, self.menu, b"OFF"))
        self.set_integer(ITEM.DEPTH_OFFSET, 0)
        self.assertIsNone(TOGGLE.selected_label(self.reader, self.menu, b"OFF"))

    def test_invalid_child_label_is_rejected_by_byte_length_and_type(self):
        for label in (None, "ON", bytearray(b"ON"), b"", b"ON\0", b"x" * 128):
            with self.subTest(label_type=type(label).__name__), self.assertRaises(TOGGLE.MenuItemError):
                TOGGLE.selected_label(self.reader, self.menu, label)
        self.assertEqual(TOGGLE.selected_label(self.reader, self.menu, b"x" * 127), b"x" * 127)


if __name__ == "__main__":
    unittest.main()
