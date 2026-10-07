"""Record the all-local fast-return accounting; diagnostics remain separate from speed."""
import pathlib,subprocess,sys
r=pathlib.Path(__file__).resolve().parents[1];s=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(r/'scripts/patch_diagnostics.py'),str(s)],check=True)
subprocess.run([sys.executable,str(r/'scripts/patch_skip_local_plan.py'),str(s)],check=True)
p=s/'src/core/expert_source.cpp';t=p.read_text();old='''        if(all_local){
            d.cache_hits+=n_tok*k;'''
new='''        if(all_local){
            int32_t lab_kind[kMaxWindowEntries]{};
            const auto lab_now=strata::research::ns();
            const auto lab_begin=(uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(c0.time_since_epoch()).count();
            strata::research::trace.decision((uint32_t)d.layers,(uint16_t)n_tok,(uint16_t)k,ids,lab_kind,d.host_res,
                lab_begin,lab_now,lab_now,lab_now,lab_now);
            d.cache_hits+=n_tok*k;'''
assert t.count(old)==1;p.write_text(t.replace(old,new))
p=s/'src/program/generate.cpp';t=p.read_text();old='                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;'
assert t.count(old)==1
new='''                if(first_window&&strata::research::trace.enabled){
                    std::vector<float> lab_logits((size_t)ver.vocab());
                    if(!ver.copy_logits(0,lab_logits.data())){std::printf("ERR lab first logits copy\\n");return 1;}
                    strata::research::trace.file(strata::research::trace.prefix+"-request"+std::to_string(strata::research::trace.request)+"-first-logits.bin",lab_logits);
                }
''' +old
p.write_text(t.replace(old,new))
print('Buffered true demand/accounting for the removed host work; no predictor or expert math',flush=True)
