# Nexus update draft — 0.10.2 multiplayer test

Status: **published on Nexus on 3 October 2026** as the ordinary successor to
0.10.1, not a separate multiplayer edition. The new file is **49469**
(Main / Primary), version 0.10.2-native-test; 0.10.1 remains in file history.
The public summary and English description were saved and read back.

## What changed

The native runtime now includes an experimental, filtered teleport callback
candidate in addition to successful local save load and ship exit. The existing
master automation switch and destination settings still control the request.
Every summon continues through the game's native ownership, eligibility and
placement checks.

An earlier build of the same candidate behavior produced visible pets after
two local routes: freighter-to-station and station-to-planetary-base, with no
ship exit before the second. Opening and closing the teleporter without choosing
a destination did not produce the observed candidate event. These tests support
a teleport-related local trigger but do not establish its exact game meaning,
whether it denotes completed arrival, or whether it reacts to a remote player's
movement.

## Player-facing draft

**Teleport test:** This version includes an experimental teleport trigger. An
earlier build produced visible companions after two local teleport routes, but
the callback's meaning and behavior in multiplayer are unknown. Leave one
player stationary while the other teleports, then swap roles and observe both
screens. Turn **Automatic summoning** OFF in the in-game settings if the
behavior is disruptive. Please report the player who teleported, both
locations, whether a companion was already active, the selection mode, and
whether a pet visibly appeared for each player.

This trigger remains controlled by the existing master automation and
destination settings. It does not bypass the game's summon checks. Death and
respawn remain separate and are not automatic triggers in this version.

## Release wording boundary

Do not describe teleport summoning as a verified local-arrival fix, multiplayer
safe, or stable. The exact 0.10.2 package has passed offline checks and ZIP
readback but has not been started in NMS. Remote-player behavior, second-PC
installation and visible appearance from this exact archive remain unverified.
Nexus links the exact local ZIP hash to a VirusTotal report with 1/67 detections
(Kaspersky `VHO:Trojan.Win32.LOADER.gen`, 66 undetected). The bundled `.asi`
module separately reports 2/71 detections (Kaspersky
`VHO:Trojan.Win32.LOADER.gen` and Microsoft `Trojan:Win32/Wacatac.C!ml`); the
bundled loader reports 0/71. The Nexus page-level label says Safe to use, but
these results do not establish that the files are harmless or that detections
are false. Nexus download bytes have not been read back.
The detailed candidate map and local evidence
are in [TELEPORT-AND-GROUPED-MENU](../research/TELEPORT-AND-GROUPED-MENU.md),
[Known Issues](../KNOWN-ISSUES.md) and the
[release test checklist](0.10.2-MULTIPLAYER-TEST.md).
