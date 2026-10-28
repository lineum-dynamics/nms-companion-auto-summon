// Owned Windows-CI host. Only the current EXE inspection/status ABI is invoked.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "cas/probe.h"
#include <cstdio>
#include <cwchar>
#include <cstdint>

bool allowed() {
    wchar_t enabled[16]{},repository[128]{},image[32768]{};
    if (!GetEnvironmentVariableW(L"GITHUB_ACTIONS",enabled,16) ||
        !GetEnvironmentVariableW(L"GITHUB_REPOSITORY",repository,128) ||
        !GetModuleFileNameW(nullptr,image,32768)) return false;
    const wchar_t* leaf=std::wcsrchr(image,L'\\'); leaf=leaf?leaf+1:image;
    return !std::wcscmp(enabled,L"true") &&
        !std::wcscmp(repository,L"lineum-dynamics/nms-companion-auto-summon") &&
        !_wcsicmp(leaf,L"cas-inspection-host.exe");
}
int wmain(int argc,wchar_t** argv) {
    if (!allowed() || argc!=3) return 2;
    const bool production=std::wcscmp(argv[2],L"inspection")==0;
    if (!production && std::wcscmp(argv[2],L"stub")) return 3;
    HMODULE module=LoadLibraryExW(argv[1],nullptr,
        LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);
    if (!module) return 4;
    using Status=std::uint32_t(*)();
    using Inspect=std::uint32_t(*)(CasHostReport*,std::uint32_t);
    const auto status=reinterpret_cast<Status>(GetProcAddress(module,"CasComponentProbeStatus"));
    const auto inspect=reinterpret_cast<Inspect>(GetProcAddress(module,"CasInspectHost"));
    if (!status || !inspect || status()!=0xC45D0001u) return 5;
    CasHostReport report{};
    if (inspect(nullptr,0)!=CAS_INVALID_ARGUMENT ||
        inspect(&report,sizeof(report))!=CAS_UNSUPPORTED_HOST || report.hooks_active ||
        report.abi_version!=1 || report.struct_size!=sizeof(report)) return 6;
    if ((report.image_sha256[0]!='\0')!=production) return 7;
    if (!FreeLibrary(module)) return 8;
    std::printf("{\"passed\":true,\"diagnostic_only\":true,\"game_access\":false,"
                "\"core_methods_called\":false,\"inspection_called\":true,"
                "\"native_status\":%u,\"hooks_active\":false,\"host_sha256\":\"%s\"}\n",
                report.status,report.image_sha256);
    return 0;
}
