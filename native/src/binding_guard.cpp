#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <algorithm>
#include <cstring>
#include <stdexcept>
#include <string>
#include <utility>
#include "cas/binding_guard.hpp"
#ifndef CAS_MENU_FIXTURE
#include "MinHook.h"
#endif

namespace cas {
namespace {
constexpr std::uintptr_t get_button_rva=0x2C1DDE0;
[[maybe_unused]] constexpr std::uintptr_t bind_return_rva=0x151DDEB;
bool range(std::uintptr_t pointer, std::size_t size) {
    return size && pointer>=0x10000 && pointer<=0x7FFFFFFFFFFFULL-size+1;
}
bool read(std::uintptr_t pointer, void* destination, std::size_t size) {
    SIZE_T copied=0;
    return range(pointer,size) && ReadProcessMemory(GetCurrentProcess(),
        reinterpret_cast<void*>(pointer),destination,size,&copied) && copied==size;
}
template<std::size_t N> bool equal_at(std::uintptr_t pointer,
                                     const std::array<unsigned char,N>& expected) {
    std::array<unsigned char,N> current{};
    return read(pointer,current.data(),N) && current==expected;
}
class Code {
public:
    std::vector<unsigned char> data;
    std::vector<std::size_t> forward;
    void emit(std::initializer_list<unsigned char> bytes) { data.insert(data.end(),bytes); }
    void imm64(std::uint64_t value) {
        for (unsigned i=0;i<8;++i) data.push_back(static_cast<unsigned char>(value>>(i*8)));
    }
    void branch(unsigned char condition) {
        emit({0x0F,condition}); forward.push_back(data.size()); emit({0,0,0,0});
    }
    void resolve() {
        for (auto position:forward) {
            const auto displacement=static_cast<std::int32_t>(data.size()-position-4);
            std::memcpy(data.data()+position,&displacement,4);
        }
    }
};
}
std::vector<unsigned char> build_binding_filter(std::uintptr_t expected_return,
                                               std::uintptr_t original) {
    if (!range(expected_return,1) || !range(original,1))
        throw std::invalid_argument("Invalid binding filter address");
    Code c;
    c.emit({0x48,0xB8}); c.imm64(expected_return);
    c.emit({0x48,0x39,0x04,0x24}); c.branch(0x85);
    c.emit({0x48,0x85,0xFF}); c.branch(0x84);
    c.emit({0x8B,0x87,0x50,0xA0,0,0}); c.emit({0x83,0xF8,0x02}); c.branch(0x87);
    c.emit({0x44,0x8B,0x94,0x87,0x88,0xA0,0,0});
    c.emit({0x45,0x85,0xD2}); c.branch(0x88);
    c.emit({0xC1,0xE0,0x04}); c.emit({0x4C,0x8D,0x9C,0x07,0x58,0xA0,0,0});
    c.emit({0x41,0x83,0x3B,0}); c.branch(0x8C);
    c.emit({0x41,0x8B,0x43,0x04,0x85,0xC0}); c.branch(0x88);
    c.emit({0x41,0x3B,0x03}); c.branch(0x87);
    c.emit({0x41,0x39,0xC2}); c.branch(0x83);
    c.emit({0x4D,0x8B,0x5B,0x08}); c.emit({0x4D,0x85,0xDB}); c.branch(0x84);
    c.emit({0x4D,0x69,0xD2,0xE0,0,0,0}); c.emit({0x4D,0x01,0xD3}); c.branch(0x82);
    c.emit({0x41,0x83,0x7B,0x04,0}); c.branch(0x85);
    std::uint64_t first{},second{};
    std::memcpy(&first,menu_marker.data(),8); std::memcpy(&second,menu_marker.data()+8,8);
    c.emit({0x48,0xB8}); c.imm64(first);
    c.emit({0x49,0x39,0x83,0x88,0,0,0}); c.branch(0x85);
    c.emit({0x48,0xB8}); c.imm64(second);
    c.emit({0x49,0x39,0x83,0x90,0,0,0}); c.branch(0x85);
    c.emit({0x31,0xC0,0xC3}); c.resolve();
    c.emit({0x48,0xB8}); c.imm64(original); c.emit({0xFF,0xE0});
    return c.data;
}

bool BindingGuard::verify() const noexcept {
    if (!base_ || GetCurrentProcessId()!=pid_ ||
        reinterpret_cast<std::uintptr_t>(GetModuleHandleW(nullptr))!=base_) return false;
    MEMORY_BASIC_INFORMATION info{};
    if (VirtualQuery(reinterpret_cast<void*>(allocation_),&info,sizeof(info))!=sizeof(info) ||
        info.State!=MEM_COMMIT || info.Protect!=PAGE_EXECUTE_READ ||
        reinterpret_cast<std::uintptr_t>(info.AllocationBase)!=allocation_ ||
        reinterpret_cast<std::uintptr_t>(info.BaseAddress)>allocation_ ||
        allocation_+code_.size()>reinterpret_cast<std::uintptr_t>(info.BaseAddress)+info.RegionSize)
        return false;
    // Bounded stack buffer: generated code is under one page and never changes.
    std::array<unsigned char,4096> actual{};
    return !code_.empty() && code_.size()<=actual.size() &&
        read(allocation_,actual.data(),code_.size()) &&
        std::memcmp(actual.data(),code_.data(),code_.size())==0 &&
        equal_at(base_+get_button_rva,target_bytes_) &&
        equal_at(original_,original_bytes_) && equal_at(relay_,relay_bytes_);
}
bool BindingGuard::install(std::uintptr_t base,
                          const std::array<unsigned char,16>& file_prefix) noexcept {
    if (attempted_.exchange(true)) return false;
#ifdef CAS_MENU_FIXTURE
    (void)base; (void)file_prefix;
    return false; // Fixture hosts can never install any game hook.
#else
    try {
        if (reinterpret_cast<std::uintptr_t>(GetModuleHandleW(nullptr))!=base ||
            !range(base,get_button_rva+16) || !equal_at(base+get_button_rva,file_prefix)) return false;
        base_=base; pid_=GetCurrentProcessId();
        allocation_=reinterpret_cast<std::uintptr_t>(VirtualAlloc(nullptr,4096,
                                                     MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
        if (!allocation_) return false;
        auto* target=reinterpret_cast<void*>(base+get_button_rva);
        code_=build_binding_filter(base+bind_return_rva,base+get_button_rva);
        std::memcpy(reinterpret_cast<void*>(allocation_),code_.data(),code_.size());
        DWORD old=0;
        // MinHook requires an executable detour address even while disabled.
        if (!VirtualProtect(reinterpret_cast<void*>(allocation_),4096,PAGE_EXECUTE_READ,&old) ||
            !FlushInstructionCache(GetCurrentProcess(),reinterpret_cast<void*>(allocation_),code_.size())) return false;
        void* original=nullptr;
        // MinHook must already be initialized by the single runtime owner.
        if (MH_CreateHook(target,reinterpret_cast<void*>(allocation_),&original)!=MH_OK) return false;
        original_=reinterpret_cast<std::uintptr_t>(original);
        std::copy_n(file_prefix.begin(),5,original_bytes_.begin());
        const std::array<unsigned char,6> jump{0xFF,0x25,0,0,0,0};
        std::copy(jump.begin(),jump.end(),original_bytes_.begin()+5);
        auto destination=base+get_button_rva+5;
        std::memcpy(original_bytes_.data()+11,&destination,8);
        if (!equal_at(original_,original_bytes_)) return false;
        code_=build_binding_filter(base+bind_return_rva,original_);
        if (code_.empty() || code_.size()>4096) return false;
        if (!VirtualProtect(reinterpret_cast<void*>(allocation_),4096,PAGE_READWRITE,&old)) return false;
        std::memcpy(reinterpret_cast<void*>(allocation_),code_.data(),code_.size());
        if (!VirtualProtect(reinterpret_cast<void*>(allocation_),4096,PAGE_EXECUTE_READ,&old) ||
            !FlushInstructionCache(GetCurrentProcess(),reinterpret_cast<void*>(allocation_),code_.size()) ||
            !equal_at(base+get_button_rva,file_prefix)) return false;
        if (MH_EnableHook(target)!=MH_OK) return false;
        if (!read(base+get_button_rva,target_bytes_.data(),target_bytes_.size()) ||
            target_bytes_[0]!=0xE9 ||
            !std::equal(target_bytes_.begin()+5,target_bytes_.end(),file_prefix.begin()+5)) return false;
        std::int32_t relative{}; std::memcpy(&relative,target_bytes_.data()+1,4);
        relay_=base+get_button_rva+5+relative;
        std::copy(jump.begin(),jump.end(),relay_bytes_.begin());
        std::memcpy(relay_bytes_.data()+6,&allocation_,8);
        active_.store(verify());
        return active_.load();
    } catch (...) { active_.store(false); return false; }
#endif
}
bool BindingGuard::authorize(std::uintptr_t menu) noexcept {
    if (!active_.load() || !range(menu,0xA094)) return false;
    if (lock_.test_and_set()) { active_.store(false); return false; }
    const bool valid=active_.load() && verify();
    if (!valid) active_.store(false);
    lock_.clear();
    return valid && active_.load();
}
}
