# Companion Auto Summon for No Man's Sky - by Lineum Dynamics

**UNPUBLISHED NEXUS DRAFT — page created; not publicly released or ready for publication.**

Preparation status, 28 September 2026: account
[`LineumDynamics`](https://www.nexusmods.com/profile/LineumDynamics) owns the
created No Man's Sky draft, category **Creatures**, mod ID **4579**. Its status
is visibly **Unpublished**: [draft page](https://www.nexusmods.com/nomanssky/mods/4579)
and [general editor](https://www.nexusmods.com/games/nomanssky/mods/4579/edit/general).
The exact Nexus page title is **Companion Auto Summon for No Man's Sky - by
Lineum Dynamics**, with author field **Lineum Dynamics**. The last verified General section
was saved and marked **Section complete**: version `0.9.1-play-trial`, language
**English**, and tags **AI-Generated Content**, **AI Media** and **Quality of
Life**. The authentic company avatar was previously uploaded and visually
checked. The **1600 × 900** gallery cover and company avatar remain unchanged.
The corrected **1300 × 372** [header](https://staticdelivery.nexusmods.com/mods/1634/images/headers/4579_1790592385.jpg)
is uploaded and visually verified on the actual mod page: a dark decorative
background without embedded text, a company mark or white elements, with a
subdued paw on the right. Nexus supplies the full approved title, which is
legible in the checked screenshot. Media is **Section complete**; the page
still shows **Unpublished**. Files is now **Section complete**.
The Mod Name field requires
the ASCII hyphen above; the gallery title accepts a typographic dash. No code
ZIP was uploaded during initial draft creation; the first test upload is recorded below. Release permissions remain pending. The earlier disabled upload dialog and
`Something went wrong. Please try again.` error are historical; draft creation
has now succeeded. Keep this status outside the public description. Publication
remains blocked by unfinished release readiness, not draft creation.

Historical readback: the previous body and summary were saved to Nexus on
28 September 2026 with version **0.9.1-play-trial** (production 0.5.1, menu
0.9.0-selection). The revised 0.9.2 body below was subsequently saved and read back.
The file **Companion Auto Summon - 0.9.1 development trial**, file ID **49195**,
is saved under **Miscellaneous**, with mod-manager downloads disabled. Its ZIP
is 187,533 bytes; SHA-256:
`7025712f8f9eb89a238f37e3871e817aefee99da9bf177d2163507d23b1a1b43`.
The file description and changelog distinguish offline checks from pending live
acceptance, and state the menu-thread and absent travel-trigger limitations.
This is an unpublished test upload, not a public or stable release.

Scan readback on the same date: Nexus displayed **Some suspicious files**, while
its linked [VirusTotal report](https://www.virustotal.com/gui/file/7025712f8f9eb89a238f37e3871e817aefee99da9bf177d2163507d23b1a1b43)
showed **0/65** detections for the exact ZIP hash. The discrepancy is unresolved;
neither a false-positive cause nor a clean Nexus status has been established.

Current uploaded copy: **0.9.2-test**, production 0.5.1, combined 0.9.2-play-trial,
menu 0.9.1-diagnostics, Nexus file **49196**. Full title/byline, version, summary
and portable description were saved and read back; the page stays Unpublished.
The exact ZIP is quarantined by automated checks and cannot be routinely
downloaded. Its linked VirusTotal result is 3/60; the exact compiled entry point
reports 8/70. The specific cause and false-positive status are unresolved.
See [TESTER-HANDOFF](TESTER-HANDOFF.md) and [the scan record](../research/PORTABLE-SCAN-092.md).
No support message was sent; external contact remains unauthorized.

## Short summary

Automatically bring along an owned companion after loading your save or leaving your starship. Choose Last selected, Random or weighted By habitat selection, with optional shuffle. Configure it in the native Quick Menu. The game's summoning and placement rules still apply.

## Description

Keep a companion beside you without opening the companion menu after every landing. When you leave your starship or load your local save, the mod checks your settings and asks the game to summon one of your eligible owned companions.

Choose a familiar favourite, let Random vary your company, or use By habitat to favour companions suited to the planet under the explicit rules below. The mod does not give you pets, unlock slots, accelerate growth, improve combat values or bypass placement restrictions. You still need to own a companion that the game permits you to summon.

If your landing platform or surrounding terrain is unsuitable, the request can wait while you walk somewhere suitable. A selected random pet stays fixed during that wait. Entering your ship, choosing a pet manually or changing a mod setting cancels the pending request.

## Settings in the 0.9.2-test portable candidate

In the portable test candidate, open **Quick Menu → Companions → Companion Auto Summon** to reach the mod's settings. On PC, the default Quick Menu key is **X**. If you have changed your controls, use your assigned Quick Menu key instead.

That page has seven controls:

- **Automatic summoning:** ON/OFF. OFF cancels waiting automatic requests without dismissing your current companion. Turning ON waits for your next ship exit or successful local save load.
- **Selection:** Last selected, Random or By habitat. Last selected remembers a successful manual choice for that save; the other modes do not replace your remembered favourite.
- **Random: prefer matching biome:** favour eligible companions whose stored native habitat exactly matches the planet. If the habitat is unknown or no eligible match exists, use the ordinary eligible random pool. This only affects Random on planets, not Last selected, By habitat, stations or the Space Anomaly.
- **Planets:** allow automatic summoning on planets.
- **Space stations:** allow automatic summoning on stations.
- **Space Anomaly:** allow automatic summoning in the Nexus.
- **Shuffle companions:** use a shuffled cycle in Random, or within the weighted group chosen by By habitat. It does not affect Last selected.

Fresh-install defaults are **By habitat**, **Shuffle companions ON**, automation ON, all three locations ON, and the Random biome preference ON. Existing preferences are preserved; migration from older schemas starts the new shuffle option OFF.

Applied changes report the actual value, such as **Selection: By habitat**, **Shuffle companions: ON** or **Space stations: OFF**. If several settings change together, the confirmation lists them together. A failed save adds **(session only)**; an unchanged value produces no new confirmation. The portable candidate and its presentation still require live acceptance.

## Compatibility

The supported target is **Windows 10/11 x64, Steam build 25442159 / Cosmos 7.04**, with the exact executable fingerprint listed in the package manifest. Other builds, stores and operating systems are not supported. A game update requires renewed compatibility checks; the launcher refuses an unknown executable.

The **0.9.2-test** ZIP includes **Companion Auto Summon.exe**, Python 3.11.9
and its pinned mod runtime. You do not install Python or run pip. Windows .NET
Framework 4 and Microsoft Visual C++ v14 x64 are prerequisites. A missing VC++
runtime is explained by the launcher; use Microsoft's official runtime
instructions linked in the packaged README. Nothing is downloaded automatically.
This is not a PAK to drop into GAMEDATA/MODS. Portable live launch, second-PC
installation, multiplayer and compatibility with other mods remain unverified.

## Start the portable test

1. Quit NMS normally, then extract the complete ZIP into a new folder.
2. Double-click **Companion Auto Summon.exe** and select **Check installation**.
   Use **Choose game folder** if your Steam installation is not found.
3. Open Steam, sign in and select **Start game**. The launcher makes and verifies
   a private backup before every normal start; a failed backup prevents launch.
4. Keep the launcher open for the first live check. Closing its window is
   designed to leave the host/game running, but that remains unverified in game.

Backups, logs and working sessions stay under `%LOCALAPPDATA%\NMS-AutoPet\`.
Existing settings and manual choices are preserved; verified private session
copies keep runtime writes out of the extracted distribution. Do not terminate
the background host while playing. To play without the mod, quit normally and
start NMS through Steam. Follow **README.txt**, **README.cs.txt** and
**Multiplayer test.txt** in the supplied archive.

## FAQ

**Do I need to select a companion first?**

For Last selected, manually summon an owned companion once. Random and By habitat need no previous choice, but still require an eligible owned pet. A new installation never supplies a companion of its own.

**Will it keep summoning a pet I dismiss?**

Dismissal does not create another automatic opportunity. Another successful local save load or ship exit can do so. An already active or queued companion also prevents a duplicate request.

**Does it change my save?**

The mod does not directly edit NMS save files. Its settings and remembered manual choices live separately in `%LOCALAPPDATA%\NMS-AutoPet`. The portable launcher requires a new private verified backup before each normal start. To play without the mod, close the game normally and restart through Steam.

**How much has been tested?**

The 0.9.0 trial has one player-confirmed visible Random companion after loading in the Space Anomaly. The player reports that settings appear to save; persistence across a restart has not been checked. This does not verify By habitat, shuffle outcomes or every native control. Neither the retained 0.9.1 nor the 0.9.2 portable candidate has live acceptance. Earlier 0.8.7 load/exit and OFF/ON observations remain version-specific; an intermittent startup failure is still unexplained. Repeatability, placement, HUD/icons, remapped/controller input and multiplayer remain acceptance work. Native menu and HUD text remain English; the other thirteen language catalogs are unreviewed drafts.

**Known current-trial limitation:** the custom settings menu can stop after a
native callback thread change. This happened in the retained 0.9.0 session; its
cause and relation to the player's actions are not established. Menu 0.9.1-diagnostics in the portable candidate records more detail but does
not resolve it. The guard stops the custom menu while
retaining its native binding protection; production summoning is separate.

Teleport arrival and base removal do not create a new summon opportunity.
A reported missing pet after teleport and disappearance after base removal do
not establish why the game removed it. The mod does not automatically respawn
pets simply because they disappear, which preserves manual dismissal.

## Selection and shuffle rules

**Implemented in the development candidate; full live acceptance and public release are pending.** These selection rules remain unchanged from 0.9.0 through the 0.9.2-test candidate. The later work improves settings feedback, diagnostic evidence and distribution; it does not change the selection balance below.

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

A fresh 0.9.2-test configuration uses **By habitat + Shuffle companions ON**, automation ON and all three supported locations ON. The Random biome preference is also ON but only applies if you select Random. Existing 0.8.x preferences retain their previous mode, location and ON/OFF choices; the new shuffle option starts OFF for those upgrades. Existing 0.9.0 settings, including the shuffle choice, remain unchanged. Changing a setting does not immediately summon or dismiss a pet: the next ship exit or successful local save load supplies a new opportunity.

## Credits and disclosure

Framework: [pyMHF](https://github.com/monkeyman192/pyMHF). Native research reference: [NMS.py](https://github.com/monkeyman192/NMS.py), both by monkeyman192. Generative AI was used extensively for code, interface work, translations and this description. This is an unofficial mod, not an official Hello Games product.

---

## Internal readiness and metadata — do not publish this section

- Current portable candidate: 0.9.2-test, production 0.5.1, combined 0.9.2-play-trial, menu 0.9.1-diagnostics. 770 developer tests and final package checks passed; file 49196 and this page were read back. Automatic quarantine blocks downloading. The retained 090-r2 files remain unchanged after normal closure; its [bounded live record](../research/LIVE-090.md) does not validate portable launch or multiplayer.
- The owner will download the exact validated test archive from the unpublished page and pass it unchanged to the second Windows/Steam tester. The upload is complete; downloading and handoff are blocked by quarantine. Do not claim either has happened.
- The portable executable and bundled runtime implement the intended simpler player flow, with explicit VC++ x64 prerequisite and automatic private backups. Quiet launch, detached lifetime, target initialization and clean-second-PC behavior still need final live acceptance. Standalone developer scripts remain separate and retain their panel.
- Source: [private canonical repository](https://github.com/lineum-dynamics/nms-companion-auto-summon). Do not advertise it as a publicly accessible source link.
- Complete third-party provenance, credits, licences and reuse permissions before uploading release files. Retain the saved **AI-Generated Content** and **AI Media** disclosure tags under the reviewed submission rules; do not substitute AI Assisted.
- Donation Points eligibility and payment destinations still need checks. No donation URL, account or revenue promise is configured here.
- Investigate the observed callback-thread/menu lifecycle before claiming reliable access to every setting. Do not assign a despawn cause or add teleport/base-removal triggers from the current observation alone.
- Weighted habitat selection and shuffle are implemented in production 0.5.1 and unchanged in 0.9.2-test; their live acceptance is pending. The seven-control rules above describe that candidate, not the historical six-control 0.8.7 trial. Rechargeable technology and native translations remain unfinished. No publication is authorized until readiness is complete.
