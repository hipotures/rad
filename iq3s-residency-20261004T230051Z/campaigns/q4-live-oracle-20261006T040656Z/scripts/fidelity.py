"""Audit observed execution against tape, native counters and actual output IDs."""
from pathlib import Path
import json,re,argparse,hashlib,numpy as np
from tape import Tape,OBS
C=Path(__file__).resolve().parents[1]
def audit(label,tape):
 p=C/'raw'/label;rs=json.loads((p/'results.json').read_text());r=rs['runs'][0];t=Tape(tape);v=t.validate();o=np.fromfile(p/'raw/observations.bin',t.obs_dtype);errors=list(v['errors']);log=(p/'raw/run-engine.log').read_text();mat=re.search(r'Q4_TAPE_END mode=(\w+) windows=(\d+) main_events=(\d+) mtp_events=(\d+) output=(\d+) work_hash=([0-9a-f]+) lookup_ms=([0-9.]+) native_head_first_divergence=(-?\d+)',log)
 if not mat:errors.append('completion marker missing')
 else:
  if int(mat[2])!=len(t.ws) or int(mat[3])!=48*len(t.ws) or int(mat[4])!=int(t.ws['draft_count'].sum()) or mat[6]!=v['native_FNV64']:errors.append('native work conservation')
 if len(o)!=len(t.ws):errors.append('observation count')
 else:
  expected=np.ones((len(o),51),np.int32);expected[:,48:]=np.arange(3)[None,:]<t.ws['draft_count'][:,None]
  if not np.array_equal(o['seen'],expected):errors.append('GPU invocation count')
  if np.any(o['end_ns']<o['begin_ns']) or np.any(o['begin_ns'][1:]<o['end_ns'][:-1]):errors.append('window ordering')
  if t.version==2 and not np.all(o['qsa_seen']==1):errors.append('QSA invocation count')
  if not np.isfinite(o['activation']).all():errors.append('activation nonfinite')
 output=np.asarray(json.loads(Path(r['actual_output_ids_path']).read_text()),'<i4');expected=[]
 for w in t.ws:expected.extend(w['outputs'][:min(int(w['accepted'])+1,int(t.h['output_budget'])-len(expected))].tolist())
 if not np.array_equal(output,np.asarray(expected,'<i4')):errors.append('actual emitted IDs')
 if r['verify_windows']!=len(t.ws) or r['mtp_proposed']!=v['MTP_proposed_to_verifier'] or r['mtp_accepted']!=v['MTP_accepted_to_commit']:errors.append('spec native stats')
 if r.get('all_routed_entries')!=v['main_routed_entries']:errors.append('native demand counter')
 if r.get('actual_input_tokens')!=len(t.prompt) or r.get('reuse')!=0:errors.append('input/reuse')
 initial=None
 side=Path(str(tape)+'.initial-state.bin');observed=p/'raw/observations.bin.initial-state.bin'
 if side.exists():
  dtype=np.dtype([('name','S80'),('bytes','<u8'),('hash','<u8')])
  def state_file(path):
   raw=path.read_bytes();n=int.from_bytes(raw[:8],'little');assert len(raw)==8+n*dtype.itemsize,'state sidecar length';return np.frombuffer(raw[8:],dtype=dtype)
  try:
   expected_state=state_file(side);actual_state=state_file(observed);same=np.array_equal(expected_state,actual_state)
   if not same:errors.append('initial numerical/state sidecar mismatch')
   m=re.search(r'Q4_STATE_READY components=(\d+) read_bytes=(\d+) setup_ms=([0-9.]+) exact_initial_state=1',log)
   if not m:errors.append('native initial-state attestation missing')
   initial={'match':same,'components':len(expected_state),'bytes_checked':int(expected_state['bytes'].sum()),'setup_ms':float(m[3]) if m else None,'SHA256':hashlib.sha256(side.read_bytes()).hexdigest(),'scope':'Meaningful initial GDN, PLE, HC_R, QSA indexer/mapping/canonical host prefix and resident KV/MTP pools; streamed GPU payload redundant with checked host prefix/maps.'}
  except Exception as e:errors.append('state attestation '+repr(e))
 kv=re.search(r'KV streaming: ([0-9.]+)% of (\d+) block reads hit VRAM, ([0-9.]+) MiB read from RAM([^\n]*)',log)
 physical_kv={'primary_device_only':True,'cumulative_block_lookups':int(kv[2]),'display_hit_pct':float(kv[1]),'RAM_refill_MiB_rounded':float(kv[3]),'counter_scope':'Native process-cumulative primary-device owned QSA states. Secondary-device summary unavailable. Initialcontrolbytes checked identically; service placement/atomicCLOCK ordering may vary.'} if kv else None
 if 'OVERFLOW (too few resident cells)' in log:errors.append('unsafe KV overflow')
 reference_observations=C/'raw'/t.path.stem/'raw/observations.bin';activation_check=None
 if reference_observations.exists() and len(o)==len(t.ws):
  ref=np.fromfile(reference_observations,t.obs_dtype);mask=o['seen']>0
  aa=o['activation'][mask].astype(np.float64);bb=ref['activation'][mask].astype(np.float64);diff=aa-bb
  bits_differ=(o['activation'].view('<u4')!=ref['activation'].view('<u4'))&mask[:,:,None];where=np.argwhere(bits_differ)
  activation_check={'sampled_values':int(aa.size),'excluded_unexecuted_MTP_zero_values':int(o['activation'].size-aa.size),'bitwise_equal':not bool(np.any(bits_differ)),'max_abs_error':float(np.max(np.abs(diff))),'relative_L2':float(np.linalg.norm(diff)/max(np.linalg.norm(bb),1e-12)),'first_divergence_window_role_component':where[0].tolist() if len(where) else None,'scope':'Eight actual activation components only at executed main/MTP routed invocations, excluding padded inactive MTP rows; exact uint32 bit comparison plus numerical error. Not all hidden tensors. Oracle placement can legitimately change CPU/GPU numerical intermediates.'}
 full_log=(p/'logs/engine.log').read_text();before=full_log.split('Q4_TAPE_BEGIN')[0];graph_shapes=[int(x) for x in re.findall(r'captured the (\d+)-token window',before)]
 head_mask=np.arange(4)[None,:]<t.ws['T'][:,None];head_agreement={'positions':int(head_mask.sum()),'agreements':int(np.count_nonzero((o['native_outputs']==t.ws['outputs'])&head_mask)),'fraction':float(np.count_nonzero((o['native_outputs']==t.ws['outputs'])&head_mask)/head_mask.sum()),'scope':'Native argmax computed before forced output; includes rejected verifier lanes. This is numerical trajectory diagnostics, not quality evaluation.'} if len(o)==len(t.ws) else None
 result={'native_main_head_agreement':head_agreement,'selected_activation_check':activation_check,'graph_readiness':{'captured_shapes_before_measured_request':graph_shapes,'all_T_1_to_4_ready':set(graph_shapes)=={1,2,3,4},'scope':'Native verifier graph capture messages; main split devices represented by paired messages. MTP remains computed normally.'},'physical_KV_summary':physical_kv,'initial_state':initial,'state':'PASS' if not errors else 'FAIL','errors':errors,'label':label,'tape':v,'observed_windows':len(o),'seen_events':int(o['seen'].sum()),'native_router_id_or_coefficient_disagreements':int(o['disagreements'].sum()),'native_QSA_selection_disagreements':int(o['qsa_disagreements'].sum()) if t.version==2 else None,'native_head_first_divergence':int(mat[8]) if mat else None,'lookup_ms':float(mat[7]) if mat else None,'native_main_routing_stats':{k:r.get(k) for k in ['all_routed_entries','local_vram_entries','cpu_fallback_entries','offloaded_entries']},'time':{k:r.get(k) for k in ['pp_s','decode_s','TG','wall_s','TTFT_s']},'clock':'Window CPU monotonic timestamps; not GPU copy deadlines.','correctness_scope':'Tape structure/counts/coefficients and actual forced emission; selected finite activation components. No claim forced output equality proves model math.'}
 dest=C/'phase-a'/f'{label}-fidelity.json';dest.write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('label');a.add_argument('tape');v=a.parse_args();r=audit(v.label,v.tape);print(json.dumps(r,indent=2));assert r['state']=='PASS',r
