"""Execute the launcher against owned files and stubbed process/runtime probes.

No real game, process enumeration, dependency installation or injection occurs.
Each fixture replaces the fixed mutex name with its own random test namespace.
"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
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
$setupLease = $null''')
        text = text.replace("$setupLease.Dispose()", "$setupLease.Dispose(); Write-Host 'TEST_DISPOSE'")
        self.script.write_text(text, encoding="utf-8-sig")
        (self.bundle / "CompanionAutoSummon.py").write_bytes(b"# synthetic mod\n")
        self.bootstrap = self.bundle / "Launch-CompanionAutoSummon.py"
        self.bootstrap.write_text('''import ctypes as C
import os
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
        self.manifest = {
            "framework": "pymhf[gui]==0.2.4", "steam_build": "owned-build",
            "supported_nms_exe_sha256": hashlib.sha256(
                (self.game / "Binaries/NMS.exe").read_bytes()).hexdigest(),
            "files": [{"path": name, "sha256": hashlib.sha256(
                (self.bundle / name).read_bytes()).hexdigest()}
                for name in ("CompanionAutoSummon.py", "Launch-CompanionAutoSummon.py")],
        }
        self.write_manifest()
        self.info = {"exe": sys.executable, "major": 3, "minor": 11,
                     "bits": 64, "pymhf": "0.2.4", "dearpygui": "2.3.1"}

    def write_manifest(self):
        (self.bundle / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes() if path.is_file() else None
                for path in self.root.rglob("*")}

    def run_launcher(self, *, check=True, processes="closed", info="default",
                     held=False, child_exit=0):
        env = dict(os.environ, LOCALAPPDATA=str(self.local),
                   CAS_TEST_PROCESSES=processes, CAS_TEST_LEASE=self.lease,
                   CAS_TEST_INFO=json.dumps(self.info) if info == "default" else info,
                   CAS_TEST_CHILD_EXIT=str(child_exit), PYTHONDONTWRITEBYTECODE="1")
        # Do not inherit a PowerShell 7-only module path into Windows PowerShell.
        env["PSModulePath"] = str(Path(POWERSHELL).parent / "Modules")
        args = [POWERSHELL, "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass"]
        if held:
            def quote(value):
                return "'" + str(value).replace("'", "''") + "'"
            command = (
                "$new = $false; $held = [System.Threading.Mutex]::new($false, "
                + quote(self.lease) + ", [ref]$new); if (-not $new) { throw 'Fixture collision' }; "
                + "$global:LASTEXITCODE = 0; try { & " + quote(self.script) + " -GameDirectory " + quote(self.game)
                + (" -CheckOnly" if check else "")
                + "; $result = $LASTEXITCODE } finally { $held.Dispose() }; exit $result")
            args += ["-Command", command]
        else:
            args += ["-File", str(self.script), "-GameDirectory", str(self.game)]
            if check:
                args.append("-CheckOnly")
        before = self.snapshot()
        result = subprocess.run(args, env=env, capture_output=True, text=True, timeout=25)
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

    def test_bad_package_or_game_fails_before_runtime_probe(self):
        original = (self.bundle / "CompanionAutoSummon.py").read_bytes()
        (self.bundle / "CompanionAutoSummon.py").write_bytes(b"modified")
        code, output = self.run_launcher()
        self.assertNotEqual(code, 0)
        self.assertIn("does not match", output)
        self.assertNotIn("TEST_PROBE", output)
        (self.bundle / "CompanionAutoSummon.py").write_bytes(original)
        (self.game / "Binaries/NMS.exe").write_bytes(b"wrong build")
        code, output = self.run_launcher()
        self.assertNotEqual(code, 0)
        self.assertIn("unsupported", output)
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

    def test_normal_launch_rejects_running_game_before_setup(self):
        code, output = self.run_launcher(check=False, processes="running")
        self.assertNotEqual(code, 0)
        self.assertIn("is running", output)
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

    def test_builder_markers_and_nonownership_contract_remain_exact(self):
        source = SOURCE.read_text(encoding="utf-8")
        for marker in (
            "$modPath = Join-Path $PSScriptRoot 'CompanionAutoSummon.py'",
            "$bootstrapPath = Join-Path $PSScriptRoot 'Launch-CompanionAutoSummon.py'",
            "@('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py')",
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
