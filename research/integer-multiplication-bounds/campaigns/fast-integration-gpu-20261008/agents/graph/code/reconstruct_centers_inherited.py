#!/usr/bin/env python3
"""Retained-star support covers with literal inherited side frames.

The support-cover mechanism is credited to Swapnil round6 f2176bc11248.
This experiment freezes every unchanged positive side frame, restricts
cover nodes to the actual center space, and gives each new partial sum the
original terminal center's full frame. Helpers are private to a center.
Fresh matching and exact finite compiler checks remain mandatory.
"""
import argparse
import array
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
from check_compiled_witness import contained, read_dag, read_labels
from producer_search import digest


def rewrite(row, policy, limit, target):
    h,v,n,q,args,core,cover,roots,kinds,active = read_dag(row['dag_path'])
    ranks,frames = read_labels(row['dag_path']+'.positive',h,n)
    scalar = [0]*n
    for x in range(1,n):
        if not active[x]: continue
        if args[2*x]:
            a,b = args[2*x:2*x+2]
            assert not scalar[a]&scalar[b]
            scalar[x] = scalar[a]|scalar[b]
        else: scalar[x] = 1<<(x-1)
    side = set(); stack = [x for x,k in zip(roots,kinds) if not k]
    while stack:
        x = stack.pop()
        if x in side: continue
        side.add(x)
        if args[2*x]: stack.extend(args[2*x:2*x+2])
    aa=list(args); cc=list(core); vv=list(cover); ff=list(frames)
    rr=list(roots); records=[]
    for j,old in enumerate(roots):
        if not kinds[j]: continue
        star=scalar[old]; frame=frames[old]
        assert frame[0]==h-1
        eligible=[x for x in side if scalar[x] and not scalar[x]&~star
                  and scalar[x]!=star and contained(frames[x],frame)]
        if policy=='rank-first': eligible.sort(key=lambda x:(ranks[x],-scalar[x].bit_count(),x))
        else: eligible.sort(key=lambda x:(-scalar[x].bit_count(),ranks[x],x if policy=='largest' else -x))
        supports={}
        for x in eligible: supports.setdefault(scalar[x],x)
        choices=[]
        for a in eligible:
            b=supports.get(star^scalar[a])
            if b is not None:
                choices.append((a,b))
                if len(choices)>=limit: break
        if not choices:
            tested=0
            for ia,a in enumerate(eligible):
                rem=star^scalar[a]
                if policy!='rank-first' and rem.bit_count()>2*scalar[a].bit_count(): break
                for b in eligible[ia:]:
                    if scalar[b]&~rem: continue
                    c=supports.get(rem^scalar[b])
                    if c is not None:
                        choices.append((a,b,c))
                        if len(choices)>=limit: break
                    tested+=1
                    if tested>=200000: break
                if len(choices)>=limit or tested>=200000: break
        if not choices:
            rem=star; chosen=[]
            while rem:
                a=next(x for x in eligible if not scalar[x]&~rem)
                chosen.append(a); rem^=scalar[a]
            choices=[tuple(chosen)]
        choice=min(choices,key=lambda xs:(len(xs),sum(ranks[x] for x in xs),tuple(ranks[x] for x in xs),xs))
        acc=choice[0]
        for x in choice[1:]:
            node=len(cc); aa.extend((acc,x)); cc.append(cc[acc]&cc[x])
            vv.append(vv[acc]|vv[x]); ff.append(frame); acc=node
        assert cc[acc].bit_count()==1
        rr[j]=acc
        records.append(dict(common=(cc[acc]&-cc[acc]).bit_length()-1,
                            old_root=old,new_root=acc,selected_support_nodes=list(choice),
                            candidate_covers=len(choices),eligible_side_nodes=len(eligible)))
    newactive=[0]*len(cc); stack=list(rr)
    while stack:
        x=stack.pop()
        if newactive[x]: continue
        newactive[x]=1
        if aa[2*x]: stack.extend(aa[2*x:2*x+2])
    for x in range(1,len(cc)):
        if newactive[x] and aa[2*x]:
            assert all(contained(ff[y],ff[x]) for y in aa[2*x:2*x+2])
    target.mkdir(parents=True,exist_ok=False); dag=target/'dag.bin'
    with dag.open('wb') as stream:
        stream.write(struct.pack('<4I',h,v,len(cc),q))
        for code,values in (('I',aa),('Q',cc),('Q',vv),('I',rr),('I',kinds),('B',newactive)):
            stream.write(array.array(code,values).tobytes())
    nnew=len(cc); rnew=[0]*nnew; forced=[0]*nnew; symbols=[0]*(nnew*h)
    for x in range(1,nnew):
        if newactive[x]:
            rnew[x],forced[x],fs=ff[x]; symbols[x*h:(x+1)*h]=fs
    with Path(str(dag)+'.positive').open('wb') as stream:
        stream.write(struct.pack('<2I',h,nnew))
        for code,values in (('I',rnew),('Q',forced),('b',symbols)):
            stream.write(array.array(code,values).tobytes())
    (target/'rewrite.json').write_text(json.dumps(dict(source_dag=row['dag_path'],
        source_dag_sha256=digest(row['dag_path']),source_positive_sha256=digest(row['dag_path']+'.positive'),
        policy=policy,limit=limit,centers=records,side_output_roots_unchanged=True,
        frame_policy='unchanged side frames; private new helper inherits terminal center frame',
        new_active_nodes=sum(newactive)),indent=2,sort_keys=True)+'\n')
    return dag,records


def evaluate(task):
    parent,work,matcher,policy,limit=task; at=time.monotonic()
    document=json.loads(Path(parent).read_text())
    if 'rows' in document:
        assert len(document['rows'])==1; document=document['rows'][0]
    old=document['producer']; name=f"h{old['h']}-inherited-centers-{policy}-{limit}-"+digest(parent)[:12]
    target=Path(work)/'raw'/name
    try:
        dag,records=rewrite(old,policy,limit,target); witness=target/'selected-links.json'
        native=subprocess.run([str(matcher),str(dag),str(dag)+'.positive','104729','2',str(witness)],
                              check=True,text=True,capture_output=True)
        row=json.loads(native.stdout); row.update(dag_path=str(dag),dag_sha256=digest(dag),
            positive_sha256=digest(str(dag)+'.positive'),witness_path=str(witness),witness_sha256=digest(witness),
            schedule='rank-node',configuration=dict(center_reconstruction=policy,limit=limit,
            frame_policy='inherited-center'),original_producer_path=str(parent))
        result=dict(status='inherited-center native witness; independent compiler pending',case_id=name,
                    producer=row,selected_links=json.loads(witness.read_text()),initial_R=old['R'],
                    role_saving=old['R']-row['R'],centers=records,seconds=time.monotonic()-at)
    except Exception as error:
        result=dict(status='failed',case_id=name,error=repr(error),seconds=time.monotonic()-at)
    target.mkdir(parents=True,exist_ok=True)
    (target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent',type=Path,nargs='+',required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=7)
    p.add_argument('--policy',choices=['largest','rank-first','reverse'],default='largest')
    p.add_argument('--limit',type=int,default=64)
    a=p.parse_args();assert not a.work.exists() and not a.output.exists()
    builds=a.work/'builds';builds.mkdir(parents=True);matcher=builds/'matcher'
    subprocess.run(['c++','-O3','-std=c++17',str(Path(__file__).with_name('moment_match_rank_node.cpp')),
                    '-o',str(matcher)],check=True)
    result=dict(status='running',command=sys.argv,workers=a.workers,rows=[],
                started_utc=datetime.now(timezone.utc).isoformat(),source_sha256=digest(__file__),
                credited_public_mechanism='Swapnil-jain/integer-mult-kappa f2176bc11248 rtgm.py::search_totals',
                task_mechanism='freeze unchanged side frames; nested terminal-center helper frames')
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        futures=[pool.submit(evaluate,(parent,a.work,matcher,a.policy,a.limit)) for parent in a.parent]
        for future in as_completed(futures):
            row=future.result();result['rows'].append(row)
            tmp=a.output.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');tmp.replace(a.output)
            print(json.dumps({k:row.get(k) for k in ('case_id','status','role_saving','seconds','error')}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
