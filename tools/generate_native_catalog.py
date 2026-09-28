"""Generate immutable UTF-8 catalogs for the native build, after validation."""
import json
import re
from pathlib import Path
from validate_locales import validate

ROOT = Path(__file__).resolve().parents[1]


def generate(output):
    validate(locales_dir=ROOT / "locales", source_root=ROOT)
    catalogs = []
    for path in sorted((ROOT / "locales").glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if "messages" in value:
            catalogs.append((value["locale"], value["messages"]))
    english = dict(catalogs)["en"]
    for source in (ROOT / "native/src").glob("*.cpp"):
        used = re.findall(r'(?:catalog::text|errorNotice)\("([^"\\]+)"', source.read_text(encoding="utf-8"))
        missing = set(used) - english.keys()
        if missing:
            raise ValueError(f"Unknown literal native catalog keys in {source.name}: {sorted(missing)}")
    lines = ["#pragma once", "#include <cstring>", "#include <string>",
             "#include <stdexcept>", "namespace cas::catalog {",
             "struct Entry { const char* language; const char* key; const char* value; };",
             "inline constexpr Entry entries[] = {"]
    for language, entries in catalogs:
        for key, value in sorted(entries.items()):
            lines.append("{" + ",".join(json.dumps(s, ensure_ascii=False)
                                      for s in (language, key, value["text"])) + "},")
    lines += ["};", "inline const char* text(const char* key, const char* language = \"en\") {",
              "for (const auto& e : entries) if (!std::strcmp(e.key,key) && !std::strcmp(e.language,language)) return e.value;",
              "if (std::strcmp(language,\"en\")) return text(key,\"en\");",
              "throw std::invalid_argument(\"Unknown native catalog key\");", "}",
              "inline std::string replace(std::string text, const std::string& token, const std::string& value) {",
              "std::size_t pos = 0; while ((pos = text.find(token,pos)) != std::string::npos) { text.replace(pos,token.size(),value); pos += value.size(); } return text;", "}", "}"]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    generate(parser.parse_args().output)
