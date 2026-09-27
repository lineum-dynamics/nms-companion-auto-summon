"""Check a built two-mod folder with real discovery and no game connection.

Run with pyMHF 0.2.4: python -B tools/play_trial_framework_smoke.py ABSOLUTE_BUNDLE
Only discovery temporarily lifts class disabled flags. All constructors run
outside the game with flags restored and preferences under a temporary path.
"""

import argparse
import hashlib
from importlib import metadata, util
import inspect
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_HOOKS = {
    (0x146AC90, "AFTER"), (0x17479D0, "AFTER"), (0x1479490, "BEFORE"),
    (0x56FA50, "BEFORE"), (0x56FA50, "AFTER"), (0x1440CD0, "AFTER"),
    (0x5066A0, "AFTER"),
}
MENU_HOOKS = {
    (0x151ED00, "BEFORE"), (0x151ED00, "AFTER"), (0x1523220, "AFTER"),
    (0x1526940, "BEFORE"), (0x1526940, "AFTER"), (0x1533980, "BEFORE"),
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def check(bundle_folder):
    sys.dont_write_bytecode = True
    require(metadata.version("pymhf") == "0.2.4", "Use the supported pyMHF environment")
    require(not tuple(metadata.entry_points().select(group="pymhflib")),
            "Additional pyMHF libraries would change discovery")
    bundle = Path(bundle_folder).resolve(strict=True)
    spec = util.spec_from_file_location("cas_play_host_check", bundle / "Launch-CompanionAutoSummon-PlayTrial.py")
    host = util.module_from_spec(spec)
    spec.loader.exec_module(host)
    bundle, config = host.validate_bundle(str(bundle))
    paths = [bundle / name for name in host.PAYLOAD_FILES] + [bundle / "manifest.json"]
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    require((bundle / "CompanionAutoSummon.py").read_bytes() == (ROOT / "CompanionAutoSummon.py").read_bytes(),
            "Production auto-summon source must be byte-identical")
    require((bundle / host.BOOTSTRAP_NAME).read_bytes() == (ROOT / host.BOOTSTRAP_NAME).read_bytes(),
            "Canonical injection bootstrap must be byte-identical")
    require((bundle / host.HOST_NAME).read_bytes() == (ROOT / "tools" / host.HOST_NAME).read_bytes(),
            "Combined host must match its reviewed source")
    menu_source = (ROOT / "tools/quick_menu_order_trial.py").read_text(encoding="utf-8")
    require(menu_source.count("TRIAL_ENABLED = False") == 1, "Expected one disabled menu source flag")
    expected_menu = menu_source.replace("TRIAL_ENABLED = False", "TRIAL_ENABLED = True", 1).encode("utf-8")
    require((bundle / "CompanionMenuOrderTrial.py").read_bytes() == expected_menu,
            "Menu must differ only by its explicit build enable flag")
    for name in host.PAYLOAD_FILES:
        if name.startswith("quick_menu_"):
            require((bundle / name).read_bytes() == (ROOT / "tools" / name).read_bytes(),
                    "Menu helper differs from reviewed source")

    with tempfile.TemporaryDirectory(prefix="cas-play-framework-") as temporary:
        settings_path = Path(temporary) / "NMS-AutoPet/settings.json"
        settings_path.parent.mkdir()
        preferences = {"schema": 3, "enabled": True, "locations": [2, 3],
                       "selection_mode": "random", "prefer_same_biome": False}
        settings_bytes = (json.dumps(preferences) + "\n").encode("utf-8")
        settings_path.write_bytes(settings_bytes)
        with patch.dict(os.environ, {"PYTEST_VERSION": "cas-play-framework", "LOCALAPPDATA": temporary}):
            from pymhf import Mod
            from pymhf.core import _internal, mod_loader
            from pymhf.core.hooking import hook_manager
            import pymhf.main as framework_main

            require(not _internal.IS_INJECTED, "Run this check outside the game")
            manager = mod_loader.ModManager()
            manager.hook_manager = hook_manager
            original_load = manager._load_module
            discovered_files = {}

            def discovery_only(module):
                classes = [value for _, value in inspect.getmembers(module, inspect.isclass)
                           if value is not Mod and issubclass(value, Mod)
                           and inspect.getmodule(value) is module]
                require(len(classes) <= 1, "One file exposes multiple locally defined Mods")
                discovered_files[Path(module.__file__).name] = [cls.__name__ for cls in classes]
                for cls in classes:
                    require(cls._disabled is True, "Outside-game source guard failed")
                    cls._disabled = False
                try:
                    # This executes the unmodified framework predicate and
                    # preload path. It does not construct or register a Mod.
                    return original_load(module)
                finally:
                    for cls in classes:
                        cls._disabled = True

            with patch.object(manager, "_load_module", side_effect=discovery_only), \
                    patch.object(manager, "instantiate_mod", side_effect=AssertionError("No registration")), \
                    patch.object(hook_manager, "register_hook", side_effect=AssertionError("No hooks")), \
                    patch.object(hook_manager, "initialize_hooks", side_effect=AssertionError("No native hooks")), \
                    patch.object(sys, "path", [str(bundle), *sys.path]):
                count, bound = manager.load_mod_folder(str(bundle), bind=False, deep_search=True)
            require((count, bound) == (2, 0), "Folder discovery must preload exactly two Mods and bind nothing")
            require(set(manager._preloaded_mods) == {"CompanionAutoSummon", "CompanionMenuOrderTrial"},
                    "Unexpected discovered Mod identity")
            expected_python = {name for name in host.PAYLOAD_FILES if name.endswith(".py")}
            require(set(discovered_files) == expected_python, "A bundle Python file was not inspected")
            require(sum(len(names) for names in discovered_files.values()) == 2,
                    "Helpers or host files introduced another Mod")
            require(not manager.mods, "Discovery unexpectedly instantiated a Mod")
            production_module = manager._mod_paths["CompanionAutoSummon"]
            menu_module = manager._mod_paths["CompanionMenuOrderTrial"]
            require(production_module is not menu_module and production_module.LOGGER is not menu_module.LOGGER,
                    "Production and menu globals are not isolated")
            require(production_module.CompanionAutoSummon.__init__.__globals__ is production_module.__dict__,
                    "Production class resolved globals from another module")
            require(menu_module.CompanionMenuOrderTrial.before_builder.__globals__ is menu_module.__dict__,
                    "Menu class resolved globals from another module")
            require(menu_module.TRIAL_ENABLED is True and menu_module.CompanionMenuOrderTrial._disabled is True,
                    "Enabled artifact must still refuse native initialization outside game")
            with patch.object(menu_module, "current_process_io", side_effect=AssertionError("No game I/O")), \
                    patch.object(menu_module, "native_adapters", side_effect=AssertionError("No game calls")), \
                    patch.object(menu_module, "ensure_guard", side_effect=AssertionError("No native guard")):
                production = production_module.CompanionAutoSummon()
                menu = menu_module.CompanionMenuOrderTrial()
            require(menu._stopped and menu._guard is None, "Disabled menu constructor was not inert")
            require(production._abc_initialised and menu._abc_initialised, "Framework initialization failed")
            production_hooks = {(hook._hook_offset, hook._hook_time.name) for hook in production.hooks}
            menu_hooks = {(hook._hook_offset, hook._hook_time.name) for hook in menu.hooks}
            require(len(production.hooks) == 7 and production_hooks == PRODUCTION_HOOKS,
                    "Production hook callbacks differ")
            require(len(menu.hooks) == 6 and menu_hooks == MENU_HOOKS, "Menu hook callbacks differ")
            production_targets = {offset for offset, _ in production_hooks}
            menu_targets = {offset for offset, _ in menu_hooks}
            require(not production_targets & menu_targets, "Production and menu targets overlap")
            require(len(production._gui_widgets) == 8 and not menu._gui_widgets,
                    "GUI widget discovery differs")
            require(not production._hotkey_funcs and not menu._hotkey_funcs,
                    "A Mod introduced a physical hotkey")
            require(production.auto_enabled and production.allowed_locations == frozenset((2, 3))
                    and production.selection_mode_value == "random" and not production.prefer_same_biome_value,
                    "Existing preference semantics changed")
            require(production.settings_store.path == settings_path
                    and production.store.path == settings_path.with_name("state.json"),
                    "Stable preference/selection paths changed")
            require(settings_path.read_bytes() == settings_bytes
                    and not settings_path.with_name("state.json").exists(),
                    "Constructors changed local preference/selection data")

            # Exercise host validation and dispatch with the real folder and
            # configuration. Only injection and run_module itself are mocked.
            canonical = host._load_bootstrap(bundle)
            require(Path(canonical.__file__).resolve() == bundle / host.BOOTSTRAP_NAME,
                    "The host did not import the canonical sibling bootstrap")
            order = []
            guard = Mock(side_effect=lambda: order.append("guard"))
            launch = Mock(side_effect=lambda *args: order.append("folder") or "mocked")
            argv_before = sys.argv
            with patch.object(host, "_load_bootstrap", return_value=SimpleNamespace(install_injection_guard=guard)), \
                    patch.object(framework_main, "run_module", launch):
                require(host.main([str(bundle)]) == "mocked", "Host dispatch result changed")
            guard.assert_called_once_with()
            launch.assert_called_once_with(str(bundle), config)
            require(order == ["guard", "folder"] and sys.argv is argv_before,
                    "Host dispatch order or argument lifetime differs")

    require(all(hashlib.sha256(path.read_bytes()).hexdigest() == hashes[path.name] for path in paths),
            "Bundle changed during smoke check")
    result = {
        "version": host.VERSION, "framework": "0.2.4", "pymhflib_entry_points": [],
        "bundle_sha256": hashes, "production_byte_identical": True,
        "menu_only_enable_flag_changed": True, "actual_folder_discovery": True,
        "disabled_flags_lifted_for_discovery_only": True, "mods_preloaded_not_registered": 2,
        "production_callbacks": 7, "menu_callbacks": 6, "distinct_native_targets": 10,
        "gui_widgets": 8, "physical_hotkeys": 0, "temporary_preferences_preserved": True,
        "host_direct_folder_dispatch_mocked": True, "hooks_registered": False,
        "game_accessed": False, "user_preferences_accessed": False, "live_verified": False,
    }
    report = ROOT / "build/validation/menu-play-framework.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle_folder")
    options = parser.parse_args()
    print(json.dumps(check(options.bundle_folder)))
