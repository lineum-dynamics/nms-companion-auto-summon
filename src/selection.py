"""Pure, session-only companion selection; no game, file, or native access.

The habitat table is a mod-design heuristic, not a claim of ecological or
native-game suitability. The caller supplies owned identities separately from
temporary native eligibility, and still performs every native check itself.
Only native queue acceptance authorizes ``commit``; logical or visible pet
activity is a separate observation.
"""

from dataclasses import dataclass as _selection_dataclass
import random as _selection_random


SELECTION_MAX_COMPANIONS = 30
SELECTION_HABITATS = frozenset(range(16)) - {8, 9, 10, 11}
SELECTION_GROUP_WEIGHTS = (("exact", 13), ("related", 5), ("acceptable", 1))


class SelectionError(ValueError):
    """The supplied selection observation cannot be used safely."""


class AmbiguousIdentityError(SelectionError):
    """An identity occurs more than once and must not resolve to a pet."""


class ReservationInvalidatedError(SelectionError):
    """The reserved pet is no longer owned; cancel this opportunity."""


def _selection_identity(value):
    if type(value) is not bytes or len(value) != 16:
        raise SelectionError("Companion identity must be exactly 16 immutable bytes")
    return value


def normalize_habitat(value):
    """Normalize Weird variants; unknown categories remain unknown.

    ``None`` and integer categories outside the concrete supported set return
    ``None``. Wrong types, including bool, are invalid observations.
    """
    if value is None:
        return None
    if type(value) is not int:
        raise SelectionError("Habitat must be an integer or None")
    if value in {8, 9, 10}:
        return 7
    return value if value in SELECTION_HABITATS else None


@_selection_dataclass(frozen=True)
class Candidate:
    """Stable identity and normalized habitat, without slot or display name."""

    identity: bytes
    habitat: int | None = None

    def __post_init__(self):
        _selection_identity(self.identity)
        object.__setattr__(self, "habitat", normalize_habitat(self.habitat))


@_selection_dataclass(frozen=True)
class HabitatRules:
    """Explicit directed (planet, companion) pairs; unlisted pairs are excluded.

    Exact matches take precedence, then related, then acceptable. Configuration
    is copied into immutable sets. Tables must be disjoint and use canonical
    recognized categories; no implicit reverse pair or biological inference is
    added. Empty non-exact tables permit only exact matches.
    """

    recognized: frozenset = SELECTION_HABITATS
    related_pairs: frozenset = frozenset()
    acceptable_pairs: frozenset = frozenset()

    def __post_init__(self):
        recognized = frozenset(self.recognized)
        if any(type(value) is not int or value not in SELECTION_HABITATS
               for value in recognized):
            raise SelectionError("Recognized habitats must be canonical concrete IDs")
        object.__setattr__(self, "recognized", recognized)
        for name in ("related_pairs", "acceptable_pairs"):
            pairs = set()
            for pair in getattr(self, name):
                if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                    raise SelectionError("Habitat rules require directed pairs")
                planet, companion = pair
                if (type(planet) is not int or type(companion) is not int
                        or planet not in recognized or companion not in recognized
                        or planet == companion):
                    raise SelectionError("Non-exact habitat pairs must use distinct recognized IDs")
                pairs.add((planet, companion))
            object.__setattr__(self, name, frozenset(pairs))
        if self.related_pairs & self.acceptable_pairs:
            raise SelectionError("Related and acceptable habitat pairs must be disjoint")

    def group(self, planet_habitat, companion_habitat):
        """Return one group name, or None for unknown or unapproved pairs."""
        planet = normalize_habitat(planet_habitat)
        companion = normalize_habitat(companion_habitat)
        if planet not in self.recognized or companion not in self.recognized:
            return None
        if planet == companion:
            return "exact"
        pair = (planet, companion)
        if pair in self.related_pairs:
            return "related"
        if pair in self.acceptable_pairs:
            return "acceptable"
        return None


# Draft balance only. These relationships do not bypass native eligibility.
DEFAULT_HABITAT_RULES = HabitatRules(
    related_pairs=frozenset({
        (0, 12), (12, 0), (1, 12), (12, 1),
        (2, 13), (13, 2), (5, 6), (6, 5),
    }),
    acceptable_pairs=frozenset({
        (0, 5), (0, 4), (1, 3), (2, 5), (2, 6),
        (3, 1), (3, 5), (3, 6), (4, 5), (4, 6),
        (5, 0), (5, 2), (5, 3), (5, 4),
        (6, 2), (6, 3), (6, 4), (12, 3), (12, 5),
        (13, 5), (13, 6),
    }),
)


def _selection_roster(candidates):
    roster = {}
    try:
        iterator = iter(candidates)
    except TypeError:
        raise SelectionError("Owned roster must be an iterable of Candidate values") from None
    for candidate in iterator:
        if not isinstance(candidate, Candidate):
            raise SelectionError("Owned roster entries must be Candidate values")
        if candidate.identity in roster:
            raise AmbiguousIdentityError("Owned companion identity is ambiguous")
        if len(roster) >= SELECTION_MAX_COMPANIONS:
            raise SelectionError("Owned roster exceeds 30 companions")
        roster[candidate.identity] = candidate
    return roster


def build_habitat_groups(owned_candidates, habitat, rules=DEFAULT_HABITAT_RULES):
    """Build disjoint immutable candidate tuples from an unambiguous roster."""
    if not isinstance(rules, HabitatRules):
        raise SelectionError("rules must be HabitatRules")
    planet = normalize_habitat(habitat)
    roster = _selection_roster(owned_candidates)
    groups = {name: [] for name, _ in SELECTION_GROUP_WEIGHTS}
    for identity in sorted(roster):
        candidate = roster[identity]
        group = rules.group(planet, candidate.habitat)
        if group is not None:
            groups[group].append(candidate)
    return {name: tuple(candidates) for name, candidates in groups.items()}


class _SelectionBag:
    """Owned membership and an ordered list of not-yet-consumed identities."""

    def __init__(self):
        self.members = set()
        self.remaining = []
        self.last_accepted = None

    def reconcile(self, members, rng):
        self.remaining = [identity for identity in self.remaining if identity in members]
        if self.last_accepted not in members:
            self.last_accepted = None
        # Previously consumed surviving members stay consumed. Only genuinely
        # new group members are inserted, once, without reordering survivors.
        for identity in sorted(members - self.members):
            self.remaining.insert(rng.randrange(len(self.remaining) + 1), identity)
        self.members = set(members)

    def reserve(self, eligible, rng):
        # A cancelled singleton-only reservation can leave the last accepted
        # member in a newly prepared round. Reevaluate alternatives against
        # current eligibility without consuming or reordering that remainder.
        choices = eligible - {self.last_accepted} if len(eligible) > 1 else eligible
        for identity in self.remaining:
            if identity in choices:
                return identity
        # Exhaustion concerns the CURRENTLY eligible pool. Keep temporarily
        # ineligible unconsumed members in place instead of blocking the cycle
        # or mistaking their eventual return for a new adoption.
        refreshed = sorted(eligible - set(self.remaining))
        rng.shuffle(refreshed)
        # A fresh round must not immediately repeat this group's last accepted
        # pet when another eligible member exists. Move only the new round's
        # first member; existing unconsumed members retain their relative order.
        if len(refreshed) > 1 and refreshed[0] == self.last_accepted:
            refreshed.append(refreshed.pop(0))
        self.remaining.extend(refreshed)
        return refreshed[0]

    def commit(self, identity):
        self.remaining.remove(identity)
        self.last_accepted = identity


class CompanionSelector:
    """Reserve one fixed candidate, advancing rotation only on queue acceptance.

    Call ``reserve`` to start a normal opportunity. Repeated calls return its
    fixed reservation even during temporary ineligibility or changed habitat
    observations; the caller must still recheck native eligibility before use.
    Removing that pet raises ``ReservationInvalidatedError`` instead of drawing
    a replacement. Invalid or ambiguous observations cancel the reservation.

    Call ``cancel`` when the opportunity or settings change. Call ``reset`` on
    the caller's application/save boundary; no state is persisted. Bag keys
    separate Random from every canonical planet habitat and weighted group.
    Fresh rotation rounds avoid that group's last accepted pet when multiple
    members are currently eligible; a sole eligible member may repeat.
    Turning rotation off does not consume or reset existing bag history.
    """

    def __init__(self, rng=None, rules=DEFAULT_HABITAT_RULES):
        if not isinstance(rules, HabitatRules):
            raise SelectionError("rules must be HabitatRules")
        self._rng = _selection_random.Random() if rng is None else rng
        self._rules = rules
        self.reset()

    @property
    def pending(self):
        return self._pending

    def cancel(self):
        """Discard the reservation without consuming its rotation entry."""
        self._pending = None
        self._pending_bag = None

    def reset(self):
        """Clear all session history and reservations, retaining rules and RNG."""
        self._bags = {}
        self.cancel()

    def _members(self, key, roster):
        mode, habitat, group = key
        if mode == "random":
            return set(roster)
        return {identity for identity, candidate in roster.items()
                if self._rules.group(habitat, candidate.habitat) == group}

    def reserve(self, owned_candidates, eligible_identities, *, mode="random",
                habitat=None, rotate=True):
        """Reserve an eligible owned candidate, or return None if no group qualifies.

        Group weights are exactly 13/5/1, independent of group population;
        empty native-eligible groups are omitted from that integer draw.
        Unknown planetary habitat has no unrestricted fallback. Neutral
        station/Nexus behavior must be requested by the caller as Random.
        """
        try:
            if type(mode) is not str or mode not in {"random", "by_habitat"}:
                raise SelectionError("Selection mode must be random or by_habitat")
            if type(rotate) is not bool:
                raise SelectionError("rotate must be a bool")
            planet = normalize_habitat(habitat)
            roster = _selection_roster(owned_candidates)
            eligible = set()
            try:
                eligible_iterator = iter(eligible_identities)
            except TypeError:
                raise SelectionError("Eligible identities must be iterable") from None
            for identity in eligible_iterator:
                _selection_identity(identity)
                if identity not in roster:
                    raise SelectionError("Eligible identity is not in the owned roster")
                if identity in eligible:
                    raise AmbiguousIdentityError("Eligible companion identity is duplicated")
                eligible.add(identity)
            if self._pending is not None:
                if self._pending.identity not in roster:
                    raise ReservationInvalidatedError("Reserved companion is no longer owned")
                return self._pending
        except SelectionError:
            self.cancel()
            raise

        # Reconcile ownership for every retained context at the next normal
        # opportunity. Temporary eligibility does not change membership.
        for key, bag in self._bags.items():
            bag.reconcile(self._members(key, roster), self._rng)

        if mode == "random":
            key = ("random", None, "random")
            pool = eligible
        else:
            groups = build_habitat_groups(roster.values(), planet, self._rules)
            pools = [(name, weight, {candidate.identity for candidate in groups[name]} & eligible)
                     for name, weight in SELECTION_GROUP_WEIGHTS]
            pools = [(name, weight, pool) for name, weight, pool in pools if pool]
            if not pools:
                return None
            ticket = self._rng.randrange(sum(weight for _, weight, _ in pools))
            for name, weight, pool in pools:
                if ticket < weight:
                    key = ("by_habitat", planet, name)
                    break
                ticket -= weight
        if not pool:
            return None
        if rotate:
            bag = self._bags.setdefault(key, _SelectionBag())
            bag.reconcile(self._members(key, roster), self._rng)
            identity = bag.reserve(pool, self._rng)
        else:
            bag = None
            ordered = sorted(pool)
            identity = ordered[self._rng.randrange(len(ordered))]
        self._pending = roster[identity]
        self._pending_bag = bag
        return self._pending

    def commit(self, identity):
        """Consume only the matching reservation after native queue acceptance."""
        _selection_identity(identity)
        if self._pending is None or self._pending.identity != identity:
            return False
        if self._pending_bag is not None:
            self._pending_bag.commit(identity)
        self.cancel()
        return True
