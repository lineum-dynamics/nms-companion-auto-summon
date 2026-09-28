# Native migration boundary and source map

Recorded 28 September 2026 from a read-only review of the maintained Python
source and retained combined 0.9.2 payload. This is a migration inventory,
not a new validation of game addresses, hook ABIs, native ownership, loader
compatibility, scanner clearance or playable C++ behavior. Existing player
packages and installed sessions remain unchanged.

The first native milestone is an inert compiled ABI probe and a pure-policy
differential harness. It must not install hooks, access game memory, modify
player files, deploy a loader or launch NMS. The acceptance gates below distinguish
this offline work from a future game-integrated implementation. A native rewrite
does not itself resolve Nexus quarantine or the retained menu-thread refusal.

## Maintained inputs and generated outputs

| Layer | Canonical source | Retained generated/runtime boundary |
|---|---|---|
| Decision policy | `src/policy.py` | Concatenated by `build.py` into `CompanionAutoSummon.py` |
| Per-save favourite | `src/persistence.py` | Same production file; mod-owned state, not game saves |
| Preferences | `src/settings.py` | Same production file; schema 4 with legacy readers |
| Habitat and shuffle | `src/selection.py` | Same production file; session-only selection state |
| Game adapter | `src/runtime.py` | Production 0.5.1-experimental |
| Menu adapter | `tools/quick_menu_order_trial.py` | `CompanionMenuOrderTrial.py`, 0.9.1-diagnostics |
| Menu models | `tools/quick_menu_item.py`, `quick_menu_order.py`, `quick_menu_submenu.py`, `quick_menu_toggle.py` | Bounded snapshots, builder/activation transactions, captions and confirmation |
| Preference bridge | `tools/quick_menu_preferences.py` | Menu requests dispatched to the registered production instance |
| Binding protection | `tools/quick_menu_native_guard.py`, `quick_menu_guard_runtime.py` | Separately pinned native filter |
| Icons and language | `tools/quick_menu_icon.py`, `quick_menu_assets.py`, `game_language.py` | Native resources and read-only language diagnostics |
| Packaging | `tools/build_quick_menu_play_trial.py` | `build/quick-menu-play-trial-092-r1`, combined 0.9.2-play-trial |
| Player startup | `tools/portable_launcher.py`, `portable_host_support.py`, maintained guarded hosts | Verified backup, private session staging and exact-process pre-injection checks |

The combined builder copies production byte-identically and includes the menu
helpers, eight DDS assets and fourteen catalogs. Production has nine callbacks
on seven targets; menu has nine callbacks on six targets. TriggerAction is
shared, giving twelve framework hook targets. The native binding filter is
additional to those twelve. A replacement must not accidentally duplicate the
shared TriggerAction detour or change before/original/after ordering.

## Prior game mapping, not new native validation

Every RVA below comes from the existing exact-build source. The supported
profile is Windows x64, Steam build **25442159**, Cosmos **7.04**, executable
SHA256 `b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`.
The profile is maintained in `compatibility.json`. This inventory does not
re-disassemble the executable or establish compatibility with another build.

The prototypes express the existing ctypes contracts. `bool`, `float`,
`int32`, `uint32` and pointer widths/calling conventions need explicit native
ABI assertions and independent verification before any new game hook/call.

| RVA | Existing contract | Use |
|---|---|---|
| `0x146AC90` | `void QueuePet(void* player, int32 slot)` | Production after-hook; automation calls it |
| `0x1526940` | `bool TriggerAction(void* menu, void* action, bool called_as_menu)` | Shared production/menu before and after |
| `0x5066A0` | `void PetOwnershipUpdate(void* owner, float dt)` | Production after |
| `0x17479D0` | `void Eject(void* ship, void* player, bool animate, bool force)` | Production after |
| `0x1479490` | `void EnterCockpit(void* player)` | Production before |
| `0x1440CD0` | `void PlayerUpdate(void* player, float dt)` | Production after |
| `0x56FA50` | `bool LoadSave(void* player_state, void* common_data, void* state_data, bool network_client, bool resetting, uint32 arg6)` | Production before and after |
| `0x146A410` | `bool CanSummon(void* player, int32 slot)` | Call only |
| `0x505B70` | `bool OwnedPetEligible(void* owner, int32 slot)` | Call only |
| `0x1438040` | `void RefreshPlacement(void* arc, float range1, float range2, uint32 hand)` | Call only |
| `0x60B770` | `bool UseSummonHand()` | Call only |
| `0x9B8300` | `void TimedMessage(void* notifications, void* message, float duration, void* colour, uint32 audio, void* icon, bool flag7, float extra_time, bool flag9, bool flag10, bool flag11)` | Call only |
| `0x151ED00` | `void BuildActions(void* menu, void* render)` | Menu before and after |
| `0x1523220` | `void BuildLabel(void* menu, void* output)` | Menu after |
| `0x1533980` | `void* Append(void* header, void* incoming)` | Menu before; original used to add items |
| `0x15311C0` | `bool ConfirmPredicate(void* menu)` | Menu before and after |
| `0x151AD80` | `void LoadResources(void* menu)` | Menu after |
| `0x1432FC0` | `void* ConstructItem(void* aligned_item, uint32 icon, int32 action, bool disabled, bool background)` | Call only |
| `0x150FAC0` | `void Select(void* menu_depth_field, int32 depth, int32 index)` | Call only |
| `0xEC0670` | `void LoadTexture(void* record)` | Call only |
| `0x2D5C890` | `void RetainHandle(void* record)` | Call only |

### Object fields and identity

The current production adapter reads individual fields; it has no complete
ctypes game-object structure. A C++ port should not invent full packed structs
from these partial offsets. Retain explicit bounded reads and separately assert
the layouts of owned buffers.

| Object/base | Fields |
|---|---|
| Module base | Application pointer `+0x6E7AAE8`; summon range float `+0x52381E0` |
| Application | Local player `+0x71C690`; location `+0x57A584`; active pet `+0x29A1C0`; pet ownership/table `+0xE10D0`; solar pointer `+0x71AF70`; summon hand `+0x30E7FC` |
| Player | Pending pet `+0x6010`; physics context `+0x2A8` |
| Pet entry | Stride `0x24A0`; seed `+0x2330`; resource `+0x2370`; birth time `+0x23C0`; biome `+0x2480` |
| Ownership | Placement arc `+0x1B9140`; preview index `+0x1B9300`; emote flag `+0x1B937D` |
| Solar-system object | Planet count `+0x2544`; current planet index `+0x5196D0` |
| Planet entry | Stride `0xD9170`; biome `+0x6148`; subtype `+0x614C` |
| Common save-state data | Universal ID `+0x8980`, from `GcPlayerCommonStateData`, not player-state data |
| Notifications | Application `+0x837B40`; message count at notifications `+0x28C`; blocking float at application `+0x4BF50C` |
| Menu | Depth `+0xA050`; vector headers `+0xA058`; selected indices `+0xA088`; companion icon `+0xA104`; pending selection `+0xA16C` |
| Menu item | 224 bytes, temporary buffers aligned to 16 bytes; action `+4`; slot `+0x84`; private marker `+0x88`; name `+0x98` (64 bytes); binding `+0xD8` |
| Menu vector header | 16 bytes: signed capacity, signed count, data pointer |
| Icon resource | 24-byte owned record; handle `+0x10`; manager pointer RVAs `0x6E0D090` and `0x5901610` |

Companion identity is exactly sixteen bytes: eight seed bytes followed by eight
birth-time bytes. Seed padding and lazily generated bone-scale seed are excluded.
A slot number is not a stable identity. Duplicate identities, changed ownership
and replaced slot occupants must retain the existing refusal/cancellation rules.

### Binding filter lifetime

`GetButton` at `0x2C1DDE0` has the existing contract
`bool(void*, int32, int32, bool)`. The filter accepts an audited caller return
address at `0x151DDEB`. Only that call site provides the live menu in **RDI**;
other callers are forwarded before RDI is read. The full sixteen-byte
`CAS_MENU_V1` private marker and a native None action identify protected entries.

This is generated Win64 leaf code, preserving arguments/nonvolatile registers,
not an ordinary Python callback. The current guard validates the actual process,
disk hash, target prefix and complete nineteen-byte trampoline and checks pinned
relay/filter memory before custom operations. Bounds checks do not establish
borrowed native memory ownership. Owned-buffer tests cannot prove the game's
caller lifetime.

The filter remains installed until process exit, including after custom menu
processing stops, so existing tagged entries cannot be serialized as empty
native quick bindings. Any loader/unload plan must preserve this protection.
Removing the filter while native entries survive is not a safe cleanup strategy.

## Behavior and callback ownership to preserve

### Opportunities, startup and manual dismissal

- Successful **local** save-load completion records one deferred opportunity.
  Native summoning/placement does not run during deserialization. Network-client
  loads must not reset or arm the local player's state.
- Ship exit creates an opportunity; ship entry cancels it. Pet absence, teleport
  arrival and base removal do not currently create opportunities.
- A later local ownership update establishes readiness and consumes the load
  opportunity before arming normal policy. Acceptance consumes the request; a
  later manual dismissal must not recreate it.
- OFF, pending settings changes, native manual selection, preview/emote,
  active/queued pet, disabled location and invalidated save/application context
  cancel or suppress the existing request according to the current adapter.
- Preserve 1.5 seconds of observed on-foot stability, 0.5-second placement pacing,
  maximum 0.25-second consecutive probe gap and no default request expiry.
  Failed placement retries retain the chosen companion rather than rerolling.
- Ownership update performs refresh/check/queue after the game's placement reset.
  Final identity/intent checks happen after native eligibility calls because those
  calls may reenter callbacks. Queue acceptance is not visible-spawn evidence.

Manual favourite attribution requires a matching before/action/accepted-queue/
after transaction, same OS thread and epoch, local player, application, save,
slot and identity, and successful native action result. The action pointer is
borrowed only during BEFORE; after-return code compares its value without
dereferencing its former storage. Unrelated native queues, including battle
restoration, must not learn favourites or announce that a favourite was saved.

### Menu and resource ownership

Menu construction uses temporary aligned owned items and the game's append
function. Appending can move vector storage, so item pointers are not retained
across growth. Builder, activation and confirmation pairings have reentrancy and
thread checks. Native confirmation must first be observed released and then
pressed; neither held input nor menu rebuilding should repeatedly toggle settings.

The ordinary menu adapter pins the first accepted callback's OS thread for the
whole Mod instance. A later different thread causes `unexpected_thread` and
stops custom handling before native reads/writes. This happened in retained
090-r2 evidence. It is not established that Python caused the thread transition
or that teleport/base removal is a safe rebinding point. See
[menu lifecycle evidence](MENU-THREAD-LIFECYCLE.md). The resource-loading phase
has a separate lock and does not establish or change the ordinary callback pin.
Acquired icon references are pinned through process shutdown, including reloads.

C++ removes the Python GIL; it does not create a concurrency contract. Do not
silently share mutable callback state across threads or hold a broad mutex across
native calls that can reenter hooks. Establish ownership and explicit transaction
sequencing first. Keep existing refusal behavior until new lifecycle evidence
supports a specific change.

The menu queues preference intent; local Player.Update applies it and performs
persistence. A pending OFF request already suppresses ownership-update summoning
before it is saved. The menu must not take over game calls or file writes on an
unverified UI callback thread.

## Reuse and migration contracts

### Pure policy and selection

`src/policy.py` is already independent of game/file access and accepts supplied
observations and monotonic time. Port it first using explicit value types and an
offline differential harness. Compare complete state transitions, acceptance,
rejection and cancellation, including malformed indices/times and backward time.

`src/selection.py` can follow using immutable sixteen-byte identities, an explicit
owned roster and a separate temporarily eligible set. Inject random decisions so
tests can compare outcomes without requiring identical Python/C++ RNG algorithms.
Preserve directed 13/5/1 exact/related/acceptable group weighting independently of
group population, frozen reservations, commit only after queue acceptance and
session-only shuffle history. Unknown habitats wait; no approved owned habitat
pool skips one opportunity; neutral station/Nexus pools are unweighted.

### Preferences and per-save favourites

Retain `%LOCALAPPDATA%/NMS-AutoPet/settings.json` and `state.json` as the external
data contract; branding must not reset or silently migrate them. Settings schema
4 defaults fresh users to By habitat and shuffle ON. Schema 1/2/3 readers preserve
legacy choices and initialize shuffle OFF. Invalid existing preferences start
automation OFF and are not overwritten.

Settings reads are bounded to 4 KiB; favourite storage is bounded to 1 MiB and
256 save entries. Both reject duplicate JSON keys and unsupported/invalid
documents, reread before writes and use an atomic same-directory replacement
after flushing data. Favourites use the existing schema 1, lower-case identity
hex and `nms:{universal_id:016x}` keys. Zero save IDs allow session-only selection.
Use temporary fixture directories for native parity tests, never the player's
real data or game saves. A C++ JSON library's default duplicate-key behavior is
not sufficient evidence of contract compatibility.

### Compatibility, startup and backups

The existing portable route validates the selected installation and rechecks the
actual process handle/path/hash before every DLL injection, followed by an
independent in-game class/native-filter guard. A native loader must replace those
guarantees explicitly: actual executable identity before hooking, no force-enable
override, and no game-native HUD call to report an unsupported build. The disk
hash is not a complete validation of mapped executable bytes; preserve that limit.
See [compatibility audit](COMPATIBILITY-GUARD-AUDIT.md).

Direct loading during a normal Steam start means NMS is already running. Copying
saves inside a DLL cannot honestly preserve the current **closed-game pre-launch**
backup guarantee. The present launcher holds a setup lease, verifies closed game,
copies bounded save/preferences input, verifies source/copy/source, rechecks the
input inventory and closed-game state, then stages a private runtime session.
Define an equally clear installation/startup backup contract before presenting a
direct-load package as a player-ready replacement. Do not claim a concurrent
startup copy or a one-time installation backup is equivalent.

### Localization and assets

Fourteen catalogs with 63 keys exist. Thirteen translations are unreviewed drafts;
native menu/HUD still use English. Read-only language observation is not safe
runtime catalog selection or verified glyph coverage. Reuse catalog keys/assets
and preserve source fingerprints; any UI meaning change must update English and
every affected translation in the same change. Code-only offline prototypes do
not require artificial translation edits. See [localization status](../../LOCALIZATION.md).

## Milestone acceptance gates

1. **Offline core and inert ABI probe.** Build from explicit source inputs;
   inspect architecture/imports/exports; run the probe in an owned test process,
   never NMS. No hooks, game memory, loader deployment, saves or external settings
   access. Differential traces must cover pending/in-flight transitions,
   cancellation, rejection and valid/invalid clock/index boundaries. Record exact
   compiler/build inputs and bounded results. This validates the prototype only.
2. **Loader and compatibility contract.** Independently establish loader ABI,
   initialization/thread context, supported loader versions, conflict detection,
   failure behavior and unload lifetime. Design backup and mismatch-notification
   paths before a player deployment. Any native load observation remains distinct
   from game-hook safety. Preserve the working Python package.
3. **Passive native observation.** Only after gates above, a separate exact-build
   candidate may observe bounded lifecycle events without summoning or menu writes.
   Establish local ownership, startup timing, shared-target sequencing and actual
   callback threads. New native evidence must name its exact artifact; prior
   Python live observations do not validate it.
4. **Automation parity.** Port placement/queue adapter with original results
   preserved, same native limits and no generated companions. Controlled load,
   exit, forbidden placement, OFF and manual-dismissal checks must pass. Pure
   policy tests alone cannot establish this. Selection/persistence parity must
   precede enabling their replacement paths.
5. **Menu/resources parity.** Preserve native binding protection, pointer lifetime,
   callback pairing and thread refusal until specifically resolved. Verify native
   remapped controls, held input, seven preferences, icons, startup/reload/shutdown
   and persistence. Do not present diagnostic observation as a menu-lifecycle fix.
6. **Distribution acceptance.** Verify easy installation/removal, backups, upgrade
   failure, another Windows/Steam PC and multiplayer independently. Scanner results
   apply only to exact uploaded bytes; C++ and smaller packaging are not clearance
   or security proofs. Do not upload a prototype as a functioning replacement.

No player-facing meaning changes are introduced by this inventory. No translation
rewrite, game launch, package upload or native hook experiment was performed to
write it.
