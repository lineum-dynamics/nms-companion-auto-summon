# Native localization preparation

Recorded 28 September 2026 for Steam build 25442159 / Cosmos 7.04 and executable
SHA256 `b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`.
This combines offline authored-text checks, bounded static analysis and the
unlaunched **0.8.6-r1** observation candidate. That candidate retains production
0.4.8 and adds menu **0.8.4-language-observation**. It records native language
state without selecting a catalog or changing rendered text. Live language
observations, glyph coverage and localization acceptance remain unverified.
The running 0.8.4, prepared 0.8.5 and initial 0.8.6 artifacts are unchanged.

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

## Static encoding and drawing evidence

The current Python caption and HUD adapters still explicitly encode ASCII.
Verified native caption storage is 128 bytes including NUL; HUD message storage
is 512 bytes including NUL. The dynamic-string assignment at RVA `0x1CC560`
copies bytes unchanged. The follow-up static audit now establishes actual UTF-8
decoding on the HUD text path, beyond that byte-copy evidence.

HUD TITLE lookup at `0x6C1C99` calls `0x315FB0`, which requires native type 2.
Exact-file RTTI identifies this as `cGcNGuiTextSpecial`, vtable `0x4A36FE0`.
The TITLE call at `0x6C1CBA`, vtable slot `+0x90`, reaches setter `0x1E4CF0`.
Its bounded branch copies a string of at most 512 bytes including NUL into
metadata text storage and marks the element dirty. It is byte storage, not
UTF-16 storage.

Special text processing installs drawing callback `0x205C10` and measurement
callback `0x2DD64B0`. The drawing chain reaches `0x195D5E0`, whose iterator
`0x1956220` decodes UTF-8 at `0x1956270`. Measurement reaches `0x19568D0`, with
the corresponding decoding loop at `0x1956AB0`. Both use the same 364-byte
classification/state table at `0x4A9A4C0`; its SHA256 is
`b364bcfa7d553dcc17f5941eb28078862b133da34a520b7e44cf14e6620955ce`.
Completed codepoints feed glyph-cache lookup and glyph lookup `0x19527D0`.
The ordinary text class installs the same drawing/measurement callbacks, but
this audit did not independently re-prove the exact selected-menu-caption
object wiring.

Offline emulation of the actual table decoded all **546 current catalog text
values** into their original Unicode scalar sequences. Seven additional vectors
covered ASCII, accented Latin, Cyrillic, Chinese, Japanese, Korean and
supplementary scalars. Five malformed or incomplete vectors ended in a nonzero
decoder state. These finite checks verify the observed encoding arithmetic;
they do not execute game code or establish glyph availability. In particular,
supplementary-scalar decoding does not imply an emoji exists in the game font.

## Static native language source

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

The follow-up readiness audit verified the following scalar conditions:

| Field | RVA | Width | Accepted observation value |
|---|---|---|---|
| Initialization guard | `0x6E0154C` | 4 bytes | signed value less than -1 |
| Singleton vtable slot | `0x6E01550` | 8 bytes | image base + `0x350A7C8` |
| Internal region | `0x6E01558` | 4 bytes | 0 through 16 |
| Prior-load completion | `0x6E09DB0` | 1 byte | exactly 1 |

The static object and guard begin in zero-filled storage. Guard zero therefore
does not distinguish English from no initialization. The initialization helper
sets the guard to -1 while constructing; the getter writes region sentinel 17,
clears the load byte and installs the derived vtable. Only afterward does its
footer store the completed negative CRT epoch into the guard. Requiring a signed
value below -1 excludes the inspected uninitialized and constructing states.
Known destruction paths replace the vtable with `0x350A7B0`, which the exact
derived-vtable check rejects. The getter is not called by the observer.

Configuration `0x2BD4870` converts the external language option into the internal
region. Startup then invokes the load-all wrapper `0x2BD6A50`; that wrapper sets
the completion byte to 1 at `0x2BD6BC9` after loading its language tables.
The later setter `0x2BD4230` writes a new region and tail-calls the same loader.
Its verified direct callers at `0x3076F0` and `0x6E9B23` perform additional
UI/resource refresh work after the synchronous load returns.

Crucially, the load-all wrapper does **not** clear the completion byte on entry.
It proves a previous load completed, not that another reload is absent. The
complete refresh lifecycle, concurrency and timing relative to menu callbacks
remain unverified. A stable scalar snapshot is not a reload lock or permission
to switch rendered text.

## Prepared observation-only integration

`tools/game_language.py` reads two copies of the fixed 16-byte record beginning
at the guard and two copies of the separate completion byte: four bounded reads,
34 bytes total. It requires identical copies and all conditions above, follows
no pointers and returns only owned status/enum/name values. Short reads,
unexpected fields and exceptions never become an inferred English selection.
Success is deliberately named `initialized_load_seen`.

The opt-in candidate samples only when an existing AFTER-label callback is about
to supply a Companion Auto Summon caption, at most twice per second. Identical
observations produce no new log entry. It allows eight transition reports, then
one limit marker and stops on the next distinct observation. Construction, read
and report failures are isolated to diagnostics; the menu and preferences remain
active. The adapter rechecks its stopped state after observation before writing
the original English caption. There is no new hook, native function call,
language setter, catalog selection or translated rendering.

Twenty focused language checks cover copied fields, all seventeen enums,
initialization/teardown rejection, unstable snapshots, bounded reads, pacing,
logging limits and failure isolation. The full developer suite passed **675
tests**. The separate 0.8.6-r1 folder passed actual-framework discovery and all
six temporary preference paths without native hook registration or game access.
Its Python and Windows PowerShell 5.1 read-only preflights also passed. These are
offline/preflight results; the candidate has not been launched.

## Next boundary

First observe the guarded native language snapshots in the prepared trial while
retaining English output and the existing post-queue diagnostics. Before a later
UTF-8 rendering trial, define explicit aliases/fallback reporting for native
variants absent from the fourteen catalogs and verify the selected caption path
and language-refresh timing. Test actual fonts, accents, Cyrillic, CJK, longest
captions/scrolling, case transformations, markup and HUD icon/layout behavior.
Catalog completeness and the byte matrix do not establish official terminology
or translation review. Raw executable disassembly remains private and is not
part of the repository or release packages.
