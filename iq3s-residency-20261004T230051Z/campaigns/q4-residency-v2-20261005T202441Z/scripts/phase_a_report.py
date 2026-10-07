"""Phase A decision gate, based on completed preserved Q4 evidence only."""
import json, datetime, xml.etree.ElementTree as ET
from pathlib import Path
from campaign import C, R, load, save, status
def main():
    validation=load(C/'phase-a/trace-validation.json');assert len(validation)==9
    assert all(x['validation']['state']=='PASS' and x['current_selector']['state']=='PASS' for x in validation)
    costs=load(C/'phase-a/cost-analysis.json')
    costs=[x for x in costs if '/cost-h8/' in x['result'] and x['result'].endswith('run1/results.json')]
    assert len(costs)==3,'Complete Q4 contended costs at all context profiles first'
    test=ET.parse(C/'analysis/cost-router-tests/junit.xml').getroot()
    failures=[n.attrib['name'] for n in test.iter('testcase') if n.find('failure') is not None]
    assert set(failures)=={'ple_parity','platform_memory_test','expert_parity','pool_test'},failures
    control=load(C/'raw/control/256k/rep1/results.json')['runs'][0]
    rows=[];refs=[]
    for profile in ['32k','128k','256k']:
        root=C/'traces/diagnostic'/profile/f'{profile}-run1'
        v=load(root/'trace-validation.json');a=load(root/'observed-admissions.json');parity=load(root/'original-parity.json')
        assert all(parity[k] for k in ['input_hash_equal','output_ids_identical','MTP_aggregate_equal','routing_aggregate_equal'])
        current=load(C/'analysis/references'/profile/'6.8/current.json')
        assert current['nonlocal_entries']==v['path_counts']['-1']+v['path_counts']['1']+v['path_counts']['2']
        assert current['promotion_bytes']==v['promotion_bytes'] and current['promotions']==v['promotions']
        observed=load(root/'results.json')['runs'][0]
        rows.append({'context':profile,'actual_input':observed['actual_input_tokens'],'all_entries':v['demand_entries'],
                     'CPU_entries':v['path_counts']['-1'],'mapped_entries':v['path_counts']['1']+v['path_counts']['2'],
                     'local_pct':v['all_demand_local_hit_pct'],'promotions':v['promotions'],'promotion_GB':v['promotion_bytes']/1e9,
                     'unused_GB':a['unused_bytes']/1e9,'victim_entries':a['victim_entries_while_absent'],
                     'capacities':v['gpu_budgets'],'replay_current_verified':True})
        for path in sorted((C/'analysis/references'/profile).glob('*/*.json')):
            r=load(path);refs.append({k:r[k] for k in ['policy','rate_GB_s','nonlocal_entries','promotion_bytes','modeled_pending_wait_s'] }|{'context':profile,'path':str(path),'queue_model':r.get('queue_model','shared staged link')})
    summary={'status':'COMPLETE_MIXED','rows':rows,'references':refs,'costs':[x['result'] for x in costs],
             'decision':'PROCEED_PHASE_B','fresh256_original_control':control,
             'limitations':['Headroom references are not throughput predictions or proven optima',
                  'Detailed costs are diagnostic, with native router/events overhead excluded from headline speed',
                  'Compilation overlapped part of the first buffered128K trace; exact parity valid, its time excluded',
                  'Existing shared expert-profile.bin and MTP are frozen Q4 campaign inputs, not claimed Q4-exclusive training',
                  'Six1024-token short independent tasks limit generalization and censored-future label coverage']}
    save(C/'phase-a/summary.json',summary)
    text=['# Phase A — Q4 ground truth, costs and headroom','',
          '**COMPLETE_MIXED — proceed to causal Phase B.** All nine new Q4 traces reconcile every routed entry, exact physical slot class, issue/publication and current-selector ordering. All three long traces match the original frozen executable in input/output integer IDs, MTP aggregates and routing. Current replay matches observed nonlocal counts and copy bytes; no simulator-only TG is claimed.','',
          '|Context|Actual input|All-demand local %|CPU entries|Mapped entries|Promotions|Promotion GB|Unused GB*|Victim entries*|',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in rows:text.append(f"|{r['context']}|{r['actual_input']}|{r['local_pct']:.2f}|{r['CPU_entries']}|{r['mapped_entries']}|{r['promotions']}|{r['promotion_GB']:.2f}|{r['unused_GB']:.2f}|{r['victim_entries']}|")
    text+=['','*Unused near the end is right-censored; victim entries describe observed absence after the latest eviction, not a proven latency penalty. Every incoming promotion is immutable native Q4 data, retained without copying back to RAM. Most incoming experts are reused, but rapid changing demand exposes eviction damage.','',
           '## Fixed bytes and ownership','',
           '77,017,907,200 bytes /71.73GiB routed RAM arena,48×512 experts. Native blob classes:3,072,000bytes Q4_K/Q5_1;3,584,000bytes Q4_K/Q8_0;3,993,600bytes Q5_K/Q8_0. K24 fixes GPU ownership. Each original physical slot class is retained; no two-GPU virtual pool, size-only victim packing or added VRAM capacity. Full exact budgets are in summary.json and trace files. Expert file reads during decode are zero; mapped RAM and PCIe work are not SSD streaming.','',
           '## References and limitations','',
           '|Context|Reference|Queue|GB/s|Nonlocal entries|Promotion GB|Modeled join wait s|','|---|---|---|---:|---:|---:|---:|']
    for r in refs:text.append(f"|{r['context']}|{r['policy']}|{r['queue_model']}|{r['rate_GB_s'] if r['rate_GB_s'] else 'relaxed'}|{r['nonlocal_entries']}|{r['promotion_bytes']/1e9:.2f}|{r['modeled_pending_wait_s']:.3f}|")
    text+=['','The capacity-only reference relaxes timing and copy issue restrictions. The future next-use schedule charges serialized per-device/shared-link queues, victim withdrawal and next-window publication, but keeps observed nonpromotion work fixed. It is feasible within that modeled queue, not an optimum or hardware latency oracle.1.8GB/s is a conservative interference scenario,6.8GB/s the existing staged-expert envelope,12.6GB/s an isolated optimistic pinned limit. Newly measured contended copies below refine rather than replace these sensitivity cases.','',
           'The narrow32MiB/device forecast reference misses more despite strong future knowledge: insufficient replenishment makes a poor heuristic, not a proof that prediction cannot help. The wide160MiB/device/96-exchange reference also has limitations from a short4-window objective. Phase B must score longer resident utility/victim reuse rather than equate gate probability with net benefit.','',
           'New Q4 copy spans support approximately13.2GB/s per device for the existing pinned adaptive batch. A parallel per-device reference retains the staged sensitivity cases: original current joins model3.055/3.641/3.409s versus observed3.269/3.863/3.615s at32/128/256K (about6–7% lower). Issue overhead, synchronization and publication remain incompletely modeled. This is a useful queue validation, not a fitted throughput model. An earlier scheduler using a separate pinned staging buffer must charge CPU staging too; it cannot assume the direct pinned-batch rate for free.','',
           '## Selected exposed costs','',
           'The three-layer GPU event sample reports resident computation, mapped execution and exposed CPU-done wait separately. Phase0 also includes host-plan wait and mapped activation copy; phase3 can overlap upstream CPU execution. They are never added or multiplied by48. Exact sample distributions and conditional CPU-positive versus all-local-or-mapped results are in cost-analysis.json.','']
    for x in costs:
        profile=Path(x['result']).parents[1].name
        text.append(f"### {profile}\n\nNative router pilot targets {x['covered_target_layers']}, same-window membership {x['same_window_membership_pct']:.2f}%, next-window target-demand coverage {x['next_window_covered_target_demand_pct']:.2f}%. Five of48 layers only; raw gate confidence is not calibrated future demand. GPU gate/top10 span median {x['router_cost_gpu_ms']['median']:.5f}ms. Original-target host lead median {x['causal_host_lead_ms']['median']:.4f}ms, not an exact GPU demand deadline. Actual adaptive copies issue after verification, so current-window target lead does not make them early prefetch.\n")
        for r in x['copy_costs']:
            if r['gpu_duration_ms']:text.append(f"- GPU{r['device']} {r['bytes']}bytes: sampled copy median {r['gpu_duration_ms']['median']:.4f}ms, median effective {r['effective_GB_s']['median']:.2f}GB/s; host enqueue median {r['host_enqueue_ms']['median']:.4f}ms.")
        text.append('')
    text+=['## Correctness and baseline scope','',
           'Diagnostic build source8d542977631b6f015115ed1f09acc1c336070ab8, binaryc5f39fb7bba7ce9113d122c787414f654d0db0073c997a6ad61c82331ea3af84. Native suite62pass,2skip,4known previous fixture/environment failures: ple_parity,platform_memory_test,expert_parity,pool_test. Full errors are preserved; this is not a falsely green suite. Relevant native Q4_K/Q5_1,Q4_K/Q8_0,Q5_K/Q8_0 and pool/router/cache tests pass.','',
           'The practical control remains the original eca9d0d... executable, source6f32ec0...,0.1.39, K24/.28,100us,15workers,spec4/min-p0.5,INT8,kv-resident32768,prefillauto,suffix/reuseOFF. Fresh64-output warmups do not fully warm full-length prefill: this protocol intentionally differs from the old one-server/three-request Q4 campaign. Reused latest pool controls32/128 are compatible; a new original256K run was collected before compiling. Preserve this chronology in final paired interpretation.','',
           '## Primary references and branch plan','',
           '[Open-Jev](https://github.com/Zefan-Cai/Open-Jev) pinnedbd411888...,MIT: independent discriminative candidate scoring with LoRA/backbone; our numeric count models are Expert-Jev-inspired, not its checkpoint. [Basal](https://github.com/rkinas/basal) pinnedc3cab778...,Apache2: typed decisions/shared state; EagerBackend CPU run_shared actually flattens full forwards, so efficient CPU SOAM cannot be assumed. [Fate](https://arxiv.org/abs/2502.12224) and [SpecMD/Least-Stale](https://arxiv.org/abs/2602.03921) pinned originalv1 HTML: inspect exact stale/prefetch semantics before claiming reproduction. Borrowed code/license manifests remain under sources/.','',
           'Meaningful expensive miss/transfer/churn headroom remains plausible. Proceed with bounded cheap history/Markov/stale, native router H1/H4/H8, required local linear/32-unit MLP and temporal scorer, then hybrid. Incoming and victim expected demand are scored together. Basal is optional and needs a bounded semantic-to-Q4-demand hypothesis; do not download a large checkpoint by default. No live residency policy has been enabled at this gate.']
    (C/'phase-a/report.md').write_text('\n'.join(text)+'\n')
    record={'id':'E030-q4-ground-truth','status':'COMPLETE_MIXED','campaign':str(C),'report':str(C/'phase-a/report.md'),
            'decision':'PROCEED_PHASE_B','utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    for ledger in [C/'ledger.jsonl',R/'experiments.jsonl']:
        existing=[json.loads(x) for x in ledger.read_text().splitlines()]
        if not any(r.get('id')==record['id'] and r.get('status')==record['status'] for r in existing):
            with ledger.open('a') as f:f.write(json.dumps(record)+'\n')
    status('RUNNING',phase='B',running='bounded CPU-only learned and causal replay',next_exact_action='Train required linear/MLP/temporal on dev only, calibrate separately, compare held-out net exchanges')
    print('PHASE_A_COMPLETE',flush=True)
if __name__=='__main__':main()
