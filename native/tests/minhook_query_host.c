/* Owned fault test for the actual MinHook C helper; no game access. */
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    const char *name;
    SIZE_T returned;
    DWORD state;
    DWORD protect;
    BOOL expected;
} QueryCase;
static const QueryCase cases[] = {
    {"failed_stale_executable", 0, MEM_COMMIT, PAGE_EXECUTE_READ, FALSE},
    {"short_stale_executable", sizeof(MEMORY_BASIC_INFORMATION)-1, MEM_COMMIT, PAGE_EXECUTE_READ, FALSE},
    {"oversized_stale_executable", sizeof(MEMORY_BASIC_INFORMATION)+1, MEM_COMMIT, PAGE_EXECUTE_READ, FALSE},
    {"failed_zero_output", 0, 0, 0, FALSE},
    {"execute", sizeof(MEMORY_BASIC_INFORMATION), MEM_COMMIT, PAGE_EXECUTE, TRUE},
    {"execute_read", sizeof(MEMORY_BASIC_INFORMATION), MEM_COMMIT, PAGE_EXECUTE_READ, TRUE},
    {"execute_readwrite", sizeof(MEMORY_BASIC_INFORMATION), MEM_COMMIT, PAGE_EXECUTE_READWRITE, TRUE},
    {"execute_writecopy", sizeof(MEMORY_BASIC_INFORMATION), MEM_COMMIT, PAGE_EXECUTE_WRITECOPY, TRUE},
    {"readwrite", sizeof(MEMORY_BASIC_INFORMATION), MEM_COMMIT, PAGE_READWRITE, FALSE},
    {"readonly", sizeof(MEMORY_BASIC_INFORMATION), MEM_COMMIT, PAGE_READONLY, FALSE},
    {"noaccess", sizeof(MEMORY_BASIC_INFORMATION), MEM_COMMIT, PAGE_NOACCESS, FALSE},
    {"writecopy", sizeof(MEMORY_BASIC_INFORMATION), MEM_COMMIT, PAGE_WRITECOPY, FALSE},
    {"reserved_executable", sizeof(MEMORY_BASIC_INFORMATION), MEM_RESERVE, PAGE_EXECUTE_READ, FALSE},
    {"free_executable", sizeof(MEMORY_BASIC_INFORMATION), MEM_FREE, PAGE_EXECUTE_READ, FALSE},
    /* Preserve upstream classification of modifier bits; no new policy here. */
    {"execute_guard_modifier", sizeof(MEMORY_BASIC_INFORMATION), MEM_COMMIT, PAGE_EXECUTE_READ|PAGE_GUARD, TRUE},
    {"execute_nocache_modifier", sizeof(MEMORY_BASIC_INFORMATION), MEM_COMMIT, PAGE_EXECUTE_READ|PAGE_NOCACHE, TRUE}
};
static size_t active_case;
static unsigned query_calls;
static SIZE_T WINAPI query_fixture(LPCVOID address, PMEMORY_BASIC_INFORMATION info, SIZE_T size) {
    const QueryCase *item = &cases[active_case];
    (void)address;
    ++query_calls;
    if (size != sizeof(*info)) return 0;
    memset(info, 0, sizeof(*info));
    info->State = item->state;
    info->Protect = item->protect;
    return item->returned;
}
#define VirtualQuery query_fixture
#include "../third_party/minhook/src/buffer.c"
#undef VirtualQuery

int main(void) {
    unsigned failures = 0;
    for (active_case=0; active_case<sizeof(cases)/sizeof(cases[0]); ++active_case) {
        BOOL actual;
        query_calls = 0;
        actual = IsExecutableAddress((LPVOID)(ULONG_PTR)0x10000);
        if (actual != cases[active_case].expected || query_calls != 1) {
            fprintf(stderr, "Query case failed: %s\n", cases[active_case].name);
            ++failures;
        }
    }
    printf("{\"passed\":%s,\"cases\":%u,\"failed\":%u,\"game_access\":false}\n",
           failures ? "false" : "true", (unsigned)active_case, failures);
    return failures ? 1 : 0;
}
