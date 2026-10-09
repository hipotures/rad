# Scoped address-dependent boundary obstructions

Status: **CONDITIONAL STRUCTURAL RESULTS** and **EXACT FINITE KERNEL CONTROLS**.
These results concern specified boundary words for the joint mutable-source
component. They are not a lower bound on integer multiplication or on all
native adapters. In particular, pre/post words with several interleaved
address-dependent nonunit layers remain open.

## Question and exact operator

The [joint birth component](joint-mutable-birth-algebraic-cleanup.md) computes
a useful positive core but needs two additional line kernels to reach the
canonical complete target. Can a cheaper native address-dependent boundary
replace those two recursive calls?

Write `F=C^(tensor(h*f))`, `A_U=C_U^(tensor(f))`, and
`H_U=F*A_U^-1`. There are six complete physical banks, including both dirty
carriers. After the paid constant bank decoding and exchange, the exact core
operator is

```text
P0 = diag(H_1,H_7,F,F,F,F),       Q = diag(F,F,F,F,F,F).
```

The coupled form before that decoding has data block
`[[0,-F*S^-1],[F*S*diag(A_1^-1,A_7^-1),0]]`; its dirty endpoints are F.
Here S is the retained unimodular nonunit scalar matrix. The reduction to P0
is an exact operator calculation, not an identification of frame labels.
This report's pointwise sandwich theorem applies to the decoded operator.

## Unique post-only repair and support

Since P0 is invertible, the equation `R*P0=Q` has the unique solution

```text
R = diag(A_1,A_7,I,I,I,I).
```

In the coupled coordinates its data block is
`[[0,diag(A_1,A_7)*S^-1],[-S,0]]`. Thus a post-only adapter cannot choose a
different cancellation pattern at the level of its final operator. Each
affected repair row has exactly `2^f` nonzero input coefficients.

Consider a post-only word with arbitrary invertible monomial address moves
and T mixing layers. In one mixing layer each output coordinate depends on
at most W current coordinates. A monomial, including a nonzero scalar that
depends on the address, preserves row support. Multiplication by a mixing
layer takes the union of at most W preceding row supports. Starting from
the identity, every final row therefore has support at most `W^T`, even
with arbitrary nonunit coefficients and cancellation. Consequently

```text
T >= f/log2(W).
```

This permits globally routed monomials; it does not assume affine routing.
It is a layer-count result, not a universal time lower bound. It also does
not constrain a two-sided word by itself: a preprocessor may route inputs
into the already dense F channels before the core.

## One pointwise mixer on each side cannot repair the core

Now allow arbitrary invertible complex bank matrices `B_out(x)` and
`B_in(y)` at the two boundaries. Between them and P0, allow an arbitrary
bijective input and output address permutation independently for each bank.
For a fixed pair of output and input addresses, the resulting coefficient
block has the form

```text
B_out(x) * diag(H_j(q_j(x),p_j(y))) * B_in(y),
```

where `H_j` denotes H_1, H_7 or F as appropriate. Each H_U row has zeros,
whereas every F coefficient is nonzero. For any output x, choose y so that
one of the first two diagonal entries is zero; the chosen input permutation
is bijective, so such a y exists. The block then has rank at most W-1.
Invertible boundary bank matrices do not change that rank. The target
coefficient block is `F(x,y)*I_W`, of rank W, a contradiction.

This excludes one pointwise mixing stage on each side with per-bank routes
placed inside the sandwich. The matrices may vary arbitrarily with address
and may be nonunit. It does not exclude arbitrary permutations that mix
bank selectors with addresses outside this model, or several pointwise
mixers interleaved with routing. Without the per-bank routes, an additional
constant coupled bank decoder also preserves the deficient block rank.

## Separate unitary entropy control

For a unitary matrix M of order N, define
`Phi(M)=-sum_ij |M_ij|^2*log2(|M_ij|^2)`, with zero terms omitted.
The target has entropy `W*D*h*f`, where `D=2^(h*f)`. The decoded core has
entropy `(W-2)*D*h*f+2*D*(h-1)*f`. Their difference is `2*D*f`.

A left unitary mixing layer partitioned into blocks of size at most W
changes this potential by at most `N*log2(W)`. For each column and block,
the total squared mass is fixed. Its conditional entropy lies between zero
and `mass*log2(W)`; summing the masses over blocks and columns gives N.
Right mixing has the same bound by applying this argument to the adjoint.
Unit-modulus monomials preserve the potential. A unitary pre/post boundary
word therefore needs a total of at least

```text
T >= 2*f/(W*log2(W))
```

such layers. This is a restricted result about a unitary boundary word.
The scalar S in the actual coupled core is nonunit; this argument does not
bound it or general nonunit preprocessors.

The retained control scales one dense F bank by 2 and another by 1/2.
Both scales and their inverses are Gaussian dyadic and their product
determinant is one. The unnormalized entropy changes by
`D*((9/4)*h*f-15/2)`, which grows with f although the scale word has constant
length. Thus the unitary potential estimate cannot be applied to arbitrary
nonunit words. A uniform conditioning assumption would need its own proof
and would not follow from correct final endpoints or an available guard.

Matrix entropy for unitary gate models is a primary-source precedent:
[Nir Ailon, 2013, A Lower Bound for Fourier Transform Computation in a Linear
Model Over 2x2 Unitary Gates Using Matrix Entropy](https://arxiv.org/abs/1305.4745).
The conditioned-model extension in
[Ailon, 2014, An Omega((n log n)/R) Lower Bound for Fourier Transform Computation
in the R-Well Conditioned Model](https://arxiv.org/abs/1403.1307)
retains an explicit condition restriction. The block-layer argument above
is supplied directly; neither paper implies an unrestricted native or
multiplication lower bound for this campaign.

## Comparison with the actual transfer and precision budget

The [routing-aware transfer](../transfers/routing-aware-depth-transfer.md)
uses `f=floor(e/m)` for fixed m, rather than an independently chosen smaller
tensor multiplicity. Its paid local bill per current volume V is
`O((e*K)^tau+1)`. The root has `e=d` and `K=Theta(d^c)`, and the sharpened
stopping condition is `c*tau/(1-tau)<1`, equivalently `tau*(1+c)<1`.

If a declared implementation materializes the complete current volume once
per boundary mixing layer, the post-only support bound gives
`Omega(V*f)=Omega(V*e)` work for fixed W,m. Fitting that implementation in
the retained root bill would require `tau*(1+c)>=1`, contrary to the
stopping condition. Thus a complete materialized pass per required layer
cannot preserve that sublinear transfer contract.

This cost conclusion is conditional on materializing a full V-pass for
each layer. It does not establish that all native executions incur those
passes. Fused or streaming implementations, a different outer architecture,
and deeper two-sided nonunit intertwiners must be assessed separately.
Actual record lengths, tape moves, row stock, long chunks and precision
must be bound to the same program before using the transfer lemma.

The [endpoint-aware guard](../transfers/endpoint-aware-guards.md) separately
allows `O(e*log(e))` numeric guard under its complete literal prefix and
child-endpoint hypotheses. This can fit `o(p)` when `e<=p^epsilon`,
`epsilon<1`. A numeric allowance is not a time bound or a bound on the
condition number of arbitrary nonunit boundary words. The changed joint
core does not automatically inherit the old complete native interface.

## Complete finite evidence and reproduction

The standalone standard-library
[discriminator](../../code/synthesis/address_boundary_discriminator.py)
imports no producer code. Its exact Gaussian coefficient formula for F is
`(1+i)^(h*f-wt(r))*(1-i)^wt(r)/2^(h*f)`. For an odd label U, the ratio of
H_U to F is `(1-i)^f` on the affine constraints
`r_column dot U = (wt(U)-1)/2 mod2`, and zero elsewhere. The implementation
independently checks this identity by direct convolution with A_U^-1,
then checks every coefficient of `A_U*H_U=F`.

Four workers ran the four cases `(h,f)=(3,1),(4,1),(3,2),(4,2)`. They replayed
139,904 complete kernel-repair coefficients, all nonzero masses and supports,
and 688 rank-deficient boundary blocks with address-dependent unimodular
integer bank mixers. The finite routing controls use independent XOR input
and output routes for each bank. Exact row masses prove the stated entropy
values. The layer support calculation also checks integer power bounds at
f=16,64,256,1024; these are formula controls, not circuit searches.

The [completed run](../../runs/20261009T030551Z-synthesis-address-boundary/)
retains the unchanged protocol and full compact certificate. The original
ignored output remains at
`work/synthesis/20261009T030551Z-address-boundary/results`; it is regenerated
by the command below. The actual protocol start is
`2026-10-09T03:05:51.930374+00:00`, matching the run namespace. There is no
random seed and no downloaded dependency. The exact source SHA-256 is
`4c1e4ab0769be59b8fc4546dce340908784135d1b4bfe269e9475769e83b1b16`.

From the breakthrough worktree root, use a fresh output directory:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/address_boundary_discriminator.py \
  --workers 2 \
  --output research/integer-mult-breakthrough/work/ci/<fresh-id>-address-boundary/results
```

This exercises all four cases in under a second on the recorded host.
The source itself is the complete executable dependency closure.

The next discriminator should permit multiple nonunit pointwise mixers
interleaved with address moves on both sides and require the complete
operator, not just a frame or support match. The useful escape must avoid
the materialized full-pass cost or change the transfer; a longer adapter
alone does not supply an exponent improvement.
