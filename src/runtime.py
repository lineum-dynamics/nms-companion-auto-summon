# This fragment is appended to policy.py by build.py. Do not install fragments.
import ctypes as C
import hashlib
import logging
import math
import os
import random
from enum import Enum
from threading import Lock, get_native_id
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import time

from pymhf import Mod
from pymhf.core import _internal
from pymhf.core.hooking import static_function_hook
from pymhf.gui.decorators import BOOLEAN, ENUM, STRING


EXPECTED_EXE_SHA256 = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"
EXPECTED_PYMHF = "0.2.4"
PRODUCT_NAME = "Companion Auto Summon for No Man's Sky"
PRODUCT_AUTHOR = "Lineum Dynamics"
LOGGER = logging.getLogger("CompanionAutoSummon")

# All addresses are RVAs in the exact Steam 25442159 / Cosmos 7.04 executable.
# Derived offline from its native quick-menu SummonPet branch and player update.
APPLICATION_PTR_RVA = 0x6E7AAE8
LOCAL_PLAYER_OFFSET = 0x71C690
LOCATION_OFFSET = 0x57A584
ACTIVE_PET_OFFSET = 0x29A1C0
PENDING_PET_OFFSET = 0x6010
PET_TABLE_OFFSET = 0xE10D0
PET_ENTRY_SIZE = 0x24A0
PET_SEED_OFFSET = 0x2330
PET_BIRTH_TIME_OFFSET = 0x23C0
PET_RESOURCE_OFFSET = 0x2370
PET_BIOME_OFFSET = 0x2480
# Read-only offsets verified against this exact build's native pet adoption path.
SOLAR_SYSTEM_PTR_OFFSET = 0x71AF70
PLANET_COUNT_OFFSET = 0x2544
CURRENT_PLANET_INDEX_OFFSET = 0x5196D0
PLANET_ENTRY_SIZE = 0xD9170
PLANET_BIOME_OFFSET = 0x6148
PLANET_BIOME_SUBTYPE_OFFSET = 0x614C
CONCRETE_BIOMES = frozenset(range(16)) - {11}  # Exclude Test; All is 16.
SAVE_UNIVERSAL_ID_OFFSET = 0x8980
NOTIFICATIONS_OFFSET = 0x837B40
NOTICE_COUNT_OFFSET = 0x28C
NOTICE_BLOCK_OFFSET = 0x4BF50C
# Mirror the location set admitted by this build's native ownership eligibility.
# Membership alone never replaces that native check or placement validation.
SUPPORTED_SUMMON_LOCATIONS = frozenset({2, 3, 14})
DIAGNOSTIC_WAIT_LIMIT = 8
# Passive evidence budgets only; none controls summon timing or retry behavior.
POST_QUEUE_OBSERVATION_SECONDS = 15.0
POST_QUEUE_OBSERVATION_MAX_UPDATES = 4096  # Includes foreign ownership callbacks.
POST_QUEUE_OBSERVATION_TRANSITION_LIMIT = 8
PET_ARC_OFFSET = 0x1B9140
PET_PREVIEW_OFFSET = 0x1B9300
PET_EMOTE_OFFSET = 0x1B937D
SUMMON_ARC_RANGE_RVA = 0x52381E0
SUMMON_HAND_OFFSET = 0x30E7FC
PHYSICS_CONTEXT_OFFSET = 0x2A8
PLACEMENT_PROBE_INTERVAL = 0.5
PLACEMENT_MAX_FRAME_GAP = 0.25
QUICK_MENU_ACTION_OFFSET = 0x4
QUICK_MENU_SLOT_OFFSET = 0x84
SUMMON_PET_ACTION = 46
SelectionMode = Enum("SelectionMode", {"Last manually selected": "last_manual", "Random": "random"})


def selection_store_path():
    """Use the current Windows user's data directory, never the game folder."""
    local_data = os.environ.get("LOCALAPPDATA")
    if not local_data or not Path(local_data).is_absolute():
        raise SelectionStoreError("LOCALAPPDATA must be an absolute directory path")
    # Stable legacy directory preserves existing settings and per-save choices.
    return Path(local_data) / "NMS-AutoPet" / "state.json"


def settings_store_path():
    return selection_store_path().with_name("settings.json")


def supported_runtime():
    """Gate our hooks before the mod loader instantiates this class."""
    try:
        if not _internal.IS_INJECTED or _internal.BASE_ADDRESS <= 0:
            return False
        if version("pymhf") != EXPECTED_PYMHF:
            return False
        with Path(_internal.BINARY_PATH).open("rb") as binary:
            return hashlib.file_digest(binary, "sha256").hexdigest() == EXPECTED_EXE_SHA256
    except (OSError, ValueError, TypeError, AttributeError, PackageNotFoundError):
        return False


# Each definition is a native wrapper, not a Python implementation of the game.
# No wrapper below is called during module import.
@static_function_hook(offset=0x146AC90)
def cas_queue_pet(player: C.c_void_p, slot: C.c_int32) -> None:
    ...


@static_function_hook(offset=0x1526940)
def cas_manual_trigger(menu: C.c_void_p, action: C.c_void_p, called_as_menu: C.c_bool) -> C.c_bool:
    ...


@static_function_hook(offset=0x146A410)
def cas_can_summon(player: C.c_void_p, slot: C.c_int32) -> C.c_bool:
    ...


@static_function_hook(offset=0x5066A0)
def cas_pet_owner_update(owner: C.c_void_p, dt: C.c_float) -> None:
    ...


@static_function_hook(offset=0x1438040)
def cas_refresh_pet_placement(arc: C.c_void_p, range1: C.c_float, range2: C.c_float,
                             hand: C.c_uint32) -> None:
    ...


@static_function_hook(offset=0x505B70)
def cas_owned_pet_eligible(owner: C.c_void_p, slot: C.c_int32) -> C.c_bool:
    ...


@static_function_hook(offset=0x60B770)
def cas_use_summon_hand() -> C.c_bool:
    ...


@static_function_hook(offset=0x17479D0)
def cas_eject(ship: C.c_void_p, player: C.c_void_p, animate: C.c_bool,
             force_during_communicator: C.c_bool) -> None:
    ...


@static_function_hook(offset=0x1479490)
def cas_enter_cockpit(player: C.c_void_p) -> None:
    ...


@static_function_hook(offset=0x1440CD0)
def cas_player_update(player: C.c_void_p, dt: C.c_float) -> None:
    ...


@static_function_hook(offset=0x56FA50)
def cas_load_save(player_state: C.c_void_p, common_data: C.c_void_p, state_data: C.c_void_p,
                 network_client: C.c_bool, resetting: C.c_bool, arg6: C.c_uint32) -> C.c_bool:
    ...


@static_function_hook(offset=0x9B8300)
def cas_add_timed_message(notifications: C.c_void_p, message: C.c_void_p,
                         duration: C.c_float, colour: C.c_void_p,
                         audio: C.c_uint32, icon: C.c_void_p,
                         flag7: C.c_bool, extra_time: C.c_float,
                         flag9: C.c_bool, flag10: C.c_bool, flag11: C.c_bool) -> None:
    ...


class CompanionAutoSummon(Mod):
    """Experimental summon after a ship exit where native game rules permit it."""

    _version = "0.4.9-experimental"
    _author = PRODUCT_AUTHOR
    _description = PRODUCT_NAME
    _disabled = not supported_runtime()

    def __init__(self):
        self.policy = CompanionAutoSummonPolicy()
        self.enabled = True
        # User preference is separate from the runtime safety latch above.
        self.auto_enabled = True
        self.allowed_locations = SUPPORTED_SUMMON_LOCATIONS
        self.selection_mode_value = "last_manual"
        self.prefer_same_biome_value = True
        self.settings_store = None
        self.settings_ok = True
        self.control_lock = Lock()
        self.requested_preferences = {}
        self.pending_notice = None
        self.notifications_ok = True
        self.in_auto_call = False
        self.app_identity = None
        self.pet_identity = None
        self.store = None
        self.save_key = None
        self.saved_selection = None
        self.persistence_ok = True
        self._exit_diagnostic = None
        self._summon_observation = None
        self._placement_warmed = False
        self._pending_pet_identity = None
        self._next_probe_at = 0.0
        self._probe_primed_at = None
        self._probe_location = None
        self._probe_physics_context = None
        self._queue_rejection_logged = False
        self._load_summon_pending = False
        self._manual_attribution_ok = True
        self._manual_lock = Lock()
        self._manual_action = None
        self._manual_epoch = 0
        self._notice_icon_provider = None
        # Mod.__init__ uses inspect.getmembers(self), which evaluates properties.
        # Initialize their backing fields before the framework discovers them.
        super().__init__()
        try:
            self.store = PetSelectionStore(selection_store_path())
        except SelectionStoreError:
            self._persistence_failed()
        try:
            self.settings_store = CompanionAutoSummonSettingsStore(settings_store_path())
            preferences = self.settings_store.load_preferences()
            self.auto_enabled = preferences["enabled"]
            self.allowed_locations = frozenset(preferences["locations"])
            self.selection_mode_value = preferences["selection_mode"]
            self.prefer_same_biome_value = preferences["prefer_same_biome"]
        except (SelectionStoreError, SettingsStoreError):
            # An unreadable preference must not silently turn automation back on.
            self.auto_enabled = False
            self.settings_ok = False
            LOGGER.exception("Companion Auto Summon settings unavailable; automation starts OFF. The settings panel can enable it for this session.")
        LOGGER.info("Companion Auto Summon 0.4.9 experimental: automation %s; use the CompanionAutoSummon settings panel.",
                    "ON" if self.auto_enabled else "OFF")

    @property
    @BOOLEAN("Automatically summon companion")
    def automatic_summoning(self):
        if not self.enabled:
            return False
        return self._visible_preferences()["enabled"]

    @automatic_summoning.setter
    def automatic_summoning(self, value):
        # The GUI runs on another thread. Queue the latest desired state only;
        # file persistence and all game operations happen on local Player.Update.
        if type(value) is bool:
            self._queue_preference("enabled", value)

    @property
    @BOOLEAN("Planets")
    def planets(self):
        return 3 in self._visible_preferences()["locations"]

    @planets.setter
    def planets(self, value):
        if type(value) is bool:
            self._queue_preference("planets", value)

    @property
    @BOOLEAN("Space stations")
    def space_stations(self):
        return 2 in self._visible_preferences()["locations"]

    @space_stations.setter
    def space_stations(self, value):
        if type(value) is bool:
            self._queue_preference("space_stations", value)

    @property
    @BOOLEAN("Nexus")
    def nexus(self):
        return 14 in self._visible_preferences()["locations"]

    @nexus.setter
    def nexus(self, value):
        if type(value) is bool:
            self._queue_preference("nexus", value)

    @property
    @ENUM("Companion selection", SelectionMode)
    def companion_selection(self):
        return SelectionMode(self._visible_preferences()["selection_mode"])

    @companion_selection.setter
    def companion_selection(self, value):
        if isinstance(value, SelectionMode):
            self._queue_preference("selection_mode", value.value)

    @property
    @BOOLEAN("Prefer same biome in Random mode")
    def prefer_same_biome(self):
        return self._visible_preferences()["prefer_same_biome"]

    @prefer_same_biome.setter
    def prefer_same_biome(self, value):
        if type(value) is bool:
            self._queue_preference("prefer_same_biome", value)

    def _queue_preference(self, key, value):
        if self.enabled:
            with self.control_lock:
                self.requested_preferences[key] = value

    def _current_preferences(self):
        return {"enabled": self.auto_enabled, "locations": sorted(self.allowed_locations),
                "selection_mode": self.selection_mode_value,
                "prefer_same_biome": self.prefer_same_biome_value}

    def _merged_preferences_locked(self):
        preferences = self._current_preferences()
        for key in ("enabled", "selection_mode", "prefer_same_biome"):
            if key in self.requested_preferences:
                preferences[key] = self.requested_preferences[key]
        locations = set(preferences["locations"])
        for key, location in (("planets", 3), ("space_stations", 2), ("nexus", 14)):
            if key in self.requested_preferences:
                if self.requested_preferences[key]:
                    locations.add(location)
                else:
                    locations.discard(location)
        preferences["locations"] = sorted(locations)
        return preferences

    def _visible_preferences(self):
        with self.control_lock:
            return self._merged_preferences_locked()

    def _controls_pending(self):
        with self.control_lock:
            return bool(self.requested_preferences)

    @property
    @STRING("Status")
    def control_status(self):
        if not self.enabled:
            return "Stopped after a runtime error; restart required."
        if self._controls_pending():
            return "Change pending; return to the game to apply and save."
        suffix = "" if self.settings_ok else " (session only)"
        if self.auto_enabled and (self.policy.pending or self._load_summon_pending):
            return "Waiting for a suitable place" + suffix
        return ("Automatic summoning ON" if self.auto_enabled else "Automatic summoning OFF") + suffix

    @property
    @STRING("Companion")
    def companion_status(self):
        if self._visible_preferences()["selection_mode"] == "random":
            return "Random eligible owned companion per request; manual favorite is preserved."
        slot = self.policy.last_slot
        if slot is not None:
            return f"Selected companion: slot {slot + 1}"
        if self.saved_selection is not None:
            return "Remembered companion; waiting for ownership verification."
        return "No companion selected. Summon one manually in the game."

    def _apply_control(self):
        with self.control_lock:
            if not self.requested_preferences:
                return
            previous = self._current_preferences()
            requested = self._merged_preferences_locked()
            self.requested_preferences = {}
            if requested == previous:
                return
            self.auto_enabled = requested["enabled"]
            self.allowed_locations = frozenset(requested["locations"])
            self.selection_mode_value = requested["selection_mode"]
            self.prefer_same_biome_value = requested["prefer_same_biome"]
        self._invalidate_manual_action()
        self._finish_exit_diagnostic("cancelled by settings change")
        self._load_summon_pending = False
        self.policy.enter_ship()  # Cancel pending summons; retain the chosen pet.
        if self.settings_ok:
            try:
                self.settings_store.save_preferences(requested)
            except SettingsStoreError:
                self.settings_ok = False
                LOGGER.exception("Companion Auto Summon toggle applies to this session only; settings file preserved.")
        state = "ON" if self.auto_enabled else "OFF"
        suffix = "" if self.settings_ok else " (session only)"
        self.pending_notice = (f"Companion Auto Summon: {state}{suffix}" if previous["enabled"] != self.auto_enabled
                               else f"Companion Auto Summon: settings updated{suffix}")
        LOGGER.info(self.pending_notice)
        LOGGER.info("Companion Auto Summon preferences: locations=%s selection=%s prefer_same_biome=%s.",
                    requested["locations"], requested["selection_mode"], requested["prefer_same_biome"])

    def _finish_exit_diagnostic(self, reason):
        self._finish_summon_observation(reason)
        # All cancellation/context transitions invalidate the previous ray jobs
        # for automation. The game owns their actual cleanup; never alter them.
        self._reset_probe()
        self._pending_pet_identity = None
        self._queue_rejection_logged = False
        if self._exit_diagnostic is not None:
            LOGGER.info("Companion Auto Summon exit finished: %s.", reason)
            self._exit_diagnostic = None

    def _finish_summon_observation(self, reason):
        """Discard only passive evidence; never alter the summon policy."""
        observation = self._summon_observation
        self._summon_observation = None
        if observation is None:
            return
        try:
            last_state = observation["last_state"]
            LOGGER.info(
                "Companion Auto Summon post-queue observation finished: %s; source=%s "
                "requested_slot=%d elapsed=%.2fs updates=%d callbacks=%d logical_active_seen=%s "
                "last_active_pet=%s last_native_pending_pet=%s. Rendering unverified; no automatic retry.",
                reason, observation["source"], observation["slot"] + 1,
                observation["last_time"] - observation["accepted_at"], observation["updates"],
                observation["callbacks"], observation["active_seen"],
                last_state[0] if last_state is not None else None,
                last_state[1] if last_state is not None else None,
            )
        except Exception:
            # Diagnostic/logging faults must not stop working automation.
            pass

    def _arm_summon_observation(self, app, slot, identity, source, location, now):
        """Copy acceptance metadata after policy completion; no native operations."""
        try:
            if (type(identity) is not bytes or len(identity) != 16
                    or not 0 <= slot < 30 or not math.isfinite(now)):
                return
            self._summon_observation = {
                "app": app, "slot": slot, "identity": bytes(identity),
                "source": source if source in ("save load", "ship exit") else "unknown",
                "location": location, "accepted_at": now, "last_time": now,
                "updates": 0, "callbacks": 0, "last_state": None, "active_seen": False,
                "transition_logs": 0, "suppressed": False,
            }
            LOGGER.info(
                "Companion Auto Summon post-queue observation started: source=%s requested_slot=%d; "
                "queue acceptance does not establish active appearance.",
                self._summon_observation["source"], slot + 1,
            )
        except Exception:
            self._finish_summon_observation("observer error while starting")

    def _observe_queued_summon(self, owner, dt):
        """Bounded read-only follow-up, separate from policy and placement work."""
        observation = self._summon_observation
        if observation is None:
            return
        try:
            if observation["callbacks"] >= POST_QUEUE_OBSERVATION_MAX_UPDATES:
                self._finish_summon_observation("callback limit")
                return
            observation["callbacks"] += 1
            if not self.enabled or not self.auto_enabled:
                self._finish_summon_observation("automation unavailable or OFF")
                return
            if self._controls_pending():
                self._finish_summon_observation("settings change pending")
                return
            now = time.monotonic()
            if not math.isfinite(now) or now < observation["last_time"]:
                self._finish_summon_observation("invalid observation clock")
                return
            observation["last_time"] = now
            if now - observation["accepted_at"] >= POST_QUEUE_OBSERVATION_SECONDS:
                self._finish_summon_observation("time limit")
                return
            # The first native read is the current application slot. Never dereference the
            # retained identity as an address or use _app_for_player here: its
            # lifecycle side effects belong to the normal automation path.
            app = C.c_void_p.from_address(_internal.BASE_ADDRESS + APPLICATION_PTR_RVA).value
            if not app or app != observation["app"] or app != self.app_identity:
                self._finish_summon_observation("application context unavailable or changed")
                return
            if owner != app + PET_TABLE_OFFSET:
                if observation["callbacks"] >= POST_QUEUE_OBSERVATION_MAX_UPDATES:
                    self._finish_summon_observation("callback limit")
                return  # This callback belongs to another ownership object.
            observation["updates"] += 1
            player = app + LOCAL_PLAYER_OFFSET
            active = C.c_int32.from_address(app + ACTIVE_PET_OFFSET).value
            pending = C.c_int32.from_address(player + PENDING_PET_OFFSET).value
            location = C.c_int32.from_address(app + LOCATION_OFFSET).value
            preview = C.c_int32.from_address(owner + PET_PREVIEW_OFFSET).value
            emote = C.c_ubyte.from_address(owner + PET_EMOTE_OFFSET).value
            if not (-1 <= active < 30 and -1 <= pending < 30 and -1 <= preview < 30):
                self._finish_summon_observation("invalid companion indices")
                return
            if (location not in SUPPORTED_SUMMON_LOCATIONS or location != observation["location"]
                    or location not in self.allowed_locations):
                self._finish_summon_observation("summon location unavailable or changed")
                return
            if preview != -1 or emote != 0:
                self._finish_summon_observation("native companion preview or emote")
                return
            slot = observation["slot"]
            if self._pet_seed(app, slot) != observation["identity"]:
                self._finish_summon_observation("companion identity changed")
                return
            if active not in (-1, slot) or pending not in (-1, slot):
                self._finish_summon_observation("different companion active or queued")
                return
            if active == slot:
                # A logical index is not rendering evidence. Retain the original
                # observation window to capture a later disappearance without retrying.
                observation["active_seen"] = True
            advancing = math.isfinite(dt) and dt > 0
            state = (active, pending, advancing)
            if state != observation["last_state"]:
                if active == slot:
                    reason = "expected native active index observed; rendering unverified"
                elif observation["active_seen"]:
                    reason = "expected native active index no longer present; cause unknown"
                else:
                    reason = ("native queue still pending" if pending == slot else
                              "queue cleared without active observation; outcome indeterminate")
                if observation["transition_logs"] < POST_QUEUE_OBSERVATION_TRANSITION_LIMIT:
                    LOGGER.info(
                        "Companion Auto Summon post-queue observation: %s; source=%s "
                        "elapsed=%.2fs location=%d advancing=%s active_pet=%d native_pending_pet=%d.",
                        reason, observation["source"], now - observation["accepted_at"],
                        location, advancing, active, pending,
                    )
                    observation["transition_logs"] += 1
                elif not observation["suppressed"]:
                    LOGGER.info("Companion Auto Summon post-queue transition log limit reached; awaiting terminal observation.")
                    observation["suppressed"] = True
                observation["last_state"] = state
            if observation["callbacks"] >= POST_QUEUE_OBSERVATION_MAX_UPDATES:
                self._finish_summon_observation("callback limit")
        except Exception:
            self._finish_summon_observation("observer error")

    def _trace_policy_tick(self, now, *, location, advancing, active_pet, native_pending,
                           eligible, slot, wait_reason=None):
        """Describe existing observations; never change policy or query the game.

        Unchanged frames are silent. Cap wait transitions per exit, while always
        retaining the terminal result and the small set of observed wait reasons.
        """
        diagnostic = self._exit_diagnostic
        if diagnostic is None:
            return
        if active_pet >= 0:
            reason = "active_companion"
        elif native_pending >= 0:
            reason = "native_pending_companion"
        elif location not in SUPPORTED_SUMMON_LOCATIONS:
            reason = "not_summon_location"
        elif location not in self.allowed_locations:
            reason = "location_disabled"
        elif not advancing:
            reason = "paused_or_zero_dt"
        elif wait_reason is not None:
            reason = wait_reason
        elif not eligible:
            reason = "eligibility_false"
        else:
            reason = "stability_delay"
        elapsed = now - diagnostic["armed_at"]
        state = (reason, location, advancing, active_pet, native_pending, eligible)
        # These are observed states, not a claim about time spent in each state
        # between callbacks. Placement failure retains the exit intent.
        if active_pet == -1 and native_pending == -1:
            diagnostic["observed_waits"].add(reason)
        if slot is not None:
            if not diagnostic.get("request_logged", False):
                LOGGER.info("Companion Auto Summon exit ready after %.2fs; requesting slot %d.", elapsed, slot + 1)
                diagnostic["request_logged"] = True
            return
        if not self.policy.pending:
            # Match the existing policy's priority: backwards clock, deadline,
            # then another active/native-pending pet. Only diagnose its result.
            if now < diagnostic["last_time"]:
                outcome = "cancelled by backwards clock"
            elif self.policy._expiry is not None and elapsed >= self.policy._expiry:
                outcome = "expired"
            elif active_pet >= 0 or native_pending >= 0:
                outcome = "cancelled by active or native-pending companion"
            else:
                outcome = "cancelled by policy"
            LOGGER.info(
                "Companion Auto Summon exit %s after %.2fs; final_wait=%s location=%d advancing=%s "
                "eligible=%s active_pet=%d native_pending_pet=%d observed_waits=%s.",
                outcome, elapsed, reason, location, advancing, eligible, active_pet, native_pending,
                ",".join(sorted(diagnostic["observed_waits"])) or "none",
            )
            self._exit_diagnostic = None
            self._placement_warmed = False
            return
        if state != diagnostic["last_state"]:
            if diagnostic["wait_logs"] < DIAGNOSTIC_WAIT_LIMIT:
                LOGGER.info(
                    "Companion Auto Summon exit waiting: %s; elapsed=%.2fs location=%d advancing=%s "
                    "eligible=%s active_pet=%d native_pending_pet=%d.",
                    reason, elapsed, location, advancing, eligible, active_pet, native_pending,
                )
                diagnostic["wait_logs"] += 1
            elif not diagnostic["suppressed"]:
                LOGGER.info("Companion Auto Summon exit wait log limit reached; further transitions suppressed until final result.")
                diagnostic["suppressed"] = True
        diagnostic["last_state"] = state
        diagnostic["last_time"] = now

    def set_notice_icon_provider(self, provider):
        """Accept one process-lifetime, read-only icon provider from the menu."""
        if not callable(provider):
            return False
        if self._notice_icon_provider is None:
            self._notice_icon_provider = provider
        return self._notice_icon_provider is provider

    def _notice_icon_handle(self):
        provider = self._notice_icon_provider
        if provider is None:
            return 0
        try:
            handle = provider()
            if type(handle) is int and 0 <= handle <= 0xFFFFFFFF:
                return handle
        except Exception:
            pass
        # Presentation failure never suppresses the text or changes automation.
        return 0

    def _show_pending_notice(self, app):
        if not self.notifications_ok:
            self.pending_notice = None
            return
        if self.pending_notice is None:
            return
        try:
            notifications = app + NOTIFICATIONS_OFFSET
            # These are the native function's two early-out checks. Leave busy
            # game notifications alone and retain only our latest status message.
            if C.c_uint32.from_address(notifications + NOTICE_COUNT_OFFSET).value > 3:
                return
            if not C.c_float.from_address(app + NOTICE_BLOCK_OFFSET).value < 0:
                return
            message = C.create_string_buffer(self.pending_notice.encode("ascii")[:511], 512)
            # AddTimedMessage uses MOVAPS on the supplied RGBA, requiring 16-byte
            # alignment. Keep the allocation alive through the synchronous copy.
            colour_storage = C.create_string_buffer(31)
            colour_address = (C.addressof(colour_storage) + 15) & ~15
            colour = (C.c_float * 4).from_address(colour_address)
            colour[:] = (1.0, 1.0, 1.0, 1.0)
            icon_handle = self._notice_icon_handle()
            icon = C.c_uint32(icon_handle)
            self.pending_notice = None  # One attempt, no duplicate native retry.
            cas_add_timed_message(notifications, C.addressof(message), 5.5,
                                 colour_address, 0, C.addressof(icon),
                                 False, 0.0, False, False, icon_handle == 0)
        except Exception:
            self.notifications_ok = False
            self.pending_notice = None
            LOGGER.exception("Companion Auto Summon HUD confirmation unavailable; see the settings panel for status.")

    def _app_for_player(self, player):
        app = C.c_void_p.from_address(_internal.BASE_ADDRESS + APPLICATION_PTR_RVA).value
        if not app:
            self._invalidate_manual_action()
            self._load_summon_pending = False
            self._finish_exit_diagnostic("cancelled because application context is unavailable")
            self.policy.reset()
            self.app_identity = None
            self.pet_identity = None
            self.save_key = None
            self.saved_selection = None
            self.pending_notice = None
            return None
        if app != self.app_identity:
            self._finish_exit_diagnostic("cancelled because application context changed")
            if self.app_identity is not None:
                self._invalidate_manual_action()
                self._load_summon_pending = False
                # A replacement application without an observed successful load
                # must not inherit the last save's persisted selection.
                self.save_key = None
                self.saved_selection = None
                self.pending_notice = None
            self.policy.reset()
            self.pet_identity = None
            self.app_identity = app
        return app if player == app + LOCAL_PLAYER_OFFSET else None

    @staticmethod
    def _pet_seed(app, slot):
        # Persistent 128-bit identity: CreatureSeed uint64 + BirthTime uint64.
        # Both are copied to/from GcPetData by this build's pet load/save paths.
        # Exclude GcSeed padding and the lazily generated BoneScaleSeed at 0x2390.
        entry = app + PET_TABLE_OFFSET + slot * PET_ENTRY_SIZE
        return (C.string_at(entry + PET_SEED_OFFSET, 8)
                + C.string_at(entry + PET_BIRTH_TIME_OFFSET, 8))

    def _restore_selected(self, app):
        if self.policy.last_slot is not None:
            if self._pet_seed(app, self.policy.last_slot) == self.pet_identity:
                return
            self._finish_exit_diagnostic("cancelled because companion identity changed")
            self.policy.reset()
            self.pet_identity = None
        if self.save_key is None or self.saved_selection is None:
            return
        identity = bytes.fromhex(self.saved_selection["seed"])
        matches = []
        for slot in range(30):
            entry = app + PET_TABLE_OFFSET + slot * PET_ENTRY_SIZE
            if C.c_uint32.from_address(entry + PET_RESOURCE_OFFSET).value == 0:
                continue
            if self._pet_seed(app, slot) == identity:
                matches.append(slot)
        # Do not guess between duplicates or summon a replacement at an old slot.
        if len(matches) == 1:
            self.policy.remember(matches[0])
            self.pet_identity = identity
            LOGGER.info("Companion Auto Summon restored the remembered pet for this save (slot %d).", matches[0] + 1)

    def _persistence_failed(self):
        self.persistence_ok = False
        LOGGER.exception("Companion Auto Summon persistence unavailable; manual selection still works for this session. File preserved.")

    def _fail_closed(self):
        self.enabled = False
        self._invalidate_manual_action()
        self._load_summon_pending = False
        self._finish_exit_diagnostic("cancelled by runtime error")
        self.policy.reset()
        self.pending_notice = None
        LOGGER.exception("Companion Auto Summon disabled after a runtime error. Restart before trying again.")

    def _invalidate_manual_action(self):
        self._manual_epoch += 1
        self._manual_action = None

    def _stop_manual_attribution(self, reason):
        """Stop only learning favourites; native actions and automation continue."""
        was_available = self._manual_attribution_ok
        self._manual_attribution_ok = False
        self._invalidate_manual_action()
        if was_available:
            try:
                LOGGER.warning("Companion Auto Summon manual-choice attribution stopped: %s. Automatic summoning is unchanged.", reason)
            except Exception:
                pass

    def _enter_manual_attribution(self):
        if not self.enabled or not self._manual_attribution_ok:
            return False
        if not self._manual_lock.acquire(blocking=False):
            self._stop_manual_attribution("callback contention")
            return False
        if not self._manual_attribution_ok:
            self._manual_lock.release()
            return False
        return True

    @staticmethod
    def _manual_item_integer(action, offset):
        # This item is borrowed only during BEFORE, while the native caller
        # still owns it. Never reuse its storage after TriggerAction returns.
        if type(action) is not int or not 0x10000 <= action <= 0x7FFFFFFFFFFF - 0x88:
            raise ValueError("Invalid native menu item address")
        return C.c_int32.from_address(action + offset).value

    @cas_manual_trigger.before
    def before_manual_action(self, menu, action, called_as_menu):
        if not self._enter_manual_attribution():
            return None
        try:
            if self._manual_action is not None:
                raise RuntimeError("Nested native menu dispatch")
            if type(called_as_menu) is not bool:
                raise ValueError("Unexpected native menu flag")
            thread = get_native_id()
            record = {"call": (menu, action, called_as_menu, thread),
                      "epoch": self._manual_epoch, "candidate": None}
            # Track every dispatch, including non-pet actions, so a nested pet
            # action cannot inherit ambiguous authority from an outer call.
            action_id = self._manual_item_integer(action, QUICK_MENU_ACTION_OFFSET)
            if action_id == SUMMON_PET_ACTION:
                slot = self._manual_item_integer(action, QUICK_MENU_SLOT_OFFSET)
                if not 0 <= slot < 30:
                    raise ValueError("Unexpected native companion slot")
                app = C.c_void_p.from_address(_internal.BASE_ADDRESS + APPLICATION_PTR_RVA).value
                if app:
                    record["candidate"] = {
                        "app": app, "player": app + LOCAL_PLAYER_OFFSET, "slot": slot,
                        "identity": bytes(self._pet_seed(app, slot)), "save_key": self.save_key,
                        "accepted": False,
                    }
            if self._manual_attribution_ok and record["epoch"] == self._manual_epoch:
                self._manual_action = record
        except Exception:
            self._stop_manual_attribution("native action capture")
        finally:
            if not self._manual_attribution_ok:
                self._manual_action = None
            self._manual_lock.release()
        return None

    @cas_manual_trigger.after
    def after_manual_action(self, menu, action, called_as_menu, _result_):
        if not self._enter_manual_attribution():
            return None
        try:
            record = self._manual_action
            self._manual_action = None  # Consume before any persistence or logging.
            if record is None:
                return None
            if record["call"] != (menu, action, called_as_menu, get_native_id()):
                raise RuntimeError("Unmatched native action completion")
            if record["epoch"] != self._manual_epoch:
                return None
            candidate = record["candidate"]
            if candidate is None or not candidate["accepted"] or _result_ is not True:
                return None
            # Resolve current storage afresh. The old action address is only
            # compared above and is never dereferenced after the native call.
            app = C.c_void_p.from_address(_internal.BASE_ADDRESS + APPLICATION_PTR_RVA).value
            if (not app or app != candidate["app"] or app != self.app_identity
                    or self.save_key != candidate["save_key"]):
                return None
            player = app + LOCAL_PLAYER_OFFSET
            slot = candidate["slot"]
            if (player != candidate["player"]
                    or C.c_int32.from_address(player + PENDING_PET_OFFSET).value != slot
                    or self._pet_seed(app, slot) != candidate["identity"]
                    or record["epoch"] != self._manual_epoch
                    or not self._manual_attribution_ok or not self.enabled):
                return None
            self._remember_confirmed_companion(slot, candidate["identity"])
        except Exception:
            self._stop_manual_attribution("native action completion")
        finally:
            if not self._manual_attribution_ok:
                self._manual_action = None
            self._manual_lock.release()
        return None  # Preserve the original result, including native dismissal.

    def _remember_confirmed_companion(self, slot, identity):
        """Apply an accepted native UI choice; never infer intent from a queue."""
        if not self.enabled or not self._manual_attribution_ok:
            return
        previous_identity = self.saved_selection["seed"] if self.saved_selection else None
        self.policy.remember(slot)
        self.pet_identity = identity
        self.saved_selection = {"seed": identity.hex(), "slot": slot}
        persisted = False
        if self.save_key is not None and self.persistence_ok:
            try:
                self.store.remember(self.save_key, identity, slot)
                persisted = True
            except SelectionStoreError:
                self._persistence_failed()
        if identity.hex() != previous_identity:
            if persisted:
                prefix = "Companion saved."
            else:
                prefix = "Companion selected (session only)."
            if not self.auto_enabled:
                self.pending_notice = prefix + " Auto summoning OFF."
            elif self.selection_mode_value == "random":
                self.pending_notice = prefix + " Random stays ON."
            else:
                self.pending_notice = prefix
        LOGGER.info("Companion Auto Summon confirmed native UI companion choice: slot %d; persisted=%s.", slot + 1, persisted)

    @cas_queue_pet.after
    def remember_pet(self, player, slot):
        if not self.enabled or self.in_auto_call:
            return
        try:
            app = self._app_for_player(player)
            if app is None:
                return
            # The game sets pending=-1 if preparing the pet failed.
            if 0 <= slot < 30 and C.c_int32.from_address(player + PENDING_PET_OFFSET).value == slot:
                self._load_summon_pending = False
                self._finish_exit_diagnostic("cancelled by accepted native companion queue")
                self.policy.enter_ship()  # Preserve the existing manual favourite.
                if not self._enter_manual_attribution():
                    return
                try:
                    record = self._manual_action
                    candidate = record and record["candidate"]
                    if candidate is None:
                        return
                    if (record["epoch"] != self._manual_epoch
                            or record["call"][3] != get_native_id() or candidate["accepted"]
                            or candidate["app"] != app or candidate["player"] != player
                            or candidate["slot"] != slot or candidate["save_key"] != self.save_key
                            or candidate["identity"] != self._pet_seed(app, slot)):
                        raise RuntimeError("Native queue does not match the UI action")
                    if self._manual_attribution_ok:
                        candidate["accepted"] = True
                finally:
                    if not self._manual_attribution_ok:
                        self._manual_action = None
                    self._manual_lock.release()
        except Exception:
            self._stop_manual_attribution("native queue attribution")

    def _arm_automatic_request(self, app, source):
        """Share the existing timing/placement path across both trigger events."""
        self._restore_selected(app)
        self._finish_exit_diagnostic("replaced by " + source)
        now = time.monotonic()
        random_selection = self.selection_mode_value == "random"
        self.policy.eject(now, random_selection=random_selection)
        if self.policy.pending:
            self._pending_pet_identity = None if random_selection else self.pet_identity
            self._exit_diagnostic = {
                "source": source,
                "armed_at": now, "last_time": now, "last_state": None,
                "wait_logs": 0, "suppressed": False, "observed_waits": set(),
            }
            choice = ("one random eligible companion" if random_selection
                      else f"slot {self.policy.pending_slot + 1}")
            LOGGER.info("Companion Auto Summon %s armed for %s; stability delay=%.2fs; waiting until a suitable place.",
                        source, choice, self.policy._delay)
        elif self.policy.last_slot is None:
            LOGGER.info("Companion Auto Summon %s not armed: no selected owned companion.", source)
        else:
            LOGGER.info("Companion Auto Summon %s not armed: policy rejected the timestamp.", source)

    @cas_eject.after
    def after_exit_request(self, ship, player, animate, force_during_communicator):
        if not self.enabled or not self.auto_enabled:
            return
        try:
            app = self._app_for_player(player)
            if app is not None:
                self._invalidate_manual_action()
                self._load_summon_pending = False
                self._arm_automatic_request(app, "ship exit")
        except Exception:
            self._fail_closed()

    @cas_enter_cockpit.before
    def before_enter_ship(self, player):
        if not self.enabled:
            return
        try:
            if self._app_for_player(player) is not None:
                self._invalidate_manual_action()
                self._load_summon_pending = False
                self._finish_exit_diagnostic("cancelled by entering the ship")
                self.policy.enter_ship()
        except Exception:
            self._fail_closed()

    @cas_load_save.before
    def before_load(self, player_state, common_data, state_data, network_client, resetting, arg6):
        # Network-client deserialization must not erase the local user's selection.
        if not network_client:
            self._invalidate_manual_action()
            self._load_summon_pending = False
            self._finish_exit_diagnostic("cancelled by main save load")
            self.policy.reset()
            self.app_identity = None
            self.pet_identity = None
            self.save_key = None
            self.saved_selection = None
            self.pending_notice = None

    @cas_load_save.after
    def after_load(self, player_state, common_data, state_data, network_client, resetting, arg6, _result_):
        if not self.enabled or network_client or not _result_:
            return
        try:
            # This is GcPlayerCommonStateData, not GcPlayerStateData. The ID is
            # copied from +0x8980 in this exact executable's LoadFromData body.
            if not common_data:
                return
            save_id = C.c_uint64.from_address(common_data + SAVE_UNIVERSAL_ID_OFFSET).value
            # This records one opportunity, not game/pet/physics readiness.
            # Only a later local ownership update may arm the normal policy.
            self._load_summon_pending = self.auto_enabled
            if save_id == 0:
                LOGGER.warning("Companion Auto Summon: save has no persistent ID; selection lasts for this session only.")
                return
            self.save_key = f"nms:{save_id:016x}"
            if self.persistence_ok:
                try:
                    self.saved_selection = self.store.load(self.save_key)
                except SelectionStoreError:
                    self._persistence_failed()
            # Ownership may still be loading. No native summon or placement
            # operation is permitted during this deserialization callback.
        except Exception:
            self._fail_closed()

    @cas_player_update.after
    def after_player_update(self, player, dt):
        if not self.enabled:
            return
        if not self._controls_pending() and self.pending_notice is None:
            return
        try:
            app = self._app_for_player(player)
            if app is None:
                return
            self._apply_control()
            if math.isfinite(dt) and dt > 0:
                self._show_pending_notice(app)
        except Exception:
            self._fail_closed()

    def _prepare_loaded_summon(self, app, owner, player, dt):
        """Consume one load opportunity after observing a usable local context."""
        if not self._load_summon_pending:
            return
        preview = C.c_int32.from_address(owner + PET_PREVIEW_OFFSET).value
        emote = C.c_ubyte.from_address(owner + PET_EMOTE_OFFSET).value
        active = C.c_int32.from_address(app + ACTIVE_PET_OFFSET).value
        queued = C.c_int32.from_address(player + PENDING_PET_OFFSET).value
        # Observe overrides even while paused, outside an allowed location,
        # or before the saved companion has reappeared in the ownership table.
        if (preview != -1 or emote != 0 or active != -1 or queued != -1
                or self.policy.pending):
            self._load_summon_pending = False
            self._reset_probe()
            return
        location = C.c_int32.from_address(app + LOCATION_OFFSET).value
        if location in SUPPORTED_SUMMON_LOCATIONS and location not in self.allowed_locations:
            self._load_summon_pending = False
            self._reset_probe()
            return
        if not math.isfinite(dt) or dt <= 0 or location not in SUPPORTED_SUMMON_LOCATIONS:
            self._reset_probe()
            return
        if self.selection_mode_value == "last_manual":
            if self.saved_selection is None and self.policy.last_slot is None:
                self._load_summon_pending = False
                self._reset_probe()
                return
            now = time.monotonic()
            if not math.isfinite(now):
                raise RuntimeError("Invalid startup restoration clock")
            if now < self._next_probe_at:
                return
            self._next_probe_at = now + PLACEMENT_PROBE_INTERVAL
            self._restore_selected(app)
            if self.policy.last_slot is None:
                # Absence is not proof of removal while ownership is loading.
                # Keep the saved identity, never guess its previous slot.
                return
        # Consume BEFORE arming. Neither rejection nor later manual dismissal
        # creates another startup request; normal policy owns any paced retry.
        self._load_summon_pending = False
        self._arm_automatic_request(app, "save load")

    @cas_pet_owner_update.after
    def after_pet_owner_update(self, owner, dt):
        # Ownership.Update normally resets placement after closing the pet menu.
        # Refresh only after that reset, and check/queue within this same callback.
        self._observe_queued_summon(owner, dt)
        if not self.enabled or not self.auto_enabled:
            self._load_summon_pending = False
            return
        if not self.policy.pending and not self._load_summon_pending:
            return
        # Player.Update applies UI controls. If ownership runs first, an OFF
        # request must prevent automation immediately without doing GUI-thread I/O.
        if self._controls_pending():
            self._reset_probe()
            return
        try:
            player = owner - PET_TABLE_OFFSET + LOCAL_PLAYER_OFFSET
            app = self._app_for_player(player)
            if app is None:
                return
            self._prepare_loaded_summon(app, owner, player, dt)
            if not self.policy.pending:
                return
            selected = self.policy.pending_slot
            if selected is not None and self._pending_pet_identity != self._pet_seed(app, selected):
                self._finish_exit_diagnostic("cancelled because companion identity changed")
                if self.selection_mode_value == "last_manual":
                    self.policy.reset()
                    self.pet_identity = None
                    LOGGER.info("Companion Auto Summon forgot a companion slot whose identity changed.")
                else:
                    self.policy.enter_ship()
                return
            preview_slot = C.c_int32.from_address(owner + PET_PREVIEW_OFFSET).value
            emote_active = C.c_ubyte.from_address(owner + PET_EMOTE_OFFSET).value
            if preview_slot != -1 or emote_active != 0:
                self._finish_exit_diagnostic("cancelled because the native pet preview or emote is active")
                self.policy.enter_ship()
                return
            location = C.c_int32.from_address(app + LOCATION_OFFSET).value
            if location in SUPPORTED_SUMMON_LOCATIONS and location not in self.allowed_locations:
                self._finish_exit_diagnostic("cancelled because this location is disabled in settings")
                self.policy.enter_ship()
                return
            active_pet = C.c_int32.from_address(app + ACTIVE_PET_OFFSET).value
            native_pending = C.c_int32.from_address(player + PENDING_PET_OFFSET).value
            advancing = math.isfinite(dt) and dt > 0
            on_foot = (location in SUPPORTED_SUMMON_LOCATIONS
                       and location in self.allowed_locations and advancing)
            # Reject unexpected index values instead of treating corrupt state as "no pet".
            if not (-1 <= active_pet < 30 and -1 <= native_pending < 30):
                self._finish_exit_diagnostic(
                    f"cancelled by invalid companion indices (active={active_pet}, pending={native_pending})")
                self.policy.enter_ship()
                return
            now = time.monotonic()
            within_window = (now >= self.policy._last_time
                             and (self.policy._expiry is None
                                  or now - self.policy._ejected_at < self.policy._expiry))
            can_try = on_foot and active_pet == -1 and native_pending == -1 and within_window
            eligible = False
            wait_reason = None
            if can_try:
                eligible, wait_reason = self._probe_placement(app, owner, player, location, now)
            else:
                self._reset_probe()
                if not within_window:
                    # No new native check at/after expiry. Report the last
                    # observed wait, rather than inventing a fresh false result.
                    previous = self._exit_diagnostic and self._exit_diagnostic["last_state"]
                    wait_reason = previous[0] if previous else "deadline_before_placement_check"
            chosen_identity = self._pending_pet_identity
            source = self._exit_diagnostic.get("source", "unknown") if self._exit_diagnostic else "unknown"
            slot = self.policy.tick(now, on_foot_in_summon_location=on_foot,
                                    active_pet=active_pet, native_pending_pet=native_pending,
                                    eligible=eligible)
            self._trace_policy_tick(now, location=location, advancing=advancing,
                                    active_pet=active_pet, native_pending=native_pending,
                                    eligible=eligible, slot=slot, wait_reason=wait_reason)
            if not self.policy.pending:
                self._pending_pet_identity = None
                self._reset_probe()
            if slot is None:
                return
            if self.selection_mode_value == "random":
                # Pool scans may inspect other slots after the eventual choice.
                # Revalidate the frozen choice immediately before each paced
                # queue attempt. A temporary failure retains it, never rerolls.
                if (self._pet_seed(app, slot) != chosen_identity
                        or not self._slot_occupied(app, slot)
                        or not self._native_owned(owner, slot)
                        or not self._native_can_summon(player, slot)):
                    self.policy.resolve(False)
                    self._reset_probe(next_at=now + PLACEMENT_PROBE_INTERVAL)
                    return
            # Only an accepted native queue consumes the intent. Rejection waits
            # for a fresh throttled placement pair before retrying the same pet.
            self.in_auto_call = True
            try:
                cas_queue_pet(player, slot)
            finally:
                self.in_auto_call = False
            queued_slot = C.c_int32.from_address(player + PENDING_PET_OFFSET).value
            if queued_slot == -1:
                self.policy.resolve(False)
                self._reset_probe(next_at=now + PLACEMENT_PROBE_INTERVAL)
                if not self._queue_rejection_logged:
                    LOGGER.info("Companion Auto Summon queue was not accepted; waiting for a suitable place with the same companion.")
                    self._queue_rejection_logged = True
                return
            if queued_slot != slot:
                self.enabled = False
                self.policy.reset()
                LOGGER.error("Companion Auto Summon disabled: unexpected queued companion after summon request.")
                return
            self.policy.resolve(True)
            self._finish_exit_diagnostic("summon request accepted")
            self._arm_summon_observation(app, slot, chosen_identity, source, location, now)
            LOGGER.info("Companion Auto Summon queued slot %d through the game's normal summon path.", slot + 1)
        except Exception:
            self._fail_closed()

    @staticmethod
    def _slot_occupied(app, slot):
        return C.c_uint32.from_address(app + PET_TABLE_OFFSET + slot * PET_ENTRY_SIZE
                                       + PET_RESOURCE_OFFSET).value != 0

    @staticmethod
    def _native_owned(owner, slot):
        result = cas_owned_pet_eligible(owner, slot)
        if result is None:
            raise RuntimeError("Native companion ownership eligibility call failed.")
        return bool(result)

    @staticmethod
    def _native_can_summon(player, slot):
        result = cas_can_summon(player, slot)
        if result is None:
            raise RuntimeError("Native summon eligibility call failed.")
        return bool(result)

    @staticmethod
    def _pet_biome(app, slot):
        # GcPetData.Biome is copied unchanged into each runtime pet entry.
        biome = C.c_uint32.from_address(app + PET_TABLE_OFFSET + slot * PET_ENTRY_SIZE
                                        + PET_BIOME_OFFSET).value
        return biome if biome in CONCRETE_BIOMES else None

    @staticmethod
    def _current_planet_biome(app):
        """Read and normalize the current planet as native pet adoption does."""
        if not app:
            return None
        solar = C.c_void_p.from_address(app + SOLAR_SYSTEM_PTR_OFFSET).value
        if not solar:
            return None
        count = C.c_int32.from_address(solar + PLANET_COUNT_OFFSET).value
        if not 1 <= count <= 6:
            return None
        index = C.c_int32.from_address(solar + CURRENT_PLANET_INDEX_OFFSET).value
        if not 0 <= index < count:
            return None
        planet = solar + index * PLANET_ENTRY_SIZE
        biome = C.c_uint32.from_address(planet + PLANET_BIOME_OFFSET).value
        subtype = C.c_uint32.from_address(planet + PLANET_BIOME_SUBTYPE_OFFSET).value
        if biome not in CONCRETE_BIOMES or not 0 <= subtype <= 31:
            return None
        # Adoption maps these subtypes before its special-biome normalization.
        if subtype == 25:
            return 12  # Swamp
        if subtype == 26:
            return 13  # Lava
        return 7 if biome in {8, 9, 10} else biome  # Weird variants

    def _random_biome_pool(self, app, location, candidates):
        """Prefer matching habitat only within the already eligible random pool.

        Unknown planet data or no known match leaves every eligible candidate
        available. The readers can be replaced by owned-memory adapters in tests.
        """
        if (not self.prefer_same_biome_value or self.selection_mode_value != "random"
                or location != 3):
            return candidates
        try:
            biome = self._current_planet_biome(app)
            if biome is None:
                return candidates
            matching = [slot for slot in candidates if self._pet_biome(app, slot) == biome]
        except (OSError, ValueError):
            # Habitat is optional. A recoverable read failure must not replace
            # the native ownership/placement decision or stop ordinary random.
            return candidates
        return matching or candidates

    def _refresh_placement(self, app, owner):
        arc_range = C.c_float.from_address(_internal.BASE_ADDRESS + SUMMON_ARC_RANGE_RVA).value
        if not math.isfinite(arc_range) or arc_range <= 0:
            raise RuntimeError("Native summon placement range is invalid.")
        use_hand = cas_use_summon_hand()
        if use_hand is None:
            raise RuntimeError("Native summon hand selection call failed.")
        hand = C.c_uint32.from_address(app + SUMMON_HAND_OFFSET).value if use_hand else 0
        warmed = self._placement_warmed
        cas_refresh_pet_placement(owner + PET_ARC_OFFSET, arc_range, arc_range, hand)
        self._placement_warmed = True
        return warmed

    def _reset_probe(self, *, next_at=0.0):
        self._placement_warmed = False
        self._probe_primed_at = None
        self._probe_location = None
        self._probe_physics_context = None
        self._next_probe_at = next_at

    def _probe_placement(self, app, owner, player, location, now):
        physics_context = C.c_uint64.from_address(player + PHYSICS_CONTEXT_OFFSET).value
        if not physics_context:
            self._reset_probe(next_at=now + PLACEMENT_PROBE_INTERVAL)
            return False, "physics_context_unavailable"
        primed = (self._probe_primed_at is not None and self._probe_location == location
                  and self._probe_physics_context == physics_context
                  and 0 < now - self._probe_primed_at <= PLACEMENT_MAX_FRAME_GAP)
        if self._probe_primed_at is not None and not primed:
            self._reset_probe()
        if not primed and now < self._next_probe_at:
            return False, "probe_wait"
        selected = self.policy.pending_slot
        if selected is None:
            candidates = [slot for slot in range(30)
                          if self._slot_occupied(app, slot) and self._native_owned(owner, slot)]
        else:
            candidates = [selected] if self._native_owned(owner, selected) else []
        if not candidates:
            self._reset_probe(next_at=now + PLACEMENT_PROBE_INTERVAL)
            return False, "ownership_eligibility_false"
        self._refresh_placement(app, owner)
        if not primed:
            self._probe_primed_at = now
            self._probe_location = location
            self._probe_physics_context = physics_context
            return False, "placement_warmup"
        # The immediately following usable owner callback consumes newly primed
        # ray results. Never use a pair separated by a pause or a large frame gap.
        self._reset_probe(next_at=now + PLACEMENT_PROBE_INTERVAL)
        candidates = [slot for slot in candidates if self._native_can_summon(player, slot)]
        if not candidates:
            return False, "eligibility_false"
        if selected is None:
            candidates = self._random_biome_pool(app, location, candidates)
            slot = random.choice(candidates)
            self.policy.select_for_exit(slot)
            self._pending_pet_identity = self._pet_seed(app, slot)
            LOGGER.info("Companion Auto Summon chose random companion slot %d from %d eligible owned companions for this exit.",
                        slot + 1, len(candidates))
        return True, None


if CompanionAutoSummon._disabled:
    LOGGER.error("Companion Auto Summon is disabled: requires pyMHF 0.2.4 and the exact supported NMS.exe SHA256.")
