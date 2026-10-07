// Demonstrate shared-ID overwrite and stable layer snapshots with the real kernel.
#include <cuda_runtime.h>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

namespace strata::kernels {
void doorbell_publish_res(const float*, const int32_t*, const int32_t*, int,
                          int64_t, int64_t, float*, int32_t*, uint32_t*, void*);
}
void check(cudaError_t code) {
    if (code != cudaSuccess) { std::fprintf(stderr, "%s\n", cudaGetErrorString(code)); std::exit(1); }
}
struct Host { int32_t shared[40], stable[80]; uint32_t sequence; };
int main() {
    for (int device = 0; device < 2; ++device) {
        check(cudaSetDevice(device));
        Host *host = nullptr, *mapped = nullptr;
        check(cudaHostAlloc(&host, sizeof(Host), cudaHostAllocMapped));
        check(cudaHostGetDevicePointer(&mapped, host, 0));
        int32_t *ids = nullptr, *resident = nullptr;
        check(cudaMalloc(&ids, 80 * sizeof(int32_t)));
        check(cudaMalloc(&resident, 64 * sizeof(int32_t)));
        std::array<int32_t, 64> slots{};
        for (int i = 0; i < 64; ++i) slots[i] = i;
        check(cudaMemcpy(resident, slots.data(), sizeof(slots), cudaMemcpyHostToDevice));
        cudaStream_t stream;
        check(cudaStreamCreateWithFlags(&stream, cudaStreamNonBlocking));
        for (int rows : {1, 4}) {
            const int k = rows * 10;
            std::array<int32_t, 80> input{};
            for (int i = 0; i < k; ++i) { input[i] = i % 10; input[k + i] = 20 + i % 10; }
            check(cudaMemcpy(ids, input.data(), sizeof(input), cudaMemcpyHostToDevice));
            for (int stable = 0; stable < 2; ++stable) {
                check(cudaStreamBeginCapture(stream, cudaStreamCaptureModeThreadLocal));
                for (int layer = 0; layer < 2; ++layer) {
                    strata::kernels::doorbell_publish_res(nullptr, ids + layer * k, resident,
                        64, 0, k, nullptr, stable ? mapped->stable + layer * 40 : mapped->shared,
                        &mapped->sequence, stream);
                }
                cudaGraph_t graph;
                check(cudaStreamEndCapture(stream, &graph));
                cudaGraphExec_t executable;
                check(cudaGraphInstantiate(&executable, graph, 0));
                for (int repetition = 0; repetition < 3; ++repetition) {
                    host->sequence = 0;
                    check(cudaGraphLaunch(executable, stream));
                    check(cudaStreamSynchronize(stream));
                    assert(host->sequence == 2);
                    // The host can now satisfy want=1, but a shared row contains layer1.
                    for (int i = 0; i < k; ++i) {
                        if (stable) {
                            assert(host->stable[i] == input[i]);
                            assert(host->stable[40 + i] == input[k + i]);
                        } else {
                            assert(host->shared[i] == input[k + i]);
                            assert(host->shared[i] != input[i]);
                        }
                    }
                }
                check(cudaGraphExecDestroy(executable));
                check(cudaGraphDestroy(graph));
            }
        }
        check(cudaStreamDestroy(stream));
        check(cudaFree(ids)); check(cudaFree(resident)); check(cudaFreeHost(host));
    }
    std::puts("PASS: real shared-ID overwrite reproduced; stable layer snapshots preserve both layers on two GPUs");
}
