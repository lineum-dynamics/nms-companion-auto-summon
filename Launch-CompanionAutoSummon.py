"""Host-only pyMHF launcher with verified remote DLL addresses.

Importing this module does not import pyMHF, inspect processes or inject code.
Both launch entries preflight compatibility; the final DLL guard verifies the
actual target handle before each injection.
"""

import argparse
from contextlib import contextmanager
from functools import wraps
import os
import sys
import hashlib
import json
from pathlib import Path
import re
import tomllib
from types import SimpleNamespace
_support_directory = str(Path(__file__).absolute().parent)
if _support_directory not in sys.path:
    sys.path.insert(0, _support_directory)
import cas_compatibility as compatibility


LAUNCHER_MUTEX_NAME = r"Local\CompanionAutoSummon.Host.v1"
_ERROR_ALREADY_EXISTS = 183
EXPECTED_FRAMEWORK_CONFIG = {
    "exe": "NMS.exe", "steam_gameid": 275850, "start_paused": False, "interactive_console": False,
    "logging": {"shown": False, "log_dir": "{CURR_DIR}", "log_level": "info"},
    "gui": {"shown": True, "always_on_top": False},
}


class LauncherSessionError(RuntimeError):
    """A host session could not obtain or release its exclusive launch lease."""


def _launcher_mutex_api():
    """Bind Windows APIs lazily, only when a host actually starts."""
    if os.name != "nt":
        raise LauncherSessionError("Companion Auto Summon requires Windows.")
    import ctypes as C
    kernel = C.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateMutexW
    create.argtypes = [C.c_void_p, C.c_int, C.c_wchar_p]
    create.restype = C.c_void_p
    close = kernel.CloseHandle
    close.argtypes = [C.c_void_p]
    close.restype = C.c_int
    return SimpleNamespace(CreateMutexW=create, CloseHandle=close,
                           set_last_error=C.set_last_error, get_last_error=C.get_last_error)


@contextmanager
def launcher_session(api=None):
    """Hold one per-Windows-session host lease across all package locations.

    The named mutex is an existence lease, not a thread-owned mutex: no Wait or
    ReleaseMutex is used. A second open is refused immediately. Closing the
    last handle, including process termination, removes the kernel object; no
    stale lock file or abandoned thread ownership needs repair. The PowerShell
    setup lease uses a different name so its child can acquire this host lease.
    Optional api permits entirely fake offline checks without calling Windows.
    """
    handle = None
    try:
        try:
            if api is None:
                api = _launcher_mutex_api()
            api.set_last_error(0)
            candidate = api.CreateMutexW(None, False, LAUNCHER_MUTEX_NAME)
            if type(candidate) is not int or not 0 < candidate < (1 << 64):
                raise LauncherSessionError("Could not obtain the Companion Auto Summon host lease.")
            handle = candidate
            error = api.get_last_error()
            if error == _ERROR_ALREADY_EXISTS:
                raise LauncherSessionError("Companion Auto Summon is already starting or running. Use its existing host window.")
            if type(error) is not int or error != 0:
                raise LauncherSessionError("Could not verify the Companion Auto Summon host lease.")
        except LauncherSessionError:
            raise
        except Exception:
            raise LauncherSessionError("The Windows host-lease check failed; no mod was started.") from None
        yield
    finally:
        if handle is not None:
            try:
                if not api.CloseHandle(handle):
                    raise LauncherSessionError("Could not release the Companion Auto Summon host lease.")
            except LauncherSessionError:
                raise
            except Exception:
                raise LauncherSessionError("The Windows host-lease cleanup failed.") from None


class InjectionGuardError(RuntimeError):
    """A loaded DLL could not be identified safely in the target process."""


def _canonical_path(path):
    if not isinstance(path, str) or not path or not os.path.isabs(path):
        raise InjectionGuardError("Expected a nonempty absolute DLL path.")
    try:
        # Resolve Windows package filesystem aliases before passing a path to
        # a game launched outside the package's filesystem view.
        return os.path.normcase(os.path.realpath(path, strict=True))
    except (OSError, ValueError) as exc:
        raise InjectionGuardError(f"Cannot resolve DLL path: {path!r}") from exc


def validate_remote_module(modules, dll_path):
    """Return one full-path-matched remote DLL base, or fail closed.

    pymem MODULEINFO.filename supplies the target module's complete filename;
    lpBaseOfDll is a Python int read from its c_void_p field. Do not trust the
    local GetModuleHandle result returned by pymem's injection helper.
    """
    expected = _canonical_path(dll_path)
    matches = []
    try:
        for module in modules:
            if _canonical_path(module.filename) == expected:
                matches.append(module.lpBaseOfDll)
    except InjectionGuardError:
        raise
    except Exception as exc:
        raise InjectionGuardError("Could not enumerate target DLL paths safely.") from exc
    if len(matches) != 1:
        raise InjectionGuardError(
            f"Expected exactly one loaded target DLL at {expected!r}; found {len(matches)}."
        )
    base = matches[0]
    # This launcher is for x64 Windows. DLL image bases are allocation-granularity
    # aligned user addresses; reject null, truncated-looking low values and junk.
    if type(base) is not int or not 0x10000 <= base < (1 << 47) or base % 0x10000:
        raise InjectionGuardError(f"Invalid remote DLL base for {expected!r}: {base!r}")
    return base


def install_injection_guard(process_api=None, *, expected_executable=None, target_validator=None):
    """Wrap pymem's DLL loader before pyMHF constructs any pyRunner.

    Optional process_api and target_validator permit entirely fake offline tests.
    The original loader still performs LoadLibraryW; only its unchecked local
    address is replaced with a verified address from the target module list.
    """
    if process_api is None:
        import pymem.process as process_api
    original = process_api.inject_dll_from_path
    if getattr(original, "_companion_auto_summon_injection_guard", False) is True:
        if getattr(original, "_cas_expected_executable", None) != expected_executable:
            raise compatibility.CompatibilityError("launcher.game_changed")
        return original

    @wraps(original)
    def guarded_inject(handle, filepath):
        physical_path = _canonical_path(filepath)
        # This is the actual target handle, not a PID/name or configured path.
        # Validate on both DLL calls; never cache authority by a reused handle.
        if target_validator is None:
            compatibility.verify_target(handle, expected_executable=expected_executable)
        else:
            target_validator(handle)
        original(handle, physical_path)
        try:
            modules = process_api.enum_process_module(handle)
            return validate_remote_module(modules, physical_path)
        except InjectionGuardError:
            raise
        except Exception as exc:
            raise InjectionGuardError("Could not verify the injected target DLL.") from exc

    guarded_inject._companion_auto_summon_injection_guard = True
    guarded_inject._cas_expected_executable = expected_executable
    process_api.inject_dll_from_path = guarded_inject
    return guarded_inject


def validate_standalone_package(mod_path):
    """Refuse inconsistent siblings or changed launch configuration before pyMHF."""
    try:
        folder = Path(__file__).resolve().parent
        mod = Path(mod_path).resolve(strict=True)
        if mod != folder / "CompanionAutoSummon.py":
            raise ValueError("Foreign mod path")
        manifest_path = folder / "manifest.json"
        if manifest_path.stat().st_size > 1_000_000:
            raise ValueError("Oversized manifest")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        profile = json.loads((folder / "compatibility.json").read_text(encoding="utf-8"))
        if (profile != compatibility.PROFILE
                or manifest.get("supported_nms_exe_sha256") != compatibility.SUPPORTED_GAME_SHA256
                or manifest.get("steam_build") != compatibility.STEAM_BUILD
                or manifest.get("framework") != f"pymhf[gui]=={compatibility.FRAMEWORK_VERSION}"):
            raise ValueError("Mismatched profile")
        entries = manifest.get("files")
        if type(entries) is not list or not 1 <= len(entries) <= 256:
            raise ValueError("Invalid file inventory")
        for name in ("CompanionAutoSummon.py", "Launch-CompanionAutoSummon.py", "cas_compatibility.py", "compatibility.json"):
            records = [entry for entry in entries if type(entry) is dict and entry.get("path") == name]
            path = folder / name
            if (len(records) != 1 or path.resolve(strict=True) != path or path.stat().st_size > 4_000_000
                    or hashlib.sha256(path.read_bytes()).hexdigest() != records[0].get("sha256")):
                raise ValueError("Unverified package member")
        source = mod.read_text(encoding="utf-8")
        match = re.match(r"# /// script\r?\n(.*?)# ///\r?\n", source, re.S)
        if match is None or any(not line.startswith("#") for line in match[1].splitlines()):
            raise ValueError("Missing script configuration")
        document = tomllib.loads("\n".join(line[2:] if line.startswith("# ") else line[1:]
                                          for line in match[1].splitlines()))
        config = document["tool"]["pymhf"]
        if (config != EXPECTED_FRAMEWORK_CONFIG or type(config.get("steam_gameid")) is not int
                or config.get("start_paused") is not False or config.get("interactive_console") is not False
                or set(document) != {"requires-python", "dependencies", "tool"}
                or set(document["tool"]) != {"pymhf"}
                or document.get("requires-python") != ">=3.11,<3.14"
                or document.get("dependencies") != [f"pymhf[gui]=={compatibility.FRAMEWORK_VERSION}"]):
            raise ValueError("Unsafe launch configuration")
        return mod
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        raise compatibility.CompatibilityError("launcher.invalid_package") from None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Start verified Companion Auto Summon through pyMHF.")
    parser.add_argument("mod_path", help="Absolute path to CompanionAutoSummon.py")
    parser.add_argument("--game-directory", help="Absolute Steam game installation directory")
    parser.add_argument("--language", help="Launcher language; defaults to the Windows UI language")
    parser.add_argument("--no-dialog", action="store_true", help="Write failure text without a modal dialog")
    parser.add_argument("--check-only", action="store_true", help="Check prerequisites without starting a host or game")
    args = parser.parse_args(argv)
    if not os.path.isabs(args.mod_path):
        parser.error("CompanionAutoSummon.py must be supplied as an absolute path.")
    try:
        mod_path = os.path.realpath(args.mod_path, strict=True)
    except (OSError, ValueError):
        compatibility.show_failure(compatibility.CompatibilityError("launcher.invalid_package"),
                                   language=args.language, show_dialog=not (args.no_dialog or args.check_only))
        return 1
    if os.path.basename(mod_path) != "CompanionAutoSummon.py" or not os.path.isfile(mod_path):
        parser.error("Expected an existing CompanionAutoSummon.py file.")

    try:
        validate_standalone_package(mod_path)
        verified_executable = compatibility.verify_game_directory(args.game_directory)
        compatibility.verify_framework()
        if args.check_only:
            print(compatibility.warning_text("launcher.preflight_passed", args.language))
            return 0
        with launcher_session():
            if not compatibility.game_closed():
                raise compatibility.CompatibilityError("launcher.game_running")
            install_injection_guard(expected_executable=verified_executable)
            # Import only after preflight. The guard also verifies the actual
            # process before either DLL can be loaded by the framework.
            import pymhf
            previous_argv = sys.argv
            try:
                sys.argv = ["pymhf", "run", mod_path]
                return pymhf.run()
            finally:
                sys.argv = previous_argv
    except compatibility.CompatibilityError as error:
        compatibility.show_failure(error, language=args.language,
                                   show_dialog=not (args.no_dialog or args.check_only))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
