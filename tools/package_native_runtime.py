"""Package the explicit native player overlay, without deploying or launching it.

Only fixed reviewed files enter the archive. Build executables, source caches,
private settings, logs and saves are never collected. Loader bytes must match
the retained official release exactly. A new ZIP is published only after a full
readback and hash check; existing archives are never overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import struct
import tempfile
import zipfile

from quick_menu_assets import ASSET_HASHES, DESTINATION, _checked_path, validate_asset


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.10.0-native-test"
TITLE = "Companion Auto Summon for No Man's Sky - by Lineum Dynamics"
LOADER_SHA256 = "fa266e3513d02c08a1b808f28c10538a489eaffaa4b0707f7cc1066e71b5afd7"
LOADER_BYTES = 3615928
LOADER_URL = "https://github.com/ThirteenAG/Ultimate-ASI-Loader/releases/download/v9.7.4/Ultimate-ASI-Loader_x64.zip"
LICENSE_FILES = (
    "UAL-9.7.4-MIT.txt", "UAL-injector-zlib.txt", "UAL-MinHook-BSD-HDE.txt", "UAL-miniz-notices.txt",
    "MinHook-1.3.4-BSD-HDE.txt", "json-3.12.0-MIT.txt", "LLVM-Apache-2.0-with-exceptions.txt",
    "libcxx-LICENSE.txt", "libcxx-CREDITS.txt", "libcxxabi-LICENSE.txt", "libcxxabi-CREDITS.txt",
    "libunwind-LICENSE.txt", "compiler-rt-LICENSE.txt",
    "MinGW-w64-runtime-NOTICES.txt", "MinGW-w64-general-NOTICES.txt", "winpthreads-NOTICES.txt", "README.md",
)
OVERLAY_ICON_DIRECTORY = DESTINATION.rsplit("/", 1)[0]
ALLOWED_FILES = frozenset({
    "Binaries/winmm.dll", "Binaries/scripts/CompanionAutoSummon.asi", "README.md", "README.cs.md", "manifest.json",
    *(f"{OVERLAY_ICON_DIRECTORY}/{name}" for name in ASSET_HASHES),
    *(f"licenses/{name}" for name in LICENSE_FILES),
})


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_file(path: Path, maximum: int = 32 * 1024 * 1024) -> bytes:
    path = _checked_path(path.absolute())
    if path.stat().st_size > maximum:
        raise ValueError(f"Input exceeds size bound: {path.name}")
    with path.open("rb") as stream:
        data = stream.read(maximum + 1)
    _checked_path(path)
    if len(data) > maximum:
        raise ValueError(f"Input exceeds size bound: {path.name}")
    return data


def read_json(data: bytes):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate metadata key")
            result[key] = value
        return result
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique)


def member_name(name: str) -> None:
    path = PurePosixPath(name)
    if not name or "\\" in name or ":" in name or path.is_absolute() or any(part in (".", "..", "") for part in name.split("/")):
        raise ValueError("Invalid archive member path")
    if name not in ALLOWED_FILES:
        raise ValueError("Unapproved archive member: " + name)


def native_x64_dll(data: bytes) -> None:
    """Check structure only; matching receipt/upstream hashes establish identity."""
    if len(data) < 256 or data[:2] != b"MZ":
        raise ValueError("Expected a native DLL")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if pe < 64 or pe + 26 > len(data) or data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("Invalid PE header")
    machine, sections = struct.unpack_from("<HH", data, pe + 4)
    optional_size, characteristics = struct.unpack_from("<HH", data, pe + 20)
    if machine != 0x8664 or not 1 <= sections <= 96 or not characteristics & 0x2000:
        raise ValueError("Expected an x64 DLL image")
    if optional_size < 112 or pe + 24 + optional_size + sections * 40 > len(data):
        raise ValueError("Invalid PE table bounds")
    if struct.unpack_from("<H", data, pe + 24)[0] != 0x20B:
        raise ValueError("Expected a PE32+ image")


def payload(build: Path, loader: Path) -> tuple[dict[str, bytes], dict]:
    build = _checked_path(build.absolute(), directory=True)
    if not build.is_relative_to(ROOT / "build"):
        raise ValueError("Native build must be an explicit repository build directory")
    receipt_bytes = read_file(build / "build-receipt.json", 4 * 1024 * 1024)
    receipt = read_json(receipt_bytes)
    if receipt.get("version") != VERSION or receipt.get("gameplay_implemented") is not True:
        raise ValueError("Native build receipt has the wrong product/version")
    if receipt.get("live_verified") is not False or receipt.get("deployed") is not False:
        raise ValueError("This packager is for the unverified native test candidate")
    validation_bytes = read_file(build / "validation-receipt.json", 4 * 1024 * 1024)
    validation = read_json(validation_bytes)
    if (validation.get("version") != VERSION or validation.get("passed") is not True
            or validation.get("build_receipt_sha256") != digest(receipt_bytes)):
        raise ValueError("Native build does not have a matching successful validation receipt")
    required_validators = {"policy", "selection", "storage", "runtime", "backup"}
    validators = validation.get("validators")
    if not isinstance(validators, dict) or not required_validators.issubset(validators):
        raise ValueError("Native validation receipt is incomplete")
    for name in sorted(required_validators):
        result = validators[name]
        summary = result.get("summary", {})
        if summary.get("passed") is not True and summary.get("status") != "passed":
            raise ValueError("Native component validation did not pass: " + name)
        raw_report = read_file(build / (name + "-validation.json"), 4 * 1024 * 1024)
        if result.get("report_sha256") != digest(raw_report):
            raise ValueError("Native component report differs from its receipt: " + name)
    asi = read_file(build / "CompanionAutoSummon.asi")
    native_x64_dll(asi)
    product = receipt.get("products", {}).get("CompanionAutoSummon.asi")
    if product != {"sha256": digest(asi), "bytes": len(asi)}:
        raise ValueError("Native module does not match its build receipt")
    profile = read_json(read_file(ROOT / "compatibility.json"))
    if receipt.get("compatibility") != profile:
        raise ValueError("Native module targets a different compatibility profile")
    sources = receipt.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Native build has no source identity receipt")
    for name, expected in sources.items():
        source = PurePosixPath(name)
        if not isinstance(expected, str) or not re.fullmatch("[0-9a-f]{64}", expected):
            raise ValueError("Invalid source hash in build receipt")
        if source.is_absolute() or ".." in source.parts or "\\" in name or ":" in name:
            raise ValueError("Invalid source path in build receipt")
        # Build/source drift must not be presented as a matching review artifact.
        if digest(read_file(ROOT / name)) != expected:
            raise ValueError("Source changed after native build: " + name)
    loader_bytes = read_file(loader)
    if len(loader_bytes) != LOADER_BYTES or digest(loader_bytes) != LOADER_SHA256:
        raise ValueError("Loader differs from the exact retained official UAL 9.7.4 x64 release")
    native_x64_dll(loader_bytes)
    files = {
        "Binaries/winmm.dll": loader_bytes,
        "Binaries/scripts/CompanionAutoSummon.asi": asi,
        "README.md": read_file(ROOT / "native/player-README.md", 128 * 1024),
        "README.cs.md": read_file(ROOT / "native/player-README.cs.md", 128 * 1024),
    }
    for name in ASSET_HASHES:
        data = read_file(ROOT / "assets/ui" / name)
        validate_asset(data, name)
        files[f"{OVERLAY_ICON_DIRECTORY}/{name}"] = data
    dependency_lock_bytes = read_file(ROOT / "native/dependencies-lock.json", 2 * 1024 * 1024)
    dependency_lock = read_json(dependency_lock_bytes)
    if sorted(dependency_lock.get("package_notice_allowlist", [])) != sorted(LICENSE_FILES):
        raise ValueError("Third-party notice allowlist differs from the reviewed dependency lock")
    locked_notices = {entry["path"]: entry for entry in dependency_lock.get("notice_files", [])}
    if len(locked_notices) != len(LICENSE_FILES):
        raise ValueError("Third-party notice identity list is incomplete")
    for name in LICENSE_FILES:
        data = read_file(ROOT / "native/licenses" / name, 2 * 1024 * 1024)
        if not data.strip():
            raise ValueError("Empty third-party notice: " + name)
        data.decode("utf-8-sig")
        identity = locked_notices.get("native/licenses/" + name, {})
        if identity.get("bytes") != len(data) or identity.get("sha256") != digest(data):
            raise ValueError("Third-party notice differs from the reviewed dependency lock: " + name)
        files[f"licenses/{name}"] = data
    for name in files:
        member_name(name)
    manifest = {
        "schema": 1, "product": TITLE, "version": VERSION,
        "platform": "Windows 10/11 x64 / Steam",
        "candidate_status": "private native test; live startup, appearance, multiplayer and Nexus clearance unverified",
        "game": {key: profile[key] for key in ("steam_build", "game_release", "exe_sha256")},
        "install": {"method": "merge Binaries and GAMEDATA into the Steam game root while the game is closed",
                    "loader_conflict": "do not replace a different existing winmm.dll",
                    "launch": "normal Steam launch; do not run the previous Python launcher concurrently"},
        "settings_directory": "%LOCALAPPDATA%/NMS-AutoPet",
        "backup": "verified pre-activation snapshot while game is already running; never edits or restores original saves",
        "localization": {"in_game": "en", "catalogs": 14, "startup_errors": "Windows language where available; English fallback"},
        "loader": {"name": "Ultimate ASI Loader", "version": "9.7.4", "architecture": "x64", "upstream": LOADER_URL,
                   "upstream_member": "dinput8.dll", "installed_name": "Binaries/winmm.dll", "sha256": LOADER_SHA256},
        "build": {"receipt_sha256": digest(receipt_bytes), "source_sha256": sources,
                  "validation_receipt_sha256": digest(validation_bytes), "offline_validation_passed": True},
        "dependency_lock_sha256": digest(dependency_lock_bytes),
        "files": {name: {"bytes": len(data), "sha256": digest(data)} for name, data in sorted(files.items())},
        "manifest_note": "The manifest describes every other ZIP member; its own hash is in the packaging receipt.",
    }
    files["manifest.json"] = (json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if set(files) != ALLOWED_FILES:
        raise ValueError("Incomplete explicit player package")
    return files, manifest


def verify_zip(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or set(names) != set(files) or set(names) != ALLOWED_FILES:
            raise ValueError("ZIP contains missing, duplicate or unapproved members")
        for info in infos:
            member_name(info.filename)
            if info.flag_bits & 1 or info.is_dir() or info.file_size != len(files[info.filename]):
                raise ValueError("Invalid ZIP member metadata")
            raw = archive.read(info)
            if raw != files[info.filename]:
                raise ValueError("ZIP readback differs: " + info.filename)
        manifest = read_json(archive.read("manifest.json"))
        for name, identity in manifest["files"].items():
            raw = archive.read(name)
            if identity != {"bytes": len(raw), "sha256": digest(raw)}:
                raise ValueError("Manifest identity differs: " + name)
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC readback failed")


def package(build: Path, loader: Path, output: Path) -> dict:
    output = output.absolute()
    if output.suffix.lower() != ".zip" or output.exists():
        raise ValueError("Choose a new ZIP path; existing artifacts are never overwritten")
    _checked_path(output, missing=True)
    files, manifest = payload(build, loader)
    output.parent.mkdir(parents=True, exist_ok=True)
    _checked_path(output.parent, directory=True)
    temporary = None
    try:
        descriptor, name = tempfile.mkstemp(prefix=".cas-native-", suffix=".tmp", dir=output.parent)
        temporary = Path(name)
        with os.fdopen(descriptor, "w+b") as stream:
            with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                for member, raw in sorted(files.items()):
                    info = zipfile.ZipInfo(member, date_time=(2026, 9, 28, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            stream.flush()
            os.fsync(stream.fileno())
        verify_zip(temporary, files)
        raw = read_file(temporary, 64 * 1024 * 1024)
        # Exclusive publication preserves any artifact created by another process.
        os.link(temporary, output, follow_symlinks=False)
        verify_zip(output, files)
        return {
            "status": "packaged-and-readback-verified", "version": VERSION,
            "zip": {"path": str(output), "bytes": len(raw), "sha256": digest(raw)},
            "members": len(files), "game_overlay_files": 2 + len(ASSET_HASHES),
            "module": manifest["files"]["Binaries/scripts/CompanionAutoSummon.asi"],
            "loader": manifest["files"]["Binaries/winmm.dll"],
            "manifest_sha256": digest(files["manifest.json"]),
            "live_verified": False, "deployed": False, "uploaded": False,
        }
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", required=True, type=Path)
    parser.add_argument("--loader", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if args.report.exists():
        raise ValueError("Choose a new packaging receipt path")
    report = package(args.build, args.loader, args.output)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
