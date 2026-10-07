// Fixed-work Q4 research tape. OFF unless explicitly enabled; not a serving model.
#pragma once
#include "strata/research/q4_tape_gpu.hpp"
#include <cuda_runtime.h>
#include <array>
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <stdexcept>
#include <vector>
namespace strata::research {
struct TapeWindow {
 int64_t position; int32_t T,accepted,draft_count,emitted_before;
 int32_t inputs[4],outputs[4]; TapeRoutes routes;
};
struct TapeObservation {
 uint64_t begin_ns,end_ns; int32_t seen[51],disagreements[51],native_outputs[4]; float activation[51][8];
};
struct TapeHeader { uint64_t magic=0x3150455441343451ull; uint32_t version=1,window_bytes=sizeof(TapeWindow); uint64_t windows=0,prompt_count=0,output_budget=0,output_count=0,work_hash=0; };
struct Q4Tape {
 bool enabled=false,replaying=false,active=false; int request=0,selected=2; size_t index=0;
 std::string path; TapeHeader header; std::vector<int32_t> prompt,initial_res; std::vector<float> initial_heat;
 std::vector<TapeWindow> windows; std::vector<TapeObservation> observations; TapeWindow current{}; TapeObservation obs{};
 std::array<TapePage*,2> host{},mapped{}; uint64_t lookup_ns=0,main_events=0,mtp_events=0; int output_divergence=-1;
 static uint64_t ns(){return std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}
 static void require(bool ok,const char* why){if(!ok)throw std::runtime_error(std::string("Q4_TAPE_CONTRACT ")+why);}
 Q4Tape(){const char* p=std::getenv("STRATA_Q4_TAPE");if(!p)return;enabled=true;path=p;const char* m=std::getenv("STRATA_Q4_TAPE_MODE");require(m,"mode missing");require(std::string(m)=="record"||std::string(m)=="replay","invalid mode");replaying=std::string(m)=="replay";p=std::getenv("STRATA_Q4_TAPE_REQUEST");if(p)selected=std::atoi(p);if(replaying)load();}
 template<class T> static void io(FILE* f,T* p,size_t n,bool write){require((write?std::fwrite(p,sizeof(T),n,f):std::fread(p,sizeof(T),n,f))==n,"truncated tape IO");}
 void load(){FILE* f=std::fopen(path.c_str(),"rb");require(f,"cannot open replay tape");io(f,&header,1,false);require(header.magic==0x3150455441343451ull&&header.version==1&&header.window_bytes==sizeof(TapeWindow)&&header.windows<100000&&header.prompt_count<300000,"unsupported tape schema");prompt.resize(header.prompt_count);initial_res.resize(48*512);initial_heat.resize(48*512);windows.resize(header.windows);io(f,prompt.data(),prompt.size(),false);io(f,initial_res.data(),initial_res.size(),false);io(f,initial_heat.data(),initial_heat.size(),false);io(f,windows.data(),windows.size(),false);require(std::fgetc(f)==EOF,"trailing tape bytes");std::fclose(f);require(hash()==header.work_hash,"corrupt work hash");}
 void configure(){if(!enabled)return;int old;cudaGetDevice(&old);for(int d=0;d<2;++d){require(cudaSetDevice(d)==cudaSuccess,"device setup");require(cudaHostAlloc(&host[d],sizeof(TapePage),cudaHostAllocMapped)==cudaSuccess,"mapped tape allocation");require(cudaHostGetDevicePointer(&mapped[d],host[d],0)==cudaSuccess,"mapped tape pointer");std::memset(host[d],0,sizeof(TapePage));}cudaSetDevice(old);}
 void graph_main(int d,int l,int off,int n,int32_t* ids,float* weights,const float* x,void* stream){if(enabled)tape_route(mapped[d],l,off,n,ids,weights,x,stream);}
 void graph_mtp(int d,int step,int32_t* ids,float* weights,const float* x,void* stream){if(enabled)tape_route(mapped[d],48+step,0,10,ids,weights,x,stream);}
 void graph_mtp_head(int d,int step,int32_t* out,float* prob,void* stream){if(enabled)tape_mtp_head(mapped[d],step,out,prob,stream);}
 void begin(const std::vector<int64_t>& ids,int64_t budget,const int32_t* res,const float* heat){if(!enabled)return;++request;if(request!=selected)return;require(host[0]&&host[1],"configure missing");active=true;index=0;lookup_ns=main_events=mtp_events=0;observations.clear();observations.reserve((size_t)budget);output_divergence=-1;
  if(replaying){require(ids.size()==prompt.size()&&budget==(int64_t)header.output_budget,"request shape differs");for(size_t i=0;i<ids.size();++i)require(ids[i]==prompt[i],"input token differs");if(std::memcmp(res,initial_res.data(),48*512*sizeof(int32_t))){int n=0;for(int j=0;j<48*512;++j)n+=res[j]!=initial_res[j];std::fprintf(stderr,"Q4_TAPE_INITIAL_RES_MISMATCH count=%d\n",n);require(false,"initial resident sets/slots differ");}require(!std::memcmp(heat,initial_heat.data(),48*512*sizeof(float)),"initial native usage differs");}
  else{header.output_budget=budget;header.prompt_count=ids.size();prompt.assign(ids.begin(),ids.end());initial_res.assign(res,res+48*512);initial_heat.assign(heat,heat+48*512);windows.clear();windows.reserve((size_t)budget);}
  std::fprintf(stderr,"Q4_TAPE_BEGIN mode=%s input=%zu budget=%lld initial_residents=%zu ram_tape_bytes=%zu\n",replaying?"replay":"record",ids.size(),(long long)budget,(size_t)std::count_if(initial_res.begin(),initial_res.end(),[](int x){return x>=0;}),windows.size()*sizeof(TapeWindow));}
 void pre(int& T,int64_t p,int32_t* inputs,int emitted){if(!active)return;uint64_t t=ns();std::memset(&current,0,sizeof(current));std::memset(&obs,0,sizeof(obs));if(replaying){require(index<windows.size(),"extra window");current=windows[index];require(current.position==p&&current.T==T&&current.emitted_before==emitted,"window schedule differs");require(!std::memcmp(current.inputs,inputs,T*sizeof(int32_t)),"window input differs");}else{current.position=p;current.T=T;current.emitted_before=emitted;std::memcpy(current.inputs,inputs,T*sizeof(int32_t));}
  for(int d=0;d<2;++d){std::memset(host[d],0,sizeof(TapePage));if(replaying)host[d]->routes=current.routes;host[d]->mode=replaying?2:1;}lookup_ns+=ns()-t;obs.begin_ns=ns();}
 void head(int T,int32_t* outputs){if(!active)return;std::memcpy(obs.native_outputs,outputs,T*sizeof(int32_t));if(replaying){if(output_divergence<0&&std::memcmp(current.outputs,outputs,T*sizeof(int32_t)))output_divergence=(int)index;std::memcpy(outputs,current.outputs,T*sizeof(int32_t));}else std::memcpy(current.outputs,outputs,T*sizeof(int32_t));}
 void accepted(int a){if(!active)return;if(replaying)require(current.accepted==a,"commit prefix differs");else current.accepted=a;}
 void drafted(int n){if(!active)return;if(replaying)require(current.draft_count==n,"draft invocation count differs");else current.draft_count=n;}
 void post(){if(!active)return;uint64_t t=ns();int nonfinite=0;for(int l=0;l<51;++l){int d=l<24?0:1;auto* p=host[d];obs.seen[l]=p->seen[l];obs.disagreements[l]=p->disagreements[l];std::memcpy(obs.activation[l],p->activation[l],sizeof(obs.activation[l]));require(p->seen[l]==(l<48?1:(l-48<current.draft_count?1:0)),"route call count differs");if(l<48){if(!replaying){std::memcpy(current.routes.ids[l],p->routes.ids[l],40*4);std::memcpy(current.routes.weights[l],p->routes.weights[l],40*4);}++main_events;}else{int j=l-48;if(!replaying){std::memcpy(current.routes.mtp_ids[j],p->routes.mtp_ids[j],10*4);std::memcpy(current.routes.mtp_weights[j],p->routes.mtp_weights[j],10*4);current.routes.drafts[j]=p->routes.drafts[j];current.routes.probs[j]=p->routes.probs[j];}mtp_events+=p->seen[l];}nonfinite|=p->nonfinite;}require(!nonfinite,"nonfinite route/activation");obs.end_ns=ns();observations.push_back(obs);if(!replaying)windows.push_back(current);++index;lookup_ns+=ns()-t;for(auto* p:host)p->mode=0;}
 uint64_t hash()const{uint64_t x=1469598103934665603ull;auto add=[&](const void* p,size_t n){auto* b=(const uint8_t*)p;for(size_t i=0;i<n;++i){x^=b[i];x*=1099511628211ull;}};add(prompt.data(),prompt.size()*4);add(&header.output_budget,8);for(const auto& w:windows)add(&w,sizeof(w));return x;}
 void finish(int64_t output_count,bool cancelled){if(!active)return;require(!cancelled,"cancelled tape is invalid");if(replaying)require(index==windows.size()&&output_count==(int64_t)header.output_count,"incomplete replay");else{header.windows=windows.size();header.output_count=output_count;header.work_hash=hash();FILE* f=std::fopen(path.c_str(),"wbx");require(f,"record tape path already exists");io(f,&header,1,true);io(f,prompt.data(),prompt.size(),true);io(f,initial_res.data(),initial_res.size(),true);io(f,initial_heat.data(),initial_heat.size(),true);io(f,windows.data(),windows.size(),true);std::fclose(f);}
  const char* p=std::getenv("STRATA_Q4_TAPE_OBSERVATIONS");if(p){FILE* f=std::fopen(p,"wbx");require(f,"observation path already exists");io(f,observations.data(),observations.size(),true);std::fclose(f);}std::fprintf(stderr,"Q4_TAPE_END mode=%s windows=%zu main_events=%llu mtp_events=%llu output=%lld work_hash=%016llx lookup_ms=%.3f native_head_first_divergence=%d\n",replaying?"replay":"record",index,(unsigned long long)main_events,(unsigned long long)mtp_events,(long long)output_count,(unsigned long long)header.work_hash,lookup_ns/1e6,output_divergence);active=false;}
 ~Q4Tape(){for(auto* p:host)if(p)cudaFreeHost(p);}
};inline Q4Tape q4_tape;
}
