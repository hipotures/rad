# Odd-weight spectral channels and a coupled integer kernel completion

The five-subset central matrix at ambient dimension eight has a genuine
20-dimensional unit eigenspace. Its invariant spectral projector has diagonal
`5/14`, so a reversible Gaussian-dyadic change of coordinates cannot split this
eigenspace into an independent block with an invariant complement. An explicit
integer reversible basis does isolate the same kernel as a module, while
retaining nonzero coupling from the other 36 coordinates. These are exact scalar
results. They supply neither a physical phase schedule nor a new characteristic
root or exponent improvement.

## Question and exact screen

For odd `k=2r+1`, define

```text
f_k(t) = binom((t-1)/2,r)
       = product_{j=0}^{r-1} (t-(2j+1))/(2(j+1)),
K[S,T] = f_k(|S intersection T|),  |S|=|T|=k,
side = I-K.
```

The diagonal is one. Distinct odd intersections have central coefficient zero,
which leaves the side supported on binary label-orthogonal incidences. A unit
eigenvalue of `K` gives a kernel of the side. This does not by itself remove a
physical role, a frame conversion or a dirty-bank restoration obligation.

The inclusion-Gram matrix with entries `binom(|S intersection T|,t)` has
eigenvalues `binom(k-j,t-j) binom(h-t-j,k-t)` and multiplicities
`binom(h,j)-binom(h,j-1)` for `k <= h/2`. The matrices share their eigenspaces.
This formula is taken from Lemma 8 and Theorem 9 of Ghareghani, Ghorbani and
Mohammad-Noori, *Intersection matrices revisited*, arXiv 0902.4367v4,
2011-11-13, PDF page 12. [Pinned primary paper](https://arxiv.org/pdf/0902.4367v4).

The experiment independently uses complement reduction when `k > h/2`:
put `ell=min(k,h-k)` and write the original intersection as
`2k-h+u` for complements of size `ell`. Newton expansion of this shifted
polynomial gives the linear combination of inclusion-Gram matrices. This is
scalar analysis; it grants no physical complement permutation or new label
anchors. All coefficients are checked to remain dyadic. Independent controls
check total multiplicity, trace and the squared trace against a direct overlap
count in one row.

The four-worker attempt at actual UTC `2026-10-09T00:29:27.885110+00:00`
tested 952 cases: odd weights 3 through 17 and `k <= h <= 128`. It took about
1.286 seconds. Only the following nontrivial exceptional low zero or unit
channels occurred; the single-coordinate cases `h=k` are excluded here.

| h | k | volume | center rank | side rank | exceptional channel |
|---|---|--------|-------------|-----------|---------------------|
| 9 | 3 | 84 | 8 | 84 | constant central eigenvalue zero |
| 8 | 5 | 56 | 28 | 36 | central eigenvalue one, multiplicity 20 |
| 11 | 7 | 330 | 165 | 329 | central eigenvalue one, multiplicity 1 |

Four direct rational matrix eliminations, at `(h,k)=(8,5),(9,3),(10,7),(8,7)`,
match the predicted ranks. Generic zero channels above the central polynomial
degree are expected; the screen does not identify them as new exceptions.
Complete generic scan rows are deterministically regenerable and represented
by per-weight hashes. The compact retained JSON explicitly describes this
omission. No statement is made about weights above 17 or ambient sizes above
128. [Protocol and results](../../runs/20261009T002927Z-transfer-odd-weight-spectrum/).

## Invariant split obstruction checked without the eigenvalue formula

At `h=8,k=5`, the eigenvalues and multiplicities are

```text
eigenvalue       43/8   35/8   1    0
multiplicity      1      7   20   28.
```

The projector onto eigenvalue one is

```text
P = (64 K^3 - 624 K^2 + 1505 K)/945.
```

For a direct finite control, form the complete integer matrix `Hc=8K` from
intersections, and set `N=Hc^3-78Hc^2+1505Hc`. The checker verifies every entry
of `N^2=7560N` and `Hc N=8N`, and verifies `trace(N/7560)=20`. The direct side
rank is 36. Thus `N/7560` projects onto the complete unit eigenspace, separately
from the paper's spectral formula. Its symmetry makes it the orthogonal
projector. Every diagonal entry is exactly `5/14`; applying it to a coordinate
unit vector produces `5/14` in that coordinate. The numerator matrix hash is
`68a7e1a26256d62ca1e6522390c0f9e83d06b7bbbb3a6e34bd3b09c7dba32f47`.

Let `R=Z[i,1/2]`. If a reversible coordinate map and its inverse both had entries
in `R` and put `K` into a block diagonal form consisting of the complete
20-dimensional identity block and an invariant complement, then conjugating the
coordinate projector would give an `R`-valued spectral projector. This
projector is unique because the complement has no eigenvalue one. The entry
`5/14` is outside `R`, which is a contradiction. The same transitive-diagonal
test gives `1/330` for the constant unit channel at `h=11,k=7`.

This refutes an **invariant** Gaussian-dyadic split. It does not refute a
nonspectral kernel completion, coupled quotient, rational encoding interface,
paid nonlinear division or arbitrary native algorithm. Omitting the identity
from `I-K` is also explicitly rejected: the center rank 28 and side rank 36
are different exact quantities.

## Constructive nonspectral escape

Let `H=8(I-K)`, which is integral and has rank 36. The finite construction first
preconditions with a ballot-incidence matrix `B`. Its rows are the original
five-subset labels `S`. Its columns are subsets `a` of size 0 through 3 whose
zero-based sorted elements obey `a_i >= 2i+1`. There are exactly
`1+7+20+28=56` columns, and

```text
B[S,a] = 1 if a is contained in the complement of S, and 0 otherwise.
```

An explicit integer Euclidean row word reduces `B` to identity using only
integer shears, exchanges and sign changes; all final pivots are units. The
word itself certifies that both `B` and `B^-1` are integral. No external theorem
about ballot bases is needed for this finite assertion.

On `B^-1 H B`, two-sided Euclidean reduction retains every column operation and
every row operation, producing a literal certificate `U H V = diagonal` in
the original scalar coordinates. Every elementary factor is unimodular. The
diagonal has 36 nonzero entries and 20 zeros; divisibility conditions of a
Smith normal form are neither needed nor claimed. The last 20 columns of `V`
are a complete integral kernel basis. Column operations translate into a
chronological data word: reverse their order, replace column
`target += c*source` by data `source += c*target`, then apply the explicit
forward incidence-basis word.

The four-worker final attempt starts at actual UTC
`2026-10-09T00:40:50.418026+00:00` and takes about 0.595 seconds. Four distinct
source orders pass: lexicographic, reverse, rotation by 17 and a shuffle with
seed 20261009. Each complete word is bound to its labels. All 56 basis columns,
the complete two-sided inverse matrices and four arbitrary dyadic dirty fields
per order are replayed exactly. Word lengths are 2,179, 1,994, 2,025 and 2,465
scalar operations respectively. The lexicographic case has 2,057 shears, 76
exchanges and 46 sign changes. [Readable lexicographic summary](../../fixtures/transfers/side-kernel-lexicographic-summary.json); its omission record links the complete literal word in gzip.

In these coordinates,

```text
V^-1 K V = [[A, 0], [C, I_20]], with C != 0.
```

All four orders give 116 nonzero bottom couplings. The first retained witness
is `C[36,0]=137/8`: deleting the coupling changes output coordinate 36 by
`137/8` on the input unit vector `delta_0`. Define the actual integral projector
`P_int = V diag(0_36,I_20) V^-1`. Every complete matrix satisfies

```text
P_int^2 = P_int,  trace(P_int)=20,
H P_int = 0,     P_int H != 0.
```

Thus `K P_int=P_int`, while `P_int K != P_int`. Its image is the required
kernel, but its complementary coordinates are not invariant. In the
lexicographic case `(P_int H)[0,0]=1583`, an exact noncommutation witness. This
explains how an integral completion avoids `5/14` and why it cannot be treated
as independent unit channels. [Final protocol and compact evidence](../../runs/20261009T004050Z-transfer-side-kernel-completion/).

## Conditioning, paid interfaces and failed attempts

The scalar words use integer coefficients, so they require no extra fractional
bits on a common fixed dyadic grid. The largest forward row-L1 prefix bound,
including each literal coefficient-times-source temporary, is 9,927,120 times
the input component bound; the forward endpoint bound is 537,129. The inverse
prefix and endpoint bounds are 37,170 and 16,972. The largest scalar coefficient
uses 12 bits. These are exact finite bounds for this scalar word; applying the
conjugated `K`, its phase children or native scalar multiplication buffers is
outside this certificate.

All roles are assumed to have the same **actual** address operator while a
scalar shear is applied. A virtual source label is insufficient. The word does
not provide frame conversion, copies of complete payloads, address routing,
physical exchanges, phase normalization, full dirty scratch restoration or a
row/depth transfer. The four input-order permutations are fixture layouts,
not free native permutations. Even in a compatible common frame, 1,994–2,465
scalar operations and their inverse costs must be charged. This generic
completion is a proof of the coupled escape, not a competitive side circuit.

Three prior immutable attempts remain separate:

1. At `00:36:29`, column-only reduction exceeds the explicit 32,768-bit basis
   coefficient guard. This is an intermediate-growth failure of that algorithm.
2. At `00:37:56`, two-sided reduction reaches the algebraic checks but fails
   serialization of a very large left certificate at Python's 4,300-digit
   conversion limit. No complete certificate was emitted or claimed.
3. At `00:40:20`, first-nonzero incidence pivot selection chooses a nonunit for
   a permuted row order. The final Euclidean unit-pivot policy repairs the
   selection without adding division.

Their rejected source hashes are respectively
`b75ccd466906ebb40c9ee31eca7ebfadd4c0c15e48d1a69a7cdf58fcddde61e0`,
`95699499a396db76a5036eacabd70797ec10d0115c6f1e8405d6b96a6a55b616`, and
`3b36f5dd483f9e86736bb12c8e09fb3807c26c5563b6e46ba4f26b912a09a7d9`.
Reverse the unit-pivot, incidence-preconditioner and two-sided-growth patches,
in that order, to reconstruct all three from the final source. This reverse
recovery has been executed and hash-checked. [Recovery receipt](../../runs/20261009T004050Z-transfer-side-kernel-completion/results/source-recovery.json).
Original raw files are unchanged. The compact final JSON omits the large words
and states that omission; the complete first word is retained in the fixture gzip copy and the full raw
summary retains all four. The coordinator registers the
completed raw text archives separately.

## Leverage assessment and reproduction

The largest unit channel in this screen is 20 of 56 coordinates, about 35.7%.
This fraction is not a saving in the complete recursive child ledger. The
required coupling, basis words, phase copies and precision charges can consume
it. The other unit exception has only one of 330 coordinates. No supplied
mechanism changes the accepted characteristic root or establishes that it can
cross `kappa=10^-4`. The useful follow-up is a much cheaper coupled quotient
with a realizable source/sink chronology and an explicitly paid complete
ledger; increasing the spectrum sweep is lower priority.

From the correct research worktree, run the bounded checks:

```bash
python3 research/integer-mult-breakthrough/code/transfers/odd_weight_spectrum.py --workers 1 --small
python3 research/integer-mult-breakthrough/code/transfers/side_kernel_completion.py --workers 1 --small
```

Run the complete screen with the same commands using `--workers 4` and omitting
`--small`. Optional `--output <fresh-directory>` creates immutable protocol and
result files and rejects an existing output path. The two sources require only
Python's standard library, and the kernel completion imports only the retained
central-value function from this track's spectrum source. The spectrum config
pins the primary paper by exact arXiv version and PDF SHA256; the executable
checks do not require the downloaded PDF. The kernel completion's effective
source SHA256 is `7f47829f5bd7f0b79a88270b04f51cccbc7d4246647ac18caa82f089ba17b550`.

These are exact finite certificates plus a conditional ring obstruction and
an exact finite scalar screen. They are not formal verification, an all-size
native algorithm or an exponent claim.
