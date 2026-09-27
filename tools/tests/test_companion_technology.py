"""Owned synthetic MXML fixtures; no game, compiler or deployment access."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("cas_technology_builder", ROOT / "tools/build_companion_technology.py")
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


def prop(parent, name, text=None, **attributes):
    return BUILDER.property_node(parent, name, text, **attributes)


def source_technology():
    root = ET.Element("Data", template="cGcTechnologyTable")
    table = prop(root, "Table")
    original = prop(table, "Table", "GcTechnology", _id="ORIGINAL")
    prop(original, "ID", "ORIGINAL")
    prop(original, "UnknownFutureField", "keep exactly")
    template = prop(table, "Table", "GcTechnology", _id="SUIT_ROCKET")
    for name, text in {"ID": "SUIT_ROCKET", "Name": "OLD_NAME", "NameLower": "OLD_LOWER",
                       "Subtitle": "OLD_SUB", "Description": "OLD_DESC", "BuildFullyCharged": "true",
                       "Chargeable": "true", "ChargeAmount": "50", "RequiredTech": "",
                       "ChargeMultiplier": "1.000000", "FragmentCost": "90",
                       "PrimaryItem": "true", "UnrelatedCloneField": "preserve"}.items():
        prop(template, name, text)
    prop(prop(template, "Icon", "TkTextureResource"), "Filename", "VANILLA.DDS")
    prop(prop(template, "Category", "GcTechnologyCategory"), "TechnologyCategory", "Suit")
    prop(prop(template, "ChargeType", "GcRealitySubstanceCategory"), "SubstanceCategory", "Earth")
    prop(prop(template, "BaseStat", "GcStatsTypes"), "StatsType", "Suit_RocketLocker")
    prop(prop(template, "StatBonuses"), "StatBonuses", "old rocket bonus")
    prop(prop(template, "ChargeBy"), "ChargeBy", "ROCKETSUB", _index="0")
    prop(prop(template, "Requirements"), "Requirements", "old recipe")
    return root


def source_research():
    root = ET.Element("Data", template="cGcUnlockableTrees")
    all_trees = prop(root, "Trees")
    prop(all_trees, "Other", "untouched")
    suit = prop(all_trees, "SuitTech", "GcUnlockableItemTrees")
    tree = prop(prop(suit, "Trees"), "Trees", "GcUnlockableItemTree", _index="0")
    prop(tree, "CostTypeID", "NANITES")
    native_root = prop(tree, "Root", "GcUnlockableItemTreeNode")
    prop(native_root, "Unlockable", "ENERGY")
    native_child = prop(prop(native_root, "Children"), "Children", "GcUnlockableItemTreeNode", _index="0")
    prop(native_child, "Unlockable", "ORIGINAL")
    prop(native_child, "Children")
    return root


def source_products():
    root = ET.Element("Data", template="cGcProductTable")
    table = prop(root, "Table")
    for identifier in ("TECH_COMP", "CASING", "POWERCELL", "MICROCHIP"):
        prop(prop(table, "Table", "GcProductData", _id=identifier), "ID", identifier)
    return root


def source_language():
    root = ET.Element("Data", template="cTkLocalisationTable")
    record = prop(prop(root, "Table"), "Table", "TkLocalisationEntry", _id="ORIGINAL_TEXT")
    prop(record, "Id", "ORIGINAL_TEXT")
    for language in BUILDER.NATIVE_LANGUAGES:
        prop(record, language, "unrelated vanilla text")
    return root


class TechnologyBuilderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cas-technology-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "repository"
        self.root.mkdir()
        self.source = Path(temporary.name) / "source"
        self.source.mkdir()
        self.output = self.root / "work" / "prototype"
        self.addCleanup(patch.stopall)
        patch.object(BUILDER, "ROOT", self.root).start()
        for relative in ("cas_compatibility.py", "Start-CompanionAutoSummon.ps1", "tools/validate_locales.py", "tools/quick_menu_toggle.py",
                         "tools/quick_menu_item.py", "src/runtime.py"):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        shutil.copytree(ROOT / "locales", self.root / "locales")
        (self.root / "manifest.json").write_text(json.dumps({"steam_build": "25442159",
            "supported_nms_exe_sha256": BUILDER.TARGET_SHA256}), encoding="utf-8")
        self.hashes = {}
        for name, tree in ((BUILDER.TECHNOLOGY, source_technology()), (BUILDER.RESEARCH, source_research()),
                           (BUILDER.PRODUCTS, source_products()), (BUILDER.VANILLA_LANGUAGE, source_language())):
            self.write_source(name, tree)
        patch.object(BUILDER, "SOURCE_HASHES", self.hashes).start()
        icons = self.root / "assets/ui"
        icons.mkdir(parents=True)
        icon_hashes = {}
        for name in BUILDER.ICON_HASHES:
            data = ("owned synthetic icon " + name).encode("ascii")
            (icons / name).write_bytes(data)
            icon_hashes[name] = BUILDER.sha256(data)
        patch.object(BUILDER, "ICON_HASHES", icon_hashes).start()

    def write_source(self, name, root):
        data = BUILDER.xml_bytes(root)
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self.hashes[name] = BUILDER.sha256(data)

    def read_source(self, name):
        return ET.parse(self.source / name).getroot()

    def build(self):
        return BUILDER.build(self.source, self.output)

    def assert_refused(self, message):
        with self.assertRaisesRegex(BUILDER.PrototypeError, message):
            self.build()
        self.assertFalse(self.output.exists())

    def test_append_only_native_records_and_charge_dependency_recipe_contract(self):
        source_bytes = {name: (self.source / name).read_bytes() for name in self.hashes}
        report = self.build()
        root = ET.parse(self.output / BUILDER.TECHNOLOGY).getroot()
        table, records = BUILDER.indexed_records(root)
        source_table, _ = BUILDER.indexed_records(self.read_source(BUILDER.TECHNOLOGY))
        self.assertEqual([BUILDER.semantic(row) for row in list(table)[:2]],
                         [BUILDER.semantic(row) for row in source_table])
        self.assertEqual(set(records), {"ORIGINAL", "SUIT_ROCKET", "CAS_LINK", "CAS_RECHARGE"})
        for identifier in ("CAS_LINK", "CAS_RECHARGE"):
            row = records[identifier]
            self.assertEqual(BUILDER.value(row, "BuildFullyCharged"), "false")
            self.assertEqual(BUILDER.value(row, "UnrelatedCloneField"), "preserve")
            self.assertEqual(BUILDER.value(BUILDER.one(row, "BaseStat"), "StatsType"), "Unspecified")
            self.assertEqual(len(BUILDER.one(row, "StatBonuses")), 0)
            self.assertEqual(BUILDER.value(row, "Name"), BUILDER.value(row, "NameLower"))
            actual = tuple((BUILDER.value(item, "ID"), int(BUILDER.value(item, "Amount")))
                           for item in BUILDER.one(row, "Requirements"))
            self.assertEqual(actual, BUILDER.RECIPES[identifier])
        self.assertEqual(BUILDER.value(records["CAS_LINK"], "ChargeAmount"), "100")
        self.assertEqual([child.get("value") for child in BUILDER.one(records["CAS_LINK"], "ChargeBy")], ["POWERCELL"])
        self.assertEqual(BUILDER.value(records["CAS_RECHARGE"], "Chargeable"), "false")
        self.assertEqual(BUILDER.value(records["CAS_RECHARGE"], "ChargeAmount"), "0")
        self.assertEqual(BUILDER.value(records["CAS_RECHARGE"], "RequiredTech"), "CAS_LINK")
        self.assertEqual(len(BUILDER.one(records["CAS_RECHARGE"], "ChargeBy")), 0)
        self.assertEqual(source_bytes, {name: (self.source / name).read_bytes() for name in self.hashes})
        self.assertTrue(report["unchanged_vanilla_records_verified"])

    def test_research_adds_one_paid_branch_without_modifying_prior_nodes(self):
        self.build()
        root = ET.parse(self.output / BUILDER.RESEARCH).getroot()
        tree = root.find("./Property/Property[@name='SuitTech']/Property/Property")
        self.assertEqual(BUILDER.value(tree, "CostTypeID"), "NANITES")
        children = BUILDER.one(BUILDER.one(tree, "Root"), "Children")
        branch = children[-1]
        self.assertEqual(branch.get("_index"), "1")
        self.assertEqual(BUILDER.value(branch, "Unlockable"), "CAS_LINK")
        nested = list(BUILDER.one(branch, "Children"))
        self.assertEqual(len(nested), 1)
        self.assertEqual(BUILDER.value(nested[0], "Unlockable"), "CAS_RECHARGE")
        children.remove(branch)
        self.assertEqual(BUILDER.semantic(root), BUILDER.semantic(self.read_source(BUILDER.RESEARCH)))

    def test_only_six_authored_localization_records_all_seventeen_fields_and_aliases(self):
        report = self.build()
        root = ET.parse(self.output / BUILDER.AUTHOR_LANGUAGE).getroot()
        records = list(BUILDER.one(root, "Table"))
        self.assertEqual(len(records), 6)
        self.assertEqual({BUILDER.value(row, "Id") for row in records}, set(BUILDER.REFERENCES.values()))
        for key, reference in BUILDER.REFERENCES.items():
            row = next(row for row in records if BUILDER.value(row, "Id") == reference)
            self.assertEqual(len(row), 18)
            for native, locale in BUILDER.NATIVE_LANGUAGES.items():
                catalog = json.loads((self.root / "locales" / (locale + ".json")).read_text(encoding="utf-8"))
                self.assertEqual(BUILDER.value(row, native), catalog["messages"][key]["text"])
        self.assertEqual(report["localization"]["regional_aliases"], BUILDER.ALIASES)
        self.assertFalse(report["localization_registered"])
        self.assertFalse(report["localization"]["language_review_verified"])

    def test_catalog_values_are_consumed_directly_and_xml_escaped(self):
        path = self.root / "locales/fr.json"
        catalog = json.loads(path.read_text(encoding="utf-8"))
        text = 'Lien <prototype> & "compagnon"'
        catalog["messages"]["tech.link.name"]["text"] = text
        path.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
        self.build()
        root = ET.parse(self.output / BUILDER.AUTHOR_LANGUAGE).getroot()
        row = next(row for row in BUILDER.one(root, "Table") if BUILDER.value(row, "Id") == "CAS_LINK_NAME")
        self.assertEqual(BUILDER.value(row, "French"), text)

    def test_manifest_hashes_exact_payload_and_honest_no_runtime_or_install_claim(self):
        report = self.build()
        self.assertEqual(len(report["files"]), 6)
        self.assertEqual(len([p for p in self.output.rglob("*") if p.is_file()]), 7)
        for name, digest in report["files"].items():
            self.assertEqual(BUILDER.sha256((self.output / name).read_bytes()), digest)
        for key in ("installable", "installed", "game_launched", "runtime_integration", "inventory_writes",
                    "save_writes", "compiled", "gameplay_verified", "multiplayer_verified", "uninstall_verified"):
            self.assertIs(report[key], False)
        self.assertTrue(report["offline_only"])
        self.assertEqual(report["source_sha256"], self.hashes)
        self.assertEqual(report["target"]["exe_sha256"], BUILDER.TARGET_SHA256)
        self.assertFalse(report["target"]["executable_read_by_builder"])
        self.assertNotIn(BUILDER.PRODUCTS, report["files"])
        self.assertNotIn(BUILDER.VANILLA_LANGUAGE, report["files"])

    def test_repeated_build_refuses_without_changing_existing_output(self):
        self.build()
        before = {str(p): p.read_bytes() for p in self.output.rglob("*") if p.is_file()}
        with self.assertRaisesRegex(BUILDER.PrototypeError, "already exists"):
            self.build()
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.output.rglob("*") if p.is_file()})

    def test_source_hash_change_refused_before_output_creation(self):
        path = self.source / BUILDER.TECHNOLOGY
        path.write_bytes(path.read_bytes() + b" ")
        self.assert_refused("source hash")

    def test_unsupported_manifest_target_refused(self):
        (self.root / "manifest.json").write_text(json.dumps({"steam_build": "changed",
            "supported_nms_exe_sha256": BUILDER.TARGET_SHA256}), encoding="utf-8")
        self.assert_refused("Unsupported repository target")

    def test_missing_recipe_product_refused(self):
        root = self.read_source(BUILDER.PRODUCTS)
        table, records = BUILDER.indexed_records(root)
        table.remove(records["CASING"])
        self.write_source(BUILDER.PRODUCTS, root)
        self.assert_refused("unknown native product")

    def test_duplicate_vanilla_id_and_existing_custom_technology_are_refused(self):
        original = self.read_source(BUILDER.TECHNOLOGY)
        for identifier, message in (("ORIGINAL", "Duplicate source ID"), ("CAS_LINK", "already present")):
            root = deepcopy(original)
            prop(prop(BUILDER.one(root, "Table"), "Table", "GcTechnology", _id=identifier), "ID", identifier)
            self.write_source(BUILDER.TECHNOLOGY, root)
            with self.subTest(identifier=identifier):
                self.assert_refused(message)

    def test_existing_custom_research_and_duplicate_indices_refused(self):
        original = self.read_source(BUILDER.RESEARCH)
        for custom in (True, False):
            root = deepcopy(original)
            children = root.find("./Property/Property[@name='SuitTech']/Property/Property/Property[@name='Root']/Property[@name='Children']")
            if custom:
                BUILDER.set_value(children[0], "Unlockable", "CAS_RECHARGE")
            else:
                children.append(deepcopy(children[0]))
            self.write_source(BUILDER.RESEARCH, root)
            with self.subTest(custom=custom):
                self.assert_refused("already present" if custom else "duplicate research")

    def test_native_localization_id_collision_refused(self):
        root = self.read_source(BUILDER.VANILLA_LANGUAGE)
        BUILDER.set_value(BUILDER.one(root, "Table")[0], "Id", "CAS_LINK_NAME")
        self.write_source(BUILDER.VANILLA_LANGUAGE, root)
        self.assert_refused("Localization ID collision")

    def test_unexpected_language_shape_refused(self):
        root = self.read_source(BUILDER.VANILLA_LANGUAGE)
        row = BUILDER.one(root, "Table")[0]
        row.remove(BUILDER.one(row, "USEnglish"))
        self.write_source(BUILDER.VANILLA_LANGUAGE, root)
        self.assert_refused("native language fields")

    def test_catalog_failure_prevents_output(self):
        path = self.root / "locales/fr.json"
        catalog = json.loads(path.read_text(encoding="utf-8"))
        catalog["messages"]["tech.link.description"]["source_sha256"] = "0" * 64
        path.write_text(json.dumps(catalog), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Stale source fingerprint"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_changed_original_artwork_prevents_output(self):
        (self.root / "assets/ui/SETTINGS.DDS").write_bytes(b"unknown")
        self.assert_refused("icon hash")

    def test_output_outside_repo_build_work_or_equal_to_root_is_refused(self):
        for path in (self.root / "game/GAMEDATA/MODS/cas", self.root / "build", self.root / "work",
                     self.root / "work/../../outside"):
            with self.subTest(path=path), self.assertRaisesRegex(BUILDER.PrototypeError, "new child"):
                BUILDER.build(self.source, path)
            self.assertFalse(path.exists())

    def test_reparse_ancestor_refused_before_input_or_output_access(self):
        info = type("ReparseInfo", (), {"st_mode": 0o40755, "st_file_attributes": 0x400})()
        with patch.object(Path, "lstat", return_value=info):
            with self.assertRaisesRegex(BUILDER.PrototypeError, "reparse"):
                BUILDER.checked_output(self.output)
        self.assertFalse(self.output.exists())

    def test_missing_template_and_wrong_native_template_refused(self):
        root = self.read_source(BUILDER.TECHNOLOGY)
        table, records = BUILDER.indexed_records(root)
        table.remove(records["SUIT_ROCKET"])
        self.write_source(BUILDER.TECHNOLOGY, root)
        self.assert_refused("Missing exact clone")
        root.set("template", "UnexpectedType")
        self.write_source(BUILDER.TECHNOLOGY, root)
        self.assert_refused("Unexpected MXML template")


if __name__ == "__main__":
    unittest.main()
