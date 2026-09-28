# Combined 0.8.4 live evidence

Recorded 28 September 2026. Times below use Europe/Prague (UTC+02:00).
This is a bounded observation record, not a general compatibility claim.
Personal logs, saves and raw executable analysis are retained privately.

## Artifact and launch

- Combined **0.8.4-play-trial**, production **0.4.7-experimental**, menu
  **0.8.3-settings-trial**, on the exact Steam build pinned in the manifest.
- Fresh backup: 43 files, hashes verified before launch. All 39 bundle payloads
  matched their prelaunch hashes during the subsequent read-only check.
- The first hidden PowerShell attempt ended before a new game, host or log was
  observed. Its cause was not captured. A subsequent persistent PTY launch
  through the guarded PowerShell host succeeded; this does not verify a portable
  one-click launcher.
- At 08:15:41, both Mods and twelve native targets registered with automation ON.
  Random, all three supported locations and matching-biome preference were enabled.
  The native icon resource phase was observed at 08:16:23 and custom readiness
  at 08:17:36.
- Player preference changes were logged later. At the bounded file check,
  settings and manual-companion state again matched their prelaunch hashes.
  This is a hash comparison at that time, not a claim that settings never changed.

## Nexus startup: visible failure

| Event | Time / observation |
|---|---|
| Local save-load opportunity armed | 08:16:23.761, location 14 |
| Random choice | Displayed slot 1 of six native-eligible owned companions |
| Native queue accepted | 08:16:26.981, 3.22 seconds after arming |
| Expected native active index first observed | 08:16:29.816, 2.83 seconds after acceptance |
| Existing observer | Ended at that first matching active index |
| Player report | No visible companion |
| Later external snapshot | 08:21:35, same location; active -1, pending -1; two identical reads |

The native active index is not rendering confirmation. The gap between the
initial active observation and later inactive snapshot leaves removal time and
cause unknown. Menu preferences were changed within that gap. Do not attribute
removal to any one action, a timeout or a particular placement defect.

## Same-session ship exit: visible success

The player entered and left the ship in the Anomaly without opening companion
preview, then reported a visible pet. The ship-exit opportunity armed at
08:31:59.811. Random chose displayed slot 5 from the same count of six eligible
companions, queued at 08:32:01.437 and reached its matching active index on the
first observer update at 08:32:01.477 (logged 0.03 seconds).

An independent query/read-only sampler observed active slot 4 (zero-based),
pending -1 and location 14 at 08:32:01.486. Its discrete logical-state reads
support the log; visual confirmation comes from the player. The script neither
injects nor writes memory and is separate from the installed runtime.

This proves one successful ship exit in the unchanged session. Startup and
ship exit selected **different companions**, so timing, location within the
Anomaly and companion-specific differences remain confounders. It does not
prove a startup-only defect or repair the failed startup result.

## Menu evidence

The supplied screenshots show six distinct role icons and selected captions
`Space stations: ON` and `Space Anomaly: ON`. Logs show applied changes to
automation, selection, matching-biome, station and Anomaly controls. The planet
control, complete navigation/rebuild behavior, held input, remapping,
controllers, shortcuts and HUD icon appearance do not gain full acceptance
from these screenshots. They also do not verify translations beyond English.

Icons represent setting roles and remain stable as values change. Native
white/gray presentation marks selection; captions carry ON/OFF or mode values.
English generic labels use sentence case; proper names retain capitalization.

## Follow-up source candidate

Production **0.4.8** in prepared combined **0.8.5** retains passive observation
after the first matching active index, within the original 15-second,
4096-callback and eight-transition-log caps. It records later active/pending
changes and whether logical activity was ever observed. Existing cancellation
boundaries remain, including manual actions and context changes.

This adds no native hook, call, offset, retry, policy trigger, placement override,
save write or player-facing string. It is not installed into the running 0.8.4
bundle and is not a spawn fix. A future failure needs the longer lifecycle
record before selecting a behavioral change. Any comparison of load and ship
exit should control the companion choice and record actual visible appearance.
