"""Derive compact stage evidence and reports without versioning repeated raw arrays."""
import csv, hashlib, json, pathlib
from lab import ROOT, load, save
replay=ROOT/'experiments/E004-replay';records=[]
for path in sorted(replay.glob('v*/*-rate*/*.json')):
    r=load(path);profile=path.parent.name.split('-rate')[0]
    compact={k:v for k,v in r.items() if k not in ['frames','promotions']}
    compact.update(profile=profile,path=str(path),file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),attempt=path.parts[-3])
    compact['state']='INVALID_NUMERICAL_QUEUE' if path.parts[-3]=='v4-sensitivity' else 'VALID_WITH_LEGACY_PRECISION_CAVEAT' if path.parts[-3] in ['v1','v2','v3'] else 'VALID'
    if r['policy']=='future-capacity-free':
        compact.update(useful_promotion_bytes=None,unused_promotion_bytes=None,victim_demand_while_absent=None)
        compact['legacy_metric_correction']='Earlier free-reference raw fields of zero victim damage are unmeasured, not validated zero. Replacement and nonlocal counts remain valid.'
    records.append(compact)
save(replay/'evidence.json',records)
columns=['profile','attempt','state','policy','aggregate_transfer_budget_GB_s','nonlocal_entries','promotion_bytes','useful_promotion_bytes','unused_promotion_bytes','victim_demand_while_absent','modeled_pending_wait_s','path']
with (replay/'summary.csv').open('w') as stream:
    writer=csv.DictWriter(stream,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(records)
lines=['# Byte-aware replay evidence','',
 'Status: COMPLETE_POSITIVE for the bounded replay/headroom study. Baseline selection/publication accounting and measured-range cost sensitivities are completed. All results are fixed-trace simulations, not measured TG. Precision-repair exclusions are retained and labeled; see v4-sensitivity/repair-history.md.','',
 'The C++ selector reproduces every observed baseline promotion and final float32 usage for both main traces. Trace categories and startup slot/byte classes independently reconcile with live counters. Every policy keeps K=25, separate GPU0/GPU1 budgets, same-layer variable-size slot classes and immutable host backing. The aggregate copy queue includes 4.2 us issue overhead. Incoming entries publish only after modeled copy completion; the original blocking publication policy stalls the next window until all previous promotions are ready. Therefore lower modeled bandwidth increases wait rather than allowing unsafe late publication.','',
 'Future capacity-free replacement relaxes transfer timing completely. Future-nextuse uses true future demand, up to 96 swaps every window, a 16-window horizon and measured-range assumed transfer costs. It is a stronger feasible heuristic under those assumptions, not a proven optimum or deployable causal predictor. The earlier future-four-window count heuristic is weaker and does not establish a capacity bound.','',
 '| Profile | Policy | Nonlocal entries | Promotion GB | Modeled publication wait s |','|---|---|---:|---:|---:|']
for r in records:
    lines.append(f"| {r['profile']} | {r['policy']} ({r['attempt']}, {r['aggregate_transfer_budget_GB_s']}, {r['state']}) | {r['nonlocal_entries']} | {r['promotion_bytes']/1e9:.3f} | {r['modeled_pending_wait_s']:.3f} |")
lines+=['','Frequency is selected for bounded live confirmation: fewer modeled nonlocals at both profiles with much less churn than recency. Least-Stale is explicitly a same-layer stale-first/FIFO adaptation, not the paper\'s global SpecMD implementation. The initial Markov selector shrinks score units relative to heat and must receive a normalized follow-up before closing that family.','',
 'Limitations: nonlocal CPU/mapped/resident compute remains held at the observed trajectory; selector Python wall time is reported but not included in a fake TG estimate. Actual source categories for new policies are unavailable. Cumulative promotion bytes count transfers, not SSD reads. Timing uses one host clock; no per-event CUDA synchronization is added. A full copy/computation interference sensitivity and live candidate test are required.','',
 'Repairs and failed attempts remain in v1/repair-history.md and the diagnostic reader repair record. Raw replay arrays are retained on disk and hashed in evidence.json. Reproduce with scripts/replay.py, the recorded trace prefix, rate and policy list; exact recorded commands are retained for v3 and follow-ups.']
(replay/'report.md').write_text('\n'.join(lines)+'\n')
jev=ROOT/'experiments/E005-expert-jev';evaluation=load(jev/'v1/evaluation.json');training=load(jev/'v1/training.json')
summary={'state':'COMPLETE_NEGATIVE','scope':'Bounded trained-scorer replay and independent-episode evaluation; no claim that all learned prediction is exhausted.',
 'training':{name:{k:v for k,v in x.items() if k!='history'} for name,x in training.items()},'heldout':[x for x in evaluation['episodes'] if x['role']=='holdout'],
 'replay':[r for r in records if r['policy'].startswith('jev-')],
 'runtime_disposition':'No scorer runtime build justified yet: all three increase held-trace nonlocal work at both profiles; numeric inference is only a partial cost. Continue signal/cheap-hybrid research rather than claim generic learned methods cannot work.'}
save(jev/'summary.json',summary)
lines=['# Expert-Jev-inspired numeric scorers','',
 'Status: COMPLETE_NEGATIVE for the predeclared linear/MLP/temporal replay evaluation. This does not close all learned/predictive methods. The small models score explicit expert candidates; no released Open-Jev language backbone runs beside IQ3_S. Open-Jev revision and MIT origin are recorded in sources.json.','',
 'Development tasks: code and mathematics. Calibration: independent prose task. Holdout: transactional code, structured JSON and polynomial mathematics. Whole episodes are separated; observed state updates are causal; labels are next-four-window counts including rejected speculative branch work. Two development tasks are a small sample, so generalization is limited. The main long repository-maintenance requests were not used to fit predictors.','',
 'The target is log1p expected count under an inverse-sampling-weighted squared objective, not a softmax or probability that exactly one expert is used. Mean/std are fitted only on development rows. The affine count calibration uses calibration prose only and clamps negatives. Raw sampled data, sampling indices, checkpoints, seeds and hashes remain in v1.','',
 '| Held task | EMA coverage | Linear | MLP | Temporal MLP |','|---|---:|---:|---:|---:|']
for x in summary['heldout']:
    values=[x['cheap_baselines']['EMA']]+[x['models'][name]['mean_future_demand_coverage_at_layer_capacity'] for name in ['linear','mlp','temporal-mlp']]
    lines.append('| '+x['episode']+' | '+' | '.join(f'{v*100:.3f}%' for v in values)+' |')
lines+=['','Capacity-ranking coverage is a cost-free proxy. Finite-copy replay is also completed at both profiles and increases nonlocal entries for all three learned scorers. Linear ranking essentially duplicates EMA; the MLP and temporal features are weaker. Temporal ablation therefore has an explicit measured disposition.','',
 '| Scorer | Parameter bytes | Training s | Checkpoint SHA256 |','|---|---:|---:|---|']
for name,x in training.items():lines.append(f"| {name} | {x['parameter_bytes']} | {x['training_wall_s']:.4f} | `{x['sha256']}` |")
lines+=['','Numeric full-candidate inference is approximately 0.29 / 0.65 / 0.75 ms for linear / MLP / temporal. These are CPU numerical scoring costs only; feature extraction, state updates, selection, transfer timing and contention are not included. No deployable runtime overhead or TG gain is claimed. Additional GPU predictor memory is zero in replay; live memory/cost remains untested.','',
 'Next decision: test the simple frequency policy live, normalize the transition baseline, and investigate legitimately available token/router signals. Do not train a large model or claim a universal negative conclusion from this small dataset.']
(jev/'report.md').write_text('\n'.join(lines)+'\n')
ledger=load(ROOT/'candidate-ledger.json')
updates={
 'F01':('COMPLETE_NEGATIVE' if (ROOT/'experiments/E006-frequency/summary.json').exists() else 'RUNNING','Frequency reduces fixed-trace nonlocals but live confirmation has lower TG at both profiles; static/recency/EMA bounded comparisons complete. Existing current policy remains the measured reference.'),
 'F02':('COMPLETE_NEGATIVE','Stale-first/FIFO same-layer adaptation increases misses and transfers; original global paper scheduler not deployed.'),
 'F03':('COMPLETE_NEGATIVE','Causal Markov indexing and heat-unit normalization repaired and evaluated both profiles; normalized result still loses. This does not exhaust all transition/co-occurrence representations.'),
 'F04':('COMPLETE_NEGATIVE','Linear and small MLP trained/calibrated on separated episodes and replayed both profiles. No runtime benefit justified by these scorers.'),
 'F04T':('COMPLETE_NEGATIVE','Temporal MLP ablation complete; worse than EMA and linear on held tasks and finite-copy replay.'),
 'F05':('RUNNING','MTP token-history and cross-layer gate availability audit; preserve causality and measure readiness.'),
 'F06':('PARTIAL','Bounded causal 256-bigram history + EMA completed in replay; slight nonlocal reduction but extra transfers and feature cost. Next-router hybrid depends on E008 availability evidence.'),
 'F07':('PARTIAL','Exact per-GPU capacities, copy/publication waits and future schedule headroom measured; placement and stage-boundary critical path follow-ups pending.')}
for family in ledger['families']:
    if family['id'] in updates:family['state'],family['next']=updates[family['id']]
save(ROOT/'candidate-ledger.json',ledger)
print('Numeric stage reports and artifact manifests updated',len(records),flush=True)
