# General idempotent image/kernel flags

Allowing a common address frame to use an arbitrary idempotent rather than a self-adjoint projector is a genuine model extension. It does not reduce the exact minimum rank at a fixed paired-\(G\) cut. This note constructs the larger class and identifies which constraints a useful new chronology would have to change. No native supplier or multiplier exponent is asserted.

## Exact four-flag theorem

Let \(H\) be a finite-dimensional rational vector space of dimension \(n\). Fix image flags \(V\subseteq U\) and kernel flags \(K_0\subseteq K_1\). An idempotent \(P\) satisfying

\[
V\subseteq\operatorname{im}P\subseteq U,
\qquad K_0\subseteq\ker P\subseteq K_1
\]

exists if and only if

\[
V\cap K_0=0,\qquad U+K_1=H.
\]

Let \(A\) have independent rows spanning the annihilator of \(K_1\), and put \(v=\dim V\), \(a=\operatorname{rank}A\), and \(c=\operatorname{rank}(A|_V)\). The attained minimum and maximum ranks are

\[
r_{\min}=v+a-c,
\qquad r_{\max}=\dim U-\dim(U\cap K_0).
\]

For necessity of the first feasibility condition, an idempotent fixes its image and kills its kernel. For the second, \(H=\operatorname{im}P+\ker P\subseteq U+K_1\). The condition \(\ker P\subseteq K_1\) is equivalent to \(AP=A\). Thus \(A\) is surjective on \(F=\operatorname{im}P\). The subspace \(V\cap\ker A\), of dimension \(v-c\), lies in \(F\cap\ker A\), of dimension \(\dim F-a\), giving the lower bound \(v+a-c\). The condition \(F\cap K_0=0\) gives the upper bound.

For an attained minimum, start with \(V\) and add vectors of \(U\) whose \(A\)-images extend the current response span until it has rank \(a\). This is possible because \(U+K_1=H\). Exactly \(a-c\) directions are added. The resulting \(F_{\min}\) meets \(K_0\) trivially: a vector in that intersection has zero \(A\)-image, forcing all added response coefficients to vanish, and hence lies in \(V\cap K_0\).

For the maximum, choose a complement to \(U\cap K_0\) inside \(U\) containing \(F_{\min}\). Call it \(F_{\max}\). Both images are surjective under \(A\). Choose \(K_{\max}\) to be a complement to \(F_{\max}\cap K_1\) inside \(K_1\), containing \(K_0\). It is a complement to \(F_{\max}\) in \(H\). Next choose a complement \(E\) to \(F_{\min}\cap K_1\) inside \(F_{\max}\cap K_1\), and set \(K_{\min}=K_{\max}+E\). This is a complement to \(F_{\min}\), and contains \(K_{\max}\). The resulting endpoint projectors therefore satisfy

\[
P_{\min}P_{\max}=P_{\max}P_{\min}=P_{\min}.
\]

The proof is ordinary linear algebra and works over any field when ranks and flags are interpreted in that field. The executable constructor uses exact rationals. Its good reduction to a local ring requires invertible cleared bases and unit denominators; rational ranks or real signatures are not transferred to arbitrary primes without these conditions.

## Why fixed paired-source cuts still have the radical bound

Let \(G\) be a nonsingular rational symmetric form. Set \(K_1=V^{\perp_G}\) and \(K_0=U^{\perp_G}\). Then \(a=v\), while \(c\) is the rank of the Gram form on \(V\). Consequently

\[
r_{\min}=v+\dim\operatorname{rad}(G|_V),
\qquad r_{\max}=\dim U-\dim\operatorname{rad}(G|_U).
\]

The two feasibility conditions both reduce to \(V\cap\operatorname{rad}(G|_U)=0\). These are exactly the bounds of the [self-adjoint rational completion theorem](rational-frame-completion-and-paid-chains.md). Thus an arbitrary kernel does not remove this obstruction while both right signal constraints and left covector constraints remain paired under the same \(G\).

This conclusion is scoped to that fixed cut. Nonselfadjoint intermediate choices can give different kernel histories. A genuinely asymmetric multi-frame chronology may change \(K_0,K_1\), the response rank \(c\), or the future image intersection \(U\). Those variables must be changed and paid explicitly, rather than dropping one of the source constraints in a static calculation.

## Actual algebraic address operators

For an idempotent \(P\), define

\[
D(P)=\begin{pmatrix}I-P&P\\P&I-P\end{pmatrix}.
\]

Its complete matrix satisfies \(D(P)^2=I\). If \(P,Q\) are nested in both image and kernel, so \(PQ=QP=P\), then \(Q-P\) is an idempotent of rank \(\operatorname{rank}Q-\operatorname{rank}P\), and

\[
D(Q)D(P)=D(Q-P).
\]

These are literal rational matrix identities. At a fixed good odd prime power they define invertible linear address maps, hence permutations of the entire finite address set. They do not establish a child-width fee, a fast tape router, a weighted long-record interface, complete supplier endpoints or row/precision budgets. Those costs remain to be supplied before the class can enter a recurrence.

There is also an exact rank-metric characterization of the enlarged geodesic class. In characteristic other than two, an invertible \(M\) satisfies

\[
\operatorname{rank}(I-M)+\operatorname{rank}(I+M)=n
\]

if and only if \(M^2=I\), equivalently \(M=I-2P\) for an arbitrary idempotent. To prove the forward direction, the two image spaces have dimensions summing to \(n\); their sum contains the image of \(2I\), so their intersection is zero. The image of \((I-M)(I+M)\) lies in both, and is therefore zero. The converse follows from the \(+1/-1\) eigenspace decomposition. For two such frames, the rank distance equals \(\operatorname{rank}(P-Q)\). Equality to the positive rank difference forces both image and kernel nesting, by equality in the rank subadditivity bounds for columns and rows. This statement describes an abstract operator class; no native rank-metric pricing is assumed.

## Exact finite evidence

[idempotent_flag_completion.py](../../code/synthesis/idempotent_flag_completion.py) constructs both attained ranks and complete nested projectors, with exact rational elimination. The first attempt began at `2026-10-09T09:13:30` UTC and used four workers on dimensions `4,6,10,12`, seeds `20261009171` through `20261009174`.

All 24 generated feasible four-flag instances passed every image/kernel constraint, projector idempotence, endpoint nesting, the complete \(D(P)^2=I\) identities, and the exact relative \(D\) identity. There were 132 complete good-prime-power matrix controls among the 144 candidate reductions at moduli `5,25,7,49,11,121`; reductions with nonunit denominators were explicitly skipped by the source rather than treated as good reduction. This is not a full finite array/tape replay.

The separate paired-\(G\) control used \(G=I-J/9\) on dimension ten, three disjoint triple indicators and the cap for \(T=\{0,3,6\}\). Its minimum remains four and maximum nine even though the constructed minimum projector need not be self-adjoint. Exact image/kernel conflict, missing covector coverage and inconsistent fixed flags are negative controls. The raw protocol and certificate remain at ignored `work/synthesis/20261009T091330Z-idempotent-flag-completion/results/`.

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/idempotent_flag_completion.py \
  --workers 4 --output <fresh-output-directory>
```

Expected status: `PASS GENERAL IDEMPOTENT FLAG AND STATIC OBSTRUCTION CONTROLS`. The all-size claims are written rational/field proofs, not proof-assistant formalization or an exhaustive enumeration of circuit chronologies.

The bounded reusable entrypoint is [verify_idempotent_flags.py](../../code/synthesis/verify_idempotent_flags.py). It reruns the 24 fixed-seed exact flag cases and all 132 good-prime-power complete matrix controls, checks the paired-source minimum remains four even for the nonselfadjoint constructor, and rejects a corrupted idempotent and a nonunit denominator. Its effective standard-library source closure is this verifier, `idempotent_flag_completion.py` and the frozen `rational_frame_completion.py`.

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_idempotent_flags.py \
  --output <fresh-receipt-file>
```

Expected status: `PASS GENERAL IDEMPOTENT FLAG BOUNDED CONTROLS`. Readable protocol/certificate copies of the first attempt are retained in `runs/20261009T091330Z-synthesis-idempotent-flags/`; these are identical copies of the original complete small JSON files. Source and raw originals remain unchanged. The bounded command supplies a scoped executable check, not independent reproof of the all-size theorem or a native supplier.
