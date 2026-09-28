"""Package auto-summoning with the opt-in menu trial; never deploy or launch NMS."""

import argparse
import hashlib
from importlib import util
import json
from pathlib import Path
import re
import tomllib

_asset_spec = util.spec_from_file_location("_cas_build_assets", Path(__file__).with_name("quick_menu_assets.py"))
_asset_module = util.module_from_spec(_asset_spec)
_asset_spec.loader.exec_module(_asset_module)
ASSET_HASHES, validate_asset = _asset_module.ASSET_HASHES, _asset_module.validate_asset
_locale_spec = util.spec_from_file_location("_cas_build_locales", Path(__file__).with_name("validate_locales.py"))
_locale_module = util.module_from_spec(_locale_spec)
_locale_spec.loader.exec_module(_locale_module)
validate_locales = _locale_module.validate
_profile_spec = util.spec_from_file_location("_cas_build_profile", Path(__file__).with_name("validate_compatibility.py"))
_profile_module = util.module_from_spec(_profile_spec)
_profile_spec.loader.exec_module(_profile_module)
validate_compatibility = _profile_module.validate


ROOT = Path(__file__).resolve().parents[1]
HELPERS = ("quick_menu_item.py", "quick_menu_submenu.py", "quick_menu_order.py",
           "quick_menu_native_guard.py", "quick_menu_guard_runtime.py",
           "quick_menu_preferences.py", "quick_menu_toggle.py", "quick_menu_icon.py", "quick_menu_assets.py",
           "game_language.py")
ASSET_FILE = "SETTINGS.DDS"
PRODUCTION_FILE = "CompanionAutoSummon.py"
MENU_FILE = "CompanionMenuOrderTrial.py"
GUARD_HOST_FILE = "Launch-CompanionAutoSummon.py"
PLAY_HOST_FILE = "Launch-CompanionAutoSummon-PlayTrial.py"
LAUNCHER_FILE = "Start-CompanionAutoSummon.ps1"
CONFIG_FILE = "pymhf.toml"
CHECKED_FILES = (PRODUCTION_FILE, MENU_FILE, GUARD_HOST_FILE, PLAY_HOST_FILE,
                 "cas_compatibility.py", "compatibility.json", *HELPERS, CONFIG_FILE, LAUNCHER_FILE, *ASSET_HASHES,
                 *(f"locales/{code}.json" for code in _locale_module.LOCALES))
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
README = b"""# Companion Auto Summon for No Man's Sky

by Lineum Dynamics

Combined developer play trial.

This isolated developer bundle runs two mods in one pyMHF host:

- CompanionAutoSummon 0.5.0-experimental: automatic summoning after loading or
  ship exit, including its separate preference panel. The production source is
  copied byte-identically into this bundle.
- CompanionMenuOrderTrial 0.9.0-selection: the ordered native companion
  submenu with all seven settings, its binding filter and distinct setting icons.

The bundle version is 0.9.0-play-trial. This revision is not yet live-verified.
It adds By habitat selection with explicit 13:5:1 group weights and optional
identity-based companion rotation. Fresh installations use By habitat and
rotation ON; legacy preferences keep their selection mode with rotation OFF.
Native queue acceptance consumes a shuffle entry; rejection retains it.
Duplicate identities and changed frozen selections cancel safely. Rotation
history is session-only and resets on local loading. Known habitats have no
unrestricted fallback; unknown habitats wait, and neutral stations/Nexus use
the eligible pool without habitat weights. All native game rules still apply.
It retains optional, bounded language observations while a CAS menu caption is
selected. Two matching copies must confirm construction, the exact derived
vtable, a known native region and a prior completed-load marker. The marker is
not a reload lock. Diagnostics never change language, captions or HUD text,
follow pointers, call a language getter or add a native hook. A diagnostic
failure leaves the menu and automatic summoning active. Production retains
extended passive post-queue observation. This is not a claimed startup fix.
It adds exact-build checks before host startup and before each DLL injection
into the actual selected game process. Compatibility failures use translated
outside-game notices; --language/-Language selects a launcher language, otherwise
the Windows UI language is used with English fallback. This does not translate
the native menu. The catalogs remain unreviewed translation drafts.
This launcher revision adds a fixed setup lease and a separate host lease to
refuse duplicate launches before Steam has created NMS. Each lease lasts until
its process closes the handle. Normal setup refuses unavailable process checks.
Use Start-CompanionAutoSummon.ps1 -CheckOnly to check the package, exact game
and existing runtime while playing. It installs nothing and launches no game
or mod host; a missing runtime is reported, never prepared in check-only mode.
Previous launchers without these leases are not covered; never run them together.
Production 0.5.0 requires matching native UI pet selection before it can
remember a manual favorite. An unrelated accepted queue, including native
battle restoration, cannot overwrite that choice or announce it as saved.
Passive observation remains; no new retries or summon delays are added.
Shorter notices last 5.5 seconds. In-game validation is still required.
The native page contains Automatic summoning: ON/OFF, companion selection
(Last selected/Random/By habitat), Random: prefer matching biome, three separate
location switches (planets, space stations and Space Anomaly) and Shuffle companions.
Confirm a row with the
configured native Select action to queue its change. The local player update
applies and saves it through the existing production preference path. Pending
and session-only labels do not claim a successful disk save. Navigation,
opening and rebuilding the menu must not change a preference. The native
confirmation predicate must first report false, then true; holding Select
must not repeatedly toggle. Uncorrelated slot/tail activations do nothing.

The temporary CompanionAutoSummon development panel remains available for
this acceptance trial. The final player interface will retire it after the
native controls are verified. Existing settings are not reset or forced.

The original paw-with-arrow icon is included as SETTINGS.DDS for the parent
and notices. Each child has its own original icon: power, companion selection,
biome, planet, station, Anomaly and rotation. The biome preference affects Random on
planets only; Last selected preserves its stored value without using it.
At a future closed-game launch, the host validates all eight assets before
staging under GAMEDATA/MODS/CompanionAutoSummon/TEXTURES/UI/FRONTEND/ICONS/
COMPANIONAUTOSUMMON/. It reuses identical bytes and refuses to overwrite an
unknown file. Packaging installs nothing. One natural menu-resource phase
attempts registration; buffers remain pinned for the process lifetime. A ready
role icon is preferred, then a retained native paw, then clean text for notices.
There is no late-load or retry. Asset mounting, native lifetime and visual
results still need a live trial; the white-circle fix is not visually confirmed.

Number shortcuts for CAS entries remain blocked until native persistence and
replay are verified. Binding the current tagged None action could erase an
existing shortcut. The game may still display its standard Quick Bind hint.
This does not affect ordinary native actions or add physical hotkeys.
The source repository now validates draft menu/HUD catalogs for fourteen
languages during builds. Runtime text in this trial remains English; automatic
game-language detection and non-ASCII rendering are not yet implemented.

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
pet pages. Check the custom icon, all seven rows, native Back, close/reopen and
normal manual pet actions. First browse without confirming: every setting
must stay unchanged. Confirm one row at a time, return to play for the local
update, then reopen and compare with the development panel. Change each row
back after checking it. Confirm OFF and ON; cycle Last selected, Random and By habitat;
flip rotation, the biome preference and each location. Hold Select and verify only one
change. Check that changing a row preserves every other value. OFF cancels
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
        text, "@('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py', 'cas_compatibility.py', 'compatibility.json')",
        "@(" + ", ".join("'" + name + "'" for name in CHECKED_FILES) + ")",
        "checksum list")
    # The original package check must accept the folder argument, while still
    # requiring the host and manifest to be files. Do not relax other checks.
    text = _replace_once(
        text, "(Test-Path -LiteralPath $modPath -PathType Leaf)",
        "(Test-Path -LiteralPath $modPath -PathType Container)",
        "mod-path existence check")
    return text.encode("utf-8")


def build(*, enable_menu=False, output_name="quick-menu-play-trial-090"):
    """Create one fresh, checksum-complete folder without executing payloads."""
    if enable_menu is not True:
        raise ValueError("Pass --enable-menu for this combined developer trial")
    if not isinstance(output_name, str) or not re.fullmatch(r"quick-menu-[a-z0-9-]{1,64}", output_name):
        raise ValueError("Output must be a simple quick-menu- prefixed directory name")
    output = ROOT / "build" / output_name
    if output.exists() or output.is_symlink():
        raise FileExistsError("Trial output already exists; choose a new output name")
    validate_locales(locales_dir=ROOT / "locales", source_root=ROOT)
    validate_compatibility(source_root=ROOT, developer=True, generated=True)

    menu = (ROOT / "tools/quick_menu_order_trial.py").read_bytes()
    if menu.count(b"TRIAL_ENABLED = False") != 1:
        raise ValueError("Expected one disabled ordered submenu trial marker")
    menu = menu.replace(b"TRIAL_ENABLED = False", b"TRIAL_ENABLED = True", 1)
    if menu.count(b"SETTINGS_TOGGLE_ENABLED = False") != 1:
        raise ValueError("Expected one disabled native settings marker")
    menu = menu.replace(b"SETTINGS_TOGGLE_ENABLED = False", b"SETTINGS_TOGGLE_ENABLED = True", 1)
    for flag in (b"EXTENDED_SETTINGS_ENABLED", b"CUSTOM_ICON_ENABLED", b"LANGUAGE_OBSERVATION_ENABLED"):
        if menu.count(flag + b" = False") != 1:
            raise ValueError("Expected one disabled extended-menu feature marker")
        menu = menu.replace(flag + b" = False", flag + b" = True", 1)
    payload = {
        PRODUCTION_FILE: (ROOT / PRODUCTION_FILE).read_bytes(),
        MENU_FILE: menu,
        GUARD_HOST_FILE: (ROOT / GUARD_HOST_FILE).read_bytes(),
        PLAY_HOST_FILE: (ROOT / "tools" / PLAY_HOST_FILE).read_bytes(),
        "cas_compatibility.py": (ROOT / "cas_compatibility.py").read_bytes(),
    }
    for name in HELPERS:
        payload[name] = (ROOT / "tools" / name).read_bytes()
    for name, data in payload.items():
        compile(data, name, "exec")
    payload["compatibility.json"] = (ROOT / "compatibility.json").read_bytes()
    for code in _locale_module.LOCALES:
        payload[f"locales/{code}.json"] = (ROOT / "locales" / f"{code}.json").read_bytes()
    for asset_name in ASSET_HASHES:
        payload[asset_name] = (ROOT / "assets/ui" / asset_name).read_bytes()
        validate_asset(payload[asset_name], asset_name)
    tomllib.loads(CONFIG.decode("utf-8"))
    payload[CONFIG_FILE] = CONFIG
    payload[LAUNCHER_FILE] = _launcher((ROOT / LAUNCHER_FILE).read_bytes())
    payload["README.md"] = README

    current = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    if (current["version"] != "0.5.0-experimental"
            or current["framework"] != "pymhf[gui]==0.2.4"):
        raise ValueError("The play-trial host requires the reviewed production and framework versions")
    manifest = {
        "name": "Companion Auto Summon for No Man's Sky",
        "author": "Lineum Dynamics",
        "repository": "https://github.com/lineum-dynamics/nms-companion-auto-summon",
        "version": "0.9.0-play-trial",
        "framework": current["framework"],
        "steam_build": current["steam_build"],
        "supported_nms_exe_sha256": current["supported_nms_exe_sha256"],
        "purpose": "Automatic summoning, seven native settings, role icons and bounded scalar language observations",
        "observation_only": False,
        "auto_summon": True,
        "preference_actions": True,
        "preference_keys": ["enabled", "selection_mode", "prefer_same_biome", "locations", "rotate_companions"],
        "live_verified": False,
        "preferences_included": False,
        "manual_selection_path": "%LOCALAPPDATA%/NMS-AutoPet/state.json",
        "preferences_path": "%LOCALAPPDATA%/NMS-AutoPet/settings.json",
        "mods": [
            {"name": "CompanionAutoSummon", "version": current["version"],
             "path": PRODUCTION_FILE},
            {"name": "CompanionMenuOrderTrial", "version": "0.9.0-selection",
             "path": MENU_FILE},
        ],
        "files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest()}
                  for name, data in payload.items()],
    }
    payload["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        (output / name).parent.mkdir(parents=True, exist_ok=True)
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
    parser.add_argument("--output-name", default="quick-menu-play-trial-090")
    options = parser.parse_args()
    print(json.dumps(build(enable_menu=options.enable_menu,
                           output_name=options.output_name)))
