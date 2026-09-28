# Companion Auto Summon for No Man's Sky — by Lineum Dynamics

## Private two-player test: 0.9.2-test

This is a proposed acceptance test, not a claim of multiplayer compatibility.
Both players use Windows 10/11 x64 and Steam, with Windows .NET Framework 4
support and the Microsoft Visual C++ v14 x64 runtime. Exact game versions and
requirements still need the launcher check on each PC; the quick start covers
the one-time Microsoft runtime installation if it is missing.

Use the **same exact ZIP** and supported game, **Cosmos 7.04 / Steam build
25442159**, on both PCs. The owner downloads the exact tester ZIP from the
unpublished Nexus page and passes that unchanged ZIP to the other player. The
page stays private. Each person
keeps their own save, pets, settings and automatic backups. No save sharing.

## Prepare separately

1. Follow **README.txt**, or its Czech translation **README.cs.txt**, in the ZIP.
   Each player opens Steam, signs into their own account and checks their
   installation, then starts through **Companion Auto Summon.exe**. Every normal
   start makes and verifies a new private backup before starting the mod.
2. Use a save with an owned pet and a supported location where manual summoning
   works. For the first comparison, set **Selection: Random**, automatic
   summoning ON and the test location ON. Record Shuffle and biome-preference
   values; changing settings does not itself summon a pet.
3. Each player checks a real ship exit with no pet already active. Confirm an
   owned pet visibly appears, dismiss it, and wait about 20 seconds without a
   new trigger. It should stay dismissed. Report failures before testing together.
4. Separately check a normal save load on foot in an enabled location. If this
   requires restarting, quit normally and start through the launcher again;
   a fresh backup is automatic. Record actual appearance, not only a log result.

Keep the launcher open during this first test and do not end its background
processes. Closing its window is designed to leave the session running, but
that still needs live acceptance. The menu can stop under its known thread
guard; 0.9.1-diagnostics adds evidence, not a fix. If controls stop responding,
record the action/time and mark dependent checks blocked instead of guessing
whether a setting changed.

## Meet and compare

Meet normally in the same multiplayer session, at the same supported location.
Stay close enough to see each other. Use easily distinguishable owned pets
when available; do not adopt, abandon, edit or transfer pets just for this test.

| Check | Action | Record separately on both PCs |
|---|---|---|
| A's automatic pet | B waits without a ship exit or save load. A exits their ship with no active pet. | Did A see their owned pet? Did B see that same pet? Did B's own pet/state stay unchanged? |
| B's automatic pet | A waits. B performs the same ship-exit check. | Did B see their owned pet? Did A see it? Did A's own pet/state stay unchanged? |
| Both active | Keep each player's automatically summoned pet present. | Are both pets visible to both players, with no duplicate or unexpected replacement? |
| Manual dismissal | A dismisses their pet and waits without another trigger. Repeat for B. | Did each dismissal remain effective locally and appear correctly to the other player? |
| B's automation OFF | B confirms Automatic summoning OFF, then manually summons a pet. A performs an enabled ship exit. | Did B's manual pet remain unchanged while A's automation worked? B then dismisses it and exits their own ship: no automatic pet should appear. |
| A's automation OFF | Swap the previous roles. | Does the same independence hold for A's manual pet and B's automation? |
| Both OFF | Both confirm OFF, then manually summon and dismiss their own pets. | Do ordinary pet controls work, with no automatic replacement? |

An already active pet is not replaced by a ship exit. Remote-player loading
must not create a new opportunity for the other player's mod. Teleport arrival
and base removal are not automatic triggers; do not count missing arrival
summons as failures of those nonexistent features. Pet disappearance by itself
must not cause automatic respawning.

This two-mod test does not prove compatibility with unmodified players, other
mods, every location or public multiplayer. A later mixed test can cover one
player starting normally through Steam and the other using this exact package.

## Finish and report

Quit both games normally. To play without the mod, start NMS through Steam.
Keep each person's backups under `%LOCALAPPDATA%\NMS-AutoPet\backups\` private.
Launcher/host logs are under `%LOCALAPPDATA%\NMS-AutoPet\logs\`; framework
session files are under the adjacent `sessions` folder.
Do not delete active session files or terminate a running host to reset a test.

Report the ZIP version, each game's launcher-check result, settings, location
and approximate times. For each row distinguish **A saw**, **B saw**, **not
observed** and **blocked**. Include the relevant session logs when needed, not
saves or backup folders. One successful meeting is bounded evidence; record
repeatability, restart persistence and any menu stop as separate findings.
