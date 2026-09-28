# Companion Auto Summon for No Man's Sky

by **Lineum Dynamics**

**LOCAL DRAFT — not uploaded. Update the validation status, final installer instructions, third-party credits and permissions before publishing.**

Current branding candidate: **0.4.9-experimental**, with combined developer
trial **0.8.7-play-trial** and menu **0.8.5-branding**. Validation passed 333
production and 675 developer tests. The final 41-file `087-r1` bundle passed
actual-framework checks, all six temporary preference paths and both Python
and Windows PowerShell 5.1 read-only preflights; focused checks were repeated
after its Korean translation correction. This candidate has not launched.
The running 0.8.4 and prepared 0.8.6-r1 remain
unchanged. The in-game short title is **Companion Auto Summon**; stable filenames
and player-data paths are retained. The canonical source is the currently
private [Lineum Dynamics repository](https://github.com/lineum-dynamics/nms-companion-auto-summon).

The current candidate retains six native settings, passive summon diagnostics
and read-only language observation. It does not enable translated rendering or
fix intermittent startup placement. In 0.8.4 the player reported one invisible
Nexus startup and later confirmed a different Random pet after a ship exit.
Do not publish blanket startup, native-menu or multiplayer verification claims.
Earlier results below retain their explicit version boundaries.

One historical Random-mode Anomaly startup was confirmed for 0.4.4 / 0.7.1. On 27 September 2026, load arming at 22:23:39.698 led to native queue acceptance at 22:23:42.250 (logged 2.56 seconds). That observer recorded the expected active companion at 22:23:42.266, on its first update, then stopped. The player confirmed visible appearance. No ship exit or automatic retry preceded this result. This is one successful run, not a fix for the earlier intermittent failure; only passive diagnostics changed.

## Short description

Automatically summon an owned companion after loading a save or leaving your starship. Remember your manual favourite or choose a random eligible pet, optionally preferring the current planet's habitat. Native summoning and placement rules still apply.

## What Companion Auto Summon does

Companion Auto Summon requests a companion after you leave your starship or successfully load your local save, when the game allows summoning. Choose your last manually selected companion, or use Random to select from your eligible owned companions.

The 0.4.3 candidate adds one deferred opportunity after loading, using your existing settings, the same delay and the same native checks as the ship-exit path. Loading itself does not directly summon a pet; the request is handled later by the established local-player callback. This is not a continuous respawn rule: dismissing a pet does not repeatedly summon it again.

Random mode can prefer companions whose native habitat matches the current planet. If no eligible companion matches, or the habitat is unknown, it uses the ordinary eligible random pool. This preference is on by default and has no effect on Last manually selected mode, space stations or the Nexus.

When placement is temporarily unsuitable, the mod keeps the request pending until a suitable place is available or you cancel it. Entering the starship, making a manual companion choice or changing a Companion Auto Summon setting cancels that pending request. A chosen random companion stays fixed throughout the same pending request.

The mod does not unlock or create pets, alter their growth, trust, eggs or combat values, increase companion capacity, or override native summon and placement restrictions.

## Settings

- Automatic summoning: on by default.
- Locations: planets, space stations and the Nexus, individually configurable and on by default. The game's own permission checks still apply.
- Companion selection: Last manually selected by default, or Random.
- Prefer same biome in Random mode: on by default.
- Status and companion displays.

The combined developer trial has a native companion settings page for the six
preferences above; status/companion displays also remain in the temporary pyMHF
desktop panel. Both use the same production preference queue. Return to the game
after changing a preference so it can be applied and saved. The native page has
partial live evidence, including distinct setting icons in 0.8.4; complete
input, navigation and controller acceptance remains pending. The standalone
production package still uses the separate panel and has no native page.

In the default mode, summon an owned companion manually once to choose your favourite. Random mode does not need a previous manual choice, but you must own an eligible pet. Random selections do not replace your remembered manual favourite.

## Requirements and support scope

- Windows x64 and the Steam edition of No Man's Sky.
- Exact supported executable: Steam build 25442159 / Cosmos 7.04. The SHA256 is supplied in the package manifest; a different executable is refused.
- The development candidate uses Python 3.11–3.13 x64 and pyMHF 0.2.4 with GUI dependencies. The planned public package will bundle a tested runtime so players do not need a separate Python installation; this packaging has not yet been implemented or validated.
- Start the game with the supplied Companion Auto Summon launcher. This is a Python/pyMHF mod, not a PAK to place in GAMEDATA/MODS.

Other game builds, stores and operating systems are not supported by this package. Updates to NMS require a new compatibility check.

## Installation — draft pending final packaging

The development launcher creates a private Python environment and downloads
missing pyMHF dependencies. The combined trial runs production auto-summoning
and native settings together in one host, with exact-build compatibility
checks. Neither is the planned public installer. The public experience is to
extract the ZIP and double-click a launcher with a bundled offline runtime;
that packaging remains unverified. Replace this paragraph with the final
verified setup procedure before publishing.

## Removing or disabling Companion Auto Summon

Quit NMS, then launch it normally through Steam to play without Companion Auto Summon. Manual preferences are stored outside the save files in `%LOCALAPPDATA%\NMS-AutoPet`. This legacy directory is intentionally retained so the rename preserves existing choices. `settings.json` stores settings; `state.json` stores manual companion choices per save. Close the game before removing either file if you want to reset those preferences.

## Validation and known limits — update before upload

A separate developer candidate, 0.7.0-play-trial, adds the first
native setting: automatic summoning ON/OFF. It uses the unchanged 0.4.3
production preference queue and preserves other preferences. It passed 408
developer tests and actual pyMHF discovery/temporary-preference checks outside
the game: two Mods, 15 callbacks across 11 targets, no hook registration or
personal preference access. This does not establish in-game activation,
held-input behavior, remapped controls or controller support. Tail-only or
otherwise uncorrelated activations do not change settings. On 27 September
2026, after normal exit and a fresh verified backup, the 0.7.0 trial registered
both Mods and 11 hook targets with automation ON. Complete live preference
validation remains pending. This developer candidate is not the player ZIP.

All six existing preferences now have native controls in the combined trial;
their full acceptance remains unfinished. The separate pyMHF panel is temporary
and will be retired from the player interface after the complete native page
passes validation; existing settings will be preserved. The framework may
remain the background runtime. Do not advertise fully verified native settings
or panel-free installation until that transition has actually been delivered.

Status on 27 September 2026: production 0.4.3 passed 230 offline tests, including 140 runtime tests, and the developer suite passed 341 tests. The actual production GUI and the 0.6.2 combined-folder smoke checks also passed without game access or hook registration.

The subsequent 0.4.3 / 0.6.2 live trial registered both mods with automatic summoning enabled. After a local save loaded at a space station, the log recorded the load-triggered request, a Random selection from five eligible owned companions and native queue acceptance about 2.69 seconds after arming. No ship-exit arming event preceded this request. The player confirmed that the companion actually appeared after loading and clarified that the location was a station, not the Nexus. This verifies one station startup summon in Random mode on the development machine; the queue timing is not a measurement of visible spawn latency.

Later in the same unchanged 0.4.3 / 0.6.2 session, the player confirmed one manual dismissal with no reappearance during the observed interval. The exact location, dismissal time and interval length were not independently established, nor was the dismissed pet linked to the earlier startup summon. This is a separate player-confirmed dismissal observation, not a station-specific or immediately-after-load test.

Earlier on the same date, production 0.4.2 registered in the combined 0.6.1 trial. Its log recorded an accepted station summon request, but there was no player confirmation that the companion appeared. This establishes registration and the logged request only. The earlier 0.4.2 offline baseline passed 212 tests. Historical AutoPet 0.4.1 passed 211 offline tests and widget checks; its habitat preference was not tested in-game. Earlier versions demonstrated a basic planetary Random summon, station summoning and restoring a manual selection after restart on the development machine. These historical results do not validate the new 0.4.3 behavior.

Startup on a planet or in the Nexus, startup in Last manually selected mode, broader dismissal regression, multiplayer, a second-PC installation, unsuitable-placement recovery and the remaining live scenarios are still pending. The two bounded observations do not verify those cases. No blanket compatibility claim is made for other mods.

## Credits and permissions — complete before upload

Framework: [pyMHF by monkeyman192](https://github.com/monkeyman192/pyMHF). Native-function research reference: [NMS.py](https://github.com/monkeyman192/NMS.py). Confirm attribution and any incorporated third-party material in the final package.

Project attribution: **Companion Auto Summon for No Man's Sky — by Lineum
Dynamics**. Licence and reuse permissions remain undecided; this attribution
does not assign them. The mod's code was developed with generative AI assistance,
including substantial code generation. Recheck the Nexus **AI-Generated Content**
and **AI Media** tagging requirements before uploading this AI-written page.

The intended release is free. No donation account or paid access is configured in this draft.
