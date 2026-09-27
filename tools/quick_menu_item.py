"""Offline-testable candidate item policy; no hooks or native API bindings.

All reads and constructor/append operations are supplied by the caller. These
helpers do not establish a safe native mutation interval or binding protection.
A live adapter must establish those separately, keep its guard installed for
the entire item lifetime, and bridge constructor/append through aligned native
buffers. No Python-owned buffer may replace a game's vector allocation.
"""

from dataclasses import dataclass
from enum import Enum


DEPTH_OFFSET = 0xA050
VECTORS_OFFSET = 0xA058
SELECTIONS_OFFSET = 0xA088
COMPANION_ICON_OFFSET = 0xA104
VECTOR_SIZE = 16
ITEM_SIZE = 224
ACTION_OFFSET = 4
MARKER_OFFSET = 0x88
NAME_OFFSET = 0x98
NAME_SIZE = 64
SLOT_OFFSET = 0x84
BINDING_OFFSET = 0xD8
MAX_VECTOR_ITEMS = 256  # Diagnostic ceiling, never a changed gameplay limit.
MIN_USER_ADDRESS = 0x10000
MAX_USER_ADDRESS = 0x7FFFFFFFFFFF
CUSTOM_ACTION_MARKER = b"CAS_MENU_V1\xA7\x19\x5C\xE3\x42"
DEFAULT_LABEL = "Companion Auto Summon"
READ_SIZES = frozenset({4, VECTOR_SIZE})


class MenuItemError(RuntimeError):
    """A candidate could not be inspected or constructed without ambiguity."""


class AppendStatus(Enum):
    READY = "ready"
    APPENDED = "appended"
    ALREADY_PRESENT = "already_present"
    NOT_COMPANION_CONTEXT = "not_companion_context"


@dataclass(frozen=True)
class MenuInspection:
    """Sanitized observation; deliberately excludes native pointer identities."""

    depth: int
    capacity: int
    count: int
    selected_index: int
    selected_action: int | None
    parent_action: int | None
    custom_indices: tuple[int, ...]


def _address(pointer, offset, size):
    if type(pointer) is not int or type(offset) is not int or type(size) is not int:
        raise MenuItemError("Invalid menu range type")
    if pointer < MIN_USER_ADDRESS or offset < 0 or size <= 0:
        raise MenuItemError("Invalid menu range")
    address = pointer + offset
    if address > MAX_USER_ADDRESS - size + 1:
        raise MenuItemError("Menu range exceeds user address space")
    return address


def _copy(reader, pointer, offset, size):
    if size not in READ_SIZES:
        raise MenuItemError("Unsupported menu copy size")
    address = _address(pointer, offset, size)
    try:
        data = reader(address, size)
    except Exception:
        raise MenuItemError("Menu data could not be copied") from None
    if type(data) is not bytes or len(data) != size:
        raise MenuItemError("Menu copy must contain exact owned bytes")
    return data


def _integer(reader, pointer, offset, *, signed=True):
    return int.from_bytes(_copy(reader, pointer, offset, 4), "little", signed=signed)


def _vector(reader, menu, depth):
    header = _copy(reader, menu, VECTORS_OFFSET + depth * VECTOR_SIZE, VECTOR_SIZE)
    capacity = int.from_bytes(header[:4], "little")
    count = int.from_bytes(header[4:8], "little")
    pointer = int.from_bytes(header[8:], "little")
    if count > capacity or capacity > MAX_VECTOR_ITEMS:
        raise MenuItemError("Menu vector exceeds diagnostic bounds")
    if capacity:
        # Appending into spare capacity uses this allocation even when count
        # is zero. Validate its range without reading uninitialized entries.
        _address(pointer, 0, capacity * ITEM_SIZE)
    selected = _integer(reader, menu, SELECTIONS_OFFSET + depth * 4)
    return capacity, count, pointer, selected


def _action(reader, pointer, index):
    action = _integer(reader, pointer, index * ITEM_SIZE + ACTION_OFFSET)
    if not 0 <= action <= 66:
        raise MenuItemError("Unexpected native action value")
    return action


def _inspect(reader, menu):
    depth = _integer(reader, menu, DEPTH_OFFSET)
    if not 0 <= depth <= 2:
        raise MenuItemError("Unexpected menu depth")
    current = _vector(reader, menu, depth)
    capacity, count, pointer, selected = current
    selected_action = None
    if 0 <= selected < count:
        selected_action = _action(reader, pointer, selected)
    parent_action = None
    parent = None
    if depth:
        parent = _vector(reader, menu, depth - 1)
        _, parent_count, parent_pointer, parent_selected = parent
        if 0 <= parent_selected < parent_count:
            parent_action = _action(reader, parent_pointer, parent_selected)
    custom_indices = []
    # Only the direct companion submenu is eligible. Other contexts never
    # trigger a marker scan or the constructor/append path.
    if depth == 1 and parent_action == 45:
        for index in range(count):
            marker = _copy(reader, pointer, index * ITEM_SIZE + MARKER_OFFSET, 16)
            if marker == CUSTOM_ACTION_MARKER:
                if _action(reader, pointer, index) != 0:
                    raise MenuItemError("Candidate marker is attached to a non-inert action")
                custom_indices.append(index)
        if len(custom_indices) > 1:
            raise MenuItemError("Multiple candidate markers make the menu ambiguous")
    public = MenuInspection(depth, capacity, count, selected, selected_action,
                            parent_action, tuple(custom_indices))
    # Native identities never leave these private, short-lived call frames.
    return public, (depth, current, parent)


def inspect_menu(reader, menu):
    return _inspect(reader, menu)[0]


def _status(view):
    if view.depth != 1 or view.parent_action != 45:
        return AppendStatus.NOT_COMPANION_CONTEXT
    if view.custom_indices:
        return AppendStatus.ALREADY_PRESENT
    if view.count >= MAX_VECTOR_ITEMS:
        raise MenuItemError("Appending would exceed the diagnostic item ceiling")
    return AppendStatus.READY


def plan_append(reader, menu):
    """Plan only; this does not authorize or invoke any mutation callback."""
    return _status(inspect_menu(reader, menu))


def encode_label(label):
    """Return a nonempty ASCII label without its adapter-supplied terminator."""
    if type(label) is not str or not label or "\0" in label:
        raise MenuItemError("Candidate label must be nonempty text without NUL")
    try:
        result = label.encode("ascii")
    except UnicodeEncodeError:
        raise MenuItemError("Candidate label must be ASCII") from None
    if len(result) > 127:
        raise MenuItemError("Candidate label exceeds its bounded output")
    return result


def selected_label(reader, menu, *, label=DEFAULT_LABEL):
    """Supply text only for the unique tagged None item in the direct submenu.

    No output pointer is accepted and no native label buffer is written here.
    A future adapter must append NUL and bound its own native write to 128 bytes.
    """
    encoded = encode_label(label)
    view = inspect_menu(reader, menu)
    if (view.depth == 1 and view.parent_action == 45 and view.selected_action == 0
            and view.custom_indices == (view.selected_index,)):
        return encoded
    return None


def _authorize(guard_capability, menu):
    try:
        authorize = getattr(guard_capability, "authorize_append", None)
        allowed = callable(authorize) and authorize(menu) is True
    except Exception:
        allowed = False
    if not allowed:
        raise MenuItemError("An explicit active verified append guard is required")


def _construct(constructor, icon):
    owned = bytearray(ITEM_SIZE)
    try:
        # Adapter contract: initialize this owned buffer using the exact native
        # constructor and an aligned temporary, then copy its bytes back here.
        constructor(owned, icon, 0, False, True)
    except Exception:
        raise MenuItemError("Candidate construction failed") from None
    if len(owned) != ITEM_SIZE:
        raise MenuItemError("Constructor changed the owned item size")
    if (int.from_bytes(owned[:4], "little") != icon
            or int.from_bytes(owned[ACTION_OFFSET:ACTION_OFFSET + 4], "little") != 0
            or owned[0x4C] != 0 or owned[0x4D] != 1
            or owned[SLOT_OFFSET:SLOT_OFFSET + 4] != b"\xff" * 4
            or owned[BINDING_OFFSET:BINDING_OFFSET + 4] != b"\xff" * 4
            or owned[MARKER_OFFSET:MARKER_OFFSET + 16] != bytes(16)):
        raise MenuItemError("Constructor output differs from the candidate contract")
    name = encode_label(DEFAULT_LABEL)
    if len(name) >= NAME_SIZE or len(CUSTOM_ACTION_MARKER) != 16:
        raise MenuItemError("Candidate identity or inline name exceeds its field")
    owned[MARKER_OFFSET:MARKER_OFFSET + 16] = CUSTOM_ACTION_MARKER
    owned[NAME_OFFSET:NAME_OFFSET + NAME_SIZE] = name + bytes(NAME_SIZE - len(name))
    return bytes(owned)


def append_inert_item(reader, menu, *, constructor, append, guard_capability=None):
    """Request one native append under a separately verified live guard.

    The capability must authorize this menu twice and remain valid beyond this
    call while a candidate item can exist. A True response is the adapter's
    assertion, not a safety proof supplied by this module. The append adapter
    receives the current native header address and immutable item bytes. It
    must use the native allocator/copy path, never replace the vector pointer
    with a Python-owned buffer. APPENDED means the injected callback returned;
    this helper does not prove native visibility, navigation or binding safety.
    """
    _address(menu, DEPTH_OFFSET, 4)
    _authorize(guard_capability, menu)
    initial, identity = _inspect(reader, menu)
    status = _status(initial)
    if status is not AppendStatus.READY:
        return status
    icon = _integer(reader, menu, COMPANION_ICON_OFFSET, signed=False)
    item = _construct(constructor, icon)
    _authorize(guard_capability, menu)
    current, current_identity = _inspect(reader, menu)
    current_status = _status(current)
    if current_status is AppendStatus.ALREADY_PRESENT:
        return current_status
    if current_status is not AppendStatus.READY or current != initial or current_identity != identity:
        raise MenuItemError("Menu changed while preparing the candidate")
    if _integer(reader, menu, COMPANION_ICON_OFFSET, signed=False) != icon:
        raise MenuItemError("Borrowed companion icon changed during preparation")
    try:
        append(_address(menu, VECTORS_OFFSET + VECTOR_SIZE, VECTOR_SIZE), item)
    except Exception:
        # A native append may have had side effects before an adapter failure.
        # Never retry or attempt Python rollback of native vector storage here.
        raise MenuItemError("Native append callback failed; outcome is unverified") from None
    return AppendStatus.APPENDED
