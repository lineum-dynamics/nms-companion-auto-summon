"""In-process bridge to the existing 0.4.5 preference queue; no I/O or hooks.

The caller supplies live pyMHF registry/module lookups and the verified sibling
production path. Bundle checksums establish source provenance before startup;
the runtime checks below validate identity and the reviewed Python contract,
not a fresh file hash. Hot reload is unsupported. No method applies settings,
reads a save, invokes native functions or creates a production Mod instance.
"""

from dataclasses import dataclass
import os.path
from threading import Lock


PRODUCTION_NAME = "CompanionAutoSummon"
EXPECTED_EXE_SHA256 = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"
EXPECTED_INIT_MARKER = (
    "Companion Auto Summon 0.4.5 experimental: automation %s; use the CompanionAutoSummon settings panel."
)
_ABSENT = object()


@dataclass(frozen=True)
class PreferenceState:
    """Owned display values; pending covers any queued preference change."""

    applied: bool
    desired: bool
    pending: bool
    settings_ok: bool
    stopped: bool


class ToggleToken:
    """Opaque one-use capture. Consumption releases instance/queue references."""

    __slots__ = ("_owner", "_instance", "_queue", "_state", "_enabled_request", "_used", "_lock")

    def __init__(self, owner, instance, queue, state):
        self._owner = owner
        self._instance = instance
        self._queue = queue
        self._state = state
        self._enabled_request = queue.get("enabled", _ABSENT)
        self._used = False
        self._lock = Lock()

    def _consume(self):
        if not self._lock.acquire(blocking=False):
            return None
        try:
            if self._used:
                return None
            self._used = True
            captured = (self._owner, self._instance, self._queue, self._state, self._enabled_request)
            self._owner = self._instance = self._queue = self._state = self._enabled_request = None
            return captured
        finally:
            self._lock.release()


def _path(value):
    # Lexical normalization only: no resolve/stat/file access on a game callback.
    if type(value) is not str or not os.path.isabs(value):
        return None
    return os.path.normcase(os.path.normpath(value))


class PreferenceBridge:
    """Snapshot/capture/commit against one actual registered production instance.

    get_registered should read mod_manager.mods.get('CompanionAutoSummon');
    get_module should read sys.modules.get('CompanionAutoSummon'). Never use a
    string key with mod_manager.__getitem__, which returns a logging proxy.
    Missing registry entries can be retried during startup. Replacement after
    binding permanently makes this bridge unavailable; restart the bundle.
    """

    def __init__(self, production_path, *, get_registered, get_module):
        self._path = _path(production_path)
        if self._path is None or not callable(get_registered) or not callable(get_module):
            raise ValueError("An absolute production path and two live lookups are required")
        self._get_registered = get_registered
        self._get_module = get_module
        self._bound = None
        self._invalid = False
        self._owner = object()
        self._lock = Lock()

    def _resolve(self):
        if self._invalid:
            return None
        instance = self._get_registered()
        module = self._get_module()
        if instance is None:
            if self._bound is not None:
                self._invalid = True
            return None
        cls = type(instance)
        initializer = getattr(cls, "__init__", None)
        code = getattr(initializer, "__code__", None)
        if (module is None or getattr(module, "__name__", None) != PRODUCTION_NAME
                or _path(getattr(module, "__file__", None)) != self._path
                or cls is not getattr(module, PRODUCTION_NAME, None)
                or cls.__name__ != PRODUCTION_NAME or cls.__module__ != PRODUCTION_NAME
                or cls.__dict__.get("_disabled") is not False
                or getattr(instance, "_abc_initialised", None) is not True
                or getattr(initializer, "__globals__", None) is not module.__dict__
                or code is None or EXPECTED_INIT_MARKER not in code.co_consts
                or getattr(module, "EXPECTED_PYMHF", None) != "0.2.4"
                or getattr(module, "EXPECTED_EXE_SHA256", None) != EXPECTED_EXE_SHA256):
            if self._bound is not None:
                self._invalid = True
            return None
        if self._bound is not None and instance is not self._bound:
            self._invalid = True
            return None
        self._bound = instance
        return instance

    @staticmethod
    def _state(instance):
        queue = instance.requested_preferences
        if type(queue) is not dict:
            raise ValueError("Preference queue is unavailable")
        values = (instance.auto_enabled, queue.get("enabled", instance.auto_enabled),
                  instance.settings_ok, instance.enabled)
        if any(type(value) is not bool for value in values):
            raise ValueError("Preference values differ from the reviewed contract")
        return PreferenceState(values[0], values[1], bool(queue), values[2], not values[3])

    def _read(self, capture):
        if not self._lock.acquire(blocking=False):
            return None
        control_lock = None
        try:
            instance = self._resolve()
            if instance is None:
                return None
            candidate_lock = instance.control_lock
            if not candidate_lock.acquire(blocking=False):
                return None
            control_lock = candidate_lock
            state = self._state(instance)
            if self._resolve() is not instance:
                return None
            if capture:
                if state.stopped:
                    return None
                return ToggleToken(self._owner, instance, instance.requested_preferences, state)
            return state
        except Exception:
            return None
        finally:
            if control_lock is not None:
                control_lock.release()
            self._lock.release()

    def snapshot(self):
        """Return display state, including stopped/session-only, or None if unavailable."""
        return self._read(False)

    def capture_toggle(self):
        """Capture a prospective activation; this neither queues nor applies it."""
        return self._read(True)

    def commit_toggle(self, token, *, authorize=None):
        """Consume once and queue only enabled; False means nothing was queued.

        A newer applied queue, changed enabled request or replaced/stopped
        runtime refuses the old capture. Unrelated queued settings survive.
        Identical enabled writes within the same queue have no revision marker
        in 0.4.5 and cannot be distinguished; the visible desired value governs.
        An optional pure, nonblocking authorization predicate runs under both
        locks immediately before the write and must return literal True. It
        must not perform I/O, native calls or reenter the preference bridge.
        None permits the write after the bridge's existing validations.
        """
        if type(token) is not ToggleToken:
            return False
        captured = token._consume()
        if captured is None or captured[0] is not self._owner:
            return False
        if not self._lock.acquire(blocking=False):
            return False
        control_lock = None
        try:
            _, expected_instance, expected_queue, expected, expected_enabled = captured
            instance = self._resolve()
            if instance is None or instance is not expected_instance:
                return False
            candidate_lock = instance.control_lock
            if not candidate_lock.acquire(blocking=False):
                return False
            control_lock = candidate_lock
            current = self._state(instance)
            queue = instance.requested_preferences
            if (current.stopped or queue is not expected_queue
                    or current.applied != expected.applied or current.desired != expected.desired
                    or queue.get("enabled", _ABSENT) is not expected_enabled
                    or self._resolve() is not instance):
                return False
            if authorize is not None and authorize() is not True:
                return False
            # This is precisely the production queue, under its own existing
            # lock. Calling its property setter here would deadlock that lock.
            # Only production Player.Update applies/persists the request later.
            queue["enabled"] = not expected.desired
            return True
        except Exception:
            return False
        finally:
            if control_lock is not None:
                control_lock.release()
            self._lock.release()
