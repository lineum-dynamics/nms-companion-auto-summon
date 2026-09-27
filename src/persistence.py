"""Bounded, atomic local storage for a pet choice per save identity.

The caller supplies a mod-owned path. This module does not locate, open, or
modify game saves and performs no filesystem operations during import.
"""

import json
import os
from pathlib import Path
import tempfile


class SelectionStoreError(Exception):
    """A selection file could not be read, validated, or replaced safely."""


class PetSelectionStore:
    """Persist a 16-byte pet identity and a last-known slot, separately per save.

    Invalid caller arguments raise ``ValueError``. Invalid or inaccessible
    existing files raise ``SelectionStoreError`` and are never overwritten.
    Every operation re-reads the file; instances retain no cached selections.
    The runtime should use one writer, not concurrent mod processes.
    """

    SCHEMA = 1
    MAX_BYTES = 1024 * 1024
    MAX_ENTRIES = 256
    MAX_KEY_LENGTH = 256

    def __init__(self, path: Path):
        self.path = Path(path)

    @classmethod
    def _validate_key(cls, save_key):
        if not isinstance(save_key, str) or not 1 <= len(save_key) <= cls.MAX_KEY_LENGTH:
            raise ValueError("save_key must be a nonempty string of at most 256 characters")

    @staticmethod
    def _validate_slot(slot):
        if type(slot) is not int or not 0 <= slot <= 29:
            raise ValueError("slot must be an integer from 0 to 29")

    @staticmethod
    def _unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise SelectionStoreError("Selection file contains duplicate JSON keys")
            result[key] = value
        return result

    @classmethod
    def _validate_document(cls, document):
        if not isinstance(document, dict) or set(document) != {"schema", "selections"}:
            raise SelectionStoreError("Selection file has an invalid document structure")
        if type(document["schema"]) is not int or document["schema"] != cls.SCHEMA:
            raise SelectionStoreError("Selection file uses an unsupported schema")
        selections = document["selections"]
        if not isinstance(selections, dict) or len(selections) > cls.MAX_ENTRIES:
            raise SelectionStoreError("Selection file has an invalid selections table")
        for key, selection in selections.items():
            try:
                cls._validate_key(key)
            except ValueError as exc:
                raise SelectionStoreError("Selection file contains an invalid save identity") from exc
            if not isinstance(selection, dict) or set(selection) != {"seed", "slot"}:
                raise SelectionStoreError("Selection file contains an invalid pet selection")
            seed = selection["seed"]
            if not isinstance(seed, str) or len(seed) != 32 or any(
                char not in "0123456789abcdef" for char in seed
            ):
                raise SelectionStoreError("Selection file contains an invalid pet seed")
            try:
                cls._validate_slot(selection["slot"])
            except ValueError as exc:
                raise SelectionStoreError("Selection file contains an invalid pet slot") from exc
        return document

    def _read(self):
        try:
            with self.path.open("rb") as source:
                raw = source.read(self.MAX_BYTES + 1)
        except FileNotFoundError:
            return {"schema": self.SCHEMA, "selections": {}}
        except OSError as exc:
            raise SelectionStoreError("Cannot read the selection file") from exc
        if len(raw) > self.MAX_BYTES:
            raise SelectionStoreError("Selection file exceeds the 1 MiB limit")
        try:
            document = json.loads(raw.decode("utf-8"), object_pairs_hook=self._unique_object)
        except (UnicodeDecodeError, ValueError, RecursionError) as exc:
            raise SelectionStoreError("Selection file is not valid UTF-8 JSON") from exc
        return self._validate_document(document)

    def _write(self, document):
        self._validate_document(document)
        raw = (json.dumps(document, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
        if len(raw) > self.MAX_BYTES:
            raise SelectionStoreError("Selection file would exceed the 1 MiB limit")
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
            raise SelectionStoreError("Cannot atomically write the selection file") from exc
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    # A failed cleanup must not hide the original write error.
                    pass

    def load(self, save_key: str) -> dict | None:
        """Return ``{seed: lowercase hex, slot: int}``, or None if absent."""
        self._validate_key(save_key)
        selection = self._read()["selections"].get(save_key)
        return dict(selection) if selection is not None else None

    def remember(self, save_key: str, seed: bytes, slot: int):
        """Remember a 16-byte identity (JSON key seed), preserving other saves."""
        self._validate_key(save_key)
        if not isinstance(seed, bytes) or len(seed) != 16:
            raise ValueError("seed must be exactly 16 bytes")
        self._validate_slot(slot)
        document = self._read()
        document["selections"][save_key] = {"seed": seed.hex(), "slot": slot}
        self._write(document)

    def forget(self, save_key: str):
        """Remove one identity; missing entries do not create a file."""
        self._validate_key(save_key)
        document = self._read()
        if save_key in document["selections"]:
            del document["selections"][save_key]
            self._write(document)
