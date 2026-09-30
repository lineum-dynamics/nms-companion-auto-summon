# Companion Auto Summon for No Man's Sky - by Lineum Dynamics

**PUBLIC EARLY ALPHA PUBLISHED: 28 September 2026, 18:43 CEST. Version: 0.10.0-native-test.**

The page version and the full Description through Credits were saved and read
back on 28 September 2026. Native file **49202** was subsequently renamed
**Companion Auto Summon - ALPHA 0.10.0** and set as the **Main / Primary** file,
with mod-manager downloads OFF. Nexus displays the new file
as safe; its exact ZIP VirusTotal report showed **0/68** when checked at
**18:19 CEST** (analysis timestamp **16:15:13 UTC**). An actual manual download
completed and its SHA-256 matches the uploaded 3,725,420-byte archive:
`e00a8818230dba24066fcdc4d75a01d696c9e2573d2538aa6a9b05c5dd14bebb`.
These file results apply to file 49202, not the older retained files. Mod
**4579** is now **Published**, owned by **LineumDynamics**, with the exact title
above and author **Lineum Dynamics**. The public page shows its original upload
at **28 September 2026, 6:43PM**, the updated EARLY ALPHA summary and description,
one current file, Manual download, and **Safe to use**. All three earlier
uploads are retained in the archive. Preserve the approved media and disclosure
tags. Public source and the prerelease are available at
https://github.com/lineum-dynamics/nms-companion-auto-summon/releases/tag/v0.10.0-native-test.

One native r3 startup through Steam is now recorded: the log confirms exact
executable acceptance, a completed pre-activation backup, all twelve hooks and
the binding guard enabled, a successful local save load, and two accepted
summon queue requests. Subsequent player feedback confirms a visible pet after
ship exit. **Visible appearance after loading the save is uncertain**, so the
accepted startup queue does not establish successful visible startup summoning.
The menu, restart repeatability, second-PC installation and multiplayer remain
unverified. Native file 49202's recorded scan and verified download do not
establish gameplay reliability or permanent scanner acceptance.
Nexus publication, public GitHub visibility and the matching prerelease are
complete and verified. The final section contains internal records and must
not be copied into the player description.

## Short summary

EARLY ALPHA: automatically bring an owned companion after save loading or ship exit. Last selected, Random or weighted By habitat, with shuffle and Quick Menu settings. Exact Windows/Steam build only. Bugs are possible; back up saves before testing.

## Description

**EARLY ALPHA / First Public Test — 0.10.0-native-test. Expect bugs, incomplete behaviour and possible crashes. This is an experimental release for Windows 10/11 x64 and the exact Steam build listed below, not a stable release. Make a separate backup of your saves with the game closed before installing or testing.**

**Confirmed so far:** one player saw a companion appear after ship exit. Appearance after loading the save remains unconfirmed despite an accepted request in the log. Startup reliability, menu operation, restart repeatability, second-PC installation and multiplayer still need testing. The recorded download and scanner checks do not establish gameplay reliability.

Keep a companion beside you without opening the companion menu after every landing. When you leave your starship or load your local save, the mod checks your settings and asks the game to summon one of your eligible owned companions.

Choose a familiar favourite, let Random vary your company, or use By habitat to favour companions suited to the planet under the explicit rules below. The mod does not give you pets, unlock slots, accelerate growth, improve combat values or bypass placement restrictions. You still need to own a companion that the game permits you to summon.

If your landing platform or surrounding terrain is unsuitable, the request can wait while you walk somewhere suitable. A selected pet stays fixed during that wait. Entering your ship, choosing a pet manually or changing a mod setting cancels the pending request.

This version runs as a native module loaded during normal Steam startup. It needs no Python installation, separate mod launcher or external settings panel. The package's two game folders are merged into your Steam game installation while the game is closed.

## Settings in 0.10.0-native-test

Open **Quick Menu → Companions → Companion Auto Summon**. On PC, the default Quick Menu key is **X**. If you have changed your controls, use your assigned Quick Menu key or the game's controller prompt. The mod uses native menu actions. Its settings entry appears before individual pets.

That page has seven controls:

- **Automatic summoning:** ON/OFF. OFF cancels waiting automatic requests without dismissing your current companion. Turning ON waits for your next ship exit or successful local save load.
- **Selection:** Last selected, Random or By habitat. Last selected remembers a successful manual choice for that save; the other modes do not replace your remembered favourite.
- **Random: prefer matching biome:** favour eligible companions whose stored native habitat exactly matches the planet. If the habitat is unknown or no eligible match exists, use the ordinary eligible random pool. This only affects Random on planets, not Last selected, By habitat, stations or the Space Anomaly.
- **Planets:** allow automatic summoning on planets.
- **Space stations:** allow automatic summoning on stations.
- **Space Anomaly:** allow automatic summoning in the Nexus.
- **Shuffle companions:** use a shuffled cycle in Random, or within the weighted group chosen by By habitat. It does not affect Last selected.

Fresh-install defaults are **By habitat**, **Shuffle companions ON**, automation ON, all three locations ON, and the Random biome preference ON. Existing preferences are preserved; migration from older schemas starts the new shuffle option OFF.

Applied changes report the actual value, such as **Selection: By habitat**, **Shuffle companions: ON** or **Space stations: OFF**. If several settings change together, the confirmation lists them together. A failed save adds **(session only)**; an unchanged value produces no new confirmation. The native menu and its presentation still require live acceptance.

## Compatibility

The supported target is **Windows 10/11 x64, Steam build 25442159 / Cosmos 7.04**. The exact executable SHA-256 is:

`b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`

The module checks the actual running executable before enabling its gameplay hooks and refuses an unknown build. A game update requires renewed compatibility checks. Consoles, GOG, Game Pass, macOS and Linux/Proton are not supported by this candidate. This exact-build target is not proof of compatibility with every other mod.

In-game menu and HUD text currently use **English**. Fourteen maintained language catalogs exist; English is canonical and the other thirteen remain unreviewed translation drafts. Startup warnings use the available Windows language with English fallback. This is not full translated in-game support.

The package contains the native **CompanionAutoSummon.asi**, the pinned **Ultimate ASI Loader 9.7.4 x64**, eight original DDS icons and the required third-party notices. There is no bundled Python host or Python settings window. Native files remain subject to antivirus and Nexus checks; a smaller package does not guarantee clearance.

## Install and start

1. Close No Man's Sky normally. Exit any previous Companion Auto Summon launcher or pyMHF session. Retain a separate backup made while the game is closed before this first native test.
2. In Steam, select **No Man's Sky → Manage → Browse local files**. The game folder contains **Binaries** and **GAMEDATA**.
3. Extract the complete ZIP to a temporary folder and read **README.md** or **README.cs.md**. If the game already has **Binaries/winmm.dll**, do not overwrite a different file: another mod may use it. Reuse it only if its SHA-256 matches the loader hash in this package's README and manifest.
4. Copy the extracted **Binaries** and **GAMEDATA** folders into the game folder, merging them. When updating this mod, close the game first and replace only this mod's own module and icon files. Keep the matching package README, manifest and notices for reference.
5. Start No Man's Sky normally through **Steam**. Do not start the old Python launcher as well. No administrator command or separate mod settings panel is required.

The files added to the game are:

- **Binaries/winmm.dll** — the included loader.
- **Binaries/scripts/CompanionAutoSummon.asi** — this mod.
- Eight icons under **GAMEDATA/MODS/CompanionAutoSummon/TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/**.

Do not run the old Python and new native versions together. This is a native module with companion icon assets, not a standalone PAK installed only into GAMEDATA/MODS.

## Settings, backups and disabling the mod

Preferences, per-save manual favourites, logs and backups stay under **%LOCALAPPDATA%/NMS-AutoPet/**. Existing settings and favourites are retained. Invalid settings files are preserved; automation starts OFF and settings changes can be session-only.

Before enabling its gameplay hooks, the module makes and verifies a private snapshot of saves and external preferences. **The game process is already running at this point. This is a pre-activation snapshot, not a closed-game or pre-launch backup.** Failed verification refuses activation. Retain the separate closed-game backup for this first test. The mod does not directly edit, restore or overwrite the original NMS save files.

To disable or uninstall the native mod, close the game and remove **Binaries/scripts/CompanionAutoSummon.asi**. Its icon folder **GAMEDATA/MODS/CompanionAutoSummon/** can also be removed. Keep the shared **winmm.dll** loader if another ASI mod needs it. Remove that loader only if no other mod uses it and it still matches the packaged loader. Never remove the game's Binaries, scripts or GAMEDATA folders wholesale. Preferences and backups are deliberately retained.

**Starting through Steam alone does not disable an installed native mod.** To return to the old Python test, remove the native module first, then use the old launcher after normal game closure.

## FAQ and current limitations

**Do I need to select a companion first?**

For Last selected, manually summon an owned companion once. Random and By habitat need no previous choice, but still require an eligible owned pet. A new installation never supplies a companion of its own.

**Will it keep summoning a pet I dismiss?**

Dismissal does not create another automatic opportunity. Another successful local save load or ship exit can do so. An already active or queued companion also prevents a duplicate request.

**Does it summon after teleporting or deleting a base?**

Teleport arrival and base removal do not create a new summon opportunity. A reported missing pet after teleport and disappearance after base removal do not establish why the game removed it. The mod does not automatically respawn pets simply because they disappear, which preserves manual dismissal.

**How much has been tested?**

The native candidate has offline policy and selection comparisons, temporary-file persistence and backup tests, owned-memory runtime/menu scenarios and unsupported-host checks. A separate MinHook fixture checks forwarding and reentry using only functions authored in the test executable.

In one subsequent native r3 startup through Steam, the log confirms that the exact game executable passed its check, the private pre-activation backup completed, all twelve game hooks and the binding guard enabled, and a local save loaded successfully. The log then recorded two accepted summon queue requests. The player subsequently confirmed **a visible pet after ship exit**. **Visible appearance after loading the save remains uncertain:** the accepted startup queue establishes neither a visible success nor a visible failure. Startup reliability, the native menu, restart repeatability, all seven controls, rendered icons, remapped/controller input, placement, second-PC installation and multiplayer remain acceptance work. Historical player reports for the Python versions do not validate this native port.

**Why can the custom settings stop responding?**

The retained menu safety guard stops custom menu handling after an unexpected callback thread or overlapping callback, while keeping native quick-binding protection installed. The underlying thread-change limitation is **not fixed by the C++ port**. Automatic summoning has a separate safety latch. Check the native log and restart normally after a safety stop; a stopped menu must not be described as reliable live operation.

## Selection and shuffle rules


**Implemented in the first public test release, 0.10.0-native-test; full live acceptance is pending.** The native port retains the existing selection balance and explicit rules below. Offline comparisons against the previous implementation do not prove visible in-game outcomes.

### Choose how your companion is selected

- **Last selected:** use your remembered manual choice for this save. Habitat preferences and rotation do not change it.
- **Random:** choose from the eligible owned pool. Its separate **Random: prefer matching biome** switch first uses exact matches on planets; if none are eligible or the planet habitat is unknown, it falls back to the ordinary eligible pool. With rotation OFF, each pet in the chosen pool has an equal chance and consecutive repeats are possible.
- **By habitat:** on planets, use the explicit habitat groups below. The Random biome switch does not affect this mode. Unlisted combinations are excluded; there is no unrestricted fallback that could put a Frozen pet on Lava.

### What do the weights mean?

First choose a nonempty eligible group, then a companion within that group:

- **Exact match: weight 13** — about **68.4%** when all three groups are available.
- **Related habitat: weight 5** — about **26.3%** with all groups available.
- **Acceptable alternative: weight 1** — about **5.3%** with all groups available.

These are group probabilities, not fixed percentages for each pet. Owning more pets in one group does not increase that group's weight. Empty groups are removed and the remaining weights are renormalized. For example, related plus acceptable becomes about 83.3% versus 16.7%; one available group gets 100%. With rotation OFF, selection within the chosen group is uniform. Rotation ON uses its shuffled cycle instead.

### Which habitats are related?

Every recognized habitat exactly matches itself. The following list is read as **planet → companion habitats**. Each row lists additional related and acceptable choices; a reverse relationship exists only if its own row says so.

- **Lush:** related Swamp; acceptable Barren, Frozen.
- **Toxic:** related Swamp; acceptable Radioactive.
- **Scorched:** related Lava; acceptable Barren, Dead.
- **Radioactive:** no related group; acceptable Toxic, Barren, Dead.
- **Frozen:** no related group; acceptable Barren, Dead.
- **Barren:** related Dead; acceptable Lush, Scorched, Radioactive, Frozen.
- **Dead:** related Barren; acceptable Scorched, Radioactive, Frozen.
- **Weird / anomalous:** exact match only; recognized Weird variants share this category.
- **Swamp:** related Lush, Toxic; acceptable Radioactive, Barren.
- **Lava / volcanic:** related Scorched; acceptable Barren, Dead.
- **Waterworld:** exact match only. Adoptable Water-bound companions exist, including helmet/hermit crabs; this mod does not enable underwater summoning.
- **Gas giant:** a native adoptable companion pool has not been established by the primary evidence reviewed. This candidate accepts an already-owned exact habitat match only. Without an owned match, By habitat skips the opportunity rather than choosing an unrelated pet.

These are the mod's selection preferences, not official creature survival rules. Stored habitat determines a pet's category; its name, colour or fiery appearance does not. Scorched and Lava are separate game categories: a Scorched companion is a related choice on Lava, while an anomalous companion is excluded there. Recognizing a category does not guarantee that the game permits adoption or summoning there.

Aquatic does not automatically mean Waterworld: a crab adopted underwater on a Frozen planet is classified by its stored native habitat. Adoption and summoning are different: [a Water-bound crab owner's report](https://steamcommunity.com/app/275850/discussions/0/814724377262342410/) confirms that owning such a pet does not let the player summon it underwater. Fish caught as inventory items and creatures from gas giant moons are not evidence of adoptable Gas Giant fauna. These findings explain the selection rules; this mod has not yet been tested on either planet type.

### Stations, waiting and no suitable companion

On space stations and in the Space Anomaly, By habitat uses the ordinary unweighted eligible owned pool. There is no planet habitat to favour. The location switches and all normal game restrictions still apply; the mod does not add freighter support.

Unknown planet habitat waits for usable information. If the known owned roster has no approved habitat group, that opportunity is skipped with **No suitable companion for this habitat.** It does not substitute an unrelated pet. If a suitable owned pet exists but is temporarily ineligible, or placement is obstructed, the request can wait for a valid opportunity. No owned companions means no free pet.

Once selected, a pet stays fixed while placement is retried. Ship entry, manual pet preview/selection, a settings change, an active/queued pet or a local save change can end the wait. Losing the selected pet, moving it to a different slot during a pending request or an ambiguous identity cancels that request without drawing a replacement. By habitat also cancels if its supported planet/neutral context changes; Random keeps its selection across temporary location changes. An accepted request finishes that opportunity: it does not repeatedly respawn a dismissed pet or replace your active companion when you move.

### Shuffle companions: how it works

The seventh setting, **Shuffle companions**, affects Random and By habitat. Random keeps a shuffled eligible cycle; By habitat first draws its weighted group and then uses a separate cycle for that planet habitat and group. Stations and the Anomaly share the ordinary Random cycle. Shuffle does not force a full-roster tour or override the habitat weights.

Only a request accepted by the game's summon queue consumes a turn. Rejected placement, retries and cancellation do not. When the currently eligible remainder is exhausted, that eligible pool starts another round; temporarily unavailable pets retain their history. With another eligible pet in the chosen group, the next round avoids immediately repeating that group's last accepted choice. A sole eligible pet can repeat.

Adopting or abandoning companions updates the cycle. Renaming or reordering slots between opportunities does not reset it. Cycles are temporary: local save loading, including reloading the same save, or a new game session resets them. The remembered manual favourite is separate and is preserved. Queue acceptance is not a guarantee that the game has rendered a visible pet.

### New-install defaults and upgrades

A fresh 0.10.0-native-test configuration uses **By habitat + Shuffle companions ON**, automation ON and all three supported locations ON. The Random biome preference is also ON but only applies if you select Random. Existing 0.8.x preferences retain their previous mode, location and ON/OFF choices; the new shuffle option starts OFF for those upgrades. Existing 0.9.0 settings, including the shuffle choice, remain unchanged. Changing a setting does not immediately summon or dismiss a pet: the next ship exit or successful local save load supplies a new opportunity.

## Source and bug reports

Source repository: [Companion Auto Summon on GitHub](https://github.com/lineum-dynamics/nms-companion-auto-summon).

Reports from this early alpha help establish what works across installations. Please include:

- Mod version, exact game version/build, Windows version and confirmation that the game is the Steam edition.
- The steps to reproduce the problem, what you expected, what happened and whether it happens again after a normal restart.
- Your location: planet and habitat if known, space station or Space Anomaly; also whether you had just loaded a save, left a ship or teleported.
- Selection mode, Shuffle setting, automation/location switches, and whether an eligible companion was already active or could be summoned manually.
- Other installed mods or ASI loaders, and whether the previous Python/pyMHF launcher was running.
- A relevant excerpt from the native log in **%LOCALAPPDATA%/NMS-AutoPet/logs**, plus a screenshot or short recording if it helps explain the behaviour. Remove personal paths or identifiers before sharing; do not upload saves or credentials.

An accepted queue entry in a log is useful evidence, but please also say whether the pet actually appeared. For a crash, include the last action before it and any relevant Windows or game error text. Keep your backup until you are satisfied with the result. Close the game before changing installed files; the uninstall instructions above explain how to disable the module without deleting your settings or backups.

## Credits and disclosure

- [Ultimate ASI Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader), **9.7.4 x64**, by ThirteenAG. The package includes the unmodified pinned loader and its notices.
- [MinHook](https://github.com/TsudaKageyu/minhook), **1.3.4**, by Tsuda Kageyu and contributors, including HDE notices.
- [JSON for Modern C++](https://github.com/nlohmann/json), **3.12.0**, by Niels Lohmann and contributors.
- [pyMHF](https://github.com/monkeyman192/pyMHF) and [NMS.py](https://github.com/monkeyman192/NMS.py), by monkeyman192, provided the original Python runtime and native research references. Python/pyMHF are not dependencies of this native player package.

The archive includes component and statically linked runtime licence notices. Generative AI was used extensively for code, interface work, translations and this description. This is an unofficial mod, not an official Hello Games product.

---

## Internal readiness and metadata — do not publish this section

- Current artifact: **0.10.0-native-test**, unchanged and available as the Main / Primary Nexus file and the GitHub prerelease asset. Its immutable ZIP is 3,725,420 bytes with SHA-256 `e00a8818230dba24066fcdc4d75a01d696c9e2573d2538aa6a9b05c5dd14bebb`. Nexus currently shows Safe to use and a Manual download; its linked scan was 0/68. These are bounded file checks, not safety guarantees.
- Nexus mod **4579** was published as EARLY ALPHA at **28 September 2026, 18:43 CEST**. The GitHub repository is public with default branch `main`; prerelease `v0.10.0-native-test` and its matching ZIP were read back on **30 September 2026**. Preserve the approved title/byline, author **Lineum Dynamics**, category **Creatures**, media and **AI-Generated Content** / **AI Media** disclosure tags.
- Installation is the two-folder native overlay described above. The native r3 log records one normal Steam startup, exact-executable acceptance, completed pre-activation backup, twelve hooks plus binding guard enabled, local save load and two accepted queue requests. The player confirms visible appearance after ship exit; startup appearance remains uncertain, not an established failure. The menu remains unconfirmed. Retain the exact package identity, verify startup appearance, and complete restart, controls, placement, second-PC and multiplayer acceptance. Native compiled files are not exempt from Nexus or antivirus review.
- Earlier upload records are retained in the Nexus archive, not clearance for the native package: **49195** (0.9.1 development trial) had a 0/65 ZIP report despite the Nexus suspicious-file state; **49196** (0.9.2-test) was quarantined with ZIP 3/60 and launcher 8/70; **49197** (0.9.3-test) was quarantined with ZIP 1/58 and later launcher 3/71. Their exact hashes and bounded evidence remain in the scan records and [TESTER-HANDOFF](TESTER-HANDOFF.md). Do not delete or rewrite those uploads or infer a false-positive cause.
- The unchanged ZIP is available through the public Nexus page and GitHub prerelease. The owner-account download matched its recorded hash. The second Windows/Steam tester has not yet confirmed receipt, installation or gameplay; multiplayer remains unverified.
- Source: [canonical public repository](https://github.com/lineum-dynamics/nms-companion-auto-summon). Future commits use `core@lineum.io`; historical author metadata remains unchanged. No open-source licence for the original mod is implied by repository visibility.
- Donation Points eligibility and payment destinations still need checks. No verified company payment URL or in-game donation notice is configured. Do not invent a service, link, revenue promise or request to support staff. Existing external-contact restrictions remain in force.
- The alpha does not summon on teleport arrival or base removal and does not respawn after manual dismissal. Recent logs confirm a custom-menu safety stop on `menu_unexpected_thread`; whether the owner-reported grouped roster caused the thread change is unconfirmed. Diagnose the callback phase before changing the guard. Rechargeable technology and complete native localization remain future work; habitat weighting stays **13:5:1**.
