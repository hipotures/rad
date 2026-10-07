"""Verify wrapper timeout ends its detached descendants and leaves an external sentinel alone."""
import subprocess,time
import psutil
from lab import ROOT,load,save,owned_stop
out=ROOT/'analysis/timeout-cleanup-v1'
if out.exists():raise RuntimeError('Existing timeout cleanup attempt')
out.mkdir(parents=True);py=str(ROOT/'src/control/.venv/bin/python')
sentinel=subprocess.Popen([py,'-c','import time; time.sleep(40)'],start_new_session=True);created=psutil.Process(sentinel.pid).create_time()
try:
    cmd=[py,str(ROOT/'scripts/run_logged.py'),'--path',str(out/'fixture-wrapper'),'--timeout','2','--',py,str(ROOT/'scripts/timeout_fixture_child.py'),str(out/'child.json')]
    with (out/'test.log').open('w') as stream:r=subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=25)
    child=load(out/'child.json');wrapper=load(out/'fixture-wrapper/command.json')
    alive=False
    try:
        p=psutil.Process(child['pid']);alive=abs(p.create_time()-child['create_time'])<=.1 and p.is_running() and p.status()!=psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:pass
    untouched=sentinel.poll() is None
    result={'state':'PASS' if wrapper.get('timeout') and not alive and untouched else 'FAIL','command':cmd,'returncode':r.returncode,'wrapper_timeout':wrapper.get('timeout'),'owned_detached_child_alive':alive,'external_sentinel_alive':untouched,'recorded_owned_descendants':wrapper.get('timeout_owned_descendants'),'scope':'NoGPU/model. Wrapper process-group cleanup must include separately detached ownedSessionchildren and preserve non-descendant processes.'}
    save(out/'summary.json',result);print(result,flush=True)
    if result['state']!='PASS':raise SystemExit(1)
finally:
    owned_stop(sentinel.pid,created)
    sentinel.wait(timeout=5)
