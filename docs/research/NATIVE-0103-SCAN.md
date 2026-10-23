# Native 0.10.3 distribution and provenance investigation

Reviewed: 23 October 2026. This is a bounded investigation, **not scanner
clearance or a confirmed false-positive finding**. The owner declined support
contact and asked for an internal comparison; no support message was sent.

## Exact artifacts and observations

| Artifact | Identity and current observation |
| --- | --- |
| New ZIP | 0.10.3-native-test, 3,725,947 bytes; SHA-256 `df7cf87276391a9dc9bdf596611563b3787530da5d5c0107f51bb994f580b3f2` |
| New native ASI | 2,639,360 bytes; SHA-256 `6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652` |
| New Nexus file | **50040**, Main / Primary, uploaded 23 October 2026 at 11:05 CEST; public Files page shows automated quarantine and no file download |
| New ZIP scan | **10/67**, analysis 23 October 2026 at 09:06:05 UTC |
| New ASI scan | **10/71**, analysis 23 October 2026 at 09:09:51 UTC |
| Retained ZIP | 0.10.2-native-test, known 3,724,342 bytes; SHA-256 `e8cbffbf558476025bde0c4b619a460265325d73ecbf99fc77b04c176d5f6704`, Nexus file 49469 retained under Old files |
| Retained ZIP current scan | **28/68**, analysis **15 October 2026 at 13:13:12 UTC**, read on 23 October. This supersedes the 3 October snapshot of 1/67; it does not rewrite that historical observation |
| Pinned loader | Unchanged official UAL 9.7.4 bytes, SHA-256 `fa266e3513d02c08a1b808f28c10538a489eaffaa4b0707f7cc1066e71b5afd7`; new ZIP's relation page showed 0/49 with an earlier 22 October analysis date |

Sources: [new ZIP report](https://www.virustotal.com/gui/file/df7cf87276391a9dc9bdf596611563b3787530da5d5c0107f51bb994f580b3f2),
[new ASI report](https://www.virustotal.com/gui/file/6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652),
[retained ZIP report](https://www.virustotal.com/gui/file/e8cbffbf558476025bde0c4b619a460265325d73ecbf99fc77b04c176d5f6704),
[Nexus Files](https://www.nexusmods.com/nomanssky/mods/4579?tab=files).
Counts and verdicts are dated service observations and can change.

The new reports include AhnLab `Trojan/Win.Loader.C5957161`, ALYac,
BitDefender, eScan, GData and VIPRE `Gen:Variant.Yogi.92012`, Arcabit
`Trojan.Yogi.D1676C`, CTX `Zip.unknown.yogi` / `Dll.unknown.yogi`, Emsisoft
`Gen:Variant.Yogi.92012 (B)`, and Kaspersky `VHO:Trojan.Win32.LOADER.gen`.
Several matching labels also occur in the retained package's current report.
These names do not identify the exact source construct responsible.

## Internal comparison

Compared the exact r4 build receipt against the preserved 0.10.2
`native-runtime-0102-cosmos705-multiplayer-en-only-r2` receipt:

- Same clang 23.1.2 / LLVM-MinGW 20260922 toolchain; compiler SHA-256
  `20ba1856942744291a6aaaf9f2c94f6d0cd7cac5aa9557fce96471dc7ef25d6f`.
- Same dependency lock and all recorded `native/third_party/` and
  `native/licenses/` input hashes. No changed vendored dependency.
- Same eighteen imported DLL names. The native source delta adds no network,
  payload download, remote process creation or persistence-registration API.
  This is a reviewed delta, not a complete malware-proof claim.
- The new ASI is **2,048 bytes larger** than the recorded old ASI. The native
  changes are mapping selection, exact load-context checks, bounded logging
  and corrected three-slot label forwarding. Existing own-process memory
  reading/writing and MinHook integration predate this port.
- New archive still has 29 allowlisted members and no nested archive. ASI and
  loader match the frozen receipts/lock. PE inspection shows ASLR, DEP and
  high-entropy VA enabled, without a writable/executable image section.
- The 647,168-byte PE overlay begins exactly at the COFF symbol table. Its
  10,836 symbols and string table end at byte 2,639,073, followed by 287 bytes
  of alignment padding. This identifies compiler/linker metadata; it is not a
  finding of a separate executable payload or a detector explanation.

`tools/audit_native_archives.py` records imports, exports, sections, archive
members and receipt comparison without executing either artifact. Its bounded
receipt-only-old mode explicitly marks old binary comparison **NOT CHECKED**.
Tool SHA-256:
`1e8caca258913e9a92e0f6a80e44f77ae822f00302305333e70fe5b6f0725e82`.
The local audit JSON SHA-256 is
`1eddd1f7dbc10a666175d91fd183323fee06e563265c4372f6758f830493df50`.

## Failed old-archive read and correction

The first comparison failed before ZIP/PE decoding: Python returned
`OSError: [Errno 22] Invalid argument` on the retained 0.10.2 ZIP. This is a
**TOOL ERROR / blocked input**, not zero matches or an archive mismatch.
PowerShell's independent hash read then reported that Windows blocked the
same file as a virus or potentially unwanted application.

Read-only Defender records for this mod showed `Trojan:Win32/Suschil!rfn`
and successful protection action at 09:17:50 UTC. No unrelated detection,
private resource path or account identifier was published. No file was restored
or read through another copy, and no protection or exclusion was changed.

The interpreter was explicitly rechecked: CPython 3.11.9, pefile 2024.8.26.
The comparison continued using the available old build receipt and the new
archive; old ZIP/PE bytes remain **NOT CHECKED** in this audit.

## Independent identical rebuild

Rebuilt the unchanged final source inputs in a fresh output directory with the
same pinned compiler and `--teleport-candidate-trial`. The resulting ASI is
**byte-identical** to the final submitted module:

`6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652`.

This corroborates the source-to-artifact chain; it does not establish scanner
clearance. No changed candidate was packaged, deployed or uploaded as a scan
experiment. The original published ZIP and receipts remain unchanged.
All products, not only the ASI, matched the original r4 build. The new build
receipt SHA-256 is
`4e8d132e64c8244da7f7e717c1e3c38387001e264bb3dcbb877da42dab1fe18a`.

Reproducible commands use privately resolved aliases for the exact Python,
compiler and old receipt; the input identities above define this pass:

```powershell
& $python -B tools/audit_native_archives.py --new-zip dist/CompanionAutoSummon-0.10.3-native-test.zip --old-receipt $oldReceipt --new-receipt build/native-runtime-0103-cosmos706-r4/build-receipt.json --output build/release-0103-publication/archive-audit.json
& $python -B tools/build_native_runtime.py --toolchain $toolchain --output build/native-runtime-0103-provenance-20261023 --teleport-candidate-trial
```

## Current interpretation and next action

### Sandbox reading, later 23 October follow-up

The exact ASI Behavior page was read without uploading or requesting a rerun.
Its grouped Activity Summary reports no sandbox detections, dropped files,
IDS or Sigma match, and one UDP port-53 observation. Low/information labels
and capabilities are still present; the ten antivirus verdicts remain unchanged.
Absence in that bounded summary is not clearance.

The displayed processes load `attachment.dll` through `loaddll64` and
`rundll32`, including its `CasInspectHost`, `CasRuntimeStatus` and
`InitializeASI` exports. This is not an NMS session. The source's exact-host
guard refuses those hosts before native game hooks; the existing unsupported
owned-host runs cover that refusal separately. Do not treat the sandbox's
process launch list as proof that our code launched those harness processes.

Two entries are explicitly **Memory Pattern Urls**, not HTTP traffic:

- The Visual C++ redistributable URL occurs in `.rdata` and is an existing
  translated launcher-help string in `locales/en.json` and the other catalogs.
  `tools/generate_native_catalog.py` includes those catalog values. This does
  not establish that the native module downloads or executes a redistributable.
- The LLVM GitHub URL occurs in compiler/debug metadata sections. Its presence
  is not evidence of a GitHub connection or payload download.

Actual memory-pattern locations and the imported API list were inspected
against the frozen ASI. These observations explain some visible report text,
not the detector's exact rule. No precise attribution of the sandbox's UDP
traffic to our module was established. The remaining cause is unresolved.

### Interpretation

The premise "the old file passed, only the new port is detected" is not
supported by current evidence: the old unchanged ZIP now has more detections
and is also blocked locally. The new build has reproducible provenance and no
identified added dependency or unexplained payload. **No exact detector cause
or verified source defect has been established.** Do not call the issue fixed,
claim the detections false, or infer safety from a lower count.

Next internal work must identify a concrete unintended source/build behavior
or packaging defect with evidence before changing the artifact. If none is
found, only the host/vendor can change its own verdict; a successful local
build does not clear Nexus quarantine. The support draft remains unsent at the
owner's request. Maintain the accurate download status and preserve all hashes.
