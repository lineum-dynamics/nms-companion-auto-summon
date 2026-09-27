"""Offline energy proposal, deliberately disconnected from production/builds.

All inputs/effects are owned immutable data. Nothing here reads a game, calls a
native function, edits an inventory/save, installs technology or starts a summon.
Numerical defaults are prototype examples, not approved gameplay balance.

A future adapter must establish snapshot freshness and a safe native transaction
before applying an effect. Emitting an effect is a request, not proof of debit or
recharge. Confirm methods only validate externally supplied before/after data.
Versions and load/cycle epochs are explicit prototype inputs, not mapped native
fields. Keep one model for the current context; this is not persistent storage.
"""

from dataclasses import dataclass, replace
import re


LIMIT = 1_000_000
EVENT_IDS = frozenset(("energy.low", "energy.depleted", "energy.recharge_fuel_empty",
                       "energy.recharged_ready"))


def _integer(value, *, minimum=0):
    if type(value) is not int or not minimum <= value <= LIMIT:
        raise ValueError("Expected a bounded integer")


def _identity(value):
    if type(value) is not str or re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", value) is None:
        raise ValueError("Expected a bounded opaque identity")


def _booleans(*values):
    if any(type(value) is not bool for value in values):
        raise ValueError("Expected exact boolean flags")


@dataclass(frozen=True)
class EnergyConfig:
    capacity: int = 100
    summon_cost: int = 10
    low_threshold: int = 20

    def __post_init__(self):
        for value in (self.capacity, self.summon_cost, self.low_threshold):
            _integer(value, minimum=1)
        if not self.summon_cost <= self.low_threshold < self.capacity:
            raise ValueError("Prototype cost and warning threshold must fit capacity")


@dataclass(frozen=True)
class BaseModule:
    identity: str
    version: int
    installed: bool
    complete: bool
    damaged: bool
    charge: int
    maximum: int
    cycle: int

    def __post_init__(self):
        _identity(self.identity)
        _booleans(self.installed, self.complete, self.damaged)
        for value in (self.version, self.charge, self.cycle):
            _integer(value)
        _integer(self.maximum, minimum=1)
        if self.charge > self.maximum:
            raise ValueError("Charge exceeds module capacity")


@dataclass(frozen=True)
class RechargeController:
    identity: str
    version: int
    installed: bool
    complete: bool
    damaged: bool

    def __post_init__(self):
        _identity(self.identity)
        _integer(self.version)
        _booleans(self.installed, self.complete, self.damaged)


@dataclass(frozen=True)
class EnergySnapshot:
    context: str
    load_epoch: int
    automation_enabled: bool
    base: BaseModule | None
    controller: RechargeController | None = None
    ion_batteries: int = 0
    inventory_version: int = 0

    def __post_init__(self):
        _identity(self.context)
        _integer(self.load_epoch)
        _integer(self.ion_batteries)
        _integer(self.inventory_version)
        _booleans(self.automation_enabled)
        if self.base is not None and type(self.base) is not BaseModule:
            raise ValueError("Expected an immutable base-module snapshot")
        if self.controller is not None and type(self.controller) is not RechargeController:
            raise ValueError("Expected an immutable controller snapshot")


@dataclass(frozen=True)
class Reservation:
    request_id: int
    before: EnergySnapshot


@dataclass(frozen=True)
class DebitEffect:
    """Requested charge-only transaction, awaiting external success evidence."""
    request_id: int
    before: EnergySnapshot
    after: EnergySnapshot
    charge_units: int


@dataclass(frozen=True)
class RechargePlan:
    """Requested one-battery transaction; never an automatic summon trigger."""
    before: EnergySnapshot
    after: EnergySnapshot
    batteries: int = 1


def _valid(module):
    return module is not None and module.installed and module.complete and not module.damaged


class EnergyModel:
    """One request/effect/plan at a time; no unbounded history or timers.

    Request IDs increase within a load. A new load_epoch invalidates all old
    reservations/effects; changing context requires a new load_epoch. Every
    observed snapshot change invalidates a reservation or recharge plan. A debit
    already requested must be confirmed, or explicitly cancelled, before reuse.
    Cancelling never refunds or applies anything; an adapter must not apply a
    cancelled effect later. Same-context reload retains low-warning suppression
    for the current charge cycle; depletion is explained once per load/cycle.
    """

    def __init__(self, config=EnergyConfig()):
        if type(config) is not EnergyConfig:
            raise ValueError("Expected an immutable energy configuration")
        self.config = config
        self._latest = None
        self._base_seen = self._controller_seen = None
        self._reservation = self._effect = self._recharge = None
        self._accepted = False
        self._request_highwater = -1
        self._warning_cycle = None
        self._low_warned = False
        self._depleted_warning = self._fuel_warning = None

    def cancel(self):
        """Revoke pending authority without spending, refunding or warning reset."""
        self._reservation = self._effect = self._recharge = None
        self._accepted = False

    @staticmethod
    def _module_fresh(current, previous):
        if current is None or previous is None or current.identity != previous.identity:
            return True
        if current.version < previous.version or current.version == previous.version and current != previous:
            return False
        if type(current) is BaseModule:
            if current.cycle < previous.cycle:
                return False
            if current.charge > previous.charge and current.cycle <= previous.cycle:
                return False
        return True

    def _sync(self, snapshot):
        if type(snapshot) is not EnergySnapshot:
            raise ValueError("Expected an immutable energy snapshot")
        previous = self._latest
        if previous is not None:
            if snapshot.load_epoch < previous.load_epoch:
                return False
            if snapshot.load_epoch == previous.load_epoch:
                if (snapshot.context != previous.context
                        or snapshot.inventory_version < previous.inventory_version
                        or snapshot.inventory_version == previous.inventory_version
                        and snapshot.ion_batteries != previous.ion_batteries
                        or not self._module_fresh(snapshot.base, self._base_seen)
                        or not self._module_fresh(snapshot.controller, self._controller_seen)):
                    return False
            else:
                self.cancel()
                self._request_highwater = -1
                self._base_seen = self._controller_seen = None
        if self._reservation is not None and snapshot != self._reservation.before:
            self._reservation = None
            self._accepted = False
        if self._recharge is not None and snapshot != self._recharge.before:
            self._recharge = None
        self._latest = snapshot
        if snapshot.base is not None:
            self._base_seen = snapshot.base
            key = (snapshot.context, snapshot.base.identity, snapshot.base.cycle)
            if key != self._warning_cycle:
                self._warning_cycle = key
                self._low_warned = False
        if snapshot.controller is not None:
            self._controller_seen = snapshot.controller
        return True

    def _status(self, snapshot):
        if not snapshot.automation_enabled:
            return "automation.off"
        if not _valid(snapshot.base):
            return "energy.module_unavailable"
        if snapshot.base.maximum != self.config.capacity:
            return "energy.capacity_mismatch"
        if snapshot.base.charge < self.config.summon_cost:
            return "energy.insufficient"
        return "energy.ready"

    def status(self, snapshot):
        return self._status(snapshot) if self._sync(snapshot) else "energy.stale_snapshot"

    def observe(self, snapshot):
        """Return event IDs only; repeated exits do not reset warning history."""
        if not self._sync(snapshot):
            return ()
        status = self._status(snapshot)
        if status not in ("energy.ready", "energy.insufficient"):
            return ()
        events = []
        if status == "energy.ready" and snapshot.base.charge <= self.config.low_threshold:
            if not self._low_warned:
                self._low_warned = True
                events.append("energy.low")
        elif status == "energy.insufficient":
            key = (snapshot.load_epoch, self._warning_cycle)
            if key != self._depleted_warning:
                self._depleted_warning = key
                events.append("energy.depleted")
            if _valid(snapshot.controller) and snapshot.ion_batteries == 0 and key != self._fuel_warning:
                self._fuel_warning = key
                events.append("energy.recharge_fuel_empty")
        return tuple(events)

    def reserve(self, request_id, snapshot):
        _integer(request_id)
        if not self._sync(snapshot) or request_id <= self._request_highwater:
            return None
        self._request_highwater = request_id
        if (self._status(snapshot) != "energy.ready" or self._reservation is not None
                or self._effect is not None or self._recharge is not None):
            return None
        self._reservation = Reservation(request_id, snapshot)
        self._accepted = False
        return self._reservation

    def accept_queue(self, reservation, snapshot, *, accepted):
        """Placement/queue rejection spends nothing and does not imply success."""
        _booleans(accepted)
        if not self._sync(snapshot) or reservation is not self._reservation or reservation is None:
            return False
        self._accepted = accepted
        return accepted

    def confirm_active(self, reservation, snapshot, *, request_id, context, ready, active):
        """Request one debit only for this accepted, matching, ready active pet."""
        _booleans(ready, active)
        if (not self._sync(snapshot) or reservation is None or reservation is not self._reservation
                or not self._accepted or not ready or not active
                or type(request_id) is not int or request_id != reservation.request_id
                or context != snapshot.context):
            return None
        base = snapshot.base
        if base.version == LIMIT:
            self.cancel()
            return None
        after = replace(snapshot, base=replace(base, charge=base.charge - self.config.summon_cost,
                                              version=base.version + 1))
        self._effect = DebitEffect(request_id, snapshot, after, self.config.summon_cost)
        self._reservation = None
        self._accepted = False
        return self._effect

    def confirm_debit(self, effect, after):
        """Acknowledge the exact external result, not merely effect emission."""
        if effect is None or effect is not self._effect or after != effect.after:
            return False
        if not self._sync(after) or self._effect is not effect:
            return False
        self._effect = None
        return True

    def plan_recharge(self, snapshot):
        """Controller presence plus automation ON enables proposed battery use."""
        if (not self._sync(snapshot) or self._status(snapshot) != "energy.insufficient"
                or not _valid(snapshot.controller) or snapshot.ion_batteries == 0
                or self._reservation is not None or self._effect is not None or self._recharge is not None):
            return None
        base = snapshot.base
        if LIMIT in (base.version, base.cycle, snapshot.inventory_version):
            return None
        after = replace(snapshot, base=replace(base, charge=base.maximum, version=base.version + 1,
                                              cycle=base.cycle + 1),
                        ion_batteries=snapshot.ion_batteries - 1,
                        inventory_version=snapshot.inventory_version + 1)
        self._recharge = RechargePlan(snapshot, after)
        return self._recharge

    def confirm_recharge(self, plan, after):
        """Validate exact external refill evidence; emit readiness, never summon."""
        if plan is None or plan is not self._recharge or after != plan.after:
            return ()
        # This particular transition must be validated before _sync invalidates
        # an ordinary pending plan on any observed inventory/module change.
        self._recharge = None
        if not self._sync(after):
            return ()
        return ("energy.recharged_ready",)
