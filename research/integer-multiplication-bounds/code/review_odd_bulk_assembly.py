#!/usr/bin/env python3
"""Thin independent arithmetic for a newly reviewed odd bit composition.

Only independent arithmetic reviewers are imported. The finite odd review
and unchanged complex/analytic interfaces are identified by immutable input
hashes; no accepted finite baseline is reconstructed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path
import resource
import time

from review_semantic_bulk_assembly import audit_row, require


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("certificate", "bit-review", "candidate", "previous", "output"):
        ap.add_argument("--" + name, type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), "Use a fresh result path")
    begin = time.monotonic()
    data = json.loads(args.certificate.read_text())
    reviewed = json.loads(args.bit_review.read_text())
    candidate = json.loads(args.candidate.read_text())
    old = json.loads(args.previous.read_text())
    hashes = {str(path): digest(path) for path in
              (args.certificate, args.bit_review, args.candidate, args.previous)}
    require(reviewed["status"] == "PASS", "New independent finite review failed")
    require(reviewed["candidate_file_sha256"] == hashes[str(args.candidate)],
            "New finite review input identity differs")
    full = reviewed["full"]
    require(full["h"] % 2 == 1 and full["h"] >= 11 and full["h"] != 9,
            "New odd rational scope differs")
    require(full["matches_immutable_producer_identity_and_compilation"] and
            full["candidate_id"] == candidate["candidate_id"] and
            full["compiled_sha256"] == candidate["compiled"]["compiled_sha256"] and
            full["compiled_roles"] == candidate["compiled_roles"],
            "New reviewed odd compiled witness differs")
    h, roles = full["h"], full["compiled_roles"]
    require(roles == full["logical"]["additions"] + full["logical"]["outputs"] -
            full["controller_plan"]["selected_links"], "New odd physical count differs")
    match = full["stage_matching"]
    require(match["triples"] == comb(h, 3) and match["intersection_one"] and
            match["explicit_inverse_and_bijection"] and match["rational_form_nondegenerate"] and
            match["image_sha256"] == candidate["stage_matching"]["image_sha256"],
            "New odd stage join differs")
    audit = data["odd_bit_finite_audit"]
    require(audit["h"] == h and audit["roles"] == roles and
            audit["candidate_id"] == full["candidate_id"] and
            audit["compiled_sha256"] == full["compiled_sha256"],
            "Producer promotion metadata differs")
    for path in (args.bit_review, args.candidate, args.previous):
        require(any(item["sha256"] == hashes[str(path)]
                    for item in data["input_files"].values()),
                "New producer input hash absent: " + path.name)
    require(data["promoted_complex_audit"] == old["promoted_complex_audit"],
            "Unchanged accepted complex interface metadata differs")
    old_best = max(old["witnesses"], key=lambda row: Q(row["parameters"]["kappa"]))
    require(Q(data["previous_accepted_kappa"]) == Q(old_best["parameters"]["kappa"]),
            "Prior accepted comparison differs")
    for name, expected in data["source_sha256"].items():
        require(digest(Path(__file__).with_name(name)) == expected,
                "Executed producer dependency changed: " + name)
    for row in data["witnesses"]:
        require(row["bit_counts"]["h"] == h and row["bit_counts"]["side_roles"] == roles,
                "New odd count input differs")
        require(row["complex_counts"] == old_best["complex_counts"],
                "Accepted original h28 complex count input differs")
    rows = [audit_row(row, old_best) for row in data["witnesses"]]
    require({(row["mode"], row["prefix"]) for row in rows} ==
            set(product(("conservative", "tight"), ("original", "balanced"))),
            "New four-row composition is incomplete")
    names = ("review_odd_bulk_assembly.py", "review_semantic_bulk_assembly.py",
             "review_asymmetric_motif.py", "review_compact_generic.py",
             "review_packed_unrolling.py", "review_parameter_audit.py")
    result = dict(status="PASS independent odd semantic/bulk arithmetic",
                  campaign="20261007T222521Z", generated_at=datetime.now(timezone.utc).isoformat(),
                  input_sha256=hashes,
                  reviewer_source_sha256={name: digest(Path(__file__).with_name(name)) for name in names},
                  odd_finite_identity=dict(h=h, roles=roles, candidate_id=full["candidate_id"],
                                           compiled_sha256=full["compiled_sha256"]),
                  unchanged_complex_audit=data["promoted_complex_audit"], rows=rows,
                  wall_seconds=time.monotonic() - begin,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope="Independent longer-log and exact assembly inequalities for the new odd bit input; "
                        "the previously reviewed full routing, linear guard, resampling and "
                        "balanced-prefix interfaces are retained; no finite baseline replay")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    for row in rows:
        print("PASS", row["mode"], row["prefix"], row["kappa"], flush=True)


if __name__ == "__main__":
    main()
