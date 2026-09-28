# Unsent Nexus quarantine review draft

Status: prepared for owner review only. Do not send without explicit authority.
The owner previously declined external contact; a general request to fix
packaging does not authorize emailing a provider or making the private repository
public. Refresh the exact file's scan result before using this draft.

Recipient: support@nexusmods.com

Subject: Review request: unpublished NMS mod 4579, portable test files 49196/49197

Hello Nexus Mods team,

We are the authors of Companion Auto Summon for No Man's Sky - by Lineum
Dynamics, uploaded by LineumDynamics. The mod page remains unpublished:
https://www.nexusmods.com/nomanssky/mods/4579

File 49196 (0.9.2-test) was quarantined. We preserved it and investigated its
exact bytes. Its VirusTotal report showed 3/60 detections for the ZIP and 8/70
for our managed launcher. We are not asking you to ignore those findings.

We found a concrete packaging issue against your nested-archive guidance:
the embedded Python runtime contained python311.zip. File 49197 (0.9.3-test)
extracts all 649 original members unchanged and records their source hashes.
It also adds accurate product/company/version metadata and actual build inputs,
and fixes an unrelated Steam-discovery access error. We made one corrected
release; we have not renamed or repeatedly rebuilt files to alter scan results.

0.9.3-test ZIP SHA256:
d87f868c618aec200cf276aae1faf81748eeaf7be26bd1e21a8594590627e383

Its unsigned launcher EXE SHA256:
0df7e0930c407ecdb64eba6c79ff7bae535606d9d71932e8342926e6b6120172

The launcher is a Windows .NET Framework WinForms UI and integrity gate. It
hashes the package then starts package-local Python. The mod deliberately uses
pyMHF native hooks in the exact supported NMS executable, after executable
validation and a verified private backup. It does not request administrator
rights, install services, modify antivirus settings or download payloads.

The ZIP contains launcher source, generated AssemblyInfo.cs, resolved Windows
manifest, exact locale resource and compile-only instructions in
app/BUILD-LAUNCHER.txt, plus the owned Python/mod source and pinned dependency
identities/licenses. An independent build from those supplied inputs reproduces
all compiled bytes except the compiler's timestamp and module identifier.
This is provenance evidence, not a claim of a false positive.

The canonical source repository is
https://github.com/lineum-dynamics/nms-companion-auto-summon
It is currently private. No repository access has been granted by this draft;
the supplied compiled-source inputs are also present in the uploaded ZIP.

Please review these retained files and identify any remaining file or policy
issue that prevents the portable distribution from being accepted. We will
keep the page unpublished until distribution and player testing are ready.

Thank you,
Lineum Dynamics

## Information intentionally excluded

No saves, settings, private player logs, credentials, account tokens, payment
data or game binaries. Sending would not authorize public release, changing
repository visibility or contacting antivirus vendors with further samples.
