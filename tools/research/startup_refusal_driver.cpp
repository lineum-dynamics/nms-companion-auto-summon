// Owned synthetic enum/ABI control, with no executable/file/game inspection.
#include "cas/probe.h"
#include <cstdio>
namespace { uint32_t synthetic_result=CAS_SUPPORTED_HOST_INERT; }
extern "C" uint32_t CasInspectHostProduction(CasHostReport* report,uint32_t bytes) {
    if (!report || bytes!=sizeof(CasHostReport)) return CAS_INVALID_ARGUMENT;
    *report={};
    report->struct_size=sizeof(CasHostReport);
    report->abi_version=1;
    report->status=synthetic_result;
    return synthetic_result;
}
int main() {
    CasHostReport report{};
    if (CasInspectHost(nullptr,0)!=CAS_INVALID_ARGUMENT) return 2;
    if (CasInspectHost(&report,sizeof(report))!=CAS_UNSUPPORTED_HOST ||
        report.status!=CAS_UNSUPPORTED_HOST || report.hooks_active) return 3;
    const uint32_t ordinary[]={CAS_HOST_READ_FAILED,CAS_INVALID_HOST_IMAGE,CAS_UNSUPPORTED_HOST};
    for (auto result:ordinary) {
        synthetic_result=result;
        if (CasInspectHost(&report,sizeof(report))!=result || report.status!=result) return 4;
    }
    std::printf("{\"passed\":true,\"synthetic_supported_result_refused\":true,"
                "\"ordinary_errors_preserved\":true,\"game_access\":false}\n");
    return 0;
}
