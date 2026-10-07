"""Bounded isolated build; full commands, exit status, progress and ownership retained."""
from pathlib import Path
import sys,subprocess,time,os,signal,json,hashlib,datetime
C=Path(__file__).resolve().parents[1];R=C.parents[1];v=sys.argv[1];S=C/'src'/v;B=C/'builds'/v;attempt=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');L=C/'git/builds'/v/attempt;L.mkdir(parents=True)
def save(n,x):(L/n).write_text(json.dumps(x,indent=2)+'\n')
records=[]
def run(n,cmd,timeout,cwd=None):
 start=time.monotonic()
 with (L/(n+'.log')).open('x') as out:
  p=subprocess.Popen(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT,start_new_session=True);save(n+'-pid.json',{'pid':p.pid,'command':cmd,'timeout_s':timeout});last=start
  try:
   while p.poll() is None:
    if time.monotonic()-start>timeout:raise TimeoutError(n)
    if time.monotonic()-last>15:print('BUILD_PROGRESS',v,n,round(time.monotonic()-start),flush=True);last=time.monotonic()
    time.sleep(1)
  finally:
   if p.poll() is None:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=20)
 records.append({'name':n,'command':cmd,'cwd':str(cwd),'exit_code':p.returncode,'wall_s':time.monotonic()-start});save('commands.json',records);print('BUILD_STEP',n,p.returncode,flush=True)
 if p.returncode:print((L/(n+'.log')).read_text()[-7000:],flush=True);raise SystemExit(p.returncode)
run('add',['git','add','.'],60,S);run('commit',['git','-c','user.name=Local Research','-c','user.email=research@localhost','commit','--allow-empty','-m','Fixed-work Q4 tape '+v],60,S)
cm=R/'src/control/.venv/bin/cmake';nj=R/'src/control/.venv/bin/ninja'
run('configure',[str(cm),'-S',str(S),'-B',str(B),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(nj),'-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_GGML_DIR=/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325','-DSTRATA_BUILD_TESTS=ON'],300)
run('build',[str(cm),'--build',str(B),'-j','8'],1800)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=S,text=True).strip();ident={'source_sha':head,'upstream_base':'6f32ec070f23ced9f50e704d854d775da52591ab','source':str(S),'build':str(B),'exe':str(B/'strata'),'binary_sha256':hashlib.sha256((B/'strata').read_bytes()).hexdigest(),'commands':str(L/'commands.json')};save('identity.json',ident);(C/'git'/f'{v}-identity.json').write_text(json.dumps(ident,indent=2)+'\n')
with (C/'patches'/f'{v}-{head}.diff').open('x') as f:subprocess.run(['git','diff','6f32ec070f23ced9f50e704d854d775da52591ab',head,'--binary'],cwd=S,stdout=f,check=True,timeout=60)
print('BUILD_COMPLETE',ident,flush=True)
