"""Separate request telemetry from startup/warmup; never correct measured times."""
import numpy as np
from common import *

def span(values):
    return dict(zip(['min','median','max'],map(float,np.quantile(values,[0,.5,1])))) if values else None

if __name__ == '__main__':
    no_gpu(); result=[]
    for run in load(C / 'results/live-attempts.json'):
        phases={}
        for path in (C / 'raw' / run['label'] / 'telemetry').glob('*.jsonl'):
            rows=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            phases[path.stem]={'samples':len(rows),'CPU_pct':span([x['system_cpu_pct'] for x in rows]),'steal_pct':span([x['cpu_times_percent']['steal'] for x in rows if 'steal' in x.get('cpu_times_percent',{})]),'process_RSS_GiB':span([p['rss_gib'] for x in rows for p in x.get('processes',[])]),'available_RAM_GiB':span([x['mem_available_gib'] for x in rows]),'gpus':{str(d):{key:span([g[key] for x in rows for g in x.get('gpus',[]) if int(g['index'])==d and key in g]) for key in ['util_pct','sm_mhz','memory_mhz','power_w','vram_mib','pcie_generation','pcie_width']} for d in [0,1]}}
        result.append({'label':run['label'],'task':run['task'],'block':run['block'],'arm':run['arm'],'phases':phases,'scope':'Sampling phases separated; run includes prefill/decode/completion. No exclusive decode CPU/steal attribution or post-hoc timing correction.'})
    save(C / 'results/phase-resource-diagnostics.json',result)
    print('PHASE RESOURCES',len(result),flush=True)
