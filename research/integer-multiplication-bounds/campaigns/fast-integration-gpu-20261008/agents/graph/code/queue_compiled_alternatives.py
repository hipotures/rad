#!/usr/bin/env python3
"""Use one transition slot for exact audits and new producer-partition tests."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--cohort',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
a=p.parse_args();own=Path(__file__).resolve().parent.parent;code=own/'code'
while True:
    try:
        cohort=json.loads(a.cohort.read_text())
        if cohort['status']=='complete':break
    except(FileNotFoundError,json.JSONDecodeError):pass
    time.sleep(2)
a.work.mkdir(parents=True,exist_ok=False)
geometry=own.parent/'geometry'
subprocess.run([sys.executable,str(code/'check_compiled_witness.py'),'--witness',
                str(geometry/'results'/'frontier-weighted-original-axis-23.json'),
                str(geometry/'results'/'frontier-weighted-original-axis-25.json'),
                '--frame-source','original-envelope','--output',str(a.work/'frontier-original-audit.json')],check=True)
small=a.work/'alternative-small.json'
subprocess.run([sys.executable,str(code/'alternative_producer_clones.py'),'--parent',
                str(own/'fixtures'/'small-cloned-axis-10.json'),'--work',str(a.work/'small'),
                '--output',str(small),'--workers','1'],check=True)
subprocess.run([sys.executable,str(code/'check_compiled_witness.py'),'--witness',str(small),
                '--output',str(a.work/'alternative-small-dirty-audit.json'),'--dirty'],check=True)
parents=[own/'results'/f'refined-frontier-{h}-{i}.json'for h in(23,25)for i in(1,2,3)]
inputs=a.work/'inputs';inputs.mkdir()
for h in(21,23,25):
    choices=sorted((r for r in cohort['rows']if r.get('producer',{}).get('h')==h),key=lambda r:r['producer']['R'])
    seen=set()
    for row in choices:
        key=row['producer']['dag_sha256']
        if key in seen:continue
        seen.add(key);path=inputs/f'hierarchy-{h}-{len(seen)}.json'
        path.write_text(json.dumps(dict(producer=row['producer']),indent=2,sort_keys=True)+'\n');parents.append(path)
        if len(seen)==4:break
subprocess.run([sys.executable,str(code/'alternative_producer_clones.py'),'--parent',*[str(p)for p in parents],
                '--work',str(a.work/'selected'),'--output',str(a.work/'alternative-selected.json'),
                '--workers','1','--limit','64','--rounds','3'],check=True)
