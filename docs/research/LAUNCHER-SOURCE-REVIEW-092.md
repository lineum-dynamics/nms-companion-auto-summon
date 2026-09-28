# Independent owned-launcher source review for 0.9.2

Recorded on 28 September 2026. This is a bounded review of the owned launcher,
bootstrap and packaging code, prompted by the retained Nexus quarantine. It is
not a malware clearance, a complete dependency audit or a scanner-causality
finding. No candidate was rebuilt, uploaded or executed during this review.
The running game and its host were not inspected, modified or terminated.

Reviewed sources:

- `launcher/PortableLauncher.cs`
- `tools/build_portable_entrypoint.py`
- `tools/portable_launcher.py`
- `tools/portable_host_support.py`
- `tools/build_portable_distribution.py`
- Related owned `portable_sitecustomize.py`, host compatibility checks and tests.

The exact retained scan identities and provenance are recorded separately in
[PORTABLE-SCAN-092](PORTABLE-SCAN-092.md). Repository instructions and the current
development, design, localization and manifest status were read first.

## Findings

### P2: Windows release identity is incomplete

`PortableLauncher.cs` declares no assembly title, description, product, company,
file version or informational version. `build_portable_entrypoint.py` supplies
no owned application manifest or icon.

Read-only `FileVersionInfo` inspection of the retained executable confirmed:

| Field | Retained value |
| --- | --- |
| FileDescription | Empty |
| ProductName | Empty |
| CompanyName | Empty |
| FileVersion | `0.0.0.0` |
| ProductVersion | `0.0.0.0` |
| OriginalFilename | `CompanionAutoSummon.exe` |

Static PE resource reading confirmed the compiler-default application identity
`MyApplication.app`, version `1.0.0.0`. Its execution level is already
`asInvoker`, with `uiAccess=false`; it does **not** request elevation.
`Get-AuthenticodeSignature` reports `NotSigned`.

A normal release should identify the approved product and author consistently
in assembly metadata, carry the exact release version, and use an owned
application manifest while retaining `asInvoker` and `uiAccess=false`. A normal
product icon can improve recognition. These are legitimate release identity
improvements with useful independent verification in Explorer/PE metadata.
There is no evidence that their absence caused the detections, or that adding
them would clear quarantine. Authenticode signing is a separate publisher
identity operation; assembly strings are not a signature or a malware verdict.

### P2: Unrelated protected processes can block Steam discovery

In `portable_host_support.py`, `bounded_steam_start` obtains process names for
every enumerated process. The inner handler catches `NoSuchProcess` only. An
`AccessDenied` from the name of an unrelated protected process escapes to the
outer handler and raises `PortableLaunchError("Steam could not be identified")`,
even when the iterator would subsequently return a valid Steam process.

An in-memory mock reproduced this order:

1. An unrelated process raises `AccessDenied` from `name()`.
2. A valid Steam process follows it in the mocked iterator.
3. The helper aborts before requesting the Steam URI.

The reproduction imported only the helper and used mock process objects. It
performed no live process enumeration, URI opening, attachment or injection.

Handle inaccessible unrelated candidates as a discovery limitation, while
keeping strict checks on the selected Steam parent and actual game target.
Do not weaken the game executable hash, actual-process-handle injection guard,
ambiguity refusal or launch argument restrictions. Add a focused mock test.
This is a reliability issue; no relation to antivirus detection is established.

## Behaviors examined without finding an unrelated payload

The C# executable implements a normal WinForms UI, a pinned manifest digest,
SHA256 checks and two package-local child-process paths. It uses neither shell
execution nor elevation, does not download or install dependencies, does not
register startup persistence, and contains no injection code. The hidden child
is intentional: normal Start launches the packaged `pythonw.exe`; Check uses
the packaged `python.exe` with redirected bounded output. The only C# process
termination applies to its own read-only check child after 120 seconds.

The Python bootstrap verifies the package, preserves game saves through verified
private copies, stages a verified mod session, and dispatches to the maintained
guarded host. The host helper opens the fixed Steam game URI and intentionally
uses the existing native hook framework. Its Unicode initialization adapter
compiles bytes from an absolute local script path. The reviewed paths contain
no remote-source downloader, credential collector, unrelated command execution
or external data upload. This statement does not cover every vendor module.

The package builder uses explicit manifest allowlists and verifies the final
archive bytes. The C# digest and bundled hashes establish internal integrity
against the expected release contents; they do not independently authenticate
the publisher or establish that a release is harmless. In particular, the
Python-only validation consumes the package's own manifest and is not an
alternative publisher trust anchor.

No critical owned-code security vulnerability or unexpected executable payload
was established in this bounded review. This is not proof of absence, and it
does not resolve the scanner findings.

## Appropriate follow-up boundary

Retain the quarantined bytes and their reports. Correct the identified release
metadata and reliability issue as ordinary, documented code maintenance, with
focused tests and a distinct release identity. Keep exact build inputs, source
revision, compiler identity and artifact hashes available for independent
review. Do not describe a newly compiled binary as the original quarantined
artifact, or infer that a changed hash has solved the underlying concern.

Determining whether the original detection is erroneous requires evidence from
the detecting engines or a further independent security analysis. This review
does not authorize external contact, uploading private artifacts, removing
guards, obfuscation, binary padding, antivirus exclusions or scan-driven
trial-and-error rebuilds.

## Source follow-up after review

The unclassified-process discovery fix was implemented in
`tools/portable_host_support.py`: only the initial process-name classification
now skips `AccessDenied` as well as vanished processes. No inaccessible process
is accepted as Steam. Multiple identified Steam parents still refuse launch;
access failure while inspecting the selected Steam parent's children or a
child's name remains fatal. PID selection and the existing injection guard are
unchanged.

The focused `test_portable_host_support.py` suite passed **23 tests**, including
five added mock cases for this change and the existing actual-handle refusal
case. The tests performed no live process enumeration or game access. The
retained 0.9.2 distribution and its running host were unchanged. This source
maintenance is not evidence that the scanner concern has been resolved.
