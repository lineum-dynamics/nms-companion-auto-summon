#pragma once

#include <optional>

namespace cas {

// Offline decision policy. The caller supplies observations and resolves the
// returned request; this class does not read game memory or perform a summon.
class CompanionAutoSummonPolicy {
public:
    explicit CompanionAutoSummonPolicy(
        double delay_seconds = 1.5,
        std::optional<double> expiry_seconds = std::nullopt);

    // Replacing the manual choice cancels any current opportunity.
    void remember(int slot);
    void eject(double now, bool random_selection = false);
    bool select_for_exit(int slot);
    void enter_ship() noexcept;
    void reset() noexcept;

    [[nodiscard]] std::optional<int> last_slot() const noexcept;
    [[nodiscard]] bool pending() const noexcept;
    [[nodiscard]] std::optional<int> pending_slot() const noexcept;

    // Rejection allows the same choice to be retried; acceptance finishes it.
    bool resolve(bool accepted) noexcept;

    // Only an explicit eject opportunity can return a slot. Observing an absent
    // companion cannot create an opportunity. Both native indices must be -1.
    std::optional<int> tick(
        double now,
        bool on_foot_in_summon_location,
        int active_pet,
        int native_pending_pet,
        bool eligible);

private:
    static double finite_number(double value, const char* name);
    static void validate_slot(int slot);
    void cancel_pending() noexcept;
    std::optional<double> observe_time(double now);

    double delay_;
    std::optional<double> expiry_;
    std::optional<int> slot_;
    std::optional<double> last_time_;
    std::optional<double> ejected_at_;
    std::optional<double> stable_since_;
    std::optional<int> exit_slot_;
    bool in_flight_ = false;
};

}  // namespace cas
