#!/usr/bin/env python3
"""Exact changed public skip-prefix graphs and full small dirty-word checks."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
from check_compiled_witness import check
from skip_prefix_search import initialize,worker
from producer_search import digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--builds',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.work.exists()and not a.output.exists();a.work.mkdir(parents=True)
    (a.work/'builds').mkdir()
    for name in ('moment_match_positive','match_exported_dag'):
        shutil.copyfile(a.builds/name,a.work/'builds'/name);(a.work/'builds'/name).chmod(0o755)
    initialize(a.source,a.work,a.work/'builds/moment_match_positive');rows=[]
    for depth,order in [(1,'forward'),(1,'reverse'),(2,'support-ascending'),(3,'support-descending')]:
        config=dict(h=10,threshold=2,grouping='pairs',tree='left',skip_depth=depth,strip_order=order,mode=2,seed=2026100803)
        row=worker(config)
        assert row['status']!='failed',row
        row['independent']=check(row,True);rows.append(row)
    result=dict(status='complete four independently compiled public skip-prefix dirty controls PASS',rows=rows,
        command=sys.argv,source_sha256={name:digest(Path(__file__).with_name(name)) for name in ['skip_prefix_search.py','skip_prefix_small_control.py','check_compiled_witness.py']},
        completed_utc=datetime.now(timezone.utc).isoformat(),source_revision='11817ccacb564bb7f98789c20dc11d3fece207e3')
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'],roles=[row['R']for row in rows],seconds=[row['independent']['seconds']for row in rows])),flush=True)


if __name__=='__main__':main()
