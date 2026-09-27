# Companion Auto Summon development guide

This repository is the canonical development location. Keep installed test copies and prior exports as deployment artifacts, not as competing source trees. Record live observations against the exact version; neither the historical 0.4.2 rename nor the new 0.4.3 load trigger inherits earlier gameplay verification.

## Project rules

- Write all source code, identifiers, comments, docstrings, test names, build scripts and developer diagnostics in English.
- Put translated player-facing text in separate locale resources. English is the canonical source language. Non-English text belongs in translation data or deliberately encoded Unicode test fixtures, not explanatory source prose.
- Update implementation, relevant tests and affected documentation in the same change. Do not leave the description of defaults, behavior, setup or support scope behind the code.
- Preserve native ownership, summon eligibility and placement checks. Do not generate or unlock companions, reduce gameplay limits, accelerate growth or alter game-save files.
- Never edit a running installation or terminate the game or its runtime as part of routine deployment. Preserve current progress before a new live trial.
- Keep personal saves, settings, accounts, logs, raw executable analysis and developer-machine paths out of public packages.

## Current implementation

The current candidate is 0.4.3-experimental. It adds a deferred, one-shot opportunity after a successful local save load to the existing ship-exit behavior. The load-triggered behavior is not yet live-verified. Its intended target remains Windows x64, Steam build 25442159 / Cosmos 7.04, the exact executable hash in `manifest.json`, and pyMHF 0.2.4. The present development launcher accepts Python 3.11–3.13 x64.

| Component | Responsibility |
|---|---|
| `src/policy.py` | Shared timing, pending-request and cancellation decisions |
| `src/persistence.py` | Per-save manual companion identity and atomic local storage |
| `src/settings.py` | Validated global preferences, schema migration and atomic storage |
| `src/runtime.py` | Exact-build guards, native callbacks, placement checks, settings panel and HUD |
| `build.py` | Concatenates these components into the standalone `CompanionAutoSummon.py` |
| `Launch-CompanionAutoSummon.py` | Host-side DLL address/path validation before invoking pyMHF |
| `Start-CompanionAutoSummon.ps1` | Current development setup, package/game checks and launch |
| `tests/` | Offline decision, storage, adapter and launcher checks |

Function addresses are relative to the loaded game module. Runtime objects and save identities are obtained from the running game. An exact executable hash guard disables Companion Auto Summon before hook registration on unsupported binaries. This supports portability of the addressing scheme for the same binary; it does not prove second-PC, multiplayer or cross-platform compatibility.

The default mode remembers the last manually summoned pet per save. Random mode uses the native-eligible owned pool, optionally narrowed to the planet's native habitat. Unknown habitat or an empty matching subset falls back to the full eligible pool. A selected pet remains fixed for that request and does not overwrite the manual favourite. Preference changes cancel pending intent without dismissing an active pet.

Successful local `LoadFromData` completion records one deferred opportunity when automation is enabled and common data is available. It makes no native summon, ownership-eligibility or placement function calls. A zero persistent ID still allows a session-only Random opportunity; it does not restore another save's favourite. Network-client loads leave the local context alone, and failed local loads create no opportunity.

The existing local ownership-update callback observes active/queued pets, preview/emote state, location and advancing time before preparing the load request. Last-manual identity restoration retries at the existing 0.5-second pace while the saved companion is unresolved; absence on the first frame is not proof of removal. No saved/manual choice finishes that opportunity without selecting another pet. Random uses the existing eligible pool. Once prepared, the opportunity is consumed before entering the same policy, unchanged 1.5-second stability delay and native placement/queue path used by a ship exit. No new hook, native offset, gameplay limit or preference is required.

Accepted manual selection, ship entry, a real local ship exit, applied preference changes, a later local load, unavailable/replaced application context or a runtime stop cancel or supersede the deferred opportunity. Active/queued pets and preview/emote observations consume it even while paused or outside supported locations. Supported locations disabled by the player cancel it; unsupported locations wait without placement calls. The first application acquisition preserves the opportunity, while a later replacement cannot inherit it. A dismissed pet does not re-arm a completed opportunity; only another successful local load or real ship exit can start one. This contract does not claim that deserialization proves ownership or physics readiness.

GUI callbacks queue preference changes under a lock. The local player callback applies them. Native game operations belong to the established game callbacks, never to an installer or asynchronous GUI thread.

## Naming and compatibility

The public name is **Companion Auto Summon**; the repository slug is `nms-companion-auto-summon`. The private GitHub repository is [TomasTriska88/nms-companion-auto-summon](https://github.com/TomasTriska88/nms-companion-auto-summon). Remote existence and privacy have been verified; a push is a separate operation and must be confirmed by reading back the remote commit.

The standalone file is `CompanionAutoSummon.py`, with `Launch-CompanionAutoSummon.py` and `Start-CompanionAutoSummon.ps1`. The pyMHF class and its current tab are `CompanionAutoSummon`. Preserve the framework's inherited class identity: overriding `_mod_name` independently breaks its loader/reload and GUI mappings. Do not export a second legacy alias for the Mod class, which the loader can discover as an additional mod.

Keep `%LOCALAPPDATA%/NMS-AutoPet/state.json`, `settings.json` and `runtime-0.2.4` at their legacy paths. This compatibility namespace intentionally survives the rename, preserving preferences, per-save manual selections and the prepared development environment without migration. Stored keys, schema versions and selection values are unchanged. Never rename an existing venv as a branding operation.

Only the current source and new packages receive the new names. Historical test records, immutable checksums and old installed/exported copies keep their original names. Document a later deployment explicitly; a source rename is not a deployment.

## Documentation map

- `README.md`: canonical English player guide, supported target, behavior, setup and removal.
- `README.cs.md`: Czech companion guide; keep behavior and status aligned with the English guide.
- `DEVELOPMENT.md`: canonical development rules, architecture and maintenance workflow.
- `DESIGN.md`: accepted player-experience direction, native menu/notification goals and current implementation limits.
- `QUICK-MENU.md`: exact-build menu investigation, retained observers, confirmed basic inert-item navigation, separate one-child submenu candidate and staged live-validation procedure; no live-verified custom settings are claimed.
- `ROADMAP.md`: canonical unfinished release backlog and explicitly unapproved future proposals; update status and evidence as decisions are made.
- `LOCALIZATION.md`: localization status, target languages and implementation/verification requirements.
- `CHANGELOG.md`: version-scoped changes; update with each user-visible behavior or distribution change.
- `TECHNICKE-OVERENI.md`: existing Czech technical evidence and version-scoped history. Retained private evidence is named as an external record; it is not distributed or linked through nonexistent repository paths.
- `manifest.json`: exact package hashes and bounded validation claims; generated during packaging.

The release-preparation documents in `docs/release/` contain the publication plan (`PRIPRAVA-VYDANI.md`), installer acceptance criteria (`INSTALACE-ZADANI.md`) and English draft Nexus page (`NEXUS-DESCRIPTION-DRAFT.md`). Private test evidence is retained outside this repository and the public package. Do not copy that evidence directory wholesale into a release to repair documentation links.

## Repository commands

Run these from the repository root with a supported Python interpreter:

The `tools/` commands below belong to the Git source checkout; they are not included in the player ZIP.

```text
python -B build.py
python -B tools/validate_offline.py
```

The offline suite needs no running game. Validation reports are generated under `build/validation/` and ignored by Git.

Run `python -B tools/framework_smoke.py` with an interpreter containing the supported pyMHF 0.2.4 GUI dependencies. This command constructs the real GUI widgets without a viewport or game connection and writes its report alongside the offline results. It is an explicit development verification step, not a player installation requirement for the planned portable release.

After both reports match the current source, run `python -B tools/package.py`. It regenerates package hashes and creates a verified ZIP in `dist/`. It never deploys the package, starts NMS or copies files into an installation. The generated `CompanionAutoSummon.py` and `manifest.json` are retained in Git so each committed baseline includes its exact standalone script and distribution metadata; rebuild and refresh them before committing relevant changes.

Before a local commit, inspect `git diff` and `git status --short`. Save only the intended source, documentation and tooling. Remote publication is a separate step; a local commit is not a backup on another machine.

## Validation and maintenance

Run `python -B build.py` after changing source fragments. Run meaningful affected tests; the current full offline suite is `python -B -m unittest discover -s tests -v`. Version 0.4.3 passed 230 production tests: 140 runtime, 34 policy, 24 settings, 14 persistence and 18 launcher. The separate developer suite passed 341 tests. The real production GUI smoke and actual-folder discovery smoke for the prepared 0.6.2 combined artifact also passed without game access or hook registration. Source hashes and bounded validation claims are recorded in `manifest.json` and the development validation reports. The historical 0.4.2 candidate passed 212 production tests; AutoPet 0.4.1 had 211. Tests use simulated native calls and owned buffers; passing them does not verify a game's binary interface or actual spawning.

The real-framework smoke check separately verifies widget construction and callbacks without hook registration or a game connection. Record the exact source bytes tested. After gameplay changes, collect relevant live evidence for that version, including the player's visible result. Never copy a previous version's live-success flag into a new release merely because its tests pass.

For every behavior or packaging change:

1. Update the relevant guide, defaults, known limits and locale resources where applicable.
2. Record relevant validation and unresolved cases with the exact version.
3. Rebuild and regenerate package hashes from the verified files.
4. Check extracted package contents, documentation links and data privacy.
5. Deploy only with the game closed; perform the live scenarios affected by the change.

## Remaining release work

The 0.4.3 load-triggered behavior remains live-unverified. Production 0.4.2 was subsequently registered in the combined 0.6.1 play trial, whose log recorded an accepted station queue at 20:18:19; no new visible-pet confirmation accompanies that observation. Earlier statements that 0.4.2 had never launched describe its original rename checkpoint, not the current evidence. The biome preference, second-PC installation, multiplayer and several placement/control scenarios still need live validation. Historical successes of 0.4.0 and earlier are described separately in the guides.

The proposed public installer is a portable, offline bundle with a tested private runtime and a graphical launcher. It has not been built. The existing development venv is not portable and must not be redistributed as if it were self-contained.

Localization is also not implemented. Current UI and HUD messages are English. See `LOCALIZATION.md` before changing display strings or claiming translated support.
