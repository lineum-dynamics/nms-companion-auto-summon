"""Observe exact-build lifecycle fields for a short player-assisted action.

External process reads only, sharing the resource reader's actual-process and
loaded-image guard. No hooks, native calls, process writes or save access.
One sample is not a callback trace; polling can miss intermediate transitions.
No numeric reason is assigned an event name by this tool.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import time

import pefile

from native_readonly_resource_snapshot import APP_CELL, Reader, Refusal, open_verified_process


FSM_CURRENT_CELL = 0x6E8D6E0
LOCAL_LOAD_STATE = 0x6E8EA40
LOCAL_LOAD_VTABLE = 0x4A50A30
MAX_CHANGES = 256


def sample(reader: Reader, base: int, image_size: int) -> dict:
    current = reader.pointer(base + FSM_CURRENT_CELL)
    state = base + LOCAL_LOAD_STATE
    if reader.pointer(state) != base + LOCAL_LOAD_VTABLE:
        raise Refusal("local_load_state_vtable_mismatch")
    reason = struct.unpack("<i", reader.read(state + 0x620, 4))[0]
    phase = struct.unpack("<i", reader.read(state + 0x62C, 4))[0]
    app = reader.pointer(base + APP_CELL)
    observed = {
        "fsm_current_is_local_load": current == state,
        "fsm_current_rva": f"0x{current-base:X}" if base <= current < base + image_size else "outside_main_module",
        "local_load_phase": phase,
        "position_reason_code": reason,
        "application_present": bool(app),
    }
    if app:
        observed["load_session_predicate_zero"] = reader.read(app + 0x4BE6A0, 1) == b"\0"
        session = reader.pointer(app + 0x941C70 + 0x1A8)
        observed["session_slot1_present"] = bool(session)
        if session:
            vtable = reader.pointer(session)
            session_class = {base + 0x4AA9F98: "PlayfabSession", base + 0x4AAA640: "Session"}.get(vtable)
            observed["session_slot1_class"] = session_class or "unclassified"
            if session_class is not None:
                observed["session_state_418"] = struct.unpack("<i", reader.read(session + 0x418, 4))[0]
                # Only zero/nonzero; never expose the identifier-like region.
                observed["session_region_41c_first_byte_zero"] = reader.read(session + 0x41C, 1) == b"\0"
            if reader.pointer(app + 0x941C70 + 0x1A8) != session:
                raise Refusal("session_slot_changed_during_sample")
        if reader.pointer(base + APP_CELL) != app:
            raise Refusal("application_changed_during_sample")
    if reader.pointer(base + FSM_CURRENT_CELL) != current:
        raise Refusal("fsm_changed_during_sample")
    if (struct.unpack("<i", reader.read(state + 0x620, 4))[0] != reason
            or struct.unpack("<i", reader.read(state + 0x62C, 4))[0] != phase):
        raise Refusal("local_load_fields_changed_during_sample")
    return observed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", required=True, type=int)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--seconds", type=int, default=30)
    args = parser.parse_args()
    if not 0 < args.pid < 0x100000000 or not 1 <= args.seconds <= 45:
        parser.error("--pid must be a positive DWORD; --seconds is 1..45")
    reader = None
    try:
        reader, base, image_size, digest = open_verified_process(args.pid, args.exe)
        print(json.dumps({"status": "ready", "scope": "external_readonly_lifecycle_poll",
                          "exe_sha256": digest, "steam_build": "25732212",
                          "duration_seconds": args.seconds, "interval_ms": 50}), flush=True)
        started = time.monotonic()
        previous = None
        changes = 0
        samples = 0
        unstable = 0
        while time.monotonic() - started < args.seconds:
            try:
                observed = sample(reader, base, image_size)
            except Refusal as exc:
                if str(exc) not in ("session_slot_changed_during_sample", "application_changed_during_sample", "fsm_changed_during_sample", "local_load_fields_changed_during_sample"):
                    raise
                unstable += 1
                time.sleep(0.05)
                continue
            samples += 1
            if observed != previous:
                if changes == MAX_CHANGES:
                    raise Refusal("lifecycle_change_limit_reached")
                print(json.dumps({"status": "change", "elapsed_ms": round((time.monotonic()-started)*1000),
                                  "fields": observed}, sort_keys=True), flush=True)
                changes += 1
                previous = observed
            time.sleep(0.05)
        print(json.dumps({"status": "complete", "samples": samples, "changes": changes,
                          "unstable_samples_omitted": unstable, "read_bytes": reader.bytes_read,
                          "limit": "Polling can miss transitions and does not prove callback ABI, completion or local/network semantics."}), flush=True)
        return 0
    except Refusal as exc:
        print(json.dumps({"status": "refused", "reason": str(exc)}), flush=True)
        return 1
    except (OSError, ValueError, pefile.PEFormatError):
        print(json.dumps({"status": "tool_error", "reason": "input_or_win32_failure"}), flush=True)
        return 2
    except KeyboardInterrupt:
        print(json.dumps({"status": "interrupted"}), flush=True)
        return 130
    finally:
        if reader is not None:
            reader.close()


if __name__ == "__main__":
    raise SystemExit(main())
