#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <array>
#include <cstring>
#include <cstdio>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#include "cas/menu.hpp"

namespace {
using Item=std::array<unsigned char,224>;
struct Header { std::uint32_t capacity,count; Item* pointer; };
static_assert(sizeof(Header)==16);
void check(bool value,const char* message) { if (!value) throw std::runtime_error(message); }
struct Fixture {
    alignas(16) std::array<unsigned char,0xA200> menu{};
    std::array<std::vector<Item>,3> vectors;
    std::vector<std::vector<Item>> retired;
    std::uint64_t revision=10;
    unsigned changes=0,captures=0;
    int changed_role=-1;
    bool corrupt_constructor=false,change_during_constructor=false,queue_refuse=false;
    bool mutate_source_during_append=false;
    Item* source{};
    std::string stop_reason;
    cas::MenuAdapter adapter;
    Header& header(int d) { return *reinterpret_cast<Header*>(menu.data()+0xA058+d*16); }
    std::int32_t& selected(int d) { return *reinterpret_cast<std::int32_t*>(menu.data()+0xA088+d*4); }
    std::int32_t& depth() { return *reinterpret_cast<std::int32_t*>(menu.data()+0xA050); }
    Fixture();
    void build_begin() { adapter.beforeBuilder(menu.data(),this); }
    void build_end() { adapter.afterBuilder(menu.data(),this); }
    void confirmation(bool value) { adapter.beforeConfirmation(menu.data()); adapter.afterConfirmation(menu.data(),value); }
    void trigger(Item* object,bool result=false,bool as_menu=true) {
        adapter.beforeTrigger(menu.data(),object,as_menu);
        adapter.afterTrigger(menu.data(),object,as_menu,result);
    }
    void pet(int action=46);
    void prepare();
};
thread_local Fixture* current=nullptr;
void* construct(void* output,std::uint32_t icon,std::int32_t action,bool disabled,bool background) {
    check((reinterpret_cast<std::uintptr_t>(output)&15)==0,"constructor alignment");
    std::memset(output,0,224);
    auto* bytes=static_cast<unsigned char*>(output);
    std::memcpy(bytes,&icon,4); std::memcpy(bytes+4,&action,4);
    bytes[0x4C]=static_cast<unsigned char>(disabled); bytes[0x4D]=static_cast<unsigned char>(background);
    const std::int32_t invalid=-1;
    std::memcpy(bytes+0x84,&invalid,4); std::memcpy(bytes+0xD8,&invalid,4);
    if (current->corrupt_constructor) bytes[0xD8]=0;
    if (current->change_during_constructor) current->selected(0)=-1;
    return output;
}
void* append(void* header_pointer,void* incoming) {
    auto* h=static_cast<Header*>(header_pointer);
    int depth=-1;
    for (int i=0;i<3;++i) if (&current->header(i)==h) depth=i;
    check(depth>=0,"append header");
    Item copy{}; std::memcpy(copy.data(),incoming,224);
    // Deliberately move storage after every append. No stale pre-growth item
    // address may be dereferenced by the adapter's append read-back path.
    std::vector<Item> next;
    const auto capacity=h->count+1>16?h->count+1:16;
    next.reserve(capacity);
    for (unsigned i=0;i<h->count;++i) next.push_back(h->pointer[i]);
    next.push_back(copy);
    current->retired.push_back(std::move(current->vectors[depth]));
    current->vectors[depth]=std::move(next);
    h->capacity=capacity; ++h->count; h->pointer=current->vectors[depth].data();
    if (current->mutate_source_during_append && current->source) (*current->source)[0x30]^=1;
    return h->pointer+h->count-1;
}
void select(void* depth_pointer,std::int32_t depth,std::int32_t selected) {
    check(depth_pointer==current->menu.data()+0xA050 && depth==2,"selection ABI");
    current->selected(depth)=selected;
}
bool caption(void*,int role,char* output) {
    const auto text=role==-1?std::string("Companion Auto Summon"):
        std::string("Setting ")+std::to_string(role)+": ON";
    std::memcpy(output,text.c_str(),text.size()+1); return true;
}
bool capture(void* context,int role,std::uint64_t* revision) {
    auto& fixture=*static_cast<Fixture*>(context);
    check(role>=0 && role<7,"capture role");
    ++fixture.captures; *revision=fixture.revision; return true;
}
bool change(void* context,int role,std::uint64_t revision) {
    auto& fixture=*static_cast<Fixture*>(context);
    if (fixture.queue_refuse || fixture.revision!=revision) return false;
    fixture.changed_role=role; ++fixture.changes; ++fixture.revision; return true;
}
void log(void* context,const char* reason) { static_cast<Fixture*>(context)->stop_reason=reason; }
Fixture::Fixture() {
    current=this; depth()=1; selected(0)=0; selected(1)=0; selected(2)=0;
    for (unsigned i=0;i<3;++i) {
        vectors[i].reserve(16); header(static_cast<int>(i))={16,0,vectors[i].data()};
    }
    Item root{}; std::int32_t action=45; std::memcpy(root.data()+4,&action,4);
    append(&header(0),root.data());
    std::uint32_t icon=42; std::memcpy(menu.data()+0xA104,&icon,4);
    check(adapter.initializeFixture(construct,append,select,{this,caption,capture,change,log}),"fixture initialize");
}
void Fixture::pet(int action) {
    alignas(16) Item incoming{}; std::memcpy(incoming.data()+4,&action,4); source=&incoming;
    adapter.beforeAppend(&header(1),incoming.data()); append(&header(1),incoming.data()); source=nullptr;
}
void Fixture::prepare() {
    build_begin(); pet(); build_end(); check(!adapter.stopped(),stop_reason.c_str());
}
std::vector<std::string> passed;
template<class F> void scenario(const char* name,F body) { body(); passed.emplace_back(name); }
}
int main(int argc,char** argv) {
    try {
        if (argc==2 && std::strcmp(argv[1],"--filter")==0) {
            for (const auto byte:cas::build_binding_filter(0x100151DDEBULL,0x10002C1DDE0ULL)) std::printf("%02x",byte);
            std::puts(""); return 0;
        }
        scenario("parent_before_first_pet_and_seven_children",[]{
            Fixture f; f.prepare();
            check(f.header(1).count==2 && f.header(2).count==7,"menu sizes");
            check(f.header(1).pointer[0][4]==0 && f.header(1).pointer[1][4]==46,"parent before pet");
            for (int i=0;i<7;++i) {
                std::int32_t role{}; std::memcpy(&role,f.header(2).pointer[i].data()+0x84,4);
                check(role==i,"seven roles");
                for (unsigned j=0x98;j<0xD8;++j) check(f.header(2).pointer[i][j]==0,"no inline label");
            }
        });
        scenario("no_pet_fallback_parent",[]{Fixture f; f.build_begin(); f.build_end();
            check(!f.adapter.stopped() && f.header(1).count==1 && f.header(2).count==7,"empty roster parent");});
        scenario("large_native_roster_keeps_settings_discoverable",[]{Fixture f;
            auto& rows=f.vectors[1]; rows.reserve(64);
            for (int i=0;i<28;++i) { Item native{}; const std::int32_t action=10+(i%30);
                std::memcpy(native.data()+4,&action,4); rows.push_back(native); }
            f.header(1)={64,static_cast<std::uint32_t>(rows.size()),rows.data()};
            f.build_begin(); f.build_end();
            check(!f.adapter.stopped() && f.header(1).count==29,"settings parent appended beside large native roster");
            for (int i=0;i<28;++i) check(f.header(1).pointer[i][4]==10+(i%30),"native roster row preserved");
            check(std::memcmp(f.header(1).pointer[28].data()+0x88,"CAS_MENU_V1",11)==0,"settings parent remains identifiable");
            f.selected(1)=28; f.build_begin(); f.build_end();
            check(!f.adapter.stopped() && f.header(2).count==7,"settings page opens after native roster rows");
        });
        scenario("repeated_builder_no_duplicates",[]{Fixture f; f.prepare(); f.build_begin(); f.pet(47); f.build_end();
            check(!f.adapter.stopped() && f.header(1).count==3 && f.header(2).count==7,"repeat build");});
        scenario("native_none_opens_settings_and_preserves_caption",[]{Fixture f; f.prepare();
            std::array<char,128> text{}; f.adapter.afterLabel(f.menu.data(),text.data());
            check(std::string(text.data())=="Companion Auto Summon","parent caption");
            f.trigger(f.header(1).pointer); check(!f.adapter.stopped() && f.depth()==2 && f.selected(2)==0,"open settings");
            f.adapter.afterLabel(f.menu.data(),text.data()); check(std::string(text.data())=="Setting 0: ON","child caption");});
        scenario("fresh_confirmation_seven_preferences",[]{Fixture f; f.prepare(); f.trigger(f.header(1).pointer);
            for (int role=0;role<7;++role) { f.selected(2)=role; f.confirmation(false); f.confirmation(true);
                f.trigger(f.header(2).pointer+role); check(f.changed_role==role,"changed correct role"); }
            check(!f.adapter.stopped() && f.changes==7,"all setting changes");});
        scenario("first_held_and_replayed_confirmation_refused",[]{Fixture f; f.prepare(); f.trigger(f.header(1).pointer);
            f.confirmation(true); f.trigger(f.header(2).pointer); check(f.changes==0,"initial held press");
            f.confirmation(false); f.confirmation(true); f.trigger(f.header(2).pointer);
            f.confirmation(true); f.trigger(f.header(2).pointer); f.trigger(f.header(2).pointer);
            check(!f.adapter.stopped() && f.changes==1,"held/replayed press");});
        scenario("copied_action_never_changes_preference",[]{Fixture f; f.prepare(); f.trigger(f.header(1).pointer);
            f.confirmation(false); f.confirmation(true); Item copy=f.header(2).pointer[0]; f.trigger(&copy);
            check(!f.adapter.stopped() && f.changes==0,"copied action");});
        scenario("intervening_callback_consumes_intent",[]{Fixture f; f.prepare(); f.trigger(f.header(1).pointer);
            f.confirmation(false); f.confirmation(true); std::array<char,128> text{};
            f.adapter.afterLabel(f.menu.data(),text.data()); f.trigger(f.header(2).pointer);
            check(!f.adapter.stopped() && f.changes==0,"stale confirmation");});
        scenario("stale_preference_revision_refused",[]{Fixture f; f.prepare(); f.trigger(f.header(1).pointer);
            f.confirmation(false); f.confirmation(true); ++f.revision; f.trigger(f.header(2).pointer);
            check(!f.adapter.stopped() && f.changes==0,"preference revision");});
        scenario("native_nonempty_child_page_preserved",[]{Fixture f; Item native{}; native[4]=22;
            append(&f.header(2),native.data()); f.build_begin(); f.pet(); f.build_end();
            check(f.adapter.stopped() && f.header(2).count==1 && f.header(2).pointer[0][4]==22,"foreign child page");});
        scenario("missed_pet_append_stops_without_wrong_order",[]{Fixture f; Item native{}; native[4]=46;
            append(&f.header(1),native.data()); f.build_begin(); f.build_end();
            check(f.adapter.stopped() && f.header(1).count==1,"missed insertion");});
        scenario("overlapping_incoming_rejected",[]{Fixture f; Item native{}; native[4]=46;
            append(&f.header(2),native.data()); f.selected(1)=-1; f.build_begin();
            f.adapter.beforeAppend(&f.header(1),f.header(2).pointer);
            check(f.adapter.stopped() && f.header(1).count==0,"overlapping source");});
        scenario("constructor_contract_failure_stops",[]{Fixture f; f.corrupt_constructor=true;
            f.build_begin(); f.build_end(); check(f.adapter.stopped() && f.header(1).count==0,"constructor contract");});
        scenario("constructor_revalidation_detects_context_change",[]{Fixture f; f.change_during_constructor=true;
            f.build_begin(); f.build_end(); check(f.adapter.stopped() && f.header(1).count==0,"constructor drift");});
        scenario("changed_incoming_after_native_append_stops",[]{Fixture f; f.mutate_source_during_append=true;
            f.build_begin(); f.pet(); check(f.adapter.stopped(),"incoming mutation");});
        scenario("replacement_thread_callback_is_skipped_until_safe_rebind",[]{Fixture f; f.prepare();
            std::thread other([&]{current=&f; std::array<char,128> text{};
                f.adapter.afterLabel(f.menu.data(),text.data());
                if (f.adapter.stopped() || f.stop_reason!="menu_unexpected_thread_skipped") return;
                f.build_begin(); f.build_end(); current=nullptr;}); other.join();
            check(!f.adapter.stopped() && f.stop_reason=="menu_quiescent_thread_rebound","safe recovery after thread change");});
        scenario("quiescent_builder_thread_handoff_is_recovered",[]{Fixture f; f.prepare();
            std::thread other([&]{current=&f; f.build_begin(); f.build_end(); current=nullptr;}); other.join();
            check(!f.adapter.stopped() && f.stop_reason=="menu_quiescent_thread_rebound","quiescent handoff");});
        scenario("thread_handoff_during_builder_remains_blocked",[]{Fixture f; f.prepare(); f.build_begin();
            std::thread other([&]{current=&f; f.adapter.afterBuilder(f.menu.data(),&f); current=nullptr;}); other.join();
            check(f.adapter.stopped() && f.stop_reason=="menu_unexpected_thread","in-flight handoff guard");});
        scenario("nested_builder_fails_closed",[]{Fixture f; f.build_begin(); f.build_begin();
            check(f.adapter.stopped(),"nested builder");});
        scenario("unexpected_native_true_result_fails_closed",[]{Fixture f; f.prepare(); f.trigger(f.header(1).pointer,true);
            check(f.adapter.stopped() && f.depth()==1,"native true result");});
        scenario("pending_selection_fails_closed",[]{Fixture f; f.prepare(); f.menu[0xA16C]=1;
            f.trigger(f.header(1).pointer); check(f.adapter.stopped() && f.depth()==1,"pending selection");});
        scenario("outside_companion_context_untouched",[]{Fixture f; f.header(0).pointer[0][4]=22;
            f.build_begin(); f.pet(); f.build_end(); check(!f.adapter.stopped() && f.header(1).count==1 && !f.header(2).count,"foreign context");});
        scenario("corrupt_vector_bounds_stops",[]{Fixture f; f.header(1).capacity=257;
            f.build_begin(); f.build_end(); check(f.adapter.stopped(),"vector bounds");});
        scenario("fixture_cannot_install_binding_guard",[]{cas::BindingGuard guard;
            check(!guard.install(reinterpret_cast<std::uintptr_t>(GetModuleHandleW(nullptr)),{}) && !guard.active(),"guard fixture disabled");});
        std::printf("{\"scenarios_passed\":%zu,\"game_started_or_attached\":false,\"scenario_names\":[",passed.size());
        for (unsigned i=0;i<passed.size();++i) std::printf("%s\"%s\"",i?",":"",passed[i].c_str());
        std::puts("]}"); return 0;
    } catch (const std::exception& error) { std::fprintf(stderr,"FAIL: %s\n",error.what()); return 1; }
}
