// Identical inert entry points for every diagnostic component library.
// Linked production functions are retained for static component attribution;
// this library is not a player mod and activates no hooks or game behavior.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdint>

extern "C" __declspec(dllexport) std::uint32_t CasComponentProbeStatus() {
    return 0xC45D0001u;
}
BOOL WINAPI DllMain(HINSTANCE,DWORD,LPVOID) { return TRUE; }
