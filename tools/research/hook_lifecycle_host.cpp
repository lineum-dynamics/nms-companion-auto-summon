// Source-instrumented MinHook fixture. Targets, worker and memory are owned.
#define NOMINMAX
#include "hook_audit_api.h"
#include "MinHook.h"
#include <array>
#include <cstdio>
#include <cstring>
#include <cwchar>

namespace {
struct Counts {
    unsigned opened{}, suspended{}, resumed{}, got_context{}, set_context{};
    unsigned allocations{}, executable_allocations{}, writable_code{}, restored{}, flushed{};
    unsigned foreign_threads{}, foreign_process{}, failed{}, own_worker_suspends{};
} counts;
DWORD worker_id{};
bool own(HANDLE thread) {
    const DWORD pid=GetProcessIdOfThread(thread);
    if (pid!=GetCurrentProcessId()) { ++counts.foreign_threads; return false; }
    return true;
}
void result(bool ok) { if (!ok) ++counts.failed; }
HANDLE stop_event{};
DWORD WINAPI worker(void*) { return WaitForSingleObject(stop_event,10000)==WAIT_OBJECT_0?0:1; }
using Function=int(*)(int);
Function original{};
__declspec(noinline) int target(int value) { volatile int local=value+17; return local+1; }
__declspec(noinline) int detour(int value) { return original(value)+1000; }
Function volatile invoke=target;
bool allowed() {
    wchar_t enabled[16]{},repository[128]{},image[32768]{};
    if (!GetEnvironmentVariableW(L"GITHUB_ACTIONS",enabled,16) ||
        !GetEnvironmentVariableW(L"GITHUB_REPOSITORY",repository,128) ||
        !GetModuleFileNameW(nullptr,image,32768)) return false;
    const wchar_t* leaf=std::wcsrchr(image,L'\\'); leaf=leaf?leaf+1:image;
    return !std::wcscmp(enabled,L"true") &&
        !std::wcscmp(repository,L"lineum-dynamics/nms-companion-auto-summon") &&
        !_wcsicmp(leaf,L"cas-hook-lifecycle-host.exe");
}
}

extern "C" HANDLE WINAPI CasAuditOpenThread(DWORD rights,BOOL inherit,DWORD id) {
    HANDLE h=OpenThread(rights,inherit,id);
    if (h) { ++counts.opened; own(h); } else ++counts.failed;
    return h;
}
extern "C" DWORD WINAPI CasAuditSuspendThread(HANDLE h) {
    own(h); DWORD value=SuspendThread(h); result(value!=DWORD(-1));
    if (value!=DWORD(-1)) { ++counts.suspended; if (GetThreadId(h)==worker_id) ++counts.own_worker_suspends; }
    return value;
}
extern "C" DWORD WINAPI CasAuditResumeThread(HANDLE h) {
    own(h); DWORD value=ResumeThread(h); result(value!=DWORD(-1));
    if (value!=DWORD(-1)) ++counts.resumed;
    return value;
}
extern "C" BOOL WINAPI CasAuditGetThreadContext(HANDLE h,LPCONTEXT context) {
    own(h); BOOL ok=GetThreadContext(h,context); result(ok!=FALSE);
    if (ok) ++counts.got_context; return ok;
}
extern "C" BOOL WINAPI CasAuditSetThreadContext(HANDLE h,const CONTEXT* context) {
    own(h); BOOL ok=SetThreadContext(h,context); result(ok!=FALSE);
    if (ok) ++counts.set_context; return ok;
}
extern "C" LPVOID WINAPI CasAuditVirtualAlloc(LPVOID address,SIZE_T size,DWORD type,DWORD protect) {
    LPVOID value=VirtualAlloc(address,size,type,protect);
    if (value) { ++counts.allocations; if (protect==PAGE_EXECUTE_READWRITE) ++counts.executable_allocations; }
    return value; // Failed near-address allocation probes are normal search attempts.
}
extern "C" BOOL WINAPI CasAuditVirtualProtect(LPVOID address,SIZE_T size,DWORD protect,PDWORD old) {
    BOOL ok=VirtualProtect(address,size,protect,old); result(ok!=FALSE);
    if (ok) { if (protect==PAGE_EXECUTE_READWRITE) ++counts.writable_code; else ++counts.restored; }
    return ok;
}
extern "C" BOOL WINAPI CasAuditFlushInstructionCache(HANDLE process,LPCVOID address,SIZE_T size) {
    if (process!=GetCurrentProcess()) ++counts.foreign_process;
    BOOL ok=FlushInstructionCache(process,address,size); result(ok!=FALSE);
    if (ok) ++counts.flushed; return ok;
}

int main() {
    if (!allowed()) return 2;
    stop_event=CreateEventW(nullptr,TRUE,FALSE,nullptr);
    if (!stop_event) return 3;
    HANDLE thread=CreateThread(nullptr,0,worker,nullptr,0,&worker_id);
    if (!thread) return 4;
    std::array<unsigned char,16> before{};
    void* code=reinterpret_cast<void*>(target);
    std::memcpy(before.data(),code,before.size());
    MEMORY_BASIC_INFORMATION initial{},final{};
    bool ok=VirtualQuery(code,&initial,sizeof(initial))==sizeof(initial) && invoke(4)==22;
    ok=ok && MH_Initialize()==MH_OK;
    ok=ok && MH_CreateHook(code,reinterpret_cast<void*>(detour),reinterpret_cast<void**>(&original))==MH_OK;
    ok=ok && invoke(4)==22;
    ok=ok && MH_QueueEnableHook(code)==MH_OK && MH_ApplyQueued()==MH_OK && invoke(4)==1022;
    ok=ok && MH_QueueDisableHook(code)==MH_OK && MH_ApplyQueued()==MH_OK && invoke(4)==22;
    ok=ok && !std::memcmp(before.data(),code,before.size());
    ok=ok && MH_RemoveHook(code)==MH_OK && MH_Uninitialize()==MH_OK;
    ok=ok && VirtualQuery(code,&final,sizeof(final))==sizeof(final) && initial.Protect==final.Protect;
    SetEvent(stop_event);
    const bool worker_exited=WaitForSingleObject(thread,5000)==WAIT_OBJECT_0;
    DWORD worker_exit=STILL_ACTIVE; GetExitCodeThread(thread,&worker_exit);
    CloseHandle(thread); CloseHandle(stop_event);
    ok=ok && worker_exited && worker_exit==0 && counts.own_worker_suspends>=2 &&
        counts.suspended==counts.resumed && counts.got_context>=2 &&
        counts.writable_code==counts.restored && counts.flushed>=2 &&
        !counts.foreign_threads && !counts.foreign_process && !counts.failed;
    std::printf("{\"passed\":%s,\"game_access\":false,\"scope\":\"source-instrumented owned hook fixture\","
        "\"thread_opened\":%u,\"suspended\":%u,\"resumed\":%u,\"get_context\":%u,\"set_context\":%u,"
        "\"own_worker_suspends\":%u,\"allocations\":%u,\"executable_allocations\":%u,"
        "\"writable_code\":%u,\"protection_restores\":%u,\"cache_flushes\":%u,"
        "\"foreign_threads\":%u,\"foreign_process_handles\":%u,\"failed_operations\":%u,"
        "\"worker_exited\":%s,\"target_bytes_restored\":%s}\n",ok?"true":"false",
        counts.opened,counts.suspended,counts.resumed,counts.got_context,counts.set_context,
        counts.own_worker_suspends,counts.allocations,counts.executable_allocations,
        counts.writable_code,counts.restored,counts.flushed,counts.foreign_threads,
        counts.foreign_process,counts.failed,worker_exited?"true":"false",
        !std::memcmp(before.data(),code,before.size())?"true":"false");
    return ok?0:5;
}
