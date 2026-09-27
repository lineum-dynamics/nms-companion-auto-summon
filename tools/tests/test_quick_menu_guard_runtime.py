"""Offline adapter tests: fake APIs and authored PE/owned byte fixtures only."""

from contextlib import ExitStack
import ctypes
import importlib.util
import io
from pathlib import Path
import struct
import sys
import threading
import types
import unittest
from unittest.mock import Mock, patch


TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
try:
    import quick_menu_guard_runtime as runtime
finally:
    sys.path.pop(0)


PREFIX = bytes(range(16))  # Authored test data, never a game function copy.
BASE = 0x140000000


def pe_bytes():
    data = bytearray(0x400)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HH", data, 0x84, 0x8664, 1)
    struct.pack_into("<H", data, 0x94, 240)
    data[0x98:0x9A] = b"\x0b\x02"
    struct.pack_into("<IIII", data, 0x188 + 8, 128, runtime.GET_BUTTON_RVA - 32, 128, 0x200)
    struct.pack_into("<I", data, 0x188 + 36, 0x60000020)
    data[0x220:0x230] = PREFIX
    return data


class FakeHook:
    def __init__(self, backend):
        self.backend, self.enabled = backend, False

    def enable(self):
        self.enabled = True
        target, relay = self.backend.target, self.backend.relay
        self.backend.memory[target] = (b"\xe9" + struct.pack("<i", relay - target - 5) + PREFIX[5:])
        self.backend.memory[relay] = b"\xff\x25\0\0\0\0" + struct.pack("<Q", self.backend.allocation)
        self.backend.event("enable")

    def close(self):
        raise AssertionError("A pinned hook must never be closed")

    def disable(self):
        raise AssertionError("A pinned hook must never be disabled")


class FakeBackend:
    def __init__(self):
        self.target = BASE + runtime.GET_BUTTON_RVA
        self.allocation, self.trampoline, self.relay = 0x50000000, 0x60000000, BASE + 0x100000
        self.memory = {self.target: PREFIX,
                       self.trampoline: PREFIX[:5] + b"\xff\x25\0\0\0\0" + struct.pack("<Q", self.target + 5)}
        self.events, self.callbacks = [], {}
        self.current_identity = (7, BASE, "test/NMS.exe")
        self.protected = True
        self.hook = None
        self.registry = None
        self.short_read = False

    def event(self, name):
        self.events.append(name)
        callback = self.callbacks.pop(name, None)
        if callback:
            callback()

    def identity(self):
        self.event("identity")
        return self.current_identity

    def read(self, address, size):
        self.event("read")
        data = self.memory[address][:size]
        return data[:-1] if self.short_read else data

    def allocate(self):
        self.event("allocate")
        return self.allocation

    def write_code(self, address, code):
        self.memory[address] = code
        self.event("write")

    def is_rx(self, address, size):
        self.event("rx")
        return self.protected

    def create_hook(self, target, detour):
        self.event("create")
        self.hook = FakeHook(self)
        return self.hook

    def original(self, hook):
        self.event("original")
        return self.trampoline


class Fixture:
    def __init__(self):
        self.context = runtime._Context(BASE, "test/NMS.exe", 7, PREFIX)
        self.backend = FakeBackend()
        self.registry = {"schema": runtime.SCHEMA, "lock": threading.Lock()}
        self.current_registry = self.registry

    def install(self):
        return runtime._ensure_with_backend(self.context, self.backend, self.registry,
                                            lambda: self.current_registry)


class AdapterTests(unittest.TestCase):
    def test_install_pins_before_hook_enable_and_rewrites_before_enable(self):
        f = Fixture()
        f.backend.callbacks["enable"] = lambda: self.assertIs(f.registry["guard"].hook, f.backend.hook)
        guard = f.install()
        self.assertTrue(guard.active)
        self.assertTrue(guard.authorize_append(0x70000000))
        events = f.backend.events
        self.assertEqual(events.count("allocate"), 1)
        self.assertEqual(events.count("create"), 1)
        self.assertEqual(events.count("write"), 2)
        self.assertLess(events.index("write"), events.index("create"))
        self.assertLess(max(i for i, name in enumerate(events) if name == "write"), events.index("enable"))
        self.assertFalse(any("close" in name or "free" in name for name in events))

    def test_duplicate_reuses_validated_owner_without_new_allocation(self):
        f = Fixture()
        first = f.install()
        self.assertIs(f.install(), first)
        self.assertEqual(f.backend.events.count("allocate"), 1)
        self.assertEqual(f.backend.events.count("enable"), 1)

    def test_reload_context_type_does_not_prevent_valid_reuse(self):
        f = Fixture()
        guard = f.install()
        f.context = types.SimpleNamespace(identity=f.context.identity, prefix=PREFIX, base=BASE)
        self.assertIs(f.install(), guard)

    def test_changed_emitter_is_not_silently_reused(self):
        f = Fixture()
        f.install()
        with patch.object(runtime, "build_filter", return_value=b"different"), self.assertRaises(runtime.GuardError):
            f.install()
        self.assertEqual(f.backend.events.count("enable"), 1)

    def test_original_target_mismatch_refuses_before_allocation_and_never_retries(self):
        f = Fixture()
        f.backend.memory[f.backend.target] = b"x" * 16
        with self.assertRaises(runtime.GuardError):
            f.install()
        self.assertNotIn("allocate", f.backend.events)
        self.assertEqual(f.registry["guard"].state, "failed")
        f.backend.memory[f.backend.target] = PREFIX
        with self.assertRaises(runtime.GuardError):
            f.install()
        self.assertNotIn("allocate", f.backend.events)

    def test_partial_read_and_read_exception_refuse(self):
        for failure in ("short", "exception"):
            with self.subTest(failure=failure):
                f = Fixture()
                f.backend.short_read = failure == "short"
                if failure == "exception":
                    f.backend.callbacks["read"] = Mock(side_effect=OSError("private detail"))
                with self.assertRaises(runtime.GuardError):
                    f.install()
                self.assertNotIn("allocate", f.backend.events)

    def test_failed_create_retains_allocation(self):
        f = Fixture()
        f.backend.callbacks["create"] = Mock(side_effect=RuntimeError("already created"))
        with self.assertRaisesRegex(runtime.GuardError, "during hook creation") as failure:
            f.install()
        self.assertNotIn("already created", str(failure.exception))
        guard = f.registry["guard"]
        self.assertEqual(guard.allocation, f.backend.allocation)
        self.assertFalse(guard.active)
        self.assertIsNone(guard.hook)

    def test_failure_during_enable_retains_potentially_active_hook(self):
        f = Fixture()
        f.backend.callbacks["enable"] = Mock(side_effect=RuntimeError("post-enable failure"))
        with self.assertRaises(runtime.GuardError):
            f.install()
        guard = f.registry["guard"]
        self.assertIs(guard.hook, f.backend.hook)
        self.assertTrue(guard.hook.enabled)
        self.assertEqual(guard.allocation, f.backend.allocation)
        self.assertFalse(guard.authorize_append(0x70000000))

    def test_wrong_relay_or_patch_layout_refuses_after_activation(self):
        for key in ("relay", "target"):
            with self.subTest(key=key):
                f = Fixture()
                def corrupt():
                    address = f.backend.relay if key == "relay" else f.backend.target
                    f.backend.memory[address] = b"x" * 16
                f.backend.callbacks["enable"] = corrupt
                with self.assertRaises(runtime.GuardError):
                    f.install()
                self.assertTrue(f.registry["guard"].hook.enabled)
                self.assertEqual(f.registry["guard"].state, "failed")

    def test_trampoline_continuation_is_checked_before_enable_and_during_authorization(self):
        f = Fixture()
        f.backend.memory[f.backend.trampoline] = f.backend.memory[f.backend.trampoline][:-1] + b"x"
        with self.assertRaisesRegex(runtime.GuardError, "trampoline layout"):
            f.install()
        self.assertNotIn("enable", f.backend.events)
        self.assertIs(f.registry["guard"].hook, f.backend.hook)
        f = Fixture()
        guard = f.install()
        f.backend.memory[f.backend.trampoline] = f.backend.memory[f.backend.trampoline][:-1] + b"x"
        self.assertFalse(guard.authorize_append(0x70000000))

    def test_authorization_detects_each_integrity_change_and_never_resumes(self):
        for target in ("target", "allocation", "relay", "trampoline", "protection", "identity", "pin"):
            with self.subTest(target=target):
                f = Fixture()
                guard = f.install()
                if target == "protection":
                    f.backend.protected = False
                elif target == "identity":
                    f.backend.current_identity = (8, BASE, "test/NMS.exe")
                elif target == "pin":
                    f.current_registry = {}
                else:
                    address = getattr(f.backend, target)
                    f.backend.memory[address] = b"x" * len(f.backend.memory[address])
                self.assertFalse(guard.authorize_append(0x70000000))
                self.assertEqual(guard.state, "failed")
                count = len(f.backend.events)
                self.assertFalse(guard.authorize_append(0x70000000))
                self.assertEqual(len(f.backend.events), count)
                self.assertTrue(guard.hook.enabled)

    def test_menu_pointer_is_validated_but_never_read_or_retained(self):
        f = Fixture()
        guard = f.install()
        guard.backend.read = Mock(wraps=guard.backend.read)
        self.assertTrue(guard.authorize_append(0x70000000))
        self.assertFalse(any(call.args[0] == 0x70000000 for call in guard.backend.read.call_args_list))
        self.assertNotIn("menu", guard.__dict__)
        self.assertFalse(guard.authorize_append(0))

    def test_contention_invalidates_owner_without_closing_hook(self):
        f = Fixture()
        guard = f.install()
        f.backend.callbacks["identity"] = lambda: self.assertFalse(guard.authorize_append(0x70000000))
        self.assertFalse(guard.authorize_append(0x70000000))
        self.assertEqual(guard.state, "failed")
        self.assertTrue(guard.hook.enabled)

    def test_install_owner_displacement_cannot_enable_hook(self):
        f = Fixture()
        f.backend.callbacks["allocate"] = lambda: setattr(f, "current_registry", {})
        with self.assertRaises(runtime.GuardError):
            f.install()
        self.assertNotIn("enable", f.backend.events)
        self.assertEqual(f.registry["guard"].allocation, f.backend.allocation)

    def test_reuse_wrong_context_or_registry_is_rejected(self):
        f = Fixture()
        guard = f.install()
        f.context = runtime._Context(BASE, "different/NMS.exe", 7, PREFIX)
        with self.assertRaises(runtime.GuardError):
            f.install()
        self.assertEqual(f.backend.events.count("enable"), 1)
        f.registry["schema"] = "different"
        with self.assertRaises(runtime.GuardError):
            f.install()
        self.assertTrue(guard.hook.enabled)

    def test_setup_contention_does_not_create_duplicate(self):
        f = Fixture()
        f.registry["lock"].acquire()
        try:
            with self.assertRaises(runtime.GuardError):
                f.install()
        finally:
            f.registry["lock"].release()
        self.assertEqual(f.backend.events, [])

    def test_range_rejects_type_underflow_and_overflow(self):
        for address, size in ((True, 4), (1, 4), (0x10000, 0), (runtime.MAX_USER_ADDRESS, 2)):
            with self.subTest(address=address, size=size), self.assertRaises(runtime.GuardError):
                runtime._range(address, size)


class FileAndContextTests(unittest.TestCase):
    def test_authored_pe_maps_only_executable_raw_section(self):
        self.assertEqual(runtime._pe_prefix(io.BytesIO(pe_bytes()), runtime.GET_BUTTON_RVA), PREFIX)

    def test_malformed_or_unbacked_pe_is_rejected(self):
        for offset, replacement in ((0, b"NO"), (0x80, b"NOPE"), (0x84, b"\x4c\x01"),
                                    (0x98, b"\x0b\x01"), (0x188 + 36, b"\0" * 4),
                                    (0x188 + 16, b"\0" * 4)):
            with self.subTest(offset=offset):
                data = pe_bytes()
                data[offset:offset + len(replacement)] = replacement
                with self.assertRaises(runtime.GuardError):
                    runtime._pe_prefix(io.BytesIO(data), runtime.GET_BUTTON_RVA)
        with self.assertRaises(runtime.GuardError):
            runtime._pe_prefix(io.BytesIO(b"MZ"), runtime.GET_BUTTON_RVA)

    def test_hash_must_match_before_prefix_is_returned(self):
        for valid in (False, True):
            with self.subTest(valid=valid), patch.object(Path, "open", return_value=io.BytesIO(pe_bytes())), patch.object(
                    runtime.hashlib, "file_digest", return_value=Mock(hexdigest=lambda: runtime.EXPECTED_EXE_SHA256 if valid else "bad")):
                if valid:
                    self.assertEqual(runtime._load_prefix("test/NMS.exe"), PREFIX)
                else:
                    with self.assertRaises(runtime.GuardError):
                        runtime._load_prefix("test/NMS.exe")

    def context_patches(self, **changes):
        stack = ExitStack()
        internal = types.SimpleNamespace(IS_INJECTED=True, BASE_ADDRESS=BASE, BINARY_PATH="test/NMS.exe")
        for name, value in changes.items():
            setattr(internal, name, value)
        core = types.ModuleType("pymhf.core")
        core._internal = internal
        package = types.ModuleType("pymhf")
        package.core = core
        stack.enter_context(patch.dict(sys.modules, {"pymhf": package, "pymhf.core": core}))
        stack.enter_context(patch.object(runtime.sys, "platform", "win32"))
        stack.enter_context(patch.object(runtime, "version", side_effect=lambda name: "0.2.4" if name == "pymhf" else "0.1.6"))
        stack.enter_context(patch.object(runtime, "_path", side_effect=lambda value: str(value)))
        return stack

    def test_framework_guard_fails_before_windows_backend(self):
        for values in ({"IS_INJECTED": False}, {"BASE_ADDRESS": BASE + 1}, {"BINARY_PATH": "other/NMS.exe"}):
            with self.subTest(values=values), self.context_patches(**values), patch.object(runtime, "_WindowsBackend") as factory:
                with self.assertRaises(runtime.GuardError):
                    runtime._real_context(BASE, "test/NMS.exe")
                factory.assert_not_called()

    def test_platform_filename_and_versions_are_required(self):
        for kind in ("platform", "filename", "version"):
            with self.subTest(kind=kind), self.context_patches(), patch.object(runtime, "_WindowsBackend") as factory:
                with ExitStack() as stack:
                    path = "test/NMS.exe"
                    if kind == "platform":
                        stack.enter_context(patch.object(runtime.sys, "platform", "linux"))
                    elif kind == "filename":
                        path = "test/python.exe"
                    else:
                        stack.enter_context(patch.object(runtime, "version", return_value="wrong"))
                    with self.assertRaises(runtime.GuardError):
                        runtime._real_context(BASE, path)
                    factory.assert_not_called()

    def test_current_native_process_identity_is_checked_before_file_access(self):
        for identity in ((0, BASE, "test/NMS.exe"), (7, BASE + 1, "test/NMS.exe"), (7, BASE, "test/python.exe")):
            with self.subTest(identity=identity), self.context_patches(), patch.object(runtime, "_WindowsBackend") as factory, patch.object(runtime, "_load_prefix") as read:
                factory.return_value.identity.return_value = identity
                with self.assertRaises(runtime.GuardError):
                    runtime._real_context(BASE, "test/NMS.exe")
                read.assert_not_called()

    def test_real_context_success_uses_exact_native_identity_and_file_prefix(self):
        with self.context_patches(), patch.object(runtime, "_WindowsBackend") as factory, patch.object(runtime, "_load_prefix", return_value=PREFIX):
            factory.return_value.identity.return_value = (7, BASE, "test/NMS.exe")
            context, backend = runtime._real_context(BASE, "test/NMS.exe")
            self.assertEqual(context.identity, (7, BASE, "test/NMS.exe"))
            self.assertEqual(context.prefix, PREFIX)
            self.assertIs(backend, factory.return_value)

    def test_public_entry_has_no_test_bypass_and_refusal_does_not_pin(self):
        with patch.object(runtime, "_real_context", side_effect=runtime.GuardError("outside game")), patch.dict(sys.__dict__, {}, clear=False):
            prior = sys.__dict__.pop(runtime.REGISTRY_NAME, None)
            try:
                with self.assertRaises(runtime.GuardError):
                    runtime.ensure_guard(BASE, "test/NMS.exe")
                self.assertNotIn(runtime.REGISTRY_NAME, sys.__dict__)
                with self.assertRaises(TypeError):
                    runtime.ensure_guard(BASE, "test/NMS.exe", backend=FakeBackend())
            finally:
                if prior is not None:
                    sys.__dict__[runtime.REGISTRY_NAME] = prior

    def test_import_makes_no_windows_or_file_calls(self):
        spec = importlib.util.spec_from_file_location("cas_guard_import_test", TOOLS / "quick_menu_guard_runtime.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {spec.name: module}), patch.object(ctypes, "WinDLL", side_effect=AssertionError("No Windows call on import"), create=True), patch.object(Path, "open", side_effect=AssertionError("No file access on import")):
            spec.loader.exec_module(module)


if __name__ == "__main__":
    unittest.main()
