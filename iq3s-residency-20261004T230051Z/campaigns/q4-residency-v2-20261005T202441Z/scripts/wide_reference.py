"""Repair of inline Python import path, not a changed reference or inference."""
from campaign import C,load
from q4_replay import Replay,save
from trace_reader import Trace
for profile in ['32k','128k','256k']:
    t=Trace(load(C/'traces/diagnostic'/profile/f'{profile}-run1/results.json')['trace_prefix'])
    for rate in [6.8,1.8]:
        path=C/'analysis/references'/profile/str(rate)/'future-utility-wide.json'
        assert not path.exists()
        result=Replay(t,'future-utility-wide',rate).run();save(path,result)
        print('WIDE_REFERENCE',profile,rate,result['nonlocal_entries'],result['promotion_bytes'],result['modeled_pending_wait_s'],flush=True)
