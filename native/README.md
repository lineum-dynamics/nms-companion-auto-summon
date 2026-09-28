# Native feasibility milestone 1

This directory contains an **offline experiment**, not an installable replacement
for the working Python mod. It is kept on `feat/native-runtime-feasibility`.
Do not put these outputs or an upstream proxy DLL into a game directory.

## Implemented and verified

- A Windows x64 `.asi` DLL with a fixed C ABI and the documented `InitializeASI`
  entry point. `.asi` denotes a native plugin; it does not exempt it from scans.
- An inert application `DllMain`. Explicit inspection reads the actual current
  process image path, holds a read-only executable handle, checks its x64 PE
  header and computes SHA-256 with Windows CNG. The expected digest is generated
  from the canonical `compatibility.json`, with no caller-supplied override.
- Every result remains inert, including an exact matching NMS image. There are
  no game hooks, RVA calls, pointers, network calls, save/settings writes or
  deployment code. Successful inspection is not permission to activate a mod.
- A separate C++ port of `src/policy.py`, exercised by an owned offline driver.
  It is **not yet connected to the DLL**. The Python source remains the oracle.

The final `native-probe-001-r4` build passed **31,216 command/state comparisons**
across **88 traces / four configurations**, with no differences. These are
comparison steps, not 31,216 independent tests. Scenarios include paced-state
readiness, queue acceptance/rejection, fixed retry choices, manual-favourite
preservation, invalid/reversed clocks, forbidden locations, native sentinels,
and absence without a new opportunity. Placement pacing itself belongs to the
adapter and is not implemented by this pure policy.

The owned host loaded, inspected and unloaded the DLL in **six runs**, including
a Unicode directory and System32-only PATH. Each run exercised eight concurrent
initializers, repeat initialization, invalid ABI arguments and unsupported-host
refusal. The reported current-image hash matched Python's independent hash of
the owned host. The bundle stayed unchanged **during host executions**; the
validator creates its test copies before that interval and its report afterward.

Only our owned host was run. Ultimate ASI Loader and NMS were not launched,
attached to or modified. No supported NMS-process result, loader timing,
in-memory image integrity, gameplay, antivirus clearance or multiplayer support
is established by these checks.

## Build and reproduce

The compiler is developer-only. The first build used LLVM-MinGW release
`20260922`, clang **23.1.2**, from the official archive pinned in
`toolchain-lock.json`. Its archive SHA-256 was verified before extraction and
execution. The builder records the supplied compiler identity; it does not
independently enforce the entire toolchain archive pin. Future builders must
verify the archive against that lock before using it.

From the repository root, with an already verified compiler directory:

```powershell
python -B tools/build_native_probe.py --toolchain <compiler-directory> --output build/native-probe-local
python -B tools/validate_native_probe.py --bundle build/native-probe-local
python -B tools/validate_native_policy.py --driver build/native-probe-local/policy_reference_driver.exe --report build/native-probe-local/policy-validation.json
```

Use a new build directory for each build. The builder validates localization and
the shared compatibility profile, refuses an existing output directory, checks
source stability and records exact product hashes. It does not execute output
binaries; the next two explicit commands run only the owned offline hosts.
Run the two validators sequentially because both write reports in that folder.
The native probe validator is intended once per fresh build directory.

Detailed receipts remain under `build/native-probe-001-r4`. The committed
[sanitized receipt](validation/milestone-001.json) records identities and bounded
results without personal paths. The module's PE imports are Windows CNG,
Kernel32 and UCRT API sets; no external Python, CLR, libc++ or libunwind runtime
is imported. Runtime dependencies for a complete future mod remain undecided.

## What remains

1. Port and compare the habitat selector, shuffle reservations, roster changes,
   settings migration and persistence. Preserve every existing default/schema.
2. Resolve verified backups for normal Steam startup. A DLL running inside NMS
   cannot provide the current **closed-game pre-launch** backup by copying saves
   after startup; no weaker guarantee has been silently substituted.
3. Establish loader coexistence and a safe game lifecycle before installing any
   hook. Audit each ABI and the special native quick-binding filter separately.
4. Port native integration and the X-menu, including callback ownership. The
   existing menu thread stop is a known issue, not fixed by changing languages.
5. Complete native localization, live acceptance and distribution review.

See [loader provenance](../docs/research/NATIVE-LOADER-SOURCES.md), the
[port map](../docs/research/NATIVE-PORT-MAP.md), and
[Nexus investigation](../docs/research/NEXUS-SELF-SERVICE-INVESTIGATION.md).
All fourteen player catalogs remain unchanged: this experiment introduces no
player-facing UI, language selection or translated-rendering claim.
