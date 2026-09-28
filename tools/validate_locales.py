"""Offline validation of scoped translation drafts; never imports the runtime.

This checks catalog structure, English source fingerprints and current English
presentation. It does not select a language, render glyphs or validate wording.
"""

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from string import Formatter
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("en", "fr", "it", "de", "es-ES", "nl", "ja", "ko", "pl", "pt-PT",
           "pt-BR", "ru", "zh-Hans", "zh-Hant")
MENU_KEYS = ("menu.automation", "menu.selection", "menu.biome", "menu.planets",
             "menu.space_stations", "menu.space_anomaly", "menu.rotate_companions")
TECHNOLOGY_KEYS = ("tech.link.name", "tech.link.subtitle", "tech.link.description",
                   "tech.recharger.name", "tech.recharger.subtitle", "tech.recharger.description")
LAUNCHER_KEYS = ("launcher.blocked_title", "launcher.unsupported_game", "launcher.unreadable_game",
                "launcher.game_required", "launcher.invalid_package", "launcher.wrong_framework",
                "launcher.game_changed", "launcher.game_running", "launcher.preflight_passed")
PRODUCT_KEYS = ("product.full_name", "product.author_credit")
PORTABLE_KEYS = ("portable.start", "portable.check", "portable.choose_game", "portable.ready",
                 "portable.checking", "portable.starting", "portable.started", "portable.close",
                 "portable.backup_failed", "portable.runtime_invalid", "portable.game_choice_required",
                 "portable.check_passed", "portable.check_failed", "portable.check_timeout",
                 "portable.native_runtime_missing", "portable.steam_required", "portable.start_failed")
SCOPE = "native_menu_hud_technology_launcher_panel"
KEYS = frozenset(("menu.parent_title", *MENU_KEYS, "value.on", "value.off",
                  "value.last_selected", "value.random", "value.by_habitat", "status.pending",
                  "status.session_only", "status.unavailable", "status.stopped",
                  "format.setting", "format.with_status", "hud.settings_applied",
                  "hud.setting_separator", "hud.session_suffix", "hud.companion_saved",
                  "hud.companion_session", "hud.auto_off_suffix", "hud.random_on_suffix", "hud.habitat_on_suffix",
                  "hud.no_suitable_habitat", "panel.habitat_status",
                  *TECHNOLOGY_KEYS, *LAUNCHER_KEYS, *PRODUCT_KEYS, *PORTABLE_KEYS))
UNCHANGED_ALLOWED = frozenset(("menu.parent_title", "format.setting", "format.with_status",
                               "hud.settings_applied", "hud.setting_separator", "product.full_name"))
TOP_KEYS = frozenset(("schema_version", "locale", "scope", "review_status",
                     "native_runtime_integrated", "unchanged_keys", "messages"))
MAX_TEXT_BYTES = 1024  # Catalog bound, not a promise about native buffer/glyph support.
MAX_FILE_BYTES = 65536


class CatalogError(ValueError):
    """The reviewed catalog/source contract does not match."""


def _require(condition, message):
    if not condition:
        raise CatalogError(message)


def source_fingerprint(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def _placeholders(text):
    try:
        result = Counter()
        for _literal, field, spec, conversion in Formatter().parse(text):
            if field is not None:
                _require(re.fullmatch(r"[a-z][a-z_]*", field) is not None
                         and not spec and conversion is None,
                         "Only simple named text placeholders are supported")
                result[field] += 1
        return result
    except ValueError as error:
        raise CatalogError("Malformed named placeholders") from error


def _read_catalog(path, code):
    try:
        data = path.read_bytes()
        _require(len(data) <= MAX_FILE_BYTES, "Catalog file exceeds its bound")
        catalog = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CatalogError(f"Cannot read catalog {code}") from error
    _require(type(catalog) is dict and set(catalog) == TOP_KEYS, f"Invalid {code} catalog fields")
    _require(type(catalog["schema_version"]) is int and catalog["schema_version"] == 1
             and catalog["locale"] == code and catalog["scope"] == SCOPE
             and catalog["native_runtime_integrated"] is False,
             f"Invalid {code} metadata or unsupported integration claim")
    _require(catalog["review_status"] == ("canonical" if code == "en" else "draft_unreviewed"),
             f"Invalid {code} review status; human review is not established")
    messages = catalog["messages"]
    _require(type(messages) is dict and set(messages) == KEYS, f"Missing or extra {code} message keys")
    for key, entry in messages.items():
        _require(type(entry) is dict and set(entry) == {"text", "source_sha256"}, f"Invalid {code}:{key} entry")
        text = entry["text"]
        _require(type(text) is str and bool(text.strip()) and not any(ord(char) < 32 for char in text),
                 f"Invalid {code}:{key} text")
        try:
            encoded = text.encode("utf-8")
        except UnicodeError as error:
            raise CatalogError(f"Invalid Unicode in {code}:{key}") from error
        _require(len(encoded) <= MAX_TEXT_BYTES, f"Oversized {code}:{key} text")
        _require(type(entry["source_sha256"]) is str
                 and re.fullmatch(r"[0-9a-f]{64}", entry["source_sha256"]),
                 f"Invalid {code}:{key} source fingerprint")
        _placeholders(text)
    unchanged = catalog["unchanged_keys"]
    _require(type(unchanged) is list and all(type(key) is str for key in unchanged)
             and len(set(unchanged)) == len(unchanged)
             and set(unchanged) <= UNCHANGED_ALLOWED, f"Invalid {code} unchanged-key declarations")
    return catalog


def _tree(path):
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeError) as error:
        raise CatalogError(f"Cannot inspect source {path.name}") from error


def _assignment(tree, name):
    matches = [node.value for node in tree.body if isinstance(node, ast.Assign)
               and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
               and node.targets[0].id == name]
    _require(len(matches) == 1, f"Expected one source assignment: {name}")
    return ast.literal_eval(matches[0])


def _function(tree, name):
    found = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name]
    _require(len(found) == 1, f"Expected one source function: {name}")
    return found[0]


def _menu_renderer(tree):
    """Execute only the audited pure text function, without module imports."""
    function = _function(tree, "preference_label")
    for node in ast.walk(function):
        _require(not isinstance(node, (ast.Import, ast.ImportFrom, ast.For, ast.While,
                                      ast.With, ast.Try, ast.Global, ast.Nonlocal)),
                 "Menu text source requires a new offline audit")
        if isinstance(node, ast.Call):
            allowed = (isinstance(node.func, ast.Name)
                       and node.func.id in {"setting_key", "type", "MenuItemError"})
            allowed |= (isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "item" and node.func.attr == "encode_label")
            _require(allowed, "Unexpected operation in pure menu text source")
        if isinstance(node, ast.Attribute):
            _require(isinstance(node.value, ast.Name)
                     and ((node.value.id == "state" and node.attr in {"desired", "pending", "settings_ok", "stopped"})
                          or (node.value.id == "item" and node.attr == "encode_label")),
                     "Unexpected data access in pure menu text source")
    namespace = {"__builtins__": {"type": type, "str": str, "bool": bool},
                 "SETTING_LABELS": _assignment(tree, "SETTING_LABELS"),
                 "setting_key": lambda role: role, "MenuItemError": CatalogError,
                 "item": SimpleNamespace(encode_label=lambda value: value.encode("ascii"))}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "<scoped-menu-text>", "exec"), namespace)
    return namespace["preference_label"]


def _notice_assignments(function, name):
    return [node.value for node in ast.walk(function) if isinstance(node, ast.Assign)
            and len(node.targets) == 1 and (
                isinstance(node.targets[0], ast.Name) and node.targets[0].id == name
                or isinstance(node.targets[0], ast.Attribute) and name == "self.pending_notice"
                and isinstance(node.targets[0].value, ast.Name) and node.targets[0].value.id == "self"
                and node.targets[0].attr == "pending_notice")]


def _evaluate_notice(expression, environment):
    allowed = (ast.Constant, ast.Name, ast.Load, ast.Attribute, ast.IfExp, ast.Compare,
               ast.NotEq, ast.Eq, ast.Subscript, ast.JoinedStr, ast.FormattedValue,
               ast.BinOp, ast.Add)
    _require(all(isinstance(node, allowed) for node in ast.walk(expression)),
             "HUD text source requires a new offline audit")
    return eval(compile(ast.Expression(expression), "<scoped-hud-text>", "eval"),
                {"__builtins__": {}}, environment)


def _settings_notice_renderer(tree):
    """Run only the audited pure formatter, never import the game runtime."""
    function = _function(tree, "settings_change_notice")
    for node in ast.walk(function):
        _require(not isinstance(node, (ast.Import, ast.ImportFrom, ast.While, ast.With,
                                      ast.Try, ast.Global, ast.Nonlocal, ast.Lambda,
                                      ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)),
                 "Settings notice source requires a new offline audit")
        if isinstance(node, ast.For):
            _require(isinstance(node.iter, ast.Name) and node.iter.id == "SETTINGS_NOTICE_LABELS",
                     "Settings notice must iterate the bounded label list")
        if isinstance(node, ast.Call):
            allowed = isinstance(node.func, ast.Name) and node.func.id in {"len", "ValueError"}
            if isinstance(node.func, ast.Attribute):
                allowed |= (isinstance(node.func.value, ast.Name)
                            and (node.func.value.id, node.func.attr) in {("changes", "append"), ("notice", "encode")})
                allowed |= isinstance(node.func.value, ast.Constant) and type(node.func.value.value) is str and node.func.attr == "join"
            _require(allowed, "Unexpected operation in settings notice formatter")
        if isinstance(node, ast.Attribute):
            _require((isinstance(node.value, ast.Name)
                      and (node.value.id, node.attr) in {("changes", "append"), ("notice", "encode")})
                     or isinstance(node.value, ast.Constant) and type(node.value.value) is str and node.attr == "join",
                     "Unexpected data access in settings notice formatter")
    namespace = {"__builtins__": {"len": len, "ValueError": ValueError}}
    for name in ("SETTINGS_NOTICE_LABELS", "SETTINGS_NOTICE_LOCATIONS", "SETTINGS_NOTICE_MODES"):
        namespace[name] = _assignment(tree, name)
    exec(compile(ast.Module(body=[function], type_ignores=[]), "<scoped-settings-notice>", "exec"), namespace)
    return namespace["settings_change_notice"]


def _check_sources(english, source_root):
    compatibility = _tree(source_root / "cas_compatibility.py")
    _require(_assignment(compatibility, "WARNING_KEYS") == LAUNCHER_KEYS,
             "Launcher warning keys differ from catalog scope")
    _require(_assignment(compatibility, "WARNING_FALLBACKS") == {
        "launcher.blocked_title": english["launcher.blocked_title"],
        "launcher.invalid_package": english["launcher.invalid_package"]},
        "Launcher recovery fallback differs from English catalog")
    try:
        powershell = (source_root / "Start-CompanionAutoSummon.ps1").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise CatalogError("Cannot inspect source Start-CompanionAutoSummon.ps1") from error
    _require(len(powershell) <= 100_000, "PowerShell launcher exceeds source-check bound")
    for variable, key in (("fallbackTitle", "launcher.blocked_title"),
                          ("fallbackBody", "launcher.invalid_package")):
        values = re.findall(r"^[ \t]*\$" + variable + r"[ \t]*=[ \t]*'((?:[^'\r\n]|'')*)'[ \t]*$",
                            powershell, re.MULTILINE | re.IGNORECASE)
        values = [value.replace("''", "'") for value in values]
        _require(values == [english[key]], "PowerShell recovery fallback differs from English catalog")
    calls = re.findall(r"(?:Throw-LauncherCompatibility|Get-LauncherMessage)\s+-Key\s+(['\"])([^'\"\r\n]*)\1",
                       powershell, re.IGNORECASE)
    _require(bool(calls) and all(key in LAUNCHER_KEYS for _quote, key in calls),
             "PowerShell launcher contains unknown warning keys")
    menu = _tree(source_root / "tools/quick_menu_toggle.py")
    item = _tree(source_root / "tools/quick_menu_item.py")
    _require(_assignment(item, "DEFAULT_LABEL") == english["menu.parent_title"], "Parent title differs from English catalog")
    _require(_assignment(menu, "SETTING_LABELS") == tuple(english[key] for key in MENU_KEYS),
             "Native setting labels differ from English catalog")
    render = _menu_renderer(menu)
    for role, key in enumerate(MENU_KEYS):
        for desired in (("last_manual", "random", "by_habitat") if role == 1 else (False, True)):
            for pending, settings_ok, stopped in ((False, True, False), (True, True, False),
                                                 (False, False, False), (True, False, False),
                                                 (False, True, True)):
                state = SimpleNamespace(desired=desired, pending=pending, settings_ok=settings_ok, stopped=stopped)
                value_key = ("status.stopped" if stopped else
                             {"last_manual": "value.last_selected", "random": "value.random",
                              "by_habitat": "value.by_habitat"}[desired] if role == 1
                             else "value.on" if desired else "value.off")
                expected = english["format.setting"].format(label=english[key], value=english[value_key])
                if not stopped and (pending or not settings_ok):
                    status = english["status.pending" if pending else "status.session_only"]
                    expected = english["format.with_status"].format(label=expected, status=status)
                _require(render(role, state).decode("ascii") == expected, "Rendered native menu text differs from English catalog")
        expected = english["format.setting"].format(label=english[key], value=english["status.unavailable"])
        _require(render(role, None).decode("ascii") == expected, "Unavailable caption differs from English catalog")
    runtime = _tree(source_root / "src/runtime.py")
    # These are the newly changed panel surfaces only, not whole-panel coverage.
    selection = [node.value for node in runtime.body if isinstance(node, ast.Assign)
                 and any(isinstance(target, ast.Name) and target.id == "SelectionMode" for target in node.targets)]
    _require(len(selection) == 1 and isinstance(selection[0], ast.Call)
             and len(selection[0].args) == 2, "Selection enum source shape changed")
    modes = ast.literal_eval(selection[0].args[1])
    _require([label for label, value in modes.items() if value == "by_habitat"] == [english["value.by_habitat"]],
             "Panel habitat mode differs from English catalog")
    rotation = [node for node in ast.walk(runtime) if isinstance(node, ast.FunctionDef)
                and node.name == "rotate_companions" and any(isinstance(decorator, ast.Name)
                and decorator.id == "property" for decorator in node.decorator_list)]
    _require(len(rotation) == 1, "Expected one rotation panel property")
    captions = [ast.literal_eval(decorator.args[0]) for decorator in rotation[0].decorator_list
                if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "BOOLEAN" and len(decorator.args) == 1]
    _require(captions == [english["menu.rotate_companions"]], "Panel rotation caption differs from English catalog")
    status = _function(runtime, "companion_status")
    habitat_status = [statement for statement in status.body if isinstance(statement, ast.If)
                      and any(isinstance(node, ast.Constant) and node.value == "by_habitat"
                              for node in ast.walk(statement.test))]
    _require(len(habitat_status) == 1 and len(habitat_status[0].body) == 1
             and isinstance(habitat_status[0].body[0], ast.Return)
             and ast.literal_eval(habitat_status[0].body[0].value) == english["panel.habitat_status"],
             "Panel habitat status differs from English catalog")
    _require(_assignment(runtime, "PRODUCT_NAME") == english["product.full_name"],
             "Product name differs from English catalog")
    _require("by " + _assignment(runtime, "PRODUCT_AUTHOR") == english["product.author_credit"],
             "Author credit differs from English catalog")
    control = _function(runtime, "_apply_control")
    setting_notices = _notice_assignments(control, "self.pending_notice")
    expected_call = ast.parse("settings_change_notice(previous, requested, self.settings_ok)", mode="eval").body
    _require(len(setting_notices) == 1 and ast.dump(setting_notices[0]) == ast.dump(expected_call),
             "HUD settings text source shape changed")
    setting_keys = ("enabled", "selection_mode", "prefer_same_biome", "planets", "space_stations", "nexus", "rotate_companions")
    labels = tuple(zip(setting_keys, (english[key] for key in MENU_KEYS)))
    _require(_assignment(runtime, "SETTINGS_NOTICE_LABELS") == labels,
             "HUD settings labels differ from English catalog")
    locations = {"planets": 3, "space_stations": 2, "nexus": 14}
    _require(_assignment(runtime, "SETTINGS_NOTICE_LOCATIONS") == locations,
             "HUD settings location mapping changed")
    modes = {"last_manual": english["value.last_selected"], "random": english["value.random"],
             "by_habitat": english["value.by_habitat"]}
    _require(_assignment(runtime, "SETTINGS_NOTICE_MODES") == modes,
             "HUD settings modes differ from English catalog")
    render_settings = _settings_notice_renderer(runtime)
    for mask in range(128):
        for saved in (True, False):
            for enabled in (True, False):
                for mode in modes:
                    previous = {"enabled": not enabled, "selection_mode": "random" if mode == "last_manual" else "last_manual",
                                "prefer_same_biome": not enabled, "locations": [] if enabled else [2, 3, 14],
                                "rotate_companions": not enabled}
                    requested = dict(previous, locations=list(previous["locations"]))
                    changed = []
                    for index, (key, label) in enumerate(labels):
                        if not mask & (1 << index):
                            continue
                        value = mode if key == "selection_mode" else enabled
                        if key in locations:
                            if enabled:
                                requested["locations"].append(locations[key])
                            else:
                                requested["locations"].remove(locations[key])
                        else:
                            requested[key] = value
                        display = modes[value] if key == "selection_mode" else english["value.on" if value else "value.off"]
                        changed.append(english["format.setting"].format(label=label, value=display))
                    expected = (english["hud.settings_applied"].format(
                        changes=english["hud.setting_separator"].join(changed),
                        suffix="" if saved else english["hud.session_suffix"]) if changed else None)
                    actual = render_settings(previous, requested, saved)
                    _require(actual == expected, "HUD settings notice differs from English catalog")
                    _require(actual is None or len(actual.encode("ascii")) <= 511,
                             "HUD settings notice exceeds its native bound")
    manual = _function(runtime, "_remember_confirmed_companion")
    prefixes = _notice_assignments(manual, "prefix")
    _require([ast.literal_eval(value) for value in prefixes]
             == [english["hud.companion_saved"], english["hud.companion_session"]],
             "HUD manual-choice text differs from English catalog")
    notices = _notice_assignments(manual, "self.pending_notice")
    _require([_evaluate_notice(value, {"prefix": "<prefix>"}) for value in notices]
             == ["<prefix>" + english["hud.auto_off_suffix"], "<prefix>" + english["hud.random_on_suffix"],
                 "<prefix>" + english["hud.habitat_on_suffix"], "<prefix>"],
             "HUD manual-choice suffixes differ from English catalog")
    unavailable = _notice_assignments(_function(runtime, "_choose_automatic_companion"), "self.pending_notice")
    _require([ast.literal_eval(value) for value in unavailable] == [english["hud.no_suitable_habitat"]],
             "HUD unavailable habitat notice differs from English catalog")
    known_notices = {id(value) for value in setting_notices + notices + unavailable}
    all_notices = _notice_assignments(runtime, "self.pending_notice")
    _require(all(id(value) in known_notices
                 or isinstance(value, ast.Constant) and value.value is None for value in all_notices),
             "A new HUD notice is outside the catalog's reviewed source scope")


def validated_catalogs(locales_dir=None, source_root=None):
    """Return the same owned catalog snapshot whose data and source were checked.

    Preparation tools can reuse these bytes without reopening files after their
    validation. This reads authored files only, never a running game or settings.
    """
    source_root = Path(source_root) if source_root is not None else ROOT
    directory = Path(locales_dir) if locales_dir is not None else source_root / "locales"
    _require({path.name for path in directory.glob("*.json")} == {code + ".json" for code in LOCALES},
             "Expected exactly the fourteen scoped locale files")
    catalogs = {code: _read_catalog(directory / (code + ".json"), code) for code in LOCALES}
    english = {key: entry["text"] for key, entry in catalogs["en"]["messages"].items()}
    for code, catalog in catalogs.items():
        unchanged = set()
        for key, entry in catalog["messages"].items():
            _require(entry["source_sha256"] == source_fingerprint(english[key]), f"Stale source fingerprint: {code}:{key}")
            _require(_placeholders(entry["text"]) == _placeholders(english[key]), f"Placeholder mismatch: {code}:{key}")
            if code != "en" and entry["text"] == english[key]:
                unchanged.add(key)
        _require(set(catalog["unchanged_keys"]) == unchanged and unchanged <= UNCHANGED_ALLOWED,
                 f"Untranslated English or incorrect unchanged-key declaration: {code}")
    _check_sources(english, source_root)
    return catalogs


def validate(locales_dir=None, source_root=None):
    """Read explicit paths and return a bounded report, or raise CatalogError."""
    validated_catalogs(locales_dir, source_root)
    return {"locales": len(LOCALES), "keys_per_locale": len(KEYS), "translated_drafts": len(LOCALES) - 1,
            "scope": SCOPE, "source_text_verified": True,
            "native_runtime_integrated": False, "language_review_verified": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locales-dir", type=Path)
    parser.add_argument("--source-root", type=Path)
    arguments = parser.parse_args(argv)
    try:
        print(json.dumps(validate(arguments.locales_dir, arguments.source_root), sort_keys=True))
    except (CatalogError, ValueError, TypeError, KeyError, UnicodeError) as error:
        parser.exit(1, f"Locale validation failed: {error}\n")


if __name__ == "__main__":
    main()
