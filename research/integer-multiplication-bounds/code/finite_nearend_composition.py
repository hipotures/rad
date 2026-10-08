#!/usr/bin/env python3
"""Compose exact singleton near-end role counts under reviewed models.

Input finite witnesses and analytic proof dependencies remain separate.
Retain strict rational bit/log/guard margins and compare the supported score,
not addition counts. New grounds still need full promotion when selected.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from asymmetric_motif import counts,complex_counts,score
from asymmetric_phase import compose
from downstream_parameter_optimum import as_strings,saving_enclosure


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--baseline-motif",type=Path,required=True)
    parser.add_argument("--candidates",type=Path,nargs="+",required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    assert not args.output.exists(),"Use a fresh output path"
    inputs=[args.baseline_motif]+args.candidates
    input_provenance={str(path):dict(bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest()) for path in inputs}
    baseline=json.loads(args.baseline_motif.read_text())
    roles={int(h):int(r) for h,r in baseline["verified_role_counts"].items()}
    old=dict(roles);selected={h:dict(roles=r,source=str(args.baseline_motif),gap=None) for h,r in roles.items()}
    improvements=[]
    for path in args.candidates:
        raw=json.loads(path.read_text())
        assert raw.get("reference_commit",raw.get("upstream_reference_commit"))=="bcd4ebde8692383539f8a48734e5fbf3a18a32c2"
        rows=raw.get("rows",raw.get("full_checks",[]))
        for row in rows:
            h=int(row["h"]);r=int(row.get("compiled_roles",row.get("roles")))
            if row.get("kind","global")!="global":continue
            if h not in roles or r<roles[h]:
                improvements.append(dict(h=h,old_roles=roles.get(h),new_roles=r,
                    gap=row.get("parameter",row.get("gap")),source=str(path)))
                roles[h]=r;selected[h]=dict(roles=r,source=str(path),gap=row.get("parameter",row.get("gap")))
    nc=complex_counts();ec=saving_enclosure(nc["eta"],nc["m"])
    rows=[];best_lu=best_phase=None
    for p,rp in sorted(roles.items()):
        for q,rq in sorted(roles.items()):
            n=counts(p,q,rp,rq)
            if n["D"]<=0:continue
            lu=score(n,ec);phase=compose(n)
            row=dict(p=p,q=q,Rp=rp,Rq=rq,eta=n["eta"],
                     chosen_bit_saving=phase["bit_saving_enclosure"]["chosen_saving"],
                     kappa_lu=lu["parameters"]["kappa"],kappa_phase=phase["parameters"]["kappa"])
            rows.append(row)
            if best_lu is None or lu["parameters"]["kappa"]>best_lu["parameters"]["kappa"]:best_lu=lu
            if best_phase is None or phase["parameters"]["kappa"]>best_phase["parameters"]["kappa"]:best_phase=phase
    rows.sort(key=lambda row:row["kappa_phase"],reverse=True)
    old_n=counts(52,48,old[52],old[48]);old_phase=compose(old_n);old_lu=score(old_n,ec)
    source_names=("finite_nearend_composition.py","asymmetric_motif.py","asymmetric_phase.py","downstream_parameter_optimum.py","downstream_gaussian.py")
    result=dict(settings=dict(baseline_motif=str(args.baseline_motif),candidates=list(map(str,args.candidates)),output=str(args.output)),
        started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,
        input_provenance=input_provenance,source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in source_names},
        reference_commit="bcd4ebde8692383539f8a48734e5fbf3a18a32c2",selected_role_witnesses=selected,
        improvements=improvements,best_lu=best_lu,best_phase=best_phase,ranking=rows,
        accepted_comparator=dict(p=52,q=48,kappa_lu=old_lu["parameters"]["kappa"],kappa_phase=old_phase["parameters"]["kappa"]),
        scope="Strict arithmetic score with inherited reviewed analytic models; all selected finite role witnesses exact, new headline requires its independent finite frame/rank/stage promotion")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+"\n")
    print(json.dumps(as_strings(dict(output=str(args.output),best_p=best_phase["counts"]["p"],best_q=best_phase["counts"]["q"],
        best_lu=best_lu["parameters"]["kappa"],best_phase=best_phase["parameters"]["kappa"],wall_seconds=result["wall_seconds"]))),flush=True)


if __name__=="__main__":main()
