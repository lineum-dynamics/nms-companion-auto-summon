"""Texture-owner checks using owned buffers and a synthetic resource table."""

import ctypes as C
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock


SOURCE = Path(__file__).resolve().parents[1] / "quick_menu_icon.py"
SPEC = importlib.util.spec_from_file_location("quick_menu_icon_under_test", SOURCE)
ICON = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ICON
SPEC.loader.exec_module(ICON)


class IconOwnerTests(unittest.TestCase):
    def setUp(self):
        self.slot = 0x71100000
        self.retain_slot = self.slot + ICON.RETAIN_MANAGER_PTR_RVA - ICON.MANAGER_PTR_RVA
        self.manager = 0x2220000
        self.table = 0x3330000
        self.paw = 0x4440000
        self.custom = 0x5550000
        self.menu = 0x6660000
        self.regions = {
            self.slot: bytearray(8),
            self.retain_slot: bytearray(8),
            self.manager: bytearray(0x68),
            self.table: bytearray(16),
            self.paw: bytearray(0x270),
            self.custom: bytearray(0x270),
            self.menu: bytearray(0xA108),
        }
        self.write(self.slot, self.manager, 8)
        self.write(self.retain_slot, self.manager, 8)
        self.write(self.manager + 0x5C, 2)
        self.write(self.manager + 0x60, self.table, 8)
        self.write(self.table, self.paw, 8)
        self.write(self.table + 8, self.custom, 8)
        self.write(self.menu + ICON.COMPANION_ICON_OFFSET, 1)
        self.resource(self.paw, b"TEXTURES/UI/FRONTEND/ICONS/SUMMONPET.DDS", image=77)
        self.resource(self.custom, ICON.VIRTUAL_PATH, image=88)
        self.events = []
        self.reads = []
        self.pinned = []
        self.owner = ICON.IconOwner()
        self.pin = Mock(side_effect=self.pin_owner)
        self.load = Mock(side_effect=self.load_texture)
        self.retain = Mock(side_effect=self.retain_handle)

    def write(self, address, value, size=4):
        data = value if isinstance(value, bytes) else value.to_bytes(size, "little")
        for start, region in self.regions.items():
            offset = address - start
            if 0 <= offset <= len(region) - len(data):
                region[offset:offset + len(data)] = data
                return
        raise AssertionError("Synthetic write outside owned test regions")

    def resource(self, address, name, *, image=0, texture=0):
        self.write(address + 8, 7)
        self.write(address + 0xC, name + bytes(256 - len(name)))
        self.write(address + 0x1E0, image)
        self.write(address + 0x260, texture, 8)

    def reader(self, address, size):
        self.assertIn(size, (1, 4, 8, 16))
        self.reads.append((address, size))
        for start, region in self.regions.items():
            offset = address - start
            if 0 <= offset <= len(region) - size:
                return bytes(region[offset:offset + size])
        raise OSError("Synthetic region unavailable")

    def pin_owner(self, owner):
        self.events.append("pin")
        self.pinned.append(owner)
        return True

    def load_texture(self, record):
        self.events.append("load")
        self.assertEqual(self.pinned, [self.owner])
        self.assertEqual(record % 16, 0)
        raw = C.string_at(record, ICON.RECORD_SIZE)
        self.assertEqual(raw[8:], bytes(16))
        path = C.c_void_p.from_address(record).value
        self.assertEqual(C.string_at(path), ICON.VIRTUAL_PATH)
        C.c_uint32.from_address(record + ICON.HANDLE_OFFSET).value = 2

    def retain_handle(self, pointer):
        self.events.append("retain")
        self.assertEqual(self.pinned, [self.owner])
        self.assertEqual(C.c_uint32.from_address(pointer).value, 1)
        count = int.from_bytes(self.reader(self.paw + 0x134, 4), "little")
        self.write(self.paw + 0x134, count + 1)

    def register(self, **overrides):
        kwargs = dict(load_texture=self.load, retain_handle=self.retain, pin_owner=self.pin)
        kwargs.update(overrides)
        return self.owner.register_once(self.reader, self.menu, self.slot, **kwargs)

    def handle(self, reader=None, slot=None):
        return self.owner.icon_handle(reader or self.reader, self.slot if slot is None else slot)

    def test_initial_owner_neither_calls_native_nor_reads(self):
        self.assertEqual(self.owner.status, "not_observed")
        self.assertFalse(self.owner.attempted)
        self.assertEqual(self.handle(), 0)
        self.assertEqual(self.reads, [])
        self.assertEqual(self.events, [])

    def test_registration_pins_before_both_native_calls(self):
        menu_before = bytes(self.regions[self.menu])
        self.assertTrue(self.register())
        self.assertEqual(self.events, ["pin", "retain", "load"])
        self.assertEqual(self.handle(), 2)
        self.assertEqual(self.owner.status, "custom_ready")
        self.assertEqual(bytes(self.regions[self.menu]), menu_before)

    def test_repeated_registration_never_calls_or_reads_again(self):
        self.assertTrue(self.register())
        before = list(self.reads)
        self.assertFalse(self.register())
        self.assertEqual(self.reads, before)
        self.assertEqual(self.events, ["pin", "retain", "load"])

    def test_pending_custom_uses_owned_paw_then_promotes_without_calls(self):
        self.write(self.custom + 0x1E0, 0)
        self.assertTrue(self.register())
        self.assertEqual(self.handle(), 1)
        self.assertEqual(self.owner.status, "native_ready")
        self.write(self.custom + 0x260, 0x1234567800000000, 8)
        self.assertEqual(self.handle(), 2)
        self.assertEqual(self.events, ["pin", "retain", "load"])

    def test_no_menu_read_after_initialization(self):
        self.assertTrue(self.register())
        del self.regions[self.menu]
        self.reads.clear()
        self.assertEqual(self.handle(), 2)
        self.assertFalse(any(self.menu <= address < self.menu + 0xA108 for address, _ in self.reads))

    def test_noquery_byte_does_not_reject_loaded_texture(self):
        self.write(self.custom + 0x139, 1, 1)
        self.assertTrue(self.register())
        self.assertEqual(self.handle(), 2)

    def test_error_or_substitution_cannot_display_original_or_default(self):
        for field in (0x13A, 0x13B):
            with self.subTest(field=field):
                self.setUp()
                self.write(self.custom + field, 1, 1)
                self.assertTrue(self.register())
                self.assertEqual(self.handle(), 1)

    def test_missing_asset_zero_handle_keeps_retained_paw(self):
        self.load.side_effect = lambda _: None
        self.assertTrue(self.register())
        self.assertEqual(self.handle(), 1)

    def test_wrong_custom_name_never_accepts_unrelated_texture(self):
        self.resource(self.custom, b"OTHER.DDS", image=99)
        self.assertTrue(self.register())
        self.assertEqual(self.handle(), 1)

    def test_empty_or_unterminated_custom_name_falls_back(self):
        self.write(self.custom + 0xC, bytes(256))
        self.assertTrue(self.register())
        self.assertEqual(self.handle(), 1)
        self.setUp()
        self.write(self.custom + 0xC, b"X" * 256)
        self.assertFalse(self.register())
        self.assertEqual(self.handle(), 1)

    def test_no_usable_native_icon_produces_text_only_until_custom_ready(self):
        self.write(self.paw + 0x1E0, 0)
        self.write(self.custom + 0x1E0, 0)
        self.assertTrue(self.register())
        self.retain.assert_not_called()
        self.assertEqual(self.handle(), 0)
        self.write(self.custom + 0x1E0, 5)
        self.assertEqual(self.handle(), 2)

    def test_substituted_paw_never_retains_default_resource(self):
        self.write(self.paw + 0x13B, 1, 1)
        self.assertTrue(self.register())
        self.retain.assert_not_called()
        self.assertEqual(self.handle(), 2)

    def test_invalid_handles_or_resource_type_are_not_usable(self):
        for handle in (0, 3, 0x80000000, 0xFFFFFFFF):
            with self.subTest(handle=handle):
                self.setUp()
                self.load.side_effect = lambda record: setattr(C.c_uint32.from_address(record + 16), "value", handle)
                self.assertTrue(self.register())
                self.assertEqual(self.handle(), 1)
        self.setUp()
        self.write(self.custom + 8, 6)
        self.assertTrue(self.register())
        self.assertEqual(self.handle(), 1)

    def test_pin_refusal_and_pin_exception_prevent_native_calls(self):
        for answer in (False, None, 1, RuntimeError("pin failed")):
            with self.subTest(answer=answer):
                self.setUp()
                self.pin.side_effect = answer if isinstance(answer, Exception) else None
                self.pin.return_value = answer
                self.assertFalse(self.register())
                self.retain.assert_not_called()
                self.load.assert_not_called()
                self.assertEqual(self.handle(), 0)
                self.assertFalse(self.register())

    def test_loader_exception_preserves_pinned_owned_paw(self):
        self.load.side_effect = RuntimeError("native wrapper failed")
        self.assertFalse(self.register())
        self.assertEqual(self.pinned, [self.owner])
        self.assertEqual(self.handle(), 1)
        self.assertFalse(self.register())

    def test_unknown_partial_retain_never_exposes_unconfirmed_paw(self):
        def partial(pointer):
            self.retain_handle(pointer)
            raise RuntimeError("return path failed")
        self.retain.side_effect = partial
        self.assertFalse(self.register())
        self.assertEqual(self.pinned, [self.owner])
        self.load.assert_not_called()
        self.assertEqual(self.handle(), 0)

    def test_manager_change_or_null_disables_permanently(self):
        for changed in (0, 0x7770000):
            with self.subTest(changed=changed):
                self.setUp()
                self.assertTrue(self.register())
                self.write(self.slot, changed, 8)
                self.assertEqual(self.handle(), 0)
                self.write(self.slot, self.manager, 8)
                self.reads.clear()
                self.assertEqual(self.handle(), 0)
                self.assertEqual(self.reads, [])

    def test_distinct_loader_and_retain_managers_prevent_native_calls(self):
        for value in (0, 0x7770000):
            with self.subTest(value=value):
                self.setUp()
                self.write(self.retain_slot, value, 8)
                self.assertFalse(self.register())
                self.pin.assert_not_called()
                self.load.assert_not_called()
                self.retain.assert_not_called()
                self.write(self.retain_slot, self.manager, 8)
                self.assertEqual(self.handle(), 0)

    def test_retain_manager_change_alone_disables_existing_provider(self):
        self.assertTrue(self.register())
        self.write(self.retain_slot, 0, 8)
        self.assertEqual(self.handle(), 0)
        self.write(self.retain_slot, self.manager, 8)
        self.reads.clear()
        self.assertEqual(self.handle(), 0)
        self.assertEqual(self.reads, [])

    def test_different_manager_slot_disables_without_dereference(self):
        self.assertTrue(self.register())
        self.reads.clear()
        self.assertEqual(self.handle(slot=self.slot + 8), 0)
        self.assertEqual(self.reads, [])

    def test_manager_transition_inside_resource_read_disables_permanently(self):
        for transition_read in (2, 3):
            with self.subTest(transition_read=transition_read):
                self.setUp()
                self.assertTrue(self.register())
                slot_reads = 0
                def changing_slot(address, size):
                    nonlocal slot_reads
                    value = self.reader(address, size)
                    if address == self.slot:
                        slot_reads += 1
                        if slot_reads == transition_read:
                            return bytes(8)
                    return value
                self.assertEqual(self.handle(reader=changing_slot), 0)
                self.assertEqual(self.owner.status, "manager_changed")
                self.reads.clear()
                self.assertEqual(self.handle(), 0)
                self.assertEqual(self.reads, [])

    def test_manager_transition_during_registration_disables_owned_fallback(self):
        def changing_loader(record):
            self.load_texture(record)
            self.write(self.slot, 0, 8)
        self.load.side_effect = changing_loader
        self.assertFalse(self.register())
        self.assertEqual(self.pinned, [self.owner])
        self.write(self.slot, self.manager, 8)
        self.reads.clear()
        self.assertEqual(self.handle(), 0)
        self.assertEqual(self.reads, [])

    def test_resource_identity_reuse_cannot_return_stale_owned_handle(self):
        for changed in ("pointer", "name", "type", "empty"):
            with self.subTest(changed=changed):
                self.setUp()
                self.assertTrue(self.register())
                if changed == "pointer":
                    self.regions[0x7770000] = bytearray(self.regions[self.custom])
                    self.write(self.table + 8, 0x7770000, 8)
                elif changed == "name":
                    self.resource(self.custom, b"OTHER.DDS", image=22)
                elif changed == "type":
                    self.write(self.custom + 8, 8)
                else:
                    self.write(self.table + 8, 0, 8)
                self.assertEqual(self.handle(), 0)
                self.assertEqual(self.owner.status, "resource_identity_changed")

    def test_table_growth_between_calls_uses_fresh_entry(self):
        self.assertTrue(self.register())
        self.regions[0x7770000] = bytearray(self.regions[self.table]) + bytearray(8)
        self.write(self.manager + 0x60, 0x7770000, 8)
        self.write(self.manager + 0x5C, 3)
        self.assertEqual(self.handle(), 2)

    def test_midread_table_or_readiness_change_fails_current_sample(self):
        self.assertTrue(self.register())
        for field, size, value in ((self.manager + 0x5C, 4, 3), (self.custom + 0x1E0, 4, 0)):
            with self.subTest(field=field):
                self.write(self.manager + 0x5C, 2)
                self.write(self.custom + 0x1E0, 88)
                changed = False
                def mutating(address, amount):
                    nonlocal changed
                    result = self.reader(address, amount)
                    if address == field and not changed:
                        changed = True
                        self.write(field, value, size)
                    return result
                self.assertEqual(self.handle(reader=mutating), 0)

    def test_short_nonbytes_and_exception_reads_fail_without_native_calls(self):
        self.assertTrue(self.register())
        for bad in (b"", bytearray(8), None):
            with self.subTest(bad=bad):
                self.assertEqual(self.handle(reader=lambda *_: bad), 0)
        self.assertEqual(self.handle(reader=Mock(side_effect=OSError("unreadable"))), 0)
        self.assertEqual(self.events, ["pin", "retain", "load"])

    def test_registration_reentry_and_read_reentry_do_not_deadlock(self):
        original = self.load_texture
        def reentry(record):
            self.assertFalse(self.register())
            self.assertEqual(self.handle(), 0)
            original(record)
        self.load.side_effect = reentry
        self.assertTrue(self.register())
        self.assertEqual(self.handle(), 2)
        self.assertEqual(self.events, ["pin", "retain", "load"])

    def test_bounded_read_sizes_and_worst_case_name(self):
        self.resource(self.paw, b"P" * 255, image=4)
        self.assertTrue(self.register())
        self.write(self.custom + 0x1E0, 0)
        self.reads.clear()
        self.assertEqual(self.handle(), 1)
        self.assertLessEqual(len(self.reads), 100)
        self.assertTrue(all(size in (1, 4, 8, 16) for _, size in self.reads))

    def test_invalid_initial_pointer_stops_before_pinning(self):
        for slot in (0, True, ICON.MAX_ADDRESS, -1):
            with self.subTest(slot=slot):
                owner = ICON.IconOwner()
                self.assertFalse(owner.register_once(self.reader, self.menu, slot,
                    load_texture=self.load, retain_handle=self.retain, pin_owner=self.pin))
        self.pin.assert_not_called()
        self.load.assert_not_called()
        self.retain.assert_not_called()


if __name__ == "__main__":
    unittest.main()
