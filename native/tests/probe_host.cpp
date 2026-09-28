#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <iostream>
#include <array>
#include <thread>
#include "cas/probe.h"

// An owned offline host; never locates, starts or opens another process.
int wmain(int argc, wchar_t** argv) {
    if (argc != 2) return 2;
    wchar_t absolute[32768]{};
    DWORD length = GetFullPathNameW(argv[1], 32768, absolute, nullptr);
    if (!length || length >= 32768) return 3;
    HMODULE module = LoadLibraryExW(absolute, nullptr,
        LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR | LOAD_LIBRARY_SEARCH_SYSTEM32);
    if (!module) return 4;
    auto inspect = reinterpret_cast<uint32_t (*)(CasHostReport*, uint32_t)>(
        GetProcAddress(module, "CasInspectHost"));
    auto initialize = reinterpret_cast<void (*)()>(GetProcAddress(module, "InitializeASI"));
    auto status = reinterpret_cast<uint32_t (*)()>(GetProcAddress(module, "CasInitializationStatus"));
    if (!inspect || !initialize || !status) return 5;
    CasHostReport report{};
    report.status = 0x12345678;
    if (status() != CAS_NOT_INITIALIZED ||
        inspect(nullptr, sizeof(report)) != CAS_INVALID_ARGUMENT ||
        inspect(&report, sizeof(report) - 1) != CAS_INVALID_ARGUMENT ||
        report.status != 0x12345678) return 6;
    const uint32_t result = inspect(&report, sizeof(report));
    if (result != CAS_UNSUPPORTED_HOST || report.hooks_active != 0 ||
        report.abi_version != 1 || report.struct_size != sizeof(report)) return 7;
    std::array<std::thread, 8> callers;
    for (auto& caller : callers) caller = std::thread(initialize);
    for (auto& caller : callers) caller.join();
    initialize();
    if (status() != result) return 8;
    std::cout << "{\"status\":" << result << ",\"hooks_active\":"
              << report.hooks_active << ",\"abi_version\":" << report.abi_version
              << ",\"image_sha256\":\"" << report.image_sha256
              << "\",\"initialization_status\":" << status() << "}\n";
    if (!FreeLibrary(module)) return 9;
    return 0;
}
