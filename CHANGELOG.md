# Changelog

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

Earlier prototypes and detailed version-scoped analysis are described in `TECHNICKE-OVERENI.md`. Do not interpret a historical test as validation of every later version.
