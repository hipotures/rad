# Partial-overlap Fourier ranks and a separable copied-query budget

**EXACT CHARACTERISTIC-ZERO RANK FORMULA; REFUTED WITHIN A FIXED QUERY
INTERFACE.** All odd-k scalar identities below are independent mathematical
derivations. The copy charge has additional explicit architectural premises.
It does not establish a general circuit or integer-multiplication lower bound.

## Response ranks

Let k=2t+1 and F_k(r)=binom((r-1)/2,t). In one k-cube, sources are bit labels
z in {0,1}^k. A target overlaps a fixed support J of j<k source pairs and
chooses signs alpha in {0,1}^j. The response is

    D_J[alpha,z] = F_k(j-|alpha XOR z_J|).

Every omitted source bit is retained as a spectator. The square j-bit kernel
has the same row rank as this complete rectangular response.

First consider the full cube. For relative signs d_i=+1 on matches and -1
otherwise, its kernel has the Walsh expansion

    F_k(r) = 2^(1-k) sum_(L subset [k], |L|<=t) product_(i in L) d_i.

To prove it, sum coefficients of degrees0 through t in
(1+x)^r(1-x)^(k-r). Each coefficient is a polynomial in r of degree at most
its index. At every positive odd r<k the degree-k polynomial has symmetric
coefficients, so this half sum is half its zero value at x=1. At r=k it
equals2^(k-1). These t roots and the endpoint determine the degree-at-most-t
polynomial F_k uniquely. Equivalently, the full kernel's Walsh eigenvalues
are2 on degrees0 through t and0 above t.

For a j-bit overlap, set the k-j absent relative signs to -1. For a Walsh
character of degree l the coefficient becomes

    2^(1-k) sum_(a=0)^(t-l) (-1)^a binom(k-j,a)
      = 2^(1-k) (-1)^(t-l) binom(k-j-1,t-l),

where an out-of-range binomial is zero. The identity follows directly from
Pascal's relation and cancellation of adjacent terms. Thus its eigenvalue is
2^j times that coefficient, and the exact rank is

    r_j = sum_(l=max(0,j-t))^min(t,j) binom(j,l).

Walsh is invertible over Q/C. This reasoning requires characteristic zero
(or separately controlled coefficient/unit conditions); no all-field claim
is made. Different finite characteristics can annihilate binomial factors.

| k | Ranks for j=0,...,k-1 | Raw rows per cube | Independent rows per cube |
| --- | --- | ---: | ---: |
| 3 | 1,2,2 | 19 | 13 |
| 5 | 1,2,4,6,6 | 211 | 141 |
| 7 | 1,2,4,8,14,20,20 | 2059 | 1429 |
| 9 | 1,2,4,8,16,30,50,70,70 | 19171 | 13981 |
| 11 | 1,2,4,8,16,32,62,112,182,252,252 | 175099 | 133893 |

Here raw rows sum to3^k-2^k, and independent rows sum to
L_k=sum_(j=0)^(k-1) binom(k,j) r_j. The k5 count141 independently recovers
the earlier [live/parked cap inventory](paired-cube-cap-compatible-channels.md).
All proper responses together have joint Walsh span of dimension2^(k-1):
only degrees at most t occur, and successive supports recover every such
character. A smaller joint span alone does not provide a shared physical
query circuit.

## The precise copied-query interface

Assume p>=k+1, so all highest proper overlaps are realized outside the source
cube. Prepare the source bank at one common rank-(k+1) frame Q. For every
proper nonempty support J and target-sign parity sigma, the scalar response
is supplied solely through separately normalized complete copied records
from that bank to E=Q intersection T-perp. Here dim(E)=k, so every such
compiled copy/normalization call has width1. All same-J/sigma target readers
may share those copies. Copies are not shared between distinct query
hyperplanes, moved between them for free, or replaced by direct reads from
mixed source helpers. This is an explicit separable copied-query model.

Odd intersections have zero response. Accordingly D_J splits into two
disjoint parity blocks. Simultaneously flipping one input and output sign
permutes those blocks, so each has rank r_j/2. Within each query hyperplane,
the scalar read matrix of one independent copied row has rank at most1.
Thus at least r_j/2 such copied rows are needed, even when each is read by
many targets. The two hyperplanes together need at least r_j paid copies.
This counts independent records, not distinct readers. Complete Gaussian
fields have the same required coefficient map; arbitrary dirty seeds and
their cancellation cannot increase the source signal rank of a copied row.

The existing copied-center lemma permits many readers of one complete
stream and is consistent with this premise. It does not justify charging
one stream per target. Shared actual copied frames, evolving records,
address-dependent encodings, paid row/field packing, and mixed geodesic
preparation are outside the present interface and require their own ledger.

## Highest proper overlaps already exhaust the deficit

For j=k-1, r_j=binom(k-1,t). There are k such supports. Even ignoring every
smaller overlap, additional root stock and center loss, the three-core
width1 query bill is at least

    A_k v,  A_k = 3k binom(k-1,t)/2^k,

where v=2^k binom(p,k). At k3 this equals(9/4)v. Moreover

    A_(k+2)/A_k = (k+2)/(k+1) > 1.

Hence the copied-query bill exceeds2v for every odd k>=3. The retained
source/target/correction master has at most2v deficit before paid center
copies. Additional geodesic roles enlarge stock and endpoint rank equally;
they do not fund this excess. Therefore the separate fixed-Q copied-query
architecture has nonpositive first-moment slack and cannot supply any
positive b. This conclusion uses the stated fixed master and query bill.

The [singleton quotient component](../synthesis/singleton-quotient-roots-and-paid-copies.md)
motivates this discriminator: a k5 singleton-only copied bill can be smaller
than the direct fanout charge, but the unpriced highest proper groups already
block a separate-query extension. Its new constructive protocol remains an
independent component. Changing actual source preparations, query frames or
the coupled master changes the premise and remains a research direction.

## Finite evidence and reproduction

The independently authored
[runner](../../code/obstructions/partial_overlap_fourier_rank.py) imports only
the Python standard library. Full run `20261009T123755Z-partial-overlap-fourier-rank`
uses four workers and checks k3,5,7,9,11. It retains all full and partial kernel
values and every Walsh eigenvalue, including zeros, with exact inverse
controls. Separate rational elimination checks both parity blocks through
j5. For k3,5,7 it explicitly checks all complete source/target entries on
every canonical proper support: 56,992 and16,256 entries. Wider cases use
complete kernel diagonalization, not explicit rectangular matrices.

The negative control rejects replacing rank by the number of target rows.
Every compact output, source hash, protocol, timing and original execution
log is retained. Timing is diagnostic only. No physical Gaussian pipeline,
native supplier, formal proof assistant or larger kappa is certified.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/partial_overlap_fourier_rank.py --workers 4 --output NEW_OUTPUT_DIRECTORY
python3 -B research/integer-mult-breakthrough/code/obstructions/partial_overlap_fourier_rank.py --workers 1 --bounded
```
