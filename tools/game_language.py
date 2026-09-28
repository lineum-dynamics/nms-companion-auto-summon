"""Exact-build copied language observations; no native calls or text selection.

The caller owns a guarded current-process reader. This module never creates a
process handle, follows a pointer, changes game memory, selects a language or
reads files. A stable prior-load snapshot does not prove current reload safety.
"""

from dataclasses import dataclass
import math
from threading import Lock


EXPECTED_EXE_SHA256 = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"
GUARD_RVA = 0x6E0154C
VTABLE_RVA = 0x350A7C8
LOAD_COMPLETE_RVA = 0x6E09DB0
NATIVE_LANGUAGES = (
    "ENGLISH", "USENGLISH", "FRENCH", "ITALIAN", "GERMAN", "SPANISH",
    "RUSSIAN", "POLISH", "DUTCH", "PORTUGUESE", "LATINAMERICANSPANISH",
    "BRAZILIANPORTUGUESE", "JAPANESE", "TRADITIONALCHINESE",
    "SIMPLIFIEDCHINESE", "TENCENTCHINESE", "KOREAN",
)
MIN_INTERVAL = 0.5
MAX_REPORTS = 8


@dataclass(frozen=True)
class LanguageObservation:
    """Bounded diagnostic values only; never a native pointer or locale policy."""

    status: str
    region: int | None = None
    native_language: str | None = None


def _read(reader, address, size):
    data = reader(address, size)
    if type(data) is not bytes or len(data) != size:
        raise ValueError("Incomplete language snapshot")
    return data


def read_language(reader, base):
    """Double-copy fixed fields after the caller's exact executable guard.

    The 16-byte record contains guard int32, vtable uint64 and region int32.
    No byte is interpreted until both record/flag copies agree. Even successful
    observation does not authorize changing text during a language reload.
    """
    if type(base) is not int or not 0 < base <= 0x7FFFFFFFFFFF - LOAD_COMPLETE_RVA:
        raise ValueError("Invalid guarded image base")
    first = (_read(reader, base + GUARD_RVA, 16), _read(reader, base + LOAD_COMPLETE_RVA, 1))
    second = (_read(reader, base + GUARD_RVA, 16), _read(reader, base + LOAD_COMPLETE_RVA, 1))
    if first != second:
        return LanguageObservation("unstable")
    record, loaded = first
    guard = int.from_bytes(record[:4], "little", signed=True)
    if guard >= -1:
        return LanguageObservation("not_initialized")
    if int.from_bytes(record[4:12], "little") != base + VTABLE_RVA:
        return LanguageObservation("unexpected_vtable")
    region = int.from_bytes(record[12:16], "little", signed=True)
    if not 0 <= region < len(NATIVE_LANGUAGES):
        return LanguageObservation("unconfigured")
    if loaded != b"\x01":
        return LanguageObservation("tables_not_ready")
    return LanguageObservation("initialized_load_seen", region, NATIVE_LANGUAGES[region])


class LanguageObserver:
    """Paced optional diagnostics; its failure must not stop the native menu."""

    def __init__(self, reader, base, report):
        self._reader, self._base, self._report = reader, base, report
        self._lock = Lock()
        self._next = 0.0
        self._previous = None
        self._reports = 0
        self._stopped = False

    def sample(self, now):
        """Caller supplies monotonic time while its own CAS caption is selected."""
        if not self._lock.acquire(blocking=False):
            return
        try:
            if self._stopped:
                return
            if type(now) not in (int, float) or not math.isfinite(now) or now < 0:
                self._stopped = True
                return
            if now < self._next:
                return
            self._next = now + MIN_INTERVAL
            try:
                result = read_language(self._reader, self._base)
            except Exception:
                self._stopped = True
                result = LanguageObservation("read_failed")
            if result == self._previous:
                return
            self._previous = result
            try:
                if self._reports < MAX_REPORTS:
                    self._report(result)
                    self._reports += 1
                else:
                    self._report(LanguageObservation("limit_reached"))
                    self._stopped = True
            except Exception:
                self._stopped = True
        finally:
            self._lock.release()
