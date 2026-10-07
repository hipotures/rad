"""Isolated explicit build; retain source and binary identities."""
import hashlib,subprocess
from common import *
no_gpu();p=SOURCE/'include/strata/research/q4_oracle.hpp';s=p.read_text().replace('#include <ctime>','#include <ctime>\n#include <climits>');p.write_text(s)
files=['include/strata/research/q4_oracle.hpp','include/strata/kernels/verify_kernels.hpp','include/strata/core/verify.hpp','src/core/verify.cpp','src/kernels/cuda/verify_kernels.cu','src/program/generate.cpp']
subprocess.run(['git','add','--',*files],cwd=SOURCE,check=True);subprocess.run(['git','-c','user.name=Local Research','-c','user.email=research@localhost','commit','-m','Memoize incoming demand with exact logical expiry and measure dependency waits'],cwd=SOURCE,check=True)
venv=INPUT_PARENT.parent/'src/control/.venv/bin';ggml='/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325'
commands=[[str(venv/'cmake'),'-S',str(SOURCE),'-B',str(BUILD),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(venv/'ninja'),'-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_BUILD_TESTS=ON','-DSTRATA_GGML_DIR='+ggml],[str(venv/'cmake'),'--build',str(BUILD),'-j','8']]
for k,cmd in enumerate(commands):
 ledger('Build START',command=cmd)
 with Heartbeat('build '+str(k),2),(W/'logs'/f'build-{k}.log').open('x') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
 ledger('Build END',command=cmd,exit_code=r.returncode);assert r.returncode==0,cmd
p0=load(P0/'configs.json');base=load(INPUT_PARENT/'golden-swap-phase2-20261007T093357Z/configs/runtime-identity.json')
i={'source':str(SOURCE),'build':str(BUILD),'exe':str(BUILD/'strata'),'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip(),'binary_sha256':hashlib.file_digest((BUILD/'strata').open('rb'),'sha256').hexdigest(),'base_configs_sha256':hashlib.sha256((P0/'configs.json').read_bytes()).hexdigest(),'checkpoint_sha256':hashlib.sha256((C/'models/logistic.txt').read_bytes()).hexdigest(),'phase2':base,'commands':commands,'ggml':ggml}
save(C/'configs/runtime-identity.json',i)
(C/'patches/phase3.diff').write_bytes(subprocess.check_output(['git','diff','c12a0b11',i['source_sha']],cwd=SOURCE));(C/'patches/cumulative-from-original.diff').write_bytes(subprocess.check_output(['git','diff','6f32ec07',i['source_sha']],cwd=SOURCE))
subprocess.run(['gcc','-O3','-shared','-fPIC',str(C/'code/fnv64.c'),'-o',str(W/'builds/libfnv64.so')],check=True)
progress(2,'Compiled experimental binary',version=i['source_sha'],next_action='Deterministic parity and instrumentation fixtures')
