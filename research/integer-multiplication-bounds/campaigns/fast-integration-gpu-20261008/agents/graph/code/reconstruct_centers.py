#!/usr/bin/env python3
"""Rebuild retained stars from existing side supports, then compile anew.

Exact-support-cover idea credited to Swapnil Jain's public round6 rtgm.py
(f2176bc11248). This task-local implementation acts on the new RaD edited
DAGs, preserves every side output, gives each center a fresh terminal gate,
prunes dead old center branches and rebuilds original/positive interfaces.
No old retained-link count or fixed matrix profile is reused.
"""
import argparse
import array
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
from check_compiled_witness import read_dag
from producer_search import digest


def rewrite(row,policy,limit,target):
    h,v,n,q,args,core,cover,roots,kinds,active=read_dag(row['dag_path'])
    scalar=[0]*n
    for x in range(1,n):
        if not active[x]:continue
        if args[2*x]:
            a,b=args[2*x:2*x+2];assert not scalar[a]&scalar[b]
            scalar[x]=scalar[a]|scalar[b]
        else:scalar[x]=1<<(x-1)
    side=set();stack=[x for x,k in zip(roots,kinds)if not k]
    while stack:
        x=stack.pop()
        if x in side:continue
        side.add(x)
        if args[2*x]:stack.extend(args[2*x:2*x+2])
    supports={}
    for x in sorted(side):supports.setdefault(scalar[x],x)
    ranks=[cover[x].bit_count()-core[x].bit_count()if args[2*x]else 1 for x in range(n)]
    aa=list(args);cc=list(core);vv=list(cover);ss=list(scalar);rr=list(roots);records=[]
    def add(a,b,fresh=False):
        assert not ss[a]&ss[b]
        support=ss[a]|ss[b]
        if not fresh and support in supports:return supports[support]
        node=len(cc);aa.extend((a,b));cc.append(cc[a]&cc[b]);vv.append(vv[a]|vv[b]);ss.append(support)
        ranks.append(vv[-1].bit_count()-cc[-1].bit_count())
        if not fresh:supports[support]=node
        return node
    for j,old in enumerate(roots):
        if not kinds[j]:continue
        star=scalar[old]
        candidates=[x for x in side if scalar[x]and not scalar[x]&~star and scalar[x]!=star]
        if policy=='rank-first':candidates.sort(key=lambda x:(ranks[x],-scalar[x].bit_count(),x))
        else:candidates.sort(key=lambda x:(-scalar[x].bit_count(),ranks[x],x if policy=='largest'else-x))
        choices=[]
        for a in candidates:
            b=supports.get(star^scalar[a])
            if b is not None and b in side:
                choices.append((a,b))
                if len(choices)>=limit:break
        if not choices:
            tested=0
            for ia,a in enumerate(candidates):
                rem=star^scalar[a]
                if policy!='rank-first'and rem.bit_count()>2*scalar[a].bit_count():break
                for b in candidates[ia:]:
                    if scalar[b]&~rem:continue
                    c=supports.get(rem^scalar[b])
                    if c is not None and c in side:
                        choices.append((a,b,c))
                        if len(choices)>=limit:break
                    tested+=1
                    if tested>=200000:break
                if len(choices)>=limit or tested>=200000:break
        if not choices:
            rem=star;choice=[]
            while rem:
                a=next(x for x in candidates if not scalar[x]&~rem)
                choice.append(a);rem^=scalar[a]
            choices=[tuple(choice)]
        def cost(choice):
            # Proxy only. Complete changed frames/matching determine acceptance.
            cover_union=0;core_inter=(1<<h)-1;intermediate=[]
            for x in choice:
                cover_union|=vv[x];core_inter&=cc[x]
                intermediate.append(cover_union.bit_count()-core_inter.bit_count())
            return(len(choice),sum(intermediate),tuple(ranks[x]for x in choice),choice)
        choice=min(choices,key=cost)
        acc=choice[0]
        for index,x in enumerate(choice[1:],1):acc=add(acc,x,fresh=index==len(choice)-1)
        assert ss[acc]==star and cc[acc].bit_count()==1 and ranks[acc]==h-1
        rr[j]=acc;records.append(dict(common=(cc[acc]&-cc[acc]).bit_length()-1,old_root=old,new_root=acc,selected_support_nodes=list(choice),candidate_covers=len(choices)))
    newactive=[0]*len(cc);stack=list(rr)
    while stack:
        x=stack.pop()
        if newactive[x]:continue
        newactive[x]=1
        if aa[2*x]:stack.extend(aa[2*x:2*x+2])
    target.mkdir(parents=True,exist_ok=False);dag=target/'dag.bin'
    with dag.open('wb')as stream:
        stream.write(struct.pack('<4I',h,v,len(cc),q))
        for code,values in(('I',aa),('Q',cc),('Q',vv),('I',rr),('I',kinds),('B',newactive)):stream.write(array.array(code,values).tobytes())
    (target/'rewrite.json').write_text(json.dumps(dict(source_dag=row['dag_path'],source_dag_sha256=digest(row['dag_path']),policy=policy,limit=limit,centers=records,side_output_roots_unchanged=True,new_active_nodes=sum(newactive)),indent=2,sort_keys=True)+'\n')
    return dag,records


def evaluate(task):
    parent,work,envelope,matcher,source,policy,limit=task;at=time.monotonic()
    document=json.loads(Path(parent).read_text())
    if'rows'in document:assert len(document['rows'])==1;document=document['rows'][0]
    old=document['producer'];name=f"h{old['h']}-centers-{policy}-{limit}-"+digest(parent)[:12];target=Path(work)/'raw'/name
    try:
        dag,records=rewrite(old,policy,limit,target)
        dep=subprocess.run([str(envelope),str(dag),str(dag)+'.links'],check=True,text=True,capture_output=True)
        sys.path.insert(0,str(Path(source)/'scripts'))
        from partial_swap.positive import run
        labels=run(str(dag));witness=target/'selected-links.json'
        native=subprocess.run([str(matcher),str(dag),str(dag)+'.positive','104729','2',str(witness)],check=True,text=True,capture_output=True)
        row=json.loads(native.stdout);row.update(dag_path=str(dag),dag_sha256=digest(dag),positive_sha256=digest(str(dag)+'.positive'),witness_path=str(witness),witness_sha256=digest(witness),configuration=dict(center_reconstruction=policy,limit=limit),original_producer_path=str(parent))
        result=dict(status='changed center reconstruction; independent compiler pending',case_id=name,producer=row,selected_links=json.loads(witness.read_text()),initial_R=old['R'],role_saving=old['R']-row['R'],centers=records,seconds=time.monotonic()-at)
    except Exception as error:result=dict(status='failed',case_id=name,error=repr(error),seconds=time.monotonic()-at)
    target.mkdir(parents=True,exist_ok=True);(target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,nargs='+',required=True)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=7)
    p.add_argument('--policy',choices=['largest','rank-first','reverse'],default='largest');p.add_argument('--limit',type=int,default=64)
    a=p.parse_args();assert not a.work.exists()and not a.output.exists()
    builds=a.work/'builds';builds.mkdir(parents=True);authored=Path(__file__).parent
    envelope=builds/'envelope';matcher=builds/'matcher'
    for src,dst in((a.source/'scripts'/'partial_swap'/'match_exported_dag.cpp',envelope),(authored/'moment_match_positive.cpp',matcher)):
        subprocess.run(['c++','-O3','-std=c++17',str(src),'-o',str(dst)],check=True)
    result=dict(status='running',command=sys.argv,workers=a.workers,rows=[],started_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256=digest(__file__),credited_public_mechanism='Swapnil-jain/integer-mult-kappa f2176bc11248 rtgm.py::search_totals')
    with ProcessPoolExecutor(max_workers=a.workers)as pool:
        fs=[pool.submit(evaluate,(parent,a.work,envelope,matcher,a.source,a.policy,a.limit))for parent in a.parent]
        for f in as_completed(fs):
            row=f.result();result['rows'].append(row);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:row.get(k)for k in('case_id','status','role_saving','seconds','error')}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat());a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
