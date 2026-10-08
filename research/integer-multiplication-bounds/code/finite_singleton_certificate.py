#!/usr/bin/env python3
"""Certify aligned singleton gaps with unchanged support-envelope transfer.

Small circuits exercise arbitrary dirty basis payloads and equal/asymmetric
three-stage exchange. Full grounds check every scalar coefficient, both frame
directions, every physical target and the complete stage matching. The exact
LU score is imported from the independently reviewed coordinating work.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from finite_block_search import GroupUnion, install_reference
from finite_singleton_search import singleton_class
from frame_envelope import labels, target_check
from frame_reuse import check, compile_reuse, included, optimize_chains
from frame_reuse_certificate import counted_network, program
from review_envelopes import graph_envelope_check, matching_check


def build(h, gap, base=4):
    assert h >= 6 and h % 2 == 0 and -1 <= gap < h//2
    positions = [gap if common//2 <= gap else gap+1 for common in range(h)]
    cls = singleton_class()
    circuit = GroupUnion(h, lambda n,common: cls(n,positions[common],base), "paired", 0, True)
    return circuit, positions


def case(h, gap, base, small=False, independent_dirty=False):
    from dag_network import exact_invocation, shared_scalar_model
    from reuse_network import triple_matching
    begin = time.monotonic()
    circuit, positions = build(h, gap, base)
    original = circuit.verify()
    frames, metadata = labels(circuit, True)
    code = compile_reuse(circuit, frames, optimize_chains(circuit, frames, "rank"))
    checked = check(circuit, frames, code)
    targets = target_check(circuit, frames, True)
    independent = graph_envelope_check(circuit, frames, code, dense=small)
    matching = matching_check(h)
    scalar = program(circuit, code)
    triples, images = triple_matching(h)
    assert triples == scalar["triples"]
    assert len(set(images)) == len(triples)
    assert all(len(set(t)&set(triples[j])) == 1 for t,j in zip(triples, images))
    row = dict(h=h, gap=gap, positions=positions, base=base, graph=original,
               roles=code["roles"], chains=code["chain_summary"], frames=metadata,
               checked=checked, targets=targets, independent_envelope_check=independent,
               stage_matching=matching)
    if small:
        row["dirty_basis"] = [exact_invocation(h,inverse,scalar) for inverse in (False,True)]
        row["complete_three_stage_exchange"] = [shared_scalar_model(h,seed,scalar) for seed in (1,109)]
    if independent_dirty:
        from review_frame_reuse import dirty_check
        row["independent_elementary_dirty_basis"] = dirty_check(circuit,frames,code)
    row["elapsed_seconds"] = time.monotonic()-begin
    included.cache_clear()
    GroupUnion.support_in.cache_clear()
    return row,scalar,images


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference",required=True)
    ap.add_argument("--full",nargs="+",default=["50:23"],help="Full grounds h:gap")
    ap.add_argument("--small",nargs="+",type=int,default=[6,8])
    ap.add_argument("--base",type=int,default=4)
    ap.add_argument("--asymmetric",default="52,48")
    ap.add_argument("--output",type=Path,required=True)
    args = ap.parse_args()
    install_reference(args.reference)
    from asymmetric_motif import counts, complex_counts, score, scalar_exchange, join_certificate
    from downstream_parameter_optimum import as_strings, saving_enclosure
    start = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    assert not args.output.exists(), "Use a fresh output path"
    args.output.parent.mkdir(parents=True,exist_ok=True)
    source_names = ("finite_singleton_certificate.py","finite_singleton_search.py","finite_block_search.py",
                    "frame_envelope.py","frame_reuse.py","frame_reuse_certificate.py","review_envelopes.py",
                    "review_frame_reuse.py","asymmetric_motif.py","downstream_parameter_optimum.py")
    result = dict(settings={**vars(args),"output":str(args.output)},started_utc=started,
                  upstream_reference_commit="bcd4ebde8692383539f8a48734e5fbf3a18a32c2",
                  source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in source_names},
                  small_checks=[], full_checks=[], asymmetric_small_exchange=[])
    small_cache = {}
    for h in args.small:
        gap = h//2-2
        row,scalar,matching = case(h,gap,args.base,True,h==min(args.small))
        result["small_checks"].append(row)
        small_cache[h] = scalar,matching
        print(json.dumps(dict(phase="small",h=h,gap=gap,roles=row["roles"],dirty_and_shear=True)),flush=True)
    for p,q in ((6,8),(8,6)):
        if p in small_cache and q in small_cache:
            for seed in (1,109):
                result["asymmetric_small_exchange"].append(scalar_exchange(p,q,seed,small_cache[p][0],small_cache[q][0],small_cache[q][1]))
    full = {}
    for specification in args.full:
        h,gap = map(int,specification.split(":"))
        row,scalar,matching = case(h,gap,args.base)
        result["full_checks"].append(row)
        full[h] = row,matching
        result["completed_utc"] = datetime.now(timezone.utc).isoformat()
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print(json.dumps(dict(phase="full",h=h,gap=gap,roles=row["roles"],all_frame_and_target_checks=True)),flush=True)
    p,q = map(int,args.asymmetric.split(","))
    if p in full and q in full:
        n = counts(p,q,full[p][0]["roles"],full[q][0]["roles"])
        ec = saving_enclosure(complex_counts()["eta"],complex_counts()["m"])
        result["asymmetric_score"] = as_strings(score(n,ec))
        result["asymmetric_join"] = join_certificate(p,q,full[q][1])
    result["equal_ground_counts"] = {str(h):{key:str(value) for key,value in counted_network(h,row[0]["roles"]).items()} for h,row in full.items()}
    result["transfer"] = dict(
        source_lines="Every source-copy frame is exactly the original triple line",
        frames="Positive rational E(C,V); all gate inputs/outputs nest forward, orthogonal complements reverse",
        physical_targets="Each complete output envelope is orthogonal to its designated target triple",
        scalar_schedule="L,J,L^-1,R0,V,G,R0,L,J,L^-1,G,V",
        dirty_identity="JLz+JL(z+Vx)=JLVx; inverse mixers and final V restore arbitrary scratch z",
        rank="Envelope/controller schedule creates no additional decreases; original central returns retain L",
        role_endpoints="Each surviving auxiliary role begins at 0 and ends at I_m, restored by transparent invocation",
        stage_join="Unchanged intersection-one middle matching; E<=H at every first/third shared-bank join",
        asymmetry="p,q,p changes invocation multiplicities only; W,L,D and joins use reviewed asymmetric_motif formulas",
        conditional_scope="Retains pinned upstream multiplication/lifting assumptions and the separately reviewed Gaussian-LU analytic interfaces")
    result["completed_utc"] = datetime.now(timezone.utc).isoformat()
    result["wall_seconds"] = time.monotonic()-start
    result["scope"] = "Complete finite singleton/envelope witness plus bounded dirty/shear calibration; transferred analytic score conditional on inherited reviewed interfaces"
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(dict(output=str(args.output),wall_seconds=result["wall_seconds"],roles={h:row[0]["roles"] for h,row in full.items()})),flush=True)


if __name__=="__main__":main()
