# Companion Auto Summon for No Man's Sky - by Lineum Dynamics

Status as of 28 September 2026. Working plan; neither the mod nor its page has been publicly published. The canonical source project is in a private GitHub repository; this file is maintained in `docs/release/`. References below to documents under `CompanionAutoSummon/` mean documents at the root of the repository and distribution package.

The owner-created Nexus account is `LineumDynamics`; its authentic company
avatar is saved and visually checked. A real No Man's Sky draft now exists in
category **Creatures**, mod ID **4579**, with visible status **Unpublished**:
[draft page](https://www.nexusmods.com/nomanssky/mods/4579) and
[general editor](https://www.nexusmods.com/games/nomanssky/mods/4579/edit/general).
The exact Nexus page title is **Companion Auto Summon for No Man's Sky - by
Lineum Dynamics**, with author field **Lineum Dynamics**. The General section
is saved and marked **Section complete**: version `0.8.7-play-trial`, language
**English**, and tags **AI-Generated Content**, **AI Media** and **Quality of
Life**. The **1600 × 900** gallery cover and company avatar remain unchanged.
The corrected **1300 × 372** [header](https://staticdelivery.nexusmods.com/mods/1634/images/headers/4579_1790592385.jpg)
is uploaded and visually verified on the actual mod page: a dark decorative
background without embedded text, a company mark or white elements, with a
subdued paw on the right. Nexus supplies the full approved title, which is
legible in the checked screenshot. Media is **Section complete**; the page
still shows **Unpublished** and a **Files missing** banner.
No code ZIP has been uploaded,
and files and permissions remain pending. The earlier disabled `Upload mod` button and
`Something went wrong. Please try again.` error are historical; creation is no
longer blocked. Public release still requires the acceptance work below and
the owner's release decision.

The immutable **0.4.9-experimental / 0.8.7-play-trial**, with menu
**0.8.5-branding**, is currently running from the final `087-r1` directory.
Prepared **0.8.6-r1** remains untouched and unlaunched. The full title and author
credit are used in presentation outside the game; the short in-game title
remains Companion Auto Summon. After normal closure of the previous game and
a fresh verified 46-file backup, both Mods and twelve targets loaded on
28 September 2026 at 11:07:26 (Europe/Prague). The player confirmed a visible
Random pet in the Nexus after loading and leaving the ship. Later, after a
requested manual dismissal, the player reported that the pet apparently did
not reappear; the exact waiting duration was not independently measured.
After startup, all 40 payloads, settings and remembered state matched.
Different pets were involved, so this does not establish the cause or a fix for
the [0.8.4 failure](../research/LIVE-084.md). Bounded language observation
recorded English; it does not validate translations or safe language switching.
Details are in the [0.8.7 record](../research/LIVE-087.md). Complete menu,
notice, remapping, localization and public portable-launcher acceptance remains
pending. The player also confirmed one native OFF/ON test: an exit with OFF did
not summon, ON alone did not summon, and the next exit did. The log agrees and
other preferences stayed unchanged. This does not verify the other five
controls, held input, remapping or controllers. Monetization is summarized in
the [current rules review](MONETIZATION.md).

All 14 catalogs have 41 keys. Two new keys preserve the full title as a proper
name and translate the author-credit phrase; three launcher compatibility
messages now use the full title. Native captions and in-game notices are
unchanged. Thirteen translations still await language review; an in-game
author credit has not been implemented.

Localized text composition is now prepared outside the game package: all 1,666
language/state combinations fit within existing limits without truncation.
Actual rendering and automatic language selection are not yet verified.
A real console-free pyMHF import check also passed, including reproduction of
the original failure and its resolution by a prototype. The current launcher
does not yet use it; portable installation is not thereby complete. Details:
[localization](../research/NATIVE-LOCALIZATION-AUDIT.md) and
[portable runtime](../research/PORTABLE-RUNTIME-AUDIT.md).

## Next combined test 0.8.7

The initial load and exit in 0.8.7 have confirmed visible results; broader
repeatability and Last selected mode do not. Continue the missing checks in
the running session without changing its files or host. Diagnostics do not
change summoning rules or themselves fix the earlier failure.

The final directory is `build/quick-menu-play-trial-087-r1`, with 41 files
(40 payloads and a manifest). Original output `087` remains retained,
unlaunched and superseded by the correction of two Korean particles in the
localization. Source validation passed 333 production and 675 developer tests
without failures or skips. Outside the game, the actual-framework check
verified nine callbacks per Mod across twelve targets and all six temporary
preferences; Python and Windows PowerShell 5.1 read-only preflights also passed.
After the language correction, 24 localization tests, the framework check and
both preflights passed again for final r1.

1. After loading in an enabled location, wait approximately 20 seconds without
   changing settings, opening a pet preview or summoning manually. Record the
   actual visible pet or its absence and the complete bounded diagnostic trace.
2. Then compare an ordinary ship exit in the same session. Random can select a
   different pet; that result cannot distinguish a loading-related cause from
   differences between pets. If a controlled comparison is needed, use the same
   manually selected pet in Last selected mode for the next natural load and
   exit. Do not automatically repeat an accepted request or mistake manual
   dismissal for a failure.
3. After the initial observation, combine testing of the six controls, Back,
   reopening, ordinary manual summoning and dismissal with checks of notice
   readability and icons. Verify that unrelated preferences survive; restore
   the player's preferences at the end. Mark remapping and controllers verified
   only after an actual test.
4. Selecting the Companion Auto Summon entry also performs bounded diagnostic
   language reads. Do not change the game language during the first trial.
   Text remains English; this version does not enable translations. On error,
   reading stops itself without disabling the menu or automation.

The basic observations above have already taken place; remaining controls and
appearance can be checked in the current session. New deployment or a
controlled startup repeat requires normal closure and relaunch. The portable
installer can continue to be prepared outside the running environment. The
pyMHF panel is removed only after all native controls pass acceptance. None of
these steps establishes public readiness, multiplayer support or correctness
of translations that have not yet been tested.

The following 0.4.4 / 0.7.1 and 0.7.0 results are historical records; their
next steps at the time do not describe the currently running version.

## Historical preparation and test 0.4.4 / 0.7.1

The candidate being prepared then was 0.4.4 in the separate 0.7.1 package. It
adds only passive observation after request acceptance. It does not retry a
summon or change delays or preferences. After a new backup, both Mods and 11
hook targets loaded on 27 September 2026 at 22:22:35 with automation ON;
the visible result was pending. Basic toggling in the preceding 0.7.0 had
partial confirmation, but a pet did not appear after loading in the Anomaly
despite request acceptance. Diagnostics were intended to establish what
happened next. The white circle beside the notice remained a separate visual
defect. The older 0.4.3 results below do not transfer to the new candidate.
Public release remained premature.

One Random summon after loading in the Anomaly is confirmed for 0.4.4 / 0.7.1. On 27 September 2026, the log recorded load arming at 22:23:39.698, queue acceptance at 22:23:42.250 (a reported 2.56 seconds) and the expected active pet at 22:23:42.266 on the first diagnostic update. The player confirmed actual appearance. No ship exit or repeated summon preceded it. This is one successful run; it does not fix the earlier intermittent failure because the change was diagnostic only.

## Prepared native-settings test 0.7.0

The separate 0.7.0-play-trial package contains unchanged production 0.4.3 and
the first native automatic-summoning ON/OFF control. It passed 408 developer
tests, the real pyMHF check outside the game and queueing/application of a
temporary preference change. The package has 15 files, two Mods and 15 callbacks
across 11 targets. After game closure and a fresh verified 43-file backup,
both Mods and 11 hook targets registered on 27 September 2026 at 21:48:38 with
automation ON. Full in-game toggle verification remained pending; the 0.6.2
observations below do not validate the new menu.

The next test in the game running at that time: navigation alone must not
change state; a separate confirmation should toggle OFF/ON, and holding it
should act only once. Check Back, reopening, item order, preservation of other
preferences and manual pet summoning. This check does not need another
restart. Activation paths without verified native confirmation do not toggle
anything; remapping and controllers need separate testing. Other settings
still use the temporary pyMHF panel. Once the complete native menu is finished
and verified, remove that panel from the player interface while preserving
saved preferences and the background framework runtime.

## First-release scope

Windows x64, Steam NMS build 25442159 / Cosmos 7.04, the exact supported NMS.exe fingerprint, pyMHF 0.2.4 and Python 3.11–3.13 x64. Other stores and operating systems are not prerequisites for the first release. Label the first public release a beta with specific verification limits.

First-release features: automatically summon an owned pet after ship exit or successful local save loading; Last manually selected or Random; optional home-biome preference in Random; location controls; preserved settings; waiting for a suitable place. Candidate 0.4.3 adds one deferred opportunity after loading: an appropriate local-player callback handles it with the same delay and native checks as ship exit. No native summon is called during deserialization. Manual dismissal does not trigger repeated automatic summoning. Do not add further features before completing validation. Native game restrictions, ownership and placement remain authoritative.

Owner requirement: installation must be as simple and reliable as possible. The target workflow is **extract a ZIP and launch one application**, with its own tested environment and no manual Python, pip commands or system changes. This distribution launcher has not yet been created; source candidate 0.4.9 and combined test package 0.8.7 are development variants. Specific requirements are in `INSTALLATION-REQUIREMENTS.md`.

Work order: prepare portable packaging alongside the next combined 0.8.7 test described above. Historical confirmation of station startup and a separate manual dismissal belongs to 0.4.3 / 0.6.2; it does not replace validation of the new candidate. Second-PC testing must use the final player package.

Other confirmed requirements: all source code, comments and docstrings in English; user translations separate. There are 14 catalogs of 41 keys and nine translated launcher compatibility messages. The native menu and HUD do not yet use translations; static UTF-8 evidence does not validate actual fonts, rendering or safe language switching. The authoritative status and requirements are in `CompanionAutoSummon/LOCALIZATION.md`; ongoing documentation rules are in `CompanionAutoSummon/DEVELOPMENT.md`.

The user also requires natural integration with the original game interface: unobtrusive in-game confirmations and X-menu settings. The direction is recorded in `CompanionAutoSummon/DESIGN.md`. The combined candidate contains six actual settings on a shared native subpage and distinct role icons. The temporary pyMHF panel remains a development fallback until native controls pass acceptance. Lifetime, shortcuts, remapping, controllers and complete visual behavior still require validation against the final package.

## Documented baseline

- Status as of 27 September 2026: production candidate 0.4.3 passed 230 offline tests, including 140 runtime tests; the developer suite passed 341 tests. The actual production GUI check and pyMHF combined-folder 0.6.2 check passed outside the game, without hook registration. Original `NMS-AutoPet` paths for personal data and the development environment are preserved.
- The subsequent 0.4.3 / 0.6.2 live run, after a fresh 43-file backup, registered two modules and ten native hook targets at 20:42:21 with automation enabled. At 20:42:58.578 the log recorded an opportunity after local save loading, location 2 (station), then Random slot 1 from five eligible pets at 20:43:01.260 and native queue acceptance at 20:43:01.261. Approximately 2.69 seconds elapsed from arming to acceptance; this does not measure visible spawn time. No ship-exit opportunity preceded it. The player confirmed the pet actually appeared after loading and clarified that the location was a station, not the Nexus. The documented scope is one station startup summon in Random.
- Later in the same unchanged 0.4.3 / 0.6.2 session, the player confirmed one manual dismissal and no reappearance during observation. The exact location, dismissal time and observation duration were not independently established; the dismissed pet also cannot be linked to the earlier startup summon. This is a separate player confirmation, not a dismissal test at a station or immediately after loading.
- Earlier that day, production 0.4.2 registered successfully in combined run 0.6.1. The log recorded an accepted station summon request; the player did not confirm visible appearance. This establishes registration and the request, not actual appearance or the new 0.4.3 behavior.
- Historical state before that run: 0.4.2 passed 212 offline tests and an eight-widget check in actual pyMHF 0.2.4 / Dear PyGui 2.3.1. Older AutoPet 0.4.1 passed 211 offline tests and widget checks; its biome preference had not been tested in-game. Deployment of 0.4.1 is a historical record, not a description of the currently running package.
- Older 0.4.0 verified one Random choice and actual summon on a planet. Older 0.3.3 verified a station and restoration of the manual choice after restart. Do not describe these results, retained before the 0.6.1 trial on 27 September 2026, as in-game validation of 0.4.3.
- A historical 43-file profile backup preceded deployment of 0.4.1; a separate fresh 43-file backup preceded the 0.4.3 / 0.6.2 run. Before another deployment, reassess backup freshness against new gameplay progress.
- The historical 0.4.1 Git package contained 21 files. The exact file lists and checksums for candidate 0.4.3 and combined 0.6.2 must match their own manifests; saves, user settings, runtime, game binaries and personal logs must not be included in the development ZIP.

## 1. In-game test of 0.4.3 in combined candidate 0.6.2

Keep a concise record of the version, situation, player's observation and corresponding log. A logged accepted request does not itself establish that a pet actually appeared.

Confirmed in this candidate: one Random station load with a visible pet and a separate manual dismissal without return during the player's observation. Planet and Nexus loading, Last manually selected startup, broader dismissal regression and the remaining table scenarios are not thereby verified.

| Test | Expected result |
|---|---|
| Local save load in an allowed place without ship exit | One deferred opportunity uses existing settings, the same delay and native checks; at most one eligible owned pet |
| Another ordinary exit on a planet | The existing ship-exit summon path remains functional |
| Manual dismissal after completion of the load request | No repeated summon without a new event |
| Pet already active on load, or an inappropriate/network load | No duplicate or foreign automatic summon |
| Known eligible pet with the same biome and preference enabled | Selection comes from matching eligible pets; establish the actual home biome rather than relying on appearance |
| No eligible biome match | Ordinary Random selection occurs |
| Biome preference OFF | Ordinary Random selection; a single exit may not establish the distribution |
| Return to Last manually selected | Use the original manual favourite, not the last Random choice |
| Automation or a specific location disabled | Neither load nor the next exit starts a forbidden automatic summon; an already summoned pet is not forcibly dismissed |
| Normal closure and restart through Companion Auto Summon | Settings and manual favourite survive |
| Station and Nexus | Summoning depends on the game's original checks; biome must not affect selection |
| Unsuitable place, wait over 20 seconds, move to suitable terrain | The same exit completes only at an allowed place, without entering the ship again |
| Ship entry or manual choice while waiting | The old request is cancelled |
| Freighter / natively unsupported location | No summon bypassing game rules |

The user currently has no suitable archive location for testing. This is not a failure; test when an opportunity becomes available or with a tester. Until then, do not call deferred summoning verified in-game. Check HUD and panel during these trials rather than scheduling a separate long test session.

## 2. Second player and multiplayer

First try a clean installation of the distribution package on a second Windows computer with the same supported EXE, its own account and its own save. Check the instructions, Steam detection, environment setup and launch. A new installation must not include someone else's preselected pet.

Then run a short shared in-game test: one player with Companion Auto Summon and the second initially without it; collect both players' observations, ordinary exit, manual dismissal and ship re-entry. If possible, repeat with two mod instances. Verify pet visibility, no duplicates and no changes to another player's pet or manual choices. Do not promise universal compatibility with all mods or long-term stability based on one session.

If no tester is available, a limited public beta clearly marking multiplayer unverified can be prepared later. The recommended first release nevertheless includes this test because multiplayer is the project owner's main way of playing.

## 3. Completing the distribution package

- Implement the localization system, complete translations and verify their meaning and rendering according to `LOCALIZATION.md`. Translated files alone do not establish correct translation or rendering.
- Verify the persistence-failure notice in the final UI. The source now distinguishes `Companion saved.` from `Companion selected (session only).`, addressing the old `manual favorite saved` wording defect. The failure-path rendering still needs live validation; do not reintroduce a success claim when persistence fails.
- Fix any defects and rerun affected checks. Any native-address or gameplay change requires an appropriate new in-game test; do not transfer successful results automatically to new code.
- Prepare a public launcher with a bundled standalone Python environment and pinned dependency versions. The goal is ZIP extraction and one click without downloading dependencies at use time. This is not a copy of the development venv; portability, DLL loading and licences for all bundled components need validation. Nexus approval of such packaging cannot be assumed. Manual Python installation is only the current development workflow, not the target player installation.
- Use the approved full title and **by Lineum Dynamics** credit. Complete dependency credits and the owner's licence / modification and redistribution permissions decision; branding alone does not determine a licence or legal ownership. A separate LICENSE file is a suitable way to express this, not described here as a universally mandatory Nexus format. Dependencies have their own licences; do not automatically apply ours to them.
- Shorten the player guide. During the move to Git, broken links into the private test directory were already replaced with names of externally retained records; [TECHNICAL-VERIFICATION.md](../../TECHNICAL-VERIFICATION.md) preserves result summaries. Do not package private backups or logs.
- Update the version, manifest and only results actually supported by evidence; extract the ZIP again and compare it with the manifest.
- Prepare short installation, update, normal-launch and complete-disable instructions. State that this is not a file to place in GAMEDATA/MODS.

## 4. Nexus page

Approved external title: **Companion Auto Summon for No Man's Sky**, with **by Lineum Dynamics**. For the Nexus Mod Name field, use the complete combined title **Companion Auto Summon for No Man's Sky - by Lineum Dynamics**; retain **Lineum Dynamics** in the author field. The site rejects a typographic dash in Mod Name, so that field uses an ASCII hyphen; gallery titles and graphics may retain a typographic dash or separate credit. The short in-game name remains **Companion Auto Summon**. Repository slug: `nms-companion-auto-summon`. The English draft is in the adjacent `NEXUS-DESCRIPTION-DRAFT.md`. Before publication, adapt the installation section to the final package and update the testing status.

Add a real settings screenshot and a demonstration of leaving the ship / the pet arriving. Images must not imply features that do not exist. Prepare requirements, supported build, limitations and concise release notes.

Nexus publication and monetization rules, checked on 28 September 2026:

- Use **AI-Generated Content** for predominantly AI-generated code, UI and translations; AI-generated public descriptions or promotional media also fall under **AI Media**. **AI Assisted** alone requires limited AI involvement and evidence of human creation and expertise; it is not a suitable substitute for the current CAS scope.
- Network downloads have a limited exception for necessary functionality. The rules do not automatically approve our launcher.
- Complete reuse permissions and credit the sources / authors used.

Source: [File Submission Guidelines](https://help.nexusmods.com/article/28-file-submission-guidelines), updated 4 September 2026.

The owner's objective is maximum revenue within the rules, not a predetermined limit to unobtrusive promotion. Nexus allows combining conditional Donation Points, PayPal and external donation links. The current [DP rules](https://help.nexusmods.com/article/68-donation-points-system-terms-of-service) do not contain a blanket AI exclusion; eligibility depends on content rights and Nexus's decision. Do not promise earnings.

[Donation Options & Guidelines](https://help.nexusmods.com/article/77-donation-options-guidelines) permit links on Nexus pages; that does not approve a financial element inside the game or launcher. No exact reminder frequency or donation-banner size is specified. The 100 px limit concerns links to separately approved paid content, not donations generally. Interpretation of the [Hello Games EULA](https://www.nomanssky.com/end-user-licence-agreement/) for local financial UI remains unresolved. The [review](MONETIZATION.md) retains unsent working questions; the owner explicitly prohibited contacting either organization. Use published rules only.

The current proposal combines an activation notice with neutral information
about where optional donations can be made. It is recorded in the review;
frequency and destination are not decided. Combining the texts does not create
an exception to the rules. This is not an implemented notice or confirmed
permission for that form. Introducing actual text must include the matching
English entry and every affected translation in the same change.

## 5. Publication

The author account is identified as `LineumDynamics`, and unpublished draft 4579 exists. Before publication, the working file for the stated support scope, final description and permissions must be complete. Only then publish and inspect the public page and downloaded ZIP. Neither draft creation nor the current plan establishes Nexus approval of the final package.

Further checks can be added when opportunities arise: planet and Nexus loading, Last manually selected startup, the existing ship-exit path and coexistence with the inert menu subpage. Immediate game closure is not required to continue work; the running candidate stays unchanged. Verifying biome preference itself requires knowing the available pets' home biomes. One confirmed dismissal does not replace broader regression checks.
