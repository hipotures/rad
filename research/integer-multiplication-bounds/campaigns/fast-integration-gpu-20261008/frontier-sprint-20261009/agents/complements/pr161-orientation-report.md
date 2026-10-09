# Equal-rank physical orientations on PR161

No additional complete-profile improvement came from the equal-rank orientation
choices tested here. The public PR161 physical frames have no strict-interior
singleton interval. Among 15,450 connected equal-frame components, exactly one
has a strict-interior frame: operations 19964, 19965 and 19966, with lower rank
12, current rank 13 and upper rank 14. Its two-dimensional quotient has exactly
three one-dimensional subspaces. All three were explicitly constructed, checked
and evaluated; the control and two alternatives were different actual subspaces.

The unchanged scalar DAG, selected gauges, carrier pairs, compensation deadlines,
binary supplier and assembly are pinned to upstream PR161 commit
`d14e29157bc905be1ced0776dd893d0714013f3a`. Source:
<https://github.com/CrocSwap/integer-mult-bounds>. The paired-cube compiler uses
general Clifford frames; these are legal physical orientations, without importing
PR120's incompatible nondegenerate-projector restriction. The original physical
compiler credits eumemic and icekylinx, with PR130/131/124/143 mechanisms and
inherited Apache-2.0 attribution. New scripts were prepared with OpenAI assistance.

## Experiment and result

Three processes ran concurrently through a four-worker executor, with numerical
library pools limited to one. The inherited placement routine was used unchanged:
three full passes over connected equal-frame components, reversing traversal in
the second pass, choosing the improving legal endpoint by the complete transition
moment contribution at common trial `s=0.0005885669`. Exact containment follows
each complete trial. Each process took 9.89–10.22 seconds and about 368 MiB peak
RSS; Python was 3.14.4.

Every orientation starts with the identical complete histogram and accepts
2,883, 52 and 7 moves across the three passes. All three end with identical actual
frame files, SHA-256
`b13f4dfbd47605c903458c03309c4c49cbc8c14d7417705ede77b39be1daf5dc`.
They give discovery `H(s)=0.9999871322176292` and numerical complex root
`0.0005945608603695599`. These numbers describe the same endpoint descent gain
already found by the placement lane; they are neither a complement improvement
nor an accepted final exponent saving. The equality is stronger than a rounded
moment tie: all final frame bytes and histogram multiplicities are identical.

The later converged placement frames were independently checked and surveyed.
All 32,426 singleton intervals and 14,308 equal-frame component intervals are at
legal rank endpoints; none has strict-interior equal-rank freedom. This excludes
orientation changes in the tested component definitions at this checkpoint. It
does not exclude unequal-frame exchanges, different decompositions, altered
gauges, new pairs or a changed DAG.

## Exact checks and boundaries

The upstream physical compiler freshly rebuilt the complete paid histogram,
checked value spans, carrier-chain inclusion, pair handoffs and chronology,
target containment and read-order nesting, proper children and telescoping rank
mass. Its arbitrary dirty replay modulo `2^61-1` passed both seeds and rejected
flipped signed operations, omitted recipient reads and premature late reads.

A separate retained checker uses independent binary elimination and orthogonal
complement calculations. It checked 32,426 operation value containments and
85,340 carrier/pair edges, including reversed complemented inclusion and exact
transition-rank equality. Negative indices, noncanonical rows, invalid value
frames and omitted complements were rejected. Explicit `python3 -O` execution
was rejected before writing a result. Both the three-pass orientation result and
the five-pass converged placement result passed this check.

The baseline lane's exact local scalar audit was rerun on this lane's regenerated
graph and word. It checked 1,742,400 exact source/output coefficients,
17,214,120 dirty/output coefficients, 13,041 dirty slots, 54,234 literal events,
33,746 cleanup events and the signed inverse round trip. It rejected omitted
reads, bad signs, illegal indices and omitted cleanup. Inputs match the shared
PR161 baseline hashes; this is fresh arithmetic rather than a saved verdict.

Status remains `DISCOVERY`. These scoped exact checks do not constitute the
complete global reflected Clifford word audit or the all-size transfer theorem.
No rigorous moment enclosure or 47-constraint/seven-margin assembly acceptance
was performed by this lane. Those gates belong to the independently reviewed
placement winner. No final accepted kappa is claimed here.

## Reproduction and recovery

Use the exact source snapshot from the sprint's source manifest, not a mutable PR
head. Run from the sprint directory with standard-library Python. Use new output
paths; attempts are never overwritten. Source exports are regenerable:

```bash
python3 work/repos/pr161-d14e291/scripts/paired_cube_producer.py \
  --work-dir work/complements/reproduction-export \
  --output work/complements/reproduction-producer-receipt.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
python3 agents/complements/code/screen_physical_orientations.py \
  --source work/repos/pr161-d14e291 \
  --export work/complements/reproduction-export \
  --placement-code agents/placement/code/physical_search.py \
  --output work/complements/reproduction-orientations \
  --summary work/complements/reproduction-summary.json --workers 4 --passes 3
python3 agents/complements/code/check_physical_frames.py \
  --source work/repos/pr161-d14e291 \
  --export work/complements/reproduction-export \
  --placement-code agents/placement/code/physical_search.py \
  --frames work/complements/reproduction-orientations/orientation-0/frames.json \
  --output work/complements/reproduction-geometry.json
python3 agents/baseline/code/exact_aliased_core.py \
  --export work/complements/reproduction-export \
  --tree work/repos/pr161-d14e291 \
  --output work/complements/reproduction-exact-core.json
python3 agents/complements/code/survey_frame_intervals.py \
  --source work/repos/pr161-d14e291 \
  --export work/complements/reproduction-export \
  --placement-code agents/placement/code/physical_search.py \
  --output work/complements/reproduction-public-intervals.json
```

To reproduce the converged survey/review, additionally pass the retained placement
winner's frame file with `--frames` to the survey or geometry checker. The search,
geometry, exact scalar audit and converged interval survey above were actually
exercised on pinned regenerated inputs. The raw orientation files and final frame
lists are regenerable and remain in ignored `work/complements/`. Compact complete
profiles, all three quotient-line choices, artifact sizes/hashes and receipts are
retained under `results/`. The coordinator publishes completed text evidence by
the repository's gzip archival path. Raw external files are not claimed present
in a Git clone.

Recommended next step: continue placement's bounded unequal-frame exchanges or
change gauges/pairs. Repeating these same equal-rank component orientations has
no remaining information value at the tested public or converged checkpoints.
