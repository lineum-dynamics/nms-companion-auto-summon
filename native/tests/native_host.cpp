#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "cas/probe.h"
#include <array>
#include <cstdio>
#include <thread>
#include <vector>
int wmain(int argc,wchar_t** argv) {
    if (argc != 2) return 2;
    const auto module = LoadLibraryExW(argv[1],nullptr,LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);
    if (!module) return 3;
    using Inspect = std::uint32_t(*)(CasHostReport*,std::uint32_t);
    using Status = std::uint32_t(*)();
    auto inspect = reinterpret_cast<Inspect>(GetProcAddress(module,"CasInspectHost"));
    auto status = reinterpret_cast<Status>(GetProcAddress(module,"CasRuntimeStatus"));
    auto initialize = reinterpret_cast<void(*)()>(GetProcAddress(module,"InitializeASI"));
    if (!inspect || !status || !initialize || status() != 0) return 4;
    CasHostReport report{};
    if (inspect(&report,sizeof report) != CAS_UNSUPPORTED_HOST || report.hooks_active) return 5;
    if (inspect(nullptr,0) != CAS_INVALID_ARGUMENT) return 6;
    std::vector<std::thread> calls;
    for (unsigned i=0;i<8;++i) calls.emplace_back(initialize);
    for (auto& call : calls) call.join();
    const auto deadline = GetTickCount64()+15000;
    while (status() == 1 && GetTickCount64() < deadline) Sleep(5);
    if (status() != 2) return 7;
    initialize(); if (status() != 2) return 8;
    std::printf("{\"native_status\":%u,\"host_sha256\":\"%s\",\"hooks_active\":false,\"concurrent_calls\":8}\n",status(),report.image_sha256);
    // InitializeASI process-pins production code; unloading is not an API.
    return 0;
}
