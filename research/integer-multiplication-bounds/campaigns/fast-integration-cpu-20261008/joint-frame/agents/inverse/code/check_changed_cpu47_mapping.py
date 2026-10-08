#!/usr/bin/env python3
"""Independent exact obligation map; no public/campaign assembly imports.

Mapped rows are the changed CPU theorem, not unchanged public47 inequalities.
Physical and analytic proofs are written separately; arithmetic is not proof.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

def encode(x):
    if isinstance(x, F): return str(x)
    if isinstance(x, dict): return {str(k): encode(v) for k,v in x.items()}
    if isinstance(x, (tuple,list)): return [encode(v) for v in x]
    return x

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('--literal-ledger',type=Path,required=True)
    parser.add_argument('--cpu38',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert __debug__ and not args.output.exists()
    native=json.loads(args.native.read_text())
    literal=json.loads(args.literal_ledger.read_text())
    old38=json.loads(args.cpu38.read_text())
    a,b=F(native['saving']),F(717,10**7)
    eta=F(1,10**6); eps=1-eta; beta=F(1,20); zeta=F(1,1000)
    q=eps*a; kappa=(1-10*eta)*a
    tau,sigma=1-a,1-b
    internal=tau+(1-beta)*max(sigma-tau,F(0))
    leaf=sigma+beta*(1-sigma)
    lp=1-q; lam=(max(tau,sigma,internal,leaf)+lp)/2
    c_geometry=(1-eps)/eps
    assert a==F(old38['native_saving']) and kappa==F(old38['candidate_kappa'])
    assert q==F(old38['changed_cpu_assembly']['parameters']['q'])
    assert lam==F(old38['changed_cpu_assembly']['parameters']['lambda_'])
    f=native['assembly']['finite_bridge']
    bit,co=f['bit'],f['complex']
    assert bit['W']==literal['W']==native['controller']['W']
    assert literal['replicated_wrapped_XORs']==native['controller']['wrapped_scalar_xors']==2205627596
    assert literal['owned_copy_stream_groups_upper']==4*(2300*23+1771*25)==388700
    for d in (bit,co):
        m,t=d['m'],d['maxchild']; h=1
        while m**h<=2*t**h: h+=1
        assert h==d['halving_degree'] and d['W'].bit_length()==d['wire_bits']
    coefficient=sum(d['halving_degree']*d['wire_bits'] for d in (bit,co))
    degree=F(f['rows']['degree']); rowgap=degree-F(51,25)*coefficient
    assert coefficient==852 and degree==2000 and rowgap==F(6548,25)
    E=64*(co['W']+co['m']+co['scalar_group_upper']+1)**3
    B=co['s']+E
    numeric_literal=2*co['scalar_group_upper']*co['W']**2+8*co['s']+4*co['W']+4+32*co['m']
    C0=32*co['m']*B**2
    assert E==f['semantic']['E'] and B==f['semantic']['B'] and C0==f['semantic']['C0']
    assert E>numeric_literal and 2*B*(co['m']-co['maxchild'])>=co['s']+E
    target=1-kappa
    costs=dict(completed_fft=1-eps*q,coordinate_routing=tau,guarded_tree_crt=tau,
               suffix_ring_product=1-eps,packed_recursive_children=eps*(1-kappa),
               sparse_repair_sorting=1-2*eps,phase_band_lu=-eps+18*eps*zeta,
               regular_free_axis_band_lu=-2*eps+18*eps*zeta,
               source_elementary_phase=18*eps*zeta,scalar_setup=F(0),linear_scan=F(0))
    gaps={name:target-value for name,value in costs.items()}
    assert all(v>0 for v in gaps.values())
    rows={}
    def put(name,slack,kind,statement):
        assert name not in rows and slack>0
        rows[name]=dict(classification=kind,positive_mapped_slack=slack,statement=statement)
    def retain(name,slack,statement): put(name,slack,'retained numerical/native condition',statement)
    def replace(name,slack,statement): put(name,slack,'replaced by changed CPU proof',statement)
    retain('a_positive',a,'Native bit characteristic is strictly below one at the independently enclosed saving.')
    retain('a_below_b',b-a,'Complex saving exceeds the changed bit saving.')
    retain('b_below_one_over32',F(1,32)-b,'Retain the actual complex upper restriction.')
    retain('beta_positive',beta,'Positive global complex stop exponent.')
    retain('beta_below_one',1-beta,'Stop strictly below the full selected width.')
    retain('phase_leaf_above_bit',(1-beta)*b-a,'Complete complex leaf exponent is below the bit exponent.')
    retain('q_positive',q,'Positive deferred-transform saving.')
    retain('q_below_internal',1-internal-q,'Use the actual volume-weighted internal moment.')
    retain('q_below_leaf',1-leaf-q,'Use the actual stopped complex leaf moment.')
    retain('c_positive',c_geometry,'Actual main-axis width exponent is c_geometry=(1-epsilon)/epsilon.')
    retain('c_below_one',1-c_geometry,'epsilon>1/2 implies actual c_geometry<1.')
    replace('q_below_reservations',min(eps,1-eps),'All row/front/back fields come from deferred donor axes: |donors|/d=O(log(d)/d+log(Q)/ell) tends to zero. No per-level individual reservation transforms.')
    retain('lambda_above_tau',lam-tau,'Strict native bit recurrence gap.')
    retain('lambda_above_sigma',lam-sigma,'Strict native complex recurrence gap.')
    retain('lambda_above_internal',lam-internal,'Strict actual internal-moment recurrence gap.')
    retain('lambda_prime_above_lambda',lp-lam,'Strict stopped-tree majorant gap.')
    retain('compact_leaf',lp-leaf,'Strict complete leaf gap.')
    replace('compact_reservations',min(eps,1-eps),'The external-field layer supplies disjoint complete rows and all dirty banks; whole donor transforms occur once, with two paid coordinate routes.')
    retain('lambda_prime_below_one',q,'Strict completed Fourier saving.')
    retain('epsilon_positive',eps,'Positive dimension exponent.')
    retain('epsilon_below_one',1-eps,'Main lengths dominate polynomials and child logarithms shrink.')
    replace('guard_width',17*eps,'Semantic Delta<=C0*d is o(Q); Q=Theta(d^18), including the complete changed scalar/owned-port constants.')
    replace('K_geometry',1-eps,'ell=Theta(B0^(1-epsilon)) exceeds log(Q); actual external donor fields replace the old coupled 1-epsilon(1+c)>0 constraint.')
    retain('K_dominates_log',eps*c_geometry,'Actual ell/log(Q) tends to infinity.')
    retain('record_suffix',1-eps,'ell-first suffix has log(r)<2ell and r/Q^A tends to infinity for every fixed A.')
    replace('phase_local',F(4),'theta*L_I/delta=O(d^-4) with delta=d^-4,L_I=Theta(d^8). The old delta exponent is not reused.')
    replace('phase_boundary',F(7,2),'theta*R_exception/delta=O(d^-7/2), including expanded source phase strips.')
    replace('gamma_sublinear',F(7,8),'Actual gamma=2du<=B/8; Q is a large fixed multiple of B. No claim u is sublinear in B0.')
    replace('cell_above_band',F(3),'Separate forward/inverse cells have L/R>=d^3, with all rounding margins and padded source faces.')
    retain('prime_interval_packing',1-eps,'ell superlogarithmic implies t^(19/40)/d^17 tends to infinity; distinct eligible BHP intervals remain constructible.')
    replace('alpha_positive',F(17),'Actual u=alpha^2=Theta(d^17) grows; integer alpha is chosen after B and d.')
    replace('alpha_below_one',F(1),'u/Q=Theta(d^-1), not the old alpha-squared power of B0.')
    replace('alpha_below_one_fourth',F(1,8),'gamma/B<=1/8<1/4 with alpha ceiling charged. The old small-alpha power is not asserted.')
    replace('delta_positive',F(4),'delta=d^-4>0 at every finite d; the displayed 4 is its decay exponent.')
    replace('delta_below_one_eighth',F(1,16),'For d>=2, delta<=1/16<1/8. Unrelated to public h/8.')
    retain('short_record_fallback',eps-a,'Retain the conservative native elementary-tail comparison; long polynomial spectators also pay metadata.')
    replace('small_field_exposure',F(1,32),'Inactive N/8 bank covers nine router pieces<N/16, U/T<N/64 and untouched suffix<N/64; all are actual disjoint bits restored before consumption.')
    replace('artificial_boundary',1-eps,'Physical period cuts include the larger L_F and R_F; polynomial-width cut density is superpolynomially small relative to prime lengths.')
    retain('literal_scalar_guard',F(E-numeric_literal),'The unchanged completed complex guard counts its actual G; exact BIT encoding gates return before complex arithmetic.')
    retain('row_product_gap',rowgap,'Actual stock 9*28+20*30=852, degree2000, gap6548/25; both layers and all dirty/copy fields included.')
    replace('g1_above_kappa',gaps['guarded_tree_crt'],'Paid balanced guarded-reflection CRT replaces the old d-payload triangular/prefix implementation.')
    retain('g2_above_kappa',gaps['coordinate_routing'],'Paid full-payload named-bit routing remains exponent1-a.')
    retain('g3_above_kappa',gaps['completed_fft'],'Both deferred groups cost ell*d^(1-q): normalized exponent1-epsilon*q.')
    replace('g4_above_kappa',gaps['coordinate_routing'],'Joint monotone product gather/selector/restore and two global flat shifts pay one scan plus actual named-bit routes; no d full-payload exposures.')
    replace('g5_above_kappa',min(gaps['packed_recursive_children'],gaps['phase_band_lu'],gaps['regular_free_axis_band_lu'],gaps['source_elementary_phase']),'Packed normalized kernels use the same strictly shrinking integer algorithm; every repaired free cyclic axis, scalar phase and window setup is paid.')
    replace('g6_above_kappa',min(gaps['sparse_repair_sorting'],gaps['phase_band_lu'],gaps['regular_free_axis_band_lu']),'Count SUM of expanded source packets, source-closed shrinking buffers, sparse sorting, phase and all free-axis cyclic repair.')
    retain('g7_above_kappa',gaps['suffix_ring_product'],'Actual suffix log(rQ)=O(ell+log Q), with ell chosen first.')
    assert len(rows)==47 and set(rows)==set(native['assembly']['constraints'])
    # Explicit feasible constants for the degree equality18=16+2.
    CI=CF=1024; CQ=16
    ctheta=F(1,2**50*CI**2*CQ)
    CD=F(2**64)*CQ/ctheta
    # d<=4*B0^epsilon eventually, B>=CD*B0^(18epsilon).
    u2theta_over_Q_lower=CD*ctheta/F(2**36*4096*CQ)
    inverse_chirp_over_Q_upper=F(16384)*CI**2*CQ*ctheta
    forward_chirp_over_Q_upper=F(256)*CF**2*ctheta
    assert u2theta_over_Q_lower>=2
    assert inverse_chirp_over_Q_upper<F(1,16) and forward_chirp_over_Q_upper<F(1,16)
    supplements=dict(
        lambda_above_complete_leaf=lam-leaf,
        metadata_degree_four=18*eps-4,
        metadata_joint_floor=18*eps-(2*eps+2),
        inverse_weighted_perturbation_growth=F(13),
        inverse_regular_second_tail_above_Q=F(7),
        inverse_radius_inside_phase_pocket=F(7),
        exception_radius_below_half_period=F(15,2),
        u_theta_growth=F(1),u_over_Q_decay=F(1),
        strict_theta_Q_u_squared=u2theta_over_Q_lower-1,
        inverse_total_chirp_margin=F(1,16)-inverse_chirp_over_Q_upper,
        forward_total_chirp_margin=F(1,16)-forward_chirp_over_Q_upper,
        precision_twoQ_after_chirps_and_logwords=F(7,8),
        recovery_at_Q_sixB=F(7,8),
        packed_child_logarithm_shrink=1-eps,
        packed_induction_ratio=(1-eps)*(1-kappa),
        chosen_kappa_above_old_supremum=kappa-a/(1+a))
    assert all(x>0 for x in supplements.values())
    negative_controls=dict(
        unchanged_triangular_CRT=target-eps,
        actual_geometry_old_reservation=c_geometry-q,
        actual_geometry_old_K_strict=1-eps*(1+c_geometry),
        unchanged_full_axis_Gaussian=target-eps,
        equating_old_delta_to_new_four=F(1,8*10**12)-4,
        unchanged_short_digit_chirp=1-(F(1,2)+2*eps))
    assert negative_controls['actual_geometry_old_K_strict']==0
    assert all(x<0 for name,x in negative_controls.items() if name!='actual_geometry_old_K_strict')
    assert set(old38['rejected_unchanged_public47']['constraints'])=={'g1_above_kappa','g3_above_kappa','g5_above_kappa','g6_above_kappa'}
    result=dict(status='EXACT CHANGED47 MAP AND SUPPLEMENTS PASS; WRITTEN CONDITIONAL REVIEW REQUIRED',
                recorded_utc=datetime.now(timezone.utc).isoformat(),conditional_transfer_accepted=False,
                inputs={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [args.native,args.literal_ledger,args.cpu38,Path(__file__)]},
                parameters=dict(a=a,b=b,kappa=kappa,epsilon=eps,q=q,beta=beta,zeta=zeta,lambda_=lam,lambda_prime=lp,actual_c_geometry=c_geometry),
                mapped_public47=rows,changed_cost_exponents=costs,strict_cost_gaps=gaps,
                supplements=supplements,negative_controls=negative_controls,
                feasible_constants=dict(C_I=CI,C_F=CF,C_Q=CQ,c_theta=ctheta,C_D=CD,u_squared_theta_over_Q_lower=u2theta_over_Q_lower,inverse_total_chirp_over_Q_upper=inverse_chirp_over_Q_upper,forward_total_chirp_over_Q_upper=forward_chirp_over_Q_upper),
                expenses=dict(W=bit['W'],rank_mass=native['controller']['total_rank'],complete_wrapped_XORs=literal['replicated_wrapped_XORs'],owned_copy_stream_groups_upper=literal['owned_copy_stream_groups_upper'],row_coefficient=coefficient,row_degree=degree,row_gap=rowgap),
                scope='Exact obligations and independently reconstructed semantic/stock constants; source-proved external bank, paid native residual/copy routing, Gaussian/locality/error/recovery and strong-induction contracts remain explicit mathematical hypotheses.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps(encode(dict(status=result['status'],kappa=kappa,mapped_rows=len(rows),minimum_cost_gap=min(gaps.values()),minimum_supplement=min(supplements.values()),old_K_geometry=negative_controls['actual_geometry_old_K_strict']))))

if __name__=='__main__': main()
