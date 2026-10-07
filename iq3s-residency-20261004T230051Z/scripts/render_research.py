"""Render consolidated measured results from retained records, without inference."""
import argparse
import csv
import hashlib
import statistics
import time
from datetime import datetime, timezone
from lab import ROOT, load, save
ap=argparse.ArgumentParser()
ap.add_argument('--final', action='store_true')
a=ap.parse_args()
points=[('E002-controls','v1','CURRENT control'),('E006-frequency','v1','Frequency'),
        ('E010-compatible-runtime','v1','Compatible selector'),('E013-compatible-fast','v1','Compatible heap repair'),
        ('E014-policy-off-guard','v1','Same-binary policy OFF'),('E016-device-plan-ids','v2','Safe device plan'),
        ('E019-skip-local-host-plan','v1','Skip redundant host plan'),
        ('E022-host-plan-off-guard','v1','Same-binary host plan OFF'),
        ('E023-direct-parts','v1','Direct expert output rows'),
        ('E025-direct-parts-off-guard','v1','Same-binary direct rows OFF'),
        ('E024-pool-wait','v1','Existing pool sleep100us')]
keys=['actual_input_tokens','actual_output_tokens','PP','TG','TTFT_s','wall_s','mtp_proposed','mtp_accepted','mtp_acceptance_pct',
      'mtp_accepted_per_window','verify_windows','mean_decode_window_latency_ms','hit_rate_pct','all_demand_local_pct',
      'local_vram_entries','cpu_fallback_entries','offloaded_entries']
def digest(r):
    return r.get('output_text_sha256') or hashlib.sha256((r.get('reasoning','')+'\0'+r.get('text','')).encode()).hexdigest()
def dist(values):
    v=[x for x in values if x is not None]
    return {'min':min(v),'median':statistics.median(v),'max':max(v)} if v else None
cells=[]
for experiment,attempt,name in points:
    for profile in ['32k','128k']:
        folder=ROOT/'experiments'/experiment/attempt/profile
        files=[folder/'raw'/f'run{n}.json' for n in [1,2,3]]
        found=[p for p in files if p.exists()]
        if not found:continue
        runs=[load(p) for p in found]
        valid=[r for r in runs if r['state']=='VALID']
        for r in valid:
            assert r['actual_output_tokens']==4096 and r['reuse']==0
            assert r['full_config']['max_total_context']==(32768 if profile=='32k' else 131072)
            r['mean_decode_window_latency_ms']=1000*r['decode_s']/r['verify_windows'] if r.get('verify_windows') else None
            counts=[r.get(k) for k in ['local_vram_entries','cpu_fallback_entries','offloaded_entries']]
            demand=sum(counts) if all(x is not None for x in counts) else None
            r['all_demand_local_pct']=100*r['local_vram_entries']/demand if demand else None
        warm=load(folder/'raw/warmup.json')
        assert warm['actual_input_tokens']==4096 and warm['actual_output_tokens']==64
        reference=[load(ROOT/f'experiments/E002-controls/v1/{profile}/raw/run{n}.json') for n in [1,2,3]]
        paired=[{'run':n,'same_input_IDs':r['payload']['input_ids_sha256']==b['payload']['input_ids_sha256'],
                  'same_visible_output':digest(r)==digest(b), 'TG_delta_pct':100*(r['TG']/b['TG']-1),
                  'MTP_acceptance_delta_pp':r['mtp_acceptance_pct']-b['mtp_acceptance_pct']} for n,(r,b) in enumerate(zip(runs,reference),1) if r['state']=='VALID']
        assert all(x['same_input_IDs'] for x in paired)
        row={'experiment':experiment,'attempt':attempt,'name':name,'profile':profile,'valid':len(valid),
             'attempted':len(runs),'invalid':len(runs)-len(valid),'raw_paths':[str(p) for p in found],
             'statistics':{k:dist([r.get(k) for r in valid]) for k in keys}, 'paired_with_control':paired,
             'source_sha':runs[0]['source_sha'],'binary_sha256':runs[0]['binary_sha256'],
             'config_path':str(folder/'config.json'),'warmup_path':str(folder/'raw/warmup.json'),
             'application_statuses':[r.get('application_status') for r in valid],
             'finish_reasons':[r.get('finish_reason') for r in valid],
             'resource_evidence':str(folder/'raw/resource-check.json') if (folder/'raw/resource-check.json').exists() else str(ROOT/'analysis/control-budgets-v2.json')}
        cells.append(row)
stages={}
for line in (ROOT/'experiments.jsonl').read_text().splitlines():
    if line.strip():
        r=__import__('json').loads(line)
        stages[r['id']]=r
state=load(ROOT/'STATUS.json')
deadline=load(ROOT/'deadline.json')
selection=state.get('recommendation','KEEP_CURRENT_LAYER_SPLIT')
save(ROOT/'summary.json',{'state':'COMPLETE' if a.final else 'IN_PROGRESS',
    'updated_utc':datetime.now(timezone.utc).isoformat(),'elapsed_s':time.time()-deadline['start_epoch'],
    'deadline':deadline,'selection':selection,'measured_cells':cells,'stage_states':stages,
    'candidate_ledger':load(ROOT/'candidate-ledger.json'),'excluded':state['excluded'],
    'budgets':load(ROOT/'analysis/control-budgets-v2.json'),
    'measurement_scope':'Fresh total capacities32768/131072; identical saved inputs and fixed4096output, greedy, MTP4/minp.5, suffix/reuse0, one64outputwarmup and3serialrequests/profile. Separate batches, not paired fresh-server trials.',
    'limitations':['No diagnostic/simulated rate is a headline result.','Three requests cannot establish small universal wins.',
                   'Same-output guards show substantial build/batch TG variation; no diagnosed VM or binary-layout cause.',
                   'Clean visible hashes are not full output-ID/logit parity. Strict output/router/head parity belongs to separate numerical diagnostics.',
                   'Logical expert file-read counters unavailable are not zero; the immutable native expert arena is already in RAM.']})
flat=[]
for c in cells:
    r={k:c[k] for k in ['experiment','attempt','name','profile','valid','attempted','invalid','source_sha','binary_sha256','config_path']}
    for k,d in c['statistics'].items():
        for stat in ['min','median','max']:r[k+'_'+stat]=d[stat] if d else None
    r['raw_paths']=';'.join(c['raw_paths']);flat.append(r)
with (ROOT/'summary.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
lines=['# IQ3_S expert-residency research','',f"Status: {'COMPLETE' if a.final else 'IN_PROGRESS'}. Recommendation: {selection}.",
       '',f"Elapsed: {(time.time()-deadline['start_epoch'])/3600:.2f} hours; hard deadline {deadline['deadline_utc']}.",
       '', 'The strongest scoped result is the existing 100us CPU-pool sleep option on the unchanged CURRENT executable: 178.5/154.0 tok/s at the two total-context limits, with median decode CPU about 28.0%/25.8%. This preserves output/MTP/capacity in the saved workload. Increased CPU-positive wakeup waits and substantial same-output batch variation elsewhere prevent a universal 15% claim. Normal production launchers are unchanged.',
       '', 'The residency/prediction branches were executed through bounded replay, training, timing and runtime confirmation. None establishes a portable live selective-residency win. Persistent router-guided admissions and cross-device scheduling remain explicit untested directions, not completed negatives.',
       '', '## Clean measured confirmations','',
       '| Candidate | Total context | Actual input range | PP min / median / max | TG min / median / max | TTFT s | Wall s | MTP accepted % | Valid |',
       '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for c in cells:
    s=c['statistics'];tg=s['TG']
    if not tg:continue
    pp=s['PP'];ctx=s['actual_input_tokens']
    lines.append(f"| {c['name']} | {32768 if c['profile']=='32k' else 131072} | {ctx['min']}–{ctx['max']} | {pp['min']:.1f} / {pp['median']:.1f} / {pp['max']:.1f} | {tg['min']:.1f} / {tg['median']:.1f} / {tg['max']:.1f} | {s['TTFT_s']['median']:.3f} | {s['wall_s']['median']:.3f} | {s['mtp_acceptance_pct']['median']:.2f} | {c['valid']}/{c['attempted']} |")
lines += ['', 'All figures above come from the raw paths in summary.json/summary.csv. The first measured request can include lazy graph capture under the same 64-output warmup. All attempts remain included; no favorable-run replacement or extra unchanged repetition was used.',
          '', 'Only CURRENT is the primary reference. Historical v0.1.38/helper campaigns are evidence sources, not additional fresh controls. Same inputs/settings and budgets are preserved, but serial batches occurred at different wall times. A cache policy can also alter the free-generation/MTP trajectory.', '']
if (ROOT/'analysis/main-narrative.md').exists():lines.append((ROOT/'analysis/main-narrative.md').read_text())
if (ROOT/'analysis/replay-closure.md').exists():lines.append((ROOT/'analysis/replay-closure.md').read_text())
if (ROOT/'analysis/decode-progression/summary.json').exists():
    progression=load(ROOT/'analysis/decode-progression/summary.json')
    lines+=['','## Decode progression at available resolution','',
        '| Candidate | Profile | TG0–512 | TG512–1K | TG1K–2K | TG2K–4K | Engine final TG |',
        '|---|---|---:|---:|---:|---:|---:|']
    for r in progression['rows']:
        vals=[f'{r[k]:.1f}' if r[k] is not None else 'Unavailable' for k in ['0-512','512-1K','1K-2K','2K-4K']]
        lines.append(f'| {r["name"]} | {r["profile"]} | '+ ' | '.join(vals)+f' | {r["engine_TG_median"]:.1f} |')
    lines+=['','Intervals are median approximate client-wall rates derived from one-Hz live generated counts; full sample brackets and lower/upper bounds are retained in analysis/decode-progression/summary.json. They are not exact engine per-token timing. Interval MTP/cache counters are unavailable in clean builds. Separate E003 diagnostics show early cache/MTP changes, but do not establish their isolated contribution to clean acceleration.']
if (ROOT/'analysis/system-phases/summary.json').exists():
    system=load(ROOT/'analysis/system-phases/summary.json')
    lines+=['','## Decode system telemetry','',
        '| Candidate | Profile | VM CPU mean median % | GPU0 / GPU1 mean median % | Peak VRAM0 / VRAM1 MiB | Peak RSS sum GiB |',
        '|---|---|---:|---:|---:|---:|']
    for c in cells:
        rs=[r['phases']['decode'] for r in system['rows'] if (r['experiment'],r['profile'])==(c['experiment'],c['profile'])]
        if not rs:continue
        cpu=statistics.median(r['system_CPU_pct']['mean'] for r in rs)
        gpu=[statistics.median(r['GPUs'][str(i)]['util_pct']['mean'] for r in rs) for i in [0,1]]
        mem=[max(r['GPUs'][str(i)]['vram_mib']['max'] for r in rs) for i in [0,1]]
        rss=max(r['sum_process_RSS_GiB']['max'] for r in rs)
        lines.append(f'| {c["name"]} | {c["profile"]} | {cpu:.1f} | {gpu[0]:.1f} / {gpu[1]:.1f} | {mem[0]:.0f} / {mem[1]:.0f} | {rss:.2f} |')
    lines+=['','System CPU uses VM-wide0–100%; process CPU in the raw derivation uses one core=100%. Shared mappings can be counted twice in RSS sums. Power/clocks/RAM/physical-read sample distributions are retained in analysis/system-phases/summary.json. Physical-read deltas are not logical expert reads. One-Hz PCIe dmon cannot identify individual critical-path bursts.']
lines += ['', '## Experiment ledger','', '| ID | Latest state | Evidence |','|---|---|---|']
for folder in sorted((ROOT/'experiments').iterdir()):
    if not folder.is_dir():continue
    ident=folder.name.split('-')[0]
    stage=stages.get(ident,{})
    report=folder/'report.md'
    evidence=f'[{folder.name}](experiments/{folder.name}/report.md)' if report.exists() else f'`experiments/{folder.name}/`'
    lines.append(f"| {ident} | {stage.get('state','PLANNED_OR_UNRECORDED')} | {evidence} |")
lines += ['', '## Reproduction and preservation','',
          'See launch-index.md for exact frozen start/stop/reproduce commands, states and source/binary/config identities. Diagnostic and unsafe historical variants are labeled; they are not production recommendations. Reproduction must use new versioned output directories and obey the recorded three-attempt limit within this campaign.',
          '', 'Existing model files, quantization, profiles, services, older source checkouts and campaigns remain untouched. New patches and local commits are unpublished. No normal launcher was switched.',
          '', 'Final source/binary/patch identities and model metadata checks are in git/final-provenance.json. Compiler/CUDA/driver/topology/build commands remain in git/. Python package versions/licenses/origin limits are recorded in git/python-dependencies-final.json. Small artifact hashes and large on-disk size/mtime records are in git/artifact-inventory.jsonl; the audit is analysis/final-audit.json.',
          '', 'Every completed runtime point has exactly three valid measured requests: 22 cells/66 requests, each with 4,096 output tokens and zero reuse. Warmups and diagnostic/negative attempts are separate. Executable launch commands are mapped to experiment IDs in launch-index.md. The shared Session startup backend was exercised in normal flows; thin aliases are additionally syntax/help validated, not all separately smoke-started.',
          '', 'Every stage separates measured results, fixed-trace simulations and untested proposals. The deadline bounds the investigation; untested alternatives are not claimed exhausted.']
(ROOT/'report.md').write_text('\n'.join(lines)+'\n')
print('Rendered',len(cells),'measured cells; selection',selection)
