# Canonical encoding costs and conditional reuse budgets

The new geodesic side chronology can have a profitable **framed identity
shear** profile while failing to provide a canonical C primitive. Its
exact canonical preencoder costs two rank-one bulk calls per source/sink
pair. Those calls erase the entire endpoint saving before feature costs.
The resulting first moment exceeds one, so the separate-wrapper construction
has no positive root under its own complete ledger.

The new [independent checker](../../code/transfers/encoding_slack.py) verifies
this operator algebra literally and gives exact conditional budgets for a
future adapter that actually reuses encodings. It does not supply that adapter
or transfer a framed-profile root to integer multiplication.

## Exact physical pair operator

Let `A=C_T`, `F=C_h`, `X=X_T`, with literal `A^2=X` and `A^-1=A*X`.
The generic framed central/side word maps physical raw fields x,y to

```text
x_final = F*A^-1*x
y_final = F*X*x + F*A^-1*y.
```

Thus its actual pair matrix, before any input encoding, is

```text
P = diag(F,F) * G,
G = [[A^-1, 0],
     [X, A^-1]].
```

The exact inverse of G is

```text
H = [[A, 0],
     [-I, A]],
GH=HG=I.
```

H can be executed by `y<-A*y-x_raw`, followed by `x<-A*x_raw`.
The raw negative shear must read x before x is overwritten. It remains
an ordinary paid data operation, even though it contributes no recursive
rank. Each A is one selected-rank-one bulk call across the actual f
selected columns. The physical output of P after H is `diag(F,F)`.
Every independently dirty auxiliary remains at its required full F
endpoint under the underlying arbitrary-dirty word.

The checker constructs all 16-by-16 pair entries for h=3,T=7 directly from
literal 2-by-2 C factors. It verifies both inverse products and the canonical
endpoint. Omitting the preencoder or its negative cross shear changes the
matrix. The weight-three choice retains its actual affine/phase behavior;
the proof does not assume a homogeneous weight-one interface.

For f columns, use `A_f=A^tensor f` and `X_f=X^tensor f`. The exact identities
`A_f^2=X_f` and `A_f^-1=A_f*X_f` still hold. The same pair inverse H_f
contains two rank-one selected-width calls with f columns, rather than two
constant-size scalar gates. Treating their payload size as independent of f
would omit precisely the required recursive cost.

## First-moment obstruction

The conditional complete framed profile has stock W and rank charge

```text
Wh-2v+2qh.
```

Its necessary first moment is `1-(2v-2qh)/(Wh)`. The canonical preencoder
adds 2v width-one calls, giving

```text
canonical charge = Wh+2qh,
canonical first moment = 1+2q/W > 1.
```

Every normalized child width lies in (0,1]. Lowering the exponent from one
increases or preserves each positive term. Hence no positive characteristic
root can result from this separately wrapped circuit, even if every proposed
geodesic frame interface is realizable. The assertion does not depend on
numerical root rounding or an old recurrence controller.

Stock W remains the complete physical stock. Introducing zero data banks,
discarded outputs or additional advice changes that contract; it cannot
retain W*h as an unchanged active-input baseline. A new proof could use
such interfaces, but must account for their preparation, payload volume and
outputs explicitly.

## Exact conditional encoding allowance

The immutable
[profile fixture](../../fixtures/transfers/geodesic-encoding-profiles.json)
extracts only the complete width histograms and stocks from coordinator
run20261009T013835Z. It omits the producer's floating displays and root
brackets. The original summary and generator hashes are retained. These
are consequences of the proposed chronology, not physical/native certificates.

At the reference fraction `b=20/189981`, let

```text
Phi = sum_t (n_t/W)*(t/h)^(1-b),
B1 = (1/W)*(1/h)^(1-b).
```

Adding E width-one calls passes the strict abstract moment test precisely
when `Phi+E*B1<1`. The checker bounds logarithms by the positive rational
atanh series with its geometric tail. It bounds exponentials by a positive
Taylor polynomial and a geometric omitted-term tail. No floating point is
used. Lower/upper intervals resolve the following integer budgets:

| h | v,q | Naive encoding calls | Maximum additional calls passing the conditional reference moment | Calls that must be removed |
| --- | --- | ---: | ---: | ---: |
| 9 | 84,9 | 168 | 3 | 165 |
| 10 | 120,10 | 240 | 34 | 206 |
| 12 | 220,12 | 440 | 132 | 308 |
| 16 | 560,16 | 1,120 | 451 | 669 |

For h=12, at least70% of the naive encoding calls must disappear before
the conditional reference moment can pass. For h=9 the fraction is55/56.
Other required gates, scalar buffers, affine routing and dirty returns can
only consume further slack. These numbers are targets for a genuinely
changed adapter. They are not a statement that removing the calls is legal.
The reference fraction came from a published binary-transfer benchmark;
it is not automatically the correct transfer parameter for a different
native primitive.

Four exact arithmetic workers completed
[run20261009T014839Z](../../runs/20261009T014839Z-transfer-encoding-slack/report.md)
in0.077 seconds. The actual start and every source/config/input pin are in
the protocol. The literal pair control is run once after the independent
profile computations. Its 256 entries and all four profile intervals pass.
The bounded single-worker command retains h9 and the complete pair control.

## Reusing encodings remains a hypothesis

The exact pair inverse exposes the problem that a useful new adapter must
solve. Encoding H separately at every recursive call cannot work. Keeping
encoded fields between calls would require a complete parent chronology
that accepts their differing actual operators at every mixer, scatter,
copy and inverse. A metadata name for a frame cannot substitute for those
physical conversions.

The pair G is a unitary diagonal operator followed by a shear with unitary
off-diagonal block. Its spectral norm is the golden ratio, independent of
f. This observation does not make the address transform free: a literal
factor-by-factor A_f evaluation can consume up to f grid bits, while its
returned coefficients have denominator exponent ceil(f/2), and its complex
row-L1 is2^(f/2). Fixed-tape guards
need those component and grid bounds, rather than only the spectral norm.

A three-shear signed virtual swap can eliminate input encodings algebraically,
but separate dirty-restoring words toggle every helper I->F->I->F. Their
naive rank sum is roughly3Wh rather than Wh. Cancellation or shared release
across that complete chronology would need its own literal proof and paid
ledger. No such shared word is certified by this report.

The next discriminating question is whether a joint encoded primitive or a
different coupled recurrence can make those intermediate operators useful
without paying H on each node. It must define the exact external map,
well-founded payload/depth measure, all physical row stocks and complete
native costs. The conditional geodesic profile and endpoint-aware guard
lemmas do not supply those missing interfaces.

Reproduction from the repository root, Python standard library only:

```bash
python3 -B research/integer-mult-breakthrough/code/transfers/encoding_slack.py --workers 4 --output research/integer-mult-breakthrough/work/transfers/<fresh-UTC>-encoding-slack/results
python3 -B research/integer-mult-breakthrough/code/transfers/encoding_slack.py --workers 1 --small
```

The executable closure is its own source/config/compact fixture and
`code/transfers/conditioned_frame_review.py`. It imports no geodesic producer
or synthesis module. The original geodesic source is provenance for the
immutable input, rather than a runtime dependency. No new native primitive,
transfer theorem or kappa is claimed.
