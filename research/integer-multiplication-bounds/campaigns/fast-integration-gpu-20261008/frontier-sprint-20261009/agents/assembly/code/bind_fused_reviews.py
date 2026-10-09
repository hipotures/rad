#!/usr/bin/env python3
"""Bind independently executed finite reviews to the frozen arithmetic.

Apache-2.0; prepared for RaD with OpenAI GPT-6.1 Sol assistance.
This recomputes child inventories and verifies immutable review/source
identities. It is not a rerun of the independently executed finite checkers.
The inherited all-size contracts remain conditional after this binding.
"""

import argparse
from collections import Counter
from fractions import Fraction as F
import json
from pathlib import Path
import sys

from review_fused_lifetime import (KAPPA, check_inventory, complete_profile,
    digest, encode, exact_match, histogram, need, pinned_bytes, profiles)


def verify(root, config, binding):
    rows = check_inventory(root, config)
    read = lambda pin: json.loads(pinned_bytes(root, pin))
    finite = {name: read(pin) for name, pin in binding["receipts"].items()}
    extra = binding["supplemental_sources"]
    for pin in extra.values():
        data = pinned_bytes(root, pin)
        need(len(data) == pin["bytes"], "Supplemental review source byte count")
    arithmetic, binary, fresh, geometry, signed, scalar = (finite[name] for name in
        ("arithmetic", "binary", "binary_profile", "geometry", "signed", "scalar_bounds"))
    need(arithmetic["config_sha256"] == binding["arithmetic_config_sha256"]
         and arithmetic["certificate_sha256"] == binding["author_receipt_sha256"]
         and F(arithmetic["kappa"]) == KAPPA, "Frozen arithmetic identity")
    need(binary["plan_sha256"] == config["inputs"]["bit_frames"]["sha256"]
         and binary["supplied_profile_sha256"] == config["inputs"]["bit"]["sha256"],
         "Binary finite plan/profile identity")
    exact_match(binary["profile"], fresh, "Independent freshly counted binary profile")
    bp, cp, rank, _ = profiles(fresh, rows["physical"])
    exact_match(arithmetic["bit_profile"], bp, "Arithmetic binary profile is independently finite")
    exact_match(arithmetic["complex_profile"], cp, "Arithmetic complex profile identity")
    exact_match(arithmetic["contaminated_bit_rank"], rank, "Complete independent fallback rank")
    pins = list(config["sources"].values())+list(config["inputs"].values())+list(extra.values())
    hashes = {pin["sha256"] for pin in pins}
    for field in ("source_sha256", "source170_sha256", "regenerated_export_sha256"):
        for name, sha in binary[field].items():
            need(sha in hashes, "Binary finite source omitted: "+name)
    for name, sha in geometry["input_sha256"].items():
        need(sha in hashes, "Reflected review source omitted: "+name)
    mapping = dict(candidate_frames="complex_frames", candidate_profile="physical",
        graph="complex_graph", word="complex_word", witness="complex_logical_frames",
        pairs="complex_pairs", record="scalar", fused_construction_protocol="complex_protocol")
    for name, key in mapping.items():
        need(geometry["input_sha256"][name] == config["inputs"][key]["sha256"],
             "Reflected candidate identity: "+name)
    for finite_row in (signed, scalar):
        for name, pin in rows["complex_protocol"]["input_pins"].items():
            need(finite_row["input_pins"][name]["sha256"] == pin["sha256"]
                 and finite_row["input_pins"][name]["bytes"] == pin["bytes"],
                 "Exact signed/core candidate identity: "+name)
    exact_match(signed["complete_paid_profile"], rows["physical"], "Exact signed full paid profile")
    # Recompute both reflected distributions from the explicitly charged
    # local/source/target transitions, retaining the data final children.
    for orientation in ("forward", "reflected"):
        paid = geometry[orientation]["paid"]
        H = Counter()
        for field in ("local", "source", "target"):
            for r, n in histogram(paid[field], "Geometry "+orientation+" "+field).items():
                H[r] += 3*n
        H[2] += 2*rows["physical"]["v"]
        H.pop(0, None)
        need(dict(H) == cp["hist"], "Full reflected charged distribution: "+orientation)
        need(paid["endpoint_adapter"] == {"0": 1320}, "Explicit rank-zero endpoint adapters")
    need(histogram(geometry["histogram"], "Reflected complete histogram") == cp["hist"]
         and (geometry["m"], geometry["W"], geometry["rank"], geometry["deficit"], geometry["children"])
         == (66,14843,978318,1320,cp["edges"]), "Reflected complete paid inventory")
    need(histogram(binary["reflection"]["reflected_complete_child_histogram"], "Binary reflected children")
         == bp["hist"], "Binary reflected paid distribution")
    prime = binary["prime_summary"]
    need(prime["prime_lower_bound"] == 1 << 80 and prime["maximum_new_determinant_bits"] <= 80
         and prime["inherited_prime_exclusion_sources"], "Original and new eligible-prime scope")
    need(scalar["logical_roles"] == 14843 and scalar["physical_roles"] == 12203
         and scalar["q"] == 3157 and scalar["three_q"] == 9471
         and scalar["coefficient_denominator_divides"] == 6
         and F(scalar["max_adjoint_coefficient"]) <= 26
         and scalar["max_adjoint_numerator_over_6"] == 6
         and scalar["max_literal_read_numerator_over_6"] == 6
         and F(scalar["max_root_coefficient"]) == F(1,2)
         and scalar["literal_M"] == 33568 and scalar["dirty_numerator_bit_upper"] == 33584
         and scalar["local_expanded_group_upper"] == arithmetic["bridge"]["local_scalar"] == 5264026273944,
         "Exact scalar coefficient and expanded precision bound")
    expected_status = dict(binary="PASS_INDEPENDENT_BINARY_FINITE",
        geometry="PASS_EXACT_REFLECTED_GEOMETRY_AND_INVERSE_ALGEBRA",
        signed="PASS_EXACT_SIGNED_ARBITRARY_DIRTY_CORE", scalar_bounds="PASS_EXACT_EXPANDED_SCALAR_BOUNDS")
    for name, status in expected_status.items():
        need(finite[name]["status"] == status, "Independent executed finite review did not pass")
    # Source code digests bind which checkers ran. Source imports are retained
    # by the corresponding finite lane's explicit recovery manifests.
    for name, field in (("binary","checker_sha256"), ("binary","producer_reconstruction_code_sha256"),
        ("binary","exact_algebra_sha256"), ("geometry","checker_sha256"),
        ("signed","exact_checker_sha256"), ("signed","driver_sha256"),
        ("scalar_bounds","driver_sha256")):
        need(finite[name][field] in hashes, "Executed independent checker source omitted: "+name+" "+field)
    return dict(status="ACCEPTED_CONDITIONAL", candidate_id=config["candidate_id"], kappa=KAPPA,
        arithmetic_config_sha256=binding["arithmetic_config_sha256"],
        author_receipt_sha256=binding["author_receipt_sha256"],
        source_records=len(config["sources"]), input_records=len(config["inputs"]),
        independent_review_sources=extra, receipt_pins=binding["receipts"],
        binary_profile=bp, complex_profile=cp,
        binary_formal_orientations=2, binary_formal_columns=22252,
        binary_physical_events=binary["reflection"]["literal_physical_events"],
        complex_reflected_events_per_orientation=geometry["reflected"]["event_count"],
        coefficient_adjoint_entries=scalar["expanded_adjoint_coefficients_checked"],
        coefficient_literal_read_entries=scalar["expanded_literal_read_coefficients_checked"],
        new_bit_determinant_bits=prime["maximum_new_determinant_bits"],
        retained_bit_determinant_bits=prime["maximum_retained_chosen_determinant_bits"],
        retained_prime_exclusions=prime["inherited_prime_exclusion_sources"],
        PUBLICATION_READY=False,
        scope="Independent arithmetic, freshly counted finite binary F2/local-ring/physical reflection, exact signed complex core and scalar bounds, full complemented complex geometry are tied to one immutable141-source24-input candidate. This binding does not replace their separately executed finite checks.",
        hypotheses=config["inherited_hypotheses"],
        publication_scope="The pinned171 comparison is historical. Live frontier, user one-percent gate, current upstream compatibility and tested standalone package remain separate publication conditions.")


def main():
    need(not sys.flags.optimize, "Assertion-disabled Python is unsupported")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sprint", type=Path, default=Path(__file__).resolve().parents[3])
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--binding", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    need(not args.output.exists(), "Fresh finite binding identity required")
    config, binding = (json.loads(q.read_text()) for q in (args.config,args.binding))
    need(digest(args.config) == binding["arithmetic_config_sha256"], "Binding config identity")
    result = verify(args.sprint, config, binding)
    result.update(binding_config_sha256=digest(args.binding), binder_sha256=digest(Path(__file__)))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(result),sort_keys=True,indent=2)+"\n")
    print("ACCEPTED_CONDITIONAL: "+str(KAPPA)+"; all independent finite receipts bind to frozen141/24; PUBLICATION_READY=false")


if __name__ == "__main__":
    main()
