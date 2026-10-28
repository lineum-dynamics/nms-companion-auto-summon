# Native release status and promotion gates

Reviewed: 28 October 2026.

## Current label

`0.10.3-native-test` remains **EARLY ALPHA / prerelease**. `native` describes
the C++ implementation; `test` describes its acceptance status. Neither is a
game compatibility label. Game release, Steam build and executable hash must
always be recorded separately from the mod version and source revision.

The final 0.10.3 archive passed the named local startup, load, menu/icon and
base-to-station checks. Earlier port candidates passed clean ship exit and the
reverse teleport. This evidence does not complete the wider gates below.
See [the exact release record](0.10.3-COSMOS-706.md).

The separate **0.10.4-native-test** development candidate repairs a reproduced
library error path and has local/clean-runner offline evidence. It remains
unreleased. Its exact ASI now reports **30/71** in the completed 27 October
21:53:11 UTC VirusTotal reanalysis, superseding the historical17/70 snapshot;
the original 0.10.3 ASI's dated **30/70** report is from07:50:46 UTC. These unresolved results keep the scanner gate open. Exact-package
game acceptance is separate. Candidate ZIP submission was rejected by automatic
approval review after the service warned that the stated inner-file scan would
not run; selecting that ZIP establishes no upload or scan.
Keep the 0.10.3 submission/scan history intact. See the
[guard candidate](0.10.4-QUERY-GUARD.md).

The independent Microsoft source audit and owned bundle also passed on
24 October. Its warning triage and current direct quarantine readback are in
[the investigation](../research/NATIVE-0104-SCAN.md). Compiler/fixture success
does not satisfy the scanner or moderator-review gate. A current
[review request](NEXUS-QUARANTINE-REVIEW-20261027.md) is prepared locally and
unsent. The further 27 October IAT/source audit and public vendor lookup add
attribution evidence but establish no new repair or private detection rule.

The distinct [Microsoft 0.10.5 candidate](../research/NATIVE-0105-MSVC-CANDIDATE.md)
completed an approved exact-file scan with 8/71 Yogi detections at 27 October
21:43:19 UTC. Four fixed diagnostic component libraries completed on 28 October:
all eight Yogi vendors returned Undetected for each; Cynet labelled all four,
including the inert CRT-only control. No private rule or general clearance is
established. A [0.10.6 CRT-thread correction](../research/NATIVE-0106-CRT-THREAD.md)
has a documented engineering reason and separate pending build/scan/game gates.
Neither candidate is a Nexus replacement or a released player archive.
The approved 0.10.6 scan completed on 28 October 08:22:30 UTC: 5/50, 20 timeouts,
one failure. Fresh unchanged 0.10.5 control at 08:29:05 is 10/69, one timeout,
one failure. All 75 rows are preserved for each. On 48 common completed vendors,
both have five detections; three completed Yogi vendors remain positive and
five others time out on 0.10.6. The displayed lower count is not clearance or
an established improvement. See [the complete comparison](../research/NATIVE-0106-VT-EVIDENCE-20261028.json).


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

The owner reaffirmed on 24 October that support/vendor contact is a last resort
after available internal technical analysis. The moderator rule concerns
removal of an existing host quarantine; it does not establish that engineering
analysis is exhausted or make support the current next action. The prepared
review draft stays unsent. Continue concrete bounded technical checks and
record their outcomes before revisiting contact.

Quarantine does not establish that technical analysis is exhausted. Keep a
bounded completed/open audit table: artifact and source provenance, build
environment, systematic static diagnostics, owned-host fault cases, independent
clean-host reproduction and attribution of actual sandbox events. Review each
diagnostic against its real API/integration contract before calling it a bug.
Distinguish a reproduced engineering defect from a demonstrated antivirus rule;
validate a proposed repair separately and retain the submitted bytes. The
23 October MinHook query-error fixture in the scan record is an example of new
evidence obtained after the initial provenance checks. It does not establish
the detector cause or clear Nexus quarantine.

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
- Inspect every remaining Main file, not only the replacement pair. A prior
  release can remain in Main independently: 0.10.1 did so until corrected on
  23 October. Retain superseded releases under Old without changing bytes or
  scan state; keep game-target text explicit. Old files can still expose
  download links. Visible links are not a downloaded-byte readback or clearance.
- Date every scan count and distinguish an accepted reanalysis from a button
  click or an in-progress count. Preserve the earlier observation as history;
  never combine denominators or claim that a reanalysis changes Nexus quarantine.
- Verify current public text and tag choices after saving. Legacy release tags
  and Translation can conflict with an exact-build English-only native alpha.
- In the current SCEditor source field, programmatic fill alone can leave Save
  disabled. Switching view showed the new text but still did not notify the
  form. A real source-field keyboard edit followed by restoring the exact text
  and leaving the field enabled Save. Compare the full source before saving;
  never force-enable the button or assume visible editor text was persisted.
- Preserve the source tag, immutable package receipt and separate publication
  receipt. A successful save/upload is not a successful file download or scan.

## Later exact-file control, 28 October 2026

The unchanged 0.10.6 ASI's later 13:35:26 UTC report is 9/57, 12 timeouts, two
failures and four unsupported. It still has six completed Yogi-positive vendors.
All four separately approved matched inspection/core diagnostics are Yogi-
negative, with one Cynet positive each including their inert baseline. These
results do not close the player scanner/game/Nexus gates. The next fixed
inactive startup/link probes are research only; prior uploads do not approve
new files. Full current evidence is in the research report and its dated tables.

## Inactive startup follow-up, 28 October 2026

All six specifically approved startup diagnostics completed multivendor upload.
No completed row reports Yogi; three full cases have all eight earlier Yogi
vendors Undetected, while the others have timeouts. Cynet remains on all six,
Rising on four; these are not clean files or player replacements. The frozen
full 0.10.6 ASI remains Yogi-positive. See
[the complete dated record](../research/NATIVE-0106-STARTUP-PROBES.md).
The controlled compiler-flag comparison is research only; all release, game
and Nexus gates remain unchanged. No new release label is authorized.
