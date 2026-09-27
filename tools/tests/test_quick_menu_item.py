"""Candidate-item tests using synthetic byte regions and injected callbacks."""

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock


SOURCE = Path(__file__).resolve().parents[1] / "quick_menu_item.py"
SPEC = importlib.util.spec_from_file_location("quick_menu_item_under_test", SOURCE)
ITEM = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ITEM
SPEC.loader.exec_module(ITEM)


class ItemFixture(unittest.TestCase):
    def setUp(self):
        self.menu = 0x1110000
        self.root_data = 0x2220000
        self.child_data = 0x3330000
        self.regions = {self.menu: bytearray(0xA200)}
        self.events = []
        self.reads = []
        self.set_integer(ITEM.DEPTH_OFFSET, 1)
        self.set_integer(ITEM.COMPANION_ICON_OFFSET, 0x12345678)
        self.set_vector(0, self.root_data, [45, 9], selected=0)
        self.set_vector(1, self.child_data, [46, 50], selected=0)
        self.set_vector(2, 0x5550000, [], selected=-1)
        self.guard = Mock()
        self.guard.authorize_append.side_effect = self.authorize
        self.constructor = Mock(side_effect=self.construct)
        self.append_callback = Mock(side_effect=self.append)

    def set_integer(self, offset, value, *, signed=False):
        self.regions[self.menu][offset:offset + 4] = value.to_bytes(4, "little", signed=signed)

    def set_vector(self, depth, pointer, actions, *, selected=0, capacity=None):
        if capacity is None:
            capacity = len(actions)
        start = ITEM.VECTORS_OFFSET + depth * ITEM.VECTOR_SIZE
        header = (capacity.to_bytes(4, "little") + len(actions).to_bytes(4, "little")
                  + pointer.to_bytes(8, "little"))
        self.regions[self.menu][start:start + 16] = header
        self.set_integer(ITEM.SELECTIONS_OFFSET + depth * 4, selected, signed=True)
        values = bytearray()
        for index, action in enumerate(actions):
            entry = bytearray([0x60 + index % 20] * ITEM.ITEM_SIZE)
            entry[ITEM.ACTION_OFFSET:ITEM.ACTION_OFFSET + 4] = action.to_bytes(4, "little")
            entry[ITEM.MARKER_OFFSET:ITEM.MARKER_OFFSET + 16] = bytes(16)
            values.extend(entry)
        self.regions[pointer] = values

    def reader(self, address, size):
        self.reads.append((address, size))
        for start, data in self.regions.items():
            offset = address - start
            if 0 <= offset <= len(data) - size:
                return bytes(data[offset:offset + size])
        raise OSError("private fake address was unreadable")

    def authorize(self, menu):
        self.assertEqual(menu, self.menu)
        self.events.append("guard")
        return True

    def construct(self, buffer, icon, action, disabled, background):
        self.events.append("construct")
        self.assertIs(type(buffer), bytearray)
        self.assertEqual(buffer, bytes(ITEM.ITEM_SIZE))
        self.assertEqual((icon, action, disabled, background), (0x12345678, 0, False, True))
        # Simulate native construction, including recognizable opaque fields.
        buffer[:] = bytes([0x3A]) * ITEM.ITEM_SIZE
        buffer[:4] = icon.to_bytes(4, "little")
        buffer[4:8] = action.to_bytes(4, "little")
        buffer[0x4C:0x4E] = bytes((int(disabled), int(background)))
        buffer[ITEM.SLOT_OFFSET:ITEM.SLOT_OFFSET + 4] = b"\xff" * 4
        buffer[ITEM.BINDING_OFFSET:ITEM.BINDING_OFFSET + 4] = b"\xff" * 4
        buffer[ITEM.MARKER_OFFSET:ITEM.MARKER_OFFSET + 16] = bytes(16)
        self.constructed = bytes(buffer)

    def append(self, header_address, data):
        self.events.append("append")
        self.assertEqual(header_address, self.menu + ITEM.VECTORS_OFFSET + 16)
        self.assertIs(type(data), bytes)
        self.assertEqual(len(data), ITEM.ITEM_SIZE)
        header_offset = ITEM.VECTORS_OFFSET + 16
        header = self.regions[self.menu][header_offset:header_offset + 16]
        pointer = int.from_bytes(header[8:16], "little")
        count = int.from_bytes(header[4:8], "little")
        capacity = int.from_bytes(header[:4], "little")
        # Simulate a native allocator-owned relocation, never an actual address.
        old = bytes(self.regions[pointer][:count * ITEM.ITEM_SIZE])
        destination = pointer if count < capacity else 0x6660000
        self.regions[destination] = bytearray(old + data)
        self.regions[self.menu][header_offset:header_offset + 16] = (
            max(capacity, count + 1).to_bytes(4, "little")
            + (count + 1).to_bytes(4, "little") + destination.to_bytes(8, "little"))

    def request(self, **overrides):
        arguments = dict(constructor=self.constructor, append=self.append_callback,
                         guard_capability=self.guard)
        arguments.update(overrides)
        return ITEM.append_inert_item(self.reader, self.menu, **arguments)

    def tag(self, index, *, pointer=None, marker=ITEM.CUSTOM_ACTION_MARKER, action=0):
        if pointer is None:
            pointer = self.child_data
        start = index * ITEM.ITEM_SIZE
        self.regions[pointer][start + 4:start + 8] = action.to_bytes(4, "little")
        self.regions[pointer][start + ITEM.MARKER_OFFSET:start + ITEM.MARKER_OFFSET + 16] = marker


class GuardAndConstructionTests(ItemFixture):
    def test_default_or_unverified_capability_refuses_before_reads_or_callbacks(self):
        for guard in (None, True, object(), Mock(authorize_append=Mock(return_value=1)),
                      Mock(authorize_append=Mock(return_value=False))):
            with self.subTest(guard_type=type(guard).__name__), self.assertRaises(ITEM.MenuItemError):
                self.request(guard_capability=guard)
        self.assertEqual(self.reads, [])
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()

    def test_authorized_append_orders_callbacks_and_preserves_native_item_fields(self):
        original_root = bytes(self.regions[self.root_data])
        original_neighbors = bytes(self.regions[self.child_data])
        self.assertIs(self.request(), ITEM.AppendStatus.APPENDED)
        self.assertEqual(self.events, ["guard", "construct", "guard", "append"])
        self.assertEqual(self.guard.authorize_append.call_count, 2)
        payload = self.append_callback.call_args.args[1]
        expected = bytearray(self.constructed)
        expected[0x88:0x98] = ITEM.CUSTOM_ACTION_MARKER
        expected[0x98:0xD8] = bytes(64)
        self.assertEqual(payload, bytes(expected))
        self.assertEqual(bytes(self.regions[self.root_data]), original_root)
        self.assertEqual(bytes(self.regions[0x6660000][:-224]), original_neighbors)
        self.assertEqual(self.regions[self.menu][ITEM.SELECTIONS_OFFSET + 4:ITEM.SELECTIONS_OFFSET + 8],
                         bytes(4))

    def test_expired_guard_after_construction_prevents_append(self):
        self.guard.authorize_append.side_effect = [True, False]
        with self.assertRaises(ITEM.MenuItemError):
            self.request()
        self.constructor.assert_called_once()
        self.append_callback.assert_not_called()

    def test_guard_and_constructor_errors_are_sanitized_and_never_append(self):
        self.guard.authorize_append.side_effect = RuntimeError("private pointer identity")
        with self.assertRaises(ITEM.MenuItemError) as failure:
            self.request()
        self.assertNotIn("private", str(failure.exception))
        self.guard.authorize_append.side_effect = self.authorize
        self.constructor.side_effect = RuntimeError("private pointer identity")
        with self.assertRaises(ITEM.MenuItemError) as failure:
            self.request()
        self.assertNotIn("private", str(failure.exception))
        self.append_callback.assert_not_called()

    def test_constructor_must_initialize_known_fields_and_keep_exact_owned_size(self):
        for mutation in (lambda data: data.extend(b"x"),
                         lambda data: data.__setitem__(4, 46),
                         lambda data: data.__setitem__(0x4C, 1),
                         lambda data: data.__setitem__(0x4D, 0),
                         lambda data: data.__setitem__(0x84, 0),
                         lambda data: data.__setitem__(0xD8, 0),
                         lambda data: data.__setitem__(0x88, 1)):
            with self.subTest(mutation=mutation):
                def bad_constructor(buffer, *args):
                    self.construct(buffer, *args)
                    mutation(buffer)
                self.constructor.side_effect = bad_constructor
                with self.assertRaises(ITEM.MenuItemError):
                    self.request()
        self.append_callback.assert_not_called()

    def test_changed_context_or_borrowed_icon_after_constructor_prevents_append(self):
        for field, value in ((ITEM.DEPTH_OFFSET, 2), (ITEM.COMPANION_ICON_OFFSET, 99),
                             (ITEM.SELECTIONS_OFFSET + 4, 1)):
            with self.subTest(field=field):
                self.setUp()
                def mutating_constructor(buffer, *args):
                    self.construct(buffer, *args)
                    self.set_integer(field, value)
                self.constructor.side_effect = mutating_constructor
                with self.assertRaises(ITEM.MenuItemError):
                    self.request()
                self.append_callback.assert_not_called()

    def test_second_authorization_cannot_hide_a_changed_vector(self):
        def authorize(menu):
            if self.guard.authorize_append.call_count == 2:
                self.set_vector(1, 0x7770000, [46, 50])
            return True
        self.guard.authorize_append.side_effect = authorize
        with self.assertRaises(ITEM.MenuItemError):
            self.request()
        self.append_callback.assert_not_called()

    def test_append_failure_never_retries_or_attempts_rollback(self):
        def fail_after_append(header, data):
            self.append(header, data)
            raise OSError("private native address")
        self.append_callback.side_effect = fail_after_append
        with self.assertRaises(ITEM.MenuItemError) as failure:
            self.request()
        self.assertIn("outcome is unverified", str(failure.exception))
        self.assertNotIn("private", str(failure.exception))
        self.append_callback.assert_called_once()
        self.assertIs(ITEM.plan_append(self.reader, self.menu), ITEM.AppendStatus.ALREADY_PRESENT)


class ContextAndIdentityTests(ItemFixture):
    def test_marker_is_full_128_bits_and_public_inspection_has_no_pointers(self):
        self.assertEqual(len(ITEM.CUSTOM_ACTION_MARKER), 16)
        view = ITEM.inspect_menu(self.reader, self.menu)
        self.assertEqual((view.depth, view.parent_action, view.selected_action), (1, 45, 46))
        for pointer in (self.menu, self.root_data, self.child_data):
            self.assertNotIn(str(pointer), repr(view))
        self.assertEqual(set(vars(view)), {"depth", "capacity", "count", "selected_index",
                                          "selected_action", "parent_action", "custom_indices"})

    def test_repeat_call_is_idempotent_after_native_vector_relocation(self):
        self.assertIs(self.request(), ITEM.AppendStatus.APPENDED)
        self.assertIs(self.request(), ITEM.AppendStatus.ALREADY_PRESENT)
        self.constructor.assert_called_once()
        self.append_callback.assert_called_once()
        self.assertEqual(ITEM.inspect_menu(self.reader, self.menu).custom_indices, (2,))

    def test_natural_rebuild_without_candidate_can_append_once_again(self):
        self.request()
        self.set_vector(1, self.child_data, [46, 50])
        self.assertIs(self.request(), ITEM.AppendStatus.APPENDED)
        self.assertIs(self.request(), ITEM.AppendStatus.ALREADY_PRESENT)
        self.assertEqual(self.append_callback.call_count, 2)

    def test_root_paged_or_unrelated_parent_context_does_not_construct(self):
        for depth, parent_action in ((0, 45), (2, 45), (1, 47), (1, 9)):
            with self.subTest(depth=depth, parent_action=parent_action):
                self.set_integer(ITEM.DEPTH_OFFSET, depth)
                self.regions[self.root_data][4:8] = parent_action.to_bytes(4, "little")
                self.assertIs(self.request(), ITEM.AppendStatus.NOT_COMPANION_CONTEXT)
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()

    def test_parent_selection_must_be_in_range_but_child_selection_can_be_stale(self):
        self.set_integer(ITEM.SELECTIONS_OFFSET, -1, signed=True)
        self.assertIs(ITEM.plan_append(self.reader, self.menu), ITEM.AppendStatus.NOT_COMPANION_CONTEXT)
        self.set_integer(ITEM.SELECTIONS_OFFSET, 0)
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, -1, signed=True)
        self.assertIs(ITEM.plan_append(self.reader, self.menu), ITEM.AppendStatus.READY)
        self.assertIsNone(ITEM.selected_label(self.reader, self.menu))

    def test_empty_direct_submenu_allows_native_allocation(self):
        self.set_vector(1, 0, [], selected=-1)
        self.assertIs(self.request(), ITEM.AppendStatus.APPENDED)
        self.assertEqual(ITEM.inspect_menu(self.reader, self.menu).count, 1)

    def test_partial_marker_or_untagged_none_is_not_ours(self):
        marker = ITEM.CUSTOM_ACTION_MARKER
        for changed_index in range(16):
            changed = bytearray(marker)
            changed[changed_index] ^= 0xFF
            self.tag(0, marker=bytes(changed))
            self.assertIs(ITEM.plan_append(self.reader, self.menu), ITEM.AppendStatus.READY)
            self.assertIsNone(ITEM.selected_label(self.reader, self.menu))

    def test_duplicate_marker_or_marker_on_real_action_fails_closed(self):
        self.tag(0)
        self.tag(1)
        with self.assertRaises(ITEM.MenuItemError):
            self.request()
        self.set_vector(1, self.child_data, [46, 50])
        self.tag(0, action=46)
        with self.assertRaises(ITEM.MenuItemError):
            ITEM.selected_label(self.reader, self.menu)
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()

    def test_candidate_added_during_construction_is_not_duplicated(self):
        def constructor(buffer, *args):
            self.construct(buffer, *args)
            self.tag(1)
        self.constructor.side_effect = constructor
        self.assertIs(self.request(), ITEM.AppendStatus.ALREADY_PRESENT)
        self.append_callback.assert_not_called()

    def test_only_selected_exact_candidate_has_a_label(self):
        self.tag(1)
        self.assertIsNone(ITEM.selected_label(self.reader, self.menu))
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 1)
        self.assertEqual(ITEM.selected_label(self.reader, self.menu), b"Companion Auto Summon")
        self.assertEqual(ITEM.selected_label(self.reader, self.menu, label="x" * 127), b"x" * 127)
        self.assertEqual(self.events, [])

    def test_label_bounds_reject_non_ascii_nul_empty_and_overlength(self):
        for value in ("", "x\0y", "\u00e9", "x" * 128, None, b"label"):
            with self.subTest(value_type=type(value).__name__), self.assertRaises(ITEM.MenuItemError):
                ITEM.selected_label(self.reader, self.menu, label=value)
        self.assertEqual(self.reads, [])


class BoundsTests(ItemFixture):
    def test_invalid_depth_and_parent_capacity_count_are_rejected(self):
        self.set_integer(ITEM.DEPTH_OFFSET, 3)
        with self.assertRaises(ITEM.MenuItemError):
            ITEM.plan_append(self.reader, self.menu)
        self.set_integer(ITEM.DEPTH_OFFSET, 1)
        for capacity, count in ((0, 1), (257, 1), (0xFFFFFFFF, 1)):
            self.set_integer(ITEM.VECTORS_OFFSET, capacity)
            self.set_integer(ITEM.VECTORS_OFFSET + 4, count)
            with self.subTest(capacity=capacity, count=count), self.assertRaises(ITEM.MenuItemError):
                ITEM.plan_append(self.reader, self.menu)

    def test_count_and_capacity_limit_does_not_allow_a_257th_entry(self):
        self.set_vector(1, self.child_data, [46] * 256)
        with self.assertRaises(ITEM.MenuItemError):
            self.request()
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()

    def test_invalid_occupied_pointer_is_rejected_before_item_reads(self):
        start = ITEM.VECTORS_OFFSET + 16 + 8
        for pointer in (0, 1, 0x7FFFFFFFFFFF):
            self.regions[self.menu][start:start + 8] = pointer.to_bytes(8, "little")
            with self.subTest(pointer=pointer), self.assertRaises(ITEM.MenuItemError):
                ITEM.inspect_menu(self.reader, self.menu)
        self.assertTrue(all(address >= self.menu for address, _ in self.reads))

    def test_empty_vector_with_nonzero_capacity_cannot_append_through_null_pointer(self):
        self.set_vector(1, 0, [], selected=-1, capacity=8)
        with self.assertRaises(ITEM.MenuItemError):
            self.request()
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()

    def test_allocation_range_is_checked_beyond_only_initialized_items(self):
        pointer = ITEM.MAX_USER_ADDRESS - ITEM.ITEM_SIZE + 1
        self.set_vector(1, pointer, [46], capacity=2)
        with self.assertRaises(ITEM.MenuItemError):
            self.request()
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()

    def test_reader_failure_short_copy_and_unowned_copy_have_sanitized_errors(self):
        for reader in (Mock(side_effect=OSError("sensitive private pointer")),
                       Mock(return_value=b"\0"), Mock(return_value=bytearray(4))):
            with self.subTest(reader=reader), self.assertRaises(ITEM.MenuItemError) as failure:
                ITEM.inspect_menu(reader, self.menu)
            self.assertNotIn("private", str(failure.exception))

    def test_invalid_menu_identity_never_reads_or_calls_guard(self):
        for menu in (None, True, 0, -1, 0x7FFFFFFFFFFF):
            with self.subTest(menu_type=type(menu).__name__), self.assertRaises(ITEM.MenuItemError):
                ITEM.append_inert_item(self.reader, menu, constructor=self.constructor,
                                       append=self.append_callback, guard_capability=self.guard)
        self.assertEqual(self.reads, [])
        self.guard.authorize_append.assert_not_called()


if __name__ == "__main__":
    unittest.main()
