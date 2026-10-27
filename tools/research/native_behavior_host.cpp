// Owned CI host for exact-module behavior attribution. Never a game launcher.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cwchar>
#include "cas/probe.h"

void phase(const char* value) {
    std::printf("{\"phase\":\"%s\"}\n",value);
    std::fflush(stdout);
}
DWORD WINAPI control_thread(void*) { return 0; }
bool ci_context() {
    wchar_t enabled[16]{},repository[128]{},image[32768]{};
    if (!GetEnvironmentVariableW(L"GITHUB_ACTIONS",enabled,16) ||
        !GetEnvironmentVariableW(L"GITHUB_REPOSITORY",repository,128) ||
        !GetModuleFileNameW(nullptr,image,32768)) return false;
    const auto* leaf=std::wcsrchr(image,L'\\'); leaf=leaf?leaf+1:image;
    return std::wcscmp(enabled,L"true")==0 &&
        std::wcscmp(repository,L"lineum-dynamics/nms-companion-auto-summon")==0 &&
        _wcsicmp(leaf,L"cas-behavior-host.exe")==0;
}
int wmain(int argc,wchar_t** argv) {
    if (!ci_context() || argc!=3) return 2;
    const bool baseline=std::wcscmp(argv[1],L"baseline")==0;
    const bool load=std::wcscmp(argv[1],L"load")==0;
    const bool inspect=std::wcscmp(argv[1],L"inspect")==0;
    const bool initialize=std::wcscmp(argv[1],L"initialize")==0;
    if (!baseline && !load && !inspect && !initialize) return 3;
    phase("controls-start");
    Sleep(7);
    std::uint32_t destination=0,source=0x12345678;
    SIZE_T copied=0;
    if (!WriteProcessMemory(GetCurrentProcess(),&destination,&source,sizeof(source),&copied) ||
        copied!=sizeof(source) || destination!=source) return 4;
    HANDLE thread=CreateThread(nullptr,0,control_thread,nullptr,0,nullptr);
    if (!thread) return 5;
    const auto waited=WaitForSingleObject(thread,5000);
    CloseHandle(thread);
    if (waited!=WAIT_OBJECT_0) return 6;
    phase("controls-complete");
    unsigned observed=0;
    if (!baseline) {
        phase("before-load");
        HMODULE module=LoadLibraryExW(argv[2],nullptr,
            LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);
        if (!module) {
            std::printf("{\"phase\":\"load-failed\",\"win32_error\":%lu}\n",GetLastError());
            return 7;
        }
        phase("after-load");
        if (inspect || initialize) {
            using Inspect=std::uint32_t(*)(CasHostReport*,std::uint32_t);
            auto function=reinterpret_cast<Inspect>(GetProcAddress(module,"CasInspectHost"));
            if (!function) return 8;
            CasHostReport report{};
            observed=function(&report,sizeof(report));
            if (observed!=CAS_UNSUPPORTED_HOST || report.hooks_active) return 9;
            phase("inspect-refused-unsupported-host");
        }
        if (initialize) {
            using Status=std::uint32_t(*)();
            auto start=reinterpret_cast<void(*)()>(GetProcAddress(module,"InitializeASI"));
            auto status=reinterpret_cast<Status>(GetProcAddress(module,"CasRuntimeStatus"));
            if (!start || !status || status()!=0) return 10;
            phase("before-initialize");
            start();
            const auto deadline=GetTickCount64()+10000;
            while (status()==1 && GetTickCount64()<deadline) Sleep(1);
            observed=status();
            if (observed!=2) return 11;
            phase("initialize-refused-unsupported-host");
        }
    }
    std::printf("{\"phase\":\"complete\",\"native_status\":%u,\"hooks_active\":false}\n",observed);
    std::fflush(stdout);
    // Give the instrumentation IPC a bounded drain window, identical in all cases.
    Sleep(200);
    return 0;
}
