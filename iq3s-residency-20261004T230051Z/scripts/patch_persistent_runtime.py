"""Default-off persistent router admission on the frozen two-stage full-arena path."""
import pathlib,shutil,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1]);subprocess.run([sys.executable,str(ROOT/'scripts/patch_compatible.py'),str(src)],check=True)
dest=src/'include/strata/research';shutil.copy2(ROOT/'scripts/templates/persistent_policy.hpp',dest/'persistent_policy.hpp');shutil.copy2(ROOT/'scripts/templates/persistent_runtime.hpp',dest/'persistent_runtime.hpp');(dest/'compatible_policy.hpp').unlink()
def edit(path,old,new,count=1):
 p=src/path;s=p.read_text();assert s.count(old)==count,(path,s.count(old),old[:100]);p.write_text(s.replace(old,new,count))
path='src/program/generate.cpp';p=src/path;s=p.read_text().replace('strata/research/compatible_policy.hpp','strata/research/persistent_runtime.hpp').replace('STRATA_LAB_COMPATIBLE','STRATA_LAB_PERSISTENT');s=s.replace('lab_compatible','lab_persistent').replace('strata lab compatible:','strata persistent:');p.write_text(s)
# Registration precedes adapt but window count is global to the process.
edit(path,'        // the VRAM tier follows the conversation (the same rule as the speculative loop below)', '''        auto& persistent = strata::research::persistent;
        strata::research::PersistentConfig persistent_cfg;
        persistent_cfg.prediction_weight = 1.0f; // frozen development selection before full trace ranking
        if (lab_persistent && (o.spec != 4 || o.adapt_every != 4 || o.adapt_swaps != 96 || o.adapt_decay != .7 ||
                               o.spec_split || o.prompt_cache != 0 || o.suffix_draft != 0 || adapt_nowait())) {
            std::fprintf(stderr, "strata persistent: requires frozen serial spec4/cadence4/decay.7/swaps96, lookup/reuse OFF, blocking publication\\n");
            return 2;
        }
        // the VRAM tier follows the conversation (the same rule as the speculative loop below)''')
old='''                const auto picked = strata::research::select_compatible(drive.d.usage.data(), host_res.data(),
                    (int32_t)g.n_layers, (int32_t)g.n_expert, (int32_t)split_at[0], lab_blob, lab_slots0, lab_slots1, o.adapt_swaps);
                for (const auto& pick : picked)
                    swaps.push_back({(float)pick.gain, pick.layer, pick.in, pick.out, pick.out_layer});'''
new='''                const auto selection_begin = strata::research::persistent_ns();
                if (!persistent.validate(host_res, lab_blob, lab_slots0, lab_slots1)) {
                    std::fprintf(stderr, "strata persistent: duplicate owner or physical byte capacity before selection\\n"); return false;
                }
                const auto picked = strata::research::select_persistent(drive.d.usage.data(), persistent.prediction.data(),
                    persistent.last.data(), persistent.born.data(), host_res.data(),
                    (int32_t)g.n_layers, (int32_t)g.n_expert, (int32_t)split_at[0], lab_blob, lab_slots0, lab_slots1,
                    persistent.window, o.adapt_swaps, persistent_cfg);
                persistent.select_ns += strata::research::persistent_ns() - selection_begin;
                for (const auto& pick : picked)
                    swaps.push_back({(float)pick.utility_us, pick.layer, pick.in, pick.out, pick.out_layer});'''
edit(path,old,new)
# Only the serve adaptation region, leave other modes unchanged.
p=src/path;s=p.read_text();start=s.index('        auto adapt = [&]() -> bool {');end=s.index('        // #477: write the learned profile',start);section=s[start:end]
anchor='                host_res[out] = strata::core::kNotResident;   // evicted now: the CPU computes it meanwhile';assert section.count(anchor)==1
section=section.replace(anchor,'                if (lab_persistent) persistent.issue(s.layer, s.in, out_layer, s.out, slot, lab_blob[(size_t)s.layer]);\n'+anchor)
anchor='            for (float& v : drive.d.usage) v *= o.adapt_decay;';assert section.count(anchor)==1
section=section.replace(anchor,'            if (lab_persistent) persistent.decay(o.adapt_decay);\n'+anchor)
s=s[:start]+section+s[end:];p.write_text(s)
# Publication is after ALL device events and before res_upload. Use fully qualified ref before local alias.
old='''            src.commit_exchanges();   // the resident RAM mode: the evicted experts take their places in RAM
            for (const auto& [i, slot] : pending) {
                host_res[(size_t) i] = slot;'''
edit(path,old,'''            src.commit_exchanges();   // the resident RAM mode: the evicted experts take their places in RAM
            for (const auto& [i, slot] : pending) {
                strata::research::persistent.publish(i, slot);
                host_res[(size_t) i] = slot;''',count=2)
edit(path,'            const int64_t decode_hits0 = drive.d.cache_hits;','            persistent.begin();\n            const int64_t decode_hits0 = drive.d.cache_hits;')
edit(path,'                apply_pending(!adapt_nowait());','''                const uint64_t persistent_pending_begin = lab_persistent ? strata::research::persistent_ns() : 0;
                persistent.window = (uint64_t)rounds;
                apply_pending(!adapt_nowait());
                if (lab_persistent) persistent.pending_wait_ns += strata::research::persistent_ns() - persistent_pending_begin;''')
edit(path,'            const double decode_ms = std::chrono::duration<double, std::milli>(Clock::now() - d0).count();','            const double decode_ms = std::chrono::duration<double, std::milli>(Clock::now() - d0).count();\n            persistent.finish();')
for f in ['src/core/verify.cpp','src/core/expert_source.cpp']:
 key='#include "strata/core/'+('verify.hpp' if 'verify.cpp' in f else 'expert_source.hpp')+'"';edit(f,key,key+'\n#include "strata/research/persistent_runtime.hpp"')
edit('src/core/verify.cpp','    const WeightRef* wo = wt.find("output.weight");','    if (!strata::research::persistent.configure(wt, g, device_, (int)lb_, (int)le_, err)) return false;\n    const WeightRef* wo = wt.find("output.weight");')
edit('src/core/verify.cpp','    static const bool dec_batch = [] { const char* v = std::getenv("STRATA_DEC_BATCH");','    if (strata::research::persistent.enabled && (G != 1 || batch_rec_)) { err = "persistent: serial one-group windows only"; return false; }\n    static const bool dec_batch = [] { const char* v = std::getenv("STRATA_DEC_BATCH");')
edit('src/core/verify.cpp','        if (all_resident_) {\n            resident_plan(','        strata::research::persistent.score((int)l, n, xm, logits_ + tb * NE, cs);\n        if (all_resident_) {\n            resident_plan(')
edit('src/core/expert_source.cpp','    pt("begin");\n    d.src->begin_layer','    strata::research::persistent.observe((int)d.layers, (int)n_tok, ids, d.host_res);\n    pt("begin");\n    d.src->begin_layer')
print('Persistent runtime: same owner/bytes, original async backend, defaultOFF, frozen alpha1, h8signal',flush=True)
