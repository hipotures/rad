# Independent partial-product character and real-packing review

## Assessment and evidence class

The complex track's minimum-D-product characterization is correct over `Q(i)` under a bilinear rank-D decomposition of a unital D-dimensional algebra. Its real-input half-Gaussian packing is an exact construction which saves one global binary axis, rather than an exponentially sparse coefficient domain. Neither result prices the transforms, supplies arbitrary dirty Gaussian endpoints, or proves a larger exponent.

This receipt is independent analytical proof and frozen-source inspection. It does not independently rerun the producer. Reviewed source: [partial_kernel_product_algebra.py](../../code/complex/partial_kernel_product_algebra.py), SHA256 `3e56ceb544baa77441c6371c248ddabe770769940e8c3dc32b6ac683a9393553`. The exact timestamp and source pin are recorded in its accompanying review run. No producer file is modified.

## Minimum-product characterization

Let A be a unital D-dimensional algebra over F and suppose

`mu(x,y)=W ((Ux) elementwise-multiplied by (Vy))`,

where U,V,W are square D-by-D matrices. No symmetry assumption about U and V is needed. With unit `1_A`, write `a=U1_A` and `b=V1_A`. The two unit identities give

`W diag(a) V=I`, `W diag(b) U=I`.

Thus all three matrices are invertible and all entries of a,b are nonzero. Normalize the evaluation rows by `U'=diag(a)^-1 U`, `V'=diag(b)^-1 V`, and change the output columns to `W'=W diag(a*b)`. Both normalized evaluation vectors send the unit to the all-ones vector. Applying the unit identities again gives

`W' U'=W' V'=I`, so `U'=V'=W'^-1`.

Multiplying the product identity by U' then gives

`U' mu(x,y)=(U'x) elementwise-multiplied by (U'y)`.

Every row of U' is therefore a unital character. Invertibility forces distinct rows and a complete character family. This is an algebraic normalization over F; it is not a claim that all intermediate normalizing inverses are permitted free native dyadic gates.

For the actual q_f algebra, the unit is the all-ones coefficient vector. The one-axis generator `(1,-1)` squares to minus this unit. Tensoring gives f commuting independent generators with square -1. Over `F=Q(i)` a unital character independently sends every generator to `+i` or `-i`, so there are exactly D characters. The literal C_f matrix has precisely these character rows and sends the unit to all ones. Hence a rank-D Gaussian algorithm's normalized input rows are C_f up to permutation; its output basis is the inverse character matrix with the corresponding output scalings.

This result proves the equality case of scalar product rank. It does not show that a larger-rank algorithm cannot have cheaper native conversions, nor that a character transform requires a particular tape time. In particular the named three-product recurrence uses `3^f` products, while the algebraic Gaussian minimum is `2^f`; `3^f` must not be presented as a rank lower bound. The conversion cost, complete input types and a genuine decreasing recurrence decide whether either construction helps the campaign.

## Real half-Gaussian construction

For real inputs, conjugating a row of C_f complements every selected row bit. Thus

`(C_f a)_(x xor (2^f-1)) = conjugate((C_f a)_x)`.

The pointwise product of two such spectra retains that conjugacy. Only half of its Gaussian coordinates are independent. Pair a0,a1 along one chosen axis and pack

`z = alpha*a0 + beta*a1 = ((a0+a1)+i(a0-a1))/2`.

This maps two arbitrary real fields bijectively to one arbitrary Gaussian field; unpacking is `a0=Re(z)+Im(z)`, `a1=Re(z)-Im(z)`. Apply C_(f-1) to the packed operand arrays, multiply their D/2 Gaussian spectral values, and apply C_(f-1)^-1. The omitted half is determined by conjugacy, so the packed inverse followed by the real unpack returns the complete q_f output.

The source retains both input packing denominator bits in the product and all inverse-child denominator bits. Its declared literal grid is `2+3(f-1)=3f-1`; comparison to the direct signed tensor's smaller grid uses exact trailing zeros, without truncation. Re/Im unpacking is explicit. The three-transform and three-product controls therefore compare the same actual signed dyadic tensor, rather than coefficient XOR convolution.

This does not recursively save every axis. After the first pairing the independent packed values are arbitrary Gaussian values, so the real-only premise is gone. D real input coefficients occupy D/2 complex coefficients, still D independent real fields. It is a constant density reduction and one global selected-axis reduction, not a `2^-f` orbit encoding. Arbitrary Gaussian operands require a separate interface and complete transform/carry/guard analysis. No such interface is supplied by the real control.

## Relation to the independent ring work

The complementary [ring and packing discriminator](bilinear-ring-packing-boundary.md) agrees with this characterization: in the negative-square coefficient basis the character evaluations are a full dense matrix, and the original C coordinates differ by `Phi=H/D`. Its CRT construction keeps every character, pays their encoding and decoding, and records the full integer product operands. The power-two cyclic-ring idempotent obstruction concerns faithful algebra encodings into a specified complete ring, rather than the cost of these rank-optimal character rows. The two scopes are independent and neither establishes a native complexity lower bound.

The next useful question is whether an explicitly paid higher-rank product word or nonhomomorphic integer encoding can avoid enough of the character conversion while preserving complete dirty payloads, polynomial precision and actual width/row decrease. Renaming the rank-D evaluations does not remove their transform.

The immutable [review receipt](../../runs/20261009T045833Z-transfer-partial-product-review/results/receipt.json) pins the exact inspected source and evidence class.
