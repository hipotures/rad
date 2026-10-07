"""P0 paired analysis; incomplete/early requests never become fixed-length medians."""
import csv, hashlib, json, statistics
from lab import ROOT, load, save
base=ROOT/'experiments/E027-pool-baseline'
def dist(v):
    v=[x for x in v if x is not None]
    return {'min':min(v),'median':statistics.median(v),'max':max(v)} if v else None
def phase(r):
    lo=r['started_epoch']+r['TTFT_s'];hi=r['started_epoch']+r['wall_s']
    rows=[json.loads(x) for x in open(r['telemetry']['path'])]
    decode=[x for x in rows if lo<=x['wall_time']<hi]
    def avg(v):return statistics.mean(v) if v else None
    return {'samples':len(decode),'CPU_VM_mean_pct':avg([x['system_cpu_pct'] for x in decode]),'CPU_process_mean_one_core_100':avg([sum(y['cpu_pct'] for y in x['processes']) for x in decode if x['processes']]),'GPU_mean_pct':{str(i):avg([g['util_pct'] for x in decode for g in x.get('gpus',[]) if g['index']==i]) for i in (0,1)},'CPU_positive_completion_wait_us':'UNAVAILABLE_HEADLINE; separate selected-layer diagnostics required','all_local_wait_us':'UNAVAILABLE_HEADLINE','physical_read_bytes_delta':max([sum(p['read_bytes'] for p in x['processes']) for x in decode],default=0)-min([sum(p['read_bytes'] for p in x['processes']) for x in decode],default=0) if len(decode)>1 else None}
cells=[];pairs=[];complete=True
keys=['PP','TG','TTFT_s','wall_s','actual_input_tokens','actual_output_tokens','mtp_proposed','mtp_accepted','mtp_acceptance_pct','verify_windows','hit_rate_pct','local_vram_entries','cpu_fallback_entries','offloaded_entries','CPU_VM_mean_pct','CPU_process_mean_one_core_100']
for family in ['standard']:
    for profile in ['32k','128k']:
        roles={}
        for role in ['default','sleep100us']:
            runs=[];paths=[]
            for n in [1,2,3]:
                p=base/'v1'/family/profile/role/f'rep{n}'/'raw/run.json'
                if not p.exists():continue
                r=load(p);paths.append(str(p));r['system_decode']=phase(r);r.update({k:v for k,v in r['system_decode'].items() if k in keys});runs.append(r)
            valid=[r for r in runs if r['state']=='VALID'];complete&=len(runs)==3
            cell={'experiment':'E027-pool-baseline','phase':'P1','family':family,'profile':profile,'role':role,'attempts':len(runs),'valid_fixed_length':len(valid),'raw_paths':paths,'invalid':[{'raw':str(p),'reason':r.get('invalid_reasons'),'finish_reason':r.get('finish_reason'),'output':r.get('actual_output_tokens')} for p,r in zip(paths,runs) if r['state']!='VALID'],'metrics':{k:dist([r.get(k) for r in valid]) for k in keys},'application_metrics':{k:dist([r.get(k) for r in runs if r.get('TG') and r.get('finish_reason')!='error']) for k in ['wall_s','TTFT_s','actual_output_tokens','TG']},'decode_telemetry':[r['system_decode'] for r in runs]}
            cells.append(cell);roles[role]=runs
        for n,(b,c) in enumerate(zip(roles['default'],roles['sleep100us']),1):
            ids_b=load(b['actual_output_ids_path']) if b.get('actual_output_ids_path') else []
            ids_c=load(c['actual_output_ids_path']) if c.get('actual_output_ids_path') else []
            prefix=next((i for i,(x,y) in enumerate(zip(ids_b,ids_c)) if x!=y),min(len(ids_b),len(ids_c)))
            pairs.append({'family':family,'profile':profile,'replicate':n,'same_binary':b['binary_sha256']==c['binary_sha256'],'same_input_IDs':b['payload']['input_ids_sha256']==c['payload']['input_ids_sha256'],'same_actual_output_IDs':ids_b==ids_c and bool(ids_b),'common_output_prefix_tokens':prefix,'same_MTP':all(b.get(k)==c.get(k) for k in ['mtp_proposed','mtp_accepted','verify_windows']),'same_normal_routing':all(b.get(k)==c.get(k) for k in ['local_vram_entries','cpu_fallback_entries','offloaded_entries']),'same_capacity':load(__import__('pathlib').Path(b['telemetry']['path']).parents[1]/'raw/resource-check.json')['primary_slots']==load(__import__('pathlib').Path(c['telemetry']['path']).parents[1]/'raw/resource-check.json')['primary_slots'],'TG_delta_pct':100*(c['TG']/b['TG']-1) if b.get('TG') and c.get('TG') else None,'wall_delta_pct':100*(c['wall_s']/b['wall_s']-1) if b.get('wall_s') and c.get('wall_s') else None,'both_fixed_length_valid':b['state']==c['state']=='VALID','baseline_CPU_entries':b.get('cpu_fallback_entries'),'baseline_output':b.get('actual_output_tokens')})
deltas=[]
for family in ['standard']:
    for profile in ['32k','128k']:
        a=[x for x in pairs if x['family']==family and x['profile']==profile]
        if a:deltas.append({'family':family,'profile':profile,'n':len(a),'TG_delta_pct':dist([x['TG_delta_pct'] for x in a]),'wall_delta_pct':dist([x['wall_delta_pct'] for x in a]),'CPU_entries':dist([x['baseline_CPU_entries'] for x in a])})
state='COMPLETE_MEASUREMENTS' if complete else 'RUNNING'
result={'state':state,'cells':cells,'paired':pairs,'paired_deltas':deltas,'decision':'PENDING_DIAGNOSTICS_AND_REVIEW','limits':['Fresh-server paired3replicates; no extras or favorable retries.','Different documents/tasks and application latency matter; all natural EOS kept.','One-Hz phase boundaries use clientTTFT, not exactGPUkernel timing.','Actual engine outputIDs captured by common Python wrapper, enginebinary unchanged.','Wait timings unavailable in headline; diagnostic event binary separate.','No logical expert file-read counter inferred from physical processreadbytes.']}
save(base/'summary.json',result)
rows=[]
for c in cells:
    row={k:c[k] for k in ['phase','family','profile','role','attempts','valid_fixed_length']}
    for k,v in c['metrics'].items():row[k+'_median']=v['median'] if v else None
    rows.append(row)
with (base/'summary.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
text='# E027: P1 paired standard-workload confirmation\n\nState: '+state+'. Decision pending wait diagnostics and paired review.\n\n'
text+='| Family | Context | Policy | Valid/attempts | PP | TG | TTFTs | Walls | Decode VMCPU% | CPUentries |\n|---|---|---|---:|---:|---:|---:|---:|---:|---:|\n'
for c in cells:
    def v(k,fmt='.1f'):
        d=c['metrics'][k];return format(d['median'],fmt) if d else 'unavailable'
    text+=f'| {c["family"]} | {c["profile"]} | {c["role"]} | {c["valid_fixed_length"]}/{c["attempts"]} | {v("PP")} | {v("TG")} | {v("TTFT_s",".3f")} | {v("wall_s",".3f")} | {v("CPU_VM_mean_pct")} | {v("cpu_fallback_entries",".0f")} |\n'
text+='\nActual input/output IDs and per-pair checks are in summary.json. Early endings excluded from fixed-length table, retained in application_metrics. '+ '\n\n'.join(result['limits'])+'\n'
(base/'report.md').write_text(text)
print(state,len(pairs),'pairs',sum(c['attempts'] for c in cells),'requests',flush=True)
for d in deltas:print(d,flush=True)
