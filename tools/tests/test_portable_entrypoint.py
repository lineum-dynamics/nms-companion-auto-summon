"""Compile the real gate against harmless fixtures; never open UI or execute Python."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import build_portable_entrypoint as ENTRYPOINT
import validate_locales as LOCALES


@unittest.skipUnless(os.name == "nt", "Windows .NET Framework executable tests")
class EntryPointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="cas-portable-gate-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.parent = Path(cls.temporary.name)
        cls.source = cls.parent / "fixture"
        cls.source.mkdir()
        records = []
        for relative in ("runtime/python.exe", "runtime/pythonw.exe", "app/portable_launcher.py", "mod/locales/en.json"):
            target = cls.source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"Harmless test fixture, not an executable.\n")
            records.append({"path": relative, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        cls.document = {"schema_version": 1, "version": "0.9.3-test", "files": records}
        cls.manifest = cls.source / "portable-manifest.json"
        cls.manifest.write_text(json.dumps(cls.document), encoding="utf-8")
        cls.receipt = ENTRYPOINT.build(cls.manifest, cls.source / "CompanionAutoSummon.exe")

    def setUp(self):
        self.destination = self.parent / self.id().split(".")[-1]
        shutil.copytree(self.source, self.destination)

    def verify(self, expected):
        process = subprocess.run([str(self.destination / "CompanionAutoSummon.exe"), "--verify-only"],
                                 creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
        self.assertEqual(process.returncode, expected)

    def new_manifest(self, change):
        manifest = json.loads(json.dumps(self.document))
        change(manifest)
        target = self.destination / "portable-manifest.json"
        target.write_text(json.dumps(manifest), encoding="utf-8")
        (self.destination / "CompanionAutoSummon.exe").unlink()
        ENTRYPOINT.build(target, self.destination / "CompanionAutoSummon.exe")

    def test_complete_matching_package_is_accepted_without_running_payload(self):
        self.verify(0)
        self.assertEqual(self.receipt["manifest_sha256"], hashlib.sha256(self.manifest.read_bytes()).hexdigest())

    def test_relocated_package_with_spaces_and_unicode_is_accepted(self):
        relocated = self.destination.with_name("Package spaces čínský 日本")
        self.destination.rename(relocated)
        self.destination = relocated
        self.verify(0)

    def test_changed_manifest_is_rejected(self):
        with (self.destination / "portable-manifest.json").open("ab") as stream:
            stream.write(b" ")
        self.verify(2)

    def test_missing_payload_is_rejected(self):
        (self.destination / "runtime/pythonw.exe").unlink()
        self.verify(2)

    def test_changed_payload_is_rejected(self):
        (self.destination / "runtime/python.exe").write_bytes(b"changed")
        self.verify(2)

    def test_unlisted_runtime_dependency_is_rejected(self):
        (self.destination / "runtime/unlisted.dll").write_bytes(b"foreign")
        self.verify(2)

    def test_case_insensitive_duplicate_is_rejected(self):
        self.new_manifest(lambda data: data["files"].append(dict(data["files"][0], path="RUNTIME/PYTHON.EXE")))
        self.verify(2)

    def test_traversal_is_rejected_even_with_trusted_manifest_digest(self):
        self.new_manifest(lambda data: data["files"].append(dict(data["files"][0], path="runtime/../runtime/python.exe")))
        self.verify(2)

    def test_absolute_path_is_rejected_even_with_trusted_manifest_digest(self):
        self.new_manifest(lambda data: data["files"].append(dict(data["files"][0], path="C:/Windows/system32/cmd.exe")))
        self.verify(2)

    def test_alternate_stream_path_is_rejected(self):
        self.new_manifest(lambda data: data["files"].append(dict(data["files"][0], path="runtime/python.exe:stream")))
        self.verify(2)

    def test_backslash_path_is_rejected(self):
        self.new_manifest(lambda data: data["files"].append(dict(data["files"][0], path="runtime\\python.exe")))
        self.verify(2)

    def test_missing_required_file_record_is_rejected(self):
        self.new_manifest(lambda data: data["files"].pop(0))
        self.verify(2)

    def test_manifest_version_is_required(self):
        with self.assertRaises(ValueError):
            self.new_manifest(lambda data: data.pop("version"))

    def test_windows_file_properties_identify_the_actual_release(self):
        path = str(self.destination / "CompanionAutoSummon.exe").replace("'", "''")
        command = ("[Diagnostics.FileVersionInfo]::GetVersionInfo('" + path + "') | "
                   "Select-Object FileDescription,ProductName,CompanyName,FileVersion,ProductVersion | ConvertTo-Json")
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command],
                                capture_output=True, timeout=30, check=True,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        data = json.loads(result.stdout.decode("utf-8-sig"))
        self.assertEqual(data["FileDescription"], "Companion Auto Summon for No Man's Sky")
        self.assertEqual(data["ProductName"], "Companion Auto Summon for No Man's Sky")
        self.assertEqual(data["CompanyName"], "Lineum Dynamics")
        self.assertEqual(data["FileVersion"], "0.9.3.0")
        self.assertEqual(data["ProductVersion"], "0.9.3-test")

    def test_invalid_version_cannot_enter_generated_csharp_or_manifest(self):
        for version in (None, "offline-test", "0.9.3\"", "65535.0.0", "1.2.3/4", "1.2.3\n"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                ENTRYPOINT.assembly_identity(version)

    def test_junction_directory_is_rejected(self):
        target = self.parent / "junction-target"
        target.mkdir()
        junction = self.destination / "unlisted-junction"
        # Native PowerShell only, with exact literal fixture paths; no elevated setup.
        quoted_path = str(junction).replace("'", "''")
        quoted_target = str(target).replace("'", "''")
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                                 "New-Item -ItemType Junction -Path '" + quoted_path + "' -Target '" + quoted_target + "' | Out-Null"],
                                capture_output=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.addCleanup(junction.rmdir)
        self.verify(2)

    def test_builder_refuses_existing_entrypoint(self):
        with self.assertRaises(FileExistsError):
            ENTRYPOINT.build(self.manifest, self.source / "CompanionAutoSummon.exe")

    def test_windows_argument_quoting_round_trips_through_native_process(self):
        temporary = self.parent / "quoting"
        temporary.mkdir()
        source = (ROOT / "launcher/PortableLauncher.cs").read_text(encoding="utf-8")
        harness = temporary / "Harness.cs"
        harness.write_text(source + r'''
internal static class QuoteHarness {
    public static int Main(string[] args) {
        if (args.Length == 2 && args[0] == "child") {
            System.Console.OutputEncoding = new System.Text.UTF8Encoding(false);
            System.Console.Write(args[1]); return 0;
        }
        var info = new System.Diagnostics.ProcessStartInfo {
            FileName = System.Reflection.Assembly.GetExecutingAssembly().Location,
            Arguments = "child " + CompanionAutoSummon.Portable.Package.Quote(args[0]),
            UseShellExecute = false, CreateNoWindow = true, RedirectStandardOutput = true,
            StandardOutputEncoding = new System.Text.UTF8Encoding(false)
        };
        using (var process = System.Diagnostics.Process.Start(info)) {
            string result = process.StandardOutput.ReadToEnd(); process.WaitForExit();
            return result == args[0] ? 0 : 3;
        }
    }
}
''', encoding="utf-8")
        executable = temporary / "quoting.exe"
        subprocess.run([str(ENTRYPOINT.compiler_path()), "/nologo", "/target:exe", "/main:QuoteHarness",
                        "/reference:System.Windows.Forms.dll", "/reference:System.Drawing.dll",
                        "/reference:System.Web.Extensions.dll", "/out:" + str(executable), str(harness)],
                       capture_output=True, timeout=30, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        for value in ("", "ordinary", "path with spaces", 'quote"inside', 'C:\\game spaces\\',
                      "C:\\žluťoučký\\日本", 'end\\\\"', '$(whoami); & ignored'):
            with self.subTest(value=value):
                result = subprocess.run([str(executable), value], timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
                self.assertEqual(result.returncode, 0)


class PortableCatalogTests(unittest.TestCase):
    def test_runtime_repair_link_is_the_same_official_x64_installer_in_every_locale(self):
        catalogs = LOCALES.validated_catalogs()
        link = "https://aka.ms/vc14/vc_redist.x64.exe"
        for locale, catalog in catalogs.items():
            with self.subTest(locale=locale):
                text = catalog["messages"]["portable.native_runtime_missing"]["text"]
                self.assertEqual(text.count(link), 1)
                self.assertIn("Microsoft Visual C++", text)
                self.assertIn("x64", text)

    def test_every_portable_message_has_current_draft_translations(self):
        catalogs = LOCALES.validated_catalogs()
        self.assertEqual(len(LOCALES.PORTABLE_KEYS), 17)
        for key in LOCALES.PORTABLE_KEYS:
            english = catalogs["en"]["messages"][key]["text"]
            for locale, catalog in catalogs.items():
                with self.subTest(key=key, locale=locale):
                    entry = catalog["messages"][key]
                    self.assertEqual(entry["source_sha256"], LOCALES.source_fingerprint(english))
                    if locale != "en":
                        self.assertNotEqual(entry["text"], english)
                        self.assertEqual(catalog["review_status"], "draft_unreviewed")


if __name__ == "__main__":
    unittest.main()
