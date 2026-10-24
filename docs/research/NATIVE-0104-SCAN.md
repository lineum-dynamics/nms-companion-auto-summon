# Native detection attribution, 24 October 2026

Priority: the owner requests resolution of antivirus detections and Nexus
publication. Backup work is parked separately on fix/native-backup-volume-root
at c23b417. Current branch research/native-antivirus-attribution starts from
frozen query-guard checkpoint a55a362. No backup prototype is in this work.
Desktop/app/browser control remains withdrawn. No vendor/support contact is
authorized; no security exclusion or protection change is permitted.

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
Actual CI results will be appended after readback.
