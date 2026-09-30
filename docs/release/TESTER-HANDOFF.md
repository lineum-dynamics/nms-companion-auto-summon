# 0.10.0-native-test public alpha handoff

The native candidate is packaged, offline-validated and installed for the first
local test. Its first Steam session logged successful native activation and two
accepted summon queues. The player confirmed a visible pet after ship exit.
**Post-load appearance is uncertain:** the initial report of no pet was
immediately qualified with the possibility that it was overlooked. No startup
failure is established. Menu/UI acceptance, normal restart, second-PC use and
multiplayer remain unverified. The exact ZIP is publicly downloadable as Nexus
file **49202**, with a verified owner-account download matching its hash. The
public Nexus page and GitHub repository are available. Older files remain
archived with their own historical scan records.

| Field | Current native candidate |
| --- | --- |
| ZIP | `CompanionAutoSummon-0.10.0-native-test.zip` |
| Files / bytes | 30 / 3,725,420 |
| ZIP SHA-256 | `e00a8818230dba24066fcdc4d75a01d696c9e2573d2538aa6a9b05c5dd14bebb` |
| Module SHA-256 | `3840c8f8e0dd1405b05c35dcc859f766fd36fcb7c1bade3e07ab2e7ddc5d8373` |
| Build | `build/native-runtime-0100-r3` |
| Distribution | Native ASI module, exact official UAL 9.7.4 x64 loader, eight original icons; no Python or separate launcher |
| Game | Windows 10/11 x64, Steam Cosmos 7.04 / build 25442159; exact executable hash required |
| Offline validation | Policy 31,216 commands; selection 25,733 commands; storage 721 operations; runtime 59 cases; backup 16 checks; six owned-host module runs; ten authored hook/ABI checks |
| Installation evidence | Fresh verified closed-game backup; module/loader created; eight existing icons matched |
| First native session | Actual executable verified, private pre-activation snapshot verified, twelve hooks plus guard active, local load observed, two queues accepted |
| Player appearance report | Visible pet after ship exit confirmed; post-load appearance uncertain, not an established failure |
| Nexus native file | 49202, Main / Primary; mod-manager downloads OFF; public page shows Safe to use |
| Exact native ZIP scan | Linked VirusTotal 0/68, analysis 28 September 2026 at 16:15:13 UTC |
| Owner-account download | Manual download → Slow download succeeded; 3,725,420 bytes and SHA-256 matched the frozen ZIP |
| Remaining player acceptance | Controlled startup repeat, menu, restart, second PC and multiplayer still pending |

## Issues reported after the public alpha

On 30 September 2026 the owner reported that arriving by teleport does not
summon a companion and asked for teleport as an optional trigger. The released
candidate has no teleport-arrival hook. A later candidate should add a separate
Quick Menu toggle, apply the existing location switches and native summon
eligibility, and arm only after verified arrival readiness. Recommended fresh
install default: ON, consistent with the other automatic triggers; an upgrade
from an existing settings file should preserve prior choices and leave the new
trigger OFF until the player enables it.

The owner also reported that the settings page disappears when the game groups
a large companion list. Recent native logs contain `menu_unexpected_thread`,
which proves the menu safety guard stopped custom callbacks after a callback
thread change. Those logs do not identify whether grouped entries caused the
thread change. The adapter also assumes the original companion-page ordering.
Do not remove the safety guard based only on this correlation. A candidate must
record the failing callback phase and inspect the grouped-list shape, then keep
paired game callbacks on their owning thread and preserve refusal on overlap.

Neither finding changes the released ZIP. Teleport and reliable grouped-roster
menu support remain unimplemented until a separately versioned candidate is
validated.

The ZIP is retained in the originating task's deliverables; publish only the
filename and hash, never a developer-machine path. Packaging receipts retain
their pre-deployment false flags; the later controlled installation and live
log evidence are documented separately in
[NATIVE-0100-VALIDATION](../research/NATIVE-0100-VALIDATION.md).

The saved page version is 0.10.0-native-test, with the full native description
read back through Credits. The approved title/byline, updated alpha summary and
existing AI tags were retained. The mod was published on 28 September 2026 at
18:43 CEST. Native file 49202 is Main / Primary with mod-manager downloads OFF;
older files 49195, 49196 and 49197 remain archived. The page shows **Safe to
use** and offers a Manual download. Before publication, the file was listed as
Miscellaneous and its download template displayed an archived-version notice;
the owner still retrieved and hash-verified it. That historical notice does
not describe the current Main / Primary listing. This does not establish that
the second tester has received or installed the ZIP.

## Native tester procedure

1. The owner can download **file 49202** from the public Nexus page and
   pass the unchanged ZIP to the second tester. Verify the hash above and read
   its English or Czech README. Close the game and retain a separate
   closed-game save backup for the first installation. The verified download
   recorded here was performed by the owner, not on the second PC.
2. Open Steam's **Manage → Browse local files** for No Man's Sky. Extract the
   ZIP and merge its `Binaries` and `GAMEDATA` folders into this game root.
   Do not overwrite a different existing `Binaries/winmm.dll`; the guide gives
   the exact reusable loader hash. No administrator or Python setup is needed.
3. Start normally through Steam. Do not launch the older Python/pyMHF version
   concurrently. Unknown game builds refuse this mod's gameplay hooks and show
   an available localized startup warning.
4. Open the native **Quick Menu → Companions → Companion Auto Summon**. X is
   only the default PC Quick Menu key; use the game's configured binding or
   controller prompts. In-game mod text is English. Existing settings remain
   preserved; only fresh settings default to By habitat and Shuffle ON.
5. Repeat the uncertain load-appearance check and the confirmed ship-exit
   behavior under controlled observation, manually dismiss the companion and
   check that it remains dismissed, then confirm menu order/icons and OFF/ON
   behavior. Record actual observations separately from log queue acceptance.
6. After normal game closure, test Steam restart and saved settings. Once both
   PCs pass solo checks, use the same unchanged ZIP and exact supported game
   build for multiplayer, observing both screens. Do not exchange saves or
   private backups. No second-PC or multiplayer result is recorded yet.

Native initialization also verifies a private backup before enabling gameplay
hooks, but **the game is already running then**. This is not the earlier
closed-game backup or a pre-launch backup. Original save files are never edited
or restored by the mod. Preferences, favorites, backups and logs remain under
the established `%LOCALAPPDATA%/NMS-AutoPet` directory.

Uninstall with NMS closed by removing this mod's `.asi` and its icon directory.
Keep the loader if another mod needs it. Returning to the previous Python
test requires removing this native module first. Follow the packaged selective
removal instructions; never delete shared game or mod folders.

## Retained 0.9.3-test private tester handoff

Local packaging candidate built and offline-verified. **Nexus file 49197 is
uploaded and quarantined. Exact ZIP VirusTotal: 1/58 (Bkav Pro). No clearance
or successful owner download.** Keep mod 4579
Unpublished and preserve older files. At that checkpoint the existing 0.9.2
session was retained; this paragraph describes the older Python candidate,
not the current native installation.

| Field | Value |
| --- | --- |
| ZIP | `CompanionAutoSummon-0.9.3-test.zip` |
| Files / bytes | 1,897 / 23,534,865 |
| ZIP SHA256 | `d87f868c618aec200cf276aae1faf81748eeaf7be26bd1e21a8594590627e383` |
| EXE SHA256 | `0df7e0930c407ecdb64eba6c79ff7bae535606d9d71932e8342926e6b6120172` |
| Local build / runtime input | `build/portable-093-r1` / `build/portable-runtime-3119-r4/runtime` |
| Production / combined / menu | 0.5.1-experimental / 0.9.2-play-trial / 0.9.1-diagnostics; unchanged |
| Offline developer tests | 786 passed, zero failures/errors/skips |
| Host/native runtime + relocated package | Passed; no payload mutation, game start, attachment or backup creation |
| Live / second PC / multiplayer | NOT VERIFIED for 0.9.3 |
| Nexus file / scan / owner download | 49197 / quarantined, linked exact ZIP 1/58 / blocked |

Installation remains: extract the whole ZIP, double-click **Companion Auto
Summon.exe**, check installation, then start after normally closing the game.
Use the matching English/Czech quick start after the distribution is cleared.
The company identity/build recipe improve reviewability; they do not prove a
false positive. See [the exact repair and scan boundary](../research/PORTABLE-SCAN-093.md).

The 0.9.3 version, full description and file row were saved and read back on
28 September 2026. The file is Miscellaneous with mod-manager downloads OFF;
49196 and 49195 remain present. The linked scan hash matches the exact local ZIP. Nexus now reports automated
quarantine; the ordinary owner-download route is blocked. The completed EXE
report now shows 3/71: Bkav Pro, McAfee Scanner and SecureAge. Bkav's label is
the same as the archive's; no false-positive or sole-cause claim is made.
The prepared [review request](NEXUS-QUARANTINE-REVIEW-DRAFT.md) remains unsent.

The frozen ZIP's `Multiplayer test.txt` retains the scenario plan's 0.9.2
heading. Its steps also apply to the unchanged 0.9.3 gameplay; use the 0.9.3
README and artifact identity above. Do not relabel or rewrite the uploaded ZIP.

## Retained historical evidence

The following records belong only to 0.9.2, not the new candidate.

## Retained 0.9.2-test private tester handoff

This is the local readiness record, not public download-page text. The ZIP is
built, offline-checked and uploaded as file 49196; automated Nexus quarantine
blocks owner downloading. Player acceptance remains separate. Keep mod 4579 **Unpublished**.

## Artifact identity

| Field | Recorded value |
|---|---|
| Player version | 0.9.2-test |
| Production / combined / menu | 0.5.1-experimental / 0.9.2-play-trial / 0.9.1-diagnostics |
| ZIP filename | CompanionAutoSummon-0.9.2-test.zip |
| ZIP bytes | 23,419,195 |
| ZIP SHA-256 | `1507a92c86b4126e0bfb9131ec2df228fbac2d95d3e88529db0499bd3f3349fe` |
| Packaged files | 1,245 |
| Local built directory | `build/portable-092-r1` |
| Local deliverable copy | `outputs/CompanionAutoSummon-0.9.2-test.zip` in the originating Codex task output directory; do not publish a developer-machine path |
| Runtime input | `runtime3119r3`; bundled Python 3.11.9 x64 and pinned dependencies |
| Exact game target | Windows Steam Cosmos 7.04 / build 25442159; exact executable check retained |

The final built directory passed native dependency imports and executable
`--verify-only`; those checks left the artifact unchanged and did not start the
game. Actual-framework checks of combined 092-r1 passed without native hooks,
with no GUI and mocked dispatch. These checks do not prove injected execution,
quiet live startup or multiplayer behavior.

The final developer suite passed **770 tests** in 126.079 seconds. Relocated
verification used a path containing `Káťa猫`, poisoned `PYTHONHOME`/`PYTHONPATH`
and a System32-only `PATH`. Both the full executable verification and actual
package Python check-only passed; all 1,245 packaged files remained unchanged.
No NMS start/attach or backup mutation occurred. The local diagnostic report is
`work/portable-092-relocated-check.json` in the originating workspace; it is
not a public package file. These checks do not replace a second player's test.

## First background-host startup

After normal closure of 090-r2, executable verify-only returned 0 and the
packaged Python child started. Its built-in backup verified 49 files; injection,
production initialization with automation ON and two Mods/twelve hooks were
logged at 15:34:12. The interactive C# launcher was not opened or clicked.
Visible pets, normal exit/restart, launcher-window closure and multiplayer remain
unverified. Full scope and the early window-handle warning are in
[LIVE-092](../research/LIVE-092.md).

The owner subsequently reported that things appeared to work, without
controlled per-feature acceptance, and noticed no donation message. Such a
message is not implemented; no verified company payment destination is selected
(see [MONETIZATION](MONETIZATION.md)). Post-start executable verify-only returned
0 and all 49 backup hashes still matched. This does not add launcher-click,
restart or restore acceptance.

## Evidence to finish

| Field | Status to update only from completed evidence |
|---|---|
| Final production test count | 403 passed for unchanged production 0.5.1; this is production-source evidence, not portable live acceptance |
| Final developer test count | 770 passed in the final frozen rerun (126.079 seconds) |
| Final combined reports / source match | Final native imports, executable verify-only and combined actual-framework smoke passed; relocated executable plus actual-package check-only passed |
| New Nexus file ID and exact uploaded ZIP readback | 49196; file/version/size and linked scan SHA match this exact ZIP; original 49195 retained |
| Saved version / summary / description readback | 0.9.2-test, full title/byline, unchanged summary and new portable instructions saved and read back; page remains Unpublished |
| 0.9.2 scan status for this exact hash | Nexus automated quarantine; exact ZIP VirusTotal 3/60, exact compiled launcher 8/70. Cause and false-positive status unresolved; see PORTABLE-SCAN-092 |
| Owner download hash verification | BLOCKED by Nexus quarantine; no owner-download hash check or successful download claimed |
| Unchanged ZIP passed to second tester | Not performed; second-PC handoff remains pending |
| Packaged background-host first startup | Injection, production 0.5.1 and two Mods/twelve hooks registered after a verified 49-file backup; see LIVE-092 |
| Interactive executable clicks / visible pets / normal exit / restart / launcher-close behavior | **NOT VERIFIED** |
| Second Windows/Steam PC and multiplayer | **NOT VERIFIED** |

If any packaged byte changes, create and record a new artifact identity and
repeat the affected checks. Do not reuse these values for a rebuilt ZIP.

## Owner and tester flow

1. File 49196 is uploaded and read back under Unpublished. Resolve its
   automated quarantine before treating the Nexus download route as usable.
   No support contact is authorized; do not send requests or evade the scan.
2. The owner downloads that file, verifies the SHA-256 above and passes the
   unchanged ZIP to Katya. Both PCs use the same archive and exact supported game.
3. Extract into a new folder and double-click **Companion Auto Summon.exe**.
   Follow packaged **README.txt** or **README.cs.txt**; no Python/pip setup.
4. Use **Check installation** and **Choose game folder** if needed. Windows
   10/11 x64, .NET Framework 4 and Microsoft Visual C++ v14 x64 are required.
   A missing VC runtime has a localized explanation; use the official one-time
   installation link in the README. No automatic prerequisite download occurs.
5. Open Steam and sign in before **Start game**. Installation checking itself
   does not require Steam running. Normal start requires a private verified
   backup and refuses a running game or competing launch.
6. Finish each player's solo checks, then use **Multiplayer test.txt**. Record
   actual appearance separately on each screen. Never exchange saves or backups.

Backups live under `%LOCALAPPDATA%\NMS-AutoPet\backups\`; launcher/host logs use
the adjacent `logs` folder, and private staged mod copies use `sessions`.
Settings and remembered companions remain at their existing external paths.
The extracted distribution remains unchanged by normal runtime work. Do not
delete an active session or end its host. Keep the GUI open during the first
test; detached window closure is designed behavior, not yet live acceptance.
To play without the mod, quit NMS normally and start through Steam.

## Known limits and historical scan result

Menu 0.9.1-diagnostics adds bounded phase/thread/transaction records, retaining
the unsafe-callback refusal. It does not fix the observed `unexpected_thread`
stop in 090-r2. Production summoning remains separate. Teleport arrival and
base removal do not create automatic opportunities; absence alone never
overrides manual dismissal. All selection rules and gameplay limits remain.

Historical Nexus file **49195** is the **0.9.1** development ZIP, not this
portable archive. Its SHA-256 is
`7025712f8f9eb89a238f37e3871e817aefee99da9bf177d2163507d23b1a1b43`.
Nexus displayed **Some suspicious files**, while the linked VirusTotal report
showed **0/65** for that hash. The cause remains unresolved. Neither status
establishes safety, a false-positive cause, approval or a scan result for 0.9.2.
