"""Offline adapter tests using owned ctypes memory and fake pyMHF modules.

These tests do not import the installed mod framework, locate a game process,
read the executable, or call native code. A fake Mod can be instantiated while
disabled solely so its ordinary Python callback methods can be exercised.
"""

import ctypes
import importlib.metadata
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


_SRC = Path(__file__).resolve().parents[1] / "src"


class FakeNativeFunction:
    def __init__(self, function, offset, declarations):
        self.function = function
        self.offset = offset
        declarations.append((function.__name__, offset))

    def before(self, callback):
        return callback

    def after(self, callback):
        return callback

    def __call__(self, *args, **kwargs):
        raise AssertionError("A native declaration must never execute in an offline test")


def load_runtime(*, injected=False, framework_version="0.2.4", version_error=None):
    """Compile the same concatenation as the build, with framework imports mocked."""
    # Read only our four source fragments, before replacing Path.open below.
    source = "\n\n".join(
        (_SRC / name).read_text(encoding="utf-8")
        for name in ("policy.py", "persistence.py", "settings.py", "runtime.py")
    )
    events = []
    declarations = []

    class FakeMod:
        def __init__(self):
            # Real Mod introspects the instance and evaluates GUI properties.
            # Backing fields must already exist when its constructor is called.
            for name, value in type(self).__dict__.items():
                if isinstance(value, property):
                    getattr(self, name)

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            events.append(("class-created", cls._disabled))

    internal = types.ModuleType("pymhf.core._internal")
    internal.IS_INJECTED = injected
    internal.BASE_ADDRESS = 1 if injected else 0
    internal.BINARY_PATH = "in-memory-test-executable-never-opened-on-disk.exe"
    pymhf = types.ModuleType("pymhf")
    pymhf.__path__ = []
    pymhf.Mod = FakeMod
    core = types.ModuleType("pymhf.core")
    core.__path__ = []
    core._internal = internal
    hooking = types.ModuleType("pymhf.core.hooking")
    gui = types.ModuleType("pymhf.gui")
    gui.__path__ = []
    gui_decorators = types.ModuleType("pymhf.gui.decorators")

    def gui_property(kind):
        def labelled(label):
            def decorate(function):
                function._test_gui_type = kind
                function._test_gui_label = label
                return function
            return decorate
        return labelled

    gui_decorators.BOOLEAN = gui_property("BOOLEAN")
    gui_decorators.STRING = gui_property("STRING")
    gui_decorators.ENUM = lambda label, enum: gui_property("ENUM")(label)
    gui.decorators = gui_decorators
    pymhf.gui = gui

    def static_hook(*, offset):
        return lambda function: FakeNativeFunction(function, offset, declarations)

    hooking.static_function_hook = static_hook
    pymhf.core = core
    core.hooking = hooking

    def fake_version(distribution):
        events.append(("version", distribution))
        if version_error is not None:
            raise version_error
        return framework_version

    def fake_open(path, mode="r", *args, **kwargs):
        events.append(("open", str(path), mode))
        if str(path) != internal.BINARY_PATH or mode != "rb":
            raise AssertionError("Unexpected file read during guarded module import")
        # Real hashlib is allowed to hash these owned bytes, never an executable.
        return io.BytesIO(b"offline-fake-executable-with-deliberately-wrong-hash")

    module = types.ModuleType("companion_auto_summon_runtime_under_test")
    module.__file__ = "<offline-concatenated-CompanionAutoSummon.py>"
    modules = {
        "pymhf": pymhf,
        "pymhf.core": core,
        "pymhf.core._internal": internal,
        "pymhf.core.hooking": hooking,
        "pymhf.gui": gui,
        "pymhf.gui.decorators": gui_decorators,
    }
    with patch.dict(sys.modules, modules), patch(
        "importlib.metadata.version", side_effect=fake_version
    ), patch.object(Path, "open", fake_open), patch("logging.Logger.error"):
        exec(compile(source, module.__file__, "exec"), module.__dict__)
    module._test_events = events
    module._test_declarations = declarations
    module._test_internal = internal
    # Routing tests do not call supported_runtime again: the mocked import guard
    # already disabled Mod, and callbacks run only against the owned test buffers.
    return module


class RuntimeGuardTests(unittest.TestCase):
    def test_not_injected_disables_before_fake_registration_without_file_reads(self):
        module = load_runtime()
        self.assertTrue(module.CompanionAutoSummon._disabled)
        self.assertEqual(module._test_events, [("class-created", True)])
        self.assertEqual(len(module._test_declarations), 11)

    def test_wrong_framework_disables_before_registration_and_skips_binary(self):
        module = load_runtime(injected=True, framework_version="0.2.3")
        self.assertTrue(module.CompanionAutoSummon._disabled)
        self.assertEqual(
            module._test_events,
            [("version", "pymhf"), ("class-created", True)],
        )

    def test_wrong_hash_disables_before_registration_using_only_bytesio(self):
        module = load_runtime(injected=True)
        self.assertTrue(module.CompanionAutoSummon._disabled)
        self.assertEqual(
            [event[0] for event in module._test_events],
            ["version", "open", "class-created"],
        )
        self.assertEqual(module._test_events[-1], ("class-created", True))

    def test_missing_framework_metadata_fails_closed(self):
        module = load_runtime(
            injected=True,
            version_error=importlib.metadata.PackageNotFoundError("pymhf"),
        )
        self.assertTrue(module.CompanionAutoSummon._disabled)
        self.assertEqual(module._test_events[-1], ("class-created", True))
        self.assertFalse(any(event[0] == "open" for event in module._test_events))


class RuntimeFixture(unittest.TestCase):
    def setUp(self):
        self.module = load_runtime()
        # All from_address reads are inside this test-owned allocation, or the
        # test-owned pointer object. No process discovery or process memory API.
        self.app_buffer = ctypes.create_string_buffer(0x900000)
        self.app_address = ctypes.addressof(self.app_buffer)
        first_global_rva = self.module.SUMMON_ARC_RANGE_RVA
        self.global_buffer = ctypes.create_string_buffer(
            self.module.APPLICATION_PTR_RVA - first_global_rva + ctypes.sizeof(ctypes.c_void_p))
        self.module._test_internal.BASE_ADDRESS = ctypes.addressof(self.global_buffer) - first_global_rva
        self.app_pointer = ctypes.c_void_p.from_buffer(
            self.global_buffer, self.module.APPLICATION_PTR_RVA - first_global_rva)
        self.app_pointer.value = self.app_address
        ctypes.c_float.from_buffer(self.global_buffer).value = 40.0
        self.player = self.app_address + self.module.LOCAL_PLAYER_OFFSET
        ctypes.c_uint64.from_address(self.player + self.module.PHYSICS_CONTEXT_OFFSET).value = 1
        self.owner = self.app_address + self.module.PET_TABLE_OFFSET
        self.foreign_player = self.player + 0x80
        self.clock = types.SimpleNamespace(now=0.0)
        self.module.time = types.SimpleNamespace(monotonic=lambda: self.clock.now)
        self.temp_directory = tempfile.TemporaryDirectory(prefix="companion-auto-summon-runtime-")
        self.addCleanup(self.temp_directory.cleanup)
        self.state_path = Path(self.temp_directory.name) / "CompanionAutoSummon-state.json"
        self.settings_path = Path(self.temp_directory.name) / "NMS-AutoPet" / "settings.json"
        with patch.dict(os.environ, {"LOCALAPPDATA": self.temp_directory.name}):
            self.mod = self.module.CompanionAutoSummon()
        self.mod.store = self.module.PetSelectionStore(self.state_path)
        self.common_buffer = ctypes.create_string_buffer(0xA000)
        self.common_address = ctypes.addressof(self.common_buffer)
        self.can_summon = Mock(return_value=True)
        self.ownership_eligible = Mock(return_value=True)
        self.use_hand = Mock(return_value=False)
        self.refresh_placement = Mock(return_value=None)
        self.queue_calls = []
        self.queue_reentrancy = []
        self.notice_calls = []

        def fake_queue(player, slot):
            self.queue_calls.append((player, slot))
            self.queue_reentrancy.append(self.mod.in_auto_call)
            self.set_pending(slot)
            # The real native wrapper invokes this after-hook synchronously.
            self.mod.remember_pet(player, slot)

        self.module.cas_can_summon = self.can_summon
        self.module.cas_owned_pet_eligible = self.ownership_eligible
        self.module.cas_use_summon_hand = self.use_hand
        self.module.cas_refresh_pet_placement = self.refresh_placement
        self.module.cas_queue_pet = fake_queue

        def fake_notice(*args):
            self.assertEqual(len(args), 11)
            self.notice_calls.append({
                "notifications": args[0],
                "message": ctypes.string_at(args[1]).decode("ascii"),
                "duration": args[2],
                "colour_address": args[3],
                "colour": tuple((ctypes.c_float * 4).from_address(args[3])),
                "audio": args[4],
                "icon": ctypes.c_int32.from_address(args[5]).value,
                "tail": args[6:],
            })

        self.module.cas_add_timed_message = Mock(side_effect=fake_notice)
        self.set_location(3)
        self.set_active(-1)
        self.set_pending(-1)
        self.set_preview(-1)
        self.set_notice_state(count=0, block=-1)

    def set_preview(self, slot=-1, emote=0):
        ctypes.c_int32.from_address(self.owner + self.module.PET_PREVIEW_OFFSET).value = slot
        ctypes.c_ubyte.from_address(self.owner + self.module.PET_EMOTE_OFFSET).value = emote

    def set_arc_range(self, value):
        ctypes.c_float.from_buffer(self.global_buffer).value = value

    def set_notice_state(self, *, count, block):
        ctypes.c_uint32.from_address(
            self.app_address + self.module.NOTIFICATIONS_OFFSET + self.module.NOTICE_COUNT_OFFSET
        ).value = count
        ctypes.c_float.from_address(
            self.app_address + self.module.NOTICE_BLOCK_OFFSET
        ).value = block

    def set_location(self, value):
        ctypes.c_int32.from_address(
            self.app_address + self.module.LOCATION_OFFSET
        ).value = value

    def set_active(self, value):
        ctypes.c_int32.from_address(
            self.app_address + self.module.ACTIVE_PET_OFFSET
        ).value = value

    def set_pending(self, value):
        ctypes.c_int32.from_address(
            self.player + self.module.PENDING_PET_OFFSET
        ).value = value

    def select(self, slot=5):
        self.set_pending(slot)
        self.mod.remember_pet(self.player, slot)
        self.set_pending(-1)

    def exit(self, now=0.0, player=None):
        self.clock.now = now
        self.mod.after_exit_request(0, self.player if player is None else player, True, False)

    def update(self, now, *, dt=1 / 60, player=None):
        self.clock.now = now
        observed_player = self.player if player is None else player
        self.mod.after_player_update(observed_player, dt)
        self.mod.after_pet_owner_update(self.owner + observed_player - self.player, dt)

    def probe(self, now, *, dt=1 / 60, player=None):
        """Two consecutive owner callbacks, including fresh ray warmup."""
        self.update(now, dt=dt, player=player)
        self.update(now + 0.001, dt=dt, player=player)

    def restart(self):
        """Discard instance caches; only the test-owned JSON survives."""
        with patch.dict(os.environ, {"LOCALAPPDATA": self.temp_directory.name}):
            self.mod = self.module.CompanionAutoSummon()
        self.mod.store = self.module.PetSelectionStore(self.state_path)
        self.clock.now = 0.0
        self.set_active(-1)
        self.set_pending(-1)
        self.queue_calls.clear()
        self.queue_reentrancy.clear()
        self.notice_calls.clear()
        self.module.cas_add_timed_message.reset_mock()
        self.can_summon.reset_mock(return_value=True, side_effect=True)
        self.can_summon.return_value = True
        self.ownership_eligible.reset_mock(return_value=True, side_effect=True)
        self.ownership_eligible.return_value = True
        self.use_hand.reset_mock(return_value=True, side_effect=True)
        self.use_hand.return_value = False
        self.refresh_placement.reset_mock(side_effect=True)
        self.set_preview(-1)

    def load_save(self, uid, *, success=True, network=False):
        # Contract: the deserialized common-data object carries its UID here.
        ctypes.c_uint64.from_address(
            self.common_address + self.module.SAVE_UNIVERSAL_ID_OFFSET
        ).value = uid
        args = (0, self.common_address, 0, network, False, 0)
        self.mod.before_load(*args)
        self.mod.after_load(*args, _result_=success)

    @staticmethod
    def seed(number, birth_time=1):
        return number.to_bytes(8, "little") + birth_time.to_bytes(8, "little")

    def set_pet(self, slot, seed, *, occupied=True):
        self.assertEqual(len(seed), 16)
        entry = self.app_address + self.module.PET_TABLE_OFFSET + slot * self.module.PET_ENTRY_SIZE
        ctypes.c_uint32.from_address(
            entry + self.module.PET_RESOURCE_OFFSET
        ).value = 1 if occupied else 0
        ctypes.memmove(entry + self.module.PET_SEED_OFFSET, seed[:8], 8)
        ctypes.memmove(entry + self.module.PET_BIRTH_TIME_OFFSET, seed[8:], 8)


class RuntimeRoutingTests(RuntimeFixture):
    def test_local_successful_manual_choice_is_remembered(self):
        for slot in (0, 29):
            with self.subTest(slot=slot):
                self.select(slot)
                self.assertEqual(self.mod.policy.last_slot, slot)
        self.assertEqual(self.mod.app_identity, self.app_address)

    def test_failed_manual_native_preparation_is_not_remembered(self):
        self.set_pending(-1)
        self.mod.remember_pet(self.player, 5)
        self.assertIsNone(self.mod.policy.last_slot)

    def test_foreign_manual_selection_and_exit_are_ignored(self):
        self.select(5)
        self.set_pending(7)
        self.mod.remember_pet(self.foreign_player, 7)
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.exit(player=self.foreign_player)
        self.assertFalse(self.mod.policy.pending)
        self.assertTrue(self.mod.enabled)

    def test_invalid_manual_slot_does_not_replace_selection(self):
        self.select(5)
        for slot in (-1, 30):
            self.set_pending(slot)
            self.mod.remember_pet(self.player, slot)
            self.assertEqual(self.mod.policy.last_slot, 5)

    def test_delayed_queue_is_once_and_its_hook_is_not_manual_selection(self):
        self.select(5)
        self.exit()
        remembered = Mock(wraps=self.mod.policy.remember)
        self.mod.policy.remember = remembered
        self.update(0)
        self.update(1.49)
        self.assertEqual(self.queue_calls, [])
        self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.assertEqual(self.queue_reentrancy, [True])
        remembered.assert_not_called()
        self.assertFalse(self.mod.in_auto_call)
        self.assertFalse(self.mod.policy.pending)
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.set_pending(-1)
        self.update(3)
        self.update(20)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_idle_frames_do_not_call_native_eligibility(self):
        self.select()
        self.update(0)
        self.update(2)
        self.can_summon.assert_not_called()

    def test_foreign_update_cannot_run_local_pending_request(self):
        self.select()
        self.exit()
        self.update(0, player=self.foreign_player)
        self.update(2, player=self.foreign_player)
        self.assertTrue(self.mod.policy.pending)
        self.can_summon.assert_not_called()
        self.assertEqual(self.queue_calls, [])
        self.update(3)
        self.probe(4.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_forbidden_location_never_calls_eligibility_or_queues(self):
        self.select()
        self.exit()
        self.set_location(4)
        for now in (0, 2, 11, 12, 15):
            self.update(now)
        self.assertTrue(self.mod.policy.pending)
        self.can_summon.assert_not_called()
        self.assertEqual(self.queue_calls, [])

    def test_pause_interrupts_continuous_on_foot_stability(self):
        self.select()
        self.exit()
        self.update(0)
        self.update(1, dt=0)
        self.update(2)
        self.update(3.49)
        self.assertEqual(self.queue_calls, [])
        self.probe(3.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_enter_ship_cancels_pending_but_keeps_manual_choice(self):
        self.select()
        self.exit()
        self.update(0)
        self.mod.before_enter_ship(self.player)
        self.update(2)
        self.assertEqual(self.queue_calls, [])
        self.assertFalse(self.mod.policy.pending)
        self.assertEqual(self.mod.policy.last_slot, 5)

    def test_manual_replacement_while_waiting_cancels_automatic_request(self):
        self.select()
        self.exit()
        self.update(0)
        self.select(9)
        self.update(2)
        self.assertEqual(self.queue_calls, [])
        self.assertEqual(self.mod.policy.last_slot, 9)
        self.assertFalse(self.mod.policy.pending)

    def test_changed_pet_seed_forgets_slot_instead_of_summoning_replacement(self):
        self.select(5)
        self.exit()
        self.assertEqual(self.mod.pet_identity, b"\x00" * 16)
        seed_address = (
            self.app_address
            + self.module.PET_TABLE_OFFSET
            + 5 * self.module.PET_ENTRY_SIZE
            + self.module.PET_SEED_OFFSET
        )
        ctypes.c_ubyte.from_address(seed_address).value = 1
        self.update(0)
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertIsNone(self.mod.pet_identity)
        self.assertFalse(self.mod.policy.pending)
        self.can_summon.assert_not_called()
        self.update(2)
        self.assertEqual(self.queue_calls, [])

    def test_main_load_resets_choice_and_identity(self):
        self.select()
        self.exit()
        self.mod.before_load(0, 0, 0, False, False, 0)
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertFalse(self.mod.policy.pending)
        self.assertIsNone(self.mod.app_identity)
        self.update(2)
        self.assertEqual(self.queue_calls, [])

    def test_network_client_load_preserves_local_selection_and_pending(self):
        self.select()
        self.exit()
        self.update(0)
        self.mod.before_load(0, 0, 0, True, True, 0)
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.assertTrue(self.mod.policy.pending)
        self.assertEqual(self.mod.app_identity, self.app_address)
        self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_native_ineligibility_retains_intent_until_first_suitable_place(self):
        self.can_summon.return_value = False
        self.select(); self.exit()
        for now in (0, 2, 12, 300):
            self.probe(now)
        self.assertEqual(self.queue_calls, [])
        self.assertTrue(self.mod.policy.pending)
        self.assertIn('Waiting for a suitable place', self.mod.control_status)
        self.can_summon.return_value = True
        self.probe(301)
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.assertFalse(self.mod.policy.pending)

    def test_active_or_pending_pet_cancels_request(self):
        for field in ("active", "pending"):
            with self.subTest(field=field):
                self.select()
                self.exit()
                if field == "active":
                    self.set_active(4)
                else:
                    self.set_pending(4)
                self.can_summon.reset_mock()
                self.update(0)
                self.assertFalse(self.mod.policy.pending)
                self.can_summon.assert_not_called()
                self.set_active(-1)
                self.set_pending(-1)
                self.update(2)
                self.assertEqual(self.queue_calls, [])
                self.mod.policy.reset()

    def test_unexpected_pet_index_cancels_without_native_calls(self):
        self.select()
        self.exit()
        self.set_active(30)
        self.update(0)
        self.assertFalse(self.mod.policy.pending)
        self.assertTrue(self.mod.enabled)
        self.can_summon.assert_not_called()
        self.assertEqual(self.queue_calls, [])

    def test_null_application_pointer_resets_without_native_calls(self):
        self.select()
        self.exit()
        self.app_pointer.value = None
        self.update(0)
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertIsNone(self.mod.app_identity)
        self.assertFalse(self.mod.policy.pending)
        self.can_summon.assert_not_called()

    def test_native_adapter_error_disables_and_forgets_state(self):
        self.select()
        self.exit()
        self.can_summon.side_effect = RuntimeError("fake native adapter failure")
        with self.assertLogs("CompanionAutoSummon", level="ERROR"):
            self.probe(0)
        self.assertFalse(self.mod.enabled)
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertFalse(self.mod.policy.pending)
        self.assertEqual(self.queue_calls, [])

    def test_native_eligibility_none_disables_instead_of_treating_as_false(self):
        self.select()
        self.exit()
        self.can_summon.return_value = None
        with self.assertLogs("CompanionAutoSummon", level="ERROR"):
            self.probe(0)
        self.assertFalse(self.mod.enabled)
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertFalse(self.mod.policy.pending)
        self.assertEqual(self.queue_calls, [])
        calls_before = self.can_summon.call_count
        self.update(2)
        self.assertEqual(self.can_summon.call_count, calls_before)

    def test_queue_rejection_retains_choice_and_retries_only_after_fresh_pair(self):
        self.select(); self.exit()
        rejected = Mock(return_value=None)
        self.module.cas_queue_pet = rejected
        self.update(0); self.probe(1.5)
        rejected.assert_called_once_with(self.player, 5)
        self.assertTrue(self.mod.policy.pending)
        self.assertEqual(self.mod.policy.pending_slot, 5)
        self.probe(1.6)
        rejected.assert_called_once_with(self.player, 5)
        self.probe(2.1)
        self.assertEqual(rejected.call_count, 2)
        self.assertTrue(self.mod.enabled)
        self.assertEqual(self.mod.policy.last_slot, 5)

    def test_unexpected_queue_index_still_disables_automation(self):
        self.select()
        self.exit()
        self.module.cas_queue_pet = lambda player, slot: self.set_pending(-2)
        self.update(0)
        with self.assertLogs("CompanionAutoSummon", level="ERROR"):
            self.probe(1.5)
        self.assertFalse(self.mod.enabled)
        self.assertFalse(self.mod.policy.pending)
        self.assertIsNone(self.mod.policy.last_slot)


class RuntimeLocationTests(RuntimeFixture):
    def test_all_native_supported_locations_queue_after_same_stability_and_warmup(self):
        for location in (2, 3, 14):
            with self.subTest(location=location):
                self.mod.policy.reset()
                self.queue_calls.clear()
                self.refresh_placement.reset_mock()
                self.select()
                self.set_location(location)
                self.exit()
                self.update(0)
                self.update(1.49)
                self.assertEqual(self.queue_calls, [])
                self.assertTrue(self.mod._placement_warmed)
                self.probe(1.5)
                self.assertEqual(self.queue_calls, [(self.player, 5)])
                self.assertFalse(self.mod.policy.pending)
                self.assertEqual(self.refresh_placement.call_count, 3)

    def test_native_rejection_still_blocks_newly_allowed_interior_locations(self):
        self.can_summon.return_value = False
        for location in (2, 14):
            with self.subTest(location=location):
                self.mod.policy.reset()
                self.can_summon.reset_mock()
                self.refresh_placement.reset_mock()
                self.select()
                self.set_location(location)
                self.exit()
                for now in (0, 1.5, 11.9, 12):
                    self.update(now)
                self.assertEqual(self.queue_calls, [])
                self.assertTrue(self.mod.policy.pending)
                self.assertEqual(self.mod.policy.last_slot, 5)
                self.assertEqual(self.can_summon.call_count, 1)
                self.assertEqual(self.refresh_placement.call_count, 4)

    def test_return_from_forbidden_freighter_locations_starts_fresh_stability(self):
        for location in (9, 10):
            with self.subTest(location=location):
                self.mod.policy.reset()
                self.queue_calls.clear()
                self.refresh_placement.reset_mock()
                self.ownership_eligible.reset_mock()
                self.select()
                self.set_location(location)
                self.exit()
                self.update(0)
                self.update(2)
                self.refresh_placement.assert_not_called()
                self.ownership_eligible.assert_not_called()
                self.set_location(2)
                self.update(3)
                self.update(4.49)
                self.assertEqual(self.queue_calls, [])
                self.probe(4.5)
                self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_forbidden_location_retains_intent_until_later_allowed_location(self):
        for location in (9, 10):
            with self.subTest(location=location):
                self.mod.policy.reset(); self.queue_calls.clear(); self.refresh_placement.reset_mock()
                self.select(); self.set_location(location); self.exit()
                self.update(0); self.update(300)
                self.assertTrue(self.mod.policy.pending)
                self.refresh_placement.assert_not_called()
                self.set_location(14); self.probe(301)
                self.assertEqual(self.queue_calls, [])
                self.probe(302.5)
                self.assertEqual(self.queue_calls, [(self.player, 5)])


class RuntimePlacementTests(RuntimeFixture):
    def test_player_update_handles_controls_but_never_prepares_or_queues_a_pet(self):
        self.select()
        self.exit()
        for now in (0, 2):
            self.clock.now = now
            self.mod.after_player_update(self.player, 1 / 60)
        self.ownership_eligible.assert_not_called()
        self.refresh_placement.assert_not_called()
        self.can_summon.assert_not_called()
        self.assertEqual(self.queue_calls, [])
        self.assertTrue(self.mod.policy.pending)

    def test_foreign_owner_update_does_not_touch_local_placement(self):
        self.select()
        self.exit()
        self.mod.after_pet_owner_update(self.owner + 0x80, 1 / 60)
        self.ownership_eligible.assert_not_called()
        self.refresh_placement.assert_not_called()
        self.can_summon.assert_not_called()
        self.assertTrue(self.mod.policy.pending)

    def test_first_refresh_warms_jobs_then_next_owner_callback_can_queue_once(self):
        self.mod.policy = self.module.CompanionAutoSummonPolicy(delay_seconds=0)
        self.select()
        self.exit()
        calls = Mock()
        calls.attach_mock(self.ownership_eligible, "ownership")
        calls.attach_mock(self.use_hand, "hand")
        calls.attach_mock(self.refresh_placement, "refresh")
        calls.attach_mock(self.can_summon, "can_summon")
        self.update(0)
        self.assertEqual([call[0] for call in calls.mock_calls],
                         ["ownership", "hand", "refresh"])
        self.refresh_placement.assert_called_once_with(
            self.owner + self.module.PET_ARC_OFFSET, 40.0, 40.0, 0)
        self.ownership_eligible.assert_called_once_with(self.owner, 5)
        self.assertEqual(self.queue_calls, [])
        self.assertTrue(self.mod._placement_warmed)
        self.update(0.01)
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.assertFalse(self.mod._placement_warmed)
        self.update(0.02)
        self.assertEqual(self.refresh_placement.call_count, 2)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_native_ownership_gate_prevents_refresh_and_player_eligibility(self):
        self.ownership_eligible.return_value = False
        self.select()
        self.exit()
        with self.assertLogs(self.module.LOGGER, level="INFO") as logs:
            for now in (0, 2, 12):
                self.update(now)
        self.assertTrue(any("ownership_eligibility_false" in line for line in logs.output))
        self.use_hand.assert_not_called()
        self.refresh_placement.assert_not_called()
        self.can_summon.assert_not_called()
        self.assertEqual(self.ownership_eligible.call_count, 3)
        self.assertTrue(self.mod.policy.pending)
        self.assertEqual(self.mod.policy.last_slot, 5)

    def test_failed_native_ownership_gate_disables_before_refresh(self):
        self.ownership_eligible.return_value = None
        self.select()
        self.exit()
        with self.assertLogs(self.module.LOGGER, level="ERROR"):
            self.update(0)
        self.assertFalse(self.mod.enabled)
        self.refresh_placement.assert_not_called()
        self.can_summon.assert_not_called()

    def test_native_preview_or_emote_cancels_and_retains_selected_companion(self):
        for preview, emote in ((0, 0), (29, 0), (-2, 0), (-1, 1)):
            with self.subTest(preview=preview, emote=emote):
                self.mod.policy.reset()
                self.select()
                self.exit()
                self.set_preview(preview, emote)
                self.update(0)
                self.assertFalse(self.mod.policy.pending)
                self.assertEqual(self.mod.policy.last_slot, 5)
                self.assertFalse(self.mod._placement_warmed)
        self.ownership_eligible.assert_not_called()
        self.refresh_placement.assert_not_called()
        self.can_summon.assert_not_called()

    def test_opening_native_preview_after_warmup_stops_further_refresh(self):
        self.select()
        self.exit()
        self.update(0)
        self.set_preview(5)
        self.probe(1.5)
        self.assertEqual(self.refresh_placement.call_count, 1)
        self.assertEqual(self.queue_calls, [])
        self.assertFalse(self.mod.policy.pending)
        self.assertFalse(self.mod._placement_warmed)

    def test_pause_or_leaving_supported_locations_invalidates_warmup_before_resuming(self):
        for paused in (True, False):
            with self.subTest(paused=paused):
                self.mod.policy = self.module.CompanionAutoSummonPolicy(delay_seconds=0)
                self.set_location(3)
                self.select()
                self.exit()
                self.update(0)
                self.assertTrue(self.mod._placement_warmed)
                if paused:
                    self.update(0.1, dt=0)
                else:
                    self.set_location(4)
                    self.update(0.1)
                    self.set_location(3)
                self.assertFalse(self.mod._placement_warmed)
                previous_calls = len(self.queue_calls)
                self.update(0.2)
                self.assertEqual(len(self.queue_calls), previous_calls)
                self.update(0.3)
                self.assertEqual(len(self.queue_calls), previous_calls + 1)

    def test_pending_off_control_defers_owner_before_player_update_can_apply_it(self):
        self.select()
        self.exit()
        self.update(0)
        self.mod.automatic_summoning = False
        self.clock.now = 2
        self.mod.after_pet_owner_update(self.owner, 1 / 60)
        self.assertEqual(self.refresh_placement.call_count, 1)
        self.assertEqual(self.queue_calls, [])
        self.assertFalse(self.mod._placement_warmed)
        self.mod.after_player_update(self.player, 1 / 60)
        self.assertFalse(self.mod.auto_enabled)
        self.assertFalse(self.mod.policy.pending)

    def test_native_configured_range_and_hand_are_forwarded_without_fixed_values(self):
        self.select()
        self.exit()
        self.set_arc_range(27.5)
        self.use_hand.return_value = True
        ctypes.c_uint32.from_address(self.app_address + self.module.SUMMON_HAND_OFFSET).value = 0xF0112233
        self.update(0)
        self.refresh_placement.assert_called_once_with(
            self.owner + self.module.PET_ARC_OFFSET, 27.5, 27.5, 0xF0112233)

    def test_invalid_native_range_disables_without_refresh(self):
        for value in (0, -1, float("nan"), float("inf")):
            with self.subTest(value=value):
                self.mod.enabled = True
                self.select()
                self.exit()
                self.set_arc_range(value)
                with self.assertLogs(self.module.LOGGER, level="ERROR"):
                    self.update(0)
                self.assertFalse(self.mod.enabled)
        self.use_hand.assert_not_called()
        self.refresh_placement.assert_not_called()
        self.can_summon.assert_not_called()

    def test_missing_native_hand_result_disables_without_refresh(self):
        self.select()
        self.exit()
        self.use_hand.return_value = None
        with self.assertLogs(self.module.LOGGER, level="ERROR"):
            self.update(0)
        self.assertFalse(self.mod.enabled)
        self.refresh_placement.assert_not_called()
        self.can_summon.assert_not_called()

    def test_refresh_exception_disables_without_player_eligibility_or_queue(self):
        self.select()
        self.exit()
        self.refresh_placement.side_effect = RuntimeError("offline native refresh failure")
        with self.assertLogs(self.module.LOGGER, level="ERROR"):
            self.update(0)
        self.assertFalse(self.mod.enabled)
        self.assertFalse(self.mod._placement_warmed)
        self.can_summon.assert_not_called()
        self.assertEqual(self.queue_calls, [])

    def test_late_first_callback_still_requires_fresh_placement_and_stability(self):
        self.select(); self.exit()
        self.update(300)
        self.assertTrue(self.mod.policy.pending)
        self.assertTrue(self.mod._placement_warmed)
        self.can_summon.assert_not_called()
        self.assertEqual(self.queue_calls, [])
        self.probe(301.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_nonfinite_frame_time_never_starts_native_placement_or_hud(self):
        self.select()
        self.exit()
        for dt in (float("nan"), float("inf"), -float("inf")):
            self.update(0, dt=dt)
        self.ownership_eligible.assert_not_called()
        self.use_hand.assert_not_called()
        self.refresh_placement.assert_not_called()
        self.can_summon.assert_not_called()
        self.module.cas_add_timed_message.assert_not_called()
        self.assertTrue(self.mod.policy.pending)
        self.assertFalse(self.mod._placement_warmed)

    def test_application_replacement_resets_before_reading_any_pet_identity(self):
        self.select()
        self.exit()
        self.update(0)
        other_app = ctypes.create_string_buffer(0x900000)
        self.app_pointer.value = ctypes.addressof(other_app)
        with patch.object(self.mod, "_pet_seed", side_effect=AssertionError("read after context reset")):
            self.mod.after_pet_owner_update(ctypes.addressof(other_app) + self.module.PET_TABLE_OFFSET, 1 / 60)
        self.assertTrue(self.mod.enabled)
        self.assertFalse(self.mod.policy.pending)
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertFalse(self.mod._placement_warmed)
        self.assertEqual(self.refresh_placement.call_count, 1)
        self.assertEqual(self.queue_calls, [])

    def test_load_and_next_exit_do_not_reuse_old_warmup(self):
        self.select()
        self.exit()
        self.update(0)
        self.assertTrue(self.mod._placement_warmed)
        self.load_save(123)
        self.assertFalse(self.mod._placement_warmed)
        self.mod.policy = self.module.CompanionAutoSummonPolicy(delay_seconds=0)
        self.select()
        self.exit(1)
        self.update(1)
        self.assertEqual(self.queue_calls, [])
        self.update(1.01)
        self.assertEqual(self.queue_calls, [(self.player, 5)])


class RuntimeDiagnosticTests(RuntimeFixture):
    def test_exit_without_selection_explains_why_it_did_not_arm(self):
        with self.assertLogs(self.module.LOGGER, level="INFO") as logs:
            self.exit()
        self.assertTrue(any("not armed: no selected owned companion" in line for line in logs.output))
        self.assertFalse(self.mod.policy.pending)
        self.can_summon.assert_not_called()

    def test_wait_logs_and_native_probes_remain_bounded_across_many_frames(self):
        self.select(); self.can_summon.return_value = False
        with self.assertLogs(self.module.LOGGER, level='INFO') as logs:
            self.exit()
            for frame in range(1000): self.update(frame / 100)
        self.assertEqual(sum('ship exit armed' in line for line in logs.output), 1)
        self.assertLessEqual(sum('exit waiting:' in line for line in logs.output), self.module.DIAGNOSTIC_WAIT_LIMIT)
        self.assertLessEqual(self.can_summon.call_count, 20)
        self.assertLessEqual(self.refresh_placement.call_count, 40)
        self.assertEqual(self.queue_calls, [])
        self.assertTrue(self.mod.policy.pending)

    def test_wait_state_changes_are_visible_and_stability_is_preserved(self):
        self.select()
        with self.assertLogs(self.module.LOGGER, level='INFO') as logs:
            self.exit(); self.set_location(4); self.update(0)
            self.set_location(3); self.update(0.5, dt=0)
            self.can_summon.return_value = False; self.probe(1)
            self.can_summon.return_value = True; self.probe(2)
            self.assertEqual(self.queue_calls, [])
            self.probe(2.6)
        for reason in ('not_summon_location','paused_or_zero_dt','placement_warmup','eligibility_false'):
            self.assertTrue(any(reason in line for line in logs.output), reason)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_flapping_waits_are_bounded_but_explicit_cancellation_is_reported(self):
        self.select(); self.can_summon.return_value = False
        with self.assertLogs(self.module.LOGGER, level='INFO') as logs:
            self.exit()
            for frame in range(50):
                self.set_location(3 if frame % 2 else 4); self.update(frame / 10)
            self.update(300)
            self.assertTrue(self.mod.policy.pending)
            self.mod.before_enter_ship(self.player)
        self.assertEqual(sum('exit waiting:' in line for line in logs.output), self.module.DIAGNOSTIC_WAIT_LIMIT)
        self.assertEqual(sum('wait log limit reached' in line for line in logs.output), 1)
        self.assertTrue(any('cancelled by entering the ship' in line for line in logs.output))
        self.assertFalse(self.mod.policy.pending)

    def test_indefinite_wait_distinguishes_native_rejection_location_and_pause(self):
        for reason, location, dt in (('eligibility_false',3,1/60),('not_summon_location',4,1/60),('paused_or_zero_dt',3,0)):
            with self.subTest(reason=reason):
                self.mod.policy.reset(); self.select(); self.set_location(location)
                self.can_summon.return_value = False
                with self.assertLogs(self.module.LOGGER, level='INFO') as logs:
                    self.exit(); self.probe(0,dt=dt); self.probe(300,dt=dt)
                self.assertTrue(any(reason in line for line in logs.output))
                self.assertFalse(any('exit expired' in line for line in logs.output))
                self.assertTrue(self.mod.policy.pending)
                self.assertEqual(self.queue_calls, [])

    def test_existing_active_or_pending_pet_logs_cancellation_without_native_call(self):
        for setter, reason in ((self.set_active, "active_companion"),
                               (self.set_pending, "native_pending_companion")):
            with self.subTest(reason=reason):
                self.mod.policy.reset()
                self.select()
                self.set_active(-1)
                self.set_pending(-1)
                with self.assertLogs(self.module.LOGGER, level="INFO") as logs:
                    self.exit()
                    setter(4)
                    self.update(0)
                terminal = [line for line in logs.output if "cancelled by active or native-pending" in line]
                self.assertEqual(len(terminal), 1)
                self.assertIn(f"final_wait={reason}", terminal[0])
                self.assertFalse(self.mod.policy.pending)
                self.can_summon.assert_not_called()
                self.assertEqual(self.queue_calls, [])

    def test_reentry_and_manual_replacement_have_distinct_terminal_reasons(self):
        self.select()
        with self.assertLogs(self.module.LOGGER, level="INFO") as logs:
            self.exit()
            self.mod.before_enter_ship(self.player)
            self.exit()
            self.select(8)
        self.assertEqual(sum("cancelled by entering the ship" in line for line in logs.output), 1)
        self.assertEqual(sum("cancelled by successful manual companion selection" in line
                             for line in logs.output), 1)
        self.assertFalse(self.mod.policy.pending)
        self.assertIsNone(self.mod._exit_diagnostic)
        self.assertEqual(self.mod.policy.last_slot, 8)

    def test_backwards_clock_is_not_misreported_as_expiry(self):
        self.select()
        self.can_summon.return_value = False
        with self.assertLogs(self.module.LOGGER, level="INFO") as logs:
            self.exit(2)
            self.update(2)
            self.update(1)
        self.assertTrue(any("cancelled by backwards clock" in line for line in logs.output))
        self.assertFalse(any("exit expired" in line for line in logs.output))
        self.assertFalse(self.mod.policy.pending)
        self.assertEqual(self.queue_calls, [])


class RuntimePersistenceTests(RuntimeFixture):
    def test_renamed_mod_reads_legacy_preferences_and_favorite_without_rewriting(self):
        legacy_root = Path(self.temp_directory.name) / "NMS-AutoPet"
        legacy_root.mkdir(exist_ok=True)
        seed = self.seed(1234)
        favorite = {"seed": seed.hex(), "slot": 5}
        state_path = legacy_root / "state.json"
        settings_path = legacy_root / "settings.json"
        state_bytes = json.dumps({"schema": 1, "selections": {
            "nms:000000000000000a": favorite}}).encode("utf-8")
        settings_bytes = json.dumps({"schema": 3, "enabled": False,
            "locations": [2], "selection_mode": "random",
            "prefer_same_biome": False}).encode("utf-8")
        state_path.write_bytes(state_bytes)
        settings_path.write_bytes(settings_bytes)
        with patch.dict(os.environ, {"LOCALAPPDATA": self.temp_directory.name}):
            self.mod = self.module.CompanionAutoSummon()
        self.set_pet(5, seed)
        self.load_save(0xA)
        self.assertFalse(self.mod.auto_enabled)
        self.assertEqual(self.mod.allowed_locations, frozenset({2}))
        self.assertEqual(self.mod.selection_mode_value, "random")
        self.assertFalse(self.mod.prefer_same_biome_value)
        self.assertEqual(self.mod.saved_selection, favorite)
        self.assertEqual(self.mod.store.path, state_path)
        self.assertEqual(self.mod.settings_store.path, settings_path)
        self.assertEqual(state_path.read_bytes(), state_bytes)
        self.assertEqual(settings_path.read_bytes(), settings_bytes)
        self.assertEqual(self.queue_calls, [])
        self.assertFalse((legacy_root.parent / "NMS-CompanionAutoSummon").exists())

    def save_choice(self, *, uid=0xA, slot=5, seed=None):
        if seed is None:
            seed = self.seed(1234)
        self.set_pet(slot, seed)
        self.load_save(uid)
        self.select(slot)
        return seed

    def test_instance_initialization_reads_settings_only_without_other_io(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": self.temp_directory.name}), patch.object(
            self.module.CompanionAutoSummonSettingsStore, "load_preferences", return_value=self.module.CompanionAutoSummonSettingsStore.defaults()
        ) as settings_load, patch.object(
            Path, "open", side_effect=AssertionError("unexpected read")
        ), patch.object(
            Path, "mkdir", side_effect=AssertionError("unexpected write")
        ):
            fresh = self.module.CompanionAutoSummon()
        self.assertIsNone(fresh.save_key)
        self.assertIsNone(fresh.saved_selection)
        self.assertTrue(fresh.persistence_ok)
        self.assertFalse(self.state_path.exists())
        settings_load.assert_called_once_with()

    def test_default_store_path_uses_current_users_localappdata(self):
        user_data = Path(self.temp_directory.name) / "DifferentUserData"
        with patch.dict(os.environ, {"LOCALAPPDATA": str(user_data)}), patch.object(
            self.module.CompanionAutoSummonSettingsStore, "load_preferences", return_value=self.module.CompanionAutoSummonSettingsStore.defaults()
        ), patch.object(
            Path, "open", side_effect=AssertionError("unexpected read")
        ), patch.object(Path, "mkdir", side_effect=AssertionError("unexpected write")):
            fresh = self.module.CompanionAutoSummon()
        self.assertEqual(fresh.store.path, user_data / "NMS-AutoPet" / "state.json")
        self.assertFalse(user_data.exists())

    def test_store_path_rejects_missing_empty_and_relative_profile(self):
        for value in (None, "", "relative-profile-directory"):
            with self.subTest(value=value), patch.dict(os.environ):
                if value is None:
                    os.environ.pop("LOCALAPPDATA", None)
                else:
                    os.environ["LOCALAPPDATA"] = value
                with self.assertRaises(self.module.SelectionStoreError):
                    self.module.selection_store_path()

    def test_missing_profile_keeps_manual_session_functional(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": ""}), self.assertLogs(
            "CompanionAutoSummon", level="WARNING"
        ):
            self.mod = self.module.CompanionAutoSummon()
        self.assertIsNone(self.mod.store)
        self.assertFalse(self.mod.persistence_ok)
        self.assertTrue(self.mod.enabled)
        self.load_save(0xA)
        self.set_pet(5, self.seed(1234))
        self.select(5)
        self.assertFalse(self.mod.auto_enabled)
        self.mod.automatic_summoning = True
        self.update(0, dt=0)
        self.exit(1)
        self.update(1)
        self.probe(2.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.assertFalse(self.state_path.exists())

    def test_disk_write_requires_manual_choice_after_good_load(self):
        self.set_pet(5, self.seed(1234))
        self.select(5)
        self.assertFalse(self.state_path.exists())
        self.load_save(0xA)
        self.assertFalse(self.state_path.exists())
        self.exit()
        self.update(0)
        self.update(2)
        self.assertFalse(self.state_path.exists())
        self.select(5)
        document = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(document["selections"]["nms:000000000000000a"], {
            "seed": self.seed(1234).hex(), "slot": 5,
        })

    def test_restart_restores_same_pet_after_load_without_rewriting_file(self):
        self.save_choice()
        saved_bytes = self.state_path.read_bytes()
        self.restart()
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertIsNone(self.mod.saved_selection)
        self.load_save(0xA)
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertFalse(self.mod.policy.pending)
        self.assertEqual(self.queue_calls, [])
        self.refresh_placement.assert_not_called()
        self.update(0)
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.assertEqual(self.state_path.read_bytes(), saved_bytes)
        self.set_pending(-1)
        self.probe(20)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_two_save_identities_restore_their_own_choices(self):
        self.save_choice(uid=0xA, slot=3, seed=self.seed(100))
        self.save_choice(uid=0xB, slot=7, seed=self.seed(200))
        document = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(set(document["selections"]), {
            "nms:000000000000000a", "nms:000000000000000b",
        })
        for uid, expected_slot in ((0xA, 3), (0xB, 7)):
            with self.subTest(uid=uid):
                self.restart()
                self.load_save(uid)
                self.exit()
                self.update(0)
                self.probe(1.5)
                self.assertEqual(self.queue_calls, [(self.player, expected_slot)])

    def test_unknown_save_never_borrows_another_saves_choice(self):
        self.save_choice(uid=0xA)
        self.restart()
        self.load_save(0xB)
        self.exit()
        self.update(0)
        self.update(2)
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertEqual(self.queue_calls, [])

    def test_removed_or_replaced_pet_is_not_restored(self):
        original = self.save_choice()
        for occupied, current_seed in ((False, original), (True, self.seed(4321))):
            with self.subTest(occupied=occupied):
                self.restart()
                self.set_pet(5, current_seed, occupied=occupied)
                self.load_save(0xA)
                self.exit()
                self.update(0)
                self.update(2)
                self.assertIsNone(self.mod.policy.last_slot)
                self.assertEqual(self.queue_calls, [])

    def test_unique_seed_moving_to_another_slot_is_remapped(self):
        original = self.save_choice(slot=5)
        self.restart()
        self.set_pet(5, self.seed(4321))
        self.set_pet(12, original)
        self.load_save(0xA)
        self.exit()
        self.assertEqual(self.mod.policy.last_slot, 12)
        self.update(0)
        self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 12)])

    def test_duplicate_seed_is_ambiguous_even_at_original_slot(self):
        original = self.save_choice(slot=5)
        self.restart()
        self.set_pet(12, original)
        self.load_save(0xA)
        self.exit()
        self.update(0)
        self.update(2)
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertEqual(self.queue_calls, [])

    def test_bone_scale_seed_flags_and_padding_are_not_part_of_identity(self):
        entry = self.app_address + self.module.PET_TABLE_OFFSET + 5 * self.module.PET_ENTRY_SIZE
        # BoneScaleSeed and the valid flag/padding belong to other fields.
        ctypes.memmove(entry + 0x2390, b"a" * 16, 16)
        ctypes.memmove(entry + self.module.PET_SEED_OFFSET + 8, b"b" * 8, 8)
        identity = self.seed(1234, 987654321)
        self.save_choice(seed=identity)
        document = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(
            document["selections"]["nms:000000000000000a"]["seed"],
            identity.hex(),
        )
        self.restart()
        ctypes.memmove(entry + 0x2390, b"c" * 16, 16)
        ctypes.memmove(entry + self.module.PET_SEED_OFFSET + 8, b"d" * 8, 8)
        self.load_save(0xA)
        self.exit()
        self.update(0)
        self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_birth_time_change_prevents_restoring_same_creature_seed(self):
        self.save_choice(seed=self.seed(1234, 100))
        self.restart()
        self.set_pet(5, self.seed(1234, 200))
        self.load_save(0xA)
        self.exit()
        self.update(0)
        self.update(2)
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertEqual(self.queue_calls, [])

    def test_corrupted_json_is_preserved_and_manual_session_mode_still_works(self):
        corrupt = b"{invalid-json-do-not-overwrite"
        self.state_path.write_bytes(corrupt)
        self.set_pet(5, self.seed(1234))
        with self.assertLogs("CompanionAutoSummon", level="WARNING"):
            self.load_save(0xA)
        self.assertFalse(self.mod.persistence_ok)
        self.assertTrue(self.mod.enabled)
        self.select(5)
        self.exit()
        self.update(0)
        self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.assertEqual(self.state_path.read_bytes(), corrupt)

    def test_failed_native_load_does_not_reuse_prior_key_or_write(self):
        self.save_choice(uid=0xA)
        original_bytes = self.state_path.read_bytes()
        self.load_save(0xB, success=False)
        self.assertIsNone(self.mod.save_key)
        self.assertIsNone(self.mod.saved_selection)
        self.assertIsNone(self.mod.policy.last_slot)
        self.select(5)
        self.assertEqual(self.state_path.read_bytes(), original_bytes)

    def test_zero_uid_stays_session_only_without_guessing_identity(self):
        with self.assertLogs("CompanionAutoSummon", level="WARNING"):
            self.load_save(0)
        self.assertIsNone(self.mod.save_key)
        self.select(5)
        self.assertFalse(self.state_path.exists())
        self.exit()
        self.update(0)
        self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_network_load_keeps_local_persistent_key_and_selection(self):
        self.save_choice(uid=0xA)
        local_selection = dict(self.mod.saved_selection)
        self.load_save(0xB, network=True)
        self.assertEqual(self.mod.save_key, "nms:000000000000000a")
        self.assertEqual(self.mod.saved_selection, local_selection)

    def test_null_application_clears_persistent_context(self):
        self.save_choice()
        self.exit()
        self.app_pointer.value = None
        self.update(0)
        self.assertIsNone(self.mod.save_key)
        self.assertIsNone(self.mod.saved_selection)
        self.assertIsNone(self.mod.policy.last_slot)

    def test_replacement_application_without_load_does_not_inherit_save_choice(self):
        self.save_choice()
        self.assertIsNotNone(self.mod.pending_notice)
        replacement = ctypes.create_string_buffer(0x900000)
        ctypes.memmove(ctypes.addressof(replacement), self.app_address, 0x900000)
        self.app_buffer = replacement
        self.app_address = ctypes.addressof(replacement)
        self.app_pointer.value = self.app_address
        self.player = self.app_address + self.module.LOCAL_PLAYER_OFFSET
        self.exit()
        self.assertIsNone(self.mod.save_key)
        self.assertIsNone(self.mod.saved_selection)
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertFalse(self.mod.policy.pending)
        self.assertIsNone(self.mod.pending_notice)
        self.update(0)
        self.assertEqual(self.notice_calls, [])


class RuntimeStartupSummonTests(RuntimeFixture):
    """A successful local load grants one deferred request, never a respawn loop."""

    def prepare(self, *, location=3, uid=0xA, slot=5, occupied=True, random_mode=False):
        identity = self.seed(1234)
        self.set_pet(slot, identity, occupied=occupied)
        self.mod.store.remember(f"nms:{uid:016x}", identity, slot)
        self.set_location(location)
        if random_mode:
            self.mod.selection_mode_value = "random"
        self.load_save(uid)
        return identity

    def assert_no_native_summon_work(self):
        self.refresh_placement.assert_not_called()
        self.can_summon.assert_not_called()
        self.ownership_eligible.assert_not_called()
        self.assertEqual(self.queue_calls, [])

    def test_local_load_in_each_supported_location_is_deferred_then_one_shot(self):
        for location in (2, 3, 14):
            with self.subTest(location=location):
                self.setUp()
                self.prepare(location=location)
                saved = self.state_path.read_bytes()
                self.assertTrue(self.mod._load_summon_pending)
                self.assertFalse(self.mod.policy.pending)
                self.assert_no_native_summon_work()
                self.update(0)
                self.assertFalse(self.mod._load_summon_pending)
                self.assertTrue(self.mod.policy.pending)
                self.assertEqual(self.queue_calls, [])
                self.probe(1.5)
                self.assertEqual(self.queue_calls, [(self.player, 5)])
                self.assertEqual(self.queue_reentrancy, [True])
                self.set_pending(-1)
                self.set_active(5)
                self.update(2)  # Observe activation before simulating dismissal.
                self.set_active(-1)  # A later dismissal must not replay startup.
                self.probe(100)
                self.assertEqual(self.queue_calls, [(self.player, 5)])
                self.assertEqual(self.state_path.read_bytes(), saved)

    def test_loading_and_nonadvancing_frames_cannot_accrue_startup_stability(self):
        self.prepare(location=4)
        self.probe(0)
        self.probe(200)
        self.set_location(14)
        for dt in (0, -0.1, float("nan"), float("inf")):
            self.probe(300, dt=dt)
        self.assertTrue(self.mod._load_summon_pending)
        self.assert_no_native_summon_work()
        self.probe(500)
        self.assertEqual(self.queue_calls, [])
        self.probe(501.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_startup_still_requires_fresh_nonzero_physics_and_native_placement(self):
        self.prepare(location=14)
        physics = self.player + self.module.PHYSICS_CONTEXT_OFFSET
        ctypes.c_uint64.from_address(physics).value = 0
        self.probe(0)
        self.probe(2)
        self.assert_no_native_summon_work()
        ctypes.c_uint64.from_address(physics).value = 7
        self.can_summon.return_value = False
        self.update(3)
        self.can_summon.assert_not_called()  # This frame only primes native placement.
        self.update(3.01)
        self.assertEqual(self.queue_calls, [])
        self.can_summon.return_value = True
        self.probe(5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_existing_active_pending_preview_or_emote_consumes_load_even_while_paused(self):
        for obstruction in ("active", "pending", "preview", "emote", "invalid_active", "invalid_pending"):
            with self.subTest(obstruction=obstruction):
                self.setUp()
                self.prepare(location=4)
                if obstruction == "active":
                    self.set_active(7)
                elif obstruction == "pending":
                    self.set_pending(7)
                elif obstruction == "preview":
                    self.set_preview(7)
                elif obstruction == "emote":
                    self.set_preview(-1, 1)
                elif obstruction == "invalid_active":
                    self.set_active(30)
                else:
                    self.set_pending(-2)
                self.update(0, dt=0)
                self.assertFalse(self.mod._load_summon_pending)
                self.set_active(-1)
                self.set_pending(-1)
                self.set_preview(-1)
                self.set_location(14)
                self.probe(5)
                self.probe(10)
                self.assert_no_native_summon_work()

    def test_manual_accepted_choice_cancels_startup_but_failed_choice_does_not(self):
        for accepted in (False, True):
            with self.subTest(accepted=accepted):
                self.setUp()
                self.prepare()
                self.set_pet(7, self.seed(777))
                self.set_pending(7 if accepted else -1)
                self.mod.remember_pet(self.player, 7)
                self.set_pending(-1)
                self.assertEqual(self.mod._load_summon_pending, not accepted)
                self.update(0)
                self.probe(1.5)
                self.assertEqual(self.queue_calls, [] if accepted else [(self.player, 5)])
                if accepted:
                    self.assertEqual(self.mod.policy.last_slot, 7)

    def test_ship_entry_cancels_startup_and_later_exit_creates_only_its_own_request(self):
        self.prepare()
        self.mod.before_enter_ship(self.player)
        self.assertFalse(self.mod._load_summon_pending)
        self.probe(0)
        self.probe(5)
        self.assert_no_native_summon_work()
        self.exit(10)
        self.update(10)
        self.probe(11.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_real_exit_replaces_unconsumed_load_without_second_automatic_queue(self):
        self.prepare()
        self.exit(0)
        self.assertFalse(self.mod._load_summon_pending)
        self.update(0)
        self.probe(1.5)
        self.set_pending(-1)
        self.probe(10)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_off_or_disabled_location_consumes_load_without_replaying_after_enable(self):
        for restriction in ("off", "location"):
            with self.subTest(restriction=restriction):
                self.setUp()
                if restriction == "off":
                    self.mod.auto_enabled = False
                else:
                    self.mod.allowed_locations = frozenset({3})
                self.prepare(location=14)
                self.probe(0)
                self.assertFalse(self.mod._load_summon_pending)
                if restriction == "off":
                    self.mod.automatic_summoning = True
                else:
                    self.mod.nexus = True
                self.update(2)
                self.probe(5)
                self.assert_no_native_summon_work()

    def test_pending_preference_edits_prevent_owner_work_and_applied_edits_cancel_load(self):
        for preference, value in (("automatic_summoning", False), ("nexus", False),
                                  ("prefer_same_biome", False),
                                  ("companion_selection", "random")):
            with self.subTest(preference=preference):
                self.setUp()
                self.prepare(location=14)
                if preference == "companion_selection":
                    value = self.module.SelectionMode(value)
                setattr(self.mod, preference, value)
                self.mod.after_pet_owner_update(self.owner, 1 / 60)
                self.assert_no_native_summon_work()
                self.update(0)
                self.assertFalse(self.mod._load_summon_pending)
                self.probe(5)
                self.assert_no_native_summon_work()

    def test_failed_or_null_common_load_never_arms_and_network_load_preserves_local_intent(self):
        self.prepare()
        original = dict(self.mod.saved_selection)
        self.load_save(0xB, network=True)
        self.assertTrue(self.mod._load_summon_pending)
        self.assertEqual(self.mod.saved_selection, original)
        self.assertEqual(self.mod.save_key, "nms:000000000000000a")
        self.load_save(0xB, success=False)
        self.assertFalse(self.mod._load_summon_pending)
        self.assertIsNone(self.mod.saved_selection)
        self.mod.before_load(0, 0, 0, False, False, 0)
        self.mod.after_load(0, 0, 0, False, False, 0, True)
        self.assertFalse(self.mod._load_summon_pending)
        self.probe(5)
        self.assert_no_native_summon_work()

    def test_new_local_load_replaces_pending_save_identity(self):
        self.prepare(uid=0xA, slot=5)
        replacement = self.seed(888)
        self.set_pet(7, replacement)
        self.mod.store.remember("nms:000000000000000b", replacement, 7)
        self.load_save(0xB)
        self.update(0)
        self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 7)])
        self.assertEqual(self.mod.save_key, "nms:000000000000000b")

    def test_foreign_owner_cannot_consume_local_startup_request(self):
        self.prepare()
        self.update(0, player=self.foreign_player)
        self.assertTrue(self.mod._load_summon_pending)
        self.assert_no_native_summon_work()
        self.update(1)
        self.probe(2.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_lost_or_replaced_application_cancels_load_before_native_calls(self):
        for change in ("null", "replacement"):
            with self.subTest(change=change):
                self.setUp()
                self.prepare()
                self.update(0, dt=0)  # Establish the initial application without arming.
                self.assertTrue(self.mod._load_summon_pending)
                if change == "null":
                    self.app_pointer.value = None
                else:
                    self.replacement_buffer = ctypes.create_string_buffer(0x900000)
                    self.app_pointer.value = ctypes.addressof(self.replacement_buffer)
                self.update(1)
                self.assertFalse(self.mod._load_summon_pending)
                self.assertIsNone(self.mod.save_key)
                self.assert_no_native_summon_work()

    def test_missing_or_ambiguous_favorite_rechecks_at_bounded_rate_without_slot_guess(self):
        for condition in ("unoccupied", "replaced", "duplicate"):
            with self.subTest(condition=condition):
                self.setUp()
                identity = self.prepare(occupied=condition != "unoccupied")
                if condition == "replaced":
                    self.set_pet(5, self.seed(4321))
                elif condition == "duplicate":
                    self.set_pet(7, identity)
                original = self.state_path.read_bytes()
                with patch.object(self.mod, "_restore_selected", wraps=self.mod._restore_selected) as restore:
                    self.update(0)
                    for now in (0.01, 0.1, 0.2, 0.3, 0.49):
                        self.update(now)
                    self.assertEqual(restore.call_count, 1)
                    self.assertTrue(self.mod._load_summon_pending)
                    self.assert_no_native_summon_work()
                    self.update(0.5)
                    self.assertEqual(restore.call_count, 2)
                self.set_pet(5, identity, occupied=False)
                self.set_pet(7, identity)
                self.update(1)
                self.probe(2.5)
                self.assertEqual(self.queue_calls, [(self.player, 7)])
                self.assertEqual(self.state_path.read_bytes(), original)

    def test_no_favorite_consumes_load_without_creating_identity_or_state_file(self):
        self.set_pet(5, self.seed(1234))
        self.load_save(0xA)
        self.update(0)
        self.assertFalse(self.mod._load_summon_pending)
        self.assertIsNone(self.mod.policy.last_slot)
        self.probe(5)
        self.assert_no_native_summon_work()
        self.assertFalse(self.state_path.exists())

    def test_startup_restoration_error_consumes_intent_and_preserves_saved_identity(self):
        self.prepare()
        original = self.state_path.read_bytes()
        with patch.object(self.mod, "_restore_selected", side_effect=RuntimeError("owned restoration failure")), \
                self.assertLogs("CompanionAutoSummon", level="ERROR"):
            self.update(0)
        self.assertFalse(self.mod.enabled)
        self.assertFalse(self.mod._load_summon_pending)
        self.assertFalse(self.mod.policy.pending)
        self.probe(5)
        self.assert_no_native_summon_work()
        self.assertEqual(self.state_path.read_bytes(), original)

    def test_zero_persistent_id_allows_random_session_only_but_no_invented_favorite(self):
        for random_mode in (False, True):
            with self.subTest(random_mode=random_mode):
                self.setUp()
                self.set_pet(5, self.seed(1234))
                if random_mode:
                    self.mod.selection_mode_value = "random"
                with self.assertLogs("CompanionAutoSummon", level="WARNING"):
                    self.load_save(0)
                with patch.object(self.module.random, "choice", return_value=5) as choice:
                    self.update(0)
                    self.probe(1.5)
                self.assertEqual(self.queue_calls, [(self.player, 5)] if random_mode else [])
                self.assertEqual(choice.call_count, int(random_mode))
                self.assertIsNone(self.mod.save_key)
                self.assertIsNone(self.mod.saved_selection)
                self.assertFalse(self.state_path.exists())

    def test_random_startup_retries_same_owned_choice_and_preserves_favorite_in_nexus(self):
        self.prepare(location=14, random_mode=True)
        self.set_pet(7, self.seed(777))
        original = self.state_path.read_bytes()
        accepted_queue = self.module.cas_queue_pet
        rejected = Mock(return_value=None)
        self.module.cas_queue_pet = rejected
        with patch.object(self.module.random, "choice", return_value=7) as choice, patch.object(
            self.mod, "_current_planet_biome", side_effect=AssertionError("Nexus must not read biome")
        ):
            self.update(0)
            self.probe(1.5)
            self.probe(3)
            self.assertTrue(self.mod.policy.pending)
            self.assertFalse(self.mod._load_summon_pending)
            self.module.cas_queue_pet = accepted_queue
            self.probe(5)
            choice.assert_called_once()
        self.assertEqual(self.queue_calls, [(self.player, 7)])
        self.assertEqual(self.mod.saved_selection["slot"], 5)
        self.assertEqual(self.state_path.read_bytes(), original)


class RuntimePreferencesAndRandomTests(RuntimeFixture):
    def random_mode(self):
        self.mod.companion_selection = self.module.SelectionMode("random")
        self.update(0, dt=0)

    def choose(self, slot):
        patched = patch.object(self.module.random, "choice", return_value=slot)
        choice = patched.start()
        self.addCleanup(patched.stop)
        return choice

    def test_preference_patches_merge_and_setters_only_queue(self):
        with patch.object(self.mod.settings_store, "save_preferences", side_effect=AssertionError("I/O")), \
             patch.object(self.mod, "_app_for_player", side_effect=AssertionError("game access")):
            self.mod.planets = False
            self.mod.nexus = False
            self.mod.space_stations = False
            self.mod.planets = True
            self.mod.companion_selection = self.module.SelectionMode("random")
            self.mod.prefer_same_biome = False
            self.mod.automatic_summoning = False
            self.assertTrue(self.mod.planets)
            self.assertFalse(self.mod.nexus)
            self.assertEqual(self.mod.companion_selection.name, "Random")
            self.assertFalse(self.mod.prefer_same_biome)
        self.assertEqual(self.mod.allowed_locations, frozenset({2, 3, 14}))
        self.assertEqual(self.mod.selection_mode_value, "last_manual")
        self.assertTrue(self.mod.prefer_same_biome_value)
        self.update(1, dt=0)
        self.assertEqual(self.mod.allowed_locations, frozenset({3}))
        self.assertFalse(self.mod.auto_enabled)
        self.assertFalse(self.mod.prefer_same_biome_value)
        self.restart()
        self.assertEqual(self.mod.allowed_locations, frozenset({3}))
        self.assertEqual(self.mod.selection_mode_value, "random")
        self.assertFalse(self.mod.auto_enabled)
        self.assertFalse(self.mod.prefer_same_biome_value)

    def test_default_and_invalid_gui_values_do_not_opt_into_random(self):
        self.assertEqual(self.mod.companion_selection.name, "Last manually selected")
        self.assertEqual(self.mod.allowed_locations, frozenset({2, 3, 14}))
        for value in ("random", "Random", True, None):
            self.mod.companion_selection = value
            self.mod.planets = value
        self.assertEqual(self.mod.requested_preferences, {"planets": True})
        self.update(0, dt=0)
        self.assertEqual(self.mod.selection_mode_value, "last_manual")
        self.assertFalse(self.settings_path.exists())

    def test_location_and_mode_change_cancel_and_defer_before_player_applies(self):
        self.select(); self.exit(); self.update(0)
        self.mod.nexus = False
        self.clock.now = 0.01
        self.mod.after_pet_owner_update(self.owner, 1 / 60)
        self.assertTrue(self.mod.policy.pending)
        self.can_summon.assert_not_called()
        self.mod.after_player_update(self.player, 0)
        self.assertFalse(self.mod.policy.pending)
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.assertFalse(self.mod._placement_warmed)

    def test_disabled_supported_location_cancels_without_native_calls(self):
        self.select()
        self.mod.planets = False
        self.update(0, dt=0)
        self.exit(1); self.update(1)
        self.assertFalse(self.mod.policy.pending)
        self.refresh_placement.assert_not_called()
        self.ownership_eligible.assert_not_called()
        self.set_location(2); self.probe(2)
        self.assertEqual(self.queue_calls, [])
        self.exit(3); self.probe(3); self.probe(4.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_all_locations_can_be_disabled_and_survive_restart(self):
        self.mod.planets = False; self.mod.space_stations = False; self.mod.nexus = False
        self.update(0, dt=0); self.restart(); self.select()
        self.assertEqual(self.mod.allowed_locations, frozenset())
        for location in (2, 3, 14):
            self.set_location(location); self.exit(location); self.probe(location)
            self.assertFalse(self.mod.policy.pending)
        self.refresh_placement.assert_not_called()

    def test_random_opt_in_works_without_manual_favorite(self):
        self.set_pet(7, self.seed(7)); choice = self.choose(7)
        self.random_mode(); self.exit(1)
        self.assertIsNone(self.mod.policy.last_slot)
        self.update(1)
        choice.assert_not_called()
        self.can_summon.assert_not_called()
        self.update(1.01)
        choice.assert_called_once_with([7])
        self.assertEqual(self.mod.policy.pending_slot, 7)
        self.probe(2.5)
        self.assertEqual(self.queue_calls, [(self.player, 7)])
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertIsNone(self.mod.saved_selection)
        self.assertFalse(self.state_path.exists())

    def test_random_pool_excludes_empty_unowned_and_currently_ineligible_slots(self):
        for slot in (1, 2, 3, 4): self.set_pet(slot, self.seed(slot))
        self.ownership_eligible.side_effect = lambda owner, slot: slot != 2
        self.can_summon.side_effect = lambda player, slot: slot != 3
        choice = self.choose(4)
        self.random_mode(); self.exit(1); self.probe(1)
        choice.assert_called_once_with([1, 4])
        self.assertEqual({call.args[1] for call in self.ownership_eligible.call_args_list}, {1, 2, 3, 4})
        self.assertNotIn(2, [call.args[1] for call in self.can_summon.call_args_list])

    def test_random_queue_does_not_overwrite_manual_favorite_or_save(self):
        self.set_pet(5, self.seed(5)); self.set_pet(7, self.seed(7))
        self.load_save(123); self.select(5)
        saved = self.state_path.read_bytes(); favorite = dict(self.mod.saved_selection)
        choice = self.choose(7)
        self.random_mode(); self.exit(1); self.probe(1); self.probe(2.5)
        self.assertEqual(self.queue_calls, [(self.player, 7)])
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.assertEqual(self.mod.saved_selection, favorite)
        self.assertEqual(self.state_path.read_bytes(), saved)
        choice.assert_called_once()

    def test_random_rejection_retains_same_choice_without_reroll_for_minutes(self):
        self.set_pet(1, self.seed(1)); self.set_pet(2, self.seed(2))
        choice = self.choose(1)
        self.random_mode(); self.exit(1); self.probe(1)
        rejected = Mock(return_value=None); self.module.cas_queue_pet = rejected
        self.probe(2.5)
        self.assertTrue(self.mod.policy.pending)
        self.can_summon.side_effect = lambda player, slot: slot != 1
        self.probe(3.5); self.probe(300)
        choice.assert_called_once_with([1, 2])
        rejected.assert_called_once_with(self.player, 1)
        self.assertEqual(self.mod.policy.pending_slot, 1)
        self.can_summon.side_effect = None
        self.module.cas_queue_pet = lambda player, slot: self.set_pending(slot)
        self.probe(301)
        self.assertFalse(self.mod.policy.pending)
        self.assertEqual(ctypes.c_int32.from_address(self.player + self.module.PENDING_PET_OFFSET).value, 1)

    def test_no_owned_pets_keeps_random_intent_without_refresh_or_choice(self):
        choice = self.choose(1)
        self.random_mode(); self.exit(1)
        for now in (1, 2, 300): self.probe(now)
        self.assertTrue(self.mod.policy.pending)
        self.refresh_placement.assert_not_called(); self.ownership_eligible.assert_not_called()
        self.can_summon.assert_not_called(); choice.assert_not_called()
        self.assertEqual(self.queue_calls, [])

    def test_random_has_no_reroll_if_selected_identity_is_replaced(self):
        self.set_pet(1, self.seed(1)); choice = self.choose(1)
        self.random_mode(); self.exit(1); self.probe(1)
        self.set_pet(1, self.seed(99)); self.probe(2.5)
        self.assertFalse(self.mod.policy.pending)
        self.assertEqual(self.queue_calls, [])
        choice.assert_called_once()

    def test_manual_override_cancels_random_and_saves_manual_favorite(self):
        self.set_pet(1, self.seed(1)); self.set_pet(5, self.seed(5)); choice = self.choose(1)
        self.random_mode(); self.load_save(123); self.exit(1); self.probe(1)
        self.select(5); self.probe(2.5)
        self.assertFalse(self.mod.policy.pending)
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.assertEqual(self.mod.selection_mode_value, "random")
        self.assertEqual(self.queue_calls, [])
        choice.assert_called_once()

    def test_random_mode_allows_repeat_across_exits_but_not_an_extra_draw_per_exit(self):
        self.set_pet(1, self.seed(1)); choice = self.choose(1)
        self.random_mode(); self.exit(1); self.probe(1); self.probe(2.5)
        self.set_pending(-1); self.probe(20)
        self.assertEqual(len(self.queue_calls), 1)
        choice.assert_called_once()
        self.exit(21); self.probe(21); self.probe(22.5)
        self.assertEqual(self.queue_calls, [(self.player, 1), (self.player, 1)])
        self.assertEqual(choice.call_count, 2)

    def test_final_random_native_check_can_reject_then_retry_same_choice(self):
        self.set_pet(1, self.seed(1)); choice = self.choose(1)
        self.random_mode(); self.exit(1); self.probe(1)
        # Next completed probe passes; its immediate prequeue recheck rejects.
        self.can_summon.side_effect = [True, False]
        self.probe(2.5)
        self.assertEqual(self.queue_calls, [])
        self.assertTrue(self.mod.policy.pending)
        self.can_summon.side_effect = None
        self.probe(3.5)
        self.assertEqual(self.queue_calls, [(self.player, 1)])
        choice.assert_called_once()

    def test_physics_context_zero_or_change_never_consumes_stale_probe(self):
        self.select(); self.exit(); self.update(0)
        address = self.player + self.module.PHYSICS_CONTEXT_OFFSET
        ctypes.c_uint64.from_address(address).value = 2
        self.update(0.01)
        self.can_summon.assert_not_called()
        self.update(0.02)
        self.can_summon.assert_called_once()
        ctypes.c_uint64.from_address(address).value = 0
        calls = self.refresh_placement.call_count
        self.probe(2)
        self.assertEqual(self.refresh_placement.call_count, calls)
        self.assertTrue(self.mod.policy.pending)
        ctypes.c_uint64.from_address(address).value = 3
        self.probe(3)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_large_callback_gap_restarts_priming_instead_of_using_old_jobs(self):
        self.select(); self.exit(); self.update(0)
        self.update(300)
        self.can_summon.assert_not_called()
        self.assertEqual(self.queue_calls, [])
        self.update(300.01)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_location_change_between_probe_callbacks_requires_fresh_pair(self):
        self.select(); self.exit(); self.update(0)
        self.set_location(2); self.update(0.01)
        self.can_summon.assert_not_called()
        self.update(0.02)
        self.can_summon.assert_called_once()

    def test_rejected_retries_do_not_spam_logs_or_hud(self):
        self.select(); self.exit()
        rejected = Mock(return_value=None); self.module.cas_queue_pet = rejected
        with self.assertLogs(self.module.LOGGER, level="INFO") as logs:
            self.probe(0)
            for now in range(2, 102): self.probe(now)
        self.assertEqual(rejected.call_count, 100)
        self.assertEqual(sum("queue was not accepted" in line for line in logs.output), 1)
        self.assertEqual(sum("exit ready after" in line for line in logs.output), 1)
        self.assertEqual(len(self.notice_calls), 1)  # Manual selection only.
        self.assertTrue(self.mod.policy.pending)


class RuntimeBiomeTests(RuntimeFixture):
    def set_planet(self, biome=0, subtype=0, *, count=6, index=0):
        # This independent solar-system allocation is test-owned. Current-index
        # and count fields are outside its six inline planet records.
        if not hasattr(self, "solar_buffer"):
            self.solar_buffer = ctypes.create_string_buffer(0x520000)
            self.solar_address = ctypes.addressof(self.solar_buffer)
        ctypes.c_void_p.from_address(
            self.app_address + self.module.SOLAR_SYSTEM_PTR_OFFSET).value = self.solar_address
        ctypes.c_int32.from_address(
            self.solar_address + self.module.PLANET_COUNT_OFFSET).value = count
        ctypes.c_int32.from_address(
            self.solar_address + self.module.CURRENT_PLANET_INDEX_OFFSET).value = index
        if 0 <= index < 6:
            planet = self.solar_address + index * self.module.PLANET_ENTRY_SIZE
            ctypes.c_uint32.from_address(planet + self.module.PLANET_BIOME_OFFSET).value = biome
            ctypes.c_uint32.from_address(planet + self.module.PLANET_BIOME_SUBTYPE_OFFSET).value = subtype

    def pet_biome(self, slot, biome):
        ctypes.c_uint32.from_address(self.app_address + self.module.PET_TABLE_OFFSET
                                    + slot * self.module.PET_ENTRY_SIZE + self.module.PET_BIOME_OFFSET).value = biome

    def random_mode(self):
        self.mod.companion_selection = self.module.SelectionMode("random")
        self.update(0, dt=0)

    def choose(self, slot):
        patched = patch.object(self.module.random, "choice", return_value=slot)
        choice = patched.start()
        self.addCleanup(patched.stop)
        return choice

    def test_pet_reader_preserves_all_concrete_biomes_and_rejects_sentinels(self):
        for slot in (0, 29):
            for biome in range(18):
                with self.subTest(slot=slot, biome=biome):
                    self.pet_biome(slot, biome)
                    expected = biome if biome in set(range(16)) - {11} else None
                    self.assertEqual(self.mod._pet_biome(self.app_address, slot), expected)

    def test_planet_reader_uses_native_current_index_and_adoption_normalization(self):
        cases = ((0, 0, 0), (6, 0, 6), (0, 25, 12), (3, 26, 13),
                 (8, 0, 7), (9, 0, 7), (10, 0, 7), (8, 25, 12),
                 (10, 26, 13), (12, 31, 12), (15, 0, 15))
        for raw, subtype, expected in cases:
            with self.subTest(raw=raw, subtype=subtype):
                self.set_planet(1, 0, index=0)
                self.set_planet(raw, subtype, index=5)
                self.assertEqual(self.mod._current_planet_biome(self.app_address), expected)

    def test_unavailable_or_unknown_planet_data_returns_none_without_clamping(self):
        self.assertIsNone(self.mod._current_planet_biome(0))
        self.assertIsNone(self.mod._current_planet_biome(self.app_address))  # Null root.
        for count, index in ((0, 0), (-1, 0), (7, 0), (6, -1), (6, 6), (2, 2)):
            with self.subTest(count=count, index=index):
                self.set_planet(count=count, index=index)
                self.assertIsNone(self.mod._current_planet_biome(self.app_address))
        for raw, subtype in ((11, 0), (11, 25), (16, 26), (99, 0), (0, 32), (0, 0xFFFFFFFF)):
            with self.subTest(raw=raw, subtype=subtype):
                self.set_planet(raw, subtype)
                self.assertIsNone(self.mod._current_planet_biome(self.app_address))

    def test_biome_checkbox_defaults_true_is_strict_and_cancels_old_intent_on_apply(self):
        self.assertTrue(self.mod.prefer_same_biome)
        for value in (None, 0, 1, "false", [], {}):
            self.mod.prefer_same_biome = value
        self.assertEqual(self.mod.requested_preferences, {})
        self.select(); self.exit(); self.update(0)
        with patch.object(self.mod.settings_store, "save_preferences", side_effect=AssertionError("I/O")), \
             patch.object(self.mod, "_app_for_player", side_effect=AssertionError("game access")):
            self.mod.prefer_same_biome = False
            self.assertFalse(self.mod.prefer_same_biome)
        self.clock.now = 0.01
        self.mod.after_pet_owner_update(self.owner, 1 / 60)
        self.can_summon.assert_not_called()
        self.mod.after_player_update(self.player, 0)
        self.assertFalse(self.mod.policy.pending)
        self.assertFalse(self.mod._placement_warmed)
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.restart()
        self.assertFalse(self.mod.prefer_same_biome)
        self.assertEqual(self.mod.selection_mode_value, "last_manual")

    def test_last_manual_mode_never_reads_biomes_or_replaces_favorite(self):
        self.set_pet(5, self.seed(5)); self.select(5)
        with patch.object(self.mod, "_current_planet_biome", side_effect=AssertionError("biome read")), \
             patch.object(self.mod, "_pet_biome", side_effect=AssertionError("pet biome read")):
            self.exit(); self.probe(0); self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.assertEqual(self.mod.policy.last_slot, 5)

    def test_matching_pool_is_filtered_after_native_eligibility_and_still_draws_once(self):
        self.set_planet(0)
        for slot, biome in ((1, 0), (2, 0), (3, 0), (4, 1), (5, 0), (6, 16)):
            self.set_pet(slot, self.seed(slot)); self.pet_biome(slot, biome)
        self.ownership_eligible.side_effect = lambda owner, slot: slot != 2
        self.can_summon.side_effect = lambda player, slot: slot != 3
        choice = self.choose(5)
        with patch.object(self.mod, "_pet_biome", wraps=self.mod._pet_biome) as reader:
            self.random_mode(); self.exit(1); self.probe(1); self.probe(2.5)
        choice.assert_called_once_with([1, 5])
        self.assertEqual([call.args[1] for call in reader.call_args_list], [1, 4, 5, 6])
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertFalse(self.state_path.exists())

    def test_native_swamp_and_lava_normalization_selects_stored_pet_habitat(self):
        for subtype, habitat in ((25, 12), (26, 13)):
            with self.subTest(subtype=subtype):
                self.set_planet(8, subtype)
                self.pet_biome(1, habitat); self.pet_biome(2, 8)
                self.mod.selection_mode_value = "random"
                self.assertEqual(self.mod._random_biome_pool(self.app_address, 3, [1, 2]), [1])

    def test_disabled_preference_keeps_ordinary_random_without_biome_reads(self):
        for slot in (1, 2): self.set_pet(slot, self.seed(slot))
        self.random_mode(); self.mod.prefer_same_biome = False; self.update(0, dt=0)
        choice = self.choose(2)
        with patch.object(self.mod, "_current_planet_biome", side_effect=AssertionError("biome read")):
            self.exit(1); self.probe(1); self.probe(2.5)
        choice.assert_called_once_with([1, 2])
        self.assertEqual(self.queue_calls, [(self.player, 2)])

    def test_station_and_nexus_never_read_planet_biome(self):
        self.mod.selection_mode_value = "random"
        with patch.object(self.mod, "_current_planet_biome", side_effect=AssertionError("biome read")), \
             patch.object(self.mod, "_pet_biome", side_effect=AssertionError("pet biome read")):
            for location in (2, 14):
                self.assertEqual(self.mod._random_biome_pool(self.app_address, location, [1, 2]), [1, 2])

    def test_unknown_planet_or_no_matching_pet_falls_back_to_whole_eligible_pool(self):
        self.mod.selection_mode_value = "random"
        for planet in (None, 0):
            with self.subTest(planet=planet), patch.object(self.mod, "_current_planet_biome", return_value=planet), \
                 patch.object(self.mod, "_pet_biome", side_effect=lambda app, slot: {1: None, 2: 2}[slot]):
                self.assertEqual(self.mod._random_biome_pool(self.app_address, 3, [1, 2]), [1, 2])

    def test_biome_change_after_draw_never_rerolls_or_overwrites_manual_favorite(self):
        self.set_planet(0)
        for slot, biome in ((1, 0), (2, 1), (5, 1)):
            self.set_pet(slot, self.seed(slot)); self.pet_biome(slot, biome)
        self.load_save(123); self.select(5)
        saved = self.state_path.read_bytes()
        choice = self.choose(1)
        self.random_mode(); self.exit(1); self.probe(1)
        queue = self.module.cas_queue_pet
        self.module.cas_queue_pet = Mock(return_value=None)
        self.probe(2.5)
        self.assertTrue(self.mod.policy.pending)
        self.set_planet(1)
        self.module.cas_queue_pet = queue
        self.probe(300)
        choice.assert_called_once_with([1])
        self.assertEqual(self.queue_calls, [(self.player, 1)])
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.assertEqual(self.state_path.read_bytes(), saved)

    def test_optional_biome_read_errors_fall_back_without_hiding_native_failures(self):
        self.mod.selection_mode_value = "random"
        for method in ("_current_planet_biome", "_pet_biome"):
            for failure in (OSError("test unavailable"), ValueError("test invalid read")):
                with self.subTest(method=method, failure=type(failure).__name__):
                    self.set_planet(0)
                    with patch.object(self.mod, method, side_effect=failure):
                        self.assertEqual(self.mod._random_biome_pool(self.app_address, 3, [1, 2]), [1, 2])
                    self.assertTrue(self.mod.enabled)
        self.set_pet(1, self.seed(1)); self.exit(1)
        self.can_summon.side_effect = OSError("native permission failure")
        with self.assertLogs(self.module.LOGGER, level="ERROR"):
            self.probe(1)
        self.assertFalse(self.mod.enabled)
        self.assertEqual(self.queue_calls, [])


class RuntimeControlTests(RuntimeFixture):
    def test_gui_controls_are_a_boolean_and_two_read_only_status_properties(self):
        controls = {
            "automatic_summoning": "BOOLEAN",
            "planets": "BOOLEAN",
            "space_stations": "BOOLEAN",
            "nexus": "BOOLEAN",
            "companion_selection": "ENUM",
            "prefer_same_biome": "BOOLEAN",
            "control_status": "STRING",
            "companion_status": "STRING",
        }
        for name, kind in controls.items():
            prop = getattr(self.module.CompanionAutoSummon, name)
            self.assertIsInstance(prop, property)
            self.assertEqual(prop.fget._test_gui_type, kind)
            self.assertTrue(prop.fget._test_gui_label)
        for name in ("control_status", "companion_status"):
            with self.subTest(name=name), self.assertRaises(AttributeError):
                setattr(self.mod, name, "override")

    def test_gui_setter_only_queues_latest_boolean_without_io_or_game_calls(self):
        with patch.object(self.mod, "_app_for_player", side_effect=AssertionError("game read")), patch.object(
            self.mod.settings_store, "save_preferences", side_effect=AssertionError("file write")
        ), patch.object(Path, "open", side_effect=AssertionError("file read")):
            self.mod.automatic_summoning = False
            self.mod.automatic_summoning = True
            self.mod.automatic_summoning = False
            self.assertFalse(self.mod.automatic_summoning)
            self.assertIn("pending", self.mod.control_status.lower())
        self.assertTrue(self.mod.auto_enabled)
        self.assertIs(self.mod.requested_preferences.get("enabled"), False)
        self.can_summon.assert_not_called()
        self.module.cas_add_timed_message.assert_not_called()
        self.assertFalse(self.settings_path.exists())

    def test_nonboolean_ui_requests_are_ignored(self):
        for value in (0, 1, "false", None):
            self.mod.automatic_summoning = value
        self.assertIsNone(self.mod.requested_preferences.get("enabled"))
        self.assertTrue(self.mod.automatic_summoning)

    def test_control_applies_only_on_local_update_even_when_paused(self):
        self.mod.automatic_summoning = False
        self.update(0, dt=0, player=self.foreign_player)
        self.assertTrue(self.mod.auto_enabled)
        self.assertFalse(self.settings_path.exists())
        self.update(1, dt=0)
        self.assertFalse(self.mod.auto_enabled)
        self.assertFalse(json.loads(self.settings_path.read_text())["enabled"])
        self.assertEqual(self.notice_calls, [])
        self.assertIsNotNone(self.mod.pending_notice)
        self.update(2)
        self.assertEqual(len(self.notice_calls), 1)
        self.assertIn("OFF", self.notice_calls[0]["message"])
        self.update(3)
        self.assertEqual(len(self.notice_calls), 1)

    def test_off_cancels_armed_request_and_keeps_selected_companion(self):
        self.select(5)
        self.exit()
        self.update(0)
        self.mod.automatic_summoning = False
        self.update(1, dt=0)
        self.assertFalse(self.mod.policy.pending)
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.update(2)
        self.exit(3)
        self.update(3)
        self.update(5)
        self.assertEqual(self.queue_calls, [])

    def test_on_cancels_old_request_and_waits_for_next_ship_exit(self):
        self.select(5)
        self.mod.automatic_summoning = False
        self.update(0, dt=0)
        # Exercise cancellation in the ON direction as well as normal OFF.
        self.mod.policy.eject(0)
        self.assertTrue(self.mod.policy.pending)
        self.mod.automatic_summoning = True
        self.update(1, dt=0)
        self.assertFalse(self.mod.policy.pending)
        self.update(3)
        self.assertEqual(self.queue_calls, [])
        self.exit(4)
        self.update(4)
        self.probe(5.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])

    def test_failure_latch_cannot_be_overridden_from_ui(self):
        self.mod.enabled = False
        self.mod.automatic_summoning = True
        self.assertFalse(self.mod.automatic_summoning)
        self.assertIsNone(self.mod.requested_preferences.get("enabled"))
        self.assertIn("restart", self.mod.control_status.lower())
        self.update(0)
        self.assertFalse(self.settings_path.exists())
        self.can_summon.assert_not_called()
        self.module.cas_add_timed_message.assert_not_called()

    def test_off_still_remembers_manual_pet_and_announces_disabled_state(self):
        self.load_save(0xA)
        self.mod.automatic_summoning = False
        self.update(0)
        self.notice_calls.clear()
        self.set_pet(5, self.seed(42))
        self.select(5)
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.assertEqual(json.loads(self.state_path.read_text())["selections"]["nms:000000000000000a"]["slot"], 5)
        self.update(1)
        self.assertEqual(len(self.notice_calls), 1)
        self.assertIn("OFF", self.notice_calls[0]["message"])
        self.exit(2)
        self.update(2)
        self.update(4)
        self.assertEqual(self.queue_calls, [])

    def test_toggle_persists_off_and_on_across_fresh_instances(self):
        self.assertTrue(self.mod.auto_enabled)
        self.assertFalse(self.settings_path.exists())
        self.mod.automatic_summoning = False
        self.update(0, dt=0)
        self.restart()
        self.assertFalse(self.mod.auto_enabled)
        self.mod.automatic_summoning = True
        self.update(0, dt=0)
        self.restart()
        self.assertTrue(self.mod.auto_enabled)

    def test_corrupt_settings_start_off_and_session_toggle_preserves_file(self):
        corrupt = b"{keep-this-invalid-json"
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_bytes(corrupt)
        with self.assertLogs("CompanionAutoSummon", level="WARNING"):
            self.restart()
        self.assertFalse(self.mod.auto_enabled)
        self.assertFalse(self.mod.settings_ok)
        self.mod.automatic_summoning = True
        self.update(0, dt=0)
        self.assertTrue(self.mod.auto_enabled)
        self.assertIn("session only", self.mod.control_status)
        self.assertEqual(self.settings_path.read_bytes(), corrupt)

    def test_settings_write_failure_keeps_session_toggle_without_overwriting(self):
        self.mod.settings_store.save(True)
        original = self.settings_path.read_bytes()
        self.mod.automatic_summoning = False
        with patch.object(self.mod.settings_store, "save_preferences", side_effect=self.module.SettingsStoreError("test write failure")), self.assertLogs(
            "CompanionAutoSummon", level="WARNING"
        ):
            self.update(0, dt=0)
        self.assertFalse(self.mod.auto_enabled)
        self.assertFalse(self.mod.settings_ok)
        self.assertEqual(self.settings_path.read_bytes(), original)

    def test_first_and_changed_manual_pet_each_emit_one_confirmation(self):
        self.set_pet(5, self.seed(42))
        self.set_pet(7, self.seed(84))
        self.select(5)
        self.assertEqual(self.notice_calls, [])
        self.update(0)
        self.assertEqual(len(self.notice_calls), 1)
        self.select(5)
        self.update(1)
        self.assertEqual(len(self.notice_calls), 1)
        self.select(7)
        self.update(2)
        self.update(3)
        self.assertEqual(len(self.notice_calls), 2)
        self.assertIn("slot 8", self.mod.companion_status)

    def test_automatic_queue_does_not_repeat_selection_confirmation(self):
        self.select(5)
        self.exit()
        self.update(0)
        self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.assertEqual(len(self.notice_calls), 1)
        self.assertIsNone(self.mod.pending_notice)

    def test_restored_companion_does_not_create_selection_confirmation(self):
        self.load_save(0xA)
        self.set_pet(5, self.seed(42))
        self.select(5)
        self.restart()
        self.load_save(0xA)
        self.assertIn("Remembered", self.mod.companion_status)
        self.exit()
        self.update(0)
        self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.assertEqual(self.notice_calls, [])

    def test_notification_arguments_are_owned_aligned_and_silent(self):
        self.select(5)
        self.update(0)
        self.assertEqual(len(self.notice_calls), 1)
        notice = self.notice_calls[0]
        self.assertEqual(notice["notifications"], self.app_address + self.module.NOTIFICATIONS_OFFSET)
        self.assertEqual(notice["colour_address"] % 16, 0)
        self.assertEqual(notice["colour"], (1.0, 1.0, 1.0, 1.0))
        self.assertEqual(notice["duration"], 3.0)
        self.assertEqual(notice["audio"], 0)
        self.assertEqual(notice["icon"], 0)
        self.assertEqual(notice["tail"], (False, 0.0, False, False, False))
        self.assertIn("companion selected", notice["message"])

    def test_full_or_blocked_notification_queue_delays_latest_notice(self):
        self.mod.pending_notice = "first"
        self.set_notice_state(count=4, block=-1)
        self.update(0)
        self.assertEqual(self.notice_calls, [])
        self.mod.pending_notice = "latest"
        self.set_notice_state(count=0, block=0)
        self.update(1)
        self.assertEqual(self.notice_calls, [])
        self.set_notice_state(count=0, block=-1)
        self.update(2)
        self.update(3)
        self.assertEqual([notice["message"] for notice in self.notice_calls], ["latest"])

    def test_notification_failure_disables_hud_only_and_does_not_retry(self):
        self.module.cas_add_timed_message.side_effect = RuntimeError("test HUD failure")
        self.select(5)
        self.exit()
        with self.assertLogs("CompanionAutoSummon", level="WARNING"):
            self.update(0)
        self.assertTrue(self.mod.enabled)
        self.assertFalse(self.mod.notifications_ok)
        self.assertIsNone(self.mod.pending_notice)
        self.probe(1.5)
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.module.cas_add_timed_message.assert_called_once()


class RuntimePostQueueObservationTests(RuntimeFixture):
    """Passive native-state evidence never grants another summon opportunity."""

    def accept_queue(self, *, source="ship exit", location=14, random_mode=False):
        self.set_location(location)
        self.set_pet(5, self.seed(0x13579, 91))
        self.set_pet(7, self.seed(0x24680, 92))
        self.load_save(0xABCD)
        self.select(5)
        if random_mode:
            self.mod.selection_mode_value = "random"
            self.module.random = types.SimpleNamespace(choice=Mock(return_value=7))
        if source == "save load":
            self.load_save(0xABCD)
        else:
            self.exit(1)
        self.probe(1)
        self.probe(2.5)
        self.observed_slot = 7 if random_mode else 5
        self.assertEqual(self.queue_calls, [(self.player, self.observed_slot)])
        self.assertFalse(self.mod.policy.pending)
        self.assertFalse(self.mod._load_summon_pending)
        self.assertIsNotNone(self.mod._summon_observation)
        self.accepted_at = self.mod._summon_observation["accepted_at"]
        self.module.LOGGER = Mock()

    def observe(self, now, *, dt=1 / 60, owner=None):
        self.clock.now = now
        self.mod.after_pet_owner_update(self.owner if owner is None else owner, dt)

    def begin_passive_checks(self):
        self.policy_before = dict(vars(self.mod.policy))
        self.favorite_before = dict(self.mod.saved_selection)
        self.identity_before = self.mod.pet_identity
        self.preferences_before = self.mod._current_preferences()
        self.saved_before = self.state_path.read_bytes()
        self.settings_before = self.settings_path.read_bytes() if self.settings_path.exists() else None
        self.policy_spies = []
        for name in ("eject", "tick", "resolve", "remember", "enter_ship", "reset", "select_for_exit"):
            spy = Mock(wraps=getattr(self.mod.policy, name))
            setattr(self.mod.policy, name, spy)
            self.policy_spies.append(spy)
        self.native_spies = []
        for name in ("cas_can_summon", "cas_owned_pet_eligible", "cas_use_summon_hand",
                     "cas_refresh_pet_placement", "cas_queue_pet", "cas_add_timed_message"):
            spy = Mock(side_effect=AssertionError("Passive observation called native code"))
            setattr(self.module, name, spy)
            self.native_spies.append(spy)
        self.persistence_spies = []
        for owner, name in ((self.mod.store, "remember"), (self.mod.settings_store, "save_preferences")):
            spy = Mock(wraps=getattr(owner, name))
            setattr(owner, name, spy)
            self.persistence_spies.append(spy)

    def assert_passive(self):
        for spy in self.policy_spies + self.native_spies + self.persistence_spies:
            spy.assert_not_called()
        actual_policy = {key: value for key, value in vars(self.mod.policy).items()
                         if key in self.policy_before}
        self.assertEqual(actual_policy, self.policy_before)
        self.assertEqual(self.mod.saved_selection, self.favorite_before)
        self.assertEqual(self.mod.pet_identity, self.identity_before)
        self.assertEqual(self.mod._current_preferences(), self.preferences_before)
        self.assertEqual(self.mod.requested_preferences, {})
        self.assertEqual(self.state_path.read_bytes(), self.saved_before)
        self.assertEqual(self.settings_path.read_bytes() if self.settings_path.exists() else None,
                         self.settings_before)
        self.assertEqual(self.queue_calls, [(self.player, self.observed_slot)])
        self.assertFalse(self.mod.policy.pending)
        self.assertFalse(self.mod._load_summon_pending)
        self.assertTrue(self.mod.enabled)

    def messages(self):
        result = []
        for call in self.module.LOGGER.mock_calls:
            if call.args:
                template, *arguments = call.args
                result.append(str(template) % tuple(arguments) if arguments else str(template))
        return result

    def test_accepted_queue_observes_native_active_once_then_dismissal_never_rearms(self):
        for source in ("ship exit", "save load"):
            with self.subTest(source=source):
                self.setUp()
                self.accept_queue(source=source)
                self.assertEqual(self.mod._summon_observation["source"], source)
                self.begin_passive_checks()
                self.set_pending(-1)
                self.set_active(self.observed_slot)
                self.observe(3)
                self.assertIsNone(self.mod._summon_observation)
                terminal_messages = list(self.messages())
                self.assertTrue(any("active" in line for line in terminal_messages))
                self.assertFalse(any(word in " ".join(terminal_messages).lower()
                                     for word in ("visible", "materialized", "spawn succeeded")))
                self.set_active(-1)
                self.observe(4)
                self.observe(100)
                self.assertEqual(self.messages(), terminal_messages)
                self.assert_passive()

    def test_cleared_queue_without_active_observation_remains_indeterminate_and_never_retries(self):
        self.accept_queue()
        self.begin_passive_checks()
        self.set_pending(-1)
        self.observe(3)
        self.assertIsNotNone(self.mod._summon_observation)
        self.assertTrue(any("indeterminate" in line for line in self.messages()))
        initial_messages = list(self.messages())
        for now in (4, 5, 7, 10):
            self.observe(now)
        self.assertEqual(self.messages(), initial_messages)
        self.observe(self.accepted_at + self.module.POST_QUEUE_OBSERVATION_SECONDS)
        self.assertIsNone(self.mod._summon_observation)
        self.observe(1000)
        self.assert_passive()

    def test_native_active_after_an_empty_interval_is_observed_without_a_second_request(self):
        self.accept_queue()
        self.begin_passive_checks()
        self.set_pending(-1)
        self.observe(3)
        self.set_pending(self.observed_slot)
        self.observe(4)
        self.set_pending(-1)
        self.set_active(self.observed_slot)
        self.observe(5)
        self.assertIsNone(self.mod._summon_observation)
        self.assertTrue(any("indeterminate" in line for line in self.messages()))
        self.assertTrue(any("active" in line for line in self.messages()))
        self.assert_passive()

    def test_random_observation_preserves_distinct_manual_favorite_and_private_identity(self):
        self.accept_queue(random_mode=True)
        self.assertEqual(self.mod.policy.last_slot, 5)
        self.assertEqual(self.mod._summon_observation["slot"], 7)
        identity = self.seed(0x24680, 92)
        self.assertEqual(self.mod._summon_observation["identity"], identity)
        self.begin_passive_checks()
        self.set_pending(-1)
        self.observe(3)
        self.set_active(7)
        self.observe(4)
        self.assertIsNone(self.mod._summon_observation)
        messages = " ".join(self.messages())
        for private_value in (identity.hex(), self.mod.save_key, str(self.app_address), str(self.state_path)):
            self.assertNotIn(private_value, messages)
        self.assert_passive()

    def test_same_slot_with_changed_identity_is_not_reported_as_original_active_companion(self):
        self.accept_queue()
        self.begin_passive_checks()
        self.set_pet(self.observed_slot, self.seed(0x99999, 93))
        self.set_pending(-1)
        self.set_active(self.observed_slot)
        self.observe(3)
        self.assertIsNone(self.mod._summon_observation)
        self.assertTrue(any("identity" in line for line in self.messages()))
        self.assert_passive()

    def test_foreign_owner_callbacks_do_not_dereference_or_consume_local_budget(self):
        self.accept_queue()
        self.begin_passive_checks()
        record = self.mod._summon_observation
        before = dict(record)
        global_read = Mock(return_value=types.SimpleNamespace(value=self.app_address))
        field_read = Mock(side_effect=AssertionError("Foreign owner fields must not be read"))
        fake_c = types.SimpleNamespace(c_void_p=types.SimpleNamespace(from_address=global_read),
                                       c_int32=types.SimpleNamespace(from_address=field_read),
                                       c_ubyte=types.SimpleNamespace(from_address=field_read))
        with patch.object(self.module, "C", fake_c):
            for owner in (1, self.owner + 0x80):
                self.observe(3, owner=owner)
        self.assertIs(self.mod._summon_observation, record)
        self.assertEqual(record["updates"], before["updates"])
        self.assertEqual(record["callbacks"], before["callbacks"] + 2)
        self.assertEqual(record["last_time"], 3)
        for key in before.keys() - {"callbacks", "last_time"}:
            self.assertEqual(record[key], before[key])
        self.assertEqual(global_read.call_count, 2)
        field_read.assert_not_called()
        self.assertEqual(self.messages(), [])
        self.assert_passive()

    def test_foreign_only_callback_at_deadline_terminates_before_any_native_read(self):
        self.accept_queue()
        self.begin_passive_checks()
        forbidden = Mock(side_effect=AssertionError("Expired observer must not read native memory"))
        fake_c = types.SimpleNamespace(c_void_p=types.SimpleNamespace(from_address=forbidden),
                                       c_int32=types.SimpleNamespace(from_address=forbidden),
                                       c_ubyte=types.SimpleNamespace(from_address=forbidden))
        with patch.object(self.module, "C", fake_c):
            self.observe(self.accepted_at + self.module.POST_QUEUE_OBSERVATION_SECONDS, owner=1)
            self.assertIsNone(self.mod._summon_observation)
            self.observe(1000, owner=1)
        forbidden.assert_not_called()
        self.assertTrue(any("time limit" in line for line in self.messages()))
        self.assert_passive()

    def test_foreign_callback_storm_has_bounded_global_reads_without_local_updates(self):
        self.accept_queue()
        self.begin_passive_checks()
        record = self.mod._summon_observation
        global_read = Mock(return_value=types.SimpleNamespace(value=self.app_address))
        field_read = Mock(side_effect=AssertionError("Foreign owner fields must not be read"))
        fake_c = types.SimpleNamespace(c_void_p=types.SimpleNamespace(from_address=global_read),
                                       c_int32=types.SimpleNamespace(from_address=field_read),
                                       c_ubyte=types.SimpleNamespace(from_address=field_read))
        with patch.object(self.module, "C", fake_c):
            for _ in range(self.module.POST_QUEUE_OBSERVATION_MAX_UPDATES + 10):
                self.observe(3, owner=1)
        self.assertIsNone(self.mod._summon_observation)
        self.assertEqual(record["updates"], 0)
        self.assertEqual(record["callbacks"], self.module.POST_QUEUE_OBSERVATION_MAX_UPDATES)
        self.assertEqual(global_read.call_count, self.module.POST_QUEUE_OBSERVATION_MAX_UPDATES)
        field_read.assert_not_called()
        self.assertEqual(len(self.messages()), 1)
        self.assertTrue(any("callback limit" in line for line in self.messages()))
        self.assert_passive()

    def test_null_or_replaced_application_only_cancels_diagnostic(self):
        for pointer in (None, 1):
            with self.subTest(pointer=pointer):
                self.setUp()
                self.accept_queue()
                self.begin_passive_checks()
                self.app_pointer.value = pointer
                self.observe(3)
                self.assertIsNone(self.mod._summon_observation)
                self.assert_passive()

    def test_other_active_or_pending_slot_ends_observation_without_changing_gameplay(self):
        for field in ("active", "pending"):
            with self.subTest(field=field):
                self.setUp()
                self.accept_queue()
                self.begin_passive_checks()
                (self.set_active if field == "active" else self.set_pending)(8)
                self.observe(3)
                self.assertIsNone(self.mod._summon_observation)
                self.assert_passive()

    def test_invalid_native_indices_cancel_diagnostic_only(self):
        for field in ("active", "pending"):
            for invalid in (-2, 30):
                with self.subTest(field=field, invalid=invalid):
                    self.setUp()
                    self.accept_queue()
                    self.begin_passive_checks()
                    (self.set_active if field == "active" else self.set_pending)(invalid)
                    self.observe(3)
                    self.assertIsNone(self.mod._summon_observation)
                    self.assert_passive()

    def test_preview_emote_location_or_automation_off_cancel_without_gameplay_actions(self):
        for cause in ("preview", "emote", "location", "off"):
            with self.subTest(cause=cause):
                self.setUp()
                self.accept_queue()
                if cause == "off":
                    self.mod.auto_enabled = False
                self.begin_passive_checks()
                if cause == "preview":
                    self.set_preview(5)
                elif cause == "emote":
                    self.set_preview(-1, emote=1)
                elif cause == "location":
                    self.set_location(4)
                self.observe(3)
                self.assertIsNone(self.mod._summon_observation)
                self.assert_passive()

    def test_pending_preference_edit_stops_observer_without_applying_or_persisting_it(self):
        self.accept_queue()
        self.begin_passive_checks()
        self.mod.automatic_summoning = False
        self.observe(3)
        self.assertIsNone(self.mod._summon_observation)
        self.assertEqual(self.mod.requested_preferences, {"enabled": False})
        self.assertTrue(self.mod.auto_enabled)
        self.mod.requested_preferences.clear()
        self.assert_passive()

    def test_local_load_ship_entry_manual_selection_and_applied_preferences_cancel_record(self):
        for cause in ("load", "ship", "manual", "settings"):
            with self.subTest(cause=cause):
                self.setUp()
                self.accept_queue()
                if cause == "load":
                    self.load_save(0xDCBA, success=False)
                elif cause == "ship":
                    self.mod.before_enter_ship(self.player)
                elif cause == "manual":
                    self.select(7)
                else:
                    self.mod.automatic_summoning = False
                    self.mod.after_player_update(self.player, 0)
                self.assertIsNone(self.mod._summon_observation)
                self.assertEqual(self.queue_calls, [(self.player, 5)])
                self.assertFalse(self.mod.policy.pending)
                self.assertTrue(self.mod.enabled)

    def test_network_load_and_foreign_ship_or_manual_events_preserve_local_observer(self):
        self.accept_queue()
        record = self.mod._summon_observation
        self.load_save(0xDCBA, network=True)
        self.mod.before_enter_ship(self.foreign_player)
        self.mod.remember_pet(self.foreign_player, 7)
        self.exit(3, player=self.foreign_player)
        self.assertIs(self.mod._summon_observation, record)
        self.assertEqual(self.queue_calls, [(self.player, 5)])
        self.assertFalse(self.mod.policy.pending)

    def test_nonfinite_or_backward_monotonic_clock_stops_only_diagnostic(self):
        for now in (float("nan"), float("inf"), float("-inf"), 0):
            with self.subTest(now=now):
                self.setUp()
                self.accept_queue()
                self.begin_passive_checks()
                self.observe(now)
                self.assertIsNone(self.mod._summon_observation)
                self.assert_passive()

    def test_nonadvancing_dt_still_has_a_finite_wall_clock_observation_window(self):
        self.accept_queue()
        self.begin_passive_checks()
        for dt in (0, -0.1, float("nan"), float("inf")):
            self.observe(3, dt=dt)
            self.assertIsNotNone(self.mod._summon_observation)
        self.observe(self.accepted_at + self.module.POST_QUEUE_OBSERVATION_SECONDS, dt=0)
        self.assertIsNone(self.mod._summon_observation)
        self.assert_passive()

    def test_nonadvancing_clock_has_a_finite_local_update_budget(self):
        self.accept_queue()
        self.begin_passive_checks()
        for _ in range(self.module.POST_QUEUE_OBSERVATION_MAX_UPDATES + 1):
            self.observe(3, dt=0)
        self.assertIsNone(self.mod._summon_observation)
        self.assertLessEqual(len(self.messages()), self.module.POST_QUEUE_OBSERVATION_TRANSITION_LIMIT + 3)
        self.assert_passive()

    def test_flapping_state_logs_are_capped_and_terminal_timeout_remains_available(self):
        self.accept_queue()
        self.begin_passive_checks()
        for index in range(40):
            self.set_pending(-1 if index % 2 else self.observed_slot)
            self.observe(3 + index / 100)
        self.assertIsNotNone(self.mod._summon_observation)
        self.assertLessEqual(len(self.messages()), self.module.POST_QUEUE_OBSERVATION_TRANSITION_LIMIT + 1)
        previous = len(self.messages())
        self.observe(self.accepted_at + self.module.POST_QUEUE_OBSERVATION_SECONDS)
        self.assertIsNone(self.mod._summon_observation)
        self.assertEqual(len(self.messages()), previous + 1)
        self.assert_passive()

    def test_diagnostic_logging_failure_never_disables_runtime_or_alters_policy(self):
        for stage in ("transition", "terminal"):
            with self.subTest(stage=stage):
                self.setUp()
                self.accept_queue()
                self.begin_passive_checks()
                self.module.LOGGER.info.side_effect = RuntimeError("synthetic logging failure")
                if stage == "terminal":
                    self.set_pending(-1)
                    self.set_active(self.observed_slot)
                self.observe(3)
                self.assertIsNone(self.mod._summon_observation)
                self.assert_passive()

    def test_diagnostic_arm_logging_failure_cannot_fail_closed_or_change_completed_request(self):
        self.accept_queue()
        record = dict(self.mod._summon_observation)
        self.mod._finish_summon_observation("synthetic replacement")
        self.begin_passive_checks()
        self.module.LOGGER.info.side_effect = RuntimeError("synthetic start logging failure")
        self.mod._arm_summon_observation(
            record["app"], record["slot"], record["identity"], record["source"],
            record["location"], record["accepted_at"],
        )
        self.assertIsNone(self.mod._summon_observation)
        self.assert_passive()

    def test_diagnostic_native_read_failure_does_not_fail_closed_gameplay(self):
        self.accept_queue()
        self.begin_passive_checks()
        with patch.object(self.mod, "_pet_seed", side_effect=RuntimeError("synthetic read failure")):
            self.observe(3)
        self.assertIsNone(self.mod._summon_observation)
        self.assert_passive()

    def test_rejected_queue_does_not_start_passive_observation(self):
        self.set_pet(5, self.seed(5))
        self.select(5)
        self.module.cas_queue_pet = Mock(return_value=None)
        self.exit(1)
        self.probe(1)
        self.probe(2.5)
        self.module.cas_queue_pet.assert_called_once_with(self.player, 5)
        self.assertIsNone(self.mod._summon_observation)
        self.assertTrue(self.mod.policy.pending)


if __name__ == "__main__":
    unittest.main()
