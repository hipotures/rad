#!/usr/bin/env python3
"""Thin exact composition of an independently promoted h50 bit candidate.

No graph is replayed: input identity, all independent promotion checks,
known bit counts, and the previously accepted complex assembly regressions
are verified before recomputing exact parameters.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from downstream_complex_assembly import compose
from downstream_gaussian import check_sources,network_counts,require
from downstream_parameter_optimum import as_strings,rational_decimal_lower


def parse_counts(n):
    return {k:(Q(v) if k=='eta' else v) for k,v in n.items()}


def promoted(candidate,review,reference,candidate_bytes):
    full=review['full'];r=candidate['compiled_roles'];h=candidate['h']
    require(review['status']=='PASS' and review['completed_utc'],'Independent promotion is not terminal PASS')
    require(review['reference_commit']==reference,'Promotion uses a different immutable reference')
    require(review['candidate_file_sha256']==hashlib.sha256(candidate_bytes).hexdigest(),
            'Promotion was for a different producer candidate')
    identity=dict(h=h,base=candidate['base'],positions=candidate['positions'],reference_commit=reference)
    candidate_id=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    require(candidate_id==candidate['candidate_id']==full['candidate_id'],'Candidate identity changed')
    require(h==full['h']==50 and r==full['roles'],'This composition requires promoted uniform h50 counts')
    require(full['base']==candidate['base'] and full['positions']==candidate['positions'],
            'Promoted singleton recipe changed')
    require(full['compiled_sha256']==candidate['checked']['compiled_sha256'],
            'Promoted physical program digest changed')
    require(full['matches_immutable_producer_identity_and_compilation'], 'Producer compilation is not independently matched')
    logical=full['logical'];physical=full['physical'];frames=full['rational_frames'];plan=full['controller_plan']
    for key in ('all_additions_disjoint','all_global_coefficients_exact','all_source_spans_have_common_point'):
        require(logical[key],'Missing independent logical premise '+key)
    for key in ('cancellation_free_over_any_scalar_field','every_gate_output_exact','every_physical_target_exact'):
        require(physical[key],'Missing independent physical coefficient premise '+key)
    for key in ('all_input_frames_original_lines','all_output_frames_exact','every_designated_target_orthogonal',
                'forward_and_reverse_complement_nesting'):
        require(frames[key],'Missing independent rational frame premise '+key)
    for key in ('all_links_same_source_and_acyclic','all_retained_labels_nested_by_equations'):
        require(plan[key],'Missing independent controller premise '+key)
    require(plan['independently_counted_roles']==r==logical['additions']+logical['outputs']-plan['selected_links'],
            'Promoted physical role count is not independently reconstructed')
    matching=full['stage_matching']
    require(matching['intersection_one'] and matching['distinct']==matching['images']==19600,
            'Retained bit stage joining is not validated')
    require(len(review['small_controls'])>=2,'Complete small promotion controls absent')
    basis=exchanges=0
    for small in review['small_controls']:
        require(len(small['complete_invocation_dirty_basis_including_centers'])==2,
                'Promotion lacks both dirty invocation directions')
        for b in small['complete_invocation_dirty_basis_including_centers']:
            require(b['exact_linear_map'],'Small dirty basis failed');basis+=b['input_basis_vectors']
        for e in small['complete_shared_three_stage_exchange']:
            require(e['bank_exchange'] and e['all_scratch_restored'],'Small full stage exchange failed');exchanges+=1
    require(exchanges>=4,'Four independent stage exchange controls absent')
    return network_counts(h,r),dict(candidate_id=candidate_id,roles=r,
                                   compiled_sha256=full['compiled_sha256'],
                                   nonzero_coefficients=logical['nonzero_partial_coefficients'],
                                   logical_frames=frames['logical_frames'],physical_frame_transitions=frames['physical_frame_transitions'],
                                   independently_counted_roles=plan['independently_counted_roles'],
                                   dirty_invocation_basis_checks=basis,full_stage_exchange_controls=exchanges)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--promotion-review',type=Path,required=True)
    ap.add_argument('--complex-certificate',type=Path,required=True)
    ap.add_argument('--previous-assembly',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    start=time.monotonic();reference=check_sources(args.upstream)
    candidate_bytes=args.candidate.read_bytes();candidate=json.loads(candidate_bytes)
    review=json.loads(args.promotion_review.read_text());cx=json.loads(args.complex_certificate.read_text())
    previous=json.loads(args.previous_assembly.read_text())
    require(cx['provenance']['commit']==previous['provenance']['commit']==reference['commit'],
            'Complex/assembly inputs disagree on reference')
    source=Path(__file__)
    for name,expected in previous['source_sha256'].items():
        require(hashlib.sha256((source.parent/name).read_bytes()).hexdigest()==expected,
                'Previously executed dependency changed '+name)
    regressions=[]
    for row in previous['witnesses']:
        actual=compose(parse_counts(row['bit_counts']),parse_counts(row['complex_counts']),row['mode'],
                       Q(row['old_accepted_phase_kappa']))
        for group in ('parameters','margins','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group])==row[group],'Unchanged assembly regression failed '+group)
        require(actual['minimum_margin']==Q(row['minimum_margin']) and actual['scoped_model_upper']==Q(row['scoped_model_upper']),
                'Unchanged accepted margin/ceiling regression failed')
        regressions.append(dict(mode=row['mode'],complex_W=row['complex_counts']['W'],
                                kappa=row['parameters']['kappa'],all_parameters_slacks_margins_and_cutoffs_exact=True))
    n,audit=promoted(candidate,review,reference['commit'],candidate_bytes)
    complex_row=next(r for r in cx['cases'] if r['h']==50)
    require(complex_row['terminal']['every_terminal_complement_nondegenerate_nonalternating'],
            'Reviewed complex terminal premise absent')
    require(complex_row['matching']['involution'] and complex_row['guard']['stopped_depth_branching_premise'],
            'Reviewed complex sharing/guard premise absent')
    nc=parse_counts(complex_row['shared_complex_counts'])
    old_shared=next(r for r in previous['witnesses'] if r['mode']=='tight' and r['complex_counts']['W']==nc['W'])
    old_kappa=Q(old_shared['parameters']['kappa'])
    witnesses=[compose(n,nc,mode,Q(old_shared['old_accepted_phase_kappa'])) for mode in ('conservative','tight')]
    tight=witnesses[1]
    require(tight['parameters']['kappa']>old_kappa,'Promoted bit circuit did not strictly improve accepted kappa')
    # Recheck every inherited rank formula directly, independently of recipe.
    v,m,N=n['v'],n['m'],n['N'];roles=audit['roles']
    require(n['W']==2*N+2*v*v*(roles+50) and n['L']==3*v*v*50*50,
            'Inherited bit role/central rank formula changed')
    require(n['D']==N-2*n['L'] and n['s']==n['W']*m-n['D'] and n['eta']==Q(n['D'],n['W']*m),
            'Inherited bit deficit/telescoping formula changed')
    require(nc['W']==2*nc['N']+2*nc['v']**2*(nc['R']+51) and nc['L']==3*nc['v']**2*51*50,
            'Accepted complex role/central formula changed')
    dependencies=['downstream_promoted_complex_composition.py','downstream_complex_assembly.py',
                  'downstream_complex_certificate.py','downstream_complex_circuit.py',
                  'downstream_gaussian.py','downstream_parameter_optimum.py']
    result=dict(status='PASS thin exact promoted composition; inherited independently reviewed finite/analytic interfaces',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',campaign_deadline='2026-10-08T08:25:21Z',
                provenance=reference,generated_at=datetime.now(timezone.utc).isoformat(),
                input_files={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in
                             (args.candidate,args.promotion_review,args.complex_certificate,args.previous_assembly)},
                source_sha256={name:hashlib.sha256((source.parent/name).read_bytes()).hexdigest() for name in dependencies},
                promoted_finite_audit=audit,unchanged_assembly_regressions=regressions,witnesses=witnesses,
                previous_accepted_kappa=old_kappa,strict_improvement_factor=tight['parameters']['kappa']/old_kappa,
                improvement_factor_decimal_lower=rational_decimal_lower(tight['parameters']['kappa']/old_kappa,15),
                elapsed_seconds=time.monotonic()-start,
                scope='New promoted bit recipe, accepted shared complex629617 and phase/decaying estimate; no full graph replay, universal optimum or unconditional theorem claim')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    print('PASS promoted roles',roles,'kappa',tight['parameters']['kappa'],
          'baseline ratio >=',tight['kappa_ratio_decimal_lower'],'cutoff',tight['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
