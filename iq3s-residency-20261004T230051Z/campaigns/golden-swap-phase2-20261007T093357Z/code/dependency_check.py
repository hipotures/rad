import sys,hashlib,tarfile,subprocess,importlib.metadata,platform,json,shutil
from pathlib import Path
C=Path(__file__).resolve().parents[1]
from common import *
no_gpu();gg=load(C/'references/ggml-source-original.json');archive=W/'inputs/ggml-base.tar.gz';h=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest();assert h==gg['archive_SHA256'],h
extract=W/'tmp/ggml-reference';extract.mkdir(exist_ok=False)
with tarfile.open(archive) as t:t.extractall(extract,filter='data')
base=next(extract.iterdir());local=Path(gg['path']);key=lambda root:{str(p.relative_to(root)):hashlib.file_digest(p.open('rb'),'sha256').hexdigest() for p in root.rglob('*') if p.is_file()}
with Heartbeat('pinned ggml source parity',5):
 a=key(base);b=key(local);changed=sorted(k for k in a.keys()|b.keys() if a.get(k)!=b.get(k))
assert not changed,changed[:30]
for name in ['upstream-strata-base.json','upstream-ggml-base.json']:shutil.copyfile(W/'tmp'/name,C/'references'/name)
result={'state':'PASS','upstream':'https://github.com/ggml-org/llama.cpp','base_sha':gg['pinned_commit'],'archive_sha256':h,'archive_bytes':archive.stat().st_size,'local_source':str(local),'downloadable':True,'source_files':len(a),'changed_paths':changed,'dependency_patch':'None required: every acquired source file matches the official pinned archive.','tested':'Fetched immutable commit archive with gh and compared every file SHA256 against compiled dependency snapshot, after all replay timing.'};save(C/'tests/ggml-recovery.json',result)
commands=[x['command'] for x in [json.loads(s) for s in (C/'attempt-ledger.jsonl').read_text().splitlines()] if x['message']=='Runtime build'];versions={}
for name in ['numpy','psutil','cmake','ninja','joblib','scikit-learn','cloudpickle','scipy']:
 try:versions[name]=importlib.metadata.version(name)
 except importlib.metadata.PackageNotFoundError:pass
save(C/'configs/dependencies.json',{'upstream_strata':'https://github.com/Niko1221/Strata','obtainable_base':'6f32ec070f23ced9f50e704d854d775da52591ab','experimental_source':load(C/'configs/runtime-identity.json'),'cumulative_patch':'patches/cumulative-from-original.diff','source_recovery_test':'tests/source-recovery.json','ggml':result,'exact_build_commands':commands,'toolchain':{'python':platform.python_version(),'gcc':'15.2.0 Ubuntu15.2.0-16ubuntu1','CUDA':'13.4 V13.4.92','cmake':'4.3.0','ninja':'1.13.0.git.kitware.jobserver-pipe-1','CUDA_architecture':'89'},'Python_packages':versions,'tape_checksum_helper':{'source':'code/fnv64.c','command':['gcc','-O3','-shared','-fPIC','code/fnv64.c','-o',str(W/'builds/libfnv64.so')],'parity':'tests/tape-validator-parity.json'},'offline_compile':['g++','-O3','-std=c++20','-pthread','-I'+str(SOURCE/'include'),'-I/usr/local/cuda/include','code/offline.cpp','-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(W/'builds/offline')],'host_profile':'Two RTX4090; same frozen Q4/K24/PCIe0.28/pool100us. CUDA driver/compiler version and native source remain fixed; rebuilt executables require a new identity/safety check.'})
(C/'requirements-execution.txt').write_text(''.join(f'{k}=={v}\n' for k,v in versions.items() if k not in ['cmake','ninja']))
print('GGML_PARITY_PASS',len(a),flush=True)
