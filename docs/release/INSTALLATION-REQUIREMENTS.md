# Companion Auto Summon for No Man's Sky — simple, reliable installation

by **Lineum Dynamics**

## Current portable candidate: 0.9.2-test

The player distribution uses a root **Companion Auto Summon.exe**, bundled
Python 3.11.9 and pinned dependencies. It contains production **0.5.1**,
combined **0.9.2-play-trial** and menu **0.9.1-diagnostics**. There are no player
Python/pip setup steps. Windows 10/11 x64, Windows .NET Framework 4, Microsoft
Visual C++ v14 x64 and Steam **Cosmos 7.04 / build 25442159** are required.

Normal start requires Steam open/signed in, exact package/game checks and a
private verified backup. Private session copies preserve the distribution and
existing external preferences. Closing the launcher is designed to leave its
host/game running. The packaged background child completed a verified 49-file
backup and registered both Mods and twelve hooks in NMS. The interactive C#
launcher was not opened or clicked. Visible pets, exit/restart, launcher-window
closure, second-PC and multiplayer acceptance remain unverified; see
[LIVE-092](../research/LIVE-092.md). The known menu thread stop has additional
bounded diagnostics, not a fix. The built archive passed 770 developer tests,
final native/executable/framework checks and relocated package checking without
a game launch. Its identity is recorded; upload/readback remains PENDING in [TESTER-HANDOFF](TESTER-HANDOFF.md).
Use [the player quick start](PORTABLE-QUICKSTART.md) for the simple workflow.

## Retained 0.9.1 development path

The earlier 0.9.1 PowerShell package used external Python and retained a
console-capable host. Its 403 production / 689 developer checks and read-only
preflights are historical evidence for that package, not portable acceptance.
The standalone developer script still has its separate panel. The running
090-r2 remains untouched; see [LIVE-090](../research/LIVE-090.md).

## Retained 0.8.7 installation evidence

The retained previous **0.8.7-play-trial** uses production **0.4.9-experimental**
and menu **0.8.5-branding**. Source validation passed 333 production
and 675 developer tests, without failures or skipped tests. The separate final directory
`build/quick-menu-play-trial-087-r1` contains 41 files (40 payloads and a manifest).
The original `087` is a retained, unlaunched output from before the correction of two Korean particles.
The real-framework check and all six controls with temporary preferences passed,
without native hooks or game access. Python `--check-only` and Windows
PowerShell 5.1 `-CheckOnly` passed against the installed game and runtime,
without launching, deploying or installing dependencies. In-game validation
remains incomplete. After the language correction, 24 localization tests,
the framework check and both preflights passed again for the final r1. Prepared,
unlaunched 0.8.6-r1 and retained 0.8.4 remain untouched. Final 0.8.7 / 087-r1
launched on 28 September 2026 after normal game closure and a fresh verified
46-file backup; both Mods and twelve native targets loaded at 11:07:26
(Europe/Prague). The first post-start check confirmed matching hashes for all
40 payloads, settings and remembered state. The player confirmed visible Nexus
summons after loading and leaving the ship, with a different Random pet each time.
The player also confirmed one native OFF/ON test: OFF prevented the exit summon,
ON alone summoned nothing, and the next exit did summon. Other preferences
remained unchanged. This is partial in-game evidence, not proof of a fix for
the earlier failure or a finished installer; see [LIVE-087](../research/LIVE-087.md).
PowerShell `-CheckOnly` validates the package, supported game and existing
runtime even while NMS runs. It creates, installs, stages and launches nothing.
Missing prerequisites are reported; correcting them requires a separate normal
launch with the game closed. A successful check is not in-game validation.

Normal setup and the host are protected by two fixed, distinct Windows session
leases, `Setup.v1` and `Host.v1`. They apply across package directories and live
for the lifetime of their open OS handles; closing the last handle releases
them even after a process crash. They are not lock files requiring manual
removal. If process enumeration fails, normal setup is refused.

The current hosts preserve the protection verified in 0.8.4: they check the
selected EXE before importing the framework and the actual target executable
through its process handle before each DLL injection. They reject inconsistent
configuration and foreign `pymhflib` extensions. The build also checks
`compatibility.json` against the host, native declarations and manifest.
An unknown or unreadable build cannot be forced, and preferences are not reset.

In that retained 0.8.7 package, nine compatibility messages use 14 catalogs of 41 keys each; 13 translations
remain without language review. Windows or `-Language` selects the language,
not detection of the game's language. `-NoDialog` suppresses the dialog while
retaining the console error. A bad catalog uses a short English package error.
This does not localize other launcher text or the native menu/HUD.
Two new product keys preserve the full title as a proper name and translate
the author credit; three launcher compatibility messages use the expanded title.
The short in-game name, setting captions and notices remain unchanged.

Production 0.4.9 retains passive diagnostics after the first logical active
state; menu 0.8.5-branding retains six controls, seven role icons and language
observation without enabling translations. Retained 0.8.7 / 087-r1 remains
unchanged. Live portability, complete translations
and safety of the future saved technology remain unverified; their requirements
and separate historical evidence follow below.

Historical production 0.4.4 / combined package 0.7.1 added passive diagnostics
after acceptance of a pet request. The installation approach, two Mod instances,
original preference paths and exact-game-version check remain intact.
Package 0.7.1 launched after a new backup on 27 September 2026 at 22:22:35;
registration of both Mods and 11 hook targets is confirmed. This is not an
Anomaly fix or a finished public installer. One actual summon after loading
in the Anomaly is confirmed by the player and the new active-pet observation;
repeatability and the cause of the earlier failure remain unresolved.
The original 0.7.0 is retained.

Owner requirement, as of 27 September 2026. This is a specification for the public package, not a description of a finished installer. Historical production 0.4.3 used Start-CompanionAutoSummon.ps1; combined package 0.6.2 ran production automation and experimental menu module 0.6.0 together in one host. Neither was a finished public portable installer.

Production 0.4.3 adds one deferred opportunity after successful local save loading alongside the existing ship-exit trigger. An appropriate local-player callback evaluates it with the same delay and original rules; no native summon occurs during deserialization. Existing settings remain authoritative and do not need changing. Manual dismissal does not cause repeated summoning. The development Settings preview subpage does not yet change preferences.

Historical 0.4.3 / 0.6.2 validation: 230 production tests (140 runtime), 341 developer tests and the actual production GUI and combined-folder checks outside the game passed. The subsequent 0.4.3 / 0.6.2 run on 27 September 2026, after a fresh backup, registered both modules with automation enabled. After a local save loaded at a station, Random selected one of five eligible pets and the native queue accepted the request approximately 2.69 seconds after arming; it was not a ship-exit request. The player confirmed actual appearance and clarified that the location was a station, not the Nexus. This verifies one station startup summon in Random, not all locations or the public installer.

Later in the same unchanged session, the player confirmed one manual dismissal without reappearance during observation. The exact location, dismissal time, observation duration and relationship to the earlier startup pet were not independently established. This result is therefore not described as dismissal at a station or immediately after loading. Planet, Nexus and Last manually selected startup, and broader regression checks, remain open.

The historical 0.4.2 / 0.6.1 run earlier that day established only module registration and a logged accepted station request, without player confirmation of appearance. This earlier record is not replaced by the newer result.

## Historical separate development candidate 0.7.0

0.7.0-play-trial adds only native automatic-summoning ON/OFF through the
original production 0.4.3 preference queue. Other settings and the manual
favourite are preserved. Pending application and session-only state are
displayed distinctly from a saved choice. It passed 408 developer tests and
a real pyMHF check with two Mods, 15 callbacks across 11 targets and temporary
settings outside the game. After normal closure and a fresh verified 43-file
backup, both Mods and 11 hook targets loaded on 27 September 2026 at 21:48:38
with automation ON. Complete in-game toggle testing is not yet confirmed;
this is not a finished public installer.

At that stage, the plan was to remove the temporary panel after the native
controls were complete. The 0.9.1 combined candidate disabled GUI
construction for the next trial, with acceptance still required. GUI dependency
removal is separate work; it is not implied by hiding the panel. A launcher and
background runtime remain necessary.

## Target player workflow

1. The owner downloads the validated 0.9.2-test ZIP from unpublished Nexus mod
   4579 and passes the unchanged ZIP to the second tester. Extract into a new folder.
2. Double-click **Companion Auto Summon.exe**. Use **Check installation** and,
   when needed, **Choose game folder**. Installation checking does not require Steam open.
3. Open Steam, sign in and choose **Start game**. A private verified backup is
   mandatory before launch. Keep the launcher open for the first live test.

The package includes its Python runtime. No terminal, pip setup or environment
changes belong in the portable player flow. A missing Microsoft Visual C++ x64
runtime gets a localized error and the official one-time installation procedure
in the quick start; no prerequisite is downloaded automatically. Administrator
rights are not a normal launcher requirement. Portable lifetime remains an
acceptance gate even though the graphical entry point is implemented.

## Packaging approach to validate

- An official portable Python distribution for Windows x64, pinned pyMHF and full dependency-chain versions, included licences and checksums.
- A small standalone graphical launcher. Its runtime will be included in the ZIP; installation-time network operations and an automatic updater are outside the target design.
- The portable source handles noninteractive host import and embedded-runtime preparation; the Windows Visual C++ runtime remains an explicit external prerequisite. Verify host and injected initialization through the final ZIP. An offline import check does not establish quiet live launch, target initialization or safe shutdown.
- Do not copy the development venv. Verify module, native-DLL and physical-path resolution when launched from a different directory and account.
- Keep source code available for inspection without bundling game files or personal state.

Official Python documentation describes the embedded distribution as an environment to include with an application; the application distributor should supply external packages. This supports the packaging direction but does not itself establish compatibility with this pyMHF version: [Python on Windows — embedded distribution](https://docs.python.org/3.11/using/windows.html#the-embeddable-package).

## Checks and understandable errors

- Discover Steam libraries automatically; allow explicit selection when the result is ambiguous.
- Validate the exact supported NMS.exe and our package integrity before native mod loading.
- Do not terminate a running game or attempt to attach a second launcher. Show a short instruction explaining what the player should do.
- Repeated double-clicks within a short interval must not create two mod instances.
- On a game mismatch, state the supported version and the detected version if reliably known; a long hexadecimal string alone does not belong in the main error message.
- A mismatch or inability to verify the version automatically prevents mod attachment. The maintained source retains the direct Python host check before the framework and actual-target-process verification before DLL injection. Nine compatibility messages are translated outside the game; no unverified native HUD is used. Preferences survive, and there is no option to force an unknown version. Python `--check-only` and Windows PowerShell 5.1 `-CheckOnly` run without launching, deploying or installing dependencies; their result must belong to the exact final package. Earlier guarded development launches do not validate a new portable runtime.
- Offer to open the log directory. Do not automatically upload logs or user data.
- Closing an ordinary control window must not silently terminate the game. The portable design keeps the host detached from the control window; that behavior still needs a live test.
- Do not disable Windows security, antivirus protection or script-execution rules. Absence of SmartScreen warnings or antivirus approval cannot be promised in advance.

## Updating and removal

- A new package must preserve settings and manual choices outside its own directory. Renaming to Companion Auto Summon retains `%LOCALAPPDATA%\NMS-AutoPet`, including the existing development runtime; a rename is not data migration.
- Do not replace the runtime while the game runs; prevent mixing files from two versions.
- To play without the mod, fully close the game and launch normally through Steam.
- Remove portable files only after both game and runtime have exited. Resetting personal choices is a separate, explicit action; ordinary removal must not modify game saves.
- Future custom technology requires separate update/removal validation. A disabled runtime does not itself handle an inventory item stored in a save or a data-table conflict. Current instructions for playing without the mod apply to the current version without that technology; its prototype is not being installed.

## Package acceptance tests

| Situation | Required result |
|---|---|
| Clean Windows account without Python in PATH | The package uses only its own runtime |
| Extraction elsewhere, spaces and accented characters in the path | Successful launch or a clear supported error without loading the wrong DLL |
| Different Steam library / drive | Automatic discovery or working folder selection |
| Dependencies without Internet access | No pip or download required; availability of Steam itself is assessed separately |
| Ordinary launch and native settings | No external development GUI; all intended settings remain usable through configured game controls |
| Wrong game EXE | No hook or attempt to use unverified addresses |
| Incomplete extraction or corrupt file | Clear error before mod startup |
| NMS or another Companion Auto Summon already running | No second attachment or game termination |
| Closing the launcher window during play | No unexpected NMS termination |
| Normal NMS exit | Clean termination of the companion process |
| New package version | Preferences preserved, game saves unchanged |
| Local save load in 0.4.3, followed by manual dismissal | One eligible deferred opportunity using saved preferences; no repeated summon after dismissal |
| Second computer with a matching game | Installation from a short guide without development tools |

First verify imports and check-only mode outside the game. Historical candidate 0.4.3 / 0.6.2 has one confirmed Random summon after station loading and a separate manual dismissal without reappearance during observation; later 0.8.7 and 0.9.0 evidence is recorded separately. Add missing startup and other scenarios against the exact candidate when an opportunity is available; immediate game closure is unnecessary. Running files stay unchanged during these checks. The first public package must repeat the applicable scenarios through its own launcher. Success of the current development launcher does not automatically transfer to new packaging.
