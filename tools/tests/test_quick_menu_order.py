"""Early ordering checks with owned source items and synthetic vector storage."""

from pathlib import Path
import sys
import unittest

from test_quick_menu_submenu import SUB, SubmenuFixture


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import quick_menu_order as ORDER
finally:
    sys.path.pop(0)
ITEM = ORDER.item


class OrderFixture(SubmenuFixture):
    def setUp(self):
        super().setUp()
        self.set_vector(1, self.child_data, [40, 50], selected=0)
        self.incoming = 0x9990000
        self.incoming_bytes = bytearray([0x5A] * ITEM.ITEM_SIZE)
        self.incoming_bytes[4:8] = (46).to_bytes(4, "little")
        self.regions[self.incoming] = self.incoming_bytes

    def order(self, **changes):
        arguments = dict(constructor=self.constructor, append=self.append_callback,
                         guard_capability=self.guard)
        arguments.update(changes)
        return ORDER.append_before_pet(self.reader, self.menu, self.incoming, **arguments)

    def append_original(self):
        self.append(self.menu + ITEM.VECTORS_OFFSET + ITEM.VECTOR_SIZE,
                    bytes(self.regions[self.incoming]))

    def actions(self, depth=1):
        pointer = self.vector_pointer(depth)
        offset = ITEM.VECTORS_OFFSET + depth * ITEM.VECTOR_SIZE + 4
        count = int.from_bytes(self.regions[self.menu][offset:offset + 4], "little")
        return [int.from_bytes(self.regions[pointer][index * ITEM.ITEM_SIZE + 4:
                                                    index * ITEM.ITEM_SIZE + 8], "little")
                for index in range(count)]


class OrderingTests(OrderFixture):
    def test_general_actions_then_cas_then_unchanged_original_pet(self):
        source = bytes(self.regions[self.incoming])
        general = bytes(self.regions[self.child_data])
        scalars = bytes(self.regions[self.menu][ITEM.SELECTIONS_OFFSET:ITEM.SELECTIONS_OFFSET + 12])
        self.assertIs(self.order(), True)
        self.assertEqual(self.actions(), [40, 50, 0])
        self.append_original()
        self.assertEqual(self.actions(), [40, 50, 0, 46])
        pointer = self.vector_pointer(1)
        self.assertEqual(bytes(self.regions[pointer][:2 * ITEM.ITEM_SIZE]), general)
        self.assertEqual(bytes(self.regions[pointer][3 * ITEM.ITEM_SIZE:]), source)
        self.assertEqual(bytes(self.regions[self.incoming]), source)
        self.assertEqual(bytes(self.regions[self.menu][ITEM.SELECTIONS_OFFSET:ITEM.SELECTIONS_OFFSET + 12]), scalars)
        self.assertEqual(self.reader(self.menu + ITEM.DEPTH_OFFSET, 4), b"\x01\0\0\0")
        self.assertEqual(self.regions[self.menu][0xA16C], 0)

    def test_pet_page_also_receives_parent_before_original(self):
        self.regions[self.incoming][4:8] = (47).to_bytes(4, "little")
        self.assertTrue(self.order())
        self.append_original()
        self.assertEqual(self.actions(), [40, 50, 0, 47])

    def test_existing_parent_prevents_duplicate_on_later_native_pets(self):
        self.assertTrue(self.order())
        self.append_original()
        self.assertFalse(self.order())
        self.append_original()
        self.assertEqual(self.actions(), [40, 50, 0, 46, 46])
        self.constructor.assert_called_once()
        self.append_callback.assert_called_once()

    def test_parent_position_is_stable_across_rebuild_and_depth_two_population(self):
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2)
        self.assertTrue(self.order())
        self.append_original()
        result = self.request()
        self.assertFalse(result.root_added)
        self.assertTrue(result.child_added)
        self.assertEqual(SUB._snapshot(self.reader, self.menu)[0].parent_index, 2)
        self.set_integer(ITEM.DEPTH_OFFSET, 2)
        self.set_vector(1, self.child_data, [40, 50], selected=2)
        self.set_vector(2, 0x5550000, [], selected=0)
        self.assertTrue(self.order())
        self.append_original()
        result = self.request()
        self.assertTrue(result.child_ready)
        self.assertTrue(result.page_active)
        self.assertEqual(SUB._snapshot(self.reader, self.menu)[0].parent_index, 2)
        self.assertEqual(self.actions(), [40, 50, 0, 46])
        self.assertEqual(self.actions(2), [0])

    def test_no_pets_uses_existing_builder_completion_fallback(self):
        self.regions[self.incoming][4:8] = (50).to_bytes(4, "little")
        self.assertFalse(self.order())
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()
        result = self.request()
        self.assertTrue(result.root_added)
        self.assertEqual(self.actions(), [40, 50, 0])

    def test_no_general_actions_allows_cas_to_be_first(self):
        self.set_vector(1, self.child_data, [], selected=0)
        self.assertTrue(self.order())
        self.append_original()
        self.assertEqual(self.actions(), [0, 46])

    def test_non_pet_sources_and_outside_context_do_not_construct(self):
        for action, depth, root_selected in ((0, 1, 0), (50, 1, 0), (45, 1, 0),
                                              (46, 0, 0), (46, 1, 1), (47, 2, 1)):
            with self.subTest(action=action, depth=depth):
                self.setUp()
                self.regions[self.incoming][4:8] = action.to_bytes(4, "little")
                self.set_integer(ITEM.DEPTH_OFFSET, depth)
                self.set_integer(ITEM.SELECTIONS_OFFSET, root_selected)
                self.assertFalse(self.order())
                self.constructor.assert_not_called()
                self.append_callback.assert_not_called()

    def test_missed_first_pet_cannot_cause_late_insertion(self):
        self.set_vector(1, self.child_data, [40, 50, 46], selected=0)
        with self.assertRaisesRegex(ORDER.MenuItemError, "already precede"):
            self.order()
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()


class SourceAndFailureTests(OrderFixture):
    def test_alias_inside_any_vector_allocation_is_rejected_including_spare_capacity(self):
        for depth, unused in ((0, False), (1, False), (2, False),
                              (0, True), (1, True), (2, True)):
            with self.subTest(depth=depth, unused=unused):
                self.setUp()
                pointer = (self.root_data, self.child_data, 0x5550000)[depth]
                if unused:
                    actions = [45] if depth == 0 else [50]
                    source_index = 2
                else:
                    actions = [45, 46] if depth == 0 else [50, 46]
                    source_index = 1
                self.set_vector(depth, pointer, actions, selected=0, capacity=3)
                self.regions[pointer].extend(bytes((3 - len(actions)) * ITEM.ITEM_SIZE))
                self.incoming = pointer + source_index * ITEM.ITEM_SIZE
                self.regions[pointer][self.incoming - pointer + 4:self.incoming - pointer + 8] = (46).to_bytes(4, "little")
                with self.assertRaisesRegex(ORDER.MenuItemError, "overlaps"):
                    self.order()
                self.constructor.assert_not_called()
                self.append_callback.assert_not_called()

    def test_source_starting_before_vector_but_overlapping_it_is_rejected(self):
        self.incoming = self.child_data - 112
        self.regions[self.incoming] = bytearray(self.incoming_bytes)
        with self.assertRaisesRegex(ORDER.MenuItemError, "overlaps"):
            self.order()
        self.append_callback.assert_not_called()

    def test_malformed_vector_header_refuses_before_native_callbacks(self):
        for field, value in ((ITEM.VECTORS_OFFSET + 16, 1),
                             (ITEM.VECTORS_OFFSET + 16, 257),
                             (ITEM.DEPTH_OFFSET, 3)):
            with self.subTest(field=field, value=value):
                self.setUp()
                self.set_integer(field, value)
                with self.assertRaises(ORDER.MenuItemError):
                    self.order()
                self.constructor.assert_not_called()
                self.append_callback.assert_not_called()

    def test_guard_refusal_before_or_after_constructor_never_appends(self):
        for sequence in ([False], [True, False]):
            with self.subTest(sequence=sequence):
                self.setUp()
                self.guard.authorize_append.side_effect = sequence
                with self.assertRaises(ORDER.MenuItemError):
                    self.order()
                self.append_callback.assert_not_called()

    def test_changed_incoming_action_or_other_payload_after_constructor_is_rejected(self):
        for offset in (4, 0x60, 0x84, 0xD8):
            with self.subTest(offset=offset):
                self.setUp()
                def construct(buffer, *args):
                    self.construct(buffer, *args)
                    self.regions[self.incoming][offset] ^= 1
                self.constructor.side_effect = construct
                with self.assertRaises(ORDER.MenuItemError):
                    self.order()
                self.append_callback.assert_not_called()

    def test_changed_vector_identity_or_selection_after_constructor_is_rejected(self):
        for change in ("pointer", "selection", "count", "native_action"):
            with self.subTest(change=change):
                self.setUp()
                def construct(buffer, *args):
                    self.construct(buffer, *args)
                    if change == "pointer":
                        replacement = 0x8880000
                        self.regions[replacement] = self.regions[self.child_data][:]
                        offset = ITEM.VECTORS_OFFSET + 16 + 8
                        self.regions[self.menu][offset:offset + 8] = replacement.to_bytes(8, "little")
                    elif change == "selection":
                        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 1)
                    elif change == "count":
                        self.set_integer(ITEM.VECTORS_OFFSET + 16 + 4, 1)
                    else:
                        self.regions[self.child_data][4:8] = (46).to_bytes(4, "little")
                self.constructor.side_effect = construct
                with self.assertRaises(ORDER.MenuItemError):
                    self.order()
                self.append_callback.assert_not_called()

    def test_revocation_during_final_source_reads_prevents_native_append(self):
        def reader(address, size):
            data = self.reader(address, size)
            if self.constructor.called and address == self.incoming + 16:
                self.guard.authorize_append.side_effect = lambda menu: False
            return data
        with self.assertRaises(ORDER.MenuItemError):
            ORDER.append_before_pet(reader, self.menu, self.incoming,
                                    constructor=self.constructor, append=self.append_callback,
                                    guard_capability=self.guard)
        self.append_callback.assert_not_called()

    def test_native_append_failure_is_not_retried_or_rolled_back(self):
        def append_then_fail(header, data):
            self.append(header, data)
            raise OSError("synthetic failure after append")
        self.append_callback.side_effect = append_then_fail
        with self.assertRaises(ORDER.MenuItemError):
            self.order()
        self.append_callback.assert_called_once()
        self.assertEqual(self.actions(), [40, 50, 0])

    def test_unreadable_or_short_incoming_payload_is_rejected(self):
        for size in (8, 120):
            with self.subTest(size=size):
                self.setUp()
                self.regions[self.incoming] = self.regions[self.incoming][:size]
                with self.assertRaises(ORDER.MenuItemError):
                    self.order()
                self.constructor.assert_not_called()
                self.append_callback.assert_not_called()


if __name__ == "__main__":
    unittest.main()
