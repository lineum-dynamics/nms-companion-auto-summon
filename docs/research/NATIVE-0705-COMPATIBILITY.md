# Cosmos 7.05 compatibility investigation

Status: 30 September 2026. The exact local 7.05 executable identity and static
candidate mappings are recorded below. Version 0.10.1 passed an initial live
smoke check: the owner reports a visible pet and the settings entry beside
grouped companions. A later direct load into the Anomaly reportedly had no
visible pet; an incomplete Anomaly mission preceded it, but any relationship is
unknown. Broader compatibility remains untested.

Use the reusable [native game-update mapping guide](NATIVE-UPDATE-MAP.md) for
the repeatable search workflow, evidence levels and per-build worksheet.

## Release facts

Hello Games published Cosmos 7.05 on 30 September 2026 and states that it is
live on Steam; updates for other platforms are pending. See the
[official 7.05 notes](https://www.nomanssky.com/2026/09/cosmos-7-05/).

## Existing native profile

The public 0.10.0-native-test package supports only:

- Windows 10/11 x64, Steam, Cosmos 7.04, build 25442159.
- Required `NMS.exe` SHA-256:
  `b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`.

The exact-file guard must continue to refuse unknown executables before hooks or
native game calls. Do not treat an updated version label or successful process
startup as proof that the 7.04 addresses still apply.

## Installed Steam snapshot

Checked after the owner reported the Steam update complete, on 30 September
2026. Steam reports the 275850 app installed (`StateFlags` 4), with all reported
downloaded and staged byte counts complete. Its manifest BuildID is `25624745`;
this is Steam depot metadata, not the game's patch number. The installed
`NMS.exe` reports file/product version `180383`, size `88,545,352` bytes, and
SHA-256:

`671de22649274b49fa07f5a246bc7252c4e08bb9ab623d2e65722fbab4e497a4`

The executable's recorded modification time is `2026-09-30T10:54:00.8767362Z`.
No NMS process was running during this read-only check. This confirms the local
Steam update completed and the executable differs from the supported 7.04
profile. It does not identify native addresses or validate any hook. The
published alpha must continue to reject this image until the evidence below is
complete.

After that check, the owner reported that the existing package showed its
Windows refusal dialog correctly: it said the game version was not verified,
identified supported build `25442159`, and stated that the mod was not
activated. This is live evidence for the visible mismatch-warning path only;
it does not establish 7.05 gameplay or hook compatibility.

## Preliminary static address check

The PE exception-function table in this exact 7.05 executable was parsed
read-only and compared with the 22 existing function-entry RVAs: twelve game
detours, nine direct-call targets, and the `GetButton` filter target. All 22
fall inside recorded function ranges, and none is the start of its containing
range. Therefore the 7.04 function-entry map cannot be carried into 7.05; these
addresses must not be hooked or called as if they were verified entries.

This check establishes boundaries only. It does not identify replacement
functions or validate their semantics, ABI, object layouts, callback callers,
or any required memory fields. No replacement addresses have been approved.
Keep the 7.05 integration disabled while rebuilding and verifying the map.

## NMS.py signature-match candidates

On 30 September, a read-only scan used the retained NMS.py signature records
from commit `b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`, with the existing
Python audit tooling (`pefile` and Capstone), against the hash-verified 7.05
executable. Each listed signature matched exactly once in executable sections,
and each match equals the beginning of a PE exception-table function range:

| NMS.py method | 7.05 candidate RVA | Existing 7.04 counterpart |
|---|---:|---:|
| `cTkInputPort::GetButton` | `0x2C25B40` | `0x2C1DDE0`; its binding-guard return-site caller is still unmapped |
| `cGcPlayerNotifications::AddTimedMessage` | `0x9BD8E0` | `0x9B8300` |
| `cGcPlayer::OnEnteredCockpit` | `0x1481F60` | `0x1479490` |
| `cGcSpaceshipComponent::Eject` | `0x17521C0` | `0x17479D0` |
| `cGcRealityManager::LoadTexture` | `0xEC6850` | `0xEC0670` |
| `cGcPlayer::GetDominantHand` | `0x14855F0` | possible counterpart to the old no-argument `0x60B770` helper; its machine code returns a 32-bit hand value, while the old call site treats its result as a Boolean gate |
| `cGcQuickActionMenu::TriggerAction` | `0x152FEF0` | `0x1526940` |
| `cGcPlayer::Update` | `0x14494F0` | `0x1440CD0` |
| `cGcPlayerState::SaveToData` | `0x57A690` | no equivalence established |
| `cGcPlayerState::LoadFromData` | `0x572C40` | no equivalence established |

These are name/signature-based function-entry candidates, not runtime proof.
Caller-anchored analysis below has since mapped the native targets and the
binding-guard return site used by the 7.05 test candidate. The six-argument load
hook has matching call-site layout, but NMS.py's `void` annotation conflicts
with callers consuming `AL`; preserve this ABI uncertainty in review. Static
matching does not establish successful hook installation or gameplay behavior.

This confirms that Ghidra is not required for the first bounded discovery pass:
the retained NMS.py signatures plus `pefile`/Capstone identify several unique
entries. It does not establish that these tools alone are sufficient for the
remaining semantic, caller and layout analysis.

The `AddTimedMessage` body independently confirms the leading native-call
contract: it reads the notification counter through `RCX + 0x28C`, uses `RDX`
as the message, saves `XMM2` as the duration, and copies the color pointer from
`R9`. It also consumes values from the caller's stack area in positions
consistent with the retained 7.04 eleven-argument declaration. This is strong
static ABI evidence for the replacement notification call, not live-HUD proof.

### Load hook has a caller-anchored replacement

`0x572C40` is a strong static match for the old six-argument `LoadSave` hook at
`0x56FA50`; it is no longer treated as an unmapped hook. Its direct callers at
`0x2E083F`, `0x48EE3C`, `0x48F8F3` and `0x49062D` set the same physical layout:
state object in `RCX`, two data pointers in `RDX` and `R8`, a flag in `R9`, then
the fifth and sixth arguments in the two stack slots. The candidate saves those
register arguments, reads the `RDX` and `R8` objects separately, and reads the
universal save ID at `RDX + 0x8980`, matching the old hook's common-state use.
Each inspected caller consumes `AL` immediately after the call as a status
value; one sets the fifth stack argument to 1 while other call paths pass 0.
The call at `0x49062D` sources `R9B` from a game-state flag, consistent with the
network-client parameter.

The retained NMS.py declaration demangles the function as returning `void`,
while the exact call sites use `AL` as a Boolean result. Preserve the machine
behavior expected by those callers and keep this type-annotation conflict
visible. Before enabling the candidate, finish checking all return paths and
the network-flag meaning against the exact build. This is strong static ABI and
role evidence, not live-load validation.

`SaveToData` at `0x57A690` is a separate unique signature candidate, but the
current native source does not hook it or write game-save data. Direct callers
at `0x4A8621` and `0x5D6C1C` pass an output pointer in `RDX`; a further call at
`0x5D6C5F` sets `RDX` to zero and its containing range `0x5D6C4F` has no direct
caller found by the current scan. Do not add it to this profile unless a
required native dependency is established.

## Caller- and RTTI-anchored menu candidates

The retained 7.04 menu audit also supports a few additional static candidates.
These comparisons use the exact 7.05 image above and keep raw disassembly in
the private temporary audit directory:

| Operation | 7.05 candidate RVA | Evidence |
|---|---:|---|
| `QueuePet` | `0x14738E0` | The matched 7.05 `TriggerAction` handler calls it with the same `(owner, slot)` setup and control-flow role as 7.04 `0x146AC90`. Its body stores the selected slot at `argument + 0x6020` and reads the companion table. |
| `CanSummon` | `0x1473060` | The matching 7.05 `TriggerAction` branch passes the selected slot in `EDX`, checks this Boolean result, then calls `QueuePet`. The function reads the global companion-owner table and calls the matching eligibility and normal validation helpers, paralleling 7.04 `0x146A410`. |
| `OwnedPetEligible` | `0x508200` | First helper called by the new `CanSummon`; its body reproduces the 7.04 eligibility checks: supported location, slot at most 29, acquired pet resource and unlocked slot. It now reads the application context through updated offsets. |
| Pet ownership update | `0x508D30` | Direct caller `0x4890C0` passes `RCX = game-state + 0xE0260` and the frame delta in `XMM1`. The target updates the same companion arc, preview and emote fields as 7.04 `0x5066A0`; embedded RTTI names also encode a lambda inside `cGcPlayerCreatureOwnership::Update(float)`. Its exception ranges split at `0x508D50`. |
| `RefreshPlacement` | `0x14407F0` | The mapped ownership update calls it with the same register setup and placement-arc object as the 7.04 call to `0x1438040`: arc in `RCX`, two floats in `XMM1`/`XMM2`, and hand in `R9D`. The new function is a PE exception-range entry. |
| Dominant-hand query | `0x14855F0` | The unique `GetDominantHand` match checks game state and returns the 32-bit application hand value at `+0x30E7FC` in `EAX`, or zero on its rejected path. The 7.05 adapter forwards this value directly to the matching placement helper, where the 7.04 adapter used the Boolean gate plus the same field; all other hand values still need live confirmation. |
| Quick-action update | `0x15267B0` | RTTI identifies the current `cGcQuickActionMenu` vtable at `0x4A4D550`; slot 0 is this update method, matching the retained 7.04 vtable's slot 0. |
| Quick-action builder | `0x15282B0` | The body matches the 7.04 builder's large stack frame and menu construction flow. It calls the new item constructor and append helper below. |
| Menu item constructor | `0x143B720` | Called by the builder with the item output, icon, action and flags; initializes the same `0xE0`-byte item shape and fields. |
| Menu vector append | `0x153CF40` | Called by the builder; copies `0xE0`-byte items into the native vector and uses the game's growth path when capacity is exhausted. |
| Selected-item label | `0x152C7D0` | Reads the same action-table depth, selected index and `0xE0`-byte item layout as the 7.04 label method. |
| Menu selection helper | `0x1518EF0` | Its bounds checks and selected-index store match the 7.04 `0x150FAC0` helper instruction-for-instruction; corresponding menu callers pass the same action-table, depth and index roles. |
| Confirmation predicate | `0x153A770` | It occupies slot 6 (`+0x30`) of the RTTI-identified `cGcQuickActionMenu` vtable, the same slot as the 7.04 predicate, and reads the selected item before returning a Boolean. |
| Resource initialization | `0x1524330` | The method loads the standard quick-menu summon texture and stores its resource handle in the menu object, matching the 7.04 resource-initialization role. |
| Binding filter return site | `0x152739B` | This is the return after the first `GetButton` call in the matched update-function chunk. The call arguments, following selected-item reads and code-relative position correspond to the old filter site `0x151DDEB`; the menu remains in `RDI`. |
| Retain resource handle | `0x2D65980` | Reads a 32-bit handle through `RCX`, resolves it through the resource-manager count/table at `+0x5C`/`+0x60`, checks resource state, and atomically increments its `+0x134` reference count. This matches the old `0x2D5C890` helper's algorithm and one-pointer contract. A native quick-menu caller at `0x151D467` passes the address of a temporary handle in `RCX` before copying that handle into a resource record. |
| Release resource handle | `0x2D61CE0` | Its split PE ranges together perform the old release helper's handle lookup and `lock xadd [resource+0x134], -1` path. `LoadTexture` candidate `0xEC6850` calls it at `0xEC68C6` with the address of its temporary handle after transferring ownership, matching the old `0x2D58BF0` lifetime path. |

The old-to-new match exposes these memory-layout candidates:

| Field | 7.05 candidate | 7.04 value | Evidence |
|---|---:|---:|---|
| Application-pointer RVA | `0x6E89688` | `0x6E7AAE8` | Two independent 7.05 routines load this same global pointer before using app-relative fields. |
| Local-player offset | `0x72C6F0` | `0x71C690` | Used by the matched builder and placement code. |
| Player companion-owner object | `0x25F760` | `0x24F700` | Passed by the matched summon handler to `QueuePet`. |
| Companion table offset | `0xE10D0` | `0xE10D0` | Used by `CanSummon`, `OwnedPetEligible` and `QueuePet`. |
| Pending companion slot | `0x6020` | `0x6010` | Written by `QueuePet` and read by the matched `cGcPlayer::Update`. |
| Active companion slot | `0x29A1C0` | `0x29A1C0` | Read and reset by the matched `QueuePet`. |
| Companion-entry stride | `0x24A0` | `0x24A0` | Used to index the table in both eligibility and queue code. |
| Ownership placement arc | `0x1B9140` | `0x1B9140` | Used by the matched ownership update and placement call. |

Additional mapped fields used by the runtime candidate are: common location
`app + 0x57A584`; active companion `owner + 0x29A1C0`; selected companion
`player + 0x6020`; companion resource, seed, normalized habitat and birth
identity at entry offsets `+0x2370`, `+0x2330`, `+0x2480` and `+0x23C0`;
solar-system pointer `app + 0x72AFB0`; and the placement range at image RVA
`0x527AB34`. The range resides in virtual data/BSS, so it has no raw file bytes;
the 7.05 update call at `0x509115` supplies the same value twice to the matched
placement helper. Quick-menu manager globals are RVAs `0x6E1BC10` and
`0x5910190`, both resolving to the same manager in the retained runtime check.
The native player physics pointer remains at `player + 0x2A8`, confirmed by
`cGcPlayer::Prepare` at `0x1442E70`. The notice object is `app + 0x847BB0`.

The 7.05 test candidate uses the exact executable identity recorded above and
these statically mapped targets. Its separate `native_compatibility.json`
leaves the legacy Python profile unchanged. This only permits a controlled
exact-build test; it does not label Cosmos 7.05 as verified or stable.

These observations do not prove runtime stability. The custom texture resource
retain helper and six-argument load hook have strong static counterparts, but
asset readiness and full resource/menu lifetime still need live observation.
The placement-range location has static caller evidence but lives in virtual
data/BSS, and the exact rendered-menu and summon appearance remain unverified.
Do not carry old offsets forward without their own cross-checks.

The first inspection had excluded `0x1473060` because it does not directly read
the incoming owner or slot in its own body. Following the register dataflow
showed that it deliberately obtains the owner from the game singleton and
forwards the unchanged slot in `EDX` to `0x508200`; its matching caller then
queues that same slot. This corrects the earlier tentative exclusion. The
six-argument load hook, summon-hand call, texture-handle lifetime and remaining
memory offsets have been mapped sufficiently for a guarded test build. The
candidate was subsequently rebuilt and offline-validated as
`0.10.1-native-test`; the bounded live smoke observation is recorded below.

## Required 7.05 evidence

1. Reconfirm the installed executable identity immediately before the live
   trial. Never inspect or replace a file while Steam is still writing it.
2. Run the complete offline build and owned-host validators, then package only
   the explicit allowlist and verify the resulting ZIP by readback and hashes.
3. Before live testing, close NMS normally and preserve/verify the required
   closed-game save backup. Do not modify the installed module while NMS runs.
4. Observe startup, menu placement and pet appearance in-game. Keep first-run
   backup and exact candidate hashes. A matching hash or successful loader start
   alone is not a compatibility result.
5. For a future build, upload only after the candidate passes those checks;
   describe any remaining multiplayer or scanner limits honestly. The current
   0.10.1 release status is recorded in the candidate identity below and the
   tester handoff.

Do not label 7.05 stable. The current `0.10.1-native-test` is an early public
test build with limited live acceptance; its linked VirusTotal hash matches the
local ZIP, but downloaded bytes have not been read back. Future builds still
need the evidence above and broader live testing.

## 0.10.1 candidate identity and prelaunch staging

The `0.10.1-native-test` candidate was built against the exact Steam executable
above. Its final archive is `CompanionAutoSummon-0.10.1-native-test.zip`, 30
files / 3,725,689 bytes, SHA-256
`51cf81c7cc48e835a1f9f14f96ced93d2a32b56200c5c079e23f2b0f17331116`.
The native module SHA-256 is
`29f6a18636a379c7d8cfd0d135b4966bdc73df6f53771373ce122ef910aa40a8`.
The archive was read back and every member checked against its manifest. The
loader remains the exact retained UAL 9.7.4 x64 file.

Offline verification passed: 790 developer tests; native policy 31,216
command/state comparisons across 88 traces; selector 25,733 comparisons across
59 traces; 333 storage cases / 721 operations; 59 runtime cases; 16 backup
checks; six owned-host refusal/hash/no-side-effect runs. These are controlled
offline checks, not game sessions.

The candidate module was staged locally while NMS was closed. The existing
0.10.0 module was backed up and verified before replacement; the existing UAL
loader matched the package hash and all eight installed icons already matched,
so no loader or icon files were changed. A separate closed-game backup of 52
save files and two top-level preference/state files was created and verified
before staging. After launch, the owner reported that a pet appeared and that
the settings entry remained visible beside grouped companion entries. This does
not establish full menu interaction, every location, long-session stability
or multiplayer. Nexus file **49367** is publicly listed as Main / Primary; the
mod page reports **Safe to use**, and its linked VirusTotal SHA-256 equals the
local archive hash. The file-specific summary was corrected and read back from
the public listing. Edge blocked the owner manual-download attempt
(`ERR_BLOCKED_BY_CLIENT`), so the downloaded ZIP bytes were not read back; see
the tester handoff for the remaining download-verification limit.
