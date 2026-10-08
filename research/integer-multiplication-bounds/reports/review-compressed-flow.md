# Exact controller-flow compression and measured bottleneck

Campaign clock: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.

Pruning unused controller-flow groups and ports preserves the exact optimum
and physical program for the tested h8, h12 and h50 envelope circuits.
The h50 sparse network shrinks from 2,291,542 to 35,581 vertices, but the
complete flow phase only changes from 4.3001 to 4.2273 seconds. The measured
bottleneck is source-use descriptions and admissible-link enumeration,
rather than the maximum-flow solve.

## Why pruning preserves the optimum

The original controller network has four directed layers:
source, previous-gate groups, outgoing use ports, incoming use ports, sink.
Every source-to-sink path contains exactly one admissible retained-controller
link from an outgoing to an incoming port. A gate group with no such outgoing
port, an outgoing port with no admissible successor, and an incoming port
with no admissible predecessor can belong to no complete path. Removing
those vertices and their incident edges leaves every feasible link selection
and each relevant unit capacity unchanged.

The [fresh optimizer](../code/review_compressed_flow.py) preserves the original
source-use enumeration and all admissible-link tests. It retains gate groups
and ports in their relative original order, then builds only this compressed
network. It independently checks same-source links, chronology, the
one-retained-input capacity, and exact frame inclusion. A residual-reachability
cut has capacity equal to the extracted selected-link count, independently
certifying the maximum within this fixed DAG and schedule. It makes no
global circuit-optimality claim.

| h50 network quantity | Original | Compressed |
|---|---:|---:|
| Vertices | 2,291,542 | 35,581 |
| Directed capacity edges | 2,247,254 | 50,093 |
| Admissible links | 14,514 | 14,514 |
| Selected links / minimum cut | 8,351 | 8,351 |
| Compiled physical roles | 485,237 | 485,237 |

The original `frame_reuse.optimize_chains` is untouched. The compressed
function is a separate source and is compatible with the existing compiler.
The included optimum remains that of the same topological controller-chain
ansatz, whose physical accounting and dirty restoration are separately
proved in [the controller review](review-frame-reuse.md).

## Complete finite validation

The [small controls](../runs/20261008T010350Z-review-compressed-flow/results/small.json)
use independently varying singleton positions at h8 and h12. Every selected
link and compiled hash is identical to the original optimizer. Both cases
pass the unchanged full scalar/frame/target verifiers, independently
reconstructed physical coefficients, dense rational envelope constraints,
and complete side dirty bases in both shear directions.

The [full h50 control](../runs/20261008T010350Z-review-compressed-flow/results/full50.json)
uses the independently promoted candidate
`abda739268bd6b9473e6b5d05fa63c4e7ca721783ecc2e4c3c1289635f261563`.
The verified local cache uses immutable snapshots of freshly checked local
circuits. The complete global scalar map is still checked; cache reuse is
limited to repeated local recipes within this fresh process.
Direct envelope labels were separately checked by the coordinator for all
454,388 logical frames and exact equality of every canonical Space field.

Old and compressed selected links, role count, and full compiled
serialization agree exactly with the immutable promoted program SHA256
`1c977516b156233960e65894a416fd1c2416fd9963827a019363f117c221033f`.
The benchmark additionally runs both unchanged full physical verifiers,
an independent disjoint-coefficient execution of the new program, and all
forward/reverse envelope transitions and exact designated targets. The
physical result is stronger than parity equality alone.

## Measurements and interpretation

Both full flow timers start with an empty inclusion cache and preloaded
NumPy/SciPy dependencies. On the same h50 candidate:

| Compressed phase | Seconds |
|---|---:|
| Source-use descriptions | 1.4467 |
| Admissible-link enumeration | 2.6534 |
| Sparse construction | 0.0258 |
| Maximum-flow solve | 0.0013 |
| Link and minimum-cut audit | 0.0428 |
| Complete compressed flow call | 4.2273 |

The original complete flow call takes 4.3001 seconds, so these measurements
do not establish a substantial throughput gain. They show that even a much
smaller flow instance leaves the dominant work unchanged. An envelope-only
inclusion predicate based on the already proved two mask equations is the
next discriminating optimization; generic source spans must retain their
stronger inclusion tests.

The h12 complete flow comparison is 0.01616 versus 0.01142 seconds. The
first h8 baseline included SciPy's initial import. Its original source and
successful result are retained, and its apparent speed ratio is excluded
from performance claims. The only source repair adds dependency preloading;
the optimizer and verifiers are identical. The full h50 timer uses that
repaired source and a fresh output path.

The full benchmark takes 60.91 seconds of measured work, or 62.47 seconds
in external `/usr/bin/time`, including both optimizer/physical checks and
the independent replay. It uses Python3.14.7, NumPy2.5.3, SciPy1.18.1, one
worker and one BLAS thread. Peak RSS is 3,076,420 KiB for the complete fresh
process. Because both implementations run in that process, this measurement
does not quantify their separate memory usage. No CPU timing or role-count
result from a different cache/workload condition is treated as equivalent.

## Reproduction

The [protocol](../runs/20261008T010350Z-review-compressed-flow/protocol.json)
records all source hashes, candidate identity, commands, versions, resource
allocation and the timing correction. The compressed optimizer is a valid
execution improvement with a small measured phase benefit; it introduces
no changed mathematical primitive or multiplication exponent.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  "$MATH_PY" -B research/integer-multiplication-bounds/code/review_compressed_flow.py \
  --reference "$REFERENCE" --h 8 12 --labels direct --output "$FRESH_SMALL"

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  "$MATH_PY" -B research/integer-multiplication-bounds/code/review_compressed_flow.py \
  --reference "$REFERENCE" --candidate "$CANDIDATE" \
  --labels direct --output "$FRESH_FULL"
```
