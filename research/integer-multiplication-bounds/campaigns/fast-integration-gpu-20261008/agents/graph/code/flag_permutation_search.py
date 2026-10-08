#!/usr/bin/env python3
"""Global coordinate flags on a fixed, already compiled positive-frame DAG.

Every abstract address space and mask receives the same permutation. The
scalar DAG and controller uses are unchanged. Inverse normalization must
recover the input DAG and frame bytes exactly. Geometry's actual negative
basis CRT profiler rebuilds every changed corner profile. Complete source
triple families are permutation closed; no full source-pair replay occurs.
"""
import argparse
import array
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from datetime import datetime,timezone
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
import math
from pathlib import Path
import random
import struct
import subprocess
import sys
import time
from check_compiled_witness import read_dag
from producer_search import digest


def encode_dag(h,v,n,q,args,core,cover,roots,kinds,active):
    out=bytearray(struct.pack('<4I',h,v,n,q))
    for code,values in(('I',args),('Q',core),('Q',cover),('I',roots),('I',kinds),('B',active)):
        out.extend(array.array(code,values).tobytes())
    return bytes(out)


def encode_labels(h,n,ranks,forced,symbols):
    return struct.pack('<2I',h,n)+array.array('I',ranks).tobytes()+array.array('Q',forced).tobytes()+array.array('b',symbols).tobytes()


@lru_cache(maxsize=4)
def read_parent(path):
    document=json.loads(Path(path).read_text());row=document['producer'];dag=read_dag(row['dag_path'])
    h,v,n,q,*_=dag
    with Path(row['dag_path']+'.positive').open('rb')as stream:
        assert struct.unpack('<2I',stream.read(8))==(h,n)
        ranks=array.array('I');ranks.fromfile(stream,n)
        forced=array.array('Q');forced.fromfile(stream,n)
        symbols=array.array('b');symbols.fromfile(stream,n*h)
        assert not stream.read(1)
    assert sha256(encode_dag(*dag)).hexdigest()==row['dag_sha256']
    assert sha256(encode_labels(h,n,ranks,forced,symbols)).hexdigest()==row['positive_sha256']
    return document,dag,ranks,forced,symbols


def transform(parent,target,order):
    document,dag,ranks,forced,symbols=read_parent(str(parent));row=document['producer']
    h,v,n,q,args,core,cover,roots,kinds,active=dag
    assert sorted(order)==list(range(h));permutation=[0]*h
    for new,old in enumerate(order):permutation[old]=new
    def mask(value,mapping):
        result=0
        while value:
            bit=value&-value;value-=bit;result|=1<<mapping[bit.bit_length()-1]
        return result
    mapping={x:mask(x,permutation)for x in set(core)|set(cover)|set(forced)}
    cc=array.array('Q',(mapping[x]for x in core));vv=array.array('Q',(mapping[x]for x in cover));ff=array.array('Q',(mapping[x]for x in forced))
    sy=array.array('b',[0])*(n*h)
    for old,new in enumerate(permutation):sy[new::h]=symbols[old::h]
    inverse=[0]*h
    for old,new in enumerate(permutation):inverse[new]=old
    inverse_map={x:mask(x,inverse)for x in set(cc)|set(vv)|set(ff)}
    restored_symbols=array.array('b',[0])*(n*h)
    for old,new in enumerate(permutation):restored_symbols[old::h]=sy[new::h]
    restored_dag=encode_dag(h,v,n,q,args,[inverse_map[x]for x in cc],[inverse_map[x]for x in vv],roots,kinds,active)
    restored_labels=encode_labels(h,n,ranks,[inverse_map[x]for x in ff],restored_symbols)
    assert sha256(restored_dag).hexdigest()==row['dag_sha256']
    assert sha256(restored_labels).hexdigest()==row['positive_sha256']
    source_masks={sum(1<<i for i in triple)for triple in combinations(range(h),3)}
    assert {mask(x,permutation)for x in source_masks}==source_masks
    target.mkdir(parents=True,exist_ok=False);path=target/'dag.bin'
    path.write_bytes(encode_dag(h,v,n,q,args,cc,vv,roots,kinds,active))
    Path(str(path)+'.positive').write_bytes(encode_labels(h,n,ranks,ff,sy))
    uses=target/'selected-uses.json';uses.write_text(json.dumps(document['selected_links'],sort_keys=True)+'\n')
    result=dict(row,dag_path=str(path),dag_sha256=digest(path),positive_sha256=digest(str(path)+'.positive'),
                witness_path=str(uses),witness_sha256=digest(uses))
    result['configuration']=dict(global_coordinate_order=order,old_to_new=permutation,
        original_parent=str(parent),scalar_DAG_unchanged=True,controller_use_map_unchanged=True)
    proof=dict(status='exact inverse byte normalization and complete source-triple bijection PASS',
        normalized_dag_sha256=row['dag_sha256'],normalized_positive_sha256=row['positive_sha256'],
        source_triples=v,full_source_pair_replay=False,
        geometric_transfer='Permutation preserves G=I-J/9 and commutes with L_beta; all nested projectors conjugate coherently',
        data_transfer='All triples and center indices permute bijectively; complete source-weight/data matrix family is identical as a multiset')
    wrapper=dict(producer=result,selected_links=document['selected_links'],coordinate_transfer=proof)
    input_path=target/'input-witness.json';input_path.write_text(json.dumps(wrapper,indent=2,sort_keys=True)+'\n')
    return input_path,proof


def initialize(binary,geometry,work,reverse_blocks):
    global PROFILER,WORK,RUN,REVERSE_BLOCKS
    PROFILER=Path(binary);WORK=Path(work);sys.path.insert(0,str(geometry))
    REVERSE_BLOCKS=reverse_blocks
    from run_positive_profiles import run
    RUN=run


def evaluate(task):
    parent,case,order=task;start=time.monotonic();target=WORK/'derived'/case
    try:
        witness,proof=transform(parent,target,order);output=target/'retained-profile.json'
        RUN(witness,PROFILER,'negative',target/'profile',output)
        result=json.loads(output.read_text());producer=result['producer'];h=producer['h'];alpha=result['local_phi']['alpha']
        original=read_parent(str(parent))[0]
        if order==list(range(h)) and 'copied_blocks'in original:
            assert result['copied_blocks']==original['copied_blocks'],'Identity profile changed'
        if order==list(reversed(range(h))) and str(h)in REVERSE_BLOCKS:
            assert result['copied_blocks']==REVERSE_BLOCKS[str(h)],'Reverse flag and transposed dual-root block profiles differ'
        exterior=sum(t*math.expm1(alpha*math.log(575/t))for t in(h,575-2*h))
        return dict(status='actual permuted negative-basis CRT profile PASS; transfer theorem remains separately reviewable',
            case_id=case,h=h,R=producer['R'],order=order,local_phi=result['local_phi']['value'],
            complete_axis_excess=result['local_phi']['value']+producer['R']*exterior,
            retained_witness=str(output),retained_witness_sha256=digest(output),coordinate_transfer=proof,
            dag_sha256=producer['dag_sha256'],positive_sha256=producer['positive_sha256'],seconds=time.monotonic()-start)
    except Exception as error:return dict(status='failed',case_id=case,error=repr(error),seconds=time.monotonic()-start)


def orders(h,count,seed):
    yield 'identity',list(range(h));yield 'reverse',list(reversed(range(h)))
    yield 'even-first',list(range(0,h,2))+list(range(1,h,2))
    yield 'odd-first',list(range(1,h,2))+list(range(0,h,2))
    yield 'zigzag',[x for pair in zip(range((h+1)//2),range(h-1,h//2-1,-1))for x in pair][:h]
    for rotation in range(1,h):yield f'rotation-{rotation}',list(range(rotation,h))+list(range(rotation))
    for stride in range(2,h):
        if math.gcd(stride,h)==1:yield f'stride-{stride}',[(stride*i)%h for i in range(h)]
    for index in range(count):
        order=list(range(h));random.Random(seed+104729*index+h).shuffle(order);yield f'shuffle-{index}',order


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent',type=Path,nargs='+',required=True);p.add_argument('--geometry-code',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=7);p.add_argument('--random-count',type=int,default=128);p.add_argument('--seed',type=int,default=2026100801)
    p.add_argument('--dual-reference',type=Path,nargs='+')
    p.add_argument('--previous-log',type=Path);p.add_argument('--previous-total',type=int,default=563);p.add_argument('--previous-slots',type=int,default=6)
    a=p.parse_args();assert not a.work.exists()and not a.output.exists();a.work.mkdir(parents=True);(a.work/'inputs').mkdir();builds=a.work/'builds';builds.mkdir()
    binary=builds/'positive-frame-profiles';source=a.geometry_code/'positive_frame_profiles.cpp';before=digest(source)
    subprocess.run(['c++','-O3','-std=c++17',str(source),'-o',str(binary)],check=True);assert digest(source)==before
    jobs=[]
    for parent in a.parent:
        snapshot=a.work/'inputs'/parent.name;snapshot.write_bytes(parent.read_bytes());h=json.loads(snapshot.read_text())['producer']['h'];seen=set()
        for name,order in orders(h,a.random_count,a.seed):
            key=tuple(order)
            if key in seen:continue
            seen.add(key);jobs.append((snapshot,f'h{h}-{name}',order))
    reverse_blocks={}
    for path in a.dual_reference or []:
        reference=json.loads(path.read_text());h=reference['producer']['h']
        original=next(json.loads(Path(job[0]).read_text())for job in jobs if job[1].startswith(f'h{h}-'))
        assert reference['producer']['dag_sha256']==original['producer']['dag_sha256']
        assert reference['selected_links']['links']==original['selected_links']['links']
        reverse_blocks[str(h)]=reference['copied_blocks']
    result=dict(status='running',command=sys.argv,total_cases=len(jobs),rows=[],seed=a.seed,
        started_utc=datetime.now(timezone.utc).isoformat(),source_sha256=dict(driver=digest(__file__),geometry_profiler=before,
        geometry_driver=digest(a.geometry_code/'run_positive_profiles.py')))
    active={};pending=list(jobs);last_status=0
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,initargs=(binary,a.geometry_code,a.work,reverse_blocks))as pool:
        while pending or active:
            remaining=0
            if a.previous_log:
                lines=a.previous_log.read_text().splitlines()if a.previous_log.exists()else[]
                completed=sum('"case_id"'in line and'"role_saving"'in line for line in lines)
                remaining=max(0,a.previous_total-completed)
            available=a.workers-min(a.previous_slots,remaining)
            while pending and len(active)<available:
                job=pending.pop(0);active[pool.submit(evaluate,job)]=job
            if active:
                done,_=wait(active,timeout=1,return_when=FIRST_COMPLETED)
                for future in done:
                    job=active.pop(future)
                    try:row=future.result()
                    except Exception as error:row=dict(status='failed',case_id=job[1],error=repr(error))
                    result['rows'].append(row)
                    print(json.dumps({k:row.get(k)for k in('case_id','status','R','local_phi','seconds','error')}),flush=True)
            else:time.sleep(1)
            if time.monotonic()-last_status>=15 or not pending and not active:
                tmp=a.output.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');tmp.replace(a.output)
                (a.work/'status.json').write_text(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),completed=len(result['rows']),
                    total=len(jobs),active=len(active),previous_remaining=remaining,available=available),indent=2)+'\n');last_status=time.monotonic()
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat());a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
