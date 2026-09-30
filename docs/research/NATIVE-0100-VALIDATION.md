# Native 0.10.0 test checkpoint

Recorded on 28 September 2026. Product: **Companion Auto Summon for No Man's
Sky - by Lineum Dynamics**, version **0.10.0-native-test**.

The native candidate has passed offline validation, been installed after a
verified closed-game backup, and initialized during a normal Steam game start.
Its own live log records a verified pre-activation snapshot, twelve active
gameplay/menu hooks plus the binding guard, a successful local save load, and
two accepted native summon requests. The player separately confirmed visible
pet appearance after leaving the ship. Appearance after the initial load is
**uncertain**: the player first reported that no pet appeared, then immediately
clarified that it may have been overlooked. This is not an established startup
regression. Correct menu rendering/controls, normal restart, second-PC use and
multiplayer remain unverified. The exact native ZIP has since passed through
Nexus's owner download route, with its downloaded bytes and hash verified.

## Frozen artifact

| Item | Identity |
| --- | --- |
| Source/build checkpoint | `build/native-runtime-0100-r3` |
| Player ZIP | `CompanionAutoSummon-0.10.0-native-test.zip` |
| ZIP bytes / members | 3,725,420 / 30 |
| ZIP SHA-256 | `e00a8818230dba24066fcdc4d75a01d696c9e2573d2538aa6a9b05c5dd14bebb` |
| Native module | `CompanionAutoSummon.asi`, 2,633,216 bytes |
| Native module SHA-256 | `3840c8f8e0dd1405b05c35dcc859f766fd36fcb7c1bade3e07ab2e7ddc5d8373` |
| Official loader | Ultimate ASI Loader 9.7.4 x64, 3,615,928 bytes |
| Loader SHA-256 | `fa266e3513d02c08a1b808f28c10538a489eaffaa4b0707f7cc1066e71b5afd7` |
| Packaged manifest SHA-256 | `cffa6c6af2596bdd56ff737bf13f6aeace7b0f74abd6f4a39bd0d18cfa1b0b18` |
| Build receipt SHA-256 | `dcbf9be46ad24fc8be631cf49532a44a55432f9f3ca7a4ac8cd067806ba44506` |
| Game target | Windows x64 Steam Cosmos 7.04, build 25442159 |
| Game executable SHA-256 | `b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb` |

The game overlay is two native binaries and eight original DDS icons. The
remaining ZIP members are English/Czech player guides, seventeen third-party
notices and the manifest. It contains no developer executables, Python runtime,
save files, private preferences, logs or nested archives. The loader bytes are
the unchanged upstream `dinput8.dll` release artifact installed under the
supported `winmm.dll` proxy name. ASI is the loader's native DLL convention;
it does not exempt either executable image from antivirus or Nexus checks.

Packaging required a successful validation receipt bound to this exact build
receipt, matching component reports, current source hashes, the exact official
loader, all eight reviewed icon hashes and the locked notice identities. Every
ZIP member was read back and compared, with manifest hashes and CRCs checked.
`package-receipt.json` retains `live_verified`, `deployed` and `uploaded` as
false because it records the pre-deployment packaging event. Those immutable
fields are not rewritten to describe the later live session.

## Offline validation for r3

| Check | Recorded result and boundary |
| --- | --- |
| Decision policy parity | 88 traces / 31,216 commands against maintained Python policy |
| Habitat/rotation parity | 59 traces / 25,733 commands against maintained Python selector |
| Settings/favorites parity | 333 cases / 721 operations; exact resulting bytes and invalid-file preservation |
| Runtime integration fixture | 59 cases through real Runtime/policy/selection/storage with owned synthetic memory and native-service doubles |
| Backup fixture | 16 checks; explicit caller-owned fixture paths only |
| Actual native module in owned hosts | Six runs, eight concurrent initialization calls per run; unsupported host refused and gameplay hooks remained inactive |
| Authored hook/ABI fixture | Ten checks across ten authored targets, including argument/result forwarding, mixed float/stack arguments, shared trigger order, reentry, activation gating and batch enable/disable; original bytes restored |
| Retained Python source regression | 403 production and 786 developer tests passed; these are additional source regression evidence, not native live acceptance |

The hook fixture does not prove every NMS ABI or game callback lifecycle. The
runtime fixture checks startup and exit opportunities, long terrain waits,
location restrictions, pending OFF controls, identity-safe selection, confirmed
manual UI attribution, per-save favorite isolation, accepted-only rotation,
clock reversal, callback reentry and concurrent callback refusal. Cosmetic HUD
read/delivery failures disable notifications alone; settings and summoning
continue. Invalid manual-action capture stops learning favorites alone.

Storage matches schemas 1–4 and their defaults/migrations. One intentional
strict boundary remains: escaped lone Unicode surrogate save keys are rejected
without overwriting, although Python's JSON parser accepts them. Actual runtime
save keys are ASCII identities. Valid Unicode scalar keys and Unicode paths
were tested. Persistence remains a single-writer design.

The detailed reports are retained under the r3 build directory as
`build-receipt.json`, `validation-receipt.json`, the five component validation
reports and `package-receipt.json`. The source and third-party inventory is
recorded in `native/dependencies-lock.json`. Private machine paths in raw local
receipts are deliberately not reproduced here or packaged for players.

## Deployment and first native execution

The retained private deployment receipt records game closure before and after
staging, a newly verified closed-game backup, creation of the module and loader,
and hash-matching reuse of the eight icons. Deployment itself did not start the
game. The game was subsequently started through Steam, using the native path.
The earlier Python distribution artifacts were retained.

The following sanitized events were read from this session's native log:

| UTC, 28 September 2026 | Observed event |
| --- | --- |
| 16:04:10.317 | Actual game executable verified; no native gameplay hooks active yet |
| 16:04:10.403 | Private pre-activation snapshot verified |
| 16:04:10.636 | Twelve native hooks and binding guard active; menu/automation initialized |
| 16:05:11.945 | Successful local save load recorded; waiting for readiness |
| 16:05:30.074 | Automatic summon opportunity armed |
| 16:05:32.660 | Native summon queue accepted |
| 16:05:55.204 | Another automatic summon opportunity armed |
| 16:05:56.761 | Native summon queue accepted |

The two accepted queues are not evidence of two rendered companions. The player
confirmed one visible pet after ship exit; immediate post-load appearance is
unresolved after the player's correction noted above. Do not mark it failed or
claim complete startup appearance acceptance. The initializer's snapshot was taken while the game was
already running, before enabling this mod's gameplay hooks. It is separate
from the earlier closed-game deployment backup. Neither path restores or writes
original game saves.

## Player-facing contract and remaining checks

Installation merges the packaged `Binaries` and `GAMEDATA` folders into the
Steam game root while NMS is closed. A different existing `winmm.dll` must never
be overwritten. Start normally through Steam; do not run the earlier Python
launcher concurrently. Settings and favorites retain their existing external
mod-owned directory. Use the packaged English/Czech READMEs for installation
and selective removal; do not delete shared loader files used by other mods.

The Quick Menu uses native actions and the game's configured input binding
(X is only the default PC binding). In-game text is currently English. Fourteen
catalogs exist, with translated startup errors using the Windows language and
English fallback; complete native in-game localization is not established.
Fresh defaults are By habitat with Shuffle ON. Existing preferences are
preserved. Habitat groups use relative weights **13:5:1**. The native rewrite
does not introduce teleport/base-removal triggers, automatic respawning after
manual dismissal, lower game limits or relaxed native summon eligibility.

Still required: a controlled repeat of post-load appearance and ship-exit
repeatability; correct menu order, icons, captions and persistent controls;
normal exit and subsequent Steam restart; a second Windows/Steam installation
and a two-player session. The native download result below does not extend
the gameplay acceptance boundary.

## Nexus file 49202 and verified owner download

The exact frozen ZIP was uploaded to the existing Unpublished
[mod 4579](https://www.nexusmods.com/nomanssky/mods/4579?tab=files) as a **new
Miscellaneous file 49202**, version **0.10.0-native-test**. Mod-manager download
is OFF and it is not marked primary. Files 49195, 49196 and 49197 remain
retained; none was replaced or deleted. The saved page version and complete
native description were read back through Credits. The approved full title
and byline, unchanged summary and existing AI tags were preserved.

The new file displayed the site's individual safe/tick indicator. Its linked
[VirusTotal report for the exact ZIP](https://www.virustotal.com/gui/file/e00a8818230dba24066fcdc4d75a01d696c9e2573d2538aa6a9b05c5dd14bebb/detection)
reported **0/68**, analyzed at **2026-09-28 16:15:13 UTC** (18:15:13 GMT+0200 in
the displayed report). This is a bounded scan observation, not a guarantee
that the file is harmless or a result for every later build.

An actual **Manual download → Slow download** using the owner account
completed. The downloaded file was independently checked: **3,725,420 bytes**,
SHA-256 **`e00a8818230dba24066fcdc4d75a01d696c9e2573d2538aa6a9b05c5dd14bebb`**,
matching the original package. This establishes that the owner can retrieve
this exact native candidate from Nexus. It does not mean the second tester
has received, installed or run it.

The overall mod page still displays **Some suspicious files** alongside the
retained older uploads. Do not describe the entire page as clean or the older
quarantine as lifted. The download template displayed an archived-version
notice even though the new file was listed as Miscellaneous; the category was
not changed to Archived and the successful download was hash-verified. The
older Python quarantine/scan records remain attached to their original hashes.
At the following checkpoint, the owner explicitly authorized public alpha
publication. Mod 4579 was published on 28 September 2026 at 18:43 CEST. File
49202 is Main / Primary with mod-manager downloads OFF. Files 49195, 49196 and
49197 were archived rather than deleted. The public page reads **Safe to use**,
shows the native version and provides a Manual download. This is a current
page-level readback, not a warranty or a false-positive determination for any
older file. The frozen package/validation receipts remain unchanged; the later
publication and owner-download evidence is recorded separately.

Public GitHub source and the matching prerelease remain pending verification.
