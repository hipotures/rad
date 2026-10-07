// Buffered host-clock diagnostics. No routing/cache algorithm changes and no per-event CUDA synchronization.
#pragma once
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>
#include <vector>

namespace strata::research {
inline uint64_t ns() { return (uint64_t) std::chrono::duration_cast<std::chrono::nanoseconds>(
    std::chrono::steady_clock::now().time_since_epoch()).count(); }
struct Entry { int16_t expert; int8_t token; int8_t path; int32_t slot; };
static_assert(sizeof(Entry)==8);
struct Layer { uint64_t window, t0, t1, t2, t3, t4, offset; uint32_t layer; uint16_t tokens, k; };
static_assert(sizeof(Layer)==64);
struct Window { uint64_t number, position, begin, verify_end, end, pending_begin, pending_end; uint32_t T, accepted, produced, reserved; int32_t tokens[8]; };
static_assert(sizeof(Window)==104);
struct Promotion { uint64_t window, issue, observed_ready, bytes; int32_t layer, incoming, outgoing, slot; };
static_assert(sizeof(Promotion)==48);
struct Reach { uint64_t window, begin, reached, released; int32_t layer, reserved; };
static_assert(sizeof(Reach)==40);
struct Trace {
    bool enabled=false, active=false;
    std::string prefix;
    uint64_t request=0, window=0;
    int32_t experts=0;
    int32_t token_base=0;
    std::vector<int32_t> initial, final;
    std::vector<float> initial_usage, final_usage;
    std::vector<uint64_t> blob_bytes;
    std::vector<uint64_t> slot_bytes0, slot_bytes1;
    std::vector<Entry> entries;
    std::vector<Layer> layers;
    std::vector<Window> windows;
    std::vector<Promotion> promotions;
    std::vector<Reach> reach;
    std::vector<int32_t> output_ids;
    Trace() {
        const char* p=std::getenv("STRATA_LAB_TRACE");
        if (p && *p) { enabled=true; prefix=p; }
    }
    void begin(const std::vector<int32_t>& resident, int32_t ne, const std::vector<uint64_t>& bytes, const std::vector<float>& usage) {
        if (!enabled) return;
        ++request; window=0; experts=ne; initial=resident; blob_bytes=bytes; initial_usage=usage;
        entries.clear(); layers.clear(); windows.clear(); promotions.clear(); reach.clear(); output_ids.clear();
        entries.reserve(3000000); layers.reserve(100000); windows.reserve(4096); promotions.reserve(100000); reach.reserve(100000);
        active=true;
    }
    void begin_window(uint64_t number,uint64_t position,uint32_t T,const int32_t* ids) {
        if (!active) return;
        window=number; token_base=0; Window w{};w.number=number;w.position=position;w.T=T;w.begin=ns();
        for (uint32_t i=0;i<T && i<8;++i) w.tokens[i]=(int32_t)ids[i];
        windows.push_back(w);
    }
    void decision(uint32_t layer,uint16_t nt,uint16_t k,const int32_t* ids,const int32_t* kind,
                  const int32_t* resident,uint64_t t0,uint64_t t1,uint64_t t2,uint64_t t3,uint64_t t4) {
        if (!active) return;
        Layer l{window,t0,t1,t2,t3,t4,(uint64_t)entries.size(),layer,nt,k};layers.push_back(l);
        for (int i=0;i<nt*k;++i) entries.push_back({(int16_t)ids[i],(int8_t)(i/k+token_base),(int8_t)kind[i],
            resident ? resident[(size_t)layer*(size_t)experts+(size_t)ids[i]] : -1});
    }
    void accept(uint32_t a) { if(active && !windows.empty()) {windows.back().accepted=a;windows.back().verify_end=ns();} }
    void finish_window(uint32_t produced) { if(active && !windows.empty()) {windows.back().produced=produced;windows.back().end=ns();} }
    void pending(bool start) { if(active && !windows.empty()) {(start ? windows.back().pending_begin : windows.back().pending_end)=ns();} }
    void promotion(int32_t l,int32_t in,int32_t out,int32_t slot,uint64_t bytes) {
        if(active) promotions.push_back({window,ns(),0,bytes,l,in,out,slot});
    }
    void ready(int32_t index,int32_t slot) {
        if(!active) return;
        for(auto it=promotions.rbegin();it!=promotions.rend();++it)
            if(it->observed_ready==0 && it->layer*experts+it->incoming==index && it->slot==slot) {it->observed_ready=ns();break;}
    }
    void reached(int32_t layer,uint64_t begin,uint64_t reached,uint64_t released) {
        if(active) reach.push_back({window,begin,reached,released,layer,0});
    }
    template<class T> void file(const std::string& p,const std::vector<T>& data) {
        FILE* f=std::fopen(p.c_str(),"wb");
        if(!f) { std::fprintf(stderr,"strata lab trace: cannot write %s\n",p.c_str());return; }
        std::fwrite(data.data(),sizeof(T),data.size(),f);std::fclose(f);
    }
    void flush(const std::vector<int32_t>& resident, const std::vector<float>& usage) {
        if(!active) return;
        active=false;final=resident;final_usage=usage;
        const std::string p=prefix+"-request"+std::to_string(request);
        std::filesystem::create_directories(std::filesystem::path(p).parent_path());
        file(p+"-initial.bin",initial);file(p+"-final.bin",final);file(p+"-blob-bytes.bin",blob_bytes);
        file(p+"-slot-bytes-gpu0.bin",slot_bytes0);file(p+"-slot-bytes-gpu1.bin",slot_bytes1);
        file(p+"-initial-usage.bin",initial_usage);file(p+"-final-usage.bin",final_usage);
        file(p+"-entries.bin",entries);file(p+"-layers.bin",layers);file(p+"-windows.bin",windows);
        file(p+"-promotions.bin",promotions);file(p+"-reach.bin",reach);
        file(p+"-output-ids.bin",output_ids);
        std::fprintf(stderr,"strata lab trace: request %llu, %zu windows, %zu layers, %zu entries, %zu promotions, %zu reach records; host steady_clock nanoseconds\n",
          (unsigned long long)request,windows.size(),layers.size(),entries.size(),promotions.size(),reach.size());
    }
};
inline Trace trace;
}
