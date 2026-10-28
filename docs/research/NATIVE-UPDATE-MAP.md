# Native game-update mapping guide

This guide records a repeatable way to investigate a new No Man's Sky executable
before changing Companion Auto Summon's native compatibility profile. It is a
research workflow, not permission to reuse candidate addresses. The retained
Cosmos 7.05 case study is in [NATIVE-0705-COMPATIBILITY](NATIVE-0705-COMPATIBILITY.md).
Exact Cosmos 7.06 is now mapped and final r4 has bounded local acceptance in
[NATIVE-25732212-COMPATIBILITY](NATIVE-25732212-COMPATIBILITY.md). Source
checkpoint 852c5c5 is public; Nexus upload 50040 is quarantined, so distribution
acceptance remains open. Pattern discovery and its required evidence
ledger are governed by the [NATIVE-PATTERN-PLAYBOOK](NATIVE-PATTERN-PLAYBOOK.md).

## Keep game and mod versions separate

The game version/build, mod source revision, distributed mod package version,
and verified compatibility are four separate facts. A newer mod package number
does not mean that it supports a newer game build. Before recommending,
installing, or changing a release, record all four and compare the exact game
executable identity against that package's declared and verified support.

| Fact | Snapshot checked 12 October 2026 | Interpretation |
| --- | --- | --- |
| Installed game | Cosmos 7.06, Steam build 25732212; executable SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499` | The user's target game build |
| Public mod package | Nexus lists `0.10.2-native-test`; page checked 12 October and lists 3 October as its last update | Latest public package listing; mod release number, not a game version |
| Package compatibility | Cosmos 7.05, Steam build 25624745, executable SHA-256 `671de22649274b49fa07f5a246bc7252c4e08bb9ab623d2e65722fbab4e497a4`; last package evidence recorded 9 October | Does not establish support for 7.06 |
| Locally installed mod | Last checked 9 October: Nexus `0.10.2-native-test`, ASI SHA-256 `fd1faad297e52bb672f0f1b2b1e96b4b0e163db3b6c845f850e586e91d87dbb3` | Installed package identity; current local install was not rechecked on 12 October |
| GitHub source baseline | `main` at `f7d97b61fcf152677d0d30de34f6c1b48675c436`, read back 12 October | Source revision; not a distributed release or compatibility claim |
| 7.06 native compatibility | Not approved; exact-build guard remains fail-closed | Do not describe 0.10.2 as a 7.06 update |

For every future update, first write the exact target game build and executable
hash, then identify the exact source revision and package file, then verify the
package's supported game identity. If those game identities differ, installing
the newest public mod package does not fulfill a request to port this GitHub
mod. Follow the native mapping workflow below and keep the mod disabled until
all exact-build gates pass. Reports and user-facing summaries should label
these fields explicitly instead of using an unqualified word such as
"version".

## What this can and cannot automate

The first search pass can be made much faster by scanning the exact new
executable for retained byte signatures and reporting unique matches. PE
function boundaries, caller references, RTTI/vtables, register dataflow and
field accesses can narrow the candidates further. The Cosmos 7.05 investigation
found many useful candidates this way with NMS.py records, `pefile` and
Capstone; Ghidra was not required for that first pass.

A match is only a place to investigate. It does not prove the function's role,
calling convention, arguments, object layout, lifetime, thread or in-game
behavior. Those still need independent static corroboration and exact-build
runtime acceptance. Reusable bounded string- and call-reference scanners are
maintained under `tools/`; raw disassembly remains a private research artifact.
Do not put game binaries or personal save/runtime data in Git.

`tools/native_rtti_vtable_probe.py` is a reusable read-only probe for x64 MSVC
RTTI. It validates candidate TypeDescriptors, Complete Object Locators and
class hierarchies, then reports contiguous executable vftable pointer runs and
their `.pdata` entry matches. This is structural evidence only: a valid table
does not establish every slot's semantic role, hook ABI, lifecycle or live
behavior. Record the exact executable SHA-256 with every result.

For a capped name-only scan, `tools/native_rtti_name_inventory.py --exe
<exact-exe> --contains <term>` prints unique decorated strings shaped as
`.?AV...NUL`, along with the exact executable hash. It does not validate
TypeDescriptors, COLs, hierarchies or vftables. Use a known name to validate a
new filter; record a zero only within the exact string shape, maximum name
length and selectors.

`tools/native_function_disasm.py` prints a bounded RVA window from an exact
AMD64 PE image, the executable hash and any `.pdata` entry containing the
window's starting RVA. It is a read-only inspection aid, not a function-role
classifier; it does not follow chained unwind parents or prove that the
requested bytes form a complete function.

`tools/native_pdata_function_group.py` resolves the `.pdata` range containing
an RVA to its chained unwind root and lists all ranges in that function group.
It reports the exact executable SHA-256 and is read-only. Use it before
decoding split or chained function bodies; the result proves structure, not
semantic role or runtime safety.

For every compatibility pass, maintain the pattern ledger defined in the
[playbook](NATIVE-PATTERN-PLAYBOOK.md): role, pattern kind, source and pinned
revision, source-data hash and license, regeneration command, baseline RVA,
match count and addresses for each executable SHA-256, `.pdata` entry/chain
result, caller and call-site evidence, independent anchors, contradictions,
false matches, disposition and next bounded action. Keep third-party byte
signatures outside this repository unless their license permits storing them;
pin the provider and have the scanner read its exact local data file. A scanner
may report candidates but must never rewrite or enable the native profile.

## Repeatable workflow

1. **Freeze the input identity.** Wait until Steam has finished patching. Record
   platform/store, game version and build metadata, executable path, file size,
   file/product version, timestamp and full SHA-256. All scan output must name
   that hash. A displayed version or Steam depot BuildID alone is not the
   executable identity.
2. **Choose the correct baseline.** Start from the latest verified profile and
   its map, not a guessed nearby build. Preserve old RVAs, signatures, callers,
   argument roles, field offsets and evidence. The retained 7.04 source map is
   [NATIVE-PORT-MAP](NATIVE-PORT-MAP.md); use it with the executable hash and
   compatibility profile, not as proof for a newer build. Never overwrite the
   known-good profile while researching a candidate.
3. **Run read-only signature discovery.** Search the new PE's executable
   sections for each retained signature. Record the number of matches, match
   RVA, containing PE exception/function range, and whether the match is at a
   function entry. Zero or multiple matches mean the signature did not uniquely
   relocate the target. A unique match remains a candidate. For x64 code xrefs,
   decode inside the PE exception-function ranges (`.pdata`) and confirm the
   target at a decoded instruction boundary. Whole-section linear sweeps may
   help find leads, but cannot establish caller counts or prove that a reference
   is absent.
4. **Re-establish the role from callers.** Find direct callers and compare the
   call-site setup and following control flow with the baseline: registers,
   stack arguments, floating-point registers, return use, branch conditions and
   subsequent calls. `native_call_xrefs.py` reports decoded direct calls to one
   target RVA inside `.pdata` function ranges. For a call-site or return-address
   hook, map the exact call instruction and post-call return address; finding
   the callee is not enough. A shared movement helper may be called by death,
   teleport and warp flows, so filter and verify the owning event separately.
5. **Cross-check independent anchors.** Use RTTI/vtable slots, mangled names,
   known strings/resources, repeated call patterns and reads/writes of related
   fields. Prefer two or more independent anchors for a critical mapping. Record
   contradictions rather than choosing the most convenient interpretation. A
   negative search for one narrow instruction shape (for example, a field read
   immediately followed by `ret`) rejects only that exact shape; it does not
   establish that no accessor or callback exists.
6. **Rebuild the data-layout map.** For every used global and object field,
   verify the new offset in more than one relevant routine where possible.
   Trace how values are produced and consumed. Do not carry old offsets forward
   just because one nearby field stayed put.
7. **Audit every native dependency.** Compare the candidate inventory with the
   actual hooks, direct-call targets, call-site filters, globals, object fields,
   resource handles and callback assumptions in the source. One unmapped
   dependency keeps the whole new profile disabled. Derive the inventory from
   the current source each time; the 7.04-to-7.05 case study began with 12
   detours, nine direct-call targets and one binding-filter return site, but
   those counts are not a permanent contract.
8. **Review and test the explicit candidate.** Have the evidence reviewed
   against the exact executable and current source. Keep unknown versions
   fail-closed. Before installing or doing a live trial, close NMS normally,
   preserve and verify the required backup, and do not replace an installed
   module while the game is running. Record offline results separately from
   queue acceptance and player-confirmed visible behavior.
9. **Approve the profile only after all gates pass.** Add the exact hash and
   verified mappings together. Keep the prior profile and its evidence. Record
   the new profile's offline checks, live scenarios, failures and remaining
   limits; do not inherit success from an earlier game build.

## Evidence levels

Use these labels consistently in each build's mapping table:

| Status | Meaning |
|---|---|
| `UNMAPPED` | No plausible new target has been established. |
| `CANDIDATE` | A unique signature, name, or heuristic points to a location, but role or ABI is not yet corroborated. |
| `STATIC-CORROBORATED` | Function boundary and role have independent caller/dataflow or RTTI/vtable evidence. This is still not live compatibility. |
| `ABI-CHECKED` | Argument locations, return type, call-site behavior and relevant object layout have been checked against the exact executable. |
| `LIVE-CHECKED` | The exact candidate build passed the named runtime scenario; include artifact identity and outcome. This label applies only to that scenario. |
| `PROFILE-APPROVED` | Every native dependency and required safety, offline and in-game compatibility gate for this profile has passed. Release/distribution approval is recorded separately. |

Never promote a row because a game started, a hook registered, a queue was
accepted, or another row passed.

## Durable update handoff

At the end of every compatibility work period, update this reusable map and
the report for the exact executable, even when a missing proof means the mod
must remain disabled. Preserve prior findings and add the useful new steps,
observations, corrections, misleading approaches, and deferred checks from the
current pass. Label work that was not performed `NOT CHECKED`; do not make the
next investigation infer whether a dependency was considered. End the
build-specific report with the next bounded action and the evidence needed to
close it. Keep the record concise and reproducible: exact tool versions,
search parameters, bounded outputs, interpretation limits, and relevant
private evidence locations are useful; bulk disassembly and copied raw tool
output are not.

## Per-build mapping worksheet

Copy this section into a new `NATIVE-<BUILD>-COMPATIBILITY.md` and fill it as
evidence arrives. Keep one row per independent address, field or runtime
assumption.

```text
Game/platform/build:
Executable size/version/SHA-256:
Baseline profile and hash:
Scanner/tool versions and source revision:

Target role:
Baseline RVA / signature / call-site:
New candidate RVA:
Match count and executable section:
Containing function range / entry status:
Caller and register/stack dataflow:
RTTI/vtable/name/resource corroboration:
Argument and return contract:
Related globals/object offsets:
Evidence artifact (private path or sanitized Git document):
Status:
Unresolved questions / contradictions:
Exact live scenario and result:
Reviewer and date:
```

The public Git record should contain the executable hash, sanitized RVAs,
reasoning and bounded results, but not the executable or bulk disassembly.
Private raw evidence should be retained with the exact hash so another analyst
can reproduce the interpretation without confusing outputs from different
builds.

## Lessons preserved from 7.04 to Cosmos 7.05

- The 1 October teleport pass uses the reusable
  [`native_string_xrefs.py`](../../tools/native_string_xrefs.py) helper with
  dependencies pinned in `tools/native_research_requirements.txt`. It searches
  selected printable strings, then checks direct RIP-relative references only
  inside AMD64 `.pdata` ranges. Its report is bounded evidence: it does not find
  indirect, hashed, dynamically constructed, or non-RIP-relative references,
  and it never changes the compatibility profile.
- The 1 October respawn pass uses
  [`native_call_xrefs.py`](../../tools/native_call_xrefs.py) to locate direct
  callers of one exact-build RVA and report their decoded call context and
  return-site RVA. The helper does not find indirect calls or prove what a
  caller means. The current position-helper candidate has callers in both a
  function carrying a `DoPlayerRespawn` diagnostic label and warp-related
  functions; only the former's exact return sites are being observed.
- The 1 October RTTI pass recovered the `cGcApplicationDeathState` type
  descriptor, candidate vtable and a state-dispatching update method. The
  method's class ownership and floating-point update argument are stronger
  structural evidence than a string-only lead, but its state table has not
  been semantically mapped to completed local respawn. Keep it a candidate;
  require natural in-game correlation before any hook or summon opportunity.
- A second 1 October string pass matching `respawn` found the named
  `RPCReceivedPlayerRespawned` only in MSVC RPC template/type strings, not as a
  direct code reference. Treat this as a network-path lead, not proof of a
  local-player completion callback. `RespawnPlayer` also had no direct
  RIP-relative reference in this pass; that bounded negative does not prove
  the function is absent. Record the exact scan and lead dispositions in
  [NATIVE-0705-COMPATIBILITY](NATIVE-0705-COMPATIBILITY.md).
- The focused follow-up on `RespawnReason`, `LastKnownPlayerState`,
  `SpawnLocation` and `PLAYER_RESPAWN` found a mangled lambda type associated
  with `cGcPlayerRespawn::SpawnAndPositionShip`, but no direct code reference,
  enum-value mapping or completed-event contract. Keep it as a path candidate;
  do not infer semantics from its name or the logged scalar values.
- RVA `0x331F60` is statically corroborated as a state-based reason-code
  producer: its only direct `.pdata` caller is `0x330287` in the
  `DoPlayerRespawn`-labelled function, and the returned `EAX` is stored at
  object offset `+0x620` before being passed to the shared positioning helper.
  The enum values and completion semantics remain unknown, so this producer is
  not an approved trigger. Reproduce with `native_call_xrefs.py` as recorded in
  the build-specific compatibility report.
- A full-section linear Capstone sweep can decode embedded data or begin at an
  unaligned byte and manufacture apparent instructions. Use the `.pdata`
  function-bound scan for caller counts and negative xref findings; preserve
  any broad-sweep result only as an explicitly unverified lead.
- A broad `teleport` string pass can match nearly two hundred unrelated data,
  animation and sequence names. Audio/warp labels without code references and
  mission/notification sequence types without a verified caller contract are
  not local arrival callbacks. Keep the sanitized exact-build classifications
  in [NATIVE-0705-COMPATIBILITY](NATIVE-0705-COMPATIBILITY.md).
- A live freighter-to-station sample correlated helper return `0x3302C4`,
  `reason=11`, `flag=1` with the owner's reported successful arrival, while no
  new opportunity or queue followed. Keep this the strongest arrival lead,
  not a completion hook, until local/network semantics and success timing are
  proved. See the exact-build report.
- A later local candidate-trial run armed a new opportunity at this same
  filtered return, then recorded native queue acceptance and owner-confirmed
  visible appearance after a reported freighter-to-station trip. The trial
  clears any deferred save-load request before arming and refuses to replace an
  already-pending policy request. This confirms one test path can initiate the
  request, but not that the shared return is a completed local teleport event
  or safe for multiplayer. See the exact-build report.
- A second test used a station-to-planetary-base teleporter without a ship exit.
  The session had already accepted its separate save-load queue; the filtered
  helper return later armed and accepted another request, followed by owner-
  confirmed appearance. This reproduces the experimental hook on another local
  route, but still leaves the native reason and multiplayer contract unknown.
- A raw RIP-relative ModRM-byte scan can resolve a real LEA target while
  reporting the ModRM byte two bytes into the instruction as its apparent
  address. Label such output as candidate byte offsets, then re-decode from the
  `.pdata` function start and record the actual instruction boundary before
  reasoning about callers or hooks.
- A `movss [rcx]` getter scan returned zero for Cosmos 7.05 when requiring the
  next instruction to be `ret`, but the exact image contains float field reads
  inside larger functions. The zero only rejects that two-instruction shape;
  it does not locate or rule out a teleport-completion signal.
- NMS.py signatures plus PE boundaries quickly relocated several named
  functions. That was discovery, not proof that every old hook remained valid.
- `GetButton`'s function was found uniquely, but the separate return address
  used by the binding guard still needed its own caller mapping.
- A candidate such as `CanSummon` did not directly read its incoming owner
  argument; register tracing showed it obtained the owner globally and forwarded
  the slot to an eligibility helper. Do not reject a candidate based on a
  superficial “argument unused” scan.
- `GetDominantHand` was a plausible old helper counterpart. Its 7.05 body
  returns the 32-bit hand field in `EAX` on one path and zero on another, while
  the old caller treated a no-argument helper as a Boolean gate before reading
  that field separately. The retained NMS.py `c_int64` annotation does not
  settle whether the enum's zero/nonzero meaning is equivalent; similar names
  and locations do not settle semantic compatibility.
- The 7.05 `LoadFromData` candidate at `0x572C40` has the same six physical
  argument locations as the existing load hook, and direct callers use its
  `AL` result as status. This outweighs neither the contradictory NMS.py `void`
  annotation nor the need to verify all return paths and network-flag meaning;
  keep both pieces of evidence visible. The separate `SaveToData` candidate is
  not a current native dependency and includes a null-argument call site.
- PE exception-function ranges can split code associated with one logical
  method. Treat a range boundary as useful evidence, not a complete semantic
  function map.
- The pending companion slot changed from `0x6010` to `0x6020`, while several
  nearby table values remained unchanged. Confirm each field independently.
- A section-wide linear x86 decode can miss locked operations because code and
  data are not one continuous instruction stream. For resource-handle helpers,
  decode PE function ranges and corroborate exact callers. In Cosmos 7.05,
  `0x2D65980` matches the old retain helper's one-handle lookup and atomic
  increment; `0x2D61CE0` matches the paired release operation and is called by
  the relocated texture loader. This supersedes the earlier raw-scan
  observation that no `+0x134` resource reference-count operations were found.

The 7.05 rows in [NATIVE-0705-COMPATIBILITY](NATIVE-0705-COMPATIBILITY.md)
document the static mapping behind the exact native profile in
`native_compatibility.json`. That profile accepts only the recorded Steam build
and executable hash. The owner reported one bounded live smoke pass; it does
not establish broad gameplay acceptance or support for another executable,
store or platform.

## Lessons from the Cosmos 7.06 partial pass

- A matching old object-field offset inside a new `.pdata` range can locate
  relevant logic without identifying a hookable method entry. The 7.06
  `0x508DE0` owner-field range has no decoded direct callers and consumes
  pre-existing register context, but its unwind `CHAININFO` links it to the
  true entry at `0x508DC0`. That parent is called at `0x489661` with an owner
  subobject and delta in `XMM1`, making it a stronger static update-hook
  candidate. Follow unwind parents before concluding that a method is unmapped.
- A string xref to `cGcPlayerStateData` led to a large range whose first block
  passes the name to a helper and then performs hash-like field processing.
  Treat type/data names as search anchors, not proof of load/save semantics.
- The old load RVA `0x572C40` fell inside a 7.06 range starting at `0x572410`,
  but that entry initializes object fields/subobjects and its direct caller at
  `0x2CEAF0` is another constructor. Reject containment-based load mappings;
  the `LoadFromData` candidate remains unmapped.
- A uniquely matched `GetButton` callee does not identify the correct return
  site. Map each call instruction, arguments, post-call menu state and the
  precise behavior that the binding filter must suppress. Preserve plausible
  alternate return sites until independent evidence chooses one.
- Read the NMS.py mangled name alongside the byte signature. The 7.06
  `cGcPlayer::GetDominantHand` name declares a virtual const member with an
  implicit `this` argument even though its body does not read `RCX`; check the
  source function-pointer type and actual call setup instead of assuming a
  method is static.
- The NMS.py decorated name for `AddTimedMessage` decodes to eight explicit
  parameters, but the exact 7.06 body reads three trailing flag bytes and a
  native caller at `0x3BD8EB` supplies the ten-argument layout used by the
  current `Notice` declaration. Caller and body evidence resolved this ABI;
  the decorated-name record was a misleading lead for the candidate build.
- A unique same-class method match is not automatically the right helper: the
  `cGcQuickMenu` constructor at `0x2CA290` has no explicit parameters, while
  the existing `MenuConstruct` call passes four. Preserve it as a rejected
  candidate instead of mapping by class-name similarity.
- `native_call_xrefs.py` scans decoded direct calls within `.pdata`; zero
  results mean no direct call was found by that pass, not that vtable,
  callback, exception or dynamically selected references are absent.
- A placement helper can be ABI-checked independently of the whole profile.
  The 7.06 candidate `0x14426A0` has five direct callers and retains the
  placement object's `RCX`, two scalar `XMM` inputs and `R9D` hand argument.
  Keep that useful partial mapping while leaving unrelated hooks and the exact
  build profile disabled until every required dependency is resolved.
- When an old load signature does not match, compare nearby exact type
  signatures before treating a containing `.pdata` range as a candidate. On
  Cosmos 7.06, the old load RVA `0x572C40` lies in the uniquely matched
  `cGcPlayerState::cGcPlayerState` constructor at `0x572410`; its direct caller
  is another constructor. `cGcPlayerState::LoadFromData` has zero matches and
  remains unmapped. A separate `SaveToData` match is not a substitute.
- A type name and hash-like field traversal are search anchors, not proof of a
  lifecycle load hook. The `cGcPlayerStateData` reference at `0x29F1CC3` leads
  to `0x29F1C60`, whose only direct caller found in `.pdata` is a small
  field-processing wrapper; do not install it without load-specific callers
  and argument/return evidence.
- Validate the full x64 MSVC RTTI chain before drawing conclusions from a raw
  type-name search. A 9 October scratch pass incorrectly derived the 7.06
  `.?AVcGcQuickActionMenu@@` TypeDescriptor at `0x515A44C` by subtracting 12
  bytes from its name at `0x515A458`; the header is 16 bytes, so the correct
  descriptor is `0x515A448`. That off-by-four error created a false-negative
  vftable result. The corrected 12 October probe validated COL `0x4B66FE0`,
  hierarchy bases `cGcQuickActionMenu`/`cGcQuickMenuState`, and vftable
  `0x4A504E0` with 16 executable slots. The earlier negative finding is
  superseded; slot semantics and live behavior remain separate questions.
- A missing NMS.py signature does not rule out a role mapping when exact-build
  callers independently preserve the old ABI and control-flow use. On 7.06,
  `0x573500` has four direct callers at the same load-state paths documented
  for 7.05, reads the common save value from `RDX+0x8980`, and returns a status
  in `AL`. Keep it as a static load-role candidate while the network/reset
  flags and local-player semantics remain unresolved.
- Resolve chained `.pdata` parents before interpreting a menu target RVA. On
  7.06, old `MenuConfirm` RVA `0x153A770` chains to the `TriggerAction` root at
  `0x1531E00`; old `MenuConstruct` RVA `0x143B720` is inside a 64-byte vector
  append, not the 224-byte item constructor; and old `MenuAppend` RVA
  `0x153CF40` chains to an item-mutating function that returns a Boolean.
  Reject these as direct replacements and record the observed body/ABI reason.
- Caller shapes can correct a plausible menu-name match. The root for the old
  label range is `0x152A1C0`, with six direct calls passing a menu and second
  pointer and body references to the known menu fields. Keep it as a candidate
  until output semantics and independent class/method identity are confirmed.
- The old `MenuBuilder` RVA `0x15282B0` is inside a chained routine rooted at
  `0x1527BD0`; the root and following ranges initialize many vector/container
  fields, and the only direct caller passes a member pointer from an unrelated
  initialization path. Reject this range as the builder and search for the
  actual function that creates or appends `0xE0`-byte menu items.

### Handoff after the 9 October 2026 signature and RTTI follow-up

Confirmed new evidence: `cGcPlayerState::cGcPlayerState` uniquely matches
`0x572410` in the exact 7.06 executable, while `cGcPlayerState::LoadFromData`
has no signature match. The old load RVA is therefore a constructor false
lead. A direct-call scan of `0x29F1C60` found one field-processing wrapper
caller and no load-specific role. The 9 October conclusion that the QAM vftable
was unresolved was invalidated by its TypeDescriptor offset error and is
superseded by the corrected 12 October probe below. The load hook remains
unresolved without altering the 7.05 profile.

Reproduce with CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.9 and NMS.py
data pinned at `b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`:

```text
python -B tools/native_signature_matches.py --exe "<verified Cosmos 7.06 NMS.exe>" --data-json "<pinned NMS.py data.json>" --name cGcPlayerState::cGcPlayerState --name cGcPlayerState::SaveToData --name cGcPlayerState::LoadFromData
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x29F1C60 --context 8
```

The former returned one constructor match at `0x572410`, one `SaveToData`
match at `0x57B4C0`, and no `LoadFromData` match. The latter scanned
52,110,272 bytes across `.pdata` ranges and found one direct call. `NOT CHECKED`:
indirect references and lifecycle semantics of that field-processing
routine, the replacement load method and network/reset arguments, a confirmed
Quick Action Menu slot semantics, live behavior, and all 7.06 gameplay
scenarios. The vftable identity itself was confirmed on 12 October.

Next bounded action: anchor a caller/data-flow search for the 7.06 player-state
load path from the confirmed constructor and save method, and require callsite
argument and return-use evidence before assigning a replacement. Resolve the
menu method table from verified data references or leave its feature unmapped.
Keep production source/profile unchanged until all dependencies and validation
gates are satisfied.

### Handoff after the 9 October 2026 load-callsite pass

The missing `LoadFromData` signature is now supplemented by a strong
caller-anchored role candidate at `0x573500`. Four direct calls preserve the
six physical argument locations, status-return use and same surrounding
load-state paths as the 7.05 hook. The function's eight chained `.pdata`
ranges resolve to that entry; its body reads the common save value through
`RDX+0x8980`, has an early zero-result path, and sets `AL=1` on its normal
success path. This is static evidence only, not live proof or an approved
profile mapping.

Reproduce the direct-call pass with CPython 3.11.9, pefile 2024.8.26 and
Capstone 5.0.9:

```text
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x573500 --context 10
```

The scan covered 52,110,272 bytes in `.pdata`, skipped zero ranges and found
four direct callers. `NOT CHECKED`: semantics of `R9B` and both stack flags,
local-player versus network behavior, complete return/side-effect analysis,
live load behavior, the Quick Action Menu method table, and remaining runtime
dependencies. Next, trace those four callsites and the candidate's argument
reads to settle player/network/reset behavior, then continue menu and full
dependency mapping. Keep source and profile unchanged until the remaining
evidence and safety gates pass.

### Handoff after the 9 October 2026 quick-menu root pass

Following `UNW_FLAG_CHAININFO` rejected four old menu RVAs as replacement
entries: `0x143B720` belongs to a 64-byte vector append, `0x153A770` is a
chained range inside the `TriggerAction` root, `0x153CF40` belongs to a
Boolean item-mutating function, and `0x15282B0` belongs to a
container-initialization routine. The stronger label candidate is `0x152A1C0`
with six direct callers and known menu-layout references. The actual builder,
selection, resource, append and confirmation roles still need independent ABI
and semantic evidence; the Quick Action Menu vftable conclusion here is
historical and was superseded by the corrected 12 October RTTI pass.

The `.pdata`-bounded multi-target pass scanned 52,110,272 bytes and skipped no
ranges. Reproduce individual direct-call checks with CPython 3.11.9,
pefile 2024.8.26, Capstone 5.0.9 and
`tools/native_call_xrefs.py`; use the exact root targets `0x143B680`,
`0x15182A0`, `0x1524230`, `0x1527BD0`, `0x152A1C0`, `0x1531E00` and
`0x153C840` with `--context 8`. Resolve each old RVA's unwind chain before
using a root result to make a role claim.

`NOT CHECKED`: exact label-output semantics, replacement
constructor/append/resource functions, complete binding-filter behavior,
live menu behavior, and remaining game dependencies. Next, trace the indirect
calls and data flow from the label/trigger paths to the function that creates
or appends `0xE0`-byte menu items, then identify its safe timing and ABI. Keep
source and compatibility profile unchanged until every required mapping and
safety gate is resolved.

### Handoff after the 12 October 2026 RTTI and menu-layout pass

As of 12 October, the official release log still lists Cosmos 7.06 first and
contains no 7.07 entry. The exact local executable remains Steam build
25732212, file/product version 180836, size 88,560,712 bytes and SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. The
GitHub `main` ref read back as `f7d97b61fcf152677d0d30de34f6c1b48675c436`.

The TypeDescriptor correction and validated RTTI evidence are recorded above.
Vftable slot 0 is `0x15286C0`, a QAM update candidate with chained body ranges
through `0x1529E99`; it calls `0x153C840` and label candidate `0x152A1C0`.
Slot 6 is `0x153C680`; its body reads menu depth, selection, vector count/data
and the selected item's action at `+4`, returning a Boolean. Its matching
7.05 vtable slot makes it a `STATIC-CORROBORATED` confirmation candidate,
not an approved hook. The label candidate remains static only.

The update root calls `0x1530D40` at `0x1528855` with menu `RCX` and `DL=1`
on the observed branch. The method resets menu depth/selection, clears vector
counts and selected indices, updates `+0x2C0`, and returns a Boolean. It does
not construct or append items; reject it as the missing builder/append
replacement. Treat this as a static state-transition interpretation only.

Reject `0x153C840` as an append replacement: its three direct callers are
`0x142449E`, `0x15286F3` and `0x1545F22`, and the body mutates an existing
item's action at `+4` and field at `+0x88`; it does not append to a vector.
Reject nearby `0x153C7A0` as an append candidate because it resolves a menu
context index and returns a pointer into the supplied menu object. Generic helper `0x2BF9A00` has 791
direct callers; two QAM update calls (`0x1528FE7`, `0x1529129`) pass stride
`0xE0`, consistent with vector assignment/replacement. Its broad use and the
missing lifecycle evidence make it unsuitable as a menu hook.

Reproduce the corrected RTTI pass with CPython 3.11.9 and pefile 2024.8.26:

```text
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVcGcQuickActionMenu@@"
```

Direct-call scans for this run used Capstone 5.0.7 in the `py -3.11` runtime
(the repository requirements file pins 5.0.9):

```text
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153C840 --context 10
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2BF9A00 --context 10
```

Both scans decoded 52,110,272 bytes in `.pdata` and skipped zero ranges; they
found three and 791 direct calls respectively. The RTTI helper is read-only
and does not require Capstone.

The QAM update callsite and the `0x1530D40` body were decoded in bounded
`.pdata` windows with CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x15286C0 --size 0x216
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1530D40 --size 0x127
```

The first window is the QAM vtable slot-0 root and contains the direct call at
`0x1528855`. The second is the exact `.pdata` entry for the Boolean menu state
transition. Follow chained unwind metadata separately before analyzing any
other ranges.

`NOT CHECKED`: whether QAM update builds the menu every frame or on an event;
its lifecycle and idempotency; the exact safe item-construction/append point;
selection, resource and binding-filter roles; load-candidate flag and
local-player semantics; live behavior; and the rest of the native dependency
inventory. Next, trace `0x15286C0` inputs/calls and vtable slots to find the
builder's actual item creation path and prove when it runs. Continue the full
ABI/layout audit and load-flag mapping; keep source, profile and package
unchanged until all exact-build gates pass.

### Required pattern-ledger rule recorded 12 October 2026

Every new executable or native-dependency change must follow
[NATIVE-PATTERN-PLAYBOOK](NATIVE-PATTERN-PLAYBOOK.md). `AGENTS.md` makes this
automatic and required. The exact-build report must preserve, by dependency,
the exact input/cache key, successful and failed pattern attempts, false leads,
corrections, scoped negative results, `NOT CHECKED` items and one bounded next
action. This reusable map keeps the lessons that shorten the next pass:
NMS.py unique matches are candidates; caller anchors can recover roles with no
byte-signature hit; chained unwind parents must be resolved; the MSVC RTTI
TypeDescriptor header is 16 bytes; old-RVA containment is not a mapping; and
generic helpers/state-reset methods must not be mislabeled as menu append or
builder functions. The exact Cosmos 7.06 evidence and limits remain in
[its report](NATIVE-25732212-COMPATIBILITY.md).

### Handoff after the 12 October QAM data-flow pass

The confirmed QAM update root `0x15286C0` has three `.pdata` ranges. The new
read-only `tools/native_pdata_function_group.py` reports the containing entry,
resolved unwind root, all chained ranges and the exact executable SHA-256;
use it before decoding ranges separately. A scratch chain query once returned
zero because the command quoted the game path incorrectly and then compared a
root tuple with the wrong shape. Neither result was a binary negative. Keep
such invocation/filter failures in the exact-build report and rerun them with
the reusable helper.

The full call-site window at `0x1528F80` confirms the QAM passes `R9D=0xE0`
as the item stride to generic helper `0x2BF9A00`; `RCX` points to a temporary
render vector and `RDX` to source item data in the menu vector. The function
copies/resizes that vector and has 791 direct callers, so it remains a shared
storage utility, not a menu append hook. The neighboring navigation method
`0x1530AC0` updates depth/selection fields; it is not the missing item
constructor or append path. Reuse these exact-build findings only for hash
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.

### NMS.py menu-signature coverage checked 12 October 2026

The pinned NMS.py commit is `b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`;
its `tools/data.json` SHA-256 is
`F311C9F54C0CCE199AB955A0E8DE2CFE2FCFB09274E557A2A27908C1B15BAF5F`, and
the repository license is MIT. Its only symbol names containing `menu` or
`quick` are `cGcQuickActionMenu::TriggerAction` and
`cGcQuickMenu::cGcQuickMenu`. The first uniquely locates a trigger candidate;
the second is a false lead for the four-argument menu-item constructor. The
provider has no named quick-menu builder, item-constructor or append patterns.
Treat this as a coverage gap in that dataset, not proof that the functions are
absent; continue with caller and data-layout anchors. Exact results and
reproduction commands are in the [7.06 report](NATIVE-25732212-COMPATIBILITY.md).

### Correction after the 12 October full chained-helper decode

The complete `0x2BF9A00` `.pdata` group confirms a generic vector copy/resize
helper: it uses `R9` as element size, updates the destination count to the
requested source count, and returns the destination data pointer after
allocation/copy handling. The QAM calls at `0x1528FE7` and `0x1529129` both
pass `0xE0` in `R9D`; they copy current/next menu vectors into render scratch
headers at `render+0x610` and `render+0x518`. Their shared item stride is a
shape clue, not append evidence. The helper's 791 direct callers and its body
reject it as the menu append hook.

Also, a decode window started at `0x15290D0` produced invalid initial
instructions because that RVA was not a verified boundary. The valid rerun
started at the containing `.pdata` range boundary `0x15288D6`. Treat arbitrary
RVA-start decoder output as untrusted until the start boundary is established;
the new playbook records this rule.

### QAM vtable-slot follow-up, 12 October 2026

Additional bounded review of the validated `cGcQuickActionMenu` vftable found
slot 8 at `0x153C000` and slot 10 at `0x153C5F0` return Booleans after checking
input IDs `0x56`/`0x54` and `0x17`/`0x18` respectively; slot 10 also checks a
timer at `+0xA174`. These are availability/action-predicate candidates, not
item construction. Slot 9 at `0x153C0C0` is a three-range chained function;
it reads menu depth and selection at `+0xA088`, indexes an item with stride
`0xE0`, and calls string-like helpers. Its likely text/label role remains
unverified because this pass had only filtered call/reference output. Slot 15
at `0x152A0E0` checks `EDX==4`, calls `0x152A100` and returns a Boolean; its
role remains unresolved. None is evidence of a safe builder or append hook.

One exploratory unbounded decorated-type-name dump exceeded the output budget
and was discarded; it yielded no usable inventory and is not a zero-match
finding. Bound future raw-name inventories to a narrow type family, deduplicate
and cap printed candidates, while reporting total counts separately.

The slot pass used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7. Resolve
each function group before decoding; slot 9 must include its chained ranges.
Reproduce the bounded starts with:

```text
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C000
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0C0
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C5F0
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152A0E0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C000 --size 0xB3
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0C0 --size 0x3D
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C0FD --size 0x14F
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C24C --size 0x398
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153C5F0 --size 0x8B
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152A0E0 --size 0x20
```

`NOT CHECKED`: complete caller/body semantics for these slots, the roles of
slots 1-5, 7 and 11-14, the actual item constructor/safe append point, live
behavior and the remaining native dependencies. Next bounded action: trace
the QAM update and label/trigger paths to the function that initializes an
item and changes a source menu vector's count; establish callers, arguments,
full chained body, lifecycle and thread before considering any source change.

### Follow-up on the QAM helper calls, 12 October 2026

The update call target `0x153B5B0` is a single `.pdata` range
`0x153B5B0–0x153BE52`. A bounded call-list pass shows calls to the validated
label method `0x152A1C0`, navigation/reset methods `0x151ACD0` and `0x1530D40`,
and trigger method `0x1531E00`; this pass does not establish any item
construction role. The adjacent call target `0x153BE60` is a separate chained
group (`0x153BE60–0x153BE80`, `0x153BE80–0x153BFBB`,
`0x153BFBB–0x153BFC8`). Its decoded body scans the menu's `0xE0`-stride item
vector for a pending action, adjusts selection/state and clears menu counts;
it does not append a new item. Treat it as an action/selection state handler,
not as the missing item constructor.

Vtable slot 15 at `0x152A0E0` calls `0x152A100`. That call target has no
`.pdata` entry, but the direct call and bounded code window establish the
target boundary. The helper checks the selected action at item offset `+4`
against action 4 and a bit mask, then returns a Boolean. This narrows slot 15
to a selected-action predicate candidate; the helper's standalone unwind
identity and its other callers remain unverified. It does not create or append
items. The earlier interpretation of `0x152A1C0` as a `MenuLabel` candidate
was superseded by the 12 October source-vector/caller trace: it is the QAM
source builder. Do not reuse it as a label hook. The exact-build report
records the correction and the remaining label-output question.

An additional whole-image direct-call scan for `0x152A1C0` was stopped after
more than 60 seconds with no output. It was redundant with the six callers
already recorded in the exact-build report, so it is `NOT CHECKED` and yields
no negative result. The one-target scanner decodes roughly 52 million
`.pdata` bytes per run; check the caller ledger before rerunning, and batch
unmapped targets into one pass if needed.

Reproduction used CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7:

```text
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153B5B0
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153B5B0 --size 0x8A2 | Select-String -Pattern '\bcall\b'
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153BE60
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x153BE60 --size 0x168
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x152A100 --size 0x56
```

`NOT CHECKED`: constructor and safe append point, full item-vector producer,
remaining slot roles/callers, complete lifecycle/thread behavior, the
standalone unwind/other callers of `0x152A100`, live behavior and other native
dependencies. Next action remains tracing an actual source-vector count
increase alongside initialization of a new `0xE0` item.

### QAM conditional update candidate, 12 October 2026

The QAM update callsite at `0x15288B3` calls `0x153B5B0` with `RCX=menu` and
`RDX=render` when `menu+0xA170 != -1`. The alternate state branch calls
`0x153BE60` at `0x15288C9` with the same arguments when `menu+0xA164 != 0`.
This updates the earlier handoff: those two call roles are no longer wholly
unknown, but neither target is approved as the replacement builder.

`0x153B5B0` has one `.pdata` range (`0x153B5B0–0x153BE52`). Its body obtains a
context pointer through `0x153C7A0`, compares five `0xE0`-stride records with
the current menu vectors, clears menu counts/selections on a mismatch, and
calls label/navigation helpers. Its later loop copies or initializes
`0xE0`-byte records at an address derived from that context pointer. The
relationship between that destination, the render argument and the source
QAM vector is not yet established; the body does not provide a confirmed
source-vector append/count increase. Keep `0x153B5B0` as the best conditional
menu-update/builder candidate for further tracing, not a hook mapping.

Corrected interpretation of `0x153C7A0`: it tests global context state and
returns a pointer inside the supplied menu object at a context-dependent
offset (`menu + 0x2D0 + context * 0x3480`). Earlier wording that it resolved
owner/local-player state was too broad and is superseded by this exact bounded
decode. `0x153BE60` is a separate three-range handler that searches menu items
at stride `0xE0`, updates selection/state and clears counts; it is not the
append function. Slot 15's direct call target `0x152A100` similarly checks the
selected item's action field and returns a Boolean, so it remains a predicate
candidate.

The direct target `0x151ACD0` also has no `.pdata` entry. Its bounded body
checks the current vector count and selected-index fields, clamps the selected
index and backs out through empty menu depths. It reads vector counts but does
not append or increase them. It is a depth/selection repair helper, not the
missing builder. Reproduce from the verified direct-call entry:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x151ACD0 --size 0x63
```

The adjacent `.pdata` function `0x151AB50–0x151ABD1` is a Boolean equality
comparison for two `0xE0` item records. It checks action at `+4`, fields at
`+0x40`, `+0x50`, `+0x84`, `+0x88`, `+0x90`, and the string at `+0x44`.
The `.pdata` function `0x151ADD0–0x151AE81` is a fixed-block initializer: it
initializes one record and loops through five more `0xE0` records, calling
`0x142A3AAC0` for their string fields and setting default values. It is not
the mod's one-item/four-argument constructor and does not append to a QAM
vector. These roles explain two helpers called by the QAM update but leave
the actual single-item construction and visible vector insertion unresolved.

In the chained QAM update, the render argument contains existing item vectors
at `render+0x618` (count `+0x614`) and `render+0x520` (count `+0x51C`). The
update walks those entries at stride `0xE0`, compares their fields with the
context records and writes a context index to a matching existing item's
`+0xD8` field (`0x1529D87` and `0x1529E47`), then calls navigation helper
`0x1530AC0`. These are item-metadata associations, not insertions: the writes
target item fields, not vector header counts/data/capacity. Preserve this as a
useful distinction for future builder searches.

A second batched xref pass confirms `0x151AB50` has one direct caller at
`0x15296EB`; `0x151ADD0` has two at `0x1529709` and `0x1529729`, all inside
the QAM update chain. The adjacent chained function `0x151AE90` has one caller
at `0x151B18C` from range `0x151AFCB–0x151B87C`; its body computes a minimum
distance over a pointer vector and is an adjacency false lead, not a menu
constructor. That pass again decoded 52,110,272 `.pdata` bytes with zero
skipped ranges. Use the batched scanner and preserve only these concise caller
results instead of copying its full output.

`0x142A3AAC0` is the call operand's virtual address; the PE helper requires
RVA `0x2A3AAC0`. The corrected bounded decode finds no `.pdata` entry and
shows a tiny direct-call target that writes `-1` to the qword at `RCX` and
returns. This fits a field/string sentinel initializer called with the string
field address, not a menu-item constructor. Capstone prints instruction
addresses as RVAs but call operands as VAs; filter on the operand form shown
and subtract the image base before asking an RVA-based tool.

A bounded `.?AV...NUL` byte-name search found four names containing `quick`:
the QAM type, its `cGcQuickMenuState` base, an unrelated QuickWarp notification
type and a QuickMenuRenderState helper type. It found no dedicated QAM item
class name; that does not show that an item constructor/function is absent. An
initial inline PowerShell/Python regex was over-escaped and falsely printed
zero, so that output was discarded. The reusable helper avoids that quoting
failure:

```text
py -3.11 -B tools/native_rtti_name_inventory.py --exe "<verified Cosmos 7.06 NMS.exe>" --contains quick
```

The helper output was capped, deduplicated and hash-stamped for the same
`NMS.exe`. CPython 3.11.9 was used; this raw-name pass does not replace the
validated RTTI/vftable probe.

The direct-call scanner now accepts repeated `--target-rva` flags and scans
the exact `.pdata` inventory once. A four-target run decoded 52,110,272 bytes
with zero skipped ranges: one caller each for `0x153B5B0` and `0x153BE60`,
three for `0x151ACD0`, and fourteen for `0x153C7A0`. Twelve `0x153C7A0`
callers are inside the chained QAM update body. This took about two minutes,
so batch new targets but first reuse existing caller evidence.

The QAM update also calls `0x151AB50`, a Boolean equality check across the
action/string/layout fields of two `0xE0` records. Its `0x151ADD0` helper
initializes six fixed `0xE0` records per `0x540` block, including strings via
`0x142A3AAC0`. This shows default context-item setup, not the mod's one-item
constructor or the QAM vector append. The full record layouts and helper
ABIs remain incomplete.

```text
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x153B5B0 --target-rva 0x153BE60 --target-rva 0x153C7A0 --target-rva 0x151ACD0 --context 1
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x151AB50 --size 0x81
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x151ADD0 --size 0xB1
```

`NOT CHECKED`: whether `0x153B5B0` is a safe menu-builder replacement, exact
destination ownership/count behavior, the role and caller ABI of
`0x142A3AAC0`, the complete `0x153C7A0` caller set, the item constructor and
append point, full filter/selection semantics and live behavior. Next action:
trace the `0x153B5B0` destination and record ownership, item initialization,
and source vector count changes; compare its pre/post behavior with the 7.05
builder's established contract before any hook or source change.

### Handoff after QAM count-offset tracing, 12 October 2026

The new bounded memory-displacement scanner filters decoded `.pdata` memory
operands by `READ` or `WRITE`, accepts repeated offsets in one pass, and prints
the containing runtime-function range beside each hit. On the exact 7.06
executable it scanned 52,110,272 bytes with zero skipped ranges. The filtered
write counts for `+0xA05C`, `+0xA06C` and `+0xA07C` were 14, 11 and 13; the
80-hit cap kept all results. The initial unfiltered `+0xA05C` view was capped
at 20 and must not be reused as complete evidence.

The tempting `0x2CA7BB` write to `+0xA06C` is a reset in the function
`0x2CA6D0–0x2CAA96`. Its only direct caller is `0x2CA3FE` in the pinned
`cGcQuickMenu::cGcQuickMenu` constructor. Reject it as an item producer. The
other QAM-relevant writes cluster in the already known update, reset and
conditional-helper paths; stack-local hits and the 229-caller generic
initializer are not independent menu-builder evidence. Record the base object
for each remaining count write before assigning the offsets to source or
render vectors. Reproduction and the complete bounded-build handoff are in
the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).

The matching read-filtered displacement pass found 55 reads at `+0xA05C` and
eight each at `+0xA06C` and `+0xA07C`, again across 52,110,272 `.pdata` bytes
with zero skipped ranges. These appear throughout QAM update, label,
selection/trigger, reset and conditional-update paths. The known 7.05 vector
layout and 7.06 reads support interpreting these as per-depth count fields;
read coverage proves where the counts are consulted, not where an item is
appended. Next, trace the adjacent data/capacity fields and vector-helper
arguments from `0x153B5B0`; require the destination to resolve to the same
source menu object and observe its count increase after `0xE0` item setup.

That helper tail is now decoded: `0x153B5B0` selects a `0x540`-stride context
block, reads existing selected items from the source menu vectors, and copies
or default-initializes five fixed `0xE0` context-cache records at
`context-block+0xE0`. Its `+0xA05C/+0xA06C/+0xA07C` writes only clear menu
counts while repairing state; the tail writes to the separate cache
destination. Reject it as a builder and do not repeat this append hypothesis.
Follow the remaining QAM vector-copy arguments and keep a candidate only if
its destination resolves to a source menu vector and its count grows after
one item is initialized. Full reproduction and limits are in the [7.06
report](NATIVE-25732212-COMPATIBILITY.md).

### QAM source builder and vector helpers, 12 October 2026

The broad `0xE0` stride/count scan returned 30 same-function candidates. It is
useful for finding producers, but its hit list is not a role map. Reverse
RTTI mapping rejected `0x143D700` (`cGcGalaxyPathMenu::Update`) and
`0x1545EF0` (`cGcTerrainEditMenu::Update`) as QAM methods; their vector writes
belong to other derived quick-menu states. The `0x258290` count-looking lead
uses 16-byte pairs, not `0xE0` items. A constructor reset at `0x2CA7BB`, the
context snapshot helper `0x153B5B0`, and the older RVA `0x15282B0` are also
false builder leads for the reasons recorded in the build report.

The validated `cGcQuickActionMenu` vtable is at `0x4A504E0`, with its update
slot 0 at `0x15286C0`. That update clears the three source-vector counts and
calls `0x152A1C0` with the menu and render pointers. The latter function
matches the prior builder's `(menu, render)` call shape and constructs
`0xE0`-byte items before appending them. Its source append call passes
`menu+0xA058` and the constructed item to `0x153EE50`. The builder target is
therefore a strong static replacement candidate for old builder role
`0x15282B0`, pending lifecycle/thread checks.

The item constructor candidate is `0x143D5D0` (`.pdata` entry
`0x143D5D0–0x143D6F2`). Its register and stack argument positions match the
current `MenuConstruct` function type. The vector appender candidate is
`0x153EE50` (`.pdata` entry `0x153EE50–0x153EFC7`); it copies one `0xE0`
record, increments the count at header `+4`, grows through `0x2BF93E0` when
capacity is exhausted, and returns the inserted-item pointer. These map the
old constructor and appender roles as exact-build static candidates; they do
not establish item lifetime, concurrent callers, hook safety, or live
behavior. The append helper also has a render-vector call path, so a future
detour must continue checking the exact destination header before touching
QAM state.

For future builds, the efficient sequence is: scan the known record stride
and count displacement once; shortlist candidates that touch already mapped
QAM fields; reverse-map those candidates through RTTI; then inspect only the
surviving function groups and direct callers. Stop revisiting a false lead
once its object identity or record stride contradicts the role. Preserve the
scan cap, executable hash, tool versions, and every rejected interpretation
in the per-build ledger. Full commands, exact findings and remaining gates
are in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).

The next QAM slot check maps old `MenuConfirm` to slot 6 at `0x153C680`.
That method validates menu depth/selection and a selected `0xE0` item, then
returns its Boolean predicate in `AL`, matching the old slot's role. Keep the
status at `STATIC-CORROBORATED`: callers use virtual dispatch, and live
timing/thread behavior remains unchecked. The exact vtable and chained-range
evidence is in the 7.06 report.

The first selected-index write scan found 29 `+0xA088` writes and 19
`+0xA050` writes with no truncation. `0x1530AC0` is a tempting false match
because it updates QAM selection, but its caller passes the menu and an input
state object; the function reads key/button state and handles navigation. It
does not match the old `(depth_field, depth, index)` helper ABI. Keep the old
`0x1518EF0` selection target unmapped until a matching setter callsite or
independent pattern is found. Full results and exact commands are in the
7.06 report.

### QAM text-output slot candidate and release check, 16 October 2026

The official Hello Games release log still lists Cosmos 7.06 as the newest
game patch; no 7.07 entry was present when checked on 16 October. Keep game
release, store build/executable identity and mod package version as separate
fields. The 7.06 RTTI vftable slot 9 at `0x153C0C0` is a plausible `MenuLabel`
candidate because its body reads selected QAM items and writes two text output
buffers. It appears to use `RCX=menu`, `RDX=output1`, `R8=output2`, whereas the
7.05 adapter declares a two-argument label hook and writes 128 bytes to one
buffer. Keep it as `CANDIDATE; ABI AND OUTPUT SEMANTICS UNRESOLVED`; do not
promote the address or hook it using the old prototype. This is a successful
RTTI/body shortlist, with output purpose and virtual callers still open.

Useful correction: `0x152A1C0` is now mapped as the 7.06 QAM source builder,
not `MenuLabel`; preserve the withdrawn interpretation as a false lead and
avoid repeating that label search. One exploratory direct-call scan for slot
9 did not produce its result within the bounded shell window; record it as
`NOT CHECKED`, not zero, and do not rerun it solely to search for indirect
virtual callers.

For the exact executable identity, commands, slot ranges, tool versions,
ABI discrepancy and bounded next action, see the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).

The suggested neighboring-base-vftable comparison did not work for the two
names present in the QAM hierarchy: exact RTTI queries for
`.?AVcGcQuickMenuState@@` and `.?AVcGcQuickMenu@@` each found zero validated
standalone locators. This is not evidence that slot 9 has no indirect callers;
do not repeat the same two-name query. QAM slot 14 at `0x153DDF0` is a
resource-hook false lead: its vtable-anchored body checks `[this+0x10]` and a
global value against an `EDX` argument, then returns a Boolean. It has neither
the old one-pointer ABI nor resource-management behavior. Do not interpret
adjacent code as part of that method without an independent function boundary.
Use a bounded slot-offset/callsite dataflow or an independent label signature
to continue the `MenuLabel` mapping; keep resource initialization unmapped.

### Load-flag data-flow follow-up, 16 October 2026

For Steam build 25732212 / Cosmos 7.06 (NMS.exe SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499), the +0x4BE6A0 field is set from R9B in a routine rooted at 0x495640. Its sole direct caller, 0x4955F8 in root 0x495560, derives that byte from a global session subobject using a state check, virtual predicate and object field. The same global subobject is consulted by the 0x495250 helper when a reader passes the byte in DL. This is a session-dependent state flag, but neither its exact name nor local/network meaning is established.

Two bounded corrections matter for future searches: 0x4A88F8 and 0x497A6C are chained ranges, rooted at 0x4A88C0 and 0x497A30 respectively. A zero direct-call result against 0x4A88F8 is only an interior-target negative. The corrected full .pdata query against 0x4A88C0 also found zero direct E8-style calls, and its RTTI-backed vftable query found zero slots; indirect callers remain possible. Do not repeat the short 0x4A88F8 disassembly window that ended before the field read, and quote the executable path with double quotes in PowerShell because No Man's Sky contains an apostrophe. Record the exact scan scope and corrected results in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).

The load-flag scan is useful progress but does not close the load hook: the session object's class and the predicate meaning remain NOT CHECKED. Keep the profile disabled. The next action is to map the object at application+0x941C70+0x1A8 through an independent class/constructor/RTTI anchor, then return to the unresolved MenuSelect setter and MenuResources/binding-filter roles.

The full-image displacement scan for application offset +0x941C70 is an efficiency dead end in the current helper: after more than two minutes it had produced no progress/output, with a sampled process at roughly 148 CPU seconds and 803 MB working set. It was cancelled. Record this as INTERRUPTED / NOT CHECKED, never as zero matches. Before retrying a single-global query, inspect the known callsite windows or add a bounded-function option; preserve the full dependency rescan requirement for new executable hashes. Exact command and limits are in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).

A caller-context attempt started at interior RVAs and emitted misaligned initial instructions; mark those windows TOOL ERROR and discard them. Starting at verified .pdata roots 0x48E400 and 0x32F385 corrected the argument contexts for calls into 0x495560, but still did not identify the session predicate's meaning. Continue to start bounded disassembly at function entries; see the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).

### Session RTTI and scanner-efficiency follow-up, 16 October 2026

The 7.06 RTTI chain identifies `Session` (`0x4AAA640`) and derived `PlayfabSession` (`0x4AA9F98`); the latter's slot 8 is the same `0x1C7A60` stub as the base and returns constant true. Root `0xAD5A90` allocates `0xA48`-byte objects, temporarily installs the base `Session` vtable, finishes initialization, then installs the derived `PlayfabSession` vtable. It clears `+0x41C` and stores pointers at `[manager + 0x1A0 + index*8]`, structurally matching the load path's `+0x1A8` read. Manager RTTI and constructors also identify `cGcMatchmakingPlayfab` and its Steam subclass, but the constructor chain does not connect the manager argument to application global `+0x941C70`. A full direct-call scan found no direct calls to `0xAD5A90`; exact RTTI-slot and direct-RIP-reference probes found none. Treat the relationship as a strong static lead, not a mapping, and keep load semantics and the profile disabled.

The first direct-call scanner retained every decoded instruction and exceeded 800 MiB before output. It was replaced with a streaming `disasm_lite` scan that keeps only bounded context and prints progress. A known-target batch reproduced the established 4 and 1 caller counts for `0x495560` and `0x495640` across 52,110,272 `.pdata` bytes with zero skipped ranges; the optimized scan of `0xAD5A90` returned zero direct calls. The new `native_rip_xrefs.py` helper finds exact RIP-relative references for code or data RVAs, counts all results, caps printed examples, and reports progress. An uncapped shared-global query was truncated by the tool and must not be reused. Also, `+0x941C70` is an object displacement, not an image RVA; a query using it as an RVA was rejected and is a recorded tool error.

For exact commands, vtable relationships, constructor layout and remaining limitations, see the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md). Next bounded action: map the three-argument `MenuSelect` setter or find a specific dynamic call/registration path linking the `PlayfabSession` slot to the global manager; do not restart the broad member-displacement scan. Preserve unresolved label/resource and live lifecycle gates.

### MenuSelect shortlist and false leads, 16 October 2026

The fast `.pdata` candidate mode for `+0xA088` reported 64 operands against the prior detailed ledger's 29 writes. It is a shortlist only: stack-local references, reads, `cmp`/`idiv`, `lea` and other objects all appear. The helper now labels common read-only and address-only instructions separately, but all fast access tags remain heuristic. `0x153BE80` is chained to root `0x153BE60`; the root searches selected menu items by ID from `menu+0xA164` and restores the current index. Its only direct caller is `0x15286C0` at `0x15288C9`, passing menu and render state. Reject it as the old depth/index setter. The first scan against the chained interior returned zero and is superseded by the corrected root count of one.

`0x2CA6D0` is the QAM constructor and resets `+0xA088`; `0x2D1970` initializes an unrelated vector-like header with `+0xA088=0x401`. `0x15288D6` and `0x152B394` have no direct E8 callers or validated RTTI slots. The repeated detailed offset pass was cancelled after one minute without output; preserve the earlier completed 29-write result and mark only the repeat `NOT CHECKED`. Do not promote offset matches. Exact commands and body evidence are in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).

Next bounded action: inspect QAM trigger/action call setup for a real three-argument setter matching `(depth_field, depth, index)`. Keep `MenuSelect` unmapped until then; continue resource, label, binding and live-lifecycle gates before any 7.06 profile change.

### 7.05-to-7.06 scope and selection helper, 16 October 2026

The 7.05 supported game was already Cosmos; compare only the adjacent supported-to-target patch when attributing regressions. Do not explain a 7.06 refusal using Cosmos 7.0 features that were present in the working 7.05 baseline. The exact 7.06 guard refusal is caused by the changed executable hash, not proof of a gameplay failure. Official 7.06 notes list camera, Gravitino Coil, expedition ship-transfer and crash fixes, but do not mention Quick Menu or companions.

The old `MenuSelect` RVA `0x1518EF0` is invalid in 7.06. The correct exact-build candidate is the small leaf at `0x151ADB0`, outside `.pdata`: it checks depth `<=2`, nonnegative index, index below the selected vector count, then writes the selected index at `depth_field + depth*4 + 0x38`. Three direct callers from the `TriggerAction` root `0x1531E00` pass the matching `(menu+0xA050, depth, index)` roles. Keep the old RVA rejected and promote only `0x151ADB0` to `STATIC-CORROBORATED`; do not change the active 7.05 profile until remaining dependencies are mapped.

Adjacent `0x151AD40` is an append wrapper whose third argument is an item pointer; it has 57 direct callers and is not the selection setter. `native_call_xrefs.py` now supports `--limit-per-target` while retaining complete totals, avoiding context output truncation on high-fanout targets. The full-image indexed-store detail scan was too slow and was stopped; the `disasm_lite` candidate helper completed 52,110,272 bytes with zero skipped ranges. Its first parser draft mixed base and index registers and was corrected before using its final result. `0x152E5D2` is a builder-local checked selection write under root `0x152A1C0`, not a standalone function pointer.

Exact commands, call contexts, tool versions, false leads and remaining gates are in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md). Next bounded action: port the selector address without weakening the 7.05 guard, then resume unresolved label, resource, binding-filter and load semantics.

### QAM label output correction, 16 October 2026

A complete decode of vtable slot 9 (`0x153C0C0–0x153C5E4`) supersedes the earlier claim that both `RDX` and `R8` are 256-byte text outputs. The original `R8` argument is cleared with one byte at entry and is not used again as a pointer; later `R8` values are scratch or call arguments. The primary string is written through `RDX` with a 256-byte bound and a terminator at `+0xFF`. Slot 9 remains a plausible `MenuLabel` candidate because it reads the selected QAM item and formats localized text, but the third-argument meaning and actual virtual consumer are unresolved. The old two-argument/128-byte hook cannot be reused without checking argument forwarding and output size. Preserve the prior interpretation as a superseded false lead in the exact-build report.

Next bounded action: find a virtual call/consumer for slot 9 and identify the `R8` argument before changing the hook.


### Release lineage and bounded QAM slot-9 search, 16 October 2026

The project began with the native 0.10.0 test build for Cosmos 7.04 / Steam build 25442159. The 30 September 2026 commit `9460855` ported the native profile to Cosmos 7.05 / build 25624745 in 0.10.1, while retaining the legacy Python profile for 7.04. The current 0.10.2 package remains a 7.05 build. Treat a new compatibility request as 7.05-to-7.06, preserving that adjacent baseline when explaining changes; Cosmos 7.0 features are not new relative to 7.05.

For the unresolved QAM label slot, one bounded `native_vcall_xrefs.py` scan tested slot offset `0x48` together with QAM field `+0xA050`. It found no same-range direct virtual-call examples. A full `.pdata` scan found 789 calls in 523 function ranges for the simple `[register+0x48]` form; no listed range in the inspected QAM caller windows matched. This narrows only that exact dispatch shape. It does not rule out cached function pointers, wrapper calls, another slot expression or another consumer object.

Reusable method: first constrain generic virtual-call output by a known object field, then report the raw whole-image pattern count separately from caller identity. A zero constrained count is a bounded negative, not proof that the slot is unused. Preserve the exact executable hash, tool versions and both filtered and broad commands in the build report. Mark the label consumer and auxiliary argument unresolved until an independent caller or output consumer is established; do not enable the profile from RTTI slot identity alone.


Independent QAM slot-9 anchor: `native_rip_xrefs.py` found one direct RIP-relative code reference to the validated QAM vtable, at constructor instruction `0x2CA6EC` inside root `0x2CA6D0`. It found zero direct RIP-relative references to slot-9 method RVA `0x153C0C0` and zero to adjacent vtable-slot address `0x4A504E8`, across 52,110,272 `.pdata` bytes with zero skipped ranges. This is a constructor/vtable installation result, not a virtual-caller result; RIP-relative scanning cannot identify calls dispatched through the object's vptr. Preserve the exact command and keep slot-9 caller/third-argument semantics unresolved.


### QAM icon field and LoadTexture update, 16 October 2026

A displacement match is not an object identity. The `+0xA104` candidate scan returned 18 operands, but root/caller context separated the QAM field from unrelated nested objects. The QAM constructor `0x2CA6D0` clears its own `+0xA104`, and builder `0x152A1C0` reads that field from its `RCX` menu object and passes the value to item constructor `0x143D5D0`. This supports the QAM icon-value field for the exact 7.06 hash. In contrast, `0x1526240` receives `parent+0xDC0` from its only caller and is a nested constructor; its relative `+0xA104` must not be merged with the top-level menu field or reused as the old `MenuResources` hook.

The correct 7.06 `cGcRealityManager::LoadTexture` candidate is `0xEC8700`; old `0xEC6850` is an interior address. The new body's `[RCX]` path read and `RCX+0x10` handle write match the source `TextureRecord` layout, and the exact-hash scan found 294 direct callers. No validated RTTI slot or direct caller in the `0x15xxxxxx` QAM code area was found. Keep the generic loader `STATIC-CORROBORATED`, but keep the QAM resource-ready callback and safe load timing unmapped.

Reusable rule: for a repeated member displacement, establish the caller's incoming object base and any `this` adjustment before transferring field meaning. Keep direct-call counts, RTTI results and caller-area filters scoped to their exact pattern; a zero QAM E8-caller filter does not rule out indirect use. Exact commands and the resource-hook dead end are in the Cosmos 7.06 report.


Next bounded step: find a post-resource caller for the top-level QAM icon field `+0xA104` and establish that the resource manager is ready before loading custom icons. The nested `0x1526240` constructor and generic `LoadTexture` callers do not establish that lifecycle. Then resolve slot 9's auxiliary argument/output ownership and the load hook's local-versus-network semantics; keep the 7.06 profile disabled until the full dependency ledger and required live gate are closed.

### 7.06 slot-9 argument filter and QAM icon flow, 16 October 2026

The full `[vptr+0x48]` scan decoded 52,110,272 `.pdata` bytes with zero skipped ranges and found 789 calls in 523 ranges. All 789 context-12 examples were emitted. A post-last-call register screen produced 66 broad stack-`RDX` plus `R8`-write contexts across the image, but none in the `0x1500000–0x15FFFFF` range; this only covers visible context and is not a universal zero-caller result. Context 16 is unsupported by the scanner; use 12. The two apparent UI candidates `0x1556F68` and `0x1557C35` are false leads: helper `0x540660` is a three-range unwind group (`0x540660–0x5406FF`, `0x5406FF–0x54085A`, `0x54085A–0x54088D`), saves input `R8` to `RSI`, then overwrites `R8` as scratch without restoring it. A VA/RVA mix-up when querying `0x140540660` was corrected to helper RVA `0x540660`.

The `+0xA060` shortlist produced 32 operands but included stack locals. Root-aligned QAM inspection confirms vector lookup uses the `0xE0` item stride; QAM update and label logic read the action at item `+4`, while the first dword is copied through the context cache but not read as an icon in the inspected routines. The constructor receives `menu+0xA104` into that first dword, then the builder appends the item via `0x151AD40`. This is a confirmed value path, not a confirmed draw or resource lookup. Reusable lesson: trace register values across every intervening call because the Windows x64 volatile `R8` argument may be clobbered before a virtual dispatch; for repeated offsets, confirm the object base and decode the `.pdata` parent before assigning meaning.

Next bounded step: follow the cached first dword to an exact resource or renderer consumer and identify a proven QAM receiver for label slot 9. Keep the 7.06 mapping disabled until all dependency, semantic and live gates pass.

### 7.06 QAM context-cache caller audit, 16 October 2026

Helper `0x153C7A0` returns a destination at `object+0x2D0+index*0x3480` and has 14 direct E8 calls in three ranges: 11 from the QAM update rooted at `0x15286C0`, one from `0x153B5B0`, and two from `0x15406B4–0x1540AF6` with `RCX=parent+0xDC0`. At this point, the two adjusted-base callers were unresolved; see the 18 October follow-up, which ties their direct flow to QAM `TriggerAction`. QAM update copies whole `0xE0` records into this state-selected cache; the first dword's rendering/resource use remains unverified.

The generic fast scan for `+0x2D0` found 1,852 operands and printed the first 100 before truncation, mostly stack-local candidates. Combining `--fast-candidates` with `--access read` is unsupported; removing the access option corrected the invocation but not the usefulness of this broad query. Record it as `NOT CHECKED`, never as an absence result. Next bounded step: follow the exact returned cache pointer from the QAM update into its next consumer by call/data flow, not another global offset scan.

### 7.06 icon-field consumer and slot-9 search, 16 October 2026

The exact-hash `+0xA104` candidate scan returned 18 operands across 52,110,272 `.pdata` bytes with zero skipped ranges. A newly examined block at `0x1527BDD` belongs to a chained group rooted at `0x1527BD0`; it reads `this+0xA104`, runs member cleanup/reset helpers, and writes zero. Its only direct caller is `0x924D67` in root `0x924C90`, with `RCX=parent+0x116B10`. This was initially treated as a different subobject base from the QAM constructor; the 18 October offset-composition follow-up corrects that interpretation: the enclosing QAM member is at +0x115D50, so +0x115D50 + 0xDC0 = +0x116B10. The nested object identity is established by constructor-to-cleanup offset composition; the cleanup helper has no validated RTTI-backed method slot. It is not a resource-ready callback, and the helper method identity remains unknown.

The other +0xA104 hit at 0x1526240 is called from root 0x1540120 at 0x1540145 with RCX=parent+0xDC0. The 18 October owner-relative trace proves that this parent is the QAM wrapper at outer+0x115D50 and the target is its cGcQuickActionMenu child. The provisional resource-hook rejection in this 16 October note is superseded by the 18 October handle-dataflow correction: 0x1526240 calls the native resource-manager loader and stores the handle for QUICKMENU/SUMMONPET.DDS at child+0xA104. It is now static-corroborated for native QAM resource initialization; runtime lifecycle and custom-icon behavior remain unverified.

The QAM builder's item-constructor call at `0x152A22C` passes `menu+0xA104` in `EDX` to `0x143D5D0`. The constructor stores `EDX` at the first dword of the `0xE0` item and `R8D` at `item+4`; it does not load a texture. A complete direct-E8 scan found 56 calls to this constructor, printing 50 contexts; only the QAM-builder example was examined in this pass. This maps the value transfer into an item record, not the later rendering or resource lookup.

A new `native_vcall_xrefs.py` filter for slot offset `0x48` plus same-function displacement `+0xDC0` decoded all `.pdata` bytes and returned 8 calls in 7 ranges. It did not identify a receiver proven to be the QAM object. In one tempting case, `0x1559375` calls the slot with only `RCX` explicitly set and uses `EAX` as an integer for a following helper; it does not establish the QAM label call's required `RDX` output buffer or `R8` auxiliary argument. Other returned contexts remain unclassified. Keep slot 9's consumer and ABI unresolved. A first PowerShell summary used the automatic `$Matches` hashtable as an array and failed; the result was discarded and the bounded filter was rerun using `$hitIndices`.

Reproduction against Steam build `25732212`, executable SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`, with CPython 3.11.9, pefile 2024.8.26 and Capstone 5.0.7:

```text
py -3.11 -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0xA104 --fast-candidates --limit-per-offset 50
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1527BDD
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1527BD0 --size 0xAEB
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x1527BD0 --context 10 --limit-per-target 50
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2CA6D0 --context 8 --limit-per-target 20
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1540120 --size 0x1DB
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x1526240 --size 0x139C
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x143D5D0 --size 0x120
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x143D5D0 --context 10 --limit-per-target 50
py -3.11 -B tools/native_vcall_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --slot-offset 0x48 --require-field 0xDC0 --context 6 --limit-per-range 10
```

Next bounded action: trace the first item dword from the QAM builder through the appended item consumer to an exact resource lookup or draw call, and independently identify slot 9's caller by a proven QAM object flow plus its `RDX`/`R8` setup. Do not repeat displacement-only searches without a new anchor. `NOT CHECKED`: the exact post-resource callback, item icon's downstream semantic type, remaining slot-9 contexts, local-versus-network load meaning and live 7.06 behavior. Keep source/profile mappings unchanged and 7.06 fail-closed.

### 7.06 QAM cache filter false lead and latest release check, 16 October 2026

The official [Release Log](https://www.nomanssky.com/release-log/) still lists Cosmos 7.06 first and 7.05 second on 16 October 2026; no 7.07 entry is listed. For the exact 7.06 executable, RTTI confirms slot 9 at `0x153C0C0` belongs to `cGcQuickActionMenu` vftable `0x4A504E0`, with `cGcQuickMenuState` as a base. A whole-`.pdata` filter for `[vptr+0x48]` plus same-range displacement `+0x2D0` returned 13 ranges / 21 calls with zero skipped ranges; its sole `0x15xxxxxx` candidate at `0x1557ACD` is a false lead because root-aligned disassembly shows the matched `+0x2D0` is a saved `R15` stack local. This filter is only a shortlist, not a cache-consumer or absence proof.

The exact-hash commands and the full caller/range boundary are in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md). Reusable lesson: even a vtable-slot plus field-displacement filter can match a stack save in the same function; prove the base register and track the exact pointer returned by `0x153C7A0`. Next bounded action: follow one return pointer from QAM update `0x15286C0` through copies and subsequent calls until the copied record's first dword is read or converted to a proven resource handle. Do not repeat the global `+0x2D0` query. No mapping changed; 7.06 remains disabled.

### 7.06 QAM cache action path and caller-count correction, 18 October 2026

The official [Release Log](https://www.nomanssky.com/release-log/) still lists 7.06 above 7.05 on 18 October. The installed executable hash remains `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`, so previous exact-hash dependency scans remain reusable. A same-day readback of the [Nexus page](https://www.nexusmods.com/nomanssky/mods/4579?tab=files) still lists `0.10.2-native-test` as latest, last updated 3 October; its description limits support to Windows/Steam Cosmos 7.05 build `25624745`.

The exact direct-call list for `0x153C7A0` contains 14 calls: 11 from the QAM update, one from its selected-item context-snapshot helper, and two from an input-dispatch function. Correct the earlier 12-call QAM-update count; it was a transcription/count error. In the input-dispatch path, the `+0xDC0` object is passed both to `0x153C7A0` and to known QAM `TriggerAction` at `0x1531E00`; the cached item pointer is passed in `RDX`, with `R8D=0`. This resolves the receiver identity for those direct callers, making all 14 listed direct calls statically QAM-related, while leaving indirect callers outside the scan's scope.

The cache is used for action/context snapshots and comparisons in the inspected paths. `TriggerAction` reads the incoming cached item's action identifier at `+4` and does not read its first dword before reusing that register for another object. The equality helper checks `+4` and other state fields, not the icon value at offset zero. This is a useful negative for the icon-rendering hypothesis, not proof of no renderer elsewhere. Full exact-hash commands and boundaries are in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).

Next bounded action: identify the real slot-9 caller and its `RDX`/`R8` setup, then close the safe resource callback, binding-filter and local/network load gates. Keep 7.06 disabled until the exact mapping and live acceptance gates are complete.

### 7.06 slot-9 caller filter re-audit, 18 October 2026

The `slot 0x48 + same-function +0xDC0` scan returned 8 calls in 7 ranges after decoding all `.pdata` bytes with zero skipped ranges. It did not prove a QAM receiver or slot-9 ABI. Candidate `0x155A45F` at root `0x1559BB8` is a false lead: `RDX` points to a stack buffer before a helper call that may clobber it, `R8` is set after the virtual call, its `+0xDC0` reference uses a different base, and RTTI found no validated vtable slot for the root. At the time, the seven remaining displayed contexts were not classified; the 18 October receiver-identity audit below resolves them as false-positive offset matches, without proving absence of other callers.

The exact list, root-aligned disassembly and commands are in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md). Reusable rule: a generic field-displacement filter can match unrelated object bases; verify caller receiver provenance and preserve volatile `RDX`/`R8` arguments across every intervening call. Next bounded action: follow the verified QAM subobject `parent+0xDC0` into a candidate dispatch and require the full native argument setup. Keep 7.06 disabled.

### 7.06 slot-9 receiver shortlist correction, 18 October 2026

Root-aligned inspection of all eight `slot-offset 0x48` plus `+0xDC0` matches shows that none demonstrates the QAM object as the dispatch receiver. The two `0x1493xxx` calls use `RSI+0xB90`/`RSI+0xA10` while the field hit uses `[RSI+0xDC0]`; calls `0x155395E` and `0x155665F` use `RSI`/`RDI` receivers while the field hit is based on `R13`; `0x155937B` uses `RSI` and reads `[R15+0xDC0]` only after dispatch; `0x155A45F` uses `R14` while the field hit is `[RDX+0xDC0]`; and calls `0x157C0AA`/`0x17F67E1` dispatch through a global object at `global+0x905B20` while their `+0xDC0` operands refer to local/other objects. Where a register alias is not established, leave identity unproven rather than treating the displacement as a match.

This closes the eight-hit shortlist as non-evidence for a QAM receiver: none proves that its call receiver is the verified `parent+0xDC0` subobject. Some shown expressions are directly distinct; others lack alias proof. It does not prove there is no slot-9 caller because the scan does not propagate object identity through arbitrary fields or calls. Reusable rule: require the call's exact `RCX` expression to originate from a verified QAM subobject; a same-range displacement is not object provenance. The full command set and exact executable identity are in the linked build report.

`NOT CHECKED`: the actual slot-9 caller and `R8` meaning, icon/resource consumer, safe resource-ready callback, binding-filter return site, local-versus-network load semantics and live 7.06 behavior. Next bounded action: continue from a verified QAM owner/subobject pointer and prove the receiver and complete `RDX`/`R8` setup at any candidate slot-offset `0x48` dispatch. Keep 7.06 disabled.
### 7.06 QAM nested-owner offset correction, 18 October 2026

The earlier +0x116B10 cleanup path was incorrectly called a different subobject from constructor parent+0xDC0. The QAM constructor is itself embedded at enclosing-member +0x115D50; it then constructs the QAM child at its own +0xDC0. Compose offsets before comparing bases: 0x115D50 + 0xDC0 = 0x116B10. The matching cleanup call at 0x924D67 therefore receives the same nested QAM child. The outer constructor and cleanup roots are both called through member offset +0x732920, supporting the enclosing path, though the outer class name is not RTTI-validated.

This corrects object identity only. 0x1527BD0 is a teardown cleanup reached from root 0x924C90, not a safe resource-ready callback; its method name remains unknown. Slot-offset 0x48 plus displacement 0x116B10 returned only that cleanup range, whose two virtual calls use separate receivers at +0x110998 and +0x1109A0. Filters for +0x115D50 and for both +0x115D50/+0xDC0 returned zero calls after full .pdata decoding. Treat these as bounded same-function-filter results, not absence proof. Continue with QAM pointer provenance and full RDX/R8 ABI; do not repeat the exact displacement-only queries. The exact-build report records commands and boundaries. No source mapping changed; keep 7.06 fail-closed.


### 7.06 QAM setup path and selector search, 18 October 2026

QAM owner composition is now explicit: enclosing member +0x732920, QAM wrapper +0x115D50, nested QAM child +0xDC0, giving global+0x849430. A mistaken exploratory sum 0x849A30 was an arithmetic error; discard that query's zero result. The corrected child offset is independently referenced at 0x55900A and twice in 0x1464200.

Function 0x1540120 has two direct callers, one passing global+0x848670 and one passing parent+0x115D50. It calls 0x1526240 with wrapper+0xDC0; that helper has one direct caller. The earlier statement that its body did not establish a resource load was wrong: 0x1526240 calls the resource-manager loader and stores the handle for QUICKMENU/SUMMONPET.DDS at QAM child+0xA104. The exact evidence and limits are recorded in the 18 October resource-initializer correction below and in the build-specific report. Function 0x1464200 selects a menu-state object by the field at global+0x849424 and invokes slot +0x58 on the selected object. That is confirmed QAM state flow, but it does not call slot 9 (+0x48).

The corrected same-function filters for slot +0x48 plus child offset +0x849430 returned zero calls; filtering by selector field +0x849424 produced two unrelated calls through global+0x905B20. One appears beside a QAM input-dispatch call, but the QAM dispatcher uses other slots. Record these as bounded false leads. Next use the selector-driven state flow to find further callers; require the exact QAM receiver and RDX/R8 ABI before promoting a match. Do not reuse the invalid +0x849A30 result. No native mapping changed; keep 7.06 fail-closed.


### 7.06 QAM chained selector path review, 18 October 2026

The +0x849430 QAM pointer hit at 0x55900A sits inside chained range 0x558FB5-0x559023. The full eleven-range group rooted at 0x558E40 uses the selected QAM object only to test byte +0x9A. Its indirect calls at 0x559626 and 0x559660 dispatch through slot +0x20 on a separate object at +0x933B78; no +0x48 dispatch uses the selected QAM pointer. This resolves the cross-range false lead and does not establish an actual slot-9 caller. Reusable rule: when an exact object displacement occurs in chained unwind metadata, inspect the complete parent group before treating a same-range slot filter as conclusive.


### 7.06 QAM resource-initializer recovery, 18 October 2026

Correction: the QAM setup helper at 0x1526240 is not merely member/string initialization. The earlier review missed its resource-manager call and output-handle flow. The old 7.05 `MenuResources` address 0x1524330 lies inside unrelated four-argument function root 0x1524230–0x152443C, so that address remains rejected.

The replacement 0x1526240 is a one-object QAM setup method called at 0x1540145 with RCX=wrapper+0xDC0, the verified nested cGcQuickActionMenu child. At 0x1526E89 it calls helper 0x2D63EA0 with a resource manager, output-handle temporary, type 7 and a path. The direct RIP string reference at 0x1526E5C resolves to `TEXTURES/UI/FRONTEND/ICONS/QUICKMENU/SUMMONPET.DDS`; after the call, the method compares and updates the handle at child+0xA104. This statically corroborates the resource-initialization role and provides a post-load return point. It does not yet prove runtime thread, repeated-call or teardown safety, nor live custom-icon behavior.

Reusable rule: for resource-hook recovery, follow the entire path from the candidate's caller object through the resource-manager call, resource path, output temporary and final object field. A matching field offset, a constructor zero, or a generic loader signature alone is insufficient. Treat function-level post-load ordering as static evidence only; preserve live lifecycle as a separate gate. The 18-operand fast displacement scan was used only to shortlist exact roots; its access hints were verified in focused disassembly. Two slower detailed read/write scans were interrupted and remain NOT CHECKED, not zero-match results. A PowerShell/Python path-quoting error was corrected with a here-string and was a command error, not a binary result.

The standalone custom-texture loader candidate 0xEC8700 is separate from the QAM's generic resource-manager calls. Its body matches the mod's path-at-zero and handle-at-+0x10 record, and its complete direct-call scan returned 294 references with none from 0x15xxxxxx functions. Keep the custom-icon call-timing question distinct from native QAM resource initialization.

Carry the already-static `MenuSelect` replacement `0x151ADB0` and binding-filter return site `0x15292F5` forward; do not repeat their mapping searches. The next bounded step is to trace the remaining QAM label consumer and output-buffer ABI, then resolve the load-hook local/network meaning and continue the full source-dependency ledger. Keep the exact 7.06 profile disabled until all static and live gates pass.


### 7.06 binding-filter return register confirmation, 18 October 2026

The exact return site `0x15292F5` after `GetButton` is already statically corroborated by its selected-item path. A focused root-aligned window additionally confirms `RDI` is the QAM object: after return, the handler reads depth at `+0xA050`, selected index at `+0xA088+depth*4`, vector count/data at `+0xA05C/+0xA060+depth*0x10`, and the selected `0xE0` item/action. That matches the base register and layout expected by the existing generated binding filter. `0x15292AB` remains a different fixed-button path.

This is static ABI/layout evidence only. It does not prove the live filter effect, all input paths or thread/lifecycle safety. The source's single return-site constant still targets the approved 7.05 profile; do not replace it with the 7.06 value until source chooses the site from an exact profile. The static `MenuSelect` replacement `0x151ADB0` is already recorded above as corroborated; selection mapping is not an open step.

Reusable rule: for a return-address detour, verify both the exact post-call branch and the live register carrying the object expected by generated code. A correct return address with a wrong volatile/base register would still corrupt the filter. Keep live effect and input-thread acceptance separate from static register evidence.

Next bounded step: map the actual QAM label caller and `R8` output ownership, then finish local-versus-network load semantics and the remaining source dependency ledger. Keep 7.06 fail-closed.

### 7.06 QAM slot-9 label-output method mapping, 18 October 2026

Exact-hash disassembly of all three chained ranges for RTTI-backed QAM vtable
slot 9 (`0x153C0C0–0x153C5E4`) now statically corroborates the method's label
output role. It validates the selected item and menu depth, chooses localized
text, and writes through its saved `RDX` argument with a 256-byte bound and a
terminator at `+0xFF`. At entry it clears one byte through original `R8`, then
reuses `R8`; that argument's semantic role remains `NOT CHECKED`.

This corrects “likely label” to “label-output method statically corroborated”
without closing the actual virtual caller, downstream UI consumer, or `R8`
ownership/capacity. The old 7.05 two-argument hook and 128-byte caption write
are not a safe 7.06 contract. Preserve the exact source profile and fail-closed
guard. `MenuSelect` `0x151ADB0`, resource initialization `0x1526240`, and
binding return `0x15292F5` were already statically mapped; do not spend another
search pass on those roles.

Reusable rule: a validated RTTI vtable slot plus complete selected-item and
output-buffer dataflow can establish a method's semantic role without a direct
caller. Keep that method evidence separate from the actual dispatch site,
receiver provenance, output consumer, buffer ownership, and volatile argument
setup. A caller scan with no match remains a bounded negative, not proof of no
virtual callers.

Next bounded step: continue from the verified QAM child pointer to find an
actual `+0x48` dispatch and establish `RCX`, full `RDX`/`R8` setup and output
ownership. In parallel, resolve local-versus-network load-hook semantics and
continue the exact-source dependency ledger. See the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md) for ranges and exact-hash reproduction commands.


### 7.06 load-candidate argument pass, 18 October 2026

The caller-anchored candidate `0x573500` has eight chained ranges and four
direct callers. The callee saves `RCX`/`RDX`/`R8` and `R9B`, reads the common
save object at `RDX+0x8980`, and checks the fifth physical argument at
`0x578B2F`; the zero path makes a helper/setup call ending at `0x6019F0`.
The four callsites pass different fifth/sixth values; three provide `R9=0`,
while one passes byte `[RDI+0x4BE6A0]`. These are physical-argument facts only.
They do not name the network/reset flags or prove which caller is local versus
network. The old `0x572C40` address remains rejected because its containing
entry `0x572410` is a player-state constructor.

Reusable rule: preserve ABI position and semantic meaning as separate columns.
A candidate can match argument count, common-object offset and caller shape
without proving that the source typedef's names apply. Trace the producers of
flag arguments and the branches that consume them before calling a parameter
`network` or `resetting`.

Next bounded step: identify the object/class behind
`global+0x941C70+0x1A8` and the meaning of `+0x41C`, then classify the four
caller paths as local or network before deciding whether this role can replace
the 7.05 hook. Keep 7.06 fail-closed. Exact callsites, group ranges and replay
commands are in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).


### 7.06 load flag producer correction, 18 October 2026

The fast exact-hash scan found seven `+0x4BE6A0` operands. Root-aligned
disassembly verified all seven results, including initialization at
`0x487D1B` and a byte writer at
`0x4956B8`; the latter is inside a chained segment under root `0x495640`, not
a standalone entry at `0x495675`. A direct caller search on interior `0x495675`
returned zero, but resolving the unwind root showed one caller at `0x4955F8`.
That caller reads `global+0x941C70+0x1A8`, checks fields `+0x418` and `+0x41C`,
calls vtable slot `+0x40`, derives a Boolean in `R9B`, and stores it through
the `0x495640` path. The load-role candidate later passes the same field in
`R9` at `0x4906BD`.

This strengthens the session-linked flag lead but does not prove the global
manager class or that the Boolean means network mode. The three other direct
load-candidate callers pass `R9=0`; keep all four caller contexts and stack
flags distinct. Reusable lesson: a zero direct-call scan against a chained
interior target is not a bounded negative about its root; resolve the unwind
group first. Full commands, exact counts and evidence boundaries are in the
[Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).

Next bounded step: identify the producer/meaning of session field `+0x41C`
only inside methods tied to validated Session/PlayfabSession RTTI or
constructor evidence, then follow `application+0x941C70+0x1A8` and classify the
four load-candidate paths. A global `+0x41C` scan returned 207 hints, printed
200 and was truncated; it is too broad to establish this member's writer. An
unqualified RTTI name query returned zero and a generic method probe was
interrupted; neither proves class or method absence. Keep 7.06 disabled.

### 7.06 session-flag search boundary, 18 October 2026

A broad fast-candidate scan for `+0x41C` returned 207 operands and printed
200, with the result marked truncated. This common displacement is not a
useful session-member search and supplies no class or semantic evidence. An
unqualified `PlayfabSession` type-name query returned zero locators; passing a
data RVA as `--target-rva` was rejected; a generic method-RVA probe ran more
than 60 seconds without output and was interrupted. These are bounded search
failures, not proof that the session class or methods are absent.

Reusable rule: constrain displacement scans to a verified object family and
use exact decorated RTTI evidence or constructor/vtable paths. Respect whether
a tool argument expects executable code or RTTI data. Do not infer from a
truncated candidate list; mark no-output interrupted work `NOT CHECKED`.

Next bounded step: trace the `+0x41C` writer within validated
`Session`/`PlayfabSession` methods and establish the object identity behind
`application+0x941C70+0x1A8`. Then classify the four load-candidate paths. The
current 7.06 profile remains disabled; see the exact-build report for the
session-linked flag producer evidence.


### 7.06 PlayfabSession member check, 18 October 2026

Using the full decorated RTTI name returns one validated
`PlayfabSession` vftable with 26 slots. Slot 17 (`0x239DF0`) tests the byte at
`this+0x41C` while processing the session's `+0x720` entries. Slot 20
(`0x238750`) reads four consecutive 16-byte values beginning at `+0x41C`.
Slot 11 (`0x237820`) directly calls helper `0xACA370`, which writes through
the same 64-byte region; only the first byte of its first stack source is
explicitly zeroed in the inspected body. Do not label the area a network
flag or claim the full region is zeroed.

The exact application-global `+0x941C70+0x1A8` object is still not tied to
this vftable. Matching member offsets and slot `+0x40` make it a strong lead,
not proof of object identity. A partial type-name probe returned zero; use
the full decorated name. A decode started at interior RVA `0x238BB0` was
misaligned and discarded; start from slot-20 root `0x238750`.

Next bounded step: trace the `PlayfabSession` region's producer and the
manager's slot-1 population, then classify the four load-role callers. Keep
semantic names and 7.06 runtime behavior `NOT CHECKED` and the profile disabled.


### 7.06 PlayfabSession slot population and source checkpoint, 18 October 2026

Root `0xAD5A90` preserves its incoming `RCX` manager pointer in `R14`. Its
three-byte index table is at RVA `0x4A49134` and contains `00 01 02`. The loop
allocates a `0xA48`-byte object per index, clears the leading byte at
`+0x41C`, initializes it first with the base `Session` vtable `0x4AAA640`,
then replaces that vtable with the derived `PlayfabSession` vtable
`0x4AA9F98`. At `0xAD5D70` it stores each object at
`[R14 + index*8 + 0x1A0]`. Thus this constructor's index-1 object is stored at
manager-relative `+0x1A8`, the exact field read by the load-adjacent path.
This confirms the class and layout of values produced by this constructor;
it does not prove that its `RCX` instance is the manager pointer reached from
`application+0x941C70`, or that index 1 means local, online, or network.

The exact decorated name `.?AVSession@cGcMatchmaking@@` validates one
19-slot base vtable at `0x4AAA640`. A guessed name under the
`cGcMatchmakingPlayfab` namespace returned zero locators; that spelling was
wrong and is not evidence of absence. The previously validated exact
`PlayfabSession` query remains the correct derived-type anchor.

A global fast-candidate scan for displacements `+0x1A0` and `+0x1A8` was
interrupted after decoding approximately `0x2D040A2` runtime-function bytes,
before a result summary. Record it as `INTERRUPTED / NOT CHECKED`, never as a
zero-match result. It was a poor semantic search because these are common
member offsets; the constructor's exact index table and load-path callsite
provide the useful bounded evidence. Reuse rule: follow constructor index
tables and final vtable writes, but keep owner identity and index meaning
separate from an offset match.

Reproduction against the unchanged Steam build `25732212` / NMS.exe SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`:

```text
py -3.11 -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0xAD5A90 --size 0x30E
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVSession@cGcMatchmaking@@" --max-slots 64
py -3.11 -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --type-name ".?AVPlayfabSession@cGcMatchmakingPlayfab@@" --max-slots 64
py -3.11 -c "import pefile,sys; p=pefile.PE(sys.argv[1]); print(p.get_data(0x4A49134,3).hex())" "<verified Cosmos 7.06 NMS.exe>"
```

The official NMS Release Log was rechecked on 18 October 2026: Cosmos 7.06
remains above 7.05 and no 7.07 entry is present. Nexus still lists package
`0.10.2-native-test`, last updated 3 October 2026 and targeting 7.05. The
GitHub repository's `main` and local `origin/main` both resolve to
`f7d97b61fcf152677d0d30de34f6c1b48675c436`; this update branch has research
documentation and helper changes only, with no mod-source or profile update.

`NOT CHECKED`: whether the manager argument in `0xAD5A90` is the exact object
at `application+0x941C70`, the semantic role of index 1, local/network meaning
of the load predicate, indirect constructor callers and live 7.06 behavior.
Keep 7.06 fail-closed. Next bounded action: classify the four load-role
callers using their full state transitions and resolve the application-global
manager identity; do not infer local/network semantics from slot index.


### 7.06 load-candidate caller context, 18 October 2026

The exact-hash `native_call_xrefs.py` scan found four direct calls to
`0x573500` across `52,110,272` `.pdata` bytes with zero skipped ranges.
`0x2E088F` is in the five-range unwind group rooted at `0x2DBBB0` and passes
the candidate an object at `+0xAAD0`, a save-data pointer at `RBP+0x2240`,
`R8=R14`, `R9=0`, fifth argument `1`, and sixth argument `R15B`. Calls
`0x48EECC` and `0x48F983` are in root `0x48E400`; both pass an object at
`RSI+0xAAD0`, data at `RBP+0xC0`, `R8=R15`, `R9=0`, and sixth argument
`BL`, while the fifth argument comes from `DIL` or `R13B`. Call `0x4906BD`
is in adjacent root `0x48FA60`; it passes `RDI+0xAAD0`, data from
`[RBP+0x3C0]`, `R8=RSI`, the session-derived byte `[RDI+0x4BE6A0]` in `R9`,
and zero fifth/sixth arguments. These are distinct caller paths and physical
argument facts; none independently names the parameters or proves local vs.
network behavior.

The session predicate helper `0x495560` is called four times from roots
`0x32F385` and `0x48E400`. In the latter, its return gates branches after
state comparisons against 0, 4 and 6; the call arguments include `RDX=0`
then `1`, and `R8=-2`. In the former, it receives `R8=-2` with manager-like
objects at global-relative `+0xE70` and `+0xE90`. This shows the predicate is
used during state processing, but the sentinel and flag meanings remain
unresolved. Do not transfer `network_client` or `resetting` names from the
7.05 source prototype based only on ABI position.

An initial `--context 18` request was rejected before scanning because this
helper caps context at 12 instructions. Rerunning with `--context 12` gave
the results above. Reusable rule: check helper limits before parallel scans;
record invocation errors separately from binary findings.

Reproduction against the exact 7.06 executable hash:

```text
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x573500 --context 12 --limit-per-target 10
py -3.11 -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x495560 --context 12 --limit-per-target 10
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2E088F
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x48EECC
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x48F983
py -3.11 -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x4906BD
```

Next bounded action: identify the owning classes/state paths for the three
distinct caller roots and trace a non-ABI semantic anchor for the R9 and stack
flags. Keep the load hook and 7.06 profile fail-closed until local/network and
lifecycle semantics are established.


### 7.06 matchmaking vtable and application-owner boundary, 18 October 2026

Exact RTTI queries validate `cGcMatchmaking` at vtable `0x4AA9D10`,
`cGcMatchmakingPlayfab` at `0x4AAA070`, and
`cGcMatchmakingPlayfabSteam` at `0x4AAA358`. The Steam constructor root
`0xAC7050` calls the Playfab base constructor `0xAC73D0`, then installs the
Steam vtable. Its sole direct caller is `0xAE894E` in chained range
`0xAE881A–0xAE8BB5`, rooted at `0xAE8810`. That caller allocates `0xA60`
bytes; the root `0xAE8810` is itself called at `0x2C6D3F` with
`RCX=application+0x937130`. It stores the constructed Steam manager at
`application+0x937130+0xAB40 = application+0x9E670`, then invokes its
virtual slot `+0x38`.

Steam vtable slot 8 (`0x24B920`) is a six-range method. It reads the session
pointer at `this+0x1A8`, checks the pointed object's `+0x418` state against
4, compares bytes beginning at the session's `+9` with manager data at
`+0x7CC`, and later reads session fields `+0x410` and `+0x40C`. This is
class-specific corroboration that this manager family uses a session pointer
at `+0x1A8`. It strengthens the structural match with the load predicate at
`0x495560`, which reads `[application+0x941C70]` and then `+0x1A8`.

The owner path is still unresolved: the Steam manager we traced is stored at
`application+0x9E670`, while the load path starts from the distinct field
`application+0x941C70`. The bounded scans so far have not established an
alias or copy between those fields; they do not prove that no such path exists.
The session-array helper `0xAD5A90` also has no direct E8 caller, so it is not
linked to the Steam manager instance by the constructor chain. Do not promote
the constructor's known instance to the load path's object. An early candidate
that slot 7 (`0x24B8F0`) initializes the session
array was rejected: its body calls base method `0x22B230` and writes
`this+0x6C0`; the session-pointer reads are in slot 8 (`0x24B920`). The direct
E8 scan for `0x24B8F0` returned zero as expected for a virtual method call;
resolve vtable slots before interpreting direct-call negatives.

Reproduce the class, constructor and session-slot evidence against the exact
7.06 hash:

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

`NOT CHECKED`: whether the object at `application+0x941C70` aliases the
constructed manager at `application+0x9E670`, the load-path object's exact
RTTI type, the session slot's semantic label, local/network interpretation,
and live behavior. Next bounded action: identify the owner/value path for
`application+0x941C70` without repeating a whole-image common-offset scan.
Keep 7.06 fail-closed.


### Corrected owner chain for the 7.06 load predicate, 18 October 2026

The immediately preceding section's `0x9E670` sum was incorrect. At
`0x2C6D3F`, the application setup passes `application+0x937130` to
`0xAE8810`; that constructor stores the `0xAC7050` Steam matchmaking object
at `[parent+0xAB40]` (`0xAE895B`). The checked sum is
`0x937130 + 0xAB40 = 0x941C70`, exactly the application member read by
`0x495560` (`0x4955B9`). The cGcApplication RTTI/vtable path and writes to its
`+0x38` application-pointer cell at RVA `0x6E8D708` were also traced. Thus
the owner/type identity gate is **closed statically**:
`application+0x941C70` is the constructed
`cGcMatchmakingPlayfabSteam` instance. The old different-fields conclusion
is a corrected false lead, not an open question.

The manager's `+0x1A8` session slot and the load predicate's `+0x418` and
`+0x41C` checks still need semantic and population tracing. The session-array
helper `0xAD5A90` has no direct E8 caller; its indirect caller/value path is
not established. One additional write to the application pointer cell at
`0x62D849` uses `R14`; its value and caller path remain `NOT CHECKED`. Keep
7.06 fail-closed while these gates and menu/resource/source-dependency gates
remain open. See the final correction section of
`NATIVE-25732212-COMPATIBILITY.md` for exact commands and evidence.


### Session-slot population boundary, 18 October 2026

The `cGcMatchmakingPlayfab` base constructor clears manager slots `+0x1A0`
and `+0x1A8`; the Steam-derived object inherits those null initial values.
The RTTI-anchored member scan covers the manager's full chained method groups
and found seven `+0x1A8` reader groups but no writes to `+0x1A0/+0x1A8/+0x1B0`
inside the 36 methods with `.pdata` roots. `PlayfabSession` methods similarly
read `+0x418/+0x41C` but have no writes to the checked fields in their 18
`.pdata` method groups. Methods without `.pdata` and external/dynamic writers
remain outside those negative results.

The only confirmed stride-8 indexed pointer store into the manager array is
still in `0xAD5A90`, whose direct, RIP-relative and RTTI-vtable reference
passes found no caller/link. Another fast-indexed candidate at `0x428E52` was
rejected after exact decode showed an effective `0x30` record stride. A broad
`+0x1A8` fast shortlist returned 2,069 hints and truncated at 1,000; it is not
a useful writer inventory. Do not repeat common-offset scans without a new
owner or caller anchor. Use `native_vtable_member_xrefs.py` for class-scoped
method-group searches and check the computed element stride for indexed
stores.

The load-related session predicate appears in eight filtered ranges with 12
virtual calls to session slot `+0x40`, all using application member
`+0x941C70` and session offsets `+0x418/+0x41C`. This confirms repeated use,
not the field names or local/network semantics. The `0xAD5A90` population
path, runtime timing and remaining menu/resource/source dependencies keep the
7.06 profile disabled. See the exact-build report's session-slot checkpoint.


### QAM slot-9 filters, load-flag boundary and release-label correction, 18 October 2026

Rechecked the official [NMS Release Log](https://www.nomanssky.com/release-log/)
and the live [Nexus files page](https://www.nexusmods.com/nomanssky/mods/4579?tab=files)
on 18 October. Cosmos 7.06 remains the newest listed game release. The current
Nexus version is `0.10.2-native-test`, file 49469, uploaded 3 October; file
49367 is the earlier `0.10.1-native-test`. The repository's native profile
still targets Windows/Steam Cosmos 7.05, build 25624745. Corrected stale
current-version statements in `DEVELOPMENT.md` and `AGENTS.md`; the package
number does not change its game-build target.

Three exact-hash slot-9 filters for QAM field pairs `+0xA050/+0xA088`,
`+0xA05C/+0xA060` and `+0xA100/+0xA104` each decoded all `52,110,272`
`.pdata` bytes with zero skipped ranges and returned zero matching ranges and
calls. These are same-range displacement filters, not receiver-alias proof or
a universal no-caller result.

The exact-hash `+0x4BE6A0` fast scan returned seven operands. Constructor
`0x487CE0` zeroes a 16-bit region there and has one direct caller at
`0x307E08`, passing a global-relative `+0xE70` object. Read candidate
`0x48FA60` loads the byte from `[RDI+0x4BE6A0]` into `R9B` at `0x49069A`, then
calls load-role candidate `0x573500` at `0x4906BD`. Another function rooted at
`0x495675` writes `[R12+0x4BE6A0] = BL` at `0x4956B8`. This records a producer
and a caller-side source, but does not name the byte or prove local/network
semantics.

For setter root `0x495675`, direct E8 references, direct RIP-relative memory
references, validated RTTI-vtable slots, direct immediate jumps and literal
preferred-base VA references were all zero in their stated scan scopes. A
zero from each encoding is not proof that the function has no dynamic caller.
`native_branch_xrefs.py` and `native_absolute_pointer_xrefs.py` were added as
reusable read-only probes; the first branch-scan output had a missing byte
counter and was discarded. The corrected scan decoded all `52,110,272`
`.pdata` bytes with zero skipped ranges. The RTTI probe processes one
`--target-rva` per invocation; a multi-target attempt was rerun separately.

Analysis environment: CPython 3.11.9, pefile 2024.8.26, Capstone 5.0.7. New
helper SHA-256 values: `native_branch_xrefs.py`
`FA8DBC157E094F8C793A29E46AFA0946059F69AD7070218E6D72452D9914034E`;
`native_absolute_pointer_xrefs.py`
`5E6F37D2DEDF74B5691C537B4E1F19908926DD76062686EECB5A14E516BC5F46`.
Exact commands, remaining tool digests and per-role status are recorded in
[`NATIVE-25732212-COMPATIBILITY.md`](NATIVE-25732212-COMPATIBILITY.md).

Next bounded action: resolve the producer/dynamic registration for
`0x495675` or independently establish the owner and meaning of
`+0x4BE6A0`; otherwise keep load local/network semantics `NOT CHECKED` and
continue the exact-source dependency ledger. Keep the 7.06 profile fail-closed.


### Ownership predicate and hand-query ABI, 18 October 2026

The old 7.05 ownership helper RVA `0x508200` is inside an instruction in
Cosmos 7.06: the function-root decode from `0x508107` shows an instruction
ending at `0x508201`. A full `.pdata` direct-call scan found no calls to
`0x508200`. Treat it as a rejected old address, not a relocated entry.

Leaf `0x508290` has no `.pdata` entry, but the exact call flow corroborates it
for the owner-and-slot predicate: owner-update root `0x508DC0` preserves the
incoming object in `RSI`, loads its active slot from `+0x1B9300`, restores the
same object to `RCX`, and calls the leaf. Its body checks a `0x24A0`-stride
record and returns a Boolean in `AL`. This matches the `services.owned`
machine interface. It is also called from the native `CanSummon` path with the
application companion table and slot. Keep the source unchanged until the
full dependency and runtime gates are complete.

`GetDominantHand` candidate `0x14874B0` returns the application hand field in
`EAX` or zero. It forwards incoming `RCX` to `0x1C84D0`, but that helper uses
thread-local and global data without consuming incoming `RCX`; the no-argument
source call shape is statically compatible. A complete `.pdata` E8 scan found
zero direct callers, which does not rule out virtual dispatch. Record the
service as statically corroborated, not live-verified.

The internal helper `0x50A520` has six direct callers including `CanSummon`
and the owner update. Its observed ABI is `RCX` object, `EDX` slot, `R8` output
buffer and Boolean `AL`; its full semantic label remains open. It is not a
replacement for the enclosing source `CanSummon` service.

One caller-scan attempt used unsupported `--context 14` and failed argument
validation before decoding. The corrected `--context 12` scan decoded all
`52,110,272` `.pdata` bytes with no skipped ranges. Preserve this as a tool
argument error, not as a negative scan.

Reusable method: decode from the verified function root, track each argument
through chained ranges and nested calls, and distinguish a byte-compatible
candidate from live evidence. A helper that appears not to read `RCX` can
still receive it through an unchanged call argument, so inspect the callee
before resolving the ABI.

The native profile remains Windows/Steam Cosmos 7.05 only; 7.06 stays
fail-closed. The next bounded action is to trace the owner of the load flag at
`+0x4BE6A0` and determine whether its producer can be tied to local-versus-
network load semantics. Keep the QAM slot-9 caller, label consumer, live
behavior and remaining exact-source dependencies `NOT CHECKED` until their
own evidence is recorded.


### Corrected load-flag root and 22 October release recheck

The earlier load-flag entry treated `0x495675` as a function root. It is a
chained `.pdata` range entry in the 14-range group rooted at `0x495640`; the
old zero-caller/reference results against `0x495675` were scoped and did not
show that the writer was unused. The corrected direct-call scan found one
caller of root `0x495640`, at `0x4955F8` under caller root `0x495560`.
That path derives `R9B` from a session-like pointer at application
`+0x941C70+0x1A8`, using `+0x418`, virtual slot `+0x40` and byte `+0x41C`.
The writer stores it at `[RCX+0x4BE6A0]`; a later reader calls `0x48FA60`
with the same object and passes the byte to `0x573500`. Same-object flow is
static evidence only; class identity, field meaning, local/network semantics
and live behavior remain `NOT CHECKED`.

The corrected root has 1 direct E8 caller and zero results for RIP-relative
references, validated RTTI-vtable slots, direct jumps and literal preferred
base VAs in their recorded scopes. Five raw 32-bit RVA hits each for
`0x495640` and `0x495675` were `.pdata` Begin/End/Unwind metadata, not
pointers. Reusable classifier: `tools/native_rva_data_xrefs.py`, SHA-256
`C1B88B6910DAD1FF0D2EF556A2C94C58B94F04E0B06B20253CDD561F94CE123D`.

On 22 October 2026, the official Hello Games release log still listed
Cosmos 7.06 as newest, and Nexus still listed `0.10.2-native-test` as latest
(last updated 3 October). No 7.06 source/profile mapping changed.

Next bounded action: rerun the exact `+0x41C` writer inventory with a
bounded-function strategy; inspect candidates only after anchoring the
receiver to its RTTI owner and tracing its argument source. Then resume the
remaining MenuSelect/resource and exact-source dependency gates. Keep 7.06
fail-closed.


### 7.06 Steam session bridge and corrected access classification, 22 October 2026

Steam matchmaking RTTI slot 8 at `0x24B920` calls base method `0x22BF00`
from chained range `0x24B941–0x24BD8B`. That method passes the same manager
object to dispatcher `0x22B6C0`, which iterates manager session entries at
`+0x1A0 + index*8`. This adds a static Steam-slot-to-session-dispatch link;
runtime timing and `+0x418/+0x41C` semantics remain open.

The prior RTTI-scoped `--access write` result of zero for `Session+0x41C`
was false. Capstone 5.0.7 labelled the exact store
`movups [rcx+0x41c], xmm0` as READ, so the write filter skipped it. Both
`native_vtable_member_xrefs.py` and `native_data_offset_xrefs.py` now correct
explicit MOV/VMOV-family memory destinations at operand 0. The corrected
Session scan finds one base-class slot-11 store at `0xACA3A5`; its first byte
is zero at this call. It does not prove the target load-path object uses this
base method, because `PlayfabSession` overrides slot 11. Corrected scans still
find no writes to the checked fields in the PlayfabSession `.pdata` method
groups and none to manager `+0x1A0/+0x1A8/+0x1B0` in the Steam-manager
`.pdata` groups. See the exact-build report for full counts, commands, helper
hashes and the distinction between incomplete global scans and the completed
207-candidate fast shortlist.

Reusable rule: a zero write-filter result is not reliable until its access
classifier has been checked against a known store in the same instruction
family and Capstone version. For MOV-family x86 instructions, an explicit
memory operand at position 0 is the destination even when Capstone reports
READ. Keep the instruction text, classifier version, helper hash and exact
RTTI method scope together; rerun prior write negatives after correcting the
classifier. Do not generalize a vtable method's field write to another dynamic
class or manager instance.

The official release log still lists Cosmos 7.06 as newest on 22 October;
Nexus still lists `0.10.2-native-test` last updated 3 October. No native
source/profile mapping changed. `NOT CHECKED`: the exact PlayfabSession
population path at manager `+0x1A8`, a positive `+0x41C` producer, dynamic
invocation timing, remaining source dependencies and live 7.06 behavior.
Next bounded action: trace the positive producer through the exact
PlayfabSession owner path or a caller of Session slot 11, then resume the
unresolved MenuSelect/resource/source gates. Keep 7.06 fail-closed.


### 7.06 PlayfabSession slot-11 clear path, 22 October 2026

PlayfabSession vtable slot 11 (`+0x58`, target `0x237820`) directly calls
base Session method `0xACA370`, which writes a 16-byte value at `+0x41C` with
its first byte set to zero. The vtable-member scan found no direct `+0x41C`
write in the derived method body because it does not follow callees; its
transitive base call is now confirmed.

A full slot-`0x58` scan filtered by `+0x1A0` found a manager-layout candidate
at `0x2357C0`. It calls the slot on entries `+0x1A0`, `+0x1A8` and `+0x1B0`.
The root also clears fields and releases handles, so cleanup is a plausible
interpretation. Exact RTTI and direct-E8 caller scans returned zero for this
root, leaving its manager type, dynamic caller and identity with the
application load-path manager unverified. Treat it as a candidate path that
can zero the byte, not a confirmed runtime path or a positive producer.

Reusable rule: class-scoped vtable scans report explicit accesses in the
listed method bodies; they do not include effects in callees. Follow exact
direct calls from a candidate virtual method before interpreting a zero
member-write count. A caller that loads `+0x1A8` and dispatches a vtable slot
is still only a structural link until the manager type, slot-object type and
runtime invocation path are anchored.

Next bounded action: identify the caller/type of `0x2357C0` or trace another
positive `+0x41C` producer through an RTTI-anchored PlayfabSession path, then
continue the unresolved MenuSelect/resource/source gates. Keep 7.06
fail-closed.



### 7.06 corrected vtable bound and application-owner handoff, 22 October 2026

Correction to earlier entries: the zero RTTI result for `0x2357C0` and the
64-slot Steam-vtable description came from a `--max-slots 64` query. With a
96-slot bound, both exact Playfab and PlayfabSteam RTTI tables have 87
executable slots and place `0x2357C0` at slot 80 (`+0x280`). The prior
absence claim is superseded. The full 87-slot Steam scan still finds no
direct manager-field writes in 42 `.pdata` roots; 44 slots lack `.pdata`
and are outside that scan.

The application-owner link is now statically joined:
`0xAE8D30` callers pass `global+0x937130`; the manager constructor stores
its object at parent `+0xAB40`; and `0x937130 + 0xAB40 = 0x941C70`, matching
the load predicate. Its Steam slot-8 route reaches dispatcher
`0x22B6C0`, which calls manager slot 80; `0x2357C0` calls session slot
`+0x58` on entries `+0x1A0/+0x1A8/+0x1B0`. A PlayfabSession slot-11
override calls the base helper that clears the first byte at `+0x41C`.

This is a static clear path, not proof of the `+0x1A8` entry's dynamic
type, runtime timing, byte meaning, or positive producer. The
`0xAD5A90` population route remains unconnected. Keep Cosmos 7.06
fail-closed; these results do not support a source/profile change.

`NOT CHECKED`: exact entry type/producer, positive `+0x41C` setter,
remaining MenuSelect/resource and source-dependency gates, and live 7.06
behavior. Next bounded action: connect the exact `+0x1A8` entry to a
dynamic type or positive setter; otherwise resume the remaining independent
gates. Full evidence, commands and hashes are in
`NATIVE-25732212-COMPATIBILITY.md`.



### Source data-dependency handoff, 22 October 2026

The source inventory is broader than the function-entry table. A read-only
scan of the four game-facing integration files identified fixed application,
player, companion-roster, owner-state, planet, save/notice, QAM, resource
manager and texture-resource fields, plus strides and five service function
entries. The exact values and source locations are recorded in
`NATIVE-25732212-COMPATIBILITY.md` under Source-dependency inventory beyond
function RVAs. That section is an inventory of the 7.05 source constants,
not proof of 7.06 mappings.

Carry forward status separately per dependency. Partial evidence for a QAM callback, resource initializer or function entry does not close neighboring field and layout dependencies. Leave unresolved globals, nested fields, vector layouts, strides and resource records `NOT CHECKED` until tied to an exact-hash 7.06 owner and consumer.
Next bounded action: build the per-dependency evidence ledger from those
source rows, then close the remaining QAM caller, load semantics and runtime
gates. No source/profile mapping changed; 7.06 remains fail-closed.

The official [Hello Games release log](https://www.nomanssky.com/release-log/) was checked on 22 October and still lists Cosmos 7.06 first, with no 7.07 entry. The [Nexus files page](https://www.nexusmods.com/nomanssky/mods/4579?tab=files) still lists `0.10.2-native-test`, last updated 3 October; game build and package version remain separate.


### Version identity and bounded caller rerun, 22 October 2026

The current Steam executable still matches Cosmos 7.06 / build `25732212` /
SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
The official release log lists no 7.07. Nexus still lists
`0.10.2-native-test` (last updated 3 October), and GitHub `main` remains at
`f7d97b61fcf152677d0d30de34f6c1b48675c436`, the same as this worktree's
baseline. The game build, public package number and source commit are separate
version identities.

The native target profile `native_compatibility.json` remains 7.05/build
`25624745`; root `compatibility.json` is a separate legacy Python profile for
7.04/build `25442159`. Do not change the legacy profile while preparing a
native update. Neither profile is updated to 7.06.

`native_call_xrefs.py --context 16` was rejected before decoding because the
tool's maximum context is 12; it is an invocation error, not a zero-result
scan. The corrected context-12 scan found one direct caller of `0xACA370` at
`0x237848` in the PlayfabSession slot-11 root. Its base helper sets the first
source byte for the `+0x41C` vector store to zero; the remaining 15 bytes are
unproven. This is a static partial-clear route, not a positive setter or a
runtime mapping. Full executable identity and disassembly are in
`NATIVE-25732212-COMPATIBILITY.md`. Keep 7.06 fail-closed.

### Save identity and QAM caller search, 22 October 2026

The official release log was rechecked on 22 October: Cosmos 7.06 remains
latest and no 7.07 entry is listed. The exact Steam build 25732212 and its
executable hash are unchanged.

Initial save-identity evidence moved the row from `NOT CHECKED` to `PARTIAL`;
the later two-way copy trace below supersedes this interim status. Source
`afterLoad` reads a `uint64_t` from `common+0x8980` after a successful local
load. Exact 7.06 candidate `0x573500` retains `RDX` as `R15` and reads an
8-byte value at `R15+0x8980` (`0x5736D4`). This confirms the candidate's
second-argument offset and width, not that its type is the source's common
save object. Next, resolve the four callers and identify that argument's
owner before mapping or porting the load hook.

The interaction-range candidate `0x527EB74` has zero literal preferred-base
pointer references across seven non-executable sections (88,155,208 bytes).
This closes only that pointer-search avenue; keep the interaction-range row
`PARTIAL` and do not repeat the unchanged absolute-pointer scan.

For QAM label search, the new `native_vcall_abi_candidates.py` found 789
slot-`0x48` calls in 523 `.pdata` ranges and reduced them to 55 candidates
with `RDX`/`R8` pointer setup after the last call. RTTI rejected wrapper
targets `0x2E51800` and `0x2E51880` as Havok serialization pointer
implementations. Candidate call `0x347F58` is in a range chained to root
`0x346B30`, an RTTI-confirmed `cGcAtlasBrokerAzure` slot-10 method; its
nested `[this+8]` object remains unknown. These are shortlist results, not
QAM caller evidence. Do not rerun the full slot scan or map from argument
shape alone. Continue from the confirmed QAM constructor/owner chain or an
independent UI-renderer type anchor. Exact commands and script hashes are in
`NATIVE-25732212-COMPATIBILITY.md`; the new helper is discovery-only and does
not replace receiver/RTTI/constructor proof.

No native runtime source or compatibility profile changed. No tests, build,
package or live game operation was run. Keep Cosmos 7.06 fail-closed.

The QAM receiver search added two further false-lead rules. A slot-offset
call plus a `--require-field` displacement only means both occur in the same
function range; it does not prove that the displacement supplies `RCX` or the
vtable. The `0x116B10` query returned two virtual slot-9 calls in a cleanup-like
routine, but their receivers were separate members at `+0x110998/+0x1109A0`;
the QAM child itself was passed only to a distinct direct cleanup call. The
`0xDC0` query returned seven ranges/eight calls and still did not tie a
receiver to the QAM child. Preserve these as bounded false leads and skip
these exact filters unless new receiver evidence changes the question.

Next bounded action: resume from the exact 7.06 quick-menu builder at
`0x152A1C0`, resolve its unwind and caller path, and trace whether its concrete
QAM receiver reaches slot 9 with the required output argument. Require
register-level receiver and output-buffer ownership evidence before changing
the source ABI. Keep Cosmos 7.06 fail-closed.

That builder path is now bounded: `0x152A1C0` has six direct callers and one
chained range, but neither builder range contains a virtual slot-9 call. The
slot-9 target `0x153C0C0` is a three-argument QAM method with `R8` as a
one-byte writable location and a 256-byte string-output path. Its source
wrapper still has a two-pointer ABI and 128-byte buffer assumption. Caller
and output ownership remain open. Same-range slot-9 filters on target members
`+0xA050`, `+0xA060` and `+0xA088` each returned zero, as did the earlier
combined `+0xA050/+0xA088` filter. A same-range displacement is not receiver
proof; do not rerun these filters without new receiver evidence.

Next bounded action: leave the QAM caller unresolved and map the next
independent source dependency: owner emote byte `owner+0x1B937D`. Establish
its owner and exact read/write/consumer chain. Keep the profile fail-closed
until every required source dependency and runtime gate is evidenced.

The 7.06 `owner+0x1B937D` pass found one exact byte read and zero stores in
decoded `.pdata`. Its address is inside chained range `0x508DE0`, whose root
`0x508DC0` copies the incoming owner from `RCX` to `RSI`; the same owner base
feeds the known companion slot, preview slot and placement subobject. The
consumer compares the byte with zero at `0x5090D9`. This confirms width,
owner and branch role, but the game-side producer and exact meaning are still
unknown; keep it `PARTIAL` rather than calling it a confirmed emote state.

Next bounded action: map the source's local-player physics pointer at
`player+0x2A8` from its app/local-player chain and owner placement consumer.
Keep the unsupported-build guard enabled.

The exact `+0x2A8` displacement scan returned 947 matches across `.pdata`,
many unrelated to the player. Do not promote offset-only candidates. The
placement candidate `0x14426A0` resolves the real chain: it derives
`player = app+0x72C6F0` from app global `0x6E8D708` and reads the 64-bit
`player+0x2A8` pointer before passing it to helper `0x142CE6FD0`. This is
enough to map the static field/consumer; local-player lifetime and live
transition behavior remain runtime gates.

Next bounded action: map source interaction-range `image_base+0x527AB34`
through its exact 7.06 placement consumer and verify the data width before
changing the profile.

The old 7.05 interaction-range RVA `0x527AB34` has no direct RIP-relative
reference or exact non-executable 32-bit RVA-constant reference in Cosmos
7.06. One owner-update caller loads a scalar from `0x527EB74` and passes it
twice to the placement helper with the expected register shape. That is a
candidate, not an equivalence: the data bytes and units remain unexplained.
Keep the source dependency `PARTIAL`; do not port by the apparent role alone.

Next bounded action: inspect one independent data initialization/type anchor
for `0x527EB74`; if its role remains unknown, stop that branch and continue
with another source dependency. Preserve the fail-closed build guard.

The exact QAM slot-9 body at `0x153C0C0` writes zero through its incoming
`R8` pointer, preserves `RDX` as the destination for localized string
assignment, and uses `RCX` as its receiver. Treat this as a three-part caller
ABI shape, not a semantic name for the `R8` byte. Full ranges and disassembly
are recorded in `NATIVE-25732212-COMPATIBILITY.md`.

Next bounded action: narrow QAM slot-9 candidates by this receiver/string/
writable-byte shape and verify register liveness across intervening calls;
then continue the source-dependency gates. Do not repeat the invalid context
request or the global `+0x41C` displacement scan.

### QAM slot-9 owner-offset filter and fresh-version check, 22 October 2026

Using the proven owner chain `+0x115D50 + 0xDC0 = +0x116B10` produced one
same-function shortlist range and two slot-`0x48` calls. Root-aligned
inspection rejected both: the calls use separate fields at
`+0x110998` and `+0x1109A0`; the QAM child at `+0x116B10` is cleaned up
later through `0x1527BD0`. This confirms why a same-function offset filter
is candidate triage only. Preserve the exact scope and corrected commands in
the build-specific report; do not repeat the `+0xDC0` or `+0x116B10` filter
without a new receiver/dataflow anchor.

The attempted `py -3.11` command failed before reading the executable
because the launcher could not find an installed Python; direct `python -B`
resolved CPython 3.11.9 and completed the scan. An initial disassembly window
crossed the `.pdata` boundary; the corrected `0x16F` window is the evidence
to reuse. The local Git worktree status and a fresh GitHub `main` readback
remain `NOT CHECKED` because Git status reported that the operation must run
in a work tree and the GitHub connector failed authentication. Keep this
separate from the read-only binary result.

Fresh public version evidence on 22 October still shows Cosmos 7.06 as the
latest official game patch and Nexus `0.10.2-native-test` as the latest
public mod package. The executable remains Steam build `25732212` with
SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
The 7.05 native profile remains unchanged. Next bounded action: establish
actual QAM receiver flow to a slot-`0x48` caller with live `RDX` and `R8`
arguments, then finish the exact-source dependency ledger and runtime gates.
Do not declare support or package 7.06 while those gates remain open.


### 7.06 release-readiness check, 22 October 2026

The official release log still lists Cosmos 7.06 as the latest patch; no 7.07
entry is present. The installed executable remains Steam build 25732212,
file/product version 180836, size 88,560,712, SHA-256
13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
The public Nexus package remains 0.10.2-native-test from 3 October and is
for Steam build 25624745 / Cosmos 7.05. Do not describe it as a 7.06 build.

Planning estimate for readiness to release a 7.06 update: about 10%. This is
separate from the volume of static research and does not claim compatibility.
The 7.06 identity is confirmed and partial mappings are documented, but the
source dependency ledger, several native/data mappings, source/profile port,
offline validation, archive, exact-build live checks and release readbacks
are still outstanding. Verified 7.06 release compatibility remains 0%;
keep the runtime disabled for this executable.

The worktree is branch compat/cosmos-706-25732212 at
f7d97b61fcf152677d0d30de34f6c1b48675c436. Existing modifications and
untracked research files were preserved; this handoff changed documentation
only. No tests or game operations were run. git ls-remote failed before
reading GitHub main (getaddrinfo() thread failed to start), so the remote
tip remains NOT CHECKED.

Next: finish the exact-hash dependency ledger, then close the startup,
summon and safe menu/resource gates in dependency order. Do not change source
or compatibility profiles until each required mapping is evidenced. Package
only after offline validation and exact-build runtime checks, then read back
the GitHub and Nexus release identities.


### Gate-first update rule and exact-source ledger, 22 October 2026

The repository guidance and native-pattern playbook now require a compact
gate table with one stable role per source dependency, its exact-build
evidence state, the feature/release gate it blocks, and one bounded next
action. Prioritize the shortest path to a complete requested behavior. After
a bounded search yields no evidence, record its exact scope and change the
anchor or work an independent gate; do not repeat it unchanged. Do not end a
work period after documentation alone while authorized, actionable analysis
remains. Avoid readiness percentages unless a denominator and weights were
defined; report mapping, implementation, validation, runtime and release
gates separately.

The 22 October exact-build report now has a per-dependency ledger derived
from the four game-facing native source files. It separates source function
entries, runtime/companion fields, QAM row layout, resource-manager layout
and internal callbacks. `MAPPED` in that table means static role/contract
evidence only; the 7.06 source port, profile, offline/live validation and
release remain incomplete. Keep Cosmos 7.06 fail-closed. Reuse the ledger to
select work rather than restarting from symbol discovery.

The QAM slot-9 constructor pass confirms a useful reusable chain:
`0x153C0C0` is slot 9 of vtable `0x4A504E0`; constructor `0x2CA6D0` stores
that vtable at `[this]`; parent constructor `0x2CA290` calls it with
`parent+0xDC0`; and its caller passes `outer+0x115D50`. This confirms the
QAM child owner arithmetic, not a slot-9 callsite or the meaning of `R8`.
A vcall scan requiring slot offset `0x48` and same-function displacements
`0xA050` plus `0xA088` returned zero ranges/calls. That is only a bounded
negative for this conjunction. Do not repeat it or the earlier
`+0xDC0`/`+0x116B10` filter without a new receiver/dataflow anchor.

The exact 7.06 `CanSummon` body at `0x1474F10` loads the application pointer
from global RVA `0x6E8D708`, then uses `app+0xE10D0` as the companion table.
This is independently corroborated by the session path at `0x4955AD` and
supersedes source global `0x6E89688` for this executable. Carry the exact
global identity forward, but do not infer that other app-relative 7.05
offsets survived.

Next bounded action: map the remaining application-relative summon fields
from `0x6E8D708`, prioritizing location, roster members and local-player
checks used by the requested behavior. If a field cannot be tied to an exact
owner and consumer in one bounded pass, record it and advance to an
independent gate. Preserve the slot-9 caller/`R8` blocker without repeating
the rejected same-function filters. Detailed commands, tool versions and
the dependency ledger are in `NATIVE-25732212-COMPATIBILITY.md`.

### Menu-label hook port gate, 22 October 2026

The source wrapper confirms that the outstanding QAM label work gates a real
native hook port. Current source types the saved label original as a
two-pointer function and post-writes a 128-byte caption. The 7.06 slot-9
label-output candidate at 0x153C0C0 takes a third R8 argument and writes a
256-byte output. Caller identity, R8 meaning/lifetime and output ownership
remain NOT CHECKED. Do not substitute the label candidate by name alone.
Record this argument-count and buffer-capacity mismatch in the source ledger;
resolve the real caller and output object before changing the hook.

### Active 0.10.2 source and corrected exact-build field evidence, 22 October 2026

Trace the release package to its active implementation before making a source
dependency inventory. The current player package is native C++ under
`native/src/` and targets 7.05 through `native_compatibility.json`;
`src/runtime.py` is a preserved Python/pyMHF 7.04 runtime and is not part of
the native 0.10.2 package. GitHub `main` and the local starting commit both
read back as `f7d97b61fcf152677d0d30de34f6c1b48675c436`; Nexus currently lists
0.10.2-native-test, file 49469, for Steam build 25624745 / Cosmos 7.05. The
official release log still lists Cosmos 7.06 as newest on this date. Preserve
these identities separately from the exact 7.06 executable hash and the
source branch under review.

The direct call from `0xF41680` to `0x50E1A0` does not prove that 7.06 reads
`entry+0x2330`. It passes a 16-byte key from
`base+index*0x24A0+0x46DD0` to manager resolver `0x213290`; that resolver
returns a manager-entry pointer, and only then `0x50E1A0` reads 16 bytes at
`resolver_result+0x2330`. The source identity at roster `+0x2330`/`+0x23C0`
remains `PARTIAL` until the key owner and returned object's relationship to
the owned roster are established. This correction supersedes the earlier
same-displacement inference in the exact-build report.

The source habitat dependencies now have direct exact-build static evidence.
`0x2B3A10` resolves application global `0x6E8D708`, loads solar pointer
`app+0x72AFB0`, reads 32-bit count `solar+0x2544` and index
`solar+0x5196D0`, clamps the index, scales it by `0xD9170`, and reads 32-bit
fields at `solar+index*0xD9170+0x6148/+0x614C`. `0x2C4710` independently
corroborates the count and stride, but returns a different subobject base
`solar+0x2E30+index*0xD9170`; do not conflate its returned pointer with the
direct biome-field base. Addresses and widths are statically mapped; complete
enum meaning and live transition behavior remain open.

Next bounded action: trace the producer/owner of the 16-byte key at
`base+index*0x24A0+0x46DD0` and prove whether its resolved manager entry is the
companion identity used by the native source. Reuse the exact commands and
tool hashes in `NATIVE-25732212-COMPATIBILITY.md`; do not repeat the broad
offset scan or treat the unresolved identity as mapped. Keep Cosmos 7.06
fail-closed.

### State-field transitions and efficient read/write scans, 22 October 2026

For a state/index field, require the exact-width setter, clearer/transition,
sentinel and one real consumer before marking its static role mapped. Resolve
the base object through an independent pointer chain. One matching offset or
source variable name is not enough. `native_data_offset_xrefs.py` accepts
repeated `--access` filters; request `--access read --access write` together to
avoid decoding the full `.pdata` inventory twice. Resolve chained unwind
ranges before caller scans: a zero direct-call result for a chained fragment
does not mean its parent has no callers.

The exact 7.06 report now maps active companion slot `app+0x29A1C0` as a
32-bit value. Its base is global `0x6E8D708`; one setter stores a bounded
0–29 roster slot, one clearer stores `-1`, and a consumer passes the index
with `app+0xE10D0` to helper `0x540D00`, which applies the same 30-slot limit
and `0x24A0` record stride. Live transition behavior remains open. The
earlier report's `player+0x29A1C0` label was wrong and is superseded by the
app-relative mapping in the exact-build ledger.

The earlier identity-key lead at `+0x46DD0/+0x46DD8` is still unresolved:
five/four fast candidates included a body comparing those key qwords with
row `+0x2310/+0x2318`, but exact direct-call and RTTI probes found zero. Mark
the owner `NOT CHECKED`; do not repeat those same searches without a new
invocation anchor. The next gate is the QAM slot-9 label output: recover a
real caller and the `RCX`/`RDX`/`R8` buffer contract from a new receiver or
callsite anchor, not the already negative `0xA050/0xA088` same-function filter.
Detailed evidence and reproduction commands are in
`NATIVE-25732212-COMPATIBILITY.md`. Keep 7.06 fail-closed.

### Save identity two-way mapping and load-call semantics, 22 October 2026

The save identity field is now `MAPPED` statically. A single batched read/write
`.pdata` scan for displacement `0x8980` found the exact save-side copy in
`0x57AE60`: it uses incoming `RCX` as player state and incoming `RDX` as the
common object, copies 8 bytes from `playerState+0x187E8` into
`common+0x8980`, and copies the paired field at `+0x8988`. The exact load
candidate `0x573500` retains `RCX` as `R13` and `RDX` as `R15`, then copies
8 bytes from `common+0x8980` back to `playerState+0x187E8`. Common-object
initializer `0x2A0CB70` explicitly sets `common+0x8980` to zero.

Caller `0x2E088F` proves that the same stack object at `rbp+0x2240` is
initialized at `0x2E04AF`, passed as common state to save helper `0x57AE60`
at `0x2E04CE`, and later passed to load candidate `0x573500`. RTTI identifies
the containing root `0x2DBBB0` as `cGcApplicationDeathState`, so this is a
death-state path; do not silently generalize it as an ordinary local save
load. The other two caller roots that call `0x573500`,
`0x48E400` and `0x48FA60`, have no validated RTTI vtable hits. One dynamic
fourth-argument caller still loads its byte from `[rdi+0x4BE6A0]`; that
field's meaning is not established.

The field's offset, width, owner and save/load def-use path are mapped. Live
values still need to prove that this is the stable per-save identity used by
the mod's favorite key. The load hook remains `PARTIAL`: source `Load` declares
the fourth argument as `network`, fifth as `resetting`, and sixth as a
32-bit `extra`; some exact callers pass the fourth or sixth value in byte
register/stack forms, while the candidate's fifth-argument branch is known
but its meaning is not. Do not port the hook until register/stack meanings and
local/network/death-state timing are reconciled.

Reproduction commands against the exact executable:

```text
python -B tools/native_data_offset_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --offset 0x8980 --access read --access write --limit-per-offset 100
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2A0CB70 --size 0xD0
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x57AE60 --size 0x120
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x57B140 --size 0xB0
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x573500 --size 0xA8
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x5736B0 --size 0x80
python -B tools/native_function_disasm.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x578AE0 --size 0xA0
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x57AE60 --context 12 --limit-per-target 20
python -B tools/native_pdata_function_group.py --exe "<verified Cosmos 7.06 NMS.exe>" --rva 0x2E088F
python -B tools/native_rtti_vtable_probe.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x2DBBB0 --max-slots 64
python -B tools/native_call_xrefs.py --exe "<verified Cosmos 7.06 NMS.exe>" --target-rva 0x48E400 --target-rva 0x48FA60 --context 10 --limit-per-target 40
```

The read/write scanner SHA-256 is
`5d3f80c87679dcf6dd41bde71f027628eb6af24fc6ee06ecf32924e63fac34b8`;
other helper hashes are recorded in the exact-build report. The official
release log was rechecked on 22 October: 7.06 remains latest, with no 7.07
entry. No native source/profile change, tests, build, package or live game
operation occurred. Keep 7.06 fail-closed.

Next bounded action: resolve the fourth-argument byte and sixth stack argument
through the remaining three callers, including the producer of
`[rdi+0x4BE6A0]`; then compare each call path to `Runtime::beforeLoad` and
`afterLoad`. Preserve the death-state path as a separate trigger gate.


### Load-candidate callee-first-use audit, 22 October 2026

The exact Cosmos 7.06 executable remains Steam build `25732212`, SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`. A
detailed read/write pass for `+0x4BE6A0` decoded `52,110,272` `.pdata` bytes,
skipped zero ranges and confirmed seven operands (two writes, five reads) with
exact Capstone access direction. It reproduced the heuristic inventory; no
new field owner or semantic meaning was established.

The complete unwind group for load-role candidate `0x573500` is eight adjacent
ranges through `0x579B50`. Mapping the actual prologue gives fourth-argument
home slot `[RBP+0xCC8]`, fifth stack argument `[RBP+0xCD0]`, and sixth stack
argument `[RBP+0xCD8]`. The candidate stores `R9B` at entry, then overwrites
its home slot at `0x576407` before a direct input read or address escape. The
sixth slot is first written at `0x573653`; its later byte/word/dword uses are
local scratch. The fifth input is directly read as one byte at `0x578B2F` and
gates a call to helper `0x6019F0`.

A full direct-call scan found exactly one E8-style call to helper `0x6019F0`,
at `0x578B52` in candidate `0x573500`; it decoded `52,110,272` `.pdata` bytes
and skipped no ranges. This does not rule out indirect calls. The helper
clears several state fields and takes a state-derived Boolean for its longer
continuation. This narrows the next semantic question to the fifth input and
its four callers. Do not infer that the caller's session-derived fourth byte
means `network`, or that the sixth slot means a 32-bit `extra`. The 7.05
source typedef names still do not map to this 7.06 body. Keep the hook
`PARTIAL` and the 7.06 profile disabled.

Reusable rule: trace the callee's first read/write/address escape across its
full unwind group before naming an argument. Derive home and stack offsets
from the prologue. A saved register that is overwritten before use is not
semantic evidence; an incoming stack slot reused after a write is a local,
not proof of the parameter's type. Exact commands and hashes are in the
[7.06 report](NATIVE-25732212-COMPATIBILITY.md).

Next bounded action: trace the fifth-byte branch at `0x578B2F` and helper
`0x6019F0` back to caller state, then decide whether it matches the old
`resetting` input. Keep local/network and death-state caller classification
separate, and continue the independent QAM label-output gate in parallel.


### QAM builder callers are an update chain, 22 October 2026

The direct-call scan for builder `0x152A1C0` found six calls across three
`.pdata` roots: one in QAM update root `0x15286C0`, four in `0x153B5B0`, and
one in `0x153BE80`. Complete root-aligned scans of all three groups found no
virtual call through slot offset `0x48`. This confirms that the builder and
its direct update chain do not invoke QAM label method `0x153C0C0`; it does not
exclude a separate UI-rendering path or copied function pointers.

Reusable lesson: a QAM owner and matching builder ABI do not establish who
requests the label. Follow the object into the UI/render path and prove the
receiver at the actual slot dispatch; do not repeat same-range displacement
filters or scan the builder/update roots again. The six caller RVAs, exact
commands and helper hashes are in the [7.06 report](NATIVE-25732212-COMPATIBILITY.md).

Next bounded action: trace the QAM object from the confirmed owner chain into
its higher-level UI/render consumer, then establish the `RCX` receiver and
`RDX`/`R8` outputs at slot 9. Keep the label hook `PARTIAL` and 7.06 disabled.

### Load-candidate fifth-argument trace and stale RVA, 22 October 2026

Old profile load RVA `0x572C40` lies inside the exact 7.06 `.pdata` range
`0x572410-0x573137`, rooted at `0x572410`; it is not a 7.06 function
entry. Do not carry it forward as an entry hook. Candidate `0x573500` is
still `PARTIAL`.

Caller fifth-argument values now form a useful, bounded comparison:
`0x48EECC`, `0x48F983` and `0x4906BD` pass zero; the RTTI-confirmed
`cGcApplicationDeathState` caller `0x2E088F` passes one. In `0x48E400`,
`DIL` is zero on the path to `0x48EECC`; the `DIL` write at `0x48E58C`
and the later tail write are on other paths. `R13B` stays zero from
`0x48E42D` through `0x48F983`. The candidate's zero branch calls
`0x6019F0`; one skips it. This supports mode discrimination but does not
prove the old source name `resetting`.

A `py -3.11` invocation failed before decode with `No installed Python
found!`; it is a `TOOL ERROR`, not a negative scan. The direct Python
3.11.9 interpreter, its SHA-256 and package versions are recorded in the
exact-build report. Reuse the explicit interpreter path when the launcher
cannot locate the registered runtime.

Next bounded action: establish the semantics of the session-derived
`+0x4BE6A0` byte and the source `network` gate; keep the QAM output-label
consumer as an independent blocker. Preserve the fail-closed 7.06 profile.

### Cosmos 7.06 item-field ownership and placement-range correction, 22 October 2026

The exact-build report now maps the interaction-range source role statically
from the 7.06 owner-update load at `0x509190` to placement helper `0x14426A0`
at `0x5091A5`. This parallels the 7.05 placement call using source RVA
`0x527AB34`; the 7.06 candidate is `0x527EB74`. Both are virtual-only BSS
addresses, so absent raw bytes are not a zero value. An earlier extraction
used a raw-section offset outside `SizeOfRawData` and read unrelated bytes;
that interpretation is withdrawn. Static role is mapped; live value, units
and placement behavior remain open.

The exact 7.06 item constructor initializes `item+0x84` to `-1`, zeros
`item+0x88..0x97`, copies a 64-byte-bounded string into `item+0x98..0xD7`,
and initializes `item+0xD8` to `-1`. QAM update reconciliation reads
`+0x84`, `+0x88` and `+0x90` as row comparison data and writes a row match
index into `+0xD8`. QAM trigger reads `+0x84` as the companion slot supplied to
eligibility and queue helpers. This maps the slot payload, but the current
source's marker and cleared-string spans are not free storage. Do not port
those writes until their effect is removed or proven safe. An out-of-band
item-index tracker is a candidate design only; rebuild/reallocation semantics
remain NOT CHECKED.

The whole-image offset scan for `+0x84`/`+0x88` decoded 52,110,272 `.pdata`
bytes, zero skipped ranges, and printed only 100 of 3,261 / 11,913 operands.
Those counts are not QAM ownership evidence; the constructor, QAM update and
trigger bodies are the useful anchors. Do not rerun this offset scan unchanged.

A full virtual-call ABI shortlist was accidentally repeated although the
identical command/result was already documented. The repeated result still
had 789 calls, 523 ranges and 55 argument-shape candidates, so it adds no
coverage. RTTI on shortlist method `0x33E6160` identifies Havok
`ChildArrayImpl` slot 10, a false lead for the QAM label caller. Check prior
documentation by helper name before running a broad command; use new receiver
or owner evidence to move the search.

The QAM owner-path attempt is now a bounded negative: root `0x144CB24` has no
direct callers, RTTI slots, branch targets, absolute-pointer references or
RIP-relative references in the exact image. Do not repeat it or the QAM
builder/update scans. The label consumer and `R8` meaning remain unresolved.
The virtual-call ABI shortlist repeat used `--limit 250`, versus `--limit 100`
on its first pass; it added no receiver candidate. Keep the load/network and
live-runtime gates independent.

### Resource-handle retain and release mapping, 22 October 2026

For exact Cosmos 7.06 build `25732212` and SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`, the
current source's one-pointer retain call maps to `0x2D69720`; the matching
release path is rooted at `0x2D65A80`. Both resolve the 32-bit handle through
the same manager global `0x59141E0`, count at `+0x5C`, table at `+0x60`, and
resource refcount at `+0x134`. Constructor `0x2D62D60` sets that global and
destructor group `0x2D634C0` clears it. The old `0x2D65980` address lies inside
an unrelated vector-growth method and must not be reused.

The exact evidence, reproduction commands, helper hashes, false leads and
limits are in the dated resource section of
`NATIVE-25732212-COMPATIBILITY.md`. The source has no matching icon-release
path, so resource lifetime and live rendering remain open. No source/profile,
build, test, package or live-game change occurred; keep Cosmos 7.06 fail-closed.

Next bounded action: continue the source local/network gate from the already
identified session-derived byte producer and trace its owner/callers, without
repeating the closed QAM caller chain or broad `+0x134` scans. Keep icon
rendering, release/lifetime and all live behavior gates explicit.

### Resource-manager global aliases and owner lifecycle, 22 October 2026

The QAM resource initializer reads manager global `0x6E1FC90`. Exact
write-filter scans show its startup root allocates a `0x210`-byte object,
calls constructor `0x2D62D60`, then stores that returned pointer at
`0x6E1FC90`; the constructor also stores `this` at `0x59141E0`. The teardown
root clears `0x6E1FC90`, then the resource-manager destructor clears
`0x59141E0`. This maps the 7.05 source globals `0x6E1BC10` and `0x5910190`
to the two 7.06 aliases of the same manager. The manager's `+0x5C` count and
`+0x60` table are used by QAM initialization and the mapped handle retain/
release pair.

The first full-detail access pass was interrupted after `0x1403715` decoded
bytes with no final result. A corrected reusable `native_rip_xrefs.py`
`--access write` filter uses fast whole-image decode and detailed decode only
for matching RIP targets; it completed both exact-hash write inventories with
two writes per global and zero skipped ranges. The global's 807 general RIP
references were only a shortlist; the two writes and constructor/destructor
dataflow are the useful evidence. Full reproduction commands and hashes are
in the exact-build report. No source/profile, build, test, package or live-game
change was made; keep runtime and rendering checks open.

Next bounded action: resolve whether the 7.06 load path exposes a verified
local/network predicate, or identify the QAM item-icon renderer from a new
owner/call path. Do not repeat the high-fanout global scan or closed QAM
label-owner path.

### Resource fallback selector, 22 October 2026

The native resource loader group `0x2D63EA0` checks resource byte `+0x13B`.
If nonzero, it resolves a fallback resource using the resource's `+0x110`
field and type `+0x8`; otherwise it uses the original resource. It increments
the selected resource's `+0x134` reference count only when `+0x13D` is zero.
This maps `+0x13B` to fallback selection and supports the source's decision to
avoid a substituted icon, subject to live verification. It does not map
neighboring `+0x13A`, which remains `PARTIAL`.

Exact command, scope and helper hash are recorded in the Cosmos 7.06 report.
No source/profile, build, test, package or live-game change occurred. Next
bounded action: continue with the local/network load contract or a fresh QAM
icon-render owner path; keep `+0x13A` and runtime readiness open.

### Ship-eject and cockpit hook call-shape mapping, 22 October 2026

The exact 7.06 `cGcSpaceshipComponent::Eject` candidate is `0x1754180`.
Its chained body uses `RCX` plus Boolean inputs in `R8B` and `R9B`; the source
detour matches those positions. Sixteen direct callers were found. Ordinary
local-player exit callers pass the exact application player pointer in `RDX`;
the native method does not consume that argument, so the source callback's
strict `app+0x72C6F0` equality check must remain. This prevents unrelated
callsites from arming the mod. The `cGcPlayer::OnEnteredCockpit` candidate
`0x1483E20` uses one `this` pointer in `RCX`; all three direct callers pass
`app+0x72C6F0`. Both source contracts are statically mapped; hook lifetime,
thread and live behavior remain to be checked. Neither candidate appeared in
a validated RTTI vtable slot, but both have direct-call evidence.

Exact commands, hashes and the bounded callsite-output truncation are recorded
in the dated section of `NATIVE-25732212-COMPATIBILITY.md`. No source/profile,
build, test, package or live-game change occurred.

Next bounded action: return to the local/network load contract and unresolved
QAM item identity/rendering gates. Do not treat these two static hook mappings
as runtime verification.

### Direct QAM label call and three-argument ABI, 22 October 2026

The RTTI-confirmed `cGcQuickActionMenu` slot 9 target `0x153C0C0` has one
direct decoded call at `0x1529288`, inside update root `0x15286C0`. At that
call the caller passes `RCX=QAM`, `RDX` as the 256-byte label output, and `R8`
as the adjacent byte at output `+0x100`. The callee writes the label through
`RDX` and clears the `R8` byte. The caller's immediate tail does not read that
byte; its semantic role remains unknown. This supersedes the earlier
`NOT CHECKED` caller state, but not the downstream-byte, source-port, thread
or live UI gates.

The active source wrapper currently accepts and forwards only two arguments,
and its menu adapter is sized for a 128-byte output. Any 7.06 port must retain
the opaque third pointer and the native 256-byte capacity. The exact call
chain, commands and helper hashes are in the dated QAM section of
`NATIVE-25732212-COMPATIBILITY.md`. The slot-9 direct-call scan covers E8
references in `.pdata` ranges only; it does not exclude function-pointer or
other indirect dispatches.

Reusable search lesson: once RTTI establishes a virtual method target, also
scan exact direct E8 references to that target. A function may call the slot
implementation directly from an update path, so same-slot virtual-call scans
can miss the real caller. Conversely, zero direct E8 callers is not proof of
no virtual use. No source/profile, build, test, package or live-game change
occurred. Next bounded action: establish whether QAM item identity can be
tracked safely outside the fields used by the native reconciliation pass;
then continue the remaining exact-source and runtime gates.

### QAM row flags and callback ABI checkpoint, 22 October 2026

The exact item constructor stores the fourth argument's `R9B` into one byte
at `item+0x4C` and the fifth stack argument into one byte at `item+0x4D`;
the source currently passes `false,true`. QAM update compares a row dword at
`+0x4C` and writes `0x15` there on a matched-row path, so the source's
constructor-time `+0x4C==0` check is not a durable invariant. Whether the
custom marker keeps an appended row out of that path is `NOT CHECKED`. The
`+0x4D` consumer is also unresolved. A full-image detailed offset scan was
stopped at `0x1403715` decoded `.pdata` bytes, with no final counts; this is
not a negative result. The exact roots and tool hashes are recorded in the
Cosmos 7.06 report.

The source label callback now preserves the statically mapped third pointer
when calling the original QAM slot-9 method. It still installs the 7.05 RVA
and keeps the 7.06 profile disabled. This fixes the known ABI-forwarding
omission without claiming that the target/profile, item reconciliation or
runtime behavior is ready. No build, test, package or live-game operation
occurred.

Reusable lesson: constructor defaults do not prove a field remains unchanged
after the update pass. The first QAM row-update pass compares qwords at row
`+0x84/+0x8C`, uses an 8-byte equality helper at `+0x40`, and compares dwords
at `+0x80/+0x4C`. The source's 16-byte marker at `+0x88` overlaps 12 bytes of
those comparison qwords. On a successful match, native code clears
`+0x84..+0x93` and writes dword `0x15` to `+0x4C`, which would invalidate the
source marker and constructor-time checks. A separate binding pass compares
current rows against QAM descriptors using qwords `+0x88/+0x90` and writes
the matched descriptor index to `+0xD8`; therefore the marker also participates
in source-binding identity.

The current constructor call writes `false,true` into
`+0x4C/+0x4D` after initializing qword `+0x40` to `-1`, yielding dword
`+0x4C=0xFFFF0100`; the update candidate expects `0x15`. This exact matcher
therefore advances without taking its mutation path for a row with the current
constructor state. The earlier gate table compressed these two paths; the
report now records both exact sets of comparison offsets. Candidate descriptor
values and unmatched-row retention remain `NOT CHECKED`.

Next bounded action: resolve the candidate-key producer and unmatched-row
retention path, then close the remaining source data, resource, load and
runtime gates. Do not use constructor state alone as a lasting invariant.


### QAM candidate copies and Session state setter, 22 October 2026

The exact QAM update root copies whole `0xE0` rows into selected descriptor records after their constructor initialization. The binding keys at descriptor `+0x88/+0x90` come from source-row `+0x08/+0x10`, so constructor-zero evidence cannot establish final candidate values or marker safety. The same root also copies an existing QAM item row into the candidate array. Keep the custom-row matching and rebuild-retention gate `PARTIAL` until source values and lifetime are traced.

For the validated base `Session` vtable `0x4AAA640`, slot 11's method `0xACA370` is the only bounded virtual-method write to `+0x41C`; it clears the first byte of that 16-byte region. Helper `0xACA550` sets dword `+0x418` and notifies listeners with old/new values. Nine direct callsites pass states 0, 2, 3, 4 and 5. This maps the field as a numeric state, but does not name state 4 or prove local/network semantics. The exact per-caller evidence and reproduction commands are in the latest dated section of [NATIVE-25732212-COMPATIBILITY.md](NATIVE-25732212-COMPATIBILITY.md).

Reusable method: follow data through later stores after a constructor; an initializer is not a lasting value guarantee. For owner-bounded state fields, locate the setter and enumerate its callers, recording exact values while keeping enum labels separate from observed numbers. Correct failed tool arguments and mangled RTTI selectors before treating output as evidence.

Next bounded actions: trace the state-4 caller roles and an owner-anchored positive `+0x41C` writer; trace actual source-row keys feeding QAM candidates. The 7.06 profile remains disabled. No build or tests were run.


### QAM `+0xD8` owner correction, 22 October 2026

Correction: update root `0x15286C0` has QAM in `RDI` and its third input in `R15=R8`. The mapped `+0xD8` writes target `0xE0` rows reached through that third-argument object's vectors at `+0x618` and `+0x520`, after comparing them with QAM descriptors. The third-argument type and alias to QAM source rows are not established. Withdraw the claim that this proves the source QAM row's `binding` check is an unmatched-descriptor invariant; `-1` is confirmed only at construction until another exact QAM-row writer is mapped.

Reusable method: identify the pointer base for every same-offset access. A row layout match and shared displacement do not prove the same object; trace the receiver register and input argument, then establish aliasing before assigning a source field role.

The targeted QAM slot-0 / `+0xA050` vcall filter returned zero matching ranges across the complete `.pdata` scan. It is not proof that the QAM update has no virtual caller. Next bounded action: trace the `R8` argument's owner and alias path, then inspect exact QAM-row `+0xD8` writers. Keep 7.06 disabled.


### Session state-4 transition path, 22 October 2026

State 4 is set by an exact static path in dispatcher root `0x22B6C0`: it matches an event row's identifier against session `+0x630` in the manager array, whose three-index table contains 0, 1 and 2, then calls state helper `0xACA550` with `EDX=4` when the row status is nonnegative. This includes array index 1, the manager `+0x1A8` session read by the load predicate. It ties state 4 to a real transition path on that slot, but does not name the event/status or explain `+0x41C`; local/network semantics remain unresolved.

Reusable method: for an indexed owner array, decode the exact selector table and the compared identity field. This can prove which slots a path can reach; it does not assign enum semantics without the event producer and lifecycle.

Next bounded action: map a positive `+0x41C` writer and the event kind/status producer. Keep the 7.06 profile disabled.


### QAM slot-0 receiver-filter false lead, 22 October 2026

The slot-0 / `+0x116B10` scan found one apparent call in root `0x924C90`, but the exact call at `0x924DED` receives `RCX=[RDI]`; the same root's proven QAM subobject at `RDI+0x116B10` was used for a separate direct call. RTTI did not validate the root as a vtable method. Reject this call as a QAM update caller. The slot-0 / `+0xA050` filter remains a bounded zero, not a universal no-caller proof.

Reusable lesson: resolve the call's `RCX` expression at the dispatch and compare it to the independently proven QAM subobject. Another operand with the expected offset elsewhere in the function is only a false-positive candidate.

Next bounded action: find a caller/constructor chain that proves the QAM receiver at slot 0, then trace its `R8` input. Do not repeat these same-range filters.

### QAM pending-selection state and +0x480 false leads, 22 October 2026

The exact Cosmos 7.06 global +0xA16C displacement scan found the QAM builder's
read and clear plus TriggerAction's set-to-one path. Receiver provenance is
established: TriggerAction copies entry RCX to R15; the builder saves entry
RCX in its stack frame, and [RBP+0x5680] aliases that saved receiver before it
is loaded into R12. TriggerAction sets the byte after increasing QAM depth and
calling the mapped selected-index setter. The builder consumes and clears it.
This maps a pending-selection byte statically; live timing remains open.

The QAM vtable-only scan missed this field because it covered seven
.pdata-backed vtable methods, while the relevant builder/TriggerAction paths
were reached through separate code paths. A zero from that narrow vtable
scan did not establish that the QAM field was unused. Reusable method:
combine the complete displacement scan with exact chained-range resolution,
then prove the base register from the function's saved incoming argument and
the caller/consumer path. Reject stack-relative same-displacement matches.

Follow-up of the matchmaking manager +0x480 candidate writers found only
zero-initialization in untyped 0x4B0-byte record constructors/reset paths.
Caller scans found three direct callers of 0x2237CE0 and four of its reset
helper 0x2237400; these did not establish an alias to the RTTI-identified
matchmaking manager. The zero result for interior address 0x2237D1A was
superseded by its chained group root 0x2237CE0, whose caller scan found three
calls. Do not infer ownership from a matching displacement or from a
constructor zero; use a manager-anchored write or registration/callback path.

Next bounded action: prove the fifth-argument branch and caller roles for the
7.06 load-hook candidate. Keep local/network semantics, slot-9 output ABI and
live UI/resource behavior open; 7.06 remains fail-closed.

### Application matchmaking pointer and session key follow-up, 22 October 2026

Current official sources still show Cosmos 7.06 as newest and Nexus file 49469 / package 0.10.2-native-test as the latest mod file; the Nexus compatibility text available here is for Cosmos 7.05 only. The 7.06 update is not releasable yet.

New static chain: load predicate reads application+0x941C70 and entry +0x1A8. The session constructor allocates three RTTI-confirmed PlayfabSession objects and stores them at manager +0x1A0/+0x1A8/+0x1B0 for selector bytes 0, 1, 2. Slot 20 reads the 64-byte +0x41C..+0x44C record and uses it as a lookup key. This supports key/empty-state behavior, not a network-Boolean label.

An exact +0x941C70 write scan found one store in cGcApplicationShutdownState slot 3: it calls two manager virtual slots and clears the pointer. The app vtable scan found no reads/writes to that displacement in four .pdata-backed methods. A write-only scan of global RVA 0x6E8D708 reduced 26,301 references to three stores. Retraction: the bounded-false-lead conclusion used an incorrect subtraction and is superseded by the dated correction below. A separate startup path rooted at 0xAE8810 positively writes the manager member. Do not repeat the unfiltered global scan or offset dump.

The positive manager installation and dynamic type were open at this handoff; the dated correction below closes those two static gates. Session-array population, local/network semantics, and all live 7.06 gates remain open. See the latest dated entry in [the exact-build report](NATIVE-25732212-COMPATIBILITY.md).

Reusable step: pair a write-only global reference filter with the exact member-displacement scan, then resolve its unwind root and RTTI owner. For a deep field in a large application object, convert the target to each constructor's proven subobject-relative offset before scanning that constructor. A matching class name, offset or session table is not proof that two manager pointers alias.

Next bounded action: identify the invocation or registration path that populates the confirmed manager session array, then classify the still-untyped load caller rooted at 0x495640. Keep 7.06 disabled.

### Application manager installation correction, 22 October 2026

Correction to the preceding entry: the statement that the positive manager assignment/type at application+0x941C70 remained open was superseded by exact startup-call disassembly. At 0x2C6D31 the application pointer is loaded; 0x2C6D38 adds 0x937130; 0x2C6D3F calls root 0xAE8810. That root preserves the subobject pointer in RDI, allocates and constructs a 0xA60-byte cGcMatchmakingPlayfabSteam at 0xAC7050, then stores it at [RDI+0xAB40]. The correct arithmetic is 0x937130+0xAB40=0x941C70. RTTI validates primary vtable 0x4AAA358 and secondary table 0x4AAA618. This closes the installed manager's static owner/type gate and retracts the earlier 0x2CE200 bounded-false-lead conclusion, which used an incorrect subtraction.

The manager's slot 8 method 0x24B920 forwards the same receiver to 0x22BF00, which passes it to dispatcher 0x22B6C0. That dispatcher reads manager+0x480 and iterates session entries at +0x1A0/+0x1A8/+0x1B0, including index 1. This proves an owner-class dispatch/read path, not the invocation that populates the array. The candidate slot-82 path from 0x22B230 resolves to 0x36A410, which returns -1; reject it as a session initializer.

Root 0xAD5A90 still builds PlayfabSession-shaped objects and stores the three session pointers, but no caller/registration link to the confirmed application manager has been found. Static direct E8, immediate jump, direct RIP, preferred-base pointer and exact RVA-data searches return zero within their documented scopes; the owner-bounded Steam-vtable write scan also finds no writes to the three slots. The full global +0x1A0 write scan completed with 1,686 operands, printed only the first 100, and was too noisy for ownership. Do not repeat it unchanged.

The load caller chain reaches root 0x48FA60 from a chained range within root 0x495640. Root 0x495640 is called from chained range 0x4955B4-0x495623, which resolves to root 0x495560. Root 0x495560 has four direct callers, two from 0x32F385 and two from 0x48E400. Those counts do not name the load mode; the RTTI probes for roots 0x48FA60, 0x495640 and 0x495560 found no validated slot, and the earlier caller audit left 0x48E400 untyped. Interior xref query 0x4955B4 returned zero and is superseded by the root scan against 0x495560. Local/network semantics remain NOT CHECKED. The key byte +0x41C is not a proven network flag. Exact commands and tool hashes are in the latest [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).

Current official release evidence still shows Cosmos 7.06 as the latest Hello Games patch and Nexus package 0.10.2-native-test as limited to Windows/Steam build 25624745. Keep the active 7.05 compatibility profile unchanged and 7.06 disabled. Next action: find the session-array initializer's dynamic invocation/registration path, then resolve the +0x41C producer and load semantics. QAM row, label/resource and live behavior gates also remain open.

### Player-state receiver chain and death-path hazard, 22 October 2026

See the latest [Cosmos 7.06 exact-build report](NATIVE-25732212-COMPATIBILITY.md)
for commands, hashes and full callsite evidence. The named
`cGcPlayerState::LoadFromData` signature remains a zero match, but the four
discovered direct calls to role candidate `0x573500` all pass the same
constructor-identified `cGcPlayerState` at `application+0xB940`. The positive
chain is application global `0x6E8D708` + `0xE70`, constructor
`0x2CEAF0` + `0xAAD0`, and unique `cGcPlayerState::cGcPlayerState` signature
at `0x572410`. Getter `0x2D7A50` independently returns the same
`application+0xE70` subobject.

Correction: the second root `0x32F385` call to `0x495560` at `0x32FC2C` still
passes `RCX=application+0xE70`; its `lea rbx,[rcx+0x20]` only changes the
source of `R8D`. Do not classify the load receiver as `application+0xE90` from
that unrelated argument.

The candidate's incoming `R9B` is overwritten before use; the fifth stack byte
branches to a state-clear helper, but its source parameter name is unknown.
One direct call is in `cGcApplicationDeathState::Update`, with `R9D=0` and
fifth argument `1`. Current native callback flow does not pass or filter that
fifth byte, so enabling a global load hook could treat a death-state call as a
successful local save load. Keep 7.06 fail-closed until a proven local-load
completion boundary or independent exclusion exists. Do not keep scanning the
session key `+0x41C` to label the unused candidate input as network state.

The pinned NMS.py commit and 370-record data are unchanged. Its raw-LF hash is
`14FF4F02D732E31A83885E3ED38A9304900A45D96297A3BA95DA720ED87A8832`; the
CRLF hash is `F311C9F54C0CCE199AB955A0E8DE2CFE2FCFB09274E557A2A27908C1B15BAF5F`.
They parse to the same records, so this difference is line-ending
normalization, not a new provider revision. The zero RTTI-vtable result for
`0x573500` is scoped evidence only; the constructor chain supplies the positive
owner link.

Next bounded action: trace the `0x32F385` local-load success/transition boundary
and compare it with the death-state and `0x48E400` paths. Then continue the
remaining QAM custom-row and resource/render gates. No source/profile/package
mapping changed; no tests, build or live game operation occurred.

### Local-load state-machine follow-up, 22 October 2026

See the latest [Cosmos 7.06 exact-build report](NATIVE-25732212-COMPATIBILITY.md)
for exact commands, full case targets and tool hashes. RTTI validates
`cGcApplicationLocalLoadState` vftable `0x4A50A30`; slot 3 Update root
`0x32EF50` reads and writes a 32-bit state field at `+0x62C` through a 22-case
switch. The transition helper `0x33E1C0` advances values 0-20, maps 21 to 23,
and maps values above 21 to zero. Switch case 21 (`0x3311F0`) performs final
state work and resets `+0x62C` to zero at `0x3317C0`. Treat that as a
`PARTIAL` completion candidate only: local-save completion and death/respawn
exclusion are not established.

`+0x620` is the 32-bit output of the uniquely matched
`cGcApplicationLocalLoadState::GetRespawnReason` at `0x331FB0`. The pinned
provider mangled name identifies the return type as
`cGcPlayerRespawn::RespawnReason`, but its 370-record data contains no
enumerator names. The method computes multiple values from local flags and
global game state; numeric-to-enumerator and user-save-versus-death mappings
remain unknown. Both local Update calls into `0x495560` ignore the return for completion gating. The scoped
GlobalLoadState `+0x62C` scan found zero operands in four RTTI method roots;
this does not prove the field is never accessed through aliases.

The first jump-table decode incorrectly treated unsigned RVA entries as full
virtual addresses and produced negative values; discard that output. Reparse
the 32-bit entries as unsigned RVAs and add the image base only when resolving
the branch targets. This is a reproducible correction, not a binary miss.
Next: map exact-build reason codes against a completed local save load and
death/respawn evidence before selecting a hook point. Keep 7.06 disabled; do
not repeat broad `+0x41C` scans or treat numeric state reset as a verified
completion event.

### Respawn helper relocation and path-sensitive argument mapping, 22 October 2026

The 7.06 replacement candidate for old helper RVA 0x14F7F60 is the exact .pdata root 0x14F9E20. The old address lands inside an instruction in a chained range, with zero direct E8 calls; do not shift it mechanically. The new root has 11 direct callers and matches the old helper's 0x225A length, relocated PLAYER_RESPAWN/DoPlayerRespawn references and player/ship positioning subcalls. This is strong static role corroboration, not byte identity or hook safety.

The local-load return mapping is 0x3302C4 -> 0x330314, 0x33066F -> 0x3306BF, and 0x330946 -> 0x330996. The old returns land inside 7.06 instructions. In switch case 8, the call at 0x33030F passes third argument 1: Update initializes R12D to 1 at 0x32F36F, case 8 dispatches to 0x33025C, and its path to the call has no R12 write. The nearby R12 counter loop is a separate path. The other two local-load calls pass zero. The shared new helper also has death-state and other direct callers, so keep caller filtering and event semantics separate.

Reusable correction: native_branch_xrefs.py counts only direct immediate JMP, not Jcc; its zero for 0x3302BB missed the decoded jne at 0x330276. Use instruction-root disassembly or a complete CFG before asserting that a branch does not exist. A PowerShell executable path containing an apostrophe must be assigned with double quotes; the failed single-quoted wrapper returned no scan evidence. Full commands and hashes are in the [Cosmos 7.06 exact-build report](NATIVE-25732212-COMPATIBILITY.md).

Next bounded action: map the case-8 GetRespawnReason output and prove its event source against the death-state callers. Keep the active 7.05 profile unchanged, 7.06 disabled, and continue the QAM custom-row/resource-render gates.

### GetRespawnReason conditions and exact LocalLoadState writes, 22 October 2026

Exact-build disassembly of 0x331FB0 maps the 32-bit +0x620 result to values {0,1,2,3,4,9,10,11,12,13,16,17,18}; the pinned provider gives type cGcPlayerRespawn::RespawnReason but no enumerator names. Return 11 is computed when application+0x72B068 is nonzero and application+0x72B5A4 is 1 or 14, after earlier guards. This is a static condition, not an event label.

RTTI-bounded LocalLoadState writes map +0x624/+0x625/+0x626/+0x627/+0x628 to exact owner-method stores and clears. Slot 2 root 0x32EAD0 uses RDI copied from RCX and sets +0x625/+0x626 from application conditions; slot 5 root 0x333A60 clears +0x624, +0x625/+0x626, +0x627 and +0x628. A stack-local [RBP+0x628] hit is a false positive. The exact member and method details are in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md).

False lead recorded: slot-offset 0x10 with a +0x625 same-range filter matched 0x32EE1C, but that call's RCX is another object, not the LocalLoadState receiver in RDI. The slot-offset 0x28/+0x624 filter returned zero but is not a no-dispatch proof. Use receiver def-use and vtable identity, not a nearby field displacement. Next: resolve the state-manager invocations of slots 2 and 5, then map case-8 input values. Keep the 7.06 profile disabled.

### QAM builder ABI and LocalLoadState dispatch filter, 22 October 2026

RTTI and root-aligned call evidence map the 7.06 QAM update slot 0 at 0x15286C0 to builder 0x152A1C0. The update passes its third incoming pointer as builder RDX; the builder saves RCX/RDX and calls a stack helper before any original R8 use, then overwrites R8 before its later use. This supports the current two-argument builder hook shape. In the current adapter, the second pointer is range-checked and retained only as an address, then compared by identity after the builder; its native type remains unknown without blocking that narrow source behavior. Custom-row key matching, icon/label rendering, resource lifetime and live UI behavior remain open. See the [exact-build report](NATIVE-25732212-COMPATIBILITY.md) for commands and hashes.

The LocalLoadState vtable storage is initialized at global RVA 0x6E8EA40 by root 0x32BC90. A same-range +0x62C filter for virtual slot offset 0x10 found one call at 0x331B36, but its RCX is application-global +0x905B20, not an independently proven LocalLoadState receiver. Reject it as an owner mapping. Slot offset 0x28 with the same displacement found no range, which is only a bounded filter result. Keep setter invocation and local-save/death meaning unresolved.

Reusable correction: do not infer the receiver from another object field in the same function. Resolve the actual RCX dataflow at the indirect call and independently validate its vtable or constructor identity. If a full-image command returns progress without final totals, poll its returned process session; until the completed summary is captured, mark it NOT CHECKED rather than interpreting the partial output as zero.

### Notice vector owner and count mapping, 22 October 2026

For Cosmos 7.06 build 25732212, caller `0x3BD8EB` passes `app+0x847BB0` to `AddTimedMessage` candidate `0x9BF7B0`; its application pointer is loaded from global RVA `0x6E8D708`. The embedded vector header has capacity at `+0x288`, 32-bit count at `+0x28C`, data pointer at `+0x290`, and `0x2F0`-byte records. Insert helper `0x9D8790` increments the count and returns the possibly reallocated data pointer; `0x8A49A0` clears the same application count during cleanup. The notice method deduplicates against the last message and updates its timer or appends a record. The exact report records commands and tool hashes.

The source count guard matches the native `>3` condition. The source float predicate `!(x < 0)` differs from native `COMISS`/`JAE` on NaN. A write-only exact-displacement scan found zero direct writes to `0x4BF50C` in 52,110,272 decoded `.pdata` bytes, with zero skipped ranges; this does not rule out aliases, helper-based writes, copies or non-`.pdata` initialization. Keep the condition `PARTIAL` and the 7.06 profile disabled. Switch the next bounded analysis to the independent local-save/death gate; retain the notice float producer and runtime range as open.

### Application state manager and local-load/death discriminator, 22 October 2026

The exact 7.06 `cGcApplication` state manager is now mapped. RTTI-confirmed `cTkFSM::Update` (`0x2BE4F60`) applies pending transitions, then dispatches the current state's Update through vtable slot `+0x18`; the current-state pointer is manager `+0x10`. `cTkFSM::AddStates` (`0x2BE0080`) registers each embedded state and writes its manager pointer at state `+0x18`. `APPLOCALLOAD` is the application subobject at `+0x1370` / RVA `0x6E8EA40`, with `cGcApplicationLocalLoadState::Update` root `0x32EF50`.

The direct local path reaches load candidate `0x573500` through `0x32F385 -> 0x495560 -> 0x495640 -> 0x48FA60 -> 0x573500`. The death-state candidate call at `0x2E088F` is in RTTI-confirmed `DeathState::Update` root `0x2DBBB0`; that state requests `APPVIEW` at `0x2E1AA9`, not `APPLOCALLOAD`. Requests apply on the next FSM update, so comparing the current pointer with `moduleBase+0x6E8EA40` is a promising static filter for the direct death path. This is not live proof or a complete indirect-reference audit.

Correction/tool note: the host's `py -3.11` launcher returned `No installed Python found!` before scanning. The explicit CPython 3.11.9 executable completed the commands; record the failed attempt as `TOOL ERROR`, never a zero. Full commands, tool hashes and bounded limitations are in the [exact-build report](NATIVE-25732212-COMPATIBILITY.md). Keep 7.05 unchanged and 7.06 fail-closed. Next bounded action: trace whether the existing callback can read this module-relative identity and gate on the candidate's successful return without changing the 7.05 path; live runtime, QAM rendering and notice-float producer gates remain open.

### Existing callback impact and 7.06 death-path risk, 22 October 2026

The active `loadHook` treats `R9` as `network`, calls `beforeLoad` before the original, and calls `afterLoad` only after the original returns. `afterLoad` requires `network=false`, `result=true` and a valid common-state pointer. The 7.06 DeathState caller supplies `R9D=0`, so reusing this wrapper at `0x573500` without checking the FSM current state could misclassify a successful death-state load as a user save load. A per-build state identity check against `moduleBase+0x6E8EA40` is a static candidate to exclude it; the session-derived byte `+0x4BE6A0` still has unresolved local/network meaning. Keep the 7.05 hook/profile unchanged and 7.06 disabled. Full impact notes are in the [exact-build report](NATIVE-25732212-COMPATIBILITY.md). Next: trace the appended QAM item to a verified label/icon consumer, then return to exact dependency and live gates.

### QAM selected-row label path and remaining icon gate, 22 October 2026

For exact Cosmos 7.06 build 25732212 / SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499, decorated RTTI validates cGcQuickActionMenu vftable 0x4A504E0; slot 9 is 0x153C0C0. Its direct caller 0x1529288 passes the QAM receiver, label output and opaque third argument from a full .pdata scan. The chained method selects a row from the depth-specific vector at QAM+0xA058, uses the 0xE0 stride, and reads that row's action at +4. This confirms a native label consumer for a selected appended row; it does not read the icon handle at row +0. Keep custom-row rendering/resource readiness PARTIAL until a generic renderer read is owner-proven. The broad +0xA058/+0xA060 read scan lost its final output and is NOT CHECKED, not a zero.

RTTI query correction: short type text cGcQuickActionMenu returned no validated locator; exact decorated name .?AVcGcQuickActionMenu@@ returned one. The independent cGcQuickMenuState name query did not establish a base vtable. Use exact decorated names and do not infer missing RTTI from a short-name mismatch.

Upstream recheck on 22 October: Hello Games still lists 7.06 as the newest game release; Nexus still lists 0.10.2-native-test as the latest package and the supported game identity remains 7.05 / build 25624745. No profile mapping was promoted. See the exact-build report for disassembly commands, caller evidence and tool hashes.

Next bounded action: follow the exact QAM receiver into the generic quick-menu draw/resource path and prove a first-dword icon read. Do not repeat broad offset scans whose object base is not tracked. Keep 7.05 unchanged and 7.06 fail-closed.
### RTTI-bound QAM renderer search and false dispatch leads, 22 October 2026

Against the validated 16-slot QAM vftable, seven methods had .pdata groups. Their bounded reads found no +0xA058 or +0xA104 reads; +0xA060 appeared seven times in Update, label and confirmation methods. This supports the selected-vector path but does not show an icon read, and it does not cover external renderer methods or aliases. A vftable-reference scan ties the exact QAM vptr write to constructor 0x2CA6D0; its only direct caller is 0x2CA290, with the established owner offset +0x116B10.

The complete slot-zero RDX/R8 ABI shortlist had 36 candidates. The two inspected nearby roots, 0x2C075EC and 0x2C077C0, are 16-byte stream/compression routines and are rejected as QAM callers. A call-scan request with context 14 failed tool validation; the corrected context-12 scan returned one direct constructor caller. Do not use the generic ABI shortlist as object evidence or repeat it without a new receiver constraint.

Next: trace the QAM object-proven update/render-state caller to a generic renderer and confirm a first-dword read. Keep icon/render readiness PARTIAL and 7.06 fail-closed.

### QAM dispatch and source-row resource path, 22 October 2026

The exact build remains Steam 25732212 / Cosmos 7.06 / SHA-256 `13D5060D4EFB9D2A6A6B1B349BC4257231056CC2A055DF4BB15D816262CC3499`. A reusable `native_embedded_vcall_xrefs.py` scan tracks embedded-object candidates at `owner+0xDC0` and `owner+0x116B10` through a same-range vptr load and indirect call. It returned three QAM dispatches, corroborated against the exact 16-slot RTTI table: slot 3 resets selection/depth, slot 14 checks a state/global predicate, and slot 15 checks an action/state predicate. None is the custom icon renderer. The root-aligned 17-range function group `0x1540CF0` had no slot-zero dispatch; direct E8 scans of QAM Update `0x15286C0` also returned zero, which is expected for a virtual target.

A positive but separate UI resource path reads 0xE0 source rows from `[R13+0x618]`; it reads the first dword and passes it to the keyed resource-cache helper `0x2E16E20`, then writes the returned value through `0x6DE4F0`. This does not prove that the source vector aliases the QAM-owned `+0xA060` row storage or includes custom rows appended there. Mark native source-row resource resolution `PARTIAL`, custom-row icon rendering `NOT MAPPED`, and preserve the distinction in the dependency ledger.

Reusable method: combine the validated RTTI vtable, constructor-proven embedded offset, register-tracked `lea -> object vptr -> virtual slot` path and exact `.pdata` group boundaries. The scanner is local to each `.pdata` range; if the target call spans chained ranges, group-aware provenance is still required. A function VA passed where a tool expects an RVA is a `TOOL ERROR`; convert `VA - ImageBase` before retrying. The detail-mode scanner prototype was interrupted before a final summary (`NOT CHECKED`); only the completed `disasm_lite` scan is evidence. Full commands, output bounds, hashes and the 17 chained ranges are recorded in the exact-build report.

Latest upstream recheck: Hello Games still lists 7.06 as newest; Nexus still lists 0.10.2-native-test, with explicit support only for build 25624745 / Cosmos 7.05. No source/profile mapping changed. Keep 7.05 active, 7.06 disabled. Next bounded action: prove the identity and aliasing of the QAM builder's third-argument row vector and `R13+0x618`; then follow a custom row to a resource consumer or reject the path. Keep local-load/death semantics, notice-float production, custom-row rendering, and live validation open.

### Computed frontend source-vector owner and resource consumer, 22 October 2026

The resource path in root `0x1540CF0` is anchored to caller `0x920721`, which passes `application+0x848670` in `RCX`. The root computes a per-entry object as `(RCX+0x10) + sign_extend(*(int32*)(RCX+4))*0x6D0`; that object's `+0x614/+0x618` fields supply a count and `0xE0`-stride rows. The row's first dword reaches resource lookup `0x2E16E20`, and the resolved value is applied to a UI field through `0x6DE4F0`. This confirms a generic source-row resource consumer. The function also contains QAM slots 3, 15 and 14 on an embedded receiver, but has no slot-zero dispatch in its complete chained group. No pointer identity or alias ties this source vector to the QAM `+0xA058/+0xA060` vectors or to the rows appended by the mod. Keep custom-row icon rendering `PARTIAL` and the profile disabled. The first `$py`/`$nmsExe` invocation failed before analysis because the variables were absent from that PowerShell process; classify it as `TOOL ERROR`. Full commands and hashes are in the [exact-build report](NATIVE-25732212-COMPATIBILITY.md). Next: trace the QAM builder's third argument to this computed per-entry owner or reject the relationship through root-aligned evidence.

### QAM slot-zero caller scan and generic-list false lead, 22 October 2026

For the exact executable hash in the report, the corrected `native_embedded_vcall_xrefs.py` scan of candidate owner offset `0xDC0`, filtered to vtable byte offset `0`, decoded 52,110,272 runtime-function bytes, skipped zero ranges, and returned three overall dispatches but zero slot-zero dispatches. Those three are the already verified QAM slots 3, 14 and 15. The scan at owner offset `0x10` produced 264 overall candidates and four slot-zero candidates; none has a constructor/RTTI chain proving the receiver is the QAM.

One candidate at `0x183DA4E` dispatches slot zero on a dynamically indexed object at `rsi+0x10`, then dispatches slot one, and the root later clears the list count/data/capacity and a related global. Eight direct callers enter this list-clearing routine. This is a generic object-list teardown path, not proof of QAM Update. Three other candidates (`0x31AF0B2`, `0x31AF570`, `0x31AF8DA`) do not set the QAM method's required third argument after an intervening call; `R8` is volatile, so an earlier `R8D` value cannot establish the call argument. Reject these as QAM caller matches.

The exact decorated RTTI query still validates `0x15286C0` as slot zero of `.?AVcGcQuickActionMenu@@`. A direct-E8 scan finds no callers to that virtual target (as expected for an indirect dispatch); it is not a search for all virtual callers. The corrected scanner now keeps vptr-derived slot state separate from a loaded function pointer so a second memory displacement cannot be mistaken for another vtable slot. This fixes a candidate-classification error, not the remaining group-wide provenance gap.

Reusable lesson: a generic `call [vptr+0]` or a matching embedded offset is not a class-bound Update call. Require the constructor-proven QAM receiver, complete chained `.pdata` provenance, and the third argument immediately before the indirect call. Do not infer `R8` across another call. Correct the PowerShell quoting before analysis when a path contains an apostrophe; a parser failure before executable access is `TOOL ERROR`, not a zero.

The QAM Update caller and its row-vector identity remain `NOT CHECKED`; custom-row icon rendering remains `PARTIAL`; 7.06 remains disabled. Keep the 7.05 profile active. Exact commands, scanner outputs, rejected candidates, and tool hashes are recorded in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md). Next: perform group-aware provenance from the constructor-proven QAM address `app+0x849430` through each indirect-call site and capture the actual `R8` definition at the dispatch; do not repeat generic offset or ABI-shape scans.

### Exact QAM address scan confirms only the state-selector slot, 22 October 2026

A completed exact-offset scan for `0x849430` decoded 52,110,272 runtime-function bytes with zero skipped ranges and found one indirect dispatch: `0x14642C8`, slot byte offset `0x58` (slot 11), in the known state selector rooted at `0x1464200`. The slot-zero filter returned zero. This positive control confirms that the scan sees a real QAM receiver at the exact composed address; it does not find the QAM Update caller. The helper is per `.pdata` range and does not carry an object pointer into another chained fragment or a callee that receives an already formed QAM pointer. Keep the slot-zero caller and row-vector identity unresolved; follow exact receiver provenance across full groups and function-argument boundaries.

### Group-aware QAM search and argument-seeded caller shortlist, 22 October 2026

The corrected group-aware scan uses the full `UNW_FLAG_CHAININFO` group and direct branch edges. A first version returned zero because it compared VA with RVA for sequential edges and failed its positive control; discard that run. After fixing the coordinate conversion, the scan reproduced known QAM slots 3, 11, 14 and 15 in three groups and found no slot-zero candidate for offsets `0xDC0`, `0x848670`, or `0x849430`. It processed 115 offset-bearing groups with no state truncation. Eight undecoded ranges totalling 420 bytes remain explicitly unclassified; their roles are not proof of absence.

Seeding the function-entry `RCX` as an unknown object produced 83 generic slot-zero candidates in 71 groups. A batched direct-E8 caller scan found the only QAM-offset contexts on the two known calls to `0x1540430`, and both pass the parent `global+0x848670`, not the child QAM `global+0x849430`. The root's candidate slot-zero call is on that parent; its proven child call is slot 3. Treat generic candidates as a shortlist only. Direct-call scanning and 12-instruction context cannot eliminate indirect callers or values formed earlier than the context window.

An output-handoff attempt between PowerShell processes failed because temporary directories were isolated by the sandbox. The corrected pass ran both scans in one PowerShell process, used a unique repository-local scratch file, split the 71 targets into batches of at most 64, and removed the scratch files. Keep the actual QAM Update caller and row-vector owner unresolved; 7.06 stays disabled. See the exact-build report for commands, tool hashes, skipped range addresses, and result details.

### Shared cGcQuickMenu parent and indexed source-vector relationship, 22 October 2026

Correction: the two following paragraphs' three-entry/index-2 interpretation is superseded by the constructor-loop audit below. The shared parent and QAM offset remain corroborated.

The constructor chain confirms that roots 0x1540430 and 0x1540CF0 receive the same cGcQuickMenu object at app+0x848670. The application pointer cell is RVA 0x6E8D708; initializer roots 0x2C6E20 and 0x2C8EC0 lead to cGcQuickMenu constructor 0x2CA290 at that parent. The constructor initializes three entries at offsets +0x10, +0x6E0 and +0xDB0, stride 0x6D0, and constructs QAM at +0xDC0. Root 0x1540430 calls QAM slot 3; root 0x1540CF0 calls slots 15 and 14 on that same QAM.

The resource source vector is a separate indexed entry: (parent+0x10)+sign_extend(*(int32*)(parent+4))*0x6D0, with count/pointer at +0x614/+0x618. If index 2, QAM is the entry's +0x10 subobject; the active index and QAM Update third-argument data flow remain unproven. A completed slot-0 scan requiring same-range fields 0xDC0 and 0x618 returned zero matching ranges and zero indirect calls across the decoded .pdata bytes. Its first progress-only attempt lost the final output and is NOT CHECKED; the completed rerun is only a same-range filter. Same-parent identity strengthens the resource lead but does not prove aliasing with QAM vectors +0xA058/+0xA060 or rendering of custom rows. Keep the icon gate partial and 7.06 disabled. Exact evidence and commands are in the [Cosmos 7.06 report](NATIVE-25732212-COMPATIBILITY.md). Next: trace the actual QAM Update caller's third argument into this indexed entry.

### Dynamic `+0x10` slot-zero candidates and scan truncation, 22 October 2026

A group-aware full-image query for object offset `0x10` and slot offset `0` decoded 52,109,852 runtime-function bytes, with the same eight undecoded ranges (420 bytes). It reported eight candidate dispatch records at seven unique call RVAs in six roots: `0x183DA00`, `0x31AEF60`, `0x31AF460`, `0x31AF7B0`, `0x31E0A50`, and `0x31E3780`. The two records at `0x31E0C5A` differ only in candidate object provenance. The pass processed 20,029 offset-bearing groups; 987 groups hit the 64-state limit, so this is not a complete inventory and its unreported paths are `NOT CHECKED`.

The known `0x183DA4E` path is the previously identified generic list-clear/teardown loop. The `0x31AF0B2`, `0x31AF570`, and `0x31AF8DA` candidates do not establish the required `R8` after an intervening virtual call. New candidates are `0x31E0C5A`, `0x31E3930`, and `0x31E39B9`, rooted at `0x31E0A50` or `0x31E3780`; RTTI probes for both roots returned zero validated vftable slots. Direct E8 references connect `0x31E3780` to `0x31E0A50`, and to caller roots `0x31E0A36` and `0x31E1B10`, but none proves a QAM receiver or row-owner argument. Keep all three as unresolved generic leads, not confirmed QAM callers. Do not treat the zero RTTI probes as proof that no other table form exists.

This broad `+0x10` pass did not close the slot-zero or row-vector gate. Static coverage remains 67/85 `MAPPED`, 14 `PARTIAL`, 4 `NOT CHECKED`; 7.06 remains disabled and 7.05 active. Next: constrain dynamic `+0x10` receiver tracking to the constructor-proven quick-menu owner/index expression and trace its call arguments, rather than increasing the global state limit or repeating the unbounded scan.

### RTTI classification of argument-seeded slot-zero candidates, 22 October 2026

Against the same Cosmos 7.06 executable, the argument-seeded group scan again yielded 83 generic slot-zero dispatches in 71 function groups. A batched literal preferred-image-base pointer scan found exact raw-pointer references for 23 roots and none for 48. RTTI validation of the 23 referenced roots identified six function roots in seven RTTI-backed vtable slots: `0x21BBC0` (`cGcNGuiSceneInfoTreeViewNodeData`, slot 2), `0x2C51B0` (`cGcFadeNode` and `cGcFadeNodeBase`, slot 3), `0x160E5B0` (`cGcAsteroidGrid` and `cGcVoxelAsteroidGrid`, slot 4), `0x2DC7040` (`cTk2dLayer`, slot 17), `0x2E37650` (`HgVocAlien`, slot 1), and `0x2E37690` (`HgVocAlienParams`, slot 4). The other 17 raw-reference roots had no RTTI-validated vtable hit within the 64-slot probe. No validated owner was `cGcQuickActionMenu`.

This narrows the generic shortlist but does not identify a QAM Update caller: a method's owning vtable does not establish that its incoming `RCX` is a QAM, and the raw-pointer scan only covers literal preferred-base pointers in non-relocation sections. Relative tables, relocated/dynamic references, or indirect callers remain outside that negative. Keep the caller and row-vector identity `NOT CHECKED`, custom-row icon rendering `PARTIAL`, Cosmos 7.05 active, and 7.06 disabled. No source/profile/package mapping changed. Next: continue from the constructor-proven QAM pointer through caller/argument boundaries and accept a candidate only when the exact dispatch has `RCX=app+0x849430` and the required row owner in `R8`.

### Public build recheck and bounded `+0x10` scan, 22 October 2026

Hello Games' [7.06 release note](https://www.nomanssky.com/2026/10/cosmos-7-06/) remains the latest public patch found; SteamDB's [public branch listing](https://steamdb.info/app/275850/depots/) reports build `25732212`, last updated 5 October. The local executable still matches its exact SHA-256. No 7.07/public build update was found.

The `--require-immediate 0x6D0` scanner filter reproduced three known QAM parent slots as a positive control, but it is group-level and too broad to prove a stride. The target scan found zero `+0x10` slot-zero candidates, but seven groups truncated. Six roots used `0x6D0` as `sub rsp` stack allocation; root `0x982BE0` used it as a repeated-subrecord increment without a proven QAM owner. Thus this pass closes no dependency and cannot support a negative claim. Record the full root list and `NOT CHECKED` boundary in `NATIVE-25732212-COMPATIBILITY.md`. The safer next step is to filter on the constructor-proven indexed owner and instruction/dataflow role, then inspect the remaining bounded group roots; do not raise the full-image state cap or equate an immediate match with a class match.
The direct indexed-menu helpers are now classified: root `0x1540CF0` uses `0x6D0` as an entry stride, calls a dword-zeroing helper at `0x2C36D0` and a bitset set/clear helper at `0x2C3740`, and dispatches QAM slots 14/15. Its complete 17-range group has no slot-zero call. A separate exact QAM pointer consumer at root `0x1464200` forms application+`0x849430` and calls QAM slot 11 behind a menu-state guard; it is not Update. These exact owner/caller anchors narrow the search but leave the Update caller and row owner unresolved. See the exact-build report for command and hash evidence.
The RTTI-backed QAM slot-zero Update target `0x15286C0` has zero direct decoded E8-style call references in the full `.pdata` scan; indirect/vtable calls remain outside that check. This rules out only direct calls and does not close the caller gate. Keep Update-caller discovery `NOT CHECKED` and 7.06 disabled.

### Correction: nested QAM Update dispatch found, 22 October 2026

The earlier argument-seeded interpretation of `0x15404FF` as a call on the root's incoming parent is superseded. Root `0x1540430` receives the parent `app+0x848670`, but selector value 1 materializes `0xDC0` in `EAX`, forms `RSI=RDI+RAX`, then dispatches virtual slot 0 with `RCX=RSI`. Constructor and RTTI evidence identify the receiver as the QAM at `app+0x849430`; vtable slot 0 targets Update method `0x15286C0`. The parent receiver at the outer call and the QAM receiver at the nested call are distinct.

The exact call also sets `R8=parent+sign_extend(*(int32*)parent)*0x6D0+0x10`. QAM Update stores this pointer and uses it as a record/context object. Its identity with the separate source-vector path indexed by `parent+4` and the `+0x614/+0x618` header is still unproven. The static QAM caller subgate is now corroborated; row-vector aliasing, custom-row rendering, live behavior and release gates remain open. Static source-dependency totals do not change because this nested dispatch is not an additional row in the 85-item source ledger. Keep 7.05 active and 7.06 disabled.

Reusable rule: follow register-held constants and scaled-index expressions through the complete chained function before naming the receiver; never reuse the wrapper's incoming `RCX` as the identity of a nested virtual call. See the exact-build report for commands, hashes, argument limits and the bounded root scan.

### Two-record constructor and post-Update index transfer, 22 October 2026

The complete constructor range `0x2CA290-0x2CA6CF` initializes exactly two `0x6D0` records: `parent+0x10` and `parent+0x6E0`. Its counter starts at 2; the body advances the record pointer, decrements the counter and repeats only while nonzero. The pointer ends at `parent+0xDB0`, but that address is not a third initialized record. The QAM is constructed independently at `parent+0xDC0`. The earlier index-2/QAM-overlap hypothesis is rejected; do not reuse it as owner evidence.

After the nested QAM Update call at `0x15404FF`, the wrapper freshly reads the 32-bit `parent+0` at `0x1540629`, writes that value to `parent+4` at `0x1540630`, then writes `(value == 0)` to `parent+0` at `0x1540639`. The wrapper itself makes no other call between Update and the copy. Update received a record selected by the pre-call value of `parent+0`; the resource consumer uses `parent+4`. This is a concrete index-transfer bridge. Exact record identity still requires checking callee mutation, concurrency and consumer ordering. Two-buffer alternation is an interpretation supported by the loop and transition, not live proof.

Static source coverage remains `67/85 MAPPED`, `14 PARTIAL`, `4 NOT CHECKED`; no source/profile mapping or release gate changed. Keep 7.05 active and 7.06 disabled. Next: follow the selected record's `+0x610` vector-header producer and the QAM source rows into the resource consumer; independently bound Update's possible writes to the parent index. The exact-build report contains the commands and scope.

### Copied QAM rows reach the native resource-consumer schema, 22 October 2026

The preceding next action is now partly resolved. The 12 October review already mapped `0x2BF9A00` as a vector-copy/resize helper and recorded its QAM Update call. Combining that retained exact-hash result with the newly resolved incoming `R8` record owner and the generic resource path closes the missing field/consumer relationship: Update copies `menu+0xA058+depth*0x10` rows into `incoming_record+0x610`, with count/data at `+0x614/+0x618` and stride `0xE0`. The resource consumer reads this record schema and uses the copied first dword as a resource key. It is a copy, not pointer aliasing. Requiring aliasing had prolonged this search unnecessarily.

Precise callsite correction: `0x1542038` loads the key into `R8D`; the call to `0x2E16E20` is `0x1542040`. The output is read as a dword from the stack temporary at `0x1542045` and applied through `0x6DE4F0` at `0x154204D`; it is not this call's `RAX` result. This promotes only the static `QAM item icon dword` ledger role. Exact index handoff/ordering, custom-row retention, resource lifetime/thread and visible rendering remain separate gates. Update's direct parent-pointer helper `0x3F79D0` is read-only; the other transitive helper effects are not exhaustively checked. The source `item+0xD8` invariant remains partial because copied-row writes do not establish original-row writes.

An independent scanner audit corrected shared fact sets, double LEA displacement, unsupported signed/scaled expressions and memory-first XCHG invalidation. The exact-root slot-zero reproduction still finds only `0x15404FF` on `parent+0xDC0`; its all-slot control has seven records at six unique callsites, each with 2,234 bytes and zero reported decode/state truncations. Updated helper SHA-256 is `76be238c22fbe14d9352c57d8e0cb8f88e7f35050c92a0887cea939ae8a298dd`. Width/implicit-clobber modeling and partial-decode accounting remain limited; do not infer broad completeness. Full commands and tool identities are in the [exact-build handoff](NATIVE-25732212-COMPATIBILITY.md#constructor-correction-copied-row-resource-consumer-and-scanner-audit-22-october-2026).

Current static ledger: **68/85 MAPPED (80.0%), 13 PARTIAL, 4 NOT CHECKED**, superseding 67/14/4. No native/profile mapping, game operation, test, build, package, push or publication occurred in this follow-up. Keep Cosmos 7.05 active and 7.06 disabled. Next bounded action: follow the copied-row consumer's `+8/+0x40/+0x54` predicates and the source fields `+0x4C/+0x4D/+0x88/+0x98/+0xD8`; determine required custom-row state without confusing writes to source and copied rows. Do not restart the resolved QAM Update caller search. Reuse rule: search the existing ledger for both endpoints and their helper/header bases, then join verified copy/producer/consumer evidence before widening a scan.

### Row/identity corrections and composite owner-field setters, 23 October 2026

The exact executable hash and source base are unchanged. The [exact-build report](NATIVE-25732212-COMPATIBILITY.md#current-gate-index-23-october-2026) now starts with the seven remaining static gates and their bounded next actions. Its current ledger is **78/85 MAPPED (91.8%), 7 PARTIAL, 0 NOT CHECKED**. Six field roles closed; four additional status changes reconcile already recorded static sites. This is not live compatibility or release readiness. Keep 7.05 active and 7.06 disabled.

Reusable corrections and successes:

- Roster identity: `RDI` in `0x50E1A0` is reassigned from a resolver result to `app+0xE10D0+roster_index*0x24A0` before the `+0x2330` read. Helper `0x227E80`, called by roster copier `0x506500`, independently copies the same 16-byte field. The source reads its first eight bytes. The old resolver-owner requirement is rejected; uniqueness/persistence remain live/semantic gates.
- Native row predicates: constructor defaults `+8=0`, `+0x40=-1`, `+0x54=0` admit the ordinary icon path when its key is nonzero. Copied-row `+0x4C` selects native scalar/tint branches, and `+0x4D` is inverted into a UI-node byte at `0x1541FEC`. The auxiliary `+0x98..0xD7` span is bounded inline text, separate from the main label; this constructor copies one NUL into its 64-byte capacity. These producer/consumer contracts close three static roles.
- Affine pointer correction: matcher `RSI` simplifies to context-descriptor base `+4`. The alleged item `+0x4C` write is descriptor `+0x50`; the old `0xFFFF0100` versus `0x15` protection argument is invalid. The action-`0x15` block is bypassed by custom action zero. Header keys and copied source rows must keep distinct bases; marker retention and source `+0xD8` remain partial.
- New owner-field setters: `owner=app+0xE10D0` converts preview `owner+0x1B9300` to `app+0x29A3D0` and the byte `owner+0x1B937D` to `app+0x29A44D`. Exact review of root `0x1540CF0` proves selected-slot assignment/clear (`0x154361F`, `0x1543512/0x1543646`) and byte set/clear (`0x1543703/0x154373C`). Existing owner-update readers close both field contracts. The byte is a native menu/placement guard; its old source name emote is not independently proven.
- Inventory correction: compiler defaults do not decide player scope. The public packager requires the trial receipt, which defines both observer/trial macros. Keep all 85 roles. The 22 October report already mapped three exact returns (`0x330314/0x3306BF/0x330996`) and binding-filter site `0x15292F5`; stale ledger states are now reconciled, not claimed as new matches. Observer candidate `0x14F9E20` remains partial for ABI/event policy.

The composed-offset scan completed 52,110,272 runtime-function bytes with zero skipped ranges and all candidates printed. The interrupted earlier attempt lost its final output and is NOT CHECKED; only the completed rerun supplies counts. Commands, tool hashes and exact predicates are in the dated report handoff. No source RVA/profile edit, tests, build, package, live game operation, commit, push or publication occurred. Next: texture-resource constructor/allocation/error-byte producer or the observer's physical forwarding. Do not restart the resolved QAM caller and owner-field searches. For future passes, normalize fields to every proven enclosing owner, simplify cancelling pointer arithmetic and reconcile completed evidence with the gate index in the same work period.

### Registered texture allocation and early runtime workflow, 23 October 2026

Current exact-build ledger: **79/85 MAPPED (92.9%), 6 PARTIAL, 0 NOT CHECKED**, superseding 78/7/0. The registered type-7 allocation closes resource minimum extent statically. Type registration `0x183CC71` passes factory `0x1834A80`; registrar `0x2D6B355` stores it at the type node's `+0x38`, read/called by loader `0x2D6424A/0x2D64322`. The factory allocates `0x400`, constructs via `0x1894A20`, and initializes payload `+0x1F8` through `0x1888100/0x18881D0`. The payload qword write at `+0x68` proves resource `+0x260..+0x267`. The common initializer zeroes `+0x13A` within a wider dword and the copier preserves it, but its error meaning remains open.

Reuse the allocation/registration/indirect-call def-use chain rather than requiring a convenient derived-class name. A raw leaf for offset `+0x13A` was instead `GPN::SearchContext` (validated RTTI), a false lead. Ad hoc derived-vptr COL parsing failed before validation; it established no class. Bound name queries and include MSVC `.?AU` when structs matter. Optional range bounds and signed displacements in the field scanner now support local reproductions; excluded/chained ranges are not absence evidence. Exact commands, hashes, counts, getter rejection and window limits are in the [factory handoff](NATIVE-25732212-COMPATIBILITY.md#registered-type-7-factory-and-analysis-helper-corrections-23-october-2026).

The owner authorized launching NMS. A verified private closed-game snapshot covered 61 save files plus two preferences (63 files, 8,566,112 bytes), with protected current-user/SYSTEM permissions outside Git. Sandbox backup/launch attempts did not prove success: redirected environment paths and access denial required the authorized desktop context. Check the actual process after a Steam URI request; never weaken backup permissions or call an incomplete snapshot verified.

The development-only `native_readonly_resource_snapshot.py` uses VM_READ and limited process queries, exact file/process/header/code anchors and bounded repeated reads. Startup observed all 6,580 entries; loaded-game captures intentionally examined only the first 10,000 of roughly 76,000. In the owner-confirmed open pet menu, depth 1 had six source/six copied rows with matching icon/action keys and distinct write/consumed indices 1/0. After X closed, depth 0 had seven source/six cached rows, with different keys. Ship entry was also reported; final differences cannot all be assigned solely to closure. All sampled type-7 objects had vptr `0x4B02D68` and bytes `+0x138..+0x13C=[1,0,0,0,1]`; the stock pet icon had a nonzero texture. Normal-state zeros do not establish error semantics or custom-row safety.

AGENTS.md, DEVELOPMENT.md and the mandatory playbook now require early runtime planning, a passive observation after one unproductive static attempt on an observable question, one short player action at a time, baseline/action/after-state, explicit confounders and reuse of the smallest successful command. Do independent work while awaiting the player. The [read-only handoff](NATIVE-25732212-COMPATIBILITY.md#early-read-only-game-observations-and-development-rule-23-october-2026) records both helper hashes and exact results. This prevents another static-only delay without claiming stock-game observations verify an uninstalled mod.

No native profile/RVA mapping, installed runtime, hook, implementation test suite, build, package, commit, push or publication changed. Keep 7.05 active and 7.06 disabled. Six static gates, implementation, exact-archive behavior and release remain open. Next: same-object positive `+0x13A` producer/consumer, source marker/binding retention and the remaining observer/load policy. Do not restart QAM caller discovery.

### Resource failure and deliberate HUD float policy, 23 October 2026

Current static ledger is **81/85 MAPPED (95.3%), 4 PARTIAL, 0 NOT CHECKED**, superseding 79/6/0. Following the runtime-observed type-7 vptr `0x4B02D68` to slot 13 (`0x1895AE0`) connects the same texture object directly to validator `0x18DD960`. Null/empty resource data takes a missing-data diagnostic branch, writes word `+0x139=0x0101` at `0x18DD9C3` (setting `+0x13A=1`), and returns false. Its initializer/copy were already mapped. Manager helper `0x18385F0` independently checks the same byte at `0x1838784` to veto a keyed insertion. The resource error role is now statically mapped; live failure injection was not performed.

The HUD float gate is also closed statically by an explicit source policy. Native COMISS/JAE rejects ordered nonnegative values and can continue for NaN; the existing source `<0` requirement deliberately refuses NaN before a cosmetic call. Preserve that conservative predicate. Only a source comment explains it; there is no behavior or locale change. Finite negative values were observed twice. Producer naming and full numeric range are unknown, with visible candidate delivery still a live gate.

Reuse lesson: follow the exact observed vptr/method and argument into a failure producer, and include wider overlapping stores; the useful byte setter was a word at `+0x139` outside the initial window. A known native/source truth-table difference can be an intentional stricter cosmetic policy when explicitly justified; do not expand that into permission to guess event, local/network or ABI semantics. The singular `--rva` group option does not batch repeated arguments; only the last was selected. A no-`.pdata` virtual target remains a possible leaf/thunk.

The [final exact-build handoff](NATIVE-25732212-COMPATIBILITY.md#missing-data-failure-byte-and-conservative-notice-policy-23-october-2026) records full direct-call counts, bounded/truncated field candidates, exact commands, hashes, and deferred checks. No native mapping/profile, build, implementation tests, package, deployment, commit, push or release changed. Four static gates remain: load policy, observer ABI/event policy, custom-marker retention and original-row binding invariant. Keep 7.05 active and 7.06 disabled. Next: first-callee input use at observer `0x14F9E20`, then the exact LocalLoadState event policy.


### Observer first-callee result and next passive trace, 23 October 2026

Static ledger remains **81/85 MAPPED, 4 PARTIAL, 0 NOT CHECKED**. Observer `0x14F9E20` reaches `0x563060` without consuming incoming R9 in the reviewed prefix; the complete callee overwrites R9 at `0x56306A` before use. That specific escape concern is resolved. Stack aliases and reason/completion/local-network policy remain open. A bounded reproduction of copied-row `+0xD8` writes and known navigation helper `0x1530AC0` added no original-row retention evidence; keep the two row gates partial instead of repeating that search.

The owner can save/close the game; no further game operation followed. A development-only `native_readonly_lifecycle_trace.py` is prepared for a later baseline/action/after-state observation of FSM, LocalLoadState phase/reason and the session-linked predicate. It shares the extracted actual-process guard and polls for at most 45 seconds, without hooks, native calls, game writes or private identifiers. **The new poller and refactored reader are NOT CHECKED**; earlier resource/menu observations cover their recorded older hashes. The [exact handoff](NATIVE-25732212-COMPATIBILITY.md#observer-first-callee-audit-and-prepared-lifecycle-observation-23-october-2026) records hashes, exact fields, command, limits and the next discriminator.

Next: first verify the prepared passive observation in an authorized game session, capture a confirmed local-save action and separately a teleport, and keep missed transitions/unproven callback semantics explicit. Do not enable an unverified native profile or interpret reason 11 as a verified enum. No implementation test suite, native mapping, build, package, deployment or release changed. The local checkpoint preserves analysis/rules while the four static and subsequent implementation/live/release gates remain open.

### Local research checkpoint receipt, 23 October 2026

Local commit `42190cb47df723fa28b96c69ececa4a630305b17` preserves the rules, reports, analysis helpers and comment-only HUD clarification on `compat/cosmos-706-25732212`, authored with `core@lineum.io`. The source baseline under investigation remains `f7d97b61fcf152677d0d30de34f6c1b48675c436`; the pre-existing bootstrap ABI edit remains outside this checkpoint. The staged whitespace inspection passed after removing two whitespace-only lines. No implementation tests, build, package, new deployment, push or publication ran. Personal interpreter paths were replaced with verified-path aliases without changing recorded argument values or input hashes. An initial sandbox Git-index lock denial was resolved using the authorized desktop context; no failed attempt was called a commit.

The current static ledger is **81/85 MAPPED, 4 PARTIAL, 0 NOT CHECKED**, with new lifecycle tooling explicitly NOT CHECKED separately. The public package remains `0.10.2-native-test` for Cosmos 7.05; the target remains Cosmos 7.06 / build 25732212 / exact SHA-256 recorded above. Next is the prepared player-assisted lifecycle observation and the remaining row-retention work, followed by source/profile implementation and the independent offline/live/archive/release gates. This receipt records a local checkpoint, not GitHub synchronization or a supported update.

### Local load, teleport, menu and source preparation handoff, 23 October 2026

Target remains Cosmos 7.06 / Steam 25732212 / file version 180836 /
88,560,712 bytes / SHA-256
`13D5060D4EFB9D2A6A6B1B349BC4257231056CC2A055DF4BB15D816262CC3499`.
The [exact-build handoff](NATIVE-25732212-COMPATIBILITY.md#local-load-teleport-and-menu-observations-23-october-2026)
records all commands, hashes, counts and limits. The original source baseline
is f7d97b61; this work period started at local checkpoint 508526c.

- Fresh closed-game backup: 63 files / 8,612,490 bytes, verified hashes and
  private ACL, then actual process verification after a normal Steam launch.
- One confirmed save-load trace: 893 samples/14 changes, applied LocalLoadState
  `0x6E8EA40`, reason 0 -> 1 at phase 8, then phase 0 outside that state.
  Source predicate stayed zero; session slot stayed absent. This is not a
  general local/network classifier or actual hook-completion proof.
- Confirmed teleport to station: 45-second window missed transitions; immediate
  after-state reason 11. Confirmed return to base: a longer 120-second window
  also saw no phase change (2,378 samples). Do not repeat an unchanged third
  teleport poll; use a different anchor for exact callback timing.
- Closed X baseline had nine original/zero copied rows. Two open-pet-menu
  snapshots each had six original/copied rows, equal icon/action and marker
  fields, two nonzero markers and all `+0xD8=-1`. Only stock rows were read;
  custom sentinel/rebuild/thread behavior is not validated.
- Lifecycle revisions: initial A3B7A930... remains unexecuted; 64104B09... covers
  the first captures; C785323A... extends ready-baseline capture to 1..180 s.
  Shared reader 7A550B94... actual-process guard was exercised. Aggregate
  menu reader 96DEE154... covers the last three snapshots. Use the exact
  report's full hashes; do not attach evidence to a different tool revision.
- Observer root `0x14F9E20..0x14FC07A` fully decoded: 8,794 bytes, 330 direct
  stack operands, no access at/crossing fifth argument `entryRSP+0x28`.
  All nine home-address escapes are now bounded through complete consumers:
  four-byte scalar leaves, six-byte word object, one-byte output pointers.
  The first callee overwrites incoming R9 before use. Three physical inputs
  are supported; reason/event and multiplayer claims remain separate.
- A bounded filename search found no retained old NMS executable in the named
  repositories/Documents scope; this is not global absence and no download
  followed. Missing `.pdata` on the three small leaves was resolved through
  bounded entry/branch/return decoding, not an absence conclusion.

`native_mappings.json` now supplies exact-build native function/global RVAs,
return filters and load policies to generated C++, build receipts, validation
and packaging. A correct build label with a foreign hash is rejected.
The prepared 7.06 applied-state/vtable/local-receiver guard preserves original
arguments/results and the existing zero-only veto, whose network meaning
remains unknown. Its four new native inputs were added to the inventory:
**85/89 MAPPED, 4 PARTIAL**; this is not release readiness. The native profile
still selects 7.05 and 7.06 retains activation_approved=false.

Passed: 38 focused tests; final full runs 403 production + 805 developer;
7.05 regression build/bundle (63 runtime cases, 16 backup checks, six refused
owned hosts), 25 menu scenarios and 213-byte emitter parity. Initial sandbox
temp-file failures passed in an explicit owned temp directory. The first
backup fixture hit sharing violation 32 during concurrent file-writing tests;
individual opens and a serial full bundle rerun passed. Keep this as bounded
environment evidence; do not weaken backup locking/ACLs to force a pass.
Run ancestor-lock backup fixtures separately from workspace writers.

Next: owned-memory checks of the prepared load guard, then reconcile static
field/guard mapping separately from actual custom-row retention and exact
candidate game acceptance. No new package/install/push/publication or
player-facing text change. Do not restart the resolved caller/ABI searches.

### Candidate selection, offline acceptance and first deployed trial, 23 October 2026

Static source contracts are now 89/89 MAPPED (four guard/copy/ABI reconciliations,
not four new signatures). The unpublished 0.10.3 profile selects exact 7.06 /
25732212 /13D5060D...; public 0.10.2 still targets 7.05. Passing a guarded static
contract does not close event or exact-archive gameplay acceptance. See the
[full handoff](NATIVE-25732212-COMPATIBILITY.md#candidate-selection-offline-acceptance-and-first-deployed-trial-23-october-2026)
and [immutable candidate identities](../release/0.10.3-COSMOS-706.md).

r1 passed 403 production +807 developer tests, full owned bundle (including 13
load-context cases), 28 menu scenarios and ZIP readback. The owner approved
native deployment. Fresh closed-game/private backup: 63 files/8,688,127 bytes.
Ten overlay files verified; only the owned ASI changed; old runtime preserved,
correct loader and icons reused. Normal Steam launch, exact loaded module and
native active status independently verified. The owner confirmed menu/icons,
manual pet and, after a clean no-pet baseline, automatic ship-exit appearance;
queue acceptance corroborated that specific event. Existing Automation OFF
was retained until the owner switched ON through the menu.

A main-menu reload while standing outside produced no pet and no logged load
opportunity. That acceptance gate remains open; r2 adds bounded predicate masks,
caller RVAs and Boolean results without changing the guard or original ABI.
The owner closed normally for the next trial. Next: r2 offline/package gates,
fresh verified deployment, then one discriminating load, rather than repeated
broad static scans. No public push/upload, death or multiplayer acceptance.

Reusable lessons: establish no-pet baseline before claiming a new summon;
queued settings may persist only after menu closure; read the fixed per-process
log directly if timestamp/metadata filtering misses a newly opened file. Treat
the Windows system WINMM and pinned proxy as distinct identities. For atomic
replacement from PowerShell, a null string argument needs Language.NullString
rather than an empty path; preserve and verify the previous owned file first.
Do not weaken existing safety checks after a tool/environment failure.

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

- Exact game target is unchanged: Windows/Steam Cosmos 7.06 / build 25732212,
  NMS.exe SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
  No executable decode, mapping edit or new compatibility claim occurred.
  Frozen candidate source remains `7fd4bc09a3185a214a808052da61f2223999619b`;
  package is 0.10.4-native-test, distinct from the existing 0.10.3 submission.
- Prior authorized exact-candidate ASI upload now completed: hash 765cdbdf...
  reports 17/70 at 27 October 07:47:26 UTC. The unchanged 0.10.3 ASI,
  hash 6474247c..., completed reanalysis at 07:50:46 UTC with 30/70.
  Same 75 vendor rows; one confirmed timeout and four unsupported per table.
  Candidate flagged vendors are a subset of the original's, but engine
  definition equality and repair causality are NOT CHECKED, not established.
- New candidate-specific CAPE evidence: All mode exposes 358 API rows,
  first callers 344 rundll32 / 9 outside both images / 5 zero / 0 sample.
  The trace resolves sample ordinal 1 to RVA 0x90E0, CasInspectHost;
  InitializeASI is ordinal 3. Wrong-ABI sandbox invocation is not game
  initialization proof. Four CryptoAPI HTTP requests lack PID/module
  attribution. Candidate PE Security directory is 0/0; the TLS callback
  table's first qword is zero. No generic-label-based payload inference.
- Tools: hidden IAB visible DOM and CPython 3.11.9 / pefile 2024.8.26;
  read only the exact module after SHA-256 verification, classify each
  captured first caller against recorded image base/size and exact SizeOfImage.
  Complete sanitized receipts are in NATIVE-0104-VT-EVIDENCE-20261027.json,
  SHA-256 `d3eaab4e3546af9ae56ff826097c252f72ef34a6a84d494b33ce4b2f69173237`.
  Raw report logs, machine paths and signed report URLs are not published.
- Main file 50040 remains quarantined. Candidate ZIP was selected only;
  automatic approval review rejected upload after the service's archive
  scan-limit warning. Do not retry through another route or transform bytes.
  Loader report readback is historical 22 October 0/49, with non-results,
  not a new comparable scan. No local security setting or installed file changed.
- Zenbox subsequently completed: exact candidate 4/100 Non Malicious, provider
  timestamp 27/10/2026 07:55:35 (timezone unspecified). It also invokes
  InitializeASI; do not extend CAPE's ordinal-1-only scope to Zenbox. Ten
  per-process Extra Info records are None. Its filename mismatch is the
  provider's attachment.dll versus PE CompanionAutoSummon.asi; 15 sections
  include seven debug sections. Entire 647,168-byte overlay is COFF symbols,
  declared string table and 287 zero padding bytes. Memory URLs map to the
  VC runtime diagnostic and LLVM debug producer metadata. These explain
  particular features, not the private 17 antivirus flags or general safety.
- Remaining: private detector-rule attribution, UDP/suspended-process module
  attribution, exact-candidate NMS acceptance and Nexus/download acceptance.
  Next useful evidence needs a rule/offset or a module-resolved event trace
  for unchanged bytes; those are absent from these public reports. No further
  source correction is justified by generic labels alone. Contact remains
  an unsent last-resort contingency requiring explicit owner authorization.

### Further IAT/source and vendor-report handoff, 27 October 2026

- Exact game identity and native mapping ledger are unchanged. This pass reads
  owned frozen ASIs only: 0.10.3/source852c5c55/hash6474247c and
  0.10.4/source7fd4bc09/hash765cdbdf. No NMS executable, save or installed file
  was accessed; no compatibility or game-acceptance claim was added.
- New reusable tool: tools/research/audit_native_import_refs.py, SHA-256
  `93a6015492baf1b969c9e540e7637dde9acbcf6dc558743e14ebbbfdf86a6ce6`.
  Require --image, --expected-sha256, --output. CPython3.11.9 / pefile2024.8.26 /
  Capstone5.0.7. Hash validation precedes decoding; chained roots and exact COFF
  symbols identify RIP-relative IAT operands within physical exception ranges.
  Positive CreateThread/InitializeASI control and bad-hash refusal both pass.
- Both inputs' 2,384 ranges decode completely. Named imports and all selected
  IAT-reference records are identical. WriteProcessMemory maps to the owned
  menu writer using GetCurrentProcess; thread suspension/context APIs map to
  MinHook Freeze with current-process thread enumeration. Sleep references map
  to MinHook and CRT/gdtoa; libc++ owns condition-variable waits. The linked
  constructor's dynamic lookup is GetSystemTimePreciseAsFileTime. No new
  engineering defect or private detection rule is established by this pass.
- Public Kaspersky lookup finds the original exact ASI classified Malware,
  names Loader.sb/tvv, dynamic summary No data found. Candidate lookup returns
  No search results, not clearance. Exact tvv description redirects to a
  generic class page. Premium example tables are not sample evidence. No file
  upload, account registration, feedback or support message was sent.
- Sanitized receipts: NATIVE-0104-IMPORT-ATTRIBUTION-20261027.json, SHA-256
  `112cf488d0bdf033ffceb769b8a91c39e046ddda84ed80f03e80cf0c87a99e7d`.
  This is static reference coverage, not a complete call graph or runtime trace.
  Foreign-process injection, long-sleep execution and private rule attribution
  remain unproven. Exact-candidate game acceptance and Nexus download remain open.
- Next consequential step is the owner's last-resort review decision against
  the refreshed NEXUS-QUARANTINE-REVIEW-20261027.md. The public procedure
  requires moderator review of existing quarantine; concrete failing-check /
  affected-member data remains missing. No automatic support authorization.

### Owned-host runtime attribution handoff, 27 October 2026

- Game target/ledger unchanged: Cosmos 7.06 / Steam 25732212 / executable SHA-256
  13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
  No NMS process, executable or save was accessed; no native mapping changed.
- New internal method: exact frozen ASIs reproduced on Windows-2022, then
  owned Microsoft-built host baseline/load/inspect/initialize, plain versus
  instrumented. Tooling and hash-first CI/process gates are in
  NATIVE-0104-OWNED-TRACE.md and native-behavior-audit.yml. Frida 17.24.3 official
  wheel 61f5a53b...; no local installation or security preference change.
- Run 40579107862/controller fd532ac succeeded for both ASIs. Sources852c5c55 /
  7fd4bc09 and hashes 6474247c / 765cdbdf remain distinct. Each passed 16 extra
  plain initialization repetitions and four matched plain/instrumented modes,
  with actual OS exit 0, known host API controls and verified input/post hashes.
- Observed direct selected ASI API contribution: successful CreateThread from
  RVA 0x140E, flags 0, in initialize only; unsupported-host status 2 followed.
  Sleeps/memory writes in the selected direct-caller scope were host activity.
  This is not indirect-call/packet coverage, game acceptance or AV clearance.
- Preserve failed methods: run 40576805956 stopped at both baselines because a
  final-exit callback was absent; independent OS exit handles replace it.
  Run 40577586888 completed the candidate and three original captures; original
  full-stack initialize timed out. Later direct/no-stack captures and 16 plain
  repeats passed, but the prior timeout's cause remains unresolved.
- Durable sanitized evidence NATIVE-0104-OWNED-TRACE-EVIDENCE.json, SHA-256
  `4d15608c308c8b2d059f716d27765ec254d0cd51f829126bb890e29544e24b8f`.
  Do not equate unresolved private rules with exhausted internal analysis.
  Next bounded scope is active transitions on owned hook targets with a
  method that accounts for suspended instrumentation threads; UAL lifecycle
  and exact-candidate game acceptance remain NOT CHECKED. Support stays unsent.

### Microsoft build candidate handoff, 27 October 2026

- Autonomous antivirus-blocker work now includes a maintained Microsoft build
  path, not only interpretation of public sandbox reports. Source base is
  3ea3eff plus the two-call-site intrinsic/header and candidate CI/tooling diff.
- New package candidate is 0.10.5-native-test. Frozen original source852c5c55 /
  ASI6474247c and candidate source7fd4bc09 / ASI765cdbdf stay unchanged.
- Target stays Windows/Steam Cosmos 7.06 / build 25732212 / executable SHA-256
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

### Microsoft candidate and owned-lifecycle readback, 27 October 2026

- Target remains Windows/Steam Cosmos 7.06 / build 25732212 / executable SHA-256
  13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
  No game image, mapping, save, installed mod or owner-PC protection preference
  changed. Native caller roles use a level-zero intrinsic at the existing two
  callback sites; this adds no native role or new executable compatibility.
- Maintained Microsoft build candidate 0.10.5-native-test at source085838cc /
  run40585107104 passed two-directory DLL byte identity, full owned functional
  validation and a positively controlled Defender custom scan. ASI747,520 bytes,
  SHA-2568e6dd664c1fc0982a435b5932d0c9f006f1522926aa28b9556b7f2ce7dcb4695.
  All89 recorded source digests match Git blobs at that commit and all referenced
  validation receipts match. The first PDB matches DLL GUID/age; PDB bytes differ
  between builds, so full-build/PDB byte reproducibility is not established.
- Original/query-guard owned MinHook source fixtures passed in run40585107247:
  two owned-worker suspends/resumes and two temporary code-protection changes /
  restores each; no foreign handles/failures, original bytes restored. This
  explains operations in authored functions, not exact-ASI/game sandbox events.
- Exact candidate plus unchanged official UAL9.7.4 passed run40586261812:
  three no-plugin baselines and three automatically initialized unsupported-host
  cases, restored cwd, unchanged hashes, actual OS exit0. No manual InitializeASI
  call was used; normal process exit is distinct from arbitrary DLL unloading.
- Static helper audit_msvc_candidate_artifact.py checked all1,872 table entries,
  460 chain steps, bounds/sorting/no cycles, maximum depth5 and PDB identity.
  Fifteen pefile chained-function warnings remain recorded. Its initial V1-only
  attempt refused three V2 headers; only common V1/V2 structural fields were
  subsequently reviewed. Opcode/prologue/handler semantics remain NOT CHECKED.
- Preserve incomplete CI methods:40583926085 failed cross-volume artifact upload
  after build/functional/scan success;40584515831 original stopped before compile
  at a missing historical validator, while query-guard passed. Later success
  does not relabel these overall failed runs. No frozen player bytes changed.
- Sanitized evidence NATIVE-0105-EVIDENCE.json, SHA-256
  5292514fff69b8ba26b949528c0ef9ac125e630e7d8f61ae2477a8e11968f5ef.
  Detailed methods, exact artifacts and gates: NATIVE-0105-MSVC-CANDIDATE.md.
- Multivendor submission is NOT CHECKED: new hash lookup is Item not found;
  the exact 747,520-byte ASI and displayed VirusTotal sharing/terms form are
  prepared, awaiting explicit upload confirmation. The next detection gate is
  this exact-file comparison. Game acceptance, packaging and Nexus download
  acceptance remain separate open gates; private-rule attribution and a
  confirmed-false-positive classification are not established. Support unsent.

### Component readback and CRT-thread correction handoff, 28 October 2026

- Exact target remains Windows/Steam Cosmos 7.06 / build 25732212 / executable
  SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
  No new game image, profile/RVA, gameplay filter or language meaning changed.
- The approved 0.10.5 ASI 8e6dd664 completed at 27 October 21:43:19 UTC:8/71,
  all Yogi labels. Fresh unchanged 0.10.4 control 765cdbdf completed at 21:53:11:
  30/71. Both have 75 rows; 22 malicious-to-undetected changes, all eight remaining
  positives shared. Engine/definition identity and compiler-alone causality
  remain NOT ESTABLISHED; the repeat click produced no new analysis timestamp.
- All four preregistered components from run 40591032747/source 72e76b7 completed
  their specifically approved submissions. CRT 763c3dbd (494,080 B): 1/69 at 07:22:27;
  MinHook c7b00159 (507,904 B): 1/71 at 07:23:00; binding 8e6ce240 (532,480 B): 1/71 at 07:23:32;
  core fee7eebe (1,452,032 B): 1/71 at 07:24:14 UTC today. Cynet labels all four,
  including inert CRT. All eight Yogi-positive scanners return Undetected for
  each. These fixture negatives do not exclude bootstrap/host inspection,
  reachability or interactions. Core includes the generated catalog.
- Component evidence NATIVE-0105-COMPONENT-EVIDENCE-20261028.json, SHA-256
  3eff44fb61c662094137516c5d25a86a88b6220ed8304cee4acd589d30367c69. Full 0.10.5 evidence now SHA-256
  5292514fff69b8ba26b949528c0ef9ac125e630e7d8f61ae2477a8e11968f5ef; original morning scan snapshots remain historical.
  Initial 74-row parser refused an unlabeled failure; corrected visible parser
  asserts 75 distinct rows and preserves Google timeout/Zillya failure.
- FALSE LEAD: own binding filter already uses RW allocation then verified RX;
  no permanent RWX correction is needed there. Do not weaken working guards or
  edit dependency code solely to chase scanner scores.
- Implement the documented /MT CRT worker contract correction in separate
  0.10.6-native-test: _beginthreadex, unsigned __stdcall callback, unchanged
  once owner/pin/flags 0/closed handle/no-wait/guards; zero return stops status 3.
  No low-memory failure, player crash or Yogi cause is claimed reproduced.
- New owned control forces only that factory to return zero: eight concurrent
  calls plus one retry must stay inert/status 3 with one attempt. Two-directory
  DLL identity, normal functional bundle and positively controlled Defender
  scan remain pending exact CI readback. New ASI multivendor/game/Nexus gates
  are NOT CHECKED and do not inherit 0.10.5 results. No support message sent.
  Next bounded action: read actual 0.10.6 CI/fault receipts and freeze its exact
  bytes before any new upload request. No local native execution or AV change.

### CRT-thread candidate CI readback, 28 October 2026

- Candidate source 4439c909942a333146f001e197360a9aac669c08 passed
  Microsoft source audit 40653804071 and candidate run 40653804116. Exact
  0.10.6 ASI: 749,568 B, SHA-256
  30cc9542a2af3529fd4f3a2299d6331bddf51b61f8213a0a1a779b472789de3d.
  Both directories produce identical DLL bytes. Retained PDB 5f32c8d5 matches
  CodeView GUID/age; second PDB differs. All 91 recorded source input digests
  match source Git blobs; build, validation and individual report hashes match.
- Normal owned bundle passed all eight validator groups and six foreign-host
  runs. Forced CRT factory-zero control is status 3/inert with exactly one
  attempt for eight concurrent initializer calls plus a later retry. This
  proves the bounded refusal path, not a reproduced low-memory termination or
  private antivirus rule.
- The read-only custom Defender scan/EICAR control completed, but signature
  refresh FAILED and retained definitions 1.461.156.0 dated 22 October 18:40:20 UTC.
  No detection was recorded at 28 October 08:05:21 UTC; it is not a current-defs
  verdict. Stock CI realtime protection false, custom mode positive control
  passed, preferences/bytes unchanged. Keep this limit in upload/release notes.
- Selected static ASI/PDB check: 1,882 runtime entries, 460 chain steps, depth 5,
  sorted/bounded/no cycles; three V2 headers and 15 pefile warnings retained.
  Opcode/prologue/handler semantics remain NOT CHECKED. The initial receipt
  collector guessed a hyphenated report filename and refused missing input;
  corrected retained underscore filenames before completing comparisons.
- Evidence NATIVE-0106-EVIDENCE.json SHA-256
  c04c0f1bdfd905411b015fb862695bb86fb37441d8fed52d5daea29e4c0ffdaa.
  Prepare the same owned UAL lifecycle check against this exact ASI, while
  preserving the old 0.10.5 identity and historical results. No game process or
  new executable image, mapping/profile/gameplay filter, locale text or player
  data changed. Game identity stays Cosmos 7.06/build 25732212/SHA 13d5060d.
  Loader readback, exact new-file VT and NMS/Nexus gates remain NOT CHECKED.

### Exact CRT-thread loader completion and upload preparation, 28 October 2026

- UAL run 40655172010 / controller 732d37463eb44839400b467e18f4fc3d23ce8852
  passed against frozen ASI 30cc9542 / source 4439c90: three no-plugin baselines
  and three automatic-loader cases, status 2 for every ASI case, cwd restored,
  unchanged hashes and OS exits 0. The host did not call InitializeASI. This
  closes only the owned unsupported-host startup/normal process-exit gate.
- Current sanitized NATIVE-0106-EVIDENCE.json SHA-256
  c04c0f1bdfd905411b015fb862695bb86fb37441d8fed52d5daea29e4c0ffdaa; includes exact loader observation/toolchain receipts.
  It preserves the stale Defender-definition limit and all 15 parser warnings.
- New ASI hash lookup: Item not found. The real VT form displays Terms of
  Service, Privacy Notice and sample sharing; no new file selected/uploaded.
  One new reanalysis request for public 0.10.5 stopped at a visible unsolved
  CAPTCHA. No new control timestamp. Prepare one specific approval for new
  ASI 749,568 B / SHA 30cc9542/terms/sharing and that current CAPTCHA. Existing
  four-probe approval is completed and does not silently cover another file.
- New exact-file multivendor, NMS acceptance, packaging and Nexus availability
  remain NOT CHECKED. Support unsent; no local native execution, security
  preference change, new game image/profile/RVA or player text/meaning edit.
