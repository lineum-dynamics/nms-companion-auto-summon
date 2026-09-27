# Companion Auto Summon roadmap

This is the canonical backlog for unfinished release work and future ideas. It is not a feature list for the current package or a promise of release dates. Status checked against the 0.4.2-experimental source on 27 September 2026. New proposals below have been recorded for discussion; they are not approved for implementation.

Use [DESIGN.md](DESIGN.md) for accepted product behavior, [LOCALIZATION.md](LOCALIZATION.md) for language requirements and [the release plan](docs/release/PRIPRAVA-VYDANI.md) for publication checks. Update this backlog when a proposal is accepted, deferred, rejected or implemented. Record the version and verification evidence when a task is completed.

## Accepted unfinished release work

These requirements were accepted before this backlog was created. Finish them before adding optional features that would complicate the first release.

| Work | Current boundary | Completion evidence |
|---|---|---|
| Simple, reliable installation | The development launcher still requires an external Python installation and prepares dependencies. A portable offline runtime and graphical launcher are not implemented. | Extract-and-launch on a clean second Windows account/PC; relocated and non-ASCII paths; no external Python dependency; exact-build checks; no duplicate host or unexpected game termination. Follow [installer requirements](docs/release/INSTALACE-ZADANI.md). |
| Native quick-menu settings | The separate pyMHF panel exists. Safe custom X-menu insertion is still a feasibility task. | Verified native item construction, action dispatch and cleanup; one harmless entry before preference controls; keyboard/controller navigation; shared preference store; no displaced vanilla action. |
| Localization and natural feedback | UI/HUD text is English-only; encoding and glyph coverage are unresolved. Some visible messages still need live verification. | Catalogs for all 14 official interface languages, verified language selection, placeholder checks, translation review and in-game rendering checks. Quiet ordinary summons, honest save/session-only messages and a restrained first-activation notice. |
| Live behavior and compatibility | 0.4.2 has offline evidence but has not been launched in NMS. Earlier live results belong to their original versions. | Renamed launcher and existing preferences; biome preference/fallback; location controls; restart/save switching; rejected placement followed by a suitable location; cancellation, station/Nexus and unsupported locations. Record actual appearance separately from an accepted queue request. |
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

## Deferred idea: temporary pause

No new pause control is prioritized yet. The current OFF setting already cancels pending intent, and manual dismissal after an accepted summon is respected until the next ship exit. A temporary pause would be useful only if playtesting shows a distinct need to suspend several exits without changing the saved ON preference. If revisited, define an explicit resume action and clear session boundary first; avoid a hidden timer that unexpectedly re-enables summoning. This is a proposal, not an implemented mode.

## Optional support link, subject to review

**Status: proposed; publisher permission, launcher-policy clarification and owner destination unresolved.** Prefer an optional thank-you/donation link on the Nexus page first, subject to applicable publisher terms. A small About/Support link inside the future launcher remains a separate proposal, opened only by an explicit click. No startup popup, automatic browser opening, repeated prompts, multiplayer advertisements, paid features, paid support priority or access gates.

Policy review recorded on 27 September 2026: [Nexus Donation Options & Guidelines](https://help.nexusmods.com/article/77-donation-options-guidelines) permit donation links on mod/profile/collection pages, but prohibit excessive reminders in files, benefits such as betas/features/support in exchange, and suggesting that future development depends on donations. [Nexus File Submission Guidelines](https://help.nexusmods.com/article/28-file-submission-guidelines) also restrict advertising, adware and nonessential network access. Page-level permission is not evidence that an in-launcher link or popup is allowed.

The [Hello Games EULA](https://www.nomanssky.com/end-user-licence-agreement/) (page dated 25 January 2019, checked 27 September 2026) includes broad commercial-use restrictions in section 4.2.4 and community-content advertising/link restrictions in section 6.2. Their application to a local launcher needs clarification; no explicit local-promotion exemption was found, and this is not a finding that every local link is prohibited. Recording the idea does not establish permission to monetize the mod. Recheck applicable terms before adding any destination or opting into a rewards program. Do not invent an account, donation URL, expected demand or earnings forecast. The mod remains free in the proposed distribution model.
