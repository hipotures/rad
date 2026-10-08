#!/usr/bin/env python3
"""Low-overhead task-local console status from completed individual rows."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time


def processes(work_paths):
    records=[]
    uptime=float(Path('/proc/uptime').read_text().split()[0])
    hz=os.sysconf('SC_CLK_TCK')
    for path in Path('/proc').glob('[0-9]*'):
        try:
            command=(path/'cmdline').read_bytes().replace(b'\0',b' ').decode()
            if not any(work in command for work in work_paths): continue
            stat=(path/'stat').read_text().rsplit(')',1)[1].split()
            if command.startswith('/bin/bash') or 'write_live_status.py' in command: continue
            ticks=int(stat[11])+int(stat[12]);age=max(.01,uptime-int(stat[19])/hz)
            records.append(dict(pid=int(path.name),ppid=int(stat[1]),state=stat[0],
                                cpu_ticks=ticks,lifetime_cpu_percent=round(100*ticks/hz/age,1),
                                command_prefix=command[:140]))
        except (OSError,ValueError,UnicodeDecodeError):pass
    return records


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--configuration',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--interval',type=float,default=15)
    a=p.parse_args(); cache={}; previous_cpu={};previous_time=None
    while True:
        conf=json.loads(a.configuration.read_text()); batches=[]
        for batch in conf['batches']:
            rows=[]; work=Path(batch['work']); log=Path(batch['log'])
            for line in log.read_text().splitlines() if log.exists() else []:
                try: row=json.loads(line)
                except ValueError:continue
                if isinstance(row,dict) and 'case_id' in row: rows.append(row)
            completed={}; failures=0; best={}; best_phi={}; unique=set()
            for row in rows:
                case=row['case_id']
                if row.get('status')=='failed': failures+=1;continue
                if 'result_pattern'in batch:result=work/batch['result_pattern'].format(case=case)
                else:result=work/batch.get('result_subdirectory','raw')/case/batch.get('result_filename','result.json')
                cache_key=(str(work),case)
                if cache_key not in cache:
                    try: document=json.loads(result.read_text()); producer=document.get('producer',document)
                    except (OSError,ValueError,KeyError):continue
                    cache[cache_key]=dict(h=producer['h'],R=producer['R'],dag_sha256=producer['dag_sha256'],
                                     role_saving=document.get('role_saving'),witness=str(result),
                                     local_phi=document.get('local_phi',{}).get('value'))
                data=cache[cache_key];completed[case]=data;unique.add(data['dag_sha256'])
                key=str(data['h'])
                if key not in best or data['R']<best[key]['R']:best[key]=data
                if data['local_phi'] is not None and (key not in best_phi or data['local_phi']<best_phi[key]['local_phi']):best_phi[key]=data
            batches.append(dict(name=batch['name'],planned_cases=batch['planned_cases'],
                distinct_parent_dags=batch.get('distinct_parent_dags'),completed=len(completed),
                failed=failures,unique_final_byte_dags=len(unique),best_roles=best,best_local_phi=best_phi,
                count_scope=batch.get('count_scope','native configurations and final DAG bytes'),work=batch['work'],log=batch['log']))
        current=processes([batch['work'] for batch in conf['batches']]+conf.get('extra_process_paths',[]));now=time.monotonic()
        for record in current:
            old=previous_cpu.get(record['pid'])
            if old is not None and previous_time is not None:
                record['recent_cpu_percent']=round((record['cpu_ticks']-old)/os.sysconf('SC_CLK_TCK')/(now-previous_time)*100,1)
        previous_cpu={r['pid']:r['cpu_ticks']for r in current};previous_time=now
        result=dict(utc=datetime.now(timezone.utc).isoformat(),allocation=conf['allocation'],
                    count_scope='native configurations and byte-identical final DAGs; not graph-isomorphism classes',
                    completed_cohorts=conf.get('completed_cohorts'),running=batches,current_processes=current,
                    next_batch=conf.get('next_batch'),findings=conf.get('findings'))
        tmp=a.output.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');tmp.replace(a.output)
        time.sleep(a.interval)


if __name__=='__main__':main()
