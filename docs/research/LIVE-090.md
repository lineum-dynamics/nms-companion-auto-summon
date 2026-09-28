# Combined 0.9.0 live trial

## Scope

On 28 September 2026, the separate immutable `quick-menu-play-trial-090-r2`
bundle launched with production **0.5.0-experimental** and native menu
**0.9.0-selection**. The target is the supported Steam build **25442159**.
Times below are local Europe/Prague. The player confirmed the first visible
Random startup summon. Habitat selection and shuffle outcomes remain unverified.

## Launch preparation

- Windows PowerShell 5.1 read-only preflight confirmed the exact supported
  executable and existing Python 3.11 x64 / pyMHF 0.2.4 / Dear PyGui 2.3.1 runtime.
- NMS and its previous trial host were not running. No existing host was stopped.
- A fresh backup completed at 14:10:45 with 46 save-profile files and both
  external mod preference/state files. Source/copy/source SHA256 comparison
  matched, with the game closed before and after copying. Personal paths and
  hashes stay outside the repository.
- The guarded launcher started through a console-capable PTY. It retained
  the exact-build and duplicate-host guards. All 41 payload hashes match the
  retained bundle manifest; no running payload was edited.
- Existing schema-3 preferences selected Random, automation and all three
  supported locations ON, and exact-biome preference ON. They were not reset
  to the new-install defaults. The migration starts the new shuffle option OFF.

## Observed diagnostics

- **14:11:13.488:** production 0.5.0 initialized with automation ON.
- **14:11:13.682:** native menu initialized its binding filter.
- **14:11:13.828:** pyMHF reported two mods and twelve native targets loaded.
  An early framework warning could not find the window handle; the NMS window
  was subsequently present. No claim of full GUI validation follows.
- **14:12:09.178:** local save load armed one Random opportunity in native
  location 14 (Space Anomaly). Initial eligibility was false, so it waited.
- **14:12:09.401:** the icon resource phase reported registration.
- **14:12:11.888:** the native summon queue accepted displayed slot 6 from six
  eligible companions, 2.72 seconds after arming. The expected logical active
  index 5 appeared at 14:12:11.903 and remained the last observed value when
  the 15-second observation ended. This is not proof of visible rendering.
- **14:12:26–29:** diagnostics reported custom icon readiness, insertion before
  the first companion, English language observation and submenu transition.
  Visual ordering, icons and menu behavior remain player checks.
- **14:12:32.209:** a native-menu change reached the production preference
  handler and logged Random with shuffle ON; the other logged preferences
  remained ON. This verifies a diagnostic path, not full control acceptance.

## Remaining acceptance

### Later lifecycle observations

At **14:30:17**, the menu logged `Inert menu ordering stopped (unexpected_thread)`.
The native menu guard pins the first ordinary callback thread and stops custom
menu processing when a later callback uses another thread. The native binding
filter remains. Production automation is separate: **14:31:38** armed a ship-exit
opportunity and **14:31:40** recorded an accepted queue and logical active index.
These later diagnostics are not an independent visible-spawn confirmation.
The current log does not identify which menu callback changed thread or why.

The player subsequently reported no automatic companion after teleporting to a
base, and a companion disappearing when removing a base. Neither event is a
summon trigger in the current source. The log has no teleport/base-deletion
event evidence; it cannot establish the cause of disappearance. Production has
no base-deletion or pet-dismissal call. A new request must not be inferred merely
from pet absence because deliberate manual dismissal must remain effective.
The prepared 0.9.1 keeps the same menu code and does not fix this observed stop.

### Player checks

The player confirmed that the pet appeared after loading, and reported that
settings appear to be saved correctly. They had to change the preserved Random
mode to By habitat and enable shuffle, as expected for a legacy configuration.
This is not a completed restart-persistence test. Logs additionally record mode
changes to By habitat at 14:12:38.311, Last selected at 14:12:46.868 and Random
at 14:12:47.802; those timestamps do not establish the player's eventual choice.

The player also identified generic `settings updated` HUD confirmations and the
still-visible external development panel as unfinished presentation. A separate
follow-up candidate is being prepared with specific changed values and no GUI
window in the combined trial. The running 090-r2 is not modified.

Next checks are By habitat and Shuffle companions in the native menu, then a
ship exit on a known planet. Weighted habitat choices, no suitable
pool, shuffle history, save/restart behavior, controls, placement and multiplayer
must retain their separate evidence boundaries. The earlier 0.8.7 observations
do not validate this candidate, and native queue acceptance is never treated as
visible-spawn proof. The temporary pyMHF panel remains present in this retained
090-r2 session; its removal from a later launch requires a separate candidate.

No source, catalog wording, selection rules or gameplay limits changed for this
launch. No game save was edited by the mod or deployment tooling. In-game native
text remains English; the fourteen maintained catalogs remain draft preparation.
