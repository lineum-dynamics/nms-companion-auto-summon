"""Small, atomic storage for the user's Companion Auto Summon preferences.

Only the caller-supplied settings path is used. Import and construction perform
no filesystem operations; this module never reads or modifies game saves.
"""

import json
import os
from pathlib import Path
import tempfile


class SettingsStoreError(Exception):
    """Settings could not be read, validated, or replaced safely."""


class CompanionAutoSummonSettingsStore:
    """Store schema-3 preferences and read legacy schema-1/2 settings.

    Missing settings use fresh defaults. Legacy settings migrate in memory only
    until an explicit save. Existing unreadable, malformed, or
    unsupported documents raise SettingsStoreError and are never overwritten.
    Each operation rereads the file; use one settings writer at a time.
    """

    SCHEMA = 3
    MAX_BYTES = 4096
    ALLOWED_LOCATIONS = frozenset({2, 3, 14})
    SELECTION_MODES = frozenset({"last_manual", "random"})

    def __init__(self, path: Path):
        self.path = Path(path)

    @classmethod
    def defaults(cls) -> dict:
        """Return independent preference defaults without filesystem access."""
        return {
            "enabled": True,
            "locations": sorted(cls.ALLOWED_LOCATIONS),
            "selection_mode": "last_manual",
            "prefer_same_biome": True,
        }

    @staticmethod
    def _unique_object(pairs):
        document = {}
        for key, value in pairs:
            if key in document:
                raise SettingsStoreError("Settings contain duplicate JSON keys")
            document[key] = value
        return document

    @classmethod
    def _validate_preferences(cls, preferences):
        if type(preferences) is not dict or set(preferences) != {
            "enabled", "locations", "selection_mode", "prefer_same_biome"
        }:
            raise ValueError("Preferences have an invalid structure")
        if type(preferences["enabled"]) is not bool:
            raise ValueError("Preferences enabled value must be boolean")
        if type(preferences["prefer_same_biome"]) is not bool:
            raise ValueError("Preferences biome preference must be boolean")
        locations = preferences["locations"]
        if type(locations) is not list or any(
            type(location) is not int or location not in cls.ALLOWED_LOCATIONS
            for location in locations
        ):
            raise ValueError("Preferences locations must be a list of allowed integer IDs")
        if len(locations) != len(set(locations)):
            raise ValueError("Preferences locations must not contain duplicate IDs")
        mode = preferences["selection_mode"]
        if type(mode) is not str or mode not in cls.SELECTION_MODES:
            raise ValueError("Preferences selection mode is unsupported")
        return {
            "enabled": preferences["enabled"],
            "locations": sorted(locations),
            "selection_mode": mode,
            "prefer_same_biome": preferences["prefer_same_biome"],
        }

    @classmethod
    def _validate_document(cls, document):
        if type(document) is not dict or "schema" not in document:
            raise SettingsStoreError("Settings have an invalid document structure")
        if type(document["schema"]) is not int or document["schema"] not in {1, 2, cls.SCHEMA}:
            raise SettingsStoreError("Settings use an unsupported schema")
        if document["schema"] == 1:
            if set(document) != {"schema", "enabled"} or type(document["enabled"]) is not bool:
                raise SettingsStoreError("Legacy settings have an invalid document structure")
            preferences = cls.defaults()
            preferences["enabled"] = document["enabled"]
            return preferences
        if document["schema"] == 2:
            if set(document) != {"schema", "enabled", "locations", "selection_mode"}:
                raise SettingsStoreError("Legacy settings have an invalid document structure")
            document = {**document, "prefer_same_biome": True}
        try:
            return cls._validate_preferences({key: value for key, value in document.items() if key != "schema"})
        except ValueError as exc:
            raise SettingsStoreError(str(exc)) from exc

    def _read(self):
        try:
            with self.path.open("rb") as source:
                raw = source.read(self.MAX_BYTES + 1)
        except FileNotFoundError:
            return self.defaults()
        except OSError as exc:
            raise SettingsStoreError("Cannot read the settings file") from exc
        if len(raw) > self.MAX_BYTES:
            raise SettingsStoreError("Settings exceed the 4 KiB limit")
        try:
            document = json.loads(raw.decode("utf-8"), object_pairs_hook=self._unique_object)
        except (UnicodeDecodeError, ValueError, RecursionError) as exc:
            raise SettingsStoreError("Settings are not valid UTF-8 JSON") from exc
        return self._validate_document(document)

    def load_preferences(self) -> dict:
        """Read all preferences; do not create or migrate a file on disk."""
        return self._read()

    def save_preferences(self, preferences: dict) -> None:
        """Atomically save valid preferences, preserving invalid existing files."""
        # Validate before creating directories or writing a temporary file.
        validated = self._validate_preferences(preferences)
        self._read()
        self._persist(validated)

    def load(self) -> bool:
        """Compatibility helper returning only the enabled preference."""
        return self.load_preferences()["enabled"]

    def save(self, enabled: bool) -> None:
        """Change enabled only, preserving existing location and selection choices."""
        if type(enabled) is not bool:
            raise ValueError("enabled must be a boolean")
        preferences = self._read()
        preferences["enabled"] = enabled
        self._persist(preferences)

    def _persist(self, preferences):
        document = {"schema": self.SCHEMA, **preferences}
        raw = (json.dumps(document, sort_keys=True, indent=2) + "\n").encode("utf-8")
        temporary_path = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=self.path.parent,
                prefix=f".{self.path.name}.", suffix=".tmp", delete=False,
            ) as target:
                temporary_path = Path(target.name)
                target.write(raw)
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary_path, self.path)
        except OSError as exc:
            raise SettingsStoreError("Cannot atomically write the settings file") from exc
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    # Do not replace the original error with a cleanup failure.
                    pass
