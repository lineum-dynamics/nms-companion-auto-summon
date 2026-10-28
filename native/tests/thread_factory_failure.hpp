#pragma once
#include <process.h>
#include <cstdint>

// Included only while building the owned fault-injected DLL. Original CRT
// declarations are parsed before substituting the single factory call.
extern "C" std::uintptr_t __cdecl CasFailBeginThreadEx(
    void*,unsigned,unsigned(__stdcall*)(void*),void*,unsigned,unsigned*) noexcept;
#define _beginthreadex CasFailBeginThreadEx
