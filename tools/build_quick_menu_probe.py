"""Build an isolated, explicitly enabled menu observer; never launch the game.

The production mod, installed test copy and personal settings are not modified.
The generated filenames reuse the existing guarded launcher contract. No
diagnostic performs automatic summoning. Existing output folders are immutable
to this builder, including a folder whose observer may still be running.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
STAGES = {
    "actions": {
        "source": "quick_menu_probe.py", "version": "0.1.0-observer",
        "output": "quick-menu-probe", "class": "CompanionMenuProbe",
        "purpose": "Observe existing quick-menu action IDs and depth; no custom menu or auto-summon",
        "scope": "Its single before-hook copies action IDs and depth, capped at 64 events.",
    },
    "structure": {
        "source": "quick_menu_structure_probe.py", "version": "0.2.0-observer",
        "output": "quick-menu-structure-probe", "class": "CompanionMenuStructureProbe",
        "purpose": "Observe natural menu construction and label lengths; no writes or auto-summon",
        "scope": "Its after-hooks sample bounded menu headers, selected enums and label lengths.\n"
                 "Label text, pet names, pointers and identity values are never logged.",
    },
    "phases": {
        "source": "quick_menu_phase_probe.py", "version": "0.3.0-observer",
        "output": "quick-menu-phase-probe", "class": "CompanionMenuPhaseProbe",
        "purpose": "Observe menu-local phase order and selection stability; no input or game writes",
        "scope": "Its four callbacks track natural update, controls and tail-processing phases.\n"
                 "It does not inspect physical keys, mask selection, bind shortcuts or insert items.",
    },
}


def build(*, enable_observer=False, stage="actions", output_name=None):
    if not enable_observer:
        raise ValueError("Pass --enable-observer to build the isolated diagnostic artifact")
    if stage not in STAGES:
        raise ValueError("Unknown observer stage")
    profile = STAGES[stage]
    name = profile["output"] if output_name is None else output_name
    if not isinstance(name, str) or not re.fullmatch(r"quick-menu-[a-z0-9-]{1,64}", name):
        raise ValueError("Output name must be a simple quick-menu- prefixed directory name")
    output = ROOT / "build" / name
    if output.exists():
        raise FileExistsError("Observer output already exists; choose a new --output-name")
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    source = (ROOT / "tools" / profile["source"]).read_text(encoding="utf-8")
    marker = "PROBE_ENABLED = False"
    if source.count(marker) != 1:
        raise ValueError("Expected exactly one disabled observer build marker")
    source = source.replace(marker, "PROBE_ENABLED = True")
    compile(source, profile["class"], "exec")
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
        "version": profile["version"],
        "framework": manifest["framework"],
        "steam_build": manifest["steam_build"],
        "supported_nms_exe_sha256": manifest["supported_nms_exe_sha256"],
        "purpose": profile["purpose"],
        "live_verified": False,
        "files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest()}
                  for name, data in payload.items()],
    }
    payload["manifest.json"] = (json.dumps(probe_manifest, indent=2) + "\n").encode("utf-8")
    payload["README.md"] = ("""# Isolated quick-menu observer

This is a development diagnostic, not the Companion Auto Summon player package.
It does not summon companions, change preferences, insert menu entries or open
game-save files. All callbacks return without changing native arguments/results.
""" + profile["scope"] + """

Close No Man's Sky and preserve current progress before testing. Verify a fresh
save backup when needed. Then use Start-CompanionAutoSummon.ps1 from this folder.
The existing launcher checks the package, exact game build and runtime. The
framework injects the observer and logs to this folder's logs directory.

Load a save, open the quick menu using your configured control, enter the
companion section and its summon list, back out, then close and reopen the menu.
You may manually summon an owned companion. No shortcut reassignment is needed.
Do not expect a new item yet. A read or validation failure disables further
observation for the session. High-frequency structure observations are sampled
and capped; the structure probe records lengths, not the actual label text.

Finish by exiting the game normally before closing its runtime host. To resume
the regular auto-summon test, use that installation's launcher on the next run.
Do not copy this diagnostic over the installed mod or into GAMEDATA/MODS.
""").encode("utf-8")
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        (output / name).write_bytes(data)
    if not all((output / name).read_bytes() == data for name, data in payload.items()):
        raise RuntimeError("Observer artifact readback failed")
    return {"output": str(output), "stage": stage, "files": len(payload), "deployed": False,
            "launched": False, "probe_sha256": hashlib.sha256(payload["CompanionAutoSummon.py"]).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enable-observer", action="store_true",
                        help="Build the explicitly enabled, isolated observer artifact")
    parser.add_argument("--stage", choices=STAGES, default="actions",
                        help="Choose action dispatch, structure/labels, or menu-local phase observation")
    parser.add_argument("--output-name", help="New quick-menu- prefixed directory under build/")
    args = parser.parse_args()
    print(json.dumps(build(enable_observer=args.enable_observer, stage=args.stage,
                           output_name=args.output_name)))


if __name__ == "__main__":
    main()
