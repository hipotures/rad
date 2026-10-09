#!/usr/bin/env python3
"""Independent paired-cube histogram, interval-moment and 47+7 assembly audit.

No candidate Python is imported. Complete inventories and finite bridge formulas
are reconstructed from JSON inputs. Exact moment enclosures use 40 positive
atanh terms, nine-degree exp Taylor, rigorous tails and dyadic outward rounding.
This follows the supplied RaD arithmetic supplement's method; assembly equations
originate in the retained structured_bulk_assembly interface (icekylinx,
Zhihao Chen and RaD; Apache-2.0). Authored with OpenAI Codex assistance.

Finite network construction and inherited all-size transfer remain separate
obligations. A coherent false supplied inventory is not excluded by arithmetic.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import factorial, prod
from pathlib import Path
import sys
import time

DEN = 1 << 180


def need(condition, message):
    if not condition:
        raise ValueError(message)


def down(x):
    return Q(x.numerator*DEN//x.denominator, DEN)


def up(x):
    return Q(-((-x.numerator*DEN)//x.denominator), DEN)


def log_unit(x):
    need(1 <= x <= 2, 'log range')
    z = (x-1)/(x+1)
    low = sum((2*z**(2*k+1)/Q(2*k+1) for k in range(40)), Q(0))
    return down(low), up(low+2*z**81/(81*(1-z*z)))


def log_bounds(x):
    need(x >= 1, 'log argument')
    k = 0
    while x > 2:
        x /= 2; k += 1
    lo, hi = log_unit(x); l2, h2 = log_unit(Q(2))
    return down(lo+k*l2), up(hi+k*h2)


def exp_bounds(lo, hi):
    need(0 <= lo <= hi < 1, 'exp range')
    low = sum((lo**k/Q(factorial(k)) for k in range(10)), Q(0))
    high = sum((hi**k/Q(factorial(k)) for k in range(10)), Q(0))
    return down(low), up(high+hi**10/Q(factorial(10))/(1-hi/11))


def moment(m, W, hist, saving):
    lo = hi = Q(0)
    for width, count in hist.items():
        need(type(width) is int and type(count) is int and 0 < width < m and count > 0, 'child domain')
        l, h = log_bounds(Q(m, width)); el, eh = exp_bounds(saving*l, saving*h)
        weight = Q(width*count, m*W)
        lo += weight*el; hi += weight*eh
    return down(lo), up(hi)


def hist(value):
    return {int(k): v for k, v in value.items() if int(k) and v}


def js(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): js(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [js(v) for v in value]
    return value


def normalize_certificate(cert):
    """Map the placement certificate's inventory names to this audit interface.

    No moment endpoints, verification flags or saved verdict are consumed.
    Every mapped global count is independently re-derived below.
    """
    cert = deepcopy(cert)
    if 'local_dimension' not in cert['bit']['counts']:
        cert['bit']['counts']['local_dimension'] = cert['bit']['counts']['m']//3
    if 'vertices_per_stage' not in cert['complex']:
        global_counts = cert['finite_bridge']['complex']
        cert['complex'].update(vertices_per_stage=global_counts['invocations_per_stage'],
                               W=global_counts['W'], total_rank=global_counts['s'], N=global_counts['N'])
    return cert


def check(tree, cert, verify_sources=True, *, physical_override=None, bitrow_override=None):
    cert = normalize_certificate(cert)
    read = lambda path: json.loads((tree/path).read_text())
    bcount, ccount = cert['bit']['counts'], cert['complex']['counts']
    bitrow = bitrow_override if bitrow_override is not None else read('research/paired-cube-bit/out/profile_p%d.json' % (bcount['local_dimension']//2))
    complexrow = read('certificates/paired-cube-complex-input.json')
    physical = physical_override if physical_override is not None else read('certificates/paired-cube-physical-input.json')
    profiles = {}
    for axis, row, saved in [('bit', bitrow, bcount), ('complex', physical, ccount)]:
        m, W = 3*row['h'], row['W_per_vertex']
        H = Counter()
        local = 'remaining_internal_histogram' if axis == 'bit' else 'local_histogram'
        for part in (local, 'source_data_histogram', 'target_data_histogram'):
            H.update({int(r): 3*n for r, n in row[part].items() if int(r) and n})
        gauge = 'selected_rank_histogram' if axis == 'bit' else 'physical_gauge_histogram'
        H.update({3*int(r): n for r, n in row[gauge].items() if int(r) and n})
        H[2] += 2*row['v']
        rank = sum(r*n for r, n in H.items())
        need(dict(H) == hist(row['child_histogram']) == hist(saved['child_multiplicities']), axis+' complete histogram')
        need(m*W-rank == 2*row['v']-3*row['loss'] == row['deficit_per_vertex'], axis+' exact rank deficit')
        need((m, W, rank, max(H), sum(H.values())) ==
             (saved['m'], saved['W_per_vertex'], saved['rank_per_vertex'], saved['maxchild'], saved['edge_count']), axis+' counts')
        saving = Q(cert[axis]['coarse_saving'] if axis == 'bit' else cert[axis]['saving'])
        lower, upper = moment(m, W, H, saving)
        need(upper < 1, axis+' ideal moment')
        fallback = Q(0)
        if axis == 'bit':
            bad = Q(cert['bit']['bad_fraction']); need(bad == Q(1,10**16), 'bad fraction')
            need(cert['bit']['fallback_children_per_edge'] == 32*m*m, 'full fallback')
            l, h = log_bounds(Q(m)); _, e = exp_bounds(saving*l, saving*h)
            fallback = bad*Q(32*m*m*sum(H.values()), m*W)*e
            need(Q(2*m**3, 2**80) < bad, 'bad-prime bound')
            need(rank+bad*32*m*m*sum(H.values()) < m*W, 'contaminated rank')
            need(upper+fallback < 1, 'contaminated bit moment')
        profiles[axis] = dict(m=m, W=W, rank=rank, saving=saving,
                              moment_lower=lower, moment_upper=upper,
                              ideal_gap_lower=1-upper, full_gap_lower=1-upper-fallback,
                              full_gap_decimal=float(1-upper-fallback))
        if axis == 'complex' and 'successor_grid' in cert['complex']:
            successor = Q(cert['complex']['successor_grid']['saving'])
            need(successor == saving+Q(1,10**12), 'complex successor grid binding')
            next_lower, next_upper = moment(m, W, H, successor)
            need(next_lower > 1, 'complex successor grid rejection')
            profiles[axis].update(successor_saving=successor, successor_excess_lower=next_lower-1,
                                  successor_excess_decimal=float(next_lower-1))
    # Full finite-group, scalar expansion, precision guard and row reserve.
    m, Wv, rv = (ccount[k] for k in ('m','W_per_vertex','rank_per_vertex'))
    h, v, R = (complexrow[k] for k in ('h','v','R'))
    need(physical['physical_R'] == R-physical['pairs'], 'physical roles')
    need(Wv == 2*v+physical['physical_R'], 'physical width')
    n = m//2
    vertices = 2**(m-1+(n-1)**2)*prod(2**(2*i)-1 for i in range(1,n))
    W, rank, N = vertices*Wv, vertices*rv, vertices*v
    need((vertices,W,rank,N) == tuple(cert['complex'][k] for k in ('vertices_per_stage','W','total_rank','N')), 'full global counts')
    local = 4*(complexrow['c']+v)+10*v+4*h*v+4*h*h+8*h+8+2*h
    local += 8*R*v*(complexrow['total_M_operations']+16)+32*v
    logical = 3*vertices*local+8*W+4*N+8*m*R*vertices
    G = 64*(m+1)**3*(logical+1)*(W+1)**2
    E = 64*(W+m+G+1)**3
    charge = 2*G*W*W+8*rank+4*W+4+32*m
    B, C0, maximum = rank+E, 32*m*(rank+E)**2, ccount['maxchild']
    d = 1
    while m**d <= 2*maximum**d:
        d += 1
    coefficient = d*W.bit_length()+9909+252
    degree = 70000
    degree_gap = Q(degree)-Q(51*coefficient,25)
    bridge = cert['finite_bridge']
    need(charge < E and 2*B*(m-maximum) >= rank+E and 2*B+18 < C0 and degree_gap > 0, 'finite bridge inequalities')
    need((local,logical,G) == tuple(bridge['complex'][k] for k in ('local_group_upper','logical_group_upper','finite_group_router_upper')), 'expanded scalar/router charge')
    need((E,charge,E-charge,B,C0,2*B*(m-maximum)-rank-E) == tuple(bridge['semantic'][k] for k in
         ('E','literal_charge','strict_literal_gap','B','C0','induction_gap')), 'semantic charge')
    need((coefficient, degree, str(degree_gap)) == (bridge['rows']['coefficient'],bridge['rows']['degree'],bridge['rows']['degree_gap']), 'row stock')
    # Re-derive every assembly parameter and all 47 strict constraints.
    p = {k: Q(value) for k, value in cert['assembly']['parameters'].items()}
    a,b,beta,eta,kappa = (p[k] for k in ('a_bit','a_complex','beta','eta','kappa'))
    atom = Q(cert['bit']['atom_exponent']); old = Q(cert['bit']['ordinary_leaf_saving'])
    actual = (1-atom)*Q(cert['bit']['coarse_saving'])+atom*old
    need(actual == p['actual_bit_saving'] == Q(cert['bit']['effective_saving']), 'ordinary bit saving')
    need(a <= actual and atom > actual and atom < 1-actual, 'stopped adapter/ordinary support')
    need(b == Q(cert['complex']['saving']) and kappa == Q(cert['kappa']), 'component/assembly bindings')
    tau,sigma = 1-a,1-b
    q = a*(1-2*eta); lp = 1-q; lam = (tau+lp)/2
    c = q*(1+eta); eps = (1-eta)/(1+c+q)
    minimum = eps*q; r = (minimum+1-eps)/2; delta = eta/8
    internal = tau+(1-beta)*max(sigma-tau,Q(0)); leaf = sigma+beta*(1-sigma)
    expected_parameters = dict(a_bit=a, actual_bit_saving=actual, a_complex=b,
        tau=tau, sigma=sigma, eta=eta, beta=beta, q=q, c=c, epsilon=eps,
        lambda_=lam, lambda_prime=lp, alpha_squared_power=r, delta=delta,
        C0=Q(C0), C1=Q(1), kappa=kappa)
    need(p == expected_parameters, 'derived assembly parameter bindings')
    need({key:Q(value) for key,value in cert['assembly']['recurrence'].items()} ==
         dict(internal=internal, leaf=leaf, reservations=1-c), 'assembly recurrence bindings')
    need(Q(cert['complex']['exponent']) == 1-b, 'complex exponent binding')
    margins = dict(original_prefix=1-eps*(1+c),coordinate_movement=a,
        compact_phase_layer=minimum,bulk_exposure=a,
        Gaussian_arithmetic=min(1-eps-delta,r-delta),scalar_work=1-eps-delta,dimension=eps)
    slacks = dict(bit_positive=a,complex_above_bit=b-a,complex_below_one_over32=Q(1,32)-b,
        beta_positive=beta,beta_below_one=1-beta,leaf_saving_above_bit=(1-beta)*b-a,
        q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,c_positive=c,
        c_below_one=1-c,q_below_reservations=c-q,lambda_above_tau=lam-tau,
        lambda_above_sigma=lam-sigma,lambda_above_internal=lam-internal,
        lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-(1-c),
        lambda_prime_below_one=q,epsilon_positive=eps,epsilon_below_one=1-eps,
        guard_width=1-eps,K_geometry=1-eps*(1+c),K_dominates_log=eps*c,record_suffix=1-eps,
        phase_local=1-eps-delta,phase_boundary=r-delta,gamma_sublinear=1-eps-r,
        cell_above_band=eps-(1-r)/2,prime_interval_packing=1-eps,alpha_positive=r,
        alpha_below_one=1-r,alpha_below_one_fourth=Q(1,4)-r,delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta,short_record_fallback=eps-a,
        small_field_exposure=1-eps-minimum,artificial_boundary=8-eps+r-delta-minimum,
        literal_scalar_guard=Q(E-charge),row_product_gap=degree_gap)
    slacks.update({name+'_above_kappa': value-kappa for name,value in margins.items()})
    need(len(slacks) == 47 and len(margins) == 7 and all(value > 0 for value in slacks.values()), '47 strict constraints and 7 margins')
    need(slacks == {key:Q(value) for key,value in cert['assembly']['strict_constraints'].items()}, 'recomputed constraint values')
    need(margins == {key:Q(value) for key,value in cert['assembly']['margins'].items()}, 'recomputed margins')
    need(min(margins.values()) == minimum and margins['original_prefix']-minimum == eta, 'limiting margin identity')
    need(minimum == Q(cert['assembly']['minimum_margin']) and minimum-kappa == Q(cert['assembly']['absorption_gap']), 'strict absorption')
    source_count = 0
    if verify_sources:
        for name, digest in cert['source_sha256'].items():
            path = Path(name)
            need(not path.is_absolute() and '..' not in path.parts, 'unsafe source pin path')
            need(sha256((tree/path).read_bytes()).hexdigest() == digest, 'source pin differs: '+name)
            source_count += 1
    return dict(status='PASS_INDEPENDENT_SUPPLIED_INVENTORY_ARITHMETIC', kappa=kappa,
                profiles=profiles, recomputed_strict_constraints=len(slacks), recomputed_margins=margins,
                absorption_gap=minimum-kappa, source_files_checked=source_count,
                full_group_order_bits=vertices.bit_length(), row_coefficient=coefficient,
                scope='Independent complete inventory arithmetic, dyadic interval moments, full fallback, finite '
                      'router/scalar/precision/row charges and all 47+7 assembly values. Local physical derivation '
                      'and inherited all-size analytic/machine contracts remain separately required.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--certificate', type=Path)
    parser.add_argument('--physical', type=Path)
    parser.add_argument('--bit-profile', type=Path)
    parser.add_argument('--candidate-frames', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(not sys.flags.optimize, 'assertion-disabled execution rejected')
    sys.set_int_max_str_digits(0)
    started = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat()
    certificate_path = args.certificate or args.tree/'certificates/paired-cube-network.json'
    cert = json.loads(certificate_path.read_text())
    physical = json.loads(args.physical.read_text()) if args.physical else None
    bitrow = json.loads(args.bit_profile.read_text()) if args.bit_profile else None
    if args.candidate_frames:
        need(sha256(args.candidate_frames.read_bytes()).hexdigest() == cert['candidate_frames_sha256'],
             'candidate frame source pin differs')
    def audit(candidate):
        return check(args.tree, candidate, physical_override=physical, bitrow_override=bitrow)
    result = audit(cert)
    controls = {}
    mutated = deepcopy(cert)
    H = mutated['complex']['counts']['child_multiplicities']
    # Two moved children with unchanged count and rank mass.
    keys = sorted(int(key) for key in H)
    lo, middle, high = next((a,b,c) for a in keys for b in keys for c in keys
                            if a < b < c and a+c == 2*b and H[str(b)] >= 2)
    H[str(lo)] += 1; H[str(middle)] -= 2; H[str(high)] += 1
    for name, candidate in [('mass_preserving_histogram',mutated)]:
        try:
            audit(candidate)
        except ValueError as error:
            controls[name] = str(error)
        else:
            raise ValueError('mutation accepted: '+name)
    mutated = deepcopy(cert)
    first = next(iter(mutated['source_sha256']))
    mutated['source_sha256'][first] = '0'*64
    try:
        audit(mutated)
    except ValueError as error:
        controls['source_pin_corruption'] = str(error)
    else:
        raise ValueError('source corruption accepted')
    for name, field, value in [('derived_assembly_parameter', 'tau', '1'),
                              ('assembly_recurrence', 'internal', '1')]:
        mutated = deepcopy(cert)
        group = 'parameters' if field == 'tau' else 'recurrence'
        mutated['assembly'][group][field] = value
        try:
            audit(mutated)
        except ValueError as error:
            controls[name] = str(error)
        else:
            raise ValueError('mutation accepted: '+name)
    result.update(negative_controls=controls, elapsed_seconds=time.monotonic()-started,
                  started_utc=started_utc, finished_utc=datetime.now(timezone.utc).isoformat(),
                  checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  certificate_sha256=sha256(certificate_path.read_bytes()).hexdigest(),
                  component_input_sha256={name:sha256(path.read_bytes()).hexdigest()
                      for name,path in [('physical',args.physical),('bit_profile',args.bit_profile),
                                        ('candidate_frames',args.candidate_frames)] if path})
    with args.output.open('x') as stream:
        json.dump(js(result),stream,indent=2); stream.write('\n')
    print(json.dumps(js(result),indent=2))


if __name__ == '__main__':
    main()
