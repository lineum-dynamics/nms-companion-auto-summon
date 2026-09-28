"""In-process bridge to the existing 0.5.1 preference queue; no I/O or hooks.

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
    "Companion Auto Summon 0.5.1 experimental: automation %s; use the CompanionAutoSummon settings."
)
_ABSENT = object()
SETTING_KEYS = ("enabled", "selection_mode", "prefer_same_biome", "planets", "space_stations", "nexus", "rotate_companions")
LOCATION_SETTINGS = {"planets": 3, "space_stations": 2, "nexus": 14}


@dataclass(frozen=True)
class PreferenceState:
    """Owned display values; pending covers any queued preference change."""

    applied: bool | str
    desired: bool | str
    pending: bool
    settings_ok: bool
    stopped: bool


class ToggleToken:
    """Opaque one-use capture. Consumption releases instance/queue references."""

    __slots__ = ("_owner", "_instance", "_queue", "_state", "_setting", "_request", "_used", "_lock")

    def __init__(self, owner, instance, queue, state, setting="enabled"):
        self._owner = owner
        self._instance = instance
        self._queue = queue
        self._state = state
        self._setting = setting
        self._request = queue.get(setting, _ABSENT)
        self._used = False
        self._lock = Lock()

    def _consume(self):
        if not self._lock.acquire(blocking=False):
            return None
        try:
            if self._used:
                return None
            self._used = True
            captured = (self._owner, self._instance, self._queue, self._state, self._setting, self._request)
            self._owner = self._instance = self._queue = self._state = self._setting = self._request = None
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
    def _state(instance, setting="enabled"):
        if type(setting) is not str or setting not in SETTING_KEYS:
            raise ValueError("Unsupported existing preference")
        queue = instance.requested_preferences
        if type(queue) is not dict:
            raise ValueError("Preference queue is unavailable")
        if setting == "enabled":
            applied = instance.auto_enabled
        elif setting == "selection_mode":
            applied = instance.selection_mode_value
        elif setting == "prefer_same_biome":
            applied = instance.prefer_same_biome_value
        elif setting == "rotate_companions":
            applied = instance.rotate_companions_value
        else:
            if (type(instance.allowed_locations) is not frozenset
                    or not instance.allowed_locations <= frozenset(LOCATION_SETTINGS.values())):
                raise ValueError("Location preferences differ from the reviewed contract")
            applied = LOCATION_SETTINGS[setting] in instance.allowed_locations
        desired = queue.get(setting, applied)
        if setting == "selection_mode":
            valid = all(type(value) is str and value in ("last_manual", "random", "by_habitat") for value in (applied, desired))
        else:
            valid = all(type(value) is bool for value in (applied, desired))
        if not valid or any(type(value) is not bool for value in (instance.settings_ok, instance.enabled)):
            raise ValueError("Preference values differ from the reviewed contract")
        return PreferenceState(applied, desired, bool(queue), instance.settings_ok, not instance.enabled)

    def _read(self, capture, setting):
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
            state = self._state(instance, setting)
            if self._resolve() is not instance:
                return None
            if capture:
                if state.stopped:
                    return None
                return ToggleToken(self._owner, instance, instance.requested_preferences, state, setting)
            return state
        except Exception:
            return None
        finally:
            if control_lock is not None:
                control_lock.release()
            self._lock.release()

    def snapshot(self, setting="enabled"):
        """Return display state, including stopped/session-only, or None if unavailable."""
        return self._read(False, setting)

    def capture_toggle(self, setting="enabled"):
        """Capture a prospective activation; this neither queues nor applies it."""
        return self._read(True, setting)

    def bind_notice_icon(self, provider):
        """Bind the same pinned provider to production without invoking it."""
        if not callable(provider) or not self._lock.acquire(blocking=False):
            return False
        control_lock = None
        try:
            instance = self._resolve()
            if instance is None or instance.enabled is not True:
                return False
            candidate_lock = instance.control_lock
            if not candidate_lock.acquire(blocking=False):
                return False
            control_lock = candidate_lock
            if self._resolve() is not instance or instance.enabled is not True:
                return False
            return instance.set_notice_icon_provider(provider) is True
        except Exception:
            return False
        finally:
            if control_lock is not None:
                control_lock.release()
            self._lock.release()

    def commit_toggle(self, token, *, authorize=None):
        """Consume once and queue only the captured setting; False means no write.

        A newer applied queue, changed captured request or replaced/stopped
        runtime refuses the old capture. Unrelated queued settings survive.
        Identical setting writes within the same queue have no revision marker
        in 0.5.0 and cannot be distinguished; the visible desired value governs.
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
            _, expected_instance, expected_queue, expected, setting, expected_request = captured
            instance = self._resolve()
            if instance is None or instance is not expected_instance:
                return False
            candidate_lock = instance.control_lock
            if not candidate_lock.acquire(blocking=False):
                return False
            control_lock = candidate_lock
            current = self._state(instance, setting)
            queue = instance.requested_preferences
            if (current.stopped or queue is not expected_queue
                    or current.applied != expected.applied or current.desired != expected.desired
                    or queue.get(setting, _ABSENT) != expected_request
                    or self._resolve() is not instance):
                return False
            if authorize is not None and authorize() is not True:
                return False
            # This is precisely the production queue, under its own existing
            # lock. Calling its property setter here would deadlock that lock.
            # Only production Player.Update applies/persists the request later.
            queue[setting] = ({"last_manual": "random", "random": "by_habitat", "by_habitat": "last_manual"}[expected.desired]
                              if setting == "selection_mode" else not expected.desired)
            return True
        except Exception:
            return False
        finally:
            if control_lock is not None:
                control_lock.release()
            self._lock.release()
