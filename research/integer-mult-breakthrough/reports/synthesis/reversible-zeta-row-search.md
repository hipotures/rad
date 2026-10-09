# Reversible zeta row search: eleven gates remains unresolved

Status: **EXACT SMALL CONTROLS, FINITE SOLVER TIMEOUTS AND BOUNDED
DISCOVERY NEGATIVES**. No shorter three-axis word, no new multiplication
exponent and no complete native supplier have been established.

The question is whether the eight-coordinate subset-zeta matrix
`Z3[S,T]=1[T subset S]` can use at most eleven reversible scalar row
additions, with explicitly retained Gaussian-dyadic unit scales and
row permutations. Its standard axis word has twelve additions. This is
a structural supplier question rather than a small parameter change to
the previous scalar-center leaderboard.

## Mathematical leverage, conditional on a paid tensor architecture

For a scalar gate `row_t += c*row_s`, its f-fold tensor word partitions
records by which columns carry either symbol s or t. That activity mask
is unchanged by the gate. A block with a active columns is a tensor
triangular gate, conjugate to `Z_a` by `diag(c^weight)` when c is a unit.
The remaining `2^h-2` symbols are spectators, not zero padding. Unit
row scales and finite row permutations have separate tensor wrappers.

If all partitioning, compaction, inverse routing, row padding and local
fees were paid in an admissible native contract, a g-addition base word
would suggest the normalized moment

```text
m_f(p) = g * E[(A/(h*f))^p],  A ~ Binomial(f, 2/2^h),
lim m_f(p) = g * (2/(h*2^h))^p.
```

For h=3 and g=11, the limiting root is
`p=log(11)/log(12)`, approximately 0.965. This is substantial conditional
component leverage. It is not a kappa certificate: the scalar word is
missing and the activity grouping is unpaid. Computing a numerical
activity key in polynomial metadata time does not prove a fast tape
permutation. Naive radix grouping by f mask bits can take O(V*f).

The self-reduction would naturally call **Z_a**, not C_a. If it were
proved, the exact separately recorded factorization of C_e into two
Z_e calls plus Gaussian chirps/scalars could use the resulting faster
Z supplier without a two-call same-size C bootstrap. Endpoint and
internal Z prefix growth still need a complete guard/depth proof.

## Independent models and observed outcomes

Every computational attempt used four processes and one native thread
per process. Seeds, value bounds, clocks and effective sources are in
the unchanged protocol and persistence receipts. No memory utilization
target was used.

| Attempt | New restriction/relaxation | h=3, budget eleven |
|---|---|---|
| F3/F9 packed SMT | All field coefficients; final projective rows and permutations | Both UNKNOWN after 120 s |
| Binary packed SMT | Gaussian-integer reduction modulo (1+i), free or fixed final row order | Both UNKNOWN after 120 s |
| Explicit Boolean CNF | One-hot gates, changed-row bounds from both endpoints; Glucose 4.2.1 and MapleChrono | Both interrupted after 120 s |
| Real dyadic beam | Coefficients ±2^k; unit normalization; three objectives, 1200 retained states | No witness in 24–55 s |
| Gaussian dyadic beam | Coefficients i^r(1+i)^k, including negative k; exact unit normalization | No witness in 57–64 s |

The real beams reached the last search depth with an empty retained
frontier. The Gaussian nonzero-count beam also reached that depth; the
phase and logarithmic beams reached their time budgets earlier. Beam
widths and coefficient/entry bounds are discovery restrictions.
An empty retained frontier is not an exhaustive exclusion. The reported
generated-state counts are cumulative distinct candidates within each
frontier generation, not a globally unique-state enumeration.

The explicit CNF has 4,157 variables and 37,180 clauses for the
three-axis model. Both engines timed out. It uses the valid constraints
that at most t rows can have left the initial monomial class after t
steps, and at most g-t rows can remain outside the final row class.
Adjacent identical binary gates cancel. Adjacent commuting gates may
be put in lexicographic order. These restrictions do not resolve the
case and are not being used as evidence for a twelve-gate minimum.

Reduction modulo3 is defined for all Gaussian-dyadic entries because
2 is invertible. The Gaussian units (1+i)^k i^r reduce to the eight
nonzero elements of F9. Thus the F9 necessary model includes free unit
scales pushed into row-addition coefficients. The F3 model addresses
the real dyadic subcase. Binary reduction instead requires
Gaussian-integer coefficients and integer unit scales; division by2
or(1+i) is outside that model. All larger-case results here are UNKNOWN.

## Exact controls and limits of verification

Each method recovered the four-addition two-axis control. A separate
standard-library verifier reads the retained witnesses and replays all
four forward and inverse matrix columns, checks every encountered
Gaussian-dyadic grid, and rejects one omitted arithmetic gate per word.
It independently enumerates all binary words with zero through four
active additions, giving witness counts `0,0,0,0,12`. It also enumerates
all `24^3` ternary three-addition words, including coefficients ±1 and
final row signs/permutations, finding none. These finite controls are
stronger than merely trusting the small solver status.

The small CNF UNSAT proof text is retained but has not been checked by
an independent DRUP checker. No large UNSAT proof exists. A modular SAT
word is not automatically an exact characteristic-zero circuit:
the retained two-axis SAT words separately have exact integer lifts.
The discovered dyadic controls retain their unit scale/permutation
words and exact prefix bounds. These are finite linear operators,
not native arbitrary-dirty tensor suppliers.

The related Boyar–Find literature establishes the standard gate count
for cancellation-free Sierpinski circuits. That restricted theorem
must not be substituted for an unrestricted Gaussian-dyadic row bound.
See [Cancellation-Free Circuits in Unbounded and Bounded Depth,
arXiv:1305.3041](https://arxiv.org/abs/1305.3041). Only the primary
abstract was used for this scope comparison; the coordinator's full
paper review is separate.

## Recovery and bounded verification

From the research root:

```bash
python3 -B code/synthesis/verify_zeta_row_controls.py
python3 -B code/synthesis/zeta_dyadic_row_beam.py --workers 4 --seconds 60 --output work/synthesis/<fresh-run>/results
python3 -B code/synthesis/zeta_gaussian_unit_beam.py --workers 4 --seconds 60 --output work/synthesis/<fresh-run>/results
```

The bounded verifier is standard-library only. Solver reproduction
requires the pinned dependencies in
`configs/synthesis/zeta-row-search-dependencies.json`. Downloaded
wheels and environments remain ignored. For the SMT sources use
z3-solver 4.15.4.0; for the CNF source use python-sat 1.9.dev15 with
the named engines. The exact local wheel names, hashes and acquisition
logs are retained separately. CPython 3.14.4 was used for these runs;
portable package version pinning does not claim that other platform
wheels have the same byte hashes.

Completed attempts:

- [F3/F9 search](../../runs/20261009T055111Z-synthesis-zeta-reversible-row-sat/report.md).
- [Packed binary search](../../runs/20261009T055734Z-synthesis-zeta-binary-row-sat/report.md).
- [Real dyadic discovery](../../runs/20261009T060612Z-synthesis-zeta-dyadic-row-beam/report.md).
- [Explicit CNF search](../../runs/20261009T061448Z-synthesis-zeta-binary-row-cnf/report.md).
- [Gaussian dyadic discovery](../../runs/20261009T062337Z-synthesis-zeta-gaussian-unit-beam/report.md).

Each run retains the complete compact certificate unchanged and points
to full ignored formulas/logs with byte hashes. Gzip publication of
those completed text bytes is handled by the coordinator; the original
raw directories remain immutable. Historical timings and solver
statistics are evidence, not deterministic reproduction expectations.

The next useful step is a structural cancellation/division mechanism
or a paid activity-layout primitive. Longer repetitions of the same
binary solver or an unmotivated larger-base sweep are not justified by
these results.
