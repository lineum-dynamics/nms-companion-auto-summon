# Companion technology prototype

Status: offline development, 28 September 2026. No technology is installed,
no inventory is granted and no live charge or battery mutation is implemented.
The working production mod remains independent of this prototype.

## Accepted direction

Companion Link is an earned exosuit technology for automatically summoning
already owned companions. It requires a recipe, crafting, a technology slot
and energy. Ion Battery is the working existing fuel. Companion Recharger is a
separately earned dependent technology that consumes batteries automatically;
it does not generate energy. The module names and numerical balance are drafts.
Native manual summoning, ownership, placement and pet attributes stay unchanged.

Charge is owed only after the automatic request is confirmed active, once per
request. Queue acceptance alone is insufficient. Placement failure, cancellation
and following do not incur a charge. Energy gating remains distinct from ON/OFF.
Low/depleted/fuel-empty feedback must explain interrupted automation without
repeating on every exit. A recharge confirmation means ready, not a new summon.

## Offline model

`tools/companion_energy.py` accepts immutable owned snapshots and produces
requested before/after effects. It performs no memory, file, inventory or save
access. Separate confirmation is required for an externally applied charge or
battery transaction. Load epochs, inventory versions and charge cycles are
synthetic inputs, not mapped native fields. Cancellation, context changes and
stale snapshots invalidate pending authority; the model retains bounded state.

Example values are capacity 100, cost 10, low threshold 20, and one battery per
full refill. These illustrate the model and are not approved balance or proof
that the game's charging UI uses these units. There is no new fuel preference:
an installed usable controller supplies the proposed automatic recharge ability.
The four energy event IDs contain no player prose and are not wired to the HUD.

Validation of the frozen candidate passed all 601 developer tests, including
17 energy-model tests, 18 technology-builder tests and 18 catalog tests. The
energy regression includes acceptance followed by rejection: the rejection
revokes the earlier queue latch and cannot authorize a debit. Tests use owned
synthetic data; none injects into or launches the game. The production 0.4.7
generated file remains byte-identical to the previously tested version.

## Native data prototype

The data builder is a separate offline tool. It accepts only the pinned source
table exports for Steam build 25442159 / Cosmos 7.04 and the maintained locale
catalogs, then writes a new directory under repository `build/` or `work/`.
It must refuse overwrite, unknown source tables and invalid catalogs. It never
extracts from a running game, installs files, launches NMS or packages a release.

The intended additions use stable mod-owned IDs `CAS_LINK` and `CAS_RECHARGE`,
not relocated executable addresses. The source technology template is copied
only in the private generated output, stripped of its original stat bonuses
and given the mod's own identity, recipe and icon. A research branch expresses
the base-to-controller progression without marking anything researched.
Existing technology entries and research branches must remain unchanged.

Six catalog strings supply the two names, subtitles and descriptions. Fourteen
catalogs are maintained; thirteen translations remain unreviewed drafts. The
native schema has 17 language fields: USEnglish uses English, LatinAmericanSpanish
uses the Spain Spanish draft and TencentChinese uses Simplified Chinese. These
are explicit fallbacks, not three additional reviewed language versions.
The generated localization table is author-only; registering it with the game's
localization loader is still required before a usable mod package exists.

The actual data build produced 395 technology records (393 retained plus two
new), one additional base-to-controller research branch, six localization
records and the two original icon assets. Private compiler checks passed for
all three generated MXML files: MXML to MBIN to MXML retained all semantic
properties and child ordering (formatting and compiler `_id`/`_index`
annotations were excluded from that comparison). This covers Unicode values
in all 17 fields. The exact MBINCompiler executable SHA-256 was
`82836bfa95051f7282274d087a7972ef28494302f23fa4dd22d0cc43080ebfeb`.

The prototype recipe uses the actual native product ID `CASING`, not a guessed
`METALPLATE`: the Link requires TECH_COMP x2, CASING x1 and POWERCELL x1; the
Recharger requires TECH_COMP x3, MICROCHIP x1 and POWERCELL x1. Both inherit a
provisional 90-fragment NANITES research price. These costs need balancing.

Native XML compilation checks schema acceptance, not installed behavior.
In particular an empty stat list, `RequiredTech`, battery charging, research
availability, UI text, icon rendering and saving all still need live proof.
No final installer should expose an inert module that consumes a slot but does
nothing. Full merged game tables are private intermediate files, never Git or
public release contents; a conflict-aware addition/patch strategy is unfinished.

## Evidence and remaining native work

The actual local tables were extracted using the author's
[HGPAKtool 1.1.3](https://github.com/monkeyman192/HGPAKtool/releases/tag/1.1.3)
and converted using the matched
[MBINCompiler v7.04.0-pre1](https://github.com/monkeyman192/MBINCompiler/releases/tag/v7.04.0-pre1),
which reports compiler 7.04.0.1 in the exported XML. Both downloaded tools were
checked against their release SHA-256 digests before execution. The technology
table contains 393 native entries. `POWERCELL` is an existing product and appears
in the native hazard protection charge list. This establishes valid data
references; it does not establish a custom runtime charging API.

The [exact-build runtime audit](TECHNOLOGY-RUNTIME-AUDIT.md) identifies a
structural inventory read path. It also establishes that the current `Remove`
technology branch erases the element; it must never be reused as charge debit.
Charge update and battery-consumption APIs, their thread/phase and failure
semantics still need exact native caller verification. Do not write apparent
charge fields directly or infer a safe live ABI from serialized XML.

Before a live technology test, finish native registration and a bounded read-only
inventory observer, compare native recharge behavior, and verify transaction
semantics. Use an isolated disposable test save with a verified backup before
any inventory mutation. Test absent/damaged/packaged modules, save switching,
reload, expeditions, removal and mixed multiplayer, including transfer to a
player without the mod. Saved custom IDs may outlive the runtime; auto-disable
alone does not settle their behavior after a game update or mod removal.

## Maintenance and mismatch handling

Keep gameplay policy, authored technology IDs, locale strings and recipes
separate from the exact-build native mapping. Own IDs remain stable across
releases. Executable RVAs, field layouts and table schemas may change and must
be checked before adding a supported build; a successful pattern search is a
candidate match, not sufficient ABI verification.

Unknown or unreadable executable identity must refuse integration before
hook binding or native calls. The supported PowerShell and combined paths check
the exact hash and the Mods have a disabled latch; the finished player flow
still needs a maintained localized outside-game warning, explicit recovery
guidance and a tested direct-launch boundary. Report the detected/expected
build where known, never guess a patch version from an unrecognized hash.
Do not implement an unsafe force-enable button or silently disable every other
mod. Do not make a compatibility warning depend on the unverified native HUD.

Before a future release, test mismatch and hash-read failure with mocked inputs,
verify zero injection/hook activity, and verify that settings and saves stay
untouched. Handle the runtime and custom-data installation separately: retaining
an old saved item, disabling an obsolete table patch and launching without that
data all require evidence, not an automatic cleanup guess.
