"""Targeted transaction/causality preflights, no inference or additional repeats."""
import numpy as np,json
from campaign import C,load,save
from data import episode
from transaction_filter import replay
def main():
 outputs=[]
 for task in ('code-1','code-2'):
  x,y,b,v,m,e,meta=episode(task);prefix=meta['prefix'];baseline=replay(prefix,e,np.ones(len(e),bool));truth=meta['diagnostic']['demand']
  assert baseline['nonlocal_entries_attributed']==truth['nonlocal'] and baseline['CPU_entries_attributed']==truth['CPU'] and baseline['mapped_entries_attributed']==truth['mapped']
  oracle=replay(prefix,e,y);assert oracle['nonlocal_entries_attributed']==baseline['nonlocal_entries_attributed'] and oracle['victim_absent_entries_retained']==baseline['victim_absent_entries_retained']
  reject=replay(prefix,e,np.zeros(len(e),bool));assert reject['staged_GB']==0 and reject['issued_copies']==0 and reject['useful_next4_benefit_retained']==0
  assert np.all(x[:,20]==0) and np.all(x[:,21]==0) and np.all(x[:,22]==1);assert np.all(x[x[:,41]==0,45:]==0),'No outcome history before first window'
  # Change future labels/uses without changing causal features: suffix labels are
  # not prediction inputs. Data construction prior-outcome features use only
  # prior completed windows; actual target/publication/uses stay label-side.
  outputs.append({'task':task,'unfiltered_exact_paths':'PASS','wrong_only_rejection_zero_residency_change':'PASS','zero_traffic_reject_all':'PASS','initial_past_outcome_features_zero':'PASS','oracle_descriptive':oracle,'reject_all_negative':reject})
 save(C/'tests/offline-preflight.json',{'state':'PASS','results':outputs});print('OFFLINE_PREFLIGHT_PASS',flush=True)
if __name__=='__main__':main()
