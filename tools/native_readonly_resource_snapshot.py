"""Read bounded texture-resource observations from an explicitly selected NMS PID.

Development analysis only. The exact 7.06 image is required. No hooks, native
calls, allocations, process writes, settings access or save access are used.
Output contains aggregate observations and one public stock asset's fields,
never raw addresses, arbitrary resource names or a memory dump. Matching reads
do not prove object lifetime, locking, field semantics or mod compatibility.
"""

from __future__ import annotations

import argparse
from collections import Counter
import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import pefile


EXPECTED_SHA256 = "13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499"
PROCESS_ACCESS = 0x0010 | 0x1000  # VM_READ | QUERY_LIMITED_INFORMATION
MODULE_SNAPSHOT = 0x00000008 | 0x00000010
MAX_ADDRESS = 0x7FFFFFFFFFFF
MAX_READ = 1024 * 1024
TOTAL_READ_LIMIT = 16 * 1024 * 1024
ANCHOR_RVAS = (0x15286C0, 0x508DC0, 0x2D62D60)
MANAGER_CELLS = (0x6E1FC90, 0x59141E0)
APP_CELL = 0x6E8D708
STOCK_ASSET = b"TEXTURES/UI/FRONTEND/ICONS/QUICKMENU/SUMMONPET.DDS"


class Refusal(RuntimeError):
    """A fixed diagnostic code without private process data."""


class ModuleEntry(C.Structure):
    _fields_ = [
        ("dwSize", W.DWORD), ("th32ModuleID", W.DWORD),
        ("th32ProcessID", W.DWORD), ("GlblcntUsage", W.DWORD),
        ("ProccntUsage", W.DWORD), ("modBaseAddr", C.c_void_p),
        ("modBaseSize", W.DWORD), ("hModule", W.HMODULE),
        ("szModule", W.WCHAR * 256), ("szExePath", W.WCHAR * 260),
    ]


def normalized(path: str | Path) -> str:
    return os.path.normcase(os.path.realpath(os.fspath(path)))


class Reader:
    def __init__(self, pid: int):
        self.kernel = C.WinDLL("kernel32", use_last_error=True)
        for name, result, arguments in (
            ("OpenProcess", W.HANDLE, [W.DWORD, W.BOOL, W.DWORD]),
            ("CloseHandle", W.BOOL, [W.HANDLE]),
            ("QueryFullProcessImageNameW", W.BOOL,
             [W.HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD)]),
            ("CreateToolhelp32Snapshot", W.HANDLE, [W.DWORD, W.DWORD]),
            ("Module32FirstW", W.BOOL, [W.HANDLE, C.POINTER(ModuleEntry)]),
            ("Module32NextW", W.BOOL, [W.HANDLE, C.POINTER(ModuleEntry)]),
            ("ReadProcessMemory", W.BOOL,
             [W.HANDLE, C.c_void_p, C.c_void_p, C.c_size_t,
              C.POINTER(C.c_size_t)]),
        ):
            function = getattr(self.kernel, name)
            function.restype, function.argtypes = result, arguments
        self.handle = self.kernel.OpenProcess(PROCESS_ACCESS, False, pid)
        self.bytes_read = 0
        if not self.handle:
            raise Refusal("open_readonly_process_failed")

    def close(self) -> None:
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None

    def process_path(self) -> str:
        buffer = C.create_unicode_buffer(32768)
        size = W.DWORD(len(buffer))
        if not self.kernel.QueryFullProcessImageNameW(
            self.handle, 0, buffer, C.byref(size)
        ):
            raise Refusal("process_image_query_failed")
        return normalized(buffer.value)

    def module_base(self, pid: int, expected_path: str) -> tuple[int, int]:
        snapshot = self.kernel.CreateToolhelp32Snapshot(MODULE_SNAPSHOT, pid)
        if snapshot in (None, C.c_void_p(-1).value):
            raise Refusal("module_snapshot_failed")
        try:
            entry = ModuleEntry()
            entry.dwSize = C.sizeof(entry)
            found = []
            available = self.kernel.Module32FirstW(snapshot, C.byref(entry))
            while available:
                if normalized(entry.szExePath) == expected_path:
                    found.append((entry.modBaseAddr, entry.modBaseSize))
                available = self.kernel.Module32NextW(snapshot, C.byref(entry))
            if len(found) != 1 or not found[0][0]:
                raise Refusal("main_module_not_unique")
            return found[0]
        finally:
            self.kernel.CloseHandle(snapshot)

    def read(self, address: int, size: int) -> bytes:
        if (not isinstance(address, int) or not 0 < size <= MAX_READ
                or address < 0x10000 or address > MAX_ADDRESS - size + 1):
            raise Refusal("native_range_rejected")
        if self.bytes_read + size > TOTAL_READ_LIMIT:
            raise Refusal("read_budget_exceeded")
        self.bytes_read += size
        buffer = C.create_string_buffer(size)
        copied = C.c_size_t()
        if (not self.kernel.ReadProcessMemory(
                self.handle, address, buffer, size, C.byref(copied))
                or copied.value != size):
            raise Refusal("bounded_native_read_failed")
        return buffer.raw

    def pointer(self, address: int) -> int:
        return struct.unpack("<Q", self.read(address, 8))[0]


def manager_header(reader: Reader, base: int) -> tuple[int, int, int]:
    pointers = [reader.pointer(base + rva) for rva in MANAGER_CELLS]
    if not pointers[0] or pointers[0] != pointers[1]:
        raise Refusal("manager_cells_unavailable_or_different")
    header = reader.read(pointers[0] + 0x5C, 12)
    count, table = struct.unpack("<IQ", header)
    if not 0 < count <= 131072 or not table:
        raise Refusal("manager_table_unavailable_or_out_of_bounds")
    return pointers[0], count, table


def resource_fields(data: bytes) -> tuple:
    # Restrict repeat comparisons to the observed identity and readiness fields.
    return (
        data[:0x10C], data[0x138:0x13D],
        data[0x1E0:0x1E4], data[0x260:0x268],
    )


def quick_menu_observation(reader: Reader, base: int) -> dict:
    app = reader.pointer(base + APP_CELL)
    if not app:
        return {"status": "application_unavailable"}
    parent, qam = app + 0x848670, app + 0x849430
    if reader.pointer(qam) != base + 0x4A504E0:
        return {"status": "different_vtable"}
    # This external observation is not synchronized with the game thread.
    indices = reader.read(parent, 8)
    write_index, consumed_index = struct.unpack("<ii", indices)
    if write_index not in (0, 1) or consumed_index not in (0, 1):
        return {"status": "indices_outside_constructor_proven_two_records"}
    depth_data = reader.read(qam + 0xA050, 4)
    depth = struct.unpack("<i", depth_data)[0]
    if depth not in (0, 1, 2):
        return {"status": "depth_out_of_bounds"}
    source_header_address = qam + 0xA058 + depth * 0x10
    copied_header_address = parent + 0x10 + consumed_index * 0x6D0 + 0x610
    source_header = reader.read(source_header_address, 16)
    copied_header = reader.read(copied_header_address, 16)
    source_capacity, source_count, source_data = struct.unpack("<IIQ", source_header)
    copied_capacity, copied_count, copied_data = struct.unpack("<IIQ", copied_header)
    if (source_count > 256 or copied_count > 256
            or source_count > source_capacity or copied_count > copied_capacity):
        return {"status": "row_count_out_of_bounds"}
    source_rows = reader.read(source_data, source_count * 0xE0) if source_count else b""
    copied_rows = reader.read(copied_data, copied_count * 0xE0) if copied_count else b""
    selected = struct.unpack("<i", reader.read(qam + 0xA088 + depth * 4, 4))[0]
    stable = (
        reader.read(parent, 8) == indices
        and reader.read(qam + 0xA050, 4) == depth_data
        and reader.read(source_header_address, 16) == source_header
        and reader.read(copied_header_address, 16) == copied_header
        and (not source_count or reader.read(source_data, len(source_rows)) == source_rows)
        and (not copied_count or reader.read(copied_data, len(copied_rows)) == copied_rows)
        and reader.pointer(base + APP_CELL) == app
    )
    if not stable:
        return {"status": "menu_changed_during_external_read"}
    source_keys = [source_rows[i:i+8] for i in range(0, len(source_rows), 0xE0)]
    copied_keys = [copied_rows[i:i+8] for i in range(0, len(copied_rows), 0xE0)]
    notice = struct.unpack("<f", reader.read(app + 0x4BF50C, 4))[0]
    notice_class = ("nan" if math.isnan(notice) else
                    "positive_infinity" if notice == math.inf else
                    "negative_infinity" if notice == -math.inf else
                    "finite_negative" if notice < 0 else "finite_nonnegative")
    return {
        "status": "expected_vtable_and_repeated_fields_match",
        "depth": depth, "write_index": write_index, "consumed_index": consumed_index,
        "source_row_count": source_count, "copied_row_count": copied_count,
        "selected_index": selected, "source_and_copied_icon_action_keys_equal": source_keys == copied_keys,
        "rows_with_nonzero_icon": sum(struct.unpack_from("<I", source_rows, i)[0] != 0
                                      for i in range(0, len(source_rows), 0xE0)),
        "notice_float_class": notice_class,
    }


def observe(reader: Reader, base: int, image_size: int, entry_limit: int) -> dict:
    manager, count, table = initial_header = manager_header(reader, base)
    examined = min(count, entry_limit)
    table_copy = reader.read(table, examined * 8)
    types: Counter = Counter()
    flags: Counter = Counter()
    vtables: Counter = Counter()
    ready: Counter = Counter()
    stock = []
    occupied = 0
    duplicate_pointers = 0
    seen = set()
    for index, (pointer,) in enumerate(struct.iter_unpack("<Q", table_copy)):
        if not pointer:
            continue
        occupied += 1
        if pointer in seen:
            duplicate_pointers += 1
        seen.add(pointer)
        prefix = reader.read(pointer, 12)
        resource_type = struct.unpack_from("<I", prefix, 8)[0]
        types[resource_type] += 1
        if resource_type != 7:
            continue
        data = reader.read(pointer, 0x268)
        if data[:12] != prefix:
            raise Refusal("resource_prefix_changed")
        fields = resource_fields(data)
        if resource_fields(reader.read(pointer, 0x268)) != fields:
            raise Refusal("texture_fields_changed")
        if reader.pointer(table + index * 8) != pointer:
            raise Refusal("resource_entry_changed")
        vtable = struct.unpack_from("<Q", data)[0]
        vtable_label = (f"0x{vtable-base:X}" if base <= vtable < base + image_size
                        else "outside_main_module")
        vtables[vtable_label] += 1
        flag_tuple = tuple(data[0x138:0x13D])
        flags[",".join(str(value) for value in flag_tuple)] += 1
        image = struct.unpack_from("<I", data, 0x1E0)[0]
        texture = struct.unpack_from("<Q", data, 0x260)[0]
        ready[f"image_nonzero={bool(image)},texture_nonzero={bool(texture)}"] += 1
        name = data[0xC:0x10C].split(b"\0", 1)[0]
        if name.upper() == STOCK_ASSET:
            stock.append({
                "handle": index + 1, "vtable_rva": vtable_label,
                "bytes_138_through_13c": list(flag_tuple),
                "image_nonzero": bool(image), "texture_nonzero": bool(texture),
            })
    if reader.read(table, examined * 8) != table_copy:
        raise Refusal("sampled_resource_table_changed")
    if manager_header(reader, base) != initial_header:
        raise Refusal("manager_table_header_changed")
    qam_status = quick_menu_observation(reader, base)
    return {
        "scope": "bounded_external_readonly_observation",
        "manager_cells_equal": True,
        "table_count": count, "entries_examined": examined,
        "unexamined_entries": count - examined, "occupied_entries": occupied,
        "duplicate_resource_pointers": duplicate_pointers,
        "resource_type_counts": dict(sorted(types.items())),
        "type7_vtable_rva_counts": dict(sorted(vtables.items())),
        "type7_bytes_138_139_13a_13b_13c_counts": dict(sorted(flags.items())),
        "type7_image_texture_presence_counts": dict(sorted(ready.items())),
        "stock_summonpet_asset": stock, "qam": qam_status,
        "read_bytes": reader.bytes_read,
        "limit": "Repeated reads are not a lifetime or synchronization proof; "
                 "field meaning, failure paths and mod behavior remain unverified.",
    }


def open_verified_process(pid: int, exe: Path) -> tuple[Reader, int, int, str]:
    """Open only the exact process and compare bounded loaded-image anchors."""
    if sys.platform != "win32" or C.sizeof(C.c_void_p) != 8:
        raise Refusal("windows_x64_required")
    if not 0 < pid < 0x100000000:
        raise Refusal("positive_process_id_required")
    selected_path = normalized(exe)
    if Path(selected_path).name.lower() != "nms.exe":
        raise Refusal("game_executable_required")
    raw = Path(selected_path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise Refusal("unsupported_executable_sha256")
    pe = pefile.PE(data=raw, fast_load=True)
    if pe.FILE_HEADER.Machine != 0x8664 or pe.OPTIONAL_HEADER.Magic != 0x20B:
        raise Refusal("unsupported_pe_format")
    reader = Reader(pid)
    try:
        if reader.process_path() != selected_path:
            raise Refusal("opened_process_image_path_mismatch")
        base, image_size = reader.module_base(pid, selected_path)
        if image_size != pe.OPTIONAL_HEADER.SizeOfImage:
            raise Refusal("loaded_image_size_mismatch")
        header_offset = pe.DOS_HEADER.e_lfanew
        if reader.read(base + header_offset, 24) != raw[header_offset:header_offset+24]:
            raise Refusal("loaded_pe_header_mismatch")
        # The reviewed prefixes have no relocated absolute-pointer operands.
        for rva in ANCHOR_RVAS:
            if reader.read(base + rva, 16) != pe.get_data(rva, 16):
                raise Refusal("loaded_code_anchor_mismatch")
        return reader, base, image_size, digest
    except BaseException:
        reader.close()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", required=True, type=int)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--entry-limit", type=int, default=10000)
    args = parser.parse_args()
    if not 0 < args.pid < 0x100000000 or not 1 <= args.entry_limit <= 10000:
        parser.error("--pid must be a positive DWORD; --entry-limit is 1..10000")
    reader = None
    try:
        reader, base, image_size, digest = open_verified_process(args.pid, args.exe)
        result = observe(reader, base, image_size, args.entry_limit)
        result.update({"status": "observed", "game_release": "Cosmos 7.06",
                       "steam_build": "25732212", "exe_sha256": digest,
                       "process_access": "VM_READ|QUERY_LIMITED_INFORMATION"})
        print(json.dumps(result, sort_keys=True))
        return 0
    except Refusal as exc:
        print(json.dumps({"status": "refused", "reason": str(exc)}))
        return 1
    except (OSError, ValueError, pefile.PEFormatError):
        print(json.dumps({"status": "tool_error", "reason": "input_or_win32_failure"}))
        return 2
    finally:
        if reader is not None:
            reader.close()


if __name__ == "__main__":
    raise SystemExit(main())
