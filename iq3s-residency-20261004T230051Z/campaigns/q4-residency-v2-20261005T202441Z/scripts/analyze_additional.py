"""Held-out application confirmation and transaction diagnostics, separate from main medians."""
from campaign import C,load,save
from analyze_live import stats,phase_system,counters,pcie_samples,compare
import json,re,statistics

def independent():
    runs=[]
    for variant in ['control','history-v2','early-v1']:
        for rep in [1,2,3]:
            base=C/'independent'/variant/f'rep{rep}';record=load(base/'results.json');r=record['runs'][0]
            assert r['actual_engine_input_verified'] and r['reuse']==0
            ids=load(r['actual_output_ids_path']);assert len(ids)==r['actual_output_tokens']
            system,_=phase_system(r)
            runs.append({'variant':variant,'profile':'32k-total-limit/independent72-input','replicate':rep,'raw':str(base/'raw/run.json'),
                'performance':{k:r.get(k) for k in ['PP','TG','TTFT_s','wall_s','actual_input_tokens','actual_output_tokens','mtp_proposed','mtp_accepted','verify_windows','local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries','all_routed_entries','local_vram_share_all_pct','mtp_acceptance_pct']},
                'finish_reason':r['finish_reason'],'application_status':r['application_status'],'system':system,
                'counters':counters((base/'raw/run-engine.log').read_text()),'resource':load(base/'raw/resource-check.json'),
                'input_sha256':r['actual_engine_input']['sha256'],'output_ids_path':r['actual_output_ids_path'],'output_sha256':r['actual_output_ids_sha256'],'warmup':record['warmup']})
    assert len(runs)==9
    cells=[];pairs=[]
    for variant in ['control','history-v2','early-v1']:
        selected=[r for r in runs if r['variant']==variant]
        aggregate={key:stats([r['performance'].get(key) for r in selected]) for key in selected[0]['performance']}
        aggregate['CPU_VM_pct']=stats([r['system']['decode']['CPU_VM_pct']['mean'] for r in selected])
        cells.append({'variant':variant,'attempts':3,'fixed1024_valid':sum(r['performance']['actual_output_tokens']==1024 for r in selected),'stats':aggregate,'raw_paths':[r['raw'] for r in selected]})
        if variant=='control':continue
        for b in selected:
            a=next(r for r in runs if r['variant']=='control' and r['replicate']==b['replicate'])
            parity=compare(a,b);assert parity['same_input_ids']
            same_budget=a['performance']['actual_output_tokens']==b['performance']['actual_output_tokens']==1024
            pairs.append({'variant':variant,'replicate':b['replicate'],**parity,'same1024_output_budget_completed':same_budget,
                'ratios':{key:b['performance'][key]/a['performance'][key] for key in ['PP','TG','TTFT_s','wall_s']} if same_budget else None,
                'natural_EOS_policy':'No continuation rewrite; stopped application latency retained separately if budgets incomplete.'})
    ratios=[]
    for variant in ['history-v2','early-v1']:
        selected=[x for x in pairs if x['variant']==variant and x['ratios']]
        ratios.append({'variant':variant,'n':len(selected),'ratios':{key:stats([x['ratios'][key] for x in selected]) for key in ['TG','wall_s','TTFT_s','PP']}})
    summary={'state':'COMPLETE','workload':'hold-code; whole task excluded from development/calibration','input_tokens':72,
        'context_limit':32768,'output_budget':1024,'cells':cells,'runs':runs,'paired':pairs,'paired_ratios':ratios,
        'limitation':'Independent short-input application confirmation. It does not establish long-document, Polish, translation or universal domain generalization.'}
    save(C/'phase-c/independent-summary.json',summary)
    print('INDEPENDENT',json.dumps(ratios,indent=2))

def diagnostics():
    results=[]
    for variant in ['early-diagnostic','early-reactive-diagnostic']:
        base=C/'diagnostics'/variant/'32k';result=load(base/'results.json');r=result['runs'][0]
        events=[json.loads(line) for line in (base/'early-events-request2.jsonl').read_text().splitlines()]
        text=(base/'raw/run-engine.log').read_text();counts=counters(text)['Q4_EARLY'];assert counts
        publications=[e for e in events if e['published_ns']]
        assert all(0<e['issue_ns']<=e['copy_begin_ns']<=e['copy_end_ns']<=e['published_ns'] and e['victim']!=e['incoming'] for e in publications)
        readbacks=[int(x) for x in re.findall(r'Q4_EARLY_READBACK PASS checks=(\d+)',text)]
        assert readbacks and sum(readbacks)>0
        uses=sum(e['uses'] for e in events);victim_absent=sum(e['victim_entries'] for e in events)
        issued_bytes=len(events)*3072000;assert issued_bytes==counts['bytes'] and len(events)==counts['issued']
        classified={key:sum(e['classification']==key for e in events) for key in {e['classification'] for e in events}}
        result={'variant':variant,'raw':str(base/'raw/run.json'),'events':str(base/'early-events-request2.jsonl'),
            'prediction_enabled':'reactive' not in variant,'diagnostic_only':True,'input_sha256':r['actual_engine_input']['sha256'],
            'issued':len(events),'published':len(publications),'issued_GB':issued_bytes/1e9,'published_GB':len(publications)*3072000/1e9,
            'unpublished_GB':(len(events)-len(publications))*3072000/1e9,'classes':classified,
            'observed_local_entries_after_admission':uses,'entries_after_initial_target':uses-counts['target_entries'],
            'admissions_with_more_than4_uses':sum(e['uses']>4 for e in publications),
            'victim_absent_entries_descriptive':victim_absent,'publication_order_pass':True,'readback_checks':sum(readbacks),
            'issue_to_copy_begin_ms':stats([(e['copy_begin_ns']-e['issue_ns'])/1e6 for e in events if e['copy_begin_ns']]),
            'copy_span_ms':stats([(e['copy_end_ns']-e['copy_begin_ns'])/1e6 for e in events if e['copy_end_ns']]),
            'copy_end_to_publication_ms':stats([(e['published_ns']-e['copy_end_ns'])/1e6 for e in publications]),
            'runtime_aggregates':counts,'observed_TG_not_headline':r['TG'],'performance':{key:r[key] for key in ['PP','TG','TTFT_s','wall_s','cpu_fallback_entries','nonlocal_gpu_entries','local_vram_share_all_pct','mtp_acceptance_pct']},
            'warmup_input_hash':result['warmup']['actual_engine_input']['sha256'],
            'warmup_output_hash':result['warmup']['actual_output_ids_sha256'],
            'resource':load(base/'raw/resource-check.json'),
            'charged_spare_withdrawals':re.findall(r'Q4_EARLY_RESERVE[^\n]+',text),
            'initial_spare_victim_demand_entries':None,
            'causality':'Prediction-enabled publication is ready before original target plan release. Reactive issues after original demand; a later target-ready classification does not make it prefetch of original demand.',
            'limitations':['Readbacks capped16/request; exact promoted bytes verified, not full-model logits equivalence.',
                'Use/absence counters follow last observed admission/absence. Unobserved native eviction/readmission can affect attribution; no exclusive victim latency claim.',
                'Transaction victim counters exclude the two initial spare withdrawals. Their total demand cost is reflected in full request performance/routing, but not separately instrumented; it is unavailable, not zero.',
                'Equal warmup inputs/output budgets and scheduler capacities do not imply identical warmed cache sets when ON execution diverges; warmup output hashes and resource checks are retained.',
                'More than4 local uses implies a later-window use with T<=4, not proof of uninterrupted lifetime.',
                'End-of-request right censoring and sampled host timestamps; no exact first-demand GPU timestamp.',
                'Diagnostics include buffered events/readbacks; no headlineTG or statistically established ablation speedup from one run.']}
        results.append(result)
    assert results[0]['input_sha256']==results[1]['input_sha256']
    save(C/'phase-c/prediction-ablation.json',results)
    print('DIAGNOSTIC_ABLATION',json.dumps([{k:r[k] for k in ['variant','issued','published','issued_GB','unpublished_GB','observed_local_entries_after_admission','victim_absent_entries_descriptive']} for r in results],indent=2))

if __name__=='__main__':independent();diagnostics()
