#!/usr/bin/env python3
"""Bind independently reviewed finite inputs to the unified arithmetic.

Apache-2.0; prepared for RaD with OpenAI GPT-6.1 Sol assistance.
This validates identities and recomputes child counts. It is not a rerun
or replacement of the independent finite binary/complex checkers.
"""

import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import sys

from review_balanced_unified import complete_profile, digest, encode, exact_match, histogram, need


def main():
    need(not sys.flags.optimize,"Assertion-disabled Python is unsupported")
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sprint",type=Path,default=Path(__file__).resolve().parents[3])
    for name in ("config","arithmetic","bit-receipt","bit-profile","bit-source","complex-binding","output"):
        p.add_argument("--"+name,type=Path,required=True)
    args=p.parse_args();need(not args.output.exists(),"Fresh binding identity required")
    config=json.loads(args.config.read_text());arith=json.loads(args.arithmetic.read_text())
    binary=json.loads(args.bit_receipt.read_text());fresh=json.loads(args.bit_profile.read_text())
    data=args.complex_binding.read_bytes()
    complex_binding=json.loads(gzip.decompress(data) if args.complex_binding.suffix==".gz" else data)
    need(arith["configuration_sha256"]==digest(args.config),"Arithmetic configuration identity")
    need(binary["plan_sha256"]==config["inputs"]["bit_frames"]["sha256"] and
         binary["supplied_profile_sha256"]==config["inputs"]["bit"]["sha256"],"Binary finite input identity")
    exact_match(binary["profile"],fresh,"Independent finite binary profile")
    H=Counter()
    for r,n in histogram(fresh["selected_rank_histogram"],"selected gauges").items():H[3*r]+=n
    for field in ("local_histogram","source_data_histogram","target_data_histogram"):
        for r,n in histogram(fresh[field],field).items():H[r]+=3*n
    H[2]+=2*fresh["v"];H.pop(0,None)
    need(dict(H)=={int(r):n for r,n in fresh["child_histogram"].items()},"Independent binary component recount")
    bp=complete_profile(fresh,(72,26888,1934000,60))
    exact_match(arith["bit_profile"],bp,"Arithmetic consumes independently reconstructed binary counts")
    for name,expected in binary["source_sha256"].items():
        need(digest(args.bit_source/name)==expected,"Independent finite binary source identity: "+name)
        if name in config["sources"]:
            need(config["sources"][name]["sha256"]==expected,"Frozen binary scalar/source discrepancy: "+name)
    need(complex_binding["unified_config_sha256"]==digest(args.config) and
         complex_binding["unified_receipt_sha256"]==arith["certificate_sha256"],"Complex review candidate identity")
    mapping={"candidate_frames":"complex_frames","candidate_profile":"physical",
             "graph":"complex_graph","word":"complex_selection"}
    for key,name in mapping.items():
        pin=config["inputs"][name]
        need(complex_binding["compared_sha256"][key]==pin["sha256"] and
             digest(args.sprint/pin["path"])==pin["sha256"],"Complex reflected input identity: "+name)
    result=dict(status="PASS_INDEPENDENT_FINITE_INPUT_BINDING",binary_profile=bp,
        arithmetic_sha256=digest(args.arithmetic),bit_receipt_sha256=digest(args.bit_receipt),
        bit_profile_sha256=digest(args.bit_profile),complex_binding_sha256=digest(args.complex_binding),
        binary_source_sha256=binary["source_sha256"],binary_frame_sha256=binary["plan_sha256"],
        complex_profile_canonical_sha256=complex_binding["common_canonical_profile_sha256"],
        scope="Finite binary component histogram recomputed; exact source/scalar/frame/profile identities tied to separately executed independent finite receipts and unified arithmetic. No saved verdict substitutes for a finite replay.",
        finite_receipt_locations=dict(binary=str(args.bit_receipt),complex=str(args.complex_binding)),
        retained_prime_exclusions=binary["prime_summary"]["inherited_prime_exclusion_sources"],
        all_size_contracts="Unchanged uniform local-ring/Clifford, ordinary restoration, full tensor, paid balanced routing/bulk, prime/setup and precision/recovery hypotheses remain conditional")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+"\n")
    print("PASS finite input binding, independently reconstructed full binary histogram, and all 14 finite source identities")


if __name__=="__main__":main()
