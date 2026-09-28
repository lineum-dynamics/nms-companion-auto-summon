#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <bcrypt.h>
#include <array>
#include <cstring>
#include <cwchar>
#include "cas/probe.h"
#include "compatibility_profile.hpp"

namespace {
#ifndef CAS_NATIVE_RUNTIME
volatile LONG initialization_status = CAS_NOT_INITIALIZED;
#endif

class FileHandle final {
public:
    HANDLE value = INVALID_HANDLE_VALUE;
    ~FileHandle() { if (value != INVALID_HANDLE_VALUE) CloseHandle(value); }
    FileHandle() = default;
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
};

class Sha256 final {
public:
    BCRYPT_ALG_HANDLE algorithm = nullptr;
    BCRYPT_HASH_HANDLE hash = nullptr;
    ~Sha256() {
        if (hash) BCryptDestroyHash(hash);
        if (algorithm) BCryptCloseAlgorithmProvider(algorithm, 0);
    }
    bool initialize() {
        return BCryptOpenAlgorithmProvider(&algorithm, BCRYPT_SHA256_ALGORITHM,
                                            nullptr, 0) >= 0 &&
               BCryptCreateHash(algorithm, &hash, nullptr, 0, nullptr, 0, 0) >= 0;
    }
};

bool read_at(HANDLE file, uint64_t offset, void* bytes, DWORD size) {
    LARGE_INTEGER position{};
    position.QuadPart = static_cast<LONGLONG>(offset);
    DWORD read = 0;
    return SetFilePointerEx(file, position, nullptr, FILE_BEGIN) &&
           ReadFile(file, bytes, size, &read, nullptr) && read == size;
}

uint32_t little32(const unsigned char* bytes) {
    return static_cast<uint32_t>(bytes[0]) |
           (static_cast<uint32_t>(bytes[1]) << 8) |
           (static_cast<uint32_t>(bytes[2]) << 16) |
           (static_cast<uint32_t>(bytes[3]) << 24);
}

bool is_x64_executable(HANDLE file) {
    LARGE_INTEGER size{};
    unsigned char dos[64]{};
    if (!GetFileSizeEx(file, &size) || size.QuadPart < 90 ||
        !read_at(file, 0, dos, sizeof(dos)) || dos[0] != 'M' || dos[1] != 'Z')
        return false;
    const uint32_t offset = little32(dos + 60);
    if (offset < sizeof(dos) || offset > 16 * 1024 * 1024 ||
        static_cast<uint64_t>(offset) + 26 > static_cast<uint64_t>(size.QuadPart))
        return false;
    unsigned char pe[26]{};
    if (!read_at(file, offset, pe, sizeof(pe))) return false;
    return little32(pe) == 0x00004550 && pe[4] == 0x64 && pe[5] == 0x86 &&
           pe[24] == 0x0b && pe[25] == 0x02 && !(pe[23] & 0x20);
}

bool hash_open_file(HANDLE file, char (&hex)[65]) {
    Sha256 sha;
    LARGE_INTEGER start{};
    if (!sha.initialize() || !SetFilePointerEx(file, start, nullptr, FILE_BEGIN))
        return false;
    std::array<unsigned char, 65536> block{};
    DWORD count = 0;
    for (;;) {
        if (!ReadFile(file, block.data(), static_cast<DWORD>(block.size()),
                      &count, nullptr)) return false;
        if (!count) break;
        if (BCryptHashData(sha.hash, block.data(), count, 0) < 0) return false;
    }
    unsigned char digest[32]{};
    if (BCryptFinishHash(sha.hash, digest, sizeof(digest), 0) < 0) return false;
    static constexpr char alphabet[] = "0123456789abcdef";
    for (size_t i = 0; i != sizeof(digest); ++i) {
        hex[i * 2] = alphabet[digest[i] >> 4];
        hex[i * 2 + 1] = alphabet[digest[i] & 15];
    }
    hex[64] = '\0';
    return true;
}
}

extern "C" uint32_t CasInspectHost(CasHostReport* report, uint32_t report_size) {
    if (!report || report_size != sizeof(CasHostReport)) return CAS_INVALID_ARGUMENT;
    *report = {};
    report->struct_size = sizeof(CasHostReport);
    report->abi_version = 1;
    report->status = CAS_HOST_READ_FAILED;
    wchar_t image_path[32768]{};
    DWORD length = GetModuleFileNameW(nullptr, image_path, 32768);
    if (!length || length >= 32768) return report->status;
    FileHandle image;
    // Keep the actual executable handle open without write/delete sharing for
    // both PE validation and hashing. Never resolve a second caller-given path.
    image.value = CreateFileW(image_path, GENERIC_READ, FILE_SHARE_READ, nullptr,
                             OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL |
                             FILE_FLAG_OPEN_REPARSE_POINT, nullptr);
    if (image.value == INVALID_HANDLE_VALUE) return report->status;
    BY_HANDLE_FILE_INFORMATION attributes{};
    if (!GetFileInformationByHandle(image.value, &attributes) ||
        (attributes.dwFileAttributes & (FILE_ATTRIBUTE_REPARSE_POINT |
                                        FILE_ATTRIBUTE_DIRECTORY)))
        return report->status;
    if (!is_x64_executable(image.value)) {
        report->status = CAS_INVALID_HOST_IMAGE;
        return report->status;
    }
    if (!hash_open_file(image.value, report->image_sha256)) return report->status;
    const wchar_t* leaf = std::wcsrchr(image_path, L'\\');
    leaf = leaf ? leaf + 1 : image_path;
    report->status = (_wcsicmp(leaf, L"NMS.exe") == 0 &&
                      std::strcmp(report->image_sha256, cas::profile::exe_sha256) == 0)
        ? CAS_SUPPORTED_HOST_INERT : CAS_UNSUPPORTED_HOST;
    // Even the exact supported game remains inert. No hooks exist in this probe.
    return report->status;
}

#ifndef CAS_NATIVE_RUNTIME
extern "C" uint32_t CasInitializationStatus() {
    return static_cast<uint32_t>(InterlockedCompareExchange(&initialization_status, 0, 0));
}

extern "C" void InitializeASI() {
    if (InterlockedCompareExchange(&initialization_status, CAS_INITIALIZING,
                                    CAS_NOT_INITIALIZED) != CAS_NOT_INITIALIZED)
        return;
    CasHostReport report{};
    const uint32_t result = CasInspectHost(&report, sizeof(report));
    InterlockedExchange(&initialization_status, static_cast<LONG>(result));
}

// Loader-lock restrictions also apply to static constructors: none perform work.
BOOL WINAPI DllMain(HINSTANCE, DWORD, LPVOID) { return TRUE; }
#endif
