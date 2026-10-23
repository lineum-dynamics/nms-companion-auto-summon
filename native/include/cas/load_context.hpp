#pragma once
#include <cstdint>
#include "cas/native_mapping.hpp"

namespace cas {
struct LoadContextObservation {
    // Bits: complete policy, image, application, receiver, state, vtable,
    // repeated identities. Legacy all-zero policy uses bit 7 instead.
    std::uint32_t checks{};
    bool accepted{};
};
// The reader is supplied by the host. Owned fixtures use synthetic bytes;
// production uses its bounded current-process reader. No native call or write.
template<class Read>
LoadContextObservation observe_local_load_context(std::uintptr_t base, const mapping::Build& build,
                                                 std::uintptr_t player_state, Read&& reader) noexcept {
    LoadContextObservation observation;
    const auto policy=build.local_load;
    if (!policy.state) {
        observation.accepted=!policy.current_state_cell && !policy.vtable && !policy.player_state_offset;
        if (observation.accepted) observation.checks=0x80;
        return observation;
    }
    if (!policy.current_state_cell || !policy.vtable || !policy.player_state_offset) return observation;
    observation.checks|=0x01;
    if (!base) return observation;
    observation.checks|=0x02;
    try {
        auto address_at=[&](std::uintptr_t address) {
            std::uintptr_t value{};
            reader(address,&value,sizeof value);
            return value;
        };
        const auto app_cell=base+build.globals.application;
        const auto current_cell=base+policy.current_state_cell;
        const auto expected_state=base+policy.state;
        const auto app=address_at(app_cell);
        if (app<0x10000 || app>0x7FFFFFFFFFFFULL-policy.player_state_offset) return observation;
        observation.checks|=0x04;
        if (player_state && player_state!=app+policy.player_state_offset) return observation;
        observation.checks|=0x08;
        const auto current=address_at(current_cell);
        if (current!=expected_state) return observation;
        observation.checks|=0x10;
        if (address_at(expected_state)!=base+policy.vtable) return observation;
        observation.checks|=0x20;
        if (address_at(app_cell)!=app || address_at(current_cell)!=current) return observation;
        observation.checks|=0x40;
        observation.accepted=true;
    } catch (...) {}
    return observation;
}

template<class Read>
bool applied_local_load_context(std::uintptr_t base, const mapping::Build& build,
                                std::uintptr_t player_state, Read&& reader) noexcept {
    return observe_local_load_context(base,build,player_state,reader).accepted;
}
}
