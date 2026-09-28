"""Package tested project files without game access, installation, or deployment.

Run after build.py, tools/validate_offline.py and tools/framework_smoke.py:
    python -B tools/package.py
Preserves manifest metadata, refreshes hashes/test counts, and verifies the ZIP.
"""

import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile
from validate_locales import LOCALES, validate as validate_locales
from validate_compatibility import validate as validate_compatibility


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIRECTORY = ROOT / "build" / "validation"
PACKAGE_FILES = (
    "CompanionAutoSummon.py", "Launch-CompanionAutoSummon.py", "README.md", "README.cs.md",
    "cas_compatibility.py", "compatibility.json",
    "TECHNICKE-OVERENI.md", "build.py", "Start-CompanionAutoSummon.ps1", "DEVELOPMENT.md",
    "LOCALIZATION.md", "DESIGN.md", "CHANGELOG.md", "ROADMAP.md", "QUICK-MENU.md",
    "docs/release/PRIPRAVA-VYDANI.md", "docs/release/INSTALACE-ZADANI.md",
    "docs/release/NEXUS-DESCRIPTION-DRAFT.md",
    "docs/research/TECHNOLOGY-PROTOTYPE.md", "docs/research/TECHNOLOGY-RUNTIME-AUDIT.md",
    "docs/research/COMPATIBILITY-GUARD-AUDIT.md",
    "docs/research/LIVE-084.md", "docs/release/MONETIZATION.md",
    "src/policy.py", "src/persistence.py", "src/settings.py", "src/runtime.py",
    "tests/test_policy.py", "tests/test_persistence.py", "tests/test_settings.py",
    "tests/test_runtime.py", "tests/test_launcher.py",
    "tests/test_compatibility.py",
    "tools/validate_locales.py", "tools/quick_menu_toggle.py", "tools/quick_menu_item.py",
    "tools/validate_compatibility.py",
    *(f"locales/{locale}.json" for locale in LOCALES),
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    sys.dont_write_bytecode = True
    locale_report = validate_locales(locales_dir=ROOT / "locales", source_root=ROOT)
    profile_report = validate_compatibility(source_root=ROOT, developer=True, generated=True)
    manifest_path = ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    package_version = manifest["version"]
    require(re.fullmatch(r"\d+\.\d+\.\d+-experimental", package_version),
            "Expected an explicit experimental version in manifest.json")
    version = package_version.removesuffix("-experimental")
    validation = json.loads((REPORT_DIRECTORY / f"offline-{version}.json").read_text(encoding="utf-8"))
    require(validation["version"] == version and validation["package_version"] == package_version,
            "Offline test report version differs")
    require(validation["passed"] is True and validation["source_unchanged_during_test"] is True,
            "Offline suite did not pass with unchanged sources")
    require(validation["tests_run"] > 0 and validation["failures"] == 0
            and validation["errors"] == 0 and validation["skipped"] == 0,
            "Offline suite must pass without failures, errors or skips")

    # Take a byte snapshot once, so ZIP entries and hashes describe the same
    # files even if an editor changes the worktree while packaging.
    payload = {name: (ROOT / name).read_bytes() for name in PACKAGE_FILES}
    tested_names = {"CompanionAutoSummon.py", "Launch-CompanionAutoSummon.py", "build.py", "Start-CompanionAutoSummon.ps1",
                    "cas_compatibility.py", "compatibility.json"}
    tested_names.update(path.relative_to(ROOT).as_posix() for path in ROOT.glob("src/*.py"))
    tested_names.update(path.relative_to(ROOT).as_posix() for path in ROOT.glob("tests/test_*.py"))
    require(set(validation["source_sha256"]) == tested_names, "Offline source coverage differs")
    require(tested_names <= set(PACKAGE_FILES), "New source/test files require an explicit package list update")
    for name in tested_names:
        require(digest(payload[name]) == validation["source_sha256"][name], f"Not the tested source: {name}")
    counts = validation["counts"]
    require(sum(counts.values()) == validation["tests_run"], "Test counts do not sum to the suite total")

    framework = json.loads((REPORT_DIRECTORY / f"framework-{version}.json").read_text(encoding="utf-8"))
    require(framework["version"] == version and framework["package_version"] == package_version,
            "Framework report version differs")
    require(framework["actual_framework_import_passed"] is True
            and framework["actual_gui_widget_construction_and_callbacks_passed"] is True
            and framework["disabled_outside_game"] is True and framework["hotkeys"] == 0,
            "Actual framework and GUI check did not pass")
    require(framework["framework_requirement"] == manifest["framework"]
            == f"pymhf[gui]=={framework['framework_version']}", "Framework version does not match the manifest")
    require(framework["generated_source_sha256"] == digest(payload["CompanionAutoSummon.py"]),
            "Generated source differs from the actual-framework check")

    # Preserve every other manifest field, particularly bounded live-test claims.
    manifest["offline_tests"] = {
        "passed": validation["tests_run"], "policy": counts["test_policy"],
        "persistence": counts["test_persistence"], "settings": counts["test_settings"],
        "adapter_simulation": counts["test_runtime"], "host_launcher": counts["test_launcher"],
        "compatibility": counts["test_compatibility"],
    }
    manifest["localization_catalogs"] = locale_report
    manifest["compatibility_profile_validation"] = profile_report
    manifest["files"] = [{"path": name, "sha256": digest(payload[name])} for name in PACKAGE_FILES]
    payload["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    archive_path = ROOT / "dist" / f"CompanionAutoSummon-{package_version}.zip"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_archive = archive_path.with_suffix(".zip.tmp")
    try:
        with zipfile.ZipFile(temporary_archive, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, content in payload.items():
                archive.writestr("CompanionAutoSummon/" + name, content)
        with zipfile.ZipFile(temporary_archive) as archive:
            require(archive.testzip() is None, "ZIP integrity verification failed")
            require(set(archive.namelist()) == {"CompanionAutoSummon/" + name for name in payload}, "ZIP file list differs")
            for name, content in payload.items():
                require(archive.read("CompanionAutoSummon/" + name) == content, f"ZIP bytes differ: {name}")
        for name in PACKAGE_FILES:
            require((ROOT / name).read_bytes() == payload[name], f"Project file changed during packaging: {name}")
        temporary_archive.replace(archive_path)
        manifest_path.write_bytes(payload["manifest.json"])
    finally:
        temporary_archive.unlink(missing_ok=True)
    record = {"archive": archive_path.relative_to(ROOT).as_posix(), "version": package_version,
              "files": len(payload), "bytes": archive_path.stat().st_size,
              "sha256": digest(archive_path.read_bytes()), "offline_tests_passed": validation["tests_run"],
              "deployed": False}
    (REPORT_DIRECTORY / f"package-{version}.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
