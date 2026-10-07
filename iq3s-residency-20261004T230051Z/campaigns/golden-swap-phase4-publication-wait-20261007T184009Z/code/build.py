"""Isolated build and durable source patch; no automatic updates."""
from common import *
import hashlib
no_gpu()
files=['include/strata/research/q4_oracle.hpp','include/strata/kernels/verify_kernels.hpp','include/strata/core/verify.hpp','src/core/verify.cpp','src/kernels/cuda/verify_kernels.cu','src/program/generate.cpp','include/strata/kernels/q4_trace.hpp','include/strata/kernels/shared_expert.hpp','include/strata/kernels/native_moe.hpp','include/strata/core/layer.hpp','src/kernels/cuda/shared_expert.cu','src/kernels/cuda/native_moe.cu','src/core/layer.cpp']
subprocess.run(['git','add','--',*files],cwd=SOURCE,check=True);subprocess.run(['git','-c','user.name=Local Research','-c','user.email=research@localhost','commit','-m','Record publication producer and consumer milestones in bounded buffers'],cwd=SOURCE,check=True)
venv=INPUT_PARENT.parent/'src/control/.venv/bin';ggml='/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325'
commands=[[str(venv/'cmake'),'-S',str(SOURCE),'-B',str(BUILD),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(venv/'ninja'),'-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_BUILD_TESTS=ON','-DSTRATA_GGML_DIR='+ggml],[str(venv/'cmake'),'--build',str(BUILD),'-j','8']]
for k,cmd in enumerate(commands):
 ledger('Build START',command=cmd)
 with Heartbeat('build '+str(k),2),(W/'logs'/f'build-v2-{k}.log').open('x') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
 ledger('Build END',command=cmd,exit_code=r.returncode);assert r.returncode==0,cmd
identity={'source':str(SOURCE),'build':str(BUILD),'exe':str(BUILD/'strata'),'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip(),'binary_sha256':hashlib.file_digest((BUILD/'strata').open('rb'),'sha256').hexdigest(),'base_configs_sha256':hashlib.sha256((P0/'configs.json').read_bytes()).hexdigest(),'checkpoint_sha256':hashlib.sha256((C/'models/logistic.txt').read_bytes()).hexdigest(),'parent_source':'f3b4f19157b39ae017e2fd91814c8f5728e3b1cc','commands':commands,'ggml':ggml}
save(C/'configs/runtime-identity.json',identity);(C/'patches').mkdir(exist_ok=True)
for name,base in [('phase4.diff',identity['parent_source']),('cumulative-from-original.diff','6f32ec070f23ced9f50e704d854d775da52591ab')]:
 (C/'patches'/name).write_bytes(subprocess.check_output(['git','diff',base,identity['source_sha']],cwd=SOURCE))
subprocess.run(['gcc','-O3','-shared','-fPIC',str(C/'code/fnv64.c'),'-o',str(W/'builds/libfnv64.so')],check=True)
progress(2,'Binary built; next compiled fixtures',version=identity['source_sha'])
