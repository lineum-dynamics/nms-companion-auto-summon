#include "cas/policy.hpp"

#include <cmath>
#include <stdexcept>
#include <string>

namespace cas {

CompanionAutoSummonPolicy::CompanionAutoSummonPolicy(
    double delay_seconds, std::optional<double> expiry_seconds)
    : delay_(finite_number(delay_seconds, "delay_seconds")),
      expiry_(expiry_seconds) {
    if (expiry_) {
        finite_number(*expiry_, "expiry_seconds");
    }
    if (delay_ < 0.0) {
        throw std::invalid_argument("delay_seconds must be non-negative");
    }
    if (expiry_ && *expiry_ <= 0.0) {
        throw std::invalid_argument("expiry_seconds must be positive");
    }
    reset();
}

double CompanionAutoSummonPolicy::finite_number(double value, const char* name) {
    if (!std::isfinite(value)) {
        throw std::invalid_argument(std::string(name) + " must be a finite number");
    }
    return value;
}

void CompanionAutoSummonPolicy::validate_slot(int slot) {
    if (slot < 0 || slot >= 30) {
        throw std::invalid_argument("slot must be an integer from 0 through 29");
    }
}

void CompanionAutoSummonPolicy::cancel_pending() noexcept {
    ejected_at_.reset();
    stable_since_.reset();
    exit_slot_.reset();
    in_flight_ = false;
}

std::optional<double> CompanionAutoSummonPolicy::observe_time(double now) {
    if (!std::isfinite(now)) {
        cancel_pending();
        finite_number(now, "now");
    }
    const bool reversed_time = last_time_ && now < *last_time_;
    last_time_ = now;
    if (reversed_time) {
        cancel_pending();
        return std::nullopt;
    }
    return now;
}

void CompanionAutoSummonPolicy::remember(int slot) {
    validate_slot(slot);
    slot_ = slot;
    cancel_pending();
}

void CompanionAutoSummonPolicy::eject(double now, bool random_selection) {
    const auto timestamp = observe_time(now);
    if (!timestamp) {
        return;
    }
    cancel_pending();
    if (slot_ || random_selection) {
        ejected_at_ = timestamp;
        exit_slot_ = random_selection ? std::nullopt : slot_;
    }
}

bool CompanionAutoSummonPolicy::select_for_exit(int slot) {
    validate_slot(slot);
    if (!pending()) {
        return false;
    }
    if (exit_slot_) {
        throw std::invalid_argument("this exit already has a companion");
    }
    exit_slot_ = slot;
    return true;
}

void CompanionAutoSummonPolicy::enter_ship() noexcept {
    cancel_pending();
}

void CompanionAutoSummonPolicy::reset() noexcept {
    slot_.reset();
    last_time_.reset();
    cancel_pending();
}

std::optional<int> CompanionAutoSummonPolicy::last_slot() const noexcept {
    return slot_;
}

bool CompanionAutoSummonPolicy::pending() const noexcept {
    return ejected_at_.has_value();
}

std::optional<int> CompanionAutoSummonPolicy::pending_slot() const noexcept {
    return exit_slot_;
}

bool CompanionAutoSummonPolicy::resolve(bool accepted) noexcept {
    if (!in_flight_) {
        return false;
    }
    if (accepted) {
        cancel_pending();
    } else {
        in_flight_ = false;
    }
    return true;
}

std::optional<int> CompanionAutoSummonPolicy::tick(
    double now,
    bool on_foot_in_summon_location,
    int active_pet,
    int native_pending_pet,
    bool eligible) {
    const auto timestamp = observe_time(now);
    if (!timestamp || !ejected_at_) {
        return std::nullopt;
    }
    if (expiry_ && *timestamp - *ejected_at_ >= *expiry_) {
        cancel_pending();
        return std::nullopt;
    }
    if (active_pet >= 0 || native_pending_pet >= 0) {
        cancel_pending();
        return std::nullopt;
    }
    if (!on_foot_in_summon_location) {
        stable_since_.reset();
        return std::nullopt;
    }
    if (!stable_since_) {
        stable_since_ = timestamp;
    }
    if (*timestamp - *stable_since_ < delay_) {
        return std::nullopt;
    }
    if (!eligible || active_pet != -1 || native_pending_pet != -1 ||
        !exit_slot_ || in_flight_) {
        return std::nullopt;
    }
    in_flight_ = true;
    return exit_slot_;
}

}  // namespace cas
