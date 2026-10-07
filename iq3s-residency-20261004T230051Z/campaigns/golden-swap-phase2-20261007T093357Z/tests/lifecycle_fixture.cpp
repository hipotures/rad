// Real CUDA transfers in all three physical Q4 byte classes, no model-quality claim.
#include "strata/research/q4_oracle.hpp"
#include <iostream>
#include <map>
#include <memory>
using namespace strata::research;
static void ok(bool x,const char* why){Q4Tape::require(x,why);}
static void ready(Q4Oracle::Worker& w){std::unique_lock<std::mutex> l(w.mu);ok(w.cv.wait_for(l,std::chrono::seconds(5),[&]{return w.state.load()==3||w.state.load()==7;}),"test copy timeout");ok(w.state.load()==3,"test worker failed");}
int main(){setenv("STRATA_Q4_TRANSACTION_CONTROL","1",1);setenv("STRATA_Q4_CAUSAL_VICTIM","native",1);
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
  for(int d=0;d<2;++d)for(int c=0;c<3;++c){if(d==1&&c==2)continue;int l=d?(c==0?24:30):(c==0?0:c==1?4:2);auto& w=o.workers[d][c];o.current=0;o.issue(w,l,3,12);ready(w);o.publish(w);ok(r[l*512+3]>=0,"valid class publication");int i=w.index;ok(o.lease_protected(l,3),"new generation protected");ok(o.victim(l,4,0)<0,"all compatible residents protected returns NO_SWAP");
   std::vector<uint8_t> read(b[l]);cudaSetDevice(d);ok(cudaMemcpy(read.data(),ptr(d,r[l*512+3]),b[l],cudaMemcpyDeviceToHost)==cudaSuccess,"sample readback");ok(!std::memcmp(read.data(),source(l,3),b[l]),"canonical RAM identity");
   int32_t ids[10],slots[10];std::fill(ids,ids+10,3);std::fill(slots,slots+10,r[l*512+3]);o.note_service(l,ids,slots,10,12);ok(o.lifetimes[i].distinct_uses==1&&o.lifetimes[i].first_use==12,"multiple lanes one distinct actual use");o.advance_lifetimes(12);ok(o.lease_protected(l,3),"no release before reader milestone");int before=o.victim(l,4,13);ok(before<0,"pre-release cached NO_SWAP");o.advance_lifetimes(13);ok(!o.lease_protected(l,3)&&o.victim(l,4,13)==3,"same-event cache invalidated on protection release");
  }
  std::cout<<"PASS every-device-class-copy-first-use-and-same-event-release\n";
  auto& w=o.workers[0][0];o.current=13;o.issue(w,0,4,15);bool refused=false;try{o.issue(w,0,5,18);}catch(const std::exception&){refused=true;}ok(refused,"duplicate in-flight refused");ready(w);o.publish(w);int g=w.index;ok(o.lifetimes[g].first_use<0,"new repeated generation has no prior use");o.advance_lifetimes(63);ok(o.lease_protected(0,4),"inclusive deadline");o.advance_lifetimes(64);ok(!o.lease_protected(0,4)&&o.lifetimes[g].reason==2,"unused intent safely expires");
  o.current=64;o.issue(w,0,5,12);ready(w);o.publish(w);ok(r[5]<0&&o.events.back().status==8,"late target safe abort no stale publication");
  o.issue(w,0,3,70);ready(w);o.publish(w);ok(o.lifetimes.back().first_use<0&&o.lifetimes.back().generation!=0,"readmitted expert fresh generation");
  int32_t ids[10],slots[10];std::fill(ids,ids+10,3);std::fill(slots,slots+10,r[3]);o.note_service(0,ids,slots,10,70);o.note_service(0,ids,slots,10,118);ok(o.lifetimes.back().distinct_uses==2,"distinct repeated batch service");o.advance_lifetimes(119);
  o.current=119;setenv("STRATA_Q4_ORACLE_DELAY_US","25000",1);o.issue(w,0,6,120);o.publish(w);ok(r[6]<0,"no incomplete publication");ready(w);o.publish(w);unsetenv("STRATA_Q4_ORACLE_DELAY_US");ok(r[6]>=0,"delayed publication within expiry");o.advance_lifetimes(169);
  for(int j=0;j<16;++j){o.current=170+j*2;o.issue(w,0,10+j,171+j*2);ready(w);o.publish(w);o.advance_lifetimes(220+j*2);}
  std::cout<<"PASS generation-expiry-delay-duplicate-and-repeated-spares\n";
  // Simulated ownership/protection change after selection: publication reselects and safely aborts late intent.
  o.current=300;o.issue(w,0,100,305);ready(w);int resident=-1;for(int e=0;e<512;++e)if(r[e]>=0)resident=e;ok(resident>=0,"resident exists");int prior=o.incoming_event[resident];o.leases[resident]=prior;++o.ownership_generation[0];o.publish(w);ok(r[100]<0&&w.state.load()==3,"protected publication waits bounded");o.current=354;o.publish(w);ok(r[100]<0&&w.state.load()==0,"expiry ends protected publication retry");o.leases[resident]=-1;
  o.issue(w,0,101,370);o.finish();ok(std::count_if(r.begin(),r.end(),[](int x){return x>=0;})==10,"drain restoration");o.begin();ok(o.protected_keys.empty(),"next request protection reset");o.finish();std::cout<<"PASS publication-recheck-drain-and-next-request\n";

 }
 // Destruction must join workers before callback/source/device allocation is destroyed.
 {Q4Oracle o;o.configure();o.runtime(r.data(),heat.data(),b,dr,source,ptr);o.begin();setenv("STRATA_Q4_ORACLE_DELAY_US","5000",1);o.issue(o.workers[0][0],0,102,10);}
 unsetenv("STRATA_Q4_ORACLE_DELAY_US");for(int d=0;d<2;++d){cudaSetDevice(d);ok(cudaDeviceSynchronize()==cudaSuccess,"shutdown synchronize");cudaFree(dr[d]);cudaFree(gpu[d]);}std::cout<<"PASS shutdown-with-pending-copy\n";
 q4_tape.active=false;std::cout<<"PASS ALL oracle safety fixture\n";
}
