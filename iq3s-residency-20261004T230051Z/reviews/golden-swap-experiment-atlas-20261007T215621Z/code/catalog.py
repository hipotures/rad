"""Inventory all relevant campaign results; freeze representative detail selection by identity."""
from pathlib import Path
import re
from common import *

INCLUSION = {
    'q4-multigpu': 'Original Q4 capacity, K24 ownership and runtime characterization; aggregate measurements only.',
    'q4-pool-spin': 'Contemporary ordinary pool-100us baseline and repeatability context; aggregate only.',
    'q4-residency-v2': 'Native Q4 demand traces, history/early admission, modeled future-feasible and capacity-free references.',
    'q4-conditional-admission': 'Pre-staging rejection and persistent-copy funnel; natural ON/OFF work may diverge.',
    'q4-live-oracle': 'First full-work live record/replay with future demand, real transfers and five charged spares.',
    'q4-oracle-decomposition': 'Matched incoming/victim information restrictions; E64 is routed invocations, I/V are windows.',
    'golden-swap-phase0': 'Twelve natural corpus recordings with initial state and native service journals.',
    'golden-swap-phase1': 'Frozen victim prediction, ranking metrics and unprotected admission lifetimes.',
    'golden-swap-phase2': 'First-use control, matched history/logistic, OFF/ON and independent finite-tail tapes.',
    'golden-swap-phase3': 'Planner memoization and corrected publication chronology; history/TC fixed.',
    'golden-swap-phase4-publication-wait': 'Eight retained CONTROL/TRACE requests; symmetric perturbation gate failed.',
}

def scalar(row, *keys):
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return None

def normalize(c, row, source, label=None):
    p = row.get('performance', row)
    own = row.get('ownership', {}) if isinstance(row.get('ownership'), dict) else {}
    f = row.get('fidelity', {}) if isinstance(row.get('fidelity'), dict) else {}
    d = row.get('demand', own.get('demand', {}))
    copies = row.get('copy', own.get('copies', row.get('copies', {})))
    task = scalar(row,'task','task_id','profile','context') or 'unknown'
    policy = scalar(row,'arm','policy','variant','method') or 'unknown'
    attempt = scalar(row,'block','attempt','replicate','run') or 1
    label = label or row.get('label') or f'{task}-{policy}-{attempt}'
    count = scalar(row,'windows') or scalar(p,'verify_windows') or f.get('windows')
    if count is None and row.get('main_events') is not None:
        count = row['main_events']//48
    local = scalar(row,'local','local_entries')
    cpu = scalar(row,'cpu','cpu_entries','CPU_entries')
    mapped = scalar(row,'mapped','mapped_entries')
    local = local if local is not None else scalar(d,'local')
    cpu = cpu if cpu is not None else scalar(d,'cpu')
    mapped = mapped if mapped is not None else scalar(d,'mapped')
    local = local if local is not None else scalar(p,'local_vram_entries')
    cpu = cpu if cpu is not None else scalar(p,'cpu_fallback_entries')
    mapped = mapped if mapped is not None else scalar(p,'nonlocal_gpu_entries')
    return {'id':id_for(c.name,label),'campaign':c.name,'date':c.name.split('-2026')[-1] if '-2026' in c.name else '20261005',
            'task':task,'policy':policy,'label':label,'attempt':attempt,
            'profile':scalar(row,'profile','context'),'context':row.get('context_limit'),
            'input':scalar(row,'actual_input_tokens','actual_input','input') or scalar(p,'actual_input_tokens'),
            'output':scalar(row,'emitted_tokens','recorded_output','output_tokens','output') or scalar(p,'actual_output_tokens') or f.get('emitted_tokens'),
            'windows':count,'local':local,'cpu':cpu,'mapped':mapped,
            'local_pct':scalar(row,'local_pct') or scalar(p,'local_vram_share_all_pct'),
            'decode_s':scalar(p,'decode_s'),'wall_s':scalar(p,'wall_s','request_wall_s'),
            'tok_s':scalar(p,'tok_s','TG','replay_equivalent_tok_s'),
            'copy_bytes':int(row['copy_GB']*1e9) if row.get('copy_GB') is not None else scalar(copies,'completed_bytes'),
            'promotions':scalar(copies,'issued','native_issued') or scalar(row,'issued'),
            'evictions':None,'resident_slots':None,'future':policy not in ['REPLAY_CURRENT','control','100us','layer-split','NATURAL_CURRENT'],
            'source_sha':scalar(row,'source_sha','source_SHA'),'binary_sha256':row.get('binary_sha256'),
            'model':'Qwen3.8-Flash-Next UD-Q4_K_XL','model_revision':'38bb39ee97821de2c9009abb7e93950eec396e66',
            'work_sha256':scalar(row,'work_sha256') or f.get('work_sha256'),
            'valid':row.get('valid',row.get('state','VALID') in ['VALID','PASS','COMPLETED']),
            'evidence_quality':'aggregate; chronological detail selection pending','source_result':str(source.relative_to(REPO)),
            'source_group':task,'detail':False,'kind':'MEASURED','summary_record':{
                **{k:v for k,v in row.items() if isinstance(v,(str,int,float,bool)) or v is None},
                **{k:row[k] for k in ['copy','tc','transactions','scorer','score','planner','information'] if isinstance(row.get(k),dict)}},
            'report':str((c/'report.md').relative_to(REPO))}

def discover():
    runs, experiments, sources = [], [], []
    def add(c, rows, p):
        sources.append(reference(p))
        for row in rows: runs.append(normalize(c,row,p))
    for prefix, reason in INCLUSION.items():
        c=campaign(prefix)
        experiments.append({'id':c.name,'title':prefix,'reason':reason,'report':str((c/'report.md').relative_to(REPO)),
                            'report_sha256':digest(c/'report.md')})
        if prefix in ['q4-multigpu','q4-pool-spin','q4-live-oracle']:
            p=c/'summary.json';a=load(p);add(c,a.get('runs',a.get('rows')),p)
        elif prefix=='q4-residency-v2':
            p=c/'analysis/live-run-details.json';add(c,load(p),p)
        elif prefix=='q4-conditional-admission':
            p=c/'analysis/live-records.json';add(c,load(p),p)
        elif prefix=='q4-oracle-decomposition':
            for rel in ['phase-c/32k-summary.json','phase-d/summary.json','phase-c/independent-summary.json']:
                p=c/rel
                if p.exists():add(c,load(p)['rows'],p)
            # Transfer rows are also retained as individual verified oracle journals.
            known={r['label'] for r in runs if r['campaign']==c.name}
            for p in sorted((c/'raw').glob('v2-*/results.json')):
                if p.parent.name in known:continue
                a=load(p);row=a['runs'][0] if a.get('runs') else a
                row.update(label=p.parent.name,task='code-source-'+('128k' if '128k' in p.parent.name else '256k'),
                           arm=p.parent.name.split('-')[2],attempt=int(p.parent.name[-1]) if p.parent.name[-1].isdigit() else 1)
                add(c,[row],p)
        elif prefix=='golden-swap-phase0':
            manifest=load(c/'benchmark-manifest.json')
            for task in manifest['tasks']:
                p=c/'raw'/task['task_id']/'episode.json'
                if not p.exists():continue
                a=load(p);row=a['run'];row.update(task=task['task_id'],arm='NATURAL_CURRENT',context_limit=task['context_limit'],
                            source_group=task['source_group'],profile=task['profile'],label=task['task_id'])
                add(c,[row],p)
        elif prefix.startswith('golden-swap-phase4'):
            p=c/'results/final/analysis.json';add(c,load(p)['rows'],p)
            for r in runs:
                if r['campaign']==c.name:r.update(task='math-rational',version=r['summary_record']['version'],future=True)
        else:
            p=c/'results/live-attempts.json';add(c,load(p),p)
    # Exact original IQ3_S predecessor, including authoritative numerical repair.
    c=STUDY/'experiments/E004-replay'
    experiments.append({'id':'IQ3_S-E004-replay','title':'Original IQ3_S / K25 record-demand replay',
        'reason':'Earliest byte-aware recorded-demand then future-nextuse and transfer-free simulation. Not Q4 or live throughput.',
        'report':str((c/'report.md').relative_to(REPO)),'report_sha256':digest(c/'report.md')})
    for profile in ['32k','128k']:
        for policy in ['current','frequency','future-nextuse']:
            p=c/'v6-corrected-peak'/f'{profile}-rate12p6'/f'{policy}.json'
            if p.exists():
                a=load(p);r=normalize(c,a,p,f'{profile}-{policy}-v6');r.update(campaign='IQ3_S-E004-replay',task='repository-'+profile,
                    profile=profile,kind='SIMULATION',future=policy.startswith('future'),model='Qwen3.8-Flash-Next IQ3_S',
                    decode_s=None,tok_s=None,wall_s=None,simulation_path=str(p),trace_prefix=a['trace'],split=25)
                runs.append(r);sources.append(reference(p))
    # Exact Q4 future-informed replay alternatives at one already-recorded operating point.
    c=campaign('q4-residency-v2')
    for profile in ['32k','128k','256k']:
        tp=c/'traces/diagnostic'/profile/(profile+'-run1')/'trace-request2'
        if Path(str(tp)+'-initial.bin').exists():
            p=tp.parent/'trace-validation.json';a=load(p)
            r=normalize(c,a,p,profile+'-native-diagnostic');r.update(task='repository-'+profile,policy='NATIVE_DIAGNOSTIC',future=False,
                trace_prefix=str(tp),split=24,context={'32k':32768,'128k':131072,'256k':262144}[profile],kind='MEASURED_TRACE')
            runs.append(r);sources.append(reference(p))
    for policy in ['static','current','future-feasible','future-capacity-free','future-utility','future-utility-wide']:
        p=c/'analysis/references/32k/6.8'/f'{policy}.json'
        if not p.exists():
            p=c/'analysis/references/32k/relaxed'/f'{policy}.json'
        if not p.exists():
            matches=list((c/'analysis/references/32k').glob('*/'+policy+'.json'))
            p=matches[0] if matches else p
        if p.exists():
            a=load(p);r=normalize(c,a,p,'32k-'+policy+'-modeled');r.update(task='repository-32k',policy=policy,kind='SIMULATION',future=policy.startswith('future'),
                simulation_path=str(p),trace_prefix=a['trace'],split=24,decode_s=None,tok_s=None,wall_s=None,context=32768)
            runs.append(r);sources.append(reference(p))
    # Freeze detail inclusion independently of timings: first identity/block per policy/task;
    # all Phase0 natural captures and all Phase4 versions are retained in full.
    seen=set()
    for r in sorted(runs,key=lambda r:(r['campaign'],r['task'],r['policy'],str(r['attempt']),r['label'])):
        c=CAMPAIGNS/r['campaign']
        p=c/'raw'/r['label']
        if r['campaign'].startswith('golden-swap-phase4'):
            p=Path('/srv/ai/work/rad/golden-swap-phase4-publication-wait/20261007T184009Z/raw')/r['label']
        if (p/'config.json').exists():
            cfg=load(p/'config.json');prefix='native' if r['campaign'].startswith('golden-swap-phase0') else 'oracle'
            if (p/'raw'/(prefix+'-layers.bin')).exists():
                r.update(raw_dir=str(p),journal_prefix=prefix,tape_path=cfg.get('env',{}).get('STRATA_Q4_TAPE'),
                         context=cfg.get('max_total_context',cfg.get('max_context',r['context'])),
                         source_sha=cfg.get('source_sha',r['source_sha']),binary_sha256=cfg.get('binary_sha256',r['binary_sha256']))
                if r['tape_path'] and Path(r['tape_path']).exists():
                    key=(r['campaign'],r['task'],r['policy'])
                    r['detail']=key not in seen or r['campaign'].startswith(('golden-swap-phase0','golden-swap-phase4'))
                    seen.add(key)
        if r.get('trace_prefix') and Path(r['trace_prefix']+'-initial.bin').exists():r['detail']=True
        if r['detail']:r['evidence_quality']='generation/slot/service journals' if 'raw_dir' in r else 'retained modeled schedule' if r['kind']=='SIMULATION' else 'native demand/slot trace'
    unique={r['id']:r for r in runs}
    result={'experiments':experiments,'runs':list(unique.values()),'sources':sources,
        'detail_selection':'First retained identity/block per task/policy, never selected by speed; all Phase0 captures and Phase4 attempts. Other repetitions retain aggregate results. No new simulation policy or GPU work.',
        'excluded_context':[{'campaign':'upstream-921-spin-validation','reason':'Different v0.1.40 runtime; not a Golden Swap/Q4 residency comparator.'},
                            {'campaign':'pool-persistent and E015..E029','reason':'Router/pool/persistent scheduling context; no interchangeable residency trajectory. Source inspection includes original replay lineage E003/E004/E005.'}]}
    counters={r['id']:r.get('summary_record',{}) for r in result['runs']}
    save(work_root()/'derived/selection-counters.json',counters)
    result['counter_source']=str(work_root()/'derived/selection-counters.json')
    result['runs']=[{k:v for k,v in r.items() if k!='summary_record'} for r in result['runs']]
    save(REVIEW/'configs/source-selection.json',result)
    save(REVIEW/'results/source-catalog.json',{'experiments':experiments,'sources':sources,'selection':result['detail_selection'],
         'runs':len(result['runs']),'detailed':sum(r['detail'] for r in result['runs']),'excluded':result['excluded_context']})
    return result

if __name__=='__main__':
    result=discover()
    status('SOURCE_CATALOG',f"{len(result['experiments'])} experiments, {len(result['runs'])} run records; {sum(r['detail'] for r in result['runs'])} selected detailed trajectories")
