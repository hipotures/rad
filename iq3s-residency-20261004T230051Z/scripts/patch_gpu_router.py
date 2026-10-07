"""Add default-off existing-GPU next-gate diagnostics; no expert movement."""
import pathlib
import shutil
import subprocess
import sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
source = pathlib.Path(sys.argv[1])
subprocess.run([sys.executable, str(ROOT / 'scripts/patch_diagnostics.py'), str(source)], check=True)
shutil.copy2(ROOT / 'scripts/templates/lab_gpu_router.hpp', source / 'include/strata/research/lab_gpu_router.hpp')
def edit(path, old, new):
    path = source / path; text = path.read_text()
    assert text.count(old) == 1, (path, old[:100], text.count(old))
    path.write_text(text.replace(old, new))
for path in ('src/core/verify.cpp', 'src/core/expert_source.cpp', 'src/program/generate.cpp'):
    edit(path, '#include "strata/research/lab_trace.hpp"',
         '#include "strata/research/lab_trace.hpp"\n#include "strata/research/lab_gpu_router.hpp"')
edit('src/core/verify.cpp', '    const WeightRef* wo = wt.find("output.weight");',
     '    if (!strata::research::gpu_router.configure(wt, g, device_, (int)lb_, (int)le_, err)) return false;\n'
     '    const WeightRef* wo = wt.find("output.weight");')
edit('src/core/verify.cpp', '    static const bool dec_batch = [] { const char* v = std::getenv("STRATA_DEC_BATCH");',
     '    if (strata::research::gpu_router.enabled && (G != 1 || batch_rec_)) { err = "lab GPU router: only serial one-group windows"; return false; }\n'
     '    static const bool dec_batch = [] { const char* v = std::getenv("STRATA_DEC_BATCH");')
edit('src/core/verify.cpp', '        if (all_resident_) {\n            resident_plan(',
     '        strata::research::gpu_router.score((int)l, n, xm, logits_ + tb * NE, cs);\n'
     '        if (all_resident_) {\n            resident_plan(')
edit('src/core/expert_source.cpp', '    const auto c0 = std::chrono::steady_clock::now();\n    pt("begin");',
     '    const auto c0 = std::chrono::steady_clock::now();\n'
     '    strata::research::gpu_router.host((int)d.layers, (int)n_tok);\n    pt("begin");')
edit('src/core/verify.cpp', '    if (se != cudaSuccess) { err = std::string("verify: ") + cudaGetErrorString(se); return false; }\n    commit_pending_ = false;',
     '    if (se != cudaSuccess) { err = std::string("verify: ") + cudaGetErrorString(se); return false; }\n'
     '    strata::research::gpu_router.completed(device_);\n    commit_pending_ = false;')
edit('src/program/generate.cpp', '                strata::research::trace.begin(host_res, (int32_t)g.n_expert, bytes, drive.d.usage);',
     '                strata::research::trace.begin(host_res, (int32_t)g.n_expert, bytes, drive.d.usage);\n'
     '                strata::research::gpu_router.begin();')
edit('src/program/generate.cpp', '            strata::research::trace.flush(host_res, drive.d.usage);',
     '            strata::research::trace.flush(host_res, drive.d.usage);\n'
     '            strata::research::gpu_router.flush();')
old = '                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;'
edit('src/program/generate.cpp', old,
     '                if (first_window && strata::research::gpu_router.enabled) {\n'
     '                    std::vector<float> lab_logits((size_t)ver.vocab());\n'
     '                    if (!ver.copy_logits(0, lab_logits.data())) { std::printf("ERR lab first logits copy failed\\n"); return 1; }\n'
     '                    strata::research::trace.file(strata::research::trace.prefix + "-request" + std::to_string(strata::research::trace.request) + "-first-logits.bin", lab_logits);\n'
     '                }\n' + old)
print('GPU next-gate diagnostics use existing local gate and reused logits scratch; true router untouched', flush=True)
