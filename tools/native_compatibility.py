"""Strict reader for the native runtime's separately versioned game profile."""
from __future__ import annotations

import json
from pathlib import Path
import re


FIELDS = {"schema_version", "runtime", "steam_build", "game_release", "exe_sha256"}


def load_native_profile(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate native compatibility key")
            result[key] = value
        return result

    profile = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    if not isinstance(profile, dict) or set(profile) != FIELDS:
        raise ValueError("Native compatibility profile has an unexpected schema")
    if (type(profile["schema_version"]) is not int or profile["schema_version"] != 1
            or profile["runtime"] != "native"
            or not isinstance(profile["steam_build"], str)
            or not re.fullmatch(r"[0-9]{5,12}", profile["steam_build"])
            or not isinstance(profile["game_release"], str)
            or not re.fullmatch(r"Cosmos [0-9]+\.[0-9]+", profile["game_release"])
            or not isinstance(profile["exe_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", profile["exe_sha256"])):
        raise ValueError("Native compatibility profile contains invalid values")
    if profile["game_release"] != "Cosmos 7.05" or profile["steam_build"] != "25624745":
        raise ValueError("Native profile is not the statically verified Cosmos 7.05 target")
    return profile
