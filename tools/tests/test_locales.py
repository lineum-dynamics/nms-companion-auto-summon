"""Scoped catalog and source-drift checks using only temporary authored files."""

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("cas_validate_locales", ROOT / "tools/validate_locales.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class LocaleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cas-locale-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        shutil.copytree(ROOT / "locales", self.root / "locales")
        for name in ("tools/quick_menu_toggle.py", "tools/quick_menu_item.py", "src/runtime.py"):
            target = self.root / name
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def read(self, code):
        return json.loads((self.root / "locales" / (code + ".json")).read_text(encoding="utf-8"))

    def write(self, code, value):
        (self.root / "locales" / (code + ".json")).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def validate(self):
        return VALIDATOR.validate(source_root=self.root)

    def test_fourteen_complete_drafts_match_actual_english_without_modifying_files(self):
        before = {str(path): hashlib.sha256(path.read_bytes()).digest()
                  for path in self.root.rglob("*") if path.is_file()}
        report = self.validate()
        self.assertEqual(report["locales"], 14)
        self.assertEqual(report["keys_per_locale"], 30)
        self.assertEqual(report["scope"], "native_menu_hud_technology")
        self.assertEqual(report["translated_drafts"], 13)
        self.assertTrue(report["source_text_verified"])
        self.assertFalse(report["native_runtime_integrated"])
        self.assertFalse(report["language_review_verified"])
        self.assertEqual(before, {str(path): hashlib.sha256(path.read_bytes()).digest()
                                  for path in self.root.rglob("*") if path.is_file()})

    def test_technology_keys_are_six_distinct_catalog_inputs_with_draft_translations(self):
        self.assertEqual(VALIDATOR.TECHNOLOGY_KEYS,
                         ("tech.link.name", "tech.link.subtitle", "tech.link.description",
                          "tech.recharger.name", "tech.recharger.subtitle", "tech.recharger.description"))
        english = self.read("en")["messages"]
        for code in VALIDATOR.LOCALES:
            catalog = self.read(code)
            for key in VALIDATOR.TECHNOLOGY_KEYS:
                entry = catalog["messages"][key]
                with self.subTest(code=code, key=key):
                    self.assertEqual(entry["source_sha256"],
                                     VALIDATOR.source_fingerprint(english[key]["text"]))
                    self.assertNotIn(key, catalog["unchanged_keys"])
                    if code != "en":
                        self.assertEqual(catalog["review_status"], "draft_unreviewed")
                        self.assertNotEqual(entry["text"], english[key]["text"])
        self.validate()

    def test_technology_meaning_change_requires_updated_translation_fingerprints(self):
        english = self.read("en")
        entry = english["messages"]["tech.recharger.description"]
        entry["text"] += " Changed battery requirement."
        entry["source_sha256"] = VALIDATOR.source_fingerprint(entry["text"])
        self.write("en", english)
        with self.assertRaisesRegex(VALIDATOR.CatalogError,
                                    "Stale source fingerprint: fr:tech.recharger.description"):
            self.validate()

    def test_missing_technology_or_copied_english_technology_is_rejected(self):
        original = self.read("fr")
        catalog = json.loads(json.dumps(original))
        del catalog["messages"]["tech.link.description"]
        self.write("fr", catalog)
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "message keys"):
            self.validate()
        catalog = json.loads(json.dumps(original))
        catalog["messages"]["tech.link.name"]["text"] = self.read("en")["messages"]["tech.link.name"]["text"]
        self.write("fr", catalog)
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "Untranslated English"):
            self.validate()

    def test_changed_english_invalidates_every_unupdated_translation(self):
        english = self.read("en")
        entry = english["messages"]["menu.automation"]
        entry["text"] += " changed"
        entry["source_sha256"] = VALIDATOR.source_fingerprint(entry["text"])
        self.write("en", english)
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "Stale source fingerprint: fr"):
            self.validate()

    def test_translation_fingerprint_is_key_specific(self):
        catalog = self.read("de")
        catalog["messages"]["menu.biome"]["source_sha256"] = catalog["messages"]["menu.planets"]["source_sha256"]
        self.write("de", catalog)
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "Stale source fingerprint: de:menu.biome"):
            self.validate()

    def test_missing_extra_and_duplicate_keys_are_rejected(self):
        original = self.read("fr")
        for action in ("missing", "extra"):
            catalog = json.loads(json.dumps(original))
            if action == "missing":
                del catalog["messages"]["menu.biome"]
            else:
                catalog["messages"]["unknown"] = catalog["messages"]["menu.biome"]
            self.write("fr", catalog)
            with self.subTest(action=action), self.assertRaises(VALIDATOR.CatalogError):
                self.validate()
        self.write("fr", original)
        path = self.root / "locales/fr.json"
        text = path.read_text(encoding="utf-8").replace('"schema_version": 1,', '"schema_version": 1, "schema_version": 1,', 1)
        path.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "Duplicate JSON key"):
            self.validate()

    def test_missing_or_extra_locale_file_is_rejected(self):
        path = self.root / "locales/fr.json"
        data = path.read_bytes()
        path.unlink()
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "fourteen"):
            self.validate()
        path.write_bytes(data)
        (self.root / "locales/unknown.json").write_bytes(data)
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "fourteen"):
            self.validate()

    def test_placeholder_names_counts_and_unsafe_expressions_are_rejected(self):
        original = self.read("fr")
        for value in ("{label}: {wrong}", "{label}: {value} {value}", "{label}: {value!r}",
                      "{label}: {value:>20}", "{label}: {value.name}", "{label}: {value[0]}",
                      "{label}: {}", "{label}: {value"):
            catalog = json.loads(json.dumps(original))
            catalog["messages"]["format.setting"]["text"] = value
            self.write("fr", catalog)
            with self.subTest(value=value), self.assertRaises(VALIDATOR.CatalogError):
                self.validate()

    def test_empty_nul_controls_surrogates_and_oversized_text_are_rejected(self):
        original = self.read("ja")
        for value in ("", " ", "bad\0value", "bad\nvalue", "x" * 1025, "界" * 342):
            catalog = json.loads(json.dumps(original))
            catalog["messages"]["menu.biome"]["text"] = value
            self.write("ja", catalog)
            with self.subTest(value=repr(value[:10])), self.assertRaises(VALIDATOR.CatalogError):
                self.validate()
        catalog["messages"]["menu.biome"]["text"] = "\ud800"
        (self.root / "locales/ja.json").write_text(json.dumps(catalog), encoding="utf-8")
        with self.assertRaises(VALIDATOR.CatalogError):
            self.validate()

    def test_english_placeholder_copy_cannot_be_declared_translated(self):
        catalog = self.read("fr")
        catalog["messages"]["menu.biome"]["text"] = self.read("en")["messages"]["menu.biome"]["text"]
        self.write("fr", catalog)
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "Untranslated English"):
            self.validate()
        catalog["unchanged_keys"].append("menu.biome")
        self.write("fr", catalog)
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "unchanged-key"):
            self.validate()

    def test_brand_and_format_identity_must_be_explicitly_declared(self):
        catalog = self.read("fr")
        catalog["unchanged_keys"].remove("menu.parent_title")
        self.write("fr", catalog)
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "unchanged-key"):
            self.validate()

    def test_false_review_or_runtime_integration_claim_is_rejected(self):
        original = self.read("fr")
        for key, value in (("review_status", "reviewed"), ("native_runtime_integrated", True),
                           ("locale", "en"), ("schema_version", True), ("scope", "entire_application")):
            catalog = dict(original, **{key: value})
            self.write("fr", catalog)
            with self.subTest(key=key), self.assertRaises(VALIDATOR.CatalogError):
                self.validate()

    def test_source_label_and_parent_changes_fail_without_catalog_update(self):
        for name, old, new in (("tools/quick_menu_toggle.py", "Random: prefer matching biome", "Biome"),
                               ("tools/quick_menu_item.py", 'DEFAULT_LABEL = "Companion Auto Summon"',
                                'DEFAULT_LABEL = "Changed title"')):
            path = self.root / name
            original = path.read_text(encoding="utf-8")
            path.write_text(original.replace(old, new, 1), encoding="utf-8")
            with self.subTest(name=name), self.assertRaises(VALIDATOR.CatalogError):
                self.validate()
            path.write_text(original, encoding="utf-8")

    def test_source_dynamic_caption_changes_fail_without_catalog_update(self):
        path = self.root / "tools/quick_menu_toggle.py"
        original = path.read_text(encoding="utf-8")
        for old, new in (('" (pending)"', '" (queued)"'), ('": "', '" - "'),
                         ('"Last selected"', '"Favourite"')):
            path.write_text(original.replace(old, new, 1), encoding="utf-8")
            with self.subTest(old=old), self.assertRaises(VALIDATOR.CatalogError):
                self.validate()
        path.write_text(original, encoding="utf-8")

    def test_source_hud_changes_fail_without_catalog_update(self):
        path = self.root / "src/runtime.py"
        original = path.read_text(encoding="utf-8")
        for old, new in (("Companion saved.", "Saved."), (" Random stays ON.", " Random remains ON."),
                         ("settings updated{suffix}", "preferences changed{suffix}")):
            path.write_text(original.replace(old, new, 1), encoding="utf-8")
            with self.subTest(old=old), self.assertRaises(VALIDATOR.CatalogError):
                self.validate()
        path.write_text(original.replace("self.pending_notice = None", 'self.pending_notice = "New untracked notice"', 1), encoding="utf-8")
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "outside the catalog"):
            self.validate()

    def test_source_checker_never_imports_runtime_or_executes_new_calls(self):
        runtime = self.root / "src/runtime.py"
        runtime.write_text('raise AssertionError("Runtime must never import")\n' + runtime.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertTrue(self.validate()["source_text_verified"])
        menu = self.root / "tools/quick_menu_toggle.py"
        text = menu.read_text(encoding="utf-8").replace("    setting_key(role)", '    forbidden_game_call()\n    setting_key(role)', 1)
        menu.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(VALIDATOR.CatalogError, "Unexpected operation"):
            self.validate()

    def test_cli_supports_explicit_source_and_catalog_paths(self):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "tools/validate_locales.py"),
                                 "--source-root", str(self.root), "--locales-dir", str(self.root / "locales")],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["locales"], 14)


if __name__ == "__main__":
    unittest.main()
