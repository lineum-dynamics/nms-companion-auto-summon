# Native detection attribution, 24 October 2026

Priority: the owner requests resolution of antivirus detections and Nexus
publication. Backup work is parked separately on fix/native-backup-volume-root
at c23b417. Current branch research/native-antivirus-attribution starts from
frozen query-guard checkpoint a55a362. No backup prototype is in this work.
The initial desktop/app/browser restriction was later superseded by conditional
owner authorization; see the dated readback below. No vendor/support contact
is authorized; no security exclusion or protection change is permitted.

## Exact artifacts

Game target: Windows/Steam Cosmos 7.06 / 25732212 / SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
Frozen mod candidate 0.10.4-native-test:
- ZIP: 3,726,390 bytes, SHA-256
  `70d85b240e90b8bafa524036bd4fccc7f58684d10bc93b13c2d0369e6e8d1c39`.
- ASI: 2,639,360 bytes, SHA-256
  `765cdbdf0e99aea433fd977048b38f0cd28ccbe6c26902c511310a3ee9523ffa`.

These were rehashed unchanged on 24 October. The separate submitted 0.10.3
Nexus file50040 and its dated reports are preserved in NATIVE-0103-SCAN.md.
No new-artifact scan result is available. Both new hashes returned Item not
found before manual attempts; reCAPTCHA then failed repeatedly. The owner
reports five failed challenges. Stop that optional route; a selected file,
Uploading 0%, or completed local hashing is not server acceptance or clearance.
The ZIP UI warns that its 3 MB/multiple-member condition prevents its stated
inner-file scan; no archive transformation was made to evade that condition.

## Primary-source audit and interpretation limits

Nexus's current policy says a failed security check quarantines a file until a
moderator review. It separately lists archive parsing, suspicious file types,
scan detections, nested archives and password protection. Our explicit normal
ZIP has 29 members, no nested archive and completed independent readback. That
bounds archive-structure explanations; it does not establish a private host
rule or remove actual detections.

https://help.nexusmods.com/article/117-why-has-my-mod-been-quarantined

The LLVM-MinGW owner called the reported **20241030 i686 libunwind.dll** alert
in issue466 a false positive. That is a different file, architecture and
compiler release; it does not classify this 20260922 x64 statically linked mod.
Issue512 proposes code signing but does not prove our detector cause or promise
zero detections. UAL issue178 concerns a repository source archive downloaded
instead of a release, not our pinned loader. These leads are not attribution.

- https://github.com/mstorsjo/llvm-mingw/issues/466
- https://github.com/mstorsjo/llvm-mingw/issues/512
- https://github.com/ThirteenAG/Ultimate-ASI-Loader/issues/178

Exact-label searches did not identify a reproducible Yogi/Loader rule for our
ASI. Do not infer a MinHook cause from a generic family name. Search outcomes
and third-party reports do not override the preserved file observations.

## Bounded Microsoft cross-compiler audit

Use the existing official Microsoft x64 toolchain on an isolated GitHub
Windows-2022 runner, verifying tool signatures and recording versions/hashes.
`tools/build_native_msvc_audit.py` compiles the unchanged native sources and
owned hosts; /analyze covers the active C++ units. Only JSON evidence is
retained. No player archive, binary upload, game launch or installed-file change
is part of this audit.

The diagnostic version is **0.10.4-msvc-audit**, rejected by the player packager.
A generated forced-include adapter maps only the two audited level-zero
__builtin_return_address sites to Microsoft's _ReturnAddress intrinsic. It is
not a production source/mapping change. Inlining/ABI implications and owned
checks remain explicit; this is not live NMS acceptance.

This adds an independent compiler/source check and prepares an attributable
comparison. It cannot establish an antivirus improvement without comparable
completed scans. Do not adopt, strip, rename or repeatedly vary a player binary
merely to seek fewer detections. All frozen player artifacts remain immutable.
The completed result is recorded below.

## Completed Microsoft audit readback, 24 October 2026

[Run 40083974784](https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40083974784),
job 120843032853, completed successfully at source
`1f08e37df8d046d02f193cb05b245cbd8a3189a9`. All sixteen build/inspection
commands returned zero. MSVC `/analyze` covered the nine active C++ translation
units; the four vendored C units were compiled with `/W4`, not `/analyze`.
The signed tools were cl 19.44.35229.0, rc 10.0.26100.7705 and dumpbin
14.44.35229.0 on Windows-2022 image 20261012.333.1.

The build, compiler and validation receipts form a verified hash chain. All
88 recorded source inputs match the checked-out source byte for byte. Each
referenced validation JSON matches its receipt hash. The sanitized durable
[evidence summary](NATIVE-0104-MSVC-EVIDENCE.json) preserves the CI identity,
tool signatures, receipt digests, diagnostics and validation results without
publishing raw logs or machine paths. Its SHA-256 is
`d3ef6c766b5c14ba4f54dd9fe05b2f7b4cefbeb843fe28f2d128132168ebc949`.

Passed owned checks: 31,216 policy comparisons / 88 traces; 25,733 selection
comparisons / 59 traces; 333 storage cases / 721 operations; 63 runtime cases;
sixteen backup cases; sixteen query cases; ten hook-ABI groups; 21 load-context
cases; six foreign-host refusals. These are offline checks, not NMS gameplay.
The diagnostic ASI is 747,520 bytes, SHA-256
`14d53f23f005f05e0ad696a00268c28cda8ca1e5198447dd833050dcedc7639b`.
No diagnostic binary was retained for distribution or submitted to a scanner.

### Diagnostic triage

Eighteen distinct warning locations/messages belong to six codes. Repeated
messages across host builds are not counted as additional distinct findings.

| Code / distinct findings | Source interpretation | Disposition |
| --- | --- | --- |
| C4701 / 1 | HDE `hde64.c:59` reads `c` after a loop whose initializer sets `x=16`. Every path into or out of that loop first executes `c=*p++` at line 23. | No uninitialized-use path was demonstrated. Preserve upstream code; do not initialize a variable merely to change artifact bytes. |
| C4244 / 8 | Six vendored bitfield/byte conversions and two STL instantiations from `menu.cpp:344`. The latter fills an unsigned-byte range with the literal zero. | The zero conversion is exact. Vendored bounds remain covered by owned-hook tests; this is not a proof for every possible decoder input. No new concrete defect or detector attribution was established. |
| C4310 / 1 | MinHook's short backward-jump operand explicitly encodes the low byte of `0-(2+5)`. | Intentional x86 instruction representation; ordinary hook restoration/forwarding checks passed. |
| C4324 / 1 | `TextureRecord` explicitly requests 16-byte alignment and asserts its handle offset. | Expected layout padding, not evidence of payload insertion. |
| C4459 / 1 | The local `app` in the templated load-context observation shadows the namespace declaration. | The local value is derived by the bounded reader and used consistently; no changed owner or mapping follows from the warning. |
| C6262 / 6 | Hash/copy helpers use 65,536-byte buffers; host-path inspection uses 32,768 UTF-16 characters. Inlining accounts for repeated stack-size diagnostics. | Real bounded stack usage; stack-headroom analysis for all game callers remains NOT CHECKED. No observed stack failure or AV-rule connection was established. |

The audit supplies an independent compiler and owned-runtime check. It is not
an antivirus scan and does not identify a private detection rule. In
particular, its smaller MSVC output is not evidence that it is cleaner. Do not
replace the validated player artifact with this diagnostic output.

## Exact artifact and public-host readback, 24 October 2026

The immutable 0.10.4 ZIP was rehashed and read back: size, ZIP CRCs, all 29
members, every manifest member, manifest digest, ASI and pinned loader match
the original package receipt. No player package bytes or build inputs changed.
The recorded exact game target and the 90-role mapping inventory are unchanged;
this pass did not inspect the currently installed game or claim a newer build.

Direct browser readback of mod 4579 confirms that **50040 / 0.10.3-native-test**
remains the sole Main file and is **quarantined**. Files 49469, 49367 and 49202
are under Old files. The page is logged out; no upload or page mutation occurred.
The public search-cache snapshot still showed 0.10.2 and must not replace this
direct observation. Plain HTTPS retrieval hit a web challenge; a hidden in-app
browser supplied the current visible file state without foreground app control.

The exact submitted 0.10.3 ZIP report still shows **10/67**, last completed
analysis **23 October 2026 09:06:05 UTC**. This was a report read, not a new scan.
Hash-only lookup of the 0.10.4 ASI returned **Item not found**, not zero detections.
No new upload, reanalysis, CAPTCHA attempt or security-setting change occurred.

The owner now conditionally permits computer control when another route is
insufficient and the action will not disturb them. The previous blanket UI
restriction is superseded to that extent. This does not authorize support or
vendor messages, whose earlier refusal remains effective.

## Remaining gates and bounded next action

| Gate | Current state / next evidence |
| --- | --- |
| Independent source/compiler audit | Completed with the bounded warning dispositions above; not AV clearance. |
| Exact 0.10.4 scanner result | NOT CHECKED. No completed report exists in the inspected hash lookup. |
| Existing Nexus quarantine | Confirmed on 24 October. The official policy requires moderator review to remove an existing quarantine. A current evidence-backed request is prepared in [the unsent review draft](../release/NEXUS-QUARANTINE-REVIEW-20261024.md). Sending needs the owner's explicit authorization. |
| Private detector-rule and sandbox UDP attribution | Unresolved / NOT CHECKED in this pass. Compiler success cannot settle these questions. |
| Exact 0.10.4 NMS acceptance | NOT CHECKED. Separate from distribution/scanner acceptance; prior 0.10.3 observations do not transfer. |

Official policy re-read on 24 October:
https://help.nexusmods.com/article/117-why-has-my-mod-been-quarantined
and https://help.nexusmods.com/article/128-anti-virus-false-positives.
Preserve file50040 and the submitted bytes while requesting the failed gate and
review requirements. Do not promise that moderator approval would establish
zero vendor detections. No support contact has been sent.
