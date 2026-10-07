"""Read-only attribution audit of the already frozen holdout, never selection."""
from campaign import C,load,save
from analyze_ablations import trace
from train import predict,sigmoid
from decompose import rows
import numpy as np,os,psutil,hashlib

save(C/'logs/contiguous-audit-pid.json',{'pid':os.getpid(),'create_time':psutil.Process().create_time(),'timeout_s':120})
model=load(C/'checkpoints/conditional-logistic.json')
assert hashlib.sha256((C/'checkpoints/conditional-logistic.json').read_bytes()).hexdigest()==load(C/'phase-b/frozen-decision.json')['checkpoint_sha256']
out=[]
for task in load(C/'datasets/splits.json')['holdout']:
    print('CONTIGUOUS_AUDIT_PROGRESS',task,flush=True)
    data=np.load(C/'datasets/episodes'/task/'candidate-actions.npz');X=data['X'];p=predict(model,X);a,b=model['platt'];p=sigmoid(a+b*np.log(np.maximum(p,1e-8)/np.maximum(1-p,1e-8)))
    keep=(p>=.12)&(X[:,32]<=X[:,8]+np.log(3))&(X[:,39]>0)&(X[:,21]==0)&(X[:,22]>0)
    path=C/'traces/reason-v1/32k'/task;events=rows(str(path/'events-request2')+'.jsonl');end=max(e['window'] for e in events)-3
    selected={(e['window'],e['layer'],e['incoming']):bool(k) for e,k in zip(events,keep)}
    attribution=trace(path)['publications'];baseline=retained=victim_base=victim_retained=pubs=kept=0
    for e in attribution:
        if e['issued_window']>=end:continue
        n=e['target_entries']+e['later_entries_contiguous'];baseline+=n;victim_base+=e['victim_absent_contiguous'];pubs+=1
        if selected[e['issued_window'],e['layer'],e['incoming']]:retained+=n;victim_retained+=e['victim_absent_contiguous'];kept+=1
    out.append({'task':task,'target_ready_publications':pubs,'kept_publications':kept,'recorded_contiguous_local_entries':baseline,'kept_contiguous_local_entries':retained,'contiguous_entry_recall':retained/max(1,baseline),'victim_absent_contiguous':victim_base,'kept_victim_absent_contiguous':victim_retained})
aggregate={k:sum(r[k] for r in out) for k in ['target_ready_publications','kept_publications','recorded_contiguous_local_entries','kept_contiguous_local_entries','victim_absent_contiguous','kept_victim_absent_contiguous']};aggregate['contiguous_entry_recall']=aggregate['kept_contiguous_local_entries']/aggregate['recorded_contiguous_local_entries']
save(C/'analysis/contiguous-holdout-audit.json',{'episodes':out,'aggregate':aggregate,'no_retuning_or_new_holdout_selection':True,'limits':['Post-hoc reporting audit with the SAME frozen model/threshold; original selection documents remain immutable.','Actual observed local entries end at first native or other early touch; does not prove exclusive savings against a counterfactual policy.','Original90.16% aggregate event-use retention can include native readmission; this audit is a stricter attribution measure.','Next-four-window benefit is future demand potential, not guaranteed resident/exclusive latency benefit.']})
print('CONTIGUOUS_AUDIT_COMPLETE',aggregate,flush=True)
