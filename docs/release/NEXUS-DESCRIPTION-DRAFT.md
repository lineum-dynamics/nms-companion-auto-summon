# Companion Auto Summon for No Man's Sky - by Lineum Dynamics

**UNPUBLISHED NEXUS DRAFT — page created; not publicly released or ready for publication.**

Preparation status, 28 September 2026: account
[`LineumDynamics`](https://www.nexusmods.com/profile/LineumDynamics) owns the
created No Man's Sky draft, category **Creatures**, mod ID **4579**. Its status
is visibly **Unpublished**: [draft page](https://www.nexusmods.com/nomanssky/mods/4579)
and [general editor](https://www.nexusmods.com/games/nomanssky/mods/4579/edit/general).
The exact Nexus page title is **Companion Auto Summon for No Man's Sky - by
Lineum Dynamics**, with author field **Lineum Dynamics**. The General section
is saved and marked **Section complete**: version `0.8.7-play-trial`, language
**English**, and tags **AI-Generated Content**, **AI Media** and **Quality of
Life**. The authentic company avatar was previously uploaded and visually
checked. The **1600 × 900** gallery cover and company avatar remain unchanged.
The corrected **1300 × 372** [header](https://staticdelivery.nexusmods.com/mods/1634/images/headers/4579_1790592385.jpg)
is uploaded and visually verified on the actual mod page: a dark decorative
background without embedded text, a company mark or white elements, with a
subdued paw on the right. Nexus supplies the full approved title, which is
legible in the checked screenshot. Media is **Section complete**; the page
still shows **Unpublished** and a **Files missing** banner.
The Mod Name field requires
the ASCII hyphen above; the gallery title accepts a typographic dash. No code
ZIP has been uploaded, and files and permissions remain pending. The earlier disabled upload dialog and
`Something went wrong. Please try again.` error are historical; draft creation
has now succeeded. Keep this status outside the public description. Publication
remains blocked by unfinished release readiness, not draft creation.

## Short summary

Automatically bring along an owned companion after loading your save or leaving your starship. Use your last manually selected pet or choose a random eligible companion, with an optional planet-habitat preference. The game's summoning and placement rules still apply.

## Description

Keep a companion beside you without opening the companion menu after every landing. When you leave your starship or load your local save, the mod checks your settings and asks the game to summon one of your eligible owned companions.

Choose a familiar favourite or let Random vary your company. The mod does not give you pets, unlock slots, accelerate growth, improve combat values or bypass placement restrictions. You still need to own a companion that the game permits you to summon.

If your landing platform or surrounding terrain is unsuitable, the request can wait while you walk somewhere suitable. A selected random pet stays fixed during that wait. Entering your ship, choosing a pet manually or changing a mod setting cancels the pending request.

## Settings in the 0.8.7 trial

In the combined development trial, open **Quick Menu → Companions → Companion Auto Summon** to reach the mod's settings. On PC, the default Quick Menu key is **X**. If you have changed your controls, use your assigned Quick Menu key instead.

That page has six controls:

- **Automatic summoning:** ON/OFF. OFF cancels waiting automatic requests without dismissing your current companion. Turning ON waits for your next ship exit or successful local save load.
- **Selection:** Last selected or Random. Last selected remembers a successful manual choice for that save; Random does not replace your remembered favourite.
- **Random: prefer matching biome:** favour eligible companions whose stored native habitat exactly matches the planet. If the habitat is unknown or no eligible match exists, use the ordinary eligible random pool. This does not affect Last selected, stations or the Space Anomaly.
- **Planets:** allow automatic summoning on planets.
- **Space stations:** allow automatic summoning on stations.
- **Space Anomaly:** allow automatic summoning in the Nexus.

Defaults are automation ON, all three locations ON, Last selected, and biome preference ON. Native controls have partial live validation.

## Compatibility

The supported target is **Windows x64, Steam build 25442159 / Cosmos 7.04**, with the exact executable fingerprint listed in the package manifest. Other builds, stores and operating systems are not supported. A game update requires renewed compatibility checks; the launcher refuses an unknown executable.

The current development setup requires **Python 3.11–3.13 x64 and pyMHF 0.2.4**. Start it through its supplied launcher. This is a Python/pyMHF mod, not a PAK to drop into GAMEDATA/MODS. The planned portable player installer is unfinished. Multiplayer, second-PC installation and compatibility with other mods are not yet verified.

## FAQ

**Do I need to select a companion first?**

For Last selected, manually summon an owned companion once. Random needs no previous choice, but still requires an eligible owned pet. A new installation never supplies a companion of its own.

**Will it keep summoning a pet I dismiss?**

Dismissal does not create another automatic opportunity. Another successful local save load or ship exit can do so. An already active or queued companion also prevents a duplicate request.

**Does it change my save?**

The mod does not directly edit NMS save files. Its settings and remembered manual choices live separately in `%LOCALAPPDATA%\NMS-AutoPet`. Back up your progress before testing an experimental build. To play without the mod, close the game normally and restart through Steam.

**How much has been tested?**

In one 0.8.7 session, the player confirmed visible Random companions after Nexus loading and ship exit, no apparent return after manual dismissal, and the expected OFF/ON sequence. The dismissal wait was not independently timed. Different pets were selected, and an earlier intermittent startup failure remains unexplained. Repeatability, Last selected startup, the other five controls, HUD/icons and remapped/controller input still need testing. Native menu and HUD text remain English.

## Upcoming 0.9.0: habitat selection and rotation

**Implemented in the development candidate; not yet tested in game or released.** The 0.8.7 trial described above keeps its existing behavior. These are the rules prepared for 0.9.0; balance may change after testing.

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

Aquatic does not automatically mean Waterworld: a crab adopted underwater on a Frozen planet is classified by its stored native habitat. Adoption and summoning are different: [a Water-bound crab owner's report](https://steamcommunity.com/app/275850/discussions/0/814724377262342410/) confirms that owning such a pet does not let the player summon it underwater. Fish caught as inventory items and creatures from gas giant moons are not evidence of adoptable Gas Giant fauna. These findings explain the selection rules; our 0.9.0 candidate has not yet been tested on either planet type.

### Stations, waiting and no suitable companion

On space stations and in the Space Anomaly, By habitat uses the ordinary unweighted eligible owned pool. There is no planet habitat to favour. The location switches and all normal game restrictions still apply; the mod does not add freighter support.

Unknown planet habitat waits for usable information. If the known owned roster has no approved habitat group, that opportunity is skipped with **No suitable companion for this habitat.** It does not substitute an unrelated pet. If a suitable owned pet exists but is temporarily ineligible, or placement is obstructed, the request can wait for a valid opportunity. No owned companions means no free pet.

Once selected, a pet stays fixed while placement is retried. Ship entry, manual pet preview/selection, a settings change, an active/queued pet or a local save change can end the wait. Losing the selected pet, moving it to a different slot during a pending request or an ambiguous identity cancels that request without drawing a replacement. By habitat also cancels if its supported planet/neutral context changes; Random keeps its selection across temporary location changes. An accepted request finishes that opportunity: it does not repeatedly respawn a dismissed pet or replace your active companion when you move.

### Shuffle companions: how it works

The seventh setting, **Shuffle companions**, affects Random and By habitat. Random keeps a shuffled eligible cycle; By habitat first draws its weighted group and then uses a separate cycle for that planet habitat and group. Stations and the Anomaly share the ordinary Random cycle. Shuffle does not force a full-roster tour or override the habitat weights.

Only a request accepted by the game's summon queue consumes a turn. Rejected placement, retries and cancellation do not. When the currently eligible remainder is exhausted, that eligible pool starts another round; temporarily unavailable pets retain their history. With another eligible pet in the chosen group, the next round avoids immediately repeating that group's last accepted choice. A sole eligible pet can repeat.

Adopting or abandoning companions updates the cycle. Renaming or reordering slots between opportunities does not reset it. Cycles are temporary: local save loading, including reloading the same save, or a new game session resets them. The remembered manual favourite is separate and is preserved. Queue acceptance is not a guarantee that the game has rendered a visible pet.

### New-install defaults and upgrades

A fresh 0.9.0 configuration uses **By habitat + Shuffle companions ON**, automation ON and all three supported locations ON. The Random biome preference is also ON but only applies if you select Random. Existing 0.8.x preferences retain their previous mode, location and ON/OFF choices; the new shuffle option starts OFF for those upgrades. Changing a setting does not immediately summon or dismiss a pet: the next ship exit or successful local save load supplies a new opportunity.

## Credits and disclosure

Framework: [pyMHF](https://github.com/monkeyman192/pyMHF). Native research reference: [NMS.py](https://github.com/monkeyman192/NMS.py), both by monkeyman192. Generative AI was used extensively for code, interface work, translations and this description. This is an unofficial mod, not an official Hello Games product.

---

## Internal readiness and metadata — do not publish this section

- Retained live trial: production 0.4.9, combined 0.8.7 / `087-r1`, menu 0.8.5-branding. Separate offline candidate: production 0.5.0, combined 0.9.0 / `090-r2`, menu 0.9.0-selection. The detailed upcoming rules were saved and read back on the unpublished Nexus page on 28 September 2026; version metadata stays 0.8.7 until a deliberate update. Retain the bounded [live record](../research/LIVE-087.md); do not turn one session into a general guarantee.
- **Installation placeholder:** replace with the verified player-package procedure only after portable packaging and clean-machine acceptance. No final installation instructions are approved yet.
- The temporary pyMHF desktop panel and standalone script are development implementation details, not the intended player settings interface. The combined trial still retains the panel, and the standalone script lacks the native page. Keep those facts in internal readiness records; removing the panel from the player package and verifying native controls remain release work. The pyMHF runtime dependency is separate from its desktop panel.
- Source: [private canonical repository](https://github.com/lineum-dynamics/nms-companion-auto-summon). Do not advertise it as a publicly accessible source link.
- Complete third-party provenance, credits, licences and reuse permissions before uploading release files. Retain the saved **AI-Generated Content** and **AI Media** disclosure tags under the reviewed submission rules; do not substitute AI Assisted.
- Donation Points eligibility and payment destinations still need checks. No donation URL, account or revenue promise is configured here.
- Weighted habitat selection and rotation are implemented in the separate 0.5.0 / 0.9.0 candidate, with live acceptance pending. The upcoming-version rules above mirror that candidate, not the running 0.8.7 behavior. Rechargeable technology and native translations remain unfinished. No publication is authorized until readiness is complete.
