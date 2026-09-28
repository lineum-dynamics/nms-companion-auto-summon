# Companion Auto Summon roadmap

This is the canonical backlog for unfinished release work and future ideas. It is not a feature list for the current package or a promise of release dates. Status updated on 28 September 2026: current source candidate 0.8.4-play-trial retains production 0.4.7 and menu 0.8.3-settings-trial. Final validation passed 329 production and 633 developer tests without failures or skips. The final 40-file bundle (39 payloads), real-framework offline smoke and both Python and Windows PowerShell 5.1 read-only preflights passed. No launch, deployment or setup occurred. Prepared 0.8.3 and the immutable last-launched 0.8.2 folder remain unchanged. The latter contains menu 0.8.0 and the original single icon. Registration and native active-state logs do not confirm visible icons or companions. Gameplay and interface acceptance are pending. Unaccepted proposals below remain unapproved for implementation.

Use [DESIGN.md](DESIGN.md) for accepted product behavior, [LOCALIZATION.md](LOCALIZATION.md) for language requirements and [the release plan](docs/release/PRIPRAVA-VYDANI.md) for publication checks. Update this backlog when a proposal is accepted, deferred, rejected or implemented. Record the version and verification evidence when a task is completed.

## Accepted unfinished release work

These requirements were accepted before this backlog was created. Finish them before adding optional features that would complicate the first release.

The 0.4.7 candidate retains the manual-origin repair prepared in unlaunched
0.4.5 / 0.7.2: only a matched successful native UI summon can replace or announce
a favourite. The 0.7.1 arena event's actual caller remains unknown; existing
stored choices are preserved. Shorter 5.5-second notices and the verified
icon-hide fallback need a live visual check. Combined 0.8.2 retains the six
native settings and original-icon loading/fallback from menu 0.8.0-settings-trial,
all pending live acceptance. Production 0.4.7 changes only version metadata from
0.4.6. Launcher changes add read-only `-CheckOnly`, usable while NMS runs, and
separate fixed setup/host session leases that reject duplicate launches across
package folders. Their OS handle lifetime handles process exits and crashes;
normal setup refuses an unknown process state. Preflight is not gameplay
validation. Retained older artifacts remain unchanged.

Prepared 0.8.3 assigns distinct original icons to the parent and all six settings,
with independently validated native-paw fallback. Closed-game staging validates
all seven DDS files and existing destinations before publication; the installed 0.8.2
installation is untouched. The label **Random: prefer matching biome** clarifies
the existing rule without changing it. Final validation totals belong in the
candidate manifest, and visual acceptance requires the next separate live trial.

The 0.8.4 host guard verifies the selected executable before framework import
and the actual target-handle executable before every DLL injection. It rejects
unexpected framework configuration and foreign `pymhflib` entry points.
The shared compatibility profile is checked against source/manifest declarations
during builds. Nine scoped launcher messages now consume the 14 catalogs
(39 keys each; 13 draft translations). Final validation passed 329 production
and 633 developer tests with no failures or skips. The real-framework smoke
passed with all six controls and temporary preferences, without native hooks
or game access. The rebuilt final bundle contains 40 files (39 payloads).
Python `--check-only` and Windows PowerShell 5.1 `-CheckOnly` both passed against
the installed game and runtime without launch, deployment or setup.
These checks do not complete the portable installer, all launcher translations, native
localization or the saved-technology safety work.

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
| Simple, reliable installation | Current 0.8.4 adds the guarded direct host, shared compatibility profile and nine localized compatibility messages to existing read-only preflight and setup/host leases. Both final-bundle preflights passed against the installed game/runtime. Normal setup still requires external Python and prepares dependencies. A portable offline runtime and finished graphical launcher are not implemented. | Retain the offline mismatch/no-write/lease tests, then verify extract-and-launch on a clean second Windows account/PC, relocated/non-ASCII paths, no external Python dependency and no unexpected game termination. Follow [installer requirements](docs/release/INSTALACE-ZADANI.md). |
| Native quick-menu settings | Installed 0.8.2 contains the six-row menu from 0.8.0; current unlaunched 0.8.4 retains the prepared 0.8.3 menu, seven distinct icons and explicit Random biome label. All seven DDS files are validated before closed-game staging; each role has native-paw fallback. Full-page acceptance and resource rendering/lifetime remain unverified. Keep automatic summoning and the desktop panel during acceptance. See [QUICK-MENU.md](QUICK-MENU.md). | All six controls apply/persist without changing unrelated values; native navigation/rebuilds and ordinary pet actions; default/remapped keyboard and controllers; seven correct icons, retained fallback and text-only behavior; no changed gameplay limits or shared vanilla textures. |
| Native number shortcuts | Requested next work; blocked by tagged None serialization losing the marker and potentially replacing a prior binding with an empty action. The existing native binding guard remains required. No custom shortcut or physical hotkey is implemented. | Verify native binding, replay, removal and persistence without losing existing shortcuts; prove remapped native-input behavior and controller handling before enabling it. Do not substitute physical key hooks or a second hotkey system. |
| Localization and natural feedback | Fourteen catalogs contain 39 keys; thirteen translations are drafts. Nine launcher compatibility messages use catalog lookup, with Windows UI locale/explicit override and English recovery fallback. Other launcher text and the panel remain outside this scope. Native menu/HUD remain English; no verified game-language reader or non-English glyph path exists. | Reviewed catalogs for all 14 official interface languages, complete launcher coverage, verified language selection, placeholders and in-game rendering. Quiet ordinary summons, honest save/session-only messages and a restrained first-activation notice. |
| Live behavior and compatibility | In combined trial 0.6.2, production 0.4.3 summoned one Random companion after an on-foot station load without a ship-exit trigger; the log and player confirm the result. The player later confirmed one manual dismissal without reappearance after traveling in the same unchanged session. Earlier visible results belong to their original versions. | Broaden dismissal regression; test planet/Nexus and Last manually selected startup, then normal ship-exit regression; existing preferences; biome preference/fallback; location controls; restart/save switching; rejected placement followed by a suitable location; cancellation and unsupported locations. Record actual appearance separately from an accepted queue request. |
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
The current 0.8.4 source implements the guarded host and scoped localized
outside-game warnings without an unsafe bypass or preference reset. Final-bundle
offline checks passed; live acceptance remains pending. A saved custom item still requires verified
update/removal behavior. Runtime refusal alone does not establish inventory or
data-table safety.

## Deferred idea: temporary pause

No new pause control is prioritized yet. The current OFF setting already cancels pending intent, and manual dismissal after an accepted summon is respected until the next ship exit. A temporary pause would be useful only if playtesting shows a distinct need to suspend several exits without changing the saved ON preference. If revisited, define an explicit resume action and clear session boundary first; avoid a hidden timer that unexpectedly re-enables summoning. This is a proposal, not an implemented mode.

## Maximum monetization permitted by applicable rules

**Status: owner objective clarified on 28 September 2026; no financial UI implemented or permission request sent.** Maximize revenue within actual policy and publisher permissions. A single unobtrusive link is not the agreed ceiling. Nexus supports combining conditional Donation Points, PayPal and external thank-you donation links on mod/profile/collection pages. A complete allowed scope still requires classification of local promotion and commercial permission; page-level permission alone does not resolve that.

The current [Donation Points rules](https://help.nexusmods.com/article/68-donation-points-system-terms-of-service) contain no blanket AI exclusion, but eligibility still depends on provenance, permissions and Nexus discretion. The substantial generated code/UI/translations require accurate **AI-Generated Content** disclosure under the [File Submission Guidelines](https://help.nexusmods.com/article/28-file-submission-guidelines); do not substitute **AI Assisted** to improve eligibility or visibility.

Evaluate persistent Support entries, first-activation/update/recurring notices, banner placement, sponsor and affiliate options against the [donation guidelines](https://help.nexusmods.com/article/77-donation-options-guidelines), file rules and [Hello Games EULA](https://www.nomanssky.com/end-user-licence-agreement/). Request actual limits and any relevant exceptions rather than inventing a frequency or excluding a format on taste alone. Published prohibitions still apply; unclassified proposals are not authorization to implement them. Multiplayer promotion has an explicit uploaded-content restriction. The normal paid-mod ban and publisher-endorsed exception must not be conflated.

See [Monetization review](docs/release/MONETIZATION.md) for exact source dates, limits and unsent permission-request drafts. No account, donation destination or earnings forecast is assumed. Recheck the rules and final package rights before enrollment or publication.

The owner explicitly declined contacting either organization on 28 September
2026. Research must use published rules; the retained drafts are not an active
outreach task. Unpublished limits stay unresolved rather than being invented.
