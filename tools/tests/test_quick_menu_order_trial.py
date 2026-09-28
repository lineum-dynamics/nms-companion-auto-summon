"""Ordered-menu adapter tests with fake hooks and owned synthetic memory only."""

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
from test_quick_menu_submenu_trial import TrialFixture as SubmenuFixture


SOURCE = Path(__file__).resolve().parents[1] / "quick_menu_order_trial.py"
EXPECTED_HASH = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"


def load_trial(*, enabled=False, settings_enabled=False, extended_settings=False, custom_icon=False,
               language_observation=False,
               injected=True, base=0x100000,
               framework="0.2.4", digest=EXPECTED_HASH):
    source = SOURCE.read_text(encoding="utf-8")
    if enabled:
        if source.count("TRIAL_ENABLED = False") != 1:
            raise AssertionError("Expected one disabled trial marker")
        source = source.replace("TRIAL_ENABLED = False", "TRIAL_ENABLED = True", 1)
    if settings_enabled:
        if source.count("SETTINGS_TOGGLE_ENABLED = False") != 1:
            raise AssertionError("Expected one disabled settings marker")
        source = source.replace("SETTINGS_TOGGLE_ENABLED = False", "SETTINGS_TOGGLE_ENABLED = True", 1)
    if extended_settings:
        source = source.replace("EXTENDED_SETTINGS_ENABLED = False", "EXTENDED_SETTINGS_ENABLED = True", 1)
    if custom_icon:
        source = source.replace("CUSTOM_ICON_ENABLED = False", "CUSTOM_ICON_ENABLED = True", 1)
    if language_observation:
        source = source.replace("LANGUAGE_OBSERVATION_ENABLED = False", "LANGUAGE_OBSERVATION_ENABLED = True", 1)
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
            raise AssertionError("Offline tests must not call a game wrapper")

    internal = types.ModuleType("pymhf.core._internal")
    internal.IS_INJECTED, internal.BASE_ADDRESS = injected, base
    internal.BINARY_PATH = "synthetic-order-trial.exe"
    pymhf = types.ModuleType("pymhf")
    pymhf.__path__, pymhf.Mod = [], FakeMod
    core = types.ModuleType("pymhf.core")
    core.__path__, core._internal = [], internal
    hooking = types.ModuleType("pymhf.core.hooking")
    hooking.static_function_hook = lambda *, offset: lambda function: FakeNative(function, offset)
    hooking.hook_manager = types.SimpleNamespace(_get_funchook=Mock(return_value=None))
    mod_loader = types.ModuleType("pymhf.core.mod_loader")
    mod_loader.mod_manager = types.SimpleNamespace(mods={})
    core.hooking, pymhf.core = hooking, core
    runtime = types.ModuleType("quick_menu_guard_runtime")
    runtime.GuardError = type("GuardError", (RuntimeError,), {})
    runtime.ensure_guard = Mock(side_effect=AssertionError("Import must not install native hooks"))

    helpers = {"quick_menu_item": ITEM}
    helper_names = ["quick_menu_submenu", "quick_menu_order"]
    if settings_enabled:
        helper_names.extend(("quick_menu_toggle", "quick_menu_preferences"))
    if custom_icon:
        helper_names.append("quick_menu_icon")
    if language_observation:
        helper_names.append("game_language")
    for name in helper_names:
        spec = importlib.util.spec_from_file_location(name + "_order_test", SOURCE.with_name(name + ".py"))
        helper = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {**helpers, spec.name: helper}):
            spec.loader.exec_module(helper)
        helpers[name] = helper

    def fake_version(name):
        events.append(("version", name))
        return framework

    def fake_open(path, mode="r", *args, **kwargs):
        if str(path) != internal.BINARY_PATH or mode != "rb":
            raise AssertionError("Unexpected file access")
        events.append(("binary",))
        return io.BytesIO(b"owned synthetic executable")

    module = types.ModuleType("quick_menu_order_trial_under_test")
    module.__file__ = str(SOURCE)
    with patch.dict(sys.modules, {
        **helpers, "quick_menu_guard_runtime": runtime, "pymhf": pymhf,
        "pymhf.core": core, "pymhf.core._internal": internal,
        "pymhf.core.hooking": hooking,
        "pymhf.core.mod_loader": mod_loader,
    }), patch("importlib.metadata.version", side_effect=fake_version), patch.object(
        Path, "open", fake_open
    ), patch.object(hashlib, "file_digest", return_value=Mock(hexdigest=lambda: digest)), patch.object(
        ctypes, "WinDLL", side_effect=AssertionError("No Windows APIs on import"), create=True
    ), patch.object(
        ctypes, "WINFUNCTYPE", side_effect=AssertionError("No native bindings on import"), create=True
    ):
        exec(compile(source, str(SOURCE), "exec"), module.__dict__)
    module.test_events, module.test_declarations = events, declarations
    module.test_helpers = helpers
    module.LOGGER = Mock()
    module.get_native_id = Mock(return_value=271828)
    return module


class GuardAndMetadataTests(unittest.TestCase):
    def test_disabled_import_and_instance_have_no_io_or_native_initialization(self):
        module = load_trial()
        self.assertEqual(module.test_events, [("class", True)])
        with patch.object(module, "current_process_io") as io_factory, patch.object(
            module, "native_adapters"
        ) as native_factory:
            trial = module.CompanionMenuOrderTrial()
        self.assertTrue(trial._abc_initialised)
        self.assertTrue(trial._stopped)
        self.assertEqual(len(trial.hooks), 6)
        self.assertEqual(trial._gui_widgets, [])
        self.assertEqual(trial._hotkey_funcs, [])
        io_factory.assert_not_called()
        native_factory.assert_not_called()
        module.ensure_guard.assert_not_called()
        module.hook_manager._get_funchook.assert_not_called()

    def test_unsupported_context_is_inactive_before_native_initialization(self):
        for change in ({"injected": False}, {"base": 0}, {"framework": "0.2.3"},
                       {"digest": "another-build"}):
            with self.subTest(change=change):
                module = load_trial(enabled=True, **change)
                self.assertTrue(module.CompanionMenuOrderTrial._disabled)
                module.ensure_guard.assert_not_called()

    def test_four_exact_abis_and_six_callback_phases(self):
        module = load_trial(enabled=True)
        actual = {entry.offset: list(entry.function.__annotations__.values())
                  for entry in module.test_declarations}
        self.assertEqual(actual, {
            0x151ED00: [ctypes.c_void_p, ctypes.c_void_p, None],
            0x1523220: [ctypes.c_void_p, ctypes.c_void_p, None],
            0x1526940: [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool, ctypes.c_bool],
            0x1533980: [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p],
        })
        for name, phase in (("before_builder", "before"), ("after_builder", "after"),
                            ("before_append", "before"), ("after_label", "after"),
                            ("before_trigger", "before"), ("after_trigger", "after")):
            self.assertEqual(getattr(module.CompanionMenuOrderTrial, name)._test_hook_time, phase)

    def test_guard_is_ready_before_callbacks_and_trampoline_resolution_is_lazy(self):
        module = load_trial(enabled=True)
        events, guard = [], Mock()
        with patch.object(module, "current_process_io", side_effect=lambda: (
            events.append("io") or Mock(), Mock(), Mock()
        )), patch.object(module, "native_adapters", side_effect=lambda base, resolver: (
            events.append("adapters") or Mock(), Mock(), Mock()
        )), patch.object(module, "ensure_guard", side_effect=lambda *args: (
            events.append("guard") or guard
        )):
            trial = module.CompanionMenuOrderTrial()
        self.assertEqual(events, ["io", "adapters", "guard"])
        self.assertIs(trial._guard, guard)
        self.assertFalse(trial._stopped)
        module.hook_manager._get_funchook.assert_not_called()


class OrderFixture(SubmenuFixture):
    settings_enabled = False

    def setUp(self):
        ItemFixture.setUp(self)
        self.module = load_trial(settings_enabled=self.settings_enabled,
                                 extended_settings=getattr(self, "extended_settings", False),
                                 custom_icon=getattr(self, "custom_icon", False))
        self.trial = self.module.CompanionMenuOrderTrial()
        self.trial._stopped = False
        self.trial._reader = self.reader
        self.trial._writer = Mock()
        self.trial._write_field = Mock(side_effect=self.write_field)
        self.trial._constructor = self.constructor
        self.trial._select_first = Mock(side_effect=self.select_first)
        self.trial._guard = self.guard
        self.output, self.render = 0x8880000, 0x9990000
        self.regions[self.menu][self.module.PENDING_SELECTION_OFFSET] = 0
        self.set_vector(1, self.child_data, [], selected=0)
        self.native_calls, self.native_errors = [], []
        self.fail_custom_append = False
        self.original = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(
            self.native_original)
        self.hook = types.SimpleNamespace(
            target=0x100000 + self.module.ITEM_APPEND_RVA, state="enabled", _has_noop=False,
            _before_detours=[self.trial.before_append], _after_detours=[],
            _after_detours_with_results=[],
            _func_def=types.SimpleNamespace(restype=ctypes.c_void_p,
                                           argtypes=[ctypes.c_void_p, ctypes.c_void_p]),
            original=self.original,
        )
        self.module.hook_manager._get_funchook.return_value = self.hook
        self.bindings = []

        def fake_bind(restype, *argtypes):
            def at(address):
                self.bindings.append(address)
                if address == self.hook.target:
                    raise AssertionError("Patched native append entry must never be bound")
                return Mock(side_effect=AssertionError("Constructor/selector are injected separately"))
            return at

        with patch.object(self.module.C, "WINFUNCTYPE", side_effect=fake_bind, create=True):
            _, self.trial._append, _ = self.module.native_adapters(
                0x100000, self.trial._resolve_append_original)
        self.owners = []

    def incoming(self, action=46):
        data = bytearray(b"\x73" * ITEM.ITEM_SIZE)
        data[ITEM.ACTION_OFFSET:ITEM.ACTION_OFFSET + 4] = action.to_bytes(4, "little")
        data[ITEM.MARKER_OFFSET:ITEM.MARKER_OFFSET + 16] = bytes(16)
        owner = ctypes.create_string_buffer(bytes(data), ITEM.ITEM_SIZE)
        self.owners.append(owner)
        address = ctypes.addressof(owner)
        self.regions[address] = data
        return address

    def native_original(self, header, incoming):
        # Only pointers to owned ctypes buffers reach this synthetic native
        # callback. Vector/header identities are passed to the fake byte model.
        try:
            data = ctypes.string_at(incoming, ITEM.ITEM_SIZE)
            self.native_calls.append((header, incoming, data))
            if self.fail_custom_append and data[ITEM.MARKER_OFFSET:ITEM.MARKER_OFFSET + 16] == ITEM.CUSTOM_ACTION_MARKER:
                return 0
            self.append(header, data)
            return 0x7770000
        except Exception as error:
            self.native_errors.append(error)
            return 0

    def begin(self):
        return self.trial.before_builder(self.menu, self.render)

    def finish(self):
        return self.trial.after_builder(self.menu, self.render)

    def builder(self):
        self.begin()
        return self.finish()

    def native_pet_append(self, incoming):
        header = self.menu + ITEM.VECTORS_OFFSET + ITEM.VECTOR_SIZE
        result = self.trial.before_append(header, incoming)
        self.assertIsNone(result)
        # Simulate pyMHF's one unchanged original invocation after BEFORE.
        return self.original(header, incoming)

    def prepare_parent(self):
        self.assertIsNone(self.begin())
        self.assertEqual(self.native_pet_append(self.incoming()), 0x7770000)
        self.assertIsNone(self.finish())
        self.assertFalse(self.trial._stopped)
        self.assertEqual(self.native_errors, [])
        self.assertEqual(self.vector(1)[1], 2)
        self.assertEqual(self.vector(2)[1], 1)
        self.parent = self.vector(1)[0]
        return self.parent


class TrampolineTests(OrderFixture):
    def test_resolver_returns_actual_owned_original_and_keeps_identity(self):
        self.assertIs(self.trial._resolve_append_original(), self.original)
        self.assertIs(self.trial._resolve_append_original(), self.original)
        self.assertEqual(self.native_calls, [])
        self.module.hook_manager._get_funchook.assert_called_with(self.trial.before_append)

    def test_missing_disabled_foreign_or_modified_hook_refuses_before_mutation(self):
        cases = (("missing", None), ("state", "disabled"), ("target", 12),
                 ("_has_noop", True), ("_before_detours", []),
                 ("_before_detours", ["another mod"]), ("_after_detours", [Mock()]),
                 ("_after_detours_with_results", [Mock()]))
        for field, value in cases:
            with self.subTest(field=field, value_type=type(value).__name__):
                self.setUp()
                if field == "missing":
                    self.module.hook_manager._get_funchook.return_value = None
                else:
                    setattr(self.hook, field, value)
                self.assertIsNone(self.begin())
                self.assertTrue(self.trial._stopped)
                self.assertIsNone(self.trial._building)
                self.assertEqual(self.native_calls, [])
                self.constructor.assert_not_called()
                self.assert_guard_retained()

    def test_abi_and_patched_entry_as_original_are_rejected_without_calling_them(self):
        for mutation in ("definition", "original_abi", "patched_entry", "absent"):
            with self.subTest(mutation=mutation):
                self.setUp()
                if mutation == "definition":
                    self.hook._func_def.restype = ctypes.c_bool
                elif mutation == "original_abi":
                    self.hook.original = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p)(lambda value: False)
                elif mutation == "patched_entry":
                    self.hook.original = ctypes.CFUNCTYPE(
                        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(self.hook.target)
                else:
                    self.hook.original = None
                self.assertIsNone(self.begin())
                self.assertTrue(self.trial._stopped)
                self.assertEqual(self.native_calls, [])

    def test_hook_or_original_replacement_after_first_resolution_stops(self):
        for replacement in ("hook", "original", "lookup_race"):
            with self.subTest(replacement=replacement):
                self.setUp()
                self.trial._resolve_append_original()
                if replacement == "hook":
                    self.module.hook_manager._get_funchook.return_value = types.SimpleNamespace(**vars(self.hook))
                elif replacement == "original":
                    self.hook.original = ctypes.CFUNCTYPE(
                        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(lambda *args: 1)
                else:
                    self.module.hook_manager._get_funchook.side_effect = [self.hook, None]
                self.assertIsNone(self.begin())
                self.assertTrue(self.trial._stopped)
                self.assertIsNone(self.trial._building)
                self.assertEqual(self.native_calls, [])

    def test_every_mod_append_revalidates_hook_before_using_native_original(self):
        self.begin()
        def construct_then_disable(*args):
            self.construct(*args)
            self.hook.state = "disabled"
        self.constructor.side_effect = construct_then_disable
        incoming = self.incoming()
        self.native_pet_append(incoming)
        self.assertTrue(self.trial._stopped)
        self.assertEqual([call[1] for call in self.native_calls], [incoming])
        self.assert_guard_retained()


class OrderingCallbackTests(OrderFixture):
    def test_custom_parent_precedes_untouched_native_pet_and_original_runs_once(self):
        incoming = self.incoming()
        initial_source = bytes(self.regions[incoming])
        original_root = bytes(self.regions[self.root_data])
        self.assertIsNone(self.begin())
        self.assertEqual(self.native_pet_append(incoming), 0x7770000)
        self.assertEqual(len(self.native_calls), 2)
        custom, original = self.native_calls
        self.assertNotEqual(custom[1], incoming)
        self.assertEqual(custom[2][ITEM.MARKER_OFFSET:ITEM.MARKER_OFFSET + 16], ITEM.CUSTOM_ACTION_MARKER)
        self.assertEqual(original[1:], (incoming, initial_source))
        self.assertEqual(bytes(self.regions[incoming]), initial_source)
        self.assertEqual(bytes(self.regions[self.root_data]), original_root)
        self.assertIsNone(self.finish())
        self.assertEqual(len(self.native_calls), 3)  # The selected parent prepares one child.
        self.assertEqual(self.native_calls[2][2][ITEM.SLOT_OFFSET:ITEM.SLOT_OFFSET + 4], bytes(4))
        self.assertIsNone(self.trial._building)
        self.assertFalse(self.trial._stopped)
        self.assertEqual(self.native_errors, [])
        self.assert_no_transition()

    def test_later_pets_and_repeated_build_do_not_duplicate_parent(self):
        self.prepare_parent()
        self.assertIsNone(self.begin())
        incoming = self.incoming(47)
        before = len(self.native_calls)
        self.native_pet_append(incoming)
        self.assertEqual(len(self.native_calls), before + 1)
        self.assertEqual(self.native_calls[-1][1], incoming)
        self.assertIsNone(self.finish())
        self.assertEqual(len(self.native_calls), before + 1)
        self.assertFalse(self.trial._stopped)

    def test_existing_native_prefix_and_selection_survive_insertion_before_pets(self):
        self.set_vector(1, self.child_data, [50, 51], selected=1)
        prefix = bytes(self.regions[self.child_data])
        self.begin()
        incoming = self.incoming()
        self.native_pet_append(incoming)
        self.finish()
        pointer, count = self.vector(1)
        self.assertEqual(count, 4)
        self.assertEqual(bytes(self.regions[pointer][:2 * ITEM.ITEM_SIZE]), prefix)
        self.assertEqual(ITEM._action(self.reader, pointer, 2), 0)
        self.assertEqual(ITEM._action(self.reader, pointer, 3), 46)
        self.assertEqual(self.reader(self.menu + ITEM.SELECTIONS_OFFSET + 4, 4), b"\1\0\0\0")
        self.assertEqual(self.vector(2)[1], 0)
        self.assertFalse(self.trial._stopped)
        self.assert_no_transition()

    def test_no_pet_builder_uses_native_trampoline_for_parent_and_child(self):
        self.assertIsNone(self.builder())
        self.assertFalse(self.trial._stopped)
        self.assertEqual(len(self.native_calls), 2)
        self.assertTrue(all(call[2][ITEM.MARKER_OFFSET:ITEM.MARKER_OFFSET + 16]
                            == ITEM.CUSTOM_ACTION_MARKER for call in self.native_calls))
        self.assertNotIn(self.hook.target, self.bindings)

    def test_completed_pet_or_page_without_parent_refuses_late_fallback_and_preserves_native(self):
        for action in (46, 47):
            with self.subTest(action=action):
                self.setUp()
                self.set_vector(1, self.child_data, [50, action], selected=1)
                before = {address: bytes(data) for address, data in self.regions.items()}
                # The original builder retained or constructed these entries
                # without an observed eligible append. AFTER cannot claim the
                # documented no-pet fallback or insert CAS behind them.
                self.assertIsNone(self.begin())
                self.assertIsNone(self.finish())
                self.assertTrue(self.trial._stopped)
                self.assertIsNone(self.trial._building)
                self.assertEqual(self.native_calls, [])
                self.constructor.assert_not_called()
                self.assertEqual({address: bytes(data) for address, data in self.regions.items()}, before)
                self.assert_no_transition()
                self.assert_guard_retained()

    def test_unpaired_or_wrong_header_append_never_reads_incoming(self):
        self.assertIsNone(self.trial.before_append(1, 2))
        self.assertEqual(self.reads, [])
        self.begin()
        self.reads.clear()
        self.assertIsNone(self.trial.before_append(self.menu + ITEM.VECTORS_OFFSET, 2))
        self.assertEqual(self.reads, [])
        self.assertEqual(self.native_calls, [])
        self.assertFalse(self.trial._stopped)

    def test_other_action_or_non_companion_parent_does_not_insert(self):
        for context in ("action", "parent", "depth"):
            with self.subTest(context=context):
                self.setUp()
                if context == "parent":
                    self.set_integer(ITEM.SELECTIONS_OFFSET, 1)
                elif context == "depth":
                    self.set_integer(ITEM.DEPTH_OFFSET, 0)
                self.begin()
                incoming = self.incoming(9 if context == "action" else 46)
                self.native_pet_append(incoming)
                self.assertEqual([call[1] for call in self.native_calls], [incoming])
                self.constructor.assert_not_called()
                self.assertFalse(self.trial._stopped)

    def test_missing_or_mismatched_builder_completion_stops_without_append(self):
        for mismatch in ("missing", "menu", "render", "thread"):
            with self.subTest(mismatch=mismatch):
                self.setUp()
                if mismatch != "missing":
                    self.begin()
                menu, render = self.menu, self.render
                if mismatch == "menu":
                    menu += 16
                elif mismatch == "render":
                    render += 16
                elif mismatch == "thread":
                    self.module.get_native_id.return_value += 1
                self.assertIsNone(self.trial.after_builder(menu, render))
                self.assertTrue(self.trial._stopped)
                self.assertIsNone(self.trial._building)
                self.assertEqual(self.native_calls, [])
                self.assert_guard_retained()

    def test_append_from_another_thread_stops_without_item_read(self):
        self.begin()
        self.module.get_native_id.return_value += 1
        self.reads.clear()
        self.assertIsNone(self.trial.before_append(self.menu + ITEM.VECTORS_OFFSET + 16, 2))
        self.assertTrue(self.trial._stopped)
        self.assertEqual(self.reads, [])
        self.assertEqual(self.native_calls, [])
        self.assert_guard_retained()

    def test_overlapping_callback_does_not_unlock_other_owner_and_retains_guard(self):
        self.begin()
        self.trial._lock.acquire()
        try:
            self.assertIsNone(self.trial.before_append(self.menu + ITEM.VECTORS_OFFSET + 16, 2))
            self.assertTrue(self.trial._lock.locked())
            self.assertTrue(self.trial._stopped)
            self.assertIsNone(self.trial._building)
        finally:
            self.trial._lock.release()
        self.assert_guard_retained()

    def test_nested_build_label_or_trigger_cancels_builder(self):
        for callback in ("builder", "label", "trigger"):
            with self.subTest(callback=callback):
                self.setUp()
                self.begin()
                if callback == "builder":
                    result = self.begin()
                elif callback == "label":
                    result = self.label()
                else:
                    result = self.trial.before_trigger(self.menu, 2, True)
                self.assertIsNone(result)
                self.assertTrue(self.trial._stopped)
                self.assertIsNone(self.trial._building)
                self.assertIsNone(self.finish())
                self.assertEqual(self.native_calls, [])
                self.assert_guard_retained()

    def test_read_error_stops_custom_processing_but_original_native_call_survives(self):
        incoming = self.incoming()
        self.begin()
        self.trial._reader = Mock(side_effect=OSError("private native address"))
        self.native_pet_append(incoming)
        self.assertTrue(self.trial._stopped)
        self.assertEqual([call[1] for call in self.native_calls], [incoming])
        self.assertIsNone(self.finish())
        self.assert_guard_retained()
        self.assertNotIn("private native address", repr(self.module.LOGGER.mock_calls))

    def test_reentry_during_constructor_stops_before_custom_append_without_retry(self):
        incoming = self.incoming()
        self.begin()
        def reentrant_construct(*args):
            self.construct(*args)
            self.trial.before_append(self.menu + ITEM.VECTORS_OFFSET + 16, incoming)
        self.constructor.side_effect = reentrant_construct
        self.native_pet_append(incoming)
        self.assertTrue(self.trial._stopped)
        self.assertEqual([call[1] for call in self.native_calls], [incoming])
        self.assertIsNone(self.finish())
        self.constructor.assert_called_once()
        self.assert_guard_retained()

    def test_native_append_failure_stops_without_retry_but_preserves_original_pet_call(self):
        self.fail_custom_append = True
        incoming = self.incoming()
        self.begin()
        self.native_pet_append(incoming)
        self.assertTrue(self.trial._stopped)
        self.assertEqual(len(self.native_calls), 2)
        self.assertEqual(self.native_calls[1][1], incoming)
        self.assertEqual(self.vector(1)[1], 1)
        self.assertIsNone(self.finish())
        self.assertIsNone(self.builder())
        self.assertEqual(len(self.native_calls), 2)
        self.assert_guard_retained()


class NavigationRegressionTests(OrderFixture):
    def test_parent_and_child_labels_and_native_false_navigation_are_preserved(self):
        self.prepare_parent()
        self.assertIsNone(self.label())
        self.trial._writer.assert_called_once_with(self.output, b"Companion Auto Summon")
        self.assertIsNone(self.before())
        self.assertIsNone(self.after(False))
        self.trial._write_field.assert_called_once_with(self.menu, ITEM.DEPTH_OFFSET, 2)
        self.trial._select_first.assert_called_once_with(self.menu)
        self.assertEqual(self.reader(self.menu + self.module.PENDING_SELECTION_OFFSET, 1), b"\0")
        self.trial._writer.reset_mock()
        self.assertIsNone(self.label())
        self.trial._writer.assert_called_once_with(self.output, b"Settings preview")
        self.trial._write_field.reset_mock()
        self.trial._select_first.reset_mock()
        child = self.vector(2)[0]
        self.assertIsNone(self.before(child))
        self.reads.clear()
        self.assertIsNone(self.after(False, action=child))
        self.assertEqual(self.reads, [])
        self.assert_no_transition()
        self.assertFalse(self.trial._stopped)

    def test_native_true_parent_result_stops_without_replacing_it(self):
        self.prepare_parent()
        self.before()
        self.assertIsNone(self.after(True))
        self.assertTrue(self.trial._stopped)
        self.assert_no_transition()
        self.assert_guard_retained()

    def test_vanilla_action_after_never_reads_old_action_or_changes_result(self):
        for result in (False, True):
            with self.subTest(result=result):
                self.setUp()
                self.prepare_parent()
                pet = self.vector(1)[0] + ITEM.ITEM_SIZE
                self.assertIsNone(self.before(pet))
                self.trial._reader = Mock(side_effect=AssertionError("Vanilla AFTER must not read"))
                self.assertIsNone(self.after(result, action=pet))
                self.trial._reader.assert_not_called()
                self.assertFalse(self.trial._stopped)
                self.assert_no_transition()


class CallbackDiagnosticsTests(OrderFixture):
    def warning(self):
        arguments = self.module.LOGGER.warning.call_args.args
        return arguments[0] % arguments[1:]

    def test_first_label_pins_origin_and_later_builder_thread_is_refused_before_reads(self):
        self.assertIsNone(self.label())
        self.assertFalse(self.trial._stopped)
        self.assertEqual(self.trial._thread_origin, "label_after")
        original_thread = self.trial._thread
        self.module.get_native_id.return_value += 1
        self.reads.clear()
        self.assertIsNone(self.begin())
        self.assertTrue(self.trial._stopped)
        self.assertEqual(self.trial._thread, original_thread)
        self.assertEqual(self.reads, [])
        self.assertEqual(self.native_calls, [])
        message = self.warning()
        for detail in ("unexpected_thread", "callback=builder_before",
                       "observed_thread=271829", "pinned_thread=271828", "pinned_by=label_after"):
            self.assertIn(detail, message)
        self.assert_guard_retained()

    def test_builder_completion_failure_captures_in_flight_state_before_clearing(self):
        self.begin()
        self.module.get_native_id.return_value += 1
        self.reads.clear()
        self.finish()
        message = self.warning()
        self.assertIn("callback=builder_after", message)
        self.assertIn("pinned_by=builder_before", message)
        self.assertIn("=(True, False, False, False, False, False, False)", message)
        self.assertEqual(self.trial._callback_history[-1][1:4], ("builder_after", 271829, True))
        self.assertIsNone(self.trial._building)
        self.assertEqual(self.reads, [])
        self.assertEqual(self.native_calls, [])
        for native_value in (self.menu, self.render):
            self.assertNotIn(str(native_value), message)
            self.assertNotIn(hex(native_value), message)
        self.assert_guard_retained()

    def test_rejected_append_reports_its_phase_without_reading_untrusted_item(self):
        self.begin()
        self.module.get_native_id.return_value += 1
        self.reads.clear()
        self.trial.before_append(self.menu + ITEM.VECTORS_OFFSET + ITEM.VECTOR_SIZE, 2)
        self.assertIn("append_unexpected_thread", self.warning())
        self.assertIn("callback=append observed_thread=271829", self.warning())
        self.assertEqual(self.trial._callback_history[-1][1:4], ("append", 271829, True))
        self.assertEqual(self.reads, [])
        self.assertEqual(self.native_calls, [])
        self.assert_guard_retained()

    def test_trigger_failure_records_pending_activation_and_does_not_change_native_result(self):
        self.prepare_parent()
        self.before()
        self.module.get_native_id.return_value += 1
        self.reads.clear()
        self.assertIsNone(self.after(False))
        self.assertIn("callback=trigger_after", self.warning())
        self.assertIn("=(False, True, False, False, False, True, False)", self.warning())
        self.assertIsNone(self.trial._pending)
        self.assertEqual(self.reads, [])
        self.assert_no_transition()
        self.assert_guard_retained()

    def test_trace_and_phase_logs_stay_bounded_while_normal_caption_work_continues(self):
        self.prepare_parent()
        for _ in range(80):
            self.label()
        self.assertFalse(self.trial._stopped)
        self.assertEqual(len(self.trial._callback_history), self.module.CALLBACK_HISTORY_LIMIT)
        self.assertEqual(self.trial._callback_counts["label_after"], 80)
        self.assertEqual(self.trial._writer.call_count, 80)
        first_observations = [call for call in self.module.LOGGER.info.call_args_list
                              if call.args[0].startswith("Menu callback first observed:")]
        self.assertEqual([call.args[1] for call in first_observations],
                         ["builder_before", "append", "builder_after", "label_after"])
        self.trial._callback_counts["label_after"] = self.module.CALLBACK_COUNT_LIMIT - 1
        self.trial._callback_sequence = self.module.CALLBACK_COUNT_LIMIT - 1
        self.label()
        self.label()
        self.assertEqual(self.trial._callback_counts["label_after"], self.module.CALLBACK_COUNT_LIMIT)
        self.assertEqual(self.trial._callback_sequence, self.module.CALLBACK_COUNT_LIMIT)
        self.module.get_native_id.return_value += 1
        self.label()
        warnings = self.module.LOGGER.warning.call_count
        reads = len(self.reads)
        self.label()
        self.begin()
        self.assertEqual(self.module.LOGGER.warning.call_count, warnings)
        self.assertEqual(len(self.reads), reads)
        self.assertLess(len(self.warning()), 2500)
        self.assert_guard_retained()

    def test_logging_failure_cannot_disable_normal_work_or_authorize_a_new_thread(self):
        self.module.LOGGER.info.side_effect = RuntimeError("private diagnostic failure")
        self.assertIsNone(self.label())
        self.assertFalse(self.trial._stopped)
        self.module.LOGGER.warning.side_effect = RuntimeError("private warning failure")
        self.module.get_native_id.return_value += 1
        self.reads.clear()
        self.assertIsNone(self.begin())
        self.assertTrue(self.trial._stopped)
        self.assertEqual(self.reads, [])
        self.assertEqual(self.native_calls, [])
        self.assert_guard_retained()

    def test_busy_diagnostic_lock_never_blocks_menu_or_weakens_thread_refusal(self):
        self.prepare_parent()
        self.trial._diagnostic_lock.acquire()
        try:
            self.label()
            self.assertFalse(self.trial._stopped)
            self.trial._writer.assert_called_once_with(self.output, b"Companion Auto Summon")
            self.module.get_native_id.return_value += 1
            self.reads.clear()
            self.label()
            self.assertTrue(self.trial._stopped)
            self.assertEqual(self.reads, [])
            self.assertIn("unexpected_thread", self.warning())
            self.assertIn("=unavailable counts=unavailable", self.warning())
        finally:
            self.trial._diagnostic_lock.release()
        self.assert_guard_retained()

    def test_overlapping_callback_keeps_safety_lock_owned_and_reports_attempted_phase(self):
        self.begin()
        self.trial._lock.acquire()
        try:
            self.module.get_native_id.return_value += 1
            self.reads.clear()
            self.label()
            self.assertTrue(self.trial._lock.locked())
            self.assertTrue(self.trial._stopped)
            self.assertEqual(self.reads, [])
            self.assertIn("overlapping_callback", self.warning())
            self.assertIn("callback=label_after observed_thread=271829", self.warning())
            self.assertIn("=(True, False, False, False, False, False, False)", self.warning())
        finally:
            self.trial._lock.release()
        self.assert_guard_retained()

    def test_failed_thread_lookup_cancels_safely_without_logging_exception_content(self):
        self.begin()
        self.module.get_native_id.side_effect = RuntimeError("private thread detail")
        self.reads.clear()
        self.assertIsNone(self.finish())
        self.assertIn("thread_lookup", self.warning())
        self.assertIn("callback=builder_after observed_thread=None", self.warning())
        self.assertNotIn("private thread detail", self.warning())
        self.assertEqual(self.reads, [])
        self.assertEqual(self.native_calls, [])
        self.assert_guard_retained()


class ConfirmationDiagnosticsTests(OrderFixture):
    settings_enabled = True

    def test_confirmation_completion_reports_pending_pair_before_cancelling(self):
        self.trial.before_confirmation(self.menu)
        self.module.get_native_id.return_value += 1
        self.reads.clear()
        self.assertIsNone(self.trial.after_confirmation(self.menu, False))
        arguments = self.module.LOGGER.warning.call_args.args
        message = arguments[0] % arguments[1:]
        self.assertIn("callback=confirmation_after observed_thread=271829", message)
        self.assertIn("pinned_by=confirmation_before", message)
        self.assertIn("=(False, False, True, False, False, False, False)", message)
        self.assertIsNone(self.trial._confirmation_call)
        self.assertIsNone(self.trial._confirmation_intent)
        self.assertEqual(self.reads, [])
        self.assert_no_transition()
        self.assert_guard_retained()


if __name__ == "__main__":
    unittest.main()
