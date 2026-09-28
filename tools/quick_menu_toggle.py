"""Pure recognition for explicit settings children; no hooks, I/O or mutations.

The adapter must separately establish a fresh native confirmation, pair the
TriggerAction invocation, require its original false result and consume that
authorization once. A recognized selected item is not proof of user intent.
Preference access and queued updates belong to the production bridge.
"""

from dataclasses import dataclass

import quick_menu_item as item
import quick_menu_submenu as submenu


MenuItemError = item.MenuItemError
CHILD_ROLES = submenu.SETTINGS_CHILD_ROLES
SETTING_KEYS = ("enabled", "selection_mode", "prefer_same_biome", "planets", "space_stations", "nexus", "rotate_companions")
SETTING_LABELS = ("Automatic summoning", "Selection", "Random: prefer matching biome",
                  "Planets", "Space stations", "Space Anomaly", "Rotate companions")


def setting_key(role):
    if type(role) is not int or role not in CHILD_ROLES:
        raise MenuItemError("Unknown settings child role")
    return SETTING_KEYS[role]


def preference_label(role, state):
    """Render owned preference state; this does not inspect the native world."""
    setting_key(role)
    label = SETTING_LABELS[role] + ": "
    if state is None:
        return item.encode_label(label + "unavailable")
    if state.stopped:
        return item.encode_label(label + "stopped")
    if role == 1:
        if type(state.desired) is not str or state.desired not in ("last_manual", "random", "by_habitat"):
            raise MenuItemError("Unknown companion selection preference")
        label += ("Last selected" if state.desired == "last_manual" else
                  "Random" if state.desired == "random" else "By habitat")
    else:
        if type(state.desired) is not bool:
            raise MenuItemError("Unexpected boolean preference")
        label += "ON" if state.desired else "OFF"
    if state.pending:
        label += " (pending)"
    elif not state.settings_ok:
        label += " (session only)"
    return item.encode_label(label)


@dataclass(frozen=True)
class ChildActivationToken:
    """Owned topology only; no native pointer, preference or input identity."""

    state: submenu.MenuState


def _is_selected_child(state, child_roles=(submenu.CHILD_SLOT,)):
    roles = submenu._roles(child_roles)
    return (type(state) is submenu.MenuState and state.depth == 2
            and state.parent_index is not None
            and state.companion_selected == state.parent_index
            and state.child_ready and state.child_count == len(roles)
            and 0 <= state.child_selected < len(roles))


def selected_child_state(reader, menu, *, child_roles=(submenu.CHILD_SLOT,), permitted_icons=None):
    """Copy the fully marked selected topology for a separate intent gate."""
    snapshot = submenu._snapshot(reader, menu, child_roles=child_roles, permitted_icons=permitted_icons)
    if snapshot is None or not _is_selected_child(snapshot[0], child_roles):
        return None
    return snapshot[0]


def capture_activation(reader, menu, action, called_as_menu, expected_state, *,
                       child_roles=(submenu.CHILD_SLOT,), permitted_icons=None):
    """Match a child BEFORE native execution against the intent-time snapshot."""
    if type(called_as_menu) is not bool:
        raise MenuItemError("Unexpected native menu-call flag")
    if not called_as_menu or not _is_selected_child(expected_state, child_roles):
        return None
    if (item._integer(reader, action, item.ACTION_OFFSET) != 0
            or item._copy(reader, action, item.MARKER_OFFSET, 16) != item.CUSTOM_ACTION_MARKER):
        return None
    if item._integer(reader, action, item.SLOT_OFFSET) != child_roles[expected_state.child_selected]:
        return None
    options = dict(child_roles=child_roles, permitted_icons=permitted_icons)
    snapshot = submenu._snapshot(reader, menu, **options)
    if snapshot is None or snapshot[0] != expected_state or not _is_selected_child(snapshot[0], child_roles):
        return None
    selected_address = item._address(snapshot[1][2][2], expected_state.child_selected * item.ITEM_SIZE, item.ITEM_SIZE)
    if action != selected_address:
        return None  # A copied or replayed item is not this native selection.
    submenu._same_snapshot(reader, menu, snapshot, **options)
    return ChildActivationToken(snapshot[0])


def validate_activation(reader, menu, token, *, guard_capability, child_roles=(submenu.CHILD_SLOT,),
                        permitted_icons=None):
    """Revalidate current storage AFTER a separately correlated false result.

    No old action pointer is accepted or dereferenced. Identical rebuilt storage
    can be recognized, but changed topology or an unavailable guard refuses it.
    """
    if type(token) is not ChildActivationToken or not _is_selected_child(token.state, child_roles):
        return False
    item._authorize(guard_capability, menu)
    options = dict(child_roles=child_roles, permitted_icons=permitted_icons)
    snapshot = submenu._snapshot(reader, menu, **options)
    if snapshot is None or snapshot[0] != token.state or not _is_selected_child(snapshot[0], child_roles):
        return False
    item._authorize(guard_capability, menu)
    return submenu._snapshot(reader, menu, **options) == snapshot


def selected_label(reader, menu, child_label: bytes, *, child_roles=(submenu.CHILD_SLOT,), permitted_icons=None):
    """Keep the parent caption and supply only the recognized child's label."""
    snapshot = submenu._snapshot(reader, menu, child_roles=child_roles, permitted_icons=permitted_icons)
    if snapshot is None:
        return None
    state = snapshot[0]
    if state.parent_index is None or state.companion_selected != state.parent_index:
        return None
    if state.depth == 1:
        return item.encode_label(submenu.ROOT_LABEL)
    if not _is_selected_child(state, child_roles):
        return None
    if type(child_label) is not bytes or not 0 < len(child_label) < 128 or b"\0" in child_label:
        raise MenuItemError("Invalid bounded settings label")
    return child_label
