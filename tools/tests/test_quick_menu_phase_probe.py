"""Offline phase-machine tests using fake framework and owned byte copies."""

import ctypes
import hashlib
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


SOURCE = Path(__file__).resolve().parents[1] / "quick_menu_phase_probe.py"
EXPECTED_HASH = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"


def load_probe(*, enabled=True, injected=True, base=1, framework="0.2.4", digest=EXPECTED_HASH):
    source = SOURCE.read_text(encoding="utf-8")
    if enabled:
        if source.count("PROBE_ENABLED = False") != 1:
            raise AssertionError("Unique disabled-source marker required")
        source = source.replace("PROBE_ENABLED = False", "PROBE_ENABLED = True", 1)
    events = []
    declarations = []

    class FakeMod:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            events.append(("class", cls._disabled))

    class FakeNative:
        def __init__(self, function, offset):
            self.function = function
            self.offset = offset
            declarations.append(self)

        def before(self, callback):
            callback._test_time = "before"
            callback._test_offset = self.offset
            return callback

        def after(self, callback):
            callback._test_time = "after"
            callback._test_offset = self.offset
            return callback

        def __call__(self, *args, **kwargs):
            raise AssertionError("No native game function may be invoked")

    internal = types.ModuleType("pymhf.core._internal")
    internal.IS_INJECTED = injected
    internal.BASE_ADDRESS = base
    internal.BINARY_PATH = "owned-test-bytes-only.exe"
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
        return framework

    def fake_open(path, mode="r", *args, **kwargs):
        events.append(("open", str(path)))
        if str(path) != internal.BINARY_PATH or mode != "rb":
            raise AssertionError("Unexpected file access")
        return io.BytesIO(b"owned fake executable")

    module = types.ModuleType("quick_menu_phase_probe_under_test")
    module.__file__ = str(SOURCE)
    with patch.dict(sys.modules, {"pymhf": pymhf, "pymhf.core": core,
                                 "pymhf.core._internal": internal, "pymhf.core.hooking": hooking}), patch(
        "importlib.metadata.version", side_effect=fake_version
    ), patch.object(Path, "open", fake_open), patch.object(
        hashlib, "file_digest", return_value=Mock(hexdigest=lambda: digest)
    ), patch.object(ctypes, "WinDLL", side_effect=AssertionError("No import-time Windows calls"), create=True):
        exec(compile(source, str(SOURCE), "exec"), module.__dict__)
    module.test_events = events
    module.test_declarations = declarations
    return module


class GuardTests(unittest.TestCase):
    def test_disabled_uninjected_and_invalid_base_do_not_open_binary(self):
        for settings in ({"enabled": False}, {"injected": False}, {"base": 0}):
            with self.subTest(settings=settings):
                module = load_probe(**settings)
                self.assertEqual(module.test_events, [("class", True)])

    def test_wrong_framework_or_hash_disables_before_registration(self):
        for settings in ({"framework": "0.2.3"}, {"digest": "wrong"}):
            with self.subTest(settings=settings):
                module = load_probe(**settings)
                self.assertTrue(module.CompanionMenuPhaseProbe._disabled)
                self.assertEqual(module.test_events[-1], ("class", True))

    def test_three_exact_abis_four_callbacks_and_one_mod_class(self):
        module = load_probe()
        self.assertFalse(module.CompanionMenuPhaseProbe._disabled)
        declarations = module.test_declarations
        self.assertEqual([item.offset for item in declarations], [0x151D200, 0x1530C00, 0x1525600])
        self.assertEqual(declarations[0].function.__annotations__, {
            "menu": ctypes.c_void_p, "elapsed": ctypes.c_float,
            "render": ctypes.c_void_p, "return": None})
        self.assertEqual(declarations[1].function.__annotations__, {
            "menu": ctypes.c_void_p, "buffer1": ctypes.c_void_p,
            "buffer2": ctypes.c_void_p, "return": None})
        self.assertEqual(declarations[2].function.__annotations__, {
            "menu": ctypes.c_void_p, "render": ctypes.c_void_p, "return": None})
        for name, timing, offset in (
            ("before_update", "before", 0x151D200), ("after_update", "after", 0x151D200),
            ("after_controls", "after", 0x1530C00), ("before_tail", "before", 0x1525600)):
            callback = getattr(module.CompanionMenuPhaseProbe, name)
            self.assertEqual((callback._test_time, callback._test_offset), (timing, offset))
        classes = [obj for obj in module.__dict__.values()
                   if isinstance(obj, type) and obj.__module__ == module.__name__]
        self.assertEqual(classes, [module.CompanionMenuPhaseProbe])


class PhaseFixture(unittest.TestCase):
    def setUp(self):
        self.module = load_probe()
        self.menu = 0x1110000
        self.render = 0x2220000
        self.memory = {(self.menu + 0xA050, 4): (1).to_bytes(4, "little", signed=True)}
        for level in range(3):
            self.set_vector(level)
        self.now = 10.0
        self.thread = 123456789
        self.logger = Mock()
        self.reads = []

        def reader(address, size):
            self.reads.append((address, size))
            return self.memory[address, size]

        self.reader = Mock(side_effect=reader)
        self.probe = self.module.CompanionMenuPhaseProbe(
            reader=self.reader, logger=self.logger, clock=lambda: self.now,
            thread_id=lambda: self.thread)

    def set_vector(self, level, *, capacity=4, item_count=2, selected=1, action=45, pointer=None):
        if pointer is None:
            pointer = 0x3330000 + level * 0x10000
        self.memory[self.menu + 0xA058 + level * 16, 16] = (
            capacity.to_bytes(4, "little") + item_count.to_bytes(4, "little")
            + pointer.to_bytes(8, "little"))
        self.memory[self.menu + 0xA088 + level * 4, 4] = selected.to_bytes(4, "little", signed=True)
        if 0 <= selected < item_count and pointer >= 0x10000:
            self.memory[pointer + selected * 0xE0 + 4, 4] = action.to_bytes(4, "little", signed=True)

    def enter(self):
        return self.probe.before_update(self.menu, 0.016, self.render)

    def controls(self):
        return self.probe.after_controls(self.menu, self.render, self.render + 0x100)

    def tail(self):
        return self.probe.before_tail(self.menu, self.render)

    def exit(self):
        return self.probe.after_update(self.menu, 0.016, self.render)

    def complete(self):
        for callback in (self.enter, self.controls, self.tail, self.exit):
            self.assertIsNone(callback())

    def assert_stopped(self, reason):
        self.assertTrue(self.probe._stopped)
        self.assertEqual(self.probe._counts[reason], 1)
        self.assertEqual(self.probe._invocations, {})
        self.assertEqual(self.probe._thread_ordinals, {})


class SequenceTests(PhaseFixture):
    def test_complete_sequence_preserves_memory_and_clears_all_pointer_records(self):
        before = dict(self.memory)
        self.complete()
        self.assertFalse(self.probe._stopped)
        self.assertEqual(self.memory, before)
        self.assertEqual(self.reader.call_count, 30)
        self.assertEqual(self.probe._counts["completed"], 1)
        self.assertEqual(self.probe._counts["samples"], 1)
        self.assertEqual(self.probe._invocations, {})
        logged = self.logger.info.call_args.args
        self.assertEqual(logged[1], 1)
        self.assertEqual(logged[5:7], (True, False))
        self.assertNotIn(str(self.menu), repr(self.logger.mock_calls))
        self.assertNotIn(str(self.thread), repr(self.logger.mock_calls))
        self.assertNotIn(str(0x3330000), repr(self.probe._last_signature))

    def test_early_exit_is_skipped_and_does_not_consume_sample_budget(self):
        for _ in range(100):
            self.assertIsNone(self.enter())
            self.assertIsNone(self.exit())
            self.now += 1.0
        self.assertFalse(self.probe._stopped)
        self.assertEqual(self.probe._counts["skipped"], 100)
        self.assertEqual(self.probe._counts["samples"], 0)
        self.reader.assert_not_called()
        self.assertIsNone(self.probe._last_sample_started)
        self.complete()
        self.assertEqual(self.probe._counts["samples"], 1)

    def test_tail_to_exit_selection_change_is_legitimate_and_separately_reported(self):
        self.enter()
        self.controls()
        self.tail()
        self.set_vector(1, selected=0, action=46)
        self.assertIsNone(self.exit())
        self.assertFalse(self.probe._stopped)
        self.assertEqual(self.probe._counts["interval_changes"], 0)
        self.assertEqual(self.probe._counts["post_tail_changes"], 1)
        self.assertEqual(self.logger.info.call_args.args[5:7], (True, True))

    def test_controls_to_tail_storage_change_is_reported_without_addresses(self):
        self.enter()
        self.controls()
        self.set_vector(1, pointer=0x7770000)
        self.tail()
        self.exit()
        self.assertFalse(self.probe._stopped)
        self.assertEqual(self.probe._counts["interval_changes"], 1)
        self.assertEqual(self.logger.info.call_args.args[-2], (True, False, True))
        self.assertNotIn(str(0x7770000), repr(self.logger.mock_calls))
        self.assertNotIn(str(0x7770000), repr(self.probe._last_signature))

    def test_missing_tail_stops_without_counting_a_complete_invocation(self):
        self.enter()
        self.controls()
        self.assertIsNone(self.exit())
        self.assert_stopped("missing")
        self.assertEqual(self.probe._counts["completed"], 0)
        self.assertEqual(self.probe._counts["samples"], 0)

    def test_tail_without_controls_is_missing_phase(self):
        self.enter()
        self.assertIsNone(self.tail())
        self.assert_stopped("missing")
        self.reader.assert_not_called()

    def test_duplicate_controls_or_tail_stops_observation(self):
        for duplicate in ("controls", "tail"):
            with self.subTest(duplicate=duplicate):
                self.setUp()
                self.enter()
                self.controls()
                if duplicate == "tail":
                    self.tail()
                    self.tail()
                else:
                    self.controls()
                self.assert_stopped("duplicate")

    def test_unscoped_controls_are_reported_as_unmatched_not_assumed_impossible(self):
        self.assertIsNone(self.controls())
        self.assert_stopped("unmatched")
        self.reader.assert_not_called()

    def test_wrong_menu_render_or_secondary_identity_stops_without_reads(self):
        for kind in ("menu", "render", "secondary"):
            with self.subTest(kind=kind):
                self.setUp()
                self.enter()
                menu = self.menu + (0x1000 if kind == "menu" else 0)
                render = self.render + (0x1000 if kind == "render" else 0)
                secondary = render + (0x104 if kind == "secondary" else 0x100)
                self.assertIsNone(self.probe.after_controls(menu, render, secondary))
                self.assert_stopped("identity_mismatch")
                self.reader.assert_not_called()

    def test_nested_update_stops_and_invalidates_outer_completion(self):
        self.enter()
        self.controls()
        self.assertIsNone(self.enter())
        self.assert_stopped("nested")
        reads = self.reader.call_count
        self.tail()
        self.exit()
        self.assertEqual(self.reader.call_count, reads)
        self.assertEqual(self.probe._counts["completed"], 0)

    def test_overlapping_foreign_thread_is_concurrent_not_balanced(self):
        self.enter()
        self.thread = 987654321
        self.assertIsNone(self.controls())
        self.assert_stopped("concurrent")
        self.reader.assert_not_called()

    def test_nonoverlapping_threads_receive_bounded_anonymous_ordinals(self):
        self.complete()
        self.now += 0.5
        self.thread = 987654321
        self.set_vector(0, selected=0)
        self.complete()
        self.assertFalse(self.probe._stopped)
        self.assertEqual(self.logger.info.call_args.args[1], 2)
        self.module.MAX_THREADS = 2
        self.thread = 999
        self.enter()
        self.assert_stopped("thread_limit")

    def test_contention_stops_without_waiting_or_counting_later_completion(self):
        self.enter()
        self.probe._observation_lock.acquire()
        try:
            self.assertIsNone(self.controls())
            self.assert_stopped("contention")
        finally:
            self.probe._observation_lock.release()
        self.tail()
        self.exit()
        self.reader.assert_not_called()
        self.assertEqual(self.probe._counts["completed"], 0)

    def test_contention_during_copy_stops_remaining_reads_and_clears_records(self):
        self.enter()

        def reentrant_reader(address, size):
            self.assertIsNone(self.tail())
            return self.memory[address, size]

        self.reader.side_effect = reentrant_reader
        self.assertIsNone(self.controls())
        self.assert_stopped("contention")
        self.assertEqual(self.reader.call_count, 1)
        self.assertEqual(self.probe._counts["completed"], 0)

    def test_contender_during_enter_clock_or_thread_lookup_cannot_retain_identities(self):
        for operation in ("clock", "thread"):
            with self.subTest(operation=operation):
                self.setUp()

                def interrupted_clock():
                    self.assertIsNone(self.tail())
                    return self.now

                def interrupted_thread():
                    self.assertIsNone(self.tail())
                    return self.thread

                if operation == "clock":
                    self.probe._clock = interrupted_clock
                else:
                    self.probe._thread_id = interrupted_thread
                self.assertIsNone(self.enter())
                self.assert_stopped("contention")
                self.assertEqual(self.probe._counts["updates"], 0)
                self.assertEqual(self.probe._counts["completed"], 0)
                self.reader.assert_not_called()

    def test_contender_during_exit_clock_cannot_report_completion(self):
        self.enter()
        self.controls()
        self.tail()
        reads = self.reader.call_count

        def interrupted_clock():
            self.assertIsNone(self.controls())
            return self.now

        self.probe._clock = interrupted_clock
        self.assertIsNone(self.exit())
        self.assert_stopped("contention")
        self.assertEqual(self.probe._counts["completed"], 0)
        self.assertEqual(self.probe._counts["samples"], 0)
        self.assertEqual(self.reader.call_count, reads)

    def test_clock_is_sampled_after_lock_acquisition_not_before_preemption(self):
        real_lock = self.probe._observation_lock
        proxy = Mock()

        def interleaved_acquire(*, blocking):
            self.assertFalse(blocking)
            self.probe._observation_lock = real_lock
            self.now = 11.0
            self.complete()
            self.probe._observation_lock = proxy
            return real_lock.acquire(blocking=False)

        proxy.acquire.side_effect = interleaved_acquire
        proxy.release.side_effect = real_lock.release
        self.probe._observation_lock = proxy
        self.now = 10.5
        self.assertIsNone(self.enter())
        self.probe._observation_lock = real_lock
        self.controls()
        self.tail()
        self.exit()
        self.assertFalse(self.probe._stopped)
        self.assertEqual(self.probe._counts["completed"], 2)


class BudgetAndFailureTests(PhaseFixture):
    def test_unsampled_updates_still_enforce_phase_order_without_reading(self):
        self.complete()
        reads = self.reader.call_count
        self.now += 0.1
        self.enter()
        self.controls()
        self.assertIsNone(self.exit())
        self.assert_stopped("missing")
        self.assertEqual(self.reader.call_count, reads)

    def test_sampling_is_four_hertz_and_identical_snapshots_use_one_detail(self):
        self.complete()
        for _ in range(50):
            self.complete()
        self.assertEqual(self.reader.call_count, 30)
        self.assertEqual(self.probe._counts["completed"], 51)
        for _ in range(50):
            self.now += 0.25
            self.complete()
        self.assertEqual(self.probe._counts["samples"], 51)
        self.assertEqual(self.probe._counts["details"], 1)
        self.logger.info.assert_called_once()

    def test_complete_sample_limit_clears_records_and_stops_further_reads(self):
        self.module.MAX_SAMPLES = 2
        for _ in range(5):
            self.complete()
            self.now += 0.25
        self.assertEqual(self.probe._counts["samples"], 2)
        self.assertEqual(self.reader.call_count, 60)
        self.assertEqual(self.probe._invocations, {})
        self.assertTrue(self.probe._stopped)
        self.assertEqual(self.logger.info.call_args.args[1], "sample_limit")

    def test_detail_limit_deduplicates_stable_data_then_stops(self):
        self.module.MAX_DETAILS = 2
        self.complete()
        self.now += 0.25
        self.complete()
        self.assertFalse(self.probe._stopped)
        self.now += 0.25
        self.set_vector(0, selected=0)
        self.complete()
        self.assertTrue(self.probe._stopped)
        self.assertEqual(self.probe._counts["samples"], 3)
        self.assertEqual(self.probe._counts["details"], 2)
        self.assertEqual(self.logger.info.call_args.args[1], "detail_limit")

    def test_invocation_budget_finishes_current_early_exit_without_false_sample(self):
        self.module.MAX_INVOCATIONS = 2
        self.enter()
        self.exit()
        self.enter()
        self.assertFalse(self.probe._stopped)
        self.exit()
        self.assertTrue(self.probe._stopped)
        self.assertEqual(self.probe._counts["skipped"], 2)
        self.assertEqual(self.probe._counts["samples"], 0)
        self.assertEqual(self.logger.info.call_args.args[1], "invocation_limit")

    def test_read_error_disables_once_and_never_reports_complete(self):
        self.enter()
        self.reader.side_effect = OSError("private pointer detail must not be logged")
        self.assertIsNone(self.controls())
        self.assert_stopped("read_error")
        self.tail()
        self.exit()
        self.assertEqual(self.reader.call_count, 1)
        self.assertEqual(self.probe._counts["completed"], 0)
        self.assertNotIn("private pointer", repr(self.logger.mock_calls))

    def test_short_unowned_and_invalid_depth_copies_fail_closed(self):
        for value in (b"\0" * 3, bytearray(4), (3).to_bytes(4, "little")):
            with self.subTest(value=value):
                self.setUp()
                self.enter()
                self.reader.return_value = value
                self.reader.side_effect = None
                self.controls()
                self.assert_stopped("read_error")
                self.assertEqual(self.reader.call_count, 1)

    def test_runtime_loss_clears_active_records_without_reading(self):
        self.enter()
        self.module._internal.IS_INJECTED = False
        self.assertIsNone(self.controls())
        self.assertTrue(self.probe._stopped)
        self.assertEqual(self.probe._invocations, {})
        self.reader.assert_not_called()

    def test_disabled_callback_does_not_enter_phase_machine(self):
        self.probe._disabled = True
        self.complete()
        self.assertEqual(self.probe._counts["updates"], 0)
        self.reader.assert_not_called()

    def test_clock_argument_and_logger_failures_do_not_escape(self):
        self.enter()
        self.now = 9.0
        self.assertIsNone(self.controls())
        self.assert_stopped("clock_error")
        self.setUp()
        self.assertIsNone(self.probe.before_update(None, 0.016, self.render))
        self.assert_stopped("invalid_argument")
        self.setUp()
        self.logger.info.side_effect = RuntimeError("logger unavailable")
        self.complete()
        self.assert_stopped("logging_error")

    def test_reader_is_lazily_bound_only_when_controls_are_sampled(self):
        with patch.object(self.module, "create_current_process_reader", return_value=self.reader) as factory:
            self.probe = self.module.CompanionMenuPhaseProbe(logger=self.logger, clock=lambda: self.now,
                                                            thread_id=lambda: self.thread)
            self.enter()
            self.exit()
            factory.assert_not_called()
            self.complete()
            factory.assert_called_once_with()


class BoundedCopyTests(PhaseFixture):
    def test_empty_and_stale_selection_skip_items_without_oob_reads(self):
        self.set_vector(0, item_count=0, selected=-1, pointer=0)
        self.set_vector(1, selected=2)
        snapshot, storage = self.module.inspect_menu(self.reader, self.menu)
        self.assertEqual(snapshot[1][0][4:], ("empty", None))
        self.assertEqual(snapshot[1][1][4:], ("stale_selection", None))
        self.assertEqual(len(self.reads), 8)

    def test_invalid_capacity_count_pointer_or_action_rejects_bounded_copy(self):
        for settings in ({"capacity": 257}, {"capacity": 1, "item_count": 2},
                         {"pointer": 0}, {"pointer": 0x7FFFFFFFFFFF - 0xE0}, {"action": 67}):
            with self.subTest(settings=settings):
                self.setUp()
                self.set_vector(0, **settings)
                with self.assertRaises(ValueError):
                    self.module.inspect_menu(self.reader, self.menu)
                self.assertTrue(all(size in (4, 16) for _, size in self.reads))

    def test_windows_reader_uses_explicit_abi_and_exact_count(self):
        kernel = types.SimpleNamespace(GetCurrentProcess=Mock(return_value=0xFFFFFFFFFFFFFFFF),
                                       ReadProcessMemory=Mock())

        def read(handle, address, destination, size, copied):
            destination.raw = b"x" * size
            ctypes.cast(copied, ctypes.POINTER(ctypes.c_size_t)).contents.value = size
            return 1

        kernel.ReadProcessMemory.side_effect = read
        with patch.object(ctypes, "WinDLL", return_value=kernel, create=True):
            reader = self.module.create_current_process_reader()
        self.assertEqual(reader(0x10000, 16), b"x" * 16)
        self.assertEqual(kernel.ReadProcessMemory.argtypes, [ctypes.c_void_p, ctypes.c_void_p,
                         ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)])
        self.assertIs(kernel.ReadProcessMemory.restype, ctypes.c_int)
        calls = kernel.ReadProcessMemory.call_count
        for address, size in ((None, 4), (0x10000, 128), (0x7FFFFFFFFFFF, 4)):
            with self.subTest(address=address, size=size), self.assertRaises(ValueError):
                reader(address, size)
        self.assertEqual(kernel.ReadProcessMemory.call_count, calls)
        kernel.ReadProcessMemory.side_effect = lambda *args: 1
        with self.assertRaises(OSError):
            reader(0x10000, 4)
        kernel.ReadProcessMemory.side_effect = lambda *args: 0
        with self.assertRaises(OSError):
            reader(0x10000, 4)


if __name__ == "__main__":
    unittest.main()
