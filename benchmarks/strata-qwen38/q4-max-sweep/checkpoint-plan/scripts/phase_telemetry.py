"""Client phase boundaries matched to existing1Hz telemetry, no extra runtime probes."""
import statistics

def summarize(record,samples):
 start=record.get('t_start_monotonic_s');first=record.get('t_first_monotonic_s');end=record.get('t_end_monotonic_s')
 if any(x is None for x in [start,first,end]):return {'phase_telemetry_note':'Exact client phase timestamps not saved in this early request; full-request telemetry retained. No inferred phase split.'}
 result={'phase_telemetry_note':'1Hz samples selected by exact client stream timestamps. pre_first_token includes prefill and first-token overhead; decode_after_first_token excludes first token. These are not engine PP/TG timer boundaries.'}
 def process_value(s,key):return sum(p.get(key,0) for p in s.get('processes',[]))
 for phase,lo,hi in [('pre_first_token',start,first),('decode_after_first_token',first,end)]:
  ss=[s for s in samples if lo<=s['monotonic']<=hi]
  result[phase+'_samples']=len(ss)
  if not ss:continue
  avg=lambda v:statistics.mean(v) if v else None
  result[phase+'_system_cpu_pct']=avg([s['system_cpu_pct'] for s in ss])
  result[phase+'_process_cpu_pct']=avg([process_value(s,'cpu_pct') for s in ss])
  result[phase+'_peak_rss_gib']=max(process_value(s,'rss_gib') for s in ss)
  result[phase+'_peak_ram_used_gib']=max(s['ram_used_gib'] for s in ss)
  result[phase+'_min_mem_available_gib']=min(s['mem_available_gib'] for s in ss)
  for gpu in [0,1]:
   gs=[g for s in ss for g in s.get('gpus',[]) if g['index']==gpu]
   for key in ['util_pct','power_w','sm_mhz','memory_mhz']:
    result[f'{phase}_GPU{gpu}_{key}']=avg([g[key] for g in gs if g.get(key) is not None])
  if len(ss)>=2:
   delta=process_value(ss[-1],'read_bytes')-process_value(ss[0],'read_bytes')
   result[phase+'_process_read_bytes_delta']=max(0,delta)
   result[phase+'_observed_interval_s']=ss[-1]['monotonic']-ss[0]['monotonic']
   result[phase+'_read_scope_note']='Observed process read_bytes between first/last selected1Hz sample, not entire phase; virtiofs guest counters do not measure physical host SSD reads.'
 return result
