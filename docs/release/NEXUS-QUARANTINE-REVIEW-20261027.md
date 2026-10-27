# Unsent Nexus quarantine review request — 27 October 2026

Status: **prepared locally, not sent**. The owner permits support contact only
as a last resort after internal analysis. Sending requires a new explicit
instruction. The 24 October draft remains historical; this refreshed text
contains current completed scan evidence. Public links/hashes only, no attachments.

Recipient: support@nexusmods.com

Subject: Review request: No Man's Sky mod 4579 / quarantined file 50040

Hello Nexus Mods team,

Please review Companion Auto Summon file 50040 and identify the concrete
security or file-policy check and affected archive member blocking it:
https://www.nexusmods.com/nomanssky/mods/4579?tab=files

The existing file is 0.10.3-native-test, uploaded on 23 October 2026. The
27 October direct readback still shows the only Main file quarantined. We
have preserved its submitted bytes and history.

- ZIP: CompanionAutoSummon-0.10.3-native-test.zip, 3,725,947 bytes.
- ZIP SHA-256: df7cf87276391a9dc9bdf596611563b3787530da5d5c0107f51bb994f580b3f2.
- ASI SHA-256: 6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652.
- Source: https://github.com/lineum-dynamics/nms-companion-auto-summon/tree/852c5c55458c563a8564090dd31305864483edf3
- Game target: Windows/Steam Cosmos 7.06, build 25732212, executable SHA-256
  13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.

The unchanged ASI's completed VirusTotal reanalysis is 30/70, dated
27 October 07:50:46 UTC:
https://www.virustotal.com/gui/file/6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652

We completed internal investigation before requesting this review:

- Independent clean-Windows builds reproduce the submitted bytes. Compiler,
  dependency and archive membership pins were checked against official inputs.
- A separate Microsoft compiler/source audit and owned offline checks passed;
  exact-module Defender scans completed under their recorded definitions.
- Memory/thread APIs map to intentional current-process game-menu access,
  MinHook synchronization and linked runtime helpers. Debug sections, COFF
  symbols, TLS and diagnostic/compiler URL strings have explicit PE attribution.
- Public sandbox and Kaspersky reports provide no matching rule offset or
  source function. We have not established a confirmed false positive.

Technical evidence, pinned inputs and limits:
https://github.com/lineum-dynamics/nms-companion-auto-summon/blob/research/native-antivirus-attribution/docs/research/NATIVE-0104-SCAN.md

We also reproduced and repaired a separate MinHook API-error path in an
unreleased 0.10.4-native-test candidate. Its ASI hash is
765cdbdf0e99aea433fd977048b38f0cd28ccbe6c26902c511310a3ee9523ffa;
its completed 27 October 07:47:26 UTC VirusTotal result is 17/70. This is
a distinct artifact, not file 50040, and its exact-package NMS acceptance
remains open. No antivirus benefit from the repair is causally established.

Could you review the retained file, identify the failing check/member where
disclosable, and specify what further evidence is needed for acceptance?

Thank you,
Lineum Dynamics
