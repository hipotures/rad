# Uniform source data for the half-gamma basis

The [complete certificate](gpu-parameter-results/hybrid-half-uniform-data-certificate.json)
certifies all 4,073,300 actual source pairs at the inherited reversed physical
permutation. It uses beta23 = 2/39 and beta25 = 1/57, or independently either
conjugate root beta23 = -1/3 and beta25 = 1/6. Conjugacy preserves every source
coordinate product, as proved in [the basis review](basis-conjugacy-review.md).

For every actual triple T, the first source point has
`p = 1_T - 2/13 1`, `xi = (1_T + 1)^T/2`; its coordinate products are
11/13 inside T and -1/13 outside. The second source point has
`p = 1_T - 1/19 1`, `xi = (1_T - 1/2 1)^T/2`; its products are 9/38
inside and 1/76 outside. All primal and dual coordinates are nonzero,
and both point pairings are one. The second copied center has
`p_i = e_i + 1/19 1`, `xi_i = 9/4 1^T - 4 e_i^T`; all its coordinates
are nonzero. The first factor uses its already reviewed negative centers.

The actual null projector is
`P23 tensor I25 + I23 tensor P25 - P23 tensor P25`. On the first 47 rows
and last 47 columns, divide each row by `p23[r] p25[b]` and each column by
`xi23[c] xi25[d]`. These are invertible diagonal scalings, so every NE
corner rank is preserved. The resulting exact rational matrix is

```
M[(r,b),(c,d)] = [r=c]/z23[r] + [b=d]/z25[b] - 1.
```

The certificate records the actual 25-by-23 coordinate permutation,
lexicographic triple enumeration, full expected 47-pivot permutation and
both disjoint source-index partitions. No physical gather or source-specific
basis permutation is inserted. The expected runs are
`[1,21,1,1,1,1,1,1,17,1,1]`. The 21 block is physically at rows 1..21 and
columns 553..573, the 17 block at rows 28..44 and columns 530..546, using
zero-based indices. The unchanged large-projector middle is 47..527,
of width 481. Thus one data front has exactly 9N singleton calls and
N calls each of widths 21, 17 and 481, with rank mass 528N.

This rational profile is proved by attained lower ranks and CRT upper ranks.
The original two-field exhaustive run retains complete pivot arrays for
65521 and 1000003. Every source pair has the complete expected pivot
permutation in at least one field: the nonexpected sets have sizes 284 and
24, and are disjoint. This supplies every expected NE lower rank over Q.

For the upper ranks, 99M is integer. Enumerating the two inverse weights
in each factor and both indicator values bounds every entry by 7542; this
bound even permits simultaneous diagonal indicators. Hadamard bounds every
minor of order at most 47 by `47^24 * 7542^47`, a 740-bit integer. The exact
product of 24 distinct 31-bit primes, each proved by trial division, has
744 bits and strictly exceeds that bound. For every pair and every prime,
the GPU computes the complete field rook profile, including zero rows,
and compares all 47-by-47 prefix-row/suffix-column ranks against the expected
table. All upper checks passed. Every larger minor is therefore divisible
by the prime product and smaller in absolute value, hence zero over Z.
Together with the attained lower ranks, this proves all rational NE ranks.
No generic zero-cut assumption or union of pivot IDs is used.

The successful source is [gpu_basis_family_crt_wide.py](code/gpu_basis_family_crt_wide.py),
SHA256 `eaa4669e579af3a74618c0d2451aa2df119c1cac1b2337d8179ac72e17a65c59`.
Both GPU partitions passed in approximately 40 seconds. Each prime has
independent CPU/GPU full-pivot controls. The first attempt failed its initial
control because inherited signed32 initialization added p before reduction.
It accepted no field replay. Its source and failure receipts are preserved;
the successful derivative uses signed64 initialization and branch reduction.
Canonical subtraction stays in (-p,p), and modular products fit signed64.

This closes the changed source DATA geometry. The actual local profiles,
center schedule, restriction/compiler interfaces, physical and scalar charges,
bridge and full assembled characteristic remain separate obligations.
No new multiplication saving is claimed by the scout certificate alone.
