# Degree-two five-subset motif: a scoped optimistic exclusion

A natural extension of the bit motif replaces triples by five-element
subsets. Over F2 the incidence gather/scatter gives intersection parity;
off-diagonal side corrections are needed at intersections1 and3. The
rational fitting polynomial

```
P(j)=(j-1)(j-3)=2*C(j,2)-3*j+3
```

vanishes on both neighbor types and has nonzero diagonal P(5)=8. The
question is whether its larger number of labels compensates for its larger
ambient rational dimension. In the retained uniform three-stage motif with
h incidence-center wires, it cannot beat our existing bit primitive, even
if every side role is free.

## Rank and retained rank loss

Let I_j be the inclusion matrix between five-subsets and j-subsets. The
complete fitting matrix is `2I_2 I_2^T-3I_1 I_1^T+3J`. Point and constant
columns belong to the pair-column span: summing pair columns containing a
point gives four times its incidence column, and summing all pair columns
gives the constant column times10.

Decompose that span into constants, point differences and balanced pair
coefficients (pair arrays whose sum at every point is zero). Their dimensions
are1,h-1,C(h,2)-h. Counting inclusions gives the three nonzero eigenvalues

```
lambda0 = (3h^2-78h+475)*C(h-2,3)/20,
lambda1 = (38-3h)*C(h-3,3)/4,
lambda2 = 2*C(h-4,3).
```

For h>=7 the last is positive, the middle has no integer zero, and the
first quadratic has discriminant384, which is not an integer square.
The pair inclusion Gram is nondegenerate on the same decomposition.
Consequently the exact rank is `r=C(h,2)`. At h5/6 the ranks are1/6.
This is the rank of this polynomial matrix, not a minimum rank theorem
for arbitrary fitting matrices.

With v=C(h,5), N=v^3 and m=r^3, the retained label schedule loses r
dimensions at each of h center returns in each of3v^2 invocations.
Thus `L=3v^2*h*r`, and the bit rank deficit is

```
(N-2L)/N = 1-6*h*r/v.
```

For h>=7, positivity is equivalent to
`(h-2)(h-3)(h-4)>360h`. The ratio of the left side to h increases there,
is below360 at h23 and above360 at h24. The small h5/6 rank cases also
have negative deficit. Hence any positive member has h>=24 and r>=276.

Irrespective of side-circuit size, W>=2N. The relative recurrence deficit
therefore satisfies `eta<=1/(2r^3)`. Since r^3>=276^3>2^24 and
log2>2/3, `log(r^3)>16`. Using `-log(1-eta)<=eta/(1-eta)` gives the
all-ground optimistic primitive ceiling

```
a <= 1/[16*(2*276^3-1)] = 1/672786416 < 3111/10^12.
```

The comparison on the right is already a strict rational saving supported
by the independently promoted current triple circuit. Actual side roles,
feasibility restrictions and strict recurrence absorption can only worsen
this optimistic bound within the stated schedule.

## Exact controls and measured failure

[odd_subset_motif_screen.py](../code/odd_subset_motif_screen.py) built the
complete rational matrices at h7/8/9. It checked every diagonal and
neighbor zero and obtained ranks21/28/36 over Q, covering19,453 matrix
entries. Exact count controls at h7..100 agree with the positivity threshold;
the all-size proof above, rather than this bounded sample, establishes it.

The first attempt used symbolic `Matrix.rank` and hit its120-second cap.
Its exact source and timeout evidence are preserved in
[the failed run](../runs/20261008T014008Z-five-subset-motif-screen/).
A fresh [fraction-free repair](../runs/20261008T014346Z-five-subset-rank-repair/)
used `DomainMatrix` over Q and passed the same requested complete grounds
in0.467 seconds including its wrapper. The mathematical inputs and acceptance
conditions were unchanged. This is a measurement of these bounded rank
checks, not a general speedup for research or a claim from a timed-out test.

Reproduce with the pinned SymPy1.14 environment and a fresh output:

```bash
"$PYTHON" -B research/integer-multiplication-bounds/code/odd_subset_motif_screen.py \
  --workers 1 --dense-h 7 8 9 --output "$FRESH_OUTPUT"
```

Different fitting polynomials, mixed motifs, a different center schedule,
fewer central decreases or nonuniform networks are not excluded. The result
redirects this campaign away from implementing this particular large circuit;
no universal multiplication ceiling or novelty claim follows.
