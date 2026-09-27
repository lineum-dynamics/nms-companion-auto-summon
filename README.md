# Companion Auto Summon 0.4.4 — experimental

[Český návod](README.cs.md)

This Git repository is the canonical source for Companion Auto Summon. Development commands and the maintained documentation map are in [DEVELOPMENT.md](DEVELOPMENT.md). The installed test copy and exported ZIPs are built outputs.

The new **0.4.4** candidate adds bounded passive diagnostics after the game
accepts a summon request. It records native queued/active transitions without
retrying, changing summon timing, or writing game saves. A native active-slot
observation still needs the player's visible confirmation. The separate
**0.7.1-play-trial** keeps the existing native ON/OFF menu with this candidate.
Neither version has been launched; the running 0.7.0 folder remains unchanged.
Anomaly startup and the unwanted white HUD disc are still open issues.
The evidence below belongs to the earlier versions explicitly named there.

Offline validation for this candidate passed: **253 production tests** (including 23 new observer cases), **408 developer tests**, actual pyMHF widget checks and combined-folder discovery/preference checks. No game access or live hook registration occurred during validation.

The separate developer candidate **0.7.0-play-trial** adds the first native
setting: automatic summoning ON/OFF. It queues changes through the unchanged
0.4.3 production runtime. Basic ON/OFF behavior now has partial player and log
confirmation; complete input/navigation testing remains pending. The remaining
preferences still use the temporary pyMHF development panel, which will be
retired from the player interface once all native controls are complete.
This separately built candidate registered in-game on 27 September 2026 after
a fresh verified backup; two Mods and 11 hook targets loaded with automation ON.

Version 0.4.3 adds one automatic-summon opportunity after a successful local save load, so loading directly on foot can use the same placement checks as a ship exit. One Random-mode summon after loading on a **space station** is now confirmed by the log and the user. It uses the existing automation toggle and selection/location preferences; no new option or stored-data format is introduced. The settings tab remains **CompanionAutoSummon** because pyMHF uses the Python class name. Current validation is recorded in `manifest.json`.

The candidate passed **230 production offline tests**, the real pyMHF settings-widget check and discovery checks for the combined 0.6.2 play trial. These checks use temporary data and no game connection or native hook registration. The combined trial subsequently registered in NMS with automation ON and two Mods/ten managed hooks at 20:42:21 on 27 September 2026.

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

The first automatic summon test in 0.3.1 expired without spawning. Version 0.3.2 adds native placement refresh while the quick menu is closed and bounded diagnostics; its corrected basic path passed the test above. Offline tests cover decisions, persistence and a simulated adapter. See `TECHNICKE-OVERENI.md` for the evidence and remaining scope.

## Supported target

Windows x64, Steam NMS **build 25442159 / Cosmos 7.04**, Python **3.11–3.13 x64**, and **pyMHF 0.2.4**. The exact supported EXE SHA256 is in `manifest.json`. Other game builds, stores and operating systems require additional compatibility work.

This package contains no personal saves, account credentials, preselected pet or machine-specific installation paths. Each player has their own settings. Unsupported executables are rejected before using unverified addresses.

## Settings panel

Launch through Companion Auto Summon, then **Alt+Tab to the separate pyMHF window** and open its **CompanionAutoSummon** tab. This is a desktop settings window, not an entry inside the native NMS menu. No Companion Auto Summon keyboard shortcut is registered.

- **Automatically summon companion**: on/off checkbox, enabled by default. It covers both ship exits and successful local save loads.
- Three location checkboxes enable planets, space stations and the Nexus separately. All default on. Turning all three off prevents automatic summoning everywhere.
- **Companion selection** offers **Last manually selected** (default) and **Random**. Random mode uses only owned companions accepted by the native game checks.
- **Prefer same biome in Random mode** (default ON): prefers the matching native habitat within that eligible pool on planets. Turn it OFF for ordinary random selection. Unknown/no matching habitat falls back automatically; no pet is excluded from ordinary native eligibility by this option.
- **Status**: current state, including **Waiting for a suitable place**, pending changes, session-only persistence, or a runtime error.
- **Companion**: selected slot, a remembered choice awaiting ownership verification, or the active selection mode. In Last manually selected mode, an empty choice prompts you to summon your first companion manually.

Return to the game to apply and save a change on the next local-player update before quitting. Changing settings cancels any pending automatic request, including a load opportunity still awaiting ownership, and leaves an already active companion alone. Turning on or changing mode waits for the next ship exit or successful local save load; it never immediately summons a pet. Manual selections are still remembered while automation is off.

In Last manually selected mode, new players start with no selected companion. The first accepted manual summon selects one they already own. A new or changed choice requests a three-second, silent HUD confirmation: **Companion Auto Summon: companion selected for automatic summoning.** When automation is off, the message says so; in Random mode, it confirms the saved manual favorite while Random remains on. Repeating the same choice or restoring it after a restart does not repeat the confirmation. The panel and messages use English. The Random setting has been successfully applied in a historical live session; HUD rendering and the remaining panel controls still require validation.

Explicitly selecting Random does not require a previous manual choice, but the player must own an eligible companion. Companion Auto Summon never creates or unlocks one. Random selection does not replace the remembered manual companion. The same pet may be drawn on consecutive requests.

## Behavior

1. In Last manually selected mode, manually summon your preferred companion once with Companion Auto Summon running. Random mode needs an eligible owned companion but no previous manual choice.
2. A ship exit or successful local save load supplies one opportunity. Save deserialization itself calls no summon or placement functions; the first suitable local ownership update prepares the request. The mod then uses the unchanged 1.5-second stability delay in an enabled, supported location: on foot on a planet, a space station, or the Nexus inside the Space Anomaly. No pet may be active or queued, and native ownership, eligibility and placement checks must pass.
3. If the current place is unsuitable, the request remains pending without a time limit. Walk to a suitable place and Companion Auto Summon can complete that same request; another ship entry and exit is not required.
4. In Last manually selected mode, loading the same save can restore its remembered identity without a ship exit. If ownership data is still arriving, identity lookup waits and retries at 0.5-second intervals. It never substitutes another pet at the old slot. No remembered choice means no startup summon; Random can instead wait for an eligible owned companion.
5. Manually summoning a different companion replaces that save's manual choice.

An archive platform or other temporarily unsuitable place does not expire the request; the old 12-second limit is removed. Freighters and other locations excluded by this build's native location check still cannot summon pets. While in such a location, Companion Auto Summon retains the intent and makes no native summon or placement calls; it can resume after you reach an enabled, supported location. Entering a supported location that you disabled in Companion Auto Summon settings cancels the request instead.

Re-entering the ship, a manual companion or related emote preview, an accepted manual selection, a settings change or unavailable/replaced application context cancels the request. An already active or queued companion also consumes a pending load opportunity, even before ownership is ready or while paused. Loading another local save cancels the previous request; only successful completion can supply a new opportunity. Network-client loads do not create or reset the local player's opportunity.

The load opportunity is consumed once, before the ordinary request is armed. After an accepted request, manually dismissing the pet does not repeatedly summon it again. The next real ship exit or successful local save load can create another opportunity. Automation OFF prevents either trigger.

Companion Auto Summon refreshes native placement while the menu is closed, using the game's configured range and unchanged spatial checks. It never marks an invalid position valid. Placement is checked in fresh pairs of game callbacks, with at least 0.5 seconds between pairs. If the game rejects the queue request, Companion Auto Summon waits for a fresh check and retries the same chosen pet. Once the game accepts the queue request, that opportunity is finished. Waiting on archive platforms, delayed placement and these retries still need an in-game test.

Random mode chooses at most one candidate per request after placement is prepared. Once selected, it never rerolls during that request. An identity change, manual selection or cancellation does not trigger a replacement draw. Identity, ownership and full native eligibility are checked again before queuing the selected pet.

Growth, speed, trust, eggs, combat values and game capacities are unchanged. Companion Auto Summon does not change summon limits, unlock companions, generate pets or bypass native placement restrictions.

## Persistence

The legacy `NMS-AutoPet` data directory is intentionally retained. Do not rename it: existing manual favourites, preferences and the development runtime continue to use it. Renaming the mod does not reset or copy personal data.

Manual pet choices: `%LOCALAPPDATA%\NMS-AutoPet\state.json`, outside the game and its saves. Selections are keyed by `SaveUniversalId`; pets are matched by CreatureSeed + BirthTime. Reordered slots are supported. Initial ownership loading may delay restoration; a persistently missing or ambiguous pet requires a new manual choice. The adjacent `settings.json` uses schema 3 to store enabled status, locations, selection mode and `prefer_same_biome` for all saves of this Windows user. Legacy schemas 1 and 2 migrate in memory with the biome preference ON while preserving their existing choices, including OFF. Schema 3 is written only on an explicit settings save; a stored OFF biome preference remains OFF.

Main-game and expedition contexts inside one save share one remembered choice. It is restored only where the pet exists. A zero save ID allows session-only selection; a successful local load with a valid common-data object can still supply a Random-mode opportunity without saving an identity. It never borrows another save's favorite. A damaged settings file is preserved, with persistence disabled for that session. The mod does not edit game save files; ordinary game autosaving continues.

If `settings.json` cannot be read, automation starts off. The panel can explicitly enable it for that session. A runtime error disables automatic summoning separately; the checkbox cannot override that safety stop.

## Launching / first test

Close NMS and back up the current save profile before the first test. Extract the package and install a supported x64 Python version if necessary. Run `Start-CompanionAutoSummon.ps1` from PowerShell.

The launcher refuses to proceed while NMS is running, detects Steam libraries, checks the game and packaged script, and creates a private environment under `%LOCALAPPDATA%\NMS-AutoPet\runtime-0.2.4`. It installs `pymhf[gui]==0.2.4`, including GUI dependencies, when needed, requiring internet on first setup, then launches Companion Auto Summon. This development runtime keeps its legacy path to reuse existing dependencies.

An optional `-GameDirectory` argument selects a game folder for preflight checks. It must match the installation used by the active Steam client: pyMHF still launches Steam app 275850.

Diagnostic logs are written to `logs` beside CompanionAutoSummon.py. The interactive Python console and separate logging window are disabled; the settings panel remains available.

Use `Start-CompanionAutoSummon.ps1` from a regular PowerShell terminal. It calls the host-only `Launch-CompanionAutoSummon.py`, which verifies DLLs by their full physical path and actual address in the game before Python code executes there. This guard does not edit installed framework files. Direct `pymhf run CompanionAutoSummon.py` bypasses this extra verification and is not the supported launch path for this package. `python CompanionAutoSummon.py` alone does not start the mod; copying it into GAMEDATA/MODS does not activate it.

Test the eight panel controls/displays, OFF/ON changes, individual location choices, Random mode, the biome preference and selection confirmation. Load directly on foot on a planet, station and the Nexus; confirm a single summon, then dismiss it and confirm it stays dismissed until another trigger. Also load with automation OFF or a companion already present. For the biome option, test a matching eligible pet, no matching pet, OFF, station/Nexus bypass, and an unchanged manual favorite. On an archive platform or unsuitable terrain, remain there beyond 12 seconds, then walk to a valid place and check that the waiting pet appears once. Also test normal ship exits, immediate re-entry, manual replacement, save switching and a restart. The single 0.4.3 station startup in Random mode and one later manual dismissal without reappearance are confirmed as described above; remaining startup scenarios and broader dismissal regression still need live checks. Verify multiplayer after the basic behavior works.

To disable the whole mod: quit NMS and launch normally through Steam. To forget choices, close NMS and remove only `state.json`. Removing `settings.json` restores all defaults: automation on, all three locations on, Last manually selected mode, and biome preference on for Random mode.

## Source

Development rules and architecture are maintained in [DEVELOPMENT.md](DEVELOPMENT.md). Source code, comments and developer diagnostics are English. The settings panel and HUD are currently English-only; the planned language coverage and remaining work are recorded in [LOCALIZATION.md](LOCALIZATION.md). [DESIGN.md](DESIGN.md) records the native-menu and notification goals. The separate developer menu has an inert **Settings preview** child; it does not change preferences. Version-scoped changes are in [CHANGELOG.md](CHANGELOG.md).

`src/` contains policy, pet persistence, settings and runtime code. `build.py` rebuilds and syntax-checks CompanionAutoSummon.py without installing or launching it. Run offline tests with `python -B -m unittest discover -s tests -v`. `manifest.json` records checksums and validation status. `TECHNICKE-OVERENI.md` contains technical evidence in Czech. The panel uses the framework's documented [GUI properties](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/docs/docs/gui/gui.rst).

The maintained release backlog and proposed future features are in [ROADMAP.md](ROADMAP.md).

Prepared for sharing; not published to a mod service.
