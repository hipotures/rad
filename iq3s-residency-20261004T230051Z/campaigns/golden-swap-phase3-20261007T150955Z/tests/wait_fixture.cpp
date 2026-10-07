#include "strata/kernels/verify_kernels.hpp"
#include <cuda_runtime.h>
#include <thread>
#include <chrono>
#include <iostream>
using namespace strata::kernels;
int main(){for(int d=0;d<2;++d){cudaSetDevice(d);uint32_t* h=nullptr;uint32_t* m=nullptr;unsigned long long* stats=nullptr;cudaStream_t s;cudaHostAlloc(&h,4,cudaHostAllocMapped);cudaHostGetDevicePointer(&m,h,0);cudaMalloc(&stats,16);cudaMemset(stats,0,16);cudaStreamCreate(&s);*h=0;
 std::thread release([&]{std::this_thread::sleep_for(std::chrono::milliseconds(20));*(volatile uint32_t*)h=1;});
 wait_flag_ge_timed(m,1,stats,s);cudaStreamSynchronize(s);release.join();unsigned long long a[2];cudaMemcpy(a,stats,16,cudaMemcpyDeviceToHost);if(a[1]!=1||a[0]<1000000||a[0]>200000000)return 2;
 wait_flag_ge_timed(m,1,stats,s);cudaStreamSynchronize(s);unsigned long long b[2];cudaMemcpy(b,stats,16,cudaMemcpyDeviceToHost);if(b[1]!=2||b[0]<a[0]||b[0]-a[0]>1000000)return 3;
 std::cout<<"PASS device="<<d<<" blocked_ns="<<a[0]<<" ready_floor_ns="<<b[0]-a[0]<<"\n";cudaStreamDestroy(s);cudaFree(stats);cudaFreeHost(h);}}
