#!/usr/bin/env python3
"""Closing whole-complex composition of one independently promoted early DAG.

This fresh adapter reads the selected single-case payload and the direct-
first-allocation audit. It preserves the accepted twelve-row predecessor,
reconstructs all native variants, and includes a conservative added-group
bit guard. No physical graph or prior allocation is replayed here.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_compound_whole_semantic_bulk import generic_characteristic
from downstream_compound_whole_parameters import whole_witness
from downstream_descendant_joined_characteristic import audit_boundary_histogram
from downstream_gaussian import network_counts, require
from downstream_parameter_optimum import as_strings
from downstream_promoted_complex_composition import parse_counts
from downstream_whole_complex_semantic_bulk import check_sources, check_input_hashes


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def closing_input(row, peer, ranking, source_dir, case_path, peer_path):
    require(peer['status']=='PASS INDEPENDENT CLOSING DIRECT-FIRST-ALLOCATION COMPOUND',
            'Fresh direct-first-allocation independent promotion absent')
    check_sources(peer, source_dir, 'review_early_compound_bit_witness.py')
    check_input_hashes(peer)
    require(peer['frozen_review_source_sha256']==sha(source_dir/'review_compound_bit_witness.py'),
            'Frozen independent native/frame reviewer differs')
    require(peer['input_sha256'][str(case_path)]==sha(case_path), 'Selected case bytes differ')
    require(not peer['old_allocation_parent_jobs_replayed'] and
            not peer['producer_allocator_cloner_selector_imported'],
            'Direct original-to-rounds independent scope absent')
    require(peer['reference_commit']=='bcd4ebde8692383539f8a48734e5fbf3a18a32c2',
            'Immutable upstream revision differs')
    full=peer['full'];nominee=ranking['nomination'];h,R=row['h'],row['compiled_roles']
    require(h==53 and (h,R)==(full['h'],full['roles'])==(nominee['h'],nominee['roles']) and
            row['candidate_id']==peer['candidate_id']==nominee['candidate_id'] and
            row['checked']['compiled_sha256']==full['final_compiled_sha256']==nominee['compiled_sha256'],
            'Selected closing case, nomination and independent identity differ')
    require(full['current_actual_frames_retained_at_all_stages'] and
            not full['old_baseline_physical_replayed'] and not full['producer_cloner_selector_imported'],
            'Actual-frame all-round induction absent')
    for key in ('all_global_coefficients_exact','all_additions_disjoint'):
        require(full['logical'][key], 'Independent scalar graph failed '+key)
    for key in ('every_gate_output_exact','every_physical_target_exact','cancellation_free_over_any_scalar_field'):
        require(full['physical'][key], 'Independent physical graph failed '+key)
    for key in ('all_input_frames_original_lines','all_output_frames_exact',
                'all_source_spans_contained_in_actual_frames','every_designated_target_orthogonal',
                'forward_and_reverse_complement_nesting'):
        require(full['rational_frames'][key], 'Independent native frame failed '+key)
    dirty=peer['small_control']['complete_invocation_dirty_basis']
    require({x['inverse'] for x in dirty}=={False,True} and all(x['exact_linear_map'] for x in dirty),
            'Fresh complete arbitrary-dirty invocation controls absent')
    counts=network_counts(h,R)
    for key in ('h','v','m','N','W','L','D','s'):
        require(full['exact_counts'][key]==counts[key], 'Independent actual count differs '+key)
        if key!='v':require(row['exact_counts'][key]==counts[key], 'Producer actual count differs '+key)
    require(full['exact_counts']['R']==R and row['exact_counts']['side_roles']==R,
            'Actual physical role count differs')
    boundary=audit_boundary_histogram(row['exact_counts'],h,R)
    timeline=full['independent_actual_rank_timeline']
    require(timeline['exact_aggregate_rank_histogram']==row['exact_counts']['rank_histogram'] and
            timeline['rank_sum']==counts['s'] and timeline['edge_count']==row['exact_counts']['edge_count'] and
            not timeline['producer_aggregate_rank_functions_imported'],
            'Independent chronological actual histogram differs')
    require(row['literal_scalar_guard']==full['literal_scalar_guard'] and
            row['literal_scalar_guard']['slack']>0, 'Actual normal literal bit guard differs')
    return counts,boundary,dict(status='INDEPENDENT CLOSING EARLY-ALLOCATION FINITE PROMOTION PASS',
        h=h,roles=R,candidate_id=peer['candidate_id'],compiled_sha256=full['final_compiled_sha256'],
        counts=counts,path=str(peer_path),sha256=sha(peer_path),
        direct_first_allocation=True,source_actual_frames_all_rounds=True,
        old_allocation_parent_jobs_replayed=False,old_baseline_physical_replayed=False,
        dirty_control_basis_per_direction=[x['input_basis_vectors'] for x in dirty],
        independent_actual_chronological_histogram_exact=True,new_fixed_table_prime_required=True)


def bit_guard(row, counts, protect):
    normal=row['literal_scalar_guard'];W,m,v=counts['W'],counts['m'],counts['v']
    E=64*(W+m+1)**3;G=normal['G']+3*protect*v*v
    depth=2*G*W*W+4*counts['s']+4*W+4
    require(normal['E']==E and E>depth, 'Conservative protected bit grouped-gate guard failed')
    return dict(status='PASS conservative changed-center bit grouped-gate bound',
        actual_normal_G=normal['G'],additional_group_upper=3*protect*v*v,G_upper=G,
        E=E,depth_upper=depth,strict_slack=E-depth,
        scope='Normal literal enumeration plus conservative added groups; no claimed protected literal enumeration',
        complex_guard_unchanged=True,each_output_f2_sum_terms_at_most_W=True,
        elementary_operation_bound_per_group=2*W*W)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('current-assembly','current-review','closing-case','closing-promotion',
                'closing-transfer-report','ranking','output'):
        ap.add_argument('--'+key,type=Path,required=True)
    ap.add_argument('--closing-transfer-report-sha256',required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path');start=time.monotonic()
    source_dir=Path(__file__).parent
    old=json.loads(args.current_assembly.read_text());accepted=json.loads(args.current_review.read_text())
    row=json.loads(args.closing_case.read_text());peer=json.loads(args.closing_promotion.read_text())
    ranking=json.loads(args.ranking.read_text())
    check_sources(old,source_dir);check_input_hashes(old)
    check_sources(accepted,source_dir,'review_compound_two_whole_assembly.py');check_input_hashes(accepted)
    check_sources(ranking,source_dir)
    require(accepted['status']=='PASS independent complete compound h53 zero one two protected whole-complex assembly' and
            accepted['input_sha256'][str(args.current_assembly.resolve())]==sha(args.current_assembly),
            'Current independently accepted twelve-row checkpoint absent')
    require(sha(args.closing_transfer_report)==args.closing_transfer_report_sha256,
            'Frozen closing all-size transfer report differs')
    require(ranking['nomination']['source_case']['sha256']==sha(args.closing_case) and
            ranking['unfinished_at_snapshot']==[], 'Closing ranking input identity differs')
    previous=max(Q(x['kappa']) for x in accepted['rows'])
    require(previous==max(Q(x['parameters']['kappa']) for x in old['witnesses']),
            'Current accepted exact kappa differs')
    primitives={x['protected_centers']:x for x in old['generic_characteristics']}
    require(set(primitives)=={0,1,2} and len(old['witnesses'])==12, 'Current native variants absent')
    nc=parse_counts(old['complex_counts_unchanged']);G=old['complex_scalar_G_unchanged']
    regressions=[]
    for w in old['witnesses']:
        protect=w['native_bit_primitive']['protected_centers'];p=primitives[protect]
        old_phase={**w['complex_branching_certificate'],
            'chosen_saving':Q(w['complex_branching_certificate']['chosen_saving']),
            'strict_primitive_gap':Q(w['complex_branching_certificate']['strict_primitive_gap'])}
        rebuilt=whole_witness(parse_counts(w['bit_counts']),nc,w['mode'],w['prefix'],
            Q(w['previous_accepted_kappa']),p,old_phase,G)
        for key in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b',
                    'stopped_leaf_certificate','compact_row_padding'):
            require(as_strings(rebuilt[key])==w[key], 'Accepted twelve-row regression differs '+key)
        regressions.append(dict(native_construction_id=w['native_construction_id'],
            mode=w['mode'],prefix=w['prefix'],kappa=w['parameters']['kappa'],unchanged=True))
    n,boundary,finite=closing_input(row,peer,ranking,source_dir,args.closing_case,args.closing_promotion)
    phase=old['witnesses'][0]['complex_branching_certificate'];phase={**phase,
        'chosen_saving':Q(phase['chosen_saving']),'strict_primitive_gap':Q(phase['strict_primitive_gap'])}
    native=[];witnesses=[]
    for protect in (0,1,2):
        primitive=generic_characteristic(n['h'],n['side_roles'],protect)
        primitive['construction_id']=f'closing-h{n["h"]}-normal' if protect==0 else f'closing-h{n["h"]}-protected-{protect}-center'
        for family,key in (('middle','final_middle'),('joined','joined'),('data','stage3_data')):
            require(primitive['family_ranks'][family]==boundary[key+'_copies']*boundary[key+'_residual_rank'],
                    'Generic family differs from actual closing boundary '+family)
        a=primitive['saving'];b=phase['chosen_saving'];require(b>2*a, 'Fixed-half leaf fails')
        if protect in (0,2):
            chosen=ranking['nomination_normal_primitive' if protect==0 else 'nomination_two_center_primitive']
            require(a==Q(chosen['saving']), 'Frozen nomination exact saving differs')
        changed_phase={**phase,'phase_above_twice_bit':b-2*a,
                       'beta_half_leaf_above_bit':b/2-a,'new_native_bit_saving':a}
        guard=bit_guard(row,primitive['counts'],protect)
        for mode in ('conservative','tight'):
            for prefix in ('original','balanced'):
                w=whole_witness(primitive['counts'],nc,mode,prefix,previous,primitive,changed_phase,G)
                w['native_construction_id']=primitive['construction_id']
                w['native_bit_primitive']=dict(kind=primitive['certificate_kind'],protected_centers=protect,
                    actual_compound_finite_identity=finite,normal_boundary_histogram=boundary,
                    protected_rank_change=6*protect*n['v']**2,
                    protected_histogram_scope='Normal actual histogram plus separately reviewed changed center rank theorem' if protect else 'Complete actual normal histogram',
                    actual_bit_literal_guard=row['literal_scalar_guard'],conservative_changed_center_bit_guard=guard,
                    changed_fixed_table_prime_required=True,giant_native_table_materialized=False)
                w['whole_complex_transfer']={**old['witnesses'][0]['whole_complex_transfer'],
                    'changed_bit_product_stock':w['compact_row_padding'],'old_combined_rows_historical_only':True}
                witnesses.append(w)
        native.append(primitive)
    require(max(w['parameters']['kappa'] for w in witnesses)==
            Q(ranking['nomination']['prospective_tight_balanced_wholeC_score']), 'Frozen nomination score differs')
    names=('downstream_closing_whole_semantic_bulk.py','downstream_compound_whole_semantic_bulk.py',
           'downstream_compound_whole_parameters.py','downstream_closing_candidate_rank.py',
           'downstream_whole_complex_parameters.py','downstream_whole_complex_semantic_bulk.py',
           'downstream_descendant_joined_characteristic.py','downstream_gaussian.py',
           'downstream_rotated_batch_characteristic.py','downstream_parameter_optimum.py')
    paths=(args.current_assembly,args.current_review,args.closing_case,args.closing_promotion,
           args.closing_transfer_report,args.ranking)
    result=dict(status='PASS STRICT CLOSING-EARLY-BIT WHOLE-COMPLEX ASSEMBLY; FINAL INDEPENDENT REVIEW REQUIRED',
        campaign_start='2026-10-07T22:25:21Z',campaign_original_deadline='2026-10-08T08:25:21Z',
        campaign_deadline='2026-10-08T10:00:00Z',generated_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256={name:sha(source_dir/name) for name in names},input_sha256={str(p):sha(p) for p in paths},
        previous_accepted_kappa=previous,accepted_twelve_row_regressions=regressions,
        compound_finite_audit=finite,actual_boundary_histogram_audit=boundary,generic_characteristics=native,
        complex_counts_unchanged=nc,complex_scalar_G_unchanged=G,
        protected_input_audit=old['protected_input_audit'],two_protected_input_audit=old['two_protected_input_audit'],
        witnesses=witnesses,elapsed_seconds=time.monotonic()-start,
        scope='Fresh independent direct-first-allocation actual DAG/histogram with distinct zero/one/two protected native constructions. Normal literal G and conservative added-group G_upper are distinguished. All twelve accepted predecessor rows numerically unchanged. New fixed table/prime and separate eventual setup, strict absorption and original conditional-machine thresholds remain explicit.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for w in witnesses:
        print(w['native_construction_id'],w['mode'],w['prefix'],w['parameters']['kappa'],
              w['compact_row_padding']['polynomial_degree'],w['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
