"""Assert agreement of exact-build declarations without importing game code."""

import argparse
import ast
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PROFILE_FIELDS = frozenset(("schema_version", "steam_build", "game_release", "exe_sha256", "framework_version"))
CONSTANTS = {"steam_build": "STEAM_BUILD", "game_release": "GAME_RELEASE",
             "exe_sha256": "SUPPORTED_GAME_SHA256", "framework_version": "FRAMEWORK_VERSION"}
DEVELOPER_SOURCES = ("tools/quick_menu_order_trial.py", "tools/quick_menu_guard_runtime.py",
                     "tools/quick_menu_item_trial.py", "tools/build_companion_technology.py")


class CompatibilityProfileError(ValueError):
    """A declaration disagrees with the exact supported-build profile."""


def require(condition, message):
    if not condition:
        raise CompatibilityProfileError(message)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate compatibility JSON key")
        result[key] = value
    return result


def literal(path, name):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assignments = [node.value for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    require(len(assignments) == 1, "Expected one literal compatibility declaration: " + name)
    try:
        return ast.literal_eval(assignments[0])
    except (ValueError, TypeError) as error:
        raise CompatibilityProfileError("Compatibility declarations must be literal values") from error


def validate(source_root=None, *, developer=False, generated=False):
    root = Path(source_root) if source_root is not None else ROOT
    profile = json.loads((root / "compatibility.json").read_text(encoding="utf-8"), object_pairs_hook=_unique)
    require(type(profile) is dict and set(profile) == PROFILE_FIELDS and type(profile["schema_version"]) is int
            and profile["schema_version"] == 1, "Invalid compatibility profile fields")
    require(type(profile["exe_sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", profile["exe_sha256"]),
            "Invalid executable fingerprint")
    require(type(profile["steam_build"]) is str and re.fullmatch(r"[0-9]{1,16}", profile["steam_build"]),
            "Invalid supported Steam build")
    for field, constant in CONSTANTS.items():
        require(literal(root / "cas_compatibility.py", constant) == profile[field],
                "Host compatibility declaration differs: " + field)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"), object_pairs_hook=_unique)
    require(manifest.get("supported_nms_exe_sha256") == profile["exe_sha256"]
            and manifest.get("steam_build") == profile["steam_build"]
            and manifest.get("framework") == f"pymhf[gui]=={profile['framework_version']}",
            "Manifest compatibility declarations differ")
    sources = ["src/runtime.py"]
    if generated:
        sources.append("CompanionAutoSummon.py")
    if developer:
        sources.extend(DEVELOPER_SOURCES)
    for name in sources:
        constant = "TARGET_SHA256" if name.endswith("build_companion_technology.py") else "EXPECTED_EXE_SHA256"
        require(literal(root / name, constant) == profile["exe_sha256"], "Native target differs: " + name)
    require(literal(root / "src/runtime.py", "EXPECTED_PYMHF") == profile["framework_version"],
            "Native framework declaration differs")
    if generated:
        require(literal(root / "CompanionAutoSummon.py", "EXPECTED_PYMHF") == profile["framework_version"],
                "Generated framework declaration differs")
    return {"steam_build": profile["steam_build"], "game_release": profile["game_release"],
            "native_sources_checked": len(sources), "generated_source_checked": generated,
            "developer_sources_checked": developer, "all_declarations_match": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--developer", action="store_true")
    parser.add_argument("--generated", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate(developer=args.developer, generated=args.generated)))


if __name__ == "__main__":
    main()
