# Companion Auto Summon — verification scope as of 28 September 2026

Historical sections retain the status recorded for their named versions,
including statements that a candidate had not yet launched. For the latest
bounded observations, read the current-candidate section and its linked live record.

## Current candidate 0.4.9 / 0.8.7

The external title is **Companion Auto Summon for No Man's Sky**, credited
**by Lineum Dynamics**. The short in-game title, settings, and summoning rules
remain unchanged. Production 0.4.9 and menu 0.8.5-branding contain updated
metadata; all 14 catalogs have 41 entries, including the full title and author credit.

333 production tests and 675 developer tests passed without failures or skips,
along with an offline check using the real framework and both read-only preflight checks.
After a minor grammatical correction to the Korean title, 24 localization tests
passed again, as did the framework check and both checks of the final
`build/quick-menu-play-trial-087-r1` package. It contains 40 payload files and a manifest.
It was launched on 28 September after the game had been closed normally and a backup
of 46 files had been verified. At 11:07:26, both mods and twelve targets loaded;
the first check found no changes to the package files, preferences, or remembered
manual selection. The user confirmed a visible summon in the Anomaly after loading
and after exiting the ship; the log confirms two accepted requests and active slots.
These were different random pets, so this does not prove that the earlier intermittent
failure has been fixed. Language observation reported ENGLISH, without enabling
translations. The [0.8.7 record](docs/research/LIVE-087.md) retains the details
and unverified areas. The original `087` output is superseded. The earlier 0.8.4
and prepared 0.8.6-r1 remain immutable. Habitat-weighted selection and shuffle
are a separate proposal, not part of this candidate.

## Historical 0.8.4 result and preparation of 0.8.5

Combined 0.8.4 was launched on 28 September 2026 after a verified backup of 43 files.
Both mods and twelve native targets loaded; screenshots confirmed six distinct
settings icons. Loading in the Anomaly did not produce a visible pet. The game
briefly reported an active slot, but a later read found no active or pending pet.
A later ship exit in the same session successfully summoned a different random pet.
The cause of this difference remains unproven; see the [record](docs/research/LIVE-084.md).

Source 0.4.8 / 0.8.5 keeps diagnostics running after the first active slot until
the original limit of 15 seconds / 4096 callbacks. It does not repeat summoning,
change gameplay rules or text, and is not deployed. The running 0.8.4 is unchanged.

## Original preparation of 0.8.4 — protection against an unverified version

The launchers now verify the selected game and recheck the actual target process
before each DLL injection. An unknown or unreadable version, a different installation,
a mismatched framework, foreign pyMHF extensions, or an incomplete package cause
launch to be refused. There is no forced override, preference change, or save write.
The native guard before hook registration remains independent.

Nine launcher messages have text in all 14 catalogs; thirteen translations remain
unreviewed drafts. The warning uses the console and, optionally, a Windows dialog,
not an unverified game function. The language comes from Windows or an explicit choice.
Check-only mode and the no-dialog option do not display a window.
The catalogs now contain 39 keys; complete application localization is unfinished.

Production automation 0.4.7 and menu 0.8.3 are unchanged. Candidate 0.8.4
has not been launched in the game or deployed. The last installation, 0.8.2,
and the previous unlaunched 0.8.3 package remain untouched. The runtime guard
alone does not establish the safety of future custom technologies stored in inventory.

The final source passed 329 production tests and 633 developer tests without skips.
The combined package has 39 files and a manifest. Real pyMHF verified loading both
classes and six options with temporary preferences, without attaching to the game
or installing hooks. Direct checks through Python and Windows PowerShell 5.1 passed
against the existing game and runtime without launching or installing anything.
A quoting error in the older PowerShell test command and handling of paths containing
characters outside the Unicode Basic Multilingual Plane were also fixed.

## Previous preparation of 0.8.3 — icons and language catalogs

The separate, unlaunched 0.8.3 package keeps production 0.4.7 unchanged and adds
menu 0.8.3. It contains seven original icons, an explicit Random biome-option label,
and the same gameplay rules. The previous 0.8.2 installation was not overwritten.
294 production tests and 563 developer tests passed, including checks of icon mapping,
independent fallback to the original paw, and rejection of unknown target files.
Real pyMHF verified two mod classes, 18 callbacks for 12 targets, shared dispatch,
and all six settings in temporary files. There was no game attachment, native hook
installation, or change to personal data. The launcher passed its syntax check.
Independent decoding of all six new PNG/DDS pairs confirmed identical pixels
and transparency. Building from an extracted source ZIP and running its localization
check also passed in a temporary directory; the resulting production file is identical.

All 14 catalogs have the same 24 keys; 13 translations are marked as unreviewed drafts.
The validator checks freshness, parameters, and agreement with the English menu
and notices. The standalone build, combined package, and source ZIP release require
the check before writing. Tests confirmed rejection of a missing translation without
overwriting the previous output. This is not in-game language support: language detection,
glyph rendering, and coverage of the panel and launcher remain outstanding.

## Previous 0.8.2 launch

During the 0.8.2 launch, after a verified backup of 43 files and another pre-launch hash check, both mods and 12 targets loaded on 27 September 2026 at 23:58:46, with automation ON. All 17 files and personal settings remained identical. The texture was prepared and its hash matched; rendering itself is not confirmed. 294 production tests and 519 developer tests passed. Earlier 0.8.1 was stopped by preflight: psutil did not name the protected Secure System process. The corrected native Windows listing recognizes it and still rejects incomplete or erroneous results. Evidence: menu-play-0.8.2-startup.json. In-game acceptance is pending.

The private test records identified by filename below are retained outside the Git repository and distribution ZIP. This document summarizes them; personal records and backups are not distributed.

## Launched candidate 0.4.7 / 0.8.2 — launcher additions

Before the combined in-game test, the launcher adds two separate protections against
concurrent startup. PowerShell holds the first while preparing the environment and
waiting for the host; both Python host variants use the second. Named Windows objects
are shared even by copies in different directories; an existing object causes a new
launch to be refused. Release follows the handle lifetime, leaving no stale PID file.
Older launchers do not have this protection and must not run alongside the new ones.

The `-CheckOnly` switch checks package integrity, the exact game, and an already prepared
runtime, including while playing. It installs nothing, creates no environment, prepares
no DDS, and launches neither the game nor the host. A missing runtime is only reported.
During normal launch, a process-discovery failure stops execution before environment
preparation.

Gameplay behavior, native menu 0.8.0, and the icon are unchanged from the previous candidate.
Everything remains prepared for one combined test. Running 0.7.1 and unlaunched 0.7.2
and 0.8.0 are preserved.

**294 production tests** and **519 developer tests** passed.
A separate test with real Windows processes in an isolated test namespace verified
rejection of a second host and release after both normal and abrupt termination of the
test process. It used neither the production lock nor the game. Real pyMHF again passed
checks of the widgets, both mods, all six settings, and the lock–check–asset–launch–release
sequence with a simulated launch. The subsequent real mod load is described above;
the visible result and controls still await verification.

## Older prepared candidate 0.4.6 / 0.8.0 — combined test

It extends the native page with all six existing settings: automation, last manual
or random selection, same-biome preference, and three locations. Each row uses the
production runtime's existing settings queue and persistence. Opening and navigating
change nothing. Confirmation requires the original native action, the same item,
and a new press edge; holding the control must not repeatedly toggle the setting.
Source tests cover the whole page, but actual controls have not yet been verified.

The custom white paw with a circular arrow is an original 256 × 256 DDS.
The future launcher will prepare it only while the game is closed, at a unique path
under MODS; it will verify its hash and the exact game, and reject an unknown existing
file. Building the package installs nothing. Native registration is attempted once
during the menu's natural resource-loading process. Owned references are retained
for the process lifetime. Both observed global resource-manager pointers must agree;
a change or mismatch permanently disables the provider. Later reads do not use the
old menu pointer. The fallback order is the prepared custom texture, a verified retained
game paw, and finally plain notice text. Static analysis and simulation do not establish
native lifetime or actual DDS loading and rendering.

The candidate retains the manual-selection attribution fix from 0.4.5 and the 5.5-second
confirmation. It changes neither summoning rules, game limits, nor saves. The pyMHF panel
temporarily remains for comparing values during the combined test. Running 0.7.1
and prepared 0.7.2 were not overwritten. The standalone 0.4.6 ZIP contains only the
production component, without the menu or DDS.

**282 production tests** passed: 192 runtime, 34 policy, 14 persistence,
24 settings, and 18 launcher. **504 developer tests** also passed, including checks
of icon-loading failure, original game return values, and asset installation at temporary
paths. No test read personal settings or game saves. The real-pyMHF check verified eight
widgets, loading both mods, and all six options through temporary files of the original
runtime. Eighteen callbacks share 12 targets; the shared target passed both registration
orders and four combinations of simulated-original return values. Native hooks were not
installed. The PowerShell launcher's syntax and icon-provider binding also passed.
Version **0.4.6 / 0.8.0 has not yet been launched in the game**; no earlier in-game
result transfers to it.

## Older prepared candidate 0.4.5 / 0.7.2 — not yet launched

A new manual selection requires a matching native pet-control action, acceptance of
the matching request, and a successful return from the original function. Identity,
local player, application, and save context are rechecked; the original item pointer
is not read after the return. Unattributed requests, including game-driven restoration,
cancel pending automation but do not overwrite the favorite or announce a manual choice.
The actual origin of the earlier call after the arena is unknown, so the previous choice
is not restored automatically.

Brief confirmations of explicit changes last 5.5 seconds. `Companion saved.` means
persistence succeeded; otherwise, `Companion selected (session only).` is displayed.
OFF or Random status is appended where appropriate. Repeated selection of the same pet,
automatic summoning, and native restoration remain silent. Static analysis established
that the original notice function's final flag hides both icon blocks independently
of the text. The candidate enables it while preserving the ABI and using owned buffers.
Disappearance of the white circle and readability still require an in-game visual test.

**279 production tests** passed: 189 runtime (26 new), 34 policy,
14 persistence, 24 settings, and 18 launcher. **408 developer tests**, real
pyMHF 0.2.4 / Dear PyGui with all eight widgets, and the resulting combined package
also passed. Its nine production and eight menu callbacks share 11 distinct targets;
the new production pair uses the same `TriggerAction` as the menu. Python registration
and shared callback dispatch passed in both orders and four combinations of Boolean
results, always with a single call to the simulated original. The menu was disabled
during this test; native hooks were not installed and the game was not used. Temporary
settings through the shared bridge and the PowerShell launcher's syntax also passed.

Version 0.4.5 / 0.7.2 has not yet been launched. Running 0.4.4 / 0.7.1 and older
artifacts remain unchanged; their results below do not transfer to the candidate.

## Diagnostic version 0.4.4 / 0.7.1 to date

Passive observation after request acceptance does not change summoning. It reads the
existing native data through an existing callback, with limits of 15 seconds, 4096
diagnostic calls, and eight transition messages. Disappearance from the queue does not
trigger another attempt; an active slot is game-reported data, not proof of a visible pet.
Observation ends on a context change or player intervention. This version has one
confirmed Anomaly summon, described below; it does not fix the white circle.
After the game was closed normally and a new backup of 43 files was verified, 0.7.1
launched on 27 September 2026 at 22:22:35. Both mods and 11 hook targets loaded
with automation ON. All 14 payloads, settings, and remembered manual selection
remained identical at startup. Registration does not verify a visible summon.
Evidence: `menu-play-0.7.1-startup.json` and the corresponding backup record.

The 0.4.4 / 0.7.1 checks passed: **253 production tests** (including 23 new diagnostic cases), **408 developer tests**, and offline verification using real pyMHF and the combined package. The tests did not read personal settings, launch the game, or register game hooks.

One Random summon after loading in the Anomaly is confirmed for 0.4.4 / 0.7.1. On 27 September 2026, the log recorded activation by loading at 22:23:39.698, queue acceptance at 22:23:42.250 (the reported 2.56 seconds), and the expected active pet at 22:23:42.266 on the first diagnostic update. The player confirmed its actual appearance. No ship exit or repeated summon preceded it. This is one successful run; it does not fix the earlier intermittent failure, because the change was diagnostic only.

## Partial in-game 0.7.0 result and identified issues

### Later notice after the arena in 0.7.1

The player reported “manual favorite saved” after the arena but cannot identify
the triggering event. At 22:35:48.366, the log recorded acceptance of slot 2, and
the mod's external state changed from slot 3 to slot 2 with a different identity
at the same moment. ON/Random settings remained identical. The 0.4.4 hook does not
distinguish the origin of accepted requests other than its own automatic call;
an actual manual selection is therefore not established. Static analysis confirms
that a pet's return from a pet battle also reaches the same function, but the origin
of this specific live call was not captured.

A bounded external read through a query/read-only handle at 22:40:26 confirmed
location 14, active slot -1, and pending slot -1 in two identical snapshots.
At that moment, the pet was recorded as neither active nor pending; the snapshot
does not establish its state throughout the preceding interval. The exact binary
was verified. The diagnostic performed no writes to the game, runtime, or saved
preferences.

The notice lasts 3 seconds in this version, and the white circle persists. The
subsequently verified icon-hiding flag is used only in prepared 0.4.5. Evidence is
in the private record `menu-play-0.7.1-arena-notice-observation.json`. The fixes
for manual-selection attribution, readability, and rendering have not yet been deployed.

The player confirmed summoning after exiting with ON and later suppression with OFF.
The screenshot shows OFF in both the menu item and the in-game notice; the log confirms
that changes were forwarded and applied. The first description of the OFF attempt is
ambiguous: before the first recorded exit at 21:50:12, the state changed back to ON
at 21:50:07. The player explicitly explained the rapid changes as repeated presses.
This does not verify holding, remapping, controller input, or the complete back-and-reopen
menu flow.

According to the player, the pet did not appear after loading in the Anomaly, even
though the native queue accepted slot 2 at 21:49:21.727. This is a failed visible
result, not a verified summon. The runtime ends the request after queue acceptance
and does not continue observing the pet's activation. The exact cause inside the game
has not yet been identified. Mere absence of a pet does not authorize another attempt:
it could follow manual dismissal.

The screenshot also confirms rendering of the status notice for the first time.
There is an unwanted white circle above the text. The call passes a pointer to a zero
icon resource, whose visual result had not previously been verified. The record
and screenshot are retained as `menu-play-0.7.0-user-observation.json`
and `menu-play-0.7.0-off-hud.png`.

## Prepared toggle in native menu 0.7.0

The separate 0.7.0 package contains the unchanged production script 0.4.3 and the first
actual menu option: enabling/disabling automatic summoning. A change requires a new
confirmation evaluated by the game itself, the same selected item, and another check
after the native function's original return. Holding confirmation, merely displaying
the menu, or rebuilding it must not repeat the change. No fixed physical key is used.
Unverified activation paths do not apply the change.

**408 developer tests** and an offline check using real pyMHF passed:
two mods, 15 callbacks for 11 distinct targets, eight temporary panel controls,
and no custom hotkey. A test using a real Python instance of the production mod
verified queueing one change, rejecting repetition, and subsequently persisting only
to temporary settings. Other options were preserved. The test used neither game
functions nor personal files. Unchanged production retains its previous result
of 230 tests; the developer-menu change did not require rerunning them.

The package has 15 files, including 14 hash-checked payloads. After the game was closed
normally and a new backup of 43 files was verified by hash, it was launched on
27 September 2026. At 21:48:38, both mods and 11 hook targets loaded with automation ON.
All 14 payloads remained identical; the initial check confirmed unchanged settings
and remembered manual selection. Registration does not verify that the toggle works.
The next test covers OFF/ON, holding, back/reopen, item order, and ordinary pet actions.
Other settings remain in the temporary panel for now; the pyMHF panel will be removed
from the final player interface once the menu is complete.

## One-time summon after loading in version 0.4.3

A successful local save load records one opportunity if automation is enabled. Neither summoning nor placement search is called during deserialization. Subsequent local ownership updates evaluate the permitted location and the original native checks. The same 1.5-second wait and 0.5-second spacing between check pairs apply. No new hook or unverified memory address is introduced.

The saved favorite is restored by its full identity, not its old slot. A missing record during loading is checked at most twice per second. Random mode uses the same pool of eligible owned candidates. An already present or pending pet, manual selection or preview, entering the ship, a settings change, or a context change ends the opportunity. After an accepted summon, mere absence of the pet does not arm it again.

New 0.4.3 loaded in the separate combined 0.6.2 package on 27 September 2026 at 20:42:21. The log confirmed automation ON and two mods with ten hook targets. Before launch, a new verified backup of all 43 profile files was created; package files and existing configuration remained identical in the subsequent check.

**One automatic summon after loading on foot at a space station in Random mode is confirmed.** At 20:42:58.578, the log recorded the opportunity after save loading and location 2. After waiting for native eligibility, it selected slot 1 from five eligible owned pets at 20:43:01.260, and the game accepted the request at 20:43:01.261. The reported 2.69 seconds measures time to request acceptance, not the exact time to visible appearance. This request was not preceded by ship-exit activation; the later exit at 20:44:27.717 is a separate event. The user confirmed actual appearance and clarified that they were at a station, not in the Nexus. All twelve files of the running package remained identical. Evidence is retained in `menu-play-0.6.2-station-startup-success.json`.

Later in the same unchanged session, the user confirmed one manual dismissal without reappearance. The suggested procedure was to remain on foot for about ten seconds; the exact location, time, and observation duration were not independently measured. The user had traveled in the meantime, so this is not a controlled dismissal test immediately after the original station load. Private record: `menu-play-0.6.2-manual-dismissal-success.json`.

This does not verify loading on a planet or in the Nexus, last-manual-selection mode after loading, broader manual-dismissal regression coverage, biome preference, or multiplayer.

**230/230 mod tests** passed: 140 runtime, 34 policy, 24 settings, 14 persistence, and 18 launcher. In addition, 341 developer-tool tests passed, along with actual construction of eight panel controls and a check of joint loading of two classes in pyMHF with 13 callbacks for 10 distinct targets. No hook was installed into the game during these checks. SHA256 of the standalone 0.4.3 script is `87c4b8e44ec85605e5483542344c6addafd8d6ecb171cf0a7a365752419ad8dc`.

## Renaming in version 0.4.2

The approved name is **Companion Auto Summon**, repository `nms-companion-auto-summon`. The new standalone script is `CompanionAutoSummon.py`, the launchers are `Launch-CompanionAutoSummon.py` and `Start-CompanionAutoSummon.ps1`, and the class and current pyMHF tab are `CompanionAutoSummon`. Gameplay rules, RVAs, native-function signatures, stored-data formats, and default settings remain unchanged. The original `%LOCALAPPDATA%\NMS-AutoPet` location for preferences, manual selections, and the developer runtime is retained for compatibility; the rename itself does not migrate personal data.

At the time of the original record, candidate 0.4.2 had not yet been launched; QUICK-MENU.md records its subsequent combined startup with the menu. Its own offline results remain versioned. The results and `AutoPet.py` hash below explicitly belong to earlier versions, including 0.4.1; they are not retrospectively renamed. The number 211 denotes the historical test count for 0.4.1, not automatically the result of the new version.

Renamed 0.4.2 passed **212/212 offline tests**: 122 runtime, 34 policy, 24 settings, 14 persistence, and 18 launcher. The new regression test verifies preservation of preferences and manual selection at the original data location. A real-pyMHF 0.2.4 / Dear PyGui 2.3.1 check confirmed a single `CompanionAutoSummon` class with inherited `_mod_name`, eight widgets, seven callbacks for six targets, and zero hotkeys. Hooks were not registered, no viewport was created, and the game was neither launched nor attached to. SHA256 of the generated `CompanionAutoSummon.py`: `841c57ee82cd8fee7a4083a63eb846ee78bd6a8a23efcbbf5cef1b49fa96e472`.

## Historical AutoPet evidence through version 0.4.1

## What is established

**Candidate 0.4.1 passed 211 offline tests and a check of all eight settings controls using real pyMHF 0.2.4 / Dear PyGui.** The new biome preference has statically verified read addresses and category conversion matching the native game. Loading this version into NMS and biome-based selection have not yet been verified in-game. The live successes below belong to the explicitly identified earlier versions.

**Version 0.4.0 has verified loading, use of the Random option, and one random summon of an owned pet on a planet.** The log records selection of slot 3 from three eligible owned pets and an accepted request; the user confirmed actual appearance. Individual location options, full panel operation, settings after restart, and waiting for a suitable place without a time limit, including retrying a rejected request, remain unverified in-game.

**Version 0.3.3 successfully restored the selected pet after a restart and automatically summoned it after a ship exit at a station.** The log captured restoration and an accepted request; the user also confirmed actual appearance without another manual selection. Earlier 0.3.2 likewise verified the basic flow on a planet. This conclusion applies to these two tested scenarios on the same save. It does not verify the Nexus, multiplayer, unsuitable terrain, controls/HUD, or long-term stability.

The function mapping described below was obtained by statically reading NMS.exe from the filesystem. Its SHA256 is listed in the manifest. After static tests were completed, the user closed the game and authorized the first runtime test; a verified backup of 42 profile files was created beforehand. The first framework launch ended with exception 0xc0000005 before an AutoPet log was created. This did not confirm in-game functionality.

NMS.py provided signatures of existing functions. In the installed EXE, the Player.Update, OnEnteredCockpit, Spaceship.Eject, PlayerState.LoadFromData, and QuickActionMenu.TriggerAction patterns each have exactly one match. The old PlayerCreatureOwnership constructor pattern has zero matches; neither that constructor nor its structure is used.

Static analysis of the quick menu's `SummonPet` branch and its call in Player.Update produced the following map. Names of the new helper functions are our interpretation of their use; they are not an official public game API.

| Function / value | RVA or offset | Evidence |
|---|---:|---|
| Player.Update | RVA `0x1440CD0` | Unique NMS.py match; reads the pending pet and calls the spawn path |
| Spaceship.Eject | RVA `0x17479D0` | Unique NMS.py match |
| Player.OnEnteredCockpit | RVA `0x1479490` | Unique NMS.py match |
| PlayerState.LoadFromData | RVA `0x56FA50` | Six arguments; actual bool return type and CommonStateData second argument verified in the EXE |
| Summon eligibility check | RVA `0x146A410` | Direct call from the quick-menu branch, bool result |
| Summon request preparation | RVA `0x146AC90` | Direct call from the same branch; stores the slot and data for Player.Update |
| Global application pointer | RVA `0x6E7AAE8` | RIP-relative accesses in these paths |
| Local Player | app + `0x71C690` | Direct address and agreement with accessor + Player offset |
| Location | app + `0x57A584` | The native summon check permits 3/14/2; the mod also uses them from version 0.3.3 |
| Active pet | app + `0x29A1C0` | The quick menu compares the slot for dismissing the current pet |
| Pending pet | player + `0x6010` | Written during preparation and read in Player.Update |
| Pet CreatureSeed | app + `0xE10D0` + slot × `0x24A0` + `0x2330` | uint64; native copy of GcPetData.CreatureSeed |
| Pet BirthTime | same record + `0x23C0` | uint64; bidirectional copy of GcPetData.BirthTime |
| Slot occupancy | same record + `0x2370` | The native summon check requires a nonzero resource |
| SaveUniversalId | CommonStateData + `0x8980` | uint64; both load and save copy through PlayerState + `0x187E8` |
| PlayerNotifications.AddTimedMessage | RVA `0x9B8300` | Unique pattern; 11 arguments verified in the body and calling functions |
| PlayerNotifications | app + `0x837B40` | The same offset in several native calling functions |

The quick-menu branch reads the action from `MenuAction + 4` and the slot from `+0x84`. The mod neither copies this incompletely described structure nor replays the menu. It captures an accepted pet-preparation request and later calls the same function on the game thread. From version 0.3.2, automatic recalculation and evaluation run after the native pet-ownership update; GUI and HUD remain after Player.Update. The game's mechanism still prepares placement and performs the actual summon.

The native check includes index 0–29, an occupied slot, and other game-defined conditions. The mod does not change its result. The CreatureSeed + BirthTime combination protects against automatically selecting a different pet after a slot's contents change.

## Persistence and portability

SaveUniversalId is a persistent value from the game itself: LoadFromData reads it from CommonStateData + `0x8980` and writes it to PlayerState + `0x187E8`; the save function at RVA `0x576D60` performs the reverse copy. LoadFromData returns bool, which was also verified in its callers. In 0.2, this corrects the inaccurate 0.1 prototype declaration based on an older NMS.py stub. Version 0.1 was neither installed nor launched.

Pet loader `0x11FE4E0` copies CreatureSeed from GcPetData + `0x128` to runtime + `0x2330`, and BirthTime from + `0x148` to + `0x23C0`. Saving performs the reverse copies. The originally observed runtime + `0x2390` is BoneScaleSeed; it is not used for persistent identity. The persisted identity is exactly 8 bytes of CreatureSeed and 8 bytes of BirthTime, without structure padding.

After a successful local load, the corresponding manual selection is read from `%LOCALAPPDATA%\NMS-AutoPet\state.json`. In last-manual-selection mode, occupied slots are searched on the next ship exit. Only a unique match is restored, so moving to another slot is supported and ambiguous matches are not guessed. JSON is written by atomic replacement only after an accepted manual selection; game saves are not opened. Random mode in 0.4.0 does not require a prior manual selection, and random draws do not overwrite this file.

SaveUniversalId is shared by the base and expedition contexts of one save. The implementation stores one choice for the entire save and always verifies that the pet is present in the currently loaded context.

The launcher and package use relative paths, discovered Steam libraries, and the current user's directory. They contain no specific account or personal save. The GameDirectory parameter validates the directory, but pyMHF still launches app 275850 through the active Steam instance. The mod itself rechecks the actual EXE before registering hooks.

The first attempt exposed redirection of the user's AppData through Windows MSIX. The pymem version used returns the local library address when loading a DLL without verifying the remote LoadLibraryW result. This is consistent with the observed crash, but that consistency alone is not proof of the cause. `Launch-AutoPet.py` passes a canonical physical path and, instead of an assumed address, requires exactly one actually loaded library with the same full path in the target process. A missing or invalid address stops startup before its code is called. The change applies only to the launcher's host process; installed framework files are unchanged.

## Settings panel and confirmations

PyMHF provides its own desktop window. AutoPet 0.4.1 has **eight GUI properties**: five editable `BOOLEAN` values (automation, Planets, Space stations, Nexus, Prefer same biome in Random mode), one `ENUM` (Companion selection: Last manually selected / Random), and two read-only `STRING` values (Status, Companion). Defaults are automation enabled, all three locations, `last_manual`, and biome preference enabled; that preference applies only in Random mode on a planet. While waiting, Status displays `Waiting for a suitable place`. The prompt for an initial manual selection applies only to `last_manual` mode.

The GUI setter only records the requested change under a lock; changes are coalesced, and writing options to disk and calling the game happen only in the local Player.Update hook. The latest change to a given option wins. A settings change cancels the previous pending request; enabling automation or changing mode alone does not summon a pet. No hotkeys are registered. The panel requires `pymhf[gui]==0.2.4`; the launcher checks for Dear PyGui even in an existing environment.

Preferences are separate from the runtime error latch and are saved to `settings.json`, not the pet-selection file. Schema 3 adds the Boolean `prefer_same_biome`; the default document is:

```json
{"schema":3,"enabled":true,"locations":[2,3,14],"selection_mode":"last_manual","prefer_same_biome":true}
```

Locations are a sorted subset of integer IDs 2/3/14 without duplicates; an empty list is allowed. Modes are exactly `last_manual` and `random`. Schema 1 retains the original `enabled`, and schema 2 also retains locations and mode; both add the new preference as true only in memory. Reading alone does not rewrite the file. Schema 3 is created only on explicit save, and an already saved false remains false. The compatible `save(bool)` helper changes only enabled state and retains other preferences. Unknown fields, incorrect types including a Boolean instead of an ID, duplicate JSON keys, and files larger than 4 KiB are rejected. An invalid existing file means default OFF and any explicit toggle applies only to the session. Writing uses a temporary file, flush, fsync, and atomic replacement; invalid data is not overwritten.

Native `AddTimedMessage` has 11 arguments in this EXE: object, text pointer, float duration, RGBA pointer, uint32 audio, icon-resource pointer, bool, float delay, and three bool values. The older NMS.py declaration has an incorrect delay type and lacks the final bool. The text buffer is 512 bytes, and RGBA is explicitly aligned to 16 bytes for MOVAPS; an empty icon is a valid pointer to int32(0). Audio 0 corresponds to INVALID_EVENT, not an error sound.

Messages are sent only from local Player.Update with positive dt. They respect the native message count at `notifications + 0x28C` and the suppression value at `app + 0x4BF50C`; under unfavorable conditions, only the latest message waits. Loading another save cancels it. A new manual selection creates one confirmation; automatic summoning and restoration of the same pet do not. The native void return is not proof of actual display.

## Source verification and tests

- Command from the package directory: `python -B -m unittest discover -s tests -v`. The combined run result is recorded in the manifest.
- The `build.py` build joins four source parts and checks their syntax without importing them.
- Policy tests use simulated time and state, without game files.
- Adapter tests use owned memory blocks and substitutes for the framework and native functions. They verify routing and guards, **not actual binary compatibility**.
- An independent review of pyMHF 0.2.4 source confirmed decorator syntax, native calls with ASLR, the standalone-script format, and exclusion of `_disabled` classes before hook registration.
- The pending slot is checked after the mod's own native call. From 0.4.0, -1 retains the same exit and selected pet for another fresh placement-check pair; an accepted slot completes the wait. Earlier versions skipped that exit on -1. An unexpected index after the call or an exception in the native path disables automation. Recoverable optional biome-read errors in 0.4.1 only fall back to ordinary random selection. An accepted request is not considered proof that the pet was visibly displayed.
- In addition to ownership/context checks, the summon check at RVA `0x146A410` calls placement helper `0x507DF0`. The first live test exposed missing recalculation of internal data without the quick menu open; the fix is described below.
- In an older version with three GUI properties, their import and construction also passed using real installed pyMHF 0.2.4 in a separate Python environment. This ran without hook registration or game launch; it does not confirm the runtime ABI.
- For 0.4.0, a separate offline test using real pyMHF 0.2.4 and Dear PyGui passed: all seven actual widgets were created without a display window (viewport), the ENUM dropdown and all four checkbox callbacks ran, and writing schema 2 to a temporary file was verified. The framework found seven hook callbacks and zero hotkeys. Hooks were not registered; there were no native game calls or game attachment. This verifies control construction and handling; it does not establish panel visibility in an actual session, ABI correctness, or spawning.

## First live launch

After the launcher change, the second launch successfully loaded AutoPet 0.3.1. The log confirmed framework initialization, automation enabled, and one mod with five native hooks. This verifies the startup path and hook registration; it does not establish an actual spawn, confirmation display, or multiplayer.

## Placement fix in version 0.3.2

The first summon failed. A repeated exit captured at 11:01:53 activated the policy logic; native eligibility remained false until the 12 seconds expired. Manual selection and its persistence worked. A later preview opening had valid placement, but the user had moved in the meantime, so that snapshot is not a controlled comparison of the same terrain.

Static analysis proved that pet-ownership update `0x5066A0` calls placement reset `0x1439820` when the preview is closed. This clears the result, transforms, and context, but does not cancel two already initialized collision-testing jobs. The original AutoPet only read eligibility and did not initiate this missing calculation.

The new callback runs after local `Ownership.Update(owner*, float dt)`. The ownership object is `app + 0xE10D0`; its already constructed placement object is at `owner + 0x1B9140`. After native ownership/context check `0x505B70`, it calls the ordinary calculation `0x1438040(arc*, float range1, float range2, uint32 hand)`. It reads both ranges from game variable `base + 0x52381E0` and requires a positive finite value. In this session it was 40.0; the mod neither sets nor shortens it. Hand selection exactly follows the native branch: default 0; if bool function `0x60B770()` returns true, it uses uint32 from `app + 0x30E7FC`.

The first mod-initiated recalculation starts new collision queries; its result cannot be used for summoning. Subsequent updates can process the results. The full native pet check `0x146A410` and any request queueing run in the same callback before the game would clear placement again. A pet preview at `owner + 0x1B9300` or the emote flag at `owner + 0x1B937D` cancels the automatic request. Disabling, a context change, an interruption of eligible conditions, and a new exit require fresh placement preparation.

The mod does not create its own copy of a game object, overwrite placement validity, suppress reset, or call preview rendering. When the wait ends, it stops calling the calculation; the normal game performs cleanup. Detailed static evidence is in the working `work/auto-pet-placement-audit/REPORT.md`.

After a new verified backup of 42 files and closure of the previous game session, version 0.3.2 successfully loaded at 11:23:32 as one mod with six native hooks. A total of 161 offline tests passed.

## Successful basic in-game test of 0.3.2

After restarting, the user loaded the same save and exited the ship on the first planetary landing, without making a new manual pet selection. Log `pymhf-20260927T112332.log` from 27 September 2026 recorded:

- **11:27:37.264:** restoration of the remembered pet in slot 1; at .265, activation of the wait after exiting.
- **11:27:38.546:** planetary on-foot state (location 3), no active or pending pet, native eligibility false.
- **11:27:38.569:** native eligibility true; the continuous on-foot wait still has to finish.
- **11:27:40.051:** one accepted request for slot 1, 2.78 seconds after exiting.

No new manual-selection record was added during this run. The user explicitly confirmed that the pet actually appeared. The conclusion therefore rests on both the log and in-game observation, not merely request queueing. This confirms restoration of the choice between two launches and basic automatic summoning on a planet; it does not verify all pet species or all situations.

## Removal of an unnecessary restriction in version 0.3.3

The user verified at a station that version 0.3.2 did not automatically summon the pet. This matched our planet-only restriction but was not a restriction of the game itself. Check `0x505B70` explicitly accepts locations 2 (SpaceStation), 3 (PlanetOnFoot), and 14 (Nexus). The earlier recommendation to use a station to test a prohibited location was therefore inaccurate.

Version 0.3.3 uses the same three permitted locations while continuing to call the native ownership/context check, placement calculation, and full summon check. It does not unlock summoning where the game refuses it. Nexus denotes internal location 14; a different internal designation, Anomaly, has value 15 and is not automatically added. Freighter has locations 9/10 and remains rejected by the native check. One station test succeeded; this does not confirm calculation in all interiors.

After the game was closed normally and a new backup of 42 files was verified at 12:18:30, version 0.3.3 successfully loaded at 12:18:51, again as one mod with six native hooks. 165 offline tests passed.

## Successful in-game station test of 0.3.3

After restarting, the user loaded the same save and tested a ship exit at a station without the X menu or a new manual selection. Log `pymhf-20260927T121851.log` captured restoration of the pet in slot 1 and activation of the wait at **12:20:03.726**, followed by location 2. At **12:20:05.031**, native eligibility was true, and at **12:20:05.243**, the game accepted a single request 1.52 seconds after exiting. No manual-selection record was added before this attempt in the new session.

The user confirmed the pet's actual appearance at the station. The log and this observation together confirm restoration of the choice after restart and basic automatic summoning in this location. The existence of a request alone would not be enough to support that conclusion. The Nexus remains untested.

## Changes to waiting and pet selection in version 0.4.0

The default policy no longer has a 12-second expiry. A ship exit remains pending until the game accepts a request or a cancellation event occurs. An archive platform, insufficient space, or a temporarily natively prohibited location do not end the wait by themselves. The mod does not assume that a particular building will be accepted; once native checks permit the first suitable place and the stabilization delay has elapsed, it can complete the original exit.

In a supported location enabled by the user, the requirement for 1.5 seconds of continuous stable presence remains. In a natively prohibited location, the intent is retained, stability and any placement test in progress are discarded, and no native placement or summon calls occur. Returning to a permitted location therefore requires a fresh stable observation. A supported location disabled by the user is different: entering it cancels the pending exit, and a later transition does not restore it by itself.

Placement checking uses fresh pairs of callbacks after `Ownership.Update`. The first only prepares native queries; the second can evaluate their results. The second callback must have the same location and nonzero player physics-context ID (`uint64` at `player + 0x2A8`) and follow within 0.25 seconds. With a zero ID, the native calculation is not called at all; an ID change requires a new pair. An old or interrupted pair is not used for summoning. Completed pairs are at least 0.5 seconds apart, so waiting does not run the full check every frame. Each attempt uses the original game range and native restrictions. The mod does not overwrite placement validity or shorten game limits.

If summon preparation returns pending slot -1, the policy releases the attempt in progress but retains the exit intent and fixed choice. Another attempt requires a new check pair after at least 0.5 seconds. An accepted request ends that exit; the mod does not then try a second spawn. An invalid or unexpected state still causes cancellation or shutdown according to the relevant guard, not a forced summon.

Waiting is canceled by entering the ship, a manual pet preview or related emote, an accepted manual selection, an actual settings change, save loading, application-context reset, or a change to the identity of the already selected pet. A present pet or a different natively pending pet also ends the original exit. Save loading or enabling automation alone does not create a new request.

Mode `last_manual` remains the default. Mode `random` can begin waiting without a previous manual choice: after preparing placement, it selects at most one owned pet from candidates accepted by native checks. The selected slot and identity remain fixed for that exit, including after rejected queueing; waiting never serves to redraw repeatedly. Identity, occupancy, ownership, and full eligibility are rechecked before queueing. Random selection does not change the remembered manual favorite. After cancellation, no replacement draw occurs without another exit.

This section describes the current source; the scope of live results is given below. Version 0.4.0 does not yet have a confirmed flow through waiting at an archive, moving to a suitable place, or repeated queue rejection. One basic Random-mode flow on a planet has already succeeded.

The final 0.4.0 build on 27 September 2026 passed **197 offline tests** without failures or skipped cases: 109 runtime, 34 policy, 22 settings, 14 persistence, and 18 launcher. Source checksums matched before and after the run. The suite includes simulated placement rejection for 300 seconds followed by summoning, retrying the same pet after queue rejection, random selection without overwriting the favorite, cancellation by settings, and check freshness on context changes. The real-pyMHF and Dear PyGui check was repeated against the final generated script; it confirmed seven constructed controls and their options without hook registration or game calls. The historical counts of 161 and 165 above belong to versions 0.3.2 and 0.3.3.

## Verified loading of runtime 0.4.0

The user closed the 0.3.3 game session normally. Its launcher in terminal session 31576 subsequently exited with code 15; that session is historical and no longer running. Before deploying 0.4.0, a new backup of 42 profile files was created at 13:17:38, with a stable source and verified checksums. Record: `backup-0.4.0-features-test.json`.

After deployment of the tested package, the game launched at 13:18:06 as PID 4508. Log `pymhf-20260927T131811.log` confirms AutoPet 0.4.0 with automation enabled at **13:18:11.299**, and one loaded mod with six hooks at **13:18:11.561**. Retained copy: `runtime-0.4.0-startup.log`. This session's launcher had number 35396. At a later check at 13:59, NMS was no longer running; this startup record is historical.

Startup alone established only `runtime_load_verified`; the subsequent in-game result is recorded below. Biome-based selection is not part of 0.4.0 and was not tested.

## Successful random selection and summon on a planet in 0.4.0

The user stated: “I selected a random pet and a random pet appeared.” The same session's log confirmed application of settings `locations=[2,3,14]`, `selection=random` at **13:22:49.680**. At **13:24:28.249**, it restored the remembered manual choice of slot 1, and at **13:24:28.250**, it activated random selection for the ship exit. At **13:24:29.549**, it selected slot 3 from three eligible owned pets in planetary location 3. At **13:24:31.108**, the game accepted and queued the slot 3 request, 2.86 seconds after exiting. Copy: `runtime-0.4.0-random-success.log`.

A subsequent read-only runtime snapshot confirmed automation enabled, mode `random`, `settings_ok=True`, an active pet in UI slot 3, no native pending slot (`-1`), and a completed exit request. The original manual favorite and its identity remained preserved in the runtime at internal slot 0 (UI slot 1). Structured evidence and log SHA256: `random-success-0.4.0.json`.

Together, the log, observation, and snapshot confirm use of the Random option, one random selection, the pet's actual appearance on a planet, and preservation of the manual favorite in the running session. They do not establish uniform distribution or repeated draws, all GUI controls, preservation of the favorite on disk, preference persistence after restart, or summoning of the manual favorite after switching modes.

## Home-biome preference in version 0.4.1

Option `prefer_same_biome` is enabled by default and applies only to the initial pet selection in Random mode on a planet (location 3). First, the ordinary list is formed from occupied owned slots that passed native ownership, placement preparation, and the full summon check. If it includes pets with a known matching home biome, the draw is uniform within that subset. With no match, an unknown biome, or a recoverable read error, the full ordinary list remains. Stations, the Nexus, manual mode, and a disabled preference skip biome reading entirely. Once selected, the pet is not redrawn on an environment change or request rejection.

Static inspection of the exact supported EXE established the following reads; no new native function is called:

| Data | Verified address and type |
|---|---|
| Pet home biome | `uint32` at `app + 0xE10D0 + slot × 0x24A0 + 0x2480` |
| Solar system | `cGcSolarSystem` pointer at `app + 0x71AF70` |
| Planet count / current index | `int32` at `solar + 0x2544` / `solar + 0x5196D0` |
| Resulting planet biome / subtype | `uint32` at `solar + index × 0xD9170 + 0x6148` / `+0x614C` |

The pet loader copies `GcPetData+0x2B0` to runtime `+0x2480` at RVA `0x11FE63E/0x11FE644`; the save path performs the reverse copy at `0x11FECBD/0x11FECC3`. Native creation of an owned-pet record at `0x504A50` reads the current planetary biome listed above and applies this conversion at `0x504B33..0x504B67`, in this order: subtype 25 → Swamp 12, subtype 26 → Lava 13, otherwise biomes 8/9/10 → Weird 7; other values remain unchanged. The mod compares the pet's saved biome with the planet after the same conversion. Current weather, temperature, and egg readiness are not criteria.

Reading requires a nonzero context and pointer, a planet count of 1–6, and a signed index within `0 <= index < count`; an invalid index is neither guessed nor clamped. Native index -1 means no selection. Concrete biomes are 0–15 except Test 11; All 16 and out-of-range values are unknown. Zero is valid Lush. The subtype must be 0–31, and the raw biome is validated before conversion. Empty slots are not read. Caught `OSError`/`ValueError` exceptions are limited to optional biome reading and do not weaken native-summon guards. These checks are not a general guarantee that any arbitrary nonzero address is readable.

Final source 0.4.1 passed **211/211 tests**, without failures or skipped cases: 121 runtime, 34 policy, 24 settings, 14 persistence, and 18 launcher. The source did not change during the run; evidence: `offline-0.4.1.json`. Using real pyMHF 0.2.4 and Dear PyGui, all eight widgets were created and their handlers passed. The framework recognized seven hook callbacks for six targets and zero hotkeys; hooks were not registered, no viewport was created, and there was no attachment or native call to the game. Evidence: `framework-0.4.1.json`.

SHA256 of the generated `AutoPet.py`: `234cddbc483d626cff5a637d4e4f23c912c9d5bf69b5516982b965d799164fb8`. Loading 0.4.1 and biome-based selection in the game have not yet been verified. An optional read-only snapshot of values could not be obtained at 13:59 because NMS was not running; this is unavailable verification, not a failed in-game test.

## What remains

Unresolved 0.4.1 scenarios also need verification on renamed 0.4.2, including the new launcher, panel name, and restoration of existing preferences. Actual in-game loading and biome preference remain: a known match, no match, disabling it, skipping it at stations/in the Nexus, and preserving the manual favorite. The complete set of the current eight panel controls, individual location preferences, repeated random draws, returning to the manual favorite after switching, preservation or migration of settings on restart, and waiting without expiry and retrying a rejected request have not yet been verified in-game. The Random option and one planetary exit succeeded in 0.4.0. The user has no suitable place nearby for testing rejected placement, so this scenario has not yet been performed and is not a failure. When an archive platform or unsuitable terrain naturally becomes available, the user can remain for more than 12 seconds and then move to a place the game permits without entering the ship again. This test should verify one summon, preservation of the same choice on rejection, and the effectiveness of all cancellation paths.

Summoning in the Nexus, HUD confirmation display, OFF/ON toggling and its persistence, rejection on a freighter, all native branches including different input modes, response to quickly reentering the ship, specific pet species, long-term coexistence with Companion Behavior Adjustments, and multiplayer also remain unverified in-game. Static analysis and simulated tests do not replace these checks. The version therefore remains marked experimental.

The basic in-game test took place after closing the previous session and creating a new backup. Success allows follow-up tests to continue; it does not establish general compatibility or readiness for every play style.

## Primary sources

- [NMS.py — types and function signatures, commit b41bf9e](https://github.com/monkeyman192/NMS.py/blob/b41bf9e6fdff1c833b77d805bb0c8da555c4ced4/nmspy/data/types.py)
- [pyMHF 0.2.4 — hooks and native-function calls](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/pymhf/core/hooking.py)
- [pyMHF 0.2.4 — mod loader](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/pymhf/core/mod_loader.py)
- [pyMHF — standalone scripts](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/docs/docs/single_file_mods.rst)
- [pyMHF — GUI controls](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/docs/docs/gui/gui.rst)
- [MBINCompiler — audio events](https://github.com/monkeyman192/MBINCompiler/blob/44f03dd1c424d64984db4b8106673bd82d2c2816/libMBIN/Source/NMS/GameComponents/GcAudioWwiseEvents.cs)
- [MBINCompiler 7.04 pre1 — QuickMenuActions](https://github.com/monkeyman192/MBINCompiler/blob/44f03dd1c424d64984db4b8106673bd82d2c2816/libMBIN/Source/NMS/GameComponents/GcQuickMenuActions.cs)
- [MBINCompiler 7.04 pre1 — common data and SaveUniversalId](https://github.com/monkeyman192/MBINCompiler/blob/44f03dd1c424d64984db4b8106673bd82d2c2816/libMBIN/Source/NMS/GameComponents/GcPlayerCommonStateData.cs)
- [MBINCompiler 7.04 pre1 — GcPetData](https://github.com/monkeyman192/MBINCompiler/blob/44f03dd1c424d64984db4b8106673bd82d2c2816/libMBIN/Source/NMS/GameComponents/GcPetData.cs)

Detailed working dumps are in the original chat directory under `work/auto-pet-research`, `work/auto-pet-runtime-audit`, and `work/pet-autosummon-research`. The package contains no game binaries or dumps of their machine code.
