#!/usr/bin/env python3
"""Refill the same CPU slots after the pair-hierarchy producer queue finishes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--cohort',type=Path,required=True)
p.add_argument('--work',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--workers',type=int,default=9)
a=p.parse_args()
while True:
    try:
        cohort=json.loads(a.cohort.read_text())
        if cohort['status']=='complete':break
    except (FileNotFoundError,json.JSONDecodeError):
        pass
    time.sleep(2)
parents=[]
for row in cohort['rows']:
    if row['status']=='failed':continue
    parents.append(str(Path(row['initial_producer']['dag_path']).parent/'parent.json'))
command=[sys.executable,str(Path(__file__).with_name('positive_clone_search.py')),
         '--parent',*parents,'--work',str(a.work),'--output',str(a.output),
         '--workers',str(a.workers),'--rounds','4','--tag-input','--policies','scarce','late']
print(json.dumps(dict(status='queued alternative capacity-allocation policies starting',
                      parents=len(parents),workers=a.workers)),flush=True)
subprocess.run(command,check=True)
