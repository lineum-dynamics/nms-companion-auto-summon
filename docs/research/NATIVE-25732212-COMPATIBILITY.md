# Cosmos 7.06 compatibility investigation

Status: 23 October 2026. Exact 0.10.3 r4 passed final startup, load appearance,
settings/icons and clean base-to-station acceptance. Earlier port candidates
passed clean ship exit and reverse teleport. Source is public at
`852c5c55458c563a8564090dd31305864483edf3`. Nexus file **50040** is uploaded
as Main / Primary but **quarantined**; download/scanner acceptance remains open.
Unknown executable identities are refused. See the latest dated handoff and
[scan investigation](NATIVE-0103-SCAN.md).

Use the reusable [NATIVE-UPDATE-MAP](NATIVE-UPDATE-MAP.md) for the repeatable
workflow, evidence labels and handoff requirements.
The required pattern-search and result-ledger procedure is in the
[NATIVE-PATTERN-PLAYBOOK](NATIVE-PATTERN-PLAYBOOK.md).

## Release and executable identity

Hello Games published Cosmos 7.06 on 5 October 2026 and states that it is live
on Steam. The official [release log](https://www.nomanssky.com/release-log/)
still lists 7.06 first as of 23 October 2026; it contains no 7.07 entry. See
the [official 7.06 notes](https://www.nomanssky.com/2026/10/cosmos-7-06/).

| Property | Observed value |
| --- | --- |
| Platform | Windows x64, Steam |
| Game release | Cosmos 7.06 |
| Steam app manifest build ID | 25732212 |
| NMS.exe file/product version | 180836 |
| NMS.exe size | 88,560,712 bytes |
| NMS.exe modification time | 2026-10-05 19:24:55 UTC |
| NMS.exe SHA-256 | 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499 |
| Existing approved profile | Cosmos 7.05, Steam build 25624745 |
| Existing approved executable SHA-256 | 671de22649274b49fa07f5a246bc7252c4e08bb9ab623d2e65722fbab4e497a4 |
| Git source baseline under review | `f7d97b61fcf152677d0d30de34f6c1b48675c436` (`main` base) |
| Research branch | `compat/cosmos-706-25732212`; exact 7.06 candidate enabled for controlled trials |
| Latest uploaded mod | `0.10.3-native-test`, Nexus file 50040, Main / Primary; quarantined |
| Final package target | Windows/Steam Cosmos 7.06, build 25732212 and exact 7.06 hash above; bounded local acceptance passed |
| Listing readback | 23 October 2026: 0.10.3 / exact 7.06 description and file 50040; automated quarantine, no file download |

The Steam build ID and executable hash identify different things. The mod's
public 0.10.2 hash guard rejects this executable before installing native hooks.
The Git source revision and Nexus package version are separate identities.
That rejection statement describes retained 0.10.2; final 0.10.3 targets the
exact 7.06 executable with separate static, offline and live evidence.

## Current gate index, 23 October 2026

The target source ledger now has **90/90 MAPPED**, with no static PARTIAL or
NOT CHECKED role. This is a static contract index, not release readiness.
Five new load-policy inputs expanded the original 85-role inventory; none was
removed. The last four roles are reconciled as guarded source contracts using
the complete ABI audit, explicit load policy, known constructor/copy/consumer
paths and owned-memory refusal checks. This is a scope/status reconciliation,
not four new signatures or proof of native lifetime/event semantics. The dated
candidate handoff explains each decision and retains the unresolved live gates.

| Acceptance gate | Evidence/state | Next bounded action |
| --- | --- | --- |
| Local save load | Final r4 visible appearance passed; exact return 0x4906C2, local receiver/vtable and stable identity checked. Known distinct DeathState return refused statically and in owned fixtures. | Death-trigger behavior remains NOT CHECKED / unimplemented; do not infer general network classification. |
| Experimental teleport | Final r4 base-to-station and earlier r3 reverse route produced distinct opportunities, accepted queues and visible pets. Temporary other-return sampling removed. | Multiplayer moving/stationary-player control remains NOT CHECKED; completion semantics unverified. |
| Custom menu | Final r4 settings/icons passed; unchanged menu inputs passed 28 owned scenarios. | Broad rebuild, grouped sizes, death recovery and input matrix remain NOT CHECKED. |
| Archive/source | Final 29-member archive read back; remote main/branch at 852c5c5 before upload; fresh rebuild reproduces every r4 product. | Preserve immutable bytes and receipts. |
| Distribution | Nexus 50040 listing/description read back; quarantine blocks download. ZIP 10/67, ASI 10/71; old ZIP now 28/68. | Investigate a concrete source/build defect; no exact detector cause or clearance established. Support contact declined. |

The current profile selects exact 7.06. Earlier source-selection snapshots
below are historical. Source approval, installed/live observations and host
acceptance are distinct gates; the latest dated handoff governs current status.

## Tools and bounded method

Public command blocks use `$python` and `$nmsExe` as aliases for privately
resolved, verified paths; `$py` aliases `$python`. Personal interpreter paths
have been removed from historical examples. Resolve the interpreter in the
authorized desktop context, check its version/imports and recorded SHA-256,
then assign its exact path privately. The argument values and recorded input
hashes below determine reproducibility, not a developer's username/path.

The boundary pass used CPython 3.11.9 and pefile 2024.8.26 to parse the AMD64
PE exception directory in the exact executable above. The source inventory was
read from the current 7.05 native implementation in
native/src/bootstrap.cpp, native/src/runtime.cpp, native/src/menu.cpp and
native/src/binding_guard.cpp. For each existing target RVA, the pass looked
for a PE runtime-function interval [BeginAddress, EndAddress) containing it
and recorded whether the address equalled BeginAddress.

A second read-only pass used the NMS.py signature records at
[commit b41bf9e](https://github.com/monkeyman192/NMS.py/blob/b41bf9e6fdff1c833b77d805bb0c8da555c4ced4/tools/data.json)
with `tools/native_signature_matches.py` and pefile 2024.8.26. The script reads
an external JSON file and does not embed third-party signatures or rewrite the
profile. Its unique matches are discovery candidates only. Capstone 5.0.9 is
available in an isolated scratch directory and is the version pinned by
native_research_requirements.txt. The NMS.py table below records signature
matches only; caller and role analysis is recorded separately later in this
report. No live game trial was used.

The pinned external checkout is clean at commit
`b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`; its `tools/data.json` SHA-256 is
`F311C9F54C0CCE199AB955A0E8DE2CFE2FCFB09274E557A2A27908C1B15BAF5F`. Its
repository license is [MIT](https://github.com/monkeyman192/NMS.py/blob/b41bf9e6fdff1c833b77d805bb0c8da555c4ced4/LICENSE).
This dataset contains only two names with `menu` or `quick` in the symbol:
`cGcQuickActionMenu::TriggerAction` and `cGcQuickMenu::cGcQuickMenu`. It has
no named byte signatures for the current quick-menu builder, item constructor
or append helper. This is a pattern-provider coverage gap, not evidence that
those game functions do not exist.

For the owner-update candidate, `tools/native_call_xrefs.py` was run with
the following command against this exact executable:

```text
python -B tools/native_call_xrefs.py --exe "<verified-NMS.exe>" --target-rva 0x508DC0 --context 6
```

It decoded 52,110,272 bytes in `.pdata` ranges, skipped zero ranges, and found
one direct call at `0x489661`. For unwind resolution, pefile 2024.8.26 reads
the `UNWIND_INFO` header at `UnwindData`, takes flags from header byte 0 and
the unwind-code count from byte 2, then locates the trailing
`RUNTIME_FUNCTION` after `4 + 2 * align_even(count)` bytes. Following
`UNW_FLAG_CHAININFO` recursively confirms that `0x508DE0` is chained to the
entry `0x508DC0`, rather than an independent method. An initial scratch
parser used the wrong starting offset for this trailing record; its result
was discarded and the corrected parse was checked against the `.pdata`
parent entries. Resolve these unwind parents before treating nearby exception
ranges as separate functions.

The same tool with `--target-rva 0x572410 --context 8` found one direct
caller, at `0x2CEAF0` inside `0x2CEA60–0x2CF43A`. Disassembly of the target
entry shows extensive object-field initialization and subobject constructors;
the caller context is another constructor. This rejects the tempting
`0x572410` load-hook lead created by old-RVA containment.

## 7.05 address boundary check against the 7.06 executable

Every listed address lies inside a 7.06 runtime-function range, but none is
the beginning of that range. This is a bounded negative result: the 7.05
addresses cannot be reused as verified 7.06 function entries. A containing
range does not prove that it is the corresponding function, nor that its ABI,
semantics, caller context or object layout is unchanged. `UNMAPPED` in this
boundary-only table means the old RVA has not been reused as a verified entry;
later sections may establish a different 7.06 candidate for that source role.

| Native role in the 7.05 source | Existing RVA | 7.06 containing range | 7.06 status |
| --- | ---: | ---: | --- |
| QueuePet / queue hook | 0x14738E0 | 0x1473672–0x1473D2D | UNMAPPED |
| Player update hook | 0x14494F0 | 0x14493E0–0x1449594 | UNMAPPED |
| Ownership update hook | 0x508D30 | 0x5085D0–0x508DB1 | UNMAPPED |
| Ship eject hook | 0x17521C0 | 0x1751B60–0x1753648 | UNMAPPED |
| Entered cockpit hook | 0x1481F60 | 0x1481F49–0x148227A | UNMAPPED |
| Save-load hook | 0x572C40 | 0x572410–0x573137 | OLD RVA REJECTED. Caller-anchored candidate `0x573500` receives the statically constructor-identified `cGcPlayerState` at `app+0xB940` at all four discovered direct callsites. The LocalLoadState and DeathState paths are now statically distinguished through the FSM current pointer; an exact state-identity guard is a candidate. Provider signature, session-byte local/network meaning, fifth-byte semantics and live completion remain unresolved. |
| Quick-action trigger hook | 0x152FEF0 | 0x152E7B2–0x1530866 | UNMAPPED |
| Quick-menu builder hook | 0x15282B0 | 0x1527BDD–0x1528568 | UNMAPPED |
| Quick-menu label hook | 0x152C7D0 | 0x152B394–0x152E6D1 | UNMAPPED |
| Quick-menu append hook | 0x153CF40 | 0x153CCCA–0x153D9B2 | UNMAPPED |
| Quick-menu confirmation hook | 0x153A770 | 0x1534D78–0x153B5B0 | UNMAPPED |
| Quick-menu resource hook | 0x1524330 | 0x1524230–0x152443C | UNMAPPED |
| Experimental respawn observer hook | 0x14F7F60 | 0x14F7F52–0x14F7F65 | UNMAPPED |
| CanSummon | 0x1473060 | 0x1473035–0x1473376 | UNMAPPED |
| OwnedPetEligible | 0x508200 | 0x508107–0x508209 | UNMAPPED |
| RefreshPlacement | 0x14407F0 | 0x14405C5–0x144083A | UNMAPPED |
| Dominant-hand query | 0x14855F0 | 0x1485402–0x1485EA9 | UNMAPPED |
| AddTimedMessage | 0x9BD8E0 | 0x9BC7E0–0x9BE076 | UNMAPPED |
| MenuConstruct | 0x143B720 | 0x143B680–0x143B789 | UNMAPPED |
| MenuSelect | 0x1518EF0 | 0x1518D9F–0x1519058 | UNMAPPED |
| LoadTexture | 0xEC6850 | 0xEC5E77–0xEC6C7A | UNMAPPED |
| Companion icon resource retain | 0x2D65980 | 0x2D658A5–0x2D65A4E | OLD RVA REJECTED: inside an unrelated resource/string-vector method; replacement `0x2D69720` is mapped below. |
| GetButton hook | 0x2C25B40 | 0x2C25B2E–0x2C25C58 | UNMAPPED |
| Binding-filter return site | 0x152739B | 0x1526240–0x15279DC | UNMAPPED |

## NMS.py signature candidates

The external signature file was searched in executable sections of the exact
7.06 image. Each candidate below is a unique match at a PE runtime-function
entry. This relocates a named method; it does not establish that the current
method has the same caller role, ABI, object layout, or behavior needed by the
mod. In particular, a matched `GetButton` method does not map the separate
quick-menu return site used by the binding filter.

| NMS.py method | 7.06 candidate RVA | 7.06 function range | Matches | Status |
| --- | ---: | ---: | ---: | --- |
| `cTkInputPort::GetButton` | 0x2C298E0 | 0x2C298E0–0x2C29A38 | 1 | STATIC-CORROBORATED; QAM callsite and return use below |
| `cGcPlayerNotifications::AddTimedMessage` | 0x9BF7B0 | 0x9BF7B0–0x9BF9C2 | 1 | ABI-CHECKED; decorated-name record conflicts with the exact body/callsite |
| `cGcPlayer::OnEnteredCockpit` | 0x1483E20 | 0x1483E20–0x1483F31 | 1 | STATIC-CORROBORATED; three direct callers pass the application local-player pointer. |
| `cGcPlayer::GetDominantHand` | 0x14874B0 | 0x14874B0–0x14874F4 | 1 | STATIC-CORROBORATED; forwarded `RCX` and source-call ABI checked below |
| `cGcSpaceshipComponent::Eject` | 0x1754180 | 0x1754180–0x17541C9 | 1 | STATIC-CORROBORATED; receiver/Boolean ABI and local-player caller setup align. |
| `cGcQuickActionMenu::TriggerAction` | 0x1531E00 | 0x1531E00–0x1532E3C | 1 | CANDIDATE; caller evidence below |
| `cGcPlayer::Update` | 0x144B3A0 | 0x144B3A0–0x144B609 | 1 | STATIC-CORROBORATED; see below |
| `cGcPlayerState::SaveToData` | 0x57B4C0 | 0x57B4C0–0x57B4DA | 1 | CANDIDATE; not a current mod dependency |
| `cGcPlayerState::LoadFromData` | — | — | 0 | SIGNATURE UNMAPPED; receiver identity for caller-anchored candidate `0x573500` is statically corroborated below |
| `cGcRealityManager::LoadTexture` | 0xEC8700 | 0xEC8700–0xEC87A8 | 1 | CANDIDATE |
| `cGcQuickMenu::cGcQuickMenu` | 0x2CA290 | 0x2CA290–0x2CA6CF | 1 | REJECTED FOR `MenuConstruct`; constructor has no explicit arguments, while the mod call passes four |

The `LoadFromData` signature did not match. The old hook RVA happens to fall
inside the 7.06 range `0x572410–0x573137`, but that range does not identify the
old method or a replacement entry. The range entry at `0x572410` initializes
the target object's fields and subobjects; its sole direct caller at
`0x2CEAF0` is inside another constructor. Reject this range as a load-hook
replacement. Do not hook the old RVA or infer a replacement from containment
alone. The named byte signature remains unmapped; the distinct
caller-anchored candidate is assessed below.

A second bounded string-reference pass used `tools/native_string_xrefs.py`
with CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.9, selecting
`cGcPlayerCreatureOwnership`, `cGcPlayerState` and `cGcQuickActionMenu`. It
matched 15 strings and decoded 52,110,272 bytes across `.pdata` ranges with no
skipped ranges. The `cGcPlayerCreatureOwnership::Update(float)` lambda type
string is present at RVA `0x50DD290`, but this pass found no direct
RIP-relative code reference to it. The Quick Action Menu type descriptor
string at `0x515A458` likewise had no direct reference of that form. A
`cGcPlayerStateData` string reference at `0x29F1CC3` is inside function range
`0x29F1C60–0x29F8A19`; `cGcPlayerState::SaveToData` is referenced at
`0x57B4F9` inside `0x57B4E6–0x57B503`. These are follow-up anchors only; none
maps the owner update or load hook. The no-reference results are limited to
direct RIP-relative references and do not rule out RTTI, indirect or other
reference forms.

Reproduce the bounded pass with the same tool and selectors:

```powershell
python tools/native_string_xrefs.py --exe "<exact Cosmos 7.06 NMS.exe>" --contains cGcPlayerCreatureOwnership --contains cGcPlayerState --contains cGcQuickActionMenu
```

Use the pinned packages in `tools/native_research_requirements.txt`; in the
recorded local run Capstone 5.0.9 was loaded from an isolated scratch
directory.

## Load-hook role candidate (caller-anchored, not a signature match)

Although the pinned `cGcPlayerState::LoadFromData` byte signature has zero
matches, the direct callers identify a strong replacement candidate at
`0x573500`. Its `.pdata` root is `0x573500–0x573577`; seven chained ranges
follow through `0x579B50` and resolve by `UNW_FLAG_CHAININFO` to that root. The
entry saves the four register inputs and allocates a large frame. Its body
uses the second input (`RDX`, retained in `R15`) to read a common-save value at
`+0x8980`, and its normal completion sets `AL=1`; an early invalid-data path
returns zero. These are consistent with the old load hook's common-state and
Boolean-result roles, but do not prove all parameter semantics.

The `.pdata`-bounded direct-call scan found four callers, each at the
corresponding 7.05 load-call paths already recorded in
[NATIVE-0705-COMPATIBILITY](NATIVE-0705-COMPATIBILITY.md):

| 7.06 call site | Caller range | Register arguments | Stack arguments before call | Return use |
| ---: | --- | --- | --- | --- |
| `0x2E088F` | `0x2DF30D–0x2E1AD9` | `RCX=[rax+0xAAD0]`, `RDX=&[rbp+0x2240]`, `R8=r14`, `R9D=0` | arg5=`1`, arg6=`r15b` | `AL` tested |
| `0x48EECC` | `0x48E400–0x48FA5C` | `RCX=[rsi+0xAAD0]`, `RDX=&[rbp+0xC0]`, `R8=r15`, `R9D=0` | arg5=`dil`, arg6=`bl` | `AL` folded into status |
| `0x48F983` | `0x48E400–0x48FA5C` | `RCX=[rsi+0xAAD0]`, `RDX=&[rbp+0xC0]`, `R8=r15`, `R9D=0` | arg5=`r13b`, arg6=`bl` | `AL` folded into status |
| `0x4906BD` | `0x48FA60–0x49081A` | `RCX=[rdi+0xAAD0]`, `RDX=[rbp+0x3C0]`, `R8=rsi`, `R9B=[rdi+0x4BE6A0]` | arg5=`0`, arg6=`0` | `AL` folded into status |

The old 7.05 callers at `0x2E083F`, `0x48EE3C`, `0x48F8F3` and `0x49062D`
have the same surrounding caller paths. The 7.06 register/stack setup preserves
the six physical argument locations used by the current `Load` function
pointer. The receiver chain below now identifies the object at every discovered
direct callsite as the same constructor-initialized `cGcPlayerState` at
`application+0xB940`. This proves receiver identity for those direct paths, not
that `0x573500` is safe as a global hook or that every possible indirect call
has been found. The call at `0x4906BD` sources `R9B` from a session-derived
application byte, but `0x573500` overwrites its saved input before reading or
escaping it; it cannot be used as a network-client signal at this candidate.
The fifth stack byte controls a clear-helper branch, but its semantic name is
still unknown. One direct caller is in `cGcApplicationDeathState::Update`, so a
global hook can observe a death-state load as well as other state paths. Local
save-load behavior, all return paths, callback timing and runtime safety remain
unverified; do not approve the profile from this mapping alone.

Reproduce the direct caller scan with the pinned Capstone 5.0.9 environment:

```text
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x573500 --context 10
```

The scan decoded 52,110,272 bytes in `.pdata` ranges, skipped zero ranges and
found four direct calls. Resolving the chained parent used the exception
directory's `UNWIND_INFO`: follow the `RUNTIME_FUNCTION` after the aligned
unwind-code array whenever flags contain `UNW_FLAG_CHAININFO`, validating the
parent's begin, end and unwind RVA against `.pdata`. The eight ranges rooted at
`0x573500` are `573500–573577`, `573577–57359A`, `57359A–5735AA`,
`5735AA–5786A0`, `5786A0–5789DB`, `5789DB–57953A`, `57953A–579A6F` and
`579A6F–579B50` (hex RVAs).

## Caller-anchored summon-path candidates (partial)

A focused decode of the unique 7.06 `cGcQuickActionMenu::TriggerAction`
candidate at `0x1531E00` now gives a consistent path for the queued-slot
functions. These are exact-build static candidates, not an approved profile:

| 7.05 source role | 7.06 candidate | Exact-build evidence | Status |
| --- | ---: | --- | --- |
| `QueuePet` hook | `0x1475790` | `TriggerAction` call `0x1532719` passes the owner at `RCX` and selected item slot at `EDX`. The candidate stores the slot at owner `+0x6020`, reads the companion table at application `+0xE10D0`, and indexes entries with stride `0x24A0`. The 7.06 player-update candidate also reads and processes `+0x6020`. | STATIC-CORROBORATED |
| `CanSummon` gate | `0x1474F10` | `TriggerAction` call `0x15326F7` passes owner at `RCX` and selected item slot at `EDX`; the caller checks its `AL` result. The body uses the companion table at application `+0xE10D0` and calls `0x508290` and `0x50A520`. | STATIC-CORROBORATED |
| `OwnedPetEligible` / `services.owned` | `0x508290` | Directly called by `0x1474F10` with the companion table in `RCX` and slot in `EDX`. The same leaf is called by owner-update root `0x508DC0` with the original owner object in `RCX` and its active slot in `EDX`. Its body checks supported location values at application `+0x57A584`, slot at most 29, a nonzero entry field at `+0x2370`, and a zero field at `+0x2488`, then returns a Boolean in `AL`. The old `0x508200` target is inside an instruction in this build. | STATIC-CORROBORATED |
| Player update hook | `0x144B3A0` | Unique `cGcPlayer::Update` signature match at a `.pdata` entry. Its body reads the pending slot at player `+0x6020`, checks for a negative sentinel, reads associated state at `+0x6024`, `+0x6028`, `+0x6070`, `+0x6078`, `+0x6088`, and `+0x608C`, then calls `0x1475890` to process the request. | STATIC-CORROBORATED |

This confirms a likely queue-to-update data path and maps several fields for
this exact executable. The owner-update hook and load-role candidate have
static caller/body support, but no 7.06 live behavior has been checked. All
menu hooks, menu resource globals, the binding-filter return site, the load
candidate's exact flag/local-player semantics, notification/UI side effects,
and remaining runtime fields are still unresolved.

## Placement and ownership-state leads

The exact-build direct-call scan found five callers of `0x14426A0`. It is a
`.pdata` function entry at `0x14426A0–0x14426D4` with adjacent exception ranges
continuing the method. Two callers sit in the companion-ownership update path:
`0x5091A5` and `0x5092FC`. Both pass the ownership placement object at
`owner + 0x1B9140` in `RCX`, the same scalar in `XMM1` and `XMM2`, and the hand
value in `R9D`. The callee consumes those register values, reads the local
player through application `+0x72C6F0`, and updates the passed placement
object. Three other callers use the same register shape for other placement
objects. This is a strong exact-build `RefreshPlacement` candidate with the
same ABI roles as the 7.05 helper; retain it as `ABI-CHECKED`, not as live
compatibility evidence.

The companion-update path also reads or writes the prior 7.05 fields
`owner + 0x1B9140`, `owner + 0x1B9300` and `owner + 0x1B937D` in ranges
`0x508DE0–0x50923E`, `0x50923E–0x50933F` and `0x509346–0x50996D`. A
`.pdata`-bounded scan found zero direct calls to `0x508DE0`; that address is a
chained code range, not the method entry. Its unwind `CHAININFO` points back
to the real entry at `0x508DC0`. The parent entry has the method prologue,
saves `RCX` as the owner context, and takes its delta time in `XMM1`. A direct
caller at `0x489661` in `0x489150–0x489DFE` passes `RCX = rsi + 0xE0260` and
`XMM1 = xmm6`, alongside calls that update neighboring subobjects with the
same delta. The entry then falls through into the chained ranges, whose code
uses the owner fields above. This makes `0x508DC0` a
`STATIC-CORROBORATED` owner-update hook candidate with the old
`void(owner, float)` ABI. It is not live-verified; keep the exact 7.05 profile
disabled until all other dependencies and runtime gates are resolved.

The unique `cGcPlayer::GetDominantHand` signature candidate at `0x14874B0`
has an entry at a `.pdata` boundary. Its body checks game-state conditions,
returns the 32-bit value at application `+0x30E7FC` in `EAX` on the accepted
path, and returns zero otherwise. The mangled name declares a virtual const
member, while the source service has no explicit argument. The body forwards
incoming `RCX` to helper `0x1C84D0` without first changing it; that helper's
exact entry uses only thread-local and global data and does not consume its
incoming `RCX`. This resolves the apparent hidden-`this` mismatch for the
source's no-argument machine call. A full `.pdata` direct-E8 scan found zero
callers of `0x14874B0`; this is only a direct-call negative and does not rule
out virtual or other indirect calls. The candidate remains static evidence,
not live verification.

The unique `cGcPlayerNotifications::AddTimedMessage` signature candidate at
`0x9BF7B0` is ABI-checked against the current `Notice` call shape. A direct
native call at `0x3BD8EB` in `0x3BD626–0x3BD9CC` sets the notification object
in `RCX`, text in `RDX`, duration in `XMM2`, colour in `R9`, and stack values
for the resource ID, resource handle, duration and trailing flags. The callee
stores those register inputs and reads the ID and handle from entry stack
offsets `+0x28` and `+0x30`, the float from `+0x40`, and three flag bytes from
`+0x48`, `+0x50` and `+0x58`. This agrees with the ten explicit arguments in
the current `Notice` declaration and call; the native caller also uses the
same application notification object at `+0x847BB0`. Windows DbgHelp's
`UnDecorateSymbolName` decodes the pinned NMS.py decorated-name record as only
eight explicit parameters, so that record conflicts with the exact-build body
and caller and is retained as a misleading lead. This static ABI mapping does
not verify live notification behavior or thread semantics.

## Binding-guard return-site lead

A `.pdata`-bounded call scan found 145 direct callers of the uniquely matched
7.06 `cTkInputPort::GetButton` at `0x2C298E0`. In the quick-menu address
neighborhood, function `0x15288D6–0x1529E81` contains two direct calls:
`0x15292A6` (return `0x15292AB`, fixed button ID `0x11E`, `R8D=0`) and
`0x15292F0` (return `0x15292F5`, button ID loaded from
`[r12+rsi+0x4A33378]`, `R8D=1`). A bounded decode of the latter path shows
that a true return is followed by reads of the menu depth at `+0xA050`,
selection indices at `+0xA088`, and the selected `0xE0`-byte item. The
validated QAM RTTI/vtable identity and this selected-item return path now
independently corroborate `0x15292F5` as the binding-filter return site;
`0x15292AB` remains an alternate input-handler lead. The live input-filter
effect and complete runtime safety remain unchecked.

The old 7.05 filter return `0x152739B` lies inside the 7.06 range
`0x1526240–0x15279DC`, but that range contains no direct call to the matched
`GetButton`. Do not reuse the old return address. The current site is
`STATIC-CORROBORATED` at `0x15292F5`; `0x15292AB` is retained only as a
rejected alternate for this filter role. The source and profile still use
only the approved 7.05 site pending the remaining mappings and a bounded live
control check.

Both candidate returns are in a chained `.pdata` range rooted at
`0x15286C0`; the old return `0x152739B` is in the separate root `0x1526240`.
The root relationship is established by the exact-build `UNW_FLAG_CHAININFO`
records. Continue treating the two return RVAs as callsite candidates, not
function entries.

## Quick Action Menu root and caller pass

A follow-up pass resolved unwind parents for the old quick-menu hook RVAs
before interpreting their containing ranges. It also scanned all 52,110,272
bytes in `.pdata` ranges once for direct calls to the resulting candidate
roots, using Capstone 5.0.9. This corrects several containment-based leads:

| 7.05 source role | 7.06 old-RVA containing range and root | Caller/body evidence | Status |
| --- | --- | --- | --- |
| `MenuConstruct` | Old `0x143B720` is in `0x143B680–0x143B789`; root `0x143B680` | The root copies four 16-byte chunks (64 bytes total) from `RDX` into a vector at `RCX`, increments its count, and has one direct caller at `0x1424DAA`. This is not the mod's 224-byte menu-item constructor; replacement candidate `0x143D5D0` is mapped below. | OLD ADDRESS REJECTED; REPLACEMENT STATIC-CORROBORATED |
| `MenuSelect` | Old `0x1518EF0` is in chained range `0x1518D9F–0x1519058`; root `0x15182A0` | The old caller at `0x15173C3` has an incompatible string/output contract. Replacement leaf `0x151ADB0` checks depth/index/vector bounds, writes the selected index, and has three QAM `TriggerAction` callers with `(menu+0xA050, depth, index)`. | OLD ADDRESS REJECTED; REPLACEMENT STATIC-CORROBORATED |
| `MenuResources` | Old `0x1524330` lies in root `0x1524230–0x152443C` | Three direct callers pass four register arguments; the body is an unrelated four-argument helper. Replacement `0x1526240` is called from QAM setup with `RCX` at the nested QAM child; it loads `QUICKMENU/SUMMONPET.DDS` through the native resource manager and stores the handle at child `+0xA104`. | OLD ADDRESS REJECTED; REPLACEMENT STATIC-CORROBORATED FOR RESOURCE INITIALIZATION; POST-RETURN LIFECYCLE NOT LIVE-VERIFIED |
| `MenuBuilder` | Old `0x15282B0` is in chained range `0x1527BDD–0x1528568`; root `0x1527BD0` with chained body through `0x15286BB` | The root and chained body initialize many vector/container members at `+0xA098` and later offsets. Its only direct caller at `0x924D67` passes `RCX=rdi+0x116B10` from another initialization sequence, not `(menu, render)`. Replacement candidate `0x152A1C0` is mapped below. | OLD ADDRESS REJECTED; REPLACEMENT STATIC-CORROBORATED |
| `MenuLabel` | Old `0x152C7D0` is in chained range `0x152B394–0x152E6D1`; root `0x152A1C0` | Old entry is not reused. RTTI-backed `cGcQuickActionMenu` vtable slot 9 at `0x153C0C0` reads the selected QAM item and formats its localized label into the primary output buffer passed in `RDX`, with a 256-byte bound. The method clears one byte through its original `R8` argument, whose role and caller setup remain unresolved. | OLD ADDRESS REJECTED; SLOT-9 LABEL-OUTPUT METHOD STATIC-CORROBORATED; CALLER/R8 OWNERSHIP NOT CHECKED |
| `MenuConfirm` | Old `0x153A770` is in `0x1534D78–0x153B5B0`, chained to root `0x1531E00` | The same root is the unique `cGcQuickActionMenu::TriggerAction` signature candidate. The old target is not a separate function entry in this build; replacement candidate `0x153C680` matches QAM vtable slot 6 and selected-item Boolean behavior. | OLD ADDRESS REJECTED; REPLACEMENT STATIC-CORROBORATED |
| `MenuAppend` | Old `0x153CF40` is in chained range `0x153CCCA–0x153D9B2`; root `0x153C840` | Three direct callers exist. The root mutates an item action and returns a Boolean in `AL`; two menu-area callers pass a vector-like header plus a separate `R8` pointer and an `XMM1` value. This does not match the old `(header, incoming) -> pointer` append helper; replacement `0x153EE50` is mapped below. | OLD ADDRESS REJECTED; REPLACEMENT STATIC-CORROBORATED |

The unique `TriggerAction` root `0x1531E00` has three direct callers. Two are
inside `0x153B5B0–0x153BE52`; they pass the selected `0xE0`-byte item and a
Boolean and test `AL`. The remaining caller is at `0x15407A7`. This supports
the existing static `TriggerAction` candidate, but does not restore a separate
confirmation entry or establish a QAM vftable.

Reproduce each bounded direct-call query with the pinned tool and exact target
RVA; the multi-target pass in this follow-up used the same `.pdata` decode:

```text
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x143B680 --context 8
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x15182A0 --context 8
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1524230 --context 8
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1527BD0 --context 8
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x152A1C0 --context 8
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1531E00 --context 8
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153C840 --context 8
```

The `.pdata` parent was resolved from the chained `RUNTIME_FUNCTION` stored
after the aligned `UNWIND_INFO` code array, validating begin/end/unwind fields
against the exception directory. These direct-call results do not include
indirect method-table calls.

## Remaining compatibility evidence

Beyond the partial summon path and load-role candidate above, many hook targets
still lack verified caller identity, argument/return semantics, independent
RTTI/vtable or data-flow anchors, field offsets, global pointers, thread
behavior, and local-player versus network meaning. The existing 7.05 report
records useful baseline evidence but is not proof for this executable.

The old ownership-update RVA `0x508D30` lies inside the 7.06 range
`0x5085D0–0x508DB1`, but this is not a replacement mapping. The exact-build
direct-call scan found a call to the range entry at `0x5085D0` from `0xA0F692`;
that caller passes the companion table at application `+0xE10D0` and consumes
the result as a Boolean. That evidence does not establish the old update-hook
role. Keep `0x508D30` unmapped rather than reusing the containing range. The
separate `0x508DC0` candidate above is supported by its own caller, ABI and
chained owner-update body evidence; proximity between these RVAs is not part
of that mapping.

## Handoff after the 9 October static pass

The input-filter search now has a stronger candidate return at `0x15292F5`
and an alternate at `0x15292AB`; neither is safe to install until its role is
independently confirmed. A static caller/body check mapped the placement
helper candidate to `0x14426A0` with the old argument roles. The owner-update
fields occur in chained ranges rooted at the actual entry `0x508DC0`, which a
manager update caller invokes with an owner subobject and delta time. This is a
statically corroborated `void(owner, float)` hook candidate; `0x508DE0` remains
an invalid standalone hook address. The string-reference pass exposed a
`cGcPlayerCreatureOwnership::Update(float)` lambda type name and a
`cGcPlayerStateData` reference, but neither establishes a hook target. The
first inspected block for the player-state reference passes the name to a
helper then enters repeated hash-like field processing; this is a misleading
load-hook lead until its caller/data flow proves otherwise. A subsequent
signature check uniquely matched `cGcPlayerState::cGcPlayerState` at
`0x572410`, confirming the old load RVA's containing entry is the player-state
constructor, not a load method. Its one direct caller at `0x2CEAF0` is inside
another constructor. The
`AddTimedMessage` helper at `0x9BF7B0` is ABI-checked by an exact native
callsite/body despite the contradictory NMS.py decorated name. The unique
`cGcQuickMenu` constructor at `0x2CA290` is a false lead for `MenuConstruct`:
it takes no explicit arguments, while the mod's constructor pointer passes
four. These observations narrow future searches without changing the exact
7.05 guard.

`NOT CHECKED` in this pass: live behavior and threading of the owner-update
candidate; a replacement for the load hook and the meaning of its
network/reset arguments; live notification behavior and thread semantics; the
Quick Action Menu class/vtable identity and builder, label, append,
confirmation, resource, and selection helpers; placement live behavior and
remaining global and object layouts; local-player versus network behavior; and
any 7.06 live scenario.

Next bounded actions: inspect callers/data flow around the
`cGcPlayerStateData` hash-like routine in `0x29F1C60–0x29F8A19` to confirm or
reject it as a load lead; map the Quick Action Menu update/filter call path and
its class/vtable identity; then finish the dependency and layout inventory.
Keep the source and profile unchanged until every required mapping and safety
gate is resolved.

## Handoff after the 9 October signature and RTTI follow-up

The load-hook candidate at `0x572410` is now positively identified as
`cGcPlayerState::cGcPlayerState`: the pinned NMS.py signature uniquely matches
that exact `.pdata` entry. `cGcPlayerState::LoadFromData` still has zero
signature matches. The constructor's direct caller at `0x2CEAF0` lies in
`0x2CEA60–0x2CF43A` and is itself a constructor. Do not hook `0x572410` or
reuse the old `0x572C40` address. The separate `SaveToData` signature matches
`0x57B4C0`; it is not a replacement for the missing load hook.

The `cGcPlayerStateData` string at `0x29F1CC3` belongs to
`0x29F1C60–0x29F8A19`. A `.pdata`-bounded direct-call scan found one caller,
`0x2A5E58A` in `0x2A5E50E–0x2A5E5B1`; that small caller performs hash-like
field processing and tail-calls another routine. This does not establish a
player save-load lifecycle callback, so keep it as an unresolved search anchor
and do not use it as a hook.

The exact-build image contains the `.?AVcGcQuickActionMenu@@` type-descriptor
name at RVA `0x515A458`. This 9 October scratch pass incorrectly subtracted
12 bytes and targeted `0x515A44C`; an x64 MSVC TypeDescriptor has a 16-byte
header, so its correct start is `0x515A448`. The zero-reference result from
the incorrectly targeted probe is invalid and is superseded by the validated
RTTI/vftable evidence in the 12 October handoff below. The existing
`0x15292F5` binding-filter return remains a candidate only.

Reproduction used CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.9, and the
pinned NMS.py data at commit
`b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`:

```text
python -B tools/native_signature_matches.py --exe "<verified Cosmos 7.06 NMS.exe>" --data-json "<pinned NMS.py data.json>" --name cGcPlayerState::cGcPlayerState --name cGcPlayerState::SaveToData --name cGcPlayerState::LoadFromData
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x29F1C60 --context 8
```

The first command returned one match each for the constructor (`0x572410`)
and `SaveToData` (`0x57B4C0`), and zero for `LoadFromData`. The second scanned
52,110,272 bytes in `.pdata` ranges, skipped zero ranges, and found one direct
call. The RTTI probe was a bounded scratch analysis, not a complete
enumeration of indirect references. Its descriptor offset was wrong; do not
reuse its negative vftable conclusion.

The 9 October raw-file probe located the decorated name at `0x515A458` but
used the wrong TypeDescriptor RVA (`0x515A44C`, subtracting 12 instead of 16).
Its zero-reference result did not validate a Complete Object Locator and is
superseded by the structured 12 October probe. The separate raw-file search
for absolute pointers to `0x15288D6`, `0x15292AB`, `0x15292F5` and `0x1531E00`
covered only those encodings; its negative result does not rule out indirect,
relative, relocated-at-runtime or dynamically constructed references.

`NOT CHECKED`: exact meanings of the load candidate's `R9B` and two stack
arguments; whether each caller is local-player or network state; all candidate
return paths beyond the bounded checks; indirect callers of `0x29F1C60`; Quick
Action Menu helper roles; any live menu or load behavior; and all 7.06 runtime
scenarios. The vtable itself was subsequently validated on 12 October; see the
current handoff below.

Next bounded action: trace the `0x573500` candidate's flag inputs and all four
callers to settle local-player/network and reset semantics, then check every
return path against the six-argument source ABI. In parallel, establish the
Quick Action Menu method table from verified data references or keep the
entire affected menu feature unmapped. Do not change the profile or native
targets until those dependencies and remaining compatibility gates are
resolved.

## Handoff after the 9 October load-callsite pass

The 7.06 load role now has a strong caller-anchored candidate at `0x573500`
despite a zero `LoadFromData` signature match. Four direct callers use the
same physical argument layout, status return and corresponding caller paths
as the 7.05 load hook. The chained function body reads the common save value
through `RDX+0x8980` and returns success in `AL`. This upgrades the role from
unmapped to a static candidate; it does not resolve the network/reset flag
meaning, every return path, or runtime safety. The constructor false lead at
`0x572410` remains rejected, and the profile/source remain unchanged.

`NOT CHECKED`: exact flag semantics, local-player/network behavior, complete
return-path analysis, live load behavior, and all remaining menu/runtime
dependencies. Next, establish those semantics from the four callsites and
callee dataflow, then continue the menu mapping and full dependency inventory.

## Handoff after the 9 October quick-menu root pass

Following `UNW_FLAG_CHAININFO` changed the interpretation of several old menu
RVAs. The former `MenuConstruct` target is inside a 64-byte vector append, the
former `MenuConfirm` target is inside the `TriggerAction` root, the former
`MenuAppend` target is inside a Boolean item-mutating function, and the
`MenuBuilder` range belongs to a container-initialization routine. Do not carry
those RVAs forward. At that stage, `0x152A1C0` was a stronger `MenuLabel`
candidate because six direct callers passed a menu and a second pointer while
the body accessed the known menu layout. The 12 October source-vector trace
superseded and withdrew that interpretation: `0x152A1C0` is the QAM source
builder. Do not use it as the label hook. `MenuSelect` and resource setup
still lack approved roles.
The last sentence in this 9 October handoff that left the class/vtable
unresolved was superseded by the corrected 12 October RTTI pass below. No
source or profile address was changed.

`NOT CHECKED`: indirect method-table calls; whether the candidate label root
has the exact old output-buffer semantics; a replacement builder, append,
constructor, confirmation or resource helper; the full binding-filter
behavior; live menu behavior; and remaining 7.06 runtime dependencies. Next,
locate the function that constructs/appends `0xE0`-byte menu items by tracing
the menu label and trigger paths, then find an independent confirmation and
method-table identity before changing any menu hook.

## Local public-package update

On 9 October 2026, the installed module was updated from
`0.10.1-native-test-teleport-candidate-trial` to the latest public package,
`0.10.2-native-test` (Nexus file 49469). The downloaded archive and its ASI
match the package manifest. The previous ASI was backed up privately and hash
verified. The installed `winmm.dll` already matched the package-approved
Ultimate ASI Loader hash and was left unchanged; all eight installed icons
already matched the package and were left unchanged.

The 0.10.2 package still supports only Windows/Steam Cosmos 7.05 build
25624745 and the 7.05 executable hash above. It therefore continues to refuse
the local Cosmos 7.06 executable; installing the latest public package does
not clear the version warning or enable the mod on build 25732212.

No 7.06 candidate was compiled or injected, and NMS was not started after the
update. There is no 7.06 live evidence for hook installation, UI behavior,
save loading, automatic summoning, or multiplayer. No 7.06 compatibility
profile or release package was approved.

## Decision

Keep build 25732212 refused by the exact-executable guard. Do not update the
profile hash alone or carry 7.05 addresses forward. Continue only after
reproducing the pinned research-tool environment, remapping every native
dependency against this exact hash, and recording the required review and
runtime evidence. If semantic or live evidence remains unavailable, leave
native integration disabled.

## Handoff after the 12 October RTTI and menu-layout pass

The official Hello Games release log still lists Cosmos 7.06 as the newest
patch; it has no 7.07 entry. The local Steam manifest still reports build
25732212, and `NMS.exe` still has file/product version 180836, size 88,560,712
bytes and SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. A
read-only `git ls-remote origin refs/heads/main` readback returned
`f7d97b61fcf152677d0d30de34f6c1b48675c436`, the baseline under review.

Correction to the 9 October probe: the decorated type name is at RVA
`0x515A458`, but the x64 MSVC TypeDescriptor begins 16 bytes earlier at
`0x515A448`, not 12 bytes earlier at `0x515A44C`. That off-by-four error
caused a false negative in the prior raw dword search. The reusable
`tools/native_rtti_vtable_probe.py` validates the descriptor, Complete Object
Locator, class hierarchy and executable method-pointer run. It found one valid
locator at `0x4B66FE0`, with a hierarchy for `cGcQuickActionMenu` and base
`cGcQuickMenuState`, and a vftable at `0x4A504E0` with 16 consecutive
executable slots. This confirms static class/vftable identity, not every
slot's semantics or runtime behavior.

Vftable slot 0 points to `0x15286C0`, a `.pdata` entry whose chained body
continues through `0x1529E99`. It calls the item mutator at `0x153C840` and
the label candidate at `0x152A1C0`, consistent with an update path, but does
not prove that this root is a safe replacement for the old builder hook.
Slot 6 points to `0x153C680`; its body checks menu depth, selection, vector
count/data and the selected item's action at `+4`, then returns a Boolean.
Because it occupies the same vtable slot as the 7.05 confirmation method,
this is a `STATIC-CORROBORATED` confirmation candidate, not an approved hook.
`0x152A1C0` remains a label candidate.

The QAM update root calls `0x1530D40` at `0x1528855` with `RCX` holding the
menu and `DL=1` on the observed branch. This method resets menu depth and
selection fields, clears the three vector counts and related selected indices,
updates a menu state field at `+0x2C0`, and returns a Boolean. It does not
construct or append menu items; reject it as the missing builder/append
replacement. This remains a static state-transition interpretation.

The old `MenuAppend` address `0x153CF40` resolves through unwind metadata to
root `0x153C840`. That root writes an action value of 5 at the existing item's
`+4` field and clears another item field at `+0x88`; it does not append to a
vector. Its three direct callers are `0x142449E`, `0x15286F3` and `0x1545F22`,
each passing item/member context. The nearby `0x153C7A0` routine instead
selects a menu context index and returns a pointer into the supplied menu
object; it is not an append.
The generic vector helper `0x2BF9A00` has 791 direct callers across the image
and is not a menu-specific hook. The QAM update body calls it at `0x1528FE7`
and `0x1529129` with item stride `0xE0`, consistent with vector storage
assignment/replacement but not a confirmed safe append point.

Reproduce the corrected RTTI probe with CPython 3.11.9 and pefile 2024.8.26;
it does not require Capstone:

```text
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcQuickActionMenu@@"
```

For the bounded direct-call queries, this run used CPython 3.11.9, pefile
2024.8.26 and Capstone 5.0.7 (the repository requirements file pins 5.0.9):

```text
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153C840 --context 10
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2BF9A00 --context 10
```

The first scan covered 52,110,272 `.pdata` bytes, skipped zero ranges and
found three direct callers. The second covered the same bytes and found 791;
its broad result confirms this is a heavily reused generic helper, not a
QAM-specific target. The RTTI script reported the exact executable SHA-256
above. These are static findings only.

The QAM update callsite and the `0x1530D40` body were decoded in bounded
`.pdata` windows with CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15286C0 --size 0x216
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1530D40 --size 0x127
```

The first window is the QAM vtable slot-0 root and contains the direct call at
`0x1528855`. The second is the exact `.pdata` entry for the Boolean menu state
transition. This tool reports the containing range but does not follow chained
unwind parents; review those separately for chained functions.

`NOT CHECKED`: whether QAM update builds the menu each frame or only under a
specific event; the lifecycle and idempotency of that update; the function
that constructs or safely appends a new `0xE0` item; selection, resource and
binding-filter semantics; load-candidate flag/local-player semantics; live
behavior; and all remaining native dependencies. Do not replace the old
builder hook with the update method or generic vector helper without resolving
those questions. Keep the 7.05 profile and source guard unchanged, and keep
the 7.06 feature refused.

Next bounded action: trace the `0x15286C0` update path's calls and vector
inputs to identify the exact item-construction/append routine and prove when
it runs, while mapping the remaining vtable slots against their callers and
the 7.05 roles. Then continue the per-target ABI/layout audit and settle the
load candidate's two stack flags and `R9B`. Any proposed native change still
needs the documented review, offline checks and exact-build live evidence
before profile approval or packaging.

### Handoff after the 12 October pattern-search rule review

The official Hello Games release log was rechecked: Cosmos 7.06 remains its
newest listed patch, with no 7.07 entry. The [Nexus mod page](https://www.nexusmods.com/nomanssky/mods/4579)
was also checked: its listed public package remains `0.10.2-native-test`,
last updated 3 October. That is the public mod package identity, not the game
release or a 7.06 source port. The local `NMS.exe` SHA-256 still
matches `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`,
and a read-only remote `main` check still returns
`f7d97b61fcf152677d0d30de34f6c1b48675c436`. No native source, compatibility
profile or package changed in this work period.

To make future update work repeatable, `AGENTS.md` now requires the
[NATIVE-PATTERN-PLAYBOOK](NATIVE-PATTERN-PLAYBOOK.md) on every executable or
native-dependency change. The playbook defines exact cache inputs, the source
dependency inventory, bounded signature/RTTI/caller/string/layout passes,
zero/single/multiple/interior-match dispositions, per-role evidence fields,
and the mandatory dated handoff in both the reusable map and this report.
The rule specifically prevents a unique byte match, a missing match or a
plausible nearby RVA from being treated as a verified mapping.

This review consolidated previously recorded 7.06 results; it did not rerun
the signature or caller scans. The successful reusable methods are the pinned
NMS.py symbol pass, caller-anchored discovery when `LoadFromData` had zero
signature matches, chained `.pdata` parent resolution, and fully validated
RTTI/vtable parsing. Documented dead ends include old-RVA containment,
subtracting 12 instead of 16 for the x64 MSVC TypeDescriptor, treating
`0x153C840` as an append helper, treating the broadly used `0x2BF9A00` helper
as menu-specific, and interpreting `0x1530D40` as a builder. Exact build/hash
scope and reproduction detail are retained in the earlier handoffs and the
playbook.

`NOT CHECKED` in this work period: new executable scans, the actual QAM item
constructor/safe append point and its lifecycle, all remaining vtable-slot
roles, load-candidate flag/local-player semantics, live behavior and remaining
native dependencies. Next bounded action: trace the `0x15286C0` path to the
function that constructs and appends a `0xE0`-byte item; prove its callers,
argument layout, vector effect and execution timing. Use the playbook ledger
for every attempted pattern and retain the exact-build refusal until all
source dependencies and acceptance gates are resolved.

### Handoff after the 12 October QAM data-flow pass

The exact executable hash remains
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
A reusable read-only helper, `tools/native_pdata_function_group.py`, now
resolves the containing `.pdata` entry to its `UNW_FLAG_CHAININFO` root and
lists the complete group. On this build it reports three ranges for root
`0x15286C0`: `0x15286C0–0x15288D6`,
`0x15288D6–0x1529E81` and `0x1529E81–0x1529E99`. This replaces a scratch
query that first used incorrect quoting for the `No Man's Sky` path and then
compared the root tuple incorrectly. Those two scratch results were tool
errors, not evidence that the function group was absent. The helper now emits
the exact executable hash and validates that parent records exist.

The expanded bounded window at `0x1528F80` confirms the QAM update copies the
current menu vector into a temporary vector at `render + 0x610`: `RCX` is that
destination header, `RDX` is the source data pointer from the menu depth's
vector, `R8D` is its count and `R9D` is the `0xE0` item stride. The call at
`0x1528FE7` enters the generic vector helper `0x2BF9A00`; its 791 direct
callers and this copy direction keep it classified as a shared storage
helper, not a safe menu append hook. The larger context confirms the stride is
in `R9D`; the stack argument `0x10` is a separate parameter. Do not read a
truncated call-site window and mistake one stack argument for the element
stride.

Further bounded windows show `0x1530AC0` reads menu depth and selected indices,
checks action/input state and updates navigation fields; reject it as the
missing item constructor or append function. The inspected body at
`0x152E6E0` reads the selected item using the `0xE0` stride, but its full role
and the other two update calls at `0x15288B3` and `0x15288C9` remain
unverified. None of these results identifies a safe new hook point.

Reproduce the chained-range grouping with CPython 3.11.9 and pefile 2024.8.26:

```text
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15286C0
```

The bounded code windows used CPython 3.11.9, pefile 2024.8.26 and Capstone
5.0.7:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1528F80 --size 0x90
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1530AC0 --size 0x100
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153B5B0 --size 0x80
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153BE60 --size 0x80
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152E6E0 --size 0x100
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2BF9A00 --size 0x240
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2BF9A00 --context 8
```

The `native_function_disasm.py` helper prints a bounded byte window and the
`.pdata` range containing its starting RVA; windows for `0x153BE60`,
`0x152E6E0` and `0x2BF9A00` extend beyond that one range. Interpret only bytes
within confirmed ranges unless the containing function group has been
resolved. The direct-call scan covered 52,110,272 `.pdata` bytes, skipped no
ranges and found 791 direct calls. No live behavior was checked.

`NOT CHECKED`: whether either remaining QAM update call builds or refreshes
items; the exact item constructor and safe vector append; complete semantic
roles of all vtable slots; selection/resource/binding-filter compatibility;
load-candidate flag and local-player semantics; live behavior; and all other
native dependencies. Next bounded action: resolve the other QAM update call
site `0x1529129` with its full register and stack setup, then trace the vector
source data into the function that creates new menu items. Keep the exact
7.06 guard closed and do not change the runtime profile from this pass.

### Follow-up after the 12 October chained-helper and second-call check

The reusable function-group helper confirms that `0x2BF9A00` itself has three
chained ranges: `0x2BF9A00–0x2BF9A5F`, `0x2BF9A5F–0x2BF9B8A` and
`0x2BF9B8A–0x2BF9B96`. Decoding those exact ranges resolves the earlier
truncated-window ambiguity. The helper uses `R9` as element size, allocates or
copies according to vector capacity, writes the requested count to the
destination header and returns its data pointer. It does not construct an
item or increment the source menu vector. This confirms it as a generic
vector copy/resize helper, not an append hook.

The second QAM call at `0x1529129` has the same `R8D=count` and `R9D=0xE0`
setup as the first call at `0x1528FE7`. It copies the next-depth menu vector
into a temporary header at `render + 0x518`; the first call copies the current
depth into `render + 0x610`. Both targets are renderer scratch vectors. The
`0xE0` stride therefore identifies the copied item shape but does not expose
the function that creates or appends a menu item.

One exploratory disassembly started at `0x15290D0`, which is not a confirmed
instruction boundary; its initial decoded bytes were invalid and were
discarded. Starting from the verified `.pdata` range boundary at
`0x15288D6` and filtering around `0x1529129` produced the valid sequence.
`native_function_disasm.py` does not reject mid-instruction start RVAs, so
future searches must begin at a verified boundary. No mapping conclusion was
drawn from the discarded window.

Reproduction used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7:

```text
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2BF9A00
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2BF9A00 --size 0x5F
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2BF9A5F --size 0x12B
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2BF9B8A --size 0xC
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15288D6 --size 0x15AB | Select-String -Pattern '0x1529129' -Context 24,2
```

The direct-call count for `0x2BF9A00` remains 791 across 52,110,272 decoded
`.pdata` bytes and zero skipped ranges. These results narrow the menu data
flow but do not identify its construction path.

`NOT CHECKED`: the producer of the menu's source vector, the exact item
constructor and safe append point, other update-call roles, all remaining
vtable methods/dependencies, live behavior and load-candidate semantics.
Next bounded action: trace the producer and consumers of the QAM menu vectors
from `0x15286C0` and `0x152A1C0`, then locate the function that initializes a
new `0xE0` item and actually changes a source vector's count. Keep the 7.06
feature refused until that path and the remaining exact-build gates are
resolved.

### NMS.py menu-signature coverage check, 12 October 2026

The pinned external NMS.py checkout was re-read at commit
`b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`; its working tree is clean,
`tools/data.json` has SHA-256
`F311C9F54C0CCE199AB955A0E8DE2CFE2FCFB09274E557A2A27908C1B15BAF5F`, and
the repository carries an MIT license. Searching its symbol names for `menu`
or `quick` returns only `cGcQuickActionMenu::TriggerAction` and
`cGcQuickMenu::cGcQuickMenu`. On the exact 7.06 executable, the pinned
signature scan finds one entry match for each: `0x1531E00` and `0x2CA290`.
The latter remains rejected for `MenuConstruct` because its ABI does not
match the four-explicit-argument item constructor used by the mod. This
provider has no named builder, item-constructor or append signature; that
narrows the signature pass but does not establish that those functions are
absent. Continue with caller, RTTI, object-layout and vector-mutation anchors.

Reproduce the symbol inventory without printing third-party pattern bytes:

```text
py -3.11 -B -c "import json; from pathlib import Path; p=Path(r'<pinned NMS.py tools/data.json>'); rows=json.loads(p.read_text(encoding='utf-8')); print('\n'.join(sorted({r['name'] for r in rows if isinstance(r,dict) and any(x in r.get('name','').casefold() for x in ('menu','quick'))})))"
py -3.11 -B tools/native_signature_matches.py --exe "<verified Cosmos 7.06 NMS.exe>" --data-json "<pinned NMS.py tools/data.json>" --name "cGcQuickActionMenu::TriggerAction" --name "cGcQuickMenu::cGcQuickMenu"
```

The scan used CPython 3.11.9 and pefile 2024.8.26. These signatures are
discovery candidates only; role/ABI conclusions are in the earlier exact-build
tables. Keep third-party pattern bytes external and preserve the provider
commit, data hash, license, symbol names and bounded results in the ledger.

### Handoff after the 12 October QAM vtable-slot follow-up

The following observations use the same exact executable SHA-256 recorded at
the start of this report. They extend the validated 16-slot
`cGcQuickActionMenu` vftable probe but do not change the native compatibility
profile.

| Slot | Method RVA and exact range | Bounded static observation | Disposition |
| --- | --- | --- | --- |
| 8 | `0x153C000`, `0x153C000–0x153C0B3` | Checks manager input IDs `0x56` and `0x54`, menu depth and `menu+0x14==4`; returns Boolean. | Availability/state predicate candidate; not a builder. |
| 9 | `0x153C0C0`, chained ranges `0x153C0C0–0x153C0FD`, `0x153C0FD–0x153C24C`, `0x153C24C–0x153C5E4` | RTTI ties this method to `cGcQuickActionMenu` slot 9. It validates depth/selection, indexes the selected `0xE0` item, chooses localized text and writes the primary string through saved `RDX` with a 256-byte bound (`[RDX+0xFF]=0`). Entry clears one byte via original `R8`, then reuses `R8`; its semantic role is unknown. | LABEL-OUTPUT METHOD STATIC-CORROBORATED; VIRTUAL CALLER, OUTPUT CONSUMER AND R8 CONTRACT NOT CHECKED. Not builder evidence. |
| 10 | `0x153C5F0`, `0x153C5F0–0x153C67B` | Checks input IDs `0x17` and `0x18` and timer field `+0xA174`; returns Boolean. | Action/availability predicate candidate; not a builder. |
| 15 | `0x152A0E0`, `0x152A0E0–0x152A100` | Checks `EDX==4`, calls `0x152A100`, then returns Boolean. | Role unresolved; not builder evidence. |

These slot observations do not establish their complete callers, runtime
timing or behavior. Slots 1-5, 7 and 11-14 remain `NOT CHECKED` for semantic
roles. An exploratory raw decorated-type-name inventory exceeded the output
budget and was discarded; it supplied no usable result and must not be cited
as a zero-match scan. Future inventories should filter exact type-name
families, deduplicate and cap printed output.

The reviewed slot windows used CPython 3.11.9, pefile 2024.8.26 and Capstone
5.0.7. Resolve chained `.pdata` groups before decoding the corresponding
ranges. The reusable commands for this exact build are in the QAM slot
follow-up of `NATIVE-UPDATE-MAP.md`; these helpers emit/validate the executable
hash and range metadata. The interpretation above remains bounded static
evidence, not live proof.

`NOT CHECKED`: complete semantics and callers for these slots; semantic roles
for slots 1-5, 7 and 11-14; the item constructor and safe append point; menu
item lifecycle/idempotency; remaining native dependencies; load-flag and
local-player behavior; and in-game behavior. Next bounded action: trace the
QAM update and label/trigger paths until a function is shown to initialize a
new `0xE0` item and increase the source menu vector count, including its
callers, argument layout, full chained body and timing. Keep build 25732212
refused until all exact-build gates pass.

### QAM slot-9 label-output method and ABI boundary, 18 October 2026

On the unchanged Steam build 25732212 / executable SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`, the
RTTI-validated `cGcQuickActionMenu` vtable assigns slot 9 (`+0x48`) to method
`0x153C0C0`. The complete chained body has ranges `0x153C0C0–0x153C0FD`,
`0x153C0FD–0x153C24C` and `0x153C24C–0x153C5E4`. At entry, the method clears
one byte through the original `R8` argument, then saves `RDX` in `R14`. It
validates menu depth and selection, indexes the selected `0xE0`-byte item,
chooses localized text and constructs the primary output through that saved
`RDX` pointer. The body writes a terminator at offset `0xFF`, establishing a
256-byte primary output bound. The original `R8` value is not preserved as a
pointer; after its first-byte clear, `R8` is reused for scratch values and
helper arguments. Its semantic contract cannot be inferred from this method
alone.

This establishes the slot-9 label-output method more strongly than the prior
“likely label” description. It does not identify the real virtual caller,
prove which UI field consumes the primary string, or establish ownership,
capacity, lifetime or meaning of the original `R8` target. The source's old
`labelHook(void* menu, void* out)` type and 128-byte caption write do not match
the observed 7.06 method contract closely enough to reuse blindly. No source
hook or profile was changed.

Reproduction against the verified executable and existing RTTI/vtable probe:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0C0 --size 0x3D
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0FD --size 0x14F
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C24C --size 0x398
```

The slot-9 receiver shortlist remains a bounded negative, not proof that no
virtual caller exists. `NOT CHECKED`: actual slot-9 caller and its `R8` setup,
downstream output consumer, safe resource-ready callback, live binding-filter
effect, local-versus-network load semantics and all in-game 7.06 behavior.
The `MenuSelect` setter, resource initializer and binding-filter return site
are already statically corroborated; do not repeat those mappings. Keep 7.06
fail-closed. Next bounded action: use the proven QAM pointer flow to find an
actual slot-9 dispatch and track both output arguments across every
intervening call; separately resolve load-hook local/network semantics and
continue the exact-source dependency ledger.

### Load-role candidate flag and callsite recheck, 18 October 2026

Rechecked the caller-anchored candidate `0x573500` against the unchanged exact
7.06 executable hash. Its entry stores the first three physical arguments
(`RCX`, `RDX`, `R8`) and the fourth argument byte (`R9B`) in its frame, then
uses the object from `RDX` to read `+0x8980` at `0x5736D4`, consistent with the
common-save input used by the existing 7.05 load hook. The unwind group has
eight ranges rooted at `0x573500`. The fifth physical argument is read at
`0x578B2F`; when it is zero the method performs a helper/setup call sequence
ending at `0x6019F0`, and when nonzero it branches over that sequence. This
confirms that the fifth argument affects a path but does not establish its
meaning as a reset flag.

The exact direct-call scan still returns four callers. Their physical setup is
consistent but does not identify network semantics: at `0x2E088F`, `R9=0`,
fifth argument `1`, sixth argument from `R15B`; at `0x48EECC`, `R9=0`, fifth
from `DIL`, sixth from `BL`; at `0x48F983`, `R9=0`, fifth from `R13B`, sixth
from `BL`; and at `0x4906BD`, `R9` comes from `[RDI+0x4BE6A0]`, with both stack
arguments zero. The callers therefore do not justify assigning `R9` the
source prototype's `network` meaning or assigning the fifth parameter a
`resetting` meaning. The candidate remains a caller-anchored static role
candidate, not an approved replacement hook.

Reproduction against Steam build `25732212` and SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`:

```text
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x573500
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x573500 --context 12 --limit-per-target 10
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x573500 --size 0xA8
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x578AE0 --size 0x90
```

`NOT CHECKED`: semantic labels for the fourth, fifth and sixth parameters;
which caller paths are local-player or network state; all indirect callers;
complete return-path and side-effect analysis; and live loading behavior.
Next bounded action: identify the object/class behind
`global+0x941C70+0x1A8` and the meaning of its `+0x41C` predicate, then trace
which load-candidate paths are local or network without inheriting names from
the old typedef. Keep the 7.06 profile disabled.

### Session-derived load-candidate flag lead, 18 October 2026

The exact-hash fast displacement pass for `+0x4BE6A0` decoded all
`52,110,272` `.pdata` bytes with zero skipped ranges and returned seven
operand hints. These were treated as a shortlist and checked in root-aligned
disassembly. Constructor root `0x487CE0` clears the 16-bit field at
`0x487D1B`. The relevant writer is not a function entry at `0x495675`; it is
an interior chained range under unwind root `0x495640`, whose 14-range group
contains the byte store `[R12+0x4BE6A0]=BL` at `0x4956B8`. A direct-call scan
of the interior target `0x495675` returned zero, which was a bounded query of
the wrong entry. Repeating against the unwind root found one direct caller,
`0x4955F8` in chained range `0x4955B4–0x495623`, under root `0x495560`.

That caller reads the application pointer through the RIP-relative global at
`0x4955AD` (data RVA `0x6E8D708`), then the member at `+0x941C70` and its
pointer at `+0x1A8`; it checks that object's `+0x418` field for value 4, calls
its vtable slot `+0x40`, and derives `R9B`
from the return and byte `+0x41C`. It passes that Boolean to root `0x495640`,
which stores it in the `+0x4BE6A0` field. This is a concrete session-linked
producer path and strengthens the earlier `PlayfabSession` lead. It still
does not prove that the global base is a specific matchmaking manager, name
the `+0x41C` predicate, or show that the Boolean means “network”.

The 7.06 load-role candidate's caller at `0x4906BD` reads the same
`[RDI+0x4BE6A0]` field into `R9`. The other three direct callers pass `R9=0`.
This makes the fourth physical argument session-derived in one observed path,
but does not yet distinguish local/network semantics. Root-aligned disassembly
verified all seven fast-scan operands (two writes and five reads); the meaning
of the field remains unresolved.

Reproduction against the verified exact executable:

```text
py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x4BE6A0 --fast-candidates --limit-per-offset 100
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x487CE0 --size 0x250
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x495675
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x4955B4 --size 0xA0
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495675 --context 10 --limit-per-target 20
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495640 --context 10 --limit-per-target 20
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x48FD90 --size 0xA0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x48FEC0 --size 0x90
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x490670 --size 0x90
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x497A6C --size 0x58
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x4A8EB0 --size 0x80
```

Reusable correction: resolve a candidate interior RVA to its full unwind root
before scanning callers. The zero direct-call result for `0x495675` was not
evidence of no caller; its root `0x495640` has one direct caller. Continue from
the exact root and preserve the `global+0x941C70+0x1A8` relationship as a
strong lead, not a proved class identity. `NOT CHECKED`: the manager identity,
`+0x41C` meaning, indirect paths, network/local distinction and live load
behavior. Keep the 7.06 profile disabled.

### Follow-up on QAM helper roles and interrupted caller scan, 12 October 2026

Further work used the same executable SHA-256 and did not change source,
profile or package files.

The update call target `0x153B5B0` has one `.pdata` range,
`0x153B5B0–0x153BE52`. Its bounded call list includes label method
`0x152A1C0`, navigation/reset methods `0x151ACD0` and `0x1530D40`, and trigger
method `0x1531E00`. This call-list pass is not full body semantics and does
not identify item construction.

The adjacent target `0x153BE60` resolves to a three-range chained function:
`0x153BE60–0x153BE80`, `0x153BE80–0x153BFBB` and
`0x153BFBB–0x153BFC8`. Its bounded full-group decode scans the menu's
`0xE0`-stride item vector for a pending action, may update selection, calls
state-reset/label helpers and clears menu counts/flags. It does not append an
item or increment a source vector count; classify it as an action/selection
state handler, not the missing item constructor.

Vtable slot 15 (`0x152A0E0–0x152A100`) directly calls `0x152A100`. The latter
has no `.pdata` entry, but the call target gives a bounded entry point. Its
code reads the selected item through the menu depth/vector and `0xE0` stride,
checks the action field at `+4` against action 4 and a bit mask, and returns a
Boolean. This supports a selected-action predicate candidate. The standalone
unwind identity and other callers are not established; it does not construct
or append an item. At this checkpoint, `0x152A1C0` was still described as a
label/output path. The later 12 October source-vector trace superseded that
interpretation and identified it as the QAM source builder; see the dated
correction below.

An extra whole-image caller scan for `0x152A1C0` was stopped after more than
60 seconds without output. The prior exact-build report already records six
direct callers, so the repeated scan was redundant. Mark this new attempt
`NOT CHECKED`; it gives no zero-match evidence. The current one-target xref
scanner decodes roughly 52 million `.pdata` bytes per run. Check the ledger
first and batch new targets if another broad pass is necessary.

Reproduction used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7:

```text
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153B5B0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153B5B0 --size 0x8A2 | Select-String -Pattern '\bcall\b'
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153BE60
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153BE60 --size 0x168
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152A100 --size 0x56
```

`NOT CHECKED`: exact item constructor and safe append point, vector producer,
remaining vtable-slot roles/callers, complete lifecycle and thread behavior,
other callers/unwind identity of `0x152A100`, live behavior, load semantics and
the other native dependencies. Continue tracing until both initialization of
a new `0xE0` item and an increase to the source menu vector count are shown.
Keep the exact-build guard closed.

### Handoff after the 12 October conditional QAM update-path check

The exact executable remains build 25732212 with SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
This pass corrects and extends earlier static interpretations; no source,
profile or package was changed.

The slot-0 QAM update root `0x15286C0` calls `0x153B5B0` at `0x15288B3` when
`menu+0xA170 != -1`, passing `RCX=menu` and `RDX=render`. Its alternate branch
calls `0x153BE60` at `0x15288C9` with the same arguments when
`menu+0xA164 != 0`. This supersedes the earlier handoff that left both call
roles wholly unverified; it does not approve either as a replacement hook.

`0x153B5B0` is one `.pdata` range, `0x153B5B0–0x153BE52`. Its body obtains a
context pointer through `0x153C7A0`, compares five `0xE0`-stride records with
menu vectors, clears menu counts/selections on a mismatch, and calls label /
navigation paths. Its later loop copies or initializes `0xE0`-byte records
through a pointer derived from the context result. The destination relationship
to the render argument and source QAM vector remains unproven. No confirmed
source-vector count increase or safe append call was found in this pass. Keep
`0x153B5B0` as the strongest conditional menu-update/builder candidate, with
the role still unresolved.

Correction to prior wording for `0x153C7A0`: a bounded decode shows it tests
global context state and returns a pointer inside the supplied menu object at
`menu + 0x2D0 + context * 0x3480`. The previous “owner/local-player resolver”
description was imprecise and is superseded; full callers and context meaning
remain unverified. The separate three-range method `0x153BE60` scans menu
items at stride `0xE0`, adjusts selection/state and clears counts. It does not
append a new item. The direct call target `0x152A100` used by slot 15 checks
the selected item's action at `+4` against action 4 and a bit mask, then
returns Boolean; this supports a predicate candidate, not item construction.

A bounded raw decorated-name inventory (`.?AV` + 1–128 non-NUL bytes + NUL)
found four case-insensitive `quick` matches: `cGcQuickActionMenu`,
`cGcQuickMenuState`, an unrelated QuickWarp notification type and a helper
type mentioning `QuickMenuRenderState`. It found no dedicated QAM item class
name; that does not establish that a constructor or item-building function is
absent. The first inline regex was over-escaped and printed zero; discard that
false result. The reusable name-only helper now caps, deduplicates, strips the
terminator and reports the executable hash:

```text
py -3.11 -B tools/native_rtti_name_inventory.py --exe "<verified Cosmos 7.06 NMS.exe>" --contains quick
```

The helper reported four unique names for the exact executable hash above.
This byte-name scan is not a structural RTTI result; the validated RTTI
evidence remains the separate vftable probe.

Reproduction of the function and caller findings used CPython 3.11.9,
pefile 2024.8.26 and Capstone 5.0.7:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15286C0 --size 0x216 | Select-String -Pattern '0x14153b5b0|0x14153be60' -Context 12,4
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153B5B0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153B5B0 --size 0x8A2 | Select-String -Pattern '\bcall\b'
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153B5B0 --size 0x8A2 | Select-String -Pattern '0x153bd30:' -Context 0,75
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C7A0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C7A0 --size 0x9D
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153BE60
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153BE60 --size 0x168
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152A100 --size 0x56
```

`NOT CHECKED`: exact ownership of the `0x153B5B0` destination, whether the
render pointer participates in its `0xE0` writes, source vector count changes,
the constructor and append roles, full caller/context semantics for
`0x153C7A0`, helper `0x142A3AAC0` and its ABI, remaining dependencies, live
behavior and the other acceptance gates. Next bounded action: trace the
`0x153B5B0` destination field-by-field, prove which object owns its writes,
and find a matching source-vector count increment before treating it as a
builder replacement.

### Follow-up on context and vector-depth helpers, 12 October 2026

The earlier `0x153C7A0` correction is now supported by its complete bounded
body: with menu in `RCX`, the helper chooses a context value from global state
and returns `menu + 0x2D0 + context * 0x3480`. It is a menu-internal context
resolver, not an owner-pointer resolver. The exact meaning and lifetime of
each context remain unverified.

The QAM update target `0x151ACD0` has no `.pdata` entry, but is a direct call
target. Its body at the confirmed call boundary checks the selected-index
field against the active vector count, resets invalid selection, and reduces
menu depth while inner vectors are empty. It reads counts and indices but does
not increase vector counts or append items. Classify it as depth/selection
repair, not construction.

The 7.05 builder contract is confirmed as `(menu, render)` and calls item
construction and append. The new 7.06 target `0x153B5B0` receives the same
register arguments at a conditional QAM callsite and operates on five
`0xE0`-stride records. That ABI resemblance is useful candidate evidence, but
its destination is derived through menu context state and no matching source
QAM vector count increment has been established. Do not promote it to the
builder role until destination ownership and append behavior match the 7.05
contract.

Reproduction, with CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7:

```text
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C7A0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C7A0 --size 0x9D
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x151ACD0 --size 0x63
```

`NOT CHECKED`: which render fields `0x153B5B0` reads or writes, ownership of
the context record destination, whether a later callee appends that record to
the QAM vector, context lifetime/thread, and remaining builder/constructor /
append dependencies. Next action: identify the source and destination bases
for one exact `0xE0` record through the complete `0x153B5B0` path and show the
count mutation that makes it visible to the renderer.

### Batched QAM caller and item-record helper pass, 12 October 2026

`tools/native_call_xrefs.py` now accepts repeated `--target-rva` values and
decodes the `.pdata` inventory once for all targets. A four-target pass over
the exact executable scanned 52,110,272 runtime-function bytes, skipped zero
ranges and reported the hash recorded above. It found one direct call each to
`0x153B5B0` (`0x15288B3`) and `0x153BE60` (`0x15288C9`), three to
`0x151ACD0` (`0x152889F`, `0x153B7B6`, `0x153BF52`), and fourteen to
`0x153C7A0`. Eleven of the latter are inside the chained QAM update body; two
are in `0x15406B4–0x1540AF6`. The same full-image scan now answers several
target questions in one pass; it took about two minutes, so continue to use
the existing caller ledger and batch only genuinely open targets.

Two functions in that update path have distinct roles. `0x151AB50–0x151ABD1`
compares two item records and returns Boolean. It checks action `+4`, fields
`+0x40`, `+0x50`, `+0x84`, `+0x88`, `+0x90`, and compares the string at `+0x44`.
It is an equality helper, not a constructor. `0x151ADD0–0x151AE81` initializes
one `0xE0` record followed by five more at the same stride in a `0x540` block;
it resets selected fields, initializes each string through `0x142A3AAC0`, and
sets default values. This is a bulk context initializer, not the mod's
four-argument single-item constructor and not a QAM vector append. The
context records provide a credible construction-related lead but do not yet
show how a new item becomes visible to the QAM renderer.

The new bounded RTTI name inventory and the batch xref mode were exercised
against the current executable hash. The name helper found four `quick`
decorated strings under its stated search shape; it is still only a raw byte
search. The multi-target xref command is reproducible as follows:

```text
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153B5B0 --target-rva 0x153BE60 --target-rva 0x153C7A0 --target-rva 0x151ACD0 --context 1
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x151AB50 --size 0x81
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x151ADD0 --size 0xB1
```

`NOT CHECKED`: whether any function safely appends a cached context record to
the menu's source vector; the exact role of `0x142A3AAC0`; the menu/render
ownership relationship; complete QAM item lifecycle/thread behavior; the
remaining native dependencies; and live acceptance. Next, compare each
context record write and vector header before/after `0x153B5B0` across its
full caller path, then prove a source count increase and the correct
one-item constructor/append contract before touching the profile.

### Address-form correction for the context string helper, 12 October 2026

The disassembler prints instruction locations as RVAs, while relative call
operands are shown as virtual addresses. A first `.pdata` helper query used
the call operand `0x142A3AAC0` as an RVA and failed; converting with image base
`0x140000000` gives RVA `0x2A3AAC0`. That RVA has no `.pdata` entry, but the
direct call boundary is valid. The bounded body at `0x2A3AAC0` writes the
64-bit sentinel `-1` to `[RCX]` and returns, with padding after the return.
Because `0x151ADD0` calls it with `RCX` pointing at item field `+0x44`, this is
a string/field initializer candidate, not the menu-item constructor. Keep the
wrong-address lookup as `TOOL ERROR`; it is not evidence of a missing
function.

The first callsite filter also searched for the target RVA text
`0x153B5B0`, although Capstone displays that operand as VA
`0x14153B5B0`. It returned no lines and was discarded. Searching the emitted
VA text within the verified root range exposed the two call sites. For future
filters, distinguish instruction-address RVAs from call-target VAs; convert
only when passing a target to tools that require an RVA.

Reproduction:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x151ADD0 --size 0xB1
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2A3AAC0 --size 0x8
```

### Caller coverage for context-item helpers, 12 October 2026

A second batched direct-call scan used the same exact executable hash,
decoded 52,110,272 `.pdata` bytes and skipped no ranges. It found one caller
for `0x151AB50` at `0x15296EB`, and two for `0x151ADD0` at `0x1529709` and
`0x1529729`; all three are inside the chained QAM update function. This
confirms the equality and bulk-initialization helpers' immediate call scope.

The adjacent chained function `0x151AE90` is a separate lead: it computes
distances from a vector of pointers and returns the nearest candidate. It has
one direct caller at `0x151B18C` in `0x151AFCB–0x151B87C`, outside the QAM
update chain. Treat the adjacency as a false lead for menu construction.

```text
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x151AB50 --target-rva 0x151ADD0 --target-rva 0x151AE90 --context 0
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x151AE90
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x151AE90 --size 0xFC
```

The scan does not resolve indirect references or runtime use. `NOT CHECKED`:
whether the six context records are ever transferred into the source QAM
vector, whether the context helper has other indirect users, and all live
menu lifecycle behavior.

### Render-item context association in the chained update, 12 October 2026

A further bounded window inside the slot-0 update's chained range shows two
existing render vectors: data at `render+0x618` with count at `render+0x614`,
and data at `render+0x520` with count at `render+0x51C`. The first loop walks
the existing `0xE0`-byte render items and compares action/string/layout fields
against each context record across `0x3480` bytes of context entries. When a
match is found, `0x1529D87` writes the matching context index to the existing
item's `+0xD8` field. A parallel loop does the same for the second render
vector at `0x1529E47`, then calls the navigation method `0x1530AC0` at
`0x1529E64`. These are metadata updates to items already in the render
vectors; they are not appends and do not increment a vector count.

This narrows what the QAM update does after context-item initialization, but
still does not identify who constructs and appends new menu entries. Do not
mistake the `+0xD8` item-field write for a vector header mutation.

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15288D6 --size 0x15AB | Select-String -Pattern '0x1529d72:|0x1529d87:|0x1529d9e:|0x1529e32:|0x1529e47:|0x1529e64:' -Context 12,36
```

`NOT CHECKED`: the function that initially fills the two render vectors, any
later append after this association pass, and its exact item-construction and
thread/lifecycle contract. Continue from the vector producers, not this
metadata write.

### QAM offset-write scan and Quick Menu constructor false lead, 12 October 2026

The exact executable remains Steam build 25732212 with SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. A
read-only displacement scan decoded 52,110,272 `.pdata` bytes and skipped no
ranges. With the write filter and an 80-result cap (above each result count),
it found 14 operands at `+0xA05C`, 11 at `+0xA06C` and 13 at `+0xA07C`.
Relevant QAM writes include the update root `0x1528866/0x1528876/0x1528886`,
the reset path `0x1530DD4/0x1530DE8/0x1530DFC`, the conditional helper
`0x153B5B0` and its chained body, and the action-state body `0x153BE80`.
The remaining results include stack-local noise and were not treated as
object-field evidence. A prior unfiltered scan printed only the first 20
`+0xA05C` hits; that truncated output is discarded and is not a complete
negative result.

The `+0xA06C` write at `0x2CA7BB` was a new candidate. Its full `.pdata` entry
is `0x2CA6D0–0x2CAA96`. The function initializes a repeated Quick Menu layout,
then compares the field at `+0xA06C` with zero and writes zero only when the
old value is nonzero. A batched direct-call scan found one direct caller, at
`0x2CA3FE` in `0x2CA290–0x2CA6CF`, the pinned `cGcQuickMenu::cGcQuickMenu`
constructor. The operation is a constructor-time count reset, not an append
or item producer. This candidate is rejected for the missing builder role.
The scan of generic initializer `0x1AE390` had 229 direct callers and is too
broad to provide a useful menu-role anchor by itself.

Reproduce the bounded scan with the recorded local environment (CPython
3.11.9, pefile 2024.8.26, Capstone 5.0.7):

```text
py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0xA05C --offset 0xA06C --offset 0xA07C --access write --limit-per-offset 80
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2CA6D0 --size 0x3C6
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2CA6D0 --target-rva 0x1AE390 --context 6
```

The disassembly is static and the call scanner reports direct calls only; it
does not resolve indirect construction paths or establish runtime ownership.
`NOT CHECKED`: whether the three QAM-related offsets belong to the source
vector headers, which non-reset path increases their counts, and whether the
conditional helper `0x153B5B0` reaches such a producer. Next bounded action:
trace the register/object base for each QAM count write in the known update,
reset and conditional-helper ranges, then compare any non-reset mutation with
the 7.05 builder's one-item initialization and append contract. Require a
proved source-vector count increase before selecting a hook or changing the
exact-build profile.

### Count-field read coverage, 12 October 2026

A matching read-filtered scan of those three displacements decoded the same
52,110,272 `.pdata` bytes and skipped no ranges. It found 55 reads at
`+0xA05C`, eight at `+0xA06C`, and eight at `+0xA07C`. These occur in the QAM
slot-0 update and chained body, label/selection/trigger paths, state reset,
conditional helper and constructor. The 7.05 adapter's known vector layout
starts at `menu+0xA058`, with a 32-bit count four bytes into each 16-byte
header; the 7.06 readers at the corresponding count displacements support the
same menu-vector interpretation. This is field-role corroboration, not an
append proof: the reads are bounds/selection checks, and the write scan still
shows no confirmed producer that increases a source-vector count.

Reproduce with the same exact executable and local tool environment:

```text
py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0xA05C --offset 0xA06C --offset 0xA07C --access read --limit-per-offset 80
```

Next bounded action: trace only the pointer/capacity fields beside these count
reads through `0x153B5B0` and its vector-helper call arguments; match the
destination to the menu object used by label/trigger paths. A valid append
candidate must mutate the same source vector and increase its count after
initializing one `0xE0` item. The scan does not resolve indirect calls and
does not replace that object-identity check.

### Conditional-helper tail is a context snapshot, not a builder

A follow-up decode of `0x153B5B0–0x153BE52` resolves its apparent item-writing
tail. The function calls `0x153C7A0` to select a context block, computes its
`0x540`-byte stride, then reads the active menu depth and selected indices.
For each of the three menu depths, it reads the count at
`menu+0xA05C+depth*0x10` and the data pointer at
`menu+0xA060+depth*0x10`; the selected index is in the matching `+0xA088`
array. The tail copies the currently selected `0xE0`-byte item into one of
five fixed context-cache records at `context-block+0xE0+slot*0xE0`, or
initializes a default cache record when the selected depth has no valid item.
It returns a Boolean. These writes land in the context cache, not the source
menu vector, and do not increase a source-vector count. This rejects the
remaining builder interpretation for `0x153B5B0` and explains why its body
contains many `0xE0` copies and string initialization.

The same function clears count and selection fields while repairing stale or
invalid menu state. That accounts for its `+0xA05C/+0xA06C/+0xA07C` writes;
they are reset paths. Keep the cache destination and source menu vectors as
separate objects in future data-flow notes. The next search should follow the
QAM update's actual vector-copy call arguments and identify a constructor or
append caller whose destination resolves to one of the source vector headers.
Do not spend another full-image pass on `0x153B5B0` as an append candidate.

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153B5B0 --size 0x240
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153BD02 --size 0x150
```

This is static register/data-flow evidence. `NOT CHECKED`: indirect calls,
runtime cache ownership and mutation timing, the exact safe one-item
constructor/append pair, and live menu behavior.

### QAM builder, item constructor and vector appender, 12 October 2026

The exact input is the Cosmos 7.06 Steam executable recorded above, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. The
local command environment was CPython 3.11.9, pefile 2024.8.26 and Capstone
5.0.7. The build-specific source base remains
`f7d97b61fcf152677d0d30de34f6c1b48675c436`; the native source and profile are
still unchanged.

The broad vector shortlist used stride `0xE0` and count displacement `+4`.
It scanned 52,110,272 bytes in `.pdata` ranges and skipped zero ranges. The
first output contained 30 functions; an earlier print-format defect showed
instruction VAs instead of RVAs. That display issue was corrected, and the
bounded scan was rerun against the same executable and search parameters. The
scan is a candidate generator only: it does not track register/object
identity, source versus render vectors, direct callers or whether an append
actually occurs. The exact corrected output is summarized here rather than
checked in raw.

```text
py -3.11 -B tools/native_vector_stride_candidates.py --exe "<verified Cosmos 7.06 NMS.exe>" --stride 0xE0 --count-offset 4 --max-results 80
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcQuickActionMenu@@"
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x143D700
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1545EF0
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153EE50
```

Validated RTTI identifies `cGcQuickActionMenu` at vftable RVA `0x4A504E0`
with 16 executable slots; slot 0 resolves to the update entry `0x15286C0`.
That update resets the three QAM source-vector counts at menu offsets
`+0xA05C`, `+0xA06C` and `+0xA07C`, then directly calls `0x152A1C0` with the
menu in `RCX` and render pointer in `RDX`. The exact root and chained ranges
for the builder are `0x152A1C0–0x152B394` and `0x152B394–0x152E6D1`.
This establishes a direct QAM update-to-builder path and matches the old
builder hook's two-pointer call shape. It is static evidence; no update-hook
or builder-hook lifecycle, thread, reentrancy or live-screen behavior was
checked.

Inside the builder, item creation at `0x143D5D0` writes a `0xE0`-byte record
to the supplied output storage. The `.pdata` entry is
`0x143D5D0–0x143D6F2`. The observed call setup matches the existing type
`void* (*)(void*, uint32_t, int32_t, bool, bool)`: output storage in `RCX`,
the first item integer in `EDX`, action/type in `R8D`, a byte flag in `R9B`,
and the fifth argument at `[rsp+0x28]` on entry. One observed branch sets the
action/type to `0x2D`. The field meanings and all constructor call sites have
not been fully audited.

The source-vector call uses `RCX=menu+0xA058` and `RDX=item` at
`0x152A238–0x152A23B`, after a constructor call at `0x152A226`. The target
`0x153EE50` is a true `.pdata` function entry at
`0x153EE50–0x153EFC7`. Its header contract is capacity at `+0`, count at `+4`
and data at `+8`; it copies `0xE0` bytes, increments the count, uses growth
helper `0x2BF93E0` on a full vector and returns the inserted item pointer.
QAM source-builder calls establish an actual source-vector destination, not
only a render path. The same helper is also reached for render-vector work,
so any hook must validate the exact header/object before applying menu logic.

The reverse-RTTI checks reject two tempting stride/count candidates:
`0x143D700` is `cGcGalaxyPathMenu::Update` and `0x1545EF0` is
`cGcTerrainEditMenu::Update`; neither is a QAM slot. Other preserved false
leads are `0x258290` (16-byte pairs, wrong item stride), `0x2CA7BB` (a
constructor-time count reset), `0x153B5B0` (selected-item context snapshot,
not a source builder), and old RVA `0x15282B0` (inside the QAM constructor
group in this build). Do not repeat these searches as if their roles were
still unresolved; the reasons and preceding evidence are recorded above.

This maps exact-build static candidates for the old `MenuBuilder`,
`MenuConstruct` and `MenuAppend` roles to `0x152A1C0`, `0x143D5D0` and
`0x153EE50`. These are not yet approved source targets. `NOT CHECKED`:
all builder callers and indirect paths; constructor semantics beyond observed
register roles; QAM and render vector ownership/thread/lifetime; whether the
append detour's exact-header filter remains sufficient; menu label, select,
trigger, confirmation, resource and input-filter replacements; remaining
runtime/global dependencies; local-player/network and load semantics; and
live in-game behavior. Keep the native profile fail-closed until those
dependencies and acceptance gates are complete.

Next bounded action: map the remaining menu call roles from the exact 7.06
RTTI slots and their direct callers, starting with the old confirmation and
selection roles. Record the source-inventory denominator before further
searches so that each pass covers a required native dependency or a material
false lead.

### QAM confirmation predicate slot, 12 October 2026

The validated QAM vtable probe reports slot 6 at `0x153C680`. This is a true
`.pdata` root with chained ranges through `0x153C786`. Its body reads the menu
depth at `+0xA050`, the matching selected index at `+0xA088`, the vector count
at `+0xA05C + depth*0x10`, and the selected `0xE0`-byte item through the data
pointer at `+0xA060 + depth*0x10`. It returns a Boolean in `AL`, rejects
invalid depth/index/vector state, reads the selected action, and consults
additional menu/game predicates. These data and return roles align with the
old confirmation predicate at `0x153A770`, which occupied slot 6 in the
7.05 QAM vtable.

```text
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcQuickActionMenu@@"
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C680
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C680 --size 0x106
```

This is a `STATIC-CORROBORATED` candidate for the old `MenuConfirm` role:
the independent anchors are the same QAM vtable slot and matching selected
item/Boolean behavior. The probe validates the vtable and executable entry;
it does not resolve the indirect virtual-call set or prove runtime timing.
`NOT CHECKED`: whether all consumers treat it as the confirmation predicate,
thread/reentrancy behavior, and live confirmation/menu behavior. Do not
enable its hook solely from this mapping.

Next bounded action: map the old selection helper from its selected-index
stores and callers, then resolve the binding-filter return site separately
from the `GetButton` callee. Keep their roles distinct from the QAM vtable
slots.

### Selection-index write scan and input-handler false lead, 12 October 2026

A focused write scan of the QAM depth field and selected-index array used the
exact Cosmos 7.06 hash recorded above, CPython 3.11.9, pefile 2024.8.26 and
Capstone 5.0.7. It scanned 52,110,272 bytes in `.pdata` ranges, skipped zero
ranges, and printed every result below the cap: 19 writes at `+0xA050` and
29 at `+0xA088`.

```text
py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0xA050 --offset 0xA088 --access write --limit-per-offset 100
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1530AC0 --size 0x203
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1529E44 --size 0x40
```

The hits include QAM update/reset, builder, navigation and context-snapshot
ranges, plus stack-local displacement coincidences. Do not treat every
`+0xA088` write as the old `MenuSelect` helper. The tempting `0x1530AC0`
function writes selected indices, but its QAM call at `0x1529E64` sets
`RCX=menu` and `RDX=r15` (the input-state object). The callee reads the
current input action and a bit mask at `input+0x6C4`, processes navigation
events and writes menu depth/selection state. It is a menu-input handler, not
the old direct selection setter contract `(depth_field, depth, index)` used
by `MenuAdapter::afterTrigger`. Reject it for that function-pointer slot.

The older `0x1518EF0` RVA remains unmapped: in this executable it is an
interior chained range under `0x15182A0`, and its inspected direct caller has
string/output arguments inconsistent with the setter. `NOT CHECKED`: the
exact 7.06 direct selection setter, its full call set, whether selection can
be changed safely without it, and all live selection behavior. Continue from
an exact three-argument setter callsite or an independent retained-pattern
match; do not substitute the input-navigation handler or write fields just
because their offsets match.

Next bounded action: scan for a three-argument selection setter by combining
QAM callsites with the verified selected-index array field and check the
candidate's register setup and return/side-effect contract. Then resolve the
input-binding return site independently from the `GetButton` callee.

### QAM text-output slot candidate and version check, 16 October 2026

The official [No Man's Sky release log](https://www.nomanssky.com/release-log/)
was checked on 16 October 2026. Its latest listed game patch remains Cosmos
7.06; no 7.07 entry is listed. This is the game release, separate from the
mod's Nexus package version. The 7.06 Steam executable identity above is
unchanged: build 25732212, 88,560,712 bytes, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
The research used source base `f7d97b61fcf152677d0d30de34f6c1b48675c436`
with a dirty working tree, CPython 3.11.9, pefile 2024.8.26 and Capstone
5.0.7.

The validated `.?AVcGcQuickActionMenu@@` RTTI vftable at `0x4A504E0` has slot
9 at `0x153C0C0`. Its root `.pdata` range is `0x153C0C0–0x153C0FD`, with
chained ranges `0x153C0FD–0x153C24C` and `0x153C24C–0x153C5E4`. The body reads
QAM depth at `+0xA050`, selected index at `+0xA088`, vector count/data at
`+0xA05C/+0xA060`, and an item with stride `0xE0`; it selects localized
strings based on the selected item's action and writes two terminated output
buffers through `RDX` and `R8`. This makes slot 9 a plausible replacement
candidate for the old `MenuLabel` role. The evidence is RTTI slot identity
plus selected-item/text-output behavior; exact output meaning and all
consumers remain unverified.

The old source declares `label_original` as `void(*)(void*,void*)`, and its
post-hook writes a 128-byte caption to the second argument. The 7.06 body
clears both `RDX` and `R8` output buffers and terminates each at offset
`0xFF`, indicating a different three-argument contract. Do not install slot 9
with the old two-argument function type or assume which output the mod may
replace. Keep the label role `CANDIDATE; ABI AND OUTPUT SEMANTICS UNRESOLVED`.
This further confirms that the earlier `0x152A1C0` label hypothesis is
withdrawn; that address is the source builder.

Reproduce the RTTI and bounded body checks with the exact 7.06 executable:

```text
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcQuickActionMenu@@"
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0C0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0C0 --size 0x3D
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0FD --size 0x14F
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C24C --size 0x398
```

A combined exploratory shell invocation started a full-image direct-call
scan for `0x153C0C0`, but only the preceding function-group output was captured
before the 30-second command window ended. The call-xref result is
`NOT CHECKED`, not zero; it was not repeated because RTTI establishes virtual
dispatch and this direct-call scan does not cover indirect calls. The three
bounded disassembly windows above completed. `NOT CHECKED`: virtual callers,
which output is the native action label, actual output buffer ownership,
thread/timing, old-to-new output equivalence, full QAM slot inventory,
selection setter, resource initialization, binding-filter return, remaining
native dependencies and live behavior. Source and compatibility profile stay
unchanged and fail closed.

Next bounded action: establish the slot-9 caller contract through a bounded
virtual-call or neighboring base-vtable comparison, then compare both output
arguments to the 7.05 label role. Keep `MenuSelect` unmapped until a
three-argument setter callsite or independent pattern confirms its contract.

### Parent-vtable and resource-slot checks, 16 October 2026

To test the proposed neighboring-vtable comparison, the exact-build RTTI
probe was run for both base/interface-looking names listed by the validated
QAM class hierarchy. It returned `VALID_LOCATORS: 0` for each; this means no
standalone validated RTTI locator/vftable was found for these exact names. It
does not establish that the classes have no inherited methods or that slot 9
has no callers.

```text
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcQuickMenuState@@"
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcQuickMenu@@"
```

The validated QAM slot 14 points to `0x153DDF0`, despite having no `.pdata`
entry. A bounded decode from that vtable-anchored entry shows a short
two-input Boolean predicate: it checks `[RCX+0x10]`, compares `EDX` with an
application-global value, and returns in `AL`. This is inconsistent with the
old one-argument `MenuResources` hook and has no resource-loading/retaining
behavior in the verified slot body. Reject slot 14 as the resource-hook
replacement. The adjacent bytes contain further function-like code without a
verified `.pdata` or vtable boundary; do not assign those instructions to
slot 14 or infer a resource role from their proximity.

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153DDF0 --size 0x100
```

These checks used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7 on the
same SHA-256 recorded above. The standalone base-vtable route is a recorded
dead end; do not repeat those exact type-name queries. `NOT CHECKED`: another
base type, a bounded indirect slot-9 caller scan, the exact label consumer,
MenuResources replacement, selection setter and live behavior. Next, locate
slot-9 consumers using vtable-offset/callsite dataflow, or use an independent
signature and caller pattern; keep both menu hooks unmapped until their ABI
and object contract are established.

### Load-flag data-flow follow-up, 16 October 2026

This follow-up used the same verified Steam build 25732212 / Cosmos 7.06 executable, SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499. The source base remains f7d97b61fcf152677d0d30de34f6c1b48675c436 with the working-tree research changes listed by Git. Analysis used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7.

The data-offset write scan found two writes to +0x4BE6A0 across 52,110,272 bytes of .pdata ranges, with zero skipped ranges: 0x487D1B clears a 16-bit value, while 0x4956B8 stores BL to [R12+0x4BE6A0]. The latter is inside a chained range whose unwind parent is 0x495640. That routine stores its R9B argument at the field. Its sole direct caller is 0x4955F8 in the chained body rooted at 0x495560. The 0x495560 body derives R9B from a global session object at application+0x941C70, subobject+0x1A8: it checks a state value at +0x418, invokes virtual slot +0x40, then checks +0x41C. The result is a session-derived predicate; its exact name and local-player/network meaning remain unproven.

A caller scan of 0x495560 found four direct calls: 0x32F794 and 0x32FC2C in one state path, plus 0x48E56E and 0x48E583 in the main load-state path. The byte is read five times: at 0x48FDB7 and 0x48FEFE in the main state method, at 0x49069A immediately before its call to 0x573500, at 0x497A7E in a chained range rooted at 0x497A30, and at 0x4A8EF1 in a chained range rooted at 0x4A88C0. The 0x497A6C path passes the byte as DL to 0x495250; that helper has a distinct false branch and also reads the same global session subobject. These consumers confirm that the byte affects state/load processing, but do not establish whether true means online, remote, local, or another session mode.

The disassembly window for 0x4A88F8 was corrected to 0x4A88F8–0x4A90F8. It showed the field check at 0x4A8EF1 guarding a later branch. Unwind grouping resolves that range to root 0x4A88C0, with chained ranges through 0x4A9BE1. The first direct-call query incorrectly targeted the chained interior 0x4A88F8 and found zero direct calls. A corrected full .pdata scan of root 0x4A88C0 also found zero direct E8-style calls; the RTTI probe found zero validated vftable slots. These bounded negatives do not rule out other indirect-call forms. The separate range at 0x497A6C groups to 0x497A30. Its callers remain NOT CHECKED; an exact-target RTTI probe found zero validated vftable slots.

One initial PowerShell invocation did not yield usable scan output because the quoted executable path contains an apostrophe in No Man's Sky. The corrected double-quoted path produced the results above. Treat the initial attempt as a command-line quoting error, not as a binary result.

Reproduce the new field and range checks against the exact executable:

    py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x4BE6A0 --access write --limit-per-offset 100
    py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x4BE6A0 --access read --limit-per-offset 100
    py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x495675
    py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495640 --context 12
    py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495560 --context 12
    py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x4A88F8 --size 0x800
    py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x4A88F8
    py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x4A88F8 --context 10
    py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x4A88C0 --context 10
    py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x4A88C0
    py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x497A6C
    py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x495250 --size 0x250
    py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x497A30

NOT CHECKED: the type and exact semantic name of the application session object; indirect callers of 0x4A88C0 and 0x497A30 beyond validated RTTI-backed vftables; proof that the flag selects local versus network behavior; live load behavior; and remaining menu/resource/binding dependencies. Keep the load role as a static candidate and the 7.06 profile disabled. No source or profile mapping changed and no tests were run.

Next bounded action: identify the session subobject at application+0x941C70+0x1A8 through an independent class, constructor or RTTI/data-flow anchor, then verify what the +0x418/+0x41C predicate denotes. In parallel, resume the unresolved three-argument MenuSelect setter and MenuResources/binding-filter roles. Do not promote the load hook or enable 7.06 until those semantic and lifecycle gates are satisfied.

### Interrupted session-global displacement scan, 16 October 2026

A follow-up attempted to discover direct uses of the application displacement +0x941C70:

    py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x941C70 --access read --limit-per-offset 100

The script was active and consuming CPU, but had emitted no output after more than two minutes. A process snapshot showed about 148 seconds of CPU time and an approximately 803 MB working set. The run was interrupted; because this tool prints its scan totals only at completion, the amount of .pdata actually decoded and the match count are NOT CHECKED. This is an interrupted scan, not a zero-match result. The current helper has no function-range filter, so repeating this broad scan for one already localized global is not an efficient next step.

Next attempt: inspect only the known caller and consumer function windows, or add a bounded-function option to the research helper and record its exact range coverage before using it. Retain a full required-dependency rescan for a genuinely new executable hash, but batch offset searches where possible and do not let an unreported long-running scan silently consume the work period.

### Caller-context windows and disassembly-boundary correction, 16 October 2026

Three initial windows began at arbitrary interior RVAs (0x48E540, 0x32F750 and 0x32FBE0); their first decoded instructions were misaligned and are a TOOL ERROR, not evidence. Re-running from each verified .pdata root produced a valid instruction stream:

    py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x48E400 --size 0x1A0
    py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x32F385 --size 0x9C0

In root 0x48E400, calls at 0x48E56E and 0x48E583 pass RCX=rsi, R8D=-2, and RDX=0 then RDX=r15d; each tests the Boolean AL result. In root 0x32F385, call 0x32F794 passes RCX=global+0xE70, RDX=[global+0x318974], R8D=-2. Call 0x32FC2C passes RCX=global+0xE70+0x20, RDX=0, and R8D=[object+0xAA60]. These contexts corroborate distinct state-processing callers of 0x495560, but do not name its session-derived R9B predicate or resolve local/network semantics.

The correction reinforces the boundary rule: even when a target RVA is known, begin disassembly at the exact function or verified instruction boundary, then filter around the callsite. Keep the exact output limited to the call context; do not retain the misaligned byte decode as a candidate.

### Session RTTI and constructor-chain follow-up, 16 October 2026

The earlier session-global displacement query was followed with exact RTTI and bounded code evidence. The exact-build name inventory found validated names `.?AVSession@cGcMatchmaking@@` and `.?AVPlayfabSession@cGcMatchmakingPlayfab@@`; `PlayfabSession`'s class hierarchy names `Session` as its base. It also found manager types `.?AVcGcMatchmaking@@`, `.?AVcGcMatchmakingPlayfab@@` and `.?AVcGcMatchmakingPlayfabSteam@@`. The `Session` vtable is at `0x4AAA640` (19 executable slots); `PlayfabSession` is at `0x4AA9F98` (26 slots). Both inherit the same slot 8 target `0x1C7A60`; its bounded body is `mov al, 1; ret`, so the virtual predicate in the load path is always true for these tables. This leaves its callsite predicate dependent on the `+0x418 == 4` state check and nonzero `+0x41C` byte; those fields' names/semantics remain unverified.

The vtable-reference pass found one direct RIP-relative reference to the `PlayfabSession` table at `0xAD5B6C`, in root `0xAD5A90`. This function allocates `0xA48` bytes, installs a base `Session` vtable and later the derived `PlayfabSession` vtable, clears the words at `+0x414` and byte at `+0x41C`, and stores constructed object pointers at `[manager + index*8 + 0x1A0]`. The second pointer slot therefore shares the exact `+0x1A8` layout read by the load path. However, a complete direct-call pass over 52,110,272 `.pdata` bytes found zero direct calls to `0xAD5A90`, its exact RVA had zero validated RTTI-backed vtable slots, and a bounded direct-RIP-reference pass found zero references to that function entry. The observed constructor/layout is a strong class/layout lead, not proof that the load path's global manager is the same object or that its slot 1 is populated by this routine.

Manager RTTI confirms `cGcMatchmaking` at vtable `0x4AA9D10` and `cGcMatchmakingPlayfab` at `0x4AAA070`; the latter's hierarchy includes `cGcMatchmaking`. Constructor root `0xAC73D0` installs those base/derived tables and initializes manager fields including `+0x1A0`. Its sole direct caller `0xAC7050` then installs `cGcMatchmakingPlayfabSteam`; caller `0xAE881A` allocates `0xA60` bytes, calls `0xAC7050`, and stores the returned pointer at `[RDI+0xAB40]`. This is a verified Steam-specific construction chain, but the member `+0xAB40` has not been connected to the load path's application-global member `+0x941C70`; do not conflate them based on class names.

Reproduce the RTTI, vtable-reference and constructor checks on the exact executable:

    py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVSession@cGcMatchmaking@@"
    py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVPlayfabSession@cGcMatchmakingPlayfab@@"
    py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcMatchmaking@@"
    py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcMatchmakingPlayfab@@"
    py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcMatchmakingPlayfabSteam@@"
    py -3.11 -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x4AA9F90 --target-rva 0x4AA9F98 --target-rva 0x4AAA638 --target-rva 0x4AAA640 --limit-per-target 30
    py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xAD5A90 --size 0x340
    py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xAD5A90 --context 12
    py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xAD5A90
    py -3.11 -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xAD5A90 --limit-per-target 30
    py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xAC73D0 --size 0x300
    py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xAC73D0 --context 8
    py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xAC7050 --context 8

Tool corrections: an initial query incorrectly supplied member displacement `0x941C70` as an RVA and was rejected because that numeric RVA is executable; it is a `TOOL ERROR`, not a binary result. The actual RIP-relative global pointer read at `0x4955AD` resolves to RVA `0x6E8D708`. Querying that highly shared pointer without an output cap produced an oversized truncated tool response; discard its incomplete reference list and do not infer a count. `native_rip_xrefs.py` now reports total counts, caps examples, and prints progress every 5 MiB. An initial direct-call scan materialized all decoded instructions and exceeded 800 MiB working memory before completion; it was interrupted with counts `NOT CHECKED`. The helper now streams `disasm_lite` tuples with a bounded rolling context. A batched known-target pass reproduced 4 callers for `0x495560` and 1 for `0x495640` across 52,110,272 bytes, with zero ranges skipped, confirming the new output shape. With this version, the direct-call scan for `0xAD5A90` completed and returned zero direct E8-style calls. These scanner changes are research-only; no source mapping or compatibility profile changed and no tests were run.

The object at `application + 0x941C70 + 0x1A8` remains a `STRONG STATIC CANDIDATE` for a `PlayfabSession` pointer, not a confirmed mapping. `NOT CHECKED`: indirect/dynamic callers of `0xAD5A90`, proof that its manager argument is the exact object read at `application+0x941C70`, whether slot 1 is the selected local session, the meaning of `+0x418/+0x41C`, and live behavior. Keep the load hook and 7.06 profile disabled. Next bounded work: resume the three-argument `MenuSelect` setter or directly establish the dynamic manager/slot link from a specific caller or registered function table; then continue unresolved resource/label and runtime-lifecycle gates.

### MenuSelect candidate shortlist, 16 October 2026

The complete detailed write scan for `+0xA088` is already recorded above: 29 writes across the exact 7.06 `.pdata` inventory. A repeat using the detailed helper produced no output after about one minute and was interrupted; that repeat is `NOT CHECKED` and does not replace the earlier completed ledger. To shortlist specific bodies without repeating the same slow detail path, `native_data_offset_xrefs.py --fast-candidates` decoded `.pdata` boundaries with `disasm_lite`. It found 64 total `+0xA088` memory operands, including reads, address-only `lea`, `cmp`/`idiv`, stack-local strings and other objects. This is candidate discovery only; its access hints are heuristic, not an exact write count.

The small body at `0x153BE80` looked setter-like because it writes `menu+0xA088`. Unwind grouping shows it is chained to root `0x153BE60`; the root loads its target ID from `[menu+0xA164]`, searches top-level `0xE0` items and restores the corresponding index. A full direct-call scan against the correct root found one caller, QAM update at `0x15288C9`, with `RCX=menu` and `RDX=render state`. It is an internal selection-restore routine, not the old `(depth_field, depth, index)` setter. The earlier zero direct-call result for interior `0x153BE80` is superseded by the corrected root query.

Two more offset matches are false leads. `0x2CA6D0` installs the QAM vtable `0x4A504E0` and initializes `+0xA088` to zero as part of the menu constructor; it is a reset, not a setter. `0x2D1970` initializes a vector-like object whose `+0xA088` field is set to capacity `0x401`; exact RTTI reverse mapping found no vtable slot for that routine. Candidates `0x15288D6` and `0x152B394` each had zero direct E8 callers and zero validated RTTI-backed vtable slots; their indexed writes do not establish a setter contract. Keep them unpromoted.

Reproduce the fast shortlist and the corrected setter-candidate checks:

    py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0xA088 --limit-per-offset 100 --fast-candidates
    py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153BE60 --size 0x170
    py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153BE80
    py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153BE60 --context 12
    py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2CA6D0 --size 0x150
    py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D1970 --size 0x150
    py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x15288D6 --target-rva 0x152B394 --context 8

The previous fast-candidate hints mislabeled `cmp` and `idiv` memory operands as destinations. The helper now labels read-only operations and address-only `lea` separately and prints `ANALYSIS_MODE`; all fast access labels remain explicitly heuristic. It reports 64 operands for this offset in 52,110,272 bytes with zero skipped ranges, versus the earlier detailed ledger's 29 writes. `NOT CHECKED`: the exact current-build three-argument selection setter, any indirect callers of the remaining writes, `MenuSelect` behavior without a setter, the binding filter, menu resource/label lifecycle and live behavior. Keep the selection role unmapped and the compatibility profile disabled. Next bounded action: start at QAM trigger/action callers and require a callsite setup that demonstrates the old depth/index contract before considering any remaining write candidate.

### 7.05-to-7.06 scope correction and MenuSelect mapping, 16 October 2026

The supported 7.05 executable is already the Cosmos baseline. For this update, the relevant binary delta is Cosmos 7.05 to Cosmos 7.06; the 7.0 feature list must not be used to explain a regression that appeared after the 7.05 profile was working. Hello Games' 7.06 notes list space-walk camera, Gravitino Coil, expedition ship-transfer and crash fixes, with no Quick Menu or companion change called out ([official 7.06 notes](https://www.nomanssky.com/2026/10/cosmos-7-06/)). Those notes do not rule out internal code movement in the executable. The startup refusal is explained by the exact-build guard still requiring the 7.05 SHA-256; it is a safety refusal, not runtime evidence that a particular feature broke.

The old 7.05 `MenuSelect` address `0x1518EF0` is not reusable: in 7.06 it is inside a different chained `.pdata` function and its direct caller has an incompatible string/output contract. A bounded static search found the 7.06 leaf at `0x151ADB0` (no `.pdata` entry). Its body checks depth `<= 2`, rejects negative indices, checks the index against the selected vector count at `depth_field + depth*16 + 0x0C`, and stores the index at `depth_field + depth*4 + 0x38`. This is the same three-argument role used by the source: `(depth_field, depth, index)`.

The exact-build call scan found three direct calls to `0x151ADB0`; all are inside the QAM `TriggerAction` chained body rooted at `0x1531E00`. At `0x1538A72`, `RCX` is `menu+0xA050`, `EDX` is the just-updated depth, and `R8D` is the selected index. At `0x1538AD5` and `0x1538D95`, the callers pass the same depth-field base, read the current depth into `EDX`, and pass a selected index in `R8D`. This caller evidence plus the exact bounded-store body makes `0x151ADB0` a `STATIC-CORROBORATED` replacement candidate for the `MenuSelect` role. It is a candidate for the exact 7.06 executable only; source and profile remain unchanged until the remaining hooks and compatibility gates are closed.

The neighboring `0x151AD40` routine is a different helper: it accepts a depth and an item pointer, then calls the vector append function. Its 57 direct callers made the first context-12 report too large and truncated. Do not map it to `MenuSelect`. The high-fanout output problem was corrected by adding `--limit-per-target` to `native_call_xrefs.py`; totals remain complete while printed call contexts are capped. A combined rerun reported 57 calls to `0x151AD40` with two contexts printed, and three calls to `0x151ADB0` with two printed; a focused context-12 rerun printed all three setter calls.

The `0x152E5D2` indexed store inside QAM builder root `0x152A1C0` is also confirmed as builder-local bounds-checked selection work, not a separate function target. Do not promote its chained range `0x152B394` to a function pointer. The first detailed full-image indexed-store scan was stopped before completion due to slow decoding and has no match result. The optimized `native_indexed_store_xrefs.py` pass decoded all 52,110,272 `.pdata` bytes with zero skipped ranges; its exact `(base=r15, index=rcx, scale=4, displacement=0x38)` query found only `0x152E5D2`. A first parser draft confused an index register with a base register; that output was discarded, the parser was corrected, and the final query was rerun with the corrected base/index parser.

Reproduce the mapped setter and bounded call-site query against the exact 7.06 executable:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x151ADB0 --size 0x40
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x151ADB0 --context 12 --limit-per-target 10
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152E5D2
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152A1C0 --size 0x4B11
py -3.11 -B tools/native_indexed_store_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --displacement 0x38 --scale 4 --base-register r15 --index-register rcx --limit 20
```

This pass used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7. It is static evidence only; no in-game 7.06 behavior was checked. Remaining gates include menu label/output ABI, menu resource initialization and retention, binding-filter return site, all source dependencies, load local/network semantics, runtime lifecycle and live behavior. Keep `native_compatibility.json` at the approved 7.05 hash and keep 7.06 fail-closed. Next bounded action: port the confirmed selector address in a version-scoped way, then continue the remaining menu and load dependencies without changing the compatibility guard.

### QAM label-slot output follow-up, 16 October 2026

This corrects the earlier statement in “QAM text-output slot candidate and version check” that slot 9 clears and terminates two 256-byte text buffers. A complete root-aligned decode of `0x153C0C0–0x153C5E4` shows that the function saves `RDX` as its main string output, clears the first byte of the original `R8` pointer once at entry, then reuses `R8` as a scratch/argument register. No later memory access uses that original `R8` pointer. The function writes a bounded string to the `RDX` buffer and terminates it at `RDX+0xFF`; it does not establish a second text output.

The function still reads QAM depth, selection, vector count/data and selected-item action, then chooses localized strings and formats the visible text. This supports slot 9 at `0x153C0C0` as a `MenuLabel` candidate, with a main 256-byte output at `RDX`. The old hook prototype is `void(menu, output128)`; the new slot body uses a third register argument in `R8`, whose meaning remains `UNRESOLVED`. Do not assume it is a second caption or ignore it in a detour. A compatible hook would need to preserve all three arguments and account for the 256-byte native output size.

Reproduction against the exact 7.06 executable:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0C0 --size 0x524
```

The bounded filter over the full output was `Select-String -Pattern 'r8|r14 \+ 0xff'`. It showed the original `R8` pointer is used only at entry to clear one byte; later `R8` appearances are scratch values. The older interpretation is superseded, not silently deleted. This remains static evidence; virtual callers, the meaning of the auxiliary argument, exact downstream output ownership and live rendering remain `NOT CHECKED`. Keep label-hook source and the compatibility profile unchanged. Next bounded action: locate a virtual caller or independent signature/consumer for slot 9 to identify the `R8` argument and determine whether the 256-byte output is the text field the mod replaces.


### Release lineage correction and slot-9 caller search, 16 October 2026

Repository history confirms this is the second native game-build update. The original 0.10.0 native alpha targeted Steam Cosmos 7.04 / build 25442159. Commit `9460855` (30 September 2026) records the successful 7.04-to-7.05 native profile update for 0.10.1; it kept the legacy Python profile on 7.04 and updated the native profile to the exact 7.05 executable. The current 0.10.2 release notes still require Cosmos 7.05 / build 25624745. This report therefore investigates only the adjacent 7.05-to-7.06 change. The version guard refuses 7.06 because its executable hash is unmatched; that does not show that a particular feature regressed.

A bounded virtual-call search tested whether QAM label slot 9 at vtable byte offset `0x48` is called from a function that also references the known QAM depth field `+0xA050`. Against the exact 7.06 executable hash, CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7, this filter found zero function ranges and zero calls. The unfiltered structural scan decoded all 52,110,272 `.pdata` runtime-function bytes with zero skipped ranges and found 789 simple indirect calls through `[register+0x48]` in 523 ranges across the image; no ranges starting in the inspected QAM windows (`0x1528`, `0x152A`, `0x152B`, `0x152E` or `0x153`) provided a caller. This is `NO MATCH` for that direct slot-offset form in those windows, not proof that the virtual method has no callers: dispatch through a cached function pointer, wrapper, another slot form or another object remains possible.

Reproduction commands:

```text
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xA050 --context 5 --limit-per-range 10
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --context 3 --limit-per-range 3
```

The broad output was saved outside the repository and summarized by function-range header; it is not part of the evidence package. Keep `MenuLabel` unmapped and the 7.06 profile disabled. The next useful step is a different independent anchor for the slot-9 consumer or the old text-output contract, rather than repeating the same `+0x48` / `+0xA050` filter.


A second independent anchor pass used `native_rip_xrefs.py` on the exact 7.06 executable (SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`), scanning all 52,110,272 `.pdata` bytes with zero skipped ranges. Its sole direct RIP-relative reference to QAM vtable `0x4A504E0` is at `0x2CA6EC` in constructor root `0x2CA6D0`. It found zero direct RIP-relative references to slot-9 method `0x153C0C0` and adjacent vtable slot address `0x4A504E8`. This confirms only that the constructor installs the QAM vtable; it does not identify the virtual caller or the third argument. The scan cannot see dispatch through an object vptr or function pointer loaded indirectly.

Reproduction command:

    python -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x4A504E0 --target-rva 0x153C0C0 --target-rva 0x4A504E8 --limit-per-target 30


### QAM icon field and resource-loader follow-up, 16 October 2026

The exact-hash fast displacement scan for `+0xA104` decoded 52,110,272 `.pdata` bytes with zero skipped ranges and returned 18 operands. Because the helper's access labels are heuristic and the same displacement occurs in different object bases, the operands were checked against their function and caller context. In QAM constructor root `0x2CA6D0`, `RCX` is saved as the menu object and the constructor initializes `menu+0xA104` to zero. In the confirmed QAM builder root `0x152A1C0`, `RCX` is saved to `RSI`; the builder reads `dword [RSI+0xA104]` and passes it in `EDX` to item constructor `0x143D5D0`. This corroborates `+0xA104` as the QAM's native item icon value for this build, and confirms that the builder still reads this field.

Function 0x1526240 also references +0xA104. Its sole direct caller at 0x1540145 passes RCX=parent+0xDC0; the 18 October owner-relative trace proves this is the cGcQuickMenu wrapper at outer+0x115D50 and its cGcQuickActionMenu child. The earlier conclusion that this body did not load resources was incorrect; the focused dataflow correction is recorded below. The function has no validated RTTI-backed vtable slot. Its native resource-initialization role is now static-corroborated, while post-return runtime timing and safety remain unverified.

The current-build `cGcRealityManager::LoadTexture` signature candidate is `0xEC8700`, not the old 7.05 RVA `0xEC6850`. The 7.06 target is a `.pdata` entry and its body reads a path pointer from `[RCX]`, invokes the native path/resource loader, and stores the resulting handle through `RCX+0x10`. This matches the source `TextureRecord` layout, where the path is at offset 0 and the handle is at `+0x10`. A full direct-call scan found 294 callers over 52,110,272 bytes with zero skipped ranges; the RTTI probe found no validated vtable slot. Filtering the complete caller list found no direct caller in the `0x15xxxxxx` Quick Menu code range. The generic loader role is `STATIC-CORROBORATED`; its exact use/timing from the QAM remains unresolved. The old `0xEC6850` is an interior address in this build and has zero direct E8 callers and zero validated RTTI slots; do not reuse it.

A separate slot-offset query for `call [register+0x48]` in ranges referencing `+0xA104` found zero matching ranges/calls. Together with the earlier `+0xA050` query, this still does not rule out indirect dispatch through cached pointers or a wrapper. No source/profile change is approved from these results.

Reproduction commands, all against SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499` with CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7:

```text
python -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0xA104 --fast-candidates --limit-per-offset 50
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2CA6D0 --size 0x3C6
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152A1C0 --size 0x80
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1526240 --size 0x100
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1526240 --context 10 --limit-per-target 20
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1526240
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xEC8700 --size 0xA8
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xEC8700 --context 0 --limit-per-target 1000
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xEC8700
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xA104 --context 5 --limit-per-range 12
```

Next action: locate the natural QAM resource-ready callback or prove a safe post-resource timing point for the custom icon loads. Preserve the QAM icon-field evidence, but keep the resource callback, labels, load semantics and 7.06 profile disabled until their own object, ABI and lifecycle gates pass.

### QAM icon-field consumer and slot-9 search, 16 October 2026

This pass used the exact Steam 7.06 executable hash above with CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7. No game process was modified, no live behavior was checked, and no native source or compatibility-profile mapping changed.

The complete fast-candidate scan for displacement +0xA104 returned 18 operands across 52,110,272 .pdata bytes. The body rooted at 0x1527BD0 belongs to a five-range unwind group, reads this+0xA104 and performs member cleanup/reset work. Its only direct caller at 0x924D67 passes RCX=parent+0x116B10. The 18 October constructor-chain trace composes the QAM wrapper offset +0x115D50 with its child offset +0xDC0, proving that this is the same nested QAM object; the earlier different-base conclusion is corrected. The call is teardown cleanup, not a resource-ready callback. RTTI found zero validated vftable slots for helper 0x1527BD0; its native method identity remains unknown.

The other field-access body at 0x1526240 is called from 0x1540120 at 0x1540145 with RCX=wrapper+0xDC0. The 18 October owner trace now establishes that this is the embedded cGcQuickActionMenu child. Its body performs a long member initialization/copy sequence, including a conditional transfer through this+0xA104, but does not establish a resource-loading action or ready-state lifecycle point. Keep MenuResources unmapped.

At QAM-builder callsite `0x152A22C`, the builder loads `dword [menu+0xA104]` into `EDX`, passes output storage in `RCX`, and calls item constructor `0x143D5D0`. The constructor is an exact `.pdata` entry at `0x143D5D0–0x143D6F2`; it stores `EDX` at `[item]` and `R8D` at `[item+4]`, consistent with the observed `0xE0` item record. The constructor itself does not load a texture. A whole-`.pdata` direct-E8 scan counted 56 calls and printed 50 contexts. The QAM-builder example is confirmed; the rest of the callsite set was not individually audited in this pass. This establishes transfer into the item record, not whether the first dword is a raw icon identifier, loaded resource handle or what later consumes it.

A same-function filter combining vcall slot offset `0x48` with field displacement `+0xDC0` decoded all 52,110,272 `.pdata` bytes with zero skipped ranges and returned 8 calls in 7 ranges. It did not identify a receiver confirmed to be the QAM object. In the inspected case at `0x1559375`, the call explicitly sets only `RCX`; the result in `EAX` is consumed as an integer by a following helper. This does not match the known slot-9 call contract, which requires the `RDX` output pointer and has an unresolved `R8` argument. Other filter results remain unclassified; they are not a zero-caller proof. A first PowerShell summarizer collided with the built-in `$Matches` hashtable and produced invalid indexing; that output was discarded, and the query was rerun with `$hitIndices`.

Reproduce the bounded pass with the exact executable and commands:

```text
py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0xA104 --fast-candidates --limit-per-offset 50
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1527BDD
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1527BD0 --size 0xAEB
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1527BD0 --context 10 --limit-per-target 50
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2CA6D0 --context 8 --limit-per-target 20
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1527BD0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1540120 --size 0x1DB
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1526240 --size 0x139C
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x143D5D0 --size 0x120
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x143D5D0 --context 10 --limit-per-target 50
py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xDC0 --context 6 --limit-per-range 10
```

Next bounded action: follow the first dword from the QAM builder through the appended item consumer to a validated resource lookup or draw call, then find the slot-9 call through a proven QAM object flow and record its `RDX`/`R8` setup. `NOT CHECKED`: exact icon field meaning after item construction, natural QAM resource-ready callback, remaining slot-9 candidates, binding-filter return role, local-versus-network load meaning, remaining source dependencies and live 7.06 behavior. Keep the current 7.05 profile and guard unchanged; 7.06 remains unsupported and fail-closed.

### QAM slot-9 argument filter and icon-value flow, 16 October 2026

This continuation used the same Steam 7.06 executable SHA-256, source baseline and pinned NMS.py provider/data hashes recorded above; it did not repeat the full dependency inventory because the executable hash did not change. CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7 were used. The official [Hello Games release log](https://www.nomanssky.com/release-log/) was checked again and still lists Cosmos 7.06 first, with no 7.07 entry.

The broad `native_vcall_xrefs.py` query for slot byte offset `0x48` decoded all 52,110,272 `.pdata` runtime-function bytes, skipped zero ranges and reported 789 calls in 523 ranges. With `--context 12 --limit-per-range 1000`, all 789 contexts were present in the output saved outside Git. Context 16 was rejected by the tool's supported range and corrected to 12. A bounded post-last-call screen over those contexts found 66 broad cases with a stack-relative `RDX` setup and some `R8` write, but none in the `0x1500000–0x15FFFFF` code range. The 66 are only text-context candidates: some `R8` writes are scalars, and assignments outside the 12-instruction window or before an intervening call are not covered. This is not proof of no slot-9 callers.

Two apparent candidates, callsites `0x1556F68` and `0x1557C35`, set an `R8` pointer and stack-local `RDX` buffer before calling helper VA `0x140540660`, then dispatch through `[vptr+0x48]`. The helper's unwind group is rooted at RVA `0x540660` and includes chained ranges `0x5406FF–0x54085A` and `0x54085A–0x54088D`. Across the complete group, the body saves its incoming `R8` in `RSI`, overwrites `R8` with scratch values at `0x540721`, `0x540767`, `0x540781` and `0x5407FB`, and does not restore it before return. Reject both as evidence for slot 9's `R8` argument. Their receiver roots `0x1556EC0` and `0x1557BB0` and outer caller root `0x15547DE` have no validated RTTI-backed vtable slot; receiver identity remains unresolved. An initial helper query passed the disassembly VA `0x140540660` as an RVA and returned out-of-range; the corrected PE query uses RVA `0x540660`.

A separate exact-hash fast scan for displacement `+0xA060` returned 32 operands across the same `.pdata` scope with zero skipped ranges. It includes stack-local false hits, so each selected reference was checked in its `.pdata` root. The QAM update root `0x15286C0` reaches vector items through `menu+0xA060`, a `0xE0` stride and the selected index; the inspected update and slot-9 label body read the action field at item `+4`. The update copies complete `0xE0` records into its context cache, preserving the first dword, but the inspected code does not read that first dword as a texture handle or draw argument. The QAM builder's item constructor `0x143D5D0` stores the `menu+0xA104` value in the first dword and `R8D` at `item+4`, then the builder passes the returned item to append helper `0x151AD40`. This confirms transfer and copying of the value, not its downstream resource lookup or rendering meaning.

Reproduce the bounded scans and root-aligned inspections against the verified 7.06 executable:

```text
py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --context 12 --limit-per-range 1000
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x540660
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x540660 --size 0x230
py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0xA060 --fast-candidates --limit-per-offset 150
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1528DB9
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15286C0 --size 0x1800
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0C0 --size 0x524
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x151AD40 --context 12 --limit-per-target 100
```

`NOT CHECKED`: the consumer of the icon value after the QAM cache copy, the slot-9 virtual caller and `R8` meaning, a safe resource-ready callback, the binding-filter return site, local-versus-network load semantics and live 7.06 behavior. Do not modify the source mapping or compatibility guard. Next bounded action: follow the cached first dword to a renderer/resource consumer using caller and object-flow evidence, then resume the remaining native dependency gates. Cosmos 7.06 remains unsupported and fail-closed.

### QAM context-cache destination caller audit, 16 October 2026

The root-aligned helper `0x153C7A0` is a `.pdata` entry (`0x153C7A0–0x153C83D`). It returns a destination inside the supplied object at `object+0x2D0+index*0x3480`; the inspected path chooses one of three destination regions. In the QAM update, whole `0xE0` item records are copied there. This maps the cache destination and record propagation, but not a renderer or texture lookup that reads the first dword.

A complete direct-E8 scan found 14 calls to `0x153C7A0` in three function ranges. Eleven callsites are in QAM update body `0x15288D6–0x1529E81`, chained to root `0x15286C0`; one is in helper root `0x153B5B0`; two are in function range `0x15406B4–0x1540AF6` and pass `RCX=parent+0xDC0`. At that stage, the two adjusted-base callers were unclassified, so the helper was not yet established as QAM-only. The 18 October caller audit below resolves their direct flow to QAM `TriggerAction`; it still cannot rule out unobserved indirect callers. These direct callers explain where the returned cache address is used for QAM copying/comparison, but they do not establish a downstream draw consumer.

A broad fast-candidate scan for displacement `+0x2D0` found 1,852 operands across 52,110,272 `.pdata` bytes with zero skipped ranges, printed only the first 100, and marked the output truncated. The examples were dominated by stack-local offsets and did not provide a bounded consumer result. An attempted `--fast-candidates --access read` combination was rejected by the tool; the corrected no-access shortlist completed but remained too broad. Treat this as `NOT CHECKED`, not a zero-reference result. Do not repeat the whole-image offset query without a new object/caller anchor.

Reproduce the bounded helper and candidate checks against the exact 7.06 executable:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C7A0 --size 0x100
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153C7A0 --context 8 --limit-per-target 20
py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x2D0 --fast-candidates --limit-per-offset 100
```

`NOT CHECKED`: any draw/resource consumer of the cache's first dword, receiver identity in the two adjusted-base calls, the slot-9 virtual caller/auxiliary argument and live behavior. Next bounded action: track the exact cache pointer and copied record into its next consumer using call/data flow from the confirmed QAM update; avoid another displacement-only scan. Keep 7.06 disabled.

### QAM cache virtual-call shortlist and release-log recheck, 16 October 2026

The official [No Man's Sky Release Log](https://www.nomanssky.com/release-log/) was rechecked on 16 October 2026. It still lists Cosmos 7.06 first and Cosmos 7.05 next; no 7.07 entry was present. The requested target therefore remains the installed Cosmos 7.06 / Steam build `25732212`, not a later game release.

An exact-build RTTI probe reconfirmed that target `0x153C0C0` is slot 9 of the `cGcQuickActionMenu` vftable at `0x4A504E0`, with `cGcQuickMenuState` as a base. This validates the slot/type relationship only; it does not establish a caller for the method or its `R8` argument.

A narrower whole-`.pdata` filter combined virtual slot byte offset `0x48` with any same-function displacement `+0x2D0`. It decoded all `52,110,272` runtime-function bytes with zero skipped ranges, returning 13 ranges and 21 indirect calls. The one result in the broad `0x15xxxxxx` address area was callsite `0x1557ACD` in range `0x1557565–0x1557B83`. Root-aligned disassembly shows the matching `+0x2D0` is only the stack save `[rsp+0x2D0] = R15`; the filter does not match the QAM cache base or identify the receiver. Reject this as a cache-consumer lead. The screen is still limited to `[vptr+0x48]` calls and same-range numeric displacement and is not a proof that no other cache consumer exists.

Reproduction against `NMS.exe` SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499` (CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7):

```text
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153C0C0 --max-slots 30
py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0x2D0 --context 12 --limit-per-range 20
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1557565 --size 0x61E
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153B5B0
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15406B4
```

No source mapping, compatibility profile or runtime behavior changed. `NOT CHECKED`: the downstream use of the cache's copied first dword, the slot-9 caller and `R8` meaning, the safe resource-ready callback, the binding-filter return site, local-versus-network load behavior, and live 7.06 behavior. Keep 7.06 unsupported and fail-closed. Next bounded action: start from one confirmed `0x153C7A0` return in QAM update `0x15286C0`, track that exact returned pointer through each copy and subsequent call, and require a later read of the copied record's first dword or a proven resource-handle conversion before naming its role. Do not repeat a global `+0x2D0` scan.

### QAM cache consumer dataflow and direct-caller correction, 18 October 2026

The official [No Man's Sky Release Log](https://www.nomanssky.com/release-log/) was rechecked on 18 October 2026 and still lists Cosmos 7.06 above 7.05, with no 7.07 entry. The installed executable is unchanged: Steam build `25732212`, file/product version `180836`, size `88,560,712` bytes, SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.

A complete exact-hash direct-E8 scan of `0x153C7A0` reproduced 14 calls across `52,110,272` `.pdata` bytes with zero skipped ranges. It confirms 11 calls in the QAM update range `0x15288D6–0x1529E81`, one at `0x153B5D9` in the context-snapshot helper, and two in the input-dispatch range `0x15406B4–0x1540AF6`. This corrects an earlier report sentence that counted 12 update calls; the earlier count was a documentation error, not a changed binary or an extra caller.

The two adjusted-base calls are now tied to QAM by dataflow. In the input-dispatch range, `0x154074D` calls `0x153C7A0` with `RCX=RDI+0xDC0`, then reads the cached record's action at `+4`. On the dispatch branch, `0x1540794` gets that cache address again and `0x15407A7` calls QAM `TriggerAction` (`0x1531E00`) with `RCX=RDI+0xDC0`, `RDX` pointing at the selected cached record and `R8D=0`. This confirms the adjusted receiver as a QAM subobject for this path. Together with the QAM update caller and its context-snapshot helper, all 14 observed direct E8 callers have static QAM flow; this is not proof that no indirect callers exist.

The cached records serve context and action-state work in the inspected paths. QAM update passes cache records to equality helper `0x151AB50`, which compares action `+4` and other fields but not the first dword; the update also copies full `0xE0` records into the cache and resets selected record fields. `TriggerAction` saves its incoming item pointer from `RDX`, reads the action identifier at item `+4`, then reuses `RSI` for another object at `0x1532251`. In the complete `0x1531E00–0x1532E3C` disassembly, the incoming item pointer is not read at offset zero. This supports cache use for action dispatch/state comparison, not rendering of the icon value stored in the first dword. A separate renderer/resource consumer remains unverified.

Reproduction against the same executable hash (CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7):

```text
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153C7A0 --context 10 --limit-per-target 20
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1540430 --size 0x8BA
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1531E00 --size 0x103C
```

`NOT CHECKED`: any separate draw/resource consumer of the first dword, the actual slot-9 caller and `R8` meaning, a safe resource-ready callback, the binding-filter return site, local-versus-network load behavior and live 7.06 behavior. Keep the compatibility profile disabled. Next bounded action: resolve slot 9 through a QAM receiver path that sets the full native arguments, then resume the remaining resource, binding and load-lifecycle gates; do not use this cache as a renderer mapping.

### Slot-9 `+0xDC0` caller shortlist re-audit, 18 October 2026

The exact-hash `native_vcall_xrefs.py` filter for virtual slot byte offset `0x48` plus same-function displacement `+0xDC0` decoded `52,110,272` `.pdata` bytes, skipped zero ranges and returned 8 calls in 7 function ranges. The eight sites are `0x149301F`, `0x149307F`, `0x155395E`, `0x155665F`, `0x155937B`, `0x155A45F`, `0x157C0AA` and `0x17F67E1`. None establishes both a QAM receiver and the known slot-9 output-argument contract. A same-function `+0xDC0` hit can belong to another register/object than the virtual-call receiver.

The most plausible local-buffer candidate, `0x155A45F` in root `0x1559BB8–0x155A4BE`, is rejected as slot-9 caller evidence. It sets `RDX` to a stack buffer at `0x155A440`, but calls helper `0x148D2D0` at `0x155A44D` before the virtual dispatch and does not set `RDX` again; Windows x64 volatile-register rules leave the buffer argument unproven. It sets `R8B=1` only after the dispatch. The receiver is `R14` (copied from this function's entry `RCX`), while the same-function `+0xDC0` operand is a separate `[RDX+0xDC0]` read at `0x155A2E7`. An exact RTTI probe of root `0x1559BB8` found zero validated vftable slots. The call returns an integer stored in a local structure; no QAM identity or text-output use is established.

The other seven call windows remain unclassified beyond the displayed contexts; they are not promoted as slot-9 callers. This is a bounded negative for the `+0xDC0` same-function filter, not proof that slot 9 has no caller. The executable hash and release remain unchanged from the 18 October identity above.

Reproduction:

```text
py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xDC0 --context 12 --limit-per-range 10
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1559BB8 --size 0x906
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1559BB8 --max-slots 40
```

`NOT CHECKED`: the true slot-9 virtual caller, the meaning of `R8`, QAM renderer/resource lifecycle, binding-filter return site, local-versus-network load behavior and live 7.06 behavior. Next bounded action: trace the receiver specifically from the verified QAM subobject at `parent+0xDC0` into candidate virtual dispatches, while proving `RDX` and `R8` remain valid across all intervening calls. Do not accept a same-function offset match by itself. Keep 7.06 disabled.

### Slot-9 receiver identity check against every `+0xDC0` shortlist hit, 18 October 2026

Reproduced the `slot-offset 0x48` plus same-function displacement `+0xDC0` scan against the unchanged exact executable hash. It decoded all `52,110,272` `.pdata` bytes, skipped zero ranges, and returned 8 calls in 7 ranges. Root-aligned inspection of the matching `+0xDC0` operands shows why this is not a QAM receiver filter: `0x149301F`/`0x149307F` dispatch through `RSI+0xB90`/`RSI+0xA10` while the field hit is `[RSI+0xDC0]`; `0x155395E` and `0x155665F` use `RSI` and `RDI` receivers while the displacement is based on `R13`; `0x155937B` uses `RSI` and only reads `[R15+0xDC0]` after dispatch; `0x155A45F` uses `R14` while the field hit is `[RDX+0xDC0]`; `0x157C0AA` and `0x17F67E1` dispatch through a global object at `global+0x905B20`, while their `+0xDC0` hits belong to local/other objects. None of the eight windows demonstrates the verified QAM subobject at `parent+0xDC0` in the virtual-call receiver.

This resolves the review status of all eight shortlist hits: none is positive evidence for a QAM receiver because no hit demonstrates that its call receiver is the verified `parent+0xDC0` subobject. Some shown expressions are directly distinct; others simply lack alias proof. This does not prove that slot 9 has no callers, because the scan does not propagate object identity across arbitrary register copies, fields, or calls. The known `0x155A45F` candidate is also rejected for ABI reasons: a helper call intervenes after the stack-buffer `RDX` setup, and `R8` is set after the virtual dispatch. Keep the actual slot-9 caller and `R8` meaning `NOT CHECKED`.

Reproduction against Steam build `25732212`, executable SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499` (CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7):

```text
py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xDC0 --context 12 --limit-per-range 10
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1491E10 --size 0x1C8F
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15536E3 --size 0x3FD
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15562EA --size 0x3F1
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1559375 --size 0xC5
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1559BB8 --size 0x906
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x157B772 --size 0xF0E
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x17F5B70 --size 0x195C
```

`NOT CHECKED`: the actual QAM slot-9 virtual caller and `R8` meaning, icon/resource consumer, safe resource-ready callback, binding-filter return site, local-versus-network load semantics and live 7.06 behavior. Next bounded action: anchor caller discovery on the known QAM owner/subobject and follow that pointer to slot-offset `0x48` dispatches; validate any match by proving receiver and full `RDX`/`R8` setup across intervening calls. Do not repeat the same-function displacement shortlist. No source mapping or compatibility profile changed; keep 7.06 fail-closed.
### QAM nested-object provenance and +0x116B10 correction, 18 October 2026

On the unchanged Steam build 25732212 / executable SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499, the constructor chain resolves the apparently different offsets. The unique direct caller of cGcQuickMenu::cGcQuickMenu at 0x2CA290 is 0x2C8F28 in root 0x2C8EC0-0x2C914A; it passes RCX=RDI+0x115D50. That constructor calls 0x2CA6D0 at 0x2CA3FE with RCX=RSI+0xDC0. The nested constructor installs vftable 0x4A504E0, already validated for cGcQuickActionMenu slot 9. Therefore the QAM child object is at enclosing-owner offset 0x115D50 + 0xDC0 = 0x116B10.

The earlier 16 October map note that called parent+0x116B10 a different subobject from the constructor's parent+0xDC0 was an offset-base error. It is now corrected in NATIVE-UPDATE-MAP.md. A caller scan of the QAM constructor root found exactly one direct constructor caller. Separately, root 0x2C8EC0 has one direct caller at 0x2C6E8E, passing RCX=RDI+0x732920; cleanup root 0x924C90 has one direct caller at 0x32FD1B, passing RCX=global+0x732920. The shared enclosing-member offset supports the construction/cleanup relationship, but no RTTI name for that outer owner was established.

Root 0x924C90 passes RCX=RDI+0x116B10 to cleanup helper 0x1527BD0 at 0x924D67; this is the same nested QAM child after composing offsets. The helper's five-range unwind group performs member/vector cleanup and is reached from the owner's teardown path, so it is not a resource-ready callback. The helper remains rejected for the old MenuBuilder role on ABI/body evidence, and its exact native method name is still unknown.

A new slot 0x48 + same-range displacement 0x116B10 scan found one function range, 0x924C90-0x924DFF, with two indirect calls. Root-aligned disassembly shows their receivers are loaded from [RDI+0x110998] and [RDI+0x1109A0], not from the QAM object at RDI+0x116B10; these are false positives for the slot-9 caller. The exact +0x116B10 data-offset scan returned only the cleanup reference at 0x924D60. Two additional bounded filters returned zero calls: slot 0x48 plus outer QAM member displacement 0x115D50, and slot 0x48 plus both 0x115D50 and 0xDC0. Each decoded all 52,110,272 .pdata bytes with zero skipped ranges. These are bounded negative results for those same-function displacement patterns, not proof that the virtual slot has no callers through aliases or cached pointers.

Reproduction against the exact executable (CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7):
- py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2CA290 --context 12 --limit-per-target 40
- py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2C8EC0 --size 0x28A
- py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2CA290 --size 0x440
- py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2C8EC0 --context 12 --limit-per-target 30
- py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x924C90 --context 12 --limit-per-target 30
- py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x924C90 --size 0x16F
- py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x116B10 --fast-candidates --limit-per-offset 100
- py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1527BD0 --context 12 --limit-per-target 20
- py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0x116B10 --context 12 --limit-per-range 20
- py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0x115D50 --context 12 --limit-per-range 20
- py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0x115D50 --require-field 0xDC0 --context 12 --limit-per-range 20

NOT CHECKED: the actual slot-9 caller and R8 meaning, the QAM icon/resource consumer, a safe resource-ready callback, the binding-filter return site, local-versus-network load semantics and live 7.06 behavior. The exact offset correction changes no source mapping or compatibility profile. Keep 7.06 disabled. Next bounded action: resume caller discovery using independently proven QAM pointer flow and the complete slot-9 RDX/R8 ABI; do not promote the teardown call or another same-function displacement match.


### QAM setup path and selector-anchored slot-9 scan, 18 October 2026

The corrected owner-relative arithmetic gives a second independent QAM path. The enclosing object is addressed at global+0x732920; its cGcQuickMenu member is at +0x115D50 (global+0x848670), and the embedded cGcQuickActionMenu child is at wrapper+0xDC0. The exact composed global offset is therefore 0x732920 + 0x115D50 + 0xDC0 = 0x849430. An earlier exploratory sum was mistakenly written as 0x849A30; that was an arithmetic error. Discard the zero-result scan for 0x849A30 completely. The corrected value 0x849430 is independently present at 0x55900A, 0x146427F and 0x14642BE.

The QAM wrapper setup path is now linked statically. Function 0x1540120 calls 0x1526240 with RCX=wrapper+0xDC0; a complete direct-E8 scan found no other caller of 0x1526240. Function 0x1540120 itself has two direct callers: 0x2DF7D3 passes global+0x848670, and 0x91821D passes its enclosing object+0x115D50. This confirms the child object's constructor/setup relationship to the QAM wrapper. The body at 0x1526240 bulk-initializes/copies members and localized string values, but no call or dataflow establishes a texture load or resource-ready event. The sibling reset helper 0x153FF00 has one direct caller at 0x916C6A with the same wrapper-relative base and resets wrapper state; it is not a slot-9 call.

The exact-hash data-offset scan found three 0x849430 operands. A slot-offset 0x48 filter requiring 0x849430 returned zero calls across all 52,110,272 .pdata bytes with zero skipped ranges. A selector-index anchor at global+0x849424 returned 45 decoded operands. The matching slot-offset 0x48 filter returned two calls, at 0x1420D04 and 0x3359A8. Both dispatch through the unrelated global object at global+0x905B20, not through the selected QAM child. The latter function does pass global+0x848670 to the known QAM input dispatcher 0x1540430, but that dispatcher contains slots +0x30/+0x38/+0x40/+0x50 and no +0x48 call. These two results are false leads for QAM slot 9, not proof that there are no callers through aliases or cached function pointers.

A separate exact path in 0x1464200 selects one of four menu-state objects using the index at global+0x849424, selects the QAM child at global+0x849430 for one index, and calls its vtable slot +0x58. This confirms state-object flow but is a different virtual slot from slot 9 at +0x48. The UI state selector is a useful anchor; the present slot-9 shortlist does not produce a valid QAM receiver.

Reproduction against the unchanged Steam build 25732212 / executable SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499 (CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7):
- py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x115D50 --offset 0x116B10 --fast-candidates --limit-per-offset 100
- py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x849430 --fast-candidates --limit-per-offset 100
- py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x849424 --fast-candidates --limit-per-offset 100
- py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0x849430 --context 12 --limit-per-range 30
- py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0x849424 --context 12 --limit-per-range 30
- py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1540120 --context 12 --limit-per-target 30
- py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1526240 --context 12 --limit-per-target 30
- py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153FF00 --context 12 --limit-per-target 30
- py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1464200 --size 0x152
- py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x335827 --size 0x2D4
- py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x141FF22 --size 0x1571

NOT CHECKED: the actual QAM slot-9 caller and R8 meaning, the downstream icon/resource consumer, the safe resource-ready callback, the binding-filter return site, local-versus-network load semantics and live 7.06 behavior. The corrected arithmetic and added setup path do not change any native mapping or compatibility guard. Keep 7.06 disabled. Next bounded action: continue from the selector-driven QAM state flow, but accept a slot-9 candidate only when RCX provenance and the full RDX/R8 ABI are both established.


### Full chained-group check for the selector-state QAM pointer, 18 October 2026

The corrected global QAM child displacement at 0x849430 appears at 0x55900A inside chained range 0x558FB5-0x559023. Since a same-range slot filter cannot combine this operand with another chained range, the complete eleven-range unwind group was inspected from root 0x558E40 through 0x559F15. It selects a state object using global+0x849424 and checks byte +0x9A on the selected QAM child. In the full group, the only decoded indirect calls are slot +0x20 at 0x559626 and 0x559660, with receivers loaded from the separate object at [RDX+0x933B78]. No slot +0x48 call appears in this group, and the selected QAM pointer is not used as an indirect-call receiver in the inspected control flow. This closes that cross-range false lead without ruling out callers elsewhere in the image.

Reproduction against the same executable hash:
- py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x558FB5
- py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x558E40 --size 0x10D5

NOT CHECKED: the actual slot-9 caller and R8 meaning, the downstream icon/resource consumer, the safe resource-ready callback, the binding-filter return site, local-versus-network load semantics and live 7.06 behavior. The selector-based pointer path is now bounded through this parent unwind group but does not alter the fail-closed mapping.


### QAM resource initializer recovered, 18 October 2026

Correction to the earlier QAM setup-path conclusion: the statement that `0x1526240` did not establish a resource load was wrong. The earlier review recognized its member and localized-string initialization but missed the generic resource-manager calls and the output-handle dataflow. This correction supersedes the `UNMAPPED` resource-hook conclusion in that section; it does not change the native profile.

The old 7.05 resource-hook RVA `0x1524330` is not a reusable 7.06 entry. It lies inside the separate root `0x1524230–0x152443C`, whose four-register body reads and writes caller buffers through `RCX`, `R8` and `R9`. Three direct callers pass four register arguments. Reject this current function for the old one-pointer resource hook.

The replacement resource-initialization candidate is root `0x1526240–0x15279DC`. Its sole direct caller is `0x1540120` at `0x1540145`, with `RCX=wrapper+0xDC0`; the constructor-chain and owner-offset evidence above identifies that address as the nested `cGcQuickActionMenu` child. At `0x1526E89`, the method calls helper `0x2D63EA0` with a resource-manager pointer, an output handle in a stack temporary, type `7`, and a path in `R9`. It compares the returned handle with `dword [QAM+0xA104]`, releases the old value when different, and stores the new handle at `QAM+0xA104`.

The direct RIP-relative string reference at `0x1526E5C` resolves to data RVA `0x4AE6608`, the path `TEXTURES/UI/FRONTEND/ICONS/QUICKMENU/SUMMONPET.DDS`. The neighboring `+0xA100` load uses `TEXTURES/UI/FRONTEND/ICONS/QUICKMENU/SUMMONMENU.DDS`. The exact path and output field establish that this is genuine QAM resource initialization, not merely a matching member offset. Helper `0x2D63EA0` is a five-range unwind group; its body accepts the manager, output handle, type and path, uses the resource-manager table at `+0x5C/+0x60`, and increments the loaded resource reference count. This is static evidence that the original initialization has completed its native loads when `0x1526240` returns. Runtime thread, repeat-call, reload/destruction and custom-icon behavior remain unverified.

The separate `cGcRealityManager::LoadTexture` candidate `0xEC8700` still matches the mod's `TextureRecord` shape: path pointer at offset `0`, output handle at `+0x10`. It is not called directly from the `0x15xxxxxx` quick-menu code in the complete direct-call scan; the native QAM uses the generic resource-manager helper above. Keep these two loading interfaces distinct. The custom-icon loader role remains static-corroborated, while its safe mod call timing must be tested in the exact game build.

The exact-hash `+0xA104` fast-candidate pass decoded all `52,110,272` `.pdata` bytes with zero skipped ranges and returned 18 operand hints. `FAST CANDIDATE` access labels are heuristic only; the relevant constructor, setup function and caller were then checked at their exact PE function roots. Two detailed read/write scans for offsets `+0xA100`, `+0xA104` and `+0xA108` were interrupted before completion and are `NOT CHECKED`; do not cite them as zero matches. An inline Python path-read attempt first failed because PowerShell passed the Windows path through Python string-literal escaping; this was a command-invocation error, not a PE decode result. The data read was corrected through a PowerShell here-string, and `native_string_xrefs.py` independently confirmed the direct reference to the exact string.

Reproduction against Steam build `25732212`, executable SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499` (CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7):

```text
py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0xA104 --fast-candidates --limit-per-offset 300
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1524230 --size 0x20C
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1526240 --size 0x179C
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2CA6D0 --size 0x3C6
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D63EA0 --size 0x61B
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D63EA0
py -3.11 -B tools/native_string_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --contains SUMMONPET.DDS
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xEC8700 --size 0xA8
py -3.11 -c "import pefile,sys; p=pefile.PE(sys.argv[1]); print(p.get_data(0x4AE6608,128).split(bytes([0])[0:1])[0])" "<verified Cosmos 7.06 NMS.exe>"
```

Status: `0x1524330` is rejected; `0x1526240` is `STATIC-CORROBORATED` for the old resource-initialization role and offers a static post-load return point. The `MenuSelect` replacement `0x151ADB0`, binding-filter return site `0x15292F5` and slot-9 label-output method `0x153C0C0` are also statically corroborated in the earlier sections; do not repeat those mappings. `NOT CHECKED`: live call timing/thread, repeat and teardown behavior, 7.06 custom texture behavior, actual QAM slot-9 caller and `R8` contract, downstream label consumer, live binding-filter effect, local-versus-network load semantics and all in-game 7.06 behavior. Keep the 7.06 profile disabled. Next bounded action: trace the actual slot-9 caller and its argument ownership, then resolve load-hook local/network meaning and close the exact-source dependency ledger before considering any source/profile change.


### Binding-filter return-register context recheck, 18 October 2026

Focused disassembly starting at `0x15292A6` confirms the already-mapped return site `0x15292F5` in caller range `0x15288D6–0x1529E81`. The handler holds the QAM object in `RDI`: immediately after the `GetButton` call returns at `0x15292F5`, it reads depth from `[RDI+0xA050]`, selected index from `[RDI+depth*4+0xA088]`, vector count/data from `[RDI+depth*0x10+0xA05C/+0xA060]`, and indexes a `0xE0`-byte item. It then reads the action at item `+4`. This matches the base register and QAM field layout assumed by the existing generated filter and strengthens `0x15292F5` as the exact static return-site candidate.

This is static register/layout corroboration, not live proof that filtering the selected mod row has the intended effect or is safe across all input paths. `0x15292AB` remains the fixed-button alternate and is not the selected-item filter site. The existing source constant and approved profile still target only the 7.05 return RVA; do not replace one shared constant until source selection is explicitly keyed to the exact approved profile.

Reproduction against the unchanged exact executable hash:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15292A6 --size 0x100
```

`NOT CHECKED`: live filter outcome, complete input-thread/lifecycle safety, label slot-9 callers, local-versus-network load meaning and the remaining exact-source dependency ledger. No source/profile mapping changed; 7.06 stays fail-closed. Next bounded action: search for the QAM label consumer by output-buffer provenance and separately resolve load-hook local/network semantics.

### Session-flag search boundary and probe corrections, 18 October 2026

A broad fast-candidate search for displacement `+0x41C` decoded all
`52,110,272` `.pdata` bytes with zero skipped ranges, but returned 207 operand
hints and printed only 200 (`TRUNCATED: yes`). The displacement is common
across unrelated objects; this result is not a session-field inventory and
does not identify the `PlayfabSession+0x41C` writer. Do not repeat the global
offset scan as a semantic search. The exact reader and constructor evidence
above remain bounded leads only.

Probe corrections: `native_rtti_vtable_probe.py --type-name PlayfabSession`
returned zero locators for the unqualified display-name query; this does not
invalidate the earlier exact RTTI chain. Passing `--target-rva 0x4AA9F98` was
rejected because that RVA is data, not an executable method. A probe against
method `0x1C7A60` ran for more than 60 seconds without output and was
interrupted: `INTERRUPTED / NOT CHECKED`. Reuse the exact class/vtable work
already recorded in the 16 October report rather than repeating a generic
full-image method probe.

No source, profile or package changed. Next bounded action: trace `+0x41C`
writes only inside functions tied by exact RTTI/vtable or constructor evidence
to `Session`/`PlayfabSession`, then establish the object behind
`application+0x941C70+0x1A8`. Keep its class, predicate meaning, local/network
semantics, indirect callers and live load behavior `NOT CHECKED`; leave 7.06
fail-closed.


### Ownership-predicate and hand-query ABI recheck, 18 October 2026

This follow-up uses the same Steam build `25732212` executable and SHA-256
recorded above. CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7 were used.
It changes no native source or compatibility profile.

#### `services.owned`: reject the old RVA, retain the new leaf candidate

The old source target `0x508200` is not an instruction entry in 7.06. Starting
from the verified `.pdata` root `0x508107`, decoding shows the instruction at
`0x5081F9` ends at `0x508201`; `0x508200` is inside that instruction. A complete
`.pdata` direct-E8 scan also found zero calls to `0x508200`. Do not reuse it.

Leaf `0x508290` has no `.pdata` entry, but its body and callsites establish a
strong `bool(owner, slot)` replacement candidate for the source's
`services.owned` role. In the owner-update method, root `0x508DC0` saves the
incoming `RCX` owner object in `RSI`. At `0x509231` the active slot is loaded
from `[RSI+0x1B9300]`; `0x50923B` restores the same owner pointer to `RCX`, and
the method calls `0x508290` at `0x50924D`. The leaf reads that object's
`slot*0x24A0` record, checks the supported location, slot bound and entry
fields, then returns the Boolean in `AL`. This directly matches the source
callback's owner-and-slot inputs. `0x1474F10` also calls the same leaf using the
application companion table and incoming slot, corroborating its eligibility
role in the native summon path. The source still points to its 7.05 RVA and is
unchanged; the new candidate is research evidence only.

#### `services.dominant_hand`: hidden-`this` concern resolved statically

The unique `GetDominantHand` signature candidate `0x14874B0` is a `.pdata`
entry. Its accepted path returns application `+0x30E7FC` in `EAX`; rejected
state returns zero. Although the method forwards its incoming `RCX` to
`0x1C84D0`, that callee reads the thread-local state and global data and does
not consume incoming `RCX`. The source's no-argument call shape is therefore
compatible at the machine-code boundary. A complete `.pdata` direct-E8 scan
found zero callers of `0x14874B0`; this bounded result does not rule out
virtual or other indirect references. Record the service as
`STATIC-CORROBORATED`, not live-verified.

#### Native validation helper boundary

The helper at `0x50A520` is a separate `.pdata` entry with 13 chained ranges.
Its body consumes `RCX`, sign-extends the slot from `EDX`, takes an output
buffer in `R8`, and returns a Boolean in `AL`. A full direct-call scan found
six callers, including the owner update and `0x1474F10`; the latter tests its
result after the eligibility helper. This establishes the call boundary and
ABI shape, not the helper's full semantic label. Keep the enclosing
`CanSummon` candidate as the source service; do not replace it with
`0x50A520`.

One first call-xref invocation used unsupported `--context 14` and was rejected
by argument validation before decoding. The corrected `--context 12` scan
completed across all `52,110,272` `.pdata` bytes with zero skipped ranges; the
earlier attempt is a tool-argument error, not a scan result.

Reproduction commands:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x508107 --size 0x130
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x508290 --size 0x100
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x508DC0 --size 0x680
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x50924D
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x508200 --target-rva 0x508290 --context 12 --limit-per-target 30
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x14874B0 --size 0x80
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x14874B0 --context 12 --limit-per-target 30
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1C84D0 --size 0x100
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1C84D0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x50A520 --size 0x640
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x50A520 --context 12 --limit-per-target 40
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x50A520
```

The used helper SHA-256 values are already listed in this report's tool
inventory: `native_function_disasm.py`
`26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0`,
`native_call_xrefs.py`
`7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`, and
`native_pdata_function_group.py`
`FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26`.

`NOT CHECKED`: all live 7.06 behavior, the session byte's owner and local or
network meaning, the dynamic producer for `0x495675`, the QAM slot-9 caller
and `R8` contract, and the remaining exact-source dependencies. Keep the
7.06 profile fail-closed. Next bounded action: use the newly confirmed owner
object and its caller chain to trace the `+0x4BE6A0` writer or prove the next
reference form worth searching; then continue the remaining menu and load
gates without repeating the already bounded zero-reference scans.

### PlayfabSession `+0x41C` member and helper follow-up, 18 October 2026

The exact decorated RTTI query
`.?AVPlayfabSession@cGcMatchmakingPlayfab@@` succeeds with one validated
locator and the expected 26-slot vftable at `0x4AA9F98`. This replaces the
earlier unqualified display-name probe that returned zero. Slot 17 is
`0x239DF0`; its complete five-range body receives `this` in `RCX`/`RDI`, checks
state `this+0x418`, walks entries beginning at `this+0x720`, and at `0x239EB8`
tests whether the byte at `this+0x41C` is zero before processing each entry.
This confirms that the byte predicate is used by a method in the validated
`PlayfabSession` vtable, but does not name its meaning.

Slot 20 is `0x238750`; `R14` holds `this`, and its chained body reads four
consecutive 16-byte values beginning at `this+0x41C`, `+0x42C`, `+0x43C` and
`+0x44C`. This indicates that `+0x41C` is also the start of a larger structured
region. Slot 11 at `0x237820` is the sole direct caller of helper `0xACA370`
in the completed direct-call scan, passing `RCX=this`. The helper clears
members at `+0x40C`/`+0x414` and writes four XMM-sized values across the
`+0x41C` through `+0x44C` region. In this helper only the first byte of its
first stack source is explicitly zeroed; the provenance of the other source
lanes was not established, so do not describe the whole region as zeroed.
The constructor `0xAD5A90` does explicitly clear the first byte at `+0x41C`.

Together, these class-specific paths confirm a tested leading byte within a
larger member region. The boolean derived by the load-adjacent path remains a
session-linked predicate, not a proven network flag. The pointer at
`application+0x941C70+0x1A8` is still not dynamically or statically tied to
this exact vftable; matching offsets and the `+0x40` call remain a strong
lead, not object identity.

One inspection attempt began at interior RVA `0x238BB0` and produced
misaligned initial instructions; mark it `TOOL ERROR` and discard it. The
corrected decode begins at the validated slot-20 root `0x238750`. Reproduce
the positive class/method evidence with:

```text
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVPlayfabSession@cGcMatchmakingPlayfab@@" --max-slots 64
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x239EB8
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x239DF0 --size 0x144
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x238BCB
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x238750 --size 0x641
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xACA370 --context 10 --limit-per-target 20
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xACA370 --size 0x90
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xAD5A90 --size 0x300
```

`NOT CHECKED`: meaning and producer of the region's leading byte, origin of
the helper's other stack-fed lanes, identity of the application-global
subobject, local/network classification, indirect callers and live load
behavior. No source, profile or package changed. Next bounded action: trace
the exact `PlayfabSession` data producer and the manager's population of slot
1, then classify the four load-role callsites. Keep 7.06 fail-closed.


### PlayfabSession slot population and current release/source check, 18 October 2026

On the unchanged Steam build `25732212` / NMS.exe SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`,
root `0xAD5A90` preserves incoming `RCX` in `R14`. The RIP-relative index
table resolves to RVA `0x4A49134` and contains bytes `00 01 02`. The loop
allocates one `0xA48`-byte object per index, clears `+0x41C`, temporarily
installs base `Session` vtable `0x4AAA640`, completes member initialization,
then installs derived `PlayfabSession` vtable `0x4AA9F98`. It stores the
object at `0xAD5D70` through `[R14 + index*8 + 0x1A0]`. Therefore index 1
from this constructor is at manager-relative `+0x1A8`, matching the field
read by the load-adjacent path. This is strong class/layout corroboration for
the values produced by this constructor, not proof that `R14` is the same
manager instance reached from `application+0x941C70`; it also does not give
index 1 a local, online, or network meaning.

The corrected exact base RTTI spelling is
`.?AVSession@cGcMatchmaking@@`, yielding one validated 19-slot vftable at
`0x4AAA640`. A guessed name under the `cGcMatchmakingPlayfab` namespace
(`.?AVSession@cGcMatchmakingPlayfab@@`) returned zero locators; it is a
namespace correction, not a class-absence result. The exact derived name
`.?AVPlayfabSession@cGcMatchmakingPlayfab@@` remains validated at `0x4AA9F98`.

A fast-candidate scan of global displacements `+0x1A0` and `+0x1A8` was
interrupted after decoding approximately `0x2D040A2` runtime-function bytes,
before producing a result summary. Mark it `INTERRUPTED / NOT CHECKED`; do
not claim zero matches. Common displacements are a poor class-search anchor;
use the exact constructor index table, vtable overwrite, and known callsite.

Reproduce the constructor and RTTI evidence with:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xAD5A90 --size 0x30E
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVSession@cGcMatchmaking@@" --max-slots 64
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVPlayfabSession@cGcMatchmakingPlayfab@@" --max-slots 64
py -3.11 -c "import pefile,sys; p=pefile.PE(sys.argv[1]); print(p.get_data(0x4A49134,3).hex())" "<verified Cosmos 7.06 NMS.exe>"
```

The official [NMS Release Log](https://www.nomanssky.com/release-log/) was
rechecked on 18 October 2026: Cosmos 7.06 remains the latest listed release,
with 7.05 next and no 7.07 entry. The [Nexus files page](https://www.nexusmods.com/nomanssky/mods/4579?tab=files)
still shows `0.10.2-native-test`, last updated 3 October 2026; the package's
approved game target remains 7.05. The repository's GitHub `main` and local
`origin/main` resolve to `f7d97b61fcf152677d0d30de34f6c1b48675c436`.
This working branch contains research docs and native-analysis helpers only;
no mod source, compatibility profile, package, commit, or push was changed.

`NOT CHECKED`: identity of the constructor's manager versus
`application+0x941C70`, index-1 semantics, local/network load meaning,
indirect constructor callers and live 7.06 behavior. Keep the profile
disabled. Next bounded action: classify the four load-role caller paths and
resolve the application-global manager identity without inferring semantics
from an array index.


### Load-role caller contexts and parameter-name boundary, 18 October 2026

Rechecked direct-call contexts against Steam build `25732212` and the exact
executable hash above. The scan for `0x573500` decoded all `52,110,272`
runtime-function bytes with zero skipped ranges and found four direct calls:

| Call RVA | Unwind group | Physical setup immediately before call | Bounded interpretation |
| --- | --- | --- | --- |
| `0x2E088F` | root `0x2DBBB0`, five ranges | `RCX=RAX+0xAAD0`, `RDX=RBP+0x2240`, `R8=R14`, `R9=0`, fifth arg `1`, sixth arg `R15B` | Separate state path; result is tested and followed by state helpers. |
| `0x48EECC` | `0x48E400–0x48FA5C` | `RCX=RSI+0xAAD0`, `RDX=RBP+0xC0`, `R8=R15`, `R9=0`, fifth arg `DIL`, sixth arg `BL` | Main state-processing path. |
| `0x48F983` | `0x48E400–0x48FA5C` | Same receiver/data layout, `R9=0`, fifth arg `R13B`, sixth arg `BL` | A second branch in the same state processor; fifth arg differs. |
| `0x4906BD` | `0x48FA60–0x49081A` | `RCX=RDI+0xAAD0`, `RDX=[RBP+0x3C0]`, `R8=RSI`, `R9=[RDI+0x4BE6A0]`, fifth/sixth args `0` | Adjacent state path; the fourth arg is the previously traced session-derived byte. |

The target helper `0x495560` is directly called from roots `0x32F385` and
`0x48E400`. In the `0x48E400` path, state comparisons against 0, 4 and 6
lead to calls with `RDX=0` then `1` and `R8=-2`; the return value gates later
branches. The `0x32F385` calls pass `R8=-2` and objects at global-relative
`+0xE70` and `+0xE90`. This corroborates use of the helper during state
processing, but does not name its sentinel or the four load arguments.
Do not map the 7.05 source names `network_client` and `resetting` to the 7.06
arguments by position alone; `R9` differs across caller paths and the stack
flags also vary.

An attempted `native_call_xrefs.py --context 18` invocation was rejected
before scanning because the tool accepts at most 12 instructions. The exact
same queries succeeded at `--context 12`; the rejected invocation is a tool
limit correction, not a binary result.

Reproduce the exact callsite contexts and unwind roots with:

```text
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x573500 --context 12 --limit-per-target 10
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495560 --context 12 --limit-per-target 10
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2E088F
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x48EECC
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x48F983
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x4906BD
```

`NOT CHECKED`: semantic names for the native arguments, identity of the
`+0xAAD0` receivers, local/network state for each caller, and lifecycle/thread
safety. The next bounded action is to identify the caller roots' owning classes
or a non-ABI semantic anchor, then trace the flag sources. No source/profile
mapping changed; 7.06 remains disabled.


### Matchmaking RTTI, constructor owner and load-path comparison, 18 October 2026

Exact decorated RTTI queries against the unchanged executable identify three
class vtables: `cGcMatchmaking` at `0x4AA9D10`,
`cGcMatchmakingPlayfab` at `0x4AAA070`, and
`cGcMatchmakingPlayfabSteam` at `0x4AAA358`. The latter has a secondary
four-slot vtable at `0x4AAA618` for its `+0x1B8` subobject. RIP-relative
reference scans find one code reference to each primary table, at `0xAC73F1`,
`0xAC74DB`, and `0xAC7077` respectively.

Root `0xAC7050` is the Steam constructor. It calls base constructor
`0xAC73D0` at `0xAC7062`, then installs the Steam table `0x4AAA358` at
`0xAC7077` and its secondary table at `+0x1B8`. A complete direct-call scan
finds one caller of `0xAC7050`: `0xAE894E`, inside chained range
`0xAE881A–0xAE8BB5` rooted at `0xAE8810`. The caller allocates `0xA60`
bytes, passes that new object to the constructor, and stores its returned
pointer at `[parent+0xAB40]`. Root `0xAE8810` is directly called once, from
`0x2C6D3F` with `RCX=application+0x937130`; therefore the known manager
instance from this path is stored at `application+0x9E670`. The constructor
then makes an indirect call through manager vtable slot `+0x38`.

The validated Steam vtable's slot 8 is `0x24B920`, whose full unwind group
contains six ranges rooted at `0x24B920`. Its body reads the manager's
`+0x1A8` session pointer, tests the session's `+0x418` state for 4, compares
the session string starting at `+9` with manager bytes at `+0x7CC`, and later
reads session fields `+0x410` and `+0x40C`. This independently supports the
interpretation that the known Steam matchmaking class keeps a session pointer
in its `+0x1A8` slot. It makes the load path's `+0x1A8` read a stronger
manager-family match than an offset coincidence alone.

However, this constructor stores its manager pointer at
`application+0x9E670`; the load predicate at `0x495560` instead reads a
pointer from `[application+0x941C70]` and then its `+0x1A8` field. These are
distinct application-relative fields. The bounded scans so far have not
established an alias, copy, or call-argument path between them; they do not
prove no such path exists. The session-array helper `0xAD5A90` also has no
direct E8 caller, so the manager constructor chain does not connect it to the
known Steam manager instance. Keep the known constructor instance and the
load-path object separate until that owner/value path is proven. The exact
RTTI type of the load-path object therefore remains `NOT CHECKED`.

One false lead: manager slot 7 is `0x24B8F0`; its short body calls base method
`0x22B230` and writes `this+0x6C0`, so it is not evidence that the session
array is populated there. Slot 8 (`0x24B920`) performs the session reads.
The direct E8 scan for `0x24B8F0` returned zero, which is expected for an
indirect virtual call; a direct-call negative must not override validated
vtable evidence. The exact scans covered all `52,110,272` `.pdata` bytes with
zero skipped ranges.

Reproduction commands:

```text
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcMatchmaking@@" --max-slots 64
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcMatchmakingPlayfab@@" --max-slots 64
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcMatchmakingPlayfabSteam@@" --max-slots 64
py -3.11 -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x4AA9D10 --target-rva 0x4AAA070 --target-rva 0x4AAA358 --limit-per-target 50
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xAC7050 --target-rva 0xAC73D0 --target-rva 0xAE8810 --context 12 --limit-per-target 40
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x24B920
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x24B920 --size 0x400
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x495560 --size 0x220
```

Next bounded action: find the initializer or proven alias path for
`application+0x941C70` and link its static/runtime class to the validated
matchmaking family. Do not repeat the global `+0x941C70` displacement scan;
continue from the exact global-pointer and constructor/caller anchors. Keep
local/network semantics, runtime behavior, and the 7.06 profile `NOT CHECKED`.


### Corrected application-relative owner path, 18 October 2026

Correction to the immediately preceding section: its calculation
`0x937130 + 0xAB40 = 0x9E670` was a hexadecimal addition error. The correct
sum is `0x941C70`; the claim that the constructor and load predicate use
distinct application members, and the resulting `NOT CHECKED` owner/type
conclusion, are superseded by the exact path below.

The exact RTTI probe validates `.?AVcGcApplication@@` with vtable
`0x4A50888`. Its only direct RIP-relative vtable reference is at `0x32BCAE`.
Root `0x32BC90` stores that vtable at data RVA `0x6E8D6D0` and clears the
qword at `0x6E8D708`, which is `+0x38` from the vtable-bearing address. The
static initializer wrapper at `0x33500` calls this root at `0x33504`.
Application setup root `0x2C6BB7` allocates a `0x95F210`-byte object and
stores its returned pointer into that same `0x6E8D708` cell at `0x2C6C1C`.
The setup later loads the pointer at `0x2C6D31`, adds `0x937130` at
`0x2C6D38`, and calls `0xAE8810` at `0x2C6D3F`.

At `0xAE8810`, the passed `RCX` is retained as the parent in `RDI`. Its
constructor path calls Steam manager constructor `0xAC7050` at `0xAE894E`
and stores the returned manager pointer at `[RDI+0xAB40]` at `0xAE895B`.
Thus the exact application-relative destination is
`0x937130 + 0xAB40 = 0x941C70`. This is the same field that load predicate
`0x495560` reads at `0x4955B9` after loading the application pointer from
`0x6E8D708` at `0x4955AD`. Constructor `0xAC7050` installs the validated
`cGcMatchmakingPlayfabSteam` vtable `0x4AAA358`; therefore the load path's
`[application+0x941C70]` is statically connected to this constructed Steam
manager instance, and its subsequent `+0x1A8` read belongs to that manager.

The earlier distinct-offset interpretation is recorded as a corrected false
lead, not as a remaining uncertainty. A separate write to the application
pointer cell at `0x62D849` stores `R14`; an exact direct-E8 scan found no
caller of root `0x62D79E`. The value and indirect invocation path for this
writer remain `NOT CHECKED`, so do not infer its runtime effect. Also still
`NOT CHECKED`: the semantic label of manager slot `+0x1A8`, local/network
meaning of the load predicate, the session-array helper's connection to this
instance, and live behavior. Keep the 7.06 profile fail-closed.

Reproduction commands against the same exact executable hash:

```text
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcApplication@@" --max-slots 64
py -3.11 -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x4A50888 --limit-per-target 30
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x32BC90 --size 0x500
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x32BC90 --context 12 --limit-per-target 30
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2C6BB7 --size 0x130
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xAE8920 --size 0xB0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x495560 --size 0x220
py -3.11 -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x6E8D708 --limit-per-target 50000
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x62D79E --context 12 --limit-per-target 20
```

Next bounded action: stop repeating owner/type discovery for
`application+0x941C70`; trace how its `+0x1A8` session pointer is populated
and what the `+0x418` / `+0x41C` checks mean in the four load-role caller
paths. Then resume the still-open menu/resource and source-dependency gates.


### Session-slot initialization boundary and class-scoped scans, 18 October 2026

Base constructor `0xAC73D0` zeroes 16 bytes at `[this+0x1A0]` with
`movups` at `0xAC74CD`, so both manager pointers at `+0x1A0` and `+0x1A8`
start null. The Steam-derived constructor then installs its vtable but does
not populate these two slots in the inspected constructor body. The
post-construction session pointer must therefore come from a later path.

Added `tools/native_vtable_member_xrefs.py` to avoid repeating broad
whole-image displacement scans. It was run against RTTI-validated tables on
the exact executable hash above using pefile `2024.8.26` and Capstone `5.0.7`:

- Steam matchmaking vtable `0x4AAA358`, 64 slots: 36 distinct method roots
  have `.pdata` groups and 27 slots point to methods without `.pdata`. Across
  the full chained groups, there are zero writes to `+0x1A0`, `+0x1A8` or
  `+0x1B0`; reads of `+0x1A8` occur in seven method groups, including slots
  8, 30, 55, 56 and 62.
- PlayfabSession vtable `0x4AA9F98`, 26 slots: 18 distinct method roots have
  `.pdata` groups and 8 slots have no `.pdata`. Across the chained groups,
  there are zero writes to the checked `+0x410`, `+0x418`, `+0x41C`,
  `+0x42C`, `+0x43C` and `+0x44C` fields. Nine read/address-independent
  memory accesses remain in the checked root groups; exact reads include the
  `+0x418` state and `+0x41C` byte tests in slots 12 and 17. These scoped
  negatives do not cover methods without `.pdata`, other classes or dynamic
  aliases.

The known manager slot 56 method `0xACB5F0` repeats the session guard: it
requires state `+0x418 == 4`, a true virtual result from session slot `+0x40`,
and byte `+0x41C == 0` before allocating a `0x98`-byte object and entering a
later helper. This corroborates a reused eligibility condition but does not
name the flag or establish local/network meaning.

Session-array helper `0xAD5A90` remains an unconnected candidate. Its
standalone unwind group is `0xAD5A90-0xAD5D9E`; the exact direct-E8 scan
found zero callers, direct RIP scan found zero references, and
`native_rtti_vtable_probe.py --target-rva 0xAD5A90` found zero validated
vtable slots. It does contain the stride-8 indexed pointer store at
`0xAD5D70`, but no static call/value path links it to the constructed manager
instance yet.

A fast indexed-store shortlist for `[base+index*8+0x1A0]` decoded all
`52,110,272` runtime-function bytes with zero skipped ranges and produced 24
heuristic stores. Candidate `0x428E52` is a false lead: its preceding
instructions set the index register to `6*r15`, making the effective stride
`0x30`, not an eight-byte pointer array. The remaining SIMD/dword candidates
are not promoted without exact owner/type evidence. A broad fast `+0x1A8`
shortlist produced 2,069 operands, printed 1,000 and was truncated; it is
`NOT CHECKED`, not a write inventory. The tool rejected `--limit-per-offset
5000` (maximum 1,000) and rejected combining `--fast-candidates` with
`--access`; the corrected no-access shortlist remains too broad. Do not
repeat it without a stronger function/owner anchor.

A vcall scan for session slot offset `0x40` requiring application `+0x941C70`,
manager `+0x1A8`, session `+0x418` and `+0x41C` decoded the complete
`52,110,272` runtime-function bytes with zero skipped ranges. It found eight
function ranges and twelve calls, including `0x4955D6` in the load predicate
and related paths at `0x12EA427`, `0x12EAF3D`, `0x2F2354`, `0x2FBBF2`,
`0x2FBCDA`, `0x305034`, `0x305045`, `0x528B91`, `0xAE8E93`, `0xAE9157` and
`0xAE9168`. These repeat the same session fields but do not assign names to
them. An earlier query mistakenly used manager slot offset `0x1C0`; it found
zero calls under the extra filters and was corrected to the session's slot
offset `0x40`.

Reproduction commands:

```text
py -3.11 -B tools/native_vtable_member_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --vtable-rva 0x4AAA358 --slot-count 64 --offset 0x1A8 --access read
py -3.11 -B tools/native_vtable_member_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --vtable-rva 0x4AAA358 --slot-count 64 --offset 0x1A0 --offset 0x1A8 --offset 0x1B0 --access write
py -3.11 -B tools/native_vtable_member_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --vtable-rva 0x4AA9F98 --slot-count 26 --offset 0x418 --offset 0x41C --access read
py -3.11 -B tools/native_vtable_member_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --vtable-rva 0x4AA9F98 --slot-count 26 --offset 0x410 --offset 0x418 --offset 0x41C --offset 0x42C --offset 0x43C --offset 0x44C --access write
py -3.11 -B tools/native_indexed_store_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --displacement 0x1A0 --scale 8 --limit 40
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xAD5A90 --max-slots 64
py -3.11 -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xAD5A90 --limit-per-target 100
py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x40 --require-field 0x941C70 --require-field 0x1A8 --require-field 0x418 --require-field 0x41C --context 12 --limit-per-range 20
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xACB5F0 --size 0x1CE
py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x1A8 --fast-candidates --limit-per-offset 1000
```

Next bounded action: trace an independently anchored writer/callback for the
manager's `+0x1A8` session pointer. Keep the helper `0xAD5A90` unconnected and
do not infer local/network semantics from the repeated predicate. If that
path remains dynamic, continue the independent QAM slot-9 caller and exact
source-dependency gates; 7.06 remains fail-closed.


### QAM multi-field filters, load flag and release-label reconciliation, 18 October 2026

The exact local executable remains Steam build `25732212`, Cosmos 7.06,
file version `180836`, size `88,560,712`, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. The
official [Release Log](https://www.nomanssky.com/release-log/) still lists
Cosmos 7.06 first, then 7.05, with no 7.07 entry. The live [Nexus files page](https://www.nexusmods.com/nomanssky/mods/4579?tab=files)
currently lists `0.10.2-native-test`, file 49469, uploaded 3 October; its
[version-history link](https://www.nexusmods.com/nomanssky/mods/4579?tab=files&version_history=49469)
identifies file 49367 as the earlier `0.10.1-native-test`. The repository's
native profile remains Windows/Steam Cosmos 7.05, build 25624745 and the
recorded 7.05 executable hash. This corrects stale `DEVELOPMENT.md` and
`AGENTS.md` current-package wording. Package and game identities remain
separate; no 7.06 profile or native source mapping changed.

#### QAM slot-9 receiver filter results

Three filters searched slot byte offset `0x48` together with pairs of
RTTI-confirmed QAM fields. Each pass decoded all `52,110,272` `.pdata` bytes,
skipped zero ranges, and returned zero matching ranges and calls:

```text
py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xA050 --require-field 0xA088 --context 12 --limit-per-range 30
py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xA05C --require-field 0xA060 --context 12 --limit-per-range 30
py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xA100 --require-field 0xA104 --context 12 --limit-per-range 30
```

These are bounded same-range displacement negatives. They do not track a
field's base register and do not exclude a caller that simply forwards a QAM
pointer, uses a cached alias or crosses chained ranges. The true slot-9
caller, `R8` meaning and downstream string consumer remain `NOT CHECKED`.

#### Load-candidate flag `+0x4BE6A0`

The fast exact-hash data-offset scan decoded the full `.pdata` inventory with
zero skipped ranges and returned seven heuristic operand hints:

| RVA | Operand | Bounded observation |
| ---: | --- | --- |
| `0x487D1B` | `mov word ptr [rcx+0x4BE6A0],0` | Constructor-root `0x487CE0` clears both adjacent bytes. |
| `0x48FDB7` | byte compare at `[rdi+0x4BE6A0]` | Same load-candidate caller root `0x48FA60`; fast-scan hint. |
| `0x48FEFE` | byte read at `[rdi+0x4BE6A0]` | Same root; fast-scan hint. |
| `0x49069A` | `movzx r9d,byte ptr [rdi+0x4BE6A0]` | Exact decode confirms the byte is passed in `R9B` to `0x573500` at `0x4906BD`. |
| `0x4956B8` | `mov byte ptr [r12+0x4BE6A0],bl` | Exact decode confirms a write from `BL` in root `0x495675–0x49620C`. |
| `0x497A7E` | byte read at `[rdx+0x4BE6A0]` | Separate base; owner relation not established. |
| `0x4A8EF1` | byte compare at `[rax+0x4BE6A0]` | Separate base; owner relation not established. |

The `0x487CE0` constructor has one direct E8 caller at `0x307E08`; its caller
passes `RCX=[global+0xE70]+0xE70`. The batched direct-call scan reports four
direct callers of the already-mapped load predicate `0x495560`, but zero
direct E8 callers of setter `0x495675`. An RTTI probe found zero validated
vtable slots for `0x495675`; separate probes for caller roots `0x2DF30D`,
`0x48E400` and `0x48FA60` also found zero vtable slots. These negatives do not
identify the object's class and do not rule out dynamic dispatch.

The setter's checked reference-form inventory is:

| Reference form | Result for `0x495675` | Scope |
| --- | --- | --- |
| Direct decoded E8 call | 0 | Full `.pdata` call pass; `0x487CE0` has 1 direct call and `0x495560` has 4 in the same pass. |
| Direct RIP-relative memory reference | 0 | `native_rip_xrefs.py`; also 0 for `0x487CE0` and `0x573500`. |
| Validated RTTI-backed vtable slot | 0 | `native_rtti_vtable_probe.py --target-rva 0x495675`. |
| Direct immediate jump | 0 | Full corrected `.pdata` branch pass for `0x495675`, `0x487CE0` and `0x573500`. |
| Literal preferred-base VA pointer | 0 | All seven non-`.reloc` sections for those three targets. |

The setter root at `0x495675` writes a byte from `BL`, and the load caller
passes a byte from a related-looking but not yet owner-proven base in `R9B`.
Do not label the field `network`, infer that the setter is unused, or approve
the load hook from this correlation. Dynamic or relative references and
methods without `.pdata` remain outside the listed scans.

Reproduction against the exact executable (CPython 3.11.9, pefile 2024.8.26,
Capstone 5.0.7):

```text
py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x4BE6A0 --fast-candidates --limit-per-offset 100
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x490620 --size 0x150
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x495675 --size 0x200
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x487CE0 --size 0x180
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x4906BD
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x487CE0 --target-rva 0x495675 --target-rva 0x495560 --context 12 --limit-per-target 20
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495675 --max-slots 64
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2DF30D --max-slots 64
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x48E400 --max-slots 64
py -3.11 -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495675 --target-rva 0x487CE0 --target-rva 0x573500 --limit-per-target 30
py -3.11 -B tools/native_branch_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495675 --target-rva 0x487CE0 --target-rva 0x573500 --context 8 --limit-per-target 30
py -3.11 -B tools/native_absolute_pointer_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495675 --target-rva 0x487CE0 --target-rva 0x573500 --limit-per-target 30
```

The first `native_branch_xrefs.py` invocation omitted the scanned-byte
increment. Discard its reported totals; the code was corrected and the
command above was rerun. The corrected result is `52,110,272` scanned bytes,
zero skipped ranges and zero direct jumps for all three targets. One initial
`native_rtti_vtable_probe.py` invocation repeated `--target-rva`; only its
last target was processed. The three individual commands above replace that
partial attempt. A raw absolute-pointer pass initially used a one-off Python
here-string; the reusable helper above records the same check and expands it
to all three targets.

Tool digests for this follow-up: `native_vcall_xrefs.py`
`24A792FCE464FD6639A3DE92923FCD31BC1BBBB6427ACB0B866FC97308174621`;
`native_data_offset_xrefs.py`
`DF3F6D4CFEFB98E084EFED9DDE49D355F4946914649AE26DBAC07F38B6B64FB2`;
`native_function_disasm.py`
`26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0`;
`native_pdata_function_group.py`
`FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26`;
`native_call_xrefs.py`
`7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`;
`native_rtti_vtable_probe.py`
`4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028`;
`native_rip_xrefs.py`
`DBFF203DC5748821D69C66B1E4C8F75BA91044E36A45DAA77C343BE2207D08A3`;
`native_branch_xrefs.py`
`FA8DBC157E094F8C793A29E46AFA0946059F69AD7070218E6D72452D9914034E`;
`native_absolute_pointer_xrefs.py`
`5E6F37D2DEDF74B5691C537B4E1F19908926DD76062686EECB5A14E516BC5F46`.
No external pattern data was consulted for these focused owner/field scans;
the pinned provider and its data hash remain recorded in the report header.

`NOT CHECKED`: the owner/class for all `+0x4BE6A0` accesses, semantic meaning
of the byte, dynamic caller/registration for `0x495675`, true QAM slot-9
caller and `R8` contract, local-versus-network load behavior, exact-source
dependency completion, and all live 7.06 behavior. No game source mapping or
compatibility profile changed. Next bounded action: find an independently
anchored producer/dynamic registration for `0x495675`, or close the source
ledger's other unresolved dependency if that path remains dynamic; keep 7.06
fail-closed.

### Load-flag root correction and current release check, 22 October 2026

The exact executable remains Steam build `25732212` / Cosmos 7.06, file
version `180836`, size `88,560,712`, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. The
earlier follow-up used chained range entry `0x495675` as the function root.
Resolving chained unwind metadata shows it belongs to the 14-range function
group rooted at `0x495640`. The earlier zero-caller/reference counts against
`0x495675` were scoped to a non-root range entry; they did not show that the
writer was unused.

The corrected full `.pdata` call scan finds one direct E8 caller of root
`0x495640` at `0x4955F8` in the chained body of root `0x495560`. Root
`0x495560` has four direct E8 callers. At `0x4955F8` the code follows a
session-like pointer through application member `+0x941C70` and manager
member `+0x1A8`, checks state `+0x418 == 4`, calls virtual slot offset
`+0x40`, and combines its result with leading byte `+0x41C`. It passes the
result in `R9B` to `0x495640`. The exact dynamic type of the global object's
session remains unproven, so the predicate's meaning is not established.

At `0x495640`, incoming `RCX` is preserved in `R12`, `R9B` is copied to
`BL` and stored at `[R12+0x4BE6A0]` at `0x4956B8`. Later in the same chained
group, the routine calls reader `0x48FA60` at `0x497648` with `RCX=R12`.
That reader preserves the same object in `RDI`, loads `[RDI+0x4BE6A0]` at
`0x49069A`, then passes the byte in `R9` to load-role candidate `0x573500`
at `0x4906BD`. Setter and reader share an object base; local/network meaning
and live effect remain unproven.

Against corrected root `0x495640`: direct E8 callers 1 (`0x4955F8`); direct
RIP-relative references 0; validated RTTI-vtable slots 0; direct immediate
jumps 0; literal preferred-base VAs 0. A raw 32-bit RVA pass found five
`0x495640` and five `0x495675` values in `.rdata`; all matched `.pdata`
Begin/End/Unwind triples, so these are unwind metadata, not pointers.
`0xAD5A90` had zero raw RVA hits. Call, RIP and branch scans decoded
`52,110,272` `.pdata` bytes with zero skipped ranges; the absolute-VA scan
covered seven non-`.reloc` sections (`88,155,208` bytes).

The reusable raw-RVA classifier is `tools/native_rva_data_xrefs.py`,
SHA-256
`C1B88B6910DAD1FF0D2EF556A2C94C58B94F04E0B06B20253CDD561F94CE123D`.
Reproduce the root and classification checks with:

```text
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x495675
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495640 --target-rva 0x495560 --context 12 --limit-per-target 20
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x495560 --size 0xC0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x495640 --size 0xC0
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x497648
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x48FA60 --size 0xD00
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x490620 --size 0x150
py -3.11 -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495640 --limit-per-target 100
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495640 --max-slots 64
py -3.11 -B tools/native_branch_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495640 --context 8 --limit-per-target 100
py -3.11 -B tools/native_absolute_pointer_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495640 --limit-per-target 100
py -3.11 -B tools/native_rva_data_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495640 --target-rva 0x495675 --target-rva 0xAD5A90 --limit-per-target 100
```

Analysis used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7. The
official [Hello Games release log](https://www.nomanssky.com/release-log/)
was rechecked on 22 October 2026: Cosmos 7.06 remains the newest listed
patch and no 7.07 entry appears. The live [Nexus files page](https://www.nexusmods.com/nomanssky/mods/4579?tab=files)
still shows `0.10.2-native-test` as the latest public package, last updated
3 October; `0.10.1-native-test` is the earlier file. Package version and
game-build compatibility remain separate identities.

`NOT CHECKED`: exact type identity and producer of the object at
`application+0x941C70+0x1A8`; semantics of `+0x418`/`+0x41C` and the
session-derived byte; whether `0x573500`'s argument means local or network;
indirect references outside the checked encodings; QAM slot-9 caller and
`R8` contract; remaining source-dependency inventory; and live 7.06
behavior. An exact `+0x41C` writer scan was started and reached partial
progress, but was interrupted when its process/session ended. Mark it
`INTERRUPTED / NOT CHECKED`, not as a count or zero result. No source/profile
mapping changed; 7.06 remains fail-closed.

Next bounded action: rerun the `+0x41C` writer inventory using a
bounded-function strategy, inspect candidates only against their RTTI owner
and complete argument path, then resume the remaining menu/resource and
source-dependency gates. Do not repeat zero-reference scans against chained
range entry `0x495675`.

### Steam session-dispatch bridge and access-filter correction, 22 October 2026

The executable remains Windows/Steam Cosmos 7.06, build `25732212`, file
version `180836`, size `88,560,712`, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. The
current research baseline is `f7d97b61fcf152677d0d30de34f6c1b48675c436` on
`compat/cosmos-706-25732212`; native source/profile mappings remain unchanged.

An exact RTTI query validates `.?AVcGcMatchmakingPlayfabSteam@@` at vtable
`0x4AAA358` with 64 slots. Slot 8 points to `0x24B920`, whose unwind group
contains six `.pdata` ranges. Its chained body at `0x24B949` directly calls
`0x22BF00`; `RCX` still carries the manager passed to slot 8. A direct-E8
scan reports one caller of `0x22BF00` at that site and zero direct callers
of `0x24B920`; the latter is expected for a vtable entry and is not an unused-
method result. Root `0x22BF00` preserves the manager in `RSI`, restores it to
`RCX` and calls `0x22B6C0` at `0x22BF82`. The dispatcher at `0x22B6C0`
enumerates its event queue and selects objects through
`manager + index*8 + 0x1A0`, comparing each selected object's `+0x630` with
the event key. This closes a static Steam-slot-to-session-dispatch path; it
does not establish when the slot runs or the semantic meaning of session
fields `+0x418/+0x41C`.

Exact RTTI checks also validate base `Session` at vtable `0x4AAA640` (19
slots) and derived `PlayfabSession` at `0x4AA9F98` (26 slots). The earlier
`native_vtable_member_xrefs.py --access write` scan incorrectly returned
zero for `Session+0x41C`. Its `--access any` output labelled
`movups xmmword ptr [rcx+0x41c], xmm0` as `R`, even though the exact decode
shows the memory operand is the instruction destination. In root `0xACA370`,
byte `[rsp+0x20]` is set to zero before the vector is loaded and stored at
`[rcx+0x41c]` at `0xACA3A5`; the remaining 15 source bytes are not proven
zero. This is a base-`Session` vtable method at slot 11, not proof that this
method receives the load path's object. `PlayfabSession` overrides slot 11.

Both research scanners now correct Capstone 5.0.7's READ-only report for an
explicit MOV/VMOV-family memory destination at operand 0. Re-running the
RTTI-scoped write checks finds one `Session+0x41C` write at `0xACA3A5`, zero
`PlayfabSession` writes to the checked `+0x410/+0x418/+0x41C/+0x42C/+0x43C/
+0x44C` offsets across its 18 `.pdata` method roots, and zero Steam-manager
writes to `+0x1A0/+0x1A8/+0x1B0` across 36 roots. The last two remain bounded
negatives after the classifier correction. Methods without `.pdata` (15
Session slots, 8 PlayfabSession slots and 27 Steam-manager slots), aliases,
non-vtable routines and dynamic offsets remain outside these searches.

A `native_vcall_xrefs.py` scan requiring both slot offset `0x58` and field
displacement `0x41C` decoded all `52,110,272` `.pdata` bytes with zero skipped
ranges and found zero matching function ranges. This does not rule out a
caller that lacks the same-range field reference. The completed global fast
`+0x41C` shortlist from the preceding pass returned 207 operand candidates.
Shortlisted copy helper `0x249F80` writes a 64-byte block beginning at
`+0x41C`, but all three checked callers pass a source whose leading byte was
cleared; it is not evidence of a positive flag setter. A detailed global
writer scan previously emitted progress through `0xF036E0` without a final
summary. A repeated fast invocation in this work period emitted progress
through `0x1903DA7` but no final summary was captured. Mark both incomplete
invocations `NOT CHECKED`; do not use them as match counts. The earlier
completed fast count of 207 remains the only usable global shortlist result.

Reproduction against the exact executable (`CPython 3.11.9`, pefile
`2024.8.26`, Capstone `5.0.7`):

```text
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcMatchmakingPlayfabSteam@@" --max-slots 64
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVSession@cGcMatchmaking@@" --max-slots 64
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVPlayfabSession@cGcMatchmakingPlayfab@@" --max-slots 64
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x24B949
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x24B8F0 --size 0x100
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x22BF00 --target-rva 0x24B920 --context 12 --limit-per-target 30
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x22BF00 --size 0x110
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x22B6C0 --size 0x180
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xACA370 --size 0x240
python -B tools/native_vtable_member_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --vtable-rva 0x4AAA640 --slot-count 19 --offset 0x41C --access write
python -B tools/native_vtable_member_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --vtable-rva 0x4AA9F98 --slot-count 26 --offset 0x410 --offset 0x418 --offset 0x41C --offset 0x42C --offset 0x43C --offset 0x44C --access write
python -B tools/native_vtable_member_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --vtable-rva 0x4AAA358 --slot-count 64 --offset 0x1A0 --offset 0x1A8 --offset 0x1B0 --access write
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x58 --require-field 0x41C --context 8 --limit-per-range 20
```

Corrected helper SHA-256 values: `native_vtable_member_xrefs.py`
`E621C1062B52E08A3CD8F3AB2F9844E8E8BE78487D08D998A60AC840EF482CBC` and
`native_data_offset_xrefs.py`
`5D3F80C87679DCF6DD41BDE71F027628EB6AF24FC6EE06ECF32924E63FAC34B8`.
The previous `native_vtable_member_xrefs.py` digest
`D9AEAFE567107AAB5C77A6F8A2B91E0C9B40543435C9D459F55BF25C3BC7AC7B`
produced the false zero for the Session store. No external pattern data was
used for this focused owner/field follow-up; the pinned provider remains
recorded in the report header.

The official [Hello Games release log](https://www.nomanssky.com/release-log/)
was rechecked on 22 October 2026 and still lists Cosmos 7.06 first with no
7.07 entry. The [Nexus files page](https://www.nexusmods.com/nomanssky/mods/4579?tab=files)
still lists `0.10.2-native-test`, last updated 3 October; the package remains
separately identified from game compatibility.

`NOT CHECKED`: whether the load path's `+0x1A8` object is the PlayfabSession
instance built by `0xAD5A90`, whether or when Steam slot 8 and Session slot 11
run for that object, the semantic meaning and positive producer of
`+0x41C`, indirect writers outside the checked RTTI method groups, remaining
MenuSelect/resource/source-dependency gates, and live 7.06 behavior. No native
source/profile mapping changed; 7.06 remains fail-closed.

Next bounded action: trace the `+0x41C` positive producer through an exact
PlayfabSession owner path or a caller of base Session slot 11, using the
corrected access classifier. If that remains unanchored, resume the remaining
MenuSelect/resource and source-dependency gates without another broad offset
scan.

### PlayfabSession slot-11 clear path, 22 October 2026

The exact PlayfabSession RTTI table maps slot 11 (`+0x58`) to root
`0x237820`. That method preserves its receiver in `RDI` and calls base Session
method `0xACA370` at `0x237848`. The base method writes a 16-byte value to
`[RCX+0x41C]`; the first source byte was set to zero immediately before the
load. Thus the derived slot-11 method has a statically confirmed path that
zeros the first byte at `+0x41C`. The PlayfabSession vtable scan's zero direct
memory-write count remains accurate for its own method bodies, but it did not
follow this callee and must not be read as “no writes through this method.”

A slot-offset `0x58` scan requiring manager field `+0x1A0` returned 20
function ranges and 25 indirect calls across the full `.pdata` image. One
manager-layout candidate, root `0x2357C0`, calls slot `+0x58` on pointers
loaded from `+0x1A0`, `+0x1A8` and `+0x1B0` at `0x2357DF`, `0x2357EC` and
`0x2357F9`. Its body also clears manager fields and releases stored handles,
so cleanup is a plausible interpretation, not a verified function name or
lifecycle. An exact RTTI target probe found no validated vtable slot for
`0x2357C0`, and a full direct-E8 scan found zero callers. Its dynamic caller,
manager class, and relationship to the specific application object at
`+0x941C70` remain `NOT CHECKED`. Therefore this is a concrete static
zeroing path candidate, not proof that it executes on the load-path session.

The exact PlayfabSession method `0x237820` confirms the override-and-base
call chain. The earlier candidate `0x2357C0` does not yet establish that the
`+0x1A8` object belongs to the same constructed Steam manager used by the
load predicate. Do not promote this cleanup path into a semantic label for
the byte or assume it supplies the byte's positive value.

Reproduction against the exact executable:

```text
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x58 --require-field 0x1A0 --context 8 --limit-per-range 30
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2357C0 --max-slots 64
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2357C0 --size 0x240
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x237820 --size 0x180
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xACA370 --size 0x240
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2357C0 --context 12 --limit-per-target 20
```

`NOT CHECKED`: dynamic invocation and type identity of `0x2357C0`, whether its
`+0x1A8` entry is the exact load-path object, a positive producer for
`+0x41C`, and all source dependency and live 7.06 gates. No source/profile
mapping changed; 7.06 remains fail-closed. Next bounded action: establish the
manager owner/caller for `0x2357C0` or find the positive producer through an
RTTI-anchored PlayfabSession path; then resume the open MenuSelect/resource
gates without a broad offset-only scan.



### Corrected vtable bound, owner chain, and session-clear path, 22 October 2026

This section supersedes the earlier zero-slot result for `0x2357C0`, the
64-slot Steam-vtable count, and the associated unresolved-owner conclusion.
Those results used a `--max-slots 64` probe; they were bounded by the query
limit and did not establish that the function was absent from RTTI tables.

With `--max-slots 96`, exact RTTI validates both
`.?AVcGcMatchmakingPlayfab@@` at vtable `0x4AAA070` and
`.?AVcGcMatchmakingPlayfabSteam@@` at `0x4AAA358`, each with 87 executable
slots. Root `0x2357C0` is slot 80 (`+0x280`) in both. The corresponding
preferred-base pointer locations, `0x4AAA2F0` and `0x4AAA5D8`, equal
vtable start plus `0x280`. The earlier zero RTTI result was a false negative
caused by the 64-slot bound.

The corrected full Steam table scan covers 87 slots. Across its 42
`.pdata` method roots, it finds zero direct writes to manager offsets
`+0x1A0`, `+0x1A8` and `+0x1B0`; 44 slots have no `.pdata` entry and
remain outside that method-body scan. The `+0x1A8` access-any scan finds ten
operands: eight reads in eight method groups, including slot 80, and two
address-only LEAs in slot 8's chained body. Do not treat the vtable write
negative as whole-program proof.

The static owner path now joins the Steam event dispatcher to the application
object used by the load predicate. Six direct callers of `0xAE8D30` pass
`global+0x937130` as `RCX`. The constructor root `0xAE8810` has one direct
caller, at `0x2C6D3F`, which passes the same pointer. The constructor stores
the Steam manager at parent `+0xAB40`; the verified sum
`0x937130 + 0xAB40 = 0x941C70` matches the application member read by the
load predicate. In `0xAE8D30`, the Steam manager's slot 8 is called at
`0xAE8E93`. Its target `0x24B920` reaches `0x22BF00`, which forwards the
same manager to dispatcher root `0x22B6C0`. That dispatcher calls manager
slot 80 (`+0x280`); `0x2357C0` then dispatches slot `+0x58` on manager
entries `+0x1A0`, `+0x1A8` and `+0x1B0`.

For a dynamically typed `PlayfabSession` entry, slot 11 (`0x237820`)
calls base `Session` helper `0xACA370`. The helper stores a 16-byte value
at `+0x41C` after setting its first source byte to zero. This closes a
static path by which the first byte can be cleared through the manager event
route. It does not prove the entry at `+0x1A8` has that dynamic type, when
the route runs, what the byte means, or where its positive value is produced.
The remaining 15 stored bytes are not proven zero.

Session-array helper `0xAD5A90` remains an unconnected population candidate:
the checked direct-call, exact RTTI-slot, literal-VA and RIP-relative probes
did not connect its manager argument to this application manager. Those
scope-limited negatives do not rule out indirect or dynamically registered
call paths. There is still no verified positive producer or semantic name for
`+0x41C`. The native source and compatibility profile are unchanged; 7.06
must remain fail-closed.

Reproduction against the exact executable, using CPython 3.11.9,
pefile 2024.8.26 and Capstone 5.0.7:

```text
python -B tools/native_rtti_vtable_probe.py --exe NMS_EXE --type-name .?AVcGcMatchmakingPlayfab@@ --max-slots 96
python -B tools/native_rtti_vtable_probe.py --exe NMS_EXE --type-name .?AVcGcMatchmakingPlayfabSteam@@ --max-slots 96
python -B tools/native_rtti_vtable_probe.py --exe NMS_EXE --target-rva 0x2357C0 --max-slots 96
python -B tools/native_vtable_member_xrefs.py --exe NMS_EXE --vtable-rva 0x4AAA358 --slot-count 87 --offset 0x1A0 --offset 0x1A8 --offset 0x1B0 --access write
python -B tools/native_vtable_member_xrefs.py --exe NMS_EXE --vtable-rva 0x4AAA358 --slot-count 87 --offset 0x1A8 --access any
python -B tools/native_vcall_xrefs.py --exe NMS_EXE --slot-offset 0x280 --require-field 0x1A0 --context 8 --limit-per-range 30
python -B tools/native_vcall_xrefs.py --exe NMS_EXE --slot-offset 0x40 --require-field 0x941C70 --context 8 --limit-per-range 30
python -B tools/native_call_xrefs.py --exe NMS_EXE --target-rva 0xAE8D30 --target-rva 0xAE8810 --context 12 --limit-per-target 30
```

The corrected research-helper digests recorded for this pass are:
`native_rtti_vtable_probe.py`
`4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028`,
`native_vcall_xrefs.py`
`24A792FCE464FD6639A3DE92923FCD31BC1BBBB6427ACB0B866FC97308174621`,
`native_call_xrefs.py`
`7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`,
and `native_function_disasm.py`
`26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0`.
For full grouped decoding, `native_pdata_function_group.py` is
`FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26`.

`NOT CHECKED`: dynamic type and producer of the exact entry at
`application+0x941C70+0x1A8`; the positive producer and meaning of
`+0x41C`; invocation timing and lifecycle; indirect or dynamically
registered paths not covered by the recorded encodings; remaining
MenuSelect/resource/source-dependency gates; and live 7.06 behavior. The
official [Hello Games release log](https://www.nomanssky.com/release-log/)
was checked on 22 October 2026 and still lists Cosmos 7.06 first, with no
7.07 entry. The [Nexus files page](https://www.nexusmods.com/nomanssky/mods/4579?tab=files)
still lists `0.10.2-native-test`, last updated 3 October. These are separate
game-build and package-version facts.

Next bounded action: trace the dynamic population/type of the exact
`+0x1A8` entry or find its positive `+0x41C` producer through an
RTTI-anchored caller. If that route stays unconnected, continue the open
MenuSelect/resource and exact-source dependency gates. Keep 7.06 fail-closed;
do not change source/profile mappings on this static evidence alone.



### Source-dependency inventory beyond function RVAs, 22 October 2026

A read-only source audit of `native/src/bootstrap.cpp`,
`native/src/runtime.cpp`, `native/src/menu.cpp` and
`native/src/binding_guard.cpp` found fixed game data dependencies that the
old-RVA boundary table does not enumerate. This audit records the source side
of the ledger; it does not map these values to Cosmos 7.06. A confirmed code
entry alone cannot validate the data owner, object layout, array stride,
argument contract or call lifecycle used around it.

The source's code-entry dependencies are the twelve ordinary detours:
`0x14738E0`, `0x14494F0`, `0x508D30`, `0x17521C0`, `0x1481F60`,
`0x572C40`, `0x152FEF0`, `0x15282B0`, `0x152C7D0`, `0x153CF40`,
`0x153A770` and `0x1524330`. The compile-time respawn observer adds
`0x14F7F60` and three return-site filters
(`0x3302C4`, `0x33066F`, `0x330946`). Additional service entries are
`0x508200`, `0x1473060`, `0x14855F0`, `0x14407F0` and `0x9BD8E0`.
Menu and binding code also depends on `0x143B720`, `0x1518EF0`,
`0x2C25B40`, `0x152739B`, `0xEC6850` and `0x2D65980`. Their 7.06
function-role evidence is recorded in the earlier tables and call-path
sections; candidate status must not be promoted to runtime compatibility.

The source also hardcodes these non-entry dependencies:

| Source area | 7.05 source dependencies to revalidate on the exact executable |
| --- | --- |
| Application and player | Global pointer `0x6E89688`; player relation `+0x72C6F0`; location `+0x57A584`; active companion `+0x29A1C0`; queued companion `+0x6020`; player physics `+0x2A8`. |
| Companion roster | Table `+0xE10D0`, stride `0x24A0`, identity fields `+0x2330` and `+0x23C0`, resource field `+0x2370`, biome field `+0x2480`. The iteration limit is 30 entries. |
| Companion owner state | Preview `+0x1B9300` and emote `+0x1B937D`; placement receiver `+0x1B9140`. |
| Location and planet data | Solar-system pointer `app+0x72AFB0`; count and selected index `solar+0x2544` and `solar+0x5196D0`; planet stride `0xD9170`; biome and subtype `planet+0x6148` and `planet+0x614C`. |
| Save and notices | Save identity `common+0x8980`; interaction range `base+0x527AB34`; notice context `app+0x847BB0`; notice conditions `app+0x847BB0+0x28C` and `app+0x4BF50C`. |
| Quick-action menu | Depth `+0xA050`; vector headers `+0xA058` with 16-byte depth stride; selections `+0xA088` with 4-byte stride; icon `+0xA104`; pending state `+0xA16C`; row size `0xE0`/224; item action `+4`, role/slot `+0x84`, 16-byte marker at `+0x88`, binding `+0xD8`, and row-state bytes `+0x4C/+0x4D` and payload validation span `+0x98..+0xD8`. |
| Resource manager and resource object | Manager globals `0x6E1BC10` and `0x5910190`; manager count/table `+0x5C` and `+0x60`; 8-byte handle-table stride; resource type `+0x8`, name blocks from `+0xC` through `+0x108`, error/substitute flags `+0x13A`/`+0x13B`, image `+0x1E0` and texture pointer `+0x260`; `TextureRecord` handle output `+0x10`; bounds include manager size `0x68` and resource size `0x268`. |

This table is the 7.05 source baseline, not a blanket 7.06 status. The QAM and resource paths above have partial static evidence, but that evidence applies only to the specific values and call paths named there. Several planet, roster, manager and resource fields still lack a complete exact-hash owner-and-consumer chain. Carry forward each individually earned status and leave each unmapped row `NOT CHECKED` until its dynamic owner and read/write role are independently tied to the Cosmos 7.06 image. The mod profile remains
the approved Windows/Steam 7.05 profile, and 7.06 remains fail-closed.

Next bounded action: make the source ledger one row per hardcoded function,
global, field, stride, signature and callback, then mark each row with the
exact 7.06 hash, evidence scope, status and required runtime gate. Resolve the
remaining MenuSelect/label caller, load predicate semantics, and data-layout
owners before considering a profile or source change.


### Current source, package and executable identities, 22 October 2026

The installed executable was re-read from
`C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe`:
Steam build `25732212`, file/product version `180836`, size `88,560,712`,
SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
This matches the exact Cosmos 7.06 image used by the prior static ledger.
The official Hello Games release log still places 7.06 first, with no 7.07
entry. Nexus still lists public package `0.10.2-native-test`, last updated
3 October 2026. The GitHub default branch `main` currently points to
`f7d97b61fcf152677d0d30de34f6c1b48675c436` (3 October), matching this
worktree's baseline HEAD; no newer upstream source commit was found. These
are separate identities: game release/build/hash, Nexus package version and
Git source revision must not be substituted for one another.

The active native profile is `native_compatibility.json` and still targets
Cosmos 7.05 / Steam build `25624745` / SHA-256
`671de22649274b49fa07f5a246bc7252c4e08bb9ab623d2e65722fbab4e497a4`.
Root `compatibility.json` belongs to the legacy Python runtime and remains
Cosmos 7.04 / build `25442159` / SHA-256
`b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`.
Do not update the legacy profile when updating the native target. Neither
profile has been changed for 7.06.

The attempted caller scan with `--context 16` was rejected by argument
validation because `native_call_xrefs.py` accepts at most 12 context
instructions. It decoded no executable bytes and produced no search result.
The corrected `--context 12` run against the exact hash decoded
`52,110,272` `.pdata` bytes with zero skipped ranges and found one direct
E8-style caller of `0xACA370`, at `0x237848` inside PlayfabSession slot-11
root `0x237820–0x237993`. That method calls the base Session helper. The
helper sets only byte `[rsp+0x20]` to zero before loading a 16-byte stack
value and storing it at `[this+0x41C]`; the other 15 bytes are not proven
zero. This confirms only a partial clear path. It does not establish the
field's meaning, a positive producer, the dynamic type of the load-path
`+0x1A8` entry, or runtime invocation.

Reproduction against the verified executable:

```text
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0xACA370 --context 12 --limit-per-target 100
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x237820 --size 0x180
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xACA370 --size 0x240
```

`NOT CHECKED`: a positive `+0x41C` producer and its semantics; whether the
exact load-path entry takes this derived slot-11 route; local/network meaning
and invocation timing; the remaining QAM label, resource, binding, source
dependency and live 7.06 gates. No source, native profile or package changed;
7.06 remains fail-closed. Next bounded action: continue the independent QAM
label/output-buffer and remaining source-dependency gates. Do not repeat the
rejected `--context 16` call or widen the global `+0x41C` offset scan.


### QAM slot-9 output ABI narrowed from its exact body, 22 October 2026

The exact `cGcQuickActionMenu` slot-9 target `0x153C0C0` is rooted in a
three-range unwind group (`0x153C0C0–0x153C0FD`,
`0x153C0FD–0x153C24C`, `0x153C24C–0x153C5E4`). Its entry immediately writes
zero to the byte addressed by `R8` (`mov byte ptr [r8], 0`). The original
`R8` pointer is not saved, and later `R8` values are set up for separate
calls. The method saves incoming `RDX` in `R14`, has a branch that clears
`[RDX]`, and later passes `R14` as the destination receiver to a string
assignment helper with a localized source and length. This narrows the
static caller contract: `RCX` must be the QAM receiver, `RDX` the string
output object, and `R8` a writable byte address at dispatch. The byte's
semantic meaning and the identity of a real caller remain `NOT CHECKED`.

This body evidence improves caller triage but does not make prior
same-function `+0xDC0` hits valid: they still fail the proven receiver
identity or register-liveness checks. Do not label the `R8` byte as a
specific boolean or enum without an exact caller or downstream consumer.

Reproduction against the exact executable:

```text
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153C0C0 --max-slots 30
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0C0
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0C0 --size 0x300
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C3B7 --size 0x22D
```

`NOT CHECKED`: the true slot-9 caller, the meaning and lifetime of its `R8`
byte, downstream icon/resource use, safe call timing, remaining source
dependencies and live 7.06 behavior. Next bounded action: use the three-part
receiver/string/byte ABI to narrow candidates, then prove all three inputs
survive intervening calls before accepting a caller. Keep 7.06 fail-closed.

### QAM slot-9 owner-offset filter false lead, 22 October 2026

A new exact-hash virtual-call pass filtered slot byte offset `0x48` together
with the verified enclosing-owner displacement `+0x116B10`
(`+0x115D50` quick-menu wrapper plus `+0xDC0` QAM child). It decoded all
`52,110,272` `.pdata` bytes, skipped zero ranges and returned one function
range, `0x924C90–0x924DFF`, containing two slot-offset calls at
`0x924CE0` and `0x924CED`. This filter proves only that both operands occur
in the same function range.

The root-aligned decode rejects both calls as slot-9 candidates. Their
receivers are loaded separately from `[RDI+0x110998]` and
`[RDI+0x1109A0]`. The `+0x116B10` child address is formed later at
`0x924D60` and passed to cleanup helper `0x1527BD0` at `0x924D67`; it is
not either virtual-call receiver. Earlier calls also invalidate any carried
`RDX` or `R8` argument values, and the dispatch sites show no final
string-output or writable-byte setup. This is a useful false lead, not a
zero-caller result.

Tool corrections: `py -3.11` returned `No installed Python found!` before
opening the executable. The installed CPython 3.11.9 was available as
`python`; the corrected read-only scan completed. A first disassembly window
of `0x180` bytes extended past this `.pdata` entry, so it was repeated with
the exact entry size `0x16F`; conclusions above use only
`0x924C90–0x924DFF`. Tool versions were CPython 3.11.9, pefile 2024.8.26
and Capstone 5.0.7. `native_vcall_xrefs.py` SHA-256:
`24a792fce464fd6639a3de92923fcd31bc1bbbb6427acb0b866fc97308174621`.

Reproduction against the verified Cosmos 7.06 executable:

```text
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0x116B10 --context 12 --limit-per-range 100
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x924C90 --size 0x16F
```

The local checkout is branch `compat/cosmos-706-25732212` at HEAD
`f7d97b61fcf152677d0d30de34f6c1b48675c436`. Git `status` repeatedly
returned `fatal: this operation must be run in a work tree`, so the full
working-tree diff state is `NOT CHECKED`; no native source or compatibility
profile was edited in this analysis. The GitHub connector also failed
authentication during a fresh read. The current remote `main` tip is
therefore `NOT CHECKED` in this handoff; the earlier same-day readback is
retained as prior evidence, not refreshed evidence.

`NOT CHECKED`: the true slot-9 caller, the meaning/lifetime of `R8`, the
safe resource-ready callback, binding-filter return role, local-versus-network
load semantics, full remaining dependency ledger and live 7.06 behavior.
Next bounded action: trace a proven QAM child pointer from its owner or a
verified receiver argument into a slot-`0x48` dispatch, then confirm the
final `RDX`/`R8` definitions survive every intervening call. Do not repeat
the `+0xDC0` or `+0x116B10` same-function filters without a new dataflow
anchor. Keep 7.06 fail-closed.


### Release-readiness snapshot and fresh version check, 22 October 2026

A fresh read of the official Hello Games release log still lists Cosmos 7.06
first; no 7.07 entry is present. The installed Steam executable was read
again: file/product version 180836, size 88,560,712, SHA-256
13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
It still matches the exact 7.06 image used by this report. Nexus still lists
0.10.2-native-test, last updated 3 October; that public package supports
the earlier Steam 7.05 build 25624745, not this 7.06 executable.

Current estimate for preparing a 7.06 release: about 10% (a planning estimate,
not a compatibility score). The exact target and substantial partial static
research are in hand, but the release-critical work is not complete:
the exact-source dependency ledger is unfinished; multiple function and data
mappings and their local/network semantics remain unverified; source/profile
changes have not been made; no 7.06 offline validation, build or archive has
been produced; and no exact-archive live 7.06 check has been performed.
Release documentation and GitHub/Nexus readbacks for a 7.06 package are also
not done. Therefore the amount of 7.06 compatibility verified for release is
still 0%, and the profile remains fail-closed.

Git status now reads correctly. Branch compat/cosmos-706-25732212 remains
at f7d97b61fcf152677d0d30de34f6c1b48675c436; pre-existing modified and
untracked research/source-tool files were preserved. This handoff changed
documentation only; no native source, compatibility profile or package was
changed. No tests or game operations were run.

A fresh git ls-remote read of public GitHub main failed before returning a
ref with getaddrinfo() thread failed to start; the public GitHub commits page
also returned a cache miss. This is a network/read failure, not evidence of
an unchanged remote. Keep the current remote main tip NOT CHECKED until
a successful readback.

Next bounded action: complete the exact-build per-dependency ledger from the
existing source inventory, prioritizing dependencies that gate startup,
summoning and safe menu/resource initialization. Reuse only hash-matched
evidence, mark unresolved rows NOT CHECKED, then port and validate only
mappings whose owner, call contract and runtime role are established. Do not
spend another pass on the rejected QAM same-function filters without a new
receiver/data-flow anchor.

### Menu-label hook ABI compared with the source wrapper, 22 October 2026

A focused source review confirms why the QAM label path matters to this port.
In bootstrap.cpp, the saved original label function uses the two-argument
type (void*, void*), and labelHook forwards only (menu, output) before calling
MenuAdapter::afterLabel. In menu.cpp, afterLabel may replace that output with
a 128-byte ASCII caption after checking the selected menu state.

The 7.06 slot-9 candidate at 0x153C0C0 has a different statically recovered
contract: RCX is the QAM receiver, RDX is the localized-string output, and
R8 points to a byte written at function entry. The output is bounded to 256
bytes. The real virtual caller, R8 meaning/lifetime, and exact output ownership
are still NOT CHECKED. Therefore matching the role name “label” is not enough
to replace the old RVA or change the profile. The source detour must preserve
the third argument when forwarding the original, and the replacement write
must respect the actual output capacity.

This establishes the label path as a source-port dependency, rather than a
translation-only question. Required evidence before editing: a real callsite
with receiver and RDX/R8 setup; proof that the 256-byte destination is the
field the mod intends to customize; and a compatible detour/post-hook contract.


### Source dependency gate ledger, 22 October 2026

This is the first per-dependency gate table derived from the four game-facing
native source files. `MAPPED` means the static 7.06 owner/call/field contract
is corroborated; it does not mean live compatibility. `PARTIAL` means a
candidate exists but a caller, semantic, ABI or lifecycle question remains.
`NOT CHECKED` means no usable 7.06 evidence is recorded. The separate
implementation, offline-validation, live-runtime and release gates remain
open for every row until evidenced. Detailed disassembly, commands and false
leads remain in the sections linked by each role; this table is the short
progress index, not a replacement for that evidence.

#### Function entries, direct calls and return-site filters

| Stable source role | 7.05 source dependency | 7.06 state and evidence anchor | Remaining gate |
| --- | ---: | --- | --- |
| QueuePet hook | `0x14738E0` | MAPPED: candidate `0x1475790`; QAM call, owner slot and player-update path agree. | ABI/lifecycle and exact-build runtime behavior. |
| Player update hook | `0x14494F0` | MAPPED: candidate `0x144B3A0`; unique signature and pending-slot processing body. | Hook lifecycle and exact-build runtime behavior. |
| Ownership update hook | `0x508D30` | MAPPED: replacement `0x508DC0`; owner/delta caller and chained body. The old RVA is rejected. | Hook lifecycle and exact-build runtime behavior. |
| Ship eject hook | `0x17521C0` | MAPPED: candidate `0x1754180`; receiver plus `R8B`/`R9B` Boolean ABI matches source, and ordinary direct callers pass the application local-player pointer in `RDX`. | Confirm exact-process hook lifecycle, thread and live auto-summon timing. |
| Entered-cockpit hook | `0x1481F60` | MAPPED: candidate `0x1483E20`; one `this` player pointer in `RCX`, three direct callers pass `app+0x72C6F0`. | Confirm exact-process hook lifecycle and live state-reset behavior. |
| Save-load hook | `0x572C40` | MAPPED for guarded source contract: target `0x573500`, six physical slots with opaque byte slots 4/5 forwarded, slot 6 retained without semantic naming, Boolean result. Exact return `0x4906C2`, vtable and `app+0xB940` receiver exclude the known DeathState caller; source fourth byte must be zero. Applied-state gating was rejected by r2 timing evidence. Deferred readiness remains authoritative. | Exercise corrected candidate; callback identity is not a general network classifier or completed-load event. |
| Quick-action trigger hook | `0x152FEF0` | MAPPED: QAM `TriggerAction` candidate `0x1531E00` and static callers. | Detour lifecycle and exact-build runtime behavior. |
| Quick-menu builder hook | `0x15282B0` | MAPPED: builder candidate `0x152A1C0`, item creation and owner path corroborated. | Hook lifecycle and live menu behavior. |
| Quick-menu label hook | `0x152C7D0` | MAPPED: RTTI-confirmed QAM slot 9 `0x153C0C0` has one direct caller at `0x1529288`; `RCX=QAM`, `RDX=256-byte label buffer`, `R8=adjacent byte at buffer+0x100`. Source callback now forwards all three arguments; its installed RVA is still the 7.05 value. | Add the 7.06 target only in a verified build-specific profile; preserve the opaque byte and verify hook/thread/UI behavior. |
| Quick-menu append hook | `0x153CF40` | MAPPED: append candidate `0x153EE50`, function entry and vector-header contract corroborated. | Hook lifecycle and live menu behavior. |
| Quick-menu confirmation hook | `0x153A770` | MAPPED: slot-6 candidate `0x153C680` and selected-item Boolean behavior. | Hook lifecycle and live menu behavior. |
| Quick-menu resource hook | `0x1524330` | MAPPED: replacement `0x1526240`; QAM child and native resource-handle dataflow corroborated. | Thread, repeat-call, reload/destruction and live texture behavior. |
| Experimental respawn observer | `0x14F7F60` | MAPPED for three physical inputs at `0x14F9E20`, complete stack-home alias audit and exact return filters `0x330314/0x3306BF/0x330996`. The experimental trial retains reason 11/flag 1 at the first return and additionally requires the applied LocalLoadState. | Exact candidate behavior, completion and multiplayer semantics remain open; no death/respawn trigger is introduced. |
| Respawn return filter 1 | `0x3302C4` | MAPPED statically: LocalLoadState call `0x33030F` returns to `0x330314`; its case-8 path passes third argument 1. Retained 22 October caller/CFG evidence; the old return is not a boundary. | Verify reason 11, event/completion semantics, observer ABI and exact-build live behavior separately; do not infer completed death/respawn from the helper name. |
| Respawn return filter 2 | `0x33066F` | MAPPED statically: LocalLoadState call `0x3306BA` returns to `0x3306BF`, third argument 0. Retained 22 October decoded-call evidence. | Preserve the intended caller filter; verify observer ABI, event semantics and live behavior. |
| Respawn return filter 3 | `0x330946` | MAPPED statically: LocalLoadState call `0x330991` returns to `0x330996`, third argument 0. Retained 22 October decoded-call evidence. | Preserve the intended caller filter; verify observer ABI, event semantics and live behavior. |
| CanSummon service | `0x1473060` | MAPPED: candidate `0x1474F10`, called from QAM trigger with owner and slot; result tested. | Exact-build runtime behavior. |
| OwnedPetEligible service | `0x508200` | MAPPED: leaf `0x508290`, with owner/slot callers and Boolean eligibility body; old RVA rejected. | Exact-build runtime behavior and source-field reconciliation. |
| RefreshPlacement service | `0x14407F0` | MAPPED: candidate `0x14426A0`; caller setup and register ABI match the source wrapper. | Exact-build runtime behavior. |
| Dominant-hand service | `0x14855F0` | MAPPED: candidate `0x14874B0`; source no-argument call shape checked at the machine-code boundary. | Exact-build runtime behavior. |
| AddTimedMessage service | `0x9BD8E0` | MAPPED for source ABI at `0x9BF7B0`; exact body/callsite ABI overrides the conflicting provider name. | UI side effects and exact-build runtime behavior. |
| Menu item constructor | `0x143B720` | MAPPED: candidate `0x143D5D0`, 224-byte item construction and caller setup corroborated. | Remaining item fields and live menu behavior. |
| Menu selection setter | `0x1518EF0` | MAPPED: candidate `0x151ADB0`, depth/index bounds, write and three QAM callers corroborated. | Hook lifecycle and live menu behavior. |
| Texture loader service | `0xEC6850` | MAPPED: candidate `0xEC8700`; `TextureRecord` path/handle ABI corroborated. Old RVA rejected. | Exact source call/lifecycle and live resource behavior. |
| Companion icon retain/release service | `0x2D65980` | MAPPED: retain `0x2D69720` and release `0x2D65A80` use the same resource-manager global, handle table, and `+0x134` reference count; both take a pointer to a 32-bit handle. | Preserve the exact-executable hash gate and file-vs-live-memory prefix check; verify readiness, lifetime and live icon rendering. |
| GetButton hook guard | `0x2C25B40` | MAPPED: current method candidate `0x2C298E0`; QAM call/return path corroborated. | Verify actual-process guard and live input behavior. |
| Binding-filter return site | `0x152739B` | MAPPED statically: return `0x15292F5` follows the verified GetButton call, with QAM in `RDI` and the exact depth/selection/vector/item reads used by the generated filter. This normalizes the ledger to its retained static caller/layout proof; no new binary match is claimed. | Confirm live filter result, thread and input lifecycle. |

#### Runtime, companion and placement data

| Stable source role | 7.05 source dependency | 7.06 state and evidence anchor | Remaining gate |
| --- | ---: | --- | --- |
| Application pointer global | 7.05 `0x6E89688` | MAPPED: the 7.06 application pointer is at `0x6E8D708`; `0x1474F10` loads it before using `+0xE10D0`, corroborated by the session path at `0x4955AD`. | Port the exact value in a build-specific way and tie every app-relative consumer to its owner. |
| Load policy: applied-state cell | New 7.06 policy `base+0x6E8D6E0`, 8 bytes | MAPPED: FSM current pointer is manager `+0x10`; the owner-proven Update applies the pending state before dispatch. Passive capture observes the exact LocalLoadState object during a confirmed local save load. | Exercise the actual candidate guard and keep network/event interpretation separate. |
| Load policy: state object | New 7.06 policy `base+0x6E8EA40` | MAPPED: the constructor/registration chain identifies the application LocalLoadState; the confirmed load trace enters and exits this exact object. | Verify synchronous hook timing and the candidate archive. |
| Load policy: state vtable | New 7.06 policy `base+0x4A50A30`, 8-byte comparison | MAPPED: RTTI-confirmed LocalLoadState vtable, checked successfully by every accepted lifecycle sample. | Verify candidate refusal on changed/unreadable identity. |
| Load policy: local receiver | New 7.06 policy `app+0xB940` | MAPPED: constructor-derived cGcPlayerState address matches all four discovered direct load-candidate receivers; the policy checks the incoming receiver against this exact application subobject. | Verify actual hook behavior; this receiver check is not a general multiplayer classification. |
| Load policy: callback return | New 7.06 policy `base+0x4906C2` | MAPPED: return after the verified call at `0x4906BD` in root `0x48FA60`; r2 recorded this exact caller, matching receiver, zero source byte, success and readable nonzero common key during owner-confirmed load. The distinct known DeathState return is rejected. | Corrected candidate must produce a deferred load opportunity and visible pet; general network semantics remain open. |
| Local-player pointer | `app+0x72C6F0` | MAPPED statically: the placement candidate reads it from the exact 7.06 application object. | Confirm local-player identity and behavior in the live path. |
| Location value | `app+0x57A584` | MAPPED statically: exact helper `0x50A520` reads this from global `0x6E8D708` and branches on the location value. | Confirm exact source enum meanings and live behavior. |
| Active companion slot | `app+0x29A1C0`, 4 bytes | MAPPED: exact application global `0x6E8D708`; setter stores a 0–29 roster slot, clearer stores `-1`, and a consumer passes the value to the roster-index helper. | Confirm transition timing and behavior in the live local-player path. |
| Queued companion slot | `player+0x6020` | MAPPED: queue and player-update candidates read/write this request slot. | Confirm runtime trigger timing and state lifecycle. |
| Companion roster pointer | `app+0xE10D0` | MAPPED: QAM eligibility path uses this table. | Verify exact live owner and roster lifecycle. |
| Companion roster stride | `0x24A0` | MAPPED: exact candidate indexes the table using this stride. | Confirm all runtime readers use the same record type. |
| Source identity component 1 (source name: seed) | `entry+0x2330`, 8 bytes in source | MAPPED statically: `0x50E1A0` redefines `RDI` as `app+0xE10D0+roster_index*0x24A0` before its 16-byte read at `0x50E9D5`. Independent roster copier `0x506500` passes row `+0x2320` to `0x227E80`, which copies 16 bytes at subobject `+0x10`. The old resolver-result interpretation is superseded by the 23 October handoff. | Source uses only the first 8 of 16 native bytes. Verify semantic naming, identity uniqueness/persistence and live favorite restoration separately. |
| Source identity component 2 (source name: birth) | `entry+0x23C0` | MAPPED statically: exact slot-indexed consumers use the same roster base and `0x24A0` stride, reading/writing 8 bytes. The internal semantic name is unverified. | Confirm value semantics and exact-build runtime behavior. |
| Companion resource field | `entry+0x2370` | MAPPED statically: eligibility and summon-support paths read this field; eligibility requires nonzero. | Confirm source interpretation and exact-build runtime behavior. |
| Source habitat field | `entry+0x2480` | MAPPED statically: exact slot-indexed helper reads a 32-bit value from this row field. `entry+0x2488` is a separate field. | Confirm biome/enum meanings and exact-build runtime behavior. |
| Companion iteration limit | `30` entries | MAPPED statically: exact 7.06 helpers reject slot indices 30 and above. | Confirm bounds against live roster size and all source loops. |
| Owner preview/active-slot field | `owner+0x1B9300` | MAPPED statically: `owner=app+0xE10D0`, so this is `app+0x29A3D0`. The native menu consumer initializes/clears it to -1 at `0x1543512/0x1543646`, writes the selected eligible row slot at `0x154361F`, and the owner-update consumer treats -1 as absent and otherwise uses the slot. See the 23 October composite-address handoff. | Verify selected-preview behavior and source cancellation timing live; do not conflate it with the separate active companion slot. |
| Owner emote/busy guard | `owner+0x1B937D`, 1 byte | MAPPED statically as a menu-driven placement/preview guard: the same byte is `app+0x29A44D`; native code sets it at `0x1543703` when selected action is `0x22`, menu selector is nonzero and helper `0x50A220` succeeds, otherwise clears it at `0x154373C`. Owner update `0x5090D9` consumes the byte to select its placement/preview path. | Verify live meaning and timing; the source name emote is not independently established. Keep native eligibility and placement checks. |
| Owner placement receiver | `owner+0x1B9140` | MAPPED: placement caller passes this subobject to the ABI-checked candidate. | Confirm exact-build live placement behavior. |
| Player physics pointer | `player+0x2A8`, 8 bytes | MAPPED statically: placement candidate `0x14426A0` derives player from app global `0x6E8D708` plus `0x72C6F0` and reads this qword before passing it to helper `0x142CE6FD0`. | Confirm pointer identity/lifecycle with the local player in the live path. |
| Solar-system pointer | `app+0x72AFB0` | MAPPED statically: exact consumers `0x50A520` and `0x2B3A10` load it through application global `0x6E8D708`. | Confirm runtime object lifetime and replacement across transitions. |
| Solar-system planet count | `solar+0x2544`, 4 bytes | MAPPED statically: `0x2B3A10` reads it and clamps the chosen index to `count-1`; `0x2C4710` independently bounds a planet loop with it. | Confirm live boundary behavior for all supported locations. |
| Selected planet index | `solar+0x5196D0`, 4 bytes | MAPPED statically: `0x2B3A10` reads it, treats it as an index and bounds it against the count. | Confirm the producer and behavior during transitions/live play. |
| Planet-array stride | `0xD9170` | MAPPED statically: `0x2B3A10` multiplies the bounded index by this stride before reading fields; `0x2C4710` independently uses it for planet iteration. | Confirm the containing object/layout in live transitions; do not substitute the separate `solar+0x2E30` result base from `0x2C4710` for the direct `0x2B3A10` field base. |
| Planet biome field | `solar+index*0xD9170+0x6148`, 4 bytes | MAPPED statically: `0x2B3A10` reads this exact displacement after deriving the app and solar pointers. | Confirm the full enum mapping and live values. |
| Planet subtype field | `solar+index*0xD9170+0x614C`, 4 bytes | MAPPED statically: `0x2B3A10` reads this dword and special-cases `0x19` and `0x1A`; the source semantic name remains to be validated. | Confirm the enum mapping and live values. |
| Save identity field | `common+0x8980`, 8 bytes | MAPPED statically: initializer `0x2A0CB70` clears the qword; save helper `0x57AE60` copies `playerState+0x187E8` into `common+0x8980`; load candidate `0x573500` copies it back to `playerState+0x187E8`. The `0x2E088F` caller passes the same initialized local object to the save and load paths. | Confirm live values establish the same per-save identity used by favorites; local/network invocation semantics remain a separate load-hook gate. |
| Interaction range field | source `base+0x527AB34` | MAPPED statically: exact owner-update consumer loads a 4-byte scalar from `0x527EB74` at `0x509190` and passes it through both XMM inputs to placement candidate `0x14426A0` at `0x5091A5`; its owner and receiver match the 7.05 placement path. The candidate is virtual-only BSS, not raw-backed. | Verify its runtime value, units and placement behavior in a controlled live run. |
| Notice context | `app+0x847BB0` | MAPPED statically: direct caller `0x3BD8EB` loads the application pointer from global `0x6E8D708` and passes `app+0x847BB0` as `RCX` to `0x9BF7B0`. | Confirm notification lifetime, thread and live UI behavior. |
| Notice vector count | `app+0x847BB0+0x28C` | MAPPED statically: 4-byte count in a vector header with capacity at `+0x288` and data pointer at `+0x290`; insertion helper `0x9D8790` increments it, records use stride `0x2F0`, and cleanup root `0x8A49A0` clears it. `0x9BF7B0` rejects counts above 3 and compares the last message before appending. | Confirm lifecycle and exact-build live behavior. |
| Notice global condition | `app+0x4BF50C` | MAPPED statically: `0x9BF7F9/0x9BF801/0x9BF804` read the 4-byte float and reject ordered nonnegative values. Preserve the existing source policy requiring an ordered negative value, deliberately also suppressing NaN. The exact-build live captures observed a finite negative value. The predicate is intentionally conservative rather than equivalent on NaN; see the final 23 October handoff. | Verify thread/lifetime and visible delivery of the actual candidate archive; the producer's semantic name and broader numeric range are not established. |

#### Quick Action Menu and resource data

| Stable source role | 7.05 source dependency | 7.06 state and evidence anchor | Remaining gate |
| --- | ---: | --- | --- |
| QAM depth | `menu+0xA050` | MAPPED: setter and trigger callers use it as the depth field. | Confirm live menu lifecycle. |
| QAM vector headers | `menu+0xA058` | MAPPED: builder/append path uses the vector-header base. | Confirm live menu lifecycle and all depths. |
| QAM vector depth stride | `0x10` bytes | MAPPED: exact builder access uses this per-depth spacing. | Confirm every source access against the live object. |
| QAM selected-index array | `menu+0xA088` | MAPPED: setter writes the selected index used by trigger/update paths. | Confirm live menu lifecycle. |
| QAM selected-index stride | `4` bytes | MAPPED: candidate indexes a 32-bit value per depth. | Confirm every source access against the live object. |
| QAM icon/resource handle | `menu+0xA104` | MAPPED statically: resource initializer stores the returned handle and builder transfers it to the item. | Live resource readiness, ownership and rendering semantics. |
| QAM pending-state byte | `menu+0xA16C` | MAPPED statically: TriggerAction receiver `RCX` is retained in `R15` and sets the byte to 1 after changing depth/selection; builder receiver `RCX` is recovered from its saved entry slot and reads then clears the byte. See the dated owner/lifecycle evidence below. | Verify live transition timing; retain the source fail-closed check. |
| QAM item size/stride | `0xE0` / 224 bytes | MAPPED: constructor and append contract use 224-byte records. | Verify all source item consumers. |
| QAM item icon dword | `item+0x0` | MAPPED statically: the selected QAM depth vector is copied into the incoming frontend record at `+0x610` with `0xE0` stride; the generic consumer reads the copied first dword as `R8D` at `0x1542038`, calls resource lookup `0x2E16E20` at `0x1542040`, and applies its output through `0x6DE4F0`. See the dated copy/consumer handoff below. | Verify update/draw index ordering, active depth and custom-row retention, resource lifetime/thread and visible rendering. This is a field/consumer contract, not runtime custom-row proof. |
| QAM item action | `item+0x4` | MAPPED: trigger/update paths read this action identifier. | Confirm live menu behavior. |
| QAM item role/slot | `item+0x84` | MAPPED statically: constructor initializes the 4-byte field to `-1`; QAM trigger reads it as a companion slot and passes it to eligibility/queue helpers. | Verify parent sentinel and child-slot behavior in the live menu. |
| QAM custom marker bytes | `item+0x88`, 16 bytes | MAPPED for constructed/checked metadata: constructor clears these 16 bytes, the mod writes its exact sentinel, and the full-row native copy retains the bytes. Copied-row comparisons and descriptor keys have distinct proven bases. Two stock snapshots agree; owned tests refuse changed child markers and a lost parent with native pet rows. | Actual custom-row retention, all rebuild paths and key equality/collisions are live acceptance gates; this is not a universal invariant or writer-absence claim. |
| QAM row-state byte 1 | `item+0x4C` | MAPPED statically: constructor stores `R9B`; the owner-proven copied-row renderer reads one byte at `0x15420C4` and `0x1542890` for scalar/tint and alternate-branch selection. The alleged original-row dword write at `0x152960B` instead targets a context descriptor field at base `+0x50`; see the 23 October affine-base correction. | Verify live visual meaning, retention and source guard behavior; constructor state is not a lifetime guarantee. |
| QAM row-state byte 2 | `item+0x4D` | MAPPED statically: constructor stores the fifth argument as one byte. `0x1541FAE` reads the copied row byte and `0x1541FDA-0x1541FEC` writes its Boolean inverse to a selected UI component byte `+0x61`. Current source value 1 produces UI flag 0. | Identify the exact UI child if a semantic name is needed; verify live visual effect and lifecycle. Do not label it background without further evidence. |
| QAM custom payload span | `item+0x98..0xD7` | MAPPED statically as a 64-byte auxiliary inline-text capacity: constructor `0x143D5D0` copies one NUL from fixed empty-string source `0x4A41320` into `+0x98` and terminates `+0xD7`. Renderer `0x15422EA-0x1542356` uses the copied span as auxiliary text; an empty first byte skips its text update and sets its UI-node flag. The main label uses the separate proven label output. | Verify custom-row retention and live UI behavior; do not describe this constructor path as copying 64 bytes or equate auxiliary text with the main label. |
| QAM item `+0xD8` | `item+0xD8`, 4 bytes | MAPPED as a guarded accepted-state contract: constructor sets original `-1`; native binding loops write indices to copied frontend rows and the renderer treats `-1` as no binding UI. The source continues requiring original `-1`; an owned test refuses a changed original value without overwriting it. | Actual original-row retention and exact-archive behavior remain live gates. No absence of other native writers is claimed. |
| Resource-manager global | `0x6E1BC10` | MAPPED: `0x6E1FC90`; QAM resource initializer reads it, startup stores the constructor-returned manager pointer, and teardown clears it. | Verify live manager stability and UI/resource lifecycle. |
| Resource-retain manager global | `0x5910190` | MAPPED: `0x59141E0`; the same constructor stores `this`, and the manager destructor clears it. Startup also stores the same returned pointer at `0x6E1FC90`. | Verify live refcount lifecycle and preserve the exact identity guard. |
| Resource-manager minimum extent | `0x68` bytes | MAPPED statically: manager allocation is `0x210` bytes; constructor initializes through `+0x1C8`, while source's `0x68` check covers the `+0x5C/+0x60` count/table fields it reads. | Verify live manager and pointed table stability. |
| Resource-manager count | `manager+0x5C` | MAPPED statically in the native manager helper. | Verify live manager stability during use. |
| Resource-manager table pointer | `manager+0x60` | MAPPED statically in the native manager helper. | Verify live table stability during use. |
| Resource-handle table stride | `8` bytes | MAPPED statically by handle lookup. | Verify live table and handle lifetime. |
| Resource type field | `resource+0x8` | MAPPED statically by loader path. | Confirm type values for the exact source resource. |
| Resource name blocks | `resource+0x0C..0x108`, 16-byte chunks | MAPPED statically by the name comparison loop. | Confirm live string representation and object extent. |
| Resource error flag | `resource+0x13A` | MAPPED statically: constructor `0x2D62D34` zeroes it in a dword at `+0x139`; the observed type-7 vptr's slot 13 (`0x1895AE0`) passes the same resource to `0x18DD960`, whose missing/empty-data failure writes word `+0x139=0x0101` at `0x18DD9C3`, setting byte `+0x13A=1`. Manager helper `0x1838784` independently consumes that byte as an insertion veto. Copier `0x2D652F0/0x2D652F7` preserves it. | Verify actual candidate icon readiness/fallback and lifetime in game; no destructive or forced-failure trial was performed. |
| Resource substitute flag | `resource+0x13B` | MAPPED statically: native resource loader `0x2D63EA0` branches on nonzero and resolves a fallback through `0x2D68490` using fields `+0x110` and `+0x8`. | Confirm whether suppressing substituted assets is the intended live icon policy. |
| Resource image value | `resource+0x1E0` | MAPPED statically as a checked resource member. | Confirm exact source rendering consumer. |
| Resource texture pointer | `resource+0x260` | MAPPED statically as the texture member. | Confirm pointer lifetime and renderer use. |
| Resource minimum extent | `0x268` bytes | MAPPED statically for the registered type-7 texture factory: registration `0x183CC71` stores callback `0x1834A80`; the loader calls that registered field. The callback allocates `0x400` bytes and invokes `0x1894A20`, which constructs payload `resource+0x1F8`; the payload initializer writes the qword at `resource+0x260`, ending at `+0x268`. See the 23 October factory handoff. | Verify actual cached-object class, replacement and lifetime in the live path; a readable memory region alone does not establish object lifetime. |
| TextureRecord path | `record+0x0` | MAPPED: loader candidate reads the path from the source-compatible record. | Confirm live load/reload lifecycle. |
| TextureRecord handle | `record+0x10` | MAPPED: loader candidate writes the returned handle at this offset. | Confirm release/retain and destruction behavior. |

#### Internal callbacks (not game RVAs)

These are source-to-source contracts rather than executable mappings; keep
them in the port review so a game-function ABI change does not silently
truncate or reinterpret their arguments.

| Callback | Source contract | 7.06 state |
| --- | --- | --- |
| Caption | `(context, role, output)` | SOURCE-ONLY; output capacity and native label adapter remain open. |
| Capture | `(context, role, revision)` | SOURCE-ONLY; exact QAM snapshot fields remain partly NOT CHECKED. |
| Change | `(context, role, revision)` | SOURCE-ONLY; exact QAM mutation and live confirmation remain open. |
| Log | `(context, message)` | SOURCE-ONLY; developer-only callback, not a game RVA. |

The ledger makes the current blocker order explicit: (1) do not change the
source/profile while required rows are `PARTIAL` or `NOT CHECKED`; (2) close
the QAM slot-9 caller/output contract and resource lifecycle before porting
the custom row; (3) map the remaining summon-state, planet, save and notice
data against exact 7.06 owners; (4) resolve local/network load semantics;
(5) perform the separately required source, offline, live and release gates.
The fastest completed work so far is static mapping of the queue-to-summon
path and much of the menu/resource structure; the ledger is not evidence that
the native 7.06 port has been implemented or verified. No source or profile
was changed; keep 7.06 fail-closed.

Next bounded action: continue the source port inventory from the newly
mapped 7.06 application pointer, resolving the remaining app-relative runtime
fields in their exact owner functions. Do not repeat the QAM slot-9
same-function field filter; use a new receiver-dataflow method or leave that
caller gate open while advancing independent dependencies.


### QAM vtable constructor anchor and application-global relocation, 22 October 2026

The exact Cosmos 7.06 executable remains Steam build `25732212`, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
CPython is 3.11.9, pefile is 2024.8.26 and Capstone is 5.0.7. The new bounded
pass used `native_rtti_vtable_probe.py`, `native_pdata_function_group.py`,
`native_function_disasm.py`, `native_call_xrefs.py` and
`native_vcall_xrefs.py`. Their SHA-256 values are:

| Script | SHA-256 |
| --- | --- |
| `native_rtti_vtable_probe.py` | `4e60908321b4f2aef2d314dff8f7cc6c00e62252683434ff6482758beee50028` |
| `native_pdata_function_group.py` | `fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26` |
| `native_function_disasm.py` | `26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0` |
| `native_call_xrefs.py` | `7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf` |
| `native_vcall_xrefs.py` | `24a792fce464fd6639a3de92923fcd31bc1bbbb6427acb0b866fc97308174621` |

The RTTI probe again identifies `0x153C0C0` as slot 9 of
`cGcQuickActionMenu`, with vtable RVA `0x4A504E0`. The exact child constructor
at `0x2CA6D0–0x2CAA96` stores a RIP-relative pointer resolving to that same
vtable at `[this]`. Its parent constructor at `0x2CA290` calls it at
`0x2CA3FE` with `RCX=parent+0xDC0`; the caller at `0x2C8F28` passes
`RCX=outer+0x115D50`. This statically confirms the child identity and owner
arithmetic `outer+0x116B10`. It does not identify a caller of slot 9 or prove
the label output's `R8` meaning.

A new vcall shortlist required slot byte offset `0x48` and both QAM field
displacements `0xA050` and `0xA088`. It decoded all `52,110,272` `.pdata`
bytes, skipped zero ranges, and returned zero matching ranges/calls. The
helper filters only by same-function displacement presence; this is a
bounded negative for that combination, not evidence that slot 9 has no
caller. Do not repeat this exact filter. The next label search needs a
receiver-dataflow anchor or a different evidence source.

The exact `CanSummon` candidate at `0x1474F10` loads a pointer through the
RIP-relative reference at `0x1474F14`; resolving the instruction gives
global RVA `0x6E8D708` (`0x1474F1B + 0x5A187ED`). It then uses
`R11+0xE10D0` as the companion table for
calls to `0x508290` and `0x50A520`. The same global RVA is independently
referenced at `0x4955AD` in the session path documented earlier. This
corroborates `0x6E8D708` as the exact-build application-pointer global used
by these paths and supersedes the source's 7.05 global `0x6E89688`. The
source/profile was not changed; no other app-relative field is validated by
this relocation alone.

Reproduction against the exact executable:

```text
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153C0C0 --max-slots 30
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2CA6D0 --size 0x3C6
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2CA290 --size 0x440
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2CA290 --context 12 --limit-per-target 100
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xA050 --require-field 0xA088 --context 12 --limit-per-range 30
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1474F10
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1474F10 --size 0x4B
```

The first short-wait invocation of `native_pdata_function_group.py` did not
return before its 10-second shell limit and its session identifier was not
retained; the corrected 30-second invocation completed and produced the
recorded boundary. No conclusion was drawn from the incomplete call. No
native source/profile change, build, package or live game operation occurred.

`NOT CHECKED`: the actual slot-9 callsite and `R8` contract; the exact live
application-relative roster and planet fields outside the static paths above;
load local/network semantics; and all runtime, offline and release gates.
Next bounded action: reconcile the 16-byte 7.06 read at `entry+0x2330` with
the source's 8-byte identity component using the exact consumer/producer path;
then map the still-unchecked planet-array fields. Do not repeat the capped
global offset scan or promote any other matches from it without owner
dataflow. Keep 7.06 fail-closed.


### Roster identity and habitat fields from exact 7.06 consumers, 22 October 2026

The focused scan was seeded only with source-used companion-record offsets
`0x2330`, `0x23C0`, `0x2480`, `0x2370` and nearby `0x2488`. The exact-build
fast-candidate pass decoded `52,110,272` `.pdata` bytes with zero skipped
ranges. It reported 100 matches for `0x2330`, 72 for `0x2370`, 81 for
`0x23C0`, 163 for `0x2480`, and 86 for `0x2488`; only 20 examples per
offset were printed. `READ_HINT`/`WRITE_HINT` are heuristic. The high counts,
truncated examples and stack/unrelated-object matches make this a shortlist
only, not field evidence.

Caller tracing established a roster owner for two candidates. Direct callers
of chained root `0x50D4B0` include `0x747977`, which passes `RCX=RDI+0xE10D0`
and `R8D=slot`, and `0x12BBF4A`, which first loads the application pointer
from global `0x6E8D708` and adds `0xE10D0`. The bounded body sets the record
base to `table+slot*0x24A0`, reads eight bytes at `entry+0x23C0`, and reads a
32-bit value at `entry+0x2480`. The same exact row arithmetic as the source
therefore corroborates the source's second identity-component address/width
and habitat-value address/width. Those internal semantic names are still
source interpretations, not names proven by this helper. The nearby `+0x2488`
check remains a distinct field and must not be substituted for the habitat
value.

Superseded on 23 October: the following resolver-result interpretation missed the later roster-row definition of `RDI`; use the current identity ledger and dated correction.

The exact slot-indexed path to root `0x50E1A0` is also established: caller
`0xF41680` passes the application-owned base and a slot in `EDX`; the target
computes `slot*0x24A0`, then derives a 16-byte lookup key from
`base+slot*0x24A0+0x46DD0`. Resolver `0x213290` compares both qwords of that
key against its manager entries and returns a matching entry pointer. Only
after that call does `0x50E1A0` read 16 bytes at `[resolver_result+0x2330]`.
This is not a read from the directly indexed roster entry. The source helper
instead copies eight bytes from `entry+0x2330` and eight from
`entry+0x23C0`; neither address nor the source names `seed`/`birth` can be
equated to the resolver key/result from the shared offsets alone. Keep the
identity gate `PARTIAL` until the source-side key, manager entry and returned
object are tied together by owner/dataflow evidence.

The exact helper `0x50A520` additionally reads `app+0x57A584` and
`app+0x72AFB0` through the same `0x6E8D708` global. This corroborates the
source location offset and a solar-system pointer access. Its downstream
native helper, runtime identity and planet field ownership are not established
by those reads alone.

Tool provenance: CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7;
`native_data_offset_xrefs.py` SHA-256
`5d3f80c87679dcf6dd41bde71f027628eb6af24fc6ee06ecf32924e63fac34b8`,
`native_call_xrefs.py` SHA-256
`7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf`,
`native_pdata_function_group.py` SHA-256
`fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26`, and
`native_function_disasm.py` SHA-256
`26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`.

Reproduction against the exact executable:

```text
python -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x2330 --offset 0x23C0 --offset 0x2480 --offset 0x2370 --offset 0x2488 --fast-candidates --limit-per-offset 20
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x50D522
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x50D4B0 --size 0x7EE
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x50D4B0 --context 12 --limit-per-target 30
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x50E9D5
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x50E1A0 --context 12 --limit-per-target 30
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xF41680 --size 0x142
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x50E1A0 --size 0xAFD
```

No native source/profile change, build, package or live game operation was
performed. The unresolved width at `+0x2330`, planet-array fields, slot-9
caller/`R8`, load local/network semantics and all runtime/release gates remain
open. Keep 7.06 fail-closed.
No source or profile change was made. No tests or game operations were run.

Next: include this wrapper/callee mismatch in the per-dependency ledger, then
resolve the receiver and output-buffer lifetime from a new data-flow anchor.
Do not repeat the prior same-function offset filters.


### Active package source, identity dataflow correction and planet fields, 22 October 2026

Version identities were rechecked against the current public repository,
installed executable and public release pages. The local worktree is
`compat/cosmos-706-25732212` at `f7d97b61fcf152677d0d30de34f6c1b48675c436`,
which is also the GitHub `main` tip; that source commit records the Nexus
0.10.2 release. The active player implementation is native C++ under
`native/src/`, built and packaged against `native_compatibility.json`.
`src/runtime.py` is retained Python/pyMHF code with a Cosmos 7.04 profile; it
is not an input to the current native player package and must not enter its
dependency denominator. Nexus currently lists `0.10.2-native-test`, file
49469, for Windows/Steam 25624745 / Cosmos 7.05. The official Hello Games
release log still lists Cosmos 7.06 as the newest patch on this date. The
exact local 7.06 executable remains build `25732212`, size `88,560,712`,
SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
No package or source identity changed.

#### Corrected 16-byte identity observation

Superseded on 23 October: the resolver-result interpretation below missed a later `RDI` redefinition. See the roster identity producer/consumer correction in the latest handoff.

The earlier description of `0x50E1A0` as reading `entry+0x2330` was too
strong. Its only direct callsite is `0xF4173C` in root `0xF41680`. That caller
passes `RCX=app+0xE10D0` and passes a value derived as `([RDX])-1` in `EDX`;
the surrounding slot/eligibility checks are part of this caller, but the
semantic link from this index to the source identity contract remains open.
In `0x50E1A0`, the index is multiplied by `0x24A0`; the function derives a
16-byte lookup-key pointer at `base+index*0x24A0+0x46DD0` and passes it to
resolver `0x213290`. The resolver compares both qwords against manager entries
and returns the matching manager-entry pointer. Only then does `0x50E1A0`
read 16 bytes from `[resolver_result+0x2330]` and copy them to
`[resolver_result+0x2390]`. This is not a direct 16-byte read from the
indexed roster entry. The active 7.05 C++ source reads eight bytes at
`entry+0x2330` and eight at `entry+0x23C0`; neither source component is
validated by the similar displacement in the resolver result. Keep the
identity dependency `PARTIAL`. Do not port it until the producer/owner of the
`+0x46DD0` key and its relation to the source roster identity are established.

#### Exact 7.06 planet-field mapping

The independent fast-candidate scan covered all `52,110,272` `.pdata` bytes
with zero skipped ranges for displacements `0x2544`, `0x5196D0`, `0x6148` and
`0x614C`. It reported respectively 887, 606, 93 and 35 operand matches; only
12 examples per displacement were printed, so the output was a candidate
shortlist, not a negative or a mapping by itself.

Function `0x2B3A10` supplies the owner chain. At `0x2B3DC2`, its RIP-relative
load resolves as `0x2B3DC9 + 0x6BD993F = 0x6E8D708`. It loads the solar-system
pointer from `[app+0x72AFB0]` into `R9`, then reads 32-bit fields
`[solar+0x5196D0]` and `[solar+0x2544]`. It clamps the index to the range
`0..count-1`, multiplies it by `0xD9170`, then reads 32-bit values at
`solar+index*0xD9170+0x614C` and `solar+index*0xD9170+0x6148`. The subtype
values `0x19` and `0x1A` are translated to result values `0xC` and `0xD`;
the complete enum mapping and live values remain open. This directly maps the
source's solar pointer, count, selected index, stride, biome and subtype
addresses and widths for the exact 7.06 image.

An independent path through `0x50A520` passes the same solar pointer to
`0x2C4710`, which reads the count and also uses stride `0xD9170`. That helper
returns a pointer based at `solar+0x2E30+index*0xD9170`; this is a distinct
result-object base and must not replace the direct `solar+index*stride`
base established by `0x2B3A10` for the biome fields.

Reproduction against the exact executable:

```text
python -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x2544 --offset 0x5196D0 --offset 0x6148 --offset 0x614C --fast-candidates --limit-per-offset 12
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2B3A10
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2B3A10 --size 0xA1F
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2B3A10 --context 12 --limit-per-target 20
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x50A520 --size 0x70
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2C4710 --size 0x211
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x50E1A0 --size 0xAFD
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x213290 --size 0xBF
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x50E1A0 --context 12 --limit-per-target 20
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xF41680 --size 0x142
```

Tool hashes remain recorded above for `native_data_offset_xrefs.py`,
`native_call_xrefs.py`, `native_pdata_function_group.py` and
`native_function_disasm.py`. No source/profile change, build, package, tests
or live game operation occurred.

Next bounded action: identify the exact producer and owner of the 16-byte
`base+index*0x24A0+0x46DD0` key and determine whether its resolver result is
the companion identity consumed by the native source. If that chain does not
close in one bounded pass, record the gap and advance to an independent open
gate such as the QAM output contract. Keep 7.06 fail-closed.


### Active companion slot transition and bounded identity-key result, 22 October 2026

The preceding next action was attempted. The fast-candidate scan found five
`0x46DD0` operand candidates and four `0x46DD8` candidates. Candidate function
`0x50DFB0` compares the two key qwords with two qwords in a roster row at
`+0x2310/+0x2318`, but its object owner remains unknown. A full direct-E8 scan
found no direct caller of `0x50DFB0`, and the RTTI probe found no RTTI-backed
vtable slot for it. These are bounded negatives for direct calls and recovered
vtable membership only; indirect/dynamic invocation remains possible. Keep
the key owner and source identity relationship `NOT CHECKED` and do not repeat
the same displacement, direct-E8 or RTTI queries without a new invocation
anchor. The earlier identity mapping remains `PARTIAL`.

The source dependency row for `active_pet` is now corrected to the exact 7.06
application object: `app+0x29A1C0`, four bytes. A detailed operand-access scan
of all 52,110,272 `.pdata` bytes skipped zero ranges and reported 53 read
operands and three write operands for displacement `0x29A1C0`. Exact dataflow
ties two state transitions to application global `0x6E8D708`: function
`0x1475335` compares the current dword with a candidate slot, bounds that slot
to 0–29, uses the same `0x24A0` roster stride, then writes the selected slot at
`0x14753AA`; function `0x14756B0` checks the dword against `-1` and writes
`0xFFFFFFFF` at `0x147576D` when clearing it. The third displacement write at
`0x1475CAF` uses an `RCX` base whose object identity has not been established;
do not count it as a confirmed application write.

An exact consumer is in chained range `0x5120C2-0x512558`, whose unwind root is
`0x510EF0`. At `0x5124A3` the code loads a 32-bit value from
`[app+0x29A1C0]`, passes it as the index to `0x540D00`, and passes the roster
base `app+0xE10D0` in `RCX`. The helper rejects indices above 29 and indexes
records with stride `0x24A0`. The root's one direct caller is `0x1191FE9`; an
initial direct-call query against chained range `0x5120C2` returned zero,
which did not mean that the owning function lacked callers. Query chained
roots for callers. The exact source uses the same field as an active slot and
gates its behavior on `-1`; static ownership, width, slot range and clear
sentinel are now mapped. Transition timing and live local-player behavior
remain unverified.

For future full access scans, run both access filters in one decode. This
investigation initially launched separate read and write scans; the scanner
accepts repeated `--access` arguments, so one
`--access read --access write` command avoids the duplicated full `.pdata`
work.

Reproduction against the exact executable:

```text
python -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x29A1C0 --access read --access write --limit-per-offset 100
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x5124A3
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x5120C2 --size 0x496
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x540D00
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x540D00 --size 0x180
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x510EF0
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x510EF0 --context 8 --limit-per-target 20
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1475335 --size 0x1F2
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x14756B0 --size 0xDC
```

Tool hashes for `native_data_offset_xrefs.py`, `native_function_disasm.py`,
`native_pdata_function_group.py`, `native_call_xrefs.py` and
`native_rtti_vtable_probe.py` are recorded in this report. No native source or
compatibility profile was changed; no tests, build, package or live game
operation was run. Keep 7.06 fail-closed.

Next bounded action: resume the independent QAM label-output gate. Search from
the confirmed QAM vtable/constructor chain for a real slot-9 invocation and
recover its `RCX`, `RDX`, `R8`, destination ownership and caller. Do not repeat
the prior same-function `0xA050/0xA088` vcall conjunction; switch to an
independent receiver/callsite anchor and record a bounded negative if that
path does not close.


### QAM slot-9 receiver-filter false leads, 22 October 2026

The first new receiver anchor was exact QAM child offset `0x116B10`, composed
by the verified constructor chain. A full `.pdata` scan for slot offset `0x48`
plus same-range displacement `0x116B10` decoded 52,110,272 bytes with zero
skipped ranges and returned one function range, `0x924C90-0x924DFF`, containing
two indirect slot-9 calls. Disassembly shows those calls use receivers loaded
from `[rdi+0x110998]` and `[rdi+0x1109A0]`; the QAM child offset appears later
in the same routine at a separate direct cleanup call `0x1527BD0` with
`RCX=rdi+0x116B10`. The function has one direct caller at `0x32FD1B`, among a
sequence of cleanup-like calls. The displacement filter did not identify the
receiver and this range is a false lead for the QAM label invocation.

A second full scan for slot offset `0x48` plus same-range displacement `0xDC0`
decoded the same complete `.pdata` range set and returned seven function
ranges with eight candidate calls. None of the printed callsite contexts ties
`RCX` to the QAM subobject at `parent+0xDC0`; the filter therefore supplies no
QAM invocation evidence. Do not repeat either same-range filter unchanged.
`native_vcall_xrefs.py` reports slot-offset calls and optional same-range
displacements only; receiver identity must be followed independently.

Reproduction against the exact executable:

```text
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0x116B10 --context 8 --limit-per-range 10
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x924C90 --size 0x16F
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x924C90 --context 10 --limit-per-target 20
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xDC0 --context 8 --limit-per-range 10
```

`native_vcall_xrefs.py` SHA-256 is
`24a792fce464fd6639a3de92923fcd31bc1bbbb6427acb0b866fc97308174621`.

Next bounded action: start from the mapped 7.06 quick-menu builder at
`0x152A1C0`, resolve its exact unwind range and call/dataflow path, and test
whether its concrete QAM receiver reaches slot 9 with the required output
argument. If it does not, preserve the caller/receiver gap and change anchor;
do not treat either offset-filter shortlist as a vtable-type match. Keep 7.06
fail-closed.


### Quick-menu builder and slot-9 output contract, 22 October 2026

The builder anchor was resolved. `0x152A1C0` is a root with one chained range,
`0x152B394-0x152E6D1`, and has six direct callers. A bounded decode of both
ranges found no indirect call through slot offset `0x48`, so the builder itself
does not call QAM slot 9. Keep the rendering/caller path open; the six direct
builder callers do not establish a slot-9 caller.

The exact RTTI-confirmed QAM slot-9 body `0x153C0C0` is a three-argument
method: `RCX` is its QAM receiver, `RDX` is the string output, and `R8` points
to a byte that the method clears to zero at entry. The body uses QAM members
`+0xA050`, `+0xA058`, `+0xA05C`, `+0xA060` and `+0xA088`; its bounded
string-copy paths stop at 256 bytes and place a terminator at output offset
`0xFF`. The source wrapper still assumes two pointer arguments and a
128-byte post-write. This is an ABI/capacity mismatch, not a safe replacement
mapping. The caller, `R8` meaning/lifetime and destination ownership remain
`NOT CHECKED`.

To test the QAM-member anchor, the full `.pdata` virtual-call scanner used
slot offset `0x48` with each candidate displacement separately. It reported
zero ranges/calls for `+0xA060`, `+0xA088` and `+0xA050`. The prior
`+0xA050` plus `+0xA088` conjunction was also zero. These results are bounded
to decoded direct virtual-call operands in `.pdata`; they do not exclude calls
through a copied function pointer, dynamic dispatch shape or another event
mechanism. Do not repeat these exact same-range filters without a fresh
receiver anchor.

Reproduction against the exact executable:

```text
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152A1C0
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x152A1C0 --context 12 --limit-per-target 20
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152A1C0 --size 0x11D4 | Select-String -Pattern 'call qword ptr \[.*\+ 0x48\]' -Context 10,8
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152B394 --size 0x315D | Select-String -Pattern 'call qword ptr \[.*\+ 0x48\]' -Context 10,8
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0C0
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0C0 --size 0x3D
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0FD --size 0x14F
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C24C --size 0x398
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xA060 --context 10 --limit-per-range 10
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xA088 --context 10 --limit-per-range 10
python -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xA050 --context 10 --limit-per-range 10
```

Tool hashes remain recorded above, including
`native_vcall_xrefs.py`. No native source/profile change, tests, build,
package or live game operation occurred. Keep 7.06 fail-closed.

Next bounded action: map an independent unresolved runtime dependency from the
source ledger, beginning with the owner emote byte at source offset
`owner+0x1B937D`. Establish its owner, access width, read/write paths and
consumer; leave QAM slot-9 call ownership explicitly open rather than
repeating offset-only searches.


### Owner emote/busy guard, exact 7.06 read and owner-base chain, 22 October 2026

The exact-access scan for displacement `0x1B937D` decoded 52,110,272 `.pdata`
bytes with zero skipped ranges and found one operand: a one-byte read at
`0x5090D9` in chained range `0x508DE0-0x50923E`. It found zero writes at that
displacement in decoded `.pdata`. This is a bounded negative for exact
displacement stores in those ranges; it does not exclude writes expressed
through another layout, callback or non-`.pdata` code.

The unwind chain resolves this read to owner-update root `0x508DC0`, whose
entry copies incoming `RCX` to `RSI`. The same root group reads the source's
companion slot at `+0x1B90F0`, iterates records with `0x24A0` stride, reads
the preview slot at `+0x1B9300`, and uses the placement subobject at
`+0x1B9140`; this independently corroborates the `owner` base used by the
source hook. At `0x5090D9`, the byte is compared with zero and controls a
branch to a different owner-update path. The source variable calls it `emote`,
but static evidence currently establishes only a one-byte nonzero gate, not
the producer or exact game meaning. Keep the dependency `PARTIAL` and do not
rename or port it as a confirmed emote flag.

The exact hook root has one previously recorded direct caller at `0x489661`,
which supplies the owner subobject in `RCX` and the update delta in `XMM1`.
The earlier source-hook mapping remains static only; live local/network
identity and invocation timing are still open.

Reproduction against the exact executable:

```text
python -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x1B937D --access read --access write --limit-per-offset 100
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x5090D9
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x508DC0 --size 0x20
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x508DE0 --size 0x45E
```

The scanner hash is recorded above. No source/profile change, tests, build,
package or live game operation occurred. Keep 7.06 fail-closed.

Next bounded action: map the source's local-player physics pointer at
`player+0x2A8` using the app-global/local-player chain and its exact consumer
at the owner placement probe. Keep `owner+0x1B937D` `PARTIAL` until a producer
or stronger semantic anchor is found.


### Local-player physics pointer, exact app-chain mapping, 22 October 2026

The detailed `.pdata` scan for displacement `0x2A8` decoded 52,110,272 bytes
with zero skipped ranges and reported 947 operands, of which the command
printed only its first 120. Many examples were stack locals or unrelated
objects, so the global offset list alone was not usable for assigning the
source role.

The already mapped placement candidate `0x14426A0` supplies the independent
base chain. At `0x14426B6` it loads the application pointer from the global
that resolves to `0x6E8D708`, then adds `0x72C6F0` to form the local-player
base in `R13`. In the same chained function group, it reads a 64-bit value
from `[R13+0x2A8]` at `0x1442ADF`, `0x1442B04` and `0x1442B46`, passing the
value in `RDX` to helper `0x142CE6FD0`. This maps the source's exact 8-byte
pointer field and one static consumer path. Live identity, lifetime and
transition behavior remain unverified; keep those as runtime gates.

Reproduction against the exact executable:

```text
python -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x2A8 --access read --access write --limit-per-offset 120
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x14426A0
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x14426A0 --size 0x34
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x14426A0 --size 0x4E6 | Select-String -Pattern '\+ 0x2a8' -Context 8,8
```

The offset scanner hash is recorded above. No source/profile change, tests,
build, package or live game operation occurred. Keep 7.06 fail-closed.

Next bounded action: trace the source's interaction-range address
`image_base+0x527AB34` through its exact 7.06 placement consumer. Treat the
RVA as a candidate until an exact data reference and value width are found.


### Interaction-range RVA mismatch and scalar candidate, 22 October 2026

The source reads a `float` from `image_base+0x527AB34`, validates it as finite
and positive, and passes the same value twice to the placement service. Two
exact-hash checks did not find that old address in Cosmos 7.06: a full
`.pdata` RIP-relative scan decoded 52,110,272 bytes with zero skipped ranges
and found zero direct references; the non-executable data scan checked
31,431,680 bytes across four sections and found zero exact 32-bit RVA
constants. Keep the 7.05 RVA rejected for direct reuse.

A consumer anchor exists at owner-update instruction `0x509190`:
`movss xmm1, dword ptr [rip+0x4D759DC]` resolves to data RVA `0x527EB74`.
The value is passed in both `XMM1` and `XMM2` to placement candidate
`0x14426A0` at callsite `0x5091A5`, with `RCX=owner+0x1B9140` and the hand in
`R9D`. The exact RIP scan found one reference to `0x527EB74`, at `0x509190`.
The RVA lies in the `.data` virtual-only tail and has no raw file bytes. An
earlier scratch extraction applied the raw-section offset formula beyond
`SizeOfRawData` and returned unrelated bytes; discard that value. No raw bytes
does not mean that the runtime global is zero. The 7.05 report also places
source RVA `0x527AB34` in virtual data/BSS and records the matching placement
call path. The same owner-update consumer shape now maps `0x527EB74` statically
to the placement-distance scalar role. Its runtime value, units and in-game
placement behavior remain unverified.

Reproduction against the exact executable:

```text
python -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x527AB34 --limit-per-target 50
python -B tools/native_rva_data_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x527AB34 --limit-per-target 50
python -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x527EB74 --limit-per-target 50
```

`native_rip_xrefs.py` SHA-256 is
`dbff203dc5748821d69c66b1e4c8f75ba91044e36a45daa77c343be2207d08a3`;
`native_rva_data_xrefs.py` SHA-256 is
`c1b88b6910dad1ff0d2ef556a2c94c58b94f04e0b06b20253cdd561f94ce123d`.
No source/profile change, tests, build, package or live game operation
occurred. Keep 7.06 fail-closed.

The static role question is now closed by the exact consumer and old-build
call-path parity. Further raw-file inspection cannot provide the value for a
virtual-only global; keep its runtime value and units as separate live gates
and continue with independent compatibility blockers.


### Save-identity width and virtual-call ABI shortlist, 22 October 2026

The official [No Man's Sky release log](https://www.nomanssky.com/release-log/)
was checked again on 22 October 2026. Cosmos 7.06 remains the newest listed
patch; no 7.07 entry is present. The exact local executable remains Steam
build `25732212`, size `88,560,712` bytes, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
Analysis used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7.

The source `Runtime::afterLoad` reads a `std::uint64_t` at
`common+0x8980` only after a successful non-network load. The exact-build
load-role candidate `0x573500` saves incoming `RDX` at entry, copies it to
`R15` at `0x573537`, reads an 8-byte value from `[R15+0x8980]` at `0x5736D4`
and copies that value to another object. This confirms the displacement and
width for the candidate's second argument. It does not prove the second
argument is the same common-save object used by the source or establish the
field's identity semantics across the four callers. At this point the
dependency was upgraded from `NOT CHECKED` to `PARTIAL`; the later
two-way-def-use evidence below supersedes that interim state.

The new `native_vcall_abi_candidates.py` helper scanned the complete
`.pdata` inventory for virtual calls through byte offset `0x48`: 52,110,272
bytes, zero skipped ranges, 523 ranges and 789 calls. Requiring `RDX` and
`R8` pointer setup after the last intervening call produced 55 candidates.
This is a bounded ABI shortlist, not a class or caller mapping. RTTI reverse
mapping identified `0x2E51800` and `0x2E51880` as slot 11/10 methods on five
Havok serialization pointer-implementation vtables; these are false leads
for the QAM label hook. Their direct-call and RIP-relative caller scans each
returned zero.

The more promising-shaped slot call at `0x347F58` has receiver
`RCX=[R15+8]`, a stack output in `RDX`, and a separate pointer in `R8`. Its
`.pdata` entry is chained to root `0x346B30`. The full root is RTTI-confirmed
as `cGcAtlasBrokerAzure` vtable slot 10; it has no direct-call references,
and its literal pointer appears in one `.rdata` entry. The nested object's
type is unresolved, so this is not accepted as a QAM label caller. Do not
repeat the broad slot scan or map the nested pointer from its argument shape.

The candidate interaction-range data at RVA `0x527EB74` was also checked
for literal preferred-base pointer references: zero matches in 88,155,208
non-relocation-section bytes across seven sections. This closes that one
pointer-scan avenue only; it does not rule out relative, dynamic or code-based
initialization. Leave the source field `PARTIAL` and stop repeating this
unchanged absolute-pointer query.

Reproduction commands against the exact executable:

```text
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x573500 --size 0xA8
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x5736B0 --size 0x80
python -B tools/native_vcall_abi_candidates.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --limit 100
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2E51800 --max-slots 64
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2E51880 --max-slots 64
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2E51800 --target-rva 0x2E51880 --context 12 --limit-per-target 20
python -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2E51800 --target-rva 0x2E51880 --limit-per-target 20
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x346DCE
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x346B30 --max-slots 64
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x346B30 --context 12 --limit-per-target 20
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x347F0E --size 0x70
python -B tools/native_absolute_pointer_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2E51800 --target-rva 0x2E51880 --target-rva 0x346B30 --target-rva 0x527EB74 --limit-per-target 20
```

Tool SHA-256 values for this pass:

| Script | SHA-256 |
| --- | --- |
| `native_vcall_abi_candidates.py` | `7b5184fc14c2314ab8a561838519aa3eafa35df2ac68977527bb135efba92944` |
| `native_vcall_xrefs.py` | `24a792fce464fd6639a3de92923fcd31bc1bbbb6427acb0b866fc97308174621` |
| `native_rtti_vtable_probe.py` | `4e60908321b4f2aef2d314dff8f7cc6c00e62252683434ff6482758beee50028` |
| `native_pdata_function_group.py` | `fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26` |
| `native_function_disasm.py` | `26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0` |
| `native_call_xrefs.py` | `7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf` |
| `native_absolute_pointer_xrefs.py` | `5e6f37d2dedf74b5691c537b4e1f19908926dd76062686eecb5a14e516bc5f46` |
| `native_rip_xrefs.py` | `dbff203dc5748821d69c66b1e4c8f75ba91044e36a45daa77c343be2207d08a3` |

No source or compatibility profile was changed. No tests, build, package or
live game operation was run. Keep Cosmos 7.06 fail-closed.

Next bounded action: establish the exact type and producer of the second
argument passed to `0x573500` in its four callers, especially the stack object
at `0x2E088F`; this should decide whether `common+0x8980` is the same local
save identity used by `afterLoad`. In parallel, keep the QAM slot-9 caller
`NOT CHECKED`; only resume it from a proven UI/QAM receiver anchor, not another
slot-offset shortlist.


### Load-candidate argument first-use audit, 22 October 2026

The official [No Man's Sky release log](https://www.nomanssky.com/release-log/)
was rechecked on 22 October 2026; Cosmos 7.06 remains the newest listed patch,
with no 7.07 entry. The local executable still matches Steam build `25732212`,
size `88,560,712` bytes and SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.

A detailed read/write pass for displacement `0x4BE6A0` decoded all
`52,110,272` `.pdata` bytes and skipped no ranges. It confirmed the same seven
operands previously found by the heuristic scan: two writes and five reads.
This validates their access directions but does not merge the different
register bases or identify the field's meaning.

The unwind group for `0x573500` contains eight adjacent ranges spanning
`0x573500–0x579B50`. Its prologue stores incoming `R9B` at entry `[RSP+0x20]`,
then sets `RBP` so `[RBP+0xCC8]` aliases that fourth-register home slot,
`[RBP+0xCD0]` aliases the fifth argument, and `[RBP+0xCD8]` aliases the sixth.
The complete group scan shows:

| Physical slot | Exact 7.06 use | What is established |
| --- | --- | --- |
| Fourth argument, incoming `R9B` | Saved at `0x573500`; the home slot is overwritten by `BL` at `0x576407` before a direct input read or address escape. | This candidate does not consume the incoming value before reusing the slot. The session-derived caller byte is not proof of `network` semantics. |
| Fifth stack argument | `cmp byte ptr [RBP+0xCD0], 0` at `0x578B2F`; zero enters a helper path, nonzero skips it. | The candidate reads a one-byte Boolean here; its meaning is still unknown. |
| Sixth stack argument | First direct access is `mov byte ptr [RBP+0xCD8], AL` at `0x573653`, before any input read. Later byte/word/dword operations use the reused local slot. | Caller stores and later mixed-width accesses do not establish an `extra` parameter type or meaning. |

The zero-fifth-argument branch calls `0x6019F0` with the third-argument object
and a state-derived Boolean. A full direct-call scan decoded `52,110,272`
`.pdata` bytes, skipped no ranges and found exactly one direct call to this
helper, at `0x578B52` in the load candidate. This does not exclude indirect
calls. The helper clears several state fields before a flag-dependent
continuation. This maps the branch effect statically, but it does not
establish whether the fifth input means `resetting` or another mode.
The four callsites remain distinct: `0x2E088F` is in
`cGcApplicationDeathState`; `0x48EECC` and `0x48F983` share root `0x48E400`;
`0x4906BD` is in root `0x48FA60` and supplies the session-derived fourth byte.
The other roots still lack a validated RTTI class. The 7.05 typedef names
`network`, `resetting` and `extra` remain unverified against this 7.06 body.

Reproduction against the exact executable (CPython 3.11.9, pefile 2024.8.26,
Capstone 5.0.7):

```text
python -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x4BE6A0 --access read --access write --limit-per-offset 100
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x573500
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x573500 --size 0x6530 | Select-String -Pattern '0xcc8|0xcd0|0xcd8|0xd38'
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x490620 --size 0x150
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x48EE80 --size 0x90
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x48F940 --size 0x90
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x578AE0 --size 0xA0
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x6019F0
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x6019F0 --size 0x200
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x6019F0 --context 12 --limit-per-target 100
```

`native_data_offset_xrefs.py` SHA-256 is
`5d3f80c87679dcf6dd41bde71f027628eb6af24fc6ee06ecf32924e63fac34b8`;
`native_function_disasm.py` is
`26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`;
`native_pdata_function_group.py` is
`fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26`;
`native_call_xrefs.py` is
`7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf`.
No native source/profile change, tests, build, package or live game operation
occurred. Keep 7.06 fail-closed.

Next bounded action: trace the fifth-byte decision at `0x578B2F` through the
caller state and helper `0x6019F0` to establish its meaning before mapping it
to a source parameter. Do not spend another broad scan trying to name the
fourth or sixth input; this candidate overwrites those slots before reading
them. Keep the QAM slot-9 caller as a separate unresolved release gate.


### QAM builder callers are an update chain, 22 October 2026

A direct-call inventory of builder `0x152A1C0` on the exact executable found
six calls in three `.pdata` roots: `0x1528893` in `0x15286C0`, four calls
(`0x153B7AA`, `0x153BA88`, `0x153BBA8`, `0x153BCBE`) in `0x153B5B0`, and
`0x153BF4A` in `0x153BE80`. All call setups pass a QAM object in `RCX` and a
render-related pointer in `RDX`, consistent with builder/update work.

Root-aligned scans of all three complete groups found no virtual call through
slot offset `0x48`. This narrows the caller gap: the builder and its confirmed
QAM update callers do not invoke the RTTI-confirmed label method
`0x153C0C0`. It does not rule out a separate rendering path or calls through
copied function pointers. Do not repeat the builder-root slot scan.

Reproduction against the exact executable:

```text
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x152A1C0 --context 12 --limit-per-target 20
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15286C0
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15286C0 --size 0x181D | Select-String -Pattern 'call qword ptr \[.*\+ 0x48\]' -Context 6,6
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153B5B0 --size 0x8A2 | Select-String -Pattern 'call qword ptr \[.*\+ 0x48\]' -Context 6,6
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153BE80 --size 0x13B | Select-String -Pattern 'call qword ptr \[.*\+ 0x48\]' -Context 6,6
```

`native_call_xrefs.py` SHA-256 is
`7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf`;
`native_function_disasm.py` is
`26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`;
`native_pdata_function_group.py` is
`fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26`.
No source/profile change, tests, build, package or live game operation
occurred. Keep 7.06 fail-closed.

Next bounded action: follow the higher-level UI/render path that owns or
receives the confirmed QAM object, then test for a slot-9 dispatch with the
three-argument output contract already mapped. The QAM builder/update chain
is now a recorded false lead for the label call; do not return to offset-only
filters or scan these same roots again.

### Fifth-argument callers and stale 7.05 RVA, 22 October 2026

The active native source profile remains Cosmos 7.05 and installs its load
hook at old RVA `0x572C40` in `native/src/bootstrap.cpp`. On the exact
Cosmos 7.06 executable, `0x572C40` is contained in `.pdata` range
`0x572410-0x573137`, whose function root is `0x572410`; it is not a
separate function entry. Do not reuse this RVA as a 7.06 entry hook unless
a deliberate interior-hook site and instruction-safe patch are separately
proved. The load-role candidate `0x573500` remains a distinct `PARTIAL`
candidate, not a completed source mapping.

The full root-aligned caller trace narrows the candidate's fifth byte:

| Call site | Caller evidence | Fifth argument |
| --- | --- | --- |
| `0x2E088F` | RTTI-confirmed `cGcApplicationDeathState` path | `1` |
| `0x48EECC` | Root `0x48E400`; the path to this call retains `DIL=0` from `0x48E4B4` | `0` |
| `0x48F983` | Same root; `R13B` was zeroed at `0x48E42D` and is unchanged before this call | `0` |
| `0x4906BD` | Root `0x48FA60`; caller stages literal zero | `0` |

In root `0x48E400`, the write `movzx edi,r14b` at `0x48E58C` belongs to
a branch that bypasses `0x48EECC`; the call-reaching branch starts at
`0x48E5A1`. The later `DIL` write near `0x48F920` is also outside the
first call path. `R13D` is initialized to zero at `0x48E42D` and has no
intervening write before the second call. Thus all three non-death-state
callers pass zero, while the death-state caller passes one.

The callee reads the fifth input at `0x578B2F`: zero calls helper
`0x6019F0`, which clears state fields before a flag-dependent continuation;
nonzero skips that helper. The caller pattern may help distinguish load
modes, but it does not prove that the input is source parameter `resetting`.
Keep the parameter name unresolved. The 7.05 wrapper uses its fourth Boolean
as the `network` gate, but no 7.06 mapping for that slot is confirmed; the
candidate callee overwrites its fourth-argument home slot before reading it.
The session-derived byte at `+0x4BE6A0` still lacks a verified local/network
meaning.

The command `py -3.11 -B tools/native_function_disasm.py --exe
'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe'
--rva 0x48EE80 --size 0x90` failed before decoding with `No installed
Python found!`; this is a launcher `TOOL ERROR`, not a scan result. The
working interpreter is
`<verified-CPython-3.11.9-executable>`
(Python 3.11.9, SHA-256
`5F7B89A612C9B8AF1D6456CDFCD1DBE5CA630849E79AEBCED9BEE9A6694952EC`),
with pefile 2024.8.26 and Capstone 5.0.7.

Reproduction:

```powershell
& $python -B tools/native_pdata_function_group.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x572C40
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x48E400 --size 0x165C | Select-String -Pattern 'dil|r13|48eecc|48f983' -Context 3,3
```

`native_pdata_function_group.py` SHA-256:
`fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26`;
`native_function_disasm.py` SHA-256:
`26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`.
The exact executable remains Steam build `25732212`, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
No source/profile changes, build, tests, package or live-game operation
were made. Keep 7.06 fail-closed.

Next bounded actions: resolve the owner and local/network meaning of
`+0x4BE6A0`; independently find the QAM slot-9 rendering consumer and prove
its output contract. Do not promote `0x573500` or rename its fifth input
from caller correlation alone.

### QAM item-field ownership and corrected placement-range mapping, 22 October 2026

The exact executable remains Windows x64 Steam Cosmos 7.06, build `25732212`,
file version `180836`, size `88,560,712`, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. The
source baseline is `f7d97b61fcf152677d0d30de34f6c1b48675c436`; the 7.05 profile
in `native_compatibility.json` remains unchanged. The pinned NMS.py provider
remains commit `b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`, `tools/data.json`
SHA-256 `F311C9F54C0CCE199AB955A0E8DE2CFE2FCFB09274E557A2A27908C1B15BAF5F`,
MIT. Analysis used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7.

The exact item constructor `0x143D5D0–0x143D6F2` writes a 0xE0-byte record.
Its body initializes dword `item+0x84` to `-1`, zeros the 16 bytes
`item+0x88..0x97`, copies a bounded string into `item+0x98..0xD7`, and
initializes dword `item+0xD8` to `-1`. This disproves the assumption that the
source's 16-byte marker at `+0x88` and 64-byte cleared span at `+0x98..+0xD7`
are unowned storage.

The QAM update group rooted at `0x15286C0` contains a 0xE0-stride row
reconciliation pass. It compares row fields at `+0x88`, `+0x90`, `+0x84`,
`+0x50`, `+0x40`, `+4` and a string beginning at `+0x44`; after a match it
writes the match index to `+0xD8`. The source's required `binding==-1` is
therefore not established as a lasting invariant. Separately, the exact QAM
trigger group rooted at `0x1531E00` reads `item+0x84` in its summon branches,
compares it with the active companion slot, and passes it to eligibility
`0x1474F10` and queue `0x1475790`. This maps `+0x84` as a slot/action payload,
while leaving the `-1` parent-sentinel behavior to live verification.

The existing mod writes a custom marker into the native `+0x88/+0x90`
comparison key and clears the constructor's `+0x98..+0xD7` string area.
Those writes need a safe redesign or exact behavior proof before porting the
menu adapter. An out-of-band record-index tracker is a possible direction,
but its vector-rebuild and reallocation behavior is NOT CHECKED. Do not use
the source marker/payload checks as evidence that the corresponding native
fields are free.

A prior full `.pdata` displacement scan decoded 52,110,272 bytes with zero
skipped ranges and reported 3,261 operands for `+0x84` and 11,913 for `+0x88`,
printing at most the first 100 per offset. These whole-image counts and
truncated examples do not establish QAM ownership; the exact constructor,
update and trigger roots above provide the usable evidence. Do not repeat
that broad offset scan unchanged.

The virtual-call ABI shortlist was rerun with a different print cap (`--limit
100` on the first pass and `--limit 250` on the repeat), not the exact same
command. Both passes reported 789 calls in 523 ranges and 55 `RDX`/`R8`-setup
candidates; the larger cap added no receiver candidate or coverage. One listed method at
`0x33E6160` was checked with RTTI and belongs to Havok
`ChildArrayImpl` slot 10, not the QAM class. Treat it as a false lead for the
QAM label caller; the nested call's receiver is not independently mapped.
Search the documentation by helper name before running a discovery command,
not only by the target RVA.

The earlier BSS extraction and the earlier `+0x84/+0x88` broad scan were
corrected or bounded as described above. No native source/profile change,
build, tests, package or live game operation occurred. Keep Cosmos 7.06
fail-closed.

Reproduction against the exact executable:

```text
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x143D5D0
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x143D5D0 --size 0x122
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15286C0 --size 0x27D9
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1531E00 --size 0x97B0
python -B tools/native_vcall_abi_candidates.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --limit 250
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x33E6160 --max-slots 256
python -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x84 --offset 0x88 --access read --access write --limit-per-offset 100
```

Tool SHA-256 values:

| Script | SHA-256 |
| --- | --- |
| `native_function_disasm.py` | `26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0` |
| `native_pdata_function_group.py` | `fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26` |
| `native_vcall_abi_candidates.py` | `7b5184fc14c2314ab8a561838519aa3ea35df2ac68977527bb135efba92944` |
| `native_rtti_vtable_probe.py` | `4e60908321b4f2aef2d314dff8f7cc6c00e62252683434ff6482758beee50028` |
| `native_data_offset_xrefs.py` | `5d3f80c87679dcf6dd41bde71f027628eb6af24fc6ee06ecf32924e63fac34b8` |
| `native_rip_xrefs.py` | `dbff203dc5748821d69c66b1e4c8f75ba91044e36a45daa77c343be2207d08a3` |

The attempted higher-level QAM owner path is now CLOSED as a bounded negative:
root `0x144CB24` has no direct callers, RTTI slots, branch targets, absolute
pointer references or RIP-relative references in the exact image. Do not
repeat that path or the QAM builder/update scans. The slot-9 label caller and
its `R8` meaning remain unresolved; keep the load/network and live-runtime
gates separate.

### Resource-handle retain and release pair, 22 October 2026

The exact executable remains Windows x64 Steam Cosmos 7.06, build `25732212`,
file version `180836`, size `88,560,712`, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. Source
baseline is `f7d97b61fcf152677d0d30de34f6c1b48675c436`; profile and native source
remain unmodified. Provider: NMS.py commit
`b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`, `tools/data.json` SHA-256
`F311C9F54C0CCE199AB955A0E8DE2CFE2FCFB09274E557A2A27908C1B15BAF5F`, MIT.
Environment: CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7.

The active source calls old address `0x2D65980` with one argument,
`&p->paw_handle`, which is a pointer to a 32-bit resource handle. The old RVA
is not a 7.06 function entry: it lies inside a string/vector-growth routine
and is not safe to carry forward by address proximity.

An exact `.pdata` scan for atomic operations on object displacement `+0x134`
decoded 52,110,272 runtime-function bytes with zero skipped ranges and found
10 atomic operands. Matching the operation type, handle lookup, manager global,
and source ABI isolated the pair below:

- Retain `0x2D69720–0x2D69780`: reads a signed 32-bit handle through `RCX`,
  rejects zero/out-of-range handles, loads the manager through global RVA
  `0x59141E0`, indexes its `+0x60` table using the `+0x5C` count, checks
  resource state, and performs `lock inc dword ptr [resource+0x134]`.
- Release `0x2D65A80–0x2D65BBA`: follows the same one-pointer handle, global,
  count and table path; checks the same resource state and performs
  `lock xadd dword ptr [resource+0x134], -1`. When the previous count is one,
  it enters manager-side cleanup/list handling. This is a static mapping of
  the counter and cleanup path; actual unload/readiness behavior is not live
  verified.
- Resource-manager constructor root `0x2D62D60` stores its `this` pointer in
  global `0x59141E0`; destructor group `0x2D634C0` clears that global. This
  independently ties both helpers to the same manager object.

This maps the current source's retain ABI and the matching native release
operation. It does not establish a safe release point for the mod's cached
icons: current source has no corresponding destructor/reload/release path.
The 7.06 profile must remain fail-closed until resource lifetime, thread and
rendering behavior are verified, and all other required dependency gates pass.

False leads and tool lessons: a broad `+0x134` read/write scan produced 1,008
operands (1,000 printed); `0x2D6140` is destructor-like subobject teardown,
`0x2D5720` initializes the field to `0x7FFFF`, and old target `0x2D65980` is
inside an unrelated vector-growth method. Do not select by offset alone. The
atomic-only scan reduced this to 10 candidates, but the manager-global,
handle-table and one-pointer ABI evidence was still required. One RIP-target
query mistakenly used `0x58841E0`; correct RIP arithmetic is
`0x2D65A9B+0x2BAE745 = 0x59141E0`. The no-hit from the incorrect target is a
command/arithmetic error, not binary evidence.

Direct-call scan of release root `0x2D65A80` found 4,110 calls in 52,110,272
bytes and printed only 100. This is a generic, high-fanout handle operation;
the count alone does not identify callers. Do not rerun the same uncapped or
same-cap scan. The earlier retain scan found 1,114 direct calls and also
printed only a bounded sample.

Reproduction against the exact executable:

```text
python -B tools/native_atomic_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x134 --limit-per-offset 100
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D69720 --size 0x60
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D69720
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D62D60 --size 0x2BC
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D634C0 --size 0x250
python -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x59141E0 --limit-per-target 100
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D65A80 --size 0x13A
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D65AB1
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2D65A80 --context 12 --limit-per-target 100
```

Tool SHA-256 values:

| Script | SHA-256 |
| --- | --- |
| `native_atomic_xrefs.py` | `925073ec9c8abd0209a5c2ad53a8df81babf2a5e13cb7713f056151b4a2726f2` |
| `native_function_disasm.py` | `26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0` |
| `native_pdata_function_group.py` | `fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26` |
| `native_rip_xrefs.py` | `dbff203dc5748821d69c66b1e4c8f75ba91044e36a45daa77c343be2207d08a3` |
| `native_call_xrefs.py` | `7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf` |

The first attempt to launch four scans at once quoted the executable path
incorrectly around `No Man's Sky`; no output was captured and it was discarded
as a command-construction error. Individual corrected disassembly and group
queries against the exact hash succeeded. Do not interpret the failed attempt
as a zero-result scan.

No native source/profile change, build, tests, package or live game operation
occurred. Next bounded action: resume the independent session/local-network
gate from the exact session-derived byte producer, or map the QAM icon's
rendering consumer. Keep 7.06 disabled until these and the other release gates
are closed.

### Resource-manager globals and QAM owner lifecycle, 22 October 2026

The exact executable remains Windows x64 Steam Cosmos 7.06, build `25732212`,
file version `180836`, size `88,560,712`, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. Source
baseline is `f7d97b61fcf152677d0d30de34f6c1b48675c436`; provider commit is
`b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`, data SHA-256
`F311C9F54C0CCE199AB955A0E8DE2CFE2FCFB09274E557A2A27908C1B15BAF5F`, MIT.
Analysis used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7.

QAM resource-initializer root `0x1526240` loads its manager argument from RIP
global `0x6E1FC90` at `0x1526E4C`, then calls generic loader `0x2D63EA0` at
`0x1526E89`. Exact arithmetic is `0x1526E53+0x58F8E3D=0x6E1FC90`.

The write-only RIP-relative scan of this global found exactly two writes in
all `52,110,272` runtime-function bytes, with zero skipped ranges:

- Startup root `0x18600C2` allocates `0x210` bytes at `0x186017C`, passes the
  allocation to manager constructor `0x2D62D60` at `0x186018E`, and stores
  the returned pointer to `0x6E1FC90` at `0x1860198`.
- Constructor `0x2D62D60` stores its `this` pointer into global `0x59141E0`
  at `0x2D62D7A`, initializes manager fields through `+0x1C8`, and returns
  `this` in `RAX` at `0x2D62FF4`. The outer startup path therefore places the
  same manager pointer in both `0x59141E0` and `0x6E1FC90`.
- Teardown root `0x183D380` clears `0x6E1FC90` at `0x183D42C` before invoking
  the pointed object's virtual teardown. Resource-manager destructor group
  `0x2D634C0` clears `0x59141E0` at `0x2D63703`.

This independently closes the source's two-global identity check for this
build: old source globals `0x6E1BC10` and `0x5910190` map to `0x6E1FC90` and
`0x59141E0`, respectively, and both are set to the same object during
initialization. The object is allocated as `0x210` bytes; fields `+0x5C` and
`+0x60` are the count and handle-table pointer used by the QAM loader and
retain/release helpers. Static allocation/teardown evidence does not establish
live manager stability, resource readiness, or safe hook timing.

The first access-filter implementation decoded every instruction with full
Capstone details and was interrupted at `0x1403715` cumulative bytes; it had
no final count and is `NOT CHECKED`. The helper was optimized to keep the fast
`disasm_lite` whole-image pass and decode only exact target matches in detail.
The corrected write-filter run found two writes to each alias global with zero
skipped ranges. A general read/write scan of `0x6E1FC90` found 807 direct
RIP-relative references; only 100 examples were printed, and that count is not
an owner proof. Do not repeat the full access scan when the write-only result
already answers the global-lifecycle question.

Reproduction against the exact executable:

```text
python -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x6E1FC90 --access write --limit-per-target 100
python -B tools/native_rip_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x59141E0 --access write --limit-per-target 100
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1526240 --size 0x179C | Select-String -Pattern '0x1526E89' -Context 18,5
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x18600C2 --size 0x120
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D62D60 --size 0x2BC | Select-String -Pattern '0x2d62d7a:|0x2d6300' -Context 3,4
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x183D380 --size 0x120
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D634C0 --size 0x250
```

`native_rip_xrefs.py` SHA-256 after adding the reusable access filter is
`e9592776047326d362547caecc5b1c27c3f3e9e09f50705b2a2b65ee30f6b0f1`;
`native_function_disasm.py` SHA-256 remains
`26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`.

No source/profile change, build, tests, package or live game operation
occurred. The two manager globals are now statically mapped; keep icon
readiness, live manager lifetime, UI thread and rendering gates open. Next
bounded action: investigate the local/network load distinction or the QAM
item-icon render consumer, without repeating the QAM owner-path or the broad
global displacement scans.

### Resource fallback flag behavior, 22 October 2026

Within the exact resource manager loader group `0x2D63EA0`, instruction
`0x2D64418` checks `resource+0x13B`. When it is nonzero, the loader passes
`resource+0x110` and the type at `resource+0x8` to fallback resolver
`0x2D68490`; otherwise it keeps the original resource pointer. It then checks
`resource+0x13D` and increments `+0x134` only when that byte is zero. This
maps `+0x13B` as a fallback/substitute selector, not as a generic ready flag.
The mod currently skips custom resources with `+0x13B` set; that is
consistent with avoiding a substituted icon, but its live menu effect remains
unverified. The neighboring source field `+0x13A` was not read in this helper
and remains `PARTIAL`; do not infer its meaning from proximity.

Reproduction against the exact executable:

```text
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2D63EA0 --size 0x61B | Select-String -Pattern '0x13a|0x13b|0x13d' -Context 5,5
```

`native_function_disasm.py` SHA-256 is
`26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`.
No native source/profile change, build, tests, package or live-game operation
occurred. Keep the separate `+0x13A` meaning and actual icon readiness gate
open.

### Ship-eject and entered-cockpit hook contracts, 22 October 2026

The exact executable remains Windows x64 Steam Cosmos 7.06, build `25732212`,
file version `180836`, size `88,560,712`, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. Source
baseline is `f7d97b61fcf152677d0d30de34f6c1b48675c436`; the 7.05 profile and
native source remain unchanged. The NMS.py signature provider is pinned at
commit `b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`, data SHA-256
`F311C9F54C0CCE199AB955A0E8DE2CFE2FCFB09274E557A2A27908C1B15BAF5F`, MIT.

The exact signature candidate `cGcSpaceshipComponent::Eject` is function
`0x1754180`, with unwind group ranges `0x1754180–0x17541C9`,
`0x17541C9–0x1754351` and `0x1754351–0x175435C`. The body saves `RCX` as its
receiver, consumes Boolean inputs from `R8B` and `R9B`, and saves then
overwrites the incoming `RDX` home slot before reading it as an input. The
source detour's receiver and two Boolean positions match. Direct-call scan
found 16 callers in `52,110,272` runtime-function bytes with zero skipped
ranges. Ordinary local-player exit paths at `0x65A9DA` and `0x65B550` pass
`RDX=app+0x72C6F0`; other callsites also use local-player-derived pointers.
The native method itself does not consume `RDX`, so the mod callback must keep
its existing exact-pointer check: `Runtime::afterExit` arms only when
`appFor(player)` sees equality with `app+0x72C6F0`, otherwise it does nothing.
This gives a safe static boundary for unrelated callers, but does not prove
that every eject path should create an opportunity or establish live timing.
The RTTI probe found no validated vtable slot for this RVA; this is consistent
with the direct-call evidence and is not a no-caller result.

The unique `cGcPlayer::OnEnteredCockpit` candidate is `0x1483E20`, exact range
`0x1483E20–0x1483F31`. Its body uses `RCX` as the player receiver and has no
additional input parameters, matching the source's one-pointer detour. A
complete direct-call scan found three callers; each passes the application
local-player pointer at `app+0x72C6F0`. Its RTTI-vtable probe also returned
zero; the three direct callsites independently establish use. Both hooks are
now statically mapped to their source call shapes and local-player role. Their
exact-process hook creation, execution thread and live behavior remain open.

Reproduction against the exact executable:

```text
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1754180 --context 12 --limit-per-target 100
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1754180
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1754180 --size 0x1DC
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1754180 --max-slots 256
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1483E20 --context 12 --limit-per-target 100
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1483E20 --size 0x111
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1483E20 --max-slots 256
```

Tool SHA-256 values: `native_call_xrefs.py`
`7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf`;
`native_function_disasm.py`
`26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`;
`native_pdata_function_group.py`
`fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26`;
`native_rtti_vtable_probe.py`
`4e60908321b4f2aef2d314dff8f7cc6c00e62252683434ff6482758beee50028`.

One caller-output view was truncated by the tool while printing all 16 eject
call contexts. A narrower rerun retained all callsite IDs and only the
register-setup instructions; the `16` total is complete. Do not infer that all
16 callers pass the same `RDX` value; use the exact local-player equality
guard already present in the source.

No native source/profile change, build, tests, package or live game operation
occurred. Next bounded action: return to the load/local-network predicate or
the unresolved QAM item identity/rendering gates. Keep runtime hook and live
behavior checks separate.

### Direct QAM slot-9 caller and three-argument label ABI, 22 October 2026

The exact RTTI-confirmed QAM slot-9 function `0x153C0C0` has one direct E8
caller in the complete `.pdata` scan: call `0x1529288` in function range
`0x15288D6–0x1529E81`, chained to root `0x15286C0`. RTTI identifies that root
as `cGcQuickActionMenu`; its slot 9 is `0x153C0C0`. At the call, the caller
sets `RCX=RDI` (the QAM), `RDX=R15` (the label buffer), and
`R8=R15+0x100` (one byte immediately after the 256-byte label area). The
callee writes and terminates its primary label in the 256-byte `RDX` area and
clears the byte addressed by its original `R8`. The caller's immediate tail
does not read `[R15+0x100]`; that bounded observation does not establish what
other code does with the byte. Preserve it as an opaque third output pointer.

This closes the static caller and ABI part of the source dependency. The
current source callback in `native/src/bootstrap.cpp` accepts only two
arguments and calls the original with two; `MenuAdapter::afterLabel` in
`native/src/menu.cpp` uses a 128-byte caption/output boundary. A 7.06 port must
forward the third argument unchanged and respect the 256-byte native label
capacity. The output byte's semantic name, downstream consumer, detour thread,
and live UI behavior remain `NOT CHECKED`. Do not change the 7.05 profile or
claim 7.06 support from this static mapping alone.

Reproduction against the exact executable (CPython 3.11.9, pefile 2024.8.26,
Capstone 5.0.7):

```powershell
& $python -B tools/native_call_xrefs.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --target-rva 0x153C0C0 --context 12 --limit-per-target 100
& $python -B tools/native_pdata_function_group.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x1529288
& $python -B tools/native_rtti_vtable_probe.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --target-rva 0x15286C0 --max-slots 30
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x15286C0 --size 0x181D
```

The call scan decoded `52,110,272` runtime-function bytes and skipped zero
ranges; it reports one direct call to this target. This count covers direct
decoded calls only and is not proof against other invocation forms. Relevant
tool SHA-256 values: `native_call_xrefs.py`
`7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf`;
`native_pdata_function_group.py`
`fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26`;
`native_rtti_vtable_probe.py`
`4e60908321b4f2aef2d314dff8f7cc6c00e62252683434ff6482758beee50028`;
`native_function_disasm.py`
`26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`.
No native source/profile change, build, tests, package or live game operation
occurred. Next bounded action: map the source-safe QAM item identity across
the native update/reconciliation cycle, then continue the remaining exact
source and live-runtime gates; do not repeat the closed label-caller scan.

### QAM row-flag first stores and update-path mutation, 22 October 2026

Superseded on 23 October: this section conflates an interior context-descriptor pointer with a source item. Its `0xFFFF0100` versus `0x15` argument is invalid. Constructor byte stores remain valid; see the affine-base correction in the latest handoff.

The exact item constructor `0x143D5D0–0x143D6F2` stores `R9B` as a one-byte
write to item `+0x4C` and its fifth stack argument as a one-byte write to
`+0x4D`. The active source calls this constructor with `false,true`, so its
post-construction checks observe `+0x4C=0` and `+0x4D=1`. Those observations
describe the constructor return only.

Root-aligned disassembly of QAM update root `0x15286C0` shows a row candidate
at `RSI` being compared against an update candidate at `+0x84`, `+0x8C`,
through the 8-byte equality helper at `+0x40`, at `+0x80`, and as a dword at
`+0x4C`. The
candidate scratch row initializes the 16 bytes at `[R12+R14-0x4B8]` to zero
and its expected `+0x4C` dword to `0x15`; the bounded root disassembly shows
only those initializations and later reads for these candidate fields. A
source-created item instead starts with qword `item+0x40 = -1`; its fourth
argument sets byte `+0x4C=0` and fifth argument sets byte `+0x4D=1`, so the
comparison dword at `+0x4C` is `0xFFFF0100`. It therefore fails this exact
matched-row comparison on `+0x4C` and advances to the next candidate. On a
successful match, instruction `0x152960B` writes `0x15` to `[RSI+0x4C]` and
the preceding code clears `+0x84..+0x93`.

This gives static evidence that an item created with the current constructor
arguments avoids this matched-row mutation path, independently of the marker
bytes. It does not prove that no other update path mutates the item or that
the unmatched row is retained through every rebuild. The constructor
argument meanings and `+0x4D` consumer remain unresolved.

The exact match sequence compares qwords at `[RSI+0x8C]` and `[RSI+0x84]`,
then applies the 8-byte equality helper at `[RSI+0x40]`, compares a dword at
`+0x80`, and compares a dword at `+0x4C` against candidate source-row values.
Any shown mismatch advances to the next candidate; the `+0x4C=0x15` write is
on the successful match path. This is distinct from the following binding
pass, which really does compare row qwords at `+0x88` and `+0x90` before it
can write a binding index to `+0xD8`. The earlier gate table compressed
these two passes into one statement; it has now been corrected to list both.
The source marker at `+0x88`
overlaps 4 bytes of the qword at `+0x84` and 8 bytes of the qword at `+0x8C`,
so it deliberately changes data the reconciler compares. This explains why a
marker can prevent an ordinary key match, but does not by itself prove how an
unmatched mod row is retained or handled after the candidate loop. On a
successful match, the update path clears the 16 bytes at `+0x84..+0x93`,
including the source marker at `+0x88`; it also writes `+0x4C=0x15`. Thus the
adapter's marker and constructor-field checks remain valid only if the custom
row avoids that match path. The current constructor's `+0x4C` dword mismatch
provides that protection in this exact comparison path; other update paths
and live retention remain open.

The update root also creates 0xE0-stride rows and writes the `+0x4C` byte;
the exact trigger-root scan returned six `+0x4C` byte tests, but the `RSI`
object at those sites was not independently tied to a QAM item. Keep those
six hits as leads, not item-field mappings. A whole-image detailed operand
scan for `+0x4C/+0x4D` was stopped after decoding `0x1403715` runtime-function
bytes because it was too slow for displacement-only discovery. It produced
no final counts and is `NOT CHECKED`, not a zero-match result. Prefer exact
owner paths and skip another full-detail whole-image offset scan.

This turn also made the smallest safe source ABI correction: `label_original`
and `labelHook` now forward the QAM label method's third pointer unchanged.
The installed label RVA and compatibility profile remain at their 7.05
values, so the 7.06 mapping is still fail-closed. No build, tests, package or
live game operation occurred.

Reproduction against the verified executable:

```powershell
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x143D5D0 --size 0x122
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x15286C0 --size 0x181D
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x1531E00 --size 0x97B0
& $python -B tools/native_data_offset_xrefs.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --offset 0x4C --offset 0x4D --access read --limit-per-offset 5
```

`native_function_disasm.py` SHA-256 is
`26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`;
`native_data_offset_xrefs.py` SHA-256 is
`5d3f80c87679dcf6dd41bde71f027628eb6af24fc6ee06ecf32924e63fac34b8`.
Next bounded action: trace the update match source/key and prove whether the
custom marker makes the appended row bypass or enter the matched-row path;
then continue the unresolved icon, binding, load and live-runtime gates.

### QAM update binding pass and `+0xD8` index, 22 October 2026

The same update root has a separate pass over current 0xE0-byte rows from the
pointer at `[R15+0x618]`, with count at `[R15+0x614]` (`R15` is not independently
named here). It retrieves the candidate descriptor array through QAM getter
`0x153C7A0`, then scans 0x540-byte candidate rows. For
each menu row it compares action `+0x4`, dword `+0x40`, qwords `+0x90` and
`+0x88`, the 8 bytes at `+0x44`, dword `+0x84`, and dword `+0x50`. Only when
these comparisons pass does it write the candidate counter to row `+0xD8`
(`0x1529D87` / `0x1529E47`). A mismatch advances to another candidate; this
loop does not write a binding index for that row. This maps the source's
`binding==-1` check to an unmatched descriptor index, subject to other update
paths and rebuild behavior remaining unverified.

Correction on 23 October: the following row-update paragraph uses an interior descriptor pointer as an item base. Its flag-dword protection argument is superseded; retain the separately established copied-row binding-loop observations above.

This is distinct from the earlier row-update match pass. That pass compares
qwords at `+0x84/+0x8C`, uses an 8-byte equality helper at `+0x40`, and compares
`+0x80/+0x4C`; on a match it clears `+0x84..+0x93` and writes `+0x4C=0x15`.
The active source's constructor flags make its `+0x4C` dword `0xFFFF0100`,
which fails that pass's expected `0x15` value. In the separate binding pass,
the source marker stored at `+0x88` changes the qwords explicitly compared at
`+0x88/+0x90`; whether any generated descriptor can equal the marker remains
unverified. Preserve both facts: the marker is native comparison data and it
serves as the source's custom-row discriminator.

The helper called at `0x1529D4F` is leaf code at `0x1A25460`, outside `.pdata`.
Its exact body compares the two dwords at each input pointer and ANDs the two
equal results, so it is an 8-byte equality check, not a string comparison.
QAM getter `0x153C7A0` returns
`QAM+0x2D0+state*0x3480`, after selecting state from the local-player/session
path. The returned descriptor values and full vector retention semantics are
not established by that getter alone.

Reproduction against the verified executable:

```powershell
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x15286C0 --size 0x181D
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x1A25460 --size 0x80
& $python -B tools/native_pdata_function_group.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x153C7A0
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x153C7A0 --size 0x9D
```

`native_function_disasm.py` SHA-256 is
`26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`;
`native_pdata_function_group.py` SHA-256 is
`fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26`.
Next bounded action: identify the candidate descriptor field values/producer
and prove row retention over the full rebuild path; do not rerun generic
`+0x88/+0x90` displacement searches.


### QAM candidate-key dataflow and Session-state setter, 22 October 2026

The QAM update root `0x15286C0` does not leave the descriptor keys at the constructor's zero values. In the branch beginning at `0x1529737`, it copies a full `0xE0`-byte source row from `R13` into a stack temporary, then copies that row into the selected array returned by QAM getter `0x153C7A0`, at `getter-result + RBX + 0x80` (`0x15297C5–0x1529849`). A second branch selects an existing QAM row through its per-depth pointer/count entries, uses the `0xE0` row stride, and copies another full row to the same descriptor area (`0x152986F–0x15299B3`). Consequently, candidate descriptor qwords `+0x88` and `+0x90` are populated from source-row qwords `+0x08` and `+0x10`; they are dynamic copied data, not constructor-guaranteed zeros. This corrects the earlier inference based on the group constructor alone.

This establishes the source-to-destination copy and the key offsets used by the separate binding pass. It does not establish the actual values in each candidate, whether any can equal the mod marker, or whether an unmatched row survives every rebuild. Keep the source marker and binding/reconciliation behavior `PARTIAL`; do not infer marker safety from zeroed constructor fields.

The Session RTTI selector must use the full decorated name `.?AVSession@cGcMatchmaking@@`. It validates vtable `0x4AAA640` with 19 executable slots; slot 11 is `0xACA370`. The earlier short selector `.?AVSession@@` returned zero validated locators and was a query miss, not a binary negative. An owner-bounded write scan over this vtable found one `+0x41C` write in slot 11 (`0xACA3A5`) and no `+0x418` writes in its `.pdata` methods. Slot 11 clears the first byte of the 16-byte region before copying it; the remaining 15 bytes are not proven zero.

Non-vtable helper `0xACA550` reads the old dword at `this+0x418`, writes `EDX` there, then reports the old/new dwords to each listener in the `this+0x470` array (count `+0x46C`, stride `0x40`) through its slot `+0x10`. This statically maps `+0x418` as a numeric state field. The exact direct-call scan found nine E8 sites in `.pdata`: `0xACA3CB` passes 0; `0x237E1B`, `0x22B841` and `0x23ACF3` pass 4; `0x23870F`, `0x23A3C5` and `0x23A611` pass 3; `0x239E64` passes 5; and `0x23BF04` passes 2. The load predicate's `+0x418 == 4` is therefore a concrete state test, but the state-4 name, exact dynamic object at the load path's manager slot `+0x1A8`, and local/network meaning remain unresolved. This call list covers direct decoded calls only.

Several probe attempts in this pass failed before producing evidence: `native_call_xrefs.py --context 14` exceeds its supported maximum of 12; `native_vtable_member_xrefs.py` does not accept `--limit-per-offset`; and the short Session RTTI selector misses the decorated namespace. The corrected queries below replace those attempts. None of the failed invocations is a zero-match result.

Reproduction against the exact executable (Steam build `25732212`, SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`):

```powershell
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x15286C0 --size 0x181D
& $python -B tools/native_rtti_vtable_probe.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --type-name '.?AVSession@cGcMatchmaking@@' --max-slots 96
& $python -B tools/native_vtable_member_xrefs.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --vtable-rva 0x4AAA640 --slot-count 19 --offset 0x418 --offset 0x41C --access write
& $python -B tools/native_call_xrefs.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --target-rva 0xACA550 --context 12 --limit-per-target 40
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0xACA550 --size 0x130
```

Tool SHA-256: `native_function_disasm.py` `26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`; `native_rtti_vtable_probe.py` `4e60908321b4f2aef2d314dff8f7cc6c00e62252683434ff6482758beee50028`; `native_vtable_member_xrefs.py` `e621c1062b52e08a3cd8f3ab2f9844e8e8be78487d08d998a60ac840ef482cbc`; `native_call_xrefs.py` `7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf`. This pass used owner-anchored exact-build disassembly, not the external NMS.py pattern table.

Next bounded actions: inspect the exact producer/control-flow around the state-4 setter sites and find a positive `+0x41C` write on the same RTTI-anchored session object; separately follow the QAM source rows feeding the dynamic candidate copies. Do not repeat the broad `+0x41C` offset scan or infer local/network meaning from state number alone. No 7.06 profile, target RVA, package or live game state changed; no build or tests were run. Keep the 7.06 profile fail-closed.


### QAM `+0xD8` object-base correction, 22 October 2026

The previous mapping of the source's `item+0xD8` check to the native binding pass is withdrawn. Root `0x15286C0` saves `RCX` (the RTTI-confirmed QAM receiver) in `RDI` and the incoming third argument `R8` in `R15` (`0x15286DE`, `0x15286ED`). It then passes that third-argument pointer to builder `0x152A1C0` as `RDX` at `0x1528893`.

The binding loops read row counts/pointers from the third-argument object at `+0x614/+0x618` and `+0x51C/+0x520`, walk `0xE0`-byte rows, compare them against QAM descriptors returned by `0x153C7A0`, and write the matched candidate ordinal to `[row+0xD8]` at `0x1529D87` and `0x1529E47`. The runtime type of that object and any alias to QAM source vectors are not established. A same-offset match does not prove that the source's QAM `item+0xD8` is modified.

The source QAM row's `+0xD8` is confirmed only as constructor-initialized to `-1`; whether another native path changes that row remains `NOT CHECKED`. The binding pass still compares QAM descriptor keys at `+0x88/+0x90`; those keys receive dynamic copied source-row bytes as recorded above. Keep the source check fail-closed without claiming it is a mapped persistent invariant.

A targeted vcall scan for slot offset `0x0` and same-range QAM displacement `+0xA050` decoded all `52,110,272` `.pdata` bytes with zero skipped ranges, but returned zero matching function ranges/calls. This is only a negative for that filter; the actual virtual caller may not reference the QAM field in the same function. Do not repeat this filter unchanged.

Reproduction:

```powershell
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x15286C0 --size 0x181D
& $python -B tools/native_vcall_xrefs.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --slot-offset 0x0 --require-field 0xA050 --context 12 --limit-per-range 30
```

`native_vcall_xrefs.py` SHA-256: `24a792fce464fd6639a3de92923fcd31bc1bbbb6427acb0b866fc97308174621`. This bounded negative does not prove that the update method has no virtual caller.

Next bounded action: establish the runtime owner and pointer origin of the update's `R8` argument through a validated caller/constructor path, then prove or reject aliasing with QAM source vectors and trace QAM-row `+0xD8` writes. No source/profile mapping changed; no build, tests, package or live operation occurred. Keep 7.06 fail-closed.


### Session state-4 transition through the matchmaking session slots, 22 October 2026

Root `0x22B6C0` saves its manager receiver from `RCX` in `RBX`, obtains an event-row list through manager member `+0x480`, and walks rows. For the matching case, it reads the event identifier at row `+0x10`, then iterates three session pointers from `[manager+0x1A0+index*8]`. The index table is at RVA `0x4A49134`; its three values are 0, 1 and 2. Each candidate session identifier at `+0x630` is compared with the event identifier. On a match with the event status dword at row `+0x4` nonnegative, caller `0x22B841` invokes helper `0xACA550` with `RCX=session` and `EDX=4`.

Because index 1 is explicitly included, this exact static event path can set state dword `+0x418` to 4 on the manager's `+0x1A8` session entry when its identifier matches. This links the load predicate's state-4 test to a real transition path on the same array slot. The event kind and nonnegative-status meaning are not named by this evidence. It also does not set or explain the separate byte at session `+0x41C`, so the load candidate's `R9B` meaning and local/network distinction remain unresolved.

RTTI probing `0x22B6C0` returned no validated vtable slot; this helper is mapped here by its exact manager/session dataflow, not by a class-method label. The three table values and caller branch are static observations only.

Reproduction against Steam build `25732212` and executable SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`:

```powershell
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x22B6C0 --size 0x1A0
& $python -B tools/native_rtti_vtable_probe.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --target-rva 0x22B6C0 --max-slots 96
& $python -B -c 'import pefile,sys; p=pefile.PE(sys.argv[1]); r=0x4A49134; print("RVA",hex(r),"bytes",p.get_data(r,3).hex(" "))' 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe'
```

`native_function_disasm.py` SHA-256: `26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`; `native_rtti_vtable_probe.py` SHA-256: `4e60908321b4f2aef2d314dff8f7cc6c00e62252683434ff6482758beee50028`. Data parsing used pefile `2024.8.26`; no external signature pattern was used.

Next bounded action: identify a positive write to the same session's `+0x41C` field and trace the event-row kind/status producers before naming state 4 or the load byte as local/network. Keep the profile disabled; no source/profile mapping, build, tests, package or live game operation occurred.


### QAM slot-0 receiver-filter false lead, 22 October 2026

A full `.pdata` scan for indirect slot offset `0x0` with same-range displacement `+0x116B10` returned one callsite, `0x924DED` in root `0x924C90`. Root-aligned disassembly shows that `+0x116B10` is used earlier at `0x924D60` as the receiver for a separate direct call to `0x1527BD0`; the slot-0 call at `0x924DED` instead sets `RCX=[RDI]`. It does not pass the QAM subobject pointer established at `RDI+0x116B10`. RTTI probing root `0x924C90` found no validated vtable slot. Reject this call as evidence for `cGcQuickActionMenu::Update` or its third-argument owner.

The earlier slot-0 filter requiring `+0xA050` returned no matching ranges. Both results are bounded same-range filters and do not establish that the QAM update has no virtual caller. They show why the receiver at the exact indirect call must be compared with the proven subobject, rather than inferring it from another offset in the same function.

Reproduction against the exact executable:

```powershell
& $python -B tools/native_vcall_xrefs.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --slot-offset 0x0 --require-field 0x116B10 --context 12 --limit-per-range 20
& $python -B tools/native_function_disasm.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --rva 0x924C90 --size 0x16F
& $python -B tools/native_rtti_vtable_probe.py --exe 'C:\Program Files (x86)\Steam\steamapps\common\No Man''s Sky\Binaries\NMS.exe' --target-rva 0x924C90 --max-slots 96
```

`native_vcall_xrefs.py` SHA-256: `24a792fce464fd6639a3de92923fcd31bc1bbbb6427acb0b866fc97308174621`. This receiver-mismatch lead is rejected; the actual QAM update callsite and `R8` owner remain `NOT CHECKED`.

Next bounded action: continue from a caller or constructor that proves the QAM receiver at the indirect dispatch; use the `R8` origin there to identify the vector owner before mapping `+0xD8`. Do not repeat either same-range filter unchanged. Keep 7.06 disabled.

### QAM pending-selection byte owner and lifecycle, 22 October 2026

An exact displacement scan of the verified executable for 0xA16C decoded
52,110,272 runtime-function bytes and skipped zero ranges. It found eight
operands. Five were stack-relative writes of a float at RSP+0xA16C inside
large unrelated functions; they are stack locals, not QAM field accesses.
The remaining three are one read and two writes in the established QAM
builder and TriggerAction paths.

The read at 0x152C33E compares byte [R12+0xA16C] with zero. Its function is
the builder rooted at 0x152A1C0. At entry, the builder saves RCX at [RSP+8],
pushes eight nonvolatile registers, and sets RBP to RSP-0x5638. Therefore
[RBP+0x5680] aliases the saved entry RCX slot. The path loads that pointer to
R12 at 0x152B047 and later checks [R12+0xA16C]. The clear at 0x152E5D7 writes
zero to that same receiver-relative byte after the builder's selected-depth
processing loop. This recovers the exact owner even though the field access
occurs in a chained .pdata range.

The set at 0x1538A5A is in TriggerAction's chained group rooted at 0x1531E00.
That function copies entry RCX directly to R15 at 0x1531E35. In the relevant
branch it increments QAM depth at +0xA050, clamps the depth to 2, sets the
byte [R15+0xA16C] to 1, then calls the already mapped selection setter
0x151ADB0 with the QAM depth field, depth and selected index. The builder
later tests and clears this byte. The static behavior supports the narrow
name `pending selection state`; exact live timing and visible menu behavior
remain unverified.

An RTTI-bounded scan of the 16-slot QAM vtable 0x4A504E0 found seven methods
with .pdata and no +0xA16C operand matches; nine slots had no .pdata and were
not scanned. That zero was not a whole-class negative: the exact consumers
are the builder and TriggerAction paths, outside the supplied set of seven
vtable method roots. A global displacement scan followed by unwind-root,
receiver and stack-slot provenance closed this field without repeating the
failed owner-only query.

The scan also followed the separate matchmaking manager +0x480 zero-store
candidates. The write at 0x222D05F/0x222D1A9 belongs to constructor root
0x222CF40, which allocates and initializes a 0x4B0-byte record; its one direct
caller is 0x222F0D0. Writes at 0x223742A and 0x2237E0F belong to reset /
construction roots 0x2237400 and 0x2237CE0. The former has four direct
callers, and the latter has three, passing stack-output and byte arguments
without a validated matchmaking-manager owner. Other candidate roots
0x222B3C0 and 0x222C0E0 had zero direct E8 callers in the completed scan.
RTTI probes of 0x222B426, 0x222C134, 0x222CF40, 0x2237400, 0x2237D1A and
0x2237CE0 found no validated vtable slots. These constructor zeros are not
positive event-list producers and do not map the manager's +0x480 source. No
owner-proven positive writer for that manager field has been found.

Corrected search notes: native_data_offset_xrefs.py does not accept
--context; the invocation was rejected before decoding, then rerun without
that option. A caller search against interior range 0x2237D1A returned zero;
the unwind group identifies 0x2237CE0 as its root, and a corrected direct
call scan of that root found three callers. Do not use a direct-call zero for
an interior chained range as an owner-level result. In PowerShell, quote the
No Man's Sky executable path as a double-quoted variable so its apostrophe
cannot split a single-quoted command.

Reproduction against Steam build 25732212 and executable SHA-256
13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499:

```powershell
$nmsExe = "C:/Program Files (x86)/Steam/steamapps/common/No Man's Sky/Binaries/NMS.exe"
python -B tools/native_data_offset_xrefs.py --exe $nmsExe --offset 0xA16C --access read --access write --limit-per-offset 30
python -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A504E0 --slot-count 16 --offset 0xA16C --access read --access write
python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x152C33E
python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x1538A5A
python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x152A1C0 --size 0x253D
python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1531E00 --size 0x97B0
python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x152E5D7 --size 0xA0
python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x2237CE0 --context 12 --limit-per-target 20
```

Tool SHA-256: native_data_offset_xrefs.py
5d3f80c87679dcf6dd41bde71f027628eb6af24fc6ee06ecf32924e63fac34b8;
native_vtable_member_xrefs.py
e621c1062b52e08a3cd8f3ab2f9844e8e8be78487d08d998a60ac840ef482cbc;
native_pdata_function_group.py
fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26;
native_function_disasm.py
26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0;
native_call_xrefs.py
7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf;
native_rtti_vtable_probe.py
4e60908321b4f2aef2d314dff8f7cc6c00e62252683434ff6482758beee50028.
The tools used pefile 2024.8.26 and Capstone 5.0.7. No source/profile mapping
changed; no build, tests, package, push or live game operation occurred.

Next bounded action: resume the independent source-port gate at the exact
7.06 load candidate's fifth-argument branch and prove its caller roles before
naming local/network semantics. Keep the profile disabled while the remaining
QAM label/resource, custom-row and runtime gates remain open.

### Session manager ownership and key-field audit, 22 October 2026

The official [Hello Games release log](https://www.nomanssky.com/release-log/) still lists Cosmos 7.06 as newest on 22 October 2026; no 7.07 entry is present. The current Nexus [files page](https://www.nexusmods.com/nomanssky/mods/4579?tab=files) still lists file 49469, package 0.10.2-native-test, uploaded 3 October. The available compatibility text remains limited to Windows/Steam Cosmos 7.05, build 25624745. This is not a 7.06-ready package.

The load-adjacent predicate reads the application pointer at data RVA 0x6E8D708, then the member at application+0x941C70, manager entry +0x1A8, session dword +0x418 and the first byte of the 64-byte region at +0x41C. RTTI validates PlayfabSession at vftable 0x4AA9F98 as derived from Session at 0x4AAA640. In both known vtables, slot 8 at offset +0x40 resolves to 0x1C7A60, which returns constant true. The application member is now class-confirmed as the Steam manager by the exact construction and install chain below. Conditional on the object at manager+0x1A8 being a Session/PlayfabSession instance, the observed predicate reduces to state==4 and byte[session+0x41C]!=0. The dynamic type in that session slot remains unproven, and the byte is not identified as network state.

The RTTI-anchored PlayfabSession slot 20, root 0x238750, copies four 16-byte chunks from +0x41C, +0x42C, +0x43C and +0x44C into a 64-byte lookup record. It combines that record with the byte at +0x8 and searches application-owned tables. The constructor root 0xAD5A90 allocates 0xA48-byte session objects, clears the leading +0x41C byte, installs the PlayfabSession vtable, and stores the three objects at manager+[0x1A0,0x1A8,0x1B0] using selector bytes 00 01 02 from data RVA 0x4A49134. This makes +0x41C key-like and empty/nonempty-tested; it still does not identify the field or prove local/network meaning. It also does not prove that this constructor's manager is the object stored at application+0x941C70.

The exact write-filtered scan for application displacement +0x941C70 decoded 52,110,272 .pdata bytes, skipped zero ranges and found one direct write: 0x3340AA in root 0x333CA0. RTTI identifies root 0x333CA0 as slot 3 of cGcApplicationShutdownState vftable 0x4A50A90. It reads the current member at 0x33407F, calls virtual offsets +0x58 and +0x18 on that object, then stores zero at +0x941C70. The initial call scan against interior chained range 0x334068 returned zero and is superseded by the root query against 0x333CA0; that root also has zero direct E8 callers, but its RTTI vtable slot proves an indirect dispatch path. Neither zero is proof of no invocation.

The bounded cGcApplication vtable scan validated vftable 0x4A50888 with six slots, four .pdata-backed roots and two slots without .pdata; it found no +0x941C70 operands in the scanned roots. The complete offset scan found 275 operands, one direct write, and no LEA using that exact displacement. A write-only RIP scan of global pointer RVA 0x6E8D708 found three stores: allocation assignment at 0x2C6C1C, static zero initialization at 0x32BCA0, and a zero store at 0x62D849. The first stores an allocated 0x95F210-byte application object. Constructor root 0x2C6E20 calls subobject initializer 0x2CE200 on application+0x937130; the earlier claim that the +0x941C70 member was unreachable from the +0x937130 subobject is retracted below because it used incorrect subtraction. The positive setter is in a separate startup root 0xAE8810; the 0x2CE200 accesses were not re-evaluated.

Do not repeat the full unfiltered application-global reference scan (26,301 references), the full +0x941C70 operand dump, the 0x334068 interior call scan, or the same 0x2CE200 constructor window. At that time the positive installation/type gate remained open; the correction below closes it. The exact session-construction invocation, the caller/runtime role of 0x4906BD, and local/network semantics remain open. Keep the source hook and 7.06 profile fail-closed.

One raw-PE probe initially used the invalid RVA 0x4AA91134 and failed before reading data. The correct selector table RVA is 0x4A49134 and its bytes are 00 01 02. Treat the first error as TOOL ERROR, not a scan result.

Reproduction with the exact executable SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499:

    $py = $python
    $nmsExe = "C:/Program Files (x86)/Steam/steamapps/common/No Man's Sky/Binaries/NMS.exe"
    & $py -B tools/native_rip_xrefs.py --exe $nmsExe --target-rva 0x6E8D708 --access write --limit-per-target 300
    & $py -B tools/native_rtti_vtable_probe.py --exe $nmsExe --type-name '.?AVcGcApplication@@' --max-slots 96
    & $py -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A50888 --slot-count 6 --offset 0x941C70 --access any
    & $py -B tools/native_data_offset_xrefs.py --exe $nmsExe --offset 0x941C70 --access write --limit-per-offset 100
    & $py -B tools/native_data_offset_xrefs.py --exe $nmsExe --offset 0x941C70 --limit-per-offset 1000 | Select-String -Pattern 'lea|SCANNED_RUNTIME_FUNCTION_BYTES|SKIPPED_RUNTIME_RANGES|OPERAND_MATCHES|PRINTED'
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x3340AA
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x333CA0 --size 0x468
    & $py -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x333CA0 --max-slots 40
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2C6E20 --size 0x883
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2CE200 --size 0x7C0
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0xAD5A90
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0xAD5A90 --size 0x30E
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x238750
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x238750 --size 0x641
    & $py -B -c 'import pefile,sys; p=pefile.PE(sys.argv[1]); r=0x4A49134; print(hex(r),p.get_data(r,3).hex(" "))' $nmsExe

Tools used CPython 3.11.9 (SHA-256 5F7B89A612C9B8AF1D6456CDFCD1DBE5CA630849E79AEBCED9BEE9A6694952EC), pefile 2024.8.26 and Capstone 5.0.7. Tool hashes: native_rip_xrefs.py E9592776047326D362547CAECC5B1C27C3F3E9E09F50705B2A2B65EE30F6B0F1; native_data_offset_xrefs.py 5D3F80C87679DCF6DD41BDE71F027628EB6AF24FC6EE06ECF32924E63FAC34B8; native_rtti_name_inventory.py 253259913FC3AE0F4E7D011E0B56E45CEB3AA88CC2EECAA90B0617B7A86DCCBC; native_rtti_vtable_probe.py 4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028; native_vtable_member_xrefs.py E621C1062B52E08A3CD8F3AB2F9844E8E8BE78487D08D998A60AC840EF482CBC; native_pdata_function_group.py FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26; native_function_disasm.py 26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0; native_call_xrefs.py 7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF.

No source/profile mapping changed. No tests, build, package, push or live game operation occurred.

Next bounded action: identify the dynamic invocation or registration path that populates the confirmed manager session array, then classify the still-untyped load caller without assigning local/network semantics from the key byte. Keep the 7.06 profile disabled.

### Correction: application manager installation and session dispatch, 22 October 2026

This correction supersedes the preceding session-manager handoff statements that the positive installation and dynamic type of application+0x941C70 remained open, the 16 October note that the constructor member had not been connected to that global, and the claim that helper 0x2CE200 could not reach that member. The latter claim used incorrect subtraction. The correct relative displacement is 0x941C70 - 0x937130 = 0xAB40. The accesses inside 0x2CE200 were not re-evaluated by this correction.

The [Hello Games release log](https://www.nomanssky.com/release-log/) still lists Cosmos 7.06 first and has no 7.07 entry. The current [Nexus description](https://www.nexusmods.com/nomanssky/mods/4579?tab=description) still lists package 0.10.2-native-test, last updated 3 October 2026, for Windows/Steam build 25624745 only. The exact local executable remains Windows x64 Steam Cosmos 7.06, build 25732212, file version 180836, size 88,560,712 bytes, SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499. The source HEAD remains f7d97b61fcf152677d0d30de34f6c1b48675c436. The active native profile remains Cosmos 7.05, build 25624745, SHA-256 671de22649274b49fa07f5a246bc7252c4e08bb9ab623d2e65722fbab4e497a4.

#### Positive installation and owner chain

Root 0x2C6BB7 contains the application startup callsite: it loads the application pointer at 0x2C6D31, adds 0x937130 at 0x2C6D38, and calls root 0xAE8810 at 0x2C6D3F. Root 0xAE8810 preserves incoming RCX in RDI. It allocates 0xA60 bytes and, on the successful path, calls constructor 0xAC7050 before storing the returned object at [RDI+0xAB40]; the allocation-failure path stores zero. Therefore the constructed member address is application+0x937130+0xAB40 = application+0x941C70.

Constructor 0xAC7050 first calls base constructor 0xAC73D0. It then installs primary vtable 0x4AAA358 at [this] and secondary vtable 0x4AAA618 at [this+0x1B8]. Exact RTTI identifies 0x4AAA358 as cGcMatchmakingPlayfabSteam, derived from cGcMatchmakingPlayfab. After storing the returned object at application+0x941C70, the startup function immediately calls its vtable slot 7 at offset +0x38, target 0x24B8F0. The installed pointer and its dynamic Steam-manager type are now statically confirmed.

The manager's slot 8 target 0x24B920 forwards the same RCX receiver to root 0x22BF00. That root preserves the receiver in RSI and passes it to dispatcher 0x22B6C0. The dispatcher reads the manager's +0x480 event-list member and walks session pointers at [manager+0x1A0+index*8], using selector values 0, 1 and 2; a matching event can set state +0x418 to 4. This confirms a manager-owned session-array read/dispatch path. It does not prove how those pointers are populated or name index 1 as local versus online.

#### Rejected initializer route and remaining link

Slot 7 method 0x24B8F0 calls helper 0x22B230. The helper's indirect call at vtable offset +0x290 selects slot 82. RTTI resolves that slot to 0x36A410 for the confirmed Steam manager; the bounded body returns -1. This is not the session-array initializer and is a rejected lead.

Root 0xAD5A90 remains the exact static routine that allocates 0xA48-byte PlayfabSession objects and stores three pointers at manager offsets +0x1A0, +0x1A8 and +0x1B0. Its invocation on the manager stored at application+0x941C70 remains unproven. The completed direct E8 scan found zero callers; the direct immediate-jump scan found zero; literal preferred-base pointer scan found zero across 88,155,208 bytes in seven non-relocation sections; exact 32-bit RVA-data scan found zero across 31,431,680 bytes in four non-executable sections; and the earlier bounded direct-RIP scan found zero. The owner-bounded Steam-manager vtable scan checked 42 .pdata method roots and found zero writes to +0x1A0/+0x1A8/+0x1B0; 44 vtable slots had no .pdata range. These are scoped negatives, not proof against dynamic registration or aliases.

A full .pdata write-filter scan of displacement +0x1A0 decoded 52,110,272 bytes with zero skipped ranges and counted 1,686 operands. It printed only its first 100 matches, many of which were stack locals. This was too noisy to assign object ownership; do not repeat the same global displacement scan. The constructor's exact stores and the manager's exact dispatcher reads remain separate evidence until an invocation or registration path is found.

The load predicate's application member is now class-confirmed as the Steam manager, but the runtime object in its +0x1A8 entry is still not linked to 0xAD5A90. Therefore state==4 and nonzero byte at session+0x41C remains conditional on that session object being PlayfabSession. Slot 20 uses the 64-byte +0x41C region as part of an application-table lookup key; the byte is still not identified as a network flag.

A new exact caller trace found one direct call to root 0x48FA60 at 0x497648 inside chained range 0x497464-0x4978CD, itself belonging to group root 0x495640. The query against interior 0x497464 returned zero and is superseded by the root-aligned query against 0x495640, which found one caller at 0x4955F8 inside chained range 0x4955B4-0x495623. native_pdata_function_group resolves that range to root 0x495560. At 0x4955F8 the code computes R9B from a virtual call through +0x40 and a nonzero test of [RBX+0x41C], then calls 0x495640. An initial xref and RTTI query against interior 0x4955B4 returned zero and is superseded by root-aligned queries: root 0x495560 has four direct E8 callers, two in root 0x32F385 and two in root 0x48E400; the RTTI probe against 0x495560 found no validated vtable slot. This remains static Boolean dataflow, not proof of local/network semantics or the named roles of these functions.

#### Reproduction

Run from the repository root against the verified executable. The placeholders must resolve to the exact file and interpreter recorded in the report header.

    $py = "<verified CPython 3.11.9 executable>"
    $nmsExe = "<verified Cosmos 7.06 NMS.exe>"
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2C6BB7 --size 0x21D
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0xAE8810 --size 0x513
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0xAC7050 --size 0x375
    & $py -B tools/native_rtti_vtable_probe.py --exe $nmsExe --type-name ".?AVcGcMatchmakingPlayfabSteam@@" --max-slots 96
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x24B8F0 --size 0x25
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x22B230 --size 0xDE
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x36A410 --size 0x8
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x24B920
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x24B920 --size 0x40
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x22BF00 --size 0x110
    & $py -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4AAA358 --slot-count 87 --offset 0x1A0 --offset 0x1A8 --offset 0x1B0 --access write
    & $py -B tools/native_data_offset_xrefs.py --exe $nmsExe --offset 0x1A0 --access write --limit-per-offset 100
    & $py -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0xAD5A90 --context 12 --limit-per-target 30
    & $py -B tools/native_branch_xrefs.py --exe $nmsExe --target-rva 0xAD5A90 --limit-per-target 30
    & $py -B tools/native_absolute_pointer_xrefs.py --exe $nmsExe --target-rva 0xAD5A90 --limit-per-target 30
    & $py -B tools/native_rva_data_xrefs.py --exe $nmsExe --target-rva 0xAD5A90 --limit-per-target 30
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x497648
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x497648
    & $py -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x48FA60 --context 12 --limit-per-target 50
    & $py -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x48FA60 --max-slots 96
    & $py -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x48FA60 --max-slots 96
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x4906BD
    & $py -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x495640 --context 12 --limit-per-target 30
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x4955F8
    & $py -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x495560 --context 12 --limit-per-target 30
    & $py -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x495560 --max-slots 96
    & $py -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x495640 --max-slots 96

A one-off query used the incomplete RTTI selector .?AVPlayfabSession@cGcMatchmaking@@ and found no locator; the correct selector is .?AVPlayfabSession@cGcMatchmakingPlayfab@@, already validated in the earlier same-hash report. A grouped PowerShell invocation also failed before scanning because single quotes split the executable path at the apostrophe in No Man's Sky; subsequent commands used a double-quoted variable. Both errors are TOOL ERROR/query misses, not binary negatives.

Tool SHA-256: native_function_disasm.py 26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0; native_pdata_function_group.py fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26; native_rtti_vtable_probe.py 4e60908321b4f2aef2d314dff8f7cc6c00e62252683434ff6482758beee50028; native_call_xrefs.py 7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf; native_rip_xrefs.py e9592776047326d362547caecc5b1c27c3f3e9e09f50705b2a2b65ee30f6b0f1; native_branch_xrefs.py fa8dbc157e094f8c793a29e46afa0946059f69ad7070218e6d72452d9914034e; native_absolute_pointer_xrefs.py 5e6f37d2dedf74b5691c537b4e1f19908926dd76062686eecb5a14e516bc5f46; native_rva_data_xrefs.py c1b88b6910dad1ff0d2ef556a2c94c58b94f04e0b06b20253cdd561f94ce123d; native_vtable_member_xrefs.py e621c1062b52e08a3cd8f3ab2f9844e8e8be78487d08d998a60ac840ef482cbc; native_data_offset_xrefs.py 5d3f80c87679dcf6dd41bde71f027628eb6af24fc6ee06ecf32924e63fac34b8. Tools ran with CPython 3.11.9 (SHA-256 5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec), pefile 2024.8.26 and Capstone 5.0.7.

No native source, compatibility-profile or package mapping changed. No tests, build, package, push or live game operation occurred. The 7.06 profile remains fail-closed.

Next bounded action: locate the invocation or registration route for 0xAD5A90 using a new evidence source; otherwise map an alternative exact owner-proven positive writer for the manager's session array. Then prove the +0x41C key producer and local/network semantics without transferring the 7.05 parameter names. Only after these gates close should source-port and release gates resume; the remaining QAM row/label/resource and live behavior gates still block a 7.06 release.

### Player-state receiver chain and load-hook policy, 22 October 2026

The official [Hello Games release log](https://www.nomanssky.com/release-log/)
still lists Cosmos 7.06 first and has no 7.07 entry. The current [Nexus files
page](https://www.nexusmods.com/nomanssky/mods/4579?tab=files) still lists file
49469 / package `0.10.2-native-test`; the listed compatibility text remains
Windows/Steam build 25624745 (Cosmos 7.05) only. The 7.06 profile remains
unsupported.

#### Receiver identity closure

The named NMS.py signature `cGcPlayerState::LoadFromData` still has zero
matches in the exact 7.06 executable. The separate caller-anchored candidate
`0x573500` now has a stronger receiver proof: every one of its four direct
`.pdata`-bounded call instructions passes the same constructed
`cGcPlayerState` object at `application+0xB940`.

The application constructor path is `0x2C6E20 -> 0x2CEA60`. It passes
`application+0xE70` to `0x2CEA60`; that initializer passes
`application+0xE70+0xAAD0` to `0x572410`. The pinned NMS.py
`cGcPlayerState::cGcPlayerState` signature uniquely matches `0x572410`, so the
constructed receiver is `application+0xB940`. A separate no-`.pdata` getter at
`0x2D7A50` loads the application pointer from global RVA `0x6E8D708`, adds
`0xE70`, and returns that subobject. The death-state call at `0x2E088F` uses
the returned pointer plus `0xAAD0`, matching the constructed object.

The other paths now resolve to that same receiver. Root `0x307367` calls
`0x4886E0` at `0x307D53` and `0x307E1B`; both set `RCX=*(application global)`
then add `0xE70`. Root `0x4886E0` saves its incoming `RCX` in `RDI` and calls
`0x48E400` with it. Root `0x48E400` saves `RCX` in `RSI`; its two calls to
`0x495560` pass `RCX=RSI`. Root `0x32F385` also calls `0x495560` at
`0x32F794` and `0x32FC2C` with `RCX=application+0xE70`. Correction to the
earlier caveat: at `0x32FC2C`, `lea rbx,[rcx+0x20]` changes `RBX` for a later
`R8D` read but leaves `RCX` unchanged. It does not pass `application+0xE90`
as the first argument.

The remaining direct chain is `0x495560 -> 0x495640 -> 0x48FA60 -> 0x573500`.
The single direct caller of `0x495640` is `0x4955F8`; the single direct caller
of `0x48FA60` is `0x497648`, which passes the saved `RCX` in `R12`. Thus its
`0x4906BD` call also uses `RCX=application+0xE70+0xAAD0`. A batched exact-hash
direct-call scan decoded 52,110,272 `.pdata` bytes with zero skipped ranges
and confirmed four direct `0x573500` callsites. This proves the receiver for
the discovered direct calls; it does not exclude other indirect calls or
establish that this is a safe global hook point. The RTTI probe found zero
validated vtable slots targeting `0x573500`; the constructor/receiver chain is
the positive owner evidence.

#### Input semantics and source-policy blocker

At `0x4906BD`, the fourth register input comes from
`application+0x4BE6A0`, which is set from the session-linked predicate in the
`0x495560` path. The candidate body saves incoming `R9B` but overwrites the
home slot at `0x576407` before a direct input read or address escape. Do not
call this input `network_client`. The fifth stack byte is read at `0x578B2F`;
zero enters helper `0x6019F0`, which clears several state fields, while nonzero
skips that helper. The four callsites pass `1`, a byte in `DIL`, a byte in
`R13B`, and `0`, respectively. This is a proven branch effect, not a proven
source parameter name. The sixth stack slot is also reused before its original
value is read.

Most importantly, one direct call is inside the uniquely pattern-matched
`cGcApplicationDeathState::Update` root. It passes `R9D=0` and fifth argument
`1`. The current `native/src/bootstrap.cpp` load hook calls `beforeLoad()` and
then `afterLoad(common, network, result)` around every target invocation;
the runtime callback does not receive or filter the fifth argument. If this
death-state call returns true, the current non-network path would treat it as
a successful local save load and can create a summon opportunity. That
conflicts with the repository rule that death/respawn must remain a separate,
verified trigger. Do not add `0x573500` to the profile until a caller-specific
local-save completion boundary or an independently verified exclusion is
found. The old source names `network_client` and `resetting` cannot safely be
carried forward by argument position.

The pinned NMS.py data file contains 370 records. Its raw-LF copy has SHA-256
`14FF4F02D732E31A83885E3ED38A9304900A45D96297A3BA95DA720ED87A8832`; the
CRLF form has SHA-256
`F311C9F54C0CCE199AB955A0E8DE2CFE2FCFB09274E557A2A27908C1B15BAF5F`. Both
parse to the same records from pinned commit
`b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`; the hash difference is line
endings, not a provider revision. This provider has no named Matchmaking or
PlayfabSession function patterns. Absence is a provider-coverage gap, not proof
that those routines are absent.

Reproduce from the repository root with the same verified executable and
pinned provider copy:

```powershell
$py = $python
$nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
$provider = '<pinned NMS.py data.json copy>'
& $py -B tools/native_signature_matches.py --exe $nmsExe --data-json $provider --name 'cGcPlayerState::cGcPlayerState' --name 'cGcPlayerState::SaveToData' --name 'cGcPlayerState::LoadFromData'
& $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2D7A50 --size 0x100
& $py -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x573500 --target-rva 0x495560 --target-rva 0x495640 --target-rva 0x48FA60 --target-rva 0x48E400 --target-rva 0x4886E0 --context 8 --limit-per-target 20
& $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x32F385 --size 0x930 | Select-String -Pattern '0x32f794:|0x32fc2c:' -Context 12,12
& $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x495560 --size 0x100
& $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x495640 --size 0x23A0 | Select-String -Pattern '0x497648:' -Context 24,18
& $py -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x573500 --max-slots 128
& $py -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0xAD5A90 --max-slots 160
```

These commands used CPython 3.11.9 (SHA-256
`5F7B89A612C9B8AF1D6456CDFCD1DBE5CA630849E79AEBCED9BEE9A6694952EC`),
pefile 2024.8.26 and Capstone 5.0.7. Tool SHA-256 values:
`native_signature_matches.py` `47A22766E2A26A02E86926891B5AC0F533AA9B881759968C358B36139988CF36`;
`native_function_disasm.py` `26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0`;
`native_call_xrefs.py` `7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`;
`native_rtti_vtable_probe.py` `4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028`.
The target executable SHA-256 is
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.

No native source, compatibility profile or package mapping changed. No tests,
build, package, push or live game operation occurred. Keep the 7.06 profile
fail-closed. Next bounded action: trace the success/transition boundary of the
`0x32F385` local-load path and distinguish it from the death-state and
`0x48E400` paths; only then choose a local-only hook point or retain the current
unsupported guard. Do not repeat broad `+0x41C` scans. The QAM custom-row,
resource/render consumer and live behavior gates still block a release.

### Local-load state-machine follow-up, 22 October 2026

The next bounded pass found a narrower completion candidate than the generic
player-state function, but did not close the local-save-versus-respawn gate.
The exact executable remains Cosmos 7.06 / Steam build `25732212`, file
version `180836`, size `88,560,712`, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.

RTTI identifies vftable `0x4A50A30` as
`cGcApplicationLocalLoadState`; slot 3 is root `0x32EF50`, whose chained
`.pdata` ranges include the full Update body through `0x3317CF`. In that body,
`RSI` is the state object. Its 32-bit member at `+0x62C` is read by a switch
with 22 cases (0 through 21) and written during state transitions. The jump
table at RVA `0x331DF0` resolves to these case targets:

```text
00:32F39A 01:32FD85 02:32FDFA 03:32FF04 04:32FF33 05:32FF9C
06:32FFFC 07:33022E 08:33025C 09:3303DF 10:33056B 11:3305EF
12:3306C4 13:3309E1 14:330A8B 15:330CC8 16:330D91 17:330F49
18:330FFF 19:331066 20:3310C0 21:3311F0
```

The helper at `0x33E1C0`, called nine times directly from this Update body,
returns the next numeric state for inputs 0 through 20, returns 23 for input
21, and returns 0 for inputs above 21. Case 21 begins at `0x3311F0`; after its
final state work, the body writes zero to `[RSI+0x62C]` at `0x3317C0`. This is
a candidate finalization/reset boundary in `cGcApplicationLocalLoadState`, not
proof that a user save has completed or that death/respawn is excluded.

The two local Update calls into `0x495560` at `0x32F794` and `0x32FC2C` do not
use the returned `AL` as an observed completion condition. At `0x32F794`, the
call receives `RCX=application+0xE70`, `EDX=[application+0x318974]` and
`R8D=0xFFFFFFFE`; the next instruction writes zero to
`[application+0x318970]`. At `0x32FC2C`, it receives the same `RCX`, `EDX=0`
and `R8D=[application+0xE90+0xAA60]`; the code then clears `EDX`, calls
`0x5D6260` with `RCX=application+0xE90`, and does not test the prior `AL`.
Therefore these `0x495560` calls remain false leads as local-load completion
signals. The earlier `0x5805D0` lead is also still rejected as a boundary: its
body computes spatial/planet state and has one direct caller from this Update.

The state object also stores a 32-bit value at `+0x620` returned by the
uniquely pattern-matched `cGcApplicationLocalLoadState::GetRespawnReason` at
`0x331FB0`. Its pinned provider mangled name returns the typed enum
`cGcPlayerRespawn::RespawnReason`; the 370-record provider contains no
enumerator names. The complete method returns several integer codes (including
0, 1, 2, 3, 4, 9-13, 16-18) based on state flags and global game state; Update
forwards or tests the value, including a direct comparison to 2 at `0x3307C9`.
The field is a computed enum value, not a Boolean. Numeric-to-enumerator and
user-save-versus-death mappings remain unknown. The older 7.05 runtime
observations of reason values are not transferred to this executable.

An owner-bounded scan against RTTI-validated LocalLoadState vftable
`0x4A50A30` checked five `.pdata` method roots (six slots had no `.pdata`) and
found 30 operands for `+0x62C`, including the reads and writes above. The same
scan against GlobalLoadState vftable `0x4A50970` checked four roots (seven
slots had no `.pdata`) and found zero `+0x62C` operands. This is a bounded
owner-method result only; it does not exclude aliases or other callers.

One one-off jump-table parse initially subtracted the image base from each
32-bit table entry and produced invalid negative RVAs. That output was
discarded before interpretation. The instruction sequence adds the image base
to the zero-extended 32-bit table values; re-reading them as unsigned RVAs
produced the 22 destinations above. This was an analysis-script/decode error,
not a game-binary negative result.

Reproduce the bounded checks from the repository root:

```powershell
$py = $python
$nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
& $py -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A50A30 --slot-count 11 --offset 0x62c --access any
& $py -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A50A30 --slot-count 11 --offset 0x620 --access any
& $py -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A50970 --slot-count 11 --offset 0x62c --access any
& $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x33E1C0 --size 0x180
& $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x331FB0 --size 0x260
& $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x32F730 --size 0x90
& $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x32FBF0 --size 0x100
& $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x3311F0 --size 0x5DF
& $py -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x33E1C0 --context 5 --limit-per-target 30
$script = @'
import sys, struct, pefile
pe = pefile.PE(sys.argv[1], fast_load=True)
data = pe.get_data(0x331DF0, 0x16 * 4)
for i in range(0x16):
    print(f'case {i:02d}: RVA 0x{struct.unpack_from("<I", data, i * 4)[0]:06X}')
'@
$script | & $py -B - $nmsExe
```

The runs used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7. Tool
SHA-256: `native_vtable_member_xrefs.py`
`E621C1062B52E08A3CD8F3AB2F9844E8E8BE78487D08D998A60AC840EF482CBC`;
`native_function_disasm.py`
`26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0`;
`native_call_xrefs.py`
`7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`;
`native_rtti_vtable_probe.py`
`4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028`.

The 7.06 profile and native source remain unchanged. No tests, build, package,
push or live game operation occurred. Keep the exact-build profile fail-closed.
Next bounded action: establish which exact `GetRespawnReason` code and state-21
transition correspond to a completed user save load, and prove that the same
path cannot be produced by death/respawn. Until then, do not hook state 21 or
promote `0x573500`. The QAM custom-row, label/resource and live behavior gates
also remain open.

### Relocated respawn-position helper and case-8 argument proof, 22 October 2026

This pass advances the experimental respawn-observer mapping but does not establish a safe 7.06 trigger. The target remains Windows x64 Steam Cosmos 7.06, build 25732212, file version 180836, size 88,560,712, SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499. Source HEAD remains f7d97b61fcf152677d0d30de34f6c1b48675c436; the active profile remains 7.05/build 25624745.

The old experimental observer target 0x14F7F60 is invalid in this executable. It lies inside the instruction beginning at 0x14F7F5A, in a chained unwind range belonging to root 0x14F7F40, and an exact .pdata-bounded E8 scan found zero direct calls to 0x14F7F60. Do not shift this address mechanically or install a hook there.

The strongest replacement candidate for the old player/ship positioning helper is the exact .pdata root 0x14F9E20-0x14FC07A. It has 11 direct callers. The old body length 0x225A matches the new body length 0x225A; its PLAYER_RESPAWN string reference moves from 0x14FA051 to 0x14FBF11, and the DoPlayerRespawn reference resolves from the local-load path at 0x3302BB. Internal player and ship positioning calls also move consistently: old 0x14F9242 -> 0x1500410 and 0x14F9267 -> 0x1500ED0 correspond to new 0x14FB102 -> 0x15022D0 and 0x14FB127 -> 0x1502D90. These independent anchors strongly support the same helper role after relocation; they do not prove byte identity or safe hook semantics.

| Old local-load call / return | 7.06 call / return | 7.06 third argument |
| --- | --- | --- |
| 0x3302BF / 0x3302C4 | 0x33030F / 0x330314 | 1 on switch case 8 |
| 0x33066A / 0x33066F | 0x3306BA / 0x3306BF | 0 |
| 0x330941 / 0x330946 | 0x330991 / 0x330996 | 0 |

The three 7.05 return RVAs are not valid 7.06 instruction boundaries: 0x3302C4 is inside the instruction at 0x3302C2, 0x33066F is inside the store at 0x33066D, and 0x330946 is inside the instruction at 0x330943. The three new returns above follow the exact five-byte E8 calls and are instruction boundaries. Other direct callers of the shared helper include two calls in the death-state root at 0x2E0A24 and 0x2E10C2, plus six calls in other roots. In particular, the 0x2E0A24 death-state call passes R8B=1. The helper is shared; a global detour without a verified caller filter would mix lifecycle paths.

Correction to the preceding unresolved note: the 0x33030F call does receive third argument 1 on its actual switch-case-8 path. The RTTI-validated LocalLoadState Update at root 0x32F385 initializes R12D to 1 at 0x32F36F, then dispatches through the +0x62C switch table; case 8 targets 0x33025C. That case reaches the merged block at 0x3302BB and call 0x33030F without writing R12. At 0x3302FE it executes movzx r8d,r12b, so R8D is 1 for this case. The nearby 0x330030-0x3300DD block does use R12 as a counter, but that is a separate control-flow path and is not a predecessor of case 8. The prior concern conflated these paths. This proves the static argument for this callsite only; it does not name the argument or identify the respawn event.

At 0x33030F, EDX comes from the 32-bit field [RSI+0x620], populated at 0x3302DC by GetRespawnReason at 0x331FB0. The pinned provider types this as cGcPlayerRespawn::RespawnReason, but enumerator names and the mapping to user save, teleport, death or network events remain unknown. Do not carry the 7.05 runtime observation reason=11 into this build as a verified enum meaning. The other two LocalLoadState calls pass third argument zero.

Two analysis corrections belong in the reusable playbook. First, native_branch_xrefs.py reports only direct immediate JMP instructions; its zero result for 0x3302BB did not find the conditional branch at 0x330276 (jne 0x3302BB). Use root-aligned disassembly or a CFG that includes conditional branches; never interpret this tool's zero as no branch. Second, one PowerShell wrapper initially placed the executable path containing the apostrophe in No Man's Sky inside single quotes and exited before either scanner produced output. That invocation is not binary evidence; assigning the path with a double-quoted PowerShell string corrected it.

Reproduce the exact-build checks from the repository root:

    $py = $python
    $nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x14F7F60
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x14F9E20
    & $py -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x14F7F60 --context 5 --limit-per-target 100
    & $py -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x14F9E20 --context 5 --limit-per-target 100
    & $py -B tools/native_string_xrefs.py --exe $nmsExe --contains DoPlayerRespawn --contains PLAYER_RESPAWN
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x330030 --size 0x180
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x3301A7 --size 0x200
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x32EF50 --size 0x2900 | Select-String -Pattern '0x1403302bb'

A diagnostic invocation of native_branch_xrefs.py with targets 0x3302BB, 0x3302FE and 0x33030F returned zero direct-JMP references; that output is incomplete for conditional branches and must not be used as a path-exclusion result. The correct disassembly above shows the conditional 0x330276 -> 0x3302BB edge.

Environment: CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7. Tool SHA-256: native_call_xrefs.py 7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF; native_pdata_function_group.py FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26; native_function_disasm.py 26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0; native_string_xrefs.py 08E81155608CC6A5F235EF5B6C8D95243EAC38DE99D947C5628A90D109E267C8; native_branch_xrefs.py FA8DBC157E094F8C793A29E46AFA0946059F69AD7070218E6D72452D9914034E.

No source, profile or package mapping changed. No tests, build, package, push or live game operation occurred. Keep 7.06 fail-closed. Next bounded action: derive which GetRespawnReason outputs reach the LocalLoadState case-8 positioning call and establish whether this path is exclusive to the intended local event; compare it with the two death-state calls. Then resume the independent QAM custom-row/resource-render gates.

### Respawn-reason output conditions and LocalLoadState field writes, 22 October 2026

A new bounded pass disassembled the complete cGcApplicationLocalLoadState::GetRespawnReason body at 0x331FB0 and scanned exact member writes in the RTTI-validated LocalLoadState vtable 0x4A50A30 (11 slots, five .pdata-backed roots, six slots without .pdata). The 32-bit result stored at state+0x620 is computed from several LocalLoadState bytes and application/global state; it is not a single event flag.

The exact method body returns one of 0, 1, 2, 3, 4, 9, 10, 11, 12, 13, 16, 17 or 18. The enumerator names are absent from the pinned provider. A useful static condition is that return 11 is selected when application+0x72B068 is nonzero and application+0x72B5A4 is 1 or 14, after earlier guards in the same method. The application pointer is loaded from the already mapped global RVA 0x6E8D708. This condition may guide a future exact-build observation, but it does not identify the game event represented by 1, 14 or reason 11.

The owner-bounded write scan found:
- +0x624: one byte clear at 0x333A75 in RTTI vtable slot 5 root 0x333A60.
- +0x625: one byte computed at 0x32EC6A inside the seven-range chained group rooted at 0x32EAD0 (slot 2), plus a 16-bit clear of +0x625/+0x626 at 0x333AE2 in slot 5.
- +0x626: one byte computed at 0x32EC8F from application+0x7328CB and application+0x72B5A4==5; it is cleared with +0x625 at 0x333AE2.
- +0x627: one byte clear at 0x333AF0 in slot 5.
- +0x628: one dword clear at 0x333ADC in slot 5. A second apparent +0x628 write at 0x3323D4 is to [RBP+0x628], a stack local, and is a base-object false positive.

The slot-2 method stores its receiver from RCX in RDI at 0x32EAE2, so the writes through RDI in its chained range are tied to the LocalLoadState object. The slot-5 method similarly stores RCX in RDI at 0x333A72 before its clears. These findings map exact widths, directions and owner-method bases; they do not prove that the fields have only these writers outside the bounded RTTI method set or establish a reason enum name.

A filtered virtual-call scan is a false lead for invoking the slot-2 setter. Slot offset 0x10 plus same-range +0x625 matched only call 0x32EE1C inside the setter's own range; at that instruction RCX was prepared from another object at 0x905B30, not the LocalLoadState receiver in RDI. A matching member displacement elsewhere in a function does not make every virtual call in that function a dispatch on the same object. Slot offset 0x28 plus same-range +0x624 produced zero candidates, which is only a filter result and not evidence that slot 5 is never invoked. Direct E8 scans of roots 0x32EAD0 and 0x333A60 also returned zero; both are vtable methods, so direct-call scans are not the invocation path.

Reproduce the exact-build checks from the repository root:

    $py = $python
    $nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x331FB0 --size 0x260
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x32EAD0 --size 0x273
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x333A60 --size 0xA6
    & $py -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A50A30 --slot-count 11 --offset 0x624 --access write
    & $py -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A50A30 --slot-count 11 --offset 0x625 --access write
    & $py -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A50A30 --slot-count 11 --offset 0x627 --access write
    & $py -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A50A30 --slot-count 11 --offset 0x628 --access write
    & $py -B tools/native_vcall_xrefs.py --exe $nmsExe --slot-offset 0x10 --require-field 0x625 --context 6 --limit-per-range 5
    & $py -B tools/native_vcall_xrefs.py --exe $nmsExe --slot-offset 0x28 --require-field 0x624 --context 6 --limit-per-range 5
    & $py -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x32EAD0 --target-rva 0x333A60 --context 5 --limit-per-target 30

Tool SHA-256: native_vtable_member_xrefs.py E621C1062B52E08A3CD8F3AB2F9844E8E8BE78487D08D998A60AC840EF482CBC; native_vcall_xrefs.py 24A792FCE464FD6639A3DE92923FCD31BC1BBBB6427ACB0B866FC97308174621; native_function_disasm.py 26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0; native_call_xrefs.py 7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF. Environment remains CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7.

No source/profile/package mapping changed and no tests, build, package, push or live game operation occurred. Keep 7.06 fail-closed. Next bounded action: anchor the LocalLoadState object's state-manager vtable invocation for slots 2 and 5, then derive which field values can reach the case-8 GetRespawnReason call. The local-save/death meaning remains unresolved; QAM custom-row and resource-render gates also remain open.

### QAM builder argument contract and LocalLoadState receiver-filter follow-up, 22 October 2026

This pass closes the static argument-shape question for the existing two-argument QAM builder hook, while leaving row identity/rendering and all live behavior gates open. The exact executable remains Cosmos 7.06 / Steam build 25732212, file version 180836, size 88,560,712, SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.

RTTI confirms 0x15286C0 as slot 0 of cGcQuickActionMenu vftable 0x4A504E0. Its update root saves incoming R8 in R15, then at 0x1528893 sets RDX=R15 and RCX=RDI before calling builder root 0x152A1C0. The builder has one chained .pdata range (0x152A1C0-0x152B394, chained 0x152B394-0x152E6D1). It saves incoming RCX and RDX; before any use of incoming R8, it calls stack helper 0x1433E2ED0, after which R8 is volatile. The later observed R8 use at 0x152A226 follows an explicit mov r8d,0x2d. This supports the current source wrapper shape builderHook(menu, render) and builder_original(menu, render) for this call path; it proves only that the builder does not consume its incoming third register value before clobber/overwrite, not the native type or semantic owner of RDX.

The source behavior is also bounded: MenuAdapter::beforeBuilder at native/src/menu.cpp:391-401 validates the second pointer for a one-byte readable range and stores its numeric address. afterBuilder at lines 430-446 compares pointer identity and does not dereference it. Thus the pointer's native type is not required for this source wrapper's current behavior. This does not prove that the QAM menu itself is safe or that custom rows, icons, labels, or resources render correctly. The existing source target RVA remains the 7.05 value; no 7.06 profile or source mapping was changed.

The LocalLoadState invocation attempt remains unresolved. RTTI vtable 0x4A50A30 is assigned through global storage RVA 0x6E8EA40 by initialization root 0x32BC90; the exact RIP-relative scan found only the address passed at 0x32BD7F and the vtable store at 0x32BDC8. A raw preferred-base pointer scan for the vtable returned zero, which does not cover relative or dynamically formed references. A filtered slot-2 scan (slot offset 0x10, same-range field +0x62C) returned one call at 0x331B36, inside the chained LocalLoadState Update root 0x32EF50. At that call, RCX is loaded from the application global at 0x6E8D708 and adjusted by +0x905B20; the nearby [RSI+0x62C] belongs to a different register chain. No evidence ties the dispatch receiver to the LocalLoadState object or its slot-2 setter, so reject it as proof of that invocation. The slot-5 scan (0x28, same-range +0x62C) returned zero matching ranges; that is only a filter result, not proof that slot 5 is never invoked.

The first batched scanner invocation returned progress only because its session output was not polled to completion. It was not recorded as a zero; the scans were rerun with session polling and only their complete final totals above are used. This is a tool-orchestration correction, not binary evidence.

Reproduce the QAM ABI checks from the repository root:

    $py = $python
    $nmsExe = "C:/Program Files (x86)/Steam/steamapps/common/No Man's Sky/Binaries/NMS.exe"
    & $py -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x15286C0 --max-slots 32
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x152A1C0
    & $py -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x152A1C0 --context 8 --limit-per-target 50
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x15286C0 --size 0x250
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x152A1C0 --size 0x90

Reproduce the LocalLoadState receiver checks:

    & $py -B tools/native_rip_xrefs.py --exe $nmsExe --target-rva 0x4A50A30 --limit-per-target 30
    & $py -B tools/native_absolute_pointer_xrefs.py --exe $nmsExe --target-rva 0x4A50A30 --limit-per-target 30
    & $py -B tools/native_rip_xrefs.py --exe $nmsExe --target-rva 0x6E8EA40 --target-rva 0x6E8D708 --limit-per-target 100
    & $py -B tools/native_vcall_xrefs.py --exe $nmsExe --slot-offset 0x10 --require-field 0x62c --context 8 --limit-per-range 12
    & $py -B tools/native_vcall_xrefs.py --exe $nmsExe --slot-offset 0x28 --require-field 0x62c --context 8 --limit-per-range 12
    & $py -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x331AF2
    & $py -B tools/native_function_disasm.py --exe $nmsExe --rva 0x331AF2 --size 0x90

Tool SHA-256 values: native_rtti_vtable_probe.py 4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028; native_pdata_function_group.py FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26; native_call_xrefs.py 7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF; native_function_disasm.py 26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0; native_rip_xrefs.py E9592776047326D362547CAECC5B1C27C3F3E9E09F50705B2A2B65EE30F6B0F1; native_absolute_pointer_xrefs.py 5E6F37D2DEDF74B5691C537B4E1F19908926DD76062686EECB5A14E516BC5F46; native_vcall_xrefs.py 24A792FCE464FD6639A3DE92923FCD31BC1BBBB6427ACB0B866FC97308174621. Environment: CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7.

No native source, profile, package mapping, tests, build, package, push or live game operation changed. Keep 7.06 disabled. Next bounded action: trace the appended QAM item from helper 0x143D5D0 through its vector/consumer path and identify a real icon-rendering read, while keeping the still-unresolved LocalLoadState dispatch and local-save-versus-death distinction as separate release gates.

### Notice vector owner, insertion and cleanup mapping, 22 October 2026

The 7.06 notice context and count are now statically mapped. Native caller root `0x3BD626-0x3BD9CC` loads the application pointer from global RVA `0x6E8D708` into `RBX` at `0x3BD872`, then passes `app+0x847BB0` as `RCX` to `AddTimedMessage` candidate `0x9BF7B0` at `0x3BD8EB`. That candidate reads a 32-bit count at context `+0x28C`, capacity at `+0x288`, and data pointer at `+0x290`. It checks the last record's text at record `+0x80`; a match updates the float at record `+0x2E0`, otherwise it creates and appends a record with stride `0x2F0`.

The only decoded direct caller of insertion helper `0x9D8790` is `0x9BF968`. It receives the vector header at context `+0x288`, record data pointer in `R8`, and a pointer to the temporary record in the fifth stack slot. The helper uses header dword `+0` as capacity and dword `+4` as count, increments count on the in-capacity path, and sets the incremented count after its reallocation path. The caller stores the returned data pointer back at context `+0x290`. Cleanup root `0x8A49A0` independently loads the same application global, reads count at `app+0x847E3C` and pointer at `app+0x847E40`, processes the `count*0x2F0` span, then clears the 32-bit count. This is static field/setter/consumer/clear evidence; it does not establish runtime lifetime, thread, or visible delivery.

The source check in `native/src/runtime.cpp:461` correctly rejects `count > 3` like the native method. Its float check `!(value < 0)` is not identical for NaN: the native `COMISS` followed by `JAE` skips nonnegative values but continues for unordered input, whereas the source check returns on unordered input. A write-only `native_data_offset_xrefs.py` scan found zero direct writes to displacement `0x4BF50C` in all 52,110,272 decoded `.pdata` bytes, with zero skipped ranges. This bounded negative does not exclude writes through helper arguments, aliases, copies, or non-`.pdata` initialization; keep the producer, meaning and runtime range `PARTIAL` and do not claim the predicates are fully equivalent.

Reproduce from the repository root with CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7 and the exact `NMS.exe` SHA-256 above:

    $nmsExe = "C:/Program Files (x86)/Steam/steamapps/common/No Man's Sky/Binaries/NMS.exe"
    python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x9D8790
    python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x9D8790 --size 0x1C7
    python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x9D8790 --context 12 --limit-per-target 10
    python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x9BF7B0 --size 0x230
    python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x3BD626 --size 0x3A6
    python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x8A49A0 --size 0x170
    python -B tools/native_data_offset_xrefs.py --exe $nmsExe --offset 0x4BF50C --access write --limit-per-offset 50

Tool SHA-256: `native_pdata_function_group.py` `FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26`; `native_function_disasm.py` `26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0`; `native_call_xrefs.py` `7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`; `native_data_offset_xrefs.py` `5D3F80C87679DCF6DD41BDE71F027628EB6AF24FC6EE06ECF32924E63FAC34B8`.

No native source, profile, package mapping, build, package, push or live game operation changed. Keep 7.06 disabled. Next: resolve the `app+0x4BF50C` producer/comparison contract, then continue the independent QAM rendering and local-save-versus-death gates.

### Application state-manager identity and local-load/death separation, 22 October 2026

This pass maps the exact Cosmos 7.06 application state manager and a static discriminator for the death-state call. The executable identity remains Steam build `25732212`, file version `180836`, size `88,560,712`, SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.

RTTI validates `cGcApplication` vftable `0x4A50888` and its `cTkFSM` base vftable `0x4A50850`. `cTkFSM::AddStates` root `0x2BE0080` stores the descriptor-table pointer at manager `+0x08`, clears the current-state pointer at `+0x10`, and walks 24-byte descriptors. For each row it forms `state = manager + descriptor.offset`, copies the 16-byte state key to `state+0x08`, stores the manager pointer at `state+0x18`, clears `state+0x20`, and invokes state slot `+0x08`. The `APPLOCALLOAD` descriptor is row `+0x48` in table RVA `0x5092200`, with state offset `+0x1370`; the corresponding object is RVA `0x6E8EA40` and has the RTTI-validated `cGcApplicationLocalLoadState` vftable `0x4A50A30` (Update slot 3, root `0x32EF50`).

`cTkFSM::Update` root `0x2BE4F60` is RTTI-confirmed slot 2 of both vftables. It resolves a pending key first, then loads the current state from manager `+0x10` and calls its vtable slot `+0x18`. Application Update root `0x2D7580` calls it at `0x2D7777` with `RCX` pointing to the static `cGcApplication` object at RVA `0x6E8D6D0`. The transition resolver `0x2BE4B00` sets the manager's current pointer at `+0x10` when applying a request. Therefore the exact state identity candidate is `current == moduleBase+0x6E8EA40`, read from `moduleBase+0x6E8D6E0`. This static object must not be confused with the adjacent application pointer cell at RVA `0x6E8D708` used by other subsystems.

The request helper `0x2BE4BD0` was scanned across all `52,110,272` decoded `.pdata` bytes with zero skipped ranges and has nine direct E8 callers. The sole direct caller that requests the `APPLOCALLOAD` key is selector Update root `0x306FD0`, at `0x3083C2`; its alternate key is `APPGLOBALLOAD`. DeathState Update root `0x2DBBB0` requests `APPVIEW` at `0x2E1AA9`, while its load-candidate call at `0x2E088F` is in the same chained root group. Since requests are pending until the next `cTkFSM::Update`, a death-state load call remains under the DeathState current pointer during that call.

The candidate local path is statically connected: LocalLoadState Update root `0x32F385` calls `0x495560` at `0x32F794` and `0x32FC2C`; `0x495560` calls `0x495640` at `0x4955F8`; the chained `0x495640` group calls root `0x48FA60` at `0x497648`; and `0x48FA60` calls load candidate `0x573500` at `0x4906BD`. The full `.pdata` direct-call scan found one caller of `0x48FA60` and the four previously recorded direct callers of `0x573500`, including the DeathState call. This makes a current-state identity check a promising static way to distinguish that death path from the local-load path. It does not prove live callback timing, thread, repeat behavior, or that every possible indirect invocation is covered.

The raw preferred-base pointer scan for `0x2BE4BD0` found zero literal pointers in seven non-`.reloc` sections. This is only a bounded pointer-form result; relative tables, dynamically formed addresses and indirect dispatch remain outside that scan. The direct-call scan is complete only for decoded `.pdata` E8 calls, not every possible reference form.

One invocation using `py -3.11` failed before analysis with `No installed Python found!`; it is a `TOOL ERROR`, not binary evidence. Rerunning with the explicitly verified CPython 3.11.9 executable completed. Environment: CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7.

Reproduce from the repository root against the exact executable hash above:

```text
$python = "<verified CPython 3.11.9 executable>"
$nmsExe = "<verified Cosmos 7.06 NMS.exe>"
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2BE0080 --size 0x250
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2BE4B00 --size 0x1A0
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2BE4F60 --size 0x100
& $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x2BE4F60 --max-slots 8
& $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x2BE4BD0 --context 10 --limit-per-target 100
& $python -B tools/native_absolute_pointer_xrefs.py --exe $nmsExe --target-rva 0x2BE4BD0 --limit-per-target 20
& $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x48FA60 --target-rva 0x495560 --target-rva 0x495640 --target-rva 0x573500 --context 8 --limit-per-target 20
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x495560 --size 0x220
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x495640 --size 0x220
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x3083C2
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x2E1AA9
```

Tool SHA-256: `native_function_disasm.py` `26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0`; `native_pdata_function_group.py` `FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26`; `native_call_xrefs.py` `7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`; `native_rtti_vtable_probe.py` `4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028`; `native_absolute_pointer_xrefs.py` `5E6F37D2DEDF74B5691C537B4E1F19908926DD76062686EECB5A14E516BC5F46`.

No source, profile or package mapping changed; no tests, build, package, push or live game operation occurred. Keep the active 7.05 profile unchanged and 7.06 disabled. Next bounded action: map the existing native callback's access to module-relative state identity and successful-load return, then decide whether that exact guard can be implemented without changing the 7.05 path. Runtime confirmation, QAM custom-row/resource rendering and the notice-float producer remain open release gates.

### Existing load callback versus the 7.06 state gate, 22 October 2026

The current source wrapper at `native/src/bootstrap.cpp:244` treats physical `R9` as `network`, calls `Runtime::beforeLoad(network)`, forwards all six arguments to the original, then calls `Runtime::afterLoad(common, network, result)` after return. `Runtime::afterLoad` at `native/src/runtime.cpp:140` accepts only `network == false`, a true native result and a non-null common-state pointer; it then reads an eight-byte ID at `common+0x8980` and arms the existing load-pending flow. The current hook RVA remains the verified 7.05 value `0x572C40`.

This confirms why merely moving the hook to 7.06 candidate `0x573500` is unsafe. Its DeathState caller at `0x2E088F` supplies `R9D=0`; if the unchanged wrapper sees a successful result, it would classify that death-path load as a local save load. The state-manager evidence above offers a static filter: run the load callbacks only while `*(moduleBase+0x6E8D6E0) == moduleBase+0x6E8EA40`, while always forwarding the original native arguments unchanged. However, the 7.06 `R9B` at local caller `0x4906BD` is derived from the session byte at `+0x4BE6A0`; its local/network meaning remains unproven. Do not silently replace or reinterpret this input, and do not change the active 7.05 callback.

This closes the source-to-callback impact analysis and strengthens the known death exclusion, but not the native session flag semantics, exact callback timing/thread, runtime event behavior, other native dependency gates or 7.06 live verification. No source/profile/package mapping changed; no tests, build, package, push or live game operation occurred. Keep 7.06 fail-closed. Next bounded action: trace the QAM appended item from constructor/helper `0x143D5D0` through the registered vector and identify an exact label/icon consumer, without repeating already mapped builder ABI work.

### QAM appended-row label consumer and icon-render boundary, 22 October 2026

Rechecked the exact target executable: Steam Cosmos 7.06 build 25732212, file version 180836, size 88,560,712, SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499. CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7. The current public Nexus file remains 0.10.2-native-test / file 49469, uploaded 3 October; its compatibility text still names Windows/Steam build 25624745 / Cosmos 7.05 only. The Hello Games release log still lists Cosmos 7.06 as newest on 22 October, with no 7.07 entry. No public 7.06-compatible mod package was found.

The RTTI query using undecorated cGcQuickActionMenu returned zero validated locators. This was a query-name mismatch, not missing RTTI: rerunning with exact decorated name .?AVcGcQuickActionMenu@@ found one validated CompleteObjectLocator at 0x4B66FE0, vftable 0x4A504E0, and 16 slots. Slot 9 is label method 0x153C0C0; slot 0 is Update 0x15286C0. An RTTI name inventory for QuickMenu returned only the decorated cGcQuickMenuState base and an unrelated template lambda; a standalone base vtable was not established.

The label method's full chained .pdata group is 0x153C0C0-0x153C0FD, 0x153C0FD-0x153C24C, and 0x153C24C-0x153C5E4. A complete direct-call scan of 0x153C0C0 decoded all 52,110,272 .pdata bytes with zero skipped ranges and found one E8 caller: 0x1529288 in root 0x15288D6. At that call, RCX=RDI is the QAM receiver, RDX=R15 is the label output buffer, and R8=R15+0x100 is an opaque output argument that the existing hook forwards unchanged.

Root-aligned disassembly shows the native label method reads selected depth at QAM+0xA050, selected index at QAM+0xA088+depth*4, vector count at [QAM+0xA058+depth*0x10]+4, and selected row from [QAM+0xA060+depth*0x10] + index*0xE0. It then reads the selected row's action at row+4; the two specialized action comparisons are 0x16 and 0x17. This proves a selected 0xE0 row from the registered QAM vectors reaches the label path. The mod's afterLabel hook runs after the native function and overwrites the text only for its marker-identified custom row. The custom row's own action is initialized as zero; native pet actions 46/47 are the observed trigger for inserting the custom parent/child rows.

This label proof does not establish the icon path. The method does not read the first dword at row+0, where the constructor stores the icon/resource handle. The generic quick-menu renderer or another exact consumer of that field remains unresolved; custom-row visibility and resource readiness therefore remain PARTIAL.

A broad native_data_offset_xrefs.py read query for +0xA058/+0xA060 emitted progress but its final summary was not captured. Discard it as NOT CHECKED, not a zero, and do not repeat the same broad displacement scan. Continue from the proven QAM object and renderer call path. The short RTTI query, corrected decorated-name query, and full QAM slot-9 consumer trace are reproducible below:

    & $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --type-name cGcQuickActionMenu --max-slots 16
    & $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --type-name '.?AVcGcQuickActionMenu@@' --max-slots 16
    & $python -B tools/native_rtti_name_inventory.py --exe $nmsExe --contains QuickMenu --limit 100
    & $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x153C0C0
    & $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x153C0C0 --context 8 --limit-per-target 50
    & $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x153C0C0 --size 0x3D
    & $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x153C0FD --size 0x14F
    & $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x153C24C --size 0x398

Tool SHA-256: native_rtti_name_inventory.py 253259913FC3AE0F4E7D011E0B56E45CEB3AA88CC2EECAA90B0617B7A86DCCBC; native_rtti_vtable_probe.py 4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028; native_pdata_function_group.py FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26; native_call_xrefs.py 7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF; native_function_disasm.py 26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0.

Git HEAD for this pass: f7d97b61fcf152677d0d30de34f6c1b48675c436. The pre-existing working tree had changes before this doc-only pass; native/src/menu.cpp was unmodified. No native/profile mapping changed; no tests, build, package, push or live game operation occurred. Keep 7.05 active and 7.06 disabled. Next bounded action: trace the selected QAM vector from the proven object into the generic quick-menu draw/resource consumer and identify a root-aligned read of the first item dword; preserve the NOT CHECKED scan and do not reuse the broad displacement query. Load callback semantics, notice-float production, custom-row/resource rendering and all live behavior gates still block a 7.06 release.
### QAM vtable-bound member scan and rejected generic dispatch candidates, 22 October 2026

The exact-build RTTI-vtable scan used the validated cGcQuickActionMenu vftable 0x4A504E0, 16 slots, and found seven slot methods with .pdata groups; nine slot methods had no .pdata entry and are outside the method-body negative. The bounded method-member scan returned zero direct reads of object offsets +0xA058 and +0xA104. For +0xA060 it found seven reads: five in QAM Update slot 0, one in label slot 9, and one in confirmation slot 6. The result supports the known vector data flow and shows that the scanned QAM virtual methods do not directly read the icon handle at item +0. It does not exclude a non-virtual method, a generic caller, an alias, a dynamic offset or code outside these RTTI method groups. Keep the icon renderer gate open.

A direct RIP-relative read scan of vftable 0x4A504E0 found one code reference, at 0x2CA6EC in root 0x2CA6D0. Root-aligned disassembly shows that this constructor stores that vftable at [this]. A full .pdata direct-call scan found its sole direct caller at 0x2CA3FE in cGcQuickMenu constructor root 0x2CA290, passing the nested QAM subobject at parent+0xDC0. The prior constructor chain maps the enclosing QAM object to owner+0x116B10. Querying RTTI for decorated type .?AVcGcQuickMenu@@ returned no standalone locator; do not infer that the validated child QAM RTTI is missing.

A complete slot-zero ABI-shape scan decoded 52,110,272 .pdata bytes, zero skipped ranges, 1,415 runtime ranges and 2,063 indirect calls; 36 had the narrow RDX/R8 setup shape. The inspected near-address candidates at 0x2C075EC and 0x2C077C0 are 16-byte stream/compression routines: they parse stream headers, compare the Zstd marker 0x5A737464 and call stream operations. Reject these as quick-menu render or QAM Update callers. This ABI-shape list is a lead generator, not receiver proof. Do not repeat it without a new object-proven constraint.

One call-xref invocation used context 14, outside the tool's supported 0-12 range, and failed before scanning. Rerunning with context 12 completed and found one direct constructor caller. The invalid invocation is a TOOL ERROR, not binary evidence.

Reproduce the bounded class scan and construction path against the exact executable:

    & $python -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A504E0 --slot-count 16 --offset 0xA058 --access read
    & $python -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A504E0 --slot-count 16 --offset 0xA060 --access read
    & $python -B tools/native_vtable_member_xrefs.py --exe $nmsExe --vtable-rva 0x4A504E0 --slot-count 16 --offset 0xA104 --access read
    & $python -B tools/native_rip_xrefs.py --exe $nmsExe --target-rva 0x4A504E0 --limit-per-target 100 --access read
    & $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x2CA6D0 --context 12 --limit-per-target 20
    & $python -B tools/native_vcall_abi_candidates.py --exe $nmsExe --slot-offset 0x0 --limit 200

Tool SHA-256: native_vtable_member_xrefs.py E621C1062B52E08A3CD8F3AB2F9844E8E8BE78487D08D998A60AC840EF482CBC; native_rip_xrefs.py E9592776047326D362547CAECC5B1C27C3F3E9E09F50705B2A2B65EE30F6B0F1; native_call_xrefs.py 7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF; native_vcall_abi_candidates.py 7B5184FC14C2314AB8A561838519AA3EAFA35DF2AC68977527BB135EFBA92944.

No source or profile mapping changed. No test, build, package, push or live game operation occurred. Keep 7.05 active and 7.06 disabled. Next bounded action: use the owner-proven QAM subobject and its actual update/render-state caller to locate the generic row renderer, then confirm a first-dword icon read. Keep unsupported external-consumer paths explicitly open; do not repeat the generic slot-zero candidate scan.

### Chained QAM dispatch and source-row resource path, 22 October 2026

The exact executable identity remains Steam build 25732212 / Cosmos 7.06, file version 180836, size 88,560,712, SHA-256 `13D5060D4EFB9D2A6A6B1B349BC4257231056CC2A055DF4BB15D816262CC3499`. The exact decorated RTTI result remains `cGcQuickActionMenu` vftable `0x4A504E0`, 16 slots. A new `tools/native_embedded_vcall_xrefs.py` scanner tracks an embedded-object candidate from `lea owner+offset` through a vptr load to an indirect slot call within one `.pdata` range. Scanning offsets `0xDC0` and `0x116B10` decoded all 52,110,272 runtime-function bytes, skipped zero ranges, and returned three candidate dispatches. Comparing the slot offsets with the validated QAM vtable confirms these calls:

- `0x15409C9`, QAM slot 3 (`0x18`), from `RDI+0xDC0`; slot 3 targets `0x1530CD0`, a short selection/depth reset method.
- `0x1540FF9`, QAM slot 15 (`0x78`), from `R15+0xDC0`; slot 15 targets `0x152A0E0`, which accepts only action index 4 and then checks QAM state through `0x152A100`.
- `0x1541CF9`, QAM slot 14 (`0x70`), from `R15+0xDC0`; slot 14 targets `0x153DDF0`, a short state/global predicate.

These are real QAM dispatches, but none is the icon renderer. A full `.pdata` slot-zero scan was restricted to the 17 ranges in the chained group rooted at `0x1540CF0`; it found no slot-zero dispatch in that group. Separately, a complete direct-E8 scan of `0x15286C0` found zero direct callers. Since `0x15286C0` is QAM vtable slot 0, the direct-call zero is expected for a virtual target and is not an absence claim. The embedded-object scanner currently resets register provenance at each `.pdata` range; it cannot prove or reject dataflow that crosses chained ranges.

The same 17-range group contains a separate, positive source-row resource path. In its chained range `0x15419CF-0x1542B37`, the routine reads a row count from `[R13+0x614]` and a row pointer from `[R13+0x618]`, then indexes rows with stride `0xE0`. It checks the first dword at `0x1541F18`; at `0x1542038` it passes that dword in `R8D` to `0x2E16E20`. That helper hashes the integer key and searches/creates a resource-cache entry. The returned value is then passed to `0x6DE4F0` at `0x154204D`, which writes the value into UI-object fields. This establishes resource resolution for records in the `R13+0x618` source vector.

It does not yet establish that `R13+0x618` aliases any QAM-owned depth vector at `menu+0xA058` / item pointer `menu+0xA060`, or that it contains the rows appended by `MenuAdapter::afterBuilder`. Keep this as a positive generic-row lead, not proof that the custom row's icon is rendered. The QAM builder copies rows from its opaque third-argument object, while the source code appends custom rows into the QAM-owned vector; their exact relationship to this renderer's source vector remains unverified.

The initial detail-mode prototype of the embedded-call scanner was interrupted before producing a final summary and is `NOT CHECKED`; no counts from that attempt are used. The completed scanner uses `disasm_lite`, reports progress, and is intentionally limited to same-range register tracking. Two disassembler invocations also passed image VAs instead of RVAs (`0x142E16E20` and `0x1406DE4F0`) and failed before analysis; corrected RVAs `0x2E16E20` and `0x6DE4F0` produced the results above. Do not report these tool errors as zero references.

Reproduce the new full-image scan and the exact caller/render evidence against the executable hash above:

```text
$python = "<verified CPython 3.11.9 executable>"
$nmsExe = "<verified Cosmos 7.06 NMS.exe>"
& $python -B tools/native_embedded_vcall_xrefs.py --exe $nmsExe --object-offset 0xDC0 --object-offset 0x116B10 --context 10
& $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --type-name '.?AVcGcQuickActionMenu@@' --max-slots 16
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x1541CF9
& $python -B tools/native_vcall_xrefs.py --exe $nmsExe --slot-offset 0x0 --context 8 --limit-per-range 10
& $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x15286C0 --context 8 --limit-per-target 20
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1541F00 --size 0x180
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2E16E20 --size 0x140
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x6DE4F0 --size 0x140
```

The slot-zero output was filtered to the 17 ranges returned for root `0x1540CF0`: `0x1540CF0-0x1540D45`, `0x1540D45-0x1540D5D`, `0x1540D5D-0x1540DA9`, `0x1540DA9-0x1540E1B`, `0x1540E1B-0x15413C2`, `0x15413C2-0x15419CF`, `0x15419CF-0x1542B37`, `0x1542B37-0x1543057`, `0x1543057-0x1543144`, `0x1543144-0x15432B9`, `0x15432B9-0x15432D7`, `0x15432D7-0x154332C`, `0x154332C-0x15434EA`, `0x15434EA-0x1543584`, `0x1543584-0x15435F8`, `0x15435F8-0x1543775`, and `0x1543775-0x1543802`.

Tool SHA-256: `native_embedded_vcall_xrefs.py` `451B96B8D606AD7BC07153BD95204418225BE67FC98AE2096EECDBA8D7C58BCE`; `native_vcall_xrefs.py` `24A792FCE464FD6639A3DE92923FCD31BC1BBBB6427ACB0B866FC97308174621`; `native_rtti_vtable_probe.py` `4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028`; `native_pdata_function_group.py` `FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26`; `native_call_xrefs.py` `7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`; `native_function_disasm.py` `26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0`. Environment: CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7.

No source, compatibility profile, package mapping, tests, build, package, push or live game operation changed. Keep 7.05 active and 7.06 disabled. `NOT CHECKED`: identity/aliasing between `R13+0x618` and the QAM-owned vectors, the actual custom-row render callback, the notice-float producer, the local-save versus death callback semantics, and all 7.06 live behavior. Next bounded action: prove whether the builder's third-argument row owner and this resource consumer share the same exact base/pointer, then follow one custom row through that consumer or reject the path with root-aligned evidence. Do not repeat the offset-only or generic ABI searches.

### Computed frontend source-vector owner and resource consumer, 22 October 2026

The exact target remains Steam build `25732212` / Cosmos `7.06`, file version `180836`, size `88,560,712`, SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. Analysis ran with CPython `3.11.9`, pefile `2024.8.26`, and Capstone `5.0.7`.

The `R13+0x618` path is now anchored to its actual parent object. Root `0x1540CF0` has one decoded direct caller, `0x920721`. That caller loads the application pointer from global RVA `0x6E8D708`, adds `0x848670`, and passes the resulting object in `RCX`; `RDX` is `RSI+0x20E68`. The root saves `RCX` in `R15`, sets `RDI=RCX+0x10`, and computes `R13=RDI+sign_extend(*(int32*)(R15+4))*0x6D0`. The chained range then reads source count from `[R13+0x614]` and source pointer from `[R13+0x618]`, indexes `0xE0`-byte rows, and reads the first dword at `0x1541F18`. At `0x1542038` it passes that dword as a resource key to `0x2E16E20`; at `0x154204D` the resolved value is passed to `0x6DE4F0` for a UI-object field update. This is positive evidence of an icon/resource consumer for the computed per-entry source vector.

Root 0x1540CF0 contains two constructor/vtable-validated embedded QAM dispatches from R15+0xDC0 (slots 15 and 14); its complete 17-range chained group contains no slot-zero dispatch. The slot-3 dispatch at 0x15409C9 is in a separate five-range group rooted at 0x1540430. The constructor-chain pass below proves that both roots address the same cGcQuickMenu parent and the same embedded QAM. This co-location does not prove that the computed R13+0x618 vector aliases the QAM depth vectors at menu+0xA058/+0xA060, that its rows are the custom rows appended by MenuAdapter::afterBuilder, or that the resource key is rendered as an icon. Treat the generic row consumer as a stronger lead, not custom-row proof. A separate RTTI probe for root 0x1540CF0 found no validated vtable slot targeting that function; the direct E8 caller above is the usable anchor, and the RTTI zero is not an absence claim.

One first invocation referred to `$py` and `$nmsExe` without defining them in that PowerShell process; it failed before opening the executable and is a `TOOL ERROR`, not a scan result. Corrected commands used the verified CPython executable and explicit executable path. Reproduce against the hash above:

```text
# $python is the verified interpreter resolved during preflight.
$nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
& $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x1540CF0 --context 8 --limit-per-target 20
& $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x1540CF0 --max-slots 80
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x920655 --size 0x180
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1540CF0 --size 0x220
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1540CF0 --size 0x2B12 | Select-String -Pattern 'r13' | ForEach-Object { $_.Line }
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1541E30 --size 0x260
```

Tool SHA-256: `native_call_xrefs.py` `7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`; `native_rtti_vtable_probe.py` `4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028`; `native_function_disasm.py` `26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0`.

No native source, compatibility profile, package mapping, tests, build, package, push or live game operation changed. Keep 7.05 active and 7.06 disabled. Next bounded action: connect the QAM Update third argument to this exact computed source-vector owner through a caller or constructor path; do not repeat same-offset or generic ABI scans. Local-save/death semantics, notice-float production, custom-row rendering/resource lifetime and live 7.06 behavior remain release gates.

### QAM slot-zero caller search and generic-list false lead, 22 October 2026

The target remains the exact Cosmos 7.06 Steam executable, build `25732212`, file version `180836`, size `88,560,712`, SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. Analysis used CPython `3.11.9`, pefile `2024.8.26`, and Capstone `5.0.7`.

The exact decorated RTTI probe validates function `0x15286C0` as slot zero of `.?AVcGcQuickActionMenu@@` at vftable RVA `0x4A504E0`. The direct-E8 scan reports zero calls to `0x15286C0`, which is expected for a virtual target and does not search indirect dispatches. The previous same-range candidate scan requiring offset `0xDC0` and slot zero had a classification flaw: when a register held a loaded method pointer, an indirect memory call could inherit the old virtual slot instead of using the method pointer state. The helper was corrected to keep objects, vptrs, and loaded function pointers distinct and to apply the vtable displacement only to a tracked vptr. The correction narrows candidate classification; it does not add cross-`.pdata` register provenance.

Completed corrected full-image scans against the exact hash:

- Owner offset `0xDC0`, slot byte offset `0`: decoded `52,110,272` runtime-function bytes, skipped `0`, found `3` overall candidate dispatches and `0` filtered slot-zero dispatches. The three are the already established QAM slots 3, 14 and 15.
- Owner offset `0x10`, slot byte offset `0`: decoded `52,110,272` bytes, skipped `0`, found `264` overall candidate dispatches and `4` filtered slot-zero candidates. The candidates are `0x183DA4E`, `0x31AF0B2`, `0x31AF570`, and `0x31AF8DA`.

Candidate `0x183DA4E` is in the chained group rooted at `0x183DA00`. It loads an object from a dynamically indexed list entry at `rsi+0x10`, calls vtable slot zero and then slot one. The same root walks the list and then clears its count, data pointer and capacity fields; it also clears a related global field. A complete direct-E8 scan finds eight callers to this root. This is a generic list teardown/clear path. No RTTI or constructor evidence ties its element at `rsi+0x10` to the embedded QAM at `app+0x849430`, so it is rejected as a QAM Update caller.

The other three candidates are in roots around `0x31AF0B2`, `0x31AF570` and `0x31AF8DA`. They set `R8D` before a preceding virtual call, then do not write `R8` again before slot zero. Since `R8` is volatile under Win64, that earlier value cannot identify the third argument at slot zero. Their receivers also lack a QAM constructor/RTTI chain. These are rejected candidates, not caller proof. This scan has therefore not found the actual QAM Update caller or established the identity of its `R8` row-vector argument.

One corrected scan attempt failed before starting Python because the executable path containing `No Man's Sky` was enclosed in a single-quoted PowerShell string. The parser split the path before the binary opened; this is `TOOL ERROR`, not a zero result. The completed rerun defined `$nmsExe` using a double-quoted PowerShell string. Tool hashes: `native_embedded_vcall_xrefs.py` `CF0773881A2D6E2AE69B9DB4EBC43E62B1224120C5594C4DBAD8B0D7292541D4`; `native_call_xrefs.py` `7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`; `native_pdata_function_group.py` `FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26`; `native_rtti_vtable_probe.py` `4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028`.

Reproduce the completed scans and the two full-image direct-call queries from this repository in PowerShell:

```powershell
# $python is the verified interpreter resolved during preflight.
$nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
& $python -B tools/native_embedded_vcall_xrefs.py --exe $nmsExe --object-offset 0xDC0 --slot-offset 0 --context 12
& $python -B tools/native_embedded_vcall_xrefs.py --exe $nmsExe --object-offset 0x10 --slot-offset 0 --context 12
& $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x183DA00 --context 10 --limit-per-target 30
& $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x15286C0 --context 8 --limit-per-target 30
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x183DA4E
& $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x15286C0 --max-slots 24
```

The two long scans each require their final summary. Progress-only output is incomplete; record the attempt as `NOT CHECKED` and resume the same session until it finishes. The direct-call scanner reports `DIRECT_CALLS: 8` for `0x183DA00` and `DIRECT_CALLS: 0` for the virtual QAM target `0x15286C0`.

The dependency ledger remains at 67/85 `MAPPED`, 14 `PARTIAL`, and 4 `NOT CHECKED`; these are static source-mapping counts, not release readiness. No source/profile or package mapping changed. Keep Cosmos 7.05 active, 7.06 fail-closed/disabled, and do not publish. Next action: trace the constructor-proven QAM address `app+0x849430` with group-aware provenance through every indirect caller and record `RCX`, `RDX`, `R8`, and stack arguments at the exact dispatch. The row-vector alias, custom-row icon rendering, local-save/death semantics, notice-float producer and live 7.06 behavior remain release gates.

### Exact QAM address scan confirms only the state-selector slot, 22 October 2026

A completed full-image scan using candidate address offset `0x849430` decoded `52,110,272` runtime-function bytes and skipped zero ranges. It returned one indirect dispatch: call `0x14642C8` in root `0x1464200`, vtable byte offset `0x58` (slot 11), with the receiver formed as `RDX+0x849430`. Filtering the same query to slot zero returned zero. The direct disassembly in the earlier selector analysis shows this is the known menu-state selection path using the index at global+`0x849424`; slot `0x58` is not QAM Update at slot zero. This is a useful positive control for the exact object offset, but the scan remains per `.pdata` range and does not propagate a pointer into a different chained fragment or a callee that receives an already formed QAM pointer.

Reproduction against the exact hash with CPython `3.11.9`, pefile `2024.8.26`, and Capstone `5.0.7`:

```powershell
# $python is the verified interpreter resolved during preflight.
$nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
& $python -B tools/native_embedded_vcall_xrefs.py --exe $nmsExe --object-offset 0x849430 --context 12
& $python -B tools/native_embedded_vcall_xrefs.py --exe $nmsExe --object-offset 0x849430 --slot-offset 0 --context 12
```

Both runs completed with zero skipped ranges; the unfiltered run found exactly one candidate at `0x14642C8`, and the slot-zero filter returned zero. Tool SHA-256: `native_embedded_vcall_xrefs.py` `CF0773881A2D6E2AE69B9DB4EBC43E62B1224120C5594C4DBAD8B0D7292541D4`. Keep the QAM Update caller and row-vector owner `NOT CHECKED`; this exact-offset negative is bounded, not a global absence proof. Next: resolve caller and receiver provenance across chained groups and function-argument boundaries.

### Group-aware QAM search and argument-seeded caller shortlist, 22 October 2026

To check the remaining `.pdata` boundary gap, a group-aware scanner was added. It resolves `UNW_FLAG_CHAININFO` groups, follows decoded direct conditional/unconditional branches inside each group, tracks the exact virtual receiver in `RCX`, and does not carry volatile registers across calls. It is still a candidate tool: it does not propagate object identity from a caller into a separately called function, and a requested offset does not establish a class.

The first scanner version reported zero calls, but it also failed a positive control: its sequential CFG edge compared an instruction VA with an RVA. That zero is invalid. After fixing the VA-to-RVA conversion, the exact-offset scan reproduced four known calls across three groups: QAM slots 3 (`0x15409C9`), 11 (`0x14642C8`), 14 (`0x1541CF9`), and 15 (`0x1540FF9`). The positive controls pass; none is slot zero. The scan covered groups containing offsets `0xDC0`, `0x848670`, or `0x849430`, had no state-limit truncation, and confirmed the prior known QAM calls. It found no slot-zero candidate in these offset-derived paths.

Eight exception-directory ranges totalling 420 bytes yielded no Capstone instructions and are explicitly unclassified, not treated as proof of absence: `0x43BEAC-0x43BECC`, `0x624078-0x6240B4`, `0x11599DC-0x1159A08`, `0x15D202C-0x15D2064`, `0x198C954-0x198C9BC`, `0x19F68D8-0x19F68F0`, `0x318B318-0x318B344`, and `0x33A88F8-0x33A8930`. Their bytes look data-like, but their roles were not mapped. The corrected scan processed 115 groups containing the requested offsets, found four candidate dispatches, and had zero truncated groups.

The separate argument-seeded slot-zero pass found 83 generic virtual-call candidates in 71 function groups when treating each root's incoming `RCX` as a possible object. This is only a shortlist. A direct-E8 caller query for those 71 roots returned 179 callsite blocks. The QAM-related direct caller contexts were the two known calls at `0x335927` and `0x335992` to root `0x1540430`; both pass the cGcQuickMenu parent at `global+0x848670`, not its QAM child at `global+0x849430`. Root `0x1540430` later dispatches QAM slot 3 at `0x15409C9`; its slot-zero candidate at `0x15404FF` uses the parent receiver. This is not a QAM Update caller. Direct-E8 queries and 12-instruction contexts do not prove the absence of indirect callers, cached aliases, or a value set earlier than the printed context.

An attempt to read candidate output from a second PowerShell process failed because the sandbox assigned that process a different temporary directory. It failed before the caller scan ran and is `TOOL ERROR`, not a result. The completed caller pass generated the seed output and direct-call query in one PowerShell process, used a unique repository-local scratch file, split 71 targets into batches of at most 64, and removed the scratch files afterward.

Reproduce the corrected group-aware positive-control pass against the exact executable with CPython `3.11.9`, pefile `2024.8.26`, and Capstone `5.0.7`:

```powershell
# $python is the verified interpreter resolved during preflight.
$nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
& $python -B tools/native_group_embedded_vcall_xrefs.py --exe $nmsExe --object-offset 0xDC0 --object-offset 0x848670 --object-offset 0x849430 --context 8 --max-states-per-instruction 64
& $python -B tools/native_group_embedded_vcall_xrefs.py --exe $nmsExe --seed-object-register rcx --slot-offset 0 --context 0 --max-states-per-instruction 64 --max-results 120
```

The caller query used `native_call_xrefs.py --context 12 --limit-per-target 20` over the 71 unique `ROOT` values printed by the argument-seeded run, split into two target batches because the tool accepts at most 64 targets per pass. Exact hashes: `native_group_embedded_vcall_xrefs.py` `D83C9FACD87AB351ECC739C43C51E139EF9BC1218CE46D36047291C397064DEE`; `native_pdata_function_group.py` `FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26`; `native_call_xrefs.py` `7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`.

The row-vector owner and QAM Update caller remain `NOT CHECKED`; custom-row icon rendering remains `PARTIAL`. Static mapping remains 67/85 `MAPPED`, 14 `PARTIAL`, and 4 `NOT CHECKED`. Keep Cosmos 7.05 active and 7.06 fail-closed/disabled. No source/profile or package mapping changed. Next: continue from the function-pointer argument boundary by resolving which candidate roots can be reached indirectly with `RCX=app+0x849430` and the actual row pointer in `R8`; do not promote the parent receiver or a generic slot-zero match.

### Shared cGcQuickMenu parent and indexed source-vector relationship, 22 October 2026

Correction: this section's three-entry/index-2 interpretation is superseded by the two-record constructor audit below. The shared parent and QAM offset remain corroborated.

The constructor chain confirms that the two renderer/state roots operate on the same cGcQuickMenu object. The application global pointer cell is RVA 0x6E8D708. Its initializer calls root 0x2C6E20 with that pointer; this root forms app+0x732920 and calls 0x2C8EC0. Root 0x2C8EC0 forms app+0x848670 and calls cGcQuickMenu constructor 0x2CA290 with that address. The constructor initializes entries at this+0x10, this+0x6E0, and this+0xDB0 with stride 0x6D0, then constructs the QAM subobject at this+0xDC0. Thus this QAM is at app+0x849430.

Root 0x1540430 has two direct callers, 0x335927 and 0x335992; each passes the same app+0x848670 parent. Its QAM slot-3 call at 0x15409C9 is in a five-range chained group rooted at 0x1540430. Root 0x1540CF0 has the direct caller 0x920721, which also passes app+0x848670; its slot-15 and slot-14 calls use R15+0xDC0, the exact QAM subobject established by the constructor. This resolves parent and QAM identity across the constructor, state and resource-consumer paths.

The source vector is indexed separately: R13=(parent+0x10)+sign_extend(*(int32*)(parent+4))*0x6D0, then its count and pointer are read at +0x614/+0x618. The constructor establishes three candidate entry bases; when the index is 2, R13=parent+0xDB0 and the QAM is exactly R13+0x10. Static analysis does not establish that index 2 is active at the resource call, what parent+4 means at runtime, or that the QAM Update third argument is this R13 pointer. The source-vector header and QAM-owned depth-vector header at menu+0xA058/+0xA060 are distinct locations; no pointer alias or custom-row render has been proven.

A completed full .pdata scan of slot offset 0 requiring same-range fields 0xDC0 and 0x618 found zero matching ranges and zero indirect calls, across 52,110,272 decoded bytes with zero skipped ranges. Its first invocation printed progress but its final result was lost; that attempt is NOT CHECKED. The completed rerun is only a same-range displacement filter, not proof that no QAM Update call or alias exists.

Reproduce against the exact executable hash above:
    # $python is the verified interpreter resolved during preflight.
    $nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
    & $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x2C6E20 --context 10 --limit-per-target 20
    & $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x2C8EC0 --context 8 --limit-per-target 20
    & $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x2CA290 --context 10 --limit-per-target 20
    & $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x1540430 --context 8 --limit-per-target 20
    & $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x1540CF0 --context 8 --limit-per-target 20
    & $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x15409C9
    & $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2C6E20 --size 0x80
    & $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2CA290 --size 0x260
    & $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1540430 --size 0x284
    & $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x15406B4 --size 0x442
    & $python -B tools/native_vcall_xrefs.py --exe $nmsExe --slot-offset 0 --require-field 0xDC0 --require-field 0x618 --context 12 --limit-per-range 20

Tool SHA-256: native_call_xrefs.py 7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF; native_pdata_function_group.py FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26; native_function_disasm.py 26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0; native_vcall_xrefs.py 24A792FCE464FD6639A3DE92923FCD31BC1BBBB6427ACB0B866FC97308174621. Environment: CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7.

No source, compatibility profile, package mapping, tests, build, package, push or live game operation changed. Keep 7.05 active and 7.06 disabled. Next bounded action: trace the actual QAM Update caller's R8 input to this indexed entry and follow the copied/appended row into the consumer. Keep parent+4 runtime value, local-save/death semantics, notice-float production, custom-row rendering/resource lifetime and live 7.06 behavior open.

### RTTI classification of argument-seeded slot-zero candidates, 22 October 2026

The target executable remains Steam build `25732212`, Cosmos `7.06`, file version `180836`, size `88,560,712`, SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. The argument-seeded group scan produced 83 generic slot-zero dispatches in 71 unique function groups. Its roots were queried in batches of at most 64 with `native_absolute_pointer_xrefs.py --limit-per-target 10`, which searches literal preferred-image-base 64-bit pointers in non-relocation sections: 23 roots had at least one exact pointer reference; 48 had none.

The 23 referenced roots were then checked with the `find_target_vftables` RTTI validator from `native_rtti_vtable_probe.py`, with a maximum of 64 slots. Six roots produced seven validated vtable-slot associations:

| Root RVA | RTTI owner | Slot |
| --- | --- | ---: |
| `0x21BBC0` | `cGcNGuiSceneInfoTreeViewNodeData` | 2 |
| `0x2C51B0` | `cGcFadeNode`; `cGcFadeNodeBase` | 3 |
| `0x160E5B0` | `cGcAsteroidGrid`; `cGcVoxelAsteroidGrid` | 4 |
| `0x2DC7040` | `cTk2dLayer` | 17 |
| `0x2E37650` | `HgVocAlien` | 1 |
| `0x2E37690` | `HgVocAlienParams` | 4 |

The remaining 17 roots with raw pointer hits had no RTTI-validated slot within that probe bound. None of the six validated owners was `cGcQuickActionMenu`. These hits map the candidate function's vtable membership only; they do not prove that its incoming `RCX` is the QAM at the internal call. The 48 zero raw-pointer results and 17 zero RTTI results are bounded to literal preferred-base pointers and the 64-slot validator; they do not rule out relative tables, relocated/cached values, or dynamic calls.

Reproducible commands/parameters against the exact executable:

```powershell
# $python is the verified interpreter resolved during preflight.
$nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
& $python -B tools/native_group_embedded_vcall_xrefs.py --exe $nmsExe --seed-object-register rcx --slot-offset 0 --context 0 --max-states-per-instruction 64 --max-results 120
# Extract/deduplicate its 71 ROOT RVAs and pass them to native_absolute_pointer_xrefs.py in batches of at most 64.
# RTTI CLI equivalents for the six validated roots:
& $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x21BBC0 --max-slots 64
& $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x2C51B0 --max-slots 64
& $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x160E5B0 --max-slots 64
& $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x2DC7040 --max-slots 64
& $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x2E37650 --max-slots 64
& $python -B tools/native_rtti_vtable_probe.py --exe $nmsExe --target-rva 0x2E37690 --max-slots 64
```

Tool SHA-256: `native_group_embedded_vcall_xrefs.py` `D83C9FACD87AB351ECC739C43C51E139EF9BC1218CE46D36047291C397064DEE`; `native_absolute_pointer_xrefs.py` `5E6F37D2DEDF74B5691C537B4E1F19908926DD76062686EECB5A14E516BC5F46`; `native_rtti_vtable_probe.py` `4E60908321B4F2AEF2D314DFF8F7CC6C00E62252683434FF6482758BEEE50028`. Environment: CPython `3.11.9`, pefile `2024.8.26`, Capstone `5.0.7`.

This reduces generic false leads but does not find the QAM Update caller or row-vector alias. Static coverage remains 67/85 `MAPPED`, 14 `PARTIAL`, 4 `NOT CHECKED`; these counts are not release readiness. Keep Cosmos 7.05 active, 7.06 fail-closed/disabled, and do not publish. No source/profile/package mapping changed. Next: trace the exact QAM pointer and row-owner argument across caller boundaries; do not repeat the unrestricted argument-seeded scan without a new receiver constraint.

### Latest public build check and stride-filtered slot-zero follow-up, 22 October 2026

The installed `NMS.exe` still has file version `180836`, size `88,560,712`, and SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. Hello Games' [Cosmos 7.06 announcement](https://www.nomanssky.com/2026/10/cosmos-7-06/) dates the public patch to 5 October 2026. SteamDB's [public branch record](https://steamdb.info/app/275850/depots/) still reports build `25732212`, updated 5 October. No later public patch/build was found in this check. The local executable hash matches the exact build identity used throughout this report.

The generic `+0x10` slot-zero scan produced seven truncated groups. To bound follow-up analysis, `native_group_embedded_vcall_xrefs.py` gained a repeatable `--require-immediate` filter that runs dataflow only for function groups containing the selected numeric immediate outside memory operands. A positive-control pass with `--object-offset 0xDC0 --require-immediate 0x6D0` processed all `52,109,852` runtime-function bytes, found 62 groups containing the immediate, and had zero truncated groups. It reproduced QAM parent candidates: slot `0x18` at `0x15409C9` (root `0x1540430`), slot `0x78` at `0x1540FF9`, and slot `0x70` at `0x1541CF9` (both root `0x1540CF0`). This is a scanner positive control, not proof that the immediate itself identifies a quick-menu entry.

The filtered target pass `--object-offset 0x10 --slot-offset 0 --require-immediate 0x6D0` again processed all `52,109,852` bytes and found 62 groups containing the immediate. Twenty-three groups acquired an offset/argument seed; seven truncated, and there were zero candidate dispatches. The seven truncated roots/ranges were `0x42BCA0` (`0x42BCA0-0x42C1AE`), `0x7BB1E0` (`0x7BB1E0-0x7BB4AE`), `0x982BE0` (`0x982BE0-0x982FEA`), `0xA0C110` (`0xA0C110-0xA0C2F5`), `0xA71C40` (`0xA71C40-0xA71EE2`), `0x134B760` (`0x134B760-0x134B8D0`), and `0x13F65B0` (`0x13F65B0-0x13F6A03`). Disassembly showed six contain `sub rsp, 0x6D0`, a stack-frame allocation rather than a menu stride. Root `0x982BE0` does contain `add r14, 0x6D0` in a loop initializing eight repeated subrecords; its class and relationship to QAM are unproven. These are filter false leads or unresolved groups, not evidence that the QAM slot-zero call is absent. The target pass also reported the same eight undecoded ranges totalling 420 bytes, which remain unclassified.

This experiment narrows the work, but closes no compatibility dependency. It demonstrates why a constant-only group filter is too broad: the same number can be a stack size, a loop stride in another class, or a menu stride. Next use the constructor-proven owner/index expression and instruction/dataflow role, inspect the remaining bounded roots individually, and keep the QAM caller/row-owner gate `NOT CHECKED` until the exact receiver and arguments are proven.

Reproduce with the exact binary:

```powershell
# $python is the verified interpreter resolved during preflight.
$nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
& $python -B tools/native_group_embedded_vcall_xrefs.py --exe $nmsExe --object-offset 0xDC0 --require-immediate 0x6D0 --context 10 --max-states-per-instruction 64 --max-results 150
& $python -B tools/native_group_embedded_vcall_xrefs.py --exe $nmsExe --object-offset 0x10 --slot-offset 0 --require-immediate 0x6D0 --context 12 --max-states-per-instruction 64 --max-results 150
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x42BCA0 --size 0x50E
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x7BB1E0 --size 0x2CE
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x982BE0 --size 0x40A
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0xA0C110 --size 0x1E5
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0xA71C40 --size 0x2A2
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x134B760 --size 0x170
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x13F65B0 --size 0x453
```

The `py -3.11` launcher returned `No installed Python found!` before reading the executable. This is an environment/tool-launch error, not a zero-match result. `Get-Command python` resolved to CPython `3.11.9`; imports reported pefile `2024.8.26` and Capstone `5.0.7`, so the scans used that explicit interpreter. Interpreter SHA-256: `5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec`. Updated scanner SHA-256: `1e322dd25379789d6f60d461d53b9778dc4020d90d2993d560f16ca52f8bac1e`.

Tool SHA-256: `native_group_embedded_vcall_xrefs.py` `1e322dd25379789d6f60d461d53b9778dc4020d90d2993d560f16ca52f8bac1e`; `native_function_disasm.py` `26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`; `native_pdata_function_group.py` `fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26`. Static mapping remains 67/85 `MAPPED` (78.8%), 14 `PARTIAL`, 4 `NOT CHECKED`; this follow-up added evidence but closed zero dependencies. The source and `native_compatibility.json` were not changed. Cosmos 7.05 remains active and 7.06 remains disabled. No build, package, tests, push, publication, or live game operation was performed.
### Indexed quick-menu helpers and global QAM guard, 22 October 2026

The exact 17-range group rooted at `0x1540CF0` confirms that `0x6D0` is a real selected-entry stride in this path, rather than the stack-size false leads. It forms an indexed entry from the `cGcQuickMenu` parent and reads its `+0x614/+0x618` vector fields. Its direct helper at `0x2C36D0` only writes zero to the dword at `RCX`; its helper at `0x2C3740` sets or clears a bit in the dword array at `RCX`, using `EDX` as the bit index and `R8B` as set/clear. The callsites pass selected-entry fields around `+0x6C4` and `+0x6D4`. This maps menu state helpers, not a QAM Update dispatch. The complete `0x1540CF0` group still has QAM slots 14 and 15 and no slot-zero dispatch.

The separate five-range group rooted at `0x1464200` reads the active menu selector from application offset `+0x849424`. In the selector branch for the QAM, it forms `RCX=application+0x849430`, loads that object's vtable, and calls slot `0x58` (slot 11) at `0x14642C8`. This is a concrete QAM callsite, but it is a guarded slot-11 query, not slot-zero Update. It narrows the QAM caller search without closing it.

Reproduce with `native_pdata_function_group.py` and `native_function_disasm.py` using ranges and commands immediately above. Their SHA-256 values are `fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26` and `26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0` respectively.

The owner/helper evidence is limited to this exact executable and static register/control-flow analysis. Runtime selector values, update timing, and the custom-row consumer remain `NOT CHECKED`. No source or profile mapping changed; 7.05 remains active and 7.06 disabled.
Reproduce the indexed-menu helper and QAM guard evidence with the exact executable:

```powershell
# $python is the verified interpreter resolved during preflight.
$nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x1540CF0
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1540CF0 --size 0x2B12 | Select-String -Pattern '0x6d0|0x614|0x618' -Context 10,10
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2C36D0 --size 0x100
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2C3740 --size 0x100
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x146427F
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1464200 --size 0x45C
```
### Direct-call check for the RTTI-mapped QAM Update method, 22 October 2026

A full decoded `.pdata` E8-style direct-call scan of the QAM slot-zero Update target `0x15286C0` processed `52,110,272` bytes, skipped zero ranges, and found zero direct calls. This rules out only decoded direct `call rel32` references in the scanned ranges. The known vtable slot-zero method can still be called indirectly; the QAM caller gate remains `NOT CHECKED` and 7.06 stays disabled.

```powershell
# $python is the verified interpreter resolved during preflight.
$nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
& $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x15286C0 --context 12 --limit-per-target 40
```

`native_call_xrefs.py` SHA-256: `7eb4ca84d93d7a64d7d754ea9ec1d60e488f63f0f581a0c031486940385fbfaf`. The result is not a negative for virtual calls, cached method pointers, or dynamic call targets. Static coverage remains 67/85 `MAPPED`, 14 `PARTIAL`, 4 `NOT CHECKED`; no dependency or release gate closed.

### Corrected nested QAM Update dispatch, 22 October 2026

The previous argument-seeded interpretation of slot-zero call `0x15404FF` was wrong: it treated the root's incoming `RCX` as the nested call receiver because the scan lost an offset loaded into a register. A complete root-aligned decode shows `RDI=RCX` at entry; `R15D=[RDI+0xDB4]`; selector value 1 loads `EAX=0xDC0`; `RSI=RDI+RAX`; then `RCX=RSI`, `RAX=[RSI]`, `R8=RDI+sign_extend(*(int32*)RDI)*0x6D0+0x10`, and `call [RAX]` dispatches slot zero at `0x15404FF`. This is a nested QAM receiver, not the parent receiver passed to the root.

Caller root `0x335827` contains the two direct calls to `0x1540430`. Both pass `RCX=application+0x848670`. The first, `0x335927`, is guarded by selector `application+0x849424 == 2`, so it selects another menu subobject. The second, `0x335992`, runs when that selector is not 2 and the adjacent state is at least `0xB`; its selector-1 path enters the QAM branch above. The established cGcQuickMenu constructor at `0x2CA290` places the QAM at `parent+0xDC0=application+0x849430`. RTTI validates QAM vftable `0x4A504E0`; slot 0 points to `0x15286C0`.

At `0x15286C0`, the prologue saves incoming `R8`, copies it to `R15`, and uses that pointer at `+0x268`, `+0x26C` and `+0x620`; it also passes it onward in `RDX` to QAM update/render helpers. This confirms that the caller supplies a record/context pointer. It does not prove that this pointer aliases the separate resource-source entry computed from `parent+0x10+sign_extend(*(int32*)(parent+4))*0x6D0`, nor QAM-owned vectors at `menu+0xA058/+0xA060`. The `parent+0` and `parent+4` index fields must remain distinct until a producer or runtime observation proves their relationship. `RDX`/`R9` and stack-argument roles at the nested dispatch remain unresolved; the visible caller does not establish them.

The prior full-image `+0x10` slot-zero pass was not a valid negative for this call: it did not propagate the register-held `0xDC0` through `lea RSI,[RDI+RAX]`, and seven unrelated candidate groups had truncated dataflow. The corrected targeted root scan below reports the exact `parent+0xDC0` object, with zero skipped/truncated ranges for the selected group. This closes the static QAM Update caller subgate, not the source-vector alias or any live/release gate.

Reproduce against the exact local executable (Steam build `25732212`, Cosmos `7.06`, file version `180836`, size `88,560,712`, SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`):

```powershell
# $python is the verified interpreter resolved during preflight.
$nmsExe = "C:\Program Files (x86)\Steam\steamapps\common\No Man's Sky\Binaries\NMS.exe"
& $python -B tools/native_group_embedded_vcall_xrefs.py --exe $nmsExe --object-offset 0x10 --object-offset 0xDC0 --seed-object-register rcx --index-field-offset 0 --index-field-offset 0x4 --index-stride 0x6D0 --slot-offset 0 --require-immediate 0x6D0 --root-rva 0x1540430 --context 12 --max-states-per-instruction 64 --max-results 30
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1540430 --size 0x110
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x335827 --size 0x2D4
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x15286C0 --size 0x216
```

The group-aware scan processed the selected 2,234-byte root group, found one slot-zero dispatch at `0x15404FF` with object expression `parent+0xDC0`, and reported zero skipped ranges and zero state-limit truncations. The same root-aligned disassembly reproduced QAM slot 3 at `0x15409C9`. Tools: `native_group_embedded_vcall_xrefs.py` SHA-256 `73d6c7e5b3c8f7c703f177526c6614e7090eb0d6446583ebfd5b33627c2834cd`; `native_function_disasm.py` `26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`; `native_pdata_function_group.py` `fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26`. Environment: CPython `3.11.9` (interpreter SHA-256 `5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec`), pefile `2024.8.26`, Capstone `5.0.7`.

The QAM caller is now statically corroborated. The data-field ledger remains `67/85 MAPPED`, `14 PARTIAL`, `4 NOT CHECKED` (78.8% static mapping coverage); this is not release readiness, and the denominator does not include nested call paths as separate source dependencies. No native source or `native_compatibility.json` mapping changed. 7.05 remains active; 7.06 remains disabled. No build, package, test, push, publication or live-game operation was performed. Next: prove or reject the relationship between the call's `R8` record pointer and the renderer/source vector, then continue the remaining static, local/network and live gates.

### Constructor correction, copied-row resource consumer and scanner audit, 22 October 2026

Inputs remain Cosmos 7.06 / Steam build `25732212`, executable size `88,560,712`, file version `180836`, SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`; source baseline `f7d97b61fcf152677d0d30de34f6c1b48675c436`, dirty compatibility branch `compat/cosmos-706-25732212`. This pass changes analysis tooling and documentation only. No external signature-provider pattern was used for these owner/dataflow checks.

**Constructor correction.** A complete `0x2CA290-0x2CA6CF` review establishes exactly two records, `parent+0x10` and `parent+0x6E0`, stride `0x6D0`. The loop counter starts at 2, the body advances the pointers, and the decrement/branch at `0x2CA3ED/0x2CA3F1` permits two iterations. The pointer ends at `parent+0xDB0`; this is not a third initialized record. The QAM is constructed separately at `parent+0xDC0`. The earlier three-entry/index-2 overlap interpretation is rejected. This constructor does not directly initialize the two 32-bit index fields at `parent+0/+4`; the bounded reset/close body `0x1540300-0x154042A` does not initialize them either.

**Index handoff.** The Update wrapper reads `parent+0` at `0x15404DC` to choose the incoming `R8` record. After the QAM call returns, it freshly reads that dword at `0x1540629`, copies it to `parent+4` at `0x1540630`, and writes `(value == 0)` to `parent+0` at `0x1540639`. The wrapper makes no additional call between Update and this copy. The separate resource consumer selects `parent+0x10+sign_extend(*(int32*)(parent+4))*0x6D0`. Two-buffer alternation is a supported interpretation; exact pre/post-call identity still depends on mutation, concurrency and consumer ordering. The complete three-range QAM Update group has no own-body parent-index write identified in this review. Its explicit parent-pointer escape at `0x1528918` calls the read-only leaf `0x3F79D0-0x3F7A49`, which has no stores or calls. Effects of other transitive helpers remain `NOT CHECKED`; this is not a blanket no-mutation proof.

**Copy, not pointer alias.** The 12 October helper review already established the complete three-range `0x2BF9A00` vector-copy/resize contract. That successful evidence was not linked to the later resource-consumer gate. Reusing it against the unchanged exact hash, the newly resolved `R8` owner gives a direct producer: Update `0x1528F88-0x1529003` accepts depths 0 through 2, selects `menu+0xA058+depth*0x10`, passes its count/data in `R8D/RDX`, stride `0xE0` in `R9D`, and destination `incoming_record+0x610` in `RCX` to `0x2BF9A00` at `0x1528FE7`. It stores the returned data pointer at destination `+8`; the helper assigns the destination count at `+4`. Invalid depth clears that count. Thus record `+0x614/+0x618` contains copies of the selected QAM rows. Pointer aliasing with `menu+0xA060` is unnecessary and must not be claimed.

The owner-proven generic resource consumer reads count/data at the same record offsets, uses stride `0xE0`, and consumes the row's first 32-bit value as a resource key. Precise callsite correction: `0x1542038` is the key load into `R8D`; the actual call to `0x2E16E20` is at `0x1542040`, not `0x1542038` as earlier prose stated. It then loads the 32-bit output from the stack temporary at `0x1542045` and passes it to UI field writer `0x6DE4F0` at `0x154204D`. Do not describe this particular output as an `RAX` return value.

This closes the static **QAM item icon dword** field/consumer role: the full-row copy preserves `item+0`, and the matching frontend record schema has a resource consumer for that value. It does not prove a particular appended custom row is selected, survives rebuild, or visibly renders. Those runtime, ordering, retention and resource-lifecycle gates remain open. The `item+0xD8` lasting invariant also remains `PARTIAL`; writes to copied records do not establish writes to original QAM rows.

**Tool correction.** The group scanner previously shared mutable empty sets for object/vtable/method facts, applied a constant-index LEA displacement twice in some expressions, mishandled a scaled object term, ignored negative register signs and retained stale register facts for memory-first `XCHG`. The helper now uses independent sets, applies displacement once, rejects unsupported signed/scaled expressions and invalidates exchanged register outputs. Both targeted root passes still reproduce `0x15404FF` with receiver `argRCX+0xDC0`; slot-zero yields one candidate, all slots yield seven records at six unique callsites. Each pass covers the selected 2,234-byte group with zero reported undecoded ranges and zero state truncation. Register-width/implicit-clobber modeling and partial-decode accounting remain incomplete; broad completeness or absence claims are unsupported.

Reproduction uses the already verified explicit Python executable and exact NMS executable (`$python` and `$nmsExe` from the preceding section):

```powershell
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2CA290 --size 0x43F
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1540430 --size 0x284
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x15286C0 --size 0x17D9
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x3F79D0 --size 0xB0
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1540300 --size 0x130
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x2BF9A00
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x2BF9A00 --size 0x196
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x15419CF --size 0x6BD
& $python -B tools/native_group_embedded_vcall_xrefs.py --exe $nmsExe --object-offset 0x10 --object-offset 0xDC0 --seed-object-register rcx --index-field-offset 0 --index-field-offset 4 --index-stride 0x6D0 --slot-offset 0 --require-immediate 0x6D0 --root-rva 0x1540430 --context 12 --max-states-per-instruction 64 --max-results 30
# Repeat the preceding command without --slot-offset 0 for the all-slot control.
```

Updated scanner SHA-256: `76be238c22fbe14d9352c57d8e0cb8f88e7f35050c92a0887cea939ae8a298dd`. Other tools retain the hashes in the preceding handoff. Environment remains CPython `3.11.9` (interpreter SHA-256 `5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec`), pefile `2024.8.26`, Capstone `5.0.7`.

**Current handoff:** one ledger role changed `PARTIAL -> MAPPED`; current totals are **68/85 MAPPED (80.0%), 13 PARTIAL, 4 NOT CHECKED**, replacing the previous 67/14/4 snapshot. This is static source mapping only. Implementation/profile selection, offline validation, exact-archive live verification and publication remain open. No native source/profile mapping, game operation, test, build, package, push or publication was performed in this follow-up. Keep 7.05 active and 7.06 disabled. Next bounded action: trace the original QAM row fields `+0x4C/+0x4D/+0x88/+0x98/+0xD8` through the now-proven row copy and native consumer branches, starting with the exact `+8`, `+0x40` and `+0x54` checks before the icon-key read; distinguish source mutation from copied-row mutation and establish whether custom rows retain the required behavior. Do not restart the resolved QAM Update caller search.

### Roster identity, native row predicates and composite owner-field producers, 23 October 2026

The resumed pass revalidated the unchanged executable SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`, source base `f7d97b61fcf152677d0d30de34f6c1b48675c436`, dirty branch `compat/cosmos-706-25732212`, CPython `3.11.9`, pefile `2024.8.26` and Capstone `5.0.7`. Retained bounded findings from the interrupted 22 October follow-up are recorded here with new composite-address evidence. No external signature-provider data was used. The official [release log](https://www.nomanssky.com/release-log/) still lists Cosmos 7.06 first; [SteamDB public](https://steamdb.info/app/275850/depots/) still reports build `25732212`, updated 5 October. No newer public patch/build was found on 23 October.

#### Corrected roster identity producer and consumer

Caller `0xF41680` passes `RCX=app+0xE10D0` to `0x50E1A0`. The earlier ledger wrongly propagated a resolver result held in `RDI` at `0x50E2A1` beyond a later definition. At `0x50E661`, `RBX` receives the available roster index from the 30-entry search; `0x50E66E` forms `RDI=RBX*0x24A0`, and `0x50E67F` adds the original roster owner `RSI`. The 16-byte read at `0x50E9D5` is consequently from the actual roster row `+0x2330`, copied to row `+0x2390` at `0x50E9E8`. The `+0x46DD0` key belongs to a separate input table with indices up to 17; its resolver result is not the owner of this later read.

Independent roster copier `0x506500-0x506903` passes source/destination `+0x2320` to helper `0x227E80-0x227EED`; the helper copies 16 bytes at subobject `+0x10` at `0x227ECF/0x227ED6`. This establishes a producer for roster `+0x2330`. The source reads the first eight bytes of this native 16-byte field. Its address/subset contract is MAPPED; semantic seed naming, uniqueness of the selected eight bytes with birth, persistence and live favorite restoration remain separate gates. Retire the erroneous requirement to identify the `+0x46DD0` resolver owner before mapping this source field.

#### Copied-row icon predicates and field consumers

The exact constructor is `0x143D5D0-0x143D6F2`. Its default byte `+8=0`, qword `+0x40=-1`, word `+0x54=0` and chosen nonzero icon meet the ordinary resource-key branch predicates at `0x1541E7F`, `0x1541F00`, `0x1541F0C` and `0x1541F18`. Byte `+0x54` chooses layout adjustment and rejoins; it does not reject this branch. No action-zero, marker `+0x88` or payload check occurs on this selected-row path before the icon lookup. This is a static path, not proof of live selection or lookup success.

The same constructor writes one byte from `R9B` to `+0x4C` and the fifth stack byte to `+0x4D`. The owner-proven copied-row renderer reads `+0x4C` at `0x15420C4/0x1542890` for scalar/tint and alternate-branch selection. It reads `+0x4D` at `0x1541FAE`, saves the value across lookup `0x2067A0`, and writes its Boolean inverse to a selected UI component byte `+0x61` at `0x1541FEC`. Source value 1 produces UI flag 0. These byte producer/consumer roles are MAPPED statically; exact child identity and live meaning remain unverified.

The constructor's inline-text source is fixed RVA `0x4A41320`, beginning with NUL. This path copies one terminating byte to item `+0x98` and forces `+0xD7=0`; 64 bytes is the capacity, not the number copied. The copy thunk resolves to VCRUNTIME140 `memmove`. For the source's zero-initialized item, clearing that span is redundant on this constructor path. Renderer `0x15422EA-0x1542356` consumes the copied span as auxiliary inline text: an empty first byte sets its UI-node flag and skips the text update; a nonempty value is compared and passed to `0x1CC560`. The separately mapped label method/output is the main-label path. The auxiliary-text role is MAPPED; retention and visible UI results remain open.

#### Affine-base correction to the alleged row-flag mutation

In the action-`0x15` Update block, let `P=QAM+0x2D0+state*0x3480` and `B=EBX`. The setup produces `R14=P+0x540+B*0x540` and `RSI=-0x53C-B*0x540`; at `0x15294AD` the sum is `RSI=P+4`. Each subsequent descriptor advances this pointer by `0x540`. Thus `[RSI+0x4C]` is descriptor `+0x50`, not source item `+0x4C`. Write `0x152960B` restores that descriptor field to `0x15`; the constructor independently initializes item `+0x50=0x15`. The earlier `0xFFFF0100` versus `0x15` argument compared different fields and is superseded. The whole block requires source action `0x15` at `0x1529352`; custom action zero instead branches to `0x15296C7`.

Likewise the clear at `[RSI+0x84]` targets descriptor `+0x88`, not an original item marker at `+0x88`. In the separate snapshot path, a complete source row is copied to descriptor `+0x80`, so descriptor header qwords `+0x88/+0x90` are sourced from row `+8/+0x10`. Keep this header distinct from the marker at original/copy row `+0x88`. The separate binding loop does compare copied-row `+0x88/+0x90` against candidate keys, and writes the matched ordinal to copied-row `+0xD8`. Renderer `0x1542A15` omits binding UI for `-1`. These observations do not establish all original-row mutations or retention; both custom marker and source `+0xD8` gates remain PARTIAL.

#### New exact setters through the enclosing application

The owner is `app+0xE10D0`. Therefore owner-relative preview `+0x1B9300` is application-relative `+0x29A3D0`, and owner-relative byte `+0x1B937D` is application-relative `+0x29A44D`. Searching only the owner-relative displacement had missed real writers.

A batched fast-candidate pass over these composed displacements and adjacent possible wider-store bases completed `52,110,272` runtime-function bytes, reported zero skipped ranges, and printed every match. Preview `0x29A3D0` had five operands; busy `0x29A44D` had two byte stores; adjacent `0x29A44C` had one distinct byte store. Queries `0x29A440/0x29A448` returned zero. These counts are candidate evidence; exact root-aligned review establishes the fields:

- In the complete 17-range root `0x1540CF0`, `RBX` is loaded from application global `0x6E8D708` at `0x15434EA`. The selected copied row supplies its 32-bit slot `+0x84` in `ESI` at `0x154334D`. The action-`0x2E` path requires native eligibility `0x508290`; it assigns that selected slot at `0x154361F`. Other paths clear the field to `-1` at `0x1543512/0x1543646`. The already mapped owner-update consumer reads owner `+0x1B9300`, rejects -1 and uses the slot with the same eligibility/placement owner. This closes the preview/selected-slot static gate; the separate active companion slot remains a different field.
- Action `0x22`, a nonzero menu selector and successful helper `0x50A220` set application byte `+0x29A44D` at `0x1543703`. The alternate/failure path clears it at `0x154373C`, then stores the associated 16-byte placement value at `app+0x29A450`. Owner update reads the same byte at `0x5090D9` and selects its placement/preview branch. This closes the byte's static guard contract. The source name `emote` is not independently established; do not promote that semantic name to a proven fact.

The interrupted earlier composite scan lost its final output and its old process ID was unavailable after resumption. It is NOT CHECKED, not zero; only the completed rerun above supplies counts. The prior adjacent owner-relative pass had eight `+0x1B9300` operands and one `+0x1B937D` read; none supplied the missing byte writer. Reuse the composed-owner method rather than repeating that negative.

#### Selected package and ledger reconciliation

`tools/build_native_runtime.py` defaults the observer/trial flags off, but `tools/package_native_runtime.py` requires `teleport_candidate_trial=True` and the exact reviewed filter in the build receipt. The trial build defines both `CAS_RESPAWN_OBSERVER` and `CAS_TELEPORT_CANDIDATE_TRIAL`. Consequently the public package includes the observer and all three return filters; they cannot be dropped from the 85-role denominator by inspecting the compiler defaults alone.

The existing 22 October relocation section already recorded observer candidate `0x14F9E20`, all three exact LocalLoadState calls/returns (`0x33030F/0x330314`, `0x3306BA/0x3306BF`, `0x330991/0x330996`) and flag values. Their NOT CHECKED ledger rows were stale. The observer is now PARTIAL pending ABI/event policy; the three return addresses are MAPPED statically with their live/semantic gates retained. The binding-filter row likewise now reflects its existing static `0x15292F5` caller/register/layout proof; its remaining thread/input tests are live gates. These four status normalizations are retained evidence, not new binary discoveries.

#### Reproduction and handoff

Use the verified explicit interpreter and executable from the preceding handoff:

```powershell
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x50E1A0 --size 0xAFD
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x506500 --size 0x403
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x227E80 --size 0x6D
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x143D5D0 --size 0x122
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x15288D6 --size 0x15AB
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x15419CF --size 0x1168
& $python -B tools/native_data_offset_xrefs.py --exe $nmsExe --offset 0x29A3D0 --offset 0x29A440 --offset 0x29A448 --offset 0x29A44C --offset 0x29A44D --fast-candidates --limit-per-offset 100
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x1543703
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1542B37 --size 0x9B3
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x15434EA --size 0x9A
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x15435F8 --size 0x17D
```

Tool SHA-256: `native_data_offset_xrefs.py` `5d3f80c87679dcf6dd41bde71f027628eb6af24fc6ee06ecf32924e63fac34b8`; `native_function_disasm.py` `26022f1b7b2ede68acaf2cad6f6ccb41b5e3146a3fb7faa36df9c6e520fc2cb0`; `native_pdata_function_group.py` `fb1adbfa08a7bddf4a82500eae082b6abacc33de3cd53b303c68a84e58971b26`. The interpreter hash remains `5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec`.

Current source ledger: **78/85 MAPPED (91.8%), 7 PARTIAL, 0 NOT CHECKED**. Six partial field roles closed; four previously recorded static sites were reconciled; the observer moved from an inaccurate NOT CHECKED state to PARTIAL. No native mapping/profile, test, build, package, game operation, commit, push or publication was performed. Localization impact is none: only analysis/documentation rules changed, with no player text or behavior edit. Keep 7.05 active and 7.06 disabled. The compact gate index at the top is the next-work queue. Next bounded analysis: establish the actual texture-resource constructor/allocation and error-byte producer, or the observer's physical argument forwarding, rather than reopening resolved menu dispatch and owner-field searches.

### Registered type-7 factory and analysis helper corrections, 23 October 2026

This supersedes the preceding 78/85 count. Against the executable/source identities at the top, the current ledger is **79/85 MAPPED (92.9%), 6 PARTIAL, 0 NOT CHECKED**. The additional closed static role is resource minimum extent; live compatibility and release readiness remain separate.

#### Allocation and registration proof

- `0xEC8700-0xEC87A8` takes one texture-record pointer, passes type 7/path/flags `0x1000` through `0x183E770-0x183E840` to loader `0x2D63EA0`, and stores the output handle at record `+0x10`.
- Registration root `0x183C8C0` loads manager cell `0x6E1FC90` at `0x183CC1B`, selects type 7 at `0x183CC22`, forms factory `0x1834A80` at `0x183CC3F`, and passes it in physical argument six at `0x183CC46` to registrar `0x2D6B1B0` at `0x183CC71`.
- Registrar `0x2D6B1B0-0x2D6B3AD` resolves the type node through manager `+0xB8`/vector `+0xD8`. Its prologue puts argument six at `RBP+0x7F`; it preserves that value and stores it in node `+0x38` at `0x2D6B355`. Loader `0x2D63EA0-0x2D644BB` selects the same node, reads node `+0x38` at `0x2D6424A`, and invokes it at `0x2D64322`.
- Factory `0x1834A80-0x1834ADA` requests `0x400` bytes (`ECX` at `0x1834A95`, allocator call `0x1834A9D`), calls constructor `0x1894A20` at `0x1834AB3`, performs its post-load step and returns the same allocation.
- Constructor `0x1894A20-0x1894B24` calls common resource constructor `0x2D62BC0` with `EDX=7` at `0x1894A48`. It initializes payload `resource+0x1F8` through `0x1888100` at `0x1894AF1`; that helper calls `0x18881D0` at `0x188816D`. The qword write at `0x1888244` is payload `+0x68`, hence resource `+0x260..+0x267`. This establishes the required `0x268` minimum static extent. Another type-7 allocation at `0x183C5EF/0x183C5F4` independently also requests `0x400`.

Completed full direct-call scans decoded 52,110,272 bytes with zero skipped ranges: common constructor `0x2D62BC0` had 11 callsites; type-7 constructor `0x1894A20` had two (`0x1834AB3/0x1840516`). The full RIP scan for factory `0x1834A80` had one reference, `0x183CC3F`. Counts cover only the stated decoded direct forms.

The common `cTkResource` RTTI/vtable `0x352FFC0` is structurally validated. Its constructor `0x2D62BC0-0x2D62D5B` zeroes a dword at `+0x139` (`0x2D62D34`), covering `+0x13A`. Copier `0x2D65250-0x2D6532F` copies byte `+0x13A` at `0x2D652F0/0x2D652F7`, alongside `+0x139/+0x13B`. Initialization/copying does not prove the source name error. The fallback consumer at `0x2D64418` reads neighboring `+0x13B`; `+0x13A` remains PARTIAL.

#### Reproduction and bounded helper changes

Use the explicit verified interpreter/executable recorded above. Representative exact bounded commands for the chain:

```powershell
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1834A80 --size 0x5A
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1894A20 --size 0x104
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1888100 --size 0xC4
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x18881D0 --size 0x7C
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x183CC71
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x2D6B355
& $python -B tools/native_rip_xrefs.py --exe $nmsExe --target-rva 0x1834A80 --limit-per-target 20
& $python -B tools/native_data_offset_xrefs.py --exe $nmsExe --offset 0x139 --offset 0x13A --offset 0x260 --rva-min 0x2D60000 --rva-max 0x2D70000 --fast-candidates --limit-per-offset 80
& $python -B tools/native_data_offset_xrefs.py --exe $nmsExe --offset 0x13A --offset=-0x13A --rva-min 0x14DCC10 --rva-max 0x14DE09F --fast-candidates --limit-per-offset 20
& $python -B tools/native_rtti_name_inventory.py --exe $nmsExe --contains SearchContext --max-name-bytes 512 --include-structs
```

`native_data_offset_xrefs.py` now has optional RVA bounds, counts excluded ranges and preserves displacement signs in fast candidate parsing/labels. Bounds include only complete `.pdata` ranges; excluded chained fragments remain outside any negative. The manager window decoded 62,683 bytes, zero skipped, 157,140 excluded ranges: five `+0x139`, two `+0x13A` copier operands and zero `+0x260` in that window. The negative control decoded 5,263 bytes: positive `+0x13A` zero, negative `-0x13A` two (`0x14DD13A/0x14DD142`). A 381-byte busy-byte control reproduced both known setters. No updated global field count is claimed.

Final SHA-256: `native_data_offset_xrefs.py` `B7EEF065D428871F434199FF69F83C298A0891454D1EC52C752E9360E28D513A`; `native_rtti_name_inventory.py` `77B8AB67A79E1F7E8597AD8B53DC7572A1E2FEC05F8B4D0424AB56F3E61E844B`. Historical full-image counts keep their historical tool hashes. The name tool's new opt-in `--include-structs` includes `.?AU` as well as `.?AV`; its class-only default is unchanged.

Useful failed or bounded approaches:

- TextureResource/ResourceTexture inventory queries were zero, not proof of class absence. A broader class/struct Texture query with 512-byte names found 68 but printed 60: unprinted names were unclassified. The narrower cTkTexture query was zero.
- Getter-byte discovery found leaves `0x13554F0/0x1355500/0x1355510` for `+0x139/+0x13A/+0x13B`, all with zero decoded direct E8 callers. Validated reverse RTTI identifies `0x1355500` as `.?AUSearchContext@GPN@@`, vtable `0x4ADA858` slot 5, base SearchInterface. Reject it as a resource getter.
- An ad hoc derived-vptr COL parser failed on an invalid locator and later PEFormatError: TOOL ERROR, with no derived-class conclusion. Manager constructor `0x2D62D60` was not resource-allocation evidence; the registered callback chain is the useful proof.
- Initial windows crossed the ends of `0xEC8700`, `0x183E770` and `0x1888100`. Only established extents were used; the bounded commands above avoid adjoining bodies.

No profile/native RVA mapping, installed runtime, build, package or release changed. Next: connect `+0x13A` to a same-object nonzero producer/consumer or justify an explicit source policy from its actual use. Ordinary-state zeros do not establish error semantics.

### Early read-only game observations and development rule, 23 October 2026

The owner authorized launching NMS, then confirmed loading a save with X closed, opening the pet summon menu, and closing X. The owner also reported boarding the ship to avoid environmental harm. Its exact ordering relative to the final capture is unconfirmed; do not attribute all final differences solely to closing X.

Before launch, a private closed-game snapshot hash-verified 61 save files and two preference files: **63 files, 8,566,112 bytes**. Original files were held read-only during copying. Snapshot/receipt use a protected current-user/SYSTEM ACL outside Git. Initial sandbox attempts failed with MethodInvocationException/UnauthorizedAccessException and yielded no verified receipt. LOCALAPPDATA was redirected; the real absolute backup path was also denied in that context. The authorized desktop operation succeeded without weakening permissions. A sandbox Steam URI request did not establish a running game; desktop launch was followed by an actual process check. No process was terminated or installed runtime changed.

The development helper `tools/native_readonly_resource_snapshot.py` requests only `PROCESS_VM_READ|PROCESS_QUERY_LIMITED_INFORMATION`. It requires an explicit PID and exact hash, checks the opened process image path, module size, loaded COFF header and 16-byte prefixes at `0x15286C0/0x508DC0/0x2D62D60`. Reads/work are bounded; sampled table/identity checks are repeated. Output is aggregates, one public SUMMONPET asset and bounded QAM/header comparisons. There is no game write, injection, hook, native call, settings or save operation; it is not packaged player functionality.

```powershell
& $python -B tools/native_readonly_resource_snapshot.py --pid <verified-NMS-pid> --exe $nmsExe --entry-limit 10000
```

Initial helper SHA-256 `86E047C986478A6C35216AB9BD07BB48D63D8A531F669627A4A7BD0C9C3146F1` covers the first two captures. Extended QAM/notice-float helper `2261A30190BC6D61B26404B5FF755251879398F66AB2A278E1BC2058E8BD2A07` covers the last two. These are direct read-only game observations, without an implementation test suite, build, package, new hooks or deployment.

| Capture / owner-reported state | Table / examined entries | Type-7 entries observed | QAM result |
| --- | --- | --- | --- |
| After startup; exact screen unconfirmed | 6,580 / 6,580 | 6,452 | Expected vtable; detailed rows not yet implemented |
| Save loaded, X closed | 76,467 / first 10,000 | 7,737 | Expected vtable; detailed rows not yet implemented |
| Pet summon menu open | 76,476 / first 10,000 | 7,736 | Depth 1; source 6 rows, copied 6 rows, icon/action keys equal; 5 nonzero icons; selected index 3; write index 1, consumed index 0 |
| X closed; ship entry also reported | 76,476 / first 10,000 | 7,736 | Depth 0; source 7 rows, copied 6 rows, keys differ; 7 nonzero source icons; selected index 2; write index 1, consumed index 0 |

Both manager cells matched in every capture. Every sampled type-7 object had vptr RVA `0x4B02D68` and bytes `+0x138..+0x13C = [1,0,0,0,1]`. SUMMONPET stayed at handle 5617 in this process, image dword zero and texture pointer nonzero. Most sampled textures had that shape; 91 loaded-game entries had nonzero image/zero texture. Handle numbers are observations, never reusable constants.

The confirmed open-menu capture corroborates the source-to-frontend copy schema and distinct indices in one stock-game state. Closed-menu cached rows need not equal the current source depth. This does not prove custom-row retention, lifetime/thread safety, error semantics, ABI forwarding or released mod behavior. Loaded-game captures leave all entries after 10,000 unexamined. Both detailed captures saw a finite negative notice float, leaving NaN policy untested.

A scratch attempt to reverse the observed vtable through its preceding file COL pointer failed a validity assertion before RTTI validation: TOOL ERROR, not a class identification or class-absence result. Its command session was polled to final exit 1. Do not assign the common base class name to this observed vptr.

The owner identified the workflow failure: runtime evidence arrived too late. AGENTS.md now requires planning it during the first work period, preparing a minimal safe observation after one unproductive static attempt on an observable question, and requesting one specific player action at a time. DEVELOPMENT.md links the mandatory playbook procedure for baseline/action/after-state, confounders, exact-process identity, privacy and separate release gates.

Current ledger remains **79/85 MAPPED, 6 PARTIAL, 0 NOT CHECKED**. Keep 7.05 active and 7.06 integration disabled. These normal-state observations do not automatically close the six static gates. Localization impact is none: analysis tools and workflow/docs only. Next: a positive `+0x13A` producer/consumer and the source marker/binding contract via the corroborated owner chain. Implementation, archive and behavior gates remain open.

### Missing-data failure byte and conservative notice policy, 23 October 2026

This supersedes 79/85: **81/85 MAPPED (95.3%), 4 PARTIAL, 0 NOT CHECKED**. Resource `+0x13A` and the notice float contract are now statically mapped. The four remaining rows are the load-hook policy, observer ABI/event policy, marker retention and original-row `+0xD8` invariant. The native profile remains 7.05.

#### Resource failure producer connected to the observed texture object

The runtime-observed type-7 vptr `0x4B02D68` has a contiguous executable pointer run. Slots 0..15 resolve to `0x1894B30, 0x18338C0, 0x18338D0, 0x1888960, 0x1C7A60, 0x472C50, 0x1CB9D0, 0x1833BF0, 0x1895480, 0x1833990, 0x2D661F0, 0x1833960, 0x1895410, 0x1895AE0, 0x1896FB0, 0x1897020`. Its preceding word is not a validated absolute COL pointer, so this identifies method pointers, not a new RTTI class name.

Slot 13 target `0x1895AE0` saves the incoming resource in RBX, saves data/size from RDX/R8D, and sets neighboring `+0x13B=1` if data is null. No call or RCX redefinition intervenes before the call to `0x18DD960` at `0x1895B23`. Thus the callee receives the same texture resource, not a lookalike sibling object.

Complete callee `0x18DD960-0x18DD9F7` preserves RCX in RBX and checks slot 1 (the already-ready getter). When not already ready, null data or a nonpositive size takes a diagnostic path referencing generic missing-resource-data text at `0x4B04898`, then writes **word `resource+0x139=0x0101` at `0x18DD9C3`** and returns false. Byte `+0x13A` is therefore set to 1 on this exact missing/empty-data failure. Common constructor `0x2D62D34` clears it within a dword; copier `0x2D652F0/0x2D652F7` preserves it. This closes the source's error-veto byte contract without conflating it with `+0x13B`.

Independent manager helper root `0x18385F0` has three ranges (`0x18385F0-0x1838646`, `0x1838646-0x183870E`, `0x183870E-0x18387EB`). It saves incoming RDX as the resource in RBP. With a nonzero resource key and R8B false, it checks bytes `+0x139` at `0x1838777` and `+0x13A` at `0x1838784`; either nonzero skips the keyed insertion path. Generic loader call `0x2D64028` passes its resource in RDX and zero in R8D. This corroborates the same byte's native veto role. All live samples were ordinary successful resources; no missing-data fault was induced.

A bounded range scan `0x1833000..0x1898000` decoded 389,411 bytes, zero skipped, 155,979 excluded ranges: `+0x138` 44 hints (30 printed), `+0x139` 7 (all printed), `+0x13A` one (the consumer above), `+0x13B` 87 (30 printed). This is a candidate scan with unclassified truncated outputs, not a global producer-negative. Following the consumer's callers exposed the wider word store outside that window.

Completed full direct E8 scans each decoded 52,110,272 bytes, zero skipped. Targets `0x18385F0/0x1888960/0x1895480` had 4/0/1 direct calls. The four manager calls are `0x184C46D, 0x1895AA7, 0x18DD9D9, 0x2D64028`. Target `0x18DD960` had eight: `0x184C88B, 0x18773F3, 0x18894F0, 0x18913E0, 0x1895B23, 0x18A57BD, 0x18B415B, 0x18E0FD0`. All were printed.

Reproduce with the unchanged verified Python/Capstone/pefile and executable:

```powershell
& $python -B tools/native_data_offset_xrefs.py --exe $nmsExe --offset 0x138 --offset 0x139 --offset 0x13A --offset 0x13B --rva-min 0x1833000 --rva-max 0x1898000 --fast-candidates --limit-per-offset 30
& $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x18385F0 --target-rva 0x1895480 --target-rva 0x1888960 --limit-per-target 24 --context 8
& $python -B tools/native_call_xrefs.py --exe $nmsExe --target-rva 0x18DD960 --limit-per-target 40 --context 8
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x1838784
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x18385F0 --size 0x1FB
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x18DD960 --size 0x97
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x1895AE0 --size 0x48
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x9BF7B0 --size 0xB0
```

Tool hashes remain those recorded above: data-offset helper `B7EEF065D428871F434199FF69F83C298A0891454D1EC52C752E9360E28D513A`; direct-call helper `7EB4CA84D93D7A64D7D754EA9EC1D60E488F63F0F581A0C031486940385FBFAF`; disassembly helper `26022F1B7B2EDE68ACAF2CAD6F6CCB41B5E3146A3FB7FAA36DF9C6E520FC2CB0`; group helper `FB1ADBFA08A7BDDF4A82500EAE082B6ABACC33DE3CD53B303C68A84E58971B26`.

Tool limits: `native_pdata_function_group.py --rva` is singular. An attempted multi-`--rva` invocation selected only its last target (`0x2D661F0`, one range `0x2D661F0-0x2D6635F`); it did not inspect the other three. A later individual query for `0x1888960` returned no containing `.pdata` range. Combined with its direct-call zero this does not exclude a valid virtual leaf/thunk. Its semantics were not needed for the slot-13 failure proof. A bounded inspection of `0x1895870..0x1895AD4` connected its `0x1895AA7` resource argument, without claiming the excerpt includes every return/chained range.

#### Notice float: retain the existing deliberate refusal

`0x9BF7F9` reads the 4-byte application field; `COMISS` at `0x9BF801` followed by `JAE` at `0x9BF804` rejects ordered nonnegative values. Under the ordinary masked comparison semantics, unordered input does not take that branch. The source already requires `<0`, so it suppresses a cosmetic notice for NaN. Preserve this intentional conservative policy, rather than claiming full predicate equivalence or searching indefinitely for a producer to prove NaN impossible. Two owner-assisted observations saw a finite negative value.

The only runtime.cpp edit is an explanatory comment beside the unchanged predicate. No code behavior, player-facing text, native RVA, profile, build, test suite, package or installation changed; localization impact is none. The changelog records the unreleased tooling/workflow and this existing policy. Source field provenance and predicate are mapped; semantic naming/range of the producer and exact-archive visible HUD delivery remain separate. This reasoning does not relax local/network, event-completion or ABI requirements.

Next bounded action: complete the observer's argument-use audit at `0x14F9E20` (including its first callee's possible volatile-input use), then resolve the selected LocalLoadState event policy. Marker/source-binding retention still needs its own producer/copy/consumer boundary; stock rows alone do not verify custom rows. Keep unsupported integration disabled.


### Observer first-callee audit and prepared lifecycle observation, 23 October 2026

The owner asked whether the game could be closed and was told to save/exit normally; no further game reads, launch or installed-runtime changes followed. The observations above are retained. The ledger remains **81/85 MAPPED, 4 PARTIAL, 0 NOT CHECKED**; this source ledger does not imply that new development tools are validated.

Observer `0x14F9E20` preserves its incoming RCX, EDX and low R8 byte and reaches first callee `0x563060` at `0x14F9F71` without reading/saving incoming R9 in that reviewed prefix. Complete callee `0x563060-0x5630CE` overwrites R9 with RCX at `0x56306A`, before using it; it cannot propagate the observer's incoming fourth register value. This resolves the specific first-callee R9 escape concern. It does not close the remaining stack-alias/completion/event-policy audit or establish reason 11 as teleport.

Reproduction uses the unchanged disassembly/group helper hashes recorded above:

```powershell
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x14F9E20 --size 0x170
& $python -B tools/native_pdata_function_group.py --exe $nmsExe --rva 0x563060
& $python -B tools/native_function_disasm.py --exe $nmsExe --rva 0x563060 --size 0x6E
```

The copied-row binding-write excerpts at `0x1529D87/0x1529E47` were reproduced from the complete `0x15288D6..0x1529E81` range (`--size 0x15AB`, filtered context 27/9). They still operate on the incoming record's `+0x614/+0x618` and `+0x51C/+0x520` vectors, not original QAM vectors. The subsequent helper `0x1530AC0-0x1530CC3` is already documented navigation (group query reproduced one 0x203-byte range). That bounded check adds no original-row invariant evidence; do not restart the navigation search or relabel copied writes as original writes. Marker and binding retention remain PARTIAL.

Prepared next tool: `tools/native_readonly_lifecycle_trace.py`, SHA-256 `A3B7A930FE48E10FC0A78FEF389F41518CC2D15EBFCC9D0F602D6AADACA39D0C`. It imports the extracted exact-process guard from resource helper SHA-256 `7A550B94F9DC63FE5C9443A9A607001EC4FD110A79B555F124EF28D02FF36D09`. These two new revisions are **NOT CHECKED: not executed, built or tested**. Prior live evidence remains attached only to the two earlier resource-helper hashes.

```powershell
& $python -B tools/native_readonly_lifecycle_trace.py --pid <verified-NMS-pid> --exe $nmsExe --seconds 30
```

The proposed 50-ms poll is bounded to 1..45 seconds and 256 changed records. It reads FSM current pointer cell `0x6E8D6E0`, verifies LocalLoadState at `0x6E8EA40` with vptr `0x4A50A30`, and samples its phase `+0x62C` and reason `+0x620`. With an application pointer it also samples the source load predicate byte at app `+0x4BE6A0`, and session slot app `+0x941C70+0x1A8`. Session `+0x418/+0x41C` is read only for exact known Session/PlayfabSession vptrs; only zero/nonzero is emitted for the identifier-like leading byte. Addresses/private identifiers are not emitted. Changed identity/phase samples are refused/omitted. It has no hooks, process writes, native calls, settings or save operation.

Next live question: which phase/reason/predicate changes are actually observed during one confirmed local-save load, then separately during one ordinary teleport? Capture baseline before requesting the action; do not name enums from old-build numbers. Polling can miss transitions and is not a callback ABI/completion proof. The source callback/tracepoint and local-versus-network gates remain open even if a reason correlates once. Prepare the precise action and backup before a future authorized game session; the owner need not keep this session open.

The source runtime.cpp change remains a comment beside the unchanged conservative HUD predicate, now explicitly scoped to the reviewed 7.06 native comparison. No player-facing text, native mapping/profile, implementation test suite, package, deployment or public release changed. A local research checkpoint can preserve the rules, reports and analysis code independently of the pre-existing bootstrap ABI edit. Do not publish or call the port supported from this checkpoint.

### Local research checkpoint receipt, 23 October 2026

Local commit `42190cb47df723fa28b96c69ececa4a630305b17` preserves the rules, reports, analysis helpers and comment-only HUD clarification on `compat/cosmos-706-25732212`, authored with `core@lineum.io`. The source baseline under investigation remains `f7d97b61fcf152677d0d30de34f6c1b48675c436`; the pre-existing bootstrap ABI edit remains outside this checkpoint. The staged whitespace inspection passed after removing two whitespace-only lines. No implementation tests, build, package, new deployment, push or publication ran. Personal interpreter paths were replaced with verified-path aliases without changing recorded argument values or input hashes. An initial sandbox Git-index lock denial was resolved using the authorized desktop context; no failed attempt was called a commit.

The current static ledger is **81/85 MAPPED, 4 PARTIAL, 0 NOT CHECKED**, with new lifecycle tooling explicitly NOT CHECKED separately. The public package remains `0.10.2-native-test` for Cosmos 7.05; the target remains Cosmos 7.06 / build 25732212 / exact SHA-256 recorded above. Next is the prepared player-assisted lifecycle observation and the remaining row-retention work, followed by source/profile implementation and the independent offline/live/archive/release gates. This receipt records a local checkpoint, not GitHub synchronization or a supported update.

### Local load, teleport and menu observations, 23 October 2026

Exact target: Cosmos 7.06 / Steam 25732212 / file version 180836 /
88,560,712 bytes / SHA-256
`13D5060D4EFB9D2A6A6B1B349BC4257231056CC2A055DF4BB15D816262CC3499`.
Source work period started at local checkpoint `508526c`; the original
dependency baseline remains `f7d97b61fcf152677d0d30de34f6c1b48675c436`.
CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7 were verified again;
interpreter SHA-256 is `5F7B89A612C9B8AF1D6456CDFCD1DBE5CA630849E79AEBCED9BEE9A6694952EC`.

Before launch, a fresh closed-game backup verified 61 save files and two
preferences, 63 files / 8,612,490 bytes, source/copy SHA-256 equality and
protected current-user/SYSTEM permissions. No restoration or save edit ran.
Normal Steam launch was followed by an actual process check. The old native
mod remained disabled on 7.06; no new DLL, hook or installed runtime was used.
The owner operated the game UI and confirmed each arrival/control state.

#### Capture revisions and exact scope

- Initial lifecycle revision `A3B7A930FE48E10FC0A78FEF389F41518CC2D15EBFCC9D0F602D6AADACA39D0C`
  was not executed. Revision `64104B0940A16CE96E930419108DDBA95BC5DC75B03D9687D2968C32627BE6C5`
  reads an initial sample before printing ready and covers the first three captures.
- Revision `C785323A3C8B1CEEDCB75F3BD749881B5EDC133A8E3A90AF1A67980D74789D30`
  extends duration to 1..180 seconds (default 120) and adds
  `--stop-after-local-load`: three outside-state, phase-zero samples after
  observing LocalLoadState. The stop is not callback/completion proof.
- These lifecycle captures used shared reader revision
  `7A550B94F9DC63FE5C9443A9A607001EC4FD110A79B555F124EF28D02FF36D09`.
  Its opened-process/image guard was exercised; it is no longer NOT CHECKED.
- Menu aggregate revision `96DEE154C0FA1E727F2768A85E21A7143A47903350578122518CE7824E28AEBC`
  adds equality/nonzero counts for 16-byte original/copied markers and counts
  of signed 4-byte `+0xD8` values. It emits no marker bytes or raw pointers.

All reads use the exact executable hash, opened-process path/module size,
loaded PE header and three bounded code anchors. Access is only
`VM_READ|QUERY_LIMITED_INFORMATION`. There are no process writes, native
calls, hooks, settings/save operations or account-identifier output.

```powershell
& $python -B tools/native_readonly_lifecycle_trace.py --pid <verified-NMS-pid> --exe $nmsExe --seconds 45
& $python -B tools/native_readonly_lifecycle_trace.py --pid <verified-NMS-pid> --exe $nmsExe --seconds 2
& $python -B tools/native_readonly_lifecycle_trace.py --pid <verified-NMS-pid> --exe $nmsExe --seconds 120 --stop-after-local-load
& $python -B tools/native_readonly_resource_snapshot.py --pid <verified-NMS-pid> --exe $nmsExe --entry-limit 1
```

#### Named question: what changes during a confirmed local load versus teleport?

| Capture/action | Baseline and observed result | Bound |
| --- | --- | --- |
| Main menu -> owner-confirmed local save load | Current FSM `0x6E930A0`, phase 2/reason 0 -> LocalLoadState `0x6E8EA40`, phases 3,5,6,8,10,11,12,13,14,15,17,19,20 -> current `0x6E8F140`, phase 0/reason 1. Reason first became 1 at phase 8. | 45 s, 893 samples, 14 changes, zero omitted unstable samples, 58,117 bytes read. |
| Confirmed teleport to station | Baseline current `0x6E8F140`, phase 0/reason 1; timed window saw no changes. | 45 s, 893 samples, zero changes/unstable samples, 58,117 bytes. This does not show when/why the transition was missed. |
| Immediate station after-state | Same current state and phase 0; reason 11, following the owner's arrival/control confirmation. | 2 s, 41 samples, zero changes/unstable samples, 2,737 bytes. Association only; callback timing not captured. |
| Confirmed return to base | Baseline already reason 11, phase 0/current `0x6E8F140`; repeated longer window saw no changes. | 120,016 ms, 2,378 samples, zero changes/unstable samples, 154,642 bytes; duration limit, not automatic observed-state exit. |

The application was present, source predicate byte `app+0x4BE6A0` was zero,
and session slot `app+0x941C70+0x1A8` was absent in every accepted sample.
This does not establish that the byte classifies all network/local cases.
The save load's first LocalLoadState sample was at 25,735 ms; phase 8/reason 1
at 37,844 ms; outside state/phase 0 at 44,204 ms. Poll interval is 50 ms.
Do not request another identical teleport poll after the two bounded misses.
Use a different event anchor if exact call timing is needed. No death or
multiplayer action was performed. The owner was told the game could be saved
and closed after the menu reads; actual shutdown was not claimed.

#### Named question: do original and consumed copied menu fields agree?

At the base with X closed: depth 0, source rows 9 / copied rows 0;
source `+0xD8` values all -1 and zero nonzero marker fields; 5,548 bytes read.
This is an inactive after-state, not a failed active-menu copy.
Then the owner opened X -> summon pets and held it without summoning.
Two independent accepted snapshots each observed depth 1, write index 0,
consumed index 1, six original and six copied rows, equal icon/action keys
and equal marker fields. Two marker fields were nonzero in each vector;
all six original and six copied `+0xD8` values were -1. Five original icons
were nonzero, selected index was 3; each snapshot read 6,892 bytes.
Notice float was finite negative. Resource scope was only the first entry
of 76,575, not a whole-table readiness result.

These results corroborate the statically established owner/copy contract.
They do not verify an appended custom marker, arbitrary equality collisions,
rebuild retention, thread synchronization or an uninstalled mod's behavior.

#### Observer stack-alias audit

Full `0x14F9E20..0x14FC07A` decodes 8,794 bytes. After the proven prologue,
`RBP=entryRSP-0x448` and body `RSP=entryRSP-0x548`; 330 direct stack operands
have zero accesses at/crossing fifth-argument start `entryRSP+0x28`.
The largest home-slot access ends at that boundary, not beyond it.
Incoming RCX/EDX/low R8 are retained; the already audited first callee
`0x563060` overwrites R9 before use. The remaining nine LEAs are now bounded:

| LEA sites | Home address | Consumer and extent |
| --- | --- | --- |
| `0x14FA092`, `0x14FB331` | entry +0x20 / +0x08 | Leaf `0x1CDAF0..0x1CDB1F` reads four bytes. |
| `0x14FA7C1`, `0x14FA7DF` | entry +0x10 / +0x20 | Context fields +8/+0x18 passed to complete chained `0x14FC080..0x14FC25A`; first is read as four bytes at `0x14FC0A7`, second receives one byte at `0x14FC24C`. |
| `0x14FA9D7`, `0x14FAB1E`, `0x14FB995` | entry +0x18 | Tenth argument of complete chained `0x14FEB30..0x14FF308`; forwarded only to byte outputs in `0x15108B0` (sixth argument) / `0x1512370` (fifth). Stores at `0x1510951/0x1511907/0x1511CC3` and `0x15123BE/0x151282A`; the latter register is subsequently redefined. |
| `0x14FB368` | entry +0x08 | Leaf `0x14F9940..0x14F996C` writes four bytes on both branches. |
| `0x14FB5F7` | entry +0x20 | Leaf `0x1362600..0x1362666` reads/writes words at +0,+2,+4; caller's separate +6 byte is also inside the home area. |

Reproduce with the recorded disassembly helper and `.pdata` group helper:
observer `--rva 0x14F9E20 --size 0x225A`; group roots `0x14FC080`,
`0x14FEB30`, `0x15108B0`, `0x1512370`; inspect the LEAs and exact consumer
offsets above using instruction boundaries from the group roots.
The three small leaves have no containing `.pdata` entry; that helper's
error was followed by bounded entry/branch/return decoding, not absence claims.
An initial window of the second leaf stopped before its final branch return;
the corrected window includes `0x14F996B`. No extra stack input is inferred
from borrowed shadow homes. Physical three-input forwarding is now supported;
event completion, native meaning of reason 11 and multiplayer policy remain
separate from this ABI result.

A bounded old-binary inventory (`rg --files --hidden -g '*NMS*.exe'`, excluding
Git/dependency caches) in the original repository, compatibility worktree and
Documents/Codex found no old executable filename. This does not prove global
absence. No depot download or repeated broad search followed.

#### Source preparation and regression checkpoint

`native_mappings.json` is now the single build-specific RVA/return/policy input.
Generated C++ constants, build receipts, bundle validation and packaging
expectations use the same exact release/build/hash record. Profile reading
also rejects a well-formed foreign hash carrying an approved build label.
7.06 remains `activation_approved=false`; normal build/package and runtime
activation reject it. The root native profile still selects 7.05.

The prepared 7.06 policy checks the applied FSM state, its vtable and
`app+0xB940` receiver before and after the original load call, with repeated
application/state reads. Arguments/results pass through unchanged. The
existing zero-only fourth-input veto is retained without naming it network.
The 7.05 callback sequence is preserved. The existing label forwarding of
the opaque third output is retained. Four new policy-input rows expand the
inventory to **85/89 MAPPED, 4 PARTIAL**; no old role was removed or promoted.

Owner-authorized offline results: 38 focused tests, 403 production tests,
805 developer tests; native 7.05 regression build; policy 31,216 commands,
selector 25,733 commands, storage 333 cases/721 operations, runtime 63 cases,
backup 16 checks, six unsupported-host runs; menu 25 scenarios and exact
213-byte filter parity. Counts of comparison commands are not independent tests.
All final runs passed; initial sandbox runs failed on atomic temp-file writes
(production 17 failures/134 errors; developer 8 failures/9 errors), then passed
in an explicit owned temp directory in the authorized desktop context.

Build `build/native-mapping-prep-20261023-r1` used LLVM-MinGW 20260922 archive
SHA-256 `E3AD77D117A4BEA19A7A3B333341824D79A5A371004A10E25B8504E7B3047666`,
compiler wrapper SHA-256 `20BA1856942744291A6AAAF9F2C94F6D0CD7CAC5AA9557FCE96471DC7EF25D6F`.
ASI is 2,637,312 bytes / SHA-256
`3B4CBCC804CE0D52641435C232111789DBC1500626FA8DD7C40A159F881B0AB6`.
This build selects 7.05; it is not a 7.06 gameplay test or a new release.
Menu report is `build/native-menu-mapping-20261023-r1/menu-validation.json`.
Private build/validation receipts retain exact source/product hashes.

The first native bundle run failed backup before any checks with sharing
violation 32 while another file-writing suite ran. Later individual directory
opens passed; a serial rerun passed all 16 backup checks and the full bundle.
Concurrent ancestor-lock interference is a plausible cause, not a proven
production defect. No backup permission/sharing/check was weakened. Run this
denial-of-write fixture separately from other workspace writers.

Next bounded action: exercise the new applied-state policy in owned memory
and reconcile static guard contracts separately from custom-row retention
and exact-candidate game acceptance. No package, deployment, push or
publication occurred. Localization impact: no player-facing text/meaning
change; only developer diagnostic wording and internal tooling changed.

### Candidate selection, offline acceptance and first deployed trial, 23 October 2026

This supersedes the preceding 85/89 preparation stage. The static inventory is
**89/89 MAPPED, 0 PARTIAL, 0 NOT CHECKED**. Four reconciliations are explicit
source contracts, not four newly discovered signatures: the exact load receiver
and applied-state policy with opaque byte forwarding; the complete observer
three-input/home-alias audit; constructor/check/full-copy marker fields; and
original-row D8=-1 checked at acceptance, with ordinal writers in copied rows.
Custom retention across every rebuild, event completion, network semantics and
exact-candidate gameplay remain independent acceptance gates. Static mapping
coverage is not release readiness.

The native profile now selects exact 7.06/build 25732212/hash 13D5060D... for
unpublished 0.10.3. The mapping entry permits controlled activation, while the
independent runtime guard continues rejecting unknown executable identities.
The public 0.10.2 package remains 7.05. Owner-authorized final offline results:
403 production tests, 807 developer tests; 63 runtime cases, 16 backup checks,
13 load-context cases, 28 menu scenarios; 31,216 policy /25,733 selector commands,
333 storage cases/721 operations, hook ABI checks and six unsupported-host runs.
Exact 213-byte filter parity SHA-256 is
95D2C565AFFA312A94493072258EBBE9FE531841D65065D71914332999DCE3EF.
Build directory: build/native-runtime-0103-cosmos706-r1. Its immutable
build/validation/package receipts and the 29-member archive readback passed.

The [candidate record](../release/0.10.3-COSMOS-706.md) preserves full identities:
r1 ZIP 3,725,241 bytes / SHA-256
543EBEB847DBF31C2344FB7D6F3E82AEEE5343CFE2B8CC64D1034DFA6ACC5AAA;
ASI 2,638,336 bytes /
A1AB7D0E8F9B6F0580882EA29CF82FF580E89BD436BFEF37E7363FFC94C0B78C.
No public upload or push occurred. Native source inputs and candidate byte
receipts are separate from subsequent documentation and live evidence.

The owner explicitly authorized installation and launch. A fresh closed-game
backup verified 61 save files +2 preferences, 63 files/8,688,127 bytes, with
protected current-user/SYSTEM permissions. The prior ASI was preserved privately;
all ten installed overlay hashes matched, and only the ASI changed. Existing
pinned loader/eight icons were reused. An initial File.Replace call failed
because PowerShell converted null to an empty backup path. The target remained
unchanged. Passing Language.NullString.Value completed atomic replacement;
one exact owned staging file was hash-checked and removed before launch.
Do not generalize this into bypassing loader-conflict or private-backup checks.

Normal Steam launch was verified as actual PID 70240, exact executable and
loaded candidate hash. A bounded read of the owned status export and its RIP
relative four-byte cell used VM_READ|QUERY_LIMITED_INFORMATION: 17 bytes,
no native call/write, status 4 (active). The fresh fixed process log independently
confirmed startup, pre-activation snapshot and hooks active at 07:46:40 UTC.
FileInfo briefly exposed zero log length; the first timestamp-filtered query
missed the log. Direct reading of its fixed process-specific filename returned
all lines. Do not interpret cached metadata or mixed DateTime kinds as no
initialization. Two WINMM modules are expected here: packaged proxy and Windows
system library; compare full module identity/hash, not the basename alone.

The owner confirmed the X-menu entry, settings/icons and a manual pet. Existing
Automation OFF was preserved. The owner switched it ON; file readback confirmed
persistence after menu closure. The immediate pre-closure OFF read was a timing
observation, not a failed setting change. First ship cycle retained the old pet
and was inconclusive. After explicit manual dismissal, a second cycle armed an
opportunity at 07:57:55.535 and accepted the queue at 07:58:01.413 UTC; the owner
confirmed visible automatic appearance. This is one completed local ship-exit
check, not location-matrix/multiplayer acceptance.

A separate main-menu reload with Automation ON produced no visible pet while
the owner was standing outside. The observer recorded reason 1 at returns
0x330314/0x330996, but no load-completion/opportunity line. The cause is unknown;
do not attribute it to eligibility, state, result or source byte without evidence.
The owner saved/closed normally for the next trial. No process was killed.
r2 now adds bounded check-mask/caller-RVA/Boolean diagnostics to load and filtered
teleport callbacks while preserving the original policy and forwarding. Its
build/package/live checks are pending. At most 16 records per path/process;
never print common-key values, private IDs, pointers or save paths.

Next bounded action: finish r2 offline gates and immutable packaging, fresh
closed-game backup/deployment, then capture one confirmed load and the filtered
teleport context if needed. Reconcile the first failed predicate using that
specific call; do not restart full-image signature discovery. No death,
multiplayer, second-PC or public-release claim follows. Player text/meaning
unchanged; developer diagnostics are English.

### Diagnostic r2 offline and startup receipt, 23 October 2026

The bounded diagnostic candidate r2 passed its build and serial full owned-host
bundle, including 16 context-mask cases, 63 runtime cases, 16 backup checks and
six unsupported hosts. Policy/selection/storage counts and the unchanged menu
inputs retain the preceding bounds. Its 29-member ZIP readback passed:
3,725,794 bytes / SHA-256
2FF7CB2CD3C4635C1D0B4CD7692090E2C61547CE8BB66E8EF7D5C3D0E9F49759;
ASI 2,639,360 bytes /
D631F345099C8E4A67C11C89BF69AD4A0F1CAA7DFFD8AB409E767B5D5037509B.
Full identities are in the [candidate record](../release/0.10.3-COSMOS-706.md).

After owner-confirmed normal closure, a fresh private closed-game backup
verified 63 files/8,758,888 bytes. Prior ASI privately retained; ten installed
overlay files verified, only ASI changed. Normal Steam launch was verified as
actual process 71332 with the exact r2 module. The native pre-activation receipt
verified the same file/byte count and protected permissions. Hooks active logged
at 08:11:09.718 UTC. The owner was asked for one normal load with no ship/manual
summon action; confirmation/results are pending. No game process was killed.

Policy and original forwarding are unchanged. Diagnostic masks identify the
first failed predicate; they are not an event/MP classifier. Pending bounded
action: read that actual callback's caller/masks/result/key-presence predicates,
then repair only the supported failure and repeat affected gates. Static ledger
remains 89/89 source contracts with load and teleport gameplay gates open.
No public push/upload or release, no locale/player-text change.

### Measured load-timing correction and final r4 acceptance, 23 October 2026

This supersedes the pending r2 action. Static source inventory is now 90/90
MAPPED: exact local-load return 0x4906C2 is the fifth added policy input. r2
recorded a successful call at that return, zero source byte, matching receiver,
readable nonzero common key, and masks 0x0f before/after. The applied FSM state
was the first refusal. Position reason 1 followed later. Requiring a state seen
later in the load at this earlier callback was a new source-policy error.

The corrected guard requires the exact verified return, app+0xB940 receiver,
state vtable and stable identities, preserving original arguments/result,
opaque zero-only veto and deferred native readiness. The distinct known death
return cannot pass. The source/helper policy and schema include callback_return;
21 owned cases include the pre-applied-state positive control and foreign
caller/receiver/vtable/unstable-state negatives. Never reuse this RVA across a
new executable hash without revalidation. AGENTS and the mandatory playbook
now require actual callback-boundary timing evidence before adding predicates.

r3 passed 808 developer tests, full native bundle and 28 menu scenarios. The
owner saw a pet on station load: successful callback 08:33:29.895 UTC, deferred
opportunity 08:33:44.138, accepted queue 08:33:45.751. After manual dismissal,
station-to-base teleport created a distinct opportunity at 08:36:11.368 and
accepted queue at 08:36:12.948; visible appearance confirmed. Teleport's applied
state mask was 0x7f. This does not prove that the earlier unrecorded r2 trip was
refused by the state guard. r2 after-state reads independently established a
station, reason 11/phase 0, no active/queued pet; they did not capture a callback.
The extra unverified FSM restriction on experimental teleport was removed to
preserve its baseline filter. Temporary other-return sampling added no new
caller evidence and was removed from final r4.

Final r4 ZIP dist/CompanionAutoSummon-0.10.3-native-test.zip is 3,725,947 bytes /
SHA-256 DF7CF87276391A9DC9BDF596611563B3787530DA5D5C0107F51BB994F580B3F2.
ASI is 2,639,360 bytes /
6474247C07E7659EFC6E4FC698A1E7CDF9471C3EC471656675A251FF5FE96652.
Full 29-member/ten-overlay readback passed; its immutable r4 build/bundle
receipts passed, including 21 context cases, 63 runtime cases, 16 backup checks,
hook ABI and six unsupported hosts. The unchanged menu input hashes match the
passing r3 report: 28 scenarios/213-byte filter parity. No player UI/catalog
meaning changed. Full artifact/receipt hashes are in the release record.

After owner-confirmed normal closure, a fresh private closed-game backup
verified 63 files/8,783,300 bytes, protected current user/SYSTEM. Previous ASI
privately retained; only ASI changed; all ten installed hashes matched.
Actual process 36728 loaded the exact final ASI, completed a matching private
pre-activation snapshot and logged hooks active at 08:42:44.348 UTC. The owner
confirmed final load appearance and settings/icons, then manually dismissed the
pet before base-to-station teleport and confirmed a new pet. Final native log:
load 08:43:43.684 with masks 0x16f/0x16f, deferred opportunity 08:43:57.706,
accepted queue 08:44:24.417; distinct teleport opportunity 08:46:27.944 with
mask 0x7f, queue accepted 08:46:29.560. Queue logs corroborate the named owner
confirmations; they do not alone prove appearance.

Local checkpoint 63236a1 retained r1/r2 source/evidence with core@lineum.io;
corrected source and final receipts still await release checkpoint/synchronization.
Canonical remote main was freshly read as f7d97b61; no open port PR was returned.
Fresh authenticated Nexus readback still showed 49469/0.10.2 Main Primary.
Next: commit corrected source/release identity, fast-forward remote main and
branch without rewriting, verify remote heads, upload this exact archive, then
record file ID/status/readback. No upload/push has occurred yet. Multiplayer,
second-PC, death/respawn, full location matrix and long-session acceptance remain
NOT CHECKED; no stable/general event-safety claim. Do not modify active game
runtime or immutable candidate receipts to record these later observations.


## Publication, scan comparison and reproducible build handoff, 23 October 2026

- Exact game remains Windows/Steam Cosmos 7.06 / 25732212, executable SHA-256
  `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
  Static inventory is 90/90 MAPPED; this pass adds no new mapping or live trial.
- Final source `852c5c55458c563a8564090dd31305864483edf3` was read back on
  remote main and compatibility branch before upload. Frozen r4 ZIP SHA-256
  `df7cf87276391a9dc9bdf596611563b3787530da5d5c0107f51bb994f580b3f2`,
  3,725,947 bytes, was uploaded to Nexus as **50040**, Main / Primary.
  Public version, target, summary and full description were saved/read back.
  File 49469 remains under Old files. **Quarantine prevents new download.**
- GitHub prerelease 421642329 / v0.10.3-native-test points to that exact source.
  Binary upload is on hold; no binary delivery/readback is claimed.
- New ZIP/ASI scans are 10/67 and 10/71 (23 October). Rechecking the unchanged
  old 0.10.2 ZIP found 28/68 in its 15 October report, superseding the dated
  1/67 snapshot. Earlier Nexus acceptance is not current scanner clearance.
- Read of the old ZIP failed before decoding: Python Errno 22; independent
  PowerShell reported an OS malware/PUA block. Record TOOL ERROR / blocked
  input, not a match result. Explicit CPython 3.11.9 and pefile 2024.8.26 were
  rechecked. No restore, exclusion, alternate-copy access or protection change.
- Old/new build receipts have the same compiler hash, dependency lock, vendored
  input hashes and imported DLL names. New ASI is only 2,048 bytes larger.
  Source deltas are mapping/load checks, diagnostics and label forwarding;
  no exact detector cause or verified source defect is established.
- Fresh `build/native-runtime-0103-provenance-20261023` from unchanged r4 inputs
  reproduced **all products exactly**. ASI remains
  `6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652`.
  Receipt SHA-256 `4e8d132e64c8244da7f7e717c1e3c38387001e264bb3dcbb877da42dab1fe18a`.
  This corroborates provenance, not antivirus clearance.
- The reusable read-only comparison is `tools/audit_native_archives.py`;
  `docs/research/NATIVE-0103-SCAN.md` records commands, identities, blocked-read
  correction, results and limits. README/Known Issues/Nexus mirrors separate
  actual final gameplay, candidate history, publication and availability.
- Owner declined support contact and requested internal diagnosis. The request
  remains unsent. No modified artifact was packaged/uploaded to change a scan.
  Death trigger, multiplayer isolation, second PC, broad input/location matrix
  and long-session acceptance remain NOT CHECKED / unsupported as documented.
- Next bounded step: establish a concrete unintended source/build behavior or
  packaging defect before changing native code. If no defect is found, a local
  rebuild cannot change the host verdict. Preserve hashes and accurately keep
  Nexus distribution open until actual clearance/download readback. Recheck
  current versus old exact-file scans before drawing a regression conclusion.


### Final description and provenance follow-up, 23 October 2026

Public Nexus file 50040 was rechecked later the same day and remains
quarantined. The current description was read back with exact 7.06/build,
actual local acceptance, scan findings, current Known Issues and complete
selection/install/removal/credit text. Legacy release tags and Translation
were removed; English, functional tags and AI disclosures were retained and
publicly read back. GitHub About remains accurate. GitHub prerelease body
now states quarantine and absent binary assets, and matched API readback.

The exact ASI Behavior report uses non-NMS DLL harness hosts. Two displayed
URLs are memory-pattern strings: the redistributable address is retained
catalog text in `.rdata`; the LLVM address is compiler/debug metadata.
Neither is proof of an executed download. The bounded Activity Summary has
no sandbox detection or dropped-file result, with one UDP observation whose
module attribution is unproven. Antivirus verdicts remain unresolved; do not
promote this to clearance or a confirmed false positive.

Read-only audit tool SHA-256:
`1e8caca258913e9a92e0f6a80e44f77ae822f00302305333e70fe5b6f0725e82`.
Audit JSON SHA-256:
`1eddd1f7dbc10a666175d91fd183323fee06e563265c4372f6758f830493df50`.
COFF symbols/string table account for the 647,168-byte PE overlay, with only
zero alignment padding after it. No exact detector source or concrete native
regression was established by this pass. Source input hashes remain identical
to the accepted r4 receipt; all documentation links resolve. No native code,
package bytes or installed runtime changed during this publication audit.

The remaining gate is distribution/scanner acceptance, separate from the
completed bounded local functional checks. Support contact remains declined.
Keep the exact artifact and findings; change native/build code only for a
substantiated defect, and read back actual host/download acceptance before
claiming completion. Wider runtime gates remain explicitly NOT CHECKED.

### Retained-file correction and security audit handoff, 23 October 2026

- Base source e007688349dec1c63e2adc9ab01759c65b92d7e8, branch
  compat/cosmos-706-25732212. Exact 7.06 / 25732212 executable remains
  `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`;
  mapping coverage remains 90/90 MAPPED. No game, mapping, native input,
  immutable r4 artifact/receipt or deployment changed in this work period.
- The owner noticed 0.10.1 in Main while 0.10.2 was Old. The latter was moved
  automatically by the update replacement; the former was an overlooked Main
  entry. File 49367 was changed to Old and public categories read back:
  Main only 50040; Old 49469, 49367, 49202. Both 7.05 releases still show
  download links; no downloaded-byte verification or new old-file read occurred.
- Exact 0.10.1 ZIP report is also flagged: 22/60, analysis 15 October
  11:37:05 UTC. Its attempted reanalysis did not yield a new date/result.
  Do not treat a download link, green historical Nexus icon or Old category
  as current scanner clearance or infer a 7.06 source regression from them.
- The unchanged final ASI's accepted reanalysis completed at 23 October
  14:33:20 UTC as 15/63, superseding 10/71 at 09:09:51. No new upload/rebuild.
  ZIP reanalysis NOT CHECKED; its separate 09:06:05 report remains 10/67.
- Reviewed initialization/rollback, host guard, binding/MinHook memory and
  storage/backup I/O, plus 0.10.1-to-0.10.2 source delta. No demonstrated
  new payload, concrete unintended behavior or exact detector cause found.
  All 9,053 installed toolchain files match the original official archive;
  current GitHub asset digest matches the pinned ZIP. Receipt SHA-256
  `713d2aa6d2ec398ea1834b013c2778963f0bbc0f3a4a23e5df91f49aef55bacd`.
  Extra installed files, environment and independent compiler/source rebuild
  NOT CHECKED. Provenance is not clearance. The scan record preserves the
  standard-library algorithm, interpreter hash, exact source/API commands,
  completed versus unsuccessful scan attempts, and interpretation limits.
- Current Nexus official procedure requires moderator review to clear an
  already quarantined file; no owner control was found. Contact remains
  declined and unperformed. Next actual distribution evidence needs host
  clearance and a verified download. A future native/build change needs a
  substantiated engineering defect; repeated byte changes are not a remedy.
  Wider game acceptance remains NOT CHECKED as previously documented.
- Public Nexus description was updated and read back with 15/63, the toolchain
  result and retained-file targets/categories. GitHub prerelease body matched
  API readback with the frozen source target and zero binary assets. SCEditor
  fill alone left Save disabled; an actual keyboard edit restored to exact
  source text enabled it. Preserve that failed-method correction in the release
  gates; visible editor contents alone do not prove persistence.

### Audit completeness and query-error handoff, 23 October 2026

- Source base 73a9f6e273ebdecbe4d74323b2f1b56cf9cb0b38; exact game remains
  7.06 / 25732212 / `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
  The 90 mapped roles and frozen r4 native inputs/receipts are unchanged. No
  player module, mapping, vendored source, package, deployment or live test changed.
- Technical analysis is not exhausted. Current file-set check has 9,053 files,
  zero extra/missing and eighteen compiler override controls absent/empty.
  Historical environment and independent clean-host reproduction remain open.
- Clang 23.1.2 default analysis completed nine C++ and four MinHook C units:
  two diagnostics, reviewed as a dead initialization and a modeled null patch
  path not reproduced in CAS. No broad safety or detector-clearance claim.
  Analysis receipt SHA-256
  `d28d7e5f9e01729befff1832e2110c6c0436671cbff1d8c01c5958db640775fd`.
- Follow-up review found a separate real error contract issue: MinHook's
  IsExecutableAddress ignores a failed VirtualQuery before reading its output.
  Owned fixture `tools/research/minhook_query_failure_host.cpp` demonstrates
  failed-query/stale-executable output incorrectly accepted by unchanged code;
  both ordinary success controls behave as expected. Baseline exits 1.
  Canonical LF fixture SHA-256 `4124e7f87bde52b7b8f07d7066a9ec5ffaa7945264e1fd80b600aa4d7d2ff046`;
  the scan record also retains the line-ending-equivalent executed-copy hash.
- Minimal return-size guard in a separate buffer.c copy passes all three cases.
  Prototype receipt `ef3131003d11525b215e4dd818b189acfa205b5b804f4fb0816bdeaa48cbf0ef`.
  First aggregate-initializer prototype failed strict C++ fixture compilation;
  record it as a build/tool error. No production patch has been applied.
- This is a pre-existing robustness defect, not evidence that NMS encountered
  the error, an exact detector rule or a 7.06 regression. The scan record now
  preserves the API contracts, commands, source/receipt hashes and bounded
  completed/open table. Do not treat a discovered defect as scan clearance.
- Next: integrate a provenance-tracked guard only as a distinct candidate with
  real C-build and owned-hook/runtime regression validation; obtain a clean-host
  r4 reproduction and inspect available per-process sandbox attribution.
  Exact detector cause and distribution acceptance remain open. Support contact
  remains declined; wider game/multiplayer/second-PC gates remain NOT CHECKED.

### MinHook guard integration handoff, 23 October 2026

- Base `760f74db2a5fbc709d4103304efa917a55c4a98f`, branch
  `fix/native-query-guard`, distinct candidate 0.10.4-native-test. Installed game
  rehash is unchanged: 7.06 / 25732212 / 88,560,712 bytes /
  `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
  Native mappings, 90 source-derived role entries and game consumers are unchanged;
  reuse their exact-hash evidence. The affected dependency is MinHook's query
  error path; no new game RVA/pattern claim is needed or made.
- Integrate only the proven full-result guard; patched buffer.c SHA-256
  `3a9b2f7a1fb084e72897acd8095d4325ab03545669b5b43d89d13ea71d113035`.
  Keep upstream and local identities and packaged notice disclosure. New
  dependency validator reverses the patch to upstream before build/package.
- Local r1 build receipt `e2b32cb1cac41c175b8d76e7f8ba4cfac9399914157dc8107e18f812b9e76f1e`;
  ASI `765cdbdf0e99aea433fd977048b38f0cd28ccbe6c26902c511310a3ee9523ffa`.
  Sixteen real-C query cases and ten owned-hook ABI groups pass; 403 production,
  820 developer tests and 28 menu cases pass. Full bundle pending: unchanged
  backup driver refused its first directory hold with Windows error 32 before
  any completed backup check. Preserve that failure and retry once on fresh
  isolated fixtures; never weaken source/destination locks or ACL checks.
- New clean Windows workflow compares frozen r4 source and the candidate using
  commit-pinned official actions and hash-checked compiler, retaining JSON only.
  Actual independent run/readback is pending; same-PC results are not independent.
- Full methods/commands/source identity and failures are retained in
  NATIVE-0103-SCAN.md and docs/release/0.10.4-QUERY-GUARD.md. Next: complete
  bounded backup discrimination, independent CI comparison, then allowlisted
  candidate packaging. Fresh exact-candidate game acceptance and scanner status
  remain NOT CHECKED. No player wording, meaning or catalog values changed.
  Frozen 0.10.3 bytes/status remain intact; detector attribution, sandbox UDP
  attribution, multiplayer/second-PC/wider live gates remain open. No contact.

### Independent reproduction and completed offline guard handoff, 23 October 2026

- Candidate source checkpoint `7fd4bc09a3185a214a808052da61f2223999619b`;
  branch `fix/native-query-guard`; module/native input checkpoint
  `55164191f11168cce31cc05b558498925b14c630`. Exact game/mappings and 90-role
  evidence are unchanged. Preserve the explicit cache/input scope above.
- Completed 403 production and 828 developer tests, 28 menu cases, sixteen real-C
  query cases, ten owned-hook ABI groups and the full native bundle. Backup
  passed all sixteen refusal/integrity cases on an explicit owned temporary
  volume with unchanged production locks/ACLs. The original C: root sharing
  conflict and both failed receipts remain recorded; this does not verify a
  current real-save/pre-activation backup on that original volume.
- Clean GitHub Windows run 39982338490 reproduced every frozen-r4 and candidate
  product byte at the historical source prefix. Initial differing hashes were
  traced to the JSON assertion's UTF-16 absolute source path; source receipt
  differences were exactly CRLF/LF. Never treat a raw cross-machine hash mismatch
  as a payload change without resolving paths/line endings and generated inputs.
- The clean run also exposed a test-only literal-SID assertion rejecting valid
  LA alias rendering. Corrected validator compares actual token/trustee SIDs,
  exact allowed/full-access ACEs and root protection; eight new tests pass.
  Production backup is unchanged. Final corrected CI run is pending readback;
  frozen old-validator failure must stay explicit, not rewritten as a pass.
- Frozen new ZIP: 3,726,390 bytes /
  `70d85b240e90b8bafa524036bd4fccc7f58684d10bc93b13c2d0369e6e8d1c39`,
  29 members / ten overlay files. ASI remains
  `765cdbdf0e99aea433fd977048b38f0cd28ccbe6c26902c511310a3ee9523ffa`.
  Full receipts, commands and environment limits are indexed in
  docs/release/0.10.4-QUERY-GUARD.md. Preserve all frozen 0.10.3 bytes and status.
- New ASI hash-only VirusTotal lookup returned Item not found, not a clean scan.
  New ZIP/ASI upload awaits explicit browser-upload confirmation. No deployment,
  new-artifact game acceptance, upload or support contact occurred. Next bounded
  steps: corrected CI readback and, if authorized, exact-candidate scan; then
  fresh verified real backup before any player-assisted game trial. Detector and
  sandbox UDP attribution, Nexus acceptance and broader live gates remain open.

### Final clean-runner and archive handoff, 23 October 2026

- Corrected clean Windows run 39983965743 succeeded for both source jobs at
  `7fd4bc09a3185a214a808052da61f2223999619b`. Candidate standard bundle passed;
  both exact ASIs reproduce byte-for-byte at the historical source prefix.
  Frozen-r4's original SID-string assertion remains explicitly false, followed
  by sixteen corrected identity/ACL checks on byte-identical backup code and
  six foreign-host checks. This is not second-PC NMS gameplay acceptance.
- Independent summary hashes: candidate
  `b7135fedd34a778d072a15dca91cde8e553112c5b3ea87d7e230ef3d483e2c23`;
  r4 `b3c1308f6c806d5f86e74072b801eba21faf65fcfa717c59e9117e3e6fb10ba2`.
  Archive delta receipt `b934bf91c280c3fea327f1420d967f0a515302eca3648d1a1b5f0f63c169538a`
  confirms unchanged loader/compiler/imports/exports and no W+X image sections;
  four expected package members changed, none added/removed.
- Exact new ZIP/ASI upload and service terms are now explicitly authorized.
  Upload/result readback is pending, not scanner clearance. Prepare the upload
  form and bundle foreseeable file/sharing/terms confirmations before asking
  next time; the first premature question caused an avoidable second prompt.
- Latest direct Nexus readback still shows 0.10.3/file50040 quarantined, with
  0.10.2 and 0.10.1 under Old. No Nexus replacement, game deployment or support
  contact occurred. Temporary owned R: mapping was verified and removed.
  Next: finish exact-file scan readback, then require fresh real backup and
  player-assisted exact-package acceptance before any publication claim.

### Repository-only continuation and backup collision, 24 October 2026

- Source code base `7fd4bc09a3185a214a808052da61f2223999619b`, branch
  `fix/native-query-guard`; pending changes at this checkpoint are documentation
  and an original read-only metadata helper. Rehashed game remains 7.06 /
  25732212 / 88,560,712 bytes /
  `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
  Frozen 0.10.4 ZIP/ASI still match their existing receipts; no native mapping
  or 90-role cache input changed in this resumed pass.
- Manual VirusTotal attempts did not establish server acceptance or a completed
  scan. Both exact hashes initially returned Item not found. The UI showed
  failed reCAPTCHA connectivity and then a checkbox; the owner reports five
  failed challenges. Stop this optional route; use the release host's own file
  review after a functional candidate, without treating a queued upload as a
  clean scan. The ZIP UI also warns that the 3 MB/multiple-member condition
  prevents its stated inner-file scan. Do not repackage merely to change that.
- The prior reload was not executed: automatic approval review failed because
  account usage was exhausted, not because it classified the action unsafe.
  Browser access worked again on 24 October. No scan outcome was obtained.
- A read-only root-lock preflight still failed with Windows error 32. Original
  helper `tools/research/native_root_handle_audit.py` used extended handle
  metadata, matched volume/file identity and reported only matching process
  basenames. It read no target contents/process memory and closed no source
  handles. One accessible matching writer was Lenovo-signed VaultPlugin.exe,
  parent SmartConnect, in Lenovo Ready For Assistant. 119 inaccessible processes
  remain an attribution limit; one match does not prove there is no other holder.
  Helper SHA-256 `21b41afe5ab302010a4aa32685a69f8e7465f41c17923dcc3913f528f329f150`.
  Layout reference: MIT-licensed winsiderss/phnt commit
  `53fbbdc5b5d2b08761db1c7b26bfa8c820924356`, ntexapi.h; no phnt code is compiled
  into the player package. The native backup's read-only ancestor hold denies
  existing write sharing even at the entire volume root.
- The owner briefly authorized normal Smart Connect closure; opening its UI was
  confirmed, but the close action returned a foreground-process-id error.
  Closure was NOT verified. The owner then explicitly withdrew desktop control.
  **Current constraint: repository code/documentation and owned offline fixtures
  only. Do not control browser/native apps, close processes, deploy or start NMS
  without a new direct instruction.** Do not repeat CAPTCHA requests.
- For the backup code remedy, Microsoft documents NTFS's requirement that a
  directory be empty before attaching a reparse point. An isolated owned fixture
  confirmed empty-directory mount-point creation and nonempty refusal/error145;
  no real volume root was changed. Receipt SHA-256
  `a8828c258c3fb4d6b2444aa43df4c1920dbd4d24b4c425d5673ce6c02911f7c6`.
  This is a bounded NTFS observation, not permission to relax all ancestor locks.
- Next bounded implementation: test a volume-GUID-anchored NTFS root guard with
  a strictly held first child; preserve actual source/destination ancestor and
  file write/delete refusal, ACL, inventory and hash checks. Unknown/empty-root
  cases retain strict refusal. Do not overwrite the frozen 0.10.4 candidate;
  any changed production artifact needs a distinct identity and its own checks.
  Nexus file50040's last direct readback was still quarantined on 23 October;
  no newer listing, actual download, 0.10.4 live acceptance or detector cause is
  established. The backup collision and antivirus quarantine are separate gates.

### Antivirus-priority cross-compiler handoff, 24 October 2026

The owner redirected work to antivirus/Nexus publication. Backup prototype
c23b417 is parked separately and is not part of the active source; current
research/native-antivirus-attribution starts at a55a362. Native 0.10.4 inputs,
exact game hash, 90 game-specific roles and address mappings are unchanged.
Desktop/app/browser control remains withdrawn; code, documentation and owned
isolated checks only. No support/vendor message is authorized.

Public primary-source review found reports about different historical compiler
DLLs and a wrongly downloaded UAL source archive, not a detector explanation
for this ASI. Nexus explicitly separates file-type, archive and scan gates;
quarantine clearance needs host review. Manual VT attempts remain unconfirmed.
See NATIVE-0104-SCAN.md for precise artifact identities, sources and limits.

Next bounded action is a signed-Microsoft-toolchain source audit on an isolated
GitHub runner. It uses a distinct diagnostic version, records the two-site
return-address adapter and retains only JSON evidence. The production packager
rejects the diagnostic identity. It is not an AV-evasion rebuild, scan result,
new game mapping or new player release. Read back compilation/static diagnostics
and owned tests before drawing conclusions. Scanner cause and Nexus acceptance
remain unresolved; no global safety or false-positive claim is made.


### Microsoft audit, artifact integrity and current quarantine handoff, 24 October 2026

- Source base/research branch: `1f08e37df8d046d02f193cb05b245cbd8a3189a9`,
  `research/native-antivirus-attribution`. No native/gameplay, profile, locale,
  dependency or package byte was changed. The recorded exact game is 7.06 /
  25732212 / `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`;
  no installed-executable inspection or new game-compatibility claim occurred.
- Read back successful isolated Windows run40083974784/job120843032853. Signed
  MSVC19.44.35229.0 compiled/analyzed nine C++ units and compiled four vendored
  C units. All sixteen build/inspection commands and the full owned bundle
  passed. Verified all 88 source input hashes and the compiler/build/validator
  receipt chain. Sanitized durable evidence is `NATIVE-0104-MSVC-EVIDENCE.json`,
  SHA-256 `1ae44da169bcaf8b0b7494487dd85a969420a01213935204be4f7936793a2aaa`.
- Triaged eighteen distinct diagnostics/six codes: guaranteed first decoder
  assignment, deliberate byte/bitfield representations and zero fill, explicit
  texture alignment, local shadowing, and 64 KiB buffer/path stack use. General
  stack headroom and all arbitrary decoder inputs are NOT CHECKED. No new
  concrete AV cause or general safety proof was established. Preserve the
  separate diagnostic identity; do not substitute its smaller binary for a
  player release. See `NATIVE-0104-SCAN.md` for the bounded dispositions.
- Rehashed the complete frozen 0.10.4 ZIP, all 29 members, manifest, module and
  loader against their original receipts. ZIP remains
  `70d85b240e90b8bafa524036bd4fccc7f58684d10bc93b13c2d0369e6e8d1c39`;
  ASI `765cdbdf0e99aea433fd977048b38f0cd28ccbe6c26902c511310a3ee9523ffa`.
  Source/mapping cache inputs and the 90-role denominator are unchanged.
- Direct current Nexus readback: file50040 / 0.10.3 remains quarantined and the
  sole Main file; 49469,49367,49202 are Old. The public search snapshot returned
  stale 0.10.2 data; plain HTTPS was challenged. A hidden in-app browser supplied
  the actual current listing after the owner conditionally reauthorized computer
  control when another route is insufficient and it will not disturb them.
- Existing 0.10.3 ZIP report still shows 10/67, completed 23 October09:06:05UTC.
  New 0.10.4 ASI hash lookup returns Item not found. No new scan, upload, CAPTCHA,
  installed-runtime change or support/vendor message occurred. The earlier
  support-contact refusal remains effective; computer-control authorization
  does not authorize messages.
- Next bounded action: submit the current source-backed moderator-review draft
  only after explicit owner authorization. Official Nexus policy requires staff
  review to remove an existing quarantine. Draft:
  `../release/NEXUS-QUARANTINE-REVIEW-20261024.md`. Keep the submitted bytes and
  request the specific failed gate/review requirements. Scanner acceptance,
  private detector-rule/UDP attribution and exact 0.10.4 NMS gameplay remain
  separate unresolved/NOT CHECKED gates. Backup work remains parked; do not
  confuse that runtime gate with antivirus quarantine.


### Internal-first antivirus attribution and actual scanner evidence, 24 October 2026

- The owner corrected the proposed next step: support/vendor contact is a last
  resort after available internal analysis. No email was sent. The review draft
  remains a contingency; AGENTS.md and release gates now preserve this direction.
- Research base before this continuation was 3783eeb. Scanner orchestration is
  at 74056977e3d0e8fc30be2e60e481343355665f2d; no native source/profile,
  localization, game mapping or frozen player package changed. Exact recorded
  game target remains Windows/Steam 7.06 / 25732212 /
  `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
  The 90-role mapping cache is unchanged; no installed game was inspected.
- Full CAPE/Zenbox reports supplied evidence absent from the grouped summary.
  Of 357 nonempty CAPE API records, 344 first caller addresses fall in the
  reported rundll32 image; thirteen are other modules, zero are the target.
  Exception-filter and token API callers were positively assigned to the host
  executable. Five HTTP requests use CryptoAPI and certificate CTL/OCSP endpoints;
  no packet PID/call stack ties them to the ASI. Zenbox UDP still lacks module
  attribution, and its per-process details are None. The full Zenbox report
  says Non Malicious 4/100 and includes an unsigned-rundll32 Sigma label; the
  earlier grouped no-Sigma statement is explicitly bounded/corrected.
- Hash-matched submitted ASI has Security directory0/0 and Windows status
  NotSigned. Its TLS callback list begins with a null qword at RVA0x13E298,
  so the displayed pre-entry-callback label does not prove an executed callback.
  Preserve the static fields, report ranges and interpretation limits in
  NATIVE-0104-BEHAVIOR-EVIDENCE.json, SHA-256
  `a28d6c1bf0076ba6c9c1e1da726716b8ec7c13de187b1b35e8d22113e8fc7049`.
- Actual completed scanner run40089173239 reproduced each exact ASI, then used
  the signed active Defender scanner4.18.26090.9 / engine1.1.26090.9 /
  definitions1.461.181.0 (24 October05:51:57UTC). Both original6474247c... and
  candidate765cdbdf... returned no threats/exit0 with unchanged post-scan bytes.
  Each runner first detected the official harmless EICAR control in the same
  documented read-only custom-scan mode. Global policy digests were unchanged;
  no game, customer data or local-PC security setting was accessed/changed.
  Automatic antivirus cloud transmission is NOT CHECKED; no explicit workflow
  binary upload occurred. Durable sanitized evidence:
  NATIVE-0104-DEFENDER-EVIDENCE.json, SHA-256
  `a12dce3dc3c9a361721714f1ba0c7979e21f6ccaf4b5c6d4caf916d67bcfdb84`.
- Retain all six failed attempt receipts: ambiguous CurrentVersion alias, stock
  path exclusion, and exclusion-removal attempt whose effective check still
  said excluded. None scanned an input. The final method uses documented
  read-only custom scanning, whose findings are in stdout and whose file
  exclusions are ignored, plus a real positive engine control. Never promote
  an excluded input, zero process error, or absent UI/event result to clearance.
- Tools: CPython3.11.9 executable SHA-256
  `5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec`;
  pefile2024.8.26; PowerShell AST validation passed. Exact source pins, commands,
  scanner hash, receipt digests and failed methods are in NATIVE-0104-SCAN.md
  and the dedicated Defender workflow/script. Raw logs and signed report URLs
  are not published. No player UI meaning changed.
- These results do not identify the private Yogi/Loader rule or demonstrate an
  antivirus benefit from the MinHook repair: both inputs have the same bounded
  Defender result. Whole ZIP/loader scan, fresh candidate multivendor verdict,
  exact-candidate NMS acceptance and Nexus download acceptance remain open.
  Next bounded gate is comparable exact-candidate evidence from the engines
  reporting detections through an available authorized scan route; do not
  repeat failed CAPTCHA flows or vary artifact bytes merely to reduce alerts.
  No support contact is currently the next action.

### Paired antivirus evidence and candidate attribution handoff, 27 October 2026

- Target remains Cosmos 7.06 / Steam build 25732212 / executable SHA-256
  `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
  Existing native ledger states are unchanged. This period adds scanner
  evidence, not executable mappings, runtime verification or activation approval.
- Exact frozen 0.10.4 ASI, source 7fd4bc09..., hash 765cdbdf..., completed its
  prior authorized VirusTotal upload: 17/70 at 27 October 07:47:26 UTC.
  Submitted 0.10.3 ASI, source 852c5c55..., hash 6474247c..., completed
  reanalysis: 30/70 at 07:50:46 UTC. Same 75 vendor rows include one timeout
  and four unsupported results. No claim of identical engine definitions,
  repair-caused improvement, confirmed false positive or scanner clearance.
- Candidate CAPE All table: 358 nonempty API rows; first callers 344 inside
  rundll32, nine outside both known images, five zero and zero inside the ASI.
  Positive export resolution is ordinal 1 -> sample RVA 0x90E0/CasInspectHost,
  not ordinary InitializeASI activation at ordinal 3. Token-query callers
  resolve to rundll32 RVAs 0x62E5/0x6339/0x6435/0x6282. Four CryptoAPI HTTP
  requests lack module attribution. Zero logged sample callers does not prove
  that no sample instruction executed or that ordinary NMS use is safe.
- Exact candidate PE rechecked with CPython 3.11.9 / pefile 2024.8.26:
  no certificate table, first TLS callback qword zero, no parser warnings.
  Method: capture the visible All table, verify input SHA-256, then compare
  each first caller to host/sample image ranges using exact PE SizeOfImage.
  No module execution or game access was involved. Durable evidence:
  NATIVE-0104-VT-EVIDENCE-20261027.json, SHA-256
  `d3eaab4e3546af9ae56ff826097c252f72ef34a6a84d494b33ce4b2f69173237`.
- Candidate ZIP selected but submission rejected by automatic approval review
  after the archive-scan-limit warning; scan is NOT CHECKED. Existing loader
  0/49 report is dated 22 October and has timeouts/failures. Nexus 50040 is
  still the sole Main file and quarantined. No source/profile/locale/installed
  file/security-policy change, game launch, deployment or support contact.
- Zenbox subsequently completed with 4/100 Non Malicious for the exact
  candidate, timestamp 27/10/2026 07:55:35, timezone unspecified. It invokes
  InitializeASI as well; CAPE's ordinal-1 limitation is not a Zenbox conclusion.
  Ten per-process Extra Info entries show None. Filename mismatch follows
  provider renaming; seven of the 15 PE sections are debug sections. Overlay
  bytes are fully accounted for by COFF symbols/string table/zero padding.
  URLs map to VC runtime diagnostic text and LLVM debug metadata. The private
  Yogi/Loader rule and UDP/suspended-process attribution remain unresolved.
- Next useful attribution evidence needs actual rule/offset or module-resolved
  events for the unchanged hash, beyond these public reports. No production
  repair follows from generic labels alone. Exact-candidate game acceptance
  and Nexus/download acceptance remain open. Two GitHub label searches timed
  out (TOOL ERROR); broad web label searches found no attributable rule.

### Further IAT/source and vendor-report handoff, 27 October 2026

- Cosmos7.06 / Steam25732212 / executable SHA-256
  `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`
  remains the target. No game binary decode, mapping/locale/source behavior
  change, game launch or new compatibility claim occurred. Frozen package
  identities remain distinct: 0.10.3/source852c5c55/ASI6474247c and
  0.10.4/source7fd4bc09/ASI765cdbdf.
- tools/research/audit_native_import_refs.py now provides hash-first static
  IAT-reference attribution with exact COFF symbols and chained unwind roots.
  Tool SHA-256 `93a6015492baf1b969c9e540e7637dde9acbcf6dc558743e14ebbbfdf86a6ce6`;
  CPython3.11.9 / pefile2024.8.26 / Capstone5.0.7. Use --image,
  --expected-sha256, --output. Correct-hash reproduction, known CreateThread
  reference and incorrect-hash refusal before decoding/output all passed.
- All 2,384 physical exception ranges decode for both ASIs. Selected IAT
  reference records and named imports match exactly. Memory writes map to
  current-process menu data; MinHook supplies thread freeze/context operations
  and lock yields; CRT/libc++ supplies other waits. The dynamic constructor
  resolves GetSystemTimePreciseAsFileTime. No arbitrary dynamic-call or runtime
  argument/execution inference is made. No new concrete defect was found.
- Original hash's public Kaspersky report says Malware, Loader.sb/tvv,
  dynamic summary No data found. Candidate lookup has No search results.
  The exact tvv link redirects to generic Trojan class text. No attribution
  follows from either missing public data or premium example tables.
- Full sanitized receipts: NATIVE-0104-IMPORT-ATTRIBUTION-20261027.json,
  SHA-256 `112cf488d0bdf033ffceb769b8a91c39e046ddda84ed80f03e80cf0c87a99e7d`.
  The remaining private rule/event data, exact-candidate game acceptance and
  Nexus download acceptance are open. A refreshed review request is local and
  unsent; the owner must explicitly authorize the last-resort contact step.

### Owned-host runtime attribution handoff, 27 October 2026

- Target remains Cosmos 7.06 / Steam 25732212 / executable SHA-256
  13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
  This pass runs exact owned ASIs in isolated CI, not a game executable. No
  mapping, profile, player source/locale, installed file or save changed.
- Run 40579107862/controller fd532ac reproduced source 852c5c55/ASI 6474247c and
  source 7fd4bc09/ASI 765cdbdf unchanged. Both passed 16 extra plain initialization
  repeats and four paired plain/instrumented modes. Compiler signature/hash,
  Frida 17.24.3 wheel pin, exact disk hashes and actual OS exit 0 are recorded.
  The controller and host independently refuse unrelated execution contexts.
- Exact direct selected caller evidence: CreateThread from ASI RVA 0x140E,
  creation flags 0, returns success; host reports unsupported status 2. Other
  selected direct ASI dangerous-operation labels were not observed in these
  modes. Indirect/system-library behavior and active game hooks are outside
  this scope; host hooks_active=false is a contract, not an independent hook scan.
- Both baseline terminal-callback failures from run 40576805956 and the single
  original full-stack initialize timeout from run 40577586888 remain incomplete.
  Direct cached-module-map attribution avoids stack walking/module enumeration
  in critical callbacks. Later success does not identify the earlier timeout.
- Evidence: NATIVE-0104-OWNED-TRACE-EVIDENCE.json, SHA-256
  `4d15608c308c8b2d059f716d27765ec254d0cd51f829126bb890e29544e24b8f`;
  method/commands/pins/limitations in NATIVE-0104-OWNED-TRACE.md. No binaries or
  raw logs are committed; no owner-PC tool install, protection change or contact.
- Internal analysis is not declared exhausted. Next bounded independent step:
  owned active-hook transitions with appropriate instrumentation controls.
  Full UAL lifecycle, active exact-candidate game acceptance, private detector
  explanation and Nexus download acceptance remain separate open gates.

### Microsoft build candidate handoff, 27 October 2026

- Autonomous antivirus-blocker work now includes a maintained Microsoft build
  path, not only interpretation of public sandbox reports. Source base is
  3ea3eff plus the two-call-site intrinsic/header and candidate CI/tooling diff.
- New package candidate is 0.10.5-native-test. Frozen original source852c5c55 /
  ASI6474247c and candidate source7fd4bc09 / ASI765cdbdf stay unchanged.
- Target stays Windows/Steam Cosmos 7.06 / build25732212 / executable SHA-256
  13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
  No game image is decoded and no mapping or gameplay policy changes. The two
  caller-filter roles keep the same level-zero call-site semantics.
- Candidate CI uses signed Microsoft tools, external full PDBs and two distinct
  build directories with a byte-identical DLL gate. Owned functional validation
  and a positive-control Defender scan precede binary retention. Local Python
  syntax, dependency provenance and fourteen 64-key locale checks passed.
- Compilation/reproduction/runtime/scan results are NOT CHECKED until actual CI
  readback. Multivendor attribution, active hook/UAL lifecycle, exact-candidate
  game acceptance and Nexus acceptance remain separate unresolved gates.
- Reproducible commands and remaining gates: NATIVE-0105-MSVC-CANDIDATE.md.
  The next bounded action is CI build/readback, then exact-file multivendor
  comparison if the build and functional gates pass. No support contact.
