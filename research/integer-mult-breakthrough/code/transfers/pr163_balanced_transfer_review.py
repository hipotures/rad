#!/usr/bin/env python3
"""Independent exact arithmetic review of PR163's paid transfer interface.

Consumes a compact source-bound mathematical fixture as data. No external
implementation is executed or imported. Words, moment enclosures and all-size
native/analytic contracts remain separate assumptions and review tasks.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import prod
from pathlib import Path
import sys
import time


TOPIC = Path(__file__).resolve().parents[2]
FIXTURE = TOPIC/'fixtures/transfers/pr163-paid-balanced-transfer.json'
FIXTURE_SHA = '36e66dc1e4424d2a0ccca1ad2bcf34699edc47cd8cafc0ae8e6d1be2089a224e'
GRID = 10**18


def require(test, message):
    if not test:
        raise ValueError(message)


def reject_float(value):
    require(not isinstance(value, float), 'Binary float in mathematical input')
    if isinstance(value, dict):
        for item in value.values():
            reject_float(item)
    elif isinstance(value, list):
        for item in value:
            reject_float(item)


def below(value):
    scaled = value*GRID
    return Q((scaled.numerator-1)//scaled.denominator, GRID)


def exact_bridge(profile):
    h,v,R,c,q,matched,M,scalar_R = [profile[k] for k in
        ('h','v','R','c','q','matched','total_M_operations','scalar_role_reserve')]
    require(h >= 2 and h % 2 == 0, 'Even positive complex base dimension')
    require(scalar_R == c+q-matched, 'Full pre-reuse scalar inventory')
    require(scalar_R-R == profile['reuse_pairs'], 'Actual physical handoff count')
    m = 3*h
    hist = {int(k):int(n) for k,n in profile['child_histogram'].items()}
    require(all(0<t<m and n>0 for t,n in hist.items()), 'Proper positive complete children')
    localW = 2*v+R
    localS = sum(t*n for t,n in hist.items())
    r = max(hist)
    require((m,localW,localS,r) == tuple(profile[k] for k in
        ('m','W_per_vertex','rank_per_vertex','maxchild')), 'Local inventory mismatch')
    require(m*localW-localS == profile['deficit_per_vertex'] == 2*v-3*profile['loss'],
            'Paid shared-core rank deficit')
    half = m//2
    vertices = 2**(m-1+(half-1)**2)*prod(2**(2*i)-1 for i in range(1,half))
    W,s,N = vertices*localW,vertices*localS,vertices*v
    local = 4*(c+v)+10*v+4*h*v+4*h*h+8*h+8+2*h+8*scalar_R*v*(M+16)+32*v
    K = 3*vertices*local+8*W+4*N+8*m*scalar_R*vertices
    route = 64*(m+1)**3*(K+1)*(W+1)**2
    E = 64*(W+m+route+1)**3
    literal = 2*route*W*W+8*s+4*W+4+32*m
    B = s+E
    C0 = 32*m*B*B
    require(E > literal, 'Complete literal scalar charge not dominated')
    require(2*B*(m-r) >= s+E and C0 > 2*B+18, 'Exact-child induction gap')
    degree = 1
    while m**degree <= 2*r**degree:
        degree += 1
    complex_rows = degree*W.bit_length()
    rows = complex_rows+9909+252
    row_gap = Q(70000)-Q(51,25)*rows
    require(row_gap > 0, 'Full simultaneous row reserve insufficient')
    return dict(m=m,maxchild=r,W_bits=W.bit_length(),halving_degree=degree,
                local_group_upper=local,complex_rows=complex_rows,rows=rows,
                row_degree=70000,row_gap=row_gap,suffix_slope=280000,
                strict_literal_gap=E-literal,C0=C0,
                induction_gap=2*B*(m-r)-s-E)


def assemble(a,b,beta,eta,weakening,kappa,bridge):
    require(0<a<b< Q(1,32) and 0<beta<1 and 0<eta<Q(1,2), 'Supplier range')
    tau,sigma = 1-a,1-b
    q = a*(1-2*eta)
    c = q+eta/4
    eps = (1-eta)/(1+q)
    lp = 1-q
    lam = (tau+lp)/2
    g = eps*q
    r = (g+1-eps)/2
    delta = eta/8
    internal = tau+(1-beta)*max(sigma-tau,Q(0))
    leaf = sigma+beta*(1-sigma)
    margins = dict(g1=1-eps,g2=a,g3=g,g4=a,
        g5=min(1-eps-delta,r-delta),g6=1-eps-delta,g7=eps)
    # Each displayed source constraint follows from the complete paid
    # interface. Names bind to its saved mathematical certificate as data.
    slacks = dict(a_positive=a,a_below_b=b-a,b_below_one_over32=Q(1,32)-b,
        beta_positive=beta,beta_below_one=1-beta,phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
        c_positive=c,c_below_one=1-c,q_below_reservations=c-q,
        lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf,compact_reservations=lp-(1-c),lambda_prime_below_one=q,
        epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps,
        K_geometry=1-eps*(1+c),K_dominates_log=eps*c,record_suffix=1-eps,
        phase_local=1-eps-delta,phase_boundary=r-delta,gamma_sublinear=1-eps-r,
        cell_above_band=eps-(1-r)/2,prime_interval_packing=1-eps,
        alpha_positive=r,alpha_below_one=1-r,alpha_below_one_fourth=Q(1,4)-r,
        delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,
        short_record_fallback=eps-a,small_field_exposure=1-eps-g,
        artificial_boundary=8-eps+r-delta-g,
        literal_scalar_guard=bridge['strict_literal_gap'],row_product_gap=bridge['row_gap'])
    slacks.update({name+'_above_kappa':value-kappa for name,value in margins.items()})
    require(len(slacks)==47 and len(margins)==7, 'Complete selected arithmetic inventory')
    require(all(value>0 for value in slacks.values()), 'A paid strict constraint failed')
    require(min(margins.values())==g, 'Different controlling margin')
    require(1-eps-g==eta and 1-eps-r==eta/2, 'Balance identities failed')
    require(1-eps*(1+c)==eta-eps*eta/4, 'Geometric gap deleted')
    require(kappa==below(g) and kappa+Q(1,GRID)>g, 'Fixed-parameter grid claim')
    return dict(parameters=dict(a_bit=a,a_complex=b,tau=tau,sigma=sigma,beta=beta,
        h=eta,q=q,c=c,epsilon=eps,lambda_=lam,lambda_prime=lp,
        alpha_squared_power=r,delta=delta,kappa=kappa),constraints=slacks,
        margins=margins,minimum_margin=g,
        recurrence=dict(internal=internal,leaf=leaf,reservations=1-c))


def comparison(row):
    a,b,beta,eta,zeta = [Q(row[k]) for k in ('a','complex_saving','beta','eta','weakening')]
    actual = Q(row['actual_bit_saving'])
    require(a==min(actual,(1-beta)*b-zeta), 'Matched transfer must use both suppliers')
    q = a*(1-2*eta)
    if row['layout']=='balanced':
        eps = (1-eta)/(1+q)
    else:
        require(row['layout']=='original', 'Unknown paid layout')
        c = q*(1+eta)
        eps = (1-eta)/(1+c+q)
    g = eps*q
    require(g==Q(row['minimum_margin']) and below(g)==Q(row['kappa']),
            'Matched arithmetic disagrees with retained certificate')
    return dict(name=row['name'],layout=row['layout'],kappa=str(below(g)),
                margin=str(g),scope='Matched arithmetic only; no old finite profile invented')


def evaluate(data, workers):
    reject_float(data)
    bridge = exact_bridge(data['complex_profile'])
    expected = data['expected_bridge_compact']
    for name,key in [('full_role_bits','W_bits'),('local_group_upper','local_group_upper'),
        ('row_coefficient','rows'),('complex_row_coefficient','complex_rows'),
        ('row_degree','row_degree'),('row_degree_gap','row_gap'),('suffix_slope','suffix_slope'),
        ('maxchild','maxchild'),('halving_degree','halving_degree')]:
        require(Q(expected[name])==bridge[key], 'Paid bridge mismatch '+name)
    require(expected['C1']==1 and expected['fixed_odd_divisor']==3, 'Changed grid/endpoint input')
    sup = data['suppliers']
    coarse,old,theta = Q(sup['coarse_bit_saving']),Q(data['old_atom_saving']),Q(sup['atom_exponent'])
    actual = (1-theta)*coarse+theta*old
    critical = coarse/(1+coarse-old)
    require(actual==Q(sup['actual_uniform_bit_saving']), 'Stopped ordinary supplier changed')
    require(actual<theta<1-actual, 'Atom and restored-row tolls not both paid')
    require(theta-Q(1,10**24)<=critical<theta, 'Least strict atom grid claim')
    b,beta,eta,zeta,k = [Q(sup[name]) for name in
        ('complex_saving','beta','eta','strict_weakening','kappa')]
    a = min(actual,(1-beta)*b-zeta)
    require(a==Q(sup['weakened_transfer_saving']), 'Joint supplier weakening changed')
    assembly = assemble(a,b,beta,eta,zeta,k,bridge)
    for section in ['parameters','constraints','margins','recurrence']:
        expect = data['expected_assembly'][section]
        require(set(expect)==set(assembly[section]), 'Expected section keys differ '+section)
        require(all(Q(expect[key])==assembly[section][key] for key in expect),
                'Exact selected transfer differs '+section)
    require(Q(data['expected_assembly']['minimum_margin'])==assembly['minimum_margin'],
            'Selected minimum mismatch')
    require(a>Q(1,9999) and k>Q(1,10000), 'Conditional target threshold comparison')
    frozen_phase_upper = Q(71744622,10**12)
    require(frozen_phase_upper/(1+frozen_phase_upper)<Q(1,10000), 'Frozen phase ceiling scope')
    par = assembly['parameters']
    direct_power = par['tau']*(1+par['c']/beta)
    require(direct_power>par['lambda_prime'], 'Direct activity ledger negative must separate')
    require(1-Q(1,2**50)>par['lambda_'], 'Frozen exchange exponent cannot be silently retained')
    old_prefix = 1-par['epsilon']*(1+par['c'])
    require(old_prefix<k, 'Selected row must actually depend on paid balanced layout')
    # A separate proposed activity interface may consume the improved
    # ordinary supplier. This is selected-width slack, never kappa.
    activity_p,activity_c,activity_beta = Q(9997,10000),Q(1,10000),Q(1,2)
    activity_tau = 1-actual
    activity_power = activity_tau*(1+activity_c/activity_beta)
    require(activity_power<activity_p and activity_p>Q(97,100),
            'The improved ordinary contract must fit the specified activity envelope')
    require(11**100<12**97, 'Hypothetical shorter-word Jensen input')
    selected_saving = (1-activity_beta)*(1-activity_p)
    H_power = activity_c*activity_tau/(1-activity_tau)
    H_saving = (1-activity_p)*(1-H_power)
    require(selected_saving==Q(3,20000) and selected_saving>Q(1,10000),
            'Direct selected-width compatibility calculation')
    require(H_power<1 and H_saving>selected_saving, 'Separate balanced cutoff calculation')
    if workers==1:
        rows = list(map(comparison,data['matched_comparisons']))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(comparison,data['matched_comparisons']))
    negatives = []
    for name,tamper in [('collapsed virtual scalar stock', lambda x:x.update(scalar_role_reserve=x['R'])),
                        ('full-width child', lambda x:x['child_histogram'].update({'66':1}))]:
        changed = dict(data['complex_profile'])
        changed['child_histogram'] = dict(changed['child_histogram'])
        tamper(changed)
        try:
            exact_bridge(changed)
        except ValueError:
            negatives.append(name)
        else:
            raise ValueError('Invalid paid inventory accepted')
    return dict(conditional_kappa=str(k),conditional_target_crossed=True,
        certified_source_supplier_values_used=True,bit_is_selected_bottleneck=a==actual,
        complete_constraints=len(assembly['constraints']),complete_margins=len(assembly['margins']),
        minimum_margin=str(assembly['minimum_margin']),atom_lower_gap=str(theta-actual),
        ordinary_saving=str(actual),complex_saving=str(b),matched_comparisons=rows,
        balanced_gain_at_matched_constants=str(Q(rows[3]['kappa'])-Q(rows[2]['kappa'])),
        finer_backoff_gain=str(Q(rows[4]['kappa'])-Q(rows[3]['kappa'])),
        row_reserve=dict(full_role_bits=bridge['W_bits'],coefficient=bridge['rows'],
                        degree=bridge['row_degree'],degree_gap=str(bridge['row_gap'])),
        exact_induction_gaps_positive=True,
        retained_old_prefix_rejects_selected_point=True,
        direct_activity_power_is_a_different_interface=True,
        frozen_original_exchange_cannot_supply_selected_tau=True,
        hypothetical_activity_interoperability=dict(tau=str(activity_tau),
            potential_power=str(activity_p),K_power=str(activity_c),
            fixed_cutoff_power=str(activity_beta),local_overhead_power=str(activity_power),
            direct_selected_width_saving=str(selected_saving),balanced_cutoff_power=str(H_power),
            balanced_selected_width_saving=str(H_saving),shorter_word_found=False,
            scope='Conditional updated ordinary ABI plus hypothetical g11; selected-width cost only, not kappa'),
        negative_controls=negatives,
        external_word_replayed=False,external_implementation_imported=False,
        all_size_contracts_proved=False,new_local_multiplier_claim=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.workers<1:
        parser.error('workers must be positive')
    # The pinned 24 KiB fixture has a 5899-digit complete scalar gap.
    # Keep a bounded parser, without weakening any mathematical check.
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(10000)
    source = Path(__file__).resolve()
    source_hash = sha256(source.read_bytes()).hexdigest()
    require(sha256(FIXTURE.read_bytes()).hexdigest()==FIXTURE_SHA, 'Mathematical input drift')
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    result = evaluate(json.loads(FIXTURE.read_text()),args.workers)
    require(sha256(source.read_bytes()).hexdigest()==source_hash, 'Review source changed')
    require(sha256(FIXTURE.read_bytes()).hexdigest()==FIXTURE_SHA, 'Review input changed')
    result.update(status='PASS INDEPENDENT SCOPED PR163 TRANSFER ARITHMETIC',
        started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=source_hash,input_sha256=FIXTURE_SHA,workers=args.workers,
        seconds=time.monotonic()-clock,
        scope='Conditional supplied moments, finite inventories and paid transfer assumptions; no independent word, routing, prime, recovery or all-size theorem')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as out:
            out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in
        ('status','conditional_kappa','complete_constraints','seconds')}),flush=True)


if __name__=='__main__':
    main()
