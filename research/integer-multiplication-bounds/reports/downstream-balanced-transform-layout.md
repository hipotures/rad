# Balanced chunks in the synthetic transform

Campaign `20261007T222521Z`, immutable interval
`2026-10-07T22:25:21Z` to `2026-10-08T08:25:21Z`.

This is a changed layout construction, proposed independently by the
parent branch and audited here. It replaces the old low-bit remainder
prefix by nearly equal complete chunks. Only the extra leading bit of
each long axis enters the individually processed prefix. The proposed
synthetic-transform cost becomes

```
O(T*p*[d + p*K^(tau-1) + ell*d^lambda']).
```

The old `d*K` term becomes `d`. The named-slot and movement checker passed
3,800 shapes and2,068,936 axis-round chronology checks in4.506 seconds on
one reserved CPU. Independent analytic transfer review is pending. No
upgraded multiplication headline is claimed here.

## Complete positional construction

Retain the original transform parameters: D=d-1 axes, each of length
2^(ell-1) or2^ell, a contiguous polynomial coefficient suffix, and
K=floor(d^c) with1<=K<=ell-1. Put n=ell-1 and q=floor(n/K). Divide n by q:

```
n=q*L+t, 0<=t<q.
```

Split every axis's common n low slots into t consecutive chunks of width
L+1 and q-t chunks of widthL, with the same boundaries on every axis.
Then each width K_j satisfies K<=K_j<2K. Indeed qK<=n<(q+1)K, so
K<=n/q<K+K/q<=2K; the integer ceiling of n/q is at most2K-1.
Widths differ by at most one, including q=1 and t=0.

Move only `(i,ell-1)` for each long axis into the prefix, in increasing
axis order, preserving all remaining relative order. This takes at mostD
single-bit moves. The rest of each axis now consists of q complete chunks.
Reorder chunk labels from axis-major `(i,j)` to chunk-major `(j,i)` by
the original left-to-right selection schedule, using at mostDq-1 swaps.
This schedule is a permutation of the same named slots; it neither pads
the address space nor changes polynomial suffixes.

An unequal-width nonadjacent swap requires one single-bit move and one
equal-width chunk interchange. With an arbitrary spectator gap M and
equal-width fields x,y, the two cases are

```
a0 x M y -> x M a0 y -> y M a0 x,
x M b0 y -> b0 x M y -> b0 y M x.
```

Both are already permitted by the pinned arbitrary-gap interchange and
single-bit movement interfaces. The bit move preserves every other
relative slot order. The following equal-width swap treats that bit and
the gap as spectators, giving exactly the desired unequal-chunk exchange.
Inverse operations in reverse chronological order restore every slot.
Each swap costs O(V*K^tau), since its common width is at most2K and the
additional single-bit move costsO(V). Thus total chunk order/restoration
cost isO(V*Dq*K^tau)=O(V*p*K^(tau-1)), usingD*ell=O(p).
The only prefix construction/restoration work isO(V*d).

## Round chronology and frequency convention

Process the extra leading round h=ell-1 on the long axes individually,
if present. Then process all common levels h=ell-2,...,0 in decreasing
order. There is no low-bit prefix phase. At each common level, the group
with that named slot consists of D consecutive chunks of one widthK_j.
All participating selected bits have the same offset from its low end.
It therefore has complete rectangular shape

```
[P] x [2^K_j]^D x [S],
P*S*2^(D*K_j)=M.
```

Previous/following chunk groups and the prefix are spectators. The group
descriptor specifies K_j and the common offset; the full named-slot table
continues to locate every coordinate. Each original slot `(i,h)` still
writes frequency bit `a_i-1-h`, where a_i=log2(t_i). Long and short axes
therefore retain their original differing frequency significance.

For a forward round, lower named slots encode
`k_i=sum_(v<h)2^v*x_(i,v)`, and earlier processed high slots are branch
bits. The round has the same butterfly pairings and exact twiddle
`E=-sum_i (2r/2^(h+1))*b_i*k_i mod2r`. In the opposite direction,
lower slots have already been recovered before the inverse twiddle and
current butterfly. The original proof of exact operators consequently
remains `L_new*B*F^-` and `F^+*B^-1*L_new^-1`, with the new explicit
positional permutation replacing the old one. This is not a change in
Fourier convention or an uncharged move of whole frequency indices.

## Uniform compact layer for the slightly variable widths

The retained statement writes K=floor(d^c). This construction needs its
uniform extension to supplied widths in

```
floor(d^c) <= K_j < 2*floor(d^c),
D*K_j <= D*ell=O(p).
```

The proof has no material use of equality after reading the supplied
descriptor. All required lower bounds follow fromK_j>=floor(d^c):
K_j/logp tends to infinity; the guarded segments and deterministic repair
use the same uniform eventual cutoff; front/back reservation counts are
no larger; and row ranges contain at least the same number of bits.
Each recursive node retains that round's entire suppliedK_j, globalG and
H=dG. The complex coefficient depth depends on selected-axis recurrence
and the fixed graph rather than chunk width, so its scalar guard is
unchanged. The new compact internal exponent has noK factor.

For descriptor and address bounds, K_j<=ell-1<p and D*K_j=O(p), while
the complete prefix/suffix record count remainsM. Thus the same fixed
comparison bands and O(p) descriptor bound cover all round headers.
Two factors of the fixed bound2 only change implicit constants in any
retained elementary width estimate. Polynomial descriptor work is still
absorbed by the superpolynomial coefficient-record suffix. The machine
reads K_j, validates its displayed band and reuses the fixed tape program;
there is no machine family indexed by an input-dependent chunk width.

Whole-row padding, cyclic role splits, complete front/back field ranges,
pointwise alignment, dirty restoration and local exceptional repair remain
exactly those in the independently reviewed compact layout. Every call
returns with those temporary fields restored before the next transform
operation. Reconstructing them for another round does not create extra
record volume or an input-dependent number of tapes.

The original individual-prefix proof uses exact dyadics on the
2^(-p-s) grid after s<=D kernels, withp+D+O(1)=O(p) bits. It now applies
to at most one prefix round. Each common round uses one completed compact
layer truncation; the signed monomial commutes with component truncation,
and each exact completed round is a contraction. Hence the original
disk-grid format and error less than sqrt(2)*ell*2^-p are retained.
No untruncated intermediate is charged as a contraction.

## Consequence and remaining structural limit

The prefix margin changes from `1-epsilon*(1+c)` to `1-epsilon`.
The geometry requirementK=o(ell) remains the strict feasibility condition
`epsilon*(1+c)<1`; it is no longer a margin that kappa must lie below.
The other final margins, including

```
g2=epsilon*a*c, g3<epsilon*a, g4=a*(1-epsilon),
```

are unchanged. Even discarding g4, K=o(ell) gives
g2<a*(1-epsilon). Combined withg3<epsilon*a this gives the scoped upper
bounda/2. When the complex savingb>4a, the guard has fixed headroom as
epsilon tends to1/2, c tends to1 and q tends toa. The phase inverse's
gamma and cell gaps remain positive. Thus the declared family can
approach a/2 with strict fixed rational parameters if this layout transfer
is accepted. The preceding compact family approacheda/(2+a).

The exact difference is `a^2/[2*(2+a)]`. For current a near3.1e-9 this
is only about2.4e-18 in kappa, a relative gain near1.6e-9. It is an actual
changed layout with a sharper cost bound, but it cannot explain a large
new exponent improvement. The nonadjacent movement margin independently
enforces almost the same ceiling as the CRT margin. Larger progress needs
a stronger bit movement exponent or a genuinely sharper routing/interface
than the current complete-chunk construction.

Source: [downstream_balanced_transform_layout.py](../code/downstream_balanced_transform_layout.py).
Run: [20261008T014406Z-downstream-balanced-layout](../runs/20261008T014406Z-downstream-balanced-layout/).
The source preserves
exact symbolic operations and inverses, exhaustive tiny address patterns,
deterministic larger boundary patterns and forward/reverse named-round
chronology. These are finite controls supporting the written proof; they
do not establish asymptotic fixed-tape costs by execution. Novelty is
unclaimed, and independent transfer review is pending.

The actual movement controls include1,718 unequal-width swaps implemented
as one bit move plus one completed equal-width interchange. The inverse
schedule restores all named slots in every case. The protocol records
executed source hash
`0407be4df42eb01d753f8fb411d6c5b445bdad7f689cbac8e598104a143acb8d`,
ordered command, immutable reference and external log. One useful worker
was reserved from the sixteen-worker campaign pool after a completion and
released on terminal result; no running job was interrupted or restarted.
