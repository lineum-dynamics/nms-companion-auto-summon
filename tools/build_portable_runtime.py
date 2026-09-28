"""Assemble a fresh pinned embedded runtime; never install globally or attach.

Downloads are optional and limited to the exact HTTPS lock entries. Wheels are
unpacked without executing setup, postinstall scripts, entry points or pip.
"""

import argparse
import base64
import csv
import hashlib
from io import BytesIO, StringIO
import json
from pathlib import Path, PurePosixPath
import re
import stat
import urllib.parse
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[1]
LOCK = Path(__file__).with_name("portable_runtime_lock.json")
MAX_ARCHIVE_BYTES = 100_000_000
MAX_MEMBER_BYTES = 50_000_000
MAX_EXPANDED_BYTES = 300_000_000
STDLIB_DIRECTORY = "Lib/stdlib"
PTH = b"Lib/stdlib\n.\nLib/site-packages\nLib/site-packages/win32\nLib/site-packages/win32/lib\nLib/site-packages/pythonwin\n"
ARCHIVE_SUFFIXES = frozenset({
    ".zip", ".zipx", ".7z", ".rar", ".tar", ".tgz", ".taz", ".gz", ".gzip",
    ".bz", ".bz2", ".tbz", ".tbz2", ".xz", ".txz", ".lz", ".lzma", ".tlz",
    ".z", ".zst", ".tzst", ".cab", ".cpio", ".iso", ".wim", ".esd",
    ".whl", ".egg", ".jar", ".war", ".ear", ".nupkg", ".appx", ".msix",
    ".appxbundle", ".msixbundle",
})
ARCHIVE_SIGNATURES = (
    b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08", b"7z\xbc\xaf\x27\x1c",
    b"Rar!\x1a\x07", b"MSCF", b"\x1f\x8b", b"BZh", b"\xfd7zXZ\x00",
    b"\x28\xb5\x2f\xfd", b"LZIP", b"\x1f\x9d", b"MSWIM\x00\x00\x00",
    b"070701", b"070702", b"070707",
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_member(name):
    """Reject paths that could escape or alias a Windows extraction root."""
    path = PurePosixPath(name)
    if (not name or any(ord(char) < 32 for char in name) or "\\" in name or path.is_absolute() or any(part in ("", ".", "..") for part in name.split("/"))
            or any(":" in part or part.endswith((".", " ")) for part in path.parts)
            or any(re.fullmatch(r"(?i)(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part) for part in path.parts)):
        raise ValueError("Unsafe archive member")
    return path


def reject_archive_payload(name, data):
    """Reject nested containers by filename or content; never disguise them.

The sole supported nested input is CPython's locked python311.zip, which is
expanded before this final-payload check. ZIP detection also finds prefixed
containers, rather than relying on their extension or first bytes alone.
    This check covers distribution archive/compression formats, not every
    container format. Vendor COFF static linker libraries remain unchanged;
    ZIP signatures and structure are still checked regardless of suffix.
"""
    if (PurePosixPath(name).suffix.casefold() in ARCHIVE_SUFFIXES
            or data.startswith(ARCHIVE_SIGNATURES)
            or data[257:262] == b"ustar"
            or (len(data) >= 32774 and data[32769:32774] == b"CD001")
            or has_zip_container(data)):
        raise ValueError("Nested archive payload is unsupported: " + name)


def has_zip_container(data):
    """Recognize a complete prefixed ZIP, not bytecode's ZIP signature constants.

CPython's zipimport.pyc contains a literal empty-directory marker. The standard
is_zipfile probe accepts that literal despite unrelated bytes following it, so
require the declared end-of-directory comment to end at the payload boundary.
"""
    end = data.rfind(b"PK\x05\x06", max(0, len(data) - 65557))
    if end < 0 or end + 22 > len(data):
        return False
    comment_length = int.from_bytes(data[end + 20:end + 22], "little")
    return end + 22 + comment_length == len(data) and zipfile.is_zipfile(BytesIO(data))


def claim_file(name, files, directories):
    """Reserve a Windows path without file/directory or case collisions."""
    path = safe_member(name)
    folded = name.casefold()
    parents = {parent.as_posix().casefold() for parent in path.parents if parent.parts}
    if folded in files or folded in directories or parents.intersection(files):
        raise ValueError("Archive or runtime files collide")
    files.add(folded)
    directories.update(parents)


def load_lock(path=LOCK):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != 1 or data.get("target") != "CPython 3.11.9 Windows x64":
        raise ValueError("Unsupported runtime lock")
    entries = [data["python"], *data["wheels"]]
    if data["python"]["version"] != "3.11.9" or len(data["wheels"]) != 20:
        raise ValueError("Unexpected locked runtime closure")
    seen = set()
    for entry in entries:
        name = entry["filename"]
        if len(safe_member(name).parts) != 1 or name.casefold() in seen:
            raise ValueError("Invalid or duplicate archive filename")
        seen.add(name.casefold())
        parsed = urllib.parse.urlparse(entry["url"])
        if parsed.scheme != "https" or parsed.hostname not in ("www.python.org", "files.pythonhosted.org"):
            raise ValueError("Unapproved runtime origin")
        if not re.fullmatch("[0-9a-f]{64}", entry["sha256"]) or not 0 < entry["bytes"] <= MAX_ARCHIVE_BYTES:
            raise ValueError("Invalid locked artifact identity")
    return data


def archive_bytes(entry, cache, download):
    path = cache / entry["filename"]
    if not path.exists():
        if not download:
            raise FileNotFoundError("A locked artifact is absent; download explicitly")
        with urllib.request.urlopen(entry["url"], timeout=45) as response:
            if urllib.parse.urlparse(response.url).hostname not in ("www.python.org", "files.pythonhosted.org"):
                raise ValueError("Unapproved download redirect")
            raw = response.read(MAX_ARCHIVE_BYTES + 1)
        if len(raw) != entry["bytes"] or digest(raw) != entry["sha256"]:
            raise ValueError("Downloaded artifact differs from the reviewed lock")
        cache.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(raw)
    raw = path.read_bytes()
    if len(raw) != entry["bytes"] or digest(raw) != entry["sha256"]:
        raise ValueError("Cached artifact differs from the reviewed lock")
    return raw


def read_archive(raw, wheel=False):
    """Read bounded, nonaliasing regular files; verify every wheel RECORD hash."""
    files, folded, directories, expanded_size = {}, set(), set(), 0
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        if len(archive.infolist()) > 10000:
            raise ValueError("Archive has too many entries")
        for entry in archive.infolist():
            if entry.is_dir():
                directory = safe_member(entry.filename.rstrip("/"))
                directory_paths = {directory.as_posix().casefold(), *(
                    parent.as_posix().casefold() for parent in directory.parents if parent.parts)}
                if directory_paths.intersection(folded):
                    raise ValueError("Archive files and directories collide")
                directories.update(directory_paths)
                continue
            safe_member(entry.filename)
            if stat.S_ISLNK(entry.external_attr >> 16) or not 0 <= entry.file_size <= MAX_MEMBER_BYTES:
                raise ValueError("Unsafe archive entry")
            claim_file(entry.filename, folded, directories)
            expanded_size += entry.file_size
            if expanded_size > MAX_EXPANDED_BYTES:
                raise ValueError("Expanded archive exceeds its bound")
            files[entry.filename] = archive.read(entry)
    if sum(map(len, files.values())) > MAX_EXPANDED_BYTES:
        raise ValueError("Expanded archive exceeds its bound")
    if wheel:
        records = [name for name in files if name.endswith(".dist-info/RECORD")]
        if len(records) != 1:
            raise ValueError("Expected one wheel RECORD")
        covered = set()
        for name, checksum, size in csv.reader(StringIO(files[records[0]].decode("utf-8"))):
            if name in covered or name not in files:
                raise ValueError("Wheel RECORD file set differs")
            covered.add(name)
            if name == records[0] and not checksum and not size:
                continue
            expected = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(files[name]).digest()).decode().rstrip("=")
            if checksum != expected or int(size) != len(files[name]):
                raise ValueError("Wheel RECORD checksum differs")
        if covered != set(files):
            raise ValueError("Wheel RECORD is incomplete")
    return files


def assemble(output, cache, *, download=False, lock_path=LOCK):
    output, cache = Path(output), Path(cache)
    if not output.is_absolute() or output.exists():
        raise ValueError("Supply a fresh absolute runtime output directory")
    lock = load_lock(lock_path)
    payload, owners, notices, sources = {}, {}, [], {}
    claimed, directories = set(), set()
    stdlib = None

    def add(name, data, owner):
        reject_archive_payload(name, data)
        claim_file(name, claimed, directories)
        payload[name] = data
        owners[name.casefold()] = owner

    for entry in [lock["python"], *lock["wheels"]]:
        is_python = entry is lock["python"]
        files = read_archive(archive_bytes(entry, cache, download), wheel=not is_python)
        licenses = []
        for name, data in files.items():
            if is_python and name == "python311.zip":
                members = read_archive(data)
                if not members:
                    raise ValueError("The Python standard-library archive is empty")
                stdlib = {"input_artifact": entry["filename"], "input_member": name,
                          "input_member_sha256": digest(data), "destination": STDLIB_DIRECTORY,
                          "member_count": len(members), "member_bytes_modified": False}
                for member, contents in members.items():
                    destination = STDLIB_DIRECTORY + "/" + member
                    add(destination, contents, entry["filename"])
                    sources[destination] = {"archive_member": name, "archive_sha256": stdlib["input_member_sha256"],
                                            "member": member}
                continue
            # Preserve installer scripts as inert data; never execute them.
            destination = name if is_python else "Lib/site-packages/" + name
            add(destination, data, entry["filename"])
            if (is_python and name == "LICENSE.txt") or (".dist-info/" in name and any(
                    word in name.casefold() for word in ("license", "licence", "copying", "notice", "authors"))):
                licenses.append({"path": destination, "sha256": digest(data)})
        if not licenses:
            raise ValueError("A runtime artifact lacks packaged license notices")
        notices.append({"artifact": entry["filename"], "url": entry["url"], "sha256": entry["sha256"],
                        "licenses": licenses})
    if stdlib is None:
        raise ValueError("The pinned Python standard-library archive is absent")
    original_pth = payload["python311._pth"]
    payload["python311._pth"] = PTH
    owners["python311._pth"] = "Companion Auto Summon owned relative-path configuration"
    for source, target in (("portable_sitecustomize.py", "sitecustomize.py"),):
        add(target, Path(__file__).with_name(source).read_bytes(), "Companion Auto Summon owned bootstrap")
    add("runtime-lock.json", (json.dumps(lock, indent=2) + "\n").encode(), "Reviewed artifact lock")
    add("THIRD-PARTY-NOTICES.json", (json.dumps(notices, indent=2) + "\n").encode(), "Artifact notice index")
    manifest = {"schema": 1, "python": "3.11.9", "platform": "win_amd64", "framework": "0.2.4",
                "vendor_wheel_bytes_modified": False, "python_path_configuration_replaced": True,
                "original_pth_sha256": digest(original_pth),
                "python_standard_library": stdlib, "nested_archives_shipped": False,
                "local_python_installation_required": False,
                "game_lifecycle_verified": False, "clean_windows_verified": False,
                "files": [{"path": name, "sha256": digest(data), "origin": owners[name.casefold()],
                           **({"source_archive": sources[name]} if name in sources else {})}
                          for name, data in sorted(payload.items())]}
    payload["runtime-manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    for name, data in payload.items():
        reject_archive_payload(name, data)
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if any((output / name).read_bytes() != data for name, data in payload.items()):
        raise RuntimeError("Runtime readback differs")
    return {"files": len(payload), "bytes": sum(map(len, payload.values())),
            "manifest_sha256": digest(payload["runtime-manifest.json"]), "assembled": True,
            "game_accessed": False, "installed_globally": False, "launched": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    print(json.dumps(assemble(args.output, args.cache, download=args.download)))
