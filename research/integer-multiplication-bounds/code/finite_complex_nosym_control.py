#!/usr/bin/env python3
"""Exact literal option identity and native no-symmetry complex controls."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time
from unittest.mock import patch
import frame_reuse
import finite_complex_clone_options as old
import finite_complex_clone_nosym as new
from finite_clone_batch import serialized


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    from scipy.optimize._highspy import _core
    native=_core._Highs();status,before=native.getOptionValue('mip_detect_symmetry');assert before is True
    assert native.setOptionValue('mip_detect_symmetry',False)==_core.HighsStatus.kOk
    status,after=native.getOptionValue('mip_detect_symmetry');assert after is False
    at=time.monotonic();identities=[]
    for h in (8,12):
        circuit=old.witness.TripleSideCircuit(h);frames,_=old.witness.binary.labels(circuit)
        with patch.object(frame_reuse,'included',old.witness.binary.admissible):
            plan=frame_reuse.optimize_chains(circuit,frames,'rank')
            for limit in (2,4,12):
                for policy in ('wide','narrow','seeded'):
                    for seed in (0,104729):
                        left,_=old.opportunities(circuit,frames,plan,limit,policy,seed)
                        right,_=new.opportunities(circuit,frames,plan,limit,policy,seed)
                        a=json.dumps([serialized(job) for job in left],sort_keys=True,separators=(',',':'))
                        b=json.dumps([serialized(job) for job in right],sort_keys=True,separators=(',',':'))
                        assert a==b
                        identities.append(dict(h=h,limit=limit,policy=policy,seed=seed,jobs=len(left),literal_jobs_sha256=sha256(a.encode()).hexdigest()))
    baseline=json.loads(args.baseline.read_text());saved={row['h']:row for row in baseline['rows']};rows=[]
    for h in (8,12):
        row=new.case(h,saved[h],4,'wide',0,6.0,dirty=h==8,exchange=h==8);rows.append(row)
        print(json.dumps(dict(h=h,roles=row['compiled_roles'],clones=row['role_saving'],solver=row['compatibility_selection']['solver'])),flush=True)
    value=dict(status='Terminal exact offered-job identity and native no-symmetry complex witness PASS',
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        old_option_source_sha256=sha256(Path(old.__file__).read_bytes()).hexdigest(),
        new_option_source_sha256=sha256(Path(new.__file__).read_bytes()).hexdigest(),
        baseline_input_sha256=sha256(args.baseline.read_bytes()).hexdigest(),
        native_option=dict(name='mip_detect_symmetry',default=before,verified_setting=after,highs_version=native.version()),
        literal_option_identity_controls=identities,rows=rows,elapsed_seconds=time.monotonic()-at,
        scope='Literal offered jobs unchanged by early chain-table termination; exact integer feasibility and all actual binary phase/Gram/physical/target/G/E checks; h8 complete Gaussian dirty/shared')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
