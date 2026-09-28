"""Portable archive validation tests: no downloads, framework or game access."""

import base64
import hashlib
from importlib import util
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import json


spec = util.spec_from_file_location("portable_runtime_builder_tests", Path(__file__).resolve().parents[1] / "build_portable_runtime.py")
builder = util.module_from_spec(spec)
spec.loader.exec_module(builder)


def archive(entries):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as stream:
        for name, data in entries:
            stream.writestr(name, data)
    return buffer.getvalue()


def assemble_fixture(output, python_entries):
    """Use owned fake input bytes; exercise extraction, provenance and writes."""
    raw = archive(python_entries)
    python_entry = {"filename": "python-3.11.9-embed-amd64.zip", "sha256": builder.digest(raw),
                    "url": "https://www.python.org/test-fixture", "bytes": len(raw)}
    lock = {"python": python_entry, "wheels": []}
    with patch.object(builder, "load_lock", return_value=lock), \
            patch.object(builder, "archive_bytes", return_value=raw):
        return builder.assemble(output, output.parent / "cache")


def python_fixture(stdlib, extra=()):
    return [("python311.zip", stdlib), ("python311._pth", b"python311.zip\n.\n"),
            ("LICENSE.txt", b"Test fixture license"), ("python311.dll", b"MZowned fixture"), *extra]


class PortableRuntimeTests(unittest.TestCase):
    def test_path_rejection_covers_windows_aliases_and_escape(self):
        for name in ("../escape", "/absolute", "a\\b", "c:stream", "a//b", "a/./b", "a/../b", "a. ", "CON", "com1.txt", "nul/x", "bad\0path"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                builder.safe_member(name)
        self.assertEqual(str(builder.safe_member("Lib/site-packages/valid.py")), "Lib/site-packages/valid.py")

    def test_archive_rejects_case_aliases_and_traversal(self):
        for entries in ((("same.py", b"x"), ("SAME.py", b"y")), (("../outside", b"x"),)):
            with self.assertRaises(ValueError):
                builder.read_archive(archive(entries))

    def test_archive_rejects_file_directory_collisions_before_writes(self):
        for entries in (
                (("a", b"x"), ("a/b.py", b"y")),
                (("a/b.py", b"y"), ("A", b"x")),
                (("a/", b""), ("A", b"x")),
                (("A", b"x"), ("a/", b""))):
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                builder.read_archive(archive(entries))

    def test_archive_checks_expanded_bound_before_reading_payload(self):
        raw = archive((("one", b"123"), ("two", b"456")))
        with patch.object(builder, "MAX_EXPANDED_BYTES", 5), self.assertRaisesRegex(ValueError, "bound"):
            builder.read_archive(raw)

    def test_final_payload_rejects_archive_suffixes_and_content(self):
        cases = [("hidden.dat", magic + b"owned fixture") for magic in builder.ARCHIVE_SIGNATURES]
        cases.extend(("nested" + suffix.upper(), b"no recognizable magic") for suffix in builder.ARCHIVE_SUFFIXES)
        cases.extend((
            ("hidden-tar.dat", b"\0" * 257 + b"ustar" + b"\0" * 300),
            ("prefixed.dat", b"MZowned prefix" + archive((("inner.txt", b"x"),))),
        ))
        for name, data in cases:
            with self.subTest(name=name, data=data[:8]), self.assertRaisesRegex(ValueError, "Nested archive"):
                builder.reject_archive_payload(name, data)
        builder.reject_archive_payload("normal.dll", b"MZordinary native bytes")
        builder.reject_archive_payload("normal.pyc", b"\xa7\x0d\x0d\x0aordinary bytecode fixture")
        builder.reject_archive_payload("native.lib", b"!<arch>\nowned linker fixture")
        with self.assertRaisesRegex(ValueError, "Nested archive"):
            builder.reject_archive_payload("disguised.lib", archive((("a.txt", b"a"),)))

    def test_zip_signature_constants_inside_bytecode_are_not_a_nested_archive(self):
        # zipimport.pyc contains a literal empty ZIP marker, not a ZIP container.
        bytecode = b"\xa7\x0d\x0d\x0aowned constants" + archive(()) + b"more bytecode instructions"
        self.assertTrue(zipfile.is_zipfile(BytesIO(bytecode)))
        builder.reject_archive_payload("zipimport.pyc", bytecode)
        with self.assertRaisesRegex(ValueError, "Nested archive"):
            builder.reject_archive_payload("prefixed-empty.dat", b"owned prefix" + archive(()))

    def test_stdlib_extracts_exact_members_with_original_archive_provenance(self):
        members = [("os.pyc", b"\xa7\x0d\x0d\x0aowned os bytecode"),
                   ("encodings/__init__.pyc", b"\xa7\x0d\x0d\x0aowned package bytecode"),
                   ("LICENSE.txt", b"unchanged standard-library notice")]
        nested = archive(members)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "runtime"
            result = assemble_fixture(output, python_fixture(nested))
            manifest = json.loads((output / "runtime-manifest.json").read_text(encoding="utf-8"))
            self.assertFalse((output / "python311.zip").exists())
            self.assertEqual((output / "python311._pth").read_bytes().splitlines()[0], b"Lib/stdlib")
            self.assertNotIn(b"python311.zip", (output / "python311._pth").read_bytes())
            self.assertEqual((output / "python311.dll").read_bytes(), b"MZowned fixture")
            self.assertEqual(manifest["python_standard_library"]["input_member_sha256"], builder.digest(nested))
            self.assertEqual(manifest["python_standard_library"]["member_count"], len(members))
            self.assertFalse(manifest["python_standard_library"]["member_bytes_modified"])
            self.assertFalse(manifest["nested_archives_shipped"])
            files = {entry["path"]: entry for entry in manifest["files"]}
            for member, data in members:
                name = "Lib/stdlib/" + member
                self.assertEqual((output / name).read_bytes(), data)
                self.assertEqual(files[name]["sha256"], builder.digest(data))
                self.assertEqual(files[name]["source_archive"], {
                    "archive_member": "python311.zip", "archive_sha256": builder.digest(nested), "member": member})
            self.assertFalse(result["game_accessed"])

    def test_stdlib_unsafe_members_and_destination_collision_refuse_output(self):
        cases = [python_fixture(archive(entries)) for entries in (
            (("../escape.pyc", b"x"),),
            (("os.pyc", b"x"), ("OS.pyc", b"y")),
            (("package", b"x"), ("package/module.pyc", b"y")),
        )]
        cases.append(python_fixture(archive((("os.pyc", b"x"),)),
                                    extra=(("Lib/stdlib/OS.pyc", b"collision"),)))
        cases.append(python_fixture(archive((("os.pyc", b"x"),)),
                                    extra=(("Lib/STDLIB", b"file-directory collision"),)))
        for entries in cases:
            with self.subTest(entries=[name for name, _ in entries]), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "runtime"
                with self.assertRaises(ValueError):
                    assemble_fixture(output, entries)
                self.assertFalse(output.exists())

    def test_unapproved_nested_containers_are_not_shipped_or_renamed(self):
        ordinary_stdlib = archive((("os.pyc", b"ordinary bytecode fixture"),))
        cases = [
            python_fixture(ordinary_stdlib, (("other.zip", archive((("a.txt", b"a"),))),)),
            python_fixture(ordinary_stdlib, (("disguised.dat", archive((("a.txt", b"a"),))),)),
            python_fixture(archive((("inside.zip", archive((("a.txt", b"a"),))),))),
        ]
        for entries in cases:
            with tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "runtime"
                with self.assertRaisesRegex(ValueError, "Nested archive"):
                    assemble_fixture(output, entries)
                self.assertFalse(output.exists())

    def test_missing_or_empty_stdlib_refuses_output(self):
        for entries in (python_fixture(archive(())), [("LICENSE.txt", b"notice")]):
            with tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "runtime"
                with self.assertRaisesRegex(ValueError, "standard-library"):
                    assemble_fixture(output, entries)
                self.assertFalse(output.exists())

    def test_wheel_record_checks_full_set_size_and_digest(self):
        data = b"owned payload"
        checksum = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
        record = f"module.py,{checksum},{len(data)}\nowned.dist-info/RECORD,,\n".encode()
        good = [("module.py", data), ("owned.dist-info/RECORD", record)]
        self.assertEqual(builder.read_archive(archive(good), wheel=True)["module.py"], data)
        for entries in ([("module.py", data+b"x"), good[1]], good+[("unlisted.py", b"x")], good[:1]):
            with self.assertRaises(ValueError):
                builder.read_archive(archive(entries), wheel=True)

    def test_cached_artifact_needs_exact_locked_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            cache = Path(folder)
            (cache / "artifact.zip").write_bytes(b"bad")
            entry = {"filename":"artifact.zip", "bytes":3, "sha256":hashlib.sha256(b"yes").hexdigest()}
            with self.assertRaises(ValueError):
                builder.archive_bytes(entry, cache, False)

    def test_missing_artifact_never_downloads_implicitly(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                builder.archive_bytes({"filename":"absent.zip"}, Path(folder), False)

    def test_existing_output_is_never_reused_or_modified(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            sentinel = path / "keep"
            sentinel.write_bytes(b"existing runtime")
            with self.assertRaises(ValueError):
                builder.assemble(path, path)
            self.assertEqual(sentinel.read_bytes(), b"existing runtime")

    def test_reviewed_lock_has_exact_framework_and_python_artifacts(self):
        lock = builder.load_lock()
        self.assertEqual(lock["python"]["version"], "3.11.9")
        self.assertEqual(len(lock["wheels"]), 20)
        pins = {entry["name"]:entry["version"] for entry in lock["wheels"]}
        self.assertEqual(pins["pymhf"], "0.2.4")
        self.assertEqual(pins["pyrun-injected"], "0.2.0")
        self.assertEqual(pins["dearpygui"], "2.3.1")


if __name__ == "__main__":
    unittest.main()
