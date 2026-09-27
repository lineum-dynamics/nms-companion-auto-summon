# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["pymhf[gui]==0.2.4"]
#
# [tool.pymhf]
# exe = "NMS.exe"
# steam_gameid = 275850
# start_paused = false
# interactive_console = false
#
# [tool.pymhf.logging]
# shown = false
# log_dir = "{CURR_DIR}"
# log_level = "info"
#
# [tool.pymhf.gui]
# shown = false
# always_on_top = false
# ///
"""Opt-in, exact-build observation of naturally selected quick-menu actions.

This developer probe adds no menu entries and invokes no native game function.
Its source is disabled; an isolated diagnostic build must explicitly enable it.
Only a before callback copies two verified integers from the current process.
"""

import ctypes as C
import hashlib
import logging
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from threading import Lock

from pymhf import Mod
from pymhf.core import _internal
from pymhf.core.hooking import static_function_hook


PROBE_ENABLED = False
EXPECTED_EXE_SHA256 = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"
EXPECTED_PYMHF = "0.2.4"
TRIGGER_ACTION_RVA = 0x1526940
ACTION_ID_OFFSET = 4
ACTION_DEPTH_OFFSET = 0xA050
MAX_EVENTS = 64
MIN_USER_ADDRESS = 0x10000
MAX_USER_ADDRESS = 0x7FFFFFFFFFFF
LOGGER = logging.getLogger("CompanionMenuProbe")


def supported_runtime():
    """Reject the class before registration unless every explicit guard passes."""
    try:
        if not PROBE_ENABLED or not _internal.IS_INJECTED or _internal.BASE_ADDRESS <= 0:
            return False
        if C.sizeof(C.c_void_p) != 8 or version("pymhf") != EXPECTED_PYMHF:
            return False
        with Path(_internal.BINARY_PATH).open("rb") as binary:
            return hashlib.file_digest(binary, "sha256").hexdigest() == EXPECTED_EXE_SHA256
    except (OSError, ValueError, TypeError, AttributeError, PackageNotFoundError):
        return False


def checked_read_address(pointer, offset, size):
    """Validate a bounded scalar range without touching native memory."""
    if type(pointer) is not int or type(offset) is not int or type(size) is not int:
        raise ValueError("Invalid scalar address type")
    if pointer < MIN_USER_ADDRESS or offset < 0 or size != 4:
        raise ValueError("Invalid scalar address range")
    address = pointer + offset
    if address > MAX_USER_ADDRESS - size + 1:
        raise ValueError("Scalar address outside user memory")
    return address


def create_current_process_reader():
    """Bind a read-only Windows API lazily, inside the injected callback only.

    The returned callable copies exactly four bytes or raises. It never opens
    another process, retains input pointers, changes memory, or closes handles.
    The current-process pseudo handle requires no CloseHandle.
    """
    kernel32 = C.WinDLL("kernel32", use_last_error=True)
    get_current_process = kernel32.GetCurrentProcess
    get_current_process.argtypes = []
    get_current_process.restype = C.c_void_p
    read_process_memory = kernel32.ReadProcessMemory
    read_process_memory.argtypes = [C.c_void_p, C.c_void_p, C.c_void_p,
                                   C.c_size_t, C.POINTER(C.c_size_t)]
    read_process_memory.restype = C.c_int
    handle = get_current_process()

    def read_exact(address, size):
        checked_read_address(address, 0, size)
        buffer = C.create_string_buffer(size)
        transferred = C.c_size_t(0)
        succeeded = read_process_memory(handle, address, buffer, size, C.byref(transferred))
        if not succeeded or transferred.value != size:
            raise OSError("Unable to copy the complete diagnostic scalar")
        return buffer.raw

    return read_exact


def read_scalar(reader, address):
    """Parse only an exact Python-owned scalar copy; reject partial reads."""
    value = reader(address, 4)
    if not isinstance(value, bytes) or len(value) != 4:
        raise ValueError("Diagnostic reader must return exactly four owned bytes")
    return int.from_bytes(value, "little", signed=True)


@static_function_hook(offset=TRIGGER_ACTION_RVA)
def cas_probe_trigger_action(menu: C.c_void_p, action: C.c_void_p,
                             called_as_menu: C.c_bool) -> C.c_bool:
    ...


class CompanionMenuProbe(Mod):
    """Bounded observation only; every callback returns None to preserve play."""

    _disabled = not supported_runtime()

    def __init__(self, reader=None, logger=None):
        self._reader = reader
        self._logger = LOGGER if logger is None else logger
        self._stopped = False
        self._event_count = 0
        self._observation_lock = Lock()
        super().__init__()

    def _stop_after_error(self):
        self._stopped = True
        try:
            self._logger.warning("Quick menu probe disabled after an invalid or unreadable observation.")
        except Exception:
            pass  # Logging failure must never alter a native call.

    @cas_probe_trigger_action.before
    def observe_action(self, menu, action, called_as_menu):
        # A contended or reentrant callback passes through without waiting.
        if not self._observation_lock.acquire(blocking=False):
            return None
        try:
            if self._stopped or self._disabled or not PROBE_ENABLED:
                return None
            if not _internal.IS_INJECTED or _internal.BASE_ADDRESS <= 0:
                self._stopped = True
                return None
            if type(called_as_menu) is not bool:
                raise ValueError("Invalid menu-call flag")
            action_address = checked_read_address(action, ACTION_ID_OFFSET, 4)
            depth_address = checked_read_address(menu, ACTION_DEPTH_OFFSET, 4)
            if self._reader is None:
                self._reader = create_current_process_reader()
            action_id = read_scalar(self._reader, action_address)
            if not 0 <= action_id <= 66:
                raise ValueError("Unexpected quick-menu action")
            depth = read_scalar(self._reader, depth_address)
            if not 0 <= depth <= 2:
                raise ValueError("Unexpected quick-menu depth")
            self._logger.info("Quick menu observation: action=%d depth=%d called_as_menu=%s",
                              action_id, depth, called_as_menu)
            self._event_count += 1
            if self._event_count >= MAX_EVENTS:
                self._stopped = True
                self._logger.info("Quick menu probe reached its 64-event limit; observation stopped.")
        except Exception:
            self._stop_after_error()
        finally:
            self._observation_lock.release()
        return None
