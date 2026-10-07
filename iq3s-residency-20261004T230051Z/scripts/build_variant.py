"""Build an isolated frozen-base variant. Every attempt has separate logs and commands."""
import argparse, hashlib, json, pathlib, subprocess, time, shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='6f32ec070f23ced9f50e704d854d775da52591ab'
ap=argparse.ArgumentParser();ap.add_argument('variant');ap.add_argument('--patch-script');ap.add_argument('--attempt',default='v1');ap.add_argument('--experiment',default='E003-diagnostics');a=ap.parse_args()
src=ROOT/'src'/a.variant;build=ROOT/'builds'/a.variant;attempt=ROOT/'experiments'/a.experiment/a.attempt/'build'
if (attempt/'commands.json').exists() or src.exists() or build.exists():raise RuntimeError('Existing build attempt; refuse overwrite')
attempt.mkdir(parents=True,exist_ok=True)
from lab import deadline as campaign_deadline
deadline=campaign_deadline();commands=[]
def call(name,cmd,cwd=None,check=True):
 path=attempt/f'{name}.log';start=time.time()
 with path.open('w') as f:r=subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,timeout=max(1,min(1800,int(deadline-time.time()-2700))))
 commands.append({'name':name,'command':cmd,'cwd':str(cwd) if cwd else None,'returncode':r.returncode,'wall_s':time.time()-start,'log':str(path)})
 (attempt/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 print(name,r.returncode,flush=True)
 if r.returncode and check:print(path.read_text()[-6000:],flush=True);raise SystemExit(r.returncode)
call('clone',['git','clone','--no-hardlinks','--no-checkout',str(ROOT/'src/control'),str(src)])
call('checkout',['git','checkout','--detach',BASE],src)
# Share the frozen, already inspected Python dependency environment read-only.
# This also lets upstream CMake register the same NumPy fixture tests as control.
(src/'.venv').symlink_to(ROOT/'src/control/.venv',target_is_directory=True)
with (src/'.git/info/exclude').open('a') as stream:stream.write('\n# Read-only pinned research dependency environment\n.venv\n')
if a.patch_script:
 shutil.copy2(ROOT/'scripts'/a.patch_script,attempt/'patch-script.py')
 shutil.copytree(ROOT/'scripts/templates',attempt/'templates',dirs_exist_ok=True)
 call('patch',['python3',str(ROOT/'scripts'/a.patch_script),str(src)])
 call('patch-diff',['git','diff','--binary'],src)
 call('add',['git','add','.'],src)
 call('commit',['git','-c','user.name=Local Research','-c','user.email=research@localhost','commit','-m','Local '+a.variant+' experiment; frozen base and reversible patch'],src)
call('configure',[str(ROOT/'src/control/.venv/bin/cmake'),'-S',str(src),'-B',str(build),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(ROOT/'src/control/.venv/bin/ninja'),'-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_GGML_DIR=/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325','-DSTRATA_BUILD_TESTS=ON'])
call('build',[str(ROOT/'src/control/.venv/bin/cmake'),'--build',str(build),'-j','8'])
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip()
manifest={'source_sha':head,'base':BASE,'source':str(src),'build':str(build),'binary_sha256':hashlib.sha256((build/'strata').read_bytes()).hexdigest(),'commands':str(attempt/'commands.json'),'variant':a.variant}
(attempt/'identity.json').write_text(json.dumps(manifest,indent=2)+'\n')
call('local-patch',['git','diff',BASE,head,'--binary'],src)
print(json.dumps(manifest),flush=True)
