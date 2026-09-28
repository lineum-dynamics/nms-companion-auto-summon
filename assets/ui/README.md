# Original quick-menu icon candidates

## Current status

The source set now adds a distinct **Rotate companions** icon to the existing
parent and six setting icons. The running **0.8.7-r1** package remains immutable
and does not contain this addition. Earlier 0.8.4 screenshots confirmed the six
setting icons; the new rotation icon has only offline validation. Resource
registration alone does not confirm visible icons or a visible companion.

All eight textures use the unique virtual directory
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
| Rotate companions (6) | `ROTATE.DDS` |

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
also visually inspected. `tools/build_settings_icons.cjs` renders the seven
editable setting SVGs to PNG/DDS and `settings-icons-preview-rotate.png`. The earlier
six-setting preview and all original image bytes remain unchanged. All DDS
files use the same reviewed dimensions and format. Offline rendering is not
evidence of their native appearance.

`rotate.svg` uses two crossing arrows, deliberately distinct from the selection
paw and the parent's circular arrow. It has no visible text or background;
native selection tint and effects remain the game's responsibility. Its
256 x 256 `ROTATE.DDS` uses the same one-mip RGBA32 format and SHA256
`429cf9baa614271c479a7e64c28648152b4a873b8dd07cd0e5640eb147ccc5cf`.

## Closed-game staging and ownership

The source staging helper validates all eight DDS files' exact hashes, legacy
headers and existing destinations before staging under
`GAMEDATA/MODS/CompanionAutoSummon/TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/`.
NMS must be verified closed throughout staging. Exact existing bytes are reused;
unexpected files and redirected paths are refused. Publication is atomic per
file, not an eight-file transaction: a later refusal leaves previously verified
files intact. Packaging itself does not deploy. The running package and installed
assets remain unchanged; the standalone production ZIP excludes these assets.

The exact-build menu resource callback makes one phase attempt, loading each
texture at most once. Each has its own aligned native record and path buffer,
all process-pinned before resource calls. One verified native paw is retained
for fallback. Fresh bounded checks select the requested role's ready custom
handle, then that paw; the HUD uses only the parent role and stays text-only
when neither is usable. A partial failure stops remaining loads without retry;
an observed manager transition or recycled resource disables the provider.
No vanilla resource field or shared texture is replaced, and there is no late
load, retry or release path. The eight-icon extension has no live validation of
the new texture's mounting, decoding, resource lifetime or small-size appearance.
Offline pixel equality and source tests do not establish those live results.
