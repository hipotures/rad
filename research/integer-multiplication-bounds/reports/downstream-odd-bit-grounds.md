# Odd bit grounds: constructive matching and exact small controls

Campaign `20261007T222521Z`; immutable clock
`2026-10-07T22:25:21Z` to `2026-10-08T08:25:21Z`.

Evenness is not a mathematical requirement of the rational bit frame or
first/third auxiliary-bank join. The preserved routines restrict to even
grounds because their explicit matching and globally aligned point order
were written for that case. This report supplies a constructive odd-ground
extension, with full finite controls at h7/h11. It does not promote a new
final exponent or a full h49 side graph.

## A bijection with intersection exactly one

Let h=2r+1 with r>=3, and distinguish z=2r. Pair the remaining points as
P_i={2i,2i+1}. Partition the triples into three invariant classes.

1. For triples avoiding z, use the pinned even-ground matching on 2r
   points. A triple containing a full pair retains its singleton and cycles
   that pair among the r-1 pairs not containing the singleton. A triple
   drawn from three pairs retains the point in the least indexed pair and
   flips the other two to their partners.
2. For `{z,a,b}` with a,b from different pairs, flip both a,b to their
   partners, retaining z.
3. For `{z} union P_i`, replace P_i by P_(i+1 mod r), retaining z.

The first class inherits the original bijection; the second is an
involution; the third is a fixed-point-free cyclic permutation. Each image
intersects the original triple in exactly one point. Reversing the full-pair
cycles and retaining the partner flips gives an explicit inverse. Neither
regularity nor an unproved perfect-matching assumption is used.

The exact checker evaluates forward and inverse images of every triple at
h7, h9, h11, h13 and h49. At h49 the classes have respectively 17,296,
1,104 and 24 triples; all 18,424 images are distinct and satisfy the required
intersection condition. A bijection suffices for shared-bank addressing;
the original bit join does not require an involution.

## An odd root order without changing the preserved recursion

For common point i=z, keep all r global pairs. For common point i!=z,
keep the r-1 unaffected pairs and put the orphan i xor 1 together with z
as the last pair. Each common-point group has n=h-1 even vertices, with
an ordinary paired root and the pinned base4 weighted exclusion recursion.

The fresh adapter keeps `GroupUnion` in its existing natural global input
order. Its local subclass reorders the root points, constructs the same
canonical pair-input dictionary and canonicalizes the unordered output
keys. Therefore it changes neither the local scalar variables nor the
complete requested exclusion map. The inherited global formal-support
interner and dead-node removal are used unchanged. Every addition is still
checked for disjoint support; cross-group interned sums still have their
original common-point/pair-star support certificate.

The adapter is a changed finite graph. It does not merely change the
rounding of an old saving or remove an evenness assertion from a verifier.
All local/global coefficient, target, physical-copy and retained-controller
checks remain enabled.

## Rational frames, endpoints and rank accounting

The form H=I-J/9 has eigenvalues 1 and 1-h/9, so it is nondegenerate for
every odd h other than 9. A triple line always has squared norm2, and the
pairing of two triple indicators is their intersection size minus one.
The new matching therefore gives orthogonal nondegenerate lines.

For a common-point source span, `sum_j x_j=3x_i` and
`x^T H x=sum_(j!=i) x_j^2`. The support envelopes retain the already
reviewed equal-core/sum/support equations; their quadratic form is
`sum_(j outside core) x_j^2+(|core|-1)z^2`. Positivity, nondegeneracy,
nesting, complementary reverse frames and physical-target orthogonality
do not depend on even h. The dense small checker independently solves
those equations over exact rational arithmetic.

At a first/third-bank join, the old tensor labels remain
`E=F tensor <t_A> tensor <t_B>` and
`Hjoin=<t_B tensor t_pi(A)>^perp tensor F`. The matched orthogonality
gives E contained in Hjoin. Both labels are nondegenerate; their nested
residual is therefore nondegenerate over the rationals. The binary
nonalternating condition of the complex phase construction is irrelevant
to this bit join. Here dimE=h and dimHjoin=h^3-h; deleting the separate
end/source edges and installing the join removes one physical role and
exactly h^3 rank, as in the reviewed even-ground proof.

The common scalar schedule and arbitrary-dirty cancellation are unchanged.
The inverse middle invocation uses orthogonal-complement labels. All
surviving auxiliary roles have source0 and sinkI, while data endpoints and
the N negative source projections remain the original ones. For a fully
certified odd ground with actual side-role count R, the same formulas are

```
v=C(h,3), N=v^3, m=h^3,
W=2N+2v^2(R+h), L=3v^2h^2,
D=N-2L, s=W*m-D.
```

A transferred movement saving additionally needs D>0. The h7/h11 tests
are finite calibration cases and do not claim that inequality. A full h49
certificate would have to check all coefficients and physical frames and
compose its own exact saving. The independently accepted complex circuit
may remain at even h50.

## Measured controls and current status

| Finite control | h7 | h11 |
|---|---:|---:|
| Global additions | 303 | 2,397 |
| Partial outputs | 105 | 495 |
| Retained controller links | 47 | 183 |
| Actual side roles | 361 | 2,709 |
| Complete invocation coordinates, each direction | 438 | 3,050 |
| Independently solved dense frame constraints | 296 | 2,210 |
| Forward/reverse physical frame transitions | 1,934 | 15,006 |

Both grounds pass independently reconstructed logical/physical
coefficients, positive envelope and target checks, equation-based
controller-plan checks, complete side-shear dirty bases and both complete
invocation dirty bases including centers. The h7 test also runs two full
three-stage exchanges, seeds1/109, each including all 987,350 physical
coordinates, 3,675 invocations and arbitrary dirty shared/middle banks.
Both complete bank exchanges and every scratch coordinate pass. A full
h11 three-stage replay was not run; the written tensor/scalar argument and
h7 replay are preserved separately from that omitted measurement.

The successful small run took 13.95 seconds on one CPU, with peak resident
memory 138,992KiB and no swaps. Its first attempt used system Python,
passed the h7 constructor, then stopped at a missing NumPy dependency.
The retained repair uses the existing campaign math environment without
changing the source or any check: Python3.14.7, NumPy2.5.3, SciPy1.18.1,
BLAS/OMP thread counts1. The exact maximum flow uses integer capacities;
no floating threshold certifies a frame or count.

Status: producer finite controls and constructive all-odd matching proof
pass; independent review is pending. Full h49 construction is deferred
while the newly announced compact-control movement interface is audited.
No exponent improvement is attributed to these calibration cases.

Source: [downstream_odd_bit_circuit.py](../code/downstream_odd_bit_circuit.py).
Runs: [matching-only](../runs/20261008T012145Z-downstream-odd-matching/),
[successful small controls](../runs/20261008T011530Z-downstream-odd-small-math/),
[retained dependency failure](../runs/20261008T011503Z-downstream-odd-small/).
Their protocols/results preserve immutable upstream and authored helper
hashes, exact commands and external execution/resource log locations.
