"""Owned-file/fake-Windows compatibility checks; no game or real dialogs."""

import builtins
import ctypes as C
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("cas_compatibility_tested", ROOT / "cas_compatibility.py")
COMPAT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPAT)


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / "owned-\u6d4b\u8bd5-\u010desk\u00fd"
        self.executable = self.directory / "Binaries" / "NMS.exe"
        self.executable.parent.mkdir(parents=True)
        self.executable.write_bytes(b"owned executable fixture, never run")
        self.checksum = hashlib.sha256(self.executable.read_bytes()).hexdigest()
        self.hash_patch = patch.object(COMPAT, "SUPPORTED_GAME_SHA256", self.checksum)
        self.hash_patch.start()
        self.addCleanup(self.hash_patch.stop)

    def assert_error(self, key, operation):
        with self.assertRaises(COMPAT.CompatibilityError) as raised:
            operation()
        self.assertEqual(raised.exception.key, key)
        self.assertEqual(str(raised.exception), key)
        return raised.exception

    def test_import_has_no_file_process_framework_or_dialog_access(self):
        source = (ROOT / "cas_compatibility.py").read_text(encoding="utf-8")
        original_import = builtins.__import__
        def guarded_import(name, *args, **kwargs):
            if name.split(".", 1)[0] in {"pymhf", "pymem", "pyrun_injected"}:
                self.fail("Import must not load an injector or framework")
            return original_import(name, *args, **kwargs)
        with patch("builtins.__import__", side_effect=guarded_import), \
                patch.object(Path, "open", side_effect=AssertionError("file read")), \
                patch.object(Path, "resolve", side_effect=AssertionError("filesystem resolution")), \
                patch.object(C, "WinDLL", side_effect=AssertionError("Windows API"), create=True):
            namespace = {"__file__": str(ROOT / "cas_compatibility.py"), "__name__": "inert_import"}
            exec(compile(source, "cas_compatibility.py", "exec"), namespace)
        self.assertEqual(namespace["PROFILE"], {
            "schema_version": 1, "steam_build": "25442159", "game_release": "Cosmos 7.04",
            "exe_sha256": "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb",
            "framework_version": "0.2.4"})

    def test_directory_check_hashes_owned_executable_without_writing(self):
        before = {path.relative_to(self.directory): path.read_bytes()
                  for path in self.directory.rglob("*") if path.is_file()}
        self.assertEqual(COMPAT.verify_game_directory(self.directory), self.executable.resolve())
        after = {path.relative_to(self.directory): path.read_bytes()
                 for path in self.directory.rglob("*") if path.is_file()}
        self.assertEqual(after, before)

    def test_missing_relative_or_invalid_directory_never_creates_files(self):
        for value in (None, "", "relative", "bad\0path", self.directory / "missing", self.executable):
            with self.subTest(value=value):
                self.assert_error("launcher.game_required", lambda: COMPAT.verify_game_directory(value))
        self.assertFalse((self.directory / "missing").exists())

    def test_wrong_hash_unreadable_and_mid_hash_change_have_distinct_errors(self):
        self.executable.write_bytes(b"changed fixture")
        self.assert_error("launcher.unsupported_game", lambda: COMPAT.verify_game_directory(self.directory))
        with patch.object(Path, "open", side_effect=PermissionError("private path must not leak")):
            self.assert_error("launcher.unreadable_game", lambda: COMPAT.verify_game_directory(self.directory))
        with patch.object(COMPAT.os, "fstat", side_effect=[SimpleNamespace(st_size=4, st_mtime_ns=1),
                                                        SimpleNamespace(st_size=4, st_mtime_ns=2)]):
            self.assert_error("launcher.game_changed", lambda: COMPAT.verify_game_directory(self.directory))

    def test_actual_target_is_queried_and_rehashed_for_every_call(self):
        query = Mock(return_value=str(self.executable))
        self.assertEqual(COMPAT.verify_target(71, self.executable, query), self.executable.resolve())
        self.executable.write_bytes(b"different executable after first DLL check")
        self.assert_error("launcher.unsupported_game", lambda: COMPAT.verify_target(71, self.executable, query))
        self.assertEqual(query.call_args_list, [unittest.mock.call(71), unittest.mock.call(71)])

    def test_selected_path_cannot_stand_in_for_a_different_actual_target(self):
        other = Path(self.temporary.name) / "another" / "NMS.exe"
        other.parent.mkdir()
        other.write_bytes(self.executable.read_bytes())
        query = Mock(return_value=str(other))
        self.assert_error("launcher.game_changed", lambda: COMPAT.verify_target(71, self.executable, query))
        self.assertEqual(COMPAT.verify_target(71, query=query), other.resolve())
        self.assert_error("launcher.game_changed", lambda: COMPAT.verify_target(71, other / "missing", query))

    def test_invalid_handle_query_failure_and_nonexecutable_are_refused(self):
        query = Mock(return_value=str(self.executable))
        for handle in (None, 0, -1, False, True, (1 << 64) - 1, 1 << 64, "71"):
            with self.subTest(handle=handle):
                self.assert_error("launcher.unreadable_game", lambda: COMPAT.verify_target(handle, query=query))
        query.assert_not_called()
        for result in (None, "", "NMS.exe", str(self.executable) + "\0", str(self.directory / "absent")):
            with self.subTest(result=result):
                self.assert_error("launcher.unreadable_game", lambda: COMPAT.verify_target(71, query=lambda _: result))
        self.assert_error("launcher.unreadable_game", lambda: COMPAT.verify_target(71, query=Mock(side_effect=OSError())))
        other = self.executable.with_name("another.exe")
        other.write_bytes(self.executable.read_bytes())
        self.assert_error("launcher.unsupported_game", lambda: COMPAT.verify_target(71, query=lambda _: str(other)))

    def test_bounded_query_uses_actual_handle_unicode_and_win32_flag(self):
        calls = []
        def api(handle, flags, buffer, size):
            calls.append((handle, flags, len(buffer), size._obj.value))
            buffer.value = str(self.executable)
            size._obj.value = len(buffer.value.encode("utf-16-le")) // 2
            return 1
        self.assertEqual(COMPAT._query_target_image(71, api), str(self.executable))
        self.assertEqual(calls, [(71, 0, COMPAT.MAX_PATH_CHARACTERS, COMPAT.MAX_PATH_CHARACTERS)])

    def test_query_counts_non_bmp_path_as_utf16_code_units(self):
        text = "C:\\owned-\U0001f43e-\u6d4b\u8bd5\\NMS.exe"
        code_units = len(text.encode("utf-16-le")) // 2
        self.assertGreater(code_units, len(text))
        def api(_handle, _flags, buffer, size_pointer):
            buffer.value = text
            size_pointer._obj.value = code_units
            return 1
        self.assertEqual(COMPAT._query_target_image(71, api), text)

        def wrong_size(_handle, _flags, buffer, size_pointer):
            buffer.value = text
            size_pointer._obj.value = len(text)
            return 1
        self.assert_error("launcher.unreadable_game", lambda: COMPAT._query_target_image(71, wrong_size))

    def test_query_rejects_failure_truncation_embedded_nul_and_wrong_length(self):
        for result, size, text in ((0, 3, "abc"), (1, 0, ""),
                                   (1, COMPAT.MAX_PATH_CHARACTERS, "abc"),
                                   (1, 8, "abc"), (1, 7, "abc\0def"),
                                   (1, 6, "\U0001f43e\0def"), (1, 1, "\ud800")):
            with self.subTest(result=result, size=size, text=text):
                def api(_handle, _flags, buffer, size_pointer):
                    buffer.value = text
                    size_pointer._obj.value = size
                    return result
                self.assert_error("launcher.unreadable_game", lambda: COMPAT._query_target_image(71, api))

    def test_framework_check_uses_metadata_and_refuses_errors(self):
        entries = SimpleNamespace(select=Mock(return_value=()))
        with patch.object(COMPAT.metadata, "version", return_value="0.2.4") as version, \
                patch.object(COMPAT.metadata, "entry_points", return_value=entries):
            self.assertIs(COMPAT.verify_framework(), True)
            version.assert_called_once_with("pymhf")
            entries.select.assert_called_once_with(group="pymhflib")
        for value in ("0.2.3", "0.2.5", None):
            with patch.object(COMPAT.metadata, "version", return_value=value):
                self.assert_error("launcher.wrong_framework", COMPAT.verify_framework)
        with patch.object(COMPAT.metadata, "version", side_effect=COMPAT.metadata.PackageNotFoundError()):
            self.assert_error("launcher.wrong_framework", COMPAT.verify_framework)

    def test_foreign_framework_libraries_and_unreadable_registry_are_rejected(self):
        entries = SimpleNamespace(select=Mock(return_value=(SimpleNamespace(name="foreign-library"),)))
        with patch.object(COMPAT.metadata, "version", return_value="0.2.4"), \
                patch.object(COMPAT.metadata, "entry_points", return_value=entries):
            self.assert_error("launcher.invalid_package", COMPAT.verify_framework)
            entries.select.assert_called_once_with(group="pymhflib")
        with patch.object(COMPAT.metadata, "version", return_value="0.2.4"), \
                patch.object(COMPAT.metadata, "entry_points", side_effect=OSError("unreadable metadata")):
            self.assert_error("launcher.wrong_framework", COMPAT.verify_framework)

    def test_error_diagnostics_only_contain_stable_category(self):
        error = COMPAT.CompatibilityError("launcher.unsupported_game", build="private data")
        self.assertEqual(str(error), "launcher.unsupported_game")
        self.assertEqual(error.fields, {"build": "private data"})
        unknown = COMPAT.CompatibilityError("not a known message", path="private")
        self.assertEqual(unknown.key, "launcher.invalid_package")
        self.assertEqual(unknown.fields, {})


class WarningTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        for code in COMPAT.LOCALES:
            shutil.copyfile(ROOT / "locales" / (code + ".json"), self.directory / (code + ".json"))
        self.locale_patch = patch.object(COMPAT, "LOCALES_DIRECTORY", self.directory)
        self.locale_patch.start()
        self.addCleanup(self.locale_patch.stop)

    def alter(self, code, mutate):
        path = self.directory / (code + ".json")
        data = json.loads(path.read_text(encoding="utf-8"))
        mutate(data)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_all_fourteen_warning_catalogs_format_their_actual_translation(self):
        for code in COMPAT.LOCALES:
            catalog = json.loads((self.directory / (code + ".json")).read_text(encoding="utf-8"))
            for key in COMPAT.WARNING_KEYS:
                with self.subTest(code=code, key=key):
                    expected = catalog["messages"][key]["text"].format(
                        build="Cosmos 7.04 (Steam 25442159)", version="0.2.4")
                    self.assertEqual(COMPAT.warning_text(key, code), expected)

    def test_aliases_and_unsupported_languages_use_explicit_supported_catalogs(self):
        aliases = {"FR_fr": "fr", "pt_br": "pt-BR", "pt": "pt-PT", "es-MX": "es-ES",
                   "zh-CN": "zh-Hans", "zh-TW": "zh-Hant", "zh-HK": "zh-Hant",
                   "zh-Hans-SG": "zh-Hans", "zh-Hant-HK": "zh-Hant", "EN-gb": "en",
                   "cs-CZ": "en", "unsupported": "en", "../../outside": "en"}
        for alias, expected in aliases.items():
            with self.subTest(alias=alias):
                self.assertEqual(COMPAT.warning_text("launcher.game_required", alias),
                                 COMPAT.warning_text("launcher.game_required", expected))

    def test_default_language_queries_host_ui_only_and_falls_back_on_failure(self):
        with patch.object(COMPAT, "_windows_ui_language", return_value="fr-FR"):
            self.assertEqual(COMPAT.warning_text("launcher.game_required"), COMPAT.warning_text("launcher.game_required", "fr"))
        with patch.object(COMPAT, "_windows_ui_language", side_effect=OSError()):
            self.assertEqual(COMPAT.warning_text("launcher.game_required"), COMPAT.warning_text("launcher.game_required", "en"))
        def locale_name(language, buffer, capacity, flags):
            self.assertEqual((language, capacity, flags), (0x40C, 85, 0))
            buffer.value = "fr-FR"
            return 6
        api = SimpleNamespace(GetUserDefaultUILanguage=lambda: 0x40C, LCIDToLocaleName=locale_name)
        self.assertEqual(COMPAT._windows_ui_language(api), "fr-FR")

    def test_missing_catalog_uses_only_generic_english_package_fallback(self):
        (self.directory / "fr.json").unlink()
        self.assertEqual(COMPAT.warning_text("launcher.unsupported_game", "fr"),
                         COMPAT.WARNING_FALLBACKS["launcher.invalid_package"])
        self.assertEqual(COMPAT.warning_text("launcher.blocked_title", "fr"),
                         COMPAT.WARNING_FALLBACKS["launcher.blocked_title"])
        (self.directory / "en.json").unlink()
        self.assertEqual(COMPAT.warning_text("launcher.wrong_framework", "en"),
                         COMPAT.WARNING_FALLBACKS["launcher.invalid_package"])

    def test_bad_fingerprints_placeholders_and_untranslated_text_are_refused(self):
        original = (self.directory / "fr.json").read_bytes()
        english = json.loads((self.directory / "en.json").read_text(encoding="utf-8"))
        for field, value in (("source_sha256", "0" * 64), ("text", "Bad {build.__class__}"),
                             ("text", "Bad {build!r}"), ("text", "Bad {build}{build}"),
                             ("text", "Bad\0text"), ("text", "x" * 1025),
                             ("text", english["messages"]["launcher.unsupported_game"]["text"])):
            with self.subTest(field=field, value=value):
                (self.directory / "fr.json").write_bytes(original)
                self.alter("fr", lambda data: data["messages"]["launcher.unsupported_game"].__setitem__(field, value))
                self.assertEqual(COMPAT.warning_text("launcher.unsupported_game", "fr"),
                                 COMPAT.WARNING_FALLBACKS["launcher.invalid_package"])

    def test_duplicate_oversized_bad_metadata_and_english_drift_fall_back(self):
        original = (self.directory / "en.json").read_bytes()
        for malformed in (b'{"schema_version":1,"schema_version":1}', b"x" * 65537,
                          b'{"messages":{}}', b'\xff'):
            with self.subTest(malformed=malformed[:20]):
                (self.directory / "en.json").write_bytes(malformed)
                self.assertEqual(COMPAT.warning_text("launcher.game_required", "en"),
                                 COMPAT.WARNING_FALLBACKS["launcher.invalid_package"])
        (self.directory / "en.json").write_bytes(original)
        self.alter("en", lambda data: data["messages"]["launcher.game_required"].__setitem__("text", "Changed text"))
        self.assertEqual(COMPAT.warning_text("launcher.game_required", "en"),
                         COMPAT.WARNING_FALLBACKS["launcher.invalid_package"])

    def test_explicit_fields_are_bounded_and_do_not_allow_format_traversal(self):
        self.assertIn("reviewed test build", COMPAT.warning_text("launcher.unsupported_game", "en", build="reviewed test build"))
        for fields in ({"build": "bad\0value"}, {"build": "x" * 257}, {"path": "unexpected"}, {"version": object()}):
            self.assertEqual(COMPAT.warning_text("launcher.unsupported_game", "en", **fields),
                             COMPAT.WARNING_FALLBACKS["launcher.invalid_package"])
        self.assertEqual(COMPAT.warning_text("unknown", "en"), COMPAT.WARNING_FALLBACKS["launcher.invalid_package"])

    def test_failure_is_stderr_plus_optional_mocked_host_dialog(self):
        error = COMPAT.CompatibilityError("launcher.unsupported_game")
        with patch.object(sys, "stderr", new_callable=io.StringIO) as output, \
                patch.object(COMPAT, "_message_box") as dialog:
            body = COMPAT.show_failure(error, "fr", show_dialog=False)
            self.assertIn(body, output.getvalue())
            dialog.assert_not_called()
            COMPAT.show_failure(error, "fr")
            dialog.assert_called_once_with(COMPAT.warning_text("launcher.blocked_title", "fr"), body)
        with patch.object(sys, "stderr", new_callable=io.StringIO), \
                patch.object(COMPAT, "_message_box", side_effect=OSError()):
            self.assertEqual(COMPAT.show_failure(ValueError("private"), "en"),
                             COMPAT.WARNING_FALLBACKS["launcher.invalid_package"])


class FakeProcesses:
    def __init__(self, names, *, error=18, close=True):
        self.names = iter(names)
        self.error, self.close = error, close
        self.closed = []

    def CreateToolhelp32Snapshot(self, flags, pid):
        assert (flags, pid) == (2, 0)
        return 123

    def Process32FirstW(self, handle, entry):
        return self.Process32NextW(handle, entry)

    def Process32NextW(self, handle, entry):
        assert handle == 123
        try:
            entry._obj.name = next(self.names)
            return True
        except StopIteration:
            return False

    def get_last_error(self):
        return self.error

    def CloseHandle(self, handle):
        self.closed.append(handle)
        return self.close


class ProcessSnapshotTests(unittest.TestCase):
    def test_owned_snapshot_copies_protected_names_and_closes_handle(self):
        api = FakeProcesses(["System", "Secure System", "owned.exe"])
        self.assertEqual(COMPAT._windows_process_names(api), ["System", "Secure System", "owned.exe"])
        self.assertEqual(api.closed, [123])

    def test_incomplete_empty_failed_cleanup_and_oversized_snapshot_refuse(self):
        for api in (FakeProcesses([]), FakeProcesses(["owned.exe"], error=5),
                    FakeProcesses(["owned.exe"], close=False), FakeProcesses(["owned.exe"] * 65537)):
            with self.subTest(api=api), self.assertRaises(COMPAT.CompatibilityError):
                COMPAT._windows_process_names(api)
            self.assertEqual(api.closed, [123])

    def test_running_or_unknown_process_state_is_not_closed(self):
        for names, closed in ((["System", "owned.exe"], True), (["NMS.exe"], False),
                              (["nMs.ExE"], False), ([""], False), ([], False), ([None], False)):
            with patch.object(COMPAT, "_windows_process_names", return_value=names):
                self.assertIs(COMPAT.game_closed(), closed)
        with patch.object(COMPAT, "_windows_process_names", side_effect=OSError()):
            self.assertIs(COMPAT.game_closed(), False)


if __name__ == "__main__":
    unittest.main()
