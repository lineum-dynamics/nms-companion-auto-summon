"""Release boundaries using harmless fixture bytes; never compile or execute payloads."""

import hashlib
from importlib import util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import build_portable_distribution as distribution

SPEC = util.spec_from_file_location("cas_distribution_profile", ROOT / "cas_compatibility.py")
COMPATIBILITY = util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPATIBILITY)


class PortableDistributionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cas-release-boundary-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.runtime = self.root / "runtime"
        self.mod = self.root / "mod"
        self.runtime.mkdir()
        self.mod.mkdir()
        self.runtime_document = {
            "schema": 1, "python": "3.11.9", "platform": "win_amd64", "framework": "0.2.4",
            "files": self.write_payloads(self.runtime, {"python.exe": b"inert Python fixture", "pythonw.exe": b"inert windowed fixture"}),
        }
        self.mod_document = {
            "version": "0.9.2-play-trial", "framework": "pymhf[gui]==0.2.4",
            "steam_build": COMPATIBILITY.STEAM_BUILD,
            "supported_nms_exe_sha256": COMPATIBILITY.SUPPORTED_GAME_SHA256,
            "mods": [
                {"name": "CompanionAutoSummon", "version": "0.5.1-experimental", "path": "CompanionAutoSummon.py"},
                {"name": "CompanionMenuOrderTrial", "version": "0.9.1-diagnostics", "path": "CompanionMenuOrderTrial.py"},
            ],
            "files": self.write_payloads(self.mod, {"CompanionAutoSummon.py": b"owned mod fixture"}),
        }
        self.write_manifests()
        self.source = self.root / "source"
        for name in ("tools/portable_launcher.py", "tools/portable_host_support.py", "launcher/PortableLauncher.cs",
                     "launcher/PortableLauncher.manifest",
                     "launcher/BUILD-LAUNCHER.txt",
                     "docs/release/PORTABLE-QUICKSTART.md", "docs/release/PORTABLE-QUICKSTART.cs.md",
                     "docs/release/MULTIPLAYER-TEST.md"):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"Owned fixture documentation or code; never executed.\n")
        (self.source / "compatibility.json").write_bytes((ROOT / "compatibility.json").read_bytes())

    @staticmethod
    def write_payloads(folder, payloads):
        result = []
        for name, data in payloads.items():
            target = folder / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            result.append({"path": name, "sha256": hashlib.sha256(data).hexdigest()})
        return result

    def write_manifests(self):
        (self.runtime / "runtime-manifest.json").write_text(json.dumps(self.runtime_document), encoding="utf-8")
        (self.mod / "manifest.json").write_text(json.dumps(self.mod_document), encoding="utf-8")

    def build_with_traps(self, output, archive):
        with patch.object(distribution, "ROOT", self.source), \
                patch.object(distribution, "validate_locales"), \
                patch.object(distribution, "validate_compatibility"), \
                patch.object(distribution, "build_entrypoint", side_effect=AssertionError("Invalid input reached compilation")), \
                patch.object(distribution.subprocess, "run", side_effect=AssertionError("No child processes allowed")):
            return distribution.build(self.runtime, self.mod, output, archive)

    def test_manifest_allowlist_excludes_private_and_unlisted_files(self):
        for name in ("settings.json", "state.json", "saves/save.hg", "logs/host.log", "unlisted.py"):
            target = self.mod / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"Private test-only content")
        result = distribution.verified_files(self.mod, "manifest.json")
        self.assertEqual(set(result), {"CompanionAutoSummon.py", "manifest.json"})
        self.assertNotIn(b"Private test-only content", result.values())

    def test_changed_payload_checksum_is_rejected(self):
        (self.mod / "CompanionAutoSummon.py").write_bytes(b"tampered")
        with self.assertRaises(ValueError):
            distribution.verified_files(self.mod, "manifest.json")

    def test_traversal_and_absolute_input_paths_are_rejected(self):
        external = self.root / "private.txt"
        external.write_bytes(b"private")
        for path in ("../private.txt", external.as_posix(), "sub/../CompanionAutoSummon.py", "file:stream"):
            with self.subTest(path=path):
                self.mod_document["files"] = [{"path": path, "sha256": hashlib.sha256(b"private").hexdigest()}]
                self.write_manifests()
                with self.assertRaises((ValueError, FileNotFoundError)):
                    distribution.verified_files(self.mod, "manifest.json")

    def test_case_insensitive_duplicate_allowlist_entries_are_rejected(self):
        duplicate = dict(self.mod_document["files"][0], path="COMPANIONAUTOSUMMON.PY")
        self.mod_document["files"].append(duplicate)
        self.write_manifests()
        with self.assertRaises(ValueError):
            distribution.verified_files(self.mod, "manifest.json")

    def test_duplicate_manifest_object_fields_are_rejected(self):
        (self.mod / "manifest.json").write_text('{"files": [], "files": []}', encoding="utf-8")
        with self.assertRaises(ValueError):
            distribution.verified_files(self.mod, "manifest.json")

    def test_self_manifest_record_cannot_reuse_an_old_manifest_digest(self):
        checksum = hashlib.sha256((self.mod / "manifest.json").read_bytes()).hexdigest()
        self.mod_document["files"].append({"path": "manifest.json", "sha256": checksum})
        self.write_manifests()
        with self.assertRaises(ValueError):
            distribution.verified_files(self.mod, "manifest.json")

    def test_invalid_runtime_identity_refuses_before_any_output(self):
        for index, (field, value) in enumerate((("schema", 2), ("python", "3.12.0"),
                                               ("platform", "win32"), ("framework", "0.2.5"))):
            with self.subTest(field=field):
                previous = self.runtime_document[field]
                self.runtime_document[field] = value
                self.write_manifests()
                output = self.root / ("invalid-runtime-" + str(index))
                archive = self.root / ("invalid-runtime-" + str(index) + ".zip")
                with self.assertRaises(ValueError):
                    self.build_with_traps(output, archive)
                self.assertFalse(output.exists())
                self.assertFalse(archive.exists())
                self.runtime_document[field] = previous

    def test_invalid_mod_version_build_or_framework_refuses_before_any_output(self):
        for index, (field, value) in enumerate((("version", "0.9.1-play-trial"), ("steam_build", "other-build"),
                                               ("supported_nms_exe_sha256", "0" * 64),
                                               ("framework", "pymhf[gui]==0.2.5"), ("mods", []))):
            with self.subTest(field=field):
                previous = self.mod_document[field]
                self.mod_document[field] = value
                self.write_manifests()
                output = self.root / ("invalid-mod-" + str(index))
                archive = self.root / ("invalid-mod-" + str(index) + ".zip")
                with self.assertRaises(ValueError):
                    self.build_with_traps(output, archive)
                self.assertFalse(output.exists())
                self.assertFalse(archive.exists())
                self.mod_document[field] = previous

    def test_existing_output_is_preserved(self):
        output = self.root / "existing"
        output.mkdir()
        marker = output / "keep.txt"
        marker.write_bytes(b"preserve")
        archive = self.root / "new.zip"
        with self.assertRaises(ValueError):
            self.build_with_traps(output, archive)
        self.assertEqual(marker.read_bytes(), b"preserve")
        self.assertFalse(archive.exists())

    def test_nested_archive_is_rejected_before_compilation_or_output(self):
        from io import BytesIO
        content = BytesIO()
        with zipfile.ZipFile(content, "w") as archive:
            archive.writestr("data.txt", b"nested content")
        for index, name in enumerate(("python311.zip", "disguised.dat")):
            with self.subTest(name=name):
                previous = list(self.runtime_document["files"])
                self.runtime_document["files"].extend(self.write_payloads(self.runtime, {name: content.getvalue()}))
                self.write_manifests()
                output = self.root / ("nested-" + str(index))
                destination = self.root / ("nested-" + str(index) + ".zip")
                with self.assertRaises(ValueError):
                    self.build_with_traps(output, destination)
                self.assertFalse(output.exists())
                self.assertFalse(destination.exists())
                self.runtime_document["files"] = previous

    def test_assembly_records_explicit_payloads_after_required_offline_gates(self):
        (self.runtime / "developer-secret.txt").write_bytes(b"private runtime source")
        (self.mod / "state.json").write_bytes(b"private mod state")
        output, archive = self.root / "assembled", self.root / "assembled.zip"
        def fake_compile(manifest, target):
            target.write_bytes(b"inert fixture entry point")
            return {"manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest()}
        with patch.object(distribution, "ROOT", self.source), \
                patch.object(distribution, "validate_locales") as locales, \
                patch.object(distribution, "validate_compatibility") as compatibility, \
                patch.object(distribution, "build_entrypoint", side_effect=fake_compile), \
                patch.object(distribution, "validate_distribution") as gate, \
                patch.object(distribution.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as process:
            receipt = distribution.build(self.runtime, self.mod, output, archive)
        locales.assert_called_once()
        compatibility.assert_called_once()
        gate.assert_called_once_with(output)
        self.assertEqual(process.call_count, 2)
        self.assertEqual(process.call_args_list[0].args[0][1:4], ["-I", "-B", "-c"])
        self.assertEqual(process.call_args_list[1].args[0][1:], ["--verify-only"])
        self.assertTrue(receipt["archive_verified"])
        self.assertTrue(receipt["final_runtime_check_passed"])
        self.assertFalse(receipt["launched"])
        self.assertFalse(receipt["deployed"])
        self.assertFalse(receipt["live_verified"])
        self.assertFalse(receipt["multiplayer_verified"])
        with zipfile.ZipFile(archive) as package:
            self.assertNotIn("runtime/developer-secret.txt", package.namelist())
            self.assertNotIn("mod/state.json", package.namelist())
            manifest = json.loads(package.read("portable-manifest.json"))
            listed = {entry["path"] for entry in manifest["files"]}
            self.assertEqual(listed | {"portable-manifest.json", distribution.ENTRYPOINT}, set(package.namelist()))
            for entry in manifest["files"]:
                self.assertEqual(hashlib.sha256(package.read(entry["path"])).hexdigest(), entry["sha256"])


if __name__ == "__main__":
    unittest.main()
