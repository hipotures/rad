#!/usr/bin/env python3
"""Selective exact joint-region budgets; identical frame assignments skipped.

Keeps terminal and source frames literal, changes only bounded containing
consumer region assignments. Signed-positive baseline is a distinct frame
family. SQLite claims prevent identical assignment replays across workers;
it stores only hashes and is disposable. Role/dirty/moment evidence always
comes from an actual compiled word, never a local gate accounting proxy.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import struct
import sys,time
import joint_region_search_v3 as region
import joint_positive_search as positive
WORK=None
ORIGINAL_ASSIGN=None
POSITIVE_ASSIGN=None


def initialize(source,work):
    global WORK,ORIGINAL_ASSIGN,POSITIVE_ASSIGN
    WORK=Path(work);region.initialize(source,work);positive.WORK=WORK
    ORIGINAL_ASSIGN=region.assignments;POSITIVE_ASSIGN=positive.assign


def evaluate(config):
    at=time.monotonic();case='-'.join(str(config[k])for k in('h','kind','policy','rank_delta','sweeps','limit'))
    c=region.graph(config['h'])
    if config['kind']=='original':assigned,diagnostic=ORIGINAL_ASSIGN(c,config)
    else:assigned,diagnostic=POSITIVE_ASSIGN(c,config['h'],config)
    signature=sha256(json.dumps(sorted(assigned.items()),separators=(',',':')).encode()).hexdigest()
    with sqlite3.connect(WORK/'assignment-claims.sqlite',timeout=30)as database:
        try:database.execute('INSERT INTO claims VALUES (?,?,?)',(config['h'],signature,case));database.commit();prior=None
        except sqlite3.IntegrityError:prior=database.execute('SELECT case_id FROM claims WHERE h=? AND digest=?',(config['h'],signature)).fetchone()[0]
    if prior is not None:
        target=WORK/'raw'/case;target.mkdir(parents=True,exist_ok=False)
        row=dict(status='deduplicated identical complete frame assignment',case_id=case,configuration=config,assignment_sha256=signature,duplicate_of=prior,seconds=time.monotonic()-at)
    else:
        conf={k:v for k,v in config.items()if k!='kind'}
        if config['kind']=='original':
            region.assignments=lambda circuit,configuration:(assigned,diagnostic);row=region.evaluate(conf);region.assignments=ORIGINAL_ASSIGN
        else:
            positive.assign=lambda circuit,h,configuration:(assigned,diagnostic);row=positive.evaluate(conf);positive.assign=POSITIVE_ASSIGN
        actual=WORK/'raw'/row['case_id'];target=WORK/'raw'/case
        # The underlying producer uses an unambiguous five-field ID within
        # each frame family; family prefix keeps the cohort ledger explicit.
        row.update(case_id=case,assignment_sha256=signature,configuration=config,full_result_path=str(actual/'result.json'))
        (actual/'result.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
        target.mkdir(parents=True,exist_ok=False)
    row['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest();(target/'result.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(case_id=case,status=row['status'],R=row.get('compiled',{}).get('roles'),duplicate_of=row.get('duplicate_of'),seconds=row['seconds'])),flush=True)
    return row


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=6)
    p.add_argument('--dimensions',nargs='+',type=int,default=[23,25]);p.add_argument('--limits',nargs='+',type=int,default=[1,4,16,64,256]);p.add_argument('--policies',nargs='+',default=['rank-first','largest','sparse','late']);p.add_argument('--rank-deltas',nargs='+',type=int,default=[1,2,4]);p.add_argument('--signed-baseline',action='store_true')
    a=p.parse_args();assert not a.work.exists()and not a.output.exists();a.work.mkdir(parents=True)
    with sqlite3.connect(a.work/'assignment-claims.sqlite')as db:db.execute('CREATE TABLE claims(h INTEGER,digest TEXT,case_id TEXT,PRIMARY KEY(h,digest))')
    configs=[dict(h=h,kind='original',policy=policy,rank_delta=delta,sweeps=1,limit=limit)for limit in a.limits for h in a.dimensions for policy in a.policies for delta in a.rank_deltas]
    if a.signed_baseline:configs=[dict(h=h,kind='positive',policy='positive',rank_delta=1,sweeps=1,limit=0)for h in a.dimensions]+configs
    result=dict(status='running',command=sys.argv,source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',configurations=configs,rows=[]);pending=list(configs);active={}
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,initargs=(a.source,a.work))as pool:
        while pending or active:
            while pending and len(active)<a.workers:
                c=pending.pop(0);active[pool.submit(evaluate,c)]=c
            done,_=wait(active,return_when=FIRST_COMPLETED)
            for f in done:
                active.pop(f);row=f.result();result['rows'].append({k:v for k,v in row.items()if k!='independent'});tmp=a.output.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');tmp.replace(a.output)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat());a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
