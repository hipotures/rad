"""One deterministic causal replay per episode/family; fixed shared scheduler."""
from campaign import C,load,save,guard
from trace_reader import Trace
from q4_replay import Replay
from causal_policies import Provider
FAMILIES=['ema','recency','frequency','least-stale-inspired','markov',
          'jev-linear','jev-mlp','jev-temporal-mlp','hybrid-history']
def main():
    assert (C/'phase-a/report.md').exists() and (C/'phase-b/learned/evaluation.json').exists()
    # Entire-task holdouts remain separate. Primary long workload is descriptive
    # transfer only; never used to refit the model or calibration.
    episodes=load(C/'datasets/manifest.json')['episodes']
    for ctx in ['32k','128k','256k']:
        r=load(C/'traces/diagnostic'/ctx/f'{ctx}-run1/results.json')
        episodes.append({'name':ctx,'role':'benchmark-transfer','prefix':r['trace_prefix']})
    summary=[]
    for episode in episodes:
        guard();t=Trace(episode['prefix']);root=C/'phase-b/replay'/episode['name']
        for name in ['static','current']+FAMILIES:
            path=root/(name+'.json')
            if path.exists():result=load(path)
            else:
                provider=None if name in ['static','current'] else Provider(t,name)
                result=Replay(t,name,13.2,provider,parallel_copy=True).run()
                result['episode']=episode['name'];result['role']=episode['role']
                if provider is not None:result['predictor_cost']=provider.costs()
                save(path,result)
            summary.append({k:result[k] for k in ['policy','nonlocal_entries','promotion_bytes','victim_entries','modeled_pending_wait_s','selector_wall_s']}|{'episode':episode['name'],'role':episode['role'],'path':str(path)})
            save(C/'phase-b/competition-progress.json',summary)
            print('CAUSAL',episode['name'],name,result['nonlocal_entries'],result['promotion_bytes'],flush=True)
    save(C/'phase-b/competition.json',summary)
if __name__=='__main__':main()
