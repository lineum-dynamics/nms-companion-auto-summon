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
