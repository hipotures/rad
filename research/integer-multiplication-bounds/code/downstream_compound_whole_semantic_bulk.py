#!/usr/bin/env python3
"""Complete whole-complex assembly on a separately promoted compound bit DAG.

Only immutable identities, rank categories and exact logarithms are read.
No physical graph or accepted baseline is replayed. A protected center is
a separate native construction, with its own identifier/table/prime.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_compound_whole_parameters import whole_witness
from downstream_descendant_joined_characteristic import audit_boundary_histogram
from downstream_gaussian import ceil_q,network_counts,require
from downstream_parameter_optimum import as_strings,rational_decimal_lower
from downstream_promoted_complex_composition import parse_counts
from downstream_rotated_batch_characteristic import log_bounds
from downstream_whole_complex_parameters import whole_witness as old_whole_witness
from downstream_whole_complex_semantic_bulk import check_sources,check_input_hashes


def sha(p):
    return sha256(p.read_bytes()).hexdigest()


def generic_characteristic(h,R,protected):
    require(protected in (0,1,2),'Unknown protected-center construction')
    n=network_counts(h,R);v,m=n['v'],n['m'];J=(R+h)*v*v
    n['L']-=3*protected*v*v;n['D']+=6*protected*v*v;n['s']-=6*protected*v*v
    n['eta']=Q(n['D'],n['W']*m)
    kernels=dict(middle=h*h,joined=2*h,data=h*h+h-1)
    runs={key:m-2*d for key,d in kernels.items()}
    copies=dict(middle=J,joined=J,data=2*n['N'])
    ranks={key:copies[key]*(m-kernels[key]) for key in kernels}
    hist={}
    for key,r in runs.items():hist[r]=hist.get(r,0)+copies[key]
    long_rank=sum(r*c for r,c in hist.items());individual=n['s']-long_rank
    require(individual>0 and sum(ranks.values())<n['s'] and 2*max(kernels.values())<m,
            'Changed disjoint generic families invalid')
    lm=log_bounds(m);logs={key:log_bounds(r) for key,r in runs.items()}
    moments={key:copies[key]*runs[key]*logs[key][0] for key in runs}
    M=sum(moments.values());linear=n['s']*lm[1]-M;quadratic=Q(n['s'],2)*lm[1]**2
    require(linear>0,'Normalized characteristic coefficient nonpositive')
    gap=lambda a:n['D']-a*linear-a*a*quadratic/(1-a*lm[1])
    lo,hi=Q(0),Q(1,10**5)
    require(hi*lm[1]<1 and gap(lo)>0>gap(hi),'Positive normalized root bracket failed')
    for _ in range(100):
        mid=(lo+hi)/2
        if gap(mid)>0:lo=mid
        else:hi=mid
    a=Q(lo.numerator*10**24//lo.denominator,10**24)
    require(gap(a)>0,'Normalized strict positive-exponential witness failed')
    maximum=max(runs.values());depth=1
    while m**depth<=2*maximum**depth:depth+=1
    bits=n['W'].bit_length();degree=1000*ceil_q(Q(bits*depth)*(2+Q(1,25))/1000)
    # The old direct negative test is preserved as a comparison. Its
    # larger Wm linear term is not falsely relabeled as the normalized one.
    negative_linear=n['W']*m*lm[1]-M
    ngap=lambda x:n['D']-x*negative_linear-x*x*quadratic
    nl,nu=Q(0),Q(1,10**5)
    for _ in range(100):
        mid=(nl+nu)/2
        if ngap(mid)>0:nl=mid
        else:nu=mid
    negative=Q(nl.numerator*10**24//nl.denominator,10**24)
    require(ngap(negative)>0 and a>negative and maximum==m-4*h,
            'Two distinct strict Taylor estimates or maximum child differ')
    return dict(certificate_kind='GENERIC METRIC FLAGS, NORMALIZED POSITIVE-EXPONENTIAL TAYLOR',
                h=h,roles=R,counts=n,protected_centers=protected,
                construction_id=f'compound-h{h}-normal' if protected==0 else f'compound-h{h}-protected-{protected}-center',
                kernel_dimensions=kernels,family_multiplicities=copies,family_ranks=ranks,
                grouped_runs=runs,long_run_histogram={str(r):c for r,c in sorted(hist.items())},
                long_grouped_rank=long_rank,individual_pivot_count=individual,
                rank_log_moment_lower=moments,logarithm_intervals={'m':list(lm),**{k:list(v) for k,v in logs.items()}},
                taylor_linear_coefficient=linear,taylor_quadratic_coefficient=quadratic,
                saving=a,strict_taylor_gap=gap(a),root_bracket=[lo,hi],
                sufficient_inequality='D-a*(s*ln(m)_U-M_L)-a^2*s*ln(m)_U^2/[2*(1-a*ln(m)_U)]>0',
                positive_exp_justification='exp(t)<=1+t+t^2/[2(1-t)] for0<=t<1; sum exact child ranks normalized by m^(1-a)',
                direct_negative_comparison=dict(saving=negative,strict_taylor_gap=ngap(negative),
                    linear_coefficient=negative_linear,quadratic_coefficient=quadratic,
                    estimate='D-a*(Wm*ln(m)_U-M_L)-a^2*s*ln(m)_U^2/2>0'),
                maximum_child_rank=maximum,child_ratio=Q(maximum,m),depth_per_ceil_log2e=depth,
                W_binary_upper_exponent=bits,sufficient_row_degree=degree,
                native_basis='One constructively fixed rational metric isometry with full complementary flags for all useful nondegenerate kernels',
                fixed_table_changed=True,runtime_basis_adapter=False,
                giant_basis_table_prime_materialized=False,
                setup='Finite deterministic reflection construction, new native table and shared admissible odd prime; eventual fixed setup separate',
                saving_decimal_lower=rational_decimal_lower(a,18))


def promoted_input(producer,promotion,promotion_path,producer_path,source_dir):
    require(promotion['status']=='PASS independent compound actual-frame h53 finite witness',
            'Independent compound finite promotion absent')
    check_sources(promotion,source_dir);check_input_hashes(promotion)
    require(promotion['input_sha256'][str(producer_path)]==sha(producer_path),
            'Independent compound producer bytes differ')
    row=producer['rows'][0];full=promotion['full'];h,R=row['h'],row['compiled_roles']
    require((h,R)==(full['h'],full['roles']) and h==53 and
            producer['candidate_id']==row['candidate_id']==promotion['candidate_id'] and
            row['final']['checked']['compiled_sha256']==full['final_compiled_sha256'],
            'Selected compound identity differs')
    require(full['current_actual_frames_retained_at_all_stages'] and
            not full['old_baseline_physical_replayed'] and not full['producer_cloner_selector_imported'],
            'Independent current actual-frame/history premise absent')
    require(promotion['reference_commit']=='bcd4ebde8692383539f8a48734e5fbf3a18a32c2',
            'Independent compound review changed immutable upstream')
    for k in ('all_global_coefficients_exact','all_additions_disjoint'):
        require(full['logical'][k],'Selected scalar graph failed '+k)
    for k in ('every_gate_output_exact','every_physical_target_exact','cancellation_free_over_any_scalar_field'):
        require(full['physical'][k],'Selected physical graph failed '+k)
    for k in ('all_input_frames_original_lines','all_output_frames_exact',
              'all_source_spans_contained_in_actual_frames','every_designated_target_orthogonal',
              'forward_and_reverse_complement_nesting'):
        require(full['rational_frames'][k],'Selected native graph failed '+k)
    dirty=promotion['small_control']['complete_invocation_dirty_basis']
    require({r['inverse'] for r in dirty}=={False,True} and all(r['exact_linear_map'] for r in dirty),
            'Fresh compound complete dirty invocation controls absent')
    n=network_counts(h,R)
    for key in ('h','v','m','N','W','L','D','s'):
        require(full['exact_counts'][key]==n[key],'Independent actual network count differs '+key)
        if key!='v':require(row['exact_counts'][key]==n[key],'Producer actual rank count differs '+key)
    require(full['exact_counts']['R']==R and row['exact_counts']['side_roles']==R,
            'Actual physical side role count differs')
    audit=audit_boundary_histogram(row['exact_counts'],h,R)
    timeline=full['independent_actual_rank_timeline']
    require(timeline['exact_aggregate_rank_histogram']==row['exact_counts']['rank_histogram'] and
            timeline['rank_sum']==n['s'] and timeline['edge_count']==row['exact_counts']['edge_count'] and
            not timeline['producer_aggregate_rank_functions_imported'],
            'Independent actual chronological rank histogram differs')
    require(row['literal_scalar_guard']==full['literal_scalar_guard'] and
            full['literal_scalar_guard']['slack']>0,'Selected actual literal bit guard differs')
    return row,n,audit,dict(status='INDEPENDENT COMPOUND FINITE PROMOTION PASS',h=h,roles=R,
        candidate_id=promotion['candidate_id'],compiled_sha256=full['final_compiled_sha256'],
        counts=n,path=str(promotion_path),sha256=sha(promotion_path),
        source_actual_frames_all_rounds=True,old_baseline_physical_replayed=False,
        dirty_control_basis_per_direction=[x['input_basis_vectors'] for x in dirty],
        independent_actual_chronological_histogram_exact=True,
        new_fixed_table_prime_required=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('previous-assembly','previous-review','compound-producer','compound-promotion',
                'compound-transfer-report','generic-construction-report'):
        ap.add_argument('--'+key,type=Path,required=True)
    ap.add_argument('--compound-transfer-report-sha256',required=True)
    ap.add_argument('--generic-construction-report-sha256',required=True)
    ap.add_argument('--include-protected-one',action='store_true')
    ap.add_argument('--protected-report',type=Path)
    ap.add_argument('--protected-report-sha256')
    ap.add_argument('--protected-count-review',type=Path)
    ap.add_argument('--include-protected-two',action='store_true')
    ap.add_argument('--two-protected-report',type=Path)
    ap.add_argument('--two-protected-report-sha256')
    ap.add_argument('--two-protected-review',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path');start=time.monotonic()
    source_dir=Path(__file__).parent
    old=json.loads(args.previous_assembly.read_text());accepted=json.loads(args.previous_review.read_text())
    producer=json.loads(args.compound_producer.read_text());promotion=json.loads(args.compound_promotion.read_text())
    check_sources(old,source_dir);check_sources(accepted,source_dir,'review_whole_complex_assembly.py')
    check_input_hashes(accepted)
    require(accepted['status']=='PASS independent complete whole-complex generic-bit conditional assembly' and
            accepted['input_sha256'][str(args.previous_assembly.resolve())]==sha(args.previous_assembly),
            'Previous complete whole-complex acceptance absent')
    for p,d in ((args.compound_transfer_report,args.compound_transfer_report_sha256),
                (args.generic_construction_report,args.generic_construction_report_sha256)):
        require(p.is_file() and sha(p)==d,'Frozen complete analytic transfer report differs')
    previous=max(Q(r['kappa']) for r in accepted['rows'])
    require(previous==max(Q(r['parameters']['kappa']) for r in old['witnesses']),
            'Previous exact complete kappa differs')
    oldp=old['generic_characteristic_certificate']['witness'];nc=parse_counts(old['witnesses'][0]['complex_counts'])
    phase=old['whole_complex_characteristic'];phase['chosen_saving']=Q(phase['chosen_saving'])
    phase['strict_primitive_gap']=Q(phase['strict_primitive_gap'])
    G=old['accepted_whole_complex_transfer']['literal_enhanced_guard']['G'];regressions=[]
    for row in old['witnesses']:
        regenerated=old_whole_witness(parse_counts(row['bit_counts']),nc,row['mode'],row['prefix'],
            Q(row['previous_accepted_kappa']),oldp,phase,G)
        for key in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b',
                    'stopped_leaf_certificate','compact_row_padding'):
            require(as_strings(regenerated[key])==row[key],'Unchanged wholeC regression differs '+key)
        regressions.append(dict(mode=row['mode'],prefix=row['prefix'],kappa=row['parameters']['kappa'],unchanged=True))
    row,n,audit,finite=promoted_input(producer,promotion,args.compound_promotion,args.compound_producer,source_dir)
    variants=[0];protected_audit=None;two_protected_audit=None;paths=[args.previous_assembly,args.previous_review,args.compound_producer,
        args.compound_promotion,args.compound_transfer_report,args.generic_construction_report]
    if args.include_protected_one:
        require(args.protected_report and args.protected_count_review and
                sha(args.protected_report)==args.protected_report_sha256,'Protected construction review absent')
        protected_audit=json.loads(args.protected_count_review.read_text())
        require(protected_audit['status']=='PASS','Protected count/scalar/native review absent')
        variants.append(1);paths.extend((args.protected_report,args.protected_count_review))
    if args.include_protected_two:
        require(args.two_protected_report and args.two_protected_review and
                sha(args.two_protected_report)==args.two_protected_report_sha256,
                'Two-disjoint-center independent report absent')
        two_protected_audit=json.loads(args.two_protected_review.read_text())
        require(two_protected_audit['status'].startswith('PASS'),
                'Two-disjoint-center independent control absent')
        variants.append(2);paths.extend((args.two_protected_report,args.two_protected_review))
    witnesses=[];primitives=[]
    for protect in variants:
        primitive=generic_characteristic(n['h'],n['side_roles'],protect);newn=primitive['counts']
        for name,key in (('middle','final_middle'),('joined','joined'),('data','stage3_data')):
            require(primitive['family_ranks'][name]==audit[key+'_copies']*audit[key+'_residual_rank'],
                    'Generic credited family differs from actual changed boundary '+name)
        a=primitive['saving'];b=phase['chosen_saving'];require(b>2*a,'Fixed-half complex leaf feasibility failed')
        newphase={**phase,'phase_above_twice_bit':b-2*a,'beta_half_leaf_above_bit':b/2-a,
                  'new_native_bit_saving':a}
        for mode in ('conservative','tight'):
            for prefix in ('original','balanced'):
                witness=whole_witness(newn,nc,mode,prefix,previous,primitive,newphase,G)
                witness['native_construction_id']=primitive['construction_id']
                witness['native_bit_primitive']=dict(kind=primitive['certificate_kind'],protected_centers=protect,
                    actual_compound_finite_identity=finite,normal_boundary_histogram=audit,
                    protected_rank_change=6*protect*n['v']**2,
                    protected_histogram_scope='Normal actual histogram plus separately reviewed changed center rank theorem' if protect else 'Complete actual normal histogram',
                    actual_bit_literal_guard=row['literal_scalar_guard'],
                    changed_fixed_table_prime_required=True,giant_native_table_materialized=False)
                witness['whole_complex_transfer']={**old['accepted_whole_complex_transfer'],
                    'changed_bit_product_stock':witness['compact_row_padding'],
                    'old_combined_rows_historical_only':True}
                witnesses.append(witness)
        primitives.append(primitive)
    dependencies={p.name:sha(p) for p in source_dir.glob('downstream_*.py')
                  if p.name in ('downstream_compound_whole_semantic_bulk.py','downstream_compound_whole_parameters.py',
                    'downstream_whole_complex_parameters.py','downstream_whole_complex_semantic_bulk.py',
                    'downstream_descendant_joined_characteristic.py','downstream_gaussian.py',
                    'downstream_rotated_batch_characteristic.py','downstream_parameter_optimum.py')}
    result=dict(status='PASS STRICT COMPOUND-BIT WHOLE-COMPLEX ASSEMBLY; FINAL INDEPENDENT REVIEW REQUIRED',
        campaign_start='2026-10-07T22:25:21Z',campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
        generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=dependencies,
        input_sha256={str(p):sha(p) for p in paths},previous_accepted_kappa=previous,
        accepted_wholeC_regressions=regressions,compound_finite_audit=finite,
        actual_boundary_histogram_audit=audit,generic_characteristics=primitives,
        complex_counts_unchanged=nc,complex_scalar_G_unchanged=G,
        protected_input_audit=protected_audit,two_protected_input_audit=two_protected_audit,
        witnesses=witnesses,elapsed_seconds=time.monotonic()-start,
        scope='Fresh actual compound h53 finite identity/rank categories and normalized strict characteristic. New ground-specific depth and complete PRODUCT stock. Protected center has a distinct construction/table/prime; original accepted rows remain bytewise unchanged. All fixed giant basis/table/prime/layout/absorption/full-machine thresholds remain separately eventual.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for w in witnesses:
        print(w['native_construction_id'],w['mode'],w['prefix'],w['parameters']['kappa'],
              w['compact_row_padding']['polynomial_degree'],w['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
