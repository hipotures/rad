#!/usr/bin/env python3
"""Bounded exact four-flag constructor/operator and obstruction controls.

This checks rational projectors, complete D matrices and good-prime reductions.
It does not certify native routing, child width, finite tape arrays or kappa.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

import idempotent_flag_completion as F


def probe():
    tasks=((4,20261009171),(6,20261009172),(10,20261009173),(12,20261009174))
    rows=[F.probe(task) for task in tasks]
    static=F.static_paired_control()
    if sum(len(row['cases']) for row in rows)!=24:
        raise AssertionError('The exact flag case count changed')
    if sum(row['good_prime_power_complete_matrix_controls'] for row in rows)!=132:
        raise AssertionError('The good-denominator modular case census changed')
    if static['minimum_projector_G_self_adjoint'] or (static['minimum_rank'],static['maximum_rank'])!=(4,9):
        raise AssertionError('The nonselfadjoint paired-source obstruction changed')
    result=F.complete_flags([F.identity(3)[0]],F.identity(3),[],F.identity(3),3)
    corrupted=[list(row) for row in result['minimum_projector']]
    corrupted[0][0]+=Q(1,2)
    corrupted=tuple(tuple(row) for row in corrupted)
    if F.multiply(F.swap_block(corrupted),F.swap_block(corrupted))==F.identity(6):
        raise AssertionError('A nonidempotent frame passed the complete D involution')
    if F.good_reduction(((Q(1,5),),),25) is not None:
        raise AssertionError('A nonunit local-ring denominator was accepted')
    return dict(status='PASS GENERAL IDEMPOTENT FLAG BOUNDED CONTROLS',tasks=tasks,
                exact_flag_cases=24,good_prime_power_matrix_cases=132,static=static,
                additional_negative_controls=['nonidempotent_complete_D','nonunit_local_ring_denominator'],
                scope='Rational/field flag theorem controls and complete matrix identities; no native or exponent')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('A fresh optional output is required')
    sources=(Path(__file__).resolve(),Path(F.__file__).resolve(),Path(F.R.__file__).resolve())
    before={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}
    receipt=probe()
    if before!={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}:
        raise AssertionError('The effective flag source closure changed')
    receipt.update(source_closure=before,verified_utc=datetime.now(timezone.utc).isoformat(),stdlib_only=True)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'])


if __name__=='__main__':
    main()
