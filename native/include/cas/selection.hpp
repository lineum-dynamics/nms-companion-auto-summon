#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <optional>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>

namespace cas::selection {

// Pure session-only selection. The caller supplies ownership separately from
// temporary native eligibility, and commits only after native queue acceptance.
using Identity = std::array<std::uint8_t, 16>;
using RandomRange = std::function<std::size_t(std::size_t)>;
inline constexpr std::size_t max_companions = 30;
enum class Mode { Random, ByHabitat };
enum class Group { Random, Exact, Related, Acceptable };

struct SelectionError : std::invalid_argument { using std::invalid_argument::invalid_argument; };
struct AmbiguousIdentityError : SelectionError { using SelectionError::SelectionError; };
struct ReservationInvalidatedError : SelectionError { using SelectionError::SelectionError; };

std::optional<int> normalize_habitat(std::optional<int> habitat) noexcept;

struct Candidate {
    Identity identity;
    std::optional<int> habitat;
    explicit Candidate(Identity identity_value, std::optional<int> habitat_value = std::nullopt);
};

class HabitatRules {
public:
    using Pairs = std::set<std::pair<int, int>>;
    explicit HabitatRules(std::set<int> recognized = {0,1,2,3,4,5,6,7,12,13,14,15},
                          Pairs related = {}, Pairs acceptable = {});
    std::optional<Group> group(std::optional<int> planet, std::optional<int> companion) const noexcept;
private:
    std::set<int> recognized_;
    Pairs related_;
    Pairs acceptable_;
};

HabitatRules default_habitat_rules();
using HabitatGroups = std::array<std::vector<Candidate>, 3>;
HabitatGroups build_habitat_groups(const std::vector<Candidate>& owned,
                                  std::optional<int> habitat,
                                  const HabitatRules& rules = default_habitat_rules());

struct BagSnapshot {
    Mode mode;
    std::optional<int> habitat;
    Group group;
    std::set<Identity> members;
    std::vector<Identity> remaining;
    std::optional<Identity> last_accepted;
};

class CompanionSelector {
public:
    // randrange(n) must return an unbiased integer in [0,n). No global RNG or
    // persisted state is used. The function is called even when n == 1.
    explicit CompanionSelector(RandomRange randrange,
                               HabitatRules rules = default_habitat_rules());
    std::optional<Candidate> reserve(const std::vector<Candidate>& owned,
                                    const std::vector<Identity>& eligible,
                                    Mode mode = Mode::Random,
                                    std::optional<int> habitat = std::nullopt,
                                    bool rotate = true);
    [[nodiscard]] const std::optional<Candidate>& pending() const noexcept;
    bool commit(const Identity& identity);
    void cancel() noexcept;
    void reset() noexcept;
    // Read-only snapshots support parity testing without exposing mutation.
    [[nodiscard]] std::vector<BagSnapshot> snapshot() const;
private:
    struct Bag {
        std::set<Identity> members;
        std::vector<Identity> remaining;
        std::optional<Identity> last_accepted;
    };
    struct Context {
        Mode mode;
        std::optional<int> habitat;
        Group group;
        Bag bag;
    };
    std::size_t draw(std::size_t bound);
    void reconcile(Bag& bag, const std::set<Identity>& members);
    Identity reserve_from_bag(Bag& bag, const std::set<Identity>& eligible);
    std::set<Identity> members(const Context& context, const std::vector<Candidate>& owned) const;
    RandomRange randrange_;
    HabitatRules rules_;
    // Python's dict has insertion order; reconciliation must preserve that RNG
    // call order as well as each context's retained rotation history.
    std::vector<Context> contexts_;
    std::optional<Candidate> pending_;
    std::optional<std::size_t> pending_bag_;
};

}  // namespace cas::selection
