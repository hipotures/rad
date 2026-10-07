// Research-only persistent admission. Default OFF. Existing CUDA copy boundary is retained.
#pragma once
#include "strata/research/persistent_policy.hpp"
#include "strata/core/weights.hpp"
#include "strata/core/layout.hpp"
#include "strata/kernels/bf16_gemv.hpp"
#include "strata/kernels/native_router.hpp"
#include "strata/kernels/elementwise.hpp"
#include <cuda_runtime.h>
#include <array>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
namespace strata::research {
inline uint64_t persistent_ns(){return (uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}
struct PersistentRuntime {
 bool enabled=false,active=false;uint64_t window=0;int request=0;
 static constexpr int max_tokens=4,k=10;
 static constexpr std::array<int,5> origins{5,12,25,32,38},targets{13,20,33,40,46};
 struct Pair{bool valid=false;int device=-1;const uint16_t*gate=nullptr;};
 std::array<Pair,5>pairs{};std::array<bool,2>configured{};
 std::array<int32_t*,2>ids{},host_ids{},mapped_ids{};
 std::array<float*,2>weights{},host_weights{},mapped_weights{};
 std::array<uint32_t*,2>sequence{},mapped_sequence{};
 std::vector<float> prediction;std::vector<uint64_t>last,born;
 struct Admission{uint64_t issue=0,published=0,first_use=0,evicted=0,bytes=0,uses=0,use_windows=0,last_use=UINT64_MAX,victim_uses=0;int32_t layer,in,out_layer,out,slot;};
 std::vector<Admission>admissions;std::vector<int32_t>by_in,by_out;uint64_t host_prediction_entries=0,select_ns=0,pending_wait_ns=0;double selector_us=0;
 PersistentRuntime(){const char*v=std::getenv("STRATA_LAB_PERSISTENT");enabled=v&&v[0]=='1';if(enabled){prediction.assign(48*512,0.f);last.assign(48*512,UINT64_MAX);born=last;by_in.assign(48*512,-1);by_out=by_in;}}
 bool configure(const strata::core::WeightTable&wt,const strata::core::ModelGeometry&g,int device,int first,int end,std::string&error){
  if(!enabled)return true;
  if(device<0||device>1||g.n_embd!=2560||g.n_expert!=512||g.n_layers!=48||!((first==0&&end==25)||(first==25&&end==48))){error="persistent: only frozen IQ3_S K25 two-stage path";return false;}
  if(configured[device])return true;
  auto ok=[](cudaError_t e){return e==cudaSuccess;};
  if(!ok(cudaMalloc(&ids[device],max_tokens*k*sizeof(int32_t)))||!ok(cudaMalloc(&weights[device],max_tokens*k*sizeof(float)))||
   !ok(cudaHostAlloc(&host_ids[device],origins.size()*max_tokens*k*sizeof(int32_t),cudaHostAllocMapped))||!ok(cudaHostGetDevicePointer(&mapped_ids[device],host_ids[device],0))||
   !ok(cudaHostAlloc(&host_weights[device],origins.size()*max_tokens*k*sizeof(float),cudaHostAllocMapped))||!ok(cudaHostGetDevicePointer(&mapped_weights[device],host_weights[device],0))||
   !ok(cudaHostAlloc(&sequence[device],64,cudaHostAllocMapped))||!ok(cudaHostGetDevicePointer(&mapped_sequence[device],sequence[device],0))){error="persistent: bounded signal allocation failed";return false;}
  *sequence[device]=0;
  for(size_t i=0;i<origins.size();++i)if(origins[i]>=first&&targets[i]<end){const auto*gate=wt.find("blk."+std::to_string(targets[i])+".ffn_gate_inp.weight");if(!gate||gate->kind!=strata::core::WeightKind::Bf16InF32||gate->bytes!=2560ull*512*2){error="persistent: existing native BF16 gate missing";return false;}pairs[i]={true,device,(const uint16_t*)gate->data};}
  configured[device]=true;return true;
 }
 void score(int layer,int tokens,const float*x,float*scratch,cudaStream_t stream){
  if(!enabled)return;if(tokens<1||tokens>max_tokens)throw std::runtime_error("persistent: unsupported group geometry");
  for(size_t i=0;i<origins.size();++i)if(origins[i]==layer&&pairs[i].valid){const auto&p=pairs[i];int dev=p.device;
   strata::kernels::bf16_gemv_fp32_mmvf_multi(x,2560,p.gate,scratch,512,2560,512,tokens,stream);
   strata::kernels::native_router_top10_multi(scratch,ids[dev],weights[dev],tokens,stream);
   strata::kernels::doorbell_publish(nullptr,ids[dev],weights[dev],0,tokens*k,nullptr,mapped_ids[dev]+i*max_tokens*k,mapped_weights[dev]+i*max_tokens*k,mapped_sequence[dev],stream);
  }
 }
 void begin(){if(!enabled)return;active=true;++request;admissions.clear();admissions.reserve(4096);std::fill(by_in.begin(),by_in.end(),-1);std::fill(by_out.begin(),by_out.end(),-1);host_prediction_entries=select_ns=pending_wait_ns=0;}
 void observe(int layer,int tokens,const int32_t*actual,const int32_t*resident){
  if(!enabled||!active)return;
  if(layer<0||layer>=48||tokens<1||tokens>4)throw std::runtime_error("persistent: dispatch geometry");
  for(int q=0;q<tokens*k;++q){int e=actual[q];if(e<0||e>=512)throw std::runtime_error("persistent: actual expert ID");int at=layer*512+e;last[at]=window;
   int id=by_in[at];if(id>=0&&resident[at]>=0){auto&a=admissions[id];++a.uses;if(!a.first_use)a.first_use=persistent_ns();if(a.last_use!=window){++a.use_windows;a.last_use=window;}}
   id=by_out[at];if(id>=0&&resident[at]<0)++admissions[id].victim_uses;
  }
  // The native dispatch's existing ring fence makes the mapped top10 visible here.
  for(size_t i=0;i<origins.size();++i)if(origins[i]==layer&&pairs[i].valid){int dev=pairs[i].device;const auto*in=host_ids[dev]+i*max_tokens*k;const auto*w=host_weights[dev]+i*max_tokens*k;
   for(int q=0;q<tokens*k;++q){if(in[q]<0||in[q]>=512||!std::isfinite(w[q])||w[q]<0||w[q]>1)throw std::runtime_error("persistent: prediction ID/confidence");prediction[targets[i]*512+in[q]]+=w[q]*10.f;++host_prediction_entries;}
  }
 }
 void decay(float factor){if(enabled)for(float&x:prediction)x*=factor;}
 void issue(int layer,int in,int out_layer,int out,int slot,uint64_t bytes){if(!enabled)return;int a=layer*512+in,b=out_layer*512+out;
  if(by_in[b]>=0)admissions[by_in[b]].evicted=persistent_ns();
  const int id=(int)admissions.size();Admission row{};row.issue=persistent_ns();row.bytes=bytes;row.layer=layer;row.in=in;row.out_layer=out_layer;row.out=out;row.slot=slot;admissions.push_back(row);by_in[a]=id;by_out[b]=id;born[a]=window;
 }
 void publish(int at,int slot){if(!enabled)return;int id=by_in[at];if(id<0||admissions[id].slot!=slot||admissions[id].published)throw std::runtime_error("persistent: publication identity");admissions[id].published=persistent_ns();}
 bool validate(const std::vector<int32_t>&res,const std::vector<uint64_t>&blob,const std::vector<uint64_t>&s0,const std::vector<uint64_t>&s1){
  if(!enabled)return true;for(int gpu=0;gpu<2;++gpu){const auto&sizes=gpu?s1:s0;std::vector<uint8_t>used(sizes.size(),0);for(int l=gpu?25:0;l<(gpu?48:25);++l)for(int e=0;e<512;++e){int slot=res[l*512+e];if(slot<0)continue;if((size_t)slot>=sizes.size()||used[slot]||blob[l]>sizes[slot])return false;used[slot]=1;}}return true;
 }
 void finish(){if(!enabled)return;active=false;uint64_t bytes=0,useful=0,wasted=0,repeat=0,victim=0,ready=0,late=0,unpublished=0,used=0;
  for(const auto&a:admissions){bytes+=a.bytes;victim+=a.victim_uses;used+=a.uses;if(a.uses){++useful;if(a.use_windows>1)++repeat;if(a.published&&a.published<=a.first_use)++ready;else++late;}else++wasted;if(!a.published)++unpublished;}
  std::fprintf(stderr,"strata persistent: request=%d promotions=%zu bytes=%llu useful=%llu wasted=%llu repeated=%llu ready=%llu late=%llu unpublished=%llu useful_entries=%llu victim_entries=%llu prediction_entries=%llu selector_ms=%.3f pending_ms=%.3f; safe-boundary persistent, no restore\n",request,admissions.size(),(unsigned long long)bytes,(unsigned long long)useful,(unsigned long long)wasted,(unsigned long long)repeat,(unsigned long long)ready,(unsigned long long)late,(unsigned long long)unpublished,(unsigned long long)used,(unsigned long long)victim,(unsigned long long)host_prediction_entries,select_ns/1e6,pending_wait_ns/1e6);
  // Detail is written only after decode timing, never synchronously per-token.
  const char*prefix=std::getenv("STRATA_LAB_PERSISTENT_LOG");if(prefix){std::string file=std::string(prefix)+"-request"+std::to_string(request)+".csv";FILE*f=std::fopen(file.c_str(),"w");if(!f)throw std::runtime_error("persistent: admission log open");std::fprintf(f,"layer,in,out_layer,out,slot,bytes,issue_ns,published_ns,first_use_ns,evicted_ns,uses,use_windows,victim_entries\n");for(const auto&a:admissions)std::fprintf(f,"%d,%d,%d,%d,%d,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu\n",a.layer,a.in,a.out_layer,a.out,a.slot,(unsigned long long)a.bytes,(unsigned long long)a.issue,(unsigned long long)a.published,(unsigned long long)a.first_use,(unsigned long long)a.evicted,(unsigned long long)a.uses,(unsigned long long)a.use_windows,(unsigned long long)a.victim_uses);std::fclose(f);}
 }
};
inline PersistentRuntime persistent;
}
