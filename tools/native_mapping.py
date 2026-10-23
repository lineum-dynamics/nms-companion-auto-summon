"""Read exact-build native mappings and generate the selected C++ constants.

Unapproved entries are research inputs. The normal profile/build/package path
rejects them, and generated constants retain the independent activation gate.
"""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re


ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = tuple("queue_pet player_update owner_update ship_eject enter_cockpit "
                  "load_player_state trigger_action build_menu label_menu append_menu "
                  "confirm_menu load_menu_resources position_observer can_summon "
                  "owned_pet_eligible refresh_placement dominant_hand add_timed_message "
                  "construct_menu_item select_menu_item load_texture retain_resource get_button".split())
GLOBALS = ("application", "resource_manager", "retain_manager", "interaction_range")
LOCAL_LOAD = ("current_state_cell", "state", "vtable", "player_state_offset")
BUILD_FIELDS = {"game_release", "exe_sha256", "activation_approved", "evidence", "functions",
                "globals", "binding_return", "position_returns", "local_load"}


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate native mapping key")
        result[key] = value
    return result


def _offset(value, *, zero=False):
    if not isinstance(value, str) or not re.fullmatch(r"0x[0-9A-Fa-f]{1,8}", value):
        raise ValueError("Native mapping requires hexadecimal DWORD values")
    number = int(value, 16)
    if number == 0 and not zero:
        raise ValueError("Native mapping requires a nonzero RVA")
    return number


def _fields(values, names, *, zero=False):
    if type(values) is not dict or set(values) != set(names):
        raise ValueError("Native mapping has unexpected fields")
    return {key: _offset(values[key], zero=zero) for key in names}


def read_native_mappings(path: Path = ROOT / "native_mappings.json") -> dict:
    registry = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique)
    if (type(registry) is not dict or set(registry) != {"schema_version", "builds"}
            or type(registry["schema_version"]) is not int or registry["schema_version"] != 1
            or type(registry["builds"]) is not dict or not registry["builds"]):
        raise ValueError("Native mapping registry has an unexpected schema")
    result = {}
    for build, record in registry["builds"].items():
        if (not re.fullmatch(r"[0-9]{5,12}", build) or type(record) is not dict
                or set(record) != BUILD_FIELDS):
            raise ValueError("Native mapping build has an unexpected schema")
        if (not isinstance(record["game_release"], str)
                or not re.fullmatch(r"Cosmos [0-9]+\.[0-9]+", record["game_release"])
                or not isinstance(record["exe_sha256"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", record["exe_sha256"])
                or type(record["activation_approved"]) is not bool):
            raise ValueError("Native mapping has invalid identity or approval fields")
        evidence = record["evidence"]
        if (not isinstance(evidence, str) or not evidence or "\\" in evidence
                or PurePosixPath(evidence).is_absolute() or ":" in evidence
                or ".." in PurePosixPath(evidence).parts):
            raise ValueError("Native mapping evidence must be a repository-relative path")
        normalized = dict(record, steam_build=build)
        normalized["functions"] = _fields(record["functions"], FUNCTIONS)
        normalized["globals"] = _fields(record["globals"], GLOBALS)
        normalized["binding_return"] = _offset(record["binding_return"])
        returns = record["position_returns"]
        if type(returns) is not list or len(returns) != 3:
            raise ValueError("Native mapping requires three position returns")
        normalized["position_returns"] = [_offset(value) for value in returns]
        if len(set(normalized["position_returns"])) != 3:
            raise ValueError("Native mapping position returns must be distinct")
        normalized["local_load"] = _fields(record["local_load"], LOCAL_LOAD, zero=True)
        policy = normalized["local_load"].values()
        if any(policy) and not all(policy):
            raise ValueError("Native mapping local-load policy must be complete or all zero")
        result[build] = normalized
    if len({record["exe_sha256"] for record in result.values()}) != len(result):
        raise ValueError("Native mapping executable identities must be distinct")
    return result


def load_native_mapping(profile: dict, *, path: Path = ROOT / "native_mappings.json",
                        require_approved: bool = True) -> dict:
    record = read_native_mappings(path).get(profile["steam_build"])
    if (record is None or record["game_release"] != profile["game_release"]
            or record["exe_sha256"] != profile["exe_sha256"]):
        raise ValueError("Native profile has no exact game/build/hash mapping")
    if require_approved and not record["activation_approved"]:
        raise ValueError("Native mapping is not approved for activation")
    return record


def write_mapping_header(mapping: dict, path: Path) -> None:
    lines = ["#pragma once", "namespace cas::mapping {", "inline constexpr Build target=[] {",
             "    Build build{};",
             f"    build.steam_build={json.dumps(mapping['steam_build'])};",
             f"    build.exe_sha256={json.dumps(mapping['exe_sha256'])};",
             f"    build.activation_approved={str(mapping['activation_approved']).lower()};"]
    for group, names in (("functions", FUNCTIONS), ("globals", GLOBALS), ("local_load", LOCAL_LOAD)):
        for name in names:
            lines.append(f"    build.{group}.{name}=0x{mapping[group][name]:X};")
    lines.append(f"    build.binding_return=0x{mapping['binding_return']:X};")
    for index, value in enumerate(mapping["position_returns"]):
        lines.append(f"    build.position_returns[{index}]=0x{value:X};")
    lines += ["    return build;", "}();", "}", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
