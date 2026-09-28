// Offline parity driver. Only stdin/stdout/stderr are used; no game integration.
// Arguments: [delay_seconds [expiry_seconds|none]] (default: 1.5, none).
// Line commands: reset | remember SLOT | eject NOW BOOL | select SLOT | enter |
// resolve BOOL | tick NOW ON_FOOT ACTIVE_PET NATIVE_PENDING_PET ELIGIBLE.
// Booleans must be 0 or 1. NaN and infinity are forwarded to policy validation.

#include "cas/policy.hpp"

#include <charconv>
#include <cstdlib>
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <variant>
#include <vector>

namespace {

using Result = std::variant<std::monostate, bool, int>;

double parse_number(const std::string& token) {
    char* end = nullptr;
    const double value = std::strtod(token.c_str(), &end);
    if (end == token.c_str() || *end != '\0') {
        throw std::invalid_argument("expected a numeric token");
    }
    return value;
}

int parse_integer(const std::string& token) {
    int value = 0;
    const auto result = std::from_chars(token.data(), token.data() + token.size(), value);
    if (result.ec != std::errc{} || result.ptr != token.data() + token.size()) {
        throw std::invalid_argument("expected an integer token");
    }
    return value;
}

bool parse_boolean(const std::string& token) {
    if (token == "0") {
        return false;
    }
    if (token == "1") {
        return true;
    }
    throw std::invalid_argument("expected a boolean token (0 or 1)");
}

void require_size(const std::vector<std::string>& tokens, std::size_t size) {
    if (tokens.size() != size) {
        throw std::invalid_argument("incorrect command argument count");
    }
}

Result apply_command(cas::CompanionAutoSummonPolicy& policy,
             const std::vector<std::string>& tokens) {
    if (tokens.empty()) {
        throw std::invalid_argument("expected a command");
    }
    const std::string& command = tokens[0];
    if (command == "reset") {
        require_size(tokens, 1);
        policy.reset();
    } else if (command == "remember") {
        require_size(tokens, 2);
        policy.remember(parse_integer(tokens[1]));
    } else if (command == "eject") {
        require_size(tokens, 3);
        const double now = parse_number(tokens[1]);
        const bool random_selection = parse_boolean(tokens[2]);
        policy.eject(now, random_selection);
    } else if (command == "select") {
        require_size(tokens, 2);
        return policy.select_for_exit(parse_integer(tokens[1]));
    } else if (command == "enter") {
        require_size(tokens, 1);
        policy.enter_ship();
    } else if (command == "resolve") {
        require_size(tokens, 2);
        return policy.resolve(parse_boolean(tokens[1]));
    } else if (command == "tick") {
        require_size(tokens, 6);
        const double now = parse_number(tokens[1]);
        const bool on_foot = parse_boolean(tokens[2]);
        const int active = parse_integer(tokens[3]);
        const int native_pending = parse_integer(tokens[4]);
        const bool eligible = parse_boolean(tokens[5]);
        const auto slot = policy.tick(now, on_foot, active, native_pending, eligible);
        if (slot) {
            return *slot;
        }
    } else {
        throw std::invalid_argument("unknown command");
    }
    return std::monostate{};
}

void emit_optional_integer(std::optional<int> value) {
    if (value) {
        std::cout << *value;
    } else {
        std::cout << "null";
    }
}

void emit_json_string(const std::string& value) {
    constexpr char hex[] = "0123456789abcdef";
    std::cout << '"';
    for (unsigned char character : value) {
        if (character == '"' || character == '\\') {
            std::cout << '\\' << static_cast<char>(character);
        } else if (character < 0x20) {
            std::cout << "\\u00" << hex[character >> 4] << hex[character & 0xf];
        } else {
            std::cout << static_cast<char>(character);
        }
    }
    std::cout << '"';
}

void emit_state(const cas::CompanionAutoSummonPolicy& policy, const Result& result,
                const std::optional<std::string>& error) {
    std::cout << "{\"result\":";
    if (std::holds_alternative<bool>(result)) {
        std::cout << (std::get<bool>(result) ? "true" : "false");
    } else if (std::holds_alternative<int>(result)) {
        std::cout << std::get<int>(result);
    } else {
        std::cout << "null";
    }
    std::cout << ",\"last_slot\":";
    emit_optional_integer(policy.last_slot());
    std::cout << ",\"pending\":" << (policy.pending() ? "true" : "false");
    std::cout << ",\"pending_slot\":";
    emit_optional_integer(policy.pending_slot());
    std::cout << ",\"error\":";
    if (error) {
        emit_json_string(*error);
    } else {
        std::cout << "null";
    }
    std::cout << "}\n";
}

}  // namespace

int main(int argc, char* argv[]) {
    try {
        if (argc > 3) {
            throw std::invalid_argument("usage: policy_reference_driver [delay [expiry|none]]");
        }
        const double delay = argc >= 2 ? parse_number(argv[1]) : 1.5;
        const std::optional<double> expiry =
            argc >= 3 && std::string(argv[2]) != "none"
                ? std::optional<double>(parse_number(argv[2]))
                : std::nullopt;
        cas::CompanionAutoSummonPolicy policy(delay, expiry);
        std::string line;
        while (std::getline(std::cin, line)) {
            std::istringstream stream(line);
            std::vector<std::string> tokens;
            for (std::string token; stream >> token;) {
                tokens.push_back(token);
            }
            Result result = std::monostate{};
            std::optional<std::string> error;
            try {
                result = apply_command(policy, tokens);
            } catch (const std::exception& exception) {
                error = exception.what();
            }
            emit_state(policy, result, error);
        }
        return std::cin.bad() ? 1 : 0;
    } catch (const std::exception& exception) {
        std::cerr << exception.what() << '\n';
        return 2;
    }
}
