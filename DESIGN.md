# Companion Auto Summon player experience

This document records the accepted product direction. It distinguishes the current experimental implementation from the intended public experience.

## Goal

Companion Auto Summon should feel consistent with No Man's Sky: familiar controls, the game's presentation style, appropriate language and a small number of meaningful notifications. It remains a third-party mod; do not claim official endorsement or disguise the origin of its installer or download page.

## Current state

The current candidate is 0.4.2-experimental; the approved name is Companion Auto Summon. The separate pyMHF tab uses the class name `CompanionAutoSummon`. Settings are in the separate pyMHF window, in English. HUD messages use the game's existing timed-message function, but actual on-screen rendering has not yet been confirmed. There is no custom entry in the game's X quick menu, no localization system and no finished public launcher.

## Intended settings integration

Prefer one dedicated CompanionAutoSummon/automatic-companion entry in the companion section of the native quick menu. Its final label and position must fit the existing layout and terminology. Do not replace a vanilla action or reuse its ID for a different purpose without a verified, non-conflicting implementation.

Expose the same underlying preferences:

- Automatic summoning on/off.
- Last manually selected or Random selection mode.
- Prefer matching native habitat in Random mode, relevant only on planets.
- Per-location controls for planets, space stations and the Nexus, if the menu safely supports a compact subpage.

The native menu and any retained development panel must share one preference store and apply changes through the same established game-thread path. Translated labels must not become internal setting values. A menu appearance change must not bypass native eligibility, change a companion's attributes or write game save files.

Native menu insertion is a feasibility task, not an implemented capability. First verify menu construction, available item ownership/IDs, text handling and action dispatch for the pinned binary. Then try one harmless read-only custom entry in a controlled test. Only after its navigation and lifecycle are sound should it be allowed to change a preference. Retain the desktop panel for development until this route is proven.

The initial read-only audit found a known-action dispatcher, but no verified registration API for custom entries. Existing submenu transitions in the pinned executable clamp depth to two beyond the root. Prefer a flat settings page within the verified limit; do not assume another nested location submenu is possible. A new numeric action ID alone does not create a working native action. The next investigation must establish native item construction, ownership and cleanup, then observe natural menu use before modifying it.

The subsequent exact-build static audit located menu construction, native item append and label-building paths. It also found unchecked action-classification indexing and no general custom-name fallback. An isolated observation-only probe is being prepared before any custom item is inserted. See [QUICK-MENU.md](QUICK-MENU.md) for the verified scope, diagnostic procedure and remaining boundaries.

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
