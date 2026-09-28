"""Original-icon validation and publication checks using temporary game roots."""

import importlib.util
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import Mock, patch


TOOLS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("quick_menu_assets_tested", TOOLS / "quick_menu_assets.py")
assets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assets)
ORIGINAL = (TOOLS.parent / "assets/ui/SETTINGS.DDS").read_bytes()


class IconAssetTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.bundle = self.root / "bundle"
        self.bundle.mkdir()
        (self.bundle / assets.ASSET_NAME).write_bytes(ORIGINAL)
        self.game = self.root / "game"
        (self.game / "Binaries").mkdir(parents=True)
        (self.game / "Binaries/NMS.exe").write_bytes(b"synthetic executable; never run")
        self.destination = self.game / assets.DESTINATION
        self.closed = Mock(return_value=True)

    def install(self):
        return assets.install_icon(self.bundle, self.game, self.closed)

    def prepare_destination(self, data=ORIGINAL):
        self.destination.parent.mkdir(parents=True, exist_ok=True)
        self.destination.write_bytes(data)

    def test_original_header_payload_and_hash(self):
        self.assertEqual(assets.validate_asset(ORIGINAL), assets.ASSET_SHA256)

    def prepare_icon_set(self):
        for name in assets.ASSET_HASHES:
            data = (TOOLS.parent / "assets/ui" / name).read_bytes()
            (self.bundle / name).write_bytes(data)

    def test_all_eight_original_assets_are_distinct_and_validated_by_name(self):
        self.assertEqual(tuple(assets.ASSET_HASHES), (
            "SETTINGS.DDS", "AUTOMATION.DDS", "SELECTION.DDS", "BIOME.DDS",
            "PLANET.DDS", "STATION.DDS", "ANOMALY.DDS", "ROTATE.DDS",
        ))
        self.assertEqual(len(set(assets.ASSET_HASHES.values())), 8)
        for name, expected in assets.ASSET_HASHES.items():
            data = (TOOLS.parent / "assets/ui" / name).read_bytes()
            self.assertEqual(assets.validate_asset(data, name), expected)
            if name != assets.ASSET_NAME:
                with self.assertRaises(assets.AssetError):
                    assets.validate_asset(data, assets.ASSET_NAME)
        for name in ("../SETTINGS.DDS", "settings.dds", "OTHER.DDS", None):
            with self.assertRaises(assets.AssetError):
                assets.validate_asset(ORIGINAL, name)

    def test_complete_set_installs_once_and_preserves_existing_main_icon(self):
        self.prepare_icon_set()
        self.prepare_destination()
        result = assets.install_icons(self.bundle, self.game, self.closed)
        self.assertEqual(len(result["files"]), 8)
        self.assertEqual(sum(entry["installed"] for entry in result["files"]), 7)
        self.assertEqual(self.destination.read_bytes(), ORIGINAL)
        with patch.object(assets.os, "link", side_effect=AssertionError("unexpected mutation")):
            self.assertTrue(assets.install_icons(self.bundle, self.game, self.closed)["reused"])

    def test_missing_late_source_prevents_all_set_mutation(self):
        self.prepare_icon_set()
        (self.bundle / "ROTATE.DDS").unlink()
        with self.assertRaises(assets.AssetError):
            assets.install_icons(self.bundle, self.game, self.closed)
        self.assertFalse((self.game / "GAMEDATA").exists())

    def test_unknown_late_destination_prevents_earlier_file_publication(self):
        self.prepare_icon_set()
        late = self.game / assets._destination("ROTATE.DDS")
        late.parent.mkdir(parents=True)
        late.write_bytes(b"user-owned content")
        with self.assertRaises(assets.AssetError):
            assets.install_icons(self.bundle, self.game, self.closed)
        self.assertEqual(list(late.parent.iterdir()), [late])
        self.assertEqual(late.read_bytes(), b"user-owned content")

    def test_wrong_size_type_signature_header_and_pixels_refused(self):
        invalid = [bytearray(ORIGINAL), ORIGINAL[:-1], ORIGINAL + b"x",
                   b"BAD " + ORIGINAL[4:]]
        for offset, value in ((12, 128), (16, 512), (28, 2), (80, 4),
                              (92, 0xFF0000), (104, 0), (112, 0x200), (32, 1)):
            data = bytearray(ORIGINAL)
            struct.pack_into("<I", data, offset, value)
            invalid.append(bytes(data))
        invalid.append(ORIGINAL[:-1] + bytes([ORIGINAL[-1] ^ 1]))
        for data in invalid:
            with self.subTest(kind=type(data), length=len(data)), self.assertRaises(assets.AssetError):
                assets.validate_asset(data)

    def test_stages_only_fixed_original_and_preserves_neighbor(self):
        neighbor = self.game / "Binaries/neighbor.txt"
        neighbor.write_bytes(b"keep")
        result = self.install()
        self.assertTrue(result["installed"])
        self.assertFalse(result["reused"])
        self.assertEqual(result["relative_path"], assets.DESTINATION)
        self.assertEqual(self.destination.read_bytes(), ORIGINAL)
        self.assertEqual(neighbor.read_bytes(), b"keep")
        self.assertEqual(list(self.destination.parent.iterdir()), [self.destination])
        self.assertNotIn(str(self.root), str(result))
        self.assertGreaterEqual(self.closed.call_count, 3)

    def test_identical_destination_reused_without_mutation(self):
        self.prepare_destination()
        with patch.object(assets.os, "link", side_effect=AssertionError("no publication")), \
                patch.object(assets.tempfile, "mkstemp", side_effect=AssertionError("no temporary")):
            self.assertTrue(self.install()["reused"])
        self.assertEqual(self.closed.call_count, 2)

    def test_unexpected_destination_preserved(self):
        for data in (b"user file", ORIGINAL[:-1] + b"x"):
            self.prepare_destination(data)
            with self.assertRaises(assets.AssetError):
                self.install()
            self.assertEqual(self.destination.read_bytes(), data)
            self.assertEqual(list(self.destination.parent.iterdir()), [self.destination])

    def test_running_unknown_or_failing_closed_check_prevents_mutation(self):
        for result in (False, None, 1):
            self.closed.return_value = result
            with self.subTest(result=result), self.assertRaises(assets.AssetError):
                self.install()
            self.assertFalse((self.game / "GAMEDATA").exists())
        self.closed.side_effect = RuntimeError("private process detail")
        with self.assertRaisesRegex(assets.AssetError, "game-closed check failed") as caught:
            self.install()
        self.assertNotIn("private", str(caught.exception))

    def test_invalid_source_prevents_directory_creation(self):
        (self.bundle / assets.ASSET_NAME).write_bytes(b"invalid")
        with self.assertRaises(assets.AssetError):
            self.install()
        self.assertFalse((self.game / "GAMEDATA").exists())

    def test_relative_dotdot_missing_game_and_file_directory_refused(self):
        with self.assertRaises(assets.AssetError):
            assets.install_icon(Path("bundle"), self.game, self.closed)
        with self.assertRaises(assets.AssetError):
            assets.install_icon(self.bundle, self.game / ".." / "game", self.closed)
        (self.game / "Binaries/NMS.exe").unlink()
        with self.assertRaises(assets.AssetError):
            self.install()
        (self.game / "Binaries/NMS.exe").write_bytes(b"fake")
        (self.game / "GAMEDATA").write_bytes(b"not a directory")
        with self.assertRaises(assets.AssetError):
            self.install()

    def test_symlink_source_and_destination_escape_refused(self):
        source = self.bundle / assets.ASSET_NAME
        self.prepare_destination()
        original_lstat = Path.lstat
        # Model the lstat result directly: creating real symlinks on Windows
        # requires privileges, whereas refusal must be tested everywhere.
        for link_path in (source, self.destination, self.root, self.game / "GAMEDATA"):
            def linked(path):
                info = original_lstat(path)
                if path == link_path:
                    return type("LinkStat", (), {"st_mode": assets.stat.S_IFLNK | 0o777,
                                                 "st_file_attributes": 0})()
                return info
            with self.subTest(path=link_path.name), patch.object(Path, "lstat", linked), \
                    self.assertRaises(assets.AssetError):
                self.install()
        self.assertEqual(source.read_bytes(), ORIGINAL)
        self.assertEqual(self.destination.read_bytes(), ORIGINAL)

    def test_windows_reparse_flag_rejected_even_without_symlink_mode(self):
        original_lstat = Path.lstat
        def tagged(path):
            info = original_lstat(path)
            if path == self.game:
                return type("ReparseStat", (), {"st_mode": info.st_mode,
                                                "st_file_attributes": 0x400})()
            return info
        with patch.object(Path, "lstat", tagged), self.assertRaises(assets.AssetError):
            self.install()
        self.assertFalse((self.game / "GAMEDATA").exists())

    def test_concurrent_unknown_destination_is_not_overwritten(self):
        original_link = os.link
        def race(source, destination, **kwargs):
            destination.write_bytes(b"concurrent user file")
            return original_link(source, destination, **kwargs)
        with patch.object(assets.os, "link", side_effect=race), self.assertRaises(assets.AssetError):
            self.install()
        self.assertEqual(self.destination.read_bytes(), b"concurrent user file")
        self.assertEqual(list(self.destination.parent.iterdir()), [self.destination])

    def test_concurrent_identical_destination_is_reused(self):
        original_link = os.link
        def race(source, destination, **kwargs):
            destination.write_bytes(ORIGINAL)
            return original_link(source, destination, **kwargs)
        with patch.object(assets.os, "link", side_effect=race):
            self.assertTrue(self.install()["reused"])

    def test_game_opening_before_publication_leaves_no_destination(self):
        self.destination.parent.mkdir(parents=True)
        self.closed.side_effect = [True, True, False]
        with self.assertRaises(assets.AssetError):
            self.install()
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.destination.parent.iterdir()), [])

    def test_final_closed_check_runs_after_destination_readback(self):
        def closed():
            if self.destination.exists():
                self.assertEqual(self.destination.read_bytes(), ORIGINAL)
                return False
            return True
        self.closed.side_effect = closed
        with self.assertRaises(assets.AssetError):
            self.install()
        self.assertEqual(self.destination.read_bytes(), ORIGINAL)
        self.assertEqual(list(self.destination.parent.iterdir()), [self.destination])

    def test_failed_publication_never_uses_replace_and_cleans_temporary(self):
        with patch.object(assets.os, "link", side_effect=OSError("unsupported")), \
                patch.object(assets.os, "replace", side_effect=AssertionError("must not replace")), \
                self.assertRaises(assets.AssetError):
            self.install()
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.destination.parent.iterdir()), [])

    def test_path_permission_errors_are_bounded_and_do_not_leak_paths(self):
        with patch.object(Path, "lstat", side_effect=PermissionError(str(self.root))), \
                self.assertRaises(assets.AssetError) as caught:
            self.install()
        self.assertNotIn(str(self.root), str(caught.exception))
        self.assertFalse((self.game / "GAMEDATA").exists())

    def test_game_opening_before_first_directory_prevents_creation(self):
        self.closed.side_effect = [True, False]
        with self.assertRaises(assets.AssetError):
            self.install()
        self.assertFalse((self.game / "GAMEDATA").exists())

    def test_existing_same_bytes_still_checks_closed_after_readback(self):
        self.prepare_destination()
        self.closed.side_effect = [True, False]
        with self.assertRaises(assets.AssetError):
            self.install()
        self.assertEqual(self.closed.call_count, 2)
        self.assertEqual(self.destination.read_bytes(), ORIGINAL)


if __name__ == "__main__":
    unittest.main()
