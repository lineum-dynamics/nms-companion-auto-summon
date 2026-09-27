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
framework log at 15:54:43 local time reports one mod and one hook. This confirms
registration, not menu behavior or a custom item. The player's natural-menu
sequence and scalar observations are still pending. Generated observer SHA256:
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

The builder writes only to `build/quick-menu-probe/` and never launches, attaches,
deploys or modifies the installed mod. It copies the existing guarded launchers
and emits a small diagnostic manifest. The generated script filename remains
`CompanionAutoSummon.py` to satisfy the guarded launcher's filename contract, but
its only Mod class is `CompanionMenuProbe`. Automatic summoning is absent in this
isolated diagnostic session. The original mod and its files stay separate.

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
