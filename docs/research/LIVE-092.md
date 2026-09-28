# 0.9.2 first packaged background-host startup

Recorded on 28 September 2026; times below are local Europe/Prague time.
This establishes one packaged background-host startup and native registration.
It does not establish visible companion behavior or the interactive launcher flow.

## Artifact and launch boundary

The owner closed the 090-r2 game normally before this trial. Its previous
terminal session 48413 ended with recorded exit code 15. No running trial files
were replaced. The separate 0.9.2-test artifact contains production
0.5.1-experimental, combined 0.9.2-play-trial and menu 0.9.1-diagnostics.
Its archive identity and offline checks are in
[TESTER-HANDOFF](../release/TESTER-HANDOFF.md).

The root executable passed `--verify-only` with exit code 0. The live start then
used packaged `runtime/pythonw.exe -I -B app/portable_launcher.py`, the child
command used by the graphical launcher. The interactive C# launcher was not
opened or clicked. This does not verify its Start game, Check installation or
Choose game folder buttons, visual layout or window closure.

## Observed sequence

| Local time | Observation |
|---|---|
| 15:33:51 | Packaged background process started as PID 58736. |
| 15:33:55 | Backup/session identifier: `2026-09-28_15-33-55_56d915c3`. |
| 15:34:07 | NMS started as PID 29456. |
| 15:34:12.150 | Session log reports injection complete. |
| 15:34:12.368 | Production 0.5.1 initialized with automation ON. |
| 15:34:12.593 | Menu native binding filter registered. |
| 15:34:12.721 | Framework reports two Mods and twelve hooks initialized. |
| 15:34:12.723 | Early-startup warning: `Cannot find window handle`. |

The warning is retained without assigning a cause or claiming visible GUI
failure or success. The session log is `pymhf-20260928T153411.log`; the personal
log remains outside Git and the release archive.

The built-in backup was stored under
`%LOCALAPPDATA%\NMS-AutoPet\backups\2026-09-28_15-33-55_56d915c3_before-0.9.2`.
Source/copy/source verification completed for 49 files. A later backup-target
check matched all 49 recorded hashes, with zero mismatches and no INCOMPLETE
marker. This verifies backup integrity, not restoration or later gameplay saves.

The working mod was staged under
`%LOCALAPPDATA%\NMS-AutoPet\sessions\2026-09-28_15-33-55_56d915c3\mod`.
This is a new private session, not a rewrite of the retained 090-r2 runtime.
Do not alter or remove this session while its host/game is running.

## Subsequent bounded owner report

After the startup, the owner reported that things appeared to work, but that no
financial-support notice had been seen. This is a general positive report, not
controlled acceptance of companion appearance, each menu control, specific HUD
values or restart persistence. Those checks remain separate below.

Absence of that notice is expected: no in-game financial message is implemented,
and no verified company payment destination has been selected. The proposed
combined activation/donation notice is recorded in
[MONETIZATION](../release/MONETIZATION.md); it is not current functionality.

A post-start executable `--verify-only` also returned 0. The 49 backup hashes
still matched with zero mismatches. This does not validate interactive launcher
clicks or a restore operation.

## Acceptance still required

- Visible owned companion after loading and after ship exit; initialization
  alone does not establish a native summon request or visible rendering.
- All seven settings, specific HUD confirmations, persistence after restart,
  manual dismissal and unchanged native placement/ownership limits.
- Interactive C# executable clicks/display, quiet visible startup, normal
  shutdown, another launch and launcher-window closure while the game continues.
- A second Windows/Steam PC and two-player visibility/independence checks.
- Menu lifetime across callback changes. The diagnostic menu retains the
  `unexpected_thread` refusal; registration does not demonstrate a repair.

Teleport arrival and base removal still create no automatic summon opportunity.
Pet absence alone must not override manual dismissal. No source behavior,
locale text or packaged bytes changed to record this startup.
