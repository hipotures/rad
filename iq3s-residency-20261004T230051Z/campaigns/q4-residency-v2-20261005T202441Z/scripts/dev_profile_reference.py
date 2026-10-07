"""Development-only unchanged profile reference; never changes the runtime baseline."""
import numpy as np
from campaign import C,load,save
from trace_reader import Trace

def main():
    manifest=load(C/'datasets/manifest.json')['episodes'];freq=np.zeros((48,512),np.float64)
    for row in manifest:
        if row['role']=='development':freq+=Trace(row['prefix']).counts().sum(0)
    long=[]
    for ctx in ['32k','128k','256k']:
        long.append({'name':ctx,'role':'benchmark-transfer','prefix':load(C/'traces/diagnostic'/ctx/f'{ctx}-run1/results.json')['trace_prefix']})
    summaries=[]
    for row in manifest+long:
        t=Trace(row['prefix']);state=np.full_like(t.initial,-1)
        for l in range(t.nl):
            slots=t.initial[l,t.initial[l]>=0];ids=np.argsort(-freq[l],kind='stable')[:len(slots)]
            state[l,ids]=slots
        local=CPU=mapped=0
        for layer,entries in t.grouped():
            l=int(layer['layer']);ids=entries['expert'];bad=state[l,ids]<0
            uniq,first=np.unique(ids,return_index=True);uniq=uniq[np.argsort(first)];miss=uniq[state[l,uniq]<0]
            nm=len(miss)*72//256;pcie=miss[-nm:] if nm else [];mp=int(np.isin(ids,pcie).sum())
            mapped+=mp;CPU+=int(bad.sum())-mp;local+=int((~bad).sum())
        result={'episode':row['name'],'role':row['role'],'policy':'static-development-only',
                'all_routed_entries':len(t.entries),'local_entries':local,'CPU_entries':CPU,'mapped_entries':mapped,
                'nonlocal_entries':CPU+mapped,'promotion_bytes':0,'capacity':int((state>=0).sum()),
                'training_episodes':[r['name'] for r in manifest if r['role']=='development'],
                'limitations':['Initial placement uses development counts only; capacities/physical slots match each recorded profile',
                               'No measured TG; original control runtime profile remains unchanged',
                               'Warmup state is replaced as the defining static-profile reference; not controlled practical speed']}
        out=C/'phase-b/dev-static'/f"{row['name']}.json";assert not out.exists();save(out,result);summaries.append(result)
    save(C/'phase-b/dev-static-summary.json',summaries)
if __name__=='__main__':main()
