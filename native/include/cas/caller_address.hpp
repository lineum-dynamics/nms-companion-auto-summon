#pragma once

// This must expand at the native callback, not inside a helper function:
// the filter needs the game's caller, rather than a wrapper's return address.
#if defined(_MSC_VER)
#include <intrin.h>
#pragma intrinsic(_ReturnAddress)
#define CAS_CALLER_ADDRESS() _ReturnAddress()
#elif defined(__clang__) || defined(__GNUC__)
#define CAS_CALLER_ADDRESS() __builtin_return_address(0)
#else
#error Unsupported compiler for native callback attribution
#endif
