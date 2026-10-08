# Independent review: a global tensor-axis choice

A single fixed tensor-axis permutation improves the grouped interchange
construction on the accepted h51 R502265 bit network. With exact rotated
data profiles, the independently certified primitive saving is

`a=7995389364283801/10^24`.

The two-family version alone supports
`a=7532290048832643/10^24`. Both exceed the previous fixed-axis
three-family saving `5385522401708297/10^24`. These are primitive
interchange exponents `tau=1-a`, not composed multiplication savings.
The construction changes the fixed rational bit address table; it does
not insert a coordinate-gather operation into the physical recursion.
The scalar network and separate complex arithmetic circuit are unchanged.

This report extends the accepted [contiguous-pivot transfer](review-contiguous-pivot-transfer.md)
and [data-family review](review-pivot-extension.md). It uses the original
manuscript at `bcd4ebde8692383539f8a48734e5fbf3a18a32c2` and the
independently accepted h51 finite input. The campaign began at
2026-10-07 22:25:21 UTC; the original 08:25:21 UTC deadline and the user's
active 10:00:00 UTC extension are retained in the protocol.

## One basis choice for the complete frame system

In the original tensor order, an ambient coordinate is `(i,j,k)`.
Choose the new order `(k,i,j)`, so that

`old_index=i*h^2+j*h+k` maps to `new_index=k*h^2+i*h+j`.

Let C be this fixed permutation matrix. The tensor metric
`(I-J/9) tensor (I-J/9) tensor (I-J/9)` is invariant under C.
Thus C is a rational orthogonal isomorphism for the ambient bilinear form.
Every source, gate and sink matrix M is replaced *simultaneously* by
`C*M*C^-1`. Rational frame Gram determinants, nondegeneracy, inclusions,
orthogonality and edge ranks are preserved. Scalar pointwise gates and
their physical roles are unchanged. Since the original routed endpoint
differences are I, the new endpoint differences are still exactly I.
The original common-frame proof therefore implements the same external
shear `H<-H+D` on arbitrary payloads and scratch rows.

This is a change in how the fixed address program is defined before
execution. Each new edge matrix is factored and implemented directly in
the existing field order. C is never applied to an array as a runtime
adapter. In particular, arbitrary pivots still cannot be gathered for free.
Only increasing consecutive row/column pairs in the new partial
permutation are concatenated, using the proved componentwise field updates.

Changing only a source, gate incidence or sink would break the common-frame
identity. The complete small-array discriminator changes all incidences
and reproduces the original output exactly; omitting one incidence
conjugation fails on all eight dirty probes.

## The new fixed prime and tape alphabet

Although C preserves the rational frame determinants, the canonical
lower/lower triangular-factor table changes. A different fixed odd prime
q may be needed. Choose q outside the finite set dividing any denominator
of a new assigned frame or factor, and outside the finite set dividing a
nonzero diagonal numerator of a triangular factor. The original
section-04 matrix-shear lemma then applies over `Z/q^b Z` to every new
fixed matrix, for every width b. This is the same finite-table prime
selection argument as the original lemma, applied to the new table.

There is one finite q for the complete bit primitive, not a prime selected
for each input width or each recursive call. The finite tape alphabet can
encode its q address symbols with a fixed `ceil(log2 q)` bit overhead
alongside the binary payload and descriptor symbols. The original
binary/radix stream conversion permits any fixed q with these properties;
its setup and width constants may change but its asymptotic cost does not.
The pointwise scalar circuit still computes in characteristic two, while
the address projections and ranks remain rational. No reduction of the
rational frame proof to characteristic two is used.

The complete giant new factor table and a numerical value of this new q
were not materialized. Their deterministic finite construction and prime
selection are part of the fixed-program setup, as in the original theorem.
Their constant thresholds must be retained as eventual thresholds. They
are not claimed to be covered by a displayed numerical cutoff without an
explicit constant bound. The separate h28 complex circuit, its factors and
its semantic numerical guard are unchanged; its arithmetic table is not
recomputed from this rational bit basis.

## Every middle rank becomes an h-squared batch

The middle terminal residual becomes

`(I-P_t) tensor I_(h^2)`.

Write s0=h^2. For the base h-dimensional complement `I-P_t`, the
rightmost lower/lower profile is known exactly: diagonals i<a, pivot
`(a,h-1)`, diagonals `a<i<h-1`, and a zero last row, where a is the
least coordinate of the triple. The profile of the tensor product with
`I_s0` consists of

`(i*s0+k,j*s0+k)`, for each base pivot `(i,j)` and `0<=k<s0`.

To see this directly, each suffix coordinate k has an independent copy
of the base elimination, and operations between different k never
interact. Equivalently, tensor the lower/lower factors of the base matrix
with I_s0; they remain invertible lower matrices, and the canonical
partial permutation is the displayed tensor product.

Each base pivot supplies one increasing contiguous block of length s0,
including the offdiagonal base pivot. Therefore *all* middle rank is
partitioned into h^2-sized children. Larger consecutive diagonal blocks
are simply split at those boundaries. The precise least-coordinate
frequencies no longer affect this family's moment:

```text
T_middle=(R+h)*v^2*h^2*(h-1).
middle_child_count=T_middle/h^2.
M_middle=T_middle*log(h^2).
```

No arithmetic update is changed to addition modulo `q^(h^2*b)`.
Updates remain separate modulo `q^b`, and only their intervening field
interchanges are concatenated.

## The joined uncapped bound survives the rotation

Originally, a joined edge has residual `I-P_E-P_K`, where

```text
E=F tensor line(t_A) tensor line(t_B)
K=line(t_B) tensor line(t_piA) tensor F.
```

The matching has rational intersection one, so E and K are orthogonal.
After the axis cycle,

```text
E'=line(t_B) tensor F tensor line(t_A)
K'=F tensor line(t_B) tensor line(t_piA).
```

The universal low-rank proof is independent of coordinate order. The
joined matrix still has rank `m-2h`, at least `t=m-4h` diagonal pivots
and at most `g=4h+1` diagonal runs. There are still
`J=(R+h)*v^2` physical joins, disjoint from middle auxiliary terminal edges.

Use K' for the short-run proof: the residual annihilates
`e_i tensor t_B tensor t_piA` for every i. Its earliest support columns
are `i*h^2+h*min(B)+min(piA)`. The exact suffix-rank argument excludes
them from the canonical pivot profile. These h holes are spaced h^2
apart, so every increasing contiguous joined run has length at most
h^2-1. The uncapped Jensen moment

`M_joined>=J*t*log(t/g)`

therefore remains valid without adding h to the run-count bound. No
assumption that the old E kernel stays in the same coordinate positions
is made.

## Exact rotated data profiles

The disjoint stage3 X `in->2` and Y `0->1` data residuals become

`(I-P_t3) tensor (I_(h^2)-(P_t1 tensor P_t2))`.

Both parentheses mean complementary projections; the second is
`I_(h^2)-(P_t1 tensor P_t2)`. It has rank h^2-1 and a rank-one
complement. Its indicator u has nine nonzero coordinates. Its dual v
has no zero coordinates because the individual triple dual entries are
2/6 or -1/6. The same rank-one profile lemma applies. If
`k=h*min(t1)+min(t2)`, its increasing run lengths are the positive members
of `k, h^2-k-2, 1`.

Let Pi3 and Pi12 be the two complementary-projection profiles. Tensoring
their lower factors gives a valid lower/lower factorization of the data
residual, so its canonical profile is exactly `Pi3 tensor Pi12`. Each
of the h-1 base pivots repeats the suffix runs above. This also holds
when a base pivot is offdiagonal: adding its constant row and column
offsets preserves increasing consecutive pairs. The suffix zero final row
separates neighboring base blocks. All runs have length at most h^2-2.

Put `f(a)=C(h-a-1,2)` and `k=h*a+b`. The exact rank-log moment from
the 2N data edges is

```text
M_data = 2*v*(h-1)*sum_(a,b) f(a)*f(b)*[
              k*log(k)+(h^2-k-2)*log(h^2-k-2)]
```

with zero terms omitted. The singleton pivot has logarithm zero. The
rank identity is exactly
`2N*(h-1)*(h^2-1)`, as before. This family is disjoint from the middle
terminal and joined auxiliary families. Every other pivot remains an
individual child.

A separate conservative source row uses the universal low-rank data
diagonal bound and an explicit h^2 cap. It is retained independently;
the exact tensor profile supplies the stronger displayed saving. The old
third-axis data holes are not silently carried across the basis cycle.

## Uniform recurrence, rows and exact characteristic

Here h=51, v=20825, m=132651 and R=502265. The entire original rank
sum is unchanged:

```text
W=453752231686250
s=60190685022033566875
D=W*m-s=2263379181875.
```

All middle children have r=h^2=2601; joined children have r<=h^2-1;
exact data children have r<=h^2-2. Unchanged pivots have r=1.
Thus `r*floor(e/m)<=e/h<e`, and depth is at most `ceil(log_h e)`.
The grouped arbitrary-width tail schedule, complete row split/merge,
active bitmap restoration and fixed-tape parking transfer from the earlier
report apply with the same depth bound. Each child still uses logical
volume V/W. No padded volume proportional to the batch width is inserted.

Complete row divisibility by `W^ceil(log_h e)` is supplied by padding an
untouched reservoir by at most a factor two after it exceeds that divisor.
For e<=C*p with fixed C, W<2^49 and p>=max(2,C), it is sufficient to have
`ell>100log2(p)`. The retained `ell>=p^(1-epsilon)/2` gives this eventually.
The new q and factor-table width constants only change the fixed C/setup
threshold; they do not change its asymptotic exponent. A final composed
cutoff must retain these eventual qualifications.

Let M_lower be the proved middle, joined and exact data rank-log moments,
and let `L_upper=log(m)_upper`. Independent 64-term rational logarithm
enclosures yield

```text
s + a*(s*L_upper-M_lower)
  + a^2*s*L_upper^2/(2*(1-a*L_upper)) < W*m.
```

This is the correct positive-exponential characteristic bound and proves
`sum n_r*r^(1-a)<W*m^(1-a)`. The exact chosen a is truncated below a
96-step rational root bracket on a 10^-24 grid. The complete certificate
retains a strictly positive rational gap. Thousands of distinct data logs
are first rounded *downward* from their proved lower bounds to the common
dyadic denominator 2^256 before summation. This controls artifact size
while preserving the inequality; no floating-point threshold is used.

Three independently supported variants are retained:

| Physical subset | Certified a |
|---|---:|
| Rotated middle and joined | 7532290048832643/10^24 |
| Above plus conservatively capped data | 7719575247586207/10^24 |
| Above with exact data tensor profiles | 7995389364283801/10^24 |

The source does not optimize the complex characteristic or compose final
layer margins. A fresh explicit-a assembly is required; the earlier
uniform expression `1-log_m(s/W)` does not describe these grouped calls.

## Executed controls and recovery

The [fresh source](../code/review_axis_batching.py), SHA256
`b9c7937028c655bd57437ab2b2c4a73358d1ae4a379c28fbf8a1e5320c7ff707`,
and [run](../runs/20261008T0506Z-review-axis-batching/protocol.json)
independently construct six full middle matrices at h6/h8, totaling 1,884
rank pivots. Every pivot profile equals the predicted base-profile lift,
and every middle rank is in h^2-sized groups. Two full joined matrices
check all rotated K kernel holes, ranks, diagonal bounds and maximum runs;
their complete metric invariance checks contain 308,800 entries. Two
full data matrices verify the exact Kronecker profiles, suffix run lengths
and inclusion of offdiagonal base blocks.

Eight complete arbitrary dirty two-role array probes compare the original
and simultaneously conjugated common-frame programs. All 23,328 output
payload entries agree with the same external shear and role swap, with
two spectator prefixes. Missing one conjugated incidence fails in all
eight cases. This is an independent frame-interface discriminator, not
a replay of the old finite scalar graph.

The [certificate](../runs/20261008T0506Z-review-axis-batching/results/certificate.json)
has SHA256
`6b0a6fcf470753341bed22374f68e67b2f5631a605a4202a33bd199903fa18c6`.
Execution was terminal PASS in 4.76 seconds, one CPU worker,
Python 3.14.7, 38,440 KiB peak RSS, no swap, seed643 and a 120-second
timeout. The owned reservation was released in finally. The protocol
pins the accepted finite identity, dependencies, command and external
log path. Reproduce it with a fresh output path.

No giant new factor table, global prime or multiplication machine was
materialized. The all-size result is the proved simultaneous frame
conjugation and tensor-profile construction, combined with the previously
accepted physical grouped-interchange and fixed-tape transfer. Parent
publication owns the commit, push and remote verification. All executed
source and result bytes remain unchanged.
