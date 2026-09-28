"""Owned portable bootstrap. Importing never starts or accesses the game.

The native entry point verifies the complete distribution before starting this
script. This second check also protects direct invocations. Only normal launch
creates private logs/backups or hands control to the existing guarded host.
"""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
from importlib import util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import uuid


MAX_MANIFEST_BYTES = 8 * 1024 * 1024
VERSION = "0.9.3-test"
MAX_FILES = 30000
MAX_BACKUP_BYTES = 1024 * 1024 * 1024
SETUP_MUTEX = r"Local\CompanionAutoSummon.Setup.v1"
PACKAGE_FAILURE_TITLE = "Companion Auto Summon for No Man's Sky could not start"
PACKAGE_FAILURE_BODY = "The mod package is incomplete or inconsistent. Extract a complete matching package and try again."


class PortableError(RuntimeError):
    def __init__(self, key):
        self.key = key
        super().__init__(key)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def regular_path(root, name):
    """Refuse alternate streams, traversal and Windows reparse points."""
    if (type(name) is not str or not name or "\\" in name or ":" in name
            or any(ord(c) < 32 for c in name)):
        raise ValueError("Invalid payload path")
    parts = PurePosixPath(name).parts
    if not parts or PurePosixPath(name).is_absolute() or "/".join(parts) != name or any(p in (".", "..") for p in parts):
        raise ValueError("Invalid payload components")
    path = Path(root)
    for part in parts:
        path /= part
        info = path.lstat()
        if path.is_symlink() or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError("Reparse payload refused")
    if not path.is_file() or path.resolve(strict=True) != Path(root) / name:
        raise ValueError("Non-regular payload")
    return path


def validate_distribution(root):
    root = Path(root).resolve(strict=True)
    manifest_path = regular_path(root, "portable-manifest.json")
    data = manifest_path.read_bytes()
    if len(data) > MAX_MANIFEST_BYTES:
        raise ValueError("Oversized manifest")
    manifest = json.loads(data, object_pairs_hook=unique_object)
    if (type(manifest) is not dict or type(manifest.get("schema_version")) is not int
            or manifest["schema_version"] != 1 or manifest.get("version") != VERSION):
        raise ValueError("Unsupported portable package")
    files = manifest.get("files")
    if type(files) is not list or not 1 <= len(files) <= MAX_FILES:
        raise ValueError("Invalid manifest file set")
    checked = set()
    for entry in files:
        if type(entry) is not dict:
            raise ValueError("Invalid manifest entry")
        name, expected = entry.get("path"), entry.get("sha256")
        if (type(name) is not str or name.casefold() in checked or type(expected) is not str
                or re.fullmatch(r"[0-9a-f]{64}", expected) is None):
            raise ValueError("Invalid or duplicate payload entry")
        path = regular_path(root, name)
        if digest(path) != expected:
            raise ValueError("Changed portable payload")
        checked.add(name.casefold())
    required = {"runtime/python.exe", "runtime/pythonw.exe", "app/portable_launcher.py",
                "mod/manifest.json", "mod/launch-companionautosummon-playtrial.py", "mod/cas_compatibility.py"}
    if not required <= checked:
        raise ValueError("Incomplete portable package")
    # Unknown runtime code can run before ordinary module validation. The EXE
    # performs this same check before starting Python at all.
    for folder in ("runtime", "app"):
        for path in (root / folder).rglob("*"):
            if path.is_file() and path.relative_to(root).as_posix().casefold() not in checked:
                raise ValueError("Unlisted runtime or launcher file")
    return manifest


def load_module(path, name):
    spec = util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Module unavailable")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def steam_roots():
    """Use Steam's local registry links, with its conventional fallback."""
    import winreg
    roots = set()
    for hive, key in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
                      (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
                      (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam")):
        try:
            with winreg.OpenKey(hive, key) as opened:
                for field in ("SteamPath", "InstallPath"):
                    try:
                        value, kind = winreg.QueryValueEx(opened, field)
                        if kind == winreg.REG_SZ and Path(value).is_absolute():
                            roots.add(Path(value))
                    except OSError:
                        pass
        except OSError:
            pass
    program_files = os.environ.get("ProgramFiles(x86)")
    if program_files:
        roots.add(Path(program_files) / "Steam")
    return roots


def discover_games(roots):
    libraries = {Path(p).resolve() for p in roots if Path(p).is_dir()}
    for root in tuple(libraries):
        path = root / "steamapps/libraryfolders.vdf"
        if path.is_file():
            if path.stat().st_size > 4 * 1024 * 1024:
                raise ValueError("Oversized Steam libraries file")
            for match in re.finditer(r'"path"\s*"((?:\\.|[^"\\])*)"', path.read_text(encoding="utf-8-sig")):
                value = match[1].replace("\\\\", "\\")
                if Path(value).is_absolute() and Path(value).is_dir():
                    libraries.add(Path(value).resolve())
    found = set()
    for library in libraries:
        manifest = library / "steamapps/appmanifest_275850.acf"
        if not manifest.is_file():
            continue
        if manifest.stat().st_size > 1024 * 1024:
            raise ValueError("Oversized Steam application manifest")
        text = manifest.read_text(encoding="utf-8-sig")
        install = re.search(r'"installdir"\s*"([^"\\/:]+)"', text)
        if not re.search(r'"appid"\s*"275850"', text) or not install or install[1] in (".", ".."):
            continue
        game = library / "steamapps/common" / install[1]
        if (game / "Binaries/NMS.exe").is_file():
            found.add(game.resolve())
    return sorted(found, key=lambda p: str(p).casefold())


def select_game(explicit, compatibility, roots=None):
    if explicit:
        return compatibility.verify_game_directory(explicit).parent.parent
    candidates = discover_games(steam_roots() if roots is None else roots)
    if not candidates:
        raise PortableError("portable.game_choice_required")
    matching = []
    failures = []
    for candidate in candidates:
        try:
            matching.append(compatibility.verify_game_directory(candidate).parent.parent)
        except compatibility.CompatibilityError as error:
            failures.append(error)
    if not matching:
        raise failures[0]
    if len(matching) != 1:
        raise PortableError("portable.game_choice_required")
    return matching[0]


def require_steam(compatibility):
    """Read local process names without opening a game process or launching it."""
    try:
        names = compatibility._windows_process_names()
        if not any(type(name) is str and name.casefold() == "steam.exe" for name in names):
            raise PortableError("portable.steam_required")
    except PortableError:
        raise
    except Exception:
        raise PortableError("portable.steam_required") from None


@contextmanager
def setup_lease(bootstrap):
    # Reuse the existing handle-lifetime implementation with the separate setup
    # name. The host keeps its original name and still acquires its own lease.
    original = bootstrap.LAUNCHER_MUTEX_NAME
    bootstrap.LAUNCHER_MUTEX_NAME = SETUP_MUTEX
    try:
        with bootstrap.launcher_session():
            yield
    finally:
        bootstrap.LAUNCHER_MUTEX_NAME = original


def _backup_files(save_root, preference_root):
    result = []
    for root in (save_root, preference_root):
        if root.exists() and (root.is_symlink() or getattr(root.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
            raise ValueError("Backup source root is a reparse point")
    if save_root.exists():
        if not save_root.is_dir():
            raise ValueError("Save directory is not a directory")
        for path in save_root.rglob("*"):
            info = path.lstat()
            if path.is_symlink() or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise ValueError("Save reparse point refused")
            if path.is_file():
                result.append((path, "saves/" + path.relative_to(save_root).as_posix()))
    for name in ("settings.json", "state.json"):
        path = preference_root / name
        if path.exists():
            if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise ValueError("Preference reparse point refused")
            if not path.is_file():
                raise ValueError("Preference is not a file")
            result.append((path, "preferences/" + name))
    if len(result) > 10000 or sum(path.stat().st_size for path, _ in result) > MAX_BACKUP_BYTES:
        raise ValueError("Backup exceeds bounded profile size")
    return sorted(result, key=lambda pair: pair[1])


def backup_profiles(save_root, preference_root, destination, game_closed):
    """Copy and source/copy/source verify while the game remains closed."""
    save_root, preference_root, destination = map(Path, (save_root, preference_root, destination))
    if not game_closed():
        raise PortableError("launcher.game_running")
    files = _backup_files(save_root, preference_root)
    destination.mkdir(parents=True, exist_ok=False)
    incomplete = destination / "INCOMPLETE"
    incomplete.write_text("Backup verification has not completed.\n", encoding="utf-8")
    entries = []
    for source, name in files:
        if not game_closed():
            raise PortableError("launcher.game_running")
        before = digest(source)
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as incoming, target.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing)
        if digest(target) != before or digest(source) != before:
            raise PortableError("portable.backup_failed")
        entries.append({"path": name, "sha256": before, "bytes": target.stat().st_size})
    if not game_closed() or [(str(p), name) for p, name in _backup_files(save_root, preference_root)] != [(str(p), name) for p, name in files]:
        raise PortableError("portable.backup_failed")
    # A final pass detects a source changed after its individual copy check.
    if any(digest(path) != entry["sha256"] for (path, _), entry in zip(files, entries)):
        raise PortableError("portable.backup_failed")
    if not game_closed():
        raise PortableError("launcher.game_running")
    (destination / "backup-manifest.json").write_text(json.dumps({
        "schema_version": 1, "verified": True, "files": entries,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "game_closed_before_and_after": True,
    }, indent=2) + "\n", encoding="utf-8")
    incomplete.unlink()  # Only the marker just created by this function.
    return destination


def portable_text(key, compatibility, language=None):
    try:
        code = compatibility._language_code(language)
        english = json.loads((compatibility.LOCALES_DIRECTORY / "en.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)["messages"]
        selected = english if code == "en" else json.loads((compatibility.LOCALES_DIRECTORY / (code + ".json")).read_text(encoding="utf-8"), object_pairs_hook=unique_object)["messages"]
        canonical, entry = english[key], selected[key]
        if (canonical["source_sha256"] != hashlib.sha256(canonical["text"].encode("utf-8")).hexdigest()
                or entry["source_sha256"] != canonical["source_sha256"]):
            raise ValueError("Stale message")
        return entry["text"]
    except Exception:
        return compatibility.warning_text("launcher.invalid_package", language)


def stage_mod(source, destination):
    """Make a private, verified session copy for framework cache and logs."""
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    destination.mkdir(parents=True, exist_ok=False)
    for entry in manifest["files"]:
        name = entry["path"]
        incoming = regular_path(source, name)
        if digest(incoming) != entry["sha256"]:
            raise PortableError("portable.runtime_invalid")
        outgoing = destination / name
        outgoing.parent.mkdir(parents=True, exist_ok=True)
        with incoming.open("rb") as reader, outgoing.open("xb") as writer:
            shutil.copyfileobj(reader, writer)
        if digest(outgoing) != entry["sha256"]:
            raise PortableError("portable.runtime_invalid")
    with (destination / "manifest.json").open("xb") as writer:
        writer.write((source / "manifest.json").read_bytes())
    return destination


def run(root, args):
    validate_distribution(root)
    root = Path(root).resolve(strict=True)
    # Imports only after integrity validation. Each path is owned by this ZIP.
    sys.path.insert(0, str(root / "mod"))
    sys.path.insert(0, str(root / "app"))
    compatibility = load_module(root / "mod/cas_compatibility.py", "_cas_portable_compatibility")
    host = load_module(root / "mod/Launch-CompanionAutoSummon-PlayTrial.py", "_cas_portable_play_host")
    host.validate_bundle(str(root / "mod"))
    game = select_game(args.game_directory, compatibility)
    compatibility.verify_framework()
    support = load_module(root / "app/portable_host_support.py", "_cas_portable_host_support")
    support.verify_runtime(root / "runtime")
    if args.check_only:
        print(portable_text("portable.check_passed", compatibility, args.language))
        return 0
    if not compatibility.game_closed():
        raise PortableError("launcher.game_running")
    require_steam(compatibility)
    bootstrap = host._load_bootstrap(root / "mod")
    with setup_lease(bootstrap):
        if not compatibility.game_closed():
            raise PortableError("launcher.game_running")
        local = os.environ.get("LOCALAPPDATA")
        roaming = os.environ.get("APPDATA")
        if not local or not roaming or not Path(local).is_absolute() or not Path(roaming).is_absolute():
            raise PortableError("portable.backup_failed")
        data = Path(local) / "NMS-AutoPet"
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + uuid.uuid4().hex[:8]
        try:
            backup_profiles(Path(roaming) / "HelloGames/NMS", data,
                            data / "backups" / (stamp + "_before-" + VERSION), compatibility.game_closed)
        except PortableError:
            raise
        except Exception:
            raise PortableError("portable.backup_failed") from None
        # The child owns its log handle. Closing the .NET UI never closes a
        # pipe needed by the live host and never terminates the game.
        log_dir = data / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        staged = stage_mod(root / "mod", data / "sessions" / stamp / "mod")
        sys.path.insert(0, str(staged))
        host = load_module(staged / "Launch-CompanionAutoSummon-PlayTrial.py", "_cas_portable_session_host")
        host.validate_bundle(str(staged))
        with (log_dir / (stamp + "_portable.log")).open("x", encoding="utf-8", buffering=1) as log:
            original_out, original_err = sys.stdout, sys.stderr
            try:
                sys.stdout = sys.stderr = log
                support.prepare_host(root / "runtime")
                options = [str(staged), "--game-directory", str(game)]
                if args.language:
                    options += ["--language", args.language]
                if args.no_dialog:
                    options.append("--no-dialog")
                return host.main(options)
            except Exception:
                import traceback
                traceback.print_exc(file=log)
                raise
            finally:
                sys.stdout, sys.stderr = original_out, original_err


def main(argv=None, root=None):
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-directory")
    parser.add_argument("--language")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--no-dialog", action="store_true")
    args = parser.parse_args(argv)
    root = Path(root) if root is not None else Path(__file__).resolve().parent.parent
    compatibility = None
    try:
        validate_distribution(root)
        compatibility = load_module(root / "mod/cas_compatibility.py", "_cas_portable_failure")
        return run(root, args)
    except Exception as error:
        key = getattr(error, "key", "portable.runtime_invalid")
        try:
            title, text = PACKAGE_FAILURE_TITLE, PACKAGE_FAILURE_BODY
            if compatibility is not None:
                title = compatibility.warning_text("launcher.blocked_title", args.language)
                text = (compatibility.warning_text(key, args.language) if key.startswith("launcher.")
                        else portable_text(key, compatibility, args.language))
            if args.check_only or args.no_dialog:
                print(text, file=sys.stderr)
            else:
                import ctypes
                ctypes.windll.user32.MessageBoxW(None, text, title, 0x10)
        except Exception:
            # The native entry point already supplies a package-error dialog
            # if required resources cannot be verified before dispatch.
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
