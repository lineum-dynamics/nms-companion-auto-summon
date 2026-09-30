# Teleport arrival and grouped companion menu

Status: updated 30 September 2026 against the published 0.10.1-native-test
candidate and the exact Steam Cosmos 7.05 executable. The published archive is
unchanged. Teleport summoning remains unimplemented because no successful local
teleporter-completion callback has been verified. The current menu candidate
has passed one owner-confirmed grouped-roster visibility smoke test; broader
menu lifecycle acceptance remains open.

## Owner reports

- A pet does not automatically appear after teleport arrival.
- With a large owned roster, the game groups companions in its menu and the
  Companion Auto Summon settings page is no longer visible.
- In the current 0.10.1 candidate, the owner later confirmed that the settings
  entry remained visible beside a grouped roster. This supersedes the earlier
  single report of a missing entry for that observed menu state, but it does
  not establish behavior for every roster or menu rebuild.
- One direct load into the Anomaly had no visible pet while an Anomaly mission
  was incomplete. The owner has not established that the mission state caused
  the missing pet; this is separate from a confirmed teleporter-arrival test.
- The owner reports that after dying, the settings menu was missing and no pet
  appeared. The current runtime has no death/respawn opportunity trigger, so
  no automatic summon is expected from death alone. The same session recorded
  `menu_unexpected_thread`; the timing is consistent with a UI-thread change,
  but the log has no death event and does not prove the cause.

These are separate problems: the first needs a trustworthy local-arrival event;
the second needs a menu adapter that tolerates native menu variants.

## Verified source constraints

- `native/src/bootstrap.cpp` currently hooks successful local save-load
  completion and ship exit as opportunity sources. Its twelve-hook table has no
  verified teleport-completion hook.
- `native/src/runtime.cpp` only records a local load opportunity after a
  successful non-network load. Ship exit arms through `afterExit`. Teleport
  arrival does not arm the current policy.
- The current upstream `NMS.py` function-signature dataset lists 373 functions.
  Its seven names matching teleport, portal, or warp refer to spaceship/system
  warp and portal-rune UI behavior; none identifies a successful base, station,
  or Anomaly teleporter-arrival callback. System warp is not a substitute for
  teleport arrival. Source checked on 30 September 2026:
  <https://raw.githubusercontent.com/monkeyman192/NMS.py/master/tools/data.json>.
- The exact executable's CodeView record names an internal `nms.pdb`, but no
  matching PDB is installed beside the game and the Microsoft symbol server
  returned 404 for its recorded GUID/age. The binary remains available for
  read-only static analysis; no teleport hook has been inferred from a position
  jump or generic warp function.
- `native/src/menu.cpp` recognizes the companion category through native action
  45, looks for pet append actions 46/47, and rejects insertion if those actions
  are already in the vector. A child settings page is limited to depth two and
  exactly seven rows; row roles are the rows' numeric indices.
- The grouped-roster screenshot from the current candidate shows the settings
  entry visible with grouped native rows. A new offline menu fixture also checks
  that 28 opaque native rows are preserved and the settings page can be opened
  after them. The fixture does not claim those synthetic actions are the game's
  exact group action IDs.
- The published adapter pins its first accepted callback thread. A later thread
  change logs `menu_unexpected_thread` and permanently stops menu handling. A
  local test change now skips an out-of-transaction callback on another thread,
  then permits rebinding only at a quiescent builder start. A thread change
  during a builder, append, confirmation or trigger transaction still fails
  closed. Offline fixtures verify both safe recovery and in-flight refusal;
  this does not establish the exact game callback order or live fix.
- Retained logs establish the thread-change guard as one stop reason. They do
  not establish that grouped companions caused the thread change or that this
  was the only reason the settings page was absent.

These checks are intentional safety boundaries. Do not remove them or accept an
unknown menu layout as a workaround.

## Design direction

Treat teleport arrival as an independent opportunity setting, separate from the
existing supported-location toggles. The proposed control is **Summon after
teleport**, under the existing native settings page. A qualifying event must be
successful completion for the local player, not merely a changed location,
position, menu state, or network-client update. The existing global automation
switch, destination-location preferences, native ownership/eligibility checks,
placement checks, pending-request cancellation rules, and retry behavior still
apply. Default the new option ON for fresh installs and existing preference
files when upgrading, so existing players receive the new capability. Preserve
all other saved preferences; the existing global automation and
destination-location switches remain authoritative. Document the new default in
the update notes. This is an accepted design direction, not a claim that the
feature is already implemented.

Make the settings entry discoverable independently of the number, ordering, or
grouping of owned pets. Anchor it to a verified semantic menu container or a
stable native construction phase, not a pet slot, exact row count, or assumed
relative ordering among pets. Support the native grouped and ungrouped layouts
only after their structures and callback ownership are recorded for the exact
supported executable. Keep native entries, quick bindings, ownership limits,
and grouped navigation unchanged. Preserve the binding filter if custom menu
handling stops.

## Evidence needed before implementation

1. Identify and verify an exact-build successful teleporter-completion callback
   and its local-player/network semantics. Reject generic movement, location,
   ship/system warp or position changes as substitutes.
2. Repeat the grouped-menu scenario after roster changes and menu rebuilds. If
   the page disappears, capture bounded menu depth, vector counts, native action
   classes, callback phase and callback thread at the first safe refusal,
   without pet names, save data, writes or unbounded logging.
3. Verify the proposed thread recovery in the current game after death/menu
   rebuilds, and confirm that actions and settings still work. Keep rebinding
   restricted to a quiescent builder start; do not rebind during a transaction.

## Acceptance conditions

- Teleport and current load/ship-exit triggers can be controlled independently.
- Only a completed local teleport creates one opportunity; a network client's
  arrival does not alter local state or summon for the remote player.
- The same location, ownership, eligibility, placement, and no-duplicate rules
  apply after teleport. Unsupported or unsuitable places never bypass game
  checks.
- The settings page remains visible and usable with ordinary and grouped pet
  rosters, including changes to the roster after startup. Native pet rows and
  groups remain intact, regardless of their order or count.
- A failed native validation stops only the custom menu path safely and reports
  a bounded diagnostic; the binding guard remains active.
- Player-facing wording is added to the canonical English catalog and every
  affected locale entry in the same implementation change.
- Verify the exact supported executable and compare live behavior before
  updating any distribution. The current installed module and public alpha are
  not modified by this investigation.
