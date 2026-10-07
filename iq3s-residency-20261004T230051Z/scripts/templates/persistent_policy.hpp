// Persistent, same-device variable-byte admission. No mathematical expert changes.
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <tuple>
#include <vector>
namespace strata::research {
struct PersistentConfig {
 float prediction_weight=.5f;
 double miss_entry_us=80.0, forecast_windows=16.0, copy_GB_s=1.8, launch_us=4.2;
 float margin=1.5f;
 uint64_t bytes_per_device=16ull*1024*1024;
 uint64_t minimum_age=8, protect_recent=2, candidate_recent=8;
};
struct PersistentSwap {double utility_us;int32_t layer,in,out_layer,out,slot;uint64_t bytes;};
struct PersistentVictim {double score;int32_t layer,expert,slot;};
struct PersistentBucket {uint64_t bytes;std::vector<PersistentVictim>cold;};
struct PersistentIncoming {double score;int32_t layer,expert;};
inline std::vector<PersistentSwap> select_persistent(const float* heat,const float* prediction,
 const uint64_t* last,const uint64_t* born,const int32_t* resident,int32_t nl,int32_t ne,int32_t split,
 const std::vector<uint64_t>& blob,const std::vector<uint64_t>& slots0,const std::vector<uint64_t>&slots1,
 uint64_t window,int32_t maximum,const PersistentConfig&cfg={}) {
 std::vector<PersistentSwap>result;
 if(!heat||!prediction||!last||!born||!resident||nl<=0||ne<=0||split<=0||split>=nl||blob.size()!=(size_t)nl||maximum<=0||cfg.copy_GB_s<=0)return result;
 constexpr auto never=std::numeric_limits<uint64_t>::max();
 const auto recent=[&](uint64_t at,uint64_t n){return at!=never&&window>=at&&window-at<n;};
 const auto cold_after=[](const auto&a,const auto&b){return std::tie(a.score,a.layer,a.expert,a.slot)>std::tie(b.score,b.layer,b.expert,b.slot);};
 // Existing heat is a four-window EMA with decay .7; forecast16windows=4blocks.
 const double avoided_us_per_heat=cfg.miss_entry_us*(cfg.forecast_windows/4.0)*.3;
 for(int gpu=0;gpu<2;++gpu){
  const auto& sizes=gpu?slots1:slots0;const int begin=gpu?split:0,end=gpu?nl:split;
  std::vector<PersistentBucket>buckets;std::vector<PersistentIncoming>incoming;
  for(uint64_t b:sizes)if(std::none_of(buckets.begin(),buckets.end(),[&](const auto&q){return q.bytes==b;}))buckets.push_back({b,{}});
  std::sort(buckets.begin(),buckets.end(),[](const auto&a,const auto&b){return a.bytes<b.bytes;});
  for(int l=begin;l<end;++l)for(int e=0;e<ne;++e){
   size_t i=(size_t)l*ne+e;double score=(double)heat[i]+(double)cfg.prediction_weight*prediction[i];
   if(!std::isfinite(score))return {};
   int slot=resident[i];
   if(slot>=0){
    if((size_t)slot>=sizes.size()||blob[l]>sizes[slot])return {};
    if(recent(last[i],cfg.protect_recent)||recent(born[i],cfg.minimum_age))continue;
    auto b=std::lower_bound(buckets.begin(),buckets.end(),sizes[slot],[](const auto&q,uint64_t v){return q.bytes<v;});b->cold.push_back({score,l,e,slot});
   }else if(heat[i]>=2.f&&recent(last[i],cfg.candidate_recent))incoming.push_back({score,l,e});
  }
  for(auto&b:buckets)std::make_heap(b.cold.begin(),b.cold.end(),cold_after);
  std::sort(incoming.begin(),incoming.end(),[](const auto&a,const auto&b){if(a.score!=b.score)return a.score>b.score;return std::tie(a.layer,a.expert)<std::tie(b.layer,b.expert);});
  uint64_t bytes=0;
  for(const auto&hot:incoming){
   uint64_t need=blob[hot.layer];if(need>cfg.bytes_per_device-bytes)continue;
   PersistentBucket*best=nullptr;
   for(auto&b:buckets)if(b.bytes>=need&&!b.cold.empty()&&(!best||std::tie(b.cold.front().score,b.bytes)<std::tie(best->cold.front().score,best->bytes)))best=&b;
   if(!best)continue;
   const auto cold=best->cold.front();
   double utility=(hot.score-cold.score-cfg.margin)*avoided_us_per_heat-(double)need/(cfg.copy_GB_s*1e3)-cfg.launch_us;
   if(utility<=0)continue;
   std::pop_heap(best->cold.begin(),best->cold.end(),cold_after);best->cold.pop_back();
   result.push_back({utility,hot.layer,hot.expert,cold.layer,cold.expert,cold.slot,need});bytes+=need;
  }
 }
 std::sort(result.begin(),result.end(),[](const auto&a,const auto&b){if(a.utility_us!=b.utility_us)return a.utility_us>b.utility_us;return std::tie(a.layer,a.in,a.out_layer,a.out)<std::tie(b.layer,b.in,b.out_layer,b.out);});
 if(result.size()>(size_t)maximum)result.resize(maximum);
 return result;
}
}
