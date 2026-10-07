"""Compact observed resources and stage times, retaining CPU steal without adjustment."""
import json,csv,statistics,collections
from common import *
def dist(v):return {'min':min(v),'median':statistics.median(v),'max':max(v)} if v else None
if __name__=='__main__':
 no_gpu();rows=load(C/'results/live-attempts.json');out=[]
 for r in rows:
  if not r['valid']:continue
  samples=[json.loads(s) for s in (C/'raw'/r['label']/'telemetry/run.jsonl').read_text().splitlines()];sw=[s['swap_memory'] for s in samples if 'swap_memory' in s]
  r['resources']['system_CPU_pct']=dist([s['system_cpu_pct'] for s in samples]);r['resources']['host_RAM_used_GiB']=dist([s['ram_used_gib'] for s in samples]);r['resources']['swap']={'samples':len(sw),'total_bytes':max((s['total'] for s in sw),default=None),'used_peak_bytes':max((s['used'] for s in sw),default=None),'system_sin_delta_bytes':max(s['sin'] for s in sw)-min(s['sin'] for s in sw) if sw else None,'system_sout_delta_bytes':max(s['sout'] for s in sw)-min(s['sout'] for s in sw) if sw else None,'scope':'System-wide snapshots; not exclusive per-request attribution. Early development has no explicit snapshot.'}
  out.append({'label':r['label'],'task':r['task'],'arm':r['arm'],'kind':r.get('kind'),'startup_s':r.get('startup_s'),'warmup_s':r.get('warmup_s'),'shutdown_s':r.get('cleanup_s'),'prefill_s':r['prefill_s'],'decode_s':r['decode_s'],'wall_s':r['wall_s'],'resources':r['resources']})
 save(C/'results/live-attempts.json',rows);save(C/'results/resource-and-stage-summary.json',out)
 fields=['label','task','arm','kind','startup_s','warmup_s','shutdown_s','prefill_s','decode_s','wall_s','CPU_pct_median','steal_pct_median','host_peak_rss_GiB','RAM_used_peak_GiB','GPU0_vram_peak_MiB','GPU1_vram_peak_MiB','GPU0_power_peak_W','GPU1_power_peak_W','GPU0_clock_median_MHz','GPU1_clock_median_MHz','swap_total_bytes','swap_used_peak_bytes']
 with (C/'results/resources.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader()
  for x in out:
   rr=x['resources'];gp=rr['GPU'];row={k:x.get(k) for k in fields[:10]};row.update(CPU_pct_median=rr['system_CPU_pct']['median'],steal_pct_median=rr['cpu_steal_pct']['median'],host_peak_rss_GiB=rr['host_peak_rss_GiB'],RAM_used_peak_GiB=rr['host_RAM_used_GiB']['max'],GPU0_vram_peak_MiB=gp['0']['vram_mib']['max'],GPU1_vram_peak_MiB=gp['1']['vram_mib']['max'],GPU0_power_peak_W=gp['0']['power_w']['max'],GPU1_power_peak_W=gp['1']['power_w']['max'],GPU0_clock_median_MHz=gp['0']['sm_mhz']['median'],GPU1_clock_median_MHz=gp['1']['sm_mhz']['median'],swap_total_bytes=rr['swap']['total_bytes'],swap_used_peak_bytes=rr['swap']['used_peak_bytes']);w.writerow(row)
 summaries=load(C/'results/main-summary.json');references=[]
 for summary in summaries:
  if summary['arm'] not in ['REPLAY_CURRENT','ORACLE_FULL']:continue
  group=[r for r in rows if r['valid'] and r['task']==summary['task'] and r['arm']==summary['arm'] and r.get('kind') in ['main','independent']];pairs=[]
  for r in group:
   cur=next(x for x in rows if x['valid'] and x['task']==r['task'] and x.get('block')==r.get('block') and x['arm']=='REPLAY_CURRENT');full=next(x for x in rows if x['valid'] and x['task']==r['task'] and x.get('block')==r.get('block') and x['arm']=='ORACLE_FULL');saving=cur['decode_s']-full['decode_s'];pairs.append({'task':r['task'],'block':r['block'],'arm':r['arm'],'TG_pct':100*(r['tok_s']/cur['tok_s']-1),'wall_pct':100*(r['wall_s']/cur['wall_s']-1),'retention':(cur['decode_s']-r['decode_s'])/saving if saving>0 else None,'stable':saving>.01*cur['decode_s']})
  if pairs:
   summary['paired_TG_pct']=dist([x['TG_pct'] for x in pairs]);summary['paired_wall_pct']=dist([x['wall_pct'] for x in pairs]);summary['retention']=dist([x['retention'] for x in pairs if x['retention'] is not None]);references.extend(pairs)
 save(C/'results/main-summary.json',summaries);save(C/'results/reference-paired-blocks.json',references)
 print('RESOURCE_SUMMARY',len(out),flush=True)
