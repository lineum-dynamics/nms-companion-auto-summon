"""Pure policy for appending the CAS parent before native pet construction.

The adapter supplies a current native builder context and an original append
trampoline. This module performs no I/O, hooks, scalar writes or allocation on
its own. Reading menu depth/selection establishes scope; neither is changed.
"""

import quick_menu_item as item
import quick_menu_submenu as submenu


PET_ACTIONS = frozenset((46, 47))
MenuItemError = item.MenuItemError


def _source_copy(reader, incoming):
    item._address(incoming, 0, item.ITEM_SIZE)
    return b"".join(item._copy(reader, incoming, offset, 16)
                    for offset in range(0, item.ITEM_SIZE, 16))


def _independent_source(incoming, snapshot):
    """Reject overlap with allocated storage, including unused capacity."""
    start = item._address(incoming, 0, item.ITEM_SIZE)
    end = start + item.ITEM_SIZE
    for capacity, _count, pointer, _selected in snapshot[1]:
        if capacity:
            allocation = item._address(pointer, 0, capacity * item.ITEM_SIZE)
            if start < allocation + capacity * item.ITEM_SIZE and allocation < end:
                raise MenuItemError("Incoming native item overlaps menu vector storage")


def _first_pet(reader, snapshot):
    state, vectors = snapshot
    if state.parent_index is not None:
        raise MenuItemError("The submenu parent appeared during insertion")
    companion = vectors[1]
    if any(item._action(reader, companion[2], index) in PET_ACTIONS
           for index in range(companion[1])):
        raise MenuItemError("Native pet entries already precede the missing parent")


def append_before_pet(reader, menu, incoming, *, constructor, append, guard_capability,
                      child_roles=(0,), permitted_icons=None, icon_handle=None):
    """Append one parent before an eligible original pet append, or do nothing.

    The incoming native item must be independent of every current vector
    allocation. The adapter must append that original item only after this
    helper returns, using the unchanged incoming pointer. A True result means
    the CAS parent was appended and verified; it does not append the native
    item or establish native thread/lifetime ownership by itself.
    """
    action = item._action(reader, incoming, 0)
    if action not in PET_ACTIONS:
        return False
    options = {"child_roles": child_roles, "permitted_icons": permitted_icons}
    snapshot = submenu._snapshot(reader, menu, **options)
    if snapshot is None or snapshot[0].parent_index is not None:
        return False
    _independent_source(incoming, snapshot)
    _first_pet(reader, snapshot)
    original = _source_copy(reader, incoming)
    if int.from_bytes(original[item.ACTION_OFFSET:item.ACTION_OFFSET + 4], "little") != action:
        raise MenuItemError("Incoming native action changed during inspection")
    submenu._same_snapshot(reader, menu, snapshot, **options)

    def checked_append(header, data):
        expected_header = menu + item.VECTORS_OFFSET + item.VECTOR_SIZE
        if header != expected_header:
            raise MenuItemError("Ordering may append only to the companion vector")
        current = submenu._same_snapshot(reader, menu, snapshot, **options)
        _independent_source(incoming, current)
        _first_pet(reader, current)
        if _source_copy(reader, incoming) != original:
            raise MenuItemError("Incoming native item changed before insertion")
        # Source-copy callbacks can fail, revoke authorization, or expose a
        # changed vector. Recheck after those reads and authorize last.
        submenu._same_snapshot(reader, menu, snapshot, **options)
        item._authorize(guard_capability, menu)
        append(header, data)

    submenu._append_role(reader, menu, snapshot, submenu.ROOT_SLOT,
                         constructor, checked_append, guard_capability,
                         icon_handle=icon_handle, **options)
    if _source_copy(reader, incoming) != original:
        raise MenuItemError("Incoming native item changed during insertion; outcome is unverified")
    return True
