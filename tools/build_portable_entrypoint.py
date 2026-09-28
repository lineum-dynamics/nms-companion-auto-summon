"""Compile the offline portable Windows entry point with a pinned manifest.

Uses the Windows .NET Framework compiler already present on supported systems.
It never installs dependencies or starts a game, launcher UI, or mod host.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from validate_locales import validated_catalogs

ROOT = Path(__file__).resolve().parents[1]


def compiler_path():
    windows = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    compiler = windows / "Microsoft.NET/Framework64/v4.0.30319/csc.exe"
    if not compiler.is_file():
        raise RuntimeError("The Windows .NET Framework 4 compiler is unavailable")
    return compiler


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
        messages = {code: {key: value["text"] for key, value in catalog["messages"].items()}
                    for code, catalog in catalogs.items()}
        catalog_path = staging / "portable-locales.json"
        catalog_path.write_text(json.dumps(messages, ensure_ascii=False), encoding="utf-8")
        executable = staging / "CompanionAutoSummon.exe"
        result = subprocess.run([
            str(compiler_path()), "/nologo", "/target:winexe", "/platform:x64", "/optimize+",
            "/reference:System.Windows.Forms.dll", "/reference:System.Drawing.dll",
            "/reference:System.Web.Extensions.dll", "/out:" + str(executable),
            "/resource:" + str(catalog_path) + ",PortableLocales", str(source_path),
        ], capture_output=True, text=True, timeout=60, check=False)
        if result.returncode:
            raise RuntimeError("Entry point compilation failed: " + result.stdout + result.stderr)
        with output_path.open("xb") as target:
            target.write(executable.read_bytes())
    return {"manifest_sha256": digest,
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
