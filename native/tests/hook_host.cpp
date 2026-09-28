// Standalone MinHook/Win64 ABI smoke host. Every hook target is an authored
// function in THIS executable. No game process, address, ABI override, save,
// loader, binding guard or production mod runtime is accessed or loaded.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>
#include <vector>
#include "MinHook.h"

namespace {
void require(bool value,const char* reason) { if (!value) throw std::runtime_error(reason); }
std::array<unsigned char,128> owned{};
void* first=owned.data()+16;
void* second=owned.data()+48;
void* third=owned.data()+80;
void* fourth=owned.data()+96;
DWORD owner_thread{};
unsigned native_calls{},detour_calls{},mod_calls{};
bool active=false;
std::vector<std::string> trace;
void native(const char* name) {
    require(GetCurrentThreadId()==owner_thread,"native thread differs");
    ++native_calls; trace.emplace_back(name);
}
void mod(const char* name) {
    require(GetCurrentThreadId()==owner_thread,"detour thread differs");
    ++mod_calls; trace.emplace_back(name);
}
using Update=void(*)(void*,float);
using Queue=void(*)(void*,int);
using Eject=void(*)(void*,void*,bool,bool);
using One=void(*)(void*);
using Two=void(*)(void*,void*);
using Trigger=bool(*)(void*,void*,bool);
using Load=bool(*)(void*,void*,void*,bool,bool,std::uint32_t);
using Confirm=bool(*)(void*);
using Append=void*(*)(void*,void*);
using Notice=void(*)(void*,void*,float,void*,std::uint32_t,void*,bool,float,bool,bool,bool);

Update original_update{};
Queue original_queue{};
Eject original_eject{};
One original_one{};
Two original_builder{};
Trigger original_trigger{};
Load original_load{};
Confirm original_confirm{};
Append original_append{};
Notice original_notice{};

__declspec(noinline) void nativeUpdate(void* pointer,float delta) {
    require(pointer==first && delta==0.125f,"update arguments"); native("update");
}
__declspec(noinline) void nativeQueue(void* pointer,int slot) {
    require(pointer==first && slot==-19,"queue arguments"); native("queue");
}
__declspec(noinline) void nativeEject(void* ship,void* player,bool animate,bool force) {
    require(ship==second && player==first && animate && !force,"eject arguments"); native("eject");
}
__declspec(noinline) void nativeOne(void* pointer) {
    require(pointer==third,"one arguments"); native("one");
}
__declspec(noinline) void* nativeAppend(void* header,void* item) {
    require(header==second && item==third,"append arguments"); native("append"); return fourth;
}
Append volatile call_append=nativeAppend;
__declspec(noinline) void nativeBuilder(void* menu,void* render) {
    require(menu==first && render==second,"builder arguments"); native("builder_begin");
    require(call_append(second,third)==fourth,"nested append return"); native("builder_end");
}
Queue volatile call_queue=nativeQueue;
__declspec(noinline) bool nativeTrigger(void* menu,void* action,bool called) {
    require(menu==first && action==second,"trigger arguments"); native("trigger_begin");
    call_queue(first,-19); native("trigger_end"); return !called;
}
__declspec(noinline) bool nativeLoad(void* player,void* common,void* state,bool network,
                                   bool resetting,std::uint32_t extra) {
    require(player==first && common==second && state==third && network && !resetting &&
        extra==0xA17C920Fu,"six-argument load forwarding"); native("load"); return true;
}
__declspec(noinline) bool nativeConfirm(void* menu) {
    require(menu==first,"confirmation arguments"); native("confirm"); return false;
}
__declspec(noinline) void nativeNotice(void* notifications,void* message,float duration,
                                     void* colour,std::uint32_t audio,void* icon,bool seventh,
                                     float extra,bool ninth,bool tenth,bool eleventh) {
    require(notifications==first && message==second && duration==5.5f && colour==third &&
        audio==0x85ED7BC1u && icon==fourth && seventh && extra==-0.25f && !ninth && tenth && !eleventh,
        "mixed float/register/stack notification forwarding"); native("notice");
}

void updateHook(void* pointer,float delta) {
    ++detour_calls; const bool started=active;
    original_update(pointer,delta); if (started && active) mod("update_after");
}
void queueHook(void* pointer,int slot) {
    ++detour_calls; const bool started=active;
    original_queue(pointer,slot); if (started && active) mod("queue_after");
}
void ejectHook(void* ship,void* player,bool animate,bool force) {
    ++detour_calls; const bool started=active;
    original_eject(ship,player,animate,force); if (started && active) mod("eject_after");
}
void oneHook(void* pointer) { ++detour_calls; if (active) mod("one_before"); original_one(pointer); }
void builderHook(void* menu,void* render) {
    ++detour_calls; const bool started=active;
    if (started) mod("builder_before"); original_builder(menu,render);
    if (started && active) mod("builder_after");
}
bool triggerHook(void* menu,void* action,bool called) {
    ++detour_calls; const bool started=active;
    if (started) { mod("runtime_action_before"); mod("menu_action_before"); }
    const bool result=original_trigger(menu,action,called);
    if (started && active) { mod("menu_action_after"); mod("runtime_action_after"); }
    return result;
}
bool loadHook(void* player,void* common,void* state,bool network,bool resetting,std::uint32_t extra) {
    ++detour_calls; const bool started=active;
    if (started) mod("load_before"); const bool result=original_load(player,common,state,network,resetting,extra);
    if (started && active) mod("load_after"); return result;
}
bool confirmHook(void* menu) {
    ++detour_calls; const bool started=active;
    if (started) mod("confirm_before"); const bool result=original_confirm(menu);
    if (started && active) mod("confirm_after"); return result;
}
void* appendHook(void* header,void* incoming) {
    ++detour_calls; if (active) mod("append_before"); return original_append(header,incoming);
}
void noticeHook(void* notifications,void* message,float duration,void* colour,std::uint32_t audio,
                void* icon,bool seventh,float extra,bool ninth,bool tenth,bool eleventh) {
    ++detour_calls; const bool started=active;
    original_notice(notifications,message,duration,colour,audio,icon,seventh,extra,ninth,tenth,eleventh);
    if (started && active) mod("notice_after");
}

Update volatile call_update=nativeUpdate;
Eject volatile call_eject=nativeEject;
One volatile call_one=nativeOne;
Two volatile call_builder=nativeBuilder;
Trigger volatile call_trigger=nativeTrigger;
Load volatile call_load=nativeLoad;
Confirm volatile call_confirm=nativeConfirm;
Notice volatile call_notice=nativeNotice;
struct Hook { void* target; void* detour; void** original; std::array<unsigned char,16> prefix{}; };
template<class F> void* address(F function) { return reinterpret_cast<void*>(function); }

void allCalls() {
    call_update(first,0.125f); call_queue(first,-19); call_eject(second,first,true,false);
    call_one(third); call_builder(first,second);
    require(!call_trigger(first,second,true),"trigger false result");
    require(call_trigger(first,second,false),"trigger true result");
    require(call_load(first,second,third,true,false,0xA17C920Fu),"load bool result");
    require(!call_confirm(first),"confirm false result");
    require(call_append(second,third)==fourth,"append pointer result");
    call_notice(first,second,5.5f,third,0x85ED7BC1u,fourth,true,-0.25f,false,true,false);
}
void reset() { native_calls=detour_calls=mod_calls=0; trace.clear(); }
}

int main() {
    try {
        owner_thread=GetCurrentThreadId();
        std::array<Hook,10> hooks{{
            {address(nativeUpdate),address(updateHook),reinterpret_cast<void**>(&original_update)},
            {address(nativeQueue),address(queueHook),reinterpret_cast<void**>(&original_queue)},
            {address(nativeEject),address(ejectHook),reinterpret_cast<void**>(&original_eject)},
            {address(nativeOne),address(oneHook),reinterpret_cast<void**>(&original_one)},
            {address(nativeBuilder),address(builderHook),reinterpret_cast<void**>(&original_builder)},
            {address(nativeTrigger),address(triggerHook),reinterpret_cast<void**>(&original_trigger)},
            {address(nativeLoad),address(loadHook),reinterpret_cast<void**>(&original_load)},
            {address(nativeConfirm),address(confirmHook),reinterpret_cast<void**>(&original_confirm)},
            {address(nativeAppend),address(appendHook),reinterpret_cast<void**>(&original_append)},
            {address(nativeNotice),address(noticeHook),reinterpret_cast<void**>(&original_notice)}}};
        // Establish the baseline without initializing any hook library.
        allCalls(); const auto baseline=native_calls;
        require(baseline==17 && detour_calls==0 && mod_calls==0,"plain native baseline");
        require(MH_Initialize()==MH_OK,"MinHook initialize");
        for (auto& hook:hooks) {
            std::memcpy(hook.prefix.data(),hook.target,hook.prefix.size());
            require(MH_CreateHook(hook.target,hook.detour,hook.original)==MH_OK,"create authored hook");
        }
        reset(); allCalls(); require(native_calls==baseline && !detour_calls,"created hooks remain disabled");
        for (auto& hook:hooks) require(MH_QueueEnableHook(hook.target)==MH_OK,"queue enable");
        reset(); allCalls(); require(native_calls==baseline && !detour_calls,"queued hooks remain disabled until apply");
        require(MH_ApplyQueued()==MH_OK,"batch enable");
        reset(); allCalls();
        require(native_calls==baseline && detour_calls==14 && mod_calls==0,"activation gate preserves native originals");
        active=true; reset(); allCalls();
        require(native_calls==baseline && detour_calls==14 && mod_calls==23,"enabled callback count");
        trace.clear(); call_trigger(first,second,true);
        require(trace==std::vector<std::string>{"runtime_action_before","menu_action_before","trigger_begin",
            "queue","queue_after","trigger_end","menu_action_after","runtime_action_after"},"shared trigger and same-thread queue reentry order");
        trace.clear(); call_builder(first,second);
        require(trace==std::vector<std::string>{"builder_before","builder_begin","append_before","append",
            "builder_end","builder_after"},"builder native append reentry order");
        // This fixture owns ALL its authored hooks; production retains its
        // game binding guard for process lifetime and has no such cleanup path.
        active=false;
        for (auto& hook:hooks) require(MH_QueueDisableHook(hook.target)==MH_OK,"queue disable");
        require(MH_ApplyQueued()==MH_OK,"batch disable");
        reset(); allCalls(); require(native_calls==baseline && !detour_calls && !mod_calls,"disabled hooks preserve originals");
        for (auto& hook:hooks) {
            require(std::memcmp(hook.prefix.data(),hook.target,hook.prefix.size())==0,"authored original bytes restored");
            require(MH_RemoveHook(hook.target)==MH_OK,"remove owned fixture hook");
        }
        require(MH_Uninitialize()==MH_OK,"fixture cleanup");
        std::puts("{\"authored_hook_targets\":10,\"native_calls_per_pass\":17,\"detours_per_enabled_pass\":14,\"checks_passed\":10,\"argument_and_result_forwarding\":true,\"mixed_float_stack_arguments\":true,\"shared_trigger_order\":true,\"same_thread_reentry\":true,\"activation_gate\":true,\"batch_enable_disable\":true,\"original_bytes_restored\":true,\"game_started_or_attached\":false,\"nms_abi_proven\":false}");
        return 0;
    } catch (const std::exception& error) {
        std::fprintf(stderr,"Owned ABI fixture failed: %s\n",error.what()); return 1;
    }
}
