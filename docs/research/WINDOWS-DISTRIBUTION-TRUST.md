# Windows distribution trust and Nexus quarantine

Research checked on 28 September 2026 against the primary sources linked below.
This is distribution guidance, not a malware clearance. No provider was
contacted, no sample was submitted, no signing service was purchased, and no
running game was inspected or changed.

The exact retained 0.9.2 archive and executable are documented in
[PORTABLE-SCAN-092](PORTABLE-SCAN-092.md). Their observed detection counts were
3/60 and 8/70 respectively. A matching build receipt establishes provenance;
it does not establish why an engine flagged the program or overrule its result.

## Three distinct systems

| System | What the current evidence establishes | What it does not establish |
| --- | --- | --- |
| Nexus file moderation | File 49196 is quarantined and cannot currently serve the intended tester download. | The exact failing internal check, or automatic release after a code change. |
| VirusTotal engine results | The exact owned launcher is flagged by eight engines in the retained report. | The triggering instructions, a confirmed false positive, or a Microsoft Defender finding. |
| Windows SmartScreen reputation | The launcher is unsigned; Microsoft documents file and publisher reputation checks. | That SmartScreen caused the Nexus quarantine or these antivirus detections. |

Microsoft describes SmartScreen reputation as a combination of file-hash and
publisher evidence. Newly signed files may still warn, and current guidance
explicitly says EV certificates no longer provide an automatic initial bypass.
Unsigned new versions establish reputation separately. Signing is therefore a
publisher identity and distribution investment, not a promised antivirus
clearance. [Microsoft: SmartScreen reputation](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation)

## A concrete package-format incompatibility to address

Nexus currently lists nested archives among its rejected upload structures.
The retained `build/portable-092-r1/portable-manifest.json` declares one such
payload: `runtime/python311.zip`, SHA256
`7d0f59c930e7d3d9352399ea3c95c0272489b3c09a8e95faaedfa8a23e20e5b1`.
This is a documented structural incompatibility to investigate independently
of the flagged executable. It is not proof that this check caused file 49196's
specific quarantine. The same help page recommends keeping a quarantined file
for moderator review and describes contacting support or a moderator as the
route to unblocking it. It gives no current numerical antivirus threshold.
[Nexus: Why has my mod been quarantined?](https://help.nexusmods.com/article/117-why-has-my-mod-been-quarantined)

The legitimate technical next step is to evaluate shipping the same pinned
standard-library contents as ordinary extracted files, retaining licensing,
origin hashes, isolation, integrity validation, and the exact game guard.
Do not rename the archive, obscure its signature, or replace it with a downloader.
Test both ordinary Python initialization and the owned native-child interpreter
probe before considering that format usable. This is a project recommendation,
not a claim that the revised layout has already passed or will be accepted by
Nexus. Python documents application-local embedding, editable isolated `._pth`
paths, and distribution of dependencies with the application; our chosen
extracted layout still needs its own verification.
[Python 3.11 on Windows](https://docs.python.org/3.11/using/windows.html#the-embeddable-package)

Nexus distinguishes its own security checks from VirusTotal scans. A red status
can mean either an internal failure or significant detections, and requires
manual review. Its documentation also recognizes that mod techniques or unusual
structures can produce false positives; that general explanation is not a
determination about our file.
[Nexus: Virus Scanning](https://help.nexusmods.com/article/128-anti-virus-false-positives)

## Useful owned-launcher improvements

Accurate `AssemblyTitle`, `AssemblyDescription`, `AssemblyProduct`,
`AssemblyCompany`, `AssemblyVersion`, `AssemblyFileVersion`, and
`AssemblyInformationalVersion` make the file's identity and release inspectable
in Windows. Keep the approved product name, Lineum Dynamics attribution and an
exact release version; do not impersonate another publisher. These attributes
are metadata, not a publisher certificate or an antivirus exemption.
[Microsoft: Assembly attributes](https://learn.microsoft.com/en-us/dotnet/standard/assembly/set-attributes)

The existing builder uses the normal .NET Framework C# compiler without
`/nowin32manifest`. Microsoft documents that the compiler already supplies a
default `asInvoker` manifest. Consequently, absence of an owned custom manifest
is not evidence that the executable requests elevation or lacks one. An explicit
`/win32manifest` can make the same ordinary-user requirement reproducible and
reviewable. Preserve `asInvoker` and `uiAccess="false"`; do not add administrator
requirements as a speculative remedy.
[Microsoft: C# resource compiler options](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-options/resources#win32manifest)

A custom Win32 manifest can state the application identity, four-part version,
`amd64` architecture and Windows 10/11 compatibility. Keep it embedded in the
executable. Do not add DPI or code-page switches without testing their actual
UI and native-integration effects. These declarations describe runtime behavior;
they do not authenticate the developer.
[Microsoft: Application manifests](https://learn.microsoft.com/en-us/windows/win32/sbscs/application-manifests)

The project should preserve transparent source, dependency provenance, stable
versioning and immutable release receipts. Any replacement should have an
ordinary functional reason and a reviewed diff. Recompiling arbitrary variants
until a scanner stops detecting them would not establish a repaired defect.
Keep the old artifacts and report identities for comparison.

## Signing, if separately authorized

Use a publicly trusted Authenticode identity for Lineum Dynamics if the owner
chooses to establish one. A .NET strong name is an assembly identity mechanism;
Microsoft explicitly warns that it is not a trust decision about the publisher.
A self-generated strong-name key is therefore not a substitute for Authenticode.
[Microsoft: Enhanced strong naming](https://learn.microsoft.com/en-us/dotnet/standard/assembly/enhanced-strong-naming)

Microsoft Artifact Signing currently supports organization validation in the
European Union, which includes the Czech Republic. The service requires an
Azure setup and legal-entity identity validation. This research has not verified
Lineum Dynamics' eligibility or existing resources and authorizes neither
account creation nor spending.
[Microsoft: Artifact Signing setup](https://learn.microsoft.com/en-us/azure/artifact-signing/quickstart)

For a future signing pipeline, sign the final owned executable using SHA256 and
a timestamp, verify it with the Authenticode policy, and only then record its
final hash and build the distributable ZIP. `signtool verify /pa /v` is the
documented ordinary Authenticode verification mode. A successful signature check
establishes signature validity, not a clean antivirus result. Do not modify the
signed executable afterwards or overwrite vendor identities on third-party files.
[Microsoft: SignTool](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool)

## External review and its authority boundary

Microsoft offers a software-developer sample submission route for disputed
Microsoft detections and returns an analyst determination. Its guidance says to
wait for that determination before escalating a dispute. That is distinct from
SmartScreen consumer reputation and cannot correct other vendors' detections or
unlock Nexus moderation. None of the eight retained launcher detections is
identified as Microsoft Defender, so Microsoft submission is not presently an
evidence-based primary remedy for this exact report.
[Microsoft: File submissions](https://learn.microsoft.com/en-us/unified-secops/submission-guide)

The public submission page states that submission details are retained for up
to 30 days. Its displayed MSI consent also describes US-only storage for threat
analysis and malware research in a non-ISO-compliant system, with confidentiality
and integrity safeguards. Do not interpret the details-retention statement as a
verified promise to delete every submitted binary after 30 days. Before any
future submission, review the actual consent shown to that account and submit
only an explicitly approved artifact, never saves, credentials or private logs.
[Microsoft: Submission form and consent](https://www.microsoft.com/en-us/wdsi/filesubmission)

The owner's existing no-contact instruction remains in force. An internal
evidence packet can be prepared without sending it. Actual Nexus moderator
contact, vendor submissions, certificate enrollment and purchases require the
appropriate new authority. No amount of local testing can truthfully be reported
as a provider's approval. Completion requires observing the intended final file
available from Nexus and preserving that file's exact identity.
