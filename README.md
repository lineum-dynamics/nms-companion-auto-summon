# Companion Auto Summon for No Man's Sky - by Lineum Dynamics

**EARLY ALPHA / prerelease: 0.10.3-native-test for Steam Cosmos 7.06.**

**Download status, 23 October 2026:** the update is uploaded to Nexus as file
**50040**, Main / Primary, but automated quarantine currently blocks its download.
The exact ZIP scan reports **10/67** (09:06 UTC); a later ASI reanalysis reports
**15/63** (14:33 UTC). The cause is under
investigation; these are not confirmed false positives. The GitHub prerelease
currently records source and release notes, with binary upload on hold.
Do not disable security protection to install the file. See the
[scan and provenance record](docs/research/NATIVE-0103-SCAN.md).

Automatically summon an owned companion after a local save load or ship exit,
with an **experimental teleport trigger**, using the game's normal ownership,
eligibility and placement checks. Choose **Last selected**, **Random** or
**By habitat**, with optional **Shuffle**. This native C++ package starts normally
through Steam; no Python, pyMHF, separate launcher or external settings panel is
required. It does not create pets, unlock slots, accelerate growth or change
combat values.

[Nexus page](https://www.nexusmods.com/nomanssky/mods/4579) ·
[GitHub prerelease](https://github.com/lineum-dynamics/nms-companion-auto-summon/releases/tag/v0.10.3-native-test) ·
[Report a bug](https://github.com/lineum-dynamics/nms-companion-auto-summon/issues) ·
[Release notes and exact evidence](docs/release/0.10.3-COSMOS-706.md)

## Compatibility and verification

- **Target:** Windows 10/11 x64, Steam Cosmos **7.06**, build **25732212** only.
  NMS.exe SHA-256:
  `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
  Unknown executable builds refuse activation before gameplay hooks.
- **Mod package:** `0.10.3-native-test`, 3,725,947 bytes; ZIP SHA-256
  `df7cf87276391a9dc9bdf596611563b3787530da5d5c0107f51bb994f580b3f2`.
  Source checkpoint: `852c5c55458c563a8564090dd31305864483edf3`.
- **Final archive checked in game:** normal startup, visible companion after
  save load, settings/icons, and a clean base-to-station teleport. Earlier
  7.06 candidates also passed clean ship exit and station-to-base teleport.
- **Offline:** 808 developer tests, 28 menu scenarios, 21 load-context cases
  and the full native validation bundle passed. These do not establish
  antivirus clearance or broad gameplay acceptance.
- Consoles, GOG, Game Pass, macOS and Linux/Proton are unsupported by this alpha.
  Native menu/HUD currently use English; other catalogs remain unreviewed drafts.

The retained **0.10.2-native-test**, Nexus file **49469**, targets **7.05 /
Steam 25624745**. Files 49469 (0.10.2) and 49367 (0.10.1) are under **Old files**;
that category preserves release history and is separate from scan status.
Game release/build/hash, Git revision
and mod package version are separate identities. The test label remains until
the [promotion gates](docs/release/NATIVE-RELEASE-GATES.md) are evidenced; it is
not a permanent name or an automatic consequence of using native C++.

## Install and update

Use these instructions only for an accepted, matching archive; the current
Nexus upload remains quarantined.

1. Close NMS normally and make a separate backup while the game is closed.
   Exit any old CAS Python/pyMHF session; never run both runtimes together.
2. Extract `CompanionAutoSummon-0.10.3-native-test.zip` and read its English
   README. In Steam, open **No Man's Sky → Manage → Browse local files**.
3. Merge the extracted **Binaries** and **GAMEDATA** folders into that game root.
   Replace only this mod's owned files, with the game closed. Do not overwrite
   another mod's `Binaries/winmm.dll`; reuse an existing loader only if it matches
   the package's exact pinned hash.
4. Start normally through **Steam**. Open **Quick Menu → Companions → Companion
   Auto Summon**. X is the default PC binding; use your configured input or the
   controller prompt if different.

The overlay contains the pinned Ultimate ASI Loader 9.7.4, our
`Binaries/scripts/CompanionAutoSummon.asi`, and eight icons under
`GAMEDATA/MODS/CompanionAutoSummon/`. It is not a standalone PAK.

## Settings and selection

The seven controls are **Automatic summoning**, **Selection**, **Random: prefer
matching biome**, three separate location controls (**Planets**, **Space
stations**, **Space Anomaly**), and **Shuffle companions**. Turning automation
OFF cancels waiting requests without dismissing the current pet. Changing a
setting does not itself summon a pet.

- **Last selected:** remembers a confirmed manual choice for that save.
- **Random:** chooses from eligible owned pets. The optional matching-biome
  preference applies only on planets; if no exact matches exist or habitat is
  unknown, the ordinary eligible pool is used.
- **By habitat:** on planets, selects a nonempty exact, related or acceptable
  habitat group with weights **13:5:1**, then selects within it. Empty groups
  are omitted and weights renormalized. Unlisted habitat combinations are
  excluded. Stations and the Anomaly use the ordinary eligible pool. The full
  directional rules are in [the habitat design](docs/research/HABITAT-SELECTION.md)
  and the Nexus description; these are selection preferences, not official
  creature survival rules.
- **Shuffle:** uses a cycle for Random and each selected By habitat group.
  Only an accepted queue request consumes a turn; a rejected placement retries
  the same pet. The cycle avoids immediate repetition when another eligible
  choice exists, updates with ownership changes and resets on local load/session.
  It does not affect Last selected.

Fresh profiles use **By habitat**, **Shuffle ON**, automation ON, the three
locations ON and Random's biome preference ON. Existing choices are preserved.
Manual dismissal alone does not create another opportunity. Native placement
may defer a request; queue acceptance alone does not prove visible appearance.

## Saves, preferences and removal

Before enabling gameplay hooks, the module verifies a private snapshot while
NMS is already running. This **pre-activation snapshot does not replace the
closed-game backup**. Original save files are not edited or automatically
restored. Preferences, per-save manual favourites, logs and backups stay in
`%LOCALAPPDATA%/NMS-AutoPet`; routine upgrades do not require deleting them.

To uninstall, close NMS and remove only `Binaries/scripts/CompanionAutoSummon.asi`
and, optionally, `GAMEDATA/MODS/CompanionAutoSummon/`. Keep `winmm.dll` if another
mod uses it; remove it only if unused and still identical to the package loader.
Never delete shared game/mod folders. Settings and backups are retained.

## Known issues in 0.10.3-native-test

- Nexus quarantine currently blocks distribution; scan findings are unresolved.
- Teleport has bounded local success. Its exact event meaning and remote-player
  isolation are unverified; no multiplayer-safe claim is made.
- Death/respawn has no separate automatic trigger. Menu recovery after death
  and reliability across every rebuild remain unverified; an earlier missing
  menu report was accompanied by a UI-thread stop, without a recorded death event.
- A historical Anomaly load had no visible pet during an incomplete mission;
  no causal link to mission state is established. Broad location/mod coverage,
  second-PC installation and long-session acceptance remain open.
- Underwater and freighter summoning are not added. Normal game restrictions
  remain authoritative.

See the [canonical Known Issues](docs/KNOWN-ISSUES.md) and
[tester handoff](docs/release/TESTER-HANDOFF.md). Reports should include the exact
mod/game build, trigger/location, settings, whether a manual summon works and
whether a pet visibly appeared. Share only a short sanitized excerpt or
screenshot; do not upload saves, private backups, credentials or entire logs.

## Source, credits and history

[DEVELOPMENT.md](DEVELOPMENT.md), [DESIGN.md](DESIGN.md),
[LOCALIZATION.md](LOCALIZATION.md), [CHANGELOG.md](CHANGELOG.md) and
[ROADMAP.md](ROADMAP.md) retain architecture, evidence and planned work.
Native builds use `native_compatibility.json` and `native_mappings.json`;
root Python manifests and portable-launcher instructions describe retained
legacy implementations. Earlier public package identities and scan results
are preserved in the tester handoff and [archived README](docs/release/README-BEFORE-0103-PUBLICATION.md).

Includes Ultimate ASI Loader 9.7.4 by ThirteenAG, MinHook 1.3.4 by Tsuda Kageyu
and contributors, and JSON for Modern C++ 3.12.0 by Niels Lohmann and contributors,
with required notices. pyMHF/NMS.py by monkeyman192 informed the original runtime
and research. Generative AI was used extensively for code, UI, translations
and documentation. This is an unofficial mod, not a Hello Games product.
