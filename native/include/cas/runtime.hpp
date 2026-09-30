#pragma once
#include "cas/policy.hpp"
#include "cas/selection.hpp"
#include "cas/storage.hpp"
#include <atomic>
#include <cstdint>
#include <functional>
#include <mutex>
#include <thread>

namespace cas {
using Address = std::uintptr_t;
// Every native operation is explicit and replaceable by an owned-memory fixture.
// The production adapter binds these only after verifying the actual executable.
struct RuntimeServices {
    Address base{};
    std::function<void(Address, void*, std::size_t)> read;
    std::function<bool(Address,int)> owned, can_summon;
    std::function<void(Address,float,float,std::uint32_t)> placement;
    std::function<std::uint32_t()> dominant_hand;
    std::function<void(Address,int)> queue;
    std::function<void(Address,const std::string&)> notice;
    std::function<void(const char*)> log;
    std::function<double()> clock;
    std::function<bool()> allow_menu_change;
    selection::RandomRange random;
};

// All callback entry points are nonblocking. A concurrent gameplay callback
// closes the safety latch; it cannot race an in-progress native queue decision.
// Same-thread native reentry is allowed, with epoch/context checks before queue.
class Runtime final {
public:
    Runtime(RuntimeServices services, std::filesystem::path data_directory);
    void beforeLoad(bool network) noexcept;
    void afterLoad(Address common, bool network, bool result) noexcept;
    void afterExit(Address player) noexcept;
    void beforeEnter(Address player) noexcept;
    void afterPlayer(Address player, float dt) noexcept;
    void afterOwner(Address owner, float dt) noexcept;
    void beforeAction(Address menu, Address action, bool called_as_menu) noexcept;
    void afterAction(Address menu, Address action, bool called_as_menu, bool result) noexcept;
    void afterQueue(Address player, int slot) noexcept;
    bool caption(int role, char* output128) noexcept;
    bool capture(int role, std::uint64_t* revision) noexcept;
    bool change(int role, std::uint64_t revision) noexcept;
    bool enabled() const noexcept { return safe_.load(); }
private:
    struct Row { int slot; selection::Candidate candidate; std::optional<int> raw_habitat; };
    struct Context {
        int kind{}; std::optional<int> habitat;
        bool operator==(const Context& b) const { return kind == b.kind && habitat == b.habitat; }
    };
    struct Manual {
        Address menu{}, action{}, app{}, player{};
        bool called{}, candidate{}, accepted{};
        int slot{}; selection::Identity identity{};
        std::uint64_t epoch{}; std::string save_key; std::thread::id thread;
    };
    template<class T> T read(Address address) const {
        T result{}; services_.read(address, &result, sizeof result); return result;
    }
    template<class F> void guarded(F&& work) noexcept {
        if (!safe_.load()) return;
        std::unique_lock<std::recursive_mutex> lock(mutex_, std::try_to_lock);
        if (!lock.owns_lock()) { safe_ = false; return; }
        if (!safe_.load()) return;
        try { work(); } catch (...) { stop(); }
    }
    void stop() noexcept;
    void log(const char*) noexcept;
    void cancel();
    void invalidate();
    void resetProbe(double next = 0);
    Address appFor(Address player);
    selection::Identity identity(Address app, int slot) const;
    bool occupied(Address app, int slot) const;
    std::optional<int> petHabitat(Address app, int slot) const;
    std::optional<int> planetHabitat(Address app) const;
    std::vector<Row> roster(Address app) const;
    Context context(Address app, int location) const;
    bool reservedSafe(Address app, int slot) const;
    void restore(Address app);
    void arm(Address app);
    void prepareLoad(Address app, Address owner, Address player, float dt);
    bool choose(Address app, int location, std::vector<int> candidates);
    bool probe(Address app, Address owner, Address player, int location, double now);
    void tick(Address owner, float dt);
    void applyControls();
    std::string value(int role, const Preferences& prefs) const;
    std::string label(int role) const;
    RuntimeServices services_;
    SettingsStore settings_;
    SelectionStore favorites_;
    Preferences prefs_;
    std::optional<Preferences> requested_;
    bool settings_ok_ = true, persistence_ok_ = true, notice_disabled_ = false;
    std::atomic<bool> safe_{true};
    std::recursive_mutex mutex_;
    std::uint64_t revision_ = 0, epoch_ = 0;
    CompanionAutoSummonPolicy policy_;
    selection::CompanionSelector selector_;
    selection::HabitatRules rules_;
    Address app_{};
    std::string save_key_, notice_;
    std::optional<Favorite> favorite_;
    std::optional<selection::Identity> manual_identity_, pending_identity_;
    std::optional<Context> selection_context_;
    std::optional<Manual> manual_;
    bool manual_ok_ = true, load_pending_ = false, in_auto_ = false, owner_ticking_ = false;
    std::optional<double> primed_;
    double next_probe_ = 0;
    int probe_location_ = -1;
    std::uint64_t probe_physics_ = 0;
};
}
