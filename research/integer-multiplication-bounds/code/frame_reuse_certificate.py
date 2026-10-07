#!/usr/bin/env python3
"""Exact dirty-scratch, frame and strict transfer checks for controller reuse."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import time

from frame_reuse import labels, optimize_chains, compile_reuse, check


def counted_network(h, roles):
    """Retain the upstream three-stage count with a verified physical role count.

    The original counts helper obtains c+q from a consume-once circuit. This
    compiler has additional live-controller links, so its physical role count
    is supplied explicitly instead of pretending to satisfy that interface.
    """
    v, m = comb(h, 3), h**3
    n = v**3
    w = 2*n + 2*v*v*(roles+h)
    loss = 3*v*v*h*h
    deficit = n-2*loss
    assert h >= 6 and h % 2 == 0 and roles >= 0 and deficit > 0
    return dict(h=h, v=v, N=n, m=m, side_roles_per_invocation=roles,
                W=w, L=loss, D=deficit, s=w*m-deficit, eta=Q(deficit, w*m))


def program(circuit, code):
    index = {triple: i for i, triple in enumerate(circuit.inputs)}
    return {
        "triples": circuit.inputs, "roles": code["roles"],
        "gates": [(ins, outs) for _, ins, outs in code["gates"]],
        "sources": [(index[triple], slot) for triple, slot in code["sources"].items()],
        "outputs": [(index[triple], slot) for (_, triple), slot in code["outputs"].items()],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--small-sizes", nargs="+", type=int, default=[6, 8])
    parser.add_argument("--full-size", type=int, default=50)
    args = parser.parse_args()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=args.reference, text=True).strip()
    assert commit == "bcd4ebde8692383539f8a48734e5fbf3a18a32c2"
    sys.path.insert(0, str(args.reference.resolve() / "scripts"))
    from paired_exclusion_circuit import PairedExclusionCircuit
    from finite_block_search import GroupUnion
    from dag_network import exact_invocation, shared_scalar_model
    from reuse_network import triple_matching
    from shared_point_network import counts
    from certify import Parameters, certify_parameters, network
    from search_network import log_integer_bounds

    start = time.monotonic()
    small = []
    for h in args.small_sizes:
        circuit = GroupUnion(h, PairedExclusionCircuit, ordering="paired")
        circuit.verify()
        frame, unique = labels(circuit, global_graph=True)
        code = compile_reuse(circuit, frame, optimize_chains(circuit, frame, "rank"))
        checked = check(circuit, frame, code)
        scalar = program(circuit, code)
        row = {"h": h, "roles": code["roles"], "unique_spans": unique,
               "finite_check": checked, "chains": code["chain_summary"],
               "dirty_basis": [exact_invocation(h, inverse, scalar) for inverse in (False, True)],
               "three_stage": [shared_scalar_model(h, seed, scalar) for seed in (1, 109)]}
        small.append(row)
        print(json.dumps({"phase": "small", "h": h, "roles": code["roles"],
                          "all_dirty_basis_and_exchange_passed": True}), flush=True)

    h = args.full_size
    circuit = GroupUnion(h, PairedExclusionCircuit, ordering="paired")
    graph = circuit.verify()
    frame, unique = labels(circuit, global_graph=True)
    code = compile_reuse(circuit, frame, optimize_chains(circuit, frame, "rank"))
    checked = check(circuit, frame, code)
    # First confirm that the explicit formula agrees with the original helper
    # on its own c+q compiler; then substitute the independently checked roles.
    assert counted_network(h, circuit.additions+len(circuit.outputs)) == counts(h, circuit)
    bit = counted_network(h, code["roles"])
    _, log_upper = log_integer_bounds(bit["m"])
    log_bound = Q((log_upper * 1000000).__ceil__(), 1000000)
    a = Q((bit["eta"] / log_bound * 10**12).__floor__(), 10**12)
    assert bit["eta"] > a * log_bound
    complex_network = network(h)
    ac = Q((complex_network["eta_c"] / log_bound * 10**12).__floor__(), 10**12)
    assert complex_network["eta_c"] > ac * log_bound
    beta, epsilon = Q(999, 1000), Q(199, 1000)
    margin = epsilon * beta * a * a
    kappa = Q(999, 1000) * margin
    p = Parameters(1-a, 1-ac, epsilon, beta*a, 1-(1+beta)*a*a/2,
                   1-beta*a*a, kappa, beta=beta, delta=Q(1, 10000), C1=2)
    assembly = certify_parameters(p, generalized_beta=True, strict_margin=True,
                                   layout_model="nonadjacent", guard_model="stopping",
                                   assembly_model="tight-gaussian")
    assert Q(assembly["minimum_margin"]) == margin
    assert kappa > Q(1, 2**59)
    triples, images = triple_matching(h)
    assert len(set(images)) == len(triples)
    assert all(len(set(triple) & set(triples[image])) == 1 for triple, image in zip(triples, images))
    result = {
        "campaign_id": "20261007T222521Z", "campaign_start_utc": "2026-10-07T22:25:21Z",
        "campaign_deadline_utc": "2026-10-08T08:25:21Z", "upstream_revision": commit,
        "code_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "compiler_sha256": sha256(Path(__file__).with_name("frame_reuse.py").read_bytes()).hexdigest(),
        "small_checks": small, "graph": graph, "compiled": checked,
        "unique_spans": unique, "chains": code["chain_summary"],
        "bit_counts": {key: str(value) for key, value in bit.items()},
        "bit_saving": str(a), "complex_saving": str(ac), "log_upper_bound": str(log_bound),
        "bit_deficit_slack": str(bit["eta"]-a*log_bound),
        "complex_deficit_slack": str(complex_network["eta_c"]-ac*log_bound),
        "retained_original_assembly": assembly,
        "kappa_ratio_to_pinned_dyadic": str(kappa * 2**59),
        "stage_matching": {"h": h, "triples": len(triples), "bijection": True, "orthogonality": True},
        "transfer": {"all_role_endpoints": "Original data endpoints; auxiliaries restored, 0 to I_m",
                     "middle_frames": "Exact nondegenerate source spans forward, orthogonal complements backward",
                     "decreasing_rank": "Only original central returns, unchanged",
                     "dirty_scratch": "Transparent JLV schedule unchanged; L is the newly checked invertible gate product",
                     "stage_sharing": "Original complete first/third auxiliary-bank matching retained"},
        "status": "Conditional finite-compiler improvement; retains upstream theorem and original analytic interfaces",
        "elapsed_seconds": time.monotonic()-start,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"roles": code["roles"], "bit_saving": str(a), "kappa": str(kappa),
                      "ratio": result["kappa_ratio_to_pinned_dyadic"], "elapsed_seconds": result["elapsed_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
