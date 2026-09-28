# Companion Auto Summon localization

The **0.10.0-native-test** source has **64 keys in each of fourteen catalogs**.
The new `native.activation_failed` warning explains that NMS may continue with
the mod disabled. Windows-language startup warnings are compiled into the native
module; in-game menu/HUD remain English. Existing draft-review metadata is
preserved. Historical catalog counts below belong to their retained versions.

Packaging **0.9.3-test** retains all **63 keys across fourteen catalogs**.
No UI wording or meaning changes. Windows product/company identity and version
are invariant branding/build metadata. The English/Czech quick starts both
describe the new version and conditional Nexus distribution. Validation passes;
native language rendering and linguistic review remain unverified.

Retained **0.9.2-test** source has **63 keys in each of fourteen catalogs**:
the previous 46 plus seventeen `portable.*` entries for the graphical launcher,
status and failures, including missing Visual C++ runtime and Steam. The English
catalog is canonical; thirteen translations remain unreviewed drafts. The
portable launcher's local Windows-language selection is separate from the
English-only native menu/HUD. The final 0.9.2 developer suite passed 770 tests; package and relocated checks
also passed without a game launch. The later packaged background start registered
both Mods and twelve hooks; it did not exercise the interactive launcher or
verify native text rendering. See [LIVE-092](docs/research/LIVE-092.md).
Nexus readback and language acceptance remain separate in
[TESTER-HANDOFF](docs/release/TESTER-HANDOFF.md).

Menu 0.9.1-diagnostics changes only developer logs and needs no player-text
rewrite. The new launcher labels and messages are updated across all fourteen
catalogs in the same change. `PORTABLE_KEYS` identifies their maintained scope;
the UI must consume catalog values rather than adding untranslated copies.
No native language-rendering or complete linguistic-review claim follows.

## Status

Retained source **0.5.1 / 0.9.1** implemented setting-specific HUD confirmations using
the maintained setting labels and values. All fourteen catalogs replace the
old generic/automation formats with `hud.settings_applied` (`{changes}{suffix}`)
and `hud.setting_separator` (`; `), keeping 46 keys. The separator and wrapper
contain no words and are explicitly declared invariant; actual labels, mode
values and session-only suffixes use each locale's existing draft translations.
A batch reports every effective change once in menu order. No-op changes emit
nothing; saving failure adds one session-only suffix.

The offline `NativeText.settings_notice(changes=..., saved=..., locale=...)`
renderer preserves all changes and falls back to a complete English message
if a translated batch exceeds 511 UTF-8 bytes. The native runtime remains on
its bounded English ASCII path. Source/catalog checks exercise every subset
of settings, all modes, both Boolean directions and persistence outcomes.
This does not establish automatic game-language selection or translated glyphs.

The 090-r2 visible caption is **Shuffle companions** in English; every locale
now names shuffled selection rather than a fixed rotation. The stable
`menu.rotate_companions` key and stored `rotate_companions` preference remain
unchanged. All thirteen translations retain draft status.

`locales/en.json` is canonical English alongside thirteen translated
**unreviewed draft** catalogs. The retained 0.5.1 / 0.9.1 catalog had 46 keys in each:
the original 24 cover the native parent title, six settings labels,
values/statuses, caption formats and current HUD notices; six keys cover the
proposed rechargeable technologies, nine cover launcher compatibility
messages and two cover product identity. Five new keys cover companion rotation,
By habitat, its manual-choice suffix, an unsuitable-habitat notice and one
changed development-panel status. In the 0.4.9 / 0.8.7 branding
candidate, `product.full_name` is the invariant proper name **Companion Auto Summon
for No Man's Sky**; `product.author_credit` translates **by Lineum Dynamics**.
The full title also replaces the short name in `launcher.blocked_title`,
`launcher.unsupported_game` and `launcher.game_running`, with all affected
translations and fingerprints updated. New source labels are **Shuffle companions**
and **By habitat**; **Random: prefer matching biome** keeps its existing
planet-only Random meaning. Native menu/HUD rendering remains English.
The final `090-r2` trial launched on 28 September 2026 with production 0.5.0 and
menu 0.9.0 initialized. This startup adds no native-language rendering or
seven-row menu acceptance; see [LIVE-090](docs/research/LIVE-090.md).
Previously tested 0.8.7-r1 and 0.8.4 and prepared, unlaunched 0.8.6-r1
artifacts remain unchanged.

The catalogs are **not integrated into the game runtime**. Native text still
uses the existing English ASCII path. The current 0.9.0 menu retains observation
of copied game-language scalars for developer diagnostics only. There is no language
selector, automatic catalog choice, verified non-English rendering or native-language
terminology review. English and Czech README files remain documentation
translations. Only the new rotation caption, By habitat enum value and
`panel.habitat_status` are now checked for the development panel; its other text,
other launcher/setup messages and older inert-preview captions remain outside
the current 63-key catalog; this is not
whole-application coverage. At 11:08:53 on 28 September 2026, the bounded observer
reported native region 0 (ENGLISH) with prior initialization/load seen. This is
one live scalar observation, not reload safety or translated-rendering evidence;
see [the retained 0.8.7 record](docs/research/LIVE-087.md).

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
persistence; otherwise it is `Companion selected (session only).` OFF/Random/By
habitat suffixes preserve that distinction. `hud.habitat_on_suffix` says
` Habitat selection stays ON.`; `hud.no_suitable_habitat` says
`No suitable companion for this habitat.` only when the known owned roster has
no approved habitat group. Temporary ineligibility/placement remains quiet.
`panel.habitat_status` reads `Habitat-aware owned companion per request; manual
favorite is preserved.` All five additions have synchronized English fingerprints
and thirteen draft translations. Retained 0.9.1 validation passed
403 production and 689 developer tests. The 091-r1 bundle is built and passed
actual-framework checks plus Python and Windows PowerShell 5.1 read-only
preflights; it has not launched. The new HUD work
passed 19 native-text and 29 catalog tests. No new language rendering or gameplay
acceptance is claimed.

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

Each UTF-8 JSON file declares schema version 1, locale, `native_menu_hud_technology_launcher_panel` scope,
review status and `native_runtime_integrated: false`. Entries contain display
`text` and `source_sha256`: SHA256 of that key's exact canonical English UTF-8
text. English edits invalidate existing fingerprints in every translation.
Updating a fingerprint must follow an actual meaning/translation review, not
serve as a way to hide an unchanged stale translation. A matching fingerprint
proves synchronization only, not translation quality.

`tools/validate_locales.py` requires exactly all fourteen files and all 63 keys,
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
menu combinations, the three newly changed panel surfaces and every current
HUD notice against the catalog. It parses
`src/runtime.py` without importing or running it. Only the extracted pure menu and settings-confirmation functions run, with
restricted calls and owned sample state. The settings check covers every subset
of the seven controls, all mode values, both Boolean directions and successful
or failed persistence; it rejects missing or mislabeled applied changes. Source strings
changed without matching catalog updates fail the check.

The exported `PRODUCT_KEYS` tuple identifies `product.full_name` and
`product.author_credit`. Static checks compare these with the literal
`PRODUCT_NAME` and `PRODUCT_AUTHOR` in `src/runtime.py`. The full proper name is
explicitly allowed to remain unchanged in each translation; the credit phrase
is translated while Lineum Dynamics remains a proper name. These entries do not
mean a native About surface or author credit has been implemented. The in-game
short title remains Companion Auto Summon.

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
legacy inspected files: `src/runtime.py`, `tools/quick_menu_toggle.py`,
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

Offline preparation now exists in `tools/native_text.py`. It consumes one
validated immutable catalog snapshot and renders complete menu/HUD messages
within the current byte limits, with explicit whole-message English fallback
for overflow or unsupported locale IDs. The earlier 2,086 single-message
menu/HUD combinations fit without fallback. The new multi-setting confirmation
path separately checks complete batches; long translated batches may require
the complete English fallback. This is not imported by the native mod or play-trial
bundle. See [the preparation and static evidence](docs/research/NATIVE-LOCALIZATION-AUDIT.md).
The retained 0.8.7 and subsequent menu candidates include a guarded read-only language observer, with stable
double copies, constructor/vtable/range checks, two samples per second and a
bounded transition log. The completed-load flag remains set during a known
reload, so it is not a rendering-readiness lock. The 17 native enum values are
not yet mapped to the 14 catalogs. Static UTF-8 decoding is confirmed in both
measurement and drawing; actual fonts, glyph coverage and layout remain unverified.

- Retain the canonical English catalog with stable English keys and named placeholders.
- Bind the separate UTF-8 locale values to display paths after verifying native encoding. Do not put translated prose into runtime conditionals or use translated labels as persistence values.
- Keep stable stored settings such as `last_manual` and `random` independent of translated display text.
- Provide a language override and English fallback. The observation-only reader does not yet select a catalog; verify live observations, native variant mapping and reload behavior before enabling automatic choice.
- Before game startup, a launcher may use a verified configured choice or a system-language fallback. That is not proof of the game's language.
- Cover all player-facing panel labels, options, status messages, HUD notices, launch/setup errors and recovery instructions. Messages controlled by third-party framework UI need a separate coverage decision; do not claim the entire framework is translated by translating Companion Auto Summon alone.

## Technical work required

The current HUD path uses ASCII encoding. Directly inserting accented or CJK text would fail and disable HUD notifications for that session. Exact-build static analysis now confirms UTF-8 decoding in native measurement and drawing; font coverage and visible acceptance still require a bounded in-game test before replacing the current path. Respect the native buffer size, preserve whole messages and test the actual result in the game.

pyMHF GUI decorators currently capture fixed labels at class definition, and the selection widget displays Enum member names. Updating a dictionary alone will not translate existing controls. Implement and verify an appropriate label/option binding or rebuild mechanism without changing stable selection values.

The 0.9.1 and current 0.9.2 combined candidates suppress this temporary development panel using
`gui.shown = false`; the standalone developer script retains it. Complete
in-game acceptance of the native settings workflow is still required. Prioritize native menu/HUD and launcher
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
