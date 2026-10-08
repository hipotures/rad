#!/usr/bin/env python3
"""Exact phase assembly for the new complex primitive and decaying recurrence.

The accepted bit certificate and new full complex certificate are read-only
inputs. Their independent finite proofs remain separate obligations.
No floating point is used in an acceptance inequality.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from downstream_gaussian import BASELINE_KAPPA,ceil_q,check_sources,network_counts,require
from downstream_parameter_optimum import as_strings,compact_lower,rational_decimal_lower,saving_enclosure


def scalar_checks():
    geometric=balances=0
    for ratio in [Q(1,2),Q(2,3),Q(999,1000),Q(1000000,1000001)]:
        for depth in range(1,65):
            value=sum((ratio**i for i in range(depth)),Q(0))
            require(value==(1-ratio**depth)/(1-ratio),'Decaying geometric identity failed')
            require(value<1/(1-ratio),'Decaying geometric bound failed')
            geometric+=1
    for a,b in [(Q(1,64),Q(1,32)),(Q(1,2**20),Q(1,2**18)),
                (Q(3,10**9),Q(13,10**9))]:
        tau=1-a;c=a;q=a*a;x=q/b
        require(a*c==a-tau*c==q,'Movement/internal balance failed')
        require(b*x==q,'Leaf balance failed')
        require(q/(1+max(4*x,c+q))==a*a/(1+max(4*a*a/b,a+a*a)),
                'Full seven-margin scoped ceiling failed')
        balances+=1
    return dict(exact_decaying_geometric_checks=geometric,exact_balance_checks=balances,
                status='PASS scalar identities supporting the separately written all-size proof')


def compose(n,nc,mode,old_kappa):
    eb=saving_enclosure(n['eta'],n['m']);ec=saving_enclosure(nc['eta'],nc['m'])
    a,b=eb['chosen_saving'],ec['chosen_saving']
    require(0<a<b<Q(1,32),'New complex recurrence requires sigma<tau')
    tau,sigma=1-a,1-b;c=a
    # This is strict slack on the changed recurrence estimate. The tighter
    # parameter row separately reduces the old fixed guard/epsilon slack.
    recurrence_slack=Q(1,2**64)
    q=a*a*(1-recurrence_slack)
    x=(q/b)*(1+recurrence_slack);beta=1-x
    internal=tau*(1+c);leaf=sigma+beta*(1-sigma)
    lp=1-q;lam=(lp+max(tau,sigma,internal))/2
    require(mode in ('conservative','tight'),'Unknown composition mode')
    guard_slack=Q(1,2**20) if mode=='conservative' else Q(1,2**64)
    zeta=Q(1,2**30) if mode=='conservative' else Q(1,2**64)
    C1=5-4*beta+zeta
    prefix_cap=1+c+q
    eps=(1-guard_slack)/max(C1,prefix_cap)
    r=(1-eps)/2;delta=r/8
    B=nc['s']+64*(nc['W']+nc['m']+1)**3
    C0=32*nc['m']*B*B*(1+1/zeta)
    margins=dict(g1=1-eps*(1+c),g2=eps*a*c,g3=eps*q,
                 g4=a*(1-eps),g5=min(1-eps-delta,r-delta),
                 g6=1-eps-delta,g7=eps)
    G=min(margins.values());kappa=compact_lower(G,places=40)
    slacks=dict(bit_primitive=eb['strict_primitive_gap'],complex_primitive=ec['strict_primitive_gap'],
                tau_above_sigma=tau-sigma,decaying_ratio_gap=b-a,
                lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
                unrolled_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
                leaf_cost=lp-leaf,guard=1-eps*C1,
                local_convolution_cost=1-eps-delta,boundary_solve_cost=r-delta,
                gamma_sublinear=1-eps-r,cell_larger_than_band=eps-(1-r)/2,
                prime_interval_and_line_growth=1-eps,alpha_power=r,
                prefix_cost=1-eps*(1+c),K_smaller_than_ell=1-eps-eps*c,
                movement_vs_layer=margins['g2']-margins['g3'],
                prefix_vs_layer=margins['g1']-margins['g3'],
                nonadjacent_vs_layer=margins['g4']-margins['g3'],
                absorption=G-kappa,improvement_over_accepted_phase=kappa-old_kappa)
    for key,value in slacks.items():require(value>0,'Nonpositive decaying composition slack '+key)
    require(G==margins['g3'],'Unexpected seven-margin bottleneck')
    require(Q(9,10)<=beta<1 and 0<r<=Q(1,3),'Phase/guard parameter domain failed')
    require(0<nc['D'] and 2<=nc['s']<nc['m']**5,'Complex guard/count premise failed')
    au,bu=eb['saving_upper'],ec['saving_upper']
    require(au<ec['saving_lower'],'Primitive ordering not certified at interval level')
    upper=min(au*au*bu/(bu+4*au*au),au*au/(1+au+au*au))
    require(kappa<upper,'Scoped upper bound failed')
    k=ceil_q(1/r)
    cutoffs=dict(gamma=ceil_q(Q(7)/(1-eps-r)),logarithmic_alpha=16*k*k+1,
                 full_guard=ceil_q(Q((2*ceil_q(C0)).bit_length())/(1-eps*C1)),
                 phase_cell=ceil_q(Q(9)/(eps-(1-r)/2)))
    require(cutoffs['gamma']*(1-eps-r)>=7,'Gamma cutoff failed')
    require(Q(1,k)<=r,'Alpha cutoff orientation failed')
    require(cutoffs['full_guard']*(1-eps*C1)>=(2*ceil_q(C0)).bit_length(),'Guard cutoff failed')
    require(cutoffs['phase_cell']*(eps-(1-r)/2)>=9,'Cell cutoff failed')
    # Counterexample to importing the growing-ratio expression: it would
    # claim an internal exponent below the true top-level overhead.
    wrong_growing=sigma+beta*(tau-sigma)+tau*c
    require(wrong_growing<internal,'Wrong-branch negative control failed')
    return dict(status='Strict exact arithmetic composition; separately reviewed finite/phase and decaying proofs required',
                mode=mode,bit_counts=n,complex_counts=nc,
                bit_saving_enclosure=eb,complex_saving_enclosure=ec,
                parameters=dict(tau=tau,sigma=sigma,a_bit=a,a_complex=b,beta=beta,c=c,
                                lambda_prime=lp,lambda_=lam,epsilon=eps,alpha_squared_power=r,
                                delta=delta,C0=C0,C1=C1,zeta=zeta,kappa=kappa),
                internal_exponent=internal,leaf_exponent=leaf,
                internal_branch='sigma<tau: decaying geometric sum; top-level exponent tau(1+c)',
                guard_vs_prefix_denominators=dict(guard=C1,prefix=prefix_cap),
                constraint_slacks=slacks,margins=margins,minimum_margin=G,
                scoped_model_upper=upper,achieved_fraction_of_upper=kappa/upper,
                kappa_ratio_to_baseline=kappa/BASELINE_KAPPA,
                kappa_ratio_decimal_lower=rational_decimal_lower(kappa/BASELINE_KAPPA,15),
                old_accepted_phase_kappa=old_kappa,strict_improvement_factor=kappa/old_kappa,
                improvement_factor_decimal_lower=rational_decimal_lower(kappa/old_kappa,15),
                wrong_growing_branch_control=dict(invalid_internal_exponent=wrong_growing,
                                                   true_top_internal_exponent=internal,
                                                   strict_underestimate=internal-wrong_growing),
                cutoff_log2_b={**cutoffs,'common':max(cutoffs.values())},
                additional_eventual_cutoffs=['BHP primary prime threshold and interval packing',
                                            'Strict recurrence logarithm/constant absorption',
                                            'Unmodified original fixed-tape multiplication interfaces'],
                proof_obligations=['Complete new complex scalar/binary-frame/terminal/phase/rank proof',
                                   'Separate promoted bit circuit and rational-frame proof',
                                   'Reviewed phase-cell/GS/Schur Gaussian transfer',
                                   'All-size decaying recurrence and seven-margin assembly',
                                   'Pinned complete conditional upstream multiplication theorem'])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--bit-certificate',type=Path,required=True)
    ap.add_argument('--complex-certificate',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    start=time.monotonic();provenance=check_sources(args.upstream)
    bit=json.loads(args.bit_certificate.read_text());complex_=json.loads(args.complex_certificate.read_text())
    require(bit['provenance']['commit']==complex_['provenance']['commit']==provenance['commit'],
            'Input certificates disagree on immutable upstream')
    bn=bit['best']['counts']
    require(bn['p']==bn['q']==50 and bn['outer_side_roles']==bn['middle_side_roles'],
            'This bounded composition starts with the promoted uniform h50 primitive')
    n=network_counts(50,bn['outer_side_roles'])
    for key in ('N','m','W','L','D','s','eta'):require(Q(n[key])==Q(bn[key]),'Bit input count changed '+key)
    row=next(r for r in complex_['cases'] if r['h']==50)
    require(row['terminal']['every_terminal_complement_nondegenerate_nonalternating'],
            'Complex terminal checks absent')
    require(row['matching']['involution'] and row['guard']['stopped_depth_branching_premise'],
            'Complex matching/guard checks absent')
    nc={k:(Q(v) if k=='eta' else v) for k,v in row['shared_complex_counts'].items()}
    old_kappa=Q(bit['best']['parameters']['kappa'])
    unshared=dict(nc);unshared['W']=row['unshared_W'];unshared['s']=row['unshared_s']
    unshared['eta']=Q(unshared['D'],unshared['W']*unshared['m'])
    witnesses=[compose(n,nc,'conservative',old_kappa),compose(n,nc,'tight',old_kappa),
               compose(n,unshared,'tight',old_kappa)]
    names=['downstream_complex_assembly.py','downstream_complex_certificate.py',
           'downstream_complex_circuit.py','downstream_gaussian.py','downstream_parameter_optimum.py']
    source=Path(__file__)
    result=dict(campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_deadline='2026-10-08T08:25:21Z',provenance=provenance,
                generated_at=datetime.now(timezone.utc).isoformat(),
                input_certificates={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                    for p in [args.bit_certificate,args.complex_certificate]},
                source_sha256={name:hashlib.sha256((source.parent/name).read_bytes()).hexdigest() for name in names},
                scalar_checks=scalar_checks(),witnesses=witnesses,elapsed_seconds=time.monotonic()-start,
                scope='Declared complex/phase/decaying-movement family; no universal optimum or unconditional theorem claim')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for w in witnesses:
        print('PASS new complex',w['mode'],'shared' if w['complex_counts']['W']==nc['W'] else 'unshared',
              'kappa',w['parameters']['kappa'],'baseline ratio >=',w['kappa_ratio_decimal_lower'],flush=True)


if __name__=='__main__':main()
