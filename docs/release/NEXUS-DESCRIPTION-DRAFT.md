# Companion Auto Summon for No Man's Sky

by **Lineum Dynamics**

**LOCAL DRAFT — no Nexus page has been uploaded. Not ready for publication.**

## Short summary

Automatically bring along an owned companion after loading your save or leaving your starship. Use your last manually selected pet or choose a random eligible companion, with an optional planet-habitat preference. The game's summoning and placement rules still apply.

## Description

Keep a companion beside you without opening the companion menu after every landing. When you leave your starship or load your local save, the mod checks your settings and asks the game to summon one of your eligible owned companions.

Choose a familiar favourite or let Random vary your company. The mod does not give you pets, unlock slots, accelerate growth, improve combat values or bypass placement restrictions. You still need to own a companion that the game permits you to summon.

If your landing platform or surrounding terrain is unsuitable, the request can wait while you walk somewhere suitable. A selected random pet stays fixed during that wait. Entering your ship, choosing a pet manually or changing a mod setting cancels the pending request.

## Settings

The combined development trial has six controls in its native companion settings page:

- **Automatic summoning:** ON/OFF. OFF cancels waiting automatic requests without dismissing your current companion. Turning ON waits for your next ship exit or successful local save load.
- **Selection:** Last selected or Random. Last selected remembers a successful manual choice for that save; Random does not replace your remembered favourite.
- **Random: prefer matching biome:** favour eligible companions whose stored native habitat exactly matches the planet. If the habitat is unknown or no eligible match exists, use the ordinary eligible random pool. This does not affect Last selected, stations or the Space Anomaly.
- **Planets:** allow automatic summoning on planets.
- **Space stations:** allow automatic summoning on stations.
- **Space Anomaly:** allow automatic summoning in the Nexus.

Defaults are automation ON, all three locations ON, Last selected, and biome preference ON. Native controls have partial live validation; the temporary pyMHF desktop panel remains available during development. The standalone production script uses that panel and does not include the native page.

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

## Credits and disclosure

Framework: [pyMHF](https://github.com/monkeyman192/pyMHF). Native research reference: [NMS.py](https://github.com/monkeyman192/NMS.py), both by monkeyman192. Generative AI was used extensively for code, interface work, translations and this description. This is an unofficial mod, not an official Hello Games product.

---

## Internal readiness and metadata — do not publish this section

- Candidate: production 0.4.9, combined 0.8.7 / `087-r1`, menu 0.8.5-branding. Retain the bounded [live record](../research/LIVE-087.md); do not turn one session into a general guarantee.
- **Installation placeholder:** replace with the verified player-package procedure only after portable packaging and clean-machine acceptance. No final installation instructions are approved yet.
- Source: [private canonical repository](https://github.com/lineum-dynamics/nms-companion-auto-summon). Do not advertise it as a publicly accessible source link.
- Complete third-party provenance, credits, licences and reuse permissions before upload. Apply **AI-Generated Content** and **AI Media** disclosure under the reviewed submission rules; do not substitute AI Assisted.
- Donation Points eligibility and payment destinations still need checks. No donation URL, account or revenue promise is configured here.
- Weighted habitat selection, shuffle, rechargeable technology and native translations are roadmap work, not current features. No publication is authorized until readiness is complete.
