"""Owned-data policy for an inert two-level menu trial; no import-time I/O.

Native construction/append and guard authorization are supplied by the adapter.
No helper writes depth, selection or flags, clears native entries, or retains a
native pointer in a public result. Native lifetime and callback pairing remain
adapter contracts; a successful policy check is not a lifetime proof.
"""

from dataclasses import dataclass

import quick_menu_item as item


ROOT_SLOT = -1
CHILD_SLOT = 0
ROOT_LABEL = item.DEFAULT_LABEL
CHILD_LABEL = "Settings preview"
SETTINGS_CHILD_ROLES = (0, 1, 2, 3, 4, 5)
MenuItemError = item.MenuItemError


@dataclass(frozen=True)
class MenuState:
    """Owned scalars only; vector storage identities are deliberately excluded."""

    depth: int
    root_capacity: int
    root_count: int
    root_selected: int
    companion_capacity: int
    companion_count: int
    companion_selected: int
    child_capacity: int
    child_count: int
    child_selected: int
    parent_index: int | None
    child_ready: bool
    icon: int


@dataclass(frozen=True)
class BuilderResult:
    status: str
    root_added: bool = False
    child_added: bool = False
    child_ready: bool = False
    page_active: bool = False


@dataclass(frozen=True)
class ActivationToken:
    """Capture for the root only; the adapter separately pairs native calls."""

    state: MenuState


def _roles(child_roles):
    if (type(child_roles) is not tuple or any(type(role) is not int for role in child_roles)
            or child_roles not in ((CHILD_SLOT,), SETTINGS_CHILD_ROLES)):
        raise MenuItemError("Unsupported explicit submenu roles")
    return child_roles


def _icons(permitted_icons):
    if permitted_icons is None:
        return ()
    if (type(permitted_icons) is not tuple or len(permitted_icons) > 2
            or any(type(icon) is not int or not 0 <= icon <= 0xFFFFFFFF for icon in permitted_icons)
            or len(set(permitted_icons)) != len(permitted_icons)):
        raise MenuItemError("Unsupported explicit submenu icon handles")
    return permitted_icons


def _candidate(reader, pointer, index, slot, icon, *, permitted_icons=None):
    offset = index * item.ITEM_SIZE
    if (item._action(reader, pointer, index) != 0
            or item._integer(reader, pointer, offset + item.SLOT_OFFSET) != slot
            or item._integer(reader, pointer, offset, signed=False) not in (icon,) + _icons(permitted_icons)
            or item._integer(reader, pointer, offset + item.BINDING_OFFSET) != -1
            or item._copy(reader, pointer, offset + item.MARKER_OFFSET, 16) != item.CUSTOM_ACTION_MARKER):
        raise MenuItemError("Tagged submenu item differs from its role")
    flags = item._copy(reader, pointer, offset + 0x4C, 4)
    if flags[:2] != b"\0\x01":
        raise MenuItemError("Tagged submenu item has unexpected flags")
    if any(item._copy(reader, pointer, offset + item.NAME_OFFSET + chunk, 16) != bytes(16)
           for chunk in range(0, item.NAME_SIZE, 16)):
        raise MenuItemError("Tagged submenu item has an unexpected inline name")


def _snapshot(reader, menu, *, child_roles=(CHILD_SLOT,), permitted_icons=None, _allow_partial=False):
    """Return owned state plus identities usable only inside this call chain."""
    roles = _roles(child_roles)
    _icons(permitted_icons)
    depth = item._integer(reader, menu, item.DEPTH_OFFSET)
    if not 0 <= depth <= 2:
        raise MenuItemError("Unexpected native menu depth")
    if depth not in (1, 2):
        return None
    root = item._vector(reader, menu, 0)
    if not 0 <= root[3] < root[1] or item._action(reader, root[2], root[3]) != 45:
        return None
    companion = item._vector(reader, menu, 1)
    children = item._vector(reader, menu, 2)
    icon = item._integer(reader, menu, item.COMPANION_ICON_OFFSET, signed=False)
    found = []
    for index in range(companion[1]):
        marker = item._copy(reader, companion[2], index * item.ITEM_SIZE + item.MARKER_OFFSET, 16)
        if marker == item.CUSTOM_ACTION_MARKER:
            _candidate(reader, companion[2], index, ROOT_SLOT, icon, permitted_icons=permitted_icons)
            found.append(index)
    if len(found) > 1:
        raise MenuItemError("Multiple submenu parent markers are ambiguous")
    parent = found[0] if found else None
    ready = False
    if parent is not None and companion[3] == parent and children[1]:
        # Never replace/clear a native page. A nonempty vector is reusable only
        # when it already contains our complete explicitly requested page.
        # Prefix validation is private to one checked append transaction.
        if children[1] > len(roles) or (children[1] != len(roles) and not _allow_partial):
            raise MenuItemError("A nonempty native child page must be preserved")
        for index in range(children[1]):
            _candidate(reader, children[2], index, roles[index], icon, permitted_icons=permitted_icons)
        ready = children[1] == len(roles)
    state = MenuState(depth, root[0], root[1], root[3], companion[0], companion[1], companion[3],
                      children[0], children[1], children[3], parent, ready, icon)
    return state, (root, companion, children)


def _same_snapshot(reader, menu, expected, *, child_roles=(CHILD_SLOT,), permitted_icons=None,
                   _allow_partial=False):
    current = _snapshot(reader, menu, child_roles=child_roles, permitted_icons=permitted_icons,
                        _allow_partial=_allow_partial)
    if current != expected:
        raise MenuItemError("Menu changed while preparing the submenu")
    return current


def _append_role(reader, menu, expected, role, constructor, append, guard, *, child_roles=(CHILD_SLOT,),
                 permitted_icons=None, icon_handle=None):
    roles = _roles(child_roles)
    allowed_icons = _icons(permitted_icons)
    state, vectors = expected
    chosen_icon = state.icon if icon_handle is None else icon_handle
    if type(chosen_icon) is not int or chosen_icon not in (state.icon,) + allowed_icons:
        raise MenuItemError("Construction icon was not explicitly permitted")
    options = dict(child_roles=roles, permitted_icons=permitted_icons, _allow_partial=True)
    depth = 1 if role == ROOT_SLOT else 2
    if role == ROOT_SLOT:
        if state.parent_index is not None or state.companion_count >= item.MAX_VECTOR_ITEMS:
            raise MenuItemError("Submenu parent cannot be appended")
        if state.companion_selected == state.companion_count and state.child_count:
            raise MenuItemError("Appending the selected parent would adopt a native child page")
    elif not (state.parent_index is not None and state.companion_selected == state.parent_index
              and state.child_count < len(roles) and role == roles[state.child_count]):
        raise MenuItemError("Native child entries cannot be replaced")
    item._authorize(guard, menu)
    _same_snapshot(reader, menu, expected, **options)
    payload = bytearray(item._construct(constructor, chosen_icon))
    payload[item.SLOT_OFFSET:item.SLOT_OFFSET + 4] = role.to_bytes(4, "little", signed=True)
    item._authorize(guard, menu)
    _same_snapshot(reader, menu, expected, **options)
    header = item._address(menu, item.VECTORS_OFFSET + depth * item.VECTOR_SIZE, item.VECTOR_SIZE)
    try:
        append(header, bytes(payload))
    except Exception:
        raise MenuItemError("Native submenu append failed; outcome is unverified") from None
    # The appended payload is read back through the newly reported native
    # storage. Never dereference the pre-append vector pointer after growth.
    current = _snapshot(reader, menu, **options)
    if current is None:
        raise MenuItemError("Submenu context disappeared after native append")
    after, after_vectors = current
    if (after.depth != state.depth or after.icon != state.icon
            or after_vectors[0] != vectors[0]
            or after.companion_selected != state.companion_selected
            or after.child_selected != state.child_selected):
        raise MenuItemError("Native append changed the submenu context")
    if role == ROOT_SLOT:
        if (after.companion_count != state.companion_count + 1
                or after.parent_index != state.companion_count
                or after_vectors[2] != vectors[2]):
            raise MenuItemError("Native submenu parent append could not be verified")
    elif (after_vectors[1] != vectors[1] or after.child_count != state.child_count + 1):
        raise MenuItemError("Native submenu child append could not be verified")
    return current


def complete_builder(reader, menu, *, constructor, append, guard_capability, child_roles=(CHILD_SLOT,),
                     permitted_icons=None, icon_handle=None):
    """Restore the parent and its exact explicit page, preserving native entries."""
    roles = _roles(child_roles)
    options = dict(child_roles=roles, permitted_icons=permitted_icons)
    append_options = dict(options, icon_handle=icon_handle)
    item._authorize(guard_capability, menu)
    snapshot = _snapshot(reader, menu, **options)
    if snapshot is None:
        return BuilderResult("outside_context")
    root_added = child_added = False
    if snapshot[0].parent_index is None:
        snapshot = _append_role(reader, menu, snapshot, ROOT_SLOT, constructor, append, guard_capability,
                                **append_options)
        root_added = True
    state = snapshot[0]
    while state.companion_selected == state.parent_index and not state.child_ready:
        snapshot = _append_role(reader, menu, snapshot, roles[state.child_count], constructor, append,
                                guard_capability, **append_options)
        child_added = True
        state = snapshot[0]
    return BuilderResult("prepared", root_added, child_added, state.child_ready,
                         state.depth == 2 and state.child_ready)


def selected_label(reader, menu, *, child_roles=(CHILD_SLOT,), permitted_icons=None):
    snapshot = _snapshot(reader, menu, child_roles=child_roles, permitted_icons=permitted_icons)
    if snapshot is None:
        return None
    state = snapshot[0]
    if state.parent_index is None or state.companion_selected != state.parent_index:
        return None
    if state.depth == 1:
        return item.encode_label(ROOT_LABEL)
    if state.child_ready and child_roles == (CHILD_SLOT,) and state.child_selected == 0:
        return item.encode_label(CHILD_LABEL)
    return None


def capture_activation(reader, menu, action, called_as_menu, *, child_roles=(CHILD_SLOT,), permitted_icons=None):
    """Capture only a selected parent activation before the native None call."""
    roles = _roles(child_roles)
    if type(called_as_menu) is not bool:
        raise MenuItemError("Unexpected native menu-call flag")
    if not called_as_menu:
        return None
    if item._integer(reader, action, item.ACTION_OFFSET) != 0:
        return None
    if item._copy(reader, action, item.MARKER_OFFSET, 16) != item.CUSTOM_ACTION_MARKER:
        return None
    slot = item._integer(reader, action, item.SLOT_OFFSET)
    if slot in roles:
        return None  # Child preference changes require a separate intent gate.
    if slot != ROOT_SLOT:
        raise MenuItemError("Unknown marked submenu activation role")
    snapshot = _snapshot(reader, menu, child_roles=roles, permitted_icons=permitted_icons)
    if snapshot is None:
        return None
    state, vectors = snapshot
    if (state.depth != 1 or state.parent_index is None
            or state.companion_selected != state.parent_index or not state.child_ready):
        return None
    selected_address = item._address(vectors[1][2], state.parent_index * item.ITEM_SIZE, item.ITEM_SIZE)
    if selected_address != action:
        return None  # A copied/replayed item is not this native selection.
    return ActivationToken(state)


def validate_activation(reader, menu, token, *, guard_capability, child_roles=(CHILD_SLOT,), permitted_icons=None):
    """Revalidate the current menu after a separately correlated false result.

    No action pointer is accepted or read after native execution. The adapter
    must pair arguments/native thread and preserve the original false result.
    A True result authorizes only the established topology; it performs no
    selection/depth writes and makes no all-thread ownership claim.
    """
    if type(token) is not ActivationToken:
        return False
    item._authorize(guard_capability, menu)
    options = dict(child_roles=child_roles, permitted_icons=permitted_icons)
    snapshot = _snapshot(reader, menu, **options)
    if snapshot is None or snapshot[0] != token.state:
        return False
    state = snapshot[0]
    if (state.depth != 1 or state.parent_index is None
            or state.companion_selected != state.parent_index or not state.child_ready):
        return False
    item._authorize(guard_capability, menu)
    return _snapshot(reader, menu, **options) == snapshot
