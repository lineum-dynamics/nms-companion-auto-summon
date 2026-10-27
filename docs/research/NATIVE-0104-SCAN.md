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
`1ae44da169bcaf8b0b7494487dd85a969420a01213935204be4f7936793a2aaa`.

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
| Exact 0.10.4 scanner result | Microsoft Defender completed the exact ASI scan with no detection and a passing positive control; see below. A new whole-package/multivendor scan remains NOT CHECKED. |
| Existing Nexus quarantine | Confirmed on 24 October. Moderator review concerns removal of that quarantine; the owner requires internal analysis first. The [unsent review draft](../release/NEXUS-QUARANTINE-REVIEW-20261024.md) is a last-resort contingency, not the current next action. |
| Private detector-rule and sandbox UDP attribution | Still unresolved. Full-report analysis below positively assigns several API calls to the sandbox host and identifies certificate endpoints; UDP module attribution is still absent. |
| Exact 0.10.4 NMS acceptance | NOT CHECKED. Separate from distribution/scanner acceptance; prior 0.10.3 observations do not transfer. |

Official policy re-read on 24 October:
https://help.nexusmods.com/article/117-why-has-my-mod-been-quarantined
and https://help.nexusmods.com/article/128-anti-virus-false-positives.
Preserve file50040 and the submitted bytes while requesting the failed gate and
review requirements. Do not promise that moderator approval would establish
zero vendor detections. No support contact has been sent.

## Continued internal analysis after owner correction, 24 October 2026

The owner explicitly rejected making the support request the next step:
contact is a last resort after available internal analysis. No message was
sent. The following work adds technical evidence rather than treating the
quarantine policy as proof that diagnosis is complete.

### Full sandbox reports, not only the grouped summary

The Behavior page exposes full-report links for the exact submitted ASI,
SHA-256 `6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652`.
Read the provider-specific HTML through **Full Reports**; the grouped summary
does not contain all of the following detail. Stable links and sanitized
measurements are in [the behavior evidence](NATIVE-0104-BEHAVIOR-EVIDENCE.json),
SHA-256 `a28d6c1bf0076ba6c9c1e1da726716b8ec7c13de187b1b35e8d22113e8fc7049`.
Raw logs, temporary signed URLs and encoded token contents were not published.

| Observation | Bounded finding |
| --- | --- |
| Zenbox full report | Provider verdict **Non Malicious, 4/100**, generated as displayed `23/10/2026 09:17:59`; its displayed time zone was not established. This single provider's result does not clear the fifteen antivirus verdicts. |
| Zenbox Sigma text | The full report lists **Unsigned DLL Loaded by RunDLL32/RegSvr32**. The earlier grouped `Sigma Rules: NOT FOUND` does not establish that every provider report lacks such a label. Preserve this correction. |
| Zenbox UDP | The port53 observation is attributable to the Zenbox report, but its per-process extra-information entries are all `None`; there is no module/call-stack attribution. Do not call it the mod's DNS request or dismiss it as proven background traffic. |
| CAPE visible API records | Selecting Behavior / All yields 357 nonempty records (one empty table row excluded). The first reported caller is within the supplied rundll32 image range in 344 records, in other module ranges in thirteen, and in the target ASI range in zero. This is address classification of this captured trace, not proof of all possible execution or a complete call stack. |
| Positive caller attribution | `SetUnhandledExceptionFilter` is called from rundll32 RVA `0x6D01`; token calls from `0x62E5`, `0x6339`, `0x6435` and `0x6282`. These addresses lie in the reported host executable, not the ASI. `LdrLoadDll` records the target base used for the comparison. |
| CAPE network API filter | No Network-category API record is displayed for the selected rundll32 process. Its separate network packet tables contain traffic without a linking PID or call stack. |
| CAPE HTTP | Five GET requests, all with `Microsoft-CryptoAPI/10.0`: two CTL downloads from `ctldl.windowsupdate.com`, two OCSP requests to `ocsp.digicert.com`, one to `oneocsp.microsoft.com`. These are certificate-trust/revocation endpoints; the initiating process remains unproven. This is no demonstrated companion-mod payload download. |

Caller classification used host base `0x7FF6E8B00000`, host size `0x17000`,
target base `0x7FFE59DD0000` from that report, and exact PE SizeOfImage
2,031,616 bytes. Read the API table cells after selecting **All**, discard
only the empty row, and compare the first reported caller against those
half-open ranges. Preserve unclassified/other addresses rather than assigning
them to the target. The private raw table has its digest in the evidence JSON.

Primary endpoint references:
https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-trust
and https://learn.microsoft.com/en-us/azure/security/fundamentals/azure-certificate-authority-details.
They explain the endpoint purpose, not the sample's initiating process.

### Check static labels against the exact PE

Using pefile2024.8.26 against the hash-matched submitted ASI, the Security
directory has file offset/size **0/0**. Windows `Get-AuthenticodeSignature`
reports **NotSigned**. CAPE's broad `invalid_authenticode_signature` label
therefore must not be paraphrased as an observed forged/modified signature.

The TLS directory exists at RVA `0x13E2A0`, size40, with a callback-table
address resolving to RVA `0x13E298`. Its first eight raw bytes are all zero:
the callback list terminates immediately with **zero callbacks**. A `.tls`
section and generic TLS labels do not prove a pre-entry payload or executed
callback. pefile returned no parser warning. No TLS section or metadata was
removed or renamed to affect scanning.

Reproduce the structural check after verifying the input SHA-256:

```python
pe = pefile.PE(module_path)
security = pe.OPTIONAL_HEADER.DATA_DIRECTORY[4]
tls = pe.OPTIONAL_HEADER.DATA_DIRECTORY[9]
callback_rva = pe.DIRECTORY_ENTRY_TLS.struct.AddressOfCallBacks - pe.OPTIONAL_HEADER.ImageBase
first_callback_slot = pe.get_data(callback_rva, 8)
exports = [(s.ordinal, s.name, s.address) for s in pe.DIRECTORY_ENTRY_EXPORT.symbols]
```

The export table maps ordinal1 to CasInspectHost, ordinal2 to CasRuntimeStatus
and ordinal3 to InitializeASI. CAPE invoked ordinal1 through rundll32, a
different calling contract from the owned-host struct/size interface. This
does not establish an actual correct-ABI InitializeASI game activation, a
native hook, or the function arguments consumed in that sandbox call.

These findings narrow several misleading labels to their actual evidence.
They do **not** identify the private Yogi/Loader detection rule, prove the
sample benign in every environment or resolve the existing quarantine.

### Completed exact-module Defender scans

[Run40089173239](https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40089173239)
completed both source jobs at controller
`74056977e3d0e8fc30be2e60e481343355665f2d`. Each job built the original
module bytes at the historical source prefix and checked the expected SHA-256
before scanning. The independent source/compiler audit is a separate result.

| Input | Source revision | Result |
| --- | --- | --- |
| Submitted 0.10.3 ASI, `6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652` | `852c5c55458c563a8564090dd31305864483edf3` | Scan completed; command reported no threats, exit0. Exact hash preserved afterward. |
| Frozen 0.10.4 ASI, `765cdbdf0e99aea433fd977048b38f0cd28ccbe6c26902c511310a3ee9523ffa` | `7fd4bc09a3185a214a808052da61f2223999619b` | Scan completed; command reported no threats, exit0. Exact hash preserved afterward. |

Both jobs used platform4.18.26090.9, engine1.1.26090.9 and the same updated
definitions1.461.181.0, dated **24 October 2026 05:51:57 UTC**. Scanner
SHA-256 `c0c9670d63a8a7de9c0ef5ba58231826b0abee03c2b3ba6f858114d96ea12315`
has a valid Microsoft Windows Publisher signature. Sanitized receipts and
their original digests are in [the Defender evidence](NATIVE-0104-DEFENDER-EVIDENCE.json),
SHA-256 `a12dce3dc3c9a361721714f1ba0c7979e21f6ccaf4b5c6d4caf916d67bcfdb84`.

The stock GitHub image has real-time protection off and build volumes excluded.
Ordinary custom scans therefore cannot provide the desired evidence there.
The final method used Microsoft's documented **read-only custom scan**
(`-Scan -ScanType 3 -File <exact-module> -DisableRemediation`), which ignores
file exclusions and reports findings in command output. Machine-wide policy
digests match before and after both completed scans. No module was executed,
restored, renamed, stripped or submitted through a workflow upload. Automatic
cloud transmission by the antivirus engine was not observed or established.

Before accepting either zero result, the identical scanner mode detected the
official harmless 68-byte EICAR positive control on that same runner. Its hash
was `275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f`,
with `Virus:DOS/EICAR_Test_File`, exit2. No test marker was written to the
owner's PC, source tree or release ZIP. This separates an operating detector
from a scan skipped by exclusions. Event/UI absence is not used as evidence in
this mode because Microsoft documents that findings are reported to stdout.

Reproduce the CI job by explicitly dispatching `native-defender-audit.yml`
on the research branch with `scan_modules=true`. Normal pushes only probe
engine readiness. `tools/research/scan_native_defender.ps1` requires this
repository's GitHub Actions context, exact input path/hash, signed active
scanner, positive control and unchanged post-scan bytes/policy. A nonzero or
incomplete module scan remains a detection/tool-error investigation, not a pass.

Primary method references:
https://learn.microsoft.com/en-us/defender-endpoint/command-line-arguments-microsoft-defender-antivirus
and https://www.eicar.org/download-anti-malware-testfile/.

### Preserve failed methods and interpretation limits

[Failed-attempt evidence](NATIVE-0104-DEFENDER-ATTEMPTS.json) retains six cases:
run40087854670 stopped before scanning because both a versioned scanner and
its CurrentVersion alias matched; run40088417931 resolved the canonical signed
tool but confirmed that the input was excluded; run40088735176 attempted to
remove the covering CI root exclusion but the effective check still reported
excluded. All six records have `scan_performed=false`. They are not clean
results. The last attempt does not prove why effective policy stayed excluded;
no new exclusion was added and the owner's machine was unaffected. The final
read-only method changes no machine-wide preference and verifies actual engine
operation with a positive control instead of silently ignoring this failure.

Local receipt/PE processing used CPython3.11.9, executable SHA-256
`5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec`.
PowerShell parser validation passed for the scanner script. No native source,
mapping, language value, player artifact or installed runtime changed.

Defender did not distinguish the original and query-guard modules under the
same definitions. This establishes neither improvement from that repair nor a
resolution of BitDefender/Kaspersky verdicts. The entire ZIP and loader were
not scanned in this run. Fresh multivendor evidence for the candidate, the
private rule explanation, Zenbox's UDP module attribution, exact-candidate NMS
acceptance and Nexus download acceptance remain separate open gates. Contact
stays a last-resort contingency; no message was sent or authorized.
