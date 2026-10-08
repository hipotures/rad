#!/usr/bin/env python3
"""Refill finished producer slots with paid clones on new seeded DAGs."""
import argparse,json,subprocess,sys,time
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--cohorts',type=Path,nargs='+',required=True)
    p.add_argument('--wait-for',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--workers',type=int,required=True)
    p.add_argument('--per-dimension',type=int,default=32)
    a=p.parse_args();assert not a.work.exists();a.work.mkdir(parents=True)
    rows=[]
    for path in a.cohorts:
        obj=json.loads(path.read_text());assert obj['status']=='complete';rows.extend(obj['rows'])
    parents=[];ids=[];inputs=a.work/'inputs';inputs.mkdir()
    for h in (23,25):
        seen=set()
        for row in sorted([r for r in rows if r.get('h')==h],key=lambda r:r['R']):
            key=row['logical_graph_sha256']
            if key in seen:continue
            seen.add(key);path=inputs/f'h{h}-{len(seen):03d}.json'
            path.write_text(json.dumps(dict(producer=row))+'\n');parents.append(path)
            ids.append(dict(h=h,logical_graph_sha256=key,R=row['R'],case_id=row['case_id']))
            if len(seen)==a.per_dimension:break
    code=Path(__file__).resolve().parent.parent/'agents/graph/code/positive_clone_search.py'
    command=[sys.executable,'-u',str(code),'--parent',*[str(x) for x in parents],
             '--work',str(a.work/'clones'),'--output',str(a.work/'results.json'),
             '--workers',str(a.workers),'--rounds','3','--policies','wide8','scarce','late','--tag-input']
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),command=command,parents=ids,
                  code_sha256=sha256(code.read_bytes()).hexdigest(),wait_for=str(a.wait_for),
                  question='Do paid whole-controller clones on newly seeded distinct DAGs improve the physical recurrence?',
                  source_inputs=[dict(path=str(x),sha256=sha256(x.read_bytes()).hexdigest())for x in a.cohorts])
    (a.work/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    print(json.dumps(dict(status='READY DISTINCT CLONE QUEUE',parents=len(parents),configurations=3*len(parents),wait_for=str(a.wait_for))),flush=True)
    while True:
        try:
            if json.loads(a.wait_for.read_text()).get('status')=='complete':break
        except (OSError,ValueError):pass
        time.sleep(10)
    print(json.dumps(dict(status='LAUNCHING NEW PAID CLONE EXPERIMENTS',utc=datetime.now(timezone.utc).isoformat())),flush=True)
    with (a.work/'compute.log').open('w') as log:
        child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        (a.work/'process.json').write_text(json.dumps(dict(pid=child.pid,command=command),indent=2)+'\n')
        print(json.dumps(dict(pid=child.pid,command=command)),flush=True)
        rc=child.wait()
    (a.work/'completion.json').write_text(json.dumps(dict(exit_code=rc,utc=datetime.now(timezone.utc).isoformat()))+'\n')
    assert rc==0

if __name__=='__main__':main()
