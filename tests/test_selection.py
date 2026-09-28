"""Deterministic selector invariants without game, framework, or save access."""

from dataclasses import FrozenInstanceError
import importlib.util
from pathlib import Path
import random
import unittest


_spec = importlib.util.spec_from_file_location(
    "companion_selection_under_test",
    Path(__file__).resolve().parents[1] / "src" / "selection.py",
)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
Candidate = _module.Candidate
HabitatRules = _module.HabitatRules
CompanionSelector = _module.CompanionSelector
SelectionError = _module.SelectionError
AmbiguousIdentityError = _module.AmbiguousIdentityError
ReservationInvalidatedError = _module.ReservationInvalidatedError
DEFAULT_HABITAT_RULES = _module.DEFAULT_HABITAT_RULES
normalize_habitat = _module.normalize_habitat
build_habitat_groups = _module.build_habitat_groups


def identity(number):
    return number.to_bytes(16, "little")


def candidates(*habitats):
    return [Candidate(identity(index + 1), habitat)
            for index, habitat in enumerate(habitats)]


def ids(roster):
    return [candidate.identity for candidate in roster]


class StableRng:
    """Append insertions and preserve shuffle order for readable cycle cases."""

    def __init__(self):
        self.calls = []

    def randrange(self, stop):
        self.calls.append(("randrange", stop))
        return stop - 1

    def shuffle(self, values):
        self.calls.append(("shuffle", len(values)))


class TicketRng:
    """Use exact integer tickets rather than a probabilistic tolerance test."""

    def __init__(self, *tickets):
        self.tickets = list(tickets)
        self.stops = []

    def randrange(self, stop):
        self.stops.append(stop)
        value = self.tickets.pop(0)
        if not 0 <= value < stop:
            raise AssertionError((value, stop))
        return value

    def shuffle(self, values):
        raise AssertionError("Uniform non-rotation draws must not shuffle")


class BoundaryRng(StableRng):
    """Force the preceding ascending round's last member to the next head."""

    def shuffle(self, values):
        super().shuffle(values)
        values.reverse()


class CandidateAndHabitatTests(unittest.TestCase):
    def test_candidate_has_immutable_identity_and_habitat(self):
        candidate = Candidate(identity(1), 0)
        with self.assertRaises(FrozenInstanceError):
            candidate.identity = identity(2)
        with self.assertRaises(FrozenInstanceError):
            candidate.habitat = 5
        self.assertEqual(candidate, Candidate(identity(1), 0))

    def test_identity_requires_exactly_sixteen_immutable_bytes(self):
        for invalid in (None, "x" * 16, b"x" * 15, b"x" * 17,
                        bytearray(16), memoryview(bytes(16)), 16):
            with self.subTest(value=invalid), self.assertRaises(SelectionError):
                Candidate(invalid, 0)
        self.assertEqual(Candidate(bytes(16)).identity, bytes(16))

    def test_habitat_normalization_distinguishes_unknown_from_lush(self):
        self.assertEqual(normalize_habitat(0), 0)
        for value in (8, 9, 10):
            self.assertEqual(normalize_habitat(value), 7)
            self.assertEqual(Candidate(identity(1), value).habitat, 7)
        for value in (None, -1, 11, 16, 100):
            self.assertIsNone(normalize_habitat(value))
            self.assertIsNone(Candidate(identity(1), value).habitat)
        for invalid in (True, False, 0.0, "0", []):
            with self.subTest(value=invalid), self.assertRaises(SelectionError):
                normalize_habitat(invalid)

    def test_default_table_matches_every_explicit_directed_row(self):
        related = {0: {12}, 1: {12}, 2: {13}, 3: set(), 4: set(),
                   5: {6}, 6: {5}, 7: set(), 12: {0, 1}, 13: {2},
                   14: set(), 15: set()}
        acceptable = {0: {5, 4}, 1: {3}, 2: {5, 6}, 3: {1, 5, 6},
                      4: {5, 6}, 5: {0, 2, 3, 4}, 6: {2, 3, 4},
                      7: set(), 12: {3, 5}, 13: {5, 6}, 14: set(), 15: set()}
        self.assertEqual(DEFAULT_HABITAT_RULES.recognized, frozenset(related))
        for planet in related:
            for companion in related:
                expected = ("exact" if planet == companion else
                            "related" if companion in related[planet] else
                            "acceptable" if companion in acceptable[planet] else None)
                with self.subTest(planet=planet, companion=companion):
                    self.assertEqual(DEFAULT_HABITAT_RULES.group(planet, companion), expected)

    def test_unknowns_and_frozen_lava_have_no_unrestricted_fallback(self):
        for planet, companion in ((4, 13), (13, 4), (None, 0), (0, None),
                                  (11, 0), (0, 16), (-1, -1), (14, 15)):
            self.assertIsNone(DEFAULT_HABITAT_RULES.group(planet, companion))
        self.assertEqual(DEFAULT_HABITAT_RULES.group(8, 10), "exact")

    def test_custom_rules_are_copied_frozen_and_directional(self):
        pairs = {(0, 5)}
        rules = HabitatRules(recognized={0, 5}, acceptable_pairs=pairs)
        pairs.clear()
        self.assertEqual(rules.group(0, 5), "acceptable")
        self.assertIsNone(rules.group(5, 0))
        self.assertEqual(rules.group(0, 0), "exact")
        self.assertIsNone(rules.group(4, 4))
        with self.assertRaises(FrozenInstanceError):
            rules.acceptable_pairs = frozenset()
        self.assertIsNone(HabitatRules().group(0, 5))

    def test_invalid_or_overlapping_rule_tables_are_rejected(self):
        configurations = [
            {"recognized": {11}}, {"recognized": {True}},
            {"related_pairs": {(0, 0)}}, {"related_pairs": {(0, 16)}},
            {"related_pairs": {(0,)}}, {"related_pairs": {"05"}},
            {"related_pairs": {(0, 5)}, "acceptable_pairs": {(0, 5)}},
        ]
        for configuration in configurations:
            with self.subTest(configuration=configuration), self.assertRaises(SelectionError):
                HabitatRules(**configuration)

    def test_group_builder_is_disjoint_sorted_and_excludes_unapproved(self):
        roster = candidates(0, 12, 5, 13, None)
        groups = build_habitat_groups(reversed(roster), 0)
        self.assertEqual(groups, {"exact": (roster[0],), "related": (roster[1],),
                                  "acceptable": (roster[2],)})
        self.assertEqual(build_habitat_groups(roster, None),
                         {"exact": (), "related": (), "acceptable": ()})


class WeightedChoiceTests(unittest.TestCase):
    def test_each_integer_ticket_has_exact_thirteen_five_one_weight(self):
        # Twenty exact pets still get 13 tickets, not twenty times that weight.
        roster = candidates(*([0] * 20 + [12, 5]))
        outcomes = {"exact": 0, "related": 0, "acceptable": 0}
        for ticket in range(19):
            rng = TicketRng(ticket, 0)
            selected = CompanionSelector(rng).reserve(
                roster, ids(roster), mode="by_habitat", habitat=0, rotate=False)
            outcomes[DEFAULT_HABITAT_RULES.group(0, selected.habitat)] += 1
            self.assertEqual(rng.stops[0], 19)
        self.assertEqual(outcomes, {"exact": 13, "related": 5, "acceptable": 1})

    def test_empty_eligible_groups_are_removed_and_weights_renormalized(self):
        roster = candidates(0, 12, 5)
        for indices, expected in (((1, 2), {12: 5, 5: 1}),
                                  ((0, 2), {0: 13, 5: 1}),
                                  ((0, 1), {0: 13, 12: 5}),
                                  ((2,), {5: 1})):
            outcomes = dict.fromkeys(expected, 0)
            total = sum(expected.values())
            for ticket in range(total):
                rng = TicketRng(ticket, 0)
                selected = CompanionSelector(rng).reserve(
                    roster, [roster[index].identity for index in indices],
                    mode="by_habitat", habitat=0, rotate=False)
                outcomes[selected.habitat] += 1
                self.assertEqual(rng.stops[0], total)
            self.assertEqual(outcomes, expected)

    def test_uniform_member_draw_uses_only_selected_groups_population(self):
        roster = candidates(0, 0, 0, 12, 5)
        selected_ids = []
        for member_ticket in range(3):
            rng = TicketRng(12, member_ticket)
            selected = CompanionSelector(rng).reserve(
                roster, ids(roster), mode="by_habitat", habitat=0, rotate=False)
            selected_ids.append(selected.identity)
            self.assertEqual(rng.stops, [19, 3])
        self.assertEqual(selected_ids, ids(roster[:3]))

    def test_unknown_planet_and_no_approved_eligible_group_wait(self):
        roster = candidates(13, None)
        rng = TicketRng()
        selector = CompanionSelector(rng)
        for habitat in (None, -1, 11, 16, 4):
            self.assertIsNone(selector.reserve(roster, ids(roster),
                                               mode="by_habitat", habitat=habitat))
        self.assertEqual(rng.stops, [])
        self.assertIsNone(selector.pending)

    def test_random_neutral_selection_includes_unknown_habitat(self):
        roster = candidates(None)
        self.assertEqual(CompanionSelector(TicketRng(0)).reserve(
            roster, ids(roster), mode="random", habitat=None, rotate=False), roster[0])


class ReservationAndRotationTests(unittest.TestCase):
    def setUp(self):
        self.roster = candidates(0, 0, 0)
        self.rng = StableRng()
        self.selector = CompanionSelector(self.rng)

    def reserve(self, roster=None, eligible=None, **options):
        roster = self.roster if roster is None else roster
        return self.selector.reserve(roster, ids(roster) if eligible is None else eligible,
                                     **options)

    def accepted(self, roster=None, eligible=None, **options):
        selected = self.reserve(roster, eligible, **options)
        self.assertIsNotNone(selected)
        self.assertTrue(self.selector.commit(selected.identity))
        return selected

    def test_full_cycle_contains_each_identity_once_before_repeating(self):
        first = [self.accepted().identity for _ in range(3)]
        second = [self.accepted().identity for _ in range(3)]
        self.assertEqual(first, ids(self.roster))
        self.assertEqual(second, ids(self.roster))

    def test_new_round_avoids_last_accepted_without_dropping_any_member(self):
        self.selector = CompanionSelector(BoundaryRng())
        first = [self.accepted().identity for _ in range(3)]
        second = [self.accepted().identity for _ in range(3)]
        self.assertEqual(first, ids(self.roster))
        self.assertEqual(second, [self.roster[1].identity, self.roster[0].identity,
                                  self.roster[2].identity])
        self.assertNotEqual(first[-1], second[0])
        self.assertEqual(set(first), set(second))

    def test_cancel_at_round_boundary_preserves_the_unconsumed_choice(self):
        self.selector = CompanionSelector(BoundaryRng())
        for _ in range(3):
            self.accepted()
        selected = self.reserve()
        self.assertEqual(selected, self.roster[1])
        self.selector.cancel()
        self.assertEqual(self.accepted(), selected)
        self.assertEqual(self.accepted(), self.roster[0])

    def test_cancelled_choice_does_not_replace_last_accepted_for_renewal(self):
        self.selector = CompanionSelector(BoundaryRng())
        self.assertEqual(self.accepted(), self.roster[0])
        self.assertEqual(self.accepted(), self.roster[1])
        self.assertEqual(self.reserve(), self.roster[2])
        self.selector.cancel()
        # The cancelled third pet is now ineligible. A fresh eligible-only
        # round must avoid the actually accepted second pet, not the third.
        self.assertEqual(self.accepted(eligible=ids(self.roster[:2])), self.roster[0])
        self.assertEqual(self.accepted(), self.roster[2])

    def test_boundary_avoidance_preserves_unavailable_remainders_order(self):
        self.selector = CompanionSelector(BoundaryRng())
        self.roster = candidates(0, 0, 0, 0)
        self.accepted()
        self.accepted()
        self.assertEqual(self.accepted(eligible=ids(self.roster[:2])), self.roster[0])
        self.assertEqual(self.accepted(), self.roster[2])
        self.assertEqual(self.accepted(), self.roster[3])
        self.assertEqual(self.accepted(), self.roster[1])

    def test_single_eligible_member_may_repeat_at_every_boundary(self):
        self.selector = CompanionSelector(BoundaryRng())
        eligible = [self.roster[0].identity]
        for _ in range(5):
            self.assertEqual(self.accepted(eligible=eligible), self.roster[0])

    def test_cancelled_singleton_round_uses_newly_returned_alternative(self):
        self.selector = CompanionSelector(BoundaryRng())
        for _ in range(3):
            self.accepted()
        last = self.roster[2]
        self.assertEqual(self.reserve(eligible=[last.identity]), last)
        self.selector.cancel()
        # No queue accepted the singleton repeat. A now-eligible alternative
        # must prevent that repeat, without inserting a duplicate remainder.
        eligible = [self.roster[0].identity, last.identity]
        self.assertEqual(self.accepted(eligible=eligible), self.roster[0])
        self.assertEqual(self.accepted(eligible=eligible), last)
        self.assertEqual(self.accepted(eligible=eligible), self.roster[0])

    def test_last_accepted_is_separate_for_each_weighted_group(self):
        self.selector = CompanionSelector(BoundaryRng())
        roster = candidates(0, 0, 12, 12)
        options = {"mode": "by_habitat", "habitat": 0}
        related = ids(roster[2:])
        self.assertEqual(self.accepted(roster, related, **options), roster[2])
        self.assertEqual(self.accepted(roster, related, **options), roster[3])
        self.assertEqual(self.accepted(roster, ids(roster[:2]), **options), roster[0])
        # An intervening exact-group acceptance must not erase related history.
        self.assertEqual(self.accepted(roster, related, **options), roster[2])

    def test_retry_is_fixed_and_draws_no_more_randomness(self):
        selected = self.reserve()
        calls = list(self.rng.calls)
        self.assertIs(self.reserve(eligible=[]), selected)
        self.assertIs(self.reserve(list(reversed(self.roster)), mode="by_habitat",
                                   habitat=13, rotate=False), selected)
        self.assertEqual(self.rng.calls, calls)
        self.assertIs(self.selector.pending, selected)
        with self.assertRaises(AttributeError):
            self.selector.pending = None

    def test_cancel_does_not_consume_but_matching_commit_does(self):
        selected = self.reserve()
        self.selector.cancel()
        self.assertFalse(self.selector.commit(selected.identity))
        self.assertEqual(self.reserve(), selected)
        self.assertFalse(self.selector.commit(self.roster[1].identity))
        self.assertEqual(self.selector.pending, selected)
        self.assertTrue(self.selector.commit(selected.identity))
        self.assertFalse(self.selector.commit(selected.identity))
        self.assertEqual(self.reserve(), self.roster[1])

    def test_removed_reserved_identity_cancels_without_replacement(self):
        selected = self.reserve()
        remaining = self.roster[1:]
        with self.assertRaises(ReservationInvalidatedError):
            self.reserve(remaining)
        self.assertIsNone(self.selector.pending)
        self.assertFalse(self.selector.commit(selected.identity))
        # Only a caller-authorized new opportunity can reserve again.
        self.assertEqual(self.reserve(remaining), remaining[0])

    def test_duplicate_roster_cancels_reservation_without_consuming(self):
        selected = self.reserve()
        with self.assertRaises(AmbiguousIdentityError):
            self.reserve(self.roster + [Candidate(selected.identity, 5)])
        self.assertIsNone(self.selector.pending)
        self.assertEqual(self.reserve(), selected)

    def test_roster_reorder_and_rebuilt_metadata_preserve_remaining_order(self):
        baseline = CompanionSelector(random.Random(348))
        reordered = CompanionSelector(random.Random(348))
        for index in range(9):
            a = baseline.reserve(self.roster, ids(self.roster))
            # Slots and names are deliberately not part of selector identity.
            rebuilt = [Candidate(candidate.identity, candidate.habitat)
                       for candidate in reversed(self.roster)]
            b = reordered.reserve(rebuilt, list(reversed(ids(self.roster))))
            self.assertEqual(a.identity, b.identity, index)
            baseline.commit(a.identity)
            reordered.commit(b.identity)

    def test_adoption_inserts_once_without_restoring_consumed_members(self):
        self.assertEqual(self.accepted(), self.roster[0])
        adopted = Candidate(identity(4), 0)
        enlarged = self.roster + [adopted]
        outcomes = [self.accepted(enlarged).identity for _ in range(3)]
        self.assertEqual(outcomes, ids(self.roster[1:]) + [adopted.identity])
        self.assertEqual(self.accepted(enlarged), self.roster[0])

    def test_abandonment_removes_only_disappeared_member(self):
        self.accepted()
        reduced = [self.roster[0], self.roster[2]]
        self.assertEqual(self.accepted(reduced), self.roster[2])
        self.assertEqual(self.accepted(reduced), self.roster[0])

    def test_temporary_ineligibility_is_not_new_adoption(self):
        self.assertEqual(self.accepted(), self.roster[0])
        self.assertEqual(self.accepted(eligible=[self.roster[2].identity]), self.roster[2])
        # The returning consumed first pet must wait for the unconsumed second.
        self.assertEqual(self.accepted(), self.roster[1])

    def test_exhausted_eligible_pool_recycles_without_blocking_hidden_remainder(self):
        only_first = [self.roster[0].identity]
        for _ in range(4):
            self.assertEqual(self.accepted(eligible=only_first), self.roster[0])
        # Hidden, unconsumed members retained both status and relative order.
        self.assertEqual(self.accepted(), self.roster[1])
        self.assertEqual(self.accepted(), self.roster[2])
        self.assertEqual(self.accepted(), self.roster[0])

    def test_empty_eligibility_does_not_reset_owned_history(self):
        self.accepted()
        self.assertIsNone(self.reserve(eligible=[]))
        self.assertEqual(self.accepted(), self.roster[1])

    def test_rotation_off_does_not_consume_or_reset_rotation_history(self):
        self.accepted()
        self.assertEqual(self.accepted(rotate=False), self.roster[2])
        self.assertEqual(self.accepted(), self.roster[1])

    def test_context_and_group_cycles_are_separate(self):
        roster = candidates(0, 0, 12, 12)
        a = self.accepted(roster, mode="by_habitat", habitat=0)
        self.assertEqual(a, roster[2])  # Final ticket picks related.
        b = self.accepted(roster, mode="by_habitat", habitat=12)
        self.assertEqual(b, roster[0])  # Separate context's related group.
        c = self.accepted(roster, mode="by_habitat", habitat=0)
        self.assertEqual(c, roster[3])
        # Random did not share consumption with either habitat context.
        self.assertEqual(self.accepted(roster), roster[0])

    def test_group_membership_change_reconciles_without_resetting_survivors(self):
        roster = candidates(0, 0, 12, 12)
        self.assertEqual(self.accepted(roster, mode="by_habitat", habitat=0), roster[2])
        changed = [roster[0], Candidate(roster[1].identity, 12), roster[2], roster[3]]
        # New related member is inserted once after the surviving unconsumed pet.
        self.assertEqual(self.accepted(changed, mode="by_habitat", habitat=0), roster[3])
        self.assertEqual(self.accepted(changed, mode="by_habitat", habitat=0), changed[1])

    def test_reset_clears_all_history_and_pending_state(self):
        self.accepted()
        self.reserve()
        self.selector.reset()
        self.assertIsNone(self.selector.pending)
        self.assertFalse(self.selector.commit(self.roster[1].identity))
        self.assertEqual(self.reserve(), self.roster[0])


class SelectionInputTests(unittest.TestCase):
    def test_owned_roster_is_bounded_and_duplicates_never_bias_selection(self):
        roster = candidates(*([0] * 31))
        selector = CompanionSelector(StableRng())
        self.assertIsNotNone(selector.reserve(roster[:30], ids(roster[:30])))
        selector.cancel()
        with self.assertRaises(SelectionError):
            selector.reserve(iter(roster), ids(roster))
        with self.assertRaises(AmbiguousIdentityError):
            build_habitat_groups([roster[0], roster[0]], 0)
        self.assertIsNone(selector.pending)

    def test_unknown_duplicate_or_malformed_eligible_ids_cancel_pending(self):
        roster = candidates(0, 5)
        selector = CompanionSelector(StableRng())
        for eligible in ([identity(30)], [roster[0].identity] * 2,
                         [b"short"], [bytearray(16)], [None]):
            selector.reserve(roster, ids(roster))
            with self.subTest(eligible=eligible), self.assertRaises(SelectionError):
                selector.reserve(roster, eligible)
            self.assertIsNone(selector.pending)

    def test_invalid_options_and_roster_entries_are_refused(self):
        roster = candidates(0)
        for options in ({"mode": "habitat"}, {"mode": "last_manual"}, {"mode": []},
                        {"rotate": 1}, {"habitat": True}):
            with self.subTest(options=options), self.assertRaises(SelectionError):
                CompanionSelector().reserve(roster, ids(roster), **options)
        with self.assertRaises(SelectionError):
            CompanionSelector().reserve([object()], [])
        with self.assertRaises(SelectionError):
            CompanionSelector(rules={})

    def test_noniterable_observations_cancel_without_consuming(self):
        roster = candidates(0, 0)
        selector = CompanionSelector(StableRng())
        for owned, eligible in ((None, []), (roster, None)):
            selected = selector.reserve(roster, ids(roster))
            with self.assertRaises(SelectionError):
                selector.reserve(owned, eligible)
            self.assertIsNone(selector.pending)
            self.assertEqual(selector.reserve(roster, ids(roster)), selected)
            selector.cancel()

    def test_empty_roster_creates_no_reservation(self):
        selector = CompanionSelector(TicketRng())
        self.assertIsNone(selector.reserve([], []))
        self.assertIsNone(selector.reserve([], [], mode="by_habitat", habitat=0))
        self.assertIsNone(selector.pending)


if __name__ == "__main__":
    unittest.main()
