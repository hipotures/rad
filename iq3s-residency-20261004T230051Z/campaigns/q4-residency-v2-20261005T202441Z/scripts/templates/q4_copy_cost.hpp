// Default-off, buffered copy costs; no per-layer synchronization or weight change.
#pragma once
#include "strata/research/lab_trace.hpp"
#include <cuda_runtime.h>
#include <array>
#include <stdexcept>
namespace strata::research {
struct Q4CopyRecord {
 uint64_t window, enqueue_begin, enqueue_end, bytes;
 int32_t layer,in,out,slot,device,event_index;
 float gpu_ms;int32_t observed_complete;
};
static_assert(sizeof(Q4CopyRecord)==64);
struct Q4CopyCost {
 bool enabled=false;static constexpr int cap=256;
 std::array<std::array<std::array<cudaEvent_t,2>,cap>,2>events{};
 std::array<int,2>used{},counter{};std::array<bool,2>configured{};
 std::vector<Q4CopyRecord>records;
 Q4CopyCost(){const char*p=std::getenv("STRATA_Q4_COPY_COST");enabled=p&&p[0]=='1'&&trace.enabled;}
 bool configure(int device,std::string&err){
  if(!enabled||configured[device])return true;
  if(device<0||device>1){err="Q4 copy cost device";return false;}
  for(auto&pair:events[device])for(auto&e:pair)if(cudaEventCreate(&e)!=cudaSuccess){err="Q4 copy event allocation";return false;}
  configured[device]=true;return true;
 }
 void begin(){if(!enabled)return;used={};counter={};records.clear();records.reserve(20000);}
 int start(int device,int layer,int in,int out,int slot,uint64_t bytes,cudaStream_t stream){
  if(!enabled||!trace.active)return -1;
  int event=-1;
  if(counter[device]++%32==0&&used[device]<cap){event=used[device]++;if(cudaEventRecord(events[device][event][0],stream)!=cudaSuccess)throw std::runtime_error("Q4 copy begin event");}
  records.push_back({trace.window,ns(),0,bytes,layer,in,out,slot,device,event,-1.f,0});return (int)records.size()-1;
 }
 void end(int index,cudaStream_t stream){
  if(index<0)return;auto&r=records[index];r.enqueue_end=ns();
  if(r.event_index>=0&&cudaEventRecord(events[r.device][r.event_index][1],stream)!=cudaSuccess)throw std::runtime_error("Q4 copy end event");
 }
 void flush(){
  if(!enabled)return;
  int original=-1;cudaGetDevice(&original);
  for(auto&r:records)if(r.event_index>=0){
   cudaSetDevice(r.device);auto&pair=events[r.device][r.event_index];
   const auto status=cudaEventQuery(pair[1]);
   if(status==cudaSuccess){if(cudaEventElapsedTime(&r.gpu_ms,pair[0],pair[1])!=cudaSuccess)throw std::runtime_error("Q4 copy elapsed");r.observed_complete=1;}
   else if(status!=cudaErrorNotReady)throw std::runtime_error("Q4 copy completion error");
  }
  cudaSetDevice(original);trace.file(trace.prefix+"-request"+std::to_string(trace.request)+"-copy-cost.bin",records);
 }
};
inline Q4CopyCost q4_copy_cost;
}
