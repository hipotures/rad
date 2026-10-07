// Diagnostic-only GPU spans. No policy, new synchronization, or per-token I/O.
#pragma once
#include "strata/research/lab_trace.hpp"
#include <cuda_runtime.h>
#include <array>
#include <cmath>
#include <stdexcept>

namespace strata::research {
struct MissSpanRecord {
    uint64_t window, observed_ns;
    int32_t device, layer, group, phase, tokens, token_base;
    float gpu_ms;
    int32_t reserved;
};
static_assert(sizeof(MissSpanRecord)==48);
struct MissWaits {
    // Fixed diagnostic layer sample, not a model routing or placement rule.
    static constexpr std::array<int32_t,3> layers{2,24,40};
    bool enabled=false;
    std::array<int32_t,3> owners{-1,-1,-1};
    std::array<std::array<std::array<std::array<cudaEvent_t,2>,4>,2>,3> events{};
    std::vector<MissSpanRecord> records;
    MissWaits() {
        const char* v=std::getenv("STRATA_LAB_MISS_WAITS");
        enabled=v && v[0]=='1' && trace.enabled;
    }
    int index(int32_t layer) const {
        for(size_t i=0;i<layers.size();++i) if(layers[i]==layer) return (int)i;
        return -1;
    }
    bool configure(int32_t device,int32_t first,int32_t last,bool all_resident,std::string& err) {
        if(!enabled) return true;
        if(device<0 || device>1 || all_resident) {
            err="lab miss waits requires the frozen non-all-resident dual-device verifier";
            return false;
        }
        for(size_t i=0;i<layers.size();++i) {
            if(layers[i]<first || layers[i]>=last) continue;
            if(owners[i]!=-1 && owners[i]!=device) {err="lab miss waits duplicate layer owner";return false;}
            if(owners[i]==device) continue;
            owners[i]=device;
            for(auto& group:events[i]) for(auto& phase:group) for(auto& event:phase)
                if(cudaEventCreate(&event)!=cudaSuccess) {err="lab miss waits event allocation failed";return false;}
        }
        return true;
    }
    void begin() {
        if(!enabled) return;
        records.clear();records.reserve(120000);
    }
    void mark(int32_t device,int32_t layer,int32_t group,int32_t phase,bool start,cudaStream_t stream) {
        if(!enabled) return;
        const int i=index(layer);
        if(i<0) return;
        if(group<0 || group>1 || phase<0 || phase>3 || owners[(size_t)i]!=device)
            throw std::runtime_error("lab miss waits invalid event identity");
        // Explicit external nodes remain observable after CUDA graph replay.
        if(cudaEventRecordWithFlags(events[(size_t)i][(size_t)group][(size_t)phase][start ? 0 : 1],stream,
                                    cudaEventRecordExternal)!=cudaSuccess)
            throw std::runtime_error("lab miss waits event record failed");
    }
    void completed(int32_t device,int32_t T,int32_t groups) {
        if(!enabled || !trace.active) return;
        if(T<1 || T>8 || groups<1 || groups>2) throw std::runtime_error("lab miss waits invalid window");
        const int32_t split=(T+1)/2;
        const uint64_t observed=ns();
        for(size_t i=0;i<layers.size();++i) if(owners[i]==device)
            for(int32_t group=0;group<groups;++group) for(int32_t phase=0;phase<4;++phase) {
                float elapsed=0;
                const auto& pair=events[i][(size_t)group][(size_t)phase];
                if(cudaEventElapsedTime(&elapsed,pair[0],pair[1])!=cudaSuccess || !std::isfinite(elapsed) || elapsed<0)
                    throw std::runtime_error("lab miss waits captured elapsed time unavailable");
                const int32_t base=group ? split : 0;
                const int32_t n=groups==1 ? T : (group ? T-split : split);
                records.push_back({trace.window,observed,device,layers[i],group,phase,n,base,elapsed,0});
            }
    }
    void flush() {
        if(!enabled) return;
        trace.file(trace.prefix+"-request"+std::to_string(trace.request)+"-miss-spans.bin",records);
        std::fprintf(stderr,"strata lab miss waits: %zu buffered GPU phase spans, 3 selected layers, diagnostic only\n",records.size());
    }
};
inline MissWaits miss_waits;
}
