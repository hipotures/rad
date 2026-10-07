#include "strata/kernels/cpu/native_expert.hpp"
#include "strata/kernels/cpu/pool.hpp"
#include "ggml.h"
#include <vector>
#include <cmath>
#include <iostream>
#include <cstring>
using namespace strata::kernels::cpu;
int main() {
    NativeFmt f; std::string err;
    if (!native_fmt(14,8,2560,640,f,err)) { std::cerr << err; return 1; }
    std::vector<uint8_t> blob(f.bytes);
    std::vector<float> weights(2560*640);
    for (size_t i=0;i<weights.size();++i) weights[i]=0.01f*std::sin(float(i%1009)*0.1f);
    ggml_quantize_chunk(GGML_TYPE_Q6_K,weights.data(),blob.data(),0,640,2560,nullptr);
    ggml_quantize_chunk(GGML_TYPE_Q6_K,weights.data(),blob.data()+f.up_off,0,640,2560,nullptr);
    ggml_quantize_chunk(GGML_TYPE_Q8_0,weights.data(),blob.data()+f.down_off,0,2560,640,nullptr);
    constexpr int nt=3;
    alignas(64) uint8_t act[nt][kNativeActBytes], hq[nt][kNativeHBytes];
    std::vector<float> x(2560), ff(nt*640), ref(nt*2560), pooled(nt*2560);
    const void* acts[nt]; const void* hs[nt]; float* ffs[nt]; float* outs[nt];
    ExpertJobMulti job; job.blob=blob.data(); job.nt=nt;
    for (int t=0;t<nt;++t) {
        for (int i=0;i<2560;++i) x[i]=std::cos(float(i+t)*0.07f);
        native_quant_act(f,x.data(),act[t]); acts[t]=act[t]; ffs[t]=ff.data()+t*640;
        outs[t]=ref.data()+t*2560; job.nact[t]=act[t]; job.out[t]=pooled.data()+t*2560;
    }
    native_gu_rows(f,blob.data(),acts,nt,ffs,0,640);
    for (int t=0;t<nt;++t) { native_quant_h(f,ffs[t],hq[t]); hs[t]=hq[t]; }
    native_down_rows(f,blob.data(),hs,nt,outs,0,2560);
    ExpertPool pool(2,false,true); pool.run_split_multi_native(f,&job,1);
    float maxdiff=0; size_t nonzero=0;
    for (size_t i=0;i<ref.size();++i) {
        if (!std::isfinite(pooled[i])) return 2;
        maxdiff=std::max(maxdiff,std::abs(ref[i]-pooled[i])); nonzero+=(pooled[i]!=0);
    }
    bool exact=std::memcmp(ref.data(),pooled.data(),ref.size()*sizeof(float))==0;
    std::cout << "{\"status\":\"" << ((exact&&nonzero)?"PASS":"FAIL")
      << "\",\"gu_type\":14,\"down_type\":8,\"n_embd\":2560,\"n_ff\":640,\"tokens\":3,\"blob_bytes\":" << f.bytes
      << ",\"pool_vs_serial_bit_identical\":" << (exact?"true":"false") << ",\"max_abs_diff\":" << maxdiff
      << ",\"nonzero_outputs\":" << nonzero << "}\n";
    return (exact&&nonzero)?0:3;
}
