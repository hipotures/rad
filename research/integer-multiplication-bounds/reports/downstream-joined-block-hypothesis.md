# Proposed sharper joined moment

This report proposes a stronger estimate for joined runs in the accepted
reflected rational program. It is separate from the completed Householder
headline and is not promoted until independent all-size/profile review and
complete arithmetic pass. The program already groups these diagonal runs;
the proposal sharpens its characteristic estimate rather than changing
the scalar graph, factor table, physical schedule or row-depth bound.

In the rotated reflected basis, a joined residual is

`A=I-P_B tensor I tensor P_A-I tensor P_B tensor P_C`,

where the matched triples A,C intersect in one point. Consequently their
rational line projections satisfy `P_A P_C=P_C P_A=0`. All reflected
triple source and dual coordinates are nonzero at h51.

Let `B0=I_(h²)-P_B tensor P_C` and `T=I_h tensor P_A`. Choose proof-only
invertible lower matrices S,R in the outer factor with
`S u_B=u_B[0] e0` and `v_B^T R=v_B[h-1] e_last^T`. Explicitly, S is
unit lower with `S[i,0]=-u_B[i]/u_B[0]` for i>0; R is unit lower with
`R[h-1,j]=-v_B[j]/v_B[h-1]` for j<h-1. Their product D=SR is lower and
has unit diagonal. Therefore

`(S tensor I) A (R tensor I)=D tensor B0-c e0 e_last^T tensor T`,

where `c=u_B[0]*v_B[h-1]`. The canonical lower/lower partial permutation
is unchanged by these proof-only lower transformations. The actual
implementation continues using the original reflected canonical factors;
no additional factor denominators or runtime S/R maps are introduced.

Index outer blocks by i=0,...,h-1, each of size n=h². In the first block
row, every nonzero column lies in block0 or the last block. A rightmost
pivot in the last block has zero value in every interior block row, so
its column clearing and lower-row elimination leave interior diagonal
blocks unchanged. A rightmost pivot in block0 has no rightward tail and
therefore also changes only earlier-block entries. These two types may
interleave: it is not necessary that every spike pivot occur before every
block0 pivot.

Now process any interior outer block i=1,...,h-2. Its entries in all
blocks to the right are zero. Its local diagonal block remains B0. A
rightmost local pivot clears only that block and earlier blocks; a row
whose local B0 part vanishes may pivot in an earlier block, with no tail
in later blocks. Thus elimination of this block leaves every later
diagonal B0 unchanged. Induction gives an exact copy of the local B0
partial permutation in each of these h-2 interior diagonal blocks.

B0 is a rank-one complement whose source has first nonzero coordinate
zero and whose dual has nonzero last coordinate. Its canonical profile
has pivot `(0,n-1)`, diagonals1,...,n-2 and a zero final row. Therefore
each interior block supplies one isolated maximal diagonal run of length
`n-2=h²-2`. The neighboring local rows are not diagonal, so these h-2
runs can be subtracted from the universal whole-matrix run bound.

The accepted universal profile guarantees at least `t=m-4h` diagonal
pivots in at most `g=4h+1` diagonal runs. Put

```text
mass=(h-2)*(h²-2)
t_rem=t-mass
g_rem=g-(h-2)=3h+3.
```

At h51, `t_rem=5096`, `g_rem=156`, and `t_rem>g_rem`. The remaining
rank-log moment is at least `t_rem*ln(t_rem/g_rem)` by Jensen and
monotonicity in the remaining diagonal mass. Hence the proposed joined
moment for `C=(R+h)*v²` physical joins is

`C*[mass*ln(h²-2)+t_rem*ln(t_rem/g_rem)]`.

All offdiagonal pivots contribute a nonnegative moment and can be omitted
from this lower bound. The old universal Jensen moment is retained as an
independent fallback. The maximum joined child remains below h², while
the uncapped middle children still determine the global127449 maximum
and p^2600 row stock. The characteristic uses exact logarithm intervals
with the same strict remainder proof, not a floating-point threshold.

The fresh [small control](../code/downstream_joined_block_profile.py)
constructs the original and concentrated joined matrices independently,
performs exact rightmost elimination, and checks full profile invariance
and isolated interior runs. It also tests the two necessary qualifications:
moving the spike into an interior row can destroy that block's profile;
omitting dense-first-coordinate reflection changes the local complement
profile. Its completed run will be linked when available. No giant h51
profile replay or new finite promotion is proposed by these controls.

## Completed follow-up

The exact controls passed in
[run060824](../runs/20261008T060824Z-downstream-joined-block-profile-repair/results/certificate.json).
The independent all-size/profile audit passed in
[run0603](../runs/20261008T0603Z-review-joined-block-drain/results/certificate.json),
and the strict characteristic and complete parameter producer are
documented in the [characteristic report](downstream-joined-block-characteristic.md)
and [assembly report](downstream-joined-block-semantic-bulk.md). The
historical hypothesis is retained above; final independent assembly
arithmetic remains a distinct acceptance step.
