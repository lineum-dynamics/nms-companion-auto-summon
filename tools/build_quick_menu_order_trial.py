"""Build an explicitly enabled ordered submenu trial; never deploy or start NMS."""

import argparse
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
HELPERS = ("quick_menu_item.py", "quick_menu_submenu.py", "quick_menu_order.py",
           "quick_menu_native_guard.py", "quick_menu_guard_runtime.py")


def build(*, enable_order=False, output_name="quick-menu-order-trial"):
    if enable_order is not True:
        raise ValueError("Pass --enable-order for this mutating developer trial")
    if not isinstance(output_name, str) or not re.fullmatch(r"quick-menu-[a-z0-9-]{1,64}", output_name):
        raise ValueError("Output must be a simple quick-menu- prefixed directory name")
    output = ROOT / "build" / output_name
    if output.exists():
        raise FileExistsError("Trial output already exists; choose a new output name")
    main = (ROOT / "tools/quick_menu_order_trial.py").read_text(encoding="utf-8")
    if main.count("TRIAL_ENABLED = False") != 1:
        raise ValueError("Expected one disabled ordered submenu trial marker")
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
        "Companion Auto Summon", "Companion Auto Summon ordered submenu trial"
    ).encode("utf-8")
    payload["README.md"] = b"""# Native submenu developer trial

This developer trial adds a Companion Auto Summon submenu with one inert child,
Settings preview. The parent is inserted during native construction before the
first individual pet or pet page, with an end fallback when no pets are listed.
It is not an observation-only probe or the player release.
No settings are applied, no preferences are changed and automatic summoning is
absent. The icon is still borrowed from the native menu; no custom texture is
installed or loaded by this trial.

Close NMS normally, preserve current progress and verify a fresh backup before
starting this isolated trial. Use this folder's Start-CompanionAutoSummon.ps1
with the exact supported executable. The item-specific native binding filter
must be installed before custom entries can be added and remains installed for
the process lifetime, including after a stopped callback. Never hot-reload this
trial, disable/remove its filter or replace its files while NMS is running.

Open the quick menu using your configured control and enter companions. Select
Companion Auto Summon, then inspect Settings preview. Activating this child has
no settings effect. Use the native back control, navigate to neighboring native
entries, close and reopen the menu, and confirm ordinary manual pet actions
still work. Check that repeated openings do not add duplicate entries.

Do not rebind an occupied shortcut during this first navigation test. Shortcut
replay, remapping, controller operation, save/reload/removal and coexistence
remain separate acceptance checks. Visibility alone does not verify them.

Exit NMS normally before closing its pyMHF host. The installed regular mod is
unchanged and can be used through its own launcher in a later game session.
Never copy this trial into GAMEDATA/MODS or over an installed/running version.
"""
    current = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    manifest = {
        "name": "Companion Auto Summon ordered submenu trial",
        "version": "0.6.0-order-trial",
        "framework": current["framework"], "steam_build": current["steam_build"],
        "supported_nms_exe_sha256": current["supported_nms_exe_sha256"],
        "purpose": "One ordered native companion submenu before individual pets, with an inert child and binding filter",
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
        raise RuntimeError("Submenu trial readback failed")
    return {"output": str(output), "files": len(payload), "launched": False,
            "deployed": False, "observation_only": False,
            "trial_sha256": hashlib.sha256(payload["CompanionAutoSummon.py"]).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enable-order", action="store_true")
    parser.add_argument("--output-name", default="quick-menu-order-trial")
    options = parser.parse_args()
    print(json.dumps(build(enable_order=options.enable_order,
                           output_name=options.output_name)))
