#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <bcrypt.h>
#include <shlobj.h>
#include "MinHook.h"
#include "cas/probe.h"
#include "cas/runtime.hpp"
#include "cas/menu.hpp"
#include "cas/backup.hpp"
#include "catalog.hpp"
#include "compatibility_profile.hpp"
#include <array>
#include <chrono>
#include <cstring>
#include <filesystem>
#include <iomanip>
#include <memory>
#include <random>
#include <sstream>
#include <vector>

namespace {
using cas::Address;
static_assert(sizeof(void*) == 8 && sizeof(bool) == 1 && sizeof(float) == 4 && sizeof(int) == 4);
volatile LONG status = 0; // 0 idle, 1 initializing, 2 refused, 3 stopped, 4 active
cas::Runtime* runtime = nullptr;
cas::MenuAdapter* menu_adapter = nullptr;
cas::BindingGuard* binding = nullptr;
HANDLE log_file = INVALID_HANDLE_VALUE;
HANDLE instance_mutex = nullptr; // Process lifetime, prevents a second native CAS.
std::mutex log_mutex;
struct File {
    HANDLE h = INVALID_HANDLE_VALUE;
    explicit File(HANDLE value) : h(value) {}
    ~File() { if (h != INVALID_HANDLE_VALUE) CloseHandle(h); }
};
void log(const char* text) noexcept {
    try {
        std::unique_lock<std::mutex> lock(log_mutex,std::try_to_lock);
        if (!lock.owns_lock() || log_file == INVALID_HANDLE_VALUE) return;
        SYSTEMTIME t{}; GetSystemTime(&t); char line[1024]{};
        const auto size = std::snprintf(line,sizeof line,"%04u-%02u-%02uT%02u:%02u:%02u.%03uZ %s\r\n",t.wYear,t.wMonth,t.wDay,t.wHour,t.wMinute,t.wSecond,t.wMilliseconds,text);
        if (size > 0 && static_cast<std::size_t>(size) < sizeof line) { DWORD written{}; WriteFile(log_file,line,static_cast<DWORD>(size),&written,nullptr); }
    } catch (...) {}
}
void require(bool result, const char* message) { if (!result) throw std::runtime_error(message); }
void readMemory(Address address, void* out, std::size_t size) {
    require(address >= 0x10000 && size <= 1024*1024 && address <= 0x7FFFFFFFFFFF-size,"Invalid native read range");
    SIZE_T copied{};
    require(ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(address),out,size,&copied) && copied == size,"Native bounded read failed");
}
void readFile(HANDLE file, std::uint64_t offset, void* out, DWORD size) {
    LARGE_INTEGER pos{}; pos.QuadPart = static_cast<LONGLONG>(offset); DWORD copied{};
    require(SetFilePointerEx(file,pos,nullptr,FILE_BEGIN) && ReadFile(file,out,size,&copied,nullptr) && copied == size,"Native profile file read failed");
}
std::string hash(HANDLE file) {
    BCRYPT_ALG_HANDLE algorithm{}; BCRYPT_HASH_HANDLE context{};
    require(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,nullptr,0) >= 0,"Hash provider unavailable");
    try {
        require(BCryptCreateHash(algorithm,&context,nullptr,0,nullptr,0,0) >= 0,"Hash creation failed");
        LARGE_INTEGER pos{}; require(SetFilePointerEx(file,pos,nullptr,FILE_BEGIN),"Hash seek failed");
        std::array<unsigned char,65536> bytes{}; DWORD count{};
        for (;;) { require(ReadFile(file,bytes.data(),static_cast<DWORD>(bytes.size()),&count,nullptr),"Hash read failed"); if (!count) break;
            require(BCryptHashData(context,bytes.data(),count,0) >= 0,"Hash data failed"); }
        std::array<unsigned char,32> digest{};
        require(BCryptFinishHash(context,digest.data(),static_cast<ULONG>(digest.size()),0) >= 0,"Hash finalization failed");
        BCryptDestroyHash(context); context = nullptr; BCryptCloseAlgorithmProvider(algorithm,0); algorithm = nullptr;
        std::ostringstream out; for (const auto byte : digest) out << std::hex << std::setw(2) << std::setfill('0') << unsigned(byte); return out.str();
    } catch (...) { if (context) BCryptDestroyHash(context); if (algorithm) BCryptCloseAlgorithmProvider(algorithm,0); throw; }
}
std::array<unsigned char,16> prefix(HANDLE image, Address base, std::uint32_t rva) {
    IMAGE_DOS_HEADER dos{}; readFile(image,0,&dos,sizeof dos);
    require(dos.e_magic == IMAGE_DOS_SIGNATURE && dos.e_lfanew >= 64 && dos.e_lfanew <= 0x1000000,"Invalid PE header");
    IMAGE_NT_HEADERS64 nt{}; readFile(image,dos.e_lfanew,&nt,sizeof nt);
    require(nt.Signature == IMAGE_NT_SIGNATURE && nt.FileHeader.Machine == IMAGE_FILE_MACHINE_AMD64 && nt.FileHeader.NumberOfSections <= 96,"Invalid x64 image");
    for (unsigned i = 0; i < nt.FileHeader.NumberOfSections; ++i) {
        IMAGE_SECTION_HEADER section{};
        readFile(image,dos.e_lfanew+24+nt.FileHeader.SizeOfOptionalHeader+i*sizeof section,&section,sizeof section);
        if (rva >= section.VirtualAddress && std::uint64_t(rva)+16 <= std::uint64_t(section.VirtualAddress)+section.SizeOfRawData) {
            require((section.Characteristics & IMAGE_SCN_MEM_EXECUTE) != 0,"Native target is not executable");
            std::array<unsigned char,16> expected{}, actual{};
            readFile(image,section.PointerToRawData+(rva-section.VirtualAddress),expected.data(),16);
            readMemory(base+rva,actual.data(),16);
            require(actual == expected,"Native target already modified; refusing competing hooks");
            return expected;
        }
    }
    throw std::runtime_error("Native target outside executable sections");
}
std::filesystem::path knownFolder(REFKNOWNFOLDERID id) {
    PWSTR value{}; require(SUCCEEDED(SHGetKnownFolderPath(id,KF_FLAG_DEFAULT,nullptr,&value)),"User directory unavailable");
    const std::filesystem::path result(value); CoTaskMemFree(value); return result;
}
void safeDirectory(const std::filesystem::path& path) {
    require(path.is_absolute(),"Expected absolute private directory");
    std::filesystem::path current;
    for (const auto& component : path) {
        current /= component;
        const auto attributes = GetFileAttributesW(current.c_str());
        if (attributes != INVALID_FILE_ATTRIBUTES)
            require((attributes & FILE_ATTRIBUTE_DIRECTORY) && !(attributes & FILE_ATTRIBUTE_REPARSE_POINT),"Private directory is not a plain directory");
    }
    std::filesystem::create_directories(path);
}
std::string systemLanguage() {
    wchar_t name[LOCALE_NAME_MAX_LENGTH]{};
    if (!GetUserDefaultLocaleName(name,LOCALE_NAME_MAX_LENGTH)) return "en";
    std::wstring code(name);
    if (code.rfind(L"zh",0) == 0) return code.find(L"TW") != code.npos || code.find(L"HK") != code.npos || code.find(L"Hant") != code.npos ? "zh-Hant" : "zh-Hans";
    if (code.rfind(L"pt",0) == 0) return code.find(L"BR") != code.npos ? "pt-BR" : "pt-PT";
    if (code.rfind(L"es",0) == 0) return "es-ES";
    std::string result; for (const auto c : code) { if (c == L'-') break; if (c < 128) result += static_cast<char>(c); }
    return result;
}
std::wstring wide(const std::string& text) {
    const auto size = MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,text.data(),static_cast<int>(text.size()),nullptr,0);
    require(size > 0,"Invalid UTF-8 notice"); std::wstring value(size,L'\0');
    require(MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,text.data(),static_cast<int>(text.size()),value.data(),size) == size,"UTF-8 conversion failed"); return value;
}
void errorNotice(const char* key) noexcept {
    try { const auto language = systemLanguage();
        auto text = cas::catalog::replace(cas::catalog::text(key,language.c_str()),"{build}",cas::profile::steam_build);
        MessageBoxW(nullptr,wide(text).c_str(),wide(cas::catalog::text("launcher.blocked_title",language.c_str())).c_str(),MB_OK|MB_ICONWARNING);
    } catch (...) {}
}

using Update = void(*)(void*,float);
using Queue = void(*)(void*,int);
using Eject = void(*)(void*,void*,bool,bool);
using One = void(*)(void*);
using Two = void(*)(void*,void*);
using Trigger = bool(*)(void*,void*,bool);
using Load = bool(*)(void*,void*,void*,bool,bool,std::uint32_t);
using Confirm = bool(*)(void*);
Queue queue_original{}; Update player_original{}, owner_original{};
Eject eject_original{}; One enter_original{}, resources_original{};
Load load_original{}; Trigger trigger_original{}; Two builder_original{}, label_original{};
Confirm confirm_original{}; cas::MenuAppend append_original{};

bool active() noexcept { return InterlockedCompareExchange(&status,0,0) == 4; }
void queueHook(void* player,int slot) { const bool started=active(); queue_original(player,slot); if (started && active() && runtime) runtime->afterQueue(reinterpret_cast<Address>(player),slot); }
void playerHook(void* player,float dt) { const bool started=active(); player_original(player,dt); if (started && active() && runtime) runtime->afterPlayer(reinterpret_cast<Address>(player),dt); }
void ownerHook(void* owner,float dt) { const bool started=active(); owner_original(owner,dt); if (started && active() && runtime) runtime->afterOwner(reinterpret_cast<Address>(owner),dt); }
void ejectHook(void* ship,void* player,bool animate,bool force) { const bool started=active(); eject_original(ship,player,animate,force); if (started && active() && runtime) runtime->afterExit(reinterpret_cast<Address>(player)); }
void enterHook(void* player) { if (active() && runtime) runtime->beforeEnter(reinterpret_cast<Address>(player)); enter_original(player); }
bool loadHook(void* player,void* common,void* state,bool network,bool resetting,std::uint32_t extra) {
    const bool started=active();
    if (started && runtime) runtime->beforeLoad(network); const bool result = load_original(player,common,state,network,resetting,extra);
    if (started && active() && runtime) runtime->afterLoad(reinterpret_cast<Address>(common),network,result); return result;
}
bool triggerHook(void* menu,void* action,bool called) {
    const bool started=active();
    if (started && runtime) runtime->beforeAction(reinterpret_cast<Address>(menu),reinterpret_cast<Address>(action),called);
    if (started && menu_adapter) menu_adapter->beforeTrigger(menu,action,called);
    const bool result = trigger_original(menu,action,called);
    if (started && active() && menu_adapter) menu_adapter->afterTrigger(menu,action,called,result);
    if (started && active() && runtime) runtime->afterAction(reinterpret_cast<Address>(menu),reinterpret_cast<Address>(action),called,result);
    return result;
}
void builderHook(void* menu,void* render) {
    const bool started=active();
    if (started && menu_adapter) menu_adapter->beforeBuilder(menu,render); builder_original(menu,render);
    if (started && active() && menu_adapter) menu_adapter->afterBuilder(menu,render);
}
void labelHook(void* menu,void* out) { const bool started=active(); label_original(menu,out); if (started && active() && menu_adapter) menu_adapter->afterLabel(menu,out); }
void* appendHook(void* header,void* incoming) { if (active() && menu_adapter) menu_adapter->beforeAppend(header,incoming); return append_original(header,incoming); }
bool confirmHook(void* menu) {
    const bool started=active();
    if (started && menu_adapter) menu_adapter->beforeConfirmation(menu); const bool result = confirm_original(menu);
    if (started && active() && menu_adapter) menu_adapter->afterConfirmation(menu,result); return result;
}
void resourcesHook(void* menu) { const bool started=active(); resources_original(menu); if (started && active() && menu_adapter) menu_adapter->afterResources(menu); }

struct Hook { std::uint32_t rva; void* callback; void** original; };
template<class F> void* function(F pointer) { return reinterpret_cast<void*>(pointer); }
std::vector<Hook> hooks() {
    return {{0x146AC90,function(queueHook),reinterpret_cast<void**>(&queue_original)},
            {0x1440CD0,function(playerHook),reinterpret_cast<void**>(&player_original)},
            {0x5066A0,function(ownerHook),reinterpret_cast<void**>(&owner_original)},
            {0x17479D0,function(ejectHook),reinterpret_cast<void**>(&eject_original)},
            {0x1479490,function(enterHook),reinterpret_cast<void**>(&enter_original)},
            {0x56FA50,function(loadHook),reinterpret_cast<void**>(&load_original)},
            {0x1526940,function(triggerHook),reinterpret_cast<void**>(&trigger_original)},
            {0x151ED00,function(builderHook),reinterpret_cast<void**>(&builder_original)},
            {0x1523220,function(labelHook),reinterpret_cast<void**>(&label_original)},
            {0x1533980,function(appendHook),reinterpret_cast<void**>(&append_original)},
            {0x15311C0,function(confirmHook),reinterpret_cast<void**>(&confirm_original)},
            {0x151AD80,function(resourcesHook),reinterpret_cast<void**>(&resources_original)}};
}

DWORD WINAPI initialize(void*) noexcept {
    bool is_game = false;
    std::vector<void*> created;
    try {
        wchar_t path[32768]{}; const auto length = GetModuleFileNameW(nullptr,path,32768);
        require(length && length < 32768,"Actual host path unavailable");
        is_game = _wcsicmp(std::filesystem::path(path).filename().c_str(),L"NMS.exe") == 0;
        CasHostReport report{};
        const auto inspection = CasInspectHost(&report,sizeof report);
        if (inspection != CAS_SUPPORTED_HOST_INERT) {
            InterlockedExchange(&status,2);
            if (is_game) errorNotice(inspection == CAS_UNSUPPORTED_HOST ? "launcher.unsupported_game" : "launcher.unreadable_game");
            return 0;
        }
        File image(CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_FLAG_OPEN_REPARSE_POINT,nullptr));
        require(image.h != INVALID_HANDLE_VALUE && hash(image.h) == cas::profile::exe_sha256,"Host changed after inspection");
        require(!GetModuleHandleW(L"python311.dll") && !GetModuleHandleW(L"python312.dll") && !GetModuleHandleW(L"python313.dll"),"Competing Python runtime is present");
        const auto base = reinterpret_cast<Address>(GetModuleHandleW(nullptr));
        const auto definitions = hooks();
        for (const auto& hook : definitions) prefix(image.h,base,hook.rva);
        for (const auto rva : {0x146A410u,0x505B70u,0x1438040u,0x60B770u,0x9B8300u,0x1432FC0u,0x150FAC0u,0xEC0670u,0x2D5C890u}) prefix(image.h,base,rva);
        const auto binding_prefix = prefix(image.h,base,0x2C1DDE0);
        wchar_t name[128]{}; std::swprintf(name,128,L"Local\\CompanionAutoSummon.Native.%lu",GetCurrentProcessId());
        instance_mutex = CreateMutexW(nullptr,FALSE,name);
        require(instance_mutex && GetLastError() != ERROR_ALREADY_EXISTS,"Another native CAS instance exists");
        const auto data = knownFolder(FOLDERID_LocalAppData) / L"NMS-AutoPet";
        safeDirectory(data / L"logs"); safeDirectory(data / L"backups");
        SYSTEMTIME now{}; GetSystemTime(&now); wchar_t stamp[80]{};
        std::swprintf(stamp,80,L"%04u%02u%02uT%02u%02u%02u-%lu-native",now.wYear,now.wMonth,now.wDay,now.wHour,now.wMinute,now.wSecond,GetCurrentProcessId());
        const auto log_path = data / L"logs" / (std::wstring(stamp)+L".log");
        log_file = CreateFileW(log_path.c_str(),FILE_APPEND_DATA,FILE_SHARE_READ,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
        require(log_file != INVALID_HANDLE_VALUE,"Private log unavailable");
        log("Native initialization: actual executable verified; no native hooks active yet");
        cas::verified_pre_activation_backup(knownFolder(FOLDERID_RoamingAppData)/L"HelloGames"/L"NMS",data,data/L"backups"/stamp);
        log("Verified private pre-activation snapshot completed; this is not a closed-game pre-launch backup");
        cas::RuntimeServices services;
        services.base = base; services.read = readMemory; services.log = log;
        services.allow_menu_change = [] { return menu_adapter && !menu_adapter->stopped(); };
        services.clock = [] { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); };
        services.random = [](std::size_t bound) {
            require(bound > 0 && bound <= 10000,"Invalid random bound");
            std::uint64_t value{}, maximum = UINT64_MAX - (UINT64_MAX % bound);
            do { require(BCryptGenRandom(nullptr,reinterpret_cast<PUCHAR>(&value),sizeof value,BCRYPT_USE_SYSTEM_PREFERRED_RNG) >= 0,"Random provider unavailable"); } while (value >= maximum);
            return static_cast<std::size_t>(value % bound);
        };
        services.owned = [base](Address owner,int slot) { return reinterpret_cast<bool(*)(void*,int)>(base+0x505B70)(reinterpret_cast<void*>(owner),slot); };
        services.can_summon = [base](Address player,int slot) { return reinterpret_cast<bool(*)(void*,int)>(base+0x146A410)(reinterpret_cast<void*>(player),slot); };
        services.use_hand = [base] { return reinterpret_cast<bool(*)()>(base+0x60B770)(); };
        services.placement = [base](Address arc,float a,float b,std::uint32_t hand) { reinterpret_cast<void(*)(void*,float,float,std::uint32_t)>(base+0x1438040)(reinterpret_cast<void*>(arc),a,b,hand); };
        // This original trampoline bypasses only our own attribution detour.
        services.queue = [](Address player,int slot) { queue_original(reinterpret_cast<void*>(player),slot); };
        services.notice = [base](Address app,const std::string& message) {
            alignas(16) float colour[4]{1,1,1,1};
            std::uint32_t icon = menu_adapter ? menu_adapter->notificationIcon() : 0;
            using Notice = void(*)(void*,void*,float,void*,std::uint32_t,void*,bool,float,bool,bool,bool);
            reinterpret_cast<Notice>(base+0x9B8300)(reinterpret_cast<void*>(app+0x837B40),const_cast<char*>(message.c_str()),5.5f,colour,0,&icon,false,0.f,false,false,icon == 0);
        };
        runtime = new cas::Runtime(std::move(services),data);
        binding = new cas::BindingGuard(); menu_adapter = new cas::MenuAdapter();
        require(MH_Initialize() == MH_OK,"MinHook initialization failed");
        for (const auto& hook : definitions) {
            auto* target = reinterpret_cast<void*>(base+hook.rva);
            // Backup and preparation can take time. Reject a hook introduced
            // since the initial compatibility pass immediately before creation.
            prefix(image.h,base,hook.rva);
            require(MH_CreateHook(target,hook.callback,hook.original) == MH_OK,"Native hook creation failed");
            created.push_back(target);
        }
        require(binding->install(base,binding_prefix),"Native binding guard unavailable");
        cas::MenuCallbacks callbacks;
        callbacks.context = runtime;
        callbacks.caption = [](void* context,int role,char* out) { return static_cast<cas::Runtime*>(context)->caption(role,out); };
        callbacks.capture = [](void* context,int role,std::uint64_t* revision) { return static_cast<cas::Runtime*>(context)->capture(role,revision); };
        callbacks.change = [](void* context,int role,std::uint64_t revision) { return static_cast<cas::Runtime*>(context)->change(role,revision); };
        callbacks.log = [](void*,const char* message) { log(message); };
        require(menu_adapter->initialize(base,binding,append_original,callbacks),"Native menu initialization failed");
        for (const auto target : created) require(MH_QueueEnableHook(target) == MH_OK,"Native hook enable queue failed");
        require(MH_ApplyQueued() == MH_OK,"Native hook activation failed");
        InterlockedExchange(&status,4); log("Native CAS active: twelve game hooks and binding guard; menu and automation enabled");
    } catch (const std::exception& error) {
        log(error.what()); InterlockedExchange(&status,3);
        // Keep all code, callback owners and trampolines pinned. Disable only
        // the hooks created by this initializer; never remove foreign hooks.
        for (auto* target : created)
            if (MH_QueueDisableHook(target) != MH_OK) log("Owned hook disable could not be queued; activation gate remains closed");
        if (!created.empty() && MH_ApplyQueued() != MH_OK)
            log("Owned hook rollback incomplete; activation gate remains closed and owners stay pinned");
        if (is_game) errorNotice("native.activation_failed");
    } catch (...) {
        log("Unexpected native initialization failure"); InterlockedExchange(&status,3);
        for (auto* target : created)
            if (MH_QueueDisableHook(target) != MH_OK) log("Owned hook disable could not be queued; activation gate remains closed");
        if (!created.empty() && MH_ApplyQueued() != MH_OK)
            log("Owned hook rollback incomplete; activation gate remains closed and owners stay pinned");
        if (is_game) errorNotice("native.activation_failed");
    }
    return 0;
}
}
extern "C" __declspec(dllexport) std::uint32_t CasRuntimeStatus() {
    return static_cast<std::uint32_t>(InterlockedCompareExchange(&status,0,0));
}
extern "C" __declspec(dllexport) void InitializeASI() {
    if (InterlockedCompareExchange(&status,1,0) != 0) return;
    HMODULE pinned{};
    if (!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&InitializeASI),&pinned)) { InterlockedExchange(&status,3); return; }
    // No wait: the worker starts only once Windows releases loader serialization.
    const auto thread = CreateThread(nullptr,0,initialize,nullptr,0,nullptr);
    if (!thread) InterlockedExchange(&status,3); else CloseHandle(thread);
}
BOOL WINAPI DllMain(HINSTANCE,DWORD,LPVOID) { return TRUE; }
