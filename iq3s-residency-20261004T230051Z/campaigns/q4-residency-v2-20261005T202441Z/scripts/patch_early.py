"""Early Q4 admission: charged spare slots, CPU-only learned scores, native gate scratch reuse."""
from pathlib import Path
import shutil,sys
C=Path(__file__).resolve().parents[1];S=Path(sys.argv[1])
def edit(path,old,new,count=1):
 p=S/path;t=p.read_text();assert t.count(old)==count,(path,old[:90],t.count(old));p.write_text(t.replace(old,new,count))
(S/'include/strata/research').mkdir(exist_ok=True)
for name in ['q4_early_policy.hpp','q4_linear_constants.hpp']:shutil.copy2(C/'scripts/templates'/name,S/'include/strata/research'/name)
for path in ['src/core/verify.cpp','src/core/expert_source.cpp','src/program/generate.cpp']:
 p=S/path;p.write_text('#include "strata/research/q4_early_policy.hpp"\n'+p.read_text())
edit('src/core/verify.cpp','    const WeightRef* wo = wt.find("output.weight");', '    if(!strata::research::q4_early.configure_gate(wt,g,device_,(int)lb_,(int)le_,err))return false;\n    const WeightRef* wo = wt.find("output.weight");')
edit('src/core/verify.cpp','        const WeightRef* w_router = v.get("ffn_gate_inp.weight");','        strata::research::q4_early.gpu_score((int)l,n,xm,logits_+tb*NE,ids_+tb*K,w_+tb*K,cs);\n        const WeightRef* w_router = v.get("ffn_gate_inp.weight");')
edit('src/core/expert_source.cpp','    d.src->begin_layer(d.layers, ids, n_tok * k);','    strata::research::q4_early.host(const_cast<int32_t*>(d.host_res),(int)d.layers,ids,(int)(n_tok*k));\n    d.src->begin_layer(d.layers, ids, n_tok * k);')
edit('src/program/generate.cpp','    const bool auto_cache = o.expert_cache < 0;', '    if(!strata::research::q4_early.configure_gate(wt,g,0,0,24,err)){std::fprintf(stderr,\"Q4 early startup: %s\\n\",err.c_str());return 1;}\n    const bool auto_cache = o.expert_cache < 0;')
edit('src/program/generate.cpp','        const int64_t room = stage_room(st.dev, true, false);', '        {const strata::core::OnDevice on_early(st.dev);if(!strata::research::q4_early.configure_gate(st.wt,g,st.dev,(int)st.lb,(int)st.le,err)){std::fprintf(stderr,\"Q4 early startup: %s\\n\",err.c_str());return 1;}}\n        const int64_t room = stage_room(st.dev, true, false);')
edit('src/program/generate.cpp','        Clock::time_point profile_saved_at = Clock::now();','''        if(strata::research::q4_early.enabled){
            if(!multi_gpu||stages.size()!=1||stage_of(23)!=0||stage_of(24)!=1||o.pcie_frac!=.28||o.batch>0||o.resident_budget>0||dynamic_cast<strata::core::ArenaExpertSource*>(srcp)==nullptr)throw std::runtime_error("Q4 early requires frozen full-arena serial K24/PCIe0.28");
            std::vector<uint64_t> blobs;for(int l=0;l<g.n_layers;++l)blobs.push_back(strata::kernels::cpu::expert_layout().blob_bytes(l));
            strata::research::q4_early.runtime(host_res.data(),drive.d.usage.data(),std::move(blobs),{d_res,stages[0]->d_res},
                [&](int l,int e){return srcp->blob(l,e);},[&](int dev,int slot)->void*{return dev?stages[0]->cache.device_slot(slot):xcache.device_slot(slot);});
        }
        Clock::time_point profile_saved_at = Clock::now();''')
edit('src/program/generate.cpp','            int64_t draft_offered = 0, draft_accepted = 0;','            if(strata::research::q4_early.enabled){strata::research::q4_early.begin_request();res_upload();}\n            int64_t draft_offered = 0, draft_accepted = 0;')
edit('src/program/generate.cpp','                tr("window", p, T);','                strata::research::q4_early.begin_window();\n                tr("window", p, T);')
edit('src/program/generate.cpp','                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;','                strata::research::q4_early.end_window(((rounds+1)%o.adapt_every)==0);\n                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;')
edit('src/program/generate.cpp','            static const bool state_hash = std::getenv("STRATA_STATE_HASH") != nullptr;','            if(strata::research::q4_early.enabled){apply_pending(true);strata::research::q4_early.finish();res_upload();}\n            static const bool state_hash = std::getenv("STRATA_STATE_HASH") != nullptr;')
print('PATCH Q4 early defaultOFF: one persistent staging-spare/device, no new device scratch, graph planner has no CUDA calls',flush=True)
