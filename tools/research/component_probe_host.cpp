// CI-only load/unload smoke host; no component/game methods are invoked.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cwchar>

bool allowed() {
    wchar_t enabled[16]{},repository[128]{},image[32768]{};
    if (!GetEnvironmentVariableW(L"GITHUB_ACTIONS",enabled,16) ||
        !GetEnvironmentVariableW(L"GITHUB_REPOSITORY",repository,128) ||
        !GetModuleFileNameW(nullptr,image,32768)) return false;
    const wchar_t* leaf=std::wcsrchr(image,L'\\'); leaf=leaf?leaf+1:image;
    return !std::wcscmp(enabled,L"true") &&
        !std::wcscmp(repository,L"lineum-dynamics/nms-companion-auto-summon") &&
        !_wcsicmp(leaf,L"cas-component-host.exe");
}
int wmain(int argc,wchar_t** argv) {
    if (!allowed() || argc!=2) return 2;
    HMODULE module=LoadLibraryExW(argv[1],nullptr,
        LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);
    if (!module) return 3;
    auto function=reinterpret_cast<std::uint32_t(*)()>(GetProcAddress(module,"CasComponentProbeStatus"));
    if (!function || function()!=0xC45D0001u) return 4;
    if (!FreeLibrary(module)) return 5;
    std::printf("{\"passed\":true,\"diagnostic_only\":true,\"load_status_export_unload\":true,"
                "\"game_access\":false,\"production_methods_called\":false}\n");
    return 0;
}
