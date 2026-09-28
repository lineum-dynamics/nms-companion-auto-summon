# Nexus presentation assets

`nexus-cover.svg` is the editable, self-contained 1600 × 900 cover draft for
**Companion Auto Summon for No Man's Sky**, with the modest author credit
**by Lineum Dynamics**. A small authentic Lineum Dynamics mark sits beside
that credit. The dark navy/teal background and orbital decoration remain
separate from both marks. There is no gameplay capture, game-company logo,
release badge or claim about unfinished features. The company avatar was
uploaded to the owner-created `LineumDynamics` Nexus profile on 28 September
2026 and checked on the resulting profile. The cover is uploaded as the gallery
thumbnail of [unpublished draft 4579](https://www.nexusmods.com/nomanssky/mods/4579).
`nexus-header.svg` is a 1300 × 372 decorative backdrop, with a clear dark
navy/teal area for Nexus's own title, statistics and controls. A subdued dark
teal companion glyph occupies the far right. It contains no visible text,
company mark or white artwork. Nexus supplies the complete visible title,
game qualifier and author credit. After the owner confirmed removal of the
original text-bearing header, the corrected PNG was uploaded and checked on
the actual mod page. These are draft presentation assets, not a public mod release.

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
The header retains that same companion geometry, recolored to `#173c43`
for a subdued background. The gallery cover's white glyph is unchanged.

## Exports and visual checks

The private preparation outputs include:

- `lineum-dynamics-avatar.png`, 512 × 512, rendered from the authentic brand SVG.
- `nexus-cover.png`, 1600 × 900, and its editable SVG source.
- `nexus-cover-thumbnail.png`, 400 × 225.
- `nexus-header.png`, 1300 × 372, rendered from `nexus-header.svg`.
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
The original text-bearing header was uploaded, but actual page inspection
showed that its lettering competed with Nexus's own title overlay. The corrected
text-free background was visually checked locally. Its maximum red, green and
blue channel values are 23, 60 and 67; no bright artwork remains. Its PNG SHA256
is `55909f9fb86c49ef7cae910a889d948c981fa530b7a63548153c3f5583d560b7`.
The replacement was checked in the saved Media preview and on the actual mod
page at a 1280 × 900 viewport and after restoring the normal viewport. The full
Nexus title and controls remain readable; the page still explicitly reports
that it is not published and has no release file. The initial
upload-dialog error was resolved on a later attempt. Public publication
and real gameplay screenshots remain pending.
