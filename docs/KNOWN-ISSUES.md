# Known issues

Status reviewed: 3 October 2026

Public mod build: **0.10.2-native-test**, Nexus file **49469** (Main / Primary; manual and mod-manager downloads enabled).

Supported game target: Windows x64, Steam Cosmos 7.05 / build 25624745, exact executable hash in the release package.

This page tracks reports against the current public build. A reported symptom is not proof of its suspected cause. Work-in-progress branch changes are not fixes for players until they are validated, packaged and released.

## No automatic summon after teleport or death

**Observed/current behavior:** 0.10.2 creates automatic opportunities after a successful local save load or ship exit and includes an experimental, filtered teleport callback. Earlier builds of the same candidate produced visible pets after two local teleport routes. The callback's game-level meaning and remote-player behavior are unknown, and the exact published archive has not yet been started in NMS. Death/respawn remains a separate unsupported trigger. No game eligibility or placement rule is bypassed.

**Status:** Open. Test whether a teleport by one player can summon a pet for a stationary partner and whether the exact archive starts successfully. Do not call this a verified arrival callback or multiplayer-safe behavior. Death/respawn needs a separate exact-build signal after a completed local respawn; it is not assumed to be the same event as teleport or save loading.

**Research update:** A read-only Cosmos 7.05 mapping pass on 1 October found
teleporter-selection labels and destination-position settings, but no verified
local successful-arrival callback. That pass led to a filtered candidate that
is now included in public 0.10.2 without a semantic claim. A shared
player-position helper also appears in a function with a
`DoPlayerRespawn` diagnostic label, but it is called from warp paths too and is
not verified as a successful-respawn signal. See the
[exact-build teleport and respawn research](research/TELEPORT-AND-GROUPED-MENU.md).
An offline-validated, test-only observer was loaded in one local session. Its
log recorded two candidate call sites during the successful save-load sequence,
without a reported death. They are not a verified death signal and the observer
does not request pets; the production trigger remains absent.
A later feature-branch control teleported from a freighter to a space station;
the owner saw a pet appear. The observer recorded candidate return
`0x3302C4` with `reason=11` (`0x0B`) and `flag=1`, then an accepted summon queue
1.36 seconds later. However, the same session had armed an automatic opportunity
about fourteen minutes before the teleport and recorded no new opportunity at
arrival. The source runtime arms opportunities only after local save load or
ship exit. This is consistent with an earlier pending opportunity becoming
eligible at the station, not evidence of a teleport trigger. It also confirms
this candidate helper runs during teleporter use, so it is not death-specific.
A later private candidate-trial retest produced a different sequence: at the
filtered return the test-only handler logged a new opportunity, then the native
queue accepted a request about 1.66 seconds later; the owner confirmed the pet
appeared. In this trial the handler refuses to run over an already-pending
policy request, clears a deferred save-load request, and arms a fresh one at the
candidate. This supports that the experimental hook initiated this request,
even if save-load waiting had been present. It still does not prove the return
is a semantically verified successful local teleport event or confirm
multiplayer isolation. Public 0.10.2 now includes this experimental candidate;
its exact archive still needs a live startup check.
In a second local control, the owner tested station-to-planetary-base
teleportation without a ship exit. The log showed a separate candidate
opportunity and accepted queue after the session's earlier save-load request
had already been accepted; the owner again confirmed visible appearance. This
reproduces the experimental trigger on a second local route, but does not
verify its game-level meaning, remote-player behavior, or any public fix.
An earlier negative control opened and closed the teleporter interface without
selecting a destination; it produced no observer event. The candidate call is
therefore not caused by opening or backing out of the interface alone. Whether
it marks destination confirmation, transition start or completed arrival
remains open.
A follow-up offline-validated diagnostic build corrected a stale hook-count log
message and was used for the two later local candidate trials. The packaged
0.10.2 module is a new artifact and has not yet been started in NMS.
The separate byte-pattern pass also recorded candidate references to native
teleport state; those hits are not semantic callbacks. See the
[sanitized static XREF record](research/NMS-075-STATIC-XREFS.md).

**Published 0.10.2 test behavior:** The released package includes this
filtered teleport candidate, gated by the existing master automation and
destination settings. The owner saw a pet after two local teleport routes in
an earlier build of the same candidate behavior. This supports a local test
trigger but does not establish the callback's game-level meaning or whether a
remote player's teleport can create an opportunity for the stationary player.
That local-versus-remote question is the specific multiplayer test for this
release. The exact archive still needs a fresh startup check, and no general
teleport support or multiplayer safety is claimed. Death/respawn remains a
separate unimplemented trigger.

## Settings menu can stop responding after a UI-thread change

**Observed:** The owner reported that after death the pet was absent and the Companion Auto Summon settings menu was missing. The current 0.10.1 session log recorded `menu_unexpected_thread`, which means the menu safety guard permanently stopped custom menu handling after a callback arrived on a different thread. The log contains no death event, so it does not prove that dying caused the thread change.

**Grouped roster:** One 0.10.1 live check showed the settings entry beside grouped companion rows. The 0.10.2 package includes the menu recovery candidate, but the exact archive has not yet been launched. No check covers every roster size, menu rebuild or UI-thread lifecycle.

**Fix status:** The 0.10.2 package includes the candidate that skips an isolated callback on an unexpected thread and rebinds only at a quiescent menu-builder start. It still refuses a handoff during an active builder, append, confirmation or trigger transaction. Twenty-five offline menu fixtures pass. In an earlier live test, the owner confirmed that the settings menu worked and a pet appeared after loading directly from an expedition into the Space Anomaly. That log recorded a successful local save load, an armed opportunity and an accepted summon queue. This is one successful live scenario; it does not establish recovery after death or reliability across menu rebuilds. The exact 0.10.2 archive still needs a startup and menu check.

## Other unconfirmed reports

- One direct load into the Space Anomaly had no visible pet while an Anomaly mission was incomplete. Whether mission state mattered, or whether the pet was delayed or overlooked, is unknown.
- A pet disappearing after base removal has been reported, but no causal behavior has been verified. The mod does not automatically respawn pets after manual dismissal or disappearance.

## Reporting

Please include the mod version, exact game build, location, event immediately before the problem, current summon/selection settings, whether a manual summon works, and whether the issue repeats after a normal restart. For menu reports, include whether the list is grouped and whether the menu was opened or rebuilt after death. Share only a short relevant log excerpt with personal paths and identifiers removed. Do not upload save files or private backups.

The [tester handoff](release/TESTER-HANDOFF.md) records the fuller validation history. The [Nexus page](https://www.nexusmods.com/nomanssky/mods/4579) carries the player-facing summary.
