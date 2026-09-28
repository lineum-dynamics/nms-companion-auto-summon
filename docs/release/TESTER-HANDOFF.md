# 0.9.2-test private tester handoff

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
