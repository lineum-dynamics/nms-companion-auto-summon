"""Compare the offline C++ policy driver against the maintained Python policy.

This tool executes only the explicitly supplied reference driver. It does not
launch, attach to, read or modify the game, saves, settings or installed mod.
Only the requested JSON report is written. The Python reference is loaded from
source without producing bytecode files.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import random
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PYTHON_SOURCE = ROOT / "src" / "policy.py"
NATIVE_SOURCES = (
    "native/include/cas/policy.hpp",
    "native/src/policy.cpp",
    "native/tests/policy_reference_driver.cpp",
)
BASE_SEED = 9282026
Command = tuple[Any, ...]


@dataclass(frozen=True)
class Configuration:
    name: str
    delay: float
    expiry: float | None


CONFIGURATIONS = (
    Configuration("default", 1.5, None),
    Configuration("zero_delay", 0.0, None),
    Configuration("finite_expiry", 1.5, 12.0),
    Configuration("zero_delay_finite_expiry", 0.0, 1.0),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_reference():
    namespace = {"__name__": "cas_native_policy_reference", "__file__": str(PYTHON_SOURCE)}
    exec(compile(PYTHON_SOURCE.read_text(encoding="utf-8"), str(PYTHON_SOURCE), "exec"), namespace)
    return namespace["CompanionAutoSummonPolicy"]


def tick(now: float, foot=True, active=-1, pending=-1, eligible=True) -> Command:
    return ("tick", now, foot, active, pending, eligible)


def focused_traces(config: Configuration) -> list[tuple[str, list[Command]]]:
    ready = config.delay + 0.125
    return [
        ("absence_does_not_create_opportunity", [
            tick(0), tick(300), ("remember", 2), tick(400), tick(1000),
            ("reset",), ("eject", 0.0, False), tick(0), tick(ready),
        ]),
        ("accepted_then_manual_dismissal_absence", [
            ("remember", 3), ("eject", 0.0, False), tick(0), tick(ready),
            ("resolve", True), tick(ready + 0.125, active=3),
            tick(ready + 1), tick(ready + 100), ("resolve", True),
            ("eject", ready + 101, False), tick(ready + 101), tick(ready * 2 + 101),
        ]),
        ("reject_and_retry_same_choice", [
            ("remember", 7), ("eject", 0.0, False), tick(0), tick(ready),
            tick(ready + 0.125), ("resolve", False), tick(ready + 0.25),
            ("resolve", False), tick(ready + 0.375), ("resolve", True),
            tick(ready + 0.5),
        ]),
        ("random_binding_and_manual_favourite", [
            ("remember", 3), ("eject", 0.0, True), tick(0),
            ("select", 8), ("select", 9), tick(ready), ("resolve", False),
            tick(ready + 0.125), ("resolve", True), ("eject", ready + 1, False),
            tick(ready + 1), tick(ready * 2 + 1),
        ]),
        ("random_without_favourite", [
            ("select", 2), ("eject", 0.0, True), tick(0), tick(ready),
            ("select", 0), tick(ready + 0.125), ("resolve", True), tick(300),
        ]),
        ("forbidden_location_interrupts_stability", [
            ("remember", 0), ("eject", 0.0, False), tick(0, foot=False),
            tick(1), tick(1.125, foot=False), tick(2), tick(2 + ready),
        ]),
        ("temporary_eligibility_and_unknown_sentinels", [
            ("remember", 29), ("eject", 0.0, False), tick(0, eligible=False),
            tick(ready, active=-2), tick(ready + 0.125, pending=-2),
            tick(ready + 0.25, active=-2147483648),
            tick(ready + 0.375, eligible=False), tick(ready + 0.5),
        ]),
        ("native_active_or_pending_cancels", [
            ("remember", 2), ("eject", 0.0, False), tick(0, active=2), tick(ready),
            ("eject", 10.0, False), tick(10, foot=False, pending=4), tick(10 + ready),
        ]),
        ("backward_time_cancels_and_updates_clock", [
            ("remember", 5), ("eject", 10.0, False), tick(10), tick(9), tick(12),
            ("eject", 11.0, False), tick(11), tick(13),
            ("eject", 20.0, False), tick(20), tick(20 + ready),
        ]),
        ("invalid_clock_cancels_without_forgetting_favourite", [
            ("remember", 5), ("eject", 0.0, False), tick(0), tick(math.nan), tick(2),
            ("eject", 3.0, False), ("eject", math.inf, False), tick(4),
            ("eject", 5.0, True), ("select", 7), tick(-math.inf), tick(6),
        ]),
        ("invalid_slots_preserve_state", [
            ("remember", 7), ("eject", 0.0, False), tick(0),
            ("remember", -1), ("remember", 30), ("remember", 2147483647),
            ("select", -1), ("select", 30), tick(ready),
        ]),
        ("invalid_boolean_preserves_state", [
            ("remember", 7), ("eject", 0.0, False), tick(0),
            ("eject", math.nan, 2), ("resolve", 2), tick(ready),
            ("resolve", 2), ("resolve", True),
        ]),
        ("manual_replacement_cancels_in_flight", [
            ("eject", 0.0, True), ("select", 8), tick(0), tick(ready),
            ("remember", 6), ("resolve", False), tick(ready + 0.125),
            ("eject", ready + 1, False), tick(ready + 1), tick(ready * 2 + 1),
        ]),
        ("enter_duplicate_eject_equal_time_and_reset", [
            ("remember", 4), ("eject", 10.0, False), tick(10), tick(10),
            ("eject", 10.125, False), tick(10.125), ("enter",), tick(20),
            ("reset",), ("remember", 0), ("eject", 0.0, False), tick(0), tick(ready),
        ]),
        ("expiry_boundary_and_long_wait", [
            ("remember", 1), ("eject", 0.0, False), tick(0, eligible=False),
            tick(config.expiry if config.expiry is not None else 300, eligible=False),
            tick((config.expiry if config.expiry is not None else 300) + ready),
            ("resolve", True),
        ]),
        ("finite_extreme_clock_arithmetic", [
            ("remember", 1), ("eject", -1e308, False), tick(-1e308), tick(1e308),
            ("resolve", False), tick(1e308), ("reset",),
            ("remember", 29), ("eject", -0.0, False), tick(0.0), tick(ready),
        ]),
    ]


def generated_trace(config: Configuration, seed: int) -> list[Command]:
    """Vary scenario inputs and interleave unrelated actions, using a fixed seed."""
    rng = random.Random(seed)
    commands: list[Command] = []
    ready = config.delay + 0.125
    for episode in range(96):
        base = float(episode * 1000)
        slot = rng.randrange(30)
        alternate = (slot + rng.randrange(1, 30)) % 30
        commands.append(("reset",))
        scenarios = [
            [("remember", slot), ("eject", base, False), tick(base), tick(base + ready),
             tick(base + ready + 0.125), ("resolve", True), tick(base + ready + 2)],
            [("remember", slot), ("eject", base, False), tick(base), tick(base + ready),
             ("resolve", False), tick(base + ready + 0.125), ("resolve", False),
             tick(base + ready + 0.25), ("resolve", True)],
            [("eject", base, True), tick(base), ("select", slot), ("select", alternate),
             tick(base + ready), ("resolve", False), tick(base + ready + 0.125)],
            [("remember", slot), ("eject", base, False), tick(base, foot=False),
             tick(base + 0.125), tick(base + 0.25, foot=False), tick(base + 0.5),
             tick(base + 0.5 + ready)],
            [("remember", slot), ("eject", base, False), tick(base, eligible=False),
             tick(base + ready, active=-2), tick(base + ready + 0.125, pending=-2),
             tick(base + ready + 0.25, eligible=False), tick(base + ready + 0.375)],
            [("remember", slot), ("eject", base, False),
             tick(base, active=slot if episode % 2 else -1,
                  pending=-1 if episode % 2 else alternate),
             tick(base + ready), tick(base + ready + 2)],
            [("remember", slot), ("eject", base, False), tick(base), tick(base - 1),
             ("eject", base + 1, False), tick(rng.choice([math.nan, math.inf, -math.inf])),
             tick(base + 2), ("eject", base + 3, True), ("select", alternate)],
            [("remember", slot), ("eject", base, True), ("select", alternate),
             tick(base), tick(base + ready), ("remember", slot),
             ("resolve", False), tick(base + ready + 1)],
            [("remember", slot), ("eject", base, False), tick(base, eligible=False),
             tick(base + rng.choice([12.0, 300.0, 700.0]), eligible=False),
             tick(base + 900), ("resolve", True)],
            [("remember", slot), ("eject", base, False), tick(base),
             ("remember", rng.choice([-1, 30, 2147483647])), ("select", -1),
             ("eject", math.nan, 2), ("resolve", 2), tick(base + ready)],
        ]
        commands.extend(scenarios[episode % len(scenarios)])
        for offset in range(5):
            now = base + 910 + offset
            options = [
                tick(now, eligible=rng.choice([False, True])),
                tick(now, foot=rng.choice([False, True]), active=rng.choice([-2, -1, slot])),
                ("resolve", rng.choice([False, True])),
                ("select", rng.randrange(-2, 32)),
                ("eject", now, rng.choice([False, True])),
                ("remember", rng.randrange(-2, 32)),
                ("enter",),
                tick(now - 5),
            ]
            commands.append(rng.choice(options))
    return commands


def encode(command: Command) -> str:
    def token(value):
        if type(value) is bool:
            return "1" if value else "0"
        return repr(value) if type(value) is float else str(value)
    return " ".join(token(value) for value in command)


def apply_reference(policy, command: Command):
    action, *arguments = command
    if action == "tick":
        now, foot, active, pending, eligible = arguments
        return policy.tick(now, on_foot_in_summon_location=foot, active_pet=active,
                           native_pending_pet=pending, eligible=eligible)
    if action == "eject":
        return policy.eject(arguments[0], random_selection=arguments[1])
    method = {"select": "select_for_exit", "enter": "enter_ship"}.get(action, action)
    return getattr(policy, method)(*arguments)


def reference_state(policy, result, error) -> dict[str, Any]:
    return {"result": result, "last_slot": policy.last_slot, "pending": policy.pending,
            "pending_slot": policy.pending_slot, "error": error}


def compare_record(expected: dict[str, Any], actual: Any) -> str | None:
    if type(actual) is not dict or set(actual) != set(expected):
        return "output record keys differ"
    for key in ("result", "last_slot", "pending", "pending_slot"):
        if type(actual[key]) is not type(expected[key]) or actual[key] != expected[key]:
            return f"{key} value or type differs"
    if actual["error"] is not None and type(actual["error"]) is not str:
        return "error must be null or a string"
    if (actual["error"] is None) != (expected["error"] is None):
        return "exception presence differs"
    return None


def run_trace(driver: Path, policy_class, config: Configuration, name: str,
              commands: list[Command], coverage: Counter, actions: Counter) -> dict[str, Any]:
    lines = [encode(command) for command in commands]
    process = subprocess.run(
        [str(driver), repr(config.delay), "none" if config.expiry is None else repr(config.expiry)],
        input="\n".join(lines) + "\n", capture_output=True, text=True, encoding="utf-8",
        timeout=30, check=False,
    )
    if process.returncode != 0 or process.stderr:
        raise AssertionError({"configuration": config.name, "trace": name,
                              "reason": "driver exited unsuccessfully or wrote stderr",
                              "returncode": process.returncode, "stderr": process.stderr[:2000]})
    output = process.stdout.splitlines()
    if len(output) != len(commands):
        raise AssertionError({"configuration": config.name, "trace": name,
                              "reason": "driver output count differs", "expected": len(commands),
                              "actual": len(output)})
    policy = policy_class(delay_seconds=config.delay, expiry_seconds=config.expiry)
    retry_slot = None
    for index, (command, line) in enumerate(zip(commands, output)):
        was_pending = policy.pending
        actions[command[0]] += 1
        result, error = None, None
        try:
            result = apply_reference(policy, command)
        except ValueError as exception:
            error = str(exception)
        expected = reference_state(policy, result, error)
        try:
            def reject_nonfinite(value):
                raise ValueError(f"non-finite JSON number: {value}")
            actual = json.loads(line, parse_constant=reject_nonfinite)
        except (json.JSONDecodeError, ValueError):
            actual = line[:1000]
        reason = compare_record(expected, actual)
        if reason:
            raise AssertionError({"configuration": config.name, "trace": name, "operation": index,
                                  "command": lines[index], "reason": reason,
                                  "expected": expected, "actual": actual,
                                  "context": lines[max(0, index - 4):index + 1]})
        coverage["commands_compared"] += 1
        coverage["pending_before_command"] += int(was_pending)
        coverage["exception_results"] += int(error is not None)
        if command[0] in {"eject", "remember", "reset", "enter"} and error is None:
            retry_slot = None
        if type(result) is int:
            coverage["summon_offers"] += 1
            coverage["fixed_choice_reoffers_after_rejection"] += int(result == retry_slot)
        if command[0] == "resolve" and result is True:
            coverage["accepted_resolutions" if command[1] is True else "rejected_resolutions"] += 1
            retry_slot = None if command[1] is True else policy.pending_slot
        if not policy.pending:
            retry_slot = None
        if (command[0] in {"tick", "eject"} and not math.isfinite(command[1]) and error
                and (command[0] == "tick" or type(command[2]) is bool)):
            coverage["invalid_clock_errors"] += 1
        if command[0] == "tick":
            if not was_pending and command[3:5] == (-1, -1):
                coverage["absent_without_opportunity"] += 1
            if was_pending and (command[3] < -1 or command[4] < -1):
                coverage["unknown_sentinel_observations"] += 1
            if was_pending and not command[2]:
                coverage["forbidden_location_observations"] += 1
    return {"name": name, "commands": len(commands)}


def validate(driver: Path) -> dict[str, Any]:
    policy_class = load_reference()
    inputs = {"src/policy.py": sha256(PYTHON_SOURCE),
              **{name: sha256(ROOT / name) for name in NATIVE_SOURCES},
              "tools/validate_native_policy.py": sha256(Path(__file__))}
    driver_hash = sha256(driver)
    report: dict[str, Any] = {
        "schema": 1, "scope": "offline pure-policy parity against src/policy.py",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "game_access": False, "hooks_or_native_calls": False, "live_gameplay_verified": False,
        "driver": {"path": str(driver), "sha256": driver_hash}, "source_sha256": inputs,
        "random_seed": BASE_SEED, "generated_traces_per_configuration": 6,
        "episodes_per_generated_trace": 96, "configurations": [], "passed": False,
    }
    coverage, actions = Counter(), Counter()
    try:
        for config_index, config in enumerate(CONFIGURATIONS):
            traces = focused_traces(config)
            traces.extend((f"seeded_long_trace_{index}", generated_trace(
                config, BASE_SEED + config_index * 100 + index)) for index in range(6))
            config_report = {"name": config.name, "delay_seconds": config.delay,
                             "expiry_seconds": config.expiry, "traces": []}
            report["configurations"].append(config_report)
            for name, commands in traces:
                config_report["traces"].append(run_trace(
                    driver, policy_class, config, name, commands, coverage, actions))
        minimums = {"commands_compared": 10000, "summon_offers": 100,
                    "accepted_resolutions": 30, "rejected_resolutions": 30,
                    "fixed_choice_reoffers_after_rejection": 30,
                    "absent_without_opportunity": 100, "invalid_clock_errors": 50,
                    "unknown_sentinel_observations": 50}
        report["coverage_minimums"] = minimums
        for name, minimum in minimums.items():
            if coverage[name] < minimum:
                raise AssertionError({"reason": "meaningful coverage minimum not reached",
                                      "metric": name, "minimum": minimum, "actual": coverage[name]})
        if sha256(driver) != driver_hash:
            raise AssertionError({"reason": "driver changed during validation"})
        for name, expected in inputs.items():
            if sha256(ROOT / name) != expected:
                raise AssertionError({"reason": "source changed during validation", "source": name})
        report["passed"] = True
    except (AssertionError, OSError, subprocess.SubprocessError, ValueError) as exception:
        report["failure"] = exception.args[0] if exception.args else str(exception)
        if not isinstance(report["failure"], (str, dict, list, int, float, bool, type(None))):
            report["failure"] = str(report["failure"])
    report["coverage"] = dict(sorted(coverage.items()))
    report["actions"] = dict(sorted(actions.items()))
    report["trace_count"] = sum(len(item["traces"]) for item in report["configurations"])
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    driver = arguments.driver.resolve(strict=True)
    if not driver.is_file():
        parser.error("--driver must name the compiled offline policy reference driver")
    report = validate(driver)
    destination = arguments.report.resolve()
    if destination == driver or destination in {ROOT / name for name in report["source_sha256"]}:
        parser.error("--report must not overwrite a validation input")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "traces": report["trace_count"],
                      "commands": report["coverage"].get("commands_compared", 0),
                      "report": str(destination)}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
