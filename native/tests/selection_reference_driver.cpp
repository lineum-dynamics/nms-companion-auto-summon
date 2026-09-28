// Offline stdin/stdout parity driver. It has no game or filesystem integration.
#include "cas/selection.hpp"

#include <charconv>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <variant>

namespace {
using namespace cas::selection;

struct ScriptedRandom {
    std::vector<std::uint64_t> tape;
    std::size_t position = 0;
    std::vector<std::pair<std::size_t, std::size_t>> calls;
    std::size_t operator()(std::size_t bound) {
        if (tape.empty() || !bound) throw std::runtime_error("Invalid scripted RNG");
        const auto value = static_cast<std::size_t>(tape[position++ % tape.size()] % bound);
        calls.emplace_back(bound, value);
        return value;
    }
};

std::string token(std::istringstream& input) {
    std::string value;
    if (!(input >> value)) throw std::runtime_error("Missing command token");
    return value;
}
template <typename T> T number(const std::string& value) {
    T result{};
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size()) throw std::runtime_error("Invalid number");
    return result;
}
std::optional<int> habitat(const std::string& value) {
    return value == "none" ? std::nullopt : std::optional<int>(number<int>(value));
}
Identity identity(const std::string& value) {
    if (value.size() != 32) throw std::runtime_error("Identity needs 32 hex digits");
    Identity result{};
    for (std::size_t i = 0; i < 16; ++i) {
        unsigned byte = 0;
        const auto parsed = std::from_chars(value.data() + i * 2, value.data() + i * 2 + 2, byte, 16);
        if (parsed.ec != std::errc{} || parsed.ptr != value.data() + i * 2 + 2) throw std::runtime_error("Invalid hex identity");
        result[i] = static_cast<std::uint8_t>(byte);
    }
    return result;
}
std::string identity_json(const Identity& value) {
    constexpr char digits[] = "0123456789abcdef";
    std::string result = "\"";
    for (const auto byte : value) {
        result += digits[byte >> 4];
        result += digits[byte & 15];
    }
    return result + '"';
}
std::string habitat_json(std::optional<int> value) { return value ? std::to_string(*value) : "null"; }
std::string candidate_json(const std::optional<Candidate>& value) {
    return value ? "[" + identity_json(value->identity) + "," + habitat_json(value->habitat) + "]" : "null";
}
std::string group_json(std::optional<Group> value) {
    if (!value) return "null";
    switch (*value) {
    case Group::Random: return "\"random\"";
    case Group::Exact: return "\"exact\"";
    case Group::Related: return "\"related\"";
    case Group::Acceptable: return "\"acceptable\"";
    }
    throw std::runtime_error("Invalid group");
}
template <typename T> void identities_json(std::ostream& output, const T& values) {
    output << '[';
    bool comma = false;
    for (const auto& value : values) {
        if (comma) output << ',';
        output << identity_json(value);
        comma = true;
    }
    output << ']';
}
std::vector<Candidate> roster(std::istringstream& input) {
    const auto count = number<std::size_t>(token(input));
    if (count > 100) throw std::runtime_error("Driver roster limit");
    std::vector<Candidate> result;
    for (std::size_t i = 0; i < count; ++i) {
        const auto id = identity(token(input));
        const auto category = habitat(token(input));
        result.emplace_back(id, category);
    }
    return result;
}
HabitatRules rules(std::istringstream& input) {
    const auto count = number<std::size_t>(token(input));
    if (count > 100) throw std::runtime_error("Driver rules limit");
    std::set<int> recognized;
    for (std::size_t i = 0; i < count; ++i) recognized.insert(number<int>(token(input)));
    HabitatRules::Pairs related, acceptable;
    for (auto* pairs : {&related, &acceptable}) {
        const auto pair_count = number<std::size_t>(token(input));
        if (pair_count > 1000) throw std::runtime_error("Driver pair limit");
        for (std::size_t i = 0; i < pair_count; ++i) {
            const auto first = number<int>(token(input));
            const auto second = number<int>(token(input));
            pairs->emplace(first, second);
        }
    }
    return HabitatRules(std::move(recognized), std::move(related), std::move(acceptable));
}

void emit(const CompanionSelector& selector, const ScriptedRandom& rng,
          const std::string& result, const std::string& error) {
    std::cout << "{\"result\":" << result << ",\"error\":" << error
              << ",\"pending\":" << candidate_json(selector.pending()) << ",\"bags\":[";
    bool comma = false;
    for (const auto& bag : selector.snapshot()) {
        if (comma) std::cout << ',';
        std::cout << "{\"key\":[\"" << (bag.mode == Mode::Random ? "random" : "by_habitat") << "\","
                  << habitat_json(bag.habitat) << ',' << group_json(bag.group) << "],\"members\":";
        identities_json(std::cout, bag.members);
        std::cout << ",\"remaining\":";
        identities_json(std::cout, bag.remaining);
        std::cout << ",\"last_accepted\":" << (bag.last_accepted ? identity_json(*bag.last_accepted) : "null") << '}';
        comma = true;
    }
    std::cout << "],\"rng_position\":" << rng.position << ",\"rng_calls\":[";
    comma = false;
    for (const auto& [bound, value] : rng.calls) {
        if (comma) std::cout << ',';
        std::cout << '[' << bound << ',' << value << ']';
        comma = true;
    }
    std::cout << "]}\n";
}
}

int main() {
    try {
        ScriptedRandom rng;
        std::string line;
        if (!std::getline(std::cin, line)) throw std::runtime_error("RNG tape required");
        std::istringstream first(line);
        if (token(first) != "tape") throw std::runtime_error("Expected tape command");
        const auto count = number<std::size_t>(token(first));
        if (!count || count > 100000) throw std::runtime_error("Invalid tape size");
        for (std::size_t i = 0; i < count; ++i) rng.tape.push_back(number<std::uint64_t>(token(first)));
        std::string trailing;
        if (first >> trailing) throw std::runtime_error("Trailing RNG input");
        auto current_rules = default_habitat_rules();
        auto selector = std::make_unique<CompanionSelector>(std::ref(rng), current_rules);
        while (std::getline(std::cin, line)) {
            std::istringstream input(line);
            rng.calls.clear();
            std::string result = "null", error = "null";
            try {
                const auto command = token(input);
                if (command == "reset") selector->reset();
                else if (command == "cancel") selector->cancel();
                else if (command == "commit") {
                    const auto value = token(input);
                    Identity id{};
                    if (value == "pending") {
                        if (selector->pending()) id = selector->pending()->identity;
                    } else id = identity(value);
                    result = selector->commit(id) ? "true" : "false";
                } else if (command == "reserve") {
                    const auto mode_name = token(input);
                    const auto mode = mode_name == "random" ? Mode::Random :
                        mode_name == "by_habitat" ? Mode::ByHabitat : static_cast<Mode>(-1);
                    const auto category = habitat(token(input));
                    const auto rotate_token = token(input);
                    if (rotate_token != "0" && rotate_token != "1") throw std::runtime_error("Invalid bool");
                    const auto owned = roster(input);
                    const auto eligible_count = number<std::size_t>(token(input));
                    if (eligible_count > 100) throw std::runtime_error("Driver eligibility limit");
                    std::vector<Identity> eligible;
                    for (std::size_t i = 0; i < eligible_count; ++i) eligible.push_back(identity(token(input)));
                    result = candidate_json(selector->reserve(owned, eligible, mode, category, rotate_token == "1"));
                } else if (command == "group") {
                    const auto planet = habitat(token(input));
                    const auto companion = habitat(token(input));
                    result = group_json(current_rules.group(planet, companion));
                } else if (command == "groups") {
                    const auto category = habitat(token(input));
                    const auto built = build_habitat_groups(roster(input), category, current_rules);
                    std::ostringstream out;
                    out << '[';
                    for (std::size_t i = 0; i < built.size(); ++i) {
                        if (i) out << ',';
                        out << '[';
                        for (std::size_t j = 0; j < built[i].size(); ++j) {
                            if (j) out << ',';
                            out << candidate_json(built[i][j]);
                        }
                        out << ']';
                    }
                    out << ']';
                    result = out.str();
                } else if (command == "rules") {
                    auto replacement = rules(input);
                    current_rules = replacement;
                    selector = std::make_unique<CompanionSelector>(std::ref(rng), current_rules);
                } else if (command == "default_rules") {
                    current_rules = default_habitat_rules();
                    selector = std::make_unique<CompanionSelector>(std::ref(rng), current_rules);
                } else throw std::runtime_error("Unknown command");
                if (input >> trailing) throw std::runtime_error("Trailing command input");
            } catch (const ReservationInvalidatedError&) { error = "\"ReservationInvalidatedError\""; }
              catch (const AmbiguousIdentityError&) { error = "\"AmbiguousIdentityError\""; }
              catch (const SelectionError&) { error = "\"SelectionError\""; }
            emit(*selector, rng, result, error);
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 2;
    }
}
