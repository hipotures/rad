# Followup: independent promotion of the explicit clone witness

The h51 construction with 1,431 explicit clones and 500,703 auxiliary
roles now has both the frozen
[all-size capacity, frame, invocation and guard proof](review-clone-capacities.md)
and the completed independent full changed-DAG audit. This followup
records acceptance without editing the earlier proof or its input bytes.

The full root-owned audit is
[run20261008T051931Z-review-explicit-clone-repair](../runs/20261008T051931Z-review-explicit-clone-repair/protocol.json),
with [certificate](../runs/20261008T051931Z-review-explicit-clone-repair/results/certificate.json)
SHA256 `42957dbe7471fa007bc0ab889e1f588b82267e8012ec47cd84883828c5e0662c`.
It allocates the changed DAG itself from the explicit 1,431-edit artifact
and consumes all 36,312 saved links. It imports no clone producer and
replays no accepted baseline physical program.

The audited identity is
`48ed20b27a51199045b4518e8a02546aa35b7fd4c2d203f7b9c215eb2f891541`.
The physical compiled hash is
`1c0f74cda784fe0366a1f4346f1acf1477faa2a234a9601f8f0678d60bfa30d8`.
The changed graph has 474,540 additions, 62,475 designated partial
outputs, and 36,312 links; `R=c+q-links=500703`. The audit verifies its
70,471,800 nonzero partial-output coefficients and complete intended
scalar maps, every physical addition/output, all 495,365 logical frames,
2,899,566 physical frame transitions, input lines, output labels, target
orthogonality and both forward/reverse-complement inclusion directions.
The actual plan passes separate gate capacity and chronology checks.

New h12 controls exercise all 4,239 complete source, target, central and
dirty auxiliary basis vectors in each orientation. They also verify
the complete side invocation on 4,227 basis vectors, with dense rational
controls for all 3,317 distinct small envelopes. These are whole
invocation tests; the central registers are included in the 4,239 figure.

The full certificate's W, s, N, L, D and literal operation guard agree
with the separately frozen independent accounting. In particular,
`W=452397413413750`, `D=2263379181875`, and the exact slack in
`64(W+m+1)^3>2GW²+4s+4W+4` is
`3670794861655268745434778017984148373367443208`.
The numerical guard of the separate complex primitive is unchanged.

The [uncapped audit](../runs/20261008T0533Z-review-uncapped-middle/results/certificate.json)
additionally compares these complete finite fields against the earlier
independent clone proof, pins both digests, and checks both dirty
orientation fields. This thin comparison rebuilds no graph.

The initial full run051433 completed the changed coefficient/frame
checks but then failed on a redundant missing `v` schema field. Its
source/log evidence is retained. The repair derives v from h and actual
inputs; it makes no weaker mathematical assertions. The successful
full review took 106.99s and 3513216KiB peak RSS.

Acceptance is for this feasible explicit plan and the retained
conditional transfer. There is no optimizer-optimality claim, no giant
new factor table or explicit shared finite prime, and no new final
multiplication kappa inferred solely from the role count.
