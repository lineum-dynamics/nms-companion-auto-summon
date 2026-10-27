#pragma once
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#ifdef __cplusplus
extern "C" {
#endif
HANDLE WINAPI CasAuditOpenThread(DWORD, BOOL, DWORD);
DWORD WINAPI CasAuditSuspendThread(HANDLE);
DWORD WINAPI CasAuditResumeThread(HANDLE);
BOOL WINAPI CasAuditGetThreadContext(HANDLE, LPCONTEXT);
BOOL WINAPI CasAuditSetThreadContext(HANDLE, const CONTEXT*);
LPVOID WINAPI CasAuditVirtualAlloc(LPVOID, SIZE_T, DWORD, DWORD);
BOOL WINAPI CasAuditVirtualProtect(LPVOID, SIZE_T, DWORD, PDWORD);
BOOL WINAPI CasAuditFlushInstructionCache(HANDLE, LPCVOID, SIZE_T);
#ifdef __cplusplus
}
#endif

// Only MinHook C objects get these substitutions. The recorder/host invokes
// real Windows APIs and introduces no other thread into the tested process.
#ifdef CAS_AUDIT_WRAP_APIS
#define OpenThread CasAuditOpenThread
#define SuspendThread CasAuditSuspendThread
#define ResumeThread CasAuditResumeThread
#define GetThreadContext CasAuditGetThreadContext
#define SetThreadContext CasAuditSetThreadContext
#define VirtualAlloc CasAuditVirtualAlloc
#define VirtualProtect CasAuditVirtualProtect
#define FlushInstructionCache CasAuditFlushInstructionCache
#endif
