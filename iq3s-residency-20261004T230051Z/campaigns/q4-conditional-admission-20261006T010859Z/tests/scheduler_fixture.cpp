// Actual Q4EarlyPolicy methods/copy workers, tiny deterministic immutable arena.
// This tests scheduling/bytes, not model logits. Native mathematical tests separate.
#include "strata/research/q4_early_policy.hpp"
#include <memory>
#include <set>
#include <iostream>
using Policy=strata::research::Q4EarlyPolicy;
constexpr size_t blob_bytes=3072000;
struct Fixture {
 std::vector<int32_t> res=std::vector<int32_t>(48*512,-1);
 std::vector<float> heat=std::vector<float>(48*512,0);
 std::vector<uint8_t> arena=std::vector<uint8_t>(8*blob_bytes);
 std::array<uint8_t*,2> slots{};std::array<int32_t*,2> dres{};
 std::unique_ptr<Policy> p;
 Fixture(bool conditional=false,bool reject=false){
  setenv("STRATA_Q4_EARLY","1",1);setenv("STRATA_Q4_CONDITIONAL",conditional?"1":"0",1);setenv("STRATA_Q4_CONDITIONAL_REJECT_ALL",reject?"1":"0",1);setenv("STRATA_Q4_EARLY_DIAGNOSTIC","1",1);unsetenv("STRATA_Q4_EARLY_DELAY_US");unsetenv("STRATA_Q4_EARLY_LOG");
  p=std::make_unique<Policy>();
  for(int e=0;e<8;++e)std::fill(arena.begin()+e*blob_bytes,arena.begin()+(e+1)*blob_bytes,uint8_t(17+e*23));
  for(int dev=0;dev<2;++dev){Policy::check(cudaSetDevice(dev));Policy::check(cudaMalloc(&slots[dev],4*blob_bytes));Policy::check(cudaMalloc(&dres[dev],48*512*sizeof(int32_t)));
   int base=dev?24:0,target=dev?29:9;res[base*512]=0;for(int e=0;e<3;++e)res[target*512+e]=e+1;
   auto& w=p->workers[dev];Policy::check(cudaHostAlloc(&w.staging,3993600,cudaHostAllocDefault));Policy::check(cudaHostAlloc(&w.metadata,8,cudaHostAllocDefault));Policy::check(cudaStreamCreateWithFlags(&w.stream,cudaStreamNonBlocking));Policy::check(cudaEventCreateWithFlags(&w.done,cudaEventDisableTiming));
   Policy::check(cudaHostAlloc(&p->pred_ids[dev],200*sizeof(int32_t),cudaHostAllocMapped));Policy::check(cudaHostAlloc(&p->pred_weights[dev],200*sizeof(float),cudaHostAllocMapped));Policy::check(cudaHostAlloc(&p->seq[dev],64,cudaHostAllocMapped));std::fill(p->pred_ids[dev],p->pred_ids[dev]+200,7);std::fill(p->pred_weights[dev],p->pred_weights[dev]+200,.1f);p->configured[dev]=true;w.thread=std::thread([&,dev]{p->worker_loop(dev);});
  }
  p->runtime(res.data(),heat.data(),std::vector<uint64_t>(48,blob_bytes),dres,[&](int,int e){return arena.data()+(e%8)*blob_bytes;},[&](int dev,int slot)->void*{return slots[dev]+slot*blob_bytes;});
  p->begin_request();for(int dev=0;dev<2;++dev){Policy::check(cudaSetDevice(dev));Policy::check(cudaMemcpy(dres[dev],res.data(),res.size()*4,cudaMemcpyHostToDevice));}p->begin_window();
 }
 void enqueue(int e=7){p->proposed_experts[0]=e;p->enqueue(0,9,e);}
 void ready(){auto t=std::chrono::steady_clock::now();while(p->workers[0].state.load()!=3){if(std::chrono::steady_clock::now()-t>std::chrono::seconds(2))throw std::runtime_error("fixture ready timeout");std::this_thread::sleep_for(std::chrono::microseconds(50));}}
 void target(std::initializer_list<int32_t> ids){p->host(res.data(),9,ids.begin(),ids.size());}
 void check_bytes(int e){std::vector<uint8_t> actual(blob_bytes);Policy::check(cudaSetDevice(0));Policy::check(cudaMemcpy(actual.data(),slots[0]+res[9*512+e]*blob_bytes,blob_bytes,cudaMemcpyDeviceToHost));if(std::memcmp(actual.data(),arena.data()+(e%8)*blob_bytes,blob_bytes))throw std::runtime_error("fixture byte mismatch");int32_t slot;Policy::check(cudaMemcpy(&slot,dres[0]+9*512+e,4,cudaMemcpyDeviceToHost));if(slot!=res[9*512+e])throw std::runtime_error("metadata mismatch");}
 void unique(){for(int dev=0;dev<2;++dev){std::set<int> seen;for(int l=dev*24;l<(dev+1)*24;++l)for(int e=0;e<512;++e)if(res[l*512+e]>=0&&!seen.insert(res[l*512+e]).second)throw std::runtime_error("duplicate physical slot ownership");}}
 void finish(){p->end_window(false);p->finish();unique();for(int dev=0;dev<2;++dev){int count=0;for(int l=dev*24;l<(dev+1)*24;++l)for(int e=0;e<512;++e)count+=res[l*512+e]>=0;if(count!=4)throw std::runtime_error("request-end capacity not restored");}}
 ~Fixture(){p.reset();for(int dev=0;dev<2;++dev){cudaSetDevice(dev);cudaFree(slots[dev]);cudaFree(dres[dev]);}}
};
int main(){try{
 {Fixture f;f.enqueue();f.ready();f.target({7,1,2});if(f.p->ready_admits!=1)throw std::runtime_error("good prediction not published");f.check_bytes(7);f.finish();std::cout<<"PASS forced-good/bytecheck/persistent/restoration\n";}
 {Fixture f;f.enqueue();f.ready();f.target({0,1,2});if(f.p->ready_admits||f.p->wrong!=1)throw std::runtime_error("bad prediction published");f.finish();std::cout<<"PASS forced-bad\n";}
 {Fixture f(true,true);int32_t ids[10]={};f.p->host(f.res.data(),5,ids,10);if(!f.p->rejected_before_copy||f.p->issued||f.p->traffic||f.p->workers[0].state.load())throw std::runtime_error("rejection touched staging/copy");f.target({7,1,2});f.p->end_window(false);if(!f.p->previous_wrong[0][9*512+7]&&f.p->window_wrong[9*512+7])throw std::runtime_error("rejected outcome history");f.p->finish();f.unique();std::cout<<"PASS reject-before-enqueue/no-staging/observe-rejected-target\n";}
 {Fixture f;f.enqueue();int32_t ids[10]={};f.p->host(f.res.data(),5,ids,10);if(f.p->issued!=1||!f.p->busy)throw std::runtime_error("duplicate/inflight admitted");f.ready();f.target({7,1,2});f.finish();std::cout<<"PASS duplicate/inflight\n";}
 {Fixture f;f.enqueue();f.ready();f.res[9*512]= -1;f.res[9*512+7]=1;f.target({7,1,2});if(f.p->ready_admits||f.p->wrong!=1)throw std::runtime_error("native-resident guard failed");f.finish();std::cout<<"PASS became-resident-before-publication\n";}
 {Fixture f;f.enqueue();f.ready();f.target({7,0,1});if(f.res[9*512]<0||f.res[9*512+1]<0||f.res[9*512+2]>=0)throw std::runtime_error("protected victim evicted");f.check_bytes(7);f.finish();std::cout<<"PASS victim-became-protected\n";}
 {Fixture f;setenv("STRATA_Q4_EARLY_DELAY_US","50000",1);f.enqueue();f.target({7,1,2});if(!f.p->late||f.p->ready_admits)throw std::runtime_error("delayed copy published before ready");f.finish();std::cout<<"PASS late/delayed-copy\n";}
 {Fixture f;f.enqueue();f.p->finish();f.unique();f.p->begin_request();f.p->begin_window();f.enqueue(6);f.ready();f.target({6,1,2});f.check_bytes(6);f.finish();std::cout<<"PASS pending-cancellation/next-request\n";}
 {Fixture f;f.enqueue();f.ready();f.target({7,1,2});f.p->end_window(false);if(f.res[9*512+7]<0)throw std::runtime_error("immediate swap/restore");f.p->begin_window();f.enqueue(6);f.ready();f.target({6,1,2});f.check_bytes(6);f.finish();std::cout<<"PASS repeated-spare-reuse\n";}
 {Fixture f;setenv("STRATA_Q4_EARLY_DELAY_US","50000",1);f.enqueue();}
 std::cout<<"PASS shutdown-with-pending\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<"\n";return 1;}}
