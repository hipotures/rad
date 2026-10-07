"""Exercise the actual manual alias, wildcard bind,64-token request and owned stop."""
import json,os,pathlib,signal,subprocess,time,urllib.request
from lab import ROOT,api,load,save
base=ROOT/'experiments/E027-pool-baseline/launcher-smoke';assert not base.exists();base.mkdir()
variant=ROOT/'variants/p1-baseline';cmd=[str(variant/'start-128k.sh'),'--host','0.0.0.0','--port','18080'];url='http://127.0.0.1:18080';log=(base/'launcher.log').open('w');start=time.time()
p=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
save(base/'command.json',{'command':cmd,'pid':p.pid,'start_epoch':start,'headline':False,'reason':'Actual saved alias and explicit wildcard binding smoke; no throughput repetition'})
try:
 for _ in range(900):
  h=api(url,'/health')
  if h and h.get('loaded') and h.get('status')=='ok':break
  if p.poll() is not None:raise RuntimeError('Launcher exited '+str(p.returncode))
  time.sleep(1)
 else:raise RuntimeError('Launcher timeout')
 owner=load(variant/'owned-process.json');manual=pathlib.Path(owner['attempt']);cfg=load(manual/'config.json')
 assert cfg['host']=='0.0.0.0' and cfg['max_total_context']==131072 and cfg['env']['STRATA_POOL_SPIN_US']=='100'
 listeners=subprocess.check_output(['ss','-ltnp'],text=True);(base/'listeners.txt').write_text(listeners)
 assert '0.0.0.0:18080' in listeners
 payload=load(ROOT/'workloads/warmup.json');save(base/'request.json',payload)
 req=urllib.request.Request(url+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=180) as response:data=response.read().decode()
 (base/'response.sse').write_text(data);status=api(url,'/v1/status');save(base/'status.json',status)
 chunks=[json.loads(l[5:].strip()) for l in data.splitlines() if l.startswith('data:') and l[5:].strip()!='[DONE]'];usage=next(c['usage'] for c in reversed(chunks) if c.get('usage'))
 assert usage['prompt_tokens']==4096 and usage['completion_tokens']==64,usage
 save(base/'summary.json',{'state':'PASS','health':h,'actual_counts':usage,'manual_attempt':str(manual),'cold_start_s':time.time()-start,'headline':False,'wildcard_bound':True,'source_sha':cfg['source_sha'],'binary_sha256':cfg['binary_sha256'],'config':cfg,'note':'No64-token rate used as headline performance.'})
finally:
 subprocess.run([str(variant/'stop.sh')],cwd=ROOT,check=True)
 try:p.wait(timeout=25)
 except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10)
 log.close()
save(base/'end-state.json',{'launcher_returncode':p.returncode,'GPU_compute_processes':subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()})
assert not load(base/'end-state.json')['GPU_compute_processes']
print('WILDCARD_LAUNCHER_AND_OWNED_STOP_PASS',flush=True)
