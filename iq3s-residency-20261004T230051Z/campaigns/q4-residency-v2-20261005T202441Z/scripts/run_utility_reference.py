"""Additional bounded future reference, same four-window planner and traffic cap."""
from campaign import C, load
from q4_replay import Replay, save
from trace_reader import Trace
for profile in ['32k','128k','256k']:
    prefix=load(C/'traces/diagnostic'/profile/f'{profile}-run1/results.json')['trace_prefix']
    path=C/'analysis/references'/profile/'6.8/future-utility.json'
    assert not path.exists()
    result=Replay(Trace(prefix),'future-utility',6.8).run();save(path,result)
    print('UTILITY_REFERENCE',profile,result['nonlocal_entries'],result['promotion_bytes'],result['modeled_pending_wait_s'],flush=True)
