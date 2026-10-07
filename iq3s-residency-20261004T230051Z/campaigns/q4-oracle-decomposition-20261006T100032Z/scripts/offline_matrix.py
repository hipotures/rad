import os,json,csv
from owned import C,run
env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(STRATA_Q4_TAPE=str(C/'tapes/capture-32k-v3.bin'),STRATA_Q4_TAPE_MODE='replay')
arms=[('full','full')]+[(str(h),'full') for h in [4,16,64,256]]+ [('full',str(h)) for h in [4,16,64,256]]+[('64','64')]
rows=[]
for i,v in arms:
 env.update(STRATA_Q4_ORACLE_INCOMING=i,STRATA_Q4_ORACLE_VICTIM=v)
 p=run('offline-I'+i+'-V'+v,[C/'analysis/offline','transfer','0','0'],env=env,timeout=180,area='phase-b')
 row=json.loads((p/'stdout.log').read_text());row['I']=i;row['V']=v;row['measurement_kind']='MODELED_TRANSFER_SIMULATION_NOT_INFERENCE_TG';row['physical_spares']=5;row['restoration_bytes']=17305600;row['modeled_exposed_latency']='UNAVAILABLE: fixed event pacing with queued measured-cost assumptions, no causal critical-path model';rows.append(row)
 (C/'phase-b/offline-summary.json').write_text(json.dumps(rows,indent=2)+'\n')
 print('OFFLINE_ROW',i,v,row['cpu']+row['mapped'],row['copied_bytes']/1e9,row['victim_absent_observations'],flush=True)
keys=sorted(set().union(*(r.keys() for r in rows)))
with (C/'phase-b/offline-summary.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
full=rows[0];i64=next(r for r in rows if r['I']=='64' and r['V']=='full')
match=all(full[k]==i64[k] for k in ['issued','copied_bytes','published','local','cpu','mapped','victim_absent_observations','target_ready_demand'])
(C/'phase-b/incoming64-mechanistic-match.json').write_text(json.dumps({'exact_deterministic_match':match,'reason':'First-feasible selection ignores its computed reuse utility; E64 unchanged at I>=64.'},indent=2)+'\n')
assert match,'Unexpected incoming64 effect; audit before live'
