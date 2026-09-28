# Habitat selection and companion rotation

Source candidate **0.5.0-experimental**, combined **0.9.0-play-trial**, menu
**0.9.0-selection**. Implemented in source; offline validation passed 396 production and 683 developer tests. This candidate has not been launched. The retained running 0.8.7
trial and its [bounded live evidence](LIVE-087.md) do not validate these changes.

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

Native roles 0–5 are unchanged; role 6 adds **Rotate companions**. Selection
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
