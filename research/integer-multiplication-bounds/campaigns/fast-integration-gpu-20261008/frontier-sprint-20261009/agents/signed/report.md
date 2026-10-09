# Signed output synthesis on the PR161 paired-cube supplier

## Objective and input

Test whether a small exact signed producer change improves the complete paid
complex program, rather than its scalar role count alone. The immutable input
is `CrocSwap/integer-mult-bounds` PR161 head
`d14e29157bc905be1ced0776dd893d0714013f3a`, supplied by the coordinator.
This continues the existing frontier sprint. The full supplied 14-page review
and sprint prompt were read before execution; its historical PR120 score is
not used as the current target.

The pinned producer uses p=11/h=22, 1,320 cube ports, an h20 restricted
triple module, the direct pmod_C35 pair module, all-but-one(9), star centers
and coordinate-based matching eligibility. Its current output fusion is w02.
Source fingerprints and provenance are in `input-manifest.json`.

## Exact signed variants

For a cube I and port bits (b0,b1,b2), write F2 for the face2 signal,
E02 and E12 for the two edge signals, and sigma_i=2*b_i-1. The relevant
original contribution is

`(F2 + sigma_0*E02 + sigma_1*E12)/2`.

The unchanged control reads `(F2 + sigma_0*E02)/2` and
`sigma_1*E12/2`. The three changed constructions are:

| Variant | Actual signed grouping |
|---|---|
| w12 | `(F2 + sigma_1*E12)/2`, retaining the separate E02 read |
| s | `(F2 + sigma_0*E02 + sigma_1*E12)/2` |
| e02_e12 | `sigma_0*(E02 + sigma_0*sigma_1*E12)/2`, retaining the separate face2 read |

The graph builder checks disjoint original-source supports for every new
signed addition. The finite verifier independently recomputes every signed
scalar coefficient, rather than replacing signed arithmetic with XOR. The
four resulting graph binding hashes are distinct. The w02 control hash
equals the pinned source's binding exactly.

## Method and paid accounting

Both four-worker batches reconstruct each scalar DAG, the complete source
support spans, legal carrier-use graph, fresh deterministic maximum matching,
full backward intersections, physical signed operations and chronological
gauge selection. All four have 6,201 matching arcs and 2,970 rank18 gauges.
The source's common trial saving for gauge selection is 0.00065.

The first batch uses zero physical aliases and full backward-intersection
operation frames. This is a common fresh unaliased comparison; it is not
PR161's frozen descended/reused physical program. The second batch constructs
new physical inputs on every changed DAG: monotone frame shrink using full
value spans and neighboring transition costs, followed by a newly solved
maximum matching of legal chronological donors to late recipients. Neither
batch transplants PR161's frozen physical frames or alias pairs.

The exact finite checks cover 1,742,400 signed source/target coefficient
pairs, H+K+B=I, the local K inverse and source itinerary, conservative support
containment, full carrier intersections, physical signed operations, center
dependency closure, gauges, live role chains, source endpoints, actual target
read chronology and the complete positive transition recount. The only
change to the inherited finite verifier is replacing its final fixed
2,970/rank18 comparison with the actual selected count and rank histogram;
all preceding checks are retained. This adaptation is recorded verbatim in
the raw result.

The separate baseline checker propagates exact integer adjoints through the
literal reads, signed gates, source injections and signed inverse cleanup.
It checks all source output coefficients and arbitrary dirty responses,
using exact expansion of the center coordinates and local K contribution.
Omitted read, bad sign, illegal role index and omitted cleanup controls are
rejected. The physical checker also runs its inherited modular dirty replay
and controls. Both authored entry points were separately exercised with
`python3 -O` and rejected execution before creating any output.

Complete histograms include centers, copies, initial gauges, every frame
movement, source and target endpoints, and cleanup-compatible residuals.
The inherited finite-bridge expansion is recomputed from each DAG's c, R
and literal operation count, charging expanded old-value readouts, ordinary
centers, K, exact cleanup, routing and three stages. Its conservative scalar
guard holds for all eight runs. This does not independently prove uniform
stopped recursion, ordinary leaves, row reserves or the global analytic
assembly.

## Results

| Physical policy | Variant | Physical R / W | Maximum child | Numerical complex root |
|---|---|---:|---:|---:|
| Fresh unaliased | w02, w12, s, e02_e12 | 16,011 / 18,651 | 54 | 0.0005563735502966921 |
| Fresh descent and reuse | w02, w12, s | 13,041 / 15,681 | 20 | 0.0005825626899903179 |
| Fresh descent and reuse | e02_e12 | 13,041 / 15,681 | 20 | 0.0005825628670145232 |

Every row has m=66 and exact rank deficit 1,320. Every fresh physical
reconstruction moves 8,176 operation frames and creates 2,970 late aliases.
All four unaliased complete histograms are exactly identical. The s variant
adds 1,320 signed internal nodes and removes 1,320 root uses, leaving R and
the complete histogram unchanged. It increases literal M operations from
32,426 to 33,746, and the conservative local scalar group bound from
5,485,169,032,704 to 5,708,349,569,184.

After fresh physical reconstruction, w02, w12 and s still tie exactly.
Relative to w02, e02_e12 changes child multiplicities by
`{15:+3, 16:-3, 19:-3, 20:+3}`; total rank and child count remain unchanged.
The small improvement is local to this reconstruction and remains below the
pinned PR161 complex saving 5885669/10^10 and its final numeric milestone
5878747/10^10.

An independent rational interval implementation recounts every complete
physical inventory and certifies root enclosures:

- Fresh unaliased: `(556373550/10^12, 556373551/10^12)`.
- Fresh physical w02/w12/s: `(582562689/10^12, 582562690/10^12)`.
- Fresh physical e02_e12: `(582562867/10^12, 582562868/10^12)`.

All eight profiles have moment lower bounds strictly above one at both
pinned public trial values. For the best fresh physical e02_e12 profile,
the certified excess above one at 5885669/10^10 is greater than
0.0000131549407. Thus none can support that complex saving; approximate
roots are not used to establish this rejection. The rational method uses
40 positive atanh terms, degree-nine exponential expansion, explicit tails
and outward rounding to a 2^-180 grid.

The baseline utility changed concurrently after the first interval runs.
Its small moment kernel is therefore retained as `code/interval_moments.py`.
All function ASTs match the independent baseline implementation, and complete
interval reruns against the retained kernel produce exactly identical rational
endpoints. The larger evolving assembly utility is not needed for recovery of
this lane's negative moment result.

The final source was exercised again on a bounded fresh-physical w02 control;
all scientific fields reproduce exactly. The complete pinned-source gate
also rejects a deliberately corrupted source before execution or output
creation. These receipts are recorded in the compact result.

The first successful batch took 11.634 seconds with at most 354,452 KiB
resident memory per worker. The fresh physical batch took 27.326 seconds
with at most 434,852 KiB per worker. Four workers ran concurrently and
numerical-library thread settings were one. Two earlier attempts are
preserved: a harmless zero-count histogram representation mismatch, and
Python's integer-printing limit while serializing the conservative global
scalar guard. They are implementation failures, not mathematical failures;
both were corrected before complete successful reruns.

## Interpretation and limitations

Confidence is high in this scoped negative comparison: the graphs differ,
all exact local checks run, complete inventories are recounted, and strict
rational moment bounds reject the proposed target. The finding is not a
proof that every signed synthesis or reclamation strategy fails. It covers
these output groupings, common carrier/gauge policies, and one fresh greedy
frame/alias reconstruction. It does not compare them under the pinned
PR161 optimized physical inputs, whose applicability cannot be assumed
after changing the DAG.

Literal signed inverse and bank renaming follow the separate exact scalar
core audit. General Clifford frame reflection, the all-size sharing and
stopped transfer, ordinary leaf supplier, full 47+7 assembly and broader
repository checks remain independent obligations. No accepted final kappa,
unconditional theorem, formal verification or publication-ready result is
claimed for this lane. The coordinator owns live public comparison; this
report's numerical target is explicitly the pinned PR161 input.

The next useful E3 hypothesis should change shared-release topology,
matching/physical choices or signed dependencies before the final singleton
readouts. More output-only regrouping under this common policy is unlikely
to justify a larger sweep. Full raw states are regenerable from pinned
sources; the compact export includes all complete histograms, endpoints,
checks and timings. The coordinator must archive completed text evidence,
commit and push task-owned artifacts before reporting sprint completion.

## Attribution

The paired-channel graph, compiler and gauge interfaces originate with
icekylinx and the credited contributors in the pinned source. PR117 and the
restricted h20/pmod modules are by eumemic with Claude assistance. Physical
descent and late compensation follow eumemic's implementation, the general
Clifford frame lineage and jamesyc's compensated birth-cut reuse. Original
Apache-2.0 source and notices remain unchanged. The independent exact core
and rational arithmetic are by the separate RaD baseline lane. The signed
lane's driver, edge-pair grouping, fresh reconstruction and analysis were
prepared with OpenAI GPT-6.1 Sol assistance.
