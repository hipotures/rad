#!/usr/bin/env python3
"""Prepare a bounded general-h ORIGINAL-envelope I+J profiler from pinned PR40.

The generated third-party source retains its Apache-2.0 notices and lives only
in ignored execution storage. This authored exact transformation and receipt
are sufficient to recover it from the public pinned commit.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from math import comb, factorial, prod
import os
from pathlib import Path
import shlex
import subprocess


PIN = "43f59ff533598762cbc43a5e14af2bbbc76fabbd"
SOURCE = "research/copied-both-reversed/full_profiles23.cpp"


def crt_enclosure(h):
    # The original-envelope mask+rank-four Gram formulas are the upstream
    # crt_bounds.py input. Compute the same conservative bound at actual h.
    constants = {"core1": [12*(h+1), 12*h*h-10*h+38],
                 "core2": [3*(h*h-1), 12*h*h-34*h+64],
                 "line": [6*(h+1), 12*h-28]}
    dframe = max(row[0] for row in constants.values())
    bframe = max(row[1] for row in constants.values())
    ddiff, bdiff = dframe*dframe, 2*dframe*bframe
    bound = sum(comb(h, j)*factorial(j)*bdiff**j*ddiff**(4-j) for j in range(5))
    primes = []
    for exponent in (61, 31, 19, 17, 13):
        prime, lucas = 2**exponent-1, 4
        for _ in range(exponent-2):
            lucas = (lucas*lucas-2) % prime
        assert lucas == 0 and prime > dframe
        primes.append(prime)
    assert prod(primes) > bound
    return dict(h=h, frame_constants=constants, Dframe=dframe, Bframe=bframe,
                Ddifference=ddiff, Bdifference=bdiff, all_minor_numerator_bound=bound,
                primes=primes, prime_product=prod(primes),
                strict_gap=prod(primes)-bound)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True,
                    help="Fresh task-owned ignored build directory")
    ap.add_argument("--max-dimension", type=int, default=28)
    ap.add_argument("--compiler", default=os.environ.get("CXX", "c++"))
    ap.add_argument("--no-compile", action="store_true")
    args = ap.parse_args()
    if not 6 <= args.max_dimension <= 28:
        ap.error("This bounded preparation covers dimensions6..28, except h9")
    source = args.source_root.resolve()
    text = (source/SOURCE).read_text()
    assert text.count("assert(h==23)") == 2
    assert text.count(".h23_five_prime_profiles.json") == 1
    patched = text.replace("assert(h==23)", "assert(h>=6&&h<=%d&&h!=9)" % args.max_dimension)
    patched = patched.replace(".h23_five_prime_profiles.json", ".fixed_ij_profiles.json")
    patched = patched.replace("This adapted h23 run", "This bounded general-h run")
    patched = patched.replace("Uniform h23 rank-four bound", "Bounded general-h rank-four bound")
    enclosures = [crt_enclosure(h) for h in range(6, args.max_dimension+1) if h != 9]
    args.output.mkdir(parents=True, exist_ok=False)
    target = args.output/"fixed_ij_profiles.cpp"
    target.write_text(patched)
    binary = args.output/"fixed_ij_profiles"
    command = [*shlex.split(args.compiler), "-O3", "-std=c++17", "-I",
               str(source/"scripts/partial_swap"), str(target), "-o", str(binary)]
    receipt = dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
                   repository="rohanarun/integer-mult-bounds", pinned_commit=PIN,
                   base_source=SOURCE, base_sha256=hashlib.sha256((source/SOURCE).read_bytes()).hexdigest(),
                   generated_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                   wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   patch="Two dimension guards, output suffix and dimension comments; matrix/matching algorithms unchanged",
                   dimensions=[row["h"] for row in enclosures], crt_enclosures=enclosures,
                   command=command, compilation_requested=not args.no_compile,
                   scope="Original envelope frames and original deterministic matching only; enlarged positive labels are NOT profiled")
    if not args.no_compile:
        with (args.output/"compiler.stdout").open("w") as stdout, (args.output/"compiler.stderr").open("w") as stderr:
            subprocess.run(command, stdout=stdout, stderr=stderr, check=True)
        receipt["binary_sha256"] = hashlib.sha256(binary.read_bytes()).hexdigest()
    (args.output/"receipt.json").write_text(json.dumps(receipt, indent=2)+"\n")
    print(json.dumps(dict(status="prepared" if args.no_compile else "compiled",
                          covered_dimensions=receipt["dimensions"],
                          generated_source=str(target), binary=str(binary),
                          receipt=str(args.output/"receipt.json")), indent=2))


if __name__ == "__main__":
    main()
