#pragma once
#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace cas {
inline constexpr std::array<unsigned char, 16> menu_marker{
    'C','A','S','_','M','E','N','U','_','V','1',0xA7,0x19,0x5C,0xE3,0x42};

// Exact port of quick_menu_native_guard.build_filter. This is a leaf entry,
// never a C++ detour: it must see the audited caller's original RDI and RSP.
std::vector<unsigned char> build_binding_filter(std::uintptr_t expected_return,
                                               std::uintptr_t original);

// Process-lifetime owner. The caller must pin the containing module and verify
// the complete NMS executable/profile before install. No unload/retry path.
class BindingGuard final {
public:
    BindingGuard() = default;
    BindingGuard(const BindingGuard&) = delete;
    BindingGuard& operator=(const BindingGuard&) = delete;
    bool install(std::uintptr_t base, const std::array<unsigned char,16>& file_prefix) noexcept;
    bool authorize(std::uintptr_t menu) noexcept;
    bool active() const noexcept { return active_.load(); }
private:
    bool verify() const noexcept;
    std::atomic_flag lock_ = ATOMIC_FLAG_INIT;
    std::atomic<bool> attempted_{false}, active_{false};
    std::uintptr_t base_{}, allocation_{}, original_{}, relay_{};
    std::uint32_t pid_{};
    std::vector<unsigned char> code_;
    std::array<unsigned char,16> target_bytes_{};
    std::array<unsigned char,19> original_bytes_{};
    std::array<unsigned char,14> relay_bytes_{};
};
}
