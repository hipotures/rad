"""Raw-derived paired decomposition, no historical arm or favorable exclusions."""
import json,re,csv,statistics,collections,numpy as np
from pathlib import Path
from tape import Tape
from inspect_oracle import E
from system_metrics import analyze as system
from event_diagnostics import analyze as events
from progression import analyze as progress
C=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def stat(v):
 v=[x for x in v if x is not None];return {'min':min(v),'median':statistics.median(v),'max':max(v)} if v else None
def parse_kv(log,marker):
 m=re.search(marker+r' ([^\n]+)',log);return {k:(float(v) if '.' in v else int(v) if re.fullmatch(r'-?\d+',v) else v) for k,v in re.findall(r'(\w+)=([^ ]+)',m[1])} if m else {}
def row(label):
 p=C/'raw'/label;r=load(p/'results.json')['runs'][0];cfg=r['full_config'];tape=Path(cfg['env']['STRATA_Q4_TAPE']);o=load(C/'analysis'/f'{label}-oracle.json');f=load(C/'phase-a'/f'{label}-fidelity.json');log=(p/'raw/run-engine.log').read_text();end=parse_kv(log,'Q4_ORACLE_END');info=parse_kv(log,'Q4_INFORMATION_END')
 sys=system(label,tape);ev=events(label,tape);pg=progress(label,tape)
 obs=np.fromfile(p/'raw/observations.bin',Tape(tape).obs_dtype);n=len(obs);lo=n//4;hi=3*n//4
 interior={'window_start_inclusive':lo,'window_stop_exclusive':hi,'wall_s':(int(obs['end_ns'][hi-1])-int(obs['begin_ns'][lo]))/1e9,'censoring':'Middle50% predefined; no cleanup excluded from whole request. Logical-output measure uses recorded accepted+1 advances and can differ from visible final4096 normalization.'}
 t=Tape(tape);interior['logical_committed_advances']=int((t.ws['accepted'][lo:hi]+1).sum());interior['equivalent_advances_s']=interior['logical_committed_advances']/interior['wall_s']
 io=f['initial_state'];sp=cfg['variant_overrides'];count=o['demand'];copies=o['copies'];entry={'label':label,'profile':r['profile'],'E':64,'I':sp['I'],'V':sp['V'],'policy':'current' if sp['oracle']=='off' else sp['I']+'/'+sp['V'],'unknown_fallback':sp['unknown_fallback'],'state':r['state'],'fidelity':f['state'],'ownership':o['state'],'actual_input':r['actual_input_tokens'],'recorded_output':r['actual_output_tokens'],'decode_s':r['decode_s'],'replay_equivalent_tok_s':r['actual_output_tokens']/r['decode_s'],'PP':r['PP'],'prefill_s':r['pp_s'],'TTFT_s':r['TTFT_s'],'wall_s':r['wall_s'],'local_pct':100*count['local']/sum(count.values()),'local_entries':count['local'],'CPU_entries':count['cpu'],'mapped_entries':count['mapped'],'nonlocal_entries':count['cpu']+count['mapped'],'copy_GB':(copies['completed_bytes']+copies['native_published_bytes']+copies['restoration_bytes'])/1e9,'native_GB':copies['native_published_bytes']/1e9,'oracle_GB':copies['completed_bytes']/1e9,'victim_absent_entries':copies['victim_absent'],'issued':copies['issued'],'published':copies['published'],'ready_publications':copies['ready_publications'],'late_publications':copies['late_publications'],'actual_target_ready_entries':end.get('target_ready_entries'),'late_useful_entries':end.get('late_useful_entries'),'unpublished_GB':copies['unpublished_bytes']/1e9,'unused_GB':copies['unused_bytes']/1e9,'planner_ms':end.get('planner_ms'),'publication_ms':end.get('publication_ms'),'drain_ms':end.get('drain_ms'),'restoration_ms':end.get('restoration_ms'),'future_index_setup_ms':end.get('setup_ms'),'tape_lookup_ms':f['lookup_ms'],'attestation_ms':io.get('setup_ms') if io else None,'VM_CPU':sys['system_cpu_pct']['mean'],'process_CPU':sys['process_cpu_pct']['mean'],'CPU_steal':sys['cpu_steal_pct']['mean'],'GPU0':sys['gpus']['0']['util_pct']['mean'],'GPU1':sys['gpus']['1']['util_pct']['mean'],'queries':info,'interior':interior,'raw_path':str(p),'tape':str(tape),'work_manifest':f['tape'],'initial_state':io,'native_head_agreement':f['native_main_head_agreement'],'selected_activation_check':f['selected_activation_check'],'copies':copies,'copy_lead':ev['future_lead'],'cpu_completion_spans':ev['host_quant_group_compute_completion_span'],'physical_KV':f['physical_KV_summary'],'system':sys,'progression':pg}
 for k,h in [('incoming_max_visible',sp['I']),('victim_max_visible',sp['V'])]:
  if h!='full':assert info[k]<=int(h),(label,k,h,info[k])
 assert copies['pending_at_end']==0, (label, 'undrained pending copy')
 return entry
def main():
 rows=[];extras=[]
 for p in sorted((C/'raw').glob('v2-*/results.json')):
  label=p.parent.name
  if not re.fullmatch(r'v2-(32k|128k|256k)-(current|FF|64F|F64|6464|F256)-attempt[1-3]',label):continue
  print('ANALYZE_PROGRESS',label,flush=True)
  x=row(label);m=re.fullmatch(r'v2-(32k|128k|256k)-(\w+)-attempt([1-3])',label);x.update(arm=m[2],attempt=int(m[3]));rows.append(x)
 grouped=collections.defaultdict(list)
 for x in rows:grouped[x['profile'],x['arm']].append(x)
 metrics=['PP','prefill_s','decode_s','replay_equivalent_tok_s','TTFT_s','wall_s','local_pct','CPU_entries','mapped_entries','nonlocal_entries','copy_GB','victim_absent_entries','ready_publications','late_publications','actual_target_ready_entries','late_useful_entries','planner_ms','tape_lookup_ms','attestation_ms','VM_CPU','process_CPU','CPU_steal','GPU0','GPU1','future_index_setup_ms']
 cells=[]
 for (profile,arm),rs in grouped.items():
  cells.append({'profile':profile,'arm':arm,'E':rs[0]['E'],'I':rs[0]['I'],'V':rs[0]['V'],'attempts':len(rs),'valid':sum(x['state']=='VALID' and x['fidelity']=='PASS' and x['ownership']=='PASS' for x in rs),'metrics':{k:stat([x[k] for x in rs]) for k in metrics},'rows':[x['label'] for x in rs]})
 by={(x['profile'],x['attempt'],x['arm']):x for x in rows};pairs=[];interactions=[]
 for x in rows:
  c=by.get((x['profile'],x['attempt'],'current'));full=by.get((x['profile'],x['attempt'],'FF'))
  if c is None or full is None:continue
  denom=c['decode_s']-full['decode_s'];ret=(c['decode_s']-x['decode_s'])/denom if denom>max(.1,.003*c['decode_s']) else None
  pairs.append({'profile':x['profile'],'attempt':x['attempt'],'arm':x['arm'],'current_label':c['label'],'full_label':full['label'],'candidate_label':x['label'],'TG_ratio_vs_current':c['decode_s']/x['decode_s'],'decode_ms_saved':1000*(c['decode_s']-x['decode_s']),'full_saved_ms':1000*denom,'gain_retention':ret,'unstable_retention':ret is None,'wall_ratio_vs_current':x['wall_s']/c['wall_s'],'interior_speed_ratio_vs_current':c['interior']['wall_s']/x['interior']['wall_s']})
 for attempt in [1,2,3]:
  rr={a:by.get(('32k',attempt,a)) for a in ['FF','64F','F64','6464']}
  if all(rr.values()):interactions.append({'attempt':attempt,'decode_interaction_ms':1000*(rr['6464']['decode_s']-rr['64F']['decode_s']-rr['F64']['decode_s']+rr['FF']['decode_s']),'mechanism':'Descriptive matched interaction, not linear causal coefficient; I64 does not affect deterministic decisions in first-feasible policy.'})
 for cell in cells:
  ps=[x for x in pairs if x['profile']==cell['profile'] and x['arm']==cell['arm']];cell['paired']={k:stat([p[k] for p in ps]) for k in ['TG_ratio_vs_current','gain_retention','decode_ms_saved','wall_ratio_vs_current','interior_speed_ratio_vs_current']}
 summary={'state':'DERIVED','same_tape_per_profile':'Timing repeatability, not task diversity','serving_baseline':'Unchanged Q4/K24/.28/100us','rows':rows,'cells':cells,'pairs':pairs,'interaction':interactions,'excluded':'No timing outlier exclusions; failures remain retained and listed separately.'}
 save(C/'summary.json',summary)
 keys=['profile','arm','attempt','E','I','V']+metrics
 with (C/'summary.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(rows)
 save(C/'analysis/paired-comparisons.json',{'pairs':pairs,'interactions':interactions})
 print('DERIVED',len(rows),'requests',len(cells),'cells')
 for c in cells:print(c['profile'],c['arm'],c['metrics']['replay_equivalent_tok_s'],c['paired']['gain_retention'])
if __name__=='__main__':main()
