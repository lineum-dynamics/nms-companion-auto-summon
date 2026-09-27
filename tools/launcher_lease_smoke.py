"""Check real Windows handle lifetime with isolated test names, never NMS.

Only test-owned child Python processes are started. No framework, production
mutex namespace, settings, game process or game file is accessed.
"""

import argparse
import hashlib
from importlib import util
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Launch-CompanionAutoSummon.py"


def load(name):
    if not name.startswith("Local\\CAS.LeaseSmoke."):
        raise ValueError("Only isolated test namespaces are allowed")
    spec = util.spec_from_file_location("_cas_lease_smoke", SOURCE)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.LAUNCHER_MUTEX_NAME = name
    return module


def child(name, mode):
    module = load(name)
    try:
        with module.launcher_session():
            if mode == "exit_without_finally":
                os._exit(0)
            print("acquired", flush=True)
    except module.LauncherSessionError:
        print("refused", flush=True)
        return 3
    return 0


def check():
    if os.name != "nt":
        raise RuntimeError("This explicit smoke requires Windows")
    name = "Local\\CAS.LeaseSmoke." + uuid.uuid4().hex
    module = load(name)
    before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()

    def run(mode="acquire"):
        return subprocess.run(
            [sys.executable, "-B", str(Path(__file__).resolve()), "--child", name, mode],
            capture_output=True, text=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    with module.launcher_session():
        blocked = run()
        if (blocked.returncode, blocked.stdout.strip(), blocked.stderr) != (3, "refused", ""):
            raise RuntimeError("Second process did not refuse the held lease")
    released = run()
    if (released.returncode, released.stdout.strip(), released.stderr) != (0, "acquired", ""):
        raise RuntimeError("A fresh process could not acquire after release")
    exited = run("exit_without_finally")
    if exited.returncode != 0 or exited.stdout or exited.stderr:
        raise RuntimeError("Test-owned process could not exit from its lease")
    after_exit = run()
    if (after_exit.returncode, after_exit.stdout.strip(), after_exit.stderr) != (0, "acquired", ""):
        raise RuntimeError("Process termination left a stale test lease")
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != before:
        raise RuntimeError("Launcher source changed during the smoke")
    result = {
        "passed": True, "launcher_sha256": before,
        "cross_process_refusal": True, "normal_release": True,
        "process_exit_without_finally_releases": True,
        "production_mutex_used": False, "game_accessed": False,
    }
    directory = ROOT / "build/validation"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "launcher-lease-smoke.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child", nargs=2, metavar=("TEST_NAME", "MODE"))
    args = parser.parse_args()
    if args.child:
        raise SystemExit(child(*args.child))
    print(json.dumps(check()))
