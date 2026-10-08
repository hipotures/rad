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
