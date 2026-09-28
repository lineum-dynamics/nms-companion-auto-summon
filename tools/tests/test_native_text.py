"""Offline text/state regression coverage; no game or player data access."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
import itertools
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import native_text as nt
import quick_menu_toggle as existing
from validate_locales import CatalogError, LOCALES, validated_catalogs


def states(key):
    yield None
    values = ("last_manual", "random") if key == "selection_mode" else (False, True)
    for value, pending, saved, stopped in itertools.product(values, (False, True), (False, True), (False, True)):
        yield nt.MenuTextState(value, pending=pending, settings_ok=saved, stopped=stopped)


class NativeTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogs = validated_catalogs(source_root=ROOT)
        cls.text = nt.NativeText(source_root=ROOT)

    def modified_catalog(self, language, change):
        temporary = tempfile.TemporaryDirectory(prefix="cas-native-text-")
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name) / "locales"
        shutil.copytree(ROOT / "locales", directory)
        path = directory / (language + ".json")
        catalog = deepcopy(self.catalogs[language])
        change(catalog)
        path.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
        return directory

    def test_english_menu_equivalence_for_all_current_preference_states(self):
        for role, key in enumerate(existing.SETTING_KEYS):
            for state in states(key):
                with self.subTest(role=role, state=state):
                    original = None if state is None else SimpleNamespace(**vars(state))
                    message = self.text.setting(key, state)
                    self.assertEqual(message.payload, existing.preference_label(role, original))
                    self.assertEqual(message.locale, "en")
                    self.assertIsNone(message.fallback_reason)

    def test_all_locales_menu_states_preserve_full_text_or_report_english_fallback(self):
        for locale, key in itertools.product(LOCALES, existing.SETTING_KEYS):
            for state in states(key):
                with self.subTest(locale=locale, key=key, state=state):
                    message = self.text.setting(key, state, locale)
                    self.assertEqual(message.payload.decode("utf-8"), message.text)
                    self.assertLessEqual(len(message.payload), nt.MENU_BYTES)
                    if message.fallback_reason:
                        self.assertEqual(message.fallback_reason, "byte_limit")
                        self.assertEqual(message.locale, "en")
                        self.assertEqual(message.text, self.text.setting(key, state).text)
                    else:
                        self.assertEqual(message.locale, locale)

    def test_parent_uses_catalog_and_fits_every_locale(self):
        for locale in LOCALES:
            message = self.text.parent(locale)
            self.assertEqual(message.text, self.catalogs[locale]["messages"]["menu.parent_title"]["text"])
            self.assertLessEqual(len(message.payload), nt.MENU_BYTES)
            self.assertIsNone(message.fallback_reason)

    def test_settings_notices_match_catalog_semantics_in_all_languages(self):
        for locale, enabled, saved, changed in itertools.product(LOCALES, (False, True), (False, True), (False, True)):
            text = {key: entry["text"] for key, entry in self.catalogs[locale]["messages"].items()}
            expected = text["hud.automation_state" if changed else "hud.settings_updated"].format(
                state=text["value.on" if enabled else "value.off"], suffix="" if saved else text["hud.session_suffix"])
            message = self.text.settings_notice(enabled=enabled, saved=saved, enabled_changed=changed, locale=locale)
            self.assertEqual(message.text, expected)
            self.assertEqual(message.payload.decode("utf-8"), expected)
            self.assertLessEqual(len(message.payload), nt.HUD_BYTES)
            self.assertIsNone(message.fallback_reason)

    def test_manual_notices_preserve_saved_session_off_random_distinctions(self):
        for locale, enabled, saved, mode in itertools.product(LOCALES, (False, True), (False, True), ("last_manual", "random")):
            text = {key: entry["text"] for key, entry in self.catalogs[locale]["messages"].items()}
            expected = text["hud.companion_saved" if saved else "hud.companion_session"]
            if not enabled:
                expected += text["hud.auto_off_suffix"]
            elif mode == "random":
                expected += text["hud.random_on_suffix"]
            message = self.text.companion_notice(enabled=enabled, saved=saved, selection_mode=mode, locale=locale)
            self.assertEqual(message.text, expected)
            self.assertLessEqual(len(message.payload), nt.HUD_BYTES)
            self.assertIsNone(message.fallback_reason)

    def test_unknown_locale_does_not_guess_game_language_or_interpret_a_path(self):
        for locale in (None, "cs", "fr-FR", "../fr", "../../settings", "", [], 1):
            message = self.text.setting("enabled", nt.MenuTextState(False), locale)
            self.assertEqual(message.payload, self.text.setting("enabled", nt.MenuTextState(False)).payload)
            self.assertEqual(message.locale, "en")
            self.assertEqual(message.fallback_reason, "unsupported_locale")

    def test_long_translation_falls_back_as_a_whole_without_losing_state(self):
        directory = self.modified_catalog("ja", lambda data: data["messages"]["menu.biome"].update(text="\u754c" * 50))
        text = nt.NativeText(locales_dir=directory, source_root=ROOT)
        state = nt.MenuTextState(False, settings_ok=False)
        message = text.setting("prefer_same_biome", state, "ja")
        self.assertEqual(message.payload, text.setting("prefer_same_biome", state, "en").payload)
        self.assertEqual(message.locale, "en")
        self.assertEqual(message.fallback_reason, "byte_limit")

    def test_unicode_limits_count_bytes_and_never_split_a_character(self):
        for glyph, fitting, oversized in (("\u00e9", 63, 64), ("\u754c", 42, 43), ("\U0001f43e", 31, 32)):
            self.assertEqual(nt.encode_payload(glyph * fitting, 127).decode("utf-8"), glyph * fitting)
            with self.assertRaises(nt.TextTooLong):
                nt.encode_payload(glyph * oversized, 127)
        self.assertEqual(len(nt.encode_payload("x" * 127, 127)), 127)
        self.assertEqual(len(nt.encode_payload("x" * 511, 511)), 511)
        with self.assertRaises(nt.TextTooLong):
            nt.encode_payload("x" * 512, 511)

    def test_invalid_unicode_controls_and_bounds_are_rejected(self):
        for text in ("", "  ", "a\0b", "a\nb", "a\x7fb", "\ud800", b"text", None):
            with self.subTest(text=repr(text)), self.assertRaises(nt.TextError):
                nt.encode_payload(text, 127)
        for limit in (0, -1, True, 512, "127"):
            with self.assertRaises(nt.TextError):
                nt.encode_payload("text", limit)

    def test_invalid_display_state_cannot_be_rendered_as_a_valid_preference(self):
        for key, state in (("bad", None), (0, None), ("enabled", SimpleNamespace(desired=True)),
                           ("enabled", nt.MenuTextState("random")), ("selection_mode", nt.MenuTextState(True))):
            with self.assertRaises(nt.TextError):
                self.text.setting(key, state)
        for value in (1, "yes", None):
            with self.assertRaises(nt.TextError):
                nt.MenuTextState(True, pending=value)
        with self.assertRaises(nt.TextError):
            self.text.settings_notice(enabled=1, saved=True, enabled_changed=True)
        with self.assertRaises(nt.TextError):
            self.text.companion_notice(saved=True, enabled=True, selection_mode="translated value")

    def test_stale_translation_fingerprint_is_rejected_before_preparation(self):
        directory = self.modified_catalog("fr", lambda data: data["messages"]["menu.automation"].update(source_sha256="0" * 64))
        with self.assertRaises(CatalogError):
            nt.NativeText(locales_dir=directory, source_root=ROOT)

    def test_unsafe_placeholder_is_rejected_before_preparation(self):
        directory = self.modified_catalog("fr", lambda data: data["messages"]["format.setting"].update(text="{label.__class__}: {value}"))
        with self.assertRaises(CatalogError):
            nt.NativeText(locales_dir=directory, source_root=ROOT)

    def test_missing_catalog_is_rejected_without_partial_translation(self):
        directory = self.modified_catalog("fr", lambda data: None)
        (directory / "fr.json").unlink()
        with self.assertRaises(CatalogError):
            nt.NativeText(locales_dir=directory, source_root=ROOT)

    def test_prepared_snapshot_does_not_reopen_changed_files(self):
        directory = self.modified_catalog("fr", lambda data: None)
        text = nt.NativeText(locales_dir=directory, source_root=ROOT)
        before = text.setting("enabled", nt.MenuTextState(False), "fr")
        (directory / "fr.json").write_text("corrupt", encoding="utf-8")
        with patch.object(Path, "read_bytes", side_effect=AssertionError("Render attempted file access")):
            self.assertEqual(text.setting("enabled", nt.MenuTextState(False), "fr"), before)
            text.companion_notice(saved=False, enabled=False, selection_mode="random", locale="ja")

    def test_prepared_data_and_messages_have_no_mutable_catalog_alias(self):
        owned = deepcopy(self.catalogs)
        with patch.object(nt, "validated_catalogs", return_value=owned):
            text = nt.NativeText()
        before = text.parent()
        owned["en"]["messages"]["menu.parent_title"]["text"] = "changed"
        self.assertEqual(text.parent(), before)
        with self.assertRaises(TypeError):
            text._catalogs["en"]["menu.parent_title"] = "changed"
        with self.assertRaises(FrozenInstanceError):
            before.text = "changed"


if __name__ == "__main__":
    unittest.main()
