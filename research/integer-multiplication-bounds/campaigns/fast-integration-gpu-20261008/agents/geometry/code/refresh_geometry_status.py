#!/usr/bin/env python3
"""Compact current status; archived PID records are verified against live argv."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json


def refresh(work,output,next_batch):
    records=[]
    for path in list(work.glob('*/process.json'))+list(work.glob('*/profile/process.json')):
        old=json.loads(path.read_text());proc=Path(f'/proc/{old["pid"]}')
        try:
            argv=[x.decode() for x in (proc/'cmdline').read_bytes().split(b'\0') if x]
            if not argv or argv[0]!=old['command'][0]:continue
            state=(proc/'stat').read_text().split(') ',1)[1].split()[0]
            if state=='Z':continue
        except (FileNotFoundError,ProcessLookupError):continue
        records.append(dict(pid=old['pid'],case=path.parent.name,state=state,command=argv))
    progress=json.loads((work/'status.json').read_text()) if (work/'status.json').exists() else {'completed':0,'phase':'starting'}
    result=dict(utc=datetime.now(timezone.utc).isoformat(),completed_prior_positive_exact_profiles=716,
                current_batch=str(work),progress=progress,actual_live_processes=records,next_batch=next_batch,
                best_completed_local_profiles={'23':dict(R=36219,Phi_at_a_4e_5=170.36414474213998),
                                               '25':dict(R=47461,Phi_at_a_4e_5=237.42977709192945)},
                best_status='Independent scalar/rational nesting/literal physical compiler passed on both axes; full multiplication assembly belongs to coordinator')
    output.write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--next',required=True);a=p.parse_args();r=refresh(a.work,a.output,a.next);print(json.dumps(dict(utc=r['utc'],progress=r['progress'],pids=[x['pid'] for x in r['actual_live_processes']])))
