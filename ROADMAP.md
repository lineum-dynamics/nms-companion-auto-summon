# Companion Auto Summon roadmap

Current source **0.5.0-experimental / 0.9.0-play-trial**, with menu
**0.9.0-selection**, implements the accepted By habitat and Rotate companions
work. Offline validation passed 396 production and 683 developer tests; the new candidate is
unlaunched. The running 0.8.7 package below remains unchanged, and its live
results do not validate the new selector. Source now has seven native settings
and 46 catalog keys in each of fourteen languages; native rendering remains
English. The seventh setting has an original rotation icon, checked offline. Full semantics and the
explicit heuristic table are in [HABITAT-SELECTION](docs/research/HABITAT-SELECTION.md).

This is the canonical backlog for unfinished release work and future ideas. It is not a feature list for the current package or a promise of release dates. Status updated on 28 September 2026: **Companion Auto Summon for No Man's Sky — by Lineum Dynamics**, running **0.8.7-play-trial**, contains production **0.4.9-experimental** and menu **0.8.5-branding**. It passed 333 production and 675 developer tests without failures or skips. The `build/quick-menu-play-trial-087-r1` folder has 41 files (40 payloads and its manifest) and passed real-framework offline checks, all six temporary preference paths and both Python and Windows PowerShell 5.1 read-only preflights. After normal closure and a verified 46-file backup, both Mods and twelve targets registered at 11:07:26 (Europe/Prague). The player confirmed visible Random pets after Nexus load and ship exit, then reported no apparent reappearance after a requested manual dismissal; the waiting duration was not independently measured. Initial post-start hashes matched the 40 payloads and existing settings/state. Retained **0.8.4** and prepared, unlaunched **0.8.6-r1** remain unchanged. Different pets and the unexplained earlier startup failure prevent a causal fix claim. Gameplay and full interface acceptance remain incomplete. See [LIVE-087](docs/research/LIVE-087.md). Unaccepted proposals below remain unapproved for implementation; the selection and rotation sections explicitly identify the newly implemented work.

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

The retained 0.8.7 candidate has matched manual-selection attribution, 5.5-second notices,
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
messages use fourteen catalogs (now 46 keys each; thirteen draft translations).
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
| Localization and natural feedback | Fourteen catalogs contain 46 keys; thirteen translations are drafts. Nine launcher compatibility messages use catalog lookup; two product keys cover the full name and author credit. Offline native text preparation passes 1,666 language/state combinations within byte limits; it is not connected to native rendering. Candidate 0.8.7 observes copied language scalars only. UTF-8 measurement/drawing decoders are statically verified; reload safety, language selection and live glyph rendering remain unverified. Native menu/HUD remain English. | Reviewed catalogs for all 14 official interface languages, complete launcher coverage, verified language selection, placeholders and in-game rendering. Quiet ordinary summons, honest save/session-only messages; evaluate the combined activation/donation-information proposal separately under the published-rule boundary below. |
| Live behavior and compatibility | Running 0.4.9 / 0.8.7 has player-confirmed visible Nexus summons after load and ship exit, with different Random pets. The player then reported no apparent return after requested manual dismissal; exact waiting time was not independently measured. These bounded observations do not explain the failed 0.8.4 startup or establish repeatability. | Control companion choice before attributing a load/exit difference. Broaden repeatability and dismissal regression; test planet and Last manually selected startup, preferences, biome preference/fallback, location controls, restart/save switching, obstructed placement then suitable terrain, cancellation and unsupported locations. Record visible appearance separately from queue acceptance or logical activity. |
| Multiplayer and release preparation | Second-PC installation and multiplayer remain unverified; Nexus material is still a draft. | Controlled tests with one and then, where available, two mod users; no duplicate or foreign-pet changes; accurate support limits; owner-approved attribution/reuse terms and distribution contents; current platform/publisher policy review. |

Keep the current native ownership, eligibility and placement rules. No roadmap item authorizes pet creation/unlocking, reduced gameplay limits, accelerated progression or writing NMS save files. The same exact-build guard remains required.

## Selection implementation and remaining proposals

### Selection modes and weighted habitat choice

**Status: implemented in 0.5.0 source; offline validation passed, unlaunched.**
Last selected, Random and By habitat now exist. By habitat draws a native-eligible
group with integer weights **13 exact / 5 related / 1 acceptable**, then a member
uniformly or through that group's rotation bag. Empty eligible groups are
removed and weights renormalized; group population does not change the weight.
The chosen Fibonacci ratio and the directed table are mod-design heuristics,
not native suitability or validated balance.

The [complete table](docs/research/HABITAT-SELECTION.md#directed-table) includes
Scorched↔Lava as related while leaving them distinct, excludes Frozen↔Lava and
has no unrestricted planetary fallback. Unknown planet data waits. No approved
owned group skips one opportunity with one notice; temporary native ineligibility
waits. Stations/Nexus use the unweighted eligible owned pool. Random's existing
exact-biome preference/fallback remains unchanged and does not govern By habitat.

Schema 4 uses By habitat and rotation ON only for fresh settings. Existing
schema 1/2/3 mode, biome, location and automation choices survive, with rotation
OFF; migration writes only on explicit save. Next acceptance must verify the
new mode and all seven controls visibly, including unsuitable/unknown habitats,
temporary eligibility and stable choices during placement waits.

### 1. Choose which companions Random may use

**Status: proposed; not implemented.** Allow an optional inclusion list or exclusions among the player's owned companions. This would let a player keep a large or unwanted companion out of routine automatic selection without abandoning it. Default remains all eligible owned companions; the last-manual mode remains unchanged.

Treat inclusion and exclusion as two possible interfaces for one filter, not two independent settings systems. Use stable companion identity instead of slot numbers so rearranging slots does not silently select another pet. Build the pool from native-eligible owned companions, apply the player's filter and then apply the existing biome preference within that filtered pool. If the filtered pool is empty, do not summon and provide an unobtrusive status; never silently reintroduce an excluded companion. A draw stays fixed through deferred placement retries.

### 2. Rotate companions across automatic opportunities

**Status: implemented in 0.5.0 source; offline validation passed, unlaunched.**
Rotate companions is the seventh native row. Random uses an eligible session
cycle; By habitat draws its group first, then uses that habitat/group's cycle.
Last selected is unaffected. A single eligible member may repeat; no cross-group
cycle changes the weights. No setting change dismisses or replaces an active pet
or creates a new summon opportunity.

The runtime copies at most 30 occupied pets using the verified CreatureSeed +
BirthTime token and refuses duplicate identities. Ownership reconciliation removes
lost members, inserts genuinely new members once and retains surviving consumed/
unconsumed history. Temporary ineligibility is not adoption. Exhausting the
currently eligible remainder renews that pool while hidden unconsumed members
retain their order. Between-opportunity slot reorder does not reset cycles.

A pending request freezes slot and identity. By habitat also freezes its
supported planet/neutral context; Random remains location-independent. Removal,
ambiguity, slot reorder or a changed By habitat context cancels without substituting
or redrawing; temporary unsupported locations retain the deferred wait. Only an accepted native queue consumes rotation; failed placement,
retry and cancellation do not. Acceptance is not visible-spawn evidence.
Local save/load/application boundaries reset session bags, including reloading
the same save; remote network loads do not. No cycle is written to a game save
or the manual-favourite store. Remaining work is live acceptance and balance
assessment, not another implementation promise. See the [full contract](docs/research/HABITAT-SELECTION.md).

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
