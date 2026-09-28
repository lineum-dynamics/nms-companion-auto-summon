"""Compare two host-only pyMHF imports in bounded, console-free subprocesses.

An explicit Python interpreter containing the existing pinned framework is
required. This does not install, launch or attach to a game, load a mod, call
run_module, enumerate processes or certify injected-side behavior. Only the two
test-owned Python children may be terminated on timeout or excessive output.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading


TIMEOUT_SECONDS = 15
MAX_OUTPUT_BYTES = 8192
EXPECTED_FAILURE = "prompt_toolkit.output.win32.NoConsoleScreenBufferError"
HELPER = Path(__file__).resolve().with_name("pymhf_host_import.py")
FRAMEWORK_VERSION = "0.2.4"

CHILD_CODE = r'''
import hashlib
from importlib import metadata, util
import json
import os
from pathlib import Path
import struct
import sys

def probe():
    if os.environ.get("PYTEST_VERSION") is not None or "sphinx.ext.autodoc" in sys.modules:
        raise RuntimeError("Framework test bypasses must not be active")
    if metadata.version("pymhf") != "0.2.4":
        raise RuntimeError("The smoke requires the existing pinned framework")
    if tuple(metadata.entry_points().select(group="pymhflib")):
        raise RuntimeError("Foreign framework libraries are outside this smoke")
    if struct.calcsize("P") != 8 or not (3, 11) <= sys.version_info[:2] <= (3, 13):
        raise RuntimeError("The smoke requires supported x64 Python")
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError("The child must run isolated without bytecode writes")
    framework = metadata.distribution("pymhf")
    files = ("pymhf/__init__.py", "pymhf/main.py", "pymhf/_preinject.py", "pymhf/injected.py")
    source_hashes = {name: hashlib.sha256(Path(framework.locate_file(name)).read_bytes()).hexdigest()
                     for name in files}
    result = {
        "mode": sys.argv[1], "python": ".".join(map(str, sys.version_info[:3])),
        "bits": struct.calcsize("P") * 8, "framework": metadata.version("pymhf"),
        "prompt_toolkit": metadata.version("prompt_toolkit"),
        "framework_source_sha256": source_hashes, "test_bypasses": False,
        "isolated": bool(sys.flags.isolated), "bytecode_writes": not sys.dont_write_bytecode,
    }
    try:
        if sys.argv[1] == "ordinary":
            import pymhf
        elif sys.argv[1] == "adapted":
            spec = util.spec_from_file_location("cas_host_import_prototype", sys.argv[2])
            helper = util.module_from_spec(spec)
            spec.loader.exec_module(helper)
            pymhf = helper.import_pymhf_noninteractive()
        else:
            raise ValueError("Unknown probe mode")
        if pymhf.__version__ != "0.2.4":
            raise RuntimeError("The imported framework version differs")
    except Exception as error:
        result.update(imported=False, error_type=type(error).__module__ + "." + type(error).__qualname__)
    else:
        result.update(imported=True, error_type=None)
    if source_hashes != {name: hashlib.sha256(Path(framework.locate_file(name)).read_bytes()).hexdigest()
                         for name in files}:
        raise RuntimeError("Framework sources changed during the probe")
    return result

try:
    result = probe()
except Exception as error:
    print(json.dumps({"probe_error_type": type(error).__module__ + "." + type(error).__qualname__}))
    raise SystemExit(2)
print(json.dumps(result, sort_keys=True))
'''


def clean_environment(environment):
    """Remove known bypass flags; -I separately ignores Python path overrides."""
    return {key: value for key, value in environment.items()
            if key.upper() not in {"PYTEST_VERSION", "SPHINX_AUTODOC_RUNNING"}}


def _read_limited(stream, process, output, overflow, errors):
    """Drain one stream with a strict memory cap; kill only this owned child."""
    try:
        while True:
            chunk = stream.read(1024)
            if not chunk:
                break
            if len(output) + len(chunk) > MAX_OUTPUT_BYTES:
                overflow.set()
                process.kill()
                break
            output.extend(chunk)
    except Exception:
        errors.set()
        try:
            process.kill()
        except OSError:
            pass
    finally:
        stream.close()


def _run_probe(python, mode):
    output, error_output = bytearray(), bytearray()
    overflow, reader_errors = threading.Event(), threading.Event()
    with subprocess.Popen(
        [str(python), "-I", "-B", "-c", CHILD_CODE, mode, str(HELPER)],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW, close_fds=True,
        env=clean_environment(os.environ),
    ) as process:
        readers = [threading.Thread(target=_read_limited,
                   args=(stream, process, buffer, overflow, reader_errors), daemon=True)
                   for stream, buffer in ((process.stdout, output), (process.stderr, error_output))]
        for reader in readers:
            reader.start()
        timed_out = False
        try:
            process.wait(timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            process.wait(timeout=5)
        for reader in readers:
            reader.join(timeout=2)
        if timed_out:
            raise RuntimeError("The owned import child exceeded its time limit")
        if overflow.is_set():
            raise RuntimeError("The owned import child exceeded its output limit")
        if reader_errors.is_set() or any(reader.is_alive() for reader in readers):
            raise RuntimeError("The owned import child's output could not be read safely")
        if process.returncode != 0 or error_output:
            raise RuntimeError("The owned import child failed its preconditions or wrote stderr")
    try:
        record = json.loads(output.decode("utf-8"))
    except (ValueError, UnicodeError):
        raise RuntimeError("The owned import child returned an invalid report") from None
    if not isinstance(record, dict):
        raise RuntimeError("The owned import child returned an invalid report")
    return record


def validate_comparison(ordinary, adapted):
    """Accept only the reproduced console failure and the matching import success."""
    common = ("python", "bits", "framework", "prompt_toolkit", "framework_source_sha256",
              "test_bypasses", "isolated", "bytecode_writes")
    if any(ordinary.get(key) != adapted.get(key) for key in common):
        raise RuntimeError("The import probes did not use the same framework environment")
    if (ordinary.get("framework") != FRAMEWORK_VERSION or ordinary.get("bits") != 64
            or ordinary.get("test_bypasses") is not False or ordinary.get("isolated") is not True
            or ordinary.get("bytecode_writes") is not False):
        raise RuntimeError("The import probes did not preserve the smoke boundary")
    if (ordinary.get("mode") != "ordinary" or ordinary.get("imported") is not False
            or ordinary.get("error_type") != EXPECTED_FAILURE):
        raise RuntimeError("The ordinary import did not reproduce the expected console failure")
    if (adapted.get("mode") != "adapted" or adapted.get("imported") is not True
            or adapted.get("error_type") is not None):
        raise RuntimeError("The adapted import did not succeed cleanly")


def check(framework_python):
    """Run the explicit offline comparison and return a report without local paths."""
    if os.name != "nt":
        raise RuntimeError("This no-console smoke requires Windows")
    python = Path(framework_python)
    if not python.is_absolute() or not python.is_file() or python.name.lower() != "python.exe":
        raise ValueError("Supply the absolute path to the existing framework python.exe")
    sources = (Path(__file__).resolve(), HELPER)
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
    ordinary = _run_probe(python, "ordinary")
    adapted = _run_probe(python, "adapted")
    validate_comparison(ordinary, adapted)
    if before != {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}:
        raise RuntimeError("Prototype sources changed during the smoke")
    return {
        "passed": True, "scope": "host-only framework import prototype",
        "source_sha256": before, "ordinary": ordinary, "adapted": adapted,
        "per_child_timeout_seconds": TIMEOUT_SECONDS, "per_stream_output_limit_bytes": MAX_OUTPUT_BYTES,
        "game_accessed": False, "framework_execution_started": False,
        "process_enumeration": False, "injected_interpreter_verified": False,
        "game_lifecycle_verified": False, "portable_runtime_verified": False,
        "production_launcher_changed": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework-python", required=True)
    parser.add_argument("--report", type=Path, help="Write a new JSON report; existing reports are refused")
    args = parser.parse_args()
    if args.report is not None and (args.report.exists() or not args.report.parent.is_dir()):
        parser.error("The report must be a new file in an existing directory")
    try:
        report = check(args.framework_python)
    except (OSError, ValueError, RuntimeError) as error:
        print(json.dumps({"passed": False, "error_type": type(error).__name__}))
        raise SystemExit(1) from None
    serialized = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report is not None:
        with args.report.open("x", encoding="utf-8") as report_file:
            report_file.write(serialized)
    print(serialized, end="")
