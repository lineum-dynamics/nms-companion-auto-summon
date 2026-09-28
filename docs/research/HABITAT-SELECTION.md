# Habitat selection and companion rotation

Current source **0.5.1-experimental**, combined **0.9.1-play-trial**, retains
menu **0.9.0-selection** and the selection rules introduced in 0.5.0 / 0.9.0.
The follow-up changes only settings confirmation and combined GUI presentation.
Validation passed 403 production and 689 developer tests. The 091-r1 bundle
is built and passed actual-framework checks plus Python and Windows PowerShell
5.1 read-only preflights; 0.9.1 has not launched. The immutable 090-r2 trial launched on
28 September 2026 and has one player-confirmed visible Random startup pet.
Settings appear saved according to the player; restart persistence, By habitat
and shuffle outcomes remain unverified. See [the bounded live record](LIVE-090.md). The retained 0.8.7 trial and its
[bounded live evidence](LIVE-087.md) do not validate these changes.

The retained session later stopped custom menu handling under its
`unexpected_thread` guard. The unchanged menu in 0.9.1 retains that known
limitation; it is not evidence for or against habitat selection. Teleport
arrival and base removal are not new automatic triggers, and a reported pet
disappearance has no established cause. See the live record for the bounded
menu-lifecycle investigation.

## Selection contract

The mode values are `last_manual`, `random` and `by_habitat`. Last selected
continues to use the remembered manual choice. Random retains its optional
exact-biome preference and unrestricted native-eligible fallback when no exact
match exists or the planet biome is unknown. By habitat uses the explicit
directed table below on planets; an unlisted pair is excluded. It does not use
Random's unrestricted fallback or its `prefer_same_biome` toggle.

The selector first draws a nonempty native-eligible group using integer weights
**13 exact / 5 related / 1 acceptable**, then selects a companion within that
group. Group population does not multiply the weight. With all groups present,
the probabilities are approximately 68.4%, 26.3% and 5.3%; with only related and
acceptable groups, they are 5:1. These selected Fibonacci numbers and the table
are mod-design heuristics, not ecological facts, native suitability rules or
validated gameplay balance. Every native ownership, eligibility and placement
check remains authoritative.

On stations and in the Nexus, By habitat uses the ordinary unweighted eligible
owned pool. An unknown planet habitat waits. If a complete known owned roster
contains no approved habitat group, that opportunity is skipped with one
`No suitable companion for this habitat.` notice. A matching owned pet that is
temporarily ineligible instead waits; temporary placement failure does not
produce the unsuitable-habitat notice.

## Directed table

Every recognized category matches itself in the exact group. Cells list
additional companion categories for the planet in that row. Empty cells mean
no additional group members; reverse relationships are not inferred.
`src/selection.py` is the executable table.

| Planet category | Related companion categories | Acceptable companion categories |
|---|---|---|
| 0 Lush | 12 Swamp | 5 Barren, 4 Frozen |
| 1 Toxic | 12 Swamp | 3 Radioactive |
| 2 Scorched | 13 Lava | 5 Barren, 6 Dead |
| 3 Radioactive | — | 1 Toxic, 5 Barren, 6 Dead |
| 4 Frozen | — | 5 Barren, 6 Dead |
| 5 Barren | 6 Dead | 0 Lush, 2 Scorched, 3 Radioactive, 4 Frozen |
| 6 Dead | 5 Barren | 2 Scorched, 3 Radioactive, 4 Frozen |
| 7 Weird | — | — |
| 12 Swamp | 0 Lush, 1 Toxic | 3 Radioactive, 5 Barren |
| 13 Lava | 2 Scorched | 5 Barren, 6 Dead |
| 14 Waterworld | — | — |
| 15 Gas giant | — | — |

Hello Games explicitly introduced waterworlds and gas giants in
[Worlds Part II](https://www.nomanssky.com/worlds-part-ii-update/). The same
release distinguishes non-waterworld planets with deep oceans and non-gas
giant planets: water coverage or size alone must not determine the category.
The selector recognizes both categories and currently permits exact habitat
matches only. This is selection-rule coverage, not live verification of pet
adoption, underwater summoning, native eligibility or placement there.

### Fauna, adoption and summoning evidence

Reviewed on 28 September 2026. A biome enum or a fishing catch is not evidence
of an adoptable companion. Aquatic creatures can occur on other planet types;
their appearance or being underwater does not establish Waterworld habitat.

- **Waterworld adoption has direct player evidence.** In
  [Companion Eggs on Waterworlds](https://steamcommunity.com/app/275850/discussions/0/814724377262342410/),
  dated 14–15 February 2026, the owner describes an adopted helmet crab from a
  Waterworld with native climate **Water-bound**, and reports being unable to
  summon it underwater. The replies disagree about successful placement on
  an Exo-Skiff, so skiff support must not be promised. This is firsthand gameplay
  evidence, not a test of our mod or proof that every aquatic species is adoptable.
- A second [Waterworld discovery report](https://www.reddit.com/r/NoMansSkyTheGame/comments/1t0z9b3/so_i_said_i_would_show_off_my_waterworld_it_is/)
  describes an adopted walking crab that can be summoned elsewhere and used in
  the arena, but not summoned underwater at home. The original author incorrectly
  called the planet a giant; another visitor identifies it as an ordinary
  Waterworld. Do not repeat the giant or five-moons claim.
- **Underwater adoption is distinct from underwater summoning.** The owner of
  this project independently reported adopting a crab underwater on a Frozen
  planet and being unable to summon it underwater. We have not read that pet's
  stored habitat for this observation; do not assign it to Waterworld from the
  report. The mod must continue to use the stored habitat and native placement
  checks, without adding underwater summons.
- **Gas Giant native companions remain unestablished by the reviewed primary
  gameplay evidence.** A [Gas Giant discovery record](https://www.reddit.com/r/NMSCoordinateExchange/comments/1rojggl/eissentam_gas_giant_planet_with_crystallised/)
  dated 8 March 2026 identifies Ilwor in Eissentam and reports no fauna. This
  establishes that example, not a universal no-fauna rule. Adoption reports
  from a gas giant's moons concern separate planets and cannot fill this gap.
- The official [Worlds Part II release](https://www.nomanssky.com/worlds-part-ii-update/)
  describes aquatic fauna and, separately, fishing catches on Waterworlds and
  Gas Giants. Fishing inventory items are not adoptable fauna. Neither the
  enum nor those catches justify inventing a Gas Giant companion pool.

Targeted offline reads of eleven vanilla assets from installed Steam build
25442159 support the Waterworld report. `CREATUREGENERATIONDATA` selects the
Waterworld water archetypes; `CREATUREGENERATIONARCHETYPES` links `WATERWORLD`
to `UNDERWATERTABLEWATERWORLDBASE`, which includes an enabled-probability
`HERMITCRAB` entry on underwater tiles. The corresponding named entity has
Pet/Creature interactions and a one-pellet feeding cost. The scene-to-entity
attachment and dynamic native adoption conditions were not independently
traced. These are creature ecosystem assets, not fishing products; they do
not establish that all Waterworld fauna can be adopted.

The same bounded data check did not establish a Gas Giant no-fauna rule.
Its empty biome-specific generation overrides are inconclusive because
populated ordinary biomes also have empty overrides. Zero sandworm chance
does not describe all fauna, and the standard biome asset's flora field is
not an animal-life field. Extracted copyrighted assets and their private
evidence report remain outside the repository and release packages. No game
launch, process access, save read or game/runtime modification occurred.

The candidate's exact-only rules are unchanged by this research. Waterworld
matching has a concrete use for owned Water-bound companions, but native
placement still decides whether they can appear. Gas Giant recognition does
not claim a normally obtainable native pet: without an owned exact match,
By habitat skips that opportunity with the existing unsuitable-habitat notice.
No unrelated fallback, new spawn restriction or gameplay capability is inferred
from this evidence. Gas Giant fauna-generation evidence remains a separate
research question; native summon support is not established by a lack of fauna.

Weird variants 8, 9 and 10 normalize to category 7. Category 11 and unknown
values do not become Lush or a general fallback. Existing native adoption
normalization maps swamp/lava planet subtypes before comparison. Scorched and
Lava remain distinct categories, linked as related; Frozen↔Lava stays excluded.
Appearance, weather, pet names and the player's description do not determine
stored habitat. A recognizable category does not guarantee an adoptable pet or
a native-eligible summon exists there.

## Rotation and request lifetime

`rotate_companions` affects Random and By habitat, never Last selected. Random
has one session bag; By habitat draws its weighted group first and uses a
separate bag for each normalized planet habitat and group. Neutral locations
use the unweighted Random bag. A one-member eligible pool may repeat. When
another member is currently eligible in the drawn group, a renewed round avoids
that group's last accepted identity. Cancelled reservations do not update it. Rotation
does not force a cross-group cycle that changes the group weights.

Ownership and temporary eligibility are distinct. Reconciliation removes lost
members, preserves surviving unconsumed order, and inserts each genuinely new
member once. Previously consumed surviving members remain consumed. When the
currently eligible remainder is exhausted, that eligible pool renews while
temporarily ineligible unconsumed members retain their history. Slot reorder
between opportunities does not reset cycles; names are not identities.

The runtime copies at most 30 occupied entries, using the verified 16-byte
CreatureSeed + BirthTime token. Duplicate tokens fail closed instead of being
resolved by slot. A selected request freezes its slot and identity. By habitat also freezes
its supported planet/neutral habitat context; Random is location-independent.
Temporary unsupported locations retain the deferred wait. Removal, ambiguous
identity, changed slot or a changed By habitat context while pending cancels the request; it never substitutes the new slot occupant or
silently redraws. The pure selector stores no native pointers.

Only matching native queue acceptance consumes a bag entry. Rejected placement,
retries and cancellation do not consume it. Queue acceptance is not proof that
the companion appeared or rendered; existing passive diagnostics keep that
distinction. There is no retry after an accepted request or automatic respawn
after manual dismissal. Settings changes cancel pending intent without
dismissing an active pet or creating another opportunity.

Bag history is session-only and separate from the manual favourite. Local
load/context boundaries, including loading the same save, reset it. A remote
network load does not reset local history. Disabling rotation does not itself
consume or reset a bag. The mod does not write game saves.

## Settings and interface

Schema 4 stores `rotate_companions` alongside existing preferences. A genuinely
new installation defaults to By habitat and rotation ON. Schema 1 explicitly
retains Last selected; schema 2/3 retains existing Last selected/Random and
biome/location/automation choices. All legacy schemas migrate with rotation
OFF, in memory only until an explicit settings save. A stored OFF remains OFF.

Native roles 0–5 are unchanged; role 6 adds **Shuffle companions**. Selection
cycles Last selected → Random → By habitat. Pending/session-only wording and
the shared production preference queue remain. The seventh icon is included
and verified offline, with all seven preference paths checked through the real
framework against temporary settings; complete live menu validation is pending; no new native mapping or physical
hotkey is introduced. The 46-key catalogs cover new strings in all fourteen
languages, with thirteen unreviewed translations; live text remains English.

## Acceptance boundaries

Offline checks must cover directed groups, exact integer weights, eligibility
renewal, cancellation, duplicate identities, roster edits, schema migration and
the shared preference path. Live checks still need visible results in each
mode, the seventh control/icon, changed eligible pools, pending-slot changes,
save boundaries, native input and multiplayer. None of these are established
by the earlier Random-mode Nexus successes.
