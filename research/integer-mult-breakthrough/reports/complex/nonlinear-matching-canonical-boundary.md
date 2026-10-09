# Nonlinear matchings meet two exact canonical boundaries

## Findings

Nonlinear address permutations supply genuine frames outside the Clifford
model, under the separately paid guarded routing contract. They do not
improve the two fixed local interfaces tested here.

First, the original four-port component has an exact width lower bound five
through **any invertible common address frame** whose single-bank adapters
use charged C children and monomial/diagonal wrappers. This includes
nonlinear permutations and nonunit coefficients. The existing Clifford
component already attains five.

Second, for a matched-pair primitive `A_M=alpha*I+beta*M` and canonical
`F=C_full`, a single width `h-1` C child for `F*A_M^-1`, with arbitrary
invertible monomial/diagonal wrappers, forces `M` to be a fixed odd-weight
translation. Nonlinear fixed-point-free matchings cannot enlarge that
canonical one-child family. This support-block obstruction holds for every
dimension and tensor column count, including entangled input/output
permutations.

The proofs are analytic mathematical statements with exact finite controls;
they are not Lean formal verification. They do not exclude new helpers,
coupled product representations, partial-output tasks, multiple-child
interfaces, changed physical ports, or a different global chronology. No
complete multiplication primitive or larger exponent is certified.

## The four-port column-branching bound

Let `P0,P1` be the two fixed incoming actual operators and `Q0,Q1` the
outgoing ones from the
[retained four-incidence fixture](../../fixtures/complex/noncommuting-four-incidence.json).
For a common actual frame `R`, the incoming adapters are `R*Pj^-1` and
outgoing adapters `Qi*R^-1`. Write `s(A)` for the maximum number of nonzero
entries in a column of a matrix. Over any coefficient field,

```text
s(A*B) <= s(A)*s(B).
```

Indeed, each column of the product is supported in the union of at most
`s(B)` columns of `A`. Cancellation can reduce this union. It cannot enlarge
it. Each `C^r` child has column support `2^r`; a monomial or diagonal
operator has support at most one. Thus a serial single-bank adapter charged
width sum `w` has `s <= 2^w`, without a unitary or Clifford assumption.

The two disjoint crossed products consume all four incidence width sums:

```text
(Q1*R^-1)*(R*P0^-1) = Q1*P0^-1 : every column has support8
(Q0*R^-1)*(R*P1^-1) = Q0*P1^-1 : every column has support4.
```

Consequently their total charge is at least `log2(8)+log2(4)=5`. The exact
original common operator `K_code3*Htilde_onbit2` attains incidence widths
`(1,1,1,2)`. This extends the local minimum beyond the old all-Lagrangian
search; it does not convert a local component into a complete canonical
primitive.

[column_branching_port_bound.py](../../code/complex/column_branching_port_bound.py)
imports no producer or compiler. It independently reconstructs every actual
port by the exact character sum

```text
K_A[y,x] = 2^-h * sum_z i^q_A(z) * (-1)^((x xor y) dot z).
```

It verifies exact unitarity of the fixed ports, every crossed column support,
and the original attaining representative. Its 1024 seeded sparse matrix
controls exercise the support inequality. A strict cancellation control
distinguishes the valid upper bound from an invalid equality claim. The
seed is `202610090409`. Independent synthesis-track source inspection
accepted the product accounting and scope: `f=1`, one common actual frame,
and serial single-bank adapters. Helpers, bank mixing and altered ports are
outside that review.

## Exact nonlinear family screen

[nonlinear_matching_frames.py](../../code/complex/nonlinear_matching_frames.py)
allows a one-child interface only after reconstructing its complete literal
matrix. It requires uniform power-two column and row degree, complete square
support components, and fourth-root Gaussian-dyadic coefficients. Removing
one row and column phase must give a real Walsh table; sign-group closure
then constructs actual input/output coordinates. Every original coefficient
is reconstructed from these coordinates, one C child, arbitrary address
permutations and retained unit phases. Row sparsity alone is not acceptance.

The four-worker experiment compared four fixed three-bit families with the
original physical ports. A candidate may be rejected when its relative
operator does not have the declared one-child interface.

| Common-frame family | Candidates | Non-Clifford | All four edges admitted | Minimum width |
| --- | ---: | ---: | ---: | ---: |
| All perfect-matching C primitives | 105 | 98 | 7 | 7 |
| Fixed Toffoli on the left of every actual Clifford frame | 135 | 135 | 135 | 5 |
| Fixed Toffoli on the right | 135 | 135 | 15 | 6 |
| Fixed Toffoli on both sides | 135 | 133 | 15 | 6 |

There are 510 candidates and 501 are independently checked to be
non-Clifford by their exact Pauli images. Left monomial changes preserve the
width interface class, which explains retention of the baseline five. The
stronger crossed-support proof removes any reason for expanding these
families in pursuit of a strict local width four.

All retained representatives have literal `f=1` and `f=2` edge checks on
complete four-field payloads, totaling 5760 field values. Arbitrary address
routes are synthesized exactly: an eight-point permutation needs at most
seven transpositions, each an affine conjugate of one three-bit Toffoli.
Every route image is checked. Per-address phases include all global units
exactly once; a phase corruption must fail coefficient reconstruction.
These are finite permutation and Gaussian operator certificates, not native
tape timing or a full mutable-data chronology.

## Canonical matching endpoint discriminator

Put `alpha=(1+i)/2`, `beta=(1-i)/2`. For a fixed-point-free matching
involution `M`, `A_M` is unitary, `A_M^2=M`, and its source interface uses one
C child with explicit monomial wrappers. The remaining canonical sink is
`K_M=F*A_M^-1`. The complete three-bit experiment covers all 105 matchings.
Exactly 24 matchings pair each even-parity address with an odd-parity address;
their columns all have half-size support. Only four have the complete Walsh
support blocks needed by one width-two child. They are translations by
`1,2,4,7`; all are already Clifford.

[nonlinear_canonical_matching_graph.py](../../code/complex/nonlinear_canonical_matching_graph.py)
certifies actual source, sink, and all 16 directed cross interfaces among the
four admitted primitives. Its first full run records every matching,
including rejection reasons. Literal whole `f=1/f=2` source and sink checks
cover 576 fields. The bounded path contains mixed/even nonlinear rejection
controls; the full path is cheap enough to be the preferred CI check for all
105 matchings.

## All-size support-block proof

The canonical full Gaussian kernel is

```text
F[y,x] = alpha^h * (-i)^wt(y xor x).
```

For column `x` of `K_M`, let `s=x xor M(x)` and `w=wt(s)`. Its coefficient is

```text
conj(alpha)*F[y,x] + conj(beta)*F[y,M(x)].
```

If `w` is even, the two F coefficients have ratio `+1` or `-1`, and this sum
never vanishes. Its column has full support, exceeding a width `h-1` child.
If `w` is odd, their ratio is `+i` or `-i`, and precisely half of the rows
remain:

```text
supp K_M[:,x] = { y : y dot s = x dot s + (w-1)/2 mod2 }.
```

A single `C^(h-1)` on a complete h-bit address cube has two spectator
classes. Its support graph is two disjoint complete bipartite blocks.
Invertible diagonal factors do not change its support, and arbitrary input
and output permutations preserve this block property. In particular, two
column neighborhoods are identical or disjoint.

Two distinct nonzero GF(2) normals `s,t` define independent linear
functionals. Their affine hyperplanes intersect in `2^(h-2)` points when
`h>=2`; their half-size neighborhoods overlap but differ. Hence all matching
differences must have the same normal `s`. The matching is then exactly
`M(x)=x xor s`, and `s` must have odd weight. At `h=1` the unique matching is
already the odd translation. This is a necessary support argument; the
previous exact canonical odd-line compiler supplies the converse one-child
interfaces for translations.

For any positive tensor column count `f`, fix the same other input column
labels and any common supported spectator outputs. A partially overlapping,
unequal pair of neighborhoods in one column remains partially overlapping
and unequal after tensoring. Therefore arbitrary entangled permutations of
the entire cube cannot turn this nonlinear tensor kernel into complete
single-child blocks either. This does not exclude a composition of several
children whose full widths and moments are paid.

[canonical_matching_support_obstruction.py](../../code/complex/canonical_matching_support_obstruction.py)
imports no producer. It compares the exact Gaussian coefficient with the
hyperplane formula for every coefficient of all 105 three-bit matchings,
32 four-bit sampled/translation cases, and exact selected coefficient and
partial-overlap witnesses at dimensions 16 and 64. The latter use an implicit
four-address rewrite of translation pairs, not large full matrices. Its
seed is `202610090418`; four workers completed in about 0.051 seconds. The
all-size theorem follows from the displayed algebra, not from extrapolation
of those finite checks.

## Native routing scope

The new finite routes use the separately proposed
[paid packed nonlinear routing lemma](../transfers/packed-nonlinear-routing.md),
report SHA256
`5ef7c1943ae507825f1eb313bae035f92be7659e44511deb0b70f894d4e192a0`.
Its source is `packed_toffoli.py` SHA256
`5fc6fb8ce5507fae0568e85d701918cd8ddfe65ed124810eb3edfbfff9fa7f80`.
It requires four existing complete address slots of width `(f+1)K`, restores
the arbitrary fourth address companion, and pays all complete exceptional
records. Its bill is

```text
O(V(L^tau+1) + M*A^3 + delta*M*A*(R+A)), delta <= 80*f*2^-K.
```

The companion is an address slot inside a role, not a clean scalar bank.
Adding a complete range changes volume and is not free. The separate
[guard-allocation lemma](../transfers/guarded-slot-layout-transfer.md) can
reuse an existing complete cube, but pays each reserved selected-bit
Gaussian endpoint and remainders; compaction/return, complete rows,
precision and child stopping remain obligations. Thus the three-bit local
matrices here do not establish a whole canonical source layout merely by
mentioning a fourth slot. Growing dimension also retains all router word
lengths. None of these caveats changes the support-level obstructions.

## Immutable attempts, recovery and reproduction

The nonlinear factor's first bounded attempt failed because a call to the
pinned coordinates helper omitted its ambient dimension. Its exact failed
SHA256 is
`4a8b2f18402ba4cc78edb96b669a38f29d53aa23a8464ea8eb653737fea1ca7c`.
The accepted source is
`e0048d6949270f8e3abd34de7323bde72ff97d66e8b10e80ee20b49e9068b640`.
[The recovery patch](../../fixtures/complex/nonlinear-matching-coordinate-recovery.patch)
reconstructs the failed bytes from the accepted source with
`git apply --unidiff-zero` in an isolated directory. A separate
[comment-only recovery patch](../../fixtures/complex/canonical-matching-comment-recovery.patch)
recovers the original successful canonical-graph source before correcting
its bounded-case annotation. Neither operation changes the live historical
run, its certificate, or its protocol.

The full 510-candidate original is roughly906 KB of row-level JSON. It
remains unchanged in ignored local storage. The durable compact summary
omits individual candidate rows and secondary retained ties, explicitly
names those omissions, and records the original path, byte count and SHA.
Complete text evidence publication is the coordinator's separate gzip
milestone action. No omitted local original is represented as present in a
plain Git clone. All results are deterministically regenerable using the
authored sources, pinned dependencies, fixture and commands.

Completed immutable attempts:

- [First coordinate-call failure](../../runs/20261009T040641Z-complex-nonlinear-matching-first/)
- [Bounded coordinate repair](../../runs/20261009T040726Z-complex-nonlinear-matching-coordinate-repair/)
- [Four-worker 510-candidate screen](../../runs/20261009T040727Z-complex-nonlinear-matching-full/)
- [Independent column-branching control](../../runs/20261009T041200Z-complex-column-branching-bound/)
- [Canonical matching bounded run](../../runs/20261009T041425Z-complex-canonical-matching-bounded/)
- [Canonical matching full run](../../runs/20261009T041426Z-complex-canonical-matching-full/)
- [Four-worker support-theorem controls](../../runs/20261009T041852Z-complex-matching-support-theorem/)
- [Final CI and exact source recovery](../../runs/20261009T042404Z-complex-nonlinear-matching-ci/)

Portable repeatable commands, with no reused output path, are:

```bash
python3 research/integer-mult-breakthrough/code/complex/nonlinear_matching_frames.py --workers 1 --bounded
python3 research/integer-mult-breakthrough/code/complex/nonlinear_canonical_matching_graph.py
python3 research/integer-mult-breakthrough/code/complex/column_branching_port_bound.py --bounded
python3 research/integer-mult-breakthrough/code/complex/canonical_matching_support_obstruction.py --workers 1 --bounded
```

Append an exclusive new `--output` file for a retained attempt. The full
nonlinear frame screen uses `--workers 4` without `--bounded`. Source and
every imported dependency are SHA-pinned in protocols; completed runs check
them before and after execution. Python 3.14.4 and the standard library were
used. The config files preserve all seeds, finite families, native scope and
recovery directions.

The next research question should change the coupled algebra/product or
output task. Enlarging nonlinear matching families under these fixed
single-child canonical endpoints has no mathematical leverage.
