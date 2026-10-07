from pathlib import Path
import json,hashlib,subprocess
from owned import C,run
R=C.parents[1];src=C/'src/decomposition-v2';build=C/'builds/decomposition-v2';venv=R/'src/control/.venv/bin'
run('source-add-v2',['git','add','include/strata/research'],src,timeout=30)
run('source-commit-v2',['git','-c','user.name=Local Research','-c','user.email=research@localhost','commit','-m','Add opt-in causal residual-life treatment for censored victims; default and full remain unchanged'],src,timeout=30)
run('configure-v2',[venv/'cmake','-S',src,'-B',build,'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(venv/'ninja'),'-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_GGML_DIR=/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325','-DSTRATA_BUILD_TESTS=ON'],timeout=180)
run('build-v2',[venv/'cmake','--build',build,'-j','8'],timeout=900)
identity={'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True,timeout=30).strip(),'upstream_base':'6f32ec070f23ced9f50e704d854d775da52591ab','replay_substrate':'117bc89b3bacbf263379c336557e6c8aa07aff5e','source':str(src),'build':str(build),'exe':str(build/'strata'),'binary_sha256':hashlib.sha256((build/'strata').read_bytes()).hexdigest()}
(C/'git/oracle-decomposition-v2-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
(C/'patches/information-v2.diff').write_bytes(subprocess.check_output(['git','diff','117bc89b3bacbf263379c336557e6c8aa07aff5e','HEAD'],cwd=src,timeout=30))
print(json.dumps(identity),flush=True)
