# Companion Auto Summon for No Man's Sky

by **Lineum Dynamics**

Source candidate **0.5.0-experimental / 0.9.0-play-trial**, with menu
**0.9.0-selection**, implements **By habitat** and **Shuffle companions**.
Offline validation passed 396 production and 683 developer tests; this candidate has not launched.
The previously tested **0.8.7 / 087-r1** remains unchanged. By habitat uses explicit
13/5/1 weighted habitat groups on planets and an unweighted eligible pool on
stations/Nexus; rotation keeps a separate session cycle without changing native
eligibility or placement. Fresh installs default to By habitat and rotation ON.
Existing schema 1/2/3 settings preserve their choices with rotation OFF.
See [selection semantics and limits](docs/research/HABITAT-SELECTION.md).

The retained branding candidate **0.8.7-play-trial** pairs production
**0.4.9-experimental** with menu **0.8.5-branding**. Source validation passed
**333 production and 675 developer tests**, without failures or skips. Real-framework
checks covered both Mods and all six temporary preference paths; Python and
Windows PowerShell 5.1 read-only preflights passed.
The separate final folder is `build/quick-menu-play-trial-087-r1`, with 41 files;
its focused locale, framework and both preflight checks also passed after a
Korean translation correction.
The full title is used outside the game, while
the in-game title remains **Companion Auto Summon**. Existing code identifiers,
filenames and player-data paths are retained.

The candidate retains extended passive summon diagnostics and read-only native
language observation. It does not select a translation or fix the intermittent
Nexus startup issue. The previously prepared **0.8.6-r1** remains unchanged;
its test and preflight results belong to that artifact, not to this new candidate.

The final **0.8.7 / 087-r1** launched on 28 September 2026 after normal game
closure and a fresh verified 46-file backup. Both Mods and twelve targets
registered at 11:07:26 (Europe/Prague). The player confirmed visible Random
companions in the Nexus **after both loading and leaving the ship**. After a
requested manual dismissal, the player reported no apparent reappearance; the
wait was not independently timed. These were different pets; the two summons
do not explain or prove a fix for the
[earlier 0.8.4 failure](docs/research/LIVE-084.md). Initial post-start checks
found all 40 payloads and existing settings/state unchanged. The language
observer recorded native English, without enabling translations or proving
reload readiness. The player also confirmed one native OFF/ON sequence: OFF
prevented a ship-exit summon, ON alone summoned nothing, and the next exit
summoned a pet. Other controls, remapping, HUD/icons, repeatability, Last selected and
multiplayer remain unverified. See [the bounded 0.8.7 record](docs/research/LIVE-087.md).

Fourteen catalogs now contain 46 keys, including the new selection/rotation labels,
habitat notices and one scoped development-panel status. Product name and author
credit remain covered. Three launcher messages use the expanded title. Only the nine launcher compatibility
messages use them during launch; the thirteen translations remain unreviewed
drafts. Native menu/HUD text remains English. Full launcher translation and the
portable public installer are unfinished. See [LOCALIZATION.md](LOCALIZATION.md).

0.8.2 startup registered both Mods and 12 native targets at 23:58:46 on 27 September 2026 after a verified 43-file backup. Automation is ON; all 17 payloads and the existing player files matched. The original DDS was staged and hash-verified. Visible icon/HUD, all six controls and gameplay still need the player's check. Validation: 294 production and 519 developer tests, plus real Windows lease and pyMHF checks.

[Czech user-guide translation](README.cs.md)

The canonical source is [lineum-dynamics/nms-companion-auto-summon](https://github.com/lineum-dynamics/nms-companion-auto-summon), currently a private repository. Development commands and the maintained documentation map are in [DEVELOPMENT.md](DEVELOPMENT.md). The installed test copy and exported ZIPs are built outputs.

The earlier **0.4.7 / 0.8.2-play-trial** candidate improved the development
launcher. `-CheckOnly` checks the package, supported game and existing runtime
while NMS can remain running; it creates, installs and starts nothing. Normal
setup and the running host use separate Windows session leases, `Setup.v1` and
`Host.v1`, to reject duplicate launches even from different package folders.
These leases end when their last operating-system handle closes, including
after a crash. If process enumeration fails, normal setup refuses to continue.

Production 0.4.7 changes only version metadata from 0.4.6. Installed 0.8.2 retains
**0.8.0-settings-trial**. Prepared 0.8.3 introduced the same six controls with
distinct icons and the explicit `Random: prefer matching biome` label; 0.8.4
retains that menu unchanged. The prior 0.7.1, 0.7.2 and 0.8.0 artifacts remain
unchanged. A successful check-only run is not an in-game test.

The running 0.8.7 retains all six existing
preferences on one native companion settings page: automatic summoning,
Last selected/Random, matching-biome preference, planets, space stations and
the Space Anomaly. It shares the production preference queue and stored values;
the temporary desktop panel remains available during development. The new page
has partial live evidence in 0.8.4; the parent/notice icon still needs visual acceptance.

The retained 0.8.7 launcher validates its seven DDS files before
staging them at unique mod paths with NMS closed. No vanilla texture is replaced.
One natural resource-loading callback attempts registration; a ready custom
role icon is preferred, with a retained native paw fallback. Notifications use text
alone if neither owned icon is usable. The standalone production ZIP has no
custom asset or menu and uses text-only notices unless a validated provider is
installed. Six setting icons are visible in 0.8.4 screenshots; HUD appearance
and resource teardown lifetime still need live validation.

This candidate includes the prepared **0.4.5 / 0.7.2** repair, which learns
a manual favourite only from a matched successful native companion UI action.
An accepted queue alone, including an unattributed game restoration, cannot
replace the favourite or announce a manual choice. Existing stored choices are
preserved; the earlier arena report's live caller is unknown, so no favourite
is rolled back automatically.

Explicit confirmations now request **5.5 seconds** and use shorter, truthful
wording. A statically verified native flag hides icon containers when no usable
icon exists, retaining text. These changes are loaded in 0.8.2 but have not been
visually verified. The previous **0.4.4 / 0.7.1** installation and unlaunched **0.7.2**
artifact remain unchanged. The earlier 0.4.5 candidate passed **279 production tests** and **408
developer tests**, plus real-framework widget and combined-bundle checks without
game access. Its 17 callbacks share 11 native targets; this is offline evidence.
Earlier counts below belong to their named versions.

The preceding **0.4.6 / 0.8.0** passed **282 production tests** and **504 developer
tests**, plus real pyMHF widget/folder checks. Python-only registration and
mocked-original dispatch covered 18 callbacks across 12 targets. Every native
preference row applied through the real production instance using temporary
files, and the optional icon provider bound correctly. These checks installed
no native hooks and do not confirm texture rendering, gameplay or input.


Historical 0.4.4 / 0.7.1 passed 253 production and 408 developer tests and
registered on 27 September 2026 at 22:22:35 after a fresh verified backup.
Its passive observer and the player confirmed one Random-mode Anomaly startup.
That success does not resolve the earlier intermittent failure. Passive
observation never retries a request after queue acceptance or alters game saves.

The earlier developer trial **0.7.0-play-trial** added the first native
setting: automatic summoning ON/OFF. It queues changes through the unchanged
0.4.3 production runtime. Basic ON/OFF behavior now has partial player and log
confirmation; complete input/navigation testing remains pending. The remaining
preferences in that version still use the temporary pyMHF development panel, which will be
retired from the player interface once all native controls are complete.
This separately built candidate registered in-game on 27 September 2026 after
a fresh verified backup; two Mods and 11 hook targets loaded with automation ON.

Version 0.4.3 adds one automatic-summon opportunity after a successful local save load, so loading directly on foot can use the same placement checks as a ship exit. One Random-mode summon after loading on a **space station** is now confirmed by the log and the user. It uses the existing automation toggle and selection/location preferences; no new option or stored-data format is introduced. The settings tab remains **CompanionAutoSummon** because pyMHF uses the Python class name. Current validation is recorded in `manifest.json`.

The 0.4.3 candidate passed **230 production offline tests**, the real pyMHF settings-widget check and discovery checks for the combined 0.6.2 play trial. These checks used temporary data and no game connection or native hook registration. The combined trial subsequently registered in NMS with automation ON and two Mods/ten managed hooks at 20:42:21 on 27 September 2026.

In that session, the load opportunity armed at 20:42:58.578 in station location 2, waited for native ownership eligibility, then selected slot 1 from five eligible owned companions at 20:43:01.260. The queue was accepted at 20:43:01.261, about 2.69 seconds after arming. No ship-exit arm precedes that startup request, and the user confirmed that the pet appeared automatically after loading without entering/exiting the ship. This verifies one station startup in Random mode. The player later confirmed one manual dismissal without reappearance in this unchanged session. Its exact location and duration were not independently measured, and travel separated it from the startup test. Planet/Nexus startup, Last-manual startup, biome preference and multiplayer remain unverified for this revision.

The preceding 0.4.2 candidate adopted the approved name **Companion Auto Summon**, replacing AutoPet without changing gameplay defaults or stored data. It passed **212 offline tests** and a real pyMHF 0.2.4 / Dear PyGui 2.3.1 check: one renamed mod class, eight settings widgets, seven hook callbacks for six targets, and no hotkeys. Those checks registered no hooks and used no game or visible viewport. Later, the combined developer trial 0.6.1 registered production 0.4.2 alongside the inert menu and logged an accepted station summon request at 20:18:19. There is no new user confirmation of the pet's visible appearance from that request. Neither result verifies 0.4.3's load-triggered behavior.

Automatically request your chosen companion after leaving a starship or successfully loading a local save, where the game permits it. Remembers your choice per save and your on/off preference across restarts. Includes a settings panel and a short selection confirmation.

The preceding AutoPet 0.4.1 added **Prefer same biome in Random mode**, enabled by default. On a planet, Random first prefers eligible owned companions from the same native habitat. If there is no match or the planet's habitat is unknown, it uses the ordinary eligible pool. The option has no effect on Last manually selected, stations or the Nexus. This habitat behavior still awaits live validation; the successful 0.4.0 results below are historical.

Habitat matching follows the game's own categories, including swamp, volcanic and exotic variants; temporary weather is not used. It changes only the random candidate pool. Once a pet is chosen, moving to another habitat does not reroll it during that pending request.

The historical AutoPet 0.4.1 baseline passed **211 offline tests** and construction/callback checks for all **eight settings widgets** with real pyMHF 0.2.4 and Dear PyGui. These checks ran without a game connection, hook registration or visible viewport. Neither loading 0.4.1 in NMS nor its biome selection has been tested live yet.

Version 0.4.0 adds separate planet, space-station and Nexus preferences, an optional random-owned-companion mode, and waiting for a suitable place without a time limit. Defaults: automation on, all three locations on, last manually selected companion. One basic Random-mode summon on a planet is now verified; location preferences and deferred summoning still await live validation.

**Version 0.4.0 successfully applied the Random selection setting and summoned a randomly chosen owned pet on a planet.** On 27 September 2026, the log recorded the setting change, selection of slot 3 from three eligible owned pets, and an accepted request 2.86 seconds after ship exit. The user confirmed the pet appeared. This is one successful draw and summon; it does not verify repeated draws, distribution, all seven panel controls, settings across restarts or a return to the manual favorite after switching modes.

After the random summon, a read-only runtime snapshot confirmed that manual favorite slot 1 remained remembered while slot 3 was active. This verifies preservation in the running session, not on-disk or restart persistence. The same session successfully loaded at 13:18:11 after a fresh verified backup of all 42 profile files, with automation ON and one loaded mod with six hooks. The completed 197 offline tests remain separate evidence.

**Station auto-summoning and selection restoration after restart are verified in version 0.3.3.** The same-save test restored the saved pet and submitted one request after a ship exit on a station; the user confirmed the pet actually appeared without another manual selection. Version 0.3.3 removes our extra planet-only restriction and also admits the Nexus inside the Space Anomaly. All native permission and placement checks still run. The Nexus remains untested.

The preceding version, **0.3.2**, verified basic planetary auto-summoning and selection restoration after restart through the log and user confirmation. These are bounded successes in two tested scenarios. The package remains experimental: the Nexus, multiplayer, excluded locations, unsuitable terrain, the controls/HUD and longer-term stability still need live validation.

The first automatic summon test in 0.3.1 expired without spawning. Version 0.3.2 adds native placement refresh while the quick menu is closed and bounded diagnostics; its corrected basic path passed the test above. Offline tests cover decisions, persistence and a simulated adapter. See `TECHNICAL-VERIFICATION.md` for the evidence and remaining scope.

## Supported target

Windows x64, Steam NMS **build 25442159 / Cosmos 7.04**, Python **3.11–3.13 x64**, and **pyMHF 0.2.4**. `compatibility.json` records the supported target; a build gate checks agreement with the host, native declarations and manifest. Other game builds, stores and operating systems require additional compatibility work.

This package contains no personal saves, account credentials, preselected pet or machine-specific installation paths. Each player has their own settings. Unsupported executables are rejected before using unverified addresses.

## Settings

The **0.9.0 source candidate** has a flat seven-row page under Companion Auto
Summon in the native companion menu. Confirm a row using the game's configured
Select action: selection mode cycles Last selected → Random → By habitat; the
other six rows toggle ON/OFF. Matching-biome preference
only affects Random on planets. All three locations may be OFF. Labels distinguish
queued changes from applied state and session-only persistence. Browsing or
rebuilding the page must not change a setting. The new seven-row page and rotation icon require in-game acceptance; retain the panel below as the
development fallback.

Launch through Companion Auto Summon, then **Alt+Tab to the separate pyMHF window** and open its **CompanionAutoSummon** tab. This is a desktop settings window, not an entry inside the native NMS menu. No Companion Auto Summon keyboard shortcut is registered.

- **Automatically summon companion**: on/off checkbox, enabled by default. It covers both ship exits and successful local save loads.
- Three location checkboxes enable planets, space stations and the Nexus separately. All default on. Turning all three off prevents automatic summoning everywhere.
- **Companion selection** offers **Last manually selected**, **Random** and **By habitat**. By habitat is the fresh-install default; existing choices are preserved. Every mode retains native ownership, eligibility and placement checks.
- **Prefer same biome in Random mode** (default ON): prefers the matching native habitat within that eligible pool on planets. Turn it OFF for ordinary random selection. Unknown/no matching habitat falls back automatically; no pet is excluded from ordinary native eligibility by this option.
- **Shuffle companions**: cycles eligible pets in Random, or within the weighted group chosen by By habitat. ON for fresh installs; migrated preferences start OFF. Last selected is unaffected.
- **Status**: current state, including **Waiting for a suitable place**, pending changes, session-only persistence, or a runtime error.
- **Companion**: selected slot, a remembered choice awaiting ownership verification, or the active selection mode. In Last manually selected mode, an empty choice prompts you to summon your first companion manually.

Return to the game to apply and save a change on the next local-player update before quitting. Changing settings cancels any pending automatic request, including a load opportunity still awaiting ownership, and leaves an already active companion alone. Turning on or changing mode waits for the next ship exit or successful local save load; it never immediately summons a pet. Manual selections are still remembered while automation is off.

In Last manually selected mode, new players start with no selected companion. A successful native UI summon chooses an owned companion. A changed choice requests one silent, 5.5-second confirmation: **Companion saved.** If persistence is unavailable, it says **Companion selected (session only).** Random, habitat-selection or automation-OFF status is included when relevant. Repeating the same choice, automatic summoning and game-driven restoration remain quiet. The candidate's icon fallback and new wording still need an in-game visual check. The panel and messages remain English-only.

Random and By habitat need no previous manual choice, but require an eligible owned companion; neither replaces the manual favourite. By habitat draws exact/related/acceptable groups at weights 13/5/1, independent of group size, using an explicit mod-design table. Unknown planet data waits; an owned roster with no approved group skips this opportunity with one notice. Temporary native ineligibility waits. Rotation advances only on accepted queues; without rotation, or with one eligible member, consecutive requests may select the same pet.

## Behavior

1. In Last manually selected mode, manually summon your preferred companion once with Companion Auto Summon running. Random and By habitat need an eligible owned companion but no previous manual choice.
2. A ship exit or successful local save load supplies one opportunity. Save deserialization itself calls no summon or placement functions; the first suitable local ownership update prepares the request. The mod then uses the unchanged 1.5-second stability delay in an enabled, supported location: on foot on a planet, a space station, or the Nexus inside the Space Anomaly. No pet may be active or queued, and native ownership, eligibility and placement checks must pass.
3. If the current place is unsuitable, the request remains pending without a time limit. Walk to a suitable place and Companion Auto Summon can complete that same request; another ship entry and exit is not required.
4. In Last manually selected mode, loading the same save can restore its remembered identity without a ship exit. If ownership data is still arriving, identity lookup waits and retries at 0.5-second intervals. It never substitutes another pet at the old slot. No remembered choice means no startup summon; Random can instead wait for an eligible owned companion.
5. Manually summoning a different companion replaces that save's manual choice.

An archive platform or other temporarily unsuitable place does not expire the request; the old 12-second limit is removed. Freighters and other locations excluded by this build's native location check still cannot summon pets. While in such a location, Companion Auto Summon retains the intent and makes no native summon or placement calls; it can resume after you reach an enabled, supported location. Entering a supported location that you disabled in Companion Auto Summon settings cancels the request instead.

Re-entering the ship, a manual companion or related emote preview, an accepted manual selection, a settings change or unavailable/replaced application context cancels the request. An already active or queued companion also consumes a pending load opportunity, even before ownership is ready or while paused. Loading another local save cancels the previous request; only successful completion can supply a new opportunity. Network-client loads do not create or reset the local player's opportunity.

The load opportunity is consumed once, before the ordinary request is armed. After an accepted request, manually dismissing the pet does not repeatedly summon it again. The next real ship exit or successful local save load can create another opportunity. Automation OFF prevents either trigger.

Companion Auto Summon refreshes native placement while the menu is closed, using the game's configured range and unchanged spatial checks. It never marks an invalid position valid. Placement is checked in fresh pairs of game callbacks, with at least 0.5 seconds between pairs. If the game rejects the queue request, Companion Auto Summon waits for a fresh check and retries the same chosen pet. Once the game accepts the queue request, that opportunity is finished. Waiting on archive platforms, delayed placement and these retries still need an in-game test.

Automatic selection chooses at most one candidate per request after placement is prepared. A reserved identity and slot remain fixed; ambiguity, removal or reorder of that pending pet cancels instead of redrawing. By habitat also freezes its supported planet/neutral context; Random retains its choice across temporary location changes. Between opportunities, roster reorder preserves cycle history. Native queue acceptance alone consumes rotation; rejected placement and cancellation do not. Local save/application boundaries reset session bags; network loads do not. See [the exact contract](docs/research/HABITAT-SELECTION.md).

Growth, speed, trust, eggs, combat values and game capacities are unchanged. Companion Auto Summon does not change summon limits, unlock companions, generate pets or bypass native placement restrictions.

## Persistence

The legacy `NMS-AutoPet` data directory is intentionally retained. Do not rename it: existing manual favourites, preferences and the development runtime continue to use it. Renaming the mod does not reset or copy personal data.

Manual pet choices: `%LOCALAPPDATA%\NMS-AutoPet\state.json`, outside the game and its saves. Selections are keyed by `SaveUniversalId`; pets are matched by CreatureSeed + BirthTime. Reordered slots are supported. Initial ownership loading may delay restoration; a persistently missing or ambiguous pet requires a new manual choice. The adjacent `settings.json` uses schema 4, adding `rotate_companions` to enabled status, locations, selection mode and `prefer_same_biome` for this Windows user. Schema 1 explicitly retains Last selected; schemas 2/3 retain their selection and biome choices. All migrate with rotation OFF and preserve automation/location values. Migration is in memory until explicit save. Fresh settings use By habitat and rotation ON; stored OFF choices remain OFF.

Main-game and expedition contexts inside one save share one remembered choice. It is restored only where the pet exists. A zero save ID allows session-only selection; a successful local load with a valid common-data object can still supply a Random-mode opportunity without saving an identity. It never borrows another save's favorite. A damaged settings file is preserved, with persistence disabled for that session. The mod does not edit game save files; ordinary game autosaving continues.

If `settings.json` cannot be read, automation starts off. The panel can explicitly enable it for that session. A runtime error disables automatic summoning separately; the checkbox cannot override that safety stop.

## Launching / first test

To check an extracted candidate without starting anything, run
`./Start-CompanionAutoSummon.ps1 -CheckOnly` from PowerShell. NMS may remain
running. This mode validates available package/game/runtime prerequisites and
reports missing requirements without creating an environment, installing
dependencies, staging assets or launching the host/game. It does not validate
in-game behavior or replace the backup required before a new live trial.

For normal setup and the first live test, close NMS and back up the current save profile. Extract the package and install a supported x64 Python version if necessary. Run `Start-CompanionAutoSummon.ps1` from PowerShell.

Normal setup refuses to proceed while NMS is running or process enumeration is unavailable, detects Steam libraries, checks the game and packaged script, and creates a private environment under `%LOCALAPPDATA%\NMS-AutoPet\runtime-0.2.4`. It installs `pymhf[gui]==0.2.4`, including GUI dependencies, when needed, requiring internet on first setup, then launches Companion Auto Summon. This development runtime keeps its legacy path to reuse existing dependencies. Fixed session-wide setup and host leases reject a second launch across package folders; they do not use stale lock files or require manual cleanup after a process exits.

An optional `-GameDirectory` argument selects a game folder for preflight checks. It must match the installation used by the active Steam client: pyMHF still launches Steam app 275850.

In 0.8.4, the supported hosts verify the selected executable before importing
the framework, then verify the executable belonging to the actual target
process handle before each DLL injection. Startup also rejects unexpected
framework configuration and foreign `pymhflib` entry points. An unsupported,
changed or unreadable executable refuses mod activation with an outside-game
warning; it does not reset preferences or use an unverified native HUD.
Refusal boundaries are tested offline; a supported guarded launch also succeeded
in 0.8.4 and 0.8.7. The 0.8.7 live scope is the two Nexus Random summons
documented above, not complete gameplay or installer acceptance.

Compatibility warnings use the Windows UI locale with an optional `-Language`
override, for example `-Language fr`. This is not game-language detection.
`-NoDialog` suppresses the warning dialog while retaining console errors;
`-CheckOnly` also avoids dialogs. Invalid translation data uses a short English
package-error fallback. Other setup messages still have untranslated English.

Diagnostic logs are written to `logs` beside CompanionAutoSummon.py. The interactive Python console and separate logging window are disabled; the settings panel remains available.

Use `Start-CompanionAutoSummon.ps1` from a regular PowerShell terminal. It calls the host-only `Launch-CompanionAutoSummon.py`, which verifies DLLs by their full physical path and actual address in the game before Python code executes there. This guard does not edit installed framework files. Direct `pymhf run CompanionAutoSummon.py` bypasses this extra verification and is not the supported launch path for this package. `python CompanionAutoSummon.py` alone does not start the mod; copying it into GAMEDATA/MODS does not activate it.

Test the nine panel controls/displays and seven native rows, OFF/ON changes, individual location choices, Random mode, the biome preference and selection confirmation. Load directly on foot on a planet, station and the Nexus; confirm a single summon, then dismiss it and confirm it stays dismissed until another trigger. Also load with automation OFF or a companion already present. For the biome option, test a matching eligible pet, no matching pet, OFF, station/Nexus bypass, and an unchanged manual favorite. On an archive platform or unsuitable terrain, remain there beyond 12 seconds, then walk to a valid place and check that the waiting pet appears once. Also test normal ship exits, immediate re-entry, manual replacement, save switching and a restart. The single 0.4.3 station startup in Random mode and one later manual dismissal without reappearance are confirmed as described above; remaining startup scenarios and broader dismissal regression still need live checks. Verify multiplayer after the basic behavior works.

To disable the whole mod: quit NMS and launch normally through Steam. To forget choices, close NMS and remove only `state.json`. Removing `settings.json` restores the new-install defaults: automation ON, all three locations ON, By habitat, rotation ON, and biome preference ON for Random. It does not preserve migrated preferences.

## Source

Development rules and architecture are maintained in [DEVELOPMENT.md](DEVELOPMENT.md). Source code, comments and developer diagnostics are English. The settings panel and HUD are currently English-only; the planned language coverage and remaining work are recorded in [LOCALIZATION.md](LOCALIZATION.md). [DESIGN.md](DESIGN.md) records the native-menu and notification goals. The 0.8.2 combined candidate retains all six preferences from 0.8.0; the historical 0.7.1 had the native automation toggle, and older artifacts retain an inert **Settings preview** child. Version-scoped changes are in [CHANGELOG.md](CHANGELOG.md).

`src/` contains policy, pet persistence, settings and runtime code. `build.py` rebuilds and syntax-checks CompanionAutoSummon.py without installing or launching it. Run offline tests with `python -B -m unittest discover -s tests -v`. `manifest.json` records checksums and validation status. `TECHNICAL-VERIFICATION.md` contains version-scoped technical evidence in English. The panel uses the framework's documented [GUI properties](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/docs/docs/gui/gui.rst).

The maintained release backlog and proposed future features are in [ROADMAP.md](ROADMAP.md).

Prepared for sharing; not published to a mod service.
