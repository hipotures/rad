#!/usr/bin/env python3
"""Bounded CPU-only exact regeneration into a new namespace; never run an engine."""
import argparse
import gzip
import hashlib
import subprocess
import sys
from common import *

def main(run,output):
    if output.exists():raise SystemExit('Refuse an existing output namespace')
    catalog=load(REVIEW/'site/data/catalog.json');r=next(x for x in catalog['runs'] if x['id']==run and x.get('summary_url'))
    retained=REVIEW/'evidence/browser-v1/runs'/run
    summary=load(retained/'summary.json.gz')
    for source in summary['provenance']:
        p=Path(source['path'])
        if not p.exists():raise SystemExit(f'Required retained input is unavailable: {p}; see artifact-manifest.json')
        assert p.stat().st_size==source['bytes'] and digest(p)==source['sha256'],p
    command=[sys.executable,str(REVIEW/'code/build_atlas.py'),'--only',run,'--output',str(output)]
    subprocess.run(command,check=True,timeout=240)
    checks=[]
    for l in range(48):
        d=load(retained/f'layer-{l}.json.gz');actual=digest(output/'runs'/run/f'layer-{l}.json')
        assert actual==d['normalized_source_sha256'],(run,l,'normalized file identity')
        checks.append(dict(layer=l,state='PASS',normalized_sha256=actual))
    with gzip.open(retained/'summary.json.gz','rb') as f:old=f.read()
    assert hashlib.sha256(old).hexdigest()==digest(output/'runs'/run/'summary.json'),'Summary differs'
    result=dict(state='PASS',run=run,source_files_checked=len(summary['provenance']),exact_layer_files=48,
                exact_summary=True,command=command,output=str(output),checks=checks,gpu_calls=0)
    save(REVIEW/'results/reproduction-validation.json',result)
    print('EXACT_REGENERATION_PASS',run,'48 layers and summary',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',default='golden-swap-phase2--math-inventory-block1-ORACLE_IN_HISTORY_TC')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();main(a.run,a.output)
