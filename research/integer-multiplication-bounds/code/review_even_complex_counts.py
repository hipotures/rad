#!/usr/bin/env python3
"""Independent exact count/log audit after a complete even-ground frame replay."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path


def log_interval(x, terms=64):
    assert 1 <= x <= 2
    z = (x-1)/(x+1)
    lo = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(terms)), Q(0))
    return lo, lo+2*z**(2*terms+1)/((2*terms+1)*(1-z*z))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--independent-frames', type=Path, required=True)
    parser.add_argument('--saving', type=Q, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    candidate = json.loads(args.candidate.read_text())
    frames = json.loads(args.independent_frames.read_text())
    h = candidate['h']
    assert h >= 8 and h % 2 == 0
    independent = next(row for row in frames['rows'] if row['h'] == h)
    v, m, R = comb(h, 3), h**3, independent['roles']
    N = v**3
    L = 3*v*v*h*(h+1)
    W = 2*N+2*v*v*(R+h+1)
    D = 2*N-2*L
    s = W*m-D
    assert D > 0 and 2 <= s < m**5
    eta = Q(D, W*m)
    counts = dict(h=h, v=v, m=m, N=N, R=R, W=W, L=L, D=D, s=s, eta=eta)
    assert all(Q(candidate['shared_complex_counts'][k]) == value for k, value in counts.items())
    assert R == candidate['logical']['active_additions']+2*v
    audit = independent['frames']
    assert audit['exact_output_nonzero_coefficients'] == candidate['logical']['nonzero_side_coefficients']
    assert audit['independent_logical_frames'] == v+candidate['logical']['active_additions']
    assert audit['source_lines_and_exact_target_kernels'] and audit['reverse_complements_isometric']
    assert independent['even_stage_matching']['images'] == v
    assert independent['even_stage_matching']['every_join_has_middle_coordinate_norm_one_witness']
    E = 64*(W+m+1)**3
    gates = 3*v*v*(4*R+4)
    assert gates < 6*W and 12*W**3+4*s+4*W+4 < E
    assert E == candidate['guard']['additive_guard_E']
    power = m.bit_length()-1
    lo2, hi2 = log_interval(Q(2))
    lo, hi = log_interval(Q(m, 2**power))
    lm_lo, lm_hi = power*lo2+lo, power*hi2+hi
    deficit_lo, deficit_hi = log_interval(1/(1-eta))
    primitive_lo, primitive_hi = deficit_lo/lm_hi, deficit_hi/lm_lo
    assert 0 < args.saving < primitive_lo < primitive_hi < 1
    assert Q(candidate['saving_enclosure']['saving_lower']) < primitive_lo
    assert primitive_hi < Q(candidate['saving_enclosure']['saving_upper'])
    value = dict(status='PASS independent exact even-ground finite count and primitive audit',
                 counts={key:str(x) if isinstance(x,Q) else x for key,x in counts.items()},
                 simple_supported_saving=str(args.saving),
                 strict_saving_slack=str(deficit_lo-args.saving*lm_hi),
                 primitive_lower=str(primitive_lo), primitive_upper=str(primitive_hi),
                 logarithm_terms=64, retained_additive_guard_E=E,
                 grouped_gates=gates, grouped_gate_slack=6*W-gates,
                 coefficient_guard_slack=E-(12*W**3+4*s+4*W+4),
                 source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                 input_sha256={str(p):sha256(p.read_bytes()).hexdigest()
                               for p in (args.candidate,args.independent_frames)},
                 scope='Exact count/log consequences of the unchanged reviewed even-ground scalar/frame/phase proof; the complete compact transfer is a separate dependency')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print('PASS even complex h',h,'roles',R,'simple saving',args.saving)


if __name__ == '__main__':
    main()
