#!/usr/bin/env python3
"""Exact bounded factoring screens for all demanded fixed-pair star sums.

This only scores scalar subgraphs. It does not replace a certified global
graph or claim a transferred multiplication saving. Every demanded coefficient
is verified exactly after the greedy construction.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import heapq
import json
from pathlib import Path
import random
import time

from finite_block_search import GroupUnion, install_reference, make_block_class


def greedy(demands, seed=0, mode="canonical"):
    """Most frequent pair factoring with exact disjoint formal supports."""
    demands = sorted(demands)
    universe = 0
    for support in demands:
        universe |= support
    atoms = []
    while universe:
        atom = universe & -universe
        universe -= atom
        atoms.append(atom)
    supports = list(atoms)
    args = [None] * len(atoms)
    lookup = {s: i for i, s in enumerate(supports)}
    usage = [sum(1 << i for i, target in enumerate(demands) if atom & target) for atom in atoms]
    active = set(range(len(atoms)))
    heap = []
    rng = random.Random(seed)

    def push(a, b):
        if a > b:
            a, b = b, a
        score = (usage[a] & usage[b]).bit_count()
        if score < 2:
            return
        assert not supports[a] & supports[b]
        size = (supports[a] | supports[b]).bit_count()
        tie = -size if mode == "large" else size if mode == "small" else rng.randrange(1 << 30) if mode == "random" else 0
        heapq.heappush(heap, (-score, tie, a, b))

    for a in active:
        for b in range(a+1,len(atoms)):
            push(a,b)
    while heap:
        negative, tie, a, b = heapq.heappop(heap)
        mask = usage[a] & usage[b]
        score = mask.bit_count()
        if score < 2:
            continue
        if score != -negative:
            push(a,b)
            continue
        support = supports[a] | supports[b]
        node = lookup.get(support)
        if node is None:
            node = len(supports)
            lookup[support] = node
            supports.append(support)
            args.append((a,b))
            usage.append(0)
        assert node != a and node != b
        usage[a] ^= mask
        usage[b] ^= mask
        usage[node] |= mask
        for old in (a,b):
            if usage[old].bit_count() < 2:
                active.discard(old)
        for old in sorted(active):
            if old != node:
                push(old,node)
        active.add(node)

    def add(a,b):
        assert not supports[a] & supports[b]
        support = supports[a] | supports[b]
        node = lookup.get(support)
        if node is None:
            node = len(supports)
            lookup[support] = node
            supports.append(support)
            args.append((a,b))
        return node

    def total(parts):
        assert parts
        if len(parts)==1:
            return parts[0]
        middle = len(parts)//2
        return add(total(parts[:middle]),total(parts[middle:]))

    outputs = {}
    for i,target in enumerate(demands):
        parts = sorted([j for j,z in enumerate(usage) if z & (1<<i)], key=lambda j:(supports[j].bit_count(),supports[j]))
        outputs[target] = total(parts)
        assert supports[outputs[target]] == target
    needed = set()
    stack = list(outputs.values())
    while stack:
        node = stack.pop()
        if node in needed:
            continue
        needed.add(node)
        if args[node]:
            stack.extend(args[node])
    for node in sorted(needed):
        if args[node]:
            a,b=args[node]
            assert a<node and b<node
            assert not supports[a] & supports[b]
            assert supports[node] == supports[a] | supports[b]
    digest = sha256(json.dumps({"supports":[supports[n] for n in sorted(needed)],"args":[args[n] for n in sorted(needed)],"outputs":sorted(outputs.items())},separators=(",", ":")).encode()).hexdigest()
    return {
        "additions": sum(args[n] is not None for n in needed),
        "demands": len(demands),
        "seed": seed,
        "mode": mode,
        "all_outputs_exact": True,
        "all_additions_disjoint": True,
        "circuit_sha256": digest,
    }


def extract(c):
    demands = defaultdict(set)
    original = defaultdict(set)
    for node in c.active:
        if c.args[node] and c.core[node].bit_count() == 2:
            original[c.core[node]].add(node)
        if c.args[node] and c.core[node].bit_count() == 1:
            for child in c.args[node]:
                if c.core[child].bit_count() == 2:
                    demands[c.core[child]].add(c.union[child] & ~c.core[child])
    for node in c.outputs.values():
        if c.core[node].bit_count() == 2:
            demands[c.core[node]].add(c.union[node] & ~c.core[node])
    return demands, original


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",type=int,default=50)
    parser.add_argument("--seed",type=int,default=109)
    parser.add_argument("--mode",default="canonical")
    parser.add_argument("--pairs",default="0,2;10,20;46,48")
    parser.add_argument("--output",required=True)
    args = parser.parse_args()
    started_utc=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    install_reference(args.reference)
    cls=make_block_class()
    c=GroupUnion(args.h,lambda n:cls(n,(2,),4,0),"paired",args.seed)
    demands,original=extract(c)
    selected=sorted(demands) if args.pairs == "all" else [sum(1<<int(p) for p in pair.split(",")) for pair in args.pairs.split(";")]
    rows=[]
    for pair in selected:
        result=greedy(demands[pair],args.seed^pair,args.mode)
        result["pair"]=[i for i in range(args.h) if pair & (1<<i)]
        result["original_additions"]=len(original[pair])
        result["saving"]=len(original[pair])-result["additions"]
        rows.append(result)
    result={"started_utc":started_utc,"completed_utc":datetime.now(timezone.utc).isoformat(),"wall_seconds":time.monotonic()-start,"reference_commit":"bcd4ebde8692383539f8a48734e5fbf3a18a32c2","settings":vars(args),"rows":rows,"positive_savings":sum(max(0,r["saving"]) for r in rows),"total_saving":sum(r["saving"] for r in rows),"scope":"Exploratory exact star subcircuits; a whole-graph replacement and frame transfer are required before claiming an improved bound"}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k != "rows"},indent=2,sort_keys=True))
    for row in rows[:10]:
        print(json.dumps(row,sort_keys=True))


if __name__ == "__main__":
    main()
