from campaign import C,load,save
from pathlib import Path
import subprocess,os,time
def main():
 identity=load(C/'git/builds/conditional-v1/identity.json');out=C/'tests/scheduler';out.mkdir(exist_ok=True)
 compile=['g++','-O2','-std=c++17','-pthread','-I'+identity['source']+'/include','-I/usr/local/cuda/include',str(C/'tests/scheduler_fixture.cpp'),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(out/'fixture')]
 r=subprocess.run(compile,capture_output=True,text=True,timeout=120);save(out/'compile.json',{'command':compile,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0,r.stderr
 env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(CUDA_VISIBLE_DEVICES='0,1',STRATA_Q4_EARLY='0')
 start=time.time();p=subprocess.Popen([str(out/'fixture')],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);save(out/'owned-process.json',{'pid':p.pid,'timeout_s':90,'command':[str(out/'fixture')]})
 try:stdout,_=p.communicate(timeout=90)
 except subprocess.TimeoutExpired:p.kill();stdout,_=p.communicate();save(out/'timeout.json',{'stdout':stdout});raise
 (out/'output.log').write_text(stdout);save(out/'result.json',{'returncode':p.returncode,'wall_s':time.time()-start,'PASS':[x for x in stdout.splitlines() if x.startswith('PASS ')],'source_sha':identity['source_sha'],'scope':'Real production Q4EarlyPolicy methods/CPU tracker/asynchronous CUDA workers with tiny immutable byte arena. No model logits claim. Forced-good/bad inject proposals; actual frozen gate exercised for pre-enqueue rejection; scorer scalar parity separately tested.'});assert p.returncode==0,stdout
 print(stdout,flush=True)
if __name__=='__main__':main()
