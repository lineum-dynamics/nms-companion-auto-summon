"""Submenu policy tests using authored buffers and supplied native stand-ins."""

from dataclasses import FrozenInstanceError, fields, is_dataclass
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

from test_quick_menu_item import ItemFixture, ITEM


TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
try:
    import quick_menu_submenu as SUB
finally:
    sys.path.pop(0)


class SubmenuFixture(ItemFixture):
    def append(self, header_address, data):
        self.events.append("append")
        depth = (header_address - self.menu - ITEM.VECTORS_OFFSET) // ITEM.VECTOR_SIZE
        self.assertIn(depth, (1, 2))
        self.assertEqual(header_address, self.menu + ITEM.VECTORS_OFFSET + depth * 16)
        self.assertIs(type(data), bytes)
        self.assertEqual(len(data), ITEM.ITEM_SIZE)
        offset = ITEM.VECTORS_OFFSET + depth * 16
        header = self.regions[self.menu][offset:offset + 16]
        capacity, count = int.from_bytes(header[:4], "little"), int.from_bytes(header[4:8], "little")
        pointer = int.from_bytes(header[8:], "little")
        prior = bytes(self.regions.get(pointer, b"")[:count * ITEM.ITEM_SIZE])
        destination = pointer if count < capacity else 0x6600000 + depth * 0x100000
        self.regions[destination] = bytearray(prior + data)
        self.regions[self.menu][offset:offset + 16] = (
            max(capacity, count + 1).to_bytes(4, "little")
            + (count + 1).to_bytes(4, "little") + destination.to_bytes(8, "little"))

    def request(self, **overrides):
        arguments = dict(constructor=self.constructor, append=self.append_callback, guard_capability=self.guard)
        arguments.update(overrides)
        return SUB.complete_builder(self.reader, self.menu, **arguments)

    def vector_pointer(self, depth):
        offset = ITEM.VECTORS_OFFSET + depth * 16 + 8
        return int.from_bytes(self.regions[self.menu][offset:offset + 8], "little")

    def select_parent_and_prepare(self):
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2, signed=True)
        result = self.request()
        self.parent = self.vector_pointer(1) + 2 * ITEM.ITEM_SIZE
        return result

    def mutate_entry(self, depth, index, offset, data):
        start = index * ITEM.ITEM_SIZE + offset
        pointer = self.vector_pointer(depth)
        self.regions[pointer][start:start + len(data)] = data

    def capture(self):
        return SUB.capture_activation(self.reader, self.menu, self.parent, True)

    def validate(self, token):
        return SUB.validate_activation(self.reader, self.menu, token, guard_capability=self.guard)


class FullSettingsPageTests(SubmenuFixture):
    def full_page(self, **overrides):
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2, signed=True)
        return self.request(child_roles=SUB.SETTINGS_CHILD_ROLES, **overrides)

    def test_explicit_legacy_six_roles_remain_valid_but_are_not_adopted_as_seven(self):
        legacy = (0, 1, 2, 3, 4, 5)
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2, signed=True)
        self.assertTrue(self.request(child_roles=legacy).child_ready)
        self.assertEqual(self.append_callback.call_count, 7)
        original = {key: bytes(data) for key, data in self.regions.items()}
        self.assertTrue(self.request(child_roles=legacy).child_ready)
        with self.assertRaises(SUB.MenuItemError):
            self.request(child_roles=SUB.SETTINGS_CHILD_ROLES)
        self.assertEqual(self.append_callback.call_count, 7)
        self.assertEqual(original, {key: bytes(data) for key, data in self.regions.items()})

    def test_seven_roles_are_appended_in_order_without_changing_native_scalars(self):
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2, signed=True)
        original = bytes(self.regions[self.menu])
        result = self.full_page()
        self.assertTrue(result.child_ready)
        self.assertEqual(self.append_callback.call_count, 8)
        children = self.regions[self.vector_pointer(2)]
        for role in range(7):
            entry = children[role * ITEM.ITEM_SIZE:(role + 1) * ITEM.ITEM_SIZE]
            self.assertEqual(int.from_bytes(entry[ITEM.SLOT_OFFSET:ITEM.SLOT_OFFSET + 4], "little"), role)
            self.assertEqual(entry[ITEM.ACTION_OFFSET:ITEM.ACTION_OFFSET + 4], bytes(4))
            self.assertEqual(entry[ITEM.MARKER_OFFSET:ITEM.MARKER_OFFSET + 16], ITEM.CUSTOM_ACTION_MARKER)
        for offset, size in ((ITEM.DEPTH_OFFSET, 4), (ITEM.SELECTIONS_OFFSET, 12), (0xA16C, 1)):
            self.assertEqual(self.regions[self.menu][offset:offset + size], original[offset:offset + size])
        self.full_page()
        self.assertEqual(self.append_callback.call_count, 8)

    def test_default_cannot_adopt_full_page_and_full_mode_cannot_adopt_one_child(self):
        self.select_parent_and_prepare()
        before = {key: bytes(data) for key, data in self.regions.items()}
        with self.assertRaises(SUB.MenuItemError):
            self.request(child_roles=SUB.SETTINGS_CHILD_ROLES)
        self.assertEqual(before, {key: bytes(data) for key, data in self.regions.items()})
        self.set_vector(2, self.vector_pointer(2), [], selected=-1)
        self.full_page()
        with self.assertRaises(SUB.MenuItemError):
            self.request()

    def test_partial_append_failure_is_not_repaired_by_adopting_unknown_prefix(self):
        calls = 0

        def interrupted(header, payload):
            nonlocal calls
            calls += 1
            if calls == 4:
                raise RuntimeError("Native append failed")
            self.append(header, payload)

        with self.assertRaises(SUB.MenuItemError):
            self.full_page(append=interrupted)
        before = {key: bytes(data) for key, data in self.regions.items()}
        self.constructor.reset_mock()
        with self.assertRaises(SUB.MenuItemError):
            self.full_page()
        self.constructor.assert_not_called()
        self.assertEqual(before, {key: bytes(data) for key, data in self.regions.items()})

    def test_duplicate_or_foreign_child_role_is_preserved_and_refused(self):
        self.full_page()
        self.mutate_entry(2, 3, ITEM.SLOT_OFFSET, (0).to_bytes(4, "little"))
        before = {key: bytes(data) for key, data in self.regions.items()}
        count = self.append_callback.call_count
        with self.assertRaises(SUB.MenuItemError):
            self.full_page()
        self.assertEqual(count, self.append_callback.call_count)
        self.assertEqual(before, {key: bytes(data) for key, data in self.regions.items()})

    def test_parent_activation_requires_complete_seven_children(self):
        self.full_page()
        parent = self.vector_pointer(1) + 2 * ITEM.ITEM_SIZE
        token = SUB.capture_activation(self.reader, self.menu, parent, True, child_roles=SUB.SETTINGS_CHILD_ROLES)
        self.assertIsNotNone(token)
        self.assertTrue(SUB.validate_activation(self.reader, self.menu, token, guard_capability=self.guard,
                                                child_roles=SUB.SETTINGS_CHILD_ROLES))
        self.set_integer(ITEM.VECTORS_OFFSET + 2 * 16 + 4, 5)
        with self.assertRaises(SUB.MenuItemError):
            SUB.validate_activation(self.reader, self.menu, token, guard_capability=self.guard,
                                    child_roles=SUB.SETTINGS_CHILD_ROLES)

    def test_custom_icon_is_explicit_and_does_not_write_native_icon_field(self):
        custom = 0x10203040
        def construct(buffer, icon, action, disabled, background):
            self.assertEqual(icon, custom)
            self.construct(buffer, 0x12345678, action, disabled, background)
            buffer[:4] = icon.to_bytes(4, "little")
        self.constructor.side_effect = construct
        old_icon = bytes(self.regions[self.menu][ITEM.COMPANION_ICON_OFFSET:ITEM.COMPANION_ICON_OFFSET + 4])
        self.full_page(icon_handle=custom, permitted_icons=(custom,))
        for call in self.append_callback.call_args_list:
            self.assertEqual(int.from_bytes(call.args[1][:4], "little"), custom)
        self.assertEqual(self.regions[self.menu][ITEM.COMPANION_ICON_OFFSET:ITEM.COMPANION_ICON_OFFSET + 4], old_icon)
        with self.assertRaises(SUB.MenuItemError):
            SUB._snapshot(self.reader, self.menu, child_roles=SUB.SETTINGS_CHILD_ROLES)
        self.assertTrue(SUB._snapshot(self.reader, self.menu, child_roles=SUB.SETTINGS_CHILD_ROLES,
                                      permitted_icons=(custom,))[0].child_ready)

    def test_mixed_native_and_pinned_icons_are_reusable_without_rewriting_items(self):
        self.full_page()
        custom = 0x87654321
        self.mutate_entry(2, 4, 0, custom.to_bytes(4, "little"))
        before = {key: bytes(data) for key, data in self.regions.items()}
        self.full_page(permitted_icons=(custom,), icon_handle=custom)
        self.assertEqual(before, {key: bytes(data) for key, data in self.regions.items()})
        self.assertEqual(self.append_callback.call_count, 8)

    def test_invalid_roles_and_unpermitted_icon_refuse_before_construction(self):
        for roles in ((0, 1), (0, 0, 1, 2, 3, 4), (False,), [0]):
            with self.subTest(roles=roles), self.assertRaises(SUB.MenuItemError):
                self.request(child_roles=roles)
        for permitted in ((1, 1), (True,), tuple(range(10)), (-1,), (2**32,)):
            with self.subTest(permitted=permitted), self.assertRaises(SUB.MenuItemError):
                self.request(permitted_icons=permitted)
        with self.assertRaises(SUB.MenuItemError):
            self.full_page(icon_handle=99)
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()


class RoleIconTests(SubmenuFixture):
    def varied_constructor(self, buffer, icon, action, disabled, background):
        self.construct(buffer, 0x12345678, action, disabled, background)
        buffer[:4] = icon.to_bytes(4, "little")

    def prepare_icons(self, **options):
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2, signed=True)
        self.constructor.side_effect = self.varied_constructor
        return self.request(child_roles=SUB.SETTINGS_CHILD_ROLES, **options)

    def test_parent_and_seven_children_use_distinct_explicit_icons_without_native_changes(self):
        icons = {role: 100 + role for role in (-1, 0, 1, 2, 3, 4, 5, 6)}
        permitted = tuple(icons.values()) + (200,)
        before_icon = self.reader(self.menu + ITEM.COMPANION_ICON_OFFSET, 4)
        before_native = bytes(self.regions[self.child_data])
        result = self.prepare_icons(role_icons=icons, permitted_icons=permitted)
        self.assertTrue(result.child_ready)
        for call, role in zip(self.append_callback.call_args_list, icons):
            self.assertEqual(int.from_bytes(call.args[1][:4], "little"), icons[role])
        self.assertEqual(self.reader(self.menu + ITEM.COMPANION_ICON_OFFSET, 4), before_icon)
        self.assertEqual(bytes(self.regions[self.vector_pointer(1)][:2 * ITEM.ITEM_SIZE]), before_native)
        before = {key: bytes(data) for key, data in self.regions.items()}
        self.prepare_icons(role_icons=icons, permitted_icons=permitted)
        self.assertEqual(self.append_callback.call_count, 8)
        self.assertEqual({key: bytes(data) for key, data in self.regions.items()}, before)

    def test_missing_roles_use_explicit_fallback_then_native_paw_in_legacy_mode(self):
        self.prepare_icons(role_icons={-1: 101, 2: 102}, icon_handle=103,
                           permitted_icons=(101, 102, 103))
        self.assertEqual([int.from_bytes(call.args[1][:4], "little")
                          for call in self.append_callback.call_args_list],
                         [101, 103, 103, 102, 103, 103, 103, 103])
        self.setUp()
        self.constructor.side_effect = self.varied_constructor
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2, signed=True)
        self.request(role_icons={-1: 101}, permitted_icons=(101,))
        self.assertEqual([int.from_bytes(call.args[1][:4], "little")
                          for call in self.append_callback.call_args_list], [101, 0x12345678])

    def test_entire_role_map_is_rejected_before_any_append(self):
        for mapping in ({7: 101}, {-2: 101}, {True: 101}, {"0": 101}, {0: True},
                        {0: 0}, {0: -1}, {0: 2**31}, [(0, 101)], {5: 999}):
            with self.subTest(mapping=mapping), self.assertRaises(SUB.MenuItemError):
                self.prepare_icons(role_icons=mapping, permitted_icons=(101,))
        with self.assertRaises(SUB.MenuItemError):
            self.request(role_icons={1: 101}, permitted_icons=(101,))
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()

    def test_role_choices_are_copied_before_constructor_callbacks(self):
        choices = {role: 100 + role for role in (-1, 0, 1, 2, 3, 4, 5, 6)}
        original = choices.copy()
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2, signed=True)
        def mutate_mapping(*args):
            self.varied_constructor(*args)
            choices[5] = 999
        self.constructor.side_effect = mutate_mapping
        self.request(child_roles=SUB.SETTINGS_CHILD_ROLES, role_icons=choices,
                     permitted_icons=tuple(original.values()))
        self.assertEqual([int.from_bytes(call.args[1][:4], "little")
                          for call in self.append_callback.call_args_list], list(original.values()))

    def test_allowed_icons_do_not_admit_foreign_handles_actions_or_roles(self):
        permitted = tuple(range(101, 109))
        self.prepare_icons(role_icons={role: 102 + role for role in (-1, 0, 1, 2, 3, 4, 5, 6)},
                           permitted_icons=permitted)
        for offset, value in ((0, 109), (ITEM.ACTION_OFFSET, 46), (ITEM.SLOT_OFFSET, 0)):
            pointer = self.vector_pointer(2)
            old = bytes(self.regions[pointer])
            self.mutate_entry(2, 3, offset, value.to_bytes(4, "little"))
            before = {key: bytes(data) for key, data in self.regions.items()}
            with self.subTest(offset=offset), self.assertRaises(SUB.MenuItemError):
                self.prepare_icons(permitted_icons=permitted)
            self.assertEqual({key: bytes(data) for key, data in self.regions.items()}, before)
            self.regions[pointer][:] = old

    def test_append_readback_requires_chosen_icon_even_when_another_is_permitted(self):
        def substituted(header, payload):
            changed = bytearray(payload)
            changed[:4] = (102).to_bytes(4, "little")
            self.append(header, bytes(changed))
        self.append_callback.side_effect = substituted
        with self.assertRaisesRegex(SUB.MenuItemError, "requested icon"):
            self.prepare_icons(role_icons={-1: 101}, permitted_icons=(101, 102))
        self.append_callback.assert_called_once()


class BuilderTests(SubmenuFixture):
    def test_outside_context_does_not_construct_or_append(self):
        for depth, root_selected in ((0, 0), (1, 1), (2, 1)):
            with self.subTest(depth=depth, root_selected=root_selected):
                self.set_integer(ITEM.DEPTH_OFFSET, depth)
                self.set_integer(ITEM.SELECTIONS_OFFSET, root_selected)
                self.assertEqual(self.request().status, "outside_context")
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()

    def test_unselected_parent_append_preserves_native_neighbors_and_child_page(self):
        self.set_vector(2, 0x5550000, [1, 2], selected=0)
        prior = bytes(self.regions[self.child_data])
        children = bytes(self.regions[0x5550000])
        result = self.request()
        self.assertEqual(result, SUB.BuilderResult("prepared", True, False, False, False))
        self.assertEqual(bytes(self.regions[self.vector_pointer(1)][:-224]), prior)
        self.assertEqual(bytes(self.regions[0x5550000]), children)
        payload = self.append_callback.call_args.args[1]
        self.assertEqual(payload[0x84:0x88], b"\xff" * 4)
        self.assertEqual(payload[0x88:0x98], ITEM.CUSTOM_ACTION_MARKER)
        self.assertEqual(payload[0x98:0xD8], bytes(64))
        self.assertEqual(payload[0xD8:0xDC], b"\xff" * 4)

    def test_selected_parent_prebuilds_exactly_one_inert_child(self):
        before = bytes(self.regions[self.menu])
        result = self.select_parent_and_prepare()
        self.assertEqual(result, SUB.BuilderResult("prepared", True, True, True, False))
        self.assertEqual(self.append_callback.call_count, 2)
        root, child = [call.args[1] for call in self.append_callback.call_args_list]
        expected_child = bytearray(root)
        expected_child[ITEM.SLOT_OFFSET:ITEM.SLOT_OFFSET + 4] = bytes(4)
        self.assertEqual(child, bytes(expected_child))
        self.assertEqual(child[ITEM.MARKER_OFFSET:ITEM.MARKER_OFFSET + 16], ITEM.CUSTOM_ACTION_MARKER)
        self.assertEqual(child[ITEM.NAME_OFFSET:ITEM.NAME_OFFSET + 64], bytes(64))
        self.assertEqual(self.regions[self.menu][ITEM.DEPTH_OFFSET:ITEM.DEPTH_OFFSET + 4], before[ITEM.DEPTH_OFFSET:ITEM.DEPTH_OFFSET + 4])
        self.assertEqual(self.regions[self.menu][0xA16C], before[0xA16C])
        self.assertEqual(self.regions[self.menu][ITEM.SELECTIONS_OFFSET + 8:ITEM.SELECTIONS_OFFSET + 12], b"\xff" * 4)

    def test_exact_repeat_is_idempotent(self):
        self.select_parent_and_prepare()
        original = {key: bytes(value) for key, value in self.regions.items()}
        self.assertEqual(self.request(), SUB.BuilderResult("prepared", False, False, True, False))
        self.assertEqual(self.append_callback.call_count, 2)
        self.assertEqual(self.constructor.call_count, 2)
        self.assertEqual({key: bytes(value) for key, value in self.regions.items()}, original)

    def test_native_rebuild_at_depth_two_restores_both_items_without_selecting(self):
        self.select_parent_and_prepare()
        self.set_integer(ITEM.DEPTH_OFFSET, 2)
        self.set_vector(1, self.child_data, [46, 50], selected=2)
        self.set_vector(2, 0x5550000, [], selected=0)
        self.regions[self.menu][0xA16C] = 1
        result = self.request()
        self.assertEqual(result, SUB.BuilderResult("prepared", True, True, True, True))
        self.assertEqual(self.regions[self.menu][0xA16C], 1)
        self.assertEqual(self.regions[self.menu][ITEM.DEPTH_OFFSET:ITEM.DEPTH_OFFSET + 4], (2).to_bytes(4, "little"))

    def test_existing_parent_only_appends_missing_child(self):
        self.request()
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2)
        result = self.request()
        self.assertEqual(result, SUB.BuilderResult("prepared", False, True, True, False))
        self.assertEqual(self.append_callback.call_count, 2)

    def test_unknown_nonempty_child_page_is_never_cleared_or_extended(self):
        self.select_parent_and_prepare()
        for actions in ([46], [0, 0]):
            with self.subTest(actions=actions):
                self.set_vector(2, 0x5550000, actions, selected=0)
                before = {key: bytes(value) for key, value in self.regions.items()}
                count = self.append_callback.call_count
                with self.assertRaises(SUB.MenuItemError):
                    self.request()
                self.assertEqual(self.append_callback.call_count, count)
                self.assertEqual({key: bytes(value) for key, value in self.regions.items()}, before)

    def test_missing_selected_parent_cannot_adopt_existing_native_children(self):
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2)
        self.set_vector(2, 0x5550000, [46], selected=0)
        before = {key: bytes(value) for key, value in self.regions.items()}
        with self.assertRaisesRegex(SUB.MenuItemError, "adopt a native child page"):
            self.request()
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()
        self.assertEqual({key: bytes(value) for key, value in self.regions.items()}, before)

    def test_duplicate_full_parent_marker_is_rejected(self):
        self.select_parent_and_prepare()
        pointer = self.vector_pointer(1)
        self.regions[pointer][:224] = self.regions[pointer][448:672]
        with self.assertRaises(SUB.MenuItemError):
            self.request()
        self.assertEqual(self.append_callback.call_count, 2)

    def test_incorrect_tagged_fields_are_rejected_before_callbacks(self):
        self.select_parent_and_prepare()
        for depth, index, offset, replacement in (
            (1, 2, 4, (46).to_bytes(4, "little")),
            (1, 2, 0x84, bytes(4)),
            (2, 0, 0x84, b"\xff" * 4),
            (2, 0, 0x4C, b"\x01"),
            (2, 0, 0x98, b"x"),
            (2, 0, 0xD8, bytes(4)),
            (2, 0, 0, bytes(4)),
            (2, 0, 0x88, b"X"),
        ):
            with self.subTest(depth=depth, offset=offset):
                pointer = self.vector_pointer(depth)
                before = bytes(self.regions[pointer])
                self.mutate_entry(depth, index, offset, replacement)
                with self.assertRaises(SUB.MenuItemError):
                    self.request()
                self.regions[pointer][:] = before
        self.assertEqual(self.append_callback.call_count, 2)

    def test_hostile_header_bounds_fail_without_native_callbacks(self):
        for depth, capacity, count, pointer in ((0, 257, 2, self.root_data),
                                               (1, 1, 2, self.child_data),
                                               (2, 0xFFFFFFFF, 0, 0),
                                               (2, 1, 0, 1)):
            with self.subTest(depth=depth, capacity=capacity):
                offset = ITEM.VECTORS_OFFSET + depth * 16
                old = bytes(self.regions[self.menu][offset:offset + 16])
                self.regions[self.menu][offset:offset + 16] = capacity.to_bytes(4, "little") + count.to_bytes(4, "little") + pointer.to_bytes(8, "little")
                with self.assertRaises(SUB.MenuItemError):
                    self.request()
                self.regions[self.menu][offset:offset + 16] = old
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()

    def test_missing_guard_prevents_even_reads(self):
        with self.assertRaises(SUB.MenuItemError):
            self.request(guard_capability=None)
        self.assertEqual(self.reads, [])
        self.constructor.assert_not_called()

    def test_guard_expiring_after_constructor_prevents_append(self):
        self.guard.authorize_append.side_effect = [True, True, False]
        with self.assertRaises(SUB.MenuItemError):
            self.request()
        self.constructor.assert_called_once()
        self.append_callback.assert_not_called()

    def test_constructor_changes_context_or_storage_then_append_is_refused(self):
        original = self.construct
        def changed(*args):
            original(*args)
            self.regions[0x7770000] = self.regions[self.child_data][:]
            offset = ITEM.VECTORS_OFFSET + 16 + 8
            self.regions[self.menu][offset:offset + 8] = (0x7770000).to_bytes(8, "little")
        self.constructor.side_effect = changed
        with self.assertRaises(SUB.MenuItemError):
            self.request()
        self.append_callback.assert_not_called()

    def test_append_that_does_not_change_native_vector_fails_readback(self):
        self.append_callback.side_effect = None
        with self.assertRaises(SUB.MenuItemError):
            self.request()
        self.append_callback.assert_called_once()

    def test_append_failure_after_side_effect_is_never_retried(self):
        def failing(*args):
            self.append(*args)
            raise RuntimeError("private native details")
        self.append_callback.side_effect = failing
        with self.assertRaisesRegex(SUB.MenuItemError, "outcome is unverified"):
            self.request()
        self.append_callback.assert_called_once()

    def test_short_or_failed_copies_prevent_native_operations(self):
        for reader in (lambda *_: b"", Mock(side_effect=OSError("private address"))):
            with self.subTest(reader=type(reader).__name__), self.assertRaises(SUB.MenuItemError):
                SUB.complete_builder(reader, self.menu, constructor=self.constructor,
                                     append=self.append_callback, guard_capability=self.guard)
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()


class LabelAndActivationTests(SubmenuFixture):
    def test_labels_are_only_for_selected_exact_parent_and_child(self):
        self.request()
        self.assertIsNone(SUB.selected_label(self.reader, self.menu))
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2)
        self.request()
        self.assertEqual(SUB.selected_label(self.reader, self.menu), b"Companion Auto Summon")
        self.set_integer(ITEM.DEPTH_OFFSET, 2)
        self.assertIsNone(SUB.selected_label(self.reader, self.menu))
        self.set_integer(ITEM.SELECTIONS_OFFSET + 8, 0)
        self.assertEqual(SUB.selected_label(self.reader, self.menu), b"Settings preview")

    def test_parent_capture_is_frozen_and_contains_no_native_pointers(self):
        result = self.select_parent_and_prepare()
        token = self.capture()
        self.assertIsInstance(token, SUB.ActivationToken)
        def values(value):
            if is_dataclass(value):
                return [part for entry in fields(value) for part in values(getattr(value, entry.name))]
            return [value]
        leaves = values(token) + values(result)
        for address in (self.menu, self.parent, self.root_data, self.vector_pointer(1), self.vector_pointer(2)):
            self.assertNotIn(address, leaves)
        with self.assertRaises(FrozenInstanceError):
            token.state = None
        self.assertTrue(self.validate(token))

    def test_non_menu_call_never_reads_action(self):
        reader = Mock(side_effect=AssertionError("No read expected"))
        self.assertIsNone(SUB.capture_activation(reader, self.menu, 1, False))
        reader.assert_not_called()

    def test_vanilla_action_and_child_activation_are_not_captured(self):
        self.select_parent_and_prepare()
        self.assertIsNone(SUB.capture_activation(self.reader, self.menu, self.vector_pointer(1), True))
        child = self.vector_pointer(2)
        self.assertIsNone(SUB.capture_activation(self.reader, self.menu, child, True))

    def test_copied_parent_is_not_the_selected_native_pointer(self):
        self.select_parent_and_prepare()
        pointer = self.vector_pointer(1)
        copy = 0x8880000
        self.regions[copy] = self.regions[pointer][448:672]
        self.assertIsNone(SUB.capture_activation(self.reader, self.menu, copy, True))

    def test_capture_requires_depth_one_current_selection_and_prebuilt_child(self):
        self.select_parent_and_prepare()
        for offset, value in ((ITEM.DEPTH_OFFSET, 2), (ITEM.SELECTIONS_OFFSET, 1),
                              (ITEM.SELECTIONS_OFFSET + 4, 0)):
            with self.subTest(offset=offset):
                prior = bytes(self.regions[self.menu][offset:offset + 4])
                self.set_integer(offset, value)
                self.assertIsNone(self.capture())
                self.regions[self.menu][offset:offset + 4] = prior
        self.set_vector(2, 0x5550000, [], selected=-1)
        self.assertIsNone(self.capture())

    def test_every_marker_byte_is_required(self):
        self.select_parent_and_prepare()
        for index in range(16):
            with self.subTest(index=index):
                marker = bytearray(ITEM.CUSTOM_ACTION_MARKER)
                marker[index] ^= 1
                self.mutate_entry(1, 2, ITEM.MARKER_OFFSET, marker)
                self.assertIsNone(self.capture())
        self.mutate_entry(1, 2, ITEM.MARKER_OFFSET, ITEM.CUSTOM_ACTION_MARKER)

    def test_validation_refuses_changed_owned_topology_or_guard(self):
        self.select_parent_and_prepare()
        token = self.capture()
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 0)
        self.assertFalse(self.validate(token))
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2)
        self.guard.authorize_append.return_value = False
        self.guard.authorize_append.side_effect = None
        with self.assertRaises(SUB.MenuItemError):
            self.validate(token)

    def test_second_validation_guard_cannot_change_context_unnoticed(self):
        self.select_parent_and_prepare()
        token = self.capture()
        calls = 0
        def guard(menu):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.set_integer(ITEM.SELECTIONS_OFFSET + 8, 0)
            return True
        self.guard.authorize_append.side_effect = guard
        self.assertFalse(self.validate(token))

    def test_invalid_token_is_ignored_without_memory_access(self):
        reader = Mock(side_effect=AssertionError("No read expected"))
        self.assertFalse(SUB.validate_activation(reader, self.menu, None, guard_capability=self.guard))
        reader.assert_not_called()

    def test_module_import_does_not_perform_io(self):
        name = "submenu_import_test"
        spec = importlib.util.spec_from_file_location(name, TOOLS / "quick_menu_submenu.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {name: module}), patch.object(Path, "open", side_effect=AssertionError("No I/O on import")):
            spec.loader.exec_module(module)


if __name__ == "__main__":
    unittest.main()
