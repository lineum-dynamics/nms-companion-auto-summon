# Companion Auto Summon

**LOCAL DRAFT — not uploaded. Update the validation status, final installer instructions, attribution and permissions before publishing.**

## Short description

Automatically summon an owned companion after leaving your starship. Remember your manual favourite or choose a random eligible pet, optionally preferring the current planet's habitat. Native summoning and placement rules still apply.

## What Companion Auto Summon does

Companion Auto Summon requests a companion after you leave your starship and the game allows summoning. Choose your last manually selected companion, or use Random to select from your eligible owned companions.

Random mode can prefer companions whose native habitat matches the current planet. If no eligible companion matches, or the habitat is unknown, it uses the ordinary eligible random pool. This preference is on by default and has no effect on Last manually selected mode, space stations or the Nexus.

When placement is temporarily unsuitable, the mod keeps the request pending until a suitable place is available or you cancel it. Entering the starship, making a manual companion choice or changing a Companion Auto Summon setting cancels that pending request. A chosen random companion stays fixed throughout the same pending exit.

The mod does not unlock or create pets, alter their growth, trust, eggs or combat values, increase companion capacity, or override native summon and placement restrictions.

## Settings

- Automatic summoning: on by default.
- Locations: planets, space stations and the Nexus, individually configurable and on by default. The game's own permission checks still apply.
- Companion selection: Last manually selected by default, or Random.
- Prefer same biome in Random mode: on by default.
- Status and companion displays.

The controls are in the separate pyMHF desktop window. Alt+Tab to it and open the CompanionAutoSummon tab. They are not added to the game's X quick menu. Return to the game after changing a preference so it can be applied and saved.

In the default mode, summon an owned companion manually once to choose your favourite. Random mode does not need a previous manual choice, but you must own an eligible pet. Random selections do not replace your remembered manual favourite.

## Requirements and support scope

- Windows x64 and the Steam edition of No Man's Sky.
- Exact supported executable: Steam build 25442159 / Cosmos 7.04. The SHA256 is supplied in the package manifest; a different executable is refused.
- The development candidate uses Python 3.11–3.13 x64 and pyMHF 0.2.4 with GUI dependencies. The planned public package will bundle a tested runtime so players do not need a separate Python installation; this packaging has not yet been implemented or validated.
- Start the game with the supplied Companion Auto Summon launcher. This is a Python/pyMHF mod, not a PAK to place in GAMEDATA/MODS.

Other game builds, stores and operating systems are not supported by this package. Updates to NMS require a new compatibility check.

## Installation — draft pending final packaging

The 0.4.2 development launcher currently creates a private Python environment and downloads missing pyMHF dependencies. The planned public experience is to extract the ZIP and double-click a launcher, with a bundled offline runtime and automatic compatibility checks. This launcher is not yet implemented. Replace this paragraph with the final verified setup procedure; do not publish an incomplete installer guide.

## Removing or disabling Companion Auto Summon

Quit NMS, then launch it normally through Steam to play without Companion Auto Summon. Manual preferences are stored outside the save files in `%LOCALAPPDATA%\NMS-AutoPet`. This legacy directory is intentionally retained so the rename preserves existing choices. `settings.json` stores settings; `state.json` stores manual companion choices per save. Close the game before removing either file if you want to reset those preferences.

## Validation and known limits — update before upload

The renamed 0.4.2 candidate passed 212 offline tests and a real pyMHF 0.2.4 / Dear PyGui 2.3.1 check of the renamed class and eight settings widgets, without registering hooks or connecting to the game. It has not been launched in NMS. The historical AutoPet 0.4.1 baseline passed 211 offline tests and widget checks; its habitat preference was not tested in-game. Prior versions demonstrated a basic planetary Random summon, station summoning and restoring a manual selection after restart on the development machine.

Multiplayer, a second-PC installation, unsuitable-placement recovery and the remaining live scenarios are still pending. These are not claimed as verified features in this draft. No blanket compatibility claim is made for other mods.

## Credits and permissions — complete before upload

Framework: [pyMHF by monkeyman192](https://github.com/monkeyman192/pyMHF). Native-function research reference: [NMS.py](https://github.com/monkeyman192/NMS.py). Confirm attribution and any incorporated third-party material in the final package.

Author display name and licence / reuse permissions remain to be supplied by the owner. The mod's code was developed with generative AI assistance, including substantial code generation. Apply the Nexus **AI-Generated Content** tag and **AI Media** for this AI-written page text under the current submission rules.

The intended release is free. No donation account or paid access is configured in this draft.
