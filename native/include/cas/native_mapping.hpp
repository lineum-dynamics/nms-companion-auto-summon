#pragma once
#include <array>
#include <cstdint>
#include <string_view>
#include "compatibility_profile.hpp"

namespace cas::mapping {
struct Functions {
    std::uint32_t queue_pet, player_update, owner_update, ship_eject, enter_cockpit;
    std::uint32_t load_player_state, trigger_action, build_menu, label_menu, append_menu;
    std::uint32_t confirm_menu, load_menu_resources, position_observer;
    std::uint32_t can_summon, owned_pet_eligible, refresh_placement, dominant_hand;
    std::uint32_t add_timed_message, construct_menu_item, select_menu_item;
    std::uint32_t load_texture, retain_resource, get_button;
};
struct Globals {
    std::uint32_t application, resource_manager, retain_manager, interaction_range;
};
struct LocalLoadPolicy {
    // All zero for the retained 7.05 policy. The 7.06 candidate additionally
    // requires the applied FSM state and its exact vtable/receiver identity.
    std::uint32_t current_state_cell, state, vtable, player_state_offset;
};
struct Build {
    std::string_view steam_build, exe_sha256;
    bool activation_approved; // Controlled candidate activation, not release/live acceptance.
    Functions functions;
    Globals globals;
    std::uint32_t binding_return;
    std::array<std::uint32_t,3> position_returns;
    LocalLoadPolicy local_load;
};

}

// Generated from native_mappings.json by the native build tool.
#include "native_mapping_profile.hpp"

static_assert(cas::mapping::target.steam_build == cas::profile::steam_build &&
              cas::mapping::target.exe_sha256 == cas::profile::exe_sha256,
              "Native mapping differs from the exact executable profile");
