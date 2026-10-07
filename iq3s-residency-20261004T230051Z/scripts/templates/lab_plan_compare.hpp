// Buffered per-layer arithmetic snapshots for diagnosing device-plan divergence.
#pragma once
#include "strata/research/lab_trace.hpp"
#include "strata/kernels/elementwise.hpp"
#include <cuda_runtime.h>
#include <array>
#include <stdexcept>
namespace strata::research {
struct PlanCompare {
    bool enabled=false;
    static constexpr int rows=4, width=2560, plan_words=1024;
    std::array<float*,2> host_vectors{},mapped_vectors{};
    std::array<int32_t*,2> host_plans{},mapped_plans{};
    std::array<int,2> first{},last{};
    PlanCompare(){const char* e=std::getenv("STRATA_LAB_PLAN_COMPARE");enabled=e&&e[0]=='1'&&trace.enabled;}
    bool configure(int device,int begin,int end,std::string& error){
        if(!enabled)return true;
        if(device<0||device>1||host_vectors[device]||begin>=end){error="plan compare: unsupported stage";return false;}
        first[device]=begin;last[device]=end;
        const size_t vb=(size_t)(end-begin)*2*rows*width*sizeof(float);
        const size_t pb=(size_t)(end-begin)*plan_words*sizeof(int32_t);
        if(cudaHostAlloc(&host_vectors[device],vb,cudaHostAllocMapped)!=cudaSuccess||
           cudaHostGetDevicePointer(&mapped_vectors[device],host_vectors[device],0)!=cudaSuccess||
           cudaHostAlloc(&host_plans[device],pb,cudaHostAllocMapped)!=cudaSuccess||
           cudaHostGetDevicePointer(&mapped_plans[device],host_plans[device],0)!=cudaSuccess){error="plan compare: allocation";return false;}
        std::fprintf(stderr,"plan compare: CUDA%d diagnostic mappedCPU %zu bytes; no explicit GPU buffer\n",device,vb+pb);
        return true;
    }
    void capture(int device,int layer,int tokens,const float* mixed,const float* output,const int32_t* plan,int words,cudaStream_t stream){
        if(!enabled)return;
        if(tokens<1||tokens>rows||words>plan_words)throw std::runtime_error("plan compare: geometry");
        const size_t i=(size_t)(layer-first[device]);
        strata::kernels::copy_from_mapped(mapped_vectors[device]+i*2*rows*width,mixed,(int64_t)tokens*width,stream);
        strata::kernels::copy_from_mapped(mapped_vectors[device]+(i*2+1)*rows*width,output,(int64_t)tokens*width,stream);
        strata::kernels::copy_from_mapped((float*)(mapped_plans[device]+i*plan_words),(const float*)plan,words,stream);
    }
    void completed(int device){
        if(!enabled||!trace.active||trace.windows.size()>8)return;
        const auto w=trace.window;
        const std::string prefix=trace.prefix+"-request"+std::to_string(trace.request)+"-window"+std::to_string(w)+"-device"+std::to_string(device);
        std::vector<float> v(host_vectors[device],host_vectors[device]+(size_t)(last[device]-first[device])*2*rows*width);
        std::vector<int32_t> p(host_plans[device],host_plans[device]+(size_t)(last[device]-first[device])*plan_words);
        trace.file(prefix+"-layer-vectors.bin",v);trace.file(prefix+"-plans.bin",p);
    }
};
inline PlanCompare plan_compare;
}
