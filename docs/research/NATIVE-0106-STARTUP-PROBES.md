# Fixed inactive startup comparison — 28 October 2026

All four approved matched-export inspection/core probes completed. Each has
one Cynet label, including the inert baseline. All eight earlier Yogi-positive
vendors returned Undetected on every probe. The later unchanged full 0.10.6
control still reports Yogi. Inspection/core inclusion is not sufficient under
those controls; bootstrap, reachability, interface/metadata and link-layout
differences remain unresolved. No private matching rule or defect is inferred.

## Preregistered six cases

All six have the same filename **CASStartupProbe.asi**, diagnostic resource,
and production-shaped exports CasInspectHost, CasRuntimeStatus, InitializeASI.
They link the same core/guarded MinHook sources. No player bytes are changed.

| Case | Startup source | Inspection | Link policy |
| --- | --- | --- | --- |
| cold | Inactive atomic status change; no worker | Inert refusal stub | NOREF/NOICF |
| worker | Verbatim production export tail, minimal host-only worker | Same stub | NOREF/NOICF |
| full-stub | Unchanged production bootstrap.cpp | Same stub | NOREF/NOICF |
| full-real | Same production bootstrap | Production inspector behind forced-refusal adapter | NOREF/NOICF |
| full-stub-ref | Same as full-stub | Same stub | REF/ICF |
| full-real-ref | Same as full-real | Same forced-refusal adapter | REF/ICF |

The generated worker export tail is copied verbatim from the pinned source,
starting at CasRuntimeStatus through DllMain. Its source/fragment hashes are
recorded. The worker body is an explicitly different minimal diagnostic,
not the complete initializer or an exact trace of the player ASI.

All inspector paths refuse host support. Stub cases return unsupported. Real
inspection is compiled internally without export decoration under a renamed
C symbol; the only public inspector adapter converts any supported result
to unsupported before the production initializer can proceed. A synthetic
owned control must prove supported-to-unsupported conversion and preservation
of ordinary errors/invalid-argument refusal. The minimal worker also refuses
activation even if its inspector unexpectedly reports supported.

These are intentionally inactive diagnostic libraries. They do not expose an
activation override, weaken a player guard, install hooks or access game/save
data. Full diagnostic code may be statically present; its activation branch
cannot be authorized by the diagnostic inspector. The controller and synthetic
test must pass before any multivendor upload is considered.

## Owned execution and retention controls

Use the same signed installed Microsoft toolchain and /MT, /O2, /Z7,
/DEBUG:FULL, /Brepro and basename PDB references. Keep the resource identical
across all six, and explicitly record the two intentional link policies.
NOREF requests unused-code retention; REF results must not be represented as
retaining every linked core method. No arbitrary binary transformations.

The existing authored native host loads each exact library in three fresh
processes, invokes inspection/invalid-argument checks, then makes eight
concurrent InitializeASI calls and a later retry. Every run must stop at
runtime status 2 with inactive hooks. The adapter's real inspection must return
the independently hashed owned host identity; stub hashes must be empty.
Only ordinary process exit is exercised, respecting the production pin.
Child environments omit CI tokens. No local native execution or NMS access.

Record source/generated/tool/input hashes, export/resource controls and all
actual run results. Compilation/control results are NOT CHECKED until readback.
CI retains only the six labelled ASIs and receipts, with no automatic AV upload.
Specific approval is required for those frozen files and the actual terms/
sample-sharing form before any later VirusTotal submission.

## Interpretation registered before any upload

- Cold positive: common interface/metadata/core/CRT features remain sufficient
  candidates; do not attribute the rule to an active startup operation.
- Worker positive with cold negative: the minimal startup/worker boundary is
  a fixture discriminator, not proof of a malicious API or unsafe behavior.
- Full source positive with worker negative: retain full-bootstrap callback,
  static data, code-layout or combination explanations. No arbitrary source
  deletion or player change is justified by a label alone.
- Stub/real difference: isolate inspection interaction under the full startup
  source; earlier inspection-only negatives remain bounded to their fixtures.
- REF/NOREF difference: retain layout/reachability/link effects. It does not
  identify a source defect or authorize choosing player bytes by scan score.
- All negatives: resource/interface/reachability and other full-ASI differences
  remain open. Stop repeating these same inclusion controls without a new
  discriminator. A detector's private rule remains outside our observation.

Target remains Windows/Steam Cosmos 7.06 / build 25732212 / executable SHA-256
13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
No new game image, mapping/RVA/profile or player-facing meaning is changed.
This suite is research, not a new player version or Nexus replacement. Support
contact remains unsent.

## Completed owned CI readback

[Run 40700680862](https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40700680862)
at source a88f5e11c0744a481cd947a4adec3e3e795b9340 passed without a repair run.
All 96 recorded source inputs match Git blobs. The supported-result adapter
control passed, preserving ordinary errors and invalid arguments. All 18 fresh
process runs passed, three per case: eight concurrent InitializeASI calls plus
retry reached status 2/inactive hooks. Real inspection cases match the owned
host hash; stub cases have an empty hash. The 889-byte shared export tail's
recorded hash 99a517c9 matches the reviewed source. No local native execution.

All six resources and three exported names match. The first four explicitly
request NOREF/NOICF retention; the two REF/ICF cases retain only referenced/
merged code as the linker chooses. Independent selected local PE checks confirm
x64, the three exports and no overlay. No complete unwind or game verification.

| Case | Bytes | SHA-256 |
| --- | ---: | --- |
| cold | 1,452,544 | `7505d9a7649ab435b2ebb2c28d4020214c3eb3a4082e2ac57242748c5bc89661` |
| worker | 1,452,544 | `2e95ed46873b1b9edf483a23b338a6e947975299711b4bbe01a145b303c226bc` |
| full-stub | 1,799,168 | `593f0a662c91011dc1dbe7ee5aa97126543cf212083efc68160bd179a92a1f02` |
| full-real | 1,802,240 | `8dd9e588a52c32101e933787d3c12ab2d12430fdce9524d6bd16b6e6010be9d0` |
| full-stub-ref | 746,496 | `addb9ad40048b56c1d1141e6baca69b7fb271d1070ff10156291ea0a75f20a9b` |
| full-real-ref | 749,568 | `62388dcef02f5eddaf39c1a8a05706d2233c3afba862292e6f5259e4ceb8254a` |

Full metadata/source/generated/tool identities:
[NATIVE-0106-STARTUP-IDENTITIES.json](NATIVE-0106-STARTUP-IDENTITIES.json), SHA-256
`3388b85b3c2f7bc5ea7a238063ea784be9345a8f1610d55398d296f997fe3a3d`. This is an immutable initial pre-submission record. At that initial checkpoint, submission had not yet been approved.
The later completion below supersedes that historical review state.

## Completed multivendor readback

All six specifically approved ASIs completed submission and analysis. The final
file's separately approved CAPTCHA was completed; it was an upload gate, not
an antivirus finding. Each table contains 75 unique vendors, including four
unsupported file types. Timeouts and failures remain unevaluated.

| Case | Analysis UTC | Malicious/evaluated | Timeouts | Failures | Eight earlier Yogi vendors |
| --- | --- | --- | ---: | ---: | --- |
| cold | 14:20:21 | 1/54 | 16 | 1 | 7 Undetected, 1 timeout |
| worker | 14:23:00 | 1/49 | 21 | 1 | 4 Undetected, 4 timeout |
| full-stub | 14:24:11 | 2/70 | 0 | 1 | 8 Undetected, 0 timeout |
| full-real | 14:24:13 | 2/63 | 7 | 1 | 4 Undetected, 4 timeout |
| full-stub-ref | 14:24:12 | 2/68 | 0 | 3 | 8 Undetected, 0 timeout |
| full-real-ref | 14:41:30 | 2/69 | 0 | 2 | 8 Undetected, 0 timeout |

No completed startup row reports Yogi. In full-stub, full-stub-ref and
full-real-ref all eight earlier Yogi vendors completed Undetected. The other
three cases have incomplete Yogi coverage as shown. Cynet labels every case,
including cold. Rising labels all four full cases, while cold/worker time out
on Rising; this does not locate a Rising source boundary. These are not clean
files, player replacements or confirmed false positives.

The unchanged full 0.10.6 ASI (30cc9542) at 13:35:26 UTC remains 9/57, with
12 timeouts, two failures and four unsupported. Six completed vendors still
report Yogi. Even the full startup/real-inspection/REF+ICF diagnostic does not
reproduce those labels. Startup inclusion alone is not a sufficient explanation
under these controls. The forced-refusal adapter, resources/interface metadata,
compiler recipe and object/layout differences remain unresolved.

A concrete recipe difference is now registered for a byte-only first step:
normal player MSVC builds include DLL /analyze, startup diagnostics do not.
Reproduce frozen 30cc9542 first, then omit only that flag while preserving
source, version, resources and linker settings. If bytes match, no new upload
is needed. If different, require owned validation and independent PE comparison
before considering any exact-file submission. No shipped default is changed.

Full tables, hashes and direct report links: [NATIVE-0106-STARTUP-VT-20261028.json](NATIVE-0106-STARTUP-VT-20261028.json).
Evidence SHA-256: `04fdafc602d18f091a19d322ffee6d535d6168f65e5e696c6c3a5cb34c79cc3b`.
No new game, release or Nexus acceptance is established. Support remains unsent.
