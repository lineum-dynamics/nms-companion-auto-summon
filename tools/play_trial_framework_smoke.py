"""Check a built two-mod folder with real discovery and no game connection.

Run with pyMHF 0.2.4: python -B tools/play_trial_framework_smoke.py ABSOLUTE_BUNDLE
Only discovery temporarily lifts class disabled flags. All constructors run
outside the game with flags restored and preferences under a temporary path.
"""

import argparse
import ctypes as C
from contextlib import contextmanager
from functools import wraps
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
    (0x1526940, "BEFORE"), (0x1526940, "AFTER"),
}
MENU_HOOKS = {
    (0x151ED00, "BEFORE"), (0x151ED00, "AFTER"), (0x1523220, "AFTER"),
    (0x1526940, "BEFORE"), (0x1526940, "AFTER"), (0x1533980, "BEFORE"),
    (0x15311C0, "BEFORE"), (0x15311C0, "AFTER"),
    (0x151AD80, "AFTER"),
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def check_shared_dispatch(production, menu, hooking):
    """Use real Python registration/dispatch, with no native hook binding.

    cyminhook's original attribute is read-only. Override only that attribute
    and binding in a local subclass; retain the real FuncHook initializer,
    detour lists and compound dispatcher. The actual callbacks run on an owned
    inert item. The menu instance remains disabled, so this does not establish
    active menu/native integration or manual-action gameplay behavior.
    """
    class UnboundFuncHook(hooking.FuncHook):
        @property
        def original(self):
            return self._smoke_original

        def bind(self):
            raise AssertionError("No native binding in shared-dispatch smoke")

    evidence = []
    item = C.create_string_buffer(224)  # Native None action: no app/pet reads.
    menu_storage = C.create_string_buffer(8)
    for owners in (("production", "menu"), ("menu", "production")):
        registry = hooking.HookManager()
        events = []
        shared_callbacks = []
        instances = {"production": production, "menu": menu}

        def instrument(callback, owner):
            phase = callback._hook_time.name

            @wraps(callback)
            def observed(*args, **kwargs):
                events.append((owner, phase, args, kwargs))
                result = callback(*args, **kwargs)
                require(result is None, "A shared callback changed native arguments or result")
                return result

            return observed

        with patch.object(hooking, "FuncHook", UnboundFuncHook), \
                patch.object(hooking, "_get_binary_info", return_value=None), \
                patch.object(registry, "initialize_hooks", side_effect=AssertionError("No native hooks")):
            for owner in owners:
                for callback in instances[owner].hooks:
                    if callback._hook_offset == 0x1526940:
                        definition = callback._hook_func_def
                        require(definition.restype is C.c_bool
                                and definition.argtypes == [C.c_void_p, C.c_void_p, C.c_bool],
                                "Shared TriggerAction declarations disagree on ABI")
                        callback = instrument(callback, owner)
                        shared_callbacks.append(callback)
                    registry.register_hook(callback)
        require(len(registry.hooks) == 12 and not registry.failed_hooks,
                "Python registry did not merge exactly the shared target")
        targets = [hook for key, hook in registry.hooks.items() if key.offset == 0x1526940]
        require(len(targets) == 1, "Shared TriggerAction created multiple function hooks")
        merged = targets[0]
        require(len(merged._before_detours) == 2 and not merged._after_detours
                and len(merged._after_detours_with_results) == 2
                and not merged._has_noop and not merged._disabled_detours,
                "Shared detour phases or original-call policy differ")
        require(set(merged._before_detours + merged._after_detours_with_results)
                == set(shared_callbacks), "Shared callbacks were lost during registration")
        require(all(hook.state is None for hook in registry.hooks.values()),
                "A Python-only registry hook was unexpectedly bound")
        for native_result in (False, True):
            for called_as_menu in (False, True):
                events.clear()
                args = (C.addressof(menu_storage), C.addressof(item), called_as_menu)

                def original(*received):
                    events.append(("original", "CALL", received, {}))
                    return native_result

                merged._smoke_original = Mock(side_effect=original)
                result = merged._compound_detour(*args)
                merged._smoke_original.assert_called_once_with(*args)
                require(result is native_result, "Compound dispatch replaced the original Boolean")
                expected_order = ([(owner, "BEFORE") for owner in owners]
                                  + [("original", "CALL")]
                                  + [(owner, "AFTER") for owner in owners])
                require([(owner, phase) for owner, phase, _, _ in events] == expected_order,
                        "Compound dispatch lost or reordered a shared callback")
                require(all(received == args for _, _, received, _ in events),
                        "Compound dispatch changed callback arguments")
                require(all(kwargs == {"_result_": native_result}
                            for _, phase, _, kwargs in events if phase == "AFTER"),
                        "A shared AFTER callback did not receive the native result")
                require(not merged._disabled_detours and production._manual_attribution_ok
                        and production._manual_action is None and menu._stopped,
                        "Inert shared dispatch failed or changed activation state")
        evidence.append({"registration_order": list(owners), "python_targets": len(registry.hooks),
                         "shared_before": 2, "shared_after_with_result": 2,
                         "argument_result_cases": 4, "native_original": "mocked_once_per_case"})
    return evidence


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
    require(menu_source.count("SETTINGS_TOGGLE_ENABLED = False") == 1, "Expected disabled toggle source")
    expected_menu = menu_source.replace("TRIAL_ENABLED = False", "TRIAL_ENABLED = True", 1)
    for flag in ("SETTINGS_TOGGLE_ENABLED", "EXTENDED_SETTINGS_ENABLED", "CUSTOM_ICON_ENABLED"):
        require(menu_source.count(flag + " = False") == 1, "Expected one disabled feature flag")
        expected_menu = expected_menu.replace(flag + " = False", flag + " = True", 1)
    expected_menu = expected_menu.encode("utf-8")
    require((bundle / "CompanionMenuOrderTrial.py").read_bytes() == expected_menu,
            "Menu must differ only by its four explicit build enable flags")
    require((bundle / "SETTINGS.DDS").read_bytes() == (ROOT / "assets/ui/SETTINGS.DDS").read_bytes(),
            "Packaged original icon differs from its source")
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
            from pymhf.core import hooking
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
            require(len(production.hooks) == 9 and production_hooks == PRODUCTION_HOOKS,
                    "Production hook callbacks differ")
            require(len(menu.hooks) == 9 and menu_hooks == MENU_HOOKS, "Menu hook callbacks differ")
            production_targets = {offset for offset, _ in production_hooks}
            menu_targets = {offset for offset, _ in menu_hooks}
            require(production_targets & menu_targets == {0x1526940},
                    "Only TriggerAction may be shared between production and menu")
            shared_dispatch = check_shared_dispatch(production, menu, hooking)
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

            # Exercise the bridge with the actual framework-created Python
            # instance and temporary settings. This never registers a hook or
            # calls a native function; application below is an offline method
            # invocation, not an injected player update.
            bridge = menu_module.PreferenceBridge(
                str(bundle / "CompanionAutoSummon.py"),
                get_registered=lambda: menu_module.mod_manager.mods.get("CompanionAutoSummon"),
                get_module=lambda: sys.modules.get("CompanionAutoSummon"),
            )
            with patch.object(production_module.CompanionAutoSummon, "_disabled", False), \
                    patch.dict(menu_module.mod_manager.mods, {"CompanionAutoSummon": production}):
                state = bridge.snapshot()
                require(state is not None and state.applied and state.desired and not state.pending,
                        "Bridge did not resolve the actual registered production instance")
                token = bridge.capture_toggle()
                require(bridge.commit_toggle(token, authorize=lambda: True), "Native toggle was not queued")
                require(not bridge.commit_toggle(token), "Native token replay queued another toggle")
                state = bridge.snapshot()
                require(state.applied and not state.desired and state.pending,
                        "Queued state was confused with applied state")
                require(settings_path.read_bytes() == settings_bytes, "Bridge persisted before player apply")
                production._apply_control()
                stored = json.loads(settings_path.read_text(encoding="utf-8"))
                require(stored == {**preferences, "enabled": False}, "Toggle changed another stored setting")
                state = bridge.snapshot()
                require(not state.applied and not state.desired and not state.pending and state.settings_ok,
                        "Applied bridge state differs")
                # Exercise every additional row against the real Mod instance
                # and the existing production persistence path. Each result
                # must change exactly one preference and preserve the others.
                for key in ("selection_mode", "prefer_same_biome", "planets", "space_stations", "nexus"):
                    before = bridge.snapshot(key)
                    token = bridge.capture_toggle(key)
                    require(before is not None and token is not None,
                            f"Bridge cannot capture {key}")
                    require(bridge.commit_toggle(token, authorize=lambda: True),
                            f"Bridge cannot queue {key}")
                    require(not bridge.commit_toggle(token), f"Replayed {key} was accepted")
                    pending = bridge.snapshot(key)
                    require(pending.pending and pending.applied == before.applied,
                            f"{key} applied before player update")
                    require(json.loads(settings_path.read_text(encoding="utf-8")) == stored,
                            f"{key} persisted before player update")
                    expected = dict(stored)
                    if key in ("selection_mode", "prefer_same_biome"):
                        expected[key] = pending.desired
                    else:
                        location = {"planets": 3, "space_stations": 2, "nexus": 14}[key]
                        locations = set(stored["locations"])
                        locations.add(location) if pending.desired else locations.discard(location)
                        expected["locations"] = sorted(locations)
                    production._apply_control()
                    stored = json.loads(settings_path.read_text(encoding="utf-8"))
                    require(stored == expected, f"{key} changed another stored preference")
                    applied = bridge.snapshot(key)
                    require(applied.applied == pending.desired and not applied.pending and applied.settings_ok,
                            f"{key} did not apply through production")
                provider = Mock(return_value=0)
                require(bridge.bind_notice_icon(provider), "Icon provider could not bind")
                require(bridge.bind_notice_icon(provider), "Same icon provider could not rebind")
                provider.assert_not_called()
                require(production._notice_icon_handle() == 0, "Text fallback changed")
                provider.assert_called_once_with()
                require(not settings_path.with_name("state.json").exists(), "Bridge changed companion memory")

            # Exercise host validation and dispatch with the real folder and
            # configuration. Only injection and run_module itself are mocked.
            canonical = host._load_bootstrap(bundle)
            require(Path(canonical.__file__).resolve() == bundle / host.BOOTSTRAP_NAME,
                    "The host did not import the canonical sibling bootstrap")
            order = []
            guard = Mock(side_effect=lambda: order.append("guard"))
            launch = Mock(side_effect=lambda *args: order.append("folder") or "mocked")
            argv_before = sys.argv
            asset_setup = Mock(side_effect=lambda *args: order.append("asset"))
            @contextmanager
            def owned_lease():
                order.append("lease")
                try:
                    yield
                finally:
                    order.append("release")
            with patch.object(host, "_load_bootstrap", return_value=SimpleNamespace(
                    install_injection_guard=guard, launcher_session=owned_lease)), \
                    patch.object(host, "_prepare_icon_asset", asset_setup), \
                    patch.object(host, "_game_closed", return_value=True), \
                    patch.object(framework_main, "run_module", launch):
                require(host.main([str(bundle), "--game-directory", str(Path(temporary) / "game")]) == "mocked",
                        "Host dispatch result changed")
            guard.assert_called_once_with()
            launch.assert_called_once_with(str(bundle), config)
            require(order == ["lease", "guard", "asset", "folder", "release"] and sys.argv is argv_before,
                    "Host dispatch order or argument lifetime differs")

    require(all(hashlib.sha256(path.read_bytes()).hexdigest() == hashes[path.name] for path in paths),
            "Bundle changed during smoke check")
    result = {
        "version": host.VERSION, "framework": "0.2.4", "pymhflib_entry_points": [],
        "bundle_sha256": hashes, "production_byte_identical": True,
        "menu_only_four_enable_flags_changed": True, "actual_folder_discovery": True,
        "disabled_flags_lifted_for_discovery_only": True, "mods_preloaded_not_registered": 2,
        "production_callbacks": 9, "menu_callbacks": 9, "distinct_native_targets": 12,
        "shared_target": "0x1526940", "shared_python_registry_and_dispatch": shared_dispatch,
        "shared_dispatch_owned_none_item_menu_disabled": True,
        "native_hook_binding_performed": False,
        "gui_widgets": 8, "physical_hotkeys": 0, "temporary_preferences_preserved_before_apply": True,
        "real_preference_bridge_queue_apply_verified": True,
        "real_preference_bridge_all_six_settings_verified": True,
        "real_optional_icon_provider_binding_verified": True,
        "host_direct_folder_dispatch_mocked": True, "hooks_registered": False,
        "game_accessed": False, "user_preferences_accessed": False, "live_verified": False,
    }
    report = ROOT / "build/validation" / f"menu-play-{host.VERSION}-framework.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle_folder")
    options = parser.parse_args()
    print(json.dumps(check(options.bundle_folder)))
