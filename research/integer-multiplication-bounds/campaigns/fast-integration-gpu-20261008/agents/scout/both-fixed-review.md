# Scoped review of PR40's explicit both-fixed data interface

Reviewed 2026-10-08 13:35 UTC by the GPU campaign literature scout.
This is a source and proof review, with zero CPU-bound execution allocation.
It does not claim a new replay of the full source-family computation.

[Rohan Arun's CrocSwap PR40](https://github.com/CrocSwap/integer-mult-bounds/pull/40)
fixes both local bases to `L_h=I+J` at ordered dimensions `(23,25)`.
The pinned obtainable head is `e3bf3ab0cb1ec48588e279b31a97e7a49c72f99e`;
its full executable-validation receipt names tested research commit
`43f59ff533598762cbc43a5e14af2bbbc76fabbd`. The read-only snapshot and hashes
are recorded in [input-manifest.json](input-manifest.json).
The author claims bit saving `783777693/20000000000000` and final conditional
`kappa=1959367447/50000000000000=3.918734894e-5`.
This adopts PR32 fixed profiling, PR36 copied centers and PR34/37 reversed
geometry, extending PR39's fixed-middle integration. It is not our original
both-fixed mechanism, nor is it externally accepted theorem verification.

## Exact interface

The basis is one explicit rational `K=T_M(L23 tensor L25)` with the inherited
controlled permutations unchanged. For each triple indicator `t`, retain
`H_h=I-J/9` and normalize the source projector with `t^T H_h t=2`.
After conjugation its normalized line pair is

```
p'=t+3*1,
xi'=t^T/2-5*1^T/[3(h+1)].
```

All primal and dual coordinates are nonzero. Their coordinate products are
`31/18` inside the triple and `-5/24` outside at h23; `68/39` and `-5/26`
at h25. In each dimension their sum is one. These dimension-specific values
must not be replaced by h25 or h47 constants on the first axis.

The inherited boundary prescriptions give arbitrary-matrix transfer:
the first23/last23 corner of `A tensor(v nu)` is
`diag(v_i) A diag(nu_(j+2))`, while the first25/last25 corner of `(p xi) tensor B`
is `diag(p_(r_i)) B diag(xi_(c_j))`, for
`r=(0,...,22,22,0)` and `c=(22,0,0,...,22)`.
Nonzero diagonal scalings preserve every ordered zero and nonzero minor.
Thus changed internal producer matrices can use the same physical transfer
if their actual fixed profiles are separately certified. No generic local
profile remains on either axis.

For retained-center complements, put

```
p_i=e_i+2*1/(h-9),
xi_i=(h-9)*1^T/12-(h-9)*e_i^T/4.
p'_i=e_i+(3*h-7)*1/(h-9),
xi'_i=(h-9)*1^T/[3(h+1)]-(h-9)*e_i^T/4.
```

At h23 the transformed pair is `e_i+31*1/7` and
`7*1^T/36-7*e_i^T/2`; at h25 it is `e_i+17*1/4` and
`8*1^T/39-4*e_i^T`. Every coordinate is nonzero and the pairing is one.
This covers all48 complementary rank-one calls. Each local copied update
removes exactly h original identity width-h cleanup calls and adds h rank-one
complement calls, retaining every other actual fixed-profile occurrence.

## Why the data certificate applies to the actual fixed family

Let `R=[0..22,22,0..22]`, `C=[0..22,0,0..22]`,
`beta_i=i mod25` and `gamma_j=(j+3) mod25`. After nonzero row and column
scalings the 47-square null corner for each actual source-triple pair is

```
M_ij=[R_i=C_j]/z_(R_i)+[beta_i=gamma_j]/w_(beta_i)-1.
```

The actual diagonal weights z and w are the two dimension-specific product
classes above. The prescribed sequence has47 pivots, including a run21 and
run17. The corresponding physical blocks are rows1..21/columns553..573,
rows28..44/columns530..546, and middle47..527 of width481. The resulting
data profile is `9*[1]+[21,17,481]`.

Two logically different facts are required. The inherited PR34 all-weight
rank-cut identities prove every ordered zero; zeros seen modulo a prime
are regression evidence alone. Exhaustive modular nonvanishing proves all
ordered rational prefix minors for the actual fixed source family. With
both factors fixed there is no unrestricted GL23 parameter and no generic
finite-product argument. PR40 correctly replaces that argument with the
finite all-pair certificate.

The retained complete run reports all `1771*2300=4073300` pairs,
`191445100` successful prefixes and `1409361800` ordered-zero regressions.
Exactly10 pairs fail at the first prime1000003 and succeed on complete
replay at2147483647; there are no unresolved pairs. Different pairs may
use different witness primes. A complete successful prime replay proves
every rational prefix for that pair nonzero, because all evaluated
denominators are invertible. A common runtime address prime is chosen
separately outside the finitely many bad denominator/minor factors.

I inspected the C++ fallback logic. Each retry constructs a fresh matrix
and fresh elimination state; failed prefixes are neither skipped nor used
as filters. The nested loops enumerate all strictly increasing triples
and their entire Cartesian product. A pair is counted only after the full
47-pivot sequence succeeds; an unresolved pair returns failure. All count
assertions are present. At the 31-bit fallback prime, residue multiplication
and matrix initialization use signed64-bit arithmetic; residue subtraction
and conditional correction stay within signed32-bit range. No overflow gap
was found in the inspected operations.

The default Python verifier replays all10 recorded fallback cases over
exact Q. The independent upstream Python fallback audit additionally checks
the lexical pair indices and reconstructs each primary and fallback replay
from scratch. These are reported source-author checks, not new scout runs.
The original C++ source hash is
`8ea33ecedfad214e193aa0beb96f8597d1cdb372481a16a3c36f7f0f58247866`,
and retained deterministic output hash is
`053fe39a680bbde21e162b55fd49c286c68559f22221c56d5229531ceee5d505`.

## Obligations for a changed computation DAG

Changing the internal graph while keeping source triple projectors, metric,
local bases, physical permutations and boundary restrictions unchanged
does not change the data matrix. The source-bound fixed data certificate can
therefore be reused through the exact arbitrary-matrix transfer identities.
This reuse needs an explicit check of those unchanged inputs, rather than a
new full replay solely because the internal association order changed.

Both local profiles must be reconstructed from the new actual original
envelopes, matching and physical transition multiset. A backward-positive
rank histogram cannot be inserted into an original-envelope fixed profile.
The new centers must satisfy the complete copied-stream, terminal read-only,
dirty-scratch restoration and endpoint cancellation contracts. All copies,
corrections, row/spectator volumes and setup calls remain paid. The exact new
moment and all characteristic/assembly inequalities must be recertified.

PR40's h23 fixed-profile CRT bound has115 bits, while its five-prime product
has141 bits. The all-minor bound must use the actual per-matrix denominator
for clearing; `D_upper` is a magnitude bound, not a common denominator.
Ordered rational rank recovery uses maxima of northeast ranks across primes,
not a union of pivot positions. These concerns were specifically checked in
the source's independent h23 review. A new profile must reestablish them.

The upstream full `make verify` receipt completed13:23:26 UTC with exit0,
203 regression tests,18 historical patch checks, fresh complete data replay
and fresh five-prime h23/h25 profiles. Our source review found no additional
data-interface gap. It does not establish all-size analytic, machine/tape,
strict absorption or eventual-cutoff hypotheses, nor any global optimum.

The source additionally records an optional `L23=I+tJ` family. It could be a
new finite search direction, but is not a free substitute for t=1: old
fixed-only zero minors may become nonzero, and all new fixed profiles and
data prefixes must be rebuilt. No gain from that parameterization is claimed.
