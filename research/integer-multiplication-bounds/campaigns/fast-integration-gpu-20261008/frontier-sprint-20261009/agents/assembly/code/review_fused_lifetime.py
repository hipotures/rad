#!/usr/bin/env python3
"""Independent review of the frozen fused-complex/lifetime-bit composition.

Apache-2.0. Prepared for RaD with OpenAI GPT-6.1 Sol assistance.
Only stdlib and this lane's independent arithmetic helpers are imported.
No supplier, candidate, discovery or predecessor checker is imported.
The paid bridge and transfer equations retain the original PR23/29,
James Chang PR34, RaD, Rohan Arun PR100/103, icekylinx/eumemic PR168,
chafreaky PR163 and PR170 contribution lineage. See ../NOTICE.

This is an arithmetic review of explicitly bound finite inputs. The new
binary alias geometry/F2/local-ring and complex signed/reflected finite
reviews are separate prerequisites, as are the retained all-size contracts.
"""

import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
from fractions import Fraction as F
import json
import gzip
from math import prod
from pathlib import Path
import subprocess
import sys
import time

from review_balanced_unified import (BAD, OLD, complete_profile, digest,
    encode, exact_match, histogram, integer, moment, need, pinned_bytes,
    thresholds)
from review_rebuilt168_ceiling import native_assembly

COARSE = F(161677519, 250000000000)
ATOM = F(323158477, 500000000000)
COMPLEX = F(617664283, 10**12)
BETA = F(1, 10**9)
ETA = F(1, 10**8)
WEAKENING = F(1, 10**10)
KAPPA = F(617282890, 10**12)
PUBLIC = F(305534205135809, 500000000000000000)
PUBLIC_HEAD = "89d0c75f8bf97131db21bc610e7546b699afcb9a"


def profiles(bit, physical):
    """Rebuild both complete physical histograms from charged components."""
    bp = complete_profile(bit, (72, 22252, 1600208, 60), component=True)
    cp = complete_profile(physical, (66, 14843, 978318, 20), component=True)
    need(tuple(integer(bit[k], k) for k in ("h", "v", "R", "loss"))
         == (24, 1760, 20492, 528), "Actual lifetime binary inventory")
    need(tuple(integer(bit[k], k) for k in ("physical_R", "pairs", "late_pairs"))
         == (18732, 1760, 1760), "Actual binary compensated aliases")
    need(bit["physical_R"] == bit["R"]-bit["pairs"]
         and bp["W"] == 2*bit["v"]+bit["physical_R"]
         and bp["m"] == 3*bit["h"], "Actual binary persistent stock")
    need(histogram(bit["physical_gauge_histogram"], "physical bit gauges")
         == {20: 2200} and bit["selected_roles"] == 2200
         and bit["logical_selected_roles"] == 3960, "Actual bit gauge inventory")
    need(bp["m"]*bp["W"]-bp["mass"] == 2*bit["v"]-3*bit["loss"] == 1936,
         "Binary telescoping deficit")
    rare_rank = F(bp["mass"])+BAD*32*bp["m"]**2*bp["edges"]
    rare_gap = BAD-F(2*bp["m"]**3, 1 << 80)
    need(rare_gap > 0 and rare_rank < bp["m"]*bp["W"], "Full rare-class envelope")
    return bp, cp, rare_rank, rare_gap


def full_bill(physical, scalar, cp, coarse=COARSE, atom=ATOM):
    """Derive full group, expanded scalar, routing, precision and row charges."""
    h, v, R, c, roots, M, matching, loss = (integer(scalar[k], k, 1)
        for k in ("h", "v", "R", "c", "q", "total_M_operations", "matched", "loss"))
    need((h, v, R, c, roots, M, matching, loss)
         == (22, 1320, 14843, 20045, 3157, 33568, 8359, 440),
         "Actual frozen fused scalar graph")
    need(R == c+roots-matching, "Actual fused matching inventory")
    need((physical["h"], physical["v"], physical["R"], physical["loss"])
         == (h, v, R, loss), "Scalar/physical plan mismatch")
    need((physical["physical_R"], physical["pairs"], physical["late_pairs"])
         == (12203, 2640, 2640), "Actual frozen complex alias inventory")
    need(physical["physical_R"] == R-physical["pairs"]
         and cp["m"] == 3*h and cp["W"] == 2*v+physical["physical_R"]
         and cp["m"]*cp["W"]-cp["mass"] == 2*v-3*loss == 1320,
         "Actual complex stock and telescoping")
    need(3*roots < 1 << 15, "Dirty readout numerator expansion")
    m, half = cp["m"], cp["m"]//2
    V = (1 << (m-1+(half-1)**2))*prod((1 << (2*i))-1 for i in range(1, half))
    W, s, N = V*cp["W"], V*cp["mass"], V*v
    setup = 4*(c+v)+10*v+4*h*v+4*h*h+8*h+8+2*h
    readout, involution = 8*R*v*(M+16), 32*v
    local = setup+readout+involution
    logical = 3*V*local+8*W+4*N+8*m*R*V
    router = 64*(m+1)**3*(logical+1)*(W+1)**2
    E = 64*(W+m+router+1)**3
    literal = 2*router*W*W+8*s+4*W+4+32*m
    B, C0 = s+E, 32*m*(s+E)**2
    degree = 1
    while m**degree <= 2*cp["maxchild"]**degree:
        degree += 1
    coefficient = degree*W.bit_length()+9909+252
    ordinary = (1-atom)*coarse+atom*OLD
    out = dict(V=V, W=W, s=s, N=N, m=m, maxchild=cp["maxchild"],
        physical_roles=physical["physical_R"], scalar_roles=R, reuse_pairs=physical["pairs"],
        local_scalar=local, logical_scalar=logical, router=router, E=E, literal=literal,
        B=B, C0=C0, C1=1, strict_literal_gap=E-literal,
        induction_gap=2*B*(m-cp["maxchild"])-s-E, guard_gap=C0-2*B-18,
        halving_degree=degree, wire_bits=W.bit_length(), complex_coefficient=degree*W.bit_length(),
        old_coarse_reserve=9909, old_leaf_reserve=252, row_coefficient=coefficient,
        row_degree=70000, row_gap=F(70000)-F(51*coefficient, 25), suffix_slope=280000,
        ordinary_saving=ordinary, atom=atom, coarse=coarse, old=OLD,
        adapter_gap=atom-ordinary, internal_row_gap=1-ordinary-atom, fixed_odd_divisor=3)
    need(all(out[k] > 0 for k in ("strict_literal_gap", "induction_gap", "guard_gap",
                                  "row_gap", "adapter_gap", "internal_row_gap")),
         "Full finite guard, row or paid adapter bill")
    need(local == 5264026273944 and coefficient == 12320, "Fresh full scalar/row check")
    details = dict(setup_scalar=setup, expanded_readout_scalar=readout,
        involution_scalar=involution, scalar_coefficient_bound=h+4,
        decoder_denominator_divides=6, readout_numerator_binary_digits=M+16,
        full_group_bits=V.bit_length(),
        common_odd_grid="One common dyadic grid times 3^(-K_grid); incoming odd exponent retained; no child rounding",
        selector_rows="Internally borrowed and restored under the completed ordinary wrapper",
        paid_atom_optimum=coarse/(1+coarse-OLD))
    return out, details


def independent_derivation(bit, physical, scalar):
    bp, cp, rare_rank, rare_gap = profiles(bit, physical)
    intervals = dict(bit_moment=moment(bp, COARSE, True),
        bit_next_grid=moment(bp, COARSE+F(1, 10**12), True),
        complex_moment=moment(cp, COMPLEX),
        complex_next_grid=moment(cp, COMPLEX+F(1, 10**12)))
    need(intervals["bit_moment"]["upper"] < 1
         and intervals["bit_next_grid"]["lower"] > 1
         and intervals["complex_moment"]["upper"] < 1 < intervals["complex_next_grid"]["lower"],
         "Complete supplier strict enclosures")
    bill, details = full_bill(physical, scalar, cp)
    assembly = native_assembly(bill, COMPLEX, BETA, ETA, WEAKENING, KAPPA)
    need(assembly["a"] == (1-BETA)*COMPLEX-WEAKENING
         and assembly["a"] < bill["ordinary_saving"], "Actual complex-limited interface")
    floor = PUBLIC*F(101, 100)
    need(KAPPA > floor, "Pinned one-percent publication floor")
    return dict(bit_profile=bp, complex_profile=cp, contaminated_bit_rank=rare_rank,
        prime_bad_fraction_gap=rare_gap, independent_intervals=intervals,
        bridge=bill, scalar_bill_details=details, assembly=assembly,
        cutoffs=thresholds(bill, assembly), kappa=KAPPA,
        coarse_bit_saving=COARSE, atom=ATOM, ordinary_bit_saving=bill["ordinary_saving"],
        complex_saving=COMPLEX, public_comparison=dict(public_head=PUBLIC_HEAD,
            public_kappa=PUBLIC, required_ratio=F(101, 100), publication_floor=floor,
            improvement=KAPPA-PUBLIC, relative_ratio=KAPPA/PUBLIC,
            floor_gap=KAPPA-floor,
            scope="Pinned mathematical PR171 comparison; live refresh belongs to coordinator"))


def verify_author_intervals(author, intervals):
    for name in ("bit_moment", "bit_next_grid", "complex_moment", "complex_next_grid"):
        row = author[name]
        need(set(row) == {"lower", "upper", "gap_lower"}, "Author interval fields")
        lo, hi, gap = (F(row[k]) for k in ("lower", "upper", "gap_lower"))
        own = intervals[name]
        need(0 < lo <= own["lower"] <= own["upper"] <= hi and gap == 1-hi,
             "Author interval does not contain independent enclosure: "+name)
        need(hi < 1 if name.endswith("moment") else lo > 1,
             "Author interval lacks strict separation: "+name)


def check_inventory(root, config):
    """Require every declared pin to match bytes before reading any verdict."""
    rows = {}
    for name, pin in config["inputs"].items():
        data = pinned_bytes(root, pin)
        need(len(data) == pin["bytes"], "Input byte count: "+name)
        if pin.get("encoding") == "gzip":
            data = gzip.decompress(data)
            from hashlib import sha256
            need(sha256(data).hexdigest() == pin["decoded_sha256"], "Decoded input: "+name)
        rows[name] = json.loads(data)
    for name, pin in config["sources"].items():
        data = pinned_bytes(root, pin)
        need(len(data) == pin["bytes"], "Source byte count: "+name)
    need({"bit", "physical", "scalar"}.issubset(rows), "Missing physical/scalar inputs")
    return rows


def source_and_raw_plan_closure(config, rows):
    """Cross-bind actual scalar inventories and every current declared source."""
    source_pins = list(config["sources"].values())
    input_pins = list(config["inputs"].values())
    def require_record(relative, expected, pins=source_pins):
        if isinstance(expected, dict):
            sha, size = expected["sha256"], expected.get("bytes")
        else:
            sha, size = expected, None
        matches = [pin for pin in pins if
            (pin["path"] == relative or pin["path"].endswith("/"+relative))
            and pin["sha256"] == sha and (size is None or pin["bytes"] == size)]
        need(bool(matches), "Declared source/plan closure missing: "+relative)
    for name, pin in rows["complex_protocol"]["input_pins"].items():
        require_record(name, pin, input_pins)
    for name, sha in rows["complex_protocol"]["search_sha256"].items():
        require_record(name, sha)
    for name, sha in rows["complex_protocol"]["source_context"]["source_sha256"].items():
        require_record(name, sha)
    protocol = rows["bit_protocol"]
    for block in protocol["source_files"].values():
        for name, pin in block.items():
            require_record(name, pin)
    need(any(pin["sha256"] == protocol["program_sha256"] for pin in source_pins),
         "Actual binary generator omitted")
    for block in rows["bit_source_manifest"].values():
        if isinstance(block, dict) and "files" in block:
            for name, pin in block["files"].items():
                require_record(name, pin)
    discovery = rows["complex_base_protocol"]["discovery_protocol"]
    for name, sha in discovery["dependency_pins"].items():
        require_record(name, sha)
    need(any(pin["sha256"] == discovery["driver_sha256"] for pin in source_pins),
         "Actual fused complex generator omitted")
    for row in config["closure_requirements"]:
        pin = config[row["section"]][row["key"]]
        need(pin["sha256"] == row["sha256"], "Recovery manifest differs")
    bit, scalar, physical = (rows[k] for k in ("bit", "scalar", "physical"))
    for name, sha in bit["source_sha256"].items():
        require_record(name, sha, input_pins)
    exact_match(rows["bit_frames"]["source_sha256"], bit["source_sha256"], "Actual bit compiled plan")
    graph, logical, word = (rows[k] for k in ("complex_graph", "complex_logical_frames", "complex_word"))
    need((graph["h"], graph["v"], len(graph["args"])-graph["v"], len(graph["roots"]),
          len(logical["matching_arcs"]), len(word["ops"]), len(word["opcoeff"]))
         == (22, 1320, 20045, 3157, 8359, 33568, 33568), "Raw complex scalar inventory")
    need(len(word["selected"]) == len(rows["complex_pairs"]) == 2640
         and len(rows["complex_frames"]) == physical["changed_operation_frames"] == 14526,
         "Raw complex frozen placement inventory")
    bit_graph, bit_word = rows["bit_graph"], rows["bit_word"]
    need((len(bit_graph["args"])-bit["v"], len(bit_graph["roots"]),
          len(bit_word["arcs"]), len(bit_word["ops"])) == (22556, 6624, 8688, 41288),
         "Raw binary scalar inventory")
    need(len(rows["bit_frames"]["pairs"]) == 1760
         and len(rows["bit_frames"]["frames"]) == bit["changed_operation_frames"] == 2186,
         "Raw binary frozen placement inventory")
    need(F(rows["frontier_claim"]["kappa"]) == PUBLIC, "Source-confirmed frontier certificate")
    return dict(complex_centres=20045, complex_roots=3157, complex_matching=8359,
        complex_operations=33568, complex_logical_roles=14843, complex_physical_roles=12203,
        complex_pairs=2640, complex_replacement_frames=14526,
        binary_centres=22556, binary_roots=6624, binary_matching=8688, binary_operations=41288,
        binary_logical_roles=20492, binary_physical_roles=18732, binary_pairs=1760,
        binary_replacement_frames=2186,
        scope="Raw inventory and immutable byte agreement; independent finite checks establish identities and geometry")


def main():
    need(not sys.flags.optimize, "Assertion-disabled Python is unsupported")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sprint", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), "Fresh review identity required")
    started = time.monotonic()
    config, author = (json.loads(p.read_text()) for p in (args.config, args.certificate))
    rows = check_inventory(args.sprint, config)
    raw_inventory = source_and_raw_plan_closure(config, rows)
    exact_match(author["source_pins"], config, "Author complete inventory")
    need(author["config_sha256"] == digest(args.config), "Author config identity")
    for name, value in dict(coarse=COARSE, atom=ATOM, complex_saving=COMPLEX,
        phase_stop=BETA, backoff=ETA, strict_weakening=WEAKENING, kappa=KAPPA,
        comparison_public_kappa=PUBLIC, required_publication_ratio=F(101, 100)).items():
        exact_match(config[name], value, "config."+name)
    need(config["comparison_public_head"] == PUBLIC_HEAD, "Pinned public claim head")
    own = independent_derivation(rows["bit"], rows["physical"], rows["scalar"])
    for name in ("bit_profile", "complex_profile", "contaminated_bit_rank", "bridge", "assembly",
                 "kappa", "coarse_bit_saving", "atom", "ordinary_bit_saving", "complex_saving", "cutoffs"):
        exact_match(author[name], own[name], "Independent "+name)
    verify_author_intervals(author, own["independent_intervals"])
    rejected = []
    def reject(name, call):
        try:
            call()
        except (ValueError, KeyError, ZeroDivisionError):
            rejected.append(name)
        else:
            raise ValueError("Negative control accepted: "+name)
    for name, field, value in (
        ("local width substituted for full group stock", "W", own["complex_profile"]["W"]),
        ("virtual scalar reserve collapsed", "scalar_roles", rows["physical"]["physical_R"]),
        ("expanded scalar bill omitted", "local_scalar", 0),
        ("routing bill omitted", "router", 0),
        ("stale semantic precision guard", "C0", 1),
        ("ordinary coarse reserve omitted", "old_coarse_reserve", 0),
        ("ordinary leaf reserve omitted", "old_leaf_reserve", 0),
        ("row coefficient understated", "row_coefficient", 1),
        ("row degree understated", "row_degree", 1),
        ("ordinary supplier overstated", "ordinary_saving", str(own["ordinary_bit_saving"]+F(1,10**24))),
    ):
        mutation = copy.deepcopy(author["bridge"])
        mutation[field] = value
        reject(name, lambda row=mutation: exact_match(row, own["bridge"], "Mutated full bill"))
    mutation = copy.deepcopy(rows["bit"])
    mutation["child_histogram"]["1"] += 2
    mutation["child_histogram"]["2"] -= 1
    reject("mass-preserving unpaid binary children", lambda: profiles(mutation, rows["physical"]))
    mutation = copy.deepcopy(rows["physical"])
    mutation["child_histogram"]["1"] += 2
    mutation["child_histogram"]["2"] -= 1
    reject("mass-preserving unpaid complex children", lambda: profiles(rows["bit"], mutation))
    reject("preceding unpaid atom", lambda: full_bill(rows["physical"], rows["scalar"],
        own["complex_profile"], atom=ATOM-F(1,10**12)))
    reject("next final twelve-digit grid", lambda: native_assembly(own["bridge"], COMPLEX,
        BETA, ETA, WEAKENING, KAPPA+F(1,10**12)))
    reject("zero complex stop", lambda: native_assembly(own["bridge"], COMPLEX,
        F(0), ETA, WEAKENING, KAPPA))
    reject("zero balanced reserve", lambda: native_assembly(own["bridge"], COMPLEX,
        BETA, F(0), WEAKENING, KAPPA))
    reject("strict margin used as kappa", lambda: native_assembly(own["bridge"], COMPLEX,
        BETA, ETA, WEAKENING, own["assembly"]["g"]))
    mutation = copy.deepcopy(author)
    mutation["bit_moment"]["upper"] = "9/10"
    mutation["bit_moment"]["gap_lower"] = "1/10"
    reject("fabricated saved moment", lambda: verify_author_intervals(mutation, own["independent_intervals"]))
    reject("input corruption", lambda: pinned_bytes(args.sprint,
        dict(config["inputs"]["bit_frames"], sha256="0"*64)))
    mutation = copy.deepcopy(config)
    missing = "references/three-stage-cover/pr117/LICENSE"
    mutation["sources"].pop(missing)
    reject("inherited license closure omitted", lambda: source_and_raw_plan_closure(mutation, rows))
    reject("unsafe relative source path", lambda: pinned_bytes(args.sprint,dict(path="../escape",sha256="0"*64)))
    probe = subprocess.run([sys.executable, "-O", str(Path(__file__).resolve()), "--help"],
                           capture_output=True, text=True)
    need(probe.returncode != 0 and "Assertion-disabled Python" in probe.stderr, "Optimized execution accepted")
    rejected.append("assertion-disabled execution")
    result = dict(status="PASS_INDEPENDENT_FUSED_LIFETIME_ARITHMETIC_PENDING_FINITE_GATES",
        candidate_id=config["candidate_id"], **own,
        actual_raw_inventory=raw_inventory, rejected_controls=rejected,
        checked_inputs=len(config["inputs"]), checked_sources=len(config["sources"]),
        input_pins=config["inputs"], source_pins=config["sources"],
        config_sha256=digest(args.config), certificate_sha256=digest(args.certificate),
        checker_sha256=digest(Path(__file__)),
        own_helper_sha256={name: digest(Path(__file__).with_name(name)) for name in
            ("review_balanced_unified.py", "review_rebuilt168_ceiling.py")},
        proof_boundaries=dict(binary="New alias plan, source/F2/bank-complement/dual-Gram and original exclusions require independent finite review",
            complex="New positive-first fused graph, matching, gauges,2640 aliases and raised frames require independent signed/reflected review",
            transfer="Named balanced layout, complete ordinary restoration, paid arbitrary-coordinate router, full bulk passes and semantic recovery remain inherited conditional contracts",
            formal="No unconditional all-size theorem, practical threshold or hosted-CI success is asserted"),
        elapsed_seconds=time.monotonic()-started, observation_utc=datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(encode(result), indent=2, sort_keys=True)+"\n")
    print("PASS independent fused/lifetime arithmetic; kappa="+str(KAPPA)
        +"; all full bills and47+7; sources="+str(len(config["sources"]))
        +"; inputs="+str(len(config["inputs"])))
    print("Strict absorption gap="+str(own["assembly"]["absorption_gap"])
        +"; pinned one-percent gap="+str(own["public_comparison"]["floor_gap"]))


if __name__ == "__main__":
    main()
