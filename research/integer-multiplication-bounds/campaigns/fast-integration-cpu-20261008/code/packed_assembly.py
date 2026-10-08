#!/usr/bin/env python3
"""Exact exponent arithmetic for the proposed packed conditional transfer.

No finite primitive or all-size physical contract is proved by this checker.
Unlike deleting rows from an old assembly, all changed rows are named here.
"""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path


def assembly(a, b, eps, q, kappa, beta=F(1, 20), *, guarded_crt=False, zeta=F(1,1000)):
    tau, sigma, lp = 1 - a, 1 - b, 1 - q
    internal = tau + (1 - beta) * max(sigma - tau, F(0))
    leaf = sigma + beta * (1 - sigma)
    lam = (max(tau, sigma, internal, leaf) + lp) / 2
    # Exponents relative to b=ceil(log2 n); polylog(b) needs strict gaps.
    cost_exponents = dict(
        completed_fft=1 - eps * q,
        coordinate_routing=tau,
        triangular_controlled_crt=tau if guarded_crt else eps,
        suffix_ring_product=1 - eps,
        packed_recursive_children=eps * (1 - kappa),
        sparse_repair_sorting=1 - 2 * eps,
        phase_band_lu=-eps+18*eps*zeta,
        regular_free_axis_band_lu=-2*eps+18*eps*zeta,
        source_elementary_phase=18*eps*zeta,
        scalar_polynomial_window_arithmetic=F(0),
        linear_scans=F(0),
    )
    target = 1 - kappa
    strict = dict(
        bit_saving=a, complex_saving=b, complex_above_bit=b-a,
        zeta_positive=zeta,zeta_below_one_eighth=F(1,8)-zeta,
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
        crt_inverse_metadata=18*eps-4,
        crt_bank_and_suffix_growth=1-eps,
    )
    strict.update({name+'_below_target': target-exponent
                   for name, exponent in cost_exponents.items()})
    failures={k:str(v) for k,v in strict.items() if v<=0}
    controls = dict(
        retained_full_axis_gaussian=target-eps,
        retained_per_level_reserved_axes=target-eps,
        old_short_digit_chirp_capacity=1-(F(1,2)+2*eps),
        old_compact_geometry=1-eps*(1+q),
    )
    return dict(parameters=dict(a_bit=a, a_complex=b, epsilon=eps, q=q,
                                 kappa=kappa, beta=beta, zeta=zeta,tau=tau, sigma=sigma,
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
                    'fixed elementary-function exponent zeta, including one source phase per coefficient',
                ],
                arithmetic_pass=not failures, failed_slacks=failures,
                proof_status='exact arithmetic only; all-size premises reviewed separately',
                crt_correction=('New independently reviewed guarded-reflection CRT tree pays the rotations.' if guarded_crt else
                                'The known-coordinate router does not replace d controlled modular CRT rotations.'),
                guarded_crt=guarded_crt)


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
    rejected=assembly(a,F(717,10000000),F(999999,1000000),
                      a*F(999999,1000000),a*F(99999,100000))
    assert not rejected['arithmetic_pass']
    assert set(rejected['failed_slacks'])=={'triangular_controlled_crt_below_target'}
    h=F(1,100000000)
    q=a*(1-h)
    balanced=assembly(a,F(717,10000000),(1-h)/(1+q),q,
                      a/(1+a)*F(9999999,10000000))
    assert balanced['arithmetic_pass']
    assert balanced['gain_over_old_supremum']<0
    guarded=assembly(a,F(717,10000000),F(999999,1000000),
                     a*F(999999,1000000),a*F(99999,100000),guarded_crt=True)
    assert guarded['arithmetic_pass']
    assert guarded['gain_over_old_supremum']>0
    result=dict(rejected_near_primitive_candidate=rejected,
                corrected_balanced_arithmetic=balanced,
                new_guarded_crt_composition=guarded,
                scientific_conclusion='Old triangular CRT preserves a/(1+a); the new guarded-reflection tree supports a written conditional composition approaching a, subject to the separately reviewed all-size proofs and named native premises.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps(encode(dict(rejected_crt_slack=rejected['failed_slacks'],
                                 corrected_smallest_slack=balanced['smallest_slack'],
                                 corrected_kappa=balanced['parameters']['kappa']))))


if __name__=='__main__':
    main()
