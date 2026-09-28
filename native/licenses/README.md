# Native distribution third-party notices

These notices accompany the third-party components used by the native test
package. They do not grant a license to Companion Auto Summon's own source,
artwork, name or other original material. No open-source license for the mod
itself is asserted here.

## Ultimate ASI Loader

The unmodified x64 loader is Ultimate ASI Loader **v9.7.4**, from
<https://github.com/ThirteenAG/Ultimate-ASI-Loader/releases/tag/v9.7.4>, source
commit `6b440669144c4a0bef5718ab155df160d231cd42`. Its upstream `dinput8.dll`
may be named `winmm.dll` using the loader's documented proxy-name support;
the executable bytes are not modified. Include these notices with the DLL:

- `UAL-9.7.4-MIT.txt`: ThirteenAG's complete root MIT notice.
- `UAL-injector-zlib.txt`: complete injector notice from its pinned commit
  `3a384e8d1b575c09383b0fab8bd92e34cb654949`.
- `UAL-MinHook-BSD-HDE.txt`: complete MinHook/HDE notice from injector's pinned
  MinHook commit `d94c64d32ea37bc4f5ee47d580709f70c6fb6080`.
- `UAL-miniz-notices.txt`: every unique copyright/license notice block in the
  release's miniz source, including RAD Game Tools/Valve, Rich Geldreich/
  Tenacious Software, Martin Raiber, the complete Unlicense dedication, and
  Alex Evans's public-domain PNG-writer attribution. Duplicate identical
  blocks are included once. No source implementation is reproduced here.

The reviewed x64 build does not include the separate x86-only d3d8to9,
MemoryModule or minidx9 components. This notice inventory follows the pinned
x64 build inputs; it is not a claim that the upstream binary was reproducibly
rebuilt from those inputs.

## Components compiled into Companion Auto Summon

- `MinHook-1.3.4-BSD-HDE.txt`: complete MinHook v1.3.4 notice, including both
  HDE notices. The retained source files match commit
  `c3fcafdc10146beb5919319d0683e44e3c30d537`.
- `json-3.12.0-MIT.txt`: complete JSON for Modern C++ v3.12.0 notice. The
  single header matches commit `55f93686c01528224f448c19128836e7df245f72`.

## Statically linked compiler and platform runtimes

The developer compiler is LLVM-MinGW **20260922**, x86_64 UCRT distribution.
The compiler itself, developer tools and their unrelated dependencies are
not player-package payloads. Retain these runtime notices:

- `LLVM-Apache-2.0-with-exceptions.txt`, including the complete LLVM
  exceptions and legacy notice retained by the distribution.
- `libcxx-LICENSE.txt`, `libcxxabi-LICENSE.txt`, `libunwind-LICENSE.txt` and
  `compiler-rt-LICENSE.txt`, obtained from LLVM commit
  `85ac560262434c9ccfc0c183ec22d4138ed647fb` reported by the pinned compiler.
  `libcxx-CREDITS.txt` and `libcxxabi-CREDITS.txt` retain the corresponding
  upstream contributor lists referenced by their historical notices.
- `MinGW-w64-runtime-NOTICES.txt`, the complete runtime notice compilation
  shipped with the toolchain, without removing potentially unused portions.
- `MinGW-w64-general-NOTICES.txt` and `winpthreads-NOTICES.txt`, copied in full
  from the same pinned toolchain. The official build script pins MinGW-w64
  source `57b595039040eaa15bece85b7cc71d952281b269`.

The notices retain upstream wording. Their inclusion is not an endorsement,
a safety certification or evidence of Nexus approval. Exact component,
source, notice and retained upstream-binary identities are recorded in the
repository's `native/dependencies-lock.json`. The UAL archive is not nested
inside the player package; the required DLL and these notices are individual
files. No proprietary game executable or game source is included here.
