# Companion Auto Summon for No Man's Sky - by Lineum Dynamics

**EARLY ALPHA — 0.10.1-native-test. Expect bugs and incomplete compatibility.
Keep a separate backup made while the game is closed before installing.**

Automatically summon an owned companion after loading a save or leaving your
ship, using the game's normal summon checks. Choose **By habitat**, **Random**
or **Last selected**, with optional **Shuffle**. The current native version
loads during normal Steam startup: **no Python, pyMHF, separate launcher or
external settings panel is required**. It does not create companions, reduce
gameplay limits or bypass unsuitable terrain.

Supported target: **Windows 10/11 x64, Steam Cosmos 7.05, build 25624745 only**.
The running executable must match SHA-256
`671de22649274b49fa07f5a246bc7252c4e08bb9ab623d2e65722fbab4e497a4`.
Unknown game builds refuse activation before this mod enables gameplay hooks.
Unexpected unsafe runtime state stops automation; restart after resolving the
problem. Consoles, GOG, Game Pass, macOS and Linux/Proton are not supported by
this alpha.

[Nexus Mods](https://www.nexusmods.com/nomanssky/mods/4579) ·
[GitHub releases](https://github.com/lineum-dynamics/nms-companion-auto-summon/releases) ·
[Report a bug](https://github.com/lineum-dynamics/nms-companion-auto-summon/issues) ·
[Full alpha release notes](docs/release/ALPHA-0100-RELEASE-NOTES.md)

**The public alpha is available on Nexus Mods**, verified on 30 September
2026. Nexus file **49367** is Main / Primary. The canonical GitHub repository
and 0.10.1 prerelease are public; this exact source/archive pairing is recorded
in the [tester handoff](docs/release/TESTER-HANDOFF.md).

## Install the native alpha

1. Close NMS and retain your closed-game backup. Stop the old CAS Python/pyMHF
   session if you used an earlier test; never run both versions together.
2. Extract `CompanionAutoSummon-0.10.1-native-test.zip`. In Steam, open
   **No Man's Sky → Manage → Browse local files**.
3. Merge the extracted **Binaries** and **GAMEDATA** folders into this game
   root. **Do not overwrite another mod's `Binaries/winmm.dll`.** An existing
   loader may be reused only if it matches the exact hash in the packaged
   README; stop if it differs. Replace only this mod's own files on an update.
4. Start NMS normally through **Steam**. Open **Quick Menu → Companions →
   Companion Auto Summon**. X is the default PC Quick Menu binding; use your
   configured input or the game's controller prompt if different.

Fresh settings use **By habitat** and **Shuffle ON**; existing preferences are
preserved. By habitat weighs compatible groups **13:5:1** on planets and uses
a neutral pool on stations/Anomaly. Random's same-biome preference applies
only to Random. Last selected uses the last confirmed manual companion for
that save. Shuffle advances after accepted requests; a blocked placement
retries the same pet. Manual dismissal alone does not trigger another summon.

The module also verifies a private snapshot before enabling its hooks, while
the game is already running. This **does not replace the separate closed-game
backup** above. Original save files are not edited or restored by the mod.
Preferences and favorites remain in `%LOCALAPPDATA%/NMS-AutoPet`.

To uninstall, close NMS and remove only `Binaries/scripts/CompanionAutoSummon.asi`
and `GAMEDATA/MODS/CompanionAutoSummon`. Keep `winmm.dll` if another mod uses it;
remove it only if unused and still identical to this package's loader. Do not
delete shared game or mod folders. See the packaged English/Czech READMEs for
the full installation and removal instructions.

## Known issues in 0.10.1-native-test

- There is no automatic summon trigger after teleport arrival or death/respawn.
  This build triggers after a successful local save load or ship exit. A read-only
  Cosmos 7.05 static-analysis pass narrowed the teleport search to native state
  references, but no successful local completion callback is verified yet. A
  feature-branch live test saw a pet after a freighter-to-station teleport, but
  its automatic opportunity had been armed about fourteen minutes earlier; this
  does not establish teleport support. The public archive remains unchanged. See
  [teleport/menu research](docs/research/TELEPORT-AND-GROUPED-MENU.md).
- The owner reported that the settings menu disappeared after death. The
  0.10.1 log recorded a UI callback-thread safety stop, but did not record a
  death event; whether death caused the thread change is unknown. One grouped
  roster smoke check did show the settings entry, but other menu rebuilds remain
  unverified. A feature-branch recovery candidate passed 25 offline menu tests
  and one live scenario: the owner reports the menu worked and a pet appeared
  after a direct load from an expedition into the Anomaly. The log confirms a
  successful local load and accepted summon queue. Recovery after death and
  other menu rebuilds remain unverified; the candidate is not in the public
  download.
- One direct load into the Space Anomaly had no visible pet during an
  incomplete mission; a causal connection has not been established.

See the [canonical Known Issues record](docs/KNOWN-ISSUES.md) for current
status and reporting details. The public Nexus description carries the same
player-facing limitations. The 0.10.1 offline suite and limited grouped-menu
smoke are not broad compatibility acceptance; second-PC and multiplayer
testing remain open.

The 0.10.1 archive is **3,725,689 bytes**, SHA-256
`51cf81c7cc48e835a1f9f14f96ced93d2a32b56200c5c079e23f2b0f17331116`.
Nexus file **49367** is the Main / Primary file, with mod-manager downloads
OFF. The public page says **Safe to use** and the linked VirusTotal SHA-256
matches the local archive. Edge blocked the owner's manual download, so its
downloaded bytes were not read back. These bounded observations are not a safety
guarantee. No second-tester receipt or installation is claimed.

**Please report reproducible problems**, including the alpha version, game
build, location/trigger, selection mode and Shuffle state, expected result and
actual result. Add a short relevant log excerpt or screenshot after removing
personal paths/account details. Do not upload full saves, private backups,
credentials or whole user-data folders. The
[validation checkpoint](docs/research/NATIVE-0705-COMPATIBILITY.md),
[Known Issues record](docs/KNOWN-ISSUES.md) and
[tester handoff](docs/release/TESTER-HANDOFF.md) retain the precise evidence.

## Retained Python candidates and earlier evidence

Everything below is **historical**. The launcher, Python/pyMHF prerequisites,
old file IDs and old test counts describe their named versions; they are not
installation instructions or current compatibility claims for the native
0.10.1 alpha above. Retaining them does not make an older quarantined file
cleared or make the current alpha fully tested.

Retained packaging candidate: **0.9.3-test**. It extracts the original Python
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

The 0.9.2 historical tester flow used a Nexus draft and owner-mediated sharing.
The current native 0.10.0 alpha is publicly downloadable from the Nexus link at
the top of this README; this older process does not describe the native package.

Retained unlaunched 0.9.1 source **0.5.1-experimental / 0.9.1-play-trial**, with menu
**0.9.0-selection**, reports each changed setting and its applied value. A batch
keeps every effective change; failed persistence adds one session-only suffix.
The combined trial sets `gui.shown = false`, leaving settings in the native
Quick Menu. The standalone developer mod keeps its panel. Validation
passed 403 production and 689 developer tests. Actual-framework checks and both
read-only launch preflights passed; the combined archive has 42 verified files. That candidate
has not launched; the retained **090-r2** files remain unchanged after normal
closure before 0.9.2. Native text is English.

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

Prior live trial **0.5.0-experimental / 0.9.0-play-trial**, with menu
**0.9.0-selection**, implements **By habitat** and **Shuffle companions**.
Offline validation passed 396 production and 683 developer tests. The final
`090-r2` candidate launched on 28 September 2026 after a verified backup of
46 save files and two mod preference/state files. Its log records production
0.5.0, menu 0.9.0 and two Mods with twelve hooks initialized. Existing schema-3
settings retained Random with shuffle OFF during the in-memory migration.
The player confirmed a visible Random pet after loading in the Space Anomaly
and reports that settings appear to save. Restart persistence, complete native
control acceptance, By habitat and shuffle outcomes remain unverified; see
[the bounded live record](docs/research/LIVE-090.md).
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

Fourteen catalogs now contain 63 keys: the retained 46 menu/HUD, branding and
compatibility entries plus seventeen portable launcher entries. Nine compatibility
messages and the portable launcher use catalog lookup outside the game. The thirteen
translations remain unreviewed drafts; native menu/HUD text remains English.
The portable package is built and offline-checked, while live portability and
complete language acceptance remain unverified. See [LOCALIZATION.md](LOCALIZATION.md).

0.8.2 startup registered both Mods and 12 native targets at 23:58:46 on 27 September 2026 after a verified 43-file backup. Automation is ON; all 17 payloads and the existing player files matched. The original DDS was staged and hash-verified. Visible icon/HUD, all six controls and gameplay still need the player's check. Validation: 294 production and 519 developer tests, plus real Windows lease and pyMHF checks.

[Czech user-guide translation](README.cs.md)

The canonical source is the public [lineum-dynamics/nms-companion-auto-summon](https://github.com/lineum-dynamics/nms-companion-auto-summon) repository. Development commands and the maintained documentation map are in [DEVELOPMENT.md](DEVELOPMENT.md). The installed test copy and exported ZIPs are built outputs.

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

The retained 0.8.7 has all six existing
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

Windows 10/11 x64, Steam NMS **build 25442159 / Cosmos 7.04**, bundled Python **3.11.9 x64**, and bundled **pyMHF 0.2.4**. Windows .NET Framework 4 and Microsoft Visual C++ v14 x64 are prerequisites. `compatibility.json` records the supported target; a build gate checks agreement with the host, native declarations and manifest. Other game builds, stores and operating systems require additional compatibility work.

This package contains no personal saves, account credentials, preselected pet or machine-specific installation paths. Each player has their own settings. Unsupported executables are rejected before using unverified addresses.

## Settings

The **0.9.3-test candidate** has seven rows at **Quick Menu → Companions →
Companion Auto Summon**. The default PC Quick Menu key is **X**; use your assigned
key if you remapped it. Confirm a row using the game's configured
Select action: selection mode cycles Last selected → Random → By habitat; the
other six rows toggle ON/OFF. Matching-biome preference
only affects Random on planets. All three locations may be OFF. Labels distinguish
queued changes from applied state and session-only persistence. Browsing or
rebuilding the page must not change a setting. Complete navigation, the shuffle
icon and current confirmations still require in-game acceptance. The combined
launch does not create an external pyMHF control window.

The seven native controls are:

- **Automatic summoning**: ON/OFF, enabled by default. Covers both ship exits and successful local save loads.
- **Selection**: **Last selected**, **Random** or **By habitat**. By habitat is the fresh-install default; existing choices are preserved. Every mode retains native ownership, eligibility and placement checks.
- **Random: prefer matching biome** (default ON): prefers the matching native habitat within the eligible pool on planets. OFF, unknown habitat or no eligible match uses the ordinary random pool. This only affects Random and does not change native eligibility.
- **Planets**: allow automatic summoning on planets, default ON.
- **Space stations**: allow automatic summoning on stations, default ON.
- **Space Anomaly**: allow automatic summoning in the Nexus, default ON.
- **Shuffle companions**: cycles eligible pets in Random, or within the weighted group chosen by By habitat. ON for fresh installs; migrated older preferences start OFF. Last selected is unaffected.

The standalone developer script has no native menu; only that setup retains the
separate pyMHF **CompanionAutoSummon** tab, accessible with Alt+Tab. It exposes
these preferences plus **Status** and **Companion** diagnostic displays for pending
changes, waiting placement, persistence and the remembered or active selection.
No mod-specific keyboard shortcut is registered; the combined trial uses the
game's configured menu actions.

A change applies and saves on the next local-player update; return from the
standalone developer panel before quitting. The HUD names the effective change,
for example `Selection: By habitat` or `Shuffle companions: ON`. Several changed
settings are listed together. Failed saving adds `(session only)`; unchanged
values produce no confirmation. Changing settings cancels any pending automatic request, including a load opportunity still awaiting ownership, and leaves an already active companion alone. Turning on or changing mode waits for the next ship exit or successful local save load; it never immediately summons a pet. Manual selections are still remembered while automation is off.

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

If `settings.json` cannot be read, automation starts off. The mod settings can explicitly enable it for that session. A runtime error disables automatic summoning separately; the checkbox cannot override that safety stop.

## Launching / first test

1. Quit NMS normally, extract the complete **0.9.3-test** ZIP into a new folder,
   and double-click **Companion Auto Summon.exe**.
2. Select **Check installation**. If needed, use **Choose game folder** to locate
   your Steam installation, then check again. A different game executable is refused.
3. Select **Start game**. A verified private backup is required before each
   normal start; failure prevents launch. No Python/pip installation is needed.
4. Keep the launcher open for the first live test. Do not end its background
   host. Closing the launcher is designed to leave the session running, but
   that behavior has not yet been proven in game.

See [the complete quick start](docs/release/PORTABLE-QUICKSTART.md) for the
one-time Microsoft Visual C++ x64 prerequisite, first pet checks and recovery.
Backups, logs and private sessions live under `%LOCALAPPDATA%\NMS-AutoPet\`;
existing `settings.json` and `state.json` remain there. Backup copying verifies
the source before and after copying. Session files must not be removed while
playing, and personal data must not be shared with another tester.

To play without the mod, quit NMS normally and start it through Steam. Removing
`settings.json` resets the approved fresh defaults rather than preserving your
choices; routine upgrades do not require deleting it. After both solo checks,
use [the multiplayer plan](docs/release/MULTIPLAYER-TEST.md). Record visible
pets independently on each PC; a log request alone does not prove appearance.

The earlier PowerShell/external-Python workflow is a retained developer path,
not the portable player's installation procedure. Developer commands and
version-scoped checks remain in [DEVELOPMENT.md](DEVELOPMENT.md).

## Source

Development rules and architecture are maintained in [DEVELOPMENT.md](DEVELOPMENT.md). Source code, comments and developer diagnostics are English. The native menu, retained developer panel and HUD are currently English-only; the planned language coverage and remaining work are recorded in [LOCALIZATION.md](LOCALIZATION.md). [DESIGN.md](DESIGN.md) records the native-menu and notification goals. The 0.8.2 combined candidate retains all six preferences from 0.8.0; the historical 0.7.1 had the native automation toggle, and older artifacts retain an inert **Settings preview** child. Version-scoped changes are in [CHANGELOG.md](CHANGELOG.md).

`src/` contains policy, pet persistence, settings and runtime code. `build.py` rebuilds and syntax-checks CompanionAutoSummon.py without installing or launching it. Run offline tests with `python -B -m unittest discover -s tests -v`. `manifest.json` records checksums and validation status. `TECHNICAL-VERIFICATION.md` contains version-scoped technical evidence in English. The panel uses the framework's documented [GUI properties](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/docs/docs/gui/gui.rst).

The maintained release backlog and proposed future features are in [ROADMAP.md](ROADMAP.md).

Prepared for sharing; not published to a mod service.
