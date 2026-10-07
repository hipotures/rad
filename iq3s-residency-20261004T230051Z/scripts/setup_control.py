"""Materialize the immutable reference and its own build/venv; save all commands."""
import hashlib, json, os, pathlib, shutil, subprocess, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
OLD = pathlib.Path('/srv/ai/strata-pr578-refresh-20261004-control')
BASE = '6f32ec070f23ced9f50e704d854d775da52591ab'
SRC = ROOT/'src/control'
BUILD = ROOT/'builds/control'
DEPS = pathlib.Path('/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325')
DEADLINE = json.loads((ROOT/'deadline.json').read_text())['deadline_epoch']
def call(name, cmd, cwd=None):
    remaining = max(1, min(1800, int(DEADLINE-time.time()-2700)))
    log = ROOT/'logs'/f'{name}.log'
    with log.open('w') as f:
        result = subprocess.run(cmd, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, timeout=remaining)
    record = {'command':cmd,'cwd':str(cwd) if cwd else None,'returncode':result.returncode,'log':str(log)}
    (ROOT/'git'/f'{name}.json').write_text(json.dumps(record,indent=2))
    if result.returncode:
        print(log.read_text()[-6000:], flush=True)
        raise SystemExit(result.returncode)
    print(name,'OK',flush=True)

call('clone-control',['git','clone','--no-hardlinks','--no-checkout',str(OLD),str(SRC)])
call('checkout-control',['git','checkout','--detach',BASE],SRC)
call('venv-control',['uv','venv',str(SRC/'.venv'),'--python','/usr/bin/python3.14'])
call('deps-control',['uv','pip','install','--python',str(SRC/'.venv/bin/python'),'cmake==4.3.0','ninja==1.13.0','jinja2','psutil','numpy','jsonschema'])
old = json.loads(pathlib.Path('/srv/ai/benchmarks/strata-qwen38/threeway-32k-128k-longdecode-20261004T212330Z/git/CURRENT-preserved-control-configure-command.json').read_text())['command']
# Use the preserved compiler/CMake executable and flags. New generated outputs only.
cmd=[str(SRC/'.venv/bin/cmake'),'-S',str(SRC),'-B',str(BUILD),'-G','Ninja',
     '-DCMAKE_MAKE_PROGRAM='+str(SRC/'.venv/bin/ninja'),'-DCMAKE_BUILD_TYPE=Release',
     '-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_GGML_DIR='+str(DEPS),'-DSTRATA_BUILD_TESTS=ON']
call('configure-control',cmd)
call('build-control',[str(SRC/'.venv/bin/cmake'),'--build',str(BUILD),'-j','8'])
exe=BUILD/'strata'
manifest={'source_head':BASE,'source_status':subprocess.check_output(['git','status','--porcelain'],cwd=SRC,text=True),'binary':str(exe),'binary_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'source':str(SRC),'build':str(BUILD),'ggml_source':str(DEPS),'toolchain_comparison_required':True,'preserved_configure':old}
(ROOT/'git/control-build.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest),flush=True)
