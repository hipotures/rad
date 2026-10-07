#!/usr/bin/env python3
"""Exact p,q,p tensor-network composition and retained Gaussian-LU scoring.

The first and third tensor axes have the same circuit, while the middle axis
may differ. Shared scratch uses the middle-axis orthogonality matching.
Finite scalar tests establish restoration; the report supplies the separate
rational frame and rank transfer. Scores retain the complex h=50 motif.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import time

from downstream_gaussian import BASELINE_KAPPA, check_sources
from downstream_parameter_optimum import (as_strings, compact_lower,
                                          rational_decimal_lower, root_enclosure,
                                          saving_enclosure)
from frame_envelope import labels, target_check
from frame_reuse import optimize_chains, compile_reuse, check
from frame_reuse_certificate import program, counted_network


def counts(p, q, rp, rq):
    assert p >= 6 and q >= 6 and p % 2 == q % 2 == 0
    vp, vq, m = comb(p, 3), comb(q, 3), p*p*q
    n = vp*vp*vq
    w = 2*n + vp*vq*(rp+p) + vp*vp*(rq+q)
    loss = 2*vp*vq*p*p + vp*vp*q*q
    deficit = n-2*loss
    return dict(p=p, q=q, vp=vp, vq=vq, N=n, m=m,
                outer_side_roles=rp, middle_side_roles=rq,
                W=w, L=loss, D=deficit, s=w*m-deficit,
                eta=Q(deficit, w*m),
                joined_scratch_roles=vp*vq*(rp+p))


def complex_counts():
    v, m = comb(50, 3), 50**3
    n = v**3
    z = comb(47, 3)+3*47
    w = 2*n+3*v*v*(v*z+51)
    loss = 3*v*v*51*50
    s = w*m-2*n+2*loss
    return dict(ground=50, v=v, N=n, m=m, W=w, L=loss, s=s,
                eta=Q(w*m-s, w*m))


def score(n, ec):
    assert n['D'] > 0 and 2 <= n['s'] < n['m']**5
    eb = saving_enclosure(n['eta'], n['m'])
    a, b = eb['chosen_saving'], ec['chosen_saving']
    xlo, xhi = root_enclosure(a, b)
    beta = 1-xhi
    tau, sigma = 1-a, 1-b
    c = a*beta/(tau+a*beta)*(1-Q(1, 2**32))
    lamp = 1-a*c
    threshold = tau*(1+c/beta)
    lam = (lamp+threshold)/2
    epsilon, r, delta, c1 = Q(2, 3)-Q(1, 2**20), Q(1, 3), Q(1, 2**22), Q(3, 2)
    margins = dict(g1=1-epsilon*(1+c), g2=epsilon*c*a,
                   g3=epsilon*(1-lamp), g4=a*(1-epsilon),
                   g5=Q(1, 2)+r/2-delta-epsilon,
                   g6=1-delta-epsilon, g7=epsilon)
    minimum = min(margins.values())
    kappa = compact_lower(minimum)
    slacks = dict(bit_primitive=eb['strict_primitive_gap'],
                  complex_primitive=ec['strict_primitive_gap'],
                  lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
                  packed_recurrence=lam-threshold,
                  lambda_prime_above_lambda=lamp-lam,
                  leaf_cost=lamp-(sigma+beta*(1-sigma)),
                  guard=1-c1*epsilon, guard_stopping_range=beta-Q(15, 16),
                  gaussian_cost=Q(1, 2)+r/2-delta-epsilon,
                  gamma_sublinear=1-epsilon-r,
                  prime_interval_and_line_growth=1-epsilon,
                  prefix_cost=1-epsilon*(1+c), scalar_cost=1-delta-epsilon,
                  K_smaller_than_ell=1-epsilon-epsilon*c,
                  absorption=minimum-kappa)
    assert all(v > 0 for v in slacks.values())
    assert minimum == margins['g2'] == margins['g3']
    _, upper_root = root_enclosure(eb['saving_upper'], ec['saving_upper'])
    ceiling = Q(2, 3)*ec['saving_upper']*upper_root
    assert kappa < ceiling
    nc = complex_counts()
    guard_b = nc['s']+64*(nc['W']+nc['m']+1)**3
    return dict(status='Conditional composition score; independent frame/rank and analytic review required',
                counts=n, bit_saving_enclosure=eb,
                retained_complex_counts=nc, complex_saving_enclosure=ec,
                balance_root_interval=[xlo, xhi],
                parameters=dict(tau=tau, sigma=sigma, a_bit=a, a_complex=b,
                                beta=beta, c=c, lambda_=lam, lambda_prime=lamp,
                                epsilon=epsilon, delta=delta, alpha_squared_power=r,
                                C1=c1, C0=128*nc['m']*guard_b**2, kappa=kappa),
                margins=margins, constraint_slacks=slacks, minimum_margin=minimum,
                kappa_decimal_lower=rational_decimal_lower(kappa, 30),
                kappa_ratio_to_baseline=kappa/BASELINE_KAPPA,
                kappa_ratio_decimal_lower=rational_decimal_lower(kappa/BASELINE_KAPPA, 12),
                model_kappa_upper=ceiling, gamma_cutoff='b >= 2^7340032')


def scalar_exchange(p, q, seed, outer, middle, matching):
    from dag_network import invoke
    vp, vq, rp, rq = len(outer['triples']), len(middle['triples']), outer['roles'], middle['roles']
    assert vp == comb(p, 3) and vq == comb(q, 3)
    inverse = [0]*vq
    for i, image in enumerate(matching):
        inverse[image] = i
    assert sorted(matching) == list(range(vq))
    n = vp*vp*vq
    def payload(i):
        return ((i*2654435761+seed*2246822519) ^ (i*i*97)) & 0xffffffff
    x = [payload(i) for i in range(n)]
    y = [payload(n+i) for i in range(n)]
    shared_size = vp*vq*(rp+p)
    shared = [payload(2*n+i) for i in range(shared_size)]
    inner = [payload(2*n+shared_size+i) for i in range(vp*vp*(rq+q))]
    before = [list(z) for z in (x, y, shared, inner)]
    def flat(a, b, c):
        return (a*vq+b)*vp+c
    for stage in range(3):
        va, vb = (vq, vp) if stage == 0 else (vp, vp) if stage == 1 else (vp, vq)
        code, h, roles = (middle, q, rq) if stage == 1 else (outer, p, rp)
        for a in range(va):
            for b in range(vb):
                indices = [flat(t, a, b) if stage == 0 else flat(a, t, b) if stage == 1
                           else flat(a, b, t) for t in range(len(code['triples']))]
                bank = inner if stage == 1 else shared
                base = ((a*vb+b) if stage < 2 else (inverse[b]*vp+a))*(roles+h)
                scratch = bank[base:base+roles]
                center = bank[base+roles:base+roles+h]
                source = y if stage == 1 else x
                target = x if stage == 1 else y
                xx, yy = [source[i] for i in indices], [target[i] for i in indices]
                invoke(xx, yy, scratch, center, code, inverse=(stage == 1))
                for i, s, t in zip(indices, xx, yy):
                    source[i], target[i] = s, t
                bank[base:base+roles+h] = scratch+center
    assert x == before[1] and y == before[0]
    assert shared == before[2] and inner == before[3]
    ncounts = counts(p, q, rp, rq)
    assert ncounts['W'] == 2*n+len(shared)+len(inner)
    return dict(p=p, q=q, seed=seed, payload_bits=32,
                data_roles=2*n, shared_roles=len(shared), middle_roles=len(inner),
                bank_exchange=True, dirty_scratch_restored=True,
                model='Exact bit scalar operation with arbitrary deterministic dirty payloads')


def join_certificate(p, q, matching):
    from itertools import combinations
    tq = list(combinations(range(q), 3))
    assert len(matching) == len(tq) and len(set(matching)) == len(tq)
    assert all(len(set(t)&set(tq[j])) == 1 for t, j in zip(tq, matching))
    m = p*p*q
    assert m-2*p >= 0
    return dict(p=p, q=q, matching_ground=q,
                orthogonal_matching_pairs=len(tq), joined_invocation_banks=comb(p, 3)*comb(q, 3),
                tail_dimension=p, head_dimension=m-p,
                removed_two_edges_rank=2*(m-p), joined_edge_rank=m-2*p,
                rank_saved_per_join=m,
                proof='E=F_p tensor t_A tensor t_B is contained in H=(t_B tensor t_pi_q(A))^perp tensor F_p',
                nondegeneracy='Ambient I-J/9 nondegenerate for p,q!=9; every triple line has norm 2')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, required=True)
    parser.add_argument('--ground-results', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--small-pairs', nargs='+', default=['6,8', '8,6'])
    args = parser.parse_args()
    started = time.monotonic()
    provenance = check_sources(args.upstream)
    sys.path.insert(0, str(args.upstream.resolve()/'scripts'))
    from paired_exclusion_circuit import PairedExclusionCircuit
    from finite_block_search import GroupUnion
    from dag_network import exact_invocation
    from reuse_network import triple_matching
    cache, checks, exchanges = {}, [], []
    pairs = [tuple(map(int, pair.split(','))) for pair in args.small_pairs]
    for h in sorted({h for pair in pairs for h in pair}):
        circuit = GroupUnion(h, PairedExclusionCircuit, ordering='paired')
        graph = circuit.verify()
        frames, metadata = labels(circuit, True)
        compiled = compile_reuse(circuit, frames, optimize_chains(circuit, frames, 'rank'))
        checked = check(circuit, frames, compiled)
        targets = target_check(circuit, frames, True)
        scalar = program(circuit, compiled)
        triples, matching = triple_matching(h)
        assert triples == scalar['triples']
        cache[h] = scalar, matching
        checks.append(dict(h=h, graph=graph, frames=metadata, finite=checked, targets=targets,
                           dirty_basis=[exact_invocation(h, inverse, scalar) for inverse in (False, True)]))
    for p, q in pairs:
        for seed in (1, 109):
            exchanges.append(scalar_exchange(p, q, seed, cache[p][0], cache[q][0], cache[q][1]))
        print(json.dumps(dict(phase='asymmetric scalar', p=p, q=q, passed=True)), flush=True)
    raw_scan = json.loads(args.ground_results.read_text())
    roles = {int(c['h']):int(c['roles']) for c in raw_scan['cases'] if c['return_code'] == 0}
    assert len(roles) == len(raw_scan['cases'])
    assert 50 not in roles
    roles[50] = 486200
    ec = saving_enclosure(complex_counts()['eta'], complex_counts()['m'])
    candidates = []
    for p, rp in sorted(roles.items()):
        for q, rq in sorted(roles.items()):
            n = counts(p, q, rp, rq)
            if p == q:
                equal = counted_network(p, rp)
                assert all(n[key] == equal[key] for key in ('N', 'm', 'W', 'L', 'D', 's', 'eta'))
            if n['D'] > 0 and n['s'] < n['m']**5:
                candidates.append(score(n, ec))
    candidates.sort(key=lambda c:c['parameters']['kappa'], reverse=True)
    best = candidates[0]
    p, q = best['counts']['p'], best['counts']['q']
    _, matching = triple_matching(q)
    joins = [join_certificate(a, b, cache[b][1]) for a, b in pairs]
    joins.append(join_certificate(p, q, matching))
    result = dict(campaign_id='20261007T222521Z', generated_at=datetime.now(timezone.utc).isoformat(),
                  provenance=provenance,
                  sources_sha256={path.name:sha256(path.read_bytes()).hexdigest() for path in
                       (Path(__file__), Path(__file__).with_name('frame_envelope.py'),
                        Path(__file__).with_name('frame_reuse.py'), args.ground_results)},
                  source_ground_protocol=raw_scan['protocol'], verified_role_counts=roles,
                  small_circuit_checks=checks, scalar_exchanges=exchanges,
                  joining_certificates=joins, best=best,
                  ranking=[dict(p=c['counts']['p'], q=c['counts']['q'], m=c['counts']['m'],
                                roles_outer=c['counts']['outer_side_roles'],
                                roles_middle=c['counts']['middle_side_roles'],
                                eta=c['counts']['eta'], kappa=c['parameters']['kappa'],
                                baseline_ratio=c['kappa_ratio_decimal_lower']) for c in candidates],
                  elapsed_seconds=time.monotonic()-started,
                  verification_boundary='Full scalar calibration at two unequal small pairs; full individual graph/frame checks at large grounds; symbolic tensor frame/rank transfer requires independent written review; Gaussian LU remains conditional on retained upstream interfaces.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result), indent=2)+'\n')
    print(json.dumps(as_strings(dict(best_p=p, best_q=q, kappa=best['parameters']['kappa'],
                                   ratio=best['kappa_ratio_decimal_lower'], elapsed_seconds=result['elapsed_seconds']))), flush=True)


if __name__ == '__main__':
    main()
