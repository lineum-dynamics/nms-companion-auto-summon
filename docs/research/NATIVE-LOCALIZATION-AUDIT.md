# Native localization preparation

Recorded 28 September 2026 for Steam build 25442159 / Cosmos 7.04 and executable
SHA256 `b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`.
This combines offline authored-text checks with bounded static analysis. It does
not establish native language detection, rendered glyphs or live acceptance.
The running 0.8.4 and prepared 0.8.5 artifacts are unchanged.

## Implemented offline preparation

`tools/native_text.py` prepares an owned immutable text snapshot using the same
catalog/source validator as the build. `validated_catalogs()` returns the data
it actually checked, so preparation need not reopen files after validation.
Missing, malformed or stale catalogs reject preparation before any text is used.
No file is written. No native module, game process or player setting is accessed.

The renderer accepts an explicit catalog ID, copied menu state and stable
preference keys. It covers the parent title, all six settings and existing HUD
settings/manual-selection notices. It preserves pending over session-only
precedence, stopped/unavailable states and the saved/session-only/OFF/Random
distinctions. English output matches the current menu and cataloged HUD meaning.
It does not decide when to show a notice or alter a preference.

Rendering uses no I/O. Complete UTF-8 payloads reserve one byte for the adapter's
terminator: menu 127 bytes, HUD 511 bytes. Oversized translated output falls back
to the complete English message with an explicit `byte_limit` reason. It never
cuts off a state suffix or a multibyte character. Invalid Unicode/control text
is rejected; an oversized English message is also rejected. Unknown locale IDs
select English with `unsupported_locale`; no OS or native enum is guessed.

Fifteen focused tests cover state parity, all catalogs, Unicode byte boundaries,
whole-message fallback, invalid state/placeholders, stale/missing catalogs and
owned snapshots. The current matrix is **103 menu cases and 16 HUD cases per
language**, **1,666 total**. All fourteen current catalogs fit without fallback.
Russian is the largest: 123/127 menu bytes and 118/511 HUD bytes. Byte length
does not measure screen width, font coverage or translation accuracy.

The renderer is a repository preparation tool, not imported by the production
mod, included in a play trial or connected to a native callback. No player-facing
wording or meaning changed; all 39 entries in all fourteen catalogs are unchanged.
Thirteen translations remain unreviewed drafts.

## Static native evidence

The current Python caption and HUD adapters explicitly encode ASCII. Replacing
that encoding without proving the downstream contract is not sufficient.
Verified native caption storage is 128 bytes including NUL; HUD message storage
is 512 bytes including NUL. The dynamic-string assignment at RVA `0x1CC560`
copies bytes unchanged. HUD TITLE reaches a virtual text-setting call at
`0x6C1CBA`, vtable slot `+0x90`; its decoder and font path remain unmapped.
Byte copying alone does not prove UTF-8 rendering.

The matching `NMS.py` language-manager signatures were checked against this exact
executable, using commit `b41bf9e6fdff1c833b77d805bb0c8da555c4ced4`:
[manager declaration](https://github.com/monkeyman192/NMS.py/blob/b41bf9e6fdff1c833b77d805bb0c8da555c4ced4/nmspy/data/types.py#L3738)
and [native enum](https://github.com/monkeyman192/NMS.py/blob/b41bf9e6fdff1c833b77d805bb0c8da555c4ced4/nmspy/data/enums/internal_enums.py#L62).
The inspected source files had no local changes. The unique getter at RVA
`0x1CB3B0` returns static object `0x6E01550`.
Its language/region field is `+8`, RVA `0x6E01558`. The loader at `0x2BD08D0`
reads that field and uses the table at `0x2BD0AC8` to choose a
`LANGUAGE\\%s_%s.MBIN` resource. The seventeen table values are:

| Value | Native resource language |
|---|---|
| 0 | ENGLISH |
| 1 | USENGLISH |
| 2 | FRENCH |
| 3 | ITALIAN |
| 4 | GERMAN |
| 5 | SPANISH |
| 6 | RUSSIAN |
| 7 | POLISH |
| 8 | DUTCH |
| 9 | PORTUGUESE |
| 10 | LATINAMERICANSPANISH |
| 11 | BRAZILIANPORTUGUESE |
| 12 | JAPANESE |
| 13 | TRADITIONALCHINESE |
| 14 | SIMPLIFIEDCHINESE |
| 15 | TENCENTCHINESE |
| 16 | KOREAN |

The getter's initialization writes invalid sentinel **17**. Before that point,
zero-filled storage could look like English. A valid-looking number alone is
therefore insufficient readiness evidence. The later setter, readiness and
language-switch/reload lifecycle have not been verified. No live read, getter
call or automatic language selector was introduced.

## Next boundary

Verify readiness and stable read timing before adding an exact-build reader.
Do not call an initializing getter merely to inspect language. Define explicit
catalog aliases/fallback reporting for native variants absent from the fourteen
catalogs. Independently trace the decoder and then test rendering of accents,
Cyrillic, CJK, longest captions and HUD icons in a separate closed-game-started
trial. Keep existing English output until those adapter requirements are met.
Catalog completeness and the byte matrix do not establish official terminology.
