# Changelog

## Unreleased follow-up — 1 October 2026

- Record the exact Cosmos 7.05 static XREF pass for teleport-related state:
  four byte-pattern candidate references each for
  `AngleFromBaseComputerWhenTeleporting` and
  `DistanceFromBaseComputerWhenTeleporting`, one for `Teleporting`, and one
  for the `gcpersonalteleporter.cpp` marker. The raw scan offsets were
  ModRM-byte positions, not instruction starts; a `.pdata`-bounded decode now
  records the valid instruction addresses and function ranges. None identifies
  a completion callback; see
  [NMS-075-STATIC-XREFS](docs/research/NMS-075-STATIC-XREFS.md).
- Contextual decoding rejects both remaining teleport-string leads as event
  hooks: `Teleporting` is a data-field label beside `Remote`, `IsActive`,
  `Timestamp` and movement/position fields; `gcpersonalteleporter.cpp` is
  passed as a diagnostic source location with line value `0x4A4`. Teleport
  completion remains unmapped.
- Decode the three teleport interaction labels at valid instruction RVAs
  `0x1002269`, `0x100227A` and `0x100228B`; they feed a shared action-object
  path and cleanup, not an observed successful-arrival result. Also map case 4
  of the `cGcApplicationDeathState` update table: it calls the shared position
  helper, confirming that helper use occurs during death-state processing but
  not proving completed respawn. Neither candidate is enabled as a trigger.
- Keep automatic summoning after death/respawn as a separate unimplemented
  trigger from save loading and teleport arrival. The 7.05 static scan found a
  shared positioning helper with three direct return sites inside a function
  carrying a `DoPlayerRespawn` diagnostic label; other callers include warp
  paths, so this is only a candidate lead.
- Add a compile-time-only observer filtered to those three return sites. It
  records bounded scalar call data and does not change summon behavior. Offline
  validation and any live observation are tracked separately; no death fix or
  player release is claimed.
- Offline validation passed and a diagnostic module was staged locally after a
  fresh verified save/preferences and previous-module backup. One live session
  captured two candidate calls during successful save loading, without a
  reported death; this is not a death trigger. A follow-up observer build
  corrects the diagnostic hook-count message. The public Nexus file remains
  unchanged.
- Record a live freighter-to-space-station teleporter control: the owner saw a
  pet appear after arrival, and the observer recorded return `0x3302C4` with
  reason `11` (`0x0B`) and flag `1`, followed 1.36 seconds later by an accepted
  summon queue. The log shows the automatic opportunity had already been armed
  at `16:30:17Z`, about fourteen minutes before the teleport, with no new
  opportunity armed at arrival. The runtime arms only after a successful local
  load or ship exit; this sequence is consistent with a prior pending
  ship-exit opportunity becoming eligible at the station, not a teleport
  trigger. The exact earlier event was not separately witnessed. This also
  confirms the candidate positioning call site runs during a teleporter path,
  so it is not death-specific. Teleport/death triggers remain unimplemented.
- A follow-up negative control opened and closed the teleporter interface
  without choosing a destination. The active log did not change and no
  candidate return was recorded. The call site is not triggered by merely
  opening/backing out of the interface; destination confirmation or the travel
  transition remains to be isolated.
- Record a second live teleport sample after the owner moved to a freighter:
  the passive observer captured two returns from the shared positioning
  helper (`0x3302C4` and `0x33066F`, both with `reason=11`), but no new
  opportunity was armed at that point. A later candidate call (`reason=9`)
  and a later ordinary queued request have no verified causal link to the
  teleport; no destination or visible pet appearance was captured. The helper
  remains unsuitable as a teleport or death trigger.
- A later test-only candidate build was live-checked on one reported
  freighter-to-station trip. At return `0x3302C4` with `reason=11`, `flag=1`,
  it armed a fresh opportunity; the native queue accepted it 1.66 seconds
  later, and the owner confirmed that the pet appeared. The candidate handler
  clears a still-deferred save-load request and does not replace an already
  pending policy request, so this request is attributable to the test hook in
  this run. The shared helper's teleport-completion and multiplayer semantics
  remain unverified; the public build is unchanged. See
  [teleport research](docs/research/TELEPORT-AND-GROUPED-MENU.md).
- A second live control from a station to a planetary base, without entering or
  exiting a ship, separately armed and accepted a request after the session's
  save-load queue had already completed. The owner confirmed the pet appeared.
  This reproduces the test hook on another local route, without establishing
  the shared helper's completion or multiplayer semantics.
- After a Windows `AppHangB1` report, the exact executable still matched the
  mapped Cosmos 7.05 hash. The restarted test session logged a successful save
  load, an armed opportunity and an accepted queue; the owner reports that the
  pet appeared only after leaving a planetary cave for the surface. This is
  consistent with the existing placement-wait behavior, not a new respawn
  trigger. Queue acceptance does not prove visible placement; the owner report
  supplies that confirmation. The Windows event identifies an application
  hang, not a faulting-module crash, and does not establish a mod cause.
- Extend the exact-build `.pdata`-bounded search across all `respawn` strings:
  60 printable matches, 52,096,118 decoded runtime-function bytes and no
  skipped ranges. `RPCReceivedPlayerRespawned` appears in network-RPC type names
  without a direct code reference; `RespawnPlayer` likewise had no direct
  RIP-relative reference. Neither result identifies a completed local respawn
  event. The owner also reports that manual companion summoning is currently
  unavailable on the freighter; this remains a bounded observation, not a
  broader freighter compatibility claim. No runtime or public release changed.
- A focused follow-up found `cGcPlayerRespawn::SpawnAndPositionShip` only in a
  compiler-generated lambda type name, without a direct code reference; it did
  not map `RespawnReason` or the logged numeric values. Keep that as a static
  respawn-path candidate, not a completion trigger.
- Map the argument flow through reason-code producer `0x331F60`: its one direct
  `.pdata` caller is inside the `DoPlayerRespawn`-labelled function, which stores
  the return value at object offset `+0x620` and forwards it to the shared
  position helper. This is dataflow evidence only; reason names and successful
  completion semantics remain unknown.
- Broaden the exact-build teleport scan to 197 printable string matches.
  Teleport animation/warp event labels and `TeleportToPlayer` had no direct
  RIP-relative code references; mission/notification sequence references did
  not reveal a verified local arrival callback. The teleport trigger remains
  unmapped and disabled.
- Record the latest live freighter-to-station sample: `0x3302C4` returned with
  `reason=11` and `flag=1` after the owner's reported arrival, but no fresh
  opportunity or queue followed and no pet appeared. A prior queue was accepted
  about ten minutes earlier. This is the strongest arrival candidate so far,
  not a verified completion trigger; the runtime and public release remain
  unchanged.
- Decode the helper's internal player/ship positioning raycasts and confirm
  that its return occurs after that helper, not necessarily after the whole
  teleport. The reason producer can return `11` under more than one state
  condition, so that value is only a test filter, not a semantic event name.
- Prepare a compile-time-only local trial for return `0x3302C4`, `reason=11`,
  `flag=1`. It uses the existing automation preference, local application
  checks, active/queued guards, supported-location wait and native placement
  eligibility. The exact-build module passed all offline bundle validators,
  including 63 runtime cases. It has not been installed or tested live; no
  production or Nexus release changed. See
  [teleport research](docs/research/TELEPORT-AND-GROUPED-MENU.md).

## Unreleased follow-up — 30 September 2026

- Record the report that after death the pet was absent and the custom settings
  page was missing. The published build has no death/respawn opportunity, and
  the recorded `menu_unexpected_thread` stop does not prove that death caused
  the UI-thread change.
- Keep teleport-arrival and death/respawn triggers as separate unimplemented
  behaviors until each has a verified local completion event.
- Test a recoverable menu-thread handoff: skip a one-off callback from an
  unexpected thread and rebind only at a quiescent builder start. Preserve the
  fail-closed guard during in-flight menu/trigger transactions. All 25 offline
  menu scenarios pass; no live test or public package is claimed.
- Add a canonical Known Issues page and require matching current summaries in
  the repository README and Nexus description.

## 0.10.1-native-test — 30 September 2026

- Map the native runtime to the exact Steam Cosmos 7.05 executable using a
  separate native profile; retain the legacy Python profile for Cosmos 7.04.
- Update native gameplay hooks, companion/placement fields, notifications,
  quick-menu actions, binding filter and texture-resource lookups.
- Record the static address evidence and reusable game-update mapping process.
- Pass 403 core regression tests, 790 tooling tests, and the complete native
  policy, selector, storage, runtime, backup and owned-host validation suite;
  read back the exact 30-file release archive. The owner confirmed a visible
  pet and mod-menu entry beside grouped companions in a limited Cosmos 7.05 smoke test;
  full-menu, long-session, location-matrix, teleport and multiplayer behavior
  remain unverified. Nexus file **49367** is Main / Primary; the public page says
  Safe to use and its linked VirusTotal SHA-256 matches the local archive. Edge
  blocked the owner's manual download, so downloaded bytes were not read back.
- Plan teleport arrival as a separate follow-up trigger. Use the game's native
  manual eligibility and placement checks; never force a summon where manual
  summoning is unavailable. Preserve explicit settings and localize any new
  setting/feedback across all fourteen game-language catalogs.
- Follow-up report: one direct load into the Space Anomaly had no visible pet.
  An Anomaly mission was incomplete beforehand, but no causal link is known;
  repeat under controlled conditions before treating it as a confirmed defect.
- Keep this labelled an early test build. The bounded smoke report does not
  establish broad 7.05 compatibility; see the [tester handoff](docs/release/TESTER-HANDOFF.md)
  and [compatibility evidence](docs/research/NATIVE-0705-COMPATIBILITY.md).

## 0.10.0-native-test — 28 September 2026

- Implement native automation, exact policy/selector parity, settings/favorite
  migrations, native quick-menu controls and icons without a Python runtime.
- Add guarded direct-Steam initialization, per-target executable checks and
  process-lifetime hooks with partial-activation gating and bounded rollback.
- Create verified private snapshots before hooks; explicitly distinguish these
  running-process snapshots from the retained closed-game launcher backups.
- Retain Last selected, Random, By habitat, weighted groups, rotation, manual
  dismissal, placement retries and native gameplay eligibility.
- Keep optional notification failures from disabling working automation;
  revalidate intent/context around native calls and concurrent callbacks.
- Add a maintained activation-failure warning across all fourteen catalogs.
  In-game language selection remains unimplemented; English menu/HUD retained.
- Package only native payload, original icons, player instructions and required
  notices. No Python, EXE launcher, fixtures, user data or nested archives.
- Offline checks are recorded separately from native live gameplay, multiplayer
  and Nexus scanner acceptance; this is an unpublished test candidate.

## Native feasibility milestone 1 — 28 September 2026

- Add an inert Windows x64 probe with the documented InitializeASI export,
  current-process executable SHA-256 inspection and no native game calls/hooks.
- Port the pure summon-opportunity policy into C++ and compare 31,216 actions
  and states with the existing Python oracle across 88 traces/four configurations.
- Verify six owned-host load/inspect/unload runs, eight concurrent initializers
  per run, invalid ABI handling and Unicode relocation. No game launched.
- Record loader provenance and current static import evidence, the complete
  existing integration port map, and unresolved pre-launch backup/lifecycle gates.
- Keep the installed mod, exact 0.9.3 Nexus artifact and all fourteen catalogs
  unchanged. This developer experiment is not a new player release.

## 0.9.3 scan follow-up and independent distribution research

- Record the completed exact launcher report: 3/71 (Bkav Pro, McAfee Scanner,
  SecureAge). Bkav's label matches the ZIP; no sole-cause or false-positive
  conclusion is established. Keep the original 0.9.3 artifact unchanged.
- Record public Nexus staff statements, a comparable NMS native migration,
  verified vendor-file provenance and a bounded native-loader feasibility plan.
  No native implementation, release clearance, external contact or new scan.
- No gameplay, runtime or player-facing wording changes; all fourteen language
  catalogs remain unchanged. See `docs/research/NEXUS-SELF-SERVICE-INVESTIGATION.md`.

## 0.9.3-test archive-layout and launcher provenance repair

- Extract the original 649 Python standard-library files unchanged and record their inner-archive provenance. Refuse nested distribution archives before packaging; retain vendor native files and licenses.
- Add correct Windows product/company/version identity with the same non-elevated behavior. Ship actual build inputs and an offline compilation recipe. This is not a claim of antivirus clearance.
- Skip inaccessible unrelated processes while identifying Steam; preserve selected-parent/target failures, ambiguity refusal and actual-process guards. Label new backups with the actual portable version.
- Pass 786 developer tests, all locale/profile checks, host/native runtime initialization, final ZIP verification and Unicode relocation with unchanged payloads. Keep production and native menu files unchanged; no 0.9.3 game start, attachment or save modification.
- Preserve quarantined Nexus file 49196 and its exact 3/60 ZIP and 8/70 EXE evidence. The 0.9.2 EXE matches a faithful rebuild except timestamp/MVID. New file 49197 is also quarantined under Unpublished; its linked exact ZIP reports 1/58 (Bkav Pro). No owner download or clearance. An unsent moderator-review draft is prepared; external contact remains unauthorized. See `docs/research/PORTABLE-SCAN-093.md`.

## 0.9.2-test first packaged background-host startup — 28 September 2026

- Start the packaged Python child after owner-confirmed normal game closure and executable verify-only success. Built-in source/copy/source backup verified 49 files; a later target check matched all 49 hashes without an incomplete marker. Stage into a new private session, retaining prior trial files.
- Observe injection completion, production 0.5.1 with automation ON, the binding filter and two Mods/twelve hooks initialized at 15:34:12. Retain the early `Cannot find window handle` warning without assigning a cause. See `docs/research/LIVE-092.md`.
- The interactive C# launcher was not opened or clicked. Visible pets, settings/HUD acceptance, normal exit/restart, launcher-window closure, second-PC use and multiplayer remain unverified. Registration does not establish a fix for the menu thread stop.

## 0.9.2-test portable candidate — preparation checkpoint

- Prepare a root graphical executable with bundled Python 3.11.9 and pinned dependencies, installation checking and game-folder selection. Portable testers do not install Python or run pip. Retain Windows .NET Framework 4 and Microsoft Visual C++ v14 x64 as checked prerequisites; no automatic prerequisite download.
- Require private, source/copy/source-verified backups before normal starts, preserve existing external preferences and stage verified mod files into private sessions. Keep runtime writes out of the extracted distribution. Detached launcher/host lifetime is prepared but not yet live-verified.
- Retain production 0.5.1 and all selection/gameplay rules. Use combined 0.9.2-play-trial and menu 0.9.1-diagnostics; log bounded callback/thread/transaction evidence without accepting arbitrary new threads or fixing the known menu stop.
- Add portable English/Czech quick starts, a private tester handoff and two-player acceptance plan. The owner will download the exact validated unpublished Nexus ZIP and pass it unchanged to the other tester. No portable live or multiplayer success is claimed.
- Build the 1,245-file portable archive; final developer validation passed 770 tests. Final native imports, executable verify-only, actual-framework checks and relocated executable/package checking passed without game start or attach. The relocated path included non-ASCII characters and isolated/poisoned Python environment variables; all packaged files remained unchanged and no backups were mutated. Artifact hash and byte count are recorded in `docs/release/TESTER-HANDOFF.md`. New Nexus upload ID/readback and scan remain PENDING; do not reuse the historical 0.9.1 file ID or Nexus/VirusTotal discrepancy as 0.9.2 evidence.

## 0.5.1 / 0.9.1 developer candidate — exact settings confirmations

- Replace generic settings-updated notices with every effective changed label and its new ON/OFF or mode value. Batch multiple changes in canonical menu order, keep one session-only suffix on save failure, and emit nothing for a no-op. Preserve preference application, storage, summon cancellation and existing latest-notice delivery semantics.
- Replace two obsolete HUD catalog formats with `hud.settings_applied` and `hud.setting_separator` across all fourteen catalogs, retaining 46 keys. Reuse existing translated labels and values; maintain draft status. Offline rendering preserves complete changes and whole-message English fallback; native runtime remains English ASCII with a 511-byte bound.
- Set `gui.shown = false` only for the combined trial, retaining the seven-control 0.9.0-selection native menu. Standalone developer launches retain the GUI because they lack that menu. This does not complete portable distribution, console-free startup, native localization or live control acceptance.
- Validation passed 403 production and 689 developer tests, actual-framework checks and both read-only preflights. The allowlisted combined ZIP has 42 verified files. The separate 0.9.1 candidate has not launched. Preserve the running 090-r2 payload and player settings. Its confirmed Random startup pet and report of apparently saved settings do not prove restart persistence, By habitat or shuffle outcomes.
- Record the retained 090-r2 `unexpected_thread` menu-stop guard at 14:30:17. The 0.9.1 menu is unchanged and does not fix it; production automation is separate. Teleport arrival/base removal create no new summon opportunity, and the cause of a reported disappearance remains unproven. Menu-lifecycle investigation is next.
- Refresh English/Czech guides and selection evidence for all seven controls and exact feedback. Save and verify the 0.9.1 description, summary, version and development ZIP on the unpublished Nexus draft (mod 4579, file 49195, Miscellaneous; mod-manager download disabled). Preserve the explicit menu-thread and travel-trigger limitations. Native hooks, gameplay rules, weights, limits and game saves are unchanged.
- Record a scan-status discrepancy: Nexus displays Some suspicious files; its linked VirusTotal report for the exact uploaded ZIP shows 0/65 detections. The cause is unresolved and the page remains unpublished.

## 0.9.0-r2 first live launch — 28 September 2026

- Start the unchanged separate 090-r2 bundle after a matching read-only preflight and a fresh verified backup of 46 save-profile files and both external mod data files. Preserve existing Random preferences; do not force new-install defaults.
- Confirm production 0.5.0, menu 0.9.0-selection and twelve native targets loaded. Diagnostics record an accepted Random startup queue in the Space Anomaly and a matching logical active index; the player confirms visible appearance. Native menu actions log shuffle ON and mode changes; the player reports settings appearing to save, without a restart-persistence check.
- Record the bounded observations in `docs/research/LIVE-090.md`. New selection behavior, seven-row UI, placement, inputs and multiplayer still need live acceptance. No source, translation wording, gameplay rules or running trial payload changed.

## Habitat fauna evidence — 28 September 2026

- Establish Waterworld adoption from a firsthand Water-bound helmet-crab report; distinguish aquatic creatures on other planet types, underwater adoption and native summon placement. Do not promise underwater or Exo-Skiff summoning.
- Record the limits of Gas Giant evidence: a no-fauna discovery example, fishing catches and separate moons do not establish an adoptable native pool. Explain the existing exact-only candidate behavior without presenting category recognition as adoption support.
- Update the research record and unpublished Nexus wording. No runtime, selection table, preferences, in-game wording or translation meaning changes; existing trial bundles remain immutable. This documentation check is not new live acceptance.

## 0.9.0-r2 terminology revision — Shuffle companions

- Rename the visible Rotate companions control to Shuffle companions in the native menu, temporary panel, all fourteen catalogs, current documentation, icon preview and unpublished Nexus rules. Keep Random as a separate selection mode. Preserve internal preference/catalog keys, asset paths, defaults and gameplay behavior.
- Retain immutable 090-r1 and prepare the separate 090-r2 bundle. All 396 production and 683 developer tests pass, as do actual-framework standalone/combined checks and Python/Windows PowerShell 5.1 read-only preflights. All seven temporary preferences work; no native hooks, game start or deployment occurred. The exact supported game is installed and NMS was closed during preflight.
- The original eight DDS payloads remain byte-identical; only the preview caption and SVG title changed. Translations remain unreviewed drafts and native rendering remains English. The next live trial must use 090-r2. Existing player preferences have not been changed; fresh defaults remain By habitat and shuffle ON, while older configurations retain their mode and shuffle OFF.
- Clarify the official Worlds Part II basis for Waterworld and Gas Giant categories. Existing exact-match-only rules remain unchanged; no live adoption or summoning support is inferred from a category's existence.

## 0.5.0 / 0.9.0 developer candidate — habitat selection and rotation

- Add By habitat alongside Last selected and Random. On planets, draw native-eligible exact/related/acceptable groups at integer weights 13:5:1, independent of group size. Use the explicit directed habitat table, including Scorched/Lava as related; exclude unlisted pairs rather than drawing an unrestricted fallback. Neutral stations/Nexus use the ordinary eligible pool. Unknown habitat and temporary eligibility/placement wait; a known owned roster without an approved group skips one opportunity with one notice.
- Add optional identity-based, session-only rotation. Reconcile adoption, removal and between-opportunity slot reorder; keep temporary ineligibility separate from ownership. Consume a turn only on native queue acceptance, avoid immediate group-boundary repeats when alternatives exist, and retain a frozen choice during retries. Duplicate identities or a changed pending slot cancel without a replacement draw. Revalidate identity and pending controls after native eligibility calls, immediately before queueing. Local save/app boundaries reset cycles; remote loads do not.
- Schema 4 gives fresh installations By habitat and rotation ON. Legacy schemas 1/2/3 preserve their existing choices and use rotation OFF, with no on-disk migration until an explicit preference save. Manual favourites remain separate. Native rules, limits, delays, mappings, hooks and game saves are unchanged.
- Preserve native role IDs 0–5 and append Rotate companions as role 6, with an original icon and a three-mode selection cycle. Update all fourteen catalogs to 46 keys, source fingerprints and validation; thirteen translations remain drafts and native rendering remains English. The offline native-text matrix covers 2,086 combinations without fallback.
- Pass 396 production and 683 developer tests without failures or skips, actual pyMHF/GUI offline checks, combined two-Mod discovery/shared dispatch/all seven temporary preferences, and Python plus Windows PowerShell 5.1 read-only preflights. Prepare the separate `quick-menu-play-trial-090-r1` with 41 payloads plus its manifest and eight original icons. No deployment or game launch; retained 0.8.7 and earlier artifacts remain unchanged. The new behavior, icon, input paths and multiplayer still need live acceptance.
- Save the complete upcoming-version rules on the unpublished Nexus draft: mode comparison, probabilities, directed habitat list, waiting/cancellation, shuffle, defaults and migration. Preserve 0.8.7 page metadata and its bounded evidence; do not present the unlaunched candidate as a tested release.

## Documentation language consistency — 28 September 2026

- Translate the complete technical verification record, installation requirements and release plan into English, with English filenames. Preserve version-scoped evidence and historical limitations.
- Update documentation links and the source package file list. Require English for canonical and internal documentation as well as executable source. Keep the explicitly labelled Czech user-guide translation and the game language catalogs separate.
- No gameplay, player-facing UI, locale meaning, preferences or running installation changes.

## Nexus profile and presentation preparation — 28 September 2026

- Reuse the authentic, proprietary Lineum Dynamics mark from the owner-designated company repository for the Nexus avatar and a modest cover byline; preserve the mod's own glyph.
- Verify the saved avatar on the owner-created `LineumDynamics` profile. The initial Nexus upload error was resolved on a later attempt, allowing unpublished draft 4579 to be created; no mod archive has been uploaded and nothing has been released.
- Use the complete Nexus page title `Companion Auto Summon for No Man's Sky - by Lineum Dynamics`, including the author credit in the name field. Prepare a dark, subdued 1300 × 372 header background without embedded text or white elements, because Nexus overlays the heading and controls. Keep the full branding on the separate gallery cover and preserve the short in-game title.
- Upload the corrected header after owner confirmation and verify the full title and controls on the actual unpublished page. Keep the gallery cover and avatar unchanged. No runtime or localization meaning changes.
- Explain the planned weighted By habitat mode and optional shuffle separately from the current Last selected/Random controls in the Nexus draft. Do not imply those roadmap features are implemented.
- Add the native settings route and default PC Quick Menu key X, with an explicit note to use the player's assigned key when controls are remapped.
- Keep temporary desktop-panel and standalone-prototype details in internal release notes instead of the Nexus player-facing settings description. Retain the pyMHF runtime requirement and pending native-control validation; no runtime or locale changes.

## 0.8.7 live observations — 28 September 2026

- Launched the unchanged final `087-r1` bundle after normal game closure and a fresh hash-verified backup of 46 profile files. Both Mods and twelve targets registered; all 40 payloads and external preference/state hashes matched at the initial post-start check.
- The player confirmed visible automatic summons after both save load and ship exit in the Space Anomaly. Logs recorded accepted Random requests for different pets (displayed slots 5 and 6), with expected logical active indices. This single session does not explain or establish a fix for the intermittent 0.8.4 startup failure.
- In the subsequent manual-dismissal check, the player reported no apparent reappearance; the requested wait was at least 20 seconds, but its duration was not independently measured.
- The player confirmed the native automation toggle: OFF prevented a ship-exit summon; ON alone did not summon; the next ship exit did. Logs agree, with other logged preferences unchanged and automation left ON. Other controls and restart persistence remain unverified for this version.
- The bounded language observer reported native ENGLISH without changing text. Resource readiness and menu insertion were logged; full visual/control, dismissal, localization and multiplayer acceptance remain incomplete. See [the bounded record](docs/research/LIVE-087.md). No runtime, setting, catalog or running-artifact changes.

## 0.4.9 / 0.8.7 developer candidate — product identity and Lineum Dynamics

- Use **Companion Auto Summon for No Man's Sky**, with **by Lineum Dynamics**, for the external product identity. Preserve the short native title, code/class/file identifiers, repository slug, mutexes and legacy player-data paths.
- Record the existing private repository transfer to `lineum-dynamics/nms-companion-auto-summon`, retaining repository identity and history. Update canonical links, source author/product metadata, README files, build metadata and the Nexus draft. No new license or legal IP assignment is introduced.
- Maintain 41 entries in every one of the fourteen catalogs: add the invariant full product name and translated author credit, and expand the product name in the three affected launcher messages. Native menu/HUD wording remains unchanged. Preserve draft review status and verify PowerShell's escaped apostrophe in the emergency title.
- Production version 0.4.9 and menu 0.8.5-branding retain the prior summon and diagnostic behavior. The new separate 0.8.7 bundle does not deploy or launch. Live 0.8.4 and prepared 0.8.6-r1 remain unchanged; no gameplay acceptance is inherited.
- Passed 333 production and 675 developer tests without failures or skips, standalone/combined real-framework offline checks, and Python plus Windows PowerShell 5.1 read-only preflights. Runtime AST comparison confirms only product/author/version metadata and the diagnostic version marker changed. The combined candidate contains 40 payloads plus its manifest.
- The weighted habitat-selection mode is a separate design proposal, with suggested Fibonacci group weights of 13:5:1 and optional shuffled cycles within each selected group. Current selection modes, default `last_manual`, exact-biome preference and fallback remain unchanged.

## 0.8.6 developer candidate — observation-only game language

- Retain byte-identical production 0.4.8, including bounded post-queue diagnostics, and all six existing menu controls. Add menu 0.8.4-language-observation with no new native hook, getter, setter or save access.
- Observe only copied language scalars while an owned CAS caption is selected. Require matching double reads, a completed constructor guard, the expected vtable, a valid native enum and prior table-load completion. Limit sampling and reports; isolate read, logging and construction failures from the menu and automatic summoning.
- Record that native language reload does not clear the completed-load byte. Observations cannot establish current rendering readiness and do not select a catalog. Verify the exact-build UTF-8 measurement and drawing decoders through static analysis and offline emulation; live fonts, glyphs and layout remain unverified.
- Pass 675 developer tests, including twenty new observer/integration cases. The final separate `quick-menu-play-trial-086-r1` has 40 payloads plus its manifest; real-framework discovery, shared Python dispatch, all six temporary preferences and Python/Windows PowerShell 5.1 read-only preflights passed. The earlier `086` output is superseded and must not be launched.
- Production retains its unchanged 333-test evidence. No live trial or deployment occurred. Running 0.8.4 and prepared 0.8.5 remain immutable. Locale impact: no player-facing text or meaning changes; all 39 keys in all fourteen catalogs stay unchanged and validated.

## Unreleased research — native text and portable host preparation

- Add an offline native menu/HUD text renderer using an immutable validated catalog snapshot. Preserve current preference/notice semantics, reject invalid data and use a complete English message with an explicit reason when a translation exceeds byte bounds. No truncation, native calls, automatic language detection or runtime integration.
- Pass fifteen focused text tests and 1,666 current language/state combinations across all fourteen catalogs without overflow fallback. Record exact-build static language-field evidence separately from still-unverified readiness, decoder and glyph behavior.
- Add a host-only noninteractive pyMHF import prototype and a bounded real subprocess comparison. Seven focused tests passed; ordinary no-console import reproduced `NoConsoleScreenBufferError`, while the adapted import succeeded without test bypasses. Current launchers/configuration are unchanged; injected-side imports, lifecycle and portable distribution remain unverified.
- The complete developer suite passed 655 tests with no failures or skips, including the 22 new preparation tests. Retained 0.8.5 bundle validation still describes its original 633-test candidate; these tools do not add live acceptance to that artifact.
- Locale impact: no player-facing text or meaning changed; all 39 keys and all fourteen catalogs remain unchanged. Running 0.8.4 and prepared 0.8.5 stay unchanged.

## 0.4.8 / 0.8.5 developer candidate — bounded follow-up after logical activity

- Preserve passive post-queue observation after the first matching active index, until the existing 15-second / 4096-callback limit or cancellation. Deduplicate active/pending transitions, including disappearance, within the existing log cap. Terminal diagnostics distinguish whether activity was ever seen and do not claim rendering or a cause of removal.
- Keep native ownership, placement, calls, hooks, summon policy, timing and manual-dismissal behavior unchanged. No retry, save mutation or player-facing text change is added. Locale impact: all fourteen catalogs remain unchanged and require validation.
- Passed 333 production and 633 developer tests with unchanged sources and no skips, including four added runtime regressions. Real-framework standalone and combined discovery/dispatch/temporary-preference checks passed without game access.
- Prepare a separate 0.8.5 candidate and version-pinned bridge; the running 0.8.4 bundle is immutable. This candidate is not a spawn fix or live-verified release.
- Record live 0.8.4 registration and six visible role icons, one failed visible Nexus load and one later successful ship exit with a different Random pet. Retain the failure and comparison without attributing a cause.
- Refresh the monetization policy review and preserve unsent clarification drafts; no financial interface, external contact or account was configured.
- Align the release backlog with the running 0.8.4 evidence and unlaunched 0.8.5 candidate; prepare one combined gameplay/menu/HUD test. Record the owner's neutral activation-plus-donation-information proposal without inventing a destination or policy permission. External contact remains declined. Documentation only; no runtime or locale text changes.


## 0.8.4 developer trial — guarded launch and localized compatibility failures

- Prepared a separate launcher candidate with byte-identical production 0.4.7 and menu 0.8.3. Prior 0.8.2/0.8.3 artifacts stay unchanged; no launch or deployment is part of this change.
- Added selected-game preflight to direct Python startup and a shared actual-process image/path/hash check before each DLL injection. Retained post-injection DLL identity verification and the independent pre-hook class guards. Reject foreign pyMHF libraries and changed/extra standalone launch configuration.
- Added nine outside-game compatibility messages in all 14 catalogs (39 keys total). Windows UI language or an explicit launcher language selects the text; unsupported languages use English. Missing or invalid message resources use maintained English emergency text. No-dialog and check-only paths avoid modal UI. Thirteen translations remain drafts; other launcher and native text are not fully localized.
- Added build-time agreement checks for host/profile/manifest, native mapping, generated framework pin and developer targets. No unknown-build override, native HUD call, setting reset or save mutation is added.
- Corrected the real Windows PowerShell 5.1 Python probe quoting and UTF-16 image-path length validation. Foreign framework libraries now fail both preflight and normal startup. Passed 329 production and 633 developer tests, including 19 actual PowerShell integration cases; the final 40-file candidate passed real-framework discovery and both read-only launch preflights. No game launch or deployment occurred.

## Unreleased research — earned companion technologies

- Added an isolated immutable energy model with separately confirmed debit and battery-refill requests, stale-context rejection, one-request accounting and bounded warning suppression. Queue acceptance alone cannot incur a charge. No production import, native inventory mutation or save access was added.
- Prepared the offline native-data direction for Companion Link and Companion Recharger, with stable authored IDs, an earned research branch and provisional recipes. Native registration, charge APIs, persistence, removal and mixed multiplayer remain unverified; the technology prototype is not installed or included in the player package.
- Added six technology name/subtitle/description entries to every catalog: 14 catalogs with 30 keys each, thirteen honest translation drafts. The original 24 entries and source checks remain unchanged; native language selection/rendering is still unfinished.
- Recorded automatic refusal on unknown game builds and a clear localized outside-game warning as release requirements. Existing exact-hash/pre-hook guards remain; direct standalone-host pre-injection coverage and final warning presentation are unfinished. Saved custom technology requires separate update/removal verification.
- Passed 601 developer tests, including 17 energy and 18 technology-data cases. Actual target-data build and all three MXML/MBIN/MXML semantic roundtrips passed with compiler 7.04.0.1. Rebuilt production remains byte-identical. No technology or runtime deployment occurred.

## 0.8.3 developer trial — role icons and maintained locale drafts

- Prepared a separate, unlaunched menu 0.8.3 with unchanged production 0.4.7. The previous 0.8.2 installation is immutable; this change does not deploy into the game.
- Added six original setting icons alongside the existing parent/notice icon. Each role has a separately owned texture, with a retained native paw fallback. Validate all seven source/destination assets before staging at a later closed-game launch. No shared vanilla textures are replaced.
- Renamed the biome row to `Random: prefer matching biome`; it still affects only Random on planets and preserves its stored value in Last selected mode.
- Added 14 UTF-8 menu/HUD catalogs with 24 keys each. English is canonical; the other 13 are unreviewed drafts. Builds and release packaging reject missing/stale entries, mismatched placeholders and drift from current English menu/HUD source. Runtime integration, game-language detection, glyph/rendering checks and panel/launcher coverage remain unfinished.
- Required a locale-impact review with every change and same-change updates for affected source text and translations. Recorded the request for native number shortcuts; current tagged None entries stay protected until persistence and replay are verified.

## 0.4.7 — read-only preflight and duplicate-launch protection

- Combined 0.8.2 registered two Mods and 12 targets at 23:58:46 on 27 September 2026 after a verified 43-file backup. Automation is ON; 17 payloads and player files matched. DDS staging and one native resource registration were observed, while visible icon/HUD and control acceptance remain pending. Passed 294 production and 519 developer tests plus real-framework and Windows checks.

- Combined0.8.2 repairs process enumeration: a complete native Windows Toolhelp snapshot recognizes protected system processes whose names psutil omitted. Unknown names, incomplete enumeration and errors still refuse launch. Earlier0.8.1 attempts stopped before asset staging or NMS startup; its built files are retained.

- Prepared the next production 0.4.7 / combined 0.8.2-play-trial candidate. Production behavior is unchanged from 0.4.6 apart from version metadata. The native menu remains 0.8.0-settings-trial, with the same six settings and icon path. Running 0.7.1 and prepared 0.7.2 / 0.8.0 artifacts remain unchanged.
- Added PowerShell `-CheckOnly` to validate package/game/existing-runtime prerequisites while NMS may remain running. It creates, installs, stages and starts nothing; missing prerequisites are reported. This check does not validate gameplay.
- Added distinct fixed `Setup.v1` and `Host.v1` Windows session mutex leases, shared across package folders. Leases remain for their OS handle lifetime and disappear when the last handle closes, including after a crash; no stale lock-file cleanup is needed.
- Normal setup refuses to continue when process enumeration fails. The portable public installer and localization remain unfinished. Live validation is pending; test evidence will be recorded separately for this revision.

## 0.4.6 — optional notification icon and complete settings trial

- Prepared production 0.4.6 with combined 0.8.0; neither has launched. Running 0.4.4 / 0.7.1 and unlaunched 0.7.2 remain unchanged. The manual-origin repair and 5.5-second notices from 0.4.5 are retained without new summon rules or timing.
- Added an optional notice-icon provider to the real production instance. A ready owned custom icon or retained native paw can be supplied by the combined trial; absent/invalid providers preserve text-only notices. The standalone ZIP includes no custom texture or native menu.
- Expanded the opt-in native page to all six existing preferences: automation, Last selected/Random, matching biome and three locations. One-use per-setting tokens preserve unrelated queued changes and the manual favourite, with pending/session-only captions. The temporary development panel remains until live acceptance passes.
- Added automatic staging of the original DDS at a unique mod path before a future game-closed launch. One verified natural resource phase attempts registration; buffers/references stay process-pinned, with fresh readiness checks and no shared texture replacement, retry or late load. Actual resource lifetime, rendering and all six controls remain unverified in-game.

## 0.4.5 — manual-selection attribution and readable confirmations

- Prepared production 0.4.5 and combined play trial 0.7.2; neither has launched. Running 0.4.4 / 0.7.1 remains unchanged.
- Learn a favourite only from a paired successful native companion UI action with a matching accepted queue and revalidated identity/context. Unknown queues, including native restoration, cannot replace it or show a manual-choice notice. The earlier arena caller remains unknown; existing choices are not rolled back. Attribution faults leave automation working.
- Request 5.5-second explicit confirmations: `Companion saved.` only after persistence succeeds, otherwise `Companion selected (session only).` Preserve OFF/Random context and silence repeated choices, automatic summoning and game restoration.
- Enable the statically verified final timed-message flag that hides both icon containers while retaining text. Preserve the native ABI and owned buffers. The white-disc outcome still needs an in-game visual check.
- Passed 279 production tests (189 runtime, including 26 new cases) and 408 developer tests. Actual pyMHF/GUI and final combined-bundle checks passed: nine production plus eight menu callbacks share eleven targets. Shared Python dispatch passed both callback orders with all four Boolean result combinations and one mocked original call. Native hooks were not bound; no game access occurred. The generated PowerShell launcher parsed successfully.

## 0.4.4 — passive post-queue diagnostics

- Recorded an open manual-attribution defect after the 0.7.1 arena report: an accepted non-CAS queue changed the stored favourite from slot 3 to slot 2; user intent was not recorded. A later read-only native snapshot found no active/pending pet. A static pet-battle restore caller reaches the same queue hook, but the live caller remains unproven. That version's three-second notices and white-disc rendering were unchanged; no attribution or HUD fix was claimed.
- Launched combined 0.7.1 after normal game exit and a fresh hash-verified backup of 43 profile files. Both Mods and 11 hook targets registered at 22:22:35 on 27 September 2026 with automation ON; all 14 payloads and the existing settings/state matched at startup. A subsequent Random-mode Anomaly load queued slot 2 after a logged 2.56 seconds; the first observer callback recorded the expected active companion 0.02 seconds later and stopped. The player confirmed visible appearance, without a preceding ship exit. This one success does not resolve the earlier intermittent failure.
- Added bounded observation after matching native queue acceptance, using the existing local ownership callback and verified fields. Records the trigger source and sanitized queue/active transitions; a native active slot is not claimed as visible spawn.
- Observation ends on active-pet detection, replacement/cancellation, invalid state or diagnostic time/read limits. Queue disappearance remains indeterminate and never retries or re-arms automation. Existing policy, native calls, gameplay limits, delays and preference application are preserved.
- Prepared combined trial 0.7.1 with the existing 0.7.0 toggle and a version-pinned bridge for production 0.4.4. Running 0.7.0 remains unchanged. No new live result; Anomaly startup and the white HUD disc remain open.

## 0.4.3 — summon opportunity after loading

- Recorded partial 0.7.0 native-toggle evidence: player-reported ON ship-exit summoning and later OFF suppression, matching queued/applied logs and an OFF menu/HUD screenshot. Rapid toggles were repeated presses; held input remains untested. Recorded a failed visible Anomaly startup despite accepted queue and an unwanted white HUD disc. No running payload was modified; queue acceptance is not spawn confirmation.
- Launched separate play trial 0.7.0 after normal game exit and a fresh hash-verified backup of 43 profile files. At 21:48:38 on 27 September 2026 both Mods and 11 hook targets registered with automation ON. All 14 payloads remained unchanged; existing settings and companion memory matched their pre-launch hashes in the initial startup check. Complete live toggle validation remains pending.
- A successful local save load records one deferred summon opportunity when automation is enabled. An eligible local ownership update restores the saved identity or uses Random, then follows the existing 1.5-second stability, native ownership and paced placement checks. No native calls occur during save deserialization.
- Existing active/queued pets, manual selection/preview, entering the ship, preference changes, another local load or loss/replacement of application context cancel the opportunity. It is consumed before arming; later manual dismissal does not cause repeated respawning. Missing ownership data is retried at the existing 0.5-second interval without guessing another pet.
- Kept the same native mappings, hook targets, gameplay limits and external preference paths. Updated the panel wording and prepared combined play trial 0.6.2 with the existing ordered inert menu. After a fresh verified backup of 43 profile files it registered at 20:42:21 on 27 September 2026 with automation ON and two Mods/ten managed hooks.
- Confirmed one Random-mode summon after an on-foot station load in combined 0.6.2: local save load armed the request, native checks waited, and slot 1 of five eligible owned companions was queued after approximately 2.69 seconds. No ship-exit trigger preceded that startup request, and the player confirmed actual appearance. Nexus/planet startup, Last manually selected startup and broader compatibility remain unverified.
- Recorded one later player-confirmed manual dismissal without reappearance in the unchanged 0.6.2 session. Travel separated it from the station startup; exact dismissal location and duration were not independently measured. No runtime changes were needed.

## Development — native quick-menu investigation

- Prepared the separate 0.7.0 play-trial source: one native automation ON/OFF
  control using the unchanged 0.4.3 production preference queue. A fresh native
  confirmation and matching original false trigger result are required;
  navigation/rebuild or uncorrelated tail activation cannot queue a change.
  One-use captures refuse stale/replaced/stopped state and preserve other
  preferences. Captions distinguish pending and session-only state. Live
  activation, held input and remapping/controller behavior remain unverified.
- Recorded the accepted retirement of the temporary pyMHF settings panel once
  all native controls are implemented and verified. Existing preferences and
  the background runtime remain; the running 0.6.2 artifact is unchanged.

- Started 0.6.1 after normal game exit and a fresh verified backup of 43 profile files. The log confirms automation ON and two Mods/ten managed hooks. All twelve payloads and both existing external configuration files remained hash-identical at startup. Actual combined summoning and visible menu order await the player's check.
- Prepared the 0.6.1 combined play trial: unchanged 0.4.2 automatic summoning plus the ordered inert menu in one verified pyMHF folder-mode host. Existing preferences and manual selection remain at their original external paths. All 341 developer tests and actual framework discovery passed; the thirteen-file artifact has not been launched and live coexistence remains pending.
- Launched the isolated 0.6.0 ordering trial after a fresh verified backup of 43 profile files. Registration reports one Mod/four managed hooks; visible order remains pending. Recorded the requirement to retain functional automatic summoning and existing preferences during subsequent menu development sessions.
- Prepared a separate disabled 0.6.0 ordered submenu trial. It inserts the settings parent before the first individual pet/page during native construction, uses the validated original append trampoline and retains the inert child and native binding guard. The end fallback refuses already-present pets. All 309 developer tests and the real disabled-framework smoke passed. Its new ten-file artifact has not been launched; live ordering remains pending and the running 0.5.0 trial is unchanged.
- Added original SVG artwork and a transparent PNG/RGBA32 DDS icon candidate with independently verified pixel equality. No custom texture is installed or loaded yet, and the asset is excluded from the player ZIP.
- Captured the first visible 0.5.0 submenu result: the player confirmed the inert child, native Back/close/reopen and manual summoning, and two screenshots confirm the normal captions without inline duplicate text. The original paw remains in use. Recorded the requested position before individual pets; this has not been changed in the running trial.
- Launched the isolated 0.5.0-submenu-trial after normal game exit, a fresh hash-verified backup of 43 profile files and independent artifact preflight. At 19:41:52 on 27 September 2026 the native binding guard reported ready, followed by one Mod/three managed hooks. Registration is confirmed; visible submenu/navigation behavior remains pending. All eight payload hashes remained unchanged after startup.
- Recorded the player's successful inert-item selection, Back/close/reopen and manual companion summoning; the running 0.4.0 trial's seven payload hashes remain unchanged. This does not validate shortcuts, remapping or a custom submenu.
- Added a separate disabled-by-default 0.5.0-submenu-trial with one inert Settings preview child, empty tile names, paired native activation callbacks and scoped captions. It preserves original arguments/results, native Back and existing bindings, uses native allocation/selection, and never writes the native deferred-selection flag. No preferences, summoning or custom texture are included. All 255 developer tests and the real disabled-framework metadata/mock-dispatch check passed; live submenu behavior remains unverified.
- Added an isolated nine-file submenu builder with explicit enablement, helper hashes and overwrite refusal. It never launches or deploys. The independent custom-icon loader audit remains a feasibility result; no custom asset loading was performed.
- Prepared source revision 0.4.1-inert-item-trial to remove the redundant inline tile name while preserving the ordinary selected-item caption. The screenshot confirms both had appeared together. All 50 affected item/trial tests, seven builder checks and the real disabled-framework smoke passed. The current running 0.4.0 trial is unchanged; this revision has not been built or deployed.
- Clarified that the entry is intended to open one flat settings page. Saved an original paw/circular-arrow icon concept as an opaque preview in the source repository, excluded from the player ZIP; transparent attempts had artifacts and were rejected. Final texture preparation, the submenu and custom texture integration remain unfinished.
- Implemented a separate disabled-by-default inert-item trial with a native leaf binding filter. The entry uses native construction/append, a full private marker and a bounded label; it has no preference or summoning effect. The production mod remains unchanged.
- After normal game exit and a fresh hash-verified backup of 43 profile files, the isolated trial registered in NMS at 18:46:26 on 27 September 2026. Its native binding filter reports ready and pyMHF reports one Mod/two managed hooks. Visible entry, navigation and shortcut behavior remain pending; registration is not a functional menu result.
- Subsequently captured successful native append/readback and label callbacks. The player confirmed the entry appears after the individual pets with the borrowed paw icon and moving text inside the icon. This is the first visible result; presentation review and the full navigation/shortcut/replay scenarios remain separate. The running trial was left unchanged.
- The native filter passed 45 own-process MinHook cases and 10,000 repeated calls. Unrelated input calls forward without Python callbacks or menu reads; protection follows item identity and the exact native operation, not physical buttons. Process-pinned guard resources survive stopped callbacks, with explicit installation/integrity checks and no unload endpoint.
- All 184 diagnostic/developer tests pass, together with the real disabled-framework metadata check. Independent review corrected missing Mod initialization, late-callback cancellation and diagnostic error handling. The isolated builder checks all helper hashes and never replaces, deploys or starts a running artifact. See `QUICK-MENU.md` for the remaining live, replay and remapping scope.
- Prepared a third, menu-local phase observer to investigate controls completion, binding boundaries and final selection handling without a global input hook, key-state reads or game writes. Source/live validation is recorded separately in `QUICK-MENU.md`; this is not a binding guard or custom menu item.
- The phase observer passed 34 focused tests and the real pyMHF ABI/owned-buffer check; all 101 diagnostic tool tests passed. Fixed a review-discovered interruption race and verified record cleanup. After normal game exit and a fresh verified backup, it loaded in NMS with three native hooks/four callbacks.
- Captured 22 changed phase records reaching 749 updates and 52 completed samples, with stable controls-to-tail snapshots and no recorded observer failure. The player reported normal native-menu behavior. The observer deliberately has no mod item; binding protection and a visible prototype remain unimplemented.
- Located exact-build construction, append and label paths through static analysis, with remaining action-ID and text-handling constraints documented in `QUICK-MENU.md`.
- Added a separately enabled developer observer and isolated build tool. It only reads bounded action/depth scalars before natural menu calls; it does not insert entries, summon companions or change preferences.
- The first observer passed 24 offline tests and real-framework metadata checks, then loaded in the supported game with one hook. It captured companion submenu action 45 at depth 0 and summon action 46 at depth 1; the player confirmed opening the menu and manually summoning a pet. This is not a working custom-menu claim.
- Prepared a separate construction/label observer with bounded read-only sampling, passing 37 focused tests and actual pyMHF 0.2.4 metadata/owned-buffer checks. Independent review identified and confirmed a timestamp ordering fix for interleaved callbacks. After normal game exit and a fresh backup, it loaded in NMS with two hooks.
- Captured natural root/companion rebuilds and label completion during the player's menu sequence: 28 changed builder snapshots, 25 label snapshots, recorded counters reaching 926 callbacks/64 samples per channel, bounded terminated labels and no observer failure. This establishes the observed read-only paths, not safe insertion or a custom settings entry.
- The builder now refuses to overwrite existing diagnostic folders, preserving any running trial; five offline builder tests cover isolation, opt-in, hashes and overwrite rejection. The combined diagnostic tool suite passed all 66 tests.
- Traced native hotkey serialization: binding a custom None action could overwrite an existing saved shortcut, so a verified binding guard remains a prerequisite for insertion. No custom binding or save change was performed by the observer.
- Recorded remappable keyboard/mouse and controller controls as an explicit acceptance requirement: protection must follow the tagged item/native operation, not fixed physical keys. No custom-menu remapping support is claimed yet.
- The production 0.4.2 script remains unchanged. The separate inert-item source candidate is not an implemented player settings feature; in-game preferences remain unfinished.

## 0.4.2 experimental — 2026-09-27

- Adopted the approved name **Companion Auto Summon** and repository slug `nms-companion-auto-summon`, replacing the working name AutoPet.
- Renamed the standalone script, guarded launchers, internal identifiers, diagnostics and current documentation. The pyMHF tab uses its class name, `CompanionAutoSummon`.
- Kept the legacy `NMS-AutoPet` preference, manual-selection and development-runtime paths, with unchanged stored schemas and defaults. No personal data migration or gameplay-rule change is part of this rename.
- Retained old version records and checksums under their historical names. Current verification is recorded in the 0.4.2 manifest; earlier offline and live results are not relabelled as tests of this version.
- Passed 212 offline tests and the real pyMHF 0.2.4 / Dear PyGui 2.3.1 check with one renamed class, eight widgets, seven callbacks for six targets and zero hotkeys. The added regression check verifies existing preference and manual-selection storage compatibility.
- Added a maintained roadmap separating accepted release work from proposed features and support-link policy questions. Included the roadmap and linked release documents in the source package.
- This source candidate has not been deployed or launched in NMS. Native-menu integration, localization and the portable public launcher remain planned work.

## Development — local Git baseline

- Established one canonical Git source tree with English development instructions, explicit ignore rules and preserved release plans.
- Added repository-relative offline validation, framework smoke and packaging tools. Packaging has no implicit deployment or game access.
- Retained gameplay candidate 0.4.1 unchanged; moving to Git does not establish additional in-game validation.

## 0.4.1 experimental — 2026-09-27

- Added an optional matching-habitat preference for Random mode on planets, enabled by default. Unknown habitat or no eligible match falls back to ordinary Random.
- Added the eighth settings widget and schema 3 migration while preserving previous preferences.
- Retained a fixed companion selection during deferred retries and preserved the manual favourite.
- Passed 211 offline tests and real-framework construction/callback checks for eight widgets. New gameplay behavior has not yet been validated in NMS.
- Added English development, localization and player-experience documents. Recorded the English-source requirement and retained Unicode test coverage using explicit escape sequences.
- Recorded portable installation, translation catalogs and native quick-menu integration as planned work. They are not features of this release.

## 0.4.0 experimental — 2026-09-27

- Added Random selection, independent location preferences and waiting for a suitable place without the former 12-second expiry.
- One Random selection and planetary summon were confirmed by the player and log; the manual favourite remained unchanged in the running session.

## 0.3.3 experimental — 2026-09-27

- Allowed the native station/planet/Nexus location set while retaining native permission and placement checks.
- A station summon and restoration of the manual selection after restart were confirmed in a controlled session. Nexus behavior remained unverified.

## 0.3.2 experimental — 2026-09-27

- Added native placement refresh without requiring the quick-menu companion preview.
- A basic planetary summon and remembered selection were confirmed in a controlled session.

Earlier prototypes and detailed version-scoped analysis are described in `TECHNICAL-VERIFICATION.md`. Do not interpret a historical test as validation of every later version.
