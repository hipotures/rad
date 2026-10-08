#!/usr/bin/env python3
"""Compact counts and actual-role ordinary-moment diagnostics for a cohort.

No exact exponent or fixed matrix-profile claim is made. Complete raw rows
stay external; their hash, command and source versions remain recoverable.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from producer_search import digest, ordinary_profile


def diagnostic(row,m,a):
    h=row['h'];hist=list(row['histogram'])
    assert sum(r*n for r,n in enumerate(hist))==h*row['R']+2*row['loss']
    hist[1]+=h;hist[h]-=h
    local=sum(n*k*t*math.expm1(a*math.log(m/t)) for r,n in enumerate(hist) if r and n
              for t,k in ordinary_profile(h,r).items() if t)
    external=row['R']*sum(t*math.expm1(a*math.log(m/t)) for t in (h,m-2*h))
    return local,external,(local+external)/row['v']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cohort',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--m',type=int,default=575);p.add_argument('--alpha',type=float,default=.0000413)
    a=p.parse_args();assert not a.output.exists()
    data=json.loads(a.cohort.read_text());groups=defaultdict(list)
    successes=[r for r in data['rows'] if r.get('producer') and r.get('status')!='failed']
    for r in successes:groups[r['producer']['h']].append(r)
    summary=dict(status='compact finite native cohort; selected compiler and complete exact assembly are separate',
        created_utc=datetime.now(timezone.utc).isoformat(),complete_raw=dict(path=str(a.cohort),
        bytes=a.cohort.stat().st_size,sha256=digest(a.cohort),recovery='deterministically regenerable from pinned source, cohort command and authored drivers; not all raw bytes are in Git'),
        command=data.get('command'),source_sha256=data.get('source_sha256'),started_utc=data.get('started_utc'),
        completed_utc=data.get('completed_utc'),cohort_status=data.get('status'),
        attempts=len(data['rows']),successful_native=len(successes),failed=len(data['rows'])-len(successes),
        unique_final_dags=len({r['producer']['dag_sha256'] for r in successes}),
        diagnostic=dict(m=a.m,alpha=a.alpha,metric='ordinary copied-local plus actual external-role excess moment divided by v',
                        scope='floating diagnostic within each dimension, includes R-dependent exterior costs; no fixed-basis widths or exponent certificate'),
        dimensions={})
    for h,rows in sorted(groups.items()):
        values=[]
        for row in rows:
            producer=row['producer']; local,external,cost=diagnostic(producer,a.m,a.alpha)
            values.append((cost,row,local,external))
        def compact(item):
            cost,row,local,external=item;p=row['producer']
            return dict(case_id=row.get('case_id'),R=p['R'],c=p['c'],matched=p['matched'],
                role_saving=row.get('role_saving'),histogram=p['histogram'],configuration=p.get('configuration'),
                dag_sha256=p['dag_sha256'],positive_sha256=p.get('positive_sha256'),
                witness_sha256=p.get('witness_sha256'),dag_path=p['dag_path'],witness_path=p['witness_path'],
                full_witness_path=row.get('full_witness_path'),local_excess=local,external_excess=external,normalized_excess=cost)
        summary['dimensions'][str(h)]=dict(attempts=len(rows),unique_final_dags=len({r['producer']['dag_sha256']for r in rows}),
            roles_min=min(r['producer']['R']for r in rows),roles_max=max(r['producer']['R']for r in rows),
            saving_counts=dict(sorted(Counter(r.get('role_saving',0)for r in rows).items())),
            best_ordinary_moment=compact(min(values,key=lambda x:x[0])),
            best_roles=compact(min(values,key=lambda x:x[1]['producer']['R'])))
    a.output.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(attempts=summary['attempts'],unique_final_dags=summary['unique_final_dags'],
          dimensions={h:(d['roles_min'],d['best_ordinary_moment']['normalized_excess'])for h,d in summary['dimensions'].items()})))


if __name__=='__main__':main()
