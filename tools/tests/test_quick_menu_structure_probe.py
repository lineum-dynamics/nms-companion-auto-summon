"""Offline tests for the separate structure probe; no game or native reads."""

import ctypes
import hashlib
import importlib.metadata
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


SOURCE = Path(__file__).resolve().parents[1] / "quick_menu_structure_probe.py"
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

        def after(self, callback):
            callback._test_hook_time = "after"
            callback._test_hook_offset = self.offset
            return callback

        def __call__(self, *args, **kwargs):
            raise AssertionError("Observer must not invoke any native game function")

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

    module = types.ModuleType("quick_menu_structure_probe_under_test")
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


class GuardTests(unittest.TestCase):
    def test_disabled_source_skips_framework_and_binary_reads(self):
        module = load_probe(enabled=False)
        self.assertTrue(module.CompanionMenuStructureProbe._disabled)
        self.assertEqual(module.test_events, [("class-created", True)])

    def test_noninjected_or_invalid_base_skips_binary_reads(self):
        for settings in ({"injected": False}, {"base": 0}):
            with self.subTest(settings=settings):
                module = load_probe(**settings)
                self.assertEqual(module.test_events, [("class-created", True)])

    def test_wrong_framework_and_missing_metadata_fail_closed(self):
        for settings in ({"framework": "0.2.3"},
                         {"version_error": importlib.metadata.PackageNotFoundError("pymhf")}):
            with self.subTest(settings=settings):
                module = load_probe(**settings)
                self.assertTrue(module.CompanionMenuStructureProbe._disabled)
                self.assertNotIn("open", [event[0] for event in module.test_events])

    def test_wrong_or_unreadable_executable_disables_class(self):
        for settings in ({"digest": "wrong"}, {"open_error": OSError("simulated")}):
            with self.subTest(settings=settings):
                module = load_probe(**settings)
                self.assertTrue(module.CompanionMenuStructureProbe._disabled)
                self.assertEqual(module.test_events[-1], ("class-created", True))

    def test_exact_runtime_exposes_one_mod_and_two_void_after_hooks(self):
        module = load_probe()
        self.assertFalse(module.CompanionMenuStructureProbe._disabled)
        self.assertEqual([hook.offset for hook in module.test_declarations], [0x151ED00, 0x1523220])
        for declaration, second_arg in zip(module.test_declarations, ("render", "output")):
            self.assertEqual(declaration.function.__annotations__, {
                "menu": ctypes.c_void_p, second_arg: ctypes.c_void_p, "return": None,
            })
        for name, offset in (("observe_builder", 0x151ED00), ("observe_label", 0x1523220)):
            callback = getattr(module.CompanionMenuStructureProbe, name)
            self.assertEqual(callback._test_hook_time, "after")
            self.assertEqual(callback._test_hook_offset, offset)
        classes = [obj for obj in module.__dict__.values()
                   if isinstance(obj, type) and obj.__module__ == module.__name__]
        self.assertEqual(classes, [module.CompanionMenuStructureProbe])


class StructureFixture(unittest.TestCase):
    def setUp(self):
        self.module = load_probe()
        self.menu = 0x100000
        self.output = 0x200000
        self.memory = {}
        self.memory[self.menu + 0xA050, 4] = (1).to_bytes(4, "little", signed=True)
        for depth in range(3):
            self.set_vector(depth, capacity=4, item_count=2, selected=1,
                            action=(45, 46, 47)[depth])
        self.memory[self.output, 128] = b"PRIVATE COMPANION LABEL\0".ljust(128, b"!")
        self.reads = []
        self.now = 10.0
        self.thread = 12
        self.logger = Mock()

        def read(address, size):
            self.reads.append((address, size))
            return self.memory[address, size]

        self.reader = Mock(side_effect=read)
        self.probe = self.module.CompanionMenuStructureProbe(
            reader=self.reader, logger=self.logger, clock=lambda: self.now,
            thread_id=lambda: self.thread)

    def set_vector(self, depth, *, capacity, item_count, selected, action=45, pointer=None):
        if pointer is None:
            pointer = 0x300000 + depth * 0x10000
        self.memory[self.menu + 0xA058 + depth * 16, 16] = (
            capacity.to_bytes(4, "little") + item_count.to_bytes(4, "little")
            + pointer.to_bytes(8, "little"))
        self.memory[self.menu + 0xA088 + depth * 4, 4] = selected.to_bytes(4, "little", signed=True)
        if pointer >= 0x10000 and 0 <= selected < item_count:
            self.memory[pointer + selected * 0xE0 + 4, 4] = action.to_bytes(4, "little", signed=True)

    def builder(self):
        # The render pointer is unused; supplying None proves no render dereference.
        return self.probe.observe_builder(self.menu, None)

    def label(self):
        return self.probe.observe_label(self.menu, self.output)


class StructureReadTests(StructureFixture):
    def test_builder_reads_three_headers_and_only_selected_action_scalars(self):
        before = dict(self.memory)
        snapshot = self.module.inspect_builder(self.reader, self.menu)
        self.assertEqual(snapshot, (1, (
            (0, 4, 2, 1, "selected", 45), (1, 4, 2, 1, "selected", 46),
            (2, 4, 2, 1, "selected", 47))))
        self.assertEqual(len(self.reads), 10)
        self.assertEqual(self.memory, before)
        self.assertTrue(all(size in (4, 16) for _, size in self.reads))

    def test_stale_indices_are_status_and_never_read_out_of_range_items(self):
        for selected in (-1, 2, 0x7FFFFFFF):
            with self.subTest(selected=selected):
                self.set_vector(0, capacity=4, item_count=2, selected=selected)
                self.reads.clear()
                snapshot = self.module.read_vector_selection(self.reader, self.menu, 0)
                self.assertEqual(snapshot, (0, 4, 2, selected, "stale_selection", None))
                self.assertEqual(len(self.reads), 2)

    def test_empty_vector_ignores_unused_data_pointer_and_index(self):
        for pointer in (0, 0xFFFFFFFFFFFFFFFF):
            with self.subTest(pointer=pointer):
                self.set_vector(0, capacity=4, item_count=0, selected=-1, pointer=pointer)
                self.reads.clear()
                self.assertEqual(self.module.read_vector_selection(self.reader, self.menu, 0),
                                 (0, 4, 0, -1, "empty", None))
                self.assertEqual(len(self.reads), 2)

    def test_count_capacity_and_diagnostic_bounds_fail_before_any_item_read(self):
        for capacity, item_count in ((0, 1), (2, 3), (257, 0), (257, 257)):
            with self.subTest(capacity=capacity, item_count=item_count):
                self.set_vector(0, capacity=capacity, item_count=item_count, selected=0)
                self.reads.clear()
                with self.assertRaises(ValueError):
                    self.module.read_vector_selection(self.reader, self.menu, 0)
                self.assertEqual(self.reads, [(self.menu + 0xA058, 16)])

    def test_maximum_diagnostic_count_reads_only_last_selected_enum(self):
        self.set_vector(0, capacity=256, item_count=256, selected=255, action=66)
        snapshot = self.module.read_vector_selection(self.reader, self.menu, 0)
        self.assertEqual(snapshot[-1], 66)
        self.assertEqual(self.reads[-1], (0x300000 + 255 * 0xE0 + 4, 4))
        self.assertEqual(len(self.reads), 3)

    def test_nonempty_vector_rejects_null_low_and_overflowing_data_ranges(self):
        for pointer in (0, 0xFFFF, 0x7FFFFFFFFFFF - 0xE0):
            with self.subTest(pointer=pointer):
                self.set_vector(0, capacity=2, item_count=2, selected=0, pointer=pointer)
                self.reads.clear()
                with self.assertRaises(ValueError):
                    self.module.read_vector_selection(self.reader, self.menu, 0)
                self.assertEqual(len(self.reads), 2)

    def test_unknown_selected_action_is_rejected(self):
        for action in (-1, 67):
            with self.subTest(action=action):
                self.set_vector(0, capacity=2, item_count=2, selected=0, action=action)
                with self.assertRaises(ValueError):
                    self.module.read_vector_selection(self.reader, self.menu, 0)

    def test_invalid_current_depth_prevents_header_reads(self):
        for depth in (-1, 3):
            with self.subTest(depth=depth):
                self.memory[self.menu + 0xA050, 4] = depth.to_bytes(4, "little", signed=True)
                self.reads.clear()
                with self.assertRaises(ValueError):
                    self.module.inspect_builder(self.reader, self.menu)
                self.assertEqual(self.reads, [(self.menu + 0xA050, 4)])

    def test_label_returns_only_terminator_metadata_and_selected_enum(self):
        snapshot = self.module.inspect_label(self.reader, self.menu, self.output)
        self.assertEqual(snapshot, (1, "selected", 46, True, 23))
        self.assertNotIn("PRIVATE", repr(snapshot))
        self.assertEqual(self.reads[-1], (self.output, 128))
        self.assertEqual(len(self.reads), 5)

    def test_label_empty_and_last_byte_terminators_are_valid(self):
        for payload, length in ((b"\0" * 128, 0), (b"x" * 127 + b"\0", 127)):
            with self.subTest(length=length):
                self.memory[self.output, 128] = payload
                self.assertEqual(self.module.inspect_label(self.reader, self.menu, self.output)[3:],
                                 (True, length))

    def test_unterminated_label_never_claims_an_actual_length(self):
        self.memory[self.output, 128] = b"x" * 128
        self.assertEqual(self.module.inspect_label(self.reader, self.menu, self.output)[3:],
                         (False, None))

    def test_bad_label_range_is_rejected_before_menu_reads(self):
        for output in (None, False, 0, 0x7FFFFFFFFFFF - 126):
            with self.subTest(output=output):
                with self.assertRaises(ValueError):
                    self.module.inspect_label(self.reader, self.menu, output)
        self.reader.assert_not_called()


class ObservationTests(StructureFixture):
    def test_after_callbacks_return_none_and_preserve_memory(self):
        before = dict(self.memory)
        self.assertIsNone(self.builder())
        self.assertIsNone(self.label())
        self.assertEqual(self.memory, before)
        self.assertFalse(self.probe._stopped)
        self.assertEqual(self.logger.info.call_count, 2)
        self.assertNotIn("PRIVATE", repr(self.logger.mock_calls))
        self.assertNotIn(self.menu, vars(self.probe).values())
        self.assertNotIn(self.output, vars(self.probe).values())
        self.assertNotIn(b"PRIVATE", repr(self.probe._channels).encode())

    def test_sampling_is_independent_per_hook_and_throttled_to_four_hertz(self):
        self.builder()
        self.label()
        self.assertEqual(self.reader.call_count, 15)
        self.now += 0.1
        for _ in range(50):
            self.assertIsNone(self.builder())
            self.assertIsNone(self.label())
        self.assertEqual(self.reader.call_count, 15)
        self.now += 0.15
        self.builder()
        self.label()
        self.assertEqual(self.reader.call_count, 30)
        self.assertEqual(self.logger.info.call_count, 2)

    def test_identical_snapshots_do_not_exhaust_detail_budget(self):
        for _ in range(80):
            self.builder()
            self.now += 0.25
        state = self.probe._channels["builder"]
        self.assertEqual(state["samples"], 80)
        self.assertEqual(state["details"], 1)
        self.assertFalse(state["capped"])
        self.logger.info.assert_called_once()

    def test_sample_budget_stops_reads_and_emits_one_frequency_summary(self):
        self.module.MAX_SAMPLES = 4
        for _ in range(20):
            self.builder()
            self.now += 0.25
        self.assertEqual(self.reader.call_count, 40)
        self.assertEqual(self.logger.info.call_count, 2)
        summary = self.logger.info.call_args.args
        self.assertEqual(summary[1:6], ("builder", "sample_limit", 4, 4, 1))
        self.assertEqual(summary[6], 0.75)
        self.assertTrue(self.probe._channels["builder"]["capped"])
        self.assertFalse(self.probe._channels["label"]["capped"])

    def test_distinct_snapshot_budget_stops_only_its_channel(self):
        self.module.MAX_DETAILS = 3
        for index in range(6):
            self.set_vector(0, capacity=4, item_count=2, selected=index % 2)
            self.builder()
            self.now += 0.25
        self.assertEqual(self.probe._channels["builder"]["details"], 3)
        self.assertEqual(self.logger.info.call_count, 4)
        self.assertEqual(self.reader.call_count, 30)
        self.assertIsNone(self.label())
        self.assertEqual(self.reader.call_count, 35)

    def test_frequency_counter_includes_throttled_callbacks_and_elapsed(self):
        self.builder()
        self.now += 0.1
        for _ in range(9):
            self.builder()
        self.set_vector(0, capacity=4, item_count=2, selected=0)
        self.now += 0.4
        self.builder()
        observation = self.logger.info.call_args.args
        self.assertEqual(observation[1:5], ("builder", 11, 2, 0.5))

    def test_sparse_callbacks_sample_immediately_without_catch_up_reads(self):
        self.builder()
        self.now += 120.0
        self.set_vector(0, capacity=4, item_count=2, selected=0)
        self.builder()
        self.assertEqual(self.reader.call_count, 20)
        self.assertEqual(self.logger.info.call_args.args[2:5], (2, 2, 120.0))

    def test_thread_identity_is_a_boolean_and_never_a_raw_id_in_logs(self):
        self.builder()
        self.thread = 987654321
        self.label()
        self.assertFalse(self.logger.info.call_args.args[5])
        self.assertNotIn("987654321", repr(self.logger.mock_calls))
        self.assertFalse(self.probe._single_thread)

    def test_contention_never_waits_or_reads_and_callback_is_counted(self):
        self.probe._observation_lock.acquire()
        try:
            self.assertIsNone(self.builder())
            self.reader.assert_not_called()
        finally:
            self.probe._observation_lock.release()
        self.now += 0.5
        self.builder()
        self.assertEqual(self.logger.info.call_args.args[2:5], (2, 1, 0.0))

    def test_preempted_callback_timestamps_after_newer_completed_sample(self):
        self.builder()
        real_lock = self.probe._observation_lock
        proxy_lock = Mock()

        def preempt_before_acquire(*, blocking):
            self.assertFalse(blocking)
            self.probe._observation_lock = real_lock
            self.now = 10.5
            self.assertIsNone(self.builder())
            self.probe._observation_lock = proxy_lock
            return real_lock.acquire(blocking=False)

        proxy_lock.acquire.side_effect = preempt_before_acquire
        proxy_lock.release.side_effect = real_lock.release
        self.probe._observation_lock = proxy_lock
        self.now = 10.25
        self.assertIsNone(self.builder())
        self.assertFalse(self.probe._stopped)
        self.assertEqual(self.reader.call_count, 20)
        self.assertEqual(self.probe._channels["builder"]["last_sample"], 10.5)
        self.logger.warning.assert_not_called()

    def test_reentrant_callback_passes_through_without_extra_reads(self):
        def nested_read(address, size):
            self.assertIsNone(self.builder())
            return self.memory[address, size]

        self.reader.side_effect = nested_read
        self.assertIsNone(self.builder())
        self.assertEqual(self.reader.call_count, 10)
        self.assertEqual(self.probe._channels["builder"]["samples"], 1)

    def test_disabled_or_lost_injection_never_reads(self):
        self.probe._disabled = True
        self.assertIsNone(self.builder())
        self.probe._disabled = False
        self.module._internal.IS_INJECTED = False
        self.assertIsNone(self.label())
        self.module._internal.IS_INJECTED = True
        self.assertIsNone(self.builder())
        self.reader.assert_not_called()

    def test_short_or_failed_read_disables_both_channels_once(self):
        for result in (b"", b"\0" * 3, bytearray(4), OSError("private diagnostic details")):
            with self.subTest(result=result):
                reader = Mock()
                if isinstance(result, Exception):
                    reader.side_effect = result
                else:
                    reader.return_value = result
                logger = Mock()
                probe = self.module.CompanionMenuStructureProbe(reader=reader, logger=logger,
                                                                clock=lambda: 10.0)
                self.assertIsNone(probe.observe_builder(self.menu, None))
                self.assertIsNone(probe.observe_label(self.menu, self.output))
                self.assertEqual(reader.call_count, 1)
                logger.warning.assert_called_once()
                self.assertNotIn("private diagnostic", repr(logger.mock_calls))

    def test_unterminated_label_is_logged_without_text_then_disables_observation(self):
        self.memory[self.output, 128] = b"x" * 128
        self.assertIsNone(self.label())
        snapshot = self.logger.info.call_args.args[-1]
        self.assertEqual(snapshot[3:], (False, None))
        self.assertTrue(self.probe._stopped)
        calls = self.reader.call_count
        self.assertIsNone(self.builder())
        self.assertEqual(self.reader.call_count, calls)
        self.logger.warning.assert_called_once()

    def test_backward_or_invalid_clock_stops_before_additional_reads(self):
        self.builder()
        for value in (9.0, float("nan"), True):
            with self.subTest(value=value):
                probe = self.module.CompanionMenuStructureProbe(reader=self.reader, logger=Mock(),
                                                                clock=lambda: value)
                probe._channels["builder"]["started"] = 10.0
                next(probe._channels["builder"]["calls"])
                reads = self.reader.call_count
                self.assertIsNone(probe.observe_builder(self.menu, None))
                self.assertEqual(self.reader.call_count, reads)
                self.assertTrue(probe._stopped)

    def test_logger_and_clock_exceptions_preserve_none_return(self):
        self.logger.info.side_effect = RuntimeError("log failure")
        self.logger.warning.side_effect = RuntimeError("warning failure")
        self.assertIsNone(self.builder())
        self.assertTrue(self.probe._stopped)
        probe = self.module.CompanionMenuStructureProbe(reader=self.reader, logger=Mock(),
                                                        clock=Mock(side_effect=RuntimeError("clock")))
        self.assertIsNone(probe.observe_label(self.menu, self.output))
        self.assertTrue(probe._stopped)

    def test_default_reader_binding_is_lazy_and_invalid_input_cannot_bind_it(self):
        with patch.object(self.module, "create_current_process_reader", return_value=self.reader) as factory:
            probe = self.module.CompanionMenuStructureProbe(logger=self.logger, clock=lambda: 10.0)
            factory.assert_not_called()
            self.assertIsNone(probe.observe_builder(None, None))
            factory.assert_not_called()
            probe = self.module.CompanionMenuStructureProbe(logger=self.logger, clock=lambda: 10.0)
            self.assertIsNone(probe.observe_builder(self.menu, None))
            factory.assert_called_once_with()


class WindowsReaderTests(unittest.TestCase):
    def setUp(self):
        self.module = load_probe(enabled=False)
        self.kernel = types.SimpleNamespace(
            GetCurrentProcess=Mock(return_value=0xFFFFFFFFFFFFFFFF),
            ReadProcessMemory=Mock())

    def make_reader(self, success=1, byte_count=None):
        def fake_read(handle, address, destination, size, copied):
            destination.raw = b"a" * size
            ctypes.cast(copied, ctypes.POINTER(ctypes.c_size_t)).contents.value = (
                size if byte_count is None else byte_count)
            return success

        self.kernel.ReadProcessMemory.side_effect = fake_read
        with patch.object(ctypes, "WinDLL", return_value=self.kernel, create=True) as loader:
            reader = self.module.create_current_process_reader()
        loader.assert_called_once_with("kernel32", use_last_error=True)
        return reader

    def test_windows_abi_and_only_explicit_bounded_copy_sizes(self):
        reader = self.make_reader()
        for size in (4, 16, 128):
            self.assertEqual(reader(0x10000, size), b"a" * size)
        self.assertEqual(self.kernel.GetCurrentProcess.argtypes, [])
        self.assertIs(self.kernel.GetCurrentProcess.restype, ctypes.c_void_p)
        self.assertEqual(self.kernel.ReadProcessMemory.argtypes, [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)])
        self.assertIs(self.kernel.ReadProcessMemory.restype, ctypes.c_int)

    def test_failed_and_partial_copies_are_rejected(self):
        for success, byte_count in ((0, 128), (1, 0), (1, 127), (1, 129)):
            with self.subTest(success=success, byte_count=byte_count):
                reader = self.make_reader(success, byte_count)
                with self.assertRaises(OSError):
                    reader(0x10000, 128)

    def test_invalid_read_range_or_size_cannot_reach_windows_api(self):
        reader = self.make_reader()
        for address, size in ((None, 4), (False, 4), (0, 4), (0x10000, 3),
                              (0x10000, 129), (0x10000, True), (0x7FFFFFFFFFFF - 126, 128)):
            with self.subTest(address=address, size=size):
                with self.assertRaises(ValueError):
                    reader(address, size)
        self.kernel.ReadProcessMemory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
