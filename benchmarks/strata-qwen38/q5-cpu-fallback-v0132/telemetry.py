import json,time,subprocess,os,signal
import campaign as c
PSS_CACHE={}

def capture_pss(pid):
 try:
  root=c.psutil.Process(pid)
  for p in [root]+root.children(recursive=True):
   t=time.monotonic()
   try:PSS_CACHE[p.pid]={"pss_gib":p.memory_full_info().pss/c.GIB,"pss_sample_wall":time.time(),"pss_read_wall_s":time.monotonic()-t}
   except (c.psutil.Error,OSError):pass
 except c.psutil.Error:pass
 return {str(k):dict(v) for k,v in PSS_CACHE.items() if c.psutil.pid_exists(k)}

class Sampler(c.Sampler):
 def run(self):
  last_progress=time.monotonic();progress_key=None
  with self.path.open('w') as f:
   while not self.stop.is_set():
    t=time.monotonic();mem=c.psutil.virtual_memory();disks=c.psutil.disk_io_counters(perdisk=True)
    s={'wall_time':time.time(),'monotonic':t,'mem_available_gib':mem.available/c.GIB,'ram_used_gib':(mem.total-mem.available)/c.GIB,'system_cpu_pct':c.psutil.cpu_percent(),'per_core_cpu_pct':c.psutil.cpu_percent(percpu=True),'processes':[], 'disk_read_bytes':{k:v.read_bytes for k,v in disks.items()}}
    try:
     root=c.psutil.Process(self.pid)
     for proc in [root]+root.children(recursive=True):
      p=self.processes.setdefault(proc.pid,proc)
      with p.oneshot():
       io=p.io_counters();mi=p.memory_info()
       row={'pid':p.pid,'name':p.name(),'rss_gib':mi.rss/c.GIB,'cpu_pct':p.cpu_percent(),'read_bytes':io.read_bytes,'read_count':io.read_count,'write_bytes':io.write_bytes}
      row.update(PSS_CACHE.get(p.pid,{'pss_gib':None,'pss_sample_wall':None,'pss_read_wall_s':None}))
      s['processes'].append(row)
    except (c.psutil.Error,OSError):pass
    try:
     data=subprocess.check_output(['nvidia-smi','--query-gpu=index,utilization.gpu,power.draw,memory.used,memory.total,clocks.sm,clocks.mem,pcie.link.gen.current,pcie.link.width.current','--format=csv,noheader,nounits'],text=True,timeout=3)
     s['gpus']=[]
     for line in data.splitlines():
      i,u,p,m,mt,sm,mc,gen,width=[x.strip() for x in line.split(',')]
      s['gpus'].append({'index':int(i),'util_pct':float(u),'power_w':float(p),'vram_gib':float(m)/1024,'total_gib':float(mt)/1024,'sm_mhz':float(sm),'memory_mhz':float(mc),'pcie_gen':gen,'pcie_width':width})
    except Exception as e:s['gpu_error']=str(e)
    s['metrics']=c.api('/metrics');self.samples.append(s);f.write(json.dumps(s)+'\n');f.flush()
    live=(s['metrics'] or {}).get('live',{}) if isinstance(s['metrics'],dict) else {}
    key=(live.get('state'),live.get('phase'),live.get('prompt_read'),live.get('generated'))
    if key!=progress_key:progress_key=key;last_progress=time.monotonic()
    if live.get('state') not in [None,'idle','loading'] and time.monotonic()-last_progress>300:
     self.abort='RUNTIME_STALL: no prompt/decode progress for300s';c.save(c.RESULTS/'raw'/'runtime-stall-abort.json',s);os.killpg(self.pid,signal.SIGTERM);return
    if mem.available<12*c.GIB:
     self.abort='RAM_ABORT: MemAvailable below 12 GiB';c.save(c.RESULTS/'raw'/'ram-abort.json',s);os.killpg(self.pid,signal.SIGTERM);return
    self.stop.wait(max(0,1-(time.monotonic()-t)))
