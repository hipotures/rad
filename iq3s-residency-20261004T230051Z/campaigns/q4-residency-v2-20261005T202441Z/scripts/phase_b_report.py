"""Finite family ledger and pre-live decision; no throughput inference from replay."""
import json,datetime
from pathlib import Path
from campaign import C,R,load,save,status
from trace_reader import Trace

def main():
    costs=load(C/'phase-a/cost-analysis.json');assert len([r for r in costs if '/cost-h4/' in r['result']])==9
    summary=load(C/'phase-b/competition.json');learned=load(C/'phase-b/learned/evaluation.json');train=load(C/'phase-b/learned/training.json')
    signal=[]
    for p in sorted((C/'phase-b/early-projection').glob('*/*.json')):
        d=load(p);r=load(d['source_result']);t=Trace(r['trace_prefix'])
        signal.append({k:d[k] for k in ['policy','prediction_enabled','target_ready','CPU_entries','mapped_entries','staging_bytes','useful_resident_entries','descriptive_victim_absent_entries','modeled_publication_metadata_s','classification']}|{
            'point':p.parent.name,'path':str(p),'original_nonlocal':int((t.entries['path']!=0).sum()),'charged_capacity':d['active_capacity_after_reserve'],'original_capacity':d['original_capacity']})
    assert len([x for x in signal if x['point'].startswith('cost-h4')])==27
    families={p:{'status':'COMPLETE_NEGATIVE' if p.startswith('jev-') or p in ['static','frequency','markov','least-stale-inspired'] else 'MIXED','raw':[x['path'] for x in summary if x['policy']==p]} for p in sorted({r['policy'] for r in summary})}
    families['static-development-only']={'status':'COMPLETE_NEGATIVE','raw':str(C/'phase-b/dev-static-summary.json'),'reason':'Independent held-out and long-document demand poorly served by2-task development profile; do not replace runtime profile.'}
    families['native-router-H1/H4/H8']={'status':'MIXED','raw':str(C/'phase-a/cost-analysis.json'),'reason':'H1 has stronger membership but most staged candidates late; H4 ready on dev but85% selected-nonresident predictions wrong; H8 weaker plus third spare.'}
    families['early-linear-hybrid']={'status':'MIXED','raw':str(C/'phase-b/early-projection'),'reason':'Charged2-spare H4 projection, immutable same-layer slot classes, guarded target publication and persistent retention; small miss reduction with high discarded copy traffic. Live test needed.'}
    families['Basal-semantic-prior']={'status':'NOT_ATTEMPTED','reason':'Only6 independent short task traces; no justified learned semantic-to-Q4-expert map. CPU EagerBackend run_shared flattens full forwards; large checkpoint cost not justified. No Polish/translation benefit claimed.','source':str(C/'sources/manifest.json')}
    finalists=[{'variant':'history-v1','reason':'Strongest cheap traffic/nonlocal tradeoff on long repository traces; significant holdout miss regression retained. Existing safe native DMA/publication only.','environment':{'STRATA_Q4_HISTORY':'1'}},
               {'variant':'early-v1','reason':'Distinct earlier persistent causal mechanism, H4 selected on dev before held-out transfer. Frozen linear score for victim protection;2 charged3.072MB spare slots; existing gate/scratch only. Must pass concurrent-CUDA dependency proof before live.','environment':{'STRATA_Q4_EARLY':'1'},'required_ablations':['same binary OFF','matched2-spare reactive scheduler','diagnostic delayed/wrong predictions and exact byte readback']}]
    out={'state':'COMPLETE_MIXED','families':families,'causal_replay':summary,'signal_projection':signal,'learned':learned,'finalists':finalists,
         'unchanged_baseline':'K24/PCIe0.28/100us/spec4/minp0.5/INT8/current frozen executable','decision':'PROCEED_PHASE_C_WITH_MAX2_FINALISTS',
         'limits':['No measured TG or exclusive latency oracle from replay','0.25ms/entry utility proxy is explicit assumption; actual overlap differs',
                   'Copy-only modeled joins match original6-7% low; predictor/feature/selection contention not a TG model',
                   'Whole-task holdouts3 short episodes; no universal language/document generalization',
                   'Projection readiness uses observed clocks; changed execution contention requires live timing',
                   'Early metadata50us is assumed and must be measured. No CUDA call permitted in host plan.']}
    save(C/'phase-b/summary.json',out)
    text=['# Phase B — causal Q4 policy competition','', '**COMPLETE_MIXED. Freeze two runtime finalists; unchanged100us Q4 remains the reference.**','',
          'Training/normalization used dev-code and dev-math only; calibration used cal-prose; hold-code, hold-structured and hold-math are entire independent episodes. Long32/128/256 repository payloads never fit the checkpoint. Last4/16 future windows are censored, not negative labels. Models predict nonexclusive expected counts, not a softmax. Seed20261005.','',
          '## Family ledger','', '| Family | Status | Disposition |','|---|---|---|']
    for name,r in families.items():text.append(f"| {name} | {r['status']} | {r.get('reason','Shared finite-byte scheduler; all9 episode results preserved.')} |")
    text+=['','## Fixed-trajectory exchange outcomes','', '| Episode | Policy | Nonlocal entries | Promotion GB | Modeled join s | Victim-absent entries |','|---|---|---:|---:|---:|---:|']
    for row in summary:
        if row['episode'] in ['32k','128k','256k','hold-code','hold-structured','hold-math'] and row['policy'] in ['current','hybrid-history','jev-linear','jev-mlp','jev-temporal-mlp']:
            text.append(f"| {row['episode']} | {row['policy']} | {row['nonlocal_entries']} | {row['promotion_bytes']/1e9:.2f} | {row['modeled_pending_wait_s']:.3f} | {row['victim_entries']} |")
    text+=['','The cheap hybrid halves long-trace promotion traffic but does not remove nonlocal work; independent short holdouts show a material miss increase. Learned policies reduce traffic more aggressively but under-admit and increase CPU/mapped work. Recency can preserve more hits by spending more bytes. None is a replay throughput winner.','',
           'CPU-only linear/MLP costs and feature/update/selection are retained per-policy in replay files.32-unit MLP learning curves fall on development batches; held-out capacity-only coverage~94–95% does not translate into a good finite replacement schedule. The16-window temporal extension is completed negative; no larger retraining after holdout inspection.','',
           '## Causal native-router timing and charged spare','', '| Point | Policy | Ready admissions | Nonlocal/original | Staging GB | Useful resident entries | Victim-absent entries |','|---|---|---:|---:|---:|---:|---:|']
    for row in signal:
        if row['point'].startswith('cost-h4') and row['policy']=='early-linear-hybrid':
            text.append(f"| {row['point']} | {'predictive' if row['prediction_enabled'] else 'reactive'} | {row['target_ready']} | {row['CPU_entries']+row['mapped_entries']}/{row['original_nonlocal']} | {row['staging_bytes']/1e9:.2f} | {row['useful_resident_entries']} | {row['descriptive_victim_absent_entries']} |")
    text+=['','H4 was selected from dev timing/readiness before its3 long-profile and3 holdout transfer traces. Raw gate scores are rankings, not calibrated future probabilities. Only5 origins/targets of48 are covered. Target truth is consulted at the actual host plan; a wrong or late staged candidate cannot publish. Incoming experts remain until later replacement; no per-use restoration. Current adaptive replacement continues. All staged bytes, two reserved native slots and modeled metadata publication waits are charged.','',
           'The reactive matched scheduler and raw-router/no-learned ranking are retained as ablations. Projection timestamps follow the original observed trajectory; no predicted TG. H4’s potential miss reduction is small and discarded copy traffic large, making live outcome uncertain. This is a bounded test of an untested mechanism, not an endorsement.','',
           '## Phase C freeze','',
           '1. **history-v1**: heat*0.2+fast*(2/3); joint incoming/victim four-window utility, copy-size penalty,0.125ms margin,96 total actions and160MiB/device budget. Safe original end-verify copy/publication.','2. **early-v1**: H4 native gate reuse, CPU-only frozen linear victim/ranking, one3.072MB staging spare/device within original cache. Stage early on a dedicated worker; publish device residency only after bytes complete and before CPU releases the target plan. Protect all current routed victims. Native reactive EMA remains.','',
           'Before live early inference, a minimal test must prove main-thread stream synchronization can coexist with the separate worker while the graph awaits the host planner. OFF parity, exact native Q4 kernels, wrong/delayed predictions, reader/slot/cancellation stress and diagnostic backing-byte readback precede speed claims. Speed binaries exclude diagnostics. Finalists may lose and remain preserved.','',
           'Model constants/checkpoints and source manifests are under checkpoints/, phase-b/learned/, datasets/, sources/. Open-Jev-inspired naming is local numeric research, not published Jev. Basal remains explicitly unattempted under the bounded-data/CPU hypothesis, not disproven.']
    (C/'phase-b/report.md').write_text('\n'.join(text)+'\n')
    record={'id':'E031-q4-causal-competition','status':'COMPLETE_MIXED','report':str(C/'phase-b/report.md'),'campaign':str(C),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    for ledger in [C/'ledger.jsonl',R/'experiments.jsonl']:
        existing=[json.loads(x) for x in ledger.read_text().splitlines()]
        if not any(x.get('id')==record['id'] and x.get('status')==record['status'] for x in existing):
            with ledger.open('a') as f:f.write(json.dumps(record)+'\n')
    s=load(C/'STATUS.json');s['phases']={'A':'COMPLETE_MIXED','B':'COMPLETE_MIXED','C':'RUNNING'};save(C/'STATUS.json',s)
    status('RUNNING',phase='C',running='ordering proof and isolated default-OFF implementations',next_exact_action='Prove CUDA dependency, build two frozen finalists, targeted correctness/OFF guard then bounded live funnel')
    print('PHASE_B_COMPLETE',flush=True)
if __name__=='__main__':main()
