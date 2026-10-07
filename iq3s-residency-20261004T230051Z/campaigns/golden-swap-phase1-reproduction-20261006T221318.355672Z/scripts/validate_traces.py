"""Validate the existing schema2 tape, logical windows and actual emitted IDs."""
import argparse,hashlib,json,pathlib,sys
import numpy as np
from legacy_tape import Tape
C=pathlib.Path(__file__).resolve().parents[1]
L=np.dtype([('event','<u8'),('begin','<u8'),('plan_end','<u8'),('cpu_end','<u8'),('layer','<i4'),('n','<i4'),('ids','<i4',(40,)),('slots','<i4',(40,)),('path','<i4',(40,))])
N=np.dtype([('issue_ns','<u8'),('publish_ns','<u8'),('bytes','<u8')]+[(k,'<i4') for k in ['window','layer','incoming','victim','slot']]+[('pad','<u4')])
def validate(p):
 p=pathlib.Path(p);episode=json.loads((p/'episode.json').read_text());t=Tape(p/'tape.bin');r=t.validate();run=episode['run'];errors=list(r['errors'])
 IDs=json.loads(pathlib.Path(run['output_ids_path']).read_text());expected=np.asarray(IDs,dtype='<i4').tobytes()
 if hashlib.sha256(expected).hexdigest()!=r['output_ids_sha256_binary']:errors.append('Actual generated output IDs differ from completed tape')
 if int(t.h['output_count'])!=len(IDs):errors.append('Native header emission count differs from actual generated IDs')
 cmd=json.loads((p/'raw/native-process.json').read_text())['command'];eos=[248044,248046]
 if '--eos-ids' in cmd:eos=[int(x) for x in cmd[cmd.index('--eos-ids')+1].split(',')]
 if run['stop_reason']=='NATURAL_EOS' and (not IDs or IDs[-1] not in eos or any(x in eos for x in IDs[:-1])):errors.append('Actual emitted EOS boundary mismatch')
 if run['stop_reason']=='NATURAL_EOS' and int(t.h['output_count'])>=int(t.h['output_budget']):errors.append('EOS boundary at output cap is ambiguous')
 if int(t.h['output_count'])<int(t.h['output_budget']) and run['stop_reason']!='NATURAL_EOS':errors.append('Sub-budget terminal prefix without observed EOS')
 if len(t.prompt)!=run['actual_input_tokens']:errors.append('Actual input count mismatch')
 actual=json.loads(pathlib.Path(run['payload']['token_ids_path']).read_text())
 if not np.array_equal(t.prompt,actual):errors.append('Actual input IDs mismatch')
 if r['MTP_proposed_to_verifier']!=run['MTP_proposed'] or r['MTP_accepted_to_commit']!=run['MTP_accepted']:errors.append('MTP verifier counters mismatch')
 if r['main_routed_entries']!=run['all_entries']:errors.append('Normal main routing denominator mismatch')
 a=np.fromfile(p/'raw/native-layers.bin',L);n=np.fromfile(p/'raw/native-native.bin',N);o=np.fromfile(p/'raw/observations.bin',t.obs_dtype)
 if len(a)!=len(t.ws)*48:errors.append('Main layer observation coverage')
 if not np.array_equal(a['event'],np.arange(len(a))):errors.append('Logical main event IDs')
 if not np.array_equal(a['layer'],np.arange(len(a))%48):errors.append('Layer IDs')
 counts={k:0 for k in ['local','cpu','mapped']}
 for row in a:
  nn=int(row['n']);slot=row['slots'][:nn];paths=row['path'][:nn]
  counts['local']+=int(np.count_nonzero(slot>=0));counts['cpu']+=int(np.count_nonzero((slot<0)&(paths==-1)));counts['mapped']+=int(np.count_nonzero((slot<0)&(paths==1)))
 for k,field in [('local','local_entries'),('cpu','cpu_entries'),('mapped','mapped_entries')]:
  if counts[k]!=run[field]:errors.append(k+' denominator mismatch')
 if len(o)!=len(t.ws):errors.append('Window observation count')
 r.update(state='PASS' if not errors else 'FAIL',errors=list(dict.fromkeys(errors)),trace_type='FULL_REPLAY_TAPE' if not errors else 'INVALID_TRACE',main_dispatch_counts=counts,normal_main_denominator=sum(counts.values()),MTP_scope='Full MTP IDs and coefficients in tape; native dispatch observations cover main only',natural_generation=True,oracle_active=False,native_admissions=len(n),native_H2D_bytes_issued=int(n['bytes'].sum()),native_publications=int(np.count_nonzero(n['publish_ns'])),initial_state_sidecar= str(p/'tape.bin.initial-state.bin') if (p/'tape.bin.initial-state.bin').exists() else None,observed_first_window=0,observed_last_window=len(t.ws)-1,right_censored=True,censoring='No future return label after final complete logical window. Independent requests are never concatenated.',causal_fields=['current IDs/weights,role,layer,window,batch/position/lane','initial residency/heat','current slot/path','native issue/publication events'],labels_namespace=['future next-use/return distances; computed offline only'],unavailable=['native queue/protection fields not explicitly recorded','per-decision complete usage/heat snapshots','MTP dispatch path breakdown','counterfactual eviction regret'])
 r['file_hashes']={str(q):hashlib.sha256(q.read_bytes()).hexdigest() for q in [p/'tape.bin',p/'raw/observations.bin',p/'raw/native-layers.bin',p/'raw/native-native.bin',p/'tape.bin.initial-state.bin'] if q.exists()}
 (p/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print('TRACE VALIDATED',p.name,r['state'],'windows',len(t.ws),'entries',r['normal_main_denominator'],flush=True)
 return r
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('path');v=a.parse_args();r=validate(v.path);sys.exit(0 if r['state']=='PASS' else 1)
