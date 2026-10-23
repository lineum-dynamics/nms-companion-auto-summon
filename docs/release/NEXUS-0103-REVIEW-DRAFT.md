# Unsent Nexus review request — 0.10.3-native-test

Status: prepared on 23 October 2026; **not sent**. The owner declined support
contact and requested internal investigation. The retained scan snapshot below
predates the later 0.10.2 comparison; use the current scan record for findings.
Sending requires new explicit authorization. This draft concerns only the
public file and public source below; it contains no private logs or saves.

Recipient: support@nexusmods.com

Subject: Review request: NMS mod 4579, native alpha file 50040 (0.10.3)

Hello Nexus Mods team,

We are the authors of Companion Auto Summon for No Man's Sky - by Lineum
Dynamics, published by LineumDynamics:
https://www.nexusmods.com/nomanssky/mods/4579

Our new file 50040, CompanionAutoSummon-0.10.3-native-test.zip, was uploaded
on 23 October 2026 and was quarantined automatically. Please review the exact
file and advise what prevents its acceptance. We are not claiming the scan is
a confirmed false positive or asking players to bypass it.

Archive: 3,725,947 bytes
SHA-256: df7cf87276391a9dc9bdf596611563b3787530da5d5c0107f51bb994f580b3f2
https://www.virustotal.com/gui/file/df7cf87276391a9dc9bdf596611563b3787530da5d5c0107f51bb994f580b3f2

The exact ZIP report showed 10/67 detections, analysis 23 October 2026 at
09:06:05 UTC. Our compiled CompanionAutoSummon.asi independently showed
10/71, analysis 09:09:51 UTC:
https://www.virustotal.com/gui/file/6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652

The reports include Gen:Variant.Yogi.92012 and
VHO:Trojan.Win32.LOADER.gen. These are recorded findings, not a diagnosis.
The unchanged official Ultimate ASI Loader 9.7.4 binary has SHA-256
fa266e3513d02c08a1b808f28c10538a489eaffaa4b0707f7cc1066e71b5afd7;
its bundled-file relation showed 0/49, with a separate earlier analysis date.

This is a native x64 C++ game mod. The ASI loader loads our module during
normal Steam startup; MinHook supplies the deliberate game hooks. The module
requires the exact Windows/Steam NMS 7.06 executable hash and a verified
private pre-activation backup before enabling gameplay hooks. It requests a
summon through the game's own eligibility and placement checks. It preserves
preferences outside the game saves. The ZIP has an explicit allowlist of 29
members, including the English player guide, manifest and dependency notices.

Public source for the exact submitted build:
https://github.com/lineum-dynamics/nms-companion-auto-summon/tree/852c5c55458c563a8564090dd31305864483edf3

Build inputs and dependency provenance:
https://github.com/lineum-dynamics/nms-companion-auto-summon/blob/852c5c55458c563a8564090dd31305864483edf3/native/dependencies-lock.json
https://github.com/lineum-dynamics/nms-companion-auto-summon/blob/852c5c55458c563a8564090dd31305864483edf3/tools/build_native_runtime.py

Build steps (Windows x64, Python 3.11.9, LLVM-MinGW 20260922 UCRT x86_64;
replace the toolchain placeholder with its extracted directory):

```powershell
git clone https://github.com/lineum-dynamics/nms-companion-auto-summon.git
cd nms-companion-auto-summon
git checkout 852c5c55458c563a8564090dd31305864483edf3
python -B tools/build_native_runtime.py --toolchain <toolchain-directory> --output build/review-0103 --teleport-candidate-trial
python -B tools/validate_native_bundle.py --build build/review-0103
```

These tools compile and exercise owned offline hosts; they do not deploy to,
launch or attach to the game. The player package is created separately with
tools/package_native_runtime.py using the pinned official loader. The exact
submitted artifact and validation record are documented here:
https://github.com/lineum-dynamics/nms-companion-auto-summon/blob/main/docs/release/0.10.3-COSMOS-706.md

Please identify any remaining policy or file issue and the appropriate review
steps. We have preserved the submitted bytes and recorded the quarantine.

Thank you,
Lineum Dynamics

## Scope

No attachments, personal saves, settings, private logs, credentials or game
binaries are included. This draft does not authorize contacting antivirus
vendors, uploading further samples, changing security settings or declaring
scanner clearance.
