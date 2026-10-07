from common import *
from offline_campaign import point
import statistics
no_gpu();rows=load(C/'results/offline-competition.json');old=load(P1/'results/offline-competition.json');checks=[]
for r in rows:
 if r['policy']=='current':continue
 if r['tc'] or r['post']:continue
 prev=next(x for x in old if x['task']==r['task'] and x['policy']==r['policy'] and (x['threshold']==.5 or r['policy']=='full'))
 fields=['local','cpu','mapped','copied_bytes','published','victim_absent_observations'];diff={k:[prev[k],r[k]] for k in fields if prev[k]!=r[k]};checks.append({'task':r['task'],'policy':r['policy'],'diff':diff});assert not diff,(r['task'],r['policy'],diff)
save(C/'tests/inherited-offline-parity.json',checks)
# Threshold diagnostic on calibration only, one unchanged evaluation per new setting.
sensitivity=[]
for t in [t for t in load(P0/'benchmark-manifest.json')['tasks'] if t['split']=='calibration']:
 for policy in ['native','logistic']:
  r=point(t,policy,1,0,.2);ref=next(x for x in rows if x['task']==t['task_id'] and x['policy']==policy and x['tc']==1 and x['post']==0)
  sensitivity.append({'task':t['task_id'],'policy':policy,'threshold_02':r,'same_decisions_02_05':r['decision_hash']==ref['decision_hash'],'risk_veto_05':ref['risk_veto']})
save(C/'results/threshold-sensitivity.json',sensitivity)
frontier=[]
for policy in ['native','logistic']:
 for tc,post in [(0,0),(1,0),(1,48)]:
  rs=[r for r in rows if r['policy']==policy and r['tc']==tc and r['post']==post and r['split']=='calibration'];frontier.append({'policy':policy,'tc':tc,'post':post,'nonlocal':sum(r['cpu']+r['mapped'] for r in rs),'completed_bytes':sum(r['copied_bytes'] for r in rs),'unused_bytes':sum(r['unused_bytes'] for r in rs),'victim_absence':sum(r['victim_absent_observations'] for r in rs),'risk_veto':sum(r['risk_veto'] for r in rs),'capacity_veto':sum(r['capacity_veto'] for r in rs),'cost_veto':sum(r['cost_veto'] for r in rs)})
save(C/'results/calibration-frontier.json',frontier)
selection={'policy':'logistic','history_policy':'native','threshold':.5,'post_use_events':0,'transaction_control':True,'protection_cap_per_device_class':16,'intent_expiry_after_target_invocations':48,'checkpoint_sha256':'065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':'target-use-v1','selection':'Minimal first-use control removes unused churn, preserves/improves nonlocal savings across all8 development/calibration tasks for both scorers. Post-use48 reduces copies modestly but loses many useful admissions; reject extension. History and logistic both proceed live; no learned winner forced.','threshold_mapping':'Inherited matched native heat Poisson proxy and logistic probabilities; identical common risk mapping and cost guard. Calibration .2/.5 action hashes checked, no selection on simulator wall time.','scorer_scope':'Frozen13 prefix features; no victim-future queries. Incoming full/E64 and full-current-window protection remain privileged.','cost_assumptions':{'staging_GB_s':25,'H2D_GB_s':13.2,'net_entry_gain_us':160}}
save(C/'models/selection.json',selection);ledger('Freeze common lifecycle and both scorers before main live results',selection=selection);print(json.dumps(frontier,indent=2));progress(3,'Common minimal treatment frozen; extension rejected',completed='64 development/calibration accounting rows;8 sensitivity points; inherited parity',remaining='Development OFF/ON;48 main;source block;regeneration',next_action='Counterbalanced same-binary development ablation')
