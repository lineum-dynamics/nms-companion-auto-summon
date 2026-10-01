# Native game-update mapping guide

This guide records a repeatable way to investigate a new No Man's Sky executable
before changing Companion Auto Summon's native compatibility profile. It is a
research workflow, not permission to reuse candidate addresses. The current
Cosmos 7.05 case study is in [NATIVE-0705-COMPATIBILITY](NATIVE-0705-COMPATIBILITY.md).

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

When the scanner is made reusable, keep a signature catalogue with the symbol
role, source repository and pinned revision, applicable license, signature or
regeneration recipe, baseline RVA, matches by executable SHA-256, function
boundary result, caller/call-site evidence and known false matches. If a
third-party signature cannot be copied into this repository, pin its source and
provide a script that reads that source locally rather than silently
transcribing it. The scanner should produce a review report; it must never
rewrite or enable the native profile automatically.

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
