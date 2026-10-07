#!/usr/bin/env python3
"""Wait for the current whole matrix candidate, then restore one clean excluded cell."""
import time,json,copy
from pathlib import Path
import bench as b,run as r
R=b.R
marker=R/'raw/H-OPT-FIXED-FINAL-TOKFIX-done.json'
while not marker.exists():time.sleep(10)
label='H-OPT-FIXED-FINAL-TOKFIX-CLEAN32'
c=json.loads((R/'configs/H-OPT-FIXED-FINAL-TOKFIX.json').read_text());c['log']=str(R/'logs'/f'{label}-engine.log');c['force_matrix_warmup_prefix']=True;c['benchmark_correction']='Exclude entire prior32K helper cell after background-analysis overlap; same official encoder, same initial capacities and exact matrix warmup'
b.save(R/'configs'/f'{label}.json',c)
b.sweep(label,c,contexts=('32K',))
b.status('All matrix requests and clean32K replacement completed',['clean32K replacement'])
(R/'measurements-complete.json').write_text(json.dumps({'status':'COMPLETE','time_UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'last_clean_cell':label,'no_background_analysis_during_this_replacement':True},indent=2)+'\n')
