// Bounded inventory check: enumerate devices and exercise their CUDA runtime.
#include <cuda_runtime.h>
#include <cstdio>

__global__ void square(int *out) {
    const int i = threadIdx.x;
    out[i] = i * i;
}

int main() {
    int count = 0;
    cudaError_t status = cudaGetDeviceCount(&count);
    if (status != cudaSuccess) {
        std::fprintf(stderr, "cudaGetDeviceCount: %s\n", cudaGetErrorString(status));
        return 1;
    }
    for (int device = 0; device < count; ++device) {
        cudaDeviceProp p{};
        int *output = nullptr;
        int host[32]{};
        if (cudaSetDevice(device) != cudaSuccess ||
            cudaGetDeviceProperties(&p, device) != cudaSuccess ||
            cudaMalloc(&output, sizeof(host)) != cudaSuccess) return 2;
        square<<<1, 32>>>(output);
        status = cudaMemcpy(host, output, sizeof(host), cudaMemcpyDeviceToHost);
        if (status != cudaSuccess) {
            std::fprintf(stderr, "device %d: %s\n", device, cudaGetErrorString(status));
            return 3;
        }
        for (int i = 0; i < 32; ++i) if (host[i] != i * i) return 4;
        cudaFree(output);
        std::printf("PASS device=%d name=%s compute=%d.%d total_vram_bytes=%zu\n",
                    device, p.name, p.major, p.minor, p.totalGlobalMem);
    }
    return count == 2 ? 0 : 5;
}
