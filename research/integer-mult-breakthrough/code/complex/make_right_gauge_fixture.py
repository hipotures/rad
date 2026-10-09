#!/usr/bin/env python3
"""Generate literal reflection/reuse interfaces for independent review."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path

import right_reflected_frame_gauges as producer


def make_fixture():
    exact=producer.exact
    cases=[]
    def add(kind,n,E,F=()):
        E,F=exact.basis(E),exact.basis(F)
        if kind=='reflection':
            normal=producer.reflection_gauge(E,n)
            word=producer.reflected_word(E,n)
        elif kind=='canonical-to-right':
            normal=producer.compile_canonical_to_right(E,F,n)
            word=(exact.inverse_word(exact.literal_word(E,n))
                  +exact.literal_word(producer.full(n),n)+exact.literal_word(F,n))
        elif kind=='right-to-canonical':
            normal=producer.compile_right_to_canonical(E,F,n)
            word=(exact.inverse_word(exact.literal_word(E,n))
                  +exact.inverse_word(exact.literal_word(producer.full(n),n))
                  +exact.literal_word(F,n))
        else:
            raise ValueError('Unknown fixture interface')
        cases.append(dict(kind=kind,n=n,source_subspace=list(E),target_subspace=list(F),
                          source_canonical_spec=exact.reference.frame_spec(E,n),
                          target_canonical_spec=exact.reference.frame_spec(F,n),
                          actual_relative_word=word,normal_form=normal))
    add('reflection',3,(3,))
    add('reflection',4,(1,7))
    for target in (8,14):
        add('canonical-to-right',4,(1,7),(target,))
        add('right-to-canonical',4,(1,7),(target,))
    add('reflection',16,tuple(3<<(2*j) for j in range(8)))
    donor=exact.reference.perpendicular((7,),16)[:8]
    add('canonical-to-right',16,donor,(7,))
    files=[Path(__file__),Path(producer.__file__),Path(exact.__file__),Path(exact.reference.__file__)]
    return dict(schema='right-reflected-actual-frame-interface-v1',
                generated_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256={file.name:sha256(file.read_bytes()).hexdigest() for file in files},
                cases=cases,
                scope='Literal finite actual frame gauges and child interfaces; no native stock, payload or exponent certificate.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    fixture=make_fixture()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(fixture,indent=2)+'\n')
    print(json.dumps(dict(cases=len(fixture['cases']),output=str(args.output),
                         sha256=sha256(args.output.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    main()
