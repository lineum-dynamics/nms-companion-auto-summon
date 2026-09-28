"""Validate and stage the original icon before launch; never access a process.

The caller validates the bundle manifest and exact game executable separately.
This helper accepts only the fixed original DDS and destination. Publication is
exclusive: an unexpected existing file is never replaced. Resource mounting and
native decoding are separate in-game checks, not established by installation.
"""

import hashlib
import os
from pathlib import Path
import stat
import struct
import tempfile


ASSET_NAME = "SETTINGS.DDS"
ASSET_SHA256 = "808a8b3f887a17a8ccc2b32752196e802915c87ecec43abb07205a5c7d30e9fe"
ASSET_HASHES = {
    ASSET_NAME: ASSET_SHA256,
    "AUTOMATION.DDS": "0051f22c3726f328a8c6a94f48b3329c2de6069454750052f398acb051dadce1",
    "SELECTION.DDS": "5557271126921080be9b8f2f1fc03ba4d1681084d34657fe80e70e976d21d40d",
    "BIOME.DDS": "2485582acffb956ac3d2846b63a751f10b711caea9194a761240367227fa9cb4",
    "PLANET.DDS": "606537a274aa30ea33f2371d25e65f0b0040fa6584707828d5e2d74fd64bdb49",
    "STATION.DDS": "e06024ba966738645ee90a84705c4d5ffd059aad4d5221e2248cba8d378d5db7",
    "ANOMALY.DDS": "06af129d9c90e1d080a4ca31739119557a210d482664c5090d4c7fbdbc1a6134",
    "ROTATE.DDS": "429cf9baa614271c479a7e64c28648152b4a873b8dd07cd0e5640eb147ccc5cf",
}
ASSET_SIZE = 262272
VIRTUAL_PATH = "TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/SETTINGS.DDS"
DESTINATION = "GAMEDATA/MODS/CompanionAutoSummon/" + VIRTUAL_PATH
_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class AssetError(RuntimeError):
    """The original icon could not be validated or safely staged."""


def _destination(asset_name):
    if type(asset_name) is not str or asset_name not in ASSET_HASHES:
        raise AssetError("Unknown original icon asset.")
    return DESTINATION.rsplit("/", 1)[0] + "/" + asset_name


def validate_asset(data, asset_name=ASSET_NAME):
    """Return the canonical digest only for the exact original legacy RGBA DDS."""
    _destination(asset_name)
    if type(data) is not bytes or len(data) != ASSET_SIZE or data[:4] != b"DDS ":
        raise AssetError("The icon has an invalid DDS size or signature.")
    fields = {4: 124, 8: 0x2100F, 12: 256, 16: 256, 20: 1024, 24: 0,
              28: 1, 76: 32, 80: 0x41, 84: 0, 88: 32, 92: 0xFF,
              96: 0xFF00, 100: 0xFF0000, 104: 0xFF000000, 108: 0x1000,
              112: 0, 116: 0, 120: 0, 124: 0}
    if any(struct.unpack_from("<I", data, offset)[0] != value
           for offset, value in fields.items()) or any(data[32:76]):
        raise AssetError("The icon does not use the reviewed DDS layout.")
    digest = hashlib.sha256(data).hexdigest()
    if digest != ASSET_HASHES[asset_name]:
        raise AssetError("The icon differs from the reviewed original artwork.")
    return digest


def _checked_path(path, *, missing=False, directory=False):
    """Reject redirects in every existing component, including root ancestors."""
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise AssetError("Asset paths must be absolute and normalized.")
    chain = [*reversed(path.parents), path]
    for index, component in enumerate(chain):
        try:
            info = component.lstat()
        except FileNotFoundError:
            if missing:
                return path
            raise AssetError("A required asset path is missing.") from None
        if (stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_file_attributes", 0) & _REPARSE_POINT):
            raise AssetError("Asset paths must not contain links or reparse points.")
        if (index < len(chain) - 1 or directory) and not stat.S_ISDIR(info.st_mode):
            raise AssetError("An asset directory path is not a directory.")
        if index == len(chain) - 1 and not directory and not stat.S_ISREG(info.st_mode):
            raise AssetError("An asset file path is not a regular file.")
    return path


def _read_asset(path, asset_name=ASSET_NAME):
    _checked_path(path)
    with path.open("rb") as stream:
        if os.fstat(stream.fileno()).st_size != ASSET_SIZE:
            raise AssetError("An existing icon has an unexpected size.")
        data = stream.read(ASSET_SIZE + 1)
    _checked_path(path)
    validate_asset(data, asset_name)
    return data


def _closed(predicate):
    try:
        closed = predicate() if callable(predicate) else False
    except Exception:
        raise AssetError("The game-closed check failed; icon staging stopped.") from None
    if closed is not True:
        raise AssetError("Close NMS before staging the icon.")


def _result(installed, asset_name=ASSET_NAME):
    return {"installed": installed, "reused": not installed,
            "relative_path": _destination(asset_name), "sha256": ASSET_HASHES[asset_name]}


def install_icon(bundle, game_directory, game_closed, *, asset_name=ASSET_NAME):
    """Stage one original loose asset, using an injected game-closed predicate.

    No process lookup, executable hashing or injection occurs here. If the game
    opens after publication, refusal leaves the verified asset intact; it never
    deletes an installed asset from a potentially running game. Concurrent path
    redirection is checked repeatedly, but this is not a hostile-filesystem
    isolation boundary.
    """
    try:
        return _install_icon(bundle, game_directory, game_closed, asset_name)
    except AssetError:
        raise
    except (OSError, ValueError, TypeError):
        raise AssetError("The icon paths could not be validated or staged.") from None


def _install_icon(bundle, game_directory, game_closed, asset_name=ASSET_NAME):
    relative_path = _destination(asset_name)
    bundle = _checked_path(bundle, directory=True)
    game = _checked_path(game_directory, directory=True)
    _checked_path(game / "Binaries" / "NMS.exe")
    _closed(game_closed)
    data = _read_asset(bundle / asset_name, asset_name)
    destination = game / relative_path
    _checked_path(destination, missing=True)
    if destination.exists():
        _read_asset(destination, asset_name)
        _closed(game_closed)
        return _result(False, asset_name)

    # Check the whole path before any mutation, then each created component.
    current = game
    for part in Path(relative_path).parts[:-1]:
        current = current / part
        _checked_path(current, missing=True, directory=True)
        if not current.exists():
            _closed(game_closed)
            try:
                current.mkdir()
            except FileExistsError:
                pass
        _checked_path(current, directory=True)

    temporary = None
    try:
        _checked_path(destination.parent, directory=True)
        _closed(game_closed)
        descriptor, name = tempfile.mkstemp(prefix=".cas-icon-", suffix=".tmp",
                                           dir=destination.parent)
        temporary = Path(name)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if _read_asset(temporary, asset_name) != data:
            raise AssetError("The staged icon failed readback.")
        _checked_path(destination, missing=True)
        _closed(game_closed)
        installed = True
        try:
            # A hard link publishes complete bytes atomically and refuses an
            # existing destination on Windows and POSIX. Never use replace().
            os.link(temporary, destination, follow_symlinks=False)
        except FileExistsError:
            installed = False
        _read_asset(destination, asset_name)
        _closed(game_closed)
        return _result(installed, asset_name)
    except AssetError:
        raise
    except OSError:
        raise AssetError("The icon could not be staged; existing files were not replaced.") from None
    finally:
        if temporary is not None:
            # Cleanup only our temporary name, after rechecking the path.
            try:
                _checked_path(temporary)
                temporary.unlink()
            except (OSError, AssetError):
                pass


def install_icons(bundle, game_directory, game_closed):
    """Validate the entire fixed set before staging any file; never overwrite.

    Publication remains per-file and idempotent. If the game opens or a later
    write fails, already verified assets stay intact for a subsequent launch.
    """
    try:
        bundle = _checked_path(bundle, directory=True)
        game = _checked_path(game_directory, directory=True)
        _checked_path(game / "Binaries/NMS.exe")
        _closed(game_closed)
        for name in ASSET_HASHES:
            _read_asset(bundle / name, name)
            destination = game / _destination(name)
            _checked_path(destination, missing=True)
            if destination.exists():
                _read_asset(destination, name)
        _closed(game_closed)
        results = [install_icon(bundle, game, game_closed, asset_name=name)
                   for name in ASSET_HASHES]
        return {"installed": any(result["installed"] for result in results),
                "reused": all(result["reused"] for result in results), "files": results}
    except AssetError:
        raise
    except (OSError, ValueError, TypeError):
        raise AssetError("The icon set could not be validated or staged.") from None
