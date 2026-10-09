# Coupled transfer boundary from off-diagonal cut ranks

Status: **INDEPENDENT SCOPED ANALYTICAL DEDUCTION**. This allows arbitrary complex coefficients, nonunit operations and cancellation. It restricts the actual inverse-input/output block cut ranks in a stated coordinate order. It is not a universal scan, permutation, fixed-tape or multiplication lower bound.

## Scalar block lemma with exact C phases

Let D=2^f, d=D/2 and write the full C tensor in its highest-bit midpoint split:

```text
F_f = [[alpha G, beta G], [beta G, alpha G]],
G=F_(f-1), alpha=(1+i)/2, beta=(1-i)/2.
```

Both alpha and beta are nonzero and G is invertible. Let `Y=F_f X` and partition `X=[[A,B],[C,D0]]`. Suppose both off-diagonal blocks of X have rank at most r_in and both off-diagonal blocks of Y have rank at most r_out. Set `t=alpha/beta=i`. The two exact off-diagonal equations give

```text
A = beta^-1 G^-1 Y10 - t C,
D0 = beta^-1 G^-1 Y01 - t B.
```

The LEFT block-column `[A;C]` is a sum of `[-t C;C]` and `[beta^-1 G^-1Y10;0]`. Its rank is at most r_in+r_out. The RIGHT block-column has the analogous decomposition `[B;-t B]+[0;beta^-1 G^-1Y01]`, again of rank at most r_in+r_out. Therefore

```text
rank(X) <= 2(r_in+r_out).
```

This proof does not assume X invertible. In particular both diagonal residuals have coefficient -t, not opposite signs. Factoring the first residual matrix through a common `[-t I;I]` would introduce an incorrect -t^-1 coefficient on B for the literal C tensor. The two separate block-column bounds avoid any hidden Hadamard normalization or phase assumption.

If X is invertible, D itself cannot exceed 2(r_in+r_out). A dense row-support matrix can still have small cut ranks, so this is a different discriminator from Pauli or coordinate support.

## Complete coupled source columns

For the quotient `P0=diag(I,I,F_f,...,F_f)` and target Q with F_f on every bank, a complete boundary must obey `B_out*P0*B_in=Q`. Equivalently `B_out=Q*B_in^-1*P0^-1`. In either missing-core source column j, put `X_i=(B_in^-1)_ij` and `Y_i=(B_out)_ij`; then `Y_i=F_f X_i` for every output bank i.

Assume the ACTUAL inverse-input blocks X_i have both midpoint cross ranks bounded by r_in and the ACTUAL output blocks Y_i have both bounded by r_out. The scalar lemma bounds each block's rank by 2(r_in+r_out). Their W-block vertical stack must have full rank D because it is a column submatrix of the invertible complete B_in^-1. Hence the necessary complete source-column condition is

```text
2^f <= 2W(r_in+r_out).
```

This includes coupling among banks and does not incorrectly infer that an individual block must be invertible. A sparse FORWARD input boundary does not by itself supply these bounds on its inverse blocks. Those actual inverses must be proved or their topology bounded separately.

For the weighted-scan class whose strict lower and upper entries each have the form u_i+v_j, every off-diagonal midpoint block has rank at most two. If every inverse-input and output block belongs to that class, `r_in=r_out=2`. A single invertible block requires D<=8; a W6 coupled source column requires D<=48, so f>=6 is excluded. The synthesis track independently obtained this scalar rank bound and stronger class-specific finite/common-space restrictions. Those stronger restrictions use more than the two rank assumptions and are distinct evidence; the present bound does not assert an f4 whole-boundary exclusion in the larger cut-rank class.

Repeated bounded-rank blocks or hierarchical products may be tested through their actual cut-rank growth. They do not automatically remain rank two, and an arbitrary order change cannot be folded into that assumption for free.

## Fixed-offset scan postwords

There is also a direct bound for the synthesis track's layout0 preword. For matrices in the SAME low/high coordinate split,

```text
rank((AB)10) <= rank(A10)+rank(B10).
```

Each single-bank prefix or saved-original difference contributes at most one lower cross rank: a prefix's crossing block is all ones, and a difference has one boundary entry. Its pointwise scalar bank gates and diagonal amplitudes contribute zero. A cyclic address shift of fixed magnitude s contributes at most |s|. The declared layout0 has twelve single-bank scans and six fixed offsets of magnitudes 1 through 6, so its complete B has lower cross rank at most 33, uniformly in f.

The target Q has exact lower rank 3D and P0 has 2D. From `Q=R*P0*B` it follows that

```text
rank(R10) >= D-33.
```

A postword using s such scans, aligned pointwise bank gates and cyclic shifts of total absolute magnitude H has lower rank at most s+H. Thus `s+H>=2^f-33`. Bounded or polylogarithmic numbers of these scans with bounded shifts cannot implement that named postprocessor. This does not extrapolate a finite modular rank to all f; it uses exact tensor target/core ranks and a uniform topology upper bound.

The reversal layout is explicitly outside this model. Address reversal alone has cross rank D/2; a single nonlinear or global permutation can also have extensive cross rank. Large buffers, different spectator-fiber order, hierarchical permutations and another arithmetic encoding can escape the premise. The deduction consequently cannot reject a general O(V) streaming operation merely because it has dense coordinate support.

## Provenance and next scope

The source-based [streaming review](streaming-boundary-independent-review.md) pins the frozen synthesis producer, audit and arithmetic closure. The identities above were derived independently from the tensor C coefficients and matrix rank algebra, without executing or importing those producer sources. The parent independently reviewed the block-column and complete-source reasoning. This remains an analytical proof, not a formal proof package or an all-size native implementation certificate.

The next promising alternative must provide large cut-rank transfer through an explicitly paid nonlinear permutation or structured operation, while preserving full records and dirty fields. A different product/payload encoding could change the block equation itself. Neither alternative is excluded here, and neither is supplied by a correct dense matrix postprocessor alone.
