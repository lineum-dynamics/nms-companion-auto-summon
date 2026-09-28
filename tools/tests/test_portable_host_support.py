"""Owned portable adapters: no framework execution, game or native calls."""

from importlib import util
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
from typing import NamedTuple
import unittest
from unittest.mock import Mock, patch


SOURCE = Path(__file__).resolve().parents[1] / "portable_host_support.py"
spec = util.spec_from_file_location("portable_host_support_tests", SOURCE)
support = util.module_from_spec(spec)
spec.loader.exec_module(support)


class Record(NamedTuple):
    value: str
    is_file: bool


class PortableHostSupportTests(unittest.TestCase):
    def test_unicode_file_record_preserves_file_globals_and_coding_cookie(self):
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / "K\u00e1\u0165a \u732b.py"
            script.write_bytes(b"# coding: latin-1\nanswer = prior + 1\ncaption = 'caf\xe9'\nseen_file = __file__\n")
            namespace = {"prior": 40}
            exec(support.file_as_source(str(script)), namespace, namespace)
            self.assertEqual(namespace["answer"], 41)
            self.assertEqual(namespace["caption"], "caf\u00e9")
            self.assertEqual(namespace["seen_file"], str(script))

    def test_adapter_copies_files_and_preserves_original_code_record(self):
        code = Record("sentinel = 1", False)
        path = str(Path(__file__).resolve())
        records = [code, Record(path, True)]
        adapted = support.adapt_records(records, Record)
        self.assertEqual(adapted[0], Record(support.INTERPRETER_PRELUDE, False))
        self.assertIs(adapted[1], code)
        self.assertFalse(adapted[2].is_file)
        self.assertIn(repr(path), adapted[2].value)
        self.assertTrue(records[1].is_file)

    def test_adapter_refuses_malformed_or_unbounded_records(self):
        for records in (None, (), [], [Record("a", False)] * 65, [("a", False)],
                        [Record("a\0b", False)], [Record("a", 1)], [Record("x" * 1048577, False)]):
            with self.subTest(records_type=type(records)), self.assertRaises(ValueError):
                support.adapt_records(records, Record)
        for path in (None, "", "relative.py", "a\0b"):
            with self.assertRaises(ValueError):
                support.file_as_source(path)

    def test_configuration_wraps_only_run_data_once_and_keeps_arguments(self):
        original = Mock(return_value="owned-result")
        original._cas_unicode_adapter = False
        runner = type("Runner", (), {"run_data": original})
        dllinject = SimpleNamespace(pyRunner=runner, StringType=Record)
        package = ModuleType("pyrun_injected")
        package.dllinject = dllinject
        bootstrap = SimpleNamespace(PORTABLE_BOOTSTRAP_READY=True)
        with patch.object(support.metadata, "version", side_effect=lambda name: {"pymhf":"0.2.4", "pyrun-injected":"0.2.0"}[name]), \
                patch.dict(sys.modules, {"pyrun_injected": package, "sitecustomize": bootstrap}):
            support.configure_host()
            wrapped = runner.run_data
            support.configure_host()
            self.assertIs(wrapped, runner.run_data)
            instance = runner()
            result = instance.run_data([Record("pass", False)], run_in_directory="owned", inject_sys_path=True)
        self.assertEqual(result, "owned-result")
        original.assert_called_once_with(instance, [Record(support.INTERPRETER_PRELUDE, False), Record("pass", False)], run_in_directory="owned", inject_sys_path=True)
        self.assertEqual(set(vars(runner)) - {"__module__", "__dict__", "__weakref__", "__doc__"}, {"run_data"})

    def test_wrong_framework_refuses_before_vendor_import(self):
        with patch.object(support.metadata, "version", return_value="unreviewed"):
            with self.assertRaises(RuntimeError):
                support.configure_host()


class BoundedSteamStartTests(unittest.TestCase):
    def setUp(self):
        self.child = SimpleNamespace(pid=321, name=lambda: "NMS.exe")
        self.parent = SimpleNamespace(name=lambda: "steam.exe", children=Mock(return_value=[self.child]))
        self.binary = SimpleNamespace(process_handle=123, close_process=Mock())
        self.framework = SimpleNamespace(
            psutil=SimpleNamespace(process_iter=Mock(return_value=[self.parent]),
                                   NoSuchProcess=LookupError, AccessDenied=PermissionError),
            webbrowser=SimpleNamespace(open=Mock(return_value=True)),
            pymem=SimpleNamespace(Pymem=Mock(return_value=self.binary),
                exception=SimpleNamespace(ProcessNotFound=FileNotFoundError, CouldNotOpenProcess=PermissionError),
                process=SimpleNamespace(enum_process_module=Mock(return_value=[object()]))),
            dllinject=SimpleNamespace(pyRunner=Mock(return_value="guarded-runner")),
            WrappedProcess=Mock(return_value="owned-wrapper"),
            get_process_when_ready=lambda *args: None,
        )

    def call(self, **overrides):
        options = dict(cmd=["steam://rungameid/275850"], target="NMS.exe", required_assemblies=[],
                       start_paused=False, monotonic=lambda: 0, sleep=Mock())
        options.update(overrides)
        return support.bounded_steam_start(self.framework, **options)

    def test_opens_only_the_found_steam_child_pid_and_keeps_runner_guard(self):
        self.assertEqual(self.call(), ("guarded-runner", "owned-wrapper"))
        self.framework.webbrowser.open.assert_called_once_with("steam://rungameid/275850")
        self.framework.pymem.Pymem.assert_called_once_with(321)
        self.framework.dllinject.pyRunner.assert_called_once_with(self.binary)
        self.binary.close_process.assert_not_called()

    def test_unreviewed_arguments_do_not_open_uri_or_process(self):
        for change in ({"cmd":["steam://rungameid/1"]}, {"target":"other.exe"},
                       {"required_assemblies":None}, {"required_assemblies":["unreviewed.dll"]}, {"start_paused":True}):
            with self.subTest(change=change), self.assertRaises(support.PortableLaunchError):
                self.call(**change)
        self.framework.webbrowser.open.assert_not_called()
        self.framework.pymem.Pymem.assert_not_called()

    def test_missing_steam_does_not_open_uri_or_process(self):
        self.framework.psutil.process_iter.return_value = []
        with self.assertRaises(support.PortableLaunchError):
            self.call()
        self.framework.webbrowser.open.assert_not_called()
        self.framework.pymem.Pymem.assert_not_called()

    def test_inaccessible_unclassified_process_does_not_hide_identified_steam(self):
        inaccessible = SimpleNamespace(name=Mock(side_effect=PermissionError("protected process")))
        self.framework.psutil.process_iter.return_value = [inaccessible, self.parent]
        self.assertEqual(self.call(), ("guarded-runner", "owned-wrapper"))
        self.framework.pymem.Pymem.assert_called_once_with(self.child.pid)
        self.framework.dllinject.pyRunner.assert_called_once_with(self.binary)

    def test_inaccessible_process_alone_does_not_establish_steam_identity(self):
        inaccessible = SimpleNamespace(name=Mock(side_effect=PermissionError("protected process")))
        self.framework.psutil.process_iter.return_value = [inaccessible]
        with self.assertRaisesRegex(support.PortableLaunchError, "One running Steam process"):
            self.call()
        self.framework.webbrowser.open.assert_not_called()
        self.framework.pymem.Pymem.assert_not_called()

    def test_identified_steam_ambiguity_still_refuses_with_inaccessible_process(self):
        inaccessible = SimpleNamespace(name=Mock(side_effect=PermissionError("protected process")))
        second_parent = SimpleNamespace(name=lambda: "steam.exe")
        self.framework.psutil.process_iter.return_value = [inaccessible, self.parent, second_parent]
        with self.assertRaisesRegex(support.PortableLaunchError, "One running Steam process"):
            self.call()
        self.framework.webbrowser.open.assert_not_called()
        self.framework.pymem.Pymem.assert_not_called()

    def test_selected_steam_children_access_failure_remains_fatal(self):
        self.parent.children.side_effect = PermissionError("selected parent unavailable")
        with self.assertRaisesRegex(support.PortableLaunchError, "Steam children could not be inspected"):
            self.call()
        self.framework.pymem.Pymem.assert_not_called()
        self.framework.dllinject.pyRunner.assert_not_called()

    def test_selected_steam_child_name_access_failure_remains_fatal(self):
        self.child.name = Mock(side_effect=PermissionError("selected child unavailable"))
        with self.assertRaisesRegex(support.PortableLaunchError, "Steam children could not be inspected"):
            self.call()
        self.framework.pymem.Pymem.assert_not_called()
        self.framework.dllinject.pyRunner.assert_not_called()

    def test_timeout_is_bounded_and_sleeps_without_constructing_runner(self):
        self.parent.children.return_value = []
        sleep = Mock()
        with self.assertRaisesRegex(support.PortableLaunchError, "120 seconds"):
            self.call(monotonic=Mock(side_effect=[0, 0, 121]), sleep=sleep)
        sleep.assert_called_once_with(0.1)
        self.framework.dllinject.pyRunner.assert_not_called()

    def test_empty_modules_closes_only_owned_handle_then_waits(self):
        self.framework.pymem.process.enum_process_module.return_value = []
        with self.assertRaises(support.PortableLaunchError):
            self.call(monotonic=Mock(side_effect=[0, 0, 121]))
        self.binary.close_process.assert_called_once_with()
        self.framework.dllinject.pyRunner.assert_not_called()

    def test_ambiguous_target_never_constructs_runner(self):
        self.parent.children.return_value = [self.child, self.child]
        with self.assertRaises(support.PortableLaunchError):
            self.call()
        self.framework.pymem.Pymem.assert_not_called()

    def test_actual_injection_guard_refusal_is_not_swallowed_or_retried(self):
        refusal = RuntimeError("synthetic actual-handle refusal")
        self.framework.dllinject.pyRunner.side_effect = refusal
        with self.assertRaises(RuntimeError) as result:
            self.call()
        self.assertIs(result.exception, refusal)
        self.framework.dllinject.pyRunner.assert_called_once_with(self.binary)

    def test_install_is_inert_and_idempotent(self):
        support.install_bounded_steam_start(self.framework)
        first = self.framework.get_process_when_ready
        support.install_bounded_steam_start(self.framework)
        self.assertIs(self.framework.get_process_when_ready, first)
        self.framework.psutil.process_iter.assert_not_called()
        self.framework.webbrowser.open.assert_not_called()

    def test_missing_bootstrap_refuses_before_vendor_import(self):
        with patch.object(support.metadata, "version", side_effect=lambda name: {"pymhf":"0.2.4", "pyrun-injected":"0.2.0"}[name]), \
                patch.dict(sys.modules, {"sitecustomize": SimpleNamespace()}):
            with self.assertRaises(RuntimeError):
                support.configure_host()


class FrameworkResultGuardTests(unittest.TestCase):
    def setUp(self):
        self.entry = lambda: None
        self.entry._cas_unicode_adapter = True
        self.entry._cas_run_data_entries = 4
        self.framework = SimpleNamespace(
            run_module=lambda *args, **kwargs: None,
            dllinject=SimpleNamespace(pyRunner=SimpleNamespace(run_data=self.entry)),
        )

    def test_none_before_any_new_execution_is_a_launch_failure(self):
        support.install_run_module_result_guard(self.framework)
        with self.assertRaises(support.PortableLaunchError):
            self.framework.run_module("owned-mod", {})

    def test_none_after_execution_entry_is_preserved_without_success_claim(self):
        def normal(*args, **kwargs):
            self.entry._cas_run_data_entries += 1
        self.framework.run_module = normal
        support.install_run_module_result_guard(self.framework)
        self.assertIsNone(self.framework.run_module("owned-mod", {}))

    def test_refusal_exception_propagates_unchanged(self):
        error = RuntimeError("synthetic compatibility refusal")
        def refusal(*args, **kwargs):
            raise error
        self.framework.run_module = refusal
        support.install_run_module_result_guard(self.framework)
        with self.assertRaises(RuntimeError) as result:
            self.framework.run_module("owned-mod", {})
        self.assertIs(result.exception, error)

    def test_repeated_install_does_not_rewrap_or_execute_framework(self):
        support.install_run_module_result_guard(self.framework)
        original = self.framework.run_module
        support.install_run_module_result_guard(self.framework)
        self.assertIs(self.framework.run_module, original)
        self.assertEqual(self.entry._cas_run_data_entries, 4)


if __name__ == "__main__":
    unittest.main()
