"""Owned portable initialization and bounded-start adapters.

Preparation performs no attachment. Vendor bytes and selected-image,
actual-process and DLL injection guards remain unchanged.
"""

from functools import wraps
import ctypes
import hashlib
from importlib import metadata
import json
from pathlib import Path
import re
import stat
import struct
import sys
import time


class PortableDependencyError(RuntimeError):
    """A required Microsoft system runtime is unavailable to this x64 host."""

    key = "portable.native_runtime_missing"


class PortableLaunchError(RuntimeError):
    """The owned bounded Steam start could not obtain its exact target."""

    key = "portable.start_failed"


def bounded_steam_start(framework, cmd, target, required_assemblies, start_paused,
                        *, monotonic=time.monotonic, sleep=time.sleep):
    """Replace only the reviewed Steam branch; never terminate any process.

The caller installs the existing actual-process/DLL guard before this function
runs. A found child PID is opened directly instead of reselecting by name.
"""
    if (type(cmd) is not list or cmd != ["steam://rungameid/275850"] or target != "NMS.exe"
            or type(required_assemblies) is not list or required_assemblies != [] or start_paused is not False):
        raise PortableLaunchError("Unsupported portable launch arguments")
    parents = []
    try:
        for index, process in enumerate(framework.psutil.process_iter(["name", "pid"])):
            if index >= 65536:
                raise PortableLaunchError("Process enumeration exceeded its bound")
            try:
                if process.name().casefold() == "steam.exe":
                    parents.append(process)
            except framework.psutil.NoSuchProcess:
                continue
    except Exception as error:
        raise PortableLaunchError("Steam could not be identified") from error
    if len(parents) != 1:
        raise PortableLaunchError("One running Steam process is required")
    try:
        if framework.webbrowser.open(cmd[0]) is not True:
            raise PortableLaunchError("The Steam launch request was not accepted")
    except Exception as error:
        raise PortableLaunchError("Steam could not start the selected game") from error
    deadline = monotonic() + 120.0
    while monotonic() < deadline:
        matches = []
        try:
            children = parents[0].children(recursive=True)
            if len(children) > 65536:
                raise PortableLaunchError("Steam child enumeration exceeded its bound")
            for child in children:
                try:
                    if child.name().casefold() == "nms.exe":
                        matches.append(child)
                except framework.psutil.NoSuchProcess:
                    continue
        except framework.psutil.NoSuchProcess as error:
            raise PortableLaunchError("Steam exited while waiting for the game") from error
        except Exception as error:
            raise PortableLaunchError("Steam children could not be inspected") from error
        if len(matches) > 1:
            raise PortableLaunchError("The game target is ambiguous")
        if matches:
            child = matches[0]
            if type(child.pid) is not int or child.pid <= 0:
                raise PortableLaunchError("The Steam child has no valid process identity")
            try:
                binary = framework.pymem.Pymem(child.pid)
            except (framework.pymem.exception.ProcessNotFound, framework.pymem.exception.CouldNotOpenProcess):
                sleep(0.1)
                continue
            try:
                modules = list(framework.pymem.process.enum_process_module(binary.process_handle))
            except Exception as error:
                binary.close_process()
                raise PortableLaunchError("The game image could not be inspected") from error
            if modules:
                # Do not catch a compatibility refusal or retry after a partial
                # runner construction. The existing injection guard is decisive.
                return framework.dllinject.pyRunner(binary), framework.WrappedProcess(proc=child)
            binary.close_process()
        sleep(0.1)
    raise PortableLaunchError("The Steam game did not become ready within 120 seconds")


def install_bounded_steam_start(framework):
    if getattr(framework.get_process_when_ready, "_cas_bounded_start", False):
        return

    def start(cmd, target, required_assemblies=None, start_paused=False):
        return bounded_steam_start(framework, cmd, target, required_assemblies, start_paused)

    start._cas_bounded_start = True
    framework.get_process_when_ready = start


def install_run_module_result_guard(framework):
    """Reject silent pre-start returns, without asserting target initialization."""
    original = framework.run_module
    if getattr(original, "_cas_prestart_result_guard", False) is True:
        return

    @wraps(original)
    def run_module(*args, **kwargs):
        entry = framework.dllinject.pyRunner.run_data
        if getattr(entry, "_cas_unicode_adapter", False) is not True:
            raise PortableLaunchError("The portable initialization adapter is absent")
        before = entry._cas_run_data_entries
        result = original(*args, **kwargs)
        if result is None and entry._cas_run_data_entries == before:
            raise PortableLaunchError("The framework returned before executing initialization")
        # Entry is evidence of an attempt, not a successful native bootstrap.
        # Preserve a normal post-entry return without claiming game acceptance.
        return result

    run_module._cas_prestart_result_guard = True
    framework.run_module = run_module


INTERPRETER_PRELUDE = (
    "import sys\n"
    "sys.dont_write_bytecode = True\n"
    "import sitecustomize\n"
    "if getattr(sitecustomize, 'PORTABLE_BOOTSTRAP_READY', False) is not True:\n"
    "    raise RuntimeError('The portable bootstrap did not complete')\n"
)


def initialize_interpreter():
    """Enable the owned bootstrap without processing arbitrary site .pth files."""
    sys.dont_write_bytecode = True
    import sitecustomize
    if getattr(sitecustomize, "PORTABLE_BOOTSTRAP_READY", False) is not True:
        raise RuntimeError("The portable interpreter bootstrap did not complete")


def file_as_source(path):
    """Replace narrow C fopen with Python's Unicode path handling.

The original file becomes __file__, globals are shared, and compile receives
bytes so Python honors the file's declared encoding. No source executes here.
"""
    if type(path) is not str or not path or "\0" in path or not Path(path).is_absolute():
        raise ValueError("An absolute script filename is required")
    return (
        f"__file__ = {path!r}\n"
        "with open(__file__, 'rb') as _cas_portable_script:\n"
        "    _cas_portable_source = _cas_portable_script.read()\n"
        "exec(compile(_cas_portable_source, __file__, 'exec'), globals(), globals())\n"
    )


def adapt_records(records, record_type):
    """Copy bounded typed records without changing executable string records."""
    if type(records) is not list or not 1 <= len(records) <= 64:
        raise ValueError("Expected a bounded sequence of initialization records")
    result = [record_type(INTERPRETER_PRELUDE, False)]
    for record in records:
        if type(record) is not record_type or type(record.value) is not str or type(record.is_file) is not bool:
            raise ValueError("Invalid initialization record")
        if len(record.value.encode("utf-8")) > 1048576 or "\0" in record.value:
            raise ValueError("Invalid initialization payload")
        result.append(record_type(file_as_source(record.value), False) if record.is_file else record)
    return result


def configure_host():
    """Install the narrow adapter once, before the guarded host starts pyMHF.

Importing these modules does not instantiate a runner, enumerate processes,
inject a DLL or register hooks. The caller must still use the guarded launcher.
"""
    if metadata.version("pymhf") != "0.2.4" or metadata.version("pyrun-injected") != "0.2.0":
        raise RuntimeError("Portable support requires the pinned framework")
    initialize_interpreter()
    from pyrun_injected import dllinject

    original = dllinject.pyRunner.run_data
    if getattr(original, "_cas_unicode_adapter", False):
        return

    @wraps(original)
    def run_data(self, strings, run_in_directory=None, inject_sys_path=False):
        records = adapt_records(strings, dllinject.StringType)
        run_data._cas_run_data_entries += 1
        return original(self, records,
                        run_in_directory=run_in_directory, inject_sys_path=inject_sys_path)

    run_data._cas_unicode_adapter = True
    run_data._cas_run_data_entries = 0
    dllinject.pyRunner.run_data = run_data


def verify_runtime(runtime):
    """Read the complete pinned runtime and import its required native modules.

No package manager, postinstall script, process lookup, game or hook is used.
The containing launcher must verify this manifest before starting Python.
"""
    root = Path(runtime).resolve(strict=True)
    if (sys.version_info[:3] != (3, 11, 9) or struct.calcsize("P") != 8
            or Path(sys.prefix).resolve() != root or Path(sys.base_prefix).resolve() != root
            or Path(sys.executable).resolve().parent != root or not sys.flags.isolated):
        raise RuntimeError("The private portable interpreter is required")
    manifest_path = root / "runtime-manifest.json"
    if manifest_path.stat().st_size > 2_000_000:
        raise RuntimeError("Oversized runtime manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest.get("schema") != 1 or manifest.get("python") != "3.11.9"
            or manifest.get("platform") != "win_amd64" or manifest.get("framework") != "0.2.4"):
        raise RuntimeError("Invalid portable runtime identity")
    entries = manifest.get("files")
    if type(entries) is not list or not 1 <= len(entries) <= 10000:
        raise RuntimeError("Invalid runtime file list")
    expected = {"runtime-manifest.json"}
    for entry in entries:
        name, checksum = entry.get("path"), entry.get("sha256")
        if (type(name) is not str or not name or "\\" in name or ":" in name
                or name.startswith("/") or any(part in ("", ".", "..") for part in name.split("/"))
                or name.casefold() in expected or not isinstance(checksum, str)
                or re.fullmatch("[0-9a-f]{64}", checksum) is None):
            raise RuntimeError("Invalid runtime file entry")
        path = root
        for part in name.split("/"):
            path /= part
            info = path.lstat()
            if path.is_symlink() or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise RuntimeError("Linked runtime payload refused")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
            raise RuntimeError("The portable runtime has changed")
        expected.add(name.casefold())
    actual = {path.relative_to(root).as_posix().casefold() for path in root.rglob("*") if path.is_file()}
    if actual != expected:
        raise RuntimeError("Unexpected portable runtime files")
    lock = json.loads((root / "runtime-lock.json").read_text(encoding="utf-8"))
    for entry in lock["wheels"]:
        if metadata.version(entry["name"]) != entry["version"]:
            raise RuntimeError("A portable dependency version differs")
    if tuple(metadata.entry_points().select(group="pymhflib")):
        raise RuntimeError("Foreign framework libraries are not supported")
    initialize_interpreter()
    try:
        # DearPyGui imports this VC runtime. It is deliberately not copied from
        # a developer machine or redistributed without an authorized source.
        ctypes.WinDLL("msvcp140.dll", winmode=0x00000800)
    except OSError as error:
        raise PortableDependencyError("The Microsoft Visual C++ x64 runtime is unavailable") from error
    # Required imports exercise DLL resolution without creating a GUI or hooks.
    import pymhf
    import dearpygui.dearpygui
    import win32api
    import cyminhook
    import pyrun_injected.dll
    return {"python": "3.11.9", "framework": pymhf.__version__, "files_verified": len(expected),
            "native_imports_passed": True, "game_accessed": False}


def prepare_host(runtime):
    """Verify the private runtime, then prepare Unicode-safe initialization."""
    result = verify_runtime(runtime)
    configure_host()
    import pymhf.main as framework
    install_bounded_steam_start(framework)
    install_run_module_result_guard(framework)
    return result
