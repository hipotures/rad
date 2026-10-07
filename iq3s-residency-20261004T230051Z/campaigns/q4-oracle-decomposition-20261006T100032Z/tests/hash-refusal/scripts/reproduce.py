"""Explicit experimental replay only. Post-campaign reproductions use new immutable namespaces."""
import argparse,json,hashlib,datetime,subprocess,os,shutil,sys,time
from pathlib import Path
C=Path(__file__).resolve().parents[1];R=C.parents[1];PY=R/'src/control/.venv/bin/python'
def main():
 a=argparse.ArgumentParser();a.add_argument('--arm',choices=['current','FF','64F','F64','6464','F256'],required=True);a.add_argument('--profile',choices=['32k','128k','256k'],required=True);a.add_argument('--check',action='store_true');a.add_argument('--timeout-s',type=int,default=1200);v=a.parse_args();assert 300<=v.timeout_s<=1800
 identity=json.loads((C/'git/oracle-decomposition-v2-identity.json').read_text());assert hashlib.sha256(Path(identity['exe']).read_bytes()).hexdigest()==identity['binary_sha256'];assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=identity['source'],text=True,timeout=10).strip()==identity['source_sha'];assert not subprocess.check_output(['git','status','--porcelain'],cwd=identity['source'],text=True,timeout=10).strip()
 from verify_model import verify
 model=verify();tape=C/'tapes'/f'capture-{v.profile}-v3.bin';assert tape.exists() and Path(str(tape)+'.initial-state.bin').exists()
 from tape import Tape
 validation=Tape(tape).validate();assert not validation['errors']
 from runner import config
 cfg=config(v.profile,'oracle-decomposition-v2');budgets={'current':('full','full'),'FF':('full','full'),'64F':('64','full'),'F64':('full','64'),'6464':('64','64'),'F256':('full','256')};i,b=budgets[v.arm];cfg['env'].update(STRATA_Q4_ORACLE_SUBSTRATE='1',STRATA_Q4_ORACLE_MODE='off' if v.arm=='current' else 'full',STRATA_Q4_ORACLE_STRATEGY='deadline',STRATA_Q4_ORACLE_HORIZON='64',STRATA_Q4_ORACLE_INCOMING=i,STRATA_Q4_ORACLE_VICTIM=b,STRATA_Q4_ORACLE_UNKNOWN='legacy',STRATA_Q4_TAPE=str(tape),STRATA_Q4_TAPE_MODE='replay',STRATA_Q4_TAPE_REQUEST='2');print('EXPERIMENTAL_FORCED_WORK_REPLAY_NOT_NORMAL_SERVING',flush=True);print(json.dumps({'identity':identity,'profile':v.profile,'arm':v.arm,'I':i,'V':b,'E':64,'P':'common_full_current_window','tape':str(tape),'work_validation':validation,'config':cfg},indent=2),flush=True)
 if v.check:print('CHECK_PASS_NO_SERVER',flush=True);return
 import psutil,socket
 assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,timeout=10).strip(),'Conflicting GPU compute; refuse'
 with socket.socket() as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',18146))
 dest=R/'campaigns'/('q4-decomposition-reproduce-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));dest.mkdir()
 for name in ['scripts','configs','git','inputs']:
  shutil.copytree(C/name,dest/name)
 for name in ['raw','logs','analysis','phase-a','phase-b','phase-c','tapes']:(dest/name).mkdir()
 shutil.copyfile(C/'analysis/libfnv64.so',dest/'analysis/libfnv64.so')
 for p in (C/'tapes').iterdir():
  if p.is_file():(dest/'tapes'/p.name).symlink_to(p.resolve())
 for name in ['capture-32k-v3','capture-128k-v3','capture-256k-v3']:(dest/'raw'/name).symlink_to((C/'raw'/name).resolve())
 now=time.time();mono=time.monotonic();deadline={'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deadline_utc':datetime.datetime.fromtimestamp(now+v.timeout_s,datetime.timezone.utc).isoformat(),'deadline_epoch':now+v.timeout_s,'experiment_cutoff_monotonic':mono+v.timeout_s-180};(dest/'deadline.json').write_text(json.dumps(deadline,indent=2)+'\n');(dest/'STATUS.json').write_text(json.dumps({'state':'EXPLICIT_MANUAL_REPRODUCTION','parent':str(C),'not_extension_of_completed_deadline':True},indent=2)+'\n')
 cmd=[PY,dest/'scripts/runner.py','replay','--profile',v.profile,'--label','manual-'+v.arm,'--payload',v.profile+'-run1','--variant','oracle-decomposition-v2','--tape',tape,'--oracle','off' if v.arm=='current' else 'full','--incoming',i,'--victim',b,'--unknown','legacy']
 sys.path.insert(0,str(dest/'scripts'));import importlib.util
 spec=importlib.util.spec_from_file_location('manual_owned',dest/'scripts/owned.py');owned=importlib.util.module_from_spec(spec);spec.loader.exec_module(owned)
 owned.run('manual-replay',cmd,timeout=v.timeout_s)
 print('ARTIFACTS',dest,flush=True)
if __name__=='__main__':main()
