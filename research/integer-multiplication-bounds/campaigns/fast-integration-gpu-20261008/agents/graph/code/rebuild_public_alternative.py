#!/usr/bin/env python3
"""Source-only pinned PR54 -> retained whole copies -> alternative producers.

Actual selected controller maps are retained finite witness inputs, not old
compiled graphs. Scalar source, every paid edit and literal frame are freshly
regenerated before the independent complete dirty compiler runs. An optional
geometry-selected weighted map is bound to that exact fresh DAG/frame tuple.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
from alternative_producer_clones import opportunities,rewrite
from check_large_original_witness import check
from producer_search import digest
from rebuild_public_enlarged import rebuild as rebuild_whole


def rebuild(source,work,original_path,whole_path,selected_path,weighted_path=None):
    assert not work.exists();work.mkdir(parents=True)
    initial=rebuild_whole(source,work/'whole-parent',original_path,whole_path)
    row=dict(initial['producer']);selected=json.loads(selected_path.read_text());expected=selected['producer']
    config=expected['configuration'];policy=config.get('selection_policy','conservative');limit=config['limit']
    matcher=work/'whole-parent/matcher';stages=[]
    for index,recorded in enumerate(selected['stages']):
        jobs,diagnostics,order,frames=opportunities(row,limit,policy)
        if recorded.get('terminal'):
            assert not jobs,'Retained terminal alternative frontier changed';break
        assert jobs==recorded['chosen'],'Selected exact coefficient partitions differ'
        target=work/'alternatives'/f'round-{index+1}';dag=rewrite(row,jobs,order,frames,target)
        witness=target/'selected-links.json'
        output=subprocess.run([str(matcher),str(dag),str(dag)+'.positive','104729','2',str(witness)],text=True,capture_output=True,check=True)
        new=json.loads(output.stdout)
        assert new['matched']>=row['matched']+2*len(jobs)
        assert new['R']==recorded['new_roles']
        assert digest(dag)==recorded['new_dag_sha256']
        new.update(dag_path=str(dag),dag_sha256=digest(dag),positive_sha256=digest(str(dag)+'.positive'),
                   witness_path=str(witness),witness_sha256=digest(witness),schedule='rank-node',configuration=config)
        stages.append(dict(round=index+1,new_paid_copies=len(jobs),R=new['R'],dag_sha256=new['dag_sha256'],rewrite_path=str(target/'rewrite.json')))
        row=new
    for key in('dag_sha256','positive_sha256','witness_sha256','histogram','R'):
        assert row[key]==expected[key],f'Exact final {key} differs'
    audit=check(dict(producer=row),True)
    weighted=None
    if weighted_path:
        document=json.loads(weighted_path.read_text());p=document['producer'];links=document['selected_links']
        for key in('h','R','dag_sha256','positive_sha256'):
            assert p[key]==row[key],f'Geometry-selected {key} is a different construction'
        fresh=work/'weighted-selected-uses.json';fresh.write_text(json.dumps(links,sort_keys=True)+'\n')
        producer=dict(p,dag_path=row['dag_path'],witness_path=str(fresh),witness_sha256=digest(fresh))
        wrapper=dict(document,producer=producer,selected_links=links)
        path=work/'weighted-axis.json';path.write_text(json.dumps(wrapper,indent=2,sort_keys=True)+'\n')
        weighted=dict(producer=producer,fixture=str(weighted_path),fixture_sha256=digest(weighted_path),
                      selected_map_semantic_sha256=__import__('hashlib').sha256(json.dumps(links,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                      wrapper_path=str(path),independent=check(wrapper,True))
    result=dict(status='exact source-only public whole/alternative producers and complete dirty audit PASS',
        source_head='84eb0b067741dc2690da837743fda06d133da865',repository='https://github.com/CrocSwap/integer-mult-bounds',
        whole_source_receipt=str(work/'whole-parent/rebuild-result.json'),whole_upstream_copies=initial['upstream_paid_clone_count'],
        whole_new_paid_copies=initial['new_paid_clone_count'],alternative_new_paid_copies=sum(s['new_paid_copies']for s in stages),
        producer=row,stages=stages,independent=audit,weighted_selected=weighted,
        fixtures={str(p):digest(p)for p in(original_path,whole_path,selected_path)},
        source_sha256={p.name:digest(p)for p in(Path(__file__),Path(__file__).with_name('alternative_producer_clones.py'),Path(__file__).with_name('rebuild_public_enlarged.py'))},
        command=sys.argv,completed_utc=datetime.now(timezone.utc).isoformat())
    (work/'rebuild-result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(h=row['h'],R=row['R'],status=result['status'],weighted=bool(weighted))),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in('source','work','original','whole','selected'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--weighted',type=Path)
    a=p.parse_args();rebuild(a.source.resolve(),a.work.resolve(),a.original.resolve(),a.whole.resolve(),a.selected.resolve(),a.weighted.resolve()if a.weighted else None)


if __name__=='__main__':main()
