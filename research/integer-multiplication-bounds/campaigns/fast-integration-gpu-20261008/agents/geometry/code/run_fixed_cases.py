#!/usr/bin/env python3
"""Six-slot bounded exact fixed-profile sweeps over retained changed DAGs.

Uses independently supplied scalar DAGs; original-envelope matching is rebuilt
by the pinned, minimally modified native profiler, never copied from positive
matching. This is a campaign script, not a general scheduling framework.
"""
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,shutil,subprocess,time

def worker(task,exe,root):
    start=time.monotonic();case=root/task['case_id'];case.mkdir(parents=True,exist_ok=False)
    source=Path(task['dag_path']);assert sha256(source.read_bytes()).hexdigest()==task['dag_sha256']
    dag=case/'dag.bin';shutil.copy2(source,dag)
    (case/'source-record.json').write_text(json.dumps(task,indent=2)+'\n')
    command=[str(exe),str(dag),str(dag)+'.original-links',str(dag)+'.selected-uses.json']
    with (case/'native.stdout.json').open('w') as out,(case/'native.stderr.log').open('w') as err:
        process=subprocess.Popen(command,stdout=out,stderr=err);pid=process.pid
        code=process.wait(timeout=600)
    result=dict(case_id=task['case_id'],configuration=task['configuration'],pid=pid,elapsed_seconds=time.monotonic()-start,
                exit_code=code,command=command,dag_path=str(dag),dag_sha256=task['dag_sha256'])
    if code==0:
        result.update(producer=json.loads((case/'native.stdout.json').read_text()),
                      fixed_profile=json.loads(Path(str(dag)+'.round3_rankone_certified_profiles.json').read_text()),
                      selected_links_path=str(dag)+'.selected-uses.json',
                      selected_links_sha256=sha256(Path(str(dag)+'.selected-uses.json').read_bytes()).hexdigest(),
                      status='complete exact fixed-profile finite candidate')
    else:result['status']='failed native profile'
    (case/'result.json').write_text(json.dumps(result,indent=2)+'\n');return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--executable',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--workers',type=int,default=6);args=ap.parse_args()
    assert 1<=args.workers<=6 and not args.output.exists() and not args.work.exists()
    args.work.mkdir(parents=True);raw=json.loads(args.input.read_text());rows=raw.get('rows',raw) if isinstance(raw,dict) else raw
    tasks=[r for r in rows if r.get('status')=='producer and native rank audit passed' and r.get('h') in (23,25)]
    assert len({r['case_id'] for r in tasks})==len(tasks)
    result=dict(started_utc=datetime.now(timezone.utc).isoformat(),input_sha256=sha256(args.input.read_bytes()).hexdigest(),
                executable_sha256=sha256(args.executable.read_bytes()).hexdigest(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),workers=args.workers,tasks=[r['case_id'] for r in tasks],rows=[])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(worker,task,args.executable,args.work) for task in tasks]
        for future in as_completed(futures):
            row=future.result();result['rows'].append(row)
            tmp=args.output.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(args.output)
            print(json.dumps({k:row[k] for k in ('case_id','pid','status','elapsed_seconds')}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
