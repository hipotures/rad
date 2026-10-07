// Exercise GPU-owned and CPU-owned rows in the actual captured preserving-copy kernel.
#include <strata/kernels/elementwise.hpp>
#include <cuda_runtime.h>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
static void check(cudaError_t x) {
    if(x!=cudaSuccess) {std::fprintf(stderr,"CUDA: %s\n",cudaGetErrorString(x));std::exit(1);}
}
int main() {
    int devices=0;check(cudaGetDeviceCount(&devices));if(devices<2)return 1;
    int cases=0;
    constexpr int width=2560, k=10;
    for(int device=0;device<2;++device) {
        check(cudaSetDevice(device));cudaStream_t stream;check(cudaStreamCreate(&stream));
        for(int tokens: {1,4}) for(int groups: {1,2}) {
            if(groups>tokens)continue;
            int rows=tokens*k;size_t bytes=size_t(rows)*width*sizeof(float);
            float *src=nullptr,*dst=nullptr;
            int32_t *ids=nullptr,*counts=nullptr;
            check(cudaHostAlloc(&src,bytes,cudaHostAllocMapped|cudaHostAllocPortable));
            check(cudaMalloc(&dst,bytes));check(cudaMalloc(&ids,rows*sizeof(int32_t)));
            check(cudaMalloc(&counts,groups*sizeof(int32_t)));
            for(int mode=0;mode<3;++mode) {
                std::vector<int32_t> hit_rows(rows,-1),hit_count(groups,0);
                std::vector<float> initial(rows*width),expected(rows*width),actual(rows*width);
                for(int group=0;group<groups;++group) {
                    int first=group==0?0:(tokens+1)/2;
                    int last=groups==1?tokens:(group==0?(tokens+1)/2:tokens);
                    int base=first*k,n=(last-first)*k;
                    for(int row=0;row<n;++row) {
                        bool gpu=mode==0 || (mode==2 && row%3!=1);
                        if(gpu)hit_rows[base+hit_count[group]++]=row;
                        for(int c=0;c<width;++c)initial[size_t(base+row)*width+c]=float(1+base+row+c%11);
                    }
                }
                check(cudaMemcpyAsync(ids,hit_rows.data(),rows*sizeof(int32_t),cudaMemcpyHostToDevice,stream));
                check(cudaMemcpyAsync(counts,hit_count.data(),groups*sizeof(int32_t),cudaMemcpyHostToDevice,stream));
                check(cudaStreamSynchronize(stream));
                check(cudaStreamBeginCapture(stream,cudaStreamCaptureModeThreadLocal));
                for(int group=0;group<groups;++group) {
                    int first=group==0?0:(tokens+1)/2;
                    int last=groups==1?tokens:(group==0?(tokens+1)/2:tokens);
                    int base=first*k,n=(last-first)*k;
                    strata::kernels::copy_cpu_rows_preserving_gpu(dst+size_t(base)*width,
                        src+size_t(base)*width,n,width,ids+base,counts+group,stream);
                }
                cudaGraph_t graph;check(cudaStreamEndCapture(stream,&graph));
                cudaGraphExec_t exec;check(cudaGraphInstantiate(&exec,graph,nullptr,nullptr,0));
                for(int replay=0;replay<2;++replay) {
                    for(int row=0;row<rows;++row) for(int c=0;c<width;++c)
                        src[size_t(row)*width+c]=-float(1+row+c%7+replay);
                    expected=initial;
                    for(int group=0;group<groups;++group) {
                        int first=group==0?0:(tokens+1)/2;
                        int last=groups==1?tokens:(group==0?(tokens+1)/2:tokens);
                        int base=first*k,n=(last-first)*k;
                        for(int row=0;row<n;++row) {
                            bool gpu=std::find(hit_rows.begin()+base,hit_rows.begin()+base+hit_count[group],row)
                                      !=hit_rows.begin()+base+hit_count[group];
                            if(!gpu)std::copy_n(src+size_t(base+row)*width,width,expected.begin()+size_t(base+row)*width);
                        }
                    }
                    check(cudaMemcpyAsync(dst,initial.data(),bytes,cudaMemcpyHostToDevice,stream));
                    check(cudaGraphLaunch(exec,stream));check(cudaStreamSynchronize(stream));
                    check(cudaMemcpy(actual.data(),dst,bytes,cudaMemcpyDeviceToHost));
                    if(std::memcmp(actual.data(),expected.data(),bytes)) {
                        std::fprintf(stderr,"Ownership failed device%d T%d G%d mode%d replay%d\n",device,tokens,groups,mode,replay);return 1;
                    }
                    ++cases;
                }
                check(cudaGraphExecDestroy(exec));check(cudaGraphDestroy(graph));
            }
            check(cudaFreeHost(src));check(cudaFree(dst));check(cudaFree(ids));check(cudaFree(counts));
        }
        check(cudaStreamDestroy(stream));
    }
    std::printf("PASS: %d exact row-ownership captured replays, both GPUs, T1/T4, G1/G2\n",cases);
    return 0;
}
