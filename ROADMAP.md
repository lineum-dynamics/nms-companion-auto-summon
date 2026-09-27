# Companion Auto Summon roadmap

This is the canonical backlog for unfinished release work and future ideas. It is not a feature list for the current package or a promise of release dates. Status updated on 28 September 2026: the immutable last-launched 0.8.2 folder contains production 0.4.7 and menu 0.8.0, with the original single icon. Prepared 0.8.3-play-trial / 0.8.3-settings-trial has not launched and leaves production 0.4.7 unchanged. Registration and native active-state logs do not confirm visible icons or companions. Gameplay and interface acceptance are pending. New proposals below remain unapproved for implementation.

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
| Simple, reliable installation | The 0.4.7 / 0.8.2 launcher adds read-only preflight and distinct setup/host leases across package folders. Normal setup still requires external Python and prepares dependencies. A portable offline runtime and graphical launcher are not implemented. | Validate check-only without writes or startup, duplicate launches across folders, normal/crash lease release and refusal on failed process enumeration; then extract-and-launch on a clean second Windows account/PC, relocated/non-ASCII paths, no external Python dependency, exact-build checks and no unexpected game termination. Follow [installer requirements](docs/release/INSTALACE-ZADANI.md). |
| Native quick-menu settings | Installed 0.8.2 contains the six-row menu from 0.8.0; prepared, unlaunched 0.8.3 adds seven distinct icons and clarifies the Random biome label. All seven DDS files are validated before closed-game staging; each role has native-paw fallback. Full-page acceptance and resource rendering/lifetime remain unverified. Keep automatic summoning and the desktop panel during acceptance. See [QUICK-MENU.md](QUICK-MENU.md). | All six controls apply/persist without changing unrelated values; native navigation/rebuilds and ordinary pet actions; default/remapped keyboard and controllers; seven correct icons, retained fallback and text-only behavior; no changed gameplay limits or shared vanilla textures. |
| Native number shortcuts | Requested next work; blocked by tagged None serialization losing the marker and potentially replacing a prior binding with an empty action. The existing native binding guard remains required. No custom shortcut or physical hotkey is implemented. | Verify native binding, replay, removal and persistence without losing existing shortcuts; prove remapped native-input behavior and controller handling before enabling it. Do not substitute physical key hooks or a second hotkey system. |
| Localization and natural feedback | Fourteen draft source catalogs and a required offline build validator are implemented. Runtime UI/HUD remain English; no verified game-language reader or non-English glyph path exists. Catalogs are not live localization. | Reviewed catalogs for all 14 official interface languages, verified language selection, placeholder checks and in-game rendering checks. Quiet ordinary summons, honest save/session-only messages and a restrained first-activation notice. |
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

**Status: feasibility requested on 28 September 2026; not implemented.** The
player asked whether automatic summoning could fit the game's progression
through an item or upgrade. A working concept is an exosuit technology named
**Companion Link**: acquire a recipe, craft and install it, then permit the
existing automation while it is installed. Acquisition, recipe, name and slot
cost are undecided. This is a mod design concept, not an existing game item.

The owner prefers a meaningful cost for the convenience, including recharge.
The earlier assistant suggestion of an optional requirement and free default
was not accepted as a decision. Explore an earned technology with an installation
cost and charge consumed by successful automatic summons. Exact acquisition,
fuel, capacity and usage cost remain undecided. Failed placement or cancelled
requests should not consume charge; manual summoning should retain native rules.
No pet stat bonus, free pet or lowered native limit is proposed. Native X-menu
preferences would remain the control surface. The existing runtime is unchanged.

The owner compared it to a Pokeball/Pokedex and asked whether it belongs on a
multitool. The current recommendation is a personal summoning module in the
exosuit, independent of the selected multitool. The analogy is automatic release
of an already owned companion, not capture, scanning or a new companion registry.
Pokemon is a design analogy only; use original NMS-appropriate naming and art.
Exosuit placement and the proposed energy-per-success rule are not implemented.

Fuel recommendation: use the existing Ion Battery rather than adding a second
custom consumable. One battery would refill a reservoir for several successful
automatic summons; neither ordinary following nor a failed placement would
drain it. Depletion would suspend future automation without dismissing an active
pet. Capacity and per-summon cost need playtesting. This recommendation is not
implemented or finalized; the [official Prisms notes](https://www.nomanssky.com/prisms-update/)
document Ion Battery crafting as an existing game mechanic.

**Accepted communication requirement for this proposed feature:** energy loss
must never look like a broken mod. Show one low-energy warning before depletion,
a clear recharge-required notice at depletion, and persistent charge/reason
information in the native X menu. Keep the player's automation preference ON
while energy temporarily blocks operation; do not conflate depletion with a
manual OFF selection. A brief recharge confirmation should say the module is
ready again without promising an immediate summon outside normal triggers.
Do not repeat warnings on every ship exit or warn about inactive automation.
Define warning reset/reload behavior so existing depletion is explained once
after loading, without notification spam. All added wording and its English
source must enter every locale catalog in the same implementation change.
These are recorded requirements; no charge or notification behavior is added
to the current build.

Automatic recharge is also under discussion. Distinguish automatic consumption
of stored Ion Batteries from passive energy regeneration without consumables.
The current recommendation is manual battery recharge on the basic module and
a separately earned later upgrade for automatic battery use, with transparent
inventory consumption. No fuel-use setting or extra upgrade is approved yet.
The owner subsequently suggested making automatic recharge a further upgraded
module. The recommended design is two dependent technologies: the basic summon
module works with manual recharge; a separately crafted recharge controller
automatically consumes available Ion Batteries to refill the basic module.
The controller would require the basic module and its own technology slot;
it would provide no pet bonuses or energy without fuel. Warn clearly when
available batteries run out. Names, costs and whether the controller is a
separate module or replacement tier remain proposals, not implementation.
Hello Games' [Beyond notes](https://www.nomanssky.com/beyond-update/) provide a
design precedent for a separate Launch System Recharger that replenishes launch
energy over time; this does not prove our custom module can reuse that behavior.

Feasibility evidence: the [MBINCompiler technology schema](https://github.com/monkeyman192/MBINCompiler/blob/development/libMBIN/Source/NMS/GameComponents/GcTechnology.cs)
exposes ID, recipe requirements, category and charge fields. The author's
[historical new-technology mod](https://www.nexusmods.com/nomanssky/mods/259)
demonstrates distinct additions, but dates from 2016 and does not verify Cosmos
7.04. The newer author source for [Aquatic Blaster 6.00](https://raw.githubusercontent.com/MetaIdea/nms-amumss-lua-mod-script-collection/main/FriendlyFirePL/FF_AquaticBlaster/FF_AquaticBlaster_600.lua)
also demonstrates custom technology/recipe/research entries, but reuses a native
weapon function and does not verify our target. Custom summon-triggered
consumption still requires runtime work and exact-build validation. Multiplayer safety is unverified: Hello Games describes
[technology packaging and transfer](https://www.nomanssky.com/waypoint-update/),
so test custom-ID packaging/transfer to a player without the mod, in addition
to ordinary mixed sessions, saving/reloading and uninstall behavior. Do not
assume a technology stays local merely because the summon controller is local.

The current no-progression-change/no-save-write contract still applies to
implementation: research native item registration and save ownership first, including
what happens when uninstalling the technology or the mod, changing saves and
playing expeditions or multiplayer. Do not silently add inventory contents or
edit saves to prototype this idea.

## Deferred idea: temporary pause

No new pause control is prioritized yet. The current OFF setting already cancels pending intent, and manual dismissal after an accepted summon is respected until the next ship exit. A temporary pause would be useful only if playtesting shows a distinct need to suspend several exits without changing the saved ON preference. If revisited, define an explicit resume action and clear session boundary first; avoid a hidden timer that unexpectedly re-enables summoning. This is a proposal, not an implemented mode.

## Optional support link, subject to review

**Status: proposed; publisher permission, launcher-policy clarification and owner destination unresolved.** Prefer an optional thank-you/donation link on the Nexus page first, subject to applicable publisher terms. A small About/Support link inside the future launcher remains a separate proposal, opened only by an explicit click. No startup popup, automatic browser opening, repeated prompts, multiplayer advertisements, paid features, paid support priority or access gates.

Policy review recorded on 27 September 2026: [Nexus Donation Options & Guidelines](https://help.nexusmods.com/article/77-donation-options-guidelines) permit donation links on mod/profile/collection pages, but prohibit excessive reminders in files, benefits such as betas/features/support in exchange, and suggesting that future development depends on donations. [Nexus File Submission Guidelines](https://help.nexusmods.com/article/28-file-submission-guidelines) also restrict advertising, adware and nonessential network access. Page-level permission is not evidence that an in-launcher link or popup is allowed.

The [Hello Games EULA](https://www.nomanssky.com/end-user-licence-agreement/) (page dated 25 January 2019, checked 27 September 2026) includes broad commercial-use restrictions in section 4.2.4 and community-content advertising/link restrictions in section 6.2. Their application to a local launcher needs clarification; no explicit local-promotion exemption was found, and this is not a finding that every local link is prohibited. Recording the idea does not establish permission to monetize the mod. Recheck applicable terms before adding any destination or opting into a rewards program. Do not invent an account, donation URL, expected demand or earnings forecast. The mod remains free in the proposed distribution model.
