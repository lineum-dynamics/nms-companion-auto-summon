# Changelog

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
