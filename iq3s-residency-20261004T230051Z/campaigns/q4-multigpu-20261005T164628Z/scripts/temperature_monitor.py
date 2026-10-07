"""OneHz NVML temperature sampling; survives cell changes, exits with identified driver."""
import datetime,json,pathlib,subprocess,time
import psutil
C=pathlib.Path(__file__).resolve().parents[1]
pid=1735884
parent=psutil.Process(pid);created=parent.create_time()
meta={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'started_epoch':time.time(),'parent_pid':pid,'parent_create_time':created,'command':['nvidia-smi','dmon','-i','0,1','-s','p','-d','1','-o','DT'],'reason':'Helper frontend Monitor exposes primary GPU only. Existing perGPU speed sampler already captures utilization, VRAM,power,clocks; add missing GPU1temperature without engine instrumentation. Earlier missing values stay unavailable.','scope':'Additional lowrate NVML query only; not CPU/expert profiling'}
(C/'telemetry/temperature-monitor.json').write_text(json.dumps(meta,indent=2)+'\n')
with (C/'telemetry/temperature-dmon.log').open('x') as out:
 p=subprocess.Popen(meta['command'],stdout=out,stderr=subprocess.STDOUT)
 q=psutil.Process(p.pid);q.cpu_percent();samples=[]
 try:
  while parent.is_running() and parent.status()!=psutil.STATUS_ZOMBIE and abs(parent.create_time()-created)<.1:
   if p.poll() is not None:break
   samples.append({'epoch':time.time(),'collector_CPU_one_core100':q.cpu_percent()});time.sleep(1)
 except psutil.NoSuchProcess:pass
 finally:
  p.terminate()
  try:p.wait(timeout=3)
  except subprocess.TimeoutExpired:p.kill();p.wait()
  meta.update(finished_epoch=time.time(),process_exit_code=p.returncode,CPU_samples=samples)
  (C/'telemetry/temperature-monitor-finished.json').write_text(json.dumps(meta,indent=2)+'\n')
