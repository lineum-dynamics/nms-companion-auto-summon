# Nexus presentation assets

`nexus-cover.svg` is the editable, self-contained 1600 × 900 cover draft for
**Companion Auto Summon for No Man's Sky**, with the modest author credit
**by Lineum Dynamics**. A small authentic Lineum Dynamics mark sits beside
that credit. The dark navy/teal background and orbital decoration remain
separate from both marks. There is no gameplay capture, game-company logo,
release badge or claim about unfinished features. The company avatar was
uploaded to the owner-created `LineumDynamics` Nexus profile on 28 September
2026 and checked on the resulting profile. The mod cover remains a local draft;
no mod page or cover has been uploaded.

## Brand provenance and permission

`lineum-dynamics-icon.svg` is copied from the owner-designated source project
`lineum-dynamics`, at `portal/static/icon-infinity.svg`, on 28 September 2026.
Only the two Czech comments were translated into English and whitespace/line endings
normalized. Geometry, colors, opacity, rounded background, stroke widths and
the infinity loop's dash gap are unchanged. The cover embeds those same SVG
elements as a symbol, positioned and uniformly scaled beside the byline.

- Original source SHA256: `e4502cad0e095be18cc87e843312835ab3d326c2ad5d1817b6690d29d17487c5`.
- Comment-translated copy SHA256: `37b559c2f8c5d5d0292ea8fe171e742cd31fd92fcc8f08a1533e4d64d558da7a`.

The Lineum Dynamics mark is **proprietary**, not openly licensed. The owner
authorized reuse for its Nexus account/profile and this mod's unpublished
presentation. This inclusion grants no general right to reuse, modify,
redistribute or sublicense the mark, and does not place it under a software
license elsewhere in the repository. Other uses require the owner's permission.

## Companion glyph

The white paw and clockwise arrow remain reused from
[`../ui/companion-auto-summon-icon-v1.svg`](../ui/companion-auto-summon-icon-v1.svg).
The existing cover symbol's geometry, fill and stroke attributes are unchanged;
only the separate author credit gained the brand mark. Its retained symbol
SHA256 is `c99465ef962269ad3256c55ea558d559d51c96f0894e721f700e3bec85ed2328`.
The runtime icon and game-asset staging pipeline are unaffected.

## Exports and visual checks

The private preparation outputs include:

- `lineum-dynamics-avatar.png`, 512 × 512, rendered from the authentic brand SVG.
- `nexus-cover.png`, 1600 × 900, and its editable SVG source.
- `nexus-cover-thumbnail.png`, 400 × 225.
- `brand-export-manifest.json`, with source/output hashes and renderer versions.

The retained offline export script validates the source hash, compares the brand
elements after removing comments/whitespace, and checks the unchanged companion
symbol before rendering. It uses Node 24.16.0, Sharp 0.35.4 and libvips 8.18.6,
with explicit dimensions and PNG settings; no network, browser or game operation
is involved. Results are reproducible with the same renderer and installed fonts.
The title remains editable text with Segoe UI and Inter/Arial/sans-serif fallbacks;
fonts are neither embedded nor downloaded.

All three PNGs were visually inspected on 28 September 2026. The avatar preserves
the infinity gap and cyan/white details. The cover and thumbnail have readable
titles, intact glyphs and no clipping or overlap; the author mark stays modest.
The actual Nexus avatar crop and saved profile image were visually checked.
Mod-page image presentation remains unverified because Nexus's mod-upload
dialog returned an error with `Upload mod` disabled. Local cover export and
inspection do not imply a page upload or mod publication.
