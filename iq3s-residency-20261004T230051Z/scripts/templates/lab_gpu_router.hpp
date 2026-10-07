// Diagnostic-only next-gate projection. The real router and expert execution stay unchanged.
#pragma once
#include "strata/research/lab_trace.hpp"
#include "strata/core/weights.hpp"
#include "strata/core/layout.hpp"
#include "strata/kernels/bf16_gemv.hpp"
#include "strata/kernels/native_router.hpp"
#include "strata/kernels/elementwise.hpp"
#include <cuda_runtime.h>
#include <array>
#include <algorithm>
#include <stdexcept>

namespace strata::research {
struct RouterPrediction {
    uint64_t window, available_ns, offset;
    int32_t current_layer, target_layer, tokens, k;
};
struct RouterSpan {
    uint64_t window, observed_ns;
    int32_t current_layer, device;
    float gpu_ms;
    int32_t reserved;
};
static_assert(sizeof(RouterPrediction) == 40 && sizeof(RouterSpan) == 32);
struct GpuRouter {
    bool enabled = false;
    static constexpr int max_tokens = 4, k = 10;
    static constexpr std::array<int, 5> layers{5, 20, 25, 40, 46};
    struct Pair {
        bool configured = false;
        int device = -1;
        const uint16_t* gate = nullptr;
        cudaEvent_t begin = nullptr, end = nullptr;
    };
    std::array<Pair, 5> pairs{};
    std::array<int32_t*, 2> ids{}, host_ids{}, mapped_ids{};
    std::array<float*, 2> weights{};
    std::array<uint32_t*, 2> host_sequence{}, mapped_sequence{};
    std::array<bool, 2> configured{};
    std::vector<RouterPrediction> predictions;
    std::vector<int32_t> values;
    std::vector<RouterSpan> spans;
    int64_t width = 0, experts = 0;
    GpuRouter() {
        const char* flag = std::getenv("STRATA_LAB_GPU_ROUTER");
        enabled = flag && flag[0] == '1' && trace.enabled;
    }
    int index(int layer) const {
        auto found = std::find(layers.begin(), layers.end(), layer);
        return found == layers.end() ? -1 : (int)(found - layers.begin());
    }
    bool configure(const strata::core::WeightTable& wt, const strata::core::ModelGeometry& g,
                   int device, int first, int last, std::string& error) {
        if (!enabled) return true;
        if (device < 0 || device > 1 || g.n_embd != 2560 || g.n_expert != 512 ||
            (first == 0 && last == g.n_layers)) {
            error = "lab GPU router: only the frozen two-stage IQ3_S path is supported"; return false;
        }
        if (configured[device]) return true;
        width = g.n_embd; experts = g.n_expert;
        std::filesystem::create_directories(std::filesystem::path(trace.prefix).parent_path());
        auto allocate = [&](cudaError_t result) { return result == cudaSuccess; };
        if (!allocate(cudaMalloc(&ids[device], max_tokens * k * sizeof(int32_t))) ||
            !allocate(cudaMalloc(&weights[device], max_tokens * k * sizeof(float))) ||
            !allocate(cudaHostAlloc(&host_ids[device], layers.size() * max_tokens * k * sizeof(int32_t), cudaHostAllocMapped)) ||
            !allocate(cudaHostGetDevicePointer(&mapped_ids[device], host_ids[device], 0)) ||
            !allocate(cudaHostAlloc(&host_sequence[device], 64, cudaHostAllocMapped)) ||
            !allocate(cudaHostGetDevicePointer(&mapped_sequence[device], host_sequence[device], 0))) {
            error = "lab GPU router: bounded diagnostic allocation failed"; return false;
        }
        *host_sequence[device] = 0;
        int selected = 0;
        for (int i = 0; i < (int)layers.size(); ++i) {
            int layer = layers[i], target = layer + 1;
            if (layer < first || target >= last) continue;
            const auto* gate = wt.find("blk." + std::to_string(target) + ".ffn_gate_inp.weight");
            if (!gate || gate->kind != strata::core::WeightKind::Bf16InF32 ||
                gate->bytes != (uint64_t)width * experts * 2) {
                error = "lab GPU router: expected existing native BF16 gate"; return false;
            }
            auto& pair = pairs[i]; pair.gate = (const uint16_t*)gate->data; pair.device = device;
            if (cudaEventCreate(&pair.begin) != cudaSuccess || cudaEventCreate(&pair.end) != cudaSuccess) {
                error = "lab GPU router: external timing event allocation failed"; return false;
            }
            pair.configured = true; ++selected;
        }
        configured[device] = true;
        FILE* file = std::fopen((trace.prefix + "-gpu-router-device" + std::to_string(device) + ".json").c_str(), "w");
        if (!file) { error = "lab GPU router: cannot write metadata"; return false; }
        std::fprintf(file, "{\"device\":%d,\"first\":%d,\"last\":%d,\"width\":%lld,\"experts\":%lld,\"k\":10,\"max_tokens\":4,\"selected_pairs\":%d,\"extra_explicit_GPU_bytes\":320,\"mapped_CPU_bytes\":864,\"timing_events\":%d,\"prediction_record_bytes\":40,\"span_record_bytes\":32}\n",
            device, first, last, (long long)width, (long long)experts, selected, selected * 2);
        std::fclose(file);
        return true;
    }
    void begin() {
        if (!enabled) return;
        predictions.clear(); values.clear(); spans.clear();
        predictions.reserve(320); values.reserve(64 * 5 * max_tokens * k); spans.reserve(320);
    }
    void score(int layer, int tokens, const float* activation, float* temporary_logits, cudaStream_t stream) {
        const int i = index(layer);
        if (!enabled || i < 0 || !pairs[i].configured) return;
        if (tokens < 1 || tokens > max_tokens) throw std::runtime_error("lab GPU router: unsupported token group");
        auto& pair = pairs[i]; int device = pair.device;
        if (cudaEventRecordWithFlags(pair.begin, stream, cudaEventRecordExternal) != cudaSuccess)
            throw std::runtime_error("lab GPU router: begin event");
        strata::kernels::bf16_gemv_fp32_mmvf_multi(activation, width, pair.gate, temporary_logits,
            experts, width, width, experts, tokens, stream);
        strata::kernels::native_router_top10_multi(temporary_logits, ids[device], weights[device], tokens, stream);
        // A separate doorbell fences the mapped prediction IDs. No activation copy.
        strata::kernels::doorbell_publish_res(nullptr, ids[device], nullptr, (int)experts, 0,
            tokens * k, nullptr, mapped_ids[device] + i * max_tokens * k,
            mapped_sequence[device], stream);
        if (cudaEventRecordWithFlags(pair.end, stream, cudaEventRecordExternal) != cudaSuccess)
            throw std::runtime_error("lab GPU router: end event");
    }
    void host(int layer, int tokens) {
        const int i = index(layer);
        if (!enabled || !trace.active || trace.windows.size() > 64 || i < 0 || !pairs[i].configured) return;
        const uint64_t available = ns(), offset = values.size();
        const auto* input = host_ids[pairs[i].device] + i * max_tokens * k;
        values.insert(values.end(), input, input + tokens * k);
        predictions.push_back({trace.window, available, offset, layer, layer + 1, tokens, k});
    }
    void completed(int device) {
        if (!enabled || !trace.active || trace.windows.size() > 64) return;
        for (int i = 0; i < (int)layers.size(); ++i) {
            auto& pair = pairs[i];
            if (!pair.configured || pair.device != device) continue;
            float elapsed = 0;
            if (cudaEventElapsedTime(&elapsed, pair.begin, pair.end) != cudaSuccess)
                throw std::runtime_error("lab GPU router: event timing unavailable after existing stream sync");
            spans.push_back({trace.window, ns(), layers[i], device, elapsed, 0});
        }
    }
    void flush() {
        if (!enabled) return;
        const std::string prefix = trace.prefix + "-request" + std::to_string(trace.request);
        trace.file(prefix + "-gpu-router-predictions.bin", predictions);
        trace.file(prefix + "-gpu-router-values.bin", values);
        trace.file(prefix + "-gpu-router-spans.bin", spans);
    }
};
inline GpuRouter gpu_router;
}
