"""Q4 measured pinned-copy model; preserve prior staged sensitivity results."""
from campaign import C,load,save
from trace_reader import Trace
from q4_replay import Replay
import numpy as np
for profile in ['32k','128k','256k']:
    t=Trace(load(C/'traces/diagnostic'/profile/f'{profile}-run1/results.json')['trace_prefix'])
    for policy in ['current','future-feasible','future-utility-wide']:
        path=C/'analysis/references'/profile/'parallel13.2'/(policy+'.json');assert not path.exists()
        r=Replay(t,policy,13.2,parallel_copy=True).run()
        r['observed_current_pending_wait_s']=float(np.sum(t.windows['pending_end'].astype(np.int64)-t.windows['pending_begin'].astype(np.int64))/1e9)
        r['timing_model_disposition']='Calibrated from measured Q4 per-copy spans; validate current join difference, not fitted throughput'
        save(path,r);print('PARALLEL_REFERENCE',profile,policy,r['nonlocal_entries'],r['promotion_bytes'],r['modeled_pending_wait_s'],r['observed_current_pending_wait_s'],flush=True)
