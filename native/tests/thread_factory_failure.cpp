#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdint>
#include "thread_factory_failure.hpp"

namespace { volatile LONG calls=0; }
extern "C" std::uintptr_t __cdecl CasFailBeginThreadEx(
    void*,unsigned,unsigned(__stdcall*)(void*),void*,unsigned,unsigned*) noexcept {
    InterlockedIncrement(&calls);
    return 0;
}
extern "C" __declspec(dllexport) std::uint32_t CasThreadFactoryFailureCalls() {
    return static_cast<std::uint32_t>(InterlockedCompareExchange(&calls,0,0));
}
