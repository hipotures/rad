# Independent review of the closed central release

The central-release component is an exact operator identity under its stated
literal frame interfaces. Its stock is `W=3v`, and its per-column recursive
rank charge is `Wh-2v+2qh`. The full-width feature calls and the physical dirty
endpoint `C_h*z` are essential. This review accepts that scoped component;
it does not certify a complete native circuit, the side operator, or a new
integer-multiplication exponent.

The reviewed producer is
[closed_center_release.py](../../code/synthesis/closed_center_release.py),
SHA256 `684cd04a567881dae1c117d9966bbd59a8f9b48f1cfa674bca91ac4968948252`.
Its [report](../synthesis/closed-center-release-component.md) distinguishes
the central polynomial from the missing side operation. The new
[independent source](../../code/transfers/closed_center_review.py) imports
only previously published transfer-track Gaussian arithmetic; it does not
import the synthesis or complex producer modules.

## Operator proof on every dirty field

Let `F=C_h`, `A_j=C_Tj`, `L_j=F*A_j^-1`. Let B be any invertible scalar
v-by-v bank matrix, G its first q rows, D a decoder, and `K=D*G`.
Initially the physical arrays are `x_j=A_j*X_j`, `y_j=Y_j`, `r_j=Z_j`.
All X, Y and Z arrays can be arbitrary Gaussian dyadic fields. The following
identities concern every coordinate, rather than only a selected test input.

1. The early identity-frame `B`, negative D scatter, and `B^-1` leave r=Z
   and y=`Y-K*Z`. The inverse acts on all v coordinates, including the null
   complement.
2. Moving helper j through A_j, adding its physical source, then applying
   L_j makes it `F*(Z_j+X_j)`. Every helper now has the same actual F operator.
3. Constant scalar B commutes with common F. Thus late B produces
   `F*B*(Z+X)`. Applying F inverse to the q features gives `G*(Z+X)` at the
   actual identity operator, so the second scatter leaves `y=Y+K*X`.
4. Returning those q features to F makes all v helper banks again
   `F*B*(Z+X)`. Paid B inverse leaves `F*(Z+X)`. The source transitions give
   `x=F*X`, whose subtraction leaves helpers `F*Z`.
5. Moving each sink through its L_j gives the physical target
   `L_j*(Y_j+(K*X)_j)`.

Both scatters occur with precisely the same actual identity operator on
their two operands. Both complete basis words occur with one common
actual operator. Hence this proof permits nonunit dyadic scalars, raw bank
exchanges, arbitrary old sink data, and arbitrary old helper data. It does
not permit replacing one physical frame by an abstract label with a
different Gaussian representative. All scalar word costs remain paid.

For f selected columns, the actual array operator is `F^tensor f` and each
line operator is `A_j^tensor f`. The same scalar coefficient acts once on
each array entry. Commutation with the address operator is unchanged; a
coefficient such as 3/8 remains 3/8, rather than `(3/8)^f`.

## Relative child normalization and every record

With `alpha=(1+i)/2`, `beta=(1-i)/2`, the literal line inverse is
`A_T^-1=beta*I+alpha*X_T`. For weight(T)=1 modulo4,

```text
L_T(d)=beta*F(d)+alpha*F(d xorT)
      =2*beta*F(d) if d dotT=0, else0.
```

Because T has odd norm, `T-perp` has a nondegenerate restricted dot form
of dimension h-1. Take any basis S and its dot-dual M. Routing output by
`(S,T)` and input by `(M,T)` preserves every record and splits the operator
into two quotient-bit blocks. Within either block, the operator is exactly
one `C_(h-1)` child, with output and input phase units

```text
i^(-(weight(S*a)-weight(a)))
i^(-(weight(M*b)-weight(b))).
```

There is no extra global scale: `2*beta*alpha^h=alpha^(h-1)`. The chirps
and the two complete invertible address maps still need paid native
implementations. This statement uses a dot-dual basis; it does not assume
an orthonormal basis exists for an alternating restricted form. For f
columns, the phase exponents sum across the actual column addresses.

The independent checker constructs S directly by clearing a pivot bit,
finds M by all finite dot constraints, checks both address maps are complete
permutations, and checks every literal Gaussian coefficient for all 21
five-subset labels at h=7. It compares fixed-denominator Gaussian integer
numerators, independently of the producer's Fraction matrix construction.
It checks 344,064 full relative-matrix coefficients and 86,016 routed
child-block coefficients. An omitted chirp changes a coefficient. Weight3
has the opposite support coset and fails the no-offset formula; a different
paid affine-offset adapter is not excluded.

The full inverse also remains a full-width child. Literal `C^2=X` and
`C^-1=C*X` on one bit imply `F^-1=F*X_allones`. The address translation,
selected bit positions, all f-column chirps and complete payload movement
are not free metadata.

## Ledger and independent controls

There are v line-width calls for helper injection, 3v width-(h-1) calls
for helpers, sources and sinks, and 2q full-width calls for the feature
lowering and return. With v sources, v sinks and v actual helper banks,

```text
charge = v+3v(h-1)+2qh = Wh-2v+2qh, W=3v.
```

The endpoint rank floor is `Wh-2v`; the feature round trips cost `2qh`.
For example, h=20 gives W=46,512, charge906,832 and deficit23,408 from
W*h. The full-width self mass is `2q/W=5/612`, not zero. At h=7 and h=8
the component exceeds W*h; it is not a saving at those finite sizes.
Larger examples are retained in the receipt. They are central-only ledgers
and must not be inserted into a frozen complete recurrence.

Four independent workers completed
[run 20261009T011801Z](../../runs/20261009T011801Z-transfer-closed-center-review/report.md)
in 0.566 seconds. The controls are independently specified generic bank
matrices:

| Case | Explicit initial bank/address columns | Columns determined by exact covariance |
| --- | ---: | ---: |
| Three-label color, f=1 | 72 | 72 |
| Three-label color, f=2 | 9 | 576 |
| Two-label nonunit dyadic decoder, f=2 | 96 | 96 |

The color f=2 case computes origin columns. Every gate is a convolution or
a constant scalar bank operation, hence commutes with simultaneous XOR on
all banks. Exact covariance determines all translated columns; this is
an operator argument, rather than an assertion that all 576 columns were
explicitly executed. Each case also executes a full nonzero Gaussian
dyadic field and a nontrivial translated field. These tests use an
independent column-major address convention; producer layouts are not
assumed free to permute.

The missing feature return changes the physical dirty result in every
case. Expecting raw identity on the dirty banks also fails. The nonunit
two-column case rejects powering D's coefficients. These are scoped
negative controls, not attacks on the correct component.

The existing [single-total scalar review](total-center-independent-review.md)
already binds the actual total basis, decoder, all-size inverse classes,
and complete scalar words. This new run does not independently execute
the entire single-total h=7 physical word. Its generic operator proof and
all h=7 relative interfaces support the producer's stated scope without
mislabeling its own origin-column replay as an independent replay.

## Side integration and native obligations

The side map is `I-K`. It must be composed with this component while sinks
still admit the central identity-frame scatters. A side word that has
already moved a sink to L_j incurs a return before those scatters. A
helper that has reached F incurs the corresponding paid lowering and
restoration if used by an identity-frame side scatter. Its rows cannot
be read as if they retained their earlier frames. The common helper
bank stock, copies, retired banks and final dirty anchors must be counted
once in a complete chronological word.

Same-width children are only analytically permitted under a strictly
decreasing depth/row budget and a complete time, row-stock and leaf
contract. This component supplies no such full transfer. Native basis
scales, exchanges and multiplication temporaries, affine/chirp routing,
full-width translations, endpoint-aware precision and all live payload
fields remain integration obligations. No kappa is inferred here.

Reproduce from the repository root with the Python standard library:

```bash
python3 -B research/integer-mult-breakthrough/code/transfers/closed_center_review.py --workers 4 --output research/integer-mult-breakthrough/work/transfers/<fresh-UTC>-closed-center-review/results
python3 -B research/integer-mult-breakthrough/code/transfers/closed_center_review.py --workers 1 --small
```

The closure is the independent source, its config, and
`code/transfers/conditioned_frame_review.py`, pinned by the config. The
producer is cited for review provenance but is not an executable dependency.
The bounded command omits the color f=2 case, preserves the dyadic f=2
control and all h=7 relative interfaces, and takes less than one second.
