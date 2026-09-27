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
This is a source asset only: it has not been installed into the game, loaded
through its resource manager or included in the player ZIP. The current menu
trials still use the native paw. Native path acceptance, resource readiness,
ownership/lifetime and appearance must pass before integration. Do not replace
a shared vanilla texture as a shortcut.
