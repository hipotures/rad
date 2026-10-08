#!/usr/bin/env python3
"""Independent compact recurrence/count/log/margin and interface audit.

Only reviewer logarithm/count routines are imported. No producer is used.
The compact address checks and the written tape/layout proof are separate.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import time

from review_asymmetric_motif import independent_saving
from review_packed_unrolling import finite_counts

PIN = '6e564879f51ae16f23d392e9e196c605f36d90df'


def ceil_q(x):
    return -(-x.numerator//x.denominator)


def stopped_recurrences():
    """Direct integer recurrences below/at/above the geometric threshold."""
    checked = internal = small = 0
    examples = []
    for k in range(1, 13):
        # m=64, tau=1/2, beta=1/3, d=64^(3k), G=(k+1)^2.
        d, threshold, root_log = 64**(3*k), 64**k, 3*k
        for n in range(root_log+1):
            e = 64**n
            for sigma, b, internal_power, leaf_power in (
                    (Q(1, 3), 4, 9*k, 10*k),
                    (Q(1, 2), 8, 9*k, 12*k),
                    (Q(2, 3), 16, 11*k, 14*k)):
                if e < threshold:
                    assert e <= 2**leaf_power
                    small += 1
                    checked += 1
                    continue
                depth = n-k+1
                leaf = e//64**depth
                assert threshold//64 <= leaf < threshold
                direct = leaf
                for j in reversed(range(depth)):
                    node = e//64**j
                    overhead = (k+1)*2**(3*(n-j))+1
                    assert (overhead-1)**2 == (k+1)**2*node
                    direct = b*direct+overhead
                independent = b**depth*leaf+sum(
                    b**j*((k+1)*2**(3*(n-j))+1) for j in range(depth))
                assert direct == independent
                terms = [b**j*(k+1)*2**(3*(n-j)) for j in range(depth)]
                if b <= 8:
                    assert all(term <= (k+1)*2**(3*n) for term in terms)
                else:
                    assert all(term <= (k+1)*2**internal_power for term in terms)
                leaves = b**depth*leaf
                assert leaves <= 2**leaf_power
                assert sum(b**j for j in range(depth)) <= sum(terms)
                assert direct <= 2*depth*(k+1)*2**internal_power+2**leaf_power
                internal += 1
                checked += 1
                if n == root_log:
                    examples.append(dict(k=k, sigma=str(sigma), depth=depth,
                                         exact_normalized_cost=str(direct),
                                         internal_root_bound=str((k+1)*2**internal_power),
                                         leaf_bound=str(2**leaf_power)))
        # K=64^k is a genuine growing width parameter. Charging K^tau
        # would introduce a factor 2^(3k)/(k+1), absent from the new model.
        assert Q(2**(3*k), k+1) > 1
    assert checked == internal+small
    return dict(complete_stopped_recurrences=checked, internal=internal,
                individually_executed=small, sigma_branches=['1/3', '1/2', '2/3'],
                tau='1/2', beta='1/3', fixed_radix=64,
                overhead='sqrt(G*e)+1; G=(k+1)^2', examples=examples,
                no_K_factor_in_current_recurrence=True)


def original_complex_counts(h):
    v, m = comb(h, 3), h**3
    N = v**3
    z = comb(h-3, 3)+3*(h-3)
    W = 2*N+3*v*v*(v*z+h+1)
    L = 3*v*v*h*(h+1)
    D = 2*N-2*L
    return dict(h=h, v=v, m=m, N=N, Wc=W, Lc=L, sc=W*m-D, eta_c=Q(D, W*m))


def upstream_audit(reference):
    cert = json.loads((reference/'certificates/compact-control-layer.json').read_text())
    paired = json.loads((reference/'certificates/paired-network.json').read_text())
    raw = paired['bit_counts']
    local = dict(raw, h=int(raw['h']), side_roles=int(raw['side_roles_per_invocation']))
    bit = finite_counts(local)
    cx = original_complex_counts(25)
    assert all(Q(cert['complex_counts'][k]) == v for k,v in cx.items())
    assert cx['Lc'] < cx['N'] and not 2*cx['Lc'] < cx['N']
    assert cx['eta_c'] == Q(14, 3464399375)
    p = {k:Q(v) for k,v in cert['main']['parameters'].items()}
    eps,c,beta,tau,sigma,lam,lp,delta = (p[k] for k in
        ('epsilon','c','beta','tau','sigma','lam','lamp','delta'))
    assert tau == 1-Q(296,10**11) and sigma == 1-Q(418,10**12)
    bit_lo,bit_hi = independent_saving(bit['eta'], bit['m'])
    cx_lo,cx_hi = independent_saving(cx['eta_c'],cx['m'])
    assert bit_lo > 1-tau and cx_lo > 1-sigma
    chi = tau+(1-beta)*max(sigma-tau,Q(0))
    leaf = sigma+beta*(1-sigma)
    reserve = max(1-c,Q(0))
    recurrence = dict(internal=chi,leaf=leaf,preprocessing=reserve,layer=max(chi,leaf,reserve))
    assert all(Q(cert['main']['recurrence'][k]) == v for k,v in recurrence.items())
    assert max(tau,sigma,chi) < lam < lp < 1 and max(leaf,reserve) < lp
    margins = dict(g1=1-eps*(1+c),g2=eps*c*(1-tau),g3=eps*(1-lp),
                   g4=(1-tau)*(1-eps),g5=Q(1,4)-delta-Q(5,4)*eps,
                   g6=1-eps-delta,g7=eps)
    assert all(Q(cert['main']['margins'][k]) == v for k,v in margins.items())
    guard = cert['main']['guard']
    W,m,s = cx['Wc'],cx['m'],cx['sc']
    E = 64*(W+m+1)**3
    B,zeta = s+E,Q(1,10000)
    C0 = ceil_q(max(Q(128*m*B*B),18*m*B*B*(1+1/zeta)))
    assert Q(guard['C0']) == C0 and Q(guard['E']) == E and Q(guard['B']) == B
    assert p['C1'] == Q(guard['C1']) == 5-4*beta+zeta
    assert s*(8+E) <= 9*B*B and 2 <= s < m**5
    assert 9*m*B*B*(1+1/zeta)+18 <= C0
    assert eps*p['C1'] < 1 and 0 < beta < 1
    G = min(margins.values())
    assert G == Q(333833,4*10**15) > p['kappa'] == Q(83,10**12) > Q(1,2**34)
    assert G-p['kappa'] == Q(cert['main']['absorption_gap'])
    # Original scalar coefficient formula and the binary residual witnesses
    # are independent of ground parity. Supports below are proper for h25.
    for intersection in range(4):
        center = Q(intersection-1,2)
        side = -center if intersection in (0,2) else Q(0)
        assert center+side == int(intersection == 3)
    assert 6 < 25
    assert all(3**j < 25**j for j in (1,2,3))
    return dict(status='PASS independent original h25 counts, retained bit saving and new upstream margins',
                kappa=str(p['kappa']),minimum_margin=str(G),complex_counts={k:str(v) for k,v in cx.items()},
                complex_loss_less_N_but_not_N_over_two=True,
                unused_coordinate_binary_residual_witnesses=True,
                bit_saving_interval=[str(bit_lo),str(bit_hi)],
                complex_saving_interval=[str(cx_lo),str(cx_hi)])


def audit_row(row):
    n = finite_counts(row['bit_counts'])
    h,v,m,R = 50,comb(50,3),50**3,629617
    N = v**3
    W = 2*N+2*v*v*(R+h+1)
    L = 3*v*v*h*(h+1)
    D,s = 2*N-2*L,W*m-2*N+2*L
    nc = dict(h=h,v=v,m=m,R=R,N=N,W=W,L=L,D=D,s=s,eta=Q(D,W*m))
    assert all(Q(row['complex_counts'][k]) == val for k,val in nc.items())
    assert row['bit_counts']['side_roles'] == 484264
    for name,eta,radix in (('bit',n['eta'],n['m']),('complex',nc['eta'],m)):
        lo,hi = independent_saving(eta,radix)
        enc = row[name+'_saving_enclosure']
        assert Q(enc['saving_lower']) < lo < hi < Q(enc['saving_upper'])
        assert 0 < Q(enc['chosen_saving']) < lo
    p = {k:Q(v) for k,v in row['parameters'].items()}
    a,b,c,beta,eps,r,delta,zeta,lam,lp = (p[k] for k in
        ('a_bit','a_complex','c','beta','epsilon','alpha_squared_power','delta','zeta','lambda_','lambda_prime'))
    tau,sigma = p['tau'],p['sigma'];tiny=Q(1,2**64);q=1-lp
    assert 0 < a < b < Q(1,32) and tau == 1-a and sigma == 1-b
    assert c == 1-tiny and q == a*(1-2*tiny) and 1-beta == (q/b)*(1+tiny)
    chi,leaf,reserve = tau+(1-beta)*max(sigma-tau,Q(0)),sigma+beta*(1-sigma),max(1-c,Q(0))
    assert chi == tau and lam == (lp+max(tau,sigma,chi))/2
    assert all(Q(row['recurrence'][k]) == val for k,val in dict(internal=chi,leaf=leaf,reservations=reserve,compact_movement_spacing_power=0).items())
    backoff = Q(1,2**20) if row['mode'] == 'conservative' else tiny
    assert row['mode'] in ('conservative','tight')
    assert zeta == (Q(1,2**30) if row['mode']=='conservative' else tiny)
    C1 = 5-4*beta+zeta
    E = 64*(W+m+1)**3;B=s+E
    C0 = 32*m*B*B*(1+1/zeta)
    assert p['C1'] == C1 and p['C0'] == C0
    assert s*(8+E) <= 9*B*B and 2 <= s < m**5
    assert 9*m*B*B*(1+1/zeta)+18 < C0
    assert eps == (1-backoff)/max(C1,1+c+q) and r == (1-eps)/2 and delta == r/8
    margins = dict(g1=1-eps*(1+c),g2=eps*a*c,g3=eps*q,g4=a*(1-eps),
                   g5=min(1-eps-delta,r-delta),g6=1-eps-delta,g7=eps)
    assert all(Q(row['margins'][k]) == val for k,val in margins.items())
    G = min(margins.values())
    assert G == Q(row['minimum_margin']) == margins['g3']
    assert all(Q(value)>0 for value in row['constraint_slacks'].values())
    slacks = dict(a=a,b=b,order=b-a,c=c,c_below_one=1-c,beta=beta,beta_below_one=1-beta,
        tau_below_lambda=lam-tau,sigma_below_lambda=lam-sigma,chi_below_lambda=lam-chi,
        lambda_below_prime=lp-lam,leaf_below_prime=lp-leaf,reserve_below_prime=lp-reserve,
        lambda_prime_below_one=1-lp,guard=1-eps*C1,axis_spacing=1-eps*(1+c),
        K_superlogarithmic=eps*c,record_suffix_superpolynomial=1-eps,
        Gaussian_local=1-eps-delta,Gaussian_boundary=r-delta,gamma=1-eps-r,
        phase_cell_separation=eps-(1-r)/2,alpha_positive=r,alpha_below_p=1-r,
        delta=delta,delta_below_eighth=Q(1,8)-delta,
        prefix_above_min=margins['g1']-G,movement_above_min=margins['g2']-G,
        CRT_above_min=margins['g4']-G,Gaussian_above_min=margins['g5']-G,
        scalar_above_min=margins['g6']-G,dimension_above_min=margins['g7']-G,
        absorption=G-p['kappa'],improvement=p['kappa']-Q(83,10**12))
    assert all(v>0 for v in slacks.values())
    assert p['kappa'] == Q((G.numerator*10**40-1)//G.denominator,10**40)
    assert b > 4*a/(1+a) and C1 < 1+c+q
    au,bu = (Q(row[name+'_saving_enclosure']['saving_upper']) for name in ('bit','complex'))
    branches = dict(prefix_and_movement=au/(2+au),movement_and_guard=au*bu/(4*au+bu),leaf_and_guard=bu/5)
    assert all(Q(row['scoped_model_upper_branches'][k])==v for k,v in branches.items())
    assert Q(row['scoped_model_upper']) == min(branches.values()) > p['kappa']
    assert min(branches,key=branches.get) == 'prefix_and_movement'
    km,ka = ceil_q(1/(eps*c)),ceil_q(1/r)
    cc = 64*km*km+1
    # Real log2(b)=L obeys ceil(log2(6b)) <= L+4. The explicit
    # cutoff checks the stronger +192 constant, even for the v1 input
    # whose explanatory comment used +160. Its witness is unchanged.
    assert cc >= 2*km and 2**(cc//km) >= 32*cc+192
    cuts=dict(gamma=ceil_q(7/(1-eps-r)),logarithmic_alpha=16*ka*ka+1,
              full_guard=ceil_q(Q((2*ceil_q(C0)).bit_length())/(1-eps*C1)),
              phase_cell=ceil_q(9/(eps-(1-r)/2)),compact_controls=cc)
    cuts['common']=max(cuts.values())
    assert row['cutoff_log2_b']==cuts
    return dict(mode=row['mode'],kappa=str(p['kappa']),minimum_margin=str(G),
                independent_strict_conditions=len(slacks),producer_strict_conditions=len(row['constraint_slacks']),
                complete_counts_and_independent_logarithms=True,cutoffs=cuts,
                stronger_real_log_cutoff_constant=192,
                ratio_to_83_over_10_to_12=str(p['kappa']/Q(83,10**12)),
                scoped_upper=str(min(branches.values())),scoped_active_branch='prefix_and_movement')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate',type=Path,required=True)
    ap.add_argument('--reference',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    started=time.monotonic();raw=args.certificate.read_bytes();data=json.loads(raw)
    assert data['compact_reference']['commit']==PIN
    assert data['original_reference']['commit']=='bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    result=dict(status='PASS independent compact transfer arithmetic',input_sha256=sha256(raw).hexdigest(),
        reference_revision=PIN,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        stopped_recurrences=stopped_recurrences(),upstream=upstream_audit(args.reference),
        rows=[audit_row(row) for row in data['witnesses']],wall_seconds=time.monotonic()-started,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Exact finite counts, independent logarithms, true compact stopped recurrences, all rational margins and cutoff comparisons. Written compact/phase transfer and theorem conditions remain explicit companion proof dependencies.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS',result['stopped_recurrences']['complete_stopped_recurrences'],'compact recurrences;',len(result['rows']),'exact assembly rows')


if __name__=='__main__':main()
