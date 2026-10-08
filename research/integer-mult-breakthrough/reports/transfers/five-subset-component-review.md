# Independent review of mixed pair centers and a weighted side DAG

Status: **EXACT FINITE COMPONENT REVIEW** with scoped source-level acceptance.
The new weight-five construction remains a hypothesis. No full side compiler,
native moment, Gaussian precision bound or larger kappa is accepted here.

## Paid copied centers resolve the apparent gather mismatch

The first review question was whether eliminating singleton centers by
`G_i=(1/4)*sum_j P_ij` introduced a gather from a pair-star frame to a target
outside that frame. Such a gather would fail in a strictly nested direct
implementation. That concern does **not** apply to the proposed copied-center
implementation: every designated center is copied and its complete stream is
transformed to the common target background before any scatter read.

The source contract is the PR36
[copied-center lemma](https://github.com/CrocSwap/integer-mult-bounds/blob/11817ccacb564bb7f98789c20dc11d3fece207e3/notes/copied-centers-lemma.tex),
at commit `11817ccacb564bb7f98789c20dc11d3fece207e3`, credited there to
icekylinx and the retained Paureel copy/transform/read/discard interface.
The scoped acceptance uses that actual paid sequence:

| Orientation | Original | Complete copy | Scatter | Original continuation |
|---|---|---|---|---|
| Forward | remains at D_U | D_U to D0, rank r | all reads at D0 | D_U to D1, rank h-r |
| Reverse complementary | D0 to D_Uperp, rank h-r | D_Uperp to D1, rank r | all reads at D1 | already at its inverse-mixer frame |

The copy retains every control/spectator field and coefficient, with exactly
the original role-stream volume. Copies are processed sequentially using one
fixed work stream, and copying, reads and erasure are charged linearly in that
complete volume. The rank-r copy transform remains a recursive child. No new
row coordinate or cropped payload is admitted. Each center has a distinct
terminal output-use carrier with no subsequent producer consumer bypassed.
These are required premises, rather than claims supplied by scalar algebra.

The two orientations replace return ranks `(r,h)` by `(r,h-r)`. The total new
return mass is h; the saving relative to the old return is r. For all but two
pair features `r=h-2`; the two complements have `r=h`. Therefore their local
center loss is exactly

```text
(binom(h,2)-2)*(h-2)+2*h = binom(h,2)*(h-2)+4.
```

Discarding a total or singleton **designated center** does not authorize
discarding any internal dirty carrier still needed to construct the surviving
features. Its scalar gates, frame transitions, retirement and cleanup belong
in the actual future side/gather compiler and role count.

## Exact auxiliary phase-array controls

The independently authored
[checker](../../code/transfers/copied_center_review.py) imports no old or
complex-track producer. It uses an exact auxiliary binary quadratic-phase
model: `C_Q=H^-1 diag(i^q_Q) H`, with unnormalized Walsh H and an explicit
dyadic inverse normalization. For complementary symmetric projectors,
`q_Q+q_Qperp=weight` modulo four, so `C_Q C_Qperp=C_I` exactly.

Four worker processes check pair-star and complement centers at h=8 with
arbitrary Gaussian-dyadic dirty values. There are 1,024 complete records,
each with four payload fields. Both literal copy orientations agree with the
old read values and original endpoints. Missing the copy transform and
cropping three payload fields both fail. Copy and erase volumes are recorded.

This verifies the component operator identities in a declared finite model.
It does not regenerate the inherited Gauss normal-form compiler, actual
fixed-tape schedules, arbitrary h phase endpoint program or its numerical
guard. Original auxiliary endpoint phases are retained; logical dirty values
restore under those frames, rather than an uncharged physical dephasing.

## A required eight-bit denominator allowance

The scalar substitution creates a concrete guard obligation. For target S,
write

```text
alpha_ij = (1/4)*[ij subset S] - (3/32)*|ij intersect S|,
gamma = 3/8 + sum_replaced alpha_ij.
```

Substituting the recovered total `T=(sum P-sum D)/8` gives scatter weights
`alpha_ij+gamma/8` on unreplaced P, and `-alpha_ij-gamma/8` on D. With
`h=10`, `S={0,1,2,3,4}`, replacements `{0,5}` and `{6,7}`, the unreplaced
pair `{8,9}` has coefficient **9/256**. The checker independently verifies
the substituted central polynomial on all 252 source columns.

Thus a seven-bit denominator allowance inherited from PR36 is insufficient;
the new scatter can require eight bits. A literal implementation must account
for its dyadic scaling gates and rebuild its actual scalar gate bound G and
guard E. Because these are fixed finite coefficients, the observation is not
itself an asymptotic obstruction. It prevents silently inheriting an unchanged
precision certificate. The two-factor endpoint generator also changes integer
weight from 9 to 25; its fourth-root/translation correction must be updated
and charged in the new complete ledger.

## Independent side-DAG radical witness

The complex track separately constructed a weighted intersection side DAG.
For a node let U be the span of its contributing input labels, M the span of
all downstream target labels, and H=Mperp. A nested nondegenerate piece frame
would require `U subset Fnode subset H`. If a nonzero vector v belongs to
`U intersect rad(H)`, it belongs to Fnode but pairs to zero with every vector
of Fnode. That contradicts nondegeneracy.

Since `rad(H)=M intersect Mperp`, an exact witness needs only three checks:
v is in U, v is in M, and v is orthogonal to M. Irreducibility or numerical
rank guesses are unnecessary.

The serialized [input DAG](../../fixtures/transfers/weighted-tree-h8-frame-witness.json)
was exported from the complex track's pinned source hash. The independent
checker reconstructs all source supports and downstream target sets from
its explicit chronological edges. It checks all 3,136 weighted output entries,
including the required zeros, without calling that producer. At node 28:

```text
U basis = [151,87,12]
M basis = [211,31]
v = 204 = 151 XOR 87 XOR 12 = 211 XOR 31.
dot(v,211) = dot(v,31) = 0.
```

The common kernel has dimension six. Hence this node cannot have the required
nested nondegenerate frame. A corrupted zero witness is rejected. The witness
is a scope-specific obstruction to this ordinary piece-DAG embedding, rather
than a lower bound for scalar intersection circuits, all Gaussian phase
programs, copied common-background reads or arbitrary symmetric quadratic
frame changes. Those different architectures need their own costs.

## Review outcome and continuation

The mixed-pair scalar feature reduction and paid common-background copied
reads survive this review as components under their named premises. The
necessary denominator and endpoint updates remain explicit. The actual
weighted-tree side DAG has an exact local obstruction under the nested frame
implementation, so its scalar sharing counts cannot be promoted to a phase
primitive unchanged.

The next promising direction changes the phase frames or side chronology,
then reconstructs the full child histogram, dirty word, complete copy stock,
precision, routing and outer transfer. The new row-budget mechanism may also
permit same-width children, but it cannot compensate for a missing local
native program or an omitted payload charge.

## Reproduction and credit

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/copied_center_review.py \
  --workers 1
```

The four-worker run adds `--workers 4 --output` and a fresh ignored JSON path.
The only non-code input is the serialized fixture, which includes generator
and source-result hashes. The weighted intersection recurrence is attributed
to Kaski, Koivisto and Korhonen, arXiv:1208.0554v1, and the complex track's
independently authored implementation. The reviewer wrote this checker and
analysis with AI assistance. Internal independent review is not external peer
review or formal verification.
