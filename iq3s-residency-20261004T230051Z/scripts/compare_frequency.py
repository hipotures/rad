"""Derive live frequency/control evidence only from preserved valid raw requests."""
import csv, datetime, hashlib, json, pathlib, statistics
from lab import ROOT, load, save
EXP=ROOT/'experiments/E006-frequency';out=EXP/'analysis';out.mkdir(exist_ok=True)
def resource_evidence(folder,profile):
    if (folder/'raw/resource-check.json').exists():return load(folder/'raw/resource-check.json')
    startup=load(folder/'raw/startup.json');engine=startup['metrics']['engine'];budget=load(ROOT/'analysis/control-budgets-v2.json')[profile]
    primary=engine['expert_slots_primary'];secondary=engine['expert_slots']-primary
    assert (primary,secondary)==(budget['primary_slots'],budget['helper_or_stage1_slots'])
    return {'state':'PASS_DERIVED','primary_slots':primary,'stage1_slots':secondary,'expert_cache_primary_mib':engine.get('expert_cache_primary_mib'),'expert_cache_total_mib':engine.get('expert_cache_mib'),'baseline':budget,'origin':str(folder/'raw/startup.json'),'basis':'Original control startup counters reconciled with separately validated diagnostic slot classes. No old raw file changed.'}
def distribution(xs):
    xs=[x for x in xs if x is not None]
    return {'min':min(xs),'median':statistics.median(xs),'max':max(xs)} if xs else None
def system_decode(run,path):
    begin=run['started_epoch']+run['TTFT_s'];end=run['started_epoch']+run['wall_s']
    rows=[json.loads(line) for line in pathlib.Path(run['telemetry']['path']).read_text().splitlines()]
    rows=[r for r in rows if begin<=r['wall_time']<=end]
    if not rows:return {'samples':0,'limitation':'No decode-range samples'}
    cpu=[sum(p['cpu_pct'] for p in r['processes']) for r in rows]
    result={'samples':len(rows),'window':'First visible token through last HTTP response; 1 Hz resolution, not kernel timing',
            'mean_process_cpu_pct_one_core_basis':statistics.mean(cpu),'mean_process_cpu_pct_16vcpu_basis':statistics.mean(cpu)/16,
            'mean_system_cpu_pct':statistics.mean(r['system_cpu_pct'] for r in rows),
            'peak_sum_rss_gib':max(sum(p['rss_gib'] for p in r['processes']) for r in rows),'gpus':{}}
    for index in (0,1):
        g=[x for r in rows for x in r.get('gpus',[]) if x['index']==index]
        result['gpus'][str(index)]={'mean_util_pct':statistics.mean(x['util_pct'] for x in g),'mean_power_w':statistics.mean(x['power_w'] for x in g),'peak_vram_mib':max(x['vram_mib'] for x in g)} if g else None
    pcie={str(index):[] for index in (0,1)}
    for line in (path/'telemetry/pcie-dmon.log').read_text().splitlines():
        parts=line.split()
        if len(parts)!=5 or not parts[0].isdigit():continue
        try:
            epoch=datetime.datetime.strptime(parts[0]+' '+parts[1],'%Y%m%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp()
            if begin<=epoch<=end:pcie[parts[2]].append((float(parts[3]),float(parts[4])))
        except ValueError:pass
    result['pcie']={k:{'samples':len(v),'mean_RX_printed_MB_s':statistics.mean(x[0] for x in v),'peak_RX_printed_MB_s':max(x[0] for x in v),'mean_TX_printed_MB_s':statistics.mean(x[1] for x in v),'peak_TX_printed_MB_s':max(x[1] for x in v)} if v else None for k,v in pcie.items()}
    result['pcie_interpretation']='Printed dmon MB/s, coarse samples. No per-burst cause or inference-critical-path attribution from 1 Hz alone.'
    return result
records=[];cells=[];comparisons=[]
for profile in ('32k','128k'):
    paired=[]
    for name,folder in [('control',ROOT/'experiments/E002-controls/v1'/profile),('frequency',EXP/'v1'/profile)]:
        valid=[]
        for n in (1,2,3):
            path=folder/'raw'/f'run{n}.json'
            if not path.exists():continue
            r=load(path);row={k:r.get(k) for k in ['variant','state','actual_input_tokens','actual_output_tokens','PP','TG','TTFT_s','wall_s','pp_s','decode_s','reuse','finish_reason','mtp_proposed','mtp_accepted','verify_windows','mtp_acceptance_pct','mtp_accepted_per_window','hit_rate_pct','local_vram_entries','cpu_fallback_entries','offloaded_entries','output_text_sha256','application_status','source_sha','binary_sha256']}
            if not row['output_text_sha256']:row['output_text_sha256']=hashlib.sha256((r.get('reasoning','')+'\0'+r.get('text','')).encode()).hexdigest()
            row.update(profile=profile,configuration=name,run=n,path=str(path),input_ids_sha256=r['payload']['input_ids_sha256'],system_decode=system_decode(r,folder))
            records.append(row)
            if r['state']=='VALID':valid.append(row)
        cell={'profile':profile,'configuration':name,'valid':len(valid),'attempts':len([x for x in records if x['profile']==profile and x['configuration']==name]),
              'statistics':{key:distribution([r.get(key) for r in valid]) for key in ['PP','TG','TTFT_s','wall_s','mtp_acceptance_pct','mtp_accepted_per_window','hit_rate_pct','cpu_fallback_entries','offloaded_entries']},
              'resource':resource_evidence(folder,profile)}
        cells.append(cell)
    control=[x for x in records if x['configuration']=='control' and x['profile']==profile]
    candidate=[x for x in records if x['configuration']=='frequency' and x['profile']==profile]
    for c in candidate:
        b=next(x for x in control if x['run']==c['run'])
        paired.append({'run':c['run'],'same_input_ids':b['input_ids_sha256']==c['input_ids_sha256'],'control_TG':b['TG'],'candidate_TG':c['TG'],'TG_delta_pct':100*(c['TG']/b['TG']-1),'wall_delta_pct':100*(c['wall_s']/b['wall_s']-1),'same_visible_output_hash':b['output_text_sha256']==c['output_text_sha256'] if b['output_text_sha256'] else None})
    bc=next(x for x in cells if x['profile']==profile and x['configuration']=='control');cc=next(x for x in cells if x['profile']==profile and x['configuration']=='frequency')
    delta={key:100*(cc['statistics'][key]['median']/bc['statistics'][key]['median']-1) if cc['statistics'][key] and bc['statistics'][key] else None for key in ['PP','TG','TTFT_s','wall_s']}
    comparisons.append({'profile':profile,'median_delta_pct':delta,'paired_saved_payloads':paired,'capacity_identical':bc['resource']['primary_slots']==cc['resource']['primary_slots'] and bc['resource']['stage1_slots']==cc['resource']['stage1_slots']})
summary={'state':'COMPLETE_NEGATIVE' if all(x['valid']==3 for x in cells) and all(x['median_delta_pct']['TG']<0 for x in comparisons) else 'COMPLETE_MIXED' if all(x['valid']==3 for x in cells) else 'PARTIAL',
         'scope':'One fresh server per profile, equal fixed 64-output warmup, serial three preserved 4096-output workloads. Controls reused unchanged; not three independent fresh-server replicates.',
         'changed_variable':'Existing --adapt-decay 0.7 ->1.0; source base/toolchain/common inference settings and physical cache capacities fixed.',
         'cells':cells,'comparisons':comparisons,'runs':records,
         'unavailable':['exact output token IDs from clean frontend (visible output hashes saved)','live promotion bytes and per-window cache progression without diagnostics','expert-specific SSD logical read counters','teacher-forced KL/top1 parity'],
         'correctness':'Native real-model parity zero failures, Python 268 pass/7 skipped, CTest 62 pass/2 skipped/4 documented environmental failures. Ten saved same-input-ID cases complete, four identical visible outputs; all six textual differences preserved. Numeric/JSON checks pass; no universal bitwise parity claim.',
         'limitations':['Fixed-trace replay starts from observed control post-prefill state; live frequency also changes causal warmup/prefill adaptation history.','Free generation can change because CPU and GPU quantized expert paths round differently; MTP/output trajectory effects are not isolated kernel improvements.','Three serial runs do not establish a tiny universal effect; no additional unchanged repetitions.','Fixed-length output is throughput evidence, not proof the full application task is complete.']}
save(EXP/'summary.json',summary)
columns=['configuration','profile','run','state','actual_input_tokens','actual_output_tokens','PP','TG','TTFT_s','wall_s','mtp_acceptance_pct','mtp_accepted_per_window','hit_rate_pct','cpu_fallback_entries','offloaded_entries','path']
with (EXP/'summary.csv').open('w') as stream:
    writer=csv.DictWriter(stream,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(records)
lines=['# Frequency policy live comparison','',f"Status: {summary['state']}.",'',summary['scope'],'',summary['changed_variable'],'',
       '| Profile | Config | PP median | TG min/median/max | TTFT median s | Wall median s | MTP accept | CPU fallback median | Mapped/remote median |',
       '|---|---|---:|---:|---:|---:|---:|---:|---:|']
for c in cells:
    s=c['statistics'];tg=s['TG']
    if tg:lines.append(f"| {c['profile']} | {c['configuration']} | {s['PP']['median']:.1f} | {tg['min']:.1f} / {tg['median']:.1f} / {tg['max']:.1f} | {s['TTFT_s']['median']:.3f} | {s['wall_s']['median']:.3f} | {s['mtp_acceptance_pct']['median']:.2f}% | {s['cpu_fallback_entries']['median']} | {s['offloaded_entries']['median']} |")
lines+=['','The startup capacity check passes at both profiles. Predictor GPU/host allocation added by the supported decay option is zero. Exact slot-class byte budgets are linked in analysis/control-budgets-v2.json and each raw resource-check.json. No K/cache/MTP/worker/PCIe tuning was performed.','',summary['correctness'],'',
        'The six differing short answers have coherent preserved differences (phrasing, formatting and worked example choice); mathematics remains correct and both strict JSON cases parse to the requested values. This is basic correctness evidence, not an automatic quality ranking or proof that all numerical divergence is harmless.','',
        'All run statistics, decode-only CPU/GPU/power/PCIe samples and per-payload comparisons are in summary.json. Decode telemetry spans first visible token through the response end at 1 Hz. CPU is reported on both one-core and 16-vCPU bases. PCIe bursts have no causal attribution from these samples. Unknown expert-file counters remain unavailable.','']
for x in comparisons:lines.append(f"{x['profile']} median deltas (%): `{x['median_delta_pct']}`. Saved-input comparisons: `{x['paired_saved_payloads']}`.")
lines+=['','Do not select this policy solely from the offline nonlocal reduction. The real goal is latency/TG with correct execution. Preserve the slower candidate and its executable launchers. Investigate its free-generation/MTP/cache history before claiming cache accounting implies a speed gain.','',
        'Next: bounded diagnostic frequency trace at both profiles if needed to explain the loss; actual boundary/router availability study, and compatible-slot placement replay. Do not repeat the unchanged headline points.','',
        'Reproduce: variants/frequency-v1-ready/reproduce.sh --experiment NEW_EXPERIMENT --attempt v1. Within the original campaign, the three-attempt limit remains binding; launcher paths/binary hashes/configs are frozen. Manual starts remain available without updating/rebuilding.']
(EXP/'report.md').write_text('\n'.join(lines)+'\n')
print(summary['state'],[(x['profile'],x['median_delta_pct']) for x in comparisons],flush=True)
