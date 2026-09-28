#include "cas/backup.hpp"
#include "json.hpp"

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <bcrypt.h>
#include <sddl.h>

#include <algorithm>
#include <array>
#include <cstdio>
#include <cwctype>
#include <memory>
#include <set>
#include <string>
#include <utility>
#include <vector>

namespace cas {
namespace {
namespace fs = std::filesystem;
using Json = nlohmann::json;
constexpr std::uint64_t max_file_bytes = 256ULL * 1024 * 1024;
constexpr std::uint64_t max_total_bytes = 2ULL * 1024 * 1024 * 1024;
constexpr std::size_t max_files = 4096, max_directories = 4096, max_depth = 32;

[[noreturn]] void fail(const char* message) { throw BackupError(message); }
[[noreturn]] void io_error(const char* message) {
    throw BackupError(std::string(message) + " (Windows error " + std::to_string(GetLastError()) + ")");
}

class Handle {
public:
    explicit Handle(HANDLE value = INVALID_HANDLE_VALUE) : value_(value) {}
    ~Handle() { close(); }
    Handle(const Handle&) = delete;
    Handle& operator=(const Handle&) = delete;
    Handle(Handle&& other) noexcept : value_(std::exchange(other.value_,INVALID_HANDLE_VALUE)) {}
    Handle& operator=(Handle&& other) noexcept {
        if (this != &other) { close(); value_ = std::exchange(other.value_,INVALID_HANDLE_VALUE); }
        return *this;
    }
    HANDLE get() const { return value_; }
    void close() { if (value_ != INVALID_HANDLE_VALUE) CloseHandle(value_); value_ = INVALID_HANDLE_VALUE; }
private:
    HANDLE value_;
};

class PrivateSecurity {
public:
    PrivateSecurity() {
        HANDLE raw_token = INVALID_HANDLE_VALUE;
        if (!OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&raw_token)) io_error("Cannot read snapshot owner token");
        Handle token(raw_token);
        DWORD size = 0;
        GetTokenInformation(token.get(),TokenUser,nullptr,0,&size);
        if (!size) io_error("Cannot inspect snapshot owner token");
        std::vector<unsigned char> buffer(size);
        if (!GetTokenInformation(token.get(),TokenUser,buffer.data(),size,&size)) io_error("Cannot read snapshot owner identity");
        LPWSTR sid = nullptr;
        const auto user = reinterpret_cast<const TOKEN_USER*>(buffer.data());
        if (!ConvertSidToStringSidW(user->User.Sid,&sid)) io_error("Cannot format snapshot owner identity");
        const std::wstring descriptor = std::wstring(L"D:P(A;OICI;FA;;;SY)(A;OICI;FA;;;") + sid + L")";
        LocalFree(sid);
        if (!ConvertStringSecurityDescriptorToSecurityDescriptorW(descriptor.c_str(),SDDL_REVISION_1,&descriptor_,nullptr))
            io_error("Cannot create private snapshot permissions");
        attributes_ = {sizeof(SECURITY_ATTRIBUTES),descriptor_,FALSE};
    }
    ~PrivateSecurity() { if (descriptor_) LocalFree(descriptor_); }
    PrivateSecurity(const PrivateSecurity&) = delete;
    PrivateSecurity& operator=(const PrivateSecurity&) = delete;
    SECURITY_ATTRIBUTES* get() { return &attributes_; }
private:
    PSECURITY_DESCRIPTOR descriptor_{};
    SECURITY_ATTRIBUTES attributes_{};
};

BY_HANDLE_FILE_INFORMATION information(HANDLE file) {
    BY_HANDLE_FILE_INFORMATION result{};
    if (!GetFileInformationByHandle(file,&result)) io_error("Cannot inspect a snapshot handle");
    if (result.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT) fail("Reparse paths are forbidden in backups");
    return result;
}
std::uint64_t size_of(const BY_HANDLE_FILE_INFORMATION& info) {
    return (static_cast<std::uint64_t>(info.nFileSizeHigh) << 32) | info.nFileSizeLow;
}
bool same_file(const BY_HANDLE_FILE_INFORMATION& a, const BY_HANDLE_FILE_INFORMATION& b) {
    return a.dwVolumeSerialNumber == b.dwVolumeSerialNumber && a.nFileIndexHigh == b.nFileIndexHigh &&
        a.nFileIndexLow == b.nFileIndexLow && a.nFileSizeHigh == b.nFileSizeHigh && a.nFileSizeLow == b.nFileSizeLow &&
        a.ftLastWriteTime.dwHighDateTime == b.ftLastWriteTime.dwHighDateTime &&
        a.ftLastWriteTime.dwLowDateTime == b.ftLastWriteTime.dwLowDateTime && a.dwFileAttributes == b.dwFileAttributes;
}

void validate_component(const fs::path& component) {
    const auto value = component.native();
    if (value.empty() || value == L"." || value == L".." || value.back() == L'.' || value.back() == L' ')
        fail("Noncanonical backup path component");
    if (value.find_first_of(L":<>\"|?*") != std::wstring::npos ||
        std::any_of(value.begin(),value.end(),[](wchar_t ch) { return ch < 32; }))
        fail("Unsafe backup path component");
    auto stem = value.substr(0,value.find(L'.'));
    std::transform(stem.begin(),stem.end(),stem.begin(),[](wchar_t ch) { return static_cast<wchar_t>(std::towupper(ch)); });
    if (stem == L"CON" || stem == L"PRN" || stem == L"AUX" || stem == L"NUL" ||
        (stem.size() == 4 && (stem.substr(0,3) == L"COM" || stem.substr(0,3) == L"LPT") && stem[3] >= L'1' && stem[3] <= L'9'))
        fail("Device names are forbidden in backups");
}
fs::path absolute_local(const fs::path& path) {
    if (!path.is_absolute() || path.root_name().native().size() != 2 || path.root_name().native()[1] != L':')
        fail("Backup paths must be explicit local absolute drive paths");
    for (const auto& component : path.relative_path()) validate_component(component);
    return path.lexically_normal();
}
std::wstring folded(const fs::path& path) {
    auto result = path.native();
    std::transform(result.begin(),result.end(),result.begin(),[](wchar_t ch) { return static_cast<wchar_t>(std::towlower(ch)); });
    return result;
}
bool inside(const fs::path& child, const fs::path& parent) {
    const auto c = folded(child), p = folded(parent);
    return c == p || (c.size() > p.size() && c.compare(0,p.size(),p) == 0 &&
           (p.back() == L'\\' || c[p.size()] == L'\\' || c[p.size()] == L'/'));
}
DWORD attributes(const fs::path& path) {
    const DWORD result = GetFileAttributesW(path.c_str());
    if (result == INVALID_FILE_ATTRIBUTES) {
        const auto error = GetLastError();
        if (error == ERROR_FILE_NOT_FOUND || error == ERROR_PATH_NOT_FOUND) return INVALID_FILE_ATTRIBUTES;
        io_error("Cannot inspect a backup path");
    }
    if (result & FILE_ATTRIBUTE_REPARSE_POINT) fail("Reparse paths are forbidden in backups");
    return result;
}
Handle open_directory(const fs::path& path) {
    Handle result(CreateFileW(path.c_str(),FILE_READ_ATTRIBUTES|FILE_LIST_DIRECTORY,
        FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_FLAG_BACKUP_SEMANTICS|FILE_FLAG_OPEN_REPARSE_POINT,nullptr));
    if (result.get() == INVALID_HANDLE_VALUE) io_error("Cannot hold backup directory");
    if (!(information(result.get()).dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) fail("Expected a backup directory");
    return result;
}
// Keep all existing ancestors open without delete sharing. Their names cannot
// be replaced by a junction after validation. Leaf file handles deny writes too.
bool hold_chain(const fs::path& path, std::vector<Handle>& handles, bool allow_absent) {
    auto current = path.root_path();
    handles.push_back(open_directory(current));
    for (const auto& part : path.relative_path()) {
        current /= part;
        if (attributes(current) == INVALID_FILE_ATTRIBUTES) {
            if (allow_absent) return false;
            fail("Required backup parent directory is missing");
        }
        handles.push_back(open_directory(current));
    }
    return true;
}

class Hash {
public:
    Hash() {
        if (BCryptOpenAlgorithmProvider(&algorithm_,BCRYPT_SHA256_ALGORITHM,nullptr,0) < 0) fail("Cannot create SHA-256 provider");
        DWORD bytes = 0, object_size = 0;
        if (BCryptGetProperty(algorithm_,BCRYPT_OBJECT_LENGTH,reinterpret_cast<PUCHAR>(&object_size),sizeof object_size,&bytes,0) < 0) {
            BCryptCloseAlgorithmProvider(algorithm_,0); algorithm_ = nullptr; fail("Cannot inspect SHA-256 provider");
        }
        object_.resize(object_size);
        if (BCryptCreateHash(algorithm_,&hash_,object_.data(),object_size,nullptr,0,0) < 0) {
            BCryptCloseAlgorithmProvider(algorithm_,0); algorithm_ = nullptr; fail("Cannot initialize SHA-256");
        }
    }
    ~Hash() { if (hash_) BCryptDestroyHash(hash_); if (algorithm_) BCryptCloseAlgorithmProvider(algorithm_,0); }
    Hash(const Hash&) = delete;
    Hash& operator=(const Hash&) = delete;
    void add(const unsigned char* data, DWORD count) {
        if (BCryptHashData(hash_,const_cast<PUCHAR>(data),count,0) < 0) fail("Cannot update SHA-256");
    }
    std::string finish() {
        std::array<unsigned char,32> bytes{};
        if (BCryptFinishHash(hash_,bytes.data(),static_cast<ULONG>(bytes.size()),0) < 0) fail("Cannot finish SHA-256");
        constexpr char hex[] = "0123456789abcdef";
        std::string result;
        for (auto value : bytes) { result += hex[value >> 4]; result += hex[value & 15]; }
        return result;
    }
private:
    BCRYPT_ALG_HANDLE algorithm_{};
    BCRYPT_HASH_HANDLE hash_{};
    std::vector<unsigned char> object_;
};
void rewind(HANDLE file) {
    LARGE_INTEGER zero{};
    if (!SetFilePointerEx(file,zero,nullptr,FILE_BEGIN)) io_error("Cannot rewind snapshot file");
}
std::string file_hash(HANDLE file, std::uint64_t expected) {
    rewind(file); Hash hash; std::array<unsigned char,65536> buffer{}; std::uint64_t total = 0;
    for (;;) {
        DWORD count = 0;
        if (!ReadFile(file,buffer.data(),static_cast<DWORD>(buffer.size()),&count,nullptr)) io_error("Cannot hash snapshot file");
        if (!count) break;
        total += count;
        if (total > expected) fail("Snapshot file size changed");
        hash.add(buffer.data(),count);
    }
    if (total != expected) fail("Snapshot file size changed");
    return hash.finish();
}
void write_all(HANDLE file, const unsigned char* data, DWORD length) {
    while (length) {
        DWORD written = 0;
        if (!WriteFile(file,data,length,&written,nullptr) || !written) io_error("Cannot write private snapshot");
        data += written; length -= written;
    }
}
Handle new_file(const fs::path& path) {
    Handle result(CreateFileW(path.c_str(),GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ,nullptr,CREATE_NEW,
                              FILE_ATTRIBUTE_NORMAL|FILE_FLAG_OPEN_REPARSE_POINT,nullptr));
    if (result.get() == INVALID_HANDLE_VALUE) io_error("Cannot create new snapshot file");
    const auto info = information(result.get());
    if ((info.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) || info.nNumberOfLinks != 1) fail("Unexpected snapshot file identity");
    return result;
}
void text_file(HANDLE file, const std::string& text) {
    write_all(file,reinterpret_cast<const unsigned char*>(text.data()),static_cast<DWORD>(text.size()));
    if (!FlushFileBuffers(file)) io_error("Cannot flush snapshot file");
}
void new_directory(const fs::path& path, std::vector<Handle>& handles, SECURITY_ATTRIBUTES* security = nullptr) {
    if (!CreateDirectoryW(path.c_str(),security)) io_error("Cannot create new snapshot directory");
    handles.push_back(open_directory(path));
}

struct Entry {
    fs::path source, relative;
    bool directory = false;
    BY_HANDLE_FILE_INFORMATION info{};
    Handle held;
};
struct Snapshot {
    std::vector<Entry> entries;
    std::size_t files = 0, directories = 0;
    std::uint64_t bytes = 0;
};
void add_file(Snapshot& snapshot, const fs::path& source, const fs::path& relative) {
    if (++snapshot.files > max_files) fail("Snapshot file count exceeds safety limit");
    Handle held(CreateFileW(source.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,
                            FILE_FLAG_OPEN_REPARSE_POINT|FILE_FLAG_SEQUENTIAL_SCAN,nullptr));
    if (held.get() == INVALID_HANDLE_VALUE) io_error("Cannot lock source file read-only; native activation refused");
    const auto info = information(held.get());
    if (info.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) fail("Source file changed into a directory");
    const auto size = size_of(info);
    if (size > max_file_bytes || size > max_total_bytes - snapshot.bytes) fail("Snapshot byte limit exceeded");
    snapshot.bytes += size;
    snapshot.entries.push_back({source,relative,false,info,std::move(held)});
}
std::vector<fs::path> children(const fs::path& root) {
    std::vector<fs::path> result;
    for (const auto& entry : fs::directory_iterator(root)) {
        validate_component(entry.path().filename());
        result.push_back(entry.path());
        if (result.size() > max_files + max_directories) fail("Directory entry count exceeds safety limit");
    }
    std::sort(result.begin(),result.end());
    return result;
}
void collect_tree(Snapshot& snapshot, const fs::path& source, const fs::path& relative, std::size_t depth) {
    if (depth > max_depth || ++snapshot.directories > max_directories) fail("Snapshot directory limit exceeded");
    auto held = open_directory(source);
    const auto info = information(held.get());
    snapshot.entries.push_back({source,relative,true,info,std::move(held)});
    for (const auto& child : children(source)) {
        const auto attr = attributes(child);
        if (attr == INVALID_FILE_ATTRIBUTES) fail("Source entry disappeared during snapshot");
        const auto child_relative = relative / child.filename();
        if (attr & FILE_ATTRIBUTE_DIRECTORY) collect_tree(snapshot,child,child_relative,depth+1);
        else add_file(snapshot,child,child_relative);
    }
}
Snapshot collect(const fs::path& saves, const fs::path& prefs, bool saves_present, bool prefs_present) {
    Snapshot snapshot;
    if (saves_present) collect_tree(snapshot,saves,L"saves",0);
    if (prefs_present) for (const auto* name : {L"settings.json",L"state.json"}) {
        const auto source = prefs / name;
        const auto attr = attributes(source);
        if (attr == INVALID_FILE_ATTRIBUTES) continue;
        if (attr & FILE_ATTRIBUTE_DIRECTORY) fail("Preference file is a directory");
        add_file(snapshot,source,fs::path(L"preferences")/name);
    }
    return snapshot;
}
}

BackupReport verified_pre_activation_backup(const fs::path& save_root, const fs::path& preference_root,
                                           const fs::path& requested_destination) {
    try {
        const auto saves = absolute_local(save_root), prefs = absolute_local(preference_root),
                   destination = absolute_local(requested_destination);
        if (inside(destination,saves) || inside(saves,destination) || inside(prefs,destination) || saves == prefs)
            fail("Snapshot source and destination paths overlap");
        std::vector<Handle> ancestor_handles, destination_handles;
        const bool saves_present = hold_chain(saves,ancestor_handles,true);
        const bool prefs_present = hold_chain(prefs,ancestor_handles,true);
        hold_chain(destination.parent_path(),ancestor_handles,false);
        if (attributes(destination) != INVALID_FILE_ATTRIBUTES) fail("Snapshot destination already exists");
        PrivateSecurity security;
        new_directory(destination,destination_handles,security.get());
        auto incomplete = new_file(destination/L"INCOMPLETE");
        text_file(incomplete.get(),"Incomplete before-native-hooks snapshot. Do not use unless receipt.json is verified.\n");
        auto snapshot = collect(saves,prefs,saves_present,prefs_present);
        if (prefs_present) new_directory(destination/L"preferences",destination_handles);
        Json files = Json::array();
        std::vector<Handle> copied;
        for (auto& entry : snapshot.entries) {
            const auto target = destination/entry.relative;
            if (entry.directory) { new_directory(target,destination_handles); continue; }
            auto output = new_file(target);
            Hash hash; std::array<unsigned char,65536> buffer{}; std::uint64_t total = 0;
            rewind(entry.held.get());
            for (;;) {
                DWORD count = 0;
                if (!ReadFile(entry.held.get(),buffer.data(),static_cast<DWORD>(buffer.size()),&count,nullptr)) io_error("Cannot read locked source file");
                if (!count) break;
                total += count;
                if (total > size_of(entry.info)) fail("Source size changed during copy");
                hash.add(buffer.data(),count); write_all(output.get(),buffer.data(),count);
            }
            if (total != size_of(entry.info) || !FlushFileBuffers(output.get())) fail("Snapshot copy did not finish");
            const auto digest = hash.finish();
            if (file_hash(output.get(),total) != digest || file_hash(entry.held.get(),total) != digest ||
                !same_file(entry.info,information(entry.held.get()))) fail("Snapshot byte or source metadata verification failed");
            files.push_back({{"path",entry.relative.generic_u8string()},{"bytes",total},{"sha256",digest}});
            copied.push_back(std::move(output));
        }
        // All first-pass files remain locked while listing/opening them again.
        if ((attributes(saves) != INVALID_FILE_ATTRIBUTES) != saves_present ||
            (attributes(prefs) != INVALID_FILE_ATTRIBUTES) != prefs_present) fail("Source root presence changed");
        auto second = collect(saves,prefs,saves_present,prefs_present);
        if (second.entries.size() != snapshot.entries.size() || second.files != snapshot.files || second.bytes != snapshot.bytes)
            fail("Source listing changed during snapshot");
        for (std::size_t i = 0; i < snapshot.entries.size(); ++i) {
            const auto& first = snapshot.entries[i]; const auto& again = second.entries[i];
            if (first.relative != again.relative || first.directory != again.directory ||
                !same_file(first.info,again.info)) fail("Source listing or identity changed during snapshot");
        }
        SYSTEMTIME time{}; GetSystemTime(&time);
        char timestamp[32]{};
        std::snprintf(timestamp,sizeof timestamp,"%04u-%02u-%02uT%02u:%02u:%02uZ",
            time.wYear,time.wMonth,time.wDay,time.wHour,time.wMinute,time.wSecond);
        Json receipt{{"schema",1},{"phase","before_native_hooks"},{"game_closed_before_and_after",false},
                     {"created_utc",timestamp},{"sources_write_locked_during_verification",true},
                     {"snapshot_permissions","protected_current_user_and_system"},
                     {"saves_present",saves_present},{"preferences_present",prefs_present},
                     {"files",std::move(files)},{"file_count",snapshot.files},{"bytes",snapshot.bytes}};
        auto receipt_file = new_file(destination/L"receipt.json");
        text_file(receipt_file.get(),receipt.dump(2)+"\n");
        incomplete.close();
        if (!DeleteFileW((destination/L"INCOMPLETE").c_str())) io_error("Cannot finalize snapshot marker");
        return {destination,static_cast<std::uint64_t>(snapshot.files),snapshot.bytes,saves_present,prefs_present};
    } catch (const BackupError&) { throw; }
      catch (const std::exception& error) { throw BackupError(std::string("Snapshot failed: ")+error.what()); }
}

}  // namespace cas
