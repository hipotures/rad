// Exercise the real built doorbell kernel, including replay on both devices.
#include <cuda_runtime.h>
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstdint>

namespace strata::kernels {
void doorbell_publish_res(const float*, const int32_t*, const int32_t*, int,
                          int64_t, int64_t, float*, int32_t*, uint32_t*, void*);
}
static void check(cudaError_t code) {
    if (code != cudaSuccess) {
        std::fprintf(stderr, "CUDA failure: %s\n", cudaGetErrorString(code));
        std::exit(1);
    }
}
struct Host {
    float x[1024];
    int32_t ids[40];
    uint32_t sequence;
};
int main() {
    for (int gpu = 0; gpu < 2; ++gpu) {
        check(cudaSetDevice(gpu));
        cudaStream_t stream;
        check(cudaStreamCreateWithFlags(&stream, cudaStreamNonBlocking));
        Host* host = nullptr;
        Host* mapped = nullptr;
        check(cudaHostAlloc(&host, sizeof(Host), cudaHostAllocMapped));
        check(cudaHostGetDevicePointer(&mapped, host, 0));
        float* x = nullptr;
        int32_t* ids = nullptr;
        int32_t* resident = nullptr;
        check(cudaMalloc(&x, 1024 * sizeof(float)));
        check(cudaMalloc(&ids, 40 * sizeof(int32_t)));
        check(cudaMalloc(&resident, 32 * sizeof(int32_t)));
        for (int rows : {1, 4}) {
            const int count = rows * 256, entries = rows * 10;
            std::array<int32_t, 40> input_ids{};
            std::array<int32_t, 32> slots{};
            for (int i = 0; i < entries; ++i) input_ids[i] = i % 32;
            for (int i = 0; i < 32; ++i) slots[i] = i;
            check(cudaMemcpy(ids, input_ids.data(), entries * sizeof(int32_t), cudaMemcpyHostToDevice));
            for (int mode = 0; mode < 3; ++mode) {
                // Mode 0 reproduces the original all-local stale-host behavior.
                // Mode 1 forces a fresh diagnostic copy; mode 2 has a true miss.
                slots[0] = mode == 2 ? -1 : 0;
                check(cudaMemcpy(resident, slots.data(), sizeof(slots), cudaMemcpyHostToDevice));
                check(cudaStreamBeginCapture(stream, cudaStreamCaptureModeThreadLocal));
                strata::kernels::doorbell_publish_res(x, ids, mode == 1 ? nullptr : resident,
                    32, count, entries, mapped->x, mapped->ids, &mapped->sequence, stream);
                cudaGraph_t graph;
                check(cudaStreamEndCapture(stream, &graph));
                cudaGraphExec_t executable;
                check(cudaGraphInstantiate(&executable, graph, 0));
                for (int repetition = 0; repetition < 3; ++repetition) {
                    std::array<float, 1024> input{};
                    for (int i = 0; i < count; ++i) input[i] = gpu * 10000 + repetition * 2000 + i;
                    std::fill(std::begin(host->x), std::end(host->x), -777.0f);
                    std::fill(std::begin(host->ids), std::end(host->ids), -1);
                    host->sequence = 0;
                    check(cudaMemcpy(x, input.data(), count * sizeof(float), cudaMemcpyHostToDevice));
                    check(cudaGraphLaunch(executable, stream));
                    check(cudaStreamSynchronize(stream));
                    assert(host->sequence == 1);
                    for (int i = 0; i < entries; ++i) assert(host->ids[i] == input_ids[i]);
                    for (int i = 0; i < count; ++i)
                        assert(host->x[i] == (mode == 0 ? -777.0f : input[i]));
                }
                check(cudaGraphExecDestroy(executable));
                check(cudaGraphDestroy(graph));
            }
        }
        check(cudaFree(x));
        check(cudaFree(ids));
        check(cudaFree(resident));
        check(cudaFreeHost(host));
        check(cudaStreamDestroy(stream));
    }
    std::puts("PASS: both GPUs, one/four rows, all-local/miss/forced-fresh, three graph replays");
}
