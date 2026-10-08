#!/usr/bin/env python3
"""Independently rebuild a changed two-word ledger and outward moment.

Word/profile identities are checked against the independently recovered
physical paths. No producer, profiler, assembly or upstream arithmetic is
imported. The exact enclosure implementation is this agent's authored one.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import gzip
import hashlib
import json
from math import comb
from pathlib import Path
import time

from verify_transfer_ledger import depth_degree, moment


def main():
    parser = argparse.ArgumentParser()
    for name in ("word", "profile", "physical"):
        parser.add_argument("--"+name, action="append", required=True, type=Path)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--saving", required=True, type=F)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    assert not args.output.exists()
    assert len(args.word) == len(args.profile) == len(args.physical) == 2
    started = time.monotonic()
    n, m = comb(23, 3)*comb(25, 3), 575
    width = 2*n
    rows = Counter({1: 19*n, 21: 2*n, 17: 2*n, 481: 2*n})
    local, xors, events, loss = [], 0, 0, 0
    paths = [*args.word, *args.profile, *args.physical, args.reference]
    for wordpath, profilepath, physicalpath, h in zip(args.word, args.profile, args.physical, (23, 25)):
        raw = wordpath.read_bytes()
        if wordpath.suffix == ".gz":
            raw = gzip.decompress(raw)
        word = json.loads(raw)
        profile = json.loads(profilepath.read_text())
        physical = json.loads(physicalpath.read_text())
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == physical["decompressed_word_sha256"]
        v, r = word["v"], word["R"]
        assert word["h"] == profile["h"] == physical["h"] == h
        assert v == comb(h, 3) and r == profile["R"] == physical["R"]
        assert physical["all_actual_output_symbols_exact"]
        assert physical["all_per_role_positive_frame_paths_equal_events"]
        assert all(c["every_source_target_dirty_row_exact"] for c in physical["full_basis_checks"])
        assert len(word["sources"]) == v and len(word["scatter"]) == 6*v
        assert len({o[0] for o in word["outputs"]}) == len(word["outputs"])
        assert len(word["ops"]) == physical["local_xors"]
        assert len(profile["blocks"]) == h+1 and profile["blocks"][h] == 0
        assert profile["differing_modular_profiles"] == 0 and profile["all_corner_moduli"] == 12
        assert sum(i*c for i, c in enumerate(profile["blocks"])) == h*r+h*(h-1) == profile["rank_sum"]
        rep = n//v
        complete = 4*len(word["ops"])+14*v
        xors += rep*complete
        events += rep*len(word["events"])
        width += rep*r
        loss += rep*h*(h-1)
        rows += Counter({t: c*rep for t, c in enumerate(profile["blocks"]) if t and c})
        rows += Counter({h: rep*r, m-2*h: rep*r, 1: 2*n, h-2: 2*n})
        local.append({"h": h, "v": v, "R": r, "mixer_XORs": len(word["ops"]),
                      "wrapped_XORs": complete, "replications": rep,
                      "literal_frame_events": len(word["events"]), "rank_mass": profile["rank_sum"],
                      "decompressed_word_sha256": digest})
    reference = json.loads(args.reference.read_text())
    ref = reference["controller"]
    mass = sum(t*c for t, c in rows.items())
    assert (width, mass, max(rows), xors) == (ref["W"], ref["total_rank"], ref["maxchild"], ref["wrapped_scalar_xors"])
    assert dict(rows) == {int(t): c for t, c in ref["child_multiplicities"].items()}
    assert m*width-mass == n-loss == 1846900
    assert args.saving == F(reference["saving"])
    certified = moment(m, width, rows, args.saving)
    following = moment(m, width, rows, args.saving+F(1, 10**14))
    assert certified["strictly_below_one"] and following["strictly_above_one"]
    product = depth_degree(m, max(rows))*width.bit_length()+depth_degree(784, 756)*537696432 .bit_length()
    assert product == 852 and F(2000)-F(51, 25)*product == F(6548, 25)
    prospective = args.saving*F(99999, 100000)
    epsilon = F(999999, 1000000)
    q = epsilon*args.saving
    public = F(reference["kappa"])
    old = F(475073569, 10**13)
    assert public > old and prospective > old and epsilon*q > prospective
    result = {"status": "PASS_INDEPENDENT_CHANGED_FULL_LEDGER_AND_MOMENT",
              "recorded_utc": datetime.now(timezone.utc).isoformat(),
              "local": local, "bit": {"m": m, "W": width, "rank_mass": mass,
                                       "deficit": m*width-mass, "maxchild": max(rows),
                                       "child_multiplicities": dict(sorted(rows.items()))},
              "complete_replicated_local_XORs": xors,
              "difference_from_PR58_local_XORs": xors-2206597276,
              "replicated_literal_frame_events": events,
              "explicit_copy_stream_groups_upper": 388700,
              "saving": str(args.saving), "outward_moment": certified,
              "next_saving_control": following,
              "unchanged_row_stock": {"coefficient": product, "degree": 2000,
                                      "positive_degree_gap": "6548/25", "suffix_slope": 8000},
              "public47_assembly_kappa": str(public), "difference_from_PR58_headline": str(public-old),
              "campaign_prospective_target": str(prospective),
              "campaign_target_gaps": {"native": str(args.saving-prospective),
                                       "tensor": str(epsilon*q-prospective),
                                       "complex_leaf": str(F(19, 20)*F(717, 10000000)-q)},
              "input_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "moment_source_sha256": hashlib.sha256(Path(__file__).with_name("verify_transfer_ledger.py").read_bytes()).hexdigest(),
              "workers": 1, "seconds": time.monotonic()-started,
              "scope": "Changed literal word cost, independently rebuilt native child counts and outward moment. All-phase frame schedule and owned-copy tape contract are separately reviewed; the public47 assembly number is compared to its retained exact reference, not promoted by numerical substitution. Campaign target remains subject to complete coordinator analytic/recovery proof."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "saving": str(args.saving),
                      "local_XORs": xors, "moment_gap": certified["strict_gap_lower"]}), flush=True)


if __name__ == "__main__":
    main()
