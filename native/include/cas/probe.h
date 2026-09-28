#pragma once
#include <stdint.h>

// Fixed C ABI for the inert feasibility probe, not a game-integration API.
#if defined(CAS_PROBE_BUILD)
#define CAS_PROBE_API __declspec(dllexport)
#else
#define CAS_PROBE_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

enum CasProbeStatus {
    CAS_NOT_INITIALIZED = 0,
    CAS_INVALID_ARGUMENT = 1,
    CAS_HOST_READ_FAILED = 2,
    CAS_INVALID_HOST_IMAGE = 3,
    CAS_UNSUPPORTED_HOST = 4,
    CAS_SUPPORTED_HOST_INERT = 5,
    CAS_INITIALIZING = 6
};

typedef struct CasHostReport {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t status;
    uint32_t hooks_active;
    char image_sha256[65];
} CasHostReport;

// Reads only the actual current process's executable. No caller-selected file,
// compatibility override, game pointer, hooks, settings, or save operations.
CAS_PROBE_API uint32_t CasInspectHost(CasHostReport* report, uint32_t report_size);
CAS_PROBE_API uint32_t CasInitializationStatus(void);
// Ultimate ASI Loader's explicit post-load entry point. Still inert in NMS.
CAS_PROBE_API void InitializeASI(void);

#ifdef __cplusplus
}
#endif
