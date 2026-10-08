#!/usr/bin/env python3
"""Thin reviewed global-basis and exact-tensor-data assembly producer.

A newly fixed rational Bruhat table and odd prime belong to the bit
compiler. The separate complex circuit and numerical guard are unchanged.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_batched_semantic_bulk_assembly import batch_witness,row_padding_certificate
from downstream_gaussian import require
from downstream_parameter_optimum import as_strings
from downstream_promoted_complex_composition import parse_counts
from downstream_rotated_batch_characteristic import rotated


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--previous-data-assembly',type=Path,required=True)
    ap.add_argument('--rotated-characteristic',type=Path,required=True)
    ap.add_argument('--axis-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();require(not a.output.exists(),'Use a fresh output path')
    started=time.monotonic();source_dir=Path(__file__).parent
    old=json.loads(a.previous_data_assembly.read_text());characteristic=json.loads(a.rotated_characteristic.read_text())
    review=json.loads(a.axis_review.read_text())
    for name,expected in old['source_sha256'].items():
        require(sha(source_dir/name)==expected,'Frozen predecessor source changed '+name)
    require(sha(source_dir/'downstream_rotated_batch_characteristic.py')==characteristic['source_sha256'],
            'Rotated characteristic source changed')
    require(review['status'].startswith('PASS'),'Independent compiler-basis review not terminal')
    finite=old['odd_bit_finite_audit']
    require(review['finite_candidate_id']==finite['candidate_id'] and
            review['finite_compiled_sha256']==finite['compiled_sha256'],
            'Rotated compiler finite identity differs')
    require(review['whole_common_frame_controls']['consistent_source_gate_sink_conjugation_exact'] and
            review['whole_common_frame_controls']['unchanged_external_shear_and_role_swap'],
            'Complete conjugated-frame operator control absent')
    require(all(p['lifted_base_profile_exact'] and p['all_middle_pivots_batched'] and
                p['includes_contiguous_offdiagonal_block'] for p in review['middle_profiles']),
            'Independent complete middle lift absent')
    regressions=[]
    for row in old['witnesses']:
        n,nc=parse_counts(row['bit_counts']),parse_counts(row['complex_counts'])
        oldp=next(p for p in old['data_primitive_certificate']['witnesses'] if p['variant']==row['batch_variant'])
        actual=batch_witness(n,nc,row['mode'],row['prefix'],Q(row['previous_accepted_kappa']),oldp)
        for group in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group])==row[group],'Predecessor exact regression differs '+group)
        require(as_strings(row_padding_certificate(actual))==row['compact_row_padding'],
                'Predecessor row padding differs')
        regressions.append(dict(variant=row['batch_variant'],mode=row['mode'],prefix=row['prefix'],
                                kappa=row['parameters']['kappa'],unchanged=True))
    previous=max(Q(row['parameters']['kappa']) for row in old['witnesses'])
    n=parse_counts(old['witnesses'][0]['bit_counts']);nc=parse_counts(old['witnesses'][0]['complex_counts'])
    require(n['h']==51 and n['side_roles']==502265 and nc['h']==28 and nc['R']==97586,
            'Historical fixed input differs')
    rows=[]
    names={'two-family':'axis-middle-joined','tensor-data':'axis-middle-joined-data-exact'}
    for variant in ('two-family','tensor-data'):
        p=next(r for r in characteristic['witnesses'] if r['variant']==variant)
        require(as_strings(rotated(n['h'],n['side_roles'],variant))==p,
                'Rotated exact characteristic regeneration differs')
        peer=next(r for r in review['rows'] if r['variant']==names[variant])
        for key in ('h','m','N','W','L','D','s'):
            require(peer['counts'][key]==n[key],'Independent rotated count differs '+key)
        require(Q(peer['saving'])>=Q(p['saving']) and peer['total_rank_conserved'] and
                Q(peer['strict_normalized_characteristic_gap'])>0,
                'Declared saving lacks independent larger characteristic')
        require(peer['global_maximum_run']==n['h']**2 and p['maximum_child_rank']==n['h']**2,
                'Rotated child-size bound differs')
        for mode in ('conservative','tight'):
            for prefix in ('original','balanced'):
                row=batch_witness(n,nc,mode,prefix,previous,p);row['batch_variant']=variant
                row['compact_row_padding']=row_padding_certificate(row)
                row['native_bit_primitive']=dict(certificate_kind='GLOBAL-BASIS NEGATIVE-EXPONENTIAL TAYLOR',
                    chosen_saving=Q(p['saving']),strict_taylor_gap=Q(p['strict_taylor_gap']),
                    compiler_basis_order=[3,1,2],conjugation='M_v -> Q*M_v*Q^-1 at every source/gate/sink',
                    maximum_child_rank=n['h']**2,child_width_relation='r*floor(e/m)<=e/h',
                    depth='ceil(log_h e)',middle='(I-P_t) tensor I_(h^2), h-1 complete blocks',
                    data=('Pi_3 tensor Pi_12, all contiguous increasing blocks included' if variant=='tensor-data' else 'Unchanged individual pivots'),
                    factor_table='New fixed canonical rational Bruhat table for all conjugated edge matrices',
                    native_prime='A newly fixed odd prime avoiding every new factor/Gram denominator and required unit numerator',
                    complex_guard='Original h28 complex network, factors and numerical guard unchanged')
                row['proof_obligations'].insert(0,'Independent whole-frame global basis conjugation, full middle/offdiagonal lift, exact tensor data profiles and fixed new-prime bit transfer')
                row['additional_eventual_cutoffs'] += ['New fixed native rational factor/Gram table and admissible odd prime, independent of input width',
                    'Retained layout setup constant C for the new compiler: e<=C*p after p>=C']
                rows.append(row)
    hashes=dict(old['source_sha256']);hashes['downstream_rotated_batch_characteristic.py']=characteristic['source_sha256'];hashes[Path(__file__).name]=sha(Path(__file__))
    result=dict(status='PASS STRICT CONDITIONAL GLOBAL-BASIS ASSEMBLY; INDEPENDENT FINAL ARITHMETIC REVIEW REQUIRED',
        campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
        campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
        generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
        original_reference=old['original_reference'],compact_reference=old['compact_reference'],
        input_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in (a.previous_data_assembly,a.rotated_characteristic,a.axis_review)},
        odd_bit_finite_audit=finite,promoted_complex_audit=old['promoted_complex_audit'],
        previous_accepted_kappa=previous,predecessor_regressions=regressions,
        rotated_characteristic_certificate=characteristic,independent_axis_review_sha256=sha(a.axis_review),
        witnesses=rows,elapsed_seconds=time.monotonic()-started,
        scope='New global rational bit compiler basis and grouped middle/exact-data children; scalar circuit, roles and complex precision remain fixed. New fixed factor table/prime and eventual setup C are explicit; no runtime physical pivot gather is charged as free.')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:print(result['status'],row['batch_variant'],row['mode'],row['prefix'],
                         row['parameters']['kappa'],row['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
