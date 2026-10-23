// Owned-memory checks for the production load-context predicate. No game access.
#include "cas/load_context.hpp"
#include <cstring>
#include <iostream>
#include <map>
#include <stdexcept>

namespace {
using Address=std::uintptr_t;
constexpr Address base=0x10000000, app=0x20000000;
struct Fixture {
    cas::mapping::Build build{};
    std::map<Address,Address> memory;
    unsigned app_reads{},state_reads{};
    bool change_app{},change_state{},read_called{};
    Fixture() {
        build.globals.application=0x1000;
        build.local_load={0x2000,0x3000,0x4000,0x80,0x6000};
        memory[base+0x1000]=app;
        memory[base+0x2000]=base+0x3000;
        memory[base+0x3000]=base+0x4000;
    }
    auto reader() {
        return [&](Address address,void* out,std::size_t size) {
            read_called=true;
            if (size!=sizeof(Address)) throw std::runtime_error("unexpected read width");
            auto value=memory.at(address);
            if (address==base+0x1000 && ++app_reads==2 && change_app) ++value;
            if (address==base+0x2000 && ++state_reads==2 && change_state) ++value;
            std::memcpy(out,&value,sizeof value);
        };
    }
    cas::LoadContextObservation observes(Address receiver=app+0x80,Address image=base,Address caller=0) {
        return cas::observe_local_load_context(image,build,receiver,reader(),caller);
    }
    bool accepts(Address receiver=app+0x80,Address image=base) {
        return cas::applied_local_load_context(image,build,receiver,reader());
    }
};
void require(bool value,const char* message) { if (!value) throw std::runtime_error(message); }
}
int main() {
    try {
        unsigned cases=0;
        { Fixture f; require(f.accepts(),"valid applied local state rejected"); ++cases; }
        { Fixture f; require(f.accepts(0),"state-only trial check rejected"); ++cases; }
        { Fixture f; f.build.local_load={0,0,0,0,0}; require(f.accepts(0,0) && !f.read_called,"legacy path changed"); ++cases; }
        { Fixture f; require(!f.accepts(app+0x80,0),"missing image accepted"); ++cases; }
        { Fixture f; f.memory[base+0x1000]=0; require(!f.accepts(),"missing application accepted"); ++cases; }
        { Fixture f; require(!f.accepts(app+0x90),"foreign receiver accepted"); ++cases; }
        { Fixture f; f.memory[base+0x2000]=base+0x5000; require(!f.accepts(),"other applied state accepted"); ++cases; }
        { Fixture f; f.memory[base+0x3000]=base+0x6000; require(!f.accepts(),"foreign vtable accepted"); ++cases; }
        { Fixture f; f.memory.erase(base+0x3000); require(!f.accepts(),"unreadable vtable accepted"); ++cases; }
        { Fixture f; f.change_app=true; require(!f.accepts(),"application replacement accepted"); ++cases; }
        { Fixture f; f.change_state=true; require(!f.accepts(),"applied state change accepted"); ++cases; }
        { Fixture f; f.memory[base+0x1000]=~Address{0}; require(!f.accepts(0),"noncanonical application accepted"); ++cases; }
        { Fixture f; f.build.local_load.vtable=0; require(!f.accepts(),"partial policy accepted"); ++cases; }
        { Fixture f; auto value=f.observes(); require(value.accepted && value.checks==0x7f,"success diagnostic differs"); ++cases; }
        { Fixture f; auto value=f.observes(app+0x90); require(!value.accepted && value.checks==0x07,"receiver diagnostic differs"); ++cases; }
        { Fixture f; f.memory[base+0x2000]=base+0x5000; auto value=f.observes(); require(!value.accepted && value.checks==0x0f,"state diagnostic differs"); ++cases; }
        { Fixture f; f.memory[base+0x2000]=base+0x5000; auto value=f.observes(app+0x80,base,base+0x6000); require(value.accepted && value.checks==0x16f,"verified callback before state activation rejected"); ++cases; }
        { Fixture f; require(!f.observes(app+0x80,base,base+0x7000).accepted,"foreign callback accepted in applied state"); ++cases; }
        { Fixture f; require(!f.observes(0,base,base+0x6000).accepted,"callback with no receiver accepted"); ++cases; }
        { Fixture f; f.memory[base+0x3000]=base+0x7000; require(!f.observes(app+0x80,base,base+0x6000).accepted,"callback with foreign vtable accepted"); ++cases; }
        { Fixture f; f.change_state=true; require(!f.observes(app+0x80,base,base+0x6000).accepted,"unstable callback state accepted"); ++cases; }
        std::cout << "{\"passed\":true,\"cases\":" << cases << ",\"game_access\":false}\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
