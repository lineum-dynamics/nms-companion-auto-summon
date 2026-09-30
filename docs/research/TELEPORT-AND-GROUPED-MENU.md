# Teleport arrival and grouped companion menu

Status: investigation opened 30 September 2026. The published 0.10.0-native-test
archive is unchanged. This record describes source-level constraints and owner
reports; it does not claim either issue is fixed or live-reproduced by the
current native candidate.

## Owner reports

- A pet does not automatically appear after teleport arrival.
- With a large owned roster, the game groups companions in its menu and the
  Companion Auto Summon settings page is no longer visible.

These are separate problems: the first needs a trustworthy local-arrival event;
the second needs a menu adapter that tolerates native menu variants.

## Verified source constraints

- `native/src/bootstrap.cpp` currently hooks successful local save-load
  completion and ship exit as opportunity sources. Its twelve-hook table has no
  verified teleport-completion hook.
- `native/src/runtime.cpp` only records a local load opportunity after a
  successful non-network load. Ship exit arms through `afterExit`. Teleport
  arrival does not arm the current policy.
- The retained `NMS.py` function-signature dataset identifies spaceship/system
  warp functions, but no verified base/station/Anomaly teleporter-arrival
  completion callback. System warp is not a substitute for teleport arrival.
- `native/src/menu.cpp` recognizes the companion category through native action
  45, looks for pet append actions 46/47, and rejects insertion if those actions
  are already in the vector. A child settings page is limited to depth two and
  exactly seven rows; row roles are the rows' numeric indices.
- The menu adapter pins its first accepted callback thread. A later thread change
  logs `menu_unexpected_thread` and permanently stops its menu handling. A
  builder/append transaction also requires the same thread.
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

1. Identify and verify an exact-build successful teleport-completion callback
   and its local-player/network semantics. Reject generic movement or location
   changes as substitutes.
2. Record menu depth, vector counts, native action classes, callback phase, and
   callback thread at the first safe refusal, without pet names, save data,
   writes, or unbounded logging. Determine whether grouped and ungrouped menus
   use the same settings-container path.
3. Demonstrate that any callback-thread handoff is serialized at a quiescent
   boundary. Do not rebind merely because callbacks arrive from a new thread.

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
