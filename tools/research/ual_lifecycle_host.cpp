// Owned CI executable; never masquerades as NMS or calls InitializeASI itself.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
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
        !_wcsicmp(leaf,L"cas-ual-host.exe");
}
int wmain(int argc,wchar_t** argv) {
    if (!allowed() || argc!=3) return 2;
    bool expected=std::wcscmp(argv[2],L"with-asi")==0;
    if (!expected && std::wcscmp(argv[2],L"baseline")) return 3;
    wchar_t before[32768]{},after[32768]{};
    if (!GetCurrentDirectoryW(32768,before)) return 4;
    HMODULE loader=LoadLibraryExW(argv[1],nullptr,
        LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);
    if (!loader) return 5;
    // These are normal UAL-supported IAT triggers, called from the owned EXE.
    STARTUPINFOW startup{}; startup.cb=static_cast<DWORD>(sizeof(startup)); GetStartupInfoW(&startup);
    auto time_function=reinterpret_cast<DWORD(WINAPI*)()>(GetProcAddress(loader,"timeGetTime"));
    if (!time_function) return 6;
    (void)time_function();
    HMODULE asi=GetModuleHandleW(L"CompanionAutoSummon.asi");
    std::uint32_t observed=0;
    if (expected) {
        const auto deadline=GetTickCount64()+10000;
        while (!asi && GetTickCount64()<deadline) { Sleep(1); asi=GetModuleHandleW(L"CompanionAutoSummon.asi"); }
        if (!asi) return 7;
        auto status=reinterpret_cast<std::uint32_t(*)()>(GetProcAddress(asi,"CasRuntimeStatus"));
        if (!status) return 8;
        while (status()<2 && GetTickCount64()<deadline) Sleep(1);
        observed=status(); if (observed!=2) return 9;
    } else if (asi) return 10;
    if (!GetCurrentDirectoryW(32768,after) || std::wcscmp(before,after)) return 11;
    std::printf("{\"passed\":true,\"game_access\":false,\"asi_present\":%s,"
        "\"native_status\":%u,\"manual_initialize_call\":false,"
        "\"winmm_export_called\":true,\"working_directory_restored\":true}\n",asi?"true":"false",observed);
    // Production ASI is process-pinned. Whole-process exit is the teardown.
    return 0;
}
