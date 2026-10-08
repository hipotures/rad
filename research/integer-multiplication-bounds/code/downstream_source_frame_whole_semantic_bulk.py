#!/usr/bin/env python3
"""Fresh complete source-framed bit/whole-complex conditional assembly.

Only the reviewed middle source and sink charts change. The same accepted
three-family complex histogram is recertified at b=1.4e-6; beta=1/8 makes
its leaf clear of the new bit saving. No PR15 all-rank transfer is assumed.
"""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_closing_whole_semantic_bulk import bit_guard
from downstream_compound_whole_parameters import whole_witness as old_whole_witness
from downstream_source_frame_characteristic import bit_characteristic
from downstream_source_frame_parameters import whole_witness
from downstream_gaussian import require
from downstream_parameter_optimum import as_strings
from downstream_promoted_complex_composition import parse_counts
from downstream_whole_complex_semantic_bulk import check_sources,check_input_hashes


def sha(path):return sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('current-assembly','current-review','source-frame-component','source-frame-report',
                 'finite-source-frame-control','characteristic-screen','output'):
        ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--source-frame-report-sha256',required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path');t=time.monotonic()
    src=Path(__file__).parent
    old=json.loads(args.current_assembly.read_text());peer=json.loads(args.current_review.read_text())
    component=json.loads(args.source_frame_component.read_text())
    control=json.loads(args.finite_source_frame_control.read_text())
    screen=json.loads(args.characteristic_screen.read_text())
    check_sources(old,src);check_input_hashes(old)
    check_sources(peer,src,'review_closing_whole_assembly.py');check_input_hashes(peer)
    check_sources(component,src,'review_auxiliary_source_frames.py');check_input_hashes(component)
    check_sources(control,src,'finite_auxiliary_source_frames_v2.py');check_input_hashes(control)
    check_sources(screen,src);check_input_hashes(screen)
    require(peer['status']=='PASS independent complete closing direct-first h53 zero one two protected whole-complex assembly' and
            peer['input_sha256'][str(args.current_assembly.resolve())]==sha(args.current_assembly),
            'Current complete independently accepted closing checkpoint absent')
    require(component['status']=='PASS INDEPENDENT NONZERO AUXILIARY SOURCE TRANSFER COMPONENT' and
            sha(args.source_frame_report)==args.source_frame_report_sha256,
            'Frozen independent all-size source-frame transfer absent')
    require(control['status']=='PASS actual middle source-frame endpoints and native dirty gauge' and
            control['actual_side_endpoints']['every_actual_physical_role_has_D0_first_and_D1_last'] and
            control['actual_side_endpoints']['early_or_late_retained_gate_exclusions']==0 and
            control['centers']['exclusions']==0 and control['no_flow_solver'] and control['no_old_coefficient_replay'],
            'Actual saved-plan first/last source-frame incidence absent')
    require({x['inverse'] for x in control['native_endpoint_contract']['controls']}=={False,True} and
            all(x['complete_dirty_native_basis']==10192 and x['all_side_and_central_inputs_arbitrary'] and
                x['auxiliaries_restored_up_to_required_I_shear'] and x['omitted_sink_M_rejected']
                for x in control['native_endpoint_contract']['controls']),
            'Complete native endpoint-gauge arbitrary-dirty controls absent')
    finite=old['compound_finite_audit'];h,R=finite['h'],finite['roles'];v=old['generic_characteristics'][0]['counts']['v']
    require((h,R)==(53,529181) and control['candidate_id']==finite['candidate_id'] and
            control['compiled_sha256']==finite['compiled_sha256'] and
            control['actual_side_endpoints']['roles']==R and control['centers']['roles']==h,
            'Accepted changed physical program identity differs')
    previous=max(Q(r['kappa']) for r in peer['rows'])
    require(previous==max(Q(r['parameters']['kappa']) for r in old['witnesses']), 'Current accepted exact kappa differs')
    oldp={r['protected_centers']:r for r in old['generic_characteristics']};nc=parse_counts(old['complex_counts_unchanged']);G=old['complex_scalar_G_unchanged']
    regressions=[]
    for row in old['witnesses']:
        phase={**row['complex_branching_certificate'],
            'chosen_saving':Q(row['complex_branching_certificate']['chosen_saving']),
            'strict_primitive_gap':Q(row['complex_branching_certificate']['strict_primitive_gap'])}
        rebuilt=old_whole_witness(parse_counts(row['bit_counts']),nc,row['mode'],row['prefix'],
            Q(row['previous_accepted_kappa']),oldp[row['native_bit_primitive']['protected_centers']],phase,G)
        for key in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b',
                    'stopped_leaf_certificate','compact_row_padding'):
            require(as_strings(rebuilt[key])==row[key], 'Accepted closing twelve-row regression differs '+key)
        regressions.append(dict(native_construction_id=row['native_construction_id'],
            mode=row['mode'],prefix=row['prefix'],kappa=row['parameters']['kappa'],unchanged=True))
    phase={**old['witnesses'][0]['complex_branching_certificate']};b=Q(7,5*10**6)
    credited=phase['total_grouped_rank'];linear=10*nc['s']-Q(99,10)*credited;quad=50*nc['s']
    gap=nc['D']-b*linear-b*b*quad/(1-10*b)
    require(gap==Q(screen['complex_coarse_probes'][str(b)])>0, 'Same-histogram strict coarse complex saving failed')
    require(Q(phase['logarithm_intervals']['m'][1])<10 and
            all(Q(pair[0])>Q(99,10) for key,pair in phase['logarithm_intervals'].items() if key!='m'),
            'Retained actual log enclosures fail new coarse bounds')
    phase.update(chosen_saving=b,sigma=1-b,strict_primitive_gap=gap,independent_coarse_gap=gap,
        normalized_linear_upper=linear,normalized_quadratic_upper=quad,rank_log_moment_lower=Q(99,10)*credited,
        exact_sufficient_inequality='D-b*(10s-(99/10)*grouped_rank)-50s*b^2/(1-10b)>0',
        complex_source_frames_changed=False,all_rank_PR15_children_imported=False,
        recertification='Exactly the accepted three-family histogram; ln(m)<10, every grouped ln(r)>99/10')
    original_promotion=json.loads(Path(finite['path']).read_text());normal_guard=original_promotion['full']['literal_scalar_guard']
    component_rows={r['protected_centers']:r for r in component['variants']}
    primitives=[];witnesses=[]
    for protect in (0,1,2):
        p=bit_characteristic(h,R,protect);p['construction_id']=f'source-framed-h{h}-normal' if protect==0 else f'source-framed-h{h}-protected-{protect}-center'
        independent=component_rows[protect]
        require(p['saving']==Q(independent['saving']) and p['maximum_child_rank']==independent['maximum_child'] and
                p['depth_per_ceil_log2e']==independent['least_halving_degree']==974 and
                p['W_binary_upper_exponent']==independent['wire_log2_ceiling']==50,
                'Independent new source-frame characteristic/depth differs')
        for key in ('W','L','D','s','m','v','h','N'):
            require(p['counts'][key]==independent['counts'][key], 'Independent changed counts differ '+key)
        if protect in (0,2):
            actual=control['normal' if protect==0 else 'protected2'];hist=actual['rank_histogram']
            require(actual['rank_sum']==p['counts']['s']==sum(int(r)*n for r,n in hist.items()) and
                    actual['edge_count']==sum(hist.values()) and
                    actual['eligible_physical_roles']==(R+h)*v*v and
                    actual['new_entrance_rank']==0 and actual['new_exit_rank']==h**3-h and
                    hist[str(h**3-h)]==(R+h)*v*v and actual['source_frame_rank_concentration_preserves_rank_sum'],
                    'Actual changed normal/two-center source histogram differs')
        a=p['saving'];require(b*Q(7,8)>a and b<2*a, 'Costed beta-eighth leaf or old-half negative failed')
        newphase={**phase,'new_native_bit_saving':a,'phase_above_twice_bit':b-2*a,
            'beta_half_leaf_above_bit':b/2-a,'beta_eighth_leaf_above_bit':b*Q(7,8)-a}
        guard=bit_guard({'literal_scalar_guard':normal_guard},p['counts'],protect)
        for mode in ('conservative','tight'):
            for prefix in ('original','balanced'):
                w=whole_witness(p['counts'],nc,mode,prefix,previous,p,newphase,G)
                require(w['parameters']['beta']==Q(1,8) and w['compact_row_padding']['polynomial_degree']==123000 and
                        w['compact_row_padding']['sufficient_suffix_slope']==492000,
                        'New source-frame full beta/product stock differs')
                w['native_construction_id']=p['construction_id']
                w['native_bit_primitive']=dict(kind=p['certificate_kind'],protected_centers=protect,
                    actual_compound_finite_identity=finite,normal_boundary_histogram=old['actual_boundary_histogram_audit'],
                    source_frame_relocation=p['source_frame_relocation'],source_frame_component_path=str(args.source_frame_component),
                    source_frame_component_sha256=sha(args.source_frame_component),
                    actual_source_frame_endpoint_control_path=str(args.finite_source_frame_control),
                    actual_source_frame_endpoint_control_sha256=sha(args.finite_source_frame_control),
                    actual_bit_literal_guard=normal_guard,conservative_changed_center_bit_guard=guard,
                    protected_rank_change=6*protect*v*v,changed_fixed_table_prime_required=True,
                    giant_native_table_materialized=False)
                w['whole_complex_transfer']={**old['witnesses'][0]['whole_complex_transfer'],
                    'changed_bit_product_stock':w['compact_row_padding'],'old_combined_rows_historical_only':True}
                witnesses.append(w)
        primitives.append(p)
    paths=(args.current_assembly,args.current_review,args.source_frame_component,args.source_frame_report,
           args.finite_source_frame_control,args.characteristic_screen)
    names=('downstream_source_frame_whole_semantic_bulk.py','downstream_source_frame_parameters.py',
           'downstream_source_frame_characteristic.py','downstream_closing_whole_semantic_bulk.py',
           'downstream_compound_whole_parameters.py','downstream_gaussian.py','downstream_rotated_batch_characteristic.py')
    result=dict(status='PASS STRICT NONZERO-SOURCE-FRAMED WHOLE-COMPLEX ASSEMBLY; FINAL INDEPENDENT REVIEW REQUIRED',
        campaign_start='2026-10-07T22:25:21Z',historical_deadline='2026-10-08T08:25:21Z',active_deadline='2026-10-08T10:00:00Z',
        generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256={n:sha(src/n) for n in names},
        input_sha256={str(p):sha(p) for p in paths},previous_accepted_kappa=previous,
        accepted_closing_twelve_row_regressions=regressions,compound_finite_audit=finite,
        source_frame_component_audit=component,actual_source_frame_endpoint_audit=control,
        actual_boundary_histogram_audit=old['actual_boundary_histogram_audit'],generic_characteristics=primitives,
        complex_counts_unchanged=nc,complex_scalar_G_unchanged=G,
        complex_new_coarse_saving=b,complex_new_coarse_gap=gap,complex_accepted_child_histogram_unchanged=True,
        witnesses=witnesses,elapsed_seconds=time.monotonic()-t,
        scope='New nonzero middle auxiliary source/sink chart and generic kernel h, independently reviewed on unchanged actual physical DAG. Same accepted three-family complex histogram recertified at b=1.4e-6; beta=1/8, fresh974native depth and123000joint stock. No new all-rank complex transfer is assumed. All twelve accepted predecessor rows remain unchanged. New native table/prime, fixed layout and strict absorption thresholds remain separately eventual.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for w in witnesses:print(w['native_construction_id'],w['mode'],w['prefix'],w['parameters']['kappa'],w['compact_row_padding']['polynomial_degree'],w['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
