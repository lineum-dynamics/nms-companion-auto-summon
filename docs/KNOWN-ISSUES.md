# Known issues

Status reviewed: 1 October 2026

Public mod build: **0.10.1-native-test**, Nexus file **49367**

Supported game target: Windows x64, Steam Cosmos 7.05 / build 25624745, exact executable hash in the release package.

This page tracks reports against the current public build. A reported symptom is not proof of its suspected cause. Work-in-progress branch changes are not fixes for players until they are validated, packaged and released.

## No automatic summon after teleport or death

**Observed/current behavior:** 0.10.1 creates automatic opportunities after a successful local save load or ship exit. The owner reported no automatic pet after death. The build has no verified trigger for teleport arrival or completed death/respawn, so neither event by itself requests a pet. No game eligibility or placement rule is bypassed.

**Status:** Open. Teleport arrival needs a verified local completion callback. Death/respawn needs a separate exact-build signal after a completed local respawn; it is not assumed to be the same event as teleport or save loading.

**Research update:** A read-only Cosmos 7.05 mapping pass on 1 October found
teleporter-selection labels and destination-position settings, but no verified
local successful-arrival callback. The feature remains absent from the public
build. A shared player-position helper also appears in a function with a
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
A negative control opened and closed the teleporter interface without selecting
a destination; it produced no observer event. The candidate call is therefore
not caused by opening or backing out of the interface alone. Whether it marks
destination confirmation, transition start or completed arrival remains open.
A follow-up offline-validated diagnostic build corrects a stale hook-count log
message and has not been installed in the active session.
The separate byte-pattern pass also recorded candidate references to native
teleport state; those hits are not semantic callbacks. See the
[sanitized static XREF record](research/NMS-075-STATIC-XREFS.md).

## Settings menu can stop responding after a UI-thread change

**Observed:** The owner reported that after death the pet was absent and the Companion Auto Summon settings menu was missing. The current 0.10.1 session log recorded `menu_unexpected_thread`, which means the menu safety guard permanently stopped custom menu handling after a callback arrived on a different thread. The log contains no death event, so it does not prove that dying caused the thread change.

**Grouped roster:** One 0.10.1 live check showed the settings entry beside grouped companion rows. That does not cover every roster size, menu rebuild or UI-thread lifecycle.

**Fix status:** A feature-branch change now skips an isolated callback on an unexpected thread and rebinds only at a quiescent menu-builder start. It continues to refuse a handoff during an active builder, append, confirmation or trigger transaction. Twenty-five offline menu fixtures pass. On 30 September 2026, the candidate was installed in the local Steam 7.05 test; its startup log confirmed exact-build acceptance, a verified pre-activation snapshot and activation of twelve game hooks plus the binding guard. The owner then confirmed that the settings menu worked and a pet appeared after loading directly from an expedition into the Space Anomaly. The same session log records a successful local save load, an armed opportunity and an accepted summon queue. This is one successful live scenario; it does not establish recovery after death or reliability across menu rebuilds. Public file 49367 remains unchanged; this candidate is not in the download.

## Other unconfirmed reports

- One direct load into the Space Anomaly had no visible pet while an Anomaly mission was incomplete. Whether mission state mattered, or whether the pet was delayed or overlooked, is unknown.
- A pet disappearing after base removal has been reported, but no causal behavior has been verified. The mod does not automatically respawn pets after manual dismissal or disappearance.

## Reporting

Please include the mod version, exact game build, location, event immediately before the problem, current summon/selection settings, whether a manual summon works, and whether the issue repeats after a normal restart. For menu reports, include whether the list is grouped and whether the menu was opened or rebuilt after death. Share only a short relevant log excerpt with personal paths and identifiers removed. Do not upload save files or private backups.

The [tester handoff](release/TESTER-HANDOFF.md) records the fuller validation history. The [Nexus page](https://www.nexusmods.com/nomanssky/mods/4579) carries the player-facing summary.
