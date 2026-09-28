// Offline driver for explicit temporary fixture paths. No game/user-directory
// discovery, background work, injection or runtime installation is performed.
#include "cas/storage.hpp"
#include "json.hpp"

#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {
using Json = nlohmann::json;

Json preferences_json(const cas::Preferences& value) {
    return {{"enabled", value.enabled}, {"locations", value.locations}, {"selection_mode", value.selection_mode},
            {"prefer_same_biome", value.prefer_same_biome}, {"rotate_companions", value.rotate_companions}};
}

cas::Preferences preferences(const Json& value) {
    if (!value.is_object() || value.size() != 5 || !value.contains("enabled") || !value.contains("locations") ||
        !value.contains("selection_mode") || !value.contains("prefer_same_biome") || !value.contains("rotate_companions") ||
        !value["enabled"].is_boolean() || !value["locations"].is_array() || !value["selection_mode"].is_string() ||
        !value["prefer_same_biome"].is_boolean() || !value["rotate_companions"].is_boolean())
        throw std::invalid_argument("Invalid preferences argument");
    cas::Preferences result;
    result.enabled = value["enabled"].get<bool>();
    result.locations.clear();
    for (const auto& location : value["locations"]) {
        if (!location.is_number_integer() || location < -1000 || location > 1000)
            throw std::invalid_argument("Invalid location argument");
        result.locations.push_back(location.get<int>());
    }
    result.selection_mode = value["selection_mode"].get<std::string>();
    result.prefer_same_biome = value["prefer_same_biome"].get<bool>();
    result.rotate_companions = value["rotate_companions"].get<bool>();
    return result;
}

std::string seed_hex(const cas::Favorite& favorite) {
    constexpr char digits[] = "0123456789abcdef";
    std::string result;
    for (const auto value : favorite.seed) { result += digits[value >> 4]; result += digits[value & 15]; }
    return result;
}

Json command(const Json& request) {
    const auto path = std::filesystem::u8path(request.at("path").get<std::string>());
    const auto operation = request.at("op").get<std::string>();
    cas::SettingsStore settings(path);
    cas::SelectionStore selections(path);
    if (operation == "settings_load") return preferences_json(settings.load_preferences());
    if (operation == "settings_enabled") return settings.load();
    if (operation == "settings_save") { settings.save_preferences(preferences(request.at("value"))); return nullptr; }
    if (operation == "settings_set_enabled") {
        if (!request.at("value").is_boolean()) throw std::invalid_argument("Invalid enabled argument");
        settings.save(request["value"].get<bool>()); return nullptr;
    }
    const auto key = request.at("key").get<std::string>();
    if (operation == "selection_load") {
        const auto result = selections.load(key);
        return result ? Json{{"seed", seed_hex(*result)}, {"slot", result->slot}} : Json(nullptr);
    }
    if (operation == "selection_forget") { selections.forget(key); return nullptr; }
    if (operation == "selection_remember") {
        const auto hex = request.at("seed").get<std::string>();
        if (hex.size() != 32 || hex.find_first_not_of("0123456789abcdef") != std::string::npos)
            throw std::invalid_argument("Invalid identity argument");
        if (!request.at("slot").is_number_integer() || request["slot"] < -1000 || request["slot"] > 1000)
            throw std::invalid_argument("Invalid slot argument");
        std::array<std::uint8_t, 16> seed{};
        const auto nibble = [](char c) { return c <= '9' ? c - '0' : c - 'a' + 10; };
        for (std::size_t i = 0; i < seed.size(); ++i)
            seed[i] = static_cast<std::uint8_t>((nibble(hex[i * 2]) << 4) | nibble(hex[i * 2 + 1]));
        selections.remember(key, seed, request["slot"].get<int>()); return nullptr;
    }
    throw std::invalid_argument("Unsupported command");
}
}  // namespace

int main() {
    std::string line;
    while (std::getline(std::cin, line)) {
        Json response;
        try { response = {{"ok", true}, {"result", command(Json::parse(line))}}; }
        catch (const cas::StorageError& error) { response = {{"ok", false}, {"error", "storage"}, {"message", error.what()}}; }
        catch (const std::exception& error) { response = {{"ok", false}, {"error", "argument"}, {"message", error.what()}}; }
        std::cout << response.dump() << std::endl;
    }
    return 0;
}
