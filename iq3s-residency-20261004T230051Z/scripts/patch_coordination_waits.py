"""Same-binary OFF/ON coordination timing, including the GPU planning/doorbell phase."""
import pathlib
import subprocess
import sys
r=pathlib.Path(__file__).resolve().parents[1]
s=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(r/'scripts/patch_miss_waits.py'),str(s)],check=True)
subprocess.run([sys.executable,str(r/'scripts/patch_skip_local_plan.py'),str(s)],check=True)
p=s/'src/core/expert_source.cpp';text=p.read_text()
old='''        if(all_local){
            d.cache_hits+=n_tok*k;'''
new='''        if(all_local){
            int32_t lab_kind[kMaxWindowEntries]{};
            const auto lab_now=strata::research::ns();
            const auto lab_begin=(uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(c0.time_since_epoch()).count();
            strata::research::trace.decision((uint32_t)d.layers,(uint16_t)n_tok,(uint16_t)k,ids,lab_kind,d.host_res,
                lab_begin,lab_now,lab_now,lab_now,lab_now);
            d.cache_hits+=n_tok*k;'''
assert text.count(old)==1;p.write_text(text.replace(old,new))
p=s/'include/strata/research/lab_miss_waits.hpp';text=p.read_text()
for old,new in [('cudaEvent_t,2>,4>','cudaEvent_t,2>,5>'),('phase>3','phase>4'),('phase<4','phase<5')]:
    assert text.count(old)==1,(old,text.count(old));text=text.replace(old,new)
p.write_text(text)
p=s/'src/core/verify.cpp';text=p.read_text()
old='        if (all_resident_) {\n            resident_plan('
new='        strata::research::miss_waits.mark(device_, (int32_t)l, grp, 4, true, cs);\n'+old
assert text.count(old)==1;text=text.replace(old,new)
old='        stamp(l, 17, grp);'
assert text.count(old)==1;text=text.replace(old,'        strata::research::miss_waits.mark(device_, (int32_t)l, grp, 4, false, cs);\n'+old)
p.write_text(text)
print('Five GPU phases; same-binary all-local coordination OFF/ON; no expert math change',flush=True)
