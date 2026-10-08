#!/usr/bin/env python3
"""Compose the reviewed full middle runs and promoted h51 clone.

Explicit variable-width depth and p^2600 row stock replace the earlier
h-fold/p^100 transfer. Numerical complex precision remains unchanged.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_batched_semantic_bulk_assembly import batch_witness, row_padding_certificate
from downstream_gaussian import ceil_q, require
from downstream_parameter_optimum import as_strings
from downstream_promoted_complex_composition import parse_counts
from downstream_semantic_bulk_assembly import compressed_power_certificate
from downstream_uncapped_middle_characteristic import uncapped_middle


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def uncapped_row_padding(row):
    """Strict reservoir domination for the reviewed logarithmic depth."""
    n = row['bit_counts']
    require(n['h']==51 and n['W']<2**49, 'Declared depth constant applies to h51')
    gap = 1-Q(row['parameters']['epsilon'])
    reciprocal = ceil_q(1/gap)
    cutoff = row['cutoff_log2_b']['common']
    require(cutoff>=25 and cutoff>=2*reciprocal,
            'Uncapped row-padding monotonicity cutoff failed')
    checks=[]
    for j in range(6):
        L=cutoff*2**j
        checks.append(dict(log2_b=L,strict_power_certificate=
            compressed_power_certificate(L//reciprocal,10400*(L+8))))
    require(49*26*(2*25+1)<2600*25,
            'Uncapped row degree does not dominate the depth')
    return dict(status='PASS exact uncapped logarithmic row-field domination',
                checks=checks,real_log_lower=cutoff,
                reciprocal_exponent_ceiling=reciprocal,
                maximum_child_rank=51**2*(51-2),child_ratio=Q(49,51),
                depth='ceil(log_(51/49)e)<=26ceil(log2e)',
                W_upper_binary_exponent=49,row_polynomial_degree=2600,
                inequality='b^(1-epsilon)>10400*(log2(b)+8)',
                implication='ell>=b^(1-epsilon)/2>2600*log2(p), p=6b',
                monotonicity='2^(L/k)/(L+8) increases for real L>=2k using log(2)>1/2',
                row_divisor='W^depth<p^2600 for e<=C*p, p>=C and log2(p)>=25',
                fixed_eventual_setup='p>=max(2,C) for the retained layout constant C; finite native prime/table constants remain separate')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--previous-capped-assembly',type=Path,required=True)
    ap.add_argument('--uncapped-characteristic',type=Path,required=True)
    ap.add_argument('--uncapped-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic();source_dir=Path(__file__).parent
    old=json.loads(args.previous_capped_assembly.read_text())
    primitive=json.loads(args.uncapped_characteristic.read_text())
    review=json.loads(args.uncapped_review.read_text())
    for name,digest in old['source_sha256'].items():
        require(sha(source_dir/name)==digest,'Frozen predecessor source differs '+name)
    for name,digest in primitive['source_sha256'].items():
        require(sha(source_dir/name)==digest,'Frozen uncapped source differs '+name)
    require(review['status'].startswith('PASS'),'Uncapped independent review is not terminal')
    require(review['input_sha256'][str(args.uncapped_characteristic)]==sha(args.uncapped_characteristic),
            'Independent review did not consume this uncapped certificate')
    finite=primitive['odd_bit_finite_audit']; accepted=review['clone_acceptance']
    require(finite['status']=='INDEPENDENT FINITE PROMOTION PASS' and
            accepted['candidate_id']==finite['candidate_id'] and
            accepted['compiled_sha256']==finite['compiled_sha256'] and
            accepted['roles']==finite['roles'] and
            accepted['full_finite_promotion_plus_separate_all_size_proof'],
            'Complete promoted clone interface differs')
    padding=review['row_padding']
    require(padding['sufficient_polynomial_degree']==2600 and
            padding['maximum_child']==51**2*49 and padding['W_bits']==49 and
            padding['eventual_constant_and_fixed_prime_thresholds_separate'],
            'Independent uncapped row transfer differs')
    require(all(r['old_cap_discriminated'] for r in review['actual_uncapped_middle_profiles']),
            'Independent complete uncapped profile discriminator absent')
    regressions=[]
    for row in old['witnesses']:
        n,nc=parse_counts(row['bit_counts']),parse_counts(row['complex_counts'])
        p=next(r for r in old['rotated_characteristic_certificate']['witnesses']
               if r['variant']==row['batch_variant'])
        actual=batch_witness(n,nc,row['mode'],row['prefix'],Q(row['previous_accepted_kappa']),p)
        for group in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group])==row[group],'Capped predecessor regression differs '+group)
        require(as_strings(row_padding_certificate(actual))==row['compact_row_padding'],
                'Historical capped p^100 padding regression differs')
        regressions.append(dict(variant=row['batch_variant'],mode=row['mode'],prefix=row['prefix'],
                                kappa=row['parameters']['kappa'],unchanged=True))
    previous=max(Q(row['parameters']['kappa']) for row in old['witnesses'])
    nc=parse_counts(old['witnesses'][0]['complex_counts'])
    require(nc['h']==28 and nc['R']==97586,'Original accepted complex input differs')
    rows=[]
    for p in primitive['witnesses']:
        n=parse_counts(p['counts'])
        require(n['h']==51 and n['side_roles']==500703,'Promoted clone input differs')
        require(as_strings(uncapped_middle(n['h'],n['side_roles'],p['variant']))==p,
                'Uncapped characteristic regeneration differs')
        peer=next(r for r in review['rows'] if r['side_roles']==n['side_roles'] and
                  r['variant']==p['variant'])
        for key in ('h','m','N','W','L','D','s'):
            require(peer['counts'][key]==n[key],'Independent uncapped count differs '+key)
        require(Q(peer['supplied_saving'])==Q(p['saving']) and
                Q(peer['supplied_strict_gap'])>0 and
                peer['maximum_child']==p['maximum_child_rank'],
                'Independent uncapped characteristic differs')
        for mode in ('conservative','tight'):
            for prefix in ('original','balanced'):
                row=batch_witness(n,nc,mode,prefix,previous,p)
                row['batch_variant']=p['variant']
                row['compact_row_padding']=uncapped_row_padding(row)
                row['native_bit_primitive']=dict(
                    certificate_kind='UNCAPPED ROTATED NEGATIVE-EXPONENTIAL TAYLOR',
                    chosen_saving=Q(p['saving']),strict_taylor_gap=Q(p['strict_taylor_gap']),
                    compiler_basis_order=[3,1,2],
                    middle='Full increasing runs a*h^2, (h-a-2)*h^2, h^2',
                    maximum_child_rank=p['maximum_child_rank'],child_ratio=Q(49,51),
                    child_width_relation='r*floor(e/m)<=(49/51)*e<e',
                    depth='ceil(log_(51/49)e)<=26ceil(log2e)',
                    row_divisor='W^depth<p^2600 after p>=C and log2p>=25',
                    factor_table='Accepted rotated fixed rational Bruhat table unchanged by uncapping',
                    native_prime='Same fixed admissible odd prime as the accepted rotated table; eventual setup constants separate',
                    complex_guard='Original h28 R97586 numerical network and C0/C1 unchanged')
                row['proof_obligations'].insert(0,
                    'Independent full clone finite/all-size transfer and uncapped contiguous middle runs with p^2600 row stock')
                row['additional_eventual_cutoffs'] += [
                    'Fixed native rotated table and admissible odd prime from the accepted global basis',
                    'Retained layout setup C for uncapped calls: e<=C*p after p>=C',
                    'Complete untouched row reservoir divisible by W^depth, certified below p^2600']
                rows.append(row)
    hashes=dict(old['source_sha256']);hashes.update(primitive['source_sha256']);hashes[Path(__file__).name]=sha(Path(__file__))
    result=dict(status='PASS STRICT CONDITIONAL UNCAPPED ASSEMBLY; INDEPENDENT FINAL ARITHMETIC REVIEW REQUIRED',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
                generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
                original_reference=old['original_reference'],compact_reference=old['compact_reference'],
                input_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in
                    (args.previous_capped_assembly,args.uncapped_characteristic,args.uncapped_review)},
                odd_bit_finite_audit=finite,promoted_complex_audit=old['promoted_complex_audit'],
                previous_accepted_kappa=previous,capped_predecessor_regressions=regressions,
                uncapped_characteristic_certificate=primitive,
                independent_uncapped_review_sha256=sha(args.uncapped_review),
                witnesses=rows,elapsed_seconds=time.monotonic()-started,
                scope='Complete unchanged semantic/bulk inequalities with promoted clone and full rotated middle runs. Child shrink is49/51 and row degree2600; no h-fold/p^100 transfer is asserted for new rows. Fixed prime/table/C and final absorption thresholds remain explicit.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:
        print(result['status'],row['batch_variant'],row['mode'],row['prefix'],
              row['parameters']['kappa'],row['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
