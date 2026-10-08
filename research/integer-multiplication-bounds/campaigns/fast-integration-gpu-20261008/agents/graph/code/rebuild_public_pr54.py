#!/usr/bin/env python3
"""Public pinned PR54 reconstruction with an independent complete compiler.

The source graph and606 clone jobs are public PR54 implementation, explicitly
authorized by the user during this campaign. Original-envelope compilation,
source coefficients, role trajectories and both full dirty orientations are
checked by the retained independently implemented RaD compiler. All source
credits and Apache2 notices remain in the immutable upstream snapshot.
"""
import argparse
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import struct
import sys
from check_large_original_witness import check
from producer_search import digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.work.exists()and not a.output.exists();a.work.mkdir(parents=True)
    sys.dont_write_bytecode=True
    upstream=a.source/'research/skip-clones';sys.path.insert(0,str(upstream));sys.path.insert(0,str(a.source/'scripts'))
    import clone_io
    clone_io.check_sources(clone_io.REPLAY_INPUTS)
    spec=importlib.util.spec_from_file_location('public_pr54_cloned_graph',upstream/'cloned_graph.py')
    graph=importlib.util.module_from_spec(spec);spec.loader.exec_module(graph)
    from partial_swap.graph import export
    rows=[];total_clones=0
    for h in[23,25]:
        target=a.work/f'h{h}';target.mkdir();circuit=graph.graph(h);scalar=circuit.verify()
        assert scalar==clone_io.read(upstream/f'scalar-{h}.json')
        dag=target/'dag.bin';export(circuit,dag)
        expected=clone_io.read(upstream/f'original-{h}.json');raw=(upstream/f'links-{h}.uses').read_bytes()
        n,count=struct.unpack_from('<2I',raw);assert n==len(circuit.args)and len(raw)==8+8*count
        links=[list(struct.unpack_from('<2I',raw,8+8*i))for i in range(count)]
        selected=dict(h=h,n=n,links=links);uses=target/'selected-uses.json';uses.write_text(json.dumps(selected,sort_keys=True)+'\n')
        producer=dict(expected,dag_path=str(dag),dag_sha256=digest(dag),witness_path=str(uses),witness_sha256=digest(uses),
                      frame_source='original-envelope',configuration=dict(public_PR54=True,source_head='84eb0b067741dc2690da837743fda06d133da865',schedule='rank-node-original'))
        jobs=clone_io.read(upstream/f'clone-jobs-{h}.json');rounds=[len(r['jobs'])for r in jobs['rounds']]
        assert sum(rounds)==scalar['cloned_additions'];total_clones+=sum(rounds)
        wrapper=dict(producer=producer,selected_links=selected,scalar=scalar,clone_round_counts=rounds,
            upstream_sources=dict(repository='https://github.com/CrocSwap/integer-mult-bounds',pull_request=54,
                head='84eb0b067741dc2690da837743fda06d133da865',local_read_only_snapshot=str(a.source),
                jobs_sha256=digest(upstream/f'clone-jobs-{h}.json'),cloned_graph_sha256=digest(upstream/'cloned_graph.py')))
        path=target/'axis.json';path.write_text(json.dumps(wrapper,indent=2,sort_keys=True)+'\n')
        audit=check(wrapper,True)
        row=dict(h=h,R=producer['R'],c=producer['c'],matched=producer['matched'],clone_round_counts=rounds,
            wrapper_path=str(path),wrapper_sha256=digest(path),dag_sha256=producer['dag_sha256'],independent=audit)
        rows.append(row)
        print(json.dumps(dict(h=h,R=producer['R'],rounds=rounds,status=audit['status'],seconds=audit['seconds'])),flush=True)
    assert total_clones==606
    N=1771*2300;W=2*N+2300*rows[0]['R']+1771*rows[1]['R'];assert W==159592676
    result=dict(status='publicPR54 exact606clones, selected uses, scalar, physical compiler and both complete dirty orientations PASS',
        rows=rows,N=N,W=W,total_paid_clones=total_clones,total_added_retained_links=2*total_clones,
        command=sys.argv,source_head='84eb0b067741dc2690da837743fda06d133da865',completed_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=dict(driver=digest(__file__),independent_compiler=digest(Path(__file__).with_name('check_large_original_witness.py'))),
        scope='Independent finite compiled replay; public fixed matrix CRT and complete arithmetic certificates are reviewed separately by geometry/coordinator. General transfer remains conditional.')
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
