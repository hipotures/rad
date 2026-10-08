#!/usr/bin/env python3
"""Rank-limited retained-star chains with exact nested helper frames.

The support-cover idea is credited to Swapnil round6 f2176bc11248. New
private helper frames use their actual original E(C,M) when it contains
both literal input spaces; otherwise they retain the terminal center frame.
An optional locality order completes address cliques before adding points.
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
from check_compiled_witness import contained,read_dag,read_labels
from producer_search import digest
from reconstruct_centers_rankcap import rewrite as inherited_rewrite


def rewrite(row,policy,limit,target,ordering,max_rank):
    dag,records=inherited_rewrite(row,policy,limit,target,max_rank)
    old_h,old_v,old_n,*_=read_dag(row['dag_path'])
    h,v,n,q,args,core,cover,roots,kinds,active=read_dag(dag)
    ranks,frames=read_labels(str(dag)+'.positive',h,n)
    aa=list(args);cc=list(core);vv=list(cover);ff=list(frames);next_helper=old_n;edits=[]
    for record in records:
        terminal=record['new_root'];old=record['old_root'];frame=ff[terminal]
        choice=list(record['selected_support_nodes']);initial=list(choice)
        if ordering=='locality':
            ordered=[];covered=0;common=(1<<h)-1
            while choice:
                x=min(choice,key=lambda x:((covered|vv[x]).bit_count()-(common&cc[x]).bit_count(),
                                            ff[x][0],x))
                ordered.append(x);choice.remove(x);covered|=vv[x];common&=cc[x]
            choice=ordered
        acc=choice[0]
        for x in choice[1:]:
            node=next_helper;next_helper+=1;aa[2*node:2*node+2]=[acc,x]
            cc[node]=cc[acc]&cc[x];vv[node]=vv[acc]|vv[x]
            symbols=tuple(1 if cc[node]>>i&1 else i+2 if vv[node]>>i&1 else 0 for i in range(h))
            candidate=(vv[node].bit_count()-cc[node].bit_count(),cc[node],symbols)
            feasible=contained(ff[acc],candidate) and contained(ff[x],candidate) and contained(candidate,frame)
            if node!=terminal and feasible:ff[node]=candidate
            else:ff[node]=frame
            edits.append(dict(node=node,terminal=node==terminal,old_rank=frame[0],new_rank=ff[node][0],
                              envelope_feasible=feasible,source_children=[acc,x]))
            acc=node
        assert acc==terminal
        record['original_cover_order']=initial;record['selected_support_nodes']=choice
    assert next_helper==n
    for x in range(1,n):
        if active[x] and aa[2*x]:assert all(contained(ff[y],ff[x])for y in aa[2*x:2*x+2])
    with dag.open('wb')as stream:
        stream.write(struct.pack('<4I',h,v,n,q))
        for code,values in (('I',aa),('Q',cc),('Q',vv),('I',roots),('I',kinds),('B',active)):
            stream.write(array.array(code,values).tobytes())
    rnew=[0]*n;forced=[0]*n;symbols=[0]*(n*h)
    for x in range(1,n):
        if active[x]:rnew[x],forced[x],values=ff[x];symbols[x*h:(x+1)*h]=values
    with Path(str(dag)+'.positive').open('wb')as stream:
        stream.write(struct.pack('<2I',h,n))
        for code,values in (('I',rnew),('Q',forced),('b',symbols)):stream.write(array.array(code,values).tobytes())
    (target/'envelope-helper-rewrite.json').write_text(json.dumps(dict(ordering=ordering,centers=records,
        helper_edits=edits,unchanged_side_frames=True,frame_rule='E(C,M) if exact containment holds; terminal full frame otherwise'),
        indent=2,sort_keys=True)+'\n')
    return dag,records,edits


def evaluate(task):
    parent,work,matcher,policy,limit,ordering,max_rank=task;at=time.monotonic()
    document=json.loads(Path(parent).read_text())
    if 'rows'in document:assert len(document['rows'])==1;document=document['rows'][0]
    old=document['producer'];name=f"h{old['h']}-center-envelope-r{max_rank}-{ordering}-{policy}-{limit}-"+digest(parent)[:12]
    target=Path(work)/'raw'/name
    try:
        dag,records,edits=rewrite(old,policy,limit,target,ordering,max_rank);witness=target/'selected-links.json'
        native=subprocess.run([str(matcher),str(dag),str(dag)+'.positive','104729','2',str(witness)],
                              check=True,text=True,capture_output=True)
        row=json.loads(native.stdout);row.update(dag_path=str(dag),dag_sha256=digest(dag),
            positive_sha256=digest(str(dag)+'.positive'),witness_path=str(witness),witness_sha256=digest(witness),
            schedule='rank-node',configuration=dict(center_reconstruction=policy,limit=limit,
                frame_policy='feasible-envelope-helper',cover_order=ordering,max_source_rank=max_rank),original_producer_path=str(parent))
        result=dict(status='fresh envelope-helper witness; independent compiler pending',case_id=name,
            producer=row,selected_links=json.loads(witness.read_text()),centers=records,helper_edits=edits,
            initial_R=old['R'],role_saving=old['R']-row['R'],seconds=time.monotonic()-at)
    except Exception as error:result=dict(status='failed',case_id=name,error=repr(error),seconds=time.monotonic()-at)
    target.mkdir(parents=True,exist_ok=True);(target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,nargs='+',required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=1);p.add_argument('--policy',choices=['largest','rank-first','reverse'],default='largest')
    p.add_argument('--order',nargs='+',choices=['original','locality'],default=['original','locality']);p.add_argument('--limit',type=int,default=64)
    p.add_argument('--max-rank',type=int,default=4)
    a=p.parse_args();assert not a.work.exists()and not a.output.exists();builds=a.work/'builds';builds.mkdir(parents=True)
    matcher=builds/'matcher';subprocess.run(['c++','-O3','-std=c++17',str(Path(__file__).with_name('moment_match_rank_node.cpp')),'-o',str(matcher)],check=True)
    result=dict(status='running',command=sys.argv,workers=a.workers,rows=[],started_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256=digest(__file__),credited_cover_mechanism='Swapnil round6 f2176bc11248; helper frame/order co-design is task-local')
    jobs=[(parent,a.work,matcher,a.policy,a.limit,order,a.max_rank)for parent in a.parent for order in a.order]
    with ProcessPoolExecutor(max_workers=a.workers)as pool:
        for future in as_completed([pool.submit(evaluate,job)for job in jobs]):
            row=future.result();result['rows'].append(row)
            tmp=a.output.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');tmp.replace(a.output)
            print(json.dumps({k:row.get(k)for k in('case_id','status','role_saving','seconds','error')}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
