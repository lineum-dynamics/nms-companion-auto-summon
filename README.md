# Companion Auto Summon 0.4.2 — experimental

[Český návod](README.cs.md)

This Git repository is the canonical source for Companion Auto Summon. Development commands and the maintained documentation map are in [DEVELOPMENT.md](DEVELOPMENT.md). The installed test copy and exported ZIPs are built outputs.

Version 0.4.2 adopts the approved name **Companion Auto Summon**, replacing the working name AutoPet. Script names, internal identifiers and visible branding change; gameplay defaults, native rules and stored data formats are retained. The settings tab is named **CompanionAutoSummon** because pyMHF uses the Python class name. This candidate has not been launched in NMS. Current offline results are recorded in `manifest.json`; the 0.4.1 results below are historical.

The renamed candidate passed **212 offline tests** and a real pyMHF 0.2.4 / Dear PyGui 2.3.1 check: one renamed mod class, eight settings widgets, seven hook callbacks for six targets, and no hotkeys. No hooks were registered, no game was connected and no visible viewport was created. Existing settings and manual-selection paths are covered by a rename regression check.

Automatically request your chosen companion after leaving a starship where the game permits it. Remembers your choice per save and your on/off preference across restarts. Includes a settings panel and a short selection confirmation.

The preceding AutoPet 0.4.1 added **Prefer same biome in Random mode**, enabled by default. On a planet, Random first prefers eligible owned companions from the same native habitat. If there is no match or the planet's habitat is unknown, it uses the ordinary eligible pool. The option has no effect on Last manually selected, stations or the Nexus. This habitat behavior still awaits live validation; the successful 0.4.0 results below are historical.

Habitat matching follows the game's own categories, including swamp, volcanic and exotic variants; temporary weather is not used. It changes only the random candidate pool. Once a pet is chosen, moving to another habitat does not reroll it during that exit.

The historical AutoPet 0.4.1 baseline passed **211 offline tests** and construction/callback checks for all **eight settings widgets** with real pyMHF 0.2.4 and Dear PyGui. These checks ran without a game connection, hook registration or visible viewport. Neither loading 0.4.1 in NMS nor its biome selection has been tested live yet.

Version 0.4.0 adds separate planet, space-station and Nexus preferences, an optional random-owned-companion mode, and waiting for a suitable place without a time limit. Defaults: automation on, all three locations on, last manually selected companion. One basic Random-mode summon on a planet is now verified; location preferences and deferred summoning still await live validation.

**Version 0.4.0 successfully applied the Random selection setting and summoned a randomly chosen owned pet on a planet.** On 27 September 2026, the log recorded the setting change, selection of slot 3 from three eligible owned pets, and an accepted request 2.86 seconds after ship exit. The user confirmed the pet appeared. This is one successful draw and summon; it does not verify repeated draws, distribution, all seven panel controls, settings across restarts or a return to the manual favorite after switching modes.

After the random summon, a read-only runtime snapshot confirmed that manual favorite slot 1 remained remembered while slot 3 was active. This verifies preservation in the running session, not on-disk or restart persistence. The same session successfully loaded at 13:18:11 after a fresh verified backup of all 42 profile files, with automation ON and one loaded mod with six hooks. The completed 197 offline tests remain separate evidence.

**Station auto-summoning and selection restoration after restart are verified in version 0.3.3.** The same-save test restored the saved pet and submitted one request after a ship exit on a station; the user confirmed the pet actually appeared without another manual selection. Version 0.3.3 removes our extra planet-only restriction and also admits the Nexus inside the Space Anomaly. All native permission and placement checks still run. The Nexus remains untested.

The preceding version, **0.3.2**, verified basic planetary auto-summoning and selection restoration after restart through the log and user confirmation. These are bounded successes in two tested scenarios. The package remains experimental: the Nexus, multiplayer, excluded locations, unsuitable terrain, the controls/HUD and longer-term stability still need live validation.

The first automatic summon test in 0.3.1 expired without spawning. Version 0.3.2 adds native placement refresh while the quick menu is closed and bounded diagnostics; its corrected basic path passed the test above. Offline tests cover decisions, persistence and a simulated adapter. See `TECHNICKE-OVERENI.md` for the evidence and remaining scope.

## Supported target

Windows x64, Steam NMS **build 25442159 / Cosmos 7.04**, Python **3.11–3.13 x64**, and **pyMHF 0.2.4**. The exact supported EXE SHA256 is in `manifest.json`. Other game builds, stores and operating systems require additional compatibility work.

This package contains no personal saves, account credentials, preselected pet or machine-specific installation paths. Each player has their own settings. Unsupported executables are rejected before using unverified addresses.

## Settings panel

Launch through Companion Auto Summon, then **Alt+Tab to the separate pyMHF window** and open its **CompanionAutoSummon** tab. This is a desktop settings window, not an entry inside the native NMS menu. No Companion Auto Summon keyboard shortcut is registered.

- **Automatically summon companion after ship exit**: on/off checkbox, enabled by default.
- Three location checkboxes enable planets, space stations and the Nexus separately. All default on. Turning all three off prevents automatic summoning everywhere.
- **Companion selection** offers **Last manually selected** (default) and **Random**. Random mode uses only owned companions accepted by the native game checks.
- **Prefer same biome in Random mode** (default ON): prefers the matching native habitat within that eligible pool on planets. Turn it OFF for ordinary random selection. Unknown/no matching habitat falls back automatically; no pet is excluded from ordinary native eligibility by this option.
- **Status**: current state, including **Waiting for a suitable place**, pending changes, session-only persistence, or a runtime error.
- **Companion**: selected slot, a remembered choice awaiting ownership verification, or the active selection mode. In Last manually selected mode, an empty choice prompts you to summon your first companion manually.

Return to the game to apply and save a change on the next local-player update before quitting. Changing settings cancels any pending automatic request and leaves an already active companion alone. Turning on or changing mode waits for the next ship exit; it never immediately summons a pet. Manual selections are still remembered while automation is off.

In Last manually selected mode, new players start with no selected companion. The first accepted manual summon selects one they already own. A new or changed choice requests a three-second, silent HUD confirmation: **Companion Auto Summon: companion selected for automatic summon after ship exit.** When automation is off, the message says so; in Random mode, it confirms the saved manual favorite while Random remains on. Repeating the same choice or restoring it after a restart does not repeat the confirmation. The panel and messages use English. The Random setting has been successfully applied in a live session; HUD rendering and the remaining panel controls still require validation.

Explicitly selecting Random does not require a previous manual choice, but the player must own an eligible companion. Companion Auto Summon never creates or unlocks one. Random selection does not replace the remembered manual companion. The same pet may be drawn on consecutive exits.

## Behavior

1. In Last manually selected mode, manually summon your preferred companion once with Companion Auto Summon running. Random mode needs an eligible owned companion but no previous manual choice.
2. After a ship exit, the mod waits for 1.5 seconds continuously in an enabled, supported location: on foot on a planet, a space station, or the Nexus inside the Space Anomaly. If no pet is active or queued and the native game checks accept the companion and placement, it requests the summon.
3. If the current place is unsuitable, the exit remains pending without a time limit. Walk to a suitable place and Companion Auto Summon can complete that same exit's request; another ship entry and exit is not required.
4. In Last manually selected mode, restarting through Companion Auto Summon and loading the same save restores the choice on your next ship exit. No new manual selection is needed.
5. Manually summoning a different companion replaces that save's manual choice.

An archive platform or other temporarily unsuitable place does not expire the request; the old 12-second limit is removed. Freighters and other locations excluded by this build's native location check still cannot summon pets. While in such a location, Companion Auto Summon retains the intent and makes no native summon or placement calls; it can resume after you reach an enabled, supported location. Entering a supported location that you disabled in Companion Auto Summon settings cancels the pending exit instead.

Re-entering the ship, a manual companion or related emote preview, a manual selection, a settings change, or a save/application-context reset cancels the request. An already active or queued companion also ends the pending exit. Loading a save by itself does not summon one. After an accepted request, manually dismissing the pet while walking is respected until the next ship exit.

Companion Auto Summon refreshes native placement while the menu is closed, using the game's configured range and unchanged spatial checks. It never marks an invalid position valid. Placement is checked in fresh pairs of game callbacks, with at least 0.5 seconds between pairs. If the game rejects the queue request, Companion Auto Summon waits for a fresh check and retries the same chosen pet. Once the game accepts the queue request, that exit is finished. Waiting on archive platforms, delayed placement and these retries still need an in-game test.

Random mode chooses at most one candidate per exit after placement is prepared. Once selected, it never rerolls during that exit. An identity change, manual selection or cancellation does not trigger a replacement draw. Identity, ownership and full native eligibility are checked again before queuing the selected pet.

Growth, speed, trust, eggs, combat values and game capacities are unchanged. Companion Auto Summon does not change summon limits, unlock companions, generate pets or bypass native placement restrictions.

## Persistence

The legacy `NMS-AutoPet` data directory is intentionally retained. Do not rename it: existing manual favourites, preferences and the development runtime continue to use it. Renaming the mod does not reset or copy personal data.

Manual pet choices: `%LOCALAPPDATA%\NMS-AutoPet\state.json`, outside the game and its saves. Selections are keyed by `SaveUniversalId`; pets are matched by CreatureSeed + BirthTime. Reordered slots are supported. In Last manually selected mode, a missing or ambiguous pet requires a new manual choice. The adjacent `settings.json` uses schema 3 to store enabled status, locations, selection mode and `prefer_same_biome` for all saves of this Windows user. Legacy schemas 1 and 2 migrate in memory with the biome preference ON while preserving their existing choices, including OFF. Schema 3 is written only on an explicit settings save; a stored OFF biome preference remains OFF.

Main-game and expedition contexts inside one save share one remembered choice. It is restored only where the pet exists. A missing/zero save ID allows session-only selection. A damaged settings file is preserved, with persistence disabled for that session. The mod does not edit game save files; ordinary game autosaving continues.

If `settings.json` cannot be read, automation starts off. The panel can explicitly enable it for that session. A runtime error disables automatic summoning separately; the checkbox cannot override that safety stop.

## Launching / first test

Close NMS and back up the current save profile before the first test. Extract the package and install a supported x64 Python version if necessary. Run `Start-CompanionAutoSummon.ps1` from PowerShell.

The launcher refuses to proceed while NMS is running, detects Steam libraries, checks the game and packaged script, and creates a private environment under `%LOCALAPPDATA%\NMS-AutoPet\runtime-0.2.4`. It installs `pymhf[gui]==0.2.4`, including GUI dependencies, when needed, requiring internet on first setup, then launches Companion Auto Summon. This development runtime keeps its legacy path to reuse existing dependencies.

An optional `-GameDirectory` argument selects a game folder for preflight checks. It must match the installation used by the active Steam client: pyMHF still launches Steam app 275850.

Diagnostic logs are written to `logs` beside CompanionAutoSummon.py. The interactive Python console and separate logging window are disabled; the settings panel remains available.

Use `Start-CompanionAutoSummon.ps1` from a regular PowerShell terminal. It calls the host-only `Launch-CompanionAutoSummon.py`, which verifies DLLs by their full physical path and actual address in the game before Python code executes there. This guard does not edit installed framework files. Direct `pymhf run CompanionAutoSummon.py` bypasses this extra verification and is not the supported launch path for this package. `python CompanionAutoSummon.py` alone does not start the mod; copying it into GAMEDATA/MODS does not activate it.

Test the eight panel controls/displays, OFF/ON changes, individual location choices, Random mode, the biome preference and selection confirmation. For the biome option, test a matching eligible pet, no matching pet, OFF, station/Nexus bypass, and an unchanged manual favorite. On an archive platform or unsuitable terrain, remain there beyond 12 seconds, then walk to a valid place and check that the waiting pet appears once. Also test a normal planet, station exits, immediate re-entry, manual replacement, save switching and a restart. Verify multiplayer after the basic behavior works.

To disable the whole mod: quit NMS and launch normally through Steam. To forget choices, close NMS and remove only `state.json`. Removing `settings.json` restores all defaults: automation on, all three locations on, Last manually selected mode, and biome preference on for Random mode.

## Source

Development rules and architecture are maintained in [DEVELOPMENT.md](DEVELOPMENT.md). Source code, comments and developer diagnostics are English. The settings panel and HUD are currently English-only; the planned language coverage and remaining work are recorded in [LOCALIZATION.md](LOCALIZATION.md). [DESIGN.md](DESIGN.md) records the native-menu and notification goals, which are not yet implemented. Version-scoped changes are in [CHANGELOG.md](CHANGELOG.md).

`src/` contains policy, pet persistence, settings and runtime code. `build.py` rebuilds and syntax-checks CompanionAutoSummon.py without installing or launching it. Run offline tests with `python -B -m unittest discover -s tests -v`. `manifest.json` records checksums and validation status. `TECHNICKE-OVERENI.md` contains technical evidence in Czech. The panel uses the framework's documented [GUI properties](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/docs/docs/gui/gui.rst).

The maintained release backlog and proposed future features are in [ROADMAP.md](ROADMAP.md).

Prepared for sharing; not published to a mod service.
