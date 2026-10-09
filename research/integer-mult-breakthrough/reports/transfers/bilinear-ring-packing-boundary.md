# Partial-transform product fusion and cyclic-ring capacity

## Result and scope

Two independent exact discriminators clarify what would be needed to absorb missing phase transforms into coefficient multiplication. The literal C-conjugated bilinear tensor is not ungauged XOR convolution. A complete ordinary univariate product already has collisions that prevent an operand-independent decoder from recovering XOR or negative-square convolution. Faithful CRT encoding preserves all components, but its character encoding, interpolation and full-modulus integer products are still paid operations.

There is also an all-size algebraic obstruction stronger than the monomial encoding test: a full power-two cyclic ring of dimension `N=2^n` over `Q(i)` has only `2n` field factors. A faithful algebra encoding of the `D=2^f`-character product therefore requires `2^f <= 2n`, or `N >= 2^(2^(f-1))`. A full power-two negacyclic ring has only two field factors and excludes such a faithful encoding for `f>=2`.

These are exact finite controls and analytical algebra results. They do not supply a native multiplier, an all-size precision or tape theorem, or a larger exponent. They concern faithful algebra encodings into a complete ring; arbitrary bilinear operand encodings, operand-dependent corrections, several products, Toeplitz restrictions, arbitrary extension dimensions and the existing nonzero finite-field cyclic core with its zero border remain outside the obstruction. The ring result is distinct from the coordinator's linear C-to-circulant equivalence test.

## The actual bilinear tensor

Let `C = alpha I + beta X`, `alpha=(1+i)/2`, `beta=(1-i)/2`, and `D=2^f`. Define

`m_C(u,v) = C_f^-1 ((C_f u) elementwise-multiplied by (C_f v))`.

For basis vectors indexed by `a,b,c` in `{0,1}^f`, its coefficient is

`[m_C(e_a,e_b)]_c = D^-1 (-1)^(wt(a&b) + wt(c & complement_f(a xor b)))`.

In particular every basis pair has all D output coordinates nonzero. On one axis, with `e=(u0+u1)(v0+v1)`,

`m_C(u,v) = (e/2-u1*v1, e/2-u0*v0)`.

The unit in these coordinates is the all-ones vector. This is not coefficient XOR multiplication, whose unit is `e_0` and whose basis-pair product has one coordinate. The source checks all 80 basis pairs and 576 output coefficients for f=2,3, plus complete Gaussian operand pairs for f=2..5. It rejects the ungauged substitution explicitly.

For algebra analysis, let H be the unnormalized Walsh matrix and `Phi=H/D`. In the coefficient basis of

`B_f = Q(i)[t_1,...,t_f]/(t_j^2+1)`,

the product is

`(a*b)_c = sum_(x xor y=c) (-1)^wt(x&y) a_x b_y`.

Its character evaluations substitute `t_j=i*(-1)^chi_j`. Their matrix E satisfies `E Phi=C_f`; hence `Phi m_C(u,v) = (Phi u)*(Phi v)`. This is a basis change with an actual Walsh transform, not a free identification of the input records. The finite CRT experiment uses the negative-square coefficient basis directly; it does not claim that the original C-basis operands have been encoded at zero cost.

## Collisions and complete CRT capacity

For f>=2, the ordinary products of `(X^1,X^1)` and `(X^2,X^0)` are both exactly `X^2`, even when every coefficient through degree `2D-2` is retained. The XOR targets are `e_0` and `e_2`; the negative-square targets are `-e_0` and `e_2`. Thus no operand-independent function of that one full ordinary product recovers either target. This does not exclude a decoder that uses the original operands or additional products. Carry-free radix-three packing avoids the binary sum collision but occupies `3^f` positions for `2^f` input coefficients, a ratio `(3/2)^f`.

The CRT control evaluates all D characters and assigns a distinct prime `p=3 mod4` to each. Both real and imaginary fields are retained; `F_p[i]` is a quadratic field. For input real/imaginary components bounded by B, each evaluated product component is bounded by `2D^2 B^2`. The chosen primes exceed `4D^2 B^2`, so centered recovery is exact. Four complete CRT codes and three ordinary integer products compute the Gaussian component products. Interpolation returns every coefficient exactly.

Omitting one character destroys injectivity even on bounded Gaussian integral coefficient arrays: for omitted chi, the coefficients

`k_a = i^(-wt(a)+2wt(a&chi))`

have unit magnitude, evaluate to D at chi, and to zero at every other character. This is an exact missing-component witness, rather than a dimension-only heuristic.

The actual four-worker measurements, with B=2, are:

| f | D | Full CRT modulus bits | Largest actual product-operand bits | Dense evaluation terms per operand |
| --- | --- | --- | --- | --- |
| 2 | 4 | 33 | 33 | 16 |
| 3 | 8 | 81 | 82 | 64 |
| 4 | 16 | 193 | 193 | 256 |
| 5 | 32 | 449 | 450 | 1024 |

These sizes are recorded for every one of the three products, not inferred from a hypothetical smaller oracle. This experiment supplies no native cost for prime setup, CRT encoding, character transforms, modulo operations or interpolation. For large R-bit coefficients, a CRT representation at scale `D(R+f)` can have only a constant volume factor when `R>>f`; the controls do not prove that CRT necessarily has an asymptotic volume blowup. The missing issue is a complete cheap encoding and a noncircular paid recurrence for the full products, with real width/row decrease and dirty-field endpoints.

## Power-two full-ring obstruction

First, a monomial encoding of any generator with square `+1` or `-1` into `Q(i)[X]/(X^N +/- 1)` must have exponent w satisfying `2w=0 modN`. There are at most two such exponents, and they generate at most a two-dimensional monomial span. Gaussian scalar coefficients do not change this residue constraint. Thus a faithful monomial algebra encoding is impossible for f>=2, regardless of N. This is only a monomial restriction.

The stronger result allows arbitrary polynomial encodings. Work over `F=Q(i)` and let `pi=1+i`, a Gaussian prime. For every power-of-two degree d, `(X+1)^d +/- i` is Eisenstein at pi: its constant `1 +/- i` has pi valuation one, every interior binomial coefficient is even, and its leading coefficient is one. Gauss's lemma over the Euclidean ring `Z[i]` therefore makes `X^d +/- i` irreducible over F. Degree-one factors are included.

For n>=1,

`X^(2^n)-1 = (X-1)(X+1) product_(j=1..n-1) [(X^(2^(j-1))-i)(X^(2^(j-1))+i)]`.

These `2n` distinct irreducible factors give exactly `2n` fields in the rational CRT decomposition. Similarly `X^(2^n)+1` has exactly the two irreducible factors `X^(2^(n-1)) +/- i`. Separability in characteristic zero excludes repeated factors.

The algebra B_f is a product of D copies of F because the two roots `+i,-i` of every generator polynomial are distinct. Its D nonzero primitive idempotents are mutually orthogonal. An injective multiplicative F-linear encoding, even if not assumed unital, sends them to D mutually orthogonal nonzero idempotents. A product of r fields permits at most r such idempotents: each has support on a nonempty subset of the r coordinates and the subsets must be disjoint. Therefore D<=r. This proves the stated cyclic bound and negacyclic exclusion; it also applies to Gaussian-dyadic encodings by extension to F.

Exact n=1..4 controls multiply every factor, construct every rational CRT idempotent by polynomial Bezout, verify all 120 cyclic and 16 negacyclic idempotent pair products, check their sum is one, and confirm dyadic denominators. These are finite proof controls; the all-size argument is the one above.

A positive control prevents overgeneralization. For f=2 and cyclic N=4, a faithful nonmonomial encoding exists. One tested generator pair is

`t_1 -> ((1+i)/2) X + ((-1+i)/2) X^3`, `t_2 -> i X^2`.

Their squares are -1 modulo `X^4-1`; the four basis images have exact rank four, and the full Gaussian operand product agrees. This directly distinguishes the monomial exclusion from the larger algebra result. It supplies no free native basis conversion.

## Provenance and reproduction

Authored sources:

- [bilinear_ring_packing.py](../../code/transfers/bilinear_ring_packing.py), SHA256 `ce5005636175faf19f531f76eb045ce75f7a77e6adfbdda2312019f126a4fb0b`.
- [bilinear-ring-packing.json](../../configs/transfers/bilinear-ring-packing.json), SHA256 `f1644077f9f4e21f653472293e1411815a3be352d6acc5c8ee33d08cc20242e3`.
- [power_two_ring_capacity.py](../../code/transfers/power_two_ring_capacity.py), SHA256 `7a29ed784283dbf29c1f9d41b800789152f1f4416f626fa2822c65b94c9a4e23`.
- [power-two-ring-capacity.json](../../configs/transfers/power-two-ring-capacity.json), SHA256 `35a00e8469c7944b1fad5202402346a4861ed3e3fd756feee80a7ec6ad95988e`.
- The sole helper is our independently authored [conditioned_frame_review.py](../../code/transfers/conditioned_frame_review.py), SHA256 `f663a51af46de2a8da18f8e2a7eeceb0cabc23aeb1569e61aeb198590aadf018`. No A/B/coordinator producer is imported.

Original full attempts and bounded receipts are immutable:

- [20261009T044328Z](../../runs/20261009T044328Z-transfer-bilinear-ring-packing/report.md), four workers, 0.154301 source seconds, PASS.
- [20261009T044442Z](../../runs/20261009T044442Z-transfer-bilinear-ring-bounded/report.md), one worker, f=2, PASS.
- [20261009T044815Z](../../runs/20261009T044815Z-transfer-power-two-ring-capacity/report.md), four workers, 0.120418 source seconds, PASS.
- [20261009T044843Z](../../runs/20261009T044843Z-transfer-power-two-ring-bounded/report.md), one worker, n=2 positive/negative controls, PASS.

From the repository root, Python standard library only:

```bash
python3 research/integer-mult-breakthrough/code/transfers/bilinear_ring_packing.py --workers 1 --small
python3 research/integer-mult-breakthrough/code/transfers/power_two_ring_capacity.py --workers 1 --small
```

Omit `--small` and use `--workers 4` for the complete finite sets. Optional `--output` must designate a nonexistent directory. The scripts pin their effective source, configuration and helper before and after each attempt. No failed scientific attempt or source repair occurred in these two packages.

The next useful escape is a paid nonhomomorphic operand encoding or a different ring/product recurrence, with explicit input/output conversion, complete payload bounds and genuine size decrease. A faithful full power-two ring alone cannot provide that escape cheaply in f.
