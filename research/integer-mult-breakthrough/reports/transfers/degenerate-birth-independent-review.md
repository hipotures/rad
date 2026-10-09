# Independent literal review of degenerate-frame birth reuse

An exact finite birth-reuse component is independently accepted. It combines
source-dependent dirty birth offsets with the actual frame of
`E=span(1,7)=span(1,6)` in four address bits. E has nonzero radical
`span(6)`. Reusing the retired donor reduces complete bank stock from eight
to seven and the paid rank per payload column from 28 to 24. The deficit
remains four. This component does not implement a whole identity shear,
signed exchange, canonical `C^4` primitive or native multiplication transfer.

The reviewed producer is
[degenerate_birth_reuse_probe.py](../../code/synthesis/degenerate_birth_reuse_probe.py),
SHA256 `38c0d21d5b9b26e3532cbf2c71b381f83590fff6d766569f4cdf8a5a9e81f265`.
Its [retained contract](../../fixtures/synthesis/degenerate-birth-reuse-contract.json)
has SHA256 `ac6e33b8c21d5a61cef2a27514adbb18986f21b18a527940d8c439004cd1f0e2`.
The producer's report is
[degenerate-birth-reuse-component.md](../synthesis/degenerate-birth-reuse-component.md).
This reviewer imports no synthesis or complex producer source.

## Actual anchors and transition binding

Let `F=C^tensor4`, `A_T=C_T` for an odd label T, and
`K_T=F*A_T^-1`. Initial sources are `A_1*X0` and `A_7*X1`; both sinks and
every dirty helper initially have the identity frame. Final sources are
`F*X0,F*X1`; sinks have frames `K_8,K_14`; every helper finishes as F times
its original dirty virtual value.

The common operator is constructed independently by literal gates:

```text
D = diag(i^weight(address))
P = binary address route with columns [1,6,2,8]
F_E = D^-1 P (S*C*S on coordinate0 and coordinate1) P^-1 D^-1.
```

Every `C` is the literal two-by-two Gaussian gate with diagonal `(1+i)/2`
and off-diagonal `(1-i)/2`; every S is `diag(1,i)`. All frame matrices and
both exact inverses are checked over rational Gaussian numbers. Literal
inverse-Z Pauli images independently verify
`L_E={(z,x): x in E, z+x in Eperp}`. The overlap
`E intersect Eperp={0,6}` establishes the nonzero radical. No nondegenerate
projector assumption is used.

An independent support/character decomposition constructs every used
relative matrix as complete monomial gauges and disjoint `C^rank` blocks.
All address permutations and fourth-root units are retained. A separate
[fixture binder](../../code/transfers/degenerate_birth_fixture_review.py)
also reconstructs the producer's own affine/quadratic normal forms. It
matches every physical event to the independently authored word and binds
all 256 coefficients of each of ten distinct interfaces in both stock
cases. The coefficient hashes are recomputed from independently constructed
matrices, rather than accepted as matrix correctness evidence.

The binder checks the full finite phase tables against their quadratic
polynomials, including constant terms, and checks complete input/output
affine permutations. Removing a nonzero affine offset or a nonzero global
phase constant changes the actual matrix and is rejected. The child rank is
selected rank per payload column. At f columns it denotes one selected-width
bulk child of rank r with f columns; the corresponding physical tensor has
`r*f` literal C factors. Scalar coefficients 2 and 3 are applied once to each
payload value and are not raised to the fth power.

## Correlated dirty birth identity

Write the original dirty virtual values as Za,Zb,Zc and, in the baseline,
Zd. Early identity-frame responses subtract `Za+Zb` from Y0 and
`2Za+3Zb` from Y1. Source injection makes the retained common-frame roles

```text
A = Za+X0
B = Zb+X1.
```

At its first common-frame birth, donor c keeps actual value `F_E*Zc`.
Its birth response `(1,0)` is subtracted immediately. After adding A and B,
its virtual value is `C0=Zc+A+B`; reading it into Y0 gives exactly
`Y0+X0+X1`.

At the second birth, the reused donor is not reset. Its actual value is
`F_E*C0`, which depends on both sources and earlier dirty fields. The exact
cut response is `(0,1)`. Subtracting that actual value from the second sink,
then adding `2A+3B` into c and reading c back, cancels C0 exactly. The second
sink becomes `Y1+2X0+3X1`. The donor now has virtual value
`Zc+3A+4B`.

Move sources and all helpers to their actual full frame before cleanup.
Reverse the four workspace gates in their true order, then reverse the two
source injections. This returns every dirty virtual helper to its original
value, so its actual final value is F times that value. Undoing source
injections first would leave a source-dependent offset in the donor. The
independent replay explicitly rejects that incorrect order.

The baseline instead uses a fresh Zd bank at the second birth and its
corresponding immediate response. The clean source-to-sink map is the same.
This is a birth-cut scalar identity valid on arbitrary current dirty payload;
its small exact matrix realization does not supply any absent native tape
or canonical endpoint theorem.

## Complete ledger and finite evidence

| Paid quantity | Baseline | Reused |
|---|---:|---:|
| Complete bank stock | 8 | 7 |
| Width-one children | 6 | 6 |
| Width-two children | 8 | 6 |
| Width-three children | 2 | 2 |
| Weighted rank | 28 | 24 |
| Capacity at width four | 32 | 28 |
| Endpoint deficit | 4 | 4 |

The saved calls are the fresh donor's `I->E` and the retired donor's
`E->F`, each rank two; the reuse transition is the literal identity. The
two source transitions, both sink paths, all retained helper paths and every
full-frame cleanup are included. No payload bank disappears without its
removed stock and paths being charged consistently. For `0<p<1`, the saved
moment numerator is `2*2^p>4^p`, matching the strictly improving paid-merge
potential. This observation is conditional on a legal complete word; it is
not a root or exponent for a canonical primitive.

The four-worker
[literal attempt](../../runs/20261009T021256Z-transfer-degenerate-birth-review/report.md)
passes in 6.6050 seconds. It checks all 128 baseline and 112 reused physical
basis columns at f=1, and three complete Gaussian dirty fields for each.
Because this word is Gaussian-linear, those complete basis checks certify
the stated finite operator identity at f=1. At f=2 it checks all eight or
seven bank origins and three complete dirty fields; it makes no claim that
these origins alone cover all f=2 columns. The common-frame algebra gives
the repeated-column identity when the same exact interfaces are available,
but an all-size native implementation is a separate obligation.

The reviewer uses column-major bit position `bit+4*column`; the producer uses
bit-major position `bit*f+column`. At f=1 the positions agree. At f=2 these
are finite permutation conjugate descriptions of the same tensor operators.
This statement does not grant a free native bit transpose, physical payload
route or row layout.

Negative controls reject omitting the reused old-value response, allowing
future responses to leak across the later birth, performing grouped source
uninject before workspace undo, and treating dirty physical output as raw
identity. The 32 f=1 source basis columns and both f=2 source origins give
nonzero source-dependent second birth values. Thus the birth control is
correlated with real sources, rather than merely a fresh arbitrary constant.

The two-worker
[retained-fixture binding](../../runs/20261009T021827Z-transfer-degenerate-birth-binding/report.md)
passes in 0.1851 seconds and independently confirms both full event words,
the actual radical L_E frame and all affine/quadratic/global-unit adapters.
These are exact finite certificates and analytical review, not formal
verification or native time measurements.

## Reproduction and remaining leverage

Run from the new worktree:

```sh
python3 research/integer-mult-breakthrough/code/transfers/degenerate_birth_review.py --workers 4
python3 research/integer-mult-breakthrough/code/transfers/degenerate_birth_fixture_review.py --workers 2
```

Bounded CI uses `degenerate_birth_review.py --workers 1 --small` and
`degenerate_birth_fixture_review.py --workers 1`. The first closes over its
own config and independent `conditioned_frame_review.py`; the second also
uses its own config, the first reviewer, and B's pinned contract fixture.
No downloaded checkout, producer import, external package or random seed is
needed. Full source/config/input hashes and unchanged raw outputs are retained
in the two protocols. The full literal result includes the independently
constructed normal forms; its repeated finite tables are intentionally
retained for exact review.

This component establishes that degenerate actual frames do not prevent
birth-cut reuse. To obtain breakthrough leverage, a larger DAG must expose
enough dead donor/untouched recipient pairs while preserving paid source
chronology and canonical data endpoints. Newly born roles with direct source
injection need a separately proved response contract. The component's source
encoding and sink kernel phases remain explicit, and its scalar map is not
the identity. The
[canonical encoding obstruction](canonical-encoding-slack.md)
therefore remains relevant to whole-primitive assembly. No all-size precision,
complete-row routing, fixed-tape transfer or new kappa follows from this
isolated saving.
