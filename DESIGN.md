# Companion Auto Summon for No Man's Sky — player experience

This document records the accepted product direction. It distinguishes the current experimental implementation from the intended public experience.

## Goal

Companion Auto Summon should feel consistent with No Man's Sky: familiar controls, the game's presentation style, appropriate language and a small number of meaningful notifications. It remains a third-party mod; do not claim official endorsement or disguise the origin of its installer or download page.

The approved external title is **Companion Auto Summon for No Man's Sky**, with
the byline **by Lineum Dynamics**. The in-game title remains **Companion Auto
Summon**. Present the author once in the main project/download presentation or
an appropriate About surface; keep individual native settings captions concise
and functional. An in-game author credit is a design direction, not an
implemented claim. Any future player-facing credit follows the catalog rule.
The canonical repository is
[lineum-dynamics/nms-companion-auto-summon](https://github.com/lineum-dynamics/nms-companion-auto-summon).
The repository slug, code identifiers, filenames and legacy player-data paths
remain unchanged by this presentation update.

## Current state

The follow-up **0.5.1 / 0.9.1** candidate replaces generic setting confirmations
with the changed labels and applied values, preserving session-only feedback
when persistence fails. Combined launches will omit the external pyMHF control
window through `gui.shown = false`; the native menu remains the player settings
interface. Validation passed 403 production and 689 developer tests. The 091-r1
bundle is built; actual-framework checks and both Python and Windows PowerShell
5.1 read-only preflights passed. This candidate has not launched and is not applied to the
running 090-r2. Standalone developer
launches still have their panel, and console-free packaging remains unfinished.

The running 090-r2 log later reports `Inert menu ordering stopped
(unexpected_thread)` at 14:30:17. The menu guard retains the native binding
filter but stops custom menu handling after a callback thread change; the
production automation is separate. The reason for the thread change and its
relation to the player's actions are not established. The unchanged menu in
0.9.1 does not fix this known limitation. Teleport arrival and base removal are
not automatic-summon triggers. The player reported no arrival pet and a pet
disappearing after base removal; the cause of that disappearance is unproven.
Next work is a bounded menu-lifecycle investigation, not an assumed new trigger
or automatic respawn after disappearance.

Retained source **0.5.0-experimental / 0.9.0-play-trial**, with menu
**0.9.0-selection**, now implements By habitat and Shuffle companions. Offline validation passed 396 production and 683 developer tests. The final `090-r2` candidate launched on 28 September 2026: its log records production 0.5.0, menu 0.9.0 and two Mods with twelve hooks initialized. Retained 0.8.7
and earlier artifacts remain immutable. The seven-row interface,
new selection behavior and rotation icon have no new live acceptance.
Existing schema-3 preferences retained Random with shuffle OFF during the
in-memory migration. The player confirms a visible Random startup companion
and says preferences appear saved. This is not restart-persistence, By habitat,
shuffle or full menu acceptance; see [LIVE-090](docs/research/LIVE-090.md).

By habitat uses explicit directed 13/5/1 exact/related/acceptable groups on
planets, independently of group population; stations/Nexus use the unweighted
eligible owned pool. Unknown planet data waits, no approved owned group skips
one opportunity with one notice, and temporary eligibility/placement failure
waits. Rotation is session-only, separate from the manual favourite, and consumes
only on native queue acceptance. Queue acceptance is not visible-spawn evidence.
Schema 4 defaults fresh installs to By habitat and rotation ON; legacy schemas
1/2/3 preserve their choices with rotation OFF. Details and the complete heuristic
table are in [HABITAT-SELECTION](docs/research/HABITAT-SELECTION.md).

The retained combined **0.8.7** has production **0.4.9**, menu **0.8.5-branding**, all six
existing preferences and 5.5-second confirmations. Earlier 0.8.4 screenshots confirm distinct
icons for the six setting roles. Each icon represents its function and stays
the same when its value changes; ON/OFF or the selected mode is in the caption.
White/gray is native selection styling, not the enabled state. English labels
use sentence case, with proper names such as **Space Anomaly** capitalized;
**Space stations** is a generic label and ON/OFF are uppercase state tokens.
This records the current English design, not a verified game-wide style guide.

In the earlier 0.8.4 session, the player reported no visible companion on one Nexus startup despite a brief
logical active index. A later ship exit successfully summoned another Random
pet. The retained branding candidate **0.4.9 / 0.8.7**, with menu
**0.8.5-branding**, retains extended passive diagnostics within their existing
bounds and read-only language observation in the CAS menu. The final 0.8.7-r1
launched after a verified 46-file backup. The player confirmed visible Random
summons after both Nexus save load and ship exit; different pets were chosen.
This does not establish an intermittent-failure fix or repeatability. The
prepared **0.8.6-r1** remains unchanged. See [the retained 0.8.7 evidence](docs/research/LIVE-087.md)
and [the earlier failure](docs/research/LIVE-084.md).
Full control, HUD, teardown and remapping acceptance remains incomplete.
The combined 0.9.1 candidate uses the native menu without creating the external
control window. The standalone developer ZIP retains its panel because it has
no native page or custom textures. Absence alone must never
trigger a retry after a possible manual dismissal.

Fourteen menu/HUD catalogs are now maintained and validated during builds.
The thirteen non-English catalogs are drafts, not verified language support.
Native runtime text remains English. The candidate records language scalars
without choosing a catalog; reload safety and glyph coverage require further
verification. Every change must review locale impact; changed text or meaning
requires the corresponding English and translation updates in the same change.

Native number shortcuts are requested. Their acceptance requires safe storage,
replay after restart, removal and preservation of existing assignments under
remapped native controls. Current tagged None entries remain blocked because
native serialization could replace a prior binding with an empty action.

Historical production 0.4.3 added one deferred opportunity after a successful local save load, using the existing automation toggle and summon checks. One Random-mode startup on a space station is confirmed by the log and the user, without a ship exit. Production 0.4.2 previously registered in the combined 0.6.1 trial and logged an accepted station queue at 20:18:19 without separate visible-pet confirmation. The separate pyMHF tab uses the class name `CompanionAutoSummon`. That historical trial retained its English panel and the native automation toggle; the six-control page has partial live evidence in combined 0.8.4. HUD messages use the game's existing timed-message function. The 0.7.0 trial screenshot confirms OFF text rendering with an unwanted solid white disc above it. Full native acceptance, localization and a finished public launcher remain incomplete.

Menu development sessions should retain functional automatic summoning and the
player's existing preferences. Use a separately validated combined development
bundle for normal play while menu presentation is tested. A deliberately
menu-only diagnostic is an exception and must be identified explicitly; it
must not silently replace the working mod for a player's ongoing session.

## Earned technology and update safety

The accepted next design is an earned **Companion Link** exosuit technology:
recipe acquisition, crafting, a technology slot and stored energy pay for the
convenience. The working fuel is the existing Ion Battery. Consume charge only
for a confirmed successful automatic summon; failed placement, cancelled intent,
ordinary following and native manual summoning must not consume this charge.
A separately earned **Companion Recharger** requires the base module and its own
slot and consumes actual batteries to refill it. It provides no free energy.
Names, recipes, research prices and numerical balance are prototype values.

Low energy, depletion and missing recharge fuel need concise, nonrepeating
feedback and persistent charge/reason information in the native settings page.
Energy unavailability does not change the player's ON preference or dismiss an
active pet. Recharge restores readiness; it does not create a new summon trigger.
Current implementation is an isolated offline model and native-data prototype,
not an installed requirement. See [technology research](docs/research/TECHNOLOGY-PROTOTYPE.md).

An unsupported executable must stop native integration automatically before
binding hooks or calling game functions. Exact executable identity, rather than
only a displayed patch number, is the compatibility boundary. The final launcher
must show a clear localized reason outside the game and distinguish game mismatch
from framework or package failure. Do not call an unverified HUD to report it,
overwrite preferences, offer a force-enable bypass, remove technology from saves
or silently promise an already modified save is safe without its data package.
The current candidate implements nine localized compatibility messages in the
host, with both preflight and actual-process checks before injection. It keeps
the native disabled guard. Other launcher text, the final portable installer
and native language selection remain unfinished. A compatibility refusal must
not start another game, reset preferences or attempt a native HUD notification.

## Summoning after loading

Loading directly on foot should offer the same automatic-companion behavior as a ship exit. Successful local load completion records one opportunity; it does not call native summoning or prove the world is ready. A later local ownership update waits for a supported enabled location, advancing time and the remembered identity or eligible Random pool. A missing favourite during initial ownership loading is retried at the existing 0.5-second pace. The normal 1.5-second stability delay, ownership rules and placement checks remain unchanged. Random can work session-only with a zero save ID; Last-manual mode never guesses an identity from another save.

Use the existing **Automatically summon companion** toggle for both triggers. OFF, a settings change, accepted manual selection, an active/queued pet, companion preview/emote, ship entry or an invalidated load/application context cancels the opportunity. The load opportunity is consumed before the normal request is armed, so dismissing a summoned pet does not create a recurring respawn. Another successful local load or real ship exit supplies a new opportunity. Network-client loads must not affect the local player's intent. There is no separate startup setting, shorter delay or changed gameplay limit.

The confirmed 27 September 2026 station test used production 0.4.3 in combined trial 0.6.2: the load armed at 20:42:58.578, selected one of five eligible companions and received an accepted queue about 2.69 seconds later. The user confirmed the pet appeared. The player later confirmed one manual dismissal without reappearance after traveling in the same unchanged session; its exact location and duration were not independently measured. Planet/Nexus startup, Last-manual startup, broader dismissal regression, biome matching and multiplayer remain separate unverified scenarios.

## Intended settings integration

The 0.7.0 trial has partial player/log evidence for basic ON/OFF application.
Its Anomaly load produced an accepted queue but no visible pet according to
the player. This open defect requires post-queue diagnosis; do not infer spawn
from acceptance or add retries that could override a manual dismissal.

Prefer one dedicated CompanionAutoSummon/automatic-companion entry in the companion section of the native quick menu, before individual pets and after general companion actions. The separate 0.6.0 trial implements this order in offline checks; its live result remains pending. Its final label must fit the existing layout and terminology. Do not replace a vanilla action or reuse its ID for a different purpose without a verified, non-conflicting implementation.

The retained 0.9.0-selection menu used by the 0.9.1 candidate exposes the same shared preference store with seven rows:

- Automatic summoning on/off.
- Last selected, Random or By habitat selection mode.
- Prefer matching native habitat in Random mode, relevant only on planets.
- Per-location controls for planets, space stations and the Space Anomaly (Nexus).
- Shuffle companions in Random and By habitat; no effect on Last selected.

The seven rows use the existing queue and storage. Selection cycles **Last
selected → Random → By habitat**; other rows display ON/OFF. Matching-biome preference
only affects Random on planets. All three locations may be OFF without changing
the main enabled flag or manual favourite. Queued and session-only states are
explicit. Full-page rebuild, navigation and deliberate confirmation still need
live acceptance; this is implemented source, not a verified release interface.

The native menu and any retained development panel must share one preference store and apply changes through the same established game-thread path. Translated labels must not become internal setting values. A menu appearance change must not bypass native eligibility, change a companion's attributes or write game save files.

The 0.9.1 combined candidate suppresses the separate pyMHF settings panel while
complete native-control acceptance remains pending. The final release must
verify this workflow end to end. The standalone developer panel is a temporary
development tool, not a second required player interface. Preserve existing
preferences during that transition. pyMHF may remain the background runtime;
its window must not be required during normal play. Removing GUI dependencies
is a separate packaging decision and must be checked against the framework.

The first automation toggle has bounded live evidence; now verify selection,
habitat preference and location controls. A setting may change only after a
deliberate native confirmation; navigation, hover, opening and rebuilding the
page must not change it. The native trigger's called-as-menu flag alone is not
proof of confirmation because selection paths can also dispatch an action.

The custom entry opens one flat settings page, rather than acting as another
pet or toggling every setting itself. The new candidate's children expose
automatic summoning, selection mode, the legacy Random habitat preference,
three locations and companion rotation.
Location choices should remain on that same page within the verified depth
limit. The first live inert entry did not open a subpage. The separate
0.5.0-submenu-trial introduced one inert Settings preview child for navigation
testing. The combined 0.6.1 play trial retains that child alongside production
0.4.2; the 0.6.2 bundle pairs the same inert menu with production 0.4.3 and has
passed offline folder discovery and in-game registration. One Random-mode
station summon after loading is now confirmed. The child is not connected to
these preferences.

The first screenshot confirmed a redundant name inside the icon above the
normal selected-item caption. The subsequent 0.5.0 submenu trial leaves inline
names empty and retains the ordinary captions; the player's new screenshots
confirm this appearance. The paw
was a borrowed prototype icon, not a settled product identity. The user asked
for an original custom icon. An original paw plus circular-arrow concept has
been saved as an opaque preview under `assets/concepts/` in the source repository
(excluded from the player ZIP). The transparent generation attempts had visible
artifacts and were rejected. A clean original vector glyph and its transparent
256-pixel PNG/RGBA32 DDS now exist under `assets/ui/`, with equal decoded pixels.
The 0.8.0 launcher stages that unique DDS only before a future launch with NMS
closed; it refuses unexpected existing bytes. The resource owner attempts one
native load in the verified phase and retains the original paw as fallback.
It uses fresh resource identity/readiness checks without writing the native paw
field. Loading, retained lifetime and small-size appearance remain unverified
in-game; source readiness is not proof of successful native rendering.
Do not overwrite a shared vanilla texture or distribute copied game artwork.

Historical insertion milestones: the inert-item trial has a native binding filter and confirmed visibility, selection, Back/close/reopen and normal manual companion summoning. The 0.5.0 submenu trial also has the player's confirmation of its inert child, native Back/close/reopen and ordinary pet actions, with screenshots confirming both captions and empty inline names. Shortcut, changing-pet-list, remapping and controller scenarios remain pending. At that stage, preference mutation remained gated on lifecycle and shortcut protection checks, and development retained the desktop panel. Later native preferences and the 0.9.1 combined GUI suppression are described above; complete player-interface acceptance remains pending.

The initial read-only audit found a known-action dispatcher, but no verified registration API for custom entries. Existing submenu transitions in the pinned executable clamp depth to two beyond the root. Prefer a flat settings page within the verified limit; do not assume another nested location submenu is possible. A new numeric action ID alone does not create a working native action. The next investigation must establish native item construction, ownership and cleanup, then observe natural menu use before modifying it.

The subsequent exact-build static audit located menu construction, native item append and label-building paths. It also found unchecked action-classification indexing and no general custom-name fallback. Isolated observation-only probes captured the natural companion submenu/summon route, menu vector rebuilds and bounded label completion during the player's menu sequence. Native hotkey serialization can lose an existing binding if a custom None item is bound; binding protection therefore remains a prerequisite before any custom item is inserted. See [QUICK-MENU.md](QUICK-MENU.md) for the verified scope, diagnostic procedure and remaining boundaries.

### Remappable controls

Players can change their bindings. Native-menu integration must follow the
game's current actions, focus and prompts, rather than assume physical X, Ctrl,
number keys or particular controller buttons. X is only shorthand for the
default quick-menu binding in development discussions.

Scope shortcut protection to the mod's uniquely identified menu item and the
native binding operation, independently of the physical input that requests it.
Preserve the player's ordinary navigation, activation, dismissal and native
shortcuts. Do not install a global physical-key suppression rule, rewrite the
player's bindings, or read game-save files to discover them. Player-facing
prompts must use verified native input hints; a translated literal key name does
not implement remapping support.

Before claiming support, test default and remapped keyboard/mouse actions,
reopening after an in-session binding change, controller navigation and any
supported controller remapping. Verify both the mod item and neighboring native
items, including binding attempts and retained existing shortcuts. These are
accepted requirements and test scenarios; remapping support for a custom menu
has not yet been verified across those scenarios.

## Notifications

The 0.4.4 queue-only attribution was insufficient: a pet-battle restore path can
reach the same hook. The 0.7.1 arena report changed the stored favourite, while a
later read-only snapshot showed no active or pending pet; the live caller was
not captured. No previous favourite is rolled back on that uncertain evidence.

Prepared 0.4.6 retains the 0.4.5 requirement for a matched native companion selection/shortcut, accepted
queue and successful original UI result, with fresh identity/context checks.
Unclassified queues cannot replace the favourite or announce a manual choice.
They retain native behavior and cancel pending automatic intent. Ordinary,
remapped and shortcut routes still need live checks before claiming coverage.

Explicit confirmations request 5.5 seconds. Every effective settings change
names its applied value, such as `Selection: By habitat`, `Shuffle companions:
ON` or `Space stations: OFF`. Multiple changes applied together appear in one
complete message, with one `(session only)` suffix if saving failed. A no-op
does not announce a change or cancel waiting intent. Presentation uses the
existing native notice path; it changes neither settings semantics nor summon
behavior. These new confirmations still require a visual game test.

`Companion saved.` means persistence
succeeded; otherwise use `Companion selected (session only).` OFF, Random or
habitat-selection context is appended where relevant. By habitat uses one
`No suitable companion for this habitat.` notice only when the known owned
roster has no approved group, not for temporary ineligibility or placement. Repeating the same choice, automatic
summoning and game restoration stay quiet. The combined candidate supplies a
ready original icon or retained native paw through an optional provider. Without
a usable owned handle, the verified final timed-message flag hides both icon
containers independently of the text. A new visual check must establish the
actual icon and white-disc outcomes; the ordinary standalone ZIP is text-only.

Use the game's existing visual presentation and a short localized sentence. Avoid repeated waiting errors, sounds on every summon, or messages that obscure ordinary game information. Ordinary save loads should not each generate an operational startup banner; this presentation preference is not a published monetization rule or the final frequency decision for the combined notice proposed below.

| Event | Intended feedback |
|---|---|
| First successful activation on this installation | One short ready message, after an actual valid game context exists |
| Player explicitly enables/disables automation | One confirmation of the applied state |
| Player changes selection mode or biome preference | One short confirmation, or the visible native menu state where that is sufficient |
| Player accepts a new manual favourite | One confirmation; repeated selection of the same pet stays quiet |
| Ordinary automatic summon | Quiet by default; seeing the pet is the confirmation |
| Temporary placement obstruction | Keep a status available; avoid repeated toasts or sounds while checking |
| Recoverable/terminal problem needing the player's action | One actionable localized message with details in the diagnostic log |

The owner has proposed combining the startup activation notice with neutral
information about where optional donations are possible. This is not implemented;
see [the wording and published-rule boundary](docs/release/MONETIZATION.md#combined-startup-notice-proposal).
The table's first-activation row describes the earlier operational ready notice,
not a final frequency limit for the combined proposal. A game startup and a save
load are distinct events. Any implemented copy must reflect actual readiness
and the automation preference and update English and all affected locales together.

Example English source wording, subject to terminology and display review: `Automatic companion summoning enabled.`, `Preferred companion saved.`, `Waiting for a suitable location.` These are proposed catalog values, not implemented translations or verified official game text.

An install-complete message belongs in the launcher. A ready message inside NMS must only claim the runtime is ready after successful initialization; loading a DLL or importing a module alone is insufficient. Do not claim a pet was summoned merely because the game accepted a queue request.

Use stable event keys for deduplication and merge pending notices so old state is not announced after newer state. First-run visibility should be local metadata, not a save edit. A player changing settings manually may receive feedback again; normal retries must not become repeated announcements.

## Localization and appearance

Follow `LOCALIZATION.md` for the 14 official Steam interface languages, English source keys, fallback rules, encoding, fonts and review status. Match the player's verified game language where possible, with an explicit override. Test the native HUD and menu separately from the desktop launcher.

Match existing spacing, selection feedback, input prompts and navigation. Do not invent quest rewards, milestone completions or gameplay bonuses as a way to announce the mod. Use game-provided UI resources through verified runtime paths; do not package copied game assets into the distribution.

## Public installation

The target is an extracted ZIP with a clickable launcher and an included, tested runtime. It must not require users to install Python or type setup commands. Native quick-menu settings would remove the need to visit a separate settings window during normal play; the external launcher would still be needed to start the runtime unless a different launch mechanism is separately implemented and verified.

## Verification before claiming integration

Check keyboard/controller navigation, menu open/close and rebuilds, save/context transitions, coexistence with vanilla companion actions, stored setting values, notification suppression, supported languages and multiplayer. Treat a desktop GUI test as evidence for that GUI only. Publish current support and known limits accurately.
