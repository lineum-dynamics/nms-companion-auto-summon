"""Host-only pyMHF launcher with verified remote DLL addresses.

Importing this module does not import pyMHF, inspect processes or inject code.
The PowerShell launcher remains responsible for package/game/runtime checks.
"""

import argparse
from functools import wraps
import os
import sys


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


def install_injection_guard(process_api=None):
    """Wrap pymem's DLL loader before pyMHF constructs any pyRunner.

    Optional process_api permits offline tests with an entirely fake API.
    The original loader still performs LoadLibraryW; only its unchecked local
    address is replaced with a verified address from the target module list.
    """
    if process_api is None:
        import pymem.process as process_api
    original = process_api.inject_dll_from_path
    if getattr(original, "_companion_auto_summon_injection_guard", False) is True:
        return original

    @wraps(original)
    def guarded_inject(handle, filepath):
        physical_path = _canonical_path(filepath)
        original(handle, physical_path)
        try:
            modules = process_api.enum_process_module(handle)
            return validate_remote_module(modules, physical_path)
        except InjectionGuardError:
            raise
        except Exception as exc:
            raise InjectionGuardError("Could not verify the injected target DLL.") from exc

    guarded_inject._companion_auto_summon_injection_guard = True
    process_api.inject_dll_from_path = guarded_inject
    return guarded_inject


def main(argv=None):
    parser = argparse.ArgumentParser(description="Start verified Companion Auto Summon through pyMHF.")
    parser.add_argument("mod_path", help="Absolute path to CompanionAutoSummon.py")
    args = parser.parse_args(argv)
    if not os.path.isabs(args.mod_path):
        parser.error("CompanionAutoSummon.py must be supplied as an absolute path.")
    mod_path = os.path.realpath(args.mod_path, strict=True)
    if os.path.basename(mod_path) != "CompanionAutoSummon.py" or not os.path.isfile(mod_path):
        parser.error("Expected an existing CompanionAutoSummon.py file.")

    install_injection_guard()
    # Import after installing the guard, then use pyMHF's public console entry
    # point. Running the canonical venv Python avoids stale .exe entrypoint paths.
    import pymhf
    previous_argv = sys.argv
    try:
        sys.argv = ["pymhf", "run", mod_path]
        return pymhf.run()
    finally:
        sys.argv = previous_argv


if __name__ == "__main__":
    main()
