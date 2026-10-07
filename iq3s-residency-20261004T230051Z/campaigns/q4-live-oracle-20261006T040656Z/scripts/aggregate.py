"""Recompute audited paired summaries from immutable raw records; no historical control substitution."""
from pathlib import Path
import json,re,csv,statistics,argparse
C=Path(__file__).resolve().parents[1]
def stats(v):
 return {'min':min(v),'median':statistics.median(v),'max':max(v)} if v else None
def rows(version='v3'):
 out=[]
 for profile in ['32k','128k','256k']:
  for policy in ['current','oracle']:
   for attempt in [1,2,3]:
    label=f'{version}-{policy}-{profile}-attempt{attempt}';p=C/'raw'/label
    if not (p/'results.json').exists():continue
    r=json.loads((p/'results.json').read_text())['runs'][0];f=json.loads((C/'phase-a'/f'{label}-fidelity.json').read_text());a=json.loads((C/'analysis'/f'{label}-oracle.json').read_text());hw=json.loads((C/'analysis'/f'{label}-system.json').read_text());log=(p/'raw/run-engine.log').read_text();end=re.search(r'Q4_ORACLE_END ([^\n]+)',log);timers=dict(re.findall(r'(\w+)=([^ ]+)',end[1])) if end else {}
    row={'label':label,'profile':profile,'policy':'REPLAY_CURRENT' if policy=='current' else 'REPLAY_ORACLE_FULL','attempt':attempt,'valid':r['state']=='VALID' and f['state']=='PASS' and a['state']=='PASS' and bool(f.get('initial_state',{}).get('match')),'source_sha':r['source_sha'],'binary_sha256':r['binary_sha256'],'work_sha256':f['tape']['work_sha256'],'actual_input_tokens':r['actual_input_tokens'],'output_tokens':r['actual_output_tokens'],'main_events':f['tape']['main_routed_events'],'MTP_events':f['tape']['MTP_full_routed_events'],'KV_commit_position_advances':f['tape']['committed_in_state_prefix'],'PP':r['PP'],'prefill_s':r['pp_s'],'decode_s':r['decode_s'],'replay_equivalent_tok_s':r['actual_output_tokens']/r['decode_s'],'TTFT_s':r['TTFT_s'],'wall_s':r['wall_s'],'setup_attestation_s':f['initial_state']['setup_ms']/1000,'replay_lookup_ms':f['lookup_ms'],'local_entries':a['demand']['local'],'CPU_entries':a['demand']['cpu'],'mapped_entries':a['demand']['mapped'],'local_pct':100*a['demand']['local']/sum(a['demand'].values()),'copy_GB':(a['copies']['completed_bytes']+a['copies'].get('native_published_bytes',a['copies']['native_bytes'])+a['copies'].get('restoration_bytes',0))/1e9,'oracle_copy_GB':a['copies']['completed_bytes']/1e9,'native_copy_GB':a['copies'].get('native_published_bytes',a['copies']['native_bytes'])/1e9,'native_pending_bytes':a['copies'].get('native_pending_bytes'),'restoration_bytes':a['copies'].get('restoration_bytes'),'initial_donor_absent_entries':a['copies'].get('initial_donor_absent_entries'),'target_ready_demand_entries':int(timers['target_ready_entries']) if 'target_ready_entries' in timers else None,'late_useful_demand_entries':int(timers['late_useful_entries']) if 'late_useful_entries' in timers else None,'ready_publications':a['copies']['ready_publications'],'late_publications':a['copies']['late_publications'],'victim_absent':a['copies']['victim_absent'],'resident_demand_entries_after_admission':a['copies']['uses'],'unused_bytes':a['copies']['unused_bytes'],'published':a['copies']['published'],'MTP_proposed':r['mtp_proposed'],'MTP_accepted':r['mtp_accepted'],'verify_windows':r['verify_windows'],'planner_ms':float(timers.get('planner_ms',0)) if end else None,'publication_ms':float(timers.get('publication_ms',0)) if end else None,'drain_ms':float(timers.get('drain_ms',0)) if end else None,'restore_ms':float(timers.get('restoration_ms',0)) if end else None,'future_index_setup_ms':float(timers.get('setup_ms',0)) if end else None,'CPU_mean_decode_pct':hw['system_cpu_pct']['mean'] if hw['system_cpu_pct'] else None,'GPU0_mean_decode_pct':hw['gpus']['0']['util_pct']['mean'] if hw['gpus']['0']['util_pct'] else None,'GPU1_mean_decode_pct':hw['gpus']['1']['util_pct']['mean'] if hw['gpus']['1']['util_pct'] else None,'initial_state_hash':f['initial_state']['SHA256'],'first_natural_head_divergence':f['native_head_first_divergence'],'raw':str(p.relative_to(C))}
    out.append(row)
 return out
def generate(version='v3'):
 data=rows(version);cells=[];paired=[]
 metrics=['PP','prefill_s','decode_s','replay_equivalent_tok_s','TTFT_s','wall_s','setup_attestation_s','replay_lookup_ms','local_pct','CPU_entries','mapped_entries','copy_GB','oracle_copy_GB','native_copy_GB','ready_publications','late_publications','victim_absent','planner_ms','publication_ms','drain_ms','restore_ms','CPU_mean_decode_pct','GPU0_mean_decode_pct','GPU1_mean_decode_pct']
 for profile in ['32k','128k','256k']:
  for policy in ['REPLAY_CURRENT','REPLAY_ORACLE_FULL']:
   rr=[r for r in data if r['profile']==profile and r['policy']==policy and r['valid']];cell={'profile':profile,'policy':policy,'valid':len(rr),'attempts':len([r for r in data if r['profile']==profile and r['policy']==policy]),'labels':[r['label'] for r in rr],'metrics':{m:stats([r[m] for r in rr if r[m] is not None]) for m in metrics}};cells.append(cell)
  pairs=[]
  for n in [1,2,3]:
   rr=[r for r in data if r['profile']==profile and r['attempt']==n and r['valid']]
   if len(rr)!=2:continue
   a=next(x for x in rr if x['policy']=='REPLAY_CURRENT');b=next(x for x in rr if x['policy']=='REPLAY_ORACLE_FULL');assert a['work_sha256']==b['work_sha256'] and a['initial_state_hash']==b['initial_state_hash'];pairs.append({'attempt':n,'decode_time_oracle_over_current':b['decode_s']/a['decode_s'],'throughput_oracle_over_current':a['decode_s']/b['decode_s'],'wall_oracle_over_current':b['wall_s']/a['wall_s']})
  paired.append({'profile':profile,'pairs':pairs,'median_of_paired_ratios':{m:statistics.median([p[m] for p in pairs]) if pairs else None for m in ['decode_time_oracle_over_current','throughput_oracle_over_current','wall_oracle_over_current']}})
 complete=len(data)==18 and all(r['valid'] for r in data);out={'state':'COMPLETE' if complete else 'PARTIAL','version':version,'headline_contract':'Full main/MTP/QSA fixedwork, strictly attested initial state; same common binary per arm; forced output not production generation','timing_repeatability':'One tape repeated three times per context, not task diversity','rows':data,'cells':cells,'paired':paired,'practical_control':'Unchanged frozen Q4/100us original binary remains real-use configuration','timer_caveat':'Online planner includes publication wait; overlapping wall/timers are never summed. Attestation setup/drain/restoration included in total wall.'};(C/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
 if data:
  with (C/'summary.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 print('SUMMARY',out['state'],len(data),'valid',sum(x['valid'] for x in data),flush=True);return out
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--version',default='v3');v=a.parse_args();generate(v.version)
