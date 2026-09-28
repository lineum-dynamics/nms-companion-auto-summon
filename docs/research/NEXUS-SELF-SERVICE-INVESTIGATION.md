# Nexus self-service investigation

Checked 28 September 2026 after the owner explicitly declined contacting
Nexus. This is research and a bounded architecture proposal, not a cleared
release, accepted migration, or native prototype. Existing uploaded packages
and installed sessions remain unchanged. No person/vendor was contacted, no
new sample was uploaded and no scan was requested.

## Identified component

The completed report for the exact 0.9.3 launcher is **3/71**: Bkav Pro
`W32.Malware.2D7F7A26`, McAfee Scanner `Ti!0DF7E0930C40`, SecureAge `Malicious`.
Bkav gives the ZIP the same label. This identifies the launcher as a flagged
component; it does not identify the triggering method, a malware family,
confirmed false positive or the sole Nexus rejection cause.
[Exact report](https://www.virustotal.com/gui/file/0df7e0930c407ecdb64eba6c79ff7bae535606d9d71932e8342926e6b6120172/detection).

The exact label, its suffix and ZIP hash returned no public vendor explanation
in the checked searches. SecureAge's engine uses AI classification, but that
general property cannot adjudicate this file. McAfee's suffix visibly matches
the first twelve EXE hash characters; its precise taxonomy was not established.
[VirusTotal's SecureAge integration](https://blog.virustotal.com/2019/05/virustotal-secureage.html).

Conan's maintainer attributes a different Bkav label to PyInstaller/InnoSetup
packaging. Our direct-csc launcher uses neither, so that diagnosis is not
transferable. DistroAV documents installer-only flags and subsequent vendor
review; it provides no general code fix for our launcher.
[Conan](https://github.com/conan-io/conan/issues/17862#issuecomment-2687293655),
[DistroAV](https://github.com/DistroAV/DistroAV/issues/1309#issuecomment-2991550265).

## Nexus is a separate gate

A Nexus moderator explicitly describes automatic EXE quarantine. Other staff
explain that VirusTotal is only one screening input. These statements support
an executable-related check as a plausible independent obstacle, not a precise
diagnosis of file 49197. No public numeric threshold or signing exemption was
established.
[Moderator reply](https://forums.nexusmods.com/topic/13531602-file-was-quarantined-after-uploading-a-new-mod/),
[Staff discussion](https://forums.nexusmods.com/topic/13533626-mod-updates-keep-getting-quarantined/).

The Community Manager states that review is initiated by author contact;
there is no automatic queue that will release the current file merely after
waiting. No documented author-side release control was found. The owner's
no-contact instruction is retained; the unsent request is not a pending action
to execute without new authority.
[Community Manager statement](https://forums.nexusmods.com/topic/13539136-automatic-queue-for-manual-file-verification-request-when-new-mod-releases-get-quarantined/).

## Independent package inventory

- 1,897 files, including 95 PE binaries: 5 EXE, 14 DLL, 76 PYD.
- Authenticode inventory: 31 Valid, 64 NotSigned; no invalid signed result.
  Signature status is provenance information, not malware clearance.
- 21 cached upstream artifacts match their pinned hashes and sizes. All 1,838
  vendor-origin runtime files match the upstream bytes, including stdlib files.
- No complete nested ZIP structure or tested common archive signature remains.
  `runtime/Lib/site-packages/PyWin32.chm` is an unchanged compressed Help
  container (ITSF), SHA256
  `b70a571fd19cb48387744155fdd9a7948ce13553065fa36bee0b8421f1aa4285`.
  Whether Nexus rejects this container is unknown. Four COFF linker libraries
  also remain; they are not ordinary compressed mod archives.
- Complete upstream wheels include unused demos/tests/help, three VBS and two
  JS test scripts, a stdlib development BAT, Pythonwin.exe and pythonservice.exe.
  The portable launch path does not call those programs or scripts.
- The owned C# source verifies files, displays localized controls and directly
  dispatches bundled Python. It contains no download/network, injection,
  installation/persistence, elevation or antivirus-changing function.

The independent review did not find a vendor-byte mismatch or an unexplained
compiled addition. It cannot prove absence of a vulnerability. Removing an
unrelated demo would not explain the shared EXE/ZIP detection. Any future
runtime reduction needs a supported dependency closure and functional tests.

## Comparable NMS architecture

Planetary Surveyor's author reports moving from Python/pyMHF/NMS.py to native
C++, with a smaller distribution and normal game startup using a loader and
native module. The page is marked Safe to use. The same author also credits
Nexus review and an independent report sent to staff; the posts include a later
Defender complaint about its loader. Consequently this is an installation and
architecture precedent, not proof that rewriting guarantees automatic approval.
Its code/assets have restrictive reuse permissions; this proposal does not
copy, download for reuse or authorize their use.
[Author's description](https://www.nexusmods.com/nomanssky/mods/4521?tab=description),
[Posts](https://www.nexusmods.com/nomanssky/mods/4521?tab=posts).

## Next independent engineering step

Evaluate a separately developed native loader/module offline before deciding
on a migration. Its functional value would be normal Steam game startup and a
smaller dependency surface, with the existing mod behavior and X-menu. The
current Python implementation remains the working reference.

The feasibility gate must cover:

1. Documented, licensed loader provenance and coexistence with existing loaders;
   never overwrite an unknown DLL or merely rename the current EXE.
2. Exact game identity before native integration and reviewed mappings/hooks.
3. Verified backup and private preferences/session behavior before changing any
   live installation. Do not discard safeguards when removing the launcher.
4. Existing summon eligibility, manual-dismissal handling, habitat selection,
   shuffle, menu callbacks and language catalogs. No gameplay-limit changes.
5. Offline equivalence and lifecycle tests, followed by owner-scheduled live
   acceptance. Nexus availability is a separate observed release condition.

Upstream NMS.py supports separately installed dependencies and mod directories,
but a source-only distribution plus generic `pymhf run` would bypass our exact
process/DLL checks, foreign-library rejection and mandatory backup. Preserving
our guarded bootstrap could make that design viable, at the cost of more setup
steps. It is not yet a replacement for the agreed easy portable installation.
[Official NMS.py documentation](https://github.com/monkeyman192/NMS.py).

No native implementation, automatic approval, second-PC or multiplayer result
is claimed. This research changes no player-facing wording; all fourteen
catalogs remain unchanged.
