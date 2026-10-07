// Reproduce an all-local skip bypassing host PLE readiness; verify the independent fence.
#include <cuda_runtime.h>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <chrono>
namespace strata::kernels {
void wait_flag_ge_or(const uint32_t*,uint32_t,const uint32_t*,void*);
void wait_flag_ge(const uint32_t*,uint32_t,void*);
void copy_from_mapped(float*,const float*,int64_t,void*);
}
void ck(cudaError_t c){if(c!=cudaSuccess){std::fprintf(stderr,"%s\n",cudaGetErrorString(c));std::exit(1);}}
struct State{float ple[4];uint32_t flag;};
int main(){
 for(int device=0;device<2;++device){
  ck(cudaSetDevice(device));State *h,*m;uint32_t*skip;float*out;cudaStream_t s;
  ck(cudaHostAlloc(&h,sizeof(State),cudaHostAllocMapped));ck(cudaHostGetDevicePointer(&m,h,0));
  ck(cudaMalloc(&skip,4));ck(cudaMalloc(&out,16));ck(cudaStreamCreateWithFlags(&s,cudaStreamNonBlocking));
  uint32_t ring=1;ck(cudaMemcpy(skip,&ring,4,cudaMemcpyHostToDevice));
  for(bool repair:{false,true}){
   h->flag=0;for(float&v:h->ple)v=17;
   ck(cudaStreamBeginCapture(s,cudaStreamCaptureModeThreadLocal));
   strata::kernels::wait_flag_ge_or(&m->flag,1,skip,s);
   if(repair)strata::kernels::wait_flag_ge(&m->flag,1,s);
   strata::kernels::copy_from_mapped(out,m->ple,4,s);
   cudaGraph_t g;cudaGraphExec_t ex;ck(cudaStreamEndCapture(s,&g));ck(cudaGraphInstantiate(&ex,g,0));
   ck(cudaGraphLaunch(ex,s));
   std::thread producer([&](){std::this_thread::sleep_for(std::chrono::milliseconds(40));for(float&v:h->ple)v=99;__atomic_store_n(&h->flag,1,__ATOMIC_SEQ_CST);});
   ck(cudaStreamSynchronize(s));float actual[4];ck(cudaMemcpy(actual,out,16,cudaMemcpyDeviceToHost));producer.join();
   for(float v:actual)assert(v==(repair?99:17));
   ck(cudaGraphExecDestroy(ex));ck(cudaGraphDestroy(g));
  }
  ck(cudaStreamDestroy(s));ck(cudaFree(skip));ck(cudaFree(out));ck(cudaFreeHost(h));
 }
 std::puts("PASS: all-local skip reads stale host PLE; independent producer fence reads fresh PLE on both GPUs");
}
