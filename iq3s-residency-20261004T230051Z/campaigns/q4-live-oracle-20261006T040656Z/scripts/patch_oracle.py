"""Full-scope oracle on the proven fixed-work substrate; no default algorithm changes."""
from pathlib import Path
import sys
C=Path(__file__).resolve().parents[1];S=Path(sys.argv[1]);(S/'include/strata/research/q4_oracle.hpp').write_text((C/'scripts/oracle_header.txt').read_text())
def replace(f,old,new,count=1):
 p=S/f;t=p.read_text();assert t.count(old)>=count,(f,old[:120],t.count(old));p.write_text(t.replace(old,new,count))
for f in ['src/program/generate.cpp','src/core/expert_source.cpp']:
 p=S/f;p.write_text('#include "strata/research/q4_oracle.hpp"\n'+p.read_text())
replace('src/program/generate.cpp','    strata::research::q4_tape.configure();','    strata::research::q4_tape.configure();\n    strata::research::q4_oracle.configure();')
replace('src/program/generate.cpp','        Clock::time_point profile_saved_at = Clock::now();','''        if(strata::research::q4_oracle.configured){
            if(!multi_gpu||stages.size()!=1||stage_of(23)!=0||stage_of(24)!=1||o.pcie_frac!=.28||o.batch>0||o.resident_budget>0||dynamic_cast<strata::core::ArenaExpertSource*>(srcp)==nullptr)throw std::runtime_error("Oracle requires frozen full-arena serial K24/PCIe0.28");
            std::vector<uint64_t> blobs;for(int l=0;l<g.n_layers;++l)blobs.push_back(strata::kernels::cpu::expert_layout().blob_bytes(l));
            strata::research::q4_oracle.runtime(host_res.data(),drive.d.usage.data(),std::move(blobs),{d_res,stages[0]->d_res},
                [&](int l,int e){return srcp->blob(l,e);},[&](int dev,int slot)->void*{return dev?stages[0]->cache.device_slot(slot):xcache.device_slot(slot);});
        }
        Clock::time_point profile_saved_at = Clock::now();''')
replace('src/program/generate.cpp','        auto adapt = [&]() -> bool {\n            if (!pending.empty())','        auto adapt = [&]() -> bool {\n            if(strata::research::q4_oracle.active){for(float& v:drive.d.usage)v*=o.adapt_decay;return true;}\n            if (!pending.empty())')
replace('src/program/generate.cpp','            const Clock::time_point d0 = Clock::now();\n            // STRATA_DECODE_TIMING','            const Clock::time_point d0 = Clock::now();\n            strata::research::q4_oracle.begin();\n            // STRATA_DECODE_TIMING')
replace('src/program/generate.cpp','            strata::research::q4_tape.finish(produced_n,cancelled);','            if(strata::research::q4_oracle.tracked){apply_pending(true);strata::research::q4_oracle.finish();}\n            strata::research::q4_tape.finish(produced_n,cancelled);')
replace('src/program/generate.cpp','                host_res[(size_t) i] = slot;\n                srcp->release','                strata::research::q4_oracle.native_ready((int)i/(int)g.n_expert,(int)i%(int)g.n_expert);\n                host_res[(size_t) i] = slot;\n                srcp->release')
replace('src/program/generate.cpp','                if (gs) gs->adapt_live = true;','                strata::research::q4_oracle.note_native((int)s.layer,(int)s.in,(int)s.out,slot,strata::kernels::cpu::expert_layout().blob_bytes(s.layer));\n                if (gs) gs->adapt_live = true;')
replace('src/core/expert_source.cpp','    d.src->begin_layer(d.layers, ids, n_tok * k);\n    pt("begun");','    strata::research::q4_oracle.host((int)d.layers,ids,(int)(n_tok*k));\n    d.src->begin_layer(d.layers, ids, n_tok * k);\n    pt("begun");')
replace('src/core/expert_source.cpp','    bool any_cpu = false;\n    for (int64_t i = 0; i < n; ++i)','    strata::research::q4_oracle.observe_plan((int)d.layers,ids,(int)n,kind);\n    bool any_cpu = false;\n    for (int64_t i = 0; i < n; ++i)')
replace('src/core/expert_source.cpp','    const auto c4 = std::chrono::steady_clock::now();\n    pt("ran");','    const auto c4 = std::chrono::steady_clock::now();\n    strata::research::q4_oracle.observe_cpu();\n    pt("ran");')
print('PATCH_ORACLE_V1',S,flush=True)
