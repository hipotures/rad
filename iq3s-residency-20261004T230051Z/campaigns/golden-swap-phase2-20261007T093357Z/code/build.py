import subprocess,hashlib
from common import *
no_gpu();venv=C.parents[1]/'src/control/.venv/bin'
cmd=['git','add','include/strata/research/q4_oracle.hpp'];subprocess.run(cmd,cwd=SOURCE,check=True)
subprocess.run(['git','-c','user.name=Local Research','-c','user.email=research@localhost','commit','-m','Add bounded target-use lifecycle and transaction instrumentation'],cwd=SOURCE,check=True)
commands=[[str(venv/'cmake'),'-S',str(SOURCE),'-B',str(BUILD),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(venv/'ninja'),'-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_GGML_DIR=/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325','-DSTRATA_BUILD_TESTS=ON'],[str(venv/'cmake'),'--build',str(BUILD),'-j','8']]
for i,cmd in enumerate(commands):
 ledger('Runtime build',command=cmd)
 with Heartbeat('runtime build '+str(i),2),(W/'logs'/f'build-{i}.log').open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=1200)
i={'source':str(SOURCE),'build':str(BUILD),'exe':str(BUILD/'strata'),'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip(),'binary_sha256':hashlib.file_digest((BUILD/'strata').open('rb'),'sha256').hexdigest(),'phase1_source':'20e1e10f6848f11ec5580fc5ec7f97ea5d4e520b','base_configs_sha256':hashlib.sha256((P0/'configs.json').read_bytes()).hexdigest(),'checkpoint_sha256':hashlib.sha256((C/'models/logistic.txt').read_bytes()).hexdigest()}
save(C/'configs/runtime-identity.json',i)
(C/'patches/phase2.diff').write_bytes(subprocess.check_output(['git','diff','20e1e10',i['source_sha']],cwd=SOURCE));progress(2,'Runtime binary ready',version=i['source_sha'],next_action='Compiled end-to-end smoke before policy competition')
