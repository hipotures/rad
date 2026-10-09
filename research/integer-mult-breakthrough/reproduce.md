# Reproduce the breakthrough research components

Use the canonical `hipotures/rad` repository on branch
`research/integer-mult-breakthrough-20261008`. On the CPU host, the isolated
worktree is `/home/user/DEV/rad-breakthrough`. The old CPU branch is read-only
reference material and must not be used for active development.

All commands below run from the worktree root. Standard-library Python 3.11+
and Git suffice for these retained checks; they need no network, dataset, GPU,
machine-local historical checkout or installed solver.

```sh
python3 tools/run_ci.py --group smoke --all
python3 tools/run_ci.py --group certificates --all
```

The registry records every effective local code/fixture dependency and claim
scope. The finite checks reject corrupted unitarity, incomplete moment mass,
signed work charges, zero potentials, unpaid normalization and degree capacity.
CI verifies those controls, not a multiplication algorithm or larger kappa.

To regenerate the complete initial discriminators, choose a NEW ignored or
external path for each output. Do not replace prior attempts.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/unitary_dyadic.py --self-test
python3 -B research/integer-mult-breakthrough/code/obstructions/unitary_dyadic.py --workers 4 --max-row-power 7 --max-butterfly-power 5 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/unitary/results.json
python3 -B research/integer-mult-breakthrough/code/obstructions/wider_unitary.py
python3 -B research/integer-mult-breakthrough/code/transfers/coupled_moments.py --workers 4 --cases 96 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/mixing/results.json
python3 -B research/integer-mult-breakthrough/code/transfers/deferred_normalization.py --workers 4 --cases 96 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/normalization/results.json
```

Expected outcomes: exhaustive dyadic row classifications and exact finite
Gram matrices pass; complete frozen moments at saving 1e-4 remain greater
than one; finite carry interfaces change the spectrum while the paid
redundant/padding controls recover their stated integer values. Timing and
interpreter strings vary and are not scientific claims.

The coordinator reviewed the positive-matrix minimum-potential proof and
independently ran the bounded transfer checks. A separate synthesis agent
reviewed the dyadic row descent and unitary scope. The raw initial four-worker
evidence is packed into this topic's evidence namespaces without altering
originals. Run protocols, compact summaries and source hashes distinguish
retained finite evidence from analytical assumptions.

## Additional structural components

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_complex.py
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_certificates.py
python3 -B research/integer-mult-breakthrough/code/obstructions/odd_weight_kernels.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/odd/results.json
python3 -B research/integer-mult-breakthrough/code/transfers/row_budget_recursion.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/row-budget/results.json
python3 -B research/integer-mult-breakthrough/code/transfers/copied_center_review.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/copied-review/results.json
python3 -B research/integer-mult-breakthrough/code/synthesis/shared_twist_factorization.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/shared-twist/results
```

The complex controls cover exact moments, scalar output partitions, corruption
tests, hypothetical role caps and restricted frame obstructions. Synthesis
replays the complete auxiliary source/sink/dirty maps and a necessary frozen
native ceiling. The shared scatter checks actual odd-field address maps on
arbitrary dirty payload functions; its cost comparison is between two named
auxiliary words. The row-budget check is a declared toy recurrence. Neither
the toy nor the auxiliary components establish an improved native network.

Detailed discovery commands and failed repairs are in each retained run report.
The optional XOR-SMT experiments require the wheel/version/hash in
`configs/synthesis/solver-provenance.json` and requirements file. Their retained
UNKNOWN results are inconclusive; solver timeouts and exact timings need not
recur on a different host. SMT2 input text is regenerable from retained source
and is omitted from the four-format gzip publication. Solver binaries and
environments are excluded from Git. Ordinary bounded CI needs no solver.

The coordinator reran the complex and synthesis verifiers, reviewed the static
intertwiner and dynamic scatter algebra, and checked the row-budget and
copied-center controls. Track C independently reconstructs the serialized
weighted DAG without importing its producer. Internal independent analysis
is not formal verification or external peer review.

The independently contributed [Lean package](formal/README.md) has its own
pinned prerequisites, verifier and path-filtered workflow. It formalizes only
the positive-matrix minimum-coordinate lemma, finite compositions and named
boundary counterexamples. Its workflow passed on remote commit `1576511c`;
this is separate from the finite Python root/component checks above. Follow
its own instructions to reproduce that formal scope.

The full mathematical motivation and limitations are in the linked reports.
Primary literature and framework provenance are pinned in input-manifest.json;
no downloaded source modifications are required to run these new checks.

## General phases, full Clifford components and cancellation transforms

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_quadratic_rank_interface.py
python3 -B research/integer-mult-breakthrough/code/complex/test_lagrangian_phase_interface.py
python3 -B research/integer-mult-breakthrough/code/transfers/general_phase_review.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/packed_translation.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/lagrangian_component_review.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/obstructions/lagrangian_exchange.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/test_trimmed_side_transform.py
python3 -B research/integer-mult-breakthrough/code/obstructions/trimmed_side_transform.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/trimmed/results.json
```

General phase controls retain affine radical translations and nonalternating
odd-rank C children. The four-incidence shear has exact paid ranks 1,1,1,2,
total 5, against graph minimum 6; independent review reconstructs all phases and
complete payloads. These ranks do not include a surrounding motif's endpoint
establishment. Paid translation timing is conditional on the stated streaming
primitives, not finite array runtime. The trimmed side circuit has complete
scalar matrix checks and exact SSA counts, with zeros/aliasing explicitly outside
the arbitrary-dirty model. It has no native child histogram yet.

Each new run report pins its full discovery command and source hashes.
[Global helper search reproduction](reports/synthesis/global-helper-rank-search.md)
includes the complete GF2/F3/F9 cases and retained unquotiented F9 state-limit
UNKNOWNs. [Independent graph completion](reports/synthesis/lagrangian-chart-boundary.md)
and the [incidence-wrapper report](reports/synthesis/incidence-wrapper-chronology-negative.md)
give their separate exact models. No new code requires an external solver.

The coordinator reran bounded phase, translation, four-port and exchange checks,
reviewed the literal common-frame cancellation and free-row-unit quotient, and
ran the trimmed transform and its actual corrupted-DAG controls. Internal
agent review is not external peer review or a formal proof package.

## Degenerate branching, complete cancellation words and charged guards

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_degenerate_frames.py
python3 -B research/integer-mult-breakthrough/code/transfers/branching_component_review.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/endpoint_guard_literal.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/obstructions/endpoint_guard_counterexamples.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_word_frames.py
```

Seven complex tests and an independent no-producer-import review bind the
degenerate three-helper component, every dirty/source/sink anchor, all fourteen
phase edges, auxiliary rank 12 and external rank 12. Its graph-chart comparison
is auxiliary minimum 14. This is a complete local component, not a native motif.
The whole-word verifier independently recounts chronological transitions and
checks exact small binary cuts; the many-label discovery searches remain
heuristic negative results. The monotone trimmed telescope is an optimistic
endpoint/support ledger rather than a literal four-pass Gaussian histogram.

Guard controls distinguish exact returned endpoints from charged local prefixes
and literal internal registers. The proposed O(e log e) induction has independent
analytical reviews under its listed assumptions; no fast native time/row contract
is supplied by the deliberately inefficient precision stress word.

All fourth-checkpoint run protocols identify source closures and original local
paths. Complete JSON/log text is archived under `evidence/20261008T230948Z-*`.
Large readable receipts are summaries with exact omission lists, original byte
sizes and hashes; their full frame words and cancellation frontiers remain in
complete gzip copies in the clone. No original evidence was modified or deleted.
Decompress a listed gzip to a fresh location to recover the exact original text,
or replay the report command with a fresh output directory.

## Nonlinear blocks, tensor controls and routing-aware transfer

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_nonlinear_blocks.py
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_tensor_chronologies.py
python3 -B research/integer-mult-breakthrough/code/transfers/routing_budget_transfer.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/obstructions/geodesic_transport.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/central_minrank_controls.py --workers 1 --bounded
```

These five checks use only retained source and Python's standard library. The
nonlinear conclusion concerns a conditional asymptotic local tensor moment; it
does not order finite-column moments. Literal tensor controls include arbitrary
dirty columns and the previously rejected inverse-scale ordering. The stopped
recurrence retains the fixed routing chunk, complete rows and every leaf.
Geodesic/minrank checks distinguish exact finite controls from independently
reviewed analytical implications and field/representation restrictions.

Historical failures are reconstructable from the retained source and patches.
The coordinator applied the tensor failure patch in an isolated copy, matched
the original SHA256 and reran its complete-column failure. Reversing the routing
guard patch likewise matched the initial source hash. This optional historical
source recovery uses GNU patch in addition to Python; all registered bounded
checks remain standard-library-only. The checkpoint validation retains exact
patch hashes, recovered source hashes and the observed exception log.

Complete fifth-checkpoint text evidence is published in its recorded gzip
namespaces. Large convex Toffoli rows have compact summaries with exact original
hashes and omission lists. Downloaded primary PDFs remain ignored and have
versioned URLs, byte sizes, hashes and recovery entries. All original attempts,
including rejected numeric guards and failed operator words, are unchanged.

## Sixth-checkpoint bounded components

These source/fixture checks need only Python's standard library:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_center_null_basis.py
python3 -B research/integer-mult-breakthrough/code/complex/test_center_native_leverage.py
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_convolution_gauges.py
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_field_cyclic.py
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_center_ports.py
python3 -B research/integer-mult-breakthrough/code/transfers/monotone_split_tapes.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/field_cyclic_cost_review.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/center_basis_review.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/obstructions/verify_singer_routes.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/coherent_release_bound.py --workers 1 --bounded
```

Each experiment protocol records the full four-worker attempt, exact source
identities, parameters and original output locations. The solver-dependent
padded-convolution discovery additionally uses the pinned existing
`configs/synthesis/solver-requirements.txt`; its bounded witness replay above
needs no solver. Timed-out solver cases are UNKNOWN. Historical failed source
versions are recoverable with the retained patches and GNU patch; that optional
recovery prerequisite is not required by the mathematical CI checks.

Large original Smith operation rows and center-port word/frame data are
retained unchanged locally and published as complete gzip evidence. Newly
named summaries identify omitted fields, hashes and complete recovery copies.
Execution namespace names, including documented manually selected future
names, are recovery paths; protocol clock fields supply actual run times.
The hypothetical capacity tests and scoped routing/release proofs establish
only their named contracts, without a larger multiplication exponent.

## Seventh-checkpoint bounded components

These checks require Python's standard library:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_point_center_basis.py
python3 -B research/integer-mult-breakthrough/code/complex/test_conditioned_frames.py
python3 -B research/integer-mult-breakthrough/code/complex/test_total_centers.py
python3 -B research/integer-mult-breakthrough/code/complex/test_triple_total_centers.py
python3 -B research/integer-mult-breakthrough/code/complex/wht_dirty_echo_review.py --workers 1
python3 -B research/integer-mult-breakthrough/code/transfers/odd_weight_spectrum.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/side_kernel_completion.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/conditioned_frame_review.py --workers 1
python3 -B research/integer-mult-breakthrough/code/transfers/total_center_review.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/obstructions/wht_arithmetic_dirty_echo.py --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/full_domain_lookup_boundary.py --bounded
```

Two exact elimination checks additionally need a C++17 compiler, GNU patch
and OpenMP. Generated sources, binaries and factor inputs are temporary:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_echo_elimination.py
python3 -B research/integer-mult-breakthrough/code/obstructions/verify_entangled_release.py
```

All 60 registered checks passed locally in three populated groups. Run each
with its own fresh evidence directory:

```sh
python3 tools/run_ci.py --group repository --all --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/ci-repository
python3 tools/run_ci.py --group smoke --all --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/ci-smoke
python3 tools/run_ci.py --group certificates --all --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/ci-certificates
```

The selectable full group currently has no entries; it does not combine groups.
Each group report retains command logs and effective input hashes. The larger
full 135-frame experiment needs about 5.35 GB of factor payload plus reserve;
bounded CI binds its input, patch, preflight and witness without rerunning that
minimum. The two-copy 67-frame case is small enough for complete replay.
Optional SMT discoveries use the existing pinned solver setup; these bounded
checks do not import it. UNKNOWN solver cases remain inconclusive.

Completed text evidence is retained in seventh-checkpoint gzip namespaces.
The readable coupled-kernel summary identifies omitted operation arrays,
original hash and exact recovery copy. Downloaded primary PDFs are excluded
and recoverable at pinned version URLs in the source configs. Retained patches
reconstruct historical own-source failures; that optional recovery is separate
from mathematical CI. Exact starts are explicitly unavailable where manual
aliases had no recorded launch clock. All original evidence bytes are unchanged.

These results provide scalar constructions, conditional analytical lemmas,
finite certificates and structural negatives. No complete new multiplier or
kappa>=10^-4 is certified. Native center/side integration continues on fresh
paths outside this publication.

## Closed components, actual frames and birth-reuse input

The eighth checkpoint adds 20 checks to the existing registry, for 80 total.
These commands exercise bounded actual operators and compact arithmetic:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_closed_center_release.py
python3 -B research/integer-mult-breakthrough/code/complex/verify_closed_center_interfaces.py
python3 -B research/integer-mult-breakthrough/code/complex/verify_phase_frame_primitives.py
python3 -B research/integer-mult-breakthrough/code/complex/frame_background_orientation.py
python3 -B research/integer-mult-breakthrough/code/transfers/closed_center_review.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/ballot_center_completion.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/ballot_bier_words.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/encoding_slack.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/pr127_transfer_review.py --workers 1
python3 -B research/integer-mult-breakthrough/code/obstructions/materialized_side_release_bound.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/geodesic_side_capacity.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/canonical_framed_shear_boundary.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_component_words.py --case two-axis
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_component_words.py --case native-exchanges
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_component_words.py --case closed-side
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_component_words.py --case geodesic-side
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_component_words.py --case canonical-geodesic
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_component_words.py --case tensor-preflight
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_component_words.py --case geodesic-moment
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_component_words.py --case source-cycle
```

The central component adds Kx, not the complete identity. Generic geodesic
replay checks all384 h4/f1 physical columns and rejects both omitted cleanup
and free generic gauge changes. The smaller coordinate side is a separate
component. Two-axis controls check complete kernels, child matrices and full
spectator routers. The source-cycle bounded check replays scalar columns and
the stored witness; it does not recompute the expensive finite minimum. Exact
conditional moments never certify the missing canonical primitive or transfer.

External PR127 reproduction is separate from these standard-library checks.
Follow [its run report](runs/20261009T015802Z-pr127-reproduction/report.md) and
[source pins](configs/obstructions/pr127-source-pins.json) to acquire the
unchanged downloadable checkout at the exact commit. The independent compact
arithmetic command above requires only the retained fixture, not that checkout.
The [scope review](reports/transfers/pr127-transfer-independent-review.md)
distinguishes three moments, aggregate rebilling, scalar costs and seven margins
from all47 constraints and the inherited native assumptions.

An early six-case coordinator wrapper was extended to two additional cases.
The initial source hash is recoverable through the exact
[coverage extension patch](fixtures/synthesis/component-word-coverage-extension.patch)
and archived source snapshot. Early receipts remain unchanged. Registered CI
uses the extended source. The full orthogonal Gauss-block trace likewise has
an unchanged gzip copy and a separately named compact publication summary;
neither original was overwritten to satisfy publication limits.
