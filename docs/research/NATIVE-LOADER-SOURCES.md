# Native loader source review

Reviewed 28 September 2026. This is a source and artifact provenance review,
not a working NMS integration or a distribution approval. No upstream binary
was invoked, installed into the game, uploaded, or submitted to an antivirus
vendor. Existing game files and the working Python installation were untouched.

## Candidate and recommendation

Use **ThirteenAG's Ultimate ASI Loader (UAL)** as the first external-loader
candidate for a later controlled prototype. Prefer its documented plugin ABI
over writing a new system-DLL proxy. This recommendation is conditional on a
current-game import inventory, a coexistence check, and a startup test. It does
not establish that UAL works with our current NMS executable.

- Upstream: <https://github.com/ThirteenAG/Ultimate-ASI-Loader>
- Reviewed release: [v9.7.4](https://github.com/ThirteenAG/Ultimate-ASI-Loader/releases/tag/v9.7.4),
  published 16 August 2026, 12:01:51 UTC.
- Resolved tag commit: `6b440669144c4a0bef5718ab155df160d231cd42`.
- Root license: [MIT, copyright 2023 ThirteenAG](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/6b440669144c4a0bef5718ab155df160d231cd42/license).
  Preserve the copyright and permission notice when distributing it. The root
  license does not replace notices for included third-party components.
- [Upstream installation and supported proxy names](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/6b440669144c4a0bef5718ab155df160d231cd42/readme.md)
  include x64 `version.dll`, `winmm.dll`, `winhttp.dll`, and `xinput9_1_0.dll`.
  A supported name is not evidence that a specific NMS build imports it.

Our initial owned test harness should load only our inert prototype library
and call its exports. Loading UAL would also exercise UAL's own IAT hooks and
optional file-loading behavior; that is a separate integration step.

### Current executable's static import check

A later read-only check verified the installed executable SHA-256 matches
`compatibility.json` (`b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`).
Its import table directly includes `WINMM.dll` (`timeBeginPeriod`,
`timeEndPeriod`) and `XINPUT9_1_0.dll` (`XInputSetState`, `XInputGetState`).
No direct `version.dll` import appeared. This supports investigating `winmm.dll`
as a documented loader proxy candidate instead of assuming `version.dll` works.
The inspected game directory had none of the six checked proxy names:
version, winmm, dinput8, xinput9_1_0, d3d11 and dxgi. This local observation is
not a general coexistence guarantee and must be rechecked before any installation.
No proxy was installed and no game-loading behavior was exercised.

## Retained upstream artifact

The release API and downloaded archive agree on the following identity:

| Field | Observed value |
| --- | --- |
| Asset | `Ultimate-ASI-Loader_x64.zip` |
| Archive bytes | `2762703` |
| Archive SHA-256 | `8272d83b2692662098746f2d0ad0e2d85f3c8358ab1d63f75fbe835c2c8135fd` |
| Archive contents | One file, `dinput8.dll` |
| DLL bytes | `3615928` |
| DLL SHA-256 | `fa266e3513d02c08a1b808f28c10538a489eaffaa4b0707f7cc1066e71b5afd7` |
| DLL signer subject | `CN=FusionFix` |
| Timestamp signer | DigiCert SHA256 RSA4096 Timestamp Responder 2025 1 |
| Local Authenticode result | `UnknownError`; certificate chain ended at an untrusted root |

Sources: [release metadata API](https://api.github.com/repos/ThirteenAG/Ultimate-ASI-Loader/releases/tags/v9.7.4),
[exact archive](https://github.com/ThirteenAG/Ultimate-ASI-Loader/releases/download/v9.7.4/Ultimate-ASI-Loader_x64.zip).
The archive was downloaded and its one DLL extracted only into this chat's
`work/native-loader-research` directory for static identity/signature checks.
No certificate was installed or trust setting changed. The signature is not
claimed to be trusted on this computer, nor to establish antivirus acceptance.

The publisher also offers a NoPDB x64 archive, described as the same kind of
release without embedded debugging symbols. It was not selected or tested here.
Do not choose binary variants by repeatedly seeking a lower detection count.
Record the actual chosen archive and DLL hashes, retain the upstream source
pin, and extract distributable files instead of nesting the upstream ZIP in a
Nexus upload. This review does not establish binary/source reproducibility.

## Plugin ABI and startup context

The reviewed source's
[plugin discovery and initialization](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/6b440669144c4a0bef5718ab155df160d231cd42/source/dllmain.cpp#L851-L939)
enumerates `*.asi`, loads a matching native library, then looks up and calls
`InitializeASI` as a no-argument, void-returning function. The export must be
unmangled; an appropriate x64 declaration is:

```cpp
extern "C" __declspec(dllexport) void InitializeASI();
```

Our own `DllMain` should remain minimal. Initialization must be idempotent,
catch its own failures, and refuse native game access until the exact executable
guard and necessary lifecycle checks pass. Plugin initialization is executed
synchronously on the calling thread. It is not a documented NMS main-thread or
game-ready callback.

UAL's [default configuration](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/6b440669144c4a0bef5718ab155df160d231cd42/data/scripts/global.ini)
sets `DontLoadFromDllMain=1`. Its
[initialization implementation](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/6b440669144c4a0bef5718ab155df160d231cd42/source/dllmain.cpp#L5191-L5291)
still performs its own setup/IAT patching from UAL's `DllMain`, then normally
defers plugin discovery until a hooked host API call. `LoadFromAPI` can narrow
the trigger. Neither setting proves that every calling path is outside another
DLL's loader-lock context or that NMS has initialized its game objects. Turning
`DontLoadFromDllMain` off would allow plugin discovery directly during UAL's
DLL attach and is not a suitable workaround for this project.

Microsoft's [DLL best practices](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices)
explain the loader-lock restriction and recommend deferring substantial
initialization. Do not put game discovery, settings parsing, UI, hook setup,
thread waiting, or game calls into our `DllMain`. Do not copy upstream demo
plugins' MessageBox or CreateThread-in-DllMain examples as our lifecycle design.

## Layout and exports

A conventional candidate layout, subject to later validation, is:

```text
Binaries/
  <verified supported proxy name>.dll
  scripts/
    CompanionAutoSummon.asi
```

`.asi` is UAL's documented native-plugin convention. It is not a disguised
archive and does not make the DLL exempt from scanning. `.mods` is not UAL's
default search directory and is not established here as a built-in NMS native
module interface. Do not infer another mod's loader ABI from its folder names.

UAL searches its own directory, `scripts`, `plugins`, and active overload
directories, with configurable subdirectory discovery. Prefer normal `.asi`
discovery: the separate `LoadExtraPlugins` route in the reviewed source calls
`LoadLib` but does **not** call the `InitializeASI` export afterwards. An inert
DllMain plugin placed only on that route would therefore remain inert.

The [x64 version export definition](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/6b440669144c4a0bef5718ab155df160d231cd42/source/x64.def#L341-L359)
provides these 17 `version.dll` exports:

```text
GetFileVersionInfoA       GetFileVersionInfoByHandle
GetFileVersionInfoExA     GetFileVersionInfoExW
GetFileVersionInfoSizeA   GetFileVersionInfoSizeExA
GetFileVersionInfoSizeExW GetFileVersionInfoSizeW
GetFileVersionInfoW       VerFindFileA
VerFindFileW             VerInstallFileA
VerInstallFileW          VerLanguageNameA
VerLanguageNameW         VerQueryValueA
VerQueryValueW
```

Source forwarding chooses a local `versionHooked.dll` if present, otherwise
the system-directory `version.dll`. This is an upstream proxy-chain facility,
not permission to overwrite or rename another installed mod. Any proxy choice
must be supported by the current NMS executable/dependency imports and checked
against all existing files; Vulkan rendering does not by itself establish a
load path for Direct3D proxy names.

## Coexistence and release gates

1. Inventory existing local proxy DLLs and loader configuration before any
   installation. Reuse an identified compatible loader where possible. Refuse
   an unknown conflicting file; never silently overwrite or rename it.
2. Avoid installing multiple independent loaders that each discover the same
   plugin. UAL has its own process IAT-hook mutex and module-load checks, but
   these do not prove compatibility with other loaders or renamed module copies.
   Our initialization must independently be idempotent.
3. Preserve existing configuration. A new global `version.ini` or `global.ini`
   could affect unrelated plugins. Do not enable crash-dump or file-overload
   features for this mod. Upstream's default `update` directory handling can
   become active if such a directory already exists.
4. Confirm current NMS import/load timing and normal Steam launch in a separate
   bounded test. Then validate exact-version refusal, automation/menu parity,
   save backups, manual dismissal/OFF, settings/localization, and multiplayer.
5. Inspect and document the actual released binary, compile provenance and all
   notices. Replacing Python with native code does not imply zero antivirus
   detections, Nexus acceptance, or compatibility with another NMS build.

## Included license notices to collect before bundling

The [x64 build definition](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/6b440669144c4a0bef5718ab155df160d231cd42/premake5.lua#L242-L277)
includes more than the root project. At minimum review and retain:

- UAL's MIT notice linked above.
- The [injector source notice](https://github.com/ThirteenAG/injector/blob/3a384e8d1b575c09383b0fab8bd92e34cb654949/LICENSE),
  a zlib-style license, for the pinned injector submodule and its utilities.
- [MinHook's complete BSD-style notice, including HDE portions](https://github.com/TsudaKageyu/minhook/blob/d94c64d32ea37bc4f5ee47d580709f70c6fb6080/LICENSE.txt).
  That is the MinHook commit pinned by the reviewed injector submodule. Its
  license explicitly requires the notice/disclaimer in binary distributions.
- [miniz's embedded notices](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/6b440669144c4a0bef5718ab155df160d231cd42/external/miniz/miniz.c),
  including MIT notices for RAD Game Tools/Valve and Rich Geldreich/Tenacious
  Software, and the public-domain/unlicense portion. Do not rely only on the
  shorter public-domain summary at the top of `miniz.h`.

The downloaded upstream ZIP contains only the DLL, so required accompanying
notices must be assembled explicitly before redistribution. No proprietary
Planetary Surveyor source, asset, or binary was copied or used in this review.
