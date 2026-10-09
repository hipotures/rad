# Rational frame completion inside future caps

The operation-frame descent in PR163 motivates a different question from scalar gate minimization: how small can a nondegenerate common operation frame be when both role histories and future readouts are fixed? This note gives an exact characteristic-zero answer. It does not supply a bit permutation over an odd local ring, a complex Gaussian frame, a native tape implementation, or an exponent claim.

## Exact completion theorem

Let \(B\) be a symmetric rational bilinear form, and let \(V\subseteq U\) be rational subspaces. Write \(d=\dim V\), \(R=\operatorname{rad}(B|_V)\), and \(r=\dim R\). A nondegenerate subspace \(F\) satisfying \(V\subseteq F\subseteq U\) exists if and only if

\[
V\cap\operatorname{rad}(B|_U)=0.
\]

When it exists, the smallest possible dimension is exactly \(d+r\). The largest possible dimension is \(\dim U-\dim\operatorname{rad}(B|_U)\).

For necessity, any vector of \(V\cap\operatorname{rad}(B|_U)\) would be in the radical of every containing subspace of \(U\). In addition, the map from \(R\) into the dual of \(F/V\), given by pairing, must be injective. Hence \(\dim(F/V)\ge r\).

For sufficiency, split \(V=N\oplus R\) orthogonally, with \(B|_N\) nondegenerate. The pairing map \(R\to U^*\) is injective under the stated condition. Choose \(w_1,\ldots,w_r\in U\) dual to a basis \(r_1,\ldots,r_r\) of \(R\), and subtract their orthogonal projections onto \(N\). Their pairings with the \(r_i\) remain the identity. On \(R+\langle w_1,\ldots,w_r\rangle\), the Gram matrix is

\[
\begin{pmatrix}0&I_r\\I_r&A\end{pmatrix},
\qquad \det=(-1)^r.
\]

Thus \(F=N+R+\langle w_1,\ldots,w_r\rangle\) is nondegenerate of dimension \(d+r\). For the maximum, choose a complement to \(\operatorname{rad}(B|_U)\) in \(U\) containing \(V\). Such a complement exists because their intersection is zero; its restriction of \(B\) is nondegenerate, and every nondegenerate subspace of \(U\) injects into the quotient by its radical.

The criterion is also equivalent to \(R\cap\operatorname{rad}(B|_U)=0\). The constructor returns a nonzero rational obstruction in this intersection when completion is impossible. No numerical rank tolerance is used.

## The PR163 rational form

For \(G_h=I_h-J_h/9\), the eigenvalues are \(1\) on the sum-zero hyperplane and \(1-h/9\) on the all-ones line. When \(h>9\), its real signature is \((h-1,1)\). Every radical of a rational subspace is totally isotropic, so its dimension is at most one. One direct proof is to put the real form into \(\|x\|^2-t^2\): projection of a totally isotropic subspace onto the single \(t\) coordinate is injective. Therefore a feasible rational operation frame requires either no added direction or exactly one. For \(h<9\), the form is positive definite and no added direction is needed. The singular ambient case \(h=9\) is excluded from this signature conclusion.

This is a rational statement. An odd finite field can have larger totally isotropic subspaces, and a rational basis does not automatically give an admissible local-ring interface. For a fixed rational frame, clear every denominator, retain the resulting integer basis, and exclude every prime dividing the required basis, ambient-form, or Gram denominators/determinants. New frames can enlarge those exclusions and the height bound. Their coordinate computation, exceptional-class fallback, routing and scalar costs must be charged before changing a recurrence certificate.

## A positive completion and a joint-cap obstruction

Take three disjoint triples supported on coordinates \(0\ldots8\), with indicator vectors \(v_0,v_1,v_2\). Their Gram matrix is \(3I_3-J_3\), and their radical is the line through \(r=v_0+v_1+v_2\). Let \(T=\{0,3,6\}\), and let \(U=\ker(3\chi_T-\mathbf 1)\). All three vectors are in \(U\). For \(h\ge10\), the vector \(w=\chi_T+6e_9\) is also in \(U\), and \(B(r,w)=-6\). The four-vector Gram determinant is \(-108\), giving an explicit minimal four-dimensional completion.

If instead \(U\) is the intersection of all 27 caps formed by choosing one coordinate from each of the three triples, then \(r\in\operatorname{rad}(B|_U)\). Differences between cap equations force each of the three coordinate blocks to have constant entries, and any one cap equation forces the sum of coordinates outside the first nine to be zero. Hence pairing with \(r\) vanishes throughout \(U\). No nondegenerate completion inside this joint cap exists. This constrains that fixed future-cap ansatz; it is not a universal circuit lower bound.

## Consequence for a fixed paid chain

At a scalar gate joining two roles, let their preceding frames be \(P_1,P_2\), their next required frames be \(N_1,N_2\), and let \(S\) contain every source-vector direction conservatively present at the gate. Set

\[
V=P_1+P_2+S,\qquad U=N_1\cap N_2.
\]

Within a nested, nondegenerate rational-frame chronology, feasibility and the minimum dimension follow from the theorem. At fixed neighbors, a frame of dimension \(d_F\) contributes the ideal child cost

\[
(d_F-\dim P_1)^p+(\dim N_1-d_F)^p+
(d_F-\dim P_2)^p+(\dim N_2-d_F)^p
\]

for \(0<p<1\), with zero-width terms omitted. This is concave in \(d_F\). Its minimum on the feasible dimension interval therefore occurs at an attainable minimum or maximum dimension. This reduces a local search to two constructive endpoints. Global changes still couple adjacent gates; fixed-neighbor optimality is not global optimality. Prime/fallback fees or representation-dependent costs must be included separately, and may alter which endpoint is preferable.

## Exact evidence and reproduction

The standard-library constructor is [rational_frame_completion.py](../../code/synthesis/rational_frame_completion.py), SHA-256 `8a35ffa3b5b354b4e0ec83ee75a19d76a497d47c883121d4c7a289836fd88f4c`. Its first four-worker attempt began at `2026-10-09T08:06:24.335200+00:00`, testing \(h=10,12,24,48\), seeds `20261009141` through `20261009144`. All four exact positive completions and all four 27-cap obstructions passed. Each dimension also checked six deterministic seeded lower spans against the rational radical bound. The largest task took 4.2511 seconds. Complete original evidence remains at ignored `work/synthesis/20261009T080624Z-rational-frame-completion/results/`; the directory timestamp agrees with the actual protocol start.

From the repository root, use a fresh output directory:

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/rational_frame_completion.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/<fresh-id>/results
```

Expected status: `PASS EXACT RATIONAL FRAME COMPLETION`. This evidence checks the constructor and stated finite examples. The all-size claims are the rational proofs above, rather than an enumeration of all subspaces or a formal proof-assistant verification.
