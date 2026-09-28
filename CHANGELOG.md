# Changelog

## Documentation language consistency — 28 September 2026

- Translate the complete technical verification record, installation requirements and release plan into English, with English filenames. Preserve version-scoped evidence and historical limitations.
- Update documentation links and the source package file list. Require English for canonical and internal documentation as well as executable source. Keep the explicitly labelled Czech user-guide translation and the game language catalogs separate.
- No gameplay, player-facing UI, locale meaning, preferences or running installation changes.

## Nexus profile and presentation preparation — 28 September 2026

- Reuse the authentic, proprietary Lineum Dynamics mark from the owner-designated company repository for the Nexus avatar and a modest cover byline; preserve the mod's own glyph.
- Verify the saved avatar on the owner-created `LineumDynamics` profile. Keep the description and cover local: Nexus's upload dialog currently reports an error with mod upload disabled, so no mod draft or archive has been uploaded and nothing has been released.

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
