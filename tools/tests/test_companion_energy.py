"""Pure proposal checks: owned snapshots, no game, native calls or persistence."""

from dataclasses import FrozenInstanceError, replace
import importlib.util
from pathlib import Path
import sys
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "companion_energy.py"
SPEC = importlib.util.spec_from_file_location("cas_energy_prototype", SOURCE)
ENERGY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ENERGY
SPEC.loader.exec_module(ENERGY)


class EnergyTests(unittest.TestCase):
    def setUp(self):
        self.model = ENERGY.EnergyModel()
        self.base = ENERGY.BaseModule("base-A", 1, True, True, False, 100, 100, 0)
        self.controller = ENERGY.RechargeController("controller-A", 1, True, True, False)
        self.snapshot = ENERGY.EnergySnapshot("save-A", 1, True, self.base, self.controller, 3, 1)

    def at_charge(self, charge, **changes):
        return replace(self.snapshot, base=replace(self.base, charge=charge), **changes)

    def accepted(self, snapshot=None, request=1):
        snapshot = snapshot or self.snapshot
        token = self.model.reserve(request, snapshot)
        self.assertIsNotNone(token)
        self.assertTrue(self.model.accept_queue(token, snapshot, accepted=True))
        return token

    def active(self, token, snapshot=None, **changes):
        snapshot = snapshot or self.snapshot
        args = dict(request_id=token.request_id, context=snapshot.context, ready=True, active=True)
        args.update(changes)
        return self.model.confirm_active(token, snapshot, **args)

    def test_immutable_snapshots_and_effects_cannot_silently_spend_inventory(self):
        token = self.accepted()
        effect = self.active(token)
        self.assertEqual(self.snapshot.base.charge, 100)
        self.assertEqual(self.snapshot.ion_batteries, 3)
        self.assertEqual(effect.after.base.charge, 90)
        self.assertEqual(effect.after.ion_batteries, self.snapshot.ion_batteries)
        self.assertEqual(effect.after.inventory_version, self.snapshot.inventory_version)
        with self.assertRaises(FrozenInstanceError):
            self.snapshot.base.charge = 90
        with self.assertRaises(FrozenInstanceError):
            effect.charge_units = 0

    def test_accepted_queue_alone_and_failed_placement_spend_nothing(self):
        token = self.model.reserve(1, self.snapshot)
        self.assertIsNone(self.active(token))
        self.assertFalse(self.model.accept_queue(token, self.snapshot, accepted=False))
        self.assertIsNone(self.active(token))
        self.assertTrue(self.model.accept_queue(token, self.snapshot, accepted=True))
        for flags in (dict(ready=False), dict(active=False), dict(request_id=2), dict(context="save-B")):
            with self.subTest(flags=flags):
                self.assertIsNone(self.active(token, **flags))
        self.assertEqual(self.snapshot.base.charge, 100)
        self.assertIsNotNone(self.active(token))

    def test_one_success_requests_one_debit_and_requires_external_confirmation(self):
        token = self.accepted()
        effect = self.active(token)
        self.assertIsNone(self.active(token))
        self.assertIsNone(self.model.reserve(2, self.snapshot))
        self.assertFalse(self.model.confirm_debit(effect, self.snapshot))
        self.assertTrue(self.model.confirm_debit(effect, effect.after))
        self.assertFalse(self.model.confirm_debit(effect, effect.after))
        self.assertIsNone(self.model.reserve(1, effect.after))
        self.assertIsNotNone(self.model.reserve(3, effect.after))

    def test_rejected_queue_revokes_prior_acceptance_for_the_same_request(self):
        token = self.accepted()
        self.assertFalse(self.model.accept_queue(token, self.snapshot, accepted=False))
        self.assertIsNone(self.active(token))
        self.assertIsNone(self.model._effect)
        self.assertEqual(self.snapshot.base.charge, 100)
        self.assertEqual(self.snapshot.ion_batteries, 3)
        # A later accepted placement may recover the same reserved request,
        # but only that new acceptance can authorize one debit effect.
        self.assertTrue(self.model.accept_queue(token, self.snapshot, accepted=True))
        effect = self.active(token)
        self.assertIsNotNone(effect)
        self.assertIsNone(self.active(token))
        self.assertTrue(self.model.confirm_debit(effect, effect.after))
        self.assertFalse(self.model.confirm_debit(effect, effect.after))

    def test_effect_or_reservation_copies_do_not_duplicate_authority(self):
        token = self.accepted()
        self.assertIsNone(self.active(replace(token)))
        effect = self.active(token)
        self.assertFalse(self.model.confirm_debit(replace(effect), effect.after))
        self.assertTrue(self.model.confirm_debit(effect, effect.after))

    def test_cancelled_request_and_effect_never_debit_or_refund(self):
        token = self.accepted()
        self.model.cancel()
        self.assertIsNone(self.active(token))
        self.assertIsNone(self.model.reserve(1, self.snapshot))
        token = self.accepted(request=2)
        effect = self.active(token)
        self.model.cancel()
        self.assertFalse(self.model.confirm_debit(effect, effect.after))
        self.assertEqual(self.snapshot.base.charge, 100)

    def test_context_load_module_and_inventory_changes_invalidate_reservations(self):
        changes = (
            replace(self.snapshot, context="save-B", load_epoch=2),
            replace(self.snapshot, load_epoch=2),
            replace(self.snapshot, base=replace(self.base, identity="base-B")),
            replace(self.snapshot, base=replace(self.base, version=2, damaged=True)),
            replace(self.snapshot, ion_batteries=2, inventory_version=2),
            replace(self.snapshot, automation_enabled=False),
            replace(self.snapshot, controller=None),
        )
        for snapshot in changes:
            with self.subTest(snapshot=snapshot):
                self.model = ENERGY.EnergyModel()
                token = self.accepted()
                self.assertIsNone(self.active(token, snapshot))

    def test_stale_versions_and_same_epoch_context_mismatch_are_rejected(self):
        fresh = replace(self.snapshot, base=replace(self.base, version=2, charge=90),
                        inventory_version=2, ion_batteries=2)
        self.assertEqual(self.model.status(fresh), "energy.ready")
        for snapshot in (self.snapshot, replace(fresh, context="save-B"),
                         replace(fresh, base=replace(fresh.base, charge=80)),
                         replace(fresh, ion_batteries=1), replace(fresh, load_epoch=0)):
            with self.subTest(snapshot=snapshot):
                self.assertEqual(self.model.status(snapshot), "energy.stale_snapshot")
                self.assertIsNone(self.model.reserve(10, snapshot))

    def test_charge_increase_requires_new_cycle_and_old_module_stays_stale_after_absence(self):
        low = self.at_charge(10)
        self.assertEqual(self.model.status(low), "energy.ready")
        increased = replace(low, base=replace(low.base, charge=100, version=2))
        self.assertEqual(self.model.status(increased), "energy.stale_snapshot")
        increased = replace(increased, base=replace(increased.base, cycle=1))
        self.assertEqual(self.model.status(increased), "energy.ready")
        self.model.status(replace(increased, base=None))
        self.assertEqual(self.model.status(low), "energy.stale_snapshot")

    def test_missing_incomplete_damaged_or_off_module_blocks_energy_only(self):
        snapshots = (replace(self.snapshot, base=None),
                     replace(self.snapshot, base=replace(self.base, installed=False)),
                     replace(self.snapshot, base=replace(self.base, complete=False)),
                     replace(self.snapshot, base=replace(self.base, damaged=True)),
                     replace(self.snapshot, automation_enabled=False),
                     self.at_charge(9))
        for snapshot in snapshots:
            with self.subTest(snapshot=snapshot):
                model = ENERGY.EnergyModel()
                self.assertIsNone(model.reserve(1, snapshot))
                self.assertEqual(snapshot.automation_enabled, snapshot is not snapshots[-2])

    def test_recharge_requires_on_both_valid_modules_low_charge_and_stock(self):
        empty = self.at_charge(0)
        self.assertIsNotNone(self.model.plan_recharge(empty))
        self.assertEqual(empty.ion_batteries, 3)
        for snapshot in (replace(empty, automation_enabled=False), replace(empty, base=None),
                         replace(empty, base=replace(empty.base, complete=False)),
                         replace(empty, base=replace(empty.base, damaged=True)),
                         replace(empty, controller=None),
                         replace(empty, controller=replace(self.controller, installed=False)),
                         replace(empty, controller=replace(self.controller, complete=False)),
                         replace(empty, controller=replace(self.controller, damaged=True)),
                         replace(empty, ion_batteries=0), self.at_charge(10), self.at_charge(100)):
            with self.subTest(snapshot=snapshot):
                self.assertIsNone(ENERGY.EnergyModel().plan_recharge(snapshot))

    def test_refill_is_one_explicit_battery_effect_and_never_creates_summon_intent(self):
        empty = self.at_charge(5)
        self.assertIsNone(self.model.reserve(1, empty))
        plan = self.model.plan_recharge(empty)
        self.assertEqual(plan.before, empty)
        self.assertEqual(plan.batteries, 1)
        self.assertEqual(plan.after.ion_batteries, 2)
        self.assertEqual(plan.after.base.charge, 100)
        self.assertEqual(plan.after.base.cycle, empty.base.cycle + 1)
        self.assertIsNone(self.model.plan_recharge(empty))
        self.assertEqual(self.model.confirm_recharge(plan, empty), ())
        self.assertEqual(self.model.confirm_recharge(plan, plan.after), ("energy.recharged_ready",))
        self.assertEqual(self.model.confirm_recharge(plan, plan.after), ())
        self.assertIsNone(self.model.reserve(1, plan.after))
        self.assertIsNone(self.model._reservation)
        self.assertIsNone(self.model._effect)
        self.assertEqual(self.model.observe(plan.after), ())

    def test_recharge_refuses_stale_cancelled_copied_and_wrong_inventory_effects(self):
        empty = self.at_charge(0)
        plan = self.model.plan_recharge(empty)
        wrong = replace(plan.after, ion_batteries=empty.ion_batteries)
        self.assertEqual(self.model.confirm_recharge(plan, wrong), ())
        self.assertEqual(self.model.confirm_recharge(replace(plan), plan.after), ())
        self.model.status(replace(empty, inventory_version=2, ion_batteries=2))
        self.assertEqual(self.model.confirm_recharge(plan, plan.after), ())
        self.model = ENERGY.EnergyModel()
        plan = self.model.plan_recharge(empty)
        self.model.cancel()
        self.assertEqual(self.model.confirm_recharge(plan, plan.after), ())

    def test_low_once_per_cycle_depleted_once_per_load_without_exit_spam(self):
        low = self.at_charge(20)
        self.assertEqual(self.model.observe(low), ("energy.low",))
        for request in range(1, 21):
            self.model.reserve(request, low)
            self.model.cancel()
            self.assertEqual(self.model.observe(low), ())
        reloaded = replace(low, load_epoch=2)
        self.assertEqual(self.model.observe(reloaded), ())
        empty = replace(reloaded, base=replace(low.base, version=2, charge=0))
        self.assertEqual(self.model.observe(empty), ("energy.depleted",))
        self.assertEqual(self.model.observe(empty), ())
        empty = replace(empty, load_epoch=3)
        self.assertEqual(self.model.observe(empty), ("energy.depleted",))
        self.assertEqual(self.model.observe(empty), ())
        recharged = replace(empty, base=replace(empty.base, version=3, cycle=1, charge=100))
        self.assertEqual(self.model.observe(recharged), ())
        next_low = replace(recharged, base=replace(recharged.base, version=4, charge=20))
        self.assertEqual(self.model.observe(next_low), ("energy.low",))

    def test_warning_suppression_respects_off_and_invalid_controller(self):
        empty = self.at_charge(0, ion_batteries=0, automation_enabled=False)
        self.assertEqual(self.model.observe(empty), ())
        empty = replace(empty, automation_enabled=True)
        self.assertEqual(self.model.observe(empty), ("energy.depleted", "energy.recharge_fuel_empty"))
        self.assertEqual(self.model.observe(replace(empty, automation_enabled=False)), ())
        self.assertEqual(self.model.observe(empty), ())
        broken = replace(empty, controller=replace(self.controller, damaged=True))
        self.assertEqual(ENERGY.EnergyModel().observe(broken), ("energy.depleted",))

    def test_repeated_confirmed_summons_conserve_charge_and_batteries(self):
        current = self.snapshot
        for request in range(1, 11):
            token = self.accepted(current, request)
            effect = self.active(token, current)
            self.assertEqual(effect.before.base.charge - effect.after.base.charge, 10)
            self.assertTrue(self.model.confirm_debit(effect, effect.after))
            current = effect.after
        self.assertEqual(current.base.charge, 0)
        self.assertEqual(current.ion_batteries, 3)
        self.assertIsNone(self.model.reserve(11, current))
        plan = self.model.plan_recharge(current)
        self.assertEqual(self.model.confirm_recharge(plan, plan.after), ("energy.recharged_ready",))
        self.assertEqual(plan.after.base.charge, 100)
        self.assertEqual(plan.after.ion_batteries, 2)

    def test_configurable_values_remain_prototype_only_and_bounded(self):
        config = ENERGY.EnergyConfig(capacity=60, summon_cost=6, low_threshold=12)
        self.model = ENERGY.EnergyModel(config)
        snapshot = replace(self.snapshot, base=replace(self.base, maximum=60, charge=60))
        token = self.accepted(snapshot)
        effect = self.active(token, snapshot)
        self.assertEqual(effect.after.base.charge, 54)
        self.assertEqual(ENERGY.EnergyModel(config).status(self.snapshot), "energy.capacity_mismatch")
        for args in (dict(summon_cost=True), dict(summon_cost=0), dict(capacity=ENERGY.LIMIT + 1),
                     dict(low_threshold=100), dict(low_threshold=5)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                ENERGY.EnergyConfig(**args)
        for args in (dict(charge=-1), dict(charge=101), dict(version=True), dict(identity="")):
            with self.subTest(args=args), self.assertRaises(ValueError):
                replace(self.base, **args)
        with self.assertRaises(ValueError):
            replace(self.snapshot, ion_batteries=-1)


if __name__ == "__main__":
    unittest.main()
