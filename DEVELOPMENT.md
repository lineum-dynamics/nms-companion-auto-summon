# Companion Auto Summon development guide

Current candidate validation: **333 production and 633 developer tests passed** without failures, skips or source changes. The separate 40-file 0.8.5 folder passed real-framework discovery, shared Python dispatch and all six temporary preference paths; no native binding or game access occurred. The retained 0.8.4 payloads remain unchanged.

The current source candidate is **0.8.5-play-trial**, with production **0.4.8**
and unchanged menu **0.8.3-settings-trial**. It retains the passive observation
window after the first logical active index, without adding retries or changing
summon behavior. It is not launched. The running **0.8.4** bundle is immutable.
Its registration and six distinct setting icons are confirmed, but the player
reported a failed visible Nexus startup. A later ship exit in the same session
summoned a different Random companion successfully. See
[the bounded live record](docs/research/LIVE-084.md); these two runs do not
establish the cause or an intermittent-failure fix.

This repository is the canonical development location. Keep installed test copies and prior exports as deployment artifacts, not as competing source trees. Record live observations against the exact version; neither the historical 0.4.2 rename nor the new 0.4.3 load trigger inherits earlier gameplay verification.

## Project rules

- Write all source code, identifiers, comments, docstrings, test names, build scripts and developer diagnostics in English.
- Put translated player-facing text in separate locale resources. English is the canonical source language. Non-English text belongs in translation data or deliberately encoded Unicode test fixtures, not explanatory source prose.
- Update implementation, relevant tests and affected documentation in the same change. Do not leave the description of defaults, behavior, setup or support scope behind the code.
- Review locale impact on every change. Update English and all affected translations together when text or meaning changes. Run `python -B tools/validate_locales.py`; the maintained standalone build, combined build and source packaging also run it before writing outputs. Draft completeness does not establish runtime support or language review.
- Preserve native ownership, summon eligibility and placement checks. Do not generate or unlock companions, reduce gameplay limits, accelerate growth or alter game-save files.
- Never edit a running installation or terminate the game or its runtime as part of routine deployment. Preserve current progress before a new live trial.
- Keep personal saves, settings, accounts, logs, raw executable analysis and developer-machine paths out of public packages.

## Current implementation

Repository-only native text preparation now renders the existing catalogs from
an immutable validated snapshot, preserving whole-message state within the
127-byte menu / 511-byte HUD payload limits. Fifteen focused tests and the
1,666-case language/state matrix passed. No catalog meaning, production import
or prepared play-trial payload changed. The exact-build static language field
is identified; readiness and actual UTF-8/glyph behavior are not verified.
See [native localization preparation](docs/research/NATIVE-LOCALIZATION-AUDIT.md).

The repository-only noninteractive host import prototype passed seven focused
tests and a real console-free pyMHF import comparison, including its negative
control. Existing hosts do not import it. Target-side initialization, host/game
lifecycle and a portable dependency bundle remain unverified. See
[portable runtime preparation](docs/research/PORTABLE-RUNTIME-AUDIT.md).
The full repository developer suite passed 655 tests with no failures or skips,
including these 22 new preparation tests. The original 633-test evidence above
still belongs to the unchanged 0.8.5 bundle, not to newly integrated features.

The earned-technology work is an **offline prototype**, separate from both
production and the prepared combined trial. Its pure model, pinned native-data
builder and six additional technology catalog entries do not gate the current
mod, consume inventory or write a save. See
[technology prototype](docs/research/TECHNOLOGY-PROTOTYPE.md) for evidence and
remaining native transaction/persistence work. The catalogs now contain 39 keys
in each of 14 languages; thirteen remain unreviewed drafts.

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

The final 0.8.4 candidate passed 329 production and 633 developer tests, with
unchanged sources and no skips. Its 39 payloads plus manifest passed real pyMHF
folder discovery, Python-only dispatch and all six temporary preference paths.
Both actual Windows PowerShell 5.1 `-CheckOnly` and Python `--check-only` passed
against the selected installation/runtime without launch or staging. A native
Python probe regression covers legacy PowerShell argument quoting; target-path
tests count UTF-16 units, including non-BMP characters. No new live behavior
has been verified by these checks.

The production source is **0.4.8-experimental**, prepared for **0.8.5-play-trial**. Last-launched **0.8.4-play-trial** retains production **0.4.7** and menu **0.8.3-settings-trial**. Earlier artifacts remain unchanged. The target remains Windows x64, Steam build 25442159 / Cosmos 7.04, the exact executable hash in `manifest.json`, and pyMHF 0.2.4. The development launcher accepts Python 3.11–3.13 x64.

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
The portable public installer, final GUI retirement and localization remain
unfinished; this revision does not change native hooks, summon rules or input.

The 0.8.0 menu opts into six tagged None children on one flat page: `enabled`,
`selection_mode`, `prefer_same_biome`, `planets`, `space_stations` and `nexus`.
The bridge resolves the existing production instance, captures one selected
preference and queues only that key under its existing lock. Other queued keys
and the manual favourite are preserved. Mode cycles between existing values;
the other controls flip Booleans. All three locations may be disabled. Pending
and session-only captions retain their existing meaning. Legacy trials keep
their one-child default. Full-page navigation and preference application remain
unverified in-game; the development panel stays available.

The seven original DDS icons belong to the combined development bundle.
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

The parent and notices use the original paw/arrow. The six children use power,
companion selection, biome, planet, station and Anomaly icons respectively.
An unavailable child icon falls back independently to the retained native paw.
The biome row reads `Random: prefer matching biome`; its value remains stored
but has no effect in Last selected mode. The source ZIP includes draft locale
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

Explicit confirmations request 5.5 seconds. A changed manual identity says
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

The prepared 0.8.5 bundle pins its preference bridge to the versioned 0.4.8
initializer; immutable 0.8.4 retains its 0.4.7 bridge. It keeps the production control lock, queue, application callback
and two-Mod discovery contract. The additional resource callback belongs to
the menu Mod. Old artifacts are retained; the active 0.7.1 folder is immutable.

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
| `src/persistence.py` | Per-save manual companion identity and atomic local storage |
| `src/settings.py` | Validated global preferences, schema migration and atomic storage |
| `src/runtime.py` | Exact-build guards, native callbacks, placement checks, settings panel and HUD |
| `build.py` | Concatenates these components into the standalone `CompanionAutoSummon.py` |
| `Launch-CompanionAutoSummon.py` | Host-side DLL address/path validation before invoking pyMHF |
| `Start-CompanionAutoSummon.ps1` | Read-only preflight or guarded development setup and launch |
| `tests/` | Offline decision, storage, adapter and launcher checks |

Function addresses are relative to the loaded game module. Runtime objects and save identities are obtained from the running game. An exact executable hash guard disables Companion Auto Summon before hook registration on unsupported binaries. This supports portability of the addressing scheme for the same binary; it does not prove second-PC, multiplayer or cross-platform compatibility.

The default mode remembers the last manually summoned pet per save. Random mode uses the native-eligible owned pool, optionally narrowed to the planet's native habitat. Unknown habitat or an empty matching subset falls back to the full eligible pool. A selected pet remains fixed for that request and does not overwrite the manual favourite. Preference changes cancel pending intent without dismissing an active pet.

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

The public name is **Companion Auto Summon**; the repository slug is `nms-companion-auto-summon`. The private GitHub repository is [TomasTriska88/nms-companion-auto-summon](https://github.com/TomasTriska88/nms-companion-auto-summon). Remote existence and privacy have been verified; a push is a separate operation and must be confirmed by reading back the remote commit.

The standalone file is `CompanionAutoSummon.py`, with `Launch-CompanionAutoSummon.py` and `Start-CompanionAutoSummon.ps1`. The pyMHF class and its current tab are `CompanionAutoSummon`. Preserve the framework's inherited class identity: overriding `_mod_name` independently breaks its loader/reload and GUI mappings. Do not export a second legacy alias for the Mod class, which the loader can discover as an additional mod.

Keep `%LOCALAPPDATA%/NMS-AutoPet/state.json`, `settings.json` and `runtime-0.2.4` at their legacy paths. This compatibility namespace intentionally survives the rename, preserving preferences, per-save manual selections and the prepared development environment without migration. Stored keys, schema versions and selection values are unchanged. Never rename an existing venv as a branding operation.

Only the current source and new packages receive the new names. Historical test records, immutable checksums and old installed/exported copies keep their original names. Document a later deployment explicitly; a source rename is not a deployment.

## Documentation map

- `README.md`: canonical English player guide, supported target, behavior, setup and removal.
- `README.cs.md`: Czech companion guide; keep behavior and status aligned with the English guide.
- `DEVELOPMENT.md`: canonical development rules, architecture and maintenance workflow.
- `DESIGN.md`: accepted player-experience direction, native menu/notification goals and current implementation limits.
- `QUICK-MENU.md`: exact-build menu investigation, retained observers, bounded six-setting/icon evidence and staged acceptance checks.
- `docs/research/LIVE-084.md`: failed Nexus startup, successful later ship exit with another Random pet, and limits of the current evidence.
- `docs/release/MONETIZATION.md`: dated primary-source policy review, proposed free distribution and unsent clarification drafts.
- `ROADMAP.md`: canonical unfinished release backlog and explicitly unapproved future proposals; update status and evidence as decisions are made.
- `LOCALIZATION.md`: localization status, target languages and implementation/verification requirements.
- `CHANGELOG.md`: version-scoped changes; update with each user-visible behavior or distribution change.
- `TECHNICKE-OVERENI.md`: existing Czech technical evidence and version-scoped history. Retained private evidence is named as an external record; it is not distributed or linked through nonexistent repository paths.
- `manifest.json`: exact package hashes and bounded validation claims; generated during packaging.

The release-preparation documents in `docs/release/` contain the publication plan (`PRIPRAVA-VYDANI.md`), installer acceptance criteria (`INSTALACE-ZADANI.md`) and English draft Nexus page (`NEXUS-DESCRIPTION-DRAFT.md`). Private test evidence is retained outside this repository and the public package. Do not copy that evidence directory wholesale into a release to repair documentation links.

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
