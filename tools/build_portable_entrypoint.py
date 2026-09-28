"""Compile the offline portable Windows entry point with a pinned manifest.

Uses the Windows .NET Framework compiler already present on supported systems.
It never installs dependencies or starts a game, launcher UI, or mod host.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from validate_locales import validated_catalogs

ROOT = Path(__file__).resolve().parents[1]


def assembly_identity(version):
    """Use the reviewed release version in Windows file and assembly metadata."""
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-[A-Za-z0-9.-]+)?", str(version))
    if not match or any(int(part) > 65534 for part in match.groups()):
        raise ValueError("A supported release version is required for the entry point")
    numeric = ".".join(str(int(part)) for part in match.groups()) + ".0"
    source = '\n'.join((
        'using System.Reflection;',
        '[assembly: AssemblyTitle("Companion Auto Summon for No Man\'s Sky")]',
        '[assembly: AssemblyProduct("Companion Auto Summon for No Man\'s Sky")]',
        '[assembly: AssemblyCompany("Lineum Dynamics")]',
        '[assembly: AssemblyDescription("Portable launcher and package integrity verifier")]',
        '[assembly: AssemblyVersion("' + numeric + '")]',
        '[assembly: AssemblyFileVersion("' + numeric + '")]',
        '[assembly: AssemblyInformationalVersion("' + version + '")]',
        '',
    ))
    return numeric, source


def compiler_path():
    windows = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    compiler = windows / "Microsoft.NET/Framework64/v4.0.30319/csc.exe"
    if not compiler.is_file():
        raise RuntimeError("The Windows .NET Framework 4 compiler is unavailable")
    return compiler


def application_manifest(numeric_version):
    template = (ROOT / "launcher/PortableLauncher.manifest").read_text(encoding="utf-8")
    if template.count("@@ASSEMBLY_VERSION@@") != 1:
        raise ValueError("Application manifest version placeholder is invalid")
    return template.replace("@@ASSEMBLY_VERSION@@", numeric_version)


def locale_resource(catalogs):
    messages = {code: {key: value["text"] for key, value in catalog["messages"].items()}
                for code, catalog in catalogs.items()}
    return json.dumps(messages, ensure_ascii=False)


def build(manifest_path, output_path):
    """Compile one entry point; the distribution owner verifies payload hashes."""
    manifest_path = Path(manifest_path).resolve(strict=True)
    output_path = Path(output_path).resolve()
    if output_path.exists():
        raise FileExistsError("Refusing to overwrite an existing entry point")
    if output_path.suffix.lower() != ".exe":
        raise ValueError("The entry point must have an .exe extension")
    manifest_bytes = manifest_path.read_bytes()
    if len(manifest_bytes) > 8 * 1024 * 1024:
        raise ValueError("Portable manifest exceeds its size bound")
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), list):
        raise ValueError("Unsupported portable manifest")
    numeric_version, assembly_source = assembly_identity(manifest.get("version"))
    catalogs = validated_catalogs()
    digest = hashlib.sha256(manifest_bytes).hexdigest()
    source = (ROOT / "launcher/PortableLauncher.cs").read_text(encoding="utf-8")
    if source.count("@@MANIFEST_SHA256@@") != 1:
        raise ValueError("Manifest digest placeholder is missing or duplicated")
    source = source.replace("@@MANIFEST_SHA256@@", digest)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cas-entrypoint-build-") as temporary:
        staging = Path(temporary)
        source_path = staging / "PortableLauncher.cs"
        source_path.write_text(source, encoding="utf-8")
        identity_path = staging / "AssemblyInfo.cs"
        identity_path.write_bytes(assembly_source.encode("utf-8"))
        application_manifest_path = staging / "PortableLauncher.manifest"
        application_manifest_path.write_bytes(application_manifest(numeric_version).encode("utf-8"))
        catalog_path = staging / "portable-locales.json"
        catalog_path.write_bytes(locale_resource(catalogs).encode("utf-8"))
        executable = staging / "CompanionAutoSummon.exe"
        result = subprocess.run([
            str(compiler_path()), "/nologo", "/target:winexe", "/platform:x64", "/optimize+",
            "/reference:System.Windows.Forms.dll", "/reference:System.Drawing.dll",
            "/reference:System.Web.Extensions.dll", "/out:" + str(executable),
            "/win32manifest:" + str(application_manifest_path),
            "/resource:" + str(catalog_path) + ",PortableLocales", str(source_path), str(identity_path),
        ], capture_output=True, text=True, timeout=60, check=False)
        if result.returncode:
            raise RuntimeError("Entry point compilation failed: " + result.stdout + result.stderr)
        with output_path.open("xb") as target:
            target.write(executable.read_bytes())
    return {"manifest_sha256": digest, "file_version": numeric_version,
            "product_version": manifest["version"], "company": "Lineum Dynamics",
            "exe_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
            "bytes": output_path.stat().st_size}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    options = parser.parse_args(argv)
    print(json.dumps(build(options.manifest, options.output), sort_keys=True))


if __name__ == "__main__":
    main()
