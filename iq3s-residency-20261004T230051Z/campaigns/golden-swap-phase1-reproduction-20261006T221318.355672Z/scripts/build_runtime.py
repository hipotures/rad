"""Isolated same-substrate binary; never rebuild from replay launchers."""
import subprocess,hashlib,os
from common import *
no_gpu();src=C/'source/runtime';build=C/'builds/runtime';root=C.parents[1];venv=root/'src/control/.venv/bin'
subprocess.run(['git','add','include/strata/research/q4_oracle.hpp','include/strata/research/q4_victim_model.hpp'],cwd=src,check=True,timeout=30)
subprocess.run(['git','-c','user.name=Local Research','-c','user.email=research@localhost','commit','-m','Add opt-in CPU causal victim ranking and matched exchange guards'],cwd=src,check=True,timeout=30)
commands=[['cmake','-S',str(src),'-B',str(build),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(venv/'ninja'),'-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_GGML_DIR=/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325','-DSTRATA_BUILD_TESTS=ON'],['cmake','--build',str(build),'-j','8']]
for i,cmd in enumerate(commands):
 cmd[0]=str(venv/'cmake');ledger('Isolated runtime build step',command=cmd)
 with Heartbeat('runtime build '+str(i+1),3):
  with (C/'logs'/('runtime-build-'+str(i)+'.log')).open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=900)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip();i={'source':str(src),'build':str(build),'exe':str(build/'strata'),'source_sha':head,'binary_sha256':hashlib.sha256((build/'strata').read_bytes()).hexdigest(),'capture_substrate':'117bc89b3bacbf263379c336557e6c8aa07aff5e','decomposition_substrate':'bbfea2955ec238f7e6406b11c74e577c996c4a8d','original_source':'6f32ec070f23ced9f50e704d854d775da52591ab','settings':'Q4/K24/PCIe.28/100us/15workers/MTP4minp.5/INT8KV/kvresident32768/prefillauto/suffixreuseOFF','base_configs_sha256':hashlib.sha256((P0/'configs.json').read_bytes()).hexdigest(),'frozen_selection_sha256':hashlib.sha256((C/'models/selection.json').read_bytes()).hexdigest()};save(C/'builds/runtime-identity.json',i)
(C/'patches/causal-victim.diff').write_bytes(subprocess.check_output(['git','diff','bbfea2955ec238f7e6406b11c74e577c996c4a8d','HEAD'],cwd=src));print('RUNTIME READY',i,flush=True)
