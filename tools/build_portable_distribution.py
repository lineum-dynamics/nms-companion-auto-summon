"""Assemble a portable tester ZIP from explicit verified inputs; never deploy."""

import argparse
import hashlib
import json
from pathlib import Path
import os
import subprocess
import zipfile

from build_portable_entrypoint import (application_manifest, assembly_identity,
                                       build as build_entrypoint, locale_resource)
from build_portable_runtime import reject_archive_payload
from portable_launcher import VERSION, regular_path, unique_object, validate_distribution
from validate_locales import validate as validate_locales, validated_catalogs
from validate_compatibility import validate as validate_compatibility


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = "Companion Auto Summon.exe"


def verified_files(folder, manifest_name):
    """Resolve an exact archive allowlist without discovering private files."""
    folder = Path(folder).resolve(strict=True)
    manifest_path = regular_path(folder, manifest_name)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    result, seen = {}, set()
    for entry in manifest["files"]:
        name, expected = entry["path"], entry["sha256"]
        if name.casefold() in seen or name.casefold() == manifest_name.casefold():
            raise ValueError("Duplicate allowlist path")
        path = regular_path(folder, name)
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError("Input checksum differs")
        result[name] = data
        seen.add(name.casefold())
    result[manifest_name] = manifest_path.read_bytes()
    return result


def build(runtime, mod, output, archive):
    output, archive = Path(output), Path(archive)
    if not output.is_absolute() or output.exists() or not archive.is_absolute() or archive.exists():
        raise ValueError("Use fresh absolute output and ZIP paths")
    validate_locales(locales_dir=ROOT / "locales", source_root=ROOT)
    validate_compatibility(source_root=ROOT, developer=True, generated=True)
    runtime_files = verified_files(runtime, "runtime-manifest.json")
    runtime_manifest = json.loads(runtime_files["runtime-manifest.json"])
    if (runtime_manifest.get("schema") != 1 or runtime_manifest.get("python") != "3.11.9"
            or runtime_manifest.get("platform") != "win_amd64" or runtime_manifest.get("framework") != "0.2.4"):
        raise ValueError("Unexpected runtime candidate")
    mod_files = verified_files(mod, "manifest.json")
    mod_manifest = json.loads(mod_files["manifest.json"])
    profile = json.loads((ROOT / "compatibility.json").read_text(encoding="utf-8"))
    if (mod_manifest.get("version") != "0.9.2-play-trial"
            or mod_manifest.get("steam_build") != profile["steam_build"]
            or mod_manifest.get("supported_nms_exe_sha256") != profile["exe_sha256"]
            or mod_manifest.get("framework") != "pymhf[gui]==" + profile["framework_version"]
            or mod_manifest.get("mods") != [
                {"name": "CompanionAutoSummon", "version": "0.5.1-experimental", "path": "CompanionAutoSummon.py"},
                {"name": "CompanionMenuOrderTrial", "version": "0.9.1-diagnostics", "path": "CompanionMenuOrderTrial.py"}]):
        raise ValueError("Unexpected mod candidate")
    payload = {"runtime/" + name: data for name, data in runtime_files.items()}
    payload.update({"mod/" + name: data for name, data in mod_files.items()})
    for name in ("portable_launcher.py", "portable_host_support.py"):
        payload["app/" + name] = (ROOT / "tools" / name).read_bytes()
    payload["app/PortableLauncher.cs"] = (ROOT / "launcher/PortableLauncher.cs").read_bytes()
    numeric_version, identity_source = assembly_identity(VERSION)
    payload["app/AssemblyInfo.cs"] = identity_source.encode("utf-8")
    payload["app/PortableLauncher.manifest"] = application_manifest(numeric_version).encode("utf-8")
    payload["app/portable-locales.json"] = locale_resource(validated_catalogs()).encode("utf-8")
    payload["app/BUILD-LAUNCHER.txt"] = (ROOT / "launcher/BUILD-LAUNCHER.txt").read_bytes()
    for source, target in (("PORTABLE-QUICKSTART.md", "README.txt"),
                           ("PORTABLE-QUICKSTART.cs.md", "README.cs.txt"),
                           ("MULTIPLAYER-TEST.md", "Multiplayer test.txt")):
        payload[target] = (ROOT / "docs/release" / source).read_bytes()
    # Nexus requires inspectable files, not archives nested inside the release ZIP.
    for name, data in payload.items():
        reject_archive_payload(name, data)
    manifest = {
        "schema_version": 1, "version": VERSION,
        "name": "Companion Auto Summon for No Man's Sky", "author": "Lineum Dynamics",
        "combined_version": "0.9.2-play-trial", "production_version": "0.5.1-experimental",
        "menu_version": "0.9.1-diagnostics", "game_release": "Cosmos 7.04",
        "steam_build": "25442159", "no_external_python": True,
        "installs_dependencies_at_launch": False, "native_menu_language": "English",
        "live_verified": False, "multiplayer_verified": False,
        "nested_archives": False,
        "files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest()}
                  for name, data in sorted(payload.items())],
    }
    payload["portable-manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as target:
            target.write(data)
    executable = output / ENTRYPOINT
    compiled = build_entrypoint(output / "portable-manifest.json", executable)
    validate_distribution(output)
    code = ("import sys; sys.path.insert(0, " + repr(str(output / "app")) + "); "
            "import portable_host_support; "
            "portable_host_support.verify_runtime(" + repr(str(output / "runtime")) + ")")
    environment = {key: value for key, value in os.environ.items()
                   if key.upper() not in {"PYTEST_VERSION", "SPHINX_AUTODOC_RUNNING", "VIRTUAL_ENV"}}
    subprocess.run([str(output / "runtime/python.exe"), "-I", "-B", "-c", code],
                   timeout=60, check=True, capture_output=True, env=environment,
                   creationflags=subprocess.CREATE_NO_WINDOW)
    # The verification-only entry has no UI or Python/game dispatch.
    result = subprocess.run([str(executable), "--verify-only"], timeout=120, capture_output=True)
    if result.returncode:
        raise RuntimeError("Native entry point rejected final payload")
    payload[ENTRYPOINT] = executable.read_bytes()
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
        for name, data in sorted(payload.items()):
            zipped.writestr(name, data)
    with zipfile.ZipFile(archive) as zipped:
        if len(zipped.namelist()) != len(payload) or set(zipped.namelist()) != set(payload):
            raise RuntimeError("Archive allowlist differs")
        if any(zipped.read(name) != data for name, data in payload.items()):
            raise RuntimeError("Archive bytes differ")
    return {"version": VERSION, "directory": str(output), "archive": str(archive),
            "files": len(payload), "bytes": archive.stat().st_size,
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "entrypoint": compiled, "archive_verified": True,
            "final_runtime_check_passed": True,
            "entrypoint_integrity_gate_passed": True, "launched": False,
            "deployed": False, "live_verified": False, "multiplayer_verified": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--mod", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--archive", required=True, type=Path)
    options = parser.parse_args()
    print(json.dumps(build(options.runtime, options.mod, options.output, options.archive), indent=2))
