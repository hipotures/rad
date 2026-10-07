"""Finite, isolated local builds on frozen ancestry; never mutate normal checkouts."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, time
C=Path(__file__).resolve().parents[1];R=C.parents[1]
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 a=argparse.ArgumentParser();a.add_argument('variant');a.add_argument('--base-source',default=str(R/'src/control'));a.add_argument('--base-head',default='6f32ec070f23ced9f50e704d854d775da52591ab');a.add_argument('--patch');args=a.parse_args()
 source=C/'src'/args.variant;build=C/'builds'/args.variant;logs=C/'git/builds'/args.variant
 assert not source.exists() and not build.exists() and not logs.exists(),'No overwrite of existing source/build attempt'
 logs.mkdir(parents=True);records=[]
 def run(name,cmd,cwd=None,timeout=1200):
  start=time.time()
  with (logs/f'{name}.log').open('x') as f:r=subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
  records.append({'name':name,'command':cmd,'cwd':str(cwd) if cwd else None,'exit_code':r.returncode,'wall_s':time.time()-start});save(logs/'commands.json',records)
  print('BUILD',args.variant,name,r.returncode,flush=True)
  if r.returncode:raise RuntimeError((name,(logs/f'{name}.log').read_text()[-5000:]))
 run('clone',['git','clone','--no-hardlinks','--no-checkout',args.base_source,str(source)],timeout=180)
 run('checkout',['git','checkout','--detach',args.base_head],source,60)
 (source/'.venv').symlink_to(R/'src/control/.venv',target_is_directory=True)
 with (source/'.git/info/exclude').open('a') as f:f.write('\n.venv\n')
 if args.patch:
  run('patch',[str(R/'src/control/.venv/bin/python'),str(C/'scripts'/args.patch),str(source)],timeout=90)
  run('patch-diff',['git','diff','--binary'],source,60)
  run('add',['git','add','.'],source,60)
  run('commit',['git','-c','user.name=Local Research','-c','user.email=research@localhost','commit','-m','Local Q4 conditional-admission v3 '+args.variant],source,60)
 cmake=R/'src/control/.venv/bin/cmake';ninja=R/'src/control/.venv/bin/ninja'
 run('configure',[str(cmake),'-S',str(source),'-B',str(build),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(ninja),'-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_GGML_DIR=/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325','-DSTRATA_BUILD_TESTS=ON'],timeout=300)
 run('build',[str(cmake),'--build',str(build),'-j','8'],timeout=1800)
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
 ident={'source_sha':head,'upstream_base':'6f32ec070f23ced9f50e704d854d775da52591ab','parent':args.base_head,'source':str(source),'build':str(build),'exe':str(build/'strata'),'binary_sha256':hashlib.sha256((build/'strata').read_bytes()).hexdigest(),'commands':str(logs/'commands.json')}
 save(logs/'identity.json',ident)
 run('full-patch',['git','diff','6f32ec070f23ced9f50e704d854d775da52591ab',head,'--binary'],source,60)
 print('BUILD_COMPLETE',json.dumps(ident),flush=True)
if __name__=='__main__':main()
