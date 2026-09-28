# Companion Auto Summon roadmap

This is the canonical backlog for unfinished release work and future ideas. It is not a feature list for the current package or a promise of release dates. Status updated on 28 September 2026: source candidate **0.8.5-play-trial** contains production **0.4.8** and unchanged menu **0.8.3-settings-trial**. It passed 333 production and 633 developer tests without failures or skips, plus real-framework offline checks of the separate 40-file bundle (39 payloads). It has not launched. The running **0.8.4** bundle remains unchanged. Its six setting icons are visible in screenshots, but one Nexus startup failed visibly and a later ship exit summoned a different Random pet. Gameplay and full interface acceptance remain incomplete. Unaccepted proposals below remain unapproved for implementation.

Use [DESIGN.md](DESIGN.md) for accepted product behavior, [LOCALIZATION.md](LOCALIZATION.md) for language requirements and [the release plan](docs/release/PRIPRAVA-VYDANI.md) for publication checks. Update this backlog when a proposal is accepted, deferred, rejected or implemented. Record the version and verification evidence when a task is completed.

## Accepted unfinished release work

These requirements were accepted before this backlog was created. Finish them before adding optional features that would complicate the first release.

Independent offline preparation now covers complete localized menu/HUD text
and a console-free host import, without changing the current play trials. See
[native text](docs/research/NATIVE-LOCALIZATION-AUDIT.md) and
[portable runtime](docs/research/PORTABLE-RUNTIME-AUDIT.md). Neither preparation
establishes game-language readiness, rendered translations or an installer.

The immediate priority is the intermittent Nexus startup failure. Prepared
production 0.4.8 retains passive diagnostics after the first logical active
index, within the existing 15-second / 4096-callback observation limits. It adds
no retry, placement override or summon timing change and is not a spawn fix.
See [the live 0.8.4 record](docs/research/LIVE-084.md) and the
[next combined test](docs/release/PRIPRAVA-VYDANI.md#nejbližší-společný-test-085).
Keep the running game and host intact; use the next ordinary closed-game window
for a fresh backup and the separately prepared candidate.

The candidate retains matched manual-selection attribution, 5.5-second notices,
six native controls and seven original role assets. Screenshots confirm the six
setting icons in 0.8.4; parent/HUD appearance, all controls and resource teardown
still need acceptance. The label **Random: prefer matching biome** describes the
existing planet-only Random preference. No new player-facing wording or meaning
is introduced by 0.4.8; all fourteen catalogs remain unchanged.

The guarded host, actual target-handle check before injection, read-only
preflight and separate setup/host leases remain in place. Nine compatibility
messages use fourteen catalogs (39 keys each; thirteen draft translations).
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
| Simple, reliable installation | Current 0.8.5 retains the guarded direct host, shared compatibility profile, nine localized compatibility messages, read-only preflight and setup/host leases from 0.8.4. The 0.8.4 preflights and subsequent guarded launch have bounded evidence. Normal setup still requires external Python and prepares dependencies. A portable offline runtime and finished graphical launcher are not implemented. | Retain the offline mismatch/no-write/lease tests, then verify extract-and-launch on a clean second Windows account/PC, relocated/non-ASCII paths, no external Python dependency and no unexpected game termination. Follow [installer requirements](docs/release/INSTALACE-ZADANI.md). |
| Native quick-menu settings | Running 0.8.4 and prepared 0.8.5 share menu 0.8.3, six settings and the explicit Random biome label. Six setting icons are visible in 0.8.4 screenshots. All seven DDS files are validated before staging; each role has native-paw fallback. Complete controls, parent/HUD rendering and resource lifetime remain unverified. Keep automatic summoning and the desktop panel during acceptance. See [QUICK-MENU.md](QUICK-MENU.md). | All six controls apply/persist without changing unrelated values; native navigation/rebuilds and ordinary pet actions; default/remapped keyboard and controllers; seven correct icons, retained fallback and text-only behavior; no changed gameplay limits or shared vanilla textures. |
| Native number shortcuts | Requested next work; blocked by tagged None serialization losing the marker and potentially replacing a prior binding with an empty action. The existing native binding guard remains required. No custom shortcut or physical hotkey is implemented. | Verify native binding, replay, removal and persistence without losing existing shortcuts; prove remapped native-input behavior and controller handling before enabling it. Do not substitute physical key hooks or a second hotkey system. |
| Localization and natural feedback | Fourteen catalogs contain 39 keys; thirteen translations are drafts. Nine launcher compatibility messages use catalog lookup. Offline native text preparation passes 1,666 current language/state combinations within byte limits; it is not connected to the runtime. The exact-build language field is statically identified, but readiness, language switching and glyph rendering remain unverified. Native menu/HUD remain English. | Reviewed catalogs for all 14 official interface languages, complete launcher coverage, verified language selection, placeholders and in-game rendering. Quiet ordinary summons, honest save/session-only messages; evaluate the combined activation/donation-information proposal separately under the published-rule boundary below. |
| Live behavior and compatibility | Running 0.4.7 / 0.8.4 has one visibly failed Nexus startup and one later successful ship exit with a different Random companion. Prepared 0.4.8 / 0.8.5 adds bounded passive diagnostics only. The confirmed station startup and one respected dismissal belong to historical 0.4.3 / 0.6.2; they do not verify the current candidate. | Capture the longer failed-startup lifecycle and control companion choice before attributing a load/exit difference. Broaden dismissal regression; test planet/Nexus and Last manually selected startup, normal ship exit, preferences, biome preference/fallback, location controls, restart/save switching, obstructed placement then suitable terrain, cancellation and unsupported locations. Record visible appearance separately from queue acceptance or logical activity. |
| Multiplayer and release preparation | Second-PC installation and multiplayer remain unverified; Nexus material is still a draft. | Controlled tests with one and then, where available, two mod users; no duplicate or foreign-pet changes; accurate support limits; owner-approved attribution/reuse terms and distribution contents; current platform/publisher policy review. |

Keep the current native ownership, eligibility and placement rules. No roadmap item authorizes pet creation/unlocking, reduced gameplay limits, accelerated progression or writing NMS save files. The same exact-build guard remains required.

## New proposals, in suggested order

### 1. Choose which companions Random may use

**Status: proposed; not implemented.** Allow an optional inclusion list or exclusions among the player's owned companions. This would let a player keep a large or unwanted companion out of routine automatic selection without abandoning it. Default remains all eligible owned companions; the last-manual mode remains unchanged.

Treat inclusion and exclusion as two possible interfaces for one filter, not two independent settings systems. Use stable companion identity instead of slot numbers so rearranging slots does not silently select another pet. Build the pool from native-eligible owned companions, apply the player's filter and then apply the existing biome preference within that filtered pool. If the filtered pool is empty, do not summon and provide an unobtrusive status; never silently reintroduce an excluded companion. A draw stays fixed through deferred placement retries.

### 2. Optional avoidance of the immediately previous random companion

**Status: proposed; not implemented.** An optional Random setting could make successive exits feel more varied. Recommended initial default: off, preserving ordinary Random behavior unless the player chooses otherwise.

Apply it only when at least two distinct eligible companions remain after the optional player filter and biome preference. If only one remains, allow it. Exclude the previous random companion for that draw only; do not reroll while placement is blocked or draw a replacement after cancellation. Track the previous automatic choice separately from the manual favourite and define save/context reset behavior before implementation. Live tests must distinguish a confirmed appearance from a queue request before deciding which event advances the history.

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
The current 0.8.5 source retains the guarded host and scoped localized
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
