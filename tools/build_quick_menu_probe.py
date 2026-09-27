"""Build an isolated, explicitly enabled menu observer; never launch the game.

The production mod, installed test copy and personal settings are not modified.
The generated filenames reuse the existing guarded launcher contract, but the
single Mod class is CompanionMenuProbe and performs no automatic summoning.
"""

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build" / "quick-menu-probe"


def build(*, enable_observer=False):
    if not enable_observer:
        raise ValueError("Pass --enable-observer to build the isolated diagnostic artifact")
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    source = (ROOT / "tools" / "quick_menu_probe.py").read_text(encoding="utf-8")
    marker = "PROBE_ENABLED = False"
    if source.count(marker) != 1:
        raise ValueError("Expected exactly one disabled observer build marker")
    source = source.replace(marker, "PROBE_ENABLED = True")
    compile(source, "CompanionMenuProbe", "exec")
    bootstrap = (ROOT / "Launch-CompanionAutoSummon.py").read_bytes()
    launcher = (ROOT / "Start-CompanionAutoSummon.ps1").read_text(encoding="utf-8")
    launcher = launcher.replace("Companion Auto Summon", "Companion Auto Summon menu observer")
    payload = {
        "CompanionAutoSummon.py": source.encode("utf-8"),
        "Launch-CompanionAutoSummon.py": bootstrap,
        "Start-CompanionAutoSummon.ps1": launcher.encode("utf-8"),
    }
    probe_manifest = {
        "name": "Companion Auto Summon menu observer",
        "version": "0.1.0-observer",
        "framework": manifest["framework"],
        "steam_build": manifest["steam_build"],
        "supported_nms_exe_sha256": manifest["supported_nms_exe_sha256"],
        "purpose": "Observe existing quick-menu action IDs and depth; no custom menu or auto-summon",
        "live_verified": False,
        "files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest()}
                  for name, data in payload.items()],
    }
    payload["manifest.json"] = (json.dumps(probe_manifest, indent=2) + "\n").encode("utf-8")
    payload["README.md"] = b"""# Isolated quick-menu observer

This is a development diagnostic, not the Companion Auto Summon player package.
It does not summon companions, change preferences, insert menu entries or open
game-save files. Its one before-hook returns without changing native arguments.
Only bounded action IDs, menu depth and the called-as-menu flag are logged.

Close No Man's Sky and preserve current progress before testing. Verify a fresh
save backup when needed. Then use Start-CompanionAutoSummon.ps1 from this folder.
The existing launcher checks the package, exact game build and runtime. The
framework injects the observer and logs to this folder's logs directory.

Load a save, open X, open the companion section and its summon list, back out,
close and reopen the menu, then manually summon one owned companion if desired.
Do not expect a new item yet. At most 64 action observations are recorded; a read
or validation failure disables further observation for the session.

Finish by exiting the game normally before closing its runtime host. To resume
the regular auto-summon test, use that installation's launcher on the next run.
Do not copy this diagnostic over the installed mod or into GAMEDATA/MODS.
"""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, data in payload.items():
        (OUTPUT / name).write_bytes(data)
    if not all((OUTPUT / name).read_bytes() == data for name, data in payload.items()):
        raise RuntimeError("Observer artifact readback failed")
    return {"output": str(OUTPUT), "files": len(payload), "deployed": False,
            "launched": False, "probe_sha256": hashlib.sha256(payload["CompanionAutoSummon.py"]).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enable-observer", action="store_true",
                        help="Build the explicitly enabled, isolated observer artifact")
    args = parser.parse_args()
    print(json.dumps(build(enable_observer=args.enable_observer)))


if __name__ == "__main__":
    main()
