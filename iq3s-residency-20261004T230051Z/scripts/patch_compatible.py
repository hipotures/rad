"""Minimal opt-in compatible-slot serve adaptation on the frozen full-RAM path."""
import pathlib,shutil,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1]);p=src/'src/program/generate.cpp';s=p.read_text()
target=src/'include/strata/research';target.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'scripts/templates/compatible_policy.hpp',target/'compatible_policy.hpp')
def edit(old,new,count=1):
    global s
    if s.count(old)!=count:raise RuntimeError(f'Expected{count} anchors, got{s.count(old)}: {old[:100]}')
    s=s.replace(old,new,count)
edit('#include "strata/core/expert_cache.hpp"','#include "strata/core/expert_cache.hpp"\n#include "strata/research/compatible_policy.hpp"')
anchor='        // the VRAM tier follows the conversation (the same rule as the speculative loop below)'
edit(anchor,'''        const char* lab_policy_env = std::getenv("STRATA_LAB_COMPATIBLE");
        const bool lab_compatible = lab_policy_env && lab_policy_env[0] == '1';
        if (lab_compatible && (!multi_gpu || stages.size() != 1 || o.batch > 0 || o.vram_elastic ||
                              o.resident_cpu_experts || src.complement_ready() || o.mmap_experts ||
                              peer.valid() || remote_caches)) {
            std::fprintf(stderr, "strata lab compatible: requires exactly two sequential layer stages, full immutable RAM arena, no batch/elastic/resident/helper/peer mode\\n");
            return 2;
        }
        std::vector<uint64_t> lab_blob, lab_slots0, lab_slots1;
        if (lab_compatible) {
            for (int64_t l = 0; l < g.n_layers; ++l)
                lab_blob.push_back(strata::kernels::cpu::expert_layout().blob_bytes(l));
            for (int64_t slot = 0; slot < xcache.slots(); ++slot)
                lab_slots0.push_back((uint64_t)(xcache.bytes_of(slot + 1) - xcache.bytes_of(slot)));
            for (int64_t slot = 0; slot < stages[0]->cache.slots(); ++slot)
                lab_slots1.push_back((uint64_t)(stages[0]->cache.bytes_of(slot + 1) - stages[0]->cache.bytes_of(slot)));
            std::fprintf(stderr, "strata lab compatible: enabled; same-device fitting slots, original bytes and cadence; host slot metadata %zu bytes\\n", (lab_blob.size()+lab_slots0.size()+lab_slots1.size())*sizeof(uint64_t));
        }
'''+anchor)
old='            struct Swap { float gain; int32_t layer, in, out; };'
start=s.index('        auto adapt = [&]() -> bool {');end=s.index('        // #477: write the learned profile',start);section=s[start:end]
assert section.count(old)==1
section=section.replace(old,'            struct Swap { float gain; int32_t layer, in, out; int32_t out_layer = -1; };')
begin=section.index('            for (int64_t l = 0; l < g.n_layers; ++l) {')
finish=section.index('            if (!resident_stage_swaps(',begin)
original=section[begin:finish]
section=section[:begin]+'''            if (lab_compatible) {
                const auto picked = strata::research::select_compatible(drive.d.usage.data(), host_res.data(),
                    (int32_t)g.n_layers, (int32_t)g.n_expert, (int32_t)split_at[0], lab_blob, lab_slots0, lab_slots1, o.adapt_swaps);
                for (const auto& pick : picked)
                    swaps.push_back({(float)pick.gain, pick.layer, pick.in, pick.out, pick.out_layer});
            } else {
'''+original+'''            }
'''+section[finish:]
old='                const size_t in = (size_t) s.layer * g.n_expert + s.in, out = (size_t) s.layer * g.n_expert + s.out;'
assert section.count(old)==1
section=section.replace(old,'''                const int32_t out_layer = s.out_layer >= 0 ? s.out_layer : s.layer;
                const size_t in = (size_t) s.layer * g.n_expert + s.in, out = (size_t) out_layer * g.n_expert + s.out;''')
anchor='                const strata::core::OnDevice on(gs ? gs->dev : -1);'
assert section.count(anchor)==1
section=section.replace(anchor,'''                if (lab_compatible) {
                    const auto& cache = gs ? gs->cache : xcache;
                    if (stn != stage_of(out_layer) || slot < 0 || slot >= cache.slots() ||
                        lab_blob[(size_t)s.layer] > (uint64_t)(cache.bytes_of(slot + 1) - cache.bytes_of(slot))) {
                        std::fprintf(stderr, "strata lab compatible: invalid owner/slot-size invariant\\n");
                        return false;
                    }
                }
'''+anchor)
old='                srcp->prefetch(s.layer, s.out);'
assert section.count(old)==1;section=section.replace(old,'                srcp->prefetch(out_layer, s.out);')
s=s[:start]+section+s[end:];p.write_text(s)
print('Default-off same-device compatible-slot policy applied; tests and source safety audit required',flush=True)
