"""Offline probe tests: fake framework, fake Windows reads, no game access."""

import ctypes
import hashlib
import importlib.metadata
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


SOURCE = Path(__file__).resolve().parents[1] / "quick_menu_probe.py"
EXPECTED_HASH = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"


def load_probe(*, enabled=True, injected=True, base=1, framework="0.2.4",
               digest=EXPECTED_HASH, version_error=None, open_error=None):
    source = SOURCE.read_text(encoding="utf-8")
    if enabled:
        if source.count("PROBE_ENABLED = False") != 1:
            raise AssertionError("Probe opt-in marker must be unique")
        source = source.replace("PROBE_ENABLED = False", "PROBE_ENABLED = True", 1)
    events = []
    declarations = []

    class FakeMod:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            events.append(("class-created", cls._disabled))

    class FakeNative:
        def __init__(self, function, offset):
            self.function = function
            self.offset = offset
            declarations.append(self)

        def before(self, callback):
            callback._test_hook_time = "before"
            callback._test_hook_offset = self.offset
            return callback

        def __call__(self, *args, **kwargs):
            raise AssertionError("Probe must never call a native game function")

    internal = types.ModuleType("pymhf.core._internal")
    internal.IS_INJECTED = injected
    internal.BASE_ADDRESS = base
    internal.BINARY_PATH = "offline-test-only.exe"
    pymhf = types.ModuleType("pymhf")
    pymhf.__path__ = []
    pymhf.Mod = FakeMod
    core = types.ModuleType("pymhf.core")
    core.__path__ = []
    core._internal = internal
    pymhf.core = core
    hooking = types.ModuleType("pymhf.core.hooking")
    hooking.static_function_hook = lambda *, offset: lambda fn: FakeNative(fn, offset)
    core.hooking = hooking

    def fake_version(name):
        events.append(("version", name))
        if version_error is not None:
            raise version_error
        return framework

    def fake_open(path, mode="r", *args, **kwargs):
        events.append(("open", str(path), mode))
        if str(path) != internal.BINARY_PATH or mode != "rb":
            raise AssertionError("Unexpected import file access")
        if open_error is not None:
            raise open_error
        return io.BytesIO(b"owned offline test bytes")

    module = types.ModuleType("quick_menu_probe_under_test")
    module.__file__ = str(SOURCE)
    with patch.dict(sys.modules, {
        "pymhf": pymhf, "pymhf.core": core,
        "pymhf.core._internal": internal, "pymhf.core.hooking": hooking,
    }), patch("importlib.metadata.version", side_effect=fake_version), patch.object(
        Path, "open", fake_open
    ), patch.object(hashlib, "file_digest", return_value=Mock(hexdigest=lambda: digest)), patch.object(
        ctypes, "WinDLL", side_effect=AssertionError("Import must not bind Windows APIs"), create=True
    ):
        exec(compile(source, str(SOURCE), "exec"), module.__dict__)
    module.test_events = events
    module.test_declarations = declarations
    return module


class ProbeGuardTests(unittest.TestCase):
    def test_source_is_disabled_before_any_import_file_or_version_read(self):
        module = load_probe(enabled=False)
        self.assertTrue(module.CompanionMenuProbe._disabled)
        self.assertEqual(module.test_events, [("class-created", True)])

    def test_outside_injection_is_disabled_without_binary_reads(self):
        module = load_probe(injected=False)
        self.assertTrue(module.CompanionMenuProbe._disabled)
        self.assertEqual(module.test_events, [("class-created", True)])

    def test_invalid_base_is_disabled_without_binary_reads(self):
        module = load_probe(base=0)
        self.assertEqual(module.test_events, [("class-created", True)])

    def test_wrong_framework_skips_binary_read(self):
        module = load_probe(framework="0.2.3")
        self.assertTrue(module.CompanionMenuProbe._disabled)
        self.assertEqual([row[0] for row in module.test_events], ["version", "class-created"])

    def test_missing_framework_metadata_fails_closed(self):
        module = load_probe(version_error=importlib.metadata.PackageNotFoundError("pymhf"))
        self.assertTrue(module.CompanionMenuProbe._disabled)

    def test_wrong_executable_hash_disables_before_registration(self):
        module = load_probe(digest="wrong")
        self.assertTrue(module.CompanionMenuProbe._disabled)
        self.assertEqual(module.test_events[-1], ("class-created", True))

    def test_unreadable_executable_fails_closed(self):
        module = load_probe(open_error=OSError("offline simulated read failure"))
        self.assertTrue(module.CompanionMenuProbe._disabled)

    def test_exact_runtime_enables_one_before_hook_with_bool_abi(self):
        module = load_probe()
        self.assertFalse(module.CompanionMenuProbe._disabled)
        self.assertEqual(len(module.test_declarations), 1)
        definition = module.test_declarations[0]
        self.assertEqual(definition.offset, 0x1526940)
        self.assertEqual(definition.function.__annotations__, {
            "menu": ctypes.c_void_p, "action": ctypes.c_void_p,
            "called_as_menu": ctypes.c_bool, "return": ctypes.c_bool,
        })
        callback = module.CompanionMenuProbe.observe_action
        self.assertEqual(callback._test_hook_time, "before")
        self.assertEqual(callback._test_hook_offset, 0x1526940)
        mods = [obj for obj in module.__dict__.values()
                if isinstance(obj, type) and obj.__module__ == module.__name__]
        self.assertEqual(mods, [module.CompanionMenuProbe])


class ProbeObservationTests(unittest.TestCase):
    def setUp(self):
        self.module = load_probe()
        self.menu = 0x100000
        self.action = 0x200000
        self.memory = {
            self.action + 4: (45).to_bytes(4, "little", signed=True),
            self.menu + 0xA050: (1).to_bytes(4, "little", signed=True),
        }
        self.reads = []

        def read(address, size):
            self.reads.append((address, size))
            return self.memory[address]

        self.reader = Mock(side_effect=read)
        self.logger = Mock()
        self.probe = self.module.CompanionMenuProbe(reader=self.reader, logger=self.logger)

    def observe(self):
        return self.probe.observe_action(self.menu, self.action, True)

    def test_normal_callback_only_copies_scalars_returns_none_and_preserves_memory(self):
        before = dict(self.memory)
        self.assertIsNone(self.observe())
        self.assertEqual(self.reads, [(self.action + 4, 4), (self.menu + 0xA050, 4)])
        self.assertEqual(self.memory, before)
        self.logger.info.assert_called_once_with(
            "Quick menu observation: action=%d depth=%d called_as_menu=%s", 45, 1, True)
        self.assertFalse(self.probe._stopped)
        self.assertNotIn(self.menu, vars(self.probe).values())
        self.assertNotIn(self.action, vars(self.probe).values())

    def test_invalid_pointers_fail_before_reader_access(self):
        invalid = [None, False, True, 0, -1, 0xFFFF, 1.5, "address", 0x7FFFFFFFFFFF]
        for value in invalid:
            with self.subTest(value=value):
                probe = self.module.CompanionMenuProbe(reader=self.reader, logger=Mock())
                self.assertIsNone(probe.observe_action(self.menu, value, True))
                self.assertTrue(probe._stopped)
                probe = self.module.CompanionMenuProbe(reader=self.reader, logger=Mock())
                self.assertIsNone(probe.observe_action(value, self.action, True))
                self.assertTrue(probe._stopped)
        self.reader.assert_not_called()

    def test_invalid_flag_fails_without_reading(self):
        self.assertIsNone(self.probe.observe_action(self.menu, self.action, 1))
        self.reader.assert_not_called()
        self.assertTrue(self.probe._stopped)

    def test_failed_read_stops_once_without_further_reads_or_error_details(self):
        self.reader.side_effect = OSError("private address details must not enter logs")
        self.assertIsNone(self.observe())
        self.assertIsNone(self.observe())
        self.assertEqual(self.reader.call_count, 1)
        self.logger.warning.assert_called_once_with(
            "Quick menu probe disabled after an invalid or unreadable observation.")
        self.logger.info.assert_not_called()

    def test_partial_or_non_owned_read_fails_closed(self):
        for value in [b"", b"\x00" * 3, b"\x00" * 5, bytearray(4), None]:
            with self.subTest(value=value):
                reader = Mock(return_value=value)
                logger = Mock()
                probe = self.module.CompanionMenuProbe(reader=reader, logger=logger)
                self.assertIsNone(probe.observe_action(self.menu, self.action, True))
                reads = reader.call_count
                self.assertEqual(reads, 1)
                self.assertIsNone(probe.observe_action(self.menu, self.action, True))
                self.assertEqual(reader.call_count, reads)
                logger.warning.assert_called_once()
                logger.info.assert_not_called()

    def test_unknown_action_or_depth_stops_without_logging_values(self):
        for action_id, depth in [(-1, 1), (67, 1), (45, -1), (45, 3)]:
            with self.subTest(action_id=action_id, depth=depth):
                reader = Mock(side_effect=[action_id.to_bytes(4, "little", signed=True),
                                          depth.to_bytes(4, "little", signed=True)])
                logger = Mock()
                probe = self.module.CompanionMenuProbe(reader=reader, logger=logger)
                self.assertIsNone(probe.observe_action(self.menu, self.action, False))
                self.assertTrue(probe._stopped)
                logger.info.assert_not_called()

    def test_valid_range_endpoints_are_observed(self):
        for action_id, depth in [(0, 0), (66, 2)]:
            with self.subTest(action_id=action_id, depth=depth):
                reader = Mock(side_effect=[action_id.to_bytes(4, "little"), depth.to_bytes(4, "little")])
                probe = self.module.CompanionMenuProbe(reader=reader, logger=Mock())
                self.assertIsNone(probe.observe_action(self.menu, self.action, False))
                self.assertFalse(probe._stopped)

    def test_budget_is_exactly_64_observations_and_one_cap_notice(self):
        for _ in range(100):
            self.assertIsNone(self.observe())
        self.assertEqual(self.probe._event_count, 64)
        self.assertEqual(self.reader.call_count, 128)
        self.assertEqual(self.logger.info.call_count, 65)
        self.assertEqual(self.logger.info.call_args.args,
                         ("Quick menu probe reached its 64-event limit; observation stopped.",))
        self.logger.warning.assert_not_called()

    def test_disabled_or_uninjected_callbacks_never_read(self):
        self.probe._disabled = True
        self.assertIsNone(self.observe())
        self.probe._disabled = False
        self.module._internal.IS_INJECTED = False
        self.assertIsNone(self.observe())
        self.module._internal.IS_INJECTED = True
        self.assertIsNone(self.observe())
        self.reader.assert_not_called()

    def test_logger_failure_cannot_change_original_call(self):
        self.logger.info.side_effect = RuntimeError("logging unavailable")
        self.logger.warning.side_effect = RuntimeError("logging still unavailable")
        self.assertIsNone(self.observe())
        self.assertTrue(self.probe._stopped)
        self.assertIsNone(self.observe())
        self.assertEqual(self.reader.call_count, 2)

    def test_default_reader_is_created_lazily_inside_valid_callback(self):
        with patch.object(self.module, "create_current_process_reader", return_value=self.reader) as factory:
            probe = self.module.CompanionMenuProbe(logger=self.logger)
            factory.assert_not_called()
            self.assertIsNone(probe.observe_action(self.menu, self.action, True))
            self.assertIsNone(probe.observe_action(self.menu, self.action, False))
            factory.assert_called_once_with()

    def test_reentrant_observation_passes_through_without_reading_or_waiting(self):
        calls = []

        def nested_read(address, size):
            calls.append((address, size))
            self.assertIsNone(self.observe())
            return self.memory[address]

        self.reader.side_effect = nested_read
        self.assertIsNone(self.observe())
        self.assertEqual(calls, [(self.action + 4, 4), (self.menu + 0xA050, 4)])
        self.assertEqual(self.probe._event_count, 1)
        self.logger.warning.assert_not_called()

    def test_contended_observation_returns_none_without_reading(self):
        self.probe._observation_lock.acquire()
        try:
            self.assertIsNone(self.observe())
            self.reader.assert_not_called()
        finally:
            self.probe._observation_lock.release()


class WindowsReaderTests(unittest.TestCase):
    def setUp(self):
        self.module = load_probe(enabled=False)
        self.kernel = types.SimpleNamespace(
            GetCurrentProcess=Mock(return_value=0xFFFFFFFFFFFFFFFF),
            ReadProcessMemory=Mock(),
        )

    def make_reader(self, *, success=1, count=4):
        def fake_read(handle, address, destination, size, copied):
            destination.raw = b"abcd"
            ctypes.cast(copied, ctypes.POINTER(ctypes.c_size_t)).contents.value = count
            return success

        self.kernel.ReadProcessMemory.side_effect = fake_read
        with patch.object(ctypes, "WinDLL", return_value=self.kernel, create=True) as loader:
            reader = self.module.create_current_process_reader()
        loader.assert_called_once_with("kernel32", use_last_error=True)
        return reader

    def test_reader_declares_full_windows_abi_and_copies_owned_bytes(self):
        reader = self.make_reader()
        self.assertEqual(reader(0x10000, 4), b"abcd")
        self.assertEqual(self.kernel.GetCurrentProcess.argtypes, [])
        self.assertIs(self.kernel.GetCurrentProcess.restype, ctypes.c_void_p)
        self.assertEqual(self.kernel.ReadProcessMemory.argtypes, [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t),
        ])
        self.assertIs(self.kernel.ReadProcessMemory.restype, ctypes.c_int)

    def test_failed_or_partial_windows_copy_is_rejected(self):
        for success, count in [(0, 4), (1, 0), (1, 3), (1, 5)]:
            with self.subTest(success=success, count=count):
                reader = self.make_reader(success=success, count=count)
                with self.assertRaises(OSError):
                    reader(0x10000, 4)

    def test_invalid_range_rejected_without_windows_read(self):
        reader = self.make_reader()
        for address, size in [(None, 4), (True, 4), (0xFFFF, 4), (0x10000, 0),
                              (0x10000, 8), (0x7FFFFFFFFFFD, 4)]:
            with self.subTest(address=address, size=size):
                with self.assertRaises(ValueError):
                    reader(address, size)
        self.kernel.ReadProcessMemory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
