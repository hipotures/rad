#!/usr/bin/env python3
"""Complete explicit tensor-data assembly for the reflected rational basis."""
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
from downstream_householder_characteristic import householder
from downstream_parameter_optimum import as_strings
from downstream_promoted_complex_composition import parse_counts
from downstream_uncapped_middle_semantic_bulk import uncapped_row_padding


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--previous-uncapped-assembly',type=Path,required=True)
    ap.add_argument('--reflection-characteristic',type=Path,required=True)
    ap.add_argument('--reflection-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic();source_dir=Path(__file__).parent
    old=json.loads(args.previous_uncapped_assembly.read_text())
    primitive=json.loads(args.reflection_characteristic.read_text())
    review=json.loads(args.reflection_review.read_text())
    for name,digest in old['source_sha256'].items():
        require(sha(source_dir/name)==digest,'Frozen uncapped assembly source differs '+name)
    for name,digest in primitive['source_sha256'].items():
        require(sha(source_dir/name)==digest,'Frozen reflected source differs '+name)
    require(review['status'].startswith('PASS') and review['new_address_table'] and
            review['no_runtime_basis_adapter'] and review['separate_complex_scalar_guard_unchanged'] and
            review['retained_uncapped_row_degree']==2600,
            'Independent full reflected table/guard transfer absent')
    finite=primitive['odd_bit_finite_audit']
    require(finite==old['odd_bit_finite_audit'] and
            review['finite_candidate_id']==finite['candidate_id'] and
            review['finite_compiled_sha256']==finite['compiled_sha256'] and
            review['whole_common_frame_controls']['exact_reflected_source_gate_sink_pipeline'],
            'Simultaneous reflected finite frame identity differs')
    require(primitive['independent_reflected_review_sha256']==sha(args.reflection_review),
            'Characteristic was not checked against this full review')
    regressions=[]
    for row in old['witnesses']:
        n,nc=parse_counts(row['bit_counts']),parse_counts(row['complex_counts'])
        p=next(r for r in old['uncapped_characteristic_certificate']['witnesses']
               if r['variant']==row['batch_variant'])
        actual=batch_witness(n,nc,row['mode'],row['prefix'],Q(row['previous_accepted_kappa']),p)
        for group in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group])==row[group],
                    'Uncapped predecessor regression differs '+group)
        require(as_strings(uncapped_row_padding(actual))==row['compact_row_padding'],
                'Uncapped p^2600 row regression differs')
        regressions.append(dict(variant=row['batch_variant'],mode=row['mode'],prefix=row['prefix'],
                                kappa=row['parameters']['kappa'],unchanged=True))
    previous=max(Q(r['parameters']['kappa']) for r in old['witnesses'])
    p=next(r for r in primitive['witnesses'] if r['variant']=='tensor-data')
    n=parse_counts(p['counts']);nc=parse_counts(old['witnesses'][0]['complex_counts'])
    require(n['h']==51 and n['side_roles']==500703 and nc['h']==28 and nc['R']==97586,
            'Historical finite inputs differ')
    require(as_strings(householder(n['h'],n['side_roles'],'tensor-data'))==p,
            'Reflected exact characteristic regeneration differs')
    peer=next(r for r in review['rows'] if r['data_rank']>0)
    for key in ('h','m','N','W','L','D','s'):
        require(peer['counts'][key]==n[key],'Independent reflected count differs '+key)
    require(Q(peer['explicit_saving'])>=Q(p['saving']) and
            Q(peer['strict_characteristic_gap'])>0 and
            peer['maximum_middle_child']==p['maximum_child_rank'],
            'Independent larger reflected characteristic absent')
    rows=[]
    for mode in ('conservative','tight'):
        for prefix in ('original','balanced'):
            row=batch_witness(n,nc,mode,prefix,previous,p)
            row['batch_variant']='reflected-tensor-data'
            row['compact_row_padding']=uncapped_row_padding(row)
            row['native_bit_primitive']=dict(
                certificate_kind='HOUSEHOLDER DENSE-LINE NEGATIVE-EXPONENTIAL TAYLOR',
                chosen_saving=Q(p['saving']),strict_taylor_gap=Q(p['strict_taylor_gap']),
                compiler_basis='Cycle(3,1,2)*(Q tensor Q tensor Q), Q=I-2J/51',
                simultaneous_frame_conjugation='Every source, gate, sink and incidence',
                middle='Uniform full runs h^2*(h-2), h^2',
                data='h-1 copies of h^2-2,1 per physical data edge',
                joined='Retained universal low-rank Jensen moment only',
                maximum_child_rank=p['maximum_child_rank'],child_ratio=Q(49,51),
                depth='ceil(log_(51/49)e)<=26ceil(log2e)',
                row_divisor='W^depth<p^2600 after p>=C and log2p>=25',
                factor_table='New fixed rational Bruhat table for all reflected frames',
                native_prime='A newly fixed admissible odd prime for the full reflected table; no numerical equality with the old prime is assumed',
                complex_guard='Original h28 R97586 network and semantic C0/C1 unchanged')
            row['proof_obligations'].insert(0,
                'Accepted complete H-orthogonal reflected frame/table pipeline, uniform dense-line profiles and new fixed-prime setup')
            row['additional_eventual_cutoffs'] += [
                'New fixed reflected native table, admissible odd prime and descriptor constants',
                'Retained layout setup C for reflected calls: e<=C*p after p>=C',
                'Complete untouched row stock divisible by W^depth, certified below p^2600']
            rows.append(row)
    hashes=dict(old['source_sha256']);hashes.update(primitive['source_sha256']);hashes[Path(__file__).name]=sha(Path(__file__))
    result=dict(status='PASS STRICT CONDITIONAL HOUSEHOLDER ASSEMBLY; INDEPENDENT FINAL ARITHMETIC REVIEW REQUIRED',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
                generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
                original_reference=old['original_reference'],compact_reference=old['compact_reference'],
                input_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in
                    (args.previous_uncapped_assembly,args.reflection_characteristic,args.reflection_review)},
                odd_bit_finite_audit=finite,promoted_complex_audit=old['promoted_complex_audit'],
                previous_accepted_kappa=previous,uncapped_predecessor_regressions=regressions,
                reflected_characteristic_certificate=primitive,
                independent_reflection_review_sha256=sha(args.reflection_review),
                witnesses=rows,elapsed_seconds=time.monotonic()-started,
                scope='Four explicit exact tensor-data parameter rows in a newly fixed H-orthogonal native rational basis/table. Separate complex guard and all semantic/bulk inequalities unchanged; p^2600 depth qualification explicit. The two-family primitive remains a comparison, because it is below the preceding global tensor-data headline. Sharper joined refinements are excluded.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:
        print(result['status'],row['mode'],row['prefix'],row['parameters']['kappa'],
              row['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
