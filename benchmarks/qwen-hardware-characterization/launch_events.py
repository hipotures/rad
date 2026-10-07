#!/usr/bin/env python3
"""Process + CUDA-context events: each constituent launch remains individually labeled."""
import json,pathlib,subprocess,time,sys
root=pathlib.Path(__file__).resolve().parent
seconds=float(sys.argv[1]);warm=float(sys.argv[2]);events=[]
for phase,duration in [('warmup',warm),('measured',seconds)]:
 start=time.monotonic()
 while time.monotonic()-start<duration:
  t=time.monotonic();p=subprocess.run([str(root/'hwbench'),'--mode','probe'],capture_output=True,text=True,timeout=10);end=time.monotonic()
  if p.returncode:raise RuntimeError(p.stderr)
  if phase=='measured':events.append({'start_monotonic':t,'end_monotonic':end,'process_plus_context_wall_s':end-t,'status':'OK'})
 measured=time.monotonic()-start
print(json.dumps({'status':'OK','actual_measured_seconds':measured,'completed_logical_bytes':0,'useful_work_count':len(events),'verification':'CUDA_CAPABILITY_PROBE_SUCCESS','events':events,'measurement_scope':'fresh process + CUDA initialization/probe/exit; not cold SSD'}))
