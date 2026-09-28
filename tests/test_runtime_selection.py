"""Habitat and rotation integration against owned ctypes buffers only."""
import ctypes
import json
import os
import random
import tempfile
import unittest
from unittest.mock import Mock, patch

import test_runtime as legacy


class RuntimeSelectionTests(legacy.RuntimeFixture):
    set_planet = legacy.RuntimeBiomeTests.set_planet
    pet_biome = legacy.RuntimeBiomeTests.pet_biome

    def setUp(self):
        super().setUp()
        self.mod.selector = self.module.CompanionSelector(rng=random.Random(42))
        self.mod.selection_mode_value = "by_habitat"
        self.mod.rotate_companions_value = True

    def pet(self, slot, biome, identity=None):
        self.set_pet(slot, self.seed(slot + 100) if identity is None else identity)
        self.pet_biome(slot, biome)

    def opportunity(self, now=1):
        self.set_pending(-1)
        self.set_active(-1)
        self.exit(now)
        self.probe(now)
        self.probe(now + 1.5)

    def test_fresh_defaults_are_habitat_and_rotation_without_writes(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"LOCALAPPDATA": folder}):
            mod = self.module.CompanionAutoSummon()
            self.assertEqual(mod.selection_mode_value, "by_habitat")
            self.assertTrue(mod.rotate_companions_value)
            self.assertFalse(mod.settings_store.path.exists())

    def test_existing_schema3_keeps_mode_and_draw_behavior(self):
        self.settings_path.parent.mkdir(exist_ok=True)
        raw = json.dumps({"schema": 3, "enabled": False, "locations": [2],
                          "selection_mode": "random", "prefer_same_biome": False})
        self.settings_path.write_text(raw)
        self.restart()
        self.assertEqual(self.mod.selection_mode_value, "random")
        self.assertFalse(self.mod.rotate_companions_value)
        self.assertFalse(self.mod.auto_enabled)
        self.assertEqual(self.settings_path.read_text(), raw)

    def test_lava_uses_scorched_when_exact_missing_and_excludes_frozen(self):
        self.set_planet(13)
        self.pet(1, 2)
        self.pet(2, 4)
        self.opportunity()
        self.assertEqual(self.queue_calls, [(self.player, 1)])
        self.assertIsNone(self.mod.policy.last_slot)
        self.assertFalse(self.state_path.exists())

    def test_unknown_planet_waits_then_uses_resolved_habitat(self):
        self.pet(1, 2)
        self.opportunity()
        self.assertEqual(self.queue_calls, [])
        self.assertTrue(self.mod.policy.pending)
        self.set_planet(13)
        self.probe(4)
        self.assertEqual(self.queue_calls, [(self.player, 1)])

    def test_unsuitable_owned_pool_skips_once_instead_of_summoning_frozen_on_lava(self):
        self.set_planet(13)
        self.pet(1, 4)
        self.opportunity()
        self.assertEqual(self.queue_calls, [])
        self.assertFalse(self.mod.policy.pending)
        self.update(5)
        self.assertEqual([notice["message"] for notice in self.notice_calls],
                         ["No suitable companion for this habitat."])
        self.update(20)
        self.assertEqual(len(self.notice_calls), 1)

    def test_matching_pet_temporarily_ineligible_keeps_opportunity(self):
        self.set_planet(13)
        self.pet(1, 2)
        self.pet(2, 4)
        self.ownership_eligible.side_effect = lambda owner, slot: slot != 1
        self.opportunity()
        self.assertTrue(self.mod.policy.pending)
        self.assertEqual(self.notice_calls, [])
        self.ownership_eligible.side_effect = None
        self.probe(4)
        self.assertEqual(self.queue_calls, [(self.player, 1)])

    def test_neutral_locations_need_no_planet_or_favorite(self):
        self.pet(1, 4)
        self.set_location(14)
        self.opportunity()
        self.assertEqual(self.queue_calls, [(self.player, 1)])

    def test_rotation_changes_companion_on_next_accepted_opportunity(self):
        self.pet(1, 4)
        self.pet(2, 2)
        self.set_location(2)
        self.opportunity(1)
        self.opportunity(5)
        self.assertEqual({slot for _, slot in self.queue_calls}, {1, 2})
        self.assertEqual(len(self.queue_calls), 2)

    def test_rejection_reserves_same_identity_without_consuming_cycle(self):
        self.pet(1, 0)
        self.pet(2, 0)
        self.set_planet(0)
        native_queue = self.module.cas_queue_pet
        rejected = Mock()
        self.module.cas_queue_pet = rejected
        self.opportunity()
        reserved = self.mod.selector.pending
        self.probe(4)
        self.probe(8)
        self.assertEqual({call.args[1] for call in rejected.call_args_list}, {self.mod.policy.pending_slot})
        self.assertEqual(self.mod.selector.pending, reserved)
        self.module.cas_queue_pet = native_queue
        self.probe(10)
        first = self.queue_calls[0][1]
        self.opportunity(14)
        self.assertNotEqual(self.queue_calls[-1][1], first)

    def test_removed_or_reordered_reserved_pet_cancels_without_replacement(self):
        self.pet(1, 0)
        self.pet(2, 0)
        self.set_planet(0)
        self.exit(1)
        self.probe(1)
        selected = self.mod.policy.pending_slot
        identity = self.mod._pending_pet_identity
        self.set_pet(selected, self.seed(999))
        self.set_pet(7, identity)
        self.probe(4)
        self.assertEqual(self.queue_calls, [])
        self.assertFalse(self.mod.policy.pending)
        self.assertIsNone(self.mod.selector.pending)

    def test_duplicate_identity_rejects_whole_roster_even_if_one_is_ineligible(self):
        self.set_planet(0)
        self.pet(1, 0, self.seed(99))
        self.pet(2, 0, self.seed(99))
        self.ownership_eligible.side_effect = lambda owner, slot: slot == 1
        self.opportunity()
        self.assertEqual(self.queue_calls, [])
        self.assertFalse(self.mod.policy.pending)
        self.assertTrue(self.mod.enabled)

    def test_new_duplicate_after_reservation_cancels_before_queue(self):
        self.set_planet(0)
        self.pet(1, 0)
        self.exit(1)
        self.probe(1)
        self.pet(3, 0, self.seed(101))
        self.probe(4)
        self.assertEqual(self.queue_calls, [])
        self.assertFalse(self.mod.policy.pending)

    def test_identity_replacement_inside_final_native_check_cannot_queue_new_occupant(self):
        self.pet(1, 0)
        self.set_planet(0)
        def check(player, slot):
            if self.mod.policy._in_flight:
                self.set_pet(slot, self.seed(999))
            return True
        self.can_summon.side_effect = check
        self.opportunity()
        self.assertEqual(self.queue_calls, [])
        self.assertFalse(self.mod.policy.pending)
        self.assertIsNone(self.mod.selector.pending)

    def test_duplicate_created_inside_final_native_check_cancels(self):
        self.pet(1, 0)
        self.set_planet(0)
        def check(player, slot):
            if self.mod.policy._in_flight:
                self.pet(3, 0, self.seed(101))
            return True
        self.can_summon.side_effect = check
        self.opportunity()
        self.assertEqual(self.queue_calls, [])
        self.assertFalse(self.mod.policy.pending)

    def test_off_queued_inside_final_native_check_prevents_summon(self):
        self.pet(1, 0)
        self.set_planet(0)
        def check(player, slot):
            if self.mod.policy._in_flight:
                self.mod.automatic_summoning = False
            return True
        self.can_summon.side_effect = check
        self.opportunity()
        self.assertEqual(self.queue_calls, [])
        self.assertFalse(self.mod.policy.pending)

    def test_random_rotation_waits_through_temporarily_unsupported_location(self):
        self.mod.selection_mode_value = "random"
        self.pet(1, 0)
        self.exit(1)
        self.probe(1)
        choice = self.mod.selector.pending
        self.set_location(0)
        self.update(4)
        self.assertEqual(self.mod.selector.pending, choice)
        self.assertTrue(self.mod.policy.pending)
        self.set_location(3)
        self.probe(5)
        self.probe(6.5)
        self.assertEqual(self.queue_calls, [(self.player, 1)])

    def test_unexpected_native_queue_cancels_rotation_state(self):
        self.pet(1, 0)
        self.set_planet(0)
        self.module.cas_queue_pet = lambda player, slot: self.set_pending(9)
        self.opportunity()
        self.assertFalse(self.mod.enabled)
        self.assertFalse(self.mod.policy.pending)
        self.assertIsNone(self.mod.selector.pending)

    def test_changed_habitat_cancels_frozen_request_instead_of_rerolling(self):
        self.set_planet(13)
        self.pet(1, 2)
        self.pet(2, 4)
        self.exit(1)
        self.probe(1)
        self.set_planet(4)
        self.probe(4)
        self.assertEqual(self.queue_calls, [])
        self.assertFalse(self.mod.policy.pending)

    def test_local_load_clears_reservation_network_load_preserves_it(self):
        self.pet(1, 0)
        self.set_planet(0)
        self.exit(1)
        self.probe(1)
        choice = self.mod.selector.pending
        self.load_save(987, network=True)
        self.assertEqual(self.mod.selector.pending, choice)
        self.load_save(987)
        self.assertIsNone(self.mod.selector.pending)

    def test_preference_change_cancels_reservation_without_changing_favorite(self):
        self.pet(1, 0)
        self.set_planet(0)
        self.select(1)
        self.exit(1)
        self.probe(1)
        favorite = self.mod.pet_identity
        self.mod.rotate_companions = False
        self.update(3, dt=0)
        self.assertFalse(self.mod.policy.pending)
        self.assertIsNone(self.mod.selector.pending)
        self.assertEqual(self.mod.pet_identity, favorite)
        self.assertFalse(self.mod.rotate_companions_value)


if __name__ == "__main__":
    unittest.main()
