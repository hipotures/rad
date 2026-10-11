#!/usr/bin/env python3
"""Adversarial array check of a proposed signal-only terminal gauge transfer.

The displayed ridge hypothesis is true for restricted ridge arrays. It is not
part of the inherited arbitrary-array input contract. A delta-address array
gives a compact counterexample without allocating the exponential address set.
This does not reject other dense compilers or a new fully paid scatter word.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys


def reduce_matrix(M, prime):
    return [[x.numerator * pow(x.denominator % prime, -1, prime) % prime
             for x in row] for row in M]


def product(M, x, prime):
    return tuple(sum(a * b for a, b in zip(row, x)) % prime for row in M)


def partial_swap(P, address, prime):
    h = len(P)
    H, D = address[:h], address[h:]
    delta = product(P, tuple((d - a) % prime for a, d in zip(H, D)), prime)
    return tuple((a + t) % prime for a, t in zip(H, delta)) + tuple(
        (d - t) % prime for d, t in zip(D, delta))


def shear(P, address, prime):
    h = len(P)
    H, D = address[:h], address[h:]
    delta = product(P, D, prime)
    return tuple((a + t) % prime for a, t in zip(H, delta)) + tuple(D)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    geometry_code = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
    sys.path.insert(0, str(geometry_code))
    from review_positive_physical_profiles import projector
    rows = []
    prime = 101
    for h, beta in [(23, F(1, 15)), (25, F(7, 207))]:
        star = (1 - 9 * beta) / (9 * (1 - h * beta))
        U, T = {0, 1, 2}, {0, 3, 4}
        assert len(U & T) == 1
        primal_U = [F(i in U) - 3 * beta for i in range(h)]
        primal_T = [F(i in T) - 3 * beta for i in range(h)]
        dual_U = [(F(i in U) - 3 * star) / 2 for i in range(h)]
        assert sum(x * y for x, y in zip(dual_U, primal_U)) == 1
        assert sum(x * y for x, y in zip(dual_U, primal_T)) == 0
        basis = f'beta:{beta.numerator}:{beta.denominator}'
        gamma_symbols = list(range(2, h + 2))
        gamma_symbols[0] = 1
        kernel_symbols = gamma_symbols[:]
        kernel_symbols[4] = -kernel_symbols[3]
        Gamma = projector(h, 1, gamma_symbols, basis)
        K = projector(h, 1, kernel_symbols, basis)
        PT = projector(h, sum(1 << i for i in T), [int(i in T) for i in range(h)], basis)
        assert [[x - y for x, y in zip(a, b)] for a, b in zip(Gamma, K)] == PT
        g, k, t = (reduce_matrix(M, prime) for M in [Gamma, K, PT])
        a0 = tuple([1] + [0] * (2 * h - 1))
        changed = partial_swap(t, a0, prime)
        assert changed != a0
        out_gamma = partial_swap(g, a0, prime)
        out_kernel = partial_swap(k, a0, prime)
        assert out_gamma != out_kernel
        assert partial_swap(k, changed, prime) == out_gamma
        assert partial_swap(g, out_gamma, prime) == a0
        assert partial_swap(k, out_gamma, prime) != a0
        # The proposed primitive orthogonality does prove the restricted claim.
        dual = [x.numerator * pow(x.denominator % prime, -1, prime) % prime for x in dual_U]
        ridge_address = lambda x: (sum(d * z for d, z in zip(dual, x[:h])) % prime,
                                   sum(d * z for d, z in zip(dual, x[h:])) % prime)
        assert ridge_address(changed) == ridge_address(a0)
        # A true arbitrary source is a full-address delta, not this ridge.
        theta = lambda x: int(tuple(x) == a0)
        assert theta(a0) == 1 and theta(changed) == 0
        q_point = tuple([0, 1] + [0] * (2 * h - 2))
        dirty = lambda x: int(tuple(x) in {a0, q_point})
        old = dirty(partial_swap(g, out_gamma, prime))
        new = old ^ theta(partial_swap(g, out_gamma, prime))
        dirty_echo = old ^ new
        desired_kernel_value = theta(partial_swap(k, out_gamma, prime))
        assert dirty_echo == 1 and desired_kernel_value == 0
        # The older pinned rational-shear interface also admits the same defect.
        shear_point = tuple([0] * h + [1] + [0] * (h - 1))
        assert shear(t, shear_point, prime) != shear_point
        rows.append({'h': h, 'beta': str(beta), 'common': 0,
                     'input_source': sorted(U), 'terminal_source': sorted(T),
                     'displayed_projector_prime': prime, 'primitive_orthogonality': 'PASS',
                     'Gamma_minus_K_equals_terminal_source_projector': 'PASS',
                     'restricted_ridge_invariance': 'PASS',
                     'arbitrary_delta_array_invariance': 'FAIL',
                     'logical_delta_address': a0,
                     'source_reflection_changed_address': changed,
                     'Gamma_output_address': out_gamma, 'K_output_address': out_kernel,
                     'dirty_echo_value_at_Gamma_output': dirty_echo,
                     'required_K_signal_value_at_Gamma_output': desired_kernel_value,
                     'dirty_echo_cancels_arbitrary_old_value_but_not_signal_frame_defect': True,
                     'rational_shear_delta_control': 'FAIL INVARIANCE'})
    files = ['upstream/build/sections/03-motifs.tex',
             'notes/endpoint-gauge-construction.tex', 'notes/copied-centers-lemma.tex']
    receipt = {'utc': datetime.now(timezone.utc).isoformat(),
               'status': 'FALSIFIED SIGNAL-ONLY DENSE TERMINAL TRANSFER UNDER INHERITED ARBITRARY-ARRAY CONTRACT',
               'source_revision': 'ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
               'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'public_source_files': {p: hashlib.sha256((args.snapshot / p).read_bytes()).hexdigest() for p in files},
               'contract_locations': {'arbitrary_array_and_invertible_logical_interpretation': 'upstream/build/sections/03-motifs.tex:147-185',
                                      'rational_address_shear': 'upstream/build/sections/03-motifs.tex:475-486',
                                      'unchanged_data_terminal_gauges': 'notes/endpoint-gauge-construction.tex:162-168',
                                      'copies_include_complete_role_stream': 'notes/copied-centers-lemma.tex:30-38'},
               'controls': rows,
               'conclusion': 'Orthogonality of address vectors does not restrict arbitrary wire arrays to ridge functions. A single legal neighbor source with a delta-address array leaves a nonzero terminal gauge defect after exact dirty cancellation.',
               'scope': 'This falsifies the proposed source-restriction justification, not every possible dense compiler. A different fully charged scatter/endpoint word, or a proved lossless restricted-source encoding with its complete volume and restoration costs, could require a separate investigation.',
               'remaining_checks': 'This compact counterexample does not certify an alternative network or compute its exponent.',
               'attribution': ['OpenAI original preprint', 'Avi Eisenberg (PR62)', 'eumemic (PR57)',
                               'Alejandro Zarzuelo Urdiales (PR61)', 'Inherited source contributors and independent frame research.']}
    args.output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': receipt['status'], 'axes_checked': [row['h'] for row in rows],
                      'ridge_controls': 'PASS', 'arbitrary_delta_controls': 'FAIL INVARIANCE'}), flush=True)


if __name__ == '__main__':
    main()
