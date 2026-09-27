"""Package auto-summoning with the opt-in menu trial; never deploy or launch NMS."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]
HELPERS = ("quick_menu_item.py", "quick_menu_submenu.py", "quick_menu_order.py",
           "quick_menu_native_guard.py", "quick_menu_guard_runtime.py",
           "quick_menu_preferences.py", "quick_menu_toggle.py")
PRODUCTION_FILE = "CompanionAutoSummon.py"
MENU_FILE = "CompanionMenuOrderTrial.py"
GUARD_HOST_FILE = "Launch-CompanionAutoSummon.py"
PLAY_HOST_FILE = "Launch-CompanionAutoSummon-PlayTrial.py"
LAUNCHER_FILE = "Start-CompanionAutoSummon.ps1"
CONFIG_FILE = "pymhf.toml"
CHECKED_FILES = (PRODUCTION_FILE, MENU_FILE, GUARD_HOST_FILE, PLAY_HOST_FILE,
                 *HELPERS, CONFIG_FILE, LAUNCHER_FILE)
CONFIG = b"""[pymhf]
exe = "NMS.exe"
steam_gameid = 275850
start_paused = false
interactive_console = false

[pymhf.logging]
shown = false
log_dir = "{CURR_DIR}"
log_level = "info"

[pymhf.gui]
shown = true
always_on_top = false
"""
README = b"""# Companion Auto Summon combined play trial

This isolated developer bundle runs two mods in one pyMHF host:

- CompanionAutoSummon 0.4.5-experimental: automatic summoning after loading or
  ship exit, including its separate preference panel. The production source is
  copied byte-identically into this bundle.
- CompanionMenuOrderTrial 0.7.0-toggle-trial: the ordered native companion
  submenu with one automatic-summoning toggle and its binding filter.

The bundle version is 0.7.2-play-trial. This revision is not yet live-verified.
Production 0.4.5 requires matching native UI pet selection before it can
remember a manual favorite. An unrelated accepted queue, including native
battle restoration, cannot overwrite that choice or announce it as saved.
Passive observation remains; no new retries or summon delays are added.
Shorter notices last 5.5 seconds. In-game validation is still required.
The native child displays Automatic summoning: ON/OFF. Confirm it with the
configured native Select action to queue a change. The local player update
applies and saves it through the existing production preference path. Pending
and session-only labels do not claim a successful disk save. Navigation,
opening and rebuilding the menu must not change a preference. The native
confirmation predicate must first report false, then true; holding Select
must not repeatedly toggle. Uncorrelated slot/tail activations do nothing.

Other settings still use the temporary CompanionAutoSummon development panel.
The final player interface will retire that panel after all native controls
are implemented and verified. Existing settings are not reset or forced.
The native menu icon remains borrowed; no custom texture is loaded here.

When automatic summoning is enabled, loading a save records one pending startup
intent. The first eligible local-player update handles it through the existing
selection and placement path, using the current selection mode. No settings
change is needed to activate this behavior. Deserialization makes no native
summon calls; eligibility is checked later in the established player callback.

Close NMS normally, preserve progress and verify a fresh backup before starting
this separate trial. Extract the entire folder and use its
Start-CompanionAutoSummon.ps1. It verifies the executable and package before
launching both mods through the folder-mode host. Never run a second mod host
alongside it or copy this trial over an installed/running version.

The package includes no personal data. Existing preferences and manual companion
identity remain at the absolute LOCALAPPDATA/NMS-AutoPet/settings.json and
LOCALAPPDATA/NMS-AutoPet/state.json paths. Packaging does not read, edit, reset
or copy either file, and neither mod writes the game's save files. During play,
the production mod can persist its normal local preferences and
manual companion identity. Native ownership, eligibility and placement rules
still apply; no pets are granted and no gameplay limits are lowered.

Open the quick menu with the configured control and enter companions. The CAS
entry should follow general companion actions and precede individual pets or
pet pages. Check the automation toggle, native Back, close/reopen and normal
manual pet actions. First browse without confirming: the setting must stay
unchanged. Confirm OFF, close/reopen and check OFF in both interfaces; confirm
ON and check the same. Hold Select and verify only one change. OFF cancels
pending summons without dismissing an active pet; ON alone does not summon.
The remaining controls must keep their values. This new native route is not
yet verified with default/remapped keyboard, mouse or controllers. Check automatic summoning after loading at an eligible location
and after leaving the ship, using your current preferences. Do not rebind an occupied
shortcut during the initial test. Remapping, controller behavior, changing pet
lists, shortcut persistence/removal and coexistence still need acceptance tests.

Never hot-reload either mod or disable/remove the native binding filter while
this host is active. The filter remains pinned for the game process lifetime.
Exit NMS normally before closing its pyMHF host. A later ordinary session can
use the unchanged regular installation and its own launcher.
"""


def _replace_once(text, marker, replacement, description):
    if text.count(marker) != 1:
        raise ValueError(f"Expected one known launcher {description}")
    return text.replace(marker, replacement, 1)


def _launcher(data):
    """Preserve the reviewed launcher except for four exact folder-mode edits."""
    text = data.decode("utf-8")
    text = _replace_once(
        text, "$modPath = Join-Path $PSScriptRoot 'CompanionAutoSummon.py'",
        "$modPath = $PSScriptRoot", "mod-path assignment")
    text = _replace_once(
        text, "$bootstrapPath = Join-Path $PSScriptRoot 'Launch-CompanionAutoSummon.py'",
        f"$bootstrapPath = Join-Path $PSScriptRoot '{PLAY_HOST_FILE}'",
        "host-path assignment")
    text = _replace_once(
        text, "@('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py')",
        "@(" + ", ".join("'" + name + "'" for name in CHECKED_FILES) + ")",
        "checksum list")
    # The original package check must accept the folder argument, while still
    # requiring the host and manifest to be files. Do not relax other checks.
    text = _replace_once(
        text, "(Test-Path -LiteralPath $modPath -PathType Leaf)",
        "(Test-Path -LiteralPath $modPath -PathType Container)",
        "mod-path existence check")
    return text.encode("utf-8")


def build(*, enable_menu=False, output_name="quick-menu-play-trial-072"):
    """Create one fresh, checksum-complete folder without executing payloads."""
    if enable_menu is not True:
        raise ValueError("Pass --enable-menu for this combined developer trial")
    if not isinstance(output_name, str) or not re.fullmatch(r"quick-menu-[a-z0-9-]{1,64}", output_name):
        raise ValueError("Output must be a simple quick-menu- prefixed directory name")
    output = ROOT / "build" / output_name
    if output.exists() or output.is_symlink():
        raise FileExistsError("Trial output already exists; choose a new output name")

    menu = (ROOT / "tools/quick_menu_order_trial.py").read_bytes()
    if menu.count(b"TRIAL_ENABLED = False") != 1:
        raise ValueError("Expected one disabled ordered submenu trial marker")
    menu = menu.replace(b"TRIAL_ENABLED = False", b"TRIAL_ENABLED = True", 1)
    if menu.count(b"SETTINGS_TOGGLE_ENABLED = False") != 1:
        raise ValueError("Expected one disabled native settings marker")
    menu = menu.replace(b"SETTINGS_TOGGLE_ENABLED = False", b"SETTINGS_TOGGLE_ENABLED = True", 1)
    payload = {
        PRODUCTION_FILE: (ROOT / PRODUCTION_FILE).read_bytes(),
        MENU_FILE: menu,
        GUARD_HOST_FILE: (ROOT / GUARD_HOST_FILE).read_bytes(),
        PLAY_HOST_FILE: (ROOT / "tools" / PLAY_HOST_FILE).read_bytes(),
    }
    for name in HELPERS:
        payload[name] = (ROOT / "tools" / name).read_bytes()
    for name, data in payload.items():
        compile(data, name, "exec")
    tomllib.loads(CONFIG.decode("utf-8"))
    payload[CONFIG_FILE] = CONFIG
    payload[LAUNCHER_FILE] = _launcher((ROOT / LAUNCHER_FILE).read_bytes())
    payload["README.md"] = README

    current = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    if (current["version"] != "0.4.5-experimental"
            or current["framework"] != "pymhf[gui]==0.2.4"):
        raise ValueError("The play-trial host requires the reviewed production and framework versions")
    manifest = {
        "name": "Companion Auto Summon combined play trial",
        "version": "0.7.2-play-trial",
        "framework": current["framework"],
        "steam_build": current["steam_build"],
        "supported_nms_exe_sha256": current["supported_nms_exe_sha256"],
        "purpose": "Automatic summoning plus one predicate-gated native automation toggle in one folder-mode host",
        "observation_only": False,
        "auto_summon": True,
        "preference_actions": True,
        "preference_keys": ["enabled"],
        "live_verified": False,
        "preferences_included": False,
        "manual_selection_path": "%LOCALAPPDATA%/NMS-AutoPet/state.json",
        "preferences_path": "%LOCALAPPDATA%/NMS-AutoPet/settings.json",
        "mods": [
            {"name": "CompanionAutoSummon", "version": current["version"],
             "path": PRODUCTION_FILE},
            {"name": "CompanionMenuOrderTrial", "version": "0.7.0-toggle-trial",
             "path": MENU_FILE},
        ],
        "files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest()}
                  for name, data in payload.items()],
    }
    payload["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        (output / name).write_bytes(data)
    if any((output / name).read_bytes() != data for name, data in payload.items()):
        raise RuntimeError("Combined play trial readback failed")
    return {"output": str(output), "files": len(payload), "launched": False,
            "deployed": False, "observation_only": False, "auto_summon": True,
            "production_sha256": hashlib.sha256(payload[PRODUCTION_FILE]).hexdigest(),
            "trial_sha256": hashlib.sha256(payload[MENU_FILE]).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enable-menu", action="store_true")
    parser.add_argument("--output-name", default="quick-menu-play-trial-072")
    options = parser.parse_args()
    print(json.dumps(build(enable_menu=options.enable_menu,
                           output_name=options.output_name)))
