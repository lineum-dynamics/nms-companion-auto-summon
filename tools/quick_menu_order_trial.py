# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["pymhf[gui]==0.2.4"]
# [tool.pymhf]
# exe = "NMS.exe"
# steam_gameid = 275850
# start_paused = false
# interactive_console = false
# [tool.pymhf.logging]
# shown = false
# log_dir = "{CURR_DIR}"
# log_level = "info"
# [tool.pymhf.gui]
# shown = false
# always_on_top = false
# ///
"""Disabled developer trial: ordered submenu with an opt-in automation toggle.

This is NOT an observation-only probe. An explicitly built future trial installs
a process-lifetime native binding filter before allowing native item insertion.
The exact-build and current-process guards must pass. The separately enabled
toggle uses the native confirmation predicate and the existing production
preference queue. This adapter makes no summon calls or save-file accesses.
"""

import ctypes as C
import hashlib
from importlib.metadata import PackageNotFoundError, version
import logging
from pathlib import Path
import sys
from threading import Lock, get_native_id
from time import monotonic
from types import ModuleType

# The isolated build copies these reviewed helper sources beside this script.
# Keep the loader independent of the user's current directory.
_helper_directory = str(Path(__file__).resolve().parent)
if _helper_directory not in sys.path:
    sys.path.insert(0, _helper_directory)
import quick_menu_item as item
import quick_menu_submenu as submenu
import quick_menu_order as order
from quick_menu_guard_runtime import GuardError, ensure_guard

from pymhf import Mod
from pymhf.core import _internal
from pymhf.core.hooking import hook_manager, static_function_hook


TRIAL_ENABLED = False
SETTINGS_TOGGLE_ENABLED = False
EXTENDED_SETTINGS_ENABLED = False
CUSTOM_ICON_ENABLED = False
LANGUAGE_OBSERVATION_ENABLED = False
EXPECTED_EXE_SHA256 = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"
BUILD_ACTIONS_RVA = 0x151ED00
BUILD_LABEL_RVA = 0x1523220
ITEM_CONSTRUCTOR_RVA = 0x1432FC0
ITEM_APPEND_RVA = 0x1533980
TRIGGER_ACTION_RVA = 0x1526940
SELECT_ITEM_RVA = 0x150FAC0
CONFIRM_PREDICATE_RVA = 0x15311C0
LOAD_RESOURCES_RVA = 0x151AD80
PENDING_SELECTION_OFFSET = 0xA16C
LOGGER = logging.getLogger("CompanionMenuOrderTrial")
ICON_REGISTRY_NAME = "_companion_auto_summon_icon_owner_v1"

if SETTINGS_TOGGLE_ENABLED:
    import quick_menu_toggle as toggle
    from quick_menu_preferences import PreferenceBridge
    from pymhf.core.mod_loader import mod_manager

if CUSTOM_ICON_ENABLED:
    import quick_menu_icon as icons

if LANGUAGE_OBSERVATION_ENABLED:
    from game_language import LanguageObserver


def supported_runtime():
    try:
        if not TRIAL_ENABLED or not _internal.IS_INJECTED or _internal.BASE_ADDRESS <= 0:
            return False
        if C.sizeof(C.c_void_p) != 8 or version("pymhf") != "0.2.4":
            return False
        with Path(_internal.BINARY_PATH).open("rb") as binary:
            return hashlib.file_digest(binary, "sha256").hexdigest() == EXPECTED_EXE_SHA256
    except (OSError, ValueError, TypeError, AttributeError, PackageNotFoundError):
        return False


def current_process_io():
    """Copy bounded data through Windows APIs; no external process is opened."""
    kernel = C.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.argtypes = []
    kernel.GetCurrentProcess.restype = C.c_void_p
    handle = kernel.GetCurrentProcess()
    arguments = [C.c_void_p, C.c_void_p, C.c_void_p, C.c_size_t, C.POINTER(C.c_size_t)]
    kernel.ReadProcessMemory.argtypes = arguments
    kernel.ReadProcessMemory.restype = C.c_int
    kernel.WriteProcessMemory.argtypes = arguments
    kernel.WriteProcessMemory.restype = C.c_int

    def read(address, size):
        if size not in (1, 4, 8, 16):
            raise ValueError("Unexpected item-trial read size")
        item._address(address, 0, size)
        buffer = C.create_string_buffer(size)
        transferred = C.c_size_t()
        if not kernel.ReadProcessMemory(handle, address, buffer, size, C.byref(transferred)):
            raise OSError("Item-trial copy failed")
        if transferred.value != size:
            raise OSError("Item-trial copy was incomplete")
        return buffer.raw

    def write_label(output, label):
        if type(label) is not bytes or not 0 < len(label) < 128 or b"\0" in label:
            raise ValueError("Invalid bounded label")
        item._address(output, 0, 128)
        buffer = C.create_string_buffer(label + bytes(128 - len(label)), 128)
        transferred = C.c_size_t()
        if not kernel.WriteProcessMemory(handle, output, buffer, 128, C.byref(transferred)):
            raise OSError("Item-trial label write failed")
        if transferred.value != 128:
            raise OSError("Item-trial label write was incomplete")

    def write_field(menu, offset, value):
        # Only the audited depth transition may be written. The child is
        # prebuilt and selected synchronously; the native deferred-selection
        # flag, vector headers and item storage are never replaced.
        if offset == item.DEPTH_OFFSET and type(value) is int and value == 2:
            data = value.to_bytes(4, "little", signed=True)
        else:
            raise ValueError("Unsupported submenu field write")
        address = item._address(menu, offset, len(data))
        buffer = C.create_string_buffer(data, len(data))
        transferred = C.c_size_t()
        if not kernel.WriteProcessMemory(handle, address, buffer, len(data), C.byref(transferred)):
            raise OSError("Submenu field write failed")
        if transferred.value != len(data):
            raise OSError("Submenu field write was incomplete")

    return read, write_label, write_field


def native_adapters(base, resolve_append_original):
    """Bind statically audited ABIs; adapters hold only temporary owned buffers."""
    constructor = C.WINFUNCTYPE(C.c_void_p, C.c_void_p, C.c_uint32, C.c_int32,
                               C.c_bool, C.c_bool)(base + ITEM_CONSTRUCTOR_RVA)
    select = C.WINFUNCTYPE(None, C.c_void_p, C.c_int32, C.c_int32)(base + SELECT_ITEM_RVA)

    def aligned_buffer(data):
        if len(data) != item.ITEM_SIZE:
            raise ValueError("Invalid native item size")
        owner = C.create_string_buffer(item.ITEM_SIZE + 15)
        address = (C.addressof(owner) + 15) & ~15
        C.memmove(address, bytes(data), item.ITEM_SIZE)
        return owner, address

    def construct(owned, icon, action, disabled, background):
        owner, address = aligned_buffer(owned)
        if constructor(address, icon, action, disabled, background) != address:
            raise RuntimeError("Native item constructor returned another object")
        owned[:] = C.string_at(address, item.ITEM_SIZE)  # Our aligned owned buffer only.

    def append_item(header, data):
        owner, address = aligned_buffer(data)
        original = resolve_append_original()
        if not original(header, address):
            raise RuntimeError("Native item append returned no item")
        # No item pointer is retained or read; native growth may move storage.

    def select_first(menu):
        select(menu + item.DEPTH_OFFSET, 2, 0)

    return construct, append_item, select_first


def icon_adapters(base):
    """Bind only the two audited pointer-only resource operations."""
    load = C.WINFUNCTYPE(None, C.c_void_p)(base + icons.TEXTURE_LOAD_RVA)
    retain = C.WINFUNCTYPE(None, C.c_void_p)(base + icons.HANDLE_RETAIN_RVA)
    return load, retain


def pin_icon_owner(owner):
    """Retain acquired references through process shutdown, including reloads."""
    proposed = ModuleType(ICON_REGISTRY_NAME)
    proposed.schema = "cas-icon-owner-1"
    proposed.owner = owner
    registry = sys.modules.setdefault(ICON_REGISTRY_NAME, proposed)
    return (type(registry) is ModuleType and getattr(registry, "schema", None) == proposed.schema
            and getattr(registry, "owner", None) is owner)


@static_function_hook(offset=BUILD_ACTIONS_RVA)
def cas_item_builder(menu: C.c_void_p, render: C.c_void_p) -> None:
    pass


@static_function_hook(offset=BUILD_LABEL_RVA)
def cas_item_label(menu: C.c_void_p, output: C.c_void_p) -> None:
    pass


@static_function_hook(offset=TRIGGER_ACTION_RVA)
def cas_submenu_trigger(menu: C.c_void_p, action: C.c_void_p, called_as_menu: C.c_bool) -> C.c_bool:
    pass


@static_function_hook(offset=ITEM_APPEND_RVA)
def cas_order_append(header: C.c_void_p, incoming: C.c_void_p) -> C.c_void_p:
    pass


if SETTINGS_TOGGLE_ENABLED:
    @static_function_hook(offset=CONFIRM_PREDICATE_RVA)
    def cas_toggle_confirm(menu: C.c_void_p) -> C.c_bool:
        pass
else:
    cas_toggle_confirm = None

if CUSTOM_ICON_ENABLED:
    @static_function_hook(offset=LOAD_RESOURCES_RVA)
    def cas_icon_resources(menu: C.c_void_p) -> None:
        pass
else:
    cas_icon_resources = None


class CompanionMenuOrderTrial(Mod):
    _version = ("0.8.5-branding" if LANGUAGE_OBSERVATION_ENABLED
                else "0.8.3-settings-trial" if EXTENDED_SETTINGS_ENABLED or CUSTOM_ICON_ENABLED
                else "0.7.0-toggle-trial" if SETTINGS_TOGGLE_ENABLED else "0.6.0-order-trial")
    _author = "Lineum Dynamics"
    _description = ("Native automation toggle before individual companions" if SETTINGS_TOGGLE_ENABLED
                    else "One inert native settings subpage before individual companions")
    _disabled = not supported_runtime()

    def __init__(self):
        super().__init__()
        self._lock = Lock()
        self._thread = None
        self._stopped = True
        self._notice_sent = False
        self._appended = False
        self._label_seen = False
        self._guard = None
        self._pending = None
        self._opened = False
        self._building = None
        self._append_hook = None
        self._append_original = None
        self._append_original_address = None
        self._ordered = False
        self._confirmation_call = None
        self._confirmation_ready = False  # Observe release before accepting a press.
        self._confirmation_menu = None
        self._confirmation_intent = None
        self._preferences = None
        self._icons = None
        self._icon_provider = self._notification_icon
        self._icon_phase_lock = Lock()
        self._icon_phase_seen = False
        self._known_icon_handles = set()
        self._icon_status_seen = set()
        self._language = None
        if self._disabled:
            return
        try:
            self._reader, self._writer, self._write_field = current_process_io()
            self._constructor, self._append, self._select_first = native_adapters(
                _internal.BASE_ADDRESS, self._resolve_append_original)
            # This must complete before pyMHF can enable the builder callback.
            # The separately pinned filter outlives callback failure/reload.
            self._guard = ensure_guard(_internal.BASE_ADDRESS, _internal.BINARY_PATH)
            if LANGUAGE_OBSERVATION_ENABLED:
                try:
                    self._language = LanguageObserver(self._reader, _internal.BASE_ADDRESS, self._report_language)
                except Exception:
                    self._language = None
            if SETTINGS_TOGGLE_ENABLED:
                self._preferences = PreferenceBridge(
                    str(Path(__file__).absolute().with_name("CompanionAutoSummon.py")),
                    get_registered=lambda: mod_manager.mods.get("CompanionAutoSummon"),
                    get_module=lambda: sys.modules.get("CompanionAutoSummon"),
                )
            if CUSTOM_ICON_ENABLED:
                try:
                    self._icons = icons.IconOwner()
                    self._load_texture, self._retain_icon = icon_adapters(_internal.BASE_ADDRESS)
                except Exception:
                    self._icons = None
                    try:
                        LOGGER.warning("Optional companion icon bindings unavailable; native menu remains active.")
                    except Exception:
                        pass
            self._stopped = False
            LOGGER.info("Ordering trial initialized; native binding filter installed. Managed append validation remains pending.")
        except GuardError as error:
            self._stop("initialization: " + str(error))
        except Exception:
            self._stop("initialization")

    def _stop(self, reason):
        self._stopped = True
        self._pending = None
        self._building = None
        self._confirmation_call = None
        self._confirmation_intent = None
        self._confirmation_ready = False
        self._confirmation_menu = None
        if not self._notice_sent:
            self._notice_sent = True
            try:
                LOGGER.warning("Inert menu ordering stopped (%s); native binding filter is retained.", reason)
            except Exception:
                pass

    def _enter(self, phase="ordinary"):
        if self._stopped:
            return False
        if not self._lock.acquire(blocking=False):
            self._stop("overlapping_callback")
            return False
        try:
            native_thread = get_native_id()
            if self._stopped or (self._thread is not None and native_thread != self._thread):
                self._stop("unexpected_thread")
                self._lock.release()
                return False
            self._thread = native_thread
            if self._confirmation_call is not None and phase != "confirmation_after":
                self._stop("nested_confirmation_callback")
                self._lock.release()
                return False
            if phase != "trigger_before":
                self._confirmation_intent = None
            if self._building is not None and phase not in ("append", "builder_after"):
                self._stop("nested_build_callback")
                self._lock.release()
                return False
            if self._pending is not None and (phase == "trigger_before" or (
                    phase != "trigger_after" and self._pending[4] is not None)):
                self._stop("nested_callback")
                self._lock.release()
                return False
        except Exception:
            self._stop("thread_lookup")
            self._lock.release()
            return False
        return True

    def _resolve_append_original(self):
        """Resolve only the managed trampoline; never call the patched entry."""
        if self._stopped:
            raise RuntimeError("Ordering is no longer active")
        function_hook = hook_manager._get_funchook(self.before_append)
        if self._stopped or function_hook is None:
            raise RuntimeError("Managed append hook is unavailable")
        definition = getattr(function_hook, "_func_def", None)
        if (getattr(function_hook, "target", None) != _internal.BASE_ADDRESS + ITEM_APPEND_RVA
                or getattr(function_hook, "state", None) != "enabled"
                or getattr(function_hook, "_has_noop", True)
                or getattr(function_hook, "_before_detours", None) != [self.before_append]
                or getattr(function_hook, "_after_detours", None) != []
                or getattr(function_hook, "_after_detours_with_results", None) != []
                or definition is None or definition.restype is not C.c_void_p
                or definition.argtypes != [C.c_void_p, C.c_void_p]):
            raise RuntimeError("Managed append hook contract differs")
        original = getattr(function_hook, "original", None)
        if (not callable(original) or getattr(original, "restype", None) is not C.c_void_p
                or tuple(getattr(original, "argtypes", ())) != (C.c_void_p, C.c_void_p)):
            raise RuntimeError("Managed append trampoline ABI differs")
        address = C.cast(original, C.c_void_p).value
        item._address(address, 0, 1)
        if address == function_hook.target:
            raise RuntimeError("Managed append trampoline points to the patched entry")
        if self._append_hook is not None and (
                function_hook is not self._append_hook or original is not self._append_original
                or address != self._append_original_address):
            raise RuntimeError("Managed append trampoline identity changed")
        if self._stopped or hook_manager._get_funchook(self.before_append) is not function_hook:
            raise RuntimeError("Managed append hook ownership changed")
        self._append_hook = function_hook
        self._append_original = original
        self._append_original_address = address
        return original

    def authorize_append(self, menu):
        # Helper checks this twice; a contending callback can stop insertion
        # while a native constructor has released the GIL.
        return (not self._stopped and self._thread == get_native_id()
                and self._guard is not None and self._guard.authorize_append(menu) is True
                and not self._stopped)

    def _notification_icon(self):
        return self._icon_for_role(-1)

    def _icon_for_role(self, role=-1):
        if self._icons is None:
            return 0
        try:
            handle = self._icons.icon_handle(self._reader, _internal.BASE_ADDRESS + icons.MANAGER_PTR_RVA, role)
            status = self._icons.status
            if type(status) is str and status not in self._icon_status_seen and len(self._icon_status_seen) < 6:
                self._icon_status_seen.add(status)
                try:
                    LOGGER.info("Companion icon state: %s; visual confirmation remains a player check.", status)
                except Exception:
                    pass
            return handle if type(handle) is int and 0 < handle <= 0x7FFFFFFF else 0
        except Exception:
            return 0

    @(cas_icon_resources.after if CUSTOM_ICON_ENABLED else lambda callback: callback)
    def after_resources(self, menu):
        # Initialization can use a different native thread than menu updates.
        # It must not establish or alter the ordinary callback thread baseline.
        if self._icons is None or self._icon_phase_seen:
            return None
        if not self._icon_phase_lock.acquire(blocking=False):
            return None
        try:
            if self._icon_phase_seen:
                return None
            self._icon_phase_seen = True
            self._icons.register_once(
                self._reader, menu, _internal.BASE_ADDRESS + icons.MANAGER_PTR_RVA,
                load_texture=self._load_texture, retain_handle=self._retain_icon,
                pin_owner=pin_icon_owner,
            )
            if self._preferences is not None:
                self._preferences.bind_notice_icon(self._icon_provider)
            LOGGER.info("Companion icon resource phase reached: %s; visible rendering remains unverified.",
                        self._icons.status)
        except Exception:
            try:
                LOGGER.warning("Companion icon preparation unavailable; ordinary menu and automation continue.")
            except Exception:
                pass
        finally:
            self._icon_phase_lock.release()
        return None

    def _menu_options(self, *, construction=False):
        options = {"child_roles": toggle.CHILD_ROLES} if EXTENDED_SETTINGS_ENABLED else {}
        fresh = {}
        roles = (-1, *toggle.CHILD_ROLES) if EXTENDED_SETTINGS_ENABLED else (-1,)
        for role in roles:
            handle = self._icon_for_role(role)
            if handle and handle not in self._known_icon_handles:
                if len(self._known_icon_handles) < 8:
                    self._known_icon_handles.add(handle)
                else:
                    handle = 0
            if handle:
                fresh[role] = handle
        # Recognition of already copied items survives a temporarily pending
        # provider. Only a freshly vetted handle may be used for new items.
        if self._known_icon_handles:
            options["permitted_icons"] = tuple(sorted(self._known_icon_handles))
        if fresh and construction:
            options["role_icons"] = fresh
        if self._preferences is not None and self._icons is not None:
            self._preferences.bind_notice_icon(self._icon_provider)
        return options

    def _write_checked(self, menu, offset, value):
        if not self.authorize_append(menu):
            raise RuntimeError("Submenu field write no longer authorized")
        self._write_field(menu, offset, value)
        size = 4 if offset == item.DEPTH_OFFSET else 1
        expected = value.to_bytes(size, "little")
        if self._reader(menu + offset, size) != expected:
            raise RuntimeError("Submenu field write could not be read back")

    def _select_checked(self, menu):
        if not self.authorize_append(menu):
            raise RuntimeError("Submenu selection no longer authorized")
        self._select_first(menu)
        if self._reader(menu + item.SELECTIONS_OFFSET + 8, 4) != bytes(4):
            raise RuntimeError("Submenu selection could not be read back")

    @cas_item_builder.before
    def before_builder(self, menu, render):
        if not self._enter("builder_before"):
            return None
        try:
            item._address(menu, 0, PENDING_SELECTION_OFFSET + 1)
            item._address(render, 0, 1)
            self._resolve_append_original()
            if not self._stopped:
                self._building = (menu, render, self._thread)
        except Exception:
            self._stop("builder_before")
        finally:
            if self._stopped:
                self._building = None
            self._lock.release()
        return None

    @cas_order_append.before
    def before_append(self, header, incoming):
        # This target is shared by other menu paths. Reject unrelated calls
        # without reading their native item or initiating an original call.
        building = self._building
        if self._stopped or building is None or header != building[0] + item.VECTORS_OFFSET + item.VECTOR_SIZE:
            return None
        try:
            if get_native_id() != building[2]:
                self._stop("append_unexpected_thread")
                return None
        except Exception:
            self._stop("append_thread_lookup")
            return None
        if not self._enter("append"):
            return None
        try:
            if self._building != building:
                raise RuntimeError("Native build identity changed")
            menu = building[0]

            def guarded_append(destination, payload):
                if (self._building != building or destination != header
                        or not self.authorize_append(menu)):
                    raise RuntimeError("Ordered append no longer authorized")
                self._append(destination, payload)

            added = order.append_before_pet(
                self._reader, menu, incoming, constructor=self._constructor,
                append=guarded_append, guard_capability=self,
                **self._menu_options(construction=True),
            )
            if added and not self._stopped:
                self._appended = True
                if not self._ordered:
                    self._ordered = True
                    LOGGER.info("Companion Auto Summon inserted before the first companion; visual order remains a player check.")
        except Exception:
            self._stop("ordered_append")
        finally:
            if self._stopped:
                self._building = None
            self._lock.release()
        # The framework now appends the untouched incoming native item once
        # and returns its original result. No NOOP or result replacement.
        return None

    @cas_item_builder.after
    def after_builder(self, menu, render):
        if not self._enter("builder_after"):
            return None
        try:
            if self._building != (menu, render, get_native_id()):
                raise RuntimeError("Unmatched native build completion")
            options = self._menu_options()
            snapshot = submenu._snapshot(self._reader, menu, **options)
            if snapshot is not None and snapshot[0].parent_index is None:
                # The fallback is only for builds with no individual pets.
                # A missed native append must not place CAS after those pets.
                order._first_pet(self._reader, snapshot)

            def guarded_append(header, data):
                allowed_headers = (menu + item.VECTORS_OFFSET + item.VECTOR_SIZE,
                                   menu + item.VECTORS_OFFSET + 2 * item.VECTOR_SIZE)
                if header not in allowed_headers:
                    raise RuntimeError("Submenu append header differs")
                if header == allowed_headers[0]:
                    current = submenu._snapshot(self._reader, menu, **options)
                    if current is None:
                        raise RuntimeError("Fallback companion context disappeared")
                    order._first_pet(self._reader, current)
                if not self.authorize_append(menu):
                    raise RuntimeError("Submenu append no longer authorized")
                self._append(header, data)

            result = submenu.complete_builder(
                self._reader, menu, constructor=self._constructor,
                append=guarded_append, guard_capability=self,
                **self._menu_options(construction=True),
            )
            if result.root_added and not self._appended:
                self._appended = True
                LOGGER.info("Companion Auto Summon submenu entry appended; visible navigation remains a player check.")
        except Exception:
            self._stop("builder")
        finally:
            self._building = None
            self._lock.release()
        return None

    @staticmethod
    def _report_language(observation):
        LOGGER.info("Language observation: %s; native region=%s name=%s; text unchanged, reload safety unverified.",
                    observation.status, observation.region, observation.native_language)

    def _observe_language(self):
        if self._language is None:
            return
        try:
            self._language.sample(monotonic())
        except Exception:
            # Optional diagnostics must never disable the working menu.
            self._language = None

    @cas_item_label.after
    def after_label(self, menu, output):
        if not self._enter():
            return None
        try:
            if SETTINGS_TOGGLE_ENABLED:
                options = self._menu_options()
                selected = toggle.selected_child_state(self._reader, menu, **options)
                role = selected.child_selected if selected is not None else 0
                setting = toggle.setting_key(role) if EXTENDED_SETTINGS_ENABLED else "enabled"
                state = self._preferences.snapshot(setting)
                if state is None:
                    caption = "Automatic summoning: unavailable"
                elif state.stopped:
                    caption = "Automatic summoning: stopped"
                else:
                    caption = "Automatic summoning: " + ("ON" if state.desired else "OFF")
                    if state.pending:
                        caption += " (pending)"
                    elif not state.settings_ok:
                        caption += " (session only)"
                encoded = (toggle.preference_label(role, state) if EXTENDED_SETTINGS_ENABLED
                           else item.encode_label(caption))
                label = toggle.selected_label(self._reader, menu, encoded, **options)
            else:
                label = submenu.selected_label(self._reader, menu)
            if label is not None and not self._stopped:
                self._observe_language()
                if self._stopped:
                    return None
                self._writer(output, label)
                if not self._label_seen:
                    self._label_seen = True
                    LOGGER.info("Submenu label supplied; visible rendering remains a player check.")
        except Exception:
            self._stop("label")
        finally:
            self._lock.release()
        return None

    @cas_submenu_trigger.before
    def before_trigger(self, menu, action, called_as_menu):
        if not self._enter("trigger_before"):
            return None
        try:
            intent = self._confirmation_intent
            self._confirmation_intent = None
            options = self._menu_options()
            token = submenu.capture_activation(self._reader, menu, action, called_as_menu, **options)
            preference_token = None
            if (SETTINGS_TOGGLE_ENABLED and token is None and intent is not None
                    and intent[:2] == (menu, self._thread)):
                token = toggle.capture_activation(
                    self._reader, menu, action, called_as_menu, intent[2], **options)
                if token is not None:
                    preference_token = intent[3]
            if not self._stopped:
                # Numeric argument identities live only across this original
                # invocation. The action pointer is never dereferenced AFTER.
                self._pending = (menu, action, called_as_menu, self._thread, token, preference_token)
        except Exception:
            self._stop("activation_before")
        finally:
            if self._stopped:
                self._pending = None
            self._lock.release()
        # No NOOP or argument substitution: all native calls execute normally.
        return None

    @cas_submenu_trigger.after
    def after_trigger(self, menu, action, called_as_menu, _result_):
        if not self._enter("trigger_after"):
            return None
        try:
            pending = self._pending
            if pending is None or pending[:4] != (menu, action, called_as_menu, get_native_id()):
                raise RuntimeError("Unmatched activation completion")
            if pending[4] is None:
                return None
            if _result_ is not False:
                raise RuntimeError("Tagged None action returned an unexpected result")
            if SETTINGS_TOGGLE_ENABLED and type(pending[4]) is toggle.ChildActivationToken:
                if not toggle.validate_activation(
                        self._reader, menu, pending[4], guard_capability=self, **self._menu_options()):
                    raise RuntimeError("Settings activation context changed")
                if self._reader(menu + PENDING_SELECTION_OFFSET, 1) != b"\0":
                    raise RuntimeError("Native deferred selection is still pending")
                if not self.authorize_append(menu):
                    raise RuntimeError("Settings activation no longer authorized")
                if self._preferences.commit_toggle(pending[5], authorize=lambda: not self._stopped):
                    LOGGER.info("Native menu queued a setting change; local player update will apply it.")
                else:
                    LOGGER.info("Native menu toggle was not queued because its preference context changed or was unavailable.")
                return None
            if not submenu.validate_activation(self._reader, menu, pending[4], guard_capability=self,
                                               **self._menu_options()):
                raise RuntimeError("Submenu activation context changed")
            if self._reader(menu + PENDING_SELECTION_OFFSET, 1) != b"\0":
                raise RuntimeError("Native deferred selection is still pending")
            self._write_checked(menu, item.DEPTH_OFFSET, 2)
            self._select_checked(menu)
            if not self._opened:
                self._opened = True
                LOGGER.info("Inert settings submenu transition requested; visible open/back/rebuild behavior remains unverified.")
        except Exception:
            # Never roll back native storage or free the binding guard after a
            # partial operation. Native maintenance handles an empty subpage.
            self._stop("activation_after")
        finally:
            self._pending = None
            self._lock.release()
        # Native submenu transitions also return false. True closes the menu.
        return None

    @(cas_toggle_confirm.before if SETTINGS_TOGGLE_ENABLED else lambda callback: callback)
    def before_confirmation(self, menu):
        if not SETTINGS_TOGGLE_ENABLED or not self._enter("confirmation_before"):
            return None
        try:
            item._address(menu, 0, PENDING_SELECTION_OFFSET + 1)
            self._confirmation_call = (menu, self._thread)
        except Exception:
            self._stop("confirmation_before")
        finally:
            self._lock.release()
        return None

    @(cas_toggle_confirm.after if SETTINGS_TOGGLE_ENABLED else lambda callback: callback)
    def after_confirmation(self, menu, _result_):
        if not SETTINGS_TOGGLE_ENABLED or not self._enter("confirmation_after"):
            return None
        try:
            if self._confirmation_call != (menu, self._thread) or type(_result_) is not bool:
                raise RuntimeError("Unmatched native confirmation completion")
            self._confirmation_call = None
            fresh_press = (_result_ and self._confirmation_ready
                           and self._confirmation_menu == menu)
            self._confirmation_ready = not _result_
            self._confirmation_menu = menu
            if fresh_press:
                state = toggle.selected_child_state(self._reader, menu, **self._menu_options())
                if state is not None:
                    setting = toggle.setting_key(state.child_selected) if EXTENDED_SETTINGS_ENABLED else "enabled"
                    preference = self._preferences.capture_toggle(setting)
                    if preference is not None and not self._stopped:
                        self._confirmation_intent = (menu, self._thread, state, preference)
        except Exception:
            self._stop("confirmation_after")
        finally:
            self._confirmation_call = None
            if self._stopped:
                self._confirmation_intent = None
            self._lock.release()
        return None
