#!/usr/bin/env python3
"""Independent product selector and fractional paired-face controls."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from random import Random
from time import perf_counter


def points(shape):
    return itertools.product(*(range(t) for t in shape))


def flatten(point, shape):
    index = 0
    for j,t in zip(point,shape):
        index = index*t+j
    return index


def source_bad_set(s,t,side,shift,radius):
    bad = set()
    for k in range(t//side):
        lo = s*(k*side+shift)//t
        hi = s*((k+1)*side+shift)//t
        for u in range(hi-lo):
            if u < radius or u >= hi-lo-radius:
                bad.add((lo+u)%s)
    return bad


def run_job(item):
    kind,seed = item
    started = perf_counter()
    rng = Random(seed)
    if kind.startswith("selector"):
        dimension = int(kind[-1])
        total = 0
        safe = 0
        core_records = 0
        source_stream_order = 0
        boundary_missing = 0
        for trial in range(24):
            targets = tuple(rng.choice((8,16)) for _ in range(dimension))
            sources = tuple(t-rng.randrange(1,max(2,t//4)) for t in targets)
            side = rng.choice((2,4,8))
            if side > min(targets):
                side = min(targets)
            input_values = list(points(targets))
            for shift in (0,side//2):
                output_records = []
                original_source_records = []
                source_start = tuple(s*shift//t for s,t in zip(sources,targets))
                for coarse in points(tuple(t//side for t in targets)):
                    origins = tuple(s*(k*side+shift)//t for s,t,k in zip(sources,targets,coarse))
                    lengths = tuple(s*((k+1)*side+shift)//t-a for s,t,k,a in zip(sources,targets,coarse,origins))
                    previous_index = -1
                    for local_source in points(lengths):
                        global_source = tuple(a+u for a,u in zip(origins,local_source))
                        q = tuple((2*t*j+s)//(2*s) for t,s,j in zip(targets,sources,global_source))
                        local_target = tuple(a-(k*side+shift) for a,k in zip(q,coarse))
                        core_records += 1
                        total += 1
                        if all(0<=j<side for j in local_target):
                            idx = flatten(local_target,(side,)*dimension)
                            # Product of increasing q maps preserves the packet's
                            # source order. One head scans each packet forward.
                            assert idx > previous_index
                            previous_index = idx
                            actual = input_values[flatten(tuple(a%t for a,t in zip(q,targets)),targets)]
                            expected = tuple(((2*t*(j%s)+s)//(2*s))%t for t,s,j in zip(targets,sources,global_source))
                            assert actual == expected
                            safe += 1
                            output_records.append((global_source,actual))
                        else:
                            assert any(u<2 or u>=length-2 for u,length in zip(local_source,lengths))
                            boundary_missing += 1
                        original_source_records.append(tuple((j-a)%s for j,a,s in zip(global_source,source_start,sources)))
                # Final inverse G and occupancy deletion restore the lexicographic
                # product source order; packets need not be lex-ordered as flat j.
                assert sorted(original_source_records) == list(points(sources))
                source_stream_order += len(original_source_records)
        result = {"kind":kind,"total_selector_requests":total,"safe_exact_outputs":safe,
                  "boundary_requests_excluded":boundary_missing,
                  "source_provenance_records":source_stream_order,
                  "sequential_packet_requests":core_records}
    else:
        cases = 0
        rows = []
        for dimension in (2,3,5,9):
            for side in (16,32,64):
                for radius in (1,2):
                    target = tuple(side*rng.randrange(3,8) for _ in range(dimension))
                    source = tuple(t-rng.randrange(1,max(2,t//12)) for t in target)
                    b0 = [source_bad_set(s,t,side,0,radius) for s,t in zip(source,target)]
                    b1 = [source_bad_set(s,t,side,side//2,radius) for s,t in zip(source,target)]
                    for s,t,x,y in zip(source,target,b0,b1):
                        assert s*side > (4*radius+2)*t
                        assert x.isdisjoint(y)
                        assert len(x) <= 2*radius*(t//side)
                        assert len(y) <= 2*radius*(t//side)
                    volume = math.prod(source)
                    exact = (volume-math.prod(s-len(x) for s,x in zip(source,b0))
                             -math.prod(s-len(y) for s,y in zip(source,b1))
                             +math.prod(s-len(x)-len(y) for s,x,y in zip(source,b0,b1)))
                    upper = sum(len(b0[i])*len(b1[j])*math.prod(source[k] for k in range(dimension)
                                if k not in (i,j)) for i in range(dimension) for j in range(dimension) if i!=j)
                    assert 0 <= exact <= upper
                    rows.append({"dimension":dimension,"side":side,"radius":radius,
                                 "source_shape":source,"target_shape":target,
                                 "bad_intersection_records":exact,"pair_union_bound_records":upper,
                                 "volume":volume})
                    cases += 1
        # Fixed half-grid source positions can overlap at too small a side.
        bad0 = source_bad_set(13,16,4,0,1)
        bad1 = source_bad_set(13,16,4,2,1)
        assert bad0 & bad1
        result = {"kind":kind,"cases":cases,"rows":rows,
                  "negative_too_short_fractional_side":{"source":13,"target":16,"side":4,
                                                         "radius":1,"same_axis_bad_both":sorted(bad0&bad1)}}
    result.update(seed=seed,seconds=perf_counter()-started)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    parser.add_argument("--workers",type=int,default=4)
    args = parser.parse_args()
    if not 1<=args.workers<=4:
        parser.error("at most four allocated slots")
    for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):
        os.environ[key]="1"
    out = Path(args.output)
    out.mkdir(parents=True,exist_ok=False)
    jobs = [(f"selector{d}",202610085000+d) for d in (1,2,3)]+[("fractional_faces",202610085004)]
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        results = list(executor.map(run_job,jobs))
    result = {"status":"joint selector and fractional paired-face controls passed",
              "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "workers":args.workers,"results":results,
              "limitations":["selectors test exact provenance and order, not inverse accuracy",
                             "coordinate gather and inverse are separately paid conditional interfaces"]}
    (out/"certificate.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"seconds":{x["kind"]:x["seconds"] for x in results}}))


if __name__=="__main__":
    main()
