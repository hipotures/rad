#!/usr/bin/env python3
import run as r
import json,re,statistics,subprocess,math,copy
from pathlib import Path

def clone(label,source,**flags):
 cfg=json.loads((r.ROOT/'configs'/f'{source}.json').read_text());cfg['log']=str(r.ROOT/'logs'/f'{label}-engine.log')
 for key,val in flags.items():cfg['args']=r.setarg(cfg['args'],'--'+key.replace('_','-'),val)
 r.c.save(r.ROOT/'configs'/f'{label}.json',cfg);return cfg

def top(rows,n):return sorted([x for x in rows if x['status']=='OK'],key=lambda x:(x['median_tg'],x['median_pp']),reverse=True)[:n]

def main():
 results=[]
 auto=json.loads((r.ROOT/'raw/T2-auto-done.json').read_text())
 if auto['status']=='OK':
  log=(r.ROOT/'logs/T2-auto-engine.log').read_text();k=int(re.search(r'layer split auto: K=(\d+)',log)[1])
  ks=list(dict.fromkeys([k+d for d in [-8,-4,-2,0,2,4,8]]+[12,16,20,24,28,32,36]))
  for K in ks:
   if 2<=K<48:
    label=f'T3-K{K}';results.append(r.candidate(label,r.config(label,'split',K),1))
  leaders=top(results,3)
  for item in leaders:
   label=item['candidate']+'-confirm';cfg=clone(label,item['candidate']);results.append(r.candidate(label,cfg,3,True))
  r.c.save(r.ROOT/'raw/layer-sweep-selection.json',{'auto_K':k,'swept_K':ks,'top3_screen':leaders,'confirmed':top([x for x in results if 'confirm' in x['candidate']],3)})
 else:r.c.save(r.ROOT/'raw/layer-sweep-selection.json',{'status':'SKIPPED_T2_FAILED','evidence':auto})
 # GPU1 is idle at this point. A conservative max_blob bound avoids assuming quant blobs all equal.
 mem=int(subprocess.check_output(['nvidia-smi','--id=1','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())*1024**2
 layout=Path('/srv/ai/models/strata/packs/ud-q4_k_xl/native_experts.txt')
 blob=max(int(line.split()[4]) for line in layout.read_text().splitlines() if line and not line.startswith('#'))
 safe=int((mem-2*1024**3)//((blob+255)//256*256))
 assert safe>0
 slots=sorted(set([int(safe*f) for f in [.5,.75,.9,1]]))
 r.c.save(r.ROOT/'raw/remote-capacity.json',{'free_bytes_gpu1':mem,'max_blob_bytes':blob,'reserved_bytes':2*1024**3,'safe_capacity_slots':safe,'candidate_slots':slots,'note':'No CLI remote-auto exists. Conservative recommended initial size is max safe bound; all four sizes run for both supported placement values. Single helper placement algorithm is identical in source.'})
 helpers=[]
 for placement in ['stripe','layer']:
  for N in sorted(slots,reverse=True):
   label=f'T4-{placement}-{N}';cfg=r.config(label,'helper',expert_cache_device1=N,expert_cache_remote_placement=placement)
   helpers.append(r.candidate(label,cfg,1));results.append(helpers[-1])
 # Confirm top two helper settings, even if slower; expand no further if >30% behind.
 for item in top(helpers,2):
  label=item['candidate']+'-confirm';cfg=clone(label,item['candidate']);results.append(r.candidate(label,cfg,3,True))
 r.c.save(r.ROOT/'raw/topology-selection.json',{'screened_and_confirmed':results,'ranking':top(results,len(results)),'status':'TOPOLOGIES_MEASURED'})
if __name__=='__main__':main()
