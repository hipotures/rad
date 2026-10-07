"""Same-binary ON/OFF buffered per-layer/head arithmetic diagnosis."""
import pathlib,subprocess,sys,shutil
r=pathlib.Path(__file__).resolve().parents[1];s=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(r/'scripts/patch_device_plan_diagnostics.py'),str(s)],check=True)
shutil.copy2(r/'scripts/templates/lab_plan_compare.hpp',s/'include/strata/research/lab_plan_compare.hpp')
p=s/'src/core/verify.cpp';t=p.read_text()
def replace(old,new):
 global t
 assert t.count(old)==1,(old[:90],t.count(old));t=t.replace(old,new)
replace('#include "strata/research/lab_trace.hpp"','#include "strata/research/lab_trace.hpp"\n#include "strata/research/lab_plan_compare.hpp"')
replace('    const WeightRef* wo = wt.find("output.weight");','    if (!strata::research::plan_compare.configure(device_,(int)lb_,(int)le_,err)) return false;\n    const WeightRef* wo = wt.find("output.weight");')
replace('        stamp(l, 24, grp);','        strata::research::plan_compare.capture(device_,(int)l,n,mixed_+tb*N,bo_+tb*N,pl,(int)(plan_i32_+16),cs);\n        stamp(l, 24, grp);')
replace('    commit_pending_ = false;\n    progress_at("verify window: waiting for the expert copies", (int64_t) T);','    strata::research::plan_compare.completed(device_);\n    commit_pending_ = false;\n    progress_at("verify window: waiting for the expert copies", (int64_t) T);')
replace('                if (all_resident_) wait_flag_ge(m_flag_, 1, cs);',
        '                const char* lab_ple_fence = std::getenv("STRATA_LAB_PLAN_PLE_FENCE");\n'
        '                if (all_resident_ || (device_plan_ids_ && lab_ple_fence && lab_ple_fence[0] == \'1\')) wait_flag_ge(m_flag_, 1, cs);')
p.write_text(t)
p=s/'src/program/generate.cpp';t=p.read_text()
old='                if (first_window && strata::research::trace.enabled) {'
assert t.count(old)==1
# Retain all rows of the first eight true windows, with their input IDs in the normal trace.
t=t.replace(old,'                if (strata::research::trace.enabled && strata::research::trace.windows.size() <= 8) {')
old='                    strata::research::trace.file(strata::research::trace.prefix + "-request" + std::to_string(strata::research::trace.request) + "-first-logits.bin", lab_logits);'
new='''                    for(int lab_row=0;lab_row<T;++lab_row){
                        if(!ver.copy_logits(lab_row,lab_logits.data())){std::printf("ERR lab row logits copy\\n");return 1;}
                        strata::research::trace.file(strata::research::trace.prefix+"-request"+std::to_string(strata::research::trace.request)+"-window"+std::to_string(strata::research::trace.window)+"-row"+std::to_string(lab_row)+"-logits.bin",lab_logits);
                    }'''
assert t.count(old)==1;p.write_text(t.replace(old,new))
print('Buffered native plan, activation, expert-sum and head rows; diagnostics excluded from TG',flush=True)
