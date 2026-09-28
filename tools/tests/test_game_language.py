"""Language diagnostics using synthetic scalar bytes and existing fake UI only."""

from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import Mock, patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import game_language as gl
from test_quick_menu_order_trial import load_trial
from test_quick_menu_settings_trial import SettingsFixture


BASE = 0x140000000


def records(*, guard=-2147483600, vtable=None, region=0, loaded=1):
    pointer = BASE + gl.VTABLE_RVA if vtable is None else vtable
    return (struct.pack("<iQi", guard, pointer, region), bytes((loaded,)))


def reader_for(first=None, second=None):
    first = records() if first is None else first
    second = first if second is None else second
    return Mock(side_effect=(*first, *second))


class LanguageReaderTests(unittest.TestCase):
    def test_exact_four_bounded_reads_return_only_copied_language_metadata(self):
        reader = reader_for(records(region=12))
        observation = gl.read_language(reader, BASE)
        self.assertEqual(observation, gl.LanguageObservation("initialized_load_seen", 12, "JAPANESE"))
        self.assertEqual(reader.call_args_list, [
            ((BASE + gl.GUARD_RVA, 16),), ((BASE + gl.LOAD_COMPLETE_RVA, 1),),
            ((BASE + gl.GUARD_RVA, 16),), ((BASE + gl.LOAD_COMPLETE_RVA, 1),),
        ])
        self.assertEqual(set(vars(observation)), {"status", "region", "native_language"})

    def test_all_seventeen_verified_regions_remain_native_names_not_catalog_aliases(self):
        expected = ("ENGLISH", "USENGLISH", "FRENCH", "ITALIAN", "GERMAN", "SPANISH", "RUSSIAN",
                    "POLISH", "DUTCH", "PORTUGUESE", "LATINAMERICANSPANISH", "BRAZILIANPORTUGUESE",
                    "JAPANESE", "TRADITIONALCHINESE", "SIMPLIFIEDCHINESE", "TENCENTCHINESE", "KOREAN")
        for region, name in enumerate(expected):
            self.assertEqual(gl.read_language(reader_for(records(region=region)), BASE),
                             gl.LanguageObservation("initialized_load_seen", region, name))

    def test_zero_fill_and_in_progress_constructor_never_mean_english(self):
        for guard in (0, -1, 1, 2147483647):
            result = gl.read_language(reader_for(records(guard=guard)), BASE)
            self.assertEqual(result, gl.LanguageObservation("not_initialized"))

    def test_sentinel_and_out_of_range_regions_are_not_a_language(self):
        for region in (-2147483648, -1, 17, 18, 2147483647):
            self.assertEqual(gl.read_language(reader_for(records(region=region)), BASE),
                             gl.LanguageObservation("unconfigured"))

    def test_base_class_teardown_and_unexpected_vtable_are_rejected_without_pointer_reads(self):
        for pointer in (0, BASE + 0x350A7B0, BASE + gl.VTABLE_RVA + 8):
            reader = reader_for(records(vtable=pointer))
            self.assertEqual(gl.read_language(reader, BASE), gl.LanguageObservation("unexpected_vtable"))
            self.assertEqual(reader.call_count, 4)

    def test_load_completion_must_be_exactly_one(self):
        for value in (0, 2, 255):
            self.assertEqual(gl.read_language(reader_for(records(loaded=value)), BASE),
                             gl.LanguageObservation("tables_not_ready"))

    def test_any_changed_guard_region_vtable_or_load_byte_is_unstable(self):
        for changed in (records(guard=-2147483599), records(region=2), records(vtable=0), records(loaded=0)):
            self.assertEqual(gl.read_language(reader_for(records(), changed), BASE),
                             gl.LanguageObservation("unstable"))

    def test_failed_or_partial_reads_are_not_interpreted(self):
        for response in (b"", bytes(15), bytearray(16), None, bytes(17)):
            with self.assertRaises(ValueError):
                gl.read_language(Mock(return_value=response), BASE)
        with self.assertRaises(OSError):
            gl.read_language(Mock(side_effect=OSError("owned read failure")), BASE)

    def test_invalid_base_is_rejected_before_reading(self):
        for base in (None, 0, -1, True, 1.5, 1 << 63, 0x7FFFFFFFFFFF):
            reader = Mock()
            with self.assertRaises(ValueError):
                gl.read_language(reader, base)
            reader.assert_not_called()


class LanguageObserverTests(unittest.TestCase):
    def test_repeated_samples_are_paced_and_identical_results_deduplicated(self):
        reader = Mock(side_effect=(*records(), *records()) * 2)
        report = Mock()
        observer = gl.LanguageObserver(reader, BASE, report)
        for now in (0, 0.1, 0.49, 0.5, 0.6):
            observer.sample(now)
        self.assertEqual(reader.call_count, 8)
        report.assert_called_once_with(gl.LanguageObservation("initialized_load_seen", 0, "ENGLISH"))

    def test_read_failure_stops_only_diagnostic_and_reports_once(self):
        reader, report = Mock(side_effect=OSError("owned failure")), Mock()
        observer = gl.LanguageObserver(reader, BASE, report)
        observer.sample(0)
        observer.sample(10)
        reader.assert_called_once()
        report.assert_called_once_with(gl.LanguageObservation("read_failed"))

    def test_report_exception_is_contained_and_prevents_more_work(self):
        reader = reader_for()
        observer = gl.LanguageObserver(reader, BASE, Mock(side_effect=RuntimeError("owned logger failure")))
        observer.sample(0)
        observer.sample(10)
        self.assertEqual(reader.call_count, 4)

    def test_transition_reports_have_a_hard_cap_and_end_sampling(self):
        data = []
        for region in range(10):
            data.extend((*records(region=region), *records(region=region)))
        reader, report = Mock(side_effect=data), Mock()
        observer = gl.LanguageObserver(reader, BASE, report)
        for now in range(20):
            observer.sample(now)
        self.assertEqual(reader.call_count, 36)
        self.assertEqual(report.call_count, 9)
        self.assertEqual(report.call_args.args, (gl.LanguageObservation("limit_reached"),))

    def test_busy_lock_and_invalid_time_do_not_read_native_memory(self):
        reader = Mock()
        observer = gl.LanguageObserver(reader, BASE, Mock())
        observer._lock.acquire()
        observer.sample(1)
        observer._lock.release()
        reader.assert_not_called()
        for value in (float("nan"), float("inf"), -1, True, "1"):
            gl.LanguageObserver(reader, BASE, Mock()).sample(value)
        reader.assert_not_called()


class LanguageAdapterTests(SettingsFixture):
    def test_optional_observer_sees_own_caption_without_changing_english_or_preferences(self):
        self.prepare_child()
        observer = Mock()
        self.trial._language = observer
        self.expected_label(b"Automatic summoning: ON")
        observer.sample.assert_called_once()
        self.assert_no_request()

    def test_observer_exception_preserves_label_and_working_menu(self):
        self.prepare_child()
        observer = Mock()
        observer.sample.side_effect = RuntimeError("owned observer failure")
        self.trial._language = observer
        self.expected_label(b"Automatic summoning: ON")
        self.assertIsNone(self.trial._language)
        self.assert_no_request()

    def test_non_cas_caption_does_not_sample_language(self):
        self.prepare_parent()
        self.set_integer(self.module.item.SELECTIONS_OFFSET + 4, 1)
        observer = Mock()
        self.trial._language = observer
        self.assertIsNone(self.label())
        observer.sample.assert_not_called()

    def test_invalidation_during_observation_prevents_the_caption_write(self):
        self.prepare_child()
        observer = Mock()
        observer.sample.side_effect = lambda _now: self.trial._stop("owned diagnostic boundary invalidation")
        self.trial._language = observer
        self.trial._writer.reset_mock()
        self.assertIsNone(self.label())
        self.trial._writer.assert_not_called()
        self.assertTrue(self.trial._stopped)
        self.assert_no_request()


class LanguageMetadataTests(unittest.TestCase):
    def test_optional_constructor_failure_preserves_the_preference_bridge_and_menu(self):
        module = load_trial(enabled=True, settings_enabled=True, language_observation=True)
        bridge = Mock()
        with patch.object(module, "current_process_io", return_value=(Mock(), Mock(), Mock())), \
                patch.object(module, "native_adapters", return_value=(Mock(), Mock(), Mock())), \
                patch.object(module, "ensure_guard", return_value=Mock()), \
                patch.object(module, "LanguageObserver", side_effect=RuntimeError("owned construction failure")), \
                patch.object(module, "PreferenceBridge", return_value=bridge):
            trial = module.CompanionMenuOrderTrial()
        self.assertFalse(trial._stopped)
        self.assertIs(trial._preferences, bridge)
        self.assertIsNone(trial._language)

    def test_opt_in_keeps_same_hooks_and_unknown_build_initializes_no_reader(self):
        plain = load_trial(settings_enabled=True, extended_settings=True, custom_icon=True)
        observed = load_trial(settings_enabled=True, extended_settings=True, custom_icon=True, language_observation=True)
        self.assertEqual([entry.offset for entry in plain.test_declarations],
                         [entry.offset for entry in observed.test_declarations])
        self.assertEqual(observed.CompanionMenuOrderTrial._version, "0.8.4-language-observation")
        with patch.object(observed, "current_process_io") as io, patch.object(observed, "LanguageObserver") as factory:
            trial = observed.CompanionMenuOrderTrial()
        io.assert_not_called()
        factory.assert_not_called()
        self.assertIsNone(trial._language)


if __name__ == "__main__":
    unittest.main()
