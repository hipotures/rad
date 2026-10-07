"""Regenerate compact results from immutable records into a fresh output directory."""
import argparse,json,statistics,re,hashlib,csv
from pathlib import Path
import numpy as np
from trace_io import P,H,read_gpu,identity_check
from protocol_rules import perturbation_gate,notify_tail
from dependency_graph import conservative_counterfactual_bound

def load(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def quant(v):return dict(zip(['min','median','p95','max'],map(float,np.quantile(v,[0,.5,.95,1])))) if len(v) else None

def mapping(g,values):
 cal=g['rows'][8];a,b=map(int,cal['begin']);lo0,hi0,lo1,hi1=g['host_brackets'];assert b>a
 f=(np.asarray(values,dtype=np.float64)-a)/(b-a)
 # Bounded affine interpolation, conditional on affine clocks. No unjustified midpoint attribution.
 return (1-f)*lo0+f*lo1,(1-f)*hi0+f*hi1,[(lo1-hi0)/(b-a),(hi1-lo0)/(b-a)]

def analyze_trace(p,version,decode):
 prefix=p/'raw/oracle';check=identity_check(prefix,version);assert check['state']=='PASS',check
 pub=np.fromfile(str(prefix)+'-publication-trace.bin',P);host=np.fromfile(str(prefix)+'-producer-trace.bin',H);gpu=[read_gpu(str(prefix)+f'-gpu{d}-trace.bin') for d in [0,1]]
 ack=[int(x['wait_end'])-int(x['wait_begin']) for x in pub];primary=[notify_tail(*[int(x[k]) for k in ['wait_end','notify_unlock_return','cpu_begin','cpu_end']]) for x in pub];ideal=[max(0,int(x['wait_end'])-int(x['command_available'])) for x in pub]
 worker={name:sum(max(0,int(x[b])-int(x[a])) for x in pub)/1e6 for name,a,b in [('command_to_observed','command_available','worker_observed'),('worker_setup','worker_observed','metadata_submit'),('metadata_submit_to_cuda_observation','metadata_submit','cuda_observed'),('completion_to_ack_state','cuda_observed','ack_state'),('state_to_notify_unlock_return','ack_state','notify_unlock_return')]}
 byevent={}
 for x in pub:byevent.setdefault(int(x['event']),[]).append(x)
 overlap=[0.,0.];totalA=[0.,0.];devs=[];main_span=[0.,0.]
 for g in gpu:
  d=g['device'];A=g['rows'][0];bLo,bHi,scale=mapping(g,A['begin']);eLo,eHi,_=mapping(g,A['end']);dur=(A['end']-A['begin']).astype(np.float64);lower=upper=0.;contradictions=0
  for i,r in enumerate(A):
   event=(i//24)*48+d*24+int(r['ring'])-1;assert event==int(host[event]['event']) and host[event]['flag_before']>0
   xs=byevent.get(event,[]);l=sum(max(0,int(x['wait_end'])-max(int(x['wait_begin']),bHi[i])) for x in xs);u=sum(max(0,int(x['wait_end'])-max(int(x['wait_begin']),bLo[i])) for x in xs)
   lower+=min(l,dur[i]*scale[0]);upper+=min(u,dur[i]*scale[1]);contradictions+=int(eHi[i]<int(host[event]['flag_before']))
  wait=[int((g['rows'][k]['end']-g['rows'][k]['begin']).sum()) for k in [0,1,2]];s=g['rows'][4];c=g['rows'][7];cpu=g['rows'][2]
  # Math completion is a lower readiness observation; stream/join/retirement remain required.
  math_before_cpu_end=int(np.count_nonzero(s['end']<cpu['end']));join_interval_upper=np.maximum(0,c['begin'].astype(np.int64)-cpu['end'].astype(np.int64))
  wd=(g['rows'][10]['end']-g['rows'][9]['begin']).astype(np.float64).sum();main_span[0]+=wd*scale[0];main_span[1]+=wd*scale[1]
  totalA[0]+=dur.sum()*scale[0];totalA[1]+=dur.sum()*scale[1];overlap[0]+=lower;overlap[1]+=upper
  devs.append({'device':d,'wait_ns':dict(zip(['A','B','CPU'],wait)),'wait_A_us':quant(dur/1000),'ack_overlap_ms_interval':[lower/1e6,upper/1e6],'clock_bracket_us':[(g['host_brackets'][1]-g['host_brackets'][0])/1000,(g['host_brackets'][3]-g['host_brackets'][2])/1000],'clock_scale_interval':scale,'clock_order_contradictions':contradictions,'linked_wait_A_pct':100,'shared_math_complete_before_CPU_wait_end_count':math_before_cpu_end,'shared_endpoint_limit':'Math-store completion precedes kernel retirement; this count is not a proof of shared join completion or exact masked latency.','CPU_end_to_combine_begin_ms':float(join_interval_upper.sum()/1e6),'GPU_main_stage_span_ms':float(wd/1e6),'unsupported':['Exact doorbell GPU publication time','Exact shared event completion time','Prejoin endpoint in v2','Commit/MTP/host-gap dependency edges outside verifier stage']})
 outside=[max(0,decode-main_span[1]/1e9),max(0,decode-main_span[0]/1e9)]
 return {'identity':check,'publication_ack_ms':sum(ack)/1e6,'publication_ack_us':quant(np.array(ack)/1000),'publication_generations':len(pub),'multiple_publications_per_hook':sum(len(x)>1 for x in byevent.values()),'cross_device_publications':sum(int(x['device'])!=int(x['event'])%48//24 for x in pub),'worker_subphases_ms_nested':worker,'primary_removed_ms':sum(primary)/1e6,'idealized_removed_ms':sum(ideal)/1e6,'primary_counterfactual_decode_s_interval':[max(0,decode-sum(primary)/1e9),decode],'idealized_counterfactual_decode_s_interval':[max(0,decode-sum(ideal)/1e9),decode],'primary_S_interval':conservative_counterfactual_bound(primary,decode),'idealized_S_interval':conservative_counterfactual_bound(ideal,decode),'interval_definition':'Fixed-scenario longest-path shortening upper bound is sum of removed durations. Missing/unsupported competing dependencies allow zero lower contribution. These are conservative evidence bounds, not intervention-strength ranges or statistical confidence intervals. Perturbed TRACE trajectories cannot estimate the uninstrumented baseline quantitatively.','ack_overlap_ms_interval':list(np.array(overlap)/1e6),'ack_fraction_of_wait_A_interval':[overlap[0]/totalA[1],min(1,overlap[1]/totalA[0])],'devices':devs,'completion_graph':{'state':'PARTIAL_NOT_QUANTITATIVELY_CLOSED','known':'Stream order; host acknowledgment then ownership/native flag A; B/CPU readiness; shared fork/join; serial mapped K24 handoff; captured graph ordinal/window identity','outside_main_verifier_span_s_interval':outside,'unassigned_completion_fraction_interval':list(np.array(outside)/decode),'full_completion_residual':'Unresolved: opaque commit/draft/host gaps are observed in total span but their internal dependency edges are not reconstructed. Adding them as fixed slack would fit baseline by construction and is not a validated full graph.','primary_path_contribution_interval_s':[0,sum(primary)/1e9],'idealized_path_contribution_interval_s':[0,sum(ideal)/1e9]},'clock_limit':'Affine start/end bracket interpolation is conditional; two samples do not independently bound interior drift. No cross-GPU raw clock subtraction.','producer_phase_ms':{'hook':float((host['hook_end']-host['hook_begin']).sum()/1e6),'publication_loop_including_non_ack_checks':float((host['publications_end']-host['hook_begin']).sum()/1e6),'remaining_incoming_planning':float((host['hook_end']-host['publications_end']).sum()/1e6),'native_source_plan_until_flag_A':float((host['flag_before']-host['hook_end']).sum()/1e6)}}

def main():
 q=argparse.ArgumentParser();q.add_argument('--raw-root',required=True,type=Path);q.add_argument('--output',required=True,type=Path);args=q.parse_args();args.output.mkdir(parents=True,exist_ok=False);rows=[]
 for p in sorted(args.raw_root.glob('*')):
  if not (p/'episode.json').exists():continue
  ep=load(p/'episode.json');log=(p/'raw/run-engine.log').read_text();r=ep['run'];tokens=lambda prefix:{k:float(v) for k,v in re.findall(r'(\w+)=([0-9.]+)',next(x for x in log.splitlines() if x.startswith(prefix)))}
  tele=[json.loads(s) for s in (p/'telemetry/run.jsonl').read_text().splitlines()];row={'label':p.name,'version':2 if p.name.startswith('v2-') else 1,'arm':ep['arm'],'valid':ep['valid'],'decode_s':r['decode_s'],'wall_s':r['wall_s'],'TG':r['TG'],'PP':r['PP'],'prefill_s':r['actual_input_tokens']/r['PP'],'operating_s':ep['total_operating_s'],'startup_s':ep['startup_s'],'warmup_s':ep['warmup_s'],'cleanup_s':ep['cleanup_s'],'fidelity':ep['fidelity'],'ownership':ep['ownership'],'oracle':tokens('Q4_ORACLE_END'),'planner':tokens('Q4_PLANNER_END'),'information':tokens('Q4_INFORMATION_END'),'telemetry':{'steal_pct':quant([t['cpu_times_percent']['steal'] for t in tele]),'system_cpu_pct':quant([t['system_cpu_pct'] for t in tele]),'RAM_used_gib':quant([t['ram_used_gib'] for t in tele]),'RAM_available_gib':quant([t['mem_available_gib'] for t in tele]),'swap_used_bytes_max':max(t['swap_memory']['used'] for t in tele),'GPU':{str(d):{k:quant([t['gpus'][d][k] for t in tele if len(t['gpus'])>d]) for k in ['util_pct','power_w','vram_mib','sm_mhz','memory_mhz']} for d in [0,1]}},'wait':[]}
  for x in log.splitlines():
   if x.startswith('Q4_WAIT_END'):row['wait'].append({k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',x)})
  assert row['information']['victim_next']==row['information']['victim_count']==0
  if ep['arm']=='TRACE':row['attribution']=analyze_trace(p,row['version'],r['decode_s'])
  row['raw_hashes']={str(x.relative_to(p)):hashlib.file_digest(x.open('rb'),'sha256').hexdigest() for x in p.glob('raw/*trace.bin')};rows.append(row)
 pairs=[]
 for block in [1,2,3]:
  members={r['arm']:r for r in rows if r['label'].startswith(f'v2-block{block}-')}
  if len(members)==2:
   a,b=members['CONTROL'],members['TRACE'];pairs.append({'block':block,'decode_change_pct':100*(b['decode_s']/a['decode_s']-1),'wall_change_pct':100*(b['wall_s']/a['wall_s']-1),'TG_change_pct':100*(b['TG']/a['TG']-1)})
 gate=perturbation_gate(pairs);result={'rows':rows,'paired_blocks':pairs,'perturbation_gate':gate,'primary':'INSTRUMENTATION_OR_FIDELITY_BLOCKED' if not gate['pass'] else 'ATTRIBUTION_INCONCLUSIVE','reason':'Symmetric perturbation gate failed; structural trace retained; full completion dependency graph remains incomplete. No ordinary-policy publication speedup estimate.','Phase3_headline_changed':False,'policy_new_future_queries':0,'independent_generalization':False}
 save(args.output/'analysis.json',result)
 fields=['label','version','arm','valid','decode_s','TG','prefill_s','wall_s','startup_s','warmup_s','cleanup_s','operating_s']
 with (args.output/'requests.csv').open('w') as f:
  writer=csv.DictWriter(f,fields);writer.writeheader();writer.writerows({k:r[k] for k in fields} for r in rows)
 save(args.output/'paired-blocks.json',pairs);save(args.output/'perturbation-gate.json',gate);print(json.dumps({'primary':result['primary'],'requests':len(rows),'gate':gate},indent=2))
if __name__=='__main__':main()
