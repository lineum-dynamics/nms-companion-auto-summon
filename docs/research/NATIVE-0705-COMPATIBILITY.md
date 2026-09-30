# Cosmos 7.05 compatibility investigation

Status: opened 30 September 2026. No 7.05 executable profile has been verified,
and the published native alpha does not support 7.05 yet.

## Release facts

Hello Games published Cosmos 7.05 on 30 September 2026 and states that it is
live on Steam; updates for other platforms are pending. See the
[official 7.05 notes](https://www.nomanssky.com/2026/09/cosmos-7-05/).

## Existing native profile

The public 0.10.0-native-test package supports only:

- Windows 10/11 x64, Steam, Cosmos 7.04, build 25442159.
- Required `NMS.exe` SHA-256:
  `b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`.

The exact-file guard must continue to refuse unknown executables before hooks or
native game calls. Do not treat an updated version label or successful process
startup as proof that the 7.04 addresses still apply.

## Installed Steam snapshot

Checked after the owner reported the Steam update complete, on 30 September
2026. Steam reports the 275850 app installed (`StateFlags` 4), with all reported
downloaded and staged byte counts complete. Its manifest BuildID is `25624745`;
this is Steam depot metadata, not the game's patch number. The installed
`NMS.exe` reports file/product version `180383`, size `88,545,352` bytes, and
SHA-256:

`671de22649274b49fa07f5a246bc7252c4e08bb9ab623d2e65722fbab4e497a4`

The executable's recorded modification time is `2026-09-30T10:54:00.8767362Z`.
No NMS process was running during this read-only check. This confirms the local
Steam update completed and the executable differs from the supported 7.04
profile. It does not identify native addresses or validate any hook. The
published alpha must continue to reject this image until the evidence below is
complete.

## Required 7.05 evidence

1. After Steam finishes updating, record the actual installed executable's full
   version/build metadata and SHA-256. Never inspect or replace a file while
   Steam is still writing it.
2. For every native hook and direct memory mapping, verify the new target,
   surrounding signature, calling convention, arguments and relevant object
   offsets against the exact 7.05 executable. The current bootstrap has twelve
   game hooks plus its binding filter; a matching subset is not enough to
   enable the runtime.
3. Recheck the compatibility guard, runtime reads/writes, menu construction,
   texture lookup, warning path, backup gate, loader and hook rollback against
   the exact image. Keep game binaries and raw disassembly out of Git.
4. Add a new executable profile only after every check passes. Preserve the
   7.04 profile unless evidence shows it must be retired, and keep the 7.05
   work on this branch until the profile is verified.
5. Before any live 7.05 trial, close NMS normally, preserve and verify the
   required closed-game save backup, then build an explicit candidate. Do not
   modify the installed module while NMS is running.

Do not publish 7.05 compatibility or replace the working alpha until the
updated profile, candidate identity and validation evidence are recorded.
