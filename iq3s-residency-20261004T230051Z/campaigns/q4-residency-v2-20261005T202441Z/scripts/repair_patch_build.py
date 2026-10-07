"""Resume one patch-only failure, retaining every failed source diff/log before reset."""
from campaign import C,R,save,load,guard
import subprocess,time,hashlib,sys
variant=sys.argv[1];patch=sys.argv[2];source=C/'src'/variant;build=C/'builds'/variant;logs=C/'git/builds'/variant
assert not build.exists() and not (logs/'identity.json').exists(),'Only pre-compilation application failure may resume'
with (logs/'failed-patch.diff').open('x') as f:subprocess.run(['git','diff','--binary'],cwd=source,stdout=f,check=True)
records=[]
def run(name,cmd,cwd=None,timeout=300):
 guard();start=time.time()
 with (logs/f'{name}.log').open('x') as f:r=subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 records.append({'name':name,'command':cmd,'cwd':str(cwd) if cwd else None,'exit_code':r.returncode,'wall_s':time.time()-start});save(logs/'repair-commands.json',records)
 print('REPAIR_BUILD',variant,name,r.returncode,flush=True);assert not r.returncode,(name,(logs/f'{name}.log').read_text()[-5000:])
run('reset-owned-patch',['git','restore','--source=HEAD','--worktree','--staged','.'],source)
run('patch-repaired',[str(R/'src/control/.venv/bin/python'),str(C/'scripts'/patch),str(source)])
run('patch-repaired-diff',['git','diff','--binary'],source)
run('add-repaired',['git','add','.'],source)
run('commit-repaired',['git','-c','user.name=Local Research','-c','user.email=research@localhost','commit','-m','Local Q4 residency v2 '+variant],source)
cmake=R/'src/control/.venv/bin/cmake';ninja=R/'src/control/.venv/bin/ninja'
run('configure',[str(cmake),'-S',str(source),'-B',str(build),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(ninja),'-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_GGML_DIR=/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325','-DSTRATA_BUILD_TESTS=ON'])
run('build',[str(cmake),'--build',str(build),'-j','8'],timeout=1800)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip();save(logs/'identity.json',{'source_sha':head,'upstream_base':'6f32ec070f23ced9f50e704d854d775da52591ab','parent':'6f32ec070f23ced9f50e704d854d775da52591ab','source':str(source),'build':str(build),'exe':str(build/'strata'),'binary_sha256':hashlib.sha256((build/'strata').read_bytes()).hexdigest(),'commands':[str(logs/'commands.json'),str(logs/'repair-commands.json')]})
run('full-patch',['git','diff','6f32ec070f23ced9f50e704d854d775da52591ab',head,'--binary'],source)
