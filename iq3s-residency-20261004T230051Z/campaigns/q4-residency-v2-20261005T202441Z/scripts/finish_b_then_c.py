"""Finite sequential A/B gate and C dependency proof/build; no headline overlap."""
from campaign import C,R,load,save,guard
import psutil,time,subprocess,datetime,json

def main():
    until=time.time()+600
    while psutil.pid_exists(1842760):
        guard();assert time.time()<until,'H4 diagnostic collector timeout';time.sleep(5)
    py=str(R/'src/control/.venv/bin/python')
    steps=[('cost-analysis-B',['scripts/analyze_costs.py']),('early-projection-B',['scripts/early_projection.py']),('phase-B-report',['scripts/phase_b_report.py'])]
    for name,args in steps:
        guard()
        with (C/'logs'/f'{name}.log').open('x') as f:r=subprocess.run([py]+args,cwd=C,stdout=f,stderr=subprocess.STDOUT,timeout=900)
        if r.returncode:raise RuntimeError((name,r.returncode))
        print('STEP_COMPLETE',name,flush=True)
    record={'id':'E032-q4-live-residency','status':'RUNNING','campaign':str(C),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'At most2 frozen finalists; minimal ordering proof before early live; defaultOFF guards/tests before final paired3x3contexts.'}
    for ledger in [C/'ledger.jsonl',R/'experiments.jsonl']:
        with ledger.open('a') as f:f.write(json.dumps(record)+'\n')
    with (C/'logs/async-order-proof.log').open('x') as f:r=subprocess.run([py,'scripts/run_order_proof.py'],cwd=C,stdout=f,stderr=subprocess.STDOUT,timeout=240)
    save(C/'phase-c/order-proof-status.json',{'exit_code':r.returncode,'log':str(C/'logs/async-order-proof.log')})
    print('ORDER_PROOF_RESULT',r.returncode,flush=True)
    for variant,patch in [('history-v1','patch_history.py')]+([('early-v1','patch_early.py')] if r.returncode==0 else []):
        guard()
        with (C/'logs'/f'build-{variant}.log').open('x') as f:b=subprocess.run([py,'scripts/build.py',variant,'--patch',patch],cwd=C,stdout=f,stderr=subprocess.STDOUT,timeout=2400)
        print('BUILD_RESULT',variant,b.returncode,flush=True)
        if b.returncode:raise RuntimeError(('candidate build failure preserved',variant))
if __name__=='__main__':main()
