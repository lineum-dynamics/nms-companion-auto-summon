#pragma once

#include <array>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace cas {

class StorageError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

struct Preferences {
    bool enabled = true;
    std::vector<int> locations{2, 3, 14};
    std::string selection_mode = "by_habitat";
    bool prefer_same_biome = true;
    bool rotate_companions = true;
};

struct Favorite {
    std::array<std::uint8_t, 16> seed{};
    int slot = 0;
};

// Construction performs no I/O. Paths are supplied by the caller; these stores
// never locate game saves or choose a user-data directory. Use a single writer.
// Load migrates old preferences only in memory. Explicit writes validate the
// existing file again before an atomic replacement; invalid files are retained.
class SettingsStore {
public:
    explicit SettingsStore(std::filesystem::path path);
    [[nodiscard]] static Preferences defaults();
    [[nodiscard]] Preferences load_preferences() const;
    void save_preferences(const Preferences& preferences) const;
    [[nodiscard]] bool load() const;
    void save(bool enabled) const;

private:
    std::filesystem::path path_;
};

class SelectionStore {
public:
    explicit SelectionStore(std::filesystem::path path);
    [[nodiscard]] std::optional<Favorite> load(const std::string& save_key) const;
    void remember(const std::string& save_key,
                  const std::array<std::uint8_t, 16>& seed, int slot) const;
    void forget(const std::string& save_key) const;

private:
    std::filesystem::path path_;
};

}  // namespace cas
