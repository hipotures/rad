# Nonlinear matching alignment retains the routed-edge cost

Status: **SCOPED ALL-SIZE ALGEBRAIC OBSTRUCTION**, with **EXACT FINITE LITERAL OPERATOR CONTROLS**. Nonlinear or nonunit routing does not repair one specific canonicalization mechanism. This is not a lower bound on arbitrary matching frames, arbitrary two-sided boundaries, scalar helper networks or multiplication.

## Identity independent of linear address coordinates

The earlier [coordinate routed-SWAP review](routed-swap-independent-review.md) analyzes `F*A_T^-1*P*A_U^-1` when P maps source and target directions. Its density argument extends when the matching kernels are related by conjugacy, without assuming P is linear or unitary.

Let M_U be a fixed-point-free involutive address permutation and

```text
A_U = alpha I + beta M_U,
alpha=(1+i)/2, beta=(1-i)/2.
```

Direct multiplication gives `alpha^2+beta^2=0`, `2 alpha beta=1`, hence `A_U^2=M_U`. Its inverse is `conj(alpha) I+conj(beta) M_U`, and `A_U^-2=M_U`. Let P be ANY invertible weighted address monomial, with nonzero Gaussian-dyadic weights when that ring is required. Define `A_T=P*A_U*P^-1` and `M_T=P*M_U*P^-1`. Then

```text
F*A_T^-1*P*A_U^-1 = F*P*A_U^-2 = F*P*M_U = F*M_T*P.
```

This identity is independent of address-bit linearity, matching geometry and coefficient magnitudes. Weighted M_T remains an involution, though its weights need not be unitary. If instead `A_T=P*A_U^-1*P^-1`, the same edge equals `F*P`. A nonzero scalar in the conjugacy only contributes its inverse at the edge, repeated in every selected column; it cannot create zeros.

More generally the same proof applies to any invertible A_U whose square is an invertible weighted monomial. It does not assert that arbitrary actual Lagrangian frames have that property. The quarter-turn matching kernels tested here do.

F is the full C_h tensor and every matrix coefficient is nonzero. Right multiplication by an invertible weighted monomial only permutes and rescales columns. Therefore the critical routed edge has exactly 2^h nonzero coefficients in every row and column. At f independent columns the exact support is 2^(hf). Nonunit weights and cancellation inside the original expression do not alter its proved endpoint.

One selected-width-r C child has 2^(rf) nonzeros per row and column. Arbitrary monomial or nonzero diagonal wrappers preserve that support. Consequently no single r<h child with those wrappers equals the aligned edge. The same row-support product bound excludes a serial SINGLE-BANK chain with sum of selected child widths below h. This comparison does not permit role additions, copied banks or multi-path scalar networks; those different architectures need their own ledger and can escape this premise.

This matters for a virtual signed SWAP with upper route P^-1 and lower route -P. The data anchors diag(A_U,I) at input and diag(F,F*A_T^-1) at output can be converted to canonical F outputs by the corresponding monomial corrections. The lower incidence required by that conversion is precisely the full-support edge above. The cheap canonical data alignment cannot retain the unrouted smaller incidence simultaneously under this conjugacy. The argument assumes that these actual anchors/routes are the proposed word; it does not establish a complete signed-SWAP circuit.

## Independent exact controls

The fresh [checker](../../code/transfers/coherent_matching_routing.py) reads [its own config](../../configs/transfers/coherent-matching-routing.json). It imports only the previously independent Gaussian arithmetic [helper](../../code/transfers/conditioned_frame_review.py), SHA256 `f663a51af46de2a8da18f8e2a7eeceb0cabc23aeb1569e61aeb198590aadf018`. It imports no producer, nonlinear routing supplier, frame compiler or original routed-SWAP source.

Four independent workers test h3/f1 unit-weighted matching conjugacy, h3/f2 nonunit-weighted conjugacy, h4/f1 unit-weighted conjugacy, and h4/f1 inverse nonunit conjugacy. Each uses a seeded complete matching, an explicitly nonlinear Toffoli address permutation, all fourth-root phases, and, where declared, arbitrary powers 2^e with e in [-2,2]. Source kernels, their inverses and all conjugated operators are literal Gaussian-rational matrices.

The grouped oracle separately applies the complete local operators `A_U^-1,P,A_T^-1,F` in chronological order on every column. It checks every complete real input basis vector against the closed full-C tensor coefficient and the required per-column monomial weight, including all repeated phases. All 104 grouped input columns and 4672 complete coefficients pass. Four complete arbitrary Gaussian dirty fields per case also pass the literal inverse word. The h3/f2 case binds true grouped support 64 rather than projecting the operator to one column or suppressing global weights.

The negative control omits the source A_U^-1 correction and disagrees with the actual matrix in every case. A separate positive control uses independent coordinate matchings X_0 and X_1 without an aligning route: `F*A_1^-1*A_0^-1` has support exactly 2^(h-2). Thus the claimed smaller profile is possible for a DIFFERENT edge, and importing it after canonical alignment would be an incorrect cost comparison.

The [actual-UTC four-worker run](../../runs/20261009T041311Z-transfer-coherent-matching-routing/report.md) passed in 0.153061435 seconds. Runtime is reference execution, not native tape timing. The config retains every seed and the results retain complete matching/route/weight tables, output hashes, scope and exact support counts. Original protocols/results are copied unchanged; the ignored work run is deterministically regenerable.

From the breakthrough repository root, standard library only:

```bash
python3 research/integer-mult-breakthrough/code/transfers/coherent_matching_routing.py --workers 1 --small
python3 research/integer-mult-breakthrough/code/transfers/coherent_matching_routing.py \
  --workers 4 --output research/integer-mult-breakthrough/work/transfers/<fresh-actual-UTC>-matching-routing/results
```

Require a fresh output directory. Each source/config/helper hash is recorded before execution and checked unchanged afterward. There is no unavailable external runtime input or modified dependency.

The obstruction leaves useful alternatives: source/target frames that are not aligned by this conjugacy, genuinely multi-path bank circuits, a different canonical master target, or a paid nonmonomial boundary. The [guarded nonlinear router](packed-nonlinear-routing.md) makes some of those possibilities testable; its existence alone does not evade this exact edge identity.
