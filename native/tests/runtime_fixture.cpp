// Runs the real Runtime against caller-owned synthetic bytes and native-service
// doubles. Never dereferences a game address, locates saves, or loads a DLL.
#include "cas/runtime.hpp"
#include "json.hpp"

#include <algorithm>
#include <array>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {
using Json = nlohmann::json;
using cas::Address;
constexpr Address base = 0x10000000, app = 0x20000000, solar = 0x30000000;
constexpr Address common = 0x40000000, action = 0x50000000, menu = 0x60000000;
constexpr Address player = app + 0x71C690, owner = app + 0xE10D0;
constexpr Address active = app + 0x29A1C0, queued = player + 0x6010;
constexpr Address app_pointer = base + 0x6E7AAE8;

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

struct Fixture {
    std::filesystem::path directory;
    std::map<Address, unsigned char> memory;
    std::array<bool, 30> owns{}, eligible{};
    std::unique_ptr<cas::Runtime> runtime;
    std::vector<int> queues;
    std::vector<std::string> notices, logs;
    std::function<void()> on_owned, on_can, on_placement, on_queue, after_queue;
    std::function<void(Address)> after_read;
    double now = 10;
    double last_can_time = -1;
    unsigned can_calls_this_frame = 0;
    unsigned placements = 0, owned_calls = 0, can_calls = 0, random_calls = 0, notice_calls = 0;
    bool reject_queue = false, unexpected_queue = false, fail_notice = false;

    template<class T> void put(Address address, T value) {
        const auto* bytes = reinterpret_cast<const unsigned char*>(&value);
        for (std::size_t i = 0; i < sizeof value; ++i) memory[address + i] = bytes[i];
    }
    void read(Address address, void* output, std::size_t count) {
        auto* bytes = static_cast<unsigned char*>(output);
        for (std::size_t i = 0; i < count; ++i) {
            const auto found = memory.find(address + i);
            if (found == memory.end()) throw std::runtime_error("Read outside owned synthetic memory: " + std::to_string(address+i));
            bytes[i] = found->second;
        }
        if (after_read) after_read(address);
    }
    static void once(std::function<void()>& callback) {
        auto work = std::move(callback); callback = {}; if (work) work();
    }
    explicit Fixture(std::filesystem::path path, cas::Preferences prefs = {}) : directory(std::move(path)) {
        // This is a test-only caller-selected directory; production paths are
        // never discovered. Constructing the runtime itself performs no writes.
        cas::SettingsStore(directory / L"settings.json").save_preferences(prefs);
        put<Address>(app_pointer, app); put<float>(base+0x52381E0, 12.0f);
        put<Address>(app+0x71AF70, solar);
        put<int>(solar+0x2544, 1); put<int>(solar+0x5196D0, 0);
        put<std::uint32_t>(solar+0x6148, 0); put<std::uint32_t>(solar+0x614C, 0);
        put<int>(app+0x57A584, 3); put<int>(active, -1); put<int>(queued, -1);
        put<int>(owner+0x1B9300, -1); put<std::uint8_t>(owner+0x1B937D, 0);
        put<std::uint64_t>(player+0x2A8, 123); put<std::uint32_t>(app+0x30E7FC, 0);
        put<std::uint64_t>(common+0x8980, 0x42);
        put<std::uint32_t>(app+0x837B40+0x28C, 0); put<float>(app+0x4BF50C, -1);
        put<int>(action+4, 46); put<int>(action+0x84, 0);
        for (int slot = 0; slot < 30; ++slot) {
            put<std::uint32_t>(owner+slot*0x24A0+0x2370, 0);
            put<std::uint64_t>(owner+slot*0x24A0+0x2330, slot+1);
            put<std::uint64_t>(owner+slot*0x24A0+0x23C0, 100+slot);
            put<std::uint32_t>(owner+slot*0x24A0+0x2480, 0);
            eligible[slot] = true;
        }
        cas::RuntimeServices services;
        services.base = base;
        services.read = [this](auto address, auto* output, auto size) { read(address,output,size); };
        services.owned = [this](Address actual, int slot) {
            require(actual == owner, "Nonlocal ownership service called"); ++owned_calls;
            once(on_owned); return owns.at(slot);
        };
        services.can_summon = [this](Address actual, int slot) {
            require(actual == player, "Nonlocal eligibility service called"); ++can_calls;
            if (last_can_time != now) { last_can_time = now; can_calls_this_frame = 0; }
            ++can_calls_this_frame;
            once(on_can); return eligible.at(slot);
        };
        services.placement = [this](Address actual,float one,float two,std::uint32_t hand) {
            require(actual == owner+0x1B9140 && one == 12 && two == 12 && hand == 0, "Placement arguments changed");
            ++placements; once(on_placement);
        };
        services.use_hand = [] { return false; };
        services.queue = [this](Address actual,int slot) {
            require(actual == player, "Nonlocal summon service called"); queues.push_back(slot);
            once(on_queue);
            put<int>(queued, reject_queue ? -1 : unexpected_queue ? (slot+1)%30 : slot);
            runtime->afterQueue(actual,slot);
            once(after_queue);
        };
        services.notice = [this](Address actual,const std::string& notice) {
            require(actual == app, "Nonlocal notification service called"); ++notice_calls;
            if (fail_notice) throw std::runtime_error("Synthetic notification failure");
            notices.push_back(notice);
        };
        services.log = [this](const char* text) { logs.emplace_back(text); };
        services.clock = [this] { return now; };
        services.random = [this](std::size_t bound) { ++random_calls; require(bound > 0,"Empty random pool"); return std::size_t(0); };
        runtime = std::make_unique<cas::Runtime>(std::move(services),directory);
    }
    void pet(int slot, int habitat = 0, std::uint64_t identity = 0) {
        owns[slot] = true;
        put<std::uint32_t>(owner+slot*0x24A0+0x2370,1);
        put<std::uint32_t>(owner+slot*0x24A0+0x2480,habitat);
        if (identity) put<std::uint64_t>(owner+slot*0x24A0+0x2330,identity);
    }
    std::array<std::uint8_t,16> identity(int slot) {
        std::array<std::uint8_t,16> result;
        read(owner+slot*0x24A0+0x2330,result.data(),8);
        read(owner+slot*0x24A0+0x23C0,result.data()+8,8);
        return result;
    }
    void load(bool network=false, bool accepted=true) { runtime->beforeLoad(network); runtime->afterLoad(common,network,accepted); }
    void exit() { runtime->afterExit(player); }
    void clear_pet() { put<int>(active,-1); put<int>(queued,-1); }
    void step(float dt=.05f) { now += .05; runtime->afterOwner(owner,dt); runtime->afterPlayer(player,dt); }
    void run(unsigned frames=100,float dt=.05f) { for (unsigned i=0;i<frames;++i) step(dt); }
    void toggle(int role, bool apply=true) {
        std::uint64_t revision = 0;
        require(runtime->capture(role,&revision),"Settings action capture failed");
        require(runtime->change(role,revision),"Settings action rejected");
        if (apply) runtime->afterPlayer(player,.05f);
    }
    void manual(int slot, bool result=true, bool called=true) {
        put<int>(action+4,46); put<int>(action+0x84,slot);
        runtime->beforeAction(menu,action,called);
        put<int>(queued,slot); runtime->afterQueue(player,slot);
        runtime->afterAction(menu,action,called,result);
    }
    std::optional<cas::Favorite> favorite(const std::string& key="nms:0000000000000042") {
        return cas::SelectionStore(directory/L"state.json").load(key);
    }
};

using Test = std::function<void(const std::filesystem::path&)>;
std::vector<std::pair<std::string,Test>> cases() {
    std::vector<std::pair<std::string,Test>> tests;
    auto add = [&](const char* name, Test test) { tests.emplace_back(name,std::move(test)); };
    add("absence-is-not-an-opportunity",[](auto dir) { Fixture f(dir); f.pet(0); f.run(); require(f.queues.empty(),"Absence armed automation"); });
    for (const int location : {2,3,14}) tests.emplace_back("startup-location-"+std::to_string(location),[location](auto dir) {
        Fixture f(dir); f.pet(0); f.put<int>(app+0x57A584,location); f.load();
        require(f.placements==0 && f.queues.empty(),"Load callback performed native placement");
        f.run(); require(f.queues==std::vector<int>{0},"Local load failed to summon exactly once");
        f.clear_pet(); f.run(); require(f.queues.size()==1,"Dismissal created another startup opportunity");
    });
    add("ship-exit-one-request",[](auto dir) { Fixture f(dir); f.pet(1); f.exit(); f.run(); require(f.queues==std::vector<int>{1},"Exit request missing"); f.clear_pet(); f.run(); require(f.queues.size()==1,"Dismissal rearmed exit"); });
    add("failed-and-network-loads-do-not-arm",[](auto dir) { Fixture f(dir); f.pet(0); f.load(false,false); f.run(); f.load(true,true); f.run(); require(f.queues.empty(),"Unsuccessful or network load armed"); });
    add("network-load-preserves-local-opportunity",[](auto dir) { Fixture f(dir); f.pet(0); f.load(); f.load(true); f.run(); require(f.queues.size()==1,"Network deserialize erased local opportunity"); });
    add("local-player-only",[](auto dir) { Fixture f(dir); f.pet(0); f.runtime->afterExit(player+8); f.runtime->afterOwner(owner+8,.05f); f.run(); require(f.queues.empty(),"Remote player triggered summon"); });
    add("enter-ship-cancels",[](auto dir) { Fixture f(dir); f.pet(0); f.exit(); f.step(); f.runtime->beforeEnter(player); f.run(); require(f.queues.empty(),"Ship entry failed to cancel"); });
    add("unsupported-location-waits",[](auto dir) { Fixture f(dir); f.pet(0); f.put<int>(app+0x57A584,4); f.load(); f.run(); require(f.queues.empty() && f.placements==0,"Unsupported location attempted placement"); f.put<int>(app+0x57A584,3); f.run(); require(f.queues.size()==1,"Suitable location did not resume pending load"); });
    add("disabled-location-cancels",[](auto dir) { cas::Preferences p; p.locations={3}; Fixture f(dir,p); f.pet(0); f.put<int>(app+0x57A584,14); f.load(); f.run(); f.put<int>(app+0x57A584,3); f.run(); require(f.queues.empty(),"Explicitly disabled location retained startup opportunity"); });
    add("terrain-retry-does-not-expire",[](auto dir) { Fixture f(dir); f.pet(0); f.eligible[0]=false; f.exit(); f.run(450); require(f.queues.empty(),"Ineligible terrain summoned"); f.eligible[0]=true; f.run(); require(f.queues.size()==1,"Long terrain wait lost intent"); });
    add("physics-readiness-waits",[](auto dir) { Fixture f(dir); f.pet(0); f.put<std::uint64_t>(player+0x2A8,0); f.load(); f.run(); require(f.placements==0,"Missing physics attempted placement"); f.put<std::uint64_t>(player+0x2A8,123); f.run(); require(f.queues.size()==1,"Physics readiness did not resume"); });
    add("paused-frames-cannot-summon",[](auto dir) { Fixture f(dir); f.pet(0); f.exit(); f.run(100,0); require(f.queues.empty() && f.placements==0,"Paused update invoked native placement"); f.run(); require(f.queues.size()==1,"Unpause did not resume"); });
    add("reversed-clock-does-not-probe",[](auto dir) { Fixture f(dir); f.pet(0); f.exit(); f.step(); const auto placements=f.placements; const auto owned=f.owned_calls; f.now=-1; f.step(); require(f.placements==placements && f.owned_calls==owned && f.queues.empty(),"Reversed clock invoked native probe"); f.now=20; f.run(); require(f.queues.empty(),"Reversed clock retained stale opportunity"); });
    add("nonfinite-clock-does-not-probe",[](auto dir) { Fixture f(dir); f.pet(0); f.exit(); f.step(); const auto placements=f.placements; const auto owned=f.owned_calls; f.now=std::numeric_limits<double>::quiet_NaN(); f.step(); require(f.placements==placements && f.owned_calls==owned && f.queues.empty(),"Nonfinite clock invoked native probe"); require(!f.runtime->enabled(),"Nonfinite clock failed open"); });
    add("empty-roster-waits-for-ownership",[](auto dir) { Fixture f(dir); f.load(); f.run(); require(f.queues.empty(),"Missing companions manufactured pet"); f.pet(4); f.run(); require(f.queues==std::vector<int>{4},"Late ownership failed"); });
    add("active-pet-consumes-load-opportunity",[](auto dir) { Fixture f(dir); f.pet(0); f.put<int>(active,0); f.load(); f.step(); f.clear_pet(); f.run(); require(f.queues.empty(),"Existing active pet dismissal rearmed startup"); });
    add("native-preview-cancels",[](auto dir) { Fixture f(dir); f.pet(0); f.exit(); f.put<int>(owner+0x1B9300,0); f.step(); f.put<int>(owner+0x1B9300,-1); f.run(); require(f.queues.empty(),"Native preview did not cancel automatic intent"); });
    add("native-emote-cancels",[](auto dir) { Fixture f(dir); f.pet(0); f.exit(); f.put<std::uint8_t>(owner+0x1B937D,1); f.step(); f.put<std::uint8_t>(owner+0x1B937D,0); f.run(); require(f.queues.empty(),"Native emote did not cancel"); });
    for (const int invalid : {-2,30}) tests.emplace_back("invalid-index-"+std::to_string(invalid),[invalid](auto dir) { Fixture f(dir); f.pet(0); f.exit(); f.put<int>(queued,invalid); f.step(); f.clear_pet(); f.run(); require(f.queues.empty(),"Invalid native index did not cancel"); });
    add("pending-off-blocks-before-player-update",[](auto dir) { Fixture f(dir); f.pet(0); f.exit(); f.toggle(0,false); for (int i=0;i<100;++i) { f.now+=.05; f.runtime->afterOwner(owner,.05f); } require(f.queues.empty(),"Queued OFF allowed ownership callback summon"); f.runtime->afterPlayer(player,.05f); require(!cas::SettingsStore(dir/L"settings.json").load(),"OFF was not persisted"); f.exit(); f.run(); require(f.queues.empty(),"OFF allowed ship exit summon"); });
    add("control-revision-prevents-stale-replay",[](auto dir) { Fixture f(dir); std::uint64_t rev; require(f.runtime->capture(0,&rev),"Capture failed"); require(f.runtime->change(0,rev),"Initial change failed"); require(!f.runtime->change(0,rev),"Stale menu revision replayed"); f.runtime->afterPlayer(player,.05f); require(!cas::SettingsStore(dir/L"settings.json").load(),"Stale replay undid OFF"); });
    add("control-cycle-and-captions",[](auto dir) { Fixture f(dir); char caption[128]{}; for(int role=-1;role<=6;++role) require(f.runtime->caption(role,caption) && caption[0],"Missing menu caption"); f.toggle(1); require(cas::SettingsStore(dir/L"settings.json").load_preferences().selection_mode=="last_manual","Mode cycle from habitat"); f.toggle(1); require(cas::SettingsStore(dir/L"settings.json").load_preferences().selection_mode=="random","Mode cycle from last"); f.toggle(1); require(cas::SettingsStore(dir/L"settings.json").load_preferences().selection_mode=="by_habitat","Mode cycle from random"); require(!f.runtime->caption(7,caption),"Invalid role accepted"); });
    add("hud-delivery-failure-does-not-stop-automation",[](auto dir) { Fixture f(dir); f.pet(0); f.fail_notice=true; f.toggle(2); require(f.runtime->enabled() && f.notice_calls==1,"Cosmetic native error stopped runtime"); require(!cas::SettingsStore(dir/L"settings.json").load_preferences().prefer_same_biome,"Cosmetic failure lost persisted control"); f.fail_notice=false; f.toggle(6); f.exit(); f.run(); require(f.queues.size()==1 && f.runtime->enabled(),"Cosmetic failure blocked later automatic summon"); require(f.notice_calls==1 && f.notices.empty(),"Disabled HUD retried delivery"); });
    for (const auto offset: {Address(0x837B40+0x28C),Address(0x4BF50C)}) tests.emplace_back("hud-state-read-failure-"+std::to_string(offset),[offset](auto dir) { Fixture f(dir); f.pet(0); for(Address byte=app+offset;byte<app+offset+4;++byte)f.memory.erase(byte); f.toggle(2); require(f.runtime->enabled(),"Cosmetic readiness read error stopped runtime"); f.put<std::uint32_t>(app+0x837B40+0x28C,0);f.put<float>(app+0x4BF50C,-1);f.toggle(6);f.exit();f.run();require(f.queues.size()==1 && f.notice_calls==0,"Failed HUD readiness path was retried or blocked automation"); });
    add("queue-rejection-retains-identity",[](auto dir) { Fixture f(dir); f.pet(0); f.pet(1); f.reject_queue=true; f.exit(); f.run(160); require(f.queues.size()>2,"Queue rejection did not retry"); require(std::all_of(f.queues.begin(),f.queues.end(),[&](int s){return s==f.queues[0];}),"Rejection rerolled companion"); auto previous=f.queues.size(); f.reject_queue=false; f.run(); require(f.queues.size()==previous+1,"Accepted retry repeated"); f.clear_pet(); f.run(); require(f.queues.size()==previous+1,"Acceptance was not consumed"); });
    add("unexpected-queued-slot-stops-runtime",[](auto dir) { Fixture f(dir); f.pet(0); f.unexpected_queue=true; f.exit(); f.run(); require(!f.runtime->enabled(),"Unexpected game queue failed open"); });
    add("shuffle-advances-only-accepted",[](auto dir) { Fixture f(dir); f.pet(0); f.pet(1); for(int i=0;i<4;++i){f.clear_pet();f.exit();f.run();} require(f.queues.size()==4,"Four exits did not produce four requests"); for(std::size_t i=1;i<f.queues.size();++i) require(f.queues[i]!=f.queues[i-1],"Two-companion rotation repeated consecutively"); });
    add("habitat-prefers-compatible-owned-pool",[](auto dir) { Fixture f(dir); f.pet(0,1); f.pet(1,0); f.load(); f.run(); require(f.queues==std::vector<int>{1},"Exact habitat pool was not selected"); });
    add("lava-uses-scorched-related-companion",[](auto dir) { Fixture f(dir); f.put<std::uint32_t>(solar+0x6148,2); f.put<std::uint32_t>(solar+0x614C,26); f.pet(0,4); f.pet(1,2); f.load(); f.run(); require(f.queues==std::vector<int>{1},"Lava subtype did not select related scorched companion"); });
    add("no-suitable-habitat-does-not-fallback-to-opposite",[](auto dir) { Fixture f(dir); f.put<std::uint32_t>(solar+0x6148,2); f.put<std::uint32_t>(solar+0x614C,26); f.pet(0,4); f.load(); f.run(); require(f.queues.empty() && !f.notices.empty(),"Incompatible habitat used arbitrary fallback or omitted notice"); });
    add("station-is-neutral-habitat-context",[](auto dir) { Fixture f(dir); f.put<int>(app+0x57A584,2); f.pet(0,4); f.load(); f.run(); require(f.queues==std::vector<int>{0},"Station incorrectly applied nearby planet habitat"); });
    for (const bool rotate: {false,true}) tests.emplace_back("random-optional-habitat-read-fallback-"+std::to_string(rotate),[rotate](auto dir) { cas::Preferences p; p.selection_mode="random"; p.rotate_companions=rotate; Fixture f(dir,p); f.pet(0); for(Address byte=solar+0x2544;byte<solar+0x2544+4;++byte)f.memory.erase(byte); f.load(); f.run(); require(f.queues==std::vector<int>{0} && f.runtime->enabled(),"Optional random habitat fault stopped native-eligible summon"); });
    add("last-mode-never-invents-favorite",[](auto dir) { cas::Preferences p; p.selection_mode="last_manual"; Fixture f(dir,p); f.pet(0); f.load(); f.run(); f.exit(); f.run(); require(f.queues.empty(),"Last mode invented an initial favorite"); });
    add("manual-native-ui-persists-correct-save",[](auto dir) { Fixture f(dir); f.pet(2); f.load(); f.manual(2); auto favorite=f.favorite(); require(favorite && favorite->seed==f.identity(2) && favorite->slot==2,"Confirmed UI favorite was not persisted"); require(!f.favorite("nms:0000000000000043"),"Favorite leaked across saves"); });
    add("unattributed-queue-does-not-learn",[](auto dir) { Fixture f(dir); f.pet(0); f.load(); f.put<int>(queued,0); f.runtime->afterQueue(player,0); require(!f.favorite(),"Unattributed native queue learned favorite"); f.clear_pet(); f.run(); require(f.queues.empty(),"Unattributed accepted queue did not cancel startup"); });
    add("failed-manual-action-does-not-learn",[](auto dir) { Fixture f(dir); f.pet(0); f.load(); f.manual(0,false); require(!f.favorite(),"Failed native UI result learned favorite"); });
    add("nonpet-action-does-not-learn",[](auto dir) { Fixture f(dir); f.pet(0); f.load(); f.put<int>(action+4,1); f.runtime->beforeAction(menu,action,true); f.put<int>(queued,0); f.runtime->afterQueue(player,0); f.runtime->afterAction(menu,action,true,true); require(!f.favorite(),"Non-pet action learned favorite"); });
    add("nested-manual-action-disables-only-attribution",[](auto dir) { Fixture f(dir); f.pet(0); f.load(); f.runtime->beforeAction(menu,action,true); f.runtime->beforeAction(menu,action,true); f.put<int>(queued,0); f.runtime->afterQueue(player,0); f.runtime->afterAction(menu,action,true,true); require(!f.favorite(),"Nested manual dispatch learned favorite"); f.clear_pet(); f.exit(); f.run(); require(f.queues.size()==1 && f.runtime->enabled(),"Ambiguous manual dispatch disabled unrelated automation"); });
    add("invalid-manual-item-disables-only-attribution",[](auto dir) { Fixture f(dir); f.pet(0); f.load(); f.runtime->beforeAction(menu,action+0x10000,true); f.runtime->afterAction(menu,action+0x10000,true,true); f.exit(); f.run(); require(f.queues.size()==1 && f.runtime->enabled(),"Invalid manual item disabled unrelated automation"); require(!f.favorite(),"Invalid manual item learned favorite"); });
    add("manual-favorite-retained-when-auto-off",[](auto dir) { cas::Preferences p; p.enabled=false; Fixture f(dir,p); f.pet(0); f.load(); f.manual(0); require(f.favorite().has_value(),"Auto OFF incorrectly prevented manual favorite persistence"); });
    add("last-favorite-restored-after-slot-move",[](auto dir) { cas::Preferences p; p.selection_mode="last_manual"; Fixture f(dir,p); f.pet(2); f.load(); f.manual(2); auto id=f.identity(2); f.owns[2]=false; f.put<std::uint32_t>(owner+2*0x24A0+0x2370,0); f.pet(7); for(std::size_t i=0;i<8;++i){f.memory[owner+7*0x24A0+0x2330+i]=id[i];f.memory[owner+7*0x24A0+0x23C0+i]=id[i+8];} f.clear_pet(); f.load(); f.run(); require(f.queues==std::vector<int>{7},"Moved favorite was guessed by former slot"); });
    add("local-save-switch-does-not-share-favorite",[](auto dir) { cas::Preferences p; p.selection_mode="last_manual"; Fixture f(dir,p); f.pet(0); f.load(); f.manual(0); f.clear_pet(); f.put<std::uint64_t>(common+0x8980,0x43); f.load(); f.run(); require(f.queues.empty(),"Second local save inherited first save favorite"); f.put<std::uint64_t>(common+0x8980,0x42); f.load(); f.run(); require(f.queues==std::vector<int>{0},"Returning save failed to restore its own favorite"); });
    add("duplicate-roster-identities-cancel",[](auto dir) { Fixture f(dir); f.pet(0); f.pet(1); f.put<std::uint64_t>(owner+0x24A0+0x2330,1); f.put<std::uint64_t>(owner+0x24A0+0x23C0,100); f.exit(); f.run(); require(f.queues.empty(),"Duplicate identity guessed by slot"); });
    add("reserved-identity-change-cancels",[](auto dir) { Fixture f(dir); f.pet(0); f.exit(); f.step(); f.step(); f.put<std::uint64_t>(owner+0x2330,999); f.run(); require(f.queues.empty(),"Changed slot occupant was substituted"); });
    add("raw-weird-subtype-roster-change-cancels",[](auto dir) { Fixture f(dir); f.pet(0,8); f.put<std::uint32_t>(solar+0x6148,7); bool changed=false; f.after_read=[&](Address address){if(!changed && address==owner+0x2480){changed=true;f.put<std::uint32_t>(owner+0x2480,9);}}; f.exit(); f.run(); require(changed && f.queues.empty(),"Normalized-equal raw habitat mutation was missed"); });
    add("placement-reentry-enter-cancels",[](auto dir) { Fixture f(dir); f.pet(0); f.on_placement=[&]{f.runtime->beforeEnter(player);}; f.exit(); f.run(); require(f.queues.empty() && f.runtime->enabled(),"Placement reentry cancellation ignored"); });
    add("eligibility-reentry-off-cancels",[](auto dir) { Fixture f(dir); f.pet(0); f.on_can=[&]{f.toggle(0,false);}; f.exit(); f.run(); require(f.queues.empty(),"Eligibility callback bypassed pending OFF"); });
    add("eligibility-reentry-save-load-cancels",[](auto dir) { Fixture f(dir); f.pet(0); f.on_can=[&]{f.runtime->beforeLoad(false);}; f.exit(); f.run(); require(f.queues.empty(),"Eligibility callback used stale loaded context"); });
    add("final-eligibility-reentry-enter-cancels",[](auto dir) { Fixture f(dir); f.pet(0); bool reached=false; std::function<void()> callback; callback=[&]{if(f.can_calls_this_frame<2){f.on_can=callback;return;}reached=true;f.runtime->beforeEnter(player);};f.on_can=callback;f.exit();f.run();require(reached && f.queues.empty(),"Final eligibility reentry bypassed prequeue intent guard"); });
    add("owned-service-error-fails-closed",[](auto dir) { Fixture f(dir); f.pet(0); f.on_owned=[] {throw std::runtime_error("Synthetic native failure");}; f.exit(); f.run(); require(f.queues.empty() && !f.runtime->enabled(),"Native read/call error failed open"); });
    add("concurrent-callback-closes-safety-latch",[](auto dir) { Fixture f(dir); f.pet(0); f.on_owned=[&]{std::thread other([&]{f.runtime->beforeEnter(player);});other.join();}; f.exit(); f.run(); require(f.queues.empty() && !f.runtime->enabled(),"Cross-thread callback contention failed open"); });
    add("same-thread-owner-reentry-does-not-double-queue",[](auto dir) { Fixture f(dir); f.pet(0); f.on_can=[&]{f.runtime->afterOwner(owner,.05f);}; f.exit(); f.run(); require(f.queues.size()==1 && f.runtime->enabled(),"Nested owner callback duplicated or corrupted request"); });
    add("queue-reentry-invalidated-context-does-not-read-old-app",[](auto dir) { Fixture f(dir); f.pet(0); f.after_queue=[&]{f.runtime->beforeLoad(false);f.put<Address>(app_pointer,0); for(Address byte=queued;byte<queued+sizeof(int);++byte)f.memory.erase(byte);}; f.exit(); f.run(); require(f.queues.size()==1 && f.runtime->enabled(),"Queue reentry dereferenced retired player memory"); });
    add("invalid-settings-retained-and-start-off",[](auto dir) { Fixture f(dir); f.runtime.reset(); {std::ofstream file(dir/L"settings.json",std::ios::binary);file<<"{invalid";} cas::RuntimeServices s; s.base=base;s.read=[&](auto a,auto*o,auto n){f.read(a,o,n);};s.random=[](auto){return std::size_t(0);};s.clock=[&]{return f.now;};s.log=[](auto){};f.runtime=std::make_unique<cas::Runtime>(std::move(s),dir);f.pet(0);f.load();f.exit();f.run();require(f.queues.empty(),"Malformed preferences enabled automation");std::ifstream file(dir/L"settings.json",std::ios::binary);std::string raw((std::istreambuf_iterator<char>(file)),{});require(raw=="{invalid","Malformed preferences overwritten"); });
    return tests;
}
}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) { std::cerr<<"Expected an explicit fresh fixture directory\n"; return 2; }
    const auto root = std::filesystem::u8path(argv[1]);
    if (!root.is_absolute() || std::filesystem::exists(root)) { std::cerr<<"Fixture directory must be absolute and new\n"; return 2; }
    std::filesystem::create_directories(root);
    Json results=Json::array(); bool passed=true;
    for (const auto& test: cases()) {
        try { test.second(root/std::filesystem::u8path(test.first)/L"Káťa 猫"); results.push_back({{"name",test.first},{"status","passed"}}); }
        catch(const std::exception& error){passed=false;results.push_back({{"name",test.first},{"status","failed"},{"error",error.what()}});}
    }
    std::cout<<Json{{"status",passed?"passed":"failed"},{"cases",results.size()},{"results",results}}.dump(2)<<"\n";
    return passed?0:1;
}
