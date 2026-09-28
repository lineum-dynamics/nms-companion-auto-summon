"""Host import and smoke-boundary checks with no real framework or game access."""

from contextlib import contextmanager
import copy
import importlib.util
import io
from pathlib import Path
import sys
import threading
import types
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[2]


def load(filename):
    spec = importlib.util.spec_from_file_location(filename[:-3], ROOT / "tools" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HELPER = load("pymhf_host_import.py")
SMOKE = load("noninteractive_framework_smoke.py")


class HostImportTests(unittest.TestCase):
    def test_only_import_runs_inside_dummy_session_and_context_is_restored(self):
        events = []
        fake_framework = object()
        fake_input, fake_output = object(), object()

        @contextmanager
        def session(**kwargs):
            self.assertEqual(kwargs, {"input": fake_input, "output": fake_output})
            events.append("enter")
            try:
                yield
            finally:
                events.append("exit")

        modules = {
            "prompt_toolkit.application": types.SimpleNamespace(create_app_session=session),
            "prompt_toolkit.input": types.SimpleNamespace(DummyInput=lambda: fake_input),
            "prompt_toolkit.output": types.SimpleNamespace(DummyOutput=lambda: fake_output),
        }

        def importing(name):
            self.assertEqual(name, "pymhf")
            self.assertEqual(events, ["enter"])
            events.append("import")
            return fake_framework

        with patch.dict(sys.modules, modules), patch.object(HELPER.metadata, "version", return_value="0.2.4"), \
                patch.object(HELPER, "import_module", side_effect=importing):
            self.assertIs(HELPER.import_pymhf_noninteractive(), fake_framework)
        self.assertEqual(events, ["enter", "import", "exit"])

    def test_import_exception_preserves_error_and_restores_session(self):
        events = []
        failure = ValueError("owned test failure")

        @contextmanager
        def session(**kwargs):
            events.append("enter")
            try:
                yield
            finally:
                events.append("exit")

        modules = {
            "prompt_toolkit.application": types.SimpleNamespace(create_app_session=session),
            "prompt_toolkit.input": types.SimpleNamespace(DummyInput=object),
            "prompt_toolkit.output": types.SimpleNamespace(DummyOutput=object),
        }
        with patch.dict(sys.modules, modules), patch.object(HELPER.metadata, "version", return_value="0.2.4"), \
                patch.object(HELPER, "import_module", side_effect=failure) as importing:
            with self.assertRaises(ValueError) as raised:
                HELPER.import_pymhf_noninteractive()
        self.assertIs(raised.exception, failure)
        importing.assert_called_once_with("pymhf")
        self.assertEqual(events, ["enter", "exit"])

    def test_different_framework_is_refused_before_import(self):
        with patch.object(HELPER.metadata, "version", return_value="0.2.5"), \
                patch.object(HELPER, "import_module") as importing:
            with self.assertRaises(RuntimeError):
                HELPER.import_pymhf_noninteractive()
        importing.assert_not_called()

    def test_clean_environment_removes_bypasses_without_mutating_caller(self):
        original = {"PYTEST_VERSION": "test", "sphinx_autodoc_running": "1", "PATH": "owned-value"}
        self.assertEqual(SMOKE.clean_environment(original), {"PATH": "owned-value"})
        self.assertEqual(original["PYTEST_VERSION"], "test")

    def test_output_overflow_kills_only_supplied_child_and_caps_storage(self):
        stream = io.BytesIO(b"x" * (SMOKE.MAX_OUTPUT_BYTES + 1024))
        child = Mock()
        output, overflow, errors = bytearray(), threading.Event(), threading.Event()
        SMOKE._read_limited(stream, child, output, overflow, errors)
        child.kill.assert_called_once_with()
        self.assertTrue(overflow.is_set())
        self.assertFalse(errors.is_set())
        self.assertLessEqual(len(output), SMOKE.MAX_OUTPUT_BYTES)
        self.assertTrue(stream.closed)

    def test_bounded_output_does_not_terminate_child(self):
        child = Mock()
        output, overflow, errors = bytearray(), threading.Event(), threading.Event()
        SMOKE._read_limited(io.BytesIO(b"owned output"), child, output, overflow, errors)
        child.kill.assert_not_called()
        self.assertEqual(output, b"owned output")
        self.assertFalse(overflow.is_set())
        self.assertFalse(errors.is_set())

    def test_comparison_rejects_other_failures_bypasses_and_environment_drift(self):
        ordinary = {
            "python": "3.11.9", "bits": 64, "framework": "0.2.4", "prompt_toolkit": "3.0.53",
            "framework_source_sha256": {"owned": "test hash"}, "test_bypasses": False,
            "isolated": True, "bytecode_writes": False, "mode": "ordinary", "imported": False,
            "error_type": SMOKE.EXPECTED_FAILURE,
        }
        adapted = dict(ordinary, mode="adapted", imported=True, error_type=None)
        SMOKE.validate_comparison(ordinary, adapted)
        cases = (
            ("ordinary", "error_type", "builtins.ModuleNotFoundError"),
            ("ordinary", "imported", True),
            ("adapted", "imported", False),
            ("adapted", "framework", "0.2.5"),
            ("both", "test_bypasses", True),
            ("both", "isolated", False),
            ("both", "bytecode_writes", True),
        )
        for target, key, value in cases:
            with self.subTest(target=target, key=key):
                first, second = copy.deepcopy(ordinary), copy.deepcopy(adapted)
                if target in ("ordinary", "both"):
                    first[key] = value
                if target in ("adapted", "both"):
                    second[key] = value
                with self.assertRaises(RuntimeError):
                    SMOKE.validate_comparison(first, second)


if __name__ == "__main__":
    unittest.main()
