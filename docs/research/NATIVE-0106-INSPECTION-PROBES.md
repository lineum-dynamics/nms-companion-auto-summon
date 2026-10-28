# Fixed inspection/core comparison — 28 October 2026

The CRT-thread contract correction is implemented and its owned controls pass,
but it does not resolve Yogi. The exact 0.10.6 scan completed with 5/50,
20 timeouts and one failure; the fresh unchanged 0.10.5 control has 10/69,
one timeout and one failure. Both tables have 75 rows. On the 48 vendors that
completed both, each has five positives. Cynet changed to positive and
TrendMicro-HouseCall to Undetected; the three completed Yogi vendors remain
positive. The other five earlier Yogi-positive vendors timed out on 0.10.6.
Do not advertise the lower displayed numerator as an improvement.

Earlier inert component controls were Yogi-negative. They omitted host
inspection/bootstrap and had a different exported interface. The next fixed
comparison addresses the inspection/core boundary with matched exports.

## Preregistered four cells

| Case | CasInspectHost implementation | Runtime core and guarded MinHook |
| --- | --- | --- |
| baseline | Inert unsupported-host ABI stub | Absent |
| inspection | Unchanged production probe.cpp | Absent |
| core | Same inert ABI stub | Present |
| inspection-core | Unchanged production probe.cpp | Present |

All four are called **CASInspectionProbe.dll**, have the same diagnostic
resource and exactly two exports: CasComponentProbeStatus and CasInspectHost.
The common status entry/DllMain are unchanged from the earlier inert probes.
No bootstrap, InitializeASI, worker or gameplay activation is linked. The
core set is binding_guard/policy/selection/storage/runtime/backup/menu plus
the same pinned guarded MinHook objects. The generated language catalog is
included by runtime.cpp in both core cells. No player binary is modified.

Use the same installed signed compiler and /MT, /Z7, /DEBUG:FULL, /Brepro,
/OPT:NOREF and /OPT:NOICF policies for every cell. Normalize build/source
paths; retain unused production code. Source, dependency, generated-file and
tool identities must be recorded. The workflow retains only the four inert
DLLs and sanitized receipts; no automatic antivirus upload occurs.

## Owned execution control

The host checks its exact filename and Windows-CI/repository environment.
Child environments omit CI tokens. It loads each DLL, checks the status export
and invalid-argument refusal, then invokes only CasInspectHost. The stub must
return unsupported with empty image hash; production inspection must return
unsupported with the actual owned EXE's independently computed SHA-256. Both
must have ABI 1, the correct report extent and inactive hooks, then unload.
No core/game method is invoked. This inspects only the authored host EXE;
it never opens NMS, saves or a caller-chosen executable.

## Interpretation registered before any upload

- Baseline positive: common metadata/export/CRT/stub features remain in scope;
  do not attribute the label to production host inspection.
- Inspection positive with baseline negative: the inspection source boundary
  is a sufficient fixture discriminator under these controls. It does not
  identify a private rule or establish malicious behavior.
- Only inspection-core positive: retain a combination hypothesis; do not
  declare either component alone defective.
- All cells negative: bootstrap or other reachability/layout/interaction
  differences remain unresolved. Do not weaken the exact-game guard.
- No probe result is clearance, a false-positive classification or permission
  to select a player binary repeatedly for a scanner score. A player-source
  repair requires a separate demonstrated engineering reason.

Compilation, export/resource checks, owned execution and exact identities are
NOT CHECKED until Windows-CI readback. Any later multivendor upload requires
specific approval for the frozen four files and the actual sharing/terms form.
All 0.10.3/0.10.4/0.10.5/0.10.6 player artifacts remain preserved. Game target
stays Cosmos 7.06 / Steam 25732212 / executable SHA-256
13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
No new game image or profile/RVA/text meaning change; support remains unsent.

## Initial method refusal

Run 40658954904 at 8b3ddb3932d55a17d746f29cca9171649e98064b failed at the first
export-table check after compilation and the first owned smoke call. The
initial regex accepted only bare export rows. The retained earlier exact
0.10.6 compiler receipt shows the actual Microsoft format:
`1 0 0000F010 CasInspectHost = CasInspectHost`.
The corrected reader accepts the optional implementation annotation while
preserving the exact two-name assertion. It was checked against that owned
three-export production dump before another CI attempt. This is a TOOL ERROR,
not evidence of absent exports or a diagnostic/module defect. The initial
overall run is not a passed build and no DLL artifact was retained from it.

## Completed owned build readback

Run 40659776218 at 75bb5e59d2f40bbf371261f67959e9aa6e4c62ba completed successfully.
All 93 source digests were checked against that Git revision. All four have the
same resource hash and exactly the two required exports. The owned status,
invalid-argument, unsupported-host/hash and unload checks passed in every case.
Production inspection cases returned the authored host hash e471945b962aa32995928033d3da52e3ce7db78e525f2f67080f0ba94760bb8e;
stub cases returned no image hash. No core method or game was invoked.

| Case | Bytes | SHA-256 |
| --- | ---: | --- |
| baseline | 494,592 | `8d042d4994b99feca64d45210b09d4063aa6b7ec5a8aef3dad7d47cfc57f4add` |
| inspection | 497,664 | `15a591f00db466527e33eefb0ece2dbbaa7fd78bc75f4f21442f1afb4bafaa86` |
| core | 1,452,032 | `7aac8e34c245e5e6058dc11c3195f734d407777a7d96e4b91fb62204118a397e` |
| inspection-core | 1,455,616 | `e823bf9af6cbe2d533eef365fe42529a60c120bdfad305542fd73e0eb2988b1b` |

Independent local read-only PE metadata confirms x64, the same two exports
and no overlay for all four. This does not validate complete unwind semantics
or classify the files. The frozen initial review is
[NATIVE-0106-INSPECTION-IDENTITIES.json](NATIVE-0106-INSPECTION-IDENTITIES.json),
SHA-256 `94dcebcf3f7962d696771f159b91031f139bc6529582b0f818c766a19bc269dc`. It retains tool/source/generated identities and both method
errors. No new diagnostic file has been selected or submitted to VirusTotal.
The actual form has been inspected: Terms of Service, Privacy Notice and
sample sharing. The next action requires approval for these exact four files.
The player ASIs, game mapping/profile and support-contact state are unchanged.
