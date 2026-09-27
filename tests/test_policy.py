"""Offline transition tests. No game, mod framework, or process access."""

import importlib.util
from pathlib import Path
import unittest


_spec = importlib.util.spec_from_file_location(
    "auto_pet_policy_under_test",
    Path(__file__).resolve().parents[1] / "src" / "policy.py",
)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
AutoPetPolicy = _module.AutoPetPolicy


class AutoPetPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = AutoPetPolicy()

    def tick(self, now, **overrides):
        state = dict(
            on_foot_in_summon_location=True,
            active_pet=-1,
            native_pending_pet=-1,
            eligible=True,
        )
        state.update(overrides)
        return self.policy.tick(now, **state)

    def arm(self, slot=7, now=0.0):
        self.policy.remember(slot)
        self.policy.eject(now)

    def test_no_choice_does_not_arm(self):
        self.policy.eject(0)
        self.assertIsNone(self.tick(0))
        self.assertIsNone(self.tick(2))

    def test_public_state_tracks_lifecycle_and_is_read_only(self):
        self.assertIsNone(self.policy.last_slot)
        self.assertFalse(self.policy.pending)
        self.policy.remember(3)
        self.assertEqual(self.policy.last_slot, 3)
        self.assertFalse(self.policy.pending)
        self.policy.eject(0)
        self.assertTrue(self.policy.pending)
        self.assertIsNone(self.tick(0))
        self.assertEqual(self.tick(1.5), 3)
        self.assertTrue(self.policy.pending)
        self.assertTrue(self.policy.resolve(True))
        self.assertFalse(self.policy.pending)
        self.assertEqual(self.policy.last_slot, 3)
        for name, value in (("last_slot", 10), ("pending", True), ("pending_slot", 4)):
            with self.subTest(property=name):
                with self.assertRaises(AttributeError):
                    setattr(self.policy, name, value)
        self.policy.reset()
        self.assertIsNone(self.policy.last_slot)
        self.assertFalse(self.policy.pending)

    def test_summons_once_after_observed_stability(self):
        self.arm()
        self.assertIsNone(self.tick(0.2))
        self.assertIsNone(self.tick(1.69))
        self.assertEqual(self.tick(1.7), 7)
        self.assertIsNone(self.tick(3))
        self.policy.resolve(True)
        self.assertIsNone(self.tick(20))

    def test_wait_does_not_start_at_eject_without_observations(self):
        self.arm()
        self.assertIsNone(self.tick(3))
        self.assertEqual(self.tick(4.5), 7)

    def test_forbidden_location_never_summons(self):
        self.arm()
        for now in (0, 2, 5, 11.9, 12, 20):
            self.assertIsNone(self.tick(now, on_foot_in_summon_location=False))
        self.assertIsNone(self.tick(21))
        self.assertEqual(self.tick(23), 7)

    def test_forbidden_location_interrupts_stability(self):
        self.arm()
        self.assertIsNone(self.tick(0))
        self.assertIsNone(self.tick(1, on_foot_in_summon_location=False))
        self.assertIsNone(self.tick(2))
        self.assertIsNone(self.tick(3.49))
        self.assertEqual(self.tick(3.5), 7)

    def test_reentry_cancels_but_next_exit_remembers_choice(self):
        self.arm()
        self.assertIsNone(self.tick(0))
        self.policy.enter_ship()
        self.assertIsNone(self.tick(2))
        self.policy.eject(3)
        self.assertIsNone(self.tick(3))
        self.assertEqual(self.tick(4.5), 7)

    def test_manual_replacement_cancels_old_exit(self):
        self.arm()
        self.assertIsNone(self.tick(0))
        self.policy.remember(12)
        self.assertIsNone(self.tick(2))
        self.policy.eject(3)
        self.assertIsNone(self.tick(3))
        self.assertEqual(self.tick(4.5), 12)

    def test_existing_pet_cancels_even_if_it_disappears(self):
        self.arm()
        self.assertIsNone(self.tick(0, active_pet=2))
        self.assertIsNone(self.tick(2))
        self.assertIsNone(self.tick(4))

    def test_native_pending_pet_cancels_even_before_allowed_location_arrival(self):
        self.arm()
        self.assertIsNone(
            self.tick(0, native_pending_pet=9, on_foot_in_summon_location=False)
        )
        self.assertIsNone(self.tick(2))
        self.assertIsNone(self.tick(4))

    def test_unknown_negative_indices_do_not_summon(self):
        self.arm()
        self.assertIsNone(self.tick(0))
        self.assertIsNone(self.tick(2, active_pet=-2))
        self.assertIsNone(self.tick(3, native_pending_pet=-2))
        self.assertEqual(self.tick(4), 7)

    def test_temporary_ineligibility_waits_without_restart(self):
        self.arm()
        self.assertIsNone(self.tick(0, eligible=False))
        self.assertIsNone(self.tick(2, eligible=False))
        self.assertEqual(self.tick(3), 7)

    def test_default_wait_retains_intent_for_minutes_of_ineligibility(self):
        self.arm()
        self.assertIsNone(self.tick(0, eligible=False))
        self.assertIsNone(self.tick(300, eligible=False))
        self.assertTrue(self.policy.pending)
        self.assertEqual(self.tick(301), 7)

    def test_explicit_optional_expiry_wins_at_deadline(self):
        self.policy = AutoPetPolicy(expiry_seconds=12)
        self.arm()
        self.assertIsNone(self.tick(10.5))
        self.assertIsNone(self.tick(12))
        self.assertIsNone(self.tick(13.5))

    def test_forward_clock_jump_does_not_discard_default_intent(self):
        self.arm()
        self.assertIsNone(self.tick(0))
        self.assertEqual(self.tick(1000), 7)
        self.assertIsNone(self.tick(1002))

    def test_backward_clock_jump_cancels_without_forgetting_choice(self):
        self.arm(now=10)
        self.assertIsNone(self.tick(10))
        self.assertIsNone(self.tick(9))
        self.assertIsNone(self.tick(11))
        self.policy.eject(12)
        self.assertIsNone(self.tick(12))
        self.assertEqual(self.tick(13.5), 7)

    def test_backward_clock_during_eject_does_not_rearm(self):
        self.arm(now=10)
        self.policy.eject(9)
        self.assertIsNone(self.tick(9))
        self.assertIsNone(self.tick(11))

    def test_reset_forgets_choice_pending_and_old_clock(self):
        self.arm(now=100)
        self.assertIsNone(self.tick(100))
        self.policy.reset()
        self.policy.eject(0)
        self.assertIsNone(self.tick(0))
        self.assertIsNone(self.tick(2))
        self.policy.remember(4)
        self.policy.eject(3)
        self.assertIsNone(self.tick(3))
        self.assertEqual(self.tick(4.5), 4)

    def test_duplicate_eject_restarts_observation_window(self):
        self.arm()
        self.assertIsNone(self.tick(0))
        self.policy.eject(1)
        self.assertIsNone(self.tick(1))
        self.assertIsNone(self.tick(1.5))
        self.assertEqual(self.tick(2.5), 7)

    def test_equal_timestamps_do_not_advance_stability(self):
        self.arm()
        for _ in range(4):
            self.assertIsNone(self.tick(0))
        self.assertEqual(self.tick(1.5), 7)

    def test_slot_boundaries(self):
        for slot in (0, 29):
            with self.subTest(slot=slot):
                self.policy.reset()
                self.arm(slot=slot)
                self.assertIsNone(self.tick(0))
                self.assertEqual(self.tick(1.5), slot)

    def test_invalid_slots_leave_previous_valid_pending_request_intact(self):
        self.arm()
        self.assertIsNone(self.tick(0))
        for slot in (-1, 30, 1.0, True, False, "7", None):
            with self.subTest(slot=slot):
                with self.assertRaises(ValueError):
                    self.policy.remember(slot)
        self.assertEqual(self.tick(1.5), 7)

    def test_invalid_tick_time_cancels_request(self):
        for now in (float("nan"), float("inf"), -float("inf"), True, "2", None):
            with self.subTest(now=now):
                self.policy.reset()
                self.arm()
                self.assertIsNone(self.tick(0))
                with self.assertRaises(ValueError):
                    self.tick(now)
                self.assertIsNone(self.tick(2))
                self.assertIsNone(self.tick(4))

    def test_invalid_eject_time_cancels_request(self):
        self.arm()
        with self.assertRaises(ValueError):
            self.policy.eject(float("nan"))
        self.assertIsNone(self.tick(0))
        self.assertIsNone(self.tick(2))

    def test_configuration_validation(self):
        for value in (-1, float("nan"), float("inf"), True, "1.5", None):
            with self.subTest(delay=value):
                with self.assertRaises(ValueError):
                    AutoPetPolicy(delay_seconds=value)
        for value in (0, -1, float("nan"), float("inf"), True, "12"):
            with self.subTest(expiry=value):
                with self.assertRaises(ValueError):
                    AutoPetPolicy(expiry_seconds=value)

    def test_random_exit_arms_without_manual_favorite_and_waits_for_binding(self):
        self.policy.eject(0, random_selection=True)
        self.assertTrue(self.policy.pending)
        self.assertIsNone(self.policy.last_slot)
        self.assertIsNone(self.tick(0))
        self.assertIsNone(self.tick(300))
        self.assertTrue(self.policy.select_for_exit(9))
        self.assertEqual(self.tick(301), 9)
        self.assertIsNone(self.policy.last_slot)

    def test_random_binding_preserves_manual_favorite_stability_and_exit_time(self):
        self.policy.remember(3)
        self.policy.eject(10, random_selection=True)
        self.assertIsNone(self.tick(10))
        self.policy.select_for_exit(8)
        self.assertEqual(self.tick(11.5), 8)
        self.assertEqual(self.policy.last_slot, 3)
        self.assertEqual(self.policy._ejected_at, 10)

    def test_rejected_queue_retains_choice_until_accepted_without_duplicate_inflight(self):
        self.arm()
        self.tick(0)
        self.assertEqual(self.tick(2), 7)
        self.assertIsNone(self.tick(3))
        self.assertTrue(self.policy.resolve(False))
        self.assertEqual(self.policy.pending_slot, 7)
        self.assertEqual(self.tick(4), 7)
        self.assertTrue(self.policy.resolve(True))
        self.assertFalse(self.policy.pending)
        self.assertIsNone(self.tick(300))

    def test_random_binding_cannot_reroll_or_bind_inactive_exit(self):
        self.assertFalse(self.policy.select_for_exit(2))
        self.policy.eject(0, random_selection=True)
        self.policy.select_for_exit(2)
        with self.assertRaises(ValueError):
            self.policy.select_for_exit(3)
        self.assertEqual(self.policy.pending_slot, 2)

    def test_invalid_random_binding_does_not_change_pending_choice(self):
        self.policy.eject(0, random_selection=True)
        for slot in (-1, 30, True, 1.0, None):
            with self.subTest(slot=slot), self.assertRaises(ValueError):
                self.policy.select_for_exit(slot)
        self.assertTrue(self.policy.pending)
        self.assertIsNone(self.policy.pending_slot)

    def test_manual_selection_cancels_random_inflight_and_replaces_favorite(self):
        self.policy.eject(0, random_selection=True)
        self.policy.select_for_exit(4)
        self.tick(0)
        self.assertEqual(self.tick(2), 4)
        self.policy.remember(6)
        self.assertFalse(self.policy.resolve(False))
        self.assertFalse(self.policy.pending)
        self.assertEqual(self.policy.last_slot, 6)

    def test_resolve_validation_and_random_mode_validation_preserve_state(self):
        self.arm()
        for value in (None, 1, "random"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.policy.eject(1, random_selection=value)
            with self.subTest(resolve=value), self.assertRaises(ValueError):
                self.policy.resolve(value)
        self.assertTrue(self.policy.pending)

    def test_reset_clears_favorite_random_choice_and_inflight(self):
        self.policy.remember(3)
        self.policy.eject(0, random_selection=True)
        self.policy.select_for_exit(8)
        self.tick(0); self.tick(2)
        self.policy.reset()
        self.assertFalse(self.policy.pending)
        self.assertIsNone(self.policy.pending_slot)
        self.assertIsNone(self.policy.last_slot)
        self.assertFalse(self.policy.resolve(True))

    def test_custom_zero_delay_still_needs_eligible_location_observation(self):
        self.policy = AutoPetPolicy(delay_seconds=0, expiry_seconds=1)
        self.arm()
        self.assertIsNone(self.tick(0, on_foot_in_summon_location=False))
        self.assertIsNone(self.tick(0.1, eligible=False))
        self.assertEqual(self.tick(0.2), 7)
        self.assertIsNone(self.tick(0.3))


if __name__ == "__main__":
    unittest.main()
