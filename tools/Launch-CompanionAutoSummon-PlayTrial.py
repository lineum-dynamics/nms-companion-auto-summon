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


VERSION = "0.6.2-play-trial"
HOST_NAME = "Launch-CompanionAutoSummon-PlayTrial.py"
BOOTSTRAP_NAME = "Launch-CompanionAutoSummon.py"
PAYLOAD_FILES = frozenset((
    "CompanionAutoSummon.py", "CompanionMenuOrderTrial.py",
    "quick_menu_item.py", "quick_menu_submenu.py", "quick_menu_order.py",
    "quick_menu_native_guard.py", "quick_menu_guard_runtime.py",
    HOST_NAME, BOOTSTRAP_NAME, "Start-CompanionAutoSummon.ps1",
    "pymhf.toml", "README.md",
))
EXPECTED_MODS = [
    {"name": "CompanionAutoSummon", "version": "0.4.3-experimental", "path": "CompanionAutoSummon.py"},
    {"name": "CompanionMenuOrderTrial", "version": "0.6.0-order-trial", "path": "CompanionMenuOrderTrial.py"},
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
            or manifest.get("auto_summon") is not True
            or manifest.get("preference_actions") is not False
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
        if not path.is_file() or path.resolve(strict=True).parent != bundle:
            raise BundleError("A required file is outside the play-trial folder or missing.")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise BundleError("A required play-trial file does not match its checksum.")
        checked.add(name)
    if checked != PAYLOAD_FILES:
        raise BundleError("The play-trial manifest is incomplete.")
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
    if not callable(getattr(module, "install_injection_guard", None)):
        raise BundleError("The canonical injection guard is unavailable.")
    return module


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle_folder", help="Absolute folder containing this isolated play trial")
    args = parser.parse_args(argv)
    bundle, config = validate_bundle(args.bundle_folder)
    if metadata.version("pymhf") != "0.2.4":
        raise BundleError("The play trial requires pyMHF 0.2.4.")
    if tuple(metadata.entry_points().select(group="pymhflib")):
        raise BundleError("The play-trial runtime must not load additional pyMHF libraries.")
    _load_bootstrap(bundle).install_injection_guard()
    # Omitting plugin_name explicitly selects MOD_FOLDER. The 0.2.4 CLI's
    # folder path instead enters library/user-configuration handling.
    from pymhf.main import run_module
    return run_module(str(bundle), config)


if __name__ == "__main__":
    main()
