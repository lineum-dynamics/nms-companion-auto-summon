# Fixed static component probes — 27 October 2026

The exact 0.10.5 ASI completed VirusTotal at 21:43:19 UTC:8 malicious,63 undetected,
four unsupported,71 evaluated. All eight flagged labels name Yogi. This does
not resolve the release blocker or prove a false positive. The complete
candidate verdicts are retained separately; no player bytes are varied here.

## Preregistered comparison

Build exactly these four progressive diagnostic libraries once per fixed
source/toolchain, with identical filenames, inert entry points and version
resources. They are not player candidates or replacements.

| External receipt label | Included production sources |
| --- | --- |
| crt | Common inert probe and the standard Microsoft CRT |
| minhook | crt plus the pinned guarded MinHook C/HDE objects |
| binding | minhook plus binding_guard.cpp |
| core | binding plus policy/selection/storage/runtime/backup/menu.cpp |

The production bootstrap and host-inspection layer remain outside these
libraries. Each exports only the common diagnostic status function; no
production method is called by the CI smoke host. Source methods are kept
through `/OPT:NOREF /OPT:NOICF` so a negative result cannot silently follow
linker deletion of the component under investigation. All four use the same
compile/link/debug policy. Their basename is CASComponentProbe.dll, their
resource is identical, and external case directories distinguish them.
Compilation and load/status/unload controls must pass; the owner PC never
loads the libraries. All source/dependency/tool hashes are recorded.

## Interpretation registered before any component upload

- A positive crt result would not implicate native game logic; common compiler,
  runtime/probe features would need separate attribution.
- A new positive at minhook/binding/core narrows the source inclusion boundary
  under these controls. It does not establish the proprietary rule or a
  malicious behavior, and does not prove one exact function is responsible.
- All-negative component results leave bootstrap/inspection or a combination
  effect unresolved. Unused-code retention and different reachability limit
  comparison with the actual player module.
- No probe result authorizes deleting a guard, obfuscation, packing, stripping,
  changing a player binary repeatedly for a score, or declaring it clean.
  A player-source repair still needs a demonstrated engineering reason.

The next action is the isolated CI build and exact receipt readback. Any
multivendor upload needs a concrete approval for the four frozen diagnostic
files and the displayed sharing/terms form. There is no automatic antivirus
submission or support/vendor contact in this workflow. Existing player ASIs,
their hashes and original reports remain preserved.

## Completed readback — 28 October 2026

Run 40591032747 at 72e76b7e5baa5d78cf991b0cb76c25a8ee9b29e4 built all four
frozen DLLs. All 86 recorded source digests match that commit. Owned load/status/
unload checks passed. The owner explicitly approved all four exact files,
displayed terms and sharing; all were submitted and completed.

| Probe | Bytes | Analysis UTC on 28 October | Result |
| --- | ---: | --- | --- |
| crt | 494,080 | 07:22:27 | 1/69 Cynet; Google timeout, Zillya failure |
| minhook | 507,904 | 07:23:00 | 1/71 Cynet |
| binding | 532,480 | 07:23:32 | 1/71 Cynet |
| core | 1,452,032 | 07:24:14 | 1/71 Cynet |

Every probe has 75 recorded vendor rows, four unsupported file-type rows, and
Cynet's `Malicious (score: 100)`. All eight Yogi-positive vendors from 0.10.5
(ALYac, Arcabit, BitDefender, CTX, Emsisoft, eScan, GData, VIPRE) return
Undetected for every probe. MinHook, binding and core are not sufficient
triggers under these fixture controls. This does not exclude interactions,
different reachability or bootstrap/host-inspection code. The core includes
the generated language catalog through runtime.cpp; it is not a catalog-free
control. The probes are never player payloads and are not universally clean.

The initial mandatory-label DOM parser refused CRT's unlabeled Zillya failure
row. The corrected visible vendor/status parser retains that failure with a
null label and asserts 75 distinct rows. Google timeout and Zillya failure are
not treated as negative results. Full tables, exact hashes and direct report
links: [component evidence](NATIVE-0105-COMPONENT-EVIDENCE-20261028.json), SHA-256
`3eff44fb61c662094137516c5d25a86a88b6220ed8304cee4acd589d30367c69`. The identity manifest preserves its initial pre-upload
review state; this later record is authoritative for completed submissions.

Source review also rejected an existing-filter RWX hypothesis: binding_guard
already allocates writable data then changes/verifies execute-read protection.
No redundant protection repair or weakened guard is proposed. The complete
bootstrap's CreateThread-to-CRT mismatch has an independent documented
engineering reason; see [the 0.10.6 correction](NATIVE-0106-CRT-THREAD.md).
