#!/usr/bin/env python3
"""Exact small controls for common-dependent globally aligned pair hierarchies.

Authored generic support interning imports the eligible PR40 Apache-2.0 pair
producer and reversible compiler. Upstream credits: icekylinx and the PR7
cancellation-free circuit contributors. No newly published producer is used.
The dense exact support representation is a SMALL search tool, not an
asymptotically efficient replacement for the upstream envelope representation.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
import time


PIN = "43f59ff533598762cbc43a5e14af2bbbc76fabbd"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--dimensions", nargs="+", type=int, default=[6, 7, 8, 10])
    ap.add_argument("--export-dags", action="store_true")
    args = ap.parse_args()
    if sys.flags.optimize or any(h < 6 or h == 9 or h > 20 for h in args.dimensions):
        ap.error("Run without -O, using small dimensions 6..20 except degenerate h=9")
    source = args.source_root.resolve()
    sys.path.insert(0, str(source/"scripts"))
    from exclusion_circuit import ExclusionCircuit
    from partial_swap.paired import PairedExclusionCircuit
    from partial_swap.graph import aligned_points, graph, export

    class GlobalLocal(PairedExclusionCircuit):
        def __init__(self, h, common):
            order = [p for p in range(h) if p != common]
            indices = {p: i for i, p in enumerate(order)}
            # Preserve every original global pair position. For odd h, deleting
            # its singleton leaves an EMPTY coarse vertex whose edges/weight
            # are zero. It keeps all deeper coarse indices aligned.
            self.top_groups = [[indices[p] for p in range(a, min(a+2, h))
                                if p != common] for a in range(0, h, 2)]
            super().__init__(h-1)

        def grouping(self, points):
            if len(points) == self.n:
                assert points == list(range(self.n))
                groups = self.top_groups
            else:
                groups = [points[a:a+2] for a in range(0, len(points), 2)]
            assert sorted(p for group in groups for p in group) == sorted(points)
            assert all(len(group) <= 2 for group in groups)
            assert len(groups) < len(points)
            return groups

    def retained(local):
        total = local.pair(list(range(local.n)))[0]
        local.outputs[()] = total
        stack = [total]
        while stack:
            node = stack.pop()
            if node in local.active:
                continue
            local.active.add(node)
            if local.args[node]:
                stack.extend(local.args[node])
        local.additions = sum(local.args[x] is not None for x in local.active)
        return local

    class ExactGlobal:
        compile = ExclusionCircuit.compile

        def __init__(self, h, mode):
            self.h = h
            self.inputs = list(combinations(range(h), 3))
            self.variables = {t: i+1 for i, t in enumerate(self.inputs)}
            self.args = [None]*(len(self.inputs)+1)
            self.support = [0]+[1 << i for i in range(len(self.inputs))]
            self.core = [0]+[sum(1 << p for p in t) for t in self.inputs]
            self.union = self.core[:]
            lookup = {s: i for i, s in enumerate(self.support)}
            self.outputs, self.local_checks, self.merged = {}, [], 0
            for common in range(h):
                order = aligned_points(h, common) if mode == "baseline" else [p for p in range(h) if p != common]
                local = PairedExclusionCircuit(h-1) if mode == "baseline" else GlobalLocal(h, common)
                self.local_checks.append(local.verify())
                retained(local)
                mapping = {}
                for node in sorted(local.active):
                    if not local.args[node]:
                        a, b = local.inputs[node-1]
                        mapping[node] = self.variables[tuple(sorted((common, order[a], order[b])))]
                        continue
                    a, b = (mapping[p] for p in local.args[node])
                    assert not self.support[a] & self.support[b]
                    support = self.support[a] | self.support[b]
                    if support in lookup:
                        mapping[node] = lookup[support]
                        self.merged += 1
                    else:
                        new = len(self.args)
                        lookup[support] = new
                        mapping[node] = new
                        self.args.append((a, b))
                        self.support.append(support)
                        self.core.append(self.core[a] & self.core[b])
                        self.union.append(self.union[a] | self.union[b])
                        assert self.core[-1] & (1 << common)
                for excluded, node in sorted(local.outputs.items()):
                    target = tuple(sorted((common, *(order[p] for p in excluded))))
                    self.outputs[common, target] = mapping[node]
            self.active, stack = set(), list(self.outputs.values())
            while stack:
                node = stack.pop()
                if not node or node in self.active:
                    continue
                self.active.add(node)
                if self.args[node]:
                    stack.extend(self.args[node])
            self.additions = sum(self.args[x] is not None for x in self.active)

        def verify(self):
            for node in sorted(self.active):
                if self.args[node]:
                    a, b = self.args[node]
                    assert a < node and b < node
                    assert not self.support[a] & self.support[b]
                    assert self.support[node] == self.support[a] | self.support[b]
                    assert self.core[node] == self.core[a] & self.core[b]
                    assert self.union[node] == self.union[a] | self.union[b]
                assert self.core[node]
            for (common, target), node in self.outputs.items():
                excluded = set(target)-{common}
                expected = sum(1 << i for i, triple in enumerate(self.inputs)
                               if common in triple and not excluded.intersection(triple))
                assert self.support[node] == expected
            code = self.compile()
            forward = [0]*code["roles"]
            for triple, slot in code["sources"].items():
                forward[slot] = self.variables[triple]
            for node, ins, outs in code["gates"]:
                for slot in set(ins+outs):
                    assert not self.support[forward[slot]] & ~self.support[node]
                    forward[slot] = node
            for target, slot in code["outputs"].items():
                assert forward[slot] == self.outputs[target]
            backward = [0]*code["roles"]
            for target, slot in code["outputs"].items():
                backward[slot] = self.outputs[target]
            for node, ins, outs in reversed(code["gates"]):
                for slot in set(ins+outs):
                    assert not backward[slot] or not self.support[node] & ~self.support[backward[slot]]
                    backward[slot] = node
            for triple, slot in code["sources"].items():
                assert backward[slot] == self.variables[triple]
            encoded = json.dumps({"args": self.args, "outputs": sorted(self.outputs.items())},
                                 separators=(",", ":")).encode()
            return dict(h=self.h, additions=self.additions, outputs=len(self.outputs),
                        roles=code["roles"], merged_additions=self.merged,
                        circuit_sha256=hashlib.sha256(encoded).hexdigest(),
                        all_partial_outputs_exact=True, all_additions_disjoint=True,
                        all_forward_reverse_frame_inclusions_exact=True)

    args.output.mkdir(parents=True, exist_ok=False)
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    pinned_commit=PIN, dimensions=args.dimensions,
                    wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    source_sha256={p: hashlib.sha256((source/p).read_bytes()).hexdigest()
                                   for p in ("scripts/exclusion_circuit.py", "scripts/partial_swap/paired.py",
                                             "scripts/partial_swap/graph.py", "scripts/partial_swap/binary.py")},
                    scope="Common-dependent global pair hierarchy with exact dense-support control; no moment certificate")
    (args.output/"protocol.json").write_text(json.dumps(protocol, indent=2)+"\n")
    began, results = time.monotonic(), []
    for h in args.dimensions:
        baseline_roles = None
        upstream = graph(h).verify()
        for mode in ("baseline", "global-hierarchy"):
            circuit = ExactGlobal(h, mode)
            row = dict(mode=mode, scalar=circuit.verify(), local_checks=circuit.local_checks)
            if mode == "baseline":
                assert row["scalar"]["additions"] == upstream["additions"]
                assert row["scalar"]["outputs"] == upstream["partial_outputs"]
                assert row["scalar"]["roles"] == upstream["roles"]
                baseline_roles = row["scalar"]["roles"]
                row["upstream_scalar_baseline_equal"] = True
            row["role_delta"] = row["scalar"]["roles"]-baseline_roles
            if args.export_dags:
                path = args.output/("h%d-%s.bin" % (h, mode))
                export(circuit, path)
                row["dag_file"] = path.name
                row["dag_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            results.append(row)
            (args.output/"results.json").write_text(json.dumps(results, indent=2)+"\n")
    summary = dict(status="exact_global_hierarchy_controls_pass", cases=len(results),
                   elapsed_seconds=time.monotonic()-began,
                   comparisons=[dict(h=r["scalar"]["h"], role_delta=r["role_delta"])
                                for r in results if r["mode"] == "global-hierarchy"],
                   scope="Scalar roles only; positive-label matching and complete fixed-basis moments remain untested")
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
