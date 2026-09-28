#include "cas/runtime.hpp"
#include "catalog.hpp"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <set>
#include <stdexcept>

namespace cas {
namespace {
constexpr Address app_rva = 0x6E7AAE8, local_player = 0x71C690, location_offset = 0x57A584;
constexpr Address active_pet = 0x29A1C0, queued_pet = 0x6010, pet_table = 0xE10D0;
constexpr Address pet_stride = 0x24A0, pet_seed = 0x2330, pet_birth = 0x23C0;
constexpr Address pet_resource = 0x2370, pet_biome = 0x2480, preview = 0x1B9300, emote = 0x1B937D;
bool supported(int location) { return location == 2 || location == 3 || location == 14; }
bool allowed(const Preferences& prefs, int location) {
    return std::find(prefs.locations.begin(), prefs.locations.end(), location) != prefs.locations.end();
}
bool concrete(int biome) { return biome >= 0 && biome <= 15 && biome != 11; }
}
Runtime::Runtime(RuntimeServices services, std::filesystem::path data)
    : services_(std::move(services)), settings_(data / L"settings.json"),
      favorites_(data / L"state.json"), selector_(services_.random), rules_(selection::default_habitat_rules()) {
    try { prefs_ = settings_.load_preferences(); }
    catch (const StorageError&) { prefs_.enabled = false; settings_ok_ = false; log("Settings unavailable; automation starts OFF, existing file retained"); }
    log("Native runtime initialized; no summon opportunity until local save load or ship exit");
}
void Runtime::log(const char* text) noexcept { try { if (services_.log) services_.log(text); } catch (...) {} }
void Runtime::stop() noexcept {
    safe_ = false; policy_.reset(); selector_.reset(); manual_.reset(); load_pending_ = false;
    log("Native automation stopped after a runtime error; restart required");
}
void Runtime::invalidate() { ++epoch_; manual_.reset(); }
void Runtime::resetProbe(double next) { primed_.reset(); probe_location_ = -1; probe_physics_ = 0; next_probe_ = next; }
void Runtime::cancel() { policy_.enter_ship(); selector_.cancel(); pending_identity_.reset(); selection_context_.reset(); resetProbe(); }
Address Runtime::appFor(Address player) {
    const auto app = read<Address>(services_.base + app_rva);
    if (!app) {
        invalidate(); load_pending_ = false; cancel(); policy_.reset(); selector_.reset();
        app_ = 0; manual_identity_.reset(); save_key_.clear(); favorite_.reset(); notice_.clear();
        return 0;
    }
    if (app != app_) {
        if (app_) { invalidate(); load_pending_ = false; save_key_.clear(); favorite_.reset(); notice_.clear(); }
        cancel(); policy_.reset(); selector_.reset(); manual_identity_.reset(); app_ = app;
    }
    return player == app + local_player ? app : 0;
}
selection::Identity Runtime::identity(Address app, int slot) const {
    if (slot < 0 || slot >= 30) throw std::invalid_argument("Invalid pet slot");
    selection::Identity result{};
    const auto entry = app + pet_table + slot * pet_stride;
    services_.read(entry + pet_seed, result.data(), 8);
    services_.read(entry + pet_birth, result.data() + 8, 8);
    return result;
}
bool Runtime::occupied(Address app, int slot) const {
    if (slot < 0 || slot >= 30) return false;
    return read<std::uint32_t>(app + pet_table + slot * pet_stride + pet_resource) != 0;
}
std::optional<int> Runtime::petHabitat(Address app, int slot) const {
    const auto biome = read<std::uint32_t>(app + pet_table + slot * pet_stride + pet_biome);
    return biome <= 15 && concrete(static_cast<int>(biome)) ? std::optional<int>(biome) : std::nullopt;
}
std::optional<int> Runtime::planetHabitat(Address app) const {
    const auto solar = read<Address>(app + 0x71AF70);
    if (!solar) return {};
    const auto count = read<int>(solar + 0x2544), index = read<int>(solar + 0x5196D0);
    if (count < 1 || count > 6 || index < 0 || index >= count) return {};
    const auto planet = solar + index * 0xD9170;
    const auto biome = read<std::uint32_t>(planet + 0x6148), subtype = read<std::uint32_t>(planet + 0x614C);
    if (biome > 15 || !concrete(static_cast<int>(biome)) || subtype > 31) return {};
    if (subtype == 25) return 12;
    if (subtype == 26) return 13;
    return biome >= 8 && biome <= 10 ? 7 : static_cast<int>(biome);
}
std::vector<Runtime::Row> Runtime::roster(Address app) const {
    auto snapshot = [&] {
        std::vector<Row> rows;
        for (int slot = 0; slot < 30; ++slot)
            if (occupied(app,slot)) {
                const auto id = identity(app,slot); const auto habitat = petHabitat(app,slot);
                rows.push_back({slot,selection::Candidate(id,habitat),habitat});
            }
        return rows;
    };
    auto first = snapshot(), second = snapshot();
    if (first.size() != second.size()) throw selection::SelectionError("Roster changed");
    std::set<selection::Identity> identities;
    for (std::size_t i = 0; i < first.size(); ++i) {
        if (first[i].slot != second[i].slot || first[i].candidate.identity != second[i].candidate.identity ||
            first[i].raw_habitat != second[i].raw_habitat)
            throw selection::SelectionError("Roster changed");
        if (!identities.insert(first[i].candidate.identity).second)
            throw selection::AmbiguousIdentityError("Duplicate companion identity");
    }
    return first;
}
Runtime::Context Runtime::context(Address app, int location) const {
    if (prefs_.selection_mode == "random") return {0,{}};
    if (prefs_.selection_mode == "by_habitat" && location == 3) return {1,selection::normalize_habitat(planetHabitat(app))};
    return {2,{}};
}
bool Runtime::reservedSafe(Address app, int slot) const {
    try {
        if (!pending_identity_ || !selector_.pending() || selector_.pending()->identity != *pending_identity_) return false;
        const auto rows = roster(app); const auto location = read<int>(app + location_offset);
        if (supported(location) && (!selection_context_ || !(context(app,location) == *selection_context_))) return false;
        for (const auto& row : rows) if (row.candidate.identity == *pending_identity_) {
            if (row.slot != slot) return false;
            return prefs_.selection_mode != "by_habitat" || location != 3 ||
                (selection_context_ && rules_.group(selection_context_->habitat,row.candidate.habitat).has_value());
        }
    } catch (...) { return false; }
    return false;
}
void Runtime::restore(Address app) {
    if (policy_.last_slot()) {
        if (manual_identity_ && identity(app,*policy_.last_slot()) == *manual_identity_) return;
        cancel(); policy_.reset(); manual_identity_.reset();
    }
    if (save_key_.empty() || !favorite_) return;
    std::vector<int> matches;
    for (int slot = 0; slot < 30; ++slot)
        if (occupied(app,slot) && identity(app,slot) == favorite_->seed) matches.push_back(slot);
    if (matches.size() == 1) { policy_.remember(matches[0]); manual_identity_ = favorite_->seed; }
}
void Runtime::arm(Address app) {
    restore(app); cancel(); const bool random = prefs_.selection_mode != "last_manual";
    policy_.eject(services_.clock(),random);
    if (policy_.pending()) { pending_identity_ = random ? std::nullopt : manual_identity_; log("Automatic summon opportunity armed"); }
}
void Runtime::beforeLoad(bool network) noexcept {
    guarded([&] { if (!network) {
        invalidate(); load_pending_ = false; cancel(); policy_.reset(); selector_.reset();
        app_ = 0; manual_identity_.reset(); save_key_.clear(); favorite_.reset(); notice_.clear();
    }});
}
void Runtime::afterLoad(Address common, bool network, bool result) noexcept {
    guarded([&] {
        if (network || !result || !common) return;
        const auto id = read<std::uint64_t>(common + 0x8980);
        load_pending_ = prefs_.enabled;
        if (!id) return;
        char key[32]{}; std::snprintf(key,sizeof key,"nms:%016llx",static_cast<unsigned long long>(id)); save_key_ = key;
        if (persistence_ok_) try { favorite_ = favorites_.load(save_key_); }
        catch (const StorageError&) { persistence_ok_ = false; log("Favorite file unavailable; preserved unchanged"); }
        log("Successful local save load recorded; awaiting native readiness");
    });
}
void Runtime::afterExit(Address player) noexcept {
    guarded([&] { if (!prefs_.enabled) return; if (const auto app = appFor(player)) { invalidate(); load_pending_ = false; arm(app); } });
}
void Runtime::beforeEnter(Address player) noexcept {
    guarded([&] { if (appFor(player)) { invalidate(); load_pending_ = false; cancel(); } });
}
void Runtime::prepareLoad(Address app, Address owner, Address player, float dt) {
    if (!load_pending_) return;
    if (read<int>(owner+preview) != -1 || read<std::uint8_t>(owner+emote) ||
        read<int>(app+active_pet) != -1 || read<int>(player+queued_pet) != -1 || policy_.pending()) {
        load_pending_ = false; resetProbe(); return;
    }
    const auto location = read<int>(app+location_offset);
    if (supported(location) && !allowed(prefs_,location)) { load_pending_ = false; resetProbe(); return; }
    if (!std::isfinite(dt) || dt <= 0 || !supported(location)) { resetProbe(); return; }
    if (prefs_.selection_mode == "last_manual") {
        if (!favorite_ && !policy_.last_slot()) { load_pending_ = false; resetProbe(); return; }
        const auto now = services_.clock(); if (!std::isfinite(now)) throw std::runtime_error("Invalid clock");
        if (now < next_probe_) return;
        next_probe_ = now + .5; restore(app); if (!policy_.last_slot()) return;
    }
    load_pending_ = false; arm(app);
}
bool Runtime::choose(Address app, int location, std::vector<int> candidates) {
    auto preferred = [&] {
        if (prefs_.selection_mode != "random" || !prefs_.prefer_same_biome || location != 3) return;
        try {
            const auto biome = planetHabitat(app); if (!biome) return;
            std::vector<int> matches;
            for (const auto slot : candidates) if (petHabitat(app,slot) == biome) matches.push_back(slot);
            if (!matches.empty()) candidates = std::move(matches);
        } catch (const std::exception&) {
            // Habitat preference is optional in Random mode. Native eligible
            // ownership remains mandatory and is not inferred from this read.
        }
    };
    int slot = -1; selection::Identity chosen{};
    if (prefs_.selection_mode == "random" && !prefs_.rotate_companions) {
        preferred(); const auto index = services_.random(candidates.size());
        if (index >= candidates.size()) throw std::runtime_error("Invalid random index");
        slot = candidates[index]; chosen = identity(app,slot);
    } else try {
        auto rows = roster(app); auto current = context(app,location);
        const bool habitat = prefs_.selection_mode == "by_habitat" && location == 3;
        if (habitat) {
            if (!current.habitat) return false;
            bool any = false;
            for (const auto& row : rows) any |= rules_.group(current.habitat,row.candidate.habitat).has_value();
            if (!rows.empty() && !any) { cancel(); notice_ = catalog::text("hud.no_suitable_habitat"); return false; }
        } else preferred();
        std::vector<selection::Candidate> owned; std::vector<selection::Identity> eligible;
        for (const auto& row : rows) owned.push_back(row.candidate);
        for (const auto candidate : candidates) {
            const auto it = std::find_if(rows.begin(),rows.end(),[&](const Row& row) { return row.slot == candidate; });
            if (it == rows.end()) throw selection::SelectionError("Eligible ownership changed");
            eligible.push_back(it->candidate.identity);
        }
        const auto choice = selector_.reserve(owned,eligible,habitat ? selection::Mode::ByHabitat : selection::Mode::Random,current.habitat,prefs_.rotate_companions);
        if (!choice) return false;
        for (const auto& row : rows) if (row.candidate.identity == choice->identity) slot = row.slot;
        chosen = choice->identity; selection_context_ = current;
    } catch (const selection::SelectionError&) { cancel(); log("Selection invalidated; no slot substitution"); return false; }
    if (!policy_.select_for_exit(slot)) return false;
    pending_identity_ = chosen;
    return true;
}
bool Runtime::probe(Address app, Address owner, Address player, int location, double now) {
    const auto physics = read<std::uint64_t>(player + 0x2A8);
    if (!physics) { resetProbe(now+.5); return false; }
    const bool primed = primed_ && probe_location_ == location && probe_physics_ == physics && now > *primed_ && now-*primed_ <= .25;
    if (primed_ && !primed) resetProbe();
    if (!primed && now < next_probe_) return false;
    const auto selected = policy_.pending_slot(); const auto epoch = epoch_;
    std::vector<int> candidates;
    if (selected) { if (services_.owned(owner,*selected)) candidates.push_back(*selected); }
    else for (int slot = 0; slot < 30; ++slot) if (occupied(app,slot) && services_.owned(owner,slot)) candidates.push_back(slot);
    if (candidates.empty()) { resetProbe(now+.5); return false; }
    if (!safe_ || epoch != epoch_ || !policy_.pending() || requested_) return false;
    const auto range = read<float>(services_.base+0x52381E0);
    if (!std::isfinite(range) || range <= 0) throw std::runtime_error("Invalid placement range");
    const auto hand = services_.use_hand() ? read<std::uint32_t>(app+0x30E7FC) : 0;
    if (!safe_ || epoch != epoch_ || !policy_.pending() || requested_ || appFor(player) != app) return false;
    services_.placement(owner+0x1B9140,range,range,hand);
    if (!safe_ || epoch != epoch_ || !policy_.pending() || requested_) return false;
    if (!primed) { primed_ = now; probe_location_ = location; probe_physics_ = physics; return false; }
    resetProbe(now+.5);
    candidates.erase(std::remove_if(candidates.begin(),candidates.end(),[&](int slot) { return !services_.can_summon(player,slot); }),candidates.end());
    if (!safe_ || epoch != epoch_ || !policy_.pending() || requested_ || candidates.empty()) return false;
    return selected.has_value() || choose(app,location,std::move(candidates));
}
void Runtime::tick(Address owner, float dt) {
    if (!prefs_.enabled) { load_pending_ = false; return; }
    if (!policy_.pending() && !load_pending_) return;
    if (requested_) { resetProbe(); return; }
    const auto player = owner - pet_table + local_player; const auto app = appFor(player);
    if (!app) return;
    prepareLoad(app,owner,player,dt); if (!policy_.pending()) return;
    const auto selected = policy_.pending_slot();
    if (selected && (!pending_identity_ || identity(app,*selected) != *pending_identity_)) {
        cancel(); if (prefs_.selection_mode == "last_manual") { policy_.reset(); manual_identity_.reset(); } return;
    }
    if (selected && selector_.pending() && !reservedSafe(app,*selected)) { cancel(); return; }
    if (read<int>(owner+preview) != -1 || read<std::uint8_t>(owner+emote)) { cancel(); return; }
    const auto location = read<int>(app+location_offset);
    if (supported(location) && !allowed(prefs_,location)) { cancel(); return; }
    const auto active = read<int>(app+active_pet), queued = read<int>(player+queued_pet);
    if (active < -1 || active >= 30 || queued < -1 || queued >= 30) { cancel(); return; }
    const bool on_foot = supported(location) && allowed(prefs_,location) && std::isfinite(dt) && dt > 0;
    const auto now = services_.clock(); const auto epoch = epoch_;
    bool eligible = false;
    const bool valid_time = std::isfinite(now) && (!policy_.last_observed_time() || now >= *policy_.last_observed_time());
    if (valid_time && on_foot && active == -1 && queued == -1) eligible = probe(app,owner,player,location,now);
    else resetProbe();
    const auto chosen_identity = pending_identity_;
    const auto slot = policy_.tick(now,on_foot,active,queued,eligible);
    if (!policy_.pending()) { selector_.cancel(); pending_identity_.reset(); selection_context_.reset(); resetProbe(); }
    if (!slot) return;
    if (prefs_.selection_mode != "last_manual") {
        if (selector_.pending() && !reservedSafe(app,*slot)) { cancel(); return; }
        if (!chosen_identity || identity(app,*slot) != *chosen_identity || !occupied(app,*slot) ||
            !services_.owned(owner,*slot) || !services_.can_summon(player,*slot)) {
            policy_.resolve(false); resetProbe(now+.5); return;
        }
    }
    if (!safe_ || epoch != epoch_ || appFor(player) != app || !policy_.pending() || policy_.pending_slot() != slot ||
        pending_identity_ != chosen_identity || !chosen_identity || requested_ || !occupied(app,*slot) ||
        identity(app,*slot) != *chosen_identity || (selector_.pending() && !reservedSafe(app,*slot)) ||
        read<int>(app+active_pet) != -1 || read<int>(player+queued_pet) != -1 ||
        read<int>(app+location_offset) != location || read<int>(owner+preview) != -1 || read<std::uint8_t>(owner+emote)) {
        cancel(); return;
    }
    in_auto_ = true;
    try { services_.queue(player,*slot); } catch (...) { in_auto_ = false; throw; }
    in_auto_ = false;
    // The native queue may synchronously dispatch a load/exit/control callback.
    // Never resolve a replacement opportunity using an older queue result.
    if (!safe_ || epoch != epoch_ || appFor(player) != app || requested_ ||
        !policy_.pending() || policy_.pending_slot() != slot || pending_identity_ != chosen_identity) {
        cancel(); return;
    }
    const auto queued_slot = read<int>(player+queued_pet);
    if (queued_slot == -1) { policy_.resolve(false); resetProbe(now+.5); log("Queue rejected; retaining same companion for paced placement retry"); return; }
    if (queued_slot != *slot) throw std::runtime_error("Unexpected queued companion");
    policy_.resolve(true);
    if (selector_.pending()) selector_.commit(*chosen_identity);
    cancel(); log("Native summon queue accepted; visible appearance requires player verification");
}
void Runtime::afterOwner(Address owner, float dt) noexcept {
    guarded([&] {
        if (owner_ticking_) return;
        owner_ticking_ = true;
        try { tick(owner,dt); } catch (...) { owner_ticking_ = false; throw; }
        owner_ticking_ = false;
    });
}
void Runtime::beforeAction(Address menu, Address action, bool called) noexcept {
    guarded([&] {
      try {
        if (!manual_ok_) return;
        if (manual_) { manual_ok_ = false; invalidate(); return; }
        Manual record{}; record.menu = menu; record.action = action; record.called = called;
        record.epoch = epoch_; record.thread = std::this_thread::get_id();
        if (read<int>(action+4) == 46) {
            record.slot = read<int>(action+0x84);
            if (record.slot < 0 || record.slot >= 30) { manual_ok_ = false; invalidate(); return; }
            record.app = read<Address>(services_.base+app_rva);
            if (record.app) {
                record.candidate = true; record.player = record.app+local_player;
                record.identity = identity(record.app,record.slot); record.save_key = save_key_;
            }
        }
        manual_ = record;
      } catch (...) { manual_ok_ = false; invalidate(); log("Manual choice attribution stopped after invalid native action; automation remains available"); }
    });
}
void Runtime::afterQueue(Address player, int slot) noexcept {
    guarded([&] {
      try {
        if (in_auto_) return;
        const auto app = appFor(player); if (!app) return;
        if (slot < 0 || slot >= 30 || read<int>(player+queued_pet) != slot) return;
        load_pending_ = false; cancel();
        if (!manual_ok_ || !manual_ || !manual_->candidate) return;
        auto& record = *manual_;
        if (record.epoch != epoch_ || record.thread != std::this_thread::get_id() || record.accepted ||
            record.app != app || record.player != player || record.slot != slot || record.save_key != save_key_ ||
            record.identity != identity(app,slot)) { manual_ok_ = false; invalidate(); return; }
        record.accepted = true;
      } catch (...) { manual_ok_ = false; invalidate(); log("Manual choice attribution stopped after native queue mismatch; automation remains available"); }
    });
}
void Runtime::afterAction(Address menu, Address action, bool called, bool result) noexcept {
    guarded([&] {
      try {
        if (!manual_ok_ || !manual_) return;
        const auto record = *manual_; manual_.reset();
        if (record.menu != menu || record.action != action || record.called != called || record.thread != std::this_thread::get_id()) {
            manual_ok_ = false; invalidate(); return;
        }
        if (record.epoch != epoch_ || !record.candidate || !record.accepted || !result) return;
        const auto app = read<Address>(services_.base+app_rva);
        if (!app || app != record.app || app != app_ || save_key_ != record.save_key ||
            read<int>(record.player+queued_pet) != record.slot || identity(app,record.slot) != record.identity) return;
        const bool changed = !favorite_ || favorite_->seed != record.identity;
        policy_.remember(record.slot); manual_identity_ = record.identity; favorite_ = Favorite{record.identity,record.slot};
        bool persisted = false;
        if (!save_key_.empty() && persistence_ok_) try { favorites_.remember(save_key_,record.identity,record.slot); persisted = true; }
        catch (const StorageError&) { persistence_ok_ = false; log("Favorite persistence unavailable; existing file preserved"); }
        if (changed) {
            notice_ = catalog::text(persisted ? "hud.companion_saved" : "hud.companion_session");
            if (!prefs_.enabled) notice_ += catalog::text("hud.auto_off_suffix");
            else if (prefs_.selection_mode == "random") notice_ += catalog::text("hud.random_on_suffix");
            else if (prefs_.selection_mode == "by_habitat") notice_ += catalog::text("hud.habitat_on_suffix");
        }
      } catch (...) { manual_ok_ = false; invalidate(); log("Manual choice attribution stopped after native completion; automation remains available"); }
    });
}
std::string Runtime::label(int role) const {
    static constexpr const char* keys[] = {"menu.automation","menu.selection","menu.biome","menu.planets","menu.space_stations","menu.space_anomaly","menu.rotate_companions"};
    if (role < 0 || role > 6) throw std::invalid_argument("Invalid menu role");
    return catalog::text(keys[role]);
}
std::string Runtime::value(int role, const Preferences& p) const {
    if (role == 1) return catalog::text(p.selection_mode == "random" ? "value.random" : p.selection_mode == "by_habitat" ? "value.by_habitat" : "value.last_selected");
    const bool values[] = {p.enabled,false,p.prefer_same_biome,allowed(p,3),allowed(p,2),allowed(p,14),p.rotate_companions};
    return catalog::text(values[role] ? "value.on" : "value.off");
}
bool Runtime::caption(int role, char* out) noexcept {
    try {
        if (!out || role < -1 || role > 6) return false;
        std::unique_lock<std::recursive_mutex> lock(mutex_,std::try_to_lock); if (!lock.owns_lock()) return false;
        std::string text = role == -1 ? catalog::text("menu.parent_title") :
            catalog::replace(catalog::replace(catalog::text("format.setting"),"{label}",label(role)),"{value}",
                safe_ ? value(role,requested_.value_or(prefs_)) : catalog::text("status.stopped"));
        if (role >= 0 && safe_) {
            const char* status = nullptr;
            if (requested_ && value(role,*requested_) != value(role,prefs_)) status = "status.pending";
            else if (!settings_ok_) status = "status.session_only";
            if (status) text = catalog::replace(catalog::replace(catalog::text("format.with_status"),"{label}",text),"{status}",catalog::text(status));
        }
        if (text.empty() || text.size() >= 128) return false;
        std::memset(out,0,128); std::memcpy(out,text.data(),text.size()); return true;
    } catch (...) { return false; }
}
bool Runtime::capture(int role, std::uint64_t* revision) noexcept {
    std::unique_lock<std::recursive_mutex> lock(mutex_,std::try_to_lock);
    if (!lock.owns_lock() || !safe_ || !revision || role < 0 || role > 6) return false;
    *revision = revision_; return true;
}
bool Runtime::change(int role, std::uint64_t revision) noexcept {
    try {
        std::unique_lock<std::recursive_mutex> lock(mutex_,std::try_to_lock);
        if (!lock.owns_lock() || !safe_ || revision != revision_ || role < 0 || role > 6) return false;
        auto p = requested_.value_or(prefs_);
        if (role == 0) p.enabled = !p.enabled;
        else if (role == 1) p.selection_mode = p.selection_mode == "last_manual" ? "random" : p.selection_mode == "random" ? "by_habitat" : "last_manual";
        else if (role == 2) p.prefer_same_biome = !p.prefer_same_biome;
        else if (role == 6) p.rotate_companions = !p.rotate_companions;
        else {
            const int location = role == 3 ? 3 : role == 4 ? 2 : 14;
            if (allowed(p,location)) p.locations.erase(std::remove(p.locations.begin(),p.locations.end(),location),p.locations.end());
            else { p.locations.push_back(location); std::sort(p.locations.begin(),p.locations.end()); }
        }
        if (services_.allow_menu_change && !services_.allow_menu_change()) return false;
        requested_ = std::move(p); ++revision_; return true;
    } catch (...) { return false; }
}
void Runtime::applyControls() {
    if (!requested_) return;
    const auto previous = prefs_; prefs_ = *requested_; requested_.reset();
    std::string changes;
    for (int role = 0; role < 7; ++role) if (value(role,previous) != value(role,prefs_)) {
        if (!changes.empty()) changes += catalog::text("hud.setting_separator");
        changes += catalog::replace(catalog::replace(catalog::text("format.setting"),"{label}",label(role)),"{value}",value(role,prefs_));
    }
    if (changes.empty()) return;
    invalidate(); load_pending_ = false; cancel();
    if (settings_ok_) try { settings_.save_preferences(prefs_); }
    catch (const StorageError&) { settings_ok_ = false; log("Settings persistence unavailable; existing file preserved"); }
    if (!settings_ok_) changes += catalog::text("hud.session_suffix");
    if (changes.size() > 511) throw std::runtime_error("Complete notice exceeds native buffer");
    notice_ = std::move(changes);
}
void Runtime::afterPlayer(Address player, float dt) noexcept {
    guarded([&] {
        if (!requested_ && notice_.empty()) return;
        const auto app = appFor(player); if (!app) return;
        applyControls();
        if (notice_disabled_) { notice_.clear(); return; }
        if (notice_.empty() || !std::isfinite(dt) || dt <= 0) return;
        try {
            if (read<std::uint32_t>(app+0x837B40+0x28C) > 3 || !(read<float>(app+0x4BF50C) < 0)) return;
            // Consume before the native call. Cosmetic delivery cannot retry a
            // partially accepted message or stop gameplay automation on failure.
            const auto message = std::move(notice_); notice_.clear(); services_.notice(app,message);
        } catch (...) {
            notice_disabled_ = true;
            notice_.clear();
            log("HUD confirmations unavailable; automation and saved settings are unchanged");
        }
    });
}
}
