"""Task/family summaries and persisted sampled ranking diagnostics; no refitting."""
import statistics
from common import *
metrics=load(C/'results/development-calibration-prediction-metrics.json')+load(C/'results/reserved-prediction-metrics.json')
families=[]
for split in sorted({r['split'] for r in metrics}):
 for family in sorted({r['family'] for r in metrics}):
  for model in ['logistic','tree']:
   for horizon in [1,4,16,64]:
    rows=[r for r in metrics if (r['split'],r['family'],r['model'],r['horizon'])==(split,family,model,horizon)]
    if rows:families.append({'split':split,'family':family,'model':model,'horizon':horizon,'tasks':[r['task'] for r in rows],'task_mean_auc':statistics.mean(r['auc'] for r in rows if r['auc'] is not None),'task_mean_brier':statistics.mean(r['brier'] for r in rows),'task_mean_constant_risk_brier':statistics.mean(r['positive_fraction']*(1-r['positive_fraction']) for r in rows),'observed_rows':sum(r['n'] for r in rows),'censored_rows':sum(r['censored'] for r in rows),'calibration_bins':'See task-level prediction-metrics JSON; bins are decision-weighted, counts are correlated candidate rows.'})
ranking=[]
for line in (C/'progress.jsonl').read_text().splitlines():
 r=__import__('json').loads(line)
 if r.get('message','').startswith('Prediction evaluation '):ranking.append({k:r[k] for k in ['task','model','sampled_selected_return_le4','uniform_return_le4','utc']})
save(C/'results/family-prediction-metrics.json',families)
save(C/'results/sampled-victim-ranking.json',{'records':ranking,'convention':'Within sampled native-resident decision sets, minimum frozen multi-horizon risk vs uniform candidate. Observed short return uses next-use labels; finite-tail missing returns excluded from neither comparison, so these are descriptive observed-return rates, not fully censored survival estimates.'})
print('Prediction summaries',len(families),'family/head groups',len(ranking),'ranking records',flush=True)
