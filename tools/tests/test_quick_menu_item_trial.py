"""Isolated trial tests: fake framework, synthetic menu, owned test buffers."""

import ctypes
import hashlib
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

from test_quick_menu_item import ITEM, ItemFixture


SOURCE = Path(__file__).resolve().parents[1] / "quick_menu_item_trial.py"
EXPECTED_HASH = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"


def load_trial(*, enabled=False, injected=True, base=0x100000, framework="0.2.4",
               digest=EXPECTED_HASH):
    source = SOURCE.read_text(encoding="utf-8")
    if enabled:
        if source.count("TRIAL_ENABLED = False") != 1:
            raise AssertionError("Expected one disabled trial marker")
        source = source.replace("TRIAL_ENABLED = False", "TRIAL_ENABLED = True", 1)
    events = []
    declarations = []

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
            self.function = function
            self.offset = offset
            declarations.append(self)

        def after(self, callback):
            callback._test_hook_offset = self.offset
            callback._test_hook_time = "after"
            return callback

        def __call__(self, *args):
            raise AssertionError("No real game wrapper may be called in an offline test")

    internal = types.ModuleType("pymhf.core._internal")
    internal.IS_INJECTED = injected
    internal.BASE_ADDRESS = base
    internal.BINARY_PATH = "synthetic-item-trial-executable.exe"
    pymhf = types.ModuleType("pymhf")
    pymhf.__path__ = []
    pymhf.Mod = FakeMod
    core = types.ModuleType("pymhf.core")
    core.__path__ = []
    core._internal = internal
    hooking = types.ModuleType("pymhf.core.hooking")
    hooking.static_function_hook = lambda *, offset: lambda function: FakeNative(function, offset)
    core.hooking = hooking
    pymhf.core = core
    runtime = types.ModuleType("quick_menu_guard_runtime")
    runtime.GuardError = type("GuardError", (RuntimeError,), {})
    runtime.ensure_guard = Mock(side_effect=AssertionError("Import must not install a native guard"))

    def fake_version(name):
        events.append(("version", name))
        return framework

    def fake_open(path, mode="r", *args, **kwargs):
        if str(path) != internal.BINARY_PATH or mode != "rb":
            raise AssertionError("Unexpected file access")
        events.append(("binary",))
        return io.BytesIO(b"owned synthetic executable")

    module = types.ModuleType("quick_menu_item_trial_under_test")
    module.__file__ = str(SOURCE)
    with patch.dict(sys.modules, {
        "quick_menu_item": ITEM, "quick_menu_guard_runtime": runtime,
        "pymhf": pymhf, "pymhf.core": core, "pymhf.core._internal": internal,
        "pymhf.core.hooking": hooking,
    }), patch("importlib.metadata.version", side_effect=fake_version), patch.object(
        Path, "open", fake_open
    ), patch.object(hashlib, "file_digest", return_value=Mock(hexdigest=lambda: digest)), patch.object(
        ctypes, "WinDLL", side_effect=AssertionError("No Windows API binding on import"), create=True
    ), patch.object(
        ctypes, "WINFUNCTYPE", side_effect=AssertionError("No native ABI binding on import"), create=True
    ):
        exec(compile(source, str(SOURCE), "exec"), module.__dict__)
    module.test_events = events
    module.test_declarations = declarations
    module.test_runtime = runtime
    module.LOGGER = Mock()
    module.get_native_id = Mock(return_value=271828)
    return module


class GuardAndInitializationTests(unittest.TestCase):
    def test_disabled_source_never_checks_binary_or_installs_guard(self):
        module = load_trial()
        self.assertEqual(module.test_events, [("class", True)])
        with patch.object(module, "current_process_io") as io_factory, patch.object(
            module, "native_adapters"
        ) as native_factory:
            instance = module.CompanionMenuItemTrial()
        self.assertTrue(instance._stopped)
        self.assertTrue(instance._abc_initialised)
        self.assertEqual(len(instance.hooks), 2)
        io_factory.assert_not_called()
        native_factory.assert_not_called()
        module.ensure_guard.assert_not_called()

    def test_unsupported_contexts_disable_class_before_native_initialization(self):
        for setting in ({"injected": False}, {"base": 0}, {"framework": "0.2.3"},
                        {"digest": "unsupported"}):
            with self.subTest(setting=setting):
                module = load_trial(enabled=True, **setting)
                self.assertTrue(module.CompanionMenuItemTrial._disabled)
                module.ensure_guard.assert_not_called()

    def test_class_guard_does_not_install_and_callbacks_have_exact_after_abi(self):
        module = load_trial(enabled=True)
        self.assertFalse(module.CompanionMenuItemTrial._disabled)
        module.ensure_guard.assert_not_called()
        self.assertEqual([declaration.offset for declaration in module.test_declarations],
                         [0x151ED00, 0x1523220])
        for declaration in module.test_declarations:
            self.assertEqual(list(declaration.function.__annotations__.values()),
                             [ctypes.c_void_p, ctypes.c_void_p, None])
        for name in ("after_builder", "after_label"):
            self.assertEqual(getattr(module.CompanionMenuItemTrial, name)._test_hook_time, "after")

    def test_native_guard_is_ready_before_active_instance_can_handle_callbacks(self):
        module = load_trial(enabled=True)
        order = []
        guard = Mock()
        with patch.object(module, "current_process_io", side_effect=lambda: (
            order.append("io") or Mock(), Mock()
        )), patch.object(module, "native_adapters", side_effect=lambda base: (
            order.append("adapters") or Mock(), Mock()
        )), patch.object(module, "ensure_guard", side_effect=lambda *args: (
            order.append("guard") or guard
        )):
            instance = module.CompanionMenuItemTrial()
        self.assertEqual(order, ["io", "adapters", "guard"])
        self.assertTrue(instance._abc_initialised)
        self.assertEqual(len(instance.hooks), 2)
        self.assertIs(instance._guard, guard)
        self.assertFalse(instance._stopped)

    def test_guard_initialization_error_leaves_instance_stopped(self):
        module = load_trial(enabled=True)
        with patch.object(module, "current_process_io", return_value=(Mock(), Mock())), patch.object(
            module, "native_adapters", return_value=(Mock(), Mock())
        ), patch.object(module, "ensure_guard", side_effect=RuntimeError("synthetic failure")):
            instance = module.CompanionMenuItemTrial()
        self.assertTrue(instance._stopped)
        self.assertIsNone(instance.after_builder(0x10000, 0x20000))
        self.assertIsNone(instance.after_label(0x10000, 0x20000))

    def test_guard_initialization_retains_sanitized_reason(self):
        module = load_trial(enabled=True)
        with patch.object(module, "current_process_io", return_value=(Mock(), Mock())), patch.object(
            module, "native_adapters", return_value=(Mock(), Mock())
        ), patch.object(module, "ensure_guard", side_effect=module.GuardError("integrity_mismatch")):
            instance = module.CompanionMenuItemTrial()
        self.assertTrue(instance._stopped)
        warning_args = module.LOGGER.warning.call_args.args
        self.assertIn("initialization: integrity_mismatch", warning_args)


class TrialFixture(ItemFixture):
    def setUp(self):
        super().setUp()
        self.module = load_trial()
        self.trial = self.module.CompanionMenuItemTrial()
        self.trial._stopped = False
        self.trial._reader = self.reader
        self.trial._writer = Mock()
        self.trial._constructor = self.constructor
        self.trial._append = self.append_callback
        self.trial._guard = self.guard
        self.output = 0x8880000

    def builder(self):
        return self.trial.after_builder(self.menu, 0x9990000)

    def label(self):
        return self.trial.after_label(self.menu, self.output)

    def assert_guard_retained(self):
        self.assertIs(self.trial._guard, self.guard)
        self.guard.disable.assert_not_called()
        self.guard.close.assert_not_called()
        self.guard.remove.assert_not_called()
        self.assertFalse(self.trial._lock.locked())


class CallbackTests(TrialFixture):
    def test_builder_appends_once_and_requires_readback_without_changing_return(self):
        self.assertIsNone(self.builder())
        self.assertTrue(self.trial._appended)
        self.assertFalse(self.trial._stopped)
        self.assertIsNone(self.builder())
        self.append_callback.assert_called_once()
        self.constructor.assert_called_once()
        self.assertEqual(self.module.LOGGER.info.call_count, 1)

    def test_label_writes_only_selected_full_marker_none_in_companion_context(self):
        self.assertIsNone(self.label())
        self.trial._writer.assert_not_called()
        self.tag(0, marker=bytes(16))
        self.assertIsNone(self.label())
        self.trial._writer.assert_not_called()
        self.tag(0)
        self.assertIsNone(self.label())
        self.trial._writer.assert_called_once_with(self.output, b"Companion Auto Summon")
        self.assertTrue(self.trial._label_seen)
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()

    def test_other_context_never_calls_guard_constructor_or_append(self):
        self.set_integer(ITEM.DEPTH_OFFSET, 0)
        self.assertIsNone(self.builder())
        self.guard.authorize_append.assert_not_called()
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()

    def test_guard_refusal_stops_before_constructor_and_does_not_retry(self):
        self.guard.authorize_append.side_effect = lambda menu: False
        self.assertIsNone(self.builder())
        self.assertTrue(self.trial._stopped)
        self.assertIsNone(self.builder())
        self.constructor.assert_not_called()
        self.append_callback.assert_not_called()
        self.assert_guard_retained()

    def test_constructor_error_stops_further_native_requests(self):
        self.constructor.side_effect = OSError("synthetic constructor error")
        self.assertIsNone(self.builder())
        self.assertTrue(self.trial._stopped)
        self.assertIsNone(self.builder())
        self.constructor.assert_called_once()
        self.append_callback.assert_not_called()
        self.assert_guard_retained()

    def test_append_partial_success_error_keeps_guard_and_never_rolls_back(self):
        def fail(header, data):
            self.append(header, data)
            raise OSError("synthetic append failure after mutation")
        self.append_callback.side_effect = fail
        self.assertIsNone(self.builder())
        self.assertTrue(self.trial._stopped)
        self.assertIsNone(self.builder())
        self.append_callback.assert_called_once()
        self.assertIs(ITEM.plan_append(self.reader, self.menu), ITEM.AppendStatus.ALREADY_PRESENT)
        self.assert_guard_retained()

    def test_missing_native_append_readback_stops_and_never_retries(self):
        self.append_callback.side_effect = None
        self.assertIsNone(self.builder())
        self.assertTrue(self.trial._stopped)
        self.assertFalse(self.trial._appended)
        self.assertIsNone(self.builder())
        self.append_callback.assert_called_once()
        self.assert_guard_retained()

    def test_reentry_during_constructor_stops_before_native_append(self):
        def construct(buffer, *args):
            self.construct(buffer, *args)
            self.assertIsNone(self.label())
        self.constructor.side_effect = construct
        self.assertIsNone(self.builder())
        self.assertTrue(self.trial._stopped)
        self.append_callback.assert_not_called()
        self.trial._writer.assert_not_called()
        self.assert_guard_retained()

    def test_reentry_during_reads_after_second_authorization_prevents_append(self):
        interrupted = []
        def reader(address, size):
            if self.guard.authorize_append.call_count >= 2 and not interrupted:
                interrupted.append(True)
                self.assertIsNone(self.label())
            return self.reader(address, size)
        self.trial._reader = reader
        self.assertIsNone(self.builder())
        self.assertEqual(interrupted, [True])
        self.assertTrue(self.trial._stopped)
        self.append_callback.assert_not_called()
        self.assert_guard_retained()

    def test_guard_lost_during_final_reads_prevents_append(self):
        revoked = []
        def reader(address, size):
            if self.guard.authorize_append.call_count >= 2 and not revoked:
                revoked.append(True)
                self.guard.authorize_append.side_effect = lambda menu: False
            return self.reader(address, size)
        self.trial._reader = reader
        self.assertIsNone(self.builder())
        self.assertEqual(revoked, [True])
        self.assertTrue(self.trial._stopped)
        self.append_callback.assert_not_called()
        self.assert_guard_retained()

    def test_later_different_native_thread_stops_mutation_and_retains_guard(self):
        self.assertIsNone(self.builder())
        self.module.get_native_id.return_value += 1
        self.assertIsNone(self.label())
        self.assertTrue(self.trial._stopped)
        self.trial._writer.assert_not_called()
        self.assert_guard_retained()

    def test_label_write_error_stops_without_repeated_writes(self):
        self.tag(0)
        self.trial._writer.side_effect = OSError("synthetic label write error")
        self.assertIsNone(self.label())
        self.assertTrue(self.trial._stopped)
        self.assertIsNone(self.label())
        self.trial._writer.assert_called_once()
        self.assert_guard_retained()

    def test_reentry_during_label_read_prevents_label_write(self):
        self.tag(0)
        interrupted = []
        def reader(address, size):
            if not interrupted:
                interrupted.append(True)
                self.assertIsNone(self.builder())
            return self.reader(address, size)
        self.trial._reader = reader
        self.assertIsNone(self.label())
        self.assertTrue(self.trial._stopped)
        self.trial._writer.assert_not_called()
        self.assert_guard_retained()

    def test_warning_logger_failure_cannot_escape_or_release_guard(self):
        self.trial._reader = Mock(side_effect=OSError("synthetic read error"))
        self.module.LOGGER.warning.side_effect = RuntimeError("synthetic logger failure")
        self.assertIsNone(self.builder())
        self.assertTrue(self.trial._stopped)
        self.assert_guard_retained()

    def test_thread_provider_failure_releases_lock_and_returns_none(self):
        self.module.get_native_id.side_effect = RuntimeError("synthetic thread failure")
        self.assertIsNone(self.builder())
        self.assertTrue(self.trial._stopped)
        self.assert_guard_retained()


class OwnedAdapterTests(unittest.TestCase):
    def test_native_adapters_use_aligned_owned_buffers_and_exact_abis(self):
        module = load_trial()
        declarations, calls = [], []
        base = 0x100000

        def bind(result, *arguments):
            declarations.append((result, arguments))
            def locate(target):
                if target == base + module.ITEM_CONSTRUCTOR_RVA:
                    def constructor(address, icon, action, disabled, background):
                        self.assertEqual(address % 16, 0)
                        self.assertEqual(ctypes.string_at(address, 224), bytes(224))
                        ctypes.memmove(address, b"x" * 224, 224)
                        calls.append(("constructor", icon, action, disabled, background))
                        return address
                    return constructor
                self.assertEqual(target, base + module.ITEM_APPEND_RVA)
                def append(header, address):
                    self.assertEqual(address % 16, 0)
                    calls.append(("append", header, ctypes.string_at(address, 224)))
                    return 0x5550000  # Synthetic identity, never dereferenced.
                return append
            return locate

        with patch.object(module.C, "WINFUNCTYPE", side_effect=bind, create=True):
            construct, append = module.native_adapters(base)
        owned = bytearray(224)
        construct(owned, 7, 0, False, True)
        self.assertEqual(owned, b"x" * 224)
        append(0x2220000, bytes(owned))
        self.assertEqual(declarations, [
            (ctypes.c_void_p, (ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int32,
                              ctypes.c_bool, ctypes.c_bool)),
            (ctypes.c_void_p, (ctypes.c_void_p, ctypes.c_void_p)),
        ])
        self.assertEqual(calls, [("constructor", 7, 0, False, True),
                                 ("append", 0x2220000, b"x" * 224)])

    def test_io_copies_bounded_owned_data_and_nul_padded_label(self):
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
        kernel.ReadProcessMemory.side_effect = read
        kernel.WriteProcessMemory.side_effect = write
        with patch.object(module.C, "WinDLL", return_value=kernel, create=True):
            reader, writer = module.current_process_io()
        self.assertEqual(reader(0x1230000, 16), b"q" * 16)
        writer(0x4560000, b"Companion Auto Summon")
        label = b"Companion Auto Summon"
        self.assertEqual(writes, [(0x4560000, label + bytes(128 - len(label)))])
        for label in (b"", b"x" * 128, b"a\0b", "text"):
            with self.subTest(label_type=type(label).__name__), self.assertRaises(ValueError):
                writer(0x4560000, label)
        self.assertEqual(len(writes), 1)
        with self.assertRaises(ValueError):
            reader(0x1230000, 224)

    def test_incomplete_label_write_is_an_error(self):
        module = load_trial()
        kernel = types.SimpleNamespace(GetCurrentProcess=Mock(return_value=-1),
                                       ReadProcessMemory=Mock(), WriteProcessMemory=Mock())
        kernel.WriteProcessMemory.return_value = 1
        with patch.object(module.C, "WinDLL", return_value=kernel, create=True):
            _, writer = module.current_process_io()
        with self.assertRaises(OSError):
            writer(0x1230000, b"text")


if __name__ == "__main__":
    unittest.main()
