# Independent center-basis review and uniform all-h inverse formula

Status: **CONSTRUCTIVE ALL-H SCALAR LEMMA**, **EXACT FINITE WORD REVIEW**,
and **CONDITIONAL SCALAR PREFIX GUARD**. The physical source/sink phase
chronology is open. No improved characteristic root or kappa is asserted.

The [producer's center/null construction](../complex/dyadic-center-null-basis.md)
has a useful reversible scalar completion: its first q=binom(h,2) coordinates
are the mixed pair features G, while all other source coordinates are retained.
The independent review accepts its determinant-four induction and literal
common-frame scalar word. A closed block inverse additionally establishes
uniform bounds previously reported only as finite patterns.

## Input and independence

[center_basis_review.py](../../code/transfers/center_basis_review.py) imports
no producer code. It consumes the immutable
[base inverse](../../fixtures/complex/mixed-center-h7-inverse.json) and
[local gate words](../../fixtures/complex/center-basis-local-words.json) as
data, reconstructs every incidence matrix and complete word, and checks its
own exact matrix products. The
[review contract](../../fixtures/transfers/center-basis-word-contract.json)
pins both fixtures and the producer h8/h10 word digests and operation counts.
The original producer source hashes accompany the local-word fixture.

The pair features are `P_ij(S)=1[ij subset S]`, except rows 01 and 02 are
`D_ij=1-P_ij`. The total has dyadic reconstruction
`T=(sum retained P-sum two D)/8`. The independently reconstructed decoder
uses coefficients

```text
alpha_p = 1/4*[p subset S] - 3/32*|p intersect S|,
gamma = 3/8 + alpha_01 + alpha_02,
R_S,p = alpha_p+gamma/8         on retained pairs,
R_S,p = -alpha_p-gamma/8        on the two replaced pairs.
```

This gives `R*G=K`, with `K(S,T)=(|S intersect T|-1)(|S intersect T|-3)/8`.
The known 1/256 decoder grid and its scalar guard remain charged.

## All-h block inverse

The h7 mixed base A0 is a 21-by-21 matrix. I checked both products of the
retained inverse and independently computed `|det A0|=2^15`. The original
disjoint-pair base has eigenvalues 10,-4,1 with multiplicities 1,6,14;
replacing two rows by total-minus-row has determinant factor 4/5. This also
explains the power of two without inferring it merely from an inverse table.

For every new point j>=7, use the j source columns consisting of j plus each
four-subset of `{0,1,2,3,4}`, then `{j,i,0,1,2}` for 5<=i<j. The new rows
are pairs `(i,j)`. Their lower-left block is zero and their diagonal block is

```text
B_j = [[J5-I5, U], [0, I]],
B_j^-1 = [[-I5+J5/4, -(-I5+J5/4)*U], [0,I]],
```

where every column of U is `(1,1,1,0,0)^T`. Thus `det B_j=4`, giving
`|det M_h|=2^(2h+1)` for the full pivot minor.

There is extra structure in the upper blocks. Put

```text
u_j=(1,1,1,0,...,0)^T,
v_j=B_j^-1 u_j=(-1/4,-1/4,-1/4,3/4,3/4,0,...,0)^T.
```

For new blocks j<ell, the incidence cross block is exactly
`E_j,ell=u_j e_j^T`, with index j in the ell block. Since j>=7 is outside
the first five positions,

```text
E_j,ell * B_ell^-1 * E_ell,r = 0.
```

Consequently, if M=D+E is separated into block diagonal and strictly upper
parts, `(D^-1 E)^3=0`. The inverse expansion stops after two upper edges:

```text
M^-1 = (I-D^-1 E+(D^-1 E)^2) D^-1.
```

The new-to-new inverse block is `-v_j e_j^T`. Its five nonzero entries are
1/4,1/4,1/4,-3/4,-3/4, independent of h. No products of arbitrarily many
quarters accumulate through the induction.

For the base-to-new inverse blocks, let F be the 21-by-5 feature matrix of
the five four-subsets plus a new point. This F is independent of that point.
Put `w'=F*v_5`. The extra columns for i=5 and i=6 are fixed base vectors
w5,w6; for every i>=7 they equal the unit vector w at pair12. The inverse
base-to-new block therefore has only these finite coefficient classes:

```text
first five columns:     -A0^-1 F (-I5+J5/4),
extra column i=5:        -A0^-1 (w5-w'),
extra column i=6:        -A0^-1 (w6-w'),
every extra i>=7:        -A0^-1 (w-2w').
```

The sign and second w' contribution follow from the one permitted
base-to-new-to-new path. All 609 entries in these classes and A0^-1 are
checked explicitly in the independent source and retained in the final
receipt. They are nonzero, lie on grid 1/32 and have absolute value at most
7/8. The retained diagonal identity entries have value 1. Thus for every h>=7:

```text
32*M_h^-1 is integral,
max |(M_h^-1)_i,j| <= 1,
all nonidentity coefficient classes have absolute value <= 7/8.
```

To count inverse nonzeros, put t=h-7. The base contributes 441; diagonal new
blocks contribute `3t^2+34t`; new-to-new blocks contribute `5t(t-1)/2`; and
the base-to-new blocks contribute `21*sum(j, j=7..h-1)`. Therefore

```text
nnz(M_h^-1) = 441+168t+16t^2 = (4h-7)^2.
```

These are deductions from the explicit finite coefficient classes and the
nilpotent-block proof, not extrapolations of h28 output. They have not been
formalized in a proof assistant.

## Full scalar map and dirty reversibility

In pivot/nonpivot order the complete basis is

```text
B = [[M,G_nonpivot],[0,I]],
B^-1 = [[M^-1,-M^-1 G_nonpivot],[0,I]].
```

Each column of G has at most 12 nonzeros, so each entry of the top-right
inverse block has magnitude at most 12 and denominator dividing32. The
complete inverse row-L1 norm is at most 12v, with v=binom(h,5). The null
coordinates are retained data, not initialized scratch. The exact relation
`G*B^-1=[I_q,0]` implies `K*B^-1=[R,0]`; removing the retained identity
coordinates destroys the basis's invertibility.

The independent compiler reconstructs the producer's exact h8/h10 word
digests. Diagonal blocks run oldest first; their cross terms read future
inputs before those banks are transformed. Nonpivot contributions come last.
The inverse reverses the order and negates every shear coefficient or
inverts every scale. Reversing order alone fails on arbitrary dirty data.

The [final four-worker attempt](../../runs/20261009T001447Z-transfer-center-basis-guard-scope-repair/report.md)
checks h7,8,10,16 in 1.118 seconds. At h<=10 it replays all
329 basis columns and four arbitrary dyadic fields per case, plus 67,081
independent central-kernel entries. At h16 it verifies the closed pivot
inverse, counts and complete scalar word, without claiming the full
4368-by-4368 operator replay. There are no additional scalar banks. Native
role swaps and complete payload movement must still be paid.

## A uniform scalar prefix bound

The local gate inputs expose scalar multiplication temporaries, not only the
post-shear endpoints. Their exact maximum row-L1 factors are:

| Literal local word | Forward | Inverse | Extra fractional bits forward/inverse |
| --- | ---: | ---: | --- |
| 21-bank base |260|384|0 / 5|
| 5-bank border |8|7|0 / 2|

These constants include `c*source` before adding it into the destination.
They refer to the declared scalar gate model, with swaps retained as paid
bank exchanges. A native expansion of a swap or constant multiplication
must charge its own intermediate workspace and payload moves.

Let all original scalar inputs lie on grid2^-P and have magnitude at most A.
The full forward word uses integer coefficients and obeys the conservative
component bound `(260+2v)*A`. The future-input chronology prevents repeated
amplification through previously transformed blocks.

For the inverse on arbitrary incoming basis values, first subtract the
retained nonpivot contributions. Every remaining center value has magnitude
at most v*A. Every fully recovered pivot input is bounded by 12v*A from the
complete inverse row bound. Before a fixed local word, at most q recovered
coordinates have been subtracted, so a safe literal component bound is
`384*(1+12q)*v*A`. This includes the scalar multiplication temporaries.

There is also an h-independent fractional bound. Every new block's bottom
identity coordinates remain on grid2^-P. New-to-new cross terms read only
those bottom coordinates. The fixed five-bank inverse therefore needs at
most two extra bits. Only the base block reads the recovered first-five
coordinates; its incoming grid is at worst2^-(P+2). Its local inverse needs
at most five further bits. Thus the whole inverse fits grid2^-(P+7), while
its exact endpoint fits grid2^-(P+5).

This is a conditional scalar guard lemma at identical actual address
operators, for arbitrary dirty fields. The physical global grid can remain
P+7 throughout. A reduced rational denominator in the verifier is an
analytic bound on divisibility; no free output normalization or repacking is
assumed. Physical field copies, scalar implementations, common-frame
transitions and the surrounding Gaussian words remain separate obligations.

## Negative physical control and scientific limits

Common actual address operators matter. Consider source frames C_1 and C_7
on three binary address bits, with `C_t=alpha I+beta X_t`. A shear between
those unadapted physical banks does not compute C_1 times the sum of their
virtual values. For the second virtual source `delta_0`, output address1
should contain beta under a common C_1 frame; the unadapted C_7 contribution
there is zero. This exact finite control rejects merely renaming scalar
coordinates as if their source frames had already been synchronized.

The review therefore accepts a scalar mechanism, not a free common-frame
conversion or release of null coordinates. Source/sink anchors, copied dirty
continuation, every gauge/unit, and a complete phase child ledger must still
be derived. Neither this inverse sparsity nor its uniform scalar guard
changes the frozen characteristic root by itself.

## Preserved failed attempts and reproduction

The initial
[prefix assertion failure](../../runs/20261009T001103Z-transfer-center-basis-failed/report.md)
used endpoint-only local constants 232/347 and 4/7 after its observer had begun
including multiplication temporaries. It stopped before case replay; the
original source hash and a reconstructible correction patch are retained.

The next
[finite replay](../../runs/20261009T001147Z-transfer-center-basis-review/report.md)
passed the algebra, words and field controls, but its output metadata
incorrectly described7/8 as the full inverse bound while its own observed
maximum was1. The identity-entry omission is preserved explicitly. The final
attempt adds an assertion for the full bound1, distinguishes the nonidentity
classes, and uses the safe12v row bound. These scope repairs do not alter the
literal producer word or the accepted matrix identities.

The final source depends only on its three pinned fixtures and the standard
library. A bounded source-only check is:

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/center_basis_review.py \
  --workers 1 --small
```

Run IDs are derived from actual recorded UTC starts. Use fresh output paths.
Source versions, patches, seeds, raw hashes and complete scopes accompany each
attempt. This is independent OpenAI Codex research review, not external peer
review or formal verification.
