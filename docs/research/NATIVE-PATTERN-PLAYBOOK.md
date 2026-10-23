# Native pattern discovery playbook

This is the required procedure for every No Man's Sky executable update and
every change to a native dependency. `AGENTS.md` makes it a project rule. The
purpose is to make the next update a short, reproducible delta pass while
preserving both successful patterns and failed approaches. A scan result is
discovery evidence; it does not authorize a source address, profile, build,
injection or compatibility claim.

The build-specific compatibility report is the run ledger for the exact
executable. `NATIVE-UPDATE-MAP.md` is the reusable index of methods, mistakes
and corrections. Append findings and mark superseded conclusions; do not erase
the history that explains why a lead was accepted or rejected.

## Freeze and cache the inputs

Before scanning, record these inputs in the build-specific report:

1. Game release, platform/store, store build when available, executable file
   and product version, size, timestamp and SHA-256.
2. Git source base revision, current branch and whether the working tree is
   dirty. For a dirty tree, identify the relevant source diff; an address map
   without its source revision is not reusable.
3. Previous supported game identity and its exact compatibility report.
4. Every external pattern source's repository, pinned commit, data-file
   SHA-256 and applicable license. Record the exact local data path privately
   if it contains a username or other machine-specific location.
5. Python and analysis-library versions, repository tool/script revision, and
   exact command arguments.

Use this tuple as the cache key for a result:

```text
executable SHA-256 + source revision/diff + relevant baseline role-entry hash +
pattern-provider commit/data SHA-256 + tool versions + command arguments
```

Reuse a result only when the relevant tuple fields match. A changed executable
hash invalidates every match count and RVA for that binary, even if its patch
label appears unchanged. A changed source dependency invalidates that role's
mapping and its caller/layout dependents. A changed pattern-provider file or
analysis tool invalidates the affected scan. Stable identity, inventories,
commands and already established method relationships can be carried forward;
new binary evidence must be generated against the new hash.

## Identify the active implementation first

Follow the selected player's package through its build inputs and release
allowlist before deriving the dependency inventory. Include only the native
sources and generated outputs that feed that package; preserved legacy runtimes,
experiments and test fixtures are not current dependencies unless the package
actually includes them. Record the source revision, package version and game
profile separately. A version comment in an old source tree does not identify
the implementation being ported.

## Build the dependency inventory first

Derive the required role list from the current native source, not from a list
of familiar symbols. Include hooks/detours, direct calls, call-site filters,
 globals, object fields, RTTI/vtable assumptions, resource handles, callbacks,
and any event or player/network distinctions. Give each item a stable role
name independent of its RVA. For every data field, record the exact access
width and read/write direction, its base object and derivation, and the def-use
chain to the owning consumer. Link it to the source file and existing exact-build
evidence. This is the scan coverage denominator: a successful scan of many
popular signatures does not cover a dependency omitted from the source list.

For state and index fields, trace the exact-width setter and clear/transition
path as well as a consumer. Record the sentinel and the conditions that write
it; do not infer “active”, “pending” or “empty” from a source variable name or
one comparison. Confirm the owner/base through an independent pointer chain.
When `native_data_offset_xrefs.py` needs a detailed `.pdata` pass, repeat
`--access read --access write` in one invocation so both directions are
decoded together. Do not launch separate full-image passes for those filters.
If a result lands inside a chained unwind range, resolve the chain and query
the root for direct callers; zero direct calls to the fragment is not evidence
that the containing function has no callers.

For `native_vcall_xrefs.py --require-field`, the displacement only has to occur
somewhere in the same runtime-function range. It does not tie that field to
the indirect call's receiver. Follow the `RCX`/vptr base through the exact
callsite and reject teardown or sibling-object references as false leads.

Batch candidate lookups by pattern source, then spend detailed analysis only
on changed, unresolved or contradicted roles. Keep one row per required role
and explicit rows for useful false leads; do not restart already reproduced
work or treat a missing row as a negative result.

Normalize a field to every proven enclosing owner before concluding that no
setter was found. If `owner=app+offset`, batch its relative displacement and
the composed application displacement, including plausible overlapping wider
stores. In this build, owner byte `+0x1B937D` has no direct relative writer,
but its exact application-relative byte `+0x29A44D` has a setter and clearer.
Always confirm these candidates with the same owner and exact access width.

Simplify affine pointer expressions before naming their fields, and discard
register provenance after every redefinition. An index term may cancel:
the QAM matcher pointer is descriptor base `+4`, so operand `+0x4C` accesses
descriptor `+0x50`. A later roster-row redefinition similarly invalidates an
earlier resolver-result interpretation. Do not infer a source-item write from
the printed displacement without this algebra.

## Drive the pass from unresolved gates

After inventorying the source, keep a compact gate table for the exact build.
For each stable dependency role, record its evidence state, exact-build report
link, which requested behavior or release gate it blocks, and one bounded
next action with the result that action should produce. Use `MAPPED` only for
the established static contract; keep semantic, lifecycle and live proof as
separate gates where they are still missing. A dependency inventory is the
coverage denominator, not a claim that every row is equally important to the
first usable port.

Prioritize the shortest evidence-backed critical path to a complete requested
behavior. Work independent unresolved gates while a semantic or runtime
blocker is pending. Each search should answer one named question with a
bounded input scope and a clear stop condition. After an attempt yields no
new evidence, record the exact scope and failure mode, then change the
evidence source/anchor or move to another independent gate; do not rerun the
same search unchanged. Keep successes, false leads and corrected
interpretations in the ledger so later passes can skip them.

Reconcile completed findings with the current gate table in the same work
period. A stale NOT CHECKED row must not conceal a recorded static callsite;
conversely, its live verification must remain a separate gate. Count a status
correction separately from a new match. Determine optional-feature scope from
the selected packager and receipt requirements as well as compiler defaults:
a default-off trial is still required when the public packager requires it.

Documentation is the record of analysis, not a substitute for it. At the end
of a work period, state what evidence changed, what remains blocked or
`NOT CHECKED`, and the next bounded action. Continue that action when it is
authorized and feasible; stop only for a real blocker such as missing input,
access or required runtime evidence.

## Keep one exact-build mapping input

Use `native_mappings.json` for build-specific function/global RVAs, caller
returns and load-state policies. The generator selects an exact release,
Steam build and executable hash; C++ constants and build/validation/package
receipt expectations consume that same selection. Keep research entries
unapproved and retain the independent runtime activation refusal. A changed
profile label or a higher package number cannot select another binary's RVAs.
When a policy introduces new native fields, add stable dependency rows and
recount the inventory. Source preparation is separate from game verification.

## Retain missed polling windows as evidence limits

Read and print a baseline before reporting ready and requesting the action.
Keep capture duration, poll interval, sample/change counts, player confirmation
and immediate after-state separate. In the 23 October 7.06 run, a 45-second
capture observed a full local-load sequence; a teleport showed reason 11 only
after the window. A repeated 120-second poll saw no phase change. These are
bounded misses, not proof that the callback/state never ran. Do not request a
third trip with the same unchanged polling method; use a different event
anchor or evidence source when exact timing is required.

For menu reads, compare original and consumed copied row fields as aggregates
without printing keys/private pointers. Equal stock marker bytes and `-1`
binding ordinals corroborate a copy contract; they do not validate a custom
sentinel, rebuild retention, synchronization or an uninstalled mod.

## Verify filters at the callback boundary

Before relying on a new event predicate, capture it before/after the actual
native callback with its exact caller. Use bounded masks and Boolean presence
predicates; keep private identifiers and pointers out of output. In the 7.06
r2 trial, successful load return 0x4906C2 had matching receiver/source byte and
nonzero common key, while applied-state masks stopped at 0x0f. The later
LocalLoadState trace did not justify requiring that state at the earlier call.
The corrected exact-return/vtable/receiver policy passed 21 owned cases and
produced a visible pet in r3. The distinct known DeathState caller stays
excluded. Revalidate the return and owner chain for every executable hash.

Separate a failed predicate from an event that was never recorded. One r2
teleport produced no filtered record; the later successful r3 opposite route
had a fully accepted state mask. This does not prove the earlier failure was
caused by that predicate. Keep direction, clean no-pet baseline, foreground
play, accepted requests and visible outcome in the handoff.

## Prove resource extent through the registered factory

For an opaque resource, follow the loader's exact type key into its registered
factory field, then into allocation size, constructor and payload initializer.
Trace the registration argument's physical slot through the registrar to the
same field the loader invokes. A related constructor found elsewhere does not
establish the active allocation. Record the last required member's exact write
width/end and keep live class/lifetime evidence separate. The 7.06 type-7 chain
uses node `+0x38`, factory `0x1834A80`, allocation `0x400`, and a payload qword
ending at resource `+0x268`; it closes the static minimum extent.

Include overlapping wider initialization stores when searching byte fields.
Zeroing a dword at `+0x139` initializes `+0x13A`, but neither that nor a copier
proves its semantic name. Nearby `+0x13B` fallback behavior cannot name it.
Classify raw getter matches by an exact owner before using them: the unique
`+0x13A` getter in this pass belonged to `GPN::SearchContext`, not a resource.
An invalid COL/PE parser error is TOOL ERROR with no class conclusion. A vptr
observed at runtime must not inherit a common base class's name automatically.

Follow the observed method table into the same-object failure call before
repeating a byte-offset scan. In this pass the texture slot-13 path calls
`0x18DD960` with unchanged RCX; missing/empty data writes word `+0x139=0x0101`,
setting the sought `+0x13A` byte. Its manager consumer supplied the caller
anchor. Include wider stores at neighboring offsets and follow that anchor
across helpers; the useful producer was outside the initial bounded window.

Map the actual source predicate and state its intended policy. A deliberately
stricter cosmetic refusal can remain: source `<0` suppresses NaN even though
the reviewed native COMISS/JAE can continue on unordered input. Record the
truth-table difference instead of claiming equivalence or searching without
limit for a producer to prove the exceptional value impossible. This does not
resolve or relax event, local/network, completion or hook-ABI semantics.

The group-inspection tool's `--rva` is singular: repeated arguments select
only the last. Use separate invocations for different targets. A no-`.pdata`
result for a method-table target does not exclude a valid leaf or thunk.

`native_data_offset_xrefs.py --rva-min/--rva-max` includes only whole `.pdata`
ranges within the bounds and prints exclusions. Chained ranges outside remain
unexamined. Preserve signs in fast candidate parsing and verify a positive and
negative operand control after changes. Use `--offset=-0x13A` for a negative
hex argument. Name inventory `--include-structs` is opt-in; it adds `.?AU` while
retaining the default class-only search. A print limit is not a total count.

## Bring runtime evidence forward

This step is mandatory during the first work period of a new native port.
For each open behavior, state or field question, decide whether a safe bounded
observation in the exact game can distinguish the alternatives. After one
bounded static attempt adds no evidence to an observable question, prepare the
minimal reader and the specific player action before another broad scan. Do
not wait for every static mapping to finish. If the reader lacks a safe owner
or identity anchor, record that exact prerequisite and resolve it first.

If an incoming volatile argument might escape through the first callee, inspect
that callee's complete body before widening the target scan. In the 7.06
position helper the first callee `0x563060` overwrites R9 immediately; it cannot
consume the target's incoming fourth register value. Keep stack aliases and
event policy separate from this narrow register result.

Use existing launch/inspection authorization instead of asking for it again.
Preserve the required private verified backup and unsupported-build guard.
Start with external read-only access; game writes, hooks and deployment need
their own established prerequisites and authorization. Match the actual
opened process to the selected executable/hash and loaded-code anchors. A
Steam URI being accepted is not a process-start observation.

For each player-assisted observation:

1. State the question, competing interpretations, exact-build inputs, allowed
   reads, and what result would discriminate them.
2. Capture a baseline and record the actual menu/lifecycle/location state.
   Do not label an unconfirmed startup capture as a confirmed menu state.
3. Ask for one short action in ordinary player language, with a clear stopping
   point. If native UI control is unavailable, the player performs the action.
4. Capture and acknowledge the result before asking for the next action.
   Include every intervening action; ship entry is a state change, not noise.
5. Record sanitized values/counts, tool and command hashes, limitations, useful
   failures and the next discriminator in both dated update handoffs. Keep
   saves, account identity, raw addresses/dumps and private paths outside Git.

Continue independent work while waiting for a response. Matching repeated
reads are an observation, not an object-lifetime or synchronization proof.
An unchanged flag in successful cases does not establish its error meaning.
A stock-game menu does not verify custom rows or an uninstalled hook/archive.
When the menu closes, cached frontend rows can remain from the last open menu;
record that state instead of interpreting a source/copy mismatch as corruption.

The 23 October 7.06 pass uses
`tools/native_readonly_resource_snapshot.py --pid <verified-pid> --exe <verified-exe>`.
It requests only `VM_READ|QUERY_LIMITED_INFORMATION`, checks the actual process
path, exact on-disk hash, loaded header/size and three code prefixes, caps each
read/total work and refuses changed sampled headers. Its default first 10,000
entries are a bounded sample when the manager table is larger. It reports
resource aggregates, one public stock asset, and QAM/header comparisons; no
game code is invoked. Exact observations and the tool hashes are retained in
the build report. Private backup paths must be resolved in the real authorized
desktop context: sandbox `LOCALAPPDATA`/`TEMP` values may be redirected and may
differ across calls. A denied/incomplete snapshot is not a verified backup;
retain protected permissions and resolve the execution context.

## Search in bounded passes

### 1. Retained byte signatures

Use `tools/native_signature_matches.py` with the pinned external data file and
the exact source symbol names. Batch names with repeated `--name` arguments.
The helper searches executable PE sections and reports match count, RVA,
section and containing `.pdata` range. A unique match is only a candidate.
Confirm whether it is a function entry and whether the match begins at a
decoded instruction boundary. A match inside a function, a chained unwind
range or an unrelated body is not a function relocation.

Keep third-party signatures in their licensed source. Record provider commit,
data-file hash and symbol key instead of copying bytes into this repository
unless the license clearly permits it. Never regenerate or edit the old
profile as a side effect of scanning.

### 2. Function boundaries and direct callers

For every candidate, resolve its `.pdata` entry and recursively follow
`UNW_FLAG_CHAININFO` to the true parent before naming a function. Decode x64
references within runtime-function ranges and verify instruction boundaries.
Use `tools/native_call_xrefs.py` for bounded direct-call searches; repeat
`--target-rva` to batch up to 64 targets into one decode of the runtime-function
inventory. Report that its counts cover decoded direct calls only. Indirect
calls, jump tables, callbacks and other reference forms need separate checks.
The helper now streams decoded instructions and retains only the requested
callsite context, rather than materializing every instruction in a large
function. It reports progress every 5 MiB of runtime-function bytes. This
keeps the 7.06 full `.pdata` pass bounded in memory; a known-target scan should
reproduce earlier caller counts before relying on a changed helper.

Use `tools/native_rip_xrefs.py --target-rva <rva>` for direct RIP-relative
memory references to code or data addresses. Batch related RTTI/COL/vftable
targets into one exact-hash pass. The helper counts every decoded reference,
retains only `--limit-per-target` examples (default 50), and reports progress
every 5 MiB. A zero result covers only RIP-relative memory operands; it does
not find direct `E8` calls, absolute function pointers, indirect dispatch,
relocations constructed at runtime, hashes or dynamic addresses. Keep target
RVA distinct from an object-member displacement such as `+0x941C70`.

Use `tools/native_pdata_function_group.py --exe <exact-exe> --rva <candidate>`
to report the containing entry, resolved root and every chained range in that
group. It reads the full PE exception directory, validates parent tuples,
detects missing parents/cycles, and prints the executable SHA-256. It does not
decode code or infer semantics; use `native_function_disasm.py` on the exact
bounded ranges afterward. This replaces one-off unwind parsers in scratch
commands, which are easy to get wrong.

For shared object offsets such as menu vector counts, batch
`--offset <displacement>` values with `tools/native_data_offset_xrefs.py`.
It decodes `.pdata` ranges once and caps printed matches. A displacement match
may be a read, write or unrelated object field; inspect its base register,
function callers and exact menu context before promoting it to a field map.
For fast shortlisting, add `--fast-candidates`. It uses `disasm_lite` over the
same verified `.pdata` ranges and reports every matching memory operand, but
its access hints are heuristic and it cannot apply the exact `--access` filter.
Use it only to identify bounded function candidates; confirm writes with the
detailed scanner or a full instruction decode before assigning a field role.

A broad scan can take long enough to consume a work period without producing
interim output. For an already localized global or field, use bounded function
windows or add a range filter before repeating a whole-.pdata offset scan.
If an interrupted scan prints no final totals, record its completed-byte and
match counts as NOT CHECKED; never infer zero. For a new executable hash, still
cover every required dependency, but batch offsets and preserve the full-scan
gate rather than repeating overlapping scans one displacement at a time.

For vector producers with a known record size, use
`tools/native_vector_stride_candidates.py --stride <size> --count-offset 4`
as a broad shortlist. It reports functions that contain both a matching
`imul` and a write to a count field at that displacement. Same-function
co-occurrence is weak evidence: stack temporaries, constructor resets,
render-only vectors and unrelated pair arrays can all match. Resolve the
function's `.pdata` parent, base object, direct callers, item initialization,
destination header and actual count growth before assigning a role. The
Cosmos 7.06 case study below found 30 candidates, including multiple false
leads, before caller and RTTI checks isolated the QAM producer.

`tools/native_rtti_vtable_probe.py --target-rva <candidate>` reverse-maps one
executable RVA to validated RTTI-backed vtable slots. This is useful for
rejecting a structural match that belongs to a different derived class. A
slot match still needs method-body and caller evidence; it does not establish
the slot's semantic contract or safe hook timing.

Start a disassembly window at a confirmed `.pdata` range start or another
verified instruction boundary. `native_function_disasm.py` accepts any RVA and
does not validate the first byte as an instruction boundary; starting midway
through an instruction can print plausible-looking garbage and create a false
lead. If the boundary is unknown, start at the containing range start and
filter the bounded output around the target instruction.

Compare caller setup and following code with the supported build: `RCX`,
`RDX`, `R8`, `R9`, stack arguments, XMM inputs, return register use, branch
conditions, object/member identity and side effects. For a return-site hook,
map the exact call instruction and return address plus the menu/state carried
through the call. A matching callee does not relocate a call-site hook.

### 3. Independent structural and semantic anchors

Use the anchor that fits the role and keep its limits attached to the result:

- RTTI/vtable: validate the complete TypeDescriptor, Complete Object Locator,
  class hierarchy, table and executable slot targets. For x64 MSVC, the
  TypeDescriptor name begins 16 bytes after the descriptor start. Check each
  slot against callers and method behavior; a type name or table alone does
  not prove a slot's role.
- Strings/resources: `tools/native_string_xrefs.py` finds direct RIP-relative
  references to selected strings. A zero result rules out only that reference
  form; it does not rule out indirect, hashed, dynamically built or other
  references.
- Data layout: verify each required global/field through more than one
  relevant use where practical. Record the producer, consumer, stride and
  object identity. Nearby offsets and one matching read are not enough.
- Call patterns: compare full argument and return behavior at all relevant
  direct callers. A generic helper with many unrelated callers is normally an
  anchor, not a safe hook target.
- Other byte/semantic patterns: record how the pattern was derived, its
  instruction context, masking assumptions and architecture/compiler scope.
  Similarity scoring can rank work; it cannot replace boundary, caller and
  semantic checks.

For a critical hook, require at least two independent anchors where available
(for example, a unique function signature plus corresponding callers, or RTTI
slot identity plus body/argument evidence). Record contradictions explicitly;
do not choose the interpretation that merely preserves the old address.

## Interpret outcomes consistently

Record the raw match outcome separately from the role-level evidence status:

| Search outcome | Required disposition |
| --- | --- |
| Zero matches | `NO MATCH` for this exact pattern and exact executable hash. Try a different independent anchor or mark the role `UNMAPPED`; do not claim the function is absent. |
| One match | `SINGLE CANDIDATE`. Check function entry/boundary, unwind parent, callers, ABI, layout and independent role evidence before promotion. |
| Multiple matches | `AMBIGUOUS`. List every match and boundary; eliminate only with recorded independent evidence. Never choose the nearest RVA or first hit. |
| Match in an interior/chained range | `INTERIOR` until the parent and actual instruction/function role are resolved. Old-RVA containment alone is not a match. |
| Candidate contradicted by body/callers | `FALSE LEAD` with the exact reason and the narrower search that should follow. Preserve the rejected address as a negative pattern. |
| Tool, source or evidence unavailable | `NOT CHECKED` with the blocker. Do not record it as zero matches. |
| Scan interrupted or output unavailable | `NOT CHECKED` with elapsed scope and stop reason. Do not treat a partial or cancelled full-image scan as a negative result; reuse verified evidence or batch the next pass. |
| Invocation/filter or decode boundary error | `TOOL ERROR`; preserve what failed and rerun from a verified input/boundary. Do not interpret the output as a binary result. |

Use the evidence labels already defined in `NATIVE-UPDATE-MAP.md` for the
overall role. Pattern count does not promote a role. Missing semantics or live
evidence keeps the dependent feature disabled.

## Per-role ledger entry

Add or update a concise entry in the exact-build report for every required
dependency and every material false lead. Include:

```text
Role and source location:
Pattern kind and purpose:
Baseline game/build/executable SHA-256 and baseline RVA/behavior:
Pattern provider, pinned revision, data SHA-256 and license:
Tool/script versions and exact command:
Target executable SHA-256:
Raw result: 0 / 1 / multiple / not checked; all match RVAs:
.pdata range, entry/interior result and resolved unwind parent:
Direct callers/call sites and relevant register/stack/XMM/return behavior:
Independent anchors and object/layout facts:
False matches, contradictions, omitted/negative search scope:
Role-level evidence label and reason:
Next bounded action and expected evidence:
```

Do not paste bulk disassembly, raw scanner output, game binaries, save data or
private runtime material into Git. Summarize the observation in original
words and retain a reproducible command. If a prior interpretation was wrong,
write what was corrected, why, and which earlier conclusion is superseded.

## Proven lessons from the Cosmos 7.06 pass

The following examples are retained to shorten the next pass:

| Pattern/result | What worked or failed | Reuse rule |
| --- | --- | --- |
| Pinned NMS.py signatures against build 25732212 | Several unique function-entry candidates quickly relocated named methods; the missing `LoadFromData` signature did not prevent caller-anchored discovery of a load-role candidate. | Start with pinned symbol keys for every source dependency, then use caller evidence for missing signatures. A name match and a missing match both need bounded interpretation. |
| Pinned menu-symbol coverage | The pinned data file has only `cGcQuickActionMenu::TriggerAction` and `cGcQuickMenu::cGcQuickMenu` among names containing `menu` or `quick`; it has no named builder/item-constructor/append patterns. The quick-menu constructor is an ABI false lead for the mod's four-argument item constructor. | Check provider coverage before searching. A missing provider pattern is a dataset gap; continue with caller/layout anchors and do not claim that the game function is absent. |
| Old RVA containment | Many 7.05 addresses fell inside 7.06 `.pdata` ranges but were not entries or matching roles. `0x572410` was a constructor, and several menu RVAs were interiors of unrelated/chained bodies. | Check entry equality and chained parents; never transfer an address because it is contained by a range. |
| QAM RTTI name at `0x515A458` | Subtracting 12 instead of the x64 MSVC 16-byte TypeDescriptor header produced a false negative. Validating the full chain found COL `0x4B66FE0` and vftable `0x4A504E0`. | Derive descriptor boundaries from the format and validate descriptor, COL and hierarchy before recording either a positive or negative result. |
| Old `MenuAppend` lead | `0x153C840` mutates an existing item's fields; nearby `0x153C7A0` selects a context index and returns a pointer into the supplied menu object. Neither appends. | Confirm vector count/data/capacity changes and caller argument roles before labeling a helper as append. |
| Generic vector helper `0x2BF9A00` | It has 791 direct callers. Its QAM caller passes a `0xE0` stride, but the resolved body copies/resizes a vector and assigns its requested count; the QAM destination is render scratch, not the menu's source vector. | Broadly reused helpers are data-flow anchors, not presumed safe hook points. Confirm destination, count mutation and full chained body; matching the item stride alone does not establish append behavior. |
| QAM update/state transition | Vtable slot 0 at `0x15286C0` and method `0x1530D40` narrowed the path; the latter resets state but does not create/append items. | Use RTTI to identify the class, then trace each slot and its data flow. Do not infer a builder from an update name or a call near the old RVA. |
| Nested QAM Update receiver correction, 22 October 2026 | An RCX-seeded scan showed slot zero at `0x15404FF` in root `0x1540430`, but its abstract receiver remained `arg RCX`; the full body materializes `0xDC0` in `EAX`, then forms `RSI=RDI+RAX` and dispatches on `RSI`. In selector-1, constructor/RTTI evidence identifies the QAM at `parent+0xDC0`, with slot 0 targeting `0x15286C0`. The callee consumes `R8` as a record pointer. After the call, the caller reloads `parent+0` and copies it to `parent+4`, which the separate source-vector consumer indexes; the alias is conditional on the callee leaving `parent+0` unchanged and on consumer ordering. | Do not classify a nested virtual call from the root's incoming `RCX` or a short callsite window. Propagate register constants and scaled-index arithmetic through the complete chained body, resolve the active selector, then verify the exact receiver against its constructor/vtable. When index fields differ, trace the post-call copy and check callee mutation/order before equating their owners. Keep the `R8` data owner and custom-row rendering as separate gates. |
| Constructor end pointer mistaken for another initialized element, 22 October 2026 | Constructor `0x2CA290` starts a decrement loop at 2 and initializes records at `parent+0x10` and `parent+0x6E0`. The pointer after the final increment is `parent+0xDB0`; no third iteration runs. QAM is a separate member at `parent+0xDC0`. | Derive loop count from counter and branch, and keep the final advanced pointer separate from initialized element addresses. Reject the prior index-2/QAM-overlap hypothesis; the constructor does not initialize the two index fields. |
| Selected QAM rows copied into a frontend record, 22 October 2026 | Update `0x15286C0` selects `menu+0xA058+depth*0x10`, passes its row pointer/count and `0xE0` stride to `0x2BF9A00` with destination `incoming R8+0x610`, then stores the returned pointer at destination `+8`. The 12 October helper proof already described this copy; the later owner/resource consumer finally connects it to the icon field. | Search both endpoint roles, helper RVAs and vector-header bases in the existing exact-build ledger before scanning. The destination receives a copy; do not require or claim pointer aliasing. Link the joined evidence under the stable dependency role and retire obsolete caller-discovery work. Keep index handoff, ordering and live custom-row behavior explicit. |
| Group-scanner arithmetic audit, 22 October 2026 | Separate fact sets, one application of LEA displacement, conservative treatment of scaled/negative expressions and memory-first XCHG invalidation preserve the manually verified `0x15404FF` candidate. | Reproduce the exact root after changing a helper. The current width/implicit-clobber model and partial-decode accounting remain incomplete, so zero candidates or byte totals cannot establish exhaustive absence. |
| Conditional QAM update helper | `0x15288B3` calls `0x153B5B0` with `RCX=menu`, `RDX=render` when `menu+0xA170 != -1`; it reconciles five `0xE0`-stride records and invokes label/navigation paths. | Keep it as a builder/update candidate, not an approved replacement, until the destination is shown to be the source QAM vector and an append/count change plus lifecycle are proven. |
| Menu context resolver and action-state handler | `0x153C7A0` selects a context index and returns a pointer into the supplied menu; `0x153BE60` scans `0xE0` items and clears menu state. An earlier owner/local-player interpretation was corrected. | Decode the complete helper and callers before inferring ownership from a pointer; preserve the correction and do not use either as an append hook. |
| Vector-depth repair helper | The call target `0x151ACD0` checks vector count and selected-index fields, clamps selections and backs out through empty menu depths. It has no `.pdata` entry and makes no source-vector append. | A direct call target may be a valid bounded entry without unwind metadata; decode from the call target and stop at a confirmed return/padding boundary. Do not label count reads as vector mutation. |
| Context item comparison and reset | `0x151AB50` compares `0xE0`-stride item fields and strings, returning Boolean; `0x151ADD0` initializes six fixed `0xE0` records and their string fields. | Keep equality, bulk context initialization, one-item construction and vector append as separate roles. Matching item size or string constructor calls does not make a bulk initializer a safe single-item constructor. |
| Render-item context association | A QAM update loop matches existing `0xE0` renderer items to menu context records, then stores a context index in item field `+0xD8`. | A write into an item field is not a vector append. Verify header count/data/capacity changes separately before calling a path an insertion point. |
| Adjacent function false lead | The adjacent chained `0x151AE90` body computes a minimum vector distance and has one direct caller at `0x151B18C`, outside the QAM update path. | Function adjacency is not a dependency relationship; use exact caller xrefs and body semantics before carrying a candidate forward. |
| Decorated-name inventory | The corrected bounded `.?AV...NUL` scan found four names containing `quick`; only `cGcQuickActionMenu` and `cGcQuickMenuState` are the matching QAM classes. A first PowerShell/Python regex was over-escaped and falsely printed zero. | Use the repository helper, verify a known anchor, deduplicate, cap output, and record the exact query. An escaped-regex zero is a tool error, not a binary negative; no item class name does not prove no item function exists. |
| QAM slot-role probes | Slots 8 and 10 return booleans after checking input IDs/timer state; slot 9 reads the selected item and calls string-like helpers; slot 15 dispatches on `EDX==4`. Their full roles remain partial or unresolved. | Resolve complete chained `.pdata` ranges and callers before naming a slot. A filtered reference view is a lead, not full semantic proof; none of these observations identifies an item builder or append point. |
| Unbounded decorated-type-name dump | An exploratory raw binary-name listing exceeded the output budget and was discarded without a usable inventory. | Bound output at the query: filter exact type-name families, deduplicate, cap printed rows, and report the total separately. Output truncation is `TOOL ERROR`, never a zero-match result. |
| Repeated full-image caller scan | A redundant one-target direct-call scan for the already-mapped label method was stopped after more than 60 seconds without output; it would decode about 52 million `.pdata` bytes again. | Check the existing caller ledger first. Do not repeat expensive full-image scans for known targets; batch genuinely new targets into one pass or mark the interrupted scan `NOT CHECKED`. |
| Virtual address versus RVA | Capstone prints disassembly instruction addresses as RVAs but direct call operands as VAs; an initial filter searched for the target RVA and returned no matching lines. A helper was also first queried with a call operand VA. | Read the reported image base. Convert a call target VA to an RVA before passing it to a PE helper; filter disassembly output using the displayed operand form. Treat a zero caused by mixed address spaces as `TOOL ERROR`. |
| Multi-target direct-call scan | Repeating the old scanner caused a redundant pass. The streaming batched version scanned 52,110,272 `.pdata` bytes, skipped no ranges, and reproduced caller counts for four targets in about 22 seconds. | Use one verified executable hash and repeated `--target-rva` options for new candidates; preserve per-target counts and call sites. Recheck speed if the helper changes. |
| Direct-call scanner memory | Materializing every decoded instruction for a function used more than 800 MiB before the result was available. A streaming `disasm_lite` pass with a bounded rolling call context reproduced known counts in about 22 seconds and printed progress. | Keep the bounded-context implementation; verify one known multi-caller target when changing the scanner. Record interrupted scans as `NOT CHECKED`, never zero. |
| Direct RIP-relative RTTI references | Four batched COL/vftable targets found the exact constructors that installed `Session` and `PlayfabSession` vtables. An unbounded query for a common global pointer produced output too large for the tool response. | Cap printed examples while preserving total counts; target exact vtable/COL RVAs first. Do not use truncated global-reference output. |
| Fast `+0xA088` candidate pass | `--fast-candidates` found 64 memory operands, while the separate detailed write ledger had 29 writes. The fast set included stack locals, constructor resets, reads, `cmp` operands and address-only `lea` operations. | Treat its access labels as hints and confirm every selected candidate with detailed disassembly. It shortlists code; it does not change the exact-write count. |
| `0x153BE60` selection restore | Chained body `0x153BE80` reads `menu+0xA164`, searches `0xE0` entries and restores selection by ID. Its only direct caller is QAM update `0x15286C0`, passing menu and render state; it does not take the old `(depth_field, depth, index)` contract. | Resolve the true `.pdata` root before checking callers. Reject the restore helper as `MenuSelect` and do not repeat the interior-target query. |
| Direct string references | The 7.06 scan found no direct RIP-relative reference to selected RTTI/type strings. | Keep the result scoped to direct RIP-relative references and continue with RTTI/data/caller anchors. |
| Menu count displacement scan | A write-filtered `.pdata` scan found 14/11/13 operands for `+0xA05C/+0xA06C/+0xA07C`. The tempting `0x2CA7BB` write is a zero-reset in `cGcQuickMenu::cGcQuickMenu`; a broader first view was truncated and discarded. | Use the memory-offset helper with an access filter and a cap above the observed count. Verify the base object and caller before interpreting a repeated displacement; constructor/reset writes cannot stand in for a producer. |
| Count-field readers | A read-filtered pass found 55/8/8 uses of those same offsets across the QAM update, label, selection/trigger and reset paths. | Reads corroborate count/selection roles but cannot identify an append point. Trace the adjacent data/capacity fields and helper arguments back to the same source object before approving a vector producer. |
| QAM conditional update tail | `0x153B5B0` copies or initializes five `0xE0` context-cache records from selected menu items; its count writes clear menu state. It does not append to a source vector. | Trace the destination base as well as item stride. Cache copies and fixed-record initialization can look like a builder; require a source-header count increase and caller contract. Do not repeat this rejected candidate. |
| QAM selection setter and adjacent append wrapper | The old 7.05 selection RVA `0x1518EF0` is invalid in 7.06. Leaf `0x151ADB0` has no `.pdata` entry but checks depth/index bounds and writes the same selected-index field; three callers from QAM `TriggerAction` pass `(menu+0xA050, depth, index)`. Neighbor `0x151AD40` instead takes an item pointer and appends to a vector. | Inspect small leaf helpers adjacent to verified menu routines; use exact direct-call register context to distinguish similar signatures. No `.pdata` entry does not mean no function. Cap high-fanout caller output with `--limit-per-target`; preserve total counts. |
| Indexed-store scan and register parser | The detailed full-image scan was slow and stopped before a result. The faster destination heuristic found one exact `r15 + rcx*4 + 0x38` store at `0x152E5D2`, but an initial parser draft treated any occurrence of `rcx` as the base and falsely conflated the base/index roles. | Prefer the `disasm_lite` candidate pass with separately parsed base, index, scale and displacement. Confirm candidates in root-aligned detailed disassembly and direct callers; record the parser-bug output as discarded, not evidence. |
| Supported patch scope | Cosmos 7.05 already included the Cosmos 7.0 update; current 7.06 analysis therefore compares the exact 7.05 baseline with 7.06. | Read the previous supported build identity before interpreting release notes. Attribute only to the adjacent patch unless binary evidence establishes a broader cause. |
| High-fanout call-context output | The append wrapper `0x151AD40` has 57 direct callers; a context-12 report exceeded the output budget even though the total count was available. | Use `native_call_xrefs.py --limit-per-target` to preserve the count and cap examples; request a focused target/context when the full call set is necessary. |
| QAM slot-9 output interpretation | Full chained disassembly shows the original `R8` pointer is cleared for one byte at entry but never used again as an output pointer; only the `RDX` 256-byte string is written and terminated. | Follow the original argument's dataflow across the complete chained function before naming multiple outputs. A buffer reset alone does not prove a populated output or its meaning; preserve and forward unexplained arguments. |
| Virtual-call arguments across helpers | Two apparent slot-9 callers set a stack `RDX` buffer and an `R8` pointer, then call helper `0x540660` before `[vptr+0x48]`. Its three-range unwind group shows it saves the input `R8` elsewhere and overwrites the volatile register without restoring it. | Check every call between argument setup and the virtual dispatch. Screen full context-12 output only as a candidate filter; a text-context zero is bounded to the displayed window and call form. |
| QAM vector item icon value | `+0xA060` yielded 32 heuristic operands, including stack locals. Root-aligned QAM code uses a `0xE0` stride, reads the action from item `+4`, and copies full records; the first dword set from `menu+0xA104` was not seen in the inspected QAM consumer as a texture/draw read. | Separate value initialization, append, cache copying and rendering. Confirm object base and vector source before interpreting repeated offsets; continue to a renderer/resource consumer before naming the first dword. |
| Generic context-cache offset scan | The `+0x2D0` fast shortlist found 1,852 operands and printed only the first 100, mostly stack locals. `--fast-candidates` cannot be combined with `--access read`; removing the incompatible filter still left the result too broad. | Record the invocation error, then stop widening a generic displacement query. Anchor the cache through its exact returning helper and caller data flow; a truncated shortlist is `NOT CHECKED`, not a no-match. |
| QAM cache plus virtual-slot filter | `[vptr+0x48]` plus same-function `+0x2D0` returned 13 ranges / 21 calls; the only candidate in the `0x15xxxxxx` area matched `[rsp+0x2D0] = R15`, a stack save, not the QAM cache. RTTI independently confirms slot 9 at `0x153C0C0` in `cGcQuickActionMenu` vftable `0x4A504E0`. | A same-function field filter does not track the object's base. Verify the matching operand in the `.pdata` root and track the exact pointer from `0x153C7A0`; do not infer a consumer or zero callers from a false-positive shortlist. |
| QAM slot-9 `+0xDC0` receiver audit, 18 October 2026 | Eight calls in seven `.pdata` ranges matched `[vptr+0x48]` plus any `+0xDC0` operand. None demonstrated the verified QAM `parent+0xDC0` object as the call receiver; some operands were visibly based on another object or read after dispatch, while others lacked alias proof. The stack-buffer candidate had a helper call between setting `RDX` and dispatch, and set `R8` after the call. | Treat same-range displacement matching as a candidate filter only. Compare the call's `RCX` expression to a proven QAM subobject, then follow `RDX`/`R8` through every call boundary; no displacement-only result proves or rules out a caller. |
| Official release-log check | The official release log was rechecked on 16 October 2026 and still listed Cosmos 7.06 above 7.05, with no 7.07 entry. | Recheck the official release log before each update pass; retain the exact game release/build/hash separately from the mod package version. |
| QAM context-cache input path | An exact-hash direct-E8 scan found 14 `0x153C7A0` calls: 11 in QAM update, one in its context-snapshot helper and two in a caller that passes the adjusted receiver to QAM `TriggerAction`. The dispatched cached item is read at `+4`; the inspected `TriggerAction` body does not read the first dword. | Track the returned pointer and complete caller path before naming a cache. Correct a stale caller count when exact callsite enumeration disproves it; keep this action/state cache distinct from a renderer/resource consumer. |
| Release-log recheck on 18 October 2026 | Hello Games still lists Cosmos 7.06 first and Cosmos 7.05 second; no 7.07 entry was present. The installed 7.06 executable hash is unchanged. | Recheck both the official release list and local executable identity after an interruption; reuse an existing dependency ledger only when the exact hash still matches. |
| Slot-9 `+0xDC0` caller shortlist | Eight `[vptr+0x48]` calls in seven ranges shared `+0xDC0`. Candidate `0x155A45F` set stack `RDX` before an intervening call, set `R8` after dispatch, used another base for `+0xDC0`, and its root had no validated RTTI vtable slot. | Same-function offsets do not identify the call receiver. Prove QAM object provenance and track volatile output registers across every call before naming a caller. Keep the other seven displayed contexts `NOT CHECKED` unless individually resolved. |

These facts are static and scoped to executable SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
They are not mappings for another game build.

## End-of-pass rule

Before ending any compatibility work period, update both this project's
reusable `NATIVE-UPDATE-MAP.md` and the report for the exact executable. The
exact-build report must list the dependency coverage, new successful patterns,
zero/multiple results that matter, false leads, corrections, `NOT CHECKED`
items and one bounded next action. The reusable map must capture any method,
tool behavior or failure that will shorten another update. If no mapping is
safe, record that conclusion and keep the existing exact-build guard closed.


## Additional 16 October 2026 lesson: repeated offsets and nested resources

The `+0xA104` fast scan found 18 operands, but the same displacement belonged to both the QAM object and other objects. In the QAM constructor, `RCX` is the top-level menu; in another resource constructor, the sole caller passes `parent+0xDC0`. The QAM builder independently reads its own `+0xA104` and passes the value as the native item icon. The exact `cGcRealityManager::LoadTexture` candidate also moved from old RVA `0xEC6850` to entry `0xEC8700`; the new body matches a path pointer at offset 0 and a handle at `+0x10`, with 294 direct callers.

Reuse rule: annotate each offset with its actual base object and caller adjustment. A matching displacement in a nested constructor is not corroboration for the outer object's field or a lifecycle callback. For function-pointer loaders, keep the signature/body/ABI result separate from the hook that determines when it is safe to load. Zero direct caller or RTTI counts do not rule out indirect calls.

## Additional 18 October 2026 lesson: nested QAM owner offsets

A constructor caller may expose a nested object relative to an intermediate member, while a teardown caller exposes it relative to the enclosing owner. In this build the QAM is at enclosing +0x115D50, and its nested child is at QAM +0xDC0, so the composed owner-relative address is +0x116B10. The apparent mismatch that led to an earlier false rejection came from comparing offsets with different bases.

Reuse rule: write down every object base and compose member offsets to a common root before comparing constructor, method and cleanup paths. Then inspect the virtual call's actual RCX; even a correct owner-relative displacement can coexist in the same range with unrelated virtual receivers. A teardown call remains teardown evidence, not a resource-ready event. Keep zero results bounded to the exact slot form and same-range displacement filter.


## Additional 18 October 2026 lesson: selector fields and full owner arithmetic

When a nested object is selected by a global mode/index field, combine that selector displacement with explicit base-offset hits and inspect every virtual receiver in matching ranges. In this build the QAM child is global+0x849430 and its selector is at global+0x849424; the selector-anchored slot-0x48 filter still matched two calls on a different global frontend object. A zero or nonzero same-range displacement result is only a shortlist.

Reuse rule: calculate composite offsets independently, verify them against a second constructor or caller path, and record/discard any arithmetic-error query. Track the virtual call's RCX separately from the selector or sibling object. A nearby QAM input-dispatch call does not make a following frontend-manager virtual call a QAM call.


## Additional 18 October 2026 lesson: chained unwind groups

A field hit can occur in one chained runtime-function range while a related call appears in another range under the same unwind root. A filter that requires both patterns in one range can miss that relationship. Decode the full parent group and follow the selected pointer across every branch before classifying a candidate.

Reuse rule: inspect every chained range for the root, record the actual receiver and slot at each indirect call, and distinguish a complete parent-group review from a same-range filter. A full-group bounded negative still does not rule out callers elsewhere.


## Additional 18 October 2026 lesson: resource-hook recovery from handle dataflow

The old 7.05 resource hook RVA 0x1524330 fell inside an unrelated four-argument 7.06 helper. A first review also rejected 0x1526240 because its large body looked like member and localized-string initialization. Focused exact-root inspection corrected both interpretations: 0x1526240 is called with the nested QAM object, invokes the resource-manager loader with a concrete path and output handle, then replaces the handle at QAM+0xA104. The direct string reference is `TEXTURES/UI/FRONTEND/ICONS/QUICKMENU/SUMMONPET.DDS`.

Reuse rule: prove a resource initializer by following caller object, loader arguments, exact resource path, output-handle temporary, and final owner field in one bounded call path. Do not infer the hook from the old RVA, a matching offset, or a loader signature. A function's post-load return is static ordering evidence; runtime thread and lifecycle safety still need separate verification.

Efficiency rule: use `--fast-candidates` displacement scans to identify a short list, then inspect only the corresponding complete `.pdata` roots and decode relevant RIP-relative strings. The candidate scan's read/write labels are heuristic, so verify each relevant instruction with detailed root-aligned disassembly. If a slow whole-image detail scan is interrupted, record it as `NOT CHECKED`; never turn missing output into a zero result. When reading PE data on PowerShell, pass the path through a here-string or argument rather than embedding a Windows path in a Python string literal, which can produce an escaping error unrelated to the binary.


## Additional 18 October 2026 lesson: return-site detour register proof

The 7.06 `GetButton` return at `0x15292F5` is followed by QAM reads through `RDI` for depth, selected index, vector header and the `0xE0`-byte selected item. This matches the object register and layout assumed by the generated return-address filter; a nearby fixed-button call return at `0x15292AB` does not have that selected-item path.

Reuse rule: when relocating a return-address detour, inspect the exact post-call branch and verify the caller's object register against every base register the generated code reads. Keep static register/layout compatibility separate from live input effect, thread and lifecycle safety. Do not change a shared source constant while another approved build still depends on its current site; choose return sites through the exact build profile.


## Additional 18 October 2026 lesson: RTTI slot semantics versus caller proof

For the exact Cosmos 7.06 hash, RTTI ties QAM vtable slot `+0x48` to method
`0x153C0C0`. Decoding all chained ranges shows that it reads the selected
`0xE0`-byte item and formats localized text through the primary `RDX` output
buffer, bounded to 256 bytes. It clears one byte through original `R8` at
entry, then reuses that register; the auxiliary argument's semantic contract
is still unknown. This is enough to promote the method role from “likely
label” to statically corroborated label output.

Reuse rule: RTTI slot identity plus complete method dataflow may establish what
a virtual method does even when a bounded caller scan finds no call site. Do
not let that promote the receiver/caller, downstream consumer, buffer owner,
or auxiliary argument. State the bounded negative precisely and keep each
unresolved contract separate. In particular, don't transplant an old hook's
argument count or output capacity based on its name alone.


## Additional 18 October 2026 lesson: physical ABI is not semantic naming

The 7.06 load-role candidate `0x573500` has four direct callers with the same
six physical argument positions as the existing hook. Its fifth argument is
tested in the callee, while callsites vary that stack byte and one passes
`[RDI+0x4BE6A0]` in `R9`. This does not identify the source names `network` or
`resetting`, even though the argument positions align.

Reuse rule: record each callsite's exact register/stack value and the callee's
actual reads before assigning semantic labels. Trace a flag to its producer
and to every branch it controls. Matching prototype shape is a role
candidate, not proof of parameter meaning or runtime behavior.


## Additional 18 October 2026 lesson: trace a flag to its producer root

For the load-candidate audit, one caller passed `[RDI+0x4BE6A0]` in `R9`. A
fast exact-hash scan found seven references, and root-aligned inspection
identified a writer inside a chained unwind group. The first caller query
used the interior target `0x495675` and returned zero; resolving its root
`0x495640` exposed the actual caller at `0x4955F8`. That caller derives the
stored byte from a session-like pointer at `global+0x941C70+0x1A8` and its
fields `+0x418/+0x41C`, but the class and predicate meaning remain unproved.

Reuse rule: follow a field read back through its confirmed writers, then
resolve every writer RVA to its unwind root before searching callers. Keep
the result as an object-flow lead until class identity and predicate meaning
are independently anchored. A session-shaped offset or a Boolean value is
not, by itself, proof of network semantics.


## Additional 18 October 2026 lesson: constrain common object offsets

A whole-image fast scan for `+0x41C` returned 207 hints and truncated its
200-example output. It cannot identify a member on a particular
`PlayfabSession` object. An unqualified type-name probe and a data-RVA-as-code
probe also failed to reproduce existing RTTI evidence, and a generic
whole-image method probe was interrupted after more than a minute without
progress.

Reuse rule: tie the object base to exact constructor, RTTI or vtable evidence
before scanning a common displacement. Match the tool argument to its expected
section. A truncated shortlist is only a shortlist; interrupted work is
`NOT CHECKED`, never a zero result or class-absence claim.


## Additional 18 October 2026 lesson: bind fields to exact vtable methods

The full decorated `PlayfabSession` RTTI name found one 26-slot vftable.
Slot 17 tests the leading byte at `this+0x41C`; slot 20 reads a 64-byte region
starting there; slot 11 calls a helper that writes the same region. This is
stronger member evidence than a global displacement shortlist, but still
does not name the field or connect a separate application-global pointer to
that class.

Reuse rule: follow exact decorated type names, map the slot to a function,
resolve its full chained unwind group, and verify the receiver register before
assigning member meaning. Start disassembly at the root or a proven instruction
boundary. A region's first byte can be tested as a Boolean while adjacent
bytes remain structured data; do not collapse it to a standalone flag.


## Constructor index tables and owner identity

When a constructor populates an object array, inspect the exact index table,
allocation loop, final vtable writes, and indexed store together. A temporary
base vtable may be replaced by a derived vtable before the object is stored;
record both writes and identify which one is final. A matching array offset in
another code path establishes a structural link, but not that both paths use
the same owner instance or that an index means local/network. Keep those
claims `NOT CHECKED` until a caller or runtime identity path connects them.

Avoid broad whole-image displacement scans for common offsets once a validated
constructor and a specific reader are available. If an interrupted scan has
no result summary, record `INTERRUPTED / NOT CHECKED`; never reinterpret it as
zero matches. Prefer the constructor's exact index table and bounded callsite
dataflow.


## Tool bounds and caller setup

Check a scanner's `--help` or argument bounds before launching parallel full-
image scans. If a context limit rejects the command before scanning, record a
tool invocation error and retry within the declared bound; it is not a binary
result. For native ABI work, record every caller's register and stack setup,
then keep physical positions separate from source parameter names. Different
callers may pass different values to the same position; do not copy names from
an older-build prototype until a semantic branch or producer confirms them.

For a known class, prefer `native_vtable_member_xrefs.py` after validating the
exact decorated type and slot count with `native_rtti_vtable_probe.py`. It
searches only those vtable methods and all of their chained `.pdata` ranges;
record methods without `.pdata` separately. A zero-write result is scoped to
those method groups, not all classes or dynamic aliases. When a fast indexed
store scan finds `[base + index*scale + displacement]`, inspect how the index
register was computed before naming the element stride: pre-scaling the index
can turn an apparent scale of 8 into a 0x30-byte record stride. Treat `lea`
as address calculation, not a memory read, when classifying Capstone operands.


When an apparent signature candidate has an implicit `this` argument but the
source calls it with no explicit argument, follow incoming `RCX` through every
nested call before judging ABI compatibility. The candidate may forward `RCX`
unchanged even when its own body has no direct field read; inspect the callee
to see whether that register is consumed. In the Cosmos 7.06 `GetDominantHand`
trace, `0x14874B0` forwards `RCX` to `0x1C84D0`, whose body uses only
thread-local and global data, resolving that specific machine-call shape. Do
not generalize this result to other methods. Also decode a reused old RVA from
its verified function root: in this build `0x508200` is inside an instruction
ending at `0x508201`, so it is not a valid relocated entry even though it lies
inside a `.pdata` range.

For leaf helpers without `.pdata`, use exact direct-call boundaries and
argument setup from more than one relevant caller where available. The
`0x508290` owner predicate has no exception entry, but owner-update root
`0x508DC0` passes its unchanged owner object in `RCX` and active slot in `EDX`;
its body returns the Boolean in `AL`. This establishes a source-role
candidate without pretending the helper has an independent `.pdata` method
entry. A zero direct-E8 result remains limited to direct calls and says
nothing about virtual dispatch or other indirect references.

## Distinguish matching layouts from the same owner

When an exact RTTI/vtable path confirms a class has a member array, compare
the complete owner chain in the consumer: global pointer, application member,
object pointer, and array slot. Two paths that read the same `+0x1A8` field
may belong to separate instances. If a constructor stores a known instance at
one application offset and a candidate hook reads through another, record
both exact offsets and require an alias, copy, or caller path before joining
them. A validated vtable slot can prove an indirect method even when a direct
E8 scan returns zero; keep the search type and its limitations explicit.

Before declaring two owner paths distinct, calculate every nested offset
explicitly and compare the effective application-relative destination. Verify
the hexadecimal sum with a script or calculator instead of mental arithmetic,
and record the operands and result. For example, in the Cosmos 7.06 owner
trace, `0x937130 + 0xAB40 = 0x941C70`; this equals the load predicate's member
offset and closes the constructor-to-reader owner link. If a later check
corrects an offset calculation, append a dated correction and update the
active status; mark the earlier conclusion as a corrected false lead.


## Additional 18 October 2026 lesson: filter coverage and reference forms

For QAM slot 9 at virtual-call byte offset `0x48`, three exact-hash scans
requiring same-range field pairs `(+0xA050,+0xA088)`, `(+0xA05C,+0xA060)` and
`(+0xA100,+0xA104)` each returned zero matching ranges. These are bounded
negatives for those same-range displacement combinations. A caller may only
forward the QAM receiver and never read its fields; fields in one unwind range
may also use a different base from the virtual-call receiver. Do not combine
these results into “slot 9 has no caller.”

Keep reference forms separate. `native_call_xrefs.py` finds decoded direct
calls; `native_rip_xrefs.py` finds direct RIP-relative memory operands;
`native_branch_xrefs.py` finds direct immediate jumps within decoded `.pdata`
ranges; and `native_absolute_pointer_xrefs.py` searches literal preferred-base
VAs in non-`.reloc` sections. Each tool misses the other forms, relative tables
and dynamically constructed references. The first `native_branch_xrefs.py`
run omitted its scanned-byte counter; discard that output and trust only the
corrected rerun that reported all `52,110,272` runtime-function bytes and zero
skipped ranges. Preserve tool-output failures as `NOT CHECKED`, then rerun.

The `native_rtti_vtable_probe.py --target-rva` option accepts one target. A
repeated option invocation processed only the final target in this pass; query
multiple targets with separate commands. By contrast, `native_call_xrefs.py`
and `native_rip_xrefs.py` support repeated targets for one image scan. Check
each helper's `--help` before batching.

For load-candidate flag `+0x4BE6A0`, the exact build shows a constructor zero,
a setter write from `BL`, and one caller that forwards the byte in `R9B`.
Direct-call, RIP-relative, RTTI-vtable, direct-jump and literal-VA scans did
not find a static path to the setter. This does not prove the flag means
network or that the setter is unused: retain the field as an unresolved lead
until its dynamic caller/producer or an independent semantic anchor is found.


## Additional 22 October 2026 lesson: resolve chained unwind roots first

A chained `.pdata` range may start at an address that resembles a separate
entry while belonging to a function group rooted elsewhere. The load-flag
write at `0x4956B8` is in the range beginning `0x495675`, but its group root
is `0x495640`, and the direct caller targets that root. The old zero-caller
scan against `0x495675` did not show that the writer was unused.

Reusable rule: resolve the full unwind chain before interpreting callers,
branches, RTTI slots or other reference forms. Record whether each candidate
is a group root or chained range entry. If a prior scan used a non-root
entry, keep its count as historical and scoped, mark its conclusion
superseded, and rerun against the root.

A raw 32-bit RVA scan in non-executable `.rdata` found five values each for
`0x495640` and `0x495675`; every value matched a `.pdata` Begin/End/Unwind
triple, so those were metadata rather than pointers. Classify raw RVA triples
against `.pdata` before calling them references. `native_rva_data_xrefs.py`
now reports raw matches alongside `.pdata` record matches. It excludes
`.pdata` and `.reloc`, and does not find relative offsets, code immediates or
dynamically built pointers; keep those limits explicit in the evidence.


## Additional 22 October 2026 lesson: validate operand-access filters

On the exact Cosmos 7.06 executable with Capstone 5.0.7,
`movups xmmword ptr [rcx+0x41c], xmm0` was printed as `ACCESS:R` by an
RTTI-scoped `--access any` scan. Its memory operand is the instruction's
destination, confirmed by exact disassembly. The matching `--access write`
scan therefore returned a false zero for the base `Session` vtable. The
helper now treats an explicit MOV/VMOV-family memory operand at operand 0 as
a write in both `native_vtable_member_xrefs.py` and the detailed mode of
`native_data_offset_xrefs.py`.

Reusable rule: before accepting a zero write-filter result, compare it with
`any` mode and inspect at least one known candidate's instruction and operand
position under the same Capstone version. Rerun affected class-scoped scans
after changing the classifier, and record old results as superseded. Keep
`MOV`-family fallback scope and tool hashes explicit; other instruction
families still require their own direction check. A store found in a base
vtable method does not prove that a derived object reaches that implementation
or that it writes the field value read by another code path.

## Additional 22 October 2026 lesson: vtable scans do not follow callees

The PlayfabSession slot-11 method at `0x237820` contains no direct
`+0x41C` memory operand, but it calls base Session method `0xACA370`, which
writes the field. Therefore a zero from `native_vtable_member_xrefs.py` is a
direct-method-body result only. Follow each relevant direct callee before
concluding that a virtual method has no field-write effect. For indirect
dispatch from a manager array, separately establish the manager owner, the
dynamic type stored at each slot and the invocation lifecycle; matching
offsets alone do not close those links.



## Additional 22 October 2026 lesson: validate vtable query bounds

An exact RTTI probe with `--max-slots 64` returned zero for function
`0x2357C0`. That was a query-bound false negative: the exact Playfab and
PlayfabSteam tables each contain 87 executable slots, and the target is at
slot 80. Repeating with `--max-slots 96` found it in both tables.

Before treating an RTTI zero as evidence of absence, record the requested
maximum, reported slot count, executable-slot bound and target slot index.
Raise the bound enough to cover the relevant table, then verify the returned
pointer location equals `vtable_start + slot_index * pointer_size`. Align
literal absolute-pointer hits to that same verified slot before identifying
them as vtable references. Mark old under-bounded negatives as superseded,
not as global negatives.

Likewise, update class-scoped access scans when correcting a table length:
a scan over 64 slots did not cover the 87-slot Steam table. Report the exact
slot count, `.pdata` method roots and slots without unwind metadata
separately; a method-body zero remains limited to the covered roots and
does not include callees, aliases or dynamic dispatch effects.



## Additional 22 October 2026 lesson: inventory data dependencies as well as entry points

The source function-RVA inventory was not the complete runtime dependency
inventory. A read-only pass over the game-facing integration files also found
absolute global pointers, nested object offsets, table strides, enum/value
limits, resource-manager globals and resource-record fields. A recovered
hook entry cannot validate any of those neighboring reads or writes.

For each update, enumerate every game-facing dependency from the exact source
files: executable entries, call targets, callbacks, globals, object fields,
array/vector layouts, element sizes and strides, function signatures, code
prefix checks and strings/resources used to identify data. Keep purely
platform-format constants and offline fixture code out of the game ledger,
but record any compile-time experimental path separately. Give every row the
exact executable hash, source symbol and file/line, owner chain, evidence
form, status, blind spots and required offline/runtime gate. Reconcile the
ledger against all source references before claiming it is complete.

Do not treat a familiar object offset, a matching value in a different
subobject, or one remapped hook as validation for the rest of the profile.
Preserve unresolved rows as `NOT CHECKED` and keep unsupported builds
fail-closed.


## Additional 22 October 2026 lesson: keep game, package, source and runtime profiles separate

For every update note, record four identities independently: game release and
Steam build; exact executable SHA-256; public mod package/file version; and
Git source commit. Check the official game release page, the public package
page and the repository default-branch tip separately. A matching local
baseline does not imply the public package supports the new game build, and a
higher package number does not establish game compatibility.

Inventory each runtime profile by path and purpose before editing it. In this
repository `native_compatibility.json` is the native runtime profile, while
root `compatibility.json` is the legacy Python runtime profile. Do not update
one because the other contains a nearby game version. Record both values when
they differ, and change only the profile whose runtime has passed its own
compatibility gates.

## Additional 22 October 2026 lesson: rejected CLI arguments are not scan results

When a research tool rejects an argument before decoding, record the exact
invalid invocation and the tool's limit as an invocation error. It contributes
no match count, coverage or negative evidence. Rerun with a valid value, record
the successful command and its actual coverage, and preserve the distinction
in the report and handoff. Example: `native_call_xrefs.py --context 16` is
rejected because the supported maximum is 12; rerunning with `--context 12`
found one direct caller of `0xACA370` in the exact 7.06 image.


## Additional 22 October 2026 lesson: recover callee ABI before caller search

Before reviewing virtual-call candidates, disassemble the exact target and
write down which registers carry the receiver and arguments, what each
argument points to, and which values the callee preserves or overwrites.
Use that shape to narrow callers, then track receiver identity and volatile
register setup across every call between argument preparation and dispatch.
Example: QAM slot 9 at `0x153C0C0` receives the QAM receiver in `RCX`, a
string destination in `RDX`, and writes one zero byte through `R8` at entry.
The byte's meaning is unknown. A same-function offset, a stack-buffer setup
before another call, or an `R8` assignment after dispatch cannot satisfy this
contract.

## Additional 22 October 2026 lesson: same-function filters do not prove object identity

A same-function displacement filter establishes co-occurrence only. Before
using it as a receiver anchor, identify the exact memory operand, its base
register and def-use chain, and show that the same object reaches the
indirect-call receiver at dispatch. A matching member may be a different
subobject or a cleanup path later in the function.

At each candidate call, re-establish every volatile argument after the last
intervening call. On Windows x64, `RCX`, `RDX`, `R8` and `R9` are
volatile; an earlier setup is not live merely because it appears in the same
window. For QAM slot 9, require the exact QAM receiver in `RCX`, the string
destination in `RDX`, and the writable byte pointer in `R8` at dispatch.
Example: the 7.06 `+0x116B10` plus slot-`0x48` filter found two calls, but
the field was used later for QAM-child cleanup and neither call had the
required receiver/argument contract. Keep both as false leads; do not turn
same-function matches into a caller count.

An ABI-shape scanner is only a shortlist. On the exact 7.06 image, slot
offset `0x48` produced 789 calls in 523 ranges; requiring pointer setup in
`RDX` and `R8` after the last call reduced this to 55 candidates. RTTI then
identified the tempting wrapper targets `0x2E51800` and `0x2E51880` as Havok
serialization pointer implementations, not QAM methods. Another candidate
at `0x347F58` was in a chained range rooted at `0x346B30`, an RTTI-confirmed
`cGcAtlasBrokerAzure` slot-10 method; its nested receiver `[this+8]` is still
unidentified. Neither result establishes a QAM caller. Resolve the full
`.pdata` root, receiver origin and exact owner type before promoting any
ABI-shaped call. `tools/native_vcall_abi_candidates.py` records this bounded
shortlist; its exact-build command and hash are in the 25732212 report.

For a serialized field, a one-way load read is not enough. Trace initialization,
the save-side copy from runtime state into the common object, and the load-side
copy back from that same common-object offset. This establishes the static
field contract when width and base identity agree; it still does not establish
that the value is a unique save ID or that every caller is a local load.


## Additional rule: report release readiness separately from research progress

Static-analysis effort is not release readiness. Do not give a percentage
unless the denominator and gate weights have been defined; a precise-looking
number without that basis misstates progress. Prefer explicit states for:
exact target identity; dependency mapping; source/profile port; offline
validation and archive; exact-build runtime verification; release documents;
and remote GitHub/Nexus readback. Report mapping coverage separately from
implementation, validation and release readiness. Mark every unfinished or
unobserved gate `NOT CHECKED`; a large number of useful scans must not imply
that the build is ready. State the fail-closed/runtime status directly until
every mandatory gate is satisfied.

## Additional rule: compare source detours with the exact target ABI

When porting a hook, inspect the old function-pointer typedef, detour wrapper,
post-hook writes and buffer size alongside the exact-build target body and
caller. A matching semantic role does not establish a safe replacement.
Account for added or reordered arguments, preserve them when forwarding the
original, and establish output capacity and ownership before writing. Leave
the hook unmapped if a caller or buffer contract is unresolved.

## Additional 22 October lesson: anchor virtual methods through constructors

For a virtual-method candidate, tie the exact RTTI-backed vtable to a
constructor store, then tie that constructor's `this` pointer to its parent's
field/caller chain. In Cosmos 7.06, slot 9 target `0x153C0C0` belongs to
`cGcQuickActionMenu` vtable `0x4A504E0`; constructor `0x2CA6D0` stores that
vtable at `[this]`. Parent constructor `0x2CA290` calls the child with
`parent+0xDC0`, and its caller passes `outer+0x115D50`. This establishes
class/owner identity and the composed `outer+0x116B10` child address. It does
not locate a call to slot 9 or establish the output argument's semantics.

A follow-up `native_vcall_xrefs.py` query requiring slot offset `0x48` and
both QAM displacements `0xA050` and `0xA088` returned zero function ranges
and calls across the complete `.pdata` inventory. The helper's filters only
test same-function displacement presence; this does not prove absence of a
slot-9 caller. Preserve it as a bounded negative and do not rerun the same
filter unchanged. Move to receiver-register/dataflow evidence or work an
independent unresolved dependency.

## Additional 22 October lesson: relocate the application pointer from a named consumer

Do not carry a source-build application global forward because it is nearby
or because many offsets depend on it. Use an exact-build consumer whose role
is independently established, resolve its RIP-relative operand, and verify
the pointed-to object's expected child. The 7.06 `CanSummon` candidate at
`0x1474F10` loads global RVA `0x6E8D708`, then uses `app+0xE10D0` as the
companion table for eligibility calls; the session path at `0x4955AD` reaches
the same global. This supersedes source global `0x6E89688` for the exact
25732212 executable. It does not validate every app-relative field, so
inventory and close each dependent role separately.

## Additional 22 October lesson: field matches need owner and width evidence

An offset search only returns candidate instructions. Tie the base register
to the exact owner object, trace its derivation to the field access, and record
access width and direction before mapping a source dependency. In Cosmos 7.06,
the `0x50D4B0` roster path derives `entry=app+0xE10D0+slot*0x24A0`, then reads
8 bytes at `entry+0x23C0` and 4 bytes at `entry+0x2480`; this supports those
addresses and widths, while their source semantic names remain unverified.
The `0x50E1A0` path uses the same roster base/stride but reads 16 bytes at
`entry+0x2330`, whereas the source identity helper reads 8 bytes there and a
separate 8 bytes at `entry+0x23C0`. Keep that identity dependency `PARTIAL`
until the target's 16-byte contract is reconciled with the source. Do not
promote capped offset-scan hints or a nearby field to a mapping without this
owner-and-access chain.

## Additional 22 October lesson: trace the release package to its source tree

The repository can retain multiple implementations with different game
profiles. Before calling any file the port baseline, inspect the active
compatibility profile, build inputs and package allowlist. In this repository,
the 0.10.2 player package is the native C++ implementation under `native/src/`
and its profile is Cosmos 7.05; `src/runtime.py` retains a Python/pyMHF 7.04
profile and is not the active player package. Keep the legacy source outside
the 7.06 native dependency denominator unless the selected release actually
includes it.

## Additional 22 October 2026 lesson: callee first use decides argument meaning

Map each physical Win64 register/home/stack slot through the exact callee
prologue and every chained `.pdata` range. Record the first read, write or
address escape, plus its width. A caller writing one byte into an argument
slot does not establish that the callee consumes a byte parameter; the callee
may ignore it or reuse that memory as a local. Likewise, saving `R9B` into a
home slot does not prove its meaning if the slot is overwritten before it is
read or passed by address. Do not assign old source names such as `network`,
`resetting` or `extra` from argument position alone.

In Cosmos 7.06, candidate `0x573500` has eight chained ranges. Its prologue
maps `[RBP+0xCC8]` to the incoming `R9B` home slot, `[RBP+0xCD0]` to the fifth
argument and `[RBP+0xCD8]` to the sixth. The fourth-argument home slot is
overwritten at `0x576407` before a direct read or address escape. The sixth
slot's first access is a byte write at `0x573653`; later byte, word and dword
uses operate on the reused local. Only the fifth input is directly read, as a
byte comparison at `0x578B2F`. Its semantic label is still unresolved. The
caller values and this callee-first-use result are recorded in the exact
build report; keep the load hook `PARTIAL` and 7.06 fail-closed.

When a candidate does not consume an apparent input, do not spend another
whole-image scan trying to name it from the caller's byte value. Follow the
callee's actual branch and helper effects, then use an independently anchored
caller or live observation to establish the remaining semantic contract.

## Additional 22 October 2026 lesson: launcher errors are not scan results

If a helper fails before opening or decoding the target executable, record
a `TOOL ERROR`; do not record zero matches, a missing dependency or a code
defect. Check both `python` and `py`, verify the chosen interpreter version
and required imports, then rerun with the explicit interpreter executable
if the launcher is misconfigured. Preserve the failed invocation and the
successful command, interpreter SHA-256 and dependency versions in the
exact-build report. Do not install or repair packages before this check.

A previous-build hook RVA is only a search lead. Resolve it against the new
executable's `.pdata` and instruction boundaries. In the Cosmos 7.06 audit,
old target `0x572C40` was inside function root `0x572410`, not a new function
entry; it cannot be carried forward as a 7.06 entry hook without separate
proof of a deliberate, instruction-safe interior hook. Keep the distinct
candidate `0x573500` partial until its source/runtime contract is established.

Caller flag values can narrow a meaning without naming it. Candidate
`0x573500` receives fifth-argument zero from all three non-death-state call
paths and one from the RTTI-confirmed `cGcApplicationDeathState` path; zero
takes helper `0x6019F0`, one skips it. This correlation may indicate a mode
difference, but does not prove the source parameter name `resetting`. Retain
that label as unresolved.

## Additional 22 October 2026 lesson: atomic fields need owner and ABI evidence

A whole-image displacement scan can return thousands of unrelated accesses.
Narrow it by operation semantics (for example, atomic increment/decrement of
the exact field), then require independent evidence for the owning object,
manager/table path, argument shape and callers before assigning a role. In the
7.06 resource audit, `+0x134` produced 1,008 broad operands but only 10 atomic
operands; the retain/release pair was accepted only after both used the same
handle table and global and their `RCX` pointer-to-handle ABI matched the
source. An old RVA inside a nearby unrelated routine is a false lead. Keep
refcount arithmetic separate from live resource readiness and lifetime proof.

For direct RIP-global owner searches, add a reusable read/write access filter
instead of running Capstone full-detail decode over every instruction in the
image. Keep the streaming `disasm_lite` pass for all runtime-function bytes,
then decode the detailed operands only for instructions that resolve to the
requested target. Record the interrupted full-detail attempt as `NOT CHECKED`
and the completed optimized result separately; never treat partial progress
as a zero or partial match count.

Nearby resource bytes do not share a meaning by address alone. In the 7.06
resource loader, `+0x13B` selects a fallback resource, while `+0x13A` was not
read in that helper and stays unresolved. Label each field from its exact
branch/read/write behavior; do not promote a neighbor because the mod's old
source gave it a descriptive name.

A zero RTTI-vtable hit does not mean a function is unused or a bad hook
candidate. Check whether it is a direct-call method and validate its receiver
and arguments at caller sites. Conversely, a signature match and one caller
do not make a safe detour: follow every relevant call path when the mod uses an
argument the native body itself ignores, and retain an exact identity guard in
the callback.

## Additional 22 October 2026 lesson: scan direct calls to RTTI-mapped slots

After RTTI or a constructor maps a virtual slot target, search exact direct
E8 calls to that target as a separate pass. The actual QAM label call in
Cosmos 7.06 was a direct call from the QAM update root, with `RCX`, `RDX` and
`R8` set explicitly; same-slot virtual-call candidate scans did not find it.
Record the complete `.pdata` scan scope and skipped-range count. A direct-call
hit proves only that callsite's static target and argument setup; zero E8 hits
does not rule out virtual, function-pointer or other indirect dispatch.
Inspect the caller after the call for output consumption, but keep any
consumer conclusion bounded to the traced function and path.

## Additional 22 October 2026 lesson: avoid full-detail offset scans for field naming

A detailed Capstone scan of every `.pdata` instruction for common item
displacements can run for a long time and yields candidate bases, not object
identity. In the 7.06 QAM pass, a two-offset `+0x4C/+0x4D` scan was stopped at
`0x1403715` decoded runtime-function bytes with no final counts. Treat that as
`NOT CHECKED`, never as zero matches. Start with a cheap candidate pass only
when a full-image shortlist is useful, then confirm access width, direction,
base object and def-use inside an owner-anchored function. For a small known
set of QAM methods, inspect those exact `.pdata` roots first and skip the
global scan when it cannot establish more than the owner-root evidence.


## Additional 22 October 2026 lesson: follow candidate data after constructors

Constructor zeros are initial state, not proof of final keys. In the exact 7.06 QAM update, the constructor clears descriptor key bytes, then an update root copies full `0xE0` rows from source records into the selected descriptor array. The binding pass compares qwords at descriptor `+0x88/+0x90`, which come from source-row `+0x08/+0x10`. To determine whether a custom marker can match, trace both the copy source and later comparison; do not repeat generic offset searches or infer candidate values from the constructor.

## Additional 22 October 2026 lesson: name state fields from setters first

An owner-bounded setter can map a numeric state field without naming each state. Record its access width, old/new data flow, observer notification and all directly decoded caller values. Then trace state-4 callers and lifecycle before assigning a semantic label such as connected, local or network. A matching ordinal or a session-related predicate is not enough by itself.

## Additional 22 October 2026 lesson: correct queries before interpreting zero

A failed argument check or an incomplete decorated RTTI selector does not produce a negative result. In this pass, the call scanner accepts context up to 12, the vtable member scanner has no `--limit-per-offset`, and the base Session type name includes its `cGcMatchmaking` namespace. Record the corrected query and distinguish tool/query errors from a completed zero-match scan.


## Additional 22 October 2026 lesson: a matching offset is not the same object

In exact QAM update root `0x15286C0`, `RDI` is the QAM receiver and `R15` is the incoming `R8` third argument. The binding loop writes `+0xD8` to rows from vectors based at that third argument while comparing against QAM descriptors. Do not map this to a source QAM item's `+0xD8` by displacement or row stride alone. Prove pointer aliasing between the actual row vectors before assigning the source field a native writer.

A zero vcall result filtered by a same-function QAM displacement rules out only that filter. The caller can invoke the known slot without referencing the QAM member in its own `.pdata` range. Record the complete scan scope, preserve the bounded negative, and move to a constructor, receiver or caller anchor instead of repeating the filter.


## Additional 22 October 2026 lesson: verify small indexed owner tables

When a session or manager path computes `base + index*stride`, decode the exact index source and its loop bounds. In this build, the three bytes at the data RVA used by the state dispatcher are 0, 1 and 2, so the path can visit manager entries `+0x1A0`, `+0x1A8` and `+0x1B0`. Match the event ID against the entry's own identity before claiming it affects the target slot. The resulting state number still needs event/lifecycle evidence before it receives a semantic name.


## Additional 22 October 2026 lesson: verify the virtual receiver at the call

A same-range field filter can pair a real QAM subobject access with a virtual call on a different object. In the `+0x116B10` candidate, the QAM subobject was the receiver of a direct call, while the later slot-0 call used `RCX=[RDI]`. Track `RCX` at the exact dispatch and reject the candidate when it does not equal the proven subobject.

## Additional 22 October 2026 lesson: recover an owner through a large stack frame

A global exact-displacement scan may find both object fields and stack locals.
Resolve the root function and its full chained .pdata group, then prove the
address base. In the QAM builder, entry RCX was saved at [RSP+8], eight
nonvolatile registers were pushed, and RBP was set to RSP-0x5638. The later
[RBP+0x5680] load therefore recovers that saved RCX; its R12-based +0xA16C
access is on the same QAM receiver. TriggerAction provides the independent
anchor by copying RCX directly to R15. This argument/stack-slot derivation
mapped the byte's setter, consumer and clearer.

## Additional 22 October 2026 lesson: state the owner-scan boundary

A vtable member scan covers only the supplied RTTI-backed method roots and
their chained unwind ranges. It can miss builder, callback or directly
invoked routines that access the same object. Preserve the method/slot count
and the number of slots without .pdata; follow a bounded zero with a complete
displacement scan and exact owner dataflow instead of calling the field
unused. In the QAM pass, the vtable scan checked seven roots and excluded nine
slots without .pdata; the global scan then found three QAM object accesses
among five stack-local false matches.

## Additional 22 October 2026 lesson: constructor zeros do not map a producer

Same-offset writes in similarly sized objects are not evidence of a shared
field owner. Resolve each write to its allocation/constructor root and
follow exact direct callers. The +0x480 candidates were zero-initializers in
untyped 0x4B0-byte record constructors; no caller proved an alias to the
RTTI-identified matchmaking manager. A zero at a manager-relative offset is
initial state, not proof of event-list population or a positive writer.

## Additional 22 October 2026 lesson: resolve chained-range targets before xrefs

Before a direct-call scan, use the exact target's unwind group. A scan against
an interior chained range can return zero even when the parent method has
callers. Record the parent root and rerun against it; keep the interior zero
out of any owner-level negative result. Also check each helper's accepted
arguments before adding filters; native_data_offset_xrefs.py does not accept
--context, and that invocation must be corrected rather than read as a scan.

## Additional 22 October 2026 lesson: reduce singleton reference noise by access direction

A RIP-relative global may have tens of thousands of readers. On the exact 7.06 image, global pointer RVA 0x6E8D708 had 26,301 direct RIP references, but a write-only filter reduced that to three. Resolve each store to its .pdata root before assigning a lifecycle role. Here one store allocated/installed the application object and two initialized or cleared the pointer.

## Additional 22 October 2026 lesson: search deep application fields from the proven subobject base

A displacement scan against a large application class can find many unrelated methods and stack locals. First prove the application object base and size, then calculate the requested field relative to each constructor's actual subobject argument. Correction: the earlier claim that application+0x941C70 was not reachable from application+0x937130 is retracted; it used incorrect subtraction. 0x941C70 minus 0x937130 is 0xAB40, and a separate startup root stores an RTTI-confirmed cGcMatchmakingPlayfabSteam pointer through subobject+0xAB40. The positive store and dynamic type close the app-member installation gate. The accesses in helper 0x2CE200 were not re-evaluated by this correction. Do not infer the session-array population path or local/network meaning from manager installation alone.

A zero from a store-filtered field scan describes only direct decoded writes using that base/displacement. Check whether a helper receives the field address, whether an object copy aliases it, or whether the access uses another proven subobject base. Record the exact boundary and leave positive initialization open when those paths are not established.

## Additional 22 October 2026 lesson: a Boolean-looking byte may be key emptiness

In the RTTI-anchored PlayfabSession, slot 20 copies four 16-byte chunks from +0x41C through +0x44C into a lookup key, while other methods test the first byte as empty/nonempty. This is not evidence that the byte means local versus network. Follow wider consumers and exact key producers before naming it.

## Additional 22 October 2026 lesson: separate interior-range xrefs from owner results

A call scan against chained range 0x334068 returned zero. The containing group resolves to root 0x333CA0, which is an RTTI-confirmed cGcApplicationShutdownState virtual slot. Re-run direct-call scans against the root and preserve both scopes; a zero E8 count cannot negate an indirect vtable dispatch.

A raw PE probe using invalid RVA 0x4AA91134 failed before data access. The correct selector table RVA was 0x4A49134; its bytes are 00 01 02. Classify the first invocation as TOOL ERROR, not a binary negative.

## Additional 22 October correction: application-subobject arithmetic and dynamic session ownership

The earlier statement that application+0x941C70 was unreachable from the application+0x937130 subobject is retracted. The subtraction is 0x941C70 - 0x937130 = 0xAB40. Exact startup evidence stores an RTTI-confirmed cGcMatchmakingPlayfabSteam object at [subobject+0xAB40], closing the application-member owner/type gate. The accesses in helper 0x2CE200 were not re-evaluated by that correction.

Keep three proof steps separate: a constructor's object size does not by itself prove a member assignment; a verified store plus RTTI can identify the object installed at an application member; a consumer that reads an adjacent session array does not prove which initializer populated it. Resolve the actual vtable slot before interpreting an indirect call: the candidate manager slot +0x290 maps to 0x36A410 and returns -1, so it is not the PlayfabSession initializer.

A global +0x1A0 displacement scan on the exact build completed with 1,686 operands and printed only the first 100; most are unrelated stack locals. The RTTI-bounded Steam-manager write scan is the useful scoped check: zero writes in 42 .pdata method roots, with 44 vtable slots lacking .pdata. Do not repeat the broad scan. The constructor at 0xAD5A90 remains unlinked to the installed manager; zero direct calls or static pointer references do not exclude dynamically registered invocation. Find that route or an alternative owner-proven positive writer before naming session semantics.
Root-resolution correction for the load caller: range 0x4955B4-0x495623 is chained to 0x495560. The zero direct-call and RTTI queries against 0x4955B4 were interior-range results, not owner-level negatives. The corrected root query against 0x495560 found four direct callers; its RTTI query still found no validated slot. Likewise, range 0x497464-0x4978CD belongs to root 0x495640, whose caller scan found the 0x48FA60 edge. Keep the chained-range zeros as scope errors and retain only the corrected root-level counts.

## Additional 22 October 2026 lesson: normalize provider line endings before comparing hashes

For pinned NMS.py `tools/data.json` commit `b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`, the raw-LF SHA-256 is `14FF4F02D732E31A83885E3ED38A9304900A45D96297A3BA95DA720ED87A8832`; converting the same 370-record JSON to CRLF yields `F311C9F54C0CCE199AB955A0E8DE2CFE2FCFB09274E557A2A27908C1B15BAF5F`. Verify the parsed records and record both byte hashes when line-ending normalization is possible. Do not mistake a checkout conversion for a provider revision or reuse a scan without recording the exact data bytes used.

## Additional 22 October 2026 lesson: prove plain-object ownership by pointer identity

When a class has no validated RTTI vtable, an exact constructor anchor can still prove a non-polymorphic object's identity. Trace the constructor caller's application subobject, the constructor's `this` adjustment, and each consumer's first argument back to the same address. For this build, `application+0xE70+0xAAD0=application+0xB940` ties the unique `cGcPlayerState` constructor match at `0x572410` to all four discovered direct receivers of load-role candidate `0x573500`. The candidate still has zero named `LoadFromData` signature matches. This establishes the receiver for those direct calls, not the callee's complete semantic role, absence of indirect calls or local/network behavior.

## Additional 22 October 2026 lesson: track the dispatch receiver independently from other arguments

Resolve `RCX` at every call instruction after the last intervening call. A nearby `lea` into another register may prepare `R8` or a stack argument without changing the receiver. In root `0x32F385`, `0x32FC21` writes `application+0xE90` to `RBX` for an `R8D` read, while `RCX` remains `application+0xE70` for the call to `0x495560`. Do not name an object or class from a same-function pointer unless its exact register reaches the dispatch.

## Additional 22 October 2026 lesson: exclude non-feature lifecycle callers before enabling a global hook

A function can have the correct class receiver and still run during a different feature. Candidate `0x573500` has a direct call from the exact `cGcApplicationDeathState::Update` body. The current mod's load callback filters with the fourth register input but does not receive the fifth stack byte; the candidate overwrites its fourth input before reading it, and the fifth byte's meaning is unresolved. Before a global detour is approved, prove a local-save completion boundary or a reliable call-path exclusion. Keep death/respawn separate from save-load and do not infer parameter names from the old ABI's slot positions.

## Additional 22 October 2026 lesson: map owner-bound state transitions without calling them completion

For a lifecycle candidate, first validate the class vftable with RTTI, then scan the bounded method roots for exact-width reads and writes of the member. Resolve the member's switch table and transition helper, and inspect how each caller uses the helper's return. A numerically ordered state field and a final reset are only a transition map; they do not establish that the state means a completed user save load or excludes death/respawn. A named `GetRespawnReason` returning several codes still needs an exact-build enum/event mapping before one value can gate behavior. Keep that dependency `PARTIAL` and fail-closed when the runtime contract is absent.

In the 7.06 LocalLoadState pass, the RTTI-validated Update root reads/writes a 32-bit field at `+0x62C`, and helper `0x33E1C0` advances it through 22 switch cases. Case 21 resets it to zero after final state work, but the value at `+0x620` is typed only as `cGcPlayerRespawn::RespawnReason`; the pinned provider has no enumerator names, and no numeric-to-local-save/death mapping is available. Calls whose return value is not tested or otherwise consumed are not completion predicates; preserve that call-result def-use in the ledger.

When extracting a PE switch table, verify whether entries are relative displacements or zero-extended RVAs from the machine code that forms the table base. The first 7.06 one-off parse subtracted the image base from 32-bit RVA entries and produced invalid negative values; discard such output before interpretation, correct the parsing, and record the correction as a tool/decode error rather than a binary negative.

## Additional 22 October 2026 rule: prove relocated helpers and path-specific arguments

When a native target moves, first resolve its containing and chained .pdata ranges. Reject old RVAs that land inside a new instruction, even when the surrounding function still resembles the old role. Corroborate a replacement with several independent anchors: function boundary and size, direct callers and caller roles, string references, and internal callees that perform the same operation. A matching size or fixed RVA delta is supporting evidence, not byte identity or permission to install a hook.

Map each changed call return from the actual decoded instruction end and verify it is an instruction boundary in the new executable. For each call argument, trace the value along the specific incoming control-flow path from the switch or caller entry. A register used as a counter in a neighboring block does not establish its value at a different case; equally, a nearby initializer does not establish the value if a reaching path can overwrite it. Keep exact register width and the last reaching definition in the evidence note.

Treat each cross-reference tool according to its implemented instruction classes. In the 7.06 pass, native_branch_xrefs.py searched direct immediate JMP only and missed a JNE to 0x3302BB; a zero result was a tool coverage limit, not proof of no branch. If a tool's result conflicts with root-aligned disassembly, prefer decoded instruction evidence and record the limitation. A wrapper quoting error that prevents the scanner from running is also not a binary negative.

A relocated shared helper can remain unsafe even after its address and one caller's arguments are mapped. Enumerate direct callers, identify death/respawn and other lifecycle paths, and keep callsite filtering, enum meaning and live completion semantics as separate gates. Never transfer numeric enum meanings from an older game executable without exact-build evidence.

## Additional 22 October 2026 rule: keep enum outputs and field setters owner-bound

For an unnamed native enum, record the exact output values and the conditions that produce them, but do not assign event names from numeric similarity or an older build's runtime log. Resolve the member receiver independently, then trace each exact-width setter and clearer within the RTTI-bounded owner methods. Mark stack-local displacement lookalikes separately; a matching offset with the wrong base is not a member access.

A same-range virtual-call filter can return a call on a different object than the one whose fields were matched elsewhere in that function. At every indirect dispatch, trace RCX from its last assignment to the call and validate the receiver's vtable/constructor chain before assigning an owner method. A zero result from a same-range filter or a direct E8 scan does not establish that a virtual method is never invoked.

When a native method computes an enum from several flags and global state, close two separate gates: the static input/output map and the runtime/event meaning. Keep a candidate PARTIAL until the value is observed or otherwise proven for the exact event; do not make a 7.06 hook active from static numbers alone.

## Additional 22 October 2026 rule: use applied FSM identity to separate lifecycle paths

For a shared load or lifecycle helper, map the owner state machine rather than inferring the active mode from a pending transition request. Resolve the manager's embedded state table, the exact current-state pointer field, each state's manager back-pointer, and the dispatch slot that invokes the active state. Distinguish a request queued during an Update from the transition applied at the next manager Update: the current-state pointer still names the old state while that callback is running.

Then follow one exact feature path from the state Update through its helper calls to the shared candidate, and compare it with the unwanted lifecycle path. In Cosmos 7.06, `APPLOCALLOAD` is the `cGcApplication` subobject at `+0x1370`; its Update path reaches load candidate `0x573500`, while a direct call in DeathState Update requests `APPVIEW`. A check that the FSM current pointer equals the exact LocalLoadState object is therefore a promising static discriminator, not live compatibility proof. Preserve indirect-call and runtime timing limits, and keep the build fail-closed until behavior is verified.

Use full `.pdata` call scans to enumerate decoded direct callers, but state their exact scope. A zero literal preferred-base pointer scan does not exclude relative tables, dynamically formed pointers or indirect calls. If `py -3.11` fails before decoding with `No installed Python found!`, classify it as `TOOL ERROR` and rerun with the explicitly verified Python 3.11 executable; do not record the failed invocation as a match count.

For the existing callback, compare the detour's actual parameter use with every new caller before reusing its old meaning. A shared target may still call the same code during death or another lifecycle path. Preserve the original arguments exactly, then gate mod-side effects using an independently validated state identity; do not infer `network` from an old slot or from an unnamed session byte. In the 7.06 pass the DeathState call supplies zero in `R9`, which the existing 7.05 wrapper interprets as `network=false`; without a current-state check a successful death-path return could incorrectly arm save-load behavior. Keep this as a static risk until exact-build runtime behavior is verified.

## Additional 22 October 2026 rule: map detour inputs by their actual use

For a hook argument whose native type is uncertain, trace the exact target body from entry through its first read, write, address escape or volatile-clobbering call. A register used later only after an explicit overwrite is not evidence that the original input is consumed. Record the caller's register transfer and the target's full chained .pdata group. This can establish a narrow hook ABI without naming the opaque object's native type; do not expand that conclusion into a rendering, ownership or lifecycle claim.

For virtual calls inside an owner method, the method's own fields do not identify the virtual receiver. Trace RCX at the call and compare it with the independently proven object/subobject address and RTTI or constructor chain. A same-function field filter can find a call on a sibling application object. Keep zero results scoped to the exact slot, field, decoded ranges and tool behavior.

Full-image scanners may return a live process session after printing progress. Capture and poll that session until final file hash, decoded byte/range totals, match counts and exit code are available. If output is lost or incomplete, classify the attempt as NOT CHECKED and rerun only to recover complete evidence; never record progress-only output as a zero match.

## Additional 22 October 2026 rule: map embedded vector headers through insertion and cleanup

For an embedded native vector, do not name a count from an offset hit alone. Trace the call ABI into the insertion helper and prove the header's capacity, count, data pointer, element stride, increment and returned pointer. Follow one exact consumer to the indexed record and one cleanup path that clears or transitions the count. Record the exact base object and access widths. When source and native floating-point guards differ on unordered values, record the input class explicitly; matching ordinary-value branches is not full predicate equivalence.

## Additional 22 October 2026 rule: prove selected QAM rows through the real label consumer

For a custom quick-menu item, first validate the exact decorated RTTI name and vtable, then resolve the slot's complete chained .pdata group and exact callers. Trace depth, selected index, vector count, data pointer and element stride to one selected record; distinguish the action field at +4 from an icon handle at +0. A confirmed label consumer does not prove that the renderer reads the icon or that the custom row is visible. Trace the same proven QAM object into the generic draw/resource path before promoting custom-row rendering.

The 7.06 QAM label method at slot 9 selects a 0xE0 row from the depth-specific vector and reads its action at +4; the currently mapped path does not read the first dword. The mode's after-label hook runs after the native formatter and overrides only marker-identified custom rows. Keep the icon consumer and live render behavior open until independently mapped.

The RTTI helper searches decorated MSVC class names. An undecorated short-name query may return zero validated locators even when the exact decorated name succeeds; rerun with the class's exact decorated name before recording any absence. If a full-image query prints progress but its final output is lost, mark it NOT CHECKED, not zero, and retain its exact command. Do not repeat a broad same-offset scan when the QAM base is not tracked through the call.
## Additional 22 October 2026 rule: keep RTTI method scans and virtual-call candidates scoped

A scan limited to RTTI-validated class vtable methods can prove member reads only in those exact method groups. A zero for a row icon offset does not rule out reads in a generic renderer, non-virtual helper, alias or dynamically calculated address. After a class-bound negative, pivot to the owner-proven object and follow its caller or render-state pointer; do not widen the same displacement scan.

A virtual-call ABI shortlist that requires RDX/R8 setup is only a candidate filter. Validate the exact RCX receiver and the vtable target before assigning the call to a class. In the 7.06 slot-zero shortlist, 16-byte stream routines containing the Zstd marker were false UI leads. Keep the candidate count and the inspected/rejected subset separate.

If a scanner rejects an argument before reading the binary, record TOOL ERROR and correct the argument range before retrying. Do not treat a validation failure as zero references.

## Additional 22 October 2026 rule: track embedded virtual receivers and row-resource flow

When a class instance is embedded in a parent, search candidate owner offsets by tracking a `lea owner+offset` into the object pointer, its first-qword vptr load, and the subsequent indirect call slot. Corroborate each candidate against an RTTI-validated vtable and constructor write before naming its class. An offset-only same-function match is a lead, not receiver proof. A helper limited to one `.pdata` range cannot carry register provenance across `UNW_FLAG_CHAININFO` fragments; resolve the full group and inspect the exact ranges when the call crosses a fragment boundary.

For UI rows, trace the exact record pointer, `0xE0` stride, first-dword resource value and downstream resource consumer. Keep a generic source-vector consumer separate from a custom row appended to a class-owned vector until pointer identity or an alias is proven. A confirmed integer-resource lookup does not by itself prove that a specific custom row is rendered or that the resolved handle is an icon.

For tools that require an RVA, convert an image VA by subtracting the PE image base. Record the rejected VA invocation as TOOL ERROR and use only the corrected RVA result. If a detail-mode analysis is interrupted before a summary, mark it NOT CHECKED and base conclusions only on a completed run.

## Additional 22 October 2026 rule: preserve computed row-owner identity

When a renderer reaches a vector through an indexed owner such as `base + index*stride + field`, record and follow that full expression from its caller. Matching row stride, field offsets, and action/icon layout make a useful type lead but do not prove pointer identity with a separate QAM-owned vector. A renderer and an embedded QAM dispatch in the same method may still consume different objects. Trace the builder's exact third-argument pointer to the computed owner or keep custom-row rendering unresolved; do not repeat broad displacement or generic ABI scans.

Each `exec_command` PowerShell invocation has a fresh process. Define `$python` and `$nmsExe` in the same invocation, or use verified explicit paths. An undefined shell variable that prevents the tool from opening the executable is `TOOL ERROR`, not zero-reference evidence.

## Additional 22 October 2026 rule: connect indexed vectors to their parent constructor

When a UI method computes owner + index*stride, resolve the constructor and prove its entry count, stride and embedded subobject positions. Follow direct callers to see whether state and render roots receive the same parent pointer. This can establish that a resource path and a QAM share one parent while their child vectors remain distinct. Record the exact index expression and runtime values still unknown; do not infer that an entry is active because it contains the QAM. A same-range virtual-call field filter is a bounded candidate search, not proof that a dispatch or alias is absent.

## Additional 22 October 2026 rule: preserve virtual-call register identity

Track registers as separate states: owner/object address, object vptr, and method pointer loaded from a vtable slot. For `lea owner+offset`, preserve the embedded-object candidate; for `mov reg,[owner+offset]`, do not silently promote a pointer field to a class instance without constructor or RTTI evidence. At `call [vptr+slot]`, compute the slot from the vptr once. If the register already contains a method pointer, `call reg` uses that pointer directly; do not carry the former slot through a further memory displacement. Keep this scanner output as candidate discovery until the exact receiver and arguments are reconstructed.

Do not infer a virtual method's ABI inputs across a call. In particular, Win64 `R8` is volatile: an earlier `R8` or `R8D` assignment is not the later call's third argument after another call unless it is set again. A generic slot-zero call on an object at `owner+0x10` is not a QAM Update match without the QAM constructor-proven receiver, full chained `.pdata` group, and immediate argument data flow. A list-clearing loop that calls slot zero and slot one before resetting its count/storage is a teardown candidate, not an update proof.

For exact QAM caller hunts, start from its constructor-proven address and track the receiver through the complete unwind group and direct callers. A one-range embedded-offset scan may report bounded candidates or zero; it cannot carry provenance across chained fragments and cannot prove class identity. If the result depends on an indirect caller, use group-aware provenance and record the call-site `RCX`, `RDX`, `R8`, and any stack arguments after the last intervening call. Avoid repeating generic offset and ABI-shape scans after the exact owner is known.

In PowerShell, quote paths containing apostrophes with a double-quoted string or a safely constructed literal. A shell parse failure before the binary is opened is `TOOL ERROR`, not zero-reference evidence.

## Additional 22 October 2026 rule: validate group-aware call scans with positive controls

Before trusting a negative from a new `.pdata` group scanner, require it to reproduce at least one known call in the same address path. Keep VA and RVA coordinate domains explicit in CFG edges; a scanner that misses its known positive is `TOOL ERROR`, and its zero results are invalid. When some runtime-function ranges decode to no instructions, list their exact RVAs and byte total and mark their contents unclassified; do not silently count them as code scanned or as harmless data.

For an indirect Update candidate that accepts its object through `RCX`, first scan function-entry seeded slot-zero calls as candidates, then trace the direct callsites and derive `RCX` and `R8` there. Batch direct-target xrefs within the tool limit and preserve the candidate roots used. A generic `RCX` seed is not class identity; do not promote it to QAM until the constructor-proven child pointer is traced. Direct-E8 callsites do not cover indirect calls or cached function pointers.

When sharing analysis outputs across PowerShell commands in this sandbox, do not assume `$env:TEMP` is shared by separate invocations. Run the producer and consumer in one PowerShell process or use a unique repository-local scratch file, then remove that exact file after successful parsing.

## Additional 22 October 2026 rule: bound common-offset scans before using negatives

A full-image group-aware slot-zero scan seeded only by offset `0x10` touched 20,029 groups and hit the per-instruction state cap in 987 groups. Its eight printed candidate records (seven unique call RVAs) are leads only; the truncation makes the rest of the inventory `NOT CHECKED`. Do not treat the output list as exhaustive or raise the global state limit blindly. Narrow the next pass with the constructor-proven owner, indexed-base expression, exact receiver class, or a specific set of caller groups; require a same-path positive control before using a zero.

## Additional 22 October 2026 rule: classify argument-seeded call roots before promoting them

After an argument-seeded virtual-call scan, deduplicate by function group and batch candidate root RVAs through the literal preferred-image-base pointer scanner. Run RTTI-backed vftable validation on roots with exact data references, keeping the raw-reference count separate from validated vtable hits. Record the RTTI type and slot for every validated root. A vtable owner identifies the candidate function's class membership; it does not prove that the function's incoming object argument is the receiver at the internal call. Literal-pointer zeros exclude only that representation, and a zero RTTI result does not exclude relative, relocated, cached or dynamically built references. Keep these as candidate filters and return to exact QAM receiver/argument provenance before assigning Update semantics.

## Additional 22 October 2026 rule: immediate filters need opcode and dataflow context

`--require-immediate 0x6D0` selects any function group containing that number outside a memory operand. It also selects stack prologues such as `sub rsp, 0x6D0`, so the number alone is not evidence of an indexed menu stride. Inspect the opcode and operand role, then trace the value from the constructor-proven owner/index. In the recorded target pass, six of seven truncated roots used `0x6D0` as stack allocation; a seventh contained a repeated-subrecord loop whose class was unresolved. Preserve these as false leads/unclassified until owner evidence resolves them. Print and inspect truncated group roots instead of raising the state cap for the full image.

The Windows `py -3.11` launcher can report `No installed Python found!` while `Get-Command python` resolves to a working CPython 3.11.9 with the pinned imports. Check both launchers, use the explicit interpreter path when available, and record its hash and dependency versions. A failure before opening the PE is `TOOL ERROR`, never a negative search result; do not reinstall dependencies to repair a launcher mapping.
## Additional 22 October 2026 rule: classify indexed menu helpers separately from QAM dispatch

When a constructor-proven quick-menu entry is selected with `owner + index*0x6D0`, follow helper arguments at the exact callsite. A dword-zeroing or bitset set/clear helper on entry fields is menu-state handling, not an embedded QAM Update. A same-parent QAM slot 11 call is a valid QAM caller anchor but does not establish slot-zero Update semantics. Keep the full unwind group, selector branch, receiver, and slot explicit; stop only when the actual slot-zero caller and row-owner argument are established.
## Additional 22 October 2026 rule: direct-call zeros do not cover virtual calls

A zero E8-style direct-call scan of an RTTI-mapped method rules out only decoded direct relative calls in the scanned executable ranges. Keep vtable/cached/dynamic call paths `NOT CHECKED` and continue from the constructor-proven receiver. Do not record the direct-call zero as an absent virtual caller.
