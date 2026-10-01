# Teleport arrival, respawn and grouped companion menu

Status: updated 1 October 2026 against the published 0.10.1-native-test
candidate and the exact Steam Cosmos 7.05 executable. The published archive is
unchanged. Teleport and respawn summoning remain unimplemented because neither
successful local completion event has been verified. The current menu candidate
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

The reported death case is a third, independent trigger problem. A respawn
opportunity must be considered only after the local player's respawn completes;
death itself, save loading, teleport arrival and generic movement are not
interchangeable events.

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

## Exact-build teleport mapping update (1 October 2026)

The exact Steam 7.05 executable hash remains
`671de22649274b49fa07f5a246bc7252c4e08bb9ab623d2e65722fbab4e497a4`. A
read-only PE `.pdata`-bounded string-xref pass found teleporter identifiers,
position helpers and configuration names, but no verified successful local
arrival callback. The destination CVar names
`AngleFromBaseComputerWhenTeleporting` and
`DistanceFromBaseComputerWhenTeleporting` describe placement settings; they do
not prove arrival. The simple float-getter scan supplied in the latest
PowerShell result was too narrow to support a negative conclusion because it
required a `movss [rcx]` read to be followed immediately by `ret`.

The reusable scanner, exact tool versions, reference counts, candidate RVAs,
false leads and Ghidra limitation are recorded in the
[Cosmos 7.05 compatibility report](NATIVE-0705-COMPATIBILITY.md) and the
[native update map](NATIVE-UPDATE-MAP.md). Teleport summoning remains open and
unimplemented; the current profile stays unchanged until a local completion
signal and its ABI/network semantics are proven.

A separate byte-pattern scan also found candidate RIP-relative references to
`AngleFromBaseComputerWhenTeleporting`,
`DistanceFromBaseComputerWhenTeleporting`, `Teleporting` and the
`gcpersonalteleporter.cpp` marker. That scan is not a disassembler; its hits
remain candidates until each instruction is decoded and its containing flow
identified. The sanitized offsets and exact scan limitations are recorded in
[NMS-075-STATIC-XREFS](NMS-075-STATIC-XREFS.md). Treat these byte-pattern leads
separately from the `.pdata`-bounded string-reference scan above.

## Respawn-path mapping update (1 October 2026)

The exact Cosmos 7.05 executable has a promising but unverified respawn-path
lead. A `.pdata`-bounded string-reference scan found `DoPlayerRespawn` at
instruction RVA `0x33026B` inside range `0x32F335-0x33177F`, and
`PLAYER_RESPAWN` at `0x14FA051` inside range `0x14F7F60-0x14FA1BA`. The latter
large function is a shared player-positioning helper that includes player/ship
placement raycasts. Its body reads the first argument object, saves a 32-bit
second argument and reads the low byte of the third argument.

The reusable direct-call scan found 11 callers for RVA `0x14F7F60`. Three call
sites lie inside the range carrying the `DoPlayerRespawn` label:

| Call RVA | Return RVA | Exact-build evidence |
|---:|---:|---|
| `0x3302BF` | `0x3302C4` | Passes a manager-like pointer in `RCX`, a value loaded from `[rsi + 0x620]` in `EDX`, and a byte-like flag in `R8B`. |
| `0x33066A` | `0x33066F` | Passes a manager-like pointer in `RCX`, a value loaded from `[rsi + 0x620]` in `EDX`, and zero in `R8D`. |
| `0x330941` | `0x330946` | Passes a manager-like pointer in `RCX`, a value loaded from `[rsi + 0x620]` in `EDX`, and zero in `R8D`. |

Other callers include functions with warp labels such as `WarpLight`,
`DIST_WARP`, `WARP_PURE` and `WARP_FREI`; some pass different reason-like
values, including `8`, `0xE`, `0x11` and `0xB`. Therefore, hooking this helper
without a return-site filter would confuse unrelated placement/warp work with
respawn. Even the three narrower call sites are not proof that a death occurred
or that respawning succeeded; the label and `PLAYER_RESPAWN` string are
corroborating clues, not a verified event contract.

A test-only observer records only calls returning to
`0x3302C4`, `0x33066F` or `0x330946`, plus the two scalar argument values. It
does not request a summon or change runtime policy. This observer is not the
production trigger and must not be described as a death fix. The callback was
live-exercised in a save-load sequence, but its relationship to a successful
death respawn is unknown. Before production behavior is added, the exact local
respawn completion point, call frequency, local/network semantics and
cancellation rules must be established.

The observer build `0.10.1-native-test-respawn-observer` passed the offline
native bundle validators on 1 October: 88 policy traces / 31,216 comparisons,
59 selector traces / 25,733 comparisons, 333 storage cases / 721 operations,
59 runtime cases, 16 backup checks and six owned-host refusal runs. Its module
SHA-256 is
`cc82f7ffc95eacde583b5225dc2a4d530b9dff804a5666644def12e24f197702`.
It was staged locally after a fresh verified backup of the current save and
preference files and the previously installed module. In the next local session,
the log confirmed exact-build acceptance, the private pre-activation snapshot,
active native integration and observer initialization. After the successful
local save-load event at `16:08:47Z`, the log recorded an armed opportunity at
`16:09:03Z`, then returns `0x3302C4` (`reason=1`, `flag=1`) and `0x330946`
(`reason=1`, `flag=0`) at `16:09:10Z`; the ordinary summon queue was accepted
at `16:09:11Z`. No death was reported during this sequence. This is evidence
that the candidate call sites also occur during a successful save-load
sequence, so they do not identify death by themselves. No death-specific
trigger is verified. The log's hook-count wording in this build is a fixed
baseline message; a follow-up build removes that ambiguous count. The public
0.10.1 archive and Nexus file 49367 are unchanged. The follow-up module
`dc2b7356737ae91a114a2113e8877d8acb3644d2f5853ec64e4d25ba6e17212d` passed
the offline bundle validators and removes the hardcoded count from the
diagnostic status message. It was not staged while the game was running; the
currently loaded observer remains unchanged.

## Live teleporter control (1 October 2026)

The owner teleported from a freighter to a space station in the running
observer session and reported that a companion appeared after arrival. At
`16:44:22.981Z`, the passive observer recorded return RVA `0x3302C4` with
`reason=11` (`0x0B`) and `flag=1`; at `16:44:24.345Z`, the native summon queue
was accepted. The observer records only this return site and two scalar
arguments; it does not record destination identity or a teleport event.

Crucially, the same log recorded `Automatic summon opportunity armed` at
`16:30:17.434Z`, roughly fourteen minutes before the teleport, and no new arm
event at arrival. The live runtime can arm only after a successful local save
load or ship exit. The opportunity at `16:30Z` therefore most likely came from
a ship exit, although that action was not independently captured. The observed
arrival summon is consistent with that older pending opportunity becoming
eligible at the station; it does not show that teleport arrival created a new
opportunity. This is delayed eligibility, not verified teleport-trigger
support.

The `0x3302C4` candidate return also runs during this teleporter sequence, with
a different reason value from the earlier save-load observation. It is
therefore not death-specific and cannot be used alone as a respawn trigger.
Keep the public teleport/death behavior marked unimplemented. A natural local
death/respawn observation is still needed to find a distinct, successful
respawn signal.

In a subsequent negative control, the owner opened and backed out of the
teleporter interface without selecting a destination. The active log timestamp
and contents did not change, and no candidate return was recorded. This rules
out mere interface open/back as the source of the candidate callback in this
session. It does not distinguish destination confirmation, transition start
and completed arrival; the successful trip remains the only positive sample.

The owner later teleported to a freighter. At `17:08:33.960Z`, the observer
recorded returns `0x3302C4` and `0x33066F`, both with `reason=11` and flags `1`
and `0`; it recorded no new opportunity at that moment. A later `0x3302C4`
sample at `17:11:44Z` had `reason=9`. At `17:12:53Z` the normal runtime armed
an opportunity and accepted a queue at `17:12:56Z`, but the intervening player
action and visible result were not captured. These samples further show that
the shared positioning helper runs in the teleport session; they do not
identify a teleport-completion or respawn event. The current Nexus description
does not claim freighter support, and no freighter-specific summon result was
verified in this test.

After a Windows `AppHangB1` report at `19:14:39` local time, the game restarted
with the same executable SHA-256 and Steam build. The next process logged a
successful local save load at `17:15:26Z`, armed an opportunity at `17:15:38Z`,
and accepted the ordinary summon queue at `17:16:53Z`. The owner reports that
the pet appeared only after moving from a planetary cave to the surface. This
is consistent with the existing wait for a location where native placement is
possible. The log does not identify the precise placement check or prove that
the earlier hang had the same cause as the summon delay. Windows reported an
application hang rather than a faulting-module crash; no cause is established.

The owner reports that a pet cannot currently be summoned manually on the
freighter. This is a bounded report for the current game session, not a
freighter-wide compatibility result or evidence that the mod should bypass the
game's eligibility checks. The mod's current public description does not claim
freighter support; automatic summoning must remain subject to the same native
manual summon and placement rules.

## Broader respawn-string pass (1 October 2026)

A follow-up `.pdata`-bounded scan of the exact Cosmos 7.05 executable searched
all printable strings containing `respawn`. It matched 60 strings and decoded
52,096,118 runtime-function bytes with no skipped ranges. It found no
confirmed local completion event. In particular, `RPCReceivedPlayerRespawned`
appears only in MSVC type/template names for a network RPC receiver; the scan
cannot show whether it runs for the local player. `RespawnPlayer` has no direct
RIP-relative reference in this pass, which does not prove it is unused or
absent. Player-death position labels lead to data/serialization code, not a
verified completion callback. See the detailed lead table and exact limitations
in [NATIVE-0705-COMPATIBILITY](NATIVE-0705-COMPATIBILITY.md).

A focused follow-up searched `RespawnReason`, `LastKnownPlayerState`,
`SpawnLocation` and `PLAYER_RESPAWN`. It did not map the logged numeric reason
values. A compiler-generated type name links a captured lambda to
`cGcPlayerRespawn::SpawnAndPositionShip`, but the string has no direct code
reference and does not identify successful completion. Keep it as a static
respawn-path candidate only; the exact trigger remains unresolved.

The reason argument passed to the shared positioning helper is also produced
by a state-based function at RVA `0x331F60`. A `.pdata`-bounded caller scan
found one direct caller, at `0x330287` in the `DoPlayerRespawn`-labelled
function. Its `EAX` result is stored in object field `+0x620` and forwarded to
the positioning helper. The function returns multiple codes, but their enum
names and event/success meaning are not mapped. This strengthens the dataflow
map only; it does not establish a teleport or completed-respawn trigger.

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

Treat **Summon after respawn** as a second independent opportunity setting. It
should default ON for fresh profiles and only be added on upgrade when that
preference is absent. It becomes eligible only after a completed respawn of the
local player, then follows the same global switch, destination controls,
eligibility and placement checks as every other trigger. It must not summon
during the death/respawn transition, for another player's respawn, or merely
because a shared position helper ran. This is also an accepted design
direction, not implemented behavior.

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
2. Identify and verify a separate exact-build completed local respawn event.
   Correlate any passive candidate observation with an ordinary naturally
   occurring respawn; do not infer success from the shared positioning helper.
3. Repeat the grouped-menu scenario after roster changes and menu rebuilds. If
   the page disappears, capture bounded menu depth, vector counts, native action
   classes, callback phase and callback thread at the first safe refusal,
   without pet names, save data, writes or unbounded logging.
4. Verify the proposed thread recovery in the current game after death/menu
   rebuilds, and confirm that actions and settings still work. Keep rebinding
   restricted to a quiescent builder start; do not rebind during a transaction.

## Acceptance conditions

- Teleport and current load/ship-exit triggers can be controlled independently.
- Only a completed local teleport creates one opportunity; a network client's
  arrival does not alter local state or summon for the remote player.
- Only a completed respawn of the local player creates a respawn opportunity;
  its control remains independent from the teleport and load/exit triggers.
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
