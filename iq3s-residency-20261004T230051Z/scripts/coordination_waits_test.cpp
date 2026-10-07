// Real CUDA graph replay identity/lifecycle check for diagnostic-only events.
#include "strata/research/lab_miss_waits.hpp"
#include <cassert>
#include <iostream>

int main() {
    using namespace strata::research;
    std::string err;
    if(!miss_waits.enabled) {
        assert(miss_waits.configure(0,0,25,false,err));
        assert(miss_waits.owners[0]==-1 && miss_waits.records.empty());
        std::cout << "PASS default-off creates no timing events\n";
        return 0;
    }
    trace.active=true;miss_waits.begin();
    for(int device=0;device<2;++device) {
        assert(cudaSetDevice(device)==cudaSuccess);
        assert(miss_waits.configure(device,device ? 25 : 0,device ? 48 : 25,false,err));
        cudaStream_t stream;assert(cudaStreamCreate(&stream)==cudaSuccess);
        void* scratch=nullptr;assert(cudaMalloc(&scratch,65536)==cudaSuccess);
        for(int T: {1,4}) {
            const int groups=T>=2 ? 2 : 1;
            cudaGraph_t graph;cudaGraphExec_t exec;
            assert(cudaStreamBeginCapture(stream,cudaStreamCaptureModeThreadLocal)==cudaSuccess);
            for(int layer:miss_waits.layers) if((layer<25 ? 0 : 1)==device)
                for(int group=0;group<groups;++group)for(int phase=0;phase<5;++phase) {
                    miss_waits.mark(device,layer,group,phase,true,stream);
                    assert(cudaMemsetAsync(scratch,phase,65536,stream)==cudaSuccess);
                    miss_waits.mark(device,layer,group,phase,false,stream);
                }
            assert(cudaStreamEndCapture(stream,&graph)==cudaSuccess);
            assert(cudaGraphInstantiate(&exec,graph,0)==cudaSuccess);
            for(int repeat=0;repeat<2;++repeat) {
                trace.window=100+(uint64_t)T*10+repeat;
                assert(cudaGraphLaunch(exec,stream)==cudaSuccess);
                assert(cudaStreamSynchronize(stream)==cudaSuccess);
                miss_waits.completed(device,T,groups);
            }
            assert(cudaGraphExecDestroy(exec)==cudaSuccess);
            assert(cudaGraphDestroy(graph)==cudaSuccess);
        }
        assert(cudaFree(scratch)==cudaSuccess);
        assert(cudaStreamDestroy(stream)==cudaSuccess);
    }
    assert(miss_waits.records.size()==90);
    for(const auto& r:miss_waits.records) {
        assert(r.device==(r.layer<25 ? 0 : 1));
        assert(r.gpu_ms>=0 && std::isfinite(r.gpu_ms));
        assert(r.tokens>=1 && r.token_base>=0);
    }
    std::cout << "PASS 90 spans: two GPUs, T1/T4, two replays, exact ownership/groups/finite timing\n";
}
