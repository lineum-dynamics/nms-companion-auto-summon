# Companion Auto Summon roadmap

This is the canonical backlog for unfinished release work and future ideas. It is not a feature list for the current package or a promise of release dates. Status updated on 28 September 2026: **Companion Auto Summon for No Man's Sky — by Lineum Dynamics**, running **0.8.7-play-trial**, contains production **0.4.9-experimental** and menu **0.8.5-branding**. It passed 333 production and 675 developer tests without failures or skips. The `build/quick-menu-play-trial-087-r1` folder has 41 files (40 payloads and its manifest) and passed real-framework offline checks, all six temporary preference paths and both Python and Windows PowerShell 5.1 read-only preflights. After normal closure and a verified 46-file backup, both Mods and twelve targets registered at 11:07:26 (Europe/Prague). The player confirmed visible Random pets after Nexus load and ship exit, then reported no apparent reappearance after a requested manual dismissal; the waiting duration was not independently measured. Initial post-start hashes matched the 40 payloads and existing settings/state. Retained **0.8.4** and prepared, unlaunched **0.8.6-r1** remain unchanged. Different pets and the unexplained earlier startup failure prevent a causal fix claim. Gameplay and full interface acceptance remain incomplete. See [LIVE-087](docs/research/LIVE-087.md). Unaccepted proposals below remain unapproved for implementation.

Use [DESIGN.md](DESIGN.md) for accepted product behavior, [LOCALIZATION.md](LOCALIZATION.md) for language requirements and [the release plan](docs/release/RELEASE-PREPARATION.md) for publication checks. Update this backlog when a proposal is accepted, deferred, rejected or implemented. Record the version and verification evidence when a task is completed.

## Accepted unfinished release work

These requirements were accepted before this backlog was created. Finish them before adding optional features that would complicate the first release.

Independent offline preparation now covers complete localized menu/HUD text
and a console-free host import. The new combined trial adds bounded read-only
language observation without choosing a catalog or changing display text. See
[native text](docs/research/NATIVE-LOCALIZATION-AUDIT.md) and
[portable runtime](docs/research/PORTABLE-RUNTIME-AUDIT.md). Neither preparation
establishes game-language readiness, rendered translations or an installer.

The intermittent Nexus startup failure remains unresolved. Running
production 0.4.9 retains passive diagnostics after the first logical active
index, within the existing 15-second / 4096-callback observation limits. It adds
no retry, placement override or summon timing change and is not a spawn fix.
The two [current successful summons](docs/research/LIVE-087.md) involved different
Random pets and do not reproduce the [0.8.4 failure](docs/research/LIVE-084.md).
Use the remaining checks in the
[next combined test](docs/release/RELEASE-PREPARATION.md#next-combined-test-087).
Keep the current game and host intact; routine controls and appearance checks
can continue in this session. New deployment requires normal closure and a
fresh backup as appropriate.

The candidate retains matched manual-selection attribution, 5.5-second notices,
six native controls and seven original role assets. Screenshots confirm the six
setting icons in 0.8.4. In 0.8.7 the player confirmed one native OFF/ON sequence:
OFF prevented a ship-exit summon, ON alone did not summon, and the next exit
summoned a pet, with other preferences unchanged. The other five controls,
held/remapped input and controllers remain pending. Parent/HUD appearance
and resource teardown still need acceptance. The label **Random: prefer matching biome** describes the
existing planet-only Random preference. Native captions and HUD wording remain
unchanged. The branding update adds the full product name and author-credit
keys and expands the product name in three launcher compatibility messages.

The guarded host, actual target-handle check before injection, read-only
preflight and separate setup/host leases remain in place. Nine compatibility
messages use fourteen catalogs (41 keys each; thirteen draft translations).
These checks do not complete the portable installer, full launcher/native
localization or saved-technology safety. Retained older artifacts stay unchanged.

Historical 0.4.4 / 0.7.1 added bounded passive post-queue observation; one Anomaly startup has player and native-active
confirmation, with no automatic retry. Repeatability remains unverified. Validate it against the failed Anomaly case before
deciding on a behavioral fix. That result followed a fresh backup and does not establish repeatability in newer candidates.

Historical 0.7.0 live findings: basic ON/OFF application has partial player and log
confirmation. Anomaly startup accepted a queue without a visible pet, and the
HUD shows an unwanted white disc. The 0.4.4 diagnostic now observes the
accepted queue's lifecycle without retrying or changing summon timing. Any
future retry must distinguish failed materialization from manual dismissal.
Icon suppression now has static evidence but still needs visual acceptance. Held confirmation,
remapping and controllers remain untested; rapid toggles were repeated presses.

| Work | Current boundary | Completion evidence |
|---|---|---|
| Simple, reliable installation | Current 0.8.7 retains the guarded direct host, shared compatibility profile, nine localized compatibility messages, read-only preflight and setup/host leases from 0.8.4. Current preflights and the subsequent 087-r1 launch have bounded evidence; initial payload and player-state hashes matched. Normal setup still requires external Python and prepares dependencies. A portable offline runtime and finished graphical launcher are not implemented. | Retain the offline mismatch/no-write/lease tests, then verify extract-and-launch on a clean second Windows account/PC, relocated/non-ASCII paths, no external Python dependency and no unexpected game termination. Follow [installer requirements](docs/release/INSTALLATION-REQUIREMENTS.md). |
| Native quick-menu settings | Running 0.8.7 retains six settings and the explicit Random biome label. Menu 0.8.5-branding recorded one native English observation without translated rendering. Six setting icons are visible in retained 0.8.4 screenshots. All seven DDS files are validated before staging; each role has native-paw fallback. Complete controls, parent/HUD rendering and resource lifetime remain unverified. Keep automatic summoning and the desktop panel during acceptance. See [QUICK-MENU.md](QUICK-MENU.md). | All six controls apply/persist without changing unrelated values; native navigation/rebuilds and ordinary pet actions; default/remapped keyboard and controllers; seven correct icons, retained fallback and text-only behavior; no changed gameplay limits or shared vanilla textures. |
| Native number shortcuts | Requested next work; blocked by tagged None serialization losing the marker and potentially replacing a prior binding with an empty action. The existing native binding guard remains required. No custom shortcut or physical hotkey is implemented. | Verify native binding, replay, removal and persistence without losing existing shortcuts; prove remapped native-input behavior and controller handling before enabling it. Do not substitute physical key hooks or a second hotkey system. |
| Localization and natural feedback | Fourteen catalogs contain 41 keys; thirteen translations are drafts. Nine launcher compatibility messages use catalog lookup; two product keys cover the full name and author credit. Offline native text preparation passes 1,666 language/state combinations within byte limits; it is not connected to native rendering. Candidate 0.8.7 observes copied language scalars only. UTF-8 measurement/drawing decoders are statically verified; reload safety, language selection and live glyph rendering remain unverified. Native menu/HUD remain English. | Reviewed catalogs for all 14 official interface languages, complete launcher coverage, verified language selection, placeholders and in-game rendering. Quiet ordinary summons, honest save/session-only messages; evaluate the combined activation/donation-information proposal separately under the published-rule boundary below. |
| Live behavior and compatibility | Running 0.4.9 / 0.8.7 has player-confirmed visible Nexus summons after load and ship exit, with different Random pets. The player then reported no apparent return after requested manual dismissal; exact waiting time was not independently measured. These bounded observations do not explain the failed 0.8.4 startup or establish repeatability. | Control companion choice before attributing a load/exit difference. Broaden repeatability and dismissal regression; test planet and Last manually selected startup, preferences, biome preference/fallback, location controls, restart/save switching, obstructed placement then suitable terrain, cancellation and unsupported locations. Record visible appearance separately from queue acceptance or logical activity. |
| Multiplayer and release preparation | Second-PC installation and multiplayer remain unverified; Nexus material is still a draft. | Controlled tests with one and then, where available, two mod users; no duplicate or foreign-pet changes; accurate support limits; owner-approved attribution/reuse terms and distribution contents; current platform/publisher policy review. |

Keep the current native ownership, eligibility and placement rules. No roadmap item authorizes pet creation/unlocking, reduced gameplay limits, accelerated progression or writing NMS save files. The same exact-build guard remains required.

## New proposals, in suggested order

### Selection modes and weighted habitat choice

**Status: weighted principle accepted for further design; not implemented.**
Discuss three modes: Last selected, Random and By habitat. The habitat mode
would favour a matching environment without requiring the highest matching
group on every draw. At the owner's request, use Fibonacci numbers as the basis
for the proposed balance: **13 exact / 5 related / 1 acceptable**, approximately
**68.4% / 26.3% / 5.3%** when all three groups contain eligible pets. These are
selected, nonconsecutive Fibonacci numbers. They express a strong preference
for matching habitats with some variety; the sequence itself is not evidence
of ecological suitability or better gameplay.

First choose a nonempty group using the integer weights, renormalizing when
other groups are empty, then choose among its native-eligible pets (uniformly
unless Rotate companions is enabled). For example, without an exact match,
the related/acceptable probabilities become **5:1**, about **83.3% / 16.7%**.
Group population must not change the group weight. The specific ratio and
compatibility table remain proposals to evaluate, not validated balance.

Explicitly unsuitable pairs stay excluded; Frozen versus Lava is an example.
Do not fall back without restriction to every owned pet. Scorched and Lava are
distinct native categories; they are the proposed first related pair, not an
existing merge or a verified universal suitability rule. If no approved group
contains an eligible pet, the proposed mode would skip the automatic summon.
Nonplanet behavior and the complete related/acceptable table still need design.

By habitat is the recommended future default **for new installations only**,
subject to approval of the complete feature; preserve existing preferences.
The current default remains Last manually selected. Current Random still has
an optional exact-biome preference and falls back to its full native-eligible
pool when the habitat is unknown or no exact match exists. No mode, setting,
catalog text or player data changes as part of this proposal.

### 1. Choose which companions Random may use

**Status: proposed; not implemented.** Allow an optional inclusion list or exclusions among the player's owned companions. This would let a player keep a large or unwanted companion out of routine automatic selection without abandoning it. Default remains all eligible owned companions; the last-manual mode remains unchanged.

Treat inclusion and exclusion as two possible interfaces for one filter, not two independent settings systems. Use stable companion identity instead of slot numbers so rearranging slots does not silently select another pet. Build the pool from native-eligible owned companions, apply the player's filter and then apply the existing biome preference within that filtered pool. If the filtered pool is empty, do not summon and provide an unobtrusive status; never silently reintroduce an excluded companion. A draw stays fixed through deferred placement retries.

### 2. Rotate companions across automatic opportunities

**Status: proposed; not implemented.** This develops the earlier immediate-repeat
avoidance idea into one optional shared control, provisionally named **Rotate
companions**. Random would use a shuffled cycle of its currently eligible pets.
By habitat would first make its weighted group draw, then use a separate
shuffled cycle within that group. Do not force a cycle across groups that
changes their intended probabilities. A group with one pet may repeat; Last
selected remains unaffected.

Recommending this control ON for new installations is still a proposal; existing
preferences must survive. Selection occurs only for the next normal load or
ship-exit opportunity. It never dismisses or replaces an active pet, redraws
during blocked placement or creates a replacement request after cancellation.
Define eligibility changes, cycle resets and which confirmed event advances a
cycle before implementation. Keep cycle history separate from the manual
favourite, and distinguish visible appearance from queue acceptance in tests.

Roster changes must reconcile the cycle rather than reset it. The proposed
rules are:

- Use a verified, stable companion identity; mutable slot indices and display
  names are not identities. Reordering or renaming must not restart a cycle.
- Remove no-longer-owned members while preserving the order of surviving
  unselected members. Insert each genuinely new owned member once at a random
  position in the remaining cycle; keep previously selected members marked.
- Track temporary native ineligibility separately from ownership changes so a
  pet becoming eligible again is not repeatedly treated as a new adoption.
- Recheck ownership, identity-to-slot resolution and native eligibility before
  submitting the chosen pet. If it was removed or its identity cannot be
  resolved safely while placement is deferred, cancel the request; do not
  summon a replacement occupant of its former slot or silently redraw.
- Keep each habitat context's mutually exclusive group membership separate.
  Reconcile membership for the next normal opportunity without rerolling an
  existing deferred request. Cycle membership must not alter group weights.

Reliable identity across roster edits, duplicate-looking companions and save
changes is an implementation prerequisite, not a verified current capability.
Test adoption, abandonment, reorder, rename, eligibility changes and removal of
the deferred candidate before enabling this feature. The exact cycle-advance
event and persistence/reset boundaries remain to be specified.

### 3. A small diagnostic report the player can review and share

**Status: proposed; not implemented.** Add an explicit launcher action that produces a local, readable support report. Include the mod version and verified build/commit identifier when available, game/framework versions, supported-build result and stable error categories. The purpose is to make compatibility reports useful without asking players to collect raw logs.

Use an allowlist of fields. Exclude account identifiers, save IDs, pet seeds, personal paths, credentials, raw exception text and memory contents. Show the exact report before export, provide a local file and let the player choose whether to share it. No automatic upload, telemetry or background network request. Test redaction with synthetic personal data, including unusual paths and error messages. Never label a dirty checkout as the exact clean commit without accounting for its state.

### 4. Optional preferences per save

**Status: proposed; not implemented.** A player might want Random during ordinary exploration and a different setting for another save. Current preferences are global for the Windows user; only the manual companion choice is already stored per save. This proposal would add an optional override profile, not duplicate that existing manual-selection persistence.

Default remains the global profile. Use the existing stable save identity and external mod storage; never edit game saves. Missing save identity should use the global profile without guessing or creating a persistent entry. An unreadable override must preserve the file and retain the existing fail-closed behavior rather than silently enabling automation. Switching a profile must cancel pending intent through the established game-thread path without dismissing an active companion. Define migration, explicit reset and the shared main-game/expedition identity behavior before implementation.

### 5. Craftable, rechargeable technology for automatic summoning

**Status: accepted prototype direction; offline implementation in progress.**
The owner accepted two earned exosuit technologies: Companion Link for automatic
release of already owned companions, and a dependent Companion Recharger that
consumes stored Ion Batteries. Each uses a technology slot. The base module has
manual battery recharge; the controller adds automatic battery use. No free
default requirement bypass, pet grant or lowered native limit is intended.
Names, research prices, recipes and capacity/cost numbers remain provisional.

Energy is consumed once for a confirmed successful automatic summon, never for
placement failure, cancellation or following. Native manual summoning stays
available. Keep ON distinct from insufficient charge. Explain low charge,
depletion and missing batteries with nonrepeating notices plus persistent
native-menu status. Recharge means ready again, not an immediate summon.
All actual UI additions must include English and the affected translations.

The pure energy model now produces separately confirmable debit/recharge
requests from copied snapshots. It performs no native actions. Six technology
strings are maintained in all fourteen catalogs; thirteen translations remain
drafts. A pinned native-data prototype prepares the custom records and research
branch separately from the production mod. See the
[prototype and verification boundary](docs/research/TECHNOLOGY-PROTOTYPE.md)
and [exact-build inventory audit](docs/research/TECHNOLOGY-RUNTIME-AUDIT.md).

Before live use, verify native registration, installed-item reads, actual charge
and battery transactions, normal recharge UI, persistence, uninstall, packaging,
transfer to unmodified peers and multiplayer. Do not directly edit save files
or inject prototype inventory into the normal player save. Compiling an XML
definition does not validate these behaviors.

Unknown game versions must stop native integration before hooks or native calls.
The current 0.8.7 source retains the guarded host and scoped localized
outside-game warnings without an unsafe bypass or preference reset. Final-bundle
offline checks passed; live acceptance remains pending. A saved custom item still requires verified
update/removal behavior. Runtime refusal alone does not establish inventory or
data-table safety.

## Deferred idea: temporary pause

No new pause control is prioritized yet. The current OFF setting already cancels pending intent, and manual dismissal after an accepted summon is respected until the next ship exit. A temporary pause would be useful only if playtesting shows a distinct need to suspend several exits without changing the saved ON preference. If revisited, define an explicit resume action and clear session boundary first; avoid a hidden timer that unexpectedly re-enables summoning. This is a proposal, not an implemented mode.

## Maximum monetization permitted by applicable rules

**Status: owner objective clarified on 28 September 2026; no financial UI implemented or permission request sent.** Maximize revenue within actual policy and publisher permissions. A single unobtrusive link is not the agreed ceiling. Nexus supports combining conditional Donation Points, PayPal and external thank-you donation links on mod/profile/collection pages. A complete allowed scope still requires classification of local promotion and commercial permission; page-level permission alone does not resolve that.

The current [Donation Points rules](https://help.nexusmods.com/article/68-donation-points-system-terms-of-service) contain no blanket AI exclusion, but eligibility still depends on provenance, permissions and Nexus discretion. The substantial generated code/UI/translations require accurate **AI-Generated Content** disclosure under the [File Submission Guidelines](https://help.nexusmods.com/article/28-file-submission-guidelines); do not substitute **AI Assisted** to improve eligibility or visibility.

Evaluate persistent Support entries, first-activation/update/recurring notices, banner placement, sponsor and affiliate options against the [donation guidelines](https://help.nexusmods.com/article/77-donation-options-guidelines), file rules and [Hello Games EULA](https://www.nomanssky.com/end-user-licence-agreement/). Record limits and exceptions established by published sources; unpublished limits remain unresolved. Do not contact either organization or exclude a format on taste alone. Published prohibitions still apply; unclassified proposals are not authorization to implement them. Multiplayer promotion has an explicit uploaded-content restriction. The normal paid-mod ban and publisher-endorsed exception must not be conflated.

The latest owner proposal combines a startup activation notice with neutral
information about optional donations. Record its wording, timing and unresolved
scope in the [monetization review](docs/release/MONETIZATION.md#combined-startup-notice-proposal).
This is not implemented UI, a selected payment destination or confirmed policy
permission. A normal game startup and each save load are distinct events.

See [Monetization review](docs/release/MONETIZATION.md) for exact source dates, limits and unsent permission-request drafts. No account, donation destination or earnings forecast is assumed. Recheck the rules and final package rights before enrollment or publication.

The owner explicitly declined contacting either organization on 28 September
2026. Research must use published rules; the retained drafts are not an active
outreach task. Unpublished limits stay unresolved rather than being invented.
