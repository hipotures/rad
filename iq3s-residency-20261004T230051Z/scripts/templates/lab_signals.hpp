// Bounded default-off signal and actual handoff diagnostics; never a residency policy.
#pragma once
#include "strata/research/lab_trace.hpp"
#include "strata/core/weights.hpp"
#include "strata/core/layout.hpp"
#include <cuda_runtime.h>
#include <algorithm>
#include <array>
#include <cstring>
#include <limits>
#include <stdexcept>

namespace strata::research {
struct ActivationRecord {
    uint64_t window, available_ns, offset;
    int32_t layer, token_base, tokens, width;
};
static_assert(sizeof(ActivationRecord)==40);
struct BoundaryRecord {
    uint64_t window, begin_ns, end_ns, bytes;
    int32_t device, stage_begin, stage_end, kind;
    float gpu_ms;
    int32_t reserved;
};
static_assert(sizeof(BoundaryRecord)==56);
struct Signals {
    bool enabled=false;
    std::string prefix;
    int64_t width=0, experts=0, hc=0;
    std::array<bool,2> configured{};
    std::array<std::array<cudaEvent_t,4>,2> events{};
    std::vector<ActivationRecord> activations;
    std::vector<float> values;
    std::vector<BoundaryRecord> boundaries;
    static constexpr std::array<int32_t,6> current_layers{5,20,24,25,40,46};
    Signals() {
        const char* p=std::getenv("STRATA_LAB_SIGNAL");
        const char* t=std::getenv("STRATA_LAB_TRACE");
        enabled=p && p[0]=='1' && t && t[0];
        if(enabled) prefix=t;
    }
    bool selected(int32_t layer) const {
        return std::find(current_layers.begin(),current_layers.end(),layer)!=current_layers.end();
    }
    bool configure(const strata::core::WeightTable& wt,const strata::core::ModelGeometry& g,
                   int32_t device,int32_t first,int32_t last,std::string& err) {
        if(!enabled) return true;
        if(device<0 || device>1) {err="lab signals: only the frozen two-device experiment is supported";return false;}
        if(configured[(size_t)device]) return true;
        width=g.n_embd;experts=g.n_expert;hc=g.hc;
        std::filesystem::create_directories(std::filesystem::path(prefix).parent_path());
        for(cudaEvent_t& event:events[(size_t)device]) {
            if(cudaEventCreate(&event)!=cudaSuccess) {err="lab signals: cannot allocate timing event";return false;}
        }
        for(int32_t current:current_layers) {
            const int32_t target=current+1;
            if(target<first || target>=last) continue;
            const auto* w=wt.find("blk."+std::to_string(target)+".ffn_gate_inp.weight");
            const uint64_t expected=(uint64_t)width*(uint64_t)experts*2;
            if(!w || w->kind!=strata::core::WeightKind::Bf16InF32 || w->bytes!=expected) {
                err="lab signals: next-router is not the expected native BF16 gate, layer "+std::to_string(target);
                return false;
            }
            std::vector<uint16_t> host((size_t)width*(size_t)experts);
            if(cudaMemcpy(host.data(),w->data,(size_t)expected,cudaMemcpyDeviceToHost)!=cudaSuccess) {
                err="lab signals: cannot snapshot original BF16 gate";return false;
            }
            const std::string path=prefix+"-gate-layer"+std::to_string(target)+".bin";
            if(std::filesystem::exists(path)) {err="lab signals: refuse gate snapshot overwrite";return false;}
            trace.file(path,host);
        }
        configured[(size_t)device]=true;
        const std::string meta=prefix+"-geometry-device"+std::to_string(device)+".json";
        FILE* file=std::fopen(meta.c_str(),"w");
        if(!file) {err="lab signals: cannot write geometry";return false;}
        std::fprintf(file,"{\"device\":%d,\"width\":%lld,\"experts\":%lld,\"hc\":%lld,\"first\":%d,\"last\":%d,\"capture_windows\":64,\"timing_events\":4}\n",
                     device,(long long)width,(long long)experts,(long long)hc,first,last);
        std::fclose(file);return true;
    }
    void begin() {
        if(!enabled) return;
        activations.clear();values.clear();boundaries.clear();
        activations.reserve(1024);values.reserve((size_t)64*6*4*(size_t)width);boundaries.reserve(20000);
    }
    void activation(int32_t layer,int32_t tokens,const float* x) {
        if(!enabled || !trace.active || trace.windows.size()>64 || !selected(layer)) return;
        const uint64_t available=ns(),offset=values.size();
        values.insert(values.end(),x,x+(size_t)tokens*(size_t)width);
        activations.push_back({trace.window,available,offset,layer,trace.token_base,tokens,(int32_t)width});
    }
    void mark_gpu(int32_t device,bool incoming,bool start,cudaStream_t stream) {
        if(!enabled || device<0 || device>1 || !configured[(size_t)device]) return;
        const int index=(incoming ? 0 : 2)+(start ? 0 : 1);
        // Default capture records a dependency rather than an observable event
        // node. External nodes retain elapsed-time observability after replay.
        if(cudaEventRecordWithFlags(events[(size_t)device][(size_t)index],stream,cudaEventRecordExternal)!=cudaSuccess)
            throw std::runtime_error("lab signals: event record failed");
    }
    void cpu(int32_t device,int32_t first,int32_t last,int32_t kind,uint64_t begin,uint64_t end,uint64_t bytes=0) {
        if(!enabled || !trace.active) return;
        boundaries.push_back({trace.window,begin,end,bytes,device,first,last,kind,std::numeric_limits<float>::quiet_NaN(),0});
    }
    void completed(int32_t device,int32_t first,int32_t last,int32_t T,int64_t layers) {
        if(!enabled || !trace.active || trace.windows.size()>64) return;
        const uint64_t bytes=(uint64_t)T*(uint64_t)(hc*width+width+hc)*4;
        const uint64_t observed=ns();
        for(int incoming=0;incoming<2;++incoming) {
            if((incoming && first==0) || (!incoming && last==layers)) continue;
            const int index=incoming ? 0 : 2;float elapsed=0;
            const cudaError_t result=cudaEventElapsedTime(&elapsed,events[(size_t)device][(size_t)index],events[(size_t)device][(size_t)index+1]);
            if(result!=cudaSuccess) throw std::runtime_error("lab signals: completed graph timing unavailable");
            // CPU time is completion observation, not a GPU-clock timestamp.
            boundaries.push_back({trace.window,observed,observed,bytes,device,first,last,incoming ? 10 : 11,elapsed,0});
        }
    }
    void flush() {
        if(!enabled) return;
        const std::string path=prefix+"-request"+std::to_string(trace.request);
        trace.file(path+"-activations.bin",activations);trace.file(path+"-activation-values.bin",values);trace.file(path+"-boundaries.bin",boundaries);
        std::fprintf(stderr,"strata lab signals: %zu activation records, %zu bytes of activation values, %zu boundary records; only first64 windows capture numeric signals\n",activations.size(),values.size()*4,boundaries.size());
    }
};
inline Signals signals;
}
