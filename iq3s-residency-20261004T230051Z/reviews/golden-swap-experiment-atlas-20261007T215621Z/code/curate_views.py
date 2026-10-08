#!/usr/bin/env python3
"""Choose informative retained trajectories without new measurements or retuning."""
import argparse,collections,gzip,json
from urllib.parse import urlencode
from common import REVIEW,load,save

def main(base):
 cat=load(REVIEW/'site/data/catalog.json');runs={r['id']:r for r in cat['runs']}
 current='golden-swap-phase2--code-archive-block1-REPLAY_CURRENT';full='golden-swap-phase2--code-archive-block1-ORACLE_FULL';p1='golden-swap-phase1--code-archive-block1-ORACLE_IN_LEARNED_VICTIM';p2='golden-swap-phase2--code-archive-block1-ORACLE_IN_LOGISTIC_TC';r=runs[current]
 s=load(REVIEW/r['summary_url'].lstrip('/'));layer=max(range(48),key=lambda l:sum(v[0] for v in s['all_layer_series'][l]));W=r['windows'];nonlocal_counts=[sum(v[w][4]+v[w][5]+v[w][6] for v in s['all_layer_series']) for w in range(W)];start=max(range(W-96),key=lambda w:sum(nonlocal_counts[w:w+96]))
 d=load(REVIEW/r['layer_url'].replace('{layer}',str(layer)).lstrip('/'));gs=[dict(zip(d['columns'],g)) for g in d['generations']];counts=collections.Counter(g['expert'] for g in gs if g['generation']>0 and g['publish_event'] is not None);reload=counts.most_common(1)[0][0]
 defaults={'run':current,'layer':layer,'time':'window','smooth':4,'counts':'perWindow','focus':1,'snapshot':1}
 specs=[
 ('archive-current-early-churn','CURRENT: first 128 verifier windows','churn',{'from':0,'to':128},'Separates admissions, evictions, copy volume and required local/CPU/mapped entries near decode startup. No universal initial mass-correction burst is assumed.'),
 ('archive-current-full-churn','CURRENT: the complete request','churn',{'from':0,'to':W},'Shows whether churn stabilizes or continues throughout all 769 observed verifier windows.'),
 ('archive-physical-slot-turnover','Actual GPU0 physical slot turnover','slots',{'gpu':0,'class':3072000,'from':0,'to':W,'limit':32},'Most frequently replaced compatible physical slots, with exact owners and victim-to-incoming transitions in hover. Selection is by observed replacements, not performance.'),
 ('archive-layer-residency','High-churn layer: residency and fallback','residency',{'gpu':0,'from':0,'to':128},f'Layer {layer} has the most published native admissions on this trajectory. Resident-bin fraction is the base; local, CPU and mapped demand remain distinct.'),
 ('archive-startup-decay','How much of the startup set survives?','startup',{'from':0,'to':W},'Separates survival of the original generation, return of the initial identity, first demand, first local service and cumulative replacement.'),
 ('archive-current-full-oracle','CURRENT vs FULL_ORACLE at heavy nonlocal demand','oracle',{'compare':full,'from':start,'to':start+96},'Same recorded tape, campaign and block. Interval chosen by CURRENT nonlocal work alone; aligned states show what future-informed placement changes. More copying can coexist with less fallback.'),
 ('phase1-expert122-no-tc','Phase 1: expert 122 repeatedly leaves before use','expert',{'run':p1,'layer':0,'expert':122,'time':'event','from':12500,'to':12750,'smooth':1},'Exact admission generations near the first intended target; short copied residents are re-evicted without local service. Expert 122 has 41 admissions over the finite tape.'),
 ('phase2-expert122-tc','Phase 2: the corresponding first-use-controlled expert','expert',{'run':p2,'layer':0,'expert':122,'time':'event','from':12500,'to':12750,'smooth':1},'Same logical expert demand and frozen logistic, but publication survives through the first required service. Campaign implementations/guards differ; this is a lifecycle illustration, not a paired timing ablation.'),
 ('archive-reloaded-expert','A native expert that is repeatedly reloaded','expert',{'expert':reload,'from':0,'to':W,'smooth':1},f'Layer {layer}, expert {reload}, selected by the maximum observed native published admission count. Full lifecycle includes resident intervals, local and fallback demand, and finite-tail censoring.'),
 ('auc-lifecycle-outcome','Where AUC meets a failed transaction lifetime','predictor',{'run':p1,'layer':0},'Places native-distribution AUC beside Phase 1/2 unused copied payload and retained paired throughput. Different denominators are explicit; common oracle incoming and lifecycle improvements are not credited to learning.'),
 ('archive-lease-evidence','Observed lifetime versus repeated useful service','lease',{'layer':layer},'Exploratory retention evidence: copied generations, readmissions and end-censored residents. No TTL policy or ground-truth lease category is asserted.'),
 ('archive-demand-evolution','Working-set demand in the high-churn layer','demand',{'from':0,'to':W,'smooth':8},'Demand heatmap separates the logical workload from residency. Binned display retains exact underlying lane entries for drill-down.')]
 rows=[]
 for name,title,view,extra,reason in specs:
  q={**defaults,'view':view,**extra};path='/?'+urlencode(q);rows.append({'name':name,'title':title,'view':view,'path':path,'url':base.rstrip('/')+path,'screenshot':'figures/curated/'+name+'.png','run_ids':[q['run']]+([q['compare']] if q.get('compare') else []),'selected_filters':q,'reason':reason,'selection':'Fixed retained archive block 1; high-churn layer and heavy CURRENT nonlocal range selected deterministically from counts, never a new timing outcome.'})
 save(REVIEW/'results/curated-views.json',rows)
 print('CURATED_VIEWS',len(rows),'layer',layer,'reload_expert',reload,'range',start,start+96,flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--base-url',default='http://192.168.100.207:8765');main(a.parse_args().base_url)
