#include "cas/selection.hpp"

#include <algorithm>
#include <map>

namespace cas::selection {
namespace {
using Roster = std::map<Identity, Candidate>;
Roster validated_roster(const std::vector<Candidate>& owned) {
    Roster result;
    for (const auto& candidate : owned) {
        if (result.count(candidate.identity)) {
            throw AmbiguousIdentityError("Owned companion identity is ambiguous");
        }
        if (result.size() >= max_companions) {
            throw SelectionError("Owned roster exceeds 30 companions");
        }
        result.emplace(candidate.identity, candidate);
    }
    return result;
}
constexpr std::array<Group, 3> groups = {Group::Exact, Group::Related, Group::Acceptable};
constexpr std::array<std::size_t, 3> weights = {13, 5, 1};
}

std::optional<int> normalize_habitat(std::optional<int> habitat) noexcept {
    if (!habitat) return std::nullopt;
    if (*habitat >= 8 && *habitat <= 10) return 7;
    if ((*habitat >= 0 && *habitat <= 7) || (*habitat >= 12 && *habitat <= 15)) return habitat;
    return std::nullopt;
}

Candidate::Candidate(Identity identity_value, std::optional<int> habitat_value)
    : identity(identity_value), habitat(normalize_habitat(habitat_value)) {}

HabitatRules::HabitatRules(std::set<int> recognized, Pairs related, Pairs acceptable)
    : recognized_(std::move(recognized)), related_(std::move(related)), acceptable_(std::move(acceptable)) {
    for (int value : recognized_) {
        if (normalize_habitat(value) != std::optional<int>(value)) {
            throw SelectionError("Recognized habitats must be canonical concrete IDs");
        }
    }
    for (const auto* pairs : {&related_, &acceptable_}) {
        for (const auto& pair : *pairs) {
            if (!recognized_.count(pair.first) || !recognized_.count(pair.second) || pair.first == pair.second) {
                throw SelectionError("Non-exact habitat pairs must use distinct recognized IDs");
            }
        }
    }
    for (const auto& pair : related_) {
        if (acceptable_.count(pair)) throw SelectionError("Related and acceptable habitat pairs must be disjoint");
    }
}

std::optional<Group> HabitatRules::group(std::optional<int> planet, std::optional<int> companion) const noexcept {
    planet = normalize_habitat(planet);
    companion = normalize_habitat(companion);
    if (!planet || !companion || !recognized_.count(*planet) || !recognized_.count(*companion)) return std::nullopt;
    if (*planet == *companion) return Group::Exact;
    const std::pair<int, int> pair{*planet, *companion};
    if (related_.count(pair)) return Group::Related;
    if (acceptable_.count(pair)) return Group::Acceptable;
    return std::nullopt;
}

HabitatRules default_habitat_rules() {
    return HabitatRules({0,1,2,3,4,5,6,7,12,13,14,15},
        {{0,12},{12,0},{1,12},{12,1},{2,13},{13,2},{5,6},{6,5}},
        {{0,5},{0,4},{1,3},{2,5},{2,6},{3,1},{3,5},{3,6},{4,5},{4,6},
         {5,0},{5,2},{5,3},{5,4},{6,2},{6,3},{6,4},{12,3},{12,5},{13,5},{13,6}});
}

HabitatGroups build_habitat_groups(const std::vector<Candidate>& owned,
                                  std::optional<int> habitat, const HabitatRules& rules) {
    const auto roster = validated_roster(owned);
    HabitatGroups result;
    for (const auto& [identity, candidate] : roster) {
        (void)identity;
        const auto group = rules.group(habitat, candidate.habitat);
        for (std::size_t i = 0; i < groups.size(); ++i) {
            if (group == groups[i]) result[i].push_back(candidate);
        }
    }
    return result;
}

CompanionSelector::CompanionSelector(RandomRange randrange, HabitatRules rules)
    : randrange_(std::move(randrange)), rules_(std::move(rules)) {
    if (!randrange_) throw SelectionError("A random range source is required");
}

std::size_t CompanionSelector::draw(std::size_t bound) {
    if (!bound) throw SelectionError("Random range bound must be positive");
    const auto value = randrange_(bound);
    if (value >= bound) throw SelectionError("Random range source returned an out-of-range value");
    return value;
}

void CompanionSelector::reconcile(Bag& bag, const std::set<Identity>& new_members) {
    bag.remaining.erase(std::remove_if(bag.remaining.begin(), bag.remaining.end(),
        [&](const Identity& identity) { return !new_members.count(identity); }), bag.remaining.end());
    if (bag.last_accepted && !new_members.count(*bag.last_accepted)) bag.last_accepted.reset();
    for (const auto& identity : new_members) {
        if (!bag.members.count(identity)) {
            const auto position = draw(bag.remaining.size() + 1);
            bag.remaining.insert(bag.remaining.begin() + static_cast<std::ptrdiff_t>(position), identity);
        }
    }
    bag.members = new_members;
}

Identity CompanionSelector::reserve_from_bag(Bag& bag, const std::set<Identity>& eligible) {
    for (const auto& identity : bag.remaining) {
        if (eligible.count(identity) && (eligible.size() <= 1 || bag.last_accepted != identity)) return identity;
    }
    std::vector<Identity> refreshed;
    for (const auto& identity : eligible) {
        if (std::find(bag.remaining.begin(), bag.remaining.end(), identity) == bag.remaining.end()) {
            refreshed.push_back(identity);
        }
    }
    // Equivalent to Python Random.shuffle's descending Fisher-Yates loop.
    for (std::size_t count = refreshed.size(); count > 1; --count) {
        std::swap(refreshed[count - 1], refreshed[draw(count)]);
    }
    if (refreshed.size() > 1 && bag.last_accepted == refreshed.front()) {
        std::rotate(refreshed.begin(), refreshed.begin() + 1, refreshed.end());
    }
    if (refreshed.empty()) throw std::logic_error("Eligible rotation pool cannot be empty");
    bag.remaining.insert(bag.remaining.end(), refreshed.begin(), refreshed.end());
    return refreshed.front();
}

std::set<Identity> CompanionSelector::members(const Context& context, const std::vector<Candidate>& owned) const {
    std::set<Identity> result;
    for (const auto& candidate : owned) {
        if (context.mode == Mode::Random || rules_.group(context.habitat, candidate.habitat) == context.group) {
            result.insert(candidate.identity);
        }
    }
    return result;
}

std::optional<Candidate> CompanionSelector::reserve(const std::vector<Candidate>& owned,
    const std::vector<Identity>& eligible_identities, Mode mode, std::optional<int> habitat, bool rotate) {
    Roster roster;
    std::set<Identity> eligible;
    try {
        if (mode != Mode::Random && mode != Mode::ByHabitat) {
            throw SelectionError("Selection mode must be random or by_habitat");
        }
        habitat = normalize_habitat(habitat);
        roster = validated_roster(owned);
        for (const auto& identity : eligible_identities) {
            if (!roster.count(identity)) throw SelectionError("Eligible identity is not in the owned roster");
            if (!eligible.insert(identity).second) throw AmbiguousIdentityError("Eligible companion identity is duplicated");
        }
        if (pending_) {
            if (!roster.count(pending_->identity)) throw ReservationInvalidatedError("Reserved companion is no longer owned");
            return pending_;
        }
    } catch (const SelectionError&) {
        cancel();
        throw;
    }
    for (auto& context : contexts_) reconcile(context.bag, members(context, owned));
    Context key{mode, std::nullopt, Group::Random, {}};
    std::set<Identity> pool = eligible;
    if (mode == Mode::ByHabitat) {
        const auto habitat_groups = build_habitat_groups(owned, habitat, rules_);
        std::array<std::set<Identity>, 3> pools;
        std::size_t total = 0;
        for (std::size_t i = 0; i < groups.size(); ++i) {
            for (const auto& candidate : habitat_groups[i]) {
                if (eligible.count(candidate.identity)) pools[i].insert(candidate.identity);
            }
            if (!pools[i].empty()) total += weights[i];
        }
        if (!total) return std::nullopt;
        auto ticket = draw(total);
        for (std::size_t i = 0; i < groups.size(); ++i) {
            if (pools[i].empty()) continue;
            if (ticket < weights[i]) {
                key.habitat = habitat;
                key.group = groups[i];
                pool = pools[i];
                break;
            }
            ticket -= weights[i];
        }
    }
    if (pool.empty()) return std::nullopt;
    Identity identity{};
    if (rotate) {
        auto it = std::find_if(contexts_.begin(), contexts_.end(), [&](const Context& context) {
            return context.mode == key.mode && context.habitat == key.habitat && context.group == key.group;
        });
        if (it == contexts_.end()) {
            contexts_.push_back(std::move(key));
            it = contexts_.end() - 1;
        }
        reconcile(it->bag, members(*it, owned));
        identity = reserve_from_bag(it->bag, pool);
        pending_bag_ = static_cast<std::size_t>(it - contexts_.begin());
    } else {
        auto it = pool.begin();
        std::advance(it, static_cast<std::ptrdiff_t>(draw(pool.size())));
        identity = *it;
        pending_bag_.reset();
    }
    pending_ = roster.at(identity);
    return pending_;
}

const std::optional<Candidate>& CompanionSelector::pending() const noexcept { return pending_; }
bool CompanionSelector::commit(const Identity& identity) {
    if (!pending_ || pending_->identity != identity) return false;
    if (pending_bag_) {
        auto& bag = contexts_.at(*pending_bag_).bag;
        const auto it = std::find(bag.remaining.begin(), bag.remaining.end(), identity);
        if (it == bag.remaining.end()) throw std::logic_error("Reserved companion is absent from its rotation bag");
        bag.remaining.erase(it);
        bag.last_accepted = identity;
    }
    cancel();
    return true;
}
void CompanionSelector::cancel() noexcept { pending_.reset(); pending_bag_.reset(); }
void CompanionSelector::reset() noexcept { contexts_.clear(); cancel(); }
std::vector<BagSnapshot> CompanionSelector::snapshot() const {
    std::vector<BagSnapshot> result;
    for (const auto& context : contexts_) result.push_back({context.mode, context.habitat, context.group,
        context.bag.members, context.bag.remaining, context.bag.last_accepted});
    return result;
}

}  // namespace cas::selection
