# Companion Auto Summon localization

## Status

Companion Auto Summon 0.4.3 has no localization catalog, language selector or automatic game-language detection. Its settings labels, selection options, statuses, HUD messages and launcher errors are hardcoded in English. English and Czech README files are documentation translations, not a localization system.

The load-trigger update reuses the existing control as **Automatically summon companion**, covering ship exits and successful local save loads. Status can show **Waiting for a suitable place** while a load opportunity still awaits ownership. The companion status describes a random choice per request or a remembered identity awaiting ownership verification; the manual-selection notice says **companion selected for automatic summoning**. Future translations must preserve this scope instead of promising a summon immediately during loading or only after a ship exit. No new preference or language selector accompanies the change. The developer menu's **Settings preview** child remains inert and English-only.

In the separate 0.7.0 developer candidate that child becomes **Automatic
summoning: ON/OFF**, with **(pending)**, **(session only)**, **unavailable** or
**stopped** as appropriate. These are English prototype captions, not translated
catalog entries. Pending is a queued request, not a claim that it was saved.
The older 0.6.2 artifact retains its inert preview; the active developer trial
is now 0.7.0, with live preference validation in progress.

The owner requires English source code and player-facing localization covering the game's official interface languages. Translations will be separate data resources. Technical log identifiers and developer diagnostics remain English, while actionable player-facing errors must be localized.

## Target languages

The Steam listing for No Man's Sky identifies these 14 interface languages, checked on 27 September 2026. The locale keys below are proposed Companion Auto Summon catalog keys, not verified internal NMS language IDs.

| Proposed catalog key | Interface language |
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

## Planned design

- Maintain one canonical English catalog with stable English keys and named placeholders.
- Store translated values in separate UTF-8 locale resources. Do not put translated prose into runtime conditionals or use translated labels as persistence values.
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

When adding or changing player-facing text, update the English catalog, all affected translations and the corresponding documentation in the same change. This is the intended workflow; the catalog implementation and translations are still outstanding.
