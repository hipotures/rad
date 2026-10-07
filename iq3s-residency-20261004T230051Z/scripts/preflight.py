"""Run the reference's existing test suites and save dependency/environment evidence."""
import json, pathlib, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parents[1];SRC=ROOT/'src/control';BUILD=ROOT/'builds/control'
records=[]
for name,cmd,cwd in [
 ('python-dependency-repair',['uv','pip','install','--python',str(SRC/'.venv/bin/python'),'regex==2026.9.10','pyyaml==6.0.3'],ROOT),
 ('native-tests',[str(SRC/'.venv/bin/ctest'),'--test-dir',str(BUILD),'--output-on-failure','--timeout','60','-j','1'],ROOT),
 ('python-tests',[str(SRC/'.venv/bin/python'),'-m','unittest','discover','-s','serve','-p','test_*.py'],SRC),
 ('dependencies',['uv','pip','freeze','--python',str(SRC/'.venv/bin/python')],ROOT)]:
 path=ROOT/'logs'/f'{name}.log';start=time.time()
 with path.open('w') as out:r=subprocess.run(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT,timeout=1200)
 record={'name':name,'command':cmd,'cwd':str(cwd),'returncode':r.returncode,'wall_s':time.time()-start,'log':str(path)};records.append(record)
 print(name,r.returncode,round(record['wall_s'],2),path.read_text()[-1200:],flush=True)
 (ROOT/'git/preflight.json').write_text(json.dumps(records,indent=2)+'\n')
 if name=='python-dependency-repair' and r.returncode:raise SystemExit(r.returncode)
