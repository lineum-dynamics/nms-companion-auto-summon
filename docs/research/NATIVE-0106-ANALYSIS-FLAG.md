# Controlled MSVC analysis-flag comparison — 28 October 2026

The six fixed inactive startup cases did not reproduce Yogi in completed rows.
Three full cases, including real inspection with REF/ICF, have all eight earlier
Yogi vendors Undetected. The real frozen 0.10.6 module remains Yogi-positive.
Startup inclusion alone is not sufficient under these controls. The adapters,
metadata and build recipe remain different; no private detector rule is known.

## Concrete recipe discriminator

The maintained full MSVC DLL command includes `/analyze`; startup diagnostics
do not. Microsoft's [compiler documentation](https://learn.microsoft.com/en-us/cpp/build/reference/analyze-code-analysis)
describes analysis and normal object generation; it does not establish that
this switch changes executable behavior. Its [predefined-macro reference](https://learn.microsoft.com/en-us/cpp/preprocessor/predefined-macros)
states `_PREFAST_` is defined when `/analyze` is enabled. No direct use appears
in the owned native sources. Effects through SDK/library headers or object
layout remain a hypothesis. Do not remove analysis from ordinary builds or
claim this is a correctness fix.

## Registered byte-first procedure

Use the signed Microsoft tools on an isolated owned Windows CI runner, fixed
source mirror `C:/Projects/nms-companion-auto-summon-compat-cosmos-706`, unchanged
native sources, generated catalog/profile/mapping, resource/version 0.10.6,
`/MT`, `/O2`, `/Z7`, `/DEBUG:FULL`, `/Brepro`, REF/ICF and PDB basename mapping.

1. Build A in `build/msvc-0106-a` using the original DLL `/analyze` command.
   Require exact frozen ASI SHA-256
   `30cc9542a2af3529fd4f3a2299d6331bddf51b61f8213a0a1a779b472789de3d`.
   A mismatch stops interpretation; it is not evidence against the flag.
2. Build B in `build/msvc-0106-b`, omitting only DLL `/analyze`. The explicit
   comparison flag requires candidate mode and the existing owned-CI guard.
   Verify identical source/generated/profile/mapping/version inputs, resource
   source and normalized DLL commands differing only by the one switch.
3. If the DLL bytes match, reject this output-byte explanation. Reuse the
   existing exact-file evidence; no new VirusTotal upload, third build or full
   functional repeat is justified. The factory-failure control runs during B.
4. If bytes differ, run the existing complete owned functional bundle on B,
   including unsupported hosts, plus the factory-failure control. Rebuild B as
   C in `build/msvc-0106-c` and require DLL byte identity, without claiming PDB
   identity. Run the exact B Defender custom scanner with EICAR positive control,
   preserving actual definition date/refresh failures and unchanged settings.
5. Only then retain a distinct ASI/PDB for independent PE comparison. Compare
   resources, imports/exports, section and debug metadata before considering an
   exact-file multivendor submission. New bytes need a separate action-time
   upload approval; this CI does not submit them to VirusTotal or Nexus.

The controller strips token/secret/password/credential environment entries from
child processes. It never executes native code on the owner PC, accesses NMS
or saves, changes protection settings or promotes a release. Evidence is staged
on the workspace volume before artifact upload. Failed gates retain reports,
never a selected replacement. Default source-audit/player-candidate commands
retain analysis. This normal full module is not an inactive diagnostic probe:
its unchanged exact-game guards remain authoritative.

## Interpretation limits and next action

Source syntax and recipe review precede CI. Build-byte reproduction, functional
validation, scanning and PE readback are **NOT CHECKED** until the new CI result
is read. Byte equality rules out only this flag's output effect in this recipe.
Byte inequality identifies a controlled build difference, not a virus, detector
cause, source defect or future Nexus acceptance. No version bump, player default,
native mapping, compatibility claim or localization meaning is changed.

Target remains Windows/Steam Cosmos 7.06, build 25732212, executable SHA-256
`13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499`.
Source revision, artifact identity, game compatibility and distribution status
remain separate. The next action is one controlled CI comparison and readback;
support remains unsent.


## Initial gate result and revised current-image comparison

[Initial run 40714275447](https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40714275447)
correctly stopped before building B. Image 20261026.347.1 produced A SHA-256
`a41fc094e98332682200d6c70857cc21be327843734127c092fc7484e1b583f7`, not
frozen 30cc9542 from image 20261022.344.1. All recorded native/locale/profile/
generator inputs and generated hashes match. Only the Python builder's recorded
source hash differs; its actual DLL command is byte-for-byte identical. The
three recorded Microsoft executables also match. The image change is observed,
not an identified explanation of the binary difference. Header/library hashes
were not captured on the earlier image, so they remain NOT CHECKED historically.

Independent ordinary candidate run 40714275407 built the same a41fc094 bytes
twice, passed the complete owned bundle and factory-failure control, then failed
its scanner gate. Signature updating changed the platform from 4.18.26090.9 to
4.18.26100.4 while the service/engine became unavailable. The EICAR positive
control returned RPC error 0x800106ba; no exact-module scan ran and no binary
was retained. Source-audit run 40714275317 succeeded. This is a scanner-tool
failure, not a detection or an AV improvement. Sanitized readback:
[NATIVE-0106-ANALYSIS-FLAG-INITIAL.json](NATIVE-0106-ANALYSIS-FLAG-INITIAL.json),
SHA-256 `6af29ff96b797f1cfc3a68a487d7e02f906e01effd77ebda75d89f020d8518d9`.

The scanner helper now waits at most 55 seconds after update for a running
service, nonzero engine and available signatures, then selects and verifies the
active signed scanner. It neither changes service settings nor weakens endpoint
protection. A failed readiness/control still stops retention. The actual fix's
remote behavior is NOT CHECKED until readback.

The revised experiment is registered before its next run: use only image
20261026.347.1 and the independently double-reproduced a41fc094 baseline, with
its passed owned-validation receipt ed0fd1b0700340e44f39dd5d5c2363f247294c097ccdec6faae7dda461bb8fb5.
Keep the exact same native sources, resource and normalized DLL command; build
A with /analyze and B without it. A must reproduce a41fc094, and no other
argument/input difference is permitted. Inventory the configured include,
library and native compiler directories to support later image comparisons;
this inventory does not prove every file was consumed. Historical original-image
flag attribution remains inconclusive regardless of this new result.

If A equals B, /analyze has no output-byte effect on this current recipe; reuse
the existing passed functional evidence for identical a41fc094 and do not repeat
it or a third build. If B differs, run the complete owned suite and reproduce
B as C. In both cases a new positively controlled exact-module scan is required
before retaining ASI/PDB for independent PE comparison. Existing 30cc9542 VT
verdicts do not transfer to a41fc094. No automatic VT upload, player version
bump, source/guard change or release is authorized by this protocol.


## Rolling-image guard readback and paired-baseline revision

The revised run 40716983929 at e382e974 stopped before compilation because
GitHub assigned the older 20261022.344.1 image again. The job log explicitly
identifies it; no flag result or scan is counted. Single-image gating was too
narrow for the live rolling pool. The next run registers both independently
reproduced profiles below, selected only by the observed exact image identity,
never by a detection score or a newly produced output. Unknown images stop.

| Image | Required A SHA-256 | Prior owned full-bundle receipt |
| --- | --- | --- |
| 20261022.344.1 | 30cc9542a2af3529fd4f3a2299d6331bddf51b61f8213a0a1a779b472789de3d | CI 40653804116 / 35e23e7b119b7fe3cd89132a24a6e14c9711fea894d55c3595707107dc4efd27 |
| 20261026.347.1 | a41fc094e98332682200d6c70857cc21be327843734127c092fc7484e1b583f7 | CI 40714275407 / ed0fd1b0700340e44f39dd5d5c2363f247294c097ccdec6faae7dda461bb8fb5 |

All input/command, flag-only, reproduction/validation and positive scan gates
remain. An equality conclusion covers only the actually used image. If the
older profile runs, it can directly test the frozen 30cc9542 recipe; otherwise
historical-image attribution remains untested. The scanner fix's actual
post-update control remains NOT CHECKED. No binary was retained by either
failed comparison run; no new VT submission or player edit occurred.
