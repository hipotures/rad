#!/usr/bin/env python3
"""Independent DAG/support/positive-space and selected-link review.

Reads the retained binary witness directly; imports no producer, labeler or
native matching implementation. Integer bases give exact space inclusions.
Literal compiled dirty-state action is a separate required interface review.
"""
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,array,json,struct,sys,time

def arrays(data,offset,kind,count):
    a=array.array(kind);size=a.itemsize*count;a.frombytes(data[offset:offset+size]);assert len(a)==count
    if sys.byteorder!='little' and a.itemsize>1:a.byteswap()
    return a,offset+size
def read(dag,labels):
    data=dag.read_bytes();h,v,n,q=struct.unpack_from('<4I',data);offset=16
    args,offset=arrays(data,offset,'I',2*n);core,offset=arrays(data,offset,'Q',n);cover,offset=arrays(data,offset,'Q',n)
    roots,offset=arrays(data,offset,'I',q);kind,offset=arrays(data,offset,'I',q);active,offset=arrays(data,offset,'B',n);assert offset==len(data)
    data=labels.read_bytes();assert struct.unpack_from('<2I',data)==(h,n);offset=8
    rank,offset=arrays(data,offset,'I',n);forced,offset=arrays(data,offset,'Q',n);symbols,offset=arrays(data,offset,'b',n*h);assert offset==len(data)
    return h,v,n,q,args,core,cover,roots,kind,active,rank,forced,symbols

def verify(record):
    start=time.monotonic();dag=Path(record['dag_path']);labels=Path(str(dag)+'.positive');wit=Path(record['witness_path'])
    assert sha256(dag.read_bytes()).hexdigest()==record['dag_sha256']
    assert sha256(labels.read_bytes()).hexdigest()==record['positive_sha256']
    assert sha256(wit.read_bytes()).hexdigest()==record['witness_sha256']
    h,v,n,q,args,core,cover,roots,kind,active,rank,forced,symbols=read(dag,labels)
    assert q==h*((h-1)*(h-2)//2+1)
    support=[0]*n;source_nodes=[];point_masks=[0]*h;triples=[];addition_count=0
    for x in range(1,n):
        if not active[x]:continue
        left,right=args[2*x:2*x+2]
        if left:
            assert 0<left<x and 0<right<x and active[left] and active[right]
            assert not support[left]&support[right]
            support[x]=support[left]|support[right];addition_count+=1
            assert core[x]==core[left]&core[right] and cover[x]==cover[left]|cover[right]
        else:
            assert not right and core[x]==cover[x] and core[x].bit_count()==3
            triple=tuple(i for i in range(h) if core[x]>>i&1);assert triple not in triples
            bit=1<<len(source_nodes);support[x]=bit;source_nodes.append(x);triples.append(triple)
            for i in triple:point_masks[i]|=bit
        assert core[x] and support[x]
    assert len(source_nodes)==v==h*(h-1)*(h-2)//6
    full=(1<<h)-1;output_ids=set();total_outputs=[]
    for j,x in enumerate(roots):
        assert active[x] and core[x].bit_count()==1
        common=(core[x]&-core[x]).bit_length()-1
        if kind[j]:
            assert kind[j]==1 and cover[x]==full and rank[x]==h-1
            expected=point_masks[common];total_outputs.append(j);key=(common,())
        else:
            omitted=full^cover[x];assert omitted.bit_count()==2 and not omitted&core[x]
            excluded=tuple(i for i in range(h) if omitted>>i&1)
            expected=point_masks[common]&~point_masks[excluded[0]]&~point_masks[excluded[1]];key=(common,excluded)
        assert support[x]==expected and key not in output_ids;output_ids.add(key)
    assert len(total_outputs)==h
    keys={};basis_cache={};membership_calls=0;basis_vectors_checked=0
    def key(x):
        if x not in keys:keys[x]=(forced[x],tuple(symbols[x*h:(x+1)*h]))
        return keys[x]
    def space(x):
        k=key(x)
        if k in basis_cache:return basis_cache[k]
        F,sy=k;assert F and not F&~core[x]
        assert all((s==1)==bool(F>>i&1) for i,s in enumerate(sy))
        if not args[2*x]:
            assert F==core[x] and rank[x]==1
            basis=[tuple(int(F>>i&1) for i in range(h))]
        else:
            f=F.bit_count();assert f in (1,2);classes=sorted(set(abs(s) for s in sy if abs(s)>1));assert len(classes)==rank[x]
            basis=[]
            for c in classes:
                sigma=sum(1 if s==c else -1 if s==-c else 0 for s in sy)
                basis.append(tuple(sigma if F>>i&1 else (3-f)*(1 if s==c else -1 if s==-c else 0) for i,s in enumerate(sy)))
        basis_cache[k]=basis;return basis
    def member(v,y):
        F,sy=key(y);common=(F&-F).bit_length()-1
        if sum(v)!=3*v[common] or any(v[i]!=v[common] for i in range(h) if F>>i&1):return False
        values={}
        for z,s in zip(v,sy):
            if s==0:
                if z:return False
            elif abs(s)>1:
                c=abs(s);value=z if s>0 else -z
                if c in values and values[c]!=value:return False
                values[c]=value
        return True
    inclusion_cache=set()
    def included(x,y):
        nonlocal membership_calls,basis_vectors_checked
        k=(key(x),key(y))
        if k in inclusion_cache:return
        membership_calls+=1
        assert rank[x]<=rank[y]
        for v0 in space(x):assert member(v0,y);basis_vectors_checked+=1
        inclusion_cache.add(k)
    for x in range(1,n):
        if not active[x]:continue
        bx=space(x);assert len(bx)==rank[x]
        # Positive norm under I-J/9 on the common-point hyperplane:
        # x^T G x = sum_{i != common} x_i^2. Distinct basis classes
        # have unique free nonforced coordinates and hence independent columns.
        common=(forced[x]&-forced[x]).bit_length()-1
        assert all(sum(t*t for i,t in enumerate(v0) if i!=common)>0 for v0 in bx)
        if args[2*x]:
            included(args[2*x],x);included(args[2*x+1],x)
    links=json.loads(wit.read_text())['links'];donors=set();uses=set();oldrank=[0]*n
    for x in range(1,n):
        if active[x]:oldrank[x]=cover[x].bit_count()-core[x].bit_count() if args[2*x] else 1
    for donor,use in links:
        assert donor not in donors and use not in uses and active[donor] and args[2*donor]
        donors.add(donor);uses.add(use)
        if use>>31:
            j=use&0x7fffffff;assert j<q;target=roots[j];value=target;event_order=n+j
        else:
            target=use//2;assert active[target] and args[2*target];value=args[2*target+(use&1)];event_order=target
        assert value in args[2*donor:2*donor+2]
        assert (rank[donor],oldrank[donor],donor)<(rank[target],oldrank[target],event_order)
        included(donor,target);included(value,donor)
    assert len(links)==record['matched'] and addition_count+q-len(links)==record['R']
    # Reconstruct each local residual class independently, retaining zero ranks.
    degree=[0]*n
    for x in range(1,n):
        if active[x] and args[2*x]:
            degree[args[2*x]]+=1;degree[args[2*x+1]]+=1
    for x in roots:degree[x]+=1
    hist=Counter();loss=0
    for x in range(1,n):
        if not active[x]:continue
        r=rank[x];assert degree[x]
        if args[2*x]:
            hist[r]+=degree[x]-1;hist[h-r]+=1
            hist[r-rank[args[2*x]]]+=1;hist[r-rank[args[2*x+1]]]+=1
        else:hist[1]+=degree[x]
    for j,x in enumerate(roots):
        r=rank[x]
        if kind[j]:hist[r]+=1;hist[h]+=1;loss+=r
        else:hist[h-1-r]+=1;hist[1]+=1
    for donor,use in links:
        target=roots[use&0x7fffffff] if use>>31 else use//2
        value=target if use>>31 else args[2*target+(use&1)]
        hist[h-rank[donor]]-=1;hist[rank[value]]-=1;hist[rank[target]-rank[value]]-=1;hist[rank[target]-rank[donor]]+=1
    actual=[hist[r] for r in range(h+1)];assert actual==record['histogram'] and all(x>=0 for x in actual)
    assert sum(r*count for r,count in enumerate(actual))==h*record['R']+2*loss
    copied=actual[:];copied[1]+=h;copied[h]-=h
    assert copied[h-1]==actual[h-1] and sum(r*count for r,count in enumerate(copied))==h*record['R']+loss
    return dict(status='PASS INDEPENDENT SCALAR SUPPORTS, POSITIVE SPACES, SELECTED LINKS AND RANK CLASSES',h=h,v=v,n=n,q=q,
                additions=addition_count,R=record['R'],matched=len(links),loss=loss,rank_histogram=actual,copied_rank_histogram=copied,
                all_output_supports_exact=True,all_additions_disjoint=True,positive_nondegeneracy='Exact common-point identity with independent free signed-component coordinates',
                nested_inclusion_pairs=membership_calls,integer_basis_vectors_checked=basis_vectors_checked,
                terminal_total_uses=total_outputs,terminal_encoding='Distinct high-bit terminal uses, separate from every producer-input incidence',
                unique_donors_and_input_uses=True,lexicographic_controller_dependencies_acyclic=True,
                input_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in (dag,labels,wit)},
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),elapsed_seconds=time.monotonic()-start,
                completed_utc=datetime.now(timezone.utc).isoformat(),
                limitations=['Literal compiled gates and arbitrary dirty auxiliary restoration require separate graph-worker check',
                             'Common basis theorem is a written general argument, not giant basis materialization',
                             'Native Gaussian/tape/precision/full multiplication assembly remain separate obligations'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--record',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    record=json.loads(args.record.read_text());record=record.get('producer',record)
    result=verify(record);args.output.parent.mkdir(parents=True,exist_ok=True);assert not args.output.exists();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','h','R','nested_inclusion_pairs','integer_basis_vectors_checked','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
