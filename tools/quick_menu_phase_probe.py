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
"""Disabled, read-only phase observer for one exact native quick-menu build.

This observes natural Update/Controls/Tail calls. It does not alter selection,
read input, insert an action, invoke a native game function, or access saves.
Transient addresses are used only for invocation identity and storage equality.
Every menu read uses the current callback argument, never a retained address.
"""

import ctypes as C
import hashlib
from importlib.metadata import PackageNotFoundError, version
import logging
import math
from pathlib import Path
from threading import Lock, get_native_id
from time import monotonic

from pymhf import Mod
from pymhf.core import _internal
from pymhf.core.hooking import static_function_hook


PROBE_ENABLED = False
EXPECTED_EXE_SHA256 = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"
EXPECTED_PYMHF = "0.2.4"
UPDATE_RVA = 0x151D200
CONTROLS_RVA = 0x1530C00
TAIL_RVA = 0x1525600
DEPTH_OFFSET = 0xA050
VECTORS_OFFSET = 0xA058
SELECTIONS_OFFSET = 0xA088
VECTOR_SIZE = 16
ITEM_SIZE = 0xE0
ITEM_ACTION_OFFSET = 4
# Diagnostic budgets never change a native limit or the game's menu contents.
MAX_VECTOR_ITEMS = 256
MIN_SAMPLE_INTERVAL = 0.25
MAX_INVOCATIONS = 120000
MAX_SAMPLES = 2048
MAX_DETAILS = 32
MAX_THREADS = 8
MIN_USER_ADDRESS = 0x10000
MAX_USER_ADDRESS = 0x7FFFFFFFFFFF
READ_SIZES = frozenset({4, VECTOR_SIZE})
LOGGER = logging.getLogger("CompanionMenuPhaseProbe")


def supported_runtime():
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
    if type(pointer) is not int or type(offset) is not int or type(size) is not int:
        raise ValueError("Invalid diagnostic range type")
    if pointer < MIN_USER_ADDRESS or offset < 0 or size <= 0:
        raise ValueError("Invalid diagnostic range")
    address = pointer + offset
    if address > MAX_USER_ADDRESS - size + 1:
        raise ValueError("Diagnostic range outside user memory")
    return address


def create_current_process_reader():
    """Lazily bind exact-size read-only Windows APIs in the callback."""
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
        if not read_process_memory(handle, address, buffer, size, C.byref(transferred)):
            raise OSError("Unable to copy diagnostic data")
        if transferred.value != size:
            raise OSError("Incomplete diagnostic copy")
        return buffer.raw

    return read_exact


def copy_bytes(reader, pointer, offset, size):
    if type(size) is not int or size not in READ_SIZES:
        raise ValueError("Unsupported diagnostic copy size")
    data = reader(checked_address(pointer, offset, size), size)
    if not isinstance(data, bytes) or len(data) != size:
        raise ValueError("Diagnostic copy must contain exact owned bytes")
    return data


def read_integer(reader, pointer, offset):
    return int.from_bytes(copy_bytes(reader, pointer, offset, 4), "little", signed=True)


def inspect_menu(reader, menu):
    """Return sanitized fields and separate temporary storage identities."""
    depth = read_integer(reader, menu, DEPTH_OFFSET)
    if not 0 <= depth <= 2:
        raise ValueError("Unexpected menu depth")
    vectors = []
    storage = []
    for level in range(3):
        header = copy_bytes(reader, menu, VECTORS_OFFSET + level * VECTOR_SIZE, VECTOR_SIZE)
        capacity = int.from_bytes(header[:4], "little")
        item_count = int.from_bytes(header[4:8], "little")
        data_pointer = int.from_bytes(header[8:16], "little")
        if item_count > capacity or capacity > MAX_VECTOR_ITEMS:
            raise ValueError("Menu vector exceeds diagnostic bounds")
        selected = read_integer(reader, menu, SELECTIONS_OFFSET + level * 4)
        action = None
        if item_count == 0:
            status = "empty"
        else:
            checked_address(data_pointer, 0, item_count * ITEM_SIZE)
            if not 0 <= selected < item_count:
                status = "stale_selection"
            else:
                status = "selected"
                action = read_integer(reader, data_pointer, selected * ITEM_SIZE + ITEM_ACTION_OFFSET)
                if not 0 <= action <= 66:
                    raise ValueError("Unexpected selected menu action")
        vectors.append((level, capacity, item_count, selected, status, action))
        storage.append(data_pointer)
    return (depth, tuple(vectors)), tuple(storage)


@static_function_hook(offset=UPDATE_RVA)
def cas_probe_update(menu: C.c_void_p, elapsed: C.c_float, render: C.c_void_p) -> None:
    ...


@static_function_hook(offset=CONTROLS_RVA)
def cas_probe_controls(menu: C.c_void_p, buffer1: C.c_void_p, buffer2: C.c_void_p) -> None:
    ...


@static_function_hook(offset=TAIL_RVA)
def cas_probe_tail(menu: C.c_void_p, render: C.c_void_p) -> None:
    ...


class CompanionMenuPhaseProbe(Mod):
    """A bounded phase machine that never changes a native argument/result."""

    _disabled = not supported_runtime()

    def __init__(self, reader=None, logger=None, clock=None, thread_id=None):
        self._reader = reader
        self._logger = LOGGER if logger is None else logger
        self._clock = monotonic if clock is None else clock
        self._thread_id = get_native_id if thread_id is None else thread_id
        self._observation_lock = Lock()
        self._stopped = False
        self._invocations = {}
        self._thread_ordinals = {}
        self._started = None
        self._last_clock = None
        self._last_sample_started = None
        self._last_signature = None
        self._counts = dict.fromkeys((
            "updates", "completed", "skipped", "samples", "details", "callbacks",
            "interval_changes", "post_tail_changes", "missing", "duplicate", "unmatched",
            "identity_mismatch", "nested", "concurrent", "contention", "read_error",
            "clock_error", "invalid_argument", "thread_limit", "logging_error"), 0)
        super().__init__()

    def _stop(self, reason, *, failure=True):
        if self._stopped:
            return
        self._stopped = True
        self._invocations.clear()
        self._thread_ordinals.clear()
        if failure and reason in self._counts:
            self._counts[reason] += 1
        try:
            self._logger.info("Quick menu phase observer stopped: reason=%s counts=%s", reason,
                              tuple(self._counts.items()))
        except Exception:
            pass  # Diagnostics never escape into the original game call.

    def _read_checked(self, address, size):
        if self._stopped:
            raise RuntimeError("Observation already stopped")
        data = self._reader(address, size)
        if self._stopped:
            raise RuntimeError("Observation stopped during copy")
        return data

    def _snapshot(self, menu):
        if self._reader is None:
            self._reader = create_current_process_reader()
        return inspect_menu(self._read_checked, menu)

    def _finish(self, thread, record, now, menu):
        if self._stopped:
            return
        if record["phase"] == "entered":
            self._counts["skipped"] += 1
            del self._invocations[thread]
        elif record["phase"] != "tail":
            self._stop("missing")
            return
        else:
            if record["sampled"]:
                try:
                    post, post_storage = self._snapshot(menu)
                except Exception:
                    self._stop("read_error")
                    return
                if self._stopped:
                    return
                controls, controls_storage = record["controls"]
                tail, tail_storage = record["tail"]
                interval_storage_equal = tuple(a == b for a, b in zip(controls_storage, tail_storage))
                post_storage_equal = tuple(a == b for a, b in zip(tail_storage, post_storage))
                interval_equal = controls == tail and all(interval_storage_equal)
                post_changed = tail != post or not all(post_storage_equal)
                self._counts["samples"] += 1
                self._counts["interval_changes"] += int(not interval_equal)
                self._counts["post_tail_changes"] += int(post_changed)
                signature = (controls, tail, post, interval_storage_equal, post_storage_equal)
            if self._stopped:
                return
            self._counts["completed"] += 1
            # Clear every borrowed identity before formatting/logging completion.
            del self._invocations[thread]
            if record["sampled"] and signature != self._last_signature:
                self._last_signature = signature
                self._counts["details"] += 1
                try:
                    self._logger.info(
                        "Quick menu phase: thread=%d updates=%d samples=%d elapsed=%.3f interval_equal=%s post_tail_changed=%s controls=%s tail=%s post=%s interval_storage_equal=%s post_storage_equal=%s",
                        record["ordinal"], self._counts["updates"], self._counts["samples"],
                        now - self._started, interval_equal, post_changed, controls, tail, post,
                        interval_storage_equal, post_storage_equal)
                except Exception:
                    self._stop("logging_error")
                    return
        if self._counts["updates"] >= MAX_INVOCATIONS:
            self._stop("invocation_limit", failure=False)
        elif self._counts["samples"] >= MAX_SAMPLES:
            self._stop("sample_limit", failure=False)
        elif self._counts["details"] >= MAX_DETAILS:
            self._stop("detail_limit", failure=False)

    def _observe(self, phase, menu, render, secondary=None, elapsed=None):
        if self._stopped or self._disabled or not PROBE_ENABLED:
            return None
        if not _internal.IS_INJECTED or _internal.BASE_ADDRESS <= 0:
            self._stop("runtime_unavailable", failure=False)
            return None
        if not self._observation_lock.acquire(blocking=False):
            self._stop("contention")
            return None
        try:
            if self._stopped:
                return None
            self._counts["callbacks"] += 1
            try:
                now = self._clock()
                if self._stopped:
                    return None
                if type(now) not in (int, float) or not math.isfinite(now):
                    raise ValueError("Invalid diagnostic clock")
                if self._last_clock is not None and now < self._last_clock:
                    raise ValueError("Diagnostic clock moved backwards")
                self._last_clock = now
                if self._started is None:
                    self._started = now
            except Exception:
                self._stop("clock_error")
                return None
            try:
                thread = self._thread_id()
                if self._stopped:
                    return None
                if type(thread) is not int or thread <= 0:
                    raise ValueError("Invalid native thread identity")
                checked_address(menu, DEPTH_OFFSET, 4)
                checked_address(render, 0, 0x200)
                if phase in ("enter", "exit"):
                    if type(elapsed) not in (int, float) or not math.isfinite(elapsed):
                        raise ValueError("Invalid elapsed argument")
            except Exception:
                self._stop("invalid_argument")
                return None
            if self._stopped:
                return None
            if phase == "enter":
                if self._invocations:
                    self._stop("nested" if thread in self._invocations else "concurrent")
                    return None
                if thread not in self._thread_ordinals:
                    if len(self._thread_ordinals) >= MAX_THREADS:
                        self._stop("thread_limit")
                        return None
                    self._thread_ordinals[thread] = len(self._thread_ordinals) + 1
                self._counts["updates"] += 1
                self._invocations[thread] = {
                    "menu_identity": menu, "render_identity": render, "phase": "entered",
                    "sampled": False, "ordinal": self._thread_ordinals[thread]}
                return None
            record = self._invocations.get(thread)
            if record is None:
                self._stop("concurrent" if self._invocations else "unmatched")
                return None
            if menu != record["menu_identity"] or render != record["render_identity"]:
                self._stop("identity_mismatch")
                return None
            if phase == "controls":
                if secondary != render + 0x100:
                    self._stop("identity_mismatch")
                    return None
                if record["phase"] != "entered":
                    self._stop("duplicate")
                    return None
                record["phase"] = "controls"
                if self._last_sample_started is None or now - self._last_sample_started >= MIN_SAMPLE_INTERVAL:
                    record["controls"] = self._snapshot(menu)
                    if self._stopped:
                        return None
                    record["sampled"] = True
                    self._last_sample_started = now
            elif phase == "tail":
                if record["phase"] != "controls":
                    self._stop("duplicate" if record["phase"] == "tail" else "missing")
                    return None
                if record["sampled"]:
                    record["tail"] = self._snapshot(menu)
                    if self._stopped:
                        return None
                record["phase"] = "tail"
            elif phase == "exit":
                self._finish(thread, record, now, menu)
            else:
                self._stop("unmatched")
        except Exception:
            self._stop("read_error")
        finally:
            # A contending callback can stop observation while this owner is in
            # a clock/thread/read call. Never retain identities if it resumes.
            if self._stopped:
                self._invocations.clear()
                self._thread_ordinals.clear()
            self._observation_lock.release()
        return None

    @cas_probe_update.before
    def before_update(self, menu, elapsed, render):
        self._observe("enter", menu, render, elapsed=elapsed)
        return None

    @cas_probe_controls.after
    def after_controls(self, menu, buffer1, buffer2):
        self._observe("controls", menu, buffer1, secondary=buffer2)
        return None

    @cas_probe_tail.before
    def before_tail(self, menu, render):
        self._observe("tail", menu, render)
        return None

    @cas_probe_update.after
    def after_update(self, menu, elapsed, render):
        self._observe("exit", menu, render, elapsed=elapsed)
        return None
