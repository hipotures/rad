"""Diagnostic Q4 H1/H4/H8 signals and selected exposed GPU wait phases."""
from pathlib import Path
import shutil,sys
C=Path(__file__).resolve().parents[1];R=C.parents[1];S=Path(sys.argv[1])
def edit(path,old,new,count=1):
 p=S/path;t=p.read_text();assert t.count(old)==count,(path,old[:100],t.count(old));p.write_text(t.replace(old,new,count))
# Starting source is the pinned previous full-window native-gate diagnostic.
header='include/strata/research/lab_gpu_router.hpp'
edit(header,'static constexpr std::array<int, 5> targets{13,20,33,40,46};','std::array<int, 5> targets{13,20,33,40,46};\n    int horizon=8;')
edit(header,'        enabled = flag && flag[0] == \'1\' && trace.enabled;','''        enabled = flag && flag[0] == '1' && trace.enabled;
        const char* h=std::getenv("STRATA_Q4_ROUTER_HORIZON");
        horizon=h?std::atoi(h):8;
        if(horizon!=1&&horizon!=4&&horizon!=8)throw std::runtime_error("Q4 diagnostic horizon must be1/4/8");
        for(size_t i=0;i<layers.size();++i)targets[i]=layers[i]+horizon;''')
edit(header,'only the frozen two-stage IQ3_S path is supported','only the frozen two-stage Qwen geometry is supported')
edit(header,'\\"horizons\\":[8]','\\"horizon_from_environment\\":true')
# Reuse the proven external-event instrumentation. No added synchronization.
shutil.copy2(R/'scripts/templates/lab_miss_waits.hpp',S/'include/strata/research/lab_miss_waits.hpp')
script=(R/'scripts/patch_miss_waits.py').read_text()
start=script.index("verify='src/core/verify.cpp'")
end=script.index('# Save one same-input head')
namespace={'edit':edit}
for path in ['src/core/verify.cpp','src/program/generate.cpp']:
 edit(path,'#include "strata/research/lab_trace.hpp"','#include "strata/research/lab_trace.hpp"\n#include "strata/research/lab_miss_waits.hpp"')
exec(script[start:end],namespace)
shutil.copy2(C/'scripts/templates/q4_copy_cost.hpp',S/'include/strata/research/q4_copy_cost.hpp')
for path in ['src/core/verify.cpp','src/program/generate.cpp']:
 edit(path,'#include "strata/research/lab_trace.hpp"','#include "strata/research/lab_trace.hpp"\n#include "strata/research/q4_copy_cost.hpp"')
edit('src/core/verify.cpp','    const WeightRef* wo = wt.find("output.weight");','    if (!strata::research::q4_copy_cost.configure(device_, err)) return false;\n    const WeightRef* wo = wt.find("output.weight");')
edit('src/program/generate.cpp','                strata::research::gpu_router.begin();','                strata::research::gpu_router.begin();\n                strata::research::q4_copy_cost.begin();')
edit('src/program/generate.cpp','            strata::research::gpu_router.flush();','            strata::research::gpu_router.flush();\n            strata::research::q4_copy_cost.flush();')
edit('src/program/generate.cpp','                const strata::core::OnDevice on(gs ? gs->dev : -1);\n                if (slot < 0 || b == nullptr ||',
     '                const strata::core::OnDevice on(gs ? gs->dev : -1);\n                const int q4_copy_index = slot >= 0 && b != nullptr ? strata::research::q4_copy_cost.start(gs ? gs->dev : 0, (int)s.layer, (int)s.in, (int)s.out, slot, strata::kernels::cpu::expert_layout().blob_bytes(s.layer), gs ? gs->adapt_stream : adapt_stream) : -1;\n                if (slot < 0 || b == nullptr ||')
edit('src/program/generate.cpp','                if (gs) gs->adapt_live = true;','                strata::research::q4_copy_cost.end(q4_copy_index, gs ? gs->adapt_stream : adapt_stream);\n                if (gs) gs->adapt_live = true;')
print('Q4-only diagnostic: causal native-gate horizons1/4/8;3 selected layers, no routing/cache/math changes',flush=True)
