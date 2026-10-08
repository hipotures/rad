#!/usr/bin/env python3
"""Small changed-DAG search using eligible pinned PR40 producer interfaces.

This authored wrapper imports the upstream Apache-2.0 producer; it does not
copy its source. Credits: icekylinx's parameterized retained-total producer,
the PR7 cancellation-free pair circuit and their retained upstream notices.
Output supports and reversible frames are checked exactly. Addition/role
counts only screen candidates; full fixed-basis child moments are not inferred.
"""

import argparse
import hashlib
import heapq
import json
from pathlib import Path
import subprocess
import sys
import time


PIN = "43f59ff533598762cbc43a5e14af2bbbc76fabbd"
REPOSITORY = "https://github.com/rohanarun/integer-mult-bounds"


def patterns(n):
    """All ordered compositions of n into singleton/pair groups, not all singles."""
    if n == 0:
        yield ()
        return
    for first in (2, 1):
        if first <= n:
            for rest in patterns(n-first):
                result = (first,)+rest
                if 2 in result:
                    yield result
                # Intermediate all-single suffixes must survive recursion.
    # The suffix consisting entirely of singles is needed in larger patterns.
    yield (1,)*n


def selected_patterns(n, limit):
    baseline = (2,)*(n//2)+(1,)*(n % 2)
    result, seen = [baseline], {baseline}
    for item in patterns(n):
        if 2 not in item or item in seen:
            continue
        seen.add(item)
        result.append(item)
        if len(result) >= limit:
            break
    return result[:limit]


def retain_total(local):
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path,
                        help="Fresh task-owned ignored execution directory")
    parser.add_argument("--dimensions", nargs="+", type=int, default=[6, 7, 8, 10])
    parser.add_argument("--max-patterns", type=int, default=16)
    parser.add_argument("--associations", nargs="+", choices=["balanced", "left", "right", "small-first"],
                        default=["balanced", "small-first"])
    parser.add_argument("--thresholds", nargs="+", type=int, default=[2])
    parser.add_argument("--export-dags", action="store_true")
    parser.add_argument("--matcher-directory", type=Path,
                        help="Directory containing precompiled match_exported_dag and match_positive_dag")
    args = parser.parse_args()
    if sys.flags.optimize:
        parser.error("Exact support assertions require Python without -O")
    if args.max_patterns < 1 or any(h < 6 or h == 9 for h in args.dimensions):
        parser.error("Use positive pattern limit, dimensions>=6 and h!=9")
    if any(t < 2 for t in args.thresholds):
        parser.error("Pair recursion base thresholds must be at least two")

    source = args.source_root.resolve()
    sys.path.insert(0, str(source/"scripts"))
    from partial_swap.paired import PairedExclusionCircuit
    from partial_swap.shared import SharedPointCircuit
    from partial_swap.graph import aligned_points, export
    from partial_swap.positive import run as positive_labels

    if args.matcher_directory:
        for name in ("match_exported_dag", "match_positive_dag"):
            if not (args.matcher_directory/name).is_file():
                parser.error("Missing precompiled matcher: "+str(args.matcher_directory/name))

    class ChangedCircuit(PairedExclusionCircuit):
        def __init__(self, n, pattern, association, threshold):
            self.top_pattern = pattern
            self.association = association
            self.base_threshold = threshold
            super().__init__(n)

        def grouping(self, points):
            sizes = self.top_pattern if len(points) == self.n else (2,)*(len(points)//2)+(1,)*(len(points)%2)
            assert sum(sizes) == len(points) and all(s in (1, 2) for s in sizes)
            assert 2 in sizes
            groups, offset = [], 0
            for size in sizes:
                groups.append(points[offset:offset+size])
                offset += size
            return groups

        def total(self, values):
            if self.association == "balanced":
                return super().total(values)
            values = [v for v in values if v]
            if self.association in ("left", "right"):
                if self.association == "right":
                    values = values[::-1]
                result = 0
                for value in values:
                    result = self.add(result, value)
                return result
            heap = [(self.support[x].bit_count(), self.support[x], x) for x in values]
            heapq.heapify(heap)
            while len(heap) > 1:
                _, _, left = heapq.heappop(heap)
                _, _, right = heapq.heappop(heap)
                node = self.add(left, right)
                heapq.heappush(heap, (self.support[node].bit_count(), self.support[node], node))
            return heap[0][2] if heap else 0

    args.output.mkdir(parents=True, exist_ok=False)
    inputs = ["scripts/exclusion_circuit.py", "scripts/partial_swap/paired.py",
              "scripts/partial_swap/shared.py", "scripts/partial_swap/graph.py",
              "scripts/partial_swap/binary.py"]
    protocol = dict(repository=REPOSITORY, pinned_commit=PIN,
                    source_sha256={p: hashlib.sha256((source/p).read_bytes()).hexdigest() for p in inputs},
                    wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    dimensions=args.dimensions, max_patterns=args.max_patterns,
                    associations=args.associations, thresholds=args.thresholds,
                    matcher_directory_requested=bool(args.matcher_directory),
                    scope="Changed pair/single grouping and addition association; exact supports/frames; counts screen only")
    (args.output/"protocol.json").write_text(json.dumps(protocol, indent=2)+"\n")
    began, results, hashes, baselines = time.monotonic(), [], set(), {}
    for h in args.dimensions:
        for pattern in selected_patterns(h-1, args.max_patterns):
            for threshold in args.thresholds:
                for association in args.associations:
                    local = ChangedCircuit(h-1, pattern, association, threshold)
                    local_check = local.verify()
                    retain_total(local)
                    circuit = SharedPointCircuit(h, local, point_order=aligned_points)
                    scalar, frames = circuit.verify(), circuit.verify_frames()
                    identifier = "h%d-g%s-t%d-%s" % (h, "".join(map(str, pattern)), threshold, association)
                    row = dict(id=identifier, h=h, grouping=pattern, threshold=threshold,
                               association=association, local=local_check, scalar=scalar, frames=frames)
                    digest = scalar["circuit_sha256"]
                    row["duplicate_exact_dag"] = digest in hashes
                    if not hashes or h not in baselines:
                        baselines[h] = scalar["roles"]
                    row["role_delta_from_first"] = scalar["roles"]-baselines[h]
                    if (args.export_dags or args.matcher_directory) and digest not in hashes:
                        name = identifier+".bin"
                        export(circuit, args.output/name)
                        row["dag_file"] = name
                        row["dag_sha256"] = hashlib.sha256((args.output/name).read_bytes()).hexdigest()
                        if args.matcher_directory:
                            dag = str((args.output/name).resolve())
                            def matched(name, second):
                                with (args.output/(identifier+"-"+name+".stderr")).open("w") as log:
                                    data = subprocess.check_output([str((args.matcher_directory/name).resolve()),
                                                                    dag, second], stderr=log, text=True)
                                return json.loads(data)
                            row["original_matching"] = matched("match_exported_dag", dag+".links")
                            row["positive_labels"] = positive_labels(dag)
                            row["positive_matching"] = matched("match_positive_dag", dag+".positive")
                            assert row["positive_matching"]["rank_sum"] == h*row["positive_matching"]["R"]+2*row["positive_matching"]["loss"]
                    hashes.add(digest)
                    results.append(row)
                    circuit.support_in.cache_clear()
                    (args.output/"results.json").write_text(json.dumps(results, indent=2)+"\n")
    summary = dict(status="exact_changed_dag_controls_pass", cases=len(results), distinct_dag_hashes=len(hashes),
                   improving_role_counts=sum(r["role_delta_from_first"] < 0 for r in results),
                   elapsed_seconds=time.monotonic()-began,
                   scope="No scalar-count-only headline claim; evaluate complete fixed-basis moments and changed denominator next")
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
