#!/usr/bin/env python3
"""Add explicit conditions and observation scopes without altering retained raw records."""
import json,math,os,pathlib,re,sys
R=pathlib.Path(sys.argv[1]).resolve();GIB=1<<30;MIB=1<<20
inv=json.loads((R/'inventory.json').read_text());uuids=re.findall(r'GPU UUID\s+:\s+(GPU-[a-z0-9-]+)',inv['commands']['gpus']['stdout'])
config=json.loads((R/'campaign_config.json').read_text())
exclusions=json.loads((R/'exclusions.json').read_text()) if (R/'exclusions.json').exists() else {'excluded':[]};excluded={x['raw_stdout'] for x in exclusions['excluded']}
def arg(c,key,default=None):
 a=c.get('args',[])
 return a[a.index(key)+1] if key in a else default
with (R/'normalized-results.jsonl').open('w') as out:
 for i,line in enumerate((R/'results.jsonl').read_text().splitlines()):
  r=json.loads(line);c=r['case'];mode=arg(c,'--mode',c.get('tool','unknown'));payload=int(arg(c,'--bytes',str(c.get('bs',0))));buffers=int(arg(c,'--buffers','1'));kind=arg(c,'--kind','pinned' if mode in ['transfer','bridge','pipeline','pipeline-stages'] else None)
  devices=[0,1] if '--both' in c.get('args',[]) or c.get('concurrent_device') or mode=='bridge' else [int(arg(c,'--device','0'))] if mode in ['transfer','mapped','local','gemm','pipeline','pipeline-stages','reverse','store','residency'] else []
  working={'payload_per_object_bytes':payload,'buffer_count_per_GPU':buffers,'allocation_scope':'Includes reusable payload allocations; runtime/CUDA/library internal allocation not inferred'}
  if mode in ['transfer','bridge']:working['ring_bytes_per_buffer']=max(payload,64*MIB);working['active_pattern']='Reusable ring; H2D increments sequence twice per object, so small power-of-two ring strides can visit only a subset. Warm host cache state not controlled.'
  elif mode in ['ram','combined']:working['host_arrays_total_bytes']=3*payload if payload else 3*GIB
  elif mode=='gemm':working['matrix_dimension']=256 if arg(c,'--op')=='small' else 4096;working['GPU_matrix_bytes']=3*working['matrix_dimension']**2*4
  elif mode in ['local','mapped']:working.update(host_payload_bytes=payload,GPU_allocated_payload_bytes=2*payload,active_source='mapped host' if mode=='mapped' else 'device allocation')
  elif mode in ['pipeline','pipeline-stages']:working['corpus_bytes']=16*GIB
  elif mode=='store':working.update(immutable_experts=96,host_blob_total_bytes=432*MIB,host_segments_and_blobs_total_bytes=864*MIB,preallocated_GPU_slot_bytes=4*8*MIB)
  observed=[]
  p=pathlib.Path(r.get('telemetry',''))
  if p.is_file():observed=[json.loads(x) for x in p.read_text().splitlines()]
  energy={}
  for d in devices:
   points=[(x['monotonic'],g['power_W']) for x in observed for g in x.get('gpu',[]) if g['index']==d and g.get('power_W') is not None]
   energy[str(d)]={'approx_board_energy_J':sum((b[0]-a[0])*(a[1]+b[1])/2 for a,b in zip(points,points[1:])) if len(points)>1 else None,'observation_seconds':points[-1][0]-points[0][0] if len(points)>1 else None,'scope':'trapezoid of ~1Hz whole-process board-power samples, includes setup/warmup/teardown; not a hardware energy counter or pure measured-window energy'}
  n={'raw_result_file':str(R/'results.jsonl'),'raw_result_line':i+1,'scenario_id':r['scenario_id'],'repetition':r['repetition'],'status':r['status'],'analysis_status':'EXCLUDED_BUILD_BACKGROUND' if r.get('raw_stdout') in excluded else r['status'],'path_label':r.get('path'),'storage_data_path':config['scratch'].get(c.get('storage')),'direction':arg(c,'--direction','explicit GPU'+str(devices[0])+'→host→GPU'+str(1-devices[0]) if mode=='bridge' else None),'GPU_UUIDs':[uuids[d] for d in devices if d<len(uuids)],'copy_mechanism':mode,'memory_kind':kind,'working_set':working,'stream_scope':'one stream per CUDA Buffer; bridge source/destination buffers each have a stream' if mode in ['transfer','bridge','pipeline','pipeline-stages'] else 'see native source/explicit command','configured_queue_depth':c.get('depth'),'achieved_queue_depth':r.get('achieved_depth'),'threads':int(arg(c,'--threads','1')),'affinity':r.get('affinity'),'requested_transfer_bytes_s':float(arg(c,'--rate','0')),'achieved_traffic_bytes_s':r.get('traffic_completed_bytes',0)/r['actual_measured_seconds'] if r.get('actual_measured_seconds') else None,'burst_bytes':float(arg(c,'--burst','0')),'warmup_seconds':0 if c.get('tool')=='idle' else r.get('warmup_seconds'),'actual_measured_seconds':r.get('actual_measured_seconds'),'drain_seconds':r.get('drain_seconds'),'completed_logical_bytes':r.get('completed_logical_bytes'),'reported_payload_leg_bytes':r.get('physical_leg_bytes'),'extra_bridge_validation_H2D_bytes':8*r.get('useful_work_count',0) if mode=='bridge' else 0,'physical_leg_scope':r.get('physical_leg_scope'),'useful_work_count':r.get('useful_work_count'),'latency':{k:r.get(k) for k in ['latency_sample_count','latency_sample_unit','latency_p50_ms','latency_p95_ms','latency_p99_ms','fio_latency']},'unavailable_latency_reason':None if r.get('latency_sample_count') or r.get('fio_latency') else 'No operation latency distribution collected (idle/process probe/aggregate concurrent worker; inspect retained per-worker distributions)','CPU_seconds':r.get('cpu_seconds'),'fio_native_CPU_percent':r.get('fio_cpu'),'memory_peaks':r.get('telemetry_peaks'),'sampled_GPU_energy':energy,'verification':r.get('verification'),'software_identity':r.get('software_identity'),'cache_assumptions':r.get('cache_assumptions'),'raw_stdout':r.get('raw_stdout'),'raw_stderr':r.get('raw_stderr'),'telemetry':r.get('telemetry'),'full_commands':r.get('commands')}
  out.write(json.dumps(n,allow_nan=False)+'\n')
print('Normalized result conditions written:',R/'normalized-results.jsonl')
