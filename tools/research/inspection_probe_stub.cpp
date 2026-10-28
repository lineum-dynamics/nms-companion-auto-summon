// Inert ABI-matched control, never a replacement for the production guard.
#include "cas/probe.h"
extern "C" uint32_t CasInspectHost(CasHostReport* report,uint32_t bytes) {
    if (!report || bytes!=sizeof(CasHostReport)) return CAS_INVALID_ARGUMENT;
    *report={};
    report->struct_size=sizeof(CasHostReport);
    report->abi_version=1;
    report->status=CAS_UNSUPPORTED_HOST;
    return report->status;
}
