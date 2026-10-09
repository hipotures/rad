#!/usr/bin/env python3
"""Compensated lifetime aliases for the frozen paired-cube binary word.

Recipient gauges, scalar operations and target reads are preserved. A physical
slot may pass from a dead donor to a gauged recipient only after donor death,
before recipient's actual old-value read, and under exact terminal-to-gauge
containment. The recipient compensates its inherited current dirty value.
Every gauge exterior and terminal transition is removed/replaced by the paid
handoff ledger, with the reduced physical normalization recomputed.

Discovery only until independent physical reflection, local-ring compatibility
and final assembly checks. Prepared with OpenAI assistance; inherited
PR161/PR163 source and licensing attribution remains unchanged.
"""
import argparse
from bisect import bisect_left
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode=True
from bit_frame_search import load_candidate,need,sha
from verify_bit_frames import apply_plan


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--max-donor-rank',type=int,default=20);ap.add_argument('--max-pairs',type=int,default=256)
    args=ap.parse_args();need(not sys.flags.optimize,'assertions enabled')
    need(not args.output.exists(),'fresh attempt required');args.output.mkdir(parents=True)
    started=time.monotonic();w=load_candidate(args.source.resolve());plan=json.loads(args.plan.read_text());apply_plan(w,plan)
    w.exact_frames();control=w.row();C=w.C
    candidates=defaultdict(list)
    for d,f in w.endframe.items():
        if d not in w.rootroles and d not in w.source.values() and C.dimf[f]<=args.max_donor_rank:
            candidates[f].append((w.last[d],d))
    for f in candidates:candidates[f].sort()
    sparse={f:[[(j,x) for j,x in enumerate(row) if x] for row in C.B[f]] for f in candidates}
    groups=sorted(candidates,key=lambda f:(-C.dimf[f],f));used=set();pairs=[];tests=0
    def subset(f,g):
        return all(not sum(x*a[j] for j,x in row) for row in sparse[f] for a in C.A[g])
    for b in sorted(w.order,key=lambda b:(w.readtime[b],b)):
        upper=w.readtime[b];g=w.gauge[b]['frame']
        for f in groups:
            pool=candidates[f]
            if not pool or pool[0][0]>=upper:continue
            tests+=1
            if not subset(f,g):continue
            k=bisect_left(pool,(upper,-1))-1
            while k>=0 and (pool[k][1] in used or pool[k][1]==b):k-=1
            if k<0:continue
            d=pool[k][1];pairs.append([b,d]);used.add(d);break
        if len(pairs)>=args.max_pairs:break
        if (len(pairs)+tests)%100000==0:print(json.dumps(dict(stage='search',pairs=len(pairs),tests=tests,seconds=time.monotonic()-started)),flush=True)
    other=load_candidate(args.source.resolve());apply_plan(other,plan)
    # Construct the inherited alias model against its source chronology, then
    # install the changed frame plan and recheck exact handoff geometry.
    cls=type(other);word=cls(pairs);apply_plan(word,plan)
    word.exact_frames();row=word.row();formal=word.formal(2)
    (args.output/'pairs.json').write_text(json.dumps(pairs,separators=(',',':'))+'\n')
    (args.output/'profile.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
    result=dict(status='DISCOVERY',started_utc=datetime.now(timezone.utc).isoformat(),tests=tests,
                donor_frame_groups=len(groups),pairs=len(pairs),max_donor_rank=args.max_donor_rank,
                formal_F2=formal,control_profile=control,profile=row,plan_sha256=sha(args.plan),
                pair_sha256=sha(args.output/'pairs.json'),search_sha256=sha(Path(__file__)),
                wall_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Exact rational handoffs, reduced role stock and all formal F2 columns; no final supplier or kappa acceptance.')
    (args.output/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status='DISCOVERY',pairs=len(pairs),tests=tests,R=row['R'],W=row['W_per_vertex'],
                         wall_seconds=result['wall_seconds'],formal=formal)),flush=True)


if __name__=='__main__':main()
