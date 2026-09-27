"""Build an explicitly enabled inert-item trial; never deploy or start NMS."""

import argparse
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
HELPERS = ("quick_menu_item.py", "quick_menu_native_guard.py", "quick_menu_guard_runtime.py")


def build(*, enable_inert_item=False, output_name="quick-menu-inert-item"):
    if enable_inert_item is not True:
        raise ValueError("Pass --enable-inert-item for this mutating developer trial")
    if not isinstance(output_name, str) or not re.fullmatch(r"quick-menu-[a-z0-9-]{1,64}", output_name):
        raise ValueError("Output must be a simple quick-menu- prefixed directory name")
    output = ROOT / "build" / output_name
    if output.exists():
        raise FileExistsError("Trial output already exists; choose a new output name")
    main = (ROOT / "tools/quick_menu_item_trial.py").read_text(encoding="utf-8")
    if main.count("TRIAL_ENABLED = False") != 1:
        raise ValueError("Expected one disabled inert-item trial marker")
    main = main.replace("TRIAL_ENABLED = False", "TRIAL_ENABLED = True", 1)
    payload = {"CompanionAutoSummon.py": main.encode("utf-8")}
    for name in HELPERS:
        payload[name] = (ROOT / "tools" / name).read_bytes()
    payload["Launch-CompanionAutoSummon.py"] = (ROOT / "Launch-CompanionAutoSummon.py").read_bytes()
    for name, data in payload.items():
        compile(data, name, "exec")
    launcher = (ROOT / "Start-CompanionAutoSummon.ps1").read_text(encoding="utf-8")
    old_checks = "@('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py')"
    if launcher.count(old_checks) != 1:
        raise ValueError("Expected one known launcher checksum list")
    required = ("CompanionAutoSummon.py", "Launch-CompanionAutoSummon.py", *HELPERS)
    launcher = launcher.replace(old_checks, "@(" + ", ".join("'" + name + "'" for name in required) + ")")
    payload["Start-CompanionAutoSummon.ps1"] = launcher.replace(
        "Companion Auto Summon", "Companion Auto Summon inert menu trial"
    ).encode("utf-8")
    payload["README.md"] = b"""# Inert native menu item trial

This developer trial ADDS an item. It is not an observation-only probe or the
player release. Automatic summoning and preference changes are absent here.

After normal game exit, preserve current progress and verify a fresh backup.
Use this folder's Start-CompanionAutoSummon.ps1 with the exact supported build.
The trial installs a native, item-specific shortcut-binding filter before it
can append Companion Auto Summon to the direct companion submenu. The filter
stays installed for this process's lifetime, including a stopped callback. Do
not disable/remove it or hot-reload this developer trial while NMS is running.

Open the quick menu using your configured control, then enter companions. The
new item uses the existing companion icon and the English Companion Auto Summon
label. Selecting it has no settings effect yet. Navigate across it and native
neighbors, back out, close/reopen, and confirm ordinary companion actions still
work. This first trial is for display and lifecycle, not completed settings.
Do not rebind an occupied shortcut as part of this initial test. Existing
shortcut replay, remapping/controller behavior and save/reload/removal remain
separate acceptance checks before release; do not claim them from visibility.

Exit NMS normally before closing its pyMHF host. The installed regular mod is
unchanged and can be used through its own launcher in a later game session.
Never copy this trial into GAMEDATA/MODS or over an installed/running version.
"""
    current = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    manifest = {
        "name": "Companion Auto Summon inert menu trial",
        "version": "0.4.1-inert-item-trial",
        "framework": current["framework"], "steam_build": current["steam_build"],
        "supported_nms_exe_sha256": current["supported_nms_exe_sha256"],
        "purpose": "One inert visible native companion-menu item with a separate binding filter",
        "observation_only": False, "auto_summon": False, "preference_actions": False,
        "live_verified": False,
        "files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest()}
                  for name, data in payload.items()],
    }
    payload["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        (output / name).write_bytes(data)
    if any((output / name).read_bytes() != data for name, data in payload.items()):
        raise RuntimeError("Inert trial readback failed")
    return {"output": str(output), "files": len(payload), "launched": False,
            "deployed": False, "observation_only": False,
            "trial_sha256": hashlib.sha256(payload["CompanionAutoSummon.py"]).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enable-inert-item", action="store_true")
    parser.add_argument("--output-name", default="quick-menu-inert-item")
    options = parser.parse_args()
    print(json.dumps(build(enable_inert_item=options.enable_inert_item,
                           output_name=options.output_name)))
