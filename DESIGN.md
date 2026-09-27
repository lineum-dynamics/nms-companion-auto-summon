# Companion Auto Summon player experience

This document records the accepted product direction. It distinguishes the current experimental implementation from the intended public experience.

## Goal

Companion Auto Summon should feel consistent with No Man's Sky: familiar controls, the game's presentation style, appropriate language and a small number of meaningful notifications. It remains a third-party mod; do not claim official endorsement or disguise the origin of its installer or download page.

## Current state

The current player candidate is 0.4.2-experimental; the approved name is Companion Auto Summon. The separate pyMHF tab uses the class name `CompanionAutoSummon`. Settings are in the separate pyMHF window, in English. HUD messages use the game's existing timed-message function, but actual on-screen rendering has not yet been confirmed. The player package has no custom quick-menu settings, localization system or finished public launcher. The separate developer trial's first visible menu entry is described below.

## Intended settings integration

Prefer one dedicated CompanionAutoSummon/automatic-companion entry in the companion section of the native quick menu. Its final label and position must fit the existing layout and terminology. Do not replace a vanilla action or reuse its ID for a different purpose without a verified, non-conflicting implementation.

Expose the same underlying preferences:

- Automatic summoning on/off.
- Last manually selected or Random selection mode.
- Prefer matching native habitat in Random mode, relevant only on planets.
- Per-location controls for planets, space stations and the Nexus, if the menu safely supports a compact subpage.

The native menu and any retained development panel must share one preference store and apply changes through the same established game-thread path. Translated labels must not become internal setting values. A menu appearance change must not bypass native eligibility, change a companion's attributes or write game save files.

The custom entry is intended to open one flat settings page, rather than act as
another pet or toggle every setting itself. Its children will expose automatic
summoning, selection mode, habitat preference and the three location toggles.
Location choices should remain on that same page within the verified depth
limit. The running inert entry does not open this page yet. A separate
0.5.0-submenu-trial source now prepares one inert Settings preview child as the
next navigation test; it is not connected to these preferences.

The player's screenshot confirmed a redundant name inside the icon above the
normal selected-item caption. The next source revision leaves the inline tile
name empty and retains the ordinary caption. It has not been deployed. The paw
was a borrowed prototype icon, not a settled product identity. The user asked
for an original custom icon. An original paw plus circular-arrow concept has
been saved as an opaque preview under `assets/concepts/` in the source repository
(excluded from the player ZIP). The transparent generation attempts had visible
artifacts and were rejected. Final transparency, small-size appearance and
native texture loading must be validated before replacing the borrowed icon.
Do not overwrite a shared vanilla texture or distribute copied game artwork.

Native menu insertion is not a finished player capability. The running inert-item trial has a native binding filter and confirmed visibility, selection, Back/close/reopen and normal manual companion summoning. The new submenu trial passed offline checks but has not run in NMS; shortcut, remapping and controller scenarios also remain pending. Only after navigation, lifecycle and shortcut protection pass the controlled live scenarios should it change a preference. Retain the desktop panel for development until this route is proven.

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
has not yet been implemented or verified.

## Notifications

Use the game's existing visual presentation and a short localized sentence. Avoid a startup banner on every load, repeated waiting errors, sounds on every summon, or messages that obscure ordinary game information.

| Event | Intended feedback |
|---|---|
| First successful activation on this installation | One short ready message, after an actual valid game context exists |
| Player explicitly enables/disables automation | One confirmation of the applied state |
| Player changes selection mode or biome preference | One short confirmation, or the visible native menu state where that is sufficient |
| Player accepts a new manual favourite | One confirmation; repeated selection of the same pet stays quiet |
| Ordinary automatic summon | Quiet by default; seeing the pet is the confirmation |
| Temporary placement obstruction | Keep a status available; avoid repeated toasts or sounds while checking |
| Recoverable/terminal problem needing the player's action | One actionable localized message with details in the diagnostic log |

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
