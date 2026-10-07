"""Remove only host work proven unused by a safely device-planned local group."""
import pathlib,subprocess,sys
r=pathlib.Path(__file__).resolve().parents[1];s=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(r/'scripts/patch_device_plan_v2.py'),str(s)],check=True)
p=s/'src/core/verify.cpp';t=p.read_text();old='    if (device_plan_ids_ && !device_plan_) {'
assert t.count(old)==1
new='''    const char* lab_skip_plan = std::getenv("STRATA_LAB_SKIP_LOCAL_PLAN");
    if (lab_skip_plan && lab_skip_plan[0]=='1' && !device_plan_ids_) {
        err="lab skip host plan: corrected serial device-plan IDs path is required";return false;
    }
''' + old
p.write_text(t.replace(old,new))
p=s/'src/core/expert_source.cpp';t=p.read_text();old='    // ---- plan v0.3 P6: the GPU\'s share, decided and published FIRST so the GPU starts while the CPU works.'
assert t.count(old)==1
new='''    // The corrected GPU plan owns all-local rows; only truthful host heat/counters are needed.
    static const bool lab_skip_local = [] {const char* e=std::getenv("STRATA_LAB_SKIP_LOCAL_PLAN");return e&&e[0]=='1';}();
    if (lab_skip_local && d.plan && d.host_res && d.remote_count==0 && !d.peer) {
        bool all_local=true;
        for(int64_t i=0;i<n_tok*k;++i){
            const int32_t e=ids[i];
            if(e<0||e>=d.n_expert||d.host_res[(size_t)d.layers*(size_t)d.n_expert+(size_t)e]<0){all_local=false;break;}
        }
        if(all_local){
            d.cache_hits+=n_tok*k;
            d.experts+=n_tok*k;
            ++d.layers;
            d.ms_plan+=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-c0).count();
            return;
        }
    }
''' + old
p.write_text(t.replace(old,new))
print('Opt-in all-local host-plan suppression; original true GPU math and mixed path unchanged',flush=True)
