// Real CUDA transfers in all three physical Q4 byte classes, no model-quality claim.
#include "strata/research/q4_oracle.hpp"
#include <iostream>
#include <map>
#include <memory>
using namespace strata::research;
static void ok(bool x,const char* why){Q4Tape::require(x,why);}
static void ready(Q4Oracle::Worker& w){std::unique_lock<std::mutex> l(w.mu);ok(w.cv.wait_for(l,std::chrono::seconds(5),[&]{return w.state.load()==3||w.state.load()==7;}),"test copy timeout");ok(w.state.load()==3,"test worker failed");}
int main(){
 setenv("STRATA_Q4_ORACLE_SUBSTRATE","1",1);setenv("STRATA_Q4_ORACLE_MODE","full",1);setenv("STRATA_Q4_ORACLE_CHECK","1",1);
 q4_tape.enabled=false;q4_tape.active=true;q4_tape.replaying=true;q4_tape.header.output_budget=64;q4_tape.windows.resize(8);
 for(int wi=0;wi<8;++wi){auto& w=q4_tape.windows[wi];w.T=1;for(int l=0;l<48;++l)for(int j=0;j<10;++j){w.routes.ids[l][j]=0;w.routes.weights[l][j]=.1f;}}
 q4_tape.current=q4_tape.windows[0];q4_tape.index=0;
 std::vector<uint64_t>b(48,3072000);b[2]=3993600;for(int l:{4,30,46,47})b[l]=3584000;
 auto backing=std::make_shared<std::map<std::pair<int,int>,std::vector<uint8_t>>>();
 auto source=[backing,b](int l,int e)->const uint8_t*{auto key=std::make_pair(l,e);auto it=backing->find(key);if(it==backing->end()){std::vector<uint8_t> v(b[l]);for(size_t j=0;j<v.size();++j)v[j]=(uint8_t)((j*17+e*3+l*11)&255);it=backing->emplace(key,std::move(v)).first;}return it->second.data();};
 std::array<uint8_t*,2> gpu{};std::array<int32_t*,2> dr{};std::array<std::vector<uint64_t>,2> offsets;std::vector<int32_t> r(48*512,-1);std::vector<float> heat(48*512,0);
 for(int d=0;d<2;++d){cudaSetDevice(d);offsets[d].push_back(0);std::vector<int>ls=d?std::vector<int>{24,30}:std::vector<int>{0,4,2};int s=0;for(int l:ls)for(int e:{1,2}){r[l*512+e]=s++;offsets[d].push_back(offsets[d].back()+b[l]);}ok(cudaMalloc(&gpu[d],offsets[d].back())==cudaSuccess,"fixture cache alloc");ok(cudaMalloc(&dr[d],r.size()*4)==cudaSuccess,"metadata alloc");for(int l:ls)for(int e:{1,2})ok(cudaMemcpy(gpu[d]+offsets[d][r[l*512+e]],source(l,e),b[l],cudaMemcpyHostToDevice)==cudaSuccess,"initial fill");}
 auto ptr=[&](int d,int s)->void*{return gpu[d]+offsets[d][s];};
 {Q4Oracle o;o.configure();o.runtime(r.data(),heat.data(),b,dr,source,ptr);o.begin();ok(o.active,"fixture active");ok(std::count_if(r.begin(),r.end(),[](int x){return x>=0;})==5,"five charged spares");std::cout<<"PASS physical-five-spare-capacity\n";
  // Copy/publication and exact backing readback in every device/class.
  for(int d=0;d<2;++d)for(int c=0;c<3;++c){if(d==1&&c==2)continue;int l=d?(c==0?24:30):(c==0?0:c==1?4:2);auto& w=o.workers[d][c];o.current=0;o.issue(w,l,3,12);ready(w);ok(r[l*512+3]<0,"not published before completion");o.publish(w);ok(r[l*512+3]>=0,"published expert");std::vector<uint8_t> read(b[l]);cudaSetDevice(d);ok(cudaMemcpy(read.data(),ptr(d,r[l*512+3]),b[l],cudaMemcpyDeviceToHost)==cudaSuccess,"readback");ok(!std::memcmp(read.data(),source(l,3),b[l]),"canonical copied bytes");}
  std::cout<<"PASS all-three-byte-classes-both-devices\n";
  auto& w=o.workers[0][0];o.issue(w,0,4,6);bool refused=false;try{o.issue(w,0,5,8);}catch(const std::exception&){refused=true;}ok(refused,"duplicate inflight issue refused");ready(w);
  // All current residents become protected after enqueue; publication must wait.
  int n=0;for(int e=0;e<512;++e)if(r[e]>=0){for(int j=n;j<10;++j)q4_tape.current.routes.ids[0][j]=e;++n;}
  o.publish(w);ok(w.state.load()==3&&r[4]<0,"protected victim cannot publish");for(int j=0;j<10;++j)q4_tape.current.routes.ids[0][j]=0;++o.current;o.publish(w);ok(r[4]>=0,"protection release at next logical event");std::cout<<"PASS duplicate-inflight-and-victim-protection\n";
  // Safe native/already-resident suppression. Slot identity changes mimic an independent admission.
  o.issue(w,0,5,8);ready(w);int old=r[4];r[4]=-1;r[5]=old;cudaSetDevice(0);cudaMemcpy(ptr(0,old),source(0,5),b[0],cudaMemcpyHostToDevice);o.publish(w);ok(w.state.load()==0&&o.redundant==1,"already resident copy retired");std::cout<<"PASS became-resident-before-publication\n";
  setenv("STRATA_Q4_ORACLE_DELAY_US","25000",1);o.issue(w,0,6,1);o.current=2;o.publish(w);ok(r[6]<0,"late expert remains safely nonlocal");ready(w);o.publish(w);ok(r[6]>=0&&o.events.back().status==3,"late useful persistent publication");unsetenv("STRATA_Q4_ORACLE_DELAY_US");std::cout<<"PASS delayed-copy-safe-fallback\n";
  for(int i=0;i<16;++i){int e=10+i;o.issue(w,0,e,30+i);ready(w);o.publish(w);ok(r[e]>=0,"repeated spare publication");}
  std::cout<<"PASS repeated-spare-reuse\n";
  setenv("STRATA_Q4_ORACLE_DELAY_US","5000",1);o.issue(w,0,100,90);o.finish();unsetenv("STRATA_Q4_ORACLE_DELAY_US");ok(std::count_if(r.begin(),r.end(),[](int x){return x>=0;})==10,"request-end restoration");std::cout<<"PASS cancellation-drain-restoration\n";
  o.begin();o.issue(o.workers[0][0],0,101,5);ready(o.workers[0][0]);o.publish(o.workers[0][0]);o.finish();ok(std::count_if(r.begin(),r.end(),[](int x){return x>=0;})==10,"next request capacity");std::cout<<"PASS next-request-after-cancellation\n";
 }
 // Destruction must join workers before callback/source/device allocation is destroyed.
 {Q4Oracle o;o.configure();o.runtime(r.data(),heat.data(),b,dr,source,ptr);o.begin();setenv("STRATA_Q4_ORACLE_DELAY_US","5000",1);o.issue(o.workers[0][0],0,102,10);}
 unsetenv("STRATA_Q4_ORACLE_DELAY_US");for(int d=0;d<2;++d){cudaSetDevice(d);ok(cudaDeviceSynchronize()==cudaSuccess,"shutdown synchronize");cudaFree(dr[d]);cudaFree(gpu[d]);}std::cout<<"PASS shutdown-with-pending-copy\n";
 q4_tape.active=false;std::cout<<"PASS ALL oracle safety fixture\n";
}
