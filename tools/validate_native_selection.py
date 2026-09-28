"""Differentially test the pure native selector against src/selection.py.

Executes only the supplied offline reference driver, never the game or a hook.
Every command compares the returned candidate/error, fixed reservation, complete
ordered bag history and every injected RNG bound/result. Scripted entropy avoids
depending on an implementation-specific native random-number generator.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("src/selection.py", "native/include/cas/selection.hpp",
           "native/src/selection.cpp", "native/tests/selection_reference_driver.cpp",
           "tools/validate_native_selection.py")
BASE_SEED = 9282037


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(value):
    # Exercise every byte, including the high bit and embedded zero bytes.
    return hashlib.sha256(f"native selector companion {value}".encode()).digest()[:16]


def load_reference():
    path = ROOT / "src/selection.py"
    module = types.ModuleType("cas_native_selection_reference")
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec", dont_inherit=True), module.__dict__)
    return module.__dict__


class ScriptedRandom:
    def __init__(self, tape):
        self.tape, self.position, self.calls = tape, 0, []

    def randrange(self, bound):
        assert type(bound) is int and bound > 0
        value = self.tape[self.position % len(self.tape)] % bound
        self.position += 1
        self.calls.append([bound, value])
        return value

    def shuffle(self, values):
        for i in reversed(range(1, len(values))):
            j = self.randrange(i + 1)
            values[i], values[j] = values[j], values[i]


def reserve(owned, eligible=None, mode="random", habitat=None, rotate=True):
    return ("reserve", owned, [x[0] for x in owned] if eligible is None else eligible,
            mode, habitat, rotate)


def roster(count, start=0):
    return [(identity(start + i), i % 16) for i in range(count)]


def encode(command):
    action, *args = command
    cat = lambda value: "none" if value is None else str(value)
    owned_tokens = lambda owned: [str(len(owned)), *[value for item in owned
                    for value in (item[0].hex(), cat(item[1]))]]
    if action == "reserve":
        owned, eligible, mode, habitat, rotate = args
        values = [action, mode, cat(habitat), str(int(rotate)), *owned_tokens(owned),
                  str(len(eligible)), *[x.hex() for x in eligible]]
    elif action == "commit":
        values = [action, args[0] if isinstance(args[0], str) else args[0].hex()]
    elif action == "group":
        values = [action, *map(cat, args)]
    elif action == "groups":
        values = [action, cat(args[0]), *owned_tokens(args[1])]
    elif action == "rules":
        recognized, related, acceptable = args
        values = [action, str(len(recognized)), *map(str, recognized)]
        for pairs in (related, acceptable):
            values += [str(len(pairs)), *[str(x) for pair in pairs for x in pair]]
    else:
        values = [action]
    return " ".join(values)


def candidate_json(value):
    return None if value is None else [value.identity.hex(), value.habitat]


def snapshot(selector, rng, result, error):
    return {"result": result, "error": error, "pending": candidate_json(selector.pending),
            "bags": [{"key": list(key), "members": [x.hex() for x in sorted(bag.members)],
                      "remaining": [x.hex() for x in bag.remaining],
                      "last_accepted": bag.last_accepted.hex() if bag.last_accepted is not None else None}
                     for key, bag in selector._bags.items()],
            "rng_position": rng.position, "rng_calls": rng.calls.copy()}


def focused_traces():
    a, b, c, d = [identity(i) for i in range(4)]
    owned = [(a, 0), (b, 12), (c, 5), (d, 1)]
    traces = [
        ("fixed_reservation_despite_habitat_eligibility_and_settings", [
            reserve(owned), reserve(owned, [], "by_habitat", 7, False),
            reserve(list(reversed(owned)), [b], "by_habitat", 11),
            ("commit", identity(999)), ("commit", "pending"), reserve(owned),
            ("cancel",), reserve(owned), ("commit", "pending")]),
        ("removal_invalidates_instead_of_redrawing", [
            reserve([(a, 0)], mode="by_habitat", habitat=0),
            reserve([(b, 12)], mode="by_habitat", habitat=0),
            reserve([(b, 12)], mode="by_habitat", habitat=0), ("commit", "pending")]),
        ("cancel_preserves_rotation_entry", [
            reserve(owned), ("cancel",), reserve(owned), ("cancel",), reserve(owned),
            ("commit", "pending"), reserve(owned), ("commit", "pending")]),
        ("temporary_ineligibility_and_singleton_repetition", [
            reserve(owned, [a]), ("commit", "pending"), reserve(owned, [a]),
            ("cancel",), reserve(owned, [a, b]), ("commit", "pending"),
            reserve(owned, [a]), ("commit", "pending"), reserve(owned),
            ("commit", "pending"), reserve(owned, []), reserve(owned)]),
        ("adoption_deletion_reorder_habitat_change_and_empty_roster", [
            reserve(owned), ("commit", "pending"), reserve([(a, 0), (b, 12)]),
            ("commit", "pending"), reserve([(b, 12), (a, 0), (identity(88), 5)]),
            ("cancel",), reserve(owned, mode="by_habitat", habitat=0),
            ("commit", "pending"), reserve([(a, 5), (b, 0), (c, 12), (d, 1)], mode="by_habitat", habitat=0),
            ("cancel",), reserve([]), reserve(owned)]),
        ("invalid_observations_cancel_reservation_but_not_bags", [
            reserve(owned), reserve(owned + [owned[0]]), reserve(owned),
            reserve(owned, [a, a]), reserve(owned), reserve(owned, [identity(998)]),
            reserve(owned), reserve(roster(31)), reserve(owned), reserve(owned, mode="invalid"),
            reserve(owned), ("commit", "pending"), reserve(roster(30)), ("cancel",),
            reserve(roster(30) + [roster(30)[0]])]),
        ("rotation_off_does_not_consume_or_reset_history", [
            reserve(owned), ("commit", "pending"), reserve(owned, rotate=False),
            ("commit", "pending"), reserve(owned, rotate=False), ("cancel",),
            reserve(owned), ("commit", "pending"), ("reset",), reserve(owned)]),
        ("unknown_no_fallback_and_weird_normalization", [
            reserve(owned, mode="by_habitat", habitat=11),
            reserve(owned, mode="by_habitat", habitat=None),
            reserve(owned, mode="by_habitat", habitat=-1),
            reserve([(a, 8), (b, 9), (c, 10), (d, 7)], mode="by_habitat", habitat=8),
            ("commit", "pending"), reserve([(a, 8), (b, 9), (c, 10), (d, 7)], mode="by_habitat", habitat=10),
            ("commit", "pending"), reserve(owned)]),
        ("directed_custom_rules_and_invalid_configuration", [
            ("rules", [0, 1, 2], [(0, 1)], [(2, 0)]),
            ("group", 0, 1), ("group", 1, 0), ("group", 2, 0), ("group", 0, 2),
            reserve([(a, 1), (b, 2)], mode="by_habitat", habitat=0),
            ("rules", [8], [], []), ("rules", [0, 1], [(0, 0)], []),
            ("rules", [0, 1], [(0, 2)], []), ("rules", [0, 1], [(0, 1)], [(0, 1)]),
            ("commit", "pending"), ("rules", [], [], []),
            reserve(owned, mode="by_habitat", habitat=0), ("default_rules",),
            ("groups", 0, owned), ("groups", 0, owned + [owned[0]])]),
    ]
    # Complete default table and normalization, with hard expected directed pairs.
    habitats = [None, -2147483648, -1, *range(18), 2147483647]
    traces.append(("all_habitat_pairs", [("group", p, c) for p in habitats for c in habitats]))
    traces.append(("all_habitat_group_builds", [("groups", p, roster(30)) for p in habitats]))
    round_owned = [(identity(i), 0) for i in range(30)]
    traces.append(("complete_rotation_rounds", [command for _ in range(360)
                   for command in (reserve(round_owned), ("commit", "pending"))]))
    # Retain every reachable habitat/group context at once, then reconcile all
    # contexts after ownership and habitat changes. This checks insertion-order
    # RNG consumption independently of the generated traces' frequent resets.
    all_contexts = []
    for planet in (0, 1, 2, 3, 4, 5, 6, 7, 12, 13, 14, 15):
        for companion in range(16):
            ids = [identity(i) for i in range(30) if i % 16 == companion]
            all_contexts += [reserve(roster(30), ids, "by_habitat", planet), ("commit", "pending")]
    changed = [(identity(100 + i), (15 - i) % 16) for i in range(15)] + roster(15)
    all_contexts += [reserve(changed), ("cancel",), reserve(list(reversed(changed))),
                    ("commit", "pending"), reserve([]), reserve(roster(30)), ("commit", "pending")]
    traces.append(("all_retained_contexts_reconcile_in_insertion_order", all_contexts))
    # All weighted tickets across a deliberately unequal group population. Each
    # trace receives [ticket, 0] so the group result has an independent assertion.
    weighted_owned = [(identity(i), 0) for i in range(12)] + [(identity(12), 12), (identity(13), 5)]
    for ticket in range(19):
        traces.append((f"weight_ticket_{ticket}", [reserve(weighted_owned, mode="by_habitat", habitat=0, rotate=False)]))
    for category in (0, 12, 5):
        traces.append((f"single_eligible_group_{category}", [
            reserve(weighted_owned, [identity(i) for i, (_, h) in enumerate(weighted_owned) if h == category],
                    mode="by_habitat", habitat=0, rotate=False)]))
    return traces


def generated_trace(seed, operations=1000):
    rng = random.Random(seed)
    owned = roster(15)
    commands = []
    for index in range(operations):
        choice = rng.randrange(100)
        if choice < 48:
            # Ownership changes remain distinct from native eligibility changes.
            change = rng.randrange(10)
            if change == 0 and owned:
                del owned[rng.randrange(len(owned))]
            elif change == 1 and len(owned) < 30:
                existing = {item[0] for item in owned}
                options = [identity(i) for i in range(48) if identity(i) not in existing]
                owned.append((rng.choice(options), rng.choice([None, *range(-1, 18)])))
            elif change == 2 and owned:
                i = rng.randrange(len(owned))
                owned[i] = (owned[i][0], rng.choice([None, *range(16)]))
            elif change == 3:
                rng.shuffle(owned)
            current = owned.copy()
            eligible = [item[0] for item in current if rng.randrange(4)]
            mode = rng.choice(["random", "by_habitat", "by_habitat"])
            category = rng.choice([None, *range(-1, 18)])
            if choice == 0 and current:
                current.append(current[0])
            elif choice == 1 and eligible:
                eligible.append(eligible[0])
            elif choice == 2:
                eligible.append(identity(999))
            elif choice == 3:
                mode = "invalid"
            commands.append(reserve(current, eligible, mode, category, bool(rng.randrange(4))))
        elif choice < 70:
            commands.append(("commit", "pending"))
        elif choice < 76:
            commands.append(("commit", identity(900 + rng.randrange(4))))
        elif choice < 94:
            commands.append(("cancel",))
        elif choice < 97:
            commands.append(("reset",))
        else:
            commands.append(("groups", rng.choice([None, *range(16)]), owned.copy()))
    return commands


def run_trace(driver, reference, name, commands, seed, coverage):
    tape_rng = random.Random(seed)
    tape = [tape_rng.getrandbits(64) for _ in range(4096)]
    if name.startswith("weight_ticket_"):
        tape = [int(name.removeprefix("weight_ticket_")), 0]
    rng = ScriptedRandom(tape)
    current_rules = reference["DEFAULT_HABITAT_RULES"]
    selector = reference["CompanionSelector"](rng, current_rules)
    lines = [encode(command) for command in commands]
    encoded = "tape " + str(len(tape)) + " " + " ".join(map(str, tape)) + "\n" + "\n".join(lines) + "\n"
    process = subprocess.run([str(driver)], input=encoded, capture_output=True, text=True,
                             encoding="utf-8", timeout=60, check=False)
    if process.returncode:
        raise AssertionError({"trace": name, "reason": "driver failed", "exit_code": process.returncode,
                              "stderr": process.stderr[-3000:]})
    actual_lines = process.stdout.splitlines()
    if len(actual_lines) != len(commands):
        raise AssertionError({"trace": name, "reason": "incorrect output record count",
                              "expected": len(commands), "actual": len(actual_lines)})
    candidate = reference["Candidate"]
    make_roster = lambda values: [candidate(*item) for item in values]
    records = []
    for index, command in enumerate(commands):
        action, *args = command
        coverage[f"action_{action}"] += 1
        rng.calls.clear()
        result = error = None
        pending_before = selector.pending
        try:
            if action == "reserve":
                owned, eligible, mode, habitat, rotate = args
                result = candidate_json(selector.reserve(make_roster(owned), eligible,
                        mode=mode, habitat=habitat, rotate=rotate))
                coverage["reservations_returned"] += int(result is not None)
                coverage["empty_results"] += int(result is None)
                coverage["fixed_reservations_returned"] += int(pending_before is not None and result is not None)
                coverage["habitat_requests"] += int(mode == "by_habitat")
                coverage["rotation_disabled_requests"] += int(not rotate)
                if pending_before is not None:
                    assert result == candidate_json(pending_before), "Reservation must remain fixed"
            elif action == "commit":
                selected = selector.pending.identity if selector.pending else bytes(16)
                value = selected if args[0] == "pending" else args[0]
                result = selector.commit(value)
                coverage["accepted_commits"] += int(result)
                coverage["unmatched_commits"] += int(not result)
            elif action == "cancel":
                before_bags = snapshot(selector, rng, None, None)["bags"]
                selector.cancel()
                assert snapshot(selector, rng, None, None)["bags"] == before_bags, "Cancellation consumed bag state"
            elif action == "reset":
                selector.reset()
                assert not selector._bags and selector.pending is None
            elif action == "group":
                result = current_rules.group(*args)
            elif action == "groups":
                result = [[candidate_json(item) for item in values] for values in
                          reference["build_habitat_groups"](make_roster(args[1]), args[0], current_rules).values()]
            elif action == "rules":
                replacement = reference["HabitatRules"](frozenset(args[0]), frozenset(args[1]), frozenset(args[2]))
                current_rules = replacement
                selector = reference["CompanionSelector"](rng, current_rules)
            elif action == "default_rules":
                current_rules = reference["DEFAULT_HABITAT_RULES"]
                selector = reference["CompanionSelector"](rng, current_rules)
            else:
                raise AssertionError("Unknown reference command")
        except reference["SelectionError"] as exception:
            error = type(exception).__name__
            coverage[f"error_{error}"] += 1
        expected = snapshot(selector, rng, result, error)
        actual = json.loads(actual_lines[index])
        if actual != expected:
            raise AssertionError({"trace": name, "operation": index, "command": lines[index],
                                  "context": lines[max(0, index - 3):index + 1],
                                  "expected": expected, "actual": actual})
        for bound, _ in rng.calls:
            coverage[f"rng_bound_{bound}"] += 1
        coverage["rng_calls_compared"] += len(rng.calls)
        coverage["commands_compared"] += 1
        coverage["bag_contexts_compared"] += len(expected["bags"])
        records.append(expected)
    # Assertions independent of the original selector's internal behavior.
    if name.startswith("weight_ticket_"):
        ticket = int(name.removeprefix("weight_ticket_"))
        expected_habitat = 0 if ticket < 13 else 12 if ticket < 18 else 5
        assert records[0]["result"][1] == expected_habitat, "13/5/1 group weights changed"
        assert records[0]["rng_calls"][0] == [19, ticket]
    if name == "cancel_preserves_rotation_entry":
        assert records[0]["result"] == records[2]["result"] == records[4]["result"]
        assert records[6]["result"] != records[4]["result"]
    if name == "removal_invalidates_instead_of_redrawing":
        assert records[1]["error"] == "ReservationInvalidatedError"
        assert records[1]["pending"] is None and not records[1]["rng_calls"]
    if name == "unknown_no_fallback_and_weird_normalization":
        assert all(record["result"] is None and not record["rng_calls"] for record in records[:3])
        assert records[3]["result"][1] == records[5]["result"][1] == 7
        assert len(records[5]["bags"]) == 1, "Weird variants must share one rotation context"
    if name == "directed_custom_rules_and_invalid_configuration":
        assert [r["result"] for r in records[1:5]] == ["related", None, "acceptable", None]
    if name == "complete_rotation_rounds":
        choices = [r["result"][0] for r in records[::2]]
        assert all(a != b for a, b in zip(choices, choices[1:])), "Rotation repeated at a round boundary"
        assert all(len(set(choices[i:i + 30])) == 30 for i in range(0, len(choices), 30)), "Rotation lost a member"
    return {"name": name, "commands": len(commands), "rng_calls": rng.position}


def validate(driver):
    reference = load_reference()
    inputs = {name: sha256(ROOT / name) for name in SOURCES}
    driver_hash = sha256(driver)
    report = {"schema": 1, "scope": "pure native selector parity against src/selection.py",
              "started_utc": datetime.now(timezone.utc).isoformat(), "game_access": False,
              "hooks_or_native_calls": False, "live_gameplay_verified": False,
              "driver": {"path": str(driver), "sha256": driver_hash}, "source_sha256": inputs,
              "seed": BASE_SEED, "generated_trace_count": 24, "generated_operations_per_trace": 1000,
              "comparison": ["result", "exception_class", "pending_candidate", "ordered_contexts",
                             "owned_bag_members", "ordered_remaining", "last_accepted", "all_rng_calls"],
              "passed": False, "traces": []}
    coverage = Counter()
    try:
        traces = focused_traces()
        traces += [(f"generated_{i}", generated_trace(BASE_SEED + i)) for i in range(24)]
        for i, (name, commands) in enumerate(traces):
            report["traces"].append(run_trace(driver, reference, name, commands, BASE_SEED + 100 + i, coverage))
        minimums = {"commands_compared": 24000, "accepted_commits": 1000,
                    "fixed_reservations_returned": 1000, "reservations_returned": 5000,
                    "rng_calls_compared": 10000, "bag_contexts_compared": 10000,
                    "error_AmbiguousIdentityError": 100, "error_SelectionError": 100,
                    "error_ReservationInvalidatedError": 20, "rotation_disabled_requests": 1000}
        report["coverage_minimums"] = minimums
        for metric, minimum in minimums.items():
            if coverage[metric] < minimum:
                raise AssertionError({"reason": "meaningful coverage minimum not reached", "metric": metric,
                                      "minimum": minimum, "actual": coverage[metric]})
        if sha256(driver) != driver_hash or any(sha256(ROOT / name) != value for name, value in inputs.items()):
            raise AssertionError("Validation inputs changed during the run")
        report["passed"] = True
    except (AssertionError, OSError, subprocess.SubprocessError, ValueError) as exception:
        report["failure"] = exception.args[0] if exception.args else str(exception)
    report["coverage"] = dict(sorted(coverage.items()))
    report["trace_count"] = len(report["traces"])
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    driver = arguments.driver.resolve(strict=True)
    destination = arguments.report.resolve()
    if destination == driver or destination in {ROOT / name for name in SOURCES}:
        parser.error("--report must not overwrite a validation input")
    report = validate(driver)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "traces": report["trace_count"],
                      "commands": report["coverage"].get("commands_compared", 0), "report": str(destination)}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
