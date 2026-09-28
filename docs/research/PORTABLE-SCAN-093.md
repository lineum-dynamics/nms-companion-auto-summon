# Portable 0.9.3: archive layout repair and reviewable launcher

Recorded 28 September 2026. This is a legitimate packaging correction to the
retained 0.9.2 distribution, not a claim that antivirus detections are false.
The original ZIP, executable and running session remain unchanged.

## Established problem and limits

[Nexus's current quarantine guidance](https://help.nexusmods.com/article/117-why-has-my-mod-been-quarantined),
updated 22 September 2026, explicitly rejects nested mod archives and recommends
extracting their contents. The retained 0.9.2 ZIP contains `runtime/python311.zip`.
That is a concrete package-policy mismatch. It does not establish which check
caused Nexus to quarantine file 49196; that file also has antivirus detections.

The exact 0.9.2 launcher still reports **8/70** in VirusTotal. Its Behavior tab
on 28 September displayed no behavioral detections, dropped files or network
communications, one file/directory-discovery technique and a warning that some
sandboxes were still analyzing. These are limited report observations, not a
clean bill of health; an isolated EXE without its package would fail its own
integrity gate before dispatch. The vendor-specific detection criteria remain
unknown. [Exact report](https://www.virustotal.com/gui/file/a661a4eafbaa38c9c4951adc555f5bab9f39be2f638e860655ee66603c27f5c4/behavior).

[Complete compiled-source comparison](LAUNCHER-IL-AUDIT-092.md) found the retained
EXE identical to one faithful build apart from the independently located COFF
timestamp and module identifier. All 28 methods, metadata and resources match.
This rules out unexplained additional compiled content relative to that source
and build, not vulnerabilities in every dependency or a genuine detection.

## Changes

- Extract all **649** original standard-library members into `Lib/stdlib` and
  point the relative `python311._pth` there. Preserve each `.pyc` byte; do not
  recompile, rename to disguise content, or ship the inner ZIP.
- Record the original ZIP SHA256 and original member path alongside every
  extracted member's hash. Preserve 1,192 other vendor/runtime files unchanged,
  including the native COFF linker library. Keep official locks and licenses.
- Reject distribution archives by supported suffix/signature and complete ZIP
  structure in every final payload before output. This is not a universal file
  format classifier: native object libraries are retained. Reject traversal,
  case aliases, file/directory collisions and oversized expansion before writes.
- Add accurate Windows file identity: product title, Lineum Dynamics and
  **0.9.3.0 / 0.9.3-test**. Use an explicitly named `asInvoker` application
  manifest. The old compiler default already used `asInvoker`; no elevation
  behavior changed. Metadata is reviewability work, not a proven antivirus cure.
- Ship the actual assembly identity, resolved Windows manifest, exact locale
  resource, C# template and compile-only instructions under `app/`. No external
  build-time download is required to review that launcher.
- Fix Steam discovery aborting when an unrelated process denies its name.
  Selection still requires one known Steam process; access failures for the
  selected parent/target and actual-process identity guards remain fatal.
- Use the actual distribution version when naming new backups. No existing
  backup, preference, save, session or live installation is changed.

Production 0.5.1, combined 0.9.2-play-trial and menu 0.9.1-diagnostics remain
byte-identical. Gameplay, summon opportunities, habitat weights and limits are
unchanged. No donation notice or payment destination is added.

## Exact artifact

| Field | Value |
| --- | --- |
| ZIP | `CompanionAutoSummon-0.9.3-test.zip` |
| Files / bytes | 1,897 / 23,534,865 |
| ZIP SHA256 | `d87f868c618aec200cf276aae1faf81748eeaf7be26bd1e21a8594590627e383` |
| EXE SHA256 | `0df7e0930c407ecdb64eba6c79ff7bae535606d9d71932e8342926e6b6120172` |
| EXE bytes | 94,720 |
| Distribution manifest SHA256 | `eecf4602887a189d94558ca5335cfa6d2173ee479747e5fa4366cbdfb20a2078` |
| Runtime manifest SHA256 | `a519455cb9684c73e6d6c472952b8ad9be8820e56a9fa63d15c435a6c0641f77` |
| Original inner stdlib ZIP SHA256 | `7d0f59c930e7d3d9352399ea3c95c0272489b3c09a8e95faaedfa8a23e20e5b1` |
| Local build | `build/portable-093-r1` |

## Validation and current boundary

The frozen developer suite passed **786 tests** in 77.717 seconds, without
failures, errors or skips. Unchanged production retains its 403-test evidence.
All fourteen 63-key catalogs and the exact compatibility profile validate.
There are no changed UI strings or meanings; English/Czech quick starts have
matching version and distribution-status updates. Draft language status remains.

The real embedded interpreter works with the extracted library. Offline host
and owned native-child initialization both pass with all 20 pinned dependencies
and 527 module origins inside the runtime. Unicode relocation, poisoned external
Python paths, System32-only PATH, native imports and the Unicode file adapter
pass without payload mutation, game start, injection or save access. The final
distribution's native import and EXE verification gates also pass.

Evidence: `build/validation/developer-093-final.txt`,
`build/validation/portable-093-build.json`, and
`work/portable-runtime-audit-r5/report.json`. Final ZIP relocation with an
accented/CJK path, poisoned Python environment and System32-only PATH passed
both EXE verify-only and actual-package check-only; all 1,897 files remained
unchanged. No backup was created, and no game was started or attached.
The originating task retains `work/portable-093-relocated-check.json`.

The [independent shipped-recipe build](LAUNCHER-IL-AUDIT-093.md) also passes:
all compiled bytes match except the independently identified timestamp/MVID.
All 28 methods, metadata and resources agree; no compiled input is missing.
That review copy was neither executed nor submitted to a scanner.

## Final Nexus and scan readback

After the owner renewed login, file **49197**, version **0.9.3-test**, and the
updated full description were saved and read back. The page is **Unpublished**;
the file is Miscellaneous with mod-manager downloads OFF. Older files remain.

The new upload finished in **automated quarantine**. The file's VirusTotal link
matches the exact local ZIP SHA256 above. Its report at 16:10:11 local time is
**1/58**, Bkav Pro `W32.Malware.2D7F7A26`; several engines timed out or could
not process the file. The report's `whl` classification tag is recorded without
inferring Nexus causality. [Exact archive report](https://www.virustotal.com/gui/file/d87f868c618aec200cf276aae1faf81748eeaf7be26bd1e21a8594590627e383/detection).

The exact EXE report existed but displayed no per-engine results/denominator,
so its generic no-detections banner is **not** treated as a completed clean
scan. A bounded Relations read of the archive showed individual prior results
for a subset of bundled files, not complete fresh component coverage. Neither
observation explains Bkav's archive detection or identifies a new faulty module.

Removing the nested stdlib archive resolved a concrete packaging mismatch but
did **not** resolve Nexus availability. No successful owner download, 0.9.3 game
test, second-PC or multiplayer success is claimed. The actual quarantine reason
and false-positive status remain unknown. The original 0.9.2 runtime/EXE were
not changed; both original and new EXE hashes were rechecked after the work.

Nexus's published process requires moderator review for quarantine removal.
An [unsent, concrete request](../release/NEXUS-QUARANTINE-REVIEW-DRAFT.md) includes
file IDs, exact hashes, source/build inputs and bounded evidence. No person or
vendor was contacted, no repository visibility was changed and no security
control was disabled. Do not create further scan-only variants or assert that
signing/metadata would necessarily clear the residual detection.

The originating task retains `outputs/nexus-093-quarantine.png` and browser
text snapshots under `work/nexus-093-file-state-final.txt`,
`work/virustotal-093-archive-state.txt` and `work/virustotal-093-relations.txt`.
