// Default-off, same-device compatible physical-slot policy. No model routing changes.
#pragma once
#include <algorithm>
#include <cstdint>
#include <map>
#include <tuple>
#include <vector>

namespace strata::research {
struct CompatibleSwap {double gain;int32_t layer,in,out_layer,out;};
struct CompatibleVictim {float heat;int32_t layer,expert,slot;};
struct CompatibleIncoming {float heat;int32_t layer,expert;};
inline std::vector<CompatibleSwap> select_compatible(const float* heat,const int32_t* resident,
        int32_t nl,int32_t ne,int32_t split,const std::vector<uint64_t>& blob,
        const std::vector<uint64_t>& slots0,const std::vector<uint64_t>& slots1,int32_t maximum) {
    std::vector<CompatibleSwap> choices;
    if(!heat || !resident || nl<=0 || ne<=0 || split<=0 || split>=nl ||
       blob.size()!=(size_t)nl || maximum<=0)return choices;
    for(int32_t gpu=0;gpu<2;++gpu) {
        const auto& sizes=gpu==0?slots0:slots1;
        const int32_t begin=gpu==0?0:split,end=gpu==0?split:nl;
        std::map<uint64_t,std::vector<CompatibleVictim>> buckets;
        std::map<uint64_t,size_t> used;
        std::vector<CompatibleIncoming> incoming;
        for(int32_t l=begin;l<end;++l)for(int32_t e=0;e<ne;++e) {
            const size_t index=(size_t)l*ne+e;const int32_t slot=resident[index];const float h=heat[index];
            if(slot>=0) {
                if((size_t)slot>=sizes.size() || blob[(size_t)l]>sizes[(size_t)slot])return {};
                buckets[sizes[(size_t)slot]].push_back({h,l,e,slot});
            } else if(h>=2.0f)incoming.push_back({h,l,e});
        }
        for(auto& [size,victims]:buckets)std::sort(victims.begin(),victims.end(),[](const auto& a,const auto& b){
            return std::tie(a.heat,a.layer,a.expert,a.slot)<std::tie(b.heat,b.layer,b.expert,b.slot);
        });
        std::sort(incoming.begin(),incoming.end(),[](const auto& a,const auto& b){
            if(a.heat!=b.heat)return a.heat>b.heat;
            return std::tie(a.layer,a.expert)<std::tie(b.layer,b.expert);
        });
        for(const auto& hot:incoming) {
            uint64_t best_size=0;CompatibleVictim best{};bool found=false;
            for(const auto& [size,victims]:buckets) {
                const size_t index=used[size];
                if(size<blob[(size_t)hot.layer] || index>=victims.size())continue;
                const auto& cold=victims[index];
                if(!found || std::tie(cold.heat,size)<std::tie(best.heat,best_size)) {
                    best=cold;best_size=size;found=true;
                }
            }
            if(!found || (double)hot.heat<(double)best.heat+1.5)continue;
            ++used[best_size];
            choices.push_back({(double)hot.heat-(double)best.heat,hot.layer,hot.expert,best.layer,best.expert});
        }
    }
    std::sort(choices.begin(),choices.end(),[](const auto& a,const auto& b){
        if(a.gain!=b.gain)return a.gain>b.gain;
        return std::tie(a.layer,a.in,a.out_layer,a.out)<std::tie(b.layer,b.in,b.out_layer,b.out);
    });
    if(choices.size()>(size_t)maximum)choices.resize((size_t)maximum);
    return choices;
}
}
