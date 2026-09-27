"""Exercise the real installed framework with temporary data and no game.

Run with a prepared Python environment containing the required pyMHF GUI extra:
    python -B tools/framework_smoke.py
This check imports pyMHF but never invokes its launcher or registers hooks.
"""

from datetime import datetime, timezone
import hashlib
from importlib.metadata import version as installed_version
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIRECTORY = ROOT / "build" / "validation"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    sys.dont_write_bytecode = True
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    package_version = manifest["version"]
    require(re.fullmatch(r"\d+\.\d+\.\d+-experimental", package_version),
            "Expected an explicit experimental version in manifest.json")
    version = package_version.removesuffix("-experimental")
    requirement = manifest["framework"]
    match = re.fullmatch(r"pymhf\[gui\]==([0-9.]+)", requirement)
    require(match is not None, "Expected an exact pyMHF GUI requirement")
    framework_version = installed_version("pymhf")
    gui_version = installed_version("dearpygui")
    require(framework_version == match.group(1), "Installed pyMHF does not match manifest.json")
    source = ROOT / "AutoPet.py"
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()

    # The framework's test-mode guard skips interactive prompt construction.
    # Temporary LOCALAPPDATA prevents access to the user's real preferences.
    with tempfile.TemporaryDirectory(prefix="autopet-framework-smoke-") as directory:
        with patch.dict(os.environ, {"PYTEST_VERSION": "autopet-offline-smoke", "LOCALAPPDATA": directory}):
            from pymhf.core import _internal
            from pymhf.gui.widgets import Widget
            import dearpygui.dearpygui as dpg

            require(not _internal.IS_INJECTED, "This check must run outside the game")
            spec = importlib.util.spec_from_file_location("autopet_offline_framework_smoke", source)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            require(module.AutoPet._disabled, "AutoPet must be disabled outside the game")
            require(module.EXPECTED_PYMHF == framework_version, "Generated mod framework requirement differs")
            mod = module.AutoPet()
            require(len(mod._gui_widgets) == 8, "Expected eight GUI widgets")
            require(len(mod._hotkey_funcs) == 0, "No AutoPet hotkeys should be registered")
            require(mod.automatic_summoning and mod.planets and mod.space_stations and mod.nexus,
                    "Default location controls differ")
            require(mod.companion_selection.name == "Last manually selected" and mod.prefer_same_biome,
                    "Default companion controls differ")
            dpg.create_context()
            try:
                mapping = {}
                with dpg.window(show=False):
                    for func in mod._gui_widgets:
                        widget = Widget.create(func, mapping)
                        widget._draw(mapping)
                    widget._force_end_table()
                widgets = {widget.variable_name: widget for widget in mapping.values()}
                dropdown = widgets["companion_selection"]
                require(dpg.get_item_configuration(dropdown.ids["INPUT"])["items"] == [
                    "Last manually selected", "Random"], "Selection labels differ")
                require(dpg.get_value(dropdown.id_) == "Last manually selected", "Selection default differs")
                dropdown.update_variable(None, "Random", (mod, "companion_selection"))
                for name in ("automatic_summoning", "planets", "space_stations", "nexus", "prefer_same_biome"):
                    widgets[name].update_variable(None, False, (mod, name))
                require(mod.auto_enabled and not mod.automatic_summoning, "Enabled change was not queued")
                require(mod.allowed_locations == frozenset({2, 3, 14})
                        and not mod.planets and not mod.space_stations and not mod.nexus,
                        "Location changes were not queued")
                require(mod.selection_mode_value == "last_manual"
                        and mod.companion_selection.value == "random", "Selection change was not queued")
                require(not mod.prefer_same_biome and mod._current_preferences()["prefer_same_biome"],
                        "Biome change was not queued")
            finally:
                dpg.destroy_context()
            require(not list(Path(directory).rglob("*.json")), "GUI callbacks wrote files before apply")
            # Pure control resolution writes only temporary JSON. No player or
            # ownership callback, native wrapper, hook manager, or launcher runs.
            mod._apply_control()
            stored = json.loads((Path(directory) / "NMS-AutoPet/settings.json").read_text())
            require(stored == {"schema": 3, "enabled": False, "locations": [],
                               "selection_mode": "random", "prefer_same_biome": False},
                    "Applied preference data differs")
            require(not mod.auto_enabled and mod.allowed_locations == frozenset()
                    and mod.selection_mode_value == "random", "Applied runtime preferences differ")
            require(hashlib.sha256(source.read_bytes()).hexdigest() == source_hash,
                    "Generated source changed during framework smoke check")
            record = {
                "version": version,
                "package_version": package_version,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "framework_requirement": requirement,
                "framework_version": framework_version,
                "dearpygui_version": gui_version,
                "disabled_outside_game": True,
                "hooks_discovered_not_registered": len(mod.hooks),
                "gui_widgets": len(mod._gui_widgets),
                "hotkeys": len(mod._hotkey_funcs),
                "actual_gui_widget_construction_and_callbacks_passed": True,
                "actual_framework_import_passed": True,
                "generated_source_sha256": source_hash,
            }
    REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    (REPORT_DIRECTORY / f"framework-{version}.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
