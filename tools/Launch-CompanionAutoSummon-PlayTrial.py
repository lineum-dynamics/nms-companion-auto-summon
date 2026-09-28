"""Host-only entry for one verified auto-summon and ordered-menu trial folder.

Importing performs no process access or injection. The accompanying PowerShell
launcher must establish that NMS is closed and validate its exact executable.
The original standalone bootstrap supplies the unchanged DLL injection guard.
"""

import argparse
import hashlib
from importlib import metadata, util
from pathlib import Path
import tomllib
import sys

# Source tooling lives in tools/; an exported bundle has this helper beside it.
_support_directory = Path(__file__).resolve().parent
if not (_support_directory / "cas_compatibility.py").is_file():
    _support_directory = _support_directory.parent
if str(_support_directory) not in sys.path:
    sys.path.insert(0, str(_support_directory))
import cas_compatibility as compatibility


VERSION = "0.8.6-play-trial"
HOST_NAME = "Launch-CompanionAutoSummon-PlayTrial.py"
BOOTSTRAP_NAME = "Launch-CompanionAutoSummon.py"
PAYLOAD_FILES = frozenset((
    "CompanionAutoSummon.py", "CompanionMenuOrderTrial.py",
    "quick_menu_item.py", "quick_menu_submenu.py", "quick_menu_order.py",
    "quick_menu_native_guard.py", "quick_menu_guard_runtime.py",
    "quick_menu_preferences.py", "quick_menu_toggle.py",
    "game_language.py",
    "quick_menu_icon.py", "quick_menu_assets.py", "SETTINGS.DDS",
    "AUTOMATION.DDS", "SELECTION.DDS", "BIOME.DDS", "PLANET.DDS", "STATION.DDS", "ANOMALY.DDS",
    HOST_NAME, BOOTSTRAP_NAME, "Start-CompanionAutoSummon.ps1",
    "pymhf.toml", "README.md",
    "cas_compatibility.py", "compatibility.json",
    *(f"locales/{code}.json" for code in ("en", "fr", "it", "de", "es-ES", "nl", "ja", "ko",
                                         "pl", "pt-PT", "pt-BR", "ru", "zh-Hans", "zh-Hant")),
))
EXPECTED_MODS = [
    {"name": "CompanionAutoSummon", "version": "0.4.8-experimental", "path": "CompanionAutoSummon.py"},
    {"name": "CompanionMenuOrderTrial", "version": "0.8.4-language-observation", "path": "CompanionMenuOrderTrial.py"},
]
EXPECTED_CONFIG = {
    "exe": "NMS.exe", "steam_gameid": 275850, "start_paused": False,
    "interactive_console": False,
    "logging": {"shown": False, "log_dir": "{CURR_DIR}", "log_level": "info"},
    "gui": {"shown": True, "always_on_top": False},
}


class BundleError(RuntimeError):
    """A play-trial package failed validation before any injection."""


def validate_bundle(folder):
    """Validate only the sibling isolated bundle, including its discovery set."""
    import json

    supplied = Path(folder)
    if not supplied.is_absolute():
        raise BundleError("Supply an absolute play-trial folder.")
    bundle = supplied.resolve(strict=True)
    if not bundle.is_dir() or bundle != Path(__file__).resolve(strict=True).parent:
        raise BundleError("The play-trial folder must contain this launcher.")
    if (bundle / "pyproject.toml").exists():
        raise BundleError("A play trial must not contain a competing library configuration.")
    manifest_path = bundle / "manifest.json"
    if manifest_path.resolve(strict=True).parent != bundle:
        raise BundleError("The manifest must belong to the play-trial folder.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (not isinstance(manifest, dict) or manifest.get("version") != VERSION
            or manifest.get("framework") != "pymhf[gui]==0.2.4"
            or manifest.get("supported_nms_exe_sha256") != compatibility.SUPPORTED_GAME_SHA256
            or manifest.get("steam_build") != compatibility.STEAM_BUILD
            or manifest.get("auto_summon") is not True
            or manifest.get("preference_actions") is not True
            or manifest.get("preference_keys") != ["enabled", "selection_mode", "prefer_same_biome", "locations"]
            or manifest.get("mods") != EXPECTED_MODS):
        raise BundleError("The manifest does not describe the supported combined trial.")
    entries = manifest.get("files")
    if not isinstance(entries, list) or len(entries) != len(PAYLOAD_FILES):
        raise BundleError("The play-trial manifest has an unexpected file set.")
    checked = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise BundleError("The play-trial manifest has an invalid file entry.")
        name, digest = entry.get("path"), entry.get("sha256")
        if (not isinstance(name, str) or name not in PAYLOAD_FILES or name in checked
                or not isinstance(digest, str) or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)):
            raise BundleError("The play-trial manifest has an invalid checksum entry.")
        path = bundle / name
        if not path.is_file() or path.resolve(strict=True) != bundle / name:
            raise BundleError("A required file is outside the play-trial folder or missing.")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise BundleError("A required play-trial file does not match its checksum.")
        checked.add(name)
    if checked != PAYLOAD_FILES:
        raise BundleError("The play-trial manifest is incomplete.")
    if json.loads((bundle / "compatibility.json").read_text(encoding="utf-8")) != compatibility.PROFILE:
        raise BundleError("The play-trial compatibility profile differs.")
    # pyMHF folder discovery scans the root and one child-directory level.
    # Reject unlisted Python files instead of allowing another mod to load.
    discovered = {path.relative_to(bundle).as_posix() for path in bundle.glob("*.py")}
    discovered.update(path.relative_to(bundle).as_posix() for path in bundle.glob("*/*.py"))
    expected = {name for name in PAYLOAD_FILES if name.endswith(".py")}
    if discovered != expected:
        raise BundleError("Unexpected Python files would change play-trial discovery.")
    with (bundle / "pymhf.toml").open("rb") as config_file:
        document = tomllib.load(config_file)
    if document != {"pymhf": EXPECTED_CONFIG}:
        raise BundleError("The play-trial framework configuration differs.")
    return bundle, document["pymhf"]


def _load_bootstrap(bundle):
    """Import the verified sibling host module without invoking its launcher."""
    path = bundle / BOOTSTRAP_NAME
    spec = util.spec_from_file_location("_cas_play_trial_injection_guard", path)
    if spec is None or spec.loader is None:
        raise BundleError("The canonical injection guard could not be imported.")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if (not callable(getattr(module, "install_injection_guard", None))
            or not callable(getattr(module, "launcher_session", None))):
        raise BundleError("The canonical injection guard or host lease is unavailable.")
    return module


def _windows_process_names(api=None):
    """Copy a bounded Toolhelp snapshot, including protected process names."""
    import ctypes as C
    from ctypes import wintypes as W
    class Entry(C.Structure):
        _fields_ = [("size", W.DWORD), ("usage", W.DWORD), ("pid", W.DWORD),
                    ("heap", C.c_size_t), ("module", W.DWORD), ("threads", W.DWORD),
                    ("parent", W.DWORD), ("priority", W.LONG), ("flags", W.DWORD),
                    ("name", W.WCHAR * 260)]
    if api is None:
        from types import SimpleNamespace
        kernel = C.WinDLL("kernel32", use_last_error=True)
        kernel.CreateToolhelp32Snapshot.argtypes = [W.DWORD, W.DWORD]
        kernel.CreateToolhelp32Snapshot.restype = W.HANDLE
        for function in (kernel.Process32FirstW, kernel.Process32NextW):
            function.argtypes = [W.HANDLE, C.POINTER(Entry)]
            function.restype = W.BOOL
        kernel.CloseHandle.argtypes = [W.HANDLE]
        kernel.CloseHandle.restype = W.BOOL
        api = SimpleNamespace(CreateToolhelp32Snapshot=kernel.CreateToolhelp32Snapshot,
                              Process32FirstW=kernel.Process32FirstW,
                              Process32NextW=kernel.Process32NextW,
                              CloseHandle=kernel.CloseHandle, get_last_error=C.get_last_error)
    handle = api.CreateToolhelp32Snapshot(2, 0)
    if not handle or handle == C.c_void_p(-1).value:
        raise BundleError("Windows process snapshot is unavailable.")
    try:
        entry = Entry()
        entry.size = C.sizeof(entry)
        names = []
        available = api.Process32FirstW(handle, C.byref(entry))
        while available:
            if len(names) >= 65536:
                raise BundleError("Windows process snapshot exceeded its limit.")
            names.append(entry.name)
            available = api.Process32NextW(handle, C.byref(entry))
        if api.get_last_error() != 18 or not names:
            raise BundleError("Windows process snapshot is incomplete.")
        return names
    finally:
        if not api.CloseHandle(handle):
            raise BundleError("Windows process snapshot cleanup failed.")


def _game_closed():
    """Refuse setup on unknown names, failed enumeration or a running NMS."""
    try:
        names = _windows_process_names()
        return bool(names) and all(type(name) is str and name and name.casefold() != "nms.exe"
                                   for name in names)
    except Exception:
        return False


def _prepare_icon_asset(bundle, game_directory):
    """Stage only the checked original asset in the explicitly validated game."""
    import json
    supplied = Path(game_directory)
    if not supplied.is_absolute():
        raise BundleError("Supply the absolute verified game directory.")
    game = supplied.resolve(strict=True)
    binary = game / "Binaries/NMS.exe"
    expected = json.loads((bundle / "manifest.json").read_text(encoding="utf-8")).get("supported_nms_exe_sha256")
    if not isinstance(expected, str) or len(expected) != 64:
        raise BundleError("A supported executable checksum is required before asset setup.")
    if not _game_closed():
        raise compatibility.CompatibilityError("launcher.game_running")
    try:
        with binary.open("rb") as stream:
            actual_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    except OSError:
        raise compatibility.CompatibilityError("launcher.unreadable_game") from None
    if actual_hash != expected:
        raise compatibility.CompatibilityError("launcher.game_changed")
    spec = util.spec_from_file_location("_cas_play_icon_asset_installer", bundle / "quick_menu_assets.py")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.install_icons(bundle, supplied, _game_closed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle_folder", help="Absolute folder containing this isolated play trial")
    parser.add_argument("--game-directory", required=True, help="Absolute verified Steam game directory")
    parser.add_argument("--language", help="Launcher language; defaults to the Windows UI language")
    parser.add_argument("--no-dialog", action="store_true", help="Write failure text without a modal dialog")
    parser.add_argument("--check-only", action="store_true", help="Validate without asset staging or game startup")
    args = parser.parse_args(argv)
    try:
        bundle, config = validate_bundle(args.bundle_folder)
        verified_executable = compatibility.verify_game_directory(args.game_directory)
        compatibility.verify_framework()
        if tuple(metadata.entry_points().select(group="pymhflib")):
            raise compatibility.CompatibilityError("launcher.invalid_package")
        if args.check_only:
            print(compatibility.warning_text("launcher.preflight_passed", args.language))
            return 0
        bootstrap = _load_bootstrap(bundle)
        with bootstrap.launcher_session():
            if not _game_closed():
                raise compatibility.CompatibilityError("launcher.game_running")
            bootstrap.install_injection_guard(expected_executable=verified_executable)
            _prepare_icon_asset(bundle, args.game_directory)
            if not _game_closed():
                raise compatibility.CompatibilityError("launcher.game_running")
            # Omitting plugin_name explicitly selects MOD_FOLDER. The 0.2.4 CLI's
            # folder path instead enters library/user-configuration handling.
            from pymhf.main import run_module
            return run_module(str(bundle), config)
    except compatibility.CompatibilityError as error:
        compatibility.show_failure(error, language=args.language,
                                   show_dialog=not (args.no_dialog or args.check_only))
        return 1
    except (BundleError, OSError, ValueError, KeyError) as error:
        compatibility.show_failure(compatibility.CompatibilityError("launcher.invalid_package"),
                                   language=args.language, show_dialog=not (args.no_dialog or args.check_only))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
