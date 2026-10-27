# Microsoft build candidate — 27 October 2026

The owner requests an autonomous technical resolution of the detection blocker,
including a different build/distribution approach when warranted. This is a
new **0.10.5-native-test** candidate, not a rewrite of either frozen artifact.
It is not yet a release or an antivirus clearance.

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
| Candidate compilation | NOT CHECKED until CI readback |
| Two-build byte identity | NOT CHECKED until CI readback |
| Owned functional bundle | NOT CHECKED until CI readback |
| Positive-control Defender scan | NOT CHECKED until CI readback |
| Comparable multivendor scan | NOT CHECKED |
| Active hooks and UAL lifecycle attribution | NOT CHECKED by this workflow |
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
transitions without attributing an unrelated sandbox event. Both results are
NOT CHECKED until the actual CI output is read back.

## Exact-candidate UAL lifecycle fixture

`native-ual-lifecycle.yml` downloads the retained checked candidate from
run40585107104 and the official hash-pinned UAL9.7.4 archive. It verifies ASI
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
Results remain NOT CHECKED until actual CI readback.
