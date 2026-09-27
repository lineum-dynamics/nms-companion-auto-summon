# Companion Auto Summon development instructions

- The approved public name is Companion Auto Summon; the repository slug is `nms-companion-auto-summon`. Keep the legacy `NMS-AutoPet` data and development-runtime paths for compatibility; do not silently reset or migrate player data during a rename.
- This repository is the canonical source. Installed game-test copies and old exported packages are outputs, not parallel development roots.
- Read `DEVELOPMENT.md`, `DESIGN.md`, `LOCALIZATION.md` and the current manifest before changing behavior or compatibility claims.
- All source code, identifiers, comments, docstrings, test names, tooling and developer diagnostics must be English. Translated player-facing values belong in separate locale resources. Preserve Unicode coverage in test data.
- Update the affected documentation and changelog in the same change as code. Clearly distinguish implemented behavior, offline checks, live observations and planned features.
- Keep native ownership, eligibility and placement rules intact. Do not generate or unlock pets, lower gameplay limits, alter progression or write game save files.
- Keep the exact executable guard and use verified native mappings. A new game build is not supported until its mapping and behavior have been checked.
- Do not modify an installed runtime while NMS is running. Do not kill NMS or close/terminate its pyMHF host. Before a new live trial, preserve current progress and verify a fresh backup as needed.
- Source tests and packaging must not launch, attach to or modify the game. Packaging must not deploy implicitly.
- Keep personal saves, accounts, credentials, settings, logs, raw game disassembly and copyrighted game binaries out of Git and release ZIPs.
- The public target is an easy portable installation, native-looking feedback, safe X-menu settings and verified language coverage. The current candidate does not yet implement all of these; do not claim otherwise.
- Inspect Git status before editing and preserve unrelated changes. Remote creation, pushes and public publishing are separate from local version control; use the user's actual authorization and never guess the destination account.

The current user-facing documentation includes English and Czech guides. The English-source rule does not prohibit translated documentation or locale data.
