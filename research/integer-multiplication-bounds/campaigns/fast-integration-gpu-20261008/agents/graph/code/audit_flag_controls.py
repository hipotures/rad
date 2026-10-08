#!/usr/bin/env python3
"""Bind coherent source permutations to complete small dirty-word controls."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from check_permuted_compiled_witness import check
from flag_permutation_search import transform
from producer_search import digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.work.exists() and not a.output.exists()
    a.work.mkdir(parents=True)
    document=json.loads(a.parent.read_text())
    if 'rows' in document:
        assert len(document['rows'])==1
        document=document['rows'][0]
    parent=a.work/'parent.json';parent.write_text(json.dumps(document,sort_keys=True)+'\n')
    h=document['producer']['h'];assert h<=16
    adjacent=list(range(h));adjacent[0],adjacent[1]=adjacent[1],adjacent[0]
    rows=[]
    for name,order in [('reverse',list(reversed(range(h)))),('adjacent',adjacent)]:
        witness,proof=transform(parent,a.work/name,order)
        result=check(json.loads(witness.read_text()),True)
        result.update(case_id=name,input_path=str(witness),coordinate_transfer=proof)
        rows.append(result)
    result=dict(status='complete literal scalar and both dirty permutation controls PASS',
        command=sys.argv,rows=rows,completed_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=dict(driver=digest(__file__),compiler=digest(Path(__file__).with_name('check_permuted_compiled_witness.py')),
                           coordinate_transform=digest(Path(__file__).with_name('flag_permutation_search.py'))))
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'],rows=[dict(h=x['h'],roles=x['roles'],seconds=x['seconds'])for x in rows])),flush=True)


if __name__=='__main__':main()
