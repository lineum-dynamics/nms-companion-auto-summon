"""Explicit Windows own-process native smoke; never accesses a game process.

This registers a temporary MinHook ONLY on executable buffers allocated here.
Run as a separate Python process. The code does not import the mod, enumerate
processes, open a game/save file, or install the candidate guard in NMS.
"""

import ctypes as C
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import struct
import sys

GUARD_SOURCE = Path(__file__).with_name("quick_menu_native_guard.py")
GUARD_SOURCE_BYTES = GUARD_SOURCE.read_bytes()
from quick_menu_native_guard import CUSTOM_ACTION_MARKER, build_filter


class OwnedCode:
    """Test-host allocation only, with write and execute protections separated."""

    def __init__(self, kernel, size=4096):
        self.kernel, self.size = kernel, size
        self.address = kernel.VirtualAlloc(None, size, 0x3000, 0x04)
        if not self.address:
            raise OSError("Cannot allocate test code")

    def write(self, code):
        if not 0 < len(code) <= self.size:
            raise ValueError("Invalid owned code size")
        old = C.c_uint32()
        if not self.kernel.VirtualProtect(self.address, self.size, 0x04, C.byref(old)):
            raise OSError("Cannot make test code writable")
        C.memmove(self.address, code, len(code))
        if not self.kernel.VirtualProtect(self.address, self.size, 0x20, C.byref(old)):
            raise OSError("Cannot make test code executable")
        if not self.kernel.FlushInstructionCache(C.c_void_p(-1), self.address, len(code)):
            raise OSError("Cannot flush test instructions")

    def close(self):
        if self.address and not self.kernel.VirtualFree(self.address, 0, 0x8000):
            raise OSError("Cannot free owned test code")
        self.address = None


def kernel_api():
    if sys.platform != "win32" or C.sizeof(C.c_void_p) != 8:
        raise RuntimeError("This smoke requires Windows x64")
    if Path(sys.executable).name.lower() == "nms.exe":
        raise RuntimeError("Never run this check inside the game")
    kernel = C.WinDLL("kernel32", use_last_error=True)
    for name, result, arguments in (
        ("VirtualAlloc", C.c_void_p, [C.c_void_p, C.c_size_t, C.c_uint32, C.c_uint32]),
        ("VirtualProtect", C.c_int, [C.c_void_p, C.c_size_t, C.c_uint32, C.POINTER(C.c_uint32)]),
        ("VirtualFree", C.c_int, [C.c_void_p, C.c_size_t, C.c_uint32]),
        ("FlushInstructionCache", C.c_int, [C.c_void_p, C.c_void_p, C.c_size_t]),
    ):
        function = getattr(kernel, name)
        function.restype, function.argtypes = result, arguments
    return kernel


def caller_code(target):
    # Own test caller: menu, port, button, validation, debug. Preserve RDI and
    # supply the 32-byte shadow space with Win64's required stack alignment.
    code = bytearray.fromhex(
        "57 48 83 EC 20 "                     # push rdi; sub rsp, 32
        "48 89 CF 48 89 D1 "                  # mov rdi, rcx; mov rcx, rdx
        "44 89 C2 45 89 C8 "                  # mov edx, r8d; mov r8d, r9d
        "44 0F B6 4C 24 50 "                  # movzx r9d, byte [rsp+80]
        "48 B8"
    )
    code.extend(struct.pack("<Q", target))
    code.extend(bytes.fromhex("FF D0"))       # call rax
    return_offset = len(code)
    code.extend(bytes.fromhex("48 83 C4 20 5F C3"))
    return bytes(code), return_offset


def check():
    kernel = kernel_api()
    if version("cyminhook") != "0.1.6":
        raise RuntimeError("Use the audited cyminhook 0.1.6 environment")
    import cyminhook

    allocations = []
    hook = None
    enabled = False
    cases = []

    def allocate():
        allocation = OwnedCode(kernel)
        allocations.append(allocation)
        return allocation

    def expect(name, actual, expected):
        if actual != expected:
            raise AssertionError(f"Native candidate failed: {name}")
        cases.append(name)

    try:
        target, shim, caller, other_caller = [allocate() for _ in range(4)]
        # Deliberately authored target: combine ALL native arguments. This is
        # not a game function and its non-Boolean result tests full forwarding.
        # A five-byte register-home store gives MinHook an exact one-instruction
        # prefix, also exercising the runtime adapter's 19-byte trampoline rule.
        home_store = bytes.fromhex("48 89 5C 24 08")  # mov [rsp+8], rbx
        target.write(home_store + bytes.fromhex("8B 01 31 D0 44 31 C0 44 31 C8 C3") + b"\x90" * 32)
        caller_bytes, return_offset = caller_code(target.address)
        caller.write(caller_bytes)
        other_caller.write(caller_bytes)
        expected_return = caller.address + return_offset
        shim.write(build_filter(expected_return, target.address))
        signature = C.CFUNCTYPE(C.c_uint32, C.c_void_p, C.c_uint32, C.c_uint32, C.c_bool)
        hook = cyminhook.MinHook(signature=signature, target=target.address, detour=shim.address)
        original = C.cast(hook.original, C.c_void_p).value
        expect("complete_original_trampoline_layout",
               C.string_at(original, 19), home_store + b"\xff\x25\0\0\0\0" + struct.pack("<Q", target.address + 5))
        shim.write(build_filter(expected_return, original))
        harness_signature = C.CFUNCTYPE(C.c_uint32, C.c_void_p, C.c_void_p,
                                       C.c_uint32, C.c_uint32, C.c_bool)
        invoke = harness_signature(caller.address)
        unrelated = harness_signature(other_caller.address)
        direct = signature(target.address)
        menu = C.create_string_buffer(0xA100)
        items = C.create_string_buffer(0xE0 * 3)
        menu_ptr, items_ptr = C.addressof(menu), C.addressof(items)
        port = C.c_uint32(0x9A7142D5)

        def put_menu(offset, fmt, *values):
            C.memmove(menu_ptr + offset, struct.pack(fmt, *values), struct.calcsize(fmt))

        def put_item(index, action=0, marker=CUSTOM_ACTION_MARKER):
            C.memmove(items_ptr + index * 0xE0 + 4, struct.pack("<i", action), 4)
            C.memmove(items_ptr + index * 0xE0 + 0x88, marker, 16)

        def fixture(depth=1, selection=1, count=3, capacity=3, data=None):
            C.memset(menu_ptr, 0, C.sizeof(menu))
            C.memset(items_ptr, 0, C.sizeof(items))
            put_menu(0xA050, "<i", depth)
            if 0 <= depth <= 2:
                put_menu(0xA058 + depth * 16, "<IIQ", capacity, count,
                         items_ptr if data is None else data)
                put_menu(0xA088 + depth * 4, "<i", selection)
            put_item(1)

        def run(menu_address=menu_ptr, button=0x163, validation=9, debug=True):
            return invoke(menu_address, C.byref(port), button, validation, debug)

        def normal(button=0x163, validation=9, debug=True):
            return port.value ^ button ^ validation ^ int(debug)

        fixture()
        expect("unhooked_owned_target", run(), normal())
        hook.enable()
        enabled = True
        expect("integer_native_detour_blocks_tagged_none", run(), 0)
        expect("no_physical_button_assumption", run(button=3, validation=77, debug=False), 0)
        # An invalid RDI value is deliberately supplied to another native call
        # site: successful forwarding proves the early return-address filter.
        expect("unrelated_caller_never_reads_menu",
               unrelated(1, C.byref(port), 0x163, 9, True), normal())
        expect("direct_call_preserves_all_arguments",
               direct(C.byref(port), 0x163, 9, True), normal())
        for depth in (0, 1, 2):
            fixture(depth=depth)
            expect(f"tagged_none_at_depth_{depth}", run(), 0)
        for action in (1, 45, 46, 66):
            fixture()
            put_item(1, action=action)
            expect(f"native_action_{action}_preserved", run(), normal())
        for index in range(16):
            fixture()
            marker = bytearray(CUSTOM_ACTION_MARKER)
            marker[index] ^= 1
            put_item(1, marker=bytes(marker))
            expect(f"marker_byte_{index}_required", run(), normal())
        for depth in (-1, 3, 0x7FFFFFFF):
            fixture(depth=depth)
            expect(f"invalid_depth_{depth}_not_dereferenced", run(), normal())
        for selected in (-1, 3, 0x7FFFFFFF):
            fixture(selection=selected, data=1)
            expect(f"invalid_selection_{selected}_not_dereferenced", run(), normal())
        fixture(count=0, data=1)
        expect("empty_vector_not_dereferenced", run(), normal())
        fixture(count=0xFFFFFFFF, data=1)
        expect("negative_native_count_not_dereferenced", run(), normal())
        fixture(count=4, capacity=3, data=1)
        expect("inconsistent_count_capacity_not_dereferenced", run(), normal())
        fixture(capacity=257)
        expect("tag_remains_protected_after_capacity_growth", run(), 0)
        fixture(capacity=0xFFFFFFFF, data=1)
        expect("negative_native_capacity_not_dereferenced", run(), normal())
        fixture(data=0)
        expect("null_vector_not_dereferenced", run(), normal())
        expect("null_menu_not_dereferenced", run(menu_address=0), normal())
        fixture(selection=0)
        expect("neighboring_untagged_none_preserved", run(), normal())
        fixture()
        before_menu, before_items = menu.raw, items.raw
        for _ in range(10000):
            if run() != 0:
                raise AssertionError("Repeated tagged call changed result")
        expect("menu_and_item_bytes_unchanged", (menu.raw, items.raw), (before_menu, before_items))
        hook.disable()
        enabled = False
        expect("own_target_restored_after_disable", run(), normal())
        hook.close()
        hook = None
    finally:
        # There are no game pointers or concurrently executing test callbacks.
        if hook is not None:
            if enabled:
                hook.disable()
            hook.close()
        for allocation in reversed(allocations):
            allocation.close()

    if GUARD_SOURCE.read_bytes() != GUARD_SOURCE_BYTES:
        raise RuntimeError("Native guard source changed during smoke verification")
    record = {
        "source_sha256": hashlib.sha256(GUARD_SOURCE_BYTES).hexdigest(),
        "cyminhook": "0.1.6", "cases_passed": len(cases), "cases": cases,
        "repeated_tagged_calls": 10000, "integer_native_detour_verified": True,
        "native_menu_writes": False, "hook_target": "own_allocated_test_buffer",
        "game_accessed": False, "live_verified": False,
        "limit": "Owned buffers do not establish game object lifetime or binding-path coverage.",
    }
    report = Path(__file__).resolve().parents[1] / "build/validation/menu-native-guard-smoke.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


if __name__ == "__main__":
    print(json.dumps(check()))
