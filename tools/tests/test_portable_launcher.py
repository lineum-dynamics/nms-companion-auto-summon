"""Portable startup integrity, backup and Steam selection without game access."""

import hashlib
from importlib import util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


SPEC = util.spec_from_file_location("cas_portable_launcher_tests", Path(__file__).resolve().parents[1] / "portable_launcher.py")
portable = util.module_from_spec(SPEC)
SPEC.loader.exec_module(portable)


class PortableLaunchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def package(self):
        names = ("runtime/python.exe", "runtime/pythonw.exe", "app/portable_launcher.py",
                 "mod/manifest.json", "mod/Launch-CompanionAutoSummon-PlayTrial.py", "mod/cas_compatibility.py")
        files = []
        for name in names:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(name.encode())
            files.append({"path": name, "sha256": portable.digest(path)})
        manifest = {"schema_version": 1, "version": "0.9.3-test", "files": files}
        (self.root / "portable-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return manifest

    def test_missing_or_changed_payload_refuses_before_module_import(self):
        self.package()
        portable.validate_distribution(self.root)
        (self.root / "runtime/python.exe").write_bytes(b"changed")
        with patch.object(portable, "load_module", side_effect=AssertionError("Do not import corrupt payload")), patch("sys.stderr"):
            self.assertEqual(portable.main(["--check-only", "--no-dialog"], self.root), 1)

    def test_added_runtime_code_is_refused(self):
        self.package()
        (self.root / "runtime/sitecustomize.py").write_text("raise RuntimeError()")
        with self.assertRaisesRegex(ValueError, "Unlisted"):
            portable.validate_distribution(self.root)

    def test_case_duplicate_and_traversal_paths_are_refused(self):
        for bad in ("RUNTIME/python.exe", "../outside", "runtime/../mod/manifest.json", "/absolute", "runtime/x:ads", "runtime//python.exe"):
            with self.subTest(path=bad):
                manifest = self.package()
                manifest["files"].append({"path": bad, "sha256": "0" * 64})
                (self.root / "portable-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaises((ValueError, FileNotFoundError)):
                    portable.validate_distribution(self.root)

    def test_reparse_payload_is_refused(self):
        self.package()
        path = self.root / "runtime/python.exe"
        real_lstat = Path.lstat
        def lstat(target, *args, **kwargs):
            if target == path:
                return SimpleNamespace(st_file_attributes=0x400, st_mode=0o100644)
            return real_lstat(target, *args, **kwargs)
        with patch.object(Path, "lstat", lstat), self.assertRaisesRegex(ValueError, "Reparse"):
            portable.validate_distribution(self.root)

    def test_verified_backup_preserves_save_and_preferences(self):
        save = self.root / "save"
        prefs = self.root / "prefs"
        save.mkdir(); prefs.mkdir()
        (save / "save.hg").write_bytes(b"original save")
        (prefs / "settings.json").write_text('{"enabled":false}')
        destination = self.root / "backup"
        portable.backup_profiles(save, prefs, destination, lambda: True)
        record = json.loads((destination / "backup-manifest.json").read_text())
        self.assertTrue(record["verified"])
        self.assertEqual(len(record["files"]), 2)
        self.assertEqual((destination / "saves/save.hg").read_bytes(), b"original save")
        self.assertEqual((save / "save.hg").read_bytes(), b"original save")
        self.assertFalse((destination / "INCOMPLETE").exists())

    def test_game_started_during_backup_prevents_verified_marker(self):
        save = self.root / "save"; save.mkdir()
        (save / "save.hg").write_bytes(b"save")
        destination = self.root / "backup"
        with self.assertRaises(portable.PortableError):
            portable.backup_profiles(save, self.root / "prefs", destination, Mock(side_effect=[True, False]))
        self.assertFalse((destination / "backup-manifest.json").exists())
        self.assertTrue((destination / "INCOMPLETE").exists())

    def test_source_change_during_copy_keeps_incomplete_backup(self):
        save = self.root / "save"; save.mkdir()
        source = save / "save.hg"; source.write_bytes(b"before")
        real_copy = portable.shutil.copyfileobj
        def changed_copy(incoming, outgoing):
            real_copy(incoming, outgoing)
            source.write_bytes(b"after")
        with patch.object(portable.shutil, "copyfileobj", changed_copy), self.assertRaises(portable.PortableError):
            portable.backup_profiles(save, self.root / "prefs", self.root / "backup", lambda: True)
        self.assertFalse((self.root / "backup/backup-manifest.json").exists())

    def test_existing_backup_is_never_overwritten(self):
        existing = self.root / "backup"; existing.mkdir()
        marker = existing / "keep"; marker.write_text("original")
        with self.assertRaises(FileExistsError):
            portable.backup_profiles(self.root / "save", self.root / "prefs", existing, lambda: True)
        self.assertEqual(marker.read_text(), "original")

    def test_empty_profile_is_valid_but_not_invented(self):
        portable.backup_profiles(self.root / "no-save", self.root / "no-prefs", self.root / "backup", lambda: True)
        record = json.loads((self.root / "backup/backup-manifest.json").read_text())
        self.assertEqual(record["files"], [])

    def test_session_staging_only_copies_manifest_allowlist(self):
        source = self.root / "mod"; source.mkdir()
        (source / "owned.py").write_bytes(b"verified")
        (source / "unlisted.py").write_bytes(b"never copy")
        manifest = {"files": [{"path": "owned.py", "sha256": portable.digest(source / "owned.py")}]}
        (source / "manifest.json").write_text(json.dumps(manifest))
        target = portable.stage_mod(source, self.root / "session/mod")
        self.assertEqual({p.name for p in target.iterdir()}, {"owned.py", "manifest.json"})
        self.assertEqual((target / "owned.py").read_bytes(), b"verified")
        self.assertTrue((source / "unlisted.py").exists())

    def test_changed_mod_is_not_staged_as_valid(self):
        source = self.root / "mod"; source.mkdir()
        (source / "owned.py").write_bytes(b"changed")
        (source / "manifest.json").write_text(json.dumps({"files": [{"path": "owned.py", "sha256": "0" * 64}]}))
        with self.assertRaises(portable.PortableError):
            portable.stage_mod(source, self.root / "session/mod")
        self.assertFalse((self.root / "session/mod/manifest.json").exists())

    def steam_library(self, root, appid="275850", installdir="No Man's Sky"):
        game = root / "steamapps/common" / installdir
        (game / "Binaries").mkdir(parents=True)
        (game / "Binaries/NMS.exe").write_bytes(b"fake test game")
        (root / "steamapps/appmanifest_275850.acf").write_text(f'"appid" "{appid}"\n"installdir" "{installdir}"', encoding="utf-8")
        return game

    def test_steam_discovery_uses_linked_library_and_unicode(self):
        primary = self.root / "steam"
        extra = self.root / "K\u00e1\u0165a games"
        (primary / "steamapps").mkdir(parents=True)
        game = self.steam_library(extra)
        vdf_path = str(extra).replace("\\", "\\\\")
        (primary / "steamapps/libraryfolders.vdf").write_text(f'"1" {{ "path" "{vdf_path}" }}', encoding="utf-8")
        self.assertEqual(portable.discover_games([primary]), [game.resolve()])

    def test_wrong_app_manifest_cannot_select_game(self):
        self.steam_library(self.root, appid="other")
        self.assertEqual(portable.discover_games([self.root]), [])

    def test_multiple_verified_games_require_explicit_choice(self):
        first = self.steam_library(self.root / "a")
        second = self.steam_library(self.root / "b")
        compatibility = SimpleNamespace(verify_game_directory=lambda p: p / "Binaries/NMS.exe", CompatibilityError=RuntimeError)
        with self.assertRaises(portable.PortableError) as result:
            portable.select_game(None, compatibility, [self.root / "a", self.root / "b"])
        self.assertEqual(result.exception.key, "portable.game_choice_required")
        self.assertEqual(portable.select_game(second, compatibility), second)

    def test_check_only_does_not_backup_prepare_host_or_launch(self):
        self.package()
        args = SimpleNamespace(game_directory=None, language=None, check_only=True, no_dialog=True)
        compatibility = SimpleNamespace(verify_framework=Mock())
        host = SimpleNamespace(validate_bundle=Mock(), _load_bootstrap=Mock(side_effect=AssertionError("No launch")))
        support = SimpleNamespace(verify_runtime=Mock(), prepare_host=Mock(side_effect=AssertionError("No native adapter")))
        with patch.object(portable, "load_module", side_effect=[compatibility, host, support]), \
                patch.object(portable, "select_game", return_value=self.root), \
                patch.object(portable, "backup_profiles", side_effect=AssertionError("No backup")), \
                patch.object(portable, "portable_text", return_value="check passed"), patch("builtins.print"):
            self.assertEqual(portable.run(self.root, args), 0)
        support.verify_runtime.assert_called_once()
        host._load_bootstrap.assert_not_called()

    def test_closed_steam_stops_before_backup_or_session(self):
        self.package()
        args = SimpleNamespace(game_directory=None, language=None, check_only=False, no_dialog=True)
        compatibility = SimpleNamespace(verify_framework=Mock(), game_closed=lambda: True,
                                        _windows_process_names=lambda: ["explorer.exe"])
        host = SimpleNamespace(validate_bundle=Mock(), _load_bootstrap=Mock())
        support = SimpleNamespace(verify_runtime=Mock())
        with patch.object(portable, "load_module", side_effect=[compatibility, host, support]), \
                patch.object(portable, "select_game", return_value=self.root), \
                patch.object(portable, "backup_profiles", side_effect=AssertionError("No backup")), \
                self.assertRaises(portable.PortableError) as result:
            portable.run(self.root, args)
        self.assertEqual(result.exception.key, "portable.steam_required")
        host._load_bootstrap.assert_not_called()

    def test_failed_process_enumeration_has_steam_readiness_message(self):
        compatibility = SimpleNamespace(_windows_process_names=Mock(side_effect=OSError("snapshot failed")))
        with self.assertRaises(portable.PortableError) as result:
            portable.require_steam(compatibility)
        self.assertEqual(result.exception.key, "portable.steam_required")

    def test_emergency_text_matches_canonical_catalog(self):
        messages = json.loads((Path(__file__).resolve().parents[2] / "locales/en.json").read_text(encoding="utf-8"))["messages"]
        self.assertEqual(portable.PACKAGE_FAILURE_TITLE, messages["launcher.blocked_title"]["text"])
        self.assertEqual(portable.PACKAGE_FAILURE_BODY, messages["launcher.invalid_package"]["text"])


if __name__ == "__main__":
    unittest.main()
