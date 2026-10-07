"""Selected GPU phase spans and sampled native Q4 copies; no additive oracle."""
from pathlib import Path
import json, numpy as np
from campaign import C,load,save
from trace_reader import Trace
MISS=np.dtype([(x,'<u8') for x in ['window','observed_ns']]+[(x,'<i4') for x in ['device','layer','group','phase','tokens','token_base']]+[('gpu_ms','<f4'),('reserved','<i4')])
COPY=np.dtype([(x,'<u8') for x in ['window','enqueue_begin','enqueue_end','bytes']]+[(x,'<i4') for x in ['layer','in','out','slot','device','event_index']]+[('gpu_ms','<f4'),('observed_complete','<i4')])
PRED=np.dtype([(x,'<u8') for x in ['window','available','offset']]+[(x,'<i4') for x in ['layer','target','tokens','k']])
SPAN=np.dtype([(x,'<u8') for x in ['window','observed']]+[('layer','<i4'),('device','<i4'),('gpu_ms','<f4'),('target','<i4')])
assert [x.itemsize for x in [MISS,COPY,PRED,SPAN]]==[48,64,40,32]
def dist(v):
    v=np.asarray(v)
    return {'n':len(v),'min':float(v.min()),'median':float(np.median(v)),'p95':float(np.percentile(v,95)),'max':float(v.max()),'mean':float(v.mean())} if len(v) else None
def analyze(path):
    result=load(path);t=Trace(result['trace_prefix']);assert t.validate()['state']=='PASS'
    prefix=t.prefix;miss=np.fromfile(prefix+'-miss-spans.bin',MISS);copies=np.fromfile(prefix+'-copy-cost.bin',COPY)
    predictions=np.fromfile(prefix+'-gpu-router-predictions.bin',PRED);ids=np.fromfile(prefix+'-gpu-router-values.bin','<i4')
    confidence=np.fromfile(prefix+'-gpu-router-confidence.bin','<f4');spans=np.fromfile(prefix+'-gpu-router-spans.bin',SPAN)
    demands={(int(l['window']),int(l['layer'])):(l,es) for l,es in t.grouped()}
    phases={};coverage=[];nextcoverage=[];leads=[];late=0;score_rows=[];group_bases={}
    for r in miss:
        l,es=demands[int(r['window']),int(r['layer'])];es=es[(es['token']>=r['token_base'])&(es['token']<r['token_base']+r['tokens'])]
        cpu=int(np.sum(es['path']==-1));mapped=int(np.sum((es['path']==1)|(es['path']==2)))
        key=f"layer{int(r['layer'])}/phase{int(r['phase'])}/"+('cpu-positive' if cpu else 'all-local-or-mapped')
        phases.setdefault(key,[]).append(float(r['gpu_ms']))
    for r in predictions:
        key=(int(r['window']),int(r['target']));l,actual=demands[key];offset=int(r['offset']);n=int(r['tokens']*r['k'])
        predicted=ids[offset:offset+n].reshape(int(r['tokens']),int(r['k']))
        actual_group=actual.reshape(-1)
        # Predictions are recorded per verifier group; token order uses that
        # group's ordinal. Two groups concatenate in source-order per pair.
        group_key=(int(r['window']),int(r['layer']));base=group_bases.get(group_key,0)
        group_bases[group_key]=base+int(r['tokens'])
        actual_group=actual[(actual['token']>=base)&(actual['token']<base+int(r['tokens']))]
        if len(actual_group)!=n:raise ValueError('Router group/token ordinal mismatch')
        aa=actual_group['expert'].reshape(predicted.shape)
        hit=sum(len(set(a)&set(b)) for a,b in zip(predicted,aa));coverage.append((hit,n))
        lead=int(l['t0'])-int(r['available']);leads.append(lead/1e6);late+=lead<=0
        wi=t.window_index[int(r['window'])]
        if wi+1<len(t.windows):
            nxt=demands[int(t.windows[wi+1]['number']),int(r['target'])][1]['expert']
            upcoming=set(map(int,nxt));guess=set(map(int,predicted.ravel()))
            nextcoverage.append((sum(int(e) in guess for e in nxt),len(nxt)))
        score_rows.append({'window':wi,'target':int(r['target']),'source':int(r['layer']),
             'available_ns':int(r['available']),'target_dispatch_ns':int(l['t0']),
             'ids':predicted.ravel().tolist(),'confidence':confidence[offset:offset+n].tolist(),
             'same_window_membership_hits':hit,'entries':n})
    completed=copies[(copies['event_index']>=0)&(copies['observed_complete']==1)]
    copy_rows=[]
    for dev in [0,1]:
        for bb in sorted(set(map(int,copies['bytes']))):
            r=completed[(completed['device']==dev)&(completed['bytes']==bb)]
            copy_rows.append({'device':dev,'bytes':bb,'gpu_duration_ms':dist(r['gpu_ms']),
                'effective_GB_s':dist(r['bytes']/np.maximum(r['gpu_ms'],1e-9)/1e6),
                'host_enqueue_ms':dist((copies[(copies['device']==dev)&(copies['bytes']==bb)]['enqueue_end'].astype(np.int64)-copies[(copies['device']==dev)&(copies['bytes']==bb)]['enqueue_begin'].astype(np.int64))/1e6)})
    return {'result':str(path),'prefix':prefix,'Q4_routing_validation':t.validate(),'gpu_phases':{key:dist(v) for key,v in phases.items()},
            'copy_costs':copy_rows,'copy_records':len(copies),'copy_samples_complete':len(completed),
            'router_cost_gpu_ms':dist(spans['gpu_ms']),'prediction_records':len(predictions),
            'same_window_membership_pct':100*sum(x for x,n in coverage)/sum(n for x,n in coverage),
            'next_window_covered_target_demand_pct':100*sum(x for x,n in nextcoverage)/sum(n for x,n in nextcoverage),
            'covered_target_layers':sorted(set(int(p['target']) for p in predictions)),
            'causal_host_lead_ms':dist(leads),'host_late_for_original_target_records':late,'signal_rows':score_rows,
            'limitations':['Five origins/targets out of48; no full-model predictor coverage claim',
                'Phase0 includes planning/wait and mapped activation copy; phase3 is exposed GPU CPU-done wait',
                'Selected-layer phase distributions cannot be multiplied by48 or added across overlap',
                'GPU copy events every32nd copy, capped256/device; later copies may not be sampled',
                'Completion checked after decode; only durations, not absolute GPU completion timestamps',
                'Router signal for current target may precede demand, while actual adaptive issue happens after verification']}
def main():
    rows=[]
    for path in sorted((C/'traces').glob('cost-h*/*/*/results.json')):
        out=path.parent/'cost-analysis.json'
        if out.exists():rows.append(load(out));continue
        result=analyze(path);save(out,result);rows.append(result)
        print('COSTS',path.parent.name,result['copy_samples_complete'],result['same_window_membership_pct'],flush=True)
    save(C/'phase-a/cost-analysis.json',rows)
if __name__=='__main__':main()
