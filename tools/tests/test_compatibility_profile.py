"""Exact-build declaration checks against owned files, without runtime imports."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("cas_profile_validator", ROOT / "tools/validate_compatibility.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class CompatibilityProfileTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cas-profile-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.profile = {"schema_version": 1, "steam_build": "12345678", "game_release": "Owned test release",
                        "exe_sha256": "a" * 64, "framework_version": "0.2.4"}
        self.manifest = {"steam_build": self.profile["steam_build"],
                         "supported_nms_exe_sha256": self.profile["exe_sha256"],
                         "framework": "pymhf[gui]==0.2.4"}
        self.write_json("compatibility.json", self.profile)
        self.write_json("manifest.json", self.manifest)
        self.host = {constant: self.profile[field] for field, constant in VALIDATOR.CONSTANTS.items()}
        self.write_constants("cas_compatibility.py", self.host)
        self.native = {"EXPECTED_EXE_SHA256": self.profile["exe_sha256"], "EXPECTED_PYMHF": "0.2.4"}
        self.write_constants("src/runtime.py", self.native)
        self.write_constants("CompanionAutoSummon.py", self.native)
        for name in VALIDATOR.DEVELOPER_SOURCES:
            constant = "TARGET_SHA256" if name.endswith("build_companion_technology.py") else "EXPECTED_EXE_SHA256"
            self.write_constants(name, {constant: self.profile["exe_sha256"]})

    def write_json(self, name, data):
        (self.root / name).write_text(json.dumps(data), encoding="utf-8")

    def write_constants(self, name, constants):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("raise AssertionError('Source must never be imported')\n" +
                        "\n".join(f"{key} = {value!r}" for key, value in constants.items()) + "\n",
                        encoding="utf-8")

    def validate(self, **options):
        return VALIDATOR.validate(self.root, **options)

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def test_matching_default_and_complete_profiles_are_read_only_and_never_import_sources(self):
        before = self.snapshot()
        ordinary = self.validate()
        self.assertEqual(ordinary["native_sources_checked"], 1)
        self.assertFalse(ordinary["generated_source_checked"])
        self.assertFalse(ordinary["developer_sources_checked"])
        complete = self.validate(developer=True, generated=True)
        self.assertTrue(complete["all_declarations_match"])
        self.assertEqual(complete["native_sources_checked"], 2 + len(VALIDATOR.DEVELOPER_SOURCES))
        self.assertTrue(complete["generated_source_checked"])
        self.assertTrue(complete["developer_sources_checked"])
        self.assertEqual(before, self.snapshot())

    def test_every_host_pin_must_match_the_profile(self):
        for field, constant in VALIDATOR.CONSTANTS.items():
            with self.subTest(field=field):
                changed = dict(self.host, **{constant: "different"})
                self.write_constants("cas_compatibility.py", changed)
                with self.assertRaisesRegex(VALIDATOR.CompatibilityProfileError, "Host compatibility declaration differs: " + field):
                    self.validate()
                self.write_constants("cas_compatibility.py", self.host)

    def test_production_hash_and_framework_pin_must_match_the_profile(self):
        for constant, message in (("EXPECTED_EXE_SHA256", "Native target differs"),
                                  ("EXPECTED_PYMHF", "Native framework declaration differs")):
            with self.subTest(constant=constant):
                self.write_constants("src/runtime.py", dict(self.native, **{constant: "different"}))
                with self.assertRaisesRegex(VALIDATOR.CompatibilityProfileError, message):
                    self.validate()
                self.write_constants("src/runtime.py", self.native)

    def test_each_developer_target_is_checked_independently(self):
        for name in VALIDATOR.DEVELOPER_SOURCES:
            with self.subTest(name=name):
                path = self.root / name
                original = path.read_bytes()
                path.write_text(path.read_text(encoding="utf-8").replace("a" * 64, "b" * 64), encoding="utf-8")
                with self.assertRaisesRegex(VALIDATOR.CompatibilityProfileError, "Native target differs") as failure:
                    self.validate(developer=True)
                self.assertIn(name, str(failure.exception))
                path.write_bytes(original)

    def test_generated_hash_and_framework_are_checked_when_requested(self):
        for constant in ("EXPECTED_EXE_SHA256", "EXPECTED_PYMHF"):
            with self.subTest(constant=constant):
                self.write_constants("CompanionAutoSummon.py", dict(self.native, **{constant: "different"}))
                self.assertTrue(self.validate()["all_declarations_match"])
                with self.assertRaises(VALIDATOR.CompatibilityProfileError):
                    self.validate(generated=True)
        self.write_constants("CompanionAutoSummon.py", self.native)

    def test_manifest_hash_build_and_framework_drift_are_refused(self):
        for field in ("supported_nms_exe_sha256", "steam_build", "framework"):
            with self.subTest(field=field):
                self.write_json("manifest.json", dict(self.manifest, **{field: "different"}))
                with self.assertRaisesRegex(VALIDATOR.CompatibilityProfileError, "Manifest compatibility declarations differ"):
                    self.validate()
        self.write_json("manifest.json", self.manifest)

    def test_profile_semantic_drift_is_not_silently_used_as_a_new_target(self):
        for field, changed in (("steam_build", "98765432"), ("exe_sha256", "b" * 64),
                               ("game_release", "Other release"), ("framework_version", "0.3.0")):
            with self.subTest(field=field):
                self.write_json("compatibility.json", dict(self.profile, **{field: changed}))
                with self.assertRaisesRegex(VALIDATOR.CompatibilityProfileError, "Host compatibility declaration differs"):
                    self.validate()
        self.write_json("compatibility.json", self.profile)

    def test_malformed_profile_fields_fingerprints_and_duplicate_json_are_refused(self):
        for changed in (dict(self.profile, schema_version=True), dict(self.profile, schema_version=2),
                        dict(self.profile, extra="unrecognized"), dict(self.profile, exe_sha256="A" * 64),
                        dict(self.profile, exe_sha256="a" * 63), dict(self.profile, steam_build="unknown"),
                        {key: value for key, value in self.profile.items() if key != "game_release"}):
            with self.subTest(changed=changed):
                self.write_json("compatibility.json", changed)
                with self.assertRaises(VALIDATOR.CompatibilityProfileError):
                    self.validate()
        text = json.dumps(self.profile).replace('"schema_version": 1,',
                                                '"schema_version": 1, "schema_version": 1,', 1)
        (self.root / "compatibility.json").write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(VALIDATOR.CompatibilityProfileError, "Duplicate compatibility JSON key"):
            self.validate()

    def test_missing_developer_source_and_missing_generated_file_fail_only_when_required(self):
        for name, options in [(name, {"developer": True}) for name in VALIDATOR.DEVELOPER_SOURCES] + [
                ("CompanionAutoSummon.py", {"generated": True})]:
            with self.subTest(name=name):
                path = self.root / name
                original = path.read_bytes()
                path.unlink()
                self.assertTrue(self.validate()["all_declarations_match"])
                with self.assertRaises(OSError):
                    self.validate(**options)
                path.write_bytes(original)

    def test_nonliteral_or_duplicate_native_declarations_are_refused_without_execution(self):
        path = self.root / "src/runtime.py"
        original = path.read_text(encoding="utf-8")
        for replacement in ("get_untrusted_native_value()", "'a' * 64"):
            path.write_text(original.replace(repr("a" * 64), replacement, 1), encoding="utf-8")
            with self.subTest(replacement=replacement), self.assertRaisesRegex(
                    VALIDATOR.CompatibilityProfileError, "literal values"):
                self.validate()
        path.write_text(original + "EXPECTED_EXE_SHA256 = 'duplicate'\n", encoding="utf-8")
        with self.assertRaisesRegex(VALIDATOR.CompatibilityProfileError, "Expected one literal"):
            self.validate()

    def test_production_build_profile_gate_precedes_output_creation_or_replacement(self):
        spec = importlib.util.spec_from_file_location("cas_profile_gated_build", ROOT / "build.py")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        self.write_constants("src/runtime.py", dict(self.native, EXPECTED_EXE_SHA256="b" * 64))
        target = self.root / "CompanionAutoSummon.py"
        for existing in (False, True):
            with self.subTest(existing=existing):
                if existing:
                    target.write_bytes(b"keep previous generated artifact")
                elif target.exists():
                    target.unlink()
                before = self.snapshot()
                with patch.object(builder, "ROOT", self.root), patch.object(builder, "validate_locales"), patch.object(
                        builder, "validate_compatibility", VALIDATOR.validate):
                    with self.assertRaisesRegex(VALIDATOR.CompatibilityProfileError, "Native target differs"):
                        builder.build()
                self.assertEqual(before, self.snapshot())


if __name__ == "__main__":
    unittest.main()
