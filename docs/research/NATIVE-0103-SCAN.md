# Native 0.10.3 distribution and provenance investigation

Reviewed: 23 October 2026. This is a bounded investigation, **not scanner
clearance or a confirmed false-positive finding**. The owner declined support
contact and asked for an internal comparison; no support message was sent.

**Latest scope correction:** technical analysis is not exhausted. A later
same-day systematic pass reproduced an unchecked MinHook API-error path and
validated a minimal offline prototype. This is a pre-existing robustness defect,
not an established detector cause. Production sources and the submitted r4
package remain unchanged; independent clean-host reproduction and sandbox-event
attribution are still open. See the final audit section below.

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

### Earlier interpretation, before the API-error audit

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
the accepted artifact at that stage. The later audit below identifies a
pre-existing error-handling defect without establishing an antivirus connection.
Preserve the bytes and the unresolved verdict; do not
substitute renaming, repeated recompilation or another download channel for
host clearance. Further code changes need a substantiated engineering defect;
actual release availability still needs a cleared file and download readback.

## Audit limits and newly reproduced API-error defect, 23 October 2026

Base revision: `73a9f6e273ebdecbe4d74323b2f1b56cf9cb0b38`, branch
`compat/cosmos-706-25732212`. This work adds analysis and a reusable fixture;
it does not modify native production sources, mappings, the vendored original,
the r4 archive or deployment. It corrects any impression that provenance
verification had exhausted technical analysis. Source correctness, detector
attribution and Nexus quarantine are separate gates.

### Supplemental current build-context audit

Compared the installed file set with all 9,053 original archive members:
9,053 installed, zero extra and zero missing files. Installed config files
are already part of the matched archive. The eighteen inspected compiler
environment override/include/library/config variables were absent or empty
in the current authorized desktop context; no values were recorded or printed.
The historical r4 build environment, external config search locations and a
separate clean-host build remain **NOT CHECKED**. A current-context check
cannot retroactively prove a historical process environment.

Local receipt: `build/release-0103-publication/toolchain-context-audit-20261023.json`.
SHA-256: `fb4dd623a0baa64235c23fcbb26b8c1bd8cfee66cca68b1d502bc28a6551ca92`.
Method: compare relative file-name sets from the prior pinned-archive receipt
with `Path.rglob` regular files; inspect presence/nonempty status, not values,
for `CCC_OVERRIDE_OPTIONS`, `CCC_ADD_ARGS`, `CL`, `_CL_`, `INCLUDE`, `LIB`,
`LIBPATH`, `COMPILER_PATH`, `LIBRARY_PATH`, `CPATH`, `CPLUS_INCLUDE_PATH`,
`C_INCLUDE_PATH`, `OBJC_INCLUDE_PATH`, `RC_INCLUDE_PATH`, `SDKROOT`,
`GCC_EXEC_PREFIX`, `CLANG_CONFIG_FILE_USER_DIR` and
`CLANG_CONFIG_FILE_SYSTEM_DIR`. The receipt preserves the exact queried set.

### Systematic default Clang analyzer pass

Clang 23.1.2 completed all thirteen active translation units: nine runtime
C++ files and the four MinHook C files selected by the player build. All
analysis commands returned zero. Default checkers produced two diagnostics;
this is not an exhaustive security, concurrency or whole-program proof.

- `storage.cpp:45`, dead initialization of `point`: ASCII continues before use;
  every valid multibyte branch overwrites it. This is a redundant initialization,
  not an established memory-safety fault or detector explanation.
- `hook.c:425`, possible null destination in a rollback copy: the modeled path
  assumes null after the patch-above subtraction and assumes VirtualProtect
  succeeds. The CAS caller supplies checked image-base/RVA targets and MinHook
  checks executable addresses before recording hooks. A null patch target was
  not reproduced in CAS. This warning alone does not prove a reachable fault.

Follow-up review of the latter path found the separate API-error issue below.
The Windows contracts were checked against Microsoft's
[VirtualQuery](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualquery)
and [VirtualProtect](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect)
documentation; a failed query does not provide a successful output result.

Output directory: `build/native-security-analysis-20261023`.
Analysis receipt SHA-256:
`d28d7e5f9e01729befff1832e2110c6c0436671cbff1d8c01c5958db640775fd`.
Compiler wrapper remains the pinned
`20ba1856942744291a6aaaf9f2c94f6d0cd7cac5aa9557fce96471dc7ef25d6f`.
Generated catalog/profile/mapping headers matched the prior byte-identical
rebuild. CPython remains 3.11.9 as identified above.

Reproduce per translation unit with the correct C/C++ compiler from the pinned
toolchain; run from a new private output directory and use explicit repository
paths for the following aliases. The receipt preserves all thirteen commands.

```powershell
& $compiler --analyze -O2 -Wall -Wextra -DUNICODE -D_UNICODE -D_WIN32_WINNT=0x0A00 -I $nativeInclude -I $thirdParty -I $minhookInclude -I $r4Generated -Xclang -analyzer-output=plist @unitDefines $source -o $plist
```

For C++ units, `unitDefines` is `-std=c++17 -DCAS_NATIVE_RUNTIME
-DCAS_PROBE_BUILD -DCAS_RESPAWN_OBSERVER -DCAS_TELEPORT_CANDIDATE_TRIAL`;
C units use an empty array. No link, gameplay module execution or game access
was performed by this analyzer pass.

### Reproduced MinHook query-error case and bounded repair prototype

Pinned `native/third_party/minhook/src/buffer.c`, `IsExecutableAddress`, calls
VirtualQuery without checking its return before reading `mi.State/Protect`.
When that call fails, this helper can consume output that has no successful
query contract. This is pre-existing shared dependency code, not a demonstrated
7.06 port regression or antivirus signature explanation.

The owned fixture
[`tools/research/minhook_query_failure_host.cpp`](../../tools/research/minhook_query_failure_host.cpp)
includes unchanged upstream `buffer.c` and substitutes only its query call.
It uses a constant mock address and performs no real page query or patch.
Three cases distinguish failed-query handling from ordinary executable-page
classification:

| Query case | Expected executable | Original helper | Guard prototype |
| --- | --- | --- | --- |
| Failure with executable-looking stale output | false | **true: reproduced failure** | false |
| Success, committed executable/read | true | true | true |
| Success, committed read/write | false | false | false |

Baseline exits 1 with exactly the first case failing. The prototype exits 0.
This proves the helper's error-contract defect in the injected-fault scenario;
it does not prove that Windows hit this failure in NMS or that a scanner uses
it as a detection rule. The shipped CAS path's existing valid-target checks
remain relevant to reachability.

The minimal prototype replaces the unchecked query with:

```c
if (VirtualQuery(pAddress, &mi, sizeof(mi)) != sizeof(mi))
    return FALSE;
```

It exists only in `build/native-security-analysis-20261023/query-guard-prototype-r2/buffer.c`.
The first prototype used aggregate zero initialization and failed the C++
fixture's `-Wextra -Werror` field-initializer warning. That is a build/tool
failure, not a behavioral result. r2 checks the return before any output read;
the ordinary success cases remain unchanged. The vendored original is untouched.

Committed LF fixture source SHA-256:
`4124e7f87bde52b7b8f07d7066a9ec5ffaa7945264e1fd80b600aa4d7d2ff046`.
The originally executed Windows-text copy SHA-256 is
`02d0ed98301d56c42dcb35e20ee90d3d70b5e880fa61d3d15d8ae4054f04d907`.
Their decoded C++ contents are identical after line-ending normalization;
the original receipts retain the actually executed copy's hash.
Baseline receipt SHA-256:
`72bcfe497040e6a3affd7af7463fe345b7cbcd36ea54d2e6cb1c68f8ea6b9c14`.
r2 modified buffer source SHA-256:
`f6b1036d59316db806e0b16a6592c60f6f199b7289434968764816cc886ee3a5`.
r2 receipt SHA-256:
`ef3131003d11525b215e4dd818b189acfa205b5b804f4fb0816bdeaa48cbf0ef`.

Reproduce the baseline with the unchanged vendored source include directory;
prepend the prototype directory to the include paths for the guard case.
Keep output binaries in a new build directory. The fixture deliberately exits
1 against the unguarded source; do not count that as an unexplained tooling
failure or add it to the production suite without its expected-baseline policy.

```powershell
& $cxx -std=c++17 -O2 -Wall -Wextra -Werror -static -I $minhookSource $fixture '-Wl,--no-insert-timestamp,--dynamicbase,--nxcompat' -o $ownedHost
& $ownedHost
```

### Remaining bounded analysis gates

| Gate | Current evidence / next discriminator |
| --- | --- |
| Query-error repair integration | Offline three-case prototype only. Before a changed player artifact, preserve upstream/local-patch provenance and licenses; exercise the real C build and owned-hook/runtime regression checks. No new game mapping is inferred from this helper test. |
| Independent clean-host reproduction | NOT CHECKED. Reproduce frozen r4 source and pinned toolchain in a separate clean Windows environment, compare the artifact and selected inputs, explain any difference before publishing. Same-PC reproduction is already complete. No clean CI workflow is configured in this checkout. |
| Sandbox event attribution | PARTIAL. Harness hosts and memory-pattern URLs were explained, but the UDP observation lacks module/call-chain attribution. Inspect available per-process report evidence; if absent, record that limit rather than rerunning generic tag summaries. |
| Detector-rule explanation | Unresolved. Neither the API defect nor a static analyzer diagnostic identifies the private antivirus rule. Vendor analysis may still be needed. |
| Host distribution acceptance | File 50040 remains quarantined in the last direct readback. Technical audit progress does not establish host clearance; contact is still declined and unperformed. |

No changed player package was built, deployed, uploaded or rescanned in this
pass. Native UI text and localization meanings are unchanged. Current exact
7.06 mapping and bounded game acceptance remain as previously recorded;
multiplayer, second PC and broader lifecycle/location acceptance remain open.

## Guard integration candidate, 23 October 2026

Source base `760f74db2a5fbc709d4103304efa917a55c4a98f`, branch
`fix/native-query-guard`. Distinct mod candidate **0.10.4-native-test** retains
exact game 7.06 / 25732212. Rehashed installed executable: 88,560,712 bytes,
SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
No game process was observed in the preparatory check; no deployment occurred.

The production C delta is the same minimal return-size guard proven by the
prototype. The LF vendored file is 9,854 bytes, SHA-256
`3a9b2f7a1fb084e72897acd8095d4325ab03545669b5b43d89d13ea71d113035`.
The earlier CRLF prototype hash differs because the line endings differ.
`tools/validate_native_dependencies.py` verifies 29 retained source/notice files
and reverses the exact patch to the pinned 9,814-byte original hash. The lock
and packaged notices declare the local modification; BSD/HDE notices are intact.
Twelve new provenance tests reject tampered files/notices, wrong original hash,
undeclared/extra changes, absent guard, duplicate and escaping paths.

Local first candidate build: `build/native-runtime-0104-query-guard-r1`.
Compiler wrapper unchanged. Build receipt SHA-256
`e2b32cb1cac41c175b8d76e7f8ba4cfac9399914157dc8107e18f812b9e76f1e`.
ASI: 2,639,360 bytes, SHA-256
`765cdbdf0e99aea433fd977048b38f0cd28ccbe6c26902c511310a3ee9523ffa`.
88 source inputs: three added (C fixture, patch notes, dependency validator),
six changed (lock, notice index, native/player READMEs, buffer.c and builder),
zero removed. All nine production C++ files, other MinHook C files, native
mapping/profile inputs and locale values are unchanged from frozen r4.

Completed: 403 production and 820 developer tests; sixteen real-C query cases;
ten owned-hook ABI groups; 28 menu scenarios with exact binding-filter parity.
The first bundle pass also passed policy 31,216/88 traces, selection 25,733/59
traces, storage 333 cases/721 operations and runtime 63 cases. Backup validation
stopped before its first completed check: `Cannot hold backup directory
(Windows error 32)`. The backup driver hash and backup source are byte-identical
to frozen r4; this is not evidence that the MinHook change caused the refusal.
Preserve the failed report and make one fresh isolated attempt to distinguish
a transient sharing conflict. Never remove locking or weaken snapshot rules.

A bounded clean Windows workflow now builds frozen source
`852c5c55458c563a8564090dd31305864483edf3` and the candidate on separate
Windows-2022 jobs. Official actions are commit-pinned; the 190,725,905-byte
compiler archive requires SHA-256
`e3ad77d117a4bea19a7a3b333341824d79a5a371004a10e25b8504e7b3047666`.
Only JSON evidence is retained, without binary publication, game access, cached
build inputs or private credentials. Run/readback pending at this checkpoint.
Any byte difference must be explained before a reproduction claim.

Mapping cache: the game's hash, native game consumers, 90 role entries and
mapping/profile hashes remain unchanged. This library error-path change needs
C/owned-hook regression evidence, not invented replacement RVAs. No new game
build compatibility or live acceptance is inferred. Candidate archive, exact
new-artifact game trial and scan review remain pending. The immutable 0.10.3
Nexus/GitHub status is unchanged; no support contact or rescan was performed.
