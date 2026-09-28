# Portable runtime and noninteractive host preparation

Recorded 28 September 2026 against the installed pyMHF 0.2.4 development
environment. This is offline preparation, not a portable player package or a
game-launch test. Running 0.8.4, prepared 0.8.5, host configuration, compatibility
guards and player preferences are unchanged.

## Implemented host import prototype

An ordinary pyMHF import in a Windows `CREATE_NO_WINDOW` child with closed input
and piped output failed with `prompt_toolkit.output.win32.NoConsoleScreenBufferError`.
The framework creates questionary prompts during import, even when the caller
does not intend to use its interactive CLI.

`tools/pymhf_host_import.py` narrowly wraps that import in the public
`prompt_toolkit.application.create_app_session` with `DummyInput` and
`DummyOutput`, restoring context on exit or exception. It requires pyMHF 0.2.4.
It does not call `run_module`, select a game, enumerate processes, load mods,
change environment bypass flags or weaken a compatibility check. It is not
imported by the current launchers.

`tools/noninteractive_framework_smoke.py` accepts an explicit existing framework
interpreter and runs the ordinary and adapted imports in separate isolated
`-I -B` children. Each child has a 15-second execution timeout and each output
stream an 8,192-byte cap; timeout cleanup only targets that test-owned child.
The checker requires the precise negative-control error and an adapted success,
matching framework sources and environment, no test bypasses and empty stderr.
An optional report is created exclusively and omits local paths.

The real comparison passed with **Python 3.11.9 x64, pyMHF 0.2.4 and
prompt_toolkit 3.0.53**. Ordinary import reproduced the expected failure;
adapted import succeeded. Seven focused unit tests cover dummy-session lifetime,
version refusal, exceptions, environment handling, bounded output and comparison
failures. The retained private report includes source hashes; it is not a release
payload. This proves the host import only, not the separate injected interpreter
or game lifecycle.

## Three separate integration requirements

1. **Hide the settings panel after native menu acceptance.** Installed
   `pymhf/injected.py` creates its GUI only when `gui.shown` is true (line 355),
   while the main loop continues independently (line 375). Current exact-config
   guards deliberately expect `shown=true`. A separate validated candidate must
   change that contract consistently; do not edit live configuration.
2. **Run without a console.** The host prototype resolves the reproduced import
   failure, but `_preinject.py` imports pyMHF again inside the target process.
   Native `pyrun_injected` initializes Python before applying the injected Python
   `sys.path` string. Standard-library discovery, target-side imports and the
   actual game start remain independent checks.
3. **Keep the host alive independently of a launcher window.** Installed
   `pymhf/main.py` terminates the target and host when its injected worker exits
   (lines 409–420). Closing a future graphical launch window must not terminate
   the runtime host. Do not test this by closing the player's current host.

## Portable dependency boundary

The current project supports Python 3.11–3.13 x64, narrower than the framework's
metadata. The observed environment uses CPython 3.11.9 and cp311 Windows x64
native wheels. Its `pyvenv.cfg` references an external Python installation;
copying that venv does not create a portable runtime.

The [official embeddable Python distribution](https://docs.python.org/3.11/using/windows.html#the-embeddable-package)
is designed for application distribution without pip or Tcl/Tk. It is a
candidate base, not proof of pyMHF compatibility. Pin the complete dependency
closure and package hashes before assembling a separate offline runtime.

The installed `pywin32.pth` adds `win32`, `win32/lib` and `pythonwin` and imports
`pywin32_bootstrap`, which adds `pywin32_system32` to DLL search paths. An embedded
configuration must deliberately support that trusted bootstrap or equivalent
explicit paths. Merely copying site-packages is insufficient.

`pymhf/injected.py` attempts DearPyGui import before checking `gui.shown` (lines
129–133), catching `ModuleNotFoundError`. A present package with a missing native
DLL may fail differently even with the panel hidden. DearPyGui is an optional
framework dependency, so removing `[gui]` is a possible later reduction after
native-menu acceptance and an import-closure audit, not a change made here.

Observed native dependencies include VCRUNTIME140, VCRUNTIME140_1 and, for
DearPyGui, MSVCP140 and DirectX components. Preserve dependency license notices
and use an authorized redistributable source for Microsoft files; system-folder
copies do not establish distribution rights. See
[Microsoft's redistribution guidance](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files?view=msvc-170).

The next installer candidate must retain selected-executable and actual-target
checks, package hashes, duplicate-host leases and existing preference paths.
Then verify relocation/non-ASCII paths, a clean Windows account without external
Python, no installation-time downloads, native-menu operation and ordinary game
exit. The current import success completes none of those installation checks.

## Portable assembly and owned native-child proof, 28 September 2026

This appendix supersedes the earlier preparation status only within its stated
offline scope. Work is isolated on `feat/portable-multiplayer-trial`. The running
`090-r2` game and host were not accessed or modified by this runtime work.

`tools/build_portable_runtime.py` assembles a fresh directory from the official
[CPython 3.11.9 embeddable package](https://www.python.org/downloads/release/python-3119/)
and twenty pinned PyPI wheels. Original HTTPS locations, versions, sizes and
SHA256 values are in `tools/portable_runtime_lock.json`. The Python archive hash
is `009d6bf7e3b2ddca3d784fa09f90fe54336d5b60f0e0f305c37f400bf83cfd3b`.
Both probes verify the complete metadata dependency closure of
`pymhf[gui]==0.2.4`, including `pymem[speed]`, against the bundled versions.
No venv, installed package files, system DLLs or global installation is copied.

The builder checks locked downloads and every wheel's complete RECORD hash/size
set, refuses archive traversal and Windows path aliases, and retains packaged
license notices. It never executes installers or postinstall scripts.
`runtime-manifest.json` records every generated payload file and origin;
`THIRD-PARTY-NOTICES.json` maps all 21 artifacts to preserved license files and
hashes. Vendor wheel bytes remain unchanged. Python's `_pth` is deliberately
replaced by owned relative-path configuration, retaining its original hash.
The runtime contains no pip or automatic updater.

The integration layout is `runtime/python.exe`, `runtime/pythonw.exe`, the
Python DLL/stdlib ZIP, `runtime/Lib/site-packages` and owned
`runtime/sitecustomize.py`. The launcher separately ships
`tools/portable_host_support.py` as `app/portable_host_support.py`.
`verify_runtime(runtime)` checks the runtime manifest, versions and required
native imports. `prepare_host(runtime)` additionally installs the bounded
adapters below. Preparation itself starts no game, enumerates no processes and
performs no injection or hook installation.

### Initialization and Unicode paths

Pinned [pyrun-injected 0.2.0](https://pypi.org/project/pyrun-injected/0.2.0/)
initializes Python with `PyConfig_InitPythonConfig`, `program_name='run_data'`
and `Py_InitializeFromConfig` before executing transferred strings. Its native
file records pass UTF-8 bytes to narrow `fopen_s`. A real owned-child negative
control reproduced failure for a CJK filename. The owned adapter's Python
Unicode open/compile record succeeds, preserving `__file__`, shared globals and
the script encoding cookie. The existing guarded DLL `LoadLibraryW` path stays
unchanged.

Automatic `import site` is omitted from `_pth`. An earlier trial passed imports
but created bytecode for `pywin32_bootstrap` and `sitecustomize` before the latter
could disable writes. The final run-data adapter instead prepends an owned
string that disables bytecode, imports the owned bootstrap and checks its
completion marker, before pyMHF's transferred paths and `_preinject.py`. The
host initializes the bootstrap explicitly. Relative Win32 search paths and
explicit DLL directories replace automatic vendor `.pth` processing. The
bootstrap retains a public prompt_toolkit DummyInput/DummyOutput session, with
no test environment bypass or changed vendor source.

`tools/audit_portable_runtime.py` relocates a copy under accented/CJK directories
and compiles `tools/portable_runtime_probe.cs` with the existing Windows C#
compiler. That owned child locally loads the real Python and pyrun DLLs and
calls exported `run_data`; it never opens another process or injects anything.
Children have a 30-second timeout and 16,384-byte limit per output stream.
Timeout cleanup targets only the owned child. PATH contains only System32;
PYTHONHOME/PYTHONPATH are poisoned and data paths are temporary/private.

The retained `build/portable-runtime-3119-r3/runtime` contains **1,195 files /
54,496,853 bytes**. Its manifest SHA256 is
`17b0d82d939443f1810caa1a83003140fae0c0f1e9139319f6060da951eddf3a`.
`work/portable-runtime-audit-r4/report.json` records passing console-free host
and fresh native-interpreter probes: Python 3.11.9 x64, pyMHF 0.2.4, twenty
dependencies and 528 imported module origins within the relocated runtime.
Both runtime copies remained byte-for-byte unchanged, without new bytecode.
This verifies DLL-adjacent stdlib discovery and the Unicode record adapter.
The final host probe calls `prepare_host` and confirms both startup wrappers are
installed without invoking them; the report pins the tested helper source hash.
It does not verify NMS injection, game lifecycle, multiplayer, another computer
or a clean Windows installation without current system prerequisites.

### Bounded startup and native prerequisites

The owned host adapter replaces only the reviewed framework Steam branch:
`steam://rungameid/275850`, `NMS.exe`, empty required assemblies and
`start_paused=false`. It requires one running Steam process, waits up to 120
seconds with 0.1-second sleeps and opens the matched Steam-child PID directly.
Missing, ambiguous and timed-out targets fail explicitly. Runner construction
still passes through the existing actual-handle compatibility/injection guard;
its refusal is not swallowed or retried. The adapter never terminates a process.
These discovery/URI/runner tests are mocked, not real Steam launches.

A separate narrow wrapper rejects a silent `run_module` return before any new
`run_data` entry. It preserves an ordinary post-entry return and propagates
exceptions. Entry means initialization was attempted; it is not proof that the
target completed initialization or that a mod works inside the game.

The static inventory has **94 native files**. Required DearPyGui imports
`MSVCP140.dll`, absent from the locked artifacts. Official embedded Python ships
`VCRUNTIME140.dll` and `VCRUNTIME140_1.dll`. Unused optional pywin32 MAPI modules
also import MSVCP140, and its PythonWin IDE modules import MFC140U; these optional
modules are outside the verified imported closure.
`tools/audit_portable_dependencies.py` reproduces all PE import tables without
loading the examined files. Its retained r3 report is
`work/portable-runtime-audit-r3/native-dependencies.json`.

The helper checks x64 system MSVCP140 and raises the maintained
`portable.native_runtime_missing` key if unavailable. No system DLL or Microsoft
redistributable is copied, downloaded or installed. The result is a portable
Python/framework bundle with a Microsoft Visual C++ prerequisite, not a wholly
self-contained OS runtime. The separate launcher owns the translated notice.

The focused archive/host-support suites passed **25 tests**, covering integrity
and refusal, Unicode file semantics, strict/idempotent adapters, bounded mocked
Steam discovery and pre-start versus post-entry returns. Neither these tests nor
the native-child proof establishes the known native-menu lifecycle fix, final
launcher UI acceptance, successful NMS startup/exit or multiplayer compatibility.
