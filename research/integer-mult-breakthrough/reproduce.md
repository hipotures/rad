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

## Target pivots, selected scans and general order rank

The nineteenth checkpoint adds six bounded checks, for 183 total:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/verify_cap_pivot_and_interleaving.py
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_three_scan_components.py --component selected
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_three_scan_components.py --component flux
python3 -B research/integer-mult-breakthrough/code/transfers/activity_self_bootstrap_packets.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/scan_order_cut_rank.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/boolean_jordan_basis_cost.py --workers 1 --bounded
```

Expected PASS receipts are scoped finite controls. The local pivot word
retains every dirty and ancestor column; the complete fixed-label three-scan
controls preserve the original failed simple sign lift and the later exact
dyadic lift. The two selected/flux commands eagerly import the same nine-file
closure; publish both packages together as their inventories specify. Their
complex all-size selected-order proof is independently reviewed, rather than
inferred from the F3 real-unit screen. General cut controls independently
check complete integer factorizations and unit minors, including characteristic
two. The Jordan source credits the pinned classical primary paper and pays
the two-way sequential basis ledger separately from uncharged scalar gates.

Full four-worker commands use fresh paths in their scientific reports. The
complete 1,053,367-byte general-order certificate stays unchanged in a whole
gzip copy; its readable summary omits and identifies individual order rows.
Source-only analytical reviews are labeled separately from new measurements.
The coupling note keeps the available ordinary atom distinct from the new
assembly output and accounts for every tensor packet's complete volume.

Complete run text, validation, selected public metadata and recovery material
are indexed by
[nineteenth recovery metadata](configs/recovery/checkpoint-nineteen-artifacts.json).
The downloaded main commit patch response is excluded; its pinned semantic
metadata and complete PR body are retained. All prior evidence shards remain.
These checks do not prove a faster native zeta supplier or multiplier exponent.

## Dirty cap banks, general flags and irregular routes

The eighteenth checkpoint adds seven standard-library checks, for 177 total.
Run the bounded commands from the worktree root:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/paired_cap_dirty_completion.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/paired_cap_fanout_flags.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_idempotent_flags.py
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_ordered_scan_products.py
python3 -B research/integer-mult-breakthrough/code/transfers/irregular_activity_router.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/verify_irregular_route_shapes.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/paired_cube_cap_review.py --workers 1 --bounded
```

Expected PASS receipts bind retained dirty auxiliary banks and true scalar
inverses, actual fanout flags, arbitrary image/kernel idempotent completion,
two-scan support restrictions, and literal general-width routing with all
12 guards. The independent cap review reconstructs small coefficients and
supports without importing the producer; its separate review of gate words
is analytical and does not rerun complete earlier words or every historical
failure. These checks do not supply a fast zeta primitive, native tape
implementation, arbitrary cancellation lower bound, or larger kappa.

Full four-worker commands and fresh output paths are recorded in the three
scientific reports and frozen source inventories. The two original complete
fixed-label scan certificates are 972,253 and 964,037 bytes. Readable summaries
state their omissions; the complete certificates remain unchanged in gzip
copies, without splitting. The routing inventory preserves two failed
negative-control attempts. Its ordered recovery patches reproduce historical
source versions only in an isolated mirror: first apply the adversarial
recovery patch to the accepted source, then the negative recovery patch to
that intermediate source. Never apply them to the active worktree. The
[control recovery run](runs/20261009T101623Z-irregular-control-recovery/report.md)
reconstructs both exact hashes and reproduces both rejected controls before
checking the accepted full f4/f5/f6/f7, K10 route.

All 177 local checks passed on 335 unchanged effective inputs. Complete
original run text, validation reports, control-recovery outputs and selected
public API metadata are indexed by
[eighteenth recovery metadata](configs/recovery/checkpoint-eighteen-artifacts.json).
Downloaded third-party source remains outside these archives and is identified
by obtainable pinned URLs and hashes. All preceding recovery shards and the
[historical index](reports/checkpoint-index-through-seventeen.md) remain intact.

## Maximum endpoints, paired-five words and cap channels

The seventeenth checkpoint adds eight standard-library checks, for 170 total.
From the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/paired_five_cube_discriminator.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/paired_five_complete_baseline.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/paired_cube_low_channel_boundary.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_rational_frame_block.py
python3 -B research/integer-mult-breakthrough/code/transfers/rational_completion_modular_review.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/rational_chain_candidate_review.py
python3 -B research/integer-mult-breakthrough/code/obstructions/paired_cube_cap_channels.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/paired_cube_cap_channel_census.py --workers 1 --bounded
```

Expected results are exact PASS receipts, including explicit scope-limited
negative conclusions and adverse controls. The maximum endpoint changes one
actual rational operation cut and all three block copies: twelve children
become nine and rank remains 66 locally. Its complete profile rank remains
1,934,000 with deficit 1,936. Neither this finite improvement nor the all-size
star inverse proves an improved native bit supplier or multiplier exponent.
The independent modular reviewer uses good-prime-power matrices as controls,
not indiscriminate finite-ring completion or a field-only sampler.

Removing `--bounded` regenerates the complete paired-five and cap experiments;
the scientific reports specify their four-worker commands and exact cases.
Always choose a new output path. All original runs and raw text have complete
gzip copies indexed by
[seventeenth recovery metadata](configs/recovery/checkpoint-seventeen-artifacts.json).
Sources and fixtures remain readable. The connected-block discovery inventory
records its heuristic shape filter and tested subset; its single positive
candidate is not a global optimum. No frozen external package is required to
run these bounded checks.

## Independent PR163 reviews and rational frame completion

The sixteenth checkpoint adds seven checks, bringing the registry to 162.
All bounded checks require only standard-library Python and retained source
or small fixtures. From the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/selected_activity_cylinders.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/pr163_complex_frame_audit.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_rational_frame_completion.py
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_pr163_frame_contract.py
python3 -B research/integer-mult-breakthrough/code/transfers/activity_native_tau_budget.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/pr163_balanced_transfer_review.py --workers 1
python3 -B research/integer-mult-breakthrough/code/obstructions/odd_cube_clifford_boundary.py --workers 1 --bounded
```

Expected results are exact PASS controls and retained domain/chronology
rejections. These do not rerun the full external author package or establish
native/all-size hypotheses. Full independent complex/bit audit commands and
immutable external acquisition instructions are in their scientific reports.
The [author replay record](reports/obstructions/pr163-reproduction-and-scope.md)
binds its unchanged 1,678-file closure, exact revision and excluded full gate.
The newer credit-only PR head is distinct from the replayed revision.

The main artifact manifest links [chronological sixteenth recovery metadata](configs/recovery/checkpoint-sixteen-artifacts.json). Complete gzip copies retain all original rows; no payload is
split to meet a storage limit. The full143-check report has an adjacent
readable storage note binding its unchanged bytes and original hash.

[Selected cylinder inventory](configs/complex/selected-activity-milestone.json),
[complex audit inventory](configs/complex/pr163-complex-review-milestone.json),
[rational/bit inventory](configs/synthesis/rational-frame-review-publication-manifest.json)
and [transfer inventory](configs/transfers/milestone-sixteen-freeze.json)
bind complete original evidence, inputs and bounded closures. The odd-cube
producer takes a fresh DIRECTORY as `--output`; the two bounded rational
verifiers accept fresh FILE paths. Use a unique path for every attempt.

The failed arithmetic reviewer is recoverable from its current-to-prior
patch in an isolated directory outside Git ancestry. Preserve
`code/transfers/` and `fixtures/transfers/` beneath that temporary topic,
then apply `git apply --no-index --unsafe-paths -p1` from its code directory.
The recovered source must have SHA-256
`b16ab31dffc61c15b12e9ec7510741132897c463e9fd62b94eb28510bcaf81b7`.
Its expected 4300-digit parser failure was independently replayed; do not
apply this historical patch to the live repaired source.

## Complete activity, routing and nonunit numerical guards

The fifteenth checkpoint registers seven new checks, for 155 total. They
need only standard-library Python and Git. From the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/prefix_activity_shape.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/activity_width_grouping_tapes.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_benes_control_fibers.py --component all
python3 -B research/integer-mult-breakthrough/code/obstructions/activity_gate_moment.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/interleaved_local_norms.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/disk_safe_rounding.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/geometric_endpoint_guards.py --workers 1 --small
```

Expected outcomes are exact finite PASS controls and retained corruption
rejections. The grouping consumer counts actual finite-alphabet tape
operations. Its initial prefix route is excluded. Benes addresses and
Gaussian fibers have complete scoped controls; their native time and
recursive supplier remain conditional. The moment checker does not
supply an eleven-gate circuit. The two numerical producers check their
declared domain, whole-bank, inverse, fixed-grid and rounding premises.

Full four-worker attempts and exact source/seed closures are listed in
[the activity inventory](configs/complex/activity-shape-milestone.json),
[the Benes inventory](configs/synthesis/benes-control-fiber-publication-manifest.json)
and [the transfer inventory](configs/transfers/milestone-fifteen-freeze.json).
Use a fresh ignored output for every attempt. The two numerical producers
take a JSON FILE as `--output`; the activity/interleaving and Benes sources
take a new DIRECTORY. Source-only reviews are not additional experimental
replays. The coordinator separately invoked producer numerical APIs.

The historical geometric report can be recovered with its current-to-prior
patch in a fresh directory outside any repository ancestry. Copy the
current report there under `geometric-nonunit-endpoint-guards.md`, then run
`git apply --no-index --unsafe-paths -p0` with the absolute path to
`fixtures/transfers/geometric-local-factor-contract.patch`. The recovered
SHA-256 must be `8ef7c23dfe82b93dd27bf4d3303ce592a6bcf97a995eb10e73e891c76fc85456`.
Never apply the historical patch to the live accepted report.

Complete scalar rows and the full 136-check certificate report are retained
unchanged as gzip. Their adjacent storage notes bind original byte counts
and hashes. Decompress those complete copies to recover the plain originals;
no row subset is substituted. Publication metadata records and preserves
the archive-count helper failures and their repaired complete-byte review.

## Product bases, rounding and cancellation scope

The fourteenth checkpoint adds eight bounded checks, for 148 in total.
All registered checks require only standard-library Python. Run the new
components independently from the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/product_slice_wire_floor.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/approximate_product_slice_floor.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/weighted_union_product_basis.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_zeta_row_controls_v2.py
python3 -B research/integer-mult-breakthrough/code/transfers/unitary_rounding_depth.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/obstructions/verify_nonlinear_rounding.py
python3 -B research/integer-mult-breakthrough/code/obstructions/zeta_dependency_ancestry.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/rounded_product_recovery.py --workers 1 --bounded
```

Expected outcomes are complete finite PASS controls. The nonlinear adapter
replays the producer API; it is not an independent implementation. The
separate product and ancestry reviews are analytical/source reviews.
Full discovery runs use four workers and are identified in the retained
protocols and the [product](configs/complex/product-basis-milestone.json)
and [row-search](configs/synthesis/zeta-row-publication-manifest-v2.json)
publication manifests. Solver discovery additionally requires the pinned
dependencies in `configs/synthesis/zeta-row-search-dependencies.json`;
no solver is needed for the retained bounded row verifier.

The validation run's `results/historical-recovery.json` binds three exact
historical source reconstructions. Apply each patch in a fresh isolated
tree with its recorded relative layout and direction. The weighted-union
and initial v2 instrumentation failures must fail with the retained
messages. The original rounding source has a weaker projection control
and is retained as historical evidence, not the repaired control.

## Row pools, complete products and independent zeta synthesis

The thirteenth checkpoint adds 16 bounded checks, bringing the registry to
140. These use only standard-library Python; the full registered verification
commands above remain sufficient. To run the new scientific components alone:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/partial_kernel_product_algebra.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/dyadic_quotient_channel_capacity.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/partial_product_prefix_audit.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/partial_polynomial_product_packets.py --workers 1 --bounded
for case_name in scan-order scan-bit zeta matching origin; do
  python3 -B research/integer-mult-breakthrough/code/synthesis/verify_extended_zeta_components.py --case "$case_name"
done
python3 -B research/integer-mult-breakthrough/code/transfers/bilinear_ring_packing.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/power_two_ring_capacity.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/xor_compatible_packing.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/fused_packet_envelope.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/obstructions/zeta_rectangle_rebalancing.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/retired_guard_row_pool.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/aligned_guard_row_pool.py --workers 1 --bounded
```

The frozen [product milestone manifest](configs/complex/product-algebra-milestone.json)
lists all eight complete product runs, exact artifact hashes, runtime closures
and historical recovery directions. Full producer protocols in the retained
run directories specify their four-worker commands and source/config inputs.
Use fresh output paths. The signed matching fixture binds literal full matrices
and complete dirty fields; its checker does not trust stored hashes as proof.

The [local validation receipt](runs/20261009T055823Z-checkpoint-thirteen-validation/results/historical-recovery.json)
records four independently reproduced historical versions. Reconstruct them
without modifying the live tree:

```sh
campaign_root=$(pwd)
recovery_root="$campaign_root/research/integer-mult-breakthrough/work/REPRO-UNIQUE/historical"
mkdir -p "$recovery_root/research/integer-mult-breakthrough/code/complex"
mkdir -p "$recovery_root/research/integer-mult-breakthrough/reports/complex"
mkdir -p "$recovery_root/code/synthesis"
cp research/integer-mult-breakthrough/code/complex/partial_kernel_product_algebra.py "$recovery_root/research/integer-mult-breakthrough/code/complex/"
cp research/integer-mult-breakthrough/reports/complex/partial-gaussian-product-fusion.md "$recovery_root/research/integer-mult-breakthrough/reports/complex/"
cp research/integer-mult-breakthrough/reports/complex/dyadic-quotient-channel-volume.md "$recovery_root/research/integer-mult-breakthrough/reports/complex/"
cp research/integer-mult-breakthrough/code/synthesis/two_order_scan_channels.py "$recovery_root/code/synthesis/"
cp research/integer-mult-breakthrough/code/synthesis/weighted_scan_intertwiners.py "$recovery_root/code/synthesis/"
git -C "$recovery_root" apply --unidiff-zero "$campaign_root/research/integer-mult-breakthrough/fixtures/complex/partial-product-original-recovery.patch"
git -C "$recovery_root" apply --unidiff-zero "$campaign_root/research/integer-mult-breakthrough/fixtures/complex/partial-product-budget-scope-recovery.patch"
git -C "$recovery_root" apply --unidiff-zero "$campaign_root/research/integer-mult-breakthrough/fixtures/complex/dyadic-quotient-budget-scope-recovery.patch"
git -C "$recovery_root" apply --reverse --unidiff-zero "$campaign_root/research/integer-mult-breakthrough/code/synthesis/patches/two-order-cut-control-repair.patch"
python3 -B "$recovery_root/research/integer-mult-breakthrough/code/complex/partial_kernel_product_algebra.py" --workers 1 --bounded
```

Compare the reconstructed SHA256 values with the receipt before replaying
further work. Importing the recovered two-order module and calling
`probe((3,"bit_reverse"))` must reproduce the recorded cut-control assertion;
it must not be treated as a successful full scientific run.

Finite allocation and arithmetic checks do not measure native tape time.
The conditional row recurrence assumes a complete supplied strict profile,
paid overhead and growing-depth precision. Product/ring obstructions retain
their declared embedding or encoder scopes; none is a general multiplication
lower bound. Independent analytical reviews are not formal verification.

The [narrow CI registry role repair](runs/20261009T060901Z-ci-registry-role-repair/report.md)
retains the original archive rejection and current regression checks.
Its [exact patch](fixtures/infrastructure/ci-registry-role.patch) applies
with `git apply --unidiff-zero` to published base commit
`512b27a08986bb8bd4395e0401fcdd3d11300d52` in an isolated checkout or directory
outside the live repository's Git ancestry. It reproduces both existing
infrastructure files exactly. Run the repository verification group and
the ordinary staged archive audit after applying it. The exception classifies
the exact valid CI configuration; other payload and size rules remain.

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

## Scalable actual frames and dirty birth reuse

The ninth checkpoint adds exact compact interfaces, two dirty-birth
components and independently scoped budget controls. These standard-library
commands use no downloaded source or solver:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/scalable_subspace_interfaces.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/scalable_frame_review.py --workers 1
python3 -B research/integer-mult-breakthrough/code/complex/verify_right_reflected_interfaces.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/reflected_frame_review.py --workers 1
python3 -B research/integer-mult-breakthrough/code/complex/ballot_role_budget.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_birth_swap_components.py --case equal-birth
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_birth_swap_components.py --case nested-birth
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_birth_swap_components.py --case separate-swap
python3 -B research/integer-mult-breakthrough/code/transfers/degenerate_birth_review.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/degenerate_birth_fixture_review.py --workers 1
python3 -B research/integer-mult-breakthrough/code/transfers/nested_birth_review.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/transfers/noncontained_birth_budget.py --workers 1
python3 -B research/integer-mult-breakthrough/code/obstructions/routed_swap_alignment.py --workers 1 --bounded
```

The birth wrapper replays all baseline and reused one-column physical basis
columns, two-column bank origins and three complete Gaussian fields per
case. It never promotes origin coverage to all two-column columns. The
separate-body SWAP check returns canonical raw data and full transformed
dirty banks, but its complete paid rank exceeds capacity. The routed test
binds every coefficient and every pair column of its bounded case; it does
not provide a helper word.

The [scalable recovery config](configs/complex/scalable-interface-recovery.json)
and [reflected recovery config](configs/complex/right-reflected-recovery.json)
identify exact historical source patches. Copy the current corresponding
source to an isolated directory preserving its repository path, then apply
the configured patch with `patch --batch --forward -p1 -i <absolute-patch>`.
Verify the recovered SHA-256 against the config. For the
[joint-SWAP control repair](code/synthesis/patches/joint-swap-left-control-repair.patch),
preserve its `code/synthesis/` path and use `--reverse` instead of `--forward`.
GNU patch 2.7.6 was used for the coordinator's five exact recoveries. Originals
remain unchanged. Historical failed controls are evidence of failed
attempts, not successful certificates.

The [birth-contract exporter](code/synthesis/dump_birth_contract.py) regenerates
the nested mathematical fixture in a fresh output path. The original equal
fixture is retained byte-for-byte and pinned independently. Gzip manifests
retain complete historical receipts and logs; authored source, configs,
fixtures and recovery patches remain readable. The artifact manifest records
each full copy and its original namespace.

Run the three populated CI groups using the fresh-directory commands above.
Complete local results are recorded in the ninth validation run. Algebraic
operator equality, conditional role moments and exact finite dirty components
remain distinct from a native tape proof and a multiplication exponent.

## Joint mutable births and conditional native wrappers

The tenth checkpoint adds the following standard-library checks. All commands
are from the repository root; omission of optional output arguments makes them
safe to repeat without overwriting retained evidence.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/native_gl_routes.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/native_frame_wrapper_plan.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/native_wrapper_endpoints.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/native_gl_review.py --workers 1
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_joint_boundary_components.py --case joint-mutable
python3 -B research/integer-mult-breakthrough/code/transfers/joint_mutable_birth_review.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_joint_boundary_components.py --case address-boundary
python3 -B research/integer-mult-breakthrough/code/obstructions/partial_output_budget.py --workers 1 --bounded
```

The new component wrapper retains all four original cases. Joint births check
both core and canonical maps, all one-column physical inputs, and explicit
two-column origins and Gaussian fields. The address check keeps its separately
scoped obstruction models. Runtime source freezing includes the dynamically
loaded scalar helper source; the registry lists the complete effective closure.
The joint independent reviewer imports no producer and binds the retained
fixture with its own suffix-based derivation of current-data responses.

The [joint contract exporter](code/synthesis/dump_joint_mutable_birth.py) accepts
`--output <fresh-contract.json>`. Retained fixture bytes, exporter identity and
historical protocols distinguish regeneration from verification. The initial
failed joint source is reconstructed in a fresh topic-shaped directory using
the [control-domain repair patch](code/synthesis/patches/joint-mutable-birth-control-repair.patch)
with `patch --batch --reverse -p1`; its expected hash is in the failed run's
`failure.json`. The [native GL recovery config](configs/complex/native-gl-recovery.json)
instead uses its forward patch and repository-shaped source path. Both exact
failed-source recoveries were independently repeated by the coordinator with
GNU patch 2.7.6. These failures remain failed evidence.

The native routing bill applies the pinned `original-layers` input contract.
It explicitly charges full payloads, exceptional repair, descriptor work,
three complete address slots and any growing-dimensional gate count. A third
address slot does not create a free scalar bank. Same-width recursion,
stopping, precision and complete role stock require their own proof. Read the
linked native route report before using its long-record simplification.

Completed receipts and logs have complete gzip copies with unchanged originals
and manifest hashes. New source, configurations, small fixtures and reports
remain readable. The local validation receipt records all populated CI groups;
green CI does not promote a conditional compiler or partial primitive to a
multiplication theorem.

## All-Lagrangian frames, nonlinear routing and nonunit boundaries

The eleventh checkpoint's bounded commands use only the standard library.
Run them from the repository root. They omit optional output directories;
the nonunit wrapper captures the effective imported source closure without
modifying a producer. The unique-path case also pins its original amplitude
certificate as immutable input.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/lagrangian_frame_interfaces.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/verify_general_clifford_anchors.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/one_helper_clifford_chronology.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/multiframe_helper_chronology.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_nonunit_prepost_components.py --case amplitude
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_nonunit_prepost_components.py --case paths
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_nonunit_prepost_components.py --case scan
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_nonunit_prepost_components.py --case scan-grid
python3 -B research/integer-mult-breakthrough/code/transfers/packed_toffoli.py --workers 1
python3 -B research/integer-mult-breakthrough/code/transfers/guarded_slot_layout.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/obstructions/sparse_line_input_encoding.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/borrowed_bit_permutation_words.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/guard_slot_geometry_review.py --workers 1 --bounded
```

For complete experiments use each retained run protocol and a fresh output
namespace. Full all-Lagrangian and gate-specific-helper experiments exceed
the bounded CI instances. The streaming producer and integer auditor accept
`--workers 4 --output <fresh-results-directory>`. Their full four-case matrices
are deterministically reconstructed and hashed rather than published as dense
dumps. Source snapshots and timing metadata are not substitutes for those
reproduction commands.

Six historical source hashes were independently recovered. The
[Clifford syntax](configs/complex/general-clifford-recovery.json) and
[helper orientation](configs/complex/one-helper-recovery.json) patches apply
forward to current source in an isolated repository-shaped copy. The
[Toffoli parse patch](fixtures/transfers/packed-toffoli-parse-recovery.patch)
also applies forward. For the guard source, apply the
[fixed-grid recovery](fixtures/transfers/guard-layout-fixed-grid-recovery.patch)
first, then the [control recovery](fixtures/transfers/guard-layout-control-recovery.patch)
to recover its earlier rejected control. The
[streaming annotation patch](code/synthesis/patches/streaming-density-scope-repair.patch)
instead applies in reverse to a topic-shaped copy. Use
`git apply --unidiff-zero`, preserving each patch's paths, and compare hashes
with [the coordinator receipt](runs/20261009T041916Z-checkpoint-eleven-validation/results/source-recovery.json).
Never apply recovery patches to live research sources.

The pinned original complete-stream section is downloadable from the
immutable revision and path in `input-manifest.json` under `original-streams`.
Its acquisition receipt is retained; no downloaded source checkout is required
for bounded CI. Layout claims use existing complete address chunks and paid
elementary selected-bit kernels. Borrowed-bit permutations have additional
address-shape requirements. The record-volume obstruction applies only to the
unchanged independent-coefficient representation.

## Matching, weighted scans and selected reversal

The twelfth checkpoint registers these ten reproducible bounded checks:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/nonlinear_matching_frames.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/nonlinear_canonical_matching_graph.py
python3 -B research/integer-mult-breakthrough/code/complex/column_branching_port_bound.py --bounded
python3 -B research/integer-mult-breakthrough/code/complex/canonical_matching_support_obstruction.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_weighted_scan_components.py --case solver
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_weighted_scan_components.py --case structure
python3 -B research/integer-mult-breakthrough/code/transfers/coherent_matching_routing.py --workers 1 --small
python3 -B research/integer-mult-breakthrough/code/obstructions/walsh_cyclic_embedding.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/general_control_bit_reversal.py --workers 1
python3 -B research/integer-mult-breakthrough/code/obstructions/double_guard_reversal_layout.py --workers 1 --bounded
```

Expected outcomes are exact component passes, with the scope printed by each
runner. The complete matching screen retains 510 candidate frames; full
weighted-scan experiments use the larger dimensions and commands in their
run protocols. The full cyclic experiment enumerates 323,930 affine maps;
the full two-guard experiment checks 4,160 layouts. These remain distinct
from the bounded CI cases. Use a fresh output path for every regeneration.

The two [matching recovery patches](configs/complex/nonlinear-matching-recovery.json)
and [graph annotation recovery](configs/complex/canonical-matching-recovery.json)
apply forward from the retained current sources in disposable copies.
`git apply --unidiff-zero` must recover the hashes in the
[twelfth recovery receipt](runs/20261009T045847Z-checkpoint-twelve-validation/results/historical-source-recovery.json).
Never mutate live sources to reconstruct historical attempts.

The cyclic boundary's university-hosted author manuscript is pinned by URL,
size and SHA-256 in the input manifest. Its PDF remains an external,
downloadable reference, and no bounded check depends on a downloaded paper.
The new input-control bill and same-volume layout are conditional on the
inherited stream-routing contracts and the explicitly unsupplied active
Gaussian child. These commands do not implement a complete native multiplier.

## Twentieth checkpoint: complete scan, target and budget controls

The eleven newly registered bounded checks use only the retained
standard-library runtime closures:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/target_pivot_rank_boundary.py
python3 -B research/integer-mult-breakthrough/code/complex/cap_repeated_target_pivot.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/paired_cap_side_budget.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/paired_cap_leader_budget.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_gaussian_unit_nonlex_five.py
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_two_scan_response_components.py
python3 -B research/integer-mult-breakthrough/code/transfers/selected_fiber_scan_tapes.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/selected_polynomial_scan_tapes.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/verify_selected_scan_native_records.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/phase_xor_coupled_budget.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/selected_scan_independent_replay.py --workers 1 --bounded
```

The last command imports the unchanged literal consumer but uses a new
complete endpoint reference, not the author's verifier or carry reference.
For its complete four-shape replay, replace the final flags with
`--workers 4 --output NEW_OUTPUT_DIRECTORY`. Every output namespace must be
fresh. Full run protocols retain exact seeds, worker counts and source hashes.
The selected-source analytical review adds no runtime dependency.

Complete long certificates are published whole through gzip evidence.
Separate readable summaries explicitly name their omitted arrays and bind
the complete original hash and byte count. In particular, the 1,470,225-byte
coordinator scan certificate and the long target-pivot interface certificate
are not split or cropped. Consult the chronological
[twentieth recovery shard](configs/recovery/checkpoint-twenty-artifacts.json)
for exact archive namespaces and manifests. The preceding nineteenth remote
commit passed all ten matrix jobs. Local registry changes require all three
groups to run under the unchanged CI runner. These checks do not certify
whole native transforms, new global suppliers or multiplier exponents.

## Twenty-first checkpoint: center sharing and formation barriers

The seven newly registered checks use these frozen standard-library closures:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/verify_synchronized_centers.py
python3 -B research/integer-mult-breakthrough/code/synthesis/two_response_outer_gauge_rank.py --workers 4 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/singleton_fanout_release_probe.py --workers 4 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/high_flux_selected_scan_adapter.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/synchronized_center_review.py --input research/integer-mult-breakthrough/fixtures/transfers/synchronized-center-moment-review.json --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/center_current_source_clock.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/odd_cube_dyadic_moments.py --workers 1 --bounded
```

Complete four-worker attempts, exact source pins, fixtures and command/output
contracts are retained in the linked run protocols and publication inventories.
Source-only reviews have no executable PASS entry. The dyadic feature runner
and center reviewer use exact rational enclosures; their optimistic moment
profiles are explicitly separated from literal Gaussian components.

The high-flux first attempt failed an overbroad negative control. In a
disposable topic-shaped copy, applying
[its exact recovery patch](fixtures/transfers/high-flux-negative-recovery.patch)
to the retained accepted source must recover the rejected hash recorded in
the publication manifest. Never patch a live research source to reconstruct
a historical run. All failed and accepted original text is archived whole.

The [twenty-first recovery shard](configs/recovery/checkpoint-twenty-one-artifacts.json)
indexes complete scientific, registry-validation and publication provenance.
Previous recovery shards remain necessary historical evidence. None of these
commands implements a whole native multiplier or proves a new kappa.

## Final twenty-second checkpoint

These six checks verify completed components and frozen mathematical controls:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/verify_paid_total_and_splice.py
python3 -B research/integer-mult-breakthrough/code/synthesis/singleton_quotient_copies.py --workers 4 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/audit_singleton_quotient_prefix.py
python3 -B research/integer-mult-breakthrough/code/transfers/finite_field_router_bootstrap.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/dyadic_total_center_review.py --input research/integer-mult-breakthrough/fixtures/transfers/dyadic-total-center-moment-review.json --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/partial_overlap_fourier_rank.py --workers 1 --bounded
```

Complete four-worker source runs, exact invocation snapshots, scalar/field
scopes and immutable outputs are retained in their inventories. The complete
singleton quotient contract is632,999 bytes and is published whole through
gzip; its compact index identifies its hash and deterministic exporter.
Source-only reviews add no runtime PASS. Typed F5 recurrence source was
never scientifically executed; its static syntax receipt is not evidence
for the proposed algorithm. Future reproduction is separate authorization
after the user-directed shutdown.

The [final recovery shard](configs/recovery/checkpoint-twenty-two-artifacts.json)
retains all original scientific text, CI outputs and final publication
provenance. All prior shards and source closures remain intact. The final
verification reruns the existing repository/smoke/certificate infrastructure;
it launches no new research configuration or parameter sweep.
