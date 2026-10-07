"""Repair bounded victim-safety future leakage in standalone simulation, before live jobs."""
from pathlib import Path
import subprocess,os,json,time,psutil,signal,shutil,hashlib
C=Path(__file__).resolve().parents[1]
def run(label,cmd,env=None,timeout=240):
 start=time.monotonic();out=C/'phase-b'/f'{label}.stdout';err=C/'phase-b'/f'{label}.stderr'
 with out.open('x') as o,err.open('x') as e:
  p=subprocess.Popen(cmd,cwd=C,env=env,stdout=o,stderr=e,start_new_session=True)
  rec={'command':cmd,'pid':p.pid,'create_time':psutil.Process(p.pid).create_time(),'timeout_s':timeout};last=start
  try:
   while p.poll() is None:
    if time.monotonic()-start>timeout:raise TimeoutError(label)
    if time.monotonic()-last>15:print('STRICT_OFFLINE_PROGRESS',label,round(time.monotonic()-start),flush=True);last=time.monotonic()
    time.sleep(.5)
  finally:
   if p.poll() is None:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=10)
 rec.update(exit_code=p.returncode,wall_s=time.monotonic()-start)
 if p.returncode==0 and label!='strict-horizon-build':rec['metrics']=json.loads(out.read_text())
 (C/'phase-b'/f'{label}.json').write_text(json.dumps(rec,indent=2)+'\n');print('STRICT_OFFLINE_EXIT',label,p.returncode,rec['wall_s'],flush=True);assert p.returncode==0,err.read_text()
standalone=C/'analysis/offline-strict'
if not standalone.exists():
 standalone.mkdir();shutil.copytree(C/'src/oracle-v1/include',standalone/'include');shutil.copyfile(C/'scripts/offline.cpp',standalone/'offline.cpp')
 h=standalone/'include/strata/research/q4_oracle.hpp';source=h.read_text();needle='bool protected_now(int l,int e)const{';assert needle in source;source=source.replace(needle,needle+'int at=std::max(0,current);int event=(at/48)*48+l;if(horizon&&event>at+horizon)return false;');h.write_text(source)
manifest={'base_header_source':json.loads((C/'git/oracle-v1-identity.json').read_text())['source_sha'],'modified_header_sha256':hashlib.sha256((standalone/'include/strata/research/q4_oracle.hpp').read_bytes()).hexdigest(),'simulation_source_sha256':hashlib.sha256((standalone/'offline.cpp').read_bytes()).hexdigest(),'simulation_only':True,'live_runtime_unchanged':True}
(C/'phase-b/strict-offline-provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
run('strict-horizon-build',['g++','-O3','-std=c++17','-Ianalysis/offline-strict/include','-I/usr/local/cuda/include','analysis/offline-strict/offline.cpp','-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-pthread','-o','analysis/offline-strict/offline'],timeout=120)
env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(STRATA_Q4_TAPE=str(C/'tapes/capture-32k-v1.bin'),STRATA_Q4_TAPE_MODE='replay')
for h in [1,4,16,64]:run(f'strict-horizon-{h}',['analysis/offline-strict/offline','transfer',str(h),'0'],env)
