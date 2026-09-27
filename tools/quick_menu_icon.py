"""Isolated texture owner for the exact-build developer icon trial.

Importing this module installs no hooks and calls no native functions. The
adapter may call register_once ONLY from the natural quick-menu LoadResources
AFTER callback, with the exact executable guard already satisfied. Supplied
readers must return exact owned bytes (for example, bounded current-process
ReadProcessMemory); native wrappers are void(pointer).

The owner must be pinned for the process lifetime BEFORE either native call.
There is deliberately no destructor, release, retry, late-load or atexit path.
Menu items copy handles without acquiring references; HUD messages acquire
their own reference. A fresh manager/table lookup is still required for every
use. These bounded checks are not a lock against asynchronous native teardown
or proof that the candidate asset was visibly rendered.
"""

import ctypes as C
from dataclasses import dataclass
import threading


LOAD_RESOURCES_RVA = 0x151AD80
TEXTURE_LOAD_RVA = 0xEC0670
HANDLE_RETAIN_RVA = 0x2D5C890
MANAGER_PTR_RVA = 0x6E0D090
RETAIN_MANAGER_PTR_RVA = 0x5901610
COMPANION_ICON_OFFSET = 0xA104
VIRTUAL_PATH = b"TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/SETTINGS.DDS"
RECORD_SIZE = 24
HANDLE_OFFSET = 0x10
MIN_ADDRESS = 0x10000
MAX_ADDRESS = 0x7FFFFFFFFFFF
READ_SIZES = frozenset((1, 4, 8, 16))


class IconError(RuntimeError):
    """A bounded icon observation could not be validated."""


class _ManagerChanged(IconError):
    """An observed manager transition forbids reusing any owned handle."""


def _address(pointer, offset=0, size=1):
    if (type(pointer) is not int or type(offset) is not int
            or type(size) is not int or pointer < MIN_ADDRESS
            or offset < 0 or size < 1
            or pointer + offset > MAX_ADDRESS - size + 1):
        raise IconError("Invalid icon read range")
    return pointer + offset


def _read(reader, pointer, offset, size):
    if size not in READ_SIZES:
        raise IconError("Unsupported icon read size")
    value = reader(_address(pointer, offset, size), size)
    if type(value) is not bytes or len(value) != size:
        raise IconError("Icon read must contain exact owned bytes")
    return value


def _integer(reader, pointer, offset=0, size=4):
    return int.from_bytes(_read(reader, pointer, offset, size), "little")


def _check_manager(reader, manager_slot, expected):
    # Loader/getters and smart-handle retain use two globals. Only use handles
    # while both refer to the same validated native manager object.
    retain_slot = manager_slot + RETAIN_MANAGER_PTR_RVA - MANAGER_PTR_RVA
    if (_integer(reader, manager_slot, size=8) != expected
            or _integer(reader, retain_slot, size=8) != expected):
        raise _ManagerChanged("Resource manager changed or aliases differ")


def _handle(value):
    # Native retain interprets this value as a signed int32 and ignores <= 0.
    return type(value) is int and 0 < value <= 0x7FFFFFFF


def _name(reader, pointer):
    value = bytearray()
    for offset in range(0xC, 0x10C, 16):
        chunk = _read(reader, pointer, offset, 16)
        end = chunk.find(b"\0")
        if end >= 0:
            value.extend(chunk[:end])
            return bytes(value)
        value.extend(chunk)
    raise IconError("Texture name is not terminated within its native buffer")


@dataclass(frozen=True)
class _Resource:
    """Private compare-only identity, never an address to dereference later."""

    pointer: int
    name: bytes
    ready: bool


def _resource(reader, manager_slot, manager, handle):
    """Read one original indexed texture, never a substituted default."""
    if not _handle(handle):
        return None
    _check_manager(reader, manager_slot, manager)
    count = _integer(reader, manager, 0x5C)
    table = _integer(reader, manager, 0x60, 8)
    if handle > count:
        return None
    entry = _address(table, (handle - 1) * 8, 8)
    pointer = _integer(reader, entry, size=8)
    if not pointer:
        return None
    if _integer(reader, pointer, 8) != 7:
        return None
    name = _name(reader, pointer)
    if not name:
        return None
    # +0x139 is not treated as an error: it can be the NoQuery flag. The
    # adjacent +0x13A is the error byte; +0x13B requests default substitution.
    error = _integer(reader, pointer, 0x13A, 1)
    substitute = _integer(reader, pointer, 0x13B, 1)
    image = _integer(reader, pointer, 0x1E0)
    texture = _integer(reader, pointer, 0x260, 8)
    # Recheck table identity and resource fields after the bounded copies.
    _check_manager(reader, manager_slot, manager)
    if (_integer(reader, manager, 0x5C) != count
            or _integer(reader, manager, 0x60, 8) != table
            or _integer(reader, entry, size=8) != pointer
            or _integer(reader, pointer, 8) != 7
            or _name(reader, pointer) != name
            or _integer(reader, pointer, 0x13A, 1) != error
            or _integer(reader, pointer, 0x13B, 1) != substitute
            or _integer(reader, pointer, 0x1E0) != image
            or _integer(reader, pointer, 0x260, 8) != texture):
        raise IconError("Resource changed during observation")
    # Return identity even while loading/error; readiness alone determines use.
    return _Resource(pointer, name, not (error or substitute) and bool(image or texture))


class IconOwner:
    """One registration attempt and at most two process-pinned references.

    pin_owner(self) must return exactly True and retain self independently of
    any Mod instance/toggle. The adapter must reject a second process owner.
    The phase can run on a different native thread from menu/HUD callbacks.
    Concurrent/reentrant calls return without waiting or starting another load.
    No menu pointer is retained or dereferenced after register_once returns.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._attempted = False
        self._pinned = False
        self._disabled = False
        self._manager = None
        self._manager_slot = None
        self._custom = None
        self._paw = None
        self._path = C.create_string_buffer(VIRTUAL_PATH + b"\0")
        self._storage = C.create_string_buffer(RECORD_SIZE + 15)
        self._record_address = (C.addressof(self._storage) + 15) & ~15
        C.c_void_p.from_address(self._record_address).value = C.addressof(self._path)
        self._paw_handle = C.c_uint32(0)
        self.status = "not_observed"

    @property
    def attempted(self):
        return self._attempted

    def _same_manager(self, reader, manager_slot):
        if manager_slot != self._manager_slot:
            self._disabled = True
            self.status = "manager_changed"
            return False
        _check_manager(reader, manager_slot, self._manager)
        return True

    def register_once(self, reader, menu, manager_slot, *, load_texture,
                      retain_handle, pin_owner):
        """Attempt initialization once at the validated natural native phase.

        Returns True when the registration sequence completed, not when the
        image is ready or visible. Failure keeps any possibly acquired buffers
        pinned; a retained and freshly validated paw can still be used.
        """
        if not self._lock.acquire(blocking=False):
            return False
        try:
            if self._attempted:
                return False
            self._attempted = True
            self.status = "registration_started"
            _address(menu, COMPANION_ICON_OFFSET, 4)
            _address(manager_slot, size=8)
            manager = _integer(reader, manager_slot, size=8)
            _address(manager, 0x60, 8)
            _check_manager(reader, manager_slot, manager)
            self._manager = manager
            self._manager_slot = manager_slot
            if pin_owner(self) is not True:
                self.status = "pin_refused"
                return False
            self._pinned = True
            if not self._same_manager(reader, manager_slot):
                return False
            paw_handle = _integer(reader, menu, COMPANION_ICON_OFFSET)
            paw = _resource(reader, manager_slot, manager, paw_handle)
            # Only acquire the native paw when its original texture is already
            # usable. A substituted handle would retain another resource.
            if paw is not None and paw.ready:
                if (_integer(reader, menu, COMPANION_ICON_OFFSET) != paw_handle
                        or not self._same_manager(reader, manager_slot)):
                    raise IconError("Native companion icon changed before retain")
                self._paw_handle.value = paw_handle
                retain_handle(C.addressof(self._paw_handle))
                retained = _resource(reader, manager_slot, manager, paw_handle)
                if retained is None or retained != paw:
                    raise IconError("Native companion icon changed during retain")
                self._paw = paw
            if not self._same_manager(reader, manager_slot):
                return False
            load_texture(self._record_address)
            if not self._same_manager(reader, manager_slot):
                return False
            custom_handle = C.c_uint32.from_address(
                self._record_address + HANDLE_OFFSET).value
            custom = _resource(reader, manager_slot, manager, custom_handle)
            if custom is not None and custom.name == VIRTUAL_PATH:
                self._custom = custom
            self.status = "registered"
            return True
        except _ManagerChanged:
            self._disabled = True
            self.status = "manager_changed"
            return False
        except Exception:
            self.status = "registration_failed"
            return False
        finally:
            self._lock.release()

    def icon_handle(self, reader, manager_slot):
        """Return a freshly vetted owned handle or zero, without native calls."""
        if not self._lock.acquire(blocking=False):
            return 0
        try:
            if not self._pinned or self._disabled or not self._attempted:
                return 0
            if not self._same_manager(reader, manager_slot):
                return 0
            for identity, handle, source in (
                (self._custom, C.c_uint32.from_address(
                    self._record_address + HANDLE_OFFSET).value, "custom_ready"),
                (self._paw, self._paw_handle.value, "native_ready"),
            ):
                if identity is None:
                    continue
                current = _resource(reader, manager_slot, self._manager, handle)
                if (current is None or current.pointer != identity.pointer
                        or current.name != identity.name):
                    # Do not accept a recycled handle even in the same manager.
                    self._disabled = True
                    self.status = "resource_identity_changed"
                    return 0
                if current.ready:
                    if not self._same_manager(reader, manager_slot):
                        return 0
                    self.status = source
                    return handle
            self.status = "waiting_or_unavailable"
            return 0
        except _ManagerChanged:
            self._disabled = True
            self.status = "manager_changed"
            return 0
        except Exception:
            self.status = "read_unavailable"
            return 0
        finally:
            self._lock.release()
