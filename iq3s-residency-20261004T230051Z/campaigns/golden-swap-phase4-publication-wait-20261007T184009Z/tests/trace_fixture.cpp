#include "strata/kernels/verify_kernels.hpp"
#include <cuda_runtime.h>
#include <thread>
#include <chrono>
#include <iostream>
using namespace strata::kernels;
static void ok(bool v){if(!v)throw std::runtime_error("trace fixture failed");}
int main(){for(int d=0;d<2;++d){cudaSetDevice(d);uint32_t *h,*m;unsigned long long *stats,*data,*count;cudaStream_t stream;cudaHostAlloc(&h,4,cudaHostAllocMapped);cudaHostGetDevicePointer(&m,h,0);cudaMalloc(&stats,16);cudaMalloc(&data,2*32);cudaMalloc(&count,8);cudaStreamCreateWithFlags(&stream,cudaStreamNonBlocking);cudaMemset(stats,0,16);cudaMemset(count,0,8);*h=0;
 std::thread release([&]{std::this_thread::sleep_for(std::chrono::milliseconds(20));*(volatile uint32_t*)h=1;});wait_flag_ge_timed(m,1,stats,stream,data,count,2);cudaStreamSynchronize(stream);release.join();unsigned long long r[8],n;cudaMemcpy(r,data,64,cudaMemcpyDeviceToHost);cudaMemcpy(&n,count,8,cudaMemcpyDeviceToHost);ok(n==1&&r[2]==1&&r[3]==0&&r[1]>r[0]+1000000);
 cudaGraph_t g;cudaGraphExec_t ex;cudaStreamBeginCapture(stream,cudaStreamCaptureModeGlobal);wait_flag_ge_timed(m,1,stats,stream,data,count,2);cudaStreamEndCapture(stream,&g);cudaGraphInstantiate(&ex,g,0);cudaGraphLaunch(ex,stream);cudaGraphLaunch(ex,stream);cudaStreamSynchronize(stream);cudaMemcpy(r,data,64,cudaMemcpyDeviceToHost);cudaMemcpy(&n,count,8,cudaMemcpyDeviceToHost);ok(n==3&&r[6]==1&&r[7]==1&&r[4]>=r[1]);
 cudaMemset(count,0,8);q4_trace_mark(data,count,2,24,stream);cudaStreamSynchronize(stream);cudaMemcpy(r,data,32,cudaMemcpyDeviceToHost);cudaMemcpy(&n,count,8,cudaMemcpyDeviceToHost);ok(n==1&&r[0]==r[1]&&r[2]==24&&r[3]==0);
 cudaGraphExecDestroy(ex);cudaGraphDestroy(g);cudaStreamDestroy(stream);cudaFree(stats);cudaFree(data);cudaFree(count);cudaFreeHost(h);std::cout<<"PASS device="<<d<<" delayed-ready graph-repeat bounded-overflow reset mark\n";}}
