"""Frozen CMake/compiler compatibility, binary/model identities, no rebuild."""
from campaign import C,R,load,save
from pathlib import Path
import json,subprocess,hashlib

def cache(p):
 out={}
 for line in p.read_text().splitlines():
  if '=' in line and ':' in line and not line.startswith('//'):
   key,val=line.split('=',1);out[key]=val
 return out
base=cache(R/'builds/control/CMakeCache.txt');interesting=[k for k in base if k.startswith(('STRATA_','CMAKE_CUDA_ARCHITECTURES','CMAKE_BUILD_TYPE','CMAKE_CXX_COMPILER:','CMAKE_CUDA_COMPILER:','CMAKE_CXX_FLAGS','CMAKE_CUDA_FLAGS'))]
rows=[]
for variant in ['history-v2','early-v1','cost-router-v1']:
 ident=load(C/'git/builds'/variant/'identity.json');candidate=cache(Path(ident['build'])/'CMakeCache.txt');raw_diff={k:[base[k],candidate.get(k)] for k in interesting if candidate.get(k)!=base[k]}
 diff={k:v for k,v in raw_diff.items() if not (k=='STRATA_PLE_FIXTURE_DIR:PATH' and candidate[k]==str(Path(ident['source'])/'bench/micro') and base[k]==str(R/'src/control/bench/micro'))}
 # Source/binary dirs are path provenance; flags must agree.
 actual=hashlib.sha256(Path(ident['exe']).read_bytes()).hexdigest();assert actual==ident['binary_sha256'];assert not diff,diff
 rows.append({'variant':variant,'identity':ident,'settings_identical':True,'flags':{k:base[k] for k in interesting},'runtime_flag_differences':diff,'source_relative_fixture_paths':raw_diff})
save(C/'git/build-compatibility.json',rows)
print('BUILD_FLAGS_IDENTICAL',flush=True)
