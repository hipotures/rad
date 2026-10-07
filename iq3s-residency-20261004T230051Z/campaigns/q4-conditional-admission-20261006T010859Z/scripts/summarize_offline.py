"""Descriptive aggregation of sealed outputs; no training or threshold changes."""
from campaign import C,load,save
import collections,csv
def main():
 h=load(C/'phase-b/holdout-decision.json');rows=[x['selected'] for x in h['episodes']]
 confusion={k:sum(x['confusion_matrix'][k] for x in rows) for k in ['TP','FP','FN','TN']}
 extra={'confusion_matrix':confusion,'precision':confusion['TP']/(confusion['TP']+confusion['FP']),'publication_count_recall':confusion['TP']/(confusion['TP']+confusion['FN']),'baseline_target_ready_publications':confusion['TP']+confusion['FN'],'lost_target_ready_publications':confusion['FN'],'rejected_before_copy':sum(x['rejected_before_copy'] for x in rows),'excluded_near_end_actions':sum(x['excluded_near_end_actions'] for x in rows),'late_retained':sum(x['late'] for x in rows),'modeled_net_gain_vs_unfiltered_ms':sum(x['modeled_net_gain_vs_unfiltered_ms'] for x in rows),'modeled_copy_queue_ms':sum(x['modeled_copy_queue_ms'] for x in rows),'cost_parameters':rows[0]['cost_parameters'],'cost_warning':'Estimated sum proxy versus H4 unfiltered; overlapping CPU/copy work is not additive measured request latency; model selection remained calibration-only.'}
 save(C/'analysis/heldout-transaction-details.json',extra)
 counts=collections.Counter();episodes=[]
 for path in sorted((C/'traces/reason-v1/32k').glob('*/events-request2.jsonl')):
  if path.parent.name=='32k-run1':continue
  ev=[__import__('json').loads(x) for x in path.read_text().splitlines()];ct=collections.Counter(e['classification'] for e in ev);counts.update(ct);episodes.append({'task':path.parent.name,'trace':str(path),'issued':len(ev),'reason_counts':dict(ct),'near_end_future_use_censored':sum(e['right_censored'] for e in ev)})
 alln=sum(counts.values());reason=[{'reason':k,'count':v,'bytes':v*3072000,'GB':v*.003072,'pct_all_issued':100*v/alln} for k,v in counts.most_common()]
 save(C/'analysis/episode-failure-reasons.json',{'episodes':episodes,'all_issued':alln,'reasons':reason,'caveat':'Entire diagnostic episodes including warm-fresh routing; near-end future reuse censored separately; not relabeling historical 4996 actions.'})
 cols=['policy','unpublished_reduction','benefit_recall','observed_use_recall','staged_GB','unpublished_GB','target_ready_publications','nonlocal_ratio','victim_ratio']
 with (C/'analysis/frozen-traffic-curve.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows({k:x.get(k) for k in cols} for x in h['frozen_precision_traffic_curve'])
 print('SEALED_OFFLINE_DETAILS',extra,flush=True)
if __name__=='__main__':main()
