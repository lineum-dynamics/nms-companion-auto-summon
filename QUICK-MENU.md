# Native quick-menu investigation

Status: 27 September 2026. The player mod remains 0.4.2-experimental. No custom
quick-menu entry or quick-menu preference control has been implemented. This
document separates exact-build static findings from live observations and
future mutation work. Raw disassembly is private working evidence, not part of
the repository or distribution.

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

A candidate prevention point is the native bind-modifier input query, scoped
to a verified tagged selection and its exact update context. It must suppress
only that binding attempt, without changing input state or ordinary actions.
The call sequence, thread scope, indirect callers and cleanup still require
verification before any interception. Allowing a binding and then restoring it,
or modifying save serialization, is not the chosen direction. This is static
investigation, not an implemented hotkey guard.

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

The next separate observer is `tools/quick_menu_structure_probe.py`, disabled
in source and excluded from the player package. It observes natural completion
of the builder and label functions with after-hooks that return None. All
observed direct callers pass two pointers and ignore their return values. This
static finding justifies the diagnostic declarations; their live behavior still
needs testing. Neither function is called explicitly by the observer.

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
Its launcher passed PowerShell syntax validation. This artifact has not yet
been launched in NMS; live construction and label observations remain pending.

## Controlled live sequence

1. Close NMS normally and preserve current progress; verify a fresh backup as needed.
2. Use the isolated folder's `Start-CompanionAutoSummon.ps1`. The exact executable,
   framework and explicit probe-enable guards must pass before registration.
3. Load a save and open X, the companion section and the summon list.
4. Back out, close and reopen the menu; optionally manually summon an owned pet.
5. Record the player's visible result and the bounded action/depth observations.
6. Exit the game normally before closing its host. Resume the original mod with
   its own launcher in a later session.

Do not expect a new menu item in this test. A passing observer test establishes
only the observed route on that build. Once natural behavior is confirmed, the
next stage can validate construction and label callbacks before one inert,
uniquely tagged entry. Preference changes come after navigation, rendering,
rebuilds and coexistence with vanilla actions have passed. Controller operation,
localization, multiplayer and other game builds remain separate work.

## References

- [NMS.py TriggerAction source](https://github.com/monkeyman192/NMS.py/blob/b41bf9e6fdff1c833b77d805bb0c8da555c4ced4/nmspy/data/types.py): discovery hint; its incomplete structures are not a current ABI contract.
- [pyMHF 0.2.4 hooking](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/pymhf/core/hooking.py): a before callback returning None preserves native arguments.
- [Windows ReadProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-readprocessmemory) and [GetCurrentProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentprocess): bounded copying and pseudo-handle lifetime.
