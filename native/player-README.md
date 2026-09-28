# Companion Auto Summon for No Man's Sky - by Lineum Dynamics

**0.10.0-native-test — private test candidate.** Windows 10/11, 64-bit, Steam.
This candidate is prepared for its first normal Steam launch. Its live startup,
pet appearance, multiplayer behavior and Nexus scan clearance are not yet
verified. Keep a separate closed-game backup before the first test.

## Install

1. Close No Man's Sky. Exit any previous Companion Auto Summon launcher or
   pyMHF session; the Python and native versions must never run together.
2. In Steam, right-click **No Man's Sky → Manage → Browse local files**. This
   opens the game folder containing `Binaries` and `GAMEDATA`.
3. Extract this ZIP to a temporary folder. If the game's `Binaries` already
   contains `winmm.dll`, **do not overwrite it**. Reuse it only if its SHA-256
   exactly matches the loader hash below. If it differs, stop installation;
   another mod may depend on that loader.
4. Copy the extracted **Binaries** and **GAMEDATA** folders into the game
   folder, merging the folders. When updating this mod, replace only its own
   `CompanionAutoSummon.asi` and icon files. No game executable is included.
5. Start the game normally through **Steam**. No Python installation, separate
   mod launcher, administrator command or external settings panel is required.

The game overlay contains exactly these files:

- `Binaries/winmm.dll` — official Ultimate ASI Loader 9.7.4, x64.
- `Binaries/scripts/CompanionAutoSummon.asi` — this mod's native module.
- Eight original icons in
  `GAMEDATA/MODS/CompanionAutoSummon/TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/`.

Approved loader SHA-256:
`fa266e3513d02c08a1b808f28c10538a489eaffaa4b0707f7cc1066e71b5afd7`.
The loader bytes are unchanged from the official `dinput8.dll` release asset;
`winmm.dll` is one of the loader's supported proxy names. The `.asi` is a native
DLL in the loader's documented format. Both remain subject to antivirus checks.
If either is blocked, leave it blocked and report the detection; do not add an
antivirus exclusion or substitute an unverified download.

## In the game

Open the game's **Quick Menu → Companions → Companion Auto Summon**. On a
default PC keyboard, Quick Menu is **X**; use your configured binding or the
game's controller prompt if it has been changed. The mod uses native menu
actions, not a hard-coded key press. Its settings appear before individual pets.

Fresh settings enable automatic summoning on planets, space stations and the
Space Anomaly, with **By habitat** selection and **Shuffle** enabled. Existing
settings are retained; an upgrade does not reset your previous choices.

- **By habitat:** selects from your owned companions using compatible habitat
  groups. Exact, related and acceptable groups receive relative weights 13:5:1
  where available. Stations and the Anomaly use a neutral pool. A volcanic
  planet can use a related scorched companion. If no owned companion fits,
  automation does not substitute an incompatible pet.
- **Random:** selects an eligible owned companion. Its separate same-biome
  preference applies only to this mode. Shuffle can rotate accepted choices.
- **Last selected:** uses your last confirmed manual selection for that save.
  A new player must first summon a companion manually in this mode.
- **Shuffle:** advances only after the game accepts a summon request. Temporary
  placement or queue failure retries the same companion; it does not reroll.

Automation gets one opportunity after a successful local save load or ship
exit. It waits for the game's ownership, physics and placement checks. On an
unsuitable building platform or terrain, move to open ground; a pending request
can continue when summoning becomes possible. Manual dismissal does not create
a new request. Previewing pets, entering the ship, changing settings or a new
accepted manual summon cancels the old request. The mod does not create pets,
lower gameplay limits, shorten game timers or bypass the native summon rules.

## Compatibility, settings and backups

The only supported executable is **Steam Cosmos 7.04, build 25442159**, SHA-256
`b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`.
The module checks the running executable before installing its gameplay hooks.
An unknown or changed build is refused with a localized warning. This does not
verify every possible interaction with other mods. Consoles, Game Pass, GOG,
macOS and Linux/Proton are not supported by this candidate.

In-game settings and HUD text currently use **English**. Fourteen language
catalogs exist, and startup errors use the available Windows language with
English fallback; that is not full in-game language support.

Preferences and per-save favorites stay in `%LOCALAPPDATA%/NMS-AutoPet`.
The mod does not ship anyone's settings or saves. Invalid existing settings are
retained and automation starts OFF; settings changes can then be session-only.

Before enabling its gameplay hooks, the module makes and verifies a private
snapshot under `%LOCALAPPDATA%/NMS-AutoPet/backups`. **The game is already
running at this point:** this is a pre-activation snapshot, not a closed-game
or pre-launch backup. If verification fails, activation is refused. The mod
never restores, edits or writes the original save files. For this first test,
retain your separate backup made while the game was closed.

Startup logs are in `%LOCALAPPDATA%/NMS-AutoPet/logs`. A missing pet is not proof
of a crash: check automation, location, selection mode and normal placement
eligibility first. A native runtime safety failure requires a game restart;
a HUD-only failure leaves summoning and settings working.

## Uninstall or return to the previous test

Close the game, then remove only:

- `Binaries/scripts/CompanionAutoSummon.asi`
- `GAMEDATA/MODS/CompanionAutoSummon`

Keep `Binaries/winmm.dll` if another ASI mod uses it. It may be removed only if
no other mod needs it and its hash still matches this package's loader.
Do not remove the game's `Binaries`, `scripts`, `GAMEDATA` or other mod folders.
Preferences, favorites and backups are deliberately retained. To return to
the earlier Python test, remove this native module first, then use the prior
launcher; never start both versions together.

`manifest.json` lists every packaged file and its SHA-256. `licenses/` contains
the required third-party notices. Packaging and offline tests do not establish
Nexus approval, live compatibility or successful visible pet appearance.
