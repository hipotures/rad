"""Prepare an isolated future reproducer; never append to the completed campaign."""
import argparse,datetime,hashlib,json,os,shutil,socket,subprocess,sys,time,signal
import psutil
from pathlib import Path
C=Path(__file__).resolve().parents[1]
def main():
    q=argparse.ArgumentParser();q.add_argument('--output',required=True,type=Path);q.add_argument('--arm',choices=['CONTROL','TRACE'],required=True);q.add_argument('--execute',action='store_true');a=q.parse_args()
    dest=a.output.resolve();assert not dest.exists(),'Fresh output namespace required';assert not dest.is_relative_to(C.parents[2]),'Execution must be external'
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,timeout=8).strip(),'GPU conflict'
    with socket.socket() as s:assert s.connect_ex(('127.0.0.1',18166))!=0,'Port conflict'
    manifest=json.loads((C/'input-manifest.json').read_text());ident=json.loads((C/'configs/runtime-identity.json').read_text())
    for x in manifest['external_inputs']:
        if x['id'] in ['math-rational-tape','math-rational-initial-state','warmup-payload','warmup-ids','math-rational-payload','math-rational-ids']:
            p=Path(x['path']);assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==x['sha256'],x['id']
    assert hashlib.file_digest(Path(ident['exe']).open('rb'),'sha256').hexdigest()==ident['binary_sha256']
    assert hashlib.sha256((C/'models/logistic.txt').read_bytes()).hexdigest()==ident['checkpoint_sha256']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ident['source'],text=True).strip()==ident['source_sha']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ident['source'],text=True).strip()
    dest.mkdir(parents=True);shutil.copytree(C/'code',dest/'code',ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(C/'models',dest/'models');(dest/'configs').mkdir()
    (dest/'inputs').mkdir();shutil.copyfile(C/'inputs/manifest.json',dest/'inputs/manifest.json')
    for name in ['runtime-identity.json','storage.json']:shutil.copyfile(C/'configs'/name,dest/'configs'/name)
    storage=json.loads((dest/'configs/storage.json').read_text());storage['work_root']=str(dest/'work');(dest/'configs/storage.json').write_text(json.dumps(storage,indent=2)+'\n')
    for name in ['raw','logs','builds','tmp']:(dest/'work'/name).mkdir(parents=True)
    helper=Path(json.loads((C/'configs/storage.json').read_text())['work_root'])/'builds/libfnv64.so'
    recovery=json.loads((C/'configs/runtime-recovery.json').read_text());assert hashlib.file_digest(helper.open('rb'),'sha256').hexdigest()==recovery['fnv_helper_sha256']
    shutil.copyfile(helper,dest/'work/builds/libfnv64.so')
    (dest/'active-run.json').write_text(json.dumps({'run':'runs/reproduction'},indent=2)+'\n');r=dest/'runs/reproduction';r.mkdir(parents=True)
    now=datetime.datetime.now(datetime.timezone.utc);clock={'start_utc':now.isoformat(),'deadline_utc':(now+datetime.timedelta(minutes=30)).isoformat(),'start_monotonic':time.monotonic(),'budget_s':1800,'scope':'Fresh one-request reproduction; not a campaign extension'};(r/'clock.json').write_text(json.dumps(clock,indent=2)+'\n')
    receipt={'state':'PREPARED_IDENTITY_CHECKED','arm':a.arm,'historical_campaign_replays_started':0,'output':str(dest),'binary_sha256':ident['binary_sha256'],'tape_sha256':manifest['task_provenance']['sha256'],'timeout_s':440,'maximum_measured_attempts':1,'build_or_update':False}
    (dest/'preparation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
    validation="import live; live.identities(); from tape import Tape; assert Tape("+repr(manifest['task_provenance']['tape'])+").validate()['state']=='PASS'; print('ISOLATED_RUNNER_AND_TAPE_VALIDATED_NO_INFERENCE',flush=True)"
    subprocess.run([sys.executable,'-c',validation],cwd=dest/'code',check=True,timeout=90)
    if a.execute:
        with (dest/'execution.log').open('x') as log:
            proc=subprocess.Popen([sys.executable,str(dest/'code/live.py'),'--task','math-rational','--arm',a.arm,'--label','reproduction-'+a.arm],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            created=psutil.Process(proc.pid).create_time();start=time.monotonic()
            (dest/'owned-process.json').write_text(json.dumps({'pid':proc.pid,'created':created,'historical_record_never_control_authority':True})+'\n')
            try:
                while proc.poll() is None:
                    assert time.monotonic()-start<440,'Reproduction timeout'
                    try:proc.wait(timeout=25)
                    except subprocess.TimeoutExpired:print('HEARTBEAT owned reproduction active',flush=True)
                assert proc.returncode==0,proc.returncode
            finally:
                if proc.poll() is None:
                    owned=psutil.Process(proc.pid);assert abs(owned.create_time()-created)<.1,'PID identity changed'
                    children=[(p.pid,p.create_time()) for p in owned.children(recursive=True)]
                    os.killpg(proc.pid,signal.SIGTERM)
                    try:proc.wait(timeout=20)
                    except subprocess.TimeoutExpired:
                        assert abs(psutil.Process(proc.pid).create_time()-created)<.1
                        os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=10)
                    for pid,birth in children:
                        try:
                            p=psutil.Process(pid)
                            if abs(p.create_time()-birth)<.1 and p.status()!=psutil.STATUS_ZOMBIE:p.terminate()
                        except psutil.NoSuchProcess:pass
        print('REPRODUCTION_COMPLETE',flush=True)
if __name__=='__main__':main()
