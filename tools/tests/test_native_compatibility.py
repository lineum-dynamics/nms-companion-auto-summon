from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.native_compatibility import load_native_profile
from tools.native_mapping import read_native_mappings


PROFILE = {
    "schema_version": 1,
    "runtime": "native",
    "steam_build": "25624745",
    "game_release": "Cosmos 7.05",
    "exe_sha256": "671de22649274b49fa07f5a246bc7252c4e08bb9ab623d2e65722fbab4e497a4",
}


class NativeCompatibilityTests(unittest.TestCase):
    def write(self, text: str) -> Path:
        self.temp = tempfile.TemporaryDirectory()
        path = Path(self.temp.name) / "profile.json"
        path.write_text(text, encoding="utf-8")
        self.addCleanup(self.temp.cleanup)
        return path

    def test_accepts_exact_cosmos_705_profile(self):
        self.assertEqual(load_native_profile(self.write(json.dumps(PROFILE))), PROFILE)

    def test_rejects_duplicate_keys(self):
        raw = json.dumps(PROFILE).replace('"runtime": "native"', '"runtime": "native", "runtime": "native"')
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            load_native_profile(self.write(raw))

    def test_rejects_extra_or_missing_fields(self):
        with self.assertRaisesRegex(ValueError, "schema"):
            load_native_profile(self.write(json.dumps(dict(PROFILE, unknown=True))))
        incomplete = dict(PROFILE)
        incomplete.pop("exe_sha256")
        with self.assertRaisesRegex(ValueError, "schema"):
            load_native_profile(self.write(json.dumps(incomplete)))

    def test_rejects_other_builds_and_malformed_hashes(self):
        with self.assertRaisesRegex(ValueError, "no exact game/build/hash mapping"):
            load_native_profile(self.write(json.dumps(dict(PROFILE, steam_build="25442159"))))
        with self.assertRaisesRegex(ValueError, "invalid values"):
            load_native_profile(self.write(json.dumps(dict(PROFILE, exe_sha256="0" * 63))))

    def test_rejects_well_formed_foreign_hash_with_supported_build_label(self):
        with self.assertRaisesRegex(ValueError, "no exact game/build/hash mapping"):
            load_native_profile(self.write(json.dumps(dict(PROFILE, exe_sha256="0" * 64))))

    def test_rejects_prepared_but_unapproved_706_profile(self):
        candidate = dict(PROFILE, steam_build="25732212", game_release="Cosmos 7.06",
                         exe_sha256="13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499")
        records = read_native_mappings()
        records["25732212"]["activation_approved"] = False
        with patch("tools.native_mapping.read_native_mappings", return_value=records):
            with self.assertRaisesRegex(ValueError, "not approved for activation"):
                load_native_profile(self.write(json.dumps(candidate)))

    def test_accepts_exact_706_candidate_profile(self):
        candidate = dict(PROFILE, steam_build="25732212", game_release="Cosmos 7.06",
                         exe_sha256="13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499")
        self.assertEqual(load_native_profile(self.write(json.dumps(candidate))), candidate)


if __name__ == "__main__":
    unittest.main()
