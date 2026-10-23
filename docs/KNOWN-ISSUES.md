# Known issues

Status reviewed: **23 October 2026**.

Latest uploaded mod: **0.10.3-native-test**, Nexus file **50040**, Main / Primary.
**Nexus quarantine blocks its download.** The exact ZIP is 3,725,947 bytes,
SHA-256 `df7cf87276391a9dc9bdf596611563b3787530da5d5c0107f51bb994f580b3f2`.

Supported target: Windows 10/11 x64, Steam **Cosmos 7.06 / build 25732212**,
NMS.exe SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
Unknown executable builds refuse activation before gameplay hooks. Retained
0.10.2 / file 49469 targets 7.05 / Steam 25624745 only.

Reports are observations, not proof of suspected causes. A source change is
not a public fix until the exact distributed artifact is validated and accepted.

## Distribution blocked by Nexus quarantine

**Observed:** Nexus accepted the 0.10.3 upload and displays it as Main / Primary,
but automated checks quarantine file 50040. The exact ZIP report shows 10/67
(23 October, 09:06 UTC); a later ASI reanalysis shows 15/63
(23 October, 14:33 UTC), superseding its earlier 10/71 snapshot.
The older unchanged 0.10.2 ZIP now
shows 28/68 in its 15 October analysis and is blocked by local Windows
protection. The earlier 1/67 and Nexus acceptance were historical snapshots.
The unchanged 0.10.1 ZIP also shows 22/60 in its 15 October analysis. Nexus
still displays download links for the older files; no new download-byte
verification was attempted. Their acceptance is not current scanner clearance.

**Investigation:** same compiler, vendored inputs and loader as 0.10.2; the new
ASI matches the frozen receipt and an independent rebuild byte for byte.
All 9,053 installed toolchain files match the original official archive;
GitHub's current release-asset digest matches the recorded archive pin.
No exact detector cause or confirmed false positive is established. Support
has not been contacted, as requested by the owner. Do not disable protection
or describe a different download channel as scanner clearance.
See [the scan/provenance record](research/NATIVE-0103-SCAN.md).

**Listing correction:** 0.10.2 moved to Old files when replaced by 0.10.3;
0.10.1 had been left in Main. File 49367 was moved to Old on 23 October and
the public categories were read back. This metadata correction does not
resolve quarantine or make either 7.05 package compatible with 7.06.

## Experimental teleport: local success, multiplayer unverified

The final 0.10.3 archive passed a clean base-to-station test: after manual
dismissal, a distinct opportunity and accepted queue were logged and the owner
confirmed a newly visible companion. An earlier 7.06 candidate passed the
reverse station-to-base route. An r2 trip had no pet or recorded callback;
its cause remains unproven and the miss is retained in the release history.

These are bounded local observations. The callback's exact game-level meaning,
completed-arrival semantics and remote-player isolation remain unverified.
The controlled two-player check is still required: one player stays stationary
while the other teleports, then roles swap, observing both screens independently.
The master automation switch and destination settings remain authoritative.
Turn Automatic summoning OFF if unwanted behavior occurs. No general teleport
or multiplayer-safe claim is made.

## No separate automatic death/respawn trigger

Death/respawn is unimplemented as its own trigger. The exact local-load caller
excludes the known distinct DeathState caller; shared movement helpers are not
proof of a completed respawn. Manual dismissal or disappearance after base
removal does not itself create another automatic opportunity. A future respawn
feature requires its own completed local event and ordinary eligibility checks.

## Menu recovery after death or other rebuilds remains unverified

An earlier 0.10.1 report described a missing pet and settings menu after death.
Its log recorded a callback-thread safety stop but no death event; causation
is unknown. The recovery candidate skips an isolated foreign-thread callback
and allows rebinding only at a quiescent builder start, refusing active
transactions. Earlier grouped-roster and direct-load scenarios succeeded.

The final 0.10.3 archive displayed its settings and icons correctly, and the
unchanged menu inputs passed 28 offline scenarios. This does not establish
recovery after death or reliability through every roster/rebuild lifecycle.
Normal restart remains the practical recovery for a stopped session; do not
try to override the runtime safety stop.

## Other scope and reports

- One historical direct Space Anomaly load had no visible pet during an
  incomplete mission. A causal link to mission state has not been established.
- Broad location/mod coverage, second-PC installation, all selection/control
  combinations and long-session acceptance remain open.
- Underwater summoning and freighter support are not added. Native restrictions
  remain in force. In-game menu/HUD currently use English; maintained catalogs
  do not establish finished runtime localization.

## Corrected before the 0.10.3 upload

The initial 7.06 candidate rejected a valid save-load callback because a new
applied-FSM check ran before that state was applied. r2 diagnostics measured
this timing. The corrected exact caller/receiver/vtable policy passed r3 and
the final r4 archive, with visible save-load appearance. This was a development
candidate failure; it is not an assertion that public 0.10.2 had the same bug.
See [the exact release record](release/0.10.3-COSMOS-706.md).

## Reporting and history

Include exact mod/game identity, location, preceding event, selection/Shuffle
and automation settings, whether a manual summon works, visible result and
repeatability after normal restart. For menu reports, mention grouped rows and
whether the page was rebuilt after death. Share only a short sanitized excerpt
or screenshot; never upload saves, private backups, credentials or whole logs.

The [tester handoff](release/TESTER-HANDOFF.md),
[retained 0.10.2 issue record](release/KNOWN-ISSUES-0102.md) and
[teleport/respawn research](research/TELEPORT-AND-GROUPED-MENU.md) preserve
version-scoped history. [README](../README.md) and the
[Nexus page](https://www.nexusmods.com/nomanssky/mods/4579) mirror the current scope.
