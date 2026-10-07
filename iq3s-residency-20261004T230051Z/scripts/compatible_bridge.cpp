// Offline bridge for exact native/Python selector equivalence and native cost.
#include "strata/research/compatible_policy.hpp"
struct CSwap {double gain;int32_t layer,in,out_layer,out;};
extern "C" int compatible_bridge(const float* heat,const int32_t* resident,int nl,int ne,int split,
        const uint64_t* blob,const uint64_t* slots0,int count0,const uint64_t* slots1,int count1,
        int maximum,CSwap* result) {
    const auto swaps=strata::research::select_compatible(heat,resident,nl,ne,split,
        std::vector<uint64_t>(blob,blob+nl),std::vector<uint64_t>(slots0,slots0+count0),std::vector<uint64_t>(slots1,slots1+count1),maximum);
    for(size_t i=0;i<swaps.size();++i){const auto& s=swaps[i];result[i]={s.gain,s.layer,s.in,s.out_layer,s.out};}
    return (int)swaps.size();
}
