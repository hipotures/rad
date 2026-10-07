"""Causal staging-spare scheduling projection, fixed physical bytes and current EMA.

Predictions originate at the measured origin layer. Target truth is used only
when its host plan actually begins. A staged candidate is retained when safely
published; there is no use-once restoration. This is not a measured TG model.
"""
import os
for k in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[k]='1'
import numpy as np
from campaign import C,load,save
from trace_reader import Trace
from q4_replay import Replay
from q4_features import Features
from train_q4 import Scorer
def project(path,learned=False,prediction=True):
    r=load(path);t=Trace(r['trace_prefix']);prefix=t.prefix
    cost=load(path.parent/'cost-analysis.json');signal=cost['signal_rows']
    assert t.validate()['state']=='PASS'
    base=Replay(t,'current',13.2,parallel_copy=True)
    targets=sorted(set(p['target'] for p in signal));classes=set((int(l>=t.split),int(t.blob_bytes[l])) for l in targets)
    spare={};charged=[]
    for dev,bb in sorted(classes):
        victims=[(float(t.initial_usage[l,e]),l,e,int(base.state[l,e])) for l in range(t.nl)
                 if int(l>=t.split)==dev for e in range(t.ne)
                 if base.state[l,e]>=0 and int(t.slot_bytes[dev][base.state[l,e]])==bb]
        _,l,e,slot=min(victims);base.state[l,e]=-1;spare[dev,bb]=slot
        charged.append({'device':dev,'bytes':bb,'slot':slot,'removed_layer':l,'removed_expert':e})
    predictions={};groups=[[] for _ in t.windows];f=Features(t)
    model=Scorer(C/'checkpoints/linear.npz') if learned else None
    score=t.initial_usage*.3;rows=[];jobs={};reserved=set();modeled_meta_ns=0;cpu=mapped=local=0
    staged_ready=[0,0];active={};victim_rows={};retirement_wait_ns=0
    for p in signal:predictions.setdefault((p['window'],p['source']),[]).append(p)
    for layer,entries in t.grouped():groups[t.window_index[int(layer['window'])]].append((layer,entries))
    origin=int(t.windows[0]['begin']);removed=0
    for i,w in enumerate(t.windows):
        before=int(w['begin'])-origin-removed
        if base.queue:
            end=max(base.gpu_ready);extra=max(0,end-(before+base.delay));base.delay+=extra;base.wait+=extra
            base.publish(max(end,before+base.delay));assert not base.queue
        for layer,entries in groups[i]:
            l=int(layer['layer']);dev=int(l>=t.split);bb=int(t.blob_bytes[l]);key=(dev,bb);now=int(layer['t0'])
            # A ready transaction publishes only at its target plan boundary.
            job=jobs.get(key)
            if job is not None and job['target']==l:
                demanded=set(map(int,entries['expert']))
                if job['ready_ns']>now:
                    job['classification']='late-for-original-target'
                elif job['incoming'] not in demanded:
                    job['classification']='wrong-original-target'
                elif base.state[l,job['incoming']]>=0:
                    job['classification']='superseded-resident'
                else:
                    victims=[(float(score[l,e]),e,int(base.state[l,e])) for e in range(t.ne)
                             if e not in demanded and base.state[l,e]>=0 and
                                int(t.slot_bytes[dev][base.state[l,e]])==bb]
                    if not victims:job['classification']='no-safe-victim'
                    else:
                        _,out,oldslot=min(victims);slot=spare[key]
                        assert slot>=0 and not np.any(base.state[(0 if dev==0 else t.split):(t.split if dev==0 else t.nl)]==slot)
                        base.state[l,out]=-1;base.state[l,job['incoming']]=slot;spare[key]=oldslot
                        old=active.pop((l,out),None)
                        if old is not None: old['evicted_window']=i
                        active[l,job['incoming']]=job;victim_rows[l,out]=job
                        job.update(classification='target-ready-persistent',victim=out,slot=slot,
                                   published_ns=now+50000,target_entries=int(np.sum(entries['expert']==job['incoming'])))
                        modeled_meta_ns+=50000
                reserved.discard((job['target'],job['incoming']));jobs.pop(key)
            ids=entries['expert'];bad=base.state[l,ids]<0
            for e,n in zip(*np.unique(ids,return_counts=True)):
                key_ex=(l,int(e))
                if key_ex in active:
                    row=active[key_ex]
                    if base.state[l,int(e)]<0: row['evicted_window']=i;active.pop(key_ex)
                    else:
                        row['uses']+=int(n)
                        row.setdefault('first_use_window',i)
                if key_ex in victim_rows:
                    if base.state[l,int(e)]>=0: victim_rows.pop(key_ex)
                    else: victim_rows[key_ex]['victim_entries']+=int(n)
            unique,first=np.unique(ids,return_index=True);unique=unique[np.argsort(first)]
            misses=unique[base.state[l,unique]<0];nm=len(misses)*72//256;remote=misses[-nm:] if nm else []
            ngpu=int(np.isin(ids,remote).sum());mapped+=ngpu;local+=int((~bad).sum());cpu+=int(bad.sum())-ngpu
            native_ids=np.ascontiguousarray(ids);base.lib.update_usage(base.heat[l].ctypes.data,native_ids.ctypes.data,len(ids))
            if prediction:
                for p in predictions.get((i,l),[]):
                    target=p['target'];pd=int(target>=t.split);pb=int(t.blob_bytes[target]);pk=(pd,pb)
                    if pk in jobs:continue
                    conf=np.zeros(t.ne,np.float32);np.add.at(conf,p['ids'],p['confidence'])
                    candidates=np.flatnonzero((conf>0)&(base.state[target]<0))
                    if not len(candidates):continue
                    rank=conf[candidates]*(1+.1*score[target,candidates]) if learned else conf[candidates]
                    inc=int(candidates[np.argmax(rank)])
                    # Fresh pinned staging includes CPU copy and H2D. The old
                    # measured staged-expert6.8GB/s is more conservative than
                    # direct pinned-batch13.2GB/s; buffer/event overhead charged.
                    issued=p['available_ns'];start=max(issued,staged_ready[pd]);ready=start+int(np.ceil(pb/6.8))+10000;staged_ready[pd]=ready
                    job={'window':i,'origin':l,'target':target,'incoming':inc,'issue_ns':issued,'ready_ns':ready,
                         'copy_start_ns':start,'bytes':pb,'classification':'pending','target_entries':0,'uses':0,'victim_entries':0}
                    rows.append(job);jobs[pk]=job;reserved.add((target,inc))
            else:
                # Matched reactive arm: stage a true miss after target plan;
                # it is too late for this target and waits for the next window.
                if l in targets and key not in jobs and len(misses):
                    inc=int(misses[np.argmax(score[l,misses])]);start=max(now,staged_ready[dev]);ready=start+int(np.ceil(bb/6.8))+10000;staged_ready[dev]=ready
                    job={'window':i,'origin':l,'target':l,'incoming':inc,
                        'issue_ns':now,'copy_start_ns':start,'ready_ns':ready,'bytes':bb,
                        'classification':'reactive-pending','target_entries':0,'uses':0,'victim_entries':0}
                    rows.append(job);jobs[key]=job;reserved.add((l,inc))
        counts=base.counts[i];f.observe(counts,i)
        score=model.predict(f.matrix(i)).reshape(base.state.shape) if model else base.heat*.3
        regular=(int(w['number'])+1)%4==0
        if regular:
            actions=base.selection(i)
            actions=[a for a in actions if (a[0],a[1]) not in reserved]
            issue=int(w['verify_end'])-origin-removed-(int(w['pending_end'])-int(w['pending_begin']))+base.delay
            base.issue(actions,issue,i);base.heat*=np.float32(.7);f.decay()
        if prediction:
            # A late/wrong target never blocks the next request/window. Buffers
            # retire only after copy completion in runtime; spare remains free.
            for job in jobs.values():job['classification']='pending-target-not-reached'
            retirement_wait_ns+=max(0,max(staged_ready)-int(w['verify_end']))
            jobs.clear();reserved.clear()
        removed+=int(w['pending_end'])-int(w['pending_begin'])
        for dev in [0,1]:
            slots=base.state[(0 if dev==0 else t.split):(t.split if dev==0 else t.nl)]
            used=slots[slots>=0]
            assert len(np.unique(used))==len(used)
            assert not set(map(int,used))&{slot for (d,b),slot in spare.items() if d==dev}
    ready=[x for x in rows if x['classification']=='target-ready-persistent']
    return {'source_result':str(path),'policy':'early-linear-hybrid' if learned else 'early-router',
            'prediction_enabled':prediction,'all_routed_entries':len(t.entries),'local_entries':local,
            'CPU_entries':cpu,'mapped_entries':mapped,'local_pct':100*local/len(t.entries),
            'predictive_transactions':len(rows),'target_ready':len(ready),
            'target_ready_entries':sum(x['target_entries'] for x in ready),
            'classification':{k:sum(x['classification']==k for x in rows) for k in set(x['classification'] for x in rows)},
            'staging_bytes':sum(x['bytes'] for x in rows),
            'useful_resident_entries':sum(x['uses'] for x in ready),
            'descriptive_victim_absent_entries':sum(x['victim_entries'] for x in ready),
            'modeled_retirement_wait_s':retirement_wait_ns/1e9,'charged_spares':charged,
            'original_GPU_envelope':[int(x.sum()) for x in t.slot_bytes],
            'original_capacity':int(np.count_nonzero(t.initial>=0)),
            'active_capacity_after_reserve':int(np.count_nonzero(t.initial>=0))-len(charged),
            'modeled_publication_metadata_s':modeled_meta_ns/1e9,'rows':rows,
            'limitations':['Fixed observed trajectory/timestamps, no predicted TG',
                'Stage bandwidth assumption includes CPU staging; CUDA graph/worker feasibility requires proof',
                'Target truth is consulted only at target plan time; no original-target copy issued afterward',
                'GPU residency metadata publication adds modeled50us at target; actual runtime must verify ordering',
                'Victim absent entries are descriptive, not additive or exclusive causal latency',
                'Two staged copies serialize per device; fixed observed timing ignores changed kernel contention',
                'Persistent admissions remain resident until later replacement; no swap/restore',
                'Five origins only; H8 overlapping targets can exhaust one same-class spare',
                'Reactive target publication in next window uses same charged reserve but different timing']}
def main():
    for path in sorted((C/'traces').glob('cost-h*/*/*/results.json')):
        if not (path.parent/'cost-analysis.json').exists():continue
        for learned,prediction in [(False,True),(True,True),(True,False)]:
            name=path.parents[2].name+'-'+path.parent.name
            out=C/'phase-b/early-projection'/name/f"{'linear' if learned else 'router'}-{'predictive' if prediction else 'reactive'}.json"
            if out.exists():continue
            result=project(path,learned,prediction);save(out,result)
            print('EARLY_PROJECT',name,learned,prediction,result['target_ready'],result['CPU_entries'],result['mapped_entries'],flush=True)
if __name__=='__main__':main()
