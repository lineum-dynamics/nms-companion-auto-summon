# Native release status and promotion gates

Reviewed: 23 October 2026.

## Current label

`0.10.3-native-test` remains **EARLY ALPHA / prerelease**. `native` describes
the C++ implementation; `test` describes its acceptance status. Neither is a
game compatibility label. Game release, Steam build and executable hash must
always be recorded separately from the mod version and source revision.

The final 0.10.3 archive passed the named local startup, load, menu/icon and
base-to-station checks. Earlier port candidates passed clean ship exit and the
reverse teleport. This evidence does not complete the wider gates below.
See [the exact release record](0.10.3-COSMOS-706.md).

## Evidence required before dropping the test label

For a future, newly versioned artifact, record an explicit result and evidence
for every gate. An unsupported feature need not be implemented to release;
its absence and scope must be stated consistently.

| Gate | Required evidence |
| --- | --- |
| Exact package | Source commit and public archive hashes; complete allowlist, licenses and independent archive readback |
| Installation and upgrade | Clean installation on a second Windows/Steam PC; normal upgrade preserving existing OFF choices, preferences and favourites; owned-file uninstall |
| Core runtime | Fresh load, normal exit/restart and ship exit; visible outcomes on supported planets, stations and the Anomaly; blocked placement and manual dismissal do not bypass native rules |
| Controls and selection | Master/location OFF controls, all three selection modes and Shuffle checked against their documented behavior; supported input methods and menu reopen/rebuild checks |
| Lifecycle | A documented normal play session spanning load, ship use, teleport and menu rebuild; no unresolved critical crash, unsafe-state or data-loss report; death menu recovery checked separately from any future respawn trigger |
| Multiplayer scope | If experimental teleport remains enabled in the distributed runtime, verify the moving-player/stationary-partner control in both directions; record visibility and isolation on both screens |
| Distribution | Current file review accepted by the host and download bytes checked; unresolved antivirus detections investigated without calling them confirmed false positives |
| Description consistency | README, Nexus summary/full description, canonical Known Issues, release notes and tester handoff all describe the same exact artifact, verified scope and remaining limitations |

Do not remove the suffix automatically because a game update was ported or
offline tests passed. Record the promotion decision against the completed
matrix. Publish a new version and preserve the old filename, hash, tag and
receipts; never relabel or replace the bytes of an accepted test artifact.

## Quarantine handling

For a quarantined artifact, preserve the exact bytes, record the Nexus file ID
and exact linked scan, and prepare a source/build-backed review request.
Contacting support requires explicit user authorization. Do not repeatedly
rename/rebuild files to change scan results, weaken security settings, suggest
antivirus exclusions or present an alternate binary download as scanner
clearance. Public descriptions must say when the upload is not downloadable.

## Reusable publication checks

- Resolve the exact archive hash/size, Nexus mod ID and GitHub repository before
  the consequential upload. Reuse explicit owner authorization for that same
  artifact and destination; ask again only when required or materially changed.
- In the Nexus update form, choose the correct existing file before editing
  its inherited metadata. A selected archive alone can leave details disabled.
  Inspect the form state instead of uploading a duplicate.
- Set the full package version explicitly and verify Main / Primary. Read back
  the old file's retained category/history; in the 0.10.3 update Nexus moved
  0.10.2 to Old files even with the Archive checkbox unchecked.
- Verify current public text and tag choices after saving. Legacy release tags
  and Translation can conflict with an exact-build English-only native alpha.
- Preserve the source tag, immutable package receipt and separate publication
  receipt. A successful save/upload is not a successful file download or scan.
