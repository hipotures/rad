#!/usr/bin/env python3
"""Independent promotion of a new odd-ground, full-pair bit witness.

The producer's odd constructor and matcher are not imported. This reviewer
reconstructs point orders, the explicit matching and its inverse, and every
coefficient and physical frame. The unchanged weighted recursion and exact
controller compiler are construction inputs, not independent proof claims.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

from finite_block_search import GroupUnion, install_reference, make_block_class
from frame_envelope import labels
from frame_reuse import compile_reuse, optimize_chains
from frame_reuse_certificate import program
from review_aligned_graph import check as logical_check
from review_envelopes import graph_envelope_check
from review_frame_reuse import dirty_check
from review_singleton_positions import compiled_digest, plan_check
from review_singleton_witness import physical_coefficients

REFERENCE_COMMIT = "bcd4ebde8692383539f8a48734e5fbf3a18a32c2"


def candidate_identity(h, base, positions):
    positions = list(positions)
    positions[-1] = 0
    definition = dict(h=h, base=base, positions=positions,
                      construction="odd_orphan_full_pair",
                      reference_commit=REFERENCE_COMMIT)
    return sha256(json.dumps(definition, sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


def build(h, base, positions):
    assert h >= 7 and h % 2 == 1 and h != 9
    assert len(positions) == h and positions[-1] == 0
    pairs = [tuple(range(i, i + 2)) for i in range(0, h - 1, 2)]
    root_orders = []
    for common in range(h):
        position = positions[common]
        assert type(position) is int and 0 <= position < len(pairs)
        if common == h - 1:
            groups = list(pairs)
        else:
            groups = [pair for pair in pairs if common not in pair]
            partner = next(pair for pair in pairs if common in pair)
            orphan = next(x for x in partner if x != common)
            groups.insert(position, (orphan, h - 1))
        order = [x for group in groups for x in group]
        assert sorted(order) == [x for x in range(h) if x != common]
        root_orders.append(order)

    Parent = make_block_class()

    class Ordered(Parent):
        def __init__(self, n, permutation):
            self.root_permutation = tuple(permutation)
            super().__init__(n, (2,), base, 0)

        def pair(self, points):
            ordered = [points[i] for i in self.root_permutation]
            edges = {tuple(sorted((a, b))): self.variables[tuple(sorted((a, b)))]
                     for a, b in combinations(ordered, 2)}
            total, one, two = self.block(ordered, edges,
                                         {point: 0 for point in ordered}, 0)
            return total, one, {tuple(sorted(key)): value
                                for key, value in two.items()}

    def factory(n, common):
        natural = [x for x in range(h) if x != common]
        return Ordered(n, [natural.index(x) for x in root_orders[common]])

    return GroupUnion(h, factory, "natural", 0, True)


def matching(h):
    """Reconstruct the three disjoint classes and check inverse bijectivity."""
    triples = list(combinations(range(h), 3))
    indices = {triple: i for i, triple in enumerate(triples)}
    groups = (h - 1) // 2

    def image(triple, direction):
        if h - 1 in triple:
            a, b = [x for x in triple if x != h - 1]
            if a // 2 != b // 2:
                result = (a ^ 1, b ^ 1, h - 1)
            else:
                chosen = (a // 2 + direction) % groups
                result = (2 * chosen, 2 * chosen + 1, h - 1)
        else:
            occupancy = {}
            for x in triple:
                occupancy.setdefault(x // 2, []).append(x)
            if len(occupancy) == 3:
                kept = min(occupancy)
                result = tuple(x if x // 2 == kept else x ^ 1 for x in triple)
            else:
                full = next(group for group, members in occupancy.items()
                            if len(members) == 2)
                singleton = next(members[0] for members in occupancy.values()
                                 if len(members) == 1)
                cycle = [group for group in range(groups)
                         if group != singleton // 2]
                chosen = cycle[(cycle.index(full) + direction) % len(cycle)]
                result = (2 * chosen, 2 * chosen + 1, singleton)
        return tuple(sorted(result))

    images = []
    for triple in triples:
        target = image(triple, 1)
        assert target in indices and len(set(triple).intersection(target)) == 1
        assert image(target, -1) == triple
        assert image(image(triple, -1), 1) == triple
        images.append(indices[target])
    assert sorted(images) == list(range(len(triples)))
    return images, dict(triples=len(triples), h=h, intersection_one=True,
                        explicit_inverse_and_bijection=True,
                        image_sha256=sha256(json.dumps(
                            images, separators=(",", ":")).encode()).hexdigest(),
                        rational_form_nondegenerate=h != 9)


def shared_exchange(circuit, code, images, seed):
    """Replay the complete exchange without importing the odd producer."""
    from dag_network import invoke
    h = circuit.h
    scalar = program(circuit, code)
    v = len(circuit.inputs)
    width = code["roles"] + h
    inverse = [0] * v
    for source, target in enumerate(images):
        inverse[target] = source
    n = v ** 3

    def payload(i):
        return ((i * 2654435761 + seed * 2246822519) ^ (i * i * 97)) & 0xffffffff

    x = [payload(i) for i in range(n)]
    y = [payload(n + i) for i in range(n)]
    banks = [[payload(2 * n + bank * v * v * width + i)
              for i in range(v * v * width)] for bank in range(2)]
    old_x, old_y = list(x), list(y)
    old_banks = [list(bank) for bank in banks]
    for stage in range(3):
        for a in range(v):
            for b in range(v):
                addresses = [((t * v + a) * v + b) if stage == 0 else
                             ((a * v + t) * v + b) if stage == 1 else
                             ((a * v + b) * v + t) for t in range(v)]
                bank = banks[1 if stage == 1 else 0]
                offset = (a * v + b if stage < 2 else inverse[b] * v + a) * width
                scratch = bank[offset:offset + code["roles"]]
                centers = bank[offset + code["roles"]:offset + width]
                source_bank, target_bank = (y, x) if stage == 1 else (x, y)
                source = [source_bank[i] for i in addresses]
                target = [target_bank[i] for i in addresses]
                invoke(source, target, scratch, centers, scalar, inverse=stage == 1)
                for address, first, second in zip(addresses, source, target):
                    source_bank[address] = first
                    target_bank[address] = second
                bank[offset:offset + width] = scratch + centers
    assert x == old_y and y == old_x and banks == old_banks
    return dict(seed=seed, scalar_invocations=3 * v * v,
                complete_bank_exchange=True,
                arbitrary_auxiliary_banks_restored=True)


def case(h, base, positions, expected=None, small=False, exchange=False):
    begin = time.monotonic()
    circuit = build(h, base, positions)
    logical = logical_check(circuit)
    print("PASS independent logical", h,
          logical["nonzero_partial_coefficients"], flush=True)
    frames, metadata = labels(circuit, True)
    plan = optimize_chains(circuit, frames, "rank")
    chain = plan_check(circuit, frames, plan)
    code = compile_reuse(circuit, frames, plan)
    assert code["roles"] == chain["independently_counted_roles"]
    physical = physical_coefficients(circuit, code)
    rational = graph_envelope_check(circuit, frames, code, dense=small)
    images, matched = matching(h)
    row = dict(h=h, base=base, positions=positions,
               candidate_id=candidate_identity(h, base, positions),
               compiled_roles=code["roles"], compiled_sha256=compiled_digest(code),
               logical=logical, physical=physical, rational_frames=rational,
               controller_plan=chain, optimizer_summary=code["chain_summary"],
               frame_metadata=metadata, stage_matching=matched)
    if expected is not None:
        assert row["candidate_id"] == expected["candidate_id"]
        assert code["roles"] == expected["compiled_roles"]
        assert row["compiled_sha256"] == expected["checked"]["compiled_sha256"]
        assert circuit.additions == expected["original"]["additions"]
        assert len(circuit.outputs) == expected["original"]["partial_outputs"]
        assert chain["selected_links"] == expected["chains"]["selected_links"]
        assert matched["image_sha256"] == expected["stage_matching"]["image_sha256"]
        row["matches_immutable_producer_identity_and_compilation"] = True
    if small:
        from dag_network import exact_invocation
        scalar = program(circuit, code)
        row["complete_side_dirty_basis"] = dirty_check(circuit, frames, code)
        row["complete_invocation_dirty_basis_including_centers"] = [
            exact_invocation(h, inverse, scalar) for inverse in (False, True)]
    if exchange:
        row["complete_shared_three_stage_exchange"] = [
            shared_exchange(circuit, code, images, seed) for seed in (1, 109)]
    row.update(wall_seconds=time.monotonic() - begin,
               process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    print("PASS independent odd witness", h, "roles", code["roles"], flush=True)
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), "Use a fresh result path"
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                     cwd=args.reference, text=True).strip()
    assert commit == REFERENCE_COMMIT
    sys.dont_write_bytecode = True
    install_reference(str(args.reference))
    expected = json.loads(args.candidate.read_text())
    started = datetime.now(timezone.utc).isoformat()
    begin = time.monotonic()
    full = case(expected["h"], expected["base"], expected["positions"], expected)
    small = [case(7, expected["base"], [0, 2, 1, 0, 2, 1, 0],
                  small=True, exchange=True),
             case(11, expected["base"], [0, 4, 1, 3, 2, 0, 3, 1, 4, 2, 0],
                  small=True)]
    names = ("review_odd_pair_witness.py", "finite_block_search.py",
             "frame_envelope.py", "frame_reuse.py", "frame_reuse_certificate.py",
             "review_aligned_graph.py", "review_envelopes.py",
             "review_frame_reuse.py", "review_singleton_positions.py",
             "review_singleton_witness.py", "review_rational_frames.py")
    result = dict(status="PASS", campaign="20261007T222521Z",
                  original_start_utc="2026-10-07T22:25:21Z",
                  user_extended_deadline_utc="2026-10-08T10:00:00Z",
                  started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(),
                  reference_commit=commit, python_version=sys.version,
                  candidate_file_sha256=sha256(args.candidate.read_bytes()).hexdigest(),
                  source_sha256={name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                 for name in names},
                  upstream_sha256={name: sha256((args.reference / "scripts" / name).read_bytes()).hexdigest()
                                   for name in ("dag_network.py", "exclusion_circuit.py")},
                  full=full, small_controls=small,
                  wall_seconds=time.monotonic() - begin,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope="Independent new odd finite coefficient/frame/matching witness; "
                        "complete dirty bases and shared exchange are bounded controls; "
                        "generic rank accounting and complete conditional assembly require separate arguments")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS", args.output, flush=True)


if __name__ == "__main__":
    main()
