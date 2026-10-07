// Same choices as compatible-v1; linear heap construction replaces sorting cold buckets.
#pragma once
#include <algorithm>
#include <cstdint>
#include <tuple>
#include <vector>

namespace strata::research {
struct CompatibleSwap {double gain;int32_t layer,in,out_layer,out;};
struct CompatibleVictim {float heat;int32_t layer,expert,slot;};
struct CompatibleIncoming {float heat;int32_t layer,expert;};
struct CompatibleBucket {uint64_t bytes;std::vector<CompatibleVictim> cold;};
inline std::vector<CompatibleSwap> select_compatible(const float* heat,const int32_t* resident,
        int32_t nl,int32_t ne,int32_t split,const std::vector<uint64_t>& blob,
        const std::vector<uint64_t>& slots0,const std::vector<uint64_t>& slots1,int32_t maximum) {
    std::vector<CompatibleSwap> choices;
    if(!heat || !resident || nl<=0 || ne<=0 || split<=0 || split>=nl ||
       blob.size()!=(size_t)nl || maximum<=0)return choices;
    const auto cold_after=[](const auto& a,const auto& b) {
        return std::tie(a.heat,a.layer,a.expert,a.slot)>std::tie(b.heat,b.layer,b.expert,b.slot);
    };
    for(int32_t gpu=0;gpu<2;++gpu) {
        const auto& sizes=gpu==0?slots0:slots1;
        const int32_t begin=gpu==0?0:split,end=gpu==0?split:nl;
        std::vector<CompatibleBucket> buckets;buckets.reserve(8);
        for(uint64_t bytes:sizes)
            if(std::none_of(buckets.begin(),buckets.end(),[bytes](const auto& b){return b.bytes==bytes;}))
                buckets.push_back({bytes,{}});
        std::sort(buckets.begin(),buckets.end(),[](const auto& a,const auto& b){return a.bytes<b.bytes;});
        std::vector<CompatibleIncoming> incoming;
        for(int32_t l=begin;l<end;++l)for(int32_t e=0;e<ne;++e) {
            const size_t index=(size_t)l*ne+e;const int32_t slot=resident[index];const float h=heat[index];
            if(slot>=0) {
                if((size_t)slot>=sizes.size() || blob[(size_t)l]>sizes[(size_t)slot])return {};
                const uint64_t bytes=sizes[(size_t)slot];
                auto b=std::lower_bound(buckets.begin(),buckets.end(),bytes,[](const auto& bucket,uint64_t need){return bucket.bytes<need;});
                b->cold.push_back({h,l,e,slot});
            } else if(h>=2.0f)incoming.push_back({h,l,e});
        }
        for(auto& bucket:buckets)std::make_heap(bucket.cold.begin(),bucket.cold.end(),cold_after);
        std::sort(incoming.begin(),incoming.end(),[](const auto& a,const auto& b){
            if(a.heat!=b.heat)return a.heat>b.heat;
            return std::tie(a.layer,a.expert)<std::tie(b.layer,b.expert);
        });
        for(const auto& hot:incoming) {
            CompatibleBucket* best=nullptr;
            for(auto& bucket:buckets) {
                if(bucket.bytes<blob[(size_t)hot.layer] || bucket.cold.empty())continue;
                if(!best || std::tie(bucket.cold.front().heat,bucket.bytes)<std::tie(best->cold.front().heat,best->bytes))
                    best=&bucket;
            }
            if(!best || (double)hot.heat<(double)best->cold.front().heat+1.5)continue;
            const auto cold=best->cold.front();
            std::pop_heap(best->cold.begin(),best->cold.end(),cold_after);best->cold.pop_back();
            choices.push_back({(double)hot.heat-(double)cold.heat,hot.layer,hot.expert,cold.layer,cold.expert});
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
