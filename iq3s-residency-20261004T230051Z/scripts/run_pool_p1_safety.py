"""New bounded transition tests; fail before P1 performance on lost jobs/hangs."""
import hashlib, os, subprocess, time
from lab import ROOT, save
base=ROOT/'experiments/E027-pool-baseline/safety';assert not base.exists();base.mkdir()
b=ROOT/'builds/control';s=ROOT/'src/control';src=ROOT/'scripts/pool_transition_stress.cpp';exe=base/'pool-transition-stress';records=[]
def run(name,cmd,env=None,timeout=240):
 start=time.time();p=base/(name+'.log')
 with p.open('w') as f:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 records.append({'name':name,'command':cmd,'environment':{'STRATA_POOL_SPIN_US':env.get('STRATA_POOL_SPIN_US')} if env else {},'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(p)})
 save(base/'commands.json',records);print(name,r.returncode,p.read_text()[-1400:],flush=True);assert r.returncode==0
run('compile',['/usr/bin/g++','-std=c++20','-O3','-DNDEBUG','-DSTRATA_NATIVE_EXPERTS=1','-I'+str(s/'include'),'-I/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325/ggml/include',str(src),str(b/'libstrata_kernels_cpu.a'),str(b/'ggml/src/libggml-cpu.a'),str(b/'ggml/src/libggml-base.a'),'-lm','-pthread','-o',str(exe)])
for role in ['default','100us']:
 env=os.environ.copy();env.pop('STRATA_POOL_SPIN_US',None)
 if role=='100us':env['STRATA_POOL_SPIN_US']='100'
 run('targeted-'+role,[str(exe)],env)
 run('random-'+role,[str(b/'pool_stress'),'20'],env,60)
env=os.environ.copy();env['STRATA_POOL_SPIN_US']='100'
run('real-native-IQ',[str(b/'native_expert_parity'),'/srv/ai/models/strata/models/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf','0','1','2','12'],env,300)
save(base/'summary.json',{'state':'PASS','records':records,'test_source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'test_binary_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'runtime_source_unchanged':True,'limits':['Zero legacy weights for scheduling/output-completion stress; actual native IQ experts covered separately.','Not a proof over all interleavings; existing synchronization is unchanged.']})
