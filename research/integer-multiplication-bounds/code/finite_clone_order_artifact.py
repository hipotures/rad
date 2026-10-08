#!/usr/bin/env python3
"""Supplement a frozen clone link artifact with its full node-order digest.

No solver, baseline replay or physical coefficient check is repeated.
Envelope dimensions follow the already checked E(C,V) closed form.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

from finite_clone_batch import build,BatchCloneView
from finite_clone_plan_export import tuples,digest
from finite_clone_recovered_witness import descriptions
from finite_block_search import install_reference


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True);ap.add_argument('--certificate',type=Path,required=True)
    ap.add_argument('--links',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();install_reference(args.reference)
    value=json.loads(args.certificate.read_text());row=value['rows'][0];links=json.loads(args.links.read_text())
    jobs=[dict(job,selected=frozenset(tuples(x) for x in job['selected'])) for job in row['chosen']]
    original=build(row['h'],row['base'],row['positions']);view=BatchCloneView(original,jobs)
    frames={node:SimpleNamespace(dimension=1 if view.core[node].bit_count()==3 else
                                view.union[node].bit_count()-view.core[node].bit_count()) for node in view.active}
    order=sorted(view.active,key=lambda node:(frames[node].dimension,node))
    _,uses,_=descriptions(view,frames)
    assert digest(uses)==links['descriptions_sha256']
    result=dict(status='Terminal exact order metadata PASS',candidate_id=links['candidate_id'],
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        selected_link_artifact_sha256=sha256(args.links.read_bytes()).hexdigest(),
        node_order_sha256=digest(order),node_count=len(order),description_count=len(uses),
        descriptions_sha256=digest(uses),ordering='Canonical envelope dimension then explicit node ID',
        scope='Auxiliary metadata; complete changed coefficient/frame verification remains the earlier immutable certificate')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
