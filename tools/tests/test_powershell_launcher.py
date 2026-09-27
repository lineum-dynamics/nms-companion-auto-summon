"""Execute the launcher against owned files and stubbed process/runtime probes.

No real game, process enumeration, dependency installation or injection occurs.
Each fixture replaces the fixed mutex name with its own random test namespace.
"""

import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import struct
import sys
import tempfile
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Start-CompanionAutoSummon.ps1"
POWERSHELL = shutil.which("powershell.exe")
LEASE_NAME = "Local\\CompanionAutoSummon.Setup.v1"


@unittest.skipUnless(os.name == "nt" and POWERSHELL, "Windows PowerShell required")
class PowerShellLauncherTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cas-powershell-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.bundle = self.root / "owned package"
        self.bundle.mkdir()
        self.game = self.root / "owned game"
        (self.game / "Binaries").mkdir(parents=True)
        (self.game / "Binaries/NMS.exe").write_bytes(b"synthetic executable")
        self.local = self.root / "owned local"
        self.runtime = self.local / "NMS-AutoPet/runtime-0.2.4/Scripts/python.exe"
        self.runtime.parent.mkdir(parents=True)
        self.runtime.write_bytes(b"synthetic runtime path; never executed")
        self.lease = "Local\\CAS.Test." + uuid.uuid4().hex
        self.script = self.bundle / SOURCE.name
        text = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(text.count(LEASE_NAME), 1)
        text = text.replace(LEASE_NAME, self.lease)
        self.assertEqual(text.count("$setupLease = $null"), 1)
        text = text.replace("$setupLease = $null", r'''
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
function Get-Process {
    [CmdletBinding()]
    param()
    if ($ErrorActionPreference -ne 'Stop') { throw 'Process query did not fail closed' }
    if ($env:CAS_TEST_PROCESSES -eq 'error') { throw 'Synthetic enumeration failure' }
    if ($env:CAS_TEST_PROCESSES -eq 'running') {
        [pscustomobject]@{ ProcessName = 'NMS' }
    }
    [pscustomobject]@{ ProcessName = 'NotTheGame' }
}
function Get-PythonInfo {
    param([string]$Executable, [string[]]$Arguments = @())
    Write-Host 'TEST_PROBE'
    if ($env:CAS_TEST_INFO -eq 'null') { return $null }
    return $env:CAS_TEST_INFO | ConvertFrom-Json
}
function Find-Python { throw 'Unexpected runtime creation' }
function Find-SteamGameDirectories { return @() }
$setupLease = $null''')
        text = text.replace("$setupLease.Dispose()", "$setupLease.Dispose(); Write-Host 'TEST_DISPOSE'")
        self.script.write_text(text, encoding="utf-8-sig")
        (self.bundle / "CompanionAutoSummon.py").write_bytes(b"# synthetic mod\n")
        self.bootstrap = self.bundle / "Launch-CompanionAutoSummon.py"
        self.bootstrap.write_text('''import ctypes as C
import os
import sys
arguments = sys.argv[2:]
assert arguments[arguments.index("--game-directory") + 1] == os.environ["CAS_TEST_GAME"]
assert arguments[arguments.index("--language") + 1] == os.environ["CAS_TEST_LANGUAGE"]
assert "--no-dialog" in arguments
k = C.WinDLL("kernel32", use_last_error=True)
k.CreateMutexW.argtypes = (C.c_void_p, C.c_bool, C.c_wchar_p)
k.CreateMutexW.restype = C.c_void_p
k.CloseHandle.argtypes = (C.c_void_p,)
k.CloseHandle.restype = C.c_bool
handle = k.CreateMutexW(None, False, os.environ["CAS_TEST_LEASE"])
error = C.get_last_error()
assert handle and error == 183, "setup lease must survive into child"
assert k.CloseHandle(handle)
print("TEST_CHILD_LEASE_HELD")
raise SystemExit(int(os.environ.get("CAS_TEST_CHILD_EXIT", "0")))
''', encoding="utf-8")
        shutil.copyfile(ROOT / "cas_compatibility.py", self.bundle / "cas_compatibility.py")
        shutil.copytree(ROOT / "locales", self.bundle / "locales")
        self.profile = {"schema_version": 1, "steam_build": "owned-build", "game_release": "Owned release",
                        "exe_sha256": hashlib.sha256((self.game / "Binaries/NMS.exe").read_bytes()).hexdigest(),
                        "framework_version": "0.2.4"}
        (self.bundle / "compatibility.json").write_text(json.dumps(self.profile), encoding="utf-8")
        payload = ("CompanionAutoSummon.py", "Launch-CompanionAutoSummon.py", "cas_compatibility.py",
                   "compatibility.json", *(str(path.relative_to(self.bundle)).replace("\\", "/")
                                           for path in sorted((self.bundle / "locales").glob("*.json"))))
        self.manifest = {
            "framework": "pymhf[gui]==0.2.4", "steam_build": "owned-build",
            "supported_nms_exe_sha256": hashlib.sha256(
                (self.game / "Binaries/NMS.exe").read_bytes()).hexdigest(),
            "files": [{"path": name, "sha256": hashlib.sha256(
                (self.bundle / name).read_bytes()).hexdigest()}
                for name in payload],
        }
        self.write_manifest()
        self.info = {"exe": sys.executable, "major": 3, "minor": 11,
                     "bits": 64, "pymhf": "0.2.4", "dearpygui": "2.3.1", "pymhflib_count": 0}

    def write_manifest(self):
        (self.bundle / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def refresh_checksum(self, name):
        entry = next(entry for entry in self.manifest["files"] if entry["path"] == name)
        entry["sha256"] = hashlib.sha256((self.bundle / name).read_bytes()).hexdigest()
        self.write_manifest()

    def message(self, key, language="en"):
        catalog = json.loads((self.bundle / "locales" / (language + ".json")).read_text(encoding="utf-8"))
        return catalog["messages"][key]["text"].format(
            build="Owned release (Steam owned-build)", version="0.2.4")

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes() if path.is_file() else None
                for path in self.root.rglob("*")}

    def run_launcher(self, *, check=True, processes="closed", info="default",
                     held=False, child_exit=0, language="en", select_game=True):
        env = dict(os.environ, LOCALAPPDATA=str(self.local),
                   CAS_TEST_PROCESSES=processes, CAS_TEST_LEASE=self.lease,
                   CAS_TEST_INFO=json.dumps(self.info) if info == "default" else info,
                   CAS_TEST_CHILD_EXIT=str(child_exit), PYTHONDONTWRITEBYTECODE="1",
                   CAS_TEST_GAME=str(self.game), CAS_TEST_LANGUAGE=language)
        # Do not inherit a PowerShell 7-only module path into Windows PowerShell.
        env["PSModulePath"] = str(Path(POWERSHELL).parent / "Modules")
        args = [POWERSHELL, "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass"]
        if held:
            def quote(value):
                return "'" + str(value).replace("'", "''") + "'"
            command = (
                "$new = $false; $held = [System.Threading.Mutex]::new($false, "
                + quote(self.lease) + ", [ref]$new); if (-not $new) { throw 'Fixture collision' }; "
                + "$global:LASTEXITCODE = 0; try { & " + quote(self.script)
                + (" -GameDirectory " + quote(self.game) if select_game else "")
                + " -NoDialog -Language " + quote(language)
                + (" -CheckOnly" if check else "")
                + "; $result = $LASTEXITCODE } finally { $held.Dispose() }; exit $result")
            args += ["-Command", command]
        else:
            args += ["-File", str(self.script), "-NoDialog", "-Language", language]
            if select_game:
                args += ["-GameDirectory", str(self.game)]
            if check:
                args.append("-CheckOnly")
        before = self.snapshot()
        result = subprocess.run(args, env=env, capture_output=True, text=True,
                                encoding="utf-8", errors="strict", timeout=25)
        self.assertEqual(self.snapshot(), before, "The owned package/game/runtime must remain unchanged")
        return result.returncode, result.stdout + result.stderr

    def test_check_only_validates_with_game_closed_or_running_without_setup(self):
        for state, value in (("closed", "False"), ("running", "True")):
            with self.subTest(state=state):
                code, output = self.run_launcher(processes=state)
                self.assertEqual(code, 0, output)
                for expected in ("Validated exact game build: owned-build", "pyMHF 0.2.4",
                                 "Dear PyGui 2.3.1", "No Man's Sky running: " + value,
                                 "CheckOnly completed", "TEST_PROBE"):
                    self.assertIn(expected, output)
                self.assertNotIn("TEST_CHILD", output)
                self.assertNotIn("TEST_DISPOSE", output)

    def test_check_only_missing_runtime_does_not_create_it(self):
        self.runtime.unlink()
        code, output = self.run_launcher()
        self.assertNotEqual(code, 0)
        self.assertIn("runtime is missing", output)
        self.assertNotIn("TEST_PROBE", output)
        self.assertFalse(self.runtime.exists())

    def test_check_only_rejects_damaged_or_incomplete_runtime_without_repair(self):
        for info in ("null", json.dumps(dict(self.info, pymhf="0.1")),
                     json.dumps(dict(self.info, dearpygui=None))):
            with self.subTest(info=info):
                code, output = self.run_launcher(info=info)
                self.assertNotEqual(code, 0)
                self.assertNotIn("Installing", output)
                self.assertNotIn("TEST_CHILD", output)
                self.assertNotIn("TEST_DISPOSE", output)

    def test_foreign_or_unverified_libraries_refuse_check_and_launch(self):
        for count in (1, -1, None, "0", False):
            for check in (True, False):
                with self.subTest(count=count, check=check):
                    self.info["pymhflib_count"] = count
                    code, output = self.run_launcher(check=check)
                    self.assertNotEqual(code, 0)
                    self.assertIn(self.message("launcher.invalid_package").split(".")[0], " ".join(output.split()))
                    self.assertNotIn("TEST_CHILD", output)
                    self.assertNotIn("CheckOnly completed", output)

    def test_bad_package_or_game_fails_before_runtime_probe(self):
        original = (self.bundle / "CompanionAutoSummon.py").read_bytes()
        (self.bundle / "CompanionAutoSummon.py").write_bytes(b"modified")
        code, output = self.run_launcher()
        self.assertNotEqual(code, 0)
        self.assertIn(self.message("launcher.invalid_package").split(".")[0], output)
        self.assertNotIn("TEST_PROBE", output)
        (self.bundle / "CompanionAutoSummon.py").write_bytes(original)
        (self.game / "Binaries/NMS.exe").write_bytes(b"wrong build")
        code, output = self.run_launcher()
        self.assertNotEqual(code, 0)
        self.assertIn(self.message("launcher.unsupported_game").split(".")[0], " ".join(output.split()))
        self.assertNotIn("TEST_PROBE", output)

    def test_failed_process_query_cannot_be_interpreted_as_closed(self):
        for check in (True, False):
            with self.subTest(check=check):
                code, output = self.run_launcher(check=check, processes="error")
                self.assertNotEqual(code, 0)
                self.assertIn("process enumeration succeeds", output)
                self.assertNotIn("TEST_CHILD", output)
                self.assertEqual("TEST_DISPOSE" in output, not check)
                if not check:
                    self.assertNotIn("TEST_PROBE", output)

    def test_french_build_mismatch_is_unicode_and_refused_before_runtime_probe(self):
        (self.game / "Binaries/NMS.exe").write_bytes(b"different owned executable")
        code, output = self.run_launcher(language="fr")
        self.assertNotEqual(code, 0)
        normalized = " ".join(output.split())
        self.assertIn(self.message("launcher.unsupported_game", "fr").split(".")[0], normalized)
        self.assertIn("vérifiée", output)
        self.assertIn("Owned release (Steam owned-build)", normalized)
        self.assertNotIn("TEST_PROBE", output)
        self.assertNotIn("TEST_CHILD", output)

    def test_missing_executable_is_reported_without_a_runtime_probe(self):
        (self.game / "Binaries/NMS.exe").unlink()
        code, output = self.run_launcher()
        self.assertNotEqual(code, 0)
        self.assertIn(self.message("launcher.unreadable_game").split(".")[0], " ".join(output.split()))
        self.assertNotIn("TEST_PROBE", output)

    def test_no_selected_or_discovered_installation_is_reported_without_real_discovery(self):
        code, output = self.run_launcher(select_game=False)
        self.assertNotEqual(code, 0)
        self.assertIn(self.message("launcher.game_required").rstrip("."), " ".join(output.split()))
        self.assertNotIn("TEST_PROBE", output)

    def test_broken_profile_is_refused_before_python_probe_even_with_matching_file_checksum(self):
        path = self.bundle / "compatibility.json"
        examples = [b"not JSON", json.dumps(dict(self.profile, schema_version=2)).encode(),
                    json.dumps(dict(self.profile, schema_version=True)).encode(),
                    json.dumps(dict(self.profile, schema_version="1")).encode(),
                    json.dumps(dict(self.profile, exe_sha256="0" * 64)).encode(),
                    json.dumps(dict(self.profile, framework_version="other")).encode(),
                    json.dumps(dict(self.profile, steam_build="other-build")).encode()]
        for data in examples:
            with self.subTest(data=data):
                path.write_bytes(data)
                self.refresh_checksum("compatibility.json")
                code, output = self.run_launcher()
                self.assertNotEqual(code, 0)
                self.assertNotIn("TEST_PROBE", output)
                self.assertNotIn("TEST_CHILD", output)

    def test_stale_french_or_wrong_placeholder_uses_english_package_fallback(self):
        (self.game / "Binaries/NMS.exe").write_bytes(b"different owned executable")
        path = self.bundle / "locales/fr.json"
        original = json.loads(path.read_text(encoding="utf-8"))
        for field, value in (("source_sha256", "0" * 64),
                              ("text", "Version incompatible : {version}.")):
            with self.subTest(field=field):
                catalog = json.loads(json.dumps(original))
                catalog["messages"]["launcher.unsupported_game"][field] = value
                path.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
                self.refresh_checksum("locales/fr.json")
                code, output = self.run_launcher(language="fr")
                self.assertNotEqual(code, 0)
                self.assertIn(self.message("launcher.invalid_package").split(".")[0],
                              " ".join(output.split()))
                self.assertNotIn("Cette version du jeu", output)
                self.assertNotIn("Version incompatible", output)
                self.assertNotIn("TEST_PROBE", output)
                self.assertNotIn("TEST_CHILD", output)

    def test_missing_or_changed_host_compatibility_payload_is_refused_before_probe(self):
        path = self.bundle / "cas_compatibility.py"
        for data in (None, b"changed helper"):
            with self.subTest(data=data):
                if data is None:
                    path.unlink()
                else:
                    path.write_bytes(data)
                code, output = self.run_launcher()
                self.assertNotEqual(code, 0)
                self.assertIn(self.message("launcher.invalid_package").split(".")[0], " ".join(output.split()))
                self.assertNotIn("TEST_PROBE", output)

    def test_normal_launch_rejects_running_game_before_setup(self):
        code, output = self.run_launcher(check=False, processes="running")
        self.assertNotEqual(code, 0)
        self.assertIn("already running", output)
        self.assertIn("TEST_DISPOSE", output)
        self.assertNotIn("TEST_PROBE", output)

    def test_duplicate_setup_lease_fails_fast_before_setup(self):
        code, output = self.run_launcher(check=False, held=True)
        self.assertNotEqual(code, 0)
        self.assertIn("setup or launcher is active", output)
        self.assertIn("TEST_DISPOSE", output)
        self.assertNotIn("TEST_PROBE", output)
        self.assertNotIn("TEST_CHILD", output)

    def test_check_only_does_not_acquire_existing_setup_lease(self):
        code, output = self.run_launcher(held=True, processes="running")
        self.assertEqual(code, 0, output)
        self.assertIn("CheckOnly completed", output)
        self.assertNotIn("TEST_DISPOSE", output)

    def test_setup_lease_survives_synchronous_child_and_disposes_on_both_results(self):
        for child_exit in (0, 7):
            with self.subTest(child_exit=child_exit):
                code, output = self.run_launcher(check=False, child_exit=child_exit)
                self.assertEqual(code, 0 if child_exit == 0 else 1, output)
                self.assertIn("TEST_CHILD_LEASE_HELD", output)
                self.assertIn("TEST_DISPOSE", output)
                self.assertLess(output.index("TEST_CHILD_LEASE_HELD"), output.index("TEST_DISPOSE"))

    def test_real_probe_passes_no_bytecode_flag(self):
        # Extract the actual function, and exercise it with an owned PS stub.
        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("function Get-PythonInfo {")
        end = source.index("function Find-Python {", start)
        probe = self.root / "probe.ps1"
        probe.write_text('''param([Parameter(ValueFromRemainingArguments=$true)][string[]]$ProbeArgs)
if ($ProbeArgs.Count -ne 3 -or $ProbeArgs[0] -cne '-B' -or $ProbeArgs[1] -cne '-c') { throw 'Missing probe flags' }
$global:LASTEXITCODE = 0
Write-Output $env:CAS_TEST_INFO
''', encoding="utf-8-sig")
        driver = self.root / "probe-driver.ps1"
        driver.write_text(source[start:end] + "\n$info = Get-PythonInfo -Executable $env:CAS_TEST_PROBE; if (-not $info) { throw 'Probe failed' }; Write-Output 'PROBE_OK'\n", encoding="utf-8-sig")
        result = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(driver)],
                                env=dict(os.environ, CAS_TEST_PROBE=str(probe), CAS_TEST_INFO=json.dumps(self.info)),
                                capture_output=True, text=True, timeout=25)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PROBE_OK", result.stdout)

    def test_actual_native_python_probe_survives_windows_powershell_argument_marshalling(self):
        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("function Get-PythonInfo {")
        end = source.index("function Find-Python {", start)
        driver = self.root / "native-python-probe.ps1"
        driver.write_text("[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)\n" +
                          "$ErrorActionPreference = 'Stop'\n" + source[start:end] +
                          "\n$info = Get-PythonInfo -Executable $env:CAS_TEST_NATIVE_PYTHON\n" +
                          "if ($null -eq $info) { throw 'Native Python probe returned null' }\n" +
                          "$info | ConvertTo-Json -Compress\n", encoding="utf-8-sig")
        before = self.snapshot()
        result = subprocess.run([POWERSHELL, "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy",
                                 "Bypass", "-File", str(driver)],
                                env=dict(os.environ, CAS_TEST_NATIVE_PYTHON=sys.executable,
                                         PYTHONDONTWRITEBYTECODE="1"),
                                capture_output=True, text=True, encoding="utf-8", errors="strict", timeout=25)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        info = json.loads(result.stdout)
        self.assertEqual(os.path.normcase(info["exe"]), os.path.normcase(os.path.realpath(sys.executable)))
        self.assertEqual((info["major"], info["minor"], info["bits"]),
                         (sys.version_info.major, sys.version_info.minor, struct.calcsize("P") * 8))
        versions = {distribution.metadata.get("Name", "").lower(): distribution.version
                    for distribution in importlib.metadata.distributions()}
        self.assertEqual(info["pymhf"], versions.get("pymhf"))
        self.assertEqual(info["dearpygui"], versions.get("dearpygui")
                         if importlib.util.find_spec("dearpygui") else None)
        self.assertEqual(info["pymhflib_count"], len(importlib.metadata.entry_points(group="pymhflib")))
        self.assertEqual(before, self.snapshot())

    def test_builder_markers_and_nonownership_contract_remain_exact(self):
        source = SOURCE.read_text(encoding="utf-8")
        for marker in (
            "$modPath = Join-Path $PSScriptRoot 'CompanionAutoSummon.py'",
            "$bootstrapPath = Join-Path $PSScriptRoot 'Launch-CompanionAutoSummon.py'",
            "@('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py', 'cas_compatibility.py', 'compatibility.json')",
            "(Test-Path -LiteralPath $modPath -PathType Leaf)",
            "& $runtimePython $bootstrapPath $modPath",
            "[System.Threading.Mutex]::new($false, '" + LEASE_NAME + "', [ref]$createdNew)",
        ):
            self.assertEqual(source.count(marker), 1, marker)
        self.assertNotIn("WaitOne", source)
        self.assertNotIn("ReleaseMutex", source)
        self.assertIn("Get-Process -ErrorAction Stop", source)
        self.assertNotIn("Get-Process -Name", source)


if __name__ == "__main__":
    unittest.main()
