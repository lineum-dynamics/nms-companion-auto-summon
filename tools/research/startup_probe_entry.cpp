// Inactive matched-export controls. No player/game initialization is present.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <process.h>
#include <cstdint>
#include "cas/probe.h"

namespace {
volatile LONG status=0;
#ifdef CAS_STARTUP_WORKER
unsigned __stdcall initialize(void*) noexcept {
    CasHostReport report{};
    const auto result=CasInspectHost(&report,sizeof(report));
    // Even a broken diagnostic inspector must never enable gameplay here.
    InterlockedExchange(&status,result==CAS_SUPPORTED_HOST_INERT?3:2);
    return 0;
}
#endif
}
#ifdef CAS_STARTUP_WORKER
// Generated verbatim from the pinned production export tail. It contains
// CasRuntimeStatus, InitializeASI and DllMain, referencing the worker above.
#include "startup_exports.inc"
#else
extern "C" __declspec(dllexport) std::uint32_t CasRuntimeStatus() {
    return static_cast<std::uint32_t>(InterlockedCompareExchange(&status,0,0));
}
extern "C" __declspec(dllexport) void InitializeASI() {
    InterlockedCompareExchange(&status,2,0);
}
BOOL WINAPI DllMain(HINSTANCE,DWORD,LPVOID) { return TRUE; }
#endif
