// Diagnostic-only adapter: production inspection can never authorize hooks.
#include "cas/probe.h"
extern "C" uint32_t CasInspectHostProduction(CasHostReport*,uint32_t);
extern "C" uint32_t CasInspectHost(CasHostReport* report,uint32_t bytes) {
    const auto result=CasInspectHostProduction(report,bytes);
    if (result==CAS_SUPPORTED_HOST_INERT) {
        report->status=CAS_UNSUPPORTED_HOST;
        report->hooks_active=0;
        return CAS_UNSUPPORTED_HOST;
    }
    return result;
}
