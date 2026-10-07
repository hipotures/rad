"""Minimal safe native adaptive-selector change; no early DMA, default OFF."""
from pathlib import Path
import shutil,sys
C=Path(__file__).resolve().parents[1];S=Path(sys.argv[1])
def edit(path,old,new,count=1,expected=None):
 p=S/path;t=p.read_text();assert t.count(old)==(count if expected is None else expected),(path,old[:90],t.count(old));p.write_text(t.replace(old,new,count))
(S/'include/strata/research').mkdir(exist_ok=True);shutil.copy2(C/'scripts/templates/q4_history_policy.hpp',S/'include/strata/research/q4_history_policy.hpp')
for path in ['src/core/expert_source.cpp','src/program/generate.cpp']:
 p=S/path;p.write_text('#include "strata/research/q4_history_policy.hpp"\n'+p.read_text())
edit('src/core/expert_source.cpp','    d.src->begin_layer(d.layers, ids, n_tok * k);','    strata::research::q4_history.observe(d.host_res,(int)d.layers,ids,(int)(n_tok*k));\n    d.src->begin_layer(d.layers, ids, n_tok * k);')
edit('src/program/generate.cpp','        Clock::time_point profile_saved_at = Clock::now();','''        if(strata::research::q4_history.enabled){
            if(!multi_gpu||stage_of(23)!=0||stage_of(24)!=1||o.pcie_frac!=.28)throw std::runtime_error("Q4 history requires frozen K24/PCIe0.28");
            std::vector<uint64_t> blobs;for(int l=0;l<g.n_layers;++l)blobs.push_back(strata::kernels::cpu::expert_layout().blob_bytes(l));
            strata::research::q4_history.configure(host_res.data(),(int)g.n_layers,(int)g.n_expert,blobs);
        }
        Clock::time_point profile_saved_at = Clock::now();''')
edit('src/program/generate.cpp','            std::vector<std::pair<float, int32_t>> cand, vict;\n            for (int64_t l = 0; l < g.n_layers; ++l) {','            std::vector<std::pair<float, int32_t>> cand, vict;\n            if(!(strata::research::q4_history.enabled&&strata::research::q4_history.active)){\n            for (int64_t l = 0; l < g.n_layers; ++l) {',expected=2)
edit('src/program/generate.cpp','            if ((int) swaps.size() > o.adapt_swaps) swaps.resize((size_t) o.adapt_swaps);','            if ((int) swaps.size() > o.adapt_swaps) swaps.resize((size_t) o.adapt_swaps);\n            }',expected=2)
edit('src/program/generate.cpp','            if (!resident_stage_swaps(src, xcache, host_res, g.n_expert, swaps, adapt_stream)) return false;', '''            if(strata::research::q4_history.enabled&&strata::research::q4_history.active)
                strata::research::q4_history.select(drive.d.usage,host_res,swaps,o.adapt_swaps);
            if (!resident_stage_swaps(src, xcache, host_res, g.n_expert, swaps, adapt_stream)) return false;''')
edit('src/program/generate.cpp','            int64_t draft_offered = 0, draft_accepted = 0;','            strata::research::q4_history.begin_request();\n            int64_t draft_offered = 0, draft_accepted = 0;')
edit('src/program/generate.cpp','                tr("window", p, T);','                strata::research::q4_history.begin_window();\n                tr("window", p, T);')
edit('src/program/generate.cpp','                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;', '                strata::research::q4_history.end_window();\n                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;')
edit('src/program/generate.cpp','            static const bool state_hash = std::getenv("STRATA_STATE_HASH") != nullptr;', '            strata::research::q4_history.finish();\n            static const bool state_hash = std::getenv("STRATA_STATE_HASH") != nullptr;')
print('PATCH Q4 history defaultOFF: persistent safe-boundary replacement, fixed bytes/capacities',flush=True)
