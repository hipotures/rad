#!/usr/bin/env python3
"""Pinned complete generic-basis assembly at general rational stopping beta."""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_batched_semantic_bulk_assembly import batch_witness
from downstream_gaussian import require
from downstream_general_beta_semantic_bulk import complex_counts,general_witness
from downstream_generic_metric_characteristic import generic
from downstream_parameter_optimum import as_strings
from downstream_promoted_complex_composition import parse_counts
from downstream_uncapped_middle_semantic_bulk import uncapped_row_padding


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def check_complex_controller(review,source_dir):
    require(review['status']=='Terminal independent complex controller finite/transfer PASS',
            'Independent complex controller proof absent')
    for name,digest in review['independent_source_sha256'].items():
        require(sha(source_dir/name)==digest,'Independent complex source differs '+name)
    small=next(r for r in review['rows'] if r['h']==8)
    dirty=small['complete_dirty_basis'];exchange=small['complete_shared_exchange']
    require(dirty['complete_basis_dimension']==951 and
            dirty['forward_identity_shear_and_inverse_exact'] and
            dirty['includes_both_data_banks_all_side_and_central_scratch'] and
            exchange['all_data_outputs_exact'] and exchange['all_dirty_banks_restored_exactly'] and
            exchange['middle_chronology_reversed_and_inverted'],
            'Independent changed complex complete-dirty/shared-bank controls absent')
    row=next(r for r in review['rows'] if r['h']==28)
    n=complex_counts(28,92309)
    require(parse_counts(row['counts'])==n,'Independent complex controller counts differ')
    for key in ('all_original_edges_and_terminal_complements_nonalternating',):
        require(row['logical'][key],'All-size original complex residual premise failed')
    for key in ('all_copy_outputs_source_lines_and_target_kernels_valid',
                'all_nonzero_forward_reverse_residuals_have_norm_one_witness',
                'all_scalar_coefficients_exact_without_modular_cancellation'):
        require(row['physical'][key],'Independent complete complex witness failed '+key)
    require(row['matching']['exact_orthogonal_involution'] and
            row['matching']['all_join_residuals_have_coordinate_norm_one_witness'] and
            row['matching']['triples']==n['v'] and row['matching']['joined_residual_dimension']==n['m']-2*n['h'],
            'Independent complex sharing/nonalternating join premise failed')
    require(row['chains']['all_chain_edges_exact'] and
            row['chains']['retained_at_most_one_argument_per_gate'],
            'Changed complex controller capacity/containment absent')
    g=row['guard'];G=g['actual_grouped_scalar_gates']
    E=64*(n['W']+n['m']+1)**3;depth=2*G*n['W']*n['W']+4*n['s']+4*n['W']+4
    B=n['s']+E;C0=32*n['m']*B*B
    require(g['exact_grouped_gate_bound_used'] and not g['old_six_W_condition'] and
            E==g['additive_E'] and depth==g['exact_saved_input_operation_depth_bound'] and
            E-depth==g['operation_depth_slack']>0 and C0==g['semantic_C0'] and g['semantic_C1']==1,
            'Actual complex-G/E/semantic guard arithmetic differs')
    # Both accepted cases have the identical logical Gaussian gate graph.
    # Retained controller links alter physical roles, not the macro node
    # gate count. Derive the old actual count from its accepted R=c+2v.
    c=row['logical']['logical_frames']-n['v']
    require(c+2*n['v']==97586 and G==3*n['v']*n['v']*(4*(c+n['v'])+4*n['v']+4),
            'Shared logical macro-gate count with original complex case differs')
    return n,G,dict(status='INDEPENDENT COMPLEX CONTROLLER FINITE/SCALAR/GUARD PASS',
                   h=28,roles=92309,compiled_sha256=row['physical']['compiled_sha256'],
                   counts=n,actual_grouped_scalar_gates=G,
                   exact_literal_depth=depth,exact_guard_slack=E-depth,
                   old_six_W_condition=False,complete_dirty_h8_basis=951,
                   source_sha256=review['independent_source_sha256'])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--previous-descendant-assembly',type=Path,required=True)
    ap.add_argument('--previous-final-review',type=Path,required=True)
    ap.add_argument('--generic-characteristic',type=Path,required=True)
    ap.add_argument('--root-generic-inputs',type=Path,required=True)
    ap.add_argument('--complex-controller-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic();source_dir=Path(__file__).parent
    old=json.loads(args.previous_descendant_assembly.read_text())
    final=json.loads(args.previous_final_review.read_text())
    primitive=json.loads(args.generic_characteristic.read_text())
    root=json.loads(args.root_generic_inputs.read_text())
    complex_review=json.loads(args.complex_controller_review.read_text())
    for document in (old,primitive):
        for name,digest in document['source_sha256'].items():
            require(sha(source_dir/name)==digest,'Frozen producer/root source differs '+name)
    root_sources={'review_generic_composition_inputs.py':root['source_sha256']}
    for name,digest in root_sources.items():
        require(sha(source_dir/name)==digest,'Independent root generic source differs '+name)
    for name,digest in final['reviewer_source_sha256'].items():
        require(sha(source_dir/name)==digest,'Accepted final checker source differs '+name)
    require(final['status'].startswith('PASS') and
            final['input_sha256'][str(args.previous_descendant_assembly.resolve())]==sha(args.previous_descendant_assembly),
            'Previous complete descendant result is not independently accepted')
    previous=max(Q(r['kappa']) for r in final['rows'])
    require(previous==max(Q(r['parameters']['kappa']) for r in old['witnesses']),
            'Previous complete accepted kappa differs')
    require(root['status']=='PASS root independent generic-basis inputs and written theorem review' and
            root['written_all_size_proof_reviewed'] and not root['runtime_basis_adapter'] and
            not root['all_h51_ambient_basis_instantiated'],
            'Root all-size generic construction/fixed-setup review absent')
    finite=primitive['odd_bit_finite_audit']
    require(finite==old['odd_bit_finite_audit'] and
            root['finite_candidate_id']==finite['candidate_id'] and
            root['finite_compiled_sha256']==finite['compiled_sha256'],
            'Generic constructive basis and promoted actual frame identity differ')
    p=primitive['witness'];n=parse_counts(p['counts'])
    require(as_strings(generic(n['h'],n['side_roles']))==p,
            'Generic exact characteristic regeneration differs')
    peer=root['independent_characteristic']
    for key in ('v','m','N','W','L','D','s'):
        require(peer['counts'][key]==n[key],'Root generic count differs '+key)
    require(peer['roles']==n['side_roles'] and peer['kernels']==p['kernel_dimensions'] and
            peer['family_ranks']==p['family_ranks'] and peer['run_lengths']==p['grouped_runs'] and
            peer['maximum_child']==p['maximum_child_rank'] and peer['row_degree']==66000 and
            peer['reservoir_slope']==264000 and peer['exact_depth_binary_power_verified'] and
            peer['old_2600_claim_rejected'] and
            Q(peer['chosen_saving'])>=Q(p['saving']) and Q(peer['strict_characteristic_gap'])>0,
            'Root full generic characteristic/depth/count review differs')
    require(any(r.get('actual_tensor_data_complement') and r['full_metric_identity'] and
                r['all_primal_dual_conjugations'] for r in root['independent_small_controls']),
            'Independent actual data-family common-basis control absent')
    newnc,G,newaudit=check_complex_controller(complex_review,source_dir)
    oldnc=parse_counts(old['witnesses'][0]['complex_counts'])
    require(oldnc==complex_counts(28,97586),'Original accepted complex case differs')
    regressions=[]
    for row in old['witnesses']:
        oldp=old['descendant_characteristic_certificate']['witness']
        actual=batch_witness(n,oldnc,row['mode'],row['prefix'],Q(row['previous_accepted_kappa']),oldp)
        for group in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group])==row[group],
                    'Accepted descendant predecessor regression differs '+group)
        require(as_strings(uncapped_row_padding(actual))==row['compact_row_padding'],
                'Accepted old p^2600 row regression differs')
        general=general_witness(n,oldnc,row['mode'],row['prefix'],Q(row['previous_accepted_kappa']),
                                oldp,G,beta_override=Q(1,2),native_stock=False)
        for group in ('parameters','recurrence','margins'):
            require(as_strings(general[group])==row[group],
                    'General-beta half-stop specialization differs '+group)
        regressions.append(dict(mode=row['mode'],prefix=row['prefix'],kappa=row['parameters']['kappa'],
                                unchanged=True,general_beta_half_specialization_exact=True))
    rows=[]
    for nc,label in ((oldnc,'original97586'),(newnc,'controller92309')):
        for mode in ('conservative','tight'):
            for prefix in ('original','balanced'):
                row=general_witness(n,nc,mode,prefix,previous,p,G)
                row['complex_input']=label
                row['native_bit_primitive']=dict(
                    certificate_kind=p['certificate_kind'],chosen_saving=Q(p['saving']),
                    strict_taylor_gap=Q(p['strict_taylor_gap']),
                    basis='One constructively defined rational ambient metric isometry for all useful kernels',
                    full_h51_basis_table_prime_instantiated=False,runtime_basis_adapter=False,
                    maximum_child=p['maximum_child_rank'],depth_per_ceil_log2e=651,
                    row_degree=66000,reservoir_coefficient=264000,
                    factor_table='New fixed table for every actual conjugated source/gate/sink frame',
                    native_prime='One newly fixed admissible odd prime for the complete finite table; separate eventual setup',
                    all_other_actual_edges='Individual native children; actual changed rank histogram retained')
                rows.append(row)
    hashes=dict(old['source_sha256']);hashes.update(primitive['source_sha256'])
    for name in (Path(__file__).name,'downstream_general_beta_semantic_bulk.py'):
        hashes[name]=sha(source_dir/name)
    inputs=[args.previous_descendant_assembly,args.previous_final_review,args.generic_characteristic,
            args.root_generic_inputs,args.complex_controller_review]
    result=dict(status='PASS STRICT CONDITIONAL GENERIC GENERAL-BETA ASSEMBLY; INDEPENDENT FULL REVIEW REQUIRED',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
                generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
                original_reference=old['original_reference'],compact_reference=old['compact_reference'],
                input_files={str(q):dict(bytes=q.stat().st_size,sha256=sha(q)) for q in inputs},
                odd_bit_finite_audit=finite,original_complex_audit=old['promoted_complex_audit'],
                controller_complex_audit=newaudit,generic_characteristic_certificate=primitive,
                root_generic_inputs_sha256=sha(args.root_generic_inputs),
                independent_generic_source_sha256=primitive['independent_generic_source_sha256'],
                root_generic_source_sha256=root_sources,
                previous_complete_review_sha256=sha(args.previous_final_review),
                previous_accepted_kappa=previous,accepted_descendant_regressions=regressions,
                witnesses=rows,elapsed_seconds=time.monotonic()-started,
                scope='Eight complete original/balanced and conservative/tight rows for a new finite constructive metric basis at general rational stopping beta. Old complex and independently accepted controller complex are separate inputs; actual-G/E guards checked directly. d^beta>2m and p^66000 reservoirs are explicit. Giant native basis/table/prime/layout and strict absorption constants remain uninstantiated separate eventual setup; no complete headline before independent final review.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:
        print(result['status'],row['complex_input'],row['mode'],row['prefix'],
              row['parameters']['kappa'],row['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
