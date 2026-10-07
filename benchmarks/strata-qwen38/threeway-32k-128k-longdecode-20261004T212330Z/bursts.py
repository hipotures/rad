import json,datetime,statistics,math
from pathlib import Path
R=Path(__file__).resolve().parent
rows=json.loads((R/'summary.json').read_text())['runs'];out=[]
for a in rows:
 samples=[json.loads(x) for x in Path(a['telemetry_file']).read_text().splitlines()];samples=[x for x in samples if a['t_first_monotonic_s']<=x['monotonic']<=a['t_end_monotonic_s']]
 points=[]
 for before,after in zip(samples,samples[1:]):
  n0=((before.get('metrics') or {}).get('live') or {}).get('generated');n1=((after.get('metrics') or {}).get('live') or {}).get('generated')
  if n0 is not None and n1 is not None and n1>=n0:points.append({'wall_time':after['wall_time'],'rate':(n1-n0)/(after['monotonic']-before['monotonic']),'generated':n1,'cpu_pct':after['system_cpu_pct']})
 pci=[];p=R/'telemetry'/f"{a['candidate']}-pcie-dmon.log"
 if p.exists() and samples:
  lo=samples[0]['wall_time'];hi=samples[-1]['wall_time']
  for line in p.read_text().splitlines():
   q=line.split()
   if len(q)!=5 or not q[0].isdigit():continue
   try:t=datetime.datetime.strptime(q[0]+q[1],'%Y%m%d%H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp();gpu=int(q[2]);rx=float(q[3]);tx=float(q[4])
   except ValueError:continue
   if not lo<=t<=hi:continue
   match=min(points,key=lambda x:abs(x['wall_time']-t)) if points else None
   if match and abs(match['wall_time']-t)>.75:match=None
   pci.append({'time':t,'gpu':gpu,'rx_MBps':rx,'tx_MBps':tx,'nearby_output_sample':match})
 result={'raw_path':a['raw_path'],'basis':'1Hz dmon with whole-second timestamps; nearest API output-rate interval within0.75s; association only, source/direction/critical path unlabelled','samples':pci,'gpu_summaries':{}}
 for gpu in [0,1]:
  xs=[p for p in pci if p['gpu']==gpu];burst=[x for x in xs if x['rx_MBps']>=1000];paired=[x for x in xs if x['nearby_output_sample']];rates_b=[x['nearby_output_sample']['rate'] for x in paired if x['rx_MBps']>=1000];rates_o=[x['nearby_output_sample']['rate'] for x in paired if x['rx_MBps']<1000]
  corr=None
  if len(paired)>2:
   xx=[x['rx_MBps'] for x in paired];yy=[x['nearby_output_sample']['rate'] for x in paired];mx=statistics.mean(xx);my=statistics.mean(yy);den=math.sqrt(sum((x-mx)**2 for x in xx)*sum((y-my)**2 for y in yy));corr=sum((x-mx)*(y-my) for x,y in zip(xx,yy))/den if den else None
  result['gpu_summaries'][str(gpu)]={'sample_count':len(xs),'peak_rx_MBps':max((x['rx_MBps'] for x in xs),default=None),'RX_ge1000_samples':len(burst),'mean_rate_near_burst':statistics.mean(rates_b) if rates_b else None,'mean_rate_near_other':statistics.mean(rates_o) if rates_o else None,'pearson_RX_vs_output_rate':corr}
 out.append(result)
(R/'analysis/pcie-bursts.json').write_text(json.dumps(out,indent=2))
print([(Path(x['raw_path']).stem,x['gpu_summaries']) for x in out])
