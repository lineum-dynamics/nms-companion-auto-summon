# Known issues

Status reviewed: 1 October 2026  
Public mod build: **0.10.1-native-test**, Nexus file **49367**  
Supported game target: Windows x64, Steam Cosmos 7.05 / build 25624745, exact executable hash in the release package.

This page tracks reports against the current public build. A reported symptom is not proof of its suspected cause. Work-in-progress branch changes are not fixes for players until they are validated, packaged and released.

## No automatic summon after teleport or death

**Observed/current behavior:** 0.10.1 creates automatic opportunities after a successful local save load or ship exit. It has no verified trigger for teleport arrival or death/respawn, so neither event by itself requests a pet. No game eligibility or placement rule is bypassed.

**Status:** Open. Teleport arrival needs a verified local completion callback. A
1 October 2026 static pass of the exact Cosmos 7.05 executable found multiple
RIP-relative candidate references to teleport state and single candidates for
`Teleporting` and the `gcpersonalteleporter.cpp` marker. These are not yet
decoded or verified as the successful local completion event. A death/respawn
trigger needs a separate exact-build event and safety review; it is not assumed
to be the same event as teleport or save loading. See
[the static XREF record](research/NMS-075-STATIC-XREFS.md).

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
