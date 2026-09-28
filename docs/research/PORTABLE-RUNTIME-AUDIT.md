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
