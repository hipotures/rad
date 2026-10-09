# Small nonhomomorphic ordinary-product packing discriminator

## Question and result

Can a single ordinary polynomial product encode XOR coefficient multiplication more compactly than radix-three packing, using nonlinear input label placement? This is a bilinear encoding plus a decoder, not a homomorphic embedding into a full quotient ring. The [power-two ring obstruction](bilinear-ring-packing-boundary.md) therefore does not automatically exclude it.

The exact f=2 and f=3 searches find minimum nonnegative input spans 0..4 and 0..13, respectively, with complete product lengths nine and 27. They match the radix-three construction. All shorter spans fail already because an injectively labeled set cannot contain a nontrivial three-term arithmetic progression. These are finite results for one common exponent set used by both operands; they do not prove a `3^f` lower bound for arbitrary nonlinear placements at larger f or for asymmetric operand encodings.

No native packing, multiplication cost, all-size product recurrence or exponent is supplied. Wider exhaustive search was not launched.

## Complete format and necessity

Assign each of the D=`2^f` input labels a distinct integer exponent w(a), and use the same exponent map for both operands. A full ordinary product places basis-pair `(a,b)` at exponent `w(a)+w(b)`. An operand-independent decoder can recover XOR multiplication only if every such sum has one XOR label:

`w(a)+w(b)=w(c)+w(d) => a xor b=c xor d`.

Otherwise two full ordinary basis products coincide while their requested output coordinates differ. Fixed nonzero scalar weights do not remove the contradiction: the basis operands can be rescaled to give the same product coefficient. This necessary condition is also sufficient with the explicit linear decoder that adds every ordinary product coefficient to its associated XOR coordinate.

Translation of all exponents to make their minimum zero does not affect this condition or the span. A nontrivial progression `w(a)+w(c)=2w(b)` would equate a distinct cross-pair's nonzero XOR to the self-pair XOR zero, so every admissible exponent set is progression-free.

The negative-square coefficient algebra can be treated by an explicit Gaussian phase gauge, rather than by confusing it with the original C basis. Assign input phase `gamma_a=i^wt(a)` and decode coordinate c with `gamma_c^-1`. Then

`gamma_a gamma_b/gamma_(a xor b)=(-1)^wt(a&b)`.

Thus an admissible XOR sum placement also gives a finite negative-square bilinear encoding. Returning to the original C coordinates still requires the paid `Phi=H/D` basis conversion described in the earlier report.

## Finite exhaustive scope

After translating the label at the smallest exponent to zero, affine `GL(f,2)` changes of all labels preserve compatibility. For f=2, the first two nonzero labels can be fixed to 1 and 2 and the last is 3. For f=3, the first two are again 1 and 2. The third is either 3 or a new independent label fixed to 4. In the first case, the fourth label is outside the previous two-dimensional span and can be fixed to 4. This gives exactly `24+6=30` inequivalent injective labelings, covering all `7!/168` classes.

| f | Largest allowed exponent | Complete exponent sets examined | Result |
| --- | --- | --- | --- |
| 2 | 3 | 1 | Infeasible; full search |
| 2 | 4 | 3 until first witness | Feasible |
| 3 | 12 | 792 | Infeasible; full search |
| 3 | 13 | 586 until first witness | Feasible |

The witnesses are `[0,1,3,4]` and `[0,1,3,4,9,10,12,13]`, with labels in ordinary binary order. They have nine and 27 distinct product sums, respectively. The source retains the complete sum-to-XOR map and replays full signed-integer operand products and every decoded coefficient. Positive searches stop at their first verified witness, so their examined counts are not exhaustive counts of admissible placements. The configuration records the initial feasibility hypotheses; results report agreement separately from the exact search outcome and would preserve a surprising witness rather than discard it.

## A separate all-size linear-placement result

For the narrower form `w(a)=offset+sum_j a_j d_j`, the `3^f` product-space lower bound is exact. Injectivity means that no nonzero relation `sum_j eta_j d_j=0` with `eta_j` in `{-1,0,1}` exists. Suppose two ternary digit sums s,t in `{0,1,2}^f` have the same weighted exponent. Compatibility forces their parity vectors to agree, so every entry of `s-t` is even. Dividing by two gives such an injectivity-forbidden relation. Thus s=t. Every one of the `3^f` ternary sums is distinct, and a fully materialized ordinary coefficient interval has at least that length.

This proves the radix-three volume cost for linear bit placements, including signed weights after a common shift. It is not a theorem for all nonlinear or asymmetric encoders. Also, the volume factor `(3/2)^f` must be compared to the actual inherited allowance `(E K)^tau`, not to `f^tau` in isolation. Small packets with f logarithmic in the outer width may fit a polynomial allowance; full original-shape f proportional to the width cannot. A packet format still needs a complete changed assembly and actual product bit lengths.

## Provenance and reproduction

- [xor_compatible_packing.py](../../code/transfers/xor_compatible_packing.py), SHA256 `e6d9bb4151af9010a289e34ffc6bd906c2ccf483773e13a63dd580d318b06597`, Python standard library only.
- [xor-compatible-packing.json](../../configs/transfers/xor-compatible-packing.json), SHA256 `6dacd31347e536283eba030ec76f6b92f763213d20398786c8d28392fac685fa`.
- [Full four-worker attempt](../../runs/20261009T050547Z-transfer-xor-packing/report.md), actual start 2026-10-09T05:05:47 UTC, 0.043368 source seconds, PASS.
- [Bounded one-worker attempt](../../runs/20261009T050855Z-transfer-xor-packing-bounded/report.md), actual start 2026-10-09T05:08:55 UTC, 0.040769 source seconds, PASS.

The immutable protocols, full compact results, launcher receipts, hashes and raw recovery paths are retained in those runs. No failed scientific attempt or source repair occurred.

```bash
python3 research/integer-mult-breakthrough/code/transfers/xor_compatible_packing.py --workers 1 --small
python3 research/integer-mult-breakthrough/code/transfers/xor_compatible_packing.py --workers 4
```

The bounded command covers both the positive and negative f=2 cases. Optional `--output` must name a fresh directory. Essential publication closure is the authored source and its configuration; no other track's producer is imported.
