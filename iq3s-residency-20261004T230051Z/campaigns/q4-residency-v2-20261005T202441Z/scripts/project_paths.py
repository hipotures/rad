"""Project native72/256 routing from preserved actions; no repeated policy run."""
from pathlib import Path
import numpy as np
from campaign import C,load,save
from trace_reader import Trace
def project(t,r):
    state=t.initial.copy();events={};cpu=mapped=local=cpu_jobs=mapped_jobs=0
    for p in r['rows']:events.setdefault(p['window']+1,[]).append(p)
    groups={i:[] for i in range(len(t.windows))}
    for layer,entries in t.grouped():groups[t.window_index[int(layer['window'])]].append((layer,entries))
    for i,w in enumerate(t.windows):
        for p in events.get(i,[]):
            state[p['layer'],p['outgoing']]=-1;state[p['layer'],p['incoming']]=p['slot']
        for layer,entries in groups[i]:
            l=int(layer['layer']);ids=entries['expert'];bad=state[l,ids]<0
            unique,first=np.unique(ids,return_index=True);unique=unique[np.argsort(first)]
            misses=unique[state[l,unique]<0];nm=len(misses)*72//256;remote=misses[-nm:] if nm else []
            ngpu=int(np.isin(ids,remote).sum());mapped+=ngpu;local+=int((~bad).sum());cpu+=int(bad.sum())-ngpu
            cpu_jobs+=len(misses)-nm;mapped_jobs+=nm
    assert local+cpu+mapped==len(t.entries)
    if r['policy']=='current':
        observed=t.validate()['path_counts'];assert cpu==observed[-1] and mapped==observed[1]+observed[2] and local==observed[0]
    return {'local_entries':local,'CPU_entries':cpu,'mapped_entries':mapped,'CPU_distinct_jobs':cpu_jobs,
            'mapped_distinct_jobs':mapped_jobs,'all_routed_entries':len(t.entries),'local_pct':100*local/len(t.entries),
            'denominator':'all routed MTP entries incl.rejected','planner':'native distinct routing order, floor(nmiss*72/256)',
            'limits':'Fixed observed trajectory. Group-level CPU/mapped cost is not a linear per-entry oracle.'}
def main():
    manifest=load(C/'datasets/manifest.json')['episodes'];prefixes={x['name']:x['prefix'] for x in manifest}
    for ctx in ['32k','128k','256k']:prefixes[ctx]=load(C/'traces/diagnostic'/ctx/f'{ctx}-run1/results.json')['trace_prefix']
    for name,prefix in prefixes.items():
        t=Trace(prefix)
        for file in sorted((C/'phase-b/replay'/name).glob('*.json')):
            if file.name.endswith('-paths.json'):continue
            output=file.with_name(file.stem+'-paths.json')
            if not output.exists():save(output,project(t,load(file)))
    print('NATIVE_PATH_PROJECTIONS_COMPLETE',flush=True)
if __name__=='__main__':main()
