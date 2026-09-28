"""Bounded offline host and fresh-native-interpreter relocation checks.

Only newly owned children are started. The native child loads pyrun_injected
locally; it never opens another process or invokes an injection/hook method.
This does not validate NMS initialization or the framework's game lifecycle.
"""

import argparse
import hashlib
from importlib import util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading


ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 30
OUTPUT_LIMIT = 16384


def clean_environment(work):
    env = {key: value for key, value in os.environ.items()
           if not key.upper().startswith("PYTHON") and key.upper() not in {"PYTEST_VERSION", "SPHINX_AUTODOC_RUNNING", "VIRTUAL_ENV"}}
    windows = Path(os.environ["SystemRoot"])
    env.update(PATH=str(windows / "System32"), PYTHONHOME=str(work / "nonexistent-external-python"),
               PYTHONPATH=str(work / "nonexistent-external-python"),
               LOCALAPPDATA=str(work / "private-local"), APPDATA=str(work / "private-roaming"),
               TEMP=str(work), TMP=str(work))
    return env


def run_owned(command, work, *, successful=True):
    """Bound both streams and kill only this child on timeout/overflow."""
    buffers = [bytearray(), bytearray()]
    overflow = threading.Event()
    with subprocess.Popen(command, cwd=work, env=clean_environment(work),
                          stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          creationflags=subprocess.CREATE_NO_WINDOW) as process:
        def read(stream, output):
            try:
                while chunk := stream.read(1024):
                    if len(output) + len(chunk) > OUTPUT_LIMIT:
                        overflow.set()
                        process.kill()
                        break
                    output.extend(chunk)
            finally:
                stream.close()
        readers = [threading.Thread(target=read, args=(stream, buffer), daemon=True)
                   for stream, buffer in zip((process.stdout, process.stderr), buffers)]
        for reader in readers:
            reader.start()
        try:
            process.wait(timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
            raise RuntimeError("Owned portable probe timed out") from None
        for reader in readers:
            reader.join(timeout=2)
        if overflow.is_set() or any(reader.is_alive() for reader in readers):
            raise RuntimeError("Owned portable probe exceeded output limits")
        result = {"returncode": process.returncode, "stdout": buffers[0].decode("utf-8", errors="replace"),
                  "stderr": buffers[1].decode("utf-8", errors="replace")}
        if successful and (process.returncode != 0 or result["stderr"]):
            raise RuntimeError("Owned portable probe failed: " + json.dumps(result))
        return result


PROBE = r'''
import encodings, hashlib, json, os, pathlib, sitecustomize, struct, sys
from importlib import metadata, util
root = pathlib.Path(RUNTIME).resolve()
assert sitecustomize.PORTABLE_BOOTSTRAP_READY is True
assert sys.version_info[:3] == (3, 11, 9) and struct.calcsize('P') == 8
assert sys.flags.isolated and sys.dont_write_bytecode
assert pathlib.Path(sys.prefix).resolve() == root
assert pathlib.Path(sys.base_prefix).resolve() == root
assert all(pathlib.Path(value).resolve().is_relative_to(root) for value in sys.path)
assert os.environ.get('PYTEST_VERSION') is None
import pymhf, pymhf.core._internal, dearpygui.dearpygui, cyminhook, win32api, pythoncom, pywintypes, iced_x86, regex
from packaging.requirements import Requirement
from packaging.markers import default_environment
from packaging.utils import canonicalize_name
lock = json.loads((root / 'runtime-lock.json').read_text(encoding='utf-8'))
locked = {canonicalize_name(entry['name']): entry['version'] for entry in lock['wheels']}
for name, version in locked.items():
    assert metadata.version(name) == version
pending = [('pymhf', ('gui',))]
visited, closure = set(), set()
environment = default_environment()
while pending:
    name, extras = pending.pop()
    name = canonicalize_name(name)
    identity = (name, tuple(sorted(extras)))
    if identity in visited:
        continue
    visited.add(identity)
    closure.add(name)
    assert name in locked
    for line in metadata.requires(name) or []:
        requirement = Requirement(line)
        if requirement.marker and not any(requirement.marker.evaluate(dict(environment, extra=extra)) for extra in ('', *extras)):
            continue
        dependency = canonicalize_name(requirement.name)
        assert dependency in locked and requirement.specifier.contains(locked[dependency], prereleases=True), str(requirement)
        pending.append((dependency, tuple(requirement.extras)))
assert closure == set(locked), sorted(set(locked) - closure)
assert not tuple(metadata.entry_points().select(group='pymhflib'))
assert pymhf.core._internal.IS_INJECTED is False
spec = util.spec_from_file_location('owned_portable_support', SUPPORT)
support = util.module_from_spec(spec)
spec.loader.exec_module(support)
if MODE == 'host':
    support.prepare_host(root)
    import pymhf.main as framework
    assert getattr(framework.get_process_when_ready, '_cas_bounded_start', False) is True
    assert getattr(framework.run_module, '_cas_prestart_result_guard', False) is True
else:
    support.configure_host()
from pyrun_injected import dllinject
assert getattr(dllinject.pyRunner.run_data, '_cas_unicode_adapter', False)
origins = {}
for name, module in sorted(sys.modules.items()):
    origin = getattr(module, '__file__', None)
    if not origin or name in {'__main__', '__mp_main__', 'owned_portable_support'}:
        continue
    location = pathlib.Path(origin).resolve()
    assert location.is_relative_to(root), (name, origin)
    origins[name] = location.relative_to(root).as_posix()
result = {'mode':MODE,'passed':True,'python':'3.11.9','framework':pymhf.__version__,
          'dependency_closure':len(closure),'module_origins_within_runtime':True,
          'module_count':len(origins),'stdlib_before_framework':True,'isolated':True,
          'test_bypasses':False,'bytecode_writes':False,'native_modules_imported':True,
          'unicode_adapter_installed':True,'game_accessed':False,'injection_performed':False}
pathlib.Path(REPORT).write_text(json.dumps(result, indent=2)+'\n',encoding='utf-8')
'''


def payload_snapshot(runtime):
    return {path.relative_to(runtime).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in runtime.rglob("*") if path.is_file()}


def audit(runtime, work, compiler):
    if os.name != "nt":
        raise RuntimeError("Portable probes require Windows")
    runtime, work, compiler = Path(runtime).resolve(strict=True), Path(work), Path(compiler)
    if not work.is_absolute() or work.exists():
        raise ValueError("Supply a fresh absolute audit directory")
    work.mkdir(parents=True)
    before = payload_snapshot(runtime)
    relocated = work / "Relocated K\u00e1\u0165a \u732b" / "runtime"
    shutil.copytree(runtime, relocated)
    app = relocated.parent / "app"
    app.mkdir()
    support = app / "portable_host_support.py"
    shutil.copyfile(Path(__file__).with_name("portable_host_support.py"), support)
    spec = util.spec_from_file_location("portable_support", support)
    helper = util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    child = work / "PortableRuntimeProbe.exe"
    source = Path(__file__).with_name("portable_runtime_probe.cs")
    run_owned([str(compiler), "/nologo", "/target:exe", "/platform:x64", "/out:" + str(child), str(source)], work)
    records = []
    for mode in ("host", "native"):
        report = work / (mode + ".json")
        script = work / (mode + ".py")
        code = helper.INTERPRETER_PRELUDE + "\n".join(f"{name} = {value!r}" for name, value in {
            "RUNTIME": str(relocated), "SUPPORT": str(support), "MODE": mode, "REPORT": str(report)}.items()) + "\n" + PROBE
        script.write_text(code, encoding="utf-8")
        if mode == "host":
            run_owned([str(relocated / "python.exe"), "-I", "-B", str(script)], work)
        else:
            run_owned([str(child), str(relocated), "source", str(script)], work)
        records.append(json.loads(report.read_text(encoding="utf-8")))
    # Test the real narrow native file path, then the owned Unicode-safe record.
    unicode_script = relocated.parent / "\u732b-script.py"
    marker = work / "unicode-script-result.json"
    unicode_script.write_text("import pathlib\npathlib.Path(" + repr(str(marker)) + ").write_text('ok', encoding='utf-8')\n", encoding="utf-8")
    negative = run_owned([str(child), str(relocated), "file", str(unicode_script)], work, successful=False)
    original_file_succeeded = negative["returncode"] == 0 and marker.exists()
    if marker.exists():
        marker.unlink()
    adapter_script = work / "unicode-record.py"
    adapter_script.write_text(helper.INTERPRETER_PRELUDE + helper.file_as_source(str(unicode_script)), encoding="utf-8")
    run_owned([str(child), str(relocated), "source", str(adapter_script)], work)
    if not marker.exists() or marker.read_text(encoding="utf-8") != "ok":
        raise RuntimeError("The Unicode file adapter did not execute the owned script")
    if payload_snapshot(runtime) != before or payload_snapshot(relocated) != before:
        raise RuntimeError("A portable probe changed its runtime payload")
    result = {"passed":True,"scope":"owned offline host and native run_data initialization",
              "records":records,"unicode_relocation":True,"external_python_paths_poisoned":True,
              "system_only_path":True,"original_narrow_file_succeeded":original_file_succeeded,
              "unicode_file_adapter_passed":True,"runtime_payload_unchanged":True,
              "game_accessed":False,"injection_performed":False,"game_lifecycle_verified":False,
              "clean_windows_verified":False,"native_child_source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
              "host_support_source_sha256":hashlib.sha256(support.read_bytes()).hexdigest(),
              "audit_source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "runtime_manifest_sha256":before["runtime-manifest.json"]}
    (work / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--compiler", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.runtime, args.work, args.compiler)))
