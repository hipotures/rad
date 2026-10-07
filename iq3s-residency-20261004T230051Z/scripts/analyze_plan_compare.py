"""Locate earliest native activation/output/head divergence in fenced/unfenced plans."""
import argparse,json
import numpy as np
from lab import ROOT,save
from trace_reader import Trace
ap=argparse.ArgumentParser();ap.add_argument('--attempt',default='compare-v1');a=ap.parse_args()
out=ROOT/'experiments/E016-device-plan-ids'/a.attempt
if (out/'summary.json').exists():raise RuntimeError('Existing arithmetic summary')
tr={mode:Trace(out/mode/'traces/runtime-request1') for mode in ['off','on','on-ple-fence']}
results={}
for mode in ['on','on-ple-fence']:
 a,b=tr['off'],tr[mode];res={'same_initial_residency':bool(np.array_equal(a.initial,b.initial)),'same_initial_heat':bool(np.array_equal(a.initial_usage,b.initial_usage)),'all_output_ids_identical':bool(np.array_equal(a.output_ids,b.output_ids)),'final_heat_identical':bool(np.array_equal(a.final_usage,b.final_usage)),'windows':[]}
 for wa,wb in zip(a.windows,b.windows):
  na,nb=int(wa['number']),int(wb['number']);ta,tb=int(wa['T']),int(wb['T'])
  same=ta==tb and np.array_equal(wa['tokens'][:ta],wb['tokens'][:tb]);rec={'ordinal':len(res['windows']),'windows':[na,nb],'same_inputs':bool(same),'T':[ta,tb],'first_mixed_difference':None,'first_expert_sum_difference':None,'head_rows':[]}
  if not same:res['windows'].append(rec);break
  for d,lb,le in [(0,0,25),(1,25,48)]:
   pa=f'{a.prefix}-window{na}-device{d}';pb=f'{b.prefix}-window{nb}-device{d}'
   try:x=np.fromfile(pa+'-layer-vectors.bin','<f4').reshape(le-lb,2,4,2560);y=np.fromfile(pb+'-layer-vectors.bin','<f4').reshape(le-lb,2,4,2560)
   except FileNotFoundError:raise RuntimeError("Missing required capture: refuse vacuous parity")
   for l in range(le-lb):
    for category,idx in [('mixed',0),('expert_sum',1)]:
     v,z=x[l,idx,:ta],y[l,idx,:ta];assert np.isfinite(v).all() and np.isfinite(z).all()
     dif=v.view('u4')!=z.view('u4')
     if np.any(dif) and rec[f'first_{category}_difference'] is None:rec[f'first_{category}_difference']={'layer':lb+l,'different_values':int(dif.sum()),'total_values':v.size,'max_abs':float(np.abs(v-z).max()),'relative_l2':float(np.linalg.norm(v-z)/max(1e-30,np.linalg.norm(v)))}
  for row in range(ta):
   try:x=np.fromfile(f'{a.prefix}-window{na}-row{row}-logits.bin','<f4');y=np.fromfile(f'{b.prefix}-window{nb}-row{row}-logits.bin','<f4')
   except FileNotFoundError:raise RuntimeError("Missing required capture: refuse vacuous parity")
   assert np.isfinite(x).all() and np.isfinite(y).all()
   def softmax(x):x=x.astype(float);v=np.exp(x-x.max());return v/v.sum()
   p,q=softmax(x),softmax(y);m=p>0
   rec['head_rows'].append({'row':row,'bit_identical':bool(np.array_equal(x.view('u4'),y.view('u4'))),'top1':[int(x.argmax()),int(y.argmax())],'max_abs_difference':float(np.abs(x-y).max()),'KL_off_to_variant':float((p[m]*np.log(p[m]/np.maximum(q[m],np.finfo(float).tiny))).sum())})
  res['windows'].append(rec)
  if len(res['windows'])>=8:break
 results[mode]=res
save(out/'summary.json',{'state':'PASS_REPAIR' if results['on-ple-fence']['all_output_ids_identical'] and results['on-ple-fence']['final_heat_identical'] and all(not r['first_mixed_difference'] and not r['first_expert_sum_difference'] and all(h['bit_identical'] for h in r['head_rows']) for r in results['on-ple-fence']['windows']) else 'INVESTIGATE','modes':results,'limitations':'Buffered layer captures add substantial diagnosticPCIetraffic and canmaskunsafe timing. Native delayed-hostfixture is the direct dependencytest; no TGclaim.'})
for mode,r in results.items():print(mode,r['all_output_ids_identical'],r['final_heat_identical'],json.dumps(r['windows'][:2]))
