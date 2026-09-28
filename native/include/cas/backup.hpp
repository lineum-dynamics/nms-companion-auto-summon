#pragma once

#include <cstdint>
#include <filesystem>
#include <stdexcept>

namespace cas {

struct BackupError : std::runtime_error { using std::runtime_error::runtime_error; };
struct BackupReport {
    std::filesystem::path destination;
    std::uint64_t files = 0;
    std::uint64_t bytes = 0;
    bool saves_present = false;
    bool preferences_present = false;
};

// Explicit local paths only. Never discovers, edits, restores or removes saves.
// The destination must not exist; its parent must already exist. Source roots
// may be absent for a new player. Existing files are held read-only with writes
// and deletion denied until byte/hash verification and a second listing finish.
// This is a before-native-hooks snapshot, not a claim that the game is closed.
// Any incomplete destination is retained with its INCOMPLETE marker.
BackupReport verified_pre_activation_backup(const std::filesystem::path& save_root,
    const std::filesystem::path& preference_root, const std::filesystem::path& destination);

}  // namespace cas
