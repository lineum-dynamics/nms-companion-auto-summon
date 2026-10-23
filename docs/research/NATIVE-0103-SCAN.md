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
| New ASI scan | Earlier **10/71**, 23 October 2026 09:09:51 UTC; unchanged-file reanalysis **15/63**, 23 October 2026 14:33:20 UTC |
| Retained ZIP | 0.10.2-native-test, known 3,724,342 bytes; SHA-256 `e8cbffbf558476025bde0c4b619a460265325d73ecbf99fc77b04c176d5f6704`, Nexus file 49469 retained under Old files |
| Retained ZIP current scan | **28/68**, analysis **15 October 2026 at 13:13:12 UTC**, read on 23 October. This supersedes the 3 October snapshot of 1/67; it does not rewrite that historical observation |
| Retained 0.10.1 ZIP | SHA-256 `51cf81c7cc48e835a1f9f14f96ced93d2a32b56200c5c079e23f2b0f17331116`; **22/60**, analysis **15 October 2026 at 11:37:05 UTC**, read 23 October |
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

## Older release, toolchain and unchanged-file reanalysis, 23 October 2026

### Listing categories are separate from scanner acceptance

Public Files readback initially showed 50040 / 0.10.3 and 49367 / 0.10.1 in
Main, with 49469 / 0.10.2 in Old. The 0.10.3 update form replaced 0.10.2 and
automatically moved that replaced file to Old; the independently retained
0.10.1 Main entry was an overlooked listing inconsistency. On 23 October,
49367 was changed through Edit -> File category -> Old -> Save file.
Public readback then showed only 50040 in Main, and 49469, 49367 and 49202 in
Old. Both 0.10.2 and 0.10.1 still expose manual download links. No binary was
downloaded, removed, restored or changed in this pass. Visible links are not
a downloaded-byte readback, scanner clearance or 7.06 compatibility.

The exact 0.10.1 ZIP report, reached through its own Nexus icon, shows 22/60
with analysis 15 October 11:37:05 UTC. It includes the same AhnLab
`Trojan/Win.Loader.C5957161` label, plus other generic labels. A reanalysis
button attempt did not produce a new date or analysis; do not call it a fresh
scan. The report's generated Code insights description incorrectly says the
package has no executable code; it is not authoritative evidence about the
known native ASI/loader payload.

Sources: [0.10.1 report](https://www.virustotal.com/gui/file/51cf81c7cc48e835a1f9f14f96ced93d2a32b56200c5c079e23f2b0f17331116),
[Nexus Files](https://www.nexusmods.com/nomanssky/mods/4579?tab=files).
No evidence now supports treating either accepted 7.05 release as a clean
current control. Counts from different dates and engine sets are not a
controlled regression experiment.

### Additional source and dependency audit

Reviewed initialization/rollback, exported host inspection, generated binding
code, MinHook patching and storage/backup file operations. The actual-host
hash/PE/name guard precedes gameplay access; native DllMain is inert and
InitializeASI creates only its one own-process initializer. The custom binding
code is prepared RW, made RX and checked for RX plus exact bytes before use.
Vendored MinHook uses RWX trampoline blocks and a temporary writable patch
window as part of its ordinary implementation. These are understood hooking
operations, not an identified added payload or an exact antivirus rule.
No modified hook implementation was produced as a scan experiment.

Compared source revisions 9460855250db58086ebd56ccbe0b71035bf66ee9 (0.10.1)
and 48b67e1160ac935df1841a193d92610e5a8dc8cd (0.10.2). The relevant delta is
the bounded teleport observer/trigger and quiescent menu-thread handoff.
The vendored sources, dependency lock and toolchain lock have no diff.
No new network/download/remote-process/persistence API was found in that
delta. This audit did not establish a concrete source defect or the detector
cause; it is not a comprehensive malware-proof claim.

Reproducible source commands:

```powershell
git diff 9460855250db58086ebd56ccbe0b71035bf66ee9 48b67e1160ac935df1841a193d92610e5a8dc8cd -- native/src native/include tools/build_native_runtime.py
git diff --name-only 9460855250db58086ebd56ccbe0b71035bf66ee9 48b67e1160ac935df1841a193d92610e5a8dc8cd -- native/third_party native/dependencies-lock.json native/toolchain-lock.json
```

### Full installed toolchain comparison

GitHub's release API returned the official 20260922 x64 UCRT asset size
190,725,905 and digest
`e3ad77d117a4bea19a7a3b333341824d79a5a371004a10e25b8504e7b3047666`,
matching `native/toolchain-lock.json` and the retained original archive.
Streaming SHA-256 comparison of **all 9,053 regular archive members** against
their corresponding installed files passed. No extraction, compiler execution,
installation, game access or protection change occurred. Extra installed files,
the global environment and independent binary-to-upstream-source rebuilding
were **NOT CHECKED** by this comparison.

Tools: CPython 3.11.9, standard-library hashlib/zipfile/pathlib/json;
interpreter SHA-256
`5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec`.
The local complete relative-member/hash receipt is
`build/release-0103-publication/toolchain-provenance-audit.json`, SHA-256
`713d2aa6d2ec398ea1834b013c2778963f0bbc0f3a4a23e5df91f49aef55bacd`.
It confirms the installation matches this official archive; it does not
establish antivirus clearance or audit the operating system.

Upstream metadata command:

```powershell
gh api repos/mstorsjo/llvm-mingw/releases/tags/20260922 --jq '.assets[] | select(.name == "llvm-mingw-20260922-ucrt-x86_64.zip") | {name, size, digest, browser_download_url}'
```

The comparison used the following standard-library algorithm, after hashing
the complete ZIP and checking its size against the lock. `archive` is the
original official ZIP and `installed` its extracted directory. Absolute
developer paths remain private. Each result records relative path, original
size/hash, installed hash and equality; the receipt above retains every row.

```python
def sha(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(chunk)
    return h.hexdigest()

with zipfile.ZipFile(archive) as z:
    for member in z.infolist():
        if member.is_dir():
            continue
        parts = PurePosixPath(member.filename).parts
        if len(parts) < 2 or parts[0] != installed.name or ".." in parts:
            raise ValueError("Unexpected original archive member path")
        local = installed.joinpath(*parts[1:])
        with z.open(member) as stream:
            original = sha(stream)
        with local.open("rb") as stream:
            current = sha(stream)
        assert original == current, str(PurePosixPath(*parts[1:]))
```

### Reanalysis and the remaining host gate

The same unchanged 0.10.3 ASI was submitted through its existing report's
Reanalyze action; no file was uploaded or rebuilt. Queue/in-progress states
were observed separately from completion. The completed report now shows
**15/63**, analysis **23 October 2026 14:33:20 UTC**, superseding 10/71 at
09:09:51. The original ten labels persist; additional verdicts include
Microsoft `Trojan:Win32/Wacatac.B!ml`, McAfee `Ti!6474247C07E7`,
Palo Alto `Generic.ml`, Sophos `Mal/Generic-S` and TrendMicro-HouseCall
`TROJ_GEN.R002H09JN26`. The ZIP was not reanalysed; its separate dated
09:06:05 observation remains 10/67. Do not combine these counts or imply that
reanalysis cleared Nexus. File 50040 remains quarantined.

[Nexus's current official quarantine procedure](https://help.nexusmods.com/article/117-why-has-my-mod-been-quarantined)
(updated 19 October, read 23 October) says an already quarantined file needs
moderator review for removal from quarantine. It documents remedies for archive
format/nested/password defects, none found in this exact allowlisted ZIP.
No owner-side control was found in the file editor to clear this verdict.
The owner has declined support contact, so that action remains unperformed.
No new local source/build defect was demonstrated that would justify changing
the accepted artifact. Preserve the bytes and the unresolved verdict; do not
substitute renaming, repeated recompilation or another download channel for
host clearance. Further code changes need a substantiated engineering defect;
actual release availability still needs a cleared file and download readback.
