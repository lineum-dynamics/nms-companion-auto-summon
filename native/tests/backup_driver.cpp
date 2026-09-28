// Offline fixture driver: only caller-provided paths are accessed.
#include "cas/backup.hpp"
#include "json.hpp"

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>

#include <iostream>
#include <string>

int main() {
    using Json = nlohmann::json;
    std::string line;
    while (std::getline(std::cin,line)) {
        HANDLE busy = INVALID_HANDLE_VALUE;
        try {
            const auto request = Json::parse(line);
            // A controlled fixture simulates an existing writer. No bytes are
            // written; the implementation must refuse its read-only lock.
            if (request.contains("hold_writer")) {
                const auto path = std::filesystem::u8path(request["hold_writer"].get<std::string>());
                busy = CreateFileW(path.c_str(),GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,
                    nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
                if (busy == INVALID_HANDLE_VALUE) throw std::runtime_error("Cannot open fixture writer");
            }
            const auto report = cas::verified_pre_activation_backup(
                std::filesystem::u8path(request.at("saves").get<std::string>()),
                std::filesystem::u8path(request.at("preferences").get<std::string>()),
                std::filesystem::u8path(request.at("destination").get<std::string>()));
            std::cout << Json{{"ok",true},{"files",report.files},{"bytes",report.bytes},
                {"saves_present",report.saves_present},{"preferences_present",report.preferences_present}}.dump() << '\n';
        } catch (const cas::BackupError& error) {
            std::cout << Json{{"ok",false},{"error","backup"},{"message",error.what()}}.dump() << '\n';
        } catch (const std::exception& error) {
            std::cout << Json{{"ok",false},{"error","driver"},{"message",error.what()}}.dump() << '\n';
        }
        if (busy != INVALID_HANDLE_VALUE) CloseHandle(busy);
    }
    return 0;
}
