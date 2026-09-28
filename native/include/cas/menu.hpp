#pragma once
#include <cstdint>
#include "cas/binding_guard.hpp"

namespace cas {
// Called under the menu's nonblocking owner lock. Preference methods must use
// nonblocking synchronization, copy owned state and never call native functions.
// change() queues a revision-checked request for the local Player.Update path.
struct MenuCallbacks {
    void* context{};
    bool (*caption)(void*, int role, char* output128){}; // -1 parent, 0..6 setting
    bool (*capture)(void*, int role, std::uint64_t* revision){};
    bool (*change)(void*, int role, std::uint64_t revision){};
    void (*log)(void*, const char* reason){};
};
using MenuAppend = void* (*)(void* header, void* incoming);
using MenuConstruct = void* (*)(void*, std::uint32_t, std::int32_t, bool, bool);
using MenuSelect = void (*)(void* depth_field, std::int32_t depth, std::int32_t index);

// Owns no hooks. A single runtime detour invokes before/original/after in order,
// forwarding every argument/result unchanged (including TriggerAction).
// The Impl is intentionally pinned through process exit, as are icon records.
class MenuAdapter final {
public:
    MenuAdapter() = default;
    MenuAdapter(const MenuAdapter&) = delete;
    MenuAdapter& operator=(const MenuAdapter&) = delete;
    bool initialize(std::uintptr_t base, BindingGuard* guard,
                    MenuAppend append_original, MenuCallbacks callbacks) noexcept;
    void beforeBuilder(void* menu, void* render) noexcept;
    void afterBuilder(void* menu, void* render) noexcept;
    void beforeAppend(void* header, void* incoming) noexcept;
    void afterLabel(void* menu, void* output128) noexcept;
    void beforeTrigger(void* menu, void* action, bool called_as_menu) noexcept;
    void afterTrigger(void* menu, void* action, bool called_as_menu, bool result) noexcept;
    void beforeConfirmation(void* menu) noexcept;
    void afterConfirmation(void* menu, bool result) noexcept;
    void afterResources(void* menu) noexcept;
    std::uint32_t notificationIcon() noexcept;
    bool stopped() const noexcept;
#ifdef CAS_MENU_FIXTURE
    // Owned-buffer test seam is absent from production compilation.
    bool initializeFixture(MenuConstruct, MenuAppend, MenuSelect, MenuCallbacks) noexcept;
#endif
private:
    struct Impl;
    Impl* impl_{};
};
}
