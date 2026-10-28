# CRT-aware initializer thread — 28 October 2026

The four fixed component probes completed their approved VirusTotal submissions.
All eight scanners that report Yogi on the complete 0.10.5 ASI returned
Undetected for every probe. Each probe instead has one Cynet ML label, including
the inert CRT-only baseline. This does not establish a universally clean probe
or isolate a private rule. Bootstrap/host inspection or component interactions
remain unresolved; unused-code retention/reachability limits still apply.

## Concrete first-party contract correction

The complete runtime is built with the multithreaded static Microsoft CRT
(`/MT`, libcmt). Its worker uses C++ runtime facilities including strings,
filesystem, exception handling and formatting, but was created using Win32
CreateThread. Microsoft's [multithreading guidance](https://learn.microsoft.com/en-us/cpp/parallel/multithreading-with-c-and-win32)
requires CRT-aware thread creation for this combination. The [CreateThread
documentation](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createthread)
also describes possible CRT failure under low memory.

Change the internal callback to `unsigned __stdcall` and use `_beginthreadex`.
Keep the once-only Interlocked owner, process pin, ordinary creation flags 0,
closed parent handle, no-wait initialization, host/hash/profile checks and all
gameplay filters. Returning from the callback uses the CRT's documented thread
cleanup. The factory's zero return sets stopped status 3 before any worker runs.
No player setting, language string or meaning changes.

This is a documented API contract correction. No player R6016/crash or
low-memory termination has been reproduced, and no Yogi causal connection is
claimed. It is not removal of a safety check or random player-binary variation.

## Distinct candidate and owned controls

Use the new **0.10.6-native-test** Microsoft candidate mode. Frozen 0.10.3,
0.10.4 and 0.10.5 files/reports remain separate. Game target stays exact
Windows/Steam Cosmos 7.06 / build 25732212 / executable SHA-256
13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
No game image or mapping changes and no previous game acceptance transfers.

The candidate CI builds in two directories, requires DLL byte identity, runs
the existing owned validation bundle and positive-control Defender custom scan.
Only the first build also compiles a separate fault-injected DLL. Its forced
include substitutes exactly the source factory call after original CRT
declarations; it returns zero without starting a worker. Eight concurrent
initializer calls must produce stopped/inert status 3, exactly one factory
attempt, and no retry on another call. The fault DLL is never a player payload
or an antivirus submission. Ordinary six host runs must still refuse foreign
hosts with status 2.

| Gate | State |
| --- | --- |
| Local Python syntax/dependency/locale checks | Passed, including 31 focused locale tests |
| Microsoft compilation and two-directory DLL identity | Passed, run 40653804116; DLL hash 30cc9542 below |
| Ordinary owned functional bundle | Passed, all recorded reports/source digests verified |
| Forced factory-zero, single-owner control | Passed: status 3, hooks inactive, one attempt for eight concurrent calls plus retry |
| Exact-file Defender custom scan with positive control | Completed without detection; refresh failed, retained 22 October definitions |
| Exact-candidate UAL automatic startup/normal process exit | Passed, three baselines plus three ASI cases, run 40655172010 |
| Multivendor comparison for the exact new ASI | Latest 9/57 at 13:35:26 UTC, 12 timeouts/two failures; unresolved Yogi |
| Exact-candidate NMS acceptance and Nexus availability | NOT CHECKED |

Run native-msvc-candidate.yml on the exact source commit. Its first command
uses `build_native_msvc_audit.py --release-candidate --startup-failure-fixture`;
the second excludes the fault fixture. Read actual receipts before promoting
any gate. No source/profile override, installation, save change or support
contact is part of this correction.

## Completed build and bounded readback

[Candidate run 40653804116](https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40653804116)
passed at source `4439c909942a333146f001e197360a9aac669c08`.
The ASI is **749,568 bytes**, SHA-256
`30cc9542a2af3529fd4f3a2299d6331bddf51b61f8213a0a1a779b472789de3d`.
Both build directories produced those exact DLL bytes. The retained PDB is
11,210,752 bytes, SHA-256
`5f32c8d508d3e8e4d03dcfdee7e2fdf533abd6ce600d85530d0cfd7aae47b8d1`.
The second PDB differs; whole-build/PDB byte identity is not established.
All 91 recorded source input digests match Git blobs at that exact source.
The build/validation/individual report hash chain was verified locally without
executing native files. [Source audit 40653804071](https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40653804071)
also passed.

Owned checks passed: 31,216 policy comparisons / 88 traces; 25,733 selection
comparisons / 59 traces; 333 storage cases / 721 operations; 63 runtime cases;
16 backup cases; 16 query cases; 10 hook-ABI groups; 21 load-context cases;
six unsupported-host runs with eight concurrent initializer calls each.
The separate forced factory-zero DLL returned status 3, hooks inactive,
exactly one factory call for eight simultaneous calls plus a later retry.
That DLL is not retained as a player payload or submitted to antivirus.

Defender 4.18.26090.9 / engine 1.1.26090.9 finished the read-only custom scan
at 28 October 08:05:21 UTC without a detection and detected the same-mode
68-byte EICAR control with exit 2. However, its signature refresh failed and
definitions remained **1.461.156.0, dated 22 October 18:40:20 UTC**. This is
explicitly not a current-definition verdict. Stock CI realtime protection is
false; the custom scanner was exercised and preferences/input bytes unchanged.

Selected static checks pin the exact ASI/PDB before decoding. PDB GUID/age
matches CodeView. All 1,882 runtime entries, 460 chain steps and depth 5 satisfy
selected bounds/sorting/no-cycle checks; 1,879 headers are V1 and three V2.
Seven sections, six system-DLL import groups, the expected three exports and
no overlay were recorded. Fifteen pefile 2024.8.26 chained-function warnings
remain; unwind opcode/prologue/handler semantics are outside this check.
Run `audit_msvc_candidate_artifact.py --artifact-version 0.10.6-native-test`
with the exact module/PDB paths and output argument.

Sanitized receipt: [NATIVE-0106-EVIDENCE.json](NATIVE-0106-EVIDENCE.json), SHA-256
`ebf161006dc1c92b528f7b3d65cb1a27d003e31534738a3ca313865f7c12334d`.
The initial collector stopped on an incorrectly guessed hyphenated report
filename; corrected actual underscore filenames precede all hash comparisons.
No missing input was counted as passed.

The next loader check uses the same pinned official UAL 9.7.4, exact ASI
30cc9542 and source 4439c90. The controller keeps separate exact 0.10.5/0.10.6
identities, retains the existing Windows-CI-only guard and strips CI tokens
from child environments. Three no-plugin baselines and three automatic-loader
cases must pass without the host calling InitializeASI. Normal process exit
is tested; arbitrary DLL unloading and NMS compatibility are outside this scope.

## Exact loader lifecycle completed

[UAL run 40655172010](https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40655172010)
passed at controller 732d37463eb44839400b467e18f4fc3d23ce8852. It downloaded the
unchanged exact ASI 30cc9542 from candidate run 40653804116 and used the pinned
official UAL 9.7.4/fa266e35. All three no-plugin baselines and three ASI cases
exited 0. The loader discovered and initialized the ASI automatically; the host
never called InitializeASI. Every ASI case reached unsupported status 2 and
restored its working directory; input bytes remained unchanged. Host hash
96b8fa5fb07baf86840b4d22ed8cf4fc34086be9da6f21a18898c27d03faf7ae is also
unchanged from the earlier owned 0.10.5 lifecycle fixture. These remain owned
unsupported-host observations, not NMS acceptance or arbitrary DLL unloading.

## Completed multivendor result

The owner explicitly approved this exact ASI, displayed terms/sharing and the
current control CAPTCHA. The ASI upload completed. The continued control
challenge was completed through observed DOM cells; a page reload verified
that the new control analysis was queued, then its full dated result arrived.

| Frozen module | Analysis UTC on 28 October | Malicious/evaluated | Other states |
| --- | --- | --- | --- |
| 0.10.6, 30cc9542 | 08:22:30 | 5/50 | 20 timeouts, 1 failure, 4 unsupported |
| 0.10.5 control, 8e6dd664 | 08:29:05 | 10/69 | 1 timeout, 1 failure, 4 unsupported |

Both complete tables have 75 distinct vendors. Only 48 completed both analyses;
each file has five positives among those 48. Cynet changes from Undetected to
malicious; TrendMicro-HouseCall changes the other way. eScan/GData/VIPRE still
report Yogi on both. ALYac/Arcabit/BitDefender/CTX/Emsisoft all time out on the
new candidate while remaining positive on the control. The lower displayed
numerator does not establish an improvement. Engine/definition identity is
not established from the UI. The documented CRT correction is not sufficient
to remove the observed Yogi labels and is not AV clearance.

Complete dated tables and comparison: [VT evidence](NATIVE-0106-VT-EVIDENCE-20261028.json),
SHA-256 82b926b07fd2bdd272fc3fe509b6778dfd85f2ee47ecc5c1c4cdabf796651685.
The next bounded discriminator is the preregistered
[matched-export inspection/core comparison](NATIVE-0106-INSPECTION-PROBES.md).
Those diagnostics do not modify frozen player bytes. NMS acceptance and Nexus
availability remain separate open gates. Support remains unsent.

## Afternoon controls and remaining boundary

The approved four inspection/core files completed at 13:23:12, 13:23:35,
13:25:39 and 13:26:24 UTC. All eight Yogi-positive vendors return Undetected
on all four. Cynet labels each, including the inert baseline. Inspection-only
is 1/70 because Zillya failed; the other three are 1/71. Those are not clean-file
claims. A new same-byte full 0.10.6 reanalysis at 13:35:26 is 9/57, with 12 timeouts,
two failures and four unsupported. Arcabit/CTX/Emsisoft/eScan/GData/VIPRE still
flag Yogi; ALYac and BitDefender time out. Thus six contemporaneous positive
control vendors are negative on every diagnostic. Definition/version identity
remains unestablished. The next discriminator is the fixed inactive
[startup/link comparison](NATIVE-0106-STARTUP-PROBES.md), not another player
rebuild. No NMS/Nexus acceptance or private-rule explanation is established.
