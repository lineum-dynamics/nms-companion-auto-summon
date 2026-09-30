#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <algorithm>
#include <array>
#include <atomic>
#include <cstring>
#include <stdexcept>
#include <string>
#include "cas/menu.hpp"

namespace cas {
namespace {
constexpr std::size_t depth_offset=0xA050, vectors_offset=0xA058, selections_offset=0xA088;
constexpr std::size_t icon_offset=0xA104, pending_offset=0xA16C, item_size=224;
constexpr std::uintptr_t manager_rva=0x6E1BC10, retain_manager_rva=0x5910190;
constexpr unsigned max_items=256; // Inspection ceiling, never a gameplay limit.
bool range(std::uintptr_t pointer,std::size_t length) {
    return length && pointer>=0x10000 && pointer<=0x7FFFFFFFFFFFULL-length+1;
}
void require(bool valid,const char* reason) { if (!valid) throw std::runtime_error(reason); }
void copy(std::uintptr_t address,void* destination,std::size_t size) {
    SIZE_T copied=0;
    require(range(address,size) && ReadProcessMemory(GetCurrentProcess(),
        reinterpret_cast<void*>(address),destination,size,&copied) && copied==size,
        "menu_read_unavailable");
}
template<class T> T value(std::uintptr_t address) {
    T result{}; copy(address,&result,sizeof(result)); return result;
}
void write(std::uintptr_t address,const void* source,std::size_t size) {
    SIZE_T copied=0;
    require(range(address,size) && WriteProcessMemory(GetCurrentProcess(),
        reinterpret_cast<void*>(address),source,size,&copied) && copied==size,
        "menu_write_unavailable");
}
using Item=std::array<unsigned char,item_size>;
Item item_copy(std::uintptr_t address) { Item data{}; copy(address,data.data(),data.size()); return data; }
std::int32_t action(std::uintptr_t pointer) {
    require(range(pointer,item_size),"native_item_range");
    const auto result=value<std::int32_t>(pointer+4);
    require(result>=0 && result<=66,"unexpected_native_action"); return result;
}
bool marker(std::uintptr_t pointer) {
    return value<std::array<unsigned char,16>>(pointer+0x88)==menu_marker;
}
struct Vector {
    std::uint32_t capacity{},count{};
    std::uintptr_t pointer{};
    std::int32_t selected{};
    bool operator==(const Vector& b) const {
        return capacity==b.capacity && count==b.count && pointer==b.pointer && selected==b.selected;
    }
};
Vector vector_at(std::uintptr_t menu,unsigned depth) {
    const auto header=value<std::array<unsigned char,16>>(menu+vectors_offset+depth*16);
    Vector result;
    std::memcpy(&result.capacity,header.data(),4); std::memcpy(&result.count,header.data()+4,4);
    std::memcpy(&result.pointer,header.data()+8,8);
    require(result.count<=result.capacity && result.capacity<=max_items,"menu_vector_bounds");
    if (result.capacity) require(range(result.pointer,result.capacity*item_size),"menu_vector_address");
    result.selected=value<std::int32_t>(menu+selections_offset+depth*4);
    return result;
}
struct Snapshot {
    bool context{};
    std::int32_t depth{},parent=-1;
    std::array<Vector,3> vectors{};
    std::uint32_t icon{};
    bool ready{};
    bool same_state(const Snapshot& b) const {
        if (context!=b.context || depth!=b.depth || parent!=b.parent || icon!=b.icon || ready!=b.ready)
            return false;
        for (unsigned i=0;i<3;++i)
            if (vectors[i].capacity!=b.vectors[i].capacity || vectors[i].count!=b.vectors[i].count ||
                vectors[i].selected!=b.vectors[i].selected) return false;
        return true;
    }
    bool operator==(const Snapshot& b) const { return same_state(b) && vectors==b.vectors; }
    bool selected_parent() const { return context && parent>=0 && vectors[1].selected==parent; }
    bool selected_child() const {
        return selected_parent() && depth==2 && ready && vectors[2].selected>=0 && vectors[2].selected<7;
    }
};
struct Resource {
    std::uintptr_t pointer{};
    std::string name;
    bool ready{};
    bool identity(const Resource& b) const { return pointer==b.pointer && name==b.name; }
    bool operator==(const Resource& b) const { return identity(b) && ready==b.ready; }
};
std::string resource_name(std::uintptr_t pointer) {
    std::string name;
    for (unsigned offset=0xC;offset<0x10C;offset+=16) {
        const auto part=value<std::array<char,16>>(pointer+offset);
        for (char byte:part) { if (!byte) return name; name+=byte; }
    }
    throw std::runtime_error("texture_name_unterminated");
}
void check_manager(std::uintptr_t base,std::uintptr_t expected) {
    require(range(expected,0x68) && value<std::uintptr_t>(base+manager_rva)==expected &&
        value<std::uintptr_t>(base+retain_manager_rva)==expected,"texture_manager_changed");
}
Resource resource(std::uintptr_t base,std::uintptr_t manager,std::uint32_t handle) {
    Resource result;
    if (!handle || handle>0x7FFFFFFF) return result;
    check_manager(base,manager);
    const auto count=value<std::uint32_t>(manager+0x5C);
    const auto table=value<std::uintptr_t>(manager+0x60);
    if (handle>count) return result;
    const auto entry=table+static_cast<std::uintptr_t>(handle-1)*8;
    require(range(table,static_cast<std::size_t>(handle)*8),"texture_table_bounds");
    const auto pointer=value<std::uintptr_t>(entry);
    if (!pointer) return result;
    require(range(pointer,0x268),"texture_resource_range");
    if (value<std::uint32_t>(pointer+8)!=7) return result;
    const auto name=resource_name(pointer);
    if (name.empty()) return result;
    const auto error=value<unsigned char>(pointer+0x13A), substitute=value<unsigned char>(pointer+0x13B);
    const auto image=value<std::uint32_t>(pointer+0x1E0);
    const auto texture=value<std::uintptr_t>(pointer+0x260);
    check_manager(base,manager);
    require(value<std::uint32_t>(manager+0x5C)==count && value<std::uintptr_t>(manager+0x60)==table &&
        value<std::uintptr_t>(entry)==pointer && value<std::uint32_t>(pointer+8)==7 &&
        resource_name(pointer)==name && value<unsigned char>(pointer+0x13A)==error &&
        value<unsigned char>(pointer+0x13B)==substitute && value<std::uint32_t>(pointer+0x1E0)==image &&
        value<std::uintptr_t>(pointer+0x260)==texture,"texture_resource_changed");
    return {pointer,name,!error && !substitute && (image || texture)};
}
struct alignas(16) TextureRecord {
    const char* path{}; std::uint64_t unknown{}; std::uint32_t handle{}; std::uint32_t reserved{};
};
static_assert(offsetof(TextureRecord,handle)==0x10);
constexpr std::array<const char*,8> texture_paths{
    "TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/SETTINGS.DDS",
    "TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/AUTOMATION.DDS",
    "TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/SELECTION.DDS",
    "TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/BIOME.DDS",
    "TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/PLANET.DDS",
    "TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/STATION.DDS",
    "TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/ANOMALY.DDS",
    "TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/ROTATE.DDS"};
}

struct MenuAdapter::Impl {
    enum class Phase { BuildBefore,Append,BuildAfter,Label,TriggerBefore,TriggerAfter,ConfirmBefore,ConfirmAfter };
    std::atomic<bool> stopped{false};
    std::atomic_flag lock=ATOMIC_FLAG_INIT,icon_lock=ATOMIC_FLAG_INIT;
    std::atomic<bool> notice{false};
    std::atomic<std::uintptr_t> building_menu{0};
    std::atomic<DWORD> building_thread{0};
    std::uintptr_t base{},render{},pending_menu{},pending_action{},confirmation_menu{},intent_menu{};
    DWORD thread{},pending_thread{},confirmation_thread{},intent_thread{};
    bool building{},pending{},pending_as_menu{},pending_has_token{},pending_child{},confirmation{};
    bool confirmation_ready{},intent{};
    std::uintptr_t released_menu{};
    Snapshot pending_state{},intent_state{};
    std::uint64_t pending_revision{},intent_revision{};
    BindingGuard* guard{};
    MenuCallbacks callbacks{};
    MenuAppend append{}; MenuConstruct construct{}; MenuSelect select{};
    bool fixture{};
    bool resources_attempted{},icons_disabled{};
    bool thread_rebound_notice{};
    bool thread_skip_notice{};
    std::uintptr_t manager{};
    std::array<TextureRecord,8> textures{};
    std::array<Resource,8> resources{};
    Resource paw{}; std::uint32_t paw_handle{};
    std::array<std::uint32_t,9> known_icons{};
    unsigned known_count{};

    void stop(const char* reason) noexcept {
        stopped.store(true);
        if (!notice.exchange(true) && callbacks.log) callbacks.log(callbacks.context,reason);
        // Do not clear mutable state from a contending thread. The atomic stop
        // rejects all later accesses; native binding filter stays installed.
    }
    bool enter(Phase phase) noexcept {
        if (stopped.load()) return false;
        if (lock.test_and_set()) { stop("menu_overlapping_callback"); return false; }
        const auto current=GetCurrentThreadId();
        if (stopped.load()) { lock.clear(); return false; }
        if (thread && thread!=current) {
            const bool quiescent_builder_handoff = phase==Phase::BuildBefore && !building &&
                !pending && !pending_has_token && !confirmation &&
                building_menu.load()==0 && building_thread.load()==0;
            if (!quiescent_builder_handoff) {
                const bool callback_in_flight = building || pending || pending_has_token || confirmation ||
                    building_menu.load()!=0 || building_thread.load()!=0;
                if (callback_in_flight) stop("menu_unexpected_thread");
                else {
                    // A one-off label/trigger callback on a replacement UI
                    // thread is not enough to disable the menu for the rest
                    // of the process. Drop transient click tokens and wait
                    // for a quiescent builder boundary before rebinding.
                    intent=false; confirmation_ready=false; released_menu=0;
                    if (!thread_skip_notice && callbacks.log) {
                        callbacks.log(callbacks.context,"menu_unexpected_thread_skipped");
                        thread_skip_notice=true;
                    }
                }
                lock.clear(); return false;
            }
            thread=current;
            intent=false; confirmation_ready=false; released_menu=0;
            if (!thread_rebound_notice && callbacks.log) {
                callbacks.log(callbacks.context,"menu_quiescent_thread_rebound");
                thread_rebound_notice=true;
            }
        }
        thread=current;
        if ((confirmation && phase!=Phase::ConfirmAfter) ||
            (building && phase!=Phase::Append && phase!=Phase::BuildAfter) ||
            (pending && (phase==Phase::TriggerBefore || (phase!=Phase::TriggerAfter && pending_has_token)))) {
            stop("menu_nested_callback"); lock.clear(); return false;
        }
        if (phase!=Phase::TriggerBefore) intent=false;
        return true;
    }
    void leave() { lock.clear(); }
    bool authorized(std::uintptr_t menu) {
        return !stopped.load() && thread==GetCurrentThreadId() &&
            (fixture || (guard && guard->authorize(menu))) && !stopped.load();
    }
    bool permitted(std::uint32_t icon,std::uint32_t native) const {
        return icon==native || std::find(known_icons.begin(),known_icons.begin()+known_count,icon)!=known_icons.begin()+known_count;
    }
    void candidate(std::uintptr_t pointer,int role,std::uint32_t icon) {
        const auto data=item_copy(pointer);
        std::int32_t stored_role{},binding{}; std::uint32_t stored_icon{};
        std::memcpy(&stored_role,data.data()+0x84,4); std::memcpy(&binding,data.data()+0xD8,4);
        std::memcpy(&stored_icon,data.data(),4);
        require(action(pointer)==0 && stored_role==role && binding==-1 && permitted(stored_icon,icon) &&
            std::equal(menu_marker.begin(),menu_marker.end(),data.begin()+0x88) &&
            data[0x4C]==0 && data[0x4D]==1 &&
            std::all_of(data.begin()+0x98,data.begin()+0xD8,[](unsigned char b){return b==0;}),
            "tagged_menu_role_changed");
    }
    Snapshot snapshot(std::uintptr_t menu,bool allow_partial=false) {
        require(range(menu,pending_offset+1),"menu_snapshot_range");
        Snapshot state;
        state.depth=value<std::int32_t>(menu+depth_offset);
        require(state.depth>=0 && state.depth<=2,"unexpected_menu_depth");
        if (!state.depth) return state;
        state.vectors[0]=vector_at(menu,0);
        const auto& root=state.vectors[0];
        if (root.selected<0 || static_cast<unsigned>(root.selected)>=root.count ||
            action(root.pointer+root.selected*item_size)!=45) return state;
        state.context=true;
        state.vectors[1]=vector_at(menu,1); state.vectors[2]=vector_at(menu,2);
        state.icon=value<std::uint32_t>(menu+icon_offset);
        const auto& companion=state.vectors[1];
        for (unsigned i=0;i<companion.count;++i) {
            const auto pointer=companion.pointer+i*item_size;
            if (marker(pointer)) {
                require(state.parent==-1,"duplicate_menu_parent");
                candidate(pointer,-1,state.icon); state.parent=static_cast<int>(i);
            }
        }
        const auto& children=state.vectors[2];
        if (state.selected_parent() && children.count) {
            require(children.count<=7 && (children.count==7 || allow_partial),"native_child_page_must_be_preserved");
            for (unsigned i=0;i<children.count;++i) candidate(children.pointer+i*item_size,static_cast<int>(i),state.icon);
            state.ready=children.count==7;
        }
        return state;
    }
    void same(std::uintptr_t menu,const Snapshot& expected,bool partial=false) {
        require(snapshot(menu,partial)==expected,"menu_context_changed");
    }
    void no_pets(const Snapshot& state) {
        require(state.parent<0,"menu_parent_already_present");
        for (unsigned i=0;i<state.vectors[1].count;++i) {
            const auto current=action(state.vectors[1].pointer+i*item_size);
            require(current!=46 && current!=47,"missed_first_pet_append");
        }
    }
    void independent(std::uintptr_t incoming,const Snapshot& state) {
        require(range(incoming,item_size),"incoming_item_range");
        for (const auto& vector:state.vectors) if (vector.capacity)
            require(!(incoming<vector.pointer+vector.capacity*item_size && vector.pointer<incoming+item_size),
                    "incoming_item_overlaps_vector");
    }
    std::uint32_t icon(int role) noexcept {
        if (role<-1 || role>6 || icon_lock.test_and_set()) return 0;
        std::uint32_t result=0;
        try {
            if (resources_attempted && !icons_disabled && manager) {
                check_manager(base,manager);
                const auto index=static_cast<unsigned>(role+1);
                for (unsigned choice=0;choice<2;++choice) {
                    const auto& identity=choice?paw:resources[index];
                    const auto handle=choice?paw_handle:textures[index].handle;
                    if (!identity.pointer) continue;
                    const auto current=resource(base,manager,handle);
                    if (!current.identity(identity)) { icons_disabled=true; break; }
                    if (current.ready) { check_manager(base,manager); result=handle; break; }
                }
            }
        } catch (...) { icons_disabled=true; }
        icon_lock.clear(); return result;
    }
    std::array<std::uint32_t,8> choices() {
        std::array<std::uint32_t,8> result{};
        for (int role=-1;role<7;++role) {
            const auto handle=icon(role);
            if (!handle) continue;
            if (std::find(known_icons.begin(),known_icons.begin()+known_count,handle)==known_icons.begin()+known_count) {
                if (known_count>=known_icons.size()) continue;
                known_icons[known_count++]=handle;
            }
            result[role+1]=handle;
        }
        return result;
    }
    Snapshot append_role(std::uintptr_t menu,const Snapshot& before,int role,
                         const std::array<std::uint32_t,8>& icons,
                         std::uintptr_t incoming=0,const Item* source=nullptr) {
        const unsigned depth=role==-1?1:2;
        if (role==-1) {
            require(before.parent<0 && before.vectors[1].count<max_items,"menu_parent_not_appendable");
            require(!(before.vectors[1].selected==static_cast<int>(before.vectors[1].count) &&
                before.vectors[2].count),"menu_parent_would_adopt_native_page");
            no_pets(before);
        } else require(before.selected_parent() && before.vectors[2].count<7 &&
            role==static_cast<int>(before.vectors[2].count),"menu_child_not_appendable");
        const auto chosen=icons[role+1]?icons[role+1]:before.icon;
        require(permitted(chosen,before.icon) && authorized(menu),"menu_append_unauthorized");
        same(menu,before,true);
        alignas(16) Item data{};
        require(construct(data.data(),chosen,0,false,true)==data.data(),"menu_constructor_return");
        std::uint32_t constructed_icon{},constructed_action{};
        std::int32_t constructed_slot{},constructed_binding{};
        std::memcpy(&constructed_icon,data.data(),4); std::memcpy(&constructed_action,data.data()+4,4);
        std::memcpy(&constructed_slot,data.data()+0x84,4); std::memcpy(&constructed_binding,data.data()+0xD8,4);
        require(constructed_icon==chosen && !constructed_action && data[0x4C]==0 && data[0x4D]==1 &&
            constructed_slot==-1 && constructed_binding==-1 &&
            std::all_of(data.begin()+0x88,data.begin()+0x98,[](unsigned char b){return b==0;}),
            "menu_constructor_contract");
        std::copy(menu_marker.begin(),menu_marker.end(),data.begin()+0x88);
        std::fill(data.begin()+0x98,data.begin()+0xD8,0); std::memcpy(data.data()+0x84,&role,4);
        same(menu,before,true);
        if (incoming && source) {
            independent(incoming,before); no_pets(before);
            require(item_copy(incoming)==*source,"incoming_item_changed"); same(menu,before,true);
        }
        require(authorized(menu),"menu_append_unauthorized");
        require(append(reinterpret_cast<void*>(menu+vectors_offset+depth*16),data.data())!=nullptr,
                "native_append_failed");
        const auto after=snapshot(menu,true);
        require(after.context && after.depth==before.depth && after.icon==before.icon &&
            after.vectors[0]==before.vectors[0] && after.vectors[1].selected==before.vectors[1].selected &&
            after.vectors[2].selected==before.vectors[2].selected,"append_context_changed");
        if (role==-1) require(after.vectors[1].count==before.vectors[1].count+1 &&
            after.parent==static_cast<int>(before.vectors[1].count) && after.vectors[2]==before.vectors[2],
            "parent_append_unverified");
        else require(after.vectors[1]==before.vectors[1] && after.vectors[2].count==before.vectors[2].count+1,
            "child_append_unverified");
        require(value<std::uint32_t>(after.vectors[depth].pointer+before.vectors[depth].count*item_size)==chosen,
                "append_icon_changed");
        if (incoming && source) require(item_copy(incoming)==*source,"incoming_item_changed_after_append");
        return after;
    }
};

bool MenuAdapter::initialize(std::uintptr_t base,BindingGuard* guard,
                             MenuAppend append_original,MenuCallbacks callbacks) noexcept {
    if (impl_ || !base || !guard || !guard->active() || !append_original ||
        !callbacks.caption || !callbacks.capture || !callbacks.change) return false;
    try {
        auto* state=new Impl;
        state->base=base; state->guard=guard; state->callbacks=callbacks; state->append=append_original;
        state->construct=reinterpret_cast<MenuConstruct>(base+0x143B720);
        state->select=reinterpret_cast<MenuSelect>(base+0x1518EF0);
        for (unsigned i=0;i<8;++i) state->textures[i].path=texture_paths[i];
        impl_=state; return true;
    } catch (...) { return false; }
}
#ifdef CAS_MENU_FIXTURE
bool MenuAdapter::initializeFixture(MenuConstruct construct,MenuAppend append,MenuSelect select,
                                    MenuCallbacks callbacks) noexcept {
    if (impl_ || !construct || !append || !select) return false;
    try {
        impl_=new Impl; impl_->fixture=true; impl_->construct=construct;
        impl_->append=append; impl_->select=select; impl_->callbacks=callbacks; return true;
    } catch (...) { return false; }
}
#endif
bool MenuAdapter::stopped() const noexcept { return !impl_ || impl_->stopped.load(); }
void MenuAdapter::beforeBuilder(void* menu_pointer,void* render_pointer) noexcept {
    auto* p=impl_; if (!p || !p->enter(Impl::Phase::BuildBefore)) return;
    try {
        const auto menu=reinterpret_cast<std::uintptr_t>(menu_pointer);
        const auto render=reinterpret_cast<std::uintptr_t>(render_pointer);
        require(range(menu,pending_offset+1) && range(render,1),"builder_pointer_range");
        p->render=render; p->building=true;
        p->building_thread.store(p->thread); p->building_menu.store(menu);
    } catch (const std::exception& e) { p->stop(e.what()); }
      catch (...) { p->stop("builder_before_failed"); }
    p->leave();
}
void MenuAdapter::beforeAppend(void* header_pointer,void* incoming_pointer) noexcept {
    auto* p=impl_; if (!p || p->stopped.load()) return;
    const auto menu=p->building_menu.load();
    const auto header=reinterpret_cast<std::uintptr_t>(header_pointer);
    if (!menu || header!=menu+vectors_offset+16) return;
    if (GetCurrentThreadId()!=p->building_thread.load()) { p->stop("append_unexpected_thread"); return; }
    if (!p->enter(Impl::Phase::Append)) return;
    try {
        require(p->building && p->building_menu.load()==menu,"builder_identity_changed");
        const auto incoming=reinterpret_cast<std::uintptr_t>(incoming_pointer);
        const auto native_action=action(incoming);
        if (native_action==46 || native_action==47) {
            const auto icons=p->choices();
            const auto state=p->snapshot(menu);
            if (state.context && state.parent<0) {
                p->independent(incoming,state); p->no_pets(state);
                const auto original=item_copy(incoming);
                std::int32_t copied_action{}; std::memcpy(&copied_action,original.data()+4,4);
                require(copied_action==native_action,"incoming_action_changed");
                p->same(menu,state);
                p->append_role(menu,state,-1,icons,incoming,&original);
            }
        }
    } catch (const std::exception& e) { p->stop(e.what()); }
      catch (...) { p->stop("ordered_append_failed"); }
    p->leave();
}
void MenuAdapter::afterBuilder(void* menu_pointer,void* render_pointer) noexcept {
    auto* p=impl_; if (!p || !p->enter(Impl::Phase::BuildAfter)) return;
    try {
        const auto menu=reinterpret_cast<std::uintptr_t>(menu_pointer);
        require(p->building && menu==p->building_menu.load() &&
            reinterpret_cast<std::uintptr_t>(render_pointer)==p->render &&
            p->thread==p->building_thread.load(),"builder_completion_unmatched");
        const auto icons=p->choices();
        auto state=p->snapshot(menu);
        if (state.context) {
            if (state.parent<0) state=p->append_role(menu,state,-1,icons);
            while (state.selected_parent() && !state.ready)
                state=p->append_role(menu,state,static_cast<int>(state.vectors[2].count),icons);
        }
    } catch (const std::exception& e) { p->stop(e.what()); }
      catch (...) { p->stop("builder_after_failed"); }
    p->building=false; p->building_menu.store(0); p->building_thread.store(0); p->leave();
}
void MenuAdapter::afterLabel(void* menu_pointer,void* output) noexcept {
    auto* p=impl_; if (!p || !p->enter(Impl::Phase::Label)) return;
    try {
        p->choices();
        const auto state=p->snapshot(reinterpret_cast<std::uintptr_t>(menu_pointer));
        if (state.selected_parent() && (state.depth==1 || state.selected_child())) {
            const int role=state.depth==1?-1:state.vectors[2].selected;
            std::array<char,128> caption{};
            require(p->callbacks.caption && p->callbacks.caption(p->callbacks.context,role,caption.data()),
                    "menu_caption_unavailable");
            const auto end=std::find(caption.begin(),caption.end(),'\0');
            require(end!=caption.begin() && end!=caption.end(),"menu_caption_bounds");
            // Same ASCII runtime boundary as the deployed adapter. Catalog
            // translations are retained, but native UTF-8 rendering is unproven.
            require(std::all_of(caption.begin(),end,[](unsigned char b){return b<128;}),
                    "menu_caption_encoding");
            if (!p->stopped.load()) write(reinterpret_cast<std::uintptr_t>(output),caption.data(),caption.size());
        }
    } catch (const std::exception& e) { p->stop(e.what()); }
      catch (...) { p->stop("label_failed"); }
    p->leave();
}
void MenuAdapter::beforeConfirmation(void* menu_pointer) noexcept {
    auto* p=impl_; if (!p || !p->enter(Impl::Phase::ConfirmBefore)) return;
    try {
        const auto menu=reinterpret_cast<std::uintptr_t>(menu_pointer);
        require(range(menu,pending_offset+1),"confirmation_pointer_range");
        p->confirmation=true; p->confirmation_menu=menu; p->confirmation_thread=p->thread;
    } catch (const std::exception& e) { p->stop(e.what()); }
      catch (...) { p->stop("confirmation_before_failed"); }
    p->leave();
}
void MenuAdapter::afterConfirmation(void* menu_pointer,bool result) noexcept {
    auto* p=impl_; if (!p || !p->enter(Impl::Phase::ConfirmAfter)) return;
    try {
        const auto menu=reinterpret_cast<std::uintptr_t>(menu_pointer);
        require(p->confirmation && p->confirmation_menu==menu && p->confirmation_thread==p->thread,
                "confirmation_completion_unmatched");
        p->confirmation=false;
        const bool fresh=result && p->confirmation_ready && p->released_menu==menu;
        p->confirmation_ready=!result; p->released_menu=menu;
        if (fresh) {
            p->choices();
            const auto state=p->snapshot(menu);
            std::uint64_t revision{};
            if (state.selected_child() && p->callbacks.capture &&
                p->callbacks.capture(p->callbacks.context,state.vectors[2].selected,&revision) && !p->stopped.load()) {
                p->intent=true; p->intent_menu=menu; p->intent_thread=p->thread;
                p->intent_state=state; p->intent_revision=revision;
            }
        }
    } catch (const std::exception& e) { p->stop(e.what()); }
      catch (...) { p->stop("confirmation_after_failed"); }
    p->confirmation=false; p->leave();
}
void MenuAdapter::beforeTrigger(void* menu_pointer,void* action_pointer,bool called_as_menu) noexcept {
    auto* p=impl_; if (!p || !p->enter(Impl::Phase::TriggerBefore)) return;
    try {
        const auto menu=reinterpret_cast<std::uintptr_t>(menu_pointer);
        const auto incoming=reinterpret_cast<std::uintptr_t>(action_pointer);
        const bool intent=p->intent; p->intent=false;
        p->pending_has_token=false; p->pending_child=false;
        if (called_as_menu && action(incoming)==0 && marker(incoming)) {
            p->choices();
            const auto state=p->snapshot(menu);
            const auto slot=value<std::int32_t>(incoming+0x84);
            require(slot>=-1 && slot<7,"unknown_marked_menu_role");
            if (slot==-1 && state.depth==1 && state.selected_parent() && state.ready &&
                incoming==state.vectors[1].pointer+state.parent*item_size) {
                p->pending_has_token=true; p->pending_state=state;
            } else if (slot>=0 && intent && p->intent_menu==menu && p->intent_thread==p->thread &&
                state.selected_child() && state.same_state(p->intent_state) && state.vectors[2].selected==slot &&
                incoming==state.vectors[2].pointer+slot*item_size) {
                p->same(menu,state);
                p->pending_has_token=true; p->pending_child=true; p->pending_state=state;
                p->pending_revision=p->intent_revision;
            }
        }
        p->pending=true; p->pending_menu=menu; p->pending_action=incoming;
        p->pending_as_menu=called_as_menu; p->pending_thread=p->thread;
    } catch (const std::exception& e) { p->stop(e.what()); }
      catch (...) { p->stop("trigger_before_failed"); }
    p->leave();
}
void MenuAdapter::afterTrigger(void* menu_pointer,void* action_pointer,bool called_as_menu,bool result) noexcept {
    auto* p=impl_; if (!p || !p->enter(Impl::Phase::TriggerAfter)) return;
    try {
        const auto menu=reinterpret_cast<std::uintptr_t>(menu_pointer);
        require(p->pending && p->pending_menu==menu &&
            p->pending_action==reinterpret_cast<std::uintptr_t>(action_pointer) &&
            p->pending_as_menu==called_as_menu && p->pending_thread==p->thread,"trigger_completion_unmatched");
        if (p->pending_has_token) {
            require(!result,"tagged_none_unexpected_result");
            p->choices();
            require(p->authorized(menu),"activation_unauthorized");
            const auto state=p->snapshot(menu);
            require(state.same_state(p->pending_state) && state.selected_parent() && state.ready &&
                (p->pending_child?state.selected_child():state.depth==1),"activation_context_changed");
            require(p->authorized(menu),"activation_unauthorized"); p->same(menu,state);
            require(value<unsigned char>(menu+pending_offset)==0,"native_selection_still_pending");
            require(p->authorized(menu),"activation_unauthorized");
            if (p->pending_child) {
                if (p->callbacks.change) p->callbacks.change(p->callbacks.context,state.vectors[2].selected,p->pending_revision);
            } else {
                const std::int32_t depth=2;
                write(menu+depth_offset,&depth,4);
                require(value<std::int32_t>(menu+depth_offset)==2,"depth_write_unverified");
                require(p->authorized(menu),"selection_unauthorized");
                p->select(reinterpret_cast<void*>(menu+depth_offset),2,0);
                require(value<std::int32_t>(menu+selections_offset+8)==0,"child_selection_unverified");
            }
        }
    } catch (const std::exception& e) { p->stop(e.what()); }
      catch (...) { p->stop("trigger_after_failed"); }
    p->pending=false; p->pending_has_token=false; p->leave();
}
void MenuAdapter::afterResources(void* menu_pointer) noexcept {
    auto* p=impl_; if (!p || p->fixture || p->icon_lock.test_and_set()) return;
    try {
        if (!p->resources_attempted) {
            p->resources_attempted=true;
            const auto menu=reinterpret_cast<std::uintptr_t>(menu_pointer);
            require(range(menu,icon_offset+4),"resource_menu_range");
            p->manager=value<std::uintptr_t>(p->base+manager_rva); check_manager(p->base,p->manager);
            // Impl and module are process-pinned before this natural resource
            // callback. There are no destructors/release/reload/late-load paths.
            const auto handle=value<std::uint32_t>(menu+icon_offset);
            const auto paw=resource(p->base,p->manager,handle);
            if (paw.pointer && paw.ready) {
                require(value<std::uint32_t>(menu+icon_offset)==handle,"paw_changed_before_retain");
                check_manager(p->base,p->manager); p->paw_handle=handle;
                reinterpret_cast<void(*)(void*)>(p->base+0x2D65980)(&p->paw_handle);
                require(resource(p->base,p->manager,handle)==paw,"paw_changed_during_retain"); p->paw=paw;
            }
            for (unsigned i=0;i<8;++i) {
                check_manager(p->base,p->manager);
                reinterpret_cast<void(*)(void*)>(p->base+0xEC6850)(&p->textures[i]);
                check_manager(p->base,p->manager);
                const auto loaded=resource(p->base,p->manager,p->textures[i].handle);
                if (loaded.pointer && loaded.name==texture_paths[i]) p->resources[i]=loaded;
            }
        }
    } catch (...) { p->icons_disabled=true; }
    p->icon_lock.clear();
}
std::uint32_t MenuAdapter::notificationIcon() noexcept { return impl_?impl_->icon(-1):0; }
}
