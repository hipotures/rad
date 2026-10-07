"""Join scoped GPU-clock spans to actual demand; keep diagnosis separate from speed."""
import argparse,csv,pathlib
import numpy as np
from lab import ROOT,load,save
from trace_reader import Trace
SPAN=np.dtype([(x,'<u8') for x in ['window','observed_ns']]+[(x,'<i4') for x in ['device','layer','group','phase','tokens','token_base']]+[('gpu_ms','<f4'),('reserved','<i4')])
assert SPAN.itemsize==48
def dist(a):
    a=np.asarray(a,dtype=float)
    return {'n':len(a),'min':float(a.min()),'median':float(np.median(a)),'p95':float(np.percentile(a,95)),'max':float(a.max()),'sum':float(a.sum())} if len(a) else None
ap=argparse.ArgumentParser();ap.add_argument('profile',choices=['32k','128k']);ap.add_argument('--attempt',default='v1');ap.add_argument('--experiment',default='E011-miss-waits');ap.add_argument('--reference-experiment',default='E008-router-boundary');ap.add_argument('--reference-attempt',default='v2');args=ap.parse_args()
folder=ROOT/'experiments'/args.experiment/args.attempt/args.profile;prefix=folder/'traces/runtime-request2'
t=Trace(prefix);validation=t.validate();assert validation['state']=='PASS',validation
spans=np.fromfile(str(prefix)+'-miss-spans.bin',SPAN)
assert len(spans)>0 and np.isfinite(spans['gpu_ms']).all() and np.all(spans['gpu_ms']>=0)
groups={};windows={int(w['number']):w for w in t.windows}
for r,e in t.grouped():
    layer=int(r['layer'])
    if layer not in (2,24,40):continue
    base=int(e['token'].min());n=int(r['tokens']);w=int(r['window']);T=int(windows[w]['T'])
    group=0 if base==0 else 1
    assert base in (0,(T+1)//2)
    groups[(w,layer,group)]={'T':T,'tokens':n,'token_base':base,'CPU':int(np.count_nonzero(e['path']==-1)),'local':int(np.count_nonzero(e['path']==0)),'mapped':int(np.count_nonzero(e['path']==1)),'remote':int(np.count_nonzero(e['path']==2)),'entry_count':len(e),'host_dispatch_us':(int(r['t4'])-int(r['t0']))/1000}
assert len(spans)==len(groups)*4,(len(spans),len(groups))
seen=set();rows=[]
for s in spans:
    w,l,g,p=map(int,[s['window'],s['layer'],s['group'],s['phase']]);key=(w,l,g,p)
    assert key not in seen;seen.add(key)
    assert int(s['device'])==(0 if l<25 else 1)
    counts=groups[(w,l,g)];assert int(s['tokens'])==counts['tokens'] and int(s['token_base'])==counts['token_base']
    rows.append(dict(window=w,layer=l,group=g,phase=p,device=int(s['device']),gpu_us=float(s['gpu_ms'])*1000,**counts))
stats={}
for l in (2,24,40):
    stats[str(l)]={}
    for p in range(4):
        a=[r for r in rows if r['layer']==l and r['phase']==p]
        stat={'all':dist([r['gpu_us'] for r in a]),'CPU_zero':dist([r['gpu_us'] for r in a if r['CPU']==0]),'CPU_nonzero':dist([r['gpu_us'] for r in a if r['CPU']>0]),'mapped_zero':dist([r['gpu_us'] for r in a if r['mapped']==0]),'mapped_nonzero':dist([r['gpu_us'] for r in a if r['mapped']>0])}
        stat['by_T_group']={f'T{T}G{g}':{'CPU_zero':dist([r['gpu_us'] for r in a if r['T']==T and r['group']==g and r['CPU']==0]),'CPU_nonzero':dist([r['gpu_us'] for r in a if r['T']==T and r['group']==g and r['CPU']>0]),'mapped_zero':dist([r['gpu_us'] for r in a if r['T']==T and r['group']==g and r['mapped']==0]),'mapped_nonzero':dist([r['gpu_us'] for r in a if r['T']==T and r['group']==g and r['mapped']>0])} for T,g in sorted({(r['T'],r['group']) for r in a})}
        stats[str(l)][str(p)]=stat
logits=np.fromfile(str(prefix)+'-first-logits.bin','<f4');assert len(logits)>0 and np.isfinite(logits).all()
oldfolder=ROOT/'experiments'/args.reference_experiment/args.reference_attempt/args.profile;old=Trace(oldfolder/'traces/runtime-request2')
oldlogits=np.fromfile(str(oldfolder/'traces/runtime-request2')+'-first-logits.bin','<f4');assert oldlogits.shape==logits.shape
run=load(folder/'raw/trace-run1.json');oldrun=load(oldfolder/'raw/trace-run1.json');assert run['payload']['input_ids_sha256']==oldrun['payload']['input_ids_sha256']
n=min(len(t.output_ids),len(old.output_ids));bad=np.flatnonzero(t.output_ids[:n]!=old.output_ids[:n]);common=int(bad[0]) if len(bad) else n
def softmax(x):
    x=x.astype(np.float64);x-=x.max();p=np.exp(x);return p/p.sum()
p,q=softmax(oldlogits),softmax(logits);mask=p>0;kl=float((p[mask]*np.log(p[mask]/np.maximum(q[mask],np.finfo(np.float64).tiny))).sum())
result={'state':'PASS','profile':args.profile,'trace_validation':validation,'span_count':len(spans),'selected_layer_count':3,'buffer_CPU_bytes':spans.nbytes,'phase_statistics_us':stats,'phase_definitions':{'0':'GPU plan waitA plus mapped plan copy','1':'resident grouped native expert compute','2':'waitB plus staging/fetch and mapped native grouped compute','3':'CPU-completion waitM kernel only'},'same_input_comparison':{'previous':str(oldfolder),'same_input_ids':True,'common_output_prefix_tokens':common,'all_output_ids_identical':np.array_equal(t.output_ids,old.output_ids),'all_T_identical':np.array_equal(t.windows['T'],old.windows['T']),'all_accepted_identical':np.array_equal(t.windows['accepted'],old.windows['accepted']),'all_router_entries_identical':np.array_equal(t.entries,old.entries),'first_head_top1':[int(oldlogits.argmax()),int(logits.argmax())],'first_head_KL_old_to_new':kl,'first_head_max_abs_difference':float(np.max(np.abs(oldlogits-logits))),'diagnostic_TG':[oldrun['TG'],run['TG']],'diagnostic_TG_delta_pct':100*(run['TG']/oldrun['TG']-1)},'limits':['Selected3layers only; cannot multiply by48 into a measured total.','Event nodes change graph timing. Spans include event/kernel/doorbell floors; never subtract them into a negative wait.','Phase durations are ordered within a group but groups overlap other streams/CPU; no sum or unrelated medians treated as end-to-end speedup.','Same-input first-head KL is one position, not full teacher-forced parity.','One same-workload instrumentation comparison cannot prove overhead<1%; diagnostic binaries never headline.']}
save(folder/'analysis.json',result)
with (folder/'analysis-rows.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print({k:v for k,v in result.items() if k not in ['phase_statistics_us','trace_validation']},flush=True)
