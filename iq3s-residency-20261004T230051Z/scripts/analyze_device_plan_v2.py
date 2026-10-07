"""Demand, heat and first-head validation of the safe device-plan repair."""
import json
import numpy as np
from lab import ROOT,load,save
from trace_reader import Trace
out=ROOT/'experiments/E016-device-plan-ids/diagnostic-v2'
if (out/'summary.json').exists():raise RuntimeError('Existing summary')
results={}
for p in ['32k','128k']:
 base=out/p;t=Trace(base/'traces/runtime-request2');old=Trace(ROOT/f'experiments/E015-lowrank-router/v1/{p}/traces/runtime-request2')
 valid=t.validate();assert valid['state']=='PASS',valid
 r=load(base/'raw/trace-run1.json');assert r['state']=='VALID' and r['actual_output_tokens']==4096 and r['reuse']==0
 parity={'actual_output_IDs':bool(np.array_equal(t.output_ids,old.output_ids)),'window_inputs':bool(np.array_equal(t.windows['tokens'],old.windows['tokens'])),'window_T':bool(np.array_equal(t.windows['T'],old.windows['T'])),'acceptance':bool(np.array_equal(t.windows['accepted'],old.windows['accepted'])),'router_IDs':bool(np.array_equal(t.entries['expert'],old.entries['expert'])),'paths':bool(np.array_equal(t.entries['path'],old.entries['path'])),'initial_residency':bool(np.array_equal(t.initial,old.initial)),'final_residency':bool(np.array_equal(t.final,old.final)),'initial_heat':bool(np.array_equal(t.initial_usage,old.initial_usage)),'final_heat':bool(np.array_equal(t.final_usage,old.final_usage))}
 x=np.fromfile(old.prefix+'-first-logits.bin','<f4');y=np.fromfile(t.prefix+'-first-logits.bin','<f4');assert x.shape==y.shape and len(x)>0 and np.isfinite(y).all()
 parity['first_head_bit_identical']=bool(np.array_equal(x.view('u4'),y.view('u4')))
 def softmax(x):x=x.astype(float);z=np.exp(x-x.max());return z/z.sum()
 a,b=softmax(x),softmax(y);m=a>0;head={'top1':[int(x.argmax()),int(y.argmax())],'KL_old_to_new':float((a[m]*np.log(a[m]/np.maximum(b[m],np.finfo(float).tiny))).sum()),'max_abs_difference':float(np.abs(x-y).max())}
 footer={'local':valid['path_counts'][0]==r['local_vram_entries'],'CPU':valid['path_counts'][-1]==r['cpu_fallback_entries'],'mapped':valid['path_counts'][1]+valid['path_counts'][2]==r['offloaded_entries'],'windows':valid['windows']==r['verify_windows'],'accepted':int(t.windows['accepted'].sum())==r['mtp_accepted']}
 resources=load(base/'raw/resource-check.json');slots=[resources['primary_slots'],resources['stage1_slots']]
 results[p]={'state':'PASS' if all(parity.values()) and all(footer.values()) else 'INVESTIGATE','parity':parity,'head':head,'footer':footer,'trace_validation':valid,'extra_explicit_device_bytes':[n*8+64 for n in slots],'mapped_CPU_ID_bytes':[4000,3680],'resource_check':resources}
 save(base/'analysis.json',results[p])
save(out/'summary.json',{'state':'PASS' if all(r['state']=='PASS' for r in results.values()) else 'INVESTIGATE','profiles':results,'battery':load(ROOT/'experiments/E016-device-plan-ids/v2/correctness/device-plan-ids-v2/ground-truth-checks.json'),'snapshot_repair':load(ROOT/'experiments/E016-device-plan-ids/compare-r2/summary.json')['state'],'limitations':'Fixed nativeGPU plan retains correct actual expert math. Diagnostics are not headline speed and extra driver/layout costs can affect timing.'})
print(json.dumps({p:{k:v for k,v in r.items() if k not in ['trace_validation','resource_check']} for p,r in results.items()},indent=2))
if not all(r['state']=='PASS' for r in results.values()):raise SystemExit('Do not run headlines while numerical/accounting differences unresolved')
