#!/usr/bin/env python3
"""Exact scoped lower bound for literal complex front basis wrappers.

The written proof covers any ONE common binary address basis. This script
checks source identities, retained-front attribution and arithmetic; it
does not instantiate the inherited generic basis or synthesize its gates.
"""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as F
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path

PIN='43f59ff533598762cbc43a5e14af2bbbc76fabbd'
INPUTS=['notes/copied-centers-complex.tex','notes/copied-centers-lemma.tex',
        'notes/endpoint-gauge-complex.tex','notes/structured-bulk-complex.tex',
        'references/copied-centers/pr29/two-stage-16-note.tex']


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    assert not args.output.exists()
    inputs={p:dict(sha256=hashlib.sha256((args.source_root/p).read_bytes()).hexdigest(),
                         bytes=(args.source_root/p).stat().st_size) for p in INPUTS}
    first=(args.source_root/INPUTS[0]).read_text()
    lemma=(args.source_root/INPUTS[1]).read_text()
    stage=(args.source_root/INPUTS[4]).read_text()
    assert '4N_c&27' in first
    assert 'All exterior, data-front and endpoint-correction calls remain in place.' in lemma
    assert r'Y:0\to\operatorname{im}(I-P)\otimes\operatorname{im}Q' in stage
    h=28
    triples=[sum(1<<j for j in t) for t in combinations(range(h),3)]
    assert len(set(triples))==comb(h,3)
    assert all(t.bit_count()==3 and t.bit_count()%2==1 for t in triples)
    v=len(triples);m=h*h;N=v*v;R=78790;loss=h*(h-1)
    B=v*R;W=2*N+2*B;L=2*v*loss;s=W*m-N+L
    assert (W,s,N,L)==(537696432,421548223824,10732176,4953312)
    deficit=W*m-s
    allowed=(deficit-1)//2
    # A coordinate (h-1)-space consumes h-1 basis vectors in its K_Y.
    coordinate_Y_upper=m//(h-1)
    forced_noncoordinate_fronts=(v-coordinate_Y_upper)*v
    wrapper_additions_lower=2*forced_noncoordinate_fronts
    extra_child_rank_lower=2*wrapper_additions_lower
    rank_new_lower=s+extra_child_rank_lower
    assert coordinate_Y_upper==29
    assert wrapper_additions_lower > allowed and rank_new_lower > W*m
    receipt=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
                 source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 eligible_source=dict(repository='https://github.com/rohanarun/integer-mult-bounds',
                                      sha=PIN,files=inputs),
                 binary_address_field=True,h=h,v=v,m=m,N=N,W=W,original_rank=s,
                 original_deficit=deficit,strict_row_addition_upper=allowed,
                 retained_family='The first-stage Y:0 -> t_X^perp tensor t_Y front, once per actual (X,Y) pair',
                 retained_family_calls=N,front_rank=h-1,
                 pairwise_disjoint_line_ambient_spaces=v,
                 possible_coordinate_Y_upper=coordinate_Y_upper,
                 forced_noncoordinate_fronts_lower=forced_noncoordinate_fronts,
                 forward_inverse_basis_row_additions_lower=wrapper_additions_lower,
                 extra_C_children_rank_lower=extra_child_rank_lower,
                 revised_rank_lower=rank_new_lower,
                 revised_sigma1_moment_lower=str(F(rank_new_lower,W*m)),
                 revised_sigma1_excess_lower=str(F(rank_new_lower-W*m,W*m)),
                 status='SCOPED LITERAL-WRAPPER SELF-ROUTING EXCLUSION',
                 conditions=['One common global binary address basis',
                             'Each residual keeps its independently implemented input/output normal-form wrappers',
                             'Each nontrivial binary row addition is replaced by two extra native C children of width1 at its original role volume',
                             'Original child list and denominator W retained without cross-call fusion or cancellation'],
                 scope='A proved lower bound on one retained family, not a fabricated exact gate count. No globally shared/fused basis schedule or different self-routing algorithm is excluded.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','strict_row_addition_upper','forced_noncoordinate_fronts_lower','forward_inverse_basis_row_additions_lower','extra_C_children_rank_lower','revised_sigma1_excess_lower')}))


if __name__=='__main__':main()
