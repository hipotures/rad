// Exact selector transcription from frozen Strata generate.cpp, serve adapt().
// Used only to validate trace replay, never as an inference replacement.
#include <algorithm>
#include <cstdint>
#include <vector>
struct Swap { float gain; int32_t layer, in, out; };
extern "C" int select_current(const float* usage, const int32_t* resident,
                              int nl, int ne, int max_swaps, Swap* output) {
    std::vector<Swap> swaps;
    std::vector<std::pair<float,int32_t>> cand,vict;
    for(int l=0;l<nl;++l) {
        cand.clear();vict.clear();
        const float* u=usage+l*ne;const int32_t* r=resident+l*ne;
        for(int32_t e=0;e<ne;++e) {
            if(r[e]<0) { if(u[e]>=2.0f)cand.emplace_back(u[e],e); }
            else vict.emplace_back(u[e],e);
        }
        if(cand.empty()||vict.empty())continue;
        std::sort(cand.begin(),cand.end(),[](auto& a,auto& b){return a.first>b.first;});
        const size_t nc=std::min(cand.size(),vict.size());
        std::partial_sort(vict.begin(),vict.begin()+nc,vict.end(),[](auto& a,auto& b){return a.first<b.first;});
        for(size_t i=0;i<nc;++i) {
            if(cand[i].first<vict[i].first+1.5f)break;
            swaps.push_back({cand[i].first-vict[i].first,l,cand[i].second,vict[i].second});
        }
    }
    std::sort(swaps.begin(),swaps.end(),[](const Swap& a,const Swap& b){return a.gain>b.gain;});
    if((int)swaps.size()>max_swaps)swaps.resize(max_swaps);
    std::copy(swaps.begin(),swaps.end(),output);
    return (int)swaps.size();
}
extern "C" void update_usage(float* u,const int16_t* expert,int n) {
    for(int i=0;i<n;++i)u[expert[i]]+=1.0f;
}
