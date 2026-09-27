"""Submenu adapter checks using a fake framework and owned synthetic memory."""

import ctypes
import hashlib
import importlib.util
import inspect
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

from test_quick_menu_item import ITEM, ItemFixture


SOURCE = Path(__file__).resolve().parents[1] / "quick_menu_submenu_trial.py"
HELPER_SOURCE = SOURCE.with_name("quick_menu_submenu.py")
EXPECTED_HASH = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"


def load_trial(*, enabled=False, injected=True, base=0x100000,
               framework="0.2.4", digest=EXPECTED_HASH):
    source = SOURCE.read_text(encoding="utf-8")
    if enabled:
        if source.count("TRIAL_ENABLED = False") != 1:
            raise AssertionError("Expected one disabled trial marker")
        source = source.replace("TRIAL_ENABLED = False", "TRIAL_ENABLED = True", 1)
    events, declarations = [], []

    class FakeMod:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            events.append(("class", cls._disabled))

        def __init__(self):
            self._abc_initialised = True
            self.hooks = {getattr(self, name) for name in type(self).__dict__
                          if hasattr(getattr(type(self), name), "_test_hook_offset")}
            self._gui_widgets = []
            self._hotkey_funcs = []

    class FakeNative:
        def __init__(self, function, offset):
            self.function, self.offset = function, offset
            declarations.append(self)

        def before(self, callback):
            callback._test_hook_offset = self.offset
            callback._test_hook_time = "before"
            return callback

        def after(self, callback):
            if self.function.__annotations__.get("return") is ctypes.c_bool:
                if "_result_" not in inspect.signature(callback).parameters:
                    raise AssertionError("Boolean AFTER callback must expose native result")
            callback._test_hook_offset = self.offset
            callback._test_hook_time = "after"
            return callback

        def __call__(self, *args):
            raise AssertionError("Offline tests must not call a real game wrapper")

    internal = types.ModuleType("pymhf.core._internal")
    internal.IS_INJECTED, internal.BASE_ADDRESS = injected, base
    internal.BINARY_PATH = "synthetic-submenu-trial.exe"
    pymhf = types.ModuleType("pymhf")
    pymhf.__path__, pymhf.Mod = [], FakeMod
    core = types.ModuleType("pymhf.core")
    core.__path__, core._internal = [], internal
    hooking = types.ModuleType("pymhf.core.hooking")
    hooking.static_function_hook = lambda *, offset: lambda function: FakeNative(function, offset)
    core.hooking, pymhf.core = hooking, core
    runtime = types.ModuleType("quick_menu_guard_runtime")
    runtime.GuardError = type("GuardError", (RuntimeError,), {})
    runtime.ensure_guard = Mock(side_effect=AssertionError("Import must not install native hooks"))

    helper_spec = importlib.util.spec_from_file_location("quick_menu_submenu_under_test", HELPER_SOURCE)
    helper = importlib.util.module_from_spec(helper_spec)
    with patch.dict(sys.modules, {"quick_menu_item": ITEM, helper_spec.name: helper}):
        helper_spec.loader.exec_module(helper)

    def fake_version(name):
        events.append(("version", name))
        return framework

    def fake_open(path, mode="r", *args, **kwargs):
        if str(path) != internal.BINARY_PATH or mode != "rb":
            raise AssertionError("Unexpected file access")
        events.append(("binary",))
        return io.BytesIO(b"owned synthetic executable")

    module = types.ModuleType("quick_menu_submenu_trial_under_test")
    module.__file__ = str(SOURCE)
    with patch.dict(sys.modules, {
        "quick_menu_item": ITEM, "quick_menu_submenu": helper,
        "quick_menu_guard_runtime": runtime, "pymhf": pymhf,
        "pymhf.core": core, "pymhf.core._internal": internal,
        "pymhf.core.hooking": hooking,
    }), patch("importlib.metadata.version", side_effect=fake_version), patch.object(
        Path, "open", fake_open
    ), patch.object(hashlib, "file_digest", return_value=Mock(hexdigest=lambda: digest)), patch.object(
        ctypes, "WinDLL", side_effect=AssertionError("No Windows APIs on import"), create=True
    ), patch.object(
        ctypes, "WINFUNCTYPE", side_effect=AssertionError("No native bindings on import"), create=True
    ):
        exec(compile(source, str(SOURCE), "exec"), module.__dict__)
    module.test_events, module.test_declarations = events, declarations
    module.LOGGER = Mock()
    module.get_native_id = Mock(return_value=271828)
    return module


class GuardAndInitializationTests(unittest.TestCase):
    def test_disabled_import_and_instance_perform_no_native_initialization(self):
        module = load_trial()
        self.assertEqual(module.test_events, [("class", True)])
        with patch.object(module, "current_process_io") as io_factory, patch.object(
            module, "native_adapters"
        ) as native_factory:
            trial = module.CompanionMenuSubmenuTrial()
        self.assertTrue(trial._abc_initialised)
        self.assertTrue(trial._stopped)
        self.assertEqual(len(trial.hooks), 4)
        self.assertEqual(trial._gui_widgets, [])
        self.assertEqual(trial._hotkey_funcs, [])
        io_factory.assert_not_called()
        native_factory.assert_not_called()
        module.ensure_guard.assert_not_called()

    def test_exact_supported_context_is_required_before_initialization(self):
        for change in ({"injected": False}, {"base": 0}, {"framework": "0.2.3"},
                       {"digest": "another-build"}):
            with self.subTest(change=change):
                module = load_trial(enabled=True, **change)
                self.assertTrue(module.CompanionMenuSubmenuTrial._disabled)
                module.ensure_guard.assert_not_called()

    def test_hook_metadata_retains_three_exact_abis_and_four_callbacks(self):
        module = load_trial(enabled=True)
        self.assertFalse(module.CompanionMenuSubmenuTrial._disabled)
        expected = {
            0x151ED00: [ctypes.c_void_p, ctypes.c_void_p, None],
            0x1523220: [ctypes.c_void_p, ctypes.c_void_p, None],
            0x1526940: [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool, ctypes.c_bool],
        }
        actual = {declaration.offset: list(declaration.function.__annotations__.values())
                  for declaration in module.test_declarations}
        self.assertEqual(actual, expected)
        for name, phase in (("after_builder", "after"), ("after_label", "after"),
                            ("before_trigger", "before"), ("after_trigger", "after")):
            self.assertEqual(getattr(module.CompanionMenuSubmenuTrial, name)._test_hook_time, phase)
        module.ensure_guard.assert_not_called()

    def test_guard_is_installed_before_instance_becomes_active(self):
        module = load_trial(enabled=True)
        order, guard = [], Mock()
        with patch.object(module, "current_process_io", side_effect=lambda: (
            order.append("io") or Mock(), Mock(), Mock()
        )), patch.object(module, "native_adapters", side_effect=lambda base: (
            order.append("adapters") or Mock(), Mock(), Mock()
        )), patch.object(module, "ensure_guard", side_effect=lambda *args: (
            order.append("guard") or guard
        )):
            trial = module.CompanionMenuSubmenuTrial()
        self.assertEqual(order, ["io", "adapters", "guard"])
        self.assertIs(trial._guard, guard)
        self.assertFalse(trial._stopped)

    def test_guard_failure_leaves_all_callbacks_inert(self):
        module = load_trial(enabled=True)
        with patch.object(module, "current_process_io", return_value=(Mock(), Mock(), Mock())), patch.object(
            module, "native_adapters", return_value=(Mock(), Mock(), Mock())
        ), patch.object(module, "ensure_guard", side_effect=module.GuardError("integrity_mismatch")):
            trial = module.CompanionMenuSubmenuTrial()
        self.assertTrue(trial._stopped)
        self.assertIsNone(trial.before_trigger(0x10000, 0x20000, True))
        self.assertIsNone(trial.after_trigger(0x10000, 0x20000, True, False))
        self.assertIsNone(trial.after_builder(0x10000, 0x20000))
        self.assertIsNone(trial.after_label(0x10000, 0x20000))


class TrialFixture(ItemFixture):
    def setUp(self):
        super().setUp()
        self.module = load_trial()
        self.trial = self.module.CompanionMenuSubmenuTrial()
        self.trial._stopped = False
        self.trial._reader = self.reader
        self.trial._writer = Mock()
        self.trial._write_field = Mock(side_effect=self.write_field)
        self.trial._constructor = self.constructor
        self.trial._append = self.append_callback
        self.trial._select_first = Mock(side_effect=self.select_first)
        self.trial._guard = self.guard
        self.output = 0x8880000
        self.regions[self.menu][self.module.PENDING_SELECTION_OFFSET] = 0

    def append(self, header_address, data):
        self.events.append("append")
        depth = (header_address - self.menu - ITEM.VECTORS_OFFSET) // ITEM.VECTOR_SIZE
        self.assertIn(depth, (1, 2))
        self.assertEqual(header_address, self.menu + ITEM.VECTORS_OFFSET + depth * ITEM.VECTOR_SIZE)
        self.assertIs(type(data), bytes)
        self.assertEqual(len(data), ITEM.ITEM_SIZE)
        offset = ITEM.VECTORS_OFFSET + depth * ITEM.VECTOR_SIZE
        header = self.regions[self.menu][offset:offset + 16]
        capacity = int.from_bytes(header[:4], "little")
        count = int.from_bytes(header[4:8], "little")
        pointer = int.from_bytes(header[8:], "little")
        old = bytes(self.regions[pointer][:count * ITEM.ITEM_SIZE])
        destination = pointer if count < capacity else 0x6660000 + depth * 0x10000
        self.regions[destination] = bytearray(old + data)
        self.regions[self.menu][offset:offset + 16] = (
            max(capacity, count + 1).to_bytes(4, "little")
            + (count + 1).to_bytes(4, "little") + destination.to_bytes(8, "little"))

    def write_field(self, menu, offset, value):
        self.assertEqual(menu, self.menu)
        self.events.append(("field", offset, value))
        if offset == ITEM.DEPTH_OFFSET:
            self.set_integer(offset, value, signed=True)
        elif offset == self.module.PENDING_SELECTION_OFFSET:
            self.regions[self.menu][offset] = value
        else:
            raise AssertionError("Unexpected transition field")

    def select_first(self, menu):
        self.assertEqual(menu, self.menu)
        self.events.append("select")
        self.set_integer(ITEM.SELECTIONS_OFFSET + 8, 0)

    def builder(self):
        return self.trial.after_builder(self.menu, 0x9990000)

    def label(self):
        return self.trial.after_label(self.menu, self.output)

    def vector(self, depth):
        offset = ITEM.VECTORS_OFFSET + depth * ITEM.VECTOR_SIZE
        header = self.regions[self.menu][offset:offset + 16]
        return int.from_bytes(header[8:], "little"), int.from_bytes(header[4:8], "little")

    def prepare_parent(self):
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 2)
        self.assertIsNone(self.builder())
        self.assertFalse(self.trial._stopped)
        pointer, count = self.vector(1)
        self.assertEqual(count, 3)
        self.assertEqual(self.vector(2)[1], 1)
        self.parent = pointer + 2 * ITEM.ITEM_SIZE
        return self.parent

    def before(self, action=None, called=True):
        return self.trial.before_trigger(self.menu, self.parent if action is None else action, called)

    def after(self, result=False, action=None, called=True, menu=None):
        return self.trial.after_trigger(self.menu if menu is None else menu,
                                        self.parent if action is None else action, called, result)

    def assert_no_transition(self):
        self.trial._write_field.assert_not_called()
        self.trial._select_first.assert_not_called()

    def assert_guard_retained(self):
        self.assertIs(self.trial._guard, self.guard)
        self.guard.disable.assert_not_called()
        self.guard.close.assert_not_called()
        self.guard.remove.assert_not_called()
        self.assertFalse(self.trial._lock.locked())


class CallbackTests(TrialFixture):
    def test_selected_parent_prebuilds_one_child_and_repeated_builder_is_idempotent(self):
        self.prepare_parent()
        self.assertEqual(self.append_callback.call_count, 2)
        self.assertIsNone(self.builder())
        self.assertEqual(self.append_callback.call_count, 2)
        self.assert_no_transition()

    def test_correlated_false_activation_opens_child_without_deferred_flag_writes(self):
        self.prepare_parent()
        self.assertIsNone(self.before())
        self.assertIsNotNone(self.trial._pending[4])
        self.assert_no_transition()
        self.assertIsNone(self.after(False))
        self.trial._write_field.assert_called_once_with(self.menu, ITEM.DEPTH_OFFSET, 2)
        self.trial._select_first.assert_called_once_with(self.menu)
        self.assertEqual(self.reader(self.menu + ITEM.DEPTH_OFFSET, 4), b"\x02\0\0\0")
        self.assertEqual(self.reader(self.menu + self.module.PENDING_SELECTION_OFFSET, 1), b"\0")
        self.assertIsNone(self.trial._pending)
        self.assertFalse(self.trial._stopped)
        self.assert_guard_retained()

    def test_selected_labels_distinguish_parent_and_inert_child(self):
        self.prepare_parent()
        self.assertIsNone(self.label())
        self.trial._writer.assert_called_once_with(self.output, b"Companion Auto Summon")
        self.before()
        self.after(False)
        self.trial._writer.reset_mock()
        self.assertIsNone(self.label())
        self.trial._writer.assert_called_once_with(self.output, b"Settings preview")

    def test_child_activation_never_changes_depth_or_selection(self):
        self.prepare_parent()
        self.set_integer(ITEM.DEPTH_OFFSET, 2)
        self.set_integer(ITEM.SELECTIONS_OFFSET + 8, 0)
        child = self.vector(2)[0]
        self.assertIsNone(self.before(child))
        self.assertIsNone(self.trial._pending[4])
        self.reads.clear()
        self.assertIsNone(self.after(False, action=child))
        self.assertEqual(self.reads, [])
        self.assert_no_transition()
        self.assertFalse(self.trial._stopped)

    def test_native_true_for_tagged_none_stops_but_does_not_override_result(self):
        self.prepare_parent()
        self.before()
        self.assertIsNone(self.after(True))
        self.assertTrue(self.trial._stopped)
        self.assertIsNone(self.trial._pending)
        self.assert_no_transition()
        self.assert_guard_retained()

    def test_vanilla_original_results_survive_without_any_after_reads(self):
        for result in (False, True):
            with self.subTest(result=result):
                self.setUp()
                action = self.child_data
                self.assertIsNone(self.before(action))
                self.assertIsNone(self.trial._pending[4])
                self.trial._reader = Mock(side_effect=AssertionError("Vanilla AFTER read is forbidden"))
                self.assertIsNone(self.after(result, action=action))
                self.trial._reader.assert_not_called()
                self.assertFalse(self.trial._stopped)
                self.assertIsNone(self.trial._pending)
                self.assert_no_transition()

    def test_untagged_none_never_captures_custom_candidate(self):
        self.tag(0, marker=bytes(16))
        self.assertIsNone(self.before(self.child_data))
        self.assertIsNone(self.trial._pending[4])
        self.reads.clear()
        self.assertIsNone(self.after(False, action=self.child_data))
        self.assertEqual(self.reads, [])
        self.assert_no_transition()

    def test_after_uses_fresh_menu_storage_and_never_dereferences_old_action_argument(self):
        self.prepare_parent()
        self.before()
        pointer, _ = self.vector(1)
        replacement = 0x7770000
        self.regions[replacement] = self.regions.pop(pointer)
        offset = ITEM.VECTORS_OFFSET + ITEM.VECTOR_SIZE + 8
        self.regions[self.menu][offset:offset + 8] = replacement.to_bytes(8, "little")
        self.reads.clear()
        self.assertIsNone(self.after(False))
        self.assertFalse(self.trial._stopped)
        self.assertFalse(any(pointer <= address < pointer + 3 * ITEM.ITEM_SIZE
                             for address, size in self.reads))
        self.trial._select_first.assert_called_once_with(self.menu)

    def test_pending_native_selection_prevents_transition_without_clearing_it(self):
        for value in (1, 2, 255):
            with self.subTest(value=value):
                self.setUp()
                self.prepare_parent()
                self.before()
                self.regions[self.menu][self.module.PENDING_SELECTION_OFFSET] = value
                self.assertIsNone(self.after(False))
                self.assertTrue(self.trial._stopped)
                self.assert_no_transition()
                self.assertEqual(self.reader(self.menu + self.module.PENDING_SELECTION_OFFSET, 1),
                                 bytes((value,)))
                self.assert_guard_retained()

    def test_builder_does_not_consume_an_existing_native_pending_flag(self):
        self.prepare_parent()
        self.set_integer(ITEM.DEPTH_OFFSET, 2)
        self.regions[self.menu][self.module.PENDING_SELECTION_OFFSET] = 1
        self.assertIsNone(self.builder())
        self.assertEqual(self.reader(self.menu + self.module.PENDING_SELECTION_OFFSET, 1), b"\1")
        self.assert_no_transition()

    def test_missing_or_mismatched_after_pair_stops_without_mutation(self):
        for mismatch in ("missing", "menu", "action", "flag", "thread"):
            with self.subTest(mismatch=mismatch):
                self.setUp()
                self.prepare_parent()
                if mismatch != "missing":
                    self.before()
                arguments = {}
                if mismatch == "menu":
                    arguments["menu"] = self.menu + 16
                elif mismatch == "action":
                    arguments["action"] = self.parent + ITEM.ITEM_SIZE
                elif mismatch == "flag":
                    arguments["called"] = False
                elif mismatch == "thread":
                    self.module.get_native_id.return_value += 1
                self.assertIsNone(self.after(False, **arguments))
                self.assertTrue(self.trial._stopped)
                self.assertIsNone(self.trial._pending)
                self.assert_no_transition()
                self.assert_guard_retained()

    def test_nested_trigger_inside_either_custom_or_vanilla_call_stops(self):
        for outer_custom in (False, True):
            with self.subTest(outer_custom=outer_custom):
                self.setUp()
                self.prepare_parent()
                self.before(self.parent if outer_custom else self.vector(1)[0])
                self.assertIsNone(self.before())
                self.assertTrue(self.trial._stopped)
                self.assertIsNone(self.trial._pending)
                self.assertIsNone(self.after(False))
                self.assert_no_transition()
                self.assert_guard_retained()

    def test_overlapping_callback_stops_without_releasing_another_invocation_lock(self):
        self.prepare_parent()
        self.before()
        self.trial._lock.acquire()
        try:
            self.assertIsNone(self.after(False))
            self.assertTrue(self.trial._lock.locked())
            self.assertTrue(self.trial._stopped)
            self.assertIsNone(self.trial._pending)
            self.assert_no_transition()
        finally:
            self.trial._lock.release()
        self.assert_guard_retained()

    def test_ordinary_callback_inside_custom_call_stops_and_cannot_complete_later(self):
        for callback in ("builder", "label"):
            with self.subTest(callback=callback):
                self.setUp()
                self.prepare_parent()
                self.before()
                self.assertIsNone(getattr(self, callback)())
                self.assertTrue(self.trial._stopped)
                self.assertIsNone(self.after(False))
                self.assertIsNone(self.trial._pending)
                self.assert_no_transition()

    def test_ordinary_native_rebuild_during_vanilla_call_is_allowed(self):
        self.prepare_parent()
        vanilla = self.vector(1)[0]
        self.before(vanilla)
        pending = self.trial._pending
        self.assertIsNone(self.builder())
        self.assertIs(self.trial._pending, pending)
        self.assertFalse(self.trial._stopped)
        self.assertIsNone(self.after(False, action=vanilla))
        self.assert_no_transition()

    def test_changed_selection_after_original_prevents_transition(self):
        self.prepare_parent()
        self.before()
        self.set_integer(ITEM.SELECTIONS_OFFSET + 4, 0)
        self.assertIsNone(self.after(False))
        self.assertTrue(self.trial._stopped)
        self.assert_no_transition()
        self.assert_guard_retained()

    def test_revoked_guard_after_original_prevents_transition(self):
        self.prepare_parent()
        self.before()
        self.guard.authorize_append.side_effect = lambda menu: False
        self.assertIsNone(self.after(False))
        self.assertTrue(self.trial._stopped)
        self.assert_no_transition()
        self.assert_guard_retained()

    def test_revocation_during_last_pending_read_prevents_scalar_write(self):
        self.prepare_parent()
        self.before()
        def reader(address, size):
            value = self.reader(address, size)
            if address == self.menu + self.module.PENDING_SELECTION_OFFSET:
                self.guard.authorize_append.side_effect = lambda menu: False
            return value
        self.trial._reader = reader
        self.assertIsNone(self.after(False))
        self.assertTrue(self.trial._stopped)
        self.assert_no_transition()

    def test_failed_depth_readback_stops_before_native_selection(self):
        self.prepare_parent()
        self.before()
        self.trial._write_field.side_effect = None
        self.assertIsNone(self.after(False))
        self.assertTrue(self.trial._stopped)
        self.trial._write_field.assert_called_once_with(self.menu, ITEM.DEPTH_OFFSET, 2)
        self.trial._select_first.assert_not_called()
        self.assert_guard_retained()

    def test_selection_failure_keeps_existing_inert_child_and_guard_without_rollback(self):
        self.prepare_parent()
        self.before()
        self.trial._select_first.side_effect = OSError("synthetic selector failure")
        self.assertIsNone(self.after(False))
        self.assertTrue(self.trial._stopped)
        self.assertEqual(self.vector(2)[1], 1)
        self.assertEqual(self.reader(self.menu + ITEM.DEPTH_OFFSET, 4), b"\x02\0\0\0")
        self.trial._write_field.assert_called_once_with(self.menu, ITEM.DEPTH_OFFSET, 2)
        self.assertIsNone(self.builder())
        self.assertIsNone(self.before())
        self.assertIsNone(self.after(False))
        self.trial._select_first.assert_called_once()
        self.assert_guard_retained()

    def test_partial_depth_write_error_stops_without_rollback_or_selection(self):
        self.prepare_parent()
        self.before()
        def failed_write(menu, offset, value):
            self.write_field(menu, offset, value)
            raise OSError("synthetic failure after scalar write")
        self.trial._write_field.side_effect = failed_write
        self.assertIsNone(self.after(False))
        self.assertTrue(self.trial._stopped)
        self.assertEqual(self.reader(self.menu + ITEM.DEPTH_OFFSET, 4), b"\x02\0\0\0")
        self.assertEqual(self.vector(2)[1], 1)
        self.trial._write_field.assert_called_once()
        self.trial._select_first.assert_not_called()
        self.assert_guard_retained()

    def test_invalid_native_selection_readback_stops_and_preserves_guard(self):
        self.prepare_parent()
        self.before()
        self.trial._select_first.side_effect = None
        self.assertIsNone(self.after(False))
        self.assertTrue(self.trial._stopped)
        self.assert_guard_retained()

    def test_stopped_trial_never_calls_any_native_mutator_again(self):
        self.prepare_parent()
        self.trial._stop("synthetic stop")
        self.constructor.reset_mock()
        self.append_callback.reset_mock()
        self.assertIsNone(self.builder())
        self.assertIsNone(self.label())
        self.assertIsNone(self.before())
        self.assertIsNone(self.after(False))
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()
        self.trial._writer.assert_not_called()
        self.assert_no_transition()
        self.assert_guard_retained()

    def test_warning_logger_and_thread_provider_errors_never_escape_callbacks(self):
        self.module.get_native_id.side_effect = RuntimeError("synthetic thread error")
        self.module.LOGGER.warning.side_effect = RuntimeError("synthetic logger error")
        self.assertIsNone(self.before(self.child_data))
        self.assertTrue(self.trial._stopped)
        self.assertIsNone(self.trial._pending)
        self.assert_no_transition()
        self.assert_guard_retained()


class OwnedAdapterTests(unittest.TestCase):
    def test_native_selector_and_construction_use_exact_abis_and_owned_alignment(self):
        module, declarations, calls = load_trial(), [], []
        base = 0x100000

        def bind(result, *arguments):
            declarations.append((result, arguments))
            def locate(target):
                if target == base + module.ITEM_CONSTRUCTOR_RVA:
                    def constructor(address, icon, action, disabled, background):
                        self.assertEqual(address % 16, 0)
                        ctypes.memmove(address, b"x" * 224, 224)
                        calls.append(("constructor", icon, action, disabled, background))
                        return address
                    return constructor
                if target == base + module.ITEM_APPEND_RVA:
                    def append(header, address):
                        self.assertEqual(address % 16, 0)
                        calls.append(("append", header, ctypes.string_at(address, 224)))
                        return 0x7770000
                    return append
                self.assertEqual(target, base + module.SELECT_ITEM_RVA)
                return lambda table, depth, index: calls.append(("select", table, depth, index))
            return locate

        with patch.object(module.C, "WINFUNCTYPE", side_effect=bind, create=True):
            constructor, append, select = module.native_adapters(base)
        owned = bytearray(224)
        constructor(owned, 7, 0, False, True)
        append(0x2220000, bytes(owned))
        select(0x1110000)
        self.assertEqual(declarations, [
            (ctypes.c_void_p, (ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int32,
                              ctypes.c_bool, ctypes.c_bool)),
            (ctypes.c_void_p, (ctypes.c_void_p, ctypes.c_void_p)),
            (None, (ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32)),
        ])
        self.assertEqual(calls, [("constructor", 7, 0, False, True),
                                 ("append", 0x2220000, b"x" * 224),
                                 ("select", 0x1110000 + ITEM.DEPTH_OFFSET, 2, 0)])

    def io(self):
        module = load_trial()
        kernel = types.SimpleNamespace(GetCurrentProcess=Mock(return_value=-1),
                                       ReadProcessMemory=Mock(), WriteProcessMemory=Mock())
        writes = []
        def read(handle, address, buffer, size, transferred):
            ctypes.memmove(buffer, b"q" * size, size)
            ctypes.cast(transferred, ctypes.POINTER(ctypes.c_size_t)).contents.value = size
            return 1
        def write(handle, address, buffer, size, transferred):
            writes.append((address, ctypes.string_at(buffer, size)))
            ctypes.cast(transferred, ctypes.POINTER(ctypes.c_size_t)).contents.value = size
            return 1
        kernel.ReadProcessMemory.side_effect, kernel.WriteProcessMemory.side_effect = read, write
        with patch.object(module.C, "WinDLL", return_value=kernel, create=True):
            callbacks = module.current_process_io()
        return module, kernel, writes, callbacks

    def test_io_limits_scalar_writes_to_exact_transition_fields(self):
        module, kernel, writes, (reader, label, field) = self.io()
        menu = 0x1110000
        self.assertEqual(reader(menu, 1), b"q")
        field(menu, ITEM.DEPTH_OFFSET, 2)
        self.assertEqual(writes, [(menu + ITEM.DEPTH_OFFSET, b"\x02\0\0\0")])
        for offset, value in ((ITEM.DEPTH_OFFSET, 1), (ITEM.DEPTH_OFFSET, True),
                              (module.PENDING_SELECTION_OFFSET, 0),
                              (module.PENDING_SELECTION_OFFSET, 1),
                              (module.PENDING_SELECTION_OFFSET, 2),
                              (module.PENDING_SELECTION_OFFSET, False),
                              (ITEM.VECTORS_OFFSET, 0), (ITEM.SELECTIONS_OFFSET + 8, 0)):
            with self.subTest(offset=offset, value=value), self.assertRaises(ValueError):
                field(menu, offset, value)
        self.assertEqual(len(writes), 1)
        for size in (0, 2, 128, 224):
            with self.subTest(size=size), self.assertRaises(ValueError):
                reader(menu, size)

    def test_partial_field_write_is_reported_and_label_remains_bounded(self):
        module, kernel, writes, (reader, label, field) = self.io()
        label(0x9990000, b"Settings preview")
        self.assertEqual(writes, [(0x9990000, b"Settings preview" + bytes(112))])
        kernel.WriteProcessMemory.side_effect = lambda *args: 1
        with self.assertRaises(OSError):
            field(0x1110000, ITEM.DEPTH_OFFSET, 2)
        for value in (b"", b"x" * 128, b"a\0b", "text"):
            with self.subTest(value_type=type(value).__name__), self.assertRaises(ValueError):
                label(0x9990000, value)


if __name__ == "__main__":
    unittest.main()
