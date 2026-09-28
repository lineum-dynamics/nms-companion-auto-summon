# Native quick-menu investigation

## Current status: running 0.8.4, source 0.8.6 unlaunched

The immutable running **0.8.4-play-trial** contains production **0.4.7** and menu
**0.8.3-settings-trial**. Two Mods and twelve native targets registered after a
verified backup. The player's screenshots confirm six distinct setting icons,
including station and Anomaly captions. Runtime logs show deliberate changes
to five control roles; complete navigation, all six controls, remapping,
controller and HUD icon acceptance remain incomplete.

The six existing preferences remain on a flat page: automatic summoning,
Last selected/Random, matching-biome preference, planets, space stations and
the Space Anomaly. Icons identify the setting role and remain stable when the
value changes. The caption carries the value; native white/gray highlights
indicate selection. English captions use sentence case and retain proper-name
capitalization (Space Anomaly) and ON/OFF tokens. No UI strings changed here.

Source **0.8.6** pairs menu **0.8.4-language-observation** with byte-identical
production **0.4.8** from 0.8.5 and retains the host compatibility checks.
It records bounded language observations only on owned CAS captions, using the
existing guarded reader and hook. It does not select a catalog or change text,
icons, settings, timing or summon behavior. The final `086-r1` bundle is not
launched. The developer panel remains until native controls
pass acceptance. [The live record](docs/research/LIVE-084.md) distinguishes the
failed Nexus startup from a later successful ship exit with another Random pet.

Each child is a uniquely marked None action with an explicit role. Full-page
validation requires exactly the six expected children; foreign/native content
and incomplete prior appends are never cleared or adopted. Native construction
and the original append trampoline remain in use. A deliberate, correlated
native confirmation queues only the selected preference through the existing
production instance/lock. Unrelated requests and the manual favourite survive;
pending and session-only captions do not promise a disk save. Mode cycles existing
values, the other five controls toggle, and all three locations may be OFF.
The biome row now says **Random: prefer matching biome: ON/OFF**; its behavior
remains effective only for Random on planets. Legacy source defaults retain the
one-child trial; the new bundle explicitly enables six rows.

The bundle includes `SETTINGS.DDS` for the parent and `AUTOMATION.DDS`,
`SELECTION.DDS`, `BIOME.DDS`, `PLANET.DDS`, `STATION.DDS` and `ANOMALY.DDS` for
roles 0..5. The launcher validates all seven exact hashes/headers and existing
destinations before closed-game staging under the unique CompanionAutoSummon
asset directory. Identical files are reused; unexpected files or redirects are
refused. Publication is atomic per file; packaging does not deploy.

The AFTER callback at the statically verified natural `LoadResources` phase
attempts each load at most once. All aligned records/path buffers are pinned
before resource calls, with one validated native paw retained for fallback.
No menu paw field or shared vanilla texture is replaced. Fresh dual-manager
and original-resource checks select each role's ready custom icon or the paw.
Observed manager transitions or recycled resources disable the provider;
partial registration failure stops remaining loads. There is no retry,
late-load or release path. The production HUD uses the parent icon only;
missing/invalid handles select the verified text-only HUD path.
The standalone production ZIP has neither custom asset nor native settings.

Offline helper checks cover six-role topology, stale preference captures,
unrelated queued writes, explicit icon allowlists and fallback ownership.
Final aggregate validation belongs in the candidate manifest. Screenshots from
0.8.4 confirm six distinct setting icons after native resource registration.
Parent/HUD appearance, teardown lifetime and full controls still need acceptance.
Test browsing without changes, each confirmed row, held
input, Back/reopen/rebuild, ordinary pets, saved values and remapped/controller
inputs. The optional icon must not become a prerequisite for automatic summoning.

### Requested next work: native number shortcuts and localization

Native number shortcuts are requested, but custom binding remains blocked.
The current tagged None action loses its marker during native serialization;
binding it over an existing shortcut can persist an empty action and lose the
previous binding. Keep the protective native binding guard until a verified
design covers binding, replay, removal, persistence and remapped native input.
Physical key hooks or parallel hotkeys are not the requested solution.

Fourteen draft/source catalogs and an offline text renderer are maintained.
The new language reader copies fixed scalars, double-checks stability and
reports initialization/load history without following native table pointers.
Its optional failures cannot disable the menu or automation. A known native
reload leaves the load-history flag set, so observations do not enable rendering.
UTF-8 decoding is verified statically for measurement and drawing; live glyph
coverage and catalog selection are not. Native text remains English. See
[LOCALIZATION.md](LOCALIZATION.md).

## Retained unlaunched predecessor: 0.7.2

The **0.7.2-play-trial** predecessor, with production **0.4.5**, has not
launched. It preserves native-menu preferences and the binding guard, while
restricting manual-favourite learning to a matched successful native companion
UI action. An unknown accepted queue cancels pending automatic intent but cannot
replace the favourite or announce a manual choice. Static battle-restoration
callers reach the queue directly; the specific 0.7.1 arena caller remains
unknown, and no previous favourite is rolled back.

Production adds a BEFORE/AFTER pair at the existing menu `TriggerAction` target,
RVA `0x1526940`, preserving its `bool(pointer, pointer, bool)` ABI and native
arguments/results. It copies action 46's slot/identity before dispatch, observes
one matching accepted local queue, and revalidates context after original
success without rereading the old action pointer. Nine production and eight
menu callbacks share eleven distinct managed targets. Actual pyMHF registry and
Python compound-dispatch checks passed both callback orders, four Boolean
combinations each and exactly one mocked original call. The menu was disabled
for that dispatch smoke; this does not prove active native coexistence in-game.

The candidate passed **279 production tests**, **408 developer tests**, real
GUI metadata/widgets and final two-Mod bundle/preference-bridge checks. The
PowerShell launcher parsed successfully. No native hook binding or game access
occurred. The running 0.4.4 / 0.7.1 folder remains unchanged.

### Prepared 0.7.2 HUD correction

Explicit notices request 5.5 seconds and distinguish saved from session-only
choices. Automatic summoning, repeated choices and game restoration stay quiet.
The eleven-argument `AddTimedMessage` ABI and owned text/colour/empty-icon buffers
remain unchanged. In the guarded executable, final argument 11 is stored at
message `+0x2DB`; the lower-message path passes it to renderer `0x6C1C30`.
True sets `IsHidden` on both `LARGE_ICON` and `ICON` containers, independently of
the already assigned `TITLE`. The zero-resource path can show background/glow
children, explaining why an empty icon handle alone did not remove the disc.
That candidate sets this verified final flag. The new 0.8.0 provider supplies
an owned ready icon when available and otherwise keeps this flag set.
This is static evidence;
readability and the actual disappearance of the white disc need a live check.

### Historical live trial: 0.7.1

Production 0.4.4 added passive post-queue diagnostics with the existing native
menu and a version-pinned bridge. It registered both Mods and 11 hook targets at 22:22:35 on 27 September
2026 after a fresh verified backup, with automation ON and unchanged
preferences/state. All 14 payloads matched. This does not establish visible
spawn or inherit the following 0.7.0 live results.

One Random-mode Anomaly startup is now confirmed for 0.4.4 / 0.7.1. On 27 September 2026, load arming at 22:23:39.698 led to native queue acceptance at 22:23:42.250 (logged 2.56 seconds). The new observer recorded the expected active companion at 22:23:42.266, on its first update, then stopped. The player confirmed visible appearance. No ship exit or automatic retry preceded this result. This is one successful run, not a fix for the earlier intermittent failure; only passive diagnostics changed.

Previous live trial: **0.7.0-play-trial**, containing unchanged
production 0.4.3 and an opt-in 0.7.0 native automation toggle. It passed 408
developer tests and real-framework discovery/temporary-preference checks.
It registered in-game at 21:48:38 on 27 September 2026 after normal exit and
a fresh verified backup of 43 profile files. Two Mods and 11 hook targets
loaded with automation ON. The player subsequently reported summoning on ship
exit when ON and no summon in a later OFF attempt. The screenshot shows OFF
in both the child caption and HUD; logs confirm queued and applied toggles.
The initial OFF report is ambiguous: the first logged exit followed another
ON change. Rapid toggles were confirmed as repeated presses, not held input.
Held input, remapping, controller and complete navigation checks remain pending.
The same session exposed a failed visible Anomaly startup despite native queue
acceptance, and a solid white disc above the HUD text. These remain open defects.
The following chronological records retain their original version boundaries.

Historical 0.4.3 / 0.6.2 snapshot, 27 September 2026: that candidate added a
deferred summon opportunity after local save load. Its combined 0.6.2 artifact
has passed offline checks and registered with automation ON. One Random-mode
startup summon on a space station is confirmed by the log and player; Nexus and
planet startup remain unverified. The player also confirmed one later manual
dismissal without reappearance. A separate,
disabled-by-default developer trial now implements one inert custom item and a
native binding filter. The player has confirmed visibility, selection, native
Back/close/reopen and ordinary manual pet summoning in that session. A separate
0.5.0-submenu-trial has confirmed inert-child navigation and clean captions.
The separate 0.6.0-order-trial inserts the parent before individual pets in
offline checks and has registered in-game; its visible ordering remains
unverified. The combined 0.6.1 play trial has registered with automatic
summoning ON so play can continue during menu development. Shortcut scenarios and
preference controls remain unfinished. This document separates static findings, offline verification,
live observations and future work. Raw disassembly is private working evidence,
not part of the repository or distribution.

## Verified static scope

The examined Windows Steam executable has SHA256
`b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`
(build 25442159 / Cosmos 7.04). Its hash was checked again for this investigation.
Addresses below are relative to that image, not universal game-version offsets.

| Finding | Exact-build evidence and limit |
|---|---|
| Action dispatch, RVA `0x1526940` | Receives menu pointer, action pointer and called-as-menu boolean; returns a boolean. Reads the action integer at action + `0x4`. Native dispatch handles actions 1 through 66. |
| Menu depth | A signed integer at menu + `0xA050`; ordinary submenu transitions clamp it to 2 beyond the root. Companion actions 45 and 47 use that transition. |
| Menu construction candidate, RVA `0x151ED00` | Called during the update/rebuild path; companion-specific branches were traced. This is not yet a live-validated hook or callable binding. |
| Action vectors | Start at menu + `0xA058`, one 16-byte header per depth: 32-bit capacity, 32-bit size and a data pointer. Item stride is `0xE0`. Do not manufacture or retain vector storage from Python. |
| Native append helper, RVA `0x1533980` | Copies `0xE0` bytes into native-owned storage and uses the game's growth path when needed. Its existence alone does not validate arbitrary item contents or lifecycle. |
| Basic item constructor, RVA `0x1432FC0` | Writes action at `0x4`, disabled state at `0x4C`, slot/index at `0x84`, a fixed 64-byte name at `0x98` and hotkey binding at `0xD8`. Full semantic validity remains a separate requirement. |
| Label builder, RVA `0x1523220` | Selects labels according to native actions. The item's fixed name is not a general custom-label fallback; an unknown/default action produces an empty label. |

Some other menu paths index action classification data without the dispatcher's
bounds check. Arbitrary new action integers are therefore unsafe. The current
enum also contains the Invalid sentinel 67; that is not a custom action slot.
Action 0 (None) has a valid classification entry and the dispatcher returns false
for it, making a separately tagged inert item a candidate for further study.
This is not permission to repurpose a vanilla gameplay action or proof that the
candidate works across rendering, navigation, hotkeys and menu rebuilds.

In particular, native hotkey binding can copy even a tagged None item into its
hot-action records. A disabled flag does not establish prevention. Binding,
replay, removal and game-managed persistence must be addressed before inserting
the first custom item, rather than treating them as a later cosmetic issue.

The follow-up static audit traced three context banks of ten hot-action records.
The game's save conversion writes the action integer unconditionally. Binding
None over an existing action can therefore save an empty binding; the custom
tag would not round-trip. Normal outside-menu replay ignores None's action
class, but that does not prevent the loss of the prior binding. No custom
binding was created in the live observation test.

A candidate prevention point was the native bind-modifier input query, scoped
to a verified tagged selection and its exact update context. That trace alone
does not establish coverage of remapped keyboard or controller actions. Never
turn the observed default Ctrl query into a general physical-key suppression
rule. The accepted requirement is item-specific protection at the native
binding operation, independent of the player's chosen input.

Hooking the global input query in Python adds callback overhead even to queries
the observer immediately rejects. The implemented candidate instead uses a
native leaf filter: unrelated callers go straight to the original trampoline,
before any menu read and without a Python callback. The earlier menu-local
phase observations remain separate evidence. Allowing a
binding and then restoring it, or modifying save serialization, is not the
chosen direction. The guard candidate's own-buffer evidence and remaining live
scope are described below; it is not yet a live-verified hotkey guard.

One proposed menu-local approach was ruled out statically: marking selection
invalid until the end of the update would reach a tail handler that navigates,
activates or closes the menu. Restoring after it could overwrite legitimate
changes. No selection masking was implemented or tested in the running game.

The update path rebuilds the action vectors before clamping selection and
copying items into the render state. A future insertion should use a verified
native construction point, not write directly into the render state's buffers.
Custom label display needs its own scoped, verified path.

## First diagnostic: observation only

`tools/quick_menu_probe.py` is a separate developer observer, disabled in source.
It is not imported by `build.py` and is not included in the player ZIP. Its single
before-hook observes naturally executed TriggerAction calls. It never calls a
native game function itself or changes the function's arguments or return value.

It copies only two four-byte integers: action ID and current depth. Reads use
Windows ReadProcessMemory with the current-process pseudo handle and must return
exactly four bytes. Inaccessible memory is an error, not a ctypes dereference.
The observer validates IDs 0 through 66, depth 0 through 2 and the boolean flag.
It stops on the first invalid/read-error observation or after 64 recorded events.
It records no pointer addresses, names, pet seeds, account IDs or save IDs, and
does not open game saves or the normal mod's preference files. Framework logs
still have their own standard diagnostic contents and should remain private.

No action pointer is retained or read after the native call: a call can rebuild
the menu and invalidate its old item storage. These scalar observations will not
by themselves validate vector ownership, label buffers or insertion safety.

The observer passed 24 offline tests. A real pyMHF 0.2.4 import/metadata check
confirmed one before callback, no GUI widgets/hotkeys and disabled behavior
outside the game, without registering a hook. Its Windows reader also copied a
four-byte value from a deliberately allocated buffer in the test host process;
no game process was accessed by that check.

The isolated observer subsequently loaded in NMS on 27 September 2026: the
framework log at 15:54:43 local time reports one mod and one hook. During the
player's natural-menu test at 15:58:27 through 15:59:37 local time it recorded:

| Native route | Observed action | Depth | Called as menu |
|---|---|---|---|
| Companion submenu | 45 | 0 | true |
| Summon pet | 46 | 1 | true |

The player confirmed opening the companion menu and successfully summoning a
pet manually. Ten observations were captured, also including native IDs 34 and
50 at depth 1; their meanings are not needed for this result. No observer failure
or limit notice appeared in this capture. The paged pet submenu (47) was not
observed. This establishes the two observed routes and the player's manual
summon result, not custom insertion, labels, vector ownership, hotkeys or all
navigation paths. Generated observer SHA256:
`67518f9a8edc8efb56869d6a6fa5667598c725016ffca8949dab20a58f893dd2`.

Two preceding host attempts stopped before game startup: an inherited module
environment left Windows PowerShell without Get-FileHash, and redirected standard
handles left prompt_toolkit without a console screen buffer. The successful
attempt used the existing PowerShell 7 host with a hidden console and without
redirecting its standard handles. Capture the framework's own log files instead.
This is local test evidence, not a claim of clean-machine launcher compatibility.

From the source checkout:

```text
python -B -m unittest discover -s tools/tests -p test_quick_menu_probe.py -v
python -B tools/build_quick_menu_probe.py --enable-observer
```

The action-stage builder writes only to a new `build/quick-menu-probe/` folder
and never launches, attaches, deploys or modifies the installed mod. It refuses
to overwrite any existing output folder, including a running diagnostic. Use
`--output-name quick-menu-new-trial` to retain an earlier artifact and create a
separate trial. It copies the existing guarded launchers
and emits a small diagnostic manifest. The generated script filename remains
`CompanionAutoSummon.py` to satisfy the guarded launcher's filename contract, but
its only Mod class is `CompanionMenuProbe`. Automatic summoning is absent in this
isolated diagnostic session. The original mod and its files stay separate.

## Second diagnostic: construction and labels

The second separate observer is `tools/quick_menu_structure_probe.py`, disabled
in source and excluded from the player package. It observes natural completion
of the builder and label functions with after-hooks that return None. All
observed direct callers pass two pointers and ignore their return values. This
static finding justifies the diagnostic declarations. The bounded live result
below covers natural menu use; neither function is called explicitly by the
observer.

This diagnostic reads bounded vector headers and selected action IDs after a
natural rebuild. It does not copy complete items or names. Selection clamping
occurs after construction, so an out-of-range selection is recorded as stale
without reading the item. Empty vectors are normal. Capacity/count must remain
within a conservative diagnostic ceiling of 256; exceeding it stops observation
and never changes a gameplay limit. Label observation copies at most the known
128-byte output, records only its NUL-terminated length, and never writes or
logs the text. Read errors or unexpected data stop observation.

Each callback channel samples at most four times per second and retains only
changed sanitized observations, capped at 2,048 samples or 32 detailed events
per channel plus a terminal summary. This
avoids consuming the detailed log budget on identical rebuilds before the
player reaches the menu. Callback counts, elapsed time and anonymous callback
thread comparisons support later lifecycle analysis; they do not prove that
all callbacks run on a particular engine thread.

```text
python -B -m unittest discover -s tools/tests -p "test_*probe.py" -v
python -B tools/probe_framework_smoke.py --stage structure
python -B tools/build_quick_menu_probe.py --enable-observer --stage structure
```

This writes a new `build/quick-menu-structure-probe/` artifact; it never overwrites
the first observer or changes a running game. The source passed 37 focused
offline tests, including pointer/read bounds, throttling, independent budgets,
stale selections, label termination and callback preemption. Together with the
24 first-observer tests and five builder tests, all 66 checks passed. Independent
review confirmed the timestamp ordering fix; no live-test blocker remained
within the read-only scope. No custom entry is inserted, and automatic summoning
remains absent from the separate observer session.

Run the framework smoke command with the prepared pyMHF 0.2.4 interpreter. It
inspects disabled source metadata and copies only deliberate buffers owned by
its own test host. It does not register hooks or read the NMS process.

The real pyMHF 0.2.4 check passed for source SHA256
`83bcd6a01e7b4be7e8ba90f54f0f4b73b06c9ec33080a68af3252e0614f4d28a`:
one disabled Mod class, two AFTER callbacks with the audited two-pointer/void
metadata, no widgets/hotkeys, and successful 4/16/128-byte owned-buffer copies.
The separate generated observer SHA256 is
`d752066c87aafb1a10893a8b779e8009bc0a26c85b8dd38963e2430e28405b97`.
Its launcher passed PowerShell syntax validation. After normal game exit and a
fresh verified backup, it loaded in NMS at 16:15:24 local time on 27 September
2026: the framework reports one mod and two hooks. No observer artifact was
replaced while the game was running.

### Captured construction and label result

The player reported completing the requested navigation sequence, with no
specific issue reported. The retained 16:16:22.716 through 16:16:40.064 capture
contains 28 changed builder snapshots and 25 changed label snapshots. The last
recorded counters reach 926 callbacks and 64 sampled reads in each channel;
identical samples are deliberately not logged, so these are recorded counters,
not a claim about totals for the entire session.

- Root and companion depth 0/1 transitions were captured, including selected
  companion parent 45 and summon action 46 at several pet indices.
- Root and companion lists each had eight items with capacity 18 in this
  capture. The unused depth-2 list was empty; paging through depth 2 remains
  unverified.
- Recorded label lengths were 0, 5, 9, 10, 12, 13, 14, 15 and 18 bytes, all with
  a NUL terminator inside the bounded 128-byte copy. No text was logged.
- All recorded callback thread comparisons were equal. During continuously
  open-menu segments the counters advanced at about 60 callbacks per second,
  while the observer sampled no faster than four times per second.
- No observer failure or budget-limit notice appeared in this capture.

This supports the observed layout and natural completion paths on the guarded
build. It does not establish text correctness, every thread/path, mutation
safety, allocation, custom labels or a working settings item. Binding protection
remains the next prerequisite before inserting an inert entry.

The next bounded investigation is menu-local sequencing around controls
generation, the binding block and the tail selection handler. An observer must
preserve all arguments/results, never mask selection or change input state,
and reject ambiguous/reentrant phase records. If native thread identity is
needed across ctypes callbacks, use an explicit bounded invocation map;
`threading.local` is not a reliable store for callbacks from foreign threads.
Sequence observations would not by themselves prove safe mutation or coverage
of remapped controls.

## Third diagnostic: menu-local phases

`tools/quick_menu_phase_probe.py` is the separate, disabled-source observation
stage for that sequence. It uses four callbacks on three native routines:

| Routine | Callback | Audited argument contract |
|---|---|---|
| Quick-action update, `0x151D200` | BEFORE and AFTER | menu pointer, elapsed float, render-state pointer |
| Controls text, `0x1530C00` | AFTER | menu pointer, render-state pointer, render state + `0x100` |
| Tail selection processing, `0x1525600` | BEFORE | menu pointer, render-state pointer |

All three diagnostic declarations use void return and every callback returns
None. No routine is called by the observer. The controls callback does not read
either text buffer: their identities only verify the expected invocation.

The exact-build RTTI/vtable and a virtual caller support Update's menu/float/
render contract; its scalar arithmetic uses single precision and the caller
ignores its return. Controls also has a virtual slot, so the known direct call
does not exclude other contexts. The observer must report an unmatched callback
as unsupported sequencing rather than assume that every call belongs to its
current update.

An explicit bounded record keyed by native thread ID connects one update entry,
controls completion, tail entry and update exit. Pointer identities are retained
only for comparison inside that invocation; each memory copy uses the fresh
menu argument supplied to the current callback. No pointer or thread ID is
logged. Sampled observations compare depth, bounded vector headers, selected
indices and selected action IDs. Internal vector storage identity comparisons
are emitted as booleans, never addresses.

An update that returns without controls or tail processing is counted as
skipped, not as a broken sequence: the native hot-action replay path can return
early before controls. Changes made by the tail handler before update exit are
also normal observations. Duplicate, unmatched, mismatched, nested or concurrent
sequences must not be reported as balanced. Ambiguous sequences, failed reads
or lock contention stop this diagnostic and clear its transient records.

Sampling begins at controls completion, at most four sampled invocations per
second. Closed-menu/skipped updates do not use the sample or detail budgets.
Limits are 120,000 update entries, 2,048 completed samples and 32 changed detailed
records, with a bounded terminal summary. These are observer budgets; they
change no native game limits. No input function is intercepted or called, no
physical keys are inspected, and no selection masking or shortcut write occurs.

```text
python -B -m unittest discover -s tools/tests -p "test_*probe.py" -v
python -B tools/probe_framework_smoke.py --stage phases
python -B tools/build_quick_menu_probe.py --enable-observer --stage phases
```

The isolated output is a new `build/quick-menu-phase-probe/` folder. As with the
earlier stages, creating this artifact does not launch or deploy it. The phase
stage passed 34 focused tests; the combined tool suite passed 101 tests (24
action, 37 structure, 34 phase and six builder checks). Review identified an
interrupted-entry cleanup race; the corrected source clears retained identities
on stop and has regressions for contention during clock/thread lookup and exit.
Do not alter a running diagnostic.

The real pyMHF 0.2.4 check verified one disabled class, four callbacks on three
native targets, the audited ABI metadata, no GUI/hotkeys and owned-host-buffer
copies of four and 16 bytes. Final source SHA256:
`1a80c82773367ffb80d45e8498e52c6139fe410de71e7e9eefcb425f6c38d73a`.
Generated isolated observer SHA256:
`9cbf0e6c647bb53ee3c84decd4dff996fa31053ed4c6ee88a29fb81273d6f24e`.
The generated launcher passed PowerShell syntax validation. After normal game
exit and a fresh verified backup, the isolated phase observer loaded at 17:57:41
local time on 27 September 2026. The framework reports one mod and three native
hooks, containing the four audited callbacks. The previous observers and the
production mod retained their previous hashes.

### Captured phase result

The player reported that the native menu worked so far and noted the absence
of the mod item. That absence is expected: the observer adds no item, settings
action or automatic summoning. Explain this distinction before subsequent
trials rather than describing an observation-only test as testing the mod menu.

The retained capture from 18:01:16.196 through 18:02:11.857 contains 22 changed
detail records, with the last recorded counters reaching 749 update entries
and 52 completed samples. All recorded phase details used anonymous thread
ordinal 1. Controls-completion and tail-entry snapshots matched, including all
three vector-storage identity comparisons. No interval change, post-tail change
or observer-stop notice was recorded in this capture. The absence of a recorded
post-tail change does not verify the handler's other activation/navigation paths.

This establishes successful natural phase observations for the tested sequence.
It does not establish exclusive ownership, every concurrent reader, recovery
after a failed mutation, remapped/controller binding coverage or a custom item.
At this checkpoint the next target was an inert visible entry with binding
protection. The source candidate below was subsequently implemented using a
native filter, without temporary selection masking. The phase observations
alone did not establish the safety of a mutation or input interception.

For a live trial, open the companion menu with the player's configured control,
move among native entries, back out and reopen it. Normal activation/dismissal
can exercise the tail handler; no shortcut reassignment is required. Default
keyboard input alone does not verify remapped or controller paths. A balanced
trace establishes the observed ordering and identity only; concurrency,
mutation recovery and binding-path coverage remain distinct prerequisites for
a custom item.

## Inert-item candidate, first visible result captured

The separate `tools/quick_menu_item_trial.py` source is disabled unless an
explicit isolated build enables it. It uses two AFTER callbacks: native item
construction and label completion. Its sole entry is **Companion Auto Summon**,
with the borrowed companion icon, an ASCII label, native None action 0 and a
complete private 16-byte marker. Activating it intentionally changes nothing.
It is not connected to preferences or automatic summoning.

`quick_menu_item.py` supplies bounded, independently testable inspection and
construction policy. It appends only at depth 1 beneath native companion action
45, rejects duplicate/ambiguous markers, rechecks the current vectors and icon,
and requires an active guard before construction and again before append. Native
constructor/append adapters use 16-byte-aligned temporary buffers and the game's
own allocator. They do not replace vector pointers or retain item pointers.
The label callback writes only the audited 128-byte output for the selected
tagged entry. Errors and overlapping callbacks stop further insertion; they do
not unload the native guard or try to roll back native storage.

`quick_menu_native_guard.py` emits original Win64 leaf code. It checks the real
stack return address against the exact binding-query return site `0x151DDEB`
before reading RDI. At this site RDI is the live menu throughout the native
Update invocation; the preceding controls call has returned and no native call
intervenes. The filter validates depth, signed vector counts/capacity, selected
index and the complete None+marker identity. Only that item returns false for
the native binding query; every other call tail-jumps to the original trampoline
with the original arguments, nonvolatile registers and stack intact. No physical
button is assumed, no Python callback handles unrelated inputs and no selection
field is masked. Existing tagged items remain protected after vector capacity
growth; the insertion helper's diagnostic budget is not a filter limit.

The leaf's direct reads rely on that synchronous native object's lifetime.
Bounds are not a general memory-validity guarantee. A static review found no
additional selected-item-to-primary-binding writer in the examined bank-accessor
callers and load/export paths. Replay separately refreshes cached submenu paths;
those paths are not serialized as primary bindings, but replay compatibility
still needs a targeted live test. Do not claim that all runtime-bank copies pass
through this filter.

`quick_menu_guard_runtime.py` verifies the exact executable, current injected
process, framework versions and unmodified target prefix before installation.
Its raw cyminhook integer-address detour bypasses Python on input calls. It
checks the installed target, relay, complete 19-byte original trampoline and RX
filter bytes before authorizing insertion. The hook and executable allocation
are pinned to the process before activation and have no removal/free endpoint.
Failed installation is retained and cannot be retried in that process. This
prevents callback failure or module reload from freeing a still-needed guard.
Unsupported or competing hook layouts refuse insertion. Later third-party hook
changes and hot reload are outside this isolated trial's support scope.

All 184 diagnostic/developer tests pass: 101 retained observer checks, 26 item
policy checks, 26 guard-runtime checks, 24 item-trial checks and seven isolated
builder checks. The actual cyminhook 0.1.6 native smoke passed 45 cases and 10,000
repeated calls against buffers allocated by its own Python process. It verified
the integer detour, full marker checks, forwarding from unrelated call sites
even with an invalid menu argument, unchanged data, the complete original
trampoline layout and successful test-hook removal. This is not NMS execution or
multiplayer/remapping verification. The
real pyMHF metadata smoke separately confirms disabled initialization, normal
Mod initialization, two AFTER callbacks with the audited ABI and no GUI or
physical hotkeys, without installing a game hook.

```text
python -B -m unittest discover -s tools/tests -p "test_*.py" -q
python -B tools/native_menu_guard_smoke.py
python -B tools/item_trial_framework_smoke.py
python -B tools/build_quick_menu_item_trial.py --enable-inert-item
```

Use the prepared exact framework interpreter for the two smoke commands. The
builder creates a new `build/quick-menu-inert-item/` folder, verifies copied
bytes and refuses to replace an existing output. Its launcher checks every
helper's hash in addition to the main script/bootstrap. It never launches NMS,
attaches to it, changes the running observer or deploys the regular player mod.
All trial files remain excluded from the player ZIP.

The prepared isolated artifact contains eight files and passed launcher syntax
and byte readback checks. Generated trial script SHA256:
`c5693f2652fc2cce3fe06904619d58d7bedb1181d899274de477d738e4a3ee39`.
The source entry, item helper, native filter and guard-runtime hashes are retained
in the metadata report and the generated manifest. A file-only check confirmed
the exact installed executable and target PE mapping. The production script
and the still-running phase observer retained their earlier hashes throughout
preparation; no running artifact was changed.

The live trial begins after normal game exit and a fresh verified save
backup. Explain explicitly that an inert item should now be visible, while
settings and auto-summon are absent in this isolated session. First check
companion-menu display, selection, back/close/reopen and neighboring native
actions. Do not rebind an occupied shortcut during that initial display test.
Existing shortcut replay, binding protection, remapped/controller controls,
save/reload/removal and mod coexistence are separate acceptance scenarios before
preferences or a release claim. Do not hot-reload this developer trial.

### Initial runtime registration

After the player closed NMS normally, a fresh backup of all 43 profile files was
created at 18:44:59 local time on 27 September 2026. The source remained stable
during copying and every copied SHA256 matched. Independent preflight verified
all seven payload hashes, the eight-file inventory, committed helper/source
identity and unchanged production code.

The new isolated session started at 18:46. Its log at 18:46:26 confirms the inert
trial's native binding filter was installed, followed by one Mod and two managed
framework hooks. The native filter is separately owned; it is not one of those
two framework hooks. No initialization error appeared in this startup capture.
This establishes exact-build runtime registration only. The player has been
asked to inspect the new entry, neighboring actions and close/reopen behavior;
visible rendering, navigation and shortcut behavior remain unverified here.
The generated artifact and its original manifest remain unchanged while running.

### First visible result

The native append/readback logged success at 18:47:58.099, and the scoped label
callback logged its first supplied label at 18:48:03.059. The player subsequently
confirmed seeing the item in the companion menu, at the end after the individual
pets, with a paw icon and moving text inside the icon. No insertion-stop/error
notice appears in the retained capture. This confirms visible insertion and the
reported presentation, not the full navigation, binding or replay scenarios.

End placement follows the prototype's native append operation. The paw is the
borrowed native companion icon. The running 0.4.0 helper fills the item's inline
64-byte name as well as supplying the separate selected-item label through the
128-byte label callback. There is no custom scrolling animation or overlay in
the mod. A follow-up exact-build static trace confirmed that the renderer finds
the tile's NAME element and supplies item + 0x98 to its text path; an empty first
byte skips that name path. Thus the populated inline name causes the tile text.
The exact scrolling timer was not traced. The subsequent 0.4.1-inert-item-trial
source leaves all 64 inline-name bytes empty while retaining the independent
selected-label callback. This cosmetic change passed the 50 affected item/trial
tests, seven builder tests and the real disabled-framework metadata check. It
has not been built into a new trial or deployed. Its appearance and a possible position before the
individual pet entries are presentation decisions, not changes already applied
to the running trial. No live file has been modified for this feedback.

The attached screenshot additionally confirms that the normal caption already
displays the full name below the tile, so the moving tile text is redundant.
The user asked about an original icon and a settings submenu. One flat settings
page is the intended behavior; it is not implemented by the inert test. A custom
icon concept is saved as an opaque design preview under `assets/concepts/` in
the source repository, outside the player ZIP. Transparent generation attempts
were rejected for visible artifacts; the preview is not a usable game texture.
Native texture registration and lifetime remain unverified. The existing native Utilities resource was located,
but its pixels were not inspected and it must not be described as a verified
gear icon. No existing shared game texture has been replaced.

### Basic inert-item navigation confirmed

The player subsequently confirmed selecting the mod entry, returning with
native Back, closing/reopening the menu and manually summoning a companion all
worked normally. All seven running payload hashes still matched the original
0.4.0-inert-item-trial manifest. This result does not cover shortcut binding,
replay, remapped controls, controllers or a custom subpage. The separate private
navigation record retains this distinction; no running files were changed.

## Inert submenu candidate: offline preparation

`tools/quick_menu_submenu_trial.py` is a separate, disabled-by-default
0.5.0-submenu-trial. Its entry opens a single inert **Settings preview** child.
No preferences, summon logic or custom texture are included. Both inline tile
names are empty; ordinary selected-item captions supply the text. The original
0.4.0 running trial remains immutable.

The exact-build dispatcher normally obtains its item pointer from the current
vector and selected index. The paired BEFORE/AFTER callbacks preserve native
arguments and execution for every action. They correlate transient numeric
arguments and native thread identity; only an exact selected parent with the
full marker, role and valid prebuilt child can request a transition. No action
pointer is dereferenced after native execution. Nested/unmatched callbacks or
changed context stop custom handling while retaining the binding guard.

The native None action and native submenu actions both return false. Returning
true would close/back in the inspected caller, so these callbacks always return
None to preserve the native result. They use neither NOOP nor manual forwarding
to the original function, and do not inspect physical keys.

The builder bounds-checks the temporarily absent appended parent before reading
it. An AFTER helper can therefore restore the parent at depth 1 and prebuild the
single child at depth 2 before native maintenance runs, including while the
parent is selected at depth 1. Every append uses the native allocator, checks
the active binding guard and reads back fresh storage after possible growth.
Nonempty unknown child pages are never cleared or adopted. Both roles retain
action None and the exact marker protected by the existing native leaf filter.

Activation requires no outstanding native deferred selection. Because the sole
enabled child already exists, the adapter writes depth 2 and invokes the native
bounded selection setter at `0x150FAC0` with `(menu + 0xA050, 2, 0)`, then reads
back the selection. The native pending-selection byte at `0xA16C` is never
written by this trial. This avoids a deferred request leaking into another page.
Depth animation uses the separate native previous-depth path. Native Back,
close, selection clamping and empty-page retreat remain in control.

If native pet counts change, a formerly selected index can become a vanilla
entry or become invalid. The helper uses the current complete path/roles, leaves
native descendants intact and lets native maintenance handle invalid/empty
pages. It does not force a remembered custom session back over a native page.
This is bounded to an inert child; it is not validation of future preference
actions. After a partial operation/error, insertion stops without freeing the
guard or rolling back native allocations. A prepared child remains inert and
native Back remains available in the inspected path.

All 255 developer tests passed, including 28 submenu-policy checks, 32 adapter
checks and 11 isolated-builder checks. The real pyMHF 0.2.4 metadata smoke
confirmed one disabled Mod, four callbacks across three native function targets,
no GUI/hotkeys and no hook installation. Its Python dispatcher was also exercised
with three mock-original cases to verify argument/Boolean preservation. These
checks do not establish live submenu behavior.

```text
python -B -m unittest discover -s tools/tests -p "test_*.py" -q
python -B tools/submenu_trial_framework_smoke.py
python -B tools/build_quick_menu_submenu_trial.py --enable-submenu
```

Use the prepared framework interpreter for the metadata smoke. The builder
checks source syntax and all copied hashes, refuses existing output directories,
and never launches/deploys. The prepared nine-file artifact passed eight payload
hash checks and launcher syntax validation; generated main SHA256:
`017cca120ec65fa5e442d430489758664ed5eb52a4e1e6a44d291e8ad657f5d9`.
Its first runtime registration is recorded below. Before any new live session,
exit normally and verify a fresh backup. Test opening the parent,
seeing/activating the inert child, native Back
to the parent, repeated open/close, absence of duplicates and neighboring manual
pet actions. Remapping, controllers, shortcut binding/replay and changing pet
lists remain separate acceptance scenarios. None's classification does not
provide every vanilla submenu-preview affordance; do not patch global action
tables or borrow a gameplay action ID for cosmetic parity.

### First submenu runtime registration

After the player closed the previous trial normally, a new backup of all 43
profile files was created at 19:41:01 local time on 27 September 2026. Source
files stayed stable during copying and every backup hash matched. Independent
preflight confirmed the nine-file inventory, all eight payload hashes and exact
identity with the committed source, apart from the intended trial enablement.

The new isolated session started at 19:41. Its 19:41:52.878 log reports the
submenu trial and native binding filter ready; at 19:41:53.004 pyMHF reports
one Mod and three managed hooks. These three native targets contain four
callbacks; the separate native binding filter is not included in that count.
An initial framework warning reported no window handle. A later process check
found a nonzero window handle and a responding game; this does not itself prove
the framework refreshed its cached handle or any menu behavior.

This establishes runtime registration only. The player has been asked to open
Settings preview, activate the inert child, use native Back/close/reopen and
check ordinary pet actions. Visible behavior was still pending at this startup
checkpoint. All eight payload hashes still matched; the running artifact was unchanged.

### First visible submenu result

The trial logged parent insertion at 19:42:40.404, a supplied caption at
19:42:41.590 and the requested submenu transition at 19:43:06.723. The player
then confirmed that the child appears, its activation remains inert, native
Back/close/reopen work and ordinary manual summoning still works. Two supplied
screenshots show the parent and Settings preview captions below native paw
icons, with no duplicated inline name. No stopped-submenu notice appears in
this retained capture. All eight payload hashes still matched.

This is a successful bounded visible/navigation result for this isolated
version. Custom texture loading, preference actions, changing pet counts,
shortcut binding/replay, remapping and controllers remain separate checks.
The user requested the entry before individual pets, after general companion
actions. The current running trial still appends it last; its order was not
changed live.

### Custom icon follow-up

A separate static audit found a current native texture-loading wrapper and its
resource retain/release path. Historical shorter loader declarations do not
match the current callback-object ABI. No custom loader was called and no
shared vanilla texture was replaced. An original SVG and transparent 256-pixel
PNG/RGBA32 DDS now exist under `assets/ui/`; independent decoding confirms
identical PNG/DDS pixels and transparent, opaque and antialiased regions.
Path acceptance, actual resource readiness, lifetime and in-game appearance
remain unverified. The submenu trials continue to borrow the native icon.

## Ordered submenu candidate (0.6.0)

The disabled source `tools/quick_menu_order_trial.py` retains the inert parent
and child behavior of 0.5.0. During a paired native BuildActions invocation it
inserts the parent immediately before the first depth-one pet or page append
(actions 46/47), after general companion actions. With no pets/pages, the
existing builder-completion path appends it after the general actions.

A late vector rotation was rejected: the next native rebuild can otherwise
interpret the selected custom index as a real pet before the late correction.
Early construction keeps the rendered order and native selection order equal.
No index remapping, native item replacement or additional scalar write is used.

The new append callback requires the active builder, native thread and exact
companion-vector header. The helper rechecks context and the unchanged incoming
item around construction; it rejects source overlap with any vector allocation
and a missed first pet. Every custom append uses the current managed original
trampoline. The resolver verifies ownership, ABI, enabled state and callback
lists, rejects the patched entry address and refuses a changed trampoline.
Returning None preserves the incoming native arguments and original result;
the original pet append still executes once. The pinned binding guard remains
unchanged and outlives stopped callbacks.

All 309 developer tests passed (including 17 ordering-policy, 26 adapter and
11 new builder tests). The actual pyMHF 0.2.4 disabled-import check discovered
six callbacks across four targets and passed five mocked dispatch cases
(the dispatch-only case uses a synthetic menu snapshot).
These checks do not install hooks in NMS or prove live behavior.

`tools/build_quick_menu_order_trial.py --enable-order` creates a new isolated
ten-file artifact with nine hashed payloads and refuses an existing output.
The prepared artifact is `build/quick-menu-order-trial`; it has not been
launched by its builder. The builder does not launch, deploy or alter the prior
0.5.0 trial. The regular player
mod remains 0.4.2; this trial has no automatic summoning, preference actions or
custom texture loader. Start only after normal game exit and a fresh verified
backup. Check the new position, submenu entry/Back/reopen, neighboring pet and
page actions and duplicate prevention. Hotkey replay/binding, changing pet
counts, remapped controls, controllers and callback cost remain separate checks.

### Ordering trial startup

After the player confirmed normal game exit, a fresh backup of 43 profile files
was copied and hash-verified. The isolated 0.6.0 launcher started at 20:05:49 on
27 September 2026. At 20:05:58 the log reported its binding filter initialized
and one Mod/four managed hooks loaded. The later process check found a
responding game window; an earlier framework window-handle warning does not
establish whether its cached handle was refreshed. All nine payload hashes
remained unchanged. Visual ordering/navigation is still a player check.

This session is menu-only. The player subsequently requested that automatic
summoning remain available during menu development. The next candidate must
combine the unchanged working runtime and existing external preferences with
the isolated menu trial, using the framework's supported mod-folder route.
Do not concatenate the scripts or assume imported Mod aliases are discovered.

## Combined play trial (0.6.1)

The isolated play bundle uses the framework's mod-folder loader to keep
`CompanionAutoSummon` 0.4.2-experimental and `CompanionMenuOrderTrial`
0.6.0-order-trial in separate modules within one host. The production file and
original injection-guard bootstrap are copied byte-for-byte. Only the menu
source's explicit enable flag changes in its generated copy. The regular
installation and previous trial artifacts are not overwritten.

Production has seven callbacks across six native targets; ordering has six
callbacks across four other targets. The binding filter is a separate pinned
native hook. There is one automatic-summoning instance and preference writer.
The menu still opens only Settings preview; actual controls remain in the
visible CompanionAutoSummon development panel.

The new host validates every declared payload, the exact folder configuration
and the Python discovery set before loading the unchanged injection guard.
It calls the installed framework's public `run_module(folder, config)` with
no plugin name; this selects MOD_FOLDER. The 0.2.4 CLI folder route enters a
different library/configuration flow, so it is not used. Extra registered
framework libraries are rejected for this bounded trial.

Both preference paths remain absolute under `%LOCALAPPDATA%/NMS-AutoPet`,
independent of the bundle folder. Neither building nor launching copies,
resets or migrates those files. Production retains its normal preference and
manual-selection persistence during play. No private preferences, selection
identities or game saves are included in the bundle or repository. Native
ownership, eligibility and placement rules remain unchanged.

The new thirteen-file artifact `build/quick-menu-play-trial` has twelve hashed
payloads. All 341 developer tests passed, including 15 combined-builder and 17
folder-host tests. The real pyMHF 0.2.4 smoke validated actual folder discovery
of exactly two Mods, thirteen callbacks/ten distinct targets, eight production
GUI widgets and zero physical hotkeys. Discovery-only disabled flags were
restored before construction; no native hook was registered. Temporary
preferences were preserved. The real user's two external configuration files
also remained hash-identical through packaging. The generated PowerShell
launcher parsed successfully, and every payload matched its manifest and
framework report.

### Combined startup

The player closed NMS normally. A fresh backup of 43 profile files was copied
and hash-verified before starting this bundle. At 20:16:10 on 27 September 2026,
the log reported production automation ON, the ordering binding filter ready,
and two Mods/ten managed hooks loaded. A subsequent process check found a
responding game window. The framework's earlier window-handle warning does
not prove its cached handle was refreshed. All twelve payloads and both
external preference files remained hash-identical at the startup capture.

This establishes combined registration with automatic summoning enabled.
The player's next ship exit and menu navigation must still confirm actual
coexistence and the new visible order. Neither the inert native child nor the
custom image is a finished preference control.

## Startup summoning in the combined 0.6.2 candidate

The player reported that loading directly on foot, for example in the Nexus,
did not trigger automation. This matches 0.4.2: only a ship exit armed the
policy. Production 0.4.3 now records one opportunity after successful local
save deserialization and handles it in later local ownership callbacks. It
waits for a supported enabled location, verified ownership and the existing
native placement/timing path. Native operations are never performed by the
load callback. The opportunity is consumed before arming; absence alone cannot
re-arm it after manual dismissal. Settings changes and normal manual/context
cancellation rules remain effective. No new native target or offset is used.

Combined play trial 0.6.2 copies that production script and the unchanged
0.6.0 menu into the new folder `build/quick-menu-play-trial-062`. The previous
running 0.6.1 folder remains hash-identical. All 230 production tests and 341
developer tests passed. Actual framework checks confirmed the production GUI
and the combined discovery of two Mods/ten distinct native targets without
registering hooks or accessing NMS. The new thirteen-file artifact's twelve
payloads and PowerShell syntax passed preflight. It subsequently registered
and passed one station startup check in Random mode and a later player-reported
manual dismissal without reappearance. Planet/Nexus startup and broader
regression remain to be checked.

### Combined 0.6.2 startup

After normal game exit, a fresh backup of all 43 profile files was copied and
hash-verified. The new isolated host launched at 20:42:12 on 27 September 2026.
At 20:42:21 the log confirmed production 0.4.3 automation ON, the menu binding
filter initialized, and two Mods/ten managed hooks loaded. A subsequent check
found a responding game window. The initial framework window-handle warning
does not establish whether its cached handle refreshed. All twelve payloads
and both external preference files remained hash-identical at startup.
Registration alone does not confirm a visible companion, dismissal behavior,
menu order or a completed startup summon. The running artifact stays unchanged.

### Confirmed station startup summon

At 20:42:58.578 the log armed one opportunity from local save load with location
2 (SpaceStation). Native ownership eligibility initially rejected the request;
the existing paced checks waited. At 20:43:01.260 Random selected slot 1 from
five eligible owned companions, followed by an accepted queue request at
20:43:01.261, approximately 2.69 seconds after arming. This is queue timing,
not measured visible appearance latency. No ship-exit arming precedes that startup request. A later ship exit
at 20:44:27.717 is a separate event in the retained log. The player confirmed that the companion actually appeared
and clarified that the location was a space station, not Nexus. All twelve
artifact payload hashes remained unchanged.

This verifies one station startup in Random mode. Nexus/planet startup, Last
manually selected startup, manual dismissal, biome preference, multiplayer and
the remaining menu behavior are not established by this observation. The
private evidence is retained as `menu-play-0.6.2-station-startup-success.json`.

### Player-confirmed manual dismissal

Later in the unchanged 0.6.2 session, after traveling, the player reported that
the companion was dismissed and did not reappear. The suggested check was to
remain on foot for about ten seconds. Exact location, dismissal timestamp and
duration were not independently established. This confirms the reported
no-repeat outcome once; it does not establish dismissal immediately after the
initial station load or all dismissal/trigger combinations. The retained log
is supporting session context, not a timestamped dismissal trace. Evidence:
`menu-play-0.6.2-manual-dismissal-success.json`.

## First native preference candidate: 0.7.0

The ordered adapter retains its original six callback phases when the new
`SETTINGS_TOGGLE_ENABLED` source flag is false. Both that flag and the ordinary
trial flag must be explicitly enabled by the isolated combined builder. The
new bundle contains 15 files, with 14 hashed payloads, two Mods, 15 callbacks
across 11 managed native targets, eight temporary development-panel widgets
and no physical hotkeys. The existing native binding filter is unchanged.
Production 0.4.3 and the canonical injection bootstrap are byte-identical.

### Native confirmation boundary

Static inspection of the pinned executable verified a boolean `(menu*)`
predicate at RVA `0x15311C0`. The native menu-manager calls its virtual slot
`+0x30` at `0x1535186`; a true result immediately leads to selected-action slot
`+0x38` at `0x1535193`, with the same menu and no intervening native call.
For the custom None action, the predicate's alternate-input byte table at
`0x4A23330` has value zero. Its ordinary-device branch therefore accepts only
native input query `0x53`, through the game's input object and existing mapping;
the alternative `0x55` query is skipped. These are internal native actions,
not physical keyboard keys. A separate device-type-four branch still requires
its own live coverage. No input function is called or replaced by the toggle.

The tail handler's slot dispatch is not used as authority. Its slot value four
must not be confused with a logical confirmation action. Likewise, the trigger's
called-as-menu flag and original false result alone do not prove a confirmation.
The pyMHF caller-address helper was not used: its shared captured stack address
cannot establish per-invocation provenance under concurrent entry.

The adapter observes all predicate results, including parent navigation. It
requires a false result for the same menu before a fresh true result. Holding
confirmation while opening the submenu therefore cannot arm the child. A
fresh true result captures owned selected-child topology and a one-use
preference token on the current native thread. Only the next matching trigger
can consume it. Intervening labels/builds/other triggers invalidate it; nested,
concurrent or mismatched callbacks stop custom menu processing. Tail-only or
unmatched triggers remain inert. Native arguments and return values are never
replaced, and the old action pointer is not dereferenced after execution.

After the original false result, fresh topology, current native guard,
deferred-selection state and preference ownership must still match. A final
non-native authorization check runs immediately before queuing. Revocation or
an unavailable/stopped/replaced production instance leaves preferences alone.
This is a bounded candidate, not verified support for every input/device path.

### Shared preferences and display

The bridge resolves the actual registered `CompanionAutoSummon` instance from
`mod_manager.mods`, with the existing module/class/sibling-path and reviewed
0.4.3 contract. String indexing on the manager would return a proxy and is not
used. No duplicate production module or instance is created. Only the existing
`requested_preferences["enabled"]` entry is changed under `control_lock`;
the established production player callback applies and persists it later.
Other queued settings and the remembered companion are preserved. Stale
enabled requests, replaced/applied queues and stopped/replaced instances refuse
the old token. Hot reload is unsupported; 0.4.3 has no revision counter to
distinguish identical writes within one queue.

The child caption is `Automatic summoning: ON/OFF`, with pending, session-only,
unavailable or stopped state when appropriate. The parent caption, empty inline
names, native icon and ordered insertion remain. A queued request is not
displayed as a confirmed disk save. OFF cancels waiting automation without
dismissing an active pet; ON alone creates no summon. Other controls remain in
the temporary development panel. That panel will leave the player interface
when the complete native settings page has been implemented and verified.

### Offline validation and next live check

All **408 developer tests** passed: the earlier 341 plus 18 child-recognition,
23 preference-bridge and 26 adapter regressions. The actual pyMHF smoke loaded
both classes outside the game, checked the 15 callback/11 target set, resolved
the real production Python instance, queued OFF once, refused token replay and
applied it only to temporary preferences. Other preference fields and companion
memory were preserved. No hook was registered and no game or user preference
file was accessed. The unchanged production source retains its own 230-test
report; those tests were not rerun just for developer-menu changes.

After normal game exit and a fresh backup, use the separately prepared bundle.
Browse and reopen the submenu without confirming: the value must not change.
Confirm OFF and ON individually, comparing applied state in the temporary panel
and after closing/reopening. Hold confirmation and check that it changes once.
Check parent entry while held, native Back, manual summoning, menu order and
ordinary automatic behavior after the next real trigger. These live checks,
remapped controls and controller paths remain pending. The current 0.6.2
installation is not overwritten by preparation or packaging.

## Historical observation-only live sequence

1. Close NMS normally and preserve current progress; verify a fresh backup as needed.
2. Use the isolated folder's `Start-CompanionAutoSummon.ps1`. The exact executable,
   framework and explicit probe-enable guards must pass before registration.
3. Load a save and open X, the companion section and the summon list.
4. Back out, close and reopen the menu; optionally manually summon an owned pet.
5. Record the player's visible result and the bounded action/depth observations.
6. Exit the game normally before closing its host. Resume the original mod with
   its own launcher in a later session.

Do not expect a new menu item in this test. A passing observer test establishes
only the observed route on that build. Natural action, construction and label
observations have now been captured. Verify binding protection before one
inert, uniquely tagged entry. Preference changes come after navigation, rendering,
rebuilds and coexistence with vanilla actions have passed. Controller operation,
localization, multiplayer and other game builds remain separate work.

## References

- [NMS.py TriggerAction source](https://github.com/monkeyman192/NMS.py/blob/b41bf9e6fdff1c833b77d805bb0c8da555c4ced4/nmspy/data/types.py): discovery hint; its incomplete structures are not a current ABI contract.
- [pyMHF 0.2.4 hooking](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/pymhf/core/hooking.py): a before callback returning None preserves native arguments.
- [Windows ReadProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-readprocessmemory) and [GetCurrentProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentprocess): bounded copying and pseudo-handle lifetime.
- [Python ctypes callback functions](https://docs.python.org/3.11/library/ctypes.html#callback-functions): foreign-thread callbacks and the limitation of thread-local state across invocations.
