// Minimal ordering proof: a GPU graph awaits its host planner while a distinct
// worker stages immutable bytes and publishes residency on a nonblocking stream.
// The planner never invokes CUDA while the graph is awaiting its flag.
#include <cuda_runtime.h>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <thread>
#include <vector>
#include <stdexcept>
#define CK(x) do {auto e=(x);if(e!=cudaSuccess)throw std::runtime_error(cudaGetErrorString(e));}while(0)
__global__ void consume(volatile unsigned* flag,const unsigned char* slot,const int* residency,unsigned* result,int count){
    auto begin=clock64();while(*flag==0){if(clock64()-begin>6000000000ull){*result=0xdeadbeef;return;}}
    __threadfence_system();unsigned v=0;for(int i=0;i<count;i+=4096)v=v*33+slot[i];
    *result=v ^ unsigned(residency[0]) ^ (unsigned(residency[1])<<16);
}
int main(){
 try{
  for(int device=0;device<2;++device){
   CK(cudaSetDevice(device));cudaStream_t graph_stream,copy_stream;CK(cudaStreamCreateWithFlags(&graph_stream,cudaStreamNonBlocking));CK(cudaStreamCreateWithFlags(&copy_stream,cudaStreamNonBlocking));
   unsigned *flag,*mapped_flag,*result;unsigned char *slot,*staging;int* residency;cudaEvent_t done;
   constexpr int N=3993600;CK(cudaHostAlloc(&flag,64,cudaHostAllocMapped));CK(cudaHostGetDevicePointer(&mapped_flag,flag,0));CK(cudaMalloc(&slot,N));CK(cudaHostAlloc(&staging,N,cudaHostAllocDefault));CK(cudaMalloc(&result,sizeof(unsigned)));CK(cudaMalloc(&residency,2*sizeof(int)));CK(cudaEventCreateWithFlags(&done,cudaEventDisableTiming));
   *flag=0;CK(cudaStreamBeginCapture(graph_stream,cudaStreamCaptureModeThreadLocal));consume<<<1,1,0,graph_stream>>>(mapped_flag,slot,residency,result,N);cudaGraph_t graph;CK(cudaStreamEndCapture(graph_stream,&graph));cudaGraphExec_t exec;CK(cudaGraphInstantiate(&exec,graph,0));CK(cudaGraphDestroy(graph));
   std::vector<unsigned char> immutable(N);unsigned expected=0;int meta[2]={-1,17};
   for(int iter=0;iter<200;++iter){
    for(int j=0;j<N;++j)immutable[j]=(unsigned char)((j*17+iter)%251);
    expected=0;for(int j=0;j<N;j+=4096)expected=expected*33+immutable[j];expected^=unsigned(meta[0]) ^ (unsigned(meta[1])<<16);
    *flag=0;CK(cudaGraphLaunch(exec,graph_stream));std::atomic<bool> ready{false};std::exception_ptr error;
    auto cycle_begin=std::chrono::steady_clock::now();
    std::thread planner([&]{
    std::thread worker([&]{try{CK(cudaSetDevice(device));if(iter%7==0)std::this_thread::sleep_for(std::chrono::microseconds(500));std::memcpy(staging,immutable.data(),N);CK(cudaMemcpyAsync(slot,staging,N,cudaMemcpyHostToDevice,copy_stream));CK(cudaMemcpyAsync(residency,meta,sizeof(meta),cudaMemcpyHostToDevice,copy_stream));CK(cudaEventRecord(done,copy_stream));auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(5);while(cudaEventQuery(done)==cudaErrorNotReady){if(std::chrono::steady_clock::now()>deadline)throw std::runtime_error("worker timeout");std::this_thread::yield();}CK(cudaEventQuery(done));ready.store(true,std::memory_order_release);}catch(...){error=std::current_exception();ready.store(true,std::memory_order_release);}});
    auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(6);while(!ready.load(std::memory_order_acquire)){if(std::chrono::steady_clock::now()>deadline){*flag=1;worker.join();error=std::make_exception_ptr(std::runtime_error("planner timeout"));return;}std::this_thread::yield();}
    *flag=1;worker.join();});
    auto sync_error=cudaStreamSynchronize(graph_stream);planner.join();if(error)std::rethrow_exception(error);CK(sync_error);
    auto elapsed=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-cycle_begin).count();if(elapsed>100)throw std::runtime_error("concurrent stream synchronization/copy exceeded100ms");unsigned got;CK(cudaMemcpy(&got,result,sizeof(got),cudaMemcpyDeviceToHost));if(got!=expected)throw std::runtime_error("publication/readback mismatch");
   }
   CK(cudaGraphExecDestroy(exec));CK(cudaEventDestroy(done));CK(cudaFree(slot));CK(cudaFree(result));CK(cudaFree(residency));CK(cudaFreeHost(staging));CK(cudaFreeHost(flag));CK(cudaStreamDestroy(graph_stream));CK(cudaStreamDestroy(copy_stream));std::printf("PASS device%d 200 staged-copy+metadata-before-host-release cycles; delayed producers and concurrent main-thread cudaStreamSynchronize included\n",device);
  }
 }catch(const std::exception& e){std::fprintf(stderr,"FAIL %s\n",e.what());return 1;}
}
