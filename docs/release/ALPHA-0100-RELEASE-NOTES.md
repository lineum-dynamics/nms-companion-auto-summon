# Companion Auto Summon for No Man's Sky - by Lineum Dynamics

## 0.10.0-native-test — first public alpha

**EARLY ALPHA. Expect bugs, incomplete verification and possible conflicts.
Keep a separate backup made with NMS closed before installing or updating.**

This native version automatically requests an owned companion after a
successful local save load or ship exit, using the game's normal ownership,
physics and summon-placement checks. It loads during ordinary Steam startup.
**Python, pyMHF, a separate launcher and an external settings panel are not
required.** It does not unlock pets, lower game limits or summon where the
game refuses placement.

**Available publicly on Nexus Mods and GitHub.** Nexus publication was verified
on 28 September 2026 at 18:43 CEST. The public source repository and matching
GitHub prerelease were verified on 30 September 2026.

- [Nexus Mods page](https://www.nexusmods.com/nomanssky/mods/4579)
- [GitHub releases](https://github.com/lineum-dynamics/nms-companion-auto-summon/releases)
- [GitHub bug reports](https://github.com/lineum-dynamics/nms-companion-auto-summon/issues)

## Exact supported game

**Windows 10/11 x64 · Steam · Cosmos 7.04 · build 25442159**.
Required `NMS.exe` SHA-256:
`b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`.

The module verifies the actual running executable before enabling its game
hooks. An unknown/changed build refuses activation with an available localized
warning; an unsafe runtime state stops automation. Restart after resolving a
runtime failure. This is not a promise of compatibility with every other mod.
Consoles, GOG, Game Pass, macOS and Linux/Proton are not supported by this alpha.

## Install and start

1. Close NMS and retain your closed-game save backup. If you used the previous
   CAS Python/pyMHF test, stop it; both versions must never run together.
2. Extract the whole ZIP. Open Steam's **No Man's Sky → Manage → Browse local
   files** to find the game root containing `Binaries` and `GAMEDATA`.
3. Copy and merge those two folders from the extracted package into the game
   root. **Never overwrite a different existing `Binaries/winmm.dll`**: another
   mod may need it. Reuse only a byte-identical approved loader, whose SHA-256
   appears below and in the packaged README. Stop installation if it differs.
   On update, replace only CAS's own module and icon files.
4. Start through **Steam** normally. No administrator command or Python setup
   is part of installation.

The loader is official Ultimate ASI Loader 9.7.4 x64, unchanged bytes installed
under its supported `winmm.dll` name. Its SHA-256 is
`fa266e3513d02c08a1b808f28c10538a489eaffaa4b0707f7cc1066e71b5afd7`.
Third-party notices are included. Both native binaries remain subject to
antivirus checks; do not disable protection or use unverified replacements if
a file is blocked.

## Controls and selection

Open **Quick Menu → Companions → Companion Auto Summon**. **X is only the
default PC Quick Menu binding**; use the assigned input or controller prompt.
The mod follows native menu actions rather than simulating a fixed key press.

- **By habitat:** compatible groups have relative weights **13:5:1** for
  exact, related and acceptable habitat. Stations and the Anomaly are neutral.
  No compatible owned companion means no incompatible fallback.
- **Random:** chooses an eligible owned companion. Its same-biome preference
  applies only to this mode.
- **Last selected:** uses the last confirmed manual pet for the current save.
  A new player first needs to summon a pet manually in this mode.
- **Shuffle:** rotates accepted choices. A temporary placement/queue rejection
  waits and retries the same pet; only an accepted request advances rotation.
- **Automatic summoning / location toggles:** turn automation or individual
  supported places on/off. Changing settings cancels the pending opportunity.

Fresh preferences default to **By habitat + Shuffle ON**. Existing settings
and favorites are preserved; upgrades do not reset their choices. Move from
an unsuitable platform to open ground to give a pending request a suitable
place. Manual dismissal alone does not rearm automation. Teleport arrival and
base removal are not summon triggers in this version.

## Backups and removal

The module verifies a private snapshot before enabling its gameplay hooks.
**NMS is already running during that snapshot**; it is not a closed-game or
pre-launch backup. Keep the separate closed-game backup for alpha testing.
The mod does not restore, edit or write the original saves. Preferences,
favorites, backups and logs remain under `%LOCALAPPDATA%/NMS-AutoPet`.

With the game closed, remove only:

- `Binaries/scripts/CompanionAutoSummon.asi`
- `GAMEDATA/MODS/CompanionAutoSummon`

Leave the shared loader if any other mod needs it. Remove `Binaries/winmm.dll`
only if it is unused and still matches this package's loader hash. Do not
delete `Binaries`, `scripts`, `GAMEDATA` or other mods. Preferences and backups
are intentionally retained. Remove the native module before returning to an
older Python launcher.

## What has and has not been verified

The frozen r3 build passed policy/selection parity, 333 storage cases, 59
synthetic runtime cases, 16 backup checks, six native owned-host runs and
authored hook/ABI checks. A normal Steam start initialized the native module
and its verified pre-activation snapshot. The player confirmed a visible pet
after ship exit.

**Post-load appearance is uncertain**, not a confirmed failure: the player
initially reported no pet and then said it may have been overlooked. Native
queue acceptance was logged, which does not prove rendered appearance.
Menu order/icons/controls, normal restart, another PC and multiplayer remain
unverified. Please treat this as a test build, not a stable-release claim.

Native settings and HUD currently use **English**. Fourteen catalogs are
present; translated entries remain drafts and do not establish complete
in-game localization. Startup warnings use available Windows-language entries
with English fallback. Cosmetic HUD failures disable notices alone; summoning
and setting persistence continue.

## Issues reported after publication

- A companion is **not automatically summoned after teleport arrival** in this
  version. Only successful local save loads and ship exits create opportunities.
- The owner reported that the settings page disappears when the game groups a
  large companion roster. Recent logs confirm that the menu safety guard stopped
  after a callback-thread change (`menu_unexpected_thread`), but do not establish
  whether the grouped roster caused that change. The native safety guard has not
  been relaxed. Reliable grouped-roster menu support remains under investigation.

Neither issue is fixed by this alpha package. Please mention these conditions
when reporting related behavior.

## Exact download identity

| Item | Value |
| --- | --- |
| ZIP | `CompanionAutoSummon-0.10.0-native-test.zip` |
| Bytes | 3,725,420 |
| SHA-256 | `e00a8818230dba24066fcdc4d75a01d696c9e2573d2538aa6a9b05c5dd14bebb` |
| ZIP members | 30: ten game files, two guides, seventeen notices, one manifest |
| Nexus file | 49202, Main and Primary; mod-manager downloads OFF |

The public Nexus page displays **Safe to use**, and the native file's linked
VirusTotal result was **0/68** on 28 September 2026. An owner-account manual download
matched the bytes/hash above. This is not a safety guarantee or proof that a
second tester has installed it. Use the public page's **Manual download** for
the native Main file. The three older Python uploads (49195, 49196 and 49197)
are archived; their historical scans and quarantines are separate from this
native file. Historical Python packages are not the installation route for
this alpha.

## Please report bugs

Report reproducible problems through
[GitHub Issues](https://github.com/lineum-dynamics/nms-companion-auto-summon/issues)
or the public [Nexus page](https://www.nexusmods.com/nomanssky/mods/4579).
Include:

- Mod version and game build, Windows version, and other relevant mods.
- Location and trigger: load, ship exit, menu action or another event.
- Selection mode, Shuffle state and relevant location toggles.
- Steps, expected behavior, actual behavior and whether it repeats.
- A short relevant log excerpt or screenshot, with personal paths/account
  details removed. Logs are in `%LOCALAPPDATA%/NMS-AutoPet/logs`.

**Do not upload full saves, private backups, credentials or entire user-data
folders.** For an antivirus block, report the filename and exact detection
name; do not bypass it. Successful test reports are useful too, especially
post-load appearance, restart persistence and a two-player session.
