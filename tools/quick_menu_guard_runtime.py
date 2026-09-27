"""Explicit, process-pinned adapter for the experimental native menu guard.

Importing defines helpers only. Call ensure_guard explicitly from an approved
injected trial. There is deliberately no unload, close, free, or retry endpoint.
Authorization verifies our installation, not game object ownership or every
native binding path. The leaf filter still requires its audited caller lifetime.
"""

import ctypes as C
from dataclasses import dataclass, field
import hashlib
from importlib.metadata import version
import os
from pathlib import Path
import struct
import sys
from threading import Lock

from quick_menu_native_guard import BIND_QUERY_RETURN_RVA, GET_BUTTON_RVA, build_filter


EXPECTED_EXE_SHA256 = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"
REGISTRY_NAME = "_companion_auto_summon_native_menu_guard_v1"
SCHEMA = "cas-native-menu-guard-1"
PREFIX_SIZE = 16
TRAMPOLINE_SIZE = 19  # Verified five-byte stolen instruction plus absolute jump.
ALLOCATION_SIZE = 4096
MAX_USER_ADDRESS = 0x7FFFFFFFFFFF


class GuardError(RuntimeError):
    """A sanitized refusal; it contains no native memory or pointer value."""


def _range(address, size):
    if (type(address) is not int or type(size) is not int or size <= 0
            or address < 0x10000 or address > MAX_USER_ADDRESS - size + 1):
        raise GuardError("Invalid native range")
    return address


def _path(value):
    return os.path.normcase(os.path.realpath(os.fspath(value)))


def _read_at(binary, offset, size):
    if offset < 0 or size < 1 or size > 4096:
        raise GuardError("Unsupported executable range")
    binary.seek(offset)
    value = binary.read(size)
    if len(value) != size:
        raise GuardError("Truncated executable data")
    return value


def _pe_prefix(binary, rva, size=PREFIX_SIZE):
    """Map one executable PE32+ section without external PE dependencies."""
    dos = _read_at(binary, 0, 64)
    if dos[:2] != b"MZ":
        raise GuardError("Unsupported executable header")
    pe_offset = struct.unpack_from("<I", dos, 0x3C)[0]
    if not 64 <= pe_offset <= 0x100000:
        raise GuardError("Unsupported executable header offset")
    coff = _read_at(binary, pe_offset, 24)
    machine, sections = struct.unpack_from("<HH", coff, 4)
    optional_size = struct.unpack_from("<H", coff, 20)[0]
    if (coff[:4] != b"PE\0\0" or machine != 0x8664
            or not 1 <= sections <= 96 or not 112 <= optional_size <= 4096):
        raise GuardError("Unsupported executable format")
    optional = _read_at(binary, pe_offset + 24, optional_size)
    if optional[:2] != b"\x0b\x02":
        raise GuardError("Expected a 64-bit executable")
    matches = []
    for index in range(sections):
        header = _read_at(binary, pe_offset + 24 + optional_size + index * 40, 40)
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", header, 8)
        characteristics = struct.unpack_from("<I", header, 36)[0]
        displacement = rva - virtual_address
        if 0 <= displacement and displacement + size <= max(virtual_size, raw_size):
            if displacement + size > raw_size or not characteristics & 0x20000000:
                raise GuardError("Target is not backed by executable file bytes")
            matches.append(raw_offset + displacement)
    if len(matches) != 1:
        raise GuardError("Target does not have one executable section")
    return _read_at(binary, matches[0], size)


def _load_prefix(binary_path):
    with Path(binary_path).open("rb") as binary:
        if hashlib.file_digest(binary, "sha256").hexdigest() != EXPECTED_EXE_SHA256:
            raise GuardError("Unsupported executable build")
        return _pe_prefix(binary, GET_BUTTON_RVA)


@dataclass(frozen=True)
class _Context:
    base: int
    binary_path: str
    pid: int
    prefix: bytes = field(repr=False)

    @property
    def identity(self):
        return self.pid, self.base, self.binary_path


class _MemoryInformation(C.Structure):
    _fields_ = [("BaseAddress", C.c_void_p), ("AllocationBase", C.c_void_p),
                ("AllocationProtect", C.c_uint32), ("PartitionId", C.c_uint16),
                ("RegionSize", C.c_size_t), ("State", C.c_uint32),
                ("Protect", C.c_uint32), ("Type", C.c_uint32)]


class _WindowsBackend:
    """Only created by the explicit entry point after the framework guard."""

    def __init__(self):
        self.kernel = C.WinDLL("kernel32", use_last_error=True)
        for name, result, arguments in (
            ("GetCurrentProcess", C.c_void_p, []),
            ("GetCurrentProcessId", C.c_uint32, []),
            ("GetModuleHandleW", C.c_void_p, [C.c_wchar_p]),
            ("GetModuleFileNameW", C.c_uint32, [C.c_void_p, C.c_wchar_p, C.c_uint32]),
            ("ReadProcessMemory", C.c_int, [C.c_void_p, C.c_void_p, C.c_void_p,
                                          C.c_size_t, C.POINTER(C.c_size_t)]),
            ("VirtualAlloc", C.c_void_p, [C.c_void_p, C.c_size_t, C.c_uint32, C.c_uint32]),
            ("VirtualProtect", C.c_int, [C.c_void_p, C.c_size_t, C.c_uint32,
                                       C.POINTER(C.c_uint32)]),
            ("VirtualQuery", C.c_size_t, [C.c_void_p, C.POINTER(_MemoryInformation), C.c_size_t]),
            ("FlushInstructionCache", C.c_int, [C.c_void_p, C.c_void_p, C.c_size_t]),
        ):
            function = getattr(self.kernel, name)
            function.restype, function.argtypes = result, arguments
        self.process = self.kernel.GetCurrentProcess()

    def identity(self):
        buffer = C.create_unicode_buffer(32768)
        length = self.kernel.GetModuleFileNameW(None, buffer, len(buffer))
        if not 0 < length < len(buffer):
            raise GuardError("Cannot identify the current executable")
        return (self.kernel.GetCurrentProcessId(), self.kernel.GetModuleHandleW(None),
                _path(buffer.value))

    def read(self, address, size):
        _range(address, size)
        if size > ALLOCATION_SIZE:
            raise GuardError("Native validation read exceeds its budget")
        value, copied = C.create_string_buffer(size), C.c_size_t()
        if not self.kernel.ReadProcessMemory(self.process, address, value, size, C.byref(copied)):
            raise GuardError("Cannot copy native validation data")
        if copied.value != size:
            raise GuardError("Incomplete native validation copy")
        return value.raw

    def allocate(self):
        address = self.kernel.VirtualAlloc(None, ALLOCATION_SIZE, 0x3000, 0x04)
        return _range(address, ALLOCATION_SIZE)

    def write_code(self, address, code):
        if not isinstance(code, bytes) or not 0 < len(code) <= ALLOCATION_SIZE:
            raise GuardError("Invalid filter code size")
        _range(address, ALLOCATION_SIZE)
        old = C.c_uint32()
        if not self.kernel.VirtualProtect(address, ALLOCATION_SIZE, 0x04, C.byref(old)):
            raise GuardError("Cannot prepare filter memory")
        C.memmove(address, code, len(code))
        if not self.kernel.VirtualProtect(address, ALLOCATION_SIZE, 0x20, C.byref(old)):
            raise GuardError("Cannot protect filter memory")
        if not self.kernel.FlushInstructionCache(self.process, address, len(code)):
            raise GuardError("Cannot publish filter instructions")

    def is_rx(self, address, size):
        _range(address, size)
        info = _MemoryInformation()
        if self.kernel.VirtualQuery(address, C.byref(info), C.sizeof(info)) != C.sizeof(info):
            return False
        return (info.State == 0x1000 and info.Protect == 0x20
                and info.AllocationBase == address and info.BaseAddress <= address
                and address + size <= info.BaseAddress + info.RegionSize)

    def create_hook(self, target, detour):
        import cyminhook
        signature = C.CFUNCTYPE(C.c_bool, C.c_void_p, C.c_int32, C.c_int32, C.c_bool)
        return cyminhook.MinHook(signature=signature, target=target, detour=detour)

    def original(self, hook):
        return _range(C.cast(hook.original, C.c_void_p).value, TRAMPOLINE_SIZE)


def _real_context(base, binary_path):
    """No backend injection parameter can bypass this public-entry guard."""
    if sys.platform != "win32" or C.sizeof(C.c_void_p) != 8:
        raise GuardError("The guard requires Windows x64")
    _range(base, GET_BUTTON_RVA + PREFIX_SIZE)
    normalized = _path(binary_path)
    if Path(normalized).name.casefold() != "nms.exe":
        raise GuardError("The guard requires the game executable")
    if version("pymhf") != "0.2.4" or version("cyminhook") != "0.1.6":
        raise GuardError("Unsupported native framework versions")
    from pymhf.core import _internal
    if (not _internal.IS_INJECTED or _internal.BASE_ADDRESS != base
            or _path(_internal.BINARY_PATH) != normalized):
        raise GuardError("The guard requires the matching injected context")
    backend = _WindowsBackend()
    pid, current_base, current_path = backend.identity()
    if current_base != base or current_path != normalized or pid <= 0:
        raise GuardError("The current process does not match the game context")
    return _Context(base, normalized, pid, _load_prefix(normalized)), backend


class _Guard:
    def __init__(self, context, backend, registry, registry_provider):
        self.schema = SCHEMA
        self.context, self.backend = context, backend
        self.registry, self.registry_provider = registry, registry_provider
        self.lock = Lock()
        self.state = "installing"
        self.phase = "identity"
        self.allocation = self.hook = self.original_address = None
        self.code = self.target_prefix = self.relay_bytes = self.original_bytes = None
        self.relay_address = None

    @property
    def active(self):
        return self.state == "active"

    def _owned(self):
        if (self.state == "failed" or self.registry_provider() is not self.registry
                or self.registry.get("guard") is not self):
            raise GuardError("Native guard ownership is unavailable")

    def _read(self, address, size):
        self._owned()
        result = self.backend.read(_range(address, size), size)
        self._owned()
        if not isinstance(result, bytes) or len(result) != size:
            raise GuardError("Native validation needs exact owned bytes")
        return result

    def _identity(self):
        self._owned()
        identity = self.backend.identity()
        self._owned()
        if identity != self.context.identity:
            raise GuardError("Native guard process identity changed")

    def _code_valid(self):
        self._owned()
        protected = self.backend.is_rx(self.allocation, len(self.code))
        self._owned()
        if not protected or self._read(self.allocation, len(self.code)) != self.code:
            raise GuardError("Native filter integrity changed")

    def _verify(self):
        self._identity()
        self._code_valid()
        if (self._read(self.context.base + GET_BUTTON_RVA, PREFIX_SIZE) != self.target_prefix
                or self._read(self.relay_address, len(self.relay_bytes)) != self.relay_bytes
                or self._read(self.original_address, len(self.original_bytes)) != self.original_bytes):
            raise GuardError("Native hook integrity changed")
        self._owned()

    def _install(self):
        self._identity()
        self.phase = "original target"
        target = self.context.base + GET_BUTTON_RVA
        if self._read(target, PREFIX_SIZE) != self.context.prefix:
            raise GuardError("Native target differs from the supported executable")
        self.phase = "allocation"
        self.allocation = self.backend.allocate()
        self._owned()
        self.phase = "initial filter"
        self.code = build_filter(self.context.base + BIND_QUERY_RETURN_RVA, target)
        self.backend.write_code(self.allocation, self.code)
        self._code_valid()
        # The registry already owns this object and any subsequently obtained
        # allocation/hook. Even a failed installation is never retried/freed.
        self.phase = "hook creation"
        self.hook = self.backend.create_hook(target, self.allocation)
        self._owned()
        self.phase = "trampoline validation"
        self.original_address = self.backend.original(self.hook)
        self.original_bytes = self._read(self.original_address, TRAMPOLINE_SIZE)
        expected_original = (self.context.prefix[:5] + b"\xff\x25\0\0\0\0"
                             + struct.pack("<Q", target + 5))
        if self.original_bytes != expected_original:
            raise GuardError("Unsupported native trampoline layout")
        self.phase = "final filter"
        self.code = build_filter(self.context.base + BIND_QUERY_RETURN_RVA, self.original_address)
        self.backend.write_code(self.allocation, self.code)
        self._code_valid()
        self.phase = "activation context"
        self._identity()
        if self._read(target, PREFIX_SIZE) != self.context.prefix:
            raise GuardError("Native target changed before activation")
        self.phase = "hook activation"
        self.hook.enable()
        self._owned()
        self.phase = "installed relay"
        prefix = self._read(target, PREFIX_SIZE)
        if prefix[:1] != b"\xe9" or prefix[5:] != self.context.prefix[5:]:
            raise GuardError("Unsupported installed hook layout")
        self.relay_address = _range(target + 5 + struct.unpack_from("<i", prefix, 1)[0], 14)
        self.relay_bytes = b"\xff\x25\0\0\0\0" + struct.pack("<Q", self.allocation)
        if self._read(self.relay_address, 14) != self.relay_bytes:
            raise GuardError("Installed relay does not reach this filter")
        self.target_prefix = prefix
        self.phase = "installed integrity"
        self._verify()
        self._owned()
        self.state = "active"

    def authorize_append(self, menu):
        """Validate installation for this fresh callback pointer; retain no menu."""
        if not self.active:
            return False
        if not self.lock.acquire(blocking=False):
            self.state = "failed"
            return False
        try:
            _range(menu, 0xA094)
            self._verify()
            return self.active
        except Exception:
            self.state = "failed"
            return False
        finally:
            self.lock.release()

    def _reuse(self, context):
        if (self.schema != SCHEMA or self.context.identity != context.identity
                or self.context.prefix != context.prefix or not self.active):
            raise GuardError("A different or failed native guard is already pinned")
        if not self.lock.acquire(blocking=False):
            raise GuardError("Native guard validation is busy")
        try:
            self._verify()
        except GuardError as error:
            self.state = "failed"
            raise error from None
        except Exception:
            self.state = "failed"
            raise GuardError("Pinned native guard validation failed") from None
        finally:
            self.lock.release()
        return self


def _ensure_with_backend(context, backend, registry, registry_provider):
    """Private fake-backend seam; it is never exposed by ensure_guard."""
    if not isinstance(registry, dict) or registry.get("schema") != SCHEMA:
        raise GuardError("Unsupported native guard registry")
    lock = registry.get("lock")
    if lock is None or not lock.acquire(blocking=False):
        raise GuardError("Native guard setup is busy")
    try:
        existing = registry.get("guard")
        if existing is not None:
            if getattr(existing, "schema", None) != SCHEMA:
                raise GuardError("An incompatible native guard is already pinned")
            if not existing.active:
                raise GuardError("A failed native guard remains pinned; retry is refused")
            if existing.code != build_filter(context.base + BIND_QUERY_RETURN_RVA, existing.original_address):
                raise GuardError("The pinned filter differs from this adapter")
            return existing._reuse(context)
        guard = _Guard(context, backend, registry, registry_provider)
        registry["guard"] = guard
        try:
            guard._install()
        except GuardError as error:
            guard.state = "failed"
            raise GuardError(f"Native guard refused during {guard.phase}: {error}") from None
        except Exception:
            guard.state = "failed"
            raise GuardError(f"Native guard refused during {guard.phase}; resources remain pinned") from None
        return guard
    finally:
        lock.release()


def ensure_guard(base, binary_path):
    """Validate the real game context, then install once or reuse its pinned guard."""
    try:
        context, backend = _real_context(base, binary_path)
        registry = sys.__dict__.setdefault(REGISTRY_NAME, {"schema": SCHEMA, "lock": Lock()})
        return _ensure_with_backend(context, backend, registry,
                                    lambda: sys.__dict__.get(REGISTRY_NAME))
    except GuardError:
        raise
    except Exception:
        raise GuardError("The real native guard context could not be validated") from None
