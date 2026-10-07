"""One deterministic execution per explicit queue-cost reference point."""
from pathlib import Path
import json, time
from campaign import C, load, guard
from q4_replay import Replay, save
from trace_reader import Trace
def main():
    for profile in ['32k','128k','256k']:
        path=C/'traces/diagnostic'/profile/f'{profile}-run1/results.json'
        while not path.exists():guard();time.sleep(10)
        t=Trace(load(path)['trace_prefix']);assert t.validate()['state']=='PASS'
        for rate in [1.8,6.8,12.6]:
            for policy in (['static','current','future-capacity-free','future-feasible'] if rate==6.8 else ['future-feasible']):
                target=C/'analysis/references'/profile/str(rate)/(policy+'.json')
                if target.exists():continue
                result=Replay(t,policy,rate).run();save(target,result)
                print('REFERENCE',profile,rate,policy,result['nonlocal_entries'],result['promotion_bytes'],result['modeled_pending_wait_s'],flush=True)
if __name__=='__main__':main()
