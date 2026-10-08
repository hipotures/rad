#!/usr/bin/env python3
"""Exact exponent arithmetic for the proposed packed conditional transfer.

No finite primitive or all-size physical contract is proved by this checker.
Unlike deleting rows from an old assembly, all changed rows are named here.
"""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path


def assembly(a, b, eps, q, kappa, beta=F(1, 20)):
    tau, sigma, lp = 1 - a, 1 - b, 1 - q
    internal = tau + (1 - beta) * max(sigma - tau, F(0))
    leaf = sigma + beta * (1 - sigma)
    lam = (max(tau, sigma, internal, leaf) + lp) / 2
    # Exponents relative to b=ceil(log2 n); polylog(b) needs strict gaps.
    cost_exponents = dict(
        completed_fft=1 - eps * q,
        coordinate_routing=tau,
        selected_bit_crt=tau,
        suffix_ring_product=1 - eps,
        packed_recursive_children=eps * (1 - kappa),
        sparse_repair_sorting=1 - 2 * eps,
        phase_band_lu=-eps,
        scalar_polynomial_window_arithmetic=F(0),
        linear_scans=F(0),
    )
    target = 1 - kappa
    strict = dict(
        bit_saving=a, complex_saving=b, complex_above_bit=b-a,
        beta_positive=beta, beta_below_one=1-beta,
        epsilon_above_half=eps-F(1,2), epsilon_below_one=1-eps,
        q_positive=q, q_below_bit=a-q,
        q_below_complex_leaf=(1-beta)*b-q,
        lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal, lambda_above_leaf=lam-leaf,
        lambda_prime_above_lambda=lp-lam, lambda_prime_below_one=q,
        positive_kappa=kappa, kappa_below_one=1-kappa,
        metadata_guard=18*eps-(2*eps+2),
        inverse_phase_window_gap=F(12)-F(17,2),
        forward_tensor_chirp_gap=F(18)-F(9),
        tensor_diagonal_prefix_depth=18*eps-eps,
        catalogue_cell_growth=eps-(1-eps),
    )
    strict.update({name+'_below_target': target-exponent
                   for name, exponent in cost_exponents.items()})
    assert all(v>0 for v in strict.values()), {k:str(v) for k,v in strict.items() if v<=0}
    controls = dict(
        retained_full_axis_gaussian=target-eps,
        retained_per_level_reserved_axes=target-eps,
        old_short_digit_chirp_capacity=1-(F(1,2)+2*eps),
        old_compact_geometry=1-eps*(1+q),
    )
    assert all(v<0 for v in controls.values())
    return dict(parameters=dict(a_bit=a, a_complex=b, epsilon=eps, q=q,
                                 kappa=kappa, beta=beta, tau=tau, sigma=sigma,
                                 lambda_=lam, lambda_prime=lp),
                cost_exponents=cost_exponents, target_exponent=target,
                strict_slacks=strict, rejected_unchanged_controls=controls,
                smallest_slack=min(strict.values()),
                old_balanced_supremum=a/(1+a),
                gain_over_old_supremum=kappa-a/(1+a),
                theorem_premises=[
                    'native finite bit and complex moment/compiler contracts',
                    'semantic completed-child precision and product row stock',
                    'external-bank completed layers for independent b,d,Q',
                    'paid arbitrary coordinate and selected-bit CRT routers',
                    'exact joint monotone fractional gather and restore',
                    'rounded kernel construction and Gaussian approximation bounds',
                    'source-closed sparse repair and band-LU precision',
                    'terminating strong-induction recursive integer multiplication',
                    'prime, catalogue, setup and eventual exact recovery',
                ],
                proof_status='exact arithmetic only; all-size premises reviewed separately')


def encode(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {k:encode(v) for k,v in x.items()}
    if isinstance(x, list):
        return [encode(v) for v in x]
    return x


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    a=F(783777693,20000000000000)  # Public PR40 scientific head43f59ff5.
    result=assembly(a,F(717,10000000),F(999999,1000000),
                    a*F(999999,1000000),a*F(99999,100000))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps(encode(dict(kappa=result['parameters']['kappa'],
                                 smallest_slack=result['smallest_slack'],
                                 gain=result['gain_over_old_supremum']))))


if __name__=='__main__':
    main()
