#!/usr/bin/env python3
import json,re,statistics,math,time,hashlib
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import summarize
R=Path(__file__).resolve().parent;P=R/'plots';P.mkdir(exist_ok=True)
plt.rcParams.update({'figure.figsize':(8,4.8),'axes.grid':True,'grid.alpha':.25,'font.size':10})

def finish(fig,name):
 fig.tight_layout();fig.savefig(P/(name+'.png'),dpi=160);fig.savefig(P/(name+'.svg'));plt.close(fig)
def fig():return plt.subplots()
def med(vals):return statistics.median(vals) if vals else None

def main():
 summarize.main();rows=json.loads((R/'summary.json').read_text())['rows'];measured=[x for x in rows if x['kind']=='candidate' and x['status']=='OK']
 for n,key,title,unit in [(1,'TG_tps','Decode vs actual prompt context','tokens/s'),(2,'PP_tps','Prefill vs actual prompt context','tokens/s'),(3,'TTFT_s','TTFT vs actual prompt context','s')]:
  f,a=fig()
  for label in ['FINAL-A','FINAL-B']:
   rr=[x for x in measured if x['topology']==label];targets=sorted(set(round(x['actual_prompt_tokens']/100)*100 for x in rr));ys=[med([x[key] for x in rr if abs(x['actual_prompt_tokens']-target)<9]) for target in targets]
   if targets:
    groups=[[x[key] for x in rr if abs(x['actual_prompt_tokens']-target)<9] for target in targets]
    a.errorbar([x/1000 for x in targets],ys,yerr=[[middle-min(values) for middle,values in zip(ys,groups)],[max(values)-middle for middle,values in zip(ys,groups)]],fmt='o-',capsize=3,label=label+' median / observed range')
  a.set(xlabel='Actual prompt tokens (thousands)',ylabel=unit,title=title)
  if a.lines:a.legend()
  finish(f,f'{n:02d}-context-{key}')
 f,a=fig();rr=[x for x in measured if re.fullmatch(r'T3-K\d+',x['topology'])];rr=sorted(rr,key=lambda x:int(x['layer_split_actual']));a.plot([int(x['layer_split_actual']) for x in rr],[x['TG_tps'] for x in rr],'o-',label='screen1 request')
 cc=[x for x in measured if re.fullmatch(r'T3-K\d+-confirm',x['topology'])]
 for k in sorted(set(x['layer_split_actual'] for x in cc)):
  vals=[x['TG_tps'] for x in cc if x['layer_split_actual']==k];a.errorbar(int(k),med(vals),yerr=[[med(vals)-min(vals)],[max(vals)-med(vals)]],fmt='s',color='tab:orange')
 a.set(xlabel='First GPU1 layer K',ylabel='TG tokens/s',title='Manual layer split; confirmations orange');finish(f,'04-layer-split')
 f,a=fig()
 for placement in ['stripe','layer']:
  rr=sorted([x for x in measured if x['topology'].startswith('T4-') and not x['topology'].endswith(('-confirm','-static')) and x['remote_cache_mode']==placement],key=lambda x:int(x['remote_cache_slots']))
  if rr:a.plot([int(x['remote_cache_slots']) for x in rr],[x['TG_tps'] for x in rr],'o-',label=placement)
 for row in measured:
  if row['topology'].startswith('T4-') and row['topology'].endswith('-static'):a.scatter(int(row['remote_cache_slots']),row['TG_tps'],marker='s',color='black',label='static max-capacity')
 a.set(xlabel='GPU1 remote cache slots',ylabel='TG tokens/s',title='Helper cache; one helper uses identical ownership code for both placements')
 if a.lines:a.legend()
 finish(f,'05-remote-cache')
 for index,key,title,unit in [(6,'TG_tps','MTP window cap vs decode','tokens/s'),(7,'MTP_accept','Draft acceptance vs MTP cap','%')]:
  f,a=fig();rr=[x for x in measured if x['topology'].startswith('MTP-spec') and not x['topology'].endswith('-confirm')];specs=sorted(set(int(x['spec']) for x in rr))
  a.plot(specs,[med([x[key] for x in rr if int(x['spec'])==sp]) for sp in specs],'o-',label='screen median (n=2)')
  confirms=[x for x in measured if re.fullmatch(r'MTP-spec\d+-confirm',x['topology'])]
  for j,sp in enumerate(sorted(set(int(x['spec']) for x in confirms))):
   vals=[x[key] for x in confirms if int(x['spec'])==sp];middle=med(vals)
   a.errorbar(sp,middle,yerr=[[middle-min(vals)],[max(vals)-middle]],fmt='s',color='tab:orange',label='confirmation median/range (n=3)' if j==0 else None)
  a.set(xlabel='Requested MTP spec (suffix capacity may add2)',ylabel=unit,title=title);a.legend(fontsize=8)
  if key=='MTP_accept':a.text(.5,.02,'Normal draft counters include MTP and suffix-lookup offers',ha='center',transform=a.transAxes,fontsize=8)
  finish(f,f'{index:02d}-mtp-{key}')
 f,a=fig();kvlabels=sorted(set(x['topology'] for x in measured if x['topology'].startswith('KV-')))
 for target,offset in [(127000,-.18),(259500,.18)]:
  values=[med([x['TG_tps'] for x in measured if x['topology']==label and abs(x['actual_prompt_tokens']-target)<9]) for label in kvlabels];a.bar([i+offset for i in range(len(kvlabels))],[v or 0 for v in values],width=.36,label=str(target))
 a.set_xticks(range(len(kvlabels)),kvlabels);a.set(ylabel='TG tokens/s',title='KV variants; zero bar means unavailable, not zero throughput');a.legend();finish(f,'08-kv')
 f,a=fig();rr=[x for x in measured if re.fullmatch(r'prefill-(auto|\d+)',x['topology'])];a.bar([x['topology'].replace('prefill-','') for x in rr],[x['PP_tps'] for x in rr]);a.set(xlabel='Prefill chunk',ylabel='PP tokens/s',title='Actual127K prefill candidates');finish(f,'09-prefill')
 f,a=fig();rr=[x for x in measured if x['topology']=='FINAL-A'];a.axis('off')
 if rr:
  gpu=med([x['primary_VRAM_hits_per_layer_window'] for x in rr if x['primary_VRAM_hits_per_layer_window'] is not None]);cpu=med([x['CPU_routed_entries_per_layer_window'] for x in rr if x['CPU_routed_entries_per_layer_window'] is not None]);a.axis('on');a.bar(['GPU0+GPU1 VRAM hits','CPU routed entries'],[gpu or 0,cpu or 0]);a.set(ylabel='Mean routed entries/layer/window',title='Available expert work counters (per-GPU split unavailable)');a.text(.5,.92,'PCIe counter counts distinct experts; excluded from routed-entry share',transform=a.transAxes,ha='center',fontsize=8)
 else:a.text(.5,.5,'Finalist measurements pending',ha='center')
 finish(f,'10-expert-work')
 f,a=fig();longs=[x for x in rows if x['kind']=='long_decode']
 for row in longs:
  tp=R/'telemetry'/(row['run']+'.jsonl');ss=[json.loads(line) for line in tp.read_text().splitlines()];pts=[]
  for s in ss:
   live=s.get('metrics',{}).get('live',{});n=live.get('generated');rate=live.get('tok_s')
   if n and isinstance(rate,(int,float)):pts.append((n,rate))
  if pts:
   line=a.plot([x[0] for x in pts],[x[1] for x in pts],label=row['run'].replace('LONG-FINAL-A-','')+' rolling')[0]
   means=[(s.get('metrics',{}).get('live',{}).get('generated'),s.get('metrics',{}).get('live',{}).get('tok_s_mean')) for s in ss]
   means=[(n,v) for n,v in means if n and isinstance(v,(int,float))]
   if means:a.plot([x[0] for x in means],[x[1] for x in means],'--',color=line.get_color(),alpha=.8,label=row['run'].replace('LONG-FINAL-A-','')+' cumulative')
 a.set(xlabel='Server live generated-token counter (1Hz)',ylabel='Rolling / cumulative TG tokens/s',title='Long decode rate evolution')
 if a.lines:a.legend(fontsize=7)
 finish(f,'11-long-decode')
 for name,title,field in [('12-long-hit-rate','Long decode expert hit rate','total_GPU_hits'),('16-long-acceptance','Long decode draft acceptance','MTP_accept')]:
  f,a=fig()
  if longs:
   for row in longs:
    trace_path=R/'raw'/(row['run']+'-acceptance-trace.json')
    if field=='MTP_accept' and trace_path.exists():
     trace=json.loads(trace_path.read_text());assert trace['status']=='VERIFIED_AGAINST_REQUEST_END_COUNTERS'
     points=[x for x in trace['rows'] if x['cumulative_acceptance_pct'] is not None]
     a.plot([x['generated_token_index'] for x in points],[x['cumulative_acceptance_pct'] for x in points],label=row['run'].replace('LONG-FINAL-A-',''))
     continue
    value=100*row['total_GPU_hits']/row['total_lookups'] if field=='total_GPU_hits' and row.get('total_lookups') else row.get(field)
    if value is not None:a.scatter(row['output_tokens'],value,label=row['run'].replace('LONG-FINAL-A-',''))
   note='Cumulative normal draft acceptance from upstream window trace; MTP + suffix lookup' if field=='MTP_accept' else 'Request-end aggregates only; upstream exposes no time-resolved hit counter'
   a.text(.5,.95,note,ha='center',va='top',transform=a.transAxes,fontsize=8)
   a.set(xlabel='Generated tokens (trace curve / request-end aggregate)',ylabel='%',title=title)
   if a.collections or a.lines:a.legend(fontsize=7,loc='lower right')
  else:a.axis('off');a.text(.5,.5,'Long decode pending',ha='center')
  finish(f,name)
 for index,field,title,unit in [(13,'TTFT_s','Agentic TTFT by turn','s'),(14,'PP_tps','Incremental agentic prefill by turn','new tokens/s')]:
  f,a=fig()
  for target in [63400,127000]:
   rr=[x for x in rows if x['kind']=='agentic' and x['topology']==f'AGENT-{target}'];rr.sort(key=lambda x:int(re.search(r'turn(\d+)$',x['run'])[1]))
   if rr:a.plot([int(re.search(r'turn(\d+)$',x['run'])[1]) for x in rr],[x[field] for x in rr],'o-',label=f'start{target}')
  a.set(xlabel='Turn (0 = initial read)',ylabel=unit,title=title)
  if a.lines:a.legend()
  finish(f,f'{index:02d}-agentic-{field}')
 for row in longs:
  ss=[json.loads(line) for line in (R/'telemetry'/(row['run']+'.jsonl')).read_text().splitlines()]
  ss=[sample for sample in ss if sample.get('metrics',{}).get('live',{}).get('generated')]
  if not ss:continue
  f,axes=plt.subplots(3,1,figsize=(9,8),sharex=True)
  ns=[sample['metrics']['live']['generated'] for sample in ss]
  for gpu in [0,1]:
   gs=[next((g for g in sample.get('gpus',[]) if g['index']==gpu),{}) for sample in ss]
   axes[0].plot(ns,[g.get('util_pct',math.nan) for g in gs],label=f'GPU{gpu} utilization')
   axes[1].plot(ns,[g.get('power_w',math.nan) for g in gs],label=f'GPU{gpu} power')
  axes[2].plot(ns,[sum(p['cpu_pct'] for p in sample.get('processes',[])) for sample in ss],label='process CPU (100% per thread)')
  axes[0].set(ylabel='Utilization %',title=row['run']+'; resource activity, not expert-share counters')
  axes[1].set(ylabel='Power W');axes[2].set(ylabel='CPU %',xlabel='Live generated tokens (1Hz)')
  for axis in axes:axis.legend(fontsize=8)
  finish(f,'17-resource-'+row['run'].replace('LONG-FINAL-A-',''))
 f,a=fig();rr=sorted([x for x in rows if x['kind']=='compaction'],key=lambda x:x['actual_prompt_tokens']);a.bar([str(x['actual_prompt_tokens']) for x in rr],[x['wall_s'] for x in rr]);a.set(xlabel='Actual history tokens',ylabel='Total wall s',title='Compaction of recorded coding-agent history');finish(f,'15-compaction')
 manifest={'generated_epoch_s':time.time(),'summary_sha256':hashlib.sha256((R/'summary.json').read_bytes()).hexdigest(),'rows_used':len(rows),'measured_candidate_rows':len(measured),'final_matrix_rows':sum(x['topology'] in ['FINAL-A','FINAL-B'] for x in measured),'long_decode_rows':len(longs),'agentic_rows':sum(x['kind']=='agentic' for x in rows),'compaction_rows':sum(x['kind']=='compaction' for x in rows),'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in P.glob('*') if p.suffix in ['.png','.svg']},'acceptance_trace_sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'raw').glob('LONG-FINAL-A-*-acceptance-trace.json')},'limitations':'Long acceptance curves reconstructed from upstream verify-window trace and reconciled with request-end normal MTP+suffix counters. Hit-rate available at request end only. Individual GPU expert share unavailable for split; combined routed work shown. Resource curves are not expert-share counters. Long trace logging overhead is included in timings.'}
 (P/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
