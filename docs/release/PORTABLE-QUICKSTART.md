# Companion Auto Summon for No Man's Sky — by Lineum Dynamics

## Private tester quick start: 0.9.3-test

This guide describes the portable test candidate. Its launch flow, recovery and
multiplayer behavior still need testing on real PCs. It is not a stable release.

You need Windows 10/11 x64 with its .NET Framework 4 support, the
Microsoft Visual C++ v14 x64 runtime, and the Steam edition of No Man's Sky, **Cosmos 7.04 /
Steam build 25442159**. The launcher checks the exact game executable; another
store or game update is not supported by this test package. Python 3.11.9 is
included, so you do not install Python or run pip.

After Nexus makes the file available, the owner downloads the exact
**0.9.3-test ZIP** from the unpublished page and passes that unchanged ZIP to
the other tester. The page stays private. A quarantined file is not cleared
for tester distribution; do not disable antivirus protections to use it.

## Install and start

1. Quit No Man's Sky normally and let it finish closing.
2. Extract the entire supplied ZIP into a new folder. Keep its files together;
   do not copy them into the game's MODS folder or overwrite an older test copy.
3. Double-click **Companion Auto Summon.exe** in the extracted folder.
4. Click **Check installation**. If the game was not found, use **Choose game
   folder** to select your Steam installation of No Man's Sky, then check again.
   If the check refuses the game or reports a missing requirement, keep that
   message for the owner; do not bypass the check.
5. Open Steam and sign in before clicking **Start game**. **Check installation**
   can run while Steam is closed. Before every normal start, the launcher makes a new
   private backup and verifies it against the source before and after copying.
   A failed backup prevents the modded start.
6. For this first test, keep the launcher open until you quit the game normally.
   Do not end its background processes. Closing the launcher is designed to
   leave the session running, but that behavior still needs a live check.

Your backups are in `%LOCALAPPDATA%\NMS-AutoPet\backups\`, each in its own folder.
Settings and remembered companion choices keep their existing location under
`%LOCALAPPDATA%\NMS-AutoPet\`. Verified mod files are copied into a private
`sessions` folder there; launcher/host logs use the adjacent `logs` folder, and
framework files stay in the session. Playing should leave the
extracted distribution unchanged. Do not delete a session folder while playing.

## First in-game check

1. Load a save in which you already own a companion. Use a planet, space station
   or the Space Anomaly where the game normally permits that companion.
2. Load on foot with no pet already present and wait about 20 seconds. Record
   whether a pet actually appears. If you load inside your ship, step out and
   test that event instead; these are two separate checks.
3. Open **Quick Menu → Companions → Companion Auto Summon**. The default PC key
   is **X**; use your assigned Quick Menu key if you changed it. There are seven
   settings. A changed value should be named in the confirmation message.
4. Dismiss the pet manually. It should stay dismissed until another ship exit
   or successful local save load. Then enter and exit the ship and check again.

Fresh settings use **By habitat** with **Shuffle companions ON**. Existing
settings are preserved. By habitat can deliberately skip an unsuitable owned
roster. For a simple first comparison, choose **Random** and an enabled location;
changing a setting itself does not summon a pet. Last selected needs a successful
manual choice first. An already active companion is not replaced.

## Known limits and recovery

- The custom settings menu can stop after a callback thread changes. Menu
  **0.9.1-diagnostics** records more detail but does not fix that known problem.
  Report when the menu stopped and what you were doing; do not assume teleporting
  caused it. Production summoning is separate from the menu.
- Teleport arrival and base removal are not automatic-summon triggers. Pet
  disappearance alone does not trigger a replacement, preserving manual dismissal.
- Native menu and HUD text are English. Other language catalogs are drafts.
- Portable launching, all settings, save/restart behavior and multiplayer are
  not yet fully verified. An accepted request in a log is not a visible pet.

If **Check installation** reports the missing Microsoft Visual C++ runtime,
install Microsoft's [Visual C++ v14 x64 package](https://aka.ms/vc14/vc_redist.x64.exe)
once, then check again. See [Microsoft's runtime instructions](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist).
The launcher explains a missing requirement and does not download it automatically.

To play without the mod, quit NMS normally and then start it through Steam.
Keep your backups and original ZIP. For a failed start, send the exact error and
the relevant session log to the owner; do not share your save or backup folder.
Record the ZIP version, Windows/Steam game version and whether you actually saw
the pet. Follow **Multiplayer test.txt** in this ZIP only after each
player's basic solo checks succeed.
