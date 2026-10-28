# Fixed VERSIONINFO text ablation - 28 October 2026

The original frozen 0.10.6 ASI 30cc9542 reproduced exactly with /analyze on and
off in run 40717532898. That switch cannot explain its Yogi difference from
inactive controls. The same exact module passed an exercised Defender custom
scan with definitions 1.463.10.0 dated 28 October 10:14:03 UTC. That is not a
multivendor or Nexus verdict. Yogi remains in the dated full-module VT control.

## Registered single factor

The full player ASI and inactive startup controls differ in VERSIONINFO text,
export-file/debug metadata and forced-refusal code. This test removes only the
optional StringFileInfo/VarFileInfo resource blocks from the normal full module,
while retaining fixed version numbers 0.10.6.0, prerelease flags, DLL type and
OS values. No byte patching, obfuscation or arbitrary variants.

Both use the same CompanionAutoSummon.asi/PDB basenames, sources, generated
catalog/profile/mapping, /analyze, /MT, /O2, /Z7, REF/ICF and /Brepro. Normal
builds retain their unmodified resource. The explicit diagnostic flag requires
candidate mode and rejects simultaneous analysis-flag changes. Its receipt is
not a player release or a new supported game build.

A must reproduce the independently known image-specific baseline at the
original msvc-0106-a path: 30cc9542 on 20261022.344.1 or a41fc094 on
20261026.347.1. Unknown images or mismatched bytes stop interpretation. B in
msvc-0106-b changes only the resource text blocks; normalized DLL commands,
source/generated inputs and fixed resource numbers must otherwise match.
Run the full owned bundle and startup factory-failure control on B, reproduce
B as C, and require a positively controlled exact Defender scan before retention.
Record configured include/library/compiler-directory inventories for comparison
with the retained 7,170-file old-image inventory. Inventory inclusion does not
prove every file was consumed.

After CI, independently compare A/B PE exports/imports, executable sections,
fixed resource fields and program data. Require exact .text/.data/.pdata/
.fptable/.reloc byte identity. Any .rdata difference must be identified as
specific CodeView/debug/export timestamp metadata, with basename preservation;
unexplained program-data differences block a metadata-only interpretation.
Resource and consequent PE-header/debug identity changes are expected, but must
be recorded rather than calling behavior equivalent from source alone.

B is the full guarded native module, NOT an inactive probe. It retains all
exact-game/profile refusal, initialization, eligibility and hook code. Owned
CI hosts remain unsupported and no game is accessed. It is never installed
or executed on the owner PC. Packaging, game/Nexus acceptance and AV clearance
stay false. No automatic VT submission; freeze/review exact B before any new
action-time terms/sample-sharing approval.

## Interpretation and stop rules

If identical program sections but different optional resource metadata produce
different VT labels, metadata is a sufficient static-file classification
discriminator under that scan. It is not a runtime correctness fix, universal
false-positive finding or basis for shipping a stripped-resource player module.
Preserve ordinary branding; a new player release needs its own complete checks.
Equal labels reject only this resource-text explanation; forced-refusal/
interface/layout differences and the private rule remain open. Do not keep
inventing resource variants or select player bytes by score.

Build/validation/reproduction/scan/PE and multivendor results are NOT CHECKED
until readback. Target: Windows/Steam Cosmos7.06 / build25732212 / executable
SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
No native RVA/profile, gameplay policy or localization meaning changed.
Next: this one resource ablation and exact-file readback; support remains unsent.
