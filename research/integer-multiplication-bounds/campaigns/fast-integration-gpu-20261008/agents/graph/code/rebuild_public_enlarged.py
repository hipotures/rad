#!/usr/bin/env python3
"""Regenerate pinned public PR54, then replay retained whole-chain enlargements.

PR54 code and its 606 original-envelope copies are upstream public work, used
under explicit authorization. The subsequent literal first-consumer-frame
copies are authored RaD GPU work. Every paid gate, input continuation, original
frame, selected-use map and final payload restoration is checked separately.
"""
from __future__ import annotations
import argparse
import array
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
from check_large_original_witness import check,read_dag
from positive_clone_search import opportunities,rewrite
from producer_search import digest


def original_labels(dag):
    h,v,n,q,args,core,cover,roots,kinds,active=read_dag(dag)
    ranks=[0]*n;symbols=[0]*(n*h)
    for node in range(1,n):
        if not active[node]:continue
        ranks[node]=1 if not args[2*node]else cover[node].bit_count()-core[node].bit_count()
        for i in range(h):
            symbols[node*h+i]=1 if core[node]>>i&1 else (i+2 if args[2*node]and cover[node]>>i&1 else 0)
    path=Path(str(dag)+'.positive')
    with path.open('wb')as stream:
        stream.write(struct.pack('<2I',h,n))
        for code,values in(('I',ranks),('Q',core),('b',symbols)):
            stream.write(array.array(code,values).tobytes())
    return path


def rebuild(source,work,parent_path,selected_path):
    assert source.is_dir()and not work.exists();work.mkdir(parents=True)
    sys.dont_write_bytecode=True
    upstream=source/'research/skip-clones'
    sys.path.insert(0,str(source/'scripts'));sys.path.insert(0,str(upstream))
    import clone_io
    clone_io.check_sources(clone_io.REPLAY_INPUTS)
    spec=importlib.util.spec_from_file_location('replayed_public_pr54_graph',upstream/'cloned_graph.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    from partial_swap.graph import export
    parent=json.loads(parent_path.read_text());expected=parent['producer'];h=expected['h']
    selected=json.loads(selected_path.read_text())
    circuit=module.graph(h);scalar=circuit.verify()
    assert scalar==clone_io.read(upstream/f'scalar-{h}.json')
    dag=work/'baseline.bin';export(circuit,dag);labels=original_labels(dag)
    assert digest(dag)==expected['dag_sha256'],'Pinned public scalar DAG differs'
    assert digest(labels)==expected['positive_sha256'],'Original E(C,M) literal labels differ'
    raw=(upstream/f'links-{h}.uses').read_bytes();n,count=struct.unpack_from('<2I',raw)
    assert n==len(circuit.args)and len(raw)==8+8*count
    links=[list(struct.unpack_from('<2I',raw,8+8*i))for i in range(count)]
    witness=work/'baseline-selected-uses.json'
    witness.write_text(json.dumps(dict(h=h,n=n,links=links),sort_keys=True)+'\n')
    assert digest(witness)==expected['witness_sha256'],'Pinned original matching differs'
    row=dict(expected,dag_path=str(dag),witness_path=str(witness));initial=dict(row)
    matcher=work/'matcher';native=Path(__file__).with_name('moment_match_rank_node.cpp')
    subprocess.run(['c++','-O3','-std=c++17',str(native),'-o',str(matcher)],check=True)
    policy,limit,seed=(selected['producer']['configuration'][k]for k in('policy','limit','seed'))
    stages=[]
    for index,recorded in enumerate(selected['stages']):
        jobs,diagnostics,order,frames=opportunities(row,limit,policy,seed+1000003*index)
        if recorded.get('terminal'):
            assert not jobs,'Recorded final clone frontier changed';break
        assert jobs==recorded['chosen'],'Selected paid whole-chain edits differ'
        target=work/'clones'/f'round-{index+1}'
        dag,constructed=rewrite(row,jobs,order,frames,target);witness=target/'selected-links.json'
        result=subprocess.run([str(matcher),str(dag),str(dag)+'.positive',str(seed+index),'2',str(witness)],text=True,capture_output=True,check=True)
        new=json.loads(result.stdout)
        assert new['R']==recorded['new_roles']
        assert new['matched']>=row['matched']+2*len(jobs)
        assert digest(dag)==recorded['new_dag_sha256']
        new.update(dag_path=str(dag),dag_sha256=digest(dag),positive_sha256=digest(str(dag)+'.positive'),
                   witness_path=str(witness),witness_sha256=digest(witness),schedule='rank-node',
                   configuration=dict(policy=policy,limit=limit,seed=seed,round=index+1))
        stages.append(dict(round=index+1,clones=len(jobs),R=new['R'],dag_sha256=new['dag_sha256'],rewrite_path=str(target/'rewrite.json')))
        row=new
    expected=selected['producer']
    for key in('dag_sha256','positive_sha256','witness_sha256','histogram','R'):
        assert row[key]==expected[key],f'Final {key} differs'
    audit=check(dict(producer=row),True)
    public_jobs=clone_io.read(upstream/f'clone-jobs-{h}.json')
    result=dict(status='source-only public PR54 plus literal whole-chain enlargement and full dirty audit PASS',
        source_head='84eb0b067741dc2690da837743fda06d133da865',repository='https://github.com/CrocSwap/integer-mult-bounds',
        upstream_paid_clone_count=sum(len(r['jobs'])for r in public_jobs['rounds']),
        new_paid_clone_count=sum(s['clones']for s in stages),initial_producer=initial,producer=row,
        parent_fixture=str(parent_path),parent_fixture_sha256=digest(parent_path),
        selected_fixture=str(selected_path),selected_fixture_sha256=digest(selected_path),stages=stages,independent=audit,
        source_sha256={p.name:digest(p)for p in(Path(__file__),native,Path(__file__).with_name('positive_clone_search.py'),upstream/'cloned_graph.py')},
        command=sys.argv,completed_utc=datetime.now(timezone.utc).isoformat())
    (work/'rebuild-result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(h=h,R=row['R'],new_copies=result['new_paid_clone_count'],status=result['status'])),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--parent',type=Path,required=True);p.add_argument('--selected',type=Path,required=True)
    a=p.parse_args();rebuild(a.source.resolve(),a.work.resolve(),a.parent.resolve(),a.selected.resolve())


if __name__=='__main__':main()
