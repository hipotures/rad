"""Add bounded activations and actual handoff timing to validated default-off diagnostics."""
import pathlib, shutil, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(ROOT/'scripts/patch_diagnostics.py'),str(src)],check=True)
shutil.copy2(ROOT/'scripts/templates/lab_signals.hpp',src/'include/strata/research/lab_signals.hpp')
def edit(path,old,new,count=1):
    p=src/path;content=p.read_text();actual=content.count(old)
    if actual!=count:raise RuntimeError(f'{path}: expected{count} anchors, found{actual}: {old[:100]}')
    p.write_text(content.replace(old,new,count))
for path in ['src/core/expert_source.cpp','src/core/verify.cpp','src/program/generate.cpp']:
    edit(path,'#include "strata/research/lab_trace.hpp"','#include "strata/research/lab_trace.hpp"\n#include "strata/research/lab_signals.hpp"')
edit('src/core/verify.cpp','    const WeightRef* wo = wt.find("output.weight");',
     '    if (!strata::research::signals.configure(wt, g, device_, (int32_t)lb_, (int32_t)le_, err)) return false;\n    const WeightRef* wo = wt.find("output.weight");')
edit('src/program/generate.cpp','                strata::research::trace.begin(host_res, (int32_t)g.n_expert, bytes, drive.d.usage);',
     '                strata::research::trace.begin(host_res, (int32_t)g.n_expert, bytes, drive.d.usage);\n                strata::research::signals.begin();')
edit('src/program/generate.cpp','            strata::research::trace.flush(host_res, drive.d.usage);',
     '            strata::research::trace.flush(host_res, drive.d.usage);\n            strata::research::signals.flush();')
# x_f already resides in host memory and is available after the current router's
# doorbell. Capture before CPU quantization/jobs, never a future router activation.
edit('src/core/expert_source.cpp','    const auto c1 = std::chrono::steady_clock::now();\n    if (any_cpu) {',
     '    strata::research::signals.activation((int32_t)d.layers, (int32_t)n_tok, x_f);\n    const auto c1 = std::chrono::steady_clock::now();\n    if (any_cpu) {')
edit('src/core/verify.cpp','    if (lb_ > 0) {\n        const float* hin = hand_in_ + (size_t) hrow0 * HB;',
     '    if (lb_ > 0) {\n        strata::research::signals.mark_gpu(device_, true, true, cs);\n        const float* hin = hand_in_ + (size_t) hrow0 * HB;')
edit('src/core/verify.cpp','        copy_from_mapped(inj2_, hin + (size_t) T * (HC + 1) * N, (int64_t) T * HC, cs);',
     '        copy_from_mapped(inj2_, hin + (size_t) T * (HC + 1) * N, (int64_t) T * HC, cs);\n        strata::research::signals.mark_gpu(device_, true, false, cs);')
edit('src/core/verify.cpp','        float* hout = hand_out_ + (size_t) hrow0 * HB;',
     '        strata::research::signals.mark_gpu(device_, false, true, cs);\n        float* hout = hand_out_ + (size_t) hrow0 * HB;')
edit('src/core/verify.cpp','        copy_from_mapped(hout + (size_t) T * (HC + 1) * N, inj2_, (int64_t) T * HC, cs);',
     '        copy_from_mapped(hout + (size_t) T * (HC + 1) * N, inj2_, (int64_t) T * HC, cs);\n        strata::research::signals.mark_gpu(device_, false, false, cs);')
run_anchor='bool Verifier::run(int T, const int32_t* tokens, int64_t pos0, PoolMultiFn pool, void* user, int32_t* out,\n                   std::string& err) {\n    using namespace strata::kernels;'
edit('src/core/verify.cpp',run_anchor,run_anchor+'\n    const uint64_t lab_entry = strata::research::signals.enabled ? strata::research::ns() : 0;\n    strata::research::signals.cpu(device_, (int32_t)lb_, (int32_t)le_, 4, lab_entry, lab_entry);')
edit('src/core/verify.cpp','    if (!capture(T, err) || !capture_commit(err)) return false;',
     '    const uint64_t lab_capture = strata::research::signals.enabled ? strata::research::ns() : 0;\n    if (!capture(T, err) || !capture_commit(err)) return false;\n    strata::research::signals.cpu(device_, (int32_t)lb_, (int32_t)le_, 5, lab_capture, strata::research::signals.enabled ? strata::research::ns() : 0);')
edit('src/core/verify.cpp','    if (!staged_) stage_inputs(T, tokens, pos0);\n    staged_ = false;',
     '    const uint64_t lab_stage = strata::research::signals.enabled ? strata::research::ns() : 0;\n    if (!staged_) stage_inputs(T, tokens, pos0);\n    staged_ = false;\n    strata::research::signals.cpu(device_, (int32_t)lb_, (int32_t)le_, 0, lab_stage, strata::research::signals.enabled ? strata::research::ns() : 0);')
edit('src/core/verify.cpp','    const cudaError_t le = cudaGraphLaunch(exec_[T], cs_);',
     '    const uint64_t lab_launch = strata::research::signals.enabled ? strata::research::ns() : 0;\n    const cudaError_t le = cudaGraphLaunch(exec_[T], cs_);\n    strata::research::signals.cpu(device_, (int32_t)lb_, (int32_t)le_, 1, lab_launch, strata::research::signals.enabled ? strata::research::ns() : 0);')
edit('src/core/verify.cpp','    const cudaError_t se = cudaStreamSynchronize(cs_);\n    trace_ev("SYNCED", -1, -1, (int64_t) se);',
     '    const uint64_t lab_sync = strata::research::signals.enabled ? strata::research::ns() : 0;\n    const cudaError_t se = cudaStreamSynchronize(cs_);\n    strata::research::signals.cpu(device_, (int32_t)lb_, (int32_t)le_, 2, lab_sync, strata::research::signals.enabled ? strata::research::ns() : 0);\n    if (se == cudaSuccess) strata::research::signals.completed(device_, (int32_t)lb_, (int32_t)le_, T, g.n_layers);\n    trace_ev("SYNCED", -1, -1, (int64_t) se);')
# One diagnostic head on identical effective input, not a free-generation KL.
edit('src/program/generate.cpp','                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;',
     '                if (first_window && strata::research::signals.enabled) {\n                    std::vector<float> lab_logits((size_t)ver.vocab());\n                    if (!ver.copy_logits(0, lab_logits.data())) { std::printf("ERR lab first logits copy failed\\n"); return 1; }\n                    strata::research::trace.file(strata::research::trace.prefix + "-request" + std::to_string(strata::research::trace.request) + "-first-logits.bin", lab_logits);\n                }\n                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;')
print('Bounded CUDA signal/boundary diagnostics applied; tests required',flush=True)
