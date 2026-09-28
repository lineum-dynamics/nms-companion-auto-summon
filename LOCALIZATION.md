# Companion Auto Summon localization

## Status

`locales/en.json` is canonical English alongside thirteen translated
**unreviewed draft** catalogs. Each now has the same 39 keys:
the original 24 cover the native parent title, six settings labels,
values/statuses, caption formats and current HUD notices; six keys cover the
proposed rechargeable technologies and nine cover launcher compatibility
messages. The biome label is **Random: prefer matching
biome**, which only affects Random on planets. This updates source preparation;
the running 0.8.4 artifact remains unchanged. The 0.4.8 diagnostic-only change
changes no player-facing strings or meaning; all 39 keys remain unchanged.

The catalogs are **not integrated into the game runtime**. Native text still
uses the existing English ASCII path. There is no language selector, automatic
game-language detection, verified non-English rendering or native-language
terminology review. English and Czech README files remain documentation
translations. The development panel, other launcher/setup messages and older
inert-preview captions are outside the current 39-key catalog; this is not
whole-application coverage.

The prepared launcher compatibility warnings are the first catalog consumer
in the launch path. Their scope is a blocked-start title, unsupported or
unreadable executable, missing game selection, invalid package, wrong framework,
an executable changed during startup, an already running game and a successful
check-only result. These warnings do not localize every existing launcher
message. Windows UI locale selection and an explicit locale override belong to
the launcher implementation; neither identifies the game's selected language.
The catalogs retain `native_runtime_integrated: false`: native menu/HUD language
binding and glyph support remain unverified. Launcher rendering and recovery
behavior require their own tests, separate from catalog consistency.

The technology entries are names, subtitles and descriptions for the working
names **Companion Link** and **Companion Recharger**. They describe the accepted
design: owned-companion summoning consumes stored charge and respects native
placement; Ion Batteries recharge the Link; the separate Recharger consumes
those batteries from the exosuit and requires an installed Link. These are
offline prototype inputs, not a claim that charging, battery consumption or
technology-gated summoning already works. All thirteen translations remain
drafts, including their native-game terminology.

Pending means queued, not saved. `Companion saved.` is used only after successful
persistence; otherwise it is `Companion selected (session only).` OFF/Random
suffixes preserve that distinction. Automatic summoning and game restoration
remain quiet. Catalog preparation changes none of those runtime rules.

Every change must review localization impact. **Any player-facing text or meaning
change updates English and every affected locale entry in the same change, with
no exception.** Code-only changes need no arbitrary data rewrite. Before changing
an uncovered panel/launcher string, extend catalog and source-check coverage for
that surface. Source code, technical identifiers and developer diagnostics stay
English; translated display values remain separate data.

## Target languages

The Steam listing for No Man's Sky identifies these 14 interface languages, checked on 27 September 2026. These are now Companion Auto Summon catalog filenames/keys, not verified internal NMS language IDs. English is canonical; all thirteen other catalogs are drafts awaiting language review.

| Catalog key | Interface language |
|---|---|
| `en` | English |
| `fr` | French |
| `it` | Italian |
| `de` | German |
| `es-ES` | Spanish — Spain |
| `nl` | Dutch |
| `ja` | Japanese |
| `ko` | Korean |
| `pl` | Polish |
| `pt-PT` | Portuguese — Portugal |
| `pt-BR` | Portuguese — Brazil |
| `ru` | Russian |
| `zh-Hans` | Simplified Chinese |
| `zh-Hant` | Traditional Chinese |

Source: [official Steam store language table](https://store.steampowered.com/app/275850/No_Mans_Sky/). Czech is not on that interface-language list; a Czech README must not be described as official game-language support.

## Catalog and validation contract

Each UTF-8 JSON file declares schema version 1, locale, `native_menu_hud_technology_launcher` scope,
review status and `native_runtime_integrated: false`. Entries contain display
`text` and `source_sha256`: SHA256 of that key's exact canonical English UTF-8
text. English edits invalidate existing fingerprints in every translation.
Updating a fingerprint must follow an actual meaning/translation review, not
serve as a way to hide an unchanged stale translation. A matching fingerprint
proves synchronization only, not translation quality.

`tools/validate_locales.py` requires exactly all fourteen files and all 39 keys,
rejects duplicate JSON keys, invalid/empty/oversized/control-character text and
stale hashes, and compares named placeholder names and multiplicities. Placeholders
are simple text names such as `{label}`, `{value}`, `{status}`, `{state}` and
`{suffix}`; attribute/index access, conversions and format specifications are
rejected. Catalog limits are not native buffer or glyph guarantees.

Non-English entries cannot silently copy English. Only the product name and
explicitly allowed format/brand-only templates may remain identical, and each
such key must appear in that locale's `unchanged_keys`. Other entries contain
authored translations, with honest `draft_unreviewed` status.

The validator also checks the current parent/settings labels, rendered English
menu combinations and every current HUD notice against the catalog. It parses
`src/runtime.py` without importing or running it. Only the extracted pure menu
text function runs, with restricted calls and owned sample state. Source strings
changed without matching catalog updates fail the check.

The exported `TECHNOLOGY_KEYS` tuple identifies `tech.link.name`,
`tech.link.subtitle`, `tech.link.description`, `tech.recharger.name`,
`tech.recharger.subtitle` and `tech.recharger.description`. Technology data
builders must consume these catalog values directly rather than maintain a
second literal copy. Existing menu/HUD source-drift checks remain in place.
No runtime energy-warning strings are introduced by this addition.

The exported `LAUNCHER_KEYS` tuple identifies the nine `launcher.*` entries.
Only `launcher.unsupported_game` takes `{build}` and only
`launcher.wrong_framework` takes `{version}`. They are single-line messages.
The validator parses `cas_compatibility.py` to compare its literal
`WARNING_KEYS` tuple and two-entry `WARNING_FALLBACKS` dictionary with the
catalog. It never imports or executes that helper. The two English recovery
fallbacks cover the blocked-start title and invalid package so damaged or
missing catalogs can still produce an understandable error. These intentional
fallbacks must remain synchronized with canonical English; other warning text
comes from catalog lookup.
The PowerShell launcher's two emergency fallback assignments are also checked
against those same English entries. Literal keys passed to its warning/message
helpers must belong to the nine-key scope. The check reads source text without
executing PowerShell.

Run `python -B tools/validate_locales.py` and
`python -B -m unittest discover -s tools/tests -p test_locales.py`.
The importable API is `validate(locales_dir=None, source_root=None)`: it returns
a bounded report or raises `CatalogError`. CLI alternatives are `--locales-dir`
and `--source-root`. Dependencies are the standard library, catalogs and the
five inspected files: `src/runtime.py`, `tools/quick_menu_toggle.py`,
`tools/quick_menu_item.py`, `cas_compatibility.py` and
`Start-CompanionAutoSummon.ps1`. The check must run before build/package output is
created. It never accesses the game, personal settings or saves.

The focused tests cover stale hashes, exact file/key sets,
placeholders, bounds, unsupported review claims, undeclared English copies,
source drift, absence of runtime imports and explicit-path CLI use, including
technology completeness, launcher placeholders, source-key/fallback drift and
meaning-change synchronization. Passing
them establishes data/source consistency, not linguistic or visual acceptance.

## Future runtime integration

- Retain the canonical English catalog with stable English keys and named placeholders.
- Bind the separate UTF-8 locale values to display paths after verifying native encoding. Do not put translated prose into runtime conditionals or use translated labels as persistence values.
- Keep stable stored settings such as `last_manual` and `random` independent of translated display text.
- Provide a language override and English fallback. An automatic game-language choice must use a verified read-only source; no such reader is currently implemented.
- Before game startup, a launcher may use a verified configured choice or a system-language fallback. That is not proof of the game's language.
- Cover all player-facing panel labels, options, status messages, HUD notices, launch/setup errors and recovery instructions. Messages controlled by third-party framework UI need a separate coverage decision; do not claim the entire framework is translated by translating Companion Auto Summon alone.

## Technical work required

The current HUD path uses ASCII encoding. Directly inserting accented or CJK text would fail and disable HUD notifications for that session. Determine the game's accepted text encoding and rendering behavior before replacing that path. Respect the native buffer size, do not cut a multibyte character in half, and test the actual result in the game.

pyMHF GUI decorators currently capture fixed labels at class definition, and the selection widget displays Enum member names. Updating a dictionary alone will not translate existing controls. Implement and verify an appropriate label/option binding or rebuild mechanism without changing stable selection values.

The accepted final interface retires this temporary development panel once
the native settings page is complete. Prioritize native menu/HUD and launcher
translations for the player release; do not build a second permanent settings
interface merely to translate pyMHF's development window. Verify that the
finished player package does not require that window during normal play.

The current panel has no Companion Auto Summon font/glyph configuration for the entire target language set. Verify accent, Cyrillic, Japanese, Korean and both Chinese character coverage, font licensing and readable layouts. English-only GUI smoke tests do not establish this coverage.

## Completion criteria

- Every required key exists in every supported catalog, with no duplicate keys or empty unintended values.
- Placeholder names/types match English; invalid catalog data uses a safe English fallback.
- Automated checks cover key completeness, formatting and preference independence from display language.
- Visual checks cover long text, diacritics, Cyrillic and CJK glyphs in both the launcher/panel and native HUD.
- Confirmed terminology follows the corresponding game UI where it can be verified. Translate meaning and actions accurately rather than merely copying English word order.
- Record translation review status separately from technical key coverage. Generated translations without language review are drafts, not confirmed-correct translations.
- Record unsupported or unreviewed cases on the release page instead of claiming complete verified localization.

When adding or changing player-facing text, update the English catalog, all
affected translations and the corresponding documentation in the same change.
The scoped catalogs and consistency checks now exist; runtime binding, broader
surface coverage, language review and in-game verification remain outstanding.
