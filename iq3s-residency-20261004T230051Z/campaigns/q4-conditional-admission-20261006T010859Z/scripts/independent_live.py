"""Predeclared two whole heldout applications, only after a positive primary."""
from campaign import C,load,save,guard,Session,status
from analyze_live import parity,extent
import os,psutil,signal,json,statistics
def main():
 guard();assert load(C/'phase-c/matrix-progress.json')['completed']==18
 paired=load(C/'analysis/live-paired-ratios.json');positive=any(p['wall_ratio']['median']<=.95 and p['TG_ratio']['median']>1 for p in paired)
 decision={'primary_trigger_passed':positive,'predeclared_plan':str(C/'phase-c/independent-plan.json'),'basis':'Any context >=5% median paired request wall improvement plus TG improvement; independent tasks/threshold unchanged'};save(C/'phase-c/independent-decision.json',decision)
 if not positive:print('INDEPENDENT_NOT_TRIGGERED_NO_PRACTICAL_PRIMARY_WIN',flush=True);return
 signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt('Owned application timeout')))
 save(C/'logs/independent-driver-pid.json',{'pid':os.getpid(),'create_time':psutil.Process().create_time(),'timeout_s':2400})
 for task in ('code-4','structured-4'):
  for rep in (1,2,3):
   for variant in (('control','conditional') if rep%2 else ('conditional','control')):
    guard();path=C/'independent'/task/variant/f'rep{rep}'
    if (path/'results.json').exists():continue
    assert not path.exists(),'Preserve unfinished attempt'
    cfg=load(C/'configs'/f'{variant}-128k.json');status('INDEPENDENT_APPLICATIONS',phase='C',running={'task':task,'rep':rep,'variant':variant},next_exact_action='One heldout task fresh/warm64/max1024, no task rewriting')
    with Session(C,cfg,path,'128k',port=18144) as s:
     warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID'
     r=s.request(task,'run','application');assert r['state']=='VALID' and r['actual_engine_input_verified'] and r['actual_output_tokens']==r['actual_engine_output_ID_count']
     save(path/'results.json',{'runs':[r],'warmup':warm,'headline_fixed_length':False,'natural_EOS':'Preserved application termination; no favorable retries','source':'Whole-task holdout, never fitted/calibrated'})
    print('INDEPENDENT_DONE',task,variant,rep,r['actual_output_tokens'],r['TG'],r['wall_s'],flush=True)
 results=[]
 for task in ('code-4','structured-4'):
  pairs=[]
  for rep in (1,2,3):
   a,b=[load(C/'independent'/task/v/f'rep{rep}/results.json')['runs'][0] for v in ('control','conditional')];x,y=[load(r['actual_output_ids_path']) for r in (a,b)];pairs.append({'rep':rep,'same_input':a['actual_engine_input']==b['actual_engine_input'],'same_output':x==y,'first_divergence':next((i for i,(u,v) in enumerate(zip(x,y)) if u!=v),None),'control_output':len(x),'conditional_output':len(y),'TG_ratio':b['TG']/a['TG'],'wall_ratio':b['wall_s']/a['wall_s'],'MTP_same':all(a[k]==b[k] for k in ['mtp_proposed','mtp_accepted','verify_windows'])});assert pairs[-1]['same_input']
  cells=[]
  for variant in ('control','conditional'):
   rs=[load(C/'independent'/task/variant/f'rep{i}/results.json')['runs'][0] for i in (1,2,3)];cells.append({'variant':variant,**{k:extent([r[k] for r in rs]) for k in ['TG','PP','TTFT_s','wall_s','actual_input_tokens','actual_output_tokens','cpu_fallback_entries','nonlocal_gpu_entries','mtp_acceptance_pct']},'raw':[str(C/'independent'/task/variant/f'rep{i}/results.json') for i in (1,2,3)]})
  results.append({'task':task,'cells':cells,'pairs':pairs,'median_paired_TG_ratio':statistics.median(p['TG_ratio'] for p in pairs),'median_paired_wall_ratio':statistics.median(p['wall_ratio'] for p in pairs),'interpretation':'Application latency/free generation, separately from actual128K fixed4096primary. No quality judging.'})
 save(C/'analysis/independent-live.json',results);print('INDEPENDENT_COMPLETE',json.dumps(results),flush=True)
if __name__=='__main__':main()
