"""Portable archive validation tests: no downloads, framework or game access."""

import base64
import hashlib
from importlib import util
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
import zipfile


spec = util.spec_from_file_location("portable_runtime_builder_tests", Path(__file__).resolve().parents[1] / "build_portable_runtime.py")
builder = util.module_from_spec(spec)
spec.loader.exec_module(builder)


def archive(entries):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as stream:
        for name, data in entries:
            stream.writestr(name, data)
    return buffer.getvalue()


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
