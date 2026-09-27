# Original quick-menu icon candidates

## Current status

The live **0.8.2-play-trial** folder is immutable: production **0.4.7** and
menu **0.8.0-settings-trial** still use the original single `SETTINGS.DDS`.
The prepared **0.8.3-play-trial / 0.8.3-settings-trial** has not launched and
keeps production 0.4.7 unchanged. It adds six distinct settings icons. A
registered resource or native active-state log does not confirm visible icons
or a visible companion; appearance and small-size readability need a player check.

All seven textures use the unique virtual directory
`TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/`:

| Role | Texture |
|---|---|
| Parent (-1) | `SETTINGS.DDS` |
| Automatic summoning (0) | `AUTOMATION.DDS` |
| Selection (1) | `SELECTION.DDS` |
| Random biome preference (2) | `BIOME.DDS` |
| Planets (3) | `PLANET.DDS` |
| Space stations (4) | `STATION.DDS` |
| Space Anomaly (5) | `ANOMALY.DDS` |

## Artwork and asset generation

`companion-auto-summon-icon-v1.svg` is original vector artwork: a white paw
surrounded by a clockwise arrow. It follows the accepted paw/automatic-return
concept without copying the native game texture or tracing the opaque concept
preview. The source has a transparent background and contains no text or glow;
the intended game presentation should supply selection tint and effects.

`tools/build_icon_asset.cjs` renders the SVG using `sharp`, writes a 256 x 256
RGBA PNG and an uncompressed legacy RGBA32 `SETTINGS.DDS` with one mip level,
and verifies both writes. Run with Node.js and `sharp` available. Independent
Pillow decoding confirmed pixel equality between PNG and DDS, including
transparent background, opaque white fill and antialiased edges. The PNG was
also visually inspected. `tools/build_settings_icons.cjs` generates the six
additional original SVG/PNG/DDS assets and a contact-sheet preview. All DDS
files use the same reviewed dimensions and format. Offline rendering is not
evidence of their native appearance.

## Closed-game staging and ownership

The prepared 0.8.3 combined bundle includes all seven DDS files. Its launcher
validates the complete set's exact hashes, legacy headers and existing
destinations before staging under
`GAMEDATA/MODS/CompanionAutoSummon/TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/`.
NMS must be verified closed throughout staging. Exact existing bytes are reused;
unexpected files and redirected paths are refused. Publication is atomic per
file, not a seven-file transaction: a later refusal leaves previously verified
files intact. Packaging itself does not deploy. The live 0.8.2 folder and its
asset remain unchanged; the standalone production ZIP excludes these assets.

The exact-build menu resource callback makes one phase attempt, loading each
texture at most once. Each has its own aligned native record and path buffer,
all process-pinned before resource calls. One verified native paw is retained
for fallback. Fresh bounded checks select the requested role's ready custom
handle, then that paw; the HUD uses only the parent role and stays text-only
when neither is usable. A partial failure stops remaining loads without retry;
an observed manager transition or recycled resource disables the provider.
No vanilla resource field or shared texture is replaced, and there is no late
load, retry or release path. The seven-icon candidate has no live validation of
mounting/decoding, resource lifetime or small-size appearance. Offline pixel
equality and source tests do not establish any of those live results.
