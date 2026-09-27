"""Pure recognition for the first settings child; no hooks, I/O or mutations.

The adapter must separately establish a fresh native confirmation, pair the
TriggerAction invocation, require its original false result and consume that
authorization once. A recognized selected item is not proof of user intent.
Preference access and queued updates belong to the production bridge.
"""

from dataclasses import dataclass

import quick_menu_item as item
import quick_menu_submenu as submenu


MenuItemError = item.MenuItemError


@dataclass(frozen=True)
class ChildActivationToken:
    """Owned topology only; no native pointer, preference or input identity."""

    state: submenu.MenuState


def _is_selected_child(state):
    return (type(state) is submenu.MenuState and state.depth == 2
            and state.parent_index is not None
            and state.companion_selected == state.parent_index
            and state.child_ready and state.child_count == 1
            and state.child_selected == 0)


def selected_child_state(reader, menu):
    """Copy the fully marked selected topology for a separate intent gate."""
    snapshot = submenu._snapshot(reader, menu)
    if snapshot is None or not _is_selected_child(snapshot[0]):
        return None
    return snapshot[0]


def capture_activation(reader, menu, action, called_as_menu, expected_state):
    """Match a child BEFORE native execution against the intent-time snapshot."""
    if type(called_as_menu) is not bool:
        raise MenuItemError("Unexpected native menu-call flag")
    if not called_as_menu or not _is_selected_child(expected_state):
        return None
    if (item._integer(reader, action, item.ACTION_OFFSET) != 0
            or item._copy(reader, action, item.MARKER_OFFSET, 16) != item.CUSTOM_ACTION_MARKER):
        return None
    if item._integer(reader, action, item.SLOT_OFFSET) != submenu.CHILD_SLOT:
        return None
    snapshot = submenu._snapshot(reader, menu)
    if snapshot is None or snapshot[0] != expected_state or not _is_selected_child(snapshot[0]):
        return None
    selected_address = item._address(snapshot[1][2][2], 0, item.ITEM_SIZE)
    if action != selected_address:
        return None  # A copied or replayed item is not this native selection.
    submenu._same_snapshot(reader, menu, snapshot)
    return ChildActivationToken(snapshot[0])


def validate_activation(reader, menu, token, *, guard_capability):
    """Revalidate current storage AFTER a separately correlated false result.

    No old action pointer is accepted or dereferenced. Identical rebuilt storage
    can be recognized, but changed topology or an unavailable guard refuses it.
    """
    if type(token) is not ChildActivationToken or not _is_selected_child(token.state):
        return False
    item._authorize(guard_capability, menu)
    snapshot = submenu._snapshot(reader, menu)
    if snapshot is None or snapshot[0] != token.state or not _is_selected_child(snapshot[0]):
        return False
    item._authorize(guard_capability, menu)
    return submenu._snapshot(reader, menu) == snapshot


def selected_label(reader, menu, child_label: bytes):
    """Keep the parent caption and supply only the recognized child's label."""
    snapshot = submenu._snapshot(reader, menu)
    if snapshot is None:
        return None
    state = snapshot[0]
    if state.parent_index is None or state.companion_selected != state.parent_index:
        return None
    if state.depth == 1:
        return item.encode_label(submenu.ROOT_LABEL)
    if not _is_selected_child(state):
        return None
    if type(child_label) is not bytes or not 0 < len(child_label) < 128 or b"\0" in child_label:
        raise MenuItemError("Invalid bounded settings label")
    return child_label
