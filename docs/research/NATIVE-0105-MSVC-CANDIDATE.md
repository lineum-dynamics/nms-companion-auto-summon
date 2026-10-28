# Microsoft build candidate — 27 October 2026

The owner requests an autonomous technical resolution of the detection blocker,
including a different build/distribution approach when warranted. This is a
new **0.10.5-native-test** candidate, not a rewrite of either frozen artifact.
It is not yet a release or an antivirus clearance.

**Readback:** the Microsoft candidate build, DLL reproduction, owned functional
checks, positively controlled Defender scan, owned MinHook transitions and
exact-candidate UAL startup/normal exit have completed. The explicitly approved
exact ASI submission completed at 27 October 21:43:19 UTC with 8/71 detections,
all Yogi labels. A fresh unchanged 0.10.4 control reports 30/71 at 21:53:11 UTC.
This remains unresolved. No candidate game acceptance or Nexus upload occurred.

## Engineering change

- Use the existing signed Microsoft C/C++ toolchain on an isolated Windows CI
  runner as a maintained candidate build path, not a diagnostic macro adapter.
- Express the two native callback return addresses through a call-site macro:
  Microsoft's `_ReturnAddress()` or GCC/Clang's level-zero builtin. No helper
  frame may change the attribution. No filter, RVA or gameplay policy changes.
- Generate a separate full PDB with `/Z7` and `/DEBUG:FULL`, preserve release
  optimization explicitly, normalize source/build paths, and keep the basename
  PDB reference. Preserve symbols instead of stripping the old binary.
- Build in two distinct directories and require byte-identical DLL hashes.
- Validate the produced module with the full owned functional bundle, then
  require a completed Defender scan with its harmless positive engine control.
- Retain only that checked ASI and its PDB for subsequent exact-file analysis.
  The player packager rejects the distinct version; no Nexus upload or local
  installation is performed by this workflow.

The legacy MinGW builder and both frozen player artifacts remain available
for a controlled comparison. A different compiler, smaller DLL or fewer PE
sections alone cannot establish the cause of a proprietary detection.

## Exact target and gates

Game target remains Windows/Steam Cosmos **7.06 / build 25732212**, executable
SHA-256 `13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
No new executable image is read and no mapping is changed. Earlier gameplay
acceptance does not transfer to a newly compiled module automatically.

| Gate | Current state |
| --- | --- |
| Candidate compilation | Completed, signed installed Microsoft tools, run 40585107104 |
| Two-build DLL byte identity | Completed; both hashes 8e6dd664 below; PDB bytes differ |
| Owned functional bundle | Passed; receipt hash chain and 89 recorded source inputs verified against the Git commit |
| Positive-control Defender scan | Completed, no detection recorded; EICAR detected in the same mode |
| Comparable multivendor scan | Completed exact-file 8/71, fresh control 30/71; unresolved detection, no clearance |
| Owned active-hook source fixture | Completed for original and query-guard source, run 40585107247 |
| Exact-candidate UAL lifecycle | Completed in an unsupported owned host, run 40586261812 |
| Exact-candidate NMS acceptance | NOT CHECKED |
| Nexus download acceptance | NOT CHECKED |

Run `.github/workflows/native-msvc-candidate.yml` on the exact source revision.
The entry point is `tools/build_native_msvc_audit.py --release-candidate
--output <new-repository-build-directory>`. The default audit remains separately
labelled. Read back receipts, compiler signatures, repeat hashes, functional
results and the engine control before promoting any row.

Primary references: [Microsoft DLL guidance](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices),
[separate full debug symbols](https://learn.microsoft.com/en-us/cpp/build/reference/debug-generate-debug-info),
and [basename PDB references](https://learn.microsoft.com/en-us/cpp/build/reference/pdbaltpath-use-alternate-pdb-path).
Support contact remains unsent.

## Independent active-hook source fixture

`native-hook-lifecycle.yml` builds the pinned original and query-guard MinHook
sources with compile-time recorder substitutions for selected Windows APIs.
All targets and one waiting worker are authored in the owned CI executable.
Enable/disable/remove must forward the expected function result, resume each
suspended thread, restore code bytes/protection and let the worker exit.
API ownership checks reject foreign thread/process handles. Fixed counters
replace in-process injected instrumentation and do not allocate or print while
other threads are frozen. Recorder sources do not change player dependencies.

This is an instrumented **source fixture**, not a trace of the exact frozen
ASI or a full-game test. It can explain hook-library operations under active
transitions without attributing an unrelated sandbox event. Both results have
now been read back; the completed observations below supersede preparation.

## Exact-candidate UAL lifecycle fixture

`native-ual-lifecycle.yml` downloads the retained checked candidate from
run 40585107104 and the official hash-pinned UAL9.7.4 archive. It verifies ASI
8e6dd664c1fc0982a435b5932d0c9f006f1522926aa28b9556b7f2ce7dcb4695 and loader
fa266e3513d02c08a1b808f28c10538a489eaffaa4b0707f7cc1066e71b5afd7 before use.
An authored host dynamically loads the loader after its CI/context gate and
invokes ordinary IAT-trigger APIs plus one forwarded winmm export. It never
calls InitializeASI itself. Three no-plugin baselines and three ASI cases
must observe the expected module/status, restored working directory, unchanged
input hashes and successful OS process exit. Child environments omit CI tokens.

This tests the normal process-exit lifecycle, not an unsupported ASI-unload API,
active NMS hooks, all loader exports or a universal antivirus classification.
UAL's pinned source at6b440669 documents its automatic InitializeASI call in
source/dllmain.cpp and defers plugin loading through ordinary host IAT calls.
The completed observations below supersede the initial NOT CHECKED state.

## Completed artifacts and functional readback

[Candidate run 40585107104](https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40585107104)
completed successfully at source `085838cc3ef87ee98b935c2a6774a479df3343f4`.
The ASI is **747,520 bytes**, SHA-256
`8e6dd664c1fc0982a435b5932d0c9f006f1522926aa28b9556b7f2ce7dcb4695`.
Both build directories produced those exact DLL bytes. The retained first PDB
is 11,210,752 bytes, SHA-256
`568376af58a3d4475cb6ceaea02b495e602a001bc8875d09734dc84abb183b6d`;
its MSF identity matches the DLL's CodeView GUID/age. The second PDB bytes differ;
only DLL byte reproduction is established, not whole-build/PDB byte identity.

The build/validation/report hashes match. All 89 recorded source input digests
match Git blobs at the candidate commit; that check preceded the separate
0.10.6 CRT-thread source correction.
Passed owned checks: 31,216 policy comparisons/ 88 traces; 25,733 selection
comparisons/ 59 traces; 333 storage cases/721 operations; 63 runtime cases;
16 backup cases; 16 query cases; 10 hook-ABI groups; 21 load-context cases;
six unsupported-host runs with eight concurrent initializer calls each.
No game process was started or attached and no gameplay acceptance is inferred.

Defender 4.18.26090.9 / engine 1.1.26090.9 / definitions 1.461.231.0, dated
27 October 13:01:07 UTC, completed the exact-module custom scan without a
detection. The same read-only mode detected the official harmless 68-byte EICAR
control with exit 2. Input hashes and protection preferences were unchanged.
Stock CI realtime protection was false; this is an exercised custom scan,
not a claim that realtime protection was enabled or that other vendors agree.

## Completed hook and loader observations

[Hook run 40585107247](https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40585107247)
passed both pinned source fixtures. Each observed four thread opens, two
successful suspends/resumes of the owned waiting worker, two context reads,
zero context writes, one executable allocation, two temporary code-protection
changes/restores and two instruction-cache flushes. No foreign thread/process
handle or failed operation was observed. Original code bytes/protection were
restored and the worker exited. This is source instrumentation of MinHook,
not an exact frozen-ASI trace or proof about an unrelated sandbox event.

[UAL run 40586261812](https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40586261812)
passed three no-plugin baselines and three exact-candidate runs. The official
unchanged loader discovered the ASI and invoked initialization automatically;
the host never called InitializeASI itself. The candidate reached unsupported
status 2, the working directory was restored, hashes remained unchanged and
every OS process exited 0. Active NMS hooks and arbitrary DLL unloading remain
outside this fixture.

## Static structure and method limits

The candidate has seven ordinary PE sections and six system-DLL import groups,
the three expected exports and no overlay. Full pefile 2024.8.26 parsing emits
15 chained-function warnings; they remain in the evidence. The independent
raw table pass checks all 1,872 runtime-function entries,460 chain steps and
maximum depth 5 for valid code bounds, sorting, header/flag layout and cycles.
There are 1,869 V1 and three V2 table headers. The first V1-only helper refused
those three V2 entries as TOOL_ERROR; reviewing the shared fields against the
LLVM 20.1.8 reader allowed the bounded V1/V2 check. No binary was rewritten.
Unwind opcodes, prologue semantics and all handler data remain NOT CHECKED.
This does not erase parser warnings or establish global PE/runtime correctness.

Reproduce with `tools/research/audit_msvc_candidate_artifact.py --module
<exact-ASI> --pdb <retained-PDB> --output <static-receipt>`. Primary layouts:
[Microsoft x64 exception handling](https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64)
and the [pinned LLVM reader](https://github.com/llvm/llvm-project/blob/llvmorg-20.1.8/llvm/tools/llvm-readobj/Win64EHDumper.cpp).

Incomplete attempts are preserved: run 40583926085 passed compilation,
functional, reproduction and scan steps but failed cross-volume artifact
retention; run 40584515831 stopped its original-source job before compilation
because that snapshot predates the patch-specific validator. Its query-guard
job passed. Later artifact staging/lock validation fixed those measurement
methods; neither earlier overall run is relabelled successful.

Sanitized receipts and identities: [NATIVE-0105-EVIDENCE.json](NATIVE-0105-EVIDENCE.json),
SHA-256 `5292514fff69b8ba26b949528c0ef9ac125e630e7d8f61ae2477a8e11968f5ef`.
The new candidate is not installed or packaged for players. Complete tables
and the fresh 0.10.4 comparison are in [the dated VT evidence](NATIVE-0105-VT-EVIDENCE-20261027.json).
All eight 0.10.5 positive vendors are a subset of the control's 30 positives;
22 rows changed from malicious to undetected. Engine/definition identity was
not established from the UI, and multiple build factors changed. A reanalysis
click produced no new timestamp; an independent repeat is not established.
The [four approved component probes](NATIVE-0105-COMPONENT-PROBES.md) completed
on 28 October: all eight Yogi scanners returned Undetected for each; Cynet
labelled each, including the inert CRT-only control. Bootstrap/host inspection
and component interactions remain unresolved. See the separate
[documented CRT-thread correction](NATIVE-0106-CRT-THREAD.md) for the next
engineering candidate. The support draft remains unsent.
