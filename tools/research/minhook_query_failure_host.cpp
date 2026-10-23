#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <cstdio>
static int scenario;
static SIZE_T WINAPI query_fixture(LPCVOID, PMEMORY_BASIC_INFORMATION info, SIZE_T) {
    *info = {};
    info->State = MEM_COMMIT;
    info->Protect = scenario == 2 ? PAGE_READWRITE : PAGE_EXECUTE_READ;
    // A failed API call has no successful output contract. Model stale
    // executable-looking output to test whether the return code is checked.
    return scenario == 0 ? 0 : sizeof(*info);
}
#define VirtualQuery query_fixture
#include "buffer.c"
#undef VirtualQuery
int main() {
    int failures = 0;
    for (scenario = 0; scenario < 3; ++scenario) {
        const bool expected = scenario == 1;
        const bool actual = IsExecutableAddress(reinterpret_cast<void*>(0x10000)) != FALSE;
        std::printf("scenario=%d expected=%d actual=%d\n",scenario,int(expected),int(actual));
        if (expected != actual) ++failures;
    }
    return failures ? 1 : 0;
}
