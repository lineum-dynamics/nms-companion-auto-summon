"""Pure decision policy for summoning an owned pet after leaving a ship.

This module neither reads game state nor calls the game. The adapter supplies
observations and performs the one returned summon request.
"""

import math


class AutoPetPolicy:
    """Remember a manual favorite and allow one in-flight request per exit.

    Acceptance finishes the exit; rejection retains its fixed choice for a
    paced retry. The adapter supplies fresh native checks and retry pacing.

    ``now`` must come from one monotonic clock. A backward clock step cancels
    the current exit; invalid timestamps cancel it and raise ``ValueError``.
    On-foot stability starts with the first positive observation, so time in
    a forbidden location, in transit, or before that observation cannot count
    toward it. The adapter supplies the game's supported summon locations.
    """

    def __init__(self, delay_seconds=1.5, expiry_seconds=None):
        self._delay = self._finite_number(delay_seconds, "delay_seconds")
        self._expiry = (None if expiry_seconds is None
                        else self._finite_number(expiry_seconds, "expiry_seconds"))
        if self._delay < 0:
            raise ValueError("delay_seconds must be non-negative")
        if self._expiry is not None and self._expiry <= 0:
            raise ValueError("expiry_seconds must be positive")
        self.reset()

    @staticmethod
    def _finite_number(value, name):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a finite number")
        try:
            result = float(value)
        except (ValueError, OverflowError):
            raise ValueError(f"{name} must be a finite number") from None
        if not math.isfinite(result):
            raise ValueError(f"{name} must be a finite number")
        return result

    def _cancel_pending(self):
        self._ejected_at = None
        self._stable_since = None
        self._exit_slot = None
        self._in_flight = False

    def _observe_time(self, now):
        try:
            timestamp = self._finite_number(now, "now")
        except ValueError:
            self._cancel_pending()
            raise
        reversed_time = self._last_time is not None and timestamp < self._last_time
        self._last_time = timestamp
        if reversed_time:
            self._cancel_pending()
            return None
        return timestamp

    def remember(self, slot: int):
        """Record a manual or restored choice; replacing it cancels an old exit."""
        if isinstance(slot, bool) or not isinstance(slot, int) or not 0 <= slot < 30:
            raise ValueError("slot must be an integer from 0 through 29")
        self._slot = slot
        self._cancel_pending()

    def eject(self, now: float, *, random_selection=False):
        """Arm a manual choice, or defer this exit's choice to the adapter.

        Random mode may arm without a manual favorite. Its later choice never
        changes that favorite or restarts the exit deadline/stability clock.
        """
        if type(random_selection) is not bool:
            raise ValueError("random_selection must be a bool")
        timestamp = self._observe_time(now)
        if timestamp is None:
            return
        self._cancel_pending()
        if self._slot is not None or random_selection:
            self._ejected_at = timestamp
            self._exit_slot = None if random_selection else self._slot

    def select_for_exit(self, slot: int):
        """Bind an unselected pending exit once, without changing its clocks."""
        if isinstance(slot, bool) or not isinstance(slot, int) or not 0 <= slot < 30:
            raise ValueError("slot must be an integer from 0 through 29")
        if not self.pending:
            return False
        if self._exit_slot is not None:
            raise ValueError("this exit already has a companion")
        self._exit_slot = slot
        return True

    def enter_ship(self):
        """Cancel an exit without forgetting the last manual pet choice."""
        self._cancel_pending()

    def reset(self):
        """Forget all session state, for example when loading another save."""
        self._slot = None
        self._last_time = None
        self._cancel_pending()

    @property
    def last_slot(self) -> int | None:
        """Last remembered manual choice in this session, if any."""
        return self._slot

    @property
    def pending(self) -> bool:
        """Whether an exit is still waiting for a possible summon request."""
        return self._ejected_at is not None

    @property
    def pending_slot(self) -> int | None:
        """Companion bound to this exit, separate from the manual favorite."""
        return self._exit_slot

    def resolve(self, accepted: bool):
        """Complete one queue attempt; rejection retains the same exit/choice."""
        if type(accepted) is not bool:
            raise ValueError("accepted must be a bool")
        if not self._in_flight:
            return False
        if accepted:
            self._cancel_pending()
        else:
            self._in_flight = False
        return True

    def tick(
        self,
        now: float,
        *,
        on_foot_in_summon_location: bool,
        active_pet: int,
        native_pending_pet: int,
        eligible: bool,
    ) -> int | None:
        """Offer one slot, or None; the adapter must resolve its queue result.

        An existing or natively queued pet cancels the pending exit. Unknown
        index sentinels cannot summon either: both indices must equal -1.
        The default has no expiry. An optional finite deadline is available to
        callers that explicitly need one. Retry pacing belongs to the adapter.
        """
        timestamp = self._observe_time(now)
        if timestamp is None or self._ejected_at is None:
            return None
        if self._expiry is not None and timestamp - self._ejected_at >= self._expiry:
            self._cancel_pending()
            return None
        if active_pet >= 0 or native_pending_pet >= 0:
            self._cancel_pending()
            return None
        if not on_foot_in_summon_location:
            self._stable_since = None
            return None
        if self._stable_since is None:
            self._stable_since = timestamp
        if timestamp - self._stable_since < self._delay:
            return None
        if (not eligible or active_pet != -1 or native_pending_pet != -1
                or self._exit_slot is None or self._in_flight):
            return None
        slot = self._exit_slot
        self._in_flight = True
        return slot
