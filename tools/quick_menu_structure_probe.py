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
"""Separate read-only observation of natural quick-menu builds and labels.

Disabled source. An isolated diagnostic build must explicitly enable this
exact-build probe. It never invokes a native game function, writes game memory,
retains native pointers, or logs label text. This is not a custom menu item.
"""

import ctypes as C
import hashlib
from importlib.metadata import PackageNotFoundError, version
from itertools import count
import logging
import math
from pathlib import Path
from threading import Lock, get_ident
from time import monotonic

from pymhf import Mod
from pymhf.core import _internal
from pymhf.core.hooking import static_function_hook


PROBE_ENABLED = False
EXPECTED_EXE_SHA256 = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"
EXPECTED_PYMHF = "0.2.4"
BUILD_ACTIONS_RVA = 0x151ED00
BUILD_LABEL_RVA = 0x1523220
DEPTH_OFFSET = 0xA050
VECTORS_OFFSET = 0xA058
SELECTIONS_OFFSET = 0xA088
VECTOR_SIZE = 16
ITEM_SIZE = 0xE0
ITEM_ACTION_OFFSET = 4
LABEL_SIZE = 128
# These are diagnostic read limits, not changes to any gameplay/menu limit.
MAX_VECTOR_ITEMS = 256
MIN_SAMPLE_INTERVAL = 0.25
MAX_SAMPLES = 2048
MAX_DETAILS = 32
MIN_USER_ADDRESS = 0x10000
MAX_USER_ADDRESS = 0x7FFFFFFFFFFF
READ_SIZES = frozenset({4, VECTOR_SIZE, LABEL_SIZE})
LOGGER = logging.getLogger("CompanionMenuStructureProbe")


def supported_runtime():
    """Reject unsupported or unrequested probes before hook registration."""
    try:
        if not PROBE_ENABLED or not _internal.IS_INJECTED or _internal.BASE_ADDRESS <= 0:
            return False
        if C.sizeof(C.c_void_p) != 8 or version("pymhf") != EXPECTED_PYMHF:
            return False
        with Path(_internal.BINARY_PATH).open("rb") as binary:
            return hashlib.file_digest(binary, "sha256").hexdigest() == EXPECTED_EXE_SHA256
    except (OSError, ValueError, TypeError, AttributeError, PackageNotFoundError):
        return False


def checked_address(pointer, offset, size):
    """Validate the entire range without reading it or leaking its address."""
    if type(pointer) is not int or type(offset) is not int or type(size) is not int:
        raise ValueError("Invalid diagnostic range type")
    if pointer < MIN_USER_ADDRESS or offset < 0 or size <= 0:
        raise ValueError("Invalid diagnostic range")
    address = pointer + offset
    if address > MAX_USER_ADDRESS - size + 1:
        raise ValueError("Diagnostic range outside user memory")
    return address


def create_current_process_reader():
    """Lazily bind Windows read-only APIs; no other process is opened."""
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
        if type(size) is not int or size not in READ_SIZES:
            raise ValueError("Unsupported diagnostic copy size")
        checked_address(address, 0, size)
        buffer = C.create_string_buffer(size)
        transferred = C.c_size_t(0)
        succeeded = read_process_memory(handle, address, buffer, size, C.byref(transferred))
        if not succeeded or transferred.value != size:
            raise OSError("Unable to copy complete diagnostic data")
        return buffer.raw

    return read_exact


def copy_bytes(reader, pointer, offset, size):
    if type(size) is not int or size not in READ_SIZES:
        raise ValueError("Unsupported diagnostic copy size")
    address = checked_address(pointer, offset, size)
    data = reader(address, size)
    if not isinstance(data, bytes) or len(data) != size:
        raise ValueError("Diagnostic reader returned incomplete or unowned data")
    return data


def read_integer(reader, pointer, offset):
    return int.from_bytes(copy_bytes(reader, pointer, offset, 4), "little", signed=True)


def read_depth(reader, menu):
    depth = read_integer(reader, menu, DEPTH_OFFSET)
    if not 0 <= depth <= 2:
        raise ValueError("Unexpected menu depth")
    return depth


def read_vector_selection(reader, menu, depth):
    """Return sanitized metadata only; stale selection is an expected status.

    The natural builder returns before selection maintenance. Empty vectors or
    temporarily out-of-range selected indices must not cause item reads.
    """
    if type(depth) is not int or not 0 <= depth <= 2:
        raise ValueError("Invalid requested vector depth")
    header = copy_bytes(reader, menu, VECTORS_OFFSET + depth * VECTOR_SIZE, VECTOR_SIZE)
    capacity = int.from_bytes(header[:4], "little")
    item_count = int.from_bytes(header[4:8], "little")
    data_pointer = int.from_bytes(header[8:16], "little")
    if item_count > capacity or capacity > MAX_VECTOR_ITEMS:
        raise ValueError("Menu vector exceeds diagnostic bounds")
    selected = read_integer(reader, menu, SELECTIONS_OFFSET + depth * 4)
    if item_count == 0:
        return (depth, capacity, item_count, selected, "empty", None)
    # Validate the full occupied range before computing a selected-item read.
    # Its capacity is not treated as readable initialized item data.
    checked_address(data_pointer, 0, item_count * ITEM_SIZE)
    if not 0 <= selected < item_count:
        return (depth, capacity, item_count, selected, "stale_selection", None)
    action = read_integer(reader, data_pointer, selected * ITEM_SIZE + ITEM_ACTION_OFFSET)
    if not 0 <= action <= 66:
        raise ValueError("Unexpected selected menu action")
    return (depth, capacity, item_count, selected, "selected", action)


def inspect_builder(reader, menu):
    depth = read_depth(reader, menu)
    vectors = tuple(read_vector_selection(reader, menu, level) for level in range(3))
    return (depth, vectors)


def inspect_label(reader, menu, output):
    # Validate the output range before reading any menu field.
    checked_address(output, 0, LABEL_SIZE)
    depth = read_depth(reader, menu)
    vector = read_vector_selection(reader, menu, depth)
    data = copy_bytes(reader, output, 0, LABEL_SIZE)
    terminator = data.find(b"\0")
    # No text/bytes or item pointers escape this function.
    return (depth, vector[4], vector[5], terminator >= 0,
            terminator if terminator >= 0 else None)


@static_function_hook(offset=BUILD_ACTIONS_RVA)
def cas_probe_build_actions(menu: C.c_void_p, render: C.c_void_p) -> None:
    ...


@static_function_hook(offset=BUILD_LABEL_RVA)
def cas_probe_build_label(menu: C.c_void_p, output: C.c_void_p) -> None:
    ...


class CompanionMenuStructureProbe(Mod):
    """Two throttled AFTER observers; native calls always retain their result."""

    _disabled = not supported_runtime()

    def __init__(self, reader=None, logger=None, clock=None, thread_id=None):
        self._reader = reader
        self._logger = LOGGER if logger is None else logger
        self._clock = monotonic if clock is None else clock
        self._thread_id = get_ident if thread_id is None else thread_id
        self._observation_lock = Lock()
        self._stopped = False
        self._first_thread = None
        self._single_thread = True
        self._channels = {
            name: {"calls": count(1), "started": None, "last_sample": None,
                   "samples": 0, "details": 0, "signature": None, "capped": False}
            for name in ("builder", "label")
        }
        super().__init__()

    def _stop_after_error(self):
        if self._stopped:
            return
        self._stopped = True
        try:
            self._logger.warning("Quick menu structure probe disabled after an invalid or unreadable observation.")
        except Exception:
            pass  # A diagnostic logger must not alter the native return path.

    def _observe(self, channel, menu, output):
        if self._stopped or self._disabled or not PROBE_ENABLED:
            return None
        state = self._channels[channel]
        if state["capped"]:
            return None
        if not _internal.IS_INJECTED or _internal.BASE_ADDRESS <= 0:
            self._stopped = True
            return None
        # itertools.count assigns a unique callback sequence in CPython.
        # Count callbacks even when sampling is throttled or lock-contended.
        callbacks = next(state["calls"])
        if not self._observation_lock.acquire(blocking=False):
            return None
        try:
            if self._stopped or state["capped"]:
                return None
            # Timestamp only after acquiring the lock: a preempted callback may
            # otherwise carry an older timestamp than a newer completed sample.
            now = self._clock()
            if type(now) not in (int, float) or not math.isfinite(now):
                raise ValueError("Invalid diagnostic clock")
            if state["started"] is None:
                state["started"] = now
            if now < state["started"]:
                raise ValueError("Diagnostic clock moved backwards")
            thread = self._thread_id()
            if self._first_thread is None:
                self._first_thread = thread
            same_thread = thread == self._first_thread
            self._single_thread = self._single_thread and same_thread
            if state["last_sample"] is not None:
                if now < state["last_sample"]:
                    raise ValueError("Diagnostic sample clock moved backwards")
                if now - state["last_sample"] < MIN_SAMPLE_INTERVAL:
                    return None
            # Validate known fixed ranges before lazily binding a reader.
            checked_address(menu, DEPTH_OFFSET, 4)
            if channel == "label":
                checked_address(output, 0, LABEL_SIZE)
            if self._reader is None:
                self._reader = create_current_process_reader()
            if channel == "builder":
                snapshot = inspect_builder(self._reader, menu)
            else:
                snapshot = inspect_label(self._reader, menu, output)
            state["samples"] += 1
            state["last_sample"] = now
            elapsed = now - state["started"]
            if snapshot != state["signature"]:
                state["signature"] = snapshot
                state["details"] += 1
                self._logger.info(
                    "Quick menu structure: channel=%s callbacks=%d samples=%d elapsed=%.3f same_thread=%s snapshot=%s",
                    channel, callbacks, state["samples"], elapsed, same_thread, snapshot)
            if channel == "label" and not snapshot[3]:
                raise ValueError("Label has no terminator within its bounded buffer")
            if state["samples"] >= MAX_SAMPLES or state["details"] >= MAX_DETAILS:
                state["capped"] = True
                reason = "sample_limit" if state["samples"] >= MAX_SAMPLES else "detail_limit"
                self._logger.info(
                    "Quick menu structure limit: channel=%s reason=%s callbacks=%d samples=%d details=%d elapsed=%.3f single_thread=%s",
                    channel, reason, callbacks, state["samples"], state["details"], elapsed,
                    self._single_thread)
        except Exception:
            self._stop_after_error()
        finally:
            self._observation_lock.release()
        return None

    @cas_probe_build_actions.after
    def observe_builder(self, menu, render):
        self._observe("builder", menu, render)
        return None

    @cas_probe_build_label.after
    def observe_label(self, menu, output):
        self._observe("label", menu, output)
        return None
