#!/usr/bin/env python3
"""Test source-form-equivalent controller routes on distinct edited DAGs.

The equality classes are exact integer coefficient sets for cancellation-free
gates. A protected first actual use preserves at least one output carrier for
every original gate. The physical compiler separately checks scalar equality,
address containment, rank moments and the complete transparent dirty word.
"""
from __future__ import annotations
import argparse
import array
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
from check_compiled_witness import check, read_dag
from producer_search import digest


def evaluate(task):
    document, work, matcher, dirty = task
    parent = document['producer']
    start = time.monotonic()
    target = Path(work) / 'raw' / parent['dag_sha256'][:24]
    target.mkdir(parents=True, exist_ok=False)
    try:
        h,v,n,q,args,core,cover,roots,kinds,active = read_dag(parent['dag_path'])
        scalar = [0]*n
        classes = {}
        equiv = [0]*n
        for node in range(1,n):
            if not active[node]:
                continue
            if args[2*node]:
                a,b = args[2*node:2*node+2]
                assert not scalar[a] & scalar[b]
                scalar[node] = scalar[a] | scalar[b]
            else:
                scalar[node] = 1 << (node-1)
            equiv[node] = classes.setdefault(scalar[node], node)
        equality_file = target / 'exact-equality-classes.bin'
        with equality_file.open('wb') as stream:
            stream.write(struct.pack('<I',n))
            stream.write(array.array('I',equiv).tobytes())
        witness = target / 'selected-links.json'
        native = subprocess.run([str(matcher), parent['dag_path'], parent['dag_path']+'.positive',
                                 '104729', '2', str(witness), str(equality_file)],
                                check=True, capture_output=True, text=True)
        row = json.loads(native.stdout)
        row.update(dag_path=parent['dag_path'], dag_sha256=parent['dag_sha256'],
                   positive_sha256=parent['positive_sha256'], witness_path=str(witness),
                   witness_sha256=digest(witness), schedule='rank-node', semantic_routing=True,
                   configuration=dict(equivalent_source_forms=True, seed=104729, mode=2,
                                      protect='one earliest actual use per logical node'))
        result = dict(status='exact semantic-routing candidate; compiled check pending', producer=row,
                      selected_links=json.loads(witness.read_text()), initial_R=parent['R'],
                      role_saving=parent['R']-row['R'], duplicate_nodes=n-1-len(classes),
                      equality_classes_sha256=digest(equality_file), initial_case_id=document.get('case_id'),
                      original_producer_path=parent['dag_path'], seconds=time.monotonic()-start)
        if dirty:
            result['independent'] = check(result, True)
            result['status'] = 'exact semantic routing and complete dirty dual audit PASS'
        (target / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        return result
    except Exception as error:
        result = dict(status='failed', h=parent['h'], initial_R=parent['R'], error=repr(error),
                      original_producer_path=parent['dag_path'], seconds=time.monotonic()-start)
        (target / 'failure.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--witness', type=Path, nargs='+', required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--workers', type=int, default=9)
    p.add_argument('--dirty', action='store_true')
    a = p.parse_args()
    assert not a.work.exists() and not a.output.exists() and 1 <= a.workers <= 10
    (a.work/'builds').mkdir(parents=True)
    native = Path(__file__).with_name('moment_match_equal_forms.cpp')
    matcher = a.work/'builds'/'matcher'
    subprocess.run(['c++','-O3','-std=c++17',str(native),'-o',str(matcher)],check=True)
    documents = []
    seen = set()
    for path in a.witness:
        item = json.loads(path.read_text())
        for doc in item['rows'] if 'rows' in item else [item]:
            if doc.get('status') == 'failed':
                continue
            row = doc.get('producer')
            if not row:
                continue
            key = row['dag_sha256']
            if key not in seen:
                documents.append(doc)
                seen.add(key)
    result = dict(status='running', command=sys.argv, workers=a.workers,
                  input_paths=[str(p) for p in a.witness], distinct_dags=len(documents), rows=[],
                  started_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256={p.name:digest(p) for p in (Path(__file__),native,
                                    Path(__file__).with_name('check_compiled_witness.py'))})
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        futures = [pool.submit(evaluate,(doc,a.work,matcher,a.dirty)) for doc in documents]
        for future in as_completed(futures):
            row = future.result()
            result['rows'].append(row)
            a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            print(json.dumps(dict(h=row.get('producer',{}).get('h'),R=row.get('producer',{}).get('R'),
                                  role_saving=row.get('role_saving'),status=row['status'],
                                  error=row.get('error'),seconds=row['seconds'])),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
