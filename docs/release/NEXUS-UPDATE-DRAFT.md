# Nexus update draft — teleport research follow-up

Status: **draft only; do not publish as a feature update yet.** Updated 1 October 2026.

## Current public-build wording

The current 0.10.1-native-test release still creates automatic-summon opportunities after successful local save loading and ship exit only. Teleport arrival and death/respawn do not currently create automatic summon requests.

Static analysis of the exact Cosmos 7.05 executable has now narrowed the teleport search to native teleporter state references. This is investigative progress only: no successful local teleporter-completion callback has been verified, so the public build and Nexus file 49367 remain unchanged.

## Replacement FAQ text for the current Nexus description

**Does it summon after teleporting, dying or deleting a base?**

This build creates automatic opportunities after a successful local save load or ship exit only. Teleport arrival and death/respawn do not currently trigger a request; base removal does not create one either. Manual dismissal or a missing pet does not automatically trigger a respawn. Static analysis is being used to locate a trustworthy local teleport-completion event, but no such callback has been verified yet.

## Text for the next release, only after the trigger is actually implemented

**Teleport arrival:** The new **Summon after teleport** option creates one automatic opportunity after a successful local teleport for the local player. It still uses the game's normal companion ownership, eligibility and placement checks. It never forces a summon in a location where normal manual summoning is unavailable.

Fresh profiles enable the option by default. On upgrade, it is enabled only when the preference is absent; an existing player choice is preserved.

## Release-note boundary

Do not say that teleport summoning is fixed, implemented, working or available in Nexus file 49367 until a separately versioned candidate has:

- a verified exact-build local completion callback,
- offline safety/transaction tests,
- live confirmation of a completed teleport followed by one eligible summon opportunity,
- negative coverage for non-local/network and incomplete-teleport paths,
- matching English and translated player-facing catalog entries, and
- a new packaged archive with its own identity and verification evidence.

The detailed static XREF record is in [NMS-075-STATIC-XREFS](../research/NMS-075-STATIC-XREFS.md). It is developer research, not player-facing installation evidence.
