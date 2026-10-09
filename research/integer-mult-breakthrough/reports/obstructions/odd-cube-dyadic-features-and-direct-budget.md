# Dyadic odd-cube features and the direct source-formation boundary

Status: **EXACT SCALAR COMPONENT, HYPOTHETICAL MOMENT DISCRIMINATORS, AND
SCOPED ALL-SIZE OBSTRUCTION**. The inherited odd-cube polynomial has an
explicit Gaussian-dyadic feature decoder at every odd k. A paid total root
removes the fixed odd denominator in the three-coordinate realization.
Selected optimistic k3 profiles have substantial room at b=0.001, but their
direct pure-source formation is capped below b=0.0002 for every p under
the stated stock and master. Mixing and actual physical integration remain
separate requirements. No own multiplier exponent is established.

## A decoder using only dyadic coefficients

For k=2t+1, retain the inherited scalar polynomial

    F_k(r) = binom((r-1)/2,t),

where r is the intersection size of a source and a target, each with k
nonpartner coordinates. This polynomial and its original paired-cube use
are read-only inputs from
[the existing discriminator](../../code/complex/paired_five_cube_discriminator.py).
The present realization is an elementary Newton expansion; no novelty of
the finite-difference identity is claimed.

Set c_j=Delta^j F_k(0), for 0<=j<=t. The exact identity is

    F_k(r) = sum_(j=0)^t c_j binom(r,j).

Every c_j is dyadic with denominator dividing 4^t. One first-principles
proof uses F_t(r)=binom((r-1)/2,t). Its initial values are
F_t(0)=(-1)^t*binom(2t,t)/4^t and F_t(1)=0 for t>0. Pascal's identity gives

    F_t(r+2) = F_t(r) + F_(t-1)(r).

Induction on t and then r proves that 4^t F_t(r) is integral for all
nonnegative integer r. Finite differences preserve that grid. Polynomial
degree t makes every higher difference zero. The endpoint is one at r=k
and zero at each smaller positive odd intersection.

For each nonpartner coordinate subset I of size j<=t, provide a designated
root with source incidence M[I,S]=[I subset S]. Define
D[T,I]=c_j*[I subset T]. Then

    (DM)[T,S] = sum_(I subset S intersection T) c_|I|
              = F_k(|S intersection T|).

The empty subset is an actual additional total root. It is counted as a
persistent dirty role and needs the same paid copy and restoration as other
roots. It is not an omitted constant or free clean bank. The number of
designated roots is sum_(j=0)^t 2^j*binom(p,j). This sufficient realization
need not use the minimum possible root count.

Examples of c_0,...,c_t are:

| k | Newton coefficients |
| --- | --- |
| 3 | -1/2, 1/2 |
| 5 | 3/8, -3/8, 1/4 |
| 7 | -5/16, 5/16, -1/4, 1/8 |

For k5, the degree-one roots can instead be absorbed into pair roots:
each source coordinate participates in four pairs. The additional total
root and decoder (1/4)[I subset T]-(3/32)|I intersection T| recover the
same kernel. This is the separately proposed complex-track refinement;
the present general profile deliberately retains all degree-one roots.
Restricting a symmetric decoder to top-degree roots alone can introduce
odd factors. That observation is not a universal compression lower bound.

## Finite evidence and optimistic leverage

The independently authored
[standard-library source](../../code/obstructions/odd_cube_dyadic_moments.py)
imports only the pinned exact moment engine, not the complex producer.
Its full four-worker attempt `20261009T115813Z-odd-cube-dyadic-features`
checks nine odd-k grids from3 through19 and all **18,496** scalar matrix
entries in complete paired cases k3/p3, k3/p4, k5/p5 and k7/p7. Omitting
the total feature changes the endpoint and is rejected. These are scalar
matrices, not physical Gaussian address arrays or dirty phase circuits.

The moment discriminator keeps v=2^k*binom(p,k), h=2p, m=3h and the paid
designated root count q. Its optimistic center has one source helper per
input, helper pieces [1,h-1], one full forward root call and one full inverse
on a complete owned copy. Thus R_center=v+q and extra center rank is qh
per core. All width-h calls are proper only relative to master width3h.

The inherited source clock [k-1,h-k-1,1], target clock [k,h-k-1] and both
width-two corrections are retained. Every raw cap and kernel coordinate
is counted. For overlap j>=1 its proposed pieces are
[k+1-j,j-1,h-k], with zeros omitted; j0 uses [k+1,h-k-1]. The physically
available overlaps are j>=max(0,2k-p), and j=k is absent. The rank telescope
is checked exactly, but aggregate formation and a global word are not given.
The single full root transition is an optimistic chronology until an actual
source/target word is replayed.

| Family | v | q | Complete W | Deficit | Upper moment at b=0.001 |
| --- | ---: | ---: | ---: | ---: | ---: |
| k3/p11 | 1,320 | 23 | 7,118 | 1,122 | 0.9991494932 |
| k3/p12 | 1,760 | 25 | 9,485 | 1,720 | 0.9989939640 |
| k3/p16 | 4,480 | 33 | 24,113 | 5,792 | 0.9989347975 |
| k5/p12, uncompressed degree-one roots | 25,344 | 289 | 243,433 | 29,880 | 0.9999879476 |

The quoted decimals illustrate exact outward rational intervals. They are
hypothetical complete profiles, not attained supplier bounds. Selected
k7/p16 and k7/p18 profiles already fail even the dated comparator's
beta-to-zero necessary boundary, so they do not justify a larger sweep.
The less costly k3 scalar kernel is a useful small mixing/splice target.

## Release-aware direct formation cannot supply the advertised saving

Consider precisely the direct family with one pure carried helper per
original cube source, direct scalar writes into each singleton aggregate,
and aggregate frames that grow monotonically to their literal buckets.
Copies, altered births, mixed helper signals, cancellation-created
aggregates and different endpoint stock are outside this model.

A k-cube has N=2^k odd source labels. Each of its 2k singleton buckets has
rank k and contains N/2 such labels. A proper rank-(k-1) subspace contains
at most N/4 odd labels: the nonzero parity functional splits its vectors
equally. Consequently its final N/4 unreleased source writes require the
entire rank-k bucket frame. Any l source helpers that ever drop their own
line are designated released. Each belongs to k buckets, so at least

    F >= kN/2 - kl

full-bucket incidences remain forced among unreleased helpers. Distinct
singleton buckets have the same rank and are incomparable. A helper
visiting r of them pays at least 2(r-1) extra rank above its line-to-full
geodesic. Each released helper pays at least two extra ranks: for its line L
and an intermediate F not containing L,

    distance(L,F)+distance(F,full) = h+1 > h-1.

Summing gives

    extra rank >= 2l + 2 max((k/2-1)N-(k-1)l,0)
               >= [(k-2)/(k-1)]N.

This is the release-aware argument independently developed and finitely
controlled in the
[singleton formation study](../synthesis/pure-source-singleton-fanout-release-bound.md).
The no-release96/112 bound at k5 cannot be substituted for this lower bound
when releases are allowed. At k5 the exact minimum is24 per32-source cube;
across three cores it is2.25v, already above the unspent master deficit<2v.
The same continuous exclusion holds at every odd k>=5 in this direct class.

For k3 the minimum is4 per8-source cube, or v/2 per core. It does not alone
exclude every positive deficit. However, with the retained raw19/8v side
stock, singleton-plus-total roots q=2p+1 and paid copies,

    delta_after_formation <= v/2 - 3qh,
    W >= (43/8)v,  v=8 binom(p,3),  m=6p.

For p=3,4,5 the original deficits before any release charge are respectively
-110,-152,-170. Their first moment already fails; no absent singleton bucket
is invoked. For p>=6 with a positive
deficit, its density has the strict upper bound

    delta/(mW) < 2/(129p) - 12/[43(p-1)(p-2)]
               < (2/129)(1/p-18/p^2) <= 1/4644.

The last inequality follows by maximizing y-18y^2 at y=1/36. Every child
width is at most h=m/3, including full root copies, so for b>=0,

    Phi(1-b) >= [1-delta/(mW)] 3^b
              > (4643/4644) 3^b.

The exact outward lower enclosure at b=1/5000 is greater than
1.00000436766. Therefore this fixed direct k3 family cannot attain complex
saving b>=0.0002 for any p. Under only the inherited balanced inequalities,
it also implies kappa<1/5001. This is a scoped architectural restriction,
not a lower bound for integer multiplication. A different ledger must be
derived from its actual operations.

## Remaining native obligations and reproduction

Even the optimistic scalar/moment positives need complete source formation,
target chronology, all dirty kernel restoration, native copies/erasure and
global numerical guards. The original routing condition
tau*(1+c/beta)<1-b additionally requires an ordinary saving alpha>b when
tau=1-alpha and c>0. A stronger finite complex moment alone does not provide
that ordinary supplier or bypass the separately proved self-bootstrap
restriction. The proposed k3 mixing test and a changed coupled/native route
are independent obligations.
This restriction concerns the unchanged direct interface. It is not a
generic cap on the separately balanced external transfer or every conditional
characteristic.

From the repository root, use a fresh output directory:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/odd_cube_dyadic_moments.py --workers 4 --output NEW_OUTPUT_DIRECTORY
python3 -B research/integer-mult-breakthrough/code/obstructions/odd_cube_dyadic_moments.py --workers 1 --bounded
```

Complete compact coefficients, all child histograms and exact intervals are
retained with the run and copied whole through gzip evidence. The all-size
arguments above are ordinary mathematical proofs with internal agent
criticism, not formal proof-assistant or external peer-review artifacts.
