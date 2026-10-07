"""Export retained prediction evidence; no fit, new policy, or inference."""
import argparse
import statistics
import numpy as np
from common import *

def empirical_roc(y, p, weight):
    order = np.argsort(-p, kind='stable')
    y, p, w = y[order], p[order], weight[order]
    ends = np.r_[np.flatnonzero(np.diff(p)), len(p)-1]
    tp = np.r_[0., np.cumsum(w*y)[ends]]
    fp = np.r_[0., np.cumsum(w*(1-y))[ends]]
    tpr, fpr = tp/tp[-1], fp/fp[-1]
    auc = float(np.trapezoid(tpr, fpr))
    # Display decimation only; the AUC above uses every exact score boundary.
    display = np.unique(np.r_[0, np.linspace(0,len(tpr)-1,min(801,len(tpr)),dtype=int),len(tpr)-1])
    return fpr[display].tolist(), tpr[display].tolist(), auc

def build(output):
    p1, p2 = campaign('golden-swap-phase1'), campaign('golden-swap-phase2')
    provenance = []
    def read(path):
        provenance.append(reference(path)); return load(path)
    metrics = read(p1/'results/reserved-prediction-metrics.json') + read(p1/'results/development-calibration-prediction-metrics.json')
    rocs, samples, tests = [], [], []
    for task in sorted({m['task'] for m in metrics}):
        dataset, predictions = p1/'data'/f'{task}.npz', p1/'results'/f'{task}-logistic-predictions.npy'
        provenance.extend([reference(dataset),reference(predictions)])
        d, pred = np.load(dataset), np.load(predictions)
        for hi,h in enumerate([1,4,16,64]):
            mask = d['M'][:,hi].astype(bool)
            fpr,tpr,auc = empirical_roc(d['Y'][mask,hi],pred[mask,hi],d['weight'][mask])
            old = next(x for x in metrics if x['task']==task and x['model']=='logistic' and x['horizon']==h)
            assert abs(auc-old['auc']) < 1e-10, (task,h,auc,old['auc'])
            rocs.append(dict(task=task,horizon=h,fpr=fpr,tpr=tpr,auc=auc,masked_rows=int(np.count_nonzero(~mask))))
            ids = np.flatnonzero(mask & np.isfinite(d['meta'][:,5]))
            ids = ids[np.linspace(0,len(ids)-1,min(900,len(ids)),dtype=int)]
            samples.append(dict(task=task,horizon=h,prediction=pred[ids,hi].tolist(),
                                return_gap_windows=d['meta'][ids,5].tolist(),
                                source_row=ids.tolist(),display='Deterministic evenly spaced finite-return rows; never used for metric calculation.'))
            tests.append(dict(task=task,horizon=h,auc_delta=auc-old['auc'],rows=int(mask.sum()),state='PASS'))
    reconciled = {x['label']:x for x in read(p2/'results/phase1-transaction-reconciliation.json')}
    totals = read(p2/'results/phase1-transaction-totals.json')
    paired1, paired2 = read(p1/'results/paired-blocks.json'), read(p2/'results/paired-blocks.json')
    reference2=read(p2/'results/reference-paired-blocks.json')
    funnels, live = [], []
    for c,phase,pairs in [(p1,'Phase 1',paired1),(p2,'Phase 2',paired2)]:
        rows = read(c/'results/live-attempts.json')
        groups = {}
        for x in rows:
            if not x.get('valid') or x['task'] not in ['code-archive','math-inventory','text-websocket','mixed-chinook']: continue
            groups.setdefault((x['task'],x['arm']),[]).append(x)
            if x['block'] != 1 or x['arm'] == 'REPLAY_CURRENT': continue
            cp,sc,tc = x['copy'],x.get('scorer',{}),x.get('tc',{})
            tx = reconciled.get(x['label'],{}) if phase=='Phase 1' else x.get('transactions',{})
            stages = []
            def stage(label,value,unit='transactions'):
                stages.append(dict(stage=label,value=value,unit=unit))
            stage('Candidate enumeration',tc.get('enumerated'),'candidate visits; repeated scans')
            stage('Risk / proxy scores',sc.get('scores'),'score calls')
            stage('Cost veto',tc.get('cost_veto',sc.get('rejected')),'candidate vetoes; Phase 1 combined rejects')
            stage('Protection exclusion',tc.get('protection_veto'),'excluded residents / visits')
            stage('Capacity / cap veto',tc.get('capacity_veto'),'proposal vetoes')
            stage('Risk veto',tc.get('risk_veto'),'candidate vetoes')
            stage('Admitted / copied',cp.get('issued'))
            stage('Completed',cp.get('completed'))
            stage('Published',cp.get('published'))
            part=tx.get('partition',{})
            stage('Used before eviction',part.get('published_used_before_eviction',{}).get('transactions'))
            stage('Evicted without use',part.get('published_evicted_without_use',{}).get('transactions'))
            stage('No-use resident at end',part.get('published_no_use_resident_at_end',{}).get('transactions'))
            stage('Published expert service',cp.get('uses'),'routed lane entries')
            stage('Victim demand while absent',cp.get('victim_absent'),'routed lane entries; not exclusive lost latency')
            funnels.append(dict(task=x['task'],label=phase+' · '+x['label'],stages=stages,
                scope='Block 1, main tape. Native candidate eligibility/current-window exclusions are not a fully recorded count. Different units are deliberately not connected by a synthetic conservation equation.',
                terminal_partition=part,decode_s=x['decode_s'],wall_s=x['wall_s'],provenance=reference(c/'results/live-attempts.json')))
        for (task,arm),rs in groups.items():
            def med(fn):
                vs=[fn(r) for r in rs];vs=[v for v in vs if v is not None]
                return statistics.median(vs) if vs else None
            if arm=='REPLAY_CURRENT': change=0.
            elif phase=='Phase 1':
                k='full_TG_change_pct' if arm=='ORACLE_FULL' else 'learned_TG_change_pct'
                change=statistics.median(p[k] for p in pairs if p['task']==task)
            else:
                ps=[p for p in pairs if p['task']==task and p['arm']==arm]
                change=statistics.median(100*(p['TG_ratio']-1) for p in ps) if ps else statistics.median(p['TG_pct'] for p in reference2 if p['task']==task and p['arm']==arm)
            live.append(dict(task=task,campaign=phase,policy=arm,valid=len(rs),copy_GB=med(lambda r:r.get('copy_GB')),
                unused_pct=med(lambda r:100*r['copy']['unused_bytes']/r['copy']['completed_bytes'] if r['copy']['completed_bytes'] else None),
                **{'nonlocal':med(lambda r:r['cpu_entries']+r['mapped_entries'] if 'cpu_entries' in r else r['demand']['cpu']+r['demand']['mapped'])},paired_TG_pct=change,
                planner_ms=med(lambda r:r.get('planner',{}).get('planner_ms')),score_ms=med(lambda r:r.get('scorer',{}).get('score_ms')),
                timers='Feature/model inside selection inside planner; legacy current hook is not total native planner. Do not sum.'))
    result=dict(metrics=metrics,roc=rocs,samples=samples,funnels=funnels,live_comparison=live,
        ranking=read(p1/'results/sampled-victim-ranking.json'),selection=read(p1/'models/selection.json'),
        threshold_sensitivity=read(p2/'results/threshold-sensitivity.json'),
        protection_opportunities=read(p2/'results/protection-opportunity-costs.json'),
        history_logistic=read(p2/'results/history-versus-logistic.json'),
        lifecycle_ablation=read(p2/'results/development-ablation.json'),
        phase1_mechanism_fraction=totals['ORACLE_IN_LEARNED_VICTIM']['evicted_before_intended_first_target_bytes']/totals['ORACLE_IN_LEARNED_VICTIM']['unused_completed_bytes'],
        missing=['Phase 1 live cheap-history arm: not measured in the main live matrix.',
                 'AUC on policy-dependent post-admission residents: frozen model evaluated native-state samples, not the intervention distribution.',
                 'Exact per-decision history/logistic disagreement under identical live state: policies diverge; matching vector positions is not a causal comparison.',
                 'Per-event cost/protection/cap veto timestamps: retained totals only.',
                 'Exclusive saved CPU latency, pure DMA time, and per-expert latency impact: unmeasured.',
                 'Finite-tail no-return ground truth and a validated expert-specific TTL policy: unavailable.'],
        provenance=provenance,validation=dict(state='PASS',roc_auc_checks=tests,gpu_or_fit_calls=0))
    save(output/'predictor.json',result)
    save(REVIEW/'results/predictor-validation.json',result['validation'])
    print('PREDICTOR_EXPORT',len(metrics),'metric rows',len(rocs),'exact weighted AUC checks',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=work_root()/'derived/browser-v1');build(p.parse_args().output)
