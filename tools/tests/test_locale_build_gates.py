"""Ensure incomplete locales cannot generate or replace release outputs."""

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_tool(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LocaleBuildGateTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        shutil.copytree(ROOT / "locales", self.root / "locales")
        catalog_path = self.root / "locales/fr.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        del catalog["messages"]["menu.biome"]
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

    def test_standalone_build_preserves_generated_source_when_translation_is_missing(self):
        module = load_tool("cas_locale_build_gate", "build.py")
        target = self.root / "CompanionAutoSummon.py"
        target.write_bytes(b"preserve existing generated source")
        with patch.object(module, "ROOT", self.root):
            with self.assertRaisesRegex(ValueError, "Missing or extra fr message keys"):
                module.build()
        self.assertEqual(target.read_bytes(), b"preserve existing generated source")

    def test_release_package_stops_before_reading_manifest_or_creating_archive(self):
        module = load_tool("cas_locale_package_gate", "tools/package.py")
        with patch.object(module, "ROOT", self.root):
            with self.assertRaisesRegex(ValueError, "Missing or extra fr message keys"):
                module.main()
        self.assertFalse((self.root / "dist").exists())
        self.assertFalse((self.root / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
