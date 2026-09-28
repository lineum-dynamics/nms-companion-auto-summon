# Combined 0.8.7 live evidence

Recorded 28 September 2026. Times use Europe/Prague (UTC+02:00).
This records one session on the exact supported Steam build, not general
compatibility or proof that the earlier intermittent failure is fixed.
Personal logs, saves and private launch records remain outside Git.

## Launch and preserved inputs

- Final `quick-menu-play-trial-087-r1`: combined **0.8.7-play-trial**, production
  **0.4.9-experimental**, menu **0.8.5-branding**, pyMHF **0.2.4**.
- After normal game closure, a fresh **46-file** save-profile backup passed
  source-stability and full hash readback checks, then a prelaunch recheck.
- All **40 payloads** matched their manifest. Windows PowerShell 5.1 read-only
  preflight passed against the installed game and existing runtime.
- The guarded PowerShell launcher ran through a persistent PTY. At 11:07:26,
  both Mods and twelve hook targets registered, with automation ON. This is
  development-host evidence, not a portable-installer acceptance result.
- Initial post-start hashes matched all payloads and both external player
  preference/state files. Random, all three supported locations and the
  exact-biome preference were enabled. Earlier artifacts were not overwritten.

## Visible automatic summons in the Space Anomaly

The player confirmed visible appearance after both loading and leaving the
ship. Both requests below report native location 14 (Nexus).

| Event | Save load | Ship exit |
|---|---|---|
| Opportunity armed | 11:08:36.931 | 11:09:01.348 |
| Random draw | Displayed slot 5 from six eligible owned pets | Displayed slot 6 from six eligible owned pets |
| Native queue accepted | 11:08:39.575 | 11:09:02.922 |
| Expected logical active index observed | 11:08:39.592, index 4 | 11:09:02.938, index 5 |
| Passive observer end | Native preview/emote cancellation at 13.89 s; last active index 4 | Time limit at 15.02 s; last active index 5 |
| Visible appearance | Confirmed by player | Confirmed by player |

The observer did not issue a retry. Its logical active records are separate
from the player's visual confirmation. The two opportunities chose different
pets; they are not a controlled same-companion comparison. The earlier visible
startup failure in [0.8.4](LIVE-084.md) remains unexplained, and this session
does not establish repeatability or a behavioral fix.

## Menu and language observations

The native icon-resource phase reported registration at 11:08:37.122 and
`custom_ready` at 11:08:51.395. The CAS entry reported insertion before the first
companion. These are resource/construction observations, not visual acceptance.
At 11:08:53.254 the bounded language observer reported native region 0,
`ENGLISH`, with prior initialization/load seen. Text remained unchanged; the
observation does not prove reload safety, translated rendering or font coverage.

## Remaining checks

After a requested manual dismissal check without a new ship entry or setting
change, the player reported that the pet appeared to remain dismissed. The
requested wait was at least 20 seconds; its actual duration was not independently
measured. This supports one bounded dismissal observation, not a broad regression
or an independently observed native dismissal event.

The player then confirmed the requested native automation-toggle sequence:
OFF followed by ship entry/exit did not summon; ON alone did not summon; a
subsequent ship entry/exit did. Logs show OFF applied at 11:13:04.257 and ON at
11:13:39.076, with no automatic request between. The next ship exit armed at
11:13:56.061 and accepted displayed slot 4 at 11:13:57.638; active index 3 was
observed at 11:13:57.654 and remained the last recorded index at the 15.02-second
observer limit. The other logged preferences stayed unchanged, and automation
was left ON. This verifies the automation toggle in this session, not every
setting, restart persistence, held/remapped input or controllers.

Broader manual dismissal, the other five controls and restart persistence,
HUD/parent-icon appearance, held/remapped inputs, controllers, obstructed terrain,
other locations, Last selected startup, save changes and multiplayer still need
bounded acceptance. No new selection mode, shuffle, charging or translation
behavior was introduced. Locale impact of this record: no player-facing text or
meaning changes; the fourteen catalogs remain unchanged.
