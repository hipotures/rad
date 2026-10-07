"""Apply scoped external-event timing to an isolated frozen-base diagnostic build."""
import pathlib, shutil, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(ROOT/'scripts/patch_diagnostics.py'),str(src)],check=True)
shutil.copy2(ROOT/'scripts/templates/lab_miss_waits.hpp',src/'include/strata/research/lab_miss_waits.hpp')
def edit(path,old,new,count=1):
    p=src/path;s=p.read_text()
    if s.count(old)!=count:raise RuntimeError(f'{path}: expected {count} anchors, got {s.count(old)}: {old[:120]}')
    p.write_text(s.replace(old,new,count))
verify='src/core/verify.cpp';generate='src/program/generate.cpp'
for path in [verify,generate]:
    edit(path,'#include "strata/research/lab_trace.hpp"','#include "strata/research/lab_trace.hpp"\n#include "strata/research/lab_miss_waits.hpp"')
edit(verify,'    std::fprintf(stderr, "strata verify: window up to %d tokens, %.1f MiB of device buffers%s\\n", max_t,',
     '    if (!strata::research::miss_waits.configure(device_, (int32_t)lb_, (int32_t)le_, all_resident_, err)) return false;\n    std::fprintf(stderr, "strata verify: window up to %d tokens, %.1f MiB of device buffers%s\\n", max_t,')
edit(generate,'                strata::research::trace.begin(host_res, (int32_t)g.n_expert, bytes, drive.d.usage);',
     '                strata::research::trace.begin(host_res, (int32_t)g.n_expert, bytes, drive.d.usage);\n                strata::research::miss_waits.begin();')
edit(generate,'            strata::research::trace.flush(host_res, drive.d.usage);',
     '            strata::research::trace.flush(host_res, drive.d.usage);\n            strata::research::miss_waits.flush();')
mark=lambda phase,start:f'            strata::research::miss_waits.mark(device_, (int32_t)l, grp, {phase}, {str(start).lower()}, cs);\n'
# Phase0 includes GPU plan wait plus the mapped plan copy; explicitly not a pure expert-miss cost.
edit(verify,'        } else {\n            if (device_plan_) {   // E-6:',
     '        } else {\n'+mark(0,True)+'            if (device_plan_) {   // E-6:')
edit(verify,'            stamp(l, 19, grp);\n            grouped(p_ptr, p_start, p_counts, 0, hit_out);\n            stamp(l, 20, grp);',
     mark(0,False)+mark(1,True)+'            stamp(l, 19, grp);\n            grouped(p_ptr, p_start, p_counts, 0, hit_out);\n            stamp(l, 20, grp);\n'+mark(1,False)+mark(2,True))
edit(verify,'            stamp(l, 22, grp);\n            if (device_plan_) {',
     '            stamp(l, 22, grp);\n'+mark(2,False)+mark(3,True)+'            if (device_plan_) {')
# Bracket only CPU-completion flag wait, before any returned row copies.
edit(verify,'                wait_flag_ge_or(m_flag_, ring, skip_ + grp, cs);\n                copy_or_zero_from_mapped',
     '                wait_flag_ge_or(m_flag_, ring, skip_ + grp, cs);\n'+mark(3,False)+'                copy_or_zero_from_mapped')
edit(verify,'                wait_flag_ge(m_flag_, ring, cs);               // the CPU\'s share is in the mapped rows\n                stamp(l, 23, grp);',
     '                wait_flag_ge(m_flag_, ring, cs);               // the CPU\'s share is in the mapped rows\n'+mark(3,False)+'                stamp(l, 23, grp);')
edit(verify,'    trace_ev("SYNCED", -1, -1, (int64_t) se);\n    if (se != cudaSuccess)',
     '    if (se == cudaSuccess) strata::research::miss_waits.completed(device_, T, groups_[T] > 0 ? groups_[T] : 1);\n    trace_ev("SYNCED", -1, -1, (int64_t) se);\n    if (se != cudaSuccess)')
# Save one same-input head after the existing completed verifier sync, outside headline binaries.
edit(generate,'                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;',
     '                if (first_window && strata::research::miss_waits.enabled) {\n                    std::vector<float> lab_logits((size_t)ver.vocab());\n                    if (!ver.copy_logits(0, lab_logits.data())) { std::printf("ERR lab first logits copy failed\\n"); return 1; }\n                    strata::research::trace.file(strata::research::trace.prefix + "-request" + std::to_string(strata::research::trace.request) + "-first-logits.bin", lab_logits);\n                }\n                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;')
print('Default-off selected-layer GPU miss spans applied; no headline use',flush=True)
