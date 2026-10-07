// Reproduce captured timing events and validate external event nodes on both GPUs.
#include <cuda_runtime.h>
#include <cstdio>
#include <cstdlib>
#include <initializer_list>
void check(cudaError_t e) {if(e!=cudaSuccess){std::fprintf(stderr,"CUDA: %s\n",cudaGetErrorString(e));std::exit(1);}}
int main() {
    for(int d=0;d<2;++d)for(unsigned flag:{cudaEventRecordDefault,cudaEventRecordExternal}) {
        check(cudaSetDevice(d));cudaStream_t stream;check(cudaStreamCreateWithFlags(&stream,cudaStreamNonBlocking));
        cudaEvent_t begin,end;check(cudaEventCreate(&begin));check(cudaEventCreate(&end));
        void* data=nullptr;check(cudaMalloc(&data,1048576));
        check(cudaStreamBeginCapture(stream,cudaStreamCaptureModeThreadLocal));
        check(cudaEventRecordWithFlags(begin,stream,flag));check(cudaMemsetAsync(data,0,1048576,stream));
        check(cudaEventRecordWithFlags(end,stream,flag));cudaGraph_t graph;check(cudaStreamEndCapture(stream,&graph));
        cudaGraphExec_t exec;check(cudaGraphInstantiate(&exec,graph,0));
        for(int rep=0;rep<2;++rep) {
            check(cudaGraphLaunch(exec,stream));check(cudaStreamSynchronize(stream));
            float ms=0;cudaError_t result=cudaEventElapsedTime(&ms,begin,end);
            std::printf("device=%d flag=%u rep=%d elapsed_result=%s ms=%.6f\n",d,flag,rep,cudaGetErrorString(result),ms);
            if(flag==cudaEventRecordExternal && (result!=cudaSuccess || !(ms>0)))return 2;
        }
        check(cudaGraphExecDestroy(exec));check(cudaGraphDestroy(graph));check(cudaEventDestroy(begin));check(cudaEventDestroy(end));
        check(cudaFree(data));check(cudaStreamDestroy(stream));
    }
}
