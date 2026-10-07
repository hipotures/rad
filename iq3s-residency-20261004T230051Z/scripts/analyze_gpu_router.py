"""Analyze native GPU lookahead with causal availability and actual local residency."""
import os
for k in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[k]='1'
import argparse,json,pathlib
import numpy as np
from lab import ROOT,save
from trace_reader import Trace
ap=argparse.ArgumentParser();ap.add_argument('prefix');ap.add_argument('--output',required=True);ap.add_argument('--episode',required=True);ap.add_argument('--reference',required=True);a=ap.parse_args()
prefix=str(pathlib.Path(a.prefix));t=Trace(prefix);old=Trace(a.reference)
valid=t.validate();assert valid['state']=='PASS',valid
pred=np.fromfile(prefix+'-gpu-router-predictions.bin',np.dtype([(x,'<u8') for x in ['window','available_ns','offset']]+[(x,'<i4') for x in ['current_layer','target_layer','tokens','k']]))
spans=np.fromfile(prefix+'-gpu-router-spans.bin',np.dtype([(x,'<u8') for x in ['window','observed_ns']]+[('current_layer','<i4'),('device','<i4'),('gpu_ms','<f4'),('reserved','<i4')]))
values=np.fromfile(prefix+'-gpu-router-values.bin','<i4')
assert pred.dtype.itemsize==40 and spans.dtype.itemsize==32 and len(pred)==len(spans) and len(pred)>0
assert np.isfinite(spans['gpu_ms']).all() and np.all(spans['gpu_ms']>0)
parity={'output_ids':bool(np.array_equal(t.output_ids,old.output_ids)),'window_T':bool(np.array_equal(t.windows['T'],old.windows['T'])),'window_inputs':bool(np.array_equal(t.windows['tokens'],old.windows['tokens'])),'acceptance':bool(np.array_equal(t.windows['accepted'],old.windows['accepted'])),'true_router_IDs':bool(np.array_equal(t.entries['expert'],old.entries['expert'])),'execution_paths':bool(np.array_equal(t.entries['path'],old.entries['path'])),'initial_residency':bool(np.array_equal(t.initial,old.initial)),'initial_heat':bool(np.array_equal(t.initial_usage,old.initial_usage)),'final_heat':bool(np.array_equal(t.final_usage,old.final_usage)),'final_residency':bool(np.array_equal(t.final,old.final))}
heads=None
if pathlib.Path(prefix+'-first-logits.bin').exists() and pathlib.Path(a.reference+'-first-logits.bin').exists():
 x=np.fromfile(a.reference+'-first-logits.bin','<f4');y=np.fromfile(prefix+'-first-logits.bin','<f4');assert np.isfinite(y).all() and x.shape==y.shape
 def softmax(x):x=x.astype(float);z=np.exp(x-x.max());return z/z.sum()
 p,q=softmax(x),softmax(y);m=p>0
 heads={'bit_identical':bool(np.array_equal(x.view('u4'),y.view('u4'))),'max_abs_diff':float(np.abs(x-y).max()),'top1':[int(x.argmax()),int(y.argmax())],'KL_old_to_new':float((p[m]*np.log(p[m]/np.maximum(q[m],np.finfo(float).tiny))).sum())}
truth={};observation={}
for l,e in t.grouped():
 w=int(l['window']);layer=int(l['layer'])
 for row in np.unique(e['token']):truth[w,layer,int(row)]=e[e['token']==row];observation[w,layer,int(row)]=int(l['t0'])
events=[]
for p in t.promotions:
 events.append((int(p['issue']),0,p))
 if p['observed_ready']:events.append((int(p['observed_ready']),1,p))
events.sort(key=lambda e:(e[0],e[1]));state=t.initial.copy();pos=0
spanmap={(int(s['window']),int(s['current_layer'])):float(s['gpu_ms'])*1000 for s in spans}
# For identical trajectory only, classify graph-capture windows from the preserved fresh CPU diagnostic.
cold=set();refbase=str(a.reference).rsplit('-request',1)[0]
boundfile=pathlib.Path(a.reference+'-boundaries.bin')
if boundfile.exists() and all(parity.values()):
 dt=np.dtype([(x,'<u8') for x in ['window','begin_ns','end_ns','bytes']]+[(x,'<i4') for x in ['device','stage_begin','stage_end','kind']]+[('gpu_ms','<f4'),('reserved','<i4')])
 bound=np.fromfile(boundfile,dt);cold={int(s['window']) for s in bound if int(s['kind'])==5 and int(s['end_ns'])-int(s['begin_ns'])>100000}
else:
 # Conservatively remove the first occurrence of each graph size if no matching trace is available.
 seen=set()
 for w in t.windows:
  n=int(w['T'])
  if n not in seen:cold.add(int(w['number']));seen.add(n)
actsfile=pathlib.Path(a.reference+'-activations.bin');gates={};fresh={}
if actsfile.exists() and all(parity.values()):
 dt=np.dtype([(x,'<u8') for x in ['window','available_ns','offset']]+[(x,'<i4') for x in ['layer','token_base','tokens','width']])
 acts=np.fromfile(actsfile,dt);x=np.fromfile(a.reference+'-activation-values.bin','<f4')
 for c in acts:
  at=int(c['offset']);batch=x[at:at+int(c['tokens'])*2560].reshape(int(c['tokens']),2560)
  for r,v in enumerate(batch):fresh[int(c['window']),int(c['layer']),int(c['token_base'])+r]=v
records=[]
for p in pred:
 w,current,target,n,k=[int(p[f]) for f in ['window','current_layer','target_layer','tokens','k']];available=int(p['available_ns']);at=int(p['offset'])
 while pos<len(events) and events[pos][0]<=available:
  _,kind,s=events[pos];l=int(s['layer']);state[l,int(s['outgoing'])]=-1 if kind==0 else state[l,int(s['outgoing'])]
  if kind==1:state[l,int(s['incoming'])]=int(s['slot'])
  pos+=1
 ids=values[at:at+n*k].reshape(n,k);assert np.all((ids>=0)&(ids<512))
 for row,chosen in enumerate(ids):
  actual=truth[w,target,row];bad=actual[actual['path']!=0]['expert'];missing=chosen[state[target,chosen]<0]
  lead=(observation[w,target,row]-available)/1000;cost={str(rate):float(t.blob_bytes[target]/(rate*1e9)*1e6+4.2) for rate in [12.6,1.8]}
  cpu_agreement=None
  if (w,current,row) in fresh:
   if target not in gates:
    bits=np.fromfile(refbase+f'-gate-layer{target}.bin','<u2');gates[target]=(bits.astype('<u4')<<16).view('<f4').reshape(512,2560)
   score=fresh[w,current,row]@gates[target].T;cpu=np.argpartition(score,-10)[-10:];cpu_agreement=int(np.isin(chosen,cpu).sum())
  records.append({'window':w,'current_layer':current,'target_layer':target,'row':row,'tokens':n,'available_ns':available,'target_host_ns':observation[w,target,row],'GPU_score_top10_publish_us':spanmap[w,current],'lead_from_already_computed_prediction_us':lead,'top10_matched':int(np.isin(chosen,actual['expert']).sum()),'true_nonlocal':len(bad),'predicted_true_nonlocal':int(np.isin(bad,chosen).sum()),'predicted_current_nonresident':len(missing),'false_nonresident_proposals':int(np.count_nonzero(~np.isin(missing,actual['expert']))),'optimistic_copy_us':cost,'optimistic_ready':{rate:copy<lead for rate,copy in cost.items()},'cold_window':w in cold,'CPU_fullgate_membership_agreement':cpu_agreement,'predicted_IDs':chosen.tolist()})
def dist(v):
 if not len(v):return None
 return {'n':len(v),'min':float(np.min(v)),'median':float(np.median(v)),'p95':float(np.percentile(v,95)),'max':float(np.max(v))}
def aggregate(rs):
 warm=[r for r in rs if not r['cold_window']];bad=sum(r['true_nonlocal'] for r in rs);prop=sum(r['predicted_current_nonresident'] for r in rs);wb=sum(r['true_nonlocal'] for r in warm)
 return {'rows':len(rs),'top10_precision_pct':100*sum(r['top10_matched'] for r in rs)/(10*len(rs)),'true_nonlocal_entries':bad,'nonlocal_recall_pct':100*sum(r['predicted_true_nonlocal'] for r in rs)/bad if bad else None,'nonresident_proposals':prop,'false_nonresident_proposals':sum(r['false_nonresident_proposals'] for r in rs),'warm_ready_nonlocal_recall_pct':{rate:100*sum(r['predicted_true_nonlocal'] for r in warm if r['optimistic_ready'][rate])/wb if wb else None for rate in ['12.6','1.8']},'native_GPU_score_publish_us':dist([r['GPU_score_top10_publish_us'] for r in rs]),'warm_host_lead_us':dist([r['lead_from_already_computed_prediction_us'] for r in warm]),'CPU_fullgate_top10_agreement_pct':100*sum(r['CPU_fullgate_membership_agreement'] for r in rs if r['CPU_fullgate_membership_agreement'] is not None)/(10*sum(r['CPU_fullgate_membership_agreement'] is not None for r in rs)) if any(r['CPU_fullgate_membership_agreement'] is not None for r in rs) else None}
result={'state':'PASS' if all(parity.values()) and (heads is None or heads['bit_identical']) else 'INVESTIGATE_CORRECTNESS','episode':a.episode,'prefix':prefix,'trace_validation':valid,'unchanged_math_parity':parity,'first_head':heads,'summary':aggregate(records),'by_layer':{str(l):aggregate([r for r in records if r['current_layer']==l]) for l in sorted({r['current_layer'] for r in records})},'records':records,'limitations':['GPU event cost includes nativeprojection+top10+predictionIDpublish, measured afterexistingtailSync; hostlead isbetweenCPUobservations,notGPUdeadline.','Five same-device pairs only; no cross-GPUboundary prediction.','PredictioncostalreadyspentwhenhostreadsIDs; do notchargeitagainintoreadiness.','One-blobready optimistic: excludesqueues/fullslots/victims/readerhazards. No livepromotion/TGgain demonstrated.','Extra diagnosticGPUwork/PCIetraffic excludedfromheadline speed. No overheadcertificate.']}
save(a.output,result);print(a.episode,result['state'],json.dumps(result['summary']))
