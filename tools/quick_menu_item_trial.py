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
"""Disabled developer trial: one inert visible item, no preference changes.

This is NOT an observation-only probe. An explicitly built future trial installs
a process-lifetime native binding filter before allowing native item insertion.
The exact-build and current-process guards must pass. No automatic summoning,
settings changes, key-state polling or save-file access occurs here.
"""

import ctypes as C
import hashlib
from importlib.metadata import PackageNotFoundError, version
import logging
from pathlib import Path
import sys
from threading import Lock, get_native_id

# The isolated build copies these reviewed helper sources beside this script.
# Keep the loader independent of the user's current directory.
_helper_directory = str(Path(__file__).resolve().parent)
if _helper_directory not in sys.path:
    sys.path.insert(0, _helper_directory)
import quick_menu_item as item
from quick_menu_guard_runtime import GuardError, ensure_guard

from pymhf import Mod
from pymhf.core import _internal
from pymhf.core.hooking import static_function_hook


TRIAL_ENABLED = False
EXPECTED_EXE_SHA256 = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"
BUILD_ACTIONS_RVA = 0x151ED00
BUILD_LABEL_RVA = 0x1523220
ITEM_CONSTRUCTOR_RVA = 0x1432FC0
ITEM_APPEND_RVA = 0x1533980
LOGGER = logging.getLogger("CompanionMenuItemTrial")


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
        if size not in (4, 16):
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

    return read, write_label


def native_adapters(base):
    """Bind statically audited ABIs; adapters hold only temporary owned buffers."""
    constructor = C.WINFUNCTYPE(C.c_void_p, C.c_void_p, C.c_uint32, C.c_int32,
                               C.c_bool, C.c_bool)(base + ITEM_CONSTRUCTOR_RVA)
    append = C.WINFUNCTYPE(C.c_void_p, C.c_void_p, C.c_void_p)(base + ITEM_APPEND_RVA)

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
        if not append(header, address):
            raise RuntimeError("Native item append returned no item")
        # No item pointer is retained or read; native growth may move storage.

    return construct, append_item


@static_function_hook(offset=BUILD_ACTIONS_RVA)
def cas_item_builder(menu: C.c_void_p, render: C.c_void_p) -> None:
    pass


@static_function_hook(offset=BUILD_LABEL_RVA)
def cas_item_label(menu: C.c_void_p, output: C.c_void_p) -> None:
    pass


class CompanionMenuItemTrial(Mod):
    _version = "0.4.1-inert-item-trial"
    _author = "Companion Auto Summon contributors"
    _description = "One inert native-menu item with a separate native binding guard"
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
        if self._disabled:
            return
        try:
            self._reader, self._writer = current_process_io()
            self._constructor, self._append = native_adapters(_internal.BASE_ADDRESS)
            # This must complete before pyMHF can enable the builder callback.
            # The separately pinned filter outlives callback failure/reload.
            self._guard = ensure_guard(_internal.BASE_ADDRESS, _internal.BINARY_PATH)
            self._stopped = False
            LOGGER.info("Inert menu trial ready; native binding filter installed. No auto-summon or settings actions.")
        except GuardError as error:
            self._stop("initialization: " + str(error))
        except Exception:
            self._stop("initialization")

    def _stop(self, reason):
        self._stopped = True
        if not self._notice_sent:
            self._notice_sent = True
            try:
                LOGGER.warning("Inert menu insertion stopped (%s); native binding filter is retained.", reason)
            except Exception:
                pass

    def _enter(self):
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
        except Exception:
            self._stop("thread_lookup")
            self._lock.release()
            return False
        return True

    def authorize_append(self, menu):
        # Helper checks this twice; a contending callback can stop insertion
        # while a native constructor has released the GIL.
        return (not self._stopped and self._thread == get_native_id()
                and self._guard is not None and self._guard.authorize_append(menu) is True
                and not self._stopped)

    @cas_item_builder.after
    def after_builder(self, menu, render):
        if not self._enter():
            return None
        try:
            # Avoid costly guard and native construction work outside the
            # single supported companion context. The helper rechecks again.
            if item.plan_append(self._reader, menu) is item.AppendStatus.READY:
                def guarded_append(header, data):
                    if (header != menu + item.VECTORS_OFFSET + item.VECTOR_SIZE
                            or not self.authorize_append(menu)):
                        raise RuntimeError("Inert insertion no longer authorized")
                    self._append(header, data)

                status = item.append_inert_item(
                    self._reader, menu, constructor=self._constructor,
                    append=guarded_append, guard_capability=self,
                )
                if status is item.AppendStatus.APPENDED:
                    if item.plan_append(self._reader, menu) is not item.AppendStatus.ALREADY_PRESENT:
                        raise RuntimeError("Native insertion could not be read back")
                    if not self._appended:
                        self._appended = True
                        LOGGER.info("Inert Companion Auto Summon item appended; awaiting visible navigation result.")
        except Exception:
            self._stop("builder")
        finally:
            self._lock.release()
        return None

    @cas_item_label.after
    def after_label(self, menu, output):
        if not self._enter():
            return None
        try:
            label = item.selected_label(self._reader, menu)
            if label is not None and not self._stopped:
                self._writer(output, label)
                if not self._label_seen:
                    self._label_seen = True
                    LOGGER.info("Inert menu label supplied; visible rendering remains a player check.")
        except Exception:
            self._stop("label")
        finally:
            self._lock.release()
        return None
