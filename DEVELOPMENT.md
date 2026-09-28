# Companion Auto Summon development guide

Current packaging candidate: **0.9.3-test**. It extracts the original Python
standard library to remove the nested ZIP prohibited by Nexus, supplies accurate
Windows product/company/version metadata and the actual launcher build inputs,
and fixes Steam discovery failing on an unrelated inaccessible process. Gameplay
still uses production **0.5.1**, combined **0.9.2-play-trial** and menu
**0.9.1-diagnostics**, unchanged. All **786 developer tests** and offline runtime,
relocation and executable integrity checks pass. No 0.9.3 live test or scanner
clearance is claimed. Nexus file **49197** is also quarantined; its exact ZIP reports **1/58**
(Bkav Pro) in VirusTotal. Moderator review remains necessary; no contact sent. See [packaging evidence](docs/research/PORTABLE-SCAN-093.md)
and [tester handoff](docs/release/TESTER-HANDOFF.md).

Retained distribution candidate: **0.9.2-test**, containing production
**0.5.1-experimental**, combined **0.9.2-play-trial** and menu
**0.9.1-diagnostics**. The tester ZIP provides **Companion Auto Summon.exe** and
bundled Python 3.11.9; players do not install Python or use pip. It targets
Windows 10/11 x64, Steam **Cosmos 7.04 / build 25442159**, Windows .NET Framework
4 and Microsoft Visual C++ v14 x64. Native menu/HUD text remains English.

The launcher prepares verified private backups before normal starts and uses
private session copies, preserving the extracted distribution and existing
preferences. On 28 September, the packaged background child completed a
49-file verified backup and registered both Mods and twelve hooks in NMS.
The interactive C# launcher was not opened or clicked. Visible pet behavior,
normal exit/restart, launcher-window closure, second-PC use and multiplayer
remain **unverified**; see [LIVE-092](docs/research/LIVE-092.md).
The menu adds bounded diagnostics for the known
`unexpected_thread` stop; it does not fix it. The 0.9.2 archive is built; the final developer suite passed **770 tests**.
Relocated executable verification and package checks passed without starting
the game. Nexus file **49196** and the 0.9.2 page were saved and read back,
but automated quarantine blocks downloading. See the scan evidence and
[the tester handoff](docs/release/TESTER-HANDOFF.md). Earlier results do not
validate this new package.

Retained source **0.5.1-experimental / 0.9.1-play-trial** prepares specific confirmations
for every applied setting and a combined launch without the pyMHF control
window. The seven-row native menu remains **0.9.0-selection**. Existing gameplay
rules and preference persistence are unchanged. Validation passed
403 production and 689 developer tests. Actual-framework checks and both
read-only preflights passed; the combined ZIP has 42 verified files. This
0.9.1 candidate has not launched; the retained 090-r2 files remain unchanged. The standalone
source mod retains its development GUI because it does not include the native
menu. This does not establish a finished portable or console-free launcher.

The retained 090-r2 log reports `Inert menu ordering stopped
(unexpected_thread)` at 14:30:17. The menu guard retains the native binding
filter but stops custom menu handling after a callback thread change; the
production automation is separate. The reason for the thread change and its
relation to the player's actions are not established. The unchanged menu in
0.9.1 does not fix this known limitation. Teleport arrival and base removal are
not automatic-summon triggers. The player reported no arrival pet and a pet
disappearing after base removal; the cause of that disappearance is unproven.
Next work is a bounded menu-lifecycle investigation, not an assumed new trigger
or automatic respawn after disappearance.

Retained source **0.5.0-experimental / 0.9.0-play-trial**, with menu
**0.9.0-selection**, now implements By habitat and Shuffle companions. Offline validation passed 396 production and 683 developer tests. The final `090-r2` candidate launched on 28 September 2026 through the guarded Windows PowerShell 5.1/PTY path. Retained 0.8.7
and earlier artifacts remain immutable. The seven-row interface,
new selection behavior and rotation icon have no new live acceptance.

The new session started NMS PID 16776 after a verified backup of 46 save files
and two mod preference/state files. Production 0.5.0 initialized at
14:11:13.488 (Europe/Prague); menu 0.9.0 initialized its binding filter at
14:11:13.682, and the framework reported two Mods and twelve hooks loaded at
14:11:13.828. Existing schema-3 settings retained Random with shuffle OFF in
the in-memory migration. The player subsequently confirmed a visible Random
startup companion and reports that preferences appear to save. A restart check,
By habitat, shuffle outcomes and complete menu acceptance remain pending. See [LIVE-090](docs/research/LIVE-090.md).

By habitat uses explicit directed 13/5/1 exact/related/acceptable groups on
planets, independently of group population; stations/Nexus use the unweighted
eligible owned pool. Unknown planet data waits, no approved owned group skips
one opportunity with one notice, and temporary eligibility/placement failure
waits. Rotation is session-only, separate from the manual favourite, and consumes
only on native queue acceptance. Queue acceptance is not visible-spawn evidence.
Schema 4 defaults fresh installs to By habitat and rotation ON; legacy schemas
1/2/3 preserve their choices with rotation OFF. Details and the complete heuristic
table are in [HABITAT-SELECTION](docs/research/HABITAT-SELECTION.md).

Retained 0.8.7 validation: **333 production tests and 675 developer tests passed** without failures or skips. The separate 41-file `quick-menu-play-trial-087-r1` folder (40 payloads and its manifest) passed real-framework discovery, shared Python dispatch, all six temporary preference paths and both Python and Windows PowerShell 5.1 read-only preflights. The framework checks used nine callbacks per Mod across twelve targets, without native binding or game access. The previously tested `087-r1`, retained 0.8.4 and prepared, unlaunched `086-r1` payloads remain immutable.

The retained previous candidate is **0.8.7-play-trial**, with production **0.4.9-experimental**
and menu **0.8.5-branding**. Its external title is **Companion Auto Summon for No Man's Sky**,
with the byline **by Lineum Dynamics**; the in-game short title stays unchanged.
It retains the passive observation
window after the first logical active index, without adding retries or changing
summon behavior. The menu retains bounded read-only language diagnostics when a
CAS caption is selected; it does not enable translated rendering.

Final `087-r1` launched after normal closure and a verified 46-file backup.
On 28 September 2026 at 11:07:26 (Europe/Prague), both Mods and twelve native
targets registered with Random, automation, all locations and biome preference
ON. The player confirmed visible pets after Nexus loading and ship exit. The
load queue was accepted at 11:08:39.575, with logical active index 4 at
11:08:39.592; its observation ended on native preview/emote after 13.89 seconds,
last active 4. The exit queue was accepted at 11:09:02.922, with active index 5
at 11:09:02.938; observation reached its 15.02-second deadline, last active 5.
Different Random pets prevent a controlled load/exit comparison. Initial
post-start hashes matched all 40 payloads and existing settings/state. A native
English observation at 11:08:53.254 confirms one bounded read, not language
reload readiness or translated rendering. See [LIVE-087](docs/research/LIVE-087.md).
After a requested manual dismissal, the player reported no apparent return;
the requested wait was at least 20 seconds without ship entry or settings
changes, but its actual duration was not independently measured. This is one
bounded report, not broad dismissal verification.
The player also confirmed one native OFF/ON sequence: OFF prevented the requested
ship-exit summon, ON alone created no request, and the next exit summoned a pet.
Logs record OFF at 11:13:04.257, ON at 11:13:39.076, then an exit at 11:13:56.061
and accepted queue at 11:13:57.638. Other preferences remained unchanged; this
does not verify the other five controls, held/remapped input or controllers.
The [earlier 0.8.4 startup failure](docs/research/LIVE-084.md) remains unexplained;
repeatability, Last selected, full controls/HUD/icons and multiplayer remain open.

This repository is the canonical development location. Keep installed test copies and prior exports as deployment artifacts, not as competing source trees. Record live observations against the exact version; neither the historical 0.4.2 rename nor the new 0.4.3 load trigger inherits earlier gameplay verification.

## Project rules

- Write all source code, identifiers, comments, docstrings, test names, build scripts, developer diagnostics, canonical documentation and document filenames in English. Internal evidence and release planning follow the same rule; only explicitly labelled translations and locale resources use their target language.
- Put translated player-facing text in separate locale resources. English is the canonical source language. Non-English text belongs in translation data or deliberately encoded Unicode test fixtures, not explanatory source prose.
- Update implementation, relevant tests and affected documentation in the same change. Do not leave the description of defaults, behavior, setup or support scope behind the code.
- Review locale impact on every change. Update English and all affected translations together when text or meaning changes. Run `python -B tools/validate_locales.py`; the maintained standalone build, combined build and source packaging also run it before writing outputs. Draft completeness does not establish runtime support or language review.
- Preserve native ownership, summon eligibility and placement checks. Do not generate or unlock companions, reduce gameplay limits, accelerate growth or alter game-save files.
- Never edit a running installation or terminate the game or its runtime as part of routine deployment. Preserve current progress before a new live trial.
- Keep personal saves, settings, accounts, logs, raw executable analysis and developer-machine paths out of public packages.

## Current implementation

The 0.9.2-test portable layer adds `launcher/`, `tools/portable_launcher.py`,
pinned runtime construction/audit, the executable builder and the allowlisted
distribution builder. Normal launch checks Steam, exact package/game identity,
Windows prerequisites and competing hosts, then holds its setup lease across
backup, private session staging and host lifetime. Check-only does not require
Steam running and does not perform setup or game launch. Backups verify source,
copy and source again before launch; framework writes use the staged session.
The existing target-handle/native guards remain in force. Launcher/host logs use
`%LOCALAPPDATA%\NMS-AutoPet\logs`, sessions use `sessions`, and backups use
`backups`; player preferences retain their original external location.

The built portable folder is `build/portable-092-r1`, using input runtime3119r3.
Final native imports, executable verify-only and the combined actual-framework
check passed without starting the game. The final developer suite passed
770 tests; relocated executable and actual-package check-only passed with
non-ASCII paths, poisoned Python variables and a minimal PATH, leaving 1,245
files unchanged and creating no backup. Distribution readback belongs in [TESTER-HANDOFF](docs/release/TESTER-HANDOFF.md). Source
changes after packaging require a new artifact identity; never mutate retained
ZIPs, running sessions or installed runtime files to make them match docs.


Repository-only native text preparation now renders the existing catalogs from
an immutable validated snapshot, preserving whole-message state within the
127-byte menu / 511-byte HUD payload limits. The earlier single-message matrix covered
2,086 language/state combinations without fallback; new multi-setting batches
use a complete English fallback when translated text exceeds the byte limit. This preparation remains
outside the production imports; current native menu/HUD text is English.
The exact-build UTF-8 measurement and drawing
decoders are now verified statically. The new combined trial observes copied
language scalars only: completed-load history is not a reload lock. Font coverage,
rendered glyphs, language switching and automatic catalog selection remain unverified.
See [native localization preparation](docs/research/NATIVE-LOCALIZATION-AUDIT.md).

The repository-only noninteractive host import prototype passed seven focused
tests and a real console-free pyMHF import comparison, including its negative
control. The retained hosts did not import it. The portable source now has
noninteractive host support and a bundled runtime. The first packaged background
start registered both Mods and twelve hooks in NMS; interactive launcher use,
visible behavior, shutdown and restart remain unverified. See
[portable runtime preparation](docs/research/PORTABLE-RUNTIME-AUDIT.md).
The earlier repository preparation passed 655 tests, including 22 native-text
and host-import tests. Twenty language-observer and isolation regressions bring
that earlier passing suite to 675. The original 633-test evidence still belongs
to the unchanged 0.8.5 bundle, not to newly integrated features.

The earned-technology work is an **offline prototype**, separate from both
production and the prepared combined trial. Its pure model, pinned native-data
builder and six additional technology catalog entries do not gate the current
mod, consume inventory or write a save. See
[technology prototype](docs/research/TECHNOLOGY-PROTOTYPE.md) for evidence and
remaining native transaction/persistence work. The catalogs now contain 63 keys
in each of 14 languages; thirteen remain unreviewed drafts.
The two product keys keep the full proper name invariant and translate the author
credit. Three compatibility messages now use the full title. These external
branding changes do not add an in-game credit or change native setting captions.

All maintained launchers now preflight the selected executable. The standalone
Python host also validates sibling package hashes and the exact reviewed launch
configuration. Both Python hosts reject foreign pyMHF libraries and install a
final guard that obtains the actual target image from the injection handle with
`QueryFullProcessImageNameW`, checks the chosen path and hashes the executable
before each DLL loader call. It retains the previous loaded-DLL address check.
No PID/name reopening or per-handle compatibility cache is used. Native class
guards remain independent; disk hashes do not prove every mapped byte is intact.

Nine scoped compatibility messages now use the fourteen catalogs outside NMS,
with console output and an optional Windows dialog. Windows UI language is the
default; `-Language`/`--language` selects a launcher language, and unsupported
languages fall back to English. Corrupt translation resources use the two
maintained emergency English package-failure strings. `-NoDialog`/`--no-dialog`
suppresses dialogs; `-CheckOnly`/`--check-only` performs no setup or launch and
does not display a dialog. This is not complete launcher or native localization.
Guarded injection was observed in combined 0.8.4. The portable public installer remains unverified.

`tools/validate_compatibility.py` compares the host constants, JSON profile,
manifest, production mapping and framework pin without importing runtime code.
The combined build and packaging also check generated production, menu/filter
and technology-prototype targets. Drift stops output creation. Build the separate
candidate with `python -B tools/build_quick_menu_play_trial.py --enable-menu`.
Use a fresh explicit output directory if that version's default already exists;
the builder refuses to overwrite an earlier trial. The retained unlaunched 0.9.1 artifact
is `build/quick-menu-play-trial-091-r1`, with 41 payloads plus its manifest. It
passed actual-framework checks and Python plus Windows PowerShell 5.1 read-only
preflights. The immutable running `090-r2` retains the bounded startup and
menu-stop evidence in [LIVE-090](docs/research/LIVE-090.md).
The previously tested `087-r1` and prepared, unlaunched `086-r1` folders remain
immutable.

The final 0.8.4 candidate passed 329 production and 633 developer tests, with
unchanged sources and no skips. Its 39 payloads plus manifest passed real pyMHF
folder discovery, Python-only dispatch and all six temporary preference paths.
Both actual Windows PowerShell 5.1 `-CheckOnly` and Python `--check-only` passed
against the selected installation/runtime without launch or staging. A native
Python probe regression covers legacy PowerShell argument quoting; target-path
tests count UTF-16 units, including non-BMP characters. No new live behavior
has been verified by these checks.

The current registered source is **0.5.1-experimental**, paired with menu **0.9.1-diagnostics** for **0.9.2-play-trial**; its first packaged background start is recorded in [LIVE-092](docs/research/LIVE-092.md). The prior **0.5.0 / 0.9.0 / 090-r2** was closed normally before that launch. The retained **0.8.7-play-trial** has production **0.4.9** and menu **0.8.5-branding**. Retained **0.8.4-play-trial** has production **0.4.7** and menu **0.8.3-settings-trial**. Earlier artifacts remain unchanged. The target remains Windows x64, Steam build 25442159 / Cosmos 7.04, the exact executable hash in `manifest.json`, and pyMHF 0.2.4. The development launcher accepts Python 3.11–3.13 x64.

The PowerShell launcher's `-CheckOnly` path validates package integrity, the
supported game and the existing runtime without creating files/directories,
installing dependencies, staging assets or starting a host/game. It is usable
while NMS runs. Missing prerequisites are reported rather than repaired; a
successful preflight is not evidence of in-game behavior.

Normal setup and the host hold separate fixed Windows session mutex leases,
`Setup.v1` and `Host.v1`, independent of the package directory. Their ownership
is the lifetime of the OS handles, not a lock file or a remembered PID. The
lease ends when its last handle closes, including after a crash. Duplicate
launches are refused across folders. An error enumerating processes prevents
normal setup rather than being treated as evidence that the game is closed.
The 0.9.1 and 0.9.2 combined candidates set `gui.shown = false`; standalone
developer configuration still shows the panel. Packaged background startup and
native registration are observed; interactive/visible quiet startup, shutdown,
restart and native localization remain unverified; this revision does not change native hooks, summon rules or input.

The 0.9.0 menu opts into seven tagged None children on one flat page. Existing
roles 0–5 remain `enabled`, `selection_mode`, `prefer_same_biome`, `planets`,
`space_stations` and `nexus`; role 6 appends `rotate_companions`. Explicit legacy
six-role and one-child helper contracts remain supported.
The bridge resolves the existing production instance, captures one selected
preference and queues only that key under its existing lock. Other queued keys
and the manual favourite are preserved. Mode cycles last_manual → random → by_habitat;
the other controls flip Booleans. All three locations may be disabled. Pending
and session-only captions retain their existing meaning. Legacy trials keep
their one-child default. Full-page navigation and preference application remain
incomplete in-game. The combined 0.9.1 candidate does not create the pyMHF
control window; the standalone developer script retains it.

Eight original DDS icons belong to the 0.9.0 combined development bundle.
Its launcher validates the entire fixed set before staging unique assets while
the game is closed; packaging itself never deploys.
An exact-build natural `LoadResources` AFTER callback makes one registration
attempt. Its owner and buffers are pinned before native resource operations;
it retains a verified original paw as fallback and never writes the menu's paw
field. Fresh bounded manager/resource identity and readiness checks choose a
usable handle without new native calls. No destructor, retry or late-load path
is installed. Screenshots from 0.8.4 confirm the six distinct setting icons. HUD appearance
and ownership during native teardown remain acceptance boundaries. Production 0.4.7 retains the optional idempotently
bound notice provider; absent/invalid providers yield text-only HUD notices.
The standalone ZIP does not include the custom asset or native settings page.

The parent and notices use the original paw/arrow. The seven children use power,
companion selection, biome, planet, station, Anomaly and rotation icons respectively.
An unavailable child icon falls back independently to the retained native paw.
The biome row reads `Random: prefer matching biome`; its value remains stored
but affects neither Last selected nor By habitat. The source ZIP includes draft locale
catalogs and their minimal validation sources so its `build.py` remains usable.
Catalogs are not yet consumed by the runtime; native text remains English.

Manual-favourite learning now requires a paired native companion UI action 46,
one matching accepted local queue, and a successful original result. The pair
copies and revalidates the full identity, application, save context and native
thread; the AFTER callback never rereads the original action pointer. Unknown
accepted queues cancel pending automatic intent but cannot replace the favourite
or show its confirmation. Native battle restoration can reach the queue directly;
the actual caller in the earlier arena report remains unknown. Existing stored
choices are preserved. Attribution failures stop learning, not automation.

Production adds BEFORE/AFTER callbacks to the same `TriggerAction` target already
used by the menu, RVA `0x1526940`, with unchanged `bool(pointer, pointer, bool)`
ABI and `None` callback returns. The preceding 0.7.2 bundle has nine production and eight menu
callbacks over eleven distinct managed targets. This is shared framework
dispatch, not a second native detour at that address; the native binding guard
is unchanged. Both callback orders passed the real Python registry/compound
dispatch check with all four Boolean combinations and one mocked original call.

Explicit confirmations request 5.5 seconds. Production 0.5.1 reports every
effective preference change through `settings_change_notice(previous, requested,
saved)`: canonical setting order, exact ON/OFF or mode values, one combined
message and one session-only suffix if persistence fails. No-op requests remain
silent and do not cancel existing summon intent. The complete English ASCII
message must fit 511 bytes; text is not truncated. Existing latest-notice delivery
is unchanged. All fourteen catalogs reuse the translated menu labels/values via
`hud.settings_applied` and `hud.setting_separator`; the offline renderer accepts
`settings_notice(changes=..., saved=..., locale=...)` and falls back as a whole
if translated text exceeds its byte bound. These helpers add no native calls,
game-save writes or preference semantics. A changed manual identity says
`Companion saved.` only after persistence succeeds, otherwise
`Companion selected (session only).`; OFF/Random context is appended as needed.
Repeated choices, automatic requests and game restoration remain quiet. The
existing eleven-argument timed-message ABI, owned text/colour/empty-icon buffers
and silent audio are preserved. The statically verified final Boolean hides
both icon containers when the optional provider returns no usable handle;
otherwise the validated owned icon is supplied. Visual verification is pending.

After a matching native queue acceptance, policy intent is still consumed.
A separate observer samples only the existing verified fields through the
local ownership callback. It stops after 15 seconds or 4096 observer callbacks,
with at most eight transition logs. These are diagnostic caps, not summon
delays or retry conditions. A matching active index is an intermediate logical
observation, and subsequent active/pending transitions remain observable until
the existing limits or cancellation. A terminal record states whether logical
activity was ever seen and includes the last sampled indices; rendering and
removal causes remain unverified. Queue disappearance alone is indeterminate. A manual
dismissal cannot re-arm this observer or the policy. Context changes, a new
trigger, preferences, manual selection/preview/emote and invalid state end it.
Observer failures do not disable working automation. It adds no native calls,
hooks, offsets, preference fields or game-save writes.

The retained 0.8.7 bundle pins its preference bridge to the versioned 0.4.9
initializer; immutable 0.8.6-r1 and 0.8.4 retain their 0.4.8 and 0.4.7 bridges.
It keeps the production control lock, queue, application callback
and two-Mod discovery contract. The additional resource callback belongs to
the menu Mod. Old artifacts are retained; the previously tested 0.8.7-r1 folder is immutable.

Historical 0.4.5 / 0.7.2 offline validation passed **279 production tests** (189 runtime, 34 policy,
14 persistence, 24 settings, 18 launcher) and **408 developer tests**. Actual
pyMHF 0.2.4 / Dear PyGui checks passed with nine production callbacks, eight
widgets and zero hotkeys. The generated 0.7.2 folder passed two-Mod discovery,
17-callback/11-target registration metadata, shared Python dispatch and temporary
preference-bridge checks; its PowerShell launcher parsed successfully. Shared
dispatch used a disabled menu and a mocked native original. No game access or
native hook binding occurred. Historical 0.4.4 / 0.7.1 had 253 production and
408 developer tests and registered in-game at 22:22:35 on 27 September 2026.

Earlier production 0.4.3 added a deferred, one-shot opportunity after a successful local save load to the existing ship-exit behavior. One station startup in Random mode was confirmed by both log and user, without a ship exit. Those results are historical evidence for that version, not live validation of 0.4.7. Current validation is recorded in the manifest; prior test counts do not validate the new launcher work.

| Component | Responsibility |
|---|---|
| `src/policy.py` | Shared timing, pending-request and cancellation decisions |
| `src/selection.py` | Pure habitat groups, reservations and session-only rotation bags |
| `src/persistence.py` | Per-save manual companion identity and atomic local storage |
| `src/settings.py` | Validated global preferences, schema migration and atomic storage |
| `src/runtime.py` | Exact-build guards, native callbacks, placement checks, settings panel and HUD |
| `build.py` | Concatenates these components into the standalone `CompanionAutoSummon.py` |
| `Launch-CompanionAutoSummon.py` | Host-side DLL address/path validation before invoking pyMHF |
| `Start-CompanionAutoSummon.ps1` | Read-only preflight or guarded development setup and launch |
| `tests/` | Offline decision, storage, adapter and launcher checks |

Function addresses are relative to the loaded game module. Runtime objects and save identities are obtained from the running game. An exact executable hash guard disables Companion Auto Summon before hook registration on unsupported binaries. This supports portability of the addressing scheme for the same binary; it does not prove second-PC, multiplayer or cross-platform compatibility.

Schema 4 fresh defaults are By habitat and rotation ON. Schema 1 explicitly retains last_manual; schemas 2/3 retain previous mode/biome/location choices and migrate with rotation OFF, without writing until explicit save. Random retains its exact-biome preference and unrestricted native-eligible fallback. By habitat uses only its approved groups, with the neutral-location and wait/skip rules above. A selected identity/slot/context is fixed for the request; removal, ambiguity or pending-slot/context change cancels instead of redrawing. Reorder between opportunities preserves cycle history. Only accepted queues consume rotation, and local load/application boundaries reset bags; network loads do not. Preferences never dismiss an active pet or overwrite the manual favourite.

Successful local `LoadFromData` completion records one deferred opportunity when automation is enabled and common data is available. It makes no native summon, ownership-eligibility or placement function calls. A zero persistent ID still allows a session-only Random opportunity; it does not restore another save's favourite. Network-client loads leave the local context alone, and failed local loads create no opportunity.

The existing local ownership-update callback observes active/queued pets, preview/emote state, location and advancing time before preparing the load request. Last-manual identity restoration retries at the existing 0.5-second pace while the saved companion is unresolved; absence on the first frame is not proof of removal. No saved/manual choice finishes that opportunity without selecting another pet. Random uses the existing eligible pool. Once prepared, the opportunity is consumed before entering the same policy, unchanged 1.5-second stability delay and native placement/queue path used by a ship exit. No new hook, native offset, gameplay limit or preference is required.

Accepted manual selection, ship entry, a real local ship exit, applied preference changes, a later local load, unavailable/replaced application context or a runtime stop cancel or supersede the deferred opportunity. Active/queued pets and preview/emote observations consume it even while paused or outside supported locations. Supported locations disabled by the player cancel it; unsupported locations wait without placement calls. The first application acquisition preserves the opportunity, while a later replacement cannot inherit it. A dismissed pet does not re-arm a completed opportunity; only another successful local load or real ship exit can start one. This contract does not claim that deserialization proves ownership or physics readiness.

GUI callbacks queue preference changes under a lock. The local player callback applies them. Native game operations belong to the established game callbacks, never to an installer or asynchronous GUI thread.

The historical 0.7.0 play-trial candidate enabled the first native menu preference
without changing the production script: `tools/quick_menu_toggle.py` recognizes
the selected child, `tools/quick_menu_preferences.py` resolves the actual
registered production instance and queues only `enabled` under its existing
control lock. Do not import or instantiate production again to obtain that
instance. Applied/desired/pending and session-only display state come from the
same instance. A one-use token rejects a replaced/stopped instance, an applied
or replaced queue, or a changed enabled request; unrelated requests survive.
There is no preference revision counter in 0.4.3, so an identical enabled write
within the same queue cannot be distinguished. Hot reload remains unsupported.

The native confirmation predicate adds one paired hook target. Its false-to-true
transition authorizes only the next matching selected-child trigger on the same
menu/native thread, followed by the original false result and fresh topology,
guard and preference checks. Tail/slot-only triggers cannot toggle. A release
must first be observed, including when holding confirmation while entering the
submenu. All callback arguments/results are preserved. See `QUICK-MENU.md` for
the exact-build evidence and live acceptance boundary.

Play trial 0.7.0 registered at 21:48:38 on 27 September 2026 after normal
game exit and a fresh hash-verified backup of 43 profile files. Both Mods and
11 hook targets loaded with automation ON. All 14 payloads remained unchanged;
the initial startup check found existing settings and companion memory unchanged.
The game window was subsequently responding despite an initial missing-window
warning. Subsequent player feedback and logs support basic ON/OFF application,
but held input, remapping/controllers and complete navigation remain unverified.
Anomaly startup accepted a native queue without a visible pet. That 0.4.3
runtime consumed intent at queue acceptance and performed no post-queue active-pet
observation. Diagnose that lifecycle before authorizing retries: disappearance
alone cannot distinguish failed materialization from a manual dismissal.
The player's screenshot confirms HUD text rendering with an unwanted white disc.

One Random-mode Anomaly startup is now confirmed for 0.4.4 / 0.7.1. On 27 September 2026, load arming at 22:23:39.698 led to native queue acceptance at 22:23:42.250 (logged 2.56 seconds). The new observer recorded the expected active companion at 22:23:42.266, on its first update, then stopped. The player confirmed visible appearance. No ship exit or automatic retry preceded this result. This is one successful run, not a fix for the earlier intermittent failure; only passive diagnostics changed.

## Naming and compatibility

The external title is **Companion Auto Summon for No Man's Sky**, with **by Lineum Dynamics** as the author credit. The in-game short title remains **Companion Auto Summon**; the repository slug is `nms-companion-auto-summon`. The canonical private GitHub repository is [lineum-dynamics/nms-companion-auto-summon](https://github.com/lineum-dynamics/nms-companion-auto-summon). The transfer and privacy have been verified; a push is a separate operation and must be confirmed by reading back the remote commit. This attribution does not assign a licence or change third-party rights.

The standalone file is `CompanionAutoSummon.py`, with `Launch-CompanionAutoSummon.py` and `Start-CompanionAutoSummon.ps1`. The pyMHF class and its current tab are `CompanionAutoSummon`. Preserve the framework's inherited class identity: overriding `_mod_name` independently breaks its loader/reload and GUI mappings. Do not export a second legacy alias for the Mod class, which the loader can discover as an additional mod.

Keep `%LOCALAPPDATA%/NMS-AutoPet/state.json`, `settings.json` and `runtime-0.2.4` at their legacy paths. This compatibility namespace intentionally survives the rename, preserving preferences, per-save manual selections and the prepared development environment without migration. Stored keys, schema versions and selection values are unchanged. Never rename an existing venv as a branding operation.

Only the current source and new packages receive the new names. Historical test records, immutable checksums and old installed/exported copies keep their original names. Document a later deployment explicitly; a source rename is not a deployment.

## Documentation map

- `README.md`: canonical English player guide, supported target, behavior, setup and removal.
- `README.cs.md`: Czech companion guide; keep behavior and status aligned with the English guide.
- `DEVELOPMENT.md`: canonical development rules, architecture and maintenance workflow.
- `DESIGN.md`: accepted player-experience direction, native menu/notification goals and current implementation limits.
- `QUICK-MENU.md`: exact-build menu investigation, retained observers, bounded historical six-setting/icon evidence and current seven-row acceptance checks.
- `docs/research/LIVE-084.md`: failed Nexus startup, successful later ship exit with another Random pet, and limits of the current evidence.
- `docs/release/MONETIZATION.md`: dated primary-source policy review, proposed free distribution and unsent clarification drafts.
- `ROADMAP.md`: canonical unfinished release backlog and explicitly unapproved future proposals; update status and evidence as decisions are made.
- `LOCALIZATION.md`: localization status, target languages and implementation/verification requirements.
- `CHANGELOG.md`: version-scoped changes; update with each user-visible behavior or distribution change.
- `TECHNICAL-VERIFICATION.md`: canonical English technical evidence and version-scoped history. Retained private evidence is named as an external record; it is not distributed or linked through nonexistent repository paths.
- `manifest.json`: exact package hashes and bounded validation claims; generated during packaging.

The release-preparation documents in `docs/release/` contain the publication plan (`RELEASE-PREPARATION.md`), installer acceptance criteria (`INSTALLATION-REQUIREMENTS.md`) and English draft Nexus page (`NEXUS-DESCRIPTION-DRAFT.md`). Private test evidence is retained outside this repository and the public package. Do not copy that evidence directory wholesale into a release to repair documentation links.

## Repository commands

Run these from the repository root with a supported Python interpreter:

The `tools/` commands below belong to the Git source checkout; they are not included in the player ZIP.

```text
python -B build.py
python -B tools/validate_offline.py
```

The offline suite needs no running game. Validation reports are generated under `build/validation/` and ignored by Git.

Run `python -B tools/framework_smoke.py` with an interpreter containing the supported pyMHF 0.2.4 GUI dependencies. This command constructs the real GUI widgets without a viewport or game connection and writes its report alongside the offline results. It is an explicit development verification step, not a player installation requirement for the planned portable release.

After both reports match the current source, run `python -B tools/package.py`. It regenerates package hashes and creates a verified ZIP in `dist/`. It never deploys the package, starts NMS or copies files into an installation. The generated `CompanionAutoSummon.py` and `manifest.json` are retained in Git so each committed baseline includes its exact standalone script and distribution metadata; rebuild and refresh them before committing relevant changes.

Before a local commit, inspect `git diff` and `git status --short`. Save only the intended source, documentation and tooling. Remote publication is a separate step; a local commit is not a backup on another machine.

## Validation and maintenance

Run `python -B build.py` after changing source fragments. Run meaningful affected tests; the current full offline suite is `python -B -m unittest discover -s tests -v`. Historical version 0.4.3 passed 230 production tests: 140 runtime, 34 policy, 24 settings, 14 persistence and 18 launcher. The 0.6.2 developer baseline passed 341 tests; the 0.7.0 native-toggle candidate passed 408, including 67 new child/bridge/adapter regressions. Its real production GUI and actual-folder smoke passed with two Mods, 15 callbacks across 11 targets and a real Python preference-queue/apply check using temporary files, without game access or hook registration. Those checks do not validate later source changes. Current hashes and bounded validation claims are recorded in `manifest.json` and the development validation reports. The historical 0.4.2 candidate passed 212 production tests; AutoPet 0.4.1 had 211. Tests use simulated native calls and owned buffers; passing them does not verify a game's binary interface or actual spawning.

The real-framework smoke check separately verifies widget construction and callbacks without hook registration or a game connection. Record the exact source bytes tested. After gameplay changes, collect relevant live evidence for that version, including the player's visible result. Never copy a previous version's live-success flag into a new release merely because its tests pass.

For every behavior or packaging change:

1. Update the relevant guide, defaults, known limits and locale resources where applicable.
2. Record relevant validation and unresolved cases with the exact version.
3. Rebuild and regenerate package hashes from the verified files.
4. Check extracted package contents, documentation links and data privacy.
5. Deploy only with the game closed; perform the live scenarios affected by the change.

## Remaining release work

The 0.6.2 combined trial registered production 0.4.3 and the ordered menu at 20:42:21 on 27 September 2026, with automation ON and two Mods/ten managed hooks. Its station load opportunity armed at 20:42:58.578, waited for native ownership eligibility, selected slot 1 from five eligible companions at 20:43:01.260 and queued it successfully at 20:43:01.261 (about 2.69 seconds after arming). No ship-exit arm precedes that startup request. The user confirmed the pet appeared after loading on the space station. This is one Random-mode station result, not Nexus evidence.

The player later confirmed one manual dismissal without reappearance in the same unchanged session, after traveling. Exact location, dismissal timing and duration were not independently established; this is not a controlled dismissal immediately after startup. Planet/Nexus startup, startup in Last-manual mode, broader dismissal regression, biome preference, second-PC installation, multiplayer and other placement/control scenarios remain unverified for 0.4.3. Production 0.4.2 previously registered in the 0.6.1 trial and logged an accepted station queue at 20:18:19 without separate visible-pet confirmation. Earlier statements that 0.4.2 had never launched describe its original rename checkpoint. Historical successes of 0.4.0 and earlier remain separate evidence in the guides.

The proposed public installer is a portable, offline bundle with a tested private runtime and a graphical launcher. It has not been built. The existing development venv is not portable and must not be redistributed as if it were self-contained.

Localization is also not implemented. Current UI and HUD messages are English. See `LOCALIZATION.md` before changing display strings or claiming translated support.
