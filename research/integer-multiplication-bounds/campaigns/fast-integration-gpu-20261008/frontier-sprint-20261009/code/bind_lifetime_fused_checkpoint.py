#!/usr/bin/env python3
"""Bind executed independent reviews; this does not rerun their mathematics."""
import argparse
import datetime
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent


def read(relative):
    return json.loads((ROOT / relative).read_text(), parse_int=str)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pin(relative):
    data = (ROOT / relative).read_bytes()
    return {"path": relative, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def check(record):
    actual = pin(record["path"])
    require(actual["sha256"] == record["sha256"] and
            actual["bytes"] == int(record["bytes"]),
            "Changed input: " + record["path"])


def main():
    # Exact interval slacks include a recorded 5,899-digit numerator.
    # Structural parsing stays string-based; rational comparisons are bounded.
    sys.set_int_max_str_digits(50000)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    require(not output.exists(), "Refusing to replace a checkpoint")
    config_path = "agents/transfer/configs/lifetime-fused-168-170.json"
    author_path = "work/transfer/20261009T-lifetime-fused-168-170/receipt.json"
    review_path = "work/assembly/20261009T-independent-lifetime-fused/review.json"
    binding_path = "work/assembly/20261009T-independent-lifetime-fused/finite-binding.json"
    config, author, review, binding = map(read, [config_path, author_path, review_path, binding_path])
    for records in [config["sources"], config["inputs"],
                    binding["independent_review_sources"], binding["receipt_pins"]]:
        for record in records.values():
            check(record)
    require(len(config["sources"]) == 141 and len(config["inputs"]) == 24,
            "Unexpected scientific closure")
    require(binding["author_receipt_sha256"] == pin(author_path)["sha256"],
            "Author receipt binding changed")
    require(binding["arithmetic_config_sha256"] == pin(config_path)["sha256"],
            "Arithmetic configuration binding changed")
    for field in ["candidate_id", "kappa", "atom", "coarse_bit_saving", "complex_saving",
                  "ordinary_bit_saving", "bit_profile", "complex_profile", "assembly"]:
        require(author[field] == review[field], "Independent arithmetic mismatch: " + field)
    require(binding["kappa"] == author["kappa"], "Finite/arithmetic identity mismatch")
    for field in ["bit_profile", "complex_profile"]:
        require(binding[field.replace("bit_", "binary_")] == review[field],
                "Independent finite profile mismatch: " + field)
        profile = review[field]
        histogram = {int(k): int(v) for k, v in profile["hist"].items()}
        require(sum(histogram.values()) == int(profile["edges"]), "Child-count mismatch")
        require(sum(k * v for k, v in histogram.items()) == int(profile["mass"]),
                "Rank-mass mismatch")
    assembly = review["assembly"]
    require(len(assembly["slacks"]) == 47 and len(assembly["margins"]) == 7,
            "Incomplete assembly obligations")
    require(all(Fraction(v) > 0 for v in assembly["slacks"].values()) and
            all(Fraction(v) > 0 for v in assembly["margins"].values()),
            "Nonpositive assembly obligation")
    require(Fraction(assembly["g"]) - Fraction(author["kappa"]) ==
            Fraction(assembly["absorption_gap"]) > 0, "Invalid strict absorption")
    require(binding["status"] == "ACCEPTED_CONDITIONAL", "Finite review not closed")
    frontier = read("public-frontier.json")
    top = max(Fraction(frontier["publication_comparison_threshold"]),
              Fraction(frontier["retained_maintainer_reviewed_result"]["exact_kappa"]))
    minimum = top * Fraction(101, 100)
    identity = {"candidate_id": author["candidate_id"], "kappa": author["kappa"],
                "parameters": {k: config[k] for k in ["atom", "coarse", "complex_saving",
                               "phase_stop", "backoff", "strict_weakening"]},
                "sources": config["sources"], "inputs": config["inputs"],
                "independent_review_sources": binding["independent_review_sources"],
                "finite_receipts": binding["receipt_pins"]}
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()
    result = {"recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "status": "ACCEPTED_CONDITIONAL", "candidate_id": author["candidate_id"],
              "kappa": author["kappa"], "scientific_digest": digest,
              "scientific_digest_method": "SHA256 of sorted compact JSON scientific_identity",
              "scientific_identity": identity,
              "receipts": [pin(p) for p in [config_path, author_path, review_path, binding_path]],
              "coordinator_checker": pin("code/bind_lifetime_fused_checkpoint.py"),
              "binding_scope": "Rechecked every 141/24 source/input byte identity, reviewer closure, independently recounted distributions, matching independent complete arithmetic, 47 positive slacks, seven positive margins and exact absorption. The separately executed full finite reconstructions remain the mathematical evidence.",
              "inherited_hypotheses": binding["hypotheses"],
              "prime_scope": {"new_selected_determinants_bits": 63,
                              "old_selected_determinants_bits": 106,
                              "retained_exclusions": binding["retained_prime_exclusions"]},
              "publication": {"ready": False, "minimum_relative_improvement": "1/100",
                              "observed_utc": frontier["observed_utc"],
                              "leader": frontier["highest_active_comparable_public_claim"],
                              "required_score": str(minimum),
                              "numerical_gate_passes": Fraction(author["kappa"]) >= minimum,
                              "frontier_snapshot": pin("public-frontier.json"),
                              "scope": "Research checkpoint only. Broad contribution verification and an actual release script have not been produced for this superseded candidate."},
              "recovery": "Complete receipt archives, authored code and compact frozen fixtures are preserved in lane handoffs; external source pins have immutable GitHub acquisition manifests. The reviewer cover note is an explicitly separate closure dependency."}
    with output.open("x") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "kappa": result["kappa"],
                      "scientific_digest": digest, "publication_gate": result["publication"]["numerical_gate_passes"]}))


if __name__ == "__main__":
    main()
