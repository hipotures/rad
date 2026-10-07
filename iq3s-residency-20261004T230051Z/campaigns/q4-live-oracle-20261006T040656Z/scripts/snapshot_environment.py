"""Read-only bounded provenance snapshot; no clocks/power/system mutation."""
from pathlib import Path
import subprocess,json,datetime,sys,psutil,os
C=Path(__file__).resolve().parents[1];tag=sys.argv[1] if len(sys.argv)>1 else 'current';out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'affinity':psutil.Process().cpu_affinity(),'load':os.getloadavg(),'cpu_times':psutil.cpu_times()._asdict()}
commands={'kernel':['uname','-a'],'cpu':['lscpu'],'ram':['free','-b'],'gpu':['nvidia-smi','--query-gpu=index,name,uuid,driver_version,memory.total','--format=csv'],'gpu_detail':['nvidia-smi','-q'],'topology':['nvidia-smi','topo','-m'],'cuda':['/usr/local/cuda/bin/nvcc','--version'],'compiler':['g++','--version'],'source':['git','-C',str(C.parents[1]/'src/control'),'rev-parse','HEAD'],'source_status':['git','-C',str(C.parents[1]/'src/control'),'status','--porcelain']}
for k,cmd in commands.items():
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=15);out[k]={'command':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
(C/'git'/f'environment-{tag}.json').write_text(json.dumps(out,indent=2)+'\n');print('ENVIRONMENT_SAVED',tag)
