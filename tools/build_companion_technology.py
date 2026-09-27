"""Build a private offline technology-data prototype; never install or launch it."""

import argparse
from copy import deepcopy
import hashlib
from importlib import util
import json
from pathlib import Path
import stat
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TABLES = "METADATA/REALITY/TABLES/"
TECHNOLOGY = TABLES + "NMS_REALITY_GCTECHNOLOGYTABLE.MXML"
RESEARCH = TABLES + "UNLOCKABLEITEMTREES.MXML"
PRODUCTS = TABLES + "NMS_REALITY_GCPRODUCTTABLE.MXML"
VANILLA_LANGUAGE = "LANGUAGE/NMS_LOC1_ENGLISH.MXML"
AUTHOR_LANGUAGE = "LANGUAGE/CAS_TECHNOLOGY.MXML"
ICON_DIRECTORY = "TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/"
TARGET_SHA256 = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"
SOURCE_HASHES = {
    TECHNOLOGY: "f55265017571d016ae9eabf3b352a3cfb84d7ec8dd11466d64b0eb4d3156b865",
    RESEARCH: "b3de0fdbec6fd7372160840d787c069b5b889f4165714e5d39fa35f6842fb42d",
    PRODUCTS: "11359c81a126f95014e6b52a5d484ac594a3a923bc2eb2ce465ab08ad7df1edb",
    VANILLA_LANGUAGE: "5f46a8b7232eaf5e84e9ea24f71cfef5a365aedf654625e27ebdba409ccc2472",
}
ICON_HASHES = {
    "SETTINGS.DDS": "808a8b3f887a17a8ccc2b32752196e802915c87ecec43abb07205a5c7d30e9fe",
    "AUTOMATION.DDS": "0051f22c3726f328a8c6a94f48b3329c2de6069454750052f398acb051dadce1",
}
NATIVE_LANGUAGES = {
    "English": "en", "French": "fr", "Italian": "it", "German": "de",
    "Spanish": "es-ES", "Russian": "ru", "Polish": "pl", "Dutch": "nl",
    "Portuguese": "pt-PT", "LatinAmericanSpanish": "es-ES",
    "BrazilianPortuguese": "pt-BR", "SimplifiedChinese": "zh-Hans",
    "TraditionalChinese": "zh-Hant", "TencentChinese": "zh-Hans",
    "Korean": "ko", "Japanese": "ja", "USEnglish": "en",
}
ALIASES = {"USEnglish": "en", "LatinAmericanSpanish": "es-ES", "TencentChinese": "zh-Hans"}
REFERENCES = {
    "tech.link.name": "CAS_LINK_NAME", "tech.link.subtitle": "CAS_LINK_SUB",
    "tech.link.description": "CAS_LINK_DESC", "tech.recharger.name": "CAS_RECHARGE_NAME",
    "tech.recharger.subtitle": "CAS_RECHARGE_SUB", "tech.recharger.description": "CAS_RECHARGE_DESC",
}
RECIPES = {
    "CAS_LINK": (("TECH_COMP", 2), ("CASING", 1), ("POWERCELL", 1)),
    "CAS_RECHARGE": (("TECH_COMP", 3), ("MICROCHIP", 1), ("POWERCELL", 1)),
}
MAX_INPUT_BYTES = 20_000_000
README = """# Companion Auto Summon technology data prototype

PRIVATE OFFLINE PROTOTYPE — NOT INSTALLABLE.

The two appended Suit technologies and ENERGY research branch are data only.
CAS_LINK proposes stored charge and Ion Battery recharge. CAS_RECHARGE requires
CAS_LINK and proposes automatic battery use. No runtime inventory observer,
charge debit, battery transaction or mandatory technology gate is included.
Nothing grants, researches, installs or recharges an item or edits a save.
Capacity 100, summon cost 10 and low threshold 20 are provisional design values;
only capacity is represented in the native technology data.

CAS_TECHNOLOGY.MXML contains six authored entries, using fourteen source
catalogs across seventeen native fields. USEnglish reuses English,
LatinAmericanSpanish reuses Spain Spanish, and TencentChinese reuses Simplified
Chinese. These aliases are not independent regional translations. Thirteen
catalogs remain unreviewed drafts. Native localization registration is absent.
No claim of in-game language selection, rendering or working technology is made.

Original CAS artwork is included. Merged technology/research tables contain
vanilla game data for private compiler checks: do not commit or publish them.
Source compilation, charge semantics, research UI, save/reload, multiplayer and
uninstall behavior require separate verification. Successful MXML compilation
alone establishes none of those behaviors. This tool neither compiles nor
deploys. It refuses unknown source hashes and any existing output folder.
"""


class PrototypeError(ValueError):
    """The bounded source or output contract was not satisfied."""


def require(condition, message):
    if not condition:
        raise PrototypeError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def no_links(path):
    """Reject existing links/junctions in a path before following any of them."""
    path = Path(path).absolute()
    for part in (path, *path.parents):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(info.st_mode)
                and not getattr(info, "st_file_attributes", 0) & 0x400,
                "Links and reparse points are not accepted")
    return path.resolve()


def checked_output(path):
    output = no_links(path)
    roots = (no_links(ROOT / "build"), no_links(ROOT / "work"))
    require(any(output != root and output.is_relative_to(root) for root in roots),
            "Output must be a new child of this repository's build or work directory")
    require(not output.exists(), "Output already exists; refusing overwrite")
    return output


def read_bounded(path):
    path = no_links(path)
    require(path.is_file() and path.stat().st_size <= MAX_INPUT_BYTES, "Invalid or oversized input file")
    data = path.read_bytes()
    require(len(data) <= MAX_INPUT_BYTES, "Input exceeded its bound")
    return data


def one(element, name):
    found = element.findall(f"Property[@name='{name}']")
    require(len(found) == 1, "Expected one property: " + name)
    return found[0]


def value(element, name):
    result = one(element, name).get("value")
    require(result is not None, "Missing property value: " + name)
    return result


def set_value(element, name, text):
    one(element, name).set("value", text)


def property_node(parent, name, text=None, **attributes):
    fields = {"name": name, **attributes}
    if text is not None:
        fields["value"] = text
    return ET.SubElement(parent, "Property", fields)


def semantic(element):
    """Compare data and child order, ignoring XML formatting whitespace only."""
    return (element.tag, tuple(sorted(element.attrib.items())), (element.text or "").strip(),
            tuple(semantic(child) for child in element))


def indexed_records(root):
    table = one(root, "Table")
    records = {}
    for record in table:
        key = value(record, "ID")
        require(key not in records, "Duplicate source ID: " + key)
        records[key] = record
    return table, records


def load_validator():
    spec = util.spec_from_file_location("_cas_technology_locales", ROOT / "tools/validate_locales.py")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authored_localization(template, catalogs, keys):
    require(set(keys) == set(REFERENCES), "Unexpected technology catalog keys")
    examples = list(one(template, "Table"))
    require(examples, "Missing native localization shape")
    require([child.get("name") for child in examples[0]] == ["Id", *NATIVE_LANGUAGES],
            "Unexpected native language fields")
    existing_ids = {value(entry, "Id") for entry in examples}
    require(not existing_ids.intersection(REFERENCES.values()), "Localization ID collision")
    root = ET.Element("Data", {"template": "cTkLocalisationTable"})
    table = property_node(root, "Table")
    for key in keys:
        reference = REFERENCES[key]
        entry = property_node(table, "Table", "TkLocalisationEntry", _id=reference)
        property_node(entry, "Id", reference)
        for field, locale in NATIVE_LANGUAGES.items():
            property_node(entry, field, catalogs[locale]["messages"][key]["text"])
    return root


def clone_technology(template, identifier):
    result = deepcopy(template)
    result.set("_id", identifier)
    prefix = "tech.link." if identifier == "CAS_LINK" else "tech.recharger."
    changes = {"ID": identifier, "Name": REFERENCES[prefix + "name"],
               "NameLower": REFERENCES[prefix + "name"], "Subtitle": REFERENCES[prefix + "subtitle"],
               "Description": REFERENCES[prefix + "description"], "BuildFullyCharged": "false",
               "Chargeable": "true" if identifier == "CAS_LINK" else "false",
               "ChargeAmount": "100" if identifier == "CAS_LINK" else "0",
               "RequiredTech": "" if identifier == "CAS_LINK" else "CAS_LINK"}
    for name, text in changes.items():
        set_value(result, name, text)
    require(value(one(result, "Category"), "TechnologyCategory") == "Suit", "Template is not Suit technology")
    set_value(one(result, "BaseStat"), "StatsType", "Unspecified")
    bonuses = one(result, "StatBonuses")
    bonuses[:] = []
    charge_by = one(result, "ChargeBy")
    charge_by[:] = []
    if identifier == "CAS_LINK":
        property_node(charge_by, "ChargeBy", "POWERCELL", _index="0")
    requirements = one(result, "Requirements")
    requirements[:] = []
    for product, count in RECIPES[identifier]:
        requirement = property_node(requirements, "Requirements", "GcTechnologyRequirement", _id=product)
        property_node(requirement, "ID", product)
        property_node(property_node(requirement, "Type", "GcInventoryType"), "InventoryType", "Product")
        property_node(requirement, "Amount", str(count))
    icon = "SETTINGS.DDS" if identifier == "CAS_LINK" else "AUTOMATION.DDS"
    set_value(one(result, "Icon"), "Filename", ICON_DIRECTORY + icon)
    return result


def append_research(root):
    require(not any(node.get("value") in RECIPES for node in root.iter("Property")
                    if node.get("name") == "Unlockable"), "Research ID already present")
    suit = one(one(root, "Trees"), "SuitTech")
    matches = [tree for tree in one(suit, "Trees") if value(one(tree, "Root"), "Unlockable") == "ENERGY"]
    require(len(matches) == 1, "Expected one SuitTech ENERGY root")
    tree = matches[0]
    cost_type = value(tree, "CostTypeID")
    require(cost_type == "NANITES", "Unexpected native research cost type")
    children = one(one(tree, "Root"), "Children")
    require([child.get("_index") for child in children] == [str(i) for i in range(len(children))],
            "Malformed or duplicate research child indices")
    branch = property_node(children, "Children", "GcUnlockableItemTreeNode", _index=str(len(children)))
    property_node(branch, "Unlockable", "CAS_LINK")
    nested = property_node(property_node(branch, "Children"), "Children", "GcUnlockableItemTreeNode", _index="0")
    property_node(nested, "Unlockable", "CAS_RECHARGE")
    property_node(nested, "Children")
    return children, branch, cost_type


def xml_bytes(root):
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def build(source_dir, output_dir):
    output = checked_output(output_dir)
    source = no_links(source_dir)
    require(source.is_dir(), "Missing source directory")
    manifest = json.loads(read_bounded(ROOT / "manifest.json"))
    require(manifest.get("supported_nms_exe_sha256") == TARGET_SHA256
            and str(manifest.get("steam_build")) == "25442159", "Unsupported repository target")
    validator = load_validator()
    locale_report = validator.validate(source_root=ROOT)
    catalogs = {code: json.loads(read_bounded(ROOT / "locales" / (code + ".json"))) for code in validator.LOCALES}
    inputs = {name: read_bounded(source / name) for name in SOURCE_HASHES}
    require(all(sha256(data) == SOURCE_HASHES[name] for name, data in inputs.items()),
            "Unexpected vanilla source hash; this profile is exact-build only")
    roots = {name: ET.fromstring(data) for name, data in inputs.items()}
    for name, template in ((TECHNOLOGY, "cGcTechnologyTable"), (RESEARCH, "cGcUnlockableTrees"),
                           (PRODUCTS, "cGcProductTable"), (VANILLA_LANGUAGE, "cTkLocalisationTable")):
        require(roots[name].tag == "Data" and roots[name].get("template") == template, "Unexpected MXML template")
    technologies, records = indexed_records(roots[TECHNOLOGY])
    _products, products = indexed_records(roots[PRODUCTS])
    require(not set(RECIPES).intersection(records), "Technology ID already present")
    require("SUIT_ROCKET" in records, "Missing exact clone template")
    require(all(product in products for recipe in RECIPES.values() for product, _count in recipe),
            "Recipe uses an unknown native product")
    original_technology = semantic(roots[TECHNOLOGY])
    original_research = semantic(roots[RESEARCH])
    additions = [clone_technology(records["SUIT_ROCKET"], identifier) for identifier in RECIPES]
    technologies.extend(additions)
    children, branch, cost_type = append_research(roots[RESEARCH])
    localization = authored_localization(roots[VANILLA_LANGUAGE], catalogs, validator.TECHNOLOGY_KEYS)
    payload = {TECHNOLOGY: xml_bytes(roots[TECHNOLOGY]), RESEARCH: xml_bytes(roots[RESEARCH]),
               AUTHOR_LANGUAGE: xml_bytes(localization), "README.md": README.encode("utf-8")}
    for addition in additions:
        technologies.remove(addition)
    children.remove(branch)
    require(semantic(roots[TECHNOLOGY]) == original_technology
            and semantic(roots[RESEARCH]) == original_research, "A vanilla record was modified")
    for name, expected in ICON_HASHES.items():
        data = read_bounded(ROOT / "assets/ui" / name)
        require(sha256(data) == expected, "Original icon hash mismatch")
        payload[ICON_DIRECTORY + name] = data
    report = {"name": "Companion Auto Summon technology prototype", "schema_version": 1,
              "offline_only": True, "installable": False, "installed": False, "game_launched": False,
              "runtime_integration": False, "inventory_writes": False, "save_writes": False,
              "compiled": False, "localization_registered": False, "gameplay_verified": False,
              "multiplayer_verified": False, "uninstall_verified": False,
              "target": {"steam_build": manifest["steam_build"], "exe_sha256": TARGET_SHA256,
                         "executable_read_by_builder": False, "source_profile": "Cosmos 7.04 / MBINCompiler 7.04.0.1"},
              "source_sha256": {name: sha256(data) for name, data in inputs.items()},
              "catalog_sha256": {code: sha256(read_bounded(ROOT / "locales" / (code + ".json"))) for code in catalogs},
              "localization": {**locale_report, "native_language_fields": NATIVE_LANGUAGES,
                               "regional_aliases": ALIASES},
              "provisional_balance": {"capacity": 100, "summon_cost": 10, "low_threshold": 20},
              "recipes": RECIPES, "research_cost_type": cost_type,
              "research_fragment_costs": {value(node, "ID"): value(node, "FragmentCost") for node in additions},
              "unchanged_vanilla_records_verified": True,
              "files": {name: sha256(data) for name, data in payload.items()}}
    payload["manifest.json"] = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    require(checked_output(output) == output, "Output path changed")
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(data)
    require(all(sha256((output / name).read_bytes()) == digest for name, digest in report["files"].items()),
            "Output readback mismatch")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    arguments = parser.parse_args(argv)
    try:
        report = build(arguments.source_dir, arguments.output_dir)
    except (OSError, ValueError, ET.ParseError, KeyError) as error:
        parser.exit(1, f"Technology prototype refused: {error}\n")
    print(json.dumps({"offline_only": report["offline_only"], "installable": report["installable"],
                      "payload_files": len(report["files"])}, sort_keys=True))


if __name__ == "__main__":
    main()
