"""Bounded causal next-router quality and actual handoff duration diagnostics."""
import os
for key in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[key]='1'
import argparse, collections, json, pathlib, time
import numpy as np
from lab import save
from trace_reader import Trace

ACT=np.dtype([(x,'<u8') for x in ['window','available_ns','offset']]+[(x,'<i4') for x in ['layer','token_base','tokens','width']])
BOUND=np.dtype([(x,'<u8') for x in ['window','begin_ns','end_ns','bytes']]+[(x,'<i4') for x in ['device','stage_begin','stage_end','kind']]+[('gpu_ms','<f4'),('reserved','<i4')])
assert ACT.itemsize==40 and BOUND.itemsize==56
def dist(values):
    values=np.asarray(values,dtype=float)
    return {'n':len(values),'min':float(values.min()),'median':float(np.median(values)),'p95':float(np.percentile(values,95)),'max':float(values.max()),'sum':float(values.sum())} if len(values) else None

ap=argparse.ArgumentParser();ap.add_argument('prefix');ap.add_argument('--output',required=True);a=ap.parse_args()
prefix=str(pathlib.Path(a.prefix));t=Trace(prefix);validation=t.validate();assert validation['state']=='PASS'
act=np.fromfile(prefix+'-activations.bin',ACT);values=np.fromfile(prefix+'-activation-values.bin','<f4');bound=np.fromfile(prefix+'-boundaries.bin',BOUND)
assert len(act)>0 and np.isfinite(values).all()
base=prefix.rsplit('-request',1)[0]
geometry=[json.loads(pathlib.Path(base+f'-geometry-device{g}.json').read_text()) for g in (0,1)]
width=geometry[0]['width'];ne=geometry[0]['experts'];assert width==geometry[1]['width'] and ne==512
true={};timestamps={}
for l,e in t.grouped():
    for row in np.unique(e['token']):
        key=(int(l['window']),int(l['layer']),int(row));true[key]=e[e['token']==row];timestamps[key]=int(l['t0'])
gates={};events=[]
for p in t.promotions:
    events.append((int(p['issue']),0,p))
    if p['observed_ready']:events.append((int(p['observed_ready']),1,p))
events.sort(key=lambda x:(x[0],x[1]));state=t.initial.copy();ei=0
records=[];summaries={};capture_bytes=int(values.nbytes+act.nbytes+bound.nbytes)
for r in act:
    layer=int(r['layer']);target=layer+1;available=int(r['available_ns']);win=int(r['window']);row0=int(r['token_base']);n=int(r['tokens'])
    if target not in gates:
        raw=np.fromfile(base+f'-gate-layer{target}.bin','<u2');assert len(raw)==ne*width
        gates[target]=(raw.astype('<u4')<<16).view('<f4').reshape(ne,width)
        assert np.isfinite(gates[target]).all()
        np.zeros((1,width),np.float32)@gates[target].T
    start=int(r['offset']);x=values[start:start+n*width].reshape(n,width)
    begin=time.perf_counter_ns();scores=x@gates[target].T;score_us=(time.perf_counter_ns()-begin)/1000
    begin=time.perf_counter_ns();ids=np.argpartition(scores,-10,axis=1)[:,-10:];select_us=(time.perf_counter_ns()-begin)/1000
    while ei<len(events) and events[ei][0]<=available:
        _,kind,p=events[ei];l=int(p['layer']);state[l,int(p['outgoing']) if kind==0 else int(p['incoming'])]=-1 if kind==0 else int(p['slot']);ei+=1
    for row,pred in enumerate(ids):
        key=(win,target,row0+row);actual=true[key];bad=actual[actual['path']!=0]['expert']
        match=int(np.isin(pred,actual['expert']).sum());bad_match=int(np.isin(bad,pred).sum())
        missing=int(np.count_nonzero(state[target,pred]<0));lead_us=(timestamps[key]-available)/1000
        # This is an optimistic one-blob readiness check, not an admission policy.
        # Simultaneous predicted blobs, occupied slots and compute contention only
        # increase the cost. Current-layer host work is not considered free.
        one_blob_us=t.blob_bytes[target]/12.6e9*1e6+4.2
        capture=bound[(bound['window']==win)&(bound['kind']==5)]
        cold_capture=bool(np.any(capture['end_ns']-capture['begin_ns']>100000))
        record={'window':win,'current_layer':layer,'target_layer':target,'row':row0+row,'top10_matched':match,'true_nonlocal':len(bad),'predicted_true_nonlocal':bad_match,'predicted_current_nonresident':missing,'lead_to_true_router_host_observation_us':lead_us,'batch_score_us':score_us,'batch_top10_us':select_us,'batch_tokens':n,'optimistic_one_blob_copy_us':float(one_blob_us),'optimistic_score_plus_one_blob_ready_before_true_router':bool(score_us+select_us+one_blob_us<lead_us),'cold_graph_capture_window':cold_capture}
        records.append(record)
for target in sorted(gates):
    rows=[r for r in records if r['target_layer']==target];count=len(rows);total=sum(r['true_nonlocal'] for r in rows)
    warm=[r for r in rows if not r['cold_graph_capture_window']]
    summaries[str(target)]={'rows':count,'top10_precision_pct':100*sum(r['top10_matched'] for r in rows)/(10*count),'nonlocal_recall_pct':100*sum(r['predicted_true_nonlocal'] for r in rows)/total if total else None,'true_nonlocal_entries':total,'predicted_nonresident_entries':sum(r['predicted_current_nonresident'] for r in rows),'lead_us':dist([r['lead_to_true_router_host_observation_us'] for r in rows]),'batch_score_us':dist([r['batch_score_us'] for r in rows]),'batch_top10_us':dist([r['batch_top10_us'] for r in rows]),'optimistic_ready_fraction':sum(r['optimistic_score_plus_one_blob_ready_before_true_router'] for r in rows)/count,'warm_windows_only':{'rows':len(warm),'lead_us':dist([r['lead_to_true_router_host_observation_us'] for r in warm]),'optimistic_ready_fraction':sum(r['optimistic_score_plus_one_blob_ready_before_true_router'] for r in warm)/len(warm) if warm else None}}
timings={}
for device in (0,1):
    timings[str(device)]={}
    for kind in [0,1,2,4,5,10,11]:
        rows=bound[(bound['device']==device)&(bound['kind']==kind)]
        if kind>=10:
            assert np.isfinite(rows['gpu_ms']).all() and np.all(rows['gpu_ms']>=0)
            timings[str(device)][str(kind)]={'gpu_elapsed_us':dist(rows['gpu_ms']*1000),'copy_bytes':dist(rows['bytes'])}
        else:
            assert np.all(rows['end_ns']>=rows['begin_ns'])
            timings[str(device)][str(kind)]={'host_elapsed_us':dist((rows['end_ns']-rows['begin_ns'])/1000)}
# Sequential stage transition is a host observation between existing stage0 sync
# return and stage1 entry. It excludes most resident compute and is not equal to
# the actual two-copy CUDA duration or complete boundary critical path.
gap=[]
for win in np.unique(bound['window']):
    b=bound[bound['window']==win];left=b[(b['device']==0)&(b['kind']==2)];right=b[(b['device']==1)&(b['kind']==4)]
    if len(left)==1 and len(right)==1:gap.append((int(right[0]['begin_ns'])-int(left[0]['end_ns']))/1000)
logits=np.fromfile(prefix+'-first-logits.bin','<f4');assert len(logits)>0 and np.isfinite(logits).all()
result={'state':'PASS','prefix':prefix,'trace_validation':validation,'activation_records':len(act),'numeric_rows':len(records),'capture_bytes':capture_bytes,'geometry':geometry,'gate_memory_CPU_bytes':sum(x.nbytes for x in gates.values()),'router_quality':summaries,'boundary_timings':timings,'host_stage_transition_gap_us':dist(gap),'first_window_logits':{'count':len(logits),'all_finite':True,'top1':int(logits.argmax())},'records':records,'timing_kinds':{'0':'stage_inputs CPU bracket','1':'cudaGraphLaunch CPU bracket','2':'existing stage-tail cudaStreamSynchronize CPU bracket','4':'stage call entry marker','5':'capture/capture_commit CPU bracket','10':'actual incoming mapped activation copy GPU elapsed','11':'actual outgoing mapped activation copy GPU elapsed'},'limitations':['Diagnostic-only, not a headline speed build; first64 windows selected six next-layer pairs, no generalization guarantee.','Single-thread offline CPU numeric cost excludes feature capture, scheduling, victim selection and contention. BF16 native gate snapshot converted exactly into float32; no model mutation.','Prediction uses current-layer normalized MoE activation, not true next-layer activation. True next-router IDs are evaluation labels only.','Lead ends at host observation of the true next router, a conservative deadline for avoidance of its nonlocal execution; diagnostic copying itself can increase observed lead.','Optimistic one-blob test ignores competing predictions, slot eviction and in-flight reader hazards; passing does not prove runtime feasibility.','CUDA durations stay on one device clock. CPU completion timestamps do not identify device event start. No unrelated timers are summed into miss cost.','Host tail synchronize includes final resident compute, dense/KV/head/argmax and cannot be labeled expert miss or boundary transfer time.']}
save(a.output,result)
print(json.dumps({k:v for k,v in result.items() if k not in ['records','trace_validation']},indent=2))
