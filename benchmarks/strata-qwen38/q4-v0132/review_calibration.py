"""Choose from valid warmed confirmations, retaining the unchanged-default control."""
from pathlib import Path
import json,statistics,time,copy
R=Path(__file__).resolve().parent

def review():
 p=R/'raw/calibration-selection.json';d=json.loads(p.read_text());assert d['status']=='COMPLETE'
 marker=R/'raw/calibration-confirmation-review.json'
 if marker.exists():return json.loads(marker.read_text())
 candidates=[]
 for label in [d['confirmed']['candidate'],'PLACEMENT-adaptive-v0132']:
  cfg=json.loads((R/'configs'/f'{label}.json').read_text());rows=[]
  for i in range(1,4):
   row=json.loads((R/'raw'/f'{label}-run{i}.json').read_text())
   assert row['status']=='OK' and row['generated_tokens']==256 and row['cache_reused_tokens']==0 and not row['abort']
   assert row['Strata_HEAD']=='c499bd102e7a4135c0de389dcfe38c399759ccc8' and abs(row['actual_prompt_tokens']-63400)<=8
   assert row['actual_prompt_tokens']==row['actual_prompt_tokens_tokenizer']
   rows.append(row)
  warm=json.loads((R/'raw'/f'{label}-warmup.json').read_text());assert warm['status']=='OK' and warm['generated_tokens']==256
  candidates.append({'candidate':label,'config':str(R/'configs'/f'{label}.json'),'median_TG':statistics.median(x['tg_tps'] for x in rows),'median_PP':statistics.median(x['pp_tps'] for x in rows),'runs':[str(R/'raw'/f'{label}-run{i}.json') for i in range(1,4)],'full_config':cfg})
 # Only workers/pcie/min-p are tuning variables; all remaining allocation/model paths equal.
 def stable(c):
  c=copy.deepcopy(c);a=c['args']
  for flag in ['--pool-workers','--pcie-frac','--spec-min-p']:
   if flag in a:
    j=a.index(flag);del a[j:j+2]
  for key in ['log','effective_experiment_environment']:c.pop(key,None)
  return c
 assert stable(candidates[0]['full_config'])==stable(candidates[1]['full_config']),'Confirmation vs default control has unexpected confound'
 candidates.sort(key=lambda x:(x['median_TG'],x['median_PP']),reverse=True);best=candidates[0]
 result={'status':'VERIFIED_CONFIRMED_SELECTION','created':time.time(),'rank':candidates,'winner':best['candidate'],'config':best['config'],'rule':'Warmup+3 actual64K confirmations; compare sequential tuned setting with warmed unchanged-default adaptive control. TG primary, PPsecondary. Unique unpaired prompts and normal variance reported; no automatic claim of calibrationgain.'}
 marker.write_text(json.dumps(result,indent=2));(R/'raw/calibration-selection-before-confirmation-review.json').write_text(json.dumps(d,indent=2))
 d['winner']=best['candidate'];d['config']=best['config'];d['confirmation_review']=str(marker);d['selected_confirmed_median_TG']=best['median_TG'];d['selected_confirmed_median_PP']=best['median_PP'];p.write_text(json.dumps(d,indent=2))
 s=json.loads((R/'STATUS.json').read_text());s['current_winners']['CPU_PCIe_minp']={'candidate':best['candidate'],'config':best['config'],'TG':best['median_TG'],'PP':best['median_PP'],'review':str(marker)};(R/'STATUS.json').write_text(json.dumps(s,indent=2))
 print('Reviewed calibration confirmation:',best['candidate'],'median TG',best['median_TG'],flush=True)
 return result
