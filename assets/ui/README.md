# Original quick-menu icon candidate

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
also visually inspected. Smaller in-game rendering remains unverified.

The candidate virtual texture path is
`TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/SETTINGS.DDS`.
The prepared combined **0.8.0** trial includes this DDS and stages it at
`GAMEDATA/MODS/CompanionAutoSummon/TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/SETTINGS.DDS`
only before a future launch with NMS verified closed. Exact existing bytes are
reused; unexpected files and redirected paths are refused. Packaging does not
deploy. The running 0.7.1 and unlaunched 0.7.2 artifacts remain unchanged, and
the standalone production ZIP still excludes this asset.

The exact-build menu resource callback attempts one load of the original DDS.
Its owner is process-pinned before resource calls and retains a verified native
paw for fallback. Fresh bounded resource checks prefer the ready custom handle,
then the retained paw; HUD notices remain text-only when neither is usable.
No vanilla resource field or shared texture is replaced, and there is no late
load, retry or release path. Native mounting/decoding, resource lifetime and
small-size appearance have not been verified in-game. Offline pixel equality
and source tests do not establish any of those live results.
