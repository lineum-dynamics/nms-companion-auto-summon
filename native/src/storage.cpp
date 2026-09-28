#include "cas/storage.hpp"
#include "json.hpp"

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>

#include <algorithm>
#include <atomic>
#include <functional>
#include <map>
#include <set>
#include <utility>

namespace cas {
namespace {

using Json = nlohmann::json;
constexpr std::size_t settings_limit = 4096;
constexpr std::size_t selections_limit = 1024 * 1024;
constexpr std::size_t selections_count_limit = 256;

class Handle {
public:
    explicit Handle(HANDLE value = INVALID_HANDLE_VALUE) : value_(value) {}
    ~Handle() { if (value_ != INVALID_HANDLE_VALUE) CloseHandle(value_); }
    Handle(const Handle&) = delete;
    Handle& operator=(const Handle&) = delete;
    [[nodiscard]] HANDLE get() const { return value_; }
    void close() { if (value_ != INVALID_HANDLE_VALUE) CloseHandle(value_); value_ = INVALID_HANDLE_VALUE; }
private:
    HANDLE value_;
};

[[noreturn]] void io_error(const char* operation) {
    throw StorageError(std::string(operation) + " (Windows error " + std::to_string(GetLastError()) + ")");
}

// A strict scalar-value count, not a UTF-8 byte count or UTF-16 code-unit count.
std::size_t utf8_length(const std::string& value) {
    std::size_t count = 0;
    for (std::size_t i = 0; i < value.size(); ++count) {
        const auto first = static_cast<unsigned char>(value[i++]);
        std::uint32_t point = first;
        unsigned extra = 0;
        std::uint32_t minimum = 0;
        if (first < 0x80) continue;
        if (first >= 0xc2 && first <= 0xdf) { point = first & 0x1f; extra = 1; minimum = 0x80; }
        else if (first >= 0xe0 && first <= 0xef) { point = first & 0x0f; extra = 2; minimum = 0x800; }
        else if (first >= 0xf0 && first <= 0xf4) { point = first & 7; extra = 3; minimum = 0x10000; }
        else throw std::invalid_argument("save_key must contain valid UTF-8");
        if (extra > value.size() - i) throw std::invalid_argument("save_key must contain valid UTF-8");
        while (extra--) {
            const auto next = static_cast<unsigned char>(value[i++]);
            if ((next & 0xc0) != 0x80) throw std::invalid_argument("save_key must contain valid UTF-8");
            point = (point << 6) | (next & 0x3f);
        }
        if (point < minimum || point > 0x10ffff || (point >= 0xd800 && point <= 0xdfff))
            throw std::invalid_argument("save_key must contain valid UTF-8");
    }
    return count;
}

void validate_key(const std::string& value) {
    const auto length = utf8_length(value);
    if (length == 0 || length > 256)
        throw std::invalid_argument("save_key must contain 1 to 256 Unicode characters");
}

void validate_slot(int value) {
    if (value < 0 || value > 29) throw std::invalid_argument("slot must be from 0 to 29");
}

bool keys_are(const Json& value, std::initializer_list<const char*> keys) {
    if (!value.is_object() || value.size() != keys.size()) return false;
    for (const auto key : keys) if (!value.contains(key)) return false;
    return true;
}

bool integer_is(const Json& value, std::int64_t expected) {
    return value.is_number_integer() && value == Json(expected);
}

Preferences validate_preferences(Preferences value) {
    if (value.selection_mode != "last_manual" && value.selection_mode != "random" && value.selection_mode != "by_habitat")
        throw std::invalid_argument("Preferences selection mode is unsupported");
    std::sort(value.locations.begin(), value.locations.end());
    if (std::adjacent_find(value.locations.begin(), value.locations.end()) != value.locations.end())
        throw std::invalid_argument("Preferences locations must not contain duplicate IDs");
    for (const auto location : value.locations)
        if (location != 2 && location != 3 && location != 14)
            throw std::invalid_argument("Preferences location is unsupported");
    return value;
}

Json preferences_json(const Preferences& value) {
    return {{"enabled", value.enabled}, {"locations", value.locations},
            {"selection_mode", value.selection_mode}, {"prefer_same_biome", value.prefer_same_biome},
            {"rotate_companions", value.rotate_companions}};
}

Preferences settings_document(Json value) {
    if (!value.is_object() || !value.contains("schema") || !value["schema"].is_number_integer())
        throw StorageError("Settings have an invalid document structure");
    const bool one = integer_is(value["schema"], 1), two = integer_is(value["schema"], 2);
    const bool three = integer_is(value["schema"], 3), four = integer_is(value["schema"], 4);
    if (!one && !two && !three && !four) throw StorageError("Settings use an unsupported schema");
    if (one) {
        if (!keys_are(value, {"schema", "enabled"}) || !value["enabled"].is_boolean())
            throw StorageError("Legacy settings have an invalid document structure");
        Preferences result;
        result.enabled = value["enabled"].get<bool>();
        result.selection_mode = "last_manual";
        result.rotate_companions = false;
        return result;
    }
    if (two) {
        if (!keys_are(value, {"schema", "enabled", "locations", "selection_mode"}))
            throw StorageError("Legacy settings have an invalid document structure");
        value["prefer_same_biome"] = true;
    }
    if (two || three) {
        if (!keys_are(value, {"schema", "enabled", "locations", "selection_mode", "prefer_same_biome"}) ||
            !value["selection_mode"].is_string() ||
            (value["selection_mode"] != "last_manual" && value["selection_mode"] != "random"))
            throw StorageError("Legacy settings have an invalid document structure");
        value["rotate_companions"] = false;
    }
    if (!keys_are(value, {"schema", "enabled", "locations", "selection_mode", "prefer_same_biome", "rotate_companions"}) ||
        !value["enabled"].is_boolean() || !value["prefer_same_biome"].is_boolean() ||
        !value["rotate_companions"].is_boolean() || !value["locations"].is_array() || !value["selection_mode"].is_string())
        throw StorageError("Settings preferences have an invalid structure or type");
    Preferences result;
    result.enabled = value["enabled"].get<bool>();
    result.prefer_same_biome = value["prefer_same_biome"].get<bool>();
    result.rotate_companions = value["rotate_companions"].get<bool>();
    result.selection_mode = value["selection_mode"].get<std::string>();
    result.locations.clear();
    for (const auto& location : value["locations"]) {
        if (!integer_is(location, 2) && !integer_is(location, 3) && !integer_is(location, 14))
            throw StorageError("Settings location must be an allowed integer ID");
        result.locations.push_back(location.get<int>());
    }
    try { return validate_preferences(std::move(result)); }
    catch (const std::invalid_argument& error) { throw StorageError(error.what()); }
}

std::string seed_hex(const std::array<std::uint8_t, 16>& seed) {
    constexpr char hex[] = "0123456789abcdef";
    std::string result;
    result.reserve(32);
    for (const auto byte : seed) { result += hex[byte >> 4]; result += hex[byte & 15]; }
    return result;
}

Favorite favorite_document(const Json& value) {
    if (!keys_are(value, {"seed", "slot"}) || !value["seed"].is_string() || !value["slot"].is_number_integer())
        throw StorageError("Selection file contains an invalid pet selection");
    const auto seed = value["seed"].get<std::string>();
    if (seed.size() != 32 || seed.find_first_not_of("0123456789abcdef") != std::string::npos)
        throw StorageError("Selection file contains an invalid pet seed");
    if (value["slot"] < 0 || value["slot"] > 29)
        throw StorageError("Selection file contains an invalid pet slot");
    Favorite result;
    result.slot = value["slot"].get<int>();
    const auto nibble = [](char value) { return value <= '9' ? value - '0' : value - 'a' + 10; };
    for (std::size_t i = 0; i < result.seed.size(); ++i)
        result.seed[i] = static_cast<std::uint8_t>((nibble(seed[i * 2]) << 4) | nibble(seed[i * 2 + 1]));
    return result;
}

Json selections_document(Json value) {
    if (!keys_are(value, {"schema", "selections"}) || !integer_is(value["schema"], 1) ||
        !value["selections"].is_object() || value["selections"].size() > selections_count_limit)
        throw StorageError("Selection file has an invalid document structure");
    for (const auto& entry : value["selections"].items()) {
        try { validate_key(entry.key()); }
        catch (const std::invalid_argument&) { throw StorageError("Selection file contains an invalid save identity"); }
        (void)favorite_document(entry.value());
    }
    return value;
}

Json parse_json(const std::string& raw) {
    // Python's UTF-8 JSON reference rejects a BOM, whereas the JSON library
    // otherwise tolerates one. Duplicate keys must be rejected at every level.
    if (raw.size() >= 3 && raw.compare(0, 3, "\xef\xbb\xbf") == 0)
        throw StorageError("Store is not valid UTF-8 JSON");
    std::vector<std::set<std::string>> objects;
    auto callback = [&objects](int depth, Json::parse_event_t event, Json& parsed) {
        if (depth > 32) throw StorageError("Store JSON nesting is excessive");
        if (event == Json::parse_event_t::object_start) objects.emplace_back();
        if (event == Json::parse_event_t::key) {
            if (objects.empty() || !objects.back().insert(parsed.get<std::string>()).second)
                throw StorageError("Store contains duplicate JSON keys");
        }
        if (event == Json::parse_event_t::object_end) objects.pop_back();
        return true;
    };
    try { return Json::parse(raw, callback); }
    catch (const Json::exception&) { throw StorageError("Store is not valid UTF-8 JSON"); }
}

std::optional<std::string> read_raw(const std::filesystem::path& path, std::size_t limit) {
    Handle file(CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                            nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr));
    if (file.get() == INVALID_HANDLE_VALUE) {
        const auto error = GetLastError();
        if (error == ERROR_FILE_NOT_FOUND || error == ERROR_PATH_NOT_FOUND) return std::nullopt;
        io_error("Cannot read store");
    }
    std::string raw(limit + 1, '\0');
    DWORD received = 0;
    if (!ReadFile(file.get(), raw.data(), static_cast<DWORD>(raw.size()), &received, nullptr))
        io_error("Cannot read store");
    if (received > limit) throw StorageError("Store exceeds its byte limit");
    raw.resize(received);
    return raw;
}

Preferences read_settings(const std::filesystem::path& path) {
    const auto raw = read_raw(path, settings_limit);
    return raw ? settings_document(parse_json(*raw)) : Preferences{};
}

Json read_selections(const std::filesystem::path& path) {
    const auto raw = read_raw(path, selections_limit);
    return raw ? selections_document(parse_json(*raw)) : Json{{"schema", 1}, {"selections", Json::object()}};
}

void atomic_write(const std::filesystem::path& path, const Json& document, std::size_t limit,
                  const std::function<void(const std::string&)>& validate_existing) {
    const auto raw = document.dump(2, ' ', true) + "\n";
    if (raw.size() > limit) throw StorageError("Store would exceed its byte limit");
    const auto before = read_raw(path, limit);
    if (before) validate_existing(*before);
    std::filesystem::path temporary;
    try {
        const auto parent = path.has_parent_path() ? path.parent_path() : std::filesystem::path(L".");
        std::filesystem::create_directories(parent);
        static std::atomic<unsigned long long> serial{0};
        // CREATE_NEW prevents clobbering another writer's temporary file. The
        // temporary is on the destination volume so the replacement is atomic.
        HANDLE raw_handle = INVALID_HANDLE_VALUE;
        for (unsigned attempt = 0; attempt < 64; ++attempt) {
            const auto candidate = parent / (L"." + path.filename().wstring() + L"." + std::to_wstring(GetCurrentProcessId()) +
                                              L"." + std::to_wstring(++serial) + L".tmp");
            raw_handle = CreateFileW(candidate.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, nullptr);
            if (raw_handle != INVALID_HANDLE_VALUE) { temporary = candidate; break; }
            if (GetLastError() != ERROR_FILE_EXISTS && GetLastError() != ERROR_ALREADY_EXISTS)
                io_error("Cannot create temporary store");
        }
        if (raw_handle == INVALID_HANDLE_VALUE) io_error("Cannot create unique temporary store");
        Handle target(raw_handle);
        DWORD written = 0;
        if (!WriteFile(target.get(), raw.data(), static_cast<DWORD>(raw.size()), &written, nullptr) || written != raw.size())
            io_error("Cannot write temporary store");
        if (!FlushFileBuffers(target.get())) io_error("Cannot flush temporary store");
        target.close();
        // Re-read rather than trusting a cached document. A malformed or changed
        // destination discovered here is retained, and the temporary is removed.
        const auto latest = read_raw(path, limit);
        if (latest) validate_existing(*latest);
        if (latest != before) throw StorageError("Store changed during write; retry with a single writer");
        if (latest) {
            if (!ReplaceFileW(path.c_str(), temporary.c_str(), nullptr, 0, nullptr, nullptr))
                io_error("Cannot atomically replace store");
        } else if (!MoveFileExW(temporary.c_str(), path.c_str(), MOVEFILE_WRITE_THROUGH)) {
            // No REPLACE_EXISTING: a new unexpected destination is preserved.
            io_error("Cannot atomically create store");
        }
        temporary.clear();
    } catch (const StorageError&) {
        if (!temporary.empty()) DeleteFileW(temporary.c_str());
        throw;
    } catch (const std::exception& error) {
        if (!temporary.empty()) DeleteFileW(temporary.c_str());
        throw StorageError(std::string("Cannot atomically write store: ") + error.what());
    }
}

void write_settings(const std::filesystem::path& path, const Preferences& preferences) {
    auto document = preferences_json(preferences);
    document["schema"] = 4;
    atomic_write(path, document, settings_limit, [](const auto& raw) { (void)settings_document(parse_json(raw)); });
}

void write_selections(const std::filesystem::path& path, const Json& document) {
    (void)selections_document(document);
    atomic_write(path, document, selections_limit, [](const auto& raw) { (void)selections_document(parse_json(raw)); });
}

}  // namespace

SettingsStore::SettingsStore(std::filesystem::path path) : path_(std::move(path)) {}
Preferences SettingsStore::defaults() { return {}; }
Preferences SettingsStore::load_preferences() const { return read_settings(path_); }
void SettingsStore::save_preferences(const Preferences& preferences) const {
    const auto validated = validate_preferences(preferences);
    (void)read_settings(path_);
    write_settings(path_, validated);
}
bool SettingsStore::load() const { return load_preferences().enabled; }
void SettingsStore::save(bool enabled) const {
    auto preferences = read_settings(path_);
    preferences.enabled = enabled;
    write_settings(path_, preferences);
}

SelectionStore::SelectionStore(std::filesystem::path path) : path_(std::move(path)) {}
std::optional<Favorite> SelectionStore::load(const std::string& save_key) const {
    validate_key(save_key);
    const auto document = read_selections(path_);
    const auto& selections = document["selections"];
    const auto found = selections.find(save_key);
    return found == selections.end() ? std::nullopt : std::optional<Favorite>(favorite_document(*found));
}
void SelectionStore::remember(const std::string& save_key, const std::array<std::uint8_t, 16>& seed, int slot) const {
    validate_key(save_key);
    validate_slot(slot);
    auto document = read_selections(path_);
    document["selections"][save_key] = {{"seed", seed_hex(seed)}, {"slot", slot}};
    write_selections(path_, document);
}
void SelectionStore::forget(const std::string& save_key) const {
    validate_key(save_key);
    auto document = read_selections(path_);
    if (document["selections"].erase(save_key) != 0) write_selections(path_, document);
}

}  // namespace cas
