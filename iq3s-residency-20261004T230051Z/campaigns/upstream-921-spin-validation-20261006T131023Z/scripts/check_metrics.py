"""Independent audit of captured clocks, guest ticks and primary paired medians."""
import json,pathlib,statistics,math
C=pathlib.Path(__file__).resolve().parents[1]
s=json.loads((C/'summary.json').read_text());checks=[]
for cell,v in s['cells'].items():
 ratios={k:[] for k in ['TG','wall','CPU','PP','TTFT']}
 for p in sorted((C/'raw'/cell).glob('*/pair.json')):
  if json.loads(p.read_text()).get('state')!='VALID':continue
  arm={a:json.loads((p.parent/a/'raw/measured.json').read_text()) for a in 'AB'}
  for a,r in arm.items():
   first,last=r['capture']['first_token'],r['capture']['end'];delta=[y-x for x,y in zip(first['system_cpu_ticks'],last['system_cpu_ticks'])]
   named=dict(zip(['user','nice','system','idle','iowait','irq','softirq','steal','guest','guest_nice'],delta))
   total=sum(named[k] for k in ['user','nice','system','idle','iowait','irq','softirq','steal'])
   active=sum(named[k] for k in ['user','nice','system','irq','softirq'])
   assert math.isclose(r['decode_cpu_pct'],100*active/total,abs_tol=1e-10)
   assert math.isclose(r['decode_cpu_steal_pct'],100*named['steal']/total,abs_tol=1e-10)
   assert math.isclose(r['wall_s'],r['ended_monotonic']-r['started_monotonic'],abs_tol=1e-9)
   assert r['actual_output_tokens']==4096 and r['finish_reason']=='length'
   assert math.isclose(r['TG'],r['capture']['native_last']['generated']*1000/r['capture']['native_last']['decode_ms'],abs_tol=0.051)
   assert math.isclose(r['PP'],r['capture']['native_last']['prompt_tokens']*1000/r['capture']['native_last']['prompt_ms'],abs_tol=0.051)
  for k,field in [('TG','TG'),('wall','wall_s'),('CPU','decode_cpu_pct'),('PP','PP'),('TTFT','TTFT_s')]:ratios[k].append(arm['B'][field]/arm['A'][field])
 for k,x in ratios.items():assert math.isclose(statistics.median(x),v['paired'][k]['median'],abs_tol=1e-12)
 checks.append({'cell':cell,'pairs':len(ratios['TG']),'captured_clocks_ticks_and_paired_medians':'PASS'})
(C/'metrics-audit.json').write_text(json.dumps({'state':'PASS','checks':checks},indent=2)+'\n');print('METRICS AUDIT PASS',checks)
