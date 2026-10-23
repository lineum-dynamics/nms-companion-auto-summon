"""Read-only native release comparison. Does not execute or scan either archive.

Requires pefile. Reports provenance and structural deltas, never malware safety.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile

import pefile


ASI = "Binaries/scripts/CompanionAutoSummon.asi"
LOADER = "Binaries/winmm.dll"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pe_summary(data):
    image = pefile.PE(data=data)
    imports = {}
    for entry in getattr(image, "DIRECTORY_ENTRY_IMPORT", ()):
        imports[entry.dll.decode("ascii")] = sorted(
            item.name.decode("ascii") if item.name else f"ordinal:{item.ordinal}"
            for item in entry.imports
        )
    exports = []
    for item in getattr(getattr(image, "DIRECTORY_ENTRY_EXPORT", None), "symbols", ()):
        exports.append(item.name.decode("ascii") if item.name else f"ordinal:{item.ordinal}")
    overlay = image.get_overlay_data_start_offset()
    coff_start = image.FILE_HEADER.PointerToSymbolTable
    strings_start = coff_start + image.FILE_HEADER.NumberOfSymbols * 18
    coff_end = None
    if coff_start and strings_start + 4 <= len(data):
        strings_size = struct.unpack_from("<I", data, strings_start)[0]
        if strings_size >= 4 and strings_start + strings_size <= len(data):
            coff_end = strings_start + strings_size
    flags = image.OPTIONAL_HEADER.DllCharacteristics
    return {
        "machine": hex(image.FILE_HEADER.Machine),
        "timestamp": image.FILE_HEADER.TimeDateStamp,
        "entrypoint": hex(image.OPTIONAL_HEADER.AddressOfEntryPoint),
        "dll_characteristics": hex(flags),
        "aslr": bool(flags & 0x40),
        "dep": bool(flags & 0x100),
        "high_entropy_va": bool(flags & 0x20),
        "overlay_bytes": len(data) - overlay if overlay is not None else 0,
        "coff_symbol_table_offset": coff_start,
        "coff_symbol_count": image.FILE_HEADER.NumberOfSymbols,
        "coff_table_end": coff_end,
        "coff_covers_overlay_with_zero_padding": overlay == coff_start
        and coff_end is not None and not any(data[coff_end:]),
        "sections": [
            {
                "name": section.Name.rstrip(b"\0").decode("ascii"),
                "raw_bytes": section.SizeOfRawData,
                "virtual_bytes": section.Misc_VirtualSize,
                "entropy": round(section.get_entropy(), 4),
                "writable_executable": bool(section.Characteristics & 0x80000000)
                and bool(section.Characteristics & 0x20000000),
            }
            for section in image.sections
        ],
        "imports": imports,
        "exports": sorted(exports),
    }


def archive(path):
    raw = path.read_bytes()
    with zipfile.ZipFile(path) as bundle:
        infos = bundle.infolist()
        names = [entry.filename for entry in infos]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate archive names")
        if bundle.testzip() is not None:
            raise ValueError("Archive CRC failure")
        members = {name: bundle.read(name) for name in names}
    return {
        "name": path.name,
        "bytes": len(raw),
        "sha256": digest(raw),
        "members": {name: {"bytes": len(data), "sha256": digest(data)}
                    for name, data in sorted(members.items())},
        "nested_archives": [name for name in names if name.lower().endswith(
            (".zip", ".7z", ".rar", ".tar", ".gz"))],
        "asi": pe_summary(members[ASI]),
        "loader": pe_summary(members[LOADER]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-zip", type=Path,
                        help="Omit if the old archive is inaccessible; do not bypass OS protection")
    parser.add_argument("--new-zip", required=True, type=Path)
    parser.add_argument("--old-receipt", required=True, type=Path)
    parser.add_argument("--new-receipt", required=True, type=Path)
    parser.add_argument("--dependency-lock", type=Path,
                        default=Path(__file__).resolve().parents[1] / "native/dependencies-lock.json")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    old_receipt = json.loads(args.old_receipt.read_text(encoding="utf-8-sig"))
    new_receipt = json.loads(args.new_receipt.read_text(encoding="utf-8-sig"))
    new = archive(args.new_zip)
    old = archive(args.old_zip) if args.old_zip else None
    if old is None:
        dependency_lock = json.loads(args.dependency_lock.read_text(encoding="utf-8-sig"))
        pinned_loader = next(component["binary"]["sha256"] for component in dependency_lock["components"]
                             if component["name"] == "Ultimate ASI Loader")
        old_sources, new_sources = old_receipt["sources"], new_receipt["sources"]
        changed_sources = [name for name in sorted(set(old_sources) | set(new_sources))
                           if old_sources.get(name) != new_sources.get(name)]
        report = {
            "scope": "Old build receipt versus new archive; old bytes NOT CHECKED",
            "limitation": "No claim of old archive/PE readback or antivirus clearance",
            "tool_sha256": digest(Path(__file__).read_bytes()),
            "pefile_version": pefile.__version__,
            "old_receipt_sha256": digest(args.old_receipt.read_bytes()),
            "new_receipt_sha256": digest(args.new_receipt.read_bytes()),
            "dependency_lock_matches_new_receipt": digest(args.dependency_lock.read_bytes())
            == new_receipt["sources"]["native/dependencies-lock.json"],
            "old_recorded_asi": old_receipt["products"]["CompanionAutoSummon.asi"],
            "new": new,
            "delta": {
                "compiler_hash_equal": old_receipt["compiler_sha256"] == new_receipt["compiler_sha256"],
                "compiler_sha256": new_receipt["compiler_sha256"],
                "imported_dll_names_equal": set(old_receipt["imports"]) == set(new_receipt["imports"]),
                "dependency_lock_equal": old_sources["native/dependencies-lock.json"]
                == new_sources["native/dependencies-lock.json"],
                "changed_vendored_inputs": [name for name in changed_sources
                                            if name.startswith(("native/third_party/", "native/licenses/"))],
                "changed_source_inputs": changed_sources,
                "new_asi_matches_receipt": new["members"][ASI]
                == new_receipt["products"]["CompanionAutoSummon.asi"],
                "new_loader_matches_lock": new["members"][LOADER]["sha256"]
                == pinned_loader,
            },
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"scope": report["scope"], "new_sha256": new["sha256"],
                          "delta": report["delta"], "sections": new["asi"]["sections"]}, indent=2))
        return
    old_members, new_members = old["members"], new["members"]
    old_sources, new_sources = old_receipt["sources"], new_receipt["sources"]
    old_imports, new_imports = old["asi"]["imports"], new["asi"]["imports"]
    added_imports, removed_imports = {}, {}
    for dll in sorted(set(old_imports) | set(new_imports)):
        added = sorted(set(new_imports.get(dll, ())) - set(old_imports.get(dll, ())))
        removed = sorted(set(old_imports.get(dll, ())) - set(new_imports.get(dll, ())))
        if added:
            added_imports[dll] = added
        if removed:
            removed_imports[dll] = removed
    report = {
        "scope": "Read-only archive/PE/provenance delta, not antivirus clearance",
        "pefile_version": pefile.__version__,
        "tool_sha256": digest(Path(__file__).read_bytes()),
        "old": old,
        "new": new,
        "delta": {
            "added_members": sorted(set(new_members) - set(old_members)),
            "removed_members": sorted(set(old_members) - set(new_members)),
            "changed_members": [name for name in sorted(set(old_members) & set(new_members))
                                if old_members[name] != new_members[name]],
            "compiler_hash_equal": old_receipt["compiler_sha256"] == new_receipt["compiler_sha256"],
            "compiler_sha256": new_receipt["compiler_sha256"],
            "loader_hash_equal": old_members[LOADER] == new_members[LOADER],
            "dependency_lock_equal": old_sources["native/dependencies-lock.json"]
            == new_sources["native/dependencies-lock.json"],
            "changed_vendored_inputs": [name for name in sorted(set(old_sources) | set(new_sources))
                                        if name.startswith(("native/third_party/", "native/licenses/"))
                                        and old_sources.get(name) != new_sources.get(name)],
            "added_imports": added_imports,
            "removed_imports": removed_imports,
            "exports_equal": old["asi"]["exports"] == new["asi"]["exports"],
            "old_asi_matches_receipt": old_members[ASI] == old_receipt["products"]["CompanionAutoSummon.asi"],
            "new_asi_matches_receipt": new_members[ASI] == new_receipt["products"]["CompanionAutoSummon.asi"],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"old_sha256": old["sha256"], "new_sha256": new["sha256"],
                      "delta": report["delta"]}, indent=2))


if __name__ == "__main__":
    main()
