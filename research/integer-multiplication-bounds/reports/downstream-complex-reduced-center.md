# Eliminating one redundant complex central channel

Campaign `20261007T222521Z`, immutable start/deadline
`2026-10-07T22:25:21Z` / `2026-10-08T08:25:21Z`.

The reviewed complex side construction has h point channels C_i and one
total channel C_*. Their gathered increments satisfy
`Delta C_0=3 Delta C_*-sum_(i>0) Delta C_i`. Retain only C_* and C_i for
i>0. This is h channels, and requires no division by three. The reduced
scatter is

```
if 0 is in S: C_* - (1/2) sum_(i outside S) C_i,
otherwise:   (1/2) sum_(i in S) C_i - C_*/2.
```

These are exactly the old scatter after substituting the increment
relation. All coefficients are still 0,+/-1,+/-1/2. Arbitrary initial dirty
retained channels need not satisfy any relation: early and late scatters
cancel the dirty values, leaving only the new gathered increment. Side
scratch and its mixers are unchanged. Thus the forward and reversed
chronological schedules remain exact additive shears with complete dirty
scratch restoration.

Every central register had the same broad labels in the reviewed proof.
Removing a register changes no data boundary or incidence compatibility.
Each surviving register still has one decreasing return of dimension h;
there are now h registers rather than h+1. Source/sink full-bank sharing
matches the same partner-flip invocation map and each surviving center
index. All side frames, terminal witnesses, scalar signs and binary phase
factorizations remain the reviewed ones.

For v=binom(h,3), N=v^3, m=h^3 and side role count R, the revised shared
counts are

```
W = 2N + 2v^2(R+h),
L = 3v^2 h^2,
s = W*m - 2N + 2L,
D = 2N-2L.
```

Relative to the reviewed h+1-channel witness this removes 2v^2 shared
physical roles and 3v^2 h of decreasing dimension. The grouped scalar
gate bound and E=64(W+m+1)^3 guard remain valid: the number of grouped
central gates stays four, and the larger scatter fan-in is at most W
with the same allowed coefficient magnitudes. No new precision primitive
or tape operation is introduced.

The cheap exact checker verifies the old-to-new gather column relation
and every scatter row by symbolic integer coefficients, including all
19,600 columns/rows at h=50. It checks the complete h=8 scalar basis of
1,018 coordinates in both orientations, plus six signed arbitrary dirty
probes. This is sufficient to test the changed part; the previously
reviewed h=50 side DAG is not replayed.

The tight phase/decaying assembly still has exactly the same minimum
margin and kappa as the accepted witness. The complex saving was already
above 4a/(1+a), so the limiting denominator is 1+a+a^2. This rank refinement
therefore supplies headroom for future stronger bit primitives, but is not
an improvement of the current strongest final kappa. The common parameter
cutoff also remains unchanged; a nonlimiting guard cutoff becomes smaller.
Both statements are checked as exact equalities in the result.

Status: producer controls and [independent refinement review](review-complex-refinements.md)
pass. The reviewer independently derives the factorization and arbitrary
dirty-register cancellation, then recomputes the counts, longer logarithm
enclosures, all 30 strict conditions per row and cutoffs. Its
[completed result](../runs/20261008T010040Z-review-complex-refinements/results/reduced-center.json)
matches the exact unchanged tight kappa and common cutoff and passes 680
stopped decaying recurrences. It is a changed finite construction of a
redundant central block. The overall theorem retains every conditional
upstream dependency.

Source: [downstream_complex_reduced_center.py](../code/downstream_complex_reduced_center.py).
The source takes fresh output paths and the read-only bit, complex and
assembly certificates as explicit inputs. Its run protocol records their
identities and the complete command. The only dependencies are the topic's
preserved authored exact-arithmetic helpers and Python standard library.
Run: [20261008T005450Z-downstream-reduced-center](../runs/20261008T005450Z-downstream-reduced-center/).
