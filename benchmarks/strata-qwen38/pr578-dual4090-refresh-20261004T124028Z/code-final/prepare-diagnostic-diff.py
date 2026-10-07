#!/usr/bin/env python3
"""Generate proposed boundary-only diff in memory; do not modify fresh clean checkouts."""
import pathlib,difflib
R=pathlib.Path(__file__).resolve().parent;repo=pathlib.Path('/srv/ai/strata-pr578-refresh-20261004-control')
oldpatch=(R/'git/boundary-debug-v0139-proposed.diff').read_text()
cpp_patch=oldpatch.split('+++ b/src/program/generate.cpp\n',1)[1]
startup=cpp_patch.split('@@',2)[2].split('\n@@',1)[0]
addition='\n'.join(line[1:] for line in startup.splitlines() if line.startswith('+'))+'\n'
files=['include/strata/core/remote_experts.hpp','src/program/generate.cpp'];chunks=[]
for relative in files:
 old=(repo/relative).read_text();new=old
 if relative.endswith('.hpp'):
  anchor='    int64_t resident() const { return cache_.resident(); }\n'
  new=new.replace(anchor,anchor+'    // Default-off benchmark boundary snapshots; no dispatch/policy changes.\n    int32_t benchmark_slot_of(int64_t l, int32_t e) const { return cache_.slot_of(l, e); }\n    int64_t benchmark_slots() const { return cache_.slots(); }\n',1)
 else:
  anchor='    // ---- Multi-GPU: the second GPU\'s expert tier, filled with the ranked pairs the primary does not hold\n'
  assert new.count(anchor)==1;new=new.replace(anchor,addition+anchor)
  anchor='            const int64_t req_hits = drive.d.cache_hits - decode_hits0;\n'
  assert new.count(anchor)==1;new=new.replace(anchor,'            if (benchmark_cache_debug && !benchmark_startup_only) benchmark_snapshot("request_end", &host_res);\n'+anchor)
  anchor='                const std::string pr = ver.profile_report();\n'
  # Match only the normal single-request decoder timing block, not batch mode.
  pos=new.index('strata decode timing: %lld windows');target=new.index(anchor,pos)
  counters='''                // Existing cumulative counters sampled after decode_ms; no hot-loop instrumentation.
                if (benchmark_cache_debug)
                    std::fprintf(stderr, "STRATA_BENCH_COUNTERS {\\"CPU_fallback_entries\\":%lld,\\"primary_expert_hits\\":%lld,\\"primary_pcie_experts\\":%lld,\\"CPU_missed_experts\\":%lld,\\"verify_windows\\":%lld,\\"layers\\":%lld,\\"CPU_activation_quant_ms\\":%.6f}\\n",
                                 (long long)(d1.entries - ds0.entries), (long long)(d1.hits - ds0.hits),
                                 (long long)(d1.pcie - ds0.pcie), (long long)(d1.misses - ds0.misses),
                                 (long long)dec_windows, (long long)g.n_layers, d1.actq - ds0.actq);
'''
  new=new[:target]+counters+new[target:]
 chunks.extend(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='a/'+relative,tofile='b/'+relative))
(R/'git/boundary-debug-v0139-proposed.diff').write_text(''.join(chunks))
