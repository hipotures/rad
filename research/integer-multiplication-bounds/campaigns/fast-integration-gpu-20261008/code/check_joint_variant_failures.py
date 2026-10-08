#!/usr/bin/env python3
"""Adversarial coherent-coordinate and provenance controls for joint variants."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
from bind_joint_variant_certificate import local, read


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--axes',type=Path,required=True)
    p.add_argument('--word',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    assert not a.output.exists()
    row=read(a.axes)[0]
    graph=read(a.word)
    results=[]
    for name in ['different-valid-coordinate-order','nonbijective-source-order','false-source-output-coherence','unrelated-word-transition','wrong-role-denominator']:
        r,g=deepcopy(row),deepcopy(graph)
        if name=='different-valid-coordinate-order':g['source_permutation']=list(range(g['h']))
        elif name=='nonbijective-source-order':g['source_permutation'][-1]=g['source_permutation'][0]
        elif name=='false-source-output-coherence':g['coherent_source_output_labels']=False
        elif name=='unrelated-word-transition':g['transition_sha256']='0'*64
        else:r['profile']['R']+=1
        try:local(r,g)
        except AssertionError:results.append(dict(case=name,status='REJECTED AS REQUIRED'))
        else:raise AssertionError(name)
    a.output.write_text(json.dumps(dict(status='PASS INDEPENDENT CHANGED-WORD ADVERSARIAL CONTROLS',
        created_utc=datetime.now(timezone.utc).isoformat(),cases=results,
        verifier_sha256=sha256(Path(__file__).with_name('bind_joint_variant_certificate.py').read_bytes()).hexdigest(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
    print('Five corrupt variants rejected as required')


if __name__=='__main__':main()
