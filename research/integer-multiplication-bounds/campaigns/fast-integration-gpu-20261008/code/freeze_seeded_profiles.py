#!/usr/bin/env python3
"""Select distinct completed seeded DAGs for fresh physical basis profiles."""
import argparse,json
from hashlib import sha256
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--cohorts',type=Path,nargs='+',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--per-dimension',type=int,default=64)
    p.add_argument('--dimensions',type=int,nargs='+',default=[23,25])
    a=p.parse_args();assert not a.output.exists()
    rows=[]
    for path in a.cohorts:
        obj=json.loads(path.read_text());assert obj['status']=='complete'
        rows.extend(obj['rows'])
    selected=[]
    for h in a.dimensions:
        candidates=sorted([r for r in rows if r.get('h')==h and 'dag_sha256' in r],key=lambda r:r['R'])
        seen=set()
        for r in candidates:
            key=tuple(r[k] for k in ('dag_sha256','positive_sha256','witness_sha256'))
            if key in seen:continue
            seen.add(key);links=json.loads(Path(r['witness_path']).read_text())
            selected.append(dict(producer=r,selected_links=links,case_id=r['case_id']))
            if len(seen)==a.per_dimension:break
    obj=dict(rows=selected,scope='Distinct byte DAG/frame/map triples; not graph-isomorphism classes',
             source_inputs=[dict(path=str(x),sha256=sha256(x.read_bytes()).hexdigest()) for x in a.cohorts],
             per_dimension=a.per_dimension,dimensions=a.dimensions)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(obj)+'\n')
    print(json.dumps(dict(selected=len(selected),output=str(a.output))))

if __name__=='__main__':main()
