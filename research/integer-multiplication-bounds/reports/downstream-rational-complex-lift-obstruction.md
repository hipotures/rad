# A scoped obstruction to lifting the complex labels into rational bit frames

The binary complex labels cannot simply be reused as intersection-invariant
rational bit labels with the same central construction. The required zeros
at intersections zero and two force at least C(h,2) ambient dimensions for
h>=11. Even an optimistic rank budget that retains the larger complex
endpoint saving is then negative. This excludes the stated symmetric lift;
it does not exclude other rational frames, correction circuits or bit motifs.

The campaign clock remains 2026-10-07T22:25:21Z to
2026-10-08T08:25:21Z. The source is the original immutable
CrocSwap/integer-mult-bounds input at
bcd4ebde8692383539f8a48734e5fbf3a18a32c2, particularly its rational
bit-frame and binary complex-frame distinction in sections03 and04.
This is a negative result, not a new multiplication witness.

## Exact rank obstruction

Let v=C(h,3), f=C(h,2), and index labels by triples. Let B be the
triple-pair incidence matrix, C the triple-point incidence matrix, and A
the point-pair incidence matrix. Then C=B A^T/2 and

```
A_1 = C C^T - 2 B B^T + 3 I,
B^T B = (h-4) I + A^T A,
A A^T = (h-2) I + J.
```

Here A_1 is adjacency at intersection exactly one. The first identity
follows entrywise from r-2*C(r,2)+3*1_(r=3), for r=|S intersect T|.
The other two identities follow by counting triples through a pair and
points through two pairs. For h>=5, B has full column rank; A has full
row rank.

Decompose the triple space into constants, lifted zero-sum point vectors,
the pair-incidence space orthogonal to lifted point vectors, and the
orthogonal complement of the pair-incidence space. The four eigenvalues
of A_1, with their dimensions, are

| Eigenvalue | Multiplicity |
|---|---:|
| 3*C(h-3,2) | 1 |
| (h-4)*(h-9)/2 | h-1 |
| 11-2h | f-h |
| 3 | v-f |

These formulas follow from the displayed incidence identities, rather
than a floating eigensolver. For h>=11 the eigenvalues are distinct and
v-f is the largest multiplicity. Every nonzero intersection-invariant
Gram with zeros at intersections zero and two has the form gamma I+
delta A_1. It can annihilate at most one of these four eigenspaces.
Consequently its rank is at least v-(v-f)=f. This lower bound allows
indefinite rational bilinear forms, as used by the retained bit interface.

For illustration, 3I-A_1=2BB^T-CC^T has rank f in this range. Its
pair-space form is 2I-A^T A/4. Its sign pattern is immaterial to the rank
lower bound. Rank sharpness alone does not establish the full nested-frame
transfer. The prototype uses this matrix only as an algebraic control.

## The retained central architecture loses its rank deficit

Give this lift every favorable endpoint allowance: retain 2N with N=v^3,
use the reduced h central channels, and ignore any extra side-frame rank
cost. A full first-factor span has dimension at least f. The three-stage
central losses are therefore at least 3v^2*h*f, yielding

```
D <= 2v^3 - 6v^2*h*f
   = -v^2*h*(h-1)*(8h+2)/3 < 0.
```

The rational bit endpoint allowance is actually smaller than the
optimistic 2N used here. Thus this specific lift cannot satisfy s<Wm.
The argument does not assume that the complex scalar halves are already
valid bit gates; granting them could only make the exclusion weaker.

## Executed evidence and reproduction

[The exact source](../code/downstream_rational_complex_embedding.py)
checks h=5,10,11,12 by finite-field elimination of the integer incidence
matrices, giving certified lower bounds on rational rank. It independently
computes six complete adjacency trace powers and compares them with the
displayed eigenvalues and multiplicities. The h=5 and h=10 controls retain
the two genuine pair-form rank degeneracies. All 54 grounds h=11..64
pass the exact count, multiplicity and negative-deficit checks.

[Run20261008T030607Z](../runs/20261008T030607Z-downstream-rational-lift/)
completed in0.267 seconds with one worker after admission to the current
scientific pool. Source SHA256 is
66c70aa8ea94e257d80329c2dbffcae8e5a1d32f02d2088f9e3c38c653d15664;
the compact result SHA256 is
b66e2134a5c7fcffcf92ff21a5f00fe760f5dd6b27417fedc04d6bf3cc068b75.
The protocol records the exact command, input revision, external logs and
unchanged campaign deadline. A preparatory representative-selection issue
at h=5 was corrected before the first execution: intersection zero is
unattainable there, so only attainable intersection classes are tested.

```
python3 -B code/downstream_rational_complex_embedding.py \
  --upstream /path/to/original-bcd4ebde-input \
  --output /fresh/result.json
```

The all-h conclusion is the incidence proof above. The finite controls
support that proof and preserve its endpoint degeneracies; they are not
a general impossibility theorem for rational bit constructions.
