#!/usr/bin/env python3
"""Explicit protected grouped-gate charge, without changing frozen rows."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assembly',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();assert not args.output.exists()
    a=json.loads(args.assembly.read_text());rows=[]
    for row in a['witnesses']:
        n=row['bit_counts'];native=row['native_bit_primitive'];protect=native['protected_centers'];base=native['actual_bit_literal_guard']
        assert protect in (0,1,2) and n['W']>0
        # Each split adds one grouped gather per invocation. The old
        # conservative grouped scalar bound remains a valid base; changed
        # payload rows still have at most W binary summands per output.
        extra=3*protect*n['v']**2;G=base['G']+extra;E=64*(n['W']+n['m']+1)**3
        depth=2*G*n['W']**2+4*n['s']+4*n['W']+4
        assert E==base['E'] and E>depth and n['D']>0
        rows.append(dict(native_construction_id=row['native_construction_id'],mode=row['mode'],prefix=row['prefix'],
            protected_centers=protect,normal_finite_grouped_bound=base['G'],additional_grouped_gates_upper=extra,
            protected_grouped_G_upper=G,bit_E=E,protected_bit_depth_upper=depth,strict_E_slack=E-depth,
            old_normal_guard_identified_as_base_only=True,
            complex_G_E_C0_and_all_parameters_unchanged=True,kappa=row['parameters']['kappa']))
    r=dict(status='PASS EXPLICIT PROTECTED BIT GROUPED-GATE GUARD QUALIFICATION',
        generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        assembly=dict(path=str(args.assembly),sha256=sha256(args.assembly.read_bytes()).hexdigest()),rows=rows,
        proof='Every changed central scalar output is an F2 sum of at most W registers. Each extra grouped gate has the retained2W^2 elementary bound. The protected numerical guard uses the conservative G_upper; unchanged complex C0 is separately inherited.',
        qualification='The frozen assembly field actual_bit_literal_guard identifies its NORMAL finite input. It is not silently asserted to be the protected program literal gate count. No parameter bytes, primitive Taylor witness or final kappa is changed.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(r['status'],len(rows))


if __name__=='__main__':main()
