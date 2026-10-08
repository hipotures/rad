#!/usr/bin/env python3
"""One-slot complete dirty controls containing genuine positive-frame clones."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
from producer_search import initialize,worker
from positive_clone_search import evaluate
from check_compiled_witness import check


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()
    (a.work/'builds').mkdir(parents=True,exist_ok=True);(a.work/'raw').mkdir(exist_ok=True)
    code=Path(__file__).parent
    for source,target in((code/'moment_match_positive.cpp','moment_match_positive'),
                         (code/'moment_match_rank_node.cpp','matcher'),
                         (a.source/'scripts/partial_swap/match_exported_dag.cpp','match_exported_dag')):
        subprocess.run(['c++','-O3','-std=c++17',str(source),'-o',str(a.work/'builds'/target)],check=True)
    initialize(a.source,a.work,a.work/'builds/moment_match_positive')
    result=dict(status='running',command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat(),rows=[])
    for h in(10,12,14,16):
        configuration=dict(h=h,threshold=2,grouping='pairs',tree='left',mode=2,seed=104729)
        row=worker(configuration)
        assert row['status']!='failed',row
        parent=a.work/'raw'/f'small-parent-{h}.json'
        parent.write_text(json.dumps(dict(producer=row),indent=2,sort_keys=True)+'\n')
        cloned=evaluate((parent,a.work,a.work/'builds/matcher','wide',8,104729,4))
        assert cloned['status']!='failed',cloned
        audited=check(cloned,True)
        result['rows'].append(dict(h=h,parent_roles=row['R'],clone_candidate=cloned,independent=audited))
        print(json.dumps(dict(h=h,clones=sum(len(s.get('chosen',[]))for s in cloned['stages']),
                              roles=cloned['producer']['R'],dirty_basis=audited['complete_dirty_basis'])),flush=True)
        if cloned['role_saving']:
            break
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
