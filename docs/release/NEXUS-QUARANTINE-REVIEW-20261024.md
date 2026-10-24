# Unsent Nexus quarantine review request, 24 October 2026

Status: **prepared, not sent**. Sending requires the owner's explicit
authorization; the earlier refusal of support contact remains effective.
This draft contains public artifact identities and source/build evidence only.
It does not attach a binary or disclose private logs, saves or machine paths.

Recipient: support@nexusmods.com

Subject: Quarantine review: No Man's Sky mod 4579 / file 50040, with reproducible source evidence

Hello Nexus Mods team,

We maintain Companion Auto Summon for No Man's Sky - by Lineum Dynamics,
published by LineumDynamics:
https://www.nexusmods.com/nomanssky/mods/4579

Please review quarantined file **50040**, uploaded on 23 October 2026, and
identify which security or file-policy check prevents acceptance. Direct
readback on 24 October still shows it as the sole Main file and quarantined.
We have preserved its exact submitted bytes and file history.

Submitted artifact, **0.10.3-native-test**:

- Filename: CompanionAutoSummon-0.10.3-native-test.zip
- Size: 3,725,947 bytes
- ZIP SHA-256: df7cf87276391a9dc9bdf596611563b3787530da5d5c0107f51bb994f580b3f2
- ASI SHA-256: 6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652
- Exact game target: Windows x64 / Steam Cosmos 7.06 / build 25732212;
  executable SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499

The ZIP report, read again on 24 October, shows **10/67** detections from its
completed **23 October 09:06:05 UTC** analysis:
https://www.virustotal.com/gui/file/df7cf87276391a9dc9bdf596611563b3787530da5d5c0107f51bb994f580b3f2

The ASI's latest recorded completed analysis was **15/63**, 23 October
14:33 UTC, superseding its earlier 10/71 result. That ASI result was not newly
rescanned in this follow-up:
https://www.virustotal.com/gui/file/6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652

We are not claiming that these are confirmed false positives or asking users
to disable antivirus. An exact detector-rule explanation remains unresolved.

This is a native x64 C++ game mod. The pinned official Ultimate ASI Loader
loads the module during normal Steam startup; MinHook provides intentional
in-process game hooks. Exact executable checks refuse unknown game builds
before gameplay hooks. The module asks the game's own companion-summoning
system to apply the normal ownership, eligibility and placement checks.

The normal ZIP has an explicit allowlist of 29 members, no nested archive,
and dependency notices. The pinned unmodified loader SHA-256 is
fa266e3513d02c08a1b808f28c10538a489eaffaa4b0707f7cc1066e71b5afd7.
We have not established current scanner clearance for the whole package.

Exact submitted source checkpoint:
https://github.com/lineum-dynamics/nms-companion-auto-summon/tree/852c5c55458c563a8564090dd31305864483edf3

Pinned dependencies and builder:
https://github.com/lineum-dynamics/nms-companion-auto-summon/blob/852c5c55458c563a8564090dd31305864483edf3/native/dependencies-lock.json
https://github.com/lineum-dynamics/nms-companion-auto-summon/blob/852c5c55458c563a8564090dd31305864483edf3/tools/build_native_runtime.py

A separate clean Windows run reproduced the submitted ASI byte for byte at
the recorded source prefix. It also reproduced the distinct engineering
candidate described below:
https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/39983965743

We found and repaired one independently reproduced MinHook query-error path
in a distinct, **unreleased 0.10.4-native-test** candidate. Its connection to
the antivirus verdicts is not established. Its ZIP SHA-256 is
70d85b240e90b8bafa524036bd4fccc7f58684d10bc93b13c2d0369e6e8d1c39,
and its ASI SHA-256 is
765cdbdf0e99aea433fd977048b38f0cd28ccbe6c26902c511310a3ee9523ffa.
That candidate has offline regression evidence, but no completed new-file
scan or exact-package NMS gameplay acceptance, and is not file50040.

An independent signed-Microsoft-toolchain source audit completed successfully
at source 1f08e37df8d046d02f193cb05b245cbd8a3189a9. MSVC analysis and all
owned offline runtime checks passed; warnings were retained and triaged. This
is source/test evidence, not an antivirus verdict. The diagnostic output was
not substituted for the player artifact:
https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40083974784

Please advise whether file50040 can receive moderator review, which specific
gate needs further evidence, and whether you prefer a separately identified
candidate submission for any subsequent review. We will retain the quarantined
file and avoid presenting a replacement as cleared before your review.

Thank you,
Lineum Dynamics

## Review scope

This is a routine technical review request about mod4579/file50040. It does
not assert malware absence, request a vendor whitelist, authorize additional
uploads, change security settings, or declare a release complete. No message
has been sent and no additional artifact is attached.
